# Bug Fix Proposal

## Scope
Major structural fix: migrate repository from static-only docs layout into complete Python backend architecture for PRGX-AG Nexus while preserving governance documentation intent.

## Findings
1. Backend architecture existed only as narrative, not executable modules.
2. No strict schemas, no event bus runtime, no orchestrator, and no policy tests.
3. Missing CLI, RSI loop, and triad-agent integration.

## Proposed fixes
1. Add `src/prgx_ag` modular backend with strict Pydantic models and async AetherBus.
2. Implement PRGX1/PRGX2/PRGX3 agents with Patimokkha-enforced healing flow.
3. Add orchestrator + RSI engine + bounded learning state.
4. Add pytest coverage for policy, bus, agents, RSI, and full cycle.

## Expected impact
- Architecture is now executable and testable.
- Harmful intents are programmatically blocked before write operations.
- Repository now supports production-style governance flow and self-healing cycle.

## Rollback
Revert this change set if consumers require previous static-only documentation repository state.

## 2026-03-17 Major structural fix
- Implemented full hybrid PRGX-AG architecture (.prgx-ag governance + GitHub workflows + Python runtime triad).
- Added strict schemas, event-driven nexus wiring, safe fix executor guardrails, RSI bounded learning, and manifest/policy loaders.
- Added deterministic pytest coverage for policy, bus, triad behavior, manifest loading, translation matrix, and full cycle flow.

## 2026-03-17 Bug fix and documentation alignment
- Fixed pytest execution bug by adding `pythonpath = ["src"]` in `pyproject.toml`, so test imports work without manual environment overrides.
- Updated README system architecture into database/state-aligned ER diagram based on `.prgx-ag` data sources.
- Removed completed-recommendation noise and replaced with forward-only EN/TH backlog proposals.

## 2026-03-17 Triad hardening and architecture completion pass
- Added explicit PRGX1 read-only scan methods for dependency, structure, and integrity drift observation.
- Added integrity scanner + healing intent builder + finding/narrative schemas to complete Porisjem role boundaries.
- Extended orchestrator with `PRGXAGNexus` naming, shutdown support, and compatibility alias.
- Updated README with full Porisjem/AETHERIUM framing, refreshed architecture diagram context, and new EN/TH future backlog items.

## 2026-03-17 README architecture/data-store alignment refresh
- Refined README system architecture to mirror the actual `.prgx-ag` data layout, including policy, manifest, workflow, state, and audit relationships.
- Removed completed-recommendation overlap from bilingual backlog sections and replaced it with new forward-looking EN/TH enhancement proposals.

## 2026-03-18 Source recovery fix
- Repaired `src/prgx_ag/agents/prgx1_sentry.py` after a diff artifact and concatenated multi-file patch content were accidentally committed into the module body.
- Restored the file to valid Python source so import, compile, and packaging pipelines can load the PRGX1 agent again.

## 2026-03-18 Workflow governance gate alignment
- Promoted `.github/workflows/prgx-test.yml` as the canonical repository-health gate with a consistent early `python -m compileall src` sanity check.
- Standardized Python setup/install patterns across the PRGX scan, nightly, and healing workflows to reduce dependency drift and simplify triage.
- Removed the generic GitHub Pages deployment workflow because it deployed the entire repository root instead of a dedicated static-site artifact, which was not appropriate for this repository health model.
