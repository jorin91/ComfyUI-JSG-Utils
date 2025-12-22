import os
import random
from PIL import Image
import numpy as np
import torch
import datetime
from PIL import ExifTags

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
    RETURN_TYPES = ("IMAGE", "STRING", "JSGMETADATA")
    RETURN_NAMES = ("Images", "Paths", "Metadata")
    OUTPUT_IS_LIST = (True, True, True)

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

                "apply_exif_orientation": ("BOOLEAN", {"default": True}),

                # Always Load toggle
                "always_load": ("BOOLEAN", {"default": True}),
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
        meta = self._read_metadata(path, im)

        if apply_exif_orientation:
            im = self._apply_exif_orientation(im, meta)

        rgb = im.convert("RGB")
        arr = np.asarray(rgb).astype(np.float32) / 255.0
        tensor = torch.from_numpy(arr)[None, ...]  # 1,H,W,3
        return tensor, meta
    
    def _safe_iso_dt(self, ts):
        try:
            return datetime.datetime.fromtimestamp(ts).isoformat()
        except Exception:
            return None

    def _read_metadata(self, path, im):
        meta = {
            "__type": "JSGMETADATA",
            "file": {},
            "pil": {},
            "dpi": None,
            "icc_profile": None,
            "exif": {"exif_dict": {}, "exif_bytes": None},
            "text": {},
            "raw_info_keys": [],
            "warnings": [],
        }

        # file stats
        try:
            st = os.stat(path)
            meta["file"] = {
                "path": os.path.abspath(path),
                "size_bytes": st.st_size,
                "mtime": self._safe_iso_dt(st.st_mtime),
                "atime": self._safe_iso_dt(st.st_atime),
                # st_ctime is platform dependent (Windows: creation time, Unix: metadata change)
                "ctime": self._safe_iso_dt(st.st_ctime),
            }
        except Exception as e:
            meta["warnings"].append(f"stat_failed: {e}")

        # basic PIL
        try:
            meta["pil"] = {
                "format": getattr(im, "format", None),
                "mode": getattr(im, "mode", None),
                "size": list(getattr(im, "size", (0, 0))),
            }
        except Exception as e:
            meta["warnings"].append(f"pil_basic_failed: {e}")

        # PIL info dict (png text, icc, dpi, xmp keys etc)
        try:
            info = dict(getattr(im, "info", {}) or {})
            meta["raw_info_keys"] = sorted([str(k) for k in info.keys()])

            if "dpi" in info:
                meta["dpi"] = info.get("dpi")

            if "icc_profile" in info:
                # kan groot zijn; toch bewaren (bytes) zodat je later kunt kiezen of je het embed
                meta["icc_profile"] = info.get("icc_profile")

            # tekstchunks (PNG, soms WEBP/XMP keys)
            # neem alleen str/number/bool/list/dict; bytes gaan via aparte velden
            text = {}
            for k, v in info.items():
                if k in ("icc_profile",):
                    continue
                if isinstance(v, (str, int, float, bool, list, dict)) or v is None:
                    text[str(k)] = v
                elif isinstance(v, bytes):
                    # bytes laten we niet in text dumpen; te groot/ruw
                    text[str(k)] = f"[bytes:{len(v)}]"
                else:
                    text[str(k)] = str(v)
            meta["text"] = text
        except Exception as e:
            meta["warnings"].append(f"pil_info_failed: {e}")

        # EXIF (vooral JPEG/TIFF, soms WEBP)
        try:
            exif_obj = None
            try:
                exif_obj = im.getexif()
            except Exception:
                exif_obj = None

            if exif_obj:
                # tag id -> readable name
                tag_map = ExifTags.TAGS
                exif_dict = {}
                for tag_id, value in exif_obj.items():
                    name = tag_map.get(tag_id, str(tag_id))
                    # zorg dat het json-vriendelijk blijft
                    if isinstance(value, bytes):
                        exif_dict[name] = f"[bytes:{len(value)}]"
                    else:
                        exif_dict[name] = value
                meta["exif"]["exif_dict"] = exif_dict

            # raw exif bytes (voor lossless re-embed waar mogelijk)
            try:
                exif_bytes = im.info.get("exif", None)
                meta["exif"]["exif_bytes"] = exif_bytes
            except Exception:
                pass

        except Exception as e:
            meta["warnings"].append(f"exif_failed: {e}")

        return meta

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