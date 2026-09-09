WRITE_SCOPE: ["docs/contracts/pack_night_go_receipt.md","joulewise/night_gate.py","joulewise/arm_readiness.py","scripts/rehearse_t0_unattended.py","tests/test_run_night.py","tests/test_night_gate.py"]

# D-176 seat 2 — closing nits from the Opus delta (gpt-6-astra, medium, genre implementation)
Head f60e3348 on feat/2026-09-08-d176-seat2-producer. The Opus delta at the absolute path /Users/edr/code/JouleWise/docs/process_traces/2026-09-08-handoff-redo/99el-delta-d176-seat2-fix-opus-review.md
passed findings 1–8 and named N1–N4. Cure: N1 (should-fix) — every §9/§10.3 citation into tests/test_run_night.py
(+12), scripts/run_night.py (+3) and tests/test_night_plan_writer.py (:165→:177) is stale: re-read each cited symbol
and rewrite the 17 numbers (verify each lands on its symbol). N2 — move `_production_inventory` from
scripts/rehearse_t0_unattended.py into joulewise/arm_readiness.py (the constants/resolver area) so joulewise/ no
longer imports scripts/, and have the script import it from there; regression that an import failure cannot crash the
gate (or add ImportError to the catch tuple if the move is impossible — say why). N3 — make the `_pack_evidence`
receipt-path check non-tautological (compare against the ARM state's own recorded paths, not a re-derivation) or
remove it and cite the surviving membership test. N4 — derive the test loop for non-path keys from a source
independent of ARM_CONTEXT_NON_PATH_KEYS (e.g. an explicit literal list in the test) so a mis-classified key is caught.
Acceptance (rc-gated; named modules ONLY, never discover/shard): tests.test_night_gate tests.test_run_night
tests.test_rehearse_t0_unattended tests.test_arm_readiness_schemas tests.test_docs_freshness; git diff --check; no
commit; header < 8192 bytes; report per item.
