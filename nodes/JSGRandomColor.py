import os
import colorsys

class JSGRandomColorHSVA:
    DESCRIPTION = (
        "Generates a color from HSVA values."
    )

    CATEGORY = "JSG Utils/Color"
    FUNCTION = "generate"

    RETURN_TYPES = ("COLORCODE", "STRING", "INT", "INT", "INT", "INT", "INT", "INT", "INT")
    RETURN_NAMES = ("ColorCode", "Hex", "H_deg", "S", "V", "A", "R", "G", "B")
    OUTPUT_TOOLTIPS = (
        "Returns the generated color code.",
        "Returns the generated hex color string.",
        "Returns the hue in degrees.",
        "Returns the saturation value.",
        "Returns the value channel.",
        "Returns the alpha channel.",
        "Returns the red channel.",
        "Returns the green channel.",
        "Returns the blue channel.",
    )

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                # Normalized inputs: 0.00..1.00, <0 means random
                "hue": ("FLOAT", {"default": -1.0, "min": -1.0, "max": 1.0, "step": 0.01, "tooltip": "The normalized hue value. Values below 0 randomize this channel."}),
                "saturation": ("FLOAT", {"default": -1.0, "min": -1.0, "max": 1.0, "step": 0.01, "tooltip": "The normalized saturation value. Values below 0 randomize this channel."}),
                "value": ("FLOAT", {"default": -1.0, "min": -1.0, "max": 1.0, "step": 0.01, "tooltip": "The normalized value channel. Values below 0 randomize this channel."}),

                # Alpha default opaque (1.00). <0 means random alpha.
                "alpha": ("FLOAT", {"default": 1.0, "min": -1.0, "max": 1.0, "step": 0.01, "tooltip": "The normalized alpha value. Values below 0 randomize this channel."}),

                "use_alpha": ("BOOLEAN", {"default": False, "tooltip": "Whether to include alpha in the hex outputs."}),
                "always_load": ("BOOLEAN", {"default": True, "tooltip": "Whether to force this node to re-execute every run."}),
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
