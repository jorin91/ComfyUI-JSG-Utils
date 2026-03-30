import random


class JSGRandomStringChoice:
    DESCRIPTION = (
        "Chooses one string from multiple candidates using a seed value."
    )

    CATEGORY = "JSG Utils/String"
    FUNCTION = "choose"

    RETURN_TYPES = ("STRING", "INT")
    RETURN_NAMES = ("SelectedString", "UsedSeed")
    OUTPUT_TOOLTIPS = (
        "Returns the selected string.",
        "Returns the seed used for the selection.",
    )

    MAX_OPTIONS = 128

    @classmethod
    def INPUT_TYPES(cls):
        required = {
            "seed": ("INT", {"default": 0, "min": 0, "max": 0x7FFFFFFFFFFFFFFF, "control_after_generate": True, "tooltip": "The seed used for the current selection."}),
            "include_empty_strings": ("BOOLEAN", {"default": True, "tooltip": "Whether empty visible string inputs are valid choices."}),
            "always_load": ("BOOLEAN", {"default": True, "tooltip": "Whether to force this node to re-execute every run."}),
        }

        optional = {}
        for index in range(1, cls.MAX_OPTIONS + 1):
            optional[f"string_{index}"] = ("STRING", {"default": "", "tooltip": f"The optional candidate string {index}."})

        return {
            "required": required,
            "optional": optional,
        }

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        if kwargs.get("always_load", False):
            return float("NaN")
        return hash(frozenset(kwargs.items()))

    def _normalized_options(self, kwargs, include_empty_strings=False):
        options = []
        for index in range(1, self.MAX_OPTIONS + 1):
            key = f"string_{index}"
            if key not in kwargs:
                continue

            value = kwargs.get(key, "")
            text = value.strip() if isinstance(value, str) else ""
            if text or include_empty_strings:
                options.append(text)
        return options

    def choose(self, seed=0, include_empty_strings=False, always_load=False, **kwargs):
        used_seed = int(seed)
        options = self._normalized_options(kwargs, include_empty_strings=include_empty_strings)
        if not options:
            return ("", used_seed)

        selected = random.Random(used_seed).choice(options)
        return (selected, used_seed)