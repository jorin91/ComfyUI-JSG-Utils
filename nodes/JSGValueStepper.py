from decimal import Decimal, ROUND_HALF_UP


class JSGValueStepper:
    DESCRIPTION = (
        "Steps a numeric value, outputs it as float, int, and string, then updates "
        "its value widget after each run using increment or decrement mode."
    )

    CATEGORY = "JSG Utils/Number"
    FUNCTION = "step_value"

    RETURN_TYPES = ("INT", "FLOAT", "STRING")
    RETURN_NAMES = ("Int", "Float", "String")
    OUTPUT_TOOLTIPS = (
        "The stepped value rounded to the nearest integer.",
        "The stepped value rounded to 2 decimal places.",
        "The stepped value formatted with 2 decimal places.",
    )

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "value": (
                    "FLOAT",
                    {
                        "default": 0.0,
                        "step": 0.01,
                        "round": 0.01,
                        "tooltip": "The current value. This widget is updated after each run by the JSG frontend extension.",
                    },
                ),
                "mode": (
                    ["increment", "decrement"],
                    {
                        "default": "increment",
                        "tooltip": "Whether the value widget should increase or decrease after each run.",
                    },
                ),
                "step": (
                    "FLOAT",
                    {
                        "default": 1.0,
                        "min": 0.0,
                        "step": 0.01,
                        "round": 0.01,
                        "tooltip": "The amount added to or subtracted from value after each run.",
                    },
                ),
                "include_start": (
                    "BOOLEAN",
                    {
                        "default": False,
                        "tooltip": (
                            "When enabled, output the current value first and still update "
                            "the widget to the stepped value for the next run."
                        ),
                    },
                ),
                "always_load": (
                    "BOOLEAN",
                    {
                        "default": True,
                        "tooltip": "Whether to force this node to re-execute every run.",
                    },
                ),
            }
        }

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        if kwargs.get("always_load", False):
            return float("NaN")
        return hash(frozenset(kwargs.items()))

    def step_value(self, value=0.0, mode="increment", step=1.0, include_start=False, always_load=True):
        value_decimal = Decimal(str(value))
        step_decimal = abs(Decimal(str(step)))

        if mode == "decrement":
            stepped_value = value_decimal - step_decimal
        else:
            stepped_value = value_decimal + step_decimal

        output_value = value_decimal if include_start else stepped_value
        rounded_output = output_value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        rounded_float = float(rounded_output)
        rounded_int = int(rounded_output.to_integral_value(rounding=ROUND_HALF_UP))
        return (rounded_int, rounded_float, f"{rounded_float:.2f}")
