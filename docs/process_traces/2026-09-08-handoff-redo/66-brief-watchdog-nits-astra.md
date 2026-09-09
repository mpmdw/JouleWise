WRITE_SCOPE: ["scripts/magistrate_watchdog.py","scripts/install_magistrate_watchdog.sh","docs/process/MAGISTRATE_WATCHDOG.md","tests/test_magistrate_watchdog.py","tests/test_magistrate_watchdog_cli.py","tests/test_install_magistrate_watchdog.py"]

# Seat brief — WATCHDOG-NITS-01 (gpt-6-astra, medium)
From the Opus final-head review of the census series (trace docs/process_traces/2026-09-08-handoff-redo/23-opus-final-head-contract-review.md
F2-F4) and the delta re-audit (24), all now on main (138e7edb):
F2 — `scripts/magistrate_watchdog.py` corrupt-lock branch appends a `corrupt_lock_refusal` event on EVERY tick with
no dedupe (~288 rows/day while stalled), and `notice_pending` dedupes on `reason` while the ack path keys on `id`, so
a churning `pids=[…]` list grows `notice_pending` with repeated ids. Cure: emit the event once per distinct reason
per activation (or once per state change), and key the notice dedupe on `id` consistently; regression: 10 ticks with
the same corrupt lock → 1 event and 1 pending notice; a changed pid list → a second.
F3 — `scripts/install_magistrate_watchdog.sh:90-113` re-implements `handoff_process_role`'s daemon/spare/pty-host
classifier inline; replace with a call to `"$python_bin" "$script_dir/magistrate_watchdog.py" handoff-daemons`
(the step-1 gate already uses it) and keep the installer's refusal semantics; regression: the installer refuses on
each daemon shape via the shared classifier (the existing test_install_refuses_live_daemon_host_or_spare_before_any_write
must still pass) and a test pins that the inline regex is gone.
F4 — the documented step-4 reconciliation block in docs/process/MAGISTRATE_WATCHDOG.md reads the lock bytes before
an existence check, so running it with no lock file dies with a raw FileNotFoundError; cure: a named refusal
(`handoff_lock_absent`) before reading; keep the block's extraction contract (`zsh -n`, `compile()`); regression via
the documented-block extraction tests.
Also record (doc note only, no code) the residual: PID + seconds-resolution `lstart` identity; XNU's unique pid
would be stronger — one sentence in the doc's safety-model section.
Acceptance = the three scoped test modules to a log with rc; never the repository-wide suite; no `git commit`;
header < 8192 bytes; genre implementation verdict keys; body = per-finding cure + counterfactual + tails.
