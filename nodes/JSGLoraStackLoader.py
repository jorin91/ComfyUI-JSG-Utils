import os
import struct
import json

import folder_paths
import comfy.sd
import comfy.utils

MAX_LORAS = 6

# Key used to store the LoRA stack in the model's attachment dict.
# Also consumed by JSGModelInfo.
ATTACHMENT_KEY = "jsg_lora_stack"

# Safetensors __metadata__ keys to extract, mapped to friendly names.
_METADATA_KEYS = [
    ("modelspec.title",           "title"),
    ("ss_output_name",            "output_name"),
    ("modelspec.architecture",    "architecture"),
    ("ss_base_model_version",     "base_model"),
    ("ss_sd_model_name",          "trained_on"),
    ("ss_network_dim",            "network_dim"),
    ("ss_network_alpha",          "network_alpha"),
    ("ss_epoch",                  "epoch"),
    ("ss_steps",                  "steps"),
    ("modelspec.prediction_type", "prediction_type"),
    ("modelspec.resolution",      "resolution"),
    ("ss_training_comment",       "comment"),
]


def _read_lora_metadata(lora_path: str) -> dict:
    """Read the __metadata__ header from a safetensors LoRA file.
    Returns an empty dict when the file has no metadata or is not safetensors."""
    try:
        with open(lora_path, "rb") as f:
            size = struct.unpack("<Q", f.read(8))[0]
            header = json.loads(f.read(size))
        raw = header.get("__metadata__", {})
        result = {}
        for src_key, dst_key in _METADATA_KEYS:
            val = raw.get(src_key)
            if val is not None and str(val) not in ("None", ""):
                result[dst_key] = str(val)
        return result
    except Exception:
        return {}


_STRENGTH_PROPS = {
    "default": 1.0,
    "min": -100.0,
    "max": 100.0,
    "step": 0.01,
}


def _apply_loras(model, clip, slots: list) -> tuple:
    """Apply a list of (lora_name, strength_model, strength_clip) tuples.
    Stores the accumulated stack in the model attachment."""
    lora_stack = []

    for slot_index, lora_name, strength_model, strength_clip in slots:
        if lora_name == "None":
            continue

        lora_path = folder_paths.get_full_path("loras", lora_name)
        if lora_path is None:
            continue

        lora_data = comfy.utils.load_torch_file(lora_path, safe_load=True)
        model, clip = comfy.sd.load_lora_for_models(
            model, clip, lora_data, strength_model, strength_clip
        )

        filename = os.path.basename(lora_name)
        name     = os.path.splitext(filename)[0]
        meta     = _read_lora_metadata(lora_path)

        entry = {
            "slot":           slot_index,
            "filename":       filename,
            "name":           name,
            "strength_model": strength_model,
            "strength_clip":  strength_clip,
        }
        entry.update(meta)
        lora_stack.append(entry)

    # Accumulate onto any stack already set by an upstream loader.
    existing = model.get_attachment(ATTACHMENT_KEY) or []
    model.set_attachments(ATTACHMENT_KEY, existing + lora_stack)

    return (model, clip)


# ── Simple variant: one shared strength per LoRA ─────────────────────────────

class JSGLoraStackLoader:
    DESCRIPTION = (
        "Loads up to 6 LoRAs onto a MODEL and CLIP. "
        "One strength slider controls both the diffusion model and CLIP equally. "
        "LoRA metadata is stored in the model attachment for JSGModelInfo. "
        "Stacks accumulate when chained."
    )

    CATEGORY = "JSG Utils/Model"
    FUNCTION = "load_loras"

    RETURN_TYPES = ("MODEL", "CLIP")
    RETURN_NAMES = ("model", "clip")
    OUTPUT_TOOLTIPS = (
        "Diffusion model with LoRAs applied.",
        "CLIP model with LoRAs applied.",
    )

    @classmethod
    def INPUT_TYPES(cls):
        lora_list = ["None"] + folder_paths.get_filename_list("loras")
        inputs = {
            "model": ("MODEL", {"tooltip": "Base diffusion model to apply LoRAs to."}),
            "clip":  ("CLIP",  {"tooltip": "Base CLIP model to apply LoRAs to."}),
        }
        for i in range(1, MAX_LORAS + 1):
            inputs[f"lora_{i:02d}"] = (
                lora_list,
                {"tooltip": f"LoRA slot {i}. Choose 'None' to skip."},
            )
            inputs[f"strength_{i:02d}"] = ("FLOAT", {
                **_STRENGTH_PROPS,
                "tooltip": f"Strength applied to both model and CLIP for slot {i}.",
            })
        return {"required": inputs}

    def load_loras(self, model, clip, **kwargs):
        slots = [
            (i, kwargs[f"lora_{i:02d}"], kwargs[f"strength_{i:02d}"], kwargs[f"strength_{i:02d}"])
            for i in range(1, MAX_LORAS + 1)
        ]
        return _apply_loras(model, clip, slots)


# ── Advanced variant: separate model and CLIP strengths per LoRA ─────────────

class JSGLoraStackLoaderAdvanced:
    DESCRIPTION = (
        "Loads up to 6 LoRAs onto a MODEL and CLIP with independent "
        "model and CLIP strength sliders per slot. "
        "LoRA metadata is stored in the model attachment for JSGModelInfo. "
        "Stacks accumulate when chained."
    )

    CATEGORY = "JSG Utils/Model"
    FUNCTION = "load_loras"

    RETURN_TYPES = ("MODEL", "CLIP")
    RETURN_NAMES = ("model", "clip")
    OUTPUT_TOOLTIPS = (
        "Diffusion model with LoRAs applied.",
        "CLIP model with LoRAs applied.",
    )

    @classmethod
    def INPUT_TYPES(cls):
        lora_list = ["None"] + folder_paths.get_filename_list("loras")
        inputs = {
            "model": ("MODEL", {"tooltip": "Base diffusion model to apply LoRAs to."}),
            "clip":  ("CLIP",  {"tooltip": "Base CLIP model to apply LoRAs to."}),
        }
        for i in range(1, MAX_LORAS + 1):
            inputs[f"lora_{i:02d}"] = (
                lora_list,
                {"tooltip": f"LoRA slot {i}. Choose 'None' to skip."},
            )
            inputs[f"strength_model_{i:02d}"] = ("FLOAT", {
                **_STRENGTH_PROPS,
                "tooltip": f"Diffusion model strength for slot {i}.",
            })
            inputs[f"strength_clip_{i:02d}"] = ("FLOAT", {
                **_STRENGTH_PROPS,
                "tooltip": f"CLIP strength for slot {i}.",
            })
        return {"required": inputs}

    def load_loras(self, model, clip, **kwargs):
        slots = [
            (i, kwargs[f"lora_{i:02d}"], kwargs[f"strength_model_{i:02d}"], kwargs[f"strength_clip_{i:02d}"])
            for i in range(1, MAX_LORAS + 1)
        ]
        return _apply_loras(model, clip, slots)
