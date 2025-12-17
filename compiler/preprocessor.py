from dataclasses import dataclass
from typing import Iterable

from compiler.parser import TlArgument
from compiler.utils import class_to_python_name

INVALID_ARGUMENT_NAMES = {"list"}


@dataclass
class PythonType:
    name: str
    subtype: "PythonType | None" = None


@dataclass
class ProcessedTlArgument:
    name: str
    doc: str
    python_type: PythonType
    default: str


def is_valid_name(name: str) -> bool:
    return name.isidentifier()


def get_python_type(type_: str, imports: set[str]) -> PythonType:
    # Predefined types
    if type_.startswith("int"):
        return PythonType("int")

    PREDEFINED_TYPES = {
        "Bool": "bool",
        "bytes": "bytes",
        "double": "float",
        "string": "str",
    }
    if type_ in PREDEFINED_TYPES:
        return PythonType(PREDEFINED_TYPES[type_])

    if type_.startswith("vector"):
        # vector<int32>
        type_ = type_.removeprefix("vector<").removesuffix(">")
        return PythonType("list", get_python_type(type_, imports))

    # Any other class
    type_ = class_to_python_name(type_)
    imports.add(type_)
    return PythonType(type_)


def get_default_value(python_type: PythonType) -> str:
    # TODO: Add support for doc based default value
    BUILTIN_DEFAULT_VALUES = {
        "float": "0",
        "int": "0",
        "str": '""',
        "bool": "False",
        "bytes": 'b""',
    }
    return BUILTIN_DEFAULT_VALUES.get(python_type.name, "None")


def fix_unavailable_name_if_needed(name: str):
    if name in INVALID_ARGUMENT_NAMES:
        return f"{name}_"
    return name


def preprocess_arguments(
    args: Iterable[TlArgument], imports: set[str]
) -> list[ProcessedTlArgument]:
    result = []
    for arg in args:
        type_ = get_python_type(arg.type, imports)
        default = get_default_value(type_)
        if not is_valid_name(arg.name):
            raise ValueError(f"Invalid arg name: {arg}")

        name = fix_unavailable_name_if_needed(arg.name)
        result.append(
            ProcessedTlArgument(
                name=name, doc=arg.doc, python_type=type_, default=default
            )
        )

    return result
