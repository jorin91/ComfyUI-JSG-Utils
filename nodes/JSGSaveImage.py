import os
from PIL import Image, PngImagePlugin
import numpy as np
import torch

class JSGSaveImage:
    CATEGORY = "JSG Utils/Image"
    FUNCTION = "save"
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("Image", "FilePath")

    DESCRIPTION = (
        "Saves an IMAGE tensor to disk with optional metadata.\n\n"
        "QUALITY BEHAVIOR:\n"
        "- PNG / TIFF / BMP: always lossless (quality setting ignored).\n"
        "- JPG / JPEG: lossy, controlled by 'quality' (0–100).\n"
        "- WEBP:\n"
        "  • lossless = True  → true lossless WEBP\n"
        "  • lossless = False → lossy WEBP controlled by 'quality'.\n\n"
        "METADATA:\n"
        "- DPI and ICC profile are preserved when available.\n"
        "- EXIF is preserved for JPG/JPEG/TIFF when provided.\n"
        "- PNG stores metadata as text chunks.\n\n"
        "RETURNS:\n"
        "- Passthrough IMAGE\n"
        "- Full output file path"
    )

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "output_path": ("STRING", {"default": ""}),
                "filename": ("STRING", {"default": "image"}),
                "overwrite": (["overwrite", "add_number"], {"default": "add_number"}),
                "number_delimiter": ("STRING", {"default": "_"}),
                "number_padding": ("INT", {"default": 2, "min": 0, "max": 8, "step": 1}),
                "file_type": ([
                    "png", "jpg", "jpeg", "webp", "bmp", "gif", "tiff"
                ], {"default": "png"}),
                "quality": ("INT", {"default": 100, "min": 0, "max": 100, "step": 1}),
                "lossless": ("BOOLEAN", {"default": True}),
            },
            "optional": {
                "metadata": ("JSGMETADATA",),
                "dpi": ("INT", {"default": 600, "min": 0, "max": 1200, "step": 1}),
            }
        }

    def _ensure_dir(self, out_dir):
        out_dir = os.path.abspath(out_dir)
        os.makedirs(out_dir, exist_ok=True)
        return out_dir

    def _pick_filepath(self, out_dir, base_name, ext, overwrite, delim, pad):
        # sanitize minimal
        base_name = (base_name or "image").strip()
        if not base_name:
            base_name = "image"

        candidate = os.path.join(out_dir, f"{base_name}.{ext}")

        if overwrite == "overwrite":
            return candidate

        # add_number: find first free
        if not os.path.exists(candidate):
            return candidate

        i = 1
        while True:
            num = str(i).zfill(pad) if pad and pad > 0 else str(i)
            candidate = os.path.join(out_dir, f"{base_name}{delim}{num}.{ext}")
            if not os.path.exists(candidate):
                return candidate
            i += 1

    def _tensor_to_pil(self, image_tensor):
        # Comfy IMAGE: meestal shape [B,H,W,3], float 0..1
        if isinstance(image_tensor, torch.Tensor):
            t = image_tensor
        else:
            t = torch.from_numpy(image_tensor)

        if t.dim() == 4:
            t = t[0]  # neem eerste
        t = t.clamp(0, 1)
        arr = (t.cpu().numpy() * 255.0).astype(np.uint8)
        return Image.fromarray(arr, mode="RGB")

    def _apply_metadata_save_kwargs(self, ext, meta, dpi_value, quality, lossless):
        kwargs = {}

        # DPI
        if dpi_value and dpi_value > 0:
            kwargs["dpi"] = (dpi_value, dpi_value)
        elif isinstance(meta, dict):
            # fallback naar meta dpi
            mdpi = meta.get("dpi")
            if isinstance(mdpi, (list, tuple)) and len(mdpi) == 2:
                kwargs["dpi"] = tuple(mdpi)

        # ICC profile
        if isinstance(meta, dict):
            icc = meta.get("icc_profile")
            if isinstance(icc, (bytes, bytearray)):
                kwargs["icc_profile"] = bytes(icc)

        # Format specifics
        if ext in ("jpg", "jpeg"):
            kwargs["quality"] = int(quality)
            kwargs["optimize"] = True
            # EXIF bytes (als aanwezig)
            if isinstance(meta, dict):
                exif_bytes = (((meta.get("exif") or {}).get("exif_bytes")))
                if isinstance(exif_bytes, (bytes, bytearray)):
                    kwargs["exif"] = bytes(exif_bytes)

        elif ext == "webp":
            if lossless:
                kwargs["lossless"] = True
            else:
                kwargs["quality"] = int(quality)

        elif ext == "png":
            # PNG text chunks
            if isinstance(meta, dict):
                text = meta.get("text") or {}
                if isinstance(text, dict) and text:
                    pnginfo = PngImagePlugin.PngInfo()
                    for k, v in text.items():
                        # alleen string achtige dingen; maak het voorspelbaar
                        if v is None:
                            s = ""
                        elif isinstance(v, (str, int, float, bool)):
                            s = str(v)
                        else:
                            s = str(v)
                        # pillow verwacht string keys/values
                        pnginfo.add_text(str(k), s)
                    kwargs["pnginfo"] = pnginfo

        elif ext == "tiff":
            # TIFF kan exif soms ook
            if isinstance(meta, dict):
                exif_bytes = (((meta.get("exif") or {}).get("exif_bytes")))
                if isinstance(exif_bytes, (bytes, bytearray)):
                    kwargs["exif"] = bytes(exif_bytes)

        # bmp/gif: nauwelijks metadata ondersteuning
        return kwargs

    def save(self, image, output_path, filename, overwrite, number_delimiter,
             number_padding, file_type, quality, lossless, metadata=None, dpi=0):

        if not output_path:
            raise ValueError("output_path is empty")

        out_dir = self._ensure_dir(output_path)
        ext = file_type.lower().strip().lstrip(".")
        path = self._pick_filepath(out_dir, filename, ext, overwrite, number_delimiter, number_padding)

        pil_img = self._tensor_to_pil(image)

        save_kwargs = self._apply_metadata_save_kwargs(ext, metadata, dpi, quality, lossless)
        pil_img.save(path, **save_kwargs)

        # passthrough image + full filepath
        return (image, path)
