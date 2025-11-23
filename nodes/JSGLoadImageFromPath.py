import os
from PIL import Image
import numpy as np
import torch

class JSGLoadImageFromPath:
    IS_CHANGED = True

    DESCRIPTION = (
    "Loads a single image from a file path.\n"
    "Returns the IMAGE tensor and the original path.\n"
    "Useful when iterating over a list of paths using a loop or ForEach pattern."
    )


    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "path": ("STRING", {"default": ""})
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("Image", "Path")
    FUNCTION = "load"
    CATEGORY = "JSG Utils/Image"

    def _load_image_tensor(self, path):
        im = Image.open(path).convert("RGB")
        arr = np.asarray(im).astype(np.float32) / 255.0
        return torch.from_numpy(arr)[None, ...]

    def load(self, path):
        if not path or not os.path.isfile(path):
            raise ValueError(f"Invalid file path: {path}")

        img_tensor = self._load_image_tensor(path)
        return (img_tensor, path)
