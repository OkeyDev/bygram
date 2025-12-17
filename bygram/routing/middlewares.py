import abc
from typing import Any, Awaitable, Callable

from bygram.client_manager import ClientManager
from bygram.types.base import Update


class MiddlewareBase(abc.ABC):
    @abc.abstractmethod
    async def __call__(
        self,
        update: Update,
        data: dict,
        next_handler: Callable[[Update, dict], Awaitable[Any]],
    ) -> Any:
        pass


class FindClientMiddleware(MiddlewareBase):
    def __init__(self, client_manager: ClientManager) -> None:
        self._client_manager = client_manager

    async def __call__(
        self,
        update: Update,
        data: dict,
        next_handler: Callable[[Update, dict], Awaitable[Any]],
    ) -> Any:
        data["client"] = self._client_manager.get_client_by_id(data["client_id"])
        return await next_handler(update, data)
