/**
 * JSGIterator.js
 *
 * Manages UI for JSGIteratorInputs and JSGIteratorList nodes.
 *
 * JSGIteratorInputs:
 *   - Shows item_1 … item_N input slots where N = lastConnected + 1 (min 1).
 *   - Hides all slots beyond that.
 *   - Hides the internal "_jsg_iter_index" widget.
 *
 * JSGIteratorList:
 *   - No dynamic slots; only hides "_jsg_iter_index".
 *
 * Both nodes reset _jsg_iter_index to 0 when the user manually triggers a
 * fresh start — done by watching when ALL item slots are disconnected and
 * reconnected, which signals a new iteration sequence.
 */
import { app } from "../../../scripts/app.js";

const NODE_INPUTS = "JSGIteratorInputs";
const NODE_LIST   = "JSGIteratorList";
const MAX_ITEMS   = 16;
const HIDDEN_TAG  = "jsg-hidden-iter";

// ── Helpers ───────────────────────────────────────────────────────────────────

function getWidget(node, name) {
    return (node.widgets ?? []).find(w => w.name === name) ?? null;
}

function getInput(node, name) {
    return (node.inputs ?? []).find(i => i.name === name) ?? null;
}

function hideWidget(w) {
    if (!w || w.__jsgIterHidden) return;
    w.__jsgIterHidden   = true;
    w.__origType        = w.type;
    w.__origComputeSize = w.computeSize;
    w.type              = HIDDEN_TAG;
    w.computeSize       = () => [0, -4];
    if (w.inputEl) w.inputEl.style.display = "none";
}

// ── JSGIteratorInputs: dynamic input slot management ─────────────────────────

function refreshInputSlots(node) {
    let lastConnected = 0;
    for (let i = 1; i <= MAX_ITEMS; i++) {
        const inp = getInput(node, `item_${i}`);
        if (inp && inp.link != null) lastConnected = i;
    }

    const visibleCount = Math.min(lastConnected + 1, MAX_ITEMS);

    for (let i = 1; i <= MAX_ITEMS; i++) {
        const inp = getInput(node, `item_${i}`);
        if (!inp) continue;
        inp.hidden = (i > visibleCount);
    }

    // Always hide the internal index widget
    hideWidget(getWidget(node, "_jsg_iter_index"));

    node.setSize?.(node.computeSize());
    node.setDirtyCanvas?.(true, true);
}

// Reset the iteration index to 0 whenever the first slot is newly connected.
// This lets the user start a fresh sequence without manually resetting.
function resetIndexIfNewSequence(node) {
    const w = getWidget(node, "_jsg_iter_index");
    if (!w) return;

    // Count currently connected slots
    let connected = 0;
    for (let i = 1; i <= MAX_ITEMS; i++) {
        const inp = getInput(node, `item_${i}`);
        if (inp && inp.link != null) connected++;
    }

    // If nothing is connected, reset index so the next connection starts fresh
    if (connected === 0) {
        w.value = 0;
    }
}

// Extension registration moved to JSGDynamicInputs.js (JSG.Utils.DynamicInputsV2).
