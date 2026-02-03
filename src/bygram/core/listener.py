import asyncio
import logging
import threading
from concurrent.futures import CancelledError
from contextlib import suppress
from typing import Callable

from bygram.core.types import DeserializedObject

logger = logging.getLogger(__name__)


class EventListener:
    def __init__(
        self,
        loop: asyncio.AbstractEventLoop,
        receive: Callable[[float], DeserializedObject | None],
        timeout: float = 60,
        queue_size: int = 20,
    ) -> None:
        self._loop = loop
        self._receive = receive
        self._timeout = timeout
        self._queue: asyncio.Queue = asyncio.Queue(queue_size)
        self._thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._started = False
        self._shutdown = False

    def _receive_update(self) -> DeserializedObject | None:
        return self._receive(self._timeout)

    def _put_object_to_async_queue(self, event: DeserializedObject):
        future = asyncio.run_coroutine_threadsafe(self._queue.put(event), self._loop)
        with suppress(CancelledError):
            future.result()

    def _listen_loop(self):
        while not self._shutdown:
            try:
                obj = self._receive_update()
                if obj:
                    self._put_object_to_async_queue(obj)
            except Exception:
                logger.exception("Error while processing update")

    async def wait_for_event(self) -> DeserializedObject:
        if not self._started:
            self._thread.start()
            self._started = True
        return await self._queue.get()

    def shutdown(self):
        self._shutdown = True
