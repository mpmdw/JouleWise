SESSION_MODE: delegated
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0
WRITE_SCOPE: ["joulewise/b5_analysis/windows.py", "joulewise/b5_analysis/archive.py", "joulewise/b5_analysis/steps.py", "tests/b5_analysis/fixtures.py", "tests/b5_analysis/test_windows.py", "tests/b5_analysis/test_attempt_record.py", "tests/b5_analysis/test_archive.py", "tests/fixtures/b5_analysis/**", ".scratch-s0fix/**"]

For the report envelope: genre implementation; keep the JSON header under 4,000 bytes and put all evidence in the markdown body. End your turn only after the work is complete and the report is written. Start no background task and no other agent. Commit nothing. **You have 60 minutes of wall time; write the report by minute 50 whatever is unfinished.** Do NOT run `tests.b5_analysis.test_fixture_shapes`, `test_kept_units` or the harvest-lane modules (the lead runs them); the four fast modules (`test_windows`, `test_attempt_record`, `test_archive`, `test_frozen_files`) run in seconds. Do not rebuild committed fixtures unless a row cannot be tested otherwise; prefer in-memory edits of a loaded fixture.

# Fix round for stage S0 of lane L9 (window index, attempt reader, archive handle): dispositioned review findings

You work in `/Users/edr/code/JouleWise-wt-l9` (branch `lane/2026-10-07-l9-analysis`, clean tree). An
independent reviewer executed probes and mutations against `joulewise/b5_analysis/{windows,archive,steps}.py`.
Read `/Users/edr/code/JouleWise-wt-b5-records/docs/process_traces/2026-10-block5/l9-rulings/REVIEW-s0.md`
(the dispositions bind you) and the reviewer's probes `p1` to `p7*` and `mutate.py` under
`/Users/edr/night-archive/b5-consults/l9-rulings/s0/review-scratch/` (each is the counterfactual input for a
finding). The first brief `BRIEF-sol-s0.md` beside the review still binds you, its blinding paragraph and
constraints included.

Build every row marked "Fix", with the refusal code the row names. For each: a test built from the reviewer's
counterfactual input at the function concerned, and a mutation run showing the test fails without the guard.
Row N2's five surviving mutants must all be killed by the final tests. Notes for particular rows:

- **S1**: find each pack's sealed pack id in its pack directory under `configs/campaigns/` (read how the
  frozen harvest derives `pack_id`; do not guess the path), and take the table from there at load time, not
  as typed literals. The synthetic fixtures use synthetic plan and pack ids: keep them loadable through an
  explicit, test-only argument (for example a `pack_table` parameter the tests pass), never by a silent
  bypass in production code.
- **S2**: `no_archive` entries count as attempts. The first seal is checked the same way.
- **N3**: stage S1 (`joulewise/b5_analysis/kept_units.py`, not in your scope) and its tests call
  `open_archive`; read how, and keep that call working, or say exactly what one-line change S1 needs.
- Do not weaken any existing check; edit nothing outside WRITE_SCOPE; if a fix needs a file outside it,
  finish the rest and return the scope request.

Report: one line per row (guard location, test name, mutation output), and the final result of the four fast
modules.
