SESSION_MODE: delegated
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0
WRITE_SCOPE: ["joulewise/b5_analysis/context.py", "joulewise/b5_analysis/sources_replay.py", "joulewise/b5_analysis/archive.py", "joulewise/whole_window.py", "configs/gates/hazard_refusals.json", "tests/b5_analysis/test_tripwires.py", "tests/b5_analysis/test_sources_replay.py", "tests/b5_analysis/test_context.py", "tests/b5_analysis/test_validator_context.py", "tests/b5_analysis/test_archive.py", "tests/b5_analysis/fixtures_s3b.py", "tests/b5_analysis/fixtures_s3.py", ".scratch-s3bfix3/**"]

For the report envelope: genre implementation; keep the JSON header under 4,000 bytes and put all evidence in the markdown body. End your turn only after the work is complete and the report is written. Start no background task and no other agent. Commit nothing. **You have 90 minutes of wall time; write the report by minute 80 whatever is unfinished.** Keep scratch small and delete temporary directories you create (the disk filled once today).

# Fix round for stage S3 part B of lane L9: dispositioned review findings

You work in `/Users/edr/code/JouleWise-wt-l9-s3` (branch `lane/2026-10-12-l9-s3`, head `89998b867`, clean; the
whole suite passes on this head). An independent reviewer executed probes and mutations against
`joulewise/b5_analysis/context.py` and `sources_replay.py`. Read
`/Users/edr/code/JouleWise-wt-b5-records/docs/process_traces/2026-10-block5/l9-rulings/REVIEW-s3b.md` (the
dispositions bind you; each "Fix" row states the rule). The reviewer's scratch is gone; its inputs are
described in the rows and, where a row says "the reviewer's mutants", the mutation is the removal of the
guard the row names. The three rulings and `DECISIONS.md` beside the review, and the earlier briefs
(`BRIEF-sol-s3b.md`, `BRIEF-sol-s3a.md`), still bind you, blinding paragraph and frozen files included.

Build every row marked "Fix", with the refusal code the row names. For each: a test at the function
concerned and a mutation run showing the test fails without the guard. Notes:

- **S2** is one site in `joulewise/whole_window.py` (the validator, beside the place where it re-derives and
  checks the survivor set against the context). It is the only edit you make in that file. It adds a refusal
  site: add its entry to `configs/gates/hazard_refusals.json` if `python -m tests.hazards.refusal_census`
  reports one (same classification as the file's other context-consumer sites). Without a context nothing
  changes (rerun the no-context differential tests of `tests/b5_analysis/test_validator_context.py`).
- **S1**: after removing the separate window argument of `build_context`, update its callers in the tests
  (and only the tests; no production caller exists yet).
- **S4**: the tests keep working through an explicit, named test-only argument; production defaults refuse.
- Do not weaken any existing check. Synthetic windows come from the committed archives through
  `tests/b5_analysis/fixtures.py` (they load into a private temporary directory per process).

At the end run `tests.b5_analysis.test_context`, `test_tripwires`, `test_sources_replay`,
`test_validator_context`, `test_archive` and `tests.hazards.test_refusal_allowlist`. Report: one line per
row (guard location, test name, mutation output), and the six results.
