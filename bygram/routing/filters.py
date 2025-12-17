import abc
from typing import Generic, TypeVar

from bygram.types.base import Update

T = TypeVar("T", bound=Update)


class FilterBase(Generic[T], abc.ABC):
    @abc.abstractmethod
    async def __call__(self, event: Update, data: dict) -> bool | dict:
        pass
