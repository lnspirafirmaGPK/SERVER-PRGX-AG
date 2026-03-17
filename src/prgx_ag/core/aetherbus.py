import asyncio
import logging
from collections import defaultdict, deque
from collections.abc import Awaitable, Callable
from typing import Any

Handler = Callable[[Any], Awaitable[None]]


class AetherBus:
    def __init__(self, history_size: int = 100) -> None:
        self._subs: dict[str, list[Handler]] = defaultdict(list)
        self._history: deque[tuple[str, Any]] = deque(maxlen=history_size)
        self._logger = logging.getLogger(self.__class__.__name__)

    async def subscribe(self, topic: str, handler: Handler) -> None:
        self._subs[topic].append(handler)

    async def publish(self, topic: str, payload: Any) -> None:
        self._history.append((topic, payload))
        handlers = self._subs.get(topic, [])
        if not handlers:
            return
        tasks = [self._safe_dispatch(h, payload, topic) for h in handlers]
        await asyncio.gather(*tasks)

    async def _safe_dispatch(self, handler: Handler, payload: Any, topic: str) -> None:
        try:
            await handler(payload)
        except Exception as exc:  # noqa: BLE001
            self._logger.exception("handler_failed topic=%s err=%s", topic, exc)

    @property
    def history(self) -> list[tuple[str, Any]]:
        return list(self._history)
