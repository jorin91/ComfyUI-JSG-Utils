import os
from PIL import Image
import numpy as np
import torch

class JSGFindImagesRecursiveList:
    IS_CHANGED = True

    DESCRIPTION = (
    "Recursively scans a directory and loads all matching images.\n"
    "- max_level <= 0 → unlimited recursion depth\n"
    "- max_level > 0 → scan only this many directory levels deep\n"
    "Outputs two parallel lists:\n"
    "1) A list of IMAGE tensors (not batched)\n"
    "2) A list of file paths in the same order\n"
    "Useful when you want to process multiple images at once without batching."
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

    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("Images", "Paths")
    OUTPUT_IS_LIST = (True, True)
    FUNCTION = "scan"
    CATEGORY = "JSG Utils/Image"

    def _parse_exts(self, ext_string):
        parts = [e.strip().lower() for e in ext_string.split(",") if e.strip()]
        cleaned = []
        for e in parts:
            if not e.startswith("."):
                e = "." + e
            cleaned.append(e)
        return tuple(cleaned)

    def _iter_folders(self, root, include_subdirs, max_level):
        root = os.path.abspath(root)
        yield root

        if not include_subdirs:
            return

        unlimited = (max_level <= 0)

        def walk(current, level):
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

        yield from walk(root, 0)

    def _load_image_tensor(self, path):
        im = Image.open(path).convert("RGB")
        arr = np.asarray(im).astype(np.float32) / 255.0
        tensor = torch.from_numpy(arr)[None, ...]  # 1,H,W,3
        return tensor

    def scan(self, directory, max_level, include_subdirectories, extensions):
        if not directory or not os.path.isdir(directory):
            return ([], [])

        exts = self._parse_exts(extensions)

        paths_list = []
        images_list = []

        for folder in self._iter_folders(directory, include_subdirectories, max_level):
            try:
                entries = sorted(os.listdir(folder))
            except PermissionError:
                continue

            for name in entries:
                full_path = os.path.join(folder, name)
                if not os.path.isfile(full_path):
                    continue

                if full_path.lower().endswith(exts):
                    try:
                        img_tensor = self._load_image_tensor(full_path)
                        images_list.append(img_tensor)
                        paths_list.append(full_path)
                    except Exception:
                        continue

        return (images_list, paths_list)
