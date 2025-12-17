import asyncio
import time

import pytest

from bygram.core.listener import EventListener
from bygram.core.types import DeserializedObject
from bygram.types.base import ObjectBase


def fake_receive_func(events: list[DeserializedObject] | None = None):
    if events is None:
        events = []

    def receive(timeout: float):
        if events:
            return events.pop(0)
        time.sleep(timeout)

    return receive


def create_event_listener(*events: DeserializedObject, timeout: float = 60):
    loop = asyncio.get_event_loop()
    fake_receive = fake_receive_func(list(events))
    return EventListener(loop, receive=fake_receive, timeout=timeout)


async def test_event():
    event1 = DeserializedObject(ObjectBase())
    event2 = DeserializedObject(ObjectBase())
    event_listener = create_event_listener(event1, event2)
    async with asyncio.timeout(1):
        income_event1 = await event_listener.wait_for_event()
        income_event2 = await event_listener.wait_for_event()

    assert income_event1 == event1
    assert income_event2 == event2


async def test_event_timeout():
    event_listener = create_event_listener(timeout=0.1)
    with pytest.raises(TimeoutError):
        async with asyncio.timeout(1):
            await event_listener.wait_for_event()
