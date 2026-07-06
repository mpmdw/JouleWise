# JouleWise: Project Status, Plan, And Architecture

Audience: project advisor. This is the standalone monitoring document - it
summarizes what the project is, how it is built, where it stands, and what
it needs, without requiring any other file. Pointers into the repository
are provided for anyone who wants the full evidence trail.

- Last updated: 2026-07-05
- Project phase: Phase 1 closing; Phase 2 in progress - the
  hardware-independent harness core is complete and runnable
- Repository: `github.com/mpmdw/JouleWise` (branch `main`)

## This Update (2026-07-05) — 30-second read

**Progress:** work paused for a planned break (June 13 – July 4) and resumed
with a full external audit of the code and plans. The harness core is
unchanged and verified green (169 checks). The audit tightened the planning
corpus (one status authority per phase, duplication removed), added two
tracked risks with fixes in hand (measurement-data backup; the repository
was moved off iCloud after a sync-lock recurrence), and defined one new
engineering slice (2N: seam hardening the real Mac adapters will build on —
next up, needs no hardware or approvals).

**Context from the previous update (2026-06-12):** the benchmark harness
runs end to end — one command turns a typed experiment config into a
complete, auditable energy + latency measurement bundle, proven on a
deterministic software target before any hardware time is spent. The
Raspberry Pi/Hailo accelerator was confirmed unable to run LLM workloads —
a clean, documented "not applicable" result, not a setback.

**On track:** real-hardware measurement (Mac, then NVIDIA/Jetson) remains
next after 2N and is fully specified — it is execution, not design.

**What I need from you (sanity check):** unchanged — a short
scope-confirmation that the reusable harness is the primary deliverable and
split inference the validating study — this unblocks model selection and
the first real Mac measurements. Any other thoughts are welcome.

## Summary

JouleWise is a reusable, typed, extensible benchmark harness for measuring
the energy of LLM inference across heterogeneous local hardware. The name
nods to JouleSort and Splitwise: energy measurement is the spine of the
system; disaggregated ("split") inference - running prefill and decode on
different machines with the KV cache transferred between them - is the
validating research study, not the whole architecture.

The first working slice runs on a MacBook (Apple Silicon) with MLX as the
runtime and `powermetrics` as the power source, producing complete,
auditable run bundles. Further backends (NVIDIA + vLLM/llama.cpp, Jetson
Orin, Raspberry Pi + Hailo as a feasibility finding) plug into the same
adapter interfaces.

Research questions:

- **Q1**: Under what conditions (model size, prompt length, link speed,
  device pair) does splitting inference reduce total energy versus running
  monolithically on either device?
- **Q2**: How sensitive is the split's energy cost to interconnect
  bandwidth (1GbE vs 2.5GbE vs optional 10GbE) - where is the crossover?
- **Q3**: When splitting saves energy, what latency does it cost, and vice
  versa (energy-latency Pareto frontier)?

## Status At A Glance

| Phase | Scope | Status |
|---|---|---|
| 1. Approval, feasibility, measurement design | contracts, methodology, hardware feasibility evidence | **in progress** - design artifacts complete; Hailo verdict + Phase 2 readiness closed (2026-06-12); supervisor/calendar/hardware-access gates open |
| 2. Harness, Mac vertical slice, homogeneous baselines | runnable harness, first real measurements, per-target baselines | **in progress** - mock vertical slice (2A-2F, 2J) complete and runnable; hardening slice 2N queued (ungated); hardware slices (2G-2M) gated |
| 3. Disaggregation, KV replay, interconnect sweep | split-energy decomposition, crossover dataset | planned (feasibility-first) |
| 4. Characterization and analysis | statistics, figures, claims audit | planned |
| 5. Presentation and submission | report, colloquium, reproducible release | planned |

Complete so far (all verifiable in the repository):

- A runnable harness: from a typed config, one command
  (`python3 -m joulewise run ...`) produces a complete, schema-valid,
  auditable run bundle and reduces it to energy/latency summary metrics -
  today from deterministic mock adapters (controller, bundle contract, and
  reducer math proven without hardware). Bundle writer, controller
  lifecycle, reducer, static-HTML report generator, and CLI verbs `run` /
  `validate-bundle` / `report`.
- Typed config and output schemas with validation, JSON-Schema export, and
  a CLI, plus a passing test suite (169 tests, run in CI on every push,
  including a mock end-to-end run + bundle validation).
- Adapter interface contracts (runtime / telemetry / transport), the run
  bundle artifact contract, and the measurement methodology (idle
  subtraction, measurement boundaries, clock synchronization, statistical
  protocol - highlights below).
- Evidence-shaped plans for every phase, a design-decision log (19
  decisions, each with the alternatives considered), a risk register with
  an explicit descope ladder, and example configs for the Mac and mock
  targets.
- First hardware evidence: `powermetrics` located and its superuser
  requirement confirmed on Apple Silicon; useful samplers identified
  (CPU/GPU/ANE power, thermal); MLX installation requirement recorded.

Not yet started: the real-hardware adapters (Mac MLX + powermetrics,
NVIDIA/vLLM, Jetson Orin). These are the gated Phase 2 slices 2G-2M;
code-level specs are in
`docs/phase_2/hardware_slice_implementation_guide.md`. The mock-first core
landed first by design, so measurement code is never debugging the harness
and the instrument at the same time.

Currently blocked on external input:

1. **Advisor scope confirmation** (the top project gate): confirm the
   harness is the primary artifact and disaggregation the validating
   study; required hardware scope; Hailo as feasibility-finding rather
   than must-succeed backend; stretch items. One meeting closes this.
2. Calendar anchors: colloquium date, report deadline, and the 3080 Ti
   borrow window, to derive phase target dates.
3. A local authorization session to capture the first privileged
   `powermetrics` sample (gates the powermetrics adapter, slice 2H). The
   originally planned 2026-06-10 slot passed without one; needs
   rescheduling.

Closed since the last revision (2026-06-12): the Hailo feasibility verdict
(`unsupported_workload`) and the Phase 2 readiness review.

## Architecture

```text
typed config
  -> controller
    -> transport adapter: local | ssh
    -> runtime adapter:   mock | mlx | vllm | llama.cpp | hailo-if-viable
    -> telemetry adapter: mock | powermetrics | nvidia-smi | jetson rails | wall meter
  -> run bundle (self-contained, on-disk source of truth)
    -> reducers (energy integration, idle subtraction, per-phase attribution)
    -> static report / notebooks / paper figures
```

Key elements:

- **Single controller, flexible transports.** `local` for one-machine
  runs; `ssh` for remote NVIDIA/Orin targets and split experiments.
- **Two adapter layers.** Runtime adapters answer how a model workload
  executes; telemetry adapters answer how power and thermal state are
  measured. They are independent, so any runtime can pair with any
  telemetry source.
- **A target is a composition** of transport + runtime + telemetry:

  | Target | Transport | Runtime | Telemetry |
  |---|---|---|---|
  | macbook_m3_max | local | mlx | powermetrics |
  | nvidia_3050 | ssh | vllm (llama.cpp-CUDA fallback) | nvidia-smi |
  | orin_nano | ssh | tbd | board rails (INA3221) |
  | pi5_hailo | ssh | hailo - unsupported (verdict 2026-06-12) | wall meter |

- **Every run writes a self-contained run bundle**: normalized config,
  device/environment metadata, timestamped event log (lifecycle + phase +
  token events), raw power trace, backend-native raw telemetry preserved
  verbatim, logs, model outputs, and reduced summary metrics. Summary
  numbers are always derived, re-derivable artifacts; the raw bundle is
  the source of truth.
- **Typed schemas** (Python dataclasses, standard library only in the
  core) validate configs and outputs and emit JSON Schema documentation.
- **Unsupported is a result, not a crash.** Infeasible
  hardware/model/runtime combinations return structured failure codes
  (`did_not_fit`, `runtime_unavailable`, `telemetry_unavailable`, ...)
  and still produce complete bundles - hardware applicability is itself
  reportable data (this is how a negative Hailo verdict stays a finding).
- **Dashboard v1 is a read-only run browser**, generated as static HTML
  from bundles (run table, per-run pages, power traces with phase
  shading). It has no orchestration role.

## Measurement Methodology Highlights

- **Idle subtraction.** Every run measures an idle baseline; energy
  metrics report gross and idle-subtracted values, with idle variance
  recorded.
- **Measurement boundaries are named, not assumed.** Each telemetry
  backend measures a different physical boundary - powermetrics: Apple
  SoC subsystems (CPU+GPU+ANE); nvidia-smi: GPU board only; Jetson rails:
  module input; wall meter: full system AC. Within-target comparisons are
  the primary claim type; cross-target comparisons always state the
  boundary difference, calibrated against the wall meter where available.
- **Uncertainty is quantified.** Headline comparisons use n>=5
  repetitions with mean, standard deviation, and 95% t-intervals;
  outliers are flagged (never silently dropped); raw points appear in
  every figure; differences are claimed only where intervals separate.
  Thermal state is controlled with an idle-power-recovery gate between
  repetitions.
- **Multi-node clock discipline.** For split runs, per-node clock offset
  is bounded with controller-mediated marker events and recorded;
  cross-node intervals shorter than the bound are flagged rather than
  trusted.
- **Measurement quality is first-class data**: requested vs observed
  sampling rate, dropped samples, idle variance, thermal drift, telemetry
  source - all in every summary.

## Experiment Plan

**Homogeneous baselines (Phase 2).** Per target and model: a workload
matrix spanning prefill-heavy, decode-heavy, and balanced profiles
(prompt 128-4096 tokens x decode 64-512), n=5, producing energy/token and
energy/request with intervals - and reproducing the qualitative
prefill/decode power asymmetry that motivates disaggregation.

**Disaggregation (Phase 3), feasibility-first.** KV-cache portability is
the project's central technical risk, so the phase is a ladder where each
rung is publishable even if the next fails:

1. *Synthetic transfer microbenchmark* (guaranteed): move KV-sized
   payloads between nodes with both-end power sampling - transfer energy
   and time vs payload size vs link speed, independent of any LLM
   runtime's cooperation.
2. *Offline replay* (primary): persist the prompt cache on the prefill
   node, transfer the file, resume decode on the decode node - same
   pinned runtime on both ends. Per-runtime feasibility spikes (mlx-lm,
   llama.cpp including cross-machine portability, vLLM time-boxed) run
   before any borrowed-hardware scheduling.
3. *Live split* (stretch): streamed KV during the run; explicitly
   droppable without harming the study.

Payload sizes are analytically predictable (2 x layers x kv_heads x
head_dim x 2 bytes per token, fp16), which drives experiment design - for
a 2048-token prompt: a 1.5B-class model ~56 MiB (~0.5 s at 1GbE), an
8B-class model ~256 MiB (~2.3 s at 1GbE). At 1GbE, mid-size-model
transfer time is the same order as prefill time on weaker devices -
exactly the regime where an energy crossover can exist; the sweep spans
prompt lengths and link speeds accordingly.

**Analysis (Phase 4).** Aggregation over validated bundles with an
exclusion log (no silent data drops); a deterministic figure pipeline
(every report figure regenerates from a script); a claims-to-evidence
index (every quantitative claim traces to figure -> script -> raw
bundles); a sensitivity audit checking that headline effects exceed their
confidence intervals.

## Phase Plan Detail

Each phase has a step-by-step plan and an evidence-gated exit checklist
in the repository; a phase closes only when every required item has
recorded evidence or a documented blocker.

- **Phase 1** - `docs/phase_1/`: lock contracts and methodology (done);
  gather feasibility evidence: advisor scope, Mac telemetry permissions,
  wall-meter decision, network topology for the sweep, Hailo verdict,
  NVIDIA/Orin access, calendar mapping.
- **Phase 2** - `docs/phase_2/`: bundle writer -> mock adapters ->
  controller -> reducer -> one-command run (all hardware-independent,
  exact-arithmetic tests) -> then the real Mac slice (MLX + powermetrics,
  repeated with variance) -> remote targets as access permits ->
  homogeneous baselines.
- **Phase 3** - `docs/phase_3/`: feasibility spikes -> split-run config
  schema -> transfer microbenchmark -> offline-replay splits with
  per-stage energy decomposition (prefill / transfer / deserialize /
  decode) -> interconnect sweep -> crossover dataset.
- **Phase 4** - `docs/phase_4/`: statistics ratification, aggregation,
  figures F1-F8 (baselines, traces, phase asymmetry, split decomposition,
  crossover curves, Pareto frontier, interconnect costs, measurement
  quality), claims index, results + limitations draft, background /
  related-work draft (new stage 4.6 — the report's background chapter now
  has an owner).
- **Phase 5** - `docs/phase_5/`: verified README quickstart, backend
  extension guide (verified by a shipped tutorial adapter), sample
  bundles, dataset freeze with hash manifest and release tag, colloquium
  slides, final report.

## Evolution From The Original Architecture Sketch

The project began from the "Energy Benchmark Architecture And Expanded
Plan" sketch. Its architecture survives intact; implementation thinking
has been refined in documented ways (full rationale in
`docs/decision_log.md`):

| Original sketch | Current position | Why |
|---|---|---|
| Configs YAML/JSON; bundle stores `config.yaml` | JSON now; bundle stores normalized `config.json`; YAML deferred until authoring pain is real | zero-dependency core; sorted-key JSON gives stable config hashing for aggregation (D-001, D-007) |
| "Likely Python + Pydantic" schemas | stdlib dataclasses with the same contract; Pydantic port possible later | Phase 1 runs with no installs; semantics unchanged (D-009) |
| Mac MLX slice implemented first | mock vertical slice first, Mac immediately after | the harness is proven with exact-arithmetic tests before real telemetry can confound it; Mac remains the first real backend (Phase 2 plan) |
| Dashboard file-backed; "DuckDB/SQLite if browsing gets slow" | static HTML generator; analysis aggregation via CSV + pandas in Phase 4; no DB planned | smallest sustainable tool that serves the two real uses: sanity-checking runs and showing progress (D-006) |
| Offline KV replay before live disaggregation | same, hardened into a three-rung feasibility ladder with per-runtime spikes and a same-runtime rule | KV tensors are not portable across engines; cross-runtime transfer (e.g. vLLM-prefill -> MLX-decode) is out of scope; heterogeneous *hardware* pairs use a portable runtime where its backends allow, pending an explicit portability spike (D-015) |
| GPU-to-Apple split experiments listed directly | pairings are planned only after spike verdicts; synthetic transfer sweep guarantees the crossover dataset either way | converts the project's largest feasibility risk into a bounded one (R-004, R-005) |
| (not covered) | measurement boundaries, multi-node clock discipline, controller co-residency mitigation, statistical protocol | added rigor required for defensible cross-device energy claims (D-003, D-013, D-014, D-018) |

Verdict from the 2026-06-09 audit: the sketch remains coherent; nothing
in it has been contradicted - the changes above are refinements with
recorded rationale, and the repository's plans are the maintained,
authoritative version of it.

## Risks And Minimum Viable Outcome

Top risks (full register with triggers and fallbacks in
`docs/risk_register.md`):

| Risk | Posture |
|---|---|
| KV persist/resume unsupported in a runtime (esp. vLLM) | spikes before hardware scheduling; llama.cpp fallback; synthetic-transfer floor + analytical composition keeps the study publishable |
| Cache files not portable across machines/backends | explicit cross-machine spike; fallback to same-platform pairs; portability finding is itself reportable |
| Schedule vs fixed academic deadlines | every phase has a hardware-independent floor; explicit descope ladder |
| 3080 Ti borrow window slips | borrow time is execution-only against a rehearsed runbook; pairing droppable |
| No wall meter | within-target claims unaffected; cross-target claims carry the stated boundary caveat |
| Advisor approval delay | all current work is harness-shaped and valuable under any scope |

Minimum viable outcome (worst-case floor, already a complete capstone):
the reusable harness + Mac vertical slice + homogeneous baselines +
synthetic interconnect sweep + an analytical split-energy model - honest,
measured, reproducible.

## Timeline

Dates pending (this is an explicit ask): colloquium date, report
deadline, borrow window. Once known they anchor `docs/milestones.md` and
phase target dates are derived backwards (slides want frozen figures >=1
week ahead; the report wants its claims audit >=1 week ahead). Until
then, the dependency structure is the schedule: Phase 4 is deskwork and
serves as the buffer; hardware-gated steps are scheduled around access
windows with desk work filling gaps.

Known: a local Mac authorization session needs rescheduling (unblocks the
first privileged power sample). Work paused 2026-06-13 to 2026-07-04
(planned break, recorded in `docs/milestones.md`).

## Deliverables At Completion

- The JouleWise repository: harness, adapters, tests, CI, extension
  guide, README quickstart that a new user can run in minutes.
- The dataset: raw run bundles + hash manifest, frozen and tagged, with
  every figure regenerable by script.
- The study: where splitting wins, loses, and why - with uncertainty,
  limitations, and hardware-applicability findings (including negative
  verdicts).
- Final report and colloquium presentation, every quantitative claim
  traceable to raw data.

## Repository Map (for verification)

| Where | What |
|---|---|
| `README.md` | entry point and quickstart (grows in Phase 5) |
| `AGENT_PLAN.md` | phase index and acceptance criteria |
| `docs/phase_N/phase_N_plan.md` + `_exit_checklist.md` | per-phase steps and evidence gates |
| `docs/contracts/` | measurement methodology, run-bundle layout, adapter contracts |
| `docs/decision_log.md` | every design decision with alternatives considered |
| `docs/risk_register.md` | risks, triggers, mitigations, descope ladder |
| `docs/milestones.md` | calendar map |
| `docs/run_reports/` | dated work logs with commands and outcomes |
| `joulewise/`, `tests/` | the harness package + test suite (169 tests, CI-enforced) |

## Maintenance Of This Document

Updated at phase transitions and whenever advisor-visible state changes
(a gate closes, a verdict lands, the schedule moves). The "Last updated"
date above and the repository's run reports are the freshness check.
