Committed `22ea49a5c` on `align/2026-11-08-condition-waits-sol`. Working tree clean; not pushed.

- [Design](/Users/edr/code/CapstoneProject/jw-wt/sol-condwait-sol/docs/align/v4/CONDITION-WAITS-sol.md): wait inventory, proposed condition releases, evidence limits, ≤2 h native plan, savings scenarios and registration implications.
- [Run report](/Users/edr/code/CapstoneProject/jw-wt/sol-condwait-sol/docs/run_reports/2026-11-08-condition-waits-sol.md): verification and handoff.

Recommendation: qualify joint temperature/fan/power readiness and shared quiet dwell. Retain the 300 s member idle and G0/G1/H. Savings remain unproven.

Checks passed:

- `python3.13 -B -m unittest tests.align.test_v4_cadence` — 16 tests.
- `python3.13 -B -m unittest tests.align.test_thermal_gate` — 44 synthetic tests.
- Citation bounds and Git whitespace checks.

Open: independent Opus agreement, final reference channels/power mode, and native qualification before adoption. No full suite, network, live measurements or coordination-state edits.