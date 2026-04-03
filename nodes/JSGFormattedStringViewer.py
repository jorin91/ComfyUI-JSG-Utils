class JSGFormattedStringViewer:
    DESCRIPTION = (
        "Splits a string on a separator, trims each part, and displays them "
        "line by line inside the node. Passes the original text through unchanged "
        "and also outputs the cleaned, reformatted text."
    )

    CATEGORY = "JSG Utils/String"
    FUNCTION = "format"

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("Original", "Formatted")
    OUTPUT_TOOLTIPS = (
        "The original input text, unchanged.",
        "The text split on the separator, each part trimmed and terminated with the separator, joined by newlines.",
    )

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": True,
                        "tooltip": "The input text to format.",
                    },
                ),
                "separator": (
                    "STRING",
                    {
                        "default": ",",
                        "multiline": False,
                        "tooltip": "The separator used to split the text. The whole value is treated as a single separator.",
                    },
                ),
            },
        }

    def format(self, text: str, separator: str):
        sep = separator  # whole string is the separator

        if sep and sep in text:
            parts = [p.strip() for p in text.split(sep)]
        else:
            parts = [text.strip()] if text.strip() else []

        # Remove empty parts that result from trailing/leading separators
        parts = [p for p in parts if p]

        # Formatted: each part trimmed + separator appended, one per line
        formatted = "\n".join(p + sep for p in parts) if parts else ""

        # Preview shown inside the node via the STRING widget
        return (text, formatted)
