Committed on `align/2026-11-10-w1-integration`; clean tree, no push.

- `978cbea59`: reliability merge.
- `21029737a`: three-way watchdog port, preserving W1 power restoration, timing receipts and desk fencing.
- `8bd8984cb`: handoff report.

Requested functional modules and all 416 trace-generator tests passed; validation took about 19 minutes. Import and synthetic `--dry-run` passed.

Both closure modules remain failing on pending registration bindings. The report lists all four required additions; registration files received no port edits. Native checks remain outstanding, and fixture census was blocked by sandbox denial of `ps`.

[Full report: files, commands, results and exact next steps](/Volumes/JW-EXT/jw-wt/sol-w1-integration/docs/run_reports/2026-11-10-w1-integration.md)