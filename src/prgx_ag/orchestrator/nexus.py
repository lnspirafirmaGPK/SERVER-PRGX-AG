from pathlib import Path

from prgx_ag.agents import PRGX1Sentry, PRGX2Mechanic, PRGX3Diplomat
from prgx_ag.core import AetherBus
from prgx_ag.core.events import EXECUTE_FIX, FIX_COMPLETED, RSI_FEEDBACK
from prgx_ag.policy import PatimokkhaChecker
from prgx_ag.rsi import LearningState, RSIEngine


class PRGXAGNexus:
    def __init__(self, root: Path, history_size: int = 100) -> None:
        self.bus = AetherBus(history_size=history_size)
        self.checker = PatimokkhaChecker()
        self.prgx1 = PRGX1Sentry(self.bus, root=root)
        self.prgx2 = PRGX2Mechanic(self.bus, root=root, checker=self.checker)
        self.prgx3 = PRGX3Diplomat(agent_id="PRGX3", role="Diplomat", bus=self.bus)
        self.rsi_engine = RSIEngine()
        self.learning_state = LearningState()

    async def wire_subscriptions(self) -> None:
        await self.prgx3.start()
        await self.bus.subscribe(EXECUTE_FIX, self._handle_execute_fix)

    async def _handle_execute_fix(self, payload: dict) -> None:
        findings = payload.get("findings", {})
        outcome = await self.prgx2.apply_shadow_fix(findings.get("target", "repo"), payload)
        await self.prgx3.report_result(outcome)
        gem = self.rsi_engine.analyze(outcome)
        if gem and self.learning_state.apply_gem(gem):
            await self.bus.publish(RSI_FEEDBACK, {"gem": gem})

    async def run_self_healing_cycle(self) -> None:
        await self.prgx1.publish_issue_report()

    async def run_once(self) -> None:
        await self.wire_subscriptions()
        await self.run_self_healing_cycle()

    async def run_continuous(self, interval_seconds: int = 10) -> None:
        await self.wire_subscriptions()
        while True:
            await self.run_self_healing_cycle()
            from prgx_ag.orchestrator.cycle_runner import sleep_cycle

            await sleep_cycle(interval_seconds)
