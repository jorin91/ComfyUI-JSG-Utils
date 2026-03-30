import math


class JSGMatchStringList:
    DESCRIPTION = (
        "Checks whether enough candidate strings exactly match a control string."
    )

    CATEGORY = "JSG Utils/String"
    FUNCTION = "match"

    RETURN_TYPES = ("BOOLEAN",)
    RETURN_NAMES = ("Matches",)
    OUTPUT_TOOLTIPS = (
        "Returns true when the required number of trimmed candidate strings exactly match the trimmed control string.",
    )

    MAX_OPTIONS = 128
    MATCH_TYPES = (
        "match_1",
        "match_quarter",
        "match_half",
        "match_three_quarters",
        "match_all",
    )

    @classmethod
    def INPUT_TYPES(cls):
        required = {
            "match_type": (
                [
                    "match_1",
                    "match_quarter",
                    "match_half",
                    "match_three_quarters",
                    "match_all",
                ],
                {"default": "match_1", "tooltip": "How many candidate strings must exactly match the control value."},
            ),
            "control_value": (
                "STRING",
                {"default": "", "tooltip": "The required control string. It is trimmed before comparison."},
            ),
        }

        optional = {}
        for index in range(1, cls.MAX_OPTIONS + 1):
            optional[f"string_{index}"] = (
                "STRING",
                {"default": "", "tooltip": f"The optional candidate string {index}. Empty strings are ignored."},
            )

        return {
            "required": required,
            "optional": optional,
        }

    def _normalized_control(self, control_value):
        return control_value.strip() if isinstance(control_value, str) else ""

    def _normalized_candidates(self, kwargs):
        candidates = []
        for index in range(1, self.MAX_OPTIONS + 1):
            key = f"string_{index}"
            if key not in kwargs:
                continue

            value = kwargs.get(key, "")
            text = value.strip() if isinstance(value, str) else ""
            if text:
                candidates.append(text)
        return candidates

    def _required_matches(self, match_type, total_candidates):
        if total_candidates <= 0:
            return 0

        if match_type == "match_all":
            return total_candidates
        if match_type == "match_three_quarters":
            return math.ceil(total_candidates * 0.75)
        if match_type == "match_half":
            return math.ceil(total_candidates * 0.5)
        if match_type == "match_quarter":
            return math.ceil(total_candidates * 0.25)
        return 1

    def match(self, match_type="match_1", control_value="", **kwargs):
        control_text = self._normalized_control(control_value)
        candidates = self._normalized_candidates(kwargs)

        if not control_text or not candidates:
            return (False,)

        matches = sum(1 for value in candidates if value == control_text)
        required_matches = self._required_matches(match_type, len(candidates))
        return (matches >= required_matches,)