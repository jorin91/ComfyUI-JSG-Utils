class JSGImageSizeCalc:
    DESCRIPTION = (
        "Calculates image width and height from a resolution preset and an aspect ratio. "
        "The preset defines the shortest side in pixels. "
        "Choose Landscape to place the long side as width, or Portrait to place it as height. "
        "Both dimensions are rounded to the nearest multiple of 8."
    )

    CATEGORY = "JSG Utils/Image"
    FUNCTION = "calculate"

    RETURN_TYPES = ("INT", "INT", "INT", "INT")
    RETURN_NAMES = ("width", "height", "shortest_side", "longest_side")
    OUTPUT_TOOLTIPS = (
        "Calculated image width in pixels (after rounding).",
        "Calculated image height in pixels (after rounding).",
        "Shortest side in pixels (after rounding).",
        "Longest side in pixels (after rounding).",
    )

    _RESOLUTIONS = [
        "512px",
        "768px",
        "1024px",
        "HD (720p)",
        "Full HD (1080p)",
        "1440p (2K)",
        "4K (2160p)",
        "8K (4320p)",
        "Custom",
    ]

    _RESOLUTION_MAP = {
        "512px": 512,
        "768px": 768,
        "1024px": 1024,
        "HD (720p)": 720,
        "Full HD (1080p)": 1080,
        "1440p (2K)": 1440,
        "4K (2160p)": 2160,
        "8K (4320p)": 4320,
    }

    _ASPECT_RATIOS = [
        "1:1 (Square)",
        "4:3",
        "3:2",
        "5:4",
        "16:9",
        "16:10",
        "21:9 (Ultrawide)",
        "2:1",
    ]

    _RATIO_MAP = {
        "1:1 (Square)": (1, 1),
        "4:3": (4, 3),
        "3:2": (3, 2),
        "5:4": (5, 4),
        "16:9": (16, 9),
        "16:10": (16, 10),
        "21:9 (Ultrawide)": (21, 9),
        "2:1": (2, 1),
    }

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "resolution": (
                    cls._RESOLUTIONS,
                    {
                        "default": "1024px",
                        "tooltip": (
                            "Preset resolution used as the shortest side. "
                            "Select 'Custom' to enter a manual value via custom_resolution."
                        ),
                    },
                ),
                "aspect_ratio": (
                    cls._ASPECT_RATIOS,
                    {
                        "default": "16:9",
                        "tooltip": "Width-to-height ratio of the output image.",
                    },
                ),
                "orientation": (
                    ["Landscape", "Portrait"],
                    {
                        "default": "Landscape",
                        "tooltip": (
                            "Landscape: long side becomes width (e.g. 1920x1080). "
                            "Portrait: long side becomes height (e.g. 1080x1920). "
                            "Ignored for 1:1 (Square)."
                        ),
                    },
                ),
                "custom_resolution": (
                    "INT",
                    {
                        "default": 1024,
                        "min": 64,
                        "max": 8192,
                        "step": 8,
                        "tooltip": "Shortest side in pixels. Only used when resolution is set to 'Custom'.",
                    },
                ),
                "resolution_multiplier": (
                    "FLOAT",
                    {
                        "default": 1.00,
                        "min": 0.01,
                        "max": 64.00,
                        "step": 0.01,
                        "precision": 2,
                        "tooltip": "Multiplier for the base resolution before rounding.",
                    },
                ),
                "rounding": (
                    "INT",
                    {
                        "default": 8,
                        "min": 1,
                        "max": 512,
                        "step": 1,
                        "tooltip": "Round both dimensions to this multiple (e.g. 8 for most samplers).",
                    },
                ),
            }
        }

    def calculate(self, resolution, aspect_ratio, orientation, custom_resolution, resolution_multiplier, rounding):
        short = (
            custom_resolution
            if resolution == "Custom"
            else self._RESOLUTION_MAP[resolution]
        )

        # Pas de multiplier toe vóór afronding
        short = short * resolution_multiplier

        w_ratio, h_ratio = self._RATIO_MAP[aspect_ratio]

        if w_ratio == h_ratio:
            # Square — orientation has no effect
            width = short
            height = short
        elif orientation == "Landscape":
            # Short side = height; long side = width
            height = short
            width = short * w_ratio / h_ratio
        else:
            # Portrait — short side = width; long side = height
            width = short
            height = short * w_ratio / h_ratio

        # Round both dimensions to the nearest multiple of rounding
        width = max(rounding, round(width / rounding) * rounding)
        height = max(rounding, round(height / rounding) * rounding)

        shortest_side = min(width, height)
        longest_side = max(width, height)

        return (width, height, shortest_side, longest_side)
