Committed on `ops/2026-11-11-w1-offload`; tree clean, no push.

- Fixed queue recovery, stale-receipt re-push, exception rc recording, and hold visibility.
- Preserved exit 0 for held `run` calls; added `held_reason`.
- All 17 deletion decisions match the base; release checks remain unchanged.
- All eight targeted unittest modules passed: **219 tests**.

Changed only `scripts/offload_window.py`, `tests/test_offload_window.py`, and the [run report](/Volumes/JW-EXT/jw-wt/sol-w1-offload/docs/run_reports/2026-11-11-w1-offload.md). The report contains exact commands/results, failing-first evidence, and the deletion table.

Commits: `76ef3edfc`, `361e646be`, `742a65897`, `a85ca5024`.

No open semantic questions. Next: lead cold review and remote native checks; installed hardware behavior remains unverified.

Disclosure: an overbroad Git ruling extraction displayed unrelated Block 5 summary text. This is documented in the report; no custody paths were accessed.