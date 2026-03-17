# PRGX-AG Nexus (AETHERIUM GENESIS Core)

Production-ready Python backend architecture for Porisjem Protocol orchestration with PRGX1/PRGX2/PRGX3 triad, Patimokkha governance, AetherBus eventing, and bounded RSI feedback.

## Purpose
- Provide safe self-healing automation for repository/runtime maintenance.
- Enforce ethical control gates before any write operation.
- Keep scanning, policy, translation, execution, orchestration, and RSI separated.

## Architecture Summary
- **PRGX1 Sentry**: read-only scanner; emits issue reports.
- **PRGX3 Diplomat**: translates reports into healing intent + narratives.
- **Patimokkha Checker**: blocks harmful intent (`delete_core`, `shutdown_nexus`, `exploit`, recursion abuse, infinite-loop hints).
- **PRGX2 Mechanic**: only write-capable agent, executes approved fixes.
- **AetherBus**: async pub/sub event backbone.
- **RSI Engine**: generates `GemOfWisdom` updates and applies bounded safe learning.

## Folder Structure

```text
src/prgx_ag/
  agents/         # PRGX1 / PRGX2 / PRGX3
  core/           # bus, base agent, events, exceptions
  orchestrator/   # Nexus wiring + cycle execution
  policy/         # Patimokkha governance rules
  rsi/            # gems, learning state, analysis engine
  schemas/        # strict Pydantic v2 models
  services/       # scanners, translation, narrative, fix executor
  utils/          # reusable helpers
```

## Event Flow
1. `porisjem.issue_reported`
2. `porisjem.intent_translated`
3. `porisjem.execute_fix`
4. `porisjem.fix_completed`
5. `porisjem.rsi_feedback`
6. `porisjem.audit_violation` (for rejected unsafe actions)

## Run
```bash
python -m prgx_ag.main --once
python -m prgx_ag.main --continuous --interval 10
python -m prgx_ag.main --scan-only
```

## Test
```bash
PYTHONPATH=src pytest
```

## Healing Cycle Example
- PRGX1 finds anomaly (`missing __init__.py` etc.)
- PRGX3 produces healing intent and execution envelope
- Patimokkha validates intent
- PRGX2 appends explicit repair log entry (`FIX_LOG.md`) as reversible fix
- PRGX3 emits commit-style summary
- RSI creates safe GemOfWisdom and updates bounded learning state

## Governance (Patimokkha Code)
Ethical statuses supported:
- `CLEAN`
- `MINOR_INFRACTION`
- `MAJOR_VIOLATION`
- `PARAJIKA`

## RSI Loop
- Success + revenue => efficiency/stability gain.
- Success but slow => optimization lesson.
- Failure => stability-first lesson.
- Unsafe gems are rejected by `safe_to_apply` guard and bounded parameter limits.
