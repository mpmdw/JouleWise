SESSION_MODE: delegated
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0
WRITE_SCOPE: ["joulewise/b5_analysis/context.py", "joulewise/b5_analysis/sources_replay.py", "joulewise/b5_analysis/windows.py", "joulewise/b5_analysis/archive.py", "tests/b5_analysis/test_tripwires.py", "tests/b5_analysis/test_sources_replay.py", "tests/b5_analysis/test_context.py", "tests/b5_analysis/test_windows.py", "tests/b5_analysis/fixtures_s3b.py", ".scratch-s3b/**"]

For the report envelope: genre implementation; keep the JSON header under 4,000 bytes and put all evidence in the markdown body. End your turn only after the work is complete and the report is written. Start no background task and no other agent. Commit nothing. **You have 90 minutes of wall time; write the report by minute 80 whatever is unfinished.**

# Lane L9 stage S3 part B, second round: the reference roster is rebuilt from the archived pack, as a cold ruling now prescribes

You work in `/Users/edr/code/JouleWise-wt-l9-s3b` (branch `lane/2026-10-12-l9-s3b`, cut from `7220ab119`,
clean; your earlier scratch, with its fixture cache, is restored at `.scratch-s3b/`). Part B's first round
stopped, correctly, on a question: the roster the pinned harvest archives carries no reference or spare slot.
A cold judge has ruled it: read
`/Users/edr/code/JouleWise-wt-b5-records/docs/process_traces/2026-10-block5/l9-rulings/ROSTER-RULING.md`
whole. **It is frozen: build its replacement text of erratum X1 items 6 and 7 item by item**, with its three
refusals (`roster_pack_not_archived`, `roster_plan_tree_not_sealed`, `roster_rebuild_differs_from_archive`)
exactly as spelled, the treatment of a spare that left no bundle, the rebuilt roster handed to the Erratum 2
sources replay, and the tooling fact it flags (the sizing record checked against its sealed digest in
`configs/analysis/b5/seal_pins.json`). The first brief (`BRIEF-sol-s3b.md`, beside the ruling) and the two
earlier rulings still bind you, the blinding paragraph and frozen-file constraints included.

Then:

1. Every test that used a contract-shaped copy (a roster with slot fields added by the fixture) now runs on
   the **unmodified** archive the real pinned harvest wrote; the enrichment helper is deleted. The witness
   your first brief asked for is now possible and required: S(W) on the standard window equals the ids the
   real pinned re-screen aggregated, on an unmodified archive.
2. The judge's own counterexample is a test: a plan tree with the two reference stages' slots swapped yields
   the identical archived projection and must be refused by the sealed-digest binding
   (`roster_plan_tree_not_sealed`), not by the equality check. Mutation: remove the digest binding; the test
   fails.
3. A test and mutation for each of the other two refusals, and for the spare that left no bundle (in the
   rebuilt roster; in neither S(W) nor X(W); its `bundle_absent` loss record admitted).
4. `windows.py` and `archive.py` are in scope only for what the ruling requires of them (the sealed pack
   table and sizing-record digest; reading the archived pack through the authenticated handle). Another seat
   is editing `joulewise/whole_window.py` and part A's tests in another worktree: do not touch them. If you
   need a seam in part A, report the exact change.

Run your three modules and `tests.b5_analysis.test_windows` at the end. Report: one row per item of the
ruling's replacement text (function and line, test, mutation output), what was deleted, and what is
unfinished.
