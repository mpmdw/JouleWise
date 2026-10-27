BRIDGE_TASK_V1
{"TASK_SHAPE": "autonomous",
 "GENRE": "diagnosis",
 "ROLE": "L9-2: restart lane L9's joined acceptance; root-cause the step-9b wall-deadline refusal; carry L9 to merge-ready",
 "OBJECTIVE": "Make tests.b5_analysis.test_dry_run, test_release_equality, test_joined_probes and test_chain_fixture pass on one identified L9 source without changing registered arithmetic, thresholds, exclusions, kept counts or any frozen budget; where that needs a production or budget change, return NEEDS_RULING with the evidence instead.",
 "AUTHORITY": [
   "docs/process_traces/2026-10-20-magistrate-6cff3515/L9-RULING-ADDENDUM.md (main)",
   "docs/process_traces/2026-10-20-magistrate-4b350f47/L9-RULING.md (main)",
   "lane/2026-10-20-l9-ruling-build:.codex-report/l9-ruling-build.md",
   "configs/campaigns/v5_claim_25g83/analysis_plan_block5.md and registration_block5.md (sealed; never edited)",
   "this brief"],
 "WRITE_SCOPE": [
   "tests/b5_analysis/**",
   "joulewise/b5_analysis/**",
   ".codex-report/L9-2.md",
   ".codex-report/l9-2/**"],
 "BASE_HEAD": "0576a734df9ecf8cc155af4c4a8c8dfff30e4a37",
 "BASELINE_MANIFEST": "FILL_AT_LAUNCH (launcher writes it)",
 "BASELINE_DIGEST": "FILL_AT_LAUNCH",
 "ACCEPTANCE": [
   "A1: the 9b classification in section 4 is answered from executed evidence (rate per evaluated cell, host load, RSS/swap, thread counts at step 9b), not inferred",
   "A2: the four long modules and the six short modules of section 5 each have a completed row (tests, failures, errors, skips, exit, wall, log SHA-256) at ONE source head named in the report",
   "A3: no file outside WRITE_SCOPE changed; joulewise/powermetrics_fiducial.py, reduce.py and whole_window.py byte-identical to BASE_HEAD",
   "A4: every failure remaining at report time is classified harness / L9 code / production / host, each with its leaf condition"],
 "VERIFICATION": [
   "JW_B5_SYNTHETIC_ONLY=1 JW_B5_S10_REAL_PROGRAMS=1 PYTHONDONTWRITEBYTECODE=1 python3.13 -m unittest -v <module>, one module per detached process, fresh TMPDIR each",
   "git diff --stat BASE_HEAD..HEAD shows only WRITE_SCOPE paths"],
 "EARLY_RETURN": ["NEEDS_SCOPE", "NEEDS_RULING"],
 "OUTPUT_PROTOCOL": "bridge-report/v1"}
END_BRIDGE_TASK_V1

# L9-2 brief: restart lane L9

Written 2026-10-27 by a Claude Code session for the lead to launch. Effort: **xhigh** (non-local root cause
across harness, production and host; `.claude/skills/codex/SKILL.md` §Effort selection). Seat: Sol 6.1 in Codex
Cloud, or an Opus 5.5 cloud session if Codex Cloud executors are still failing (see §2).

## 1. Why this exists

L9 is the analysis program every block-5 number goes through, and block 5's release is a hard prerequisite for
block 6's (`.codex-report/BLIND-DRY-RUN-SCOUT.md` on `report/2026-10-22-blind-dry-run-scout`). It is the critical
path to Paper A. **No one has worked on it since 2026-10-23 07:00 UTC.** Why:

1. **Codex Cloud outage, 2026-10-22/23.** The L9-1 seat lost its VM at about 07:00 UTC on 10-23
   (`exec-server transport disconnected`, then `No usable execution environment is available`). Four long
   diagnostic and acceptance runs died with unknown outcome (`lane/2026-10-20-l9-ruling-build:.codex-report/L9-1.md`,
   SUMMARY and OPEN ISSUES). The same outage stopped the 14-seat wave of 10-22, which included L9-TWIN-REWRITE and
   L9-REVIEW: executors never started (`snapshot_materialization_failed / gateway_unavailable`;
   `docs/process_traces/2026-10-23-magistrate-786c0858/RECORD.md` item 4).
2. **The handoff dropped it.** Activation 786c0858 (10-23) moved the outage's work to local Sol seats but named
   BYTES pass-1 sizing the critical path (all six t0 before 2026-11-02) and did not re-seat L9. From RUN_STATE item 68
   on, every "Next activation" pointer lists only BYTES steps. Item 53 had called L9 the critical path; nothing
   after 10-22 mentions it. Headless activations do what the pointer says, so L9 was orphaned.
3. **No liveness check on cloud seats.** A dead seat looks the same as a running one until someone reads its branch.
   The same silent stall happened to thread 01a15b81 on 10-21 (RUN_STATE item 60).

## 2. Before starting

- **Branch.** Work on `lane/2026-10-27-l9-2`, cut from `lane/2026-10-20-l9-ruling-build` at BASE_HEAD; push only
  there. The lead merges it into the ruling-build lane after review. The report path in §7 is on this branch.
- **Seat setup (Claude cloud session).** Clone `mpmdw/JouleWise-data` and run
  `bash tools/cloud/seat_setup.sh <your JouleWise checkout>` then `source /tmp/jw-seat.env` (it installs the
  cached `/bin/zsh`, links `/opt/homebrew/bin/python3.13`, sets TMPDIR). Add `JW_B5_S10_REAL_PROGRAMS=1`
  yourself. Read the l9-joined report from that clone (`git fetch origin codex/l9-joined`).
- **Stay alive.** Long modules run 6-13 h. Start each as a detached background process with durable log, exit and
  result files, and keep working or waiting with bounded checks; a container left idle is reclaimed.
- Confirm the execution environment actually runs commands (a trivial `python3.13 -c 'print(1)'` round trip).
  If Codex Cloud still reports `gateway_unavailable`, stop and return that. Do not run on a degraded VM.
- **Run one long module at a time.** The dry-run module took 20,950-24,782 s and J6 47,231 s on the 5-vCPU VM.
  L9-1 ran four production-shaped processes in parallel, which is the load profile under which the 9b refusal is
  suspected (§4). Report `nproc` and memory at start.
- Fetch and fast-forward `lane/2026-10-20-l9-ruling-build`; record the head. Do not touch the detached old-source
  worktree convention of L9-1 unless you need it; one source head for every acceptance row (A2).

## 3. What is already known (read, do not redo)

- `JouleWise-data` branch `codex/l9-joined`, `reports/l9-joined/REPORT.md` at `be260a5`, **Final diagnosis**:
  at step 9b the pulse projection for ALPHA `neg8-window-end-r1` (59-pulse v3 calibration on the canonical ALPHA
  daily end reference) hits the frozen 120 s wall deadline (`DETECTION_PROJECTION_WALL_BUDGET_S`,
  `joulewise/powermetrics_fiducial.py`) after **5,204** evaluated cells, far below the frozen 1,710,000-cell
  budget. Detection returns `detection_nonconvergent`, `reduce._verify_instrument_calibration` returns
  `instrument_calibration_invalid`, both prechecks go ineligible (`clock_anchor_unresolved`,
  `instrument_calibration_invalid`), `whole_window` returns `precheck_ineligible`, the archived NEG-8 replay
  raises `whole_window_verdict_provenance_invalid`, and the opener refuses with `paper_custody_validator_refused`.
  Input hashes are in that section.
- The same reference in isolation (`calibration-leaf-1`) completes in **24 s** with eligible evidence, and the
  isolated full step 9b (`actual-step9b-1`) exits 0. All five full dry-run modules stop at 9b.
- The code itself says the wall deadline is a "supplementary host-safety deadline" and quarantines its firing as
  non-reproducible (`powermetrics_fiducial.py`, `detection_projection.diagnostics.reproducible`). The cell budget is
  the reproducible mechanism.
- L9-1 (`.codex-report/L9-1.md`): six short modules pass at runtime baseline `ee98a1a8f`; the observer-free and
  warm-leaf full drivers cleared 9b before the outage, with final results unknown. A chain-fixture
  creator-lifetime defect is fixed (`e77ba9e42`, sensguard; 32/32 chain tests).

## 4. The question to answer first

Is 23 ms per evaluated cell (5,204 cells in 120 s) a host effect or a code-path effect inside the long-lived
test process? Candidates, each to be confirmed or excluded by measurement, not argument:

- (a) CPU contention from parallel modules or the VM's neighbours;
- (b) memory pressure or swap after hours of cached fixtures (RSS, swap-in counts at step 9b);
- (c) thread oversubscription (BLAS/numpy threads times process-pool workers; record thread counts);
- (d) state inherited from earlier tests in the same process (caches, patched callables, fork-inherited objects)
  that changes the projection's per-cell cost;
- (e) a different input reaching the projection in the full run than in the isolated control (compare the
  hashes the projection actually reads).

Instrument with read-only observation: per-cell rate, load average, RSS and swap, thread counts, all sampled at
step 9b's projection. Then run the full dry-run module **alone** on an otherwise idle VM. If it passes, (a) is
established; say so with the numbers. If it fails alone, work down (b) to (e).

## 5. Then carry L9 to merge-ready

Modules, all at one head: `tests.b5_analysis.test_dry_run` (J1-J5), `test_release_equality` (J6),
`test_joined_probes`, `test_chain_fixture` (C5/C8/C9); and `tests.test_authentication_io`,
`tests.test_docs_freshness`, `tests.b5_analysis.test_sensitivity_guard`, `tests.b5_analysis.test_mint_kept_units`,
`tests.b5_analysis.test_s10_chain_defects`, `tests.test_r4_acceptance_oracle`. Check whether J3, J4, the missing
`fill_input` error, the two J6 failures and the joined-probe failures are all downstream of 9b before fixing any
of them separately. Fix within WRITE_SCOPE only, each fix with a test that fails without it.

## 6. What not to do

- Do not change `DETECTION_PROJECTION_WALL_BUDGET_S`, the cell budget, any tolerance, assertion, exclusion or
  kept count, or any file under `joulewise/` outside `b5_analysis/`. If the evidence says the analysis path should
  not inherit a host-safety deadline whose firing is declared non-reproducible, **return NEEDS_RULING** with that
  evidence. The question matters beyond tests: the block-5 release requires the release run to reproduce the blind
  dry run byte for byte, and a refusal that depends on host load would break that.
- Open no real block-5 data root, archive, export or key directory. Synthetic fixtures only.
- No force push, no history rewrite, no merge to main. The lead merges after review and cold passes.
- Never write fix/fixes/close/resolve before "#<n>" in a commit or report (RUN_STATE item 74).

## 7. Report

`.codex-report/L9-2.md` on `lane/2026-10-27-l9-2`, pushed after every completed module (so an outage loses nothing):
SUMMARY (one paragraph: the 9b classification and the module table status), the §4 evidence, the module table
(A2), FILES CHANGED, DECISIONS I MADE, OPEN ISSUES, NEEDS_RULING.

## 8. For the lead (not the seat)

- **Ed's decision (2026-10-27, this session): "analysis of collected data should happen as soon as a noteworthy
  block of measurements is completed"; "i want analysis asap".** As soon as L9 passes acceptance and one review,
  hold the BYTES loop and run the block-5 blind dry run on the Mac, even with BYTES sessions left. If L9 is ready
  before the s1-p1 retry has run, run the dry run first only if the s1 retry can still start before 2026-11-02
  00:00 PDT afterwards; otherwise s1 first. Binding text: the directive issue of 2026-10-27.

- Put L9 back into RUN_STATE's "Next activation" pointer as a standing item beside the BYTES steps.
- Give each cloud seat a heartbeat the activations read (last push time on its report branch); a seat silent for
  more than about 3 h gets re-seated, not waited on.
- After L9-2: independent executing review, Fable and Opus cold passes, merge; then S11 records (the
  `configs/analysis/b5/analysed_windows.json` index is absent), then the real blind dry run on the Mac between
  BYTES sessions.
