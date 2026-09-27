```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "A1, A2 and A5 hold; two ungated claim routes fail A3 under amendment 66.",
  "workspace": {
    "base_requested": "1417c0c4",
    "base_mode": "descendant",
    "head_start": "4aefdd1213aa13c0dba7a4a16fa62c0bcd933267",
    "head_end": "4aefdd1213aa13c0dba7a4a16fa62c0bcd933267",
    "upstream_end": "b69c39eb",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "a1": "hold: requested spot-check rows GREEN; in-memory counterfactuals RED",
    "a2": "hold: 119 reported keys equal 119 allowlist keys; no false class or kind found",
    "a3": "fails",
    "a4": "lead-owned merge-gate rerun; no finding predicts a V1/V2 failure",
    "a5": "hold",
    "reader_methods": 30,
    "raw_capture_readers": 48,
    "supported_forms_missed": 0,
    "rule_11": false,
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "class": "1: A3 failure, amendment 66(a) row 1b",
        "location": "scripts/run_campaign.py:2811",
        "summary": "A refused member's 9.99 W idle baseline reaches a later campaign's cooldown note and member verdict. S1 changed evaluate_member and campaign_cooldown_before_member, so the unchanged-route requirement for row 1c fails."
      },
      {
        "id": "F2",
        "severity": "blocker",
        "class": "1: A3 failure, amendment 66(a) row 1b",
        "location": "joulewise/whole_window.py:788",
        "summary": "The bundle gate passes a run carrying a calibration copy with missing capture battery evidence; the calibration verifier accepts its power-derived bound and re-reduction succeeds. S1 changed the whole-window preparation function on this route."
      }
    ]
  },
  "verification": [
    {
      "id": "A2",
      "kind": "test",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3 -m unittest tests.test_bfgs_consumer_sweep.ConsumerSweepTests.test_all_supported_ungated_reads_have_checked_reasons tests.test_bfgs_consumer_sweep.ConsumerSweepTests.test_inventory_count_and_scope_boundary tests.test_bfgs_consumer_sweep.ConsumerSweepTests.test_raw_capture_inventory tests.test_bfgs_consumer_sweep.ConsumerSweepTests.test_closed_gate_and_reader_definitions",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 4 tests in 303.759s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK$"}
    },
    {
      "id": "A1",
      "kind": "test",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3 -m unittest tests.test_bfgs_consumer_sweep.DetectorExamples.test_all_scopes_and_references tests.test_bfgs_consumer_sweep.ConsumerSweepTests.test_caller_references_and_campaign_consumers tests.test_bfgs_consumer_sweep.ConsumerSweepTests.test_envelope_summary_is_gated_in_own_scope tests.test_bfgs_consumer_sweep.ConsumerSweepTests.test_salvage_non_claim_rows",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 4 tests in 477.350s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK$"}
    },
    {
      "id": "F1-current",
      "kind": "smoke",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3 /tmp/s1-refuter-77b1bee2/cooldown_probe.py /Users/edr/code/JouleWise-wt-s1-refuter-77b1bee2 /tmp/s1-refuter-77b1bee2/current_cooldown",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["[6/charging_anchor] member verdict row carries anchor bundle_id=C baseline power=9.99", "[6/charging_anchor] cooldown reasons in _member_readiness_reasons: []"]
      },
      "expected": {"exit_code": 0, "tail_regex": "baseline power=9\\.99"}
    },
    {
      "id": "F1-main",
      "kind": "smoke",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3 /tmp/s1-refuter-77b1bee2/cooldown_probe.py /tmp/s1-refuter-77b1bee2/main /tmp/s1-refuter-77b1bee2/main_cooldown",
      "cwd": "/tmp/s1-refuter-77b1bee2/main",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["[6/charging_anchor] member verdict row carries anchor bundle_id=C baseline power=9.99", "[6/charging_anchor] cooldown reasons in _member_readiness_reasons: []"]
      },
      "expected": {"exit_code": 0, "tail_regex": "baseline power=9\\.99"}
    },
    {
      "id": "F2",
      "kind": "smoke",
      "cmd": "env PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3 /tmp/s1-refuter-77b1bee2/attached_probe.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["missing_pair_rehashed run: pass capture: battery_float_evidence_missing bound: 0.02142716616057592 detail: None strict_problems: [] current_strict: True", "reduced: RunStatus.SUCCEEDED fiducial_envelope: {'method': 'common_trace_shift_plus_independent_edge_corners_v3', 'anchor_bound_s': 0.021938421455370213, 'point_j': 88.5432, 'lower_j': 88.47995267160384, 'upper_j': 88.60644732839616, 'max_abs_delta_j': 0.06324732839615876, 'wall_minus_monotonic_independent_edge_span_s': 2.1457672119140625e-06, 'independent_edge_shift_bound_j': 0.06324732839615876}"]
      },
      "expected": {"exit_code": 0, "tail_regex": "reduced: RunStatus\\.SUCCEEDED"}
    }
  ],
  "flags": [
    {
      "id": "G1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "Both A3 failures fall under amendment 66(a) row 1b because S1 changed functions on their routes.",
      "needs": "Cold-gate rulings for the production fixes inside S1 before merge."
    }
  ]
}
```

## Findings

- **F1 — BLOCKER, class (1), A3.** A charging bundle is refused by its battery gate, yet `evaluate_member` reads its 9.99 W idle baseline. The value is stored as a cooldown anchor and appears in the next campaign’s member verdict; it changes cooldown from `cap_hit` at a 0.2 W anchor to `recovered` at 9.99 W. The same probe produced those values on main. The existing BFGS-COOLDOWN-ANCHOR-01 lane has an order and interim check, but amendment 66 (a) also requires *no changed line in any function on the route* for its nonblocking row 1c. S1 added lines in [evaluate_member](/Users/edr/code/JouleWise-wt-s1-refuter-77b1bee2/scripts/run_campaign.py:2811) and [campaign_cooldown_before_member](/Users/edr/code/JouleWise-wt-s1-refuter-77b1bee2/scripts/run_campaign.py:4221). Row 1c therefore cannot exempt this A3 failure.

- **F2 — BLOCKER, class (1), A3.** The [whole-window gate](/Users/edr/code/JouleWise-wt-s1-refuter-77b1bee2/joulewise/whole_window.py:680) checks the run bundle’s battery pair. The [attachment gate](/Users/edr/code/JouleWise-wt-s1-refuter-77b1bee2/joulewise/controller.py:448) checks the calibration capture when it is attached, but reduction does not recheck the pair in the copy. In a scratch fixture, removing that pair and consistently rehashing the copied evidence left the run bundle `pass`, the capture `battery_float_evidence_missing`, strict validation clean, and [_verify_instrument_calibration](/Users/edr/code/JouleWise-wt-s1-refuter-77b1bee2/joulewise/reduce.py:1171) returning the same numeric bound. Re-reduction succeeded with an energy envelope. [Whole-window preparation](/Users/edr/code/JouleWise-wt-s1-refuter-77b1bee2/joulewise/whole_window.py:788) accepts that bound for its claim path. S1 changed that function, so amendment 66 (a) row 1c does not apply. BFGS-RAWCAPTURE-01 names this question but does not supply the missing gate.

A2 found **119 allowlist keys**, equal to the reported keys: 61 `non_claim`, 44 `strict_validation`, 8 `behind_gate`, 3 gate bodies, 2 tolerant definitions, and 1 historical row. I found no false class among them or false kind among the 30 reader methods and 48 raw-capture members. The `_run_assertions.check_a3` key exists; its nested function holds the summary read at line 734, while `_run_assertions` holds none of its own.

The four `validation` members write no file or lasting object field; the assignments in `_strict_uncertainty_evidence_problems` alter a local expected-value dictionary. Their tracked callers consume problem or refusal strings without parsing numbers from them. At `_current_core_rederivation_reasons`, the calibration bound is compared with stored values and dropped; that function returns only a `set[str]`.

A1’s requested spot checks passed on the candidate. The old detector was silent for R51-23 through R51-26, while the current detector reported those inputs. In-memory source and guard counterfactuals were caught for R51-27, R51-28, R59-3b, R60-2b, R60-6 and R72-2. A5 also holds: `battery_float.py` hashes to `4b4d7bb20625…`; it, `reduce.py` and `bundle.py` match base byte for byte, and none of the eight named consumers imports `battery_float`.

No class (4) missed supported form was found, so the three-form rule-11 route does not apply.

## Residual risk

A4 belongs to the lead’s merge gate. V1, V2 and the builder checks were reported green on the S1 head, and the merge candidate changes none of their production or sweep-test files. These A3 witnesses pass checks those suites exercise; I found no reason they would turn V1 or V2 red.

S1 REFUTER: A3 FAILS