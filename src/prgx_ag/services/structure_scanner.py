from pathlib import Path


def detect_structure_issues(root: Path) -> list[str]:
    issues: list[str] = []
    critical = [root / "README.md", root / "src", root / "tests"]
    for path in critical:
        if not path.exists():
            issues.append(f"Missing critical path: {path.name}")
    package_root = root / "src" / "prgx_ag"
    if package_root.exists() and not (package_root / "__init__.py").exists():
        issues.append("Missing __init__.py in prgx_ag package")
    return issues
