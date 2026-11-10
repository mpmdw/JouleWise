Committed on `ops/2026-11-10-watchdog-v5-installed`:

- `59dd6e2b8`: shared parser fix, synthetic regressions, and blinded unstrand script.
- `7b2f2a571`: reader audit and verification report.

Installed v5 plans now accept validated `ac_powermode`. Unknown keys still fail closed; release rules remain unchanged. Legacy v2–v4 output is byte-identical.

Targeted modules: **438 passed; 3 failed identically on untouched base**. `/bin/ps` is denied here; those driver integration tests require a native rerun. Compilation and shell syntax passed.

Operator usage, with `$S` set to completed custody:

```sh
scripts/post_window_unstrand.sh "$S"
scripts/post_window_unstrand.sh --go "$S"
```

The default is dry-run; `--go` performs uninstall. Live MBP recovery remains unverified.

[Full report: files, audit, exact tests, results, and next steps](/Volumes/JW-EXT/jw-wt/sol-wdv5/docs/run_reports/2026-11-10-watchdog-v5-installed.md)

Working tree clean. Nothing pushed.