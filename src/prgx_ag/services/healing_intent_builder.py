from __future__ import annotations

from posixpath import normpath
from typing import Any


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


def _make_fix(path: str, content: str = "") -> dict[str, str] | None:
    normalized_path = _normalize_rel_path(path)
    if normalized_path is None:
        return None

    return {
        "path": normalized_path,
        "content": content,
    }


def _build_fix_for_missing_init(issue: str) -> dict[str, str] | None:
    prefix = "Missing __init__.py in "
    if not issue.startswith(prefix):
        return None

    folder = _normalize_rel_path(issue.replace(prefix, "", 1))
    if folder is None:
        return None

    # จำกัด auto-fix เฉพาะ package path ใน src/ เพื่อลดความเสี่ยง
    if not (folder == "src" or folder.startswith("src/")):
        return None

    return _make_fix(f"{folder}/__init__.py", "")


def _build_fix_for_missing_expected_path(issue: str) -> dict[str, str] | None:
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

    return _make_fix(rel_path, "")


def _dedupe_fixes(fixes: list[dict[str, str]]) -> list[dict[str, str]]:
    deduped: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()

    for fix in fixes:
        path = fix.get("path", "")
        content = fix.get("content", "")
        key = (path, content)

        if key in seen:
            continue

        seen.add(key)
        deduped.append(
            {
                "path": path,
                "content": content,
            }
        )

    return deduped


def build_fix_plan(findings: dict[str, Any]) -> list[dict[str, str]]:
    """
    Create explicit and minimal fix operations from PRGX1 findings.

    รูปแบบผลลัพธ์ต้องคงเป็น:
        list[{"path": str, "content": str}]

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

    fix_plan: list[dict[str, str]] = []

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
