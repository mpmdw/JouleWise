**HOLD.** The original F1–F6 witnesses pass, and the producer e2e reaches `release_v4` AGREE. A remaining watchdog-verification bypass accepts invalid present evidence and exports all 22 synthetic C1 captures to both layouts.

Committed `acdf79c67` on `align/2026-11-08-exporter-confirm-sol2`. Clean tree; no push.

- Changed the [report](/Volumes/JW-EXT/jw-wt/sol-exporter-confirm-sol2/docs/analysis/v4/EXPORTER-CONFIRM-sol2.md) and [six synthetic witnesses](/Volumes/JW-EXT/jw-wt/sol-exporter-confirm-sol2/tests/v4_export/test_confirm_sol2.py).
- Tests: 70 existing tests pass; new witnesses yield 2 passes and 4 failures reproducing the bypass. Compileall and diff checks pass.
- Next: refuse invalid watchdog evidence, then rerun the witnesses and e2e.

Synthetic only. Native validation remains unrun; the fixture census was unavailable because sandbox `ps` was denied.