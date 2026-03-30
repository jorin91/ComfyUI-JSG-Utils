import { app } from "../../../scripts/app.js";

const STRING_INPUT_NODES = new Set(["JSGRandomStringChoice", "JSGCombineStrings"]);
const SEED_CONTROL_NODES = new Set(["JSGRandomStringChoice"]);
const MAX_OPTIONS = 128;
const HIDDEN_TYPE = "jsg-hidden-string";
const MAX_SAFE_RANDOM = 1125899906842624;

function getWidgetByName(node, name) {
    return (node.widgets || []).find((widget) => widget?.name === name);
}

function isStringWidget(widget) {
    return widget && typeof widget.name === "string" && /^string_\d+$/.test(widget.name);
}

function getStringWidgets(node) {
    return (node.widgets || [])
        .filter(isStringWidget)
        .sort((left, right) => {
            const leftIndex = Number(left.name.split("_")[1]);
            const rightIndex = Number(right.name.split("_")[1]);
            return leftIndex - rightIndex;
        });
}

function hasLinkedInput(node, widgetName) {
    return Boolean(
        (node.inputs || []).find((input) => input.widget?.name === widgetName && input.link != null)
    );
}

function isFilledStringWidget(node, widget) {
    const value = typeof widget?.value === "string" ? widget.value.trim() : "";
    return Boolean(value) || hasLinkedInput(node, widget?.name);
}

function hideWidget(node, widget, suffix = "") {
    if (!widget || widget.type === HIDDEN_TYPE + suffix) {
        return;
    }

    widget.origType = widget.type;
    widget.hidden = true;
    widget.origComputeSize = widget.computeSize;
    widget.origSerializeValue = widget.serializeValue;
    widget.computeSize = () => [0, -4];
    widget.type = HIDDEN_TYPE + suffix;
    widget.serializeValue = () => {
        if (!node.inputs) {
            return undefined;
        }

        const nodeInput = node.inputs.find((input) => input.widget?.name === widget.name);
        if (!nodeInput || !nodeInput.link) {
            return undefined;
        }

        return widget.origSerializeValue ? widget.origSerializeValue() : widget.value;
    };

    if (widget.linkedWidgets) {
        for (const linkedWidget of widget.linkedWidgets) {
            hideWidget(node, linkedWidget, ":" + widget.name);
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
        for (const linkedWidget of widget.linkedWidgets) {
            showWidget(linkedWidget);
        }
    }
}

function refreshVisibleWidgets(node) {
    const widgets = getStringWidgets(node);
    let lastFilledIndex = -1;

    for (let index = 0; index < widgets.length; index++) {
        if (isFilledStringWidget(node, widgets[index])) {
            lastFilledIndex = index;
        }
    }

    const visibleCount = Math.min(Math.max(lastFilledIndex + 2, 2), MAX_OPTIONS);

    for (let index = 0; index < widgets.length; index++) {
        if (index < visibleCount) {
            showWidget(widgets[index]);
        } else {
            hideWidget(node, widgets[index]);
        }
    }

    node.setSize?.(node.computeSize());
    node.setDirtyCanvas(true, true);
}

function wrapWidgetCallback(node, widget) {
    if (widget.__jsgWrapped) {
        return;
    }

    widget.__jsgWrapped = true;
    const originalCallback = widget.callback;
    const refresh = () => refreshVisibleWidgets(node);

    widget.callback = function (...args) {
        const result = originalCallback ? originalCallback.apply(this, args) : undefined;
        refresh();
        return result;
    };

    if (widget.inputEl && !widget.__jsgInputListenerAttached) {
        widget.__jsgInputListenerAttached = true;
        widget.inputEl.addEventListener("input", refresh);
        widget.inputEl.addEventListener("change", refresh);
    }
}

function applySeedControl(node) {
    const seedWidget = getWidgetByName(node, "seed");
    const controlWidget = getWidgetByName(node, "control_after_generate") || getWidgetByName(node, "control_before_generate");
    if (!seedWidget || !controlWidget) {
        return;
    }

    const min = Math.max(0, Number(seedWidget.options?.min ?? 0));
    const max = Math.min(MAX_SAFE_RANDOM, Number(seedWidget.options?.max ?? MAX_SAFE_RANDOM));
    const step = Math.max(1, Number(seedWidget.options?.step ?? 1));
    const mode = controlWidget.value;
    let nextSeed = Number(seedWidget.value);

    switch (mode) {
        case "increment":
            nextSeed += step;
            if (nextSeed > max) {
                nextSeed = min;
            }
            break;
        case "decrement":
            nextSeed -= step;
            if (nextSeed < min) {
                nextSeed = max;
            }
            break;
        case "randomize": {
            const range = Math.floor((max - min) / step) + 1;
            nextSeed = min + Math.floor(Math.random() * range) * step;
            break;
        }
        case "fixed":
        default:
            return;
    }

    seedWidget.value = nextSeed;
    seedWidget.callback?.(nextSeed);
    node.setDirtyCanvas?.(true, true);
}

app.registerExtension({
    name: "JSG.Utils.StringInputNodes",
    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (!STRING_INPUT_NODES.has(nodeData.name)) {
            return;
        }

        const onNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            const result = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;

            for (const widget of getStringWidgets(this)) {
                wrapWidgetCallback(this, widget);
            }

            refreshVisibleWidgets(this);
            return result;
        };

        const onConfigure = nodeType.prototype.onConfigure;
        nodeType.prototype.onConfigure = function () {
            const result = onConfigure ? onConfigure.apply(this, arguments) : undefined;

            for (const widget of getStringWidgets(this)) {
                wrapWidgetCallback(this, widget);
            }

            refreshVisibleWidgets(this);
            return result;
        };

        const onConnectionsChange = nodeType.prototype.onConnectionsChange;
        nodeType.prototype.onConnectionsChange = function () {
            const result = onConnectionsChange ? onConnectionsChange.apply(this, arguments) : undefined;
            refreshVisibleWidgets(this);
            return result;
        };

        const onExecuted = nodeType.prototype.onExecuted;
        nodeType.prototype.onExecuted = function () {
            const result = onExecuted ? onExecuted.apply(this, arguments) : undefined;
            if (SEED_CONTROL_NODES.has(nodeData.name)) {
                applySeedControl(this);
            }
            return result;
        };
    },
});