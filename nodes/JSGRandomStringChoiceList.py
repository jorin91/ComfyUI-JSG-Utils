import random


class JSGRandomStringChoiceList:
    DESCRIPTION = (
        "Chooses one string from a comma-separated list using a seed value."
    )

    CATEGORY = "JSG Utils/String"
    FUNCTION = "choose"

    RETURN_TYPES = ("STRING", "INT")
    RETURN_NAMES = ("SelectedString", "UsedSeed")
    OUTPUT_TOOLTIPS = (
        "Returns the selected string.",
        "Returns the seed used for the selection.",
    )

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "strings": ("STRING", {"default": "", "multiline": True, "tooltip": "The list of candidate strings, split by the separator."}),
                "separator": ("STRING", {"default": ",", "tooltip": "Character(s) used to split the string list. Every individual character in this value is treated as a separator."}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0x7FFFFFFFFFFFFFFF, "control_after_generate": True, "tooltip": "The seed used for the current selection."}),
                "include_empty_strings": ("BOOLEAN", {"default": True, "tooltip": "Whether empty entries between commas are valid choices."}),
                "always_load": ("BOOLEAN", {"default": True, "tooltip": "Whether to force this node to re-execute every run."}),
            }
        }

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        if kwargs.get("always_load", False):
            return float("NaN")
        return hash(frozenset(kwargs.items()))

    def _normalized_options(self, strings, separator=",", include_empty_strings=False):
        if not isinstance(strings, str):
            return []

        import re
        if separator:
            pattern = "[" + re.escape(separator) + "]"
            parts = re.split(pattern, strings)
        else:
            parts = [strings]

        options = []
        for value in parts:
            text = value.strip()
            if text or include_empty_strings:
                options.append(text)
        return options

    def choose(self, strings="", separator=",", seed=0, include_empty_strings=False, always_load=False):
        used_seed = int(seed)
        options = self._normalized_options(strings, separator=separator, include_empty_strings=include_empty_strings)
        if not options:
            return ("", used_seed)

        selected = random.Random(used_seed).choice(options)
        return (selected, used_seed)