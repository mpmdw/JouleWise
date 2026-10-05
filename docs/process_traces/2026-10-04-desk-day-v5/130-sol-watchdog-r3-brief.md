# Lane WD round 3 (Sol 6.1 high): review findings F1 and F2 on PR #484

Worktree: /Users/edr/code/JouleWise-wt-dd5-wd (branch `fix/2026-10-05-watchdog-no-network-in-span` at c53b9d39). Scratch /tmp/dd5-wd/ only. Leave changes uncommitted; never push. No sudo, launchctl or powermetrics.

The executing review (`/Users/edr/night-archive/desk-day-v5/sol-wdrev.md`; reproducers `/tmp/dd5-wdrev/probes.py`, `parity.py`, `all_mutations.py`) failed the PR on two findings:

- **F1 (MAJOR), `scripts/magistrate_watchdog.py:2143`.** The resident supervisor's own refresh checks discovered plans but not the installed-agent fence. So with an installed-only span active it still made both `ls-remote` calls at its normal cadence. Apply the same suppression as `decide()`: no refresh is started while a plan span is active or a night agent is installed.
- **F2 (MINOR), `:457`.** An in-flight refresh does not recheck the span before its second call. Recheck before each of the two transport calls. If the span has started, abandon the refresh, leave the cached value unchanged, and record `NOT_PROBED` for that refresh.

Copy the reviewer's two CONTRACT probes into `tests/test_magistrate_watchdog_span.py` as regression tests: the installed-only resident, and the barrier-controlled in-flight call. They must fail at c53b9d39 and pass after the fix. `parity.py` and `all_mutations.py` must still pass. Run `tests.test_magistrate_watchdog tests.test_magistrate_watchdog_cli tests.test_magistrate_watchdog_span`. Finish in this turn.

WRITE_SCOPE: ["scripts/magistrate_watchdog.py", "tests/test_magistrate_watchdog_span.py", "tests/test_magistrate_watchdog.py"]
