SESSION_MODE: delegated
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0
WRITE_SCOPE: ["joulewise/b5_analysis/kept_units.py", "tests/b5_analysis/test_kept_units.py", "tests/b5_analysis/fixtures_s1.py", ".scratch-s1/**"]

For the report envelope: genre implementation; keep the JSON header under 4,000 bytes and put all evidence in the markdown body. End your turn only after the work is complete and the report is written. Start no background task and no other agent. Commit nothing. **You have 45 minutes of wall time; write the report by minute 40.** The module's tests take about four minutes: run the full module twice at most, single tests otherwise.

# Fix round for stage S1 of lane L9 (kept units): seven dispositioned review findings

You work in `/Users/edr/code/JouleWise-wt-l9-s1` (branch `lane/2026-10-12-l9-s1`, head `3653be6dc`, clean).
An independent reviewer executed probes against `joulewise/b5_analysis/kept_units.py`. Read
`/Users/edr/code/JouleWise-wt-b5-records/docs/process_traces/2026-10-block5/l9-rulings/REVIEW-s1.md` (the
dispositions bind you) and the reviewer's probes `p1` to `p9` under
`/Users/edr/night-archive/b5-consults/l9-rulings/s1/review-scratch/` (each is the counterfactual input for one
finding). The original brief `BRIEF-sol-s1.md` beside the review still binds you, its blinding paragraph and
constraints included.

Build every row marked "Fix", with the refusal code the row names. For each: a test built from the reviewer's
counterfactual input, at the call site `load_kept_units` (or the tripwire for its row), and a mutation run
showing the test fails without the guard. For row 3 the tests must kill both of the reviewer's surviving
mutants (drop the p42-name clause; drop the not-target clause). Do not weaken any existing check and do not
edit any file outside WRITE_SCOPE.

Report: one line per row (guard location, test name, mutation output), and the final full-module result.
