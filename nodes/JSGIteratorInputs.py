import copy
import uuid

# ── AnyType: matches every ComfyUI data type in validation ────────────────────

class AnyType(str):
    """Wildcard type accepted by ComfyUI's type checker for any connection."""
    def __eq__(self, other): return True
    def __ne__(self, other): return not self.__eq__(other)

ANY = AnyType("*")

# ── Constants ─────────────────────────────────────────────────────────────────

MAX_ITEMS = 16
_LOG      = "[JSGIteratorInputs]"


# ── Re-queue helper ───────────────────────────────────────────────────────────

def _requeue(prompt, unique_id, next_index):
    """
    Insert a copy of the current prompt into the ComfyUI queue with
    _jsg_iter_index set to next_index so the next run processes the next item.
    """
    try:
        import server as comfy_server
        ps = comfy_server.PromptServer.instance

        modified  = copy.deepcopy(prompt)
        node_key  = str(unique_id)

        if node_key in modified:
            modified[node_key].setdefault("inputs", {})["_jsg_iter_index"] = next_index

        new_id = str(uuid.uuid4())
        number = ps.number
        ps.number += 1
        ps.prompt_queue.put((number, new_id, modified, {}, None))
        print(f"{_LOG} Queued iteration {next_index + 1} (id={new_id[:8]})")

    except Exception as exc:
        print(f"{_LOG} WARNING: failed to re-queue — {exc}")


# ── Node ──────────────────────────────────────────────────────────────────────

class JSGIteratorInputs:
    CATEGORY = "JSG Utils/Iterator"
    FUNCTION  = "iterate"

    RETURN_TYPES  = (ANY, "INT", "INT")
    RETURN_NAMES  = ("Item", "Index", "Total")
    OUTPUT_TOOLTIPS = (
        "The current item for this iteration.",
        "0-based index of the current iteration.",
        "Total number of connected inputs.",
    )

    DESCRIPTION = (
        "Iterates over up to 16 connected inputs, one per queue run. "
        "Press Run once — the node automatically re-queues itself for each "
        "remaining item. Connect any types (MODEL, STRING, JSGOBJECT, ...)."
    )

    @classmethod
    def INPUT_TYPES(cls):
        optional = {
            # Hidden by JS — stores the current iteration index between runs.
            "_jsg_iter_index": ("INT", {"default": 0, "min": 0, "max": MAX_ITEMS - 1}),
        }
        for i in range(1, MAX_ITEMS + 1):
            optional[f"item_{i}"] = (ANY, {"forceInput": True})

        return {
            "required":  {},
            "optional":  optional,
            "hidden":    {
                "unique_id": "UNIQUE_ID",
                "prompt":    "PROMPT",
            },
        }

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float("NaN")

    def iterate(self, _jsg_iter_index=0, unique_id=None, prompt=None, **kwargs):
        # Collect all connected items in slot order
        items = []
        for i in range(1, MAX_ITEMS + 1):
            key = f"item_{i}"
            if key in kwargs:
                items.append(kwargs[key])

        total = len(items)
        if total == 0:
            print(f"{_LOG} WARNING: no inputs connected — nothing to iterate.")
            return (None, 0, 0)

        index   = max(0, min(_jsg_iter_index, total - 1))
        current = items[index]

        # Schedule the next iteration if more items remain
        if index + 1 < total and prompt is not None and unique_id is not None:
            _requeue(prompt, unique_id, index + 1)
        else:
            print(f"{_LOG} Iteration complete ({total} item(s) processed).")

        return (current, index, total)
