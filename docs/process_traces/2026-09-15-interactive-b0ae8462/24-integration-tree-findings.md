# 24 — Integration tree `int/2026-09-16-merge-wave`: two cross-lane findings (magistrate b0ae8462, 2026-09-16 01:15 PDT)

All six lanes rebased onto the merged main individually clean; stacking them found what single-lane gates cannot:

1. **A172 × A210.** `tests/test_arm_retry.py::test_midnight_retry_two_days_later_before_install_close` pinned
   `install_close_epoch = t0 − 85 min` by construction (`third_open + 6000` with a `+ 900` close). Under A210's 10-minute
   floor the epoch moves by 75 min (1789633800 ≠ 1789629300). Fix on the A172 branch (`922c3cef`) and the tree: derive
   the lead from `run_night.install_close_epoch` on a probe plan, so the cell holds under any lead.
2. **A208 × docs-freshness fence.** A208's session-end checklist sentence "the codex/claude/t3 census are unchanged"
   matched the fence's volatile "orchestration model name" literal (`tests/test_docs_freshness.py:74`). Fix on the A208
   branch (`9ea71f2b`) and the tree: "the night gate's agent census".

Two doc conflicts resolved by ruling during the merges: runbook §0.6 (A173's classifier text governs, plus one A172
sentence bridging the `arm_idle_interactive` retry cause for real plan classes) and the glossary (A173's definitions
with A210's `t0 − 8 min` boundary). Integration quick tier: 153 modules, 0 failures, 64 s. Full replay re-run at the
final tree head `881a8d6b` before the merge wave. Registered by 08ca8197 this hour: A213 (pgrep-dialect test parser),
A214 WALL-METER-GAIN-01 (Ed is buying a POWER-Z KM003C; lane ed_external until it arrives).
