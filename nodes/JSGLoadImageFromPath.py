import os
from PIL import Image
import numpy as np
import torch
import datetime
from PIL import ExifTags

class JSGLoadImageFromPath:
    IS_CHANGED = True
    OUTPUT_TOOLTIPS = (
        "Returns the loaded image tensor.",
        "Returns the loaded file path.",
        "Returns the extracted image metadata.",
    )

    DESCRIPTION = (
    "Loads an image from a file path."
    )


    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "path": ("STRING", {"default": "", "tooltip": "The file path of the image to load."}),
                "apply_exif_orientation": ("BOOLEAN", {"default": True, "tooltip": "Whether to apply EXIF orientation before loading the image."})
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING", "JSGMETADATA")
    RETURN_NAMES = ("Image", "Path", "Metadata")
    FUNCTION = "load"
    CATEGORY = "JSG Utils/Image"

    def _load_image_tensor(self, path, apply_exif_orientation):
        im = Image.open(path)
        meta = self._read_metadata(path, im)

        if apply_exif_orientation:
            im = self._apply_exif_orientation(im, meta)

        rgb = im.convert("RGB")
        arr = np.asarray(rgb).astype(np.float32) / 255.0
        img_tensor = torch.from_numpy(arr)[None, ...]

        return img_tensor, meta
    
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

    def load(self, path, apply_exif_orientation):
        if not path or not os.path.isfile(path):
            raise ValueError(f"Invalid file path: {path}")

        img_tensor, meta = self._load_image_tensor(path, apply_exif_orientation)
        return (img_tensor, path, meta)
