Committed locally as `e3f5f6b5b` on `ops/2026-11-08-prune-plan`. Working tree is clean; nothing pushed or pruned.

Created nine documentation files:

- [Pin inventory](docs/ops/PIN-INVENTORY.md): 1,131 resolvable commits, 203 proposed tags and supporting TSVs.
- [Prune plan](docs/ops/PRUNE-PLAN.md): branch/file retirement, ordered commands, CANONICAL updates and Air/MBP cleanup procedures.
- [Tag-pinning design](docs/ops/TAG-PINNING.md): future validation contract and regression-test design.
- [Run report](docs/run_reports/2026-11-08-prune-plan.md): findings, verification and limitations.

Verification passed: 4 frozen-file tests, 9 seal-landing tests, proposed retention topology, runbook syntax and diff checks. No full suite or native MLX tests ran; no code changed.

Five cited commits remain unavailable: `4cb222a19`, `050aaad13`, `498ad1d0`, `6bcd90a3`, `9a6f8880`. External backups and server protection remain unverified.

Next: after the accepted B5 release receipt, resolve those retention gaps, refresh the inventory, then perform tag creation and standalone-bundle recovery checks before deletion.