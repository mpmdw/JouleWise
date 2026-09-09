WRITE_SCOPE: ["scripts/run_campaign.py","tests/test_run_campaign.py","tests/fixtures/custody_read_replay_allowlist.json","tests/test_custody_mode_inventory.py","docs/contracts/calibration_ledger_append.md"]

# ICLOUD-CUSTODY-LOCATOR-01 part 7 — bounded final round (gpt-6-astra, HIGH, genre implementation)
Head b598113e on fix/2026-09-08-icloud-custody-locator. Read the magistrate ruling at the absolute path
/Users/edr/code/JouleWise/docs/process_traces/2026-09-08-handoff-redo/99bw-magistrate-ruling-census-scope.md and the Opus review /Users/edr/code/JouleWise/docs/process_traces/2026-09-08-handoff-redo/99bu-ref-locator-6-opus-contract-review.md
(§2 and §3) and the Astra delta /Users/edr/code/JouleWise/docs/process_traces/2026-09-08-handoff-redo/99bv-delta-locator-6-astra-report.md (F1). Do EXACTLY these three things:
1. scripts/run_campaign.py: `_idle_admission_core_evaluation` (~:5257) takes `mode: Literal["read_replay","issuing"]
   = "issuing"` and forwards it to the bracket evaluation; ONLY `_run_whole_window_verdict_locked` (~:6283) passes
   read_replay; the live AXI campaign path (`run_axi_spec_campaign` ~:7909) and any third caller pass nothing.
   Update the allowlist row(s) accordingly (the literal moves to the whole-window replay caller) and make the reason
   name claim-readiness emission explicitly. Regression in tests/test_run_campaign.py: under a non-empty override with
   the original absent and a planted replacement, the live-capture path's bracket evaluation observes ABSENT (never
   the replacement), and the completed-window replay path observes the replacement; plus the forwarded-keyword
   assertion for all three callers.
2. tests/test_custody_mode_inventory.py + allowlist: key rows by (file, function, ordinal-within-function) with
   `line` kept as an uncompared informational field; regression: inserting a line above a listed call does NOT fail
   the inventory, while adding a second replay call in the same function DOES require a new row.
3. docs/contracts/calibration_ledger_append.md: in the part-5/6 addendum, add a "Census limits (ruled 2026-09-08)"
   paragraph listing by name the shapes the census does NOT detect (forwarding through a parameter not named
   `mode`; omitted replay defaults on wrappers; callable-container dispatch; runtime-built dicts) and stating that
   the invariant is the issuing default + caller-supplied modes + entry guards + planted-replacement fixture, the
   census being a governance aid; do NOT add census detection for those shapes.
Acceptance (rc-gated to a log): tests.test_custody_mode_inventory tests.test_calibration_ledger_custody
tests.test_run_campaign tests.test_whole_window; the counterfactuals of items 1–2 in memory; git diff --check; no
commit; header < 8192 bytes; report per item with file:line and the counterfactual.
