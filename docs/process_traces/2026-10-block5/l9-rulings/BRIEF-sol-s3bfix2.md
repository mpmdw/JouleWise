SESSION_MODE: delegated
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0
WRITE_SCOPE: ["joulewise/b5_analysis/context.py", "joulewise/b5_analysis/sources_replay.py", "tests/b5_analysis/test_tripwires.py", "tests/b5_analysis/test_sources_replay.py", "tests/b5_analysis/test_context.py", "tests/b5_analysis/fixtures_s3b.py", ".scratch-s3b/**"]

For the report envelope: genre implementation; keep the JSON header under 4,000 bytes and put all evidence in the markdown body. End your turn only after the work is complete and the report is written. Start no background task and no other agent. Commit nothing. **You have 60 minutes of wall time; write the report by minute 50 whatever is unfinished.**

# Lane L9 stage S3 part B, third round: the lead's decision on the absent spare's loss record; finish the catalog path

You work in `/Users/edr/code/JouleWise-wt-l9-s3b` (branch `lane/2026-10-12-l9-s3b`, clean; your second round
is committed; your scratch and fixture cache are at `.scratch-s3b/`). Your second round stopped, correctly, on
a question. The lead has decided it: read the section "One point of the roster ruling decided by the lead"
in `/Users/edr/code/JouleWise-wt-b5-records/docs/process_traces/2026-10-block5/l9-rulings/DECISIONS.md`. In
short: the third "in none of" check of the roster ruling's item 6(d) admits an entry of
`rescreen.survivors.reference_losses` for a spare that left no bundle when, and only when, its reason there is
`bundle_absent` and the same id carries `bundle_absent` in `harvest_reference_losses`; any other reason
refuses `roster_rebuild_differs_from_archive`. The other two checks (evaluation basis; exclusions document)
are unchanged. Everything else in the three rulings and your earlier briefs still binds you.

Build exactly that, with tests: the pinned harvest's real shape (both lists `bundle_absent`) is accepted on
the unmodified catalog-path archive; each of these refuses: the evaluator entry with another reason; the
evaluator entry present and the harvest entry absent; the harvest entry with another reason; the spare
present in the basis; the spare present in the exclusions document. A mutation run for the new condition
(accept any reason) must fail a test. Then finish what the stop left unfinished: the catalog and spare
acceptance on the original archive, the downstream replay conformance, and the eight catalog-dependent
mutations that could not run. Run your three modules at the end.

Report: the guard location, each test, each mutation output, the final result of the three modules, and
anything still unfinished.
