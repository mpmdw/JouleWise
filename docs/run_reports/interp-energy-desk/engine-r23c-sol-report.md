Committed on `engine-r23c`: `9c3df2163b30d7505ccf673dcf4d4841b9af4c5a`. Clean tree; no push.

Implemented all four changes:

- Refused selection-only W1.
- Added `anchor_sigma_w.W1_anchor_block` with explicit inclusion, exclusion or unavailability.
- Required prefixed anchor IDs in native/release inputs.
- Documented W1’s screened thermal fields reaching U1–U3 and contrast.

Touched four analysis modules, two scripts, two test modules, `ENGINE-sol.md` and the run report.

All **83 targeted tests passed**, one module per process. Compilation, diff checks and serial/parallel byte equality passed. No full suite ran.

No known blockers. Validation remains synthetic; no MLX code changed. Next: lead verifies the common exporter against the updated contract.

[Run report with exact test commands and results](/Users/edr/code/CapstoneProject/jw-wt/sol-engine-r23c/docs/run_reports/2026-11-08-engine-r23c.md)