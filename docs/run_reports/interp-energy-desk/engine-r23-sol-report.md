Committed **`bfa33bdd5cf84dbfd47c260f48fc28c3d8fc7db9`** on `engine-r23`. Clean tree; not pushed.

Applied A37 and all R23 rulings, added synthetic hand tests, and updated `ENGINE-sol.md`.

**125 targeted tests passed**, including serial/parallel byte equality. Compileall and diff checks passed. Exact commands, per-module results, and all 12 changed files are in the [run report](/Users/edr/code/CapstoneProject/jw-wt/sol-engine-r23/docs/run_reports/2026-11-08-engine-r23.md).

Exporter findings, unchanged: sensor roles use `s_fast`/`s_slow`; anchor run IDs are window-local.

No implementation blockers remain. Qualification is synthetic only; full-suite and captured-fixture cases were deliberately unrun. No MLX code changed. Next: lead registers the export contract and runs the independent synthetic comparison/release rehearsal.