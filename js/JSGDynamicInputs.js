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
