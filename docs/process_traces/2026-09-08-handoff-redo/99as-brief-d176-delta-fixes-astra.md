WRITE_SCOPE: ["docs/contracts/pack_night_go_receipt.md","docs/decision_log.md","docs/process_traces/2026-09-08-handoff-redo/85-d176-install-astra-report.md"]

# D-176 seat-1 contract — Opus delta findings N1–N6 (gpt-6-astra, medium, genre implementation)
Head 3a8b101e (branch feat/2026-09-08-d176-stage3-ruling). The Opus delta refutation passed F1–F11 and found six new
items; cure ALL, verifying every line by reading the file (numbers below are the refuter's at 3a8b101e):
N1 (BLOCKER) pack_night_go_receipt.md ~:205 — the `authorization` row's `path` was retyped to "absolute
  `night/go_receipt.json` path string inside transaction custody root", but the same row requires it to equal plan
  `pack_night.authorization_record.path` (the authorization record inside plan `custody_root`, ~:156). Restore
  "`path`: absolute path string inside transaction custody root" (the authorization record's own path); keep the
  `night/go_receipt.json` wording ONLY where the GO file's own location is meant (~:316, ~:618). Grep the whole file
  for `night/go_receipt.json` and confirm every remaining occurrence refers to the GO file, not another record.
N2 ~:176 — `plan_sha256` row still says "consumer re-reads the pinned launch-context plan path" (the route F1
  removed). Replace with "consumer re-reads the installer-pinned plan path supplied by `--night-plan`".
N3 ~:576 (seat 2) — writable seam `joulewise/night_gate.py:106–136` contains `_RECEIPT_KEYS` (:122–130) which F2
  freezes. Change to `:106–121,131–136` and add ":122–130 `_RECEIPT_KEYS` read-only".
N4 ~:592–597 — extend the split-by-symbol paragraph to `joulewise/t0_rehearsal.py`, shared by seat 2 and seat 4
  (list each seat's exact lines as installed elsewhere in the file).
N5 docs/decision_log.md D-176 entry — add a DATED 2026-09-08 addendum (do not edit the original text) stating: four
  required consumer keywords (`--night-plan` added), the GO receipt lives in `night/go_receipt.json` (the D-149
  `night/receipt.json` shape is unchanged for every class), and that the contract's §10/§10.1 rulings govern where
  they refine §1. This seat is the addendum owner; say so in the contract's seat-1 row.
N6 seat-4 seam ~:792 is a blank line inside `evaluate_g7` (:790–793) and `evaluate_g5` starts at :710 not :714 —
  re-pin both by reading joulewise/t0_rehearsal.py.
Append a "fourth pass" section to report 85. Acceptance: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest
tests.test_docs_freshness tests.test_gen_state` rc 0 to a log (gen_state because the decision log changes —
if EXPECTED_IDS/count pins fail, report NEEDS_RULING rather than editing tests); `git diff --check`; no commit;
header < 8192 bytes.
