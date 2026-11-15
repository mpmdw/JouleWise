# Cold review: `ops/2026-11-11-w1-batch-tests` @ `231d5ccfd` (+ lead fix `510ac023a`)

Opus 5.5, interim lane lead, 2026-11-11, on the Air. Reviewed cold: the diff `bb64d1e70..84dc6f5f9` (seven test
files, one shared helper) against the brief and RL-53's rules.

**Verdict: ADMIT, with one repair added by the lead.**

## What "harvest remains unrepaired" meant

The seat ran out of its test budget before reaching `tests.align.test_harvest_off_review_sol2` (its full module
timed out at 300 s) and did not run `tests.align.test_v4_next_arm_packet`. Nothing in the harvest code is broken.
Both modules have one arm witness that drives `_arm_and_install` with a session state that has no `plan_path`,
which the batch's mandatory watchdog acceptance reads:

- `test_harvest_off_review_sol2.EligibilityTests.test_older_test_window_cannot_be_silently_labelled_final`
- `test_v4_next_arm_packet.ArmOrderWitness.test_every_subprocess_write_and_disk_usage_precedes_the_dwell_stamp`

Both were red on the batch with `KeyError: 'plan_path'` (reproduced on the Air) and pass after `510ac023a`
gives them the same `session_plan` helper (2 tests, 100 s). No assertion changed; in ArmOrderWitness the plan is
written before event recording starts, so the order assertions are unaffected.

## The seat's diff

- No production file, bound file or PREQUAL harness changed; no seam parameter added. Checked.
- `session_plan` writes a synthetic plan (future `t0`) inside the caller's temporary fixture, so the real
  watchdog acceptance runs on it; `held_window_acceptance` is an explicit stand-in used only where the packet and
  Git evidence are synthetic, by scoped `patch.object`. This is the brief's allowed form.
- Assertions: unchanged in every file I read (the seat's AST comparison agrees).

## Tests

- The seat's four repaired modules: `test_r1_round6_power` 25 OK, `test_r1_round7_install` 6 OK,
  `test_r11_delta5_sol1` 8 OK, `test_r11_delta5_sol2` 13 OK (seat), confirmed by the earlier lead's base runs that
  they pass on the W1 line.
- The whole-suite comparison runs on CI for the combined PR (the Air was at load ~98; the orchestrator moved the
  bulk comparison to CI, with PR #724's CI as the W1-line base).
