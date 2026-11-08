Committed locally on `align/2026-11-07-km003c-align`; tree clean, nothing pushed.

- `4c1041c78`: reused Block meter supervision; added W1 readiness enforcement, per-member missing-DC flags, and **SECONDARY / not yet registered** DC integrals/residuals.
- `d2f38bd14`: handoff report.

R1 and coordination-state files are untouched. Selected unittest modules reported OK: **204 tests, 14 skipped**. Compileall and diff checks passed. Kit `--check` still refuses the existing R0/R1 placeholders.

[Wiring and custody documentation](/Users/edr/code/CapstoneProject/jw-wt/sol-km003c-align/docs/align/squeeze/KM003C-ALIGN.md) · [Files, test commands/results, and open questions](/Users/edr/code/CapstoneProject/jw-wt/sol-km003c-align/docs/run_reports/2026-11-07-km003c-align.md)

**Cleanup remains unverified:** sandbox restrictions prevented inspection/signaling of earlier fake-test children: **43562, 43565, 43946, 43949**. The lead should verify their identities outside the sandbox and clean up surviving fixtures before measurement.

Live capture/stop/hash verification, PDTR agreement, battery correction and DC registration remain lead-owned; no hardware validation is claimed.