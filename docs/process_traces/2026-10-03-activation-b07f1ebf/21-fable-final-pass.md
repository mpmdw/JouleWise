# Cold final pass: PR #460 (head `b39d7015`, base `4205713c`)

The change is correct and I found nothing that blocks the merge. It cannot alter a captured byte, a measured value, the registration, or any admission decision other than the intended one.

## What I checked

| # | Check | Result |
|---|---|---|
| 1 | `-m unittest tests.test_gen_g2a_window` | 12 tests, OK |
| 2 | New test run against the base version of `integrated_g2a_chain` | 1 failure, on the `G2A_ROOT` export line (the test does detect the defect) |
| 3 | Old vs new function on the production root shape (root named by the plan id) | One line differs: `G2A_ROOT` ends `…T0742ZT0742Z` on the old code and `…T0742Z` on the new |
| 4 | Old vs new on four other shapes: root without the id, default plan id with default root, default plan id with root containing it, measurement root containing the id | Byte-identical in all four |
| 5 | Chain emitted from this head with the real arm's arguments (into `/tmp`), diffed against the abandoned chain at `/Users/edr/night-custody/d117-g2a-prefill-probe-20261003T0742Z/chain.zsh` | Exactly one line differs (line 70, `G2A_ROOT`); `zsh -n` OK; sidecar verifies |
| 6 | Argv-only inspection of that chain against the real probe root and clone, in the recipe's new form | Exit 0; `--runs-root` is the real root's `runs`; session, window, plan and evidence ids all carry the plan id once; custody, probe root and clone `runs` unchanged |
| 7 | Same inspection without `MEASUREMENT_HEAD` | `FAIL measurement_head must be a full 40-character lowercase SHA-1`, exit 1 (the recipe defect, reproduced) |
| 8 | `gen_g2_phase_d.py --check`; `tests.test_gen_g2_phase_d` and `tests.test_harvest_g2a_window` | PASS; 56 tests, OK |
| 9 | Registration file sha256 at head | `8e45a0e0…a5b8`, equal to the seal record; the diff touches nothing under `configs/` or `joulewise/` |

## Why it cannot alter science

- **Only the pass order changed.** The rename pass and the pin pass are the same code; the rename now runs first, so the pinned `G2A_ROOT` line can no longer be rewritten by it.
- **The only chain that changes is one that could not run.** The old code produced a different chain only when the root contained the runsheet id, and that chain pointed at a directory that does not exist. It would have stopped at its input assertions before any reservation or capture.
- **The harvest now reads the right root.** `scripts/harvest_g2a_window.py:113` takes `G2A_ROOT` from the chain literal, so it archives the directory the probe inputs were actually built in.
- **The recipe line is desk-side only.** It supplies the same variable that `scripts/run_night.py:633` supplies on the real night, and the chain still checks the clone's HEAD against it.

## Findings

1. **Minor (follow-up at re-arm, not a merge blocker).** `docs/process_traces/2026-10-02-design-block2/52-seal-record.md` (Pins table) vs `scripts/gen_g2_phase_d.py:87-90`. The generator is one of the nine files registration §12 pins. Its sha256 moves from `69903ae2…ad16` to `76a7f043…7c46`, and this PR does not extend the seal record. §12 requires the H′ pins to be appended. I read this as a §11 fix (code made to agree with the text, no rule changed), so no new seal is needed. The append should happen before `w1` is re-armed. No arm step enforces it: step2 checks only the registration digest.

2. **Note (no action for this PR).** `registration_block2.md` §12 names later windows as a recovery window or the re-arm of a null or no-capture RECOVER window. This attempt stopped at step2 with nothing published, so it is less than a null window and fits the clause a fortiori. The seal-record extension should say so in one line, so the H′ basis is on record.

3. **Note (verified harmless).** `docs/process_traces/2026-10-03-activation-b07f1ebf/00-session-record.md:28-30` leaves the abandoned attempt's directories in place. The leftover custody directory holds only `chain.zsh` and its sidecar, with no `night_plan.json`, so step0's sibling-plan check does not see it. The doubled-suffix directory was never created. A new t0 gives new ids and paths, so step0's `test ! -e` checks pass.

4. **Nit.** `tests/test_gen_g2a_window.py:140-158` asserts the root, window id, runs root and session id, but does not assert that `CALIBRATION_LEDGER` and `LEDGER_HEAD_PIN` are unchanged. Neither name matches the rename pattern, and check 4 showed them identical even with the id in the measurement root.

FABLE FINAL PASS: PASS
