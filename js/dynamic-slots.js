import { app } from "../../scripts/app.js";

const Mode = {
    INPUT_AND_OUTPUT: "inputAndOutput",
    INPUT_ONLY: "inputOnly",
    OUTPUT_ONLY: "outputOnly",
    SEPARATE_INPUT_OUTPUT: "separateInputOutput",
};

function addInputOutputAndResize(node, inputName, inputType, outputName, outputType, mode, resize = true) {
    const [oldWidth, oldHeight] = node.size;
    const addInput = mode !== Mode.OUTPUT_ONLY && inputName;
    const addOutput = mode !== Mode.INPUT_ONLY && outputName;
    let heightDelta = LiteGraph.NODE_SLOT_HEIGHT;
    if (addInput && !addOutput && node.inputs.length < node.outputs.length) {
        heightDelta = 0;
    }
    if (addOutput && !addInput && node.outputs.length < node.inputs.length) {
        heightDelta = 0;
    }
    if (addInput) {
        node.addInput(inputName, inputType);
    }
    if (addOutput) {
        node.addOutput(outputName, outputType); 
    }

    if (!resize) {
        node.setSize([oldWidth, oldHeight]);
        return;
    }

    for (const widget of node.widgets) {
        widget.last_y += heightDelta;
    }

    node.setSize([
        Math.max(oldWidth, node.size[0]),
        Math.max(oldHeight + heightDelta, node.size[1])
    ]);
}

function removeInputOutputAndResize(node, inputName, outputName, mode, resize = true) {
    const [oldWidth, oldHeight] = node.size;
    const removeInput = mode !== Mode.OUTPUT_ONLY && inputName;
    const removeOutput = mode !== Mode.INPUT_ONLY && outputName;
    let hightDelta = -LiteGraph.NODE_SLOT_HEIGHT;
    if (removeInput && !removeOutput && node.inputs.length <= node.outputs.length) {
        hightDelta = 0;
    }
    if (removeOutput && !removeInput && node.outputs.length <= node.inputs.length) {
        hightDelta = 0;
    }
    if (removeInput) {
        node.removeInput(node.findInputSlot(inputName));
    }
    if (removeOutput) {
        node.removeOutput(node.findOutputSlot(outputName));
    }

    if (!resize) {
        node.setSize([oldWidth, oldHeight]);
        return;
    }   

    for (const widget of node.widgets) {
        widget.last_y += hightDelta;
    }

    node.setSize([
        Math.max(oldWidth, node.size[0]),
        Math.max(oldHeight + hightDelta, node.size[1])
    ])
}

const NODE_CONFIG = {
    "ComfyUI_Power_Flow.WhileLoopOpen": {
        startIndex: 0,
        mode: Mode.INPUT_AND_OUTPUT,
        inputPrefix: "initial_value_",
        outputPrefix: "value_"
    },
    "ComfyUI_Power_Flow.WhileLoopClose": {
        startIndex: 0,
        mode: Mode.INPUT_AND_OUTPUT,
        inputPrefix: "initial_value_",
        outputPrefix: "value_"
    },
    "ComfyUI_Power_Flow.ForLoopOpen": {
        startIndex: 0,
        mode: Mode.INPUT_AND_OUTPUT,
        inputPrefix: "initial_value_",
        outputPrefix: "value_"
    },
    "ComfyUI_Power_Flow.ForLoopClose": {
        startIndex: 0,
        mode: Mode.INPUT_AND_OUTPUT,
        inputPrefix: "initial_value_",
        outputPrefix: "value_"
    },
    "ComfyUI_Power_Flow.FunctionDefStart": {
        startIndex: 0,
        mode: Mode.OUTPUT_ONLY,
        inputPrefix: "input",
        outputPrefix: "input"
    },
    "ComfyUI_Power_Flow.FunctionDefEnd": {
        startIndex: 0,
        mode: Mode.INPUT_ONLY,
        inputPrefix: "output",
        outputPrefix: "output"
    },
    "ComfyUI_Power_Flow.ExecuteFunction": {
        startIndex: 0,
        mode: Mode.SEPARATE_INPUT_OUTPUT,
        inputPrefix: "input",
        outputPrefix: "output"
    },
    "ComfyUI_Power_Flow.ForInLoopOpen": {
        startIndex: 0,
        mode: Mode.INPUT_AND_OUTPUT,
        inputPrefix: "initial_value_",
        outputPrefix: "value_"
    },
    "ComfyUI_Power_Flow.ForInLoopClose": {
        startIndex: 0,
        mode: Mode.INPUT_AND_OUTPUT,
        inputPrefix: "initial_value_",
        outputPrefix: "value_"
    },
    "ComfyUI_Power_Flow.RunPythonScript": {
        startIndex: 0,
        mode: Mode.SEPARATE_INPUT_OUTPUT,
        inputPrefix: "input",
        outputPrefix: "output"
    },
    "ComfyUI_Power_Flow.PythonEval": {
        startIndex: 0,
        mode: Mode.INPUT_ONLY,
        inputPrefix: "i",
        outputPrefix: "output"
    }
}

function getMaxInputSlotCount(node, config, filter = slot => true) {
    const prefix = config.inputPrefix;
    const slots = node.inputs;

    const maxIndex = Math.max(...slots
        .filter(slot => slot.name.startsWith(prefix))
        .filter(filter)
        .map(slot => parseInt(slot.name.substring(prefix.length)))
        .filter(num => !isNaN(num)));
    return Math.max(maxIndex + 1 - config.startIndex, 0);
}

function getMaxOutputSlotCount(node, config, filter = slot => true) {
    const prefix = config.outputPrefix;
    const slots = node.outputs;
    const maxIndex = Math.max(...slots
        .filter(slot => slot.name.startsWith(prefix))
        .filter(filter)
        .map(slot => parseInt(slot.name.substring(prefix.length)))
        .filter(num => !isNaN(num)));
    return Math.max(maxIndex + 1 - config.startIndex, 0);
}

function getMaxSlotCount(node, config, inputFilter = slot => true, outputFilter = slot => true) {
    const inputCount = getMaxInputSlotCount(node, config, inputFilter);
    const outputCount = getMaxOutputSlotCount(node, config, outputFilter);
    return Math.max(inputCount, outputCount);
}

function findMaxDynamicSlotCount(graph) {
    let maxCount = 0;
    for (const node of graph.nodes) {
        const config = NODE_CONFIG[node.type];
        if (!config) {
            continue;
        }

        const count = getMaxSlotCount(node, config);
        maxCount = Math.max(maxCount, count);
    }
    return maxCount;
}

function removeRedundantDynamicSlots(node) {
    const config = NODE_CONFIG[node.type];
    if (!config) {
        return;
    }
    if (config.mode === Mode.SEPARATE_INPUT_OUTPUT || config.mode === Mode.OUTPUT_ONLY) {
        const maxOutputCount = getMaxOutputSlotCount(node, config);
        const maxLinkedOutputCount = getMaxOutputSlotCount(node, config, slot => slot.links);
        for (let i = maxOutputCount - 1; i >= maxLinkedOutputCount; i--) {
            removeInputOutputAndResize(node, null, config.outputPrefix + i, config.mode, false);
        }
    } else if (config.mode === Mode.INPUT_AND_OUTPUT) {
        const maxOutputCount = getMaxOutputSlotCount(node, config);
        const maxInputCount = getMaxInputSlotCount(node, config);
        const maxLinkedCount = getMaxSlotCount(node, config, slot => slot.link, slot => slot.links);
        for (let i = maxOutputCount; i > maxInputCount; i--) {
            const removeIndex = config.startIndex + i - 1;
            removeInputOutputAndResize(node, null, config.outputPrefix + removeIndex, config.mode, false);
        }
        for (let i = maxInputCount; i > maxLinkedCount; i--) {
            const removeIndex = config.startIndex + i - 1;
            removeInputOutputAndResize(node, config.inputPrefix + removeIndex, config.outputPrefix + removeIndex, config.mode, false);
        }
    }
} 

app.registerExtension({
    name: "ComfyUI_Power_Flow.extension.dynamic_loop_slot",
    _maxDynamicSlotCount: 0,
    _loadingGraph: false,

    async beforeConfigureGraph(graphData, missingNodeTypes) {
        this._loadingGraph = true;
        this._maxDynamicSlotCount = findMaxDynamicSlotCount(graphData);
    },

    async afterConfigureGraph(missingNodeTypes) {
        this._loadingGraph = false;
    },

    async loadedGraphNode(node, app) {
        const config = NODE_CONFIG[node.type];
        if (!config) {
            return;
        }
        removeRedundantDynamicSlots(node);
    },

    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (!(nodeData.name in NODE_CONFIG)) {
            return;
        }
        const { startIndex, mode, inputPrefix, outputPrefix } = NODE_CONFIG[nodeData.name];

        function getMaxInputIndex(node) {
            let maxIndex = -1;
            for (const input of node.inputs) {
                if (input.name.startsWith(inputPrefix)) {
                    const index = parseInt(input.name.substring(inputPrefix.length));
                    maxIndex = Math.max(maxIndex, index);
                }
            }
            return maxIndex;
        }

        function getMaxOutputIndex(node) {
            let maxIndex = -1;
            for (const output of node.outputs) {
                if (output.name.startsWith(outputPrefix)) {
                    const index = parseInt(output.name.substring(outputPrefix.length));
                    maxIndex = Math.max(maxIndex, index);
                }
            }
            return maxIndex;
        }

        function addDynamicInputOutput(node) {
            let maxInputIndex = getMaxInputIndex(node);
            let maxOutputIndex = getMaxOutputIndex(node);
            if (maxInputIndex === -1) {
                maxInputIndex = startIndex - 1;
            }
            if (maxOutputIndex === -1) {
                maxOutputIndex = startIndex - 1;
            }
            addInputOutputAndResize(node, inputPrefix + (maxInputIndex + 1), "*", outputPrefix + (maxOutputIndex + 1), "*", mode);
        }

        function removeDynamicInputOutput(node) {
            const maxInputIndex = getMaxInputIndex(node);
            const maxOutputIndex = getMaxOutputIndex(node);
            if (maxInputIndex < startIndex && maxOutputIndex < startIndex) {
                return;
            }
            removeInputOutputAndResize(node, inputPrefix + maxInputIndex, outputPrefix + maxOutputIndex, mode);
        }

        function addDynamicOutput(node) {
            let maxIndex = getMaxOutputIndex(node);
            if (maxIndex === -1) {
                maxIndex = startIndex - 1;
            }
            addInputOutputAndResize(node, null, null, outputPrefix + (maxIndex + 1), "*", mode);
        }

        function removeDynamicOutput(node) {
            const maxIndex = getMaxOutputIndex(node);
            if (maxIndex < startIndex) {
                return;
            }
            removeInputOutputAndResize(node, null, outputPrefix + maxIndex, mode);
        }

        function addDynamicInput(node) {
            let maxIndex = getMaxInputIndex(node);
            if (maxIndex === -1) {
                maxIndex = startIndex - 1;
            }
            addInputOutputAndResize(node, inputPrefix + (maxIndex + 1), "*", null, null, mode);
        }

        function removeDynamicInput(node) {
            const maxIndex = getMaxInputIndex(node);
            removeInputOutputAndResize(node, inputPrefix + maxIndex, null, mode);
        }


        // 保存extension的引用
        const extension = this;

        const onNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = async function () {
            const me = onNodeCreated?.apply(this);
            const node = this;

            if (mode === Mode.SEPARATE_INPUT_OUTPUT) {
                node.addWidget(
                    "button",
                    "add input",
                    null,
                    () => addDynamicInput(node),
                    { serialize: false },
                );
                node.addWidget(
                    "button",
                    "remove input",
                    null,
                    () => removeDynamicInput(node),
                    { serialize: false },
                );
                node.addWidget(
                    "button",
                    "add output",
                    null,
                    () => addDynamicOutput(node),
                    { serialize: false },
                );
                node.addWidget(
                    "button",
                    "remove output",
                    null,
                    () => removeDynamicOutput(node),
                    { serialize: false },
                );
            } else {
                node.addWidget(
                    "button",
                    "add a slot",
                    null,
                    () => addDynamicInputOutput(node),
                    { serialize: false },
                );
                node.addWidget(
                    "button",
                    "remove last slot",
                    null,
                    () => removeDynamicInputOutput(node),
                    { serialize: false },
                );
            }
            // 有些其它custom node会依赖固定数量的output，所以需要预先添加一些output防止这些custom node报错,
            // 例如 ComfyUI-Impact-Pack中的Impact Compare节点， 就会依赖固定数量的output
            if (extension._loadingGraph) {
                for (let i = 0; i < extension._maxDynamicSlotCount; i++) {
                    if (mode !== Mode.INPUT_ONLY) {
                        node.addOutput(outputPrefix + (i + startIndex), "*");
                    }
                }
            }
            return me;
        }
    },

});
