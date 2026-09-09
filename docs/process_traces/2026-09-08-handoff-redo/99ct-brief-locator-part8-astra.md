WRITE_SCOPE: ["tests/test_calibration_live_three_window.py","tests/test_bracket_binding_cli.py","tests/test_launch_window.py","tests/test_arm_readiness_evidence_author.py","tests/test_arm_readiness_dry_run.py","configs/paper_supply/supply_map.json","tests/test_paper_custody.py"]

# ICLOUD-CUSTODY-LOCATOR-01 part 8 — full-suite replay regressions (gpt-6-astra, HIGH, genre implementation)
Head 6d35e8af on fix/2026-09-08-icloud-custody-locator. The lead's full-suite replay (shard_tests.py --workers 4)
failed: 23 failures + 30 errors; the exact failing test ids are at the absolute path /Users/edr/code/JouleWise/docs/process_traces/2026-09-08-handoff-redo/99cs-replay-failures-locator-6d35e8af.txt
and the full log at /private/tmp/claude-501/-Users-edr-code-JouleWise/1d65b6ea-5518-4207-8f65-31f8bf376204/scratchpad/replay-locator.log (grep the tracebacks). Two classes, cure both:
A. TEST DOUBLES lacking the new `mode` keyword: tests/test_calibration_live_three_window.py patches
   `_candidate_from_observation` / `discover_calibration_candidates` with fakes (`_candidate`) that reject
   `mode=`; tests/test_bracket_binding_cli.py likewise. Update the fakes to accept and RECORD `mode`, and add one
   assertion per module that the production chain forwards `mode="issuing"` by default and `read_replay` when the
   session requests it (do not weaken any existing assertion). The errors in test_launch_window
   (ProductionArmRelocationLaunchTests), test_arm_readiness_evidence_author and test_arm_readiness_dry_run are
   CASCADES: they run the arm-readiness "focused suite" which includes the three-window tests ("focused suite refused:
   errors=20") — confirm they pass once A is cured and change nothing in them unless a genuine mismatch remains (say
   which).
B. STALE SUPPLY-MAP RECEIPT DIGESTS: tests/test_paper_custody.py (RoundFiveTests, PaperCustodyApiTests,
   PaperCustodyCensusTests) and tests/test_paper_rendering.py fail with "stale supply-map receipt digest:
   reported_energy_parents / d165_closeout / claim_evidence" because files this lane changed are in the paper custody
   transitive source census. Do a HASH-ONLY repin of configs/paper_supply/supply_map.json (diff must show only digest
   fields; no role, grant or production digest added or changed — assert that in the report). If the census
   fixture in tests/test_paper_custody.py pins an inventory digest, repin it the same way and say so.
Acceptance (rc-gated to a log): tests.test_calibration_live_three_window tests.test_bracket_binding_cli
tests.test_launch_window tests.test_arm_readiness_evidence_author tests.test_arm_readiness_dry_run
tests.test_paper_custody tests.test_paper_rendering tests.test_custody_mode_inventory
tests.test_calibration_ledger_custody tests.test_whole_window; git diff --check; no commit; header < 8192 bytes; report
per class with file:line and the assertion added.
