import math


class JSGBoolSwitch:
    DESCRIPTION = (
        "Evaluates a set of boolean inputs against a selected mode and outputs a single boolean result."
    )

    CATEGORY = "JSG Utils/Bool"
    FUNCTION = "evaluate"

    RETURN_TYPES = ("BOOLEAN",)
    RETURN_NAMES = ("Result",)
    OUTPUT_TOOLTIPS = ("True when the boolean inputs satisfy the selected mode.",)

    MAX_INPUTS = 64
    MODES = [
        "all_true",
        "all_false",
        "most_true",
        "most_false",
        "half_true",
        "half_false",
        "quarter_true",
        "quarter_false",
    ]

    @classmethod
    def INPUT_TYPES(cls):
        required = {
            "mode": (
                cls.MODES,
                {
                    "default": "all_true",
                    "tooltip": (
                        "Condition the inputs must satisfy. "
                        "'most' means a strict majority (> 50%). "
                        "'half' means at least 50%. "
                        "'quarter' means at least 25%."
                    ),
                },
            ),
            "input_count": (
                "INT",
                {
                    "default": 2,
                    "min": 1,
                    "max": cls.MAX_INPUTS,
                    "step": 1,
                    "tooltip": "Number of boolean inputs to evaluate. Only this many inputs are considered.",
                },
            ),
        }

        optional = {}
        for index in range(1, cls.MAX_INPUTS + 1):
            optional[f"bool_{index}"] = (
                "BOOLEAN",
                {
                    "default": False,
                    "tooltip": f"Boolean input {index}.",
                },
            )

        return {"required": required, "optional": optional}

    def _collect_values(self, input_count, kwargs):
        return [bool(kwargs.get(f"bool_{index}", False)) for index in range(1, input_count + 1)]

    def evaluate(self, mode="all_true", input_count=2, **kwargs):
        values = self._collect_values(input_count, kwargs)
        total = len(values)

        if total == 0:
            return (False,)

        true_count = sum(values)
        false_count = total - true_count

        if mode == "all_true":
            result = true_count == total
        elif mode == "all_false":
            result = false_count == total
        elif mode == "most_true":
            result = true_count > total / 2
        elif mode == "most_false":
            result = false_count > total / 2
        elif mode == "half_true":
            result = true_count >= math.ceil(total * 0.5)
        elif mode == "half_false":
            result = false_count >= math.ceil(total * 0.5)
        elif mode == "quarter_true":
            result = true_count >= math.ceil(total * 0.25)
        elif mode == "quarter_false":
            result = false_count >= math.ceil(total * 0.25)
        else:
            result = False

        return (result,)
