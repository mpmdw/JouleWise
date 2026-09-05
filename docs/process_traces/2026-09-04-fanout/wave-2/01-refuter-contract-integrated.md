```json
{
  "verdict": {
    "gauntlet": "NOT LANDABLE",
    "findings": [
      {"id":"F1","severity":"blocker","location":"origin/.../fan-wave-1:wave-1/04-delta-reaudit-round-1.md","text":"The requested Wave-1 ref is not an ancestor of HEAD. Its omitted terminal audit says NOT LANDABLE on unresolved same-signature DR1-F1, and the exact diff shows that audit deleted.","counterfactual":"Integrate a cleared Wave-1 tip; the ancestor check must return 0 and the audit must not be deleted."},
      {"id":"F2","severity":"blocker","location":"joulewise/reduce.py; decision_log.md:10063; calibration_acceptance_d079_v2_n17_r6.json:43","text":"CUSTODY changes the D-138-pinned reduce.py from 7b9c0d28... to 66a6ebff... without the atomic successor re-freeze or dependent-pin reissue. D-161 does not waive physics/evidence pins.","counterfactual":"The production estimator-closure comparison is false at HEAD and was true before CUSTODY."},
      {"id":"F3","severity":"blocker","location":"tests/test_arm_readiness_evidence_author.py:121; joulewise/detection_floor.py:42","text":"MODULARITY makes the frozen detection registry mandatory, but FIXTURE-MODERNIZATION's portable repo copies its Python consumer without the registry JSON/sidecar.","counterfactual":"The embedded suite errors 3/3 on the missing JSON and passes 3/3 after both files are added to the temporary fixture."},
      {"id":"F4","severity":"should_fix","location":"state_kernel.json:3986; TASK_QUEUE.md:711,856","text":"PREWINDOW's authority says occupied live roots pass and stale roots refuse; its executed test proves the reverse."},
      {"id":"F5","severity":"should_fix","location":"tests/test_paper_round7_artifacts.py:818-869","text":"The R7 regression compares lexical /var with canonical /private/var. It fails under ambient macOS TMPDIR and passes only with TMPDIR=/private/tmp."},
      {"id":"F6","severity":"nit","location":"scripts/prewindow_check.sh:51","text":"The live-family comment cites estimator re-freeze decision D-138; PREWINDOW's authority is unattended R-12."}
    ]
  },
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "NOT LANDABLE: unresolved Wave-1 ancestry, a D-138 fence violation, and a broken portable fixture are blockers; PREWINDOW and R7 add three lesser defects.",
  "workspace": {
    "base_requested": "3ad90a34c83c9283313f3d19baf80018a4e3630c",
    "base_mode": "exact",
    "head_start": "99c80bcafd9f6c6b862250cb5b12856c16898d5a",
    "head_end": "99c80bcafd9f6c6b862250cb5b12856c16898d5a",
    "upstream_end": "99c80bcafd9f6c6b862250cb5b12856c16898d5a",
    "branch": "int/2026-09-04-fan-wave-2"
  },
  "pathspec": ["docs/process_traces/2026-09-04-fanout/wave-2/01-refuter-contract-integrated.md"],
  "unowned_dirty": [],
  "verification": [
    {"id":"V1","kind":"inspection","cmd":"git merge-base --is-ancestor origin/int/2026-09-04-fan-wave-1 HEAD; rc=$?; git diff --name-status origin/int/2026-09-04-fan-wave-1..HEAD -- docs/process_traces/2026-09-04-fanout/wave-1/04-delta-reaudit-round-1.md; exit $rc","observed":{"result":"fail","exit_code":1,"tail":["D wave-1/04-delta-reaudit-round-1.md"]}},
    {"id":"V2","kind":"inspection","cmd":"python3 -c 'from joulewise import calibration_bracketing as c; a=c.load_calibration_acceptance_bound(); o=c._current_estimator_code_sha256(); e=a[\"prospective_rederivation\"][\"estimator_code_sha256\"]; print(e[\"joulewise/reduce.py\"],o[\"joulewise/reduce.py\"],o==e); raise SystemExit(o!=e)'","observed":{"result":"fail","exit_code":1,"tail":["expected reduce=7b9c0d28...","observed reduce=66a6ebff...","matches=false"]}},
    {"id":"V3","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_arm_readiness_dry_run tests.test_arm_readiness_evidence_t0 tests.test_arm_readiness_integration tests.test_arm_readiness_lifecycle tests.test_s0_blocked_enumeration","observed":{"result":"fail","exit_code":1,"tail":["Ran 154 tests in 784.106s","FAILED (errors=1, skipped=2)","MINT_TRUST errors=3"]}},
    {"id":"V4","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_bridge tests.test_campaign_generator_core tests.test_detection_floor tests.test_docs_freshness tests.test_floor_extraction tests.test_modularity tests.test_rpt001_report_slice tests.test_s0_line_audit_guard tests.test_workload_sizing","observed":{"result":"pass","exit_code":0,"tail":["Ran 473 tests in 87.886s","OK (skipped=4)"]}},
    {"id":"V5","kind":"test","cmd":"python3 -m unittest tests.test_reduce tests.test_run_campaign tests.test_capture_t0_step tests.test_paper_round7_artifacts","observed":{"result":"fail","exit_code":1,"tail":["Ran 494 tests in 1345.629s","FAILED (failures=1)","/private/var != /var"]}},
    {"id":"V6","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 docs/paper/fill-rehearsal/test_select_outcome_branches.py; PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_campaign_generator_core_parity.py --baseline-ref origin/main","observed":{"result":"pass","exit_code":0,"tail":["Ran 2 tests; OK","PARITY_OK generators=3 files=352"]}},
    {"id":"V7","kind":"test","cmd":"python3 -m unittest tests.test_capture_t0_step.CaptureT0StepTests.test_prewindow_runs_prefixes_accept_live_family_and_refuse_stale_family; rg -n 'D-138' scripts/prewindow_check.sh; rg -n 'R-12.*prewindow_check' docs/process_traces/2026-09-01-unattended/MAGISTRATE-RULING-UNATTENDED-STAGE1.md","observed":{"result":"pass","exit_code":0,"tail":["Ran 1 test in 1.196s","OK","D-138 source comment; R-12 authority"]}}
  ]
}
```

## Findings

F1-F3 are independent blockers: Wave 1 still needs DR1-F1 adjudication; CUSTODY must leave this wave for the D-138 atomic re-freeze; and the portable fixture must copy MODULARITY's registry pair. Adding that pair kills its three missing-file errors, after which twelve D-138 failures independently confirm F2.

F4-F6: correct PREWINDOW's reversed kernel/queue wording, normalize R7's expected path rather than forcing TMPDIR, and replace PREWINDOW's D-138 comment with R-12.

### Landing/ruling and claim-bearing inventory

| landing | contract/fence result |
|---|---|
| CUSTODY-HARDEN-01 | Completed-row scope matches (NEG-8 corpus admission and claim/mint barriers); F2 blocks its `reduce.py` bytes. |
| FLOOR-WORKLOAD-SIZING-01 | Matches RETIRE: archival record; helper is reporting, not authority. |
| MODULARITY-01 | P3-after-paper order matches. New frozen registry `fc91df6d...` has equal file/sidecar/hard pins; historical spec moves no issued floor literal. F3 remains. |
| PREWINDOW-V5-PIN-01 | R-12 `_v5` identifiers landed with no gate-semantic change; F4/F6 remain. |
| R7F-EXIT3-SEMANTICS-01 | Option A landed. XS repin `12d0293b...` matches; values/status/census unchanged. Sole main/landing path overlap was its registry; F5 remains. |
| aud-wo-rows | Bridge contract/checks only; no claim/digest change. |
| doc008 | Ruled root scope landed; status prose still says no `_v5` data. Magistrate semantic sign-off remains the terminal action. |
| FIXTURE-MODERNIZATION-01 | Test-only; F3 is the MODULARITY composition miss. |
| LINE-AUDIT-GUARD-01 | Ten historical-extract digests; process custody, not science. |
| rq-refresh | Planning join only; canonical status/claim-ceiling table bytes unchanged; four §3 characterizations remain uncollected/outside `_v5`. |
| GENERATOR-CORE-01 | Correctly last and D-161-scoped. All 352 non-self-bound files match main; only source/self-bound plan-tree identities rotate. |

No name deviations were found. No two Wave-2 merges directly touch one path; R7's registry is the sole main overlap. Next: clear/integrate Wave 1; rebuild without CUSTODY; cure F3-F6; rerun these modules; then magistrate runs the whole suite.

## Residual risk

No full suite, live hardware, or `[QUIET-MAC]` work ran. Real G2-a/desk-day packs remain future gates; parity used synthetic issued-shaped pins.
