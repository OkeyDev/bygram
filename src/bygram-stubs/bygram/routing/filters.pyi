import abc
from bygram.types.base import Update as Update
from typing import Generic, TypeVar

T = TypeVar('T', bound=Update)

class FilterBase(abc.ABC, Generic[T], metaclass=abc.ABCMeta):
    @abc.abstractmethod
    async def __call__(self, event: Update, data: dict) -> bool | dict: ...
