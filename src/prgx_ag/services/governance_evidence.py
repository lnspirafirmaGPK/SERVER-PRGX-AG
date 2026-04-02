from __future__ import annotations

import base64
import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _sign_payload(canonical_bytes: bytes) -> dict[str, Any]:
    """Sign the canonical payload using RSA-PSS or ECDSA.

    In production, this should load a configured private key and use
    cryptography library for RSA-PSS or ECDSA signing.
    For now, this is a placeholder that demonstrates the expected structure.
    """
    try:
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import padding, rsa
        from cryptography.hazmat.backends import default_backend

        # In production, load key from secure storage (e.g., env var, key vault)
        # For now, generate an ephemeral key (NOT SECURE for production)
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )

        signature_bytes = private_key.sign(
            canonical_bytes,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        public_key = private_key.public_key()
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')

        return {
            'algorithm': 'RSA-PSS-SHA256',
            'signature': base64.b64encode(signature_bytes).decode('utf-8'),
            'key_id': 'ephemeral-key',
            'public_key': public_pem,
        }
    except ImportError:
        # Fallback if cryptography library not available
        # This maintains backward compatibility but is NOT a real signature
        digest = hashlib.sha256(canonical_bytes).hexdigest()
        return {
            'algorithm': 'sha256',
            'digest': digest,
            'warning': 'cryptography library not available, using digest fallback',
        }


def _read_json(path: Path) -> Any:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except (json.JSONDecodeError, ValueError):
        return None


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
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
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
    candidate = (repo_root / medical_findings_path).resolve()
    try:
        candidate.relative_to(repo_root.resolve())
        medical_path = candidate
    except ValueError:
        raise ValueError(f"medical_findings_path must be inside repo_root: {medical_findings_path}")
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
    signature_data = _sign_payload(canonical.encode('utf-8'))

    signed_bundle = {
        **payload,
        'signature': signature_data,
    }

    stamp = _utc_now().strftime('%Y%m%d-%H%M%S')
    out_path = evidence_dir / f'governance-evidence-{stamp}.json'
    out_path.write_text(json.dumps(signed_bundle, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return out_path
