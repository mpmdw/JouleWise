# Opt-in audit handoff — 2026-11-08

Branch: `perf/2026-11-08-optin-audit`, supplied at `05b6d04cb`.

The [complete audit](../perf/2026-11-08-optin-audit.md) inventories 806 test IDs across the requested three refs, including 45 S10 fixture-gated cases per analysis ref, and records gates, CI coverage, results/deferrals, known pass boundaries, and per-test recommendations. The [JSON ledger](../perf/2026-11-08-optin-audit-results.json) contains process manifests and observations; the [read-only scanner](../perf/2026-11-08-optin-audit-scan.py) reproduces the source inventory from pinned Git objects.

Two failures were established:

- Full WP22: both window class setups reject a stale R11 proof after the synthetic X/Y reference counts become 3. The admission boundary passes at `199006f16` and fails after `7895b9e7e`. The added default witness fails in 0.062 s; no full window or native model is needed for it.
- PREQUAL against `origin/main`: `274e1e7a7` changes default runner argv; `9f56fe78d` makes the 120 s help probe incompatible with a 300 s dwell. The same check passes with launcher `cad9b67e0`; before the dwell it still detects the argv mismatch.

Verification: bounded targeted unittest processes totaled 828.8 s; no full suite ran. The full-corpus modules were attempted with their opt-in and capped at 120 s each. Optional dependency paths remain skipped/unqualified; MLX/native and sealed/external prerequisites were not executed. Selected default guards, producer-pin cases on main, and both lane-specific guarded cases passed. `PYTHONNOUSERSITE=1 python3.13 -m compileall -q joulewise tests docs/perf/2026-11-08-optin-audit-scan.py` passed. The packaged scanner reproduced all three pinned inventories exactly, and report coverage/command-name checks passed. `git diff --check` passed. The new witness and existing launcher check intentionally remain red; this is not block clearance.

Boundary uncertainty is material: the initial unguarded dependency probe may have inspected home user-site metadata, and initial Git commands could consult global config. No study outcome content was intentionally opened. Later test runs were fenced and user-site/global config discovery disabled. One diagnostic synthetic collection probe overlapped the initial corpus batch; unittest module processes otherwise ran serially. Details and the audit-fence artifact are disclosed in the full report. The ongoing analysis job was not signalled, reconfigured, or inspected.

No product code, raw evidence, RUN_STATE, TASK_QUEUE, state kernel, or gen-state test was changed. No kernel task, network request, integration, push, merge, or deployment was performed. This report is the handoff in place of lead-owned coordination edits, as required by the brief. No agents were delegated.

Next: lead fixes the synthetic proof refresh and reconciles/pins the launcher contract; reruns the default witness plus `JW_WP22_FULL=1 python3.13 -B -m unittest tests.align.test_v4_w1_synthetic`; then runs the report's separate required nightly/native commands after the ongoing job, with explicit expected counts and no unplanned skip-green. Remaining questions are fixture/native qualification and integration contract ownership, not permission for this audit to read sealed data.
