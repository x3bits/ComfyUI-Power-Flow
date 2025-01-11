import uuid

from .consts import TYPE_ITERATOR, TYPE_LIST
from .utils import MakeSmartType

_to_list = list


class ListToIteratorNode:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {"list": (TYPE_LIST,)}}

    RETURN_TYPES = (TYPE_ITERATOR,)
    RETURN_NAMES = ("iterator",)
    FUNCTION = "list_to_iterator"

    CATEGORY = "Power Flow/Collections"

    @classmethod
    def IS_CHANGED(cls, list):
        return str(uuid.uuid4())

    def list_to_iterator(self, list):
        return (iter(list),)


class IterateNextNode:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {"iterator": (TYPE_ITERATOR,)}}

    RETURN_TYPES = ("*", "BOOLEAN", TYPE_ITERATOR)
    RETURN_NAMES = ("item", "has_next", "iterator")
    FUNCTION = "iterator_next"

    CATEGORY = "Power Flow/Collections"

    @classmethod
    def IS_CHANGED(cls, iterator):
        return str(uuid.uuid4())

    def iterator_next(self, iterator):
        try:
            item = next(iterator)
            return (item, True, iterator)
        except StopIteration:
            return (None, False, iterator)


class StringListNode:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "list": ("STRING", {"default": "first\nsecond\nthird", "multiline": True}),
            "new_line_as_separator": ("BOOLEAN", {"default": True}),
            "separator": ("STRING", {"default": ",", "multiline": False}),
        }}

    RETURN_TYPES = (TYPE_LIST,)
    RETURN_NAMES = ("list",)
    FUNCTION = "string_list"

    CATEGORY = "Power Flow/Collections"

    def string_list(self, list, new_line_as_separator, separator):
        if list == "":
            return ([],)
        if new_line_as_separator:
            list = list.split("\n")
        else:
            list = list.split(separator)
        return (list,)


class IntListNode:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {"list": ("STRING", {"default": "1,2,3,4,5"})}}

    RETURN_TYPES = (TYPE_LIST,)
    RETURN_NAMES = ("list",)
    FUNCTION = "int_list"

    CATEGORY = "Power Flow/Collections"

    def int_list(self, list):
        if list == "":
            return ([],)
        return ([int(x.strip()) for x in list.split(",")],)


class FloatListNode:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {"list": ("STRING", {"default": "0.1,0.2,0.3,0.4,0.5"})}}

    RETURN_TYPES = (TYPE_LIST,)
    RETURN_NAMES = ("list",)
    FUNCTION = "float_list"

    CATEGORY = "Power Flow/Collections"

    def float_list(self, list):
        if list == "":
            return ([],)
        return ([float(x.strip()) for x in list.split(",")],)


class RangeNode:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "start": ("INT", {"default": 0}),
            "end": ("INT", {"default": 5}),
            "step": ("INT", {"default": 1})
        }}

    RETURN_TYPES = (TYPE_LIST,)
    RETURN_NAMES = ("list",)
    FUNCTION = "range"

    CATEGORY = "Power Flow/Collections"

    def range(self, start, end, step):
        return (range(start, end, step),)


class EmptyListNode:
    @classmethod
    def INPUT_TYPES(s):
        return {}

    RETURN_TYPES = (TYPE_LIST,)
    RETURN_NAMES = ("list",)
    FUNCTION = "empty_list"

    CATEGORY = "Power Flow/Collections"

    def empty_list(self):
        return ([],)


class AppendToListNode:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {"list": (TYPE_LIST,), "item": (MakeSmartType("*"),)}}

    RETURN_TYPES = (TYPE_LIST,)
    RETURN_NAMES = ("list",)
    FUNCTION = "append_to_list"

    CATEGORY = "Power Flow/Collections"

    def append_to_list(self, list, item):
        return (_to_list(list) + [item],)


class ToComfyWorkflowListNode:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {"list": (TYPE_LIST,)}}

    RETURN_TYPES = (MakeSmartType("*"),)
    RETURN_NAMES = ("list",)
    FUNCTION = "to_comfy_workflow_list"
    OUTPUT_IS_LIST = (True,)
    CATEGORY = "Power Flow/Collections"

    def to_comfy_workflow_list(self, list):
        return (list,)
