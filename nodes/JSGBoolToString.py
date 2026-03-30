class JSGBoolToString:
    DESCRIPTION = (
        "Returns one of two strings based on a boolean input."
    )

    CATEGORY = "JSG Utils/String"
    FUNCTION = "select"

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("Result",)
    OUTPUT_TOOLTIPS = ("Returns the string selected by the boolean input.",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "condition": ("BOOLEAN", {"default": False, "tooltip": "The boolean value that selects the output string."}),
                "true_string": ("STRING", {"default": "", "tooltip": "The string returned when the boolean value is true."}),
                "false_string": ("STRING", {"default": "", "tooltip": "The string returned when the boolean value is false."}),
                "always_load": ("BOOLEAN", {"default": True, "tooltip": "Whether to force this node to re-execute every run."}),
            }
        }

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        if kwargs.get("always_load", False):
            return float("NaN")
        return hash(frozenset(kwargs.items()))

    def select(self, condition=False, true_string="", false_string="", always_load=False):
        return (true_string if condition else false_string,)
