import random


class JSGRandomBool:
    DESCRIPTION = (
        "Generates a random boolean value from a seed."
    )

    CATEGORY = "JSG Utils/Logic"
    FUNCTION = "generate"

    RETURN_TYPES = ("BOOLEAN", "INT")
    RETURN_NAMES = ("Value", "UsedSeed")
    OUTPUT_TOOLTIPS = (
        "Returns the generated boolean value.",
        "Returns the seed used for the generation.",
    )

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "seed": ("INT", {"default": 0, "min": 0, "max": 0x7FFFFFFFFFFFFFFF, "control_after_generate": True, "tooltip": "The seed used for the current boolean result."}),
                "always_load": ("BOOLEAN", {"default": True, "tooltip": "Whether to force this node to re-execute every run."}),
            }
        }

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        if kwargs.get("always_load", False):
            return float("NaN")
        return hash(frozenset(kwargs.items()))

    def generate(self, seed=0, always_load=False):
        used_seed = int(seed)
        value = bool(random.Random(used_seed).getrandbits(1))
        return (value, used_seed)