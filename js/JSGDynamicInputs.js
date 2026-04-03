/**
 * JSGDynamicInputs.js
 *
 * Manages dynamic input visibility for all JSG nodes with variable inputs.
 *
 * Content-based (string_N): shows one empty slot beyond the last filled one.
 *   Covered nodes: JSGRandomStringChoice, JSGCombineStrings, JSGMatchStringList
 *
 * Count-based (bool_N): shows exactly as many inputs as the input_count widget says.
 *   Covered nodes: JSGBoolSwitch
 */
import { app } from "../../../scripts/app.js";

// ─── Node sets ────────────────────────────────────────────────────────────────

const STRING_INPUT_NODES = new Set([
    "JSGRandomStringChoice",
    "JSGCombineStrings",
    "JSGMatchStringList",
]);

const BOOL_INPUT_NODES = new Set([
    "JSGBoolSwitch",
]);

// ─── Shared helpers ───────────────────────────────────────────────────────────

const MAX_OPTIONS = 128;
const HIDDEN_STRING = "jsg-hidden-string";
const HIDDEN_BOOL   = "jsg-hidden-bool";

function getWidgetByName(node, name) {
    return (node.widgets || []).find((w) => w?.name === name);
}

function hideWidget(node, widget, hiddenType, suffix = "") {
    const tag = hiddenType + suffix;
    if (!widget || widget.type === tag) {
        return;
    }

    widget.origType = widget.type;
    widget.hidden = true;
    widget.origComputeSize = widget.computeSize;
    widget.origSerializeValue = widget.serializeValue;
    widget.computeSize = () => [0, -4];
    widget.type = tag;
    widget.serializeValue = () => {
        if (!node.inputs) return undefined;
        const nodeInput = node.inputs.find((i) => i.widget?.name === widget.name);
        if (!nodeInput || !nodeInput.link) return undefined;
        return widget.origSerializeValue ? widget.origSerializeValue() : widget.value;
    };

    if (widget.linkedWidgets) {
        for (const linked of widget.linkedWidgets) {
            hideWidget(node, linked, hiddenType, ":" + widget.name);
        }
    }
}

function showWidget(widget) {
    if (!widget || widget.origType == null) {
        return;
    }

    widget.type = widget.origType;
    widget.hidden = false;
    widget.computeSize = widget.origComputeSize;
    widget.serializeValue = widget.origSerializeValue;

    delete widget.origType;
    delete widget.origComputeSize;
    delete widget.origSerializeValue;

    if (widget.linkedWidgets) {
        for (const linked of widget.linkedWidgets) {
            showWidget(linked);
        }
    }
}

// ─── Content-based string inputs ──────────────────────────────────────────────

function isStringWidget(widget) {
    return widget && typeof widget.name === "string" && /^string_\d+$/.test(widget.name);
}

function getStringWidgets(node) {
    return (node.widgets || [])
        .filter(isStringWidget)
        .sort((a, b) => Number(a.name.split("_")[1]) - Number(b.name.split("_")[1]));
}

function hasLinkedInput(node, widgetName) {
    return Boolean((node.inputs || []).find((i) => i.widget?.name === widgetName && i.link != null));
}

function isFilledStringWidget(node, widget) {
    const value = typeof widget?.value === "string" ? widget.value.trim() : "";
    return Boolean(value) || hasLinkedInput(node, widget?.name);
}

function refreshStringWidgets(node) {
    const widgets = getStringWidgets(node);
    let lastFilledIndex = -1;

    for (let i = 0; i < widgets.length; i++) {
        if (isFilledStringWidget(node, widgets[i])) {
            lastFilledIndex = i;
        }
    }

    const visibleCount = Math.min(Math.max(lastFilledIndex + 2, 2), MAX_OPTIONS);

    for (let i = 0; i < widgets.length; i++) {
        if (i < visibleCount) {
            showWidget(widgets[i]);
        } else {
            hideWidget(node, widgets[i], HIDDEN_STRING);
        }
    }

    node.setSize?.(node.computeSize());
    node.setDirtyCanvas?.(true, true);
}

function wrapStringWidget(node, widget) {
    if (widget.__jsgWrapped) return;

    widget.__jsgWrapped = true;
    const original = widget.callback;
    const refresh = () => refreshStringWidgets(node);

    widget.callback = function (...args) {
        const result = original ? original.apply(this, args) : undefined;
        refresh();
        return result;
    };

    if (widget.inputEl && !widget.__jsgInputListenerAttached) {
        widget.__jsgInputListenerAttached = true;
        widget.inputEl.addEventListener("input", refresh);
        widget.inputEl.addEventListener("change", refresh);
    }
}

// ─── Count-based bool inputs ───────────────────────────────────────────────────

function isBoolWidget(widget) {
    return widget && typeof widget.name === "string" && /^bool_\d+$/.test(widget.name);
}

function getBoolWidgets(node) {
    return (node.widgets || [])
        .filter(isBoolWidget)
        .sort((a, b) => Number(a.name.split("_")[1]) - Number(b.name.split("_")[1]));
}

function refreshBoolWidgets(node) {
    const countWidget = getWidgetByName(node, "input_count");
    const count = Math.max(1, Math.round(Number(countWidget?.value ?? 1)));
    const widgets = getBoolWidgets(node);

    for (const widget of widgets) {
        const index = Number(widget.name.split("_")[1]);
        if (index <= count) {
            showWidget(widget);
        } else {
            hideWidget(node, widget, HIDDEN_BOOL);
        }
    }

    node.setSize?.(node.computeSize());
    node.setDirtyCanvas?.(true, true);
}

function wrapCountWidget(node) {
    const countWidget = getWidgetByName(node, "input_count");
    if (!countWidget || countWidget.__jsgBoolWrapped) return;

    countWidget.__jsgBoolWrapped = true;
    const original = countWidget.callback;

    countWidget.callback = function (...args) {
        const result = original ? original.apply(this, args) : undefined;
        refreshBoolWidgets(node);
        return result;
    };
}

// ─── Extension registration ───────────────────────────────────────────────────

app.registerExtension({
    name: "JSG.Utils.DynamicInputs",
    async beforeRegisterNodeDef(nodeType, nodeData) {
        const isStringNode = STRING_INPUT_NODES.has(nodeData.name);
        const isBoolNode   = BOOL_INPUT_NODES.has(nodeData.name);

        if (!isStringNode && !isBoolNode) return;

        if (isStringNode) {
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function () {
                const result = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;
                for (const widget of getStringWidgets(this)) wrapStringWidget(this, widget);
                refreshStringWidgets(this);
                return result;
            };

            const onConfigure = nodeType.prototype.onConfigure;
            nodeType.prototype.onConfigure = function () {
                const result = onConfigure ? onConfigure.apply(this, arguments) : undefined;
                for (const widget of getStringWidgets(this)) wrapStringWidget(this, widget);
                refreshStringWidgets(this);
                return result;
            };

            const onConnectionsChange = nodeType.prototype.onConnectionsChange;
            nodeType.prototype.onConnectionsChange = function () {
                const result = onConnectionsChange ? onConnectionsChange.apply(this, arguments) : undefined;
                refreshStringWidgets(this);
                return result;
            };
        }

        if (isBoolNode) {
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function () {
                const result = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;
                wrapCountWidget(this);
                refreshBoolWidgets(this);
                return result;
            };

            const onConfigure = nodeType.prototype.onConfigure;
            nodeType.prototype.onConfigure = function () {
                const result = onConfigure ? onConfigure.apply(this, arguments) : undefined;
                wrapCountWidget(this);
                refreshBoolWidgets(this);
                return result;
            };
        }
    },
});

// ─── ObjectBuilder: dynamic addInput/removeInput + name widget hiding ─────────

const OBJ_BUILDER_NODES = new Set(["JSGObjectBuilder"]);
const MAX_OBJ_FIELDS    = 16;
const HIDDEN_OBJ_TAG    = "jsg-hidden-obj";

function isFieldValueInput(inp) {
    return typeof inp?.name === "string" && /^field_value_\d+$/.test(inp.name);
}

function getFieldSlot(inp) {
    return Number(inp.name.replace("field_value_", ""));
}

function getFieldValueInputs(node) {
    return (node.inputs || []).filter(isFieldValueInput)
        .sort((a, b) => getFieldSlot(a) - getFieldSlot(b));
}

function getLinkedType(node, inp) {
    if (!inp || inp.link == null) return "*";
    return app.graph.links[inp.link]?.type ?? "*";
}

function updateObjBuilderMeta(node) {
    const metaW = getWidgetByName(node, "jsg_field_meta");
    if (!metaW) return;
    const meta = [];
    for (const inp of getFieldValueInputs(node)) {
        if (inp.link == null) continue;
        const slot    = getFieldSlot(inp);
        const link    = app.graph.links[inp.link];
        const srcNode = link ? app.graph.getNodeById(link.origin_id) : null;
        const srcOut  = srcNode?.outputs?.[link?.origin_slot];
        // Auto-name from the connected node's output label; fall back to generic name.
        const name    = srcOut?.name?.trim() || `field_${slot}`;
        meta.push({ slot, name, type: getLinkedType(node, inp) });
    }
    metaW.value = JSON.stringify(meta);

    // Push to all Unpack nodes directly connected to this Builder's 'Link' output (index 0).
    pushLinkToUnpacks(node);
}

function pushLinkToUnpacks(builderNode) {
    // Builder's 'Link' output is always at index 0.
    const linkOut = (builderNode.outputs || [])[0];
    if (!linkOut) return;
    for (const linkId of (linkOut.links || [])) {
        const link = app.graph.links[linkId];
        if (!link) continue;
        const target = app.graph.getNodeById(link.target_id);
        if (target && OBJ_UNPACK_NODES.has(target.type)) {
            setTimeout(() => refreshObjUnpack(target), 0);
        }
    }
}

function refreshObjBuilder(node) {
    const inputs = getFieldValueInputs(node);
    let lastConnected = 0;
    for (const inp of inputs) {
        if (inp.link != null) lastConnected = getFieldSlot(inp);
    }
    const targetMax = Math.min(Math.max(lastConnected + 1, 1), MAX_OBJ_FIELDS);
    const presentSlots = new Set(inputs.map(getFieldSlot));

    // Add missing slots in ascending order
    for (let i = 1; i <= targetMax; i++) {
        if (!presentSlots.has(i)) node.addInput(`field_value_${i}`, "*");
    }

    // Remove excess slots in descending order (preserves lower indices)
    const excess = inputs
        .filter(inp => getFieldSlot(inp) > targetMax)
        .sort((a, b) => getFieldSlot(b) - getFieldSlot(a));
    for (const inp of excess) {
        const idx = (node.inputs || []).indexOf(inp);
        if (idx >= 0) node.removeInput(idx);
    }

    const metaW = getWidgetByName(node, "jsg_field_meta");
    hideWidget(node, metaW, HIDDEN_OBJ_TAG);
    // hideWidget replaces serializeValue with one that returns undefined for non-linked widgets.
    // jsg_field_meta is never linked — it must always be serialized so Python receives the field list.
    if (metaW && !metaW.__jsgMetaSerializeFixed) {
        metaW.__jsgMetaSerializeFixed = true;
        metaW.serializeValue = () => metaW.value;
    }
    updateObjBuilderMeta(node);
    node.setSize?.(node.computeSize());
    node.setDirtyCanvas?.(true, true);
}

// ─── IteratorInputs: dynamic addInput/removeInput for item slots ──────────────

const ITER_INPUT_NODES = new Set(["JSGIteratorInputs"]);
const ITER_LIST_NODES  = new Set(["JSGIteratorList"]);
const MAX_ITER_ITEMS   = 16;
const HIDDEN_ITER_TAG  = "jsg-hidden-iter";

function isItemInput(inp) {
    return typeof inp?.name === "string" && /^item_\d+$/.test(inp.name);
}

function getItemSlot(inp) {
    return Number(inp.name.replace("item_", ""));
}

function getItemInputs(node) {
    return (node.inputs || []).filter(isItemInput)
        .sort((a, b) => getItemSlot(a) - getItemSlot(b));
}

function refreshIterInputs(node) {
    const inputs = getItemInputs(node);
    let lastConnected = 0;
    for (const inp of inputs) {
        if (inp.link != null) lastConnected = getItemSlot(inp);
    }
    const targetMax = Math.min(Math.max(lastConnected + 1, 1), MAX_ITER_ITEMS);
    const presentSlots = new Set(inputs.map(getItemSlot));

    for (let i = 1; i <= targetMax; i++) {
        if (!presentSlots.has(i)) node.addInput(`item_${i}`, "*");
    }

    const excess = inputs
        .filter(inp => getItemSlot(inp) > targetMax)
        .sort((a, b) => getItemSlot(b) - getItemSlot(a));
    for (const inp of excess) {
        const idx = (node.inputs || []).indexOf(inp);
        if (idx >= 0) node.removeInput(idx);
    }

    // Reset iteration index when all slots become disconnected
    if (lastConnected === 0) {
        const idxW = getWidgetByName(node, "_jsg_iter_index");
        if (idxW) idxW.value = 0;
    }

    hideWidget(node, getWidgetByName(node, "_jsg_iter_index"), HIDDEN_ITER_TAG);
    node.setSize?.(node.computeSize());
    node.setDirtyCanvas?.(true, true);
}

// ─── ObjectUnpack: Link at index 0 (fixed), field outputs 1-N (dynamic) ─────

const OBJ_UNPACK_NODES  = new Set(["JSGObjectUnpack"]);
const HIDDEN_UNPACK_TAG = "jsg-hidden-unpack";

// Follow the 'link' input to its source node (Builder or another Unpack).
function findLinkSource(node) {
    const linkInp = (node.inputs || []).find(i => i.name === "link");
    if (linkInp?.link == null) return null;
    const link = app.graph.links[linkInp.link];
    return link ? (app.graph.getNodeById(link.origin_id) ?? null) : null;
}

// Read jsg_field_meta from a Builder; traverse through chained Unpacks if needed.
function readBuilderMeta(sourceNode, visited = new Set()) {
    if (!sourceNode || visited.has(sourceNode.id)) return [];
    visited.add(sourceNode.id);
    const w = getWidgetByName(sourceNode, "jsg_field_meta");
    if (w) {
        try { return JSON.parse(w.value) || []; } catch { return []; }
    }
    // Source is another Unpack — climb the chain.
    if (OBJ_UNPACK_NODES.has(sourceNode.type)) {
        return readBuilderMeta(findLinkSource(sourceNode), visited);
    }
    return [];
}

// Push a refresh to all Unpacks connected to THIS node's Link output (index 0).
function propagateLinkDownstream(node) {
    const linkOut = (node.outputs || [])[0]; // Link is always at index 0
    if (!linkOut) return;
    for (const linkId of (linkOut.links || [])) {
        const link = app.graph.links[linkId];
        if (!link) continue;
        const target = app.graph.getNodeById(link.target_id);
        if (target && OBJ_UNPACK_NODES.has(target.type)) {
            setTimeout(() => refreshObjUnpack(target), 0);
        }
    }
}

function refreshObjUnpack(node) {
    const source = findLinkSource(node);
    const fields  = readBuilderMeta(source);

    // output[0] = Link passthrough — never touched.
    // Field outputs start at index 1; manage count to match fields exactly.
    // Simple trim from end: remove extra outputs regardless of connections
    // (removing a connected output severs the wire, which is correct — that field no longer exists).
    while ((node.outputs?.length ?? 0) - 1 > fields.length) {
        node.removeOutput((node.outputs?.length ?? 0) - 1);
    }

    // Update existing field outputs in-place (preserves connections on surviving slots).
    const existing = (node.outputs?.length ?? 0) - 1;
    for (let i = 0; i < existing; i++) {
        node.outputs[i + 1].name = (fields[i].name || "").trim() || "field";
        node.outputs[i + 1].type = fields[i].type || "*";
    }

    // Add missing field outputs.
    for (let i = existing; i < fields.length; i++) {
        node.addOutput((fields[i].name || "").trim() || "field", fields[i].type || "*");
    }

    node.setSize?.(node.computeSize());
    node.setDirtyCanvas?.(true, true);

    // Cascade to any Unpacks chained off this node's Link output.
    propagateLinkDownstream(node);
}

// ─── Extension: connection-based dynamic inputs + dynamic outputs ─────────────

app.registerExtension({
    name: "JSG.Utils.DynamicInputsV2",

    async beforeRegisterNodeDef(nodeType, nodeData) {
        const isObjBuilder = OBJ_BUILDER_NODES.has(nodeData.name);
        const isIterInputs = ITER_INPUT_NODES.has(nodeData.name);
        const isIterList   = ITER_LIST_NODES.has(nodeData.name);
        const isObjUnpack  = OBJ_UNPACK_NODES.has(nodeData.name);

        if (!isObjBuilder && !isIterInputs && !isIterList && !isObjUnpack) return;

        // ── onNodeCreated ──────────────────────────────────────────────────────
        const onNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            const r = onNodeCreated?.apply(this, arguments);
            if (isObjBuilder) refreshObjBuilder(this);
            if (isIterInputs) refreshIterInputs(this);
            if (isIterList)   hideWidget(this, getWidgetByName(this, "_jsg_iter_index"), HIDDEN_ITER_TAG);
            if (isObjUnpack)  refreshObjUnpack(this);
            return r;
        };

        // ── onConfigure (workflow load / paste) ────────────────────────────────
        const onConfigure = nodeType.prototype.onConfigure;
        nodeType.prototype.onConfigure = function () {
            const r = onConfigure?.apply(this, arguments);
            const node = this;
            // Defer so the graph can finish restoring all links before we clean up
            setTimeout(() => {
                if (isObjBuilder) refreshObjBuilder(node);
                if (isIterInputs) refreshIterInputs(node);
                if (isIterList)   hideWidget(node, getWidgetByName(node, "_jsg_iter_index"), HIDDEN_ITER_TAG);
                if (isObjUnpack)  refreshObjUnpack(node);
            }, 0);
            return r;
        };

        // ── onConnectionsChange ────────────────────────────────────────────────
        const onConnectionsChange = nodeType.prototype.onConnectionsChange;
        nodeType.prototype.onConnectionsChange = function (...args) {
            const r = onConnectionsChange?.apply(this, args);
            if (isObjBuilder) refreshObjBuilder(this);
            if (isIterInputs) refreshIterInputs(this);
            // Delay for unpack so the link graph is settled before we read it
            if (isObjUnpack)  setTimeout(() => refreshObjUnpack(this), 0);
            return r;
        };
    },
});
