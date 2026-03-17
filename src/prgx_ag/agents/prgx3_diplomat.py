from __future__ import annotations

from typing import Any
from uuid import uuid4

from prgx_ag.core import BaseAgent
from prgx_ag.core.events import EXECUTE_FIX, FIX_COMPLETED, INTENT_TRANSLATED, ISSUE_REPORTED
from prgx_ag.schemas import AuditStatus, EthicalStatus, Intent
from prgx_ag.services.healing_intent_builder import build_fix_plan
from prgx_ag.services.narrative_builder import build_commit_style_narrative
from prgx_ag.services.translation_matrix import build_healing_intent, translate_status


class PRGX3Diplomat(BaseAgent):
    async def start(self) -> None:
        await super().start()
        await self.subscribe(ISSUE_REPORTED, self.receive_issue_report)

    def create_healing_intent(self, findings: dict[str, Any]) -> Intent:
        return build_healing_intent(findings)

    def translate_to_world(self, status: EthicalStatus) -> str:
        return translate_status(status)

    def build_narrative(self, outcome) -> str:
        return build_commit_style_narrative(outcome)

    async def publish_execute_fix(self, payload: dict[str, Any]) -> None:
        await self.publish(EXECUTE_FIX, payload)

    async def receive_issue_report(self, findings: dict[str, object]) -> None:
        intent = self.create_healing_intent(findings)
        payload = {
            'envelope_id': str(uuid4()),
            'intent': intent,
            'audit_status': AuditStatus.APPROVED,
            'findings': findings,
            'fixes': build_fix_plan(findings),
        }
        await self.publish(INTENT_TRANSLATED, {'intent': intent})
        await self.publish_execute_fix(payload)

    async def report_result(self, outcome) -> None:
        await self.publish(FIX_COMPLETED, {'outcome': outcome, 'narrative': self.build_narrative(outcome)})
