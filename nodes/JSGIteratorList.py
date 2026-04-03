import copy
import uuid

# ── AnyType ───────────────────────────────────────────────────────────────────

class AnyType(str):
    def __eq__(self, other): return True
    def __ne__(self, other): return not self.__eq__(other)

ANY = AnyType("*")

_LOG = "[JSGIteratorList]"


# ── Re-queue helper ───────────────────────────────────────────────────────────

def _requeue(prompt, unique_id, next_index):
    try:
        import server as comfy_server
        ps = comfy_server.PromptServer.instance

        modified = copy.deepcopy(prompt)
        node_key = str(unique_id)

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

class JSGIteratorList:
    CATEGORY = "JSG Utils/Iterator"
    FUNCTION  = "iterate"

    RETURN_TYPES  = (ANY, "INT", "INT")
    RETURN_NAMES  = ("Item", "Index", "Total")
    OUTPUT_TOOLTIPS = (
        "The current item from the list for this iteration.",
        "0-based index of the current iteration.",
        "Total number of items in the list.",
    )

    DESCRIPTION = (
        "Iterates over a Python list, one item per queue run. "
        "Connect any node that outputs a list (e.g. JSGObjectBuilder fields "
        "or other list-producing nodes). "
        "Press Run once — the node re-queues itself for each remaining item."
    )

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "list_input": (ANY, {"forceInput": True}),
            },
            "optional": {
                # Hidden by JS — stores the current iteration index between runs.
                "_jsg_iter_index": ("INT", {"default": 0, "min": 0}),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
                "prompt":    "PROMPT",
            },
        }

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float("NaN")

    def iterate(self, list_input, _jsg_iter_index=0, unique_id=None, prompt=None, **kwargs):
        # Accept list, tuple, or any sequence
        if not isinstance(list_input, (list, tuple)):
            if hasattr(list_input, "__iter__") and not isinstance(list_input, (str, bytes)):
                try:
                    list_input = list(list_input)
                except Exception:
                    list_input = [list_input]
            else:
                # Scalar value — wrap and iterate once
                list_input = [list_input]

        total = len(list_input)
        if total == 0:
            print(f"{_LOG} WARNING: received empty list — nothing to iterate.")
            return (None, 0, 0)

        index   = max(0, min(_jsg_iter_index, total - 1))
        current = list_input[index]

        if index + 1 < total and prompt is not None and unique_id is not None:
            _requeue(prompt, unique_id, index + 1)
        else:
            print(f"{_LOG} Iteration complete ({total} item(s) processed).")

        return (current, index, total)
