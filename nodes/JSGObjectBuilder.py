import json

JSGOBJECT = "JSGOBJECT"
JSGLINK   = "JSGLINK"
MAX_FIELDS = 16
_LOG = "[JSGObjectBuilder]"


class JSGObjectBuilder:
    CATEGORY = "JSG Utils/Object"
    FUNCTION = "build"
    RETURN_TYPES = (JSGLINK, JSGOBJECT)
    RETURN_NAMES = ("Link", "Object")
    OUTPUT_TOOLTIPS = (
        "Link — connect to JSGObjectUnpack 'link' input so it mirrors this builder's fields.",
        "A JSGOBJECT containing all connected field values.",
    )

    DESCRIPTION = (
        "Bundles multiple values of any type into a single JSGOBJECT. "
        "Connect any value to a field slot and name it. "
        "Use JSGObjectUnpack to extract fields downstream."
    )

    @classmethod
    def INPUT_TYPES(cls):
        optional = {
            # Holds field metadata as JSON — managed and hidden by JS.
            "jsg_field_meta": ("STRING", {"default": "[]"}),
        }
        for i in range(1, MAX_FIELDS + 1):
            optional[f"field_value_{i}"] = ("*", {"forceInput": True})

        return {"required": {}, "optional": optional}

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float("NaN")

    def build(self, jsg_field_meta="[]", **kwargs):
        # Parse field metadata written by JS
        try:
            meta = json.loads(jsg_field_meta) if isinstance(jsg_field_meta, str) else []
            if not isinstance(meta, list):
                meta = []
        except Exception:
            print(f"{_LOG} WARNING: could not parse jsg_field_meta — using empty object.")
            meta = []

        obj = {"__fields__": []}

        for entry in meta:
            slot = entry.get("slot")
            name = (entry.get("name") or "").strip()
            type_ = entry.get("type", "*")

            if not slot or not name:
                continue

            value = kwargs.get(f"field_value_{slot}")
            obj["__fields__"].append({"name": name, "type": type_})
            obj[name] = value  # None when disconnected — preserved intentionally

        return (jsg_field_meta, obj)
