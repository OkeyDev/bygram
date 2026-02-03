import asyncio
from _typeshed import Incomplete
from bygram.core.types import DeserializedObject as DeserializedObject
from typing import Callable

logger: Incomplete

class EventListener:
    def __init__(self, loop: asyncio.AbstractEventLoop, receive: Callable[[float], DeserializedObject | None], timeout: float = 60, queue_size: int = 20) -> None: ...
    async def wait_for_event(self) -> DeserializedObject: ...
    def shutdown(self) -> None: ...
