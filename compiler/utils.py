# https://stackoverflow.com/questions/1175208/elegant-python-function-to-convert-camelcase-to-snake-case
import re

CAMEL_TO_SNAKE_REGEX = re.compile(r"(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])")


def class_to_python_name(name: str):
    return name[0].upper() + name[1:]


def func_to_python_name(name: str):
    return CAMEL_TO_SNAKE_REGEX.sub("_", name).lower()
