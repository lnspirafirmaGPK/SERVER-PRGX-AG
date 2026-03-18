from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


FindingsSummary = dict[str, Any]


def prepare_pr_branch_name(prefix: str = "prgx/heal") -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    return f"{prefix}-{stamp}"


def _bullet_list(items: list[str], default: str = "- none") -> str:
    normalized = [item.strip() for item in items if isinstance(item, str) and item.strip()]
    return "\n".join(f"- {item}" for item in normalized) or default


def _findings_summary_block(findings_summary: FindingsSummary | None) -> str:
    if not isinstance(findings_summary, dict):
        return "- summary unavailable"

    summary = str(findings_summary.get("summary", "repository scan completed")).strip()
    target = str(findings_summary.get("target", "repository")).strip()
    issue_count = findings_summary.get("issue_count", "n/a")
    return f"- Summary: {summary}\n- Target: {target}\n- Issue count: {issue_count}"


def format_pr_title(
    *,
    findings_summary: FindingsSummary | None,
    audit_result: str,
    verification_result: str,
    fix_classes: list[str],
) -> str:
    target = "repository"
    if isinstance(findings_summary, dict):
        target = str(findings_summary.get("target", target)).strip() or target

    risk = ", ".join(fix_classes) if fix_classes else "governed-repair"
    return f"chore(prgx): heal {target} [{audit_result}; {verification_result}; {risk}]"


def format_pr_body(
    *,
    findings_summary: FindingsSummary | None,
    audit_result: str,
    changed_files: list[str],
    verification_result: str,
    rollback_instructions: list[str],
    fix_classes: list[str],
    verification_commands: list[str],
) -> str:
    return (
        "## PRGX-AG Healing Report\n\n"
        "### Findings summary\n"
        f"{_findings_summary_block(findings_summary)}\n\n"
        "### Audit result\n"
        f"- Status: {audit_result}\n"
        f"- Fix classes: {', '.join(fix_classes) if fix_classes else 'none'}\n\n"
        "### Changed files\n"
        f"{_bullet_list(changed_files)}\n\n"
        "### Verification result\n"
        f"- Status: {verification_result}\n"
        f"- Commands: {', '.join(verification_commands) if verification_commands else 'none'}\n\n"
        "### Rollback instructions\n"
        f"{_bullet_list(rollback_instructions)}\n"
    )
