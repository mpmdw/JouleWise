Committed locally as `9fdec5aed`; tree clean, no push.

Fixed R2-F1–R2-F3 in [input validation](/Volumes/JW-EXT/jw-wt/sol-p1-seat7-r3/joulewise/b6_analysis_inputs.py) and [production tests](/Volumes/JW-EXT/jw-wt/sol-p1-seat7-r3/tests/independent_recompute/test_b6_production.py).

- All five targeted unittest modules pass: 104 tests under inherited TMPDIR and `/private/tmp`. Production also passes under `/tmp`; compileall passes.
- All 13 required mutants are killed, including N8 and N12. Deleting the new path guard also fails its test.
- Synthetic `--workers 1` and `--workers 2` runs exit 0 with byte-identical outputs. SHA-256 remains `7eae099a05a38aa850ac980f3e5658e7805932f3b5f30db72068eb2b641bf590`.

Exact commands, results and receipts are in the [run report](/Volumes/JW-EXT/jw-wt/sol-p1-seat7-r3/docs/run_reports/2026-11-11-p1-seat7-r3.md).

Remaining verification: repeat the five modules under native macOS `/var/folders` TMPDIR outside this sandbox, which substitutes its own temp directory. R12 remains lead-owned.