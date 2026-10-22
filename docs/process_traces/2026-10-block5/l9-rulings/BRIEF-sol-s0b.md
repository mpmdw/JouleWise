SESSION_MODE: delegated
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0
WRITE_SCOPE: ["joulewise/b5_analysis/__init__.py", "joulewise/b5_analysis/windows.py", "joulewise/b5_analysis/archive.py", "joulewise/b5_analysis/steps.py", "configs/analysis/b5/seal_pins.json", "tests/b5_analysis/__init__.py", "tests/b5_analysis/fixtures.py", "tests/b5_analysis/test_frozen_files.py", "tests/b5_analysis/test_windows.py", "tests/b5_analysis/test_attempt_record.py", "tests/b5_analysis/test_archive.py", "tests/b5_analysis/test_fixture_shapes.py", "tests/fixtures/b5_analysis/**", ".scratch-s0/**"]

For the report envelope: genre implementation; keep the JSON header under 4,000 bytes and put all evidence in the markdown body. End your turn only after the work is complete and the report is written; do not end mid-flight. Start no background task and no other agent. Commit nothing; leave your changes uncommitted in the working tree. **You have 70 minutes of wall time. Write the report by minute 60 whatever is unfinished, and list what is unfinished.** Do not re-run the six harvest-lane test modules (the lead runs them); a full `tests.b5_analysis.test_fixture_shapes` run takes many minutes, so run it once at most and single tests otherwise.

# Close stage S0 of lane L9: two requirements that arrived after the first brief, and the report the first seat did not write

You work in `/Users/edr/code/JouleWise-wt-l9`, branch `lane/2026-10-07-l9-analysis`. An earlier seat built
stage S0 from the brief `/Users/edr/code/JouleWise-wt-b5-records/docs/process_traces/2026-10-block5/l9-rulings/BRIEF-sol-s0.md`
(read it first: its constraints, its blinding paragraph and its report section all bind you) and was stopped
by a time limit before it wrote a report. The lead committed its work as it stood; the lead's own run of
`tests.b5_analysis.test_frozen_files`, `test_windows`, `test_attempt_record` and `test_archive` passed
(3, 9, 20 and 12 tests). **The lead's run of `tests.b5_analysis.test_fixture_shapes` (about 20 minutes) ended `FAILED (failures=1)`; the lead did not capture which test. Find it first (run the module's tests one at a time), and fix the cause or report why the test is wrong.** The design is `/Users/edr/night-archive/gate-prune/wave-1007b/l9/L9_DESIGN.md`
(sections 0, 3.1 to 3.3, 3.6, 3.7, 4.0, and "S0" in section 5). Two cold rulings and a decisions record now
exist beside the brief: `RULING.md`, `ERRATUM-RULING.md`, `DECISIONS.md`. Where they differ from the design
they win.

## A. Two changes

1. **A harvest checkout that was not clean** (`RULING.md`, section Z item 1; it overrides the design's T6 for
   analysed windows). Today `archive.py` records `harvest_checkout_status_not_clean` as a flag for every
   attempt. Required: on the archive of an **analysed** window (the path through `open_archive` /
   `AnalysedWindow`), `harvest_checkout.status_clean` not exactly `true`, or `status_lines` not 0, or `errors`
   non-empty, is the tooling refusal `harvest_checkout_not_clean`. On an attempt that is only part of the
   history (the path through `open_attempt_record` for a not-analysed attempt) the flag stays a flag and the
   record is accepted. Tests: an analysed window with `status_clean` false refuses; with `status_lines` 1
   refuses; with one entry in `errors` refuses; the same three on a not-analysed attempt are accepted with
   the flag. Counterfactual shown by mutation: the reader as it stands today (flag only) fails the first test.
   Check the real field names and types in `joulewise/b5/harvest.py` (the pinned program, in-tree) before you
   write the tests.
2. **Distinct timing bounds in every synthetic window** (`DECISIONS.md` section 3, item B1). A window has two
   calibration captures, one before and one after its chain; each has an alignment bound; the window's
   operative bound is derived from the pair by the bracket evaluation. In the fixtures as built, check what
   the pre-capture and post-capture bounds are. Required: in every window `fixtures.build_window` yields, the
   post-capture bound differs from the pre-capture bound by a fixed marker (choose one and name it as a
   constant in `fixtures.py`), and the three standard windows (`ALPHA_STD`, `BETA_STD`, `GAMMA_STD`) have
   three different operative bounds. `test_fixture_shapes` asserts both facts. If the committed `pin2`
   fixtures must be rebuilt for this, rebuild them by the recorded command and update `PROVENANCE.md`. If the
   mock adapter or the harness cannot express a per-capture bound, do not force it: report exactly what
   prevents it and what the smallest change outside your scope would be.

## B. The report the first seat owed (verify, do not trust)

For each item of the design's S0 list ("Tests and refusal paths"): the test that covers it, by name, or
"MISSING". Add the missing ones. For each counterfactual the design names (for example: a reader that refuses
an attempt because it is not claim-usable; a one-byte edit of `joulewise/b5/harvest.py`), show by a mutation
run, with its output, that the test fails without the guard. Then:

- **Design divergences**: everywhere the code you find differs from the design's sections 3.2, 3.3 and 3.6,
  with file and line and the reason, if the code shows one.
- **O16**: read `tests/hazards/refusal_census.py`; report which files and directories it scans, whether
  `joulewise/b5_analysis/` falls under it, and exactly which entries, if any,
  `configs/gates/hazard_refusals.json` would need for the refusal codes of S0 (do not edit that file).
- **Fixtures**: for each directory under `tests/fixtures/b5_analysis/`, the commit that wrote it and the
  command (from its `PROVENANCE.md`), and its size. Say what is in `.scratch-s0/` and what may be deleted.
- **Not done**: anything of the design's S0 list that is not built.
