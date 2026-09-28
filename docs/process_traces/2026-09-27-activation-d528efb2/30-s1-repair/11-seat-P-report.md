```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Implemented texts 12a and 10a with the requested defect-shaped tests; one stale controller test needs scope authority, and the text 10a issuing expectation needs a lead ruling.",
  "workspace": {
    "base_requested": "c7593edbcaacdd2c7bbf0175ad315fdbafe5e275",
    "base_mode": "exact",
    "head_start": "c7593edbcaacdd2c7bbf0175ad315fdbafe5e275",
    "head_end": "c7593edbcaacdd2c7bbf0175ad315fdbafe5e275",
    "upstream_end": "e7c8bcc68d9a1c4f20e11c1904e49552c81ffcd1",
    "branch": "fix/2026-09-27-s1-regress-P"
  },
  "pathspec": [
    "joulewise/bundle_read.py",
    "joulewise/aggregate.py",
    "joulewise/controller.py",
    "scripts/run_campaign.py",
    "joulewise/calibration_bracketing.py",
    "tests/test_bfgs_window_consumers.py",
    "tests/test_bfgs_calibration_bracketing.py",
    "tests/test_bfgs_consumer_sweep.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONPATH=/tmp/s1-p-test-guard:. /opt/homebrew/bin/python3 -B -m unittest tests.test_bfgs_window_consumers tests.test_bfgs_calibration_bracketing tests.test_bfgs_consumer_sweep.ConsumerSweepTests.test_12a_9_mock_admission_call_forms_are_closed -q > /tmp/s1-p-final-scoped.log 2>&1; rc=$?; tail -n 18 /tmp/s1-p-final-scoped.log; exit $rc",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 56 tests in 196.118s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 56 tests.*OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONPATH=/tmp/s1-p-test-guard:. /opt/homebrew/bin/python3 -B -m unittest tests.test_bundle_read -q > /tmp/s1-p-bundle-read.log 2>&1; rc=$?; tail -n 15 /tmp/s1-p-bundle-read.log; exit $rc",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 118 tests in 354.232s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 118 tests.*OK"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONPATH=/tmp/s1-p-test-guard:. /opt/homebrew/bin/python3 -B -m unittest tests.test_battery_float tests.test_battery_float_consumers tests.test_battery_float_sweep -q > /tmp/s1-p-battery.log 2>&1; rc=$?; tail -n 15 /tmp/s1-p-battery.log; exit $rc",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 140 tests in 289.753s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 140 tests.*OK"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONPATH=/tmp/s1-p-test-guard:. /opt/homebrew/bin/python3 -B -m unittest tests.test_aggregate tests.test_audit_bundle_validation tests.test_authentication_io tests.test_axi_request_validation tests.test_cli_run tests.test_controller tests.test_corpus_strict_validation -q > /tmp/s1-p-importers-a.log 2>&1; rc=$?; tail -n 15 /tmp/s1-p-importers-a.log; exit $rc",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["Ran 299 tests in 339.471s", "FAILED (failures=28, errors=30, skipped=1)"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "PYTHONPATH=/tmp/s1-p-test-guard:. /opt/homebrew/bin/python3 -B -m unittest tests.test_d117_contrast_v5_pack tests.test_dependence_sensitivity tests.test_experiment tests.test_floor_extraction tests.test_idle_dependence tests.test_mint_floor_artifact_generalized tests.test_p2038_production_path -q > /tmp/s1-p-importers-b.log 2>&1; rc=$?; tail -n 15 /tmp/s1-p-importers-b.log; exit $rc",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["Ran 389 tests in 435.617s", "FAILED (failures=5, errors=48, skipped=2)"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "PYTHONPATH=/tmp/s1-p-test-guard:. /opt/homebrew/bin/python3 -B -m unittest tests.test_partial_record_enclosure tests.test_phase_share tests.test_reduce tests.test_schemas tests.test_uncertainty_p2029 tests.test_whole_window_selection tests.test_window_duration_margins -q > /tmp/s1-p-importers-c.log 2>&1; rc=$?; tail -n 15 /tmp/s1-p-importers-c.log; exit $rc",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["Ran 318 tests in 736.433s", "FAILED (failures=7, errors=48, skipped=1)"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V7",
      "kind": "test",
      "cmd": "PYTHONPATH=/tmp/s1-p-test-guard:. /opt/homebrew/bin/python3 -B -m unittest tests.test_bfgs_consumer_sweep -v > /tmp/s1-p-full-sweep.log 2>&1; rc=$?; tail -n 35 /tmp/s1-p-full-sweep.log; exit $rc",
      "cwd": ".",
      "observed": {"result": "not_run", "exit_code": 130, "tail": ["test_12a_9_mock_admission_call_forms_are_closed ... ok", "test_all_supported_ungated_reads_have_checked_reasons ...", "KeyboardInterrupt"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 27 tests.*OK"}
    },
    {
      "id": "V8",
      "kind": "inspection",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "scope_deviation",
      "level": "blocking",
      "text": "tests.test_controller.SuiteControllerTests.test_mock_experiment_refuses_at_aggregation still expects WindowBatteryRefusal, contrary to ruled operational mock admission; tests/test_controller.py is excluded from this seat's scope.",
      "needs": "Lead ruling and prospective authority for the exact test path; no out-of-scope edit was made."
    },
    {
      "id": "F2",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "Text 10a's issuing mode raises CustodyFailure for an absent original; an existing test_run_campaign issuing sub-case expects calibration_ledger_custody_invalid without an exception.",
      "needs": "Approve the R-list expectation change, or request a cold ruling for campaign-core exception translation."
    },
    {
      "id": "F3",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The full consumer sweep remained in an existing repository-wide AST check and was interrupted; its new T12a-9 test passed both alone and in V1.",
      "needs": "Lead reruns the complete sweep at the integration gate."
    },
    {
      "id": "F4",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "The 21 additional direct-importer modules produced 40 failures and 126 errors in 1006 tests. Most match later-seat fixture gaps; three test_reduce failures remain untriaged.",
      "needs": "Lead and later seats compare importer results after fixture repairs."
    }
  ],
  "scope_expansion": {
    "requested_paths": ["tests/test_controller.py"],
    "reason": "A pre-existing test asserts the behavior that ruled text 12a changes.",
    "blocked_work": "Update and verify the stale controller assertion.",
    "minimal_change": "Change test_mock_experiment_refuses_at_aggregation to assert an operational aggregate with every battery_float_members status not_applicable."
  }
}
```

## Change

The window gate now admits only a nonempty, wholly `not_applicable` mock window when passed `admit_mock_window=True`. The controller’s operational aggregate and ordinary campaign completion pass that keyword. Per-member aggregation receives it as well. Claim-writing consumers and the paired-entry gate at `run_campaign.py:7848` remain strict.

The calibration battery classifier now resolves custody using its caller’s `issuing` or `read_replay` mode and reads the evidence and raw pair from the resolved directory. Missing custody and changed evidence still raise `CustodyFailure`. New tests cover these changes without reading the laptop battery.

Counterfactuals and production call sites for the new tests:

| Test | Counterfactual input or edit that turns it red | Call site exercised |
|---|---|---|
| T12a-1 | Replace the all-member admission condition with any-member admission for mock plus passing real; also checks mock plus two other refusals | `authenticate_window_members` |
| T12a-2 | Count only refused members, omitting an `unobserved_historical` member | `authenticate_window_members` |
| T12a-3 | Remove the no-obligation return for a member stopped before its battery pair | `authenticate_window_members` |
| T12a-4 | Flip the keyword default to `True` for an all-mock window | The seven strict consumers’ calls to the gate |
| T12a-5 | Remove bound-config digest comparison after changing one config byte | Gate through `BundleReader` |
| T12a-6 | Remove backend comparison from a non-mock bundle carrying a mock marker | Gate through `BundleReader` |
| T12a-7 | Return mock admission before reading another member’s missing metadata | `authenticate_window_members` |
| T12a-8 | Drop `battery_float_members` from experiment or campaign completion, or admit mock in the analysis loader | `run_experiment`, `run_campaign`, `load_analysis_inputs` |
| T12a-9 | Add the keyword to the strict analysis loader or use an invalid keyword value | Production call-site AST sweep |
| T12a-10 | Remove aggregate’s whole-set gate so `_read_member` runs first | `aggregate_experiment` |
| T12a-11 | Add mock admission at the paired-entry gate | `run_axi_spec_campaign` |
| 10a(a) | Read the absent original locator instead of its matching backup | `discover_calibration_candidates` → classifier |
| 10a(b) | Hard-code `read_replay` while issuing | Classifier → mode-aware resolver |
| 10a(c) | Skip evidence SHA validation on a changed backup copy | Classifier |
| 10a(d) | Omit raw-pair custody authentication after deleting one backup file | Classifier |
| 10a(e) | Bypass battery exclusion for a charging backup capture | `discover_calibration_candidates` → classifier |

The counterfactuals are named for the lead’s mutation check; they were not planted in this worktree. The 10a discovery tests replace candidate construction so they isolate the battery classification and custody path.

## Verification notes

V1–V3 passed. V4–V6 exercised every additional module found importing `bundle_read` or `aggregate`, with the counts and exact commands above. The scratch `sitecustomize.py` used for those runs supplies fixture bytes to any battery probe; it is outside the repository and adds no production hook. The full consumer sweep did not finish. No full suite, capture, or powermetrics run was started.

For the §4 open point, I recommend changing the existing `issuing` test to expect `CustodyFailure` when the original is absent. That preserves text 10a; its old `calibration_ledger_custody_invalid` assertion would need separate coverage with an intact original. Catching and translating the exception in campaign production code changes the ruled boundary and requires a cold ruling.

## Residual risk

The stale controller test is outside this seat’s write scope and explicitly excluded by the addendum. The three `test_reduce` failures in V6 remain to be classified after the fixture seats land.