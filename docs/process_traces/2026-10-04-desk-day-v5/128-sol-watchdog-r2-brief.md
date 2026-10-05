# Lane WD round 2 (Sol 6.1 high): skip only the network probe during a plan span

Worktree: /Users/edr/code/JouleWise-wt-dd5-wd (branch `fix/2026-10-05-watchdog-no-network-in-span`; round 1 committed). Scratch /tmp/dd5-wd/ only. Leave changes uncommitted; never push. No sudo, launchctl or powermetrics.

Round 1 (`/Users/edr/night-archive/desk-day-v5/sol-wd-r1.md`) made an active-span tick return before probing, census, recovery, fork or custody writes. **Lead ruling on its F1 and F2:** that is too broad.

- The defect (memo 3.M) is the two HTTPS `git ls-remote` calls of `remote_stop_probe()` during a measured span. Only that probe is skipped during an active or installed span.
- Every other tick behaviour stays exactly as at baseline e7d13a17: supervisor recovery, unsafe-session drain, census and clock diagnostics, the zero-capture refusal release (A212's fast retry, which must not wait for the original span bound), local STOP handling, and notices.
- Where baseline logic consumed the remote probe's result during a span, it sees the result as "not probed this tick". This must be a distinct value, never `STOP` and never `NETWORK_UNCERTAIN`, so that nothing drains, holds or emails because of the skip. Remote STOP is seen at the first tick after the span. That consequence is accepted: a remote stop never interrupts a running window.
- Report every consumer of the probe result (file:line) and what it does with the not-probed value.

Tests:
- an in-span tick makes zero network-probe calls, and the probe raises if called;
- an in-span tick still performs the zero-capture refusal release and supervisor recovery, exactly as baseline;
- a local STOP during a span behaves as baseline;
- the first post-span tick probes.

Run `tests.test_magistrate_watchdog tests.test_magistrate_watchdog_cli tests.test_magistrate_watchdog_span`. Do not run the AXI modules: they need `/bin/ps`, which the sandbox denies, and the lead runs them. Finish in this turn.

WRITE_SCOPE: ["scripts/magistrate_watchdog.py", "tests/test_magistrate_watchdog.py", "tests/test_magistrate_watchdog_cli.py", "tests/test_magistrate_watchdog_span.py"]
