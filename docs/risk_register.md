# Risk Register

Living register of risks that could sink, delay, or weaken the capstone.
Review at the start of every phase and whenever a trigger fires; update
statuses at the end of substantial runs alongside `RUN_STATE.md`.

Conventions:

- Likelihood/Impact: low / medium / high, judged against the current phase.
- Trigger: the observable event that means the risk is materializing.
- Mitigation: what we do *now* to reduce likelihood or impact.
- Fallback: what we do *if it happens* - every fallback must preserve a
  publishable result, even if smaller.
- Owner: `user` for actions needing human/lab/supervisor access, `agent` for
  repo work.

## Summary

| ID | Risk | Phase | Likelihood | Impact | Status |
|---|---|---|---|---|---|
| R-001 | Supervisor approval delayed or scope shifts | 1 | medium | high | open |
| R-002 | powermetrics sudo workflow not approved on measurement Mac | 2 | low | high | open |
| R-003 | MLX install or model-load failure on Mac | 2 | low | medium | open |
| R-004 | KV persist/resume unsupported in a target runtime | 3 | medium | high | open |
| R-005 | llama.cpp cache files not portable across machines/backends | 3 | medium | high | open |
| R-006 | 3080 Ti borrow window slips or shrinks | 3 | medium | medium | open |
| R-007 | No wall meter available | 1-4 | medium | medium | open |
| R-008 | Orin telemetry inaccessible | 2-3 | medium | low | open |
| R-009 | Hailo cannot run LLM-shaped workloads | 1 | high | low | open (by design) |
| R-010 | Controller-as-DUT contamination on Mac runs | 2 | high (unmitigated) | medium | mitigated by D-013 |
| R-011 | Benchmark network cannot be isolated | 3 | medium | medium | open |
| R-012 | Schedule: five phases vs fixed academic deadlines | all | medium | high | open |
| R-013 | Thermal throttling confounds measurements | 2-4 | medium | medium | mitigated by D-014 |
| R-014 | Model weights become unavailable or gated | 2+ | low | medium | open |
| R-015 | Schema changes after data collection starts | 2+ | low | high | mitigated |

## R-001: Supervisor approval delayed or scope shifts

- Phase: 1. Likelihood: medium. Impact: high (wrong deliverable built).
- Trigger: Phase 2 implementation slices ready to start (2A-2F complete)
  with P1-001 still open; or any supervisor communication contradicting
  `AGENT_PLAN.md` scope.
- Mitigation: the queue keeps P1-001 ranked first; all work until approval
  stays hardware-independent and harness-shaped (valuable under any scope);
  the Phase 1 exit checklist lists the exact questions to put to the
  supervisor so one meeting can close the gate.
- Fallback: if approval stalls past mock-slice completion, continue only
  mock/local work and mark every hardware purchase or borrow decision
  blocked-on-approval.
- Owner: user.

## R-002: powermetrics sudo workflow not approved on measurement Mac

- Phase: 2. Likelihood: low (user controls the machine; auth session planned
  2026-06-10). Impact: high (no Mac telemetry = no flagship vertical slice).
- Trigger: scoped sudoers rule (D-004) cannot be installed, or privileged
  sample capture fails after the auth session.
- Mitigation: D-004 defines a minimal, single-binary sudoers rule with the
  exact line documented in the instrumentation checklist; interactive-sudo
  manual fallback documented for attended runs.
- Fallback: attended runs with interactive sudo (operator present per
  experiment); if even that is unacceptable, the Mac becomes
  runtime-supported/telemetry-blocked and the first real slice moves to the
  first available CUDA target - recorded as a finding, not hidden.
- Owner: user (install rule), agent (pre-check + structured failure).

## R-003: MLX install or model-load failure on Mac

- Phase: 2. Likelihood: low. Impact: medium (delays flagship slice).
- Trigger: `pip install mlx mlx-lm` fails, or the chosen model (D-016) has
  no working MLX artifact.
- Mitigation: install into a dedicated venv with versions recorded in run
  bundles; model criteria (D-016) require known MLX availability before
  selection; smoke-test load before scheduling measurement sessions.
- Fallback: llama.cpp with the Metal backend as the Mac runtime (already a
  planned runtime for split portability under D-015); the MLX adapter then
  becomes optional rather than flagship.
- Owner: agent (with user approving installs).

## R-004: KV persist/resume unsupported in a target runtime

- Phase: 3. Likelihood: medium overall (high for vLLM file-based replay,
  low for llama.cpp, low-medium for mlx-lm). Impact: high if unmitigated -
  this is the project's central feasibility risk.
- Trigger: a Stage 3.0 spike returns `replay_unsupported` for a runtime
  needed by a planned pairing.
- Mitigation: D-015's feasibility ladder - spikes run *before* any split
  hardware time is scheduled; pairings are planned only on runtimes with
  `replay_supported` verdicts; the synthetic transfer microbenchmark
  (Stage 3.1) is independent of all runtime cooperation and guarantees a
  crossover dataset.
- Fallback: analytical composition - measured prefill energy (node A) +
  measured synthetic transfer energy (payload sized by the KV model) +
  measured decode energy (node B) bounds the split cost honestly; the report
  states the composition method explicitly.
- Owner: agent.

## R-005: llama.cpp cache files not portable across machines/backends

- Phase: 3. Likelihood: medium (session files are version- and
  model-sensitive; cross-backend CUDA-save -> Metal-load is unverified).
  Impact: high for *heterogeneous* pairings specifically.
- Trigger: Stage 3.0.2's cross-machine restore test fails or produces
  divergent output.
- Mitigation: the spike tests cross-machine restore explicitly, with pinned
  identical llama.cpp versions and identical GGUF files on both ends, before
  any heterogeneous experiment is scheduled.
- Fallback: restrict offline-replay pairings to same-platform pairs
  (GPU->GPU in the borrow window, Orin->Orin); cover heterogeneous pairs
  with the analytical composition (R-004 fallback); report the portability
  finding itself - it is a legitimate disaggregation-practicality result.
- Owner: agent.

## R-006: 3080 Ti borrow window slips or shrinks

- Phase: 3. Likelihood: medium. Impact: medium (loses GPU->GPU pairing, not
  the phase).
- Trigger: window not scheduled by Phase 3 Stage 3.2 completion; or window
  arrives before split tooling is ready.
- Mitigation: all split tooling reaches rehearsed-on-available-hardware state
  before the window (the Phase 3 plan keeps a borrow-window runbook so
  borrow time is execution-only, no debugging); calendar mapping task
  (P1-008) makes the window a tracked date.
- Fallback: GPU->GPU pairing drops to single-GPU prefill/decode phase
  decomposition plus analytical composition; 3050<->Orin and Orin<->Orin
  remain.
- Owner: user (scheduling), agent (runbook readiness).

## R-007: No wall meter available

- Phase: 1-4. Likelihood: medium. Impact: medium (boundary calibration and
  Pi/Hailo coverage lost; per-target results stand).
- Trigger: P1-003 resolves "unavailable".
- Mitigation: P1-003 is a Phase 1 gate precisely so this resolves before it
  matters; D-018's boundary table makes results honest without a meter.
- Fallback: report within-target comparisons (always boundary-consistent)
  as primary; flag cross-target absolute comparisons with the boundary
  caveat; targets with no platform telemetry (Pi) become
  telemetry-unavailable findings.
- Owner: user.

## R-008: Orin telemetry inaccessible

- Phase: 2-3. Likelihood: medium (rail sysfs paths vary by L4T version).
  Impact: low (one target of several).
- Trigger: P1-006 evidence shows neither INA3221 sysfs nor tegrastats usable.
- Mitigation: two candidate mechanisms documented before hardware time;
  wall-meter fallback if R-007 resolves positively.
- Fallback: Orin runs runtime-only (latency/throughput) marked
  telemetry-unavailable, or drops to a stretch target.
- Owner: user (access), agent (adapter).

## R-009: Hailo cannot run LLM-shaped workloads

- Phase: 1. Likelihood: high. Impact: low - *by design*: the plan treats
  Hailo as a feasibility investigation whose negative verdict is itself a
  reportable applicability finding.
- Trigger: feasibility checklist closes with any non-`supported` verdict.
- Mitigation: none needed; the verdict-code structure in
  `docs/phase_1/hailo_feasibility.md` makes the outcome publishable either
  way. Do not spend implementation effort before the verdict (standing
  do-not-do-yet rule).
- Fallback: Pi 5 CPU-only llama.cpp with wall-meter telemetry becomes an
  optional low-power data point if the meter exists; otherwise Pi/Hailo
  appears only in the applicability table.
- Owner: user (device access), agent (verdict documentation).

## R-010: Controller-as-DUT contamination on Mac runs

- Phase: 2. Likelihood: high if unmitigated. Impact: medium (biased flagship
  numbers).
- Status: mitigated by D-013 (idle baseline includes resident quiescent
  controller; deferred logging; blocking wait during measured window).
- Trigger (residual): SSH-controlled comparison runs (once transport exists)
  show a delta beyond run-to-run variance.
- Fallback: move Mac headline measurements to remote-controlled runs.
- Owner: agent.

## R-011: Benchmark network cannot be isolated

- Phase: 3. Likelihood: medium (campus/home network constraints unknown
  until P1-004 closes). Impact: medium (noisy transfer measurements).
- Trigger: P1-004 topology answer shows shared links only.
- Mitigation: prefer direct node-to-node cabling (no switch) for 1GbE/2.5GbE
  point-to-point tests - removes the isolation question entirely for
  two-node experiments; record link conditions per run in the bundle.
- Fallback: run sweeps off-hours, repeat n>=5, report observed throughput
  alongside nominal link speed (the bundle already records measured
  throughput per D-008's transfer block).
- Owner: user (hardware), agent (recording).

## R-012: Schedule: five phases vs fixed academic deadlines

- Phase: all. Likelihood: medium. Impact: high (capstones fail by calendar,
  not by code).
- Trigger: any phase exceeding its (to-be-set) calendar budget; colloquium
  or report dates announced (P1-008) leaving less runway than the plan
  assumes.
- Mitigation: P1-008 maps phases to real dates as soon as the user supplies
  them (`docs/milestones.md` holds the skeleton); every phase defines a
  hardware-independent floor and a descope ladder so cutting is a decision,
  not a scramble.
- Descope ladder (worst-case minimum viable capstone, in cut order):
  1. Drop live split (3.3) - already stretch.
  2. Drop 10GbE and one model size.
  3. Drop heterogeneous replay pairs (keep synthetic transfer + analytical
     composition).
  4. Drop Orin/Pi targets (keep Mac + one CUDA).
  5. Floor: mock harness + Mac vertical slice + homogeneous baselines +
     synthetic interconnect sweep + analytical split model. This is still a
     complete, defensible benchmark-plus-study.
- Owner: user (dates), agent (floor discipline).

## R-013: Thermal throttling confounds measurements

- Phase: 2-4. Likelihood: medium (high on passively-cooled Orin/Pi).
  Impact: medium (rep-to-rep drift, biased late reps).
- Status: mitigated by D-014 (idle-power recovery gate between reps,
  thermal_drift_c in measurement quality, interleaved ordering) - residual
  risk on targets without thermal sensors.
- Trigger: thermal_drift_c trending across reps, or cooldown cap hits
  recorded in bundles.
- Fallback: longer cooldowns, active cooling notes recorded in run metadata,
  or excluding throttled reps *with documented cause* per D-014.
- Owner: agent.

## R-014: Model weights become unavailable or gated

- Phase: 2+. Likelihood: low. Impact: medium (mid-project model swap breaks
  comparability).
- Trigger: chosen model's hub entry gated/removed; license terms change.
- Mitigation: D-016 requires mirroring chosen weights to local storage
  immediately on selection, with revisions and hashes recorded.
- Fallback: promote the recorded fallback candidate; re-run affected
  baselines (the config hash separates old/new data cleanly).
- Owner: agent.

## R-015: Schema changes after data collection starts

- Phase: 2+. Likelihood: low. Impact: high (existing bundles unreadable or
  silently misread).
- Status: mitigated structurally.
- Mitigation: schema_version field exists from v0.1; D-008 plans the only
  anticipated breaking-shape change (v0.2) *before* split data collection;
  output-schema additions are additive-only (the JSON schema does not forbid
  additional properties); `validate-bundle` pins what a valid bundle means
  per version.
- Trigger: any proposed non-additive change to a schema with bundles already
  on disk.
- Fallback: a dated migration note in this repo plus a one-shot migration
  script; never edit bundles in place (they are evidence).
- Owner: agent.
