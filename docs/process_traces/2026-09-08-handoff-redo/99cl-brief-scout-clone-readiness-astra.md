# Scout — what makes the v5 measurement clone ARM-READY for the first G2-a window (gpt-6-astra, medium, genre scout, READ-ONLY)
Read, at absolute paths: the G2-a plan seat's deliverables under
/Users/edr/code/JouleWise-wt-g2a-plan/docs/process_traces/2026-09-08-handoff-redo/99cd-g2a-first-window-plan/ (README.md,
night_plan.draft.json, validate_plan.py, preflight.log) and its report /Users/edr/code/JouleWise/docs/process_traces/2026-09-08-handoff-redo/99cd-g2a-first-window-plan/seat-report.md; the
runbook /Users/edr/code/JouleWise/docs/process_traces/2026-09-08-handoff-redo/27-scout-v5-readiness-astra-report.md; docs/process_traces/2026-08-28-live-smoke/preflight.sh and
SHAKEDOWN-G2-RUNSHEET.md; scripts/run_night.py; scripts/gen_g2_phase_d.py; the clone READ-ONLY at
/Users/edr/JouleWise-measurement-v5-20260910-1c83f2a (git status, the venv, pip freeze vs the lock, where the
calibration ledger is expected and why the loader reports calibration_ledger_missing / calibration_ledger_rollback for a
DIAGNOSTIC_NO_PACK G2-a window — does that class need a ledger at all?). Produce ONE table: every prerequisite for a real
G2-a arm, with columns: prerequisite | current state (verified how, file:line or command output) | exact fix command or
action | owner (Ed sudo/hardware vs magistrate desk vs seat) | blocking for G2-a DIAGNOSTIC_NO_PACK yes/no. Include:
the untracked joulewise.egg-info/, the lock diff's extra joulewise==0.1.0, the ledger findings, the sudo preflight
steps, the night-agent install from the clone, the custody root and its permissions, the watchdog's tolerance of the
plan, and the email-then-arm gate. ≤ 900 words; genre scout verdict keys; no edits; header < 8192 bytes.
