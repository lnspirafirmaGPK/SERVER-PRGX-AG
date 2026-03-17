from __future__ import annotations

from pathlib import Path

import yaml

from prgx_ag.utils.hashes import sha256_file


def scan_integrity_drift(root: Path) -> list[str]:
    """Read-only integrity scan against optional baseline hashes."""

    issues: list[str] = []
    critical_manifest = root / '.prgx-ag/manifests/critical_files.yaml'
    if not critical_manifest.exists():
        return issues

    data = yaml.safe_load(critical_manifest.read_text(encoding='utf-8')) or {}
    files: list[str] = data.get('critical_files', data.get('files', []))
    baseline_hashes: dict[str, str] = data.get('baseline_hashes', {})

    for rel_path in files:
        full_path = root / rel_path
        if not full_path.exists():
            issues.append(f'Missing critical file: {rel_path}')
            continue
        expected = baseline_hashes.get(rel_path)
        if expected:
            current = sha256_file(full_path)
            if current != expected:
                issues.append(f'Integrity drift detected: {rel_path}')
    return issues
