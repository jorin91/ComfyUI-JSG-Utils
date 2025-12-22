import os
import colorsys

class JSGRandomColorHSVA:
    DESCRIPTION = (
        "Generates a color from HSVA.\n"
        "Inputs are normalized floats 0.00-1.00 (step 0.01). If a channel is < 0, it will be randomized.\n"
        "If use_alpha is enabled, outputs #RRGGBBAA, otherwise #RRGGBB.\n"
        "COLORCODE output is intended for ComfyUI-RMBG compatibility, Hex is a string representation, "
        "all remaining outputs are INT values (H is degrees 0-360, S/V/A are 0-255, RGB are 0-255)."
    )

    CATEGORY = "JSG Utils/Color"
    FUNCTION = "generate"

    RETURN_TYPES = ("COLORCODE", "STRING", "INT", "INT", "INT", "INT", "INT", "INT", "INT")
    RETURN_NAMES = ("ColorCode", "Hex", "H_deg", "S", "V", "A", "R", "G", "B")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                # Normalized inputs: 0.00..1.00, <0 means random
                "hue": ("FLOAT", {"default": -1.0, "min": -1.0, "max": 1.0, "step": 0.01}),
                "saturation": ("FLOAT", {"default": -1.0, "min": -1.0, "max": 1.0, "step": 0.01}),
                "value": ("FLOAT", {"default": -1.0, "min": -1.0, "max": 1.0, "step": 0.01}),

                # Alpha default opaque (1.00). <0 means random alpha.
                "alpha": ("FLOAT", {"default": 1.0, "min": -1.0, "max": 1.0, "step": 0.01}),

                "use_alpha": ("BOOLEAN", {"default": False}),
                "always_load": ("BOOLEAN", {"default": False}),
            }
        }

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        if kwargs.get("always_load", False):
            return float("NaN")
        return hash(frozenset(kwargs.items()))

    def _rand01(self) -> float:
        # random float in [0,1)
        n = int.from_bytes(os.urandom(8), "big")
        return (n % (10**12)) / float(10**12)

    def _pick01(self, v: float) -> float:
        if v is None or v < 0.0:
            return self._rand01()
        if v > 1.0:
            return 1.0
        return v

    def generate(self, hue: float, saturation: float, value: float, alpha: float, use_alpha: bool, always_load: bool):
        h01 = self._pick01(hue)
        s01 = self._pick01(saturation)
        v01 = self._pick01(value)
        a01 = self._pick01(alpha)

        r_f, g_f, b_f = colorsys.hsv_to_rgb(h01, s01, v01)

        r = int(round(r_f * 255.0))
        g = int(round(g_f * 255.0))
        b = int(round(b_f * 255.0))
        a = int(round(a01 * 255.0))

        # clamp
        r = 0 if r < 0 else 255 if r > 255 else r
        g = 0 if g < 0 else 255 if g > 255 else g
        b = 0 if b < 0 else 255 if b > 255 else b
        a = 0 if a < 0 else 255 if a > 255 else a

        # outputs you requested:
        h_deg = int(round(h01 * 360.0))  # 0..360
        s = int(round(s01 * 255.0))
        v = int(round(v01 * 255.0))

        # clamp S/V too
        s = 0 if s < 0 else 255 if s > 255 else s
        v = 0 if v < 0 else 255 if v > 255 else v

        if use_alpha:
            hex_color = f"#{r:02X}{g:02X}{b:02X}{a:02X}"
        else:
            hex_color = f"#{r:02X}{g:02X}{b:02X}"

        return (hex_color, hex_color, h_deg, s, v, a, r, g, b)
