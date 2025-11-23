import os

class JSGFindImagePathsRecursive:
    IS_CHANGED = True

    DESCRIPTION = (
    "Recursively scans a directory and returns a LIST of image file paths.\n"
    "- max_level <= 0 → unlimited recursion depth\n"
    "- max_level > 0 → scan only this many directory levels deep\n"
    "Includes or excludes subdirectories based on the 'include_subdirectories' flag.\n"
    "Only collects files whose extensions match the provided extension list."
    )


    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "directory": ("STRING", {"default": ""}),
                # min nu negatief toestaan zodat <=0 mogelijk is
                "max_level": ("INT", {"default": 3, "min": -1, "max": 999, "step": 1}),
                "include_subdirectories": ("BOOLEAN", {"default": True}),
                "extensions": ("STRING", {
                    "default": ".png,.jpg,.jpeg,.webp,.avif,.bmp,.tif,.tiff",
                    "multiline": False
                }),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("Paths",)
    OUTPUT_IS_LIST = (True,)
    FUNCTION = "scan"
    CATEGORY = "JSG Utils/Filesystem"

    def _parse_exts(self, ext_string):
        parts = [e.strip().lower() for e in ext_string.split(",") if e.strip()]
        cleaned = []
        for e in parts:
            if not e.startswith("."):
                e = "." + e
            cleaned.append(e)
        return tuple(cleaned)

    def _iter_folders(self, root, include_subdirs, max_level):
        # altijd root meenemen
        root = os.path.abspath(root)
        yield root

        # geen subdirs? dan klaar
        if not include_subdirs:
            return

        # max_level <= 0 betekent onbeperkt
        unlimited = (max_level <= 0)

        def walk(current, level):
            # als niet onbeperkt: stop zodra we max_level hebben bereikt
            if (not unlimited) and (level >= max_level):
                return
            try:
                with os.scandir(current) as it:
                    for entry in it:
                        if entry.is_dir():
                            folder = entry.path
                            yield folder
                            yield from walk(folder, level + 1)
            except PermissionError:
                return

        # level 0 = root, dus children tellen als level 1
        yield from walk(root, 0)

    def scan(self, directory, max_level, include_subdirectories, extensions):
        if not directory or not os.path.isdir(directory):
            return ([],)

        exts = self._parse_exts(extensions)
        paths_list = []

        for folder in self._iter_folders(directory, include_subdirectories, max_level):
            try:
                entries = sorted(os.listdir(folder))
            except PermissionError:
                continue

            for name in entries:
                full_path = os.path.join(folder, name)
                if os.path.isfile(full_path) and full_path.lower().endswith(exts):
                    paths_list.append(full_path)

        return (paths_list,)
