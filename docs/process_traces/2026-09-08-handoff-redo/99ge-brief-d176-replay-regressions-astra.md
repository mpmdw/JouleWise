WRITE_SCOPE: ["tests/test_magistrate_watchdog_cli.py","tests/test_powermetrics_fiducial.py","tests/test_run_campaign.py","joulewise/arm_readiness.py","joulewise/night_gate.py","scripts/run_night.py","tests/test_arm_readiness.py","tests/test_t0_rehearsal.py","docs/contracts/pack_night_go_receipt.md","tests/fixtures/magistrate_watchdog/README.md"]

# D-176 integrated head — full-suite replay regressions + seat-4 delta residue (gpt-6-astra, HIGH, genre implementation)
Branch int/2026-09-08-d176-seats-2-3 at bda71e60 (seats 2+3 + census cure + seat 4). The lead's full replay on c16a2ac4
(pre-seat-4) failed 1+11 (list at the absolute path /Users/edr/code/JouleWise/docs/process_traces/2026-09-08-handoff-redo/99gc-replay-failures-d176-c16a2ac4.txt; log
/private/tmp/claude-501/-Users-edr-code-JouleWise/1d65b6ea-5518-4207-8f65-31f8bf376204/scratchpad/replay-intd176.log — grep the tracebacks). Cure with these RULINGS:
A. tests/test_magistrate_watchdog_cli.py (3 errors, "pack_night keys must be exact"): the watchdog's production-plan
   fixtures carry the pre-§10.3 five-key pack_night; add the sixth exact key `pack_root` (absolute, basename == pack_id)
   to the fixtures — the parser is right; do NOT relax exact keys. If the fixtures live under tests/fixtures/…, update
   them and their README.
B. tests/test_powermetrics_fiducial.py CalibrationLaunchAuthenticationTests (8 errors, "untracked pack entry:
   calibration-acceptance.json"): the consumption-point pack-tree digest (§10.3 item 5, third digest point) now
   recomputes committed_pack_tree_sha256(pack_root) and refuses untracked entries. RULING: that check applies ONLY to
   TRANSACTION_PACK launches; if these tests exercise a non-pack class, the check must not fire (fix the call site);
   if they exercise a pack class, their fixtures must commit the file into the pack tree (the production flow never
   has untracked pack entries at consumption — state that as the invariant in §10.3). Determine which by reading the
   tests; report which.
C. tests/test_run_campaign.py CampaignLaunchLineagePreflightTests.test_consistent_locator_swap_after_outer_preflight_refuses
   (expects launch_lineage_conflict, gets launch_go_receipt_invalid): RULING — for a TRANSACTION_PACK launch the GO
   admission/checks precede lineage-consistency checks (the GO is the authorization; lineage is a consistency check
   on already-admitted inputs), so the expectation updates to the GO code IF the fixture is a pack launch WITHOUT a
   GO; if the fixture is a non-pack class, the GO code must not appear at all and the consumer has a class leak —
   fix the leak. Report which.
D. Seat-4 delta residue (/Users/edr/code/JouleWise/docs/process_traces/2026-09-08-handoff-redo/99gd-delta-d176-seat4-fix-opus-review.md): pin the §10 F6 row (~:865) with line numbers
   (t0_rehearsal.py evaluate_g5 def line; tests/test_t0_rehearsal.py PackGoReplayTests and
   test_legacy_bundle_fails_g5_even_with_passing_g7_control lines); §7.1 row 4 says "items 6–9"; revisit
   tests/test_arm_readiness.py ~:152–157/:210 so LaunchConsumptionV2Tests' setUp isolation assertion is NOT relaxed for
   its own cases (give the fixture factory its own helper instead).
Acceptance (rc-gated to a log; named modules ONLY, NEVER discover/shard; end your turn after the named acceptance):
tests.test_magistrate_watchdog_cli tests.test_powermetrics_fiducial tests.test_run_campaign tests.test_arm_readiness
tests.test_t0_rehearsal tests.test_launch_window tests.test_night_gate tests.test_run_night tests.test_docs_freshness;
git diff --check; no commit; header < 8192 bytes; report per item (A/B/C which branch of the ruling applied, D).
