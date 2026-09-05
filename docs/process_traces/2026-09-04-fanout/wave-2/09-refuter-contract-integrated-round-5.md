```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "NOT LANDABLE: the restored frozen AP-2 validator leaves two stale MODULARITY tests red; one advisor-site wording should-fix also remains.",
  "workspace": {"base_requested":"origin/int/2026-09-04-fan-wave-1","base_mode":"exact","head_start":"d35231f6b00950cd28ccaf81d397f8d701e117a7","head_end":"d35231f6b00950cd28ccaf81d397f8d701e117a7","upstream_end":"d35231f6b00950cd28ccaf81d397f8d701e117a7","branch":"int/2026-09-04-fan-wave-2"},
  "pathspec": ["docs/process_traces/2026-09-04-fanout/wave-2/09-refuter-contract-integrated-round-5.md"],
  "unowned_dirty": [],
  "verdict": {
    "gauntlet": "NOT LANDABLE",
    "landings": {"requested":19,"ancestor_count":19,"name_deviations":[]},
    "prior": {
      "round1":{"F1":"CURED","F2":"CURED","F3":"CURED","F4":"CURED","F5":"CURED"},
      "round2":{"R2-F1":"CURED","R2-F2":"CURED","R2-F3":"CURED","R2-F4":"CURED"},
      "round3":{"R3-F1":"CURED","R3-F2":"CURED_VIA_R4-F1","R3-F3":"CURED","R3-F4":"CURED"},
      "round4":{"R4-F1":"CURED","R4-F2":"CURED","R4-F3":"CURED","R4-F4":"CURED","R4-F5":"CURED"},
      "opus":{"B1":"CURED","B2":"CURED","B3":"CURED","S1":"CURED","S2":"CURED","S3":"CURED","S4":"OPEN_AS_R5-F2","S5":"DISPOSITIONED_NEG8_RULING","S6":"CURED","S7":"DISPOSITIONED_LANE_RULING"}
    },
    "findings": [
      {"id":"R5-F1","severity":"blocker","location":"tests/test_modularity.py:206-230; joulewise/analysis_manifest.py:485-567","text":"The bench correctly restored the frozen v1 AP-2 validator byte-for-byte, but two MODULARITY tests still require its removed registry-generalization behavior; the changed module is red 2/10 and the claim-guard batch is red 2/407.","cure":"Keep the frozen validator bytes. Rewrite the two stale tests to assert the fixed six-pair AP-2 contract, then rerun the touched module and integration suite."},
      {"id":"R5-F2","severity":"should_fix","location":"PROJECT_STATUS.md:136,193; docs/decision_log.md:8764-8782","text":"Opus S4 remains: the advisor page says site drift is recorded and points to DRIFT.md as front-facing drift, while D-136 and current process docs make it reference-only; three site sources changed and DRIFT.md did not.","cure":"Change only the two advisor-page descriptions to the D-136 reference-only/manual-dispatch posture; do not refresh, regenerate, or deploy the site."}
    ],
    "sensitive_inventory": [
      "D-138: all four estimator inputs are base-identical and match the issued acceptance pins; reduce.py remains 7b9c0d28...",
      "Detection floor: the new nine-metric/four-scope registry is bound by JSON, sidecar, and source pin fc91df6d...; no floor value changed.",
      "D-166: three active generator sources refactor through the shared core/roster guard; 352 non-self-bound generated files match main and no dominance registration changed.",
      "Historical P2-015: campaign specification refactor regenerates all 282 frozen configs byte-identically; sizing output is diagnostic and the mission is retired.",
      "R7: producer digest is reviewed and repinned to 12d0293b...; issued values/statuses are unchanged.",
      "Fill/RQ surfaces: DG-072 wording, DS-32/PG-08 placements, and OB-01/TR-01/OR-01 retain STOP_FILL; the capstone-disposition table expressly changes neither canonical status nor claim ceiling.",
      "Frozen/process: analysis_manifest.py and draft-v1 are base-identical; D-172 is indexed 1:1 after its cold gate; D-173 is PROVISIONAL and requires a paper-supply cold gate before any supplier merge."
    ]
  },
  "verification": [
    {"id":"V1","kind":"test","cmd":"env PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_modularity.ClosedSetRegistryTests.test_analysis_condition_pairs_are_validated_as_registry_declarations tests.test_modularity.ClosedSetRegistryTests.test_frozen_ap2_row_requires_all_pairs_from_its_four_profiles","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["Ran 2 tests in 0.001s","FAILED (failures=2)"]},"expected":{"exit_code":0,"tail_regex":"Ran 2 tests.*OK"}},
    {"id":"V2","kind":"test","cmd":"env PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_modularity tests.test_campaign_generator_core tests.test_gamma_unit_roster_guard tests.test_detection_floor tests.test_floor_extraction tests.test_docs_freshness tests.test_capture_t0_step","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["FAIL: test_analysis_condition_pairs_are_validated_as_registry_declarations","FAIL: test_frozen_ap2_row_requires_all_pairs_from_its_four_profiles","Ran 407 tests in 44.663s","FAILED (failures=2, skipped=1)"]},"expected":{"exit_code":0,"tail_regex":"Ran 407 tests.*OK"}},
    {"id":"V3","kind":"test","cmd":"env PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_git_fixture_maintenance tests.test_arm_readiness_evidence_t0 tests.test_window_status_guard tests.test_arm_readiness_integration tests.test_paper_round7_artifacts tests.test_issue_dg071_dg075_statistics tests.test_analysis_finalizer tests.test_bridge","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 249 tests in 1209.358s","OK (skipped=1)"]},"expected":{"exit_code":0,"tail_regex":"Ran 249 tests.*OK"}},
    {"id":"V4","kind":"inspection","cmd":"set -e; branches='CUSTODY-HARDEN-01 FLOOR-WORKLOAD-SIZING-01 MODULARITY-01 PREWINDOW-V5-PIN-01 R7F-EXIT3-SEMANTICS-01 aud-wo-rows doc008 FIXTURE-MODERNIZATION-01 LINE-AUDIT-GUARD-01 rq-refresh GENERATOR-CORE-01 C3-RECOGNIZER-EXACT-01 PHASE-SHARE-ESTIMAND-01 docs-vs-truth GAMMA-UNIT-ROSTER-GUARD-01 one-name-sweep p1-rows COLDGATE-HANDOFF-01 GIT-FIXTURE-MAINTENANCE-SWEEP-01'; n=0; for b in $=branches; do git merge-base --is-ancestor \"origin/feat/2026-09-04-fan-$b\" HEAD; n=$((n+1)); done; printf 'landing_count=%s\\n' \"$n\"","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["landing_count=19"]},"expected":{"exit_code":0,"tail_regex":"landing_count=19"}},
    {"id":"V5","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_campaign_generator_core_parity.py --baseline-ref origin/main","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["PARITY_DIFF_EMPTY generator=GAMMA files=112","PARITY_OK generators=3 files=352 excluded=['generate_configs.py', 'plan_tree.json', 'plan_tree.sha256'] baseline=origin/main"]},"expected":{"exit_code":0,"tail_regex":"PARITY_OK generators=3 files=352.*baseline=origin/main"}},
    {"id":"V6","kind":"inspection","cmd":"rg -n 'repository is authoritative; drift is recorded|Front-facing drift: `docs/site/DRIFT.md`' PROJECT_STATUS.md; test -z \"$(git diff --name-only origin/int/2026-09-04-fan-wave-1..HEAD -- docs/site)\"; test \"$(git diff --name-only origin/int/2026-09-04-fan-wave-1..HEAD -- docs/site_src | wc -l | tr -d ' ')\" = 3; echo site_policy_mismatch=reproduced","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["site_policy_mismatch=reproduced"]},"expected":{"exit_code":0,"tail_regex":"site_policy_mismatch=reproduced"}},
    {"id":"V7","kind":"test","cmd":"set -e; PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_docs_freshness; PYTHONDONTWRITEBYTECODE=1 python3 scripts/gen_state.py --check","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 31 tests in 0.878s","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 31 tests.*OK"}}
  ],
  "flags": [
    {"id":"G1","kind":"verification_gap","level":"nonblocking","text":"Fifteen of 51 changed test modules were run; the preflight forbids this seat from running the whole suite.","needs":"Magistrate reruns the whole suite after R5-F1 is cured."},
    {"id":"G2","kind":"residual_risk","level":"nonblocking","text":"No live launcher, hardware, retained-corpus campaign, or quiet-machine measurement ran.","needs":"Existing Ed/lead-owned gates remain controlling."}
  ]
}
```

## Findings

R5-F1 — blocker. `c69cac3d` restored the pinned v1 validator and frozen draft to the exact wave-1 blobs, as required. It did not reconcile MODULARITY's tests: one now expects an arbitrary two-pair registry to pass; the other expects a dynamic selection-scope error instead of the frozen validator's earlier six-pair refusal. Keep production frozen and repair the stale tests.

R5-F2 — should-fix. Align the two `PROJECT_STATUS.md` site descriptions with D-136. This is a prose correction only; refreshing `DRIFT.md` or any site output would violate the intended cure.

Claim-bearing inventory: D-138's four source pins and every calibration artifact are unchanged. The `fc91df6d…` detection registry moves the same nine pairs/four scopes into authenticated data. The D-166 core refactor preserves 352 generated bytes; P2-015 preserves 282 configs. R7's sole digest change is paired with its reviewed repin. Fill rows remain stopped/value-unissued, RQ disposition is planning-only, and no floor literal, dominance registration, or frozen v1 byte moved. CUSTODY tightens NEG-8 ingress; its shared fixture now binds the registered corpus. D-172 was cold-gated; D-173 is explicitly provisional and fenced before supplier landing.

## Residual risk

The full suite and all live/quiet-machine gates remain magistrate or lead owned. The 249-test replay clears the prior residual T0/window-status failures on a quiescent tree; the only observed red is R5-F1.
