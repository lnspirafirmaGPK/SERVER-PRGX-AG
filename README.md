# PRGX-AG: Governed Self-Healing Core

PRGX-AG is a hybrid architecture where:
- `.github/workflows/` is the external GitHub orchestration layer.
- `.prgx-ag/` is the internal governance/manifest/state layer.
- `src/prgx_ag/` is the executable Python 3.11+ self-healing engine.

## System Architecture Diagram (Database-State Aligned)

```mermaid
erDiagram
    NEXUS ||--o{ AUDIT_LOG : writes
    NEXUS ||--|| PATIMOKKHA_POLICY : enforces
    NEXUS ||--|| RULESET_POLICY : validates
    NEXUS ||--|| TRANSLATION_MATRIX : maps_intent
    NEXUS ||--|| EXPECTED_STRUCTURE : checks
    NEXUS ||--|| CRITICAL_FILES : monitors
    NEXUS ||--|| WRITABLE_PATHS : restricts_write
    NEXUS ||--|| PROTECTED_PATHS : blocks_write
    NEXUS ||--|| LEARNING_STATE : updates
    NEXUS ||--o{ GEM_LOG : appends

    AUDIT_LOG {
      jsonl ts
      string topic
      string outcome
      string actor
    }
    PATIMOKKHA_POLICY {
      yaml version
      array blocked_intents
      array guardrails
    }
    RULESET_POLICY {
      yaml version
      array governance_rules
    }
    TRANSLATION_MATRIX {
      yaml issue_type
      string intent_type
      string severity
    }
    EXPECTED_STRUCTURE {
      yaml expected_paths
      array required_dirs
    }
    CRITICAL_FILES {
      yaml file_path
      string integrity_mode
    }
    WRITABLE_PATHS {
      yaml allowed_path
      string reason
    }
    PROTECTED_PATHS {
      yaml protected_path
      string risk_level
    }
    LEARNING_STATE {
      json cycle_count
      json success_rate
      json bounded_feedback
    }
    GEM_LOG {
      json ts
      json signal
      json adaptation
    }
```

## System Status (Data/State Structure)

| Subsystem | Source of truth | Status detail |
|---|---|---|
| Governance policy | `.prgx-ag/policy/*.yaml` | Blocks destructive intents and protected-path writes |
| Operational workflows | `.prgx-ag/workflows/*.yaml` | Includes scan-only and self-heal cycles |
| Structure contract | `.prgx-ag/manifests/*.yaml` | Expected/critical/writable/protected definitions |
| Runtime learning | `.prgx-ag/state/*.json` | Bounded RSI state and gem log |
| Audit trail | `.prgx-ag/audit/audit_log.jsonl` | Reserved for violation and cycle evidence |

## PRGX Triad
- **PRGX1 Sentry**: scans dependencies + structure, emits `porisjem.issue_reported`.
- **PRGX3 Diplomat**: translates findings into healing intents and narratives.
- **PRGX2 Mechanic**: only writer; executes approved, reversible fixes inside allowlisted paths.

## Patimokkha Governance
Blocked examples: `delete_core`, `shutdown_nexus`, `exploit`, destructive recursion, unsafe infinite loops, mass deletion, protected-path modification.

## Event Topics
- `porisjem.issue_reported`
- `porisjem.intent_translated`
- `porisjem.execute_fix`
- `porisjem.fix_completed`
- `porisjem.audit_violation`
- `porisjem.rsi_feedback`

## Active/Future Backlog (EN)
This list is intentionally limited to active and future work.

1. Add JSON Schema validation CI check for `.prgx-ag/state/*.json` and policy manifests before merge.
2. Add drift-detection report that compares runtime writes against `writable_paths.yaml` and opens governance alerts.
3. Add policy simulation mode (`--simulate-policy`) for PRGX3 intent review without execution.
4. Add architecture export command to generate Mermaid + inventory snapshot from manifests.
5. Add lightweight dashboard page for cycle metrics (success rate, blocked intents, fix latency).

## งานคงค้าง/แผนต่อยอด (TH)
รายการนี้จำกัดไว้เฉพาะงานที่กำลังดำเนินการและงานในอนาคตเท่านั้น

1. เพิ่ม CI สำหรับตรวจ JSON Schema ของ `.prgx-ag/state/*.json` และไฟล์ policy/manifest ก่อน merge
2. เพิ่มรายงานตรวจจับ drift โดยเทียบการเขียนไฟล์จริงกับ `writable_paths.yaml` และแจ้งเตือน governance
3. เพิ่มโหมดจำลองนโยบาย (`--simulate-policy`) เพื่อให้ PRGX3 ตรวจ intent ได้โดยไม่สั่งแก้จริง
4. เพิ่มคำสั่ง export สถาปัตยกรรม (Mermaid + inventory) จาก manifest อัตโนมัติ
5. เพิ่มหน้า dashboard เบื้องต้นสำหรับ metric รอบการทำงาน เช่น success rate, blocked intents, fix latency

## Local Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

## Run
```bash
python -m prgx_ag.main --once
python -m prgx_ag.main --continuous --interval 10
python -m prgx_ag.main --scan-only
```

## Safe PR-first operation
- Use `PRGX_AG_DRY_RUN=true` by default.
- Workflows run scan/heal in non-destructive mode and produce artifacts.
- Tokens/keys are read from env/GitHub Secrets only.

## Test
```bash
pytest
```
