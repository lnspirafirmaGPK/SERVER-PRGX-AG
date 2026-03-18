# The Porisjem Protocol (ผู้พิทักษ์แห่งความเงียบ)

PRGX-AG is the backend core of **AETHERIUM GENESIS (AGIOpg)**, designed as an **Eternal Immunity** system: self-observing, self-healing, recursively self-improving, and bounded by Buddhist Ethics as Code.

## Inspira vs Firma
- **Inspira (เจตจำนง):** constitutional intent and mission.
- **Firma (โครงสร้าง):** executable implementation that realizes Inspira safely.

The codebase separates intention, observation, interpretation, execution, ethics, and learning into dedicated modules.

## System Architecture Diagram (Database-State Aligned)

The runtime is organized around the `.prgx-ag` state/configuration store, where the Nexus reads manifests and policies, appends audit traces, and updates bounded learning state.

```mermaid
erDiagram
    NEXUS {
      string component "PRGXAGNexus orchestrator"
      string role "coordinates PRGX1, PRGX2, PRGX3"
    }

    AUDIT_LOG {
      jsonl ts
      string event
      string actor
      string details
    }

    LEARNING_STATE {
      float stability
      float efficiency
    }

    GEM_LOG {
      string lesson
      json param_update
      string scope
      boolean safe_to_apply
    }

    PATIMOKKHA_POLICY {
      array blocked_operations
      array principles
      map severity_mapping
    }

    RULESET_POLICY {
      string id
      string description
      string severity
      string action
    }

    TRANSLATION_MATRIX {
      string buddhic_term
      string runtime_action
    }

    EXPECTED_STRUCTURE {
      array paths
    }

    CRITICAL_FILES {
      array files
    }

    WRITABLE_PATHS {
      array paths
    }

    PROTECTED_PATHS {
      array paths
    }

    WORKFLOW_DEFINITIONS {
      string workflow_name
      string trigger_mode
      string repair_scope
    }

    NEXUS ||--o{ AUDIT_LOG : appends
    NEXUS ||--|| LEARNING_STATE : updates
    LEARNING_STATE ||--o{ GEM_LOG : emits
    NEXUS ||--|| PATIMOKKHA_POLICY : enforces
    NEXUS ||--o{ RULESET_POLICY : checks
    NEXUS ||--o{ TRANSLATION_MATRIX : interprets
    NEXUS ||--|| EXPECTED_STRUCTURE : validates
    NEXUS ||--|| CRITICAL_FILES : verifies
    NEXUS ||--|| WRITABLE_PATHS : restricts_writes
    NEXUS ||--|| PROTECTED_PATHS : prevents_mutation
    NEXUS ||--o{ WORKFLOW_DEFINITIONS : executes
```

### `.prgx-ag` Data Layout
- **Policies:** `.prgx-ag/policy/patimokkha.yaml`, `.prgx-ag/policy/ruleset.yaml`
- **Translation layer:** `.prgx-ag/translation/aethebud_matrix.yaml`
- **Manifests:** `.prgx-ag/manifests/expected_structure.yaml`, `critical_files.yaml`, `writable_paths.yaml`, `protected_paths.yaml`
- **State:** `.prgx-ag/state/learning_state.json`, `.prgx-ag/state/gem_log.json`
- **Audit trail:** `.prgx-ag/audit/audit_log.jsonl`
- **Execution flows:** `.prgx-ag/workflows/*.yaml`

## PRGX Triad
- **PRGX1 Sentry (The Eye):** read-only entropy scanner (dependencies, structure, integrity drift).
- **PRGX3 Diplomat (Brain/Mouth):** translates findings into healing intent and human narrative.
- **PRGX2 Mechanic (The Hand):** only component allowed to apply explicit fixes.

## AetherBus Topics
- `porisjem.issue_reported`
- `porisjem.intent_translated`
- `porisjem.execute_fix`
- `porisjem.fix_completed`
- `porisjem.audit_violation`
- `porisjem.rsi_feedback`

## Patimokkha Code
The policy layer blocks destructive intent patterns such as `delete_core`, `shutdown_nexus`, exploit behavior, destructive recursion, hidden destructive updates, and unsafe self-modification.

## Healing Cycle
1. PRGX1 detects anomalies.
2. PRGX3 translates to healing intent.
3. PRGX2 validates with Patimokkha and executes safe repairs.
4. PRGX3 publishes a commit-style narrative.
5. RSI engine derives a bounded GemOfWisdom and applies only safe updates.

## Local Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

## CLI Usage
```bash
python -m prgx_ag.main --once
python -m prgx_ag.main --continuous --interval 10
python -m prgx_ag.main --scan-only
```

## Testing
```bash
pytest
```

## Safety Boundaries
- PRGX1 is strictly read-only and does not write files.
- PRGX2 is the sole write authority and is constrained by allowlist/protected-path controls.
- Patimokkha validation occurs before repair execution.

## Improvement Backlog (EN)
1. Add policy drift dashboards that compare current Patimokkha/ruleset versions against recent audit outcomes.
2. Add structured retention and archival rules for `audit_log.jsonl` and `gem_log.json` to keep long-running nodes lightweight.
3. Add workflow provenance metadata so each repair can be traced back to the exact workflow definition and manifest version used.
4. Add operator-facing health summaries that aggregate stability, efficiency, blocked intents, and repair success rate in one snapshot.
5. Add schema versioning/migration notes for `.prgx-ag` state files to support future backward-compatible upgrades.

## ข้อเสนอแนะต่อยอด (TH)
1. เพิ่ม dashboard สำหรับติดตาม policy drift โดยเปรียบเทียบเวอร์ชันของ Patimokkha/ruleset กับผลลัพธ์ audit ล่าสุด
2. เพิ่มกติกา retention และ archival แบบมีโครงสร้างสำหรับ `audit_log.jsonl` และ `gem_log.json` เพื่อให้โหนดที่รันนานยังคงเบา
3. เพิ่ม metadata เรื่อง provenance ของ workflow เพื่อย้อนกลับได้ว่าการซ่อมแต่ละครั้งใช้ workflow และ manifest เวอร์ชันใด
4. เพิ่มหน้าสรุปสุขภาพระบบสำหรับผู้ดูแล ที่รวมค่า stability, efficiency, blocked intents และอัตราความสำเร็จของการซ่อมในมุมมองเดียว
5. เพิ่มแนวทาง versioning/migration ของไฟล์สถานะใน `.prgx-ag` เพื่อรองรับการอัปเกรดแบบ backward-compatible ในอนาคต
