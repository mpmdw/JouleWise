# Cold review: `w1-prepare-holds` round 3 (PH-1) @ `785d94436`

Opus 5.5, interim lane lead, 2026-11-11, on the Air. Reviewed cold: the diff `bb64d1e70..785d94436`
(`scripts/align_v4_session.py` +2/-3, `tests/align/test_v4_arm_watchdog_check.py`) against RL-65, RL-71 and RL-79.

**Verdict: ADMIT.**

**Merge state found at intake.** The seat committed on the side branch `ops/2026-11-11-w1-prepare-holds-r3`;
the launcher put only the Sol report commit (`ca22f1e68`) on `ops/2026-11-11-w1-armcheck`. PH-1 was therefore
NOT on the batch branch at `ca22f1e68`. It is merged by the lane lead with this review.

## The change

`held_window_check` skipped every record whose window is `R1` or `W1` or whose role is `development`. The skip is
now `window.window == 'R1'` only. W1 is a v4 window with a desk and a final harvest, so RL-65's rule ("a v4
window whose final harvest carries one of those reasons is held") applies to it; R1 is a rehearsal without a v4
desk harvest. A W1 or other development record now goes through the same branches as any other: deferred if not
final; `no final harvest: no capture` if final without harvest sources; otherwise its authenticated final
`exclusions` reasons are read. The function is otherwise unchanged. The one changed old test
(`test_r1_and_development_are_skipped...` -> `test_r1_is_skipped...`) changes only because the behaviour it
pinned is the one PH-1 removes; its chain-digest assertions are kept.

## Tests (Air, `python3.13 -B -m unittest`)

- `tests.align.test_v4_arm_watchdog_check -k HeldWindow`: 16 tests OK (98.8 s).
- Full `tests.align.test_v4_arm_watchdog_check`: in the 67-module comparison recorded in `docs/run_reports/2026-11-11-w1-batch-tests-opus-coldreview.md`.

## Mutation checks (W1/development/R1 tests plus the unchanged round-2 test, 6 tests)

| Mutant on the skip condition | Result |
|---|---|
| Restore the old skip (`R1`, `W1`, `development`) | killed (5 failures) |
| Skip nothing (R1 checked too) | killed (1 failure: R1's `precheck.certain_exclusion` refuses) |
| Skip `R1` and `W1` | killed (4 failures) |
| Skip `R1` and `development` | killed (5 failures) |

## Notes

- The weight-digest round and prepare-holds rounds 1 and 2 have no committed review file on this branch; the
  Fable lane lead's PH-1 finding implies a review of round 2. Their behaviour is exercised by the full module
  and by the 67-module comparison recorded in the batch review.
