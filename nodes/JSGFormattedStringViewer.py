class JSGFormattedStringViewer:
    DESCRIPTION = (
        "Splits an incoming string on a separator and displays each segment "
        "on its own line inside the node as a read-only viewer. "
        "Outputs the original text unchanged and the formatted view as a string."
    )

    CATEGORY = "JSG Utils/String"
    FUNCTION = "format"

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("Original", "Formatted")
    OUTPUT_TOOLTIPS = (
        "The original input text, unchanged.",
        "Each segment on its own line, trimmed, with the separator appended.",
    )

    OUTPUT_NODE = True

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": (
                    "STRING",
                    {
                        "forceInput": True,
                        "tooltip": "Connect a string output here to view its formatted breakdown.",
                    },
                ),
                "separator": (
                    "STRING",
                    {
                        "default": ", ",
                        "multiline": False,
                        "tooltip": "Separator used to split the text. The whole value is treated as one separator.",
                    },
                ),
            },
        }

    def format(self, text: str, separator: str):
        sep = separator

        if sep and sep in text:
            parts = [p.strip() for p in text.split(sep)]
        else:
            parts = [text.strip()] if text.strip() else []

        parts = [p for p in parts if p]
        formatted = "\n".join(p + sep for p in parts) if parts else ""

        return {"ui": {"formatted": [formatted]}, "result": (text, formatted)}
