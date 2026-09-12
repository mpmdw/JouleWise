# Record 58 — integration replay 4 (ledger row 9 evidence, FINAL)

Tree `/Users/edr/code/JouleWise-wt-integ-f0d28baa` @ 318b17f6 = origin/main ace4cc3c + #324 A177 6714ce96 + #326 gitfix 87039749 + #325 A184 43c1ce95 + #327 armfix 61872ccf (`git diff --stat origin/main..HEAD`: 11 files, +471/−54; merges clean, no conflicts).
Command (lead, unpiped to the log, venv Python 3.13.1): `PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python3 scripts/shard_tests.py --workers 4 --split` launched 06:48:59 PDT, finished before 07:33:55 PDT. Full log retained at `/tmp/magistrate-f0d28baa/replay-4-318b17f6.log`.

Exact tail:
SHARD SUMMARY index=1/4 modules=52 tests=1037 failures=0 errors=0 skipped=7 result=PASS
SHARD SUMMARY index=2/4 modules=61 tests=1310 failures=0 errors=0 skipped=75 result=PASS
SHARD SUMMARY index=3/4 modules=59 tests=1952 failures=0 errors=0 skipped=18 result=PASS
SHARD SUMMARY index=4/4 modules=61 tests=1748 failures=0 errors=0 skipped=3 result=PASS
REPLAY_RC=0

Totals: 1037 + 1310 + 1952 + 1748 = 6047 tests, failures 0, errors 0, skipped 103, `REPLAY_RC=0`. `FAIL:`/`ERROR:` census over the log: 0. The seven arm-readiness refusals of replay 2 (record 42) are gone with #327 in the tree. Replays 2 (6c5c602c) and 3 (b6d5de06) were abandoned as stale when heads moved and are not evidence. Two Astra refuters and no other suite were running on the host during the first minutes of this replay.
