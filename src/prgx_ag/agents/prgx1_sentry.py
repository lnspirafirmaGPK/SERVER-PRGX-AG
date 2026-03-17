from __future__ import annotations

from pathlib import Path

from prgx_ag.core import BaseAgent
from prgx_ag.core.events import ISSUE_REPORTED
from prgx_ag.services.dependency_scanner import scan_dependency_anomalies
from prgx_ag.services.integrity_scanner import scan_integrity_drift
from prgx_ag.services.structure_scanner import detect_structure_issues


class PRGX1Sentry(BaseAgent):
    """Read-only guardian eye (Anicca observer)."""

    def __init__(self, bus, root: Path) -> None:
        super().__init__(agent_id='PRGX1', role='Sentry', bus=bus)
        self.root = root

    def detect_outdated_dependencies(self) -> list[str]:
        return scan_dependency_anomalies(self.root)

    def detect_structural_anomalies(self) -> list[str]:
        return detect_structure_issues(self.root)

    def detect_integrity_drift(self) -> list[str]:
        return scan_integrity_drift(self.root)

    def scan_entropy(self) -> dict[str, object]:
        dep_issues = self.detect_outdated_dependencies()
        structural_issues = self.detect_structural_anomalies()
        integrity_issues = self.detect_integrity_drift()
        all_issues = dep_issues + structural_issues + integrity_issues
        return {
            'summary': 'repository scan completed',
            'target': str(self.root),
            'dependency_issues': dep_issues,
            'structural_issues': structural_issues,
            'integrity_issues': integrity_issues,
            'requires_fix': bool(all_issues),
        }

    async def publish_issue_report(self) -> dict[str, object]:
        report = self.scan_entropy()
        await self.publish(ISSUE_REPORTED, report)
        return report
