from queue import Queue
from threading import Thread

from collections.abc import Iterable
from comfy_execution.graph_utils import GraphBuilder

from .consts import TYPE_NON_USER_TYPE
from .function_control import FunctionControl
from .graph_utils import find_max_output_index
from .utils import MakeSmartType, DefaultValueWhenOutofRangeTuple, DefaultValueWhenKeyMatchedDict


def find_max_input_index(prefix, arg_dict):
    max_index = -1
    for key in arg_dict:
        if key.startswith(prefix):
            try:
                index = int(key[len(prefix):])
                max_index = max(max_index, index)
            except ValueError:
                continue
    return max_index


class RunFunctionTask:
    def __init__(self, function_definition: FunctionControl, arg_list):
        self.function_definition = function_definition
        self.arg_list = arg_list


class RunFunctionResult:
    def __init__(self, output_tuple):
        self.output_tuple = output_tuple


class ReturnResultTask:
    def __init__(self, output_tuple, exception=None):
        self.output_tuple = output_tuple
        self.exception = exception


class WaitFunctionTaskNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "output_count": ("INT",),
                "task_queue": (TYPE_NON_USER_TYPE,),
                "result_queue": (TYPE_NON_USER_TYPE,),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
                "dynprompt": "DYNPROMPT",
            },
        }

    RETURN_TYPES = DefaultValueWhenOutofRangeTuple(tuple(), "*")
    RETURN_NAMES = DefaultValueWhenOutofRangeTuple(tuple(), "*")

    FUNCTION = "wait_function_task"
    CATEGORY = "Power Flow/Don't Use"

    def wait_function_task(self, output_count, task_queue: Queue, result_queue: Queue, unique_id, dynprompt):
        task = task_queue.get()
        if isinstance(task, ReturnResultTask):
            if task.exception is not None:
                raise task.exception
            return task.output_tuple
        if not isinstance(task, RunFunctionTask):
            raise ValueError(f"Unknown task type: {type(task)}")
        graph = GraphBuilder()
        execute_function_node = graph.node(
            "ComfyUI_Power_Flow.ExecuteFunction",
        )
        function_definition = task.function_definition
        execute_function_node.set_input("function_definition", function_definition)
        for i, arg in enumerate(task.arg_list):
            execute_function_node.set_input(f"input{i}", arg)
        end_node = dynprompt.get_node(function_definition.end_node_id)
        max_input_index = find_max_input_index("output", end_node["inputs"])

        receive_result = graph.node(
            "ComfyUI_Power_Flow.ReceiveTaskResult",
        )
        receive_result.set_input("task_queue", task_queue)
        receive_result.set_input("result_queue", result_queue)
        receive_result.set_input("output_count", output_count)
        for i in range(max_input_index + 1):
            receive_result.set_input(f"output{i}", execute_function_node.out(i))
        return {
            "result": tuple([receive_result.out(i) for i in range(output_count)]),
            "expand": graph.finalize(),
        }


class ReceiveTaskResultNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "output_count": ("INT",),
                "task_queue": (TYPE_NON_USER_TYPE,),
                "result_queue": (TYPE_NON_USER_TYPE,),
            },
            "optional": DefaultValueWhenKeyMatchedDict(
                {},
                ("*",),
                lambda k: isinstance(k, str) and k.startswith("output"),
            ),
            "hidden": {
                "unique_id": "UNIQUE_ID",
            },
        }

    RETURN_TYPES = DefaultValueWhenOutofRangeTuple(tuple(), "*")
    RETURN_NAMES = DefaultValueWhenOutofRangeTuple(tuple(), "*")

    FUNCTION = "receive_task_result"
    CATEGORY = "Power Flow/Don't Use"

    def receive_task_result(self, output_count, task_queue: Queue, result_queue: Queue, unique_id, **kwargs):
        max_index = find_max_input_index("output", kwargs)
        output = [kwargs.get(f"output{i}", None) for i in range(max_index + 1)]
        result_queue.put(RunFunctionResult(output))
        graph = GraphBuilder()
        node = graph.node(
            "ComfyUI_Power_Flow.WaitFunctionTask",
        )
        node.set_input("task_queue", task_queue)
        node.set_input("result_queue", result_queue)
        node.set_input("output_count", output_count)
        return {
            "result": tuple([node.out(i) for i in range(output_count)]),
            "expand": graph.finalize(),
        }


def process_function_input(input_dict, task_queue, result_queue):
    result = {}
    for key, value in input_dict.items():
        if isinstance(value, FunctionControl):
            def run_function(*args, function_definition=value):
                task_queue.put(RunFunctionTask(function_definition, args))
                result: RunFunctionResult = result_queue.get()
                return result.output_tuple

            result[key] = run_function
        else:
            result[key] = value
    return result


class RunPythonScriptNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "script": ("STRING", {"multiline": True}),
                "output_variable_name": ("STRING", {"default": "result"}),
            },
            "optional": DefaultValueWhenKeyMatchedDict(
                {},
                ("*",),
                lambda k: isinstance(k, str) and k.startswith("input"),
            ),
            "hidden": {
                "unique_id": "UNIQUE_ID",
                "dynprompt": "DYNPROMPT",
            },
        }

    RETURN_TYPES = DefaultValueWhenOutofRangeTuple(tuple(), "*")
    RETURN_NAMES = DefaultValueWhenOutofRangeTuple(tuple(), "*")

    FUNCTION = "run_python_script"
    CATEGORY = "Power Flow/Script Control"

    def run_python_script(self, script, output_variable_name, unique_id, dynprompt, **kwargs):
        task_queue = Queue()
        result_queue = Queue()
        graph = GraphBuilder()
        wait_task_node = graph.node(
            "ComfyUI_Power_Flow.WaitFunctionTask",
        )
        max_output_index = find_max_output_index(unique_id, dynprompt)
        wait_task_node.set_input("task_queue", task_queue)
        wait_task_node.set_input("result_queue", result_queue)
        wait_task_node.set_input("output_count", max_output_index + 1)

        def run_script():
            locals_dict = {}
            input_dict = process_function_input(kwargs, task_queue, result_queue)
            try:
                exec(script, input_dict, locals_dict)
            except SystemExit as e:
                pass
            except Exception as e:
                task_queue.put(ReturnResultTask(None, e))
                return
            result = locals_dict.get(output_variable_name, None)
            if not isinstance(result, Iterable):
                result = (result,)
            task_queue.put(ReturnResultTask(result))

        thread = Thread(target=run_script)
        thread.start()

        return {
            "result": tuple([wait_task_node.out(i) for i in range(max_output_index + 1)]),
            "expand": graph.finalize(),
        }


class PythonEvalNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {"script": ("STRING",)},
            "optional": DefaultValueWhenKeyMatchedDict(
                {},
                ("*",),
                lambda k: isinstance(k, str) and k.startswith("i"),
            ),
        }

    RETURN_TYPES = (MakeSmartType("*"),)
    RETURN_NAMES = ("result",)

    FUNCTION = "python_eval"
    CATEGORY = "Power Flow/Script Control"

    def python_eval(self, script, **kwargs):
        locals_dict = {}
        try:
            result = eval(script, kwargs, locals_dict)
        except SystemExit as e:
            raise Exception("You should not use exit() in the eval script")
        return (result,)
