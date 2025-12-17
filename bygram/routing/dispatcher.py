import functools
import inspect
import logging
from typing import Any, Awaitable, Callable, Iterable, Type, TypeVar

from bygram.routing.middlewares import MiddlewareBase
from bygram.types.base import Update

from .filters import FilterBase

T = TypeVar("T", bound=Update)

Callback = Callable[..., Awaitable[Any]]

logger = logging.getLogger(__name__)


def inject_dependencies(callback: Callback, update: Update, data: dict):
    kwargs = {}
    func_sig = inspect.signature(callback)
    for param in func_sig.parameters:
        if param in data:
            kwargs[param] = data[param]

    return callback(update, **kwargs)


class Handler:
    def __init__(self, callback: Callback, filters: Iterable[FilterBase]) -> None:
        self.callback = callback
        self.callback_signature = inspect.signature(self.callback)
        self.filters = filters

    async def is_pass_filters(self, update: Update, data: dict) -> bool:
        for filter in self.filters:
            try:
                result = await inject_dependencies(filter, update, data)
            except Exception:
                logger.exception(
                    "Error with filter %s at callback %s", filter, self.callback
                )
                return False
            if not result:
                return False
            if isinstance(result, dict):
                data.update(result)

        return True

    async def __call__(self, update: Update, data: dict) -> Any:
        return await inject_dependencies(self.callback, update, data)


class Router:
    def __init__(self) -> None:
        self.callbacks: dict[Type[Update], list[Handler]] = {}
        self.routers: list[Router] = []
        self.middlewares: list[MiddlewareBase] = []

    def include_router(self, router: "Router"):
        self.include_routers(router)

    def include_routers(self, *routers: "Router"):
        # TODO: Add check on recursive router adding
        self.routers.extend(routers)

    def add_middleware(self, middleware: MiddlewareBase):
        self.middlewares.append(middleware)

    def _create_chain(self, endpoint: Callable[[Update, dict], Awaitable[Any]]):
        handler = endpoint
        for middleware in self.middlewares:
            handler = functools.partial(middleware, next_handler=handler)

        return handler

    async def _handle_update(self, update: Update, data: dict) -> bool:
        data = data.copy()
        executed = False

        async def endpoint(update: Update, data: dict):
            nonlocal executed
            executed = await self._process_update(update, data)

        chained_function = self._create_chain(endpoint)
        await chained_function(update, data)
        return executed

    async def _process_update(self, update: Update, data: dict) -> bool:
        callbacks = self.callbacks.get(type(update))
        if not callbacks:
            return False

        for c in callbacks:
            if not await c.is_pass_filters(update, data):
                continue
            await c(update, data)

        for i in self.routers:
            await i._handle_update(update, data)

        return False

    def add_handler(
        self, type: Type[Update], callback: Callback, filters: Iterable[FilterBase]
    ):
        handler = Handler(callback, filters)
        handlers = self.callbacks.setdefault(type, [])
        handlers.append(handler)

    def register(self, type: Type[Update], *filters: FilterBase):
        return functools.partial(self.add_handler, type, filters=filters)


class Dispatcher(Router):
    def __init__(self) -> None:
        super().__init__()
        self.di: dict[str, Any] = {}

    async def _feed_update(self, update: Update, client_id: int):
        data = self.di.copy()
        data["client_id"] = client_id
        try:
            await self._handle_update(update, data)
        except Exception:
            logger.exception("Error while processing update %s", update)

    async def feed_update(self, update: Update, client_id: int):
        await self._feed_update(update, client_id)

    def __setitem__(self, key: str, value: Any):
        self.di[key] = value

    def __getitem__(self, key: str):
        return self.di[key]
