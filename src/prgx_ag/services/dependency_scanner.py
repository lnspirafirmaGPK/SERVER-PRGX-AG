from pathlib import Path


def find_dependency_manifests(root: Path) -> list[Path]:
    candidates = ["pyproject.toml", "requirements.txt", "requirements-dev.txt", "package.json"]
    return [root / name for name in candidates if (root / name).exists()]
