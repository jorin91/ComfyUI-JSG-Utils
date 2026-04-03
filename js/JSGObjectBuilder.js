/**
 * JSGObjectBuilder.js
 *
 * Manages dynamic field slots for JSGObjectBuilder.
 *
 * Each slot consists of:
 *   - A STRING widget  "field_name_N"  (editable field name)
 *   - A connection input "field_value_N" (accepts any type)
 *
 * Behaviour:
 *   - Always shows the last connected slot + 1 empty slot (min 1 visible).
 *   - Hides all slots beyond that.
 *   - Hides the "jsg_field_meta" bookkeeping widget from the UI.
 *   - On every connection change or name edit: rebuilds jsg_field_meta JSON
 *     so Python knows which slots are active, their names, and their types.
 */
import { app } from "../../../scripts/app.js";

const NODE_TYPE  = "JSGObjectBuilder";
const MAX_FIELDS = 16;
const HIDDEN_TAG = "jsg-hidden-obj";

// ── Low-level helpers ─────────────────────────────────────────────────────────

function getWidget(node, name) {
    return (node.widgets ?? []).find(w => w.name === name) ?? null;
}

function getInput(node, name) {
    return (node.inputs ?? []).find(i => i.name === name) ?? null;
}

function isConnected(node, slot) {
    const inp = getInput(node, `field_value_${slot}`);
    return inp != null && inp.link != null;
}

function linkedType(node, slot) {
    const inp = getInput(node, `field_value_${slot}`);
    if (!inp || inp.link == null) return "*";
    const link = app.graph.links[inp.link];
    return link?.type ?? "*";
}

// ── Widget show/hide ──────────────────────────────────────────────────────────

function hideWidget(w) {
    if (!w || w.__jsgObjHidden) return;
    w.__jsgObjHidden    = true;
    w.__jsgOrigType     = w.type;
    w.__jsgOrigCompute  = w.computeSize;
    w.type              = HIDDEN_TAG;
    w.computeSize       = () => [0, -4];
    if (w.inputEl) w.inputEl.style.display = "none";
}

function showWidget(w) {
    if (!w || !w.__jsgObjHidden) return;
    w.__jsgObjHidden = false;
    w.type           = w.__jsgOrigType;
    w.computeSize    = w.__jsgOrigCompute;
    if (w.inputEl) w.inputEl.style.display = "";
    delete w.__jsgOrigType;
    delete w.__jsgOrigCompute;
}

// ── Input slot show/hide ──────────────────────────────────────────────────────

function hideInputSlot(node, slot) {
    const inp = getInput(node, `field_value_${slot}`);
    if (inp) inp.hidden = true;
}

function showInputSlot(node, slot) {
    const inp = getInput(node, `field_value_${slot}`);
    if (inp) inp.hidden = false;
}

// ── Metadata update ───────────────────────────────────────────────────────────

function updateMeta(node) {
    const metaW = getWidget(node, "jsg_field_meta");
    if (!metaW) return;

    const meta = [];
    for (let i = 1; i <= MAX_FIELDS; i++) {
        if (!isConnected(node, i)) continue;
        const nameW = getWidget(node, `field_name_${i}`);
        const name  = (nameW?.value ?? `field_${i}`).trim() || `field_${i}`;
        meta.push({ slot: i, name, type: linkedType(node, i) });
    }
    metaW.value = JSON.stringify(meta);
}

// ── Main refresh ──────────────────────────────────────────────────────────────

function refresh(node) {
    // Find the last slot that has a live connection
    let lastConnected = 0;
    for (let i = 1; i <= MAX_FIELDS; i++) {
        if (isConnected(node, i)) lastConnected = i;
    }

    // Show up to lastConnected + 1, but never more than MAX_FIELDS
    const visibleCount = Math.min(lastConnected + 1, MAX_FIELDS);

    for (let i = 1; i <= MAX_FIELDS; i++) {
        const nameW = getWidget(node, `field_name_${i}`);
        if (i <= visibleCount) {
            showWidget(nameW);
            showInputSlot(node, i);
        } else {
            hideWidget(nameW);
            hideInputSlot(node, i);
        }
    }

    // Always keep the bookkeeping widget hidden from the user
    hideWidget(getWidget(node, "jsg_field_meta"));

    updateMeta(node);
    node.setSize?.(node.computeSize());
    node.setDirtyCanvas?.(true, true);
}

// ── Name widget listeners ─────────────────────────────────────────────────────

function wrapNameWidgets(node) {
    for (let i = 1; i <= MAX_FIELDS; i++) {
        const w = getWidget(node, `field_name_${i}`);
        if (!w || w.__jsgNameWrapped) continue;
        w.__jsgNameWrapped = true;
        if (w.inputEl) {
            w.inputEl.addEventListener("input",  () => updateMeta(node));
            w.inputEl.addEventListener("change", () => updateMeta(node));
        }
    }
}

// Extension registration moved to JSGDynamicInputs.js (JSG.Utils.DynamicInputsV2).
