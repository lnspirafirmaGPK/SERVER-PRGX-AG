from __future__ import annotations

from pathlib import Path
from time import perf_counter
from typing import Any

from prgx_ag.core import BaseAgent
from prgx_ag.policy import PatimokkhaChecker
from prgx_ag.schemas import AuditStatus, Intent, ProcessingOutcome
from prgx_ag.services.fix_executor import apply_safe_fixes


class PRGX2Mechanic(BaseAgent):
    """Controlled executor for audited repair plans."""

    def __init__(
        self,
        bus,
        root: Path,
        checker: PatimokkhaChecker,
        allowed_paths: list[str],
        protected_paths: list[str],
        dry_run: bool = True,
    ) -> None:
        super().__init__(agent_id="PRGX2", role="Mechanic", bus=bus)
        self.root = root
        self.checker = checker
        self.allowed_paths = allowed_paths
        self.protected_paths = protected_paths
        self.dry_run = dry_run

    def _reject(
        self,
        *,
        envelope_id: str,
        message: str,
        target: str,
        details: dict[str, Any] | None = None,
    ) -> ProcessingOutcome:
        payload_details = {
            "target": target,
            "dry_run": self.dry_run,
        }
        if details:
            payload_details.update(details)

        return ProcessingOutcome(
            agent_name=self.agent_id,
            envelope_id=envelope_id,
            success=False,
            execution_time=0.0,
            message=message,
            details=payload_details,
        )

    def _coerce_audit_status(self, raw: object) -> AuditStatus | None:
        if isinstance(raw, AuditStatus):
            return raw

        if isinstance(raw, str):
            try:
                return AuditStatus(raw)
            except ValueError:
                return None

        return None

    def _normalize_fixes(self, raw: object) -> list[dict[str, str]] | None:
        if not isinstance(raw, list):
            return None

        normalized: list[dict[str, str]] = []

        for index, item in enumerate(raw):
            if not isinstance(item, dict):
                return None

            path = item.get("path")
            if not isinstance(path, str) or not path.strip():
                return None

            content = item.get("content", "")
            if content is None:
                content = ""
            elif not isinstance(content, str):
                content = str(content)

            normalized.append(
                {
                    "path": path.strip(),
                    "content": content,
                }
            )

        return normalized

    async def update_dependency(self, path: str, content: str) -> ProcessingOutcome:
        return apply_safe_fixes(
            self.root,
            fixes=[{"path": path, "content": content}],
            allowed_paths=self.allowed_paths,
            protected_paths=self.protected_paths,
            envelope_id="dependency-update",
            dry_run=self.dry_run,
        )

    async def repair_structure(
        self,
        fixes: list[dict[str, str]],
        envelope_id: str,
    ) -> ProcessingOutcome:
        return apply_safe_fixes(
            self.root,
            fixes=fixes,
            allowed_paths=self.allowed_paths,
            protected_paths=self.protected_paths,
            envelope_id=envelope_id,
            dry_run=self.dry_run,
        )

    async def cleanup(self, target: str) -> ProcessingOutcome:
        return ProcessingOutcome(
            agent_name=self.agent_id,
            envelope_id="cleanup",
            success=True,
            execution_time=0.0,
            message=f"Cleanup reviewed for {target}",
            details={"target": target, "dry_run": self.dry_run},
        )

    async def apply_shadow_fix(
        self,
        target: str,
        fix_plan: dict[str, object],
    ) -> ProcessingOutcome:
        if not isinstance(fix_plan, dict):
            return self._reject(
                envelope_id="na",
                message="Invalid fix plan payload",
                target=target,
            )

        envelope_id = str(fix_plan.get("envelope_id", "na"))

        intent = fix_plan.get("intent")
        if not isinstance(intent, Intent):
            return self._reject(
                envelope_id=envelope_id,
                message="Invalid or missing intent",
                target=target,
            )

        audit_status = self._coerce_audit_status(fix_plan.get("audit_status"))
        if audit_status is None:
            return self._reject(
                envelope_id=envelope_id,
                message="Invalid or missing audit status",
                target=target,
            )

        audit_payload = fix_plan.get("audit")
        if audit_payload is not None and not isinstance(audit_payload, dict):
            return self._reject(
                envelope_id=envelope_id,
                message="Invalid audit payload",
                target=target,
            )

        fixes = self._normalize_fixes(fix_plan.get("fixes", []))
        if fixes is None:
            return self._reject(
                envelope_id=envelope_id,
                message="Invalid fixes payload",
                target=target,
            )

        if audit_status != AuditStatus.APPROVED:
            return self._reject(
                envelope_id=envelope_id,
                message="Rejected: intent not approved",
                target=target,
                details={
                    "audit_status": str(audit_status),
                    "fix_count": len(fixes),
                },
            )

        audit = self.checker.validate_intent(intent)
        if not audit.is_allowed:
            return self._reject(
                envelope_id=envelope_id,
                message=f"Rejected by Patimokkha: {audit.reason}",
                target=target,
                details={
                    "fix_count": len(fixes),
                    "audit_reason": audit.reason,
                    "audit_status": str(audit.status),
                },
            )

        if not fixes:
            return self._reject(
                envelope_id=envelope_id,
                message="No executable fixes supplied",
                target=target,
                details={"fix_count": 0},
            )

        start = perf_counter()
        outcome = await self.repair_structure(fixes, envelope_id)
        outcome.execution_time = perf_counter() - start

        merged_details = dict(outcome.details)
        merged_details.update(
            {
                "target": target,
                "fix_count": len(fixes),
                "dry_run": self.dry_run,
                "audit_reason": audit.reason,
            }
        )
        if isinstance(audit_payload, dict):
            merged_details["payload_audit"] = audit_payload

        outcome.details = merged_details
        return outcome
