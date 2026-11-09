**HOLD:** release accepts links to empty external directories, then native restore fails from both backups when those directories are absent. Manual directory creation repairs restore; no irrecoverable payload loss was demonstrated.

The other named deletion fixes pass. The declared same-inode residual is acceptable as LOW under immutability assumptions. Forked library callers also have a LOW lock limitation.

Committed locally as `98989dc26` on `ops/2026-11-08-offload-delta2-sol1`. Clean tree; no push.

Files changed:

- [Review report](/Volumes/JW-EXT/jw-wt/sol-offload-delta2-sol1/docs/ops/AIR-OFFLOAD-DELTA2-sol1.md)
- [14 synthetic witnesses and controls](/Volumes/JW-EXT/jw-wt/sol-offload-delta2-sol1/tests/test_offload_delta2_sol1.py)

Ran `python3.13 -B -m unittest <module>`, separately:

| Module | Result |
|---|---|
| `tests.test_offload_window` | 96 passed |
| `tests.test_offload_review_fixes` | 20 passed |
| `tests.test_offload_delta_fixes` | 24 passed |
| `tests.test_offload_bench` | 1 passed |
| `tests.test_offload_delta2_sol1` | 14 passed |

Syntax and whitespace checks passed. No full suite, network, or real-data work.

Next: fix native empty-directory restoration or refuse that closure before deletion. Its prevalence in production and native mount/power-loss behavior remain unverified.