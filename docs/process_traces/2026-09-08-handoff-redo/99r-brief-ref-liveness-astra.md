WRITE_SCOPE: []

# Refuter brief — window-status liveness census landing, EXECUTION lens (gpt-6-astra, read-only)
HEAD = one commit on main (scripts/window_status.sh, scripts/run_night.py, scripts/run_campaign.py, NEW
joulewise/measurement_liveness.py, four test modules). Governing design: consult trace
docs/process_traces/2026-09-08-handoff-redo/94-consult-window-guard-astra-report.md (read at the absolute path
/Users/edr/code/JouleWise/docs/process_traces/2026-09-08-handoff-redo/94-consult-window-guard-astra-report.md).
Claims: the argv classifier is gone; a live chain = plan root with `chain.started` and no `chain.exited` whose
recorded (pid, start token) is alive; campaign liveness via a registry entry + lock with pid/start token, O_EXCL,
stale repair; unknown observations REFUSE before status or Git mutation; `JOULEWISE_CUSTODY_PARENT` (default
~/night-custody) and `JOULEWISE_ADDITIONAL_CUSTODY_PARENTS` (JSON array); 368 tests + 30 counterfactuals.
Break it, on THIS machine's real shapes (never touch the real ~/night-custody; use scratch custody parents via the
env): (1) drive the REAL night driver path that writes `chain.started` with a stub chain (`sleep 30`) under a
scratch custody parent and confirm the guard refuses while it runs and permits after `chain.exited`; kill the chain
child mid-run (SIGKILL) so no `chain.exited` is written: the guard must treat the dead pid (or reused pid with a
different start token) as NOT live and permit (with a warning) — and must never hang; (2) campaign: run
`scripts/run_campaign.py --dry-run` (must NOT register) and a real minimal campaign invocation against a scratch
runs dir with a stub CLI (must register, lock O_EXCL, unregister on exit); crash it mid-run: stale repair must
work and the guard must permit after the pid is dead; (3) the start-token identity: same pid, different start
token → not live; (4) unknown observation (malformed marker JSON, unreadable registry, registry root missing) →
REFUSE before any write; (5) the old false positives: a codex seat mentioning run_night.py, `git grep`, an editor,
unittest processes, `--dry-run` → all permit; (6) mutation: pid-only comparison; ignore chain markers; skip registry
cleanup — the named regressions must fail; (7) `bash -n`; the four modules. Report (genre review): `verdict` =
{counts, findings}; header < 8192 bytes; findings with file:line, severity, exact command.
