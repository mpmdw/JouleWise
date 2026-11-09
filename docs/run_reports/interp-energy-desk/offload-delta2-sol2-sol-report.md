**HOLD.** The reported deletion races and pressure-release defect are closed, but two accepted layouts still fail native restore from either verified copy:

- A link targets an empty external directory absent on the restore host.
- Session files under `.external/` collide with the native transport namespace.

No permanent archive-byte loss was demonstrated. The same-inode/mtime-reset residual is acceptable as LOW under immutability of all deletion roots. Fork-inherited lock re-entrancy is also LOW.

Changed only the [report](/Volumes/JW-EXT/jw-wt/sol-offload-delta2-sol2/docs/ops/AIR-OFFLOAD-DELTA2-sol2.md) and [witness module](/Volumes/JW-EXT/jw-wt/sol-offload-delta2-sol2/tests/test_offload_delta2_sol2.py).

Ran `TMPDIR=/private/tmp python3.13 -B -m unittest <module>` separately:

| Module | Result |
|---|---|
| `tests.test_offload_delta2_sol2` | 17 OK |
| `tests.test_offload_delta_fixes` | 24 OK |
| `tests.test_offload_review_fixes` | 20 OK |
| `tests.test_offload_window` | 96 OK |
| `tests.test_offload_bench` | 1 OK |

Four passing witnesses intentionally reproduce failures/residuals. Syntax and diff checks passed.

Committed locally as `9d8078287` on `ops/2026-11-08-offload-delta2-sol2`. Clean tree; no push.

Next: lead disposition of both restore gaps, fix or refuse those layouts, then verify native Air restore. Their prevalence in production remains unknown.