WRITE_SCOPE: ["joulewise/night_gate.py","scripts/run_night.py","joulewise/t0_rehearsal.py","scripts/rehearse_t0_unattended.py","joulewise/arm_readiness.py","tests/test_night_gate.py","tests/test_run_night.py","tests/test_t0_rehearsal.py","tests/test_rehearse_t0_unattended.py","tests/test_arm_readiness_schemas.py","tests/test_magistrate_watchdog.py","docs/contracts/pack_night_go_receipt.md"]

# D-176 seat 2 — fix round continuation with the finding-5 ruling (gpt-6-astra, HIGH, genre implementation)
Worktree feat/2026-09-08-d176-seat2-producer at 4b25d29f with the previous seat's UNCOMMITTED fixes for findings
1–4, 6–8 in the tree (report: /Users/edr/code/JouleWise/docs/process_traces/2026-09-08-handoff-redo/99ec-seat-d176-seat2-fix-partial-astra-report.md; keep them; do not revert).
RULING on finding 5: `validate_receipt` and `_RECEIPT_KEYS` stay FROZEN (contract §10 S3). The pack refusal receipt's
`refusal.reason` MUST be a code the frozen validator already accepts; the TRUE driver cause (night_courier_unavailable,
night_plan_overruns_deadman, night_chain_already_started, chain digest mismatch, …) travels in the receipt's `refusal`
object's detail field if the frozen validator accepts a detail there (read validate_receipt to see the exact refusal
object shape it permits), and `refusal.json` stays the authoritative cause record. Choose the registered reason code
that the validator accepts for a driver-side refusal (name it and cite the registry line); `launch_go_receipt_invalid`
is reserved for GO authentication/binding/validity per §3. If the frozen validator permits NO detail field at all,
install the cause ONLY in refusal.json and record in the contract (§10.3 addendum) that the receipt's reason is the
registered driver-refusal code while refusal.json carries the cause — and add a regression that the two agree. Fix
the three failing validator subcases accordingly; never edit the validator or the registries.
Then rerun the full acceptance (rc-gated to a log): tests.test_night_gate tests.test_run_night tests.test_t0_rehearsal
tests.test_rehearse_t0_unattended tests.test_arm_readiness_schemas tests.test_night_plan_writer
tests.test_install_night_agent tests.test_magistrate_watchdog tests.test_docs_freshness; git diff --check; no commit;
header < 8192 bytes; report the finding-5 representation with file:line and the regression.
