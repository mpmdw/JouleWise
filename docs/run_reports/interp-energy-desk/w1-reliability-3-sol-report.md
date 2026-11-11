Committed locally on `ops/2026-11-10-w1-reliability`; clean tree, nothing pushed.

- Added fresh prepare/install frequency checks, zero-or-refuse behavior, and before/after evidence. Clock gates remain unchanged.
- Kept terminal network-time ON restoration and recorded next-arm zeroing ownership.
- Changed session/night scripts, added the C helper, and updated synthetic tests/fixtures.
- **120 focused tests passed**; Python compilation, C syntax, and diff checks passed. Full suite omitted.

Commits: `ae2760684`, `445d5775a`.

[Handoff report](/Volumes/JW-EXT/jw-wt/sol-w1-reliability-3/docs/run_reports/2026-11-10-w1-reliability-r3.md) contains exact test commands/results, sudoers rules, and native checks.

Open: the owning runbook §4 was not found; replacement text is prepared in the report. The lead must identify its destination, provision the helper, re-register, and complete native checks before arming. Hardware behavior remains **PROVISIONAL**.