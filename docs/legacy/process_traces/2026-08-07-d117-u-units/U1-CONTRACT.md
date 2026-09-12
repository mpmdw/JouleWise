WRITE_SCOPE: ["joulewise/calibration_ledger.py","joulewise/calibration_bracketing.py","scripts/reserve_calibration_window_bracket.py","tests/test_calibration_ledger.py","tests/test_calibration_bracketing.py"]

IMPLEMENTATION UNIT U1 — two-slot ledger bracket-session capability + exact bracket binding.

Governing design: docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md
(finding F1 + "Ranked design decisions" item 1 + the §5A bookend sequence + the
regression expectations in "Synthetic three-window live-ledger regression") and
RATIFICATION.md in the same directory (rulings 1-3). If the memo, this prompt, and
existing code contracts conflict, named decisions (D-109/D-116 semantics in
docs/decision_log.md) win — report the conflict, do not force it. If a requested
behavior contradicts the ledger's existing fail-closed invariants, do not weaken the
invariant — report.

BUILD: an atomic bracket-session capability so ONE quiet window can finalize BOTH its
pre and post calibration observations under one unchanged committed head pin:
- session open: appends a session capability record reserving exactly two slots (pre,
  post) bound to a window/plan identity, verified against physical-head == committed
  pin at open time only;
- pre finalization: fills slot 1; post finalization: fills slot 2; each slot is
  one-use, immutable once finalized, and refuses out-of-order or duplicate use;
- governed abort/closure record for a window that dies between slots (partial state
  recoverable per memo: the abort closure is itself a receipt, never a deletion);
- exact post-collection bracket binding: the binding names the exact two receipt ids +
  content digests, refuses neighbor substitution, cross-window binding, open sessions;
- candidate discovery: finalized session observations become discoverable candidates;
  unfinalized/aborted never leak as candidates; import-exclusion unchanged;
- terminal head commit path: after post finalization the terminal head is pinned;
  physical/pin mismatch, rollback, fork refuse.

Tests: defect-shaped regressions for EVERY refusal above (duplicate/reordered/
conflicting session receipts; open session without governed closure; head mismatch;
neighbor endpoint substitution; candidate leakage from unfinalized slots), plus the
happy path (open→pre→science-gap→post→bind→terminal pin). Keep the existing suite
green: run focused tests AND `python3 -m unittest discover -s tests` unpiped and
report exact tail + exit codes.

Do NOT commit (worktree; the lead commits). Do not touch bookkeeping/state/manifest/
audit files — the trail is not yours to repair. No scope creep beyond WRITE_SCOPE; if
closure genuinely requires another file, early-return NEEDS_SCOPE with the exact path
and reason. Report deviations and what the lead should double-check.
