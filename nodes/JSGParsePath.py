import os
import re

class JSGParsePath:
    DESCRIPTION = (
    "Inspects a filesystem path to identify its file or folder characteristics."
    )

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "path": ("STRING", {"default": "", "tooltip": "The filesystem path to inspect. It must already exist."}),
            }
        }

    RETURN_TYPES = ("BOOLEAN", "BOOLEAN", "STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = (
        "IsFolder",
        "IsFile",
        "FolderPath",
        "FilenameExt",
        "FilenameOnly",
        "ExtensionOnly",
    )
    OUTPUT_TOOLTIPS = (
        "Returns whether the path is a folder.",
        "Returns whether the path is a file.",
        "Returns the folder portion of the path.",
        "Returns the filename with extension.",
        "Returns the filename without extension.",
        "Returns the file extension without a leading dot.",
    )

    FUNCTION = "parse"
    CATEGORY = "JSG Utils/File"

    def parse(self, path):
        if not path or not isinstance(path, str):
            raise ValueError("Input path is empty or invalid.")

        normalized = os.path.abspath(path)

        exists = os.path.exists(normalized)
        if not exists:
            raise ValueError(f"Path does not exist: {normalized}")

        is_folder = os.path.isdir(normalized)
        is_file = os.path.isfile(normalized)

        # Prepare outputs
        folder_path = ""
        filename_ext = ""
        filename_only = ""
        ext_only = ""

        if is_folder:
            folder_path = normalized
        else:
            # File case
            folder_path = os.path.dirname(normalized)
            filename_ext = os.path.basename(normalized)

            # Regex: (name)(.ext)
            m = re.match(r"^(?P<name>.+?)(?:\.(?P<ext>[^.]+))?$", filename_ext)

            if m:
                filename_only = m.group("name") or ""
                ext_only = m.group("ext") or ""
            else:
                # fallback
                filename_only = filename_ext
                ext_only = ""

        return (
            is_folder,
            is_file,
            folder_path,
            filename_ext,
            filename_only,
            ext_only
        )