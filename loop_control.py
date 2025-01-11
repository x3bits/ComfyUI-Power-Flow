import uuid

from comfy_execution.graph import ExecutionBlocker
from comfy_execution.graph_utils import GraphBuilder, is_link

from .consts import TYPE_WHILE_LINK, TYPE_FOR_LINK
from .graph_utils import search_nodes_between
from .utils import DefaultValueWhenOutofRangeTuple, DefaultValueWhenKeyMatchedDict
from .utils import MakeSmartType


class WhileLink:
    def __init__(self, open_node_id, enabled):
        self.open_node_id = open_node_id
        self.enabled = enabled


class ForLink:
    def __init__(self, open_node_id):
        self.open_node_id = open_node_id


def find_max_input_index(kwargs):
    max_index = -1
    for key in kwargs:
        if key.startswith("initial_value_"):
            try:
                index = int(key.split("_")[-1])
                max_index = max(max_index, index)
            except ValueError:
                continue
    return max_index


class WhileLoopOpenNode:

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {},
            "optional": DefaultValueWhenKeyMatchedDict(
                {},
                (MakeSmartType("*"),),
                lambda k: (isinstance(k, str) and k.startswith("initial_value_"))
                          or k == "enable",
            ),
            "hidden": {
                "unique_id": "UNIQUE_ID",
            },
        }

    # To pass ComfyUI's Prompt Validation, we need to implement a tuple that can handle out-of-range indices
    RETURN_TYPES = DefaultValueWhenOutofRangeTuple(
        tuple([TYPE_WHILE_LINK]), MakeSmartType("*")
    )
    RETURN_NAMES = DefaultValueWhenOutofRangeTuple(tuple(["reference"]), "*")
    FUNCTION = "while_loop_open"

    CATEGORY = "Power Flow/Flow Control"

    @classmethod
    def IS_CHANGED(cls, unique_id, enable=None, **kwargs):
        return str(uuid.uuid4())

    def while_loop_open(self, unique_id, enable=None, **kwargs):
        max_index = find_max_input_index(kwargs)
        values = []
        if enable:
            for i in range(max_index + 1):
                values.append(kwargs.get(f"initial_value_{i}", None))
        else:
            values = [ExecutionBlocker(None)] * (max_index + 1)
        return tuple([WhileLink(unique_id, enable)] + values)


class WhileLoopCloseNode:

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "open_node_link": (TYPE_WHILE_LINK,),
            },
            "optional": DefaultValueWhenKeyMatchedDict(
                {
                    "condition": ("BOOLEAN", {"lazy": True, "forceInput": True}),
                },
                (MakeSmartType("*"), {"lazy": True}),
                lambda k: isinstance(k, str) and k.startswith("initial_value_"),
            ),
            "hidden": {
                "dynprompt": "DYNPROMPT",
                "unique_id": "UNIQUE_ID",
            },
        }

    RETURN_TYPES = DefaultValueWhenOutofRangeTuple(tuple(), MakeSmartType("*"))
    RETURN_NAMES = DefaultValueWhenOutofRangeTuple(tuple(), "*")

    FUNCTION = "while_loop_close"
    CATEGORY = "Power Flow/Flow Control"

    def check_lazy_status(self, open_node_link, condition, **kwargs):
        if not open_node_link.enabled:
            return []
        if condition is None:
            return ["condition"]
        if condition:
            return list(kwargs.keys())
        return []

    def while_loop_close(
            self,
            open_node_link: WhileLink,
            condition,
            dynprompt=None,
            unique_id=None,
            **kwargs,
    ):
        max_index = find_max_input_index(kwargs)
        open_node_id = open_node_link.open_node_id
        open_node = dynprompt.get_node(open_node_id)
        if open_node_link.enabled and not condition:
            graph = GraphBuilder()
            sub_open_node = graph.node(
                open_node["class_type"],
                open_node_id,
            )
            for k, v in open_node["inputs"].items():
                sub_open_node.set_input(k, v)
            sub_open_node.set_input("enable", True)
            return {
                "result": tuple(
                    sub_open_node.out(i + 1) for i in range(max_index + 1)
                ),  # 0 is open_node_link
                "expand": graph.finalize(),
            }

        contained = search_nodes_between(open_node_id, unique_id, dynprompt)
        contained.add(open_node_id)
        contained.add(unique_id)
        graph = GraphBuilder()
        for node_id in contained:
            original_node = dynprompt.get_node(node_id)
            node = graph.node(
                original_node["class_type"],
                "Recurse" if node_id == unique_id else node_id,
            )
            node.set_override_display_id(node_id)
        for node_id in contained:
            original_node = dynprompt.get_node(node_id)
            node = graph.lookup_node("Recurse" if node_id == unique_id else node_id)
            for k, v in original_node["inputs"].items():
                if is_link(v) and v[0] in contained:
                    parent = graph.lookup_node(v[0])
                    node.set_input(k, parent.out(v[1]))
                else:
                    node.set_input(k, v)
        new_open = graph.lookup_node(open_node_id)
        if open_node_link.enabled:
            for i in range(max_index + 1):
                key = "initial_value_%d" % i
                new_open.set_input(key, kwargs.get(key, None))
        new_open.set_input("enable", True)
        my_clone = graph.lookup_node("Recurse")
        result = map(lambda x: my_clone.out(x), range(max_index + 1))
        return {
            "result": tuple(result),
            "expand": graph.finalize(),
        }


class ForLoopOpenNode:

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "list": (MakeSmartType("*"), {"rawLink": True}),
            },
            "optional": DefaultValueWhenKeyMatchedDict(
                {},
                (MakeSmartType("*"), {"rawLink": True}),
                lambda k: isinstance(k, str) and k.startswith("initial_value_"),
            ),
            "hidden": {
                "unique_id": "UNIQUE_ID",
            },
        }

    RETURN_TYPES = DefaultValueWhenOutofRangeTuple(
        tuple([TYPE_FOR_LINK, MakeSmartType("*"), ]), MakeSmartType("*")
    )
    RETURN_NAMES = DefaultValueWhenOutofRangeTuple(
        tuple(["reference", "item"]), "*"
    )
    FUNCTION = "for_loop_open"

    CATEGORY = "Power Flow/Flow Control"

    @classmethod
    def IS_CHANGED(cls, list, unique_id, **kwargs):
        return str(uuid.uuid4())

    def for_loop_open(self, list, unique_id, **kwargs):
        max_index = find_max_input_index(kwargs)
        return tuple([ForLink(unique_id)] + [ExecutionBlocker(None)] * (max_index + 2))


class ForLoopCloseNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "open_node_link": (TYPE_FOR_LINK,),
            },
            "optional": DefaultValueWhenKeyMatchedDict(
                {},
                (MakeSmartType("*"), {"rawLink": True, "lazy": True}),
                lambda k: isinstance(k, str) and k.startswith("initial_value_"),
            ),
            "hidden": {
                "unique_id": "UNIQUE_ID",
                "dynprompt": "DYNPROMPT",
            },
        }

    RETURN_TYPES = DefaultValueWhenOutofRangeTuple(tuple(), MakeSmartType("*"))
    RETURN_NAMES = DefaultValueWhenOutofRangeTuple(tuple(), "*")
    FUNCTION = "for_loop_close"

    CATEGORY = "Power Flow/Flow Control"

    def check_lazy_status(self, open_node_link, **kwargs):
        return []

    def for_loop_close(self, open_node_link, dynprompt=None, unique_id=None, **kwargs):
        max_index = find_max_input_index(kwargs)
        open_node_id = open_node_link.open_node_id
        open_node = dynprompt.get_node(open_node_id)
        this_node = dynprompt.get_node(unique_id)
        contained = search_nodes_between(open_node_id, unique_id, dynprompt)
        contained.add(open_node_id)
        contained.add(unique_id)
        graph = GraphBuilder()
        new_while_close = None
        new_while_open = None
        new_list_to_iterator = None
        new_iterate_next = None
        for node_id in contained:
            original_node = dynprompt.get_node(node_id)

            if node_id == unique_id:  # Loop close node
                new_while_close = graph.node(
                    "ComfyUI_Power_Flow.WhileLoopClose",
                    "Recurse",
                )
                new_while_close.set_override_display_id(node_id)
            elif node_id == open_node_id:  # Loop open node
                new_while_open = graph.node(
                    "ComfyUI_Power_Flow.WhileLoopOpen",
                    node_id,
                    enable=True,
                )
                new_while_open.set_override_display_id(node_id)
                new_list_to_iterator = graph.node(
                    "ComfyUI_Power_Flow.ListToIterator",
                    "ToIterator",
                )
                new_list_to_iterator.set_override_display_id(node_id)
                new_iterate_next = graph.node(
                    "ComfyUI_Power_Flow.IterateNext",
                    "IterateNext",
                )
                new_iterate_next.set_override_display_id(node_id)
            else:
                node = graph.node(
                    original_node["class_type"],
                    node_id,
                )
                node.set_override_display_id(node_id)
        for node_id in contained:
            if (node_id == open_node_id or node_id == unique_id):
                continue
            original_node = dynprompt.get_node(node_id)
            node = graph.lookup_node("Recurse" if node_id == unique_id else node_id)
            for k, v in original_node["inputs"].items():
                if is_link(v) and v[0] in contained:
                    parent = graph.lookup_node(v[0])
                    if parent.id == new_while_open.id and v[1] == 1:
                        node.set_input(k, new_iterate_next.out(0))
                    else:
                        node.set_input(k, parent.out(v[1]))
                else:
                    node.set_input(k, v)
        new_while_open.set_input("enable", True)
        new_list_to_iterator.set_input("list", open_node["inputs"]["list"])
        new_while_open.set_input("initial_value_0", new_list_to_iterator.out(0))
        for i in range(max_index + 1):
            if f"initial_value_{i}" in open_node["inputs"]:
                new_while_open.set_input(f"initial_value_{i + 1}", open_node["inputs"][f"initial_value_{i}"])
        new_iterate_next.set_input("iterator", new_while_open.out(1))
        for i in range(max_index + 1):
            original_input = this_node["inputs"][f"initial_value_{i}"]
            if not is_link(original_input) or not original_input[0] in contained:
                new_while_close.set_input(f"initial_value_{i + 1}", original_input)
                continue
            new_input_id = graph.lookup_node(original_input[0]).id
            new_while_close.set_input(f"initial_value_{i + 1}", [new_input_id, original_input[1]])
        new_while_close.set_input("condition", new_iterate_next.out(1))
        new_while_close.set_input("initial_value_0", new_iterate_next.out(2))
        new_while_close.set_input("open_node_link", new_while_open.out(0))
        result = tuple(map(lambda x: new_while_close.out(x + 1), range(max_index + 1)))
        return {
            "result": result,
            "expand": graph.finalize(),
        }
