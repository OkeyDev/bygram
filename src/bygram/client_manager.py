import asyncio
import logging

from bygram.core.serializer import SerializedWrapper
from bygram.core.types import T
from bygram.executor import Executor
from bygram.types.base import Function
from bygram.types.raw import (
    AuthorizationStateClosed,
    Close,
    UpdateAuthorizationState,
)

logger = logging.getLogger(__name__)

SHUTDOWN_TIMEOUT = 60


class Client:
    def __init__(self, client_id: int, executor: Executor) -> None:
        self.id = client_id
        self._executor = executor
        self._shutdowned = False

    async def execute(self, function: Function[T], timeout: float = 30) -> T:
        if self._shutdowned:
            raise RuntimeError("Current client already shutdowned")
        return await self._executor.execute(self.id, function, timeout)


class ClientManager:
    def __init__(self, executor: Executor, wrapper: SerializedWrapper) -> None:
        self._executor = executor
        self._wrapper = wrapper

        self._clients: dict[int, Client] = {}
        self._client_closed_event = None
        self._shutdown = False

    def create_client(self) -> Client:
        if self._shutdown:
            raise RuntimeError("Client manager is shutting down")

        client_id = self._wrapper.create_client()
        self._clients[client_id] = client = Client(client_id, self._executor)
        return client

    def get_client_by_id(self, client_id: int):
        return self._clients[client_id]

    async def handle_authorization_state_update(
        self, update: UpdateAuthorizationState, client_id: int
    ):
        if isinstance(update.authorization_state, AuthorizationStateClosed):
            client = self._clients.pop(client_id)
            client._shutdowned = True
            if self._client_closed_event:
                self._client_closed_event.set()

    async def _close_clients(self):
        logger.debug("Shutting down clients")
        tasks = [
            asyncio.create_task(client.execute(Close()))
            for client in self._clients.values()
        ]
        await asyncio.gather(*tasks, return_exceptions=True)

    async def _wait_till_all_clients_closed(self):
        self._client_closed_event = asyncio.Event()
        while self._clients:
            self._client_closed_event.clear()
            await self._client_closed_event.wait()

    async def shutdown(self):
        if self._shutdown:
            return
        self._shutdown = True
        async with asyncio.timeout(SHUTDOWN_TIMEOUT):
            await self._close_clients()
            await self._wait_till_all_clients_closed()
