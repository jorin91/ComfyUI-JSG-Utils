import json

class JSGAddMetadata:
    CATEGORY = "JSG Utils/Metadata"
    FUNCTION = "add"
    RETURN_TYPES = ("JSGMETADATA",)
    RETURN_NAMES = ("Metadata",)
    OUTPUT_TOOLTIPS = ("Returns the metadata object with the new root-level values added.",)

    DESCRIPTION = (
        "Adds values to a metadata object at the root level."
    )

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "metadata": ("JSGMETADATA", {"tooltip": "The metadata object to extend."}),
                "keys": ("STRING", {"default": "", "multiline": True, "tooltip": "The root-level keys to add, one per line or comma-separated."}),
                "values": ("STRING", {"default": "", "multiline": True, "tooltip": "The values paired with the keys."}),
                "value_mode": (["raw", "json"], {"default": "raw", "tooltip": "How the input values are interpreted before they are stored."}),
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
