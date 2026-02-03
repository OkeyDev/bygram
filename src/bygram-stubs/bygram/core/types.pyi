from bygram.types.base import ObjectBase as ObjectBase
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

T = TypeVar('T', bound=ObjectBase)

@dataclass
class DeserializedObject(Generic[T]):
    obj: T
    client_id: int | None = ...
    extra: Any | None = ...
