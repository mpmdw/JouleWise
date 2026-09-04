```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "The instrument path and digest checks are implemented, but the governed estimator edit requires a successor issued acceptance artifact outside the write scope.",
  "workspace": {"base_requested":"849915bc1393a6c1cb962a4dc12b25c33dad1f74","base_mode":"exact","head_start":"849915bc1393a6c1cb962a4dc12b25c33dad1f74","head_end":"849915bc1393a6c1cb962a4dc12b25c33dad1f74","upstream_end":"849915bc1393a6c1cb962a4dc12b25c33dad1f74","branch":"feat/2026-09-04-instrument-path-pin"},
  "pathspec": ["docs/process_traces/2026-09-04-fanout/instrument-path-pin/01-sol-report.md","joulewise/calibration_bracketing.py","joulewise/controller.py","joulewise/powermetrics_fiducial.py","scripts/validate_powermetrics_fiducial.py","tests/test_calibration_bracketing.py","tests/test_p2038_production_path.py","tests/test_powermetrics_fiducial.py"],
  "unowned_dirty": [],
  "verdict": {"implementation":"partial","acceptance":"pending_verification"},
  "verification": [
    {"id":"V1","kind":"test","cmd":"git diff --check && python3 -m unittest tests.test_powermetrics_fiducial tests.test_calibration_bracketing tests.test_p2038_production_path","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["Ran 134 tests in 506.077s","FAILED (failures=2, errors=1, skipped=1)"]},"expected":{"exit_code":0,"tail_regex":"^OK$"}},
    {"id":"V2","kind":"test","cmd":"python3 -m unittest tests.test_powermetrics_fiducial.EvidenceTests.test_digest_pinned_evidence_records_resolved_invoked_binary tests.test_powermetrics_fiducial.EvidenceTests.test_digest_pin_mismatch_refuses_with_named_code tests.test_powermetrics_fiducial.EvidenceTests.test_healthy_evidence_bytes_match_pre_budget_baseline tests.test_powermetrics_fiducial.WriterLedgerIntegrationTests.test_main_preserves_symlinked_custody_spelling_used_by_reservation tests.test_calibration_bracketing.BracketTests.test_candidate_admission_requires_active_v3_method tests.test_p2038_production_path.P2038ProductionPathTests.test_window_prepare_refuses_unregistered_instrument_digest_pin","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["Ran 6 tests in 11.790s","FAILED (errors=1)","AttributeError: module 'tests.test_calibration_bracketing' has no attribute 'BracketTests'"]},"expected":{"exit_code":0,"tail_regex":"^OK$"}},
    {"id":"V3","kind":"test","cmd":"python3 -m unittest tests.test_calibration_bracketing.CalibrationBracketingTests.test_candidate_admission_requires_active_v3_method","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 1 test in 0.007s","OK"]},"expected":{"exit_code":0,"tail_regex":"^OK$"}},
    {"id":"V4","kind":"test","cmd":"python3 -m unittest tests.test_powermetrics_fiducial.EvidenceTests.test_digest_pinned_evidence_records_resolved_invoked_binary tests.test_powermetrics_fiducial.EvidenceTests.test_digest_pin_mismatch_refuses_with_named_code tests.test_powermetrics_fiducial.EvidenceTests.test_healthy_evidence_bytes_match_pre_budget_baseline tests.test_powermetrics_fiducial.WriterLedgerIntegrationTests.test_main_preserves_symlinked_custody_spelling_used_by_reservation tests.test_calibration_bracketing.CalibrationBracketingTests.test_candidate_admission_requires_active_v3_method tests.test_p2038_production_path.P2038ProductionPathTests.test_window_prepare_refuses_unregistered_instrument_digest_pin","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 6 tests in 11.532s","OK"]},"expected":{"exit_code":0,"tail_regex":"^OK$"}},
    {"id":"V5","kind":"inspection","cmd":"shasum -a 256 /usr/bin/powermetrics && sw_vers -buildVersion","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["b762e5bf7628e77d279012882c096e922633a47aa38bd5f05c0381cfb21330c5  /usr/bin/powermetrics","25G83"]},"expected":{"exit_code":0,"tail_regex":"^25G83$"}},
    {"id":"V6","kind":"lint","cmd":"git diff --check && python3 -m py_compile joulewise/powermetrics_fiducial.py joulewise/calibration_bracketing.py joulewise/controller.py scripts/validate_powermetrics_fiducial.py tests/test_powermetrics_fiducial.py tests/test_calibration_bracketing.py tests/test_p2038_production_path.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[]},"expected":{"exit_code":0,"tail_regex":"^$"}}
  ],
  "flags": [
    {"id":"F1","kind":"scope_deviation","level":"blocking","text":"The edited estimator module no longer matches the digest in the active issued calibration-acceptance artifact, so the focused suite correctly reports that artifact as stale.","needs":"Authorize the successor acceptance artifact path so its estimator digest, derivation digest, and exact-byte registry pin can be issued together."},
    {"id":"F2","kind":"verification_gap","level":"nonblocking","text":"The first focused run also found two local test adaptations; both were corrected and pass in V2.","needs":""}
  ],
  "scope_expansion": {"requested_paths":["configs/calibration/calibration_acceptance_d079_v2_n17_r7.json"],"reason":"The active issued artifact authenticates the exact bytes of the edited estimator module; append-only issuance requires a successor artifact rather than changing the retained generation.","blocked_work":"Register the successor as active and rerun the three focused modules to a clean result.","minimal_change":"Add one successor artifact that preserves the accepted corpus and scientific values while rotating the governed estimator digest and its derived exact-byte hashes."}
}
```

## Change

The calibration writer now resolves the sampler executable before invocation and records that same path in the instrument artifact. SHA-256, a cryptographic digest used to identify exact file bytes, is recorded as both the observed value and the independently expected value selected by an append-only acceptance registry. An acceptance registry is reviewed code that maps a stable identifier to one expected digest without rewriting earlier entries.

New artifacts fail with `instrument_binary_digest_mismatch` when the observed digest, expected digest, or registry identifier disagrees. Calibration candidate admission and window preparation repeat the registry comparison. Historical artifacts remain readable because the new comparison applies only when the artifact carries the acceptance identifier.

| Finding | Executed evidence | Decision |
|---|---|---|
| The recorded path could differ from the invoked path. | The focused path regression passed in V4. | Resolve once, invoke the resolved path, and serialize the same value. |
| Digest equality was previously circular. | The mismatch regressions for artifact creation, candidate admission, and window preparation passed in V4. | Select the expected digest from reviewed code and reject disagreement by name. |
| The estimator source is governed by an issued artifact. | V1 reports the prior estimator digest and the newly observed estimator digest as unequal. | Preserve the prior issuance and request one successor artifact. |

### First-use test

This table applies a mechanical first-use check to each changed explanatory sentence in the implementation and this report. A sentence passes when every specialist term is either ordinary language, code syntax, a file name, or defined in that sentence or an earlier sentence.

| Sentence group | First specialist term | Definition available at first use | Result |
|---|---|---|---|
| Registry implementation comments | acceptance registry | The comment states that rows are reviewed, appended, and never repointed. | pass |
| Digest validation function | historical artifact | The function text distinguishes an artifact without the new identifier from a newly pinned artifact. | pass |
| Calibration command refusal | digest mismatch | The emitted fields name the observed and expected SHA-256 values. | pass |
| Window preparation check | window preparation | The surrounding function states that validation occurs before bundle creation. | pass |
| Test names and assertions | resolved invoked binary | The test constructs one resolved path and compares the recorded value directly. | pass |
| Report paragraph one | SHA-256 | The sentence defines it as a cryptographic digest for exact file bytes. | pass |
| Report paragraph one | acceptance registry | The next sentence defines the mapping and append-only rule. | pass |
| Report paragraph two | calibration candidate admission | The preceding change description establishes the calibration artifact being admitted. | pass |
| Finding table | circular digest equality | The decision states that the expected digest comes from reviewed code rather than the observed artifact. | pass |
| Verification notes | issued acceptance artifact | The change section defines the artifact and registry relationship before this use. | pass |

## Verification notes

V1 ran only the three touched test modules. It found the expected governed-source failure plus two test adaptations. V2 records an incorrect class selector, V3 corrects that selector, and V4 confirms the implementation-specific behavior and both adaptations are clean.

## Residual risk

The active issued acceptance artifact still names the estimator bytes from before this edit. Until the requested successor is issued and registered, production calibration preflight remains fail-closed and the complete focused module run remains red.
