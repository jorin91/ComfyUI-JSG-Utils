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

    def _normalized_options(self, kwargs):
        options = []
        for index in range(1, self.MAX_OPTIONS + 1):
            value = kwargs.get(f"string_{index}", "")
            text = value.strip() if isinstance(value, str) else ""
            if text:
                options.append(text)
        return options

    def choose(self, seed=0, always_load=False, **kwargs):
        options = self._normalized_options(kwargs)
        if not options:
            raise ValueError("Fill in at least one string input.")

        used_seed = int(seed)
        selected = random.Random(used_seed).choice(options)
        return (selected, used_seed)