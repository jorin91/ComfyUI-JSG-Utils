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
                "strings": ("STRING", {"default": "", "multiline": True, "tooltip": "The comma-separated list of candidate strings."}),
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

    def _normalized_options(self, strings, include_empty_strings=False):
        if not isinstance(strings, str):
            return []

        options = []
        for value in strings.split(","):
            text = value.strip()
            if text or include_empty_strings:
                options.append(text)
        return options

    def choose(self, strings="", seed=0, include_empty_strings=False, always_load=False):
        used_seed = int(seed)
        options = self._normalized_options(strings, include_empty_strings=include_empty_strings)
        if not options:
            return ("", used_seed)

        selected = random.Random(used_seed).choice(options)
        return (selected, used_seed)