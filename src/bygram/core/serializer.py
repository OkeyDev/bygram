import base64
import importlib
import json
from dataclasses import asdict
from typing import Any, cast

from bygram.core.types import DeserializedObject
from bygram.core.wrapper import TdLibWrapper
from bygram.types.base import Function, ObjectBase, T

__all__ = ["serialize_object", "deserialize_object"]

_TYPES_IMPORT_PATH = "bygram.types.raw"


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, bytes):
            s = base64.b64encode(o)
            return s.decode()
        if isinstance(o, dict) and o.get("_type"):
            o["@type"] = o.pop("_type")
            return o

        return super().default(o)


def serialize_object(obj: ObjectBase, extra: Any | None = None) -> bytes:
    data = asdict(obj)
    if extra:
        data["@extra"] = extra
    json_str = json.dumps(data, cls=CustomJSONEncoder)
    json_str = json_str.replace('"_type"', '"@type"')
    return json_str.encode()


def _convert_type_to_pythonic(t: str):
    return t[0].upper() + t[1:]


def _find_class_by_type(t: str):
    t = _convert_type_to_pythonic(t)

    module = importlib.import_module(_TYPES_IMPORT_PATH)
    current_cls = getattr(module, t, None)
    if current_cls is None:
        raise RuntimeError(
            f"Can't find type {t}. Please ensure your tdlib version is compatible with library version"
        )
    return current_cls


def deserialize_object(obj: bytes) -> DeserializedObject:
    client_id = None
    extra = None

    def object_hook(d: dict):
        nonlocal client_id
        nonlocal extra

        client_id = d.pop("@client_id", None)
        extra = d.pop("@extra", None)

        type_ = d.pop("@type", None)
        if "list" in d:
            d["list_"] = d.pop("list")
        if type_:
            return _find_class_by_type(type_)(**d)

        raise ValueError(f"Invalid object: {d}")

    deserialized = json.loads(obj, object_hook=object_hook)
    return DeserializedObject(deserialized, client_id, extra)


class SerializedWrapper:
    def __init__(self, wrapper: TdLibWrapper) -> None:
        self._wrapper = wrapper

    def create_client(self) -> int:
        return self._wrapper.create_client()

    def send(self, client_id: int, func: Function, extra: Any | None = None):
        serialized = serialize_object(func, extra)
        self._wrapper.send(client_id, serialized)

    def receive(self, timeout: float) -> DeserializedObject | None:
        raw = self._wrapper.receive(timeout)
        if raw:
            return deserialize_object(raw)
        else:
            return None

    def execute(self, func: Function[T]) -> T:
        serialized = serialize_object(func)
        response = self._wrapper.execute(serialized)
        deserialized = deserialize_object(response)
        return cast(T, deserialized.obj)
