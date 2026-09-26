```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "FIX-FIRST: cadence can treat charging captures as clean, and the dry run reads result evidence before an authentic verdict exists.",
  "workspace": {
    "base_requested": "c6814dd891db361156c45434490342a3e1dd9da3",
    "base_mode": "descendant",
    "head_start": "6b5efdc3c9c91459d3280f8b6c170107fcb5ece5",
    "head_end": "6b5efdc3c9c91459d3280f8b6c170107fcb5ece5",
    "upstream_end": "6b5efdc3c9c91459d3280f8b6c170107fcb5ece5",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "decision": "FIX-FIRST",
    "findings": [
      {"id": "F1", "severity": "blocker", "title": "Cadence capture paths are not bound to the session whose battery verdict is checked"},
      {"id": "F2", "severity": "blocker", "title": "The count-only check reads member evidence when the harvest verdict is absent"},
      {"id": "F3", "severity": "should_fix", "title": "The dry run calls an omitted non-pass window admissible"},
      {"id": "F4", "severity": "should_fix", "title": "Three consumers skip the verdict's preregistration digest check"},
      {"id": "F5", "severity": "should_fix", "title": "The writer-crash test survives removal of the post observation"},
      {"id": "F6", "severity": "nit", "title": "The liveness-test explanation still describes the old 600-second bound"},
      {"id": "F7", "severity": "nit", "title": "Four new ioreg fixtures fail git diff whitespace checks"}
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_battery_float tests.test_acc_25g83_rev5 tests.test_calibration_cadence_report tests.test_issue_calibration_acceptance_generation tests.test_validate_powermetrics_fiducial_derivation_only",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["AssertionError: None is not an instance of <class 'str'>", "Ran 205 tests in 324.538s", "FAILED (failures=1)"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_night_gate.NightGateTests.test_battery_float_charging_refuses_at_c3 tests.test_evidence_night.LifecycleTests.test_charging_fails_arm_check_for_unknown_and_calibration_payloads tests.test_evidence_night.LifecycleTests.test_charging_at_publication_preserves_plan_and_successor_claim tests.test_night_agent_install.EvidenceRenderOnlyTests.test_battery_not_at_float_refuses_install_validation_before_render tests.test_arm_readiness_evidence_t0.ArmReadinessEvidenceT0Tests.test_power_row_refuses_charging_and_stale_battery_and_records_float tests.test_arm_readiness_evidence_t0.ArmReadinessEvidenceT0Tests.test_issuance_t0_liveness_bound_passes_at_exactly_610s tests.test_arm_readiness_evidence_t0.ArmReadinessEvidenceT0Tests.test_t0_liveness_constant_is_derived_from_the_post_r1_probe_census tests.test_arm_retry.ZeroCaptureSuccessorTests.test_battery_float_zero_capture_only_and_probe_error_never_successor tests.test_epoch_continuation.EpochContinuationTests.test_revision_five_session_is_gated_on_battery_float_like_the_issuer",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 9 tests in 18.433s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONPATH=/Users/edr/code/JouleWise-wt-ed17a643-bfgd-sol python3 /tmp/bfgd_mutation_review.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["KILLED raw_digest_guard True", "KILLED history_guard True", "KILLED registry_digest_guard True"]},
      "expected": {"exit_code": 0, "tail_regex": "KILLED registry_digest_guard True"}
    },
    {
      "id": "V4",
      "kind": "smoke",
      "cmd": "PYTHONPATH=/Users/edr/code/JouleWise-wt-ed17a643-bfgd-sol python3 /tmp/bfgd_cadence_probe.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["cadence exit 0", "verdict CONTINUE", "diagnostic_only ABSENT"]},
      "expected": {"exit_code": 0, "tail_regex": "diagnostic_only ABSENT"}
    },
    {
      "id": "V5",
      "kind": "smoke",
      "cmd": "PYTHONPATH=/Users/edr/code/JouleWise-wt-ed17a643-bfgd-sol python3 /tmp/bfgd_cadence_root_probe.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["captures ['W1-d01', 'W2-d01']", "diagnostic_only ABSENT", "r5_n_verdict CONTINUE"]},
      "expected": {"exit_code": 0, "tail_regex": "captures \\['W1-d01', 'W2-d01'\\]"}
    },
    {
      "id": "V6",
      "kind": "smoke",
      "cmd": "PYTHONPATH=/Users/edr/code/JouleWise-wt-ed17a643-bfgd-sol python3 /tmp/bfgd_dryrun_probe.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["check exit 5", "member evidence reads ['W1-d01']", "W1: battery=pass recorded=absent"]},
      "expected": {"exit_code": 0, "tail_regex": "member evidence reads \\['W1-d01'\\]"}
    },
    {
      "id": "V7",
      "kind": "smoke",
      "cmd": "PYTHONPATH=/Users/edr/code/JouleWise-wt-ed17a643-bfgd-sol python3 /tmp/bfgd_check_vs_prepare.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["registration admissible for prepare-candidate: yes", "prepare exit 3", "REFUSED: battery-confounded set mismatch: computed non-pass session omitted: W1"]},
      "expected": {"exit_code": 0, "tail_regex": "computed non-pass session omitted: W1"}
    },
    {
      "id": "V8",
      "kind": "smoke",
      "cmd": "PYTHONPATH=/Users/edr/code/JouleWise-wt-ed17a643-bfgd-sol python3 /tmp/bfgd_prereg_probe.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["pinned load identity mismatch: preregistration_sha256", "cadence with wrong registration digest CONTINUE False"]},
      "expected": {"exit_code": 0, "tail_regex": "cadence with wrong registration digest CONTINUE False"}
    },
    {
      "id": "V9",
      "kind": "test",
      "cmd": "PYTHONPATH=/Users/edr/code/JouleWise-wt-ed17a643-bfgd-sol python3 /tmp/bfgd_writer_crash_mutation.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["crash test with post observation removed: PASSED"]},
      "expected": {"exit_code": 0, "tail_regex": "crash test with post observation removed: PASSED"}
    },
    {
      "id": "V10",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_validate_powermetrics_fiducial_derivation_only.DerivationOnlyLiveCaptureTests.test_battery_brackets_are_authenticated_and_outside_anchor_spans tests.test_validate_powermetrics_fiducial_derivation_only.BatteryFloatPinRegressionTests.test_sampler_protocol_estimator_and_chain_pins_are_unchanged",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Both tests passed when run separately: writer Ran 1 test in 45.219s, OK; pin Ran 1 test in 0.014s, OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V11",
      "kind": "lint",
      "cmd": "git diff --check c6814dd8 df33888f",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 2, "tail": ["Four battery_float/*.ioreg files: trailing whitespace and new blank line at EOF"]},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "E1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The sole failure in V1 is the pre-existing live-machine watch test: this sandbox returns no os_build because /usr/sbin/sysctl -n kern.osversion exits 1, Operation not permitted.",
      "needs": "Lead reruns that live-machine test outside this restricted sandbox."
    }
  ]
}
```

## Findings

**BLOCKER F1 — Cadence can label charging captures clean.** [report_window](/Users/edr/code/JouleWise-wt-ed17a643-bfgd-sol/scripts/calibration_cadence_report.py:47) authenticates the battery verdict for `--session`, then reads independently supplied `--window` paths at line 82. With W1 charging and W2 clean, the CLI accepted W1’s `powermetrics.plist` under `--session W1=W2`: exit 0, `CONTINUE`, no `diagnostic_only`. Using the [runbook’s directory argument](/Users/edr/code/JouleWise-wt-ed17a643-bfgd-sol/docs/phase_2/derivation_night_runbook.md:2571) for W2 included **both** `W1-d01` and `W2-d01` in its cadence calculation. Bind cadence captures to the authenticated session and its finalized ledger rows before using their numbers.

**BLOCKER F2 — The dry run opens result evidence before the verdict is committed.** On the real `check` path, a fixture with no verdict returned exit 5 and `recorded=absent`, yet traced `_read_member_evidence` opening `W1-d01`. [The missing-record branch](/Users/edr/code/JouleWise-wt-ed17a643-bfgd-sol/scripts/issue_calibration_acceptance_generation.py:239) falls through to the [member-evidence read](/Users/edr/code/JouleWise-wt-ed17a643-bfgd-sol/scripts/issue_calibration_acceptance_generation.py:262); that JSON contains B. This violates the required record-before-result-read order. Stop processing that session on a missing or disagreeing record.

**MATERIAL F3 — `check` gives a false admissibility answer after an omitted non-pass window.** On a full W1 charging, W1′ clean, W2 clean fixture, `check --session-ids W1-prime --session-ids W2` returned 0 and `registration admissible for prepare-candidate: yes`. The same fixture’s `prepare-candidate` returned 3: `computed non-pass session omitted: W1`. [_dry_run_epoch_bound](/Users/edr/code/JouleWise-wt-ed17a643-bfgd-sol/scripts/issue_calibration_acceptance_generation.py:312) detects only a *second* non-pass window; it does not reject the first omitted one. The issuer correctly refuses, but the prescribed desk decision reports the opposite.

**MATERIAL F4 — Three consumers accept a verdict under the wrong registration digest.** The dry run, cadence report, and continuation pass `preregistration_sha256=None`, disabling [identity check 3](/Users/edr/code/JouleWise-wt-ed17a643-bfgd-sol/joulewise/battery_float.py:457). A committed fixture record with an all-zero digest failed a pinned load with `identity mismatch: preregistration_sha256`, while the cadence CLI accepted it and emitted `CONTINUE`. Give these consumers an authenticated registration digest or refuse when it is unavailable.

**MATERIAL F5 — The recovery test does not establish its ruled outcome.** [Test 8](/Users/edr/code/JouleWise-wt-ed17a643-bfgd-sol/tests/test_validate_powermetrics_fiducial_derivation_only.py:600) allows recovery to leave no finalized row, so its `battery_float_evidence_missing` assertion need never run. Removing the writer’s post-observation call in a temporary copy left this test passing. The separate normal-writer bracket test does catch post-observation behavior; test 8 still needs a reachable recovery assertion or an explicit ruling that the no-row outcome satisfies its obligation.

**NIT F6–F7.** The [liveness-test explanation](/Users/edr/code/JouleWise-wt-ed17a643-bfgd-sol/tests/test_arm_readiness_evidence_t0.py:1059) still says 600 seconds although its assertions use 610. `git diff --check` reports trailing whitespace and a blank line at EOF in each of the four new ioreg fixtures.

The **610-second bound is right** for the implemented sites: eleven probes at 45 seconds, the battery ioreg probe’s enforced 10-second timeout, and 105 seconds of allowance. The older 645-second arithmetic assumes that ioreg also receives 45 seconds. The runbook’s arm-record item 6 is present. Direct base/candidate SHA-256 comparisons found unchanged protocol, four estimator sources, and chain bytes; the registered chain digest still matches. The logical-clock writer test passed the raw-file, artifact-key-set, anchor non-overlap, and 0-versus-2-second invariant assertions. The test diff changes expected t0 values from 600 to 610 and the probe census from 11 to 12; the other changed assertions add verdict output or preserve prior checks behind the new registry pin.

## Residual risk

The charge prohibited full test discovery. The focused 205-test run had one sandbox-dependent live-machine failure; nine additional gate tests, the isolated writer and pin tests, 39 docs/pin tests, and three killed mutations passed. The repository remained clean. **Verdict: FIX-FIRST.**