WRITE_SCOPE: ["configs/paper_supply/supply_map.json"]

# ICLOUD-CUSTODY-LOCATOR-01 — hash-only supply-map repin after merging main (gpt-6-astra, medium, genre implementation)
Branch fix/2026-09-08-icloud-custody-locator, HEAD = merge of origin/main (5a3a56c7, paper S2+S3+S7) into the locator lane;
configs/paper_supply/supply_map.json was taken from main verbatim, so its fixture receipt/inventory digests no longer
match the merged source census (the locator lane changed joulewise/calibration_ledger.py, whole_window.py,
analysis_engine/inputs.py etc., which are in the paper custody transitive source census). Do ONE hash-only repin: run
tests.test_paper_custody to see the "stale supply-map receipt digest" failures, recompute every fixture family's
receipt/inventory expected_sha256 against THIS tree, and change NOTHING else (no role, pending role, grant or
production digest; assert by diffing that only expected_sha256 fields changed). Acceptance (rc-gated; named modules
ONLY, never discover/shard; env JOULEWISE_BACKUP_ROOTS=): tests.test_paper_custody tests.test_paper_rendering
tests.test_paper_reported_energy tests.test_claim_side_bound; git diff --check; no commit; header < 8192 bytes.
