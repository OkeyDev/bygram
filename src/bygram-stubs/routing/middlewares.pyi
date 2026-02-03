import abc
from bygram.client_manager import ClientManager as ClientManager
from bygram.types.base import Update as Update
from bygram.types.raw import UpdateAuthorizationState as UpdateAuthorizationState
from typing import Any, Awaitable, Callable

class MiddlewareBase(abc.ABC, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    async def __call__(self, update: Update, data: dict, next_handler: Callable[[Update, dict], Awaitable[Any]]) -> Any: ...

class FindClientMiddleware(MiddlewareBase):
    def __init__(self, client_manager: ClientManager) -> None: ...
    async def __call__(self, update: Update, data: dict, next_handler: Callable[[Update, dict], Awaitable[Any]]) -> Any: ...

class ClientManagerMiddleware(MiddlewareBase):
    def __init__(self, client_manager: ClientManager) -> None: ...
    async def __call__(self, update: Update, data: dict, next_handler: Callable[[Update, dict], Awaitable[Any]]) -> Any: ...
