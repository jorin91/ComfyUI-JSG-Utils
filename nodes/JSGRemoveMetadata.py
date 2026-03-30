class JSGRemoveMetadata:
    CATEGORY = "JSG Utils/Metadata"
    FUNCTION = "remove"
    RETURN_TYPES = ("JSGMETADATA",)
    RETURN_NAMES = ("Metadata",)
    OUTPUT_TOOLTIPS = ("Returns the metadata object with the selected root-level keys removed.",)

    DESCRIPTION = (
        "Removes keys from a metadata object at the root level."
    )

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "metadata": ("JSGMETADATA", {"tooltip": "The metadata object to edit."}),
                "keys": ("STRING", {"default": "", "multiline": True, "tooltip": "The root-level keys to remove, one per line or comma-separated."}),
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

    def remove(self, metadata, keys):
        if not isinstance(metadata, dict):
            raise ValueError("JSGMETADATA must be a dict")

        key_list = self._parse_keys(keys)
        if not key_list:
            return (metadata,)

        out = dict(metadata)

        for k in key_list:
            out.pop(str(k), None)

        return (out,)
