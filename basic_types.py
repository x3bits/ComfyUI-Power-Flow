class IntNode:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {"value": ("INT",)}}

    RETURN_TYPES = ("INT",)
    RETURN_NAMES = ("value",)
    FUNCTION = "int_value"

    CATEGORY = "Power Flow/Basic Types"

    def int_value(self, value):
        return (value,)


class FloatNode:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {"value": ("FLOAT",)}}

    RETURN_TYPES = ("FLOAT",)
    RETURN_NAMES = ("value",)
    FUNCTION = "float_value"

    CATEGORY = "Power Flow/Basic Types"

    def float_value(self, value):
        return (value,)


class StringNode:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {"value": ("STRING",)}}

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("value",)
    FUNCTION = "string_value"

    CATEGORY = "Power Flow/Basic Types"

    def string_value(self, value):
        return (value,)


class StringMultilineNode:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {"value": ("STRING", {"multiline": True})}}

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("value",)
    FUNCTION = "string_multiline_value"

    CATEGORY = "Power Flow/Basic Types"

    def string_multiline_value(self, value):
        return (value,)


class BooleanNode:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {"value": ("BOOLEAN",)}}

    RETURN_TYPES = ("BOOLEAN",)
    RETURN_NAMES = ("value",)
    FUNCTION = "boolean_value"

    CATEGORY = "Power Flow/Basic Types"

    def boolean_value(self, value):
        return (value,)
