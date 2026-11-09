**HOLD.** F1, F3, S1-03 and S1-04 are closed for the reported cases. F2 remains incomplete under concurrent pack-path reuse.

Reproduced three blockers:

- Resumed cleanup hashes an old inode, then deletes a replacement payload.
- A link replaced by a regular file loses unbacked bytes.
- Pressure release can finish with only the Air copy intact.

Committed locally as `753969e36` on `ops/2026-11-08-offload-delta-sol1`. Clean tree; no push.

Changed files:

- [Review report](/Volumes/JW-EXT/jw-wt/sol-offload-delta-sol1/docs/ops/AIR-OFFLOAD-DELTA-sol1.md)
- [Synthetic witnesses](/Volumes/JW-EXT/jw-wt/sol-offload-delta-sol1/tests/test_offload_delta_sol1.py)

Each module ran separately with `python3.13 -B -m unittest`:

| Module | Result |
|---|---|
| `tests.test_offload_delta_sol1` | 17 passed |
| `tests.test_offload_review_fixes` | 20 passed |
| `tests.test_offload_window` | 96 passed |
| `tests.test_offload_bench` | 1 passed |

Passing witness tests reproduce defects. No full suite or real-data work ran.

The blockers require concurrent filesystem changes; their production frequency is unknown. Next: lead fixes or disables the affected deletion routes, then reruns the witnesses as safe-behavior regressions.