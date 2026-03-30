import os
from PIL import Image, PngImagePlugin
import numpy as np
import torch

class JSGSaveImage:
    CATEGORY = "JSG Utils/Image"
    FUNCTION = "save"
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("Image", "FilePath")
    OUTPUT_TOOLTIPS = (
        "Returns the original image input unchanged.",
        "Returns the written file path.",
    )
    OUTPUT_NODE = True

    DESCRIPTION = (
        "Saves an image to disk."
    )

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "The image tensor to save."}),
                "output_path": ("STRING", {"default": "", "tooltip": "The directory where the file should be written."}),
                "filename": ("STRING", {"default": "image", "tooltip": "The base filename without an extension."}),
                "overwrite": (["overwrite", "add_number"], {"default": "add_number", "tooltip": "How filename conflicts are handled."}),
                "number_delimiter": ("STRING", {"default": "_", "tooltip": "The delimiter inserted before the numbering suffix."}),
                "number_padding": ("INT", {"default": 2, "min": 0, "max": 8, "step": 1, "tooltip": "The zero-padding width for the numbering suffix."}),
                "file_type": ([
                    "png", "jpg", "jpeg", "webp", "bmp", "gif", "tiff"
                ], {"default": "png", "tooltip": "The output image format."}),
                "quality": ("INT", {"default": 100, "min": 0, "max": 100, "step": 1, "tooltip": "The compression quality for lossy formats."}),
                "lossless": ("BOOLEAN", {"default": True, "tooltip": "Whether to use lossless mode when the format supports it."}),
            },
            "optional": {
                "metadata": ("JSGMETADATA", {"tooltip": "The optional metadata object to embed into the saved file."}),
                "dpi": ("INT", {"default": 600, "min": 0, "max": 1200, "step": 1, "tooltip": "The optional DPI value to write into supported image formats."}),
                "caption": ("STRING", {"default": "", "multiline": False, "tooltip": "The optional caption written to a sidecar text file."}),
            }
        }

    def _ensure_dir(self, out_dir):
        out_dir = os.path.abspath(out_dir)
        os.makedirs(out_dir, exist_ok=True)
        return out_dir

    def _pick_filepath(self, out_dir, base_name, ext, overwrite, delim, pad):
        base_name = (base_name or "image").strip()
        if not base_name:
            base_name = "image"

        # overwrite = exact filename, geen nummer
        if overwrite == "overwrite":
            return os.path.join(out_dir, f"{base_name}.{ext}")

        # add_number: altijd nummeren, start bij 0
        i = 0
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
             number_padding, file_type, quality, lossless, metadata=None, dpi=0, caption=""):

        if not output_path:
            raise ValueError("output_path is empty")

        out_dir = self._ensure_dir(output_path)
        ext = file_type.lower().strip().lstrip(".")
        path = self._pick_filepath(out_dir, filename, ext, overwrite, number_delimiter, number_padding)

        pil_img = self._tensor_to_pil(image)

        save_kwargs = self._apply_metadata_save_kwargs(ext, metadata, dpi, quality, lossless)
        pil_img.save(path, **save_kwargs)

        # Optional caption sidecar (.txt) with same base name as saved image
        if caption is not None:
            cap = str(caption).strip()
            if cap != "":
                txt_path = os.path.splitext(path)[0] + ".txt"
                with open(txt_path, "w", encoding="utf-8", newline="\n") as f:
                    f.write(cap)

        # passthrough image + full filepath
        return (image, path)
