import os
from PIL import Image
import numpy as np
import torch

from .JSGMetadataUtils import read_metadata

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
        meta = read_metadata(path, im)

        if apply_exif_orientation:
            im = self._apply_exif_orientation(im, meta)

        rgb = im.convert("RGB")
        arr = np.asarray(rgb).astype(np.float32) / 255.0
        img_tensor = torch.from_numpy(arr)[None, ...]

        return img_tensor, meta
    
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
