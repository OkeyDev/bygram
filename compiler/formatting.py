import textwrap
from typing import Iterable

from compiler.parser import TlObjectDefinition
from compiler.preprocessor import (
    ProcessedTlArgument,
    PythonType,
    preprocess_arguments,
)
from compiler.utils import class_to_python_name

INDENT = "    "
CLASS_PARENT_NAME = "ObjectBase"

CLASS_TEMPLATE = """
@dataclass
class {name}({parent}):
{docs}

{args}
"""


def generate_class_docs(main_doc: str, args: Iterable[ProcessedTlArgument]):
    assert main_doc
    result = ['"""']

    result.append(main_doc)

    if args:
        result.append("")  # newline

    for arg in args:
        if arg.doc:
            result.append(f":param {arg.name}: {arg.doc}")

    result.append('"""')

    return result


def generate_func_docs(
    main_doc: str, args: Iterable[ProcessedTlArgument], return_type: str
):
    result = generate_class_docs(main_doc, args)
    result.insert(-1, f":return: :class:`{return_type}`")
    return result


def type_to_str(type_: PythonType):
    if type_.subtype:
        return f"{type_.name}[{type_to_str(type_.subtype)}]"
    else:
        return f"{type_.name}"


def args_to_class_string(args: Iterable[ProcessedTlArgument]):
    result = []
    for a in args:
        if a.default == "None":
            s = f'{a.name}: "{type_to_str(a.python_type)} | None" = {a.default}'
        else:
            s = f'{a.name}: "{type_to_str(a.python_type)}" = {a.default}'
        result.append(s)
    return result


def get_class_parent(name: str, related_obj: str | None):
    if related_obj is None or name.lower() == related_obj.lower():
        return CLASS_PARENT_NAME
    return class_to_python_name(related_obj)


def insert_type_arg(real_name: str, args: list[ProcessedTlArgument]):
    arg = ProcessedTlArgument(
        "_type",
        "",
        PythonType("str"),
        f'field(default="{real_name}", init=False, repr=False)',
    )
    args.insert(0, arg)


def create_class_text(obj: TlObjectDefinition, imports: set[str]):
    assert obj.type == "class"

    # Preprocessing
    args = preprocess_arguments(obj.args, imports)
    insert_type_arg(obj.name, args)

    docs = generate_class_docs(obj.doc, args)

    name = class_to_python_name(obj.name)
    parent = get_class_parent(obj.name, obj.related_obj)
    args = "\n".join(args_to_class_string(args))
    args = textwrap.indent(args, INDENT)
    docs = textwrap.indent("\n".join(docs), INDENT)

    return CLASS_TEMPLATE.format(name=name, parent=parent, docs=docs, args=args).strip()


def create_function_text(obj: TlObjectDefinition, imports: set[str]):
    assert obj.type == "function"

    args = preprocess_arguments(obj.args, imports)
    insert_type_arg(obj.name, args)

    return_type = obj.related_obj
    assert return_type
    return_type = class_to_python_name(return_type)

    docs = generate_func_docs(obj.doc, args, return_type)

    name = class_to_python_name(obj.name)
    args = "\n".join(args_to_class_string(args))
    args = textwrap.indent(args, INDENT)
    docs = textwrap.indent("\n".join(docs), INDENT)

    parent = f"Function[{return_type}]"

    return CLASS_TEMPLATE.format(name=name, parent=parent, docs=docs, args=args)
