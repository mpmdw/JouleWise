SESSION_MODE: delegated
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0
WRITE_SCOPE: ["joulewise/b5_analysis/bracket.py", "tests/b5_analysis/test_bracket.py", "tests/b5_analysis/fixtures_s2.py", ".scratch-s2/**"]

For the report envelope: genre implementation; keep the JSON header under 4,000 bytes and put all evidence in the markdown body. End your turn only after the work is complete and the report is written. Start no background task and no other agent. Commit nothing. **You have 70 minutes of wall time; write the report by minute 60 whatever is unfinished.** The module's tests take about seven minutes: run the full module twice at most, single tests otherwise.

# Fix round for stage S2 of lane L9 (the window bracket): dispositioned review findings

You work in `/Users/edr/code/JouleWise-wt-l9-s2` (branch `lane/2026-10-12-l9-s2`, head `dbecf331d`, clean).
An independent reviewer executed probes and mutations against `joulewise/b5_analysis/bracket.py`. Read
`/Users/edr/code/JouleWise-wt-b5-records/docs/process_traces/2026-10-block5/l9-rulings/REVIEW-s2.md` (the
dispositions bind you) and the reviewer's probes and mutants under
`/Users/edr/night-archive/b5-consults/l9-rulings/s2/review-scratch/` (each is the counterfactual input for a
finding; `run_mut.py` and `run_mut_window.py` name the surviving mutants). The original brief
`BRIEF-sol-s2.md` beside the review still binds you, its blinding paragraph and constraints included.

Build every row marked "Fix", with the refusal code the row names. For each: a test built from the reviewer's
counterfactual input at the function the row names, and a mutation run showing the test fails without the
guard. Row S3's three surviving mutants and the reviewer's `drop_b_fiducial_from_compared` must all be killed
by the final tests. Rows S4 and N1 ask for a choice among named routes: take the first route that the pinned
programs' real outputs support at both pins (`224a264c5` and `b039c0257`; read the frozen harvest, do not
guess), build it, and say in the report which route and the evidence. If no route exists for a row, do not
approximate: say exactly what blocks it. Do not weaken any existing check; edit nothing outside WRITE_SCOPE.

Report: one line per row (guard location, test name, mutation output), the route taken for S4 and N1, and the
final full-module result.
