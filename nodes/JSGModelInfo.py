import os

from .JSGLoraStackLoader import ATTACHMENT_KEY as _LORA_ATTACHMENT_KEY


def _fmt_strength(v: float) -> str:
    """Format a strength value: strip trailing zeros after 2 decimal places."""
    return f"{v:.2f}".rstrip("0").rstrip(".")


def _fmt_lora_short(entry: dict) -> str:
    """
    Format one LoRA as an underscore-separated tag:
      <slot>_<name>_str<strength>          (model == clip)
      <slot>_<name>_model<sm>_clip<sc>     (model != clip)
    """
    slot = entry["slot"]
    name = entry["name"]
    sm   = entry["strength_model"]
    sc   = entry["strength_clip"]

    if sm == sc:
        return f"{slot}_{name}_str{_fmt_strength(sm)}"
    return f"{slot}_{name}_model{_fmt_strength(sm)}_clip{_fmt_strength(sc)}"


def _fmt_full_info(architecture: str, model_name: str, filepath: str,
                   sampling_type: str, stack: list) -> str:
    """Dump all extracted info as a single readable string."""
    lines = [
        f"model_name={architecture}_{model_name}" if architecture else f"model_name={model_name}",
        f"filepath={filepath}",
        f"architecture={architecture}",
        f"sampling_type={sampling_type}",
    ]
    if stack:
        for entry in stack:
            sm = entry["strength_model"]
            sc = entry["strength_clip"]
            if sm == sc:
                str_part = f"str={_fmt_strength(sm)}"
            else:
                str_part = f"str_model={_fmt_strength(sm)}, str_clip={_fmt_strength(sc)}"
            meta_fields = [
                "architecture", "base_model", "trained_on",
                "network_dim", "network_alpha", "epoch", "steps",
                "prediction_type", "resolution", "comment",
            ]
            meta_parts = ", ".join(
                f"{k}={entry[k]}" for k in meta_fields if entry.get(k)
            )
            lora_line = f"lora_{entry['slot']}={entry['name']}, {str_part}"
            if meta_parts:
                lora_line += f", {meta_parts}"
            lines.append(lora_line)
    return "\n".join(lines)


class JSGModelInfo:
    DESCRIPTION = (
        "Extracts structured info from a MODEL: a formatted model name "
        "(<architecture>_<filename>), a compact LoRA list string, and a full "
        "info dump. Reads LoRA data stored by JSGLoraStackLoader."
    )

    CATEGORY = "JSG Utils/Model"
    FUNCTION = "extract"

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = (
        "model_name",
        "loras",
        "model_and_loras",
        "info",
    )
    OUTPUT_TOOLTIPS = (
        "Formatted model name: <architecture>_<filename_without_ext>, "
        "e.g. 'SDXL_cyberrealisticXL_v80'.",
        "Applied LoRAs as compact underscore-tagged strings joined by ', '. "
        "e.g. '1_MyLora_str0.8, 2_OtherLora_model1_clip0.5'. "
        "Empty when no JSGLoraStackLoader is upstream.",
        "Single combined string: '<model_name> (<loras>)'. "
        "Omits parentheses when no LoRAs are applied.",
        "Full info dump: model name, path, architecture, sampling type, "
        "and all LoRA details as a multiline string.",
    )

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model": ("MODEL", {"tooltip": "The model to extract information from."}),
            }
        }

    def extract(self, model):
        filepath     = ""
        filename_raw = ""
        model_name   = ""
        architecture = ""
        sampling_type = ""

        try:
            init_info = model.cached_patcher_init
            if init_info is not None and len(init_info) > 1:
                raw_path = init_info[1][0] if init_info[1] else None
                if isinstance(raw_path, (list, tuple)):
                    raw_path = raw_path[0]
                if isinstance(raw_path, str) and raw_path:
                    filepath     = raw_path
                    filename_raw = os.path.basename(filepath)
                    model_name   = os.path.splitext(filename_raw)[0]
        except Exception:
            pass

        try:
            architecture = model.model.model_config.__class__.__name__
        except Exception:
            pass

        try:
            sampling_type = model.model.model_type.name
        except Exception:
            pass

        # --- Formatted model name: <architecture>_<model_name> ---
        if architecture and model_name:
            formatted_model_name = f"{architecture}_{model_name}"
        elif model_name:
            formatted_model_name = model_name
        else:
            formatted_model_name = architecture

        # --- LoRA stack ---
        stack = []
        try:
            stack = model.get_attachment(_LORA_ATTACHMENT_KEY) or []
        except Exception:
            pass

        loras_str = ", ".join(_fmt_lora_short(e) for e in stack)

        info_str = _fmt_full_info(architecture, model_name, filepath, sampling_type, stack)

        if loras_str:
            model_and_loras = f"{formatted_model_name} ({loras_str})"
        else:
            model_and_loras = formatted_model_name

        return (formatted_model_name, loras_str, model_and_loras, info_str)
