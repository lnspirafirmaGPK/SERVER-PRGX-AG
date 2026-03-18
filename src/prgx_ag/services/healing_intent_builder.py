from __future__ import annotations

from posixpath import normpath
from typing import Any

DEFAULT_VERIFICATION_COMMANDS = ["compileall", "pytest", "ruff", "mypy"]


FixPlanEntry = dict[str, Any]


def _normalize_rel_path(value: str) -> str | None:
    """
    Normalize a repository-relative path and reject unsafe forms.

    Rejected cases:
    - empty path
    - absolute path
    - parent traversal (..)
    - current directory only
    """
    raw = value.strip().replace("\\", "/")
    if not raw:
        return None

    normalized = normpath(raw).replace("\\", "/")
    normalized = normalized.lstrip("./")

    if not normalized or normalized == ".":
        return None

    if normalized.startswith("/"):
        return None

    if normalized == ".." or normalized.startswith("../") or "/../" in normalized:
        return None

    return normalized


def _make_fix(
    path: str,
    *,
    content: str = "",
    fix_class: str,
    rationale: str,
    verification_commands: list[str] | None = None,
    rollback_hint: str | None = None,
    source_issue: str,
) -> FixPlanEntry | None:
    normalized_path = _normalize_rel_path(path)
    if normalized_path is None:
        return None

    return {
        "path": normalized_path,
        "content": content,
        "fix_class": fix_class,
        "rationale": rationale,
        "verification_commands": verification_commands or DEFAULT_VERIFICATION_COMMANDS.copy(),
        "rollback_hint": rollback_hint or f"Revert {normalized_path} if the package marker is not required.",
        "source_issue": source_issue,
    }


def _build_fix_for_missing_init(issue: str) -> FixPlanEntry | None:
    prefix = "Missing __init__.py in "
    if not issue.startswith(prefix):
        return None

    folder = _normalize_rel_path(issue.replace(prefix, "", 1))
    if folder is None:
        return None

    # จำกัด auto-fix เฉพาะ package path ใน src/ เพื่อลดความเสี่ยง
    if not (folder == "src" or folder.startswith("src/")):
        return None

    target_path = f"{folder}/__init__.py"
    return _make_fix(
        target_path,
        content="",
        fix_class="structural.package_marker",
        rationale="Restore the missing Python package marker required by the expected source tree.",
        rollback_hint=f"Delete {target_path} only if the directory should stop behaving as a Python package.",
        source_issue=issue,
    )


def _build_fix_for_missing_expected_path(issue: str) -> FixPlanEntry | None:
    """
    Auto-fix เฉพาะ expected path ที่เป็น __init__.py เท่านั้น
    เพื่อไม่เดาสุ่มสร้างไฟล์/โฟลเดอร์อื่นที่อาจต้องมีเนื้อหาเฉพาะ.
    """
    prefix = "Missing expected path: "
    if not issue.startswith(prefix):
        return None

    rel_path = _normalize_rel_path(issue.replace(prefix, "", 1))
    if rel_path is None:
        return None

    if not rel_path.endswith("/__init__.py") and rel_path != "__init__.py":
        return None

    if not (rel_path == "__init__.py" or rel_path.startswith("src/")):
        return None

    return _make_fix(
        rel_path,
        content="",
        fix_class="structural.expected_path",
        rationale="Restore a manifest-declared __init__.py path without inventing non-empty file contents.",
        rollback_hint=f"Revert {rel_path} if the manifest entry is intentionally being retired.",
        source_issue=issue,
    )


def _dedupe_fixes(fixes: list[FixPlanEntry]) -> list[FixPlanEntry]:
    deduped: list[FixPlanEntry] = []
    seen: set[tuple[str, str, str]] = set()

    for fix in fixes:
        path = str(fix.get("path", ""))
        content = str(fix.get("content", ""))
        fix_class = str(fix.get("fix_class", ""))
        key = (path, content, fix_class)

        if key in seen:
            continue

        seen.add(key)
        deduped.append(
            {
                "path": path,
                "content": content,
                "fix_class": fix_class,
                "rationale": str(fix.get("rationale", "")),
                "verification_commands": list(fix.get("verification_commands", [])),
                "rollback_hint": str(fix.get("rollback_hint", "")),
                "source_issue": str(fix.get("source_issue", "")),
            }
        )

    return deduped


def build_fix_plan(findings: dict[str, Any]) -> list[FixPlanEntry]:
    """
    Create explicit and minimal fix operations from PRGX1 findings.

    รูปแบบผลลัพธ์คงแกนหลักเป็นรายการ fix ที่มี path/content
    และเพิ่ม metadata เพื่อให้ workflow governance และ PR narrative ใช้งานต่อได้.

    แนวทางความปลอดภัย:
    - ไม่สร้าง fix จาก dependency_issues หรือ integrity_issues อัตโนมัติ
    - ไม่สร้าง fix จาก finding ที่กำกวม เช่น Missing critical path
    - สร้างเฉพาะไฟล์ที่ปลอดภัยและเดาเนื้อหาได้ เช่น __init__.py ว่าง
    - normalize path และกัน path traversal ตั้งแต่ต้นทาง
    """
    if not isinstance(findings, dict):
        return []

    structural_issues = findings.get("structural_issues", [])
    if not isinstance(structural_issues, list):
        return []

    fix_plan: list[FixPlanEntry] = []

    for issue in structural_issues:
        if not isinstance(issue, str):
            continue

        fix = (
            _build_fix_for_missing_init(issue)
            or _build_fix_for_missing_expected_path(issue)
        )

        if fix is not None:
            fix_plan.append(fix)

    return _dedupe_fixes(fix_plan)
