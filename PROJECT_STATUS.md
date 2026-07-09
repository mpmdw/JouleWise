# JouleWise: Project Status, Plan, And Architecture

Audience: project advisor. This is the standalone monitoring document - it
summarizes what the project is, how it is built, where it stands, and what
it needs, without requiring any other file. Pointers into the repository
are provided for anyone who wants the full evidence trail.

- Last updated: 2026-07-09 (spec-fleshing waves 1+2, C-024/C-025:
  capstone scope contract, contrast-level statistics + analysis
  registry, P2-015 detection-floor design, canonical question registry
  (PRs #29..#32, D-052..D-055); then uncertainty propagation + claim
  gates, suite order policies, token-normalization contract, campaign
  packs, claims-lint CI enforcement (PRs #33..#38, D-056..D-059). Then
  P2-034 broad campaign packs (PR #39, C-026) completed the pre-hardware
  campaign surface. Next QUIET-MAC work: C-019 shakedown + P2-015
  calibration; AGENT lanes: P2-022/P2-023 post-2M, P2-035 post-floors)
- Project phase: Phase 1 closing; Phase 2 in progress - instrument
  CAMPAIGN-READY; P2-013 evidence-integrity and P2-014 provenance fixes
  are complete; workload-suite build is merged; CP-5 pre-campaign review is
  COMPLETE and CLEARED (2026-07-09, PRs #22..#28; see
  `docs/run_reports/2026-07-09-cp5-resume.md`); the P2-015 design doc is
  merged; next is C-019 shakedown plus P2-015 quiet calibration (Window A)
- Repository: `github.com/mpmdw/JouleWise` (branch `main`)
- Live status site: https://quiet-signal-6af8833395.lakebed.app (Lakebed
  capsule; `/status.html` is the advisor cockpit and shows live overlays
  plus a drift banner when the repo has moved past the snapshot)

## This Update (as of 2026-07-09, advisor status cockpit) — 30-second read

**The public preview is being upgraded for live advisor observation.**
The project-status page remains generated from repository evidence, but
Lakebed now has a narrow fail-soft live overlay contract: freshness from
GitHub commit checks plus parsed current fields from `PROJECT_STATUS.md`,
`RUN_STATE.md`, `TASK_QUEUE.md`, and the risk register. The advisor
cockpit adds live snapshot state, attention items, campaign readiness,
evidence cards, and claim-ceiling panels; the Story page drops
hand-authored volatile counts. The operational policy is D-051: repo
markdown remains the source of truth and Lakebed never hides static
provenance. Current work follows `TASK_QUEUE.md`: C-019 shakedown, then
P2-015 quiet calibration for Window A (the CP-5 stop card was cleared
2026-07-09).

## Previous Update (as of 2026-07-08, all four streams merged) — 30-second read

**Everything landed.** The multi-stream session merged as four PRs:
P2-013 and P2-014 are closed — all 31 audit pins fixed, the suite passed
with zero expected failures (current count authority is RUN_STATE.md
Current Verification; the suite-build merge was 732 tests and the
post-alignment state is 734), bundle provenance
now records prompt/workload identities, and `validate-bundle --strict`
includes the powermetrics raw-plist-to-trace gate plus the legacy
additive-summary comparison. The six existing real corpus bundles pass
strict read-only and unrewritten; strict proves re-derivation of the
recorded evidence, not independent rerunning of the hardware session.
New-era bundles must carry shape-valid provenance to pass. The Stage
3.0.1 KV spike is merged with a lead-reverified verdict of
`replay_supported` (tokens identical; cache size +0.018% vs prediction)
— Phase 3's central technical risk is retired on current hardware. The
fixture-first 2K NVIDIA stack is merged; ALL its protocol pins remain
PROVISIONAL until first live hardware contact (the live-verification
checklist is ready). The independent project critique now carries a
second-pass reassessment (its recommendations that became code are
marked resolved; 16/17 of its checkable claims were lead-verified
against file evidence): `docs/project_critique_review.html`. Next: the
detection-floor calibration (P2-015) then the 2M two-model baseline
campaign on a quiet machine. Reader-facing status below defers to the
phase checklist matrix rows for per-item authority.

## Previous Update (2026-07-07, fifth update) — 30-second read

**The instrument grew four capabilities in one session and is now
campaign-ready.** Five parallel work streams landed (PRs #2-#6):
(1) **statistical uncertainty** — every multi-repetition experiment now
carries per-metric 95% confidence intervals with outlier detection and
explicit below-protocol flags, re-derivable byte-identically from the
raw evidence bundles (verified on a live 3-repetition run:
99.19 ± 1.36 mJ/output-token); (2) **contamination detection** — an
idle-window quality gate that mechanically flags runs taken on a
non-quiet machine (it caught its first real contamination during
verification); (3) **deep telemetry** — per-sample GPU/CPU-cluster
frequency and residency forensics plus a machine-state snapshot in
every bundle; (4) **campaign automation** — a deterministic
config-matrix generator and a resumable sequential runner, so the
planned two-model baseline matrix (4 workload shapes × 2 models × 5
repetitions) runs unattended. A review council also produced a
hardware-tiered research agenda: 16 questions answerable on current
hardware alone, 10 more behind planned gates
(`docs/research_question_bank.md`). The P2-013 evidence-integrity and
P2-014 provenance fixes are now complete; next Mac corpus step is the
baseline matrix on a quiet machine.

## Previous Update (2026-07-07, fourth update) — 30-second read

**A flagship-class model is now benchmarked.** Qwen3.5-122B (Feb 2026
generation, 122B-parameter mixture-of-experts with 10B active, a
reasoning model) ran through the identical harness and workload on the
M3 Max: **~304 J per 512-token request (~583 mJ/token) at 46 tokens/s,
repeatable to 0.3% across repetitions** — alongside the earlier 1.5B
model's ~47 J (~87 mJ/token at 257 tok/s). First cross-model finding:
the two measured points differ in size, architecture, and quantization,
so they are not a demonstrated scaling law. They are, however,
consistent with the fixed-vs-marginal structure Q4 models: decode power
barely moved (~23.5 → ~27.5 W), while the bigger model's cost showed up
mostly as time. Also this update: the
research agenda grew to six named questions (Q4-Q6) after a
multi-model review council, with a curated question bank
(`docs/research_question_bank.md`) and an instrument roadmap (richer
telemetry parsing, a difficulty-graded scored workload suite, and
implementing the statistical-uncertainty protocol) queued.

## Update Ledger

| date | label | one-line outcome | run-report link |
|---|---|---|---|
| 2026-07-06 | third update / first real energy | Mac slices 2G/2H/2I landed and produced strict-valid M3 Max measurements: ~47 J gross per 512-token request, ~77-88 mJ/output-token, TTFT ~94 ms, 257 tok/s, gross CV 1.4%, powermetrics observed at ~8.8-8.9 Hz, with prefill energy ~0.03 J. | `docs/run_reports/2026-07-06-slice-2i-first-real-energy.md` |
| 2026-07-06 | third update / powermetrics telemetry | The powermetrics telemetry adapter and privileged sampling path were brought up, preserving raw plists and exposing the real sampling-rate constraints. | `docs/run_reports/2026-07-06-slice-2h-powermetrics.md` |
| 2026-07-06 | third update / pre-hardware hardening | Slice 2N closed the evidence-path hardening before real hardware: raw evidence retention, measured-window markers, rail validation, shared bundle reading, and post-hoc reduction. | `docs/run_reports/2026-07-06-slice-2n-pre-hardware-hardening.md` |
| 2026-06-12 | first/second updates / mock vertical slice | The mock-first harness reached an end-to-end auditable run path before hardware time: typed config to complete bundle, validation, reduction, and report. | `docs/run_reports/2026-06-12-phase-2-mock-vertical-slice.md` |

## Summary

JouleWise is a reusable, typed, extensible benchmark harness for measuring
the energy of LLM inference across heterogeneous local hardware. The name
nods to JouleSort and Splitwise: energy measurement is the spine of the
system; disaggregated ("split") inference - running prefill and decode on
different machines with the KV cache transferred between them - is the
validating research study, not the whole architecture.

The capstone now has two explicit claim tracks. The guaranteed capstone is
auditable local LLM energy measurement: the harness plus the Apple-Silicon
characterization it can already execute on the M3 Max. Split
(disaggregated) inference remains the differentiating validating study;
when Phase 3 hardware and feasibility gates land, it upgrades the capstone
from local characterization to a split-energy crossover study.

The frozen capstone headline, fallback claims, contribution ladder, and
minimum-viable stop-lines are now recorded in
`docs/contracts/capstone_scope.md`; that contract is the scope pointer for
reader-facing wording under the claims ladder.

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
- **Q4** (added 2026-07-07, council C-003): What fixed-vs-marginal energy
  model `E = fixed + prefill(prompt_tokens) + decode(output_tokens)` does
  each target/model/quantization follow — and can split-run energy be
  predicted compositionally from monolithic coefficients plus transfer
  measurements?
- **Q5** (C-003/C-007): On one machine, do workload/model/quantization
  efficiency rankings stay stable as workload shape, model, and
  quantization change, or where do they flip? A cross-device ranking
  extension is hardware-gated.
- **Q6** (C-003; gated on the wall meter): Does the measurement boundary
  (platform rails vs AC wall power) change the conclusions?

Current question status, aliases, gates, and claim ceilings live in the
canonical live index, `docs/research_question_registry.md`. The curated bank
of further candidate questions and deliberately killed ones remains the
historical/deliberative record in `docs/research_question_bank.md`; the
measurement noise floor / detection limit is treated as the methodology
centerpiece rather than a numbered question.

The capability map by claim ceiling is reflected in
`docs/research_question_registry.md` (C-015), alongside the suite architecture
v2 and benchmark interop direction; the guaranteed-capstone stop-line is
recorded in the Phase 2 plan.

## Status At A Glance

| Phase | Scope | Status |
|---|---|---|
| 1. Approval, feasibility, measurement design | contracts, methodology, hardware feasibility evidence | **in progress** - design artifacts complete; Hailo verdict + Phase 2 readiness closed (2026-06-12); supervisor/calendar/hardware-access gates open |
| 2. Harness, Mac vertical slice, homogeneous baselines | runnable harness, first real measurements, per-target baselines | **in progress** - Mac vertical slice COMPLETE (2026-07-06); flagship 122B-MoE benchmarked (2026-07-07); P2-013/P2-014 integrity and provenance fixes complete (31 audit pins fixed; strict now includes raw-to-trace and provenance gates); instrument upgrades landed 2026-07-07 (statistical uncertainty per D-014, contamination gate, deep DVFS telemetry, campaign automation); suite-science hardening + expansion MERGED 2026-07-08 (analysis-plans contract D-038, Q4 L3 grid design, drift sentinels, Window-A capture covariates, suite architecture v2 + benchmark-interop direction, capability map — see the research-questions pointer above); the WORKLOAD SUITE ITSELF is now BUILT and MERGED (2026-07-08, PRs #17-#20: generic suite substrate with one-manifest/marker/window mechanism, mock+MLX suite execution, affine_mod_ladder_v1 core + smoke manifest, six jw_mixed_v1 category generators + five content-sentinel conditions; adjudicated pins D-044..D-047; live-verified on real Apple-Silicon MLX) — 2M baselines are fully tooled and covariate-complete; 2K fixture-first implementation is MERGED (2026-07-08) with ALL protocol pins PROVISIONAL pending live hardware validation; 2L gated on device access |
| 3. Disaggregation, KV replay, interconnect sweep | split-energy decomposition, crossover dataset | planned (feasibility-first) |
| 4. Characterization and analysis | statistics, figures, claims audit | planned |
| 5. Presentation and submission | report, colloquium, reproducible release | planned |

## Capstone Artifact Map

| chapter/report-component | owning doc or deliverable | status | missing evidence |
|---|---|---|---|
| Background / related work | Phase 4 Stage 4.6, `docs/phase_4/related_work_draft.md` | drafted (11 verified sources) | background-chapter assembly and the Phase 4 exit pass |
| Measurement methodology | `docs/contracts/measurement_methodology.md` | complete | Phase 4 ratification may amend statistical details against observed variance |
| Harness / instrument | `joulewise/` | complete and campaign-ready | new-era bundles must carry shape-valid provenance to pass strict |
| Apple-Silicon characterization / homogeneous baselines | Phase 2 Slice 2M, `docs/phase_2/baseline_results.md` | unblocked after P2-013/P2-014 | needs the 2M baseline corpus |
| Split-inference study | Phase 3 | planned | needs KV-feasibility spikes plus a real pairing, or the synthetic-transfer + analytical-composition floor |
| Results / limitations + claims audit | Phase 4 Stages 4.3-4.5 | planned | needs the analysis dataset and detection-floor gate |

Complete so far (all verifiable in the repository):

- A runnable harness: from a typed config, one command
  (`python3 -m joulewise run ...`) produces a complete, schema-valid,
  auditable run bundle and reduces it to energy/latency summary metrics -
  proven first on deterministic mock adapters (controller, bundle
  contract, and reducer math verified without hardware) and now running
  live on the Mac target. Bundle writer, controller
  lifecycle, reducer, static-HTML report generator, and CLI verbs `run` /
  `validate-bundle` / `reduce` (post-hoc re-derivation of summary metrics
  from the recorded power trace and events) / `report`. Strict validation
  now also re-derives powermetrics traces from raw plist evidence, checks
  legacy additive-summary compatibility, and requires shape-valid
  provenance on new-era bundles. All bundle consumers read through one
  shared, tested read layer, so displayed numbers can never diverge from
  reported ones.
- Typed config and output schemas with validation, JSON-Schema export, and
  a CLI, plus a passing test suite (current count and skips live in
  RUN_STATE.md Current Verification; run in CI on every push, including a
  mock end-to-end run + bundle validation); emitted configs
  round-trip their own published schema, and config hashes (run identity)
  are pinned by test.
- Adapter interface contracts (runtime / telemetry / transport), the run
  bundle artifact contract, and the measurement methodology (idle
  subtraction, measurement boundaries, clock synchronization, statistical
  protocol - highlights below).
- Evidence-shaped plans for every phase, a design-decision log (37
  decisions, each with the alternatives considered), a risk register with
  an explicit descope ladder, and example configs for the Mac and mock
  targets.
- The complete Mac vertical slice: the MLX runtime adapter (2G), the
  `powermetrics` telemetry adapter (2H, parser pinned to a captured
  privileged sample, raw plists preserved verbatim in every bundle), and
  the flagship integration (2I) — three strict-valid repetition bundles
  of real energy measurements on the M3 Max (~47 J gross per 512-token
  request, ~77-88 mJ/generated token, TTFT ~94 ms at 257 tokens/s,
  provisional model Qwen2.5-1.5B-Instruct-4bit mirrored locally).
- The report's related-work survey draft (11 sources with verified
  citations and an honest positioning audit) and a measurement-data
  backup protocol with a passed restore test.

Not yet started: the remote real-hardware adapters — NVIDIA/vLLM +
Jetson Orin live validation (2K/2L, gated on device access). The 2K
fixture-first implementation is MERGED (PR #11, 2026-07-08: protocol v1,
SSH transport, `nvidia-smi` + vLLM adapters, registry wiring), but all
protocol pins remain PROVISIONAL until live
hardware contact; a P1-006 evidence checklist exists there. Code-level
specs are in `docs/phase_2/hardware_slice_implementation_guide.md`. The
mock-first core landed first by design, so measurement code is never
debugging the harness and the instrument at the same time.

Waiting on external input (none of it blocks the current work):

1. NVIDIA / Jetson Orin device access evidence — the one hard gate left,
   for the remote-target slices 2K/2L. (The `nvidia_3050` in the
   architecture table is the owned always-available NVIDIA target; the
   3080 Ti is a separate, borrowed card used only for Phase 3's
   interconnect sweep.)
2. Calendar anchors: colloquium date, report deadline, and the 3080 Ti
   borrow window, to derive phase target dates.
3. Advisor scope confirmation (see the sanity-check note above) —
   finalizes model selection; deliberately deprioritized while all work
   remains harness-shaped and valuable under any scope.

Closed since the last revision: the Mac privileged-telemetry gate — the
`powermetrics` sample was captured and the scoped sudo rule installed
(2026-07-06), which is what enabled the vertical slice above.

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
  figures F1-F12 (baselines, traces, phase asymmetry, split decomposition,
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

Minimum viable outcome (worst-case floor; still a complete, defensible
capstone if reached):
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

Known: the Mac authorization gate closed 2026-07-06 (privileged sample
captured, scoped sudo rule installed); remote-device access (NVIDIA,
Orin) is the remaining hardware gate. Work paused 2026-06-13 to
2026-07-04 (planned break, recorded in `docs/milestones.md`).

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
| `joulewise/`, `tests/` | the harness package + test suite (current count and skips in RUN_STATE.md; zero expected failures, CI-enforced) |

## Process Note

The machinery exists to protect measurement claims from unchecked summaries,
stale assumptions, and review-induced drift.

This project is developed by a human researcher directing a multi-agent
AI system he designed and iteratively engineered over the course of the
project — the orchestration itself is a second, deliberate piece of
engineering alongside the benchmark, and by now it is interesting in its
own right.

The full description lives in `docs/orchestration.md` (the loop, the
roles, the artifact system, and how the topology itself evolved under
its own review machinery); this section is the summary.

**The division of labor.** Ed sets the research direction, the
methodology standards (the decision log's non-negotiables: raw-evidence
bundles, idle subtraction, named measurement boundaries, no
unauditable claims), the hardware and access decisions, and — the part
that is easy to underrate — the *process policy*: every rule below
exists because he observed a failure or an opportunity and issued a
standing instruction. The AI staff executes: a lead agent (Claude,
Anthropic's Fable-class model) is the final reviewer and single point
of accountability: decomposition, design adjudication, every final diff
gate, live verification, merges, and bookkeeping. A second, independent
model (OpenAI Codex gpt-5.5) does the volume: implementation against
pinned specs, adversarial review lenses, test writing, and
fresh-instance test auditing. A third tier (Claude Opus) serves as
specialist sweeper. Cross-model review is load-bearing by design: the
attributed catch record shows the models and review layers catching
different classes of defect.

**The machinery, briefly.** Independent tasks run as parallel git
worktrees, the lead driving each stream's Codex pipeline directly (a
topology that is itself the product of a signed cross-model
meta-review, then validated by a full session with zero coordination
stalls — the evolution is traced in `docs/orchestration.md`). Every
implementation passes through a layered pipeline: a design argument
round (the implementer must argue trade-offs before coding),
fresh-instance counterreview lenses with lead-triaged dispositions, a
test-amplification round, a writer-never-reviews-its-own-tests audit,
the lead's diff gate, and lead-side live verification on real hardware
— the one layer never delegated, because it has repeatedly caught
blockers whose own tests were green (the tests encoded the same wrong
assumption as the code). Merges add their own gate: a
pre-merge oversight pass by fresh reviewers with distinct angles, and a
standing *final-head rule* — any commit landing after the last review
round gets one more fresh review before merge (its first application
caught a crash path in a "trivial" late fix). After parallel streams
merge, a dedicated integration review hunts the cross-stream defects no
per-stream review can see (two interaction defects on its first outing, two more on its second). An
event-driven review council convenes for contract-bearing work, and —
per Ed's instruction — its *deliberations* are recorded, not just its
verdicts: the council log preserves positions, the reasoning exchanged,
who prevailed and why, and overridden dissents, so a future reader (or
model) can reconstruct why any decision was made.

**The paper trail (every claim auditable).** Each fact has one home:
`docs/decision_log.md` — the binding design decisions (the log is the count authority), each with
alternatives considered and revisit conditions; `docs/council_log.md`
— the deliberation record; `docs/stream_logs/` —
per-stream decision ledgers committed *with* the code they justify
(wrong decisions are superseded in place, never erased);
`docs/run_reports/` — one record per session with verification
evidence, a per-review-layer catch table, and a delegation-calibration
ledger (outcomes assigned by the lead after the gate, never
self-reported; prompt-defects separated from model-defects). The whole
loop is self-instrumenting: every review layer's unique catches are
attributed and tallied, and a layer that stops earning its keep is
dropped by its own evidence rule (one already has been). Delegation
boundaries move on calibration evidence, not intuition. Lessons are
folded into the process playbooks the same session they are learned —
measurably: one failure mode recurred five times before its fix was
distilled, and zero times after. The loop even reviews itself: a
meta-review consensus (C-009) redesigned the coordination topology, and
the next session (C-010) validated the redesign with a zero-stall run.

**What one day of this looks like (2026-07-07).** Five implementation
streams plus a repo-wide test audit ran concurrently: statistical
uncertainty, contamination detection, deep DVFS telemetry, campaign
automation, and a KV-cache size model. All five merged the same day;
the test suite grew 254 → 369; the layered review recorded thirteen
attributed catches including three blockers that no single reviewer
would plausibly have found together. One blocker surfaced only when the
real CLI was run against code whose own tests were green, because the
tests encoded the same wrong assumption as the code.

**How the scope grew.** The project began as an architecture sketch for
"measure LLM inference energy on edge hardware." Contracts-first
engineering turned that into an auditable instrument: typed configs,
self-contained evidence bundles, a strict re-reduction validator. The
mock vertical slice proved the math without hardware; the Mac slice
produced the first real joules; the flagship run put a 122-billion-
parameter mixture-of-experts model through the identical harness and
yielded the first real cross-model observation: two confounded points
that differ in size, architecture, and quantization, with energy/token
behavior consistent with the fixed-vs-marginal model while decode power
stays nearly flat — the big model costs time, not watts. This week the
instrument gained the statistical and
forensic machinery above, and a steelmanned, devil's-advocated research
agenda of 31 tiered questions — 16 answerable on the current hardware
alone (`docs/research_question_bank.md`). The pattern throughout:
capability first, claims only when the instrument can defend them.

**And the most recent day (2026-07-07/08).** Four checkpointed streams
were resumed, completed, and merged in one session: the integrity/
provenance overhaul (all 31 audit-pinned defects fixed; strict
validation now re-derives the power trace from raw evidence), the docs
package, the KV-cache replay feasibility verdict, and the complete
fixture-first NVIDIA stack. The layered review recorded ~30 attributed
catches, including two blockers no implementer's tests could see (a
provenance hash that did not prove the actual generation input; a
validation-gate bypass via mutable metadata), two pinned wire contracts
overturned by review before they could ever touch hardware, and one
fabricated-evidence defect caught only at the lead's diff gate. The
suite went 415 → 546 tests with zero expected failures, and the lead
never wrote implementation code and never skipped a gate.

**Where to look.** `docs/orchestration.md` is the process description.
`docs/council_log.md` is the deliberation record — C-006
is a full orchestration trace of the five-stream day; C-009/C-010 are
the topology meta-review and its validation; C-011 is the critique
counter-review. `docs/decision_log.md` holds the binding design
decisions with alternatives considered (the log is the count authority).
`docs/run_reports/` narrates each working session, with per-layer catch
tables and the delegation-calibration ledger. The executable
orchestration playbooks live outside this repository as reusable
skills (council, delegation, multi-stream worktrees, adversarial
review, and a top-level operation-loop that sequences them), so the
machinery survives this project and transfers to the next one.

## Maintenance Of This Document

Updated at phase transitions and whenever advisor-visible state changes
(a gate closes, a verdict lands, the schedule moves). The "Last updated"
date above and the repository's run reports are the freshness check.
