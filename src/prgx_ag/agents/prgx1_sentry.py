from pathlib import Path

from prgx_ag.core import BaseAgent
from prgx_ag.core.events import ISSUE_REPORTED
from prgx_ag.services.dependency_scanner import find_dependency_manifests
from prgx_ag.services.structure_scanner import detect_structure_issues


class PRGX1Sentry(BaseAgent):
    def __init__(self, bus, root: Path) -> None:
        super().__init__(agent_id="PRGX1", role="Sentry", bus=bus)
        self.root = root

    def detect_outdated_dependencies(self) -> dict:
        manifests = find_dependency_manifests(self.root)
        return {"manifests_found": [str(m.name) for m in manifests], "outdated": []}

    def detect_structural_anomalies(self) -> list[str]:
        return detect_structure_issues(self.root)

    def scan_entropy(self) -> dict:
        deps = self.detect_outdated_dependencies()
        anomalies = self.detect_structural_anomalies()
        return {
            "summary": "entropy scan",
            "target": str(self.root),
            "dependencies": deps,
            "anomalies": anomalies,
            "requires_fix": bool(anomalies),
        }

    async def publish_issue_report(self) -> dict:
        report = self.scan_entropy()
        await self.publish(ISSUE_REPORTED, report)
        return report
