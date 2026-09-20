# Record 90b — full sharded replay at the plan-path head `9f452559` (production code identical to the final head `cf17e865`), 2026-09-19 19:30–20:19 PDT

Branch worktree `JouleWise-wt-planpath-d0b83820` fast-forwarded to `9f452559` and untouched during the run. `scripts/shard_tests.py --workers 4 --split`. Log: `90b-full-replay-planpath-9f452559.log.gz`.

| shard | modules | tests | failures | errors | skipped | result |
|---|---|---|---|---|---|---|
| 1 | 60 | 1440 | 0 | 0 | 13 | PASS |
| 2 | 61 | 1494 | 0 | 1 | 2 | FAIL |
| 3 | 62 | 1896 | 0 | 0 | 81 | PASS |
| 4 | 62 | 1757 | 0 | 0 | 7 | PASS |

Total 6,587 tests / 245 module runs (244 PASS). The one error is once more `tests.test_arm_readiness_evidence_t0.test_g4_real_ruled_census_pgrep_dialect` (fresh-eyes seat 92 was alive for the run's first half; the TEST-PGREP-DIALECT-MULTILINE-01 class). The module is re-run alone at the final head `cf17e865` with no seat alive (`90b-census-module-alone.log`, addendum below). The two modules edited after this head are covered by record 90c (73 OK at `cf17e865`).

**Addendum 20:25 PDT:** `tests.test_arm_readiness_evidence_t0` alone at `cf17e865` with no seat alive: **76 tests OK in 362 s** (`90b-census-module-alone-cf17e865.log`).
