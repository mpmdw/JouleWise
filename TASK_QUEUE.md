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

## Current Queue

| Rank | ID | Priority | Status | Task | Evidence / Acceptance |
|---:|---|---|---|---|---|
| 1 | P2-006 | P2 Next Slice | UNBLOCKED + fully tooled (2026-07-07: generator + resumable campaign runner landed, PR #3 + INT-001 fix; uncertainty aggregation PR #6 ready to consume the results) | Homogeneous baselines (slice 2M) on the Mac target — NEXT ACTION: run the two-model campaign on a QUIET machine (command sequence in PR #3), then `docs/phase_2/baseline_results.md` with variance + prefill/decode comparison |
| 2 | P2-011 | P2 Next Slice | done 2026-07-07 (PR #6; stream/d014-uncertainty; council C-006 trace) | Implement D-014 statistical protocol (cross-repetition aggregation, confidence intervals, outlier flags) | `joulewise/aggregate.py` + `run_experiment` manifest enrichment; per-metric Student-t 95% CIs as serialized `UncertaintyInterval`s, MAD outliers, explicit below-protocol flags; lead-verified on a real n=3 MLX experiment incl. byte-identical re-derivation from bundles; per-member `SummaryMetrics.uncertainty` stays None by design (see C-006 DL); follow-ups: `aggregate` CLI verb, methodology-doc amendment |
| 3 | P3-000 | P3 Research Expansion | Stage 3.0.0 + 3.0.1 UNBLOCKED (2G/2I done, small model chosen) | KV persistence feasibility spikes (Phase 3 Stage 3.0) | Verdicts in `docs/phase_3/kv_feasibility.md`; must complete before any borrow-window scheduling |
| 4 | P2-008 | P2 Next Slice | done 2026-07-07 (PR #5; stream/p2-008-mock-telemetry) | Harden mock telemetry × SystemClock composition — strictly-interior stamping (centered grid + thirds fallback), 20 Hz workaround retired, lead-verified live at 1 Hz | MockTelemetryAdapter under SystemClock stamps first/last samples outside the D-026 marker window (first-sample-at-`start_sampling`, last-at-`stop_sampling`); short real-runtime windows at low power_hz reduce to 0 interior samples. Make the composition robust explicitly (interior stamping or reducer-side documented tolerance) WITHOUT breaking the FakeClock closed-form tests; bring-up config works around it at 20 Hz meanwhile. |
| 5 | P2-009 | P2 Next Slice | done 2026-07-07 (PR #4 + INT-002 follow-up; stream/p2-009-rich-telemetry) | Rich telemetry parsing + per-bundle environment capture — rich_telemetry(.idle).jsonl artifacts, idle-quality gate (first live true positive), env snapshot (per-experiment shared + FakeClock skip per INT-002) | Parse already-captured cluster/GPU DVFS residency, idle ratios, sw-requested-vs-achieved states, vendor combined_power cross-check; idle-quality gate from `gpu.idle_ratio`; env snapshot (battery/charger, Low Power Mode, memory pressure, load, display); spec in `docs/research_question_bank.md` |
| 6 | P2-010 | P2 Next Slice | open (C-004; quarantine rules apply) | Scored workload suite v1 (`affine_mod_ladder_v1`) + item/level windows | `joulewise/workloads.py` generator/scorer (stdlib); item/level marker events; `BundleReader.item_windows()`; level-window energy primary, per-item identifiability flags; per-item token count/stop reason recorded (EOS-bias audit); design in `docs/research_question_bank.md` + C-004 |
| 7 | P2-012 | P2 Next Slice | open (Ed 2026-07-07; C-005 synthesis landed — starter suite specified) | Implement `jw_mixed_v1` workload expansion (C-005) | Per the C-005 spec in `docs/research_question_bank.md`: 6 categories × 8 items, n=5, greedy `fixed_budget_exact` policy, synthetic shape-matched controls paired with hash-manifested realistic exemplars; additive config fields (`workload_profile.category`, `source_manifest`, per-item `output_policy`); category as campaign-matrix axis; per-item stop reason/token/response hash in outputs; reuses P2-010 item windows; aggregation waits on P2-011; natural-EOS 2-item pilot second. Unlocks C5-W.1..W.4 |
| 8 | P1-008 | P1 Phase Gate | waiting-user | Map phases to academic calendar | Colloquium/report dates + borrow window entered in `docs/milestones.md`; phase target dates derived |
| meta | P1-001 | P1 Phase Gate (user-deferred 2026-07-06 — "ignore for the moment"; R-001 mitigation continues to hold: all work stays harness-shaped) | waiting-user, deprioritized | Capture supervisor approval and scope notes | Dated notes in `docs/phase_1/phase_1_exit_checklist.md`; unblocks full D-016 closure (P2-004) when it lands |
| meta | P0-003 | P0 Safety (user-deferred 2026-07-06 — interim same-disk backup accepted for now) | waiting-user, deprioritized | Replace interim backup destination (R-016) with external/cloud location | User names the destination; one fresh restore test; R-016 → fully mitigated |
| 8 | P1-003 | P1 Phase Gate | open (elevated value: gates Q6 boundary-sensitivity, C-003) | Record wall-meter decision | Meter make/model or "unavailable" verdict plus measurement/export method (exit-checklist wall-meter section; informs D-018 boundary calibration) |
| 9 | P1-004 | P1 Phase Gate | partial | Fill network/interconnect topology plan | Physical topology, link-speed paths, and throughput method recorded in the exit-checklist network section |
| 10 | P1-006 | P1 Phase Gate | open | Confirm NVIDIA/Orin telemetry access paths | SSH/runtime/telemetry command evidence in the exit-checklist instrumentation section, or marked pending with blocker (gates slices 2K/2L) |
| 11 | P2-004 | P2 Next Slice | partial (provisional small-model pick 2026-07-06 opens 2G; full closure gated P1-001) | Close model selection (D-016) | Decision-log entry: models, revisions, artifact paths, local mirror, fallback candidate. Mid-model pick, CUDA load, GGUF paths outstanding. |
| 12 | P2-005 | P2 Next Slice | gated (P1-006) | Remote targets (slices 2K NVIDIA/vLLM/ssh, 2L Orin) | Remote bundle or documented access blocker; applicability table updated. Spec in the hardware-slice guide. |

## Completed Queue Items

| ID | Priority | Completed | Task | Evidence |
|---|---|---|---|---|
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
- Do not start Phase 3 work before its readiness gate — the Mac vertical
  slice (2I) and baselines (2M) must exist first (both hardware-gated).
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
