```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Round-1 bundle implementation is in place; V2 needs an out-of-scope guard allowlist ruling and edit.",
  "workspace": {
    "base_requested": "1417c0c4caf36f7ac132410b3cd3ebc7aefbd9e7",
    "base_mode": "exact",
    "head_start": "1417c0c4caf36f7ac132410b3cd3ebc7aefbd9e7",
    "head_end": "1417c0c4caf36f7ac132410b3cd3ebc7aefbd9e7",
    "upstream_end": null,
    "branch": "feat/2026-09-26-bfgs-s1-bundles"
  },
  "pathspec": [
    "joulewise/bundle_read.py",
    "scripts/build_battery_float_historical_bundles.py",
    "configs/battery_float/historical_bundles.json",
    "tests/test_bundle_read.py",
    "tests/test_controller.py",
    "tests/test_reduce.py",
    "tests/test_bfgs_window_consumers.py"
  ],
  "unowned_dirty": [
    "joulewise/controller.py",
    "joulewise/publication_privacy.py",
    "tests/test_battery_float_sweep.py",
    "tests/test_revision_five_b_readers.py",
    "tests/test_bfgs_publication_privacy.py"
  ],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_controller tests.test_bundle_read tests.test_reduce tests.test_revision_five_b_readers tests.test_bfgs_publication_privacy tests.test_bfgs_window_consumers tests.test_battery_float_sweep",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "...............................................................................................................................................................................................................................................................................................................................",
          "----------------------------------------------------------------------",
          "Ran 319 tests in 867.521s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran [0-9]+ tests in .*s\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_battery_float tests.test_battery_float_consumers tests.test_evidence_night tests.test_night_kinds",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "",
          "----------------------------------------------------------------------",
          "Ran 312 tests in 1324.962s",
          "",
          "FAILED (failures=2)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran [0-9]+ tests in .*s\\n\\nOK"
      }
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_analysis_integration tests.test_audit_amplification tests.test_audit_bundle_validation tests.test_authentication_io tests.test_axi_controller_events tests.test_axi_mock_spec tests.test_axi_request_validation tests.test_cli tests.test_cli_run tests.test_corpus_strict_validation tests.test_determinism_gate tests.test_envelope_gate tests.test_experiment tests.test_floor_extraction tests.test_gate_sensibility_rounding tests.test_idle_dependence tests.test_mint_floor_artifact_generalized tests.test_nvidia_node_integration tests.test_p2038_production_path tests.test_package_bundle_pack tests.test_paper_reported_energy tests.test_partial_record_enclosure tests.test_phase_share tests.test_powermetrics tests.test_report tests.test_rpt001_report_slice tests.test_schemas tests.test_whole_window_selection tests.test_window_duration_margins",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "----------------------------------------------------------------------",
          "Ran 1052 tests in 1026.336s",
          "",
          "FAILED (failures=51, errors=37, skipped=16)",
          "KILLED 3 renderer AST mutations: wrapper deletion, widened annotation, unregistered renderer"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran [0-9]+ tests in .*s\\n\\nOK"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "scope_deviation",
      "level": "blocking",
      "text": "V2's exact replacement-call guard now sees four pre-existing dataclasses.replace calls in controller.py because the ruled controller implementation imports battery_float. Its guard file is outside WRITE_SCOPE.",
      "needs": "Lead ruling and prospective scope for tests/test_battery_float_consumers.py."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "V3 recorded 88 failures/errors in older consumer and fixture tests. Its one in-scope authentication-surface failure was corrected and passed a focused rerun; the full V3 suite was not repeated.",
      "needs": "Round 2 or lead triage of the out-of-scope tests and consumers."
    },
    {
      "id": "F3",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "V1 completed before two additional events parser tests and the historical-set read-API correction. Focused RED/GREEN and regression checks passed for that delta.",
      "needs": ""
    }
  ],
  "scope_expansion": {
    "requested_paths": ["tests/test_battery_float_consumers.py"],
    "reason": "The exact nine-row replace guard rejects four existing, older-type controller replacements once controller.py imports battery_float.",
    "blocked_work": "Make V2 green without evading the PairVerdict forgery guard.",
    "minimal_change": "After a lead ruling, add the four existing controller call sites to the typed replace allowlist and adjust its exact count, retaining the forgery self-tests."
  }
}
```

## Change

I audited every inherited edit. I **kept** the controller brackets, salvage, MOCK and `not_reached` records, F-1 capture authentication, privacy classifications, observe sweep rows, and attachment tests after checking them against the rulings. I **corrected** [bundle_read.py](/Users/edr/code/JouleWise-wt-bfgs-s1-e6f06c96/joulewise/bundle_read.py:225) so window classification handles `not_reached` according to the parsed baseline obligation, reports every nonpass member, and turns a member read error into `CustodyUnreadable`. I also made battery-bundle event reads fail on missing files, duplicate keys, and invalid UTF-8. No inherited edit was removed wholesale.

The [historical builder](/Users/edr/code/JouleWise-wt-bfgs-s1-e6f06c96/scripts/build_battery_float_historical_bundles.py) now hashes bytes from `1417c0c4`, independent of worktree fixture changes. Regeneration preserved the JSON bytes and pin `6cbdd1aa5bbda2b77338444a86b39b2fc0e8985fe08291cb34bdd7316f4d1a53`. The set has **13 entries, all from tracked fixtures**. One committed citation remains unresolved and was reported rather than dropped: `6945160964bc8667f4bfcc1ba7b500f81045fce8301ef7aadce45a188d3e06e9` in `scripts/issue_dg071_dg075_statistics.py`. `historical_captures.json` was not created.

I expanded [test_bundle_read.py](/Users/edr/code/JouleWise-wt-bfgs-s1-e6f06c96/tests/test_bundle_read.py), [test_controller.py](/Users/edr/code/JouleWise-wt-bfgs-s1-e6f06c96/tests/test_controller.py), and [test_bfgs_window_consumers.py](/Users/edr/code/JouleWise-wt-bfgs-s1-e6f06c96/tests/test_bfgs_window_consumers.py). New changes in [test_reduce.py](/Users/edr/code/JouleWise-wt-bfgs-s1-e6f06c96/tests/test_reduce.py) give mutable synthetic fixtures authenticated pairs while preserving their physics checks; these tests are synthetic evidence, not live hardware validation.

| Ruled text | Site and biting check | Base RED → current GREEN |
| --- | --- | --- |
| FT 7, 16, 18 | Controller bracket, salvage, MOCK, runner and stamp tests; removing a bracket or advancing the measured stamp difference fails `BatteryBracketTests`. | Base: 1 failure, 4 errors. Current: 5 tests `OK`. |
| FT 8; AD2 24–25 | Reader states, four gated accessors, digest-bound MOCK config, historical pin and factory verdicts. Removing `metadata()` from an accessor fails the prospective-bundle test. | Base: prospective and missing-event rows failed; the five targeted reader methods produced 8 failures and 1 error. Current: 16 `StrictAccessorTests` passed before the two later parser rows; those two also passed separately. |
| ERR 26 | `authenticate_window_members`; omitting a member or converting its read error fails the named-member tests. | Base: helper import error, including the two-member `{` row. Current: 8 window tests `OK`. |
| ERR 31 | `BundleReader.events()` and parsed `not_reached`; accepting a missing or malformed journal fails T8. | Base: missing, malformed, duplicate-key and invalid-UTF-8 rows RED. Current: all four targeted rows GREEN. |
| FT 11; AD2 27 | Attachment authenticates capture before physics and copies the two raw files. | Base charging row failed because it gave the old blanket Revision-5 reason. Current charging and passing-capture rows: 2 `OK`; the epoch refusal passed in V1. |
| FT 13 | Publication privacy record and raw-path classifications. | Base rejected `battery_float` as unclassified. Current publication test passed in V1. |
| S1 observe sweep | Controller `bundle_pre` and `bundle_post` calls. | Base: both sweep assertions failed. Current sweep passed in V1. |

The protected paths, including `battery_float.py`, `reduce.py`, `bundle.py`, all four estimator code paths, and the named campaign and calibration trees, have zero diff from `1417c0c4`. `git diff --check` passes. No commit or push was made.

## Verification notes

The exact V1, V2 and V3 final five-line tails are in the envelope. RED checks ran against a temporary archive of `1417c0c4`; their focused GREEN counterparts ran against this worktree.

**V2 needs scope and a ruling.** Its two failures are `test_no_consumer_references_a_verdict_primitive` and `test_replace_call_allowlist_is_exact_and_only_covers_older_types`. The first reports these pre-existing controller calls verbatim:

```text
('joulewise/controller.py', 1983, 'dataclasses.replace')
('joulewise/controller.py', 2566, 'dataclasses.replace')
('joulewise/controller.py', 2569, 'dataclasses.replace')
('joulewise/controller.py', 2966, 'dataclasses.replace')
```

The exact guard currently permits nine older-type replacement sites. Adding the ruled `battery_float` import exposes four more. Changing that exact allowlist requires [tests/test_battery_float_consumers.py](/Users/edr/code/JouleWise-wt-bfgs-s1-e6f06c96/tests/test_battery_float_consumers.py), outside this seat’s WRITE_SCOPE; I did not edit or evade the guard. [V2’s verbatim log](/private/tmp/bfgs-s1-v2.log) contains both assertions.

**V3 recorded 51 failures and 37 errors.** Every failure header and final exception line is in the [failure index](/private/tmp/bfgs-s1-v3-failure-index.txt); [the full log](/private/tmp/bfgs-s1-v3.log) preserves every traceback verbatim. Examples include `ValueError: instrument calibration battery_float_evidence_missing: pre evidence missing: phase not recorded; post evidence missing: phase not recorded` in the older P2038 fixture, and `joulewise.bundle_read.BundleReadError: config.json digest does not match metadata.config_sha256` in window-duration fixtures. One V3 failure was in scope: the authentication surface guard rejected direct `read_bytes` in the historical-set loader. I replaced it with `read_authentication_input`; that guard and three focused historical-reader checks now pass. The other affected test modules remain for round 2 or the lead.

## Residual risk

**NEEDS_SCOPE and lead ruling:** authorize the narrowly described guard update in `tests/test_battery_float_consumers.py`, or rule another compliant way to account for the four existing controller replacements. Until then V2 is red. V3’s older fixtures and consumers also need later-owner triage; the reader gate was not weakened to make those tests pass.