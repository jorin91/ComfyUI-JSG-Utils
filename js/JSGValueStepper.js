/**
 * JSGValueStepper.js
 *
 * Advances the JSGValueStepper value widget after each successful execution.
 * The widget is always moved to the next stepped value after execution.
 * Python decides whether outputs include the starting value or stepped value.
 */
import { app } from "../../../scripts/app.js";

const VALUE_STEPPER_NODE = "JSGValueStepper";

function getWidgetByName(node, name) {
    return (node.widgets || []).find((widget) => widget?.name === name);
}

function roundToTwo(value) {
    return Math.round((Number(value) + Number.EPSILON) * 100) / 100;
}

function updateValueWidget(node) {
    const valueWidget = getWidgetByName(node, "value");
    const modeWidget = getWidgetByName(node, "mode");
    const stepWidget = getWidgetByName(node, "step");

    if (!valueWidget || !modeWidget || !stepWidget) {
        return;
    }

    const value = Number(valueWidget.value);
    const step = Number(stepWidget.value);
    if (!Number.isFinite(value) || !Number.isFinite(step)) {
        return;
    }

    const nextValue = modeWidget.value === "decrement"
        ? roundToTwo(value - step)
        : roundToTwo(value + step);

    valueWidget.value = nextValue;
    valueWidget.callback?.(nextValue);
    node.setDirtyCanvas?.(true, true);
}

app.registerExtension({
    name: "JSG.Utils.ValueStepper",
    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name !== VALUE_STEPPER_NODE) {
            return;
        }

        const onExecuted = nodeType.prototype.onExecuted;
        nodeType.prototype.onExecuted = function () {
            const result = onExecuted ? onExecuted.apply(this, arguments) : undefined;
            updateValueWidget(this);
            return result;
        };
    },
});
