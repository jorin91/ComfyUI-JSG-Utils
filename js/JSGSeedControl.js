/**
 * JSGSeedControl.js
 *
 * Automatically advances the seed widget after execution based on the
 * control_after_generate / control_before_generate widget value
 * (increment, decrement, randomize, fixed).
 *
 * Covered nodes: JSGRandomStringChoice, JSGRandomStringChoiceList, JSGRandomBool
 */
import { app } from "../../../scripts/app.js";

const SEED_CONTROL_NODES = new Set([
    "JSGRandomStringChoice",
    "JSGRandomStringChoiceList",
    "JSGRandomBool",
]);

const MAX_SAFE_RANDOM = 1125899906842624;

function getWidgetByName(node, name) {
    return (node.widgets || []).find((widget) => widget?.name === name);
}

function applySeedControl(node) {
    const seedWidget = getWidgetByName(node, "seed");
    const controlWidget =
        getWidgetByName(node, "control_after_generate") ||
        getWidgetByName(node, "control_before_generate");

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
    name: "JSG.Utils.SeedControl",
    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (!SEED_CONTROL_NODES.has(nodeData.name)) {
            return;
        }

        const onExecuted = nodeType.prototype.onExecuted;
        nodeType.prototype.onExecuted = function () {
            const result = onExecuted ? onExecuted.apply(this, arguments) : undefined;
            applySeedControl(this);
            return result;
        };
    },
});
