import os
import random
from PIL import Image
import numpy as np
import torch

from .JSGMetadataUtils import read_metadata

class JSGFindImagesRecursiveList:
    DESCRIPTION = (
        "Finds and loads multiple images from a directory tree."
    )

    CATEGORY = "JSG Utils/Image"
    FUNCTION = "scan"
    RETURN_TYPES = ("IMAGE", "STRING", "JSGMETADATA")
    RETURN_NAMES = ("Images", "Paths", "Metadata")
    OUTPUT_TOOLTIPS = (
        "Returns the loaded image tensors.",
        "Returns the file paths for the loaded images.",
        "Returns the metadata objects for the loaded images.",
    )
    OUTPUT_IS_LIST = (True, True, True)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "directory": ("STRING", {"default": "", "tooltip": "The root directory to scan for images."}),

                # max depth
                "max_level": ("INT", {"default": 3, "min": -1, "max": 999, "step": 1, "tooltip": "The maximum recursion depth. Values less than or equal to 0 mean unlimited depth."}),
                "include_subdirectories": ("BOOLEAN", {"default": True, "tooltip": "Whether to scan subdirectories recursively."}),

                # index + cap
                "start_index": ("INT", {"default": 0, "min": 0, "max": 999999, "tooltip": "The number of sorted items to skip before loading begins."}),
                "load_cap": ("INT", {"default": 0, "min": 0, "max": 999999, "tooltip": "The maximum number of images to load. Use 0 for no limit."}),

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
                ], {"default": "name_asc", "tooltip": "How the discovered files are ordered before start_index and load_cap are applied."}),

                # extension filter
                "extensions": ("STRING", {
                    "default": ".png,.jpg,.jpeg,.webp,.avif,.bmp,.tif,.tiff",
                    "multiline": False,
                    "tooltip": "The file extensions to include, separated by commas."
                }),

                "apply_exif_orientation": ("BOOLEAN", {"default": True, "tooltip": "Whether to apply EXIF orientation before loading the image."}),

                # Always Load toggle
                "always_load": ("BOOLEAN", {"default": True, "tooltip": "Whether to force this node to re-execute every run."}),
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

    def _load_image_tensor_and_meta(self, path, apply_exif_orientation):
        im = Image.open(path)
        meta = read_metadata(path, im)

        if apply_exif_orientation:
            im = self._apply_exif_orientation(im, meta)

        rgb = im.convert("RGB")
        arr = np.asarray(rgb).astype(np.float32) / 255.0
        tensor = torch.from_numpy(arr)[None, ...]  # 1,H,W,3
        return tensor, meta
    
    def _apply_exif_orientation(self, im, meta):
        try:
            orientation = meta.get("exif", {}).get("exif_dict", {}).get("Orientation", None)
            if orientation == 3:
                return im.rotate(180, expand=True)
            elif orientation == 6:
                return im.rotate(-90, expand=True)
            elif orientation == 8:
                return im.rotate(90, expand=True)
        except Exception:
            pass
        return im

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
         start_index, load_cap, sorting_method, extensions,
         apply_exif_orientation, always_load):

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
        metadata_list = []

        for path in sliced:
            try:
                img_tensor, meta = self._load_image_tensor_and_meta(path, apply_exif_orientation)
                images_list.append(img_tensor)
                paths_list.append(path)
                metadata_list.append(meta)
            except Exception:
                continue

        return (images_list, paths_list, metadata_list)