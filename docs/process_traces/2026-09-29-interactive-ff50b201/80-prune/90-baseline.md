# Prune baseline (before), measured 2026-09-29 at main 32ff9013

- production lines (joulewise/ + scripts/ *.py): 214026
- test lines (tests/ *.py): 267034
- test modules: 267
- whole suite (local, shard_tests --workers 6, e9827f33 today): 7,560 tests, 109 skips; wall ≈55 min (launched ≈12:37, log written 13:32 PDT, with other seats running)
- hosted CI per main push: ≈462 runner-minutes, ≈61 min wall (test-stack prune report 30-tests-opus.md, estimate from run 36382310251)
- gate ledger: 12 rows full tier; docs PR #438 open→merge 26.7 h with 3 audit rounds (20-process-sonnet.md)
- process share 09-22..09-29: ≈82 % of commits (934/1,143), ≈87 % of changed lines were records/rulings/bookkeeping; 116 cold rulings in 8 days (21-process-opus.md)
- main 09-27 16:23 → 09-29 13:28: 197 commits, +42,194 lines, 41,691 under docs/process_traces, 16 lines of product/test code (20-process-sonnet.md)
- network-time enforcement: 4 fix rounds, ≥3 cold rulings, ≈2.5 days (N1 branch +2,666 lines) → replaced by thin OFF receipt (net −225 lines)
- windows: W1/W2 were the last; cadence planned around nights (now: back-to-back, Ed 09-29)
