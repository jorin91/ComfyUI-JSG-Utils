import json

class JSGAddMetadata:
    CATEGORY = "JSG Utils/Metadata"
    FUNCTION = "add"
    RETURN_TYPES = ("JSGMETADATA",)
    RETURN_NAMES = ("Metadata",)

    DESCRIPTION = (
        "Adds (a + b) multiple metadata entries on a single JSGMETADATA object (ROOT ONLY).\n\n"
        "INPUT FORMAT:\n"
        "- 'keys' and 'values' are multiline text fields.\n"
        "- Each line represents one entry.\n"
        "- keys[n] is paired with values[n].\n\n"
        "ADD BEHAVIOR (ROOT):\n"
        "- If key does not exist: set value.\n"
        "- If key exists and is a list: append value.\n"
        "- If key exists and is not a list: convert to [old, new].\n\n"
        "VALUE MAPPING RULES:\n"
        "- No values given: all keys add an empty string\n"
        "- One value given: applied to all keys\n"
        "- Fewer values than keys: missing values become empty\n\n"
        "VALUE MODE:\n"
        "- raw: values are stored as strings\n"
        "- json: each value is parsed with JSON (numbers, booleans, lists, objects)"
    )

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "metadata": ("JSGMETADATA",),
                "keys": ("STRING", {"default": "", "multiline": True}),
                "values": ("STRING", {"default": "", "multiline": True}),
                "value_mode": (["raw", "json"], {"default": "raw"}),
            }
        }

    def _parse_keys(self, text):
        if not text:
            return []
        s = str(text).strip()
        if "\n" in s or "\r" in s:
            parts = s.replace("\r\n", "\n").replace("\r", "\n").split("\n")
        else:
            parts = s.split(",")
        return [p.strip() for p in parts if p.strip()]

    def _parse_values(self, text):
        if text is None or text == "":
            return []
        s = str(text)
        if "\n" in s or "\r" in s:
            return s.replace("\r\n", "\n").replace("\r", "\n").split("\n")
        return [p.strip() for p in s.split(",")]

    def _coerce_value(self, v, mode):
        if mode == "json":
            try:
                return json.loads(v)
            except Exception:
                return v
        return v

    def _add_value_root(self, out, key, value):
        if key not in out:
            out[key] = value
            return

        existing = out[key]

        if isinstance(existing, list):
            existing.append(value)
            return

        out[key] = [existing, value]

    def add(self, metadata, keys, values, value_mode):
        if not isinstance(metadata, dict):
            raise ValueError("JSGMETADATA must be a dict")

        key_list = self._parse_keys(keys)
        if not key_list:
            return (metadata,)

        value_list = self._parse_values(values)

        def get_value(i):
            if len(value_list) == 0:
                return ""
            if len(value_list) == 1:
                return value_list[0]
            return value_list[i] if i < len(value_list) else ""

        out = dict(metadata)

        for i, k in enumerate(key_list):
            k = str(k)
            v = self._coerce_value(get_value(i), value_mode)
            self._add_value_root(out, k, v)

        return (out,)
