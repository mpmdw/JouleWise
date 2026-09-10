# Magistrate terminal review — T0 clock refusal coverage (PR #312), merge candidate 6e0bbf67 (tests commit + merge of main afaeffef)

Reviewer: headless magistrate, activation 2145630c (Fable), full session context, not delegated. Diff read at the bench in
`/Users/edr/code/JouleWise-wt-t0-refusals` (`git diff afaeffef..6e0bbf67 -- tests/test_arm_readiness_evidence_t0.py`: 37 added lines,
three methods; production diff empty).

## Provenance

Coverage follow-up recorded on PR #311: root-cause consult 99 §Regression proposals. Astra seat 108 added the three methods unchanged and
mutation-checked each detail string; lead bench: `tests.test_arm_readiness_evidence_t0` 71 tests OK (476.9 s) and the three alone OK.

## Design-level questions (row 7)

1. **Do the tests pin real production guards?** Each method drives `_assert_clock_refusal` with an input that trips a distinct guard in
   `joulewise/arm_readiness_evidence_t0.py`: the `_capture` field validation (insufficient positive history → 'invalid or stale'), the RAW
   anchor span check ('T-0 RAW anchor span is below 600000000000 ns'), and the live-artifact age check ('not a live T-0 artifact'). The
   refuters (110 execution, 111 contract) verify the strings are the ones production raises and that the helper asserts the refusal rather
   than swallowing it.
2. **Do they encode the right invariant?** Consult 99 warned that a RAW anchor ahead of ordinary `now` alone must not refuse; both "ahead"
   tests compare within their own clock families (RAW vs RAW; ordinary capture finish vs ordinary now) — refuter 111 checks this.
3. **Portability.** No host clock is read: SYNTHETIC_MONOTONIC_NS and a literal 5×10^11 only; the tests hold on a small-uptime runner and
   on this Mac (today's class of Mac-calibrated assumptions is not present).
4. **Cost of being wrong.** Low: tests only, no production or fixture change, no threshold, no mock; the loop's shape for this PR is one
   execution refuter, one contract refuter, deltas for any fix round, the replay and this review.

## Overbuild / merge-ability prune (row 8)

Nothing to prune: three tests, each one guard.

## Replay (row 9)

Command (unpiped, rc captured): `PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=/Users/edr/code/JouleWise JOULEWISE_BACKUP_ROOTS= python3 scripts/shard_tests.py --workers 4` in
`/Users/edr/code/JouleWise-wt-t0-refusals` at 6e0bbf67 (contains origin/main afaeffef; main has since moved by docs-only trace commits), started
17:22:46 PDT, alone in-process (four shards concurrent; no seat, reviewer or other test process launched by this session; timer probe 3.28×
at start). Verbatim (113-replay-312-6e0bbf67-tail.txt):

```
WORKERS SUMMARY shards=4 modules=221 tests=5653 failures=0 errors=0 skipped=108 failed_shards=none result=PASS
rc=0
```

## Verdict

CLEAN for merge at 6e0bbf67: refuters 110 (Astra execution; static + guard-identity reasoning, execution blocked by its sandbox) and 111
(Opus contract; 0 blockers, 3 documentation nits, guard identity proven by a line-number spy: :556 / :1163 / :562); no fix round; full-suite
replay alone rc 0 with zero failures; CI to be confirmed green on 6e0bbf67 before the merge. Recorded (111): this PR does not satisfy the
kernel's 'four-worker replays under controlled concurrent agent load' clause for ARM-INTEGRATION-LOAD-01 and is not to be recorded against it.
