diff --git a/src/prgx_ag/agents/prgx1_sentry.py b/src/prgx_ag/agents/prgx1_sentry.py
--- a/src/prgx_ag/agents/prgx1_sentry.py
+++ b/src/prgx_ag/agents/prgx1_sentry.py
@@
-from __future__ import annotations
-
-from pathlib import Path
-
-from prgx_ag.core import BaseAgent
-from prgx_ag.core.events import ISSUE_REPORTED
-
-from prgx_ag.services.dependency_scanner import scan_dependency_anomalies
-
-from prgx_ag.services.integrity_scanner import scan_integrity_drift
-
-from prgx_ag.services.structure_scanner import detect_structure_issues
-
-class PRGX1Sentry(BaseAgent):
-
- """Read-only guardian eye (Anicca observer)."""
-
- def __init__(self, bus, root: Path) -> None:
-
- super().__init__(agent_id='PRGX1', role='Sentry', bus=bus)
-
- self.root = root
- def detect_outdated_dependencies(self) -> list[str]:
-
- return scan_dependency_anomalies(self.root)
-
- def detect_structural_anomalies(self) -> list[str]:
-
- return detect_structure_issues(self.root)
-
- def detect_integrity_drift(self) -> list[str]:
-
- return scan_integrity_drift(self.root)
-
- def scan_entropy(self) -> dict[str, object]:
-
- dep_issues = self.detect_outdated_dependencies()
-
- structural_issues = self.detect_structural_anomalies()
-
- integrity_issues = self.detect_integrity_drift()
-
- all_issues = dep_issues + structural_issues + integrity_issues
-
- return {
- 'summary': 'repository scan completed',
- 'target': str(self.root),
- 'dependency_issues': dep_issues,
- 'structural_issues': structural_issues,
- 'integrity_issues': integrity_issues,
- 'requires_fix': bool(all_issues),
- }
-
- async def publish_issue_report(self) -> dict[str, object]:
-
- report = self.scan_entropy()
-
- await self.publish(ISSUE_REPORTED, report)
-
- return report
+from __future__ import annotations
+
+from collections.abc import Mapping
+from pathlib import Path
+
+from prgx_ag.core import BaseAgent
+from prgx_ag.core.events import ISSUE_REPORTED
+from prgx_ag.services.dependency_scanner import scan_dependency_anomalies
+from prgx_ag.services.integrity_scanner import scan_integrity_drift
+from prgx_ag.services.structure_scanner import detect_structure_issues
+
+
+class PRGX1Sentry(BaseAgent):
+    """Read-only guardian eye (Anicca observer)."""
+
+    def __init__(self, bus, root: Path) -> None:
+        super().__init__(agent_id="PRGX1", role="Sentry", bus=bus)
+        self.root = root
+
+    def detect_outdated_dependencies(self) -> list[str]:
+        return scan_dependency_anomalies(self.root)
+
+    def detect_structural_anomalies(self) -> list[str]:
+        return detect_structure_issues(self.root)
+
+    def detect_integrity_drift(self) -> list[str]:
+        return scan_integrity_drift(self.root)
+
+    @staticmethod
+    def has_findings(report: Mapping[str, object]) -> bool:
+        return bool(report.get("requires_fix", False))
+
+    def scan_entropy(self) -> dict[str, object]:
+        dep_issues = self.detect_outdated_dependencies()
+        structural_issues = self.detect_structural_anomalies()
+        integrity_issues = self.detect_integrity_drift()
+
+        all_issues = dep_issues + structural_issues + integrity_issues
+        return {
+            "summary": "repository scan completed",
+            "target": str(self.root),
+            "dependency_issues": dep_issues,
+            "structural_issues": structural_issues,
+            "integrity_issues": integrity_issues,
+            "issue_count": len(all_issues),
+            "requires_fix": bool(all_issues),
+        }
+
+    async def publish_issue_report(self) -> dict[str, object]:
+        report = self.scan_entropy()
+
+        if not self.has_findings(report):
+            self.logger.info(
+                "No actionable findings detected; skipping %s publish.",
+                ISSUE_REPORTED,
+            )
+            return report
+
+        await self.publish(ISSUE_REPORTED, report)
+        return report

diff --git a/src/prgx_ag/agents/prgx3_diplomat.py b/src/prgx_ag/agents/prgx3_diplomat.py
--- a/src/prgx_ag/agents/prgx3_diplomat.py
+++ b/src/prgx_ag/agents/prgx3_diplomat.py
@@
-from __future__ import annotations
-
-from typing import Any
-
-from uuid import uuid4
-
-from prgx_ag.core import BaseAgent
-
-from prgx_ag.core.events import EXECUTE_FIX, FIX_COMPLETED, INTENT_TRANSLATED, ISSUE_REPORTED
-
-from prgx_ag.schemas import AuditStatus, EthicalStatus, Intent
-
-from prgx_ag.services.healing_intent_builder import build_fix_plan
-
-from prgx_ag.services.narrative_builder import build_commit_style_narrative
-
-from prgx_ag.services.translation_matrix import build_healing_intent, translate_status
-
-class PRGX3Diplomat(BaseAgent):
- async def start(self) -> None:
-
- await super().start()
-
- await self.subscribe(ISSUE_REPORTED, self.receive_issue_report)
- def create_healing_intent(self, findings: dict[str, Any]) -> Intent:
-
- return build_healing_intent(findings)
- def translate_to_world(self, status: EthicalStatus) -> str:
-
- return translate_status(status)
- def build_narrative(self, outcome) -> str:
-
- return build_commit_style_narrative(outcome)
- async def publish_execute_fix(self, payload: dict[str, Any]) -> None:
-
- await self.publish(EXECUTE_FIX, payload)
- async def receive_issue_report(self, findings: dict[str, object]) -> None:
-
- intent = self.create_healing_intent(findings)
-
- payload = {
- 'envelope_id': str(uuid4()),
- 'intent': intent,
- 'audit_status': AuditStatus.APPROVED,
- 'findings': findings,
- 'fixes': build_fix_plan(findings),
- }
-
- await self.publish(INTENT_TRANSLATED, {'intent': intent})
-
- await self.publish_execute_fix(payload)
- async def report_result(self, outcome) -> None:
-
- await self.publish(FIX_COMPLETED, {'outcome': outcome, 'narrative': self.build_narrative(outcome)})
+from __future__ import annotations
+
+from typing import Any
+from uuid import uuid4
+
+from prgx_ag.core import BaseAgent
+from prgx_ag.core.events import (
+    AUDIT_VIOLATION,
+    EXECUTE_FIX,
+    FIX_COMPLETED,
+    INTENT_TRANSLATED,
+    ISSUE_REPORTED,
+)
+from prgx_ag.policy import PatimokkhaChecker
+from prgx_ag.schemas import AuditStatus, EthicalStatus, Intent
+from prgx_ag.services.healing_intent_builder import build_fix_plan
+from prgx_ag.services.narrative_builder import build_commit_style_narrative
+from prgx_ag.services.translation_matrix import build_healing_intent, translate_status
+
+
+class PRGX3Diplomat(BaseAgent):
+    def __init__(
+        self,
+        bus,
+        checker: PatimokkhaChecker | None = None,
+        agent_id: str = "PRGX3",
+        role: str = "Diplomat",
+    ) -> None:
+        super().__init__(agent_id=agent_id, role=role, bus=bus)
+        self.checker = checker or PatimokkhaChecker()
+
+    async def start(self) -> None:
+        await super().start()
+        await self.subscribe(ISSUE_REPORTED, self.receive_issue_report)
+
+    def create_healing_intent(self, findings: dict[str, Any]) -> Intent:
+        return build_healing_intent(findings)
+
+    def translate_to_world(self, status: EthicalStatus) -> str:
+        return translate_status(status)
+
+    def build_narrative(self, outcome) -> str:
+        return build_commit_style_narrative(outcome)
+
+    def evaluate_audit(self, intent: Intent) -> tuple[AuditStatus, dict[str, Any]]:
+        audit = self.checker.validate_intent(intent)
+        audit_status = AuditStatus.APPROVED if audit.is_allowed else AuditStatus.REJECTED
+        return audit_status, audit.model_dump()
+
+    async def publish_execute_fix(self, payload: dict[str, Any]) -> None:
+        await self.publish(EXECUTE_FIX, payload)
+
+    async def receive_issue_report(self, findings: dict[str, object]) -> None:
+        if not bool(findings.get("requires_fix", False)):
+            self.logger.info("Issue report marked as non-actionable; skipping execution.")
+            return
+
+        intent = self.create_healing_intent(findings)
+        fixes = build_fix_plan(findings)
+        envelope_id = str(uuid4())
+        audit_status, audit = self.evaluate_audit(intent)
+
+        payload = {
+            "envelope_id": envelope_id,
+            "intent": intent,
+            "audit_status": audit_status,
+            "audit": audit,
+            "findings": findings,
+            "fixes": fixes,
+        }
+
+        await self.publish(INTENT_TRANSLATED, {"intent": intent})
+
+        if audit_status != AuditStatus.APPROVED:
+            await self.publish(
+                AUDIT_VIOLATION,
+                {
+                    "envelope_id": envelope_id,
+                    "intent": intent,
+                    "audit_status": audit_status,
+                    "audit": audit,
+                    "findings": findings,
+                },
+            )
+            return
+
+        if not fixes:
+            self.logger.info(
+                "No executable fix plan generated for envelope %s; skipping execution.",
+                envelope_id,
+            )
+            return
+
+        await self.publish_execute_fix(payload)
+
+    async def report_result(self, outcome) -> None:
+        await self.publish(
+            FIX_COMPLETED,
+            {"outcome": outcome, "narrative": self.build_narrative(outcome)},
+        )

diff --git a/src/prgx_ag/services/fix_executor.py b/src/prgx_ag/services/fix_executor.py
--- a/src/prgx_ag/services/fix_executor.py
+++ b/src/prgx_ag/services/fix_executor.py
@@
-from __future__ import annotations
-
-from pathlib import Path
-
-from prgx_ag.schemas import ProcessingOutcome
-
-def _is_under(path: Path, base: Path) -> bool:
- try:
-
- path.resolve().relative_to(base.resolve())
-
- return True
-
- except ValueError:
-
- return False
-def apply_safe_fixes(
- repo_root: Path,
- fixes: list[dict[str, str]],
- allowed_paths: list[str],
- protected_paths: list[str],
- envelope_id: str,
- dry_run: bool,
-) -> ProcessingOutcome:
- changed: list[str] = []
- for fix in fixes:
- rel_path = fix['path']
- target = (repo_root / rel_path).resolve()
- if any(str(rel_path).startswith(protected.rstrip('/')) for protected in protected_paths):
- return ProcessingOutcome(agent_name='PRGX2', envelope_id=envelope_id, success=False, execution_time=0.0, message=f'Protected path blocked: {rel_path}')
- allowed = any(_is_under(target, (repo_root / p).resolve()) for p in allowed_paths)
- if not allowed:
- return ProcessingOutcome(agent_name='PRGX2', envelope_id=envelope_id, success=False, execution_time=0.0, message=f'Path not allowed: {rel_path}')
- if not dry_run:
- target.parent.mkdir(parents=True, exist_ok=True)
- content = fix.get('content', '')
- target.write_text(content, encoding='utf-8')
- changed.append(rel_path)
- return ProcessingOutcome(agent_name='PRGX2', envelope_id=envelope_id, success=True, execution_time=0.01, message='Safe fixes applied', details={'changed': changed})
+from __future__ import annotations
+
+from fnmatch import fnmatch
+from pathlib import Path
+
+from prgx_ag.schemas import ProcessingOutcome
+
+
+def _is_under(path: Path, base: Path) -> bool:
+    try:
+        path.resolve().relative_to(base.resolve())
+        return True
+    except ValueError:
+        return False
+
+
+def _normalize_rel_path(rel_path: str) -> str:
+    return rel_path.replace("\\", "/").lstrip("./")
+
+
+def _matches_protected(rel_path: str, protected_paths: list[str]) -> bool:
+    normalized = _normalize_rel_path(rel_path)
+
+    for protected in protected_paths:
+        pattern = protected.replace("\\", "/").rstrip("/")
+        if not pattern:
+            continue
+
+        if normalized == pattern or normalized.startswith(f"{pattern}/"):
+            return True
+
+        if fnmatch(normalized, pattern) or fnmatch(f"./{normalized}", pattern):
+            return True
+
+    return False
+
+
+def apply_safe_fixes(
+    repo_root: Path,
+    fixes: list[dict[str, str]],
+    allowed_paths: list[str],
+    protected_paths: list[str],
+    envelope_id: str,
+    dry_run: bool,
+) -> ProcessingOutcome:
+    changed: list[str] = []
+
+    for fix in fixes:
+        rel_path = str(fix.get("path", "")).strip()
+        if not rel_path:
+            return ProcessingOutcome(
+                agent_name="PRGX2",
+                envelope_id=envelope_id,
+                success=False,
+                execution_time=0.0,
+                message="Fix entry missing path",
+            )
+
+        rel_target = Path(rel_path)
+        if rel_target.is_absolute():
+            return ProcessingOutcome(
+                agent_name="PRGX2",
+                envelope_id=envelope_id,
+                success=False,
+                execution_time=0.0,
+                message=f"Absolute path blocked: {rel_path}",
+            )
+
+        normalized_rel_path = _normalize_rel_path(rel_path)
+        target = (repo_root / normalized_rel_path).resolve()
+
+        if _matches_protected(normalized_rel_path, protected_paths):
+            return ProcessingOutcome(
+                agent_name="PRGX2",
+                envelope_id=envelope_id,
+                success=False,
+                execution_time=0.0,
+                message=f"Protected path blocked: {normalized_rel_path}",
+            )
+
+        allowed = any(_is_under(target, (repo_root / p).resolve()) for p in allowed_paths)
+        if not allowed:
+            return ProcessingOutcome(
+                agent_name="PRGX2",
+                envelope_id=envelope_id,
+                success=False,
+                execution_time=0.0,
+                message=f"Path not allowed: {normalized_rel_path}",
+            )
+
+        if not dry_run:
+            target.parent.mkdir(parents=True, exist_ok=True)
+            content = str(fix.get("content", ""))
+            target.write_text(content, encoding="utf-8")
+
+        changed.append(normalized_rel_path)
+
+    return ProcessingOutcome(
+        agent_name="PRGX2",
+        envelope_id=envelope_id,
+        success=True,
+        execution_time=0.01,
+        message="Safe fixes applied",
+        details={"changed": changed, "dry_run": dry_run},
+    )

diff --git a/src/prgx_ag/rsi/learning_state.py b/src/prgx_ag/rsi/learning_state.py
--- a/src/prgx_ag/rsi/learning_state.py
+++ b/src/prgx_ag/rsi/learning_state.py
@@
-from __future__ import annotations
-
-import json
-
-from dataclasses import dataclass, field
-
-from pathlib import Path
-
-from prgx_ag.schemas import GemOfWisdom
-
-@dataclass(slots=True)
-
-class LearningState:
- parameters: dict[str, float] = field(default_factory=lambda: {'stability': 1.0, 'efficiency': 1.0})
-
- def apply_gem(self, gem: GemOfWisdom) -> bool:
-
- if not gem.safe_to_apply:
-
- return False
-
- for key, delta in gem.param_update.items():
-
- if not isinstance(delta, (int, float)):
-
- return False
-
- current = self.parameters.get(key, 1.0)
-
- self.parameters[key] = max(0.1, min(10.0, current + float(delta)))
-
- return True
- def save(self, path: Path) -> None:
-
- path.parent.mkdir(parents=True, exist_ok=True)
-
- path.write_text(json.dumps(self.parameters, indent=2), encoding='utf-8')
+from __future__ import annotations
+
+import json
+from dataclasses import dataclass, field
+from pathlib import Path
+
+from prgx_ag.schemas import GemOfWisdom
+
+_DEFAULT_PARAMETERS: dict[str, float] = {
+    "stability": 1.0,
+    "efficiency": 1.0,
+}
+
+
+def _coerce_parameters(raw: object) -> dict[str, float]:
+    parameters = dict(_DEFAULT_PARAMETERS)
+
+    if not isinstance(raw, dict):
+        return parameters
+
+    for key, value in raw.items():
+        if isinstance(key, str) and isinstance(value, (int, float)):
+            parameters[key] = max(0.1, min(10.0, float(value)))
+
+    return parameters
+
+
+@dataclass(slots=True)
+class LearningState:
+    parameters: dict[str, float] = field(default_factory=lambda: dict(_DEFAULT_PARAMETERS))
+
+    @classmethod
+    def load(cls, path: Path) -> "LearningState":
+        if not path.exists():
+            return cls()
+
+        try:
+            raw = json.loads(path.read_text(encoding="utf-8"))
+        except (OSError, json.JSONDecodeError):
+            return cls()
+
+        return cls(parameters=_coerce_parameters(raw))
+
+    def apply_gem(self, gem: GemOfWisdom) -> bool:
+        if not gem.safe_to_apply:
+            return False
+
+        for key, delta in gem.param_update.items():
+            if not isinstance(delta, (int, float)):
+                return False
+
+            current = self.parameters.get(key, 1.0)
+            self.parameters[key] = max(0.1, min(10.0, current + float(delta)))
+
+        return True
+
+    def save(self, path: Path) -> None:
+        path.parent.mkdir(parents=True, exist_ok=True)
+        path.write_text(
+            json.dumps(self.parameters, indent=2, sort_keys=True),
+            encoding="utf-8",
+        )

diff --git a/src/prgx_ag/orchestrator/nexus.py b/src/prgx_ag/orchestrator/nexus.py
--- a/src/prgx_ag/orchestrator/nexus.py
+++ b/src/prgx_ag/orchestrator/nexus.py
@@
-from __future__ import annotations
-
-import asyncio
-
-import logging
-
-from pathlib import Path
-
-from prgx_ag.agents import PRGX1Sentry, PRGX2Mechanic, PRGX3Diplomat
-
-from prgx_ag.config import RuntimePaths, Settings, parse_path_list
-
-from prgx_ag.core import AetherBus
-
-from prgx_ag.core.events import EXECUTE_FIX, RSI_FEEDBACK
-
-from prgx_ag.policy import PatimokkhaChecker
-
-from prgx_ag.rsi import LearningState, RSIEngine
-
-from prgx_ag.rsi.gems import append_gem_log
-
-class PRGXAGNexus:
- def __init__(self, settings: Settings) -> None:
- self.settings = settings
- self.repo_root = Path(settings.repo_root).resolve()
- self.logger = logging.getLogger(self.__class__.__name__)
- self.bus = AetherBus(history_size=settings.event_history_size)
- self.checker = PatimokkhaChecker()
- defaults = RuntimePaths()
- allowed = parse_path_list(settings.allowed_write_paths, defaults.allowed)
- protected = parse_path_list(settings.protected_paths, defaults.protected)
- self.prgx1 = PRGX1Sentry(self.bus, root=self.repo_root)
- self.prgx2 = PRGX2Mechanic(self.bus, root=self.repo_root, checker=self.checker, allowed_paths=allowed, protected_paths=protected, dry_run=settings.dry_run)
- self.prgx3 = PRGX3Diplomat(agent_id='PRGX3', role='Diplomat', bus=self.bus)
- self.rsi_engine = RSIEngine()
- self.learning_state = LearningState()
- self._running = False
- async def wire_event_subscriptions(self) -> None:
- await self.prgx3.start()
- await self.bus.subscribe(EXECUTE_FIX, self._handle_execute_fix)
- async def wire_subscriptions(self) -> None:
- # backward compatibility
- await self.wire_event_subscriptions()
- async def _handle_execute_fix(self, payload: dict[str, object]) -> None:
- findings = payload.get('findings', {})
- target = str(findings.get('target', self.repo_root)) if isinstance(findings, dict) else str(self.repo_root)
- outcome = await self.prgx2.apply_shadow_fix(target, payload)
- await self.prgx3.report_result(outcome)
- gem = self.rsi_engine.analyze(outcome)
- if gem and self.learning_state.apply_gem(gem):
- self.learning_state.save(self.repo_root / '.prgx-ag/state/learning_state.json')
- append_gem_log(self.repo_root / '.prgx-ag/state/gem_log.json', gem)
- await self.bus.publish(RSI_FEEDBACK, {'gem': gem.model_dump()})
- async def run_self_healing_cycle(self) -> None:
- await self.prgx1.publish_issue_report()
- async def run_scan_only(self) -> dict[str, object]:
- return self.prgx1.scan_entropy()
- async def run_once(self) -> None:
- await self.wire_event_subscriptions()
- await self.run_self_healing_cycle()
- async def run_continuous(self, interval_seconds: int = 10) -> None:
- await self.wire_event_subscriptions()
- self._running = True
- while self._running:
- await self.run_self_healing_cycle()
- await asyncio.sleep(interval_seconds)
- async def shutdown(self) -> None:
- self._running = False
- PRGX_AG_Nexus = PRGXAGNexus
+from __future__ import annotations
+
+import asyncio
+import logging
+from pathlib import Path
+
+from prgx_ag.agents import PRGX1Sentry, PRGX2Mechanic, PRGX3Diplomat
+from prgx_ag.config import RuntimePaths, Settings, parse_path_list
+from prgx_ag.core import AetherBus
+from prgx_ag.core.events import EXECUTE_FIX, RSI_FEEDBACK
+from prgx_ag.policy import PatimokkhaChecker
+from prgx_ag.rsi import LearningState, RSIEngine
+from prgx_ag.rsi.gems import append_gem_log
+
+
+class PRGXAGNexus:
+    def __init__(self, settings: Settings) -> None:
+        self.settings = settings
+        self.repo_root = Path(settings.repo_root).resolve()
+        self.logger = logging.getLogger(self.__class__.__name__)
+        self.bus = AetherBus(history_size=settings.event_history_size)
+        self.checker = PatimokkhaChecker()
+        self.state_path = self.repo_root / ".prgx-ag/state/learning_state.json"
+
+        defaults = RuntimePaths()
+        allowed = parse_path_list(settings.allowed_write_paths, defaults.allowed)
+        protected = parse_path_list(settings.protected_paths, defaults.protected)
+
+        self.prgx1 = PRGX1Sentry(self.bus, root=self.repo_root)
+        self.prgx2 = PRGX2Mechanic(
+            self.bus,
+            root=self.repo_root,
+            checker=self.checker,
+            allowed_paths=allowed,
+            protected_paths=protected,
+            dry_run=settings.dry_run,
+        )
+        self.prgx3 = PRGX3Diplomat(
+            bus=self.bus,
+            checker=self.checker,
+            agent_id="PRGX3",
+            role="Diplomat",
+        )
+        self.rsi_engine = RSIEngine()
+        self.learning_state = LearningState.load(self.state_path)
+        self._running = False
+
+    async def wire_event_subscriptions(self) -> None:
+        await self.prgx3.start()
+        await self.bus.subscribe(EXECUTE_FIX, self._handle_execute_fix)
+
+    async def wire_subscriptions(self) -> None:
+        # backward compatibility
+        await self.wire_event_subscriptions()
+
+    async def _handle_execute_fix(self, payload: dict[str, object]) -> None:
+        findings = payload.get("findings", {})
+        target = (
+            str(findings.get("target", self.repo_root))
+            if isinstance(findings, dict)
+            else str(self.repo_root)
+        )
+
+        outcome = await self.prgx2.apply_shadow_fix(target, payload)
+        await self.prgx3.report_result(outcome)
+
+        gem = self.rsi_engine.analyze(outcome)
+        if gem and self.learning_state.apply_gem(gem):
+            self.learning_state.save(self.state_path)
+            append_gem_log(self.repo_root / ".prgx-ag/state/gem_log.json", gem)
+            await self.bus.publish(RSI_FEEDBACK, {"gem": gem.model_dump()})
+
+    async def run_self_healing_cycle(self) -> dict[str, object]:
+        return await self.prgx1.publish_issue_report()
+
+    async def run_scan_only(self) -> dict[str, object]:
+        return self.prgx1.scan_entropy()
+
+    async def run_once(self) -> None:
+        await self.wire_event_subscriptions()
+        await self.run_self_healing_cycle()
+
+    async def run_continuous(self, interval_seconds: int = 10) -> None:
+        await self.wire_event_subscriptions()
+        self._running = True
+
+        while self._running:
+            await self.run_self_healing_cycle()
+            await asyncio.sleep(interval_seconds)
+
+    async def shutdown(self) -> None:
+        self._running = False
+
+
+PRGX_AG_Nexus = PRGXAGNexus
