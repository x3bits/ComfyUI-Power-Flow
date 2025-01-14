from .utils import MakeSmartType

class IfNode:

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "condition": ("BOOLEAN",),
            },
            "optional": {
                "if_true": (MakeSmartType("*"), {"lazy": True}),
                "if_false": (MakeSmartType("*"), {"lazy": True}),
            },
        }

    RETURN_TYPES = (MakeSmartType("*"),)
    RETURN_NAMES = ("value",)

    FUNCTION = "execute"
    CATEGORY = "Power Flow/Flow Control"

    def check_lazy_status(self, condition, if_true, if_false):
        if condition:
            return ["if_true"]
        return ["if_false"]
    
    def execute(self, condition, if_true, if_false):
        if condition:
            return (if_true,)
        return (if_false,)