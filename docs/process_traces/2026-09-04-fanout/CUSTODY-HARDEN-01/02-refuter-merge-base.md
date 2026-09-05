```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "CUSTODY-HARDEN-01 is NOT LANDABLE: focused tests pass, but arbitrary sibling JSON can authenticate a forged corpus and required production-site counterfactual coverage is incomplete.",
  "workspace": {"base_requested":"fa0944575534fb66c7366e7906c22f9ce0a2c894","base_mode":"exact","head_start":"fa0944575534fb66c7366e7906c22f9ce0a2c894","head_end":"fa0944575534fb66c7366e7906c22f9ce0a2c894","upstream_end":null,"branch":"feat/2026-09-04-fan-CUSTODY-HARDEN-01"},
  "pathspec": ["docs/process_traces/2026-09-04-fanout/CUSTODY-HARDEN-01/02-refuter-merge-base.md"],
  "unowned_dirty": [],
  "verdict": {
    "gauntlet": "NOT LANDABLE",
    "findings": [
      {"id":"F1","severity":"blocker","location":"joulewise/whole_window.py:1607","text":"The registry globs every sibling *.json, so an untracked manifest can authenticate a forged artifact instead of the one governed settled_corpus.json.","counterfactual":"Redirect the registry directory to a temporary directory containing only a forged matching untracked.json; authenticated validation returns True."},
      {"id":"F2","severity":"blocker","location":"joulewise/whole_window.py:3708; joulewise/whole_window.py:5439; tests/test_run_campaign.py:7583","text":"Mint-time and claim-row identity enforcement lack required biting, per-site counterfactuals.","counterfactual":"Without the mint postcondition, the real CLI regression still passes; without claim-row require_corpus_identity=True, the direct-validator/loader test is unaffected because it never calls _validate_row."},
      {"id":"F3","severity":"blocker","location":"docs/process_traces/2026-09-04-fanout/CUSTODY-HARDEN-01/01-sol-report.md:105","text":"The dated custodied implementation report lacks the mandatory ## Clause map required by bridge-protocol/v1.1.","counterfactual":"rg for the exact heading exits 1 with no match."}
    ]
  },
  "verification": [
    {"id":"V1","kind":"inspection","cmd":"git diff --name-only $(git merge-base origin/main HEAD)..HEAD | LC_ALL=C sort","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["docs/contracts/adapter_contracts.md","docs/process_traces/2026-09-04-fanout/CUSTODY-HARDEN-01/01-sol-report.md","joulewise/analysis_engine/inputs.py","joulewise/reduce.py","joulewise/whole_window.py","tests/test_reduce.py","tests/test_run_campaign.py"]},"expected":{"exit_code":0,"tail_regex":"docs/contracts/adapter_contracts.md[\\s\\S]*tests/test_run_campaign.py"}},
    {"id":"V2","kind":"inspection","cmd":"git diff --quiet $(git merge-base origin/main HEAD)..HEAD -- RUN_STATE.md TASK_QUEUE.md docs/process/state_kernel.json docs/decision_log.md","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[]},"expected":{"exit_code":0,"tail_regex":"^$"}},
    {"id":"V3","kind":"test","cmd":"python3 -m unittest tests.test_reduce.D078R01RegressionTests.test_metadata_mock_label_cannot_bypass_current_environment_barrier tests.test_reduce.D078R01RegressionTests.test_metadata_mock_label_cannot_bypass_cpu_admission_barrier tests.test_reduce.D078R01RegressionTests.test_environment_claim_reason_channel_is_closed_and_decision_bound tests.test_reduce.D078R01RegressionTests.test_cpu_admission_ledger_shape_and_top_decision_are_fail_closed tests.test_run_campaign.IdleAdmissionCoreVerdictTests.test_drift_bound_corpus_identity_requires_external_bytes tests.test_run_campaign.IdleAdmissionCoreVerdictTests.test_drift_bound_accepts_exact_custodied_manifest_bytes tests.test_run_campaign.IdleAdmissionCoreVerdictTests.test_unissued_prefreshness_bound_wire_is_malformed_and_underived tests.test_run_campaign.IdleAdmissionCoreVerdictTests.test_governed_neg8_bound_derivation_cli_writes_sealed_artifact tests.test_run_campaign.IdleAdmissionCoreVerdictTests.test_neg8_reference_campaign_corpus_is_accepted_by_derivation_cli","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 9 tests in 0.052s","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 9 tests in .*s[\\s\\S]*OK"}},
    {"id":"V4","kind":"suite","cmd":"python3 -m unittest tests.test_run_campaign","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 272 tests in 265.308s","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 272 tests in .*s[\\s\\S]*OK"}},
    {"id":"V5","kind":"suite","cmd":"python3 -m unittest tests.test_reduce tests.test_whole_window tests.test_whole_window_selection","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 246 tests in 553.480s","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 246 tests in .*s[\\s\\S]*OK"}},
    {"id":"V6","kind":"lint","cmd":"python3 -m py_compile joulewise/reduce.py joulewise/whole_window.py joulewise/analysis_engine/inputs.py && git diff --check","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[]},"expected":{"exit_code":0,"tail_regex":"^$"}},
    {"id":"V7","kind":"other","cmd":"cd /private/tmp/jw-custody-base.H6w7gM && python3 -m unittest tests.test_reduce.D078R01RegressionTests.test_metadata_mock_label_cannot_bypass_current_environment_barrier tests.test_reduce.D078R01RegressionTests.test_metadata_mock_label_cannot_bypass_cpu_admission_barrier tests.test_run_campaign.IdleAdmissionCoreVerdictTests.test_drift_bound_corpus_identity_requires_external_bytes tests.test_run_campaign.IdleAdmissionCoreVerdictTests.test_drift_bound_accepts_exact_custodied_manifest_bytes tests.test_run_campaign.IdleAdmissionCoreVerdictTests.test_unissued_prefreshness_bound_wire_is_malformed_and_underived","cwd":".","observed":{"result":"pass","exit_code":1,"tail":["Ran 5 tests in 0.005s","FAILED (failures=3, errors=2)"]},"expected":{"exit_code":1,"tail_regex":"FAILED \\(failures=3, errors=2\\)"}},
    {"id":"V8","kind":"other","cmd":"cd /private/tmp/jw-custody-base.H6w7gM && python3 -m unittest tests.test_run_campaign.IdleAdmissionCoreVerdictTests.test_neg8_reference_campaign_corpus_is_accepted_by_derivation_cli","cwd":".","observed":{"result":"fail","exit_code":0,"tail":["Ran 1 test in 0.026s","OK"]},"expected":{"exit_code":1,"tail_regex":"FAILED"}},
    {"id":"V9","kind":"other","cmd":"python3 -c \"import hashlib,json,tempfile;from pathlib import Path;from tests.test_run_campaign import IdleAdmissionCoreVerdictTests as T;import joulewise.whole_window as w;t=T('test_drift_bound_corpus_identity_requires_external_bytes');t.setUp();s=t._drift_bound();m=s['reference_corpus']['members'];r=(json.dumps({'schema_version':w.NEG8_REFERENCE_CORPUS_SCHEMA,'corpus_id':'x','freeze_status':'settled_reference','condition_id':'x','members':[{'bundle_id':v['bundle_id'],'bundle_path':'x'} for v in m]},sort_keys=True)+'\\\\n').encode();f=s['freshness'];a=w.build_neg8_drift_bound_artifact(corpus_id='x',condition_id='x',manifest_sha256=hashlib.sha256(r).hexdigest(),scientific_config_sha256='b'*64,members=m,derivation_timestamp_s=f['derived_at_s'],freshness_bindings=f['bindings']);d=tempfile.TemporaryDirectory();Path(d.name,'untracked.json').write_bytes(r);w.REGISTERED_NEG8_REFERENCE_CORPUS_DIR=Path(d.name);z=w.validate_neg8_drift_bound_artifact(a,require_corpus_identity=True);print('untracked_manifest_accepted='+str(z));raise SystemExit(z)\"","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["untracked_manifest_accepted=True"]},"expected":{"exit_code":0,"tail_regex":"untracked_manifest_accepted=False"}},
    {"id":"V10","kind":"inspection","cmd":"rg -n '^## Clause map$' docs/process_traces/2026-09-04-fanout/CUSTODY-HARDEN-01/01-sol-report.md","cwd":".","observed":{"result":"fail","exit_code":1,"tail":[]},"expected":{"exit_code":0,"tail_regex":"Clause map"}}
  ],
  "flags": []
}
```

## Findings

### F1 — blocker — arbitrary sibling JSON is treated as repository registration

`_neg8_corpus_identity_is_authenticated` scans every `*.json` under the derivation directory instead of resolving the one governed path named by the contract, `configs/campaigns/neg8_reference_corpus/derivation/settled_corpus.json`. The executed V9 reproducer built an internally valid attacker-chosen artifact plus matching manifest bytes, placed those bytes only in `untracked.json` in a temporary registry directory, and observed `untracked_manifest_accepted=True`. The checked-in directory is presently clean and contains only the governed file; the defect is the fail-open lookup rule, not current workspace contamination.

### F2 — blocker — two production identity checks lack biting counterfactuals

The merge-base counterfactual copy consisted of the exact merge-base tree plus only the landing's two changed test files. Four behavioral seams bite there: metadata `mock` suppresses the current environment barrier; metadata `mock` suppresses the CPU barrier; the external-identity API is absent; and a dual-family artifact with freshness removed and its seal recomputed is accepted. V7 therefore fails with three assertion failures and two API errors, as expected.

The mint-time postcondition is different. V8 runs the landing's real derivation-CLI regression on the merge-base implementation, where lines 3708-3711 do not exist, and it passes. The test patches `mint_neg8_drift_bound_artifact`, so it cannot exercise the new postcondition. Likewise, the direct validator/loader regression never constructs a claim row, so it does not bite removal of the separate claim-row enforcement at line 5441. These are distinct production sites under the clause-map rule and need distinct failing mutations.

### F3 — blocker — mandatory clause map absent

The implementation report is dated 2026-09-04 and is a custodied implementation report, but it has no `## Clause map`. V10 confirms the required heading is absent. Bridge protocol §1 requires one row per independently falsifiable production site, with the biting assertion and counterfactual; the missing rows are material because the report declares V1/V2/V3 collectively without exposing the two non-biting sites in F2.

## Evidence

HEAD was exactly `fa0944575534fb66c7366e7906c22f9ce0a2c894` on `feat/2026-09-04-fan-CUSTODY-HARDEN-01`. Review range was exactly `b0ed6991c11f3a515ad293760c6dfc031adda8e1..HEAD`, where the lower endpoint is `git merge-base origin/main HEAD`. Its seven paths exactly equal the implementation report's declared `WRITE_SCOPE`. `RUN_STATE.md`, `TASK_QUEUE.md`, `docs/process/state_kernel.json`, and `docs/decision_log.md` have no delta.

All claimed test and lint commands passed at the reviewed head. No repository-wide suite or quiet-machine measurement ran. The current code's counterfactual inputs and results are:

| Behavioral change | Counterfactual input | Reverted result |
|---|---|---|
| Environment barrier ignores diagnostic mockness | `adapters.telemetry.name=mock` plus an awake post-run display | New test fails: no refusal is emitted |
| CPU barrier ignores diagnostic mockness | `adapters.telemetry.name=mock` plus duplicated admission attempt rows | New test fails: gates remain eligible |
| External corpus identity | Self-sealed forged corpus without registered/custodied bytes; exact independently held manifest bytes for the positive arm | New tests error because the external-identity interface is absent |
| No-freshness wire removal | Dual-family artifact with `freshness` deleted and seal recomputed | New test fails: reverted validator accepts it |
| Mint-time source-byte postcondition | Tracked settled corpus through the real derivation CLI | **False counterfactual:** landing test still passes after reversion |
| Claim-row external-identity enforcement | Claim row carrying a structurally valid forged drift artifact | **Not executed by a new test:** direct validator/loader coverage does not enter `_validate_row` |

The earlier-round verdict file is not present in this directory, and the refreshed prompt identifies the prior blocker as range staleness only. Therefore there was no prior-round non-staleness blocker to re-test; no base-staleness finding is made here.

## Residual risk

The exact caller-custodied-manifest positive path is covered only at the validator API. No production caller currently threads such bytes into file ingress or claim-row validation; the implementation report explicitly chooses repository registration for those paths.
