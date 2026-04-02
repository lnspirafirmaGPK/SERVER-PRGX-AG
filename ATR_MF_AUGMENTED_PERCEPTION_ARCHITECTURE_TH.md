# ATR-MF Augmented Perception Layer (APL) — High-Level Architecture Spec (TH)

เอกสารนี้เป็นสเปกระดับสถาปัตยกรรมสำหรับการพาแนวคิด ATR-MF จาก intent-driven interaction ไปสู่ production โดยยึดหลัก **blast radius ต่ำ**, **incremental capability rollout**, และ **safety-first governance**.

---

## อินพุตที่เติมจากสมมติฐาน (6–12 เดือน)
- เป้าหมายระยะ 6–12 เดือน:
  1) ทำให้ intent เดียวรันได้ทั้ง OS-native mode และ Light-native mode,
  2) คุม latency สำหรับ AR/VR และ projection ให้อยู่ใน budget,
  3) ผ่าน safety + governance สำหรับพื้นที่สาธารณะนำร่อง.
- อุปกรณ์เป้าหมาย: มือถือ (Android/iOS), Desktop (Windows), AR/VR glasses, edge projector box, building facade projector.
- ข้อจำกัดธุรกิจ/กฎหมาย/สถานที่ (สมมติฐาน):
  - ต้องมีการยินยอมจากเจ้าของพื้นที่,
  - ต้องทำ curfew ตามเทศบัญญัติท้องถิ่น,
  - ต้องมี geofencing และ safety zone รอบทางสัญจร.
- สแตก/ภาษา (เสนอ):
  - Control plane: Python + gRPC + protobuf + PostgreSQL + Redis,
  - Real-time plane: Rust/Go for Tachyon streaming,
  - Edge runtime: WASM + WebGPU/OpenGL/Vulkan backend ตามอุปกรณ์,
  - CV pipeline: ONNX Runtime / TensorRT (ตาม edge class).
- โค้ดฐาน PRGX-AG ที่มีแล้ว: ใช้ policy/audit/reliability pattern จาก runtime ใน `src/prgx_ag/*` เป็น governance backbone.

---

## 1) ภาพรวมสถาปัตยกรรม (1 หน้า)
ATR-MF APL แบ่งเป็น 3 ระนาบ:

1) **Intent & Contract Plane**
- รับเสียง/คำสั่ง → แปลงเป็น `Intent Contract` แบบ versioned
- Genesis แปลง intent เป็น `Visual Contract + Scene Graph`
- Manifest เป็น source of truth ของข้อกำหนดภาพ/พฤติกรรมที่ deploy ได้

2) **Real-time Adaptation Plane**
- BioVision วิเคราะห์สภาพแวดล้อม, segmentation, motion vectors, occlusion
- Governor + PRGX ทำ safety gating ก่อนส่งผลไป compose/render
- Tachyon ทำ deterministic transport + clock sync + delivery QoS

3) **Execution Plane (Edge/Device)**
- Edge/WASM runtime compose frame สุดท้ายโดยอิง predicted display time
- รองรับ duality:
  - **Inspira-Firma A (OS-native mode):** dispatch กลับ Android/iOS/Windows app intent
  - **Inspira-Firma B (Light-native mode):** render แสงเป็นอินเทอร์เฟซซ้อนสภาพจริง

### แกนตัดสินใจสำคัญ
- **Manifest-first deployment**: ทุก scene ต้องผ่าน manifest schema และ policy check ก่อนขึ้น real-time path
- **Safety before aesthetics**: Governor/PRGX มีสิทธิ์ block/downgrade visual intent
- **Edge-first latency**: การตัดสินใจระดับ frame timing อยู่ที่ edge runtime เสมอ
- **Fail-safe degradations**: ถ้า BioVision/Network ผิดปกติ ให้ fallback เป็น low-luminance safe overlay หรือ OS-native handoff

---

## 2) C4 (Context → Container → Component)

### C1: Context
- Actors:
  - End User (voice/gesture)
  - Developer (define intent/visual contract)
  - Org Operator (campaign/schedule)
  - Safety Admin (policy/governance)
- External systems:
  - Device OS APIs (Android/iOS/Windows)
  - Sensor feeds (camera/IMU/light sensor)
  - Identity provider / IAM
  - Compliance logging / SIEM

### C2: Containers
1. **Intent Gateway** (ASR/NLU + Intent Normalizer)
2. **Genesis Service** (intent→visual plan/scene graph)
3. **Manifest Registry** (intent/visual/scene contracts + schema/version)
4. **BioVision Service** (environment understanding + motion tracking)
5. **Governor Service** (brightness/curfew/geo/frequency constraints)
6. **PRGX Policy Service** (abuse prevention + policy enforcement + audit)
7. **Tachyon Stream Fabric** (real-time command/stream transport + sync)
8. **Edge/WASM Runtime** (per-device composition/render/project)
9. **Observability & Audit Stack** (logs/metrics/traces/evidence)

### C3: Components (ระดับโมดูลหลัก)
- Intent Gateway: `VoiceCapture`, `IntentParser`, `IntentSigner`
- Genesis: `IntentPlanner`, `SceneComposer`, `DualityResolver`
- Manifest: `SchemaValidator`, `VersionResolver`, `CompatibilityGuard`
- BioVision: `LayerSegmenter`, `MotionEstimator`, `AmbientAnalyzer`
- Governor: `GeoFenceEvaluator`, `BrightnessLimiter`, `CurfewScheduler`
- PRGX: `PolicyEngine`, `EnforcementPoint`, `AuditEmitter`
- Tachyon: `SessionManager`, `ClockSync`, `QoSController`
- Edge Runtime: `FramePredictor`, `LocalComposer`, `ProjectorDriver`, `OSModeBridge`

---

## 3) Dataflow / Controlflow

### Flow A: Voice/Intent → Output
1. VoiceCapture รับเสียง + timestamp monotonic
2. IntentParser สร้าง `IntentContract(vX.Y)`
3. Genesis สร้าง `VisualContract + SceneGraph`
4. Manifest Registry validate schema + compatibility
5. PRGX/Governor preflight check
6. Tachyon เปิด session และส่ง `RenderPlan + predicted_display_time`
7. Edge runtime compose frame และ render/project
8. ส่ง telemetry + audit event กลับ control plane

### Flow B: BioVision → Governor/PRGX → Manifest/Tachyon
1. BioVision ingest sensor/video stream
2. สร้าง `EnvironmentState` (lux, weather class, motion vectors, occlusion)
3. Governor evaluate policy (curfew/brightness/geo)
4. PRGX evaluate abuse/safety policy
5. ถ้า pass: update constraints เข้า Manifest/Tachyon
6. ถ้า fail: block/downgrade + ออก audit + fallback mode

---

## 4) Interface Contracts (ตารางสัญญาระหว่างโมดูล)

| Interface | Input (ย่อ) | Output (ย่อ) | Guarantees | Failure modes / Handling |
|---|---|---|---|---|
| `IntentContractAPI` | `{intent_id, actor_id, utterance, context, ts_mono, schema_ver}` | `{normalized_intent, confidence, mode_hint}` | exactly-once via `intent_id`, p95 < 80ms parse | ASR ambiguity → return `needs_disambiguation`; timeout → fallback OS-native |
| `GenesisPlanAPI` | `{normalized_intent, mode_hint, capability_profile}` | `{visual_contract, scene_graph, duality_plan}` | deterministic plan for same `intent_hash`; idempotent by `intent_id` | invalid capability profile → degrade template |
| `ManifestResolveAPI` | `{visual_contract, scene_graph, target_device, schema_ver}` | `{resolved_manifest, compatibility_report}` | backward-compatible minor versions; ordered by manifest revision | schema mismatch → reject with upgrade hint |
| `BioVisionStateAPI` | `{video_frame_ref, imu, lux, weather, ts_mono}` | `{env_state, layer_map, motion_vectors, confidence}` | frame order by `frame_seq`; late data discarded by watermark | sensor drop → extrapolate short window + confidence drop |
| `GovernorGateAPI` | `{resolved_manifest, env_state, location, local_time}` | `{allow|deny|downgrade, constraints, reason}` | policy evaluation p95 < 15ms, idempotent by `decision_key` | geo uncertain → safe deny / low-brightness mode |
| `PRGXEnforceAPI` | `{intent, content_tokens, actor_role, org_policy}` | `{allow|challenge|deny, enforcement_actions}` | strict ordering per session, auditable decision id | suspected abuse → challenge (step-up auth) |
| `TachyonStreamAPI` | `{session_id, render_plan, predicted_display_time, qos}` | `{ack, stream_stats, drift_ms}` | in-order per stream partition; at-least-once with dedupe key | jitter spike → adaptive bitrate / reduce layer density |
| `EdgeRenderAPI` | `{render_plan, constraints, env_delta, sync_clock}` | `{frame_presented_ts, dropped_frames, local_events}` | local monotonic clock sync drift < 2ms target | missed vsync → frame skip + phase realign |
| `AuditEventAPI` | `{event_type, subject, policy_id, decision, ts_utc}` | `{event_id, integrity_hash}` | append-only, tamper-evident chain hash | storage unavailable → local spool + signed replay |

### Schema/versioning policy
- `major.minor.patch`:
  - major: breaking
  - minor: additive backward-compatible
  - patch: bugfix semantic invariant
- Contract ทุกตัวต้องมี `schema_ver`, `producer_ver`, `compat_range`
- Backward compatibility rule: control plane ต้องรองรับ edge client ย้อนหลังอย่างน้อย 2 minor versions

### Error / Event / Audit model
- Error envelope มาตรฐาน: `{code, category, retriable, correlation_id, module, ts}`
- Event types: `INTENT_RECEIVED`, `PLAN_COMPOSED`, `POLICY_BLOCKED`, `STREAM_DEGRADED`, `FRAME_PRESENTED`
- Audit chain: hash-chained JSONL + periodic signed checkpoint

### Time/sync model
- ใช้ UTC wall clock สำหรับ audit และ monotonic clock สำหรับ latency path
- Tachyon ส่ง `predicted_display_time` และ `max_jitter_budget_ms`
- Edge runtime ใช้ PLL-style drift correction ทุก 500ms

---

## 5) Latency Budget & Benchmark Plan

### 5.1 Latency budget ตามโหมด

#### VR/AR mode (motion-to-light) เป้าหมาย p95 ≤ 20ms, p99 ≤ 28ms
- Capture sensors: 2ms
- Infer (BioVision lightweight): 6ms
- Compose (Genesis/Edge local): 4ms
- Transport (Tachyon local/edge): 3ms
- Render/Display: 5ms

#### Projector/Building mode (motion-to-projection) p95 ≤ 80ms, p99 ≤ 120ms
- Capture (camera + ambient): 10ms
- Infer (segmentation + motion): 25ms
- Compose (scene adjustment): 15ms
- Transport: 10ms
- Projector pipeline: 20ms

#### Tachyon network E2E
- Command E2E p95 ≤ 45ms intra-region
- Jitter budget ≤ 8ms (AR/VR), ≤ 20ms (building mode)
- Drift budget edge clock ≤ 2ms steady-state

### 5.2 วิธีวัด (reproducible)
- ทุก hop บังคับ trace id เดียวกัน (`correlation_id`)
- ใช้ hardware timestamp เมื่ออุปกรณ์รองรับ
- เก็บ histogram per stage + end-to-end
- แยก warm/cold path และ nominal/stress scenario

### 5.3 ชุด benchmark ขั้นต่ำ
1. `bench_intent_to_plan`: 1k intents, วัด parse+genesis
2. `bench_policy_gate`: 10k policy evaluations, วัด p95/p99
3. `bench_stream_jitter`: packet jitter/loss simulation
4. `bench_edge_render`: synthetic scene complexity ladder
5. `bench_motion_sync`: moving foreground alignment error (px + ms)

### 5.4 เครื่องมือ/สคริปต์ที่ควรมี
- `scripts/bench/run_intent_plan.py`
- `scripts/bench/run_policy_gate.py`
- `scripts/bench/run_stream_jitter.sh`
- `scripts/bench/run_edge_render.py`
- `scripts/bench/report_latency_budget.py`

---

## 6) Reliability Plan

### Retry/Timeout strategy
- Control APIs: timeout 150–300ms + exponential backoff (50,100,200,400ms)
- Tachyon stream: fast retransmit + FEC สำหรับ projection mode
- Policy/audit writes: at-least-once + idempotency key

### Ordering/Idempotency/Dedup
- ทุกคำสั่งมี `{session_id, seq_no, dedupe_key}`
- Edge runtime รับเฉพาะ seq ใหม่กว่า watermark
- Duplicate event ถูก merge ใน audit processor

### Offline & Reconciliation
- Edge local spool (encrypted) เก็บ command/audit ชั่วคราว
- reconnect แล้วทำ 3-way reconciliation:
  1) session checkpoint
  2) last applied seq
  3) policy revision hash
- conflict policy: server policy wins, edge rebase state

### Observability requirements
- Logs (structured): intent_id/session_id/policy_id/decision
- Metrics: p50/p95/p99 latency, drift, dropped frame, deny-rate
- Traces: full critical path (Gateway→Genesis→Policy→Tachyon→Edge)
- SLO alerts:
  - AR p95 latency > 20ms 5 นาทีต่อเนื่อง
  - policy deny spike > baseline + 3σ

---

## 7) Safety & Governance Plan

### Governor policy
- Brightness caps ตาม zone/time/weather class
- Curfew profiles (เช่น 22:00–06:00 ลด luminance/frequency)
- Geo-fencing: no-projection zones (ถนนหลัก, intersection, รพ.)
- Frequency constraints กัน flicker ที่เสี่ยงต่อผู้ใช้บางกลุ่ม

### PRGX policy enforcement
- Policy Engine: rule-based + risk scoring
- Enforcement Point:
  1) pre-render gate,
  2) mid-stream adaptive clamp,
  3) emergency kill-switch
- Audit trail:
  - signed decision log,
  - reason code,
  - actor/org binding,
  - immutable retention window

### Responsible building projection guideline
- ต้องมี “community impact profile” ก่อน deploy
- ใช้ quiet-hours preset ตามพื้นที่
- จำกัดเนื้อหาที่มีโอกาสรบกวนการจราจร/ความตื่นตระหนก
- มี emergency hotline + immediate shutdown protocol

### Threat model (ย่อ)
- Attacker goals: hijack display, inject harmful content, bypass curfew, impersonate operator
- Misuse cases: phishing via projected UI, traffic distraction, harassment projection
- Mitigations: mTLS + signed commands, RBAC/ABAC, step-up auth for high-impact intents, real-time anomaly detection, strict auditability

### AuthZ model
- Role: `user`, `developer`, `operator`, `safety_admin`, `org_admin`
- Scope: per device group / geography / campaign / time window
- High-risk actions ต้อง dual approval (`operator + safety_admin`)

---

## 8) Roadmap 4 เฟส (deliverables / risks / exit criteria / metrics)

### P0 — PoC (0–8 สัปดาห์)
- Deliverables:
  - intent→scene pipeline basic
  - single device edge runtime
  - basic governor caps
- Risks: โมเดล intent ผันผวน, sync clock ยังไม่นิ่ง
- Exit criteria:
  - demo dual mode (OS-native + light-native)
  - end-to-end trace ครบ
- Metrics:
  - success rate intent parse ≥ 92%
  - AR path p95 < 35ms ใน lab

### P1 — Limited Prototype (2–4 เดือน)
- Deliverables:
  - multi-device rendering profiles
  - PRGX enforcement + audit chain
  - benchmark suite v1
- Risks: policy false positive สูง, edge hardware variance
- Exit criteria:
  - ผ่าน benchmark ขั้นต่ำครบ
  - มี fallback behavior สำหรับ network loss
- Metrics:
  - policy decision p95 < 20ms
  - reconnect recovery < 3s

### P2 — Pilot First Customers (4–8 เดือน)
- Deliverables:
  - pilot deployment 2–3 พื้นที่
  - SOC/SIEM integration
  - community-safe projection playbook
- Risks: กฎหมายพื้นที่ต่างกัน, ภาระ ops สูง
- Exit criteria:
  - ไม่มี incident ระดับ critical 60 วัน
  - SLA pilot ผ่านตามสัญญา
- Metrics:
  - uptime control plane ≥ 99.5%
  - audit completeness = 100%

### P3 — Production Hardening & Scale (8–12 เดือน)
- Deliverables:
  - regional redundancy
  - automated policy rollout with canary
  - cost/latency optimization
- Risks: cross-region drift, governance drift
- Exit criteria:
  - ผ่าน chaos + failure-injection drills
  - ผ่าน external security review
- Metrics:
  - AR p95 ≤ 20ms, Projection p95 ≤ 80ms
  - Sev-1 = 0 ต่อไตรมาส

---

## 9) สิ่งที่ยังไม่รู้ + Assumptions

### Unknowns
1. เกณฑ์ทางกฎหมายการฉายแสงในแต่ละเทศบาลต่างกันเท่าใด
2. tolerance ผู้ใช้ต่อ adaptive dimming ในบริบทต่าง ๆ
3. hardware projector latency variance ใน field จริง
4. รูปแบบ abuse ที่เจอจริงหลังเปิด pilot

### Assumptions ที่ใช้ตัดสินใจ
1. มีสิทธิ์ติดตั้งเซนเซอร์และ edge box ในพื้นที่นำร่อง
2. องค์กรยอมรับการบังคับ policy override โดย Safety Admin
3. network ระดับพื้นที่นำร่องมี uplink เสถียรพอสำหรับ telemetry
4. ทีม dev ยอมรับ contract-first development และ schema governance

---

## ตัวอย่างคำสั่ง (แนะนำการสร้าง/ทดสอบงานใน PRGX-AG)

```bash
# 1) รันรอบตรวจหนึ่งครั้ง (เหมาะกับ "งานสแกน + สร้างหลักฐาน")
python -m prgx_ag.main --once

# 2) รันต่อเนื่องทุก 10 วินาที (เหมาะกับงาน monitor/repair loop)
python -m prgx_ag.main --continuous --interval 10

# 3) โหมดสแกนอย่างเดียว ไม่เขียนแก้ไข (เหมาะกับ preflight task)
python -m prgx_ag.main --scan-only

# 4) เทส end-to-end pipeline ก่อนปล่อยงานใหม่
pytest -q tests/test_pipeline_integration.py tests/test_nexus_cycle.py --maxfail=1

# 5) เทสเร็วเพื่อยืนยัน policy/governance หลัก
pytest -q tests/test_patimokkha.py tests/test_governance_evidence.py --maxfail=1
```

> ข้อเสนอเชิงปฏิบัติ: ให้เก็บ “task preset” เป็น script แยก เช่น `scripts/tasks/pilot_preflight.sh` เพื่อให้รันซ้ำได้แบบ deterministic.
