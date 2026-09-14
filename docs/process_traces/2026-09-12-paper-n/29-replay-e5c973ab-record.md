# Record 29 — full-suite replay on the merge candidate (ledger row 9 evidence, FINAL)

Tree `/Users/edr/code/JouleWise-wt-paper-n` @ e5c973ab = origin/main c53d4227 merged (0e071fa7) + the Paper-N branch (code-final 0fa5fa60, record 28 cures 50a2d72a, replay cures e5c973ab). Command (lead, unpiped to `/private/tmp/claude-501/-Users-edr-code-JouleWise/5add607a-5532-41b4-8bc1-451a6a7aa48c/scratchpad/replay-e5c973ab.log`, venv Python 3.13.1): `PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python3 scripts/shard_tests.py --workers 4 --split`, launched 15:24 PDT, finished 16:02 PDT.

Exact tail:
```text
SHARD SUMMARY index=1/4 modules=52 tests=1037 failures=0 errors=0 skipped=7 result=PASS
SHARD SUMMARY index=2/4 modules=61 tests=1311 failures=0 errors=0 skipped=75 result=PASS
SHARD SUMMARY index=3/4 modules=59 tests=1952 failures=0 errors=0 skipped=18 result=PASS
SHARD SUMMARY index=4/4 modules=61 tests=1748 failures=0 errors=0 skipped=3 result=PASS
WORKERS SUMMARY shards=4 modules=233 tests=6048 failures=0 errors=0 skipped=103 failed_shards=none result=PASS
REPLAY_RC=0
```

`FAIL:`/`ERROR:` census over the log: 0. Predecessor replay on be87d551 (log `/private/tmp/claude-501/-Users-edr-code-JouleWise/5add607a-5532-41b4-8bc1-451a6a7aa48c/scratchpad/replay-be87d551.log`, 14:40–15:20 PDT) had 6048 tests / 1 failure / 2 errors, all in two pin modules the lead's bench edits had disturbed: `tests.test_docs_freshness` (README blurb carried the literal "PR #331") and `tests.test_d165_rationale_census` (allowlist line 1524 → 1525 after round 3 inserted one line); both cured at e5c973ab (41 tests OK) and confirmed by this clean replay.
