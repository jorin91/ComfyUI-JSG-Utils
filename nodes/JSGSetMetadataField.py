from .JSGMetadataUtils import ensure_metadata


class JSGSetMetadataField:
    DESCRIPTION = (
        "Sets one text metadata field on a metadata object."
    )

    CATEGORY = "JSG Utils/Metadata"
    FUNCTION = "set_field"
    RETURN_TYPES = ("JSGMETADATA",)
    RETURN_NAMES = ("Metadata",)
    OUTPUT_TOOLTIPS = ("Returns the metadata object with the selected text field updated.",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "key": ("STRING", {"default": "", "tooltip": "The text metadata field to set."}),
                "value": ("STRING", {"default": "", "multiline": True, "tooltip": "The string value stored in the selected field."}),
                "add_if_missing": ("BOOLEAN", {"default": True, "tooltip": "Whether to create the field when it does not already exist."}),
            },
            "optional": {
                "metadata": ("JSGMETADATA", {"tooltip": "The optional metadata object to modify."}),
            }
        }

    def set_field(self, key, value, add_if_missing=True, metadata=None):
        out = ensure_metadata(metadata)
        field = str(key).strip()
        if not field:
            return (out,)

        text = dict(out.get("text") or {})
        if field in text or add_if_missing:
            text[field] = "" if value is None else str(value)
            out["text"] = text
        return (out,)
