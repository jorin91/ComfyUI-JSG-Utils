import os
import colorsys

class JSGRandomColorHSVA:
    DESCRIPTION = (
    "Generates a color from HSVA where each channel is 0-255.\n"
    "If a channel is -1, it will be randomized (0-255).\n"
    "If use_alpha is enabled, outputs #RRGGBBAA, otherwise #RRGGBB.\n"
    "COLORCODE output is intended for ComfyUI-RMBG compatibility, "
    "Hex is a string representation, all remaining outputs are INT values."
    )

    CATEGORY = "JSG Utils/Color"
    FUNCTION = "generate"

    RETURN_TYPES = ("COLORCODE", "STRING", "INT", "INT", "INT", "INT", "INT", "INT", "INT")
    RETURN_NAMES = ("COLORCODE", "Hex", "H", "S", "V", "A", "R", "G", "B")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "hue": ("INT", {"default": -1, "min": -1, "max": 255, "step": 1}),
                "saturation": ("INT", {"default": -1, "min": -1, "max": 255, "step": 1}),
                "value": ("INT", {"default": -1, "min": -1, "max": 255, "step": 1}),

                # Alpha: default 255 (opaque). -1 = random alpha.
                "alpha": ("INT", {"default": 255, "min": -1, "max": 255, "step": 1}),

                # If true: output hex includes AA always (#RRGGBBAA). If false: #RRGGBB.
                "use_alpha": ("BOOLEAN", {"default": False}),

                # Force node to rerun each execution (prevents caching)
                "always_load": ("BOOLEAN", {"default": False}),
            }
        }

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        if kwargs.get("always_load", False):
            return float("NaN")
        return hash(frozenset(kwargs.items()))

    def _rand_0_255(self) -> int:
        return int.from_bytes(os.urandom(1), "big")

    def _pick(self, v: int) -> int:
        if v is None or v < 0:
            return self._rand_0_255()
        if v > 255:
            return 255
        return v

    def generate(self, hue: int, saturation: int, value: int, alpha: int, use_alpha: bool, always_load: bool):
        h = self._pick(hue)
        s = self._pick(saturation)
        v = self._pick(value)
        a = self._pick(alpha)

        # HSV 0..255 -> 0..1 for colorsys
        h_f = h / 255.0
        s_f = s / 255.0
        v_f = v / 255.0

        r_f, g_f, b_f = colorsys.hsv_to_rgb(h_f, s_f, v_f)

        r = int(round(r_f * 255.0))
        g = int(round(g_f * 255.0))
        b = int(round(b_f * 255.0))

        # clamp rgb
        r = 0 if r < 0 else 255 if r > 255 else r
        g = 0 if g < 0 else 255 if g > 255 else g
        b = 0 if b < 0 else 255 if b > 255 else b

        if use_alpha:
            hex_color = f"#{r:02X}{g:02X}{b:02X}{a:02X}"
        else:
            hex_color = f"#{r:02X}{g:02X}{b:02X}"

        # COLORCODE is just the hex string (as used by your RMBG node)
        return (hex_color, hex_color, h, s, v, a, r, g, b)
