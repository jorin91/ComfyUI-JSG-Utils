import { app } from "../../scripts/app.js";

const NODE_TYPE = "JSGFormattedStringViewer";
const VIEWER_HEIGHT = 160; // px — initial height for the read-only viewer

app.registerExtension({
    name: "JSG.FormattedStringViewer",

    beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name !== NODE_TYPE) return;

        // ── onNodeCreated ──────────────────────────────────────────────────
        const onNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            onNodeCreated?.apply(this, arguments);

            // Build a read-only textarea wrapped in a div widget
            const container = document.createElement("div");
            container.style.cssText = [
                "width:100%",
                "height:100%",
                "box-sizing:border-box",
                "padding:4px 6px",
            ].join(";");

            const ta = document.createElement("textarea");
            ta.readOnly = true;
            ta.placeholder = "(Connect a text input to see its breakdown here)";
            ta.style.cssText = [
                "width:100%",
                "height:100%",
                "box-sizing:border-box",
                "resize:none",
                "background:#1a1a1a",
                "color:#d4d4d4",
                "border:1px solid #444",
                "border-radius:4px",
                "font-family:monospace",
                "font-size:12px",
                "line-height:1.5",
                "padding:6px 8px",
                "white-space:pre",
                "overflow-y:auto",
                "cursor:default",
                "outline:none",
            ].join(";");

            container.appendChild(ta);

            // addDOMWidget keeps the element inside the LiteGraph node frame
            this._jsgViewerWidget = this.addDOMWidget(
                "jsg_viewer",  // widget name
                "div",         // displayed element type (used by LG for sizing)
                container,
                {
                    getValue: () => ta.value,
                    setValue: (v) => { ta.value = v ?? ""; },
                    getMinHeight: () => VIEWER_HEIGHT + 12,
                }
            );

            // Store textarea reference for onExecuted
            this._jsgViewerTextarea = ta;
        };

        // ── onExecuted ────────────────────────────────────────────────────
        // Python returns { "ui": { "formatted": [<str>] }, "result": (...) }
        const onExecuted = nodeType.prototype.onExecuted;
        nodeType.prototype.onExecuted = function (message) {
            onExecuted?.apply(this, arguments);

            const formatted = message?.formatted?.[0];
            if (this._jsgViewerTextarea && formatted !== undefined) {
                this._jsgViewerTextarea.value = formatted;
                // Refresh the canvas so the node redraws at its new size
                app.graph.setDirtyCanvas(true, true);
            }
        };
    },
});
