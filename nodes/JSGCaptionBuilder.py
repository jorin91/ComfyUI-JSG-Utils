class JSGCaptionBuilder:
    CATEGORY = "JSG Utils/Caption"
    FUNCTION = "build"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("Caption",)

    DESCRIPTION = (
        "Builds a multiline caption for LoRA training with optional filtering.\n\n"
        "OUTPUT FORMAT:\n"
        "Line 1: <key_token>, <filtered taglist>   (taglist only if provided)\n"
        "Line 2: <filtered description>            (only if provided)\n\n"
        "TAG FILTERING:\n"
        "- Tags are split by commas.\n"
        "- Each tag is split into words by spaces and underscores.\n"
        "- Exclude list is comma-separated entries.\n"
        "  • Single-word exclude removes a tag if that exact word is present.\n"
        "  • Multi-word exclude removes a tag if ALL exclude-words are present (order independent).\n"
        "- Matching is exact per word (e.g. 'leg' does not match 'legs').\n"
        "- Remaining tags are rebuilt as a comma-separated list.\n\n"
        "DESCRIPTION FILTERING:\n"
        "- Description is split on periods and commas into fragments.\n"
        "- A fragment is removed if ANY exclude entry matches:\n"
        "  • single-word: exact word present\n"
        "  • multi-word: all words present (order independent)\n"
        "- Punctuation is normalized to prevent '..', ',,' or ',.' artifacts.\n\n"
        "INPUT NOTES:\n"
        "- key_token is required.\n"
        "- taglist, description and exclude lists are optional.\n"
        "- Exclude lists are comma-separated entries (entries may contain spaces/underscores).\n"
        "- Output is a single multiline STRING."
    )

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "key_token": ("STRING", {"default": ""}),
            },
            "optional": {
                "taglist": ("STRING", {"default": "", "multiline": True}),
                "tag_exclude": ("STRING", {"default": ""}),
                "description": ("STRING", {"default": "", "multiline": True}),
                "description_exclude": ("STRING", {"default": ""}),
            }
        }

    def build(self, key_token, taglist="", tag_exclude="", description="", description_exclude=""):
        key = (key_token or "").strip()
        if not key:
            raise ValueError("key_token is required and cannot be empty")

        # ---------- helpers ----------
        def split_words(text):
            # split on underscore and whitespace, exact-word matching
            if not text:
                return []
            return [w for w in text.replace("_", " ").lower().split() if w]

        def parse_exclude_entries(text):
            """
            Returns a list of exclude word-sets.
            - Input: comma-separated entries
            - Each entry can be single or multi-word
            - Matching is: exclude_set ⊆ tag_words_set (order independent, exact words)
            """
            entries = []
            if not text:
                return entries
            for raw in str(text).split(","):
                entry = raw.strip()
                if not entry:
                    continue
                ws = set(split_words(entry))
                if ws:
                    entries.append(ws)
            return entries

        def matches_excludes(words_set, exclude_sets):
            # True if any exclude set is fully contained in words_set
            if not exclude_sets or not words_set:
                return False
            for ex in exclude_sets:
                if ex.issubset(words_set):
                    return True
            return False

        tag_exclude_sets = parse_exclude_entries(tag_exclude)
        desc_exclude_sets = parse_exclude_entries(description_exclude)

        # ---------- TAG FILTER ----------
        filtered_tags = []
        if taglist:
            for raw_tag in str(taglist).split(","):
                tag = raw_tag.strip()
                if not tag:
                    continue

                tag_words = set(split_words(tag))

                # drop if any exclude entry matches (single or multi-word, order independent)
                if matches_excludes(tag_words, tag_exclude_sets):
                    continue

                # keep original tag unchanged (underscores/spaces preserved)
                filtered_tags.append(tag)

        tag_string = ", ".join(filtered_tags)

        # ---------- DESCRIPTION FILTER ----------
        desc = (description or "").strip()
        if desc and desc_exclude_sets:
            parts = []
            # split on '.' first, then ',' inside; rebuild later
            for part in desc.replace("..", ".").replace(",,", ",").split("."):
                subparts = []
                for sub in part.split(","):
                    frag = sub.strip()
                    if not frag:
                        continue

                    frag_words = set(split_words(frag))
                    if matches_excludes(frag_words, desc_exclude_sets):
                        continue

                    subparts.append(frag)

                if subparts:
                    parts.append(", ".join(subparts))

            desc = ". ".join(parts)

        # cleanup punctuation artifacts
        while ",," in desc:
            desc = desc.replace(",,", ",")
        while ".." in desc:
            desc = desc.replace("..", ".")
        desc = desc.replace(",.", ".")
        desc = desc.strip(" ,.")

        # ---------- BUILD OUTPUT ----------
        if tag_string:
            line1 = f"{key}, {tag_string}"
        else:
            line1 = key

        if desc:
            caption = f"{line1}\n{desc}"
        else:
            caption = line1

        return (caption,)
