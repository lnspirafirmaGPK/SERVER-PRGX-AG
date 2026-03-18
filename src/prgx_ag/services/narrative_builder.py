from __future__ import annotations

from prgx_ag.schemas import ProcessingOutcome, RepairNarrative


def _coerce_str(value: object, default: str = "n/a") -> str:
    if isinstance(value, str):
        stripped = value.strip()
        return stripped or default
    if value is None:
        return default
    return str(value)


def _coerce_bool(value: object, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "1", "yes", "y", "on"}:
            return True
        if lowered in {"false", "0", "no", "n", "off"}:
            return False
    return default


def _coerce_list_of_str(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    normalized: list[str] = []
    for item in value:
        if isinstance(item, str):
            text = item.strip()
            if text:
                normalized.append(text)
    return normalized


def _details_of(outcome: ProcessingOutcome) -> dict[str, object]:
    return outcome.details if isinstance(outcome.details, dict) else {}


def _mode_label(outcome: ProcessingOutcome) -> str:
    details = _details_of(outcome)
    dry_run = _coerce_bool(details.get("dry_run"), default=False)
    if outcome.success and dry_run:
        return "dry-run"
    if outcome.success:
        return "fix"
    return "blocked"


def _title_for(outcome: ProcessingOutcome) -> str:
    mode = _mode_label(outcome)
    if mode == "dry-run":
        return "Dry-run repair review completed"
    if mode == "fix":
        return "Repair applied successfully"
    return "Repair execution blocked"


def _detected_for(outcome: ProcessingOutcome) -> str:
    details = _details_of(outcome)
    target = _coerce_str(details.get("target"), default="repository")
    audit_reason = _coerce_str(details.get("audit_reason"), default="")
    fix_count = details.get("fix_count")
    fix_classes = ",".join(_coerce_list_of_str(details.get("fix_classes"))) or "none"
    segments: list[str] = [f"Target={target}"]
    if isinstance(fix_count, int):
        segments.append(f"PlannedFixes={fix_count}")
    segments.append(f"FixClasses={fix_classes}")
    if audit_reason and audit_reason != "n/a":
        segments.append(f"Audit={audit_reason}")
    segments.append(f"Message={outcome.message}")
    return " | ".join(segments)


def _repaired_for(outcome: ProcessingOutcome) -> str:
    details = _details_of(outcome)
    changed = _coerce_list_of_str(details.get("changed"))
    dry_run = _coerce_bool(details.get("dry_run"), default=False)
    verification_status = _coerce_str(details.get("verification_status"), default="not-run")
    verification_results = details.get("verification_results") if isinstance(details.get("verification_results"), list) else []
    verified_count = sum(1 for result in verification_results if isinstance(result, dict) and result.get("passed") is True)

    if changed:
        changed_preview = ", ".join(changed[:5])
        if len(changed) > 5:
            changed_preview += f", +{len(changed) - 5} more"
    else:
        changed_preview = "none"

    action = "Validated safe fix set without writing files" if outcome.success and dry_run else "Applied safe fixes" if outcome.success else "No repair applied"
    return f"{action}. Changed={changed_preview} | Verification={verification_status} | VerifiedFixes={verified_count}"


def _learned_for(outcome: ProcessingOutcome) -> str:
    details = _details_of(outcome)
    payload_audit = details.get("payload_audit")
    audit_reason = _coerce_str(details.get("audit_reason"), default="")
    execution_time = f"{outcome.execution_time:.4f}s"
    rollback_hints = _coerce_list_of_str(details.get("rollback_hints"))
    snapshots = details.get("snapshots") if isinstance(details.get("snapshots"), list) else []

    notes: list[str] = [f"ExecutionTime={execution_time}"]
    if audit_reason and audit_reason != "n/a":
        notes.append(f"Guardrail={audit_reason}")
    if isinstance(payload_audit, dict) and payload_audit:
        notes.append("PayloadAudit=present")
    if rollback_hints:
        notes.append(f"RollbackHints={len(rollback_hints)}")
    if snapshots:
        notes.append(f"Snapshots={len(snapshots)}")
    return " | ".join(notes)


def build_narrative(findings: dict[str, object], approved: bool, changed: list[str]) -> str:
    summary = _coerce_str(findings.get("summary"), default="repository scan completed")
    target = _coerce_str(findings.get("target"), default="repository")
    issue_count = findings.get("issue_count", "n/a")
    changed_text = ", ".join(changed) if changed else "none"
    return f"Detected={summary} | Target={target} | IssueCount={issue_count} | Approved={approved} | Changed={changed_text}"


def build_repair_narrative(outcome: ProcessingOutcome) -> RepairNarrative:
    return RepairNarrative(title=_title_for(outcome), detected=_detected_for(outcome), repaired=_repaired_for(outcome), learned=_learned_for(outcome))


def build_commit_style_narrative(outcome: ProcessingOutcome) -> str:
    mode = _mode_label(outcome)
    details = _details_of(outcome)
    changed = _coerce_list_of_str(details.get("changed"))
    changed_text = ", ".join(changed[:5]) if changed else "none"
    if len(changed) > 5:
        changed_text += f", +{len(changed) - 5} more"
    target = _coerce_str(details.get("target"), default="repository")
    fix_count = details.get("fix_count")
    fix_count_text = str(fix_count) if isinstance(fix_count, int) else "n/a"
    fix_classes = ",".join(_coerce_list_of_str(details.get("fix_classes"))) or "none"
    verification_status = _coerce_str(details.get("verification_status"), default="not-run")
    revertibility = len(details.get("snapshots", [])) if isinstance(details.get("snapshots"), list) else 0
    return (
        f"{mode}: {outcome.message} | target={target} | fixes={fix_count_text} | "
        f"fix_classes={fix_classes} | verification={verification_status} | revertible={revertibility} | "
        f"changed={changed_text} | elapsed={outcome.execution_time:.4f}s | envelope={outcome.envelope_id}"
    )
