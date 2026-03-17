from datetime import datetime, timezone
from uuid import uuid4

from prgx_ag.schemas import EthicalStatus, Intent

TERM_MAP = {
    "Parajika": "SYSTEM_HALT_IMMEDIATE",
    "Nirodha": "GRACEFUL_SHUTDOWN",
    "Sati": "ENABLE_DEEP_MONITORING",
    "Metta": "OPTIMIZE_UX_RESPONSE",
    "Sanghadisesa": "SUSPEND_AND_AUDIT",
}

STATUS_MAP = {
    EthicalStatus.CLEAN: "System stable and ethically aligned.",
    EthicalStatus.MINOR_INFRACTION: "Minor breach detected; corrective guidance required.",
    EthicalStatus.MAJOR_VIOLATION: "Major governance breach; constrained remediation required.",
    EthicalStatus.PARAJIKA: "Critical violation; immediate halt and audit required.",
}


def translate_internal_term(term: str) -> str:
    return TERM_MAP.get(term, "UNMAPPED_TERM")


def translate_status(status: EthicalStatus) -> str:
    return STATUS_MAP[status]


def build_healing_intent(findings: dict) -> Intent:
    return Intent(
        id=f"intent-{uuid4()}",
        source_agent="PRGX3",
        description=f"Heal findings: {findings.get('summary', 'unknown')}",
        target_firma=findings.get("target", "repository"),
        metadata=findings,
        timestamp=datetime.now(timezone.utc),
    )
