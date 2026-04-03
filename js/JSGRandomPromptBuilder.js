/**
 * JSGRandomPromptBuilder.js
 *
 * Handles the Refresh toggle for JSGRandomPromptBuilder nodes.
 *
 * When the user toggles "refresh" to true:
 *   1. Fetch fresh input spec from /object_info/ (triggers Python INPUT_TYPES → re-reads JSON files).
 *   2. Diff the dynamic widgets (those starting with "Random " or "Value ") against the new spec.
 *   3. Remove widgets that no longer exist.
 *   4. Preserve values of widgets that still exist.
 *   5. Add widgets that are new (with defaults).
 *   6. Apply the order from the new spec (index/subIndex sorted in Python).
 *   7. Reset "refresh" back to false.
 */
import { app } from "../../../scripts/app.js";
import { ComfyWidgets } from "../../../scripts/widgets.js";

const NODE_TYPE = "JSGRandomPromptBuilder";

function isDynamic(name) {
    return name.startsWith("Random ") || name.startsWith("Value ");
}

async function fetchNodeSpec() {
    const resp = await fetch("/object_info/" + NODE_TYPE);
    if (!resp.ok) throw new Error("HTTP " + resp.status);
    const json = await resp.json();
    return json[NODE_TYPE];
}

async function rebuildDynamicInputs(node) {
    let spec;
    try {
        spec = await fetchNodeSpec();
    } catch (e) {
        console.error("[JSGRandomPromptBuilder] Failed to fetch node spec:", e);
        return;
    }

    const optional = spec.input?.optional ?? {};
    const newNames = Object.keys(optional).filter(isDynamic);

    // ── Save values of current dynamic widgets ──────────────────────────────
    const savedValues = {};
    for (const w of (node.widgets ?? [])) {
        if (isDynamic(w.name)) savedValues[w.name] = w.value;
    }

    // ── Remove current dynamic widgets and clean up their DOM elements ────────
    node.widgets = (node.widgets ?? []).filter(w => {
        if (!isDynamic(w.name)) return true;
        // Multiline STRING widgets have a textarea DOM element — remove it
        if (w.inputEl) w.inputEl.remove();
        return false;
    });

    // Remove any corresponding node.inputs that belong to removed dynamic widgets
    if (node.inputs) {
        node.inputs = node.inputs.filter(
            inp => !isDynamic(inp.widget?.name ?? "")
        );
    }

    // ── Re-add dynamic widgets in new spec order ──────────────────────────────
    for (const name of newNames) {
        const [type, opts = {}] = optional[name];
        const defaultVal = (opts.default !== undefined)
            ? opts.default
            : (type === "BOOLEAN" ? true : "");
        const value = Object.prototype.hasOwnProperty.call(savedValues, name)
            ? savedValues[name]
            : defaultVal;

        if (type === "BOOLEAN") {
            node.addWidget("toggle", name, value, () => {}, {
                on:      opts.label_on  ?? "true",
                off:     opts.label_off ?? "false",
                tooltip: opts.tooltip   ?? "",
                serialize: true,
            });
        } else {
            // STRING — use ComfyWidgets.STRING for proper single/multiline handling
            const result = ComfyWidgets.STRING(node, name, [type, opts], app);
            if (result?.widget) result.widget.value = value;
        }
    }

    node.setSize(node.computeSize());
    app.graph.setDirtyCanvas(true, true);
}

// ── Extension registration ────────────────────────────────────────────────────

app.registerExtension({
    name: "JSG.RandomPromptBuilder",

    async nodeCreated(node) {
        if (node.comfyClass !== NODE_TYPE) return;

        const refreshWidget = node.widgets?.find(w => w.name === "refresh");
        if (!refreshWidget) return;

        const origCallback = refreshWidget.callback;

        refreshWidget.callback = async function (value) {
            if (origCallback) origCallback.call(this, value);

            // Only act when toggled to true
            if (!value) return;

            await rebuildDynamicInputs(node);

            // Reset refresh back to false
            refreshWidget.value = false;
            node.setDirtyCanvas(true, true);
        };
    },
});
