WRITE_SCOPE: []

# Refuter brief — WINDOW-STATUS-GUARD-CENSUS-01 landing, EXECUTION lens (gpt-6-astra, read-only)
HEAD = one commit on main. Packet: `git diff HEAD~1 HEAD` (scripts/window_status.sh, tests/test_window_status_guard.py).
Claims: the guard now matches real campaign / `window-chain` ENTRY POINTS rather than any argv mention, excludes
campaign `--dry-run`, and takes `JOULEWISE_STATUS_PS_COMMAND` (default real `ps`) so tests inject a census; census
failure refuses before writing. Break it: (1) enumerate the REAL process shapes of a live measurement on this repo —
read scripts/run_night.py (how it launches the chain), scripts/run_campaign.py, scripts/launch_window.py, the
emitted G2-a chain (`python3 -B scripts/gen_g2_phase_d.py --emit-chain $TMPDIR/chain --night-date 20260910`), and
the historical runsheets' `window-chain` invocations — and feed each shape through the guard's matcher with an
injected census: every real shape MUST refuse; (2) feed the non-measurement shapes: `python3 -m unittest
tests.test_run_campaign`, `scripts/run_campaign.py --dry-run …`, an editor holding the file open, a `grep
run_campaign` process, a codex seat whose prompt text contains `run_campaign` — none may refuse; (3) interpreter
wrappers: `/usr/bin/env python3 scripts/run_campaign.py`, `.venv/bin/python …/run_campaign.py`, an absolute path with
a space — which does the matcher miss? (4) the injection: with `JOULEWISE_STATUS_PS_COMMAND` set to a command that
exits non-zero or prints garbage, does the guard fail CLOSED (refuse, write nothing)? (5) `bash -n`, shellcheck if
available; (6) mutation: revert the entry-point matcher to the old substring grep in a $TMPDIR copy and confirm the
sibling-process regression fails. Run only tests.test_window_status_guard. Report (genre review): `verdict` =
{counts, findings}; header < 8192 bytes; findings with file:line, severity, exact demonstrating command.
