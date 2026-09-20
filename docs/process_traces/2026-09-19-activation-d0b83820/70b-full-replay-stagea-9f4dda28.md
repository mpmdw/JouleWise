# Record 70b — full sharded replay at the fix-round-4 head `9f4dda28`, 2026-09-19 16:37–17:15 PDT

Branch worktree `JouleWise-wt-stagea-d0b83820` fast-forwarded to `9f4dda28` and untouched during the run. `scripts/shard_tests.py --workers 4 --split`. Log: `70b-full-replay-stagea-9f4dda28.log.gz`.

| shard | modules | tests | failures | errors | skipped | result |
|---|---|---|---|---|---|---|
| 1 | 60 | 1438 | 0 | 0 | 13 | PASS |
| 2 | 61 | 1494 | 0 | 1 | 2 | FAIL |
| 3 | 62 | 1891 | 0 | 0 | 81 | PASS |
| 4 | 62 | 1757 | 0 | 0 | 7 | PASS |

Total 6,580 tests / 245 module runs (244 PASS); the one error is again `tests.test_arm_readiness_evidence_t0.test_g4_real_ruled_census_pgrep_dialect` — the real-process census matching a live delegated seat's multi-line argv (re-audit 81 and fresh-eyes 83 were alive; their briefs name `powermetrics`), the TEST-PGREP-DIALECT-MULTILINE-01 class (records 14/34/60/70). The 16 fix-round-4 boundary regressions and the 226-test driver module pass in the full suite. Record 70c repeats this at the final head `87c38078` and carries the lone module re-run once no seat is alive.
