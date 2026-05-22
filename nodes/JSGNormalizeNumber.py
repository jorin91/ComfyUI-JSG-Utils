class JSGNormalizeNumber:
    DESCRIPTION = (
        "Accepts a FLOAT or INT value (whichever is connected; float takes priority "
        "when both are connected) and normalises it to a fixed-width string. "
        "\n"
        "decimal_digits pads the fractional part (float only): 1.0 -> 1.0000. "
        "integer_digits pads the integer part (both modes): 1.0 -> 0001.0 or 1 -> 0001. "
        "\n"
        "Optionally removes the decimal separator and absolute value."
    )

    CATEGORY = "JSG Utils/Number"
    FUNCTION = "normalize"

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("value",)
    OUTPUT_TOOLTIPS = ("The normalised number as a fixed-width string.",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "pad_decimals": (
                    "BOOLEAN",
                    {
                        "default": True,
                        "tooltip": "When enabled, the fractional part is padded to decimal_digits places (float only).",
                    },
                ),
                "decimal_digits": (
                    "INT",
                    {
                        "default": 2,
                        "min": 0,
                        "max": 20,
                        "tooltip": (
                            "Float mode only. Active when pad_decimals is enabled. "
                            "Number of digits after the decimal point. "
                            "Example: 1.0 with decimal_digits=4 -> 1.0000."
                        ),
                    },
                ),
                "pad_integer": (
                    "BOOLEAN",
                    {
                        "default": False,
                        "tooltip": "When enabled, the integer part is left-padded with zeros to integer_digits width (float and int).",
                    },
                ),
                "integer_digits": (
                    "INT",
                    {
                        "default": 1,
                        "min": 1,
                        "max": 20,
                        "tooltip": (
                            "Active when pad_integer is enabled. "
                            "Minimum number of digits before the decimal point, left-padded with zeros. "
                            "Applies to both float and int. "
                            "Example: 1 with integer_digits=4 -> 0001, or 1.0 -> 0001.0."
                        ),
                    },
                ),
            },
            "optional": {
                "float_value": (
                    "FLOAT",
                    {
                        "forceInput": True,
                        "tooltip": "Primary float input. Takes priority over int_value when both are connected.",
                    },
                ),
                "int_value": (
                    "INT",
                    {
                        "forceInput": True,
                        "tooltip": "Fallback integer input. Used only when float_value is not connected.",
                    },
                ),
                "absolute_value": (
                    "BOOLEAN",
                    {
                        "default": False,
                        "tooltip": "When enabled, the sign is stripped and the number is always treated as positive.",
                    },
                ),
                "remove_separator": (
                    "BOOLEAN",
                    {
                        "default": False,
                        "tooltip": (
                            "Float mode only. Removes the decimal point so '1.00' becomes '100' "
                            "and '0.90' becomes '090' (or '90' when skip_leading_zero is enabled)."
                        ),
                    },
                ),
                "skip_leading_zero": (
                    "BOOLEAN",
                    {
                        "default": False,
                        "tooltip": (
                            "Float mode only. Active only when remove_separator is enabled. "
                            "When the integer part is 0, drop it: '0.90' becomes '90' instead of '090'."
                        ),
                    },
                ),
            },
        }

    def normalize(
        self,
        pad_decimals: bool,
        decimal_digits: int,
        pad_integer: bool,
        integer_digits: int,
        float_value=None,
        int_value=None,
        absolute_value: bool = False,
        remove_separator: bool = False,
        skip_leading_zero: bool = False,
    ) -> tuple:
        # ── Pick first non-None input; float takes priority ─────────────────
        if float_value is not None:
            raw_value = float(float_value)
            is_float = True
        elif int_value is not None:
            raw_value = int(int_value)
            is_float = False
        else:
            return ("",)

        # ── Absolute value ───────────────────────────────────────────────────
        if absolute_value:
            raw_value = abs(raw_value)

        # ── Format ──────────────────────────────────────────────────────────
        if is_float:
            # Format fractional part
            if pad_decimals:
                formatted = f"{raw_value:.{decimal_digits}f}"
            else:
                formatted = repr(float(raw_value))  # natural Python repr, no trailing junk

            # Split into sign, integer part, fractional part
            if formatted.startswith("-"):
                sign = "-"
                formatted = formatted[1:]
            else:
                sign = ""

            if "." in formatted:
                int_part, frac_part = formatted.split(".", 1)
            else:
                int_part, frac_part = formatted, ""

            # Pad integer part
            if pad_integer:
                int_part = int_part.zfill(integer_digits)

            if remove_separator:
                if skip_leading_zero and int_part.lstrip("0") == "":
                    # integer part is all zeros — drop it entirely
                    result = sign + frac_part
                else:
                    result = sign + int_part + frac_part
            else:
                if frac_part:
                    result = sign + int_part + "." + frac_part
                else:
                    result = sign + int_part

        else:
            value_int = int(raw_value)
            sign = "-" if value_int < 0 else ""
            digit_str = str(abs(value_int))
            if pad_integer:
                digit_str = digit_str.zfill(integer_digits)
            result = sign + digit_str

        return (result,)
