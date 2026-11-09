**HOLD.** R27 still prints threshold-dependent values before calibration completes:

- Positive-dose `detection` leaves print `false` instead of null.
- Held T summaries print zero alarm totals instead of null.

Other requested rules, W1 config mapping, and calibration pins passed verification. Complete 4- and 12-turn synthetic fills are byte-identical apart from the permitted metadata.

38 repository tests and five independent checks passed; two defect witnesses reproduced the failures. Validation was synthetic only.

Committed [the report](/Volumes/JW-EXT/jw-wt/sol-r23n-sol/docs/run_reports/2026-11-08-r23n-sol.md) as `643e0b086` on `engine-r23n-review`. Only the report changed; the tree is clean, with no push.

Next: fix the R27 leaves, add regressions, and repeat the equality check.