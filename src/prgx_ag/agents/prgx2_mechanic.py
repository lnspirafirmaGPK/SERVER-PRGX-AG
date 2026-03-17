from pathlib import Path
from time import perf_counter

from prgx_ag.core import BaseAgent
from prgx_ag.policy import PatimokkhaChecker
from prgx_ag.schemas import AuditStatus, Intent, ProcessingOutcome
from prgx_ag.services.fix_executor import apply_file_append


class PRGX2Mechanic(BaseAgent):
    def __init__(self, bus, root: Path, checker: PatimokkhaChecker) -> None:
        super().__init__(agent_id="PRGX2", role="Mechanic", bus=bus)
        self.root = root
        self.checker = checker

    def update_dependency(self, *_args, **_kwargs) -> str:
        return "dependency update simulated"

    def repair_structure(self, fix_plan: dict) -> str:
        notes_path = self.root / "FIX_LOG.md"
        apply_file_append(notes_path, f"\n- Applied repair: {fix_plan}\n")
        return "structure repaired"

    def cleanup(self) -> str:
        return "cleanup complete"

    async def apply_shadow_fix(self, target: str, fix_plan: dict) -> ProcessingOutcome:
        intent: Intent = fix_plan["intent"]
        audit_status: AuditStatus = fix_plan["audit_status"]
        start = perf_counter()

        if audit_status != AuditStatus.APPROVED:
            return ProcessingOutcome(
                agent_name=self.agent_id,
                envelope_id=fix_plan.get("envelope_id", "na"),
                success=False,
                execution_time=0.0,
                revenue_generated=0.0,
                message="Rejected: intent not approved",
                details={"target": target},
            )

        audit = self.checker.validate_intent(intent)
        if not audit.is_allowed:
            return ProcessingOutcome(
                agent_name=self.agent_id,
                envelope_id=fix_plan.get("envelope_id", "na"),
                success=False,
                execution_time=0.0,
                revenue_generated=0.0,
                message=f"Rejected by Patimokkha: {audit.reason}",
                details={"target": target},
            )

        msg = self.repair_structure(fix_plan)
        end = perf_counter()
        return ProcessingOutcome(
            agent_name=self.agent_id,
            envelope_id=fix_plan.get("envelope_id", "na"),
            success=True,
            execution_time=end - start,
            revenue_generated=1.0,
            message=msg,
            details={"target": target},
        )
