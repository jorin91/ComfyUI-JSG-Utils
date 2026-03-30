from .JSGMetadataUtils import SAFE_TEXT_METADATA_FIELDS, ensure_metadata


class JSGSetStandardMetadataField:
    DESCRIPTION = (
        "Sets one standard text metadata field on a metadata object."
    )

    CATEGORY = "JSG Utils/Metadata"
    FUNCTION = "set_field"
    RETURN_TYPES = ("JSGMETADATA",)
    RETURN_NAMES = ("Metadata",)
    OUTPUT_TOOLTIPS = ("Returns the metadata object with the selected standard text field set.",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "field": (list(SAFE_TEXT_METADATA_FIELDS), {"default": "Title", "tooltip": "The standard text metadata field to set."}),
                "value": ("STRING", {"default": "", "multiline": True, "tooltip": "The string value stored in the selected field."}),
            },
            "optional": {
                "metadata": ("JSGMETADATA", {"tooltip": "The optional metadata object to modify."}),
            }
        }

    def set_field(self, field, value, metadata=None):
        out = ensure_metadata(metadata)
        text = dict(out.get("text") or {})
        text[str(field)] = "" if value is None else str(value)
        out["text"] = text
        return (out,)
