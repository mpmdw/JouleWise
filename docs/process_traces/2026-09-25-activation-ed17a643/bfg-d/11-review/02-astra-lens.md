```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "FIX-FIRST: malformed battery output reaches GO, the prescribed harvest sequence cannot run, and authentication and consumer gaps remain.",
  "workspace": {
    "base_requested": "c6814dd8",
    "base_mode": "descendant",
    "head_start": "6b5efdc3c9c91459d3280f8b6c170107fcb5ece5",
    "head_end": "6b5efdc3c9c91459d3280f8b6c170107fcb5ece5",
    "upstream_end": "e9ed7a98d26218f74f8fe2fb3b9515bc081c615a",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "decision": "FIX-FIRST",
    "candidate": "df33888f",
    "findings": [
      {
        "id": "B1",
        "severity": "blocker",
        "title": "Structurally invalid ioreg output can produce GO",
        "location": "joulewise/battery_float.py:87",
        "evidence": "Missing closing brace, wrong object class, and nested-only required properties each parsed as passed=True and produced GO through evaluate_night."
      },
      {
        "id": "B2",
        "severity": "blocker",
        "title": "Required harvest ordering conflicts with committed-pin precondition",
        "location": "scripts/issue_calibration_acceptance_generation.py:1359",
        "evidence": "A terminal session with its new pin not yet committed returned rc=3, calibration_ledger_head_uncommitted, and wrote no verdict."
      },
      {
        "id": "M1",
        "severity": "should_fix",
        "title": "Simplified Git path history hides verdict modifications",
        "location": "joulewise/battery_float.py:439",
        "evidence": "After merging a branch that changed and restored the verdict, ordinary path log showed one addition; full-history showed three touches; load_committed_verdict accepted pass."
      },
      {
        "id": "M2",
        "severity": "should_fix",
        "title": "Cadence data are not bound to the authenticated session",
        "location": "scripts/calibration_cadence_report.py:82",
        "evidence": "The identical 200 ms STOP capture was ordinary output with a clean session and diagnostic_only=battery_float_confounded with an unrelated charging session."
      },
      {
        "id": "M3",
        "severity": "should_fix",
        "title": "Documented cadence CLI fails to import from an uninstalled checkout",
        "location": "scripts/calibration_cadence_report.py:12",
        "evidence": "env -u PYTHONPATH PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/calibration_cadence_report.py --help exited 1 with ModuleNotFoundError: No module named 'joulewise'."
      },
      {
        "id": "M4",
        "severity": "should_fix",
        "title": "Three consumers omit required registration authentication",
        "location": "joulewise/battery_float.py:454",
        "evidence": "Wrong pinned registration digest raises NoRecord; the same record loads as pass with preregistration_sha256=None, used by dry run, cadence and continuation."
      },
      {
        "id": "M5",
        "severity": "should_fix",
        "title": "Night-gate ioreg uses a 30-second timeout instead of 10 seconds",
        "location": "joulewise/night_gate.py:1513",
        "evidence": "A mocked call through production run_night._probe_runner recorded timeout=30 for IOREG_BATTERY_ARGV; battery_float.PROBE_TIMEOUT_S is 10."
      }
    ],
    "timing_judgment": "610 s correctly sums eleven 45 s sites, one explicitly bounded 10 s site, and 105 s. 645 s is the literal older uniform-timeout formula. Neither establishes the empirical runtime bound.",
    "pin_audit": "No diff in configs, the four estimator modules, calibration_bracketing, or scripts/night_chains. Pin regression passed. Writer 0 s versus 2 s probe test passed with identical stamp differences and b_fiducial_s.",
    "assertion_audit": [
      "t0 liveness boundary inputs: 600000000001 -> 610000000001; 599999999999 -> 609999999999; 600000000000 -> 610000000000.",
      "Post-R1 site count: 11 -> 12; timeout arithmetic now uses eleven default timeouts plus the battery override.",
      "Night-gate expected probe sequence gains IOREG_BATTERY_ARGV immediately after PMSET_BATT_ARGV.",
      "Night-gate reason inventory, reason-test mapping and arm-retry COLD literal gain night_refused_battery_float.",
      "Legacy receipt comparison now projects out C3 battery_float and its probe citations; it does not independently assert the full new receipt.",
      "Dry-run template gains battery=pass recorded=pass; subsequent expected line indices shift by one.",
      "Writer evidence top-level expected key set gains battery_float; manifest and artifact_sha256 expected key sets remain unchanged.",
      "Cadence STOP, numeric medians and CLI exit expectations remain unchanged; calls gain ledger/session arguments.",
      "Continuation unanimity expectation is retained on a non-Revision-5 fixture; a new Revision-5 case expects earlier battery identity refusal.",
      "Registry grammar expectations remain unchanged behind a fixture-specific digest patch; new digest-refusal assertions are added."
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "cd /tmp/bfg-astra-caux1gt4 && PYTHONDONTWRITEBYTECODE=1 python3 -B review_repros.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "LOAD_AFTER_MERGE pass",
          "CADENCE clean STOP claim-bearing",
          "CADENCE charging STOP battery_float_confounded"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "CADENCE charging STOP battery_float_confounded"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "cd /tmp/bfg-astra-caux1gt4 && PYTHONDONTWRITEBYTECODE=1 python3 -B review_harvest.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "REFUSED: ledger: calibration_ledger_head_uncommitted",
          "UNCOMMITTED_TERMINAL_PIN_RC 3",
          "VERDICT_EXISTS False"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "VERDICT_EXISTS False"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "cd /tmp/bfg-astra-caux1gt4 && PYTHONDONTWRITEBYTECODE=1 python3 -B review_mutations.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "M1-disable-charging exit 1 FAILED (failures=1)",
          "M2-disable-staleness exit 1 FAILED (failures=1)",
          "M3-suppress-custody-failure exit 1 FAILED (failures=1)",
          "M4-disable-history-check exit 1 FAILED (failures=1)"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "M4-disable-history-check exit 1 FAILED"}
    },
    {
      "id": "V4",
      "kind": "suite",
      "cmd": "cd /tmp/bfg-astra-caux1gt4 && PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_battery_float tests.test_acc_25g83_rev5 tests.test_issue_calibration_acceptance_generation tests.test_calibration_cadence_report tests.test_epoch_continuation tests.test_night_gate tests.test_arm_retry",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["Ran 385 tests in 188.619s", "FAILED (failures=1, errors=1)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "cd /tmp/bfg-astra-caux1gt4 && PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_battery_float tests.test_validate_powermetrics_fiducial_derivation_only.BatteryFloatPinRegressionTests tests.test_arm_readiness_evidence_t0.ArmReadinessEvidenceT0Tests.test_t0_liveness_constant_is_derived_from_the_post_r1_probe_census",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 31 tests in 0.966s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "cd /tmp/bfg-astra-caux1gt4 && PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_validate_powermetrics_fiducial_derivation_only.DerivationOnlyLiveCaptureTests.test_battery_brackets_are_authenticated_and_outside_anchor_spans tests.test_validate_powermetrics_fiducial_derivation_only.DerivationOnlyLiveCaptureTests.test_writer_exit_before_post_observation_never_passes_a_slot",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 2 tests in 49.310s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V7",
      "kind": "smoke",
      "cmd": "env -u PYTHONPATH PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/calibration_cadence_report.py --help",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["ModuleNotFoundError: No module named 'joulewise'"]},
      "expected": {"exit_code": 0, "tail_regex": "--session"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "B2 and M1 expose conflicts in the prescribed obligations themselves: committed-pin ordering and simplified Git history.",
      "needs": "Reconcile the governing requirements and implementation before merge."
    },
    {
      "id": "F2",
      "kind": "environment",
      "level": "nonblocking",
      "text": "V4 had one live sysctl failure caused by Operation not permitted and one missing-history error in the git-archive copy. The historical receipt test passed when rerun in the original read-only worktree.",
      "needs": "Lead-owned final verification in the normal environment."
    }
  ]
}
```

## Findings

**B1 — BLOCKER: malformed battery output reaches `GO`.**  
[The parser](/Users/edr/code/JouleWise-wt-ed17a643-bfgd-astra/joulewise/battery_float.py:87) collects matching lines without validating object structure or property depth. V1 removed the final closing brace, substituted another object class, and supplied required properties exclusively inside a nested dictionary. **Each returned `passed=True` and `GO` through `evaluate_night`.** The existing truncation test removes the required properties too, so it misses this defect. Validate a complete AppleSmartBattery object and its top-level properties; test these counterexamples through both gate paths.

**B2 — BLOCKER: the prescribed harvest sequence cannot complete.**  
[The verdict writer](/Users/edr/code/JouleWise-wt-ed17a643-bfgd-astra/scripts/issue_calibration_acceptance_generation.py:1359) requires the terminal pin already committed. [Runbook step iii](/Users/edr/code/JouleWise-wt-ed17a643-bfgd-astra/docs/phase_2/derivation_night_runbook.md:2558) generates the verdict before step iv commits that pin and verdict together. V2 reproduced a normal terminal session with its updated, uncommitted pin: exit 3, `calibration_ledger_head_uncommitted`, no verdict. Tests conceal the conflict by precommitting the pin or constructing records with `require_committed_pin=False`. The lead must reconcile this requirement conflict and test the complete harvest sequence.

**M1 — MATERIAL: Git history authentication misses merged edits.**  
[The prescribed `git log` calls](/Users/edr/code/JouleWise-wt-ed17a643-bfgd-astra/joulewise/battery_float.py:439) use default path-history simplification. V1 committed a verdict, changed and restored it on a branch, then merged that branch. The authenticator saw one adding commit and accepted the record; `--full-history` exposed all three changes. No history rewrite was needed. This violates the stated rule that any subsequent modification invalidates the record. The implementation follows the prescribed commands, so the cure also needs a requirements correction. This reproduction establishes authentication failure, not an issued candidate with changed raw evidence.

**M2 — MATERIAL: callers can change whether cadence results count.**  
[The report](/Users/edr/code/JouleWise-wt-ed17a643-bfgd-astra/scripts/calibration_cadence_report.py:82) authenticates `session_id` but independently reads `capture_paths(window)`. It neither binds that inventory to the session’s finalized rows nor authenticates those capture bytes. V1 reported identical 200 ms `STOP` data twice: a clean session supplied ordinary output; an unrelated charging session supplied `diagnostic_only`. Thus a caller can change the report’s scientific status after seeing outcomes. Derive and authenticate the capture inventory from the selected session.

**M3 — MATERIAL: the documented cadence CLI fails before parsing arguments.**  
V7 reproduced `ModuleNotFoundError: No module named 'joulewise'` using the documented script invocation from a clean checkout without `PYTHONPATH`. The newly added imports lack the repository-root bootstrap used by the issuer. Existing tests import the module and call `main`, missing the executable entry point. Add a subprocess smoke test.

**M4 — MATERIAL: three consumers skip a required identity check.**  
Dry run, cadence and continuation pass `preregistration_sha256=None`; [the loader](/Users/edr/code/JouleWise-wt-ed17a643-bfgd-astra/joulewise/battery_float.py:454) consequently omits §4.3’s registration-digest comparison. Executed evidence: an incorrect supplied digest raised `NoRecord identity mismatch: preregistration_sha256`; `None` accepted the same record as `pass`. The issuer checks this correctly, but the other consumers do not meet the specified authentication contract. Supply their authoritative pin or obtain an explicit narrowing ruling.

**M5 — MATERIAL: t0’s production probe allows 30 seconds.**  
[The night gate](/Users/edr/code/JouleWise-wt-ed17a643-bfgd-astra/joulewise/night_gate.py:1513) injects `probes.run`, bypassing `observe`’s subprocess timeout. Its production implementation, `run_night._probe_runner`, uses 30 seconds. A mocked production call recorded `timeout=30`, against the required 10 seconds. Apply the override at that executor and test the production wiring.

The pin and writer checks passed. **610 seconds is the correct arithmetic for the implemented per-command bounds**: `11 × 45 + 10 + 105`. **645 seconds is the literal older uniform-timeout formula.** Neither proves the runtime envelope; the test’s explanatory text still describes the older 600-second calculation.

## Residual risk

The 385-test run had two environmental failures, detailed in F2; the Git-history-dependent test subsequently passed in the original worktree. No full discovery or live measurement campaign ran.

The single permitted live ioreg read showed AC connected, not charging, 0 mA, and an update age of approximately 17 seconds. This supports current-format parsing only. Endpoint observations cannot detect intervening charging excursions; future-dated `UpdateTime` handling remains the explicitly deferred BFG-S amendment.

The recovery test passed, but permits a recovered session with no finalized row; it does not necessarily exercise recovery producing a finalized `evidence_missing` row. PR-body requirements were not independently verified remotely.

**FIX-FIRST.**