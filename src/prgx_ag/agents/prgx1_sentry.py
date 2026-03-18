from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

from prgx_ag.core import BaseAgent
from prgx_ag.core.events import ISSUE_REPORTED
from prgx_ag.services.dependency_scanner import scan_dependency_anomalies
from prgx_ag.services.integrity_scanner import scan_integrity_drift
from prgx_ag.services.structure_scanner import detect_structure_issues


class PRGX1Sentry(BaseAgent):
    """Read-only guardian eye (Anicca observer)."""

    def __init__(self, bus, root: Path) -> None:
        super().__init__(agent_id="PRGX1", role="Sentry", bus=bus)
        self.root = root

    def detect_outdated_dependencies(self) -> list[str]:
        return scan_dependency_anomalies(self.root)

    def detect_structural_anomalies(self) -> list[str]:
        return detect_structure_issues(self.root)

    def detect_integrity_drift(self) -> list[str]:
        return scan_integrity_drift(self.root)

    @staticmethod
    def has_findings(report: Mapping[str, object]) -> bool:
        return bool(report.get("requires_fix", False))

    def scan_entropy(self) -> dict[str, object]:
        dep_issues = self.detect_outdated_dependencies()
        structural_issues = self.detect_structural_anomalies()
        integrity_issues = self.detect_integrity_drift()

        all_issues = dep_issues + structural_issues + integrity_issues
        return {
            "summary": "repository scan completed",
            "target": str(self.root),
            "dependency_issues": dep_issues,
            "structural_issues": structural_issues,
            "integrity_issues": integrity_issues,
            "issue_count": len(all_issues),
            "requires_fix": bool(all_issues),
        }

    async def publish_issue_report(self) -> dict[str, object]:
        report = self.scan_entropy()

        if not self.has_findings(report):
            self.logger.info(
                "No actionable findings detected; skipping %s publish.",
                ISSUE_REPORTED,
            )
            return report

        await self.publish(ISSUE_REPORTED, report)
        return report
