WRITE_SCOPE: ["joulewise/analysis_engine/ratio.py","joulewise/analysis_engine/claim_side_bound.py","tests/test_claim_side_bound.py","tests/test_analysis_ratio.py","tests/fixtures/paper_custody/run_kills.py","docs/contracts/paper_claim_side_bound.md","docs/paper/results-fill-registry.md","joulewise/paper_custody.py","tests/test_paper_custody.py","configs/paper_supply/supply_map.json"]

# Paper S3 — unit vocabulary fix under the rule-11 consult (gpt-6-astra, HIGH, genre implementation)
Head 9760ee53 on feat/2026-09-08-paper-S3. The consult at the absolute path /Users/edr/code/JouleWise/docs/process_traces/2026-09-08-handoff-redo/99dt-consult-s3-units-astra-report.md
(read it; the two Opus reviews 99cz/99dn beside it are its inputs) RULES the vocabulary; the magistrate adopts it:
RULING: the sidecar copies from claim_verdicts (the B8 path), where the metric unit is author-supplied and
analysis_manifest.py ~:397/:1320–1321 requires exactly `J/token` for ratio estimands and `J` with null ratio for
absolute contrasts (:540–541); there is NO AP-SPEC → B8 unit conversion (the AP-SPEC estimand units
J/committed_output_token / J/accepted_draft_token belong to the v2 manifest path that analyze-claims rejects). Therefore:
1. ONE shared authority: add to joulewise/analysis_engine/ratio.py canonical constants (`ABSOLUTE_METRIC_UNIT = "J"`,
   `RATIO_METRIC_UNIT = "J/token"`) and a validator `validate_metric_unit_and_ratio(unit, ratio_estimand)` that accepts
   exactly {J + None} or {J/token + valid exact B8 mapping} and refuses every other pairing (both AP-SPEC strings,
   J/parsecs, empty/non-string, J with a mapping, J/token with None). S3 calls it; DO NOT change the acceptance of
   analysis_manifest.py or artifact.py in this lane (register UNIT-VOCAB-SHARED-01 as a one-line follow-up in the
   contract's follow-ups list: wire the shared validator into manifest and verdict validation).
2. claim_side_bound.py ~:24/:125–135: remove the AP-SPEC-derived _UNITS; use the shared validator; the `_j` guard
   keys on unit ≠ J as before. Fix the contract's registry pin (paper_claim_side_bound.md ~:51) and the registry
   binding text to name the B8 vocabulary.
3. Regressions (consult S1): for EACH B8 form, all other fields valid: J/token + valid mapping → produces and
   validates; J/parsecs, J/committed_output_token, J/accepted_draft_token + valid mapping → unit_mismatch through BOTH
   APIs; J + mapping → refuse; J/token + None → refuse. Add a `units_membership` mutation to S3_MUTATIONS (remove only
   the membership check → the regression must fail): report "N mutations over M distinct guards" honestly.
4. If the source census digest moves, hash-only repin supply_map.json (assert only digest fields changed).
Acceptance (rc-gated to a log): tests.test_claim_side_bound tests.test_analysis_ratio (if it exists) tests.test_paper_custody
tests.test_paper_comparison_placements tests.test_docs_freshness; run_kills.py --s3; git diff --check; no commit;
header < 8192 bytes; report per item with file:line and the counterfactual.
