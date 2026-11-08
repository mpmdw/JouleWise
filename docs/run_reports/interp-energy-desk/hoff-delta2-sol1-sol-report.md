Verdict: **HOLD**. Three synthetic witnesses reproduce:

- **HIGH:** production `runs/` declarations admit changed, unbound inputs.
- **HIGH:** an external alias back into the session can change the selected input.
- **MEDIUM:** library verification misses added files inside byte-bound ignored directories.

Committed locally as `42781bc2d` on `align/2026-11-08-hoff-delta2-sol1`. Working tree clean; no push.

Added the [report](/Users/edr/code/CapstoneProject/jw-wt/sol-hoff-delta2-sol1/docs/align/v4/HARVEST-OFF-DELTA2-sol1.md) and [witnesses](/Users/edr/code/CapstoneProject/jw-wt/sol-hoff-delta2-sol1/tests/align/test_hoff_delta2_sol1.py).

Verification: 86 prior targeted tests passed. The new module has six passing controls and three unresolved failures. The 177-file equality, memo and dwell-order checks pass. Total test time: 348 seconds; exact commands are in the report.

Native incidence remains unverified. N1/N2, RSS/finalize timing and physical dwell remain lead-owned gates. Next: fix the three closure gaps and replay the witnesses.