from typing import TextIO

from compiler.formatting import create_class_text, create_function_text
from compiler.parser import TdLibTlParser

BASE_TEXT = """
from dataclasses import dataclass, field
from .base import ObjectBase, Function, Update
""".strip()


def process_file(reader: TextIO, writer: TextIO):
    writer.write(BASE_TEXT + "\n\n")
    parser = TdLibTlParser(reader)

    count = 0
    while definition := parser.parse_definition():
        if definition.name == "Update":
            continue
        if definition.type == "class":
            text = create_class_text(definition, set())
        else:
            text = create_function_text(definition, set())
        writer.write(text + "\n\n")
        count += 1

    return count
