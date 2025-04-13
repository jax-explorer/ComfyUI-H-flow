import { app } from '../../scripts/app.js'
import { api } from '../../scripts/api.js'
import { applyTextReplacements } from "../../scripts/utils.js";

function chainCallback(object, property, callback) {
    if (object == undefined) {
        //This should not happen.
        console.error("Tried to add callback to non-existant object")
        return;
    }
    if (property in object && object[property]) {
        const callback_orig = object[property]
        object[property] = function () {
            const r = callback_orig.apply(this, arguments);
            callback.apply(this, arguments);
            return r
        };
    } else {
        object[property] = callback;
    }
}


const convDict = {
    VHS_VideoCombine : ["frame_rate", "loop_count", "filename_prefix", "format", "pingpong", "save_image"],
    SaveVideo : ["frame_rate", "loop_count", "filename_prefix", "format", "pingpong", "save_image"],
};
const renameDict  = {VHS_VideoCombine : {save_output : "save_image"}, SaveVideo : {save_output : "save_image"}}
function useKVState(nodeType) {
    chainCallback(nodeType.prototype, "onNodeCreated", function () {
        chainCallback(this, "onConfigure", function(info) {
            if (this.inputs) {
                for (let i = 0; i < this.inputs.length; i++) {
                    let dt = this?.getInputDataType(i)
                    if (dt && this.inputs[i]?.type != dt && !(dt == "IMAGE" && this.inputs[i].type == "LATENT")) {
                        this.inputs[i].type = dt
                        console.warn("input type mismatch for " + this.title + " slot " + i)

                    }
                }
            }
            if (!this.widgets) {
                //Node has no widgets, there is nothing to restore
                return
            }
            if (typeof(info.widgets_values) != "object") {
                //widgets_values is in some unknown inactionable format
                return
            }
            let widgetDict = info.widgets_values
            if (info.widgets_values.length) {
                //widgets_values is in the old list format
                if (this.type in convDict) {
                    //widget does not have a conversion format provided
                    let convList = convDict[this.type];
                    if(info.widgets_values.length >= convList.length) {
                        //has all required fields
                        widgetDict = {}
                        for (let i = 0; i < convList.length; i++) {
                            if(!convList[i]) {
                                //Element should not be processed (upload button on load image sequence)
                                continue
                            }
                            widgetDict[convList[i]] = info.widgets_values[i];
                        }
                    } else {
                        //widgets_values is missing elements marked as required
                        //let it fall through to failure state
                    }
                }
            }
            if (widgetDict.length == undefined) {
                for (let w of this.widgets) {
                    if (w.name in widgetDict) {
                        w.value = widgetDict[w.name];
                    } else {
                        //Check for a legacy name that needs migrating
                        if (this.type in renameDict && w.name in renameDict[this.type]) {
                            if (renameDict[this.type][w.name] in widgetDict) {
                                w.value = widgetDict[renameDict[this.type][w.name]]
                                continue
                            }
                        }
                        //attempt to restore default value
                        let inputs = LiteGraph.getNodeType(this.type).nodeData.input;
                        let initialValue = null;
                        if (inputs?.required?.hasOwnProperty(w.name)) {
                            if (inputs.required[w.name][1]?.hasOwnProperty("default")) {
                                initialValue = inputs.required[w.name][1].default;
                            } else if (inputs.required[w.name][0].length) {
                                initialValue = inputs.required[w.name][0][0];
                            }
                        } else if (inputs?.optional?.hasOwnProperty(w.name)) {
                            if (inputs.optional[w.name][1]?.hasOwnProperty("default")) {
                                initialValue = inputs.optional[w.name][1].default;
                            } else if (inputs.optional[w.name][0].length) {
                                initialValue = inputs.optional[w.name][0][0];
                            }
                        }
                        if (initialValue) {
                            w.value = initialValue;
                        }
                    }
                }
            } else {
                //Saved data was not a map made by this method
                //and a conversion dict for it does not exist
                //It's likely an array and that has been blindly applied
                if (info?.widgets_values?.length != this.widgets.length) {
                    //Widget could not have restored properly
                    //Note if multiple node loads fail, only the latest error dialog displays
                    app.ui.dialog.show("Failed to restore node: " + this.title + "\nPlease remove and re-add it.")
                    this.bgcolor = "#C00"
                }
            }
        });
        chainCallback(this, "onSerialize", function(info) {
            info.widgets_values = {};
            if (!this.widgets) {
                //object has no widgets, there is nothing to store
                return;
            }
            for (let w of this.widgets) {
                info.widgets_values[w.name] = w.value;
            }
        });
    })
}

function fitHeight(node) {
    node.setSize([node.size[0], node.computeSize([node.size[0], node.size[1]])[1]])
    node?.graph?.setDirtyCanvas(true);
}


function addVideoPreview(nodeType) {
    console.log("addVideoPreview")
    chainCallback(nodeType.prototype, "onNodeCreated", function() {
        var element = document.createElement("div");
        const previewNode = this;
        var previewWidget = this.addDOMWidget("videopreview", "preview", element, {
            serialize: false,
            hideOnZoom: false,
            getValue() {
                return element.value;
            },
            setValue(v) {
                element.value = v;
            },
        });
        previewWidget.computeSize = function(width) {
            if (this.aspectRatio && !this.parentEl.hidden) {
                let height = (previewNode.size[0]-20)/ this.aspectRatio + 10;
                if (!(height > 0)) {
                    height = 0;
                }
                this.computedHeight = height + 10;
                return [width, height];
            }
            return [width, -4];//no loaded src, widget should not display
        }
        element.addEventListener('contextmenu', (e)  => {
            e.preventDefault()
            return app.canvas._mousedown_callback(e)
        }, true);
        element.addEventListener('pointerdown', (e)  => {
            e.preventDefault()
            return app.canvas._mousedown_callback(e)
        }, true);
        element.addEventListener('mousewheel', (e)  => {
            e.preventDefault()
            return app.canvas._mousewheel_callback(e)
        }, true);
        previewWidget.value = {hidden: false, paused: false, params: {},
            muted: app.ui.settings.getSettingValue("VHS.DefaultMute", false)}
        previewWidget.parentEl = document.createElement("div");
        previewWidget.parentEl.className = "vhs_preview";
        previewWidget.parentEl.style['width'] = "100%"
        element.appendChild(previewWidget.parentEl);
        previewWidget.videoEl = document.createElement("video");
        previewWidget.videoEl.controls = false;
        previewWidget.videoEl.loop = true;
        previewWidget.videoEl.muted = true;
        previewWidget.videoEl.style['width'] = "100%"
        previewWidget.videoEl.addEventListener("loadedmetadata", () => {

            previewWidget.aspectRatio = previewWidget.videoEl.videoWidth / previewWidget.videoEl.videoHeight;
            fitHeight(this);
        });
        previewWidget.videoEl.addEventListener("error", () => {
            //TODO: consider a way to properly notify the user why a preview isn't shown.
            previewWidget.parentEl.hidden = true;
            fitHeight(this);
        });
        previewWidget.videoEl.onmouseenter =  () => {
            previewWidget.videoEl.muted = previewWidget.value.muted
        };
        previewWidget.videoEl.onmouseleave = () => {
            previewWidget.videoEl.muted = true;
        };

        previewWidget.imgEl = document.createElement("img");
        previewWidget.imgEl.style['width'] = "100%"
        previewWidget.imgEl.hidden = true;
        previewWidget.imgEl.onload = () => {
            previewWidget.aspectRatio = previewWidget.imgEl.naturalWidth / previewWidget.imgEl.naturalHeight;
            fitHeight(this);
        };

        var timeout = null;
        this.updateParameters = (params, force_update) => {
            console.log("updateParameters", params, force_update);
            if (!previewWidget.value.params) {
                if(typeof(previewWidget.value != 'object')) {
                    previewWidget.value =  {hidden: false, paused: false}
                }
                previewWidget.value.params = {}
            }
            Object.assign(previewWidget.value.params, params)
            if (!force_update &&
                !app.ui.settings.getSettingValue("VHS.AdvancedPreviews", false)) {
                return;
            }
            if (timeout) {
                clearTimeout(timeout);
            }
            if (force_update) {
                previewWidget.updateSource();
            } else {
                timeout = setTimeout(() => previewWidget.updateSource(),100);
            }
        };
        previewWidget.updateSource = function () {
            console.log("previewWidget.updateSource")
            console.log("previewWidget.updateSource", this.value)

            if (this.value.params == undefined) {
                return;
            }
            let params =  {}
            Object.assign(params, this.value.params);//shallow copy
            this.parentEl.hidden = this.value.hidden;
            this.videoEl.autoplay = !this.value.paused && !this.value.hidden;
            let target_width = 256
            if (element.style?.width) {
                //overscale to allow scrolling. Endpoint won't return higher than native
                target_width = element.style.width.slice(0,-2)*2;
            }
            if (!params.force_size || params.force_size.includes("?") || params.force_size == "Disabled") {
                params.force_size = target_width+"x?"
            } else {
                let size = params.force_size.split("x")
                let ar = parseInt(size[0])/parseInt(size[1])
                params.force_size = target_width+"x"+(target_width/ar)
            }
            if (app.ui.settings.getSettingValue("VHS.AdvancedPreviews", false)) {
                this.videoEl.src = api.apiURL('/viewvideo?' + new URLSearchParams(params));
            } else {
                previewWidget.videoEl.src = api.apiURL('/view?' + new URLSearchParams(params));
            }
            this.videoEl.hidden = false;
            this.imgEl.hidden = true;
        }
        previewWidget.parentEl.appendChild(previewWidget.videoEl)
        previewWidget.parentEl.appendChild(previewWidget.imgEl)
    });
}


function path_stem(path) {
    let i = path.lastIndexOf("/");
    if (i >= 0) {
        return [path.slice(0,i+1),path.slice(i+1)];
    }
    return ["",path];
}


app.registerExtension({
    name: "H-flow.Video",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if(nodeData?.name?.startsWith("VHS_")) {
            useKVState(nodeType);
            if (nodeData.description) {
                let description = nodeData.description
                let el = document.createElement("div")
                el.innerHTML = description
                if (!el.children.length) {
                    //Is plaintext. Do minor convenience formatting
                    let chunks = description.split('\n')
                    nodeData.description = chunks[0]
                    description = chunks.join('<br>')
                } else {
                    nodeData.description = el.querySelector('#VHS_shortdesc')?.innerHTML || el.children[1]?.firstChild?.innerHTML
                }
                chainCallback(nodeType.prototype, "onNodeCreated", function () {
                    helpDOM.addHelp(this, nodeType, description)
                    this.setSize(this.computeSize())
                })
            }
            chainCallback(nodeType.prototype, "onNodeCreated", function () {
                let new_widgets = []
                if (this.widgets) {
                    for (let w of this.widgets) {
                        let input = this.constructor.nodeData.input
                        let config = input?.required[w.name] ?? input.optional[w.name]
                        if (!config) {
                            continue
                        }
                        if (w?.type == "text" && config[1].vhs_path_extensions) {
                            new_widgets.push(app.widgets.VHSPATH({}, w.name, ["VHSPATH", config[1]]));
                        } else {
                            new_widgets.push(w)
                        }
                    }
                    this.widgets = new_widgets;
                }
            });
        }
        if (nodeData?.name == "SaveVideo" || nodeData?.name == "KlingImageToVideo" || nodeData?.name == "RunwayGen3ImageToVideo" || nodeData?.name == "LumaRay2ImageToVideo" || nodeData?.name == "Hailuo01ImageToVideo" || nodeData?.name == "Wan2ImageToVideo") {
            console.log("nodeData", nodeData);
            
            chainCallback(nodeType.prototype, "onExecuted", function(message) {
                console.log("onExecuted", message);
                if (message?.videos) {
                    this.updateParameters(message.videos[0], true);
                }
            });
            addVideoPreview(nodeType);

            chainCallback(nodeType.prototype, "onNodeCreated", function() {
                this._outputs = this.outputs
                Object.defineProperty(this, "outputs", {
                    set : function(value) {
                        this._outputs = value;
                        requestAnimationFrame(() => {
                            if (app.nodeOutputs[this.id + ""]) {
                                this.updateParameters(app.nodeOutputs[this.id+""].gifs[0], true);
                            }
                        })
                    },
                    get : function() {
                        return this._outputs;
                    }
                });
                //Display previews after reload/ loading workflow
                requestAnimationFrame(() => {this.updateParameters({}, true);});
            });
        }
    },
    async getCustomWidgets() {
        return {
            VHSPATH(node, inputName, inputData) {
                let w = {
                    name : inputName,
                    type : "VHS.PATH",
                    value : "",
                    draw : function(ctx, node, widget_width, y, H) {
                        //Adapted from litegraph.core.js:drawNodeWidgets
                        var show_text = app.canvas.ds.scale > 0.5;
                        var margin = 15;
                        var text_color = LiteGraph.WIDGET_TEXT_COLOR;
                        var secondary_text_color = LiteGraph.WIDGET_SECONDARY_TEXT_COLOR;
                        ctx.textAlign = "left";
                        ctx.strokeStyle = LiteGraph.WIDGET_OUTLINE_COLOR;
                        ctx.fillStyle = LiteGraph.WIDGET_BGCOLOR;
                        ctx.beginPath();
                        if (show_text)
                            ctx.roundRect(margin, y, widget_width - margin * 2, H, [H * 0.5]);
                        else
                            ctx.rect( margin, y, widget_width - margin * 2, H );
                        ctx.fill();
                        if (show_text) {
                            if(!this.disabled)
                                ctx.stroke();
                            ctx.save();
                            ctx.beginPath();
                            ctx.rect(margin, y, widget_width - margin * 2, H);
                            ctx.clip();

                            //ctx.stroke();
                            ctx.fillStyle = secondary_text_color;
                            const label = this.label || this.name;
                            if (label != null) {
                                ctx.fillText(label, margin * 2, y + H * 0.7);
                            }
                            ctx.fillStyle = this.value ? text_color : '#777';
                            ctx.textAlign = "right";
                            let disp_text = this.format_path(String(this.value || this.options.placeholder))
                            ctx.fillText(disp_text, widget_width - margin * 2, y + H * 0.7); //30 chars max
                            ctx.restore();
                        }
                    },
                    options : {},
                    format_path : function(path) {
                        //Formats the full path to be under 30 characters
                        if (path.length <= 30) {
                            return path;
                        }
                        let filename = path_stem(path)[1]
                        if (filename.length > 28) {
                            //may all fit, but can't squeeze more info
                            return filename.substr(0,30);
                        }
                        //TODO: find solution for windows, path[1] == ':'?
                        let isAbs = path[0] == '/';
                        let partial = path.substr(path.length - (isAbs ? 28:29))
                        let cutoff = partial.indexOf('/');
                        if (cutoff < 0) {
                            //Can occur, but there isn't a nicer way to format
                            return path.substr(path.length-30);
                        }
                        return (isAbs ? '/…':'…') + partial.substr(cutoff);

                    }
                };
                if (inputData.length > 1) {
                    w.options = inputData[1]
                    if (inputData[1].default) {
                        w.value = inputData[1].default;
                    }
                }

                if (!node.widgets) {
                    node.widgets = [];
                }
                node.widgets.push(w);
                return w;
            }
        }
    },
    async loadedGraphNode(node) {
        //Check and migrate inputs named batch_manager from old workflows
        if (node.type?.startsWith("VHS_") && node.inputs) {
            const batchInput = node.inputs.find((i) => i.name == "batch_manager")
            if (batchInput) {
                batchInput.name = "meta_batch"
            }
        }
    },

    async setup() {
        //cg-use-everywhere link workaround
        //particularly invasive, plan to remove
        let originalGraphToPrompt = app.graphToPrompt
        let graphToPrompt = async function() {
            let res = await originalGraphToPrompt.apply(this, arguments);
            for (let n of app.graph._nodes) {
                if (n?.type?.startsWith('VHS_LoadVideo')) {
                    if (!n?.inputs[1]?.link && res?.output[n.id]?.inputs?.vae) {
                        delete res.output[n.id].inputs.vae
                    }
                }
            }
            return res
        }
        app.graphToPrompt = graphToPrompt
    },
    async init() {
        if (app.VHSHelp != helpDOM) {
            helpDOM = app.VHSHelp
        } else {
            initHelpDOM()
        }
        let e = app.extensions.filter((w) => w.name == 'UVR5.AudioPreviewer')
        if (e.length) {
            let orig = e[0].beforeRegisterNodeDef
            e[0].beforeRegisterNodeDef = function(nodeType, nodeData, app) {
                if(!nodeData?.name?.startsWith("VHS_")) {
                    return orig.apply(this, arguments);
                }
            }
        }

    },
});
