# WP10 handoff

Implemented on main base `f193a320f`, branch
`lane/2026-11-05-magistrate-desk-fence`.

Commit: `5dfce4be7` — `feat(watchdog): fence headless R0 LaunchAgent handoffs`.
This handoff and its run report are in the subsequent documentation commit.
No push, installation, real measurement, network or coordination-state edits.

The magistrate publishes `{purpose,pid,deadline}` and bootstraps a unique
one-shot LaunchAgent. The wrapper takes fence ownership, waits for the
magistrate to exit, checks AC power and reports free space, pauses both
Spotlight daemons, and resumes them through normal/error/SIGTERM cleanup.
Active fences block relaunches; dead or expired fences clear. Existing plan
stand-down and census rules remain in force. The launcher ancestor argv
contains no second R0 entry-point name.

Files changed: watchdog; new Python launcher and shell wrapper; new WP10
tests; existing watchdog digest-fixture test; watchdog documentation; new
headless runbook; this handoff; dated run report.

Last targeted-module results:

| Module | Result |
| --- | --- |
| `tests.test_magistrate_desk_fence` | 23 passed |
| `tests.test_magistrate_watchdog` | 155 passed |
| `tests.test_magistrate_watchdog_cli` | 7 passed |
| `tests.test_magistrate_watchdog_span` | 24 passed |
| `tests.test_magistrate_watchdog_b6` | 9 passed |
| Installer module, safety wrapper | 9 passed, 1 skipped |
| `tests.test_magistrate_watchdog_yield` | 17 passed, 3 failed |

The three yield failures reproduce unchanged with the base watchdog (3/3
baseline failures). The D-172 live-fence mutation fails its CLI test as
expected (1/1). Compileall, shell syntax and whitespace checks pass.

Full suite, CI, Opus approval, real launchd/Spotlight permissions and MLX/native
checks were not run. No new Ed ruling is needed. Lead must supply WP13's exact
paths/deadline and approve the full-tier review before use. SIGKILL cannot run
a trap; fence PID reuse and cleanup margin remain explicit limits.

The existing yield fixture emitted subprocess ResourceWarnings and its
process-list cleanup is blocked here; native cleanup of synthetic processes
matching `/private/tmp/jwsol/v4-wp10/tmp/b5-driver-` is not certified. One
development rerun briefly overlapped the yield run; later tests were serial.

[Run report](docs/run_reports/2026-11-05-align-v4-wp10-desk-fence.md) contains
exact commands/counts, failure comparison, mutation evidence, limitations,
and the lead's next steps. [Launch interface](docs/process/R0_HEADLESS_LAUNCH.md).
