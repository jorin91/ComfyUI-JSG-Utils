import os
import json
import re
import random as _random_module

# ── Configuration ─────────────────────────────────────────────────────────────

# Folder containing JSON config files, relative to this file.
_PROMPTS_DIR = os.path.join(
    os.path.dirname(__file__), "..", "data", "random_prompt_generator"
)

# Base names (without extension, case-insensitive) that are always skipped.
_SKIP_FILENAMES = {"example"}

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


# ── Filter helpers ────────────────────────────────────────────────────────────

def _to_terms(raw):
    """Normalise a blacklist/whitelist value to a list of lowercase stripped strings.

    A single empty string (``""``) as the whole value means "no filter" (backward
    compatible with existing JSON files).  An empty string *inside a list*
    (``[""]``) is a valid term: it matches when the target value is exactly empty.
    """
    if isinstance(raw, str):
        return [raw.strip().lower()] if raw.strip() else []
    if isinstance(raw, list):
        return [str(s).strip().lower() for s in raw]   # keep "" items in lists
    return []


def _terms_match(terms, target, require_all):
    def _match(t):
        # Empty term means "target must be empty" (substring check would always
        # be True for "", so we use equality here instead).
        return target == "" if t == "" else t in target

    if require_all:
        return all(_match(t) for t in terms)
    return any(_match(t) for t in terms)


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


# ── Build steps ───────────────────────────────────────────────────────────────

def _select_raw_values(parts, kwargs, rng):
    """Step 1: pick a raw value (random or manual) for each part.

    Returns dict ``(index, subIndex, partsIndex) -> str``.

    When ``use_random`` is True each part in the parts-list picks
    independently from its own ``values`` pool.
    When False the first part (partsIndex 0) receives the manual
    ``Value {display}`` string and all other parts are set to "".

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
                    raw[(index, si, pi)] = (rng.choice(values) if values else "").strip()
        else:
            manual   = (kwargs.get(f"Value {display}") or "").strip()
            is_first = True
            for sub_data in subindexes:
                si = sub_data["subIndex"]
                for part in _get_parts_list(sub_data):
                    pi = part["partsIndex"]
                    raw[(index, si, pi)] = manual if is_first else ""
                    is_first = False

    return raw


def _pre_join_by_index(raw_values):
    """Step 2: produce two join-maps used by filters.

    Returns:
      slot_joined  — ``{(index, subIndex): str}`` parts joined within each slot.
      index_joined — ``{index: str}`` slots joined within each index.
    """
    # Accumulate parts per slot
    slot_parts = {}  # (idx, sub) -> [(partsIndex, val)]
    for (idx, sub, pi), val in raw_values.items():
        slot_parts.setdefault((idx, sub), []).append((pi, val))

    slot_joined = {}
    for (idx, sub), items in slot_parts.items():
        items.sort(key=lambda x: x[0])
        slot_joined[(idx, sub)] = " ".join(v for _, v in items if v)

    # Accumulate slots per index
    index_subs = {}  # idx -> [(sub, val)]
    for (idx, sub), val in slot_joined.items():
        index_subs.setdefault(idx, []).append((sub, val))

    index_joined = {}
    for idx, items in index_subs.items():
        items.sort(key=lambda x: x[0])
        index_joined[idx] = " ".join(v for _, v in items if v)

    return slot_joined, index_joined


def _valid_idx(v):
    """True when v is a usable tree-level value: a non-negative integer."""
    return isinstance(v, int) and v >= 0


def _apply_filters(parts, kwargs, raw_values, slot_raw_joined, index_raw_joined):
    """Step 3: evaluate filter rules and resolve each part to its final value.

    All raw values are already picked before this step. Filters are evaluated
    in sorted (index, subIndex, partsIndex) order. Filter targets always
    reference raw (pre-filter) values, so both forward and backward references
    work identically.

    Returns ``{(index, subIndex, partsIndex): str}``.

    Filter target tree (Index.SubIndex.PartIndex):
      - targetIndex missing/invalid          → filter skipped
      - targetIndex valid only               → whole index joined
      - targetIndex + targetSubIndex valid   → whole slot joined
      - all three valid                      → specific part value
    """
    # Build flat list sorted by (index, subIndex, partsIndex)
    all_entries = []
    for base_name, data in parts:
        index      = data["index"]
        use_random = kwargs.get(f"Random {data['name']}", True)
        for sub_data in _get_subindexes_list(data):
            si = sub_data["subIndex"]
            for part in _get_parts_list(sub_data):
                all_entries.append((index, si, part["partsIndex"], use_random, part))
    all_entries.sort(key=lambda x: (x[0], x[1], x[2]))

    final = {}
    for index, subindex, pi, use_random, part in all_entries:
        if not use_random:
            final[(index, subindex, pi)] = raw_values[(index, subindex, pi)]
            continue

        filters     = part.get("filters") or []
        require_all = bool(part.get("filtersRequireAll", False))
        valid       = True

        for flt in filters:
            t_idx = flt.get("targetIndex")
            t_sub = flt.get("targetSubIndex")
            t_pi  = flt.get("targetPartsIndex")

            # Root must always be present
            if not _valid_idx(t_idx):
                continue

            # Walk the tree as far as each level is valid
            if not _valid_idx(t_sub):
                target_val = index_raw_joined.get(t_idx, "").lower()
            elif not _valid_idx(t_pi):
                target_val = slot_raw_joined.get((t_idx, t_sub), "").lower()
            else:
                target_val = raw_values.get((t_idx, t_sub, t_pi), "").lower()

            blacklist = _to_terms(flt.get("blacklist") or [])
            whitelist = _to_terms(flt.get("whitelist") or [])

            if blacklist and _terms_match(blacklist, target_val, require_all):
                valid = False
                break
            if whitelist and not _terms_match(whitelist, target_val, require_all):
                valid = False
                break

        final[(index, subindex, pi)] = raw_values[(index, subindex, pi)] if valid else ""

    return final


def _clean_prompt(s):
    """Collapse duplicate spaces and commas that can arise from empty values."""
    s = re.sub(r'\s*,\s*', ',', s)   # strip whitespace around every comma
    s = re.sub(r',+', ', ', s)        # collapse consecutive commas
    s = re.sub(r'  +', ' ', s)        # collapse consecutive spaces
    return s.strip(' ,')


def _combine_prompt(parts, final_values, id_lora):
    """Step 4: assemble the final prompt.

    Separator logic is applied at three levels, innermost first:

    Part level (within a subIndex):
      Normal parts are space-joined; separator parts are comma-appended after.
      Example: ["tall", "athletic", "curvy"(sep)] → "tall athletic, curvy"

    SubIndex level (within an index):
      Normal subIndexes are space-joined; separator subIndexes are comma-appended.
      Example: ["tall athletic", "freckled"(sep)] → "tall athletic, freckled"

    Index level (final output):
      All index results are comma-joined.

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
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("Prompt",)
    OUTPUT_TOOLTIPS = ("The fully assembled prompt string.",)

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

        raw_values                = _select_raw_values(parts, kwargs, rng)
        slot_joined, index_joined = _pre_join_by_index(raw_values)
        final_values              = _apply_filters(parts, kwargs, raw_values, slot_joined, index_joined)
        prompt                    = _combine_prompt(parts, final_values, id_lora)

        return (prompt,)
