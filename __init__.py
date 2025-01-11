from .basic_types import (
    IntNode,
    FloatNode,
    StringNode,
    StringMultilineNode,
    BooleanNode,
)
from .collections import (
    ListToIteratorNode,
    IterateNextNode,
    StringListNode,
    IntListNode,
    FloatListNode,
    RangeNode,
    EmptyListNode,
    AppendToListNode,
    ToComfyWorkflowListNode,
)
from .debug_nodes import DisplayAnyNoOutputNode, DisplayAnyNode, ConsolePrintNode
from .function_control import (
    FunctionDefStartNode,
    FunctionDefEndNode,
    ExecuteFunctionNode,
)
from .logic import (
    NotNode,
    LogicOperationNode,
    CompareNumberNode,
    CompareStringNode,
)
from .loop_control import (
    WhileLoopOpenNode,
    WhileLoopCloseNode,
    ForLoopOpenNode,
    ForLoopCloseNode,
)
from .no_output import SaveImageNoOutput, PreviewImageNoOutput
from .script_control import (
    ReceiveTaskResultNode,
    WaitFunctionTaskNode,
    RunPythonScriptNode,
    PythonEvalNode,
)

NAME_PREFIX = "ComfyUI_Power_Flow."

NODE_CLASS_MAPPINGS = {
    f"{NAME_PREFIX}Int": IntNode,
    f"{NAME_PREFIX}Float": FloatNode,
    f"{NAME_PREFIX}String": StringNode,
    f"{NAME_PREFIX}StringMultiline": StringMultilineNode,
    f"{NAME_PREFIX}Boolean": BooleanNode,
    f"{NAME_PREFIX}WhileLoopOpen": WhileLoopOpenNode,
    f"{NAME_PREFIX}WhileLoopClose": WhileLoopCloseNode,
    f"{NAME_PREFIX}ForLoopOpen": ForLoopOpenNode,
    f"{NAME_PREFIX}ForLoopClose": ForLoopCloseNode,
    f"{NAME_PREFIX}FunctionDefStart": FunctionDefStartNode,
    f"{NAME_PREFIX}FunctionDefEnd": FunctionDefEndNode,
    f"{NAME_PREFIX}ExecuteFunction": ExecuteFunctionNode,
    f"{NAME_PREFIX}ListToIterator": ListToIteratorNode,
    f"{NAME_PREFIX}IterateNext": IterateNextNode,
    f"{NAME_PREFIX}StringList": StringListNode,
    f"{NAME_PREFIX}IntList": IntListNode,
    f"{NAME_PREFIX}FloatList": FloatListNode,
    f"{NAME_PREFIX}Range": RangeNode,
    f"{NAME_PREFIX}EmptyList": EmptyListNode,
    f"{NAME_PREFIX}NotNode": NotNode,
    f"{NAME_PREFIX}LogicOperation": LogicOperationNode,
    f"{NAME_PREFIX}CompareNumber": CompareNumberNode,
    f"{NAME_PREFIX}CompareString": CompareStringNode,
    f"{NAME_PREFIX}AppendToList": AppendToListNode,
    f"{NAME_PREFIX}ToComfyWorkflowList": ToComfyWorkflowListNode,
    f"{NAME_PREFIX}ReceiveTaskResult": ReceiveTaskResultNode,
    f"{NAME_PREFIX}WaitFunctionTask": WaitFunctionTaskNode,
    f"{NAME_PREFIX}RunPythonScript": RunPythonScriptNode,
    f"{NAME_PREFIX}DisplayAnyNoOutput": DisplayAnyNoOutputNode,
    f"{NAME_PREFIX}DisplayAny": DisplayAnyNode,
    f"{NAME_PREFIX}ConsolePrint": ConsolePrintNode,
    f"{NAME_PREFIX}PythonEval": PythonEvalNode,
    f"{NAME_PREFIX}SaveImageNoOutput": SaveImageNoOutput,
    f"{NAME_PREFIX}PreviewImageNoOutput": PreviewImageNoOutput,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    f"{NAME_PREFIX}Int": "Int",
    f"{NAME_PREFIX}Float": "Float",
    f"{NAME_PREFIX}String": "String",
    f"{NAME_PREFIX}StringMultiline": "String(Multiline)",
    f"{NAME_PREFIX}Boolean": "Boolean",
    f"{NAME_PREFIX}WhileLoopOpen": "While Loop Open",
    f"{NAME_PREFIX}WhileLoopClose": "While Loop Close",
    f"{NAME_PREFIX}ForLoopOpen": "For Loop Open",
    f"{NAME_PREFIX}ForLoopClose": "For Loop Close",
    f"{NAME_PREFIX}FunctionDefStart": "Function Definition Start",
    f"{NAME_PREFIX}FunctionDefEnd": "Function Definition End",
    f"{NAME_PREFIX}ExecuteFunction": "Execute Function",
    f"{NAME_PREFIX}ListToIterator": "List To Iterator",
    f"{NAME_PREFIX}IterateNext": "Iterate Next",
    f"{NAME_PREFIX}StringList": "String List",
    f"{NAME_PREFIX}IntList": "Int List",
    f"{NAME_PREFIX}FloatList": "Float List",
    f"{NAME_PREFIX}Range": "Range",
    f"{NAME_PREFIX}EmptyList": "Empty List",
    f"{NAME_PREFIX}NotNode": "Boolean Not",
    f"{NAME_PREFIX}LogicOperation": "Logic Operation",
    f"{NAME_PREFIX}CompareNumber": "Compare Number",
    f"{NAME_PREFIX}CompareString": "Compare String",
    f"{NAME_PREFIX}AppendToList": "Append To List",
    f"{NAME_PREFIX}ToComfyWorkflowList": "To Comfy List",
    f"{NAME_PREFIX}ReceiveTaskResult": "(Don't use) Receive Task Result",
    f"{NAME_PREFIX}WaitFunctionTask": "(Don't use) Wait Function Task",
    f"{NAME_PREFIX}RunPythonScript": "Run Python Script",
    f"{NAME_PREFIX}DisplayAnyNoOutput": "Display Any No Output",
    f"{NAME_PREFIX}DisplayAny": "Display Any",
    f"{NAME_PREFIX}ConsolePrint": "Print to Console",
    f"{NAME_PREFIX}PythonEval": "Python Eval",
    f"{NAME_PREFIX}SaveImageNoOutput": "Save Image No Output",
    f"{NAME_PREFIX}PreviewImageNoOutput": "Preview Image No Output",
}

WEB_DIRECTORY = "./js"

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
