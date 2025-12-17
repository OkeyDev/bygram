import re
from dataclasses import dataclass
from typing import Literal, TextIO

EXTRACT_COMMENT_DEF_RE = re.compile(r"@(\w+)\s+([^@]+)")
SKIP_DEFINITIONS = {
    "double",
    "string",
    "int32",
    "int53",
    "int64",
    "bytes",
    "boolFalse",
    "boolTrue",
    "vector",
}


@dataclass
class TlArgument:
    name: str
    doc: str
    type: str


TL_OBJECT_TYPE = Literal["class", "function"]


@dataclass(frozen=True)
class TlObjectDefinition:
    type: TL_OBJECT_TYPE
    name: str
    doc: str
    args: list[TlArgument]
    related_obj: str | None


@dataclass
class _ParsedObject:
    name: str
    related: str | None
    args: dict[str, str]
    descriptions: dict[str, str]


class TdLibTlParser:
    def __init__(self, source: TextIO) -> None:
        self.source = source
        self._is_def_skipped = False
        self._saved_line: str | None = None
        self._object_type: TL_OBJECT_TYPE = "class"

    def _read_line(self, skip_whitespaces: bool = True) -> str:
        if self._saved_line:
            line = self._saved_line
            self._saved_line = None
            return line

        if skip_whitespaces:
            while (line := self.source.readline()) == "\n":
                pass
            line = line.strip()
        else:
            line = self.source.readline()

        return line

    def _return_line(self, line: str):
        assert self._saved_line is None
        self._saved_line = line

    def _skip_values_definition(self):
        if self._is_def_skipped:
            return
        while True:
            line = self._read_line()
            start_word, _, _ = line.partition(" ")
            if start_word not in SKIP_DEFINITIONS:
                self._return_line(line)
                break

        self._is_def_skipped = True

    def _read_comments(self):
        results = []
        while not (line := self._read_line()).startswith("//"):
            pass
        self._return_line(line)

        while (line := self._read_line(skip_whitespaces=False)).startswith("//"):
            line = line.removeprefix("//")
            if line.startswith("-"):  # Continue of the previous line
                line = line.removeprefix("-")
                results[-1] = f"{results[-1]} {line}"
            else:
                results.append(line)
        self._return_line(line)
        return " ".join(results)

    def _parse_comments(self) -> dict[str, str]:
        comments = self._read_comments()
        if not comments:
            return {}

        matches = EXTRACT_COMMENT_DEF_RE.findall(comments)
        return {key: value.strip() for key, value in matches}

    def _create_object(self, raw: _ParsedObject):
        arguments = []
        for name, type_ in raw.args.items():
            doc = raw.descriptions.get(name, "")
            arguments.append(TlArgument(name, doc, type_))
        doc = raw.descriptions.get("description", "")
        return TlObjectDefinition(
            self._object_type, raw.name, doc, arguments, raw.related
        )

    def _read_definition(self):
        line = self._read_line()
        line = line.replace(" = ", " ")

        name, *args_raw, related = line.split()
        args = {}
        for arg in args_raw:
            k, v = arg.split(":")
            args[k] = v

        return name, args, related.removesuffix(";")

    def _check_for_functions(self):
        line = self._read_line()
        if line == "---functions---":
            self._object_type = "function"
        else:
            self._return_line(line)

    def _is_eof(self):
        if (line := self._read_line()) == "":
            return True
        self._return_line(line)
        return False

    def parse_definition(self) -> TlObjectDefinition | None:
        if self._is_eof():
            return None

        self._skip_values_definition()
        self._check_for_functions()
        descriptions = self._parse_comments()
        if "class" in descriptions:
            # Inline class creation
            obj = _ParsedObject(
                name=descriptions.pop("class"),
                related=None,
                args={},
                descriptions=descriptions,
            )
        else:
            name, args, related = self._read_definition()
            obj = _ParsedObject(name, related, args, descriptions)

        return self._create_object(obj)
