Committed the local stack; working tree is clean. Nothing pushed.

**410 files removed; 5,128 → 4,761 tracked files**, including plan/tool/report additions.

| Group | Commit | Deleted | Report |
|---|---|---:|---|
| g1 traces | `98bc99fd4` | 112 | [Details](docs/run_reports/2026-11-10-file-prune-g1.md) |
| g2 campaigns | `a7bacd7b1` | 297 | [Details](docs/run_reports/2026-11-10-file-prune-g2.md) |
| g3 CA-42 | `30098da9d` | 0—held | [Gate](docs/run_reports/2026-11-10-file-prune-g3.md) |
| g4 spikes | `2df4fc6ec` | 1 | [Handoff](docs/run_reports/2026-11-10-file-prune-g4.md) |

Updated CANONICAL, archive guidance, registry, timing hints and historical test readers. Per-path inventories record every KEEP decision. All nine D117 generations stay because live historical readers require them. #654 is folded in; `dcaf2ca2c` is included.

Verification passed:

- `compileall -q joulewise scripts tests`
- `repin.py --check`: 16 families
- Frozen-files tests: 4; seal-landing tests: 9
- Focused tests, including 42 retained MLX runtime tests using synthetic stand-ins
- Zero live deleted-path references; zero lost surviving protected pin bindings

Full suite and native MLX execution were not run.

**G3 remains blocked:** live ALIGN registration binds 20 candidate files and lacks the replacement closure. Your ALIGN deferral prevents the required migration, so the entire coupled unit stays and #668 remains held.

**NEEDS_RULING:** keep g3 held until the ALIGN owner migrates it, or commission a joint migration afterward? I recommend keeping it held.