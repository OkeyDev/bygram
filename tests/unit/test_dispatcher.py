from bygram.dispatcher import Dispatcher
from bygram.types.base import Update


class FakeUpdate(Update):
    pass


async def test_add_handler():
    dp = Dispatcher()

    called = False

    async def callback(upd: FakeUpdate):
        nonlocal called
        called = True

    dp.add_handler(FakeUpdate, callback, [])
    await dp.feed_update(FakeUpdate(), 1)

    assert called


async def test_di():
    dp = Dispatcher()

    called = False
    client_id_ = None
    dp["channel_id"] = "Test"
    channel_id_ = None

    async def callback(upd: FakeUpdate, client_id: int, channel_id: str):
        nonlocal client_id_
        nonlocal channel_id_
        nonlocal called
        called = True
        client_id_ = client_id
        channel_id_ = channel_id

    dp.add_handler(FakeUpdate, callback, [])
    await dp.feed_update(FakeUpdate(), 1)

    assert called
    assert client_id_ == 1
    assert channel_id_ == "Test"
