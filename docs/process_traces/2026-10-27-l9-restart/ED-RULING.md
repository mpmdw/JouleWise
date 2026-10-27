# Ed's ruling, 2026-10-27: L9 acceptance without full-size synthetic runs; the blind dry run is the full-size test

**Status: binding (Ed, owner).** Given in Claude Code cloud session 015ASG1T on 2026-10-27, Ed present.

**Ed's words.** Asked whether the full-size synthetic test runs were needed ("do we need to do all this or is this
excessive caution?"), Ed answered the proposal below: "yes do it ... just get l9 working again - i want to know the
full front to back results of block 5 and 6 asap". Directive issue #587 carries the scheduling side.

**What it amends.** The Build paragraph of the L9 ruling
(`docs/process_traces/2026-10-20-magistrate-4b350f47/L9-RULING.md`): "Then the executing review, the J1-J6 and C5-C9
reruns on the Mac with no conditional seams, and the cold Fable and Opus passes at L9's merge." It amends nothing
registered or sealed: the block-5 registration, analysis plan, flag catalog, estimators, exclusions, kept counts,
blinding, the independent recompute and its agreement bars, and the release record are unchanged.

## Why

- The blind dry run reads the real, immutable block-5 archives with every number closed. A tooling refusal there
  is cured blind and the run restarts in a fresh custody root (scout report
  `report/2026-10-22-blind-dry-run-scout:.codex-report/BLIND-DRY-RUN-SCOUT.md` §3). So it is already a safe
  full-size end-to-end test, on the actual data. A full-size synthetic run before it rehearses a rehearsal.
- The full-size synthetic module takes about 6 h per run on a 5-vCPU cloud VM (J6, two runs, about 13 h), so every
  fix round costs most of a day. L9 has not reached merge, and block 5 has waited, collected, since 2026-10-12.
- The real release already refuses when its outputs differ from the dry run's (`release_digest_differs_from_dry_run`),
  so the full-size double run of the release-equality test duplicates a check the release itself makes.

## The rule

1. **L9 merges** after: its changed code's tests and the J1-J6 / C5-C9 predicates pass on **reduced-size synthetic
   fixtures** that still drive every registered step (0 to 11, including 3b, 9b and the registered p42 exits) through
   the real programs; the six short modules pass (`tests.test_authentication_io`, `tests.test_docs_freshness`,
   `tests.b5_analysis.test_sensitivity_guard`, `tests.b5_analysis.test_mint_kept_units`,
   `tests.b5_analysis.test_s10_chain_defects`, `tests.test_r4_acceptance_oracle`); one independent executing review
   finds no blocker (or its blockers are fixed); CI is green. No assertion is weakened to get there; a reduced fixture
   changes sizes, not checks.
2. **The full-size end-to-end test is the real block-5 blind dry run on the Mac**, scheduled as directive #587 says.
3. **The cold Fable and Opus passes** on L9 move from "at merge" to "before the release event". They may run in
   parallel with the dry run. The release still needs them.
4. **Release equality** is tested on a reduced fixture; the real release's digest comparison is the full-size check.
5. **Full-size synthetic runs** of `test_dry_run`, `test_release_equality` and `test_chain_fixture` become optional
   diagnostics, not merge gates.
6. **Step 9b's calibration refit goes to a ruling before the real dry run.** The analysis replay refits the pulse
   calibration under the frozen 120 s host-safety wall deadline, whose firing the code marks non-reproducible; it
   fired in the full-size synthetic runs (JouleWise-data `codex/l9-joined`, report "Final diagnosis"). Options for
   the ruling: (a) the analysis replay keeps the refit and the cell budget but does not inherit the wall deadline;
   (b) the replay checks the harvest-recorded fit by hash binding and leaves arithmetic verification to the
   independent recompute; (c) keep it as is, with the reason it cannot make the release irreproducible.
   **Decided by Ed, 2026-10-27: (c)** ("yes, sure, record c as my ruling"). Reason: (a), and also the per-member
   refit cache seat L9-2 proposed, would edit `joulewise/powermetrics_fiducial.py` or `joulewise/reduce.py`. Those
   are governed estimator-source pins (`ESTIMATOR_CODE_PATHS`, `joulewise/calibration_bracketing.py`), and the last
   change to the first one forced a calibration-acceptance reissue (`_r2`). So for block 5's first dry run:
   - The wall deadline stays. The dry run runs on the quiet Mac, where the same calibration completed at harvest.
   - A deadline firing is treated as a tooling refusal: cured blind, rerun in a fresh custody root (scout report §3).
   - **Condition:** seat L9-2 confirms, with executed evidence, that a firing anywhere on the dry-run path stops
     with a refusal and cannot change a kept unit, a lost-reference list or a printed number. If it cannot confirm
     that, this choice returns to Ed before the dry run.
   - (a) and the refit cache follow later as one governed change with its reissue, unless the cache can live
     entirely in non-governed code with byte-identical outputs (then it is an ordinary L9 change).
6a. **The Mac goes to analysis first (Ed, 2026-10-27):** "bytes and that work can pause until this is done if you
   need the quiet mac for analysis". The block-5 blind dry run takes precedence over BYTES sessions, s1-p1 included.
   BYTES's registered end (no t0 after 2026-11-02 00:00 PDT) still binds. If the dry run would push s1-p1 past it,
   the lead tells Ed before holding the loop, so he can choose between the fit set and the date, or amend the end
   date prospectively while BYTES is still blinded.
7. **Block 6** follows the same principle wherever its registration allows. Where the block-6 registration itself
   requires a synthetic stage chain before its blind run, that requirement stands until amended by a dated entry
   under its §17 rules.

## Executed evidence

The wall deadline named in item 6 is the frozen constant at `joulewise/powermetrics_fiducial.py:94`, beside the
reproducible cell budget at `joulewise/powermetrics_fiducial.py:90`. Checked on main at f164bef49:

```
$ grep -n "DETECTION_PROJECTION_CELL_BUDGET = \|DETECTION_PROJECTION_WALL_BUDGET_S = " joulewise/powermetrics_fiducial.py
90:DETECTION_PROJECTION_CELL_BUDGET = 1_710_000
94:DETECTION_PROJECTION_WALL_BUDGET_S = 120.0
exit 0
```

The 6 h and 13 h module times are from lane `lane/2026-10-20-l9-ruling-build`, `.codex-report/L9-1.md`, RESULTS
TABLE (`tests.b5_analysis.test_dry_run` 22,170.927 s; `tests.b5_analysis.test_release_equality` 47,231.364 s), and
JouleWise-data `codex/l9-joined` (`dry-run-trace-6` 20,950.368 s; `calibration-leaf-1`, the same reference in
isolation, 24.36 s).
