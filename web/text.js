import { app } from "../../../scripts/app.js";
import { ComfyWidgets } from "../../../scripts/widgets.js";

// Displays input text on a node
app.registerExtension({
	name: "H-flow.Text",
	async beforeRegisterNodeDef(nodeType, nodeData, app) {
		if (nodeData.name === "TestText" || nodeData.name === "LLMTask") {
			function populate(text) {
				// 找到并移除之前添加的文本显示小部件
				if (this.widgets) {
					const textWidgetsToRemove = [];
					for (let i = 0; i < this.widgets.length; i++) {
						if (this.widgets[i]._showTextExtension) {
							textWidgetsToRemove.push(this.widgets[i]);
						}
					}
					
					// 移除之前添加的文本显示小部件
					for (const widget of textWidgetsToRemove) {
						widget.onRemove?.();
						this.widgets.splice(this.widgets.indexOf(widget), 1);
					}
				}

				// 添加新的文本显示小部件
				const v = [...text];
				if (!v[0]) {
					v.shift();
				}
				for (const list of v) {
					const w = ComfyWidgets["STRING"](this, "text2", ["STRING", { multiline: true }], app).widget;
					w.inputEl.readOnly = true;
					w.inputEl.style.opacity = 0.6;
					w.value = list;
					// 标记这个小部件是由ShowText扩展添加的
					w._showTextExtension = true;
				}

				requestAnimationFrame(() => {
					const sz = this.computeSize();
					if (sz[0] < this.size[0]) {
						sz[0] = this.size[0];
					}
					if (sz[1] < this.size[1]) {
						sz[1] = this.size[1];
					}
					this.onResize?.(sz);
					app.graph.setDirtyCanvas(true, false);
				});
			}

			// When the node is executed we will be sent the input text, display this in the widget
			const onExecuted = nodeType.prototype.onExecuted;
			nodeType.prototype.onExecuted = function (message) {
				onExecuted?.apply(this, arguments);
				populate.call(this, message.text);
			};

			const onConfigure = nodeType.prototype.onConfigure;
			// nodeType.prototype.onConfigure = function () {
			// 	onConfigure?.apply(this, arguments);
			// 	if (this.widgets_values?.length) {
			// 		populate.call(this, this.widgets_values.slice(+this.widgets_values.length > 1));
			// 	}
			// };
		}
	},
});
