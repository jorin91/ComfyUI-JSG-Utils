import os
import random
from PIL import Image
import numpy as np
import torch

class JSGFindImagesRecursiveList:
    DESCRIPTION = (
        "Recursively scans a directory and loads all matching images.\n"
        "\n"
        "Features:\n"
        "- max_level <= 0 → unlimited recursion depth\n"
        "- max_level > 0 → scan only this many directory levels deep\n"
        "- start_index → skip the first N items after sorting\n"
        "- load_cap → maximum number of images to load (0 = no limit)\n"
        "- sorting_method → choose how the file list should be ordered before slicing\n"
        "  (name, date, size, extension, directory, random, or none)\n"
        "- Always Load → forces this node to re-execute each run\n"
        "\n"
        "Outputs two parallel lists:\n"
        "1) A list of IMAGE tensors (not batched)\n"
        "2) A list of file paths in the same order\n"
        "Useful when you want to process multiple images at once without batching."
    )

    CATEGORY = "JSG Utils/Image"
    FUNCTION = "scan"
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("Images", "Paths")
    OUTPUT_IS_LIST = (True, True)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "directory": ("STRING", {"default": ""}),

                # max depth
                "max_level": ("INT", {"default": 3, "min": -1, "max": 999, "step": 1}),
                "include_subdirectories": ("BOOLEAN", {"default": True}),

                # index + cap
                "start_index": ("INT", {"default": 0, "min": 0, "max": 999999}),
                "load_cap": ("INT", {"default": 0, "min": 0, "max": 999999}),

                # sorting as dropdown enum
                "sorting_method": ([
                    "name_asc",
                    "name_desc",
                    "date_newest",
                    "date_oldest",
                    "size_smallest",
                    "size_largest",
                    "extension_asc",
                    "extension_desc",
                    "directory_asc",
                    "directory_desc",
                    "random",
                    "none"
                ], {"default": "name_asc"}),

                # extension filter
                "extensions": ("STRING", {
                    "default": ".png,.jpg,.jpeg,.webp,.avif,.bmp,.tif,.tiff",
                    "multiline": False
                }),

                # Always Load toggle
                "always_load": ("BOOLEAN", {"default": False}),
            }
        }

    # ------------------------------------------------
    # Comfy: change detection based on Always Load
    # ------------------------------------------------

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        if 'always_load' in kwargs and kwargs['always_load']:
            return float("NaN")
        else:
            return hash(frozenset(kwargs))

    # ------------------------------------------------
    # Internal helpers
    # ------------------------------------------------

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

    # ------------------------------------------------
    # Sorting method
    # ------------------------------------------------

    def _sort_paths(self, paths, method):
        if method == "none":
            return paths

        if method == "name_asc":
            return sorted(paths)

        if method == "name_desc":
            return sorted(paths, reverse=True)

        if method == "date_newest":
            return sorted(paths, key=lambda p: os.path.getmtime(p), reverse=True)

        if method == "date_oldest":
            return sorted(paths, key=lambda p: os.path.getmtime(p))

        if method == "size_smallest":
            return sorted(paths, key=lambda p: os.path.getsize(p))

        if method == "size_largest":
            return sorted(paths, key=lambda p: os.path.getsize(p), reverse=True)

        if method == "extension_asc":
            return sorted(paths, key=lambda p: os.path.splitext(p)[1].lower())

        if method == "extension_desc":
            return sorted(paths, key=lambda p: os.path.splitext(p)[1].lower(), reverse=True)

        if method == "directory_asc":
            return sorted(paths, key=lambda p: os.path.dirname(p).lower())

        if method == "directory_desc":
            return sorted(paths, key=lambda p: os.path.dirname(p).lower(), reverse=True)

        if method == "random":
            # Internal random seed per run (no extra property needed)
            # Using os.urandom to ensure a fresh seed each call
            seed = int.from_bytes(os.urandom(8), "big")
            rng = random.Random(seed)
            shuffled = paths[:]
            rng.shuffle(shuffled)
            return shuffled

        return paths

    # ------------------------------------------------
    # Main
    # ------------------------------------------------

    def scan(self, directory, max_level, include_subdirectories,
             start_index, load_cap, sorting_method, extensions, always_load):

        if not directory or not os.path.isdir(directory):
            return ([], [])

        exts = self._parse_exts(extensions)

        # 1) Collect paths
        raw_paths = []

        for folder in self._iter_folders(directory, include_subdirectories, max_level):
            try:
                entries = os.listdir(folder)
            except PermissionError:
                continue

            for name in entries:
                full_path = os.path.join(folder, name)
                if os.path.isfile(full_path) and full_path.lower().endswith(exts):
                    raw_paths.append(full_path)

        # 2) Sort
        sorted_paths = self._sort_paths(raw_paths, sorting_method)

        # 3) Slice by start_index + load_cap
        if start_index < 0:
            start_index = 0

        sliced = sorted_paths[start_index:]

        if load_cap > 0:
            sliced = sliced[:load_cap]

        # 4) Load images in this order
        images_list = []
        paths_list = []

        for path in sliced:
            try:
                img_tensor = self._load_image_tensor(path)
                images_list.append(img_tensor)
                paths_list.append(path)
            except Exception:
                continue

        return (images_list, paths_list)
