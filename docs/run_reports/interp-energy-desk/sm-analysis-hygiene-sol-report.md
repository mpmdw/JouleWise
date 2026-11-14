Committed `a5b54a210` on `test/2026-11-11-sm-analysis-hygiene`. Working tree is clean; nothing pushed.

Changed five files: the new agreement tests, `release_b5.py`, CANONICAL, the timing map, and the [run report](/Volumes/JW-EXT/jw-wt/sol-sm-analysis-hygiene/docs/run_reports/2026-11-11-sm-analysis-hygiene.md). Release verdicts now record HEAD and its advisory relation to the pin.

Verification passed: seven targeted unittest modules, compileall, and `scripts/repin.py --check` across all 16 families. All 10 focused mutants were caught. Exact commands and skips are in the report.

Four-way equality remains unproven. The constant and r4 tag differ; Git proves ancestry and byte equality except for the two existing frozen-file exceptions. No committed release record was available.

Next: lead review of that identity distinction and permitted record-field evidence. Live fixture census also needs rerunning outside the sandbox because `ps` is denied.