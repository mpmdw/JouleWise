# Seat B fix round 2 — delta re-audit R1 (fragile X4 regression) and R2 (skew rationale)

Same worktree `/Users/edr/code/JouleWise-wt-rh-transport`, branch `feat/2026-09-16-reserve-hang-transport`, head `64297f9d` (your fix round 1 is committed). Same rules: NO git writes; the lead commits by pathspec; WRITE_SCOPE in the header; tests as `TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest <module>`; bytecode to `/tmp`; no real `launchctl`, `~/night-custody`, measurement roots, or network.

A fresh delta re-audit (read-only: `nl -ba /Users/edr/code/JouleWise-wt-bk-9853dd2b/docs/process_traces/2026-09-16-activation-9853dd2b/28-seat-B-delta-reaudit-report.md`) confirmed every closure of fix round 1 by re-applying each defect, and found:

## R1 (SHOULD-FIX) — the new X4 FIFO regression is timing-fragile (`tests/test_run_night.py:~2539`)
Under load the probe's whole deadline expires DURING CLI STARTUP (the worker's eager imports take ~2.7–3.5 s) before the blocked binding read is reached, so the receipt says `phase=startup` and the assertion `phase=bindings` fails; the lead's unloaded run passed it, the refuter's loaded runs failed it repeatedly. The refuter's independent synchronized-entry probe (3 s FIFO budget, 4.5 s wall) passed at head with `phase=bindings` and the worker absent. Make the committed regression reliably reach the blocked read while keeping the deadline assertion: synchronize on entry (assert the probe has reported/entered the bindings phase before the deadline can bite — e.g. a generous `--timeout-s` such as 15 s with the FIFO writer releasing only after the receipt's phase file or progress record shows `bindings`, or a deadline that starts only when the harness observes the bindings phase), and keep asserting: `outcome: timeout`, `phase: bindings`, receipt within `--timeout-s` + 2 s of the probe's own start, no surviving worker. Run it 5 times in a row and paste the wall times. Account for CLI startup explicitly in a comment. Do not weaken the property.

## R2 (NIT) — the 60 s future-skew allowance on `finished_epoch_s` has no rationale (`joulewise/night_agent_install.py:~734`)
Add the comment: the bound tolerates the small forward step a clock resynchronisation can produce between the probe's wall-clock stamp and the installer's read (the machine-move episode of 2026-09-16 stepped the clock; `kern.boottime` moved by tens of milliseconds and NTP corrections are bounded well under a minute), while anything larger indicates a forged or mis-stamped receipt. Do not change the value.

## Verification you must run and paste
- `TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_run_night 2>&1 | tail -4`, plus the 5× loop of the R1 test with wall times.
- compileall rc; `git status --short` (only the two paths) and `git diff --stat`.

Final message: the claude-codex-report/v1 envelope under 8000 bytes.
