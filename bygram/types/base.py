from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass
class TlObject:
    pass


@dataclass
class ObjectBase(TlObject):
    pass


@dataclass
class Update(ObjectBase):
    pass


@dataclass
class Function(ObjectBase, Generic[T]):
    pass
