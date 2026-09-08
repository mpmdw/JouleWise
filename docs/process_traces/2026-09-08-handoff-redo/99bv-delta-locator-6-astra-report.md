```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Candidate propagation and entry guards hold; simple replay-forwarding shapes still evade the census.",
  "workspace": {
    "base_requested": "96bfb448",
    "base_mode": "exact",
    "head_start": "b598113e5c785b051738b52164b5328f90a0da27",
    "head_end": "b598113e5c785b051738b52164b5328f90a0da27",
    "upstream_end": null,
    "branch": "fix/2026-09-08-icloud-custody-locator"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {"id":"F1","severity":"should_fix","title":"Renamed parameters and omitted replay defaults escape the rewritten census"}
    ],
    "census": {
      "detected": ["local literal","assignment alias","callable assignment alias","factory kwargs: violation","forwarded kwargs: violation","second allowlisted-function call","shared(mode) called with replay","positional mode"],
      "new_shapes_undetected": ["shared(resolution) forwards mode=resolution","shared(mode='read_replay') called without arguments","callbacks=[loader]; callbacks[0](mode='read_replay')"],
      "check": "Shipped counterfactual tests passed. Independently executed all three new shapes: each supplied read_replay; inventory returned no violations or new replay keys. Runtime helper-populated dictionary also escaped."
    },
    "allowlist": {
      "check": "Executed all 14 shipped mode expressions and independently traced callers. L=joulewise/calibration_ledger.py; C=scripts/run_campaign.py. Numbers follow fixture order.",
      "rows": [
        "1 joulewise/analysis_engine/__init__.py:1685: CLI dispatch -> analyze_claims -> inputs; replay derivation.",
        "2 L:4974: recovery readiness -> snapshot; enforcing reservation/capture callers select issuing.",
        "3 L:5029: same readiness chain -> slot state; executed replay/issuing alternatives.",
        "4 L:4857: status snapshot custody-inert; recovery abort guarded; reservation qualification below.",
        "5 L:4891: status slot replay; recovery abort guarded; reservation qualification below.",
        "6 L:5248: recovery resume-finalize; guard :5240 precedes snapshot, issuing state check :5276 precedes finalization.",
        "7 joulewise/window_duration_margins.py:713: recorder CLI -> record -> derive -> authenticate; replay-only derivation.",
        "8 scripts/check_window_provenance.py:860: main -> assertions -> check_f52 -> existing-verdict session.",
        "9 scripts/extract_detection_floors.py:140: main -> extract_cells -> session; report derivation. Executed CLI call supplies replay.",
        "10 scripts/recover_calibration_ledger.py:233: audit branch; returns without issuance.",
        "11 scripts/recover_calibration_ledger.py:265: audit-observations branch; returns without issuance.",
        "12 C:5248: whole-window and AXI post-run evaluation branches; replay.",
        "13 C:4830: snapshot loader called by those two evaluation branches; replay.",
        "14 C:6240: retained whole-window evaluation -> session; replay."
      ],
      "qualification": "No literal reason-text overclaim established. Rows 4/5 are not universally replay-only or entry-guarded: reserve_calibration_window_bracket.py:174 status can fall through to :202 append. Executed that AST branch under an override; status output is ignored."
    },
    "candidate_discovery": "Executed shipped regression using an in-memory filesystem: default/explicit issuing returned no candidates throughout calibration_bracketing.py:1081/:1237/:1309/:2018 via whole_window.py:697; replay inspected replacement. Forcing replay at the session-to-bracket edge caused two assertion failures.",
    "abort": "Executed abort_calibration_session with lease/status sentinels: :5400 refuses before both. Public abort_bracket_session:4501 skips it and reaches _locked_append:4556; executed interception confirmed no guard or replay-status call. This existing route does not establish replacement-byte issuance.",
    "campaign": "Executed main dispatch and ordinary wrapper interception. Inspected main:8956 -> whole-window:6173 -> evaluation:6283, and main:8957 -> run_campaign:8134 -> AXI evaluation:7909. Both set whole_window=True; neither evaluation chain reaches the four issuing categories. Ordinary :8868 leaves wrapper/default :5288/:5000 False.",
    "runtime_coverage": "All four named issuing entries refused before input sentinels. No, every undetectable shape is not individually pinned: tests/test_calibration_ledger_custody.py:620 covers helper-populated kwargs followed by single-floor mint only.",
    "new_functional_defects": "None established beyond the census enforcement defect."
  },
  "verification": [
    {
      "id":"V1",
      "kind":"test",
      "cmd":"python3 -B -m unittest tests.test_custody_mode_inventory tests.test_whole_window.CandidateDiscoveryModeTests",
      "cwd":".",
      "observed":{"result":"fail","exit_code":1,"tail":["FAILED (errors=1)"]},
      "expected":{"exit_code":0,"tail_regex":"OK"}
    },
    {
      "id":"V2",
      "kind":"test",
      "cmd":"python3 -B -m unittest tests.test_calibration_ledger_custody.CustodyProbeTests.test_issuance_refuses_override_before_input_access tests.test_calibration_ledger_custody.CustodyProbeTests.test_readiness_forwards_resolution_mode_to_snapshot_and_state tests.test_calibration_ledger_custody.CustodyProbeTests.test_head_pin_advancement_forwards_issuing_mode tests.test_calibration_ledger_custody.CustodyProbeTests.test_unknown_resolution_mode_refuses_before_probe tests.test_calibration_ledger_custody.IssuingBoundaryTests.test_signature_defaults_are_issuing tests.test_calibration_ledger_custody.IssuingBoundaryTests.test_empty_override_diagnostic_is_one_line_only_for_issuing_shortcut",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["OK"]},
      "expected":{"exit_code":0,"tail_regex":"OK"}
    }
  ],
  "flags": [
    {
      "id":"E1",
      "kind":"environment",
      "level":"nonblocking",
      "text":"Read-only sandbox prevents temporary-file fixtures. V1's six inventory tests passed; candidate fixture setup failed. In-memory candidate regression passed.",
      "needs":"Lead rerun physical candidate, planted-custody, extraction, and campaign regressions."
    }
  ]
}
```

## Findings

**F1 — should_fix.** `tests/test_custody_mode_inventory.py:168` recognizes wrappers only through a parameter literally named `mode` or `**kwargs`, while `:99` exempts any scalar parameter. Consequently, `shared(resolution)` can forward replay invisibly. At `:189`, only supplied arguments are inspected; `shared(mode="read_replay"); shared()` also escapes. Both executed counterexamples returned replay without requiring an allowlist edit.

Track parameters actually forwarded into custody mode and resolve omitted defaults. Add discriminating regressions. Callable-container dispatch is an additional demonstrated limitation within the documented arbitrary-dataflow caveat.

## Residual risk

Physical planted-file regressions remain unverified here; filesystem simulation proves forwarding and assertion sensitivity, not real-file authentication. The public abort and reservation qualifications prevent a blanket “every append is guarded” conclusion. No edits occurred; HEAD remained unchanged.