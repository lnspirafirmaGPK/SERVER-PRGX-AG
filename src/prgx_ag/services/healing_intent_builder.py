from __future__ import annotations

from pathlib import Path
from posixpath import normpath
from typing import Any

from prgx_ag.services.manifest_loader import ManifestLoader

DEFAULT_VERIFICATION_COMMANDS = ["compileall", "pytest", "ruff", "mypy"]
DEFAULT_DEPENDENCY_ALLOWLIST_PATH = ".prgx-ag/allowlists/dependency_policy.yaml"

FixPlanEntry = dict[str, Any]


def _normalize_rel_path(value: str) -> str | None:
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
    validator: str,
    verification_commands: list[str] | None = None,
    rollback_hint: str | None = None,
    source_issue: str,
    metadata: dict[str, Any] | None = None,
) -> FixPlanEntry | None:
    normalized_path = _normalize_rel_path(path)
    if normalized_path is None:
        return None

    return {
        "path": normalized_path,
        "content": content,
        "fix_class": fix_class,
        "validator": validator,
        "rationale": rationale,
        "verification_commands": verification_commands or DEFAULT_VERIFICATION_COMMANDS.copy(),
        "rollback_hint": rollback_hint or f"Revert {normalized_path} if the package marker is not required.",
        "source_issue": source_issue,
        "metadata": metadata or {},
    }


def _build_fix_for_missing_init(issue: str) -> FixPlanEntry | None:
    prefix = "Missing __init__.py in "
    if not issue.startswith(prefix):
        return None

    folder = _normalize_rel_path(issue.replace(prefix, "", 1))
    if folder is None or not (folder == "src" or folder.startswith("src/")):
        return None

    target_path = f"{folder}/__init__.py"
    return _make_fix(
        target_path,
        content="",
        fix_class="create_empty_init",
        validator="validate_empty_init_fix",
        rationale="Restore the missing Python package marker required by the expected source tree.",
        rollback_hint=f"Delete {target_path} only if the directory should stop behaving as a Python package.",
        source_issue=issue,
        metadata={"safety_basis": "Creates only an empty __init__.py within allowlisted src/ package paths."},
    )


def _build_fix_for_missing_expected_path(issue: str) -> FixPlanEntry | None:
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
        fix_class="manifest_sync",
        validator="validate_manifest_sync_fix",
        rationale="Restore a manifest-declared __init__.py path without inventing non-empty file contents.",
        rollback_hint=f"Revert {rel_path} if the manifest entry is intentionally being retired.",
        source_issue=issue,
        metadata={"safety_basis": "Recreates only manifest-declared __init__.py files with empty content."},
    )


def _parse_dependency_bump_issue(issue: str) -> tuple[str, str, str] | None:
    prefix = "Allowlisted dependency bump in "
    if not issue.startswith(prefix):
        return None

    remainder = issue.replace(prefix, "", 1)
    if ":" not in remainder or "->" not in remainder:
        return None

    manifest_part, dependency_part = remainder.split(":", 1)
    package_part, spec_part = dependency_part.split("->", 1)
    manifest_path = _normalize_rel_path(manifest_part)
    package = package_part.strip()
    version_spec = spec_part.strip()

    if manifest_path is None or not package or not version_spec:
        return None
    return manifest_path, package, version_spec


def _load_dependency_policy(repo_root: Path | None) -> dict[str, Any]:
    default_policy = {"manifest_rules": {}, "packages": {}}
    candidates = [candidate for candidate in [repo_root, Path.cwd()] if candidate is not None]

    for candidate in candidates:
        policy_path = candidate / DEFAULT_DEPENDENCY_ALLOWLIST_PATH
        if not policy_path.exists():
            continue

        loader = ManifestLoader(candidate)
        try:
            data = loader.load_dependency_policy()
        except (FileNotFoundError, ValueError):
            continue

        manifest_rules = data.get("manifest_rules")
        packages = data.get("packages")
        if isinstance(manifest_rules, dict) and isinstance(packages, dict):
            return {"manifest_rules": manifest_rules, "packages": packages}

    return default_policy


def _build_dependency_bump_fix(issue: str, dependency_policy: dict[str, Any]) -> FixPlanEntry | None:
    parsed = _parse_dependency_bump_issue(issue)
    if parsed is None:
        return None

    manifest_path, package, version_spec = parsed
    manifest_rules = dependency_policy.get("manifest_rules", {})
    packages = dependency_policy.get("packages", {})
    package_policy = packages.get(package)
    manifest_policy = manifest_rules.get(manifest_path)

    if not isinstance(package_policy, dict) or not isinstance(manifest_policy, dict):
        return None

    allowed_range = str(package_policy.get("allowed_range", "")).strip()
    bump_policy = str(package_policy.get("bump_policy", "")).strip()
    allowed_packages = manifest_policy.get("allowed_packages", [])

    if not allowed_range or not bump_policy or package not in allowed_packages:
        return None
    if version_spec != allowed_range:
        return None

    return _make_fix(
        manifest_path,
        fix_class="dependency_bump",
        validator="validate_dependency_bump_fix",
        rationale=f"Update the allowlisted dependency '{package}' to the preapproved range {version_spec}.",
        rollback_hint=f"Restore the previous {package} requirement in {manifest_path} using the recorded snapshot if downstream compatibility regresses.",
        source_issue=issue,
        metadata={
            "dependency_name": package,
            "dependency_version": version_spec,
            "manifest_path": manifest_path,
            "allowlisted_range": allowed_range,
            "bump_policy": bump_policy,
            "safety_basis": "Only modifies a preapproved dependency and exact range from the repository allowlist.",
        },
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
                "validator": str(fix.get("validator", "")),
                "rationale": str(fix.get("rationale", "")),
                "verification_commands": list(fix.get("verification_commands", [])),
                "rollback_hint": str(fix.get("rollback_hint", "")),
                "source_issue": str(fix.get("source_issue", "")),
                "metadata": dict(fix.get("metadata", {})) if isinstance(fix.get("metadata"), dict) else {},
            }
        )

    return deduped


def build_fix_plan(findings: dict[str, Any], repo_root: Path | None = None) -> list[FixPlanEntry]:
    if not isinstance(findings, dict):
        return []

    structural_issues = findings.get("structural_issues", [])
    dependency_issues = findings.get("dependency_issues", [])
    if not isinstance(structural_issues, list) or not isinstance(dependency_issues, list):
        return []

    dependency_policy = _load_dependency_policy(repo_root or Path.cwd())
    fix_plan: list[FixPlanEntry] = []

    for issue in structural_issues:
        if not isinstance(issue, str):
            continue
        fix = _build_fix_for_missing_init(issue) or _build_fix_for_missing_expected_path(issue)
        if fix is not None:
            fix_plan.append(fix)

    for issue in dependency_issues:
        if not isinstance(issue, str):
            continue
        fix = _build_dependency_bump_fix(issue, dependency_policy)
        if fix is not None:
            fix_plan.append(fix)

    return _dedupe_fixes(fix_plan)
