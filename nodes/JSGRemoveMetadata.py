class JSGRemoveMetadata:
    CATEGORY = "JSG Utils/Metadata"
    FUNCTION = "remove"
    RETURN_TYPES = ("JSGMETADATA",)
    RETURN_NAMES = ("Metadata",)

    DESCRIPTION = (
        "Removes multiple metadata keys from a single JSGMETADATA object (ROOT ONLY).\n\n"
        "INPUT FORMAT:\n"
        "- 'keys' is a multiline text field.\n"
        "- Each line represents one key to remove."
    )

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "metadata": ("JSGMETADATA",),
                "keys": ("STRING", {"default": "", "multiline": True}),
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
