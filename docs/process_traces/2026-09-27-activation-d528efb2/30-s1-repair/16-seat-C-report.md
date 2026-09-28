```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Evidence-forward fixtures cleared 201 of 207 inventoried seat-C failures; six remain pending two lead rulings and seat B's shared fixture repair.",
  "workspace": {
    "base_requested": "4b4660de",
    "base_mode": "exact",
    "head_start": "4b4660dec4948f8b6d1f43a4d1e03569f886657b",
    "head_end": "4b4660dec4948f8b6d1f43a4d1e03569f886657b",
    "upstream_end": null,
    "branch": "fix/2026-09-27-s1-regress-C"
  },
  "pathspec": [
    "tests/test_arm_readiness_evidence_author.py",
    "tests/test_bracket_binding_cli.py",
    "tests/test_calibration_bracketing.py",
    "tests/test_calibration_live_three_window.py",
    "tests/test_check_window_provenance.py",
    "tests/test_d165_dominance_closeout.py",
    "tests/test_epoch_continuation.py",
    "tests/test_launch_window.py",
    "tests/test_p2038_production_path.py",
    "tests/test_phase_share.py",
    "tests/test_whole_window.py",
    "tests/test_whole_window_selection.py",
    "tests/test_window_duration_margins.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "partial",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard /opt/homebrew/bin/python3 -B -m unittest tests.test_calibration_live_three_window",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 23 tests in 16.436s", "OK (skipped=3)"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard /opt/homebrew/bin/python3 -B -m unittest tests.test_calibration_bracketing",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 93 tests in 1.548s", "OK (skipped=1)"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard /opt/homebrew/bin/python3 -B -m unittest tests.test_epoch_continuation",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 68 tests in 289.789s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard /opt/homebrew/bin/python3 -B -m unittest tests.test_d165_dominance_closeout",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 59 tests in 59.400s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard /opt/homebrew/bin/python3 -B -m unittest tests.test_dominance_closeout",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 3 tests in 26.439s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard /opt/homebrew/bin/python3 -B -m unittest tests.test_check_window_provenance",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 36 tests in 160.575s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V7",
      "kind": "test",
      "cmd": "PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard /opt/homebrew/bin/python3 -B -m unittest tests.test_bracket_binding_cli",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 19 tests in 158.841s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V8",
      "kind": "test",
      "cmd": "PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard /opt/homebrew/bin/python3 -B -m unittest tests.test_window_duration_margins",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 35 tests in 47.561s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V9",
      "kind": "test",
      "cmd": "PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard /opt/homebrew/bin/python3 -B -m unittest tests.test_p2038_production_path",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 8 tests in 672.511s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V10",
      "kind": "test",
      "cmd": "PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard /opt/homebrew/bin/python3 -B -m unittest tests.test_arm_readiness_evidence_author",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 24 tests in 654.611s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V11",
      "kind": "test",
      "cmd": "PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard /opt/homebrew/bin/python3 -B -m unittest tests.test_arm_readiness_dry_run",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 12 tests in 372.987s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V12",
      "kind": "test",
      "cmd": "PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard /opt/homebrew/bin/python3 -B -m unittest tests.test_launch_window",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 38 tests in 2207.410s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V13",
      "kind": "test",
      "cmd": "PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard /opt/homebrew/bin/python3 -B -m unittest tests.test_whole_window",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["Ran 59 tests in 496.013s", "FAILED (errors=2)"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V14",
      "kind": "test",
      "cmd": "PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard /opt/homebrew/bin/python3 -B -m unittest tests.test_whole_window_selection",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["Ran 57 tests in 287.425s", "FAILED (failures=3)"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V15",
      "kind": "test",
      "cmd": "PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard /opt/homebrew/bin/python3 -B -m unittest tests.test_phase_share",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["Ran 13 tests in 0.310s", "FAILED (failures=1)"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V16",
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
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "Text 10a makes the absent-original issuing subcases in CandidateDiscoveryModeTests.test_session_candidate_discovery_uses_original_unless_replay raise CustodyFailure; the existing assertion expects calibration_ledger_custody_invalid. The ruling reserves that R-list decision for the lead.",
      "needs": "Approve the CustodyFailure expectation for capture/instrument_evidence.json with observed absent, or request a cold ruling."
    },
    {
      "id": "F2",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "PhaseBoundaryEnvelopeTests.test_changed_source_bytes_change_a_pinned_sha256_digest pins metadata bytes that cannot include the required bound battery pair. Removing those bytes now raises BatteryStatusRefusal with battery_float_evidence_missing.",
      "needs": "Approve an R-list rewrite for the strict refusal and a sibling test that changes authenticated metadata and verifies the changed SHA."
    },
    {
      "id": "F3",
      "kind": "scope_deviation",
      "level": "blocking",
      "text": "Three whole-window-selection G11 tests import _current_core_fixture from out-of-scope tests/test_floor_extraction.py; its current-strict bundles produce environment_admission_missing and whole_window_verdict_provenance_invalid.",
      "needs": "Merge seat B's evidence-forward fixture repair, then rerun tests.test_whole_window_selection; grant this exact path only if seat B does not resolve it."
    }
  ],
  "scope_expansion": {
    "requested_paths": ["tests/test_floor_extraction.py"],
    "reason": "The shared current-strict fixture is owned by seat B and is required by three seat-C tests.",
    "blocked_work": "Passing the three MaxBracketConsumptionTests G11 cases in tests/test_whole_window_selection.py.",
    "minimal_change": "Repair _current_core_fixture with authentic current-strict bundle evidence."
  }
}
```

## Change

Built bound config and battery evidence for the claim-bearing fixtures, repaired G6/G7 capture custody with real bytes behind the affected digests, and supplied an injected battery runner for the production-path tests. The existing-test **R-list is empty**. An assertion census found no changed assertions in existing tests; one new evidence-bearing issuing-discovery sibling test was added.

| File | Inventoried failures → remaining |
|---|---:|
| `test_whole_window.py` | 14 → 2 |
| `test_whole_window_selection.py` | 18 → 3 |
| `test_d165_dominance_closeout.py` | 48 → 0 |
| `test_dominance_closeout.py` | 1 → 0 |
| `test_check_window_provenance.py` | 25 → 0 |
| `test_bracket_binding_cli.py` | 19 → 0 |
| `test_calibration_live_three_window.py` | 20 → 0 |
| `test_calibration_bracketing.py` | 6 → 0 |
| `test_epoch_continuation.py` | 6 → 0 |
| `test_p2038_production_path.py` | 9 → 0 |
| `test_window_duration_margins.py` | 24 → 0 |
| `test_phase_share.py` | 3 → 1 |
| `test_launch_window.py` | 11 → 0 |
| `test_arm_readiness_evidence_author.py` | 2 → 0 |
| `test_arm_readiness_dry_run.py` | 1 → 0 |

## Verification notes

**NEEDS_RULING — issuing custody.** For `tests.test_whole_window.CandidateDiscoveryModeTests.test_session_candidate_discovery_uses_original_unless_replay`, the old assertion expects `_prepare` to return with `calibration_ledger_custody_invalid`. Text 10a instead raises `CustodyFailure` for the `capture/instrument_evidence.json` member with `observed absent`. I recommend approving that expectation change. The new sibling test already covers issuing with a present, authenticated original.

**NEEDS_RULING — pinned phase-share SHA.** For `tests.test_phase_share.PhaseBoundaryEnvelopeTests.test_changed_source_bytes_change_a_pinned_sha256_digest`, the old metadata SHA is `7386959d…`; the evidence-bearing fixture produces `8425a9e6…`. Replacing metadata with the old stripped bytes raises `BatteryStatusRefusal`, status `battery_float_evidence_missing`, for the prospective bundle. I recommend approving that refusal assertion and moving the changed-SHA check to a sibling that mutates valid metadata and rewrites its pair. A focused probe confirmed that such a valid mutation changes the SHA and remains analyzable.

## Residual risk

**NEEDS_SCOPE / cross-seat dependency.** The three remaining `MaxBracketConsumptionTests` failures are `test_b1_r1_explicit_minted_fresh_valid_session_is_prepared_and_accepted`, `test_b1_r4_implicit_minted_fresh_valid_session_matches_explicit`, and `test_minted_semantics_loads_and_refuses_pending_ledger_snapshot`. They consume seat B’s `tests/test_floor_extraction.py` fixture. No out-of-scope file was edited. Merge seat B’s repair and rerun that module before considering the requested scope expansion.