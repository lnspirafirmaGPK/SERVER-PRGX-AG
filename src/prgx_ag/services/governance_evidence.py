from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _read_json(path: Path) -> Any:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding='utf-8'))


def _read_audit_slice(audit_log: Path, *, hours: int) -> list[dict[str, Any]]:
    if not audit_log.exists():
        return []

    cutoff = _utc_now() - timedelta(hours=max(hours, 1))
    rows: list[dict[str, Any]] = []
    for line in audit_log.read_text(encoding='utf-8').splitlines():
        record = line.strip()
        if not record:
            continue
        try:
            payload = json.loads(record)
        except json.JSONDecodeError:
            continue
        ts_raw = payload.get('ts')
        if not isinstance(ts_raw, str):
            continue
        try:
            ts = datetime.fromisoformat(ts_raw.replace('Z', '+00:00'))
        except ValueError:
            continue
        if ts >= cutoff:
            rows.append(payload)
    return rows


def append_audit_event(audit_log: Path, *, event: str, actor: str, details: dict[str, Any]) -> None:
    audit_log.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        'ts': _utc_now().isoformat(),
        'event': event,
        'actor': actor,
        'details': details,
    }
    with audit_log.open('a', encoding='utf-8') as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + '\n')


def create_signed_governance_evidence_bundle(
    repo_root: Path,
    *,
    audit_window_hours: int,
    fix_plan_metadata: dict[str, Any],
    medical_findings_path: str,
    profile_name: str,
) -> Path:
    audit_log = repo_root / '.prgx-ag/audit/audit_log.jsonl'
    medical_path = repo_root / medical_findings_path
    evidence_dir = repo_root / '.prgx-ag/artifacts/compliance'
    evidence_dir.mkdir(parents=True, exist_ok=True)

    medical_findings = _read_json(medical_path)
    if not isinstance(medical_findings, list):
        medical_findings = []

    audit_slice = _read_audit_slice(audit_log, hours=audit_window_hours)

    payload = {
        'created_at': _utc_now().isoformat(),
        'profile': profile_name,
        'audit_window_hours': audit_window_hours,
        'audit_records': audit_slice,
        'fix_plan_metadata': fix_plan_metadata,
        'medical_research_findings': medical_findings,
        'compliance_statement': 'Governance evidence bundle generated from bounded PRGX-AG runtime records.',
    }
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    signature = hashlib.sha256(canonical.encode('utf-8')).hexdigest()

    signed_bundle = {
        **payload,
        'signature': {
            'algorithm': 'sha256',
            'digest': signature,
        },
    }

    stamp = _utc_now().strftime('%Y%m%d-%H%M%S')
    out_path = evidence_dir / f'governance-evidence-{stamp}.json'
    out_path.write_text(json.dumps(signed_bundle, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return out_path
