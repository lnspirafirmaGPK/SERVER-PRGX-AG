import logging
from typing import Any

from prgx_ag.core.aetherbus import AetherBus


class BaseAgent:
    def __init__(self, agent_id: str, role: str, bus: AetherBus) -> None:
        self.agent_id = agent_id
        self.role = role
        self.bus = bus
        self.logger = logging.getLogger(agent_id)
        self._running = False

    async def subscribe(self, topic: str, handler: Any) -> None:
        await self.bus.subscribe(topic, handler)

    async def publish(self, topic: str, payload: Any) -> None:
        await self.bus.publish(topic, payload)

    async def start(self) -> None:
        self._running = True

    async def stop(self) -> None:
        self._running = False
