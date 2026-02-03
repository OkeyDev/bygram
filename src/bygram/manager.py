import asyncio
import logging
from enum import Enum, auto

from bygram.client_manager import Client, ClientManager
from bygram.core.listener import EventListener
from bygram.core.serializer import SerializedWrapper
from bygram.core.types import T
from bygram.core.wrapper import load_library
from bygram.executor import Executor
from bygram.routing.dispatcher import Dispatcher
from bygram.routing.middlewares import ClientManagerMiddleware
from bygram.strategy import EventsLoop
from bygram.types.base import Function

_instance = None

logger = logging.getLogger(__name__)


class LibraryState(Enum):
    created = auto()
    initalized = auto()
    shutting_down = auto()
    shutdowned = auto()


def create_library_manager(
    path: str,
    loop: asyncio.AbstractEventLoop | None = None,
    receive_timeout: float = 60,
):
    global _instance
    if _instance and _instance._state != LibraryState.shutdowned:
        raise RuntimeError("LibraryManager manager already exists")

    if loop is None:
        loop = asyncio.get_event_loop()

    wrapper = load_library(path)
    serialized_wrapper = SerializedWrapper(wrapper)
    listener = EventListener(loop, serialized_wrapper.receive, timeout=receive_timeout)
    executor = Executor(serialized_wrapper.send, loop)
    event_loop = EventsLoop(listener, executor)
    client_manager = ClientManager(executor, serialized_wrapper)
    library_manager = LibraryManager(client_manager, event_loop, serialized_wrapper)

    _instance = library_manager
    return library_manager


class LibraryManager:
    def __init__(
        self,
        client_manager: ClientManager,
        event_loop: EventsLoop,
        serialized_wrapper: SerializedWrapper,
    ) -> None:
        self._client_manager = client_manager
        self._serialized_wrapper = serialized_wrapper
        self._event_loop = event_loop
        self._dispatcher: Dispatcher | None = None

        self._state = LibraryState.created

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.shutdown()

    def _check_initalized(self):
        if self._state != LibraryState.initalized:
            raise RuntimeError("You should initialize LibraryManager before use")

    def create_client(self) -> Client:
        self.init()
        return self._client_manager.create_client()

    def execute(self, function: Function[T]) -> T:
        return self._serialized_wrapper.execute(function)

    def attach_dispatcher(self, dp: Dispatcher):
        if self._dispatcher:
            raise RuntimeError(f"Dispatcher already attached: {self._dispatcher}")

        self._dispatcher = dp
        self._event_loop.attach_dispatcher(self._dispatcher)
        self._dispatcher.add_middleware(ClientManagerMiddleware(self._client_manager))

    def init(self):
        if self._state == LibraryState.initalized:
            return
        if self._state in (LibraryState.shutting_down, LibraryState.shutdowned):
            raise RuntimeError("Trying to initalize library in state of shutting down")
        self._event_loop.start_listening()
        self._state = LibraryState.initalized
        logger.info("Library initalized")

    async def join(self):
        self._check_initalized()
        await self._event_loop.join()

    async def _shutdown(self):
        # Closing all clients
        await self._client_manager.shutdown()

        # Properly shutting down event reading loop
        await self._event_loop.shutdown()

    async def shutdown(self):
        if self._state != LibraryState.initalized:
            return

        logger.info("Shutting down library")
        self._state = LibraryState.shutting_down
        await self._shutdown()
        self._state = LibraryState.shutdowned
        logger.info("Library shutted down")
