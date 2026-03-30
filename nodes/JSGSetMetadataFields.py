class JSGSetMetadataFields:
    DESCRIPTION = (
        "Sets multiple text metadata fields on a metadata object."
    )

    CATEGORY = "JSG Utils/Metadata"
    FUNCTION = "set_fields"
    RETURN_TYPES = ("JSGMETADATA",)
    RETURN_NAMES = ("Metadata",)
    OUTPUT_TOOLTIPS = ("Returns the metadata object with the selected text fields updated.",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "keys": ("STRING", {"default": "", "multiline": True, "tooltip": "The text metadata fields to set, one per line or comma-separated."}),
                "values": ("STRING", {"default": "", "multiline": True, "tooltip": "The string values paired with the keys."}),
                "add_if_missing": ("BOOLEAN", {"default": True, "tooltip": "Whether to create fields that do not already exist."}),
            },
            "optional": {
                "metadata": ("JSGMETADATA", {"tooltip": "The optional metadata object to modify."}),
            }
        }

    def _ensure_metadata(self, metadata):
        from .JSGMetadataUtils import ensure_metadata
        return ensure_metadata(metadata)

    def _parse_keys(self, text):
        if not text:
            return []
        source = str(text).strip()
        if "\n" in source or "\r" in source:
            parts = source.replace("\r\n", "\n").replace("\r", "\n").split("\n")
        else:
            parts = source.split(",")
        return [part.strip() for part in parts if part.strip()]

    def _parse_values(self, text):
        if text is None or text == "":
            return []
        source = str(text)
        if "\n" in source or "\r" in source:
            return source.replace("\r\n", "\n").replace("\r", "\n").split("\n")
        return [part.strip() for part in source.split(",")]

    def set_fields(self, keys, values, add_if_missing=True, metadata=None):
        out = self._ensure_metadata(metadata)
        key_list = self._parse_keys(keys)
        if not key_list:
            return (out,)

        value_list = self._parse_values(values)

        def get_value(index):
            if len(value_list) == 0:
                return ""
            if len(value_list) == 1:
                return value_list[0]
            return value_list[index] if index < len(value_list) else ""

        text = dict(out.get("text") or {})
        for index, key in enumerate(key_list):
            field = str(key).strip()
            if not field:
                continue
            if field in text or add_if_missing:
                text[field] = get_value(index)

        out["text"] = text
        return (out,)
