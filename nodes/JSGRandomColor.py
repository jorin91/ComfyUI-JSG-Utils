import os
import colorsys

class JSGRandomColorHSV:
    DESCRIPTION = (
        "Generates a color from HSV (0-255 each). If any channel is < 0, it will be randomized.\n"
        "Outputs HEX and the actual HSV used.\n"
        "Optional always_load forces regeneration every run (prevents caching)."
    )

    CATEGORY = "JSG Utils/Color"
    FUNCTION = "generate"

    RETURN_TYPES = ("STRING", "COLORCODE", "INT", "INT", "INT")
    RETURN_NAMES = ("Color", "Color", "H", "S", "V")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "hue": ("INT", {"default": -1, "min": -1, "max": 255, "step": 1}),
                "saturation": ("INT", {"default": -1, "min": -1, "max": 255, "step": 1}),
                "value": ("INT", {"default": -1, "min": -1, "max": 255, "step": 1}),
                "always_load": ("BOOLEAN", {"default": False}),
            }
        }

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        if kwargs.get("always_load", False):
            return float("NaN")
        return hash(frozenset(kwargs.items()))

    def _rand_0_255(self) -> int:
        # cryptographically-strong random 0..255
        return int.from_bytes(os.urandom(1), "big")

    def _pick(self, v: int) -> int:
        if v is None:
            return self._rand_0_255()
        if v < 0:
            return self._rand_0_255()
        if v > 255:
            return 255
        return v

    def generate(self, hue: int, saturation: int, value: int, always_load: bool):
        h = self._pick(hue)
        s = self._pick(saturation)
        v = self._pick(value)

        # Convert 0..255 HSV to 0..1 HSV for colorsys
        h_f = h / 255.0
        s_f = s / 255.0
        v_f = v / 255.0

        r_f, g_f, b_f = colorsys.hsv_to_rgb(h_f, s_f, v_f)

        r = int(round(r_f * 255.0))
        g = int(round(g_f * 255.0))
        b = int(round(b_f * 255.0))

        # clamp
        r = 0 if r < 0 else 255 if r > 255 else r
        g = 0 if g < 0 else 255 if g > 255 else g
        b = 0 if b < 0 else 255 if b > 255 else b

        hex_color = f"#{r:02X}{g:02X}{b:02X}"
        return (hex_color, hex_color, h, s, v)
