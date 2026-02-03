import asyncio
from _typeshed import Incomplete
from bygram.core.types import T as T
from bygram.exceptions import TdlibException as TdlibException
from bygram.types.base import Function as Function, ObjectBase as ObjectBase
from bygram.types.raw import Error as Error
from typing import Any, Callable

logger: Incomplete

class Executor:
    def __init__(self, send: Callable[[int, Function, Any | None], None], loop: asyncio.AbstractEventLoop) -> None: ...
    async def process_response(self, response: ObjectBase, extra: Any): ...
    async def execute(self, client_id: int, function: Function[T], timeout: float) -> T: ...
