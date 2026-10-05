# Lane WD (Sol 6.1 high): no magistrate-watchdog network call during a plan span (memo 3.M)

Worktree: /Users/edr/code/JouleWise-wt-dd5-wd (branch `fix/2026-10-05-watchdog-no-network-in-span` at origin/main e7d13a17). Scratch /tmp/dd5-wd/ only. Leave changes uncommitted; never push. No sudo, launchctl or powermetrics.

Defect (`~/night-archive/ia-0a40/MEMO.md` §3.M, first bullet): the magistrate watchdog's launchd tick runs every 300 s, including during measured windows. Every tick runs `remote_stop_probe()` (`scripts/magistrate_watchdog.py:422`): two HTTPS `git ls-remote` calls, made before the tick checks for an active plan. The census does not see them, and they cost at least 1.75 J. That adds variance to measured members.

Change: the tick decides whether a plan span is active (`plan_span_active`, `:845`) before any network call. While a span is active, the tick makes no network call and no other avoidable work (no subprocess beyond what the span check itself needs). First establish what a remote stop currently does when it lands during an active span, and report that with file:line.

- If a remote stop has no effect on a running window (it only prevents launches), skip the probe during the span. The stop is seen at the first tick after the span ends.
- If a remote stop currently does something during a span (a stand-down, a notice), do not change that behaviour silently. Implement the skip anyway, FLAG the behaviour change with its consequence, and the lead will rule.

Tests: extend the watchdog tests (`tests/test_magistrate_watchdog*.py`). A tick inside an active span makes zero calls to the network probe; the probe raises if called. A tick outside a span still probes. The span-boundary tick probes. Run `tests.test_magistrate_watchdog tests.test_magistrate_watchdog_cli` and any other watchdog test module.

Finish in this turn; FLAG what you cannot close.

WRITE_SCOPE: ["scripts/magistrate_watchdog.py", "tests/test_magistrate_watchdog.py", "tests/test_magistrate_watchdog_cli.py", "tests/test_magistrate_watchdog_span.py"]
