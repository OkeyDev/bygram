from dataclasses import dataclass
from typing import Any, Generic, TypeVar

from bygram.types.base import ObjectBase

T = TypeVar("T", bound=ObjectBase)


@dataclass
class DeserializedObject(Generic[T]):
    obj: T
    client_id: int | None = None
    extra: Any | None = None
