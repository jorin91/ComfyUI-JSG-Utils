/**
 * JSGObjectUnpack.js
 *
 * Manages output slots for JSGObjectUnpack dynamically.
 *
 * When a JSGOBJECT is connected to the "object" input:
 *   1. Find the source node that produced the JSGOBJECT.
 *   2. Read its "jsg_field_meta" widget to get [{slot, name, type}].
 *   3. Update this node's MAX_FIELDS output slots:
 *        - Active slots: set correct name + type (visual only; Python uses * for validation).
 *        - Inactive slots: hide.
 *   4. Write "jsg_unpack_meta" widget with [{slot_idx, name, type}] so Python
 *      knows which 0-based output index maps to which field name.
 *
 * When the JSGOBJECT is disconnected: reset all outputs to hidden defaults.
 */
import { app } from "../../../scripts/app.js";

const NODE_TYPE  = "JSGObjectUnpack";
const MAX_FIELDS = 16;
const HIDDEN_TAG = "jsg-hidden-unpack";
const DEFAULT_OUTPUT_NAME = "field";

// ── Helpers ───────────────────────────────────────────────────────────────────

function getWidget(node, name) {
    return (node.widgets ?? []).find(w => w.name === name) ?? null;
}

// Walk upstream through the graph to find the JSGOBJECT producer node.
// Returns null if not found or ambiguous.
function resolveSourceNode(node) {
    const inp = (node.inputs ?? []).find(i => i.name === "object");
    if (!inp || inp.link == null) return null;
    const link = app.graph.links[inp.link];
    if (!link) return null;
    return app.graph.getNodeById(link.origin_id) ?? null;
}

// Parse jsg_field_meta from a builder node.
// Returns [{slot, name, type}] or [].
function readBuilderMeta(sourceNode) {
    if (!sourceNode) return [];
    const w = getWidget(sourceNode, "jsg_field_meta");
    if (!w) return [];
    try {
        const parsed = JSON.parse(w.value);
        return Array.isArray(parsed) ? parsed : [];
    } catch { return []; }
}

// ── Output slot management ────────────────────────────────────────────────────

function resetOutputs(node) {
    // Hide all dynamic outputs — show none
    for (let i = 0; i < MAX_FIELDS; i++) {
        if (!node.outputs[i]) continue;
        node.outputs[i].name   = DEFAULT_OUTPUT_NAME;
        node.outputs[i].type   = "*";
        node.outputs[i].hidden = true;
    }
}

function applyFields(node, fields) {
    // fields: [{slot (1-based builder slot), name, type}]
    resetOutputs(node);

    const meta = []; // for jsg_unpack_meta

    fields.forEach((f, idx) => {
        const name = (f.name || "").trim() || DEFAULT_OUTPUT_NAME;
        const type = f.type || "*";

        if (idx >= MAX_FIELDS) return; // safety cap

        if (node.outputs[idx]) {
            node.outputs[idx].name   = name;
            node.outputs[idx].type   = type;
            node.outputs[idx].hidden = false;
        }

        meta.push({ slot_idx: idx, name, type });
    });

    // Write meta for Python
    const metaW = getWidget(node, "jsg_unpack_meta");
    if (metaW) metaW.value = JSON.stringify(meta);

    node.setSize?.(node.computeSize());
    node.setDirtyCanvas?.(true, true);
}

// ── Main sync ─────────────────────────────────────────────────────────────────

function syncFromSource(node) {
    // Also hide the meta widget from the user
    const metaW = getWidget(node, "jsg_unpack_meta");
    if (metaW) {
        if (!metaW.__jsgUnpackHidden) {
            metaW.__jsgUnpackHidden   = true;
            metaW.__jsgOrigType       = metaW.type;
            metaW.__jsgOrigCompute    = metaW.computeSize;
            metaW.type                = HIDDEN_TAG;
            metaW.computeSize         = () => [0, -4];
        }
    }

    const src = resolveSourceNode(node);
    if (!src) {
        resetOutputs(node);
        node.setSize?.(node.computeSize());
        node.setDirtyCanvas?.(true, true);
        return;
    }

    const fields = readBuilderMeta(src);
    applyFields(node, fields);
}

// Extension registration moved to JSGDynamicInputs.js (JSG.Utils.DynamicInputsV2).
