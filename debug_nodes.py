import json

from .utils import MakeSmartType


class DisplayAnyNoOutputNode:

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "value": (("*", {})),
                "mode": (["raw value", "json", "tensor shape"],),
            },
        }

    @classmethod
    def VALIDATE_INPUTS(s, input_types):
        return True

    RETURN_TYPES = (
        MakeSmartType("*"),
        "STRING",
    )
    RETURN_NAMES = (
        "value",
        "text",
    )
    FUNCTION = "to_string"
    CATEGORY = "Power Flow/Utilities"

    def to_string(self, value, mode):
        def _value_to_string(value, mode):
            if mode == "tensor shape":
                text = []

                def tensorShape(tensor):
                    if isinstance(tensor, dict):
                        for k in tensor:
                            tensorShape(tensor[k])
                    elif isinstance(tensor, list):
                        for i in range(len(tensor)):
                            tensorShape(tensor[i])
                    elif hasattr(tensor, "shape"):
                        text.append(list(tensor.shape))

                tensorShape(value)
                return text
            elif mode == "json":
                return json.dumps(value, indent=4)
            else:
                return str(value)

        text = _value_to_string(value, mode)
        return {
            "ui": {"text": text},
            "result": (
                value,
                text,
            ),
        }


class DisplayAnyNode(DisplayAnyNoOutputNode):
    OUTPUT_NODE = True


_ANSI_COLORS = {
    "default": "0",
    "black": "30",
    "red": "31",
    "green": "32",
    "yellow": "33",
    "blue": "34",
    "magenta": "35",
    "cyan": "36",
    "white": "37",
    "dark gray": "90",
    "bright red": "91",
    "bright green": "92",
    "bright yellow": "93",
    "bright blue": "94",
    "bright magenta": "95",
    "bright cyan": "96",
    "bright white": "97",
}


class ConsolePrintNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "value": ("*",),
            },
            "optional": {
                "prefix": ("STRING", {"multiline": False, "default": "Value:"}),
                "color": (list(_ANSI_COLORS.keys()), {"default": "default"}),
            },
        }

    @classmethod
    def VALIDATE_INPUTS(s, input_types):
        return True

    RETURN_TYPES = (MakeSmartType("*"),)
    RETURN_NAMES = ("value",)
    FUNCTION = "print_to_console"
    CATEGORY = "Power Flow/Utilities"

    def print_to_console(self, value, prefix, color):
        if color == "default":
            print(f"{prefix} {value}")
        else:
            print(f"\033[{_ANSI_COLORS[color]}m{prefix} {value}\033[0m")
        return (value,)
