class NotNode:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {"input": ("BOOLEAN",)}}

    RETURN_TYPES = ("BOOLEAN",)
    RETURN_NAMES = ("output",)
    FUNCTION = "not_value"

    CATEGORY = "Power Flow/Logic"

    def not_value(self, input):
        return (not input,)


class LogicOperationNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "a": ("BOOLEAN", {"forceInput": True}),
                "b": ("BOOLEAN", {"forceInput": True}),
                "operation": (["and", "or", "xor"],),
            },
        }

    RETURN_TYPES = ("BOOLEAN",)
    RETURN_NAMES = ("output",)
    FUNCTION = "logic_operation"

    CATEGORY = "Power Flow/Logic"

    def logic_operation(self, a, b, operation):
        if operation == "and":
            return (a and b,)
        elif operation == "or":
            return (a or b,)
        elif operation == "xor":
            return (a != b,)
        else:
            raise ValueError(f"Invalid operation: {operation}")


class CompareNumberNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "a": ("INT,FLOAT",),
                "b": ("INT,FLOAT",),
                "operation": (["a == b", "a != b", "a > b", "a >= b", "a < b", "a <= b"],),
            },
        }

    @classmethod
    def VALIDATE_INPUTS(cls, input_types):
        return True

    RETURN_TYPES = ("BOOLEAN",)
    RETURN_NAMES = ("output",)
    FUNCTION = "compare_number"

    CATEGORY = "Power Flow/Logic"

    def compare_number(self, a, b, operation):
        if operation == "a == b":
            return (a == b,)
        elif operation == "a != b":
            return (a != b,)
        elif operation == "a > b":
            return (a > b,)
        elif operation == "a >= b":
            return (a >= b,)
        elif operation == "a < b":
            return (a < b,)
        elif operation == "a <= b":
            return (a <= b,)
        else:
            raise ValueError(f"Invalid operation: {operation}")


class CompareStringNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "a": ("STRING",),
                "b": ("STRING",),
                "operation": (["a == b", "a != b", "a > b", "a >= b", "a < b", "a <= b"],),
            },
        }

    RETURN_TYPES = ("BOOLEAN",)
    RETURN_NAMES = ("output",)
    FUNCTION = "compare_string"

    CATEGORY = "Power Flow/Logic"

    def compare_string(self, a, b, operation):
        if operation == "a == b":
            return (a == b,)
        elif operation == "a != b":
            return (a != b,)
        elif operation == "a > b":
            return (a > b,)
        elif operation == "a >= b":
            return (a >= b,)
        elif operation == "a < b":
            return (a < b,)
        elif operation == "a <= b":
            return (a <= b,)
        else:
            raise ValueError(f"Invalid operation: {operation}")
