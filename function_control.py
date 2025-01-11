from comfy_execution.graph import ExecutionBlocker
from comfy_execution.graph_utils import GraphBuilder, is_link

from .consts import TYPE_FUNCTION_START, TYPE_FUNCTION_DEF
from .graph_utils import search_nodes_between, find_max_output_index
from .utils import DefaultValueWhenOutofRangeTuple, DefaultValueWhenKeyMatchedDict


class FunctionControl:
    def __init__(self, start_node_id=None, end_node_id=None):
        self.start_node_id = start_node_id
        self.end_node_id = end_node_id


class FunctionDefStartNode:

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {},
            "optional": DefaultValueWhenKeyMatchedDict(
                {},
                ("*",),
                lambda k: isinstance(k, str) and (k.startswith("input") or k == "execute"),
            ),
            "hidden": {
                "unique_id": "UNIQUE_ID",
                "dynprompt": "DYNPROMPT",
            },
        }

    # 为了通过 ComfyUI 的Prompt Validation，需要实现一个可以处理超出范围索引的元组
    RETURN_TYPES = DefaultValueWhenOutofRangeTuple(tuple([TYPE_FUNCTION_START]), "*")
    RETURN_NAMES = DefaultValueWhenOutofRangeTuple(tuple(["function_start"]), "*")
    FUNCTION = "function_def_start"
    CATEGORY = "Power Flow/Flow Control"

    def function_def_start(self, unique_id, dynprompt, execute=False, **kwargs):
        if not execute:
            max_output_index = find_max_output_index(unique_id, dynprompt)
            return tuple([FunctionControl(start_node_id=unique_id)] + [ExecutionBlocker(None)] * (max_output_index))
        max_index = find_max_input_index(kwargs, "input")
        values = []
        for i in range(max_index + 1):
            values.append(kwargs.get(f"input{i}", None))
        return tuple([FunctionControl(start_node_id=unique_id)] + values)


class FunctionDefEndNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "function_start": (TYPE_FUNCTION_START,),
            },
            "optional": DefaultValueWhenKeyMatchedDict(
                {},
                ("*", {"lazy": True}),
                lambda k: isinstance(k, str) and (k.startswith("output") or k == "execute"),
            ),
            "hidden": {
                "unique_id": "UNIQUE_ID",
            },
        }

    RETURN_TYPES = DefaultValueWhenOutofRangeTuple(tuple([TYPE_FUNCTION_DEF]), "*")
    RETURN_NAMES = DefaultValueWhenOutofRangeTuple(tuple(["function_definition"]), "*")

    FUNCTION = "execute_function"
    CATEGORY = "Power Flow/Flow Control"

    def check_lazy_status(self, function_start, unique_id, execute=False, **kwargs):
        if not execute:
            return []
        else:
            return list(kwargs.keys())

    def execute_function(self, function_start, unique_id, execute=False, **kwargs):
        output_function_control = FunctionControl(
            start_node_id=function_start.start_node_id, end_node_id=unique_id
        )
        if not execute:
            return (output_function_control,)
        else:
            max_index = find_max_input_index(kwargs, "output")
            return tuple(
                [output_function_control]
                + [kwargs.get(f"output{i}", None) for i in range(max_index + 1)]
            )


class ExecuteFunctionNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "function_definition": (TYPE_FUNCTION_DEF,),
            },
            "optional": DefaultValueWhenKeyMatchedDict(
                {},
                ("*",),
                lambda k: isinstance(k, str) and k.startswith("input"),
            ),
            "hidden": {
                "dynprompt": "DYNPROMPT",
                "unique_id": "UNIQUE_ID",
            },
        }

    RETURN_TYPES = DefaultValueWhenOutofRangeTuple(tuple(), "*")
    RETURN_NAMES = DefaultValueWhenOutofRangeTuple(tuple(), "*")

    FUNCTION = "execute_function"
    CATEGORY = "Power Flow/Flow Control"

    def execute_function(
            self, function_definition: FunctionControl, dynprompt, unique_id, **kwargs
    ):
        contained = search_nodes_between(
            function_definition.start_node_id,
            function_definition.end_node_id,
            dynprompt,
        )
        contained.add(function_definition.end_node_id)
        contained.add(function_definition.start_node_id)

        graph = GraphBuilder()
        for node_id in contained:
            original_node = dynprompt.get_node(node_id)
            if node_id == function_definition.end_node_id:
                node = graph.node(
                    original_node["class_type"],
                    "Recurse",
                    execute=True,
                )
            elif node_id == function_definition.start_node_id:
                node = graph.node(
                    original_node["class_type"],
                    node_id,
                    execute=True,
                )
            else:
                node = graph.node(
                    original_node["class_type"],
                    node_id,
                )
            node.set_override_display_id(node_id)
        for node_id in contained:
            original_node = dynprompt.get_node(node_id)
            node = graph.lookup_node(
                "Recurse" if node_id == function_definition.end_node_id else node_id
            )
            for k, v in original_node["inputs"].items():
                if is_link(v) and v[0] in contained:
                    parent = graph.lookup_node(v[0])
                    node.set_input(k, parent.out(v[1]))
                else:
                    node.set_input(k, v)
        new_open = graph.lookup_node(function_definition.start_node_id)
        max_index = find_max_input_index(kwargs, "input")
        for i in range(max_index + 1):
            key = f"input{i}"
            new_open.set_input(key, kwargs.get(key, None))
        end_node = graph.lookup_node("Recurse")
        max_output_index = find_max_output_index(unique_id, dynprompt)
        result = tuple(map(lambda x: end_node.out(x + 1), range(max_output_index + 1)))
        return {
            "result": result,
            "expand": graph.finalize(),
        }


def find_max_input_index(kwargs, prefix):
    max_index = -1
    for key in kwargs:
        if key.startswith(prefix):
            try:
                index = int(key[len(prefix):])
                max_index = max(max_index, index)
            except ValueError:
                continue
    return max_index
