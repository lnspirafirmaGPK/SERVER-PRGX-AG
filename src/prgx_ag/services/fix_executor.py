from __future__ import annotations

from fnmatch import fnmatch
from pathlib import Path
from typing import Any

from prgx_ag.schemas import ProcessingOutcome


FixPlanEntry = dict[str, Any]


def _is_under(path: Path, base: Path) -> bool:
    try:
        path.resolve().relative_to(base.resolve())
        return True
    except ValueError:
        return False


def _normalize_rel_path(rel_path: str) -> str:
    return rel_path.replace("\\", "/").lstrip("./")


def _matches_protected(rel_path: str, protected_paths: list[str]) -> bool:
    normalized = _normalize_rel_path(rel_path)

    for protected in protected_paths:
        pattern = protected.replace("\\", "/").rstrip("/")
        if not pattern:
            continue

        # exact file or directory prefix block
        if normalized == pattern or normalized.startswith(f"{pattern}/"):
            return True

        # wildcard block เช่น .env.*, *.pem, *.key
        if fnmatch(normalized, pattern) or fnmatch(f"./{normalized}", pattern):
            return True

    return False


def _collect_fix_metadata(fixes: list[FixPlanEntry]) -> dict[str, list[str]]:
    fix_classes: list[str] = []
    verification_commands: list[str] = []
    rollback_hints: list[str] = []

    for fix in fixes:
        fix_class = str(fix.get("fix_class", "")).strip()
        if fix_class and fix_class not in fix_classes:
            fix_classes.append(fix_class)

        raw_commands = fix.get("verification_commands", [])
        if isinstance(raw_commands, list):
            for command in raw_commands:
                text = str(command).strip()
                if text and text not in verification_commands:
                    verification_commands.append(text)

        rollback_hint = str(fix.get("rollback_hint", "")).strip()
        if rollback_hint and rollback_hint not in rollback_hints:
            rollback_hints.append(rollback_hint)

    return {
        "fix_classes": fix_classes,
        "verification_commands": verification_commands,
        "rollback_hints": rollback_hints,
    }


def apply_safe_fixes(
    repo_root: Path,
    fixes: list[FixPlanEntry],
    allowed_paths: list[str],
    protected_paths: list[str],
    envelope_id: str,
    dry_run: bool,
) -> ProcessingOutcome:
    changed: list[str] = []
    metadata = _collect_fix_metadata(fixes)

    for fix in fixes:
        rel_path = str(fix.get("path", "")).strip()
        if not rel_path:
            return ProcessingOutcome(
                agent_name="PRGX2",
                envelope_id=envelope_id,
                success=False,
                execution_time=0.0,
                message="Fix entry missing path",
                details=metadata,
            )

        rel_target = Path(rel_path)
        if rel_target.is_absolute():
            return ProcessingOutcome(
                agent_name="PRGX2",
                envelope_id=envelope_id,
                success=False,
                execution_time=0.0,
                message=f"Absolute path blocked: {rel_path}",
                details=metadata,
            )

        normalized_rel_path = _normalize_rel_path(rel_path)
        target = (repo_root / normalized_rel_path).resolve()

        if _matches_protected(normalized_rel_path, protected_paths):
            return ProcessingOutcome(
                agent_name="PRGX2",
                envelope_id=envelope_id,
                success=False,
                execution_time=0.0,
                message=f"Protected path blocked: {normalized_rel_path}",
                details=metadata,
            )

        allowed = any(_is_under(target, (repo_root / p).resolve()) for p in allowed_paths)
        if not allowed:
            return ProcessingOutcome(
                agent_name="PRGX2",
                envelope_id=envelope_id,
                success=False,
                execution_time=0.0,
                message=f"Path not allowed: {normalized_rel_path}",
                details=metadata,
            )

        if not dry_run:
            target.parent.mkdir(parents=True, exist_ok=True)
            content = str(fix.get("content", ""))
            target.write_text(content, encoding="utf-8")

        changed.append(normalized_rel_path)

    return ProcessingOutcome(
        agent_name="PRGX2",
        envelope_id=envelope_id,
        success=True,
        execution_time=0.01,
        message="Safe fixes applied",
        details={
            "changed": changed,
            "dry_run": dry_run,
            **metadata,
        },
    )
