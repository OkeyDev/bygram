import asyncio
import logging
from typing import Any, Callable

from bygram.core.types import T
from bygram.exceptions import TdlibException
from bygram.types.base import Function, ObjectBase
from bygram.types.raw import Error

logger = logging.getLogger(__name__)


class Executor:
    def __init__(
        self,
        send: Callable[[int, Function, Any | None], None],
        loop: asyncio.AbstractEventLoop,
    ) -> None:
        self._send = send
        self._loop = loop
        self._waiting_response: dict[Any, asyncio.Future] = {}
        self._request_id = 1

    async def process_response(self, response: ObjectBase, extra: Any):
        waiting_lock = self._waiting_response.pop(extra, None)
        if waiting_lock is None:
            logger.warning(
                "Can't find waiter with extra %s. Lost response %s", extra, response
            )
            return

        if isinstance(response, Error):
            exc = TdlibException(response.code, response.message)
            waiting_lock.set_exception(exc)
        else:
            waiting_lock.set_result(response)

    def _next_request_id(self) -> int:
        self._request_id += 1
        return self._request_id

    async def execute(self, client_id: int, function: Function[T], timeout: float) -> T:
        request_id = self._next_request_id()
        wait_future = self._waiting_response[request_id] = self._loop.create_future()
        self._send(client_id, function, request_id)
        async with asyncio.timeout(timeout):
            return await wait_future
