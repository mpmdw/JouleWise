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
6. If `RUN_STATE.md` contains an ACTIVE `ACTIVE_STOP_CARD`, that card
   outranks this queue. Execute or preserve the card's resume/cleanup
   instructions before considering any lower-ranked work.
7. Decide whether the task is:
   - urgent workspace hygiene,
   - Phase 1 evidence work,
   - Phase 2 implementation prep,
   - later-phase research work,
   - documentation/reporting,
   - or unrelated/new scope.
8. Place or update the task in the queue with priority, rationale, evidence,
   and blockers.
9. If executing it now, say why it outranks the current top task.

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

## Ready/Shelf Rule

A partially built or proposed task is **READY** only when it has:

- one authority document or stream-log pointer,
- bounded files/modules or a bounded artifact target,
- explicit acceptance evidence or a verification command,
- no hidden hardware/user/token-budget dependency, and
- a named lane (`[AGENT]`, `[QUIET-MAC]`, or `[ED-EXTERNAL]`).

If any of those are missing, keep the item as a shelved concept or
planning note instead of letting it compete with executable queue work.
Half-finished work should be resumed only through its authority pointer
and stop-card/checkpoint state, not by inference from prose summaries.

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

The CP-5 stop card was CLEARED 2026-07-09 (`RESUME-CP5` completed; see
the Completed table and `docs/run_reports/2026-07-09-cp5-resume.md`).
Normal ranking applies.

| Rank | ID | Priority | Status | Task | Evidence / Acceptance |
|---:|---|---|---|---|---|
| 0 | P2-015-PREP | P2 Next Slice | DONE 2026-07-09 (C-024 wave 1, PR #31; C-023/D-054 superseded the planned UCB floor rule with the false-effect guard floor) [AGENT] | P2-015 detection-floor DESIGN DOC — landed as combined floors + error budget + telemetry trust + calibration runbooks | `docs/phase_2/detection_floor.md` merged with 5.5 counterreview + final-head + tail verification; campaign sizing derivable (economics table, 180-340 total bundles incl. Window-B); run report `docs/run_reports/2026-07-09-spec-fleshing-wave1.md` |
| 0a | P2-029 | P2 Next Slice | DONE 2026-07-09 (C-025 wave 2, PR #33; D-057) [AGENT] | Reducer/aggregator uncertainty propagation + claim gates | Landed per detection_floor §3; run report `docs/run_reports/2026-07-09-spec-fleshing-wave2.md` |
| 0b | P2-030 | P2 Next Slice | DONE 2026-07-09 (C-025 wave 2, PR #34; D-056 — the runtime-order-policy option was implemented, superseding the per-repetition-manifest alternative) [AGENT] | Ordering executability: rotation policies + order provenance | Pre-campaign blocker CLOSED; run report `docs/run_reports/2026-07-09-spec-fleshing-wave2.md` |
| 0c | P2-031 | P2 Next Slice | DONE 2026-07-09 (C-025 wave 2, PR #35; D-058) [AGENT] | Token-normalization contract + stack-identity table | `docs/contracts/token_normalization.md` binding; run report `docs/run_reports/2026-07-09-spec-fleshing-wave2.md` |
| 0d | P2-032 | P2 Next Slice | DONE (core five) 2026-07-09 (C-025 wave 2, PR #36) [AGENT] | Campaign packs: Q1-Q3 split suite, Q6 rail-vs-wall, C5-2.3 KV economics | `docs/campaign_packs/`; remaining breadth moved to P2-034 |
| 0e | P2-034 | P2 Next Slice | DONE 2026-07-09 (C-026, PR #39) [AGENT] | Broad campaign packs: C5-2.7/2.8, replication runbook, C5-I.1..I.5 | Six packs in `docs/campaign_packs/`; pack lint errors=0; run report `docs/run_reports/2026-07-09-p2034-broad-packs.md`; execution gated on P2-022/P2-023/P1-006/floors per pack |
| 0f | P2-035 | P3 Research Expansion | NEW (C-025; candidate design `docs/specs/rq_energy_variance_design.md`, PR #38) [AGENT after P2-015 floors] | RQ-ENERGY-VARIANCE promotion prerequisites: council round + harness gaps G-RQVAR-* (per-bundle sampler seed recording, forced-token replay mode, replay manifests) | Promotion per registry rules; C-004 quarantine binds; floors first |
| 0g | P2-036 | P3 Research Expansion | SHELF (C-026 meeting; P2-034 left the import second family deliberately unnamed) [AGENT, after HumanEval smoke] | Second-benchmark-family source session: pick + freeze the second import family (licensing/contamination/shape discipline per `docs/campaign_packs/c5_i_1_i_2_i_5_import_family.md`; MMLU/tinyBenchmarks remain rejected as first) | Named family + frozen subset manifest passing `claims_lint --mode pack`; FLORES language-set decision (D-046/B6) may share the session |
| 0h | P2-040 | P2 Next Slice | FIX ROUND COMPLETE IN WORKTREE 2026-07-10; uncommitted, lead corpus/pathspec gate pending (C-027; pre-Window-A) [AGENT] | Reducer/gate correctness batch: zero-length measured window must FAIL strict/claim paths (ARC-3); metric-specific evidence gates (gross request must not require idle-drift evidence, STA-5); joint-edge interpolation bound (STA-6); D-058 runtime-observed token denominator wins over config (STA-7, update the locking test); zero-MAD fallback review flag (STA-8); atomic experiment-manifest writes (ARC-5); unknown-config-key warning + delete-or-implement `warmup_seconds` (ARC-8); local cleanup-failure surfaced into run quality (ARC-6) | Fix round: 908 OK/11 skipped, lint errors=0; absent `runs/` makes the loud six-corpus acceptance gate pending. Lead reviews and commits by pathspec; report `docs/run_reports/2026-07-10-p2040-fix-round.md`. Broader P2-040 remainder status remains governed by adjudication. |
| 0i | P2-038 | P2 Next Slice | NEW (C-027; HARD pre-Window-A gate) [AGENT] | Production uncertainty evidence path: real Mac runs must populate `clock_anchor_bound_s` + idle-drift bound (empirically derived, derivation recorded) + an empirical marker-to-first-sample phase bound (RIG-7); plus a shakedown assertion that an eligible production run PASSES the P2-029 gates (RIG-3: today no production path writes the required fields, so real bundles cannot pass) | A production-shaped run on the merged code yields `claim_eligibility.eligible=true` with no synthetic metadata; gate reasons exercised both ways |
| 0j | P2-039 | P2 Next Slice | NEW (C-027; P2-015 must not proceed beyond SMOKE until this lands) [AGENT] | Detection-floor executable artifact: freeze the 5<=n<10 guard factor NUMERICALLY before any calibration data (STA-4); implement the D-054 floor calculator + ABBA comparative delta; versioned floor-artifact schema + validator; hand-computed fixtures; predeclared per-regime transport rule (a floor from one stack/power/duration regime does not silently bound another, RIG-6) | Floor artifact re-derivable from calibration bundles by one command; fixtures match hand math; transport rule named in the artifact |
| 0k | RPT-001 | P1 Phase Gate | NEW (C-027/NEGSPACE; capstone-critical) [AGENT] | Report skeleton + end-to-end vertical slice: create the submission-format report source (intro/problem/contribution/harness/methodology stubs) and drive ONE reproducible bundle→analysis artifact→figure/table→claims-index row→report page path using the six legacy bundles (labeled legacy L1) | Report source builds; one report-shaped figure + table + claims row exist and are regenerable by command; legacy-L1 labels present |
| 0l | P2-042 | P2 Next Slice | NEW (C-027) [AGENT] | Frozen analysis manifest from matrix generation: cell_id/block_id/condition_id per entry, sentinel linkage, enumerated contrasts with `contrast_id` (STA-10) | Manifest emitted deterministically beside the order manifest; P2-037 consumes it |
| 0m | P2-041 | P2 Next Slice | NEW (C-027) [AGENT] | Campaign verdict split: collection-usable vs claim-ready; retire the one-bundle "publishable" verdict (STA-2/9); claim-readiness consumes reducer reason codes + D-057 cap-hit/unknown rules | A one-bundle campaign can no longer be called publishable; test updated from test_run_campaign.py:827 |
| 0n | P2-037 | P2 Next Slice | NEW (C-027; REQUIRED before any P2-006 L2 interpretation) [AGENT] | Contrast/claim analysis engine (D-053/D-054 executable path): paired/block contrast CIs, LOO verdict table, design-respecting randomization checks, Holm/BH multiplicity, floor three-way verdict (not_estimable/not_resolvable/unresolved/direction_supported/equivalent), fail-closed claim evaluator; propagated variance feeds metrology-aware intervals incl. token ratios with predeclared estimand (STA-1/2/3) | Consumes the frozen analysis manifest (P2-042) + strict-valid bundles; STATS lens counterexamples become fixtures (paired [100..500] vs [101..501] → CI [1,1]); rename `_window_claim_eligibility` to window_evidence_precheck |
| 0o | SPLIT-AP | P2 Next Slice | NEW (C-027; blocks split campaign execution) [AGENT] | Split pre-registration freeze: ONE primary estimand + service-state assumption (gross vs idle-subtracted charged states, NEG-7); BOTH monolithic references predeclared with joint adjusted contrast intervals, "split wins" only if it beats both (RIG-5); missing composite/transfer floor cells named as prerequisites | Split pack + AP amended before any split data; the non-primary basis becomes a named sensitivity analysis |
| 0p | AP-EDIT | P4 Polish | NEW (C-027 text-correction batch) [AGENT] | Analysis-plan/contract corrections: AP1 "extrapolation"→"held-out in-grid prediction" (RIG-10); replication 3-outcome rule replicated/contradicted/inconclusive (RIG-11); top-up demotion language per D-062 (RIG-4); D-053 "pending ratification" markers cleared (RIG-12/STA-12); adapter contract split modes marked Phase-3-future (ARC-10); event-schema node-field + clock-domain prose reconciled to the five-key schema and raw-verbatim rule (ARC-12) | Textual; claims_lint + doc cross-refs clean |
| 0q | DOC-008 | P2 Next Slice | NEW (C-027/D-063; stage 1 of process architecture v2) [AGENT] | Machine-readable state kernel (task id, lane, status, deps, authority, acceptance, stop-card pointer) GENERATING the RUN_STATE restart block + live queue view; PROJECT_STATUS compaction with status-history archive; retire `docs/planning_reflection_protocol.md` as standalone intake (fold goal/fences/acceptance into queue rows); two-writer rule + credential-boundary push procedure into `docs/orchestration.md` | Generated blocks byte-reproducible from the kernel; one next-action surface remains |
| 0r | DOC-009 | P4 Polish | NEW (C-027) [AGENT] | Status-authority reconciliation: stale exit-checklist rows (Phase-3 KV helper, Phase-4 related-work, Phase-1 Mac rows) reconciled with dated evidence addenda; D-023 authority restored (TOP-5/REV-8) | Checklist rows match evidence; queue closures cite matrix rows |
| 0s | MET-001 | P2 Next Slice | NEW (C-027 governance batch) [AGENT] | Audit addenda: dated D-031 breach addendum naming a05e54d/8856c04/a835c73/36d5641; C-017 addendum reclassifying the PR #18 wrong-base merge as a merge-gate breach; stop-card override record for the advisor-site episode; D-050 revisit adjudication; C-024 fix-round count clarification; (the D-054 170-vs-180 amendment was ALREADY APPLIED in the C-027 sweep commit — do not duplicate); invocation-manifest recoverability AUDIT labeling each claimed invocation recovered/partially-recovered/unrecoverable (never asserted); unrecoverable final-head review evidence marked "reported, independently unverifiable" | Addenda are append-only; no history rewrites; audit result table committed |
| 0t | RETRO-001 | P2 Next Slice | NEW (C-027) [AGENT] | Retroactive independent review of the combined diffs of the four direct-to-main commits (fresh Codex lenses + lead gate), result recorded | Findings dispositioned; RUN_STATE Current Verification updated past 36d5641 |
| 0u | REPRO-001 | P2 Next Slice | NEW (C-027/NEGSPACE-9; extends P2-027) [AGENT prep, ED-EXTERNAL tail] | Exact environment lock (analysis + Mac measurement env), publish the bundle pack, one demonstrated external re-reduction by an uninvolved party | Lockfiles committed; pack published; external re-reduction documented |
| 1 | P2-015 | P2 Next Slice | NEW (C-011, amended C-014; CP-6: + Window-B-start revalidation cell; C-027: GATED on P2-038 + P2-039 beyond the SMOKE row, and acceptance now includes a daily fixed reference cell at window start/end for between-session variance, NEG-8) [QUIET-MAC] | Detection-floor calibration campaign — expanded Window A floors for gross request, idle-sub request, phase window, and item/level window, plus comparative MDE from same-condition repeats/ABBA | Versioned strict-valid calibration bundles; `docs/phase_2/detection_floor.md` as per-consumer table; per-metric/window-class `floor_abs_j` + `floor_cmp_j`; claim gate = `max(floor_abs, floor_cmp)`; calibration manifest hash cited by later reports; pre-Window-A lead-run tasks-sampler overhead smoke required before enabling any extra powermetrics samplers and validating that the 2s env-capture settle absorbs the probe burst (C-015/R2); post-suite-build shakedown gate (C-019): before any Window-A data, ONE tiny production-shaped run through the campaign-runner path (not bare `run`) → strict validation → reduce → backup, on the merged suite-substrate code; CP-6: include a Window-B-start floor-revalidation cell |
| 1a | P2-015-SMOKE | P2 Next Slice | NEW (C-026 meeting; extracted from P2-015 acceptance prose so the quiet window starts with an explicit checklist row) [QUIET-MAC first act] | Pre-Window-A tasks-sampler overhead smoke + C-019 production-shaped shakedown (campaign-runner path -> strict -> reduce -> backup) | Both preconditions in `docs/phase_2/detection_floor.md` Ordering Preconditions; lead-run; results noted in the Window-A run report BEFORE P2-015 floor cells |
| 2 | P2-006 | P2 Next Slice | UNBLOCKED; acceptance extended by C-011/C-014 [QUIET-MAC] | Homogeneous baselines (slice 2M) on the Mac target — Window A two-model campaign with drift-sentinel profiles, then `docs/phase_2/baseline_results.md` with variance + prefill/decode comparison | Campaign bundles born under the FIXED validator; pass `--strict`; FAIL-CLOSED runner + counterbalanced order manifest (C-011/D-014); drift sentinel block positions recorded (C-014); claim wording per `docs/contracts/claims_ladder.md` + `docs/contracts/analysis_plans.md`; runs AFTER P2-015 in Window A |
| 3 | P3-000 | P3 Research Expansion | 3.0.1 COMPLETE + MERGED (PR #9, verdict `replay_supported`, lead-re-verified; D-035/D-036 promoted); 3.0.2+ open — 3.0.2 needs installs (R-003 user approval) and inherits the 3.0.1 harness shape + its 2 deferred hardening fixes (ledger C-8) [AGENT] | KV persistence feasibility spikes (Phase 3 Stage 3.0) | Verdicts in `docs/phase_3/kv_feasibility.md`; checklist rows are the status authority; must complete before any borrow-window scheduling |
| 4 | P2-010 | P2 Next Slice | ENVELOPE-GATE SCRIPT MERGED 2026-07-09 (PR #23, CP-5 resume; live-gated); REMAINING: the smoke CAMPAIGN (B=5) on a quiet-window tail [QUIET-MAC] | P2-010b remainder: affine smoke campaign execution + envelope-gate verdict on its bundles | `joulewise envelope-gate` emits the D-036 verdict from strict-valid smoke bundles (script DONE); campaign acceptance in AP-5; ledger pointer `docs/stream_logs/2026-07-08-affine-ladder.md` AFF-CHECKPOINT |
| 5 | P2-019 | P2 Next Slice | NEW (C-014; CP-6 2026-07-09: + 8192 anchor as thesis-support scope, not optional) [QUIET-MAC] | `q4_l3_shape_grid_v1` campaign — Window B, AP-1, two models, n sized from Window A | 4x3 prompt/decode grid `{128,512,2048,4096}` x `{64,256,512}`; holdouts `(512,256)` and `(4096,512)`; categorical-additive fit first; top-up near-floor cells before L3 wording; CP-6: add an 8192-prompt/decode-64 anchor on the small+mid models feeding D-048 (the Phase-3 split plan uses 8192 prompts; without it the split prediction extrapolates beyond the fitted box) |
| 6 | P2-020 | P2 Next Slice | GENERATOR BUILT AND MERGED 2026-07-08 (PR #19); manifests READY (regenerated PR #26); campaign execution Window B [QUIET-MAC]; CP-6 2026-07-09: a tiny AP-6 pilot MAY ride a Window-A tail opportunistically | Content-sensitivity sentinel campaign — Window B, AP-6 | Five equal-shape ids-native conditions, n sized from Window A; request-energy deltas and MDE verdicts; AP-6 non-generalization caveat applies (D-046) |
| 7 | P2-012 | P2 Next Slice | MANIFEST WORK DONE (manifests generated ec5224e, tokenizer-identity widened + regenerated PR #26, 2026-07-09; runner+runtime+validator hash guards merged PRs #24/#27); REMAINING: identification-core campaign after Window A [QUIET-MAC]; natural-EOS pilot + full panels later phases | Identification-core campaign (jw_mixed) after Window A | Campaign bundles strict-valid per AP-4; no category claims outside matched strata |
| 8 | P2-022 | P2 Next Slice | BLOCKED post-2M per D-041 (C-027: do NOT start before the 2M corpus exists; the C-026 "revisit after Window A" note is a revisit of SEQUENCING, not permission) [AGENT, blocked] | Marker-shim energy-layer feasibility spike — verdict-shaped export path only | `external_markers_supported` / `partial(<limitation>)` / `external_markers_unsupported`; 3+ marked items, external result artifact hashed, strict bundle valid; energy-layer-only pin: no accuracy interpretation, no leaderboard join, no pass@k-energy ratio, no general adapter framework; AP row required before any L2 claim; contract in `docs/contracts/adapter_contracts.md` |
| 9 | P2-023 | P2 Next Slice | BLOCKED post-2M per D-041, post-P2-022 (C-027: same as P2-022) [AGENT, blocked] | HumanEval import smoke — `benchmark_import` manifest + suite profile plumbing goal | Freeze subset with C-005 discipline, MIT license/provenance fields, 256/512-token completion policy; no pass@k/accuracy/capability claim; design in `docs/research_question_bank.md` |
| 10 | P2-024 | P2 Next Slice | NEW (C-015; post-Window-A) [AGENT] | Cheap-campaign shortlist — select among C5-1.6 sampler ABBA / C5-1.12 quant decomposition / C5-1.8 runtime attribution per measured floors | Explicit select-after-floors row, not stealth scope; selection/analysis task; the SELECTED campaign is then queued [QUIET-MAC]; choose one only after P2-015/2M reductions identify floor/MDE headroom; bank pointer `docs/research_question_bank.md` |
| E1 | P1-008 | P1 Phase Gate | waiting-user; ED-EXTERNAL rank E1 (C-027 sweep: rank cell now matches the recorded elevation) (C-019 reassessment: every phase target is TBD, R-012 is the biggest active management risk for an undergrad timeline; late dates force uncontrolled descoping) [ED-EXTERNAL] | Map phases to academic calendar AND capture the evaluator's acceptance bar (minimum figures, demo expectation, reproducibility threshold, whether Mac-only + split-deferral is acceptable) | Colloquium/report dates + borrow window in `docs/milestones.md`; phase targets derived; acceptance-bar notes beside the P1-001 scope notes |
| 11c | P2-027 | P2 Next Slice | TOOLING MERGED 2026-07-09 (PR #25: pack + one-command verify, live tamper-gated); REMAINING [ED-EXTERNAL]: pick 2-3 corpus bundles, publish a pack, get ONE external re-reduction | Bundle-pack publication prep: select 2-3 strict-valid corpus bundles, package with re-reduction instructions (one command), so ONE external party can run strict re-reduction — converts auditability from design property (L0) to demonstrated property | Published pack + a documented external re-reduction; until then the review doc's auditability claim stays L0-scoped |
| 11e | P2-028 | P2 Next Slice | NEW (CP-6 adjudication 2026-07-09: accepted cheap formal gate) [AGENT] | Response-hash determinism gate script: formal check that repeated same-config bundles have byte-identical per-item response hashes within rep groups | Script emits a named verdict from 2+ strict-valid bundles; existing real bundles already pass informally; rides any later agent session |
| 11d | P3-001b | P3 Research Expansion | NEW (D-048/D-049; binds split prep) [AGENT after 2M coefficients exist] | Seed the split analysis-plan row: pre-registered compositional predictions per pairing/link (incl. named same-boundary headline + at least one predicted-crossover cell if feasible), per-cell transfer-boundary labels (D-049) | AP row committed BEFORE any split hardware run; phase_3_plan amendment line landed |
| meta | P1-001 | P1 Phase Gate (user-deferred 2026-07-06 — "ignore for the moment"; R-001 mitigation continues to hold: all work stays harness-shaped) | waiting-user, deprioritized | Capture supervisor approval and scope notes | Dated notes in `docs/phase_1/phase_1_exit_checklist.md`; unblocks full D-016 closure (P2-004) when it lands |
| E0 | P0-003 | P0 Safety (user-deferred 2026-07-06 — interim same-disk backup accepted for now; C-026 meeting ESCALATION: becomes REQUIRED before Window-A data accumulates — campaign bundles on one disk are unrecoverable evidence; C-027: external-lane rank E0, the top ED-EXTERNAL item) | waiting-user, PRE-WINDOW-A [ED-EXTERNAL] | Replace interim backup destination (R-016) with external/cloud location | User names the destination; one fresh restore test; R-016 → fully mitigated |
| 12 | P1-003 | P1 Phase Gate | open (elevated value: gates Q6 boundary-sensitivity, C-003) [ED-EXTERNAL] | Record wall-meter decision | Meter make/model or "unavailable" verdict plus measurement/export method (exit-checklist wall-meter section; informs D-018 boundary calibration) |
| 13 | P1-004 | P1 Phase Gate | partial [ED-EXTERNAL] | Fill network/interconnect topology plan | Physical topology, link-speed paths, and throughput method recorded in the exit-checklist network section |
| 14 | P1-006 | P1 Phase Gate | open [ED-EXTERNAL] | Confirm NVIDIA/Orin telemetry access paths | SSH/runtime/telemetry command evidence in the exit-checklist instrumentation section, or marked pending with blocker (gates slices 2K/2L) |
| 15 | P2-004 | P2 Next Slice | partial (provisional small-model pick 2026-07-06 opens 2G; full closure gated P1-001) | Close model selection (D-016) | Decision-log entry: models, revisions, artifact paths, local mirror, fallback candidate. Mid-model pick, CUDA load, GGUF paths outstanding. |
| 16 | P2-005 | P2 Next Slice | 2K fixture-first MERGED (PR #11, 2026-07-08); ALL protocol pins PROVISIONAL; live validation gated (P1-006, evidence script ready: `docs/phase_1/2k_live_verification_checklist.md`); 2L Orin open; before 2K live: pin richer nvidia-smi query fields (clocks/pstate/throttle-reasons/memory; C-015/R2); NV-GATE-2 (C-027) hard acceptance gates at live promotion: pin vLLM stream-chunk-vs-token semantics against live protocol (ARC-1), fix NVIDIA cooldown skipping under generated experiment ids (ARC-7), extend strict raw-to-trace lineage to nvidia_smi (ARC-2, overlaps P2-016d), remote temp-artifact cleanup surfaced (ARC-6), one localhost subprocess client↔real-worker integration test (ARC-11) | Remote targets (slices 2K NVIDIA/vLLM/ssh, 2L Orin) | Remote bundle or documented access blocker; applicability table updated. Spec in the hardware-slice guide. |
| 17 | P2-016 | P2 Next Slice | NEW (C-011 deferred batch; post-2M / with-2K-live) [AGENT] (d) SUPERSEDED for powermetrics-era backends by NV-GATE-2/NV-3 ruling (ADJUDICATION.md) | Critique-adjudicated queue batch: (a) post-2M controller split (experiment loop/cooldown/env capture out of controller.py); (b) node-worker protocol parity tests + table-driven validation (with 2K live); (c) NVIDIA [N/A]-row skip counts surfaced into measurement quality (with 2K live); (d) per-backend raw-to-trace strict generalization (with 2K live); (e) claims-to-evidence index seeded once 2M corpus exists; (f) schema v0.2 loader/export parity acceptance rule; (g) boundary labels propagated into report index/chart titles before any cross-boundary claims; (h) require `summary_provenance` in the strict succeeded-summary key list (C-014 scout); (i) align `token_count_source` value naming with the claims ladder's `config fallback` vocabulary (C-014 scout) | Each item lands with its named gate; dispositions + rejected items (RemoteNodeSession per B-1, run-ID randomization per D-010/D-022, console script pre-2M) recorded in C-011 |

## Completed Queue Items

| ID | Priority | Completed | Task | Evidence |
|---|---|---|---|---|
| CODEX-BRIDGE | P0 Safety | 2026-07-09 | Make the Claude Code → Codex bridge durable, full-session capable, and process-safe | Root `AGENTS.md`; tracked Claude subagent + `/codex` command; protocol checker; Claude-approved live `codex` + same-thread `codex-reply` smoke; report `2026-07-09-claude-codex-mcp-bridge.md` |
| RESUME-CP5 | P0 Safety | 2026-07-09 | Resume and complete the CP-5 pre-campaign review session | 7 PRs merged (#22..#28); stop card CLEARED; CP-6 dispositions in the stream log; run report `2026-07-09-cp5-resume.md`; suite 822 OK |
| P2-026 | P2 Next Slice | 2026-07-09 | D-033 strict legacy-bypass close (frozen six-identity allowlist) | PR #22; live-gated 6/6 corpus + tamper-fails + spoof probe fails closed |
| P2-025 | P2 Next Slice | 2026-07-09 | Campaign-runner expected-vs-realized prompt-hash check (+ runtime/validator closure) | PRs #24 + #27; fail-closed with type-discriminated sidecar inference; live-gated classifier truth table; 48/48 real-tokenizer closures |
| P2-010b-GATE | P2 Next Slice | 2026-07-09 | Envelope-gate analysis script (E1-E4 + E5 advisory, D-036 verdicts, CLI) | PR #23; live-gated on the real mock affine bundle incl. refusal cases |
| P2-027-TOOLING | P2 Next Slice | 2026-07-09 | Bundle-pack publication tooling (pack + one-command verify) | PR #25; live pack→verify→tamper→verify(2) |
| CAPTURE-HARDENING | P2 Next Slice | 2026-07-09 | Pre-campaign capture: output token IDs, fail-closed sampler pin (D-047 amendment), model weight hashing, env versions, hash-domain closure | PR #27; live MLX gate incl. two full jw_mixed suite runs |
| P2-012-MANIFESTS | P2 Next Slice | 2026-07-09 | Tokenizer identity widening + real-tokenizer manifest regeneration | PR #26; byte-identical double-regen; counts 512/512 |
| ADVISOR-SITE | P4 Polish | 2026-07-09 | Advisor status site + suite_next draft-spec packet landing (D-051) | PR #28; stop-card sha-verified intact; site regenerated with real renderer |
| P2-018 | P4 Polish | 2026-07-08 | Deploy the site as a shareable Lakebed capsule with live GitHub freshness | Live at https://quiet-signal-6af8833395.lakebed.app; `scripts/pack_capsule.py` + `site_capsule/`; per-source drift vs `main`, fails soft; run report `2026-07-08-lakebed-deploy.md` |
| P2-021 | P2 Next Slice | 2026-07-08 | Drift sentinels + block-position covariates in the 2M generator | PR #15 (merged 8765ee1); fail-loud sentinel manifest; campaign-log covariate echo; run report `2026-07-08-suite-science-expansion.md` |
| P2-017 | P2 Next Slice | 2026-07-08 | Honest per-source site provenance stamps | PR #13 site-observatory rewrite: `git log -1 -- <source>` per page + `+ uncommitted` dirty marker; parser-tested; run report `2026-07-08-site-observatory.md` |
| P2-011 | P2 Next Slice | 2026-07-07 | D-014 cross-repetition uncertainty (aggregate engine + manifest enrichment) | PR #6; lead-verified real n=3 experiment, byte-identical re-derivation; run report 2026-07-07-parallel-streams-session.md; C-006 trace |
| P2-008 | P2 Next Slice | 2026-07-07 | Mock telemetry × SystemClock strictly-interior stamping | PR #5; live-verified at 1 Hz real-MLX; 20 Hz workaround retired |
| P2-009 | P2 Next Slice | 2026-07-07 | Rich telemetry + idle-quality gate + environment capture | PR #4 + INT-002 (8856c04); idle gate first live true positive |
| 2M-TOOLING | P2 Next Slice | 2026-07-07 | Campaign matrix generator + resumable sequential runner | PR #3 + INT-001 (a05e54d); dry-run/resume/crash flows lead-verified |
| KV-SIZE | P3 Research Expansion | 2026-07-07 | Stage 3.0.0 kv-size helper (module + CLI verb) | PR #2; anchors verified against both mirrored models |
| FLAGSHIP-001 | P2 Next Slice | 2026-07-07 | User-directed flagship benchmark: Qwen3.5-122B-A10B-4bit on the M3 Max | 3/3 strict-valid bundles: ~304.0 J gross / ~298.7 J idle-sub per 512-tok request, 582-585 mJ/generated-output-token idle-sub (mean 583.4), 46 tok/s, gross CV 0.3% within one warm-cache session; legacy L1 (bases corrected 2026-07-09, C-027); run report `2026-07-07-flagship-qwen35-122b.md`; first Q4 data point |
| P1-002 | P1 Phase Gate | 2026-07-06 | Mac-local Phase 1 telemetry/runtime evidence — sample captured, fields pinned, D-004 sudoers installed + `sudo -n` verified, MLX installed | Phase 1 exit checklist instrumentation section; fixture committed; live 2I run |
| P2-003 | P2 Next Slice | 2026-07-06 | Mac MLX + powermetrics vertical slice (2G, 2H, 2I) — **first real energy numbers** | Commits `3eb0acd`/`26dca41`/`b4d4173`; 3/3 strict-valid bundles: ~47.2 J gross / ~44.4 J idle-sub per 512-token request, 79.4-90.5 mJ/generated-output-token idle-sub (mean 86.8), 257 tok/s, TTFT ~94 ms; legacy L1 (bases corrected 2026-07-09, C-027; the old 77-88 figure used the prompt+output denominator); run reports 2026-07-06 (buildout, 2H, 2I) |
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

## Shelved Follow-Ups With Triggers (C-027 disposition ledger — REV-10)

Previously promised follow-ups whose queue rows had silently died; each
now has an explicit disposition:

- D-013 SSH-controlled vs co-resident controller comparison — SHELF,
  trigger: first 2K live session (validation cell rides that session).
- Empirical corpus for the 0.40 GPU-idle contamination threshold — SHELF,
  trigger: Window-A calibration data exists (P2-015 output feeds it).
- `dvfm_states` slimming option — SHELF, trigger: bundle-size pain during
  the 2M campaign; otherwise declined as premature.
- Cold-load / model-load-energy capture — DECLINED for the capstone scope
  (CP-5 deferral made permanent unless an AP row claims it; warm-cache
  protocol is the declared scope).

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
