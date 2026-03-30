from .JSGMetadataUtils import create_blank_metadata


class JSGCreateBlankMetadata:
    DESCRIPTION = (
        "Creates a blank metadata object with safe text fields prefilled."
    )

    CATEGORY = "JSG Utils/Metadata"
    FUNCTION = "create"
    RETURN_TYPES = ("JSGMETADATA",)
    RETURN_NAMES = ("Metadata",)
    OUTPUT_TOOLTIPS = ("Returns a blank metadata object with standard text fields initialized.",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {}
        }

    def create(self):
        return (create_blank_metadata(),)
