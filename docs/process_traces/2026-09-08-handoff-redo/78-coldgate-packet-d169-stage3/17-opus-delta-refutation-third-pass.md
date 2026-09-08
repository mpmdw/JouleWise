# Opus delta refutation — D-176 seat-1 contract third pass (3a8b101e), 2026-09-08
F1–F11: all PASS (F5: the refuter's own :50 pin was wrong; REHEARSAL_RECEIPT_SCHEMA is t0_rehearsal.py:49 — seat correction accepted).
New defects introduced by the third pass:
1. BLOCKER :205 — the blanket path retype hit the `authorization` row: its `path` now names `night/go_receipt.json` while the same row requires equality with plan `pack_night.authorization_record.path` (:156). Cure: restore "absolute path string inside transaction custody root"; keep the GO-file wording only at :316 and :618.
2. Should-fix :176 — `plan_sha256` row still cites the unreachable launch-context plan path; cure: "installer-pinned plan path supplied by --night-plan".
3. Should-fix :576 — seat-2 writable seam night_gate.py:106–136 contains `_RECEIPT_KEYS` (:122–130) frozen by F2; cure: `:106–121,131–136` + read-only note.
4. Should-fix :592–597 — split-by-symbol paragraph omits joulewise/t0_rehearsal.py (seats 2 and 4).
5. Nit — decision_log D-176 §1 still says three keywords / "it is the D-149 receipt"; no seat owns the dated addendum.
6. Nit — :792 is a blank line inside evaluate_g7 (:790–793); evaluate_g5 starts at :710.
Verdict: LAND-WITH-FIXES (finding 1 first).
