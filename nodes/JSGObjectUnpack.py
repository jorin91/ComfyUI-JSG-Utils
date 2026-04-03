import json

JSGOBJECT = "JSGOBJECT"
JSGLINK   = "JSGLINK"
MAX_FIELDS = 16
_LOG = "[JSGObjectUnpack]"


class JSGObjectUnpack:
    CATEGORY = "JSG Utils/Object"
    FUNCTION = "unpack"

    # Link passthrough is ALWAYS at index 0 (matches Python RETURN_TYPES[0]).
    # Field slots start at index 1; JS adds/removes them dynamically via addOutput/removeOutput.
    # Python always returns 1 + MAX_FIELDS values so ComfyUI can route any connected output.
    RETURN_TYPES    = (JSGLINK,) + ("*",) * MAX_FIELDS
    RETURN_NAMES    = ("Link",) + tuple(f"field_{i}" for i in range(1, MAX_FIELDS + 1))
    OUTPUT_TOOLTIPS = (
        ("Link passthrough — connect to another JSGObjectUnpack 'link' input to share this schema.",)
        + tuple(f"Output for field slot {i}." for i in range(1, MAX_FIELDS + 1))
    )

    DESCRIPTION = (
        "Unpacks a JSGOBJECT into individual typed outputs. "
        "Connect to a JSGObjectBuilder output. "
        "Output slots update automatically to match the builder's fields."
    )

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                # 'link' first — connect from JSGObjectBuilder 'Link' output
                # or from another JSGObjectUnpack 'Link' output to chain.
                "link": (JSGLINK, {}),
                "object": (JSGOBJECT, {}),
            },
        }

    def unpack(self, link, object):  # noqa: A002
        # 'link' carries Builder's jsg_field_meta JSON directly — no JS widget needed.
        try:
            meta = json.loads(link) if isinstance(link, str) else []
            if not isinstance(meta, list):
                meta = []
        except Exception:
            print(f"{_LOG} WARNING: could not parse link meta — returning empty tuple.")
            meta = []

        # result[i] maps to Python return index i+1 (index 0 is the Link passthrough).
        result = [None] * MAX_FIELDS

        if isinstance(object, dict):
            for i, entry in enumerate(meta):
                if i >= MAX_FIELDS:
                    break
                field_name = (entry.get("name") or "").strip()
                if field_name and field_name in object:
                    result[i] = object[field_name]
        else:
            print(f"{_LOG} WARNING: received non-dict object — all outputs will be None.")

        # Link passthrough at index 0; field values at indices 1–MAX_FIELDS.
        return (link,) + tuple(result)
