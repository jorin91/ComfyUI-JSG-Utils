import math
import re


class JSGMatchStringList:
    DESCRIPTION = (
        "Checks whether enough candidate words match the control value(s), with configurable comparison type, case sensitivity, list splitting, and control matching mode."
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
    COMPARISON_TYPES = ("exact", "not_exact", "contains", "not_contains", "length_greater", "length_less", "length_equal")

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
                {"default": "match_all", "tooltip": "How many candidate strings must match the control value."},
            ),
            "comparison_type": (
                ["exact", "not_exact", "contains", "not_contains", "length_greater", "length_less", "length_equal"],
                {"default": "contains", "tooltip": "How each candidate is compared to the control value. Length options compare string lengths."},
            ),
            "case_sensitive": (
                "BOOLEAN",
                {"default": False, "tooltip": "When disabled, comparisons ignore case."},
            ),
            "treat_as_list": (
                "BOOLEAN",
                {"default": False, "tooltip": "When enabled, each input (including the control value) is split by the separator into individual words before matching."},
            ),
            "separator": (
                "STRING",
                {"default": ",", "tooltip": "Every individual character in this string is used as a separator when 'treat_as_list' is enabled (e.g. ', ' splits on both comma and space)."},
            ),
            "control_all_must_match": (
                "BOOLEAN",
                {"default": False, "tooltip": "When the control value is a list, a candidate counts as a match only if it matches ALL control words. When disabled, matching ANY control word is enough."},
            ),
            "control_value": (
                "STRING",
                {"default": "", "tooltip": "The required control string. Trimmed before comparison; split on the separator when 'treat_as_list' is enabled."},
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

    def _split_words(self, text, treat_as_list, separator):
        """Return a list of non-empty trimmed words from text."""
        if not isinstance(text, str):
            return []
        if treat_as_list and separator:
            pattern = "[" + re.escape(separator) + "]"
            return [w.strip() for w in re.split(pattern, text) if w.strip()]
        stripped = text.strip()
        return [stripped] if stripped else []

    def _build_control_words(self, control_value, treat_as_list, separator):
        return self._split_words(control_value, treat_as_list, separator)

    def _build_candidate_words(self, kwargs, treat_as_list, separator):
        words = []
        for index in range(1, self.MAX_OPTIONS + 1):
            key = f"string_{index}"
            if key not in kwargs:
                continue
            words.extend(self._split_words(kwargs[key], treat_as_list, separator))
        return words

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

    def _candidate_matches_control(self, candidate, control_words, comparison_type, control_all_must_match):
        """Check if a single candidate word matches the control word list."""
        if comparison_type == "contains":
            results = [needle in candidate for needle in control_words]
        elif comparison_type == "not_contains":
            results = [needle not in candidate for needle in control_words]
        elif comparison_type == "not_exact":
            results = [candidate != needle for needle in control_words]
        elif comparison_type == "length_greater":
            results = [len(candidate) > len(needle) for needle in control_words]
        elif comparison_type == "length_less":
            results = [len(candidate) < len(needle) for needle in control_words]
        elif comparison_type == "length_equal":
            results = [len(candidate) == len(needle) for needle in control_words]
        else:  # exact
            results = [candidate == needle for needle in control_words]

        return all(results) if control_all_must_match else any(results)

    def match(
        self,
        match_type="match_1",
        comparison_type="exact",
        case_sensitive=True,
        treat_as_list=False,
        separator=",",
        control_all_must_match=False,
        control_value="",
        **kwargs,
    ):
        control_words = self._build_control_words(control_value, treat_as_list, separator)
        candidates = self._build_candidate_words(kwargs, treat_as_list, separator)

        if not control_words or not candidates:
            return (False,)

        if not case_sensitive:
            control_words = [w.lower() for w in control_words]
            candidates = [w.lower() for w in candidates]

        matches = sum(
            1 for candidate in candidates
            if self._candidate_matches_control(candidate, control_words, comparison_type, control_all_must_match)
        )

        required_matches = self._required_matches(match_type, len(candidates))
        return (matches >= required_matches,)