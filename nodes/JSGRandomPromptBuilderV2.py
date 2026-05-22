import json
import os
import random as _random_module
import re


_DATA_DIR = os.path.join(
    os.path.dirname(__file__), "..", "data", "random_prompt_builder_v2"
)
_CONFIG_FILE = os.path.join(_DATA_DIR, "config.json")
_LOG = "[JSGRandomPromptBuilderV2]"
_MISSING = object()
_IGNORED_CHECK = object()


class _FreshSeedRandom:
    def __init__(self):
        self._used_seeds = set()

    def _next_seed(self):
        while True:
            seed = int.from_bytes(os.urandom(16), "big")
            if seed not in self._used_seeds:
                self._used_seeds.add(seed)
                return seed

    def choice(self, values):
        return _random_module.Random(self._next_seed()).choice(values)


_CATEGORY_INPUTS = [
    ("subject", "Subject"),
    ("ethnicity", "Ethnicity"),
    ("body_build", "Body Build"),
    ("body_detail", "Body Detail"),
    ("clothing", "Clothing"),
    ("action", "Action"),
    ("pose", "Pose"),
    ("environment", "Environment"),
    ("composition", "Composition"),
    ("lighting", "Lighting"),
    ("style", "Style"),
    ("quality", "Quality"),
]


def _load_json(path, fallback=None):
    if fallback is None:
        fallback = {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"{_LOG} WARNING: missing JSON file: {path}")
    except Exception as exc:
        print(f"{_LOG} WARNING: could not read JSON file '{path}': {exc}")
    return fallback


def _as_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _text(value):
    if value is None:
        return ""
    return str(value).strip()


def _clean_prompt(value):
    value = re.sub(r"\s*,\s*", ", ", value)
    value = re.sub(r"(,\s*)+", ", ", value)
    value = re.sub(r"\s{2,}", " ", value)
    return value.strip(" ,")


def _join_prompt(parts):
    return _clean_prompt(", ".join(p for p in parts if _text(p)))


def _clean_phrase(value):
    value = re.sub(r"\s{2,}", " ", value)
    value = re.sub(r"\s+,", ",", value)
    return value.strip(" ,")


def _format_debug_state(state, tags=None, state_priorities=None):
    tags = tags or set()
    state_priorities = state_priorities or {}
    lines = ["State:"]
    if state:
        for key in sorted(state):
            value = state[key]
            priority = state_priorities.get(key, 0)
            lines.append(f"- {key}: {json.dumps(value, ensure_ascii=False)} (priority {priority})")
    else:
        lines.append("- <empty>")

    lines.append("Tags:")
    if tags:
        for tag in sorted(tags):
            lines.append(f"- {tag}")
    else:
        lines.append("- <empty>")
    return "\n".join(lines)


def _state_write_from_value(value, default_priority=0):
    priority = default_priority if isinstance(default_priority, int) else 0
    if isinstance(value, dict) and ("value" in value or "priority" in value):
        raw_priority = value.get("priority", priority)
        priority = raw_priority if isinstance(raw_priority, int) else priority
        return value.get("value"), priority
    return value, priority


def _normalize_state_set(state_set=None, state_priority=None):
    if not isinstance(state_set, dict):
        return {}, {}
    priorities = state_priority if isinstance(state_priority, dict) else {}
    normalized = {}
    normalized_priorities = {}
    for key, raw_value in state_set.items():
        key = _text(key)
        if not key:
            continue
        value, priority = _state_write_from_value(raw_value, priorities.get(key, 0))
        normalized[key] = value
        normalized_priorities[key] = priority
    return normalized, normalized_priorities


def _merge_state_set(target, target_priorities, source, source_priorities=None):
    source_priorities = source_priorities if isinstance(source_priorities, dict) else {}
    for key, value in source.items():
        priority = source_priorities.get(key, 0)
        current_priority = target_priorities.get(key)
        if key not in target or current_priority is None or priority > current_priority:
            target[key] = value
            target_priorities[key] = priority


def _normalize_result(text="", negative="", state_set=None, state_priority=None, tags_add=None, tags_remove=None):
    normalized_state, normalized_priorities = _normalize_state_set(state_set, state_priority)
    return {
        "text": _clean_phrase(_text(text)),
        "negative": _clean_prompt(_text(negative)),
        "state_set": normalized_state,
        "state_priority": normalized_priorities,
        "tags_add": set(tags_add or []),
        "tags_remove": set(tags_remove or []),
    }


def _empty_result(result):
    return not result["text"] and not result["negative"] and not result["state_set"] and not result["tags_add"] and not result["tags_remove"]


def _allows_empty_result(value):
    return isinstance(value, dict) and bool(
        value.get("allow_empty")
        or value.get("allow_empty_result")
        or value.get("allow_empty_value")
    )


def _merge_result(target, source):
    if source["text"]:
        target["text"] = _clean_phrase(" ".join([target["text"], source["text"]]))
    if source["negative"]:
        target["negative"] = _join_prompt([target["negative"], source["negative"]])
    _merge_state_set(
        target["state_set"],
        target.setdefault("state_priority", {}),
        source["state_set"],
        source.get("state_priority", {}),
    )
    target["tags_add"].update(source["tags_add"])
    target["tags_remove"].update(source["tags_remove"])
    return target


def _apply_result_state(result, state, tags, state_priorities=None):
    if state_priorities is None:
        state_priorities = {}
    for tag in result["tags_remove"]:
        tags.discard(tag)
    for tag in result["tags_add"]:
        tags.add(tag)
    for key, value in result["state_set"].items():
        priority = result.get("state_priority", {}).get(key, 0)
        current_priority = state_priorities.get(key)
        if key not in state or current_priority is None or priority > current_priority:
            state[key] = value
            state_priorities[key] = priority


def _load_config():
    config = _load_json(_CONFIG_FILE, fallback={})
    categories = []
    for entry in config.get("categories") or []:
        if not isinstance(entry, dict):
            continue
        cid = _text(entry.get("id"))
        label = _text(entry.get("label"))
        if not cid or not label:
            continue
        order = entry.get("order", 0)
        if not isinstance(order, int):
            order = 0
        resolve_order = entry.get("resolve_order", order)
        if not isinstance(resolve_order, int):
            resolve_order = order
        categories.append({
            "id": cid,
            "label": label,
            "order": order,
            "resolve_order": resolve_order,
            "file": _text(entry.get("file")),
        })
    categories.sort(key=lambda item: item["order"])
    if not categories:
        categories = [
            {"id": cid, "label": label, "order": index, "resolve_order": index, "file": f"categories/{cid}.json"}
            for index, (cid, label) in enumerate(_CATEGORY_INPUTS)
        ]
    return config, categories


def _load_preset(preset_id):
    safe_id = re.sub(r"[^A-Za-z0-9_.-]", "", _text(preset_id)) or "none"
    path = os.path.join(_DATA_DIR, "presets", f"{safe_id}.json")
    data = _load_json(path, fallback={})
    positive = [_text(v) for v in _as_list(data.get("positive")) if _text(v)]
    negative = [_text(v) for v in _as_list(data.get("negative")) if _text(v)]
    return positive, negative


def _load_state_profile(profile_id):
    safe_id = re.sub(r"[^A-Za-z0-9_.-]", "", _text(profile_id)) or "none"
    path = os.path.join(_DATA_DIR, "state_profiles", f"{safe_id}.json")
    data = _load_json(path, fallback={})
    if not isinstance(data, dict):
        data = {}
    tags_add = [t for t in _as_list(data.get("tags_add")) if _text(t)]
    tags_remove = [t for t in _as_list(data.get("tags_remove")) if _text(t)]
    result = _normalize_result(
        state_set=data.get("state_set") if isinstance(data.get("state_set"), dict) else {},
        state_priority=data.get("state_priority") if isinstance(data.get("state_priority"), dict) else {},
        tags_add=tags_add,
        tags_remove=tags_remove,
    )
    result["ignore_state_keys"] = {
        _text(key)
        for key in _as_list(data.get("ignore_state_keys"))
        if _text(key)
    }
    result["ignore_tags"] = {
        _text(tag)
        for tag in _as_list(data.get("ignore_tags"))
        if _text(tag)
    }
    return result


def _load_category(entry):
    rel = entry.get("file") or f"categories/{entry['id']}.json"
    path = os.path.join(_DATA_DIR, rel)
    data = _load_json(path, fallback={})
    if not isinstance(data, dict):
        data = {}
    data.setdefault("id", entry["id"])
    data.setdefault("label", entry["label"])
    data.setdefault("order", entry["order"])
    data.setdefault("resolve_order", entry.get("resolve_order", entry["order"]))
    return data


def _register_generators(entries, registry, source=""):
    for gen in _as_list(entries):
        if not isinstance(gen, dict):
            continue
        gid = _text(gen.get("id"))
        if not gid:
            continue
        if gid in registry:
            print(f"{_LOG} WARNING: duplicate generator id skipped: {gid} ({source})")
            continue
        registry[gid] = gen


def _load_shared_generators():
    root = os.path.join(_DATA_DIR, "shared_generators")
    registry = {}
    if not os.path.isdir(root):
        return registry

    for dirpath, _, filenames in os.walk(root):
        for fname in filenames:
            if not fname.lower().endswith(".json"):
                continue
            path = os.path.join(dirpath, fname)
            data = _load_json(path, fallback={})
            entries = data.get("generators") if isinstance(data, dict) else None
            if entries is None:
                entries = [data]
            clean_entries = []
            for gen in _as_list(entries):
                reasons = _shared_generator_forbidden_reasons(gen)
                if reasons:
                    gid = _text(gen.get("id")) if isinstance(gen, dict) else "<unknown>"
                    print(f"{_LOG} WARNING: shared generator skipped because it contains forbidden slot/template logic: {gid} ({', '.join(sorted(set(reasons)))})")
                    continue
                clean_entries.append(gen)
            _register_generators(clean_entries, registry, source=path)
    return registry


def _category_registry(category, shared_registry):
    registry = dict(shared_registry)
    builders = []
    for builder in _as_list(category.get("builders")):
        if isinstance(builder, dict):
            marked = dict(builder)
            marked["_jsg_builder"] = True
            builders.append(marked)
    _register_generators(builders, registry, source=category.get("id", "category"))
    return registry


def _normalize_value(value):
    if value is None:
        return _normalize_result()
    if isinstance(value, str):
        return _normalize_result(text=value)
    if not isinstance(value, dict):
        return _normalize_result()

    tags_add = [t for t in _as_list(value.get("tags_add")) if _text(t)]
    tags_remove = [t for t in _as_list(value.get("tags_remove")) if _text(t)]
    return _normalize_result(
        text=value.get("text"),
        negative=value.get("negative"),
        state_set=value.get("state_set") if isinstance(value.get("state_set"), dict) else {},
        state_priority=value.get("state_priority") if isinstance(value.get("state_priority"), dict) else {},
        tags_add=tags_add,
        tags_remove=tags_remove,
    )


def _value_conditions(value):
    return value.get("conditions") if isinstance(value, dict) else None


def _value_template(value):
    if isinstance(value, dict):
        return value.get("template")
    return None


def _value_slots(value):
    if isinstance(value, dict) and isinstance(value.get("slots"), dict):
        return value.get("slots")
    return {}


def _contains_slot_condition(value):
    if isinstance(value, dict):
        if "slot" in value:
            return True
        return any(_contains_slot_condition(child) for child in value.values())
    if isinstance(value, list):
        return any(_contains_slot_condition(child) for child in value)
    return False


def _shared_generator_forbidden_reasons(gen):
    reasons = []
    if not isinstance(gen, dict):
        return reasons
    if "template" in gen:
        reasons.append("generator template")
    if "slots" in gen:
        reasons.append("generator slots")
    if _contains_slot_condition(gen.get("conditions")):
        reasons.append("generator slot condition")
    for value in _as_list(gen.get("values")):
        if not isinstance(value, dict):
            continue
        if "template" in value:
            reasons.append("generator value template")
        if "slots" in value:
            reasons.append("generator value slots")
        if _contains_slot_condition(value.get("conditions")):
            reasons.append("generator value slot condition")
    return reasons


def _generator_values(gen):
    values = gen.get("values") if isinstance(gen, dict) else None
    if isinstance(values, list) and values:
        return values
    return [""]


def _builder_values(builder):
    values = builder.get("values") if isinstance(builder, dict) else None
    if isinstance(values, list) and values:
        return values
    return [{"text": ""}]


def _result_without_text(result):
    copied = dict(result)
    copied["text"] = ""
    return copied


def _result_copy(result):
    copied = dict(result)
    copied["state_set"] = dict(result.get("state_set") or {})
    copied["state_priority"] = dict(result.get("state_priority") or {})
    copied["tags_add"] = set(result.get("tags_add") or [])
    copied["tags_remove"] = set(result.get("tags_remove") or [])
    if "_slot_results" in result:
        copied["_slot_results"] = result["_slot_results"]
    return copied


class _Resolver:
    def __init__(self, registry, rng, category_slots=None, category_id="", ignore_state_keys=None, ignore_tags=None):
        self.registry = registry
        self.rng = rng
        self.category_slots = category_slots if category_slots is not None else {}
        self.category_id = _text(category_id)
        self.ignore_state_keys = set(ignore_state_keys or [])
        self.ignore_tags = set(ignore_tags or [])

    def resolve_generator(self, generator_id, state, tags, slot_results=None, slot_defs=None, stack=None):
        gid = _text(generator_id)
        if not gid:
            return _normalize_result()
        if stack is None:
            stack = []
        if gid in stack:
            print(f"{_LOG} WARNING: generator cycle skipped: {' -> '.join(stack + [gid])}")
            return _normalize_result()

        gen = self.registry.get(gid)
        if not isinstance(gen, dict):
            print(f"{_LOG} WARNING: unknown generator: {gid}")
            return _normalize_result()

        stack = stack + [gid]
        if gen.get("_jsg_builder") and "values" in gen:
            if not self._conditions_pass(gen.get("conditions"), state, tags, None, None, stack, allow_slot_conditions=False):
                return _normalize_result()
            return self._resolve_builder_values(gen, state, tags, stack)
        if not self._conditions_pass(gen.get("conditions"), state, tags, None, None, stack, allow_slot_conditions=False):
            return _normalize_result()
        if "values" in gen:
            return self._resolve_values(_generator_values(gen), state, tags, None, None, stack, allow_slot_conditions=False)
        if "generators" in gen:
            result = _normalize_result()
            for child_id in _as_list(gen.get("generators")):
                child = self.resolve_generator(child_id, state, tags, None, None, stack)
                _apply_result_state(child, state, tags)
                _merge_result(result, child)
            return result
        return _normalize_result()

    def _resolve_values(self, values, state, tags, slot_results, slot_defs, stack, allow_slot_conditions=False):
        candidates = list(values or [])
        if not candidates:
            return _normalize_result()

        valid = []
        for value in candidates:
            value_result = _normalize_value(value)
            if self._conditions_pass(_value_conditions(value), state, tags, slot_results, slot_defs, stack, self_result=value_result, allow_slot_conditions=allow_slot_conditions):
                valid.append(value)
        if not valid:
            return _normalize_result()
        return _normalize_value(self.rng.choice(valid))

    def _resolve_builder_values(self, gen, state, tags, stack):
        candidates = [value for value in _builder_values(gen) if isinstance(value, dict)]
        if not candidates:
            return _normalize_result()

        valid = []
        for value in candidates:
            value_result = _normalize_value(value)
            if self._conditions_pass(_value_conditions(value), state, tags, None, None, stack, self_result=value_result, allow_slot_conditions=False):
                template = _text(_value_template(value))
                if template:
                    candidate_state = dict(state)
                    candidate_tags = set(tags)
                    rendered = self._resolve_template(value, candidate_state, candidate_tags, stack, template_override=template)
                    value_result["text"] = ""
                    candidate_result = _merge_result(rendered, value_result)
                else:
                    candidate_result = value_result

                if not _empty_result(candidate_result) or _allows_empty_result(value):
                    valid.append(candidate_result)
        if not valid:
            return _normalize_result()
        chosen = self.rng.choice(valid)
        if not _empty_result(chosen):
            self._merge_builder_metadata(chosen, gen)
        chosen.pop("_slot_results", None)
        return chosen

    def _resolve_template(self, gen, state, tags, stack, template_override=None):
        template = _text(template_override if template_override is not None else gen.get("template"))
        slot_defs = gen.get("slots") if isinstance(gen.get("slots"), dict) else {}
        slot_results = {}
        used_placeholder_text = False

        def replace(match):
            nonlocal used_placeholder_text
            key = _text(match.group(1))
            if not key:
                return ""
            if key in slot_defs:
                result = self._resolve_slot(key, slot_defs, slot_results, state, tags, stack)
            else:
                result = _normalize_result()
            if result["text"]:
                used_placeholder_text = True
            return result["text"]

        rendered = re.sub(r"\{([^{}]+)\}", replace, template)
        rendered = _clean_phrase(rendered)

        result = _normalize_result(text=rendered if used_placeholder_text else "")
        for slot_result in slot_results.values():
            if slot_result["negative"]:
                result["negative"] = _join_prompt([result["negative"], slot_result["negative"]])
            _merge_state_set(
                result["state_set"],
                result["state_priority"],
                slot_result["state_set"],
                slot_result.get("state_priority", {}),
            )
            result["tags_add"].update(slot_result["tags_add"])
            result["tags_remove"].update(slot_result["tags_remove"])

        result["_slot_results"] = slot_results
        self._merge_state_export(result, gen, slot_results)

        if gen.get("state_set") and isinstance(gen.get("state_set"), dict):
            state_set, state_priority = _normalize_state_set(
                gen["state_set"],
                gen.get("state_priority") if isinstance(gen.get("state_priority"), dict) else {},
            )
            _merge_state_set(result["state_set"], result["state_priority"], state_set, state_priority)
        if gen.get("negative"):
            result["negative"] = _join_prompt([result["negative"], gen.get("negative")])
        return result

    def _merge_builder_metadata(self, result, builder):
        if not isinstance(builder, dict):
            return result
        slot_results = result.get("_slot_results") if isinstance(result.get("_slot_results"), dict) else {}
        tags_add = [t for t in _as_list(builder.get("tags_add")) if _text(t)]
        tags_remove = [t for t in _as_list(builder.get("tags_remove")) if _text(t)]
        metadata = _normalize_result(
            negative=builder.get("negative"),
            state_set=builder.get("state_set") if isinstance(builder.get("state_set"), dict) else {},
            state_priority=builder.get("state_priority") if isinstance(builder.get("state_priority"), dict) else {},
            tags_add=tags_add,
            tags_remove=tags_remove,
        )
        _merge_result(result, metadata)
        self._merge_state_export(result, builder, slot_results)
        return result

    def _merge_state_export(self, result, owner, slot_results):
        if not isinstance(owner, dict):
            return result
        state_export = owner.get("state_export")
        if not isinstance(state_export, dict):
            return result
        slot_results = slot_results if isinstance(slot_results, dict) else {}
        for state_key, source in state_export.items():
            state_key = _text(state_key)
            if not state_key:
                continue
            exported, priority, should_set = self._resolve_state_export_value(source, slot_results)
            if should_set:
                _merge_state_set(
                    result["state_set"],
                    result["state_priority"],
                    {state_key: exported},
                    {state_key: priority},
                )
        return result

    def _resolve_state_export_value(self, source, slot_results):
        if source is None:
            return None, 0, False
        if isinstance(source, dict):
            raw_priority = source.get("priority", 0)
            priority = raw_priority if isinstance(raw_priority, int) else 0
            if "slot" in source:
                exported = self._slot_text(source.get("slot"), slot_results)
            elif "value" in source:
                exported = source.get("value")
            elif "template" in source:
                exported = self._render_export_template(_text(source.get("template")), slot_results)
            else:
                return None, priority, False
            if _text(exported):
                return exported, priority, True
            exported, should_set = self._empty_export_value(source.get("empty", "skip"))
            return exported, priority, should_set

        value = _text(source)
        if not value:
            return None, 0, False
        exported = self._render_export_template(value, slot_results)
        if _text(exported):
            return exported, 0, True
        return None, 0, False

    def _empty_export_value(self, mode):
        mode = _text(mode) or "skip"
        if mode == "null":
            return None, True
        if mode == "empty_string":
            return "", True
        return None, False

    def _slot_text(self, key, slot_results):
        result = slot_results.get(_text(key))
        return result["text"] if result else ""

    def _render_export_template(self, value, slot_results):
        def replace(match):
            key = _text(match.group(1))
            return self._slot_text(key, slot_results)
        if "{" in value and "}" in value:
            return _clean_phrase(re.sub(r"\{([^{}]+)\}", replace, value))
        slot_value = self._slot_text(value, slot_results)
        if slot_value:
            return slot_value
        return _clean_phrase(value)

    def _resolve_slot(self, key, slot_defs, slot_results, state, tags, stack):
        if key in slot_results:
            return slot_results[key]
        slot_def = slot_defs.get(key)
        if not isinstance(slot_def, dict):
            slot_results[key] = _normalize_result()
            return slot_results[key]

        if "values" in slot_def:
            result = self._resolve_values(_generator_values(slot_def), state, tags, slot_results, slot_defs, stack, allow_slot_conditions=True)
        else:
            result = self.resolve_generator(
                slot_def.get("generator"),
                state,
                tags,
                None,
                None,
                stack,
            )
        if not self._conditions_pass(slot_def.get("conditions"), state, tags, slot_results, slot_defs, stack, self_result=result, allow_slot_conditions=True):
            result = _normalize_result()
        _apply_result_state(result, state, tags)
        slot_results[key] = result
        return result

    def _conditions_pass(self, conditions, state, tags, slot_results, slot_defs, stack, self_result=None, allow_slot_conditions=False):
        if not conditions:
            return True
        if not isinstance(conditions, dict):
            return True

        all_checks = _as_list(conditions.get("all"))
        any_checks = _as_list(conditions.get("any"))
        none_checks = _as_list(conditions.get("none"))

        for check in all_checks:
            check_result = self._check_passes(check, state, tags, slot_results, slot_defs, stack, self_result, allow_slot_conditions)
            if check_result is not _IGNORED_CHECK and not check_result:
                return False
        if any_checks:
            any_passed = False
            for check in any_checks:
                check_result = self._check_passes(check, state, tags, slot_results, slot_defs, stack, self_result, allow_slot_conditions)
                if check_result is _IGNORED_CHECK or check_result:
                    any_passed = True
                    break
            if not any_passed:
                return False
        for check in none_checks:
            check_result = self._check_passes(check, state, tags, slot_results, slot_defs, stack, self_result, allow_slot_conditions)
            if check_result is not _IGNORED_CHECK and check_result:
                return False
        return True

    def _check_passes(self, check, state, tags, slot_results, slot_defs, stack, self_result=None, allow_slot_conditions=False):
        if not isinstance(check, dict):
            return True
        if "all" in check or "any" in check or "none" in check:
            return self._conditions_pass(check, state, tags, slot_results, slot_defs, stack, self_result, allow_slot_conditions)
        op = _text(check.get("op")) or "exists"

        if "slot" in check:
            if not allow_slot_conditions:
                return False
            key = _text(check.get("slot"))
            value = None
            if key:
                if slot_results is not None and key not in slot_results and slot_defs and key in slot_defs:
                    self._resolve_slot(key, slot_defs, slot_results, state, tags, stack)
                result = slot_results.get(key) if slot_results else None
                if result is None:
                    result = self.category_slots.get(key)
                value = result["text"] if result else None
            return self._compare(value, op, check.get("value"))

        if "state" in check:
            key = _text(check.get("state"))
            if key and key in self.ignore_state_keys:
                return _IGNORED_CHECK
            value = state.get(key, _MISSING) if key else _MISSING
            return self._compare(value, op, check.get("value"))

        if "tag" in check:
            tag = _text(check.get("tag"))
            if tag and tag in self.ignore_tags:
                return _IGNORED_CHECK
            value = tag in tags if tag else False
            return self._compare(value, op, check.get("value", True))

        return True

    def _compare(self, actual, op, expected):
        is_missing = actual is _MISSING
        exists = not is_missing and actual is not None and actual != ""
        if op == "exists":
            return exists
        if op == "missing":
            return not exists
        if op == "equals":
            return not is_missing and actual == expected
        if op == "not_equals":
            return is_missing or actual != expected
        if op == "in":
            return not is_missing and actual in _as_list(expected)
        if op == "not_in":
            return is_missing or actual not in _as_list(expected)
        return False


class _BuildContext:
    def __init__(self, owner, category_entries, categories, shared_registry, rng, state, tags, state_priorities, random_enabled, ignore_state_keys=None, ignore_tags=None):
        self.owner = owner
        self.category_entries = list(category_entries)
        self.category_by_id = {
            entry["id"]: category
            for entry, category in zip(category_entries, categories)
        }
        self.shared_registry = shared_registry
        self.rng = rng
        self.state = state
        self.tags = tags
        self.state_priorities = state_priorities
        self.random_enabled = dict(random_enabled)
        self.ignore_state_keys = set(ignore_state_keys or [])
        self.ignore_tags = set(ignore_tags or [])
        self.builder_results = {}
        self.category_results = {}
        self.category_slots = {
            entry["id"]: {}
            for entry in category_entries
        }
        self.active_builders = []

    def _category_builders(self, category_id):
        category = self.category_by_id.get(category_id, {})
        return [
            builder
            for builder in _as_list(category.get("builders"))
            if isinstance(builder, dict) and _text(builder.get("id"))
        ]

    def _builder_map(self, category_id):
        return {
            builder.get("id"): builder
            for builder in self._category_builders(category_id)
        }

    def _run_ids(self, category):
        run_ids = _as_list(category.get("run"))
        if run_ids:
            return [_text(item) for item in run_ids if _text(item)]
        return [
            builder.get("id")
            for builder in _as_list(category.get("builders"))
            if isinstance(builder, dict) and _text(builder.get("id"))
        ]

    def resolve_builder(self, category_id, builder_id, stack=None):
        category_id = _text(category_id)
        builder_id = _text(builder_id)
        if not category_id or not builder_id:
            return _normalize_result()

        key = (category_id, builder_id)
        if key in self.builder_results:
            return _result_copy(self.builder_results[key])
        if not self.random_enabled.get(category_id, True):
            result = _normalize_result()
            self.builder_results[key] = result
            return _result_copy(result)
        if key in self.active_builders:
            return _normalize_result()

        category = self.category_by_id.get(category_id, {})
        builder = self._builder_map(category_id).get(builder_id)
        if not isinstance(builder, dict):
            return _normalize_result()

        self.active_builders.append(key)
        try:
            resolver = _Resolver(
                _category_registry(category, self.shared_registry),
                self.rng,
                category_slots=self.category_slots.setdefault(category_id, {}),
                category_id=category_id,
                ignore_state_keys=self.ignore_state_keys,
                ignore_tags=self.ignore_tags,
            )
            result = resolver.resolve_generator(builder_id, self.state, self.tags, stack=stack)
            _apply_result_state(result, self.state, self.tags, self.state_priorities)
            self.owner._export_category_slots(category, builder_id, result, resolver)
            self.builder_results[key] = _result_copy(result)
            return _result_copy(result)
        finally:
            self.active_builders.pop()

    def resolve_category(self, category_id):
        category_id = _text(category_id)
        if category_id in self.category_results:
            return _result_copy(self.category_results[category_id])
        if not self.random_enabled.get(category_id, True):
            result = _normalize_result()
            self.category_results[category_id] = result
            return _result_copy(result)

        category = self.category_by_id.get(category_id, {})
        result = _normalize_result()
        text_parts = []

        for value in _as_list(category.get("values")):
            resolver = _Resolver(
                _category_registry(category, self.shared_registry),
                self.rng,
                category_slots=self.category_slots.setdefault(category_id, {}),
                category_id=category_id,
                ignore_state_keys=self.ignore_state_keys,
                ignore_tags=self.ignore_tags,
            )
            value_result = resolver._resolve_values([value], self.state, self.tags, None, None, [])
            _apply_result_state(value_result, self.state, self.tags, self.state_priorities)
            if value_result["text"]:
                text_parts.append(value_result["text"])
            _merge_result(result, _result_without_text(value_result))

        builders = self._builder_map(category_id)
        for generator_id in self._run_ids(category):
            if generator_id in builders:
                gen_result = self.resolve_builder(category_id, generator_id)
            else:
                resolver = _Resolver(
                    _category_registry(category, self.shared_registry),
                    self.rng,
                    category_slots=self.category_slots.setdefault(category_id, {}),
                    category_id=category_id,
                    ignore_state_keys=self.ignore_state_keys,
                    ignore_tags=self.ignore_tags,
                )
                gen_result = resolver.resolve_generator(generator_id, self.state, self.tags)
                _apply_result_state(gen_result, self.state, self.tags, self.state_priorities)
            if gen_result["text"]:
                text_parts.append(gen_result["text"])
            _merge_result(result, _result_without_text(gen_result))

        result["text"] = _join_prompt(text_parts)
        self.category_results[category_id] = _result_copy(result)
        return _result_copy(result)


class JSGRandomPromptBuilderV2:
    CATEGORY = "JSG Utils/Prompt"
    FUNCTION = "build"
    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("Positive Prompt", "Negative Prompt", "Debug State", "Subject")
    OUTPUT_TOOLTIPS = (
        "The assembled positive prompt string.",
        "The assembled negative prompt string.",
        "Readable overview of the final generated global state and tags.",
        "Only the resolved Subject category text, useful for filenames or labels.",
    )
    DESCRIPTION = (
        "Random Prompt Builder V2. Uses fixed category inputs, fresh JSON loading, "
        "category overrides, reusable generators, builder-local slot conditions, and global state conditions."
    )

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        if kwargs.get("always_load", True):
            return float("NaN")
        return hash(frozenset((k, str(v)) for k, v in kwargs.items()))

    @classmethod
    def INPUT_TYPES(cls):
        config, category_entries = _load_config()
        presets = [_text(p) for p in _as_list(config.get("presets")) if _text(p)]
        if not presets:
            presets = ["none"]
        state_profiles = [_text(p) for p in _as_list(config.get("state_profiles")) if _text(p)]
        if not state_profiles:
            state_profiles = [
                "SFW",
                "NSFW",
                "Mixed",
                "SFW Female",
                "NSFW Female",
                "Mixed Female",
                "SFW Male",
                "NSFW Male",
                "Mixed Male",
            ]

        required = {
            "always_load": (
                "BOOLEAN",
                {
                    "default": True,
                    "tooltip": "Force the node to re-execute so JSON and random values are refreshed every run.",
                },
            ),
            "preset": (
                presets,
                {
                    "default": config.get("default_preset", presets[0]) if config.get("default_preset") in presets else presets[0],
                    "tooltip": "Model/default prompt preset. Presets can add positive and negative fragments.",
                },
            ),
            "state_profile": (
                state_profiles,
                {
                    "default": config.get("default_state_profile", state_profiles[0]) if config.get("default_state_profile") in state_profiles else state_profiles[0],
                    "tooltip": "Initial state profile applied before category generation. Profiles set SFW/NSFW allow state and optional gender fallback state for manual subject overrides.",
                },
            ),
            "tag_lora": (
                "STRING",
                {
                    "default": "",
                    "multiline": False,
                    "tooltip": "LoRA trigger tags placed at the front of the positive prompt.",
                },
            ),
        }

        for category in category_entries:
            cid = category["id"]
            label = category["label"]
            required[f"random_{cid}"] = (
                "BOOLEAN",
                {
                    "default": True,
                    "tooltip": f"Use random generated output for {label}. Disable to use the override text.",
                },
            )
            required[f"{cid}_override"] = (
                "STRING",
                {
                    "default": "",
                    "multiline": True,
                    "tooltip": f"Manual replacement for the entire {label} category when random is disabled.",
                },
            )

        return {"required": required}

    def build(self, always_load=True, preset="none", state_profile="Mixed Female", tag_lora="", **kwargs):
        rng = _FreshSeedRandom()

        _, category_entries = _load_config()
        categories = [_load_category(entry) for entry in category_entries]
        shared_registry = _load_shared_generators()
        state = {}
        state_priorities = {}
        tags = set()
        profile_result = _load_state_profile(state_profile)
        _apply_result_state(profile_result, state, tags, state_priorities)

        preset_positive_parts, negative_parts = _load_preset(preset)
        positive_parts = []
        if _text(tag_lora):
            positive_parts.append(_text(tag_lora))

        category_results = {}
        random_enabled_by_id = {
            entry["id"]: bool(kwargs.get(f"random_{entry['id']}", True))
            for entry in category_entries
        }
        available_activity_routes = [
            route
            for route in ("action", "pose")
            if random_enabled_by_id.get(route, True)
        ]
        if not available_activity_routes:
            available_activity_routes = ["action", "pose"]
        activity_route = rng.choice(available_activity_routes)
        _apply_result_state(
            _normalize_result(state_set={"activity.route": activity_route}),
            state,
            tags,
            state_priorities,
        )
        build_context = _BuildContext(
            self,
            category_entries,
            categories,
            shared_registry,
            rng,
            state,
            tags,
            state_priorities,
            random_enabled_by_id,
            profile_result.get("ignore_state_keys", set()),
            profile_result.get("ignore_tags", set()),
        )

        for entry in sorted(category_entries, key=lambda item: (item["resolve_order"], item["order"])):
            cid = entry["id"]
            random_enabled = random_enabled_by_id.get(cid, True)
            override_text = _text(kwargs.get(f"{cid}_override", ""))

            if not random_enabled:
                if override_text:
                    category_results[cid] = _normalize_result(text=override_text)
                continue

            result = build_context.resolve_category(cid)
            category_results[cid] = result

        for entry in sorted(category_entries, key=lambda item: item["order"]):
            result = category_results.get(entry["id"])
            if not result:
                continue
            if result["text"]:
                positive_parts.append(result["text"])
            if result["negative"]:
                negative_parts.append(result["negative"])

        positive_parts.extend(preset_positive_parts)

        positive_prompt = _join_prompt(positive_parts)
        negative_prompt = _join_prompt(negative_parts)
        subject_result = category_results.get("subject") or _normalize_result()
        subject_output = subject_result.get("text", "")

        return (
            positive_prompt,
            negative_prompt,
            _format_debug_state(state, tags, state_priorities),
            subject_output,
        )

    def _resolve_category(self, category, resolver, state, tags, state_priorities=None):
        if state_priorities is None:
            state_priorities = {}
        result = _normalize_result()
        text_parts = []

        for value in _as_list(category.get("values")):
            value_result = resolver._resolve_values([value], state, tags, None, None, [])
            _apply_result_state(value_result, state, tags, state_priorities)
            if value_result["text"]:
                text_parts.append(value_result["text"])
            value_result_no_text = dict(value_result)
            value_result_no_text["text"] = ""
            _merge_result(result, value_result_no_text)

        run_ids = _as_list(category.get("run"))
        if not run_ids:
            # Builder order is semantic prompt order; keep the JSON list order intact.
            run_ids = [
                builder.get("id")
                for builder in _as_list(category.get("builders"))
                if isinstance(builder, dict)
            ]

        for generator_id in run_ids:
            gen_result = resolver.resolve_generator(generator_id, state, tags)
            _apply_result_state(gen_result, state, tags, state_priorities)
            if gen_result["text"]:
                text_parts.append(gen_result["text"])
            self._export_category_slots(category, generator_id, gen_result, resolver)
            gen_result_no_text = dict(gen_result)
            gen_result_no_text["text"] = ""
            _merge_result(result, gen_result_no_text)

        result["text"] = _join_prompt(text_parts)
        return result

    def _export_category_slots(self, category, generator_id, gen_result, resolver):
        if _empty_result(gen_result):
            return
        builders = {
            builder.get("id"): builder
            for builder in _as_list(category.get("builders"))
            if isinstance(builder, dict)
        }
        builder = builders.get(generator_id)
        if not isinstance(builder, dict):
            return
        export_as = _text(builder.get("export_as"))
        if export_as:
            resolver.category_slots[export_as] = gen_result
