import asyncio
from contextlib import suppress

from bygram.core.listener import EventListener
from bygram.core.types import DeserializedObject
from bygram.executor import Executor
from bygram.routing.dispatcher import Dispatcher


class EventsLoop:
    def __init__(
        self,
        listener: EventListener,
        executor: Executor,
        dispatcher: Dispatcher | None = None,
    ) -> None:
        self.listener = listener
        self.executor = executor
        self.dispatcher = dispatcher

        self._initalized = False
        self._events_task: asyncio.Task | None = None

    def attach_dispatcher(self, dp: Dispatcher):
        if self.dispatcher:
            raise RuntimeError(f"Dispatcher already attached: {self.dispatcher}")
        self.dispatcher = dp

    def start_listening(self):
        self._events_task = asyncio.create_task(self._listen_events())
        self._initalized = True

    async def join(self):
        if not self._initalized:
            raise RuntimeError("Bygram event loop is not initalized")

        assert self._events_task
        with suppress(asyncio.CancelledError):
            await asyncio.shield(self._events_task)

    async def _wait_event(self) -> DeserializedObject:
        return await self.listener.wait_for_event()

    async def _resend_event(self, event: DeserializedObject):
        if event.extra is not None:
            await self.executor.process_response(event.obj, event.extra)
        elif self.dispatcher:
            assert event.client_id
            await self.dispatcher.feed_update(event.obj, event.client_id)

    async def _event_cycle(self):
        event = await self._wait_event()
        await self._resend_event(event)

    async def _listen_events(self):
        while self._initalized:
            await self._event_cycle()

    async def shutdown(self):
        if not self._initalized:
            return

        assert self._events_task
        self._initalized = False
        self._events_task.cancel()
        self.listener.shutdown()

        with suppress(asyncio.CancelledError):
            await self._events_task
