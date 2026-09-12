# Record 42 — integration replay 2 (ledger row 9 evidence, provisional)

Tree `/Users/edr/code/JouleWise-wt-integ-f0d28baa` @ 6c5c602c = origin/main ace4cc3c + A177 8a5d1169 + gitfix 87039749 + A184 43c1ce95 (A177 has since moved to 0ff8ac04 and is under consult; a final replay 3 will run on the final tree).
Command: `PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python3 scripts/shard_tests.py --workers 4 --split` (04:57:40 → 05:42 PDT; `REPLAY_RC=1`).

Exact shard tail:
SHARD SUMMARY index=1/4 modules=52 tests=1035 failures=4 errors=0 skipped=7 result=FAIL
SHARD SUMMARY index=2/4 modules=61 tests=1310 failures=0 errors=0 skipped=75 result=PASS
SHARD SUMMARY index=3/4 modules=59 tests=1952 failures=0 errors=0 skipped=18 result=PASS
SHARD SUMMARY index=4/4 modules=61 tests=1748 failures=3 errors=0 skipped=3 result=FAIL
REPLAY_RC=1

Failures (7, all arm-readiness dry-run/lifecycle/evidence_t0 REFUSE with `reason_codes: ['readiness_record_expired']`; one via the real arm generator rc 2): listed in brief 40. NONE of the three PRs touches these modules or `joulewise/arm_readiness.py` (`git diff --stat origin/main..HEAD` = the three lanes' files only). Bench reproduction on PRISTINE main code (bookkeeping worktree, code identical to ace4cc3c): each fails identically in ~1.7 s; five run together → `Ran 5 tests in 13.122s FAILED (failures=5)`. Yesterday's replay 25 on main 97da620e was clean on this machine; CI on main ace4cc3c is green today. Classification pending root-cause seat 41 (brief 40), including whether the production arm-time path shares the code (night relevance).
Shards 2 and 3 (3262 tests) PASS; shards 1 and 4 fail only on the seven above (verified by the FAIL: census: no other test names).
