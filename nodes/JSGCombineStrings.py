class JSGCombineStrings:
    DESCRIPTION = (
        "Combines multiple strings into a single text value."
    )

    CATEGORY = "JSG Utils/String"
    FUNCTION = "combine"

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("Result",)
    OUTPUT_TOOLTIPS = ("Returns the combined string result.",)

    MAX_OPTIONS = 128

    @classmethod
    def INPUT_TYPES(cls):
        required = {
            "prefix": ("STRING", {"default": "", "tooltip": "The text added before each included string."}),
            "suffix": ("STRING", {"default": "", "tooltip": "The text added after each included string."}),
            "separator": ("STRING", {"default": ", ", "tooltip": "The separator inserted between the formatted strings."}),
            "always_load": ("BOOLEAN", {"default": False, "tooltip": "Whether to force this node to re-execute every run."}),
        }

        optional = {}
        for index in range(1, cls.MAX_OPTIONS + 1):
            optional[f"string_{index}"] = ("STRING", {"default": "", "tooltip": f"The optional string {index} to include in the combined result."})

        return {
            "required": required,
            "optional": optional,
        }

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        if kwargs.get("always_load", False):
            return float("NaN")
        return hash(frozenset(kwargs.items()))

    def _normalized_options(self, kwargs):
        options = []
        for index in range(1, self.MAX_OPTIONS + 1):
            value = kwargs.get(f"string_{index}", "")
            text = value.strip() if isinstance(value, str) else ""
            if text:
                options.append(text)
        return options

    def combine(self, prefix="", suffix="", separator=", ", always_load=False, **kwargs):
        combined = separator.join(
            f"{prefix}{option}{suffix}"
            for option in self._normalized_options(kwargs)
        )
        return (combined,)