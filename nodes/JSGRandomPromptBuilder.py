import os
import json
import re
import random as _random_module

# ── Configuration ─────────────────────────────────────────────────────────────

# Folder containing JSON config files, relative to this file.
_PROMPTS_DIR = os.path.join(
    os.path.dirname(__file__), "..", "data", "random_prompt_generator"
)

# Path to the state and triggers configuration file.
_STATE_FILE = os.path.join(
    os.path.dirname(__file__), "..", "data", "random_prompt_generator", "state.json"
)

# Base names (without extension, case-insensitive) that are always skipped.
_SKIP_FILENAMES = {"example", "state"}

_LOG = "[JSGRandomPromptBuilder]"


# ── Loader ────────────────────────────────────────────────────────────────────

def _load_prompt_parts():
    """
    Scans _PROMPTS_DIR for valid JSON files.

    Each file represents one complete index containing a ``subIndexes`` array.

    Skips:
      - Files whose base name (lower-case) is in _SKIP_FILENAMES.
      - Files that are not valid JSON (logs warning).
      - Files missing required fields: name (str), index (int >= 0),
        subIndexes (non-empty list).

    Duplicate index values:
      Files are processed in sorted filename order; the first claimant wins.
      Subsequent duplicates are skipped with a warning.

    Returns a list of (base_name, data) tuples sorted by index asc.
    """
    if not os.path.isdir(_PROMPTS_DIR):
        print(f"{_LOG} WARNING: prompt parts folder not found: {_PROMPTS_DIR}")
        return []

    candidates = []

    for fname in sorted(os.listdir(_PROMPTS_DIR)):
        if not fname.lower().endswith(".json"):
            continue

        base = os.path.splitext(fname)[0]
        if base.lower() in _SKIP_FILENAMES:
            continue

        fpath = os.path.join(_PROMPTS_DIR, fname)
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as exc:
            print(f"{_LOG} WARNING: skipping '{fname}' — invalid JSON: {exc}")
            continue

        if not isinstance(data.get("name"), str) or not data["name"].strip():
            print(f"{_LOG} WARNING: skipping '{fname}' — missing or empty 'name'")
            continue

        if not (isinstance(data.get("index"), int) and data.get("index", -1) >= 0):
            print(f"{_LOG} WARNING: skipping '{fname}' — 'index' must be a non-negative integer")
            continue

        if not (isinstance(data.get("subIndexes"), list) and data["subIndexes"]):
            print(f"{_LOG} WARNING: skipping '{fname}' — 'subIndexes' must be a non-empty array")
            continue

        candidates.append((base, data))

    def _sort_key(item):
        _, d = item
        return d["index"]

    candidates.sort(key=_sort_key)

    # Deduplicate — first claimant wins
    seen = {}   # index -> base_name
    parts = []
    for base, data in candidates:
        key = data["index"]
        if key in seen:
            print(
                f"{_LOG} WARNING: skipping '{base}' — "
                f"duplicate index={key} already claimed by '{seen[key]}'"
            )
            continue
        seen[key] = base
        parts.append((base, data))

    return parts


# ── Parts normalisation ──────────────────────────────────────────────────────

def _get_subindexes_list(data):
    """Return subIndex entries with a valid subIndex (int >= 0), sorted ascending.

    Entries where subIndex is absent, not an int, or < 0 are silently skipped.
    """
    result = []
    for s in (data.get("subIndexes") or []):
        if not isinstance(s, dict):
            continue
        si = s.get("subIndex")
        if not (isinstance(si, int) and si >= 0):
            continue
        result.append(dict(s))
    return sorted(result, key=lambda s: s["subIndex"])


def _get_parts_list(subindex_data):
    """Return parts from a subIndex object with a valid partsIndex (int >= 0), sorted ascending.

    Parts where partsIndex is absent, not an int, or < 0 are silently skipped.
    """
    result = []
    for p in (subindex_data.get("parts") or []):
        if not isinstance(p, dict):
            continue
        pi = p.get("partsIndex")
        if not (isinstance(pi, int) and pi >= 0):
            continue
        result.append(dict(p))
    return sorted(result, key=lambda p: p["partsIndex"])


# ── Value normalisation ───────────────────────────────────────────────────────

def _normalize_value(v):
    """Normalise a raw JSON value entry to a canonical dict.

    Accepts:
      - plain string  → {text, tags: [], removeTags: [], kv: []}
      - object        → validates fields and fills defaults

    Valid kv entries must have both 'key' (str, non-empty) and 'value' (str).
    Entries missing either field are silently dropped.
    'priority' is optional, defaults to 0; non-numeric values are coerced to 0.
    """
    if isinstance(v, str):
        return {
            "positiveText": v.strip(), "negativeText": "",
            "tags": [], "removeTags": [], "kv": [],
            "triggers": [],
            "filtersRequired": [], "filtersAny": [], "includeInPrompt": True,
        }

    if not isinstance(v, dict):
        return {
            "positiveText": "", "negativeText": "",
            "tags": [], "removeTags": [], "kv": [],
            "triggers": [],
            "filtersRequired": [], "filtersAny": [], "includeInPrompt": True,
        }

    positive_text = str(v.get("positiveText") or "").strip()
    negative_text = str(v.get("negativeText") or "").strip()

    raw_tags = v.get("tags") or []
    tags = [str(t) for t in raw_tags if isinstance(t, str) and t]

    raw_remove = v.get("removeTags") or []
    remove_tags = [str(t) for t in raw_remove if isinstance(t, str) and t]

    raw_kv = v.get("kv") or []
    kv = []
    if isinstance(raw_kv, list):
        for entry in raw_kv:
            if not isinstance(entry, dict):
                continue
            k = entry.get("key")
            val = entry.get("value")
            if not isinstance(k, str) or not k:
                continue
            if not isinstance(val, str):
                continue
            priority = entry.get("priority", 0)
            if not isinstance(priority, (int, float)):
                priority = 0
            kv.append({"key": k, "value": val, "priority": int(priority)})

    raw_required = v.get("filtersRequired") or []
    filters_required = [f for f in raw_required if isinstance(f, dict)]
    raw_any = v.get("filtersAny") or []
    filters_any = [f for f in raw_any if isinstance(f, dict)]
    raw_triggers = v.get("triggers") or []
    triggers_list = [str(t) for t in raw_triggers if isinstance(t, str) and t]
    include_in_prompt = bool(v.get("includeInPrompt", True))

    return {
        "positiveText": positive_text, "negativeText": negative_text,
        "tags": tags, "removeTags": remove_tags, "kv": kv,
        "triggers": triggers_list,
        "filtersRequired": filters_required, "filtersAny": filters_any,
        "includeInPrompt": include_in_prompt,
    }


# ── Global state helpers ──────────────────────────────────────────────────────

def _accumulate_state(value_obj, global_tags, global_kv, trigger_defs=None):
    """Update global_tags and global_kv from a passing value object.

    Processing order within each value:
      1. triggers   — named presets applied in array order; each preset runs
                      its own removeTags → tags → kv before the next starts.
      2. removeTags — value's own tag removals.
      3. tags       — value's own tags.
      4. kv         — value's own kv entries.

    global_tags : set of str
    global_kv   : dict of key -> {"value": str, "priority": int}

    KV priority rule: a new entry only overwrites an existing key when its
    priority is greater than or equal to the stored priority.
    """
    # 1. Triggers — in array order; each: removeTags → tags → kv
    if trigger_defs:
        for name in value_obj["triggers"]:
            trig = trigger_defs.get(name)
            if trig is None:
                print(f"{_LOG} WARNING: unknown trigger '{name}'")
                continue
            for tag in trig["removeTags"]:
                global_tags.discard(tag)
            for tag in trig["tags"]:
                global_tags.add(tag)
            for entry in trig["kv"]:
                k = entry["key"]
                p = entry["priority"]
                if k not in global_kv or p >= global_kv[k]["priority"]:
                    global_kv[k] = {"value": entry["value"], "priority": p}

    # 2. Own removeTags
    for tag in value_obj["removeTags"]:
        global_tags.discard(tag)

    # 3. Own tags
    for tag in value_obj["tags"]:
        global_tags.add(tag)

    # 4. Own kv
    for entry in value_obj["kv"]:
        k = entry["key"]
        p = entry["priority"]
        if k not in global_kv or p >= global_kv[k]["priority"]:
            global_kv[k] = {"value": entry["value"], "priority": p}


# ── Filter evaluation ─────────────────────────────────────────────────────────

def _eval_filter_object(flt, global_tags, global_kv):
    """Evaluate a single filter object against the current global state.

    Returns (has_conditions: bool, passed: bool).

    has_conditions is False when no valid filter conditions were found in this
    object — the caller treats such objects as non-contributing (skipped).

    Within a single filter object ALL conditions must pass (AND logic).
    Invalid or empty entries within each list are silently skipped and do not
    count as conditions.

    Supported keys:
      tagWhitelist  — list of str; each tag must be present in global_tags.
      tagBlacklist  — list of str; none of the tags may be present.
      kvWhitelist   — list of {key, value}; global_kv[key] must equal value.
      kvBlacklist   — list of {key, value}; global_kv[key] must NOT equal value.
    """
    conditions = []

    tag_wl = [t for t in (flt.get("tagWhitelist") or []) if isinstance(t, str) and t]
    for tag in tag_wl:
        conditions.append(tag in global_tags)

    tag_bl = [t for t in (flt.get("tagBlacklist") or []) if isinstance(t, str) and t]
    for tag in tag_bl:
        conditions.append(tag not in global_tags)

    kv_wl = flt.get("kvWhitelist") or []
    if isinstance(kv_wl, list):
        for entry in kv_wl:
            if not isinstance(entry, dict):
                continue
            k = entry.get("key")
            v = entry.get("value")
            if not isinstance(k, str) or not k or not isinstance(v, str):
                continue
            current = global_kv.get(k)
            conditions.append(current is not None and current["value"] == v)

    kv_bl = flt.get("kvBlacklist") or []
    if isinstance(kv_bl, list):
        for entry in kv_bl:
            if not isinstance(entry, dict):
                continue
            k = entry.get("key")
            v = entry.get("value")
            if not isinstance(k, str) or not k or not isinstance(v, str):
                continue
            current = global_kv.get(k)
            conditions.append(current is None or current["value"] != v)

    if not conditions:
        return False, True  # no valid conditions → skip this object

    return True, all(conditions)


def _eval_filters(filters_required, filters_any, global_tags, global_kv):
    """Evaluate filter lists for a part or value against the current global state.

    filtersRequired — every contributing filter object must pass (AND).
    filtersAny      — at least one contributing filter object must pass (OR).

    Filter objects with no valid conditions are skipped (non-contributing).
    If a list is empty or no objects contribute conditions, that list passes.

    Returns True if the part/value should be included.
    """
    # Phase 1: required filters — all must pass
    for flt in (filters_required or []):
        if not isinstance(flt, dict):
            continue
        has_conditions, passed = _eval_filter_object(flt, global_tags, global_kv)
        if has_conditions and not passed:
            return False

    # Phase 2: any filters — at least one must pass (if any contribute)
    if filters_any:
        results = []
        for flt in filters_any:
            if not isinstance(flt, dict):
                continue
            has_conditions, passed = _eval_filter_object(flt, global_tags, global_kv)
            if has_conditions:
                results.append(passed)
        if results and not any(results):
            return False

    return True


# ── Per-value filter helpers ─────────────────────────────────────────────────

def _value_filter_passes(value_obj, global_tags, global_kv):
    """Return True when the value's own filters pass against the current global state."""
    return _eval_filters(
        value_obj["filtersRequired"],
        value_obj["filtersAny"],
        global_tags,
        global_kv,
    )


def _resolve_value(initial_value_obj, part, global_tags, global_kv, rng):
    """Return the final value object to use for a part.

    If the initially chosen value passes its own filters, return it directly.
    Otherwise collect all values from the part pool whose filters pass (or are
    absent) and re-pick randomly from that subset — including any empty-string
    entries that have no failing filter.

    Returns a normalised value object. Falls back to an empty value if the
    qualifying subset is empty.
    """
    if _value_filter_passes(initial_value_obj, global_tags, global_kv):
        return initial_value_obj

    qualifying = [
        norm
        for norm in (_normalize_value(v) for v in (part.get("values") or []))
        if _value_filter_passes(norm, global_tags, global_kv)
    ]

    if not qualifying:
        return _normalize_value("")  # empty fallback

    return rng.choice(qualifying)


# ── State loader ──────────────────────────────────────────────────────────────

def _load_state():
    """Load initial global state and trigger definitions from state.json.

    Returns (initial_tags, initial_kv, trigger_defs):
      initial_tags  : list of str — tags seeded into global_tags before evaluation.
      initial_kv    : list of {key, value, priority} — kv seeded into global_kv
                      before evaluation. Entries with null value are documentation
                      placeholders and are skipped.
      trigger_defs  : dict of name -> {tags, removeTags, kv} — named presets that
                      value objects can reference via their "triggers" array.
    """
    if not os.path.isfile(_STATE_FILE):
        return [], [], {}

    try:
        with open(_STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as exc:
        print(f"{_LOG} WARNING: could not load state.json — {exc}")
        return [], [], {}

    # ── Initial state ──────────────────────────────────────────────────────
    init     = data.get("initialState") or {}
    raw_tags = init.get("tags") or []
    initial_tags = [str(t) for t in raw_tags if isinstance(t, str) and t]

    initial_kv = []
    for entry in (init.get("kv") or []):
        if not isinstance(entry, dict):
            continue
        k = entry.get("key")
        v = entry.get("value")
        if not isinstance(k, str) or not k:
            continue
        if v is None:              # null → documentation placeholder, skip
            continue
        if not isinstance(v, str):
            continue
        p = entry.get("priority", 0)
        if not isinstance(p, (int, float)):
            p = 0
        initial_kv.append({"key": k, "value": v, "priority": int(p)})

    # ── Triggers ───────────────────────────────────────────────────────────
    raw_triggers = data.get("triggers") or {}
    trigger_defs = {}
    if isinstance(raw_triggers, dict):
        for name, trig in raw_triggers.items():
            if not isinstance(trig, dict):
                continue
            t_tags   = [str(t) for t in (trig.get("tags")       or []) if isinstance(t, str) and t]
            t_remove = [str(t) for t in (trig.get("removeTags") or []) if isinstance(t, str) and t]
            t_kv     = []
            for entry in (trig.get("kv") or []):
                if not isinstance(entry, dict):
                    continue
                k = entry.get("key")
                v = entry.get("value")
                if not isinstance(k, str) or not k:
                    continue
                if v is None:
                    continue
                if not isinstance(v, str):
                    continue
                p = entry.get("priority", 0)
                if not isinstance(p, (int, float)):
                    p = 0
                t_kv.append({"key": k, "value": v, "priority": int(p)})
            trigger_defs[name] = {"tags": t_tags, "removeTags": t_remove, "kv": t_kv}

    # ── Default negative prompt ────────────────────────────────────────────
    default_negative = str(init.get("defaultNegativePrompt") or "").strip()

    return initial_tags, initial_kv, trigger_defs, default_negative


# ── Build steps ───────────────────────────────────────────────────────────────

def _select_raw_values(parts, kwargs, rng):
    """Step 1: pick a raw normalised value object for each part.

    Returns dict ``(index, subIndex, partsIndex) -> normalised value dict``.

    When ``use_random`` is True, each part picks independently from its own
    ``values`` pool and the chosen entry is normalised via _normalize_value.
    When False, the first part receives the manual ``Value {display}``
    string (normalised) and all other parts receive an empty normalised value.

    ``rng`` is a ``random.Random`` instance seeded per build call from OS
    entropy, isolated from the global random state.
    """
    raw = {}
    for base_name, data in parts:
        index      = data["index"]
        display    = data["name"]
        use_random = kwargs.get(f"Random {display}", True)
        subindexes = _get_subindexes_list(data)

        if use_random:
            for sub_data in subindexes:
                si = sub_data["subIndex"]
                for part in _get_parts_list(sub_data):
                    pi     = part["partsIndex"]
                    values = part.get("values") or []
                    chosen = rng.choice(values) if values else ""
                    raw[(index, si, pi)] = _normalize_value(chosen)
        else:
            manual   = (kwargs.get(f"Value {display}") or "").strip()
            is_first = True
            for sub_data in subindexes:
                si = sub_data["subIndex"]
                for part in _get_parts_list(sub_data):
                    pi = part["partsIndex"]
                    raw[(index, si, pi)] = _normalize_value(manual if is_first else "")
                    is_first = False

    return raw


def _evaluate_and_accumulate(parts, kwargs, raw_values, rng):
    """Step 2: streaming filter evaluation with live tag/kv accumulation.

    Iterates all parts in strict (index, subIndex, partsIndex) order.
    For each part:
      - Non-random parts: always included, no tag/kv accumulation.
      - Random parts:
          1. Part-level filters are checked first. If they fail the part
             resolves to empty and nothing is accumulated.
          2. If part-level filters pass, the initially chosen value's own
             filters are checked. If those fail, a re-pick is performed from
             all values in the pool whose filters pass (or are absent).
          3. The final chosen value's tags/kv are accumulated.
          4. If the value's includeInPrompt is False its text is suppressed
             (empty string stored) but accumulation still happens.

    Part-level includeInPrompt is handled purely in _combine_prompt (output).
    Value-level includeInPrompt suppresses the text in final_values but still
    allows the value to accumulate tags/kv.

    Returns ``({(index, subIndex, partsIndex): str}, {same keys: str}, global_tags, global_kv)``
    — positive text dict, negative text dict, accumulated tags, accumulated kv.
    """
    initial_tags, initial_kv, trigger_defs, _ = _load_state()

    global_tags = set(initial_tags)
    global_kv   = {}  # key -> {"value": str, "priority": int}
    for entry in initial_kv:
        k = entry["key"]
        p = entry["priority"]
        if k not in global_kv or p >= global_kv[k]["priority"]:
            global_kv[k] = {"value": entry["value"], "priority": p}

    all_entries = []
    for base_name, data in parts:
        index      = data["index"]
        eval_order = data.get("evaluationOrder")
        if not (isinstance(eval_order, int) and eval_order >= 0):
            eval_order = index
        use_random = kwargs.get(f"Random {data['name']}", True)
        for sub_data in _get_subindexes_list(data):
            si = sub_data["subIndex"]
            for part in _get_parts_list(sub_data):
                all_entries.append((eval_order, index, si, part["partsIndex"], use_random, part))
    # Sort by evaluationOrder first, then subIndex and partsIndex within each file.
    # Output order (index) is untouched — _combine_prompt sorts by index independently.
    all_entries.sort(key=lambda x: (x[0], x[2], x[3]))

    final_pos = {}
    final_neg = {}
    for eval_order, index, subindex, pi, use_random, part in all_entries:
        value_obj = raw_values[(index, subindex, pi)]

        if not use_random:
            final_pos[(index, subindex, pi)] = value_obj["positiveText"]
            final_neg[(index, subindex, pi)] = ""
            continue

        # ── 1. Part-level filter ──────────────────────────────────────────
        part_filters_required = part.get("filtersRequired") or []
        part_filters_any      = part.get("filtersAny") or []

        if not _eval_filters(part_filters_required, part_filters_any, global_tags, global_kv):
            final_pos[(index, subindex, pi)] = ""
            final_neg[(index, subindex, pi)] = ""
            continue

        # ── 2. Value-level filter + optional re-pick ──────────────────────
        chosen = _resolve_value(value_obj, part, global_tags, global_kv, rng)

        # ── 3. Accumulate tags/kv from the final chosen value ─────────────
        _accumulate_state(chosen, global_tags, global_kv, trigger_defs)

        # ── 4. Store text (suppressed if value-level includeInPrompt=False) ─
        final_pos[(index, subindex, pi)] = chosen["positiveText"] if chosen["includeInPrompt"] else ""
        final_neg[(index, subindex, pi)] = chosen["negativeText"] if chosen["includeInPrompt"] else ""

    return final_pos, final_neg, global_tags, global_kv


def _clean_prompt(s):
    """Collapse duplicate spaces and commas that can arise from empty values."""
    s = re.sub(r'\s*,\s*', ',', s)   # strip whitespace around every comma
    s = re.sub(r',+', ', ', s)        # collapse consecutive commas
    s = re.sub(r'  +', ' ', s)        # collapse consecutive spaces
    return s.strip(' ,')


def _combine_prompt(parts, final_values, id_lora):
    """Step 3: assemble the final prompt.

    Separator logic is applied at three levels, innermost first:

    Part level (within a subIndex):
      Normal parts are space-joined; separator parts are comma-appended after.
      Example: ["tall", "athletic", "curvy"(sep)] → "tall athletic, curvy"

    SubIndex level (within an index):
      Normal subIndexes are space-joined; separator subIndexes are comma-appended.
      Example: ["tall athletic", "freckled"(sep)] → "tall athletic, freckled"

    Index level (final output):
      All index results are comma-joined.

    Parts with includeInPrompt=false are skipped here (output only).
    After assembly, duplicate spaces and commas are cleaned up.
    """
    index_results = []
    for base_name, data in sorted(parts, key=lambda x: x[1]["index"]):
        index      = data["index"]
        subindexes = _get_subindexes_list(data)

        normal_sub_vals = []
        sep_sub_vals    = []

        for sub_data in subindexes:
            si         = sub_data["subIndex"]
            is_sep_sub = bool(sub_data.get("separator", False))

            # ── Part-level separator logic ────────────────────────────────
            normal_part_vals = []
            sep_part_vals    = []
            for p in _get_parts_list(sub_data):
                if not p.get("includeInPrompt", True):
                    continue
                v = final_values.get((index, si, p["partsIndex"]), "").strip()
                if not v:
                    continue
                if bool(p.get("separator", False)):
                    sep_part_vals.append(v)
                else:
                    normal_part_vals.append(v)

            normal_str = " ".join(normal_part_vals)
            pieces     = ([normal_str] if normal_str else []) + sep_part_vals
            sub_val    = ", ".join(pieces)

            if not sub_val:
                continue
            if is_sep_sub:
                sep_sub_vals.append(sub_val)
            else:
                normal_sub_vals.append(sub_val)

        # ── SubIndex-level separator logic ───────────────────────────────
        normal_str   = " ".join(normal_sub_vals)
        pieces       = ([normal_str] if normal_str else []) + sep_sub_vals
        index_result = ", ".join(pieces)
        if index_result:
            index_results.append(index_result)

    id_str = (id_lora or "").strip()
    if id_str:
        index_results.insert(0, id_str)

    return _clean_prompt(", ".join(index_results))


# ── Node class ────────────────────────────────────────────────────────────────

class JSGRandomPromptBuilder:
    CATEGORY = "JSG Utils/Prompt"
    FUNCTION = "build"
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("Positive Prompt", "Negative Prompt", "Debug")
    OUTPUT_TOOLTIPS = (
        "The fully assembled positive prompt string.",
        "The fully assembled negative prompt string (default negative from state.json prepended).",
        "Debug overview of all active tags and key/value state after evaluation.",
    )

    DESCRIPTION = (
        "Modular random prompt generator. "
        "Reads JSON config files from 'data/random_prompt_generator/' and builds a structured prompt. "
        "Each part can be randomised or manually overridden. "
        "Add new parts by dropping a JSON file in the folder and toggling Refresh."
    )

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        if kwargs.get("always_load", True):
            return float("NaN")
        return hash(frozenset((k, str(v)) for k, v in kwargs.items()))

    @classmethod
    def INPUT_TYPES(cls):
        parts = _load_prompt_parts()

        required = {
            "always_load": (
                "BOOLEAN",
                {
                    "default": True,
                    "tooltip": "When enabled, the node re-executes on every queue run so random values are always redrawn.",
                },
            ),
            "refresh": (
                "BOOLEAN",
                {
                    "default": False,
                    "label_on": "Refreshed",
                    "label_off": "Refresh",
                    "tooltip": "Toggle to reload JSON config files and rebuild dynamic inputs.",
                },
            ),
            "id_lora": (
                "STRING",
                {
                    "default": "",
                    "multiline": False,
                    "tooltip": "ID / Lora trigger word placed at the start of the prompt.",
                },
            ),
        }

        optional = {}
        for base_name, data in parts:
            display = data["name"]
            optional[f"Random {display}"] = (
                "BOOLEAN",
                {
                    "default": True,
                    "tooltip": (
                        f"When enabled, a random value is picked for '{display}'. "
                        f"When disabled, the manual value below is used."
                    ),
                },
            )
            optional[f"Value {display}"] = (
                "STRING",
                {
                    "default": "",
                    "multiline": True,
                    "tooltip": f"Manual override value for '{display}'. Used when Random is disabled.",
                },
            )

        return {"required": required, "optional": optional}

    def build(self, always_load, refresh, id_lora, **kwargs):
        # Fresh RNG seeded from OS entropy — immune to global random.seed() calls
        # made by ComfyUI or other nodes.
        rng = _random_module.Random()
        rng.seed(int.from_bytes(os.urandom(8), "big"))

        parts = _load_prompt_parts()

        _, initial_kv, _trigger_defs, default_negative = _load_state()

        raw_values                                     = _select_raw_values(parts, kwargs, rng)
        final_pos, final_neg, global_tags, global_kv   = _evaluate_and_accumulate(parts, kwargs, raw_values, rng)
        positive_prompt                                = _combine_prompt(parts, final_pos, id_lora)
        neg_parts_prompt                               = _combine_prompt(parts, final_neg, "")

        neg_pieces = [p for p in (default_negative, neg_parts_prompt) if p]
        negative_prompt = _clean_prompt(", ".join(neg_pieces))

        tag_lines = [f"  {t}" for t in sorted(global_tags)]
        kv_lines  = [f"  {k} = {v['value']}  (priority {v['priority']})" for k, v in sorted(global_kv.items())]

        debug = (
            "── Tags ─────────────────────────────────────\n"
            + ("\n".join(tag_lines) if tag_lines else "  (none)")
            + "\n\n── KV ──────────────────────────────────────\n"
            + ("\n".join(kv_lines) if kv_lines else "  (none)")
        )

        return (positive_prompt, negative_prompt, debug)
