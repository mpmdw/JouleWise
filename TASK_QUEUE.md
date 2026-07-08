# JouleWise Task Queue

This is the live queue for JouleWise work. When the user gives a new task, first
triage it here instead of assuming it should happen immediately.

## Intake Rule For New Tasks

For every new user task:

1. Read `RUN_STATE.md`.
2. Read this file.
3. Check `git status --short --branch`.
4. Review the last 2-3 commits with `git log --oneline --decorate -3`.
5. Check relevant handoffs in `docs/run_reports/`.
6. Decide whether the task is:
   - urgent workspace hygiene,
   - Phase 1 evidence work,
   - Phase 2 implementation prep,
   - later-phase research work,
   - documentation/reporting,
   - or unrelated/new scope.
7. Place or update the task in the queue with priority, rationale, evidence,
   and blockers.
8. If executing it now, say why it outranks the current top task.

## Priority Scale

- **P0 Safety**: prevents accidental data loss, bad commits, broken handoffs, or
  corrupted repo state.
- **P1 Phase Gate**: required to close the current phase or unblock the next
  phase responsibly.
- **P2 Next Slice**: next implementation slice after current phase gates are
  adequately planned or closed.
- **P3 Research Expansion**: useful experiment or feature, but not needed for
  current gate.
- **P4 Polish**: quality-of-life, dashboard polish, formatting, cleanup, or
  presentation work.

## Ranking Factors

Rank higher when a task:

- Prevents accidental loss or bad Git history.
- Produces evidence for the current phase exit checklist.
- Removes ambiguity for multiple later steps.
- Is required before physical hardware time is spent.
- Is cheap to verify and reduces future confusion.
- Matches the current phase better than jumping ahead.

Rank lower when a task:

- Depends on unavailable hardware or supervisor input.
- Is a later-phase feature.
- Adds polish before a runnable vertical slice exists.
- Produces code without a clear run-bundle or test artifact.

## Machine-State Lanes (adopted C-007, 2026-07-07)

Every task carries a lane; a session picks the top task COMPATIBLE with
its machine state, not the top task absolutely:

- **[QUIET-MAC]** — measurement campaigns only: no agent fleet, no Codex
  load, idle gate will flag contamination.
- **[AGENT]** — code, docs, feasibility spikes; safe during agent-heavy
  sessions.
- **[ED-EXTERNAL]** — needs the user: advisor, calendar, device access,
  purchases, destinations.

## Current Queue

| Rank | ID | Priority | Status | Task | Evidence / Acceptance |
|---:|---|---|---|---|---|
| 1 | P2-021 | P2 Next Slice | NEW (C-014; Window-A prerequisite) [AGENT] | Generator support for drift sentinels + block-position recording in the order manifest (`scripts/generate_matrix.py`) | `short_short` start/end sentinels per model block; block position exported for analysis; must land before Window A (P2-015/P2-006) |
| 2 | P2-015 | P2 Next Slice | NEW (C-011, amended C-014) [QUIET-MAC] | Detection-floor calibration campaign — expanded Window A floors for gross request, idle-sub request, phase window, and item/level window, plus comparative MDE from same-condition repeats/ABBA | Versioned strict-valid calibration bundles; `docs/phase_2/detection_floor.md` as per-consumer table; per-metric/window-class `floor_abs_j` + `floor_cmp_j`; claim gate = `max(floor_abs, floor_cmp)`; calibration manifest hash cited by later reports; pre-Window-A lead-run tasks-sampler overhead smoke required before enabling any extra powermetrics samplers (C-015/R2) |
| 3 | P2-006 | P2 Next Slice | UNBLOCKED; acceptance extended by C-011/C-014 [QUIET-MAC] | Homogeneous baselines (slice 2M) on the Mac target — Window A two-model campaign with drift-sentinel profiles, then `docs/phase_2/baseline_results.md` with variance + prefill/decode comparison | Campaign bundles born under the FIXED validator; pass `--strict`; FAIL-CLOSED runner + counterbalanced order manifest (C-011/D-014); drift sentinel block positions recorded (C-014); claim wording per `docs/contracts/claims_ladder.md` + `docs/contracts/analysis_plans.md`; runs AFTER P2-015 in Window A |
| 4 | P3-000 | P3 Research Expansion | 3.0.1 COMPLETE + MERGED (PR #9, verdict `replay_supported`, lead-re-verified; D-035/D-036 promoted); 3.0.2+ open — 3.0.2 needs installs (R-003 user approval) and inherits the 3.0.1 harness shape + its 2 deferred hardening fixes (ledger C-8) [AGENT] | KV persistence feasibility spikes (Phase 3 Stage 3.0) | Verdicts in `docs/phase_3/kv_feasibility.md`; checklist rows are the status authority; must complete before any borrow-window scheduling |
| 5 | P2-010 | P2 Next Slice | open (C-004, rescoped C-014/C-015; quarantine rules apply) (post-2M per D-034; C-015 stop-line) [AGENT] | P2-010a minimal generic suite substrate + P2-010b smoke ladder (`affine_mod_ladder_v1` envelope validation); full scored campaign deferred | Substrate: suite/item/block markers, `BundleReader.item_windows()`, category/source/output-policy fields, per-item stop/token/response hashes, order/cache metadata, manifest validation, and per-item status model per the bank C-015 section (spec home); future `run_bundle_layout.md` contract fields for suite/item/block markers and per-item outputs are named in `docs/research_question_bank.md` and land with implementation; smoke ladder acceptance in AP-5 |
| 6 | P2-019 | P2 Next Slice | NEW (C-014) [QUIET-MAC] | `q4_l3_shape_grid_v1` campaign — Window B, AP-1, two models, n sized from Window A | 4x3 prompt/decode grid `{128,512,2048,4096}` x `{64,256,512}`; holdouts `(512,256)` and `(4096,512)`; categorical-additive fit first; top-up near-floor cells before L3 wording |
| 7 | P2-020 | P2 Next Slice | NEW (C-014) [QUIET-MAC] | Content-sensitivity sentinel — Window B, AP-6 | Five equal-shape content conditions (repeated-seed, random-token, natural prose, code-like, multilingual), n sized from Window A; request-energy deltas and MDE verdicts reported |
| 8 | P2-012 | P2 Next Slice | open (C-005, phased by C-014; runs after P2-010a substrate) [AGENT] | Implement `jw_mixed_v1` workload expansion in phases — identification core first, natural-EOS pilot second, full panels only after above-floor structure | Per `docs/research_question_bank.md` + AP-4: common-shape 512/256 `fixed_budget_exact` stratum across 6 categories, synthetic + realistic; natural-EOS pilot >=4 items/category on reasoning/JSON/chat/multilingual; additive fields and per-item stop/token/response hashes; no category claims outside matched strata |
| 9 | P2-022 | P2 Next Slice | NEW (C-015; post-2M + post-P2-010a) [AGENT] | Marker-shim energy-layer feasibility spike — verdict-shaped export path only | `external_markers_supported` / `partial(<limitation>)` / `external_markers_unsupported`; 3+ marked items, external result artifact hashed, strict bundle valid; energy-layer-only pin: no accuracy interpretation, no leaderboard join, no pass@k-energy ratio, no general adapter framework; AP row required before any L2 claim; contract in `docs/contracts/adapter_contracts.md` |
| 10 | P2-023 | P2 Next Slice | NEW (C-015; post-P2-022) [AGENT] | HumanEval import smoke — `benchmark_import` manifest + suite profile plumbing goal | Freeze subset with C-005 discipline, MIT license/provenance fields, 256/512-token completion policy; no pass@k/accuracy/capability claim; design in `docs/research_question_bank.md` |
| 11 | P2-024 | P2 Next Slice | NEW (C-015; post-Window-A) [AGENT] | Cheap-campaign shortlist — select among C5-1.6 sampler ABBA / C5-1.12 quant decomposition / C5-1.8 runtime attribution per measured floors | Explicit select-after-floors row, not stealth scope; selection/analysis task; the SELECTED campaign is then queued [QUIET-MAC]; choose one only after P2-015/2M reductions identify floor/MDE headroom; bank pointer `docs/research_question_bank.md` |
| 12 | P1-008 | P1 Phase Gate | waiting-user [ED-EXTERNAL] | Map phases to academic calendar | Colloquium/report dates + borrow window entered in `docs/milestones.md`; phase target dates derived |
| meta | P1-001 | P1 Phase Gate (user-deferred 2026-07-06 — "ignore for the moment"; R-001 mitigation continues to hold: all work stays harness-shaped) | waiting-user, deprioritized | Capture supervisor approval and scope notes | Dated notes in `docs/phase_1/phase_1_exit_checklist.md`; unblocks full D-016 closure (P2-004) when it lands |
| meta | P0-003 | P0 Safety (user-deferred 2026-07-06 — interim same-disk backup accepted for now) | waiting-user, deprioritized | Replace interim backup destination (R-016) with external/cloud location | User names the destination; one fresh restore test; R-016 → fully mitigated |
| 13 | P1-003 | P1 Phase Gate | open (elevated value: gates Q6 boundary-sensitivity, C-003) [ED-EXTERNAL] | Record wall-meter decision | Meter make/model or "unavailable" verdict plus measurement/export method (exit-checklist wall-meter section; informs D-018 boundary calibration) |
| 14 | P1-004 | P1 Phase Gate | partial [ED-EXTERNAL] | Fill network/interconnect topology plan | Physical topology, link-speed paths, and throughput method recorded in the exit-checklist network section |
| 15 | P1-006 | P1 Phase Gate | open [ED-EXTERNAL] | Confirm NVIDIA/Orin telemetry access paths | SSH/runtime/telemetry command evidence in the exit-checklist instrumentation section, or marked pending with blocker (gates slices 2K/2L) |
| 16 | P2-004 | P2 Next Slice | partial (provisional small-model pick 2026-07-06 opens 2G; full closure gated P1-001) | Close model selection (D-016) | Decision-log entry: models, revisions, artifact paths, local mirror, fallback candidate. Mid-model pick, CUDA load, GGUF paths outstanding. |
| 17 | P2-005 | P2 Next Slice | 2K fixture-first MERGED (PR #11, 2026-07-08); ALL protocol pins PROVISIONAL; live validation gated (P1-006, evidence script ready: `docs/phase_1/2k_live_verification_checklist.md`); 2L Orin open; before 2K live: pin richer nvidia-smi query fields (clocks/pstate/throttle-reasons/memory; C-015/R2) | Remote targets (slices 2K NVIDIA/vLLM/ssh, 2L Orin) | Remote bundle or documented access blocker; applicability table updated. Spec in the hardware-slice guide. |
| 18 | P2-016 | P2 Next Slice | NEW (C-011 deferred batch; post-2M / with-2K-live) [AGENT] | Critique-adjudicated queue batch: (a) post-2M controller split (experiment loop/cooldown/env capture out of controller.py); (b) node-worker protocol parity tests + table-driven validation (with 2K live); (c) NVIDIA [N/A]-row skip counts surfaced into measurement quality (with 2K live); (d) per-backend raw-to-trace strict generalization (with 2K live); (e) claims-to-evidence index seeded once 2M corpus exists; (f) schema v0.2 loader/export parity acceptance rule; (g) boundary labels propagated into report index/chart titles before any cross-boundary claims | Each item lands with its named gate; dispositions + rejected items (RemoteNodeSession per B-1, run-ID randomization per D-010/D-022, console script pre-2M) recorded in C-011 |

## Completed Queue Items

| ID | Priority | Completed | Task | Evidence |
|---|---|---|---|---|
| P2-018 | P4 Polish | 2026-07-08 | Deploy the site as a shareable Lakebed capsule with live GitHub freshness | Live at https://quiet-signal-6af8833395.lakebed.app; `scripts/pack_capsule.py` + `site_capsule/`; per-source drift vs `main`, fails soft; run report `2026-07-08-lakebed-deploy.md` |
| P2-017 | P2 Next Slice | 2026-07-08 | Honest per-source site provenance stamps | PR #13 site-observatory rewrite: `git log -1 -- <source>` per page + `+ uncommitted` dirty marker; parser-tested; run report `2026-07-08-site-observatory.md` |
| P2-011 | P2 Next Slice | 2026-07-07 | D-014 cross-repetition uncertainty (aggregate engine + manifest enrichment) | PR #6; lead-verified real n=3 experiment, byte-identical re-derivation; run report 2026-07-07-parallel-streams-session.md; C-006 trace |
| P2-008 | P2 Next Slice | 2026-07-07 | Mock telemetry × SystemClock strictly-interior stamping | PR #5; live-verified at 1 Hz real-MLX; 20 Hz workaround retired |
| P2-009 | P2 Next Slice | 2026-07-07 | Rich telemetry + idle-quality gate + environment capture | PR #4 + INT-002 (8856c04); idle gate first live true positive |
| 2M-TOOLING | P2 Next Slice | 2026-07-07 | Campaign matrix generator + resumable sequential runner | PR #3 + INT-001 (a05e54d); dry-run/resume/crash flows lead-verified |
| KV-SIZE | P3 Research Expansion | 2026-07-07 | Stage 3.0.0 kv-size helper (module + CLI verb) | PR #2; anchors verified against both mirrored models |
| FLAGSHIP-001 | P2 Next Slice | 2026-07-07 | User-directed flagship benchmark: Qwen3.5-122B-A10B-4bit on the M3 Max | 3/3 strict-valid bundles: ~304 J / 512 tok, 583 mJ/token, 46 tok/s, CV 0.3%; run report `2026-07-07-flagship-qwen35-122b.md`; first Q4 data point |
| P1-002 | P1 Phase Gate | 2026-07-06 | Mac-local Phase 1 telemetry/runtime evidence — sample captured, fields pinned, D-004 sudoers installed + `sudo -n` verified, MLX installed | Phase 1 exit checklist instrumentation section; fixture committed; live 2I run |
| P2-003 | P2 Next Slice | 2026-07-06 | Mac MLX + powermetrics vertical slice (2G, 2H, 2I) — **first real energy numbers** | Commits `3eb0acd`/`26dca41`/`b4d4173`; 3/3 strict-valid bundles: ~47 J gross / 512 tokens, 77-88 mJ/token, 257 tok/s, TTFT ~94 ms; run reports 2026-07-06 (buildout, 2H, 2I) |
| P0-002 | P0 Safety | 2026-07-06 | Measurement-corpus backup protocol (R-016) — interim destination per user direction | `scripts/backup_runs.sh`; restore test green (`validate-bundle` on restored copy); protocol in R-016; follow-up P0-003 tracks the real destination |
| P3-001 | P3 Research Expansion | 2026-07-06 | Background/related-work draft (Phase 4 Stage 4.6) | `docs/phase_4/related_work_draft.md`: 11 sources, independently verified citations, positioning claims honestly adjusted (claims 1-2 narrowed, claim 3 stands) |
| 2G (P2-003 part) | P2 Next Slice | 2026-07-06 | MLX runtime adapter — first real generation traces on the M3 Max | Commit `3eb0acd`; succeeded bundle `example-mac-mlx-mock-telemetry` (TTFT 81.5 ms, 265.8 tok/s, `--strict` valid); suite 230 OK both interpreters; implemented by Codex via `scripts/codex-bridge`, reviewed + live-verified by Claude |
| DOC-006 | P2 Next Slice | 2026-07-06 | Independent status-review intake (user-directed): all three findings verified and fixed — P1 event-timestamp hardening, P2 `validate-bundle --strict` (D-030), P3 adapter raw-write helper | Review `2026-07-06-project-status-review.md`; fixes run report `2026-07-06-status-review-fixes.md`; 226 tests OK |
| P2-007 | P2 Next Slice | 2026-07-06 | Slice 2N pre-hardware hardening (all nine items, three commits) | Run report `2026-07-06-slice-2n-pre-hardware-hardening.md`; D-024..D-029; 216 tests OK; exit-checklist 2N row closed |
| DOC-005 | P4 Polish | 2026-07-06 | External architecture review intake (user-directed): D-024 RunContext, D-025 shared bundle reader, node-worker protocol contract, 2N items 8-9 | Run report `2026-07-06-architecture-review-intake.md`; `docs/contracts/node_worker_protocol.md` |
| DOC-004 | P4 Polish | 2026-07-05 | Agent playbook (user-directed): per-mission execution guides for all remaining steps | `docs/agent_playbook.md`; pointers in `README.md`/`AGENT_PLAN.md`; Stage 4.6 seeded with named competitor set |
| P0-001 | P0 Safety | 2026-07-05 | Move repo off iCloud-synced Desktop (R-017) | New path `~/code/CapstoneRivoire/Capstone`; git + suite verified green at the new location; recorded in `RUN_STATE.md` |
| DOC-003 | P4 Polish | 2026-07-05 | Docs/meta-layer cleanup (user-directed): drift fixes, D-023 status consolidation, plan/guide dedup, R-016/R-017, Slice 2N + Stage 4.6 planned | Run report `2026-07-05-docs-meta-cleanup.md`; D-023; risk register updated |
| P2-001 | P2 Next Slice | 2026-06-12 | Mock vertical slice: slices 2A-2E | Harness runs end-to-end; `validate-bundle` green; CI mock e2e step added; 169 tests. `joulewise/{bundle,clock,controller,reduce,cli}.py` + `adapters/`; run report `2026-06-12-phase-2-mock-vertical-slice.md` |
| P2-002 | P2 Next Slice | 2026-06-12 | Repetitions + experiment manifests (slice 2F) | `run_experiment` + cooldown gate; 3-rep + kill-after-rep-2 + cooldown tests; manifest per D-005. Same run report |
| P2-J | P2 Next Slice | 2026-06-12 | Static report generator (slice 2J) | `joulewise/report.py`; matplotlib behind `[analysis]`; graceful structured failure when absent; tests skip cleanly without the extra |
| P1-005 | P1 Phase Gate | 2026-06-12 | Hailo feasibility verdict | `unsupported_workload` from official-source desk research; recorded in the Phase 1 exit checklist Hailo section |
| P1-007 | P1 Phase Gate | 2026-06-12 | Phase 2 readiness review | Recorded in the Phase 1 exit checklist; verdict "mock-first Phase 2 may begin" |
| Q-000 | P0 Safety | 2026-06-09 | Resolve the local `Energy_Benchmark_Architecture.docx` deletion decision | User confirmed the Word doc was unrelated; deletion committed in `a5d7404` |
| PLAN-001 | P1 Phase Gate | 2026-06-09 | Build evidence-shaped plans for Phases 2-5 (user-directed) | Per-phase plan + exit-checklist docs; `docs/decision_log.md` (D-001..D-019); `docs/risk_register.md`; `docs/milestones.md`; methodology/bundle-layout amendments; `AGENT_PLAN.md` restructured as index; run report `docs/run_reports/2026-06-09-phase-2-5-planning-buildout.md` |
| CI-001 | P2 Next Slice | 2026-06-09 | Add core-tests CI workflow (D-017) | `.github/workflows/ci.yml`; extended 2026-06-12 with the mock end-to-end run |
| DOC-001 | P4 Polish | 2026-06-09 | Unify Phase 1 doc scheme with Phases 2-5 (user-directed) | `docs/phase_1/` reduced to `phase_1_plan.md` + `phase_1_exit_checklist.md`; contracts moved to `docs/contracts/`; run report `docs/run_reports/2026-06-09-phase-1-doc-unification.md` |
| DOC-002 | P4 Polish | 2026-06-09 | Add advisor-facing status/plan/architecture doc + audit original sketch (user-directed) | Root `PROJECT_STATUS.md`; run report `docs/run_reports/2026-06-09-advisor-status-doc.md` |

## Current Do-Not-Do-Yet List

- (satisfied 2026-06-12) The mock bundle/reducer path and report generator
  now exist; dashboard/report work is no longer blocked.
- (satisfied 2026-06-12) The mock lifecycle is runnable, so live
  MLX/powermetrics implementation may proceed once its hardware gates open
  (P1-002 + D-016); follow `docs/phase_2/hardware_slice_implementation_guide.md`.
- (resolved 2026-06-12) Hailo feasibility has a verdict
  (`unsupported_workload`); do not implement a Hailo backend — report it as
  an applicability finding.
- Do not implement schema v0.2 before Phase 3 Stage 3.1 (design is fixed in
  D-008; implementation waits).
- Phase 3 DESK feasibility spikes (Stage 3.0.x) may run now — their gate
  (2G/2I + model) is open. Do not start Phase 3 DATA collection, hardware
  pairings, or borrow-window scheduling before 2M baselines and the Stage
  3.0 verdicts exist (C-007 wording fix; was previously stated as a
  blanket Phase 3 hold that contradicted the queue).
- Do not schedule the 3080 Ti borrow window before Stage 3.0 verdicts and the
  rehearsed runbook exist (R-006).
- Do not start Phase 3 live-split work (3.3) before offline replay (3.2) has
  produced data.
- Do not close D-016 (model selection) without P1-001 supervisor scope or an
  explicit user go-ahead.
- (satisfied 2026-07-06) Slice 2N landed; 2G/2H may start once their own
  gates (D-016 + `[mac]` install; privileged sample + D-004 sudoers) open —
  build on the post-2N seams (RunContext raw evidence, D-026 markers,
  D-027 rail rows, 2N.3 observed-token fallback).

## Queue Maintenance

At the end of substantial work:

- Update statuses in this file.
- Add new tasks discovered during the run.
- Move completed tasks below or mark them `done`.
- Update `RUN_STATE.md` with the next highest-ranked task.
