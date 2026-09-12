# Seat brief — RECOVER-SESSION-REFUSAL-WINDOW-EXHAUSTED-01 (kernel lane A184)

WRITE_SCOPE: ["scripts/recover_calibration_ledger.py","joulewise/calibration_exits.py","tests/test_calibration_exits.py","docs/phase_2/derivation_night_runbook.md","docs/contracts/calibration_ledger_append.md","docs/contracts/powermetrics_fiducial.md"]

You are an implementation seat in the linked worktree you were started in (branch
`fix/2026-09-12-recover-window-exhausted`, from origin/main `ace4cc3c`). Do not
touch any path outside WRITE_SCOPE; if the correct change needs another path,
stop and return NEEDS_SCOPE naming it. Never run git commands that move HEAD,
never push, never touch `/Users/edr/code/JouleWise` or
`/Users/edr/JouleWise-measurement-20260913-derivation` (a measurement night is
armed there; both are fenced).

## Problem (seam audit record 113, N-4)

`scripts/recover_calibration_ledger.py` subcommand `session-refusal` maps an
aborted session's `abort_reason` through `_AUTOMATIC_ABORT_REFUSALS` (three
reasons: `display_arm_failed`, `powermetrics_never_ready`,
`pulse_calibration_rollover_gate_timeout`). The derivation night chain
(`scripts/night_chains/calibration_derivation_only.zsh` ~line 121) aborts its
session with `abort-session --reason window_exhausted` when the quiet window
cannot fit the next slot. Because `window_exhausted` is not in the map, a desk
operator running `session-refusal` on such a session gets
`calibration_session_not_open` (SESSION_NOT_OPEN) instead of the reason the
chain wrote. Runbook `docs/phase_2/derivation_night_runbook.md` §"The other
early end: window_exhausted" (~line 1659) describes the abort.

## Acceptance (kernel `docs/process/state_kernel.json` → this lane)

"session-refusal on a window_exhausted-aborted derivation session prints that
reason with a defect-shaped test and a killed cut; the runbook's harvest
section cites it."

## Work

1. Read first: `_AUTOMATIC_ABORT_REFUSALS` and the `session-refusal` branch in
   `scripts/recover_calibration_ledger.py`; `RefusalCode` and the three
   existing automatic-abort codes in `joulewise/calibration_exits.py`
   (definitions ~103–105, human strings ~264–266, and every family/tier set
   that lists them, ~285, ~331, ~367); the tests that exercise
   `session-refusal` in `tests/test_calibration_exits.py`; and whatever
   contract doc pins the refusal-code registry (the exit table in `docs/contracts/calibration_ledger_append.md` ~line 342 lists the three codes as rows with `witness.*` columns; `docs/contracts/powermetrics_fiducial.md` ~line 463 names one; mirror the row shape exactly and note whether any test parses that table
   if it exists — find the ONE home with grep before editing).
2. Add a refusal code for the window abort following EXACTLY the pattern of
   the three existing automatic-abort codes (same families/tiers, same human
   string style, e.g. `WINDOW_EXHAUSTED = "calibration_window_exhausted"`, string
   "quiet window exhausted before the next slot"), and map
   `"window_exhausted"` to it in `_AUTOMATIC_ABORT_REFUSALS`. If the
   registry's contract doc or a test asserts a frozen code count/list, update
   that ONE home in the same change and say so in the report. If you find that
   adding a code is fenced by a rule that requires a ruling (a doc says the
   registry is frozen, or a code-set digest is pinned by a night artifact),
   STOP and return NEEDS_RULING with the exact citation — do not work around it.
3. Defect-shaped regression in `tests/test_calibration_exits.py`: open a
   session the way the existing session-refusal tests do, abort it with
   `abort-session --reason window_exhausted`, then run `session-refusal` and
   assert the payload's code is the new code and `terminal_result` is
   `session_aborted`, with the process exit the existing automatic-abort cases
   use. Prove the test is defect-shaped: run it once with the map entry
   removed (it must FAIL with SESSION_NOT_OPEN), restore the bytes, run it
   again (PASS). Paste both runs' `Ran N` / result lines in the report.
4. Runbook: in the `window_exhausted` section cited above, add ONE sentence
   that `session-refusal` reports this reason as the new code (so the harvest
   operator knows what the desk tool prints). No other prose changes.
5. Run `python -m pytest tests/test_calibration_exits.py -q` (whole file) and
   `python scripts/gen_state.py --check` if either touched file is covered by
   it; `git diff --check`. Do NOT commit; leave the working tree dirty for the
   magistrate's review. Report `git status --short` and `git diff --stat`.

## Report (final message, claude-codex-report/v1 envelope per --genre)

Summary of the change; the exact registry pattern you mirrored (cite lines);
the killed-cut evidence (both runs); the whole-file test result line; any
NEEDS_SCOPE/NEEDS_RULING; anything you were unsure of. Keep it under 8000 bytes.
