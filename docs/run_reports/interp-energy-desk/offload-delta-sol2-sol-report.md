**Verdict: HOLD.** Three remaining findings:

- **HIGH:** Concurrent pack-path reuse lets cleanup delete a new pack, including on crash resume.
- **HIGH:** A verified symlink replaced by a regular file can have its unbacked bytes deleted.
- **MEDIUM:** Native restore refuses carried external inputs when their symlink targets are absent.

Original F1, F3 and S1-03 cases are closed; F2 and S1-04 are partially closed.

Added [report](/Volumes/JW-EXT/jw-wt/sol-offload-delta-sol2/docs/ops/AIR-OFFLOAD-DELTA-sol2.md) and [witnesses](/Volumes/JW-EXT/jw-wt/sol-offload-delta-sol2/tests/test_offload_delta_sol2.py). Production code is unchanged.

Ran `python3.13 -B -m unittest` separately for:

| Module | Result |
|---|---|
| `tests.test_offload_delta_sol2` | 15 OK |
| `tests.test_offload_review_fixes` | 20 OK |
| `tests.test_offload_window` | 96 OK |
| `tests.test_offload_bench` | 1 OK |

Passing witness tests reproduce defects. Syntax and diff checks passed. Synthetic only; production dependency layout and real-host behavior remain unverified.

Committed **`31aa0b00b`** on `ops/2026-11-08-offload-delta-sol2`. Clean tree; no push.

Next: lead disposition of D1–D3, fixes, and inversion of the witnesses into safety regressions.