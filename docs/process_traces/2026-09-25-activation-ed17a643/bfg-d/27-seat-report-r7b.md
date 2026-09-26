```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "partial",
  "summary": "Implemented H-1 through H-4 and completed the available H-5 sweep; the referenced integration tail was unavailable for an exact FAIL-line census.",
  "workspace": {
    "base_requested": "346e373f",
    "base_mode": "descendant",
    "head_start": "9d10cddea88cce65c1d31db457c859a48c0875a3",
    "head_end": "9d10cddea88cce65c1d31db457c859a48c0875a3",
    "upstream_end": null,
    "branch": "feat/2026-09-25-bfg-d"
  },
  "pathspec": [
    "scripts/paper_anchor_correction_quantified.py",
    "scripts/validate_powermetrics_fiducial.py",
    "tests/test_battery_float.py",
    "tests/test_battery_float_sweep.py",
    "tests/test_calibration_exits.py",
    "tests/test_calibration_writer_crash_matrix.py",
    "tests/test_revision_five_b_readers.py",
    "tests/test_t0_rehearsal.py",
    "tests/test_validate_powermetrics_fiducial_derivation_only.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_t0_rehearsal.T0RehearsalTests.test_rehearsal_t0_liveness_bound_refuses_at_600s_plus_1ns tests.test_git_fixture_maintenance.GitFixtureMaintenanceTests.test_every_test_module_routes_git_initialization_through_shared_helper tests.test_paper_round7_artifacts tests.test_calibration_exits.PublicGovernedExitWitnessTests.test_logical_producer_delay_preserves_exact_evidence_bytes",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["Ran 72 tests in 60.233s", "FAILED (failures=6)"]},
      "expected": {"exit_code": 1, "tail_regex": "FAILED \\(failures=6\\)"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_t0_rehearsal",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 32 tests in 15.100s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_calibration_exits.PublicGovernedExitWitnessTests.test_logical_producer_delay_preserves_exact_evidence_bytes tests.test_validate_powermetrics_fiducial_derivation_only.DerivationOnlyLiveCaptureTests.test_battery_brackets_are_authenticated_and_outside_anchor_spans",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 2 tests in 90.338s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_paper_round7_artifacts",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 69 tests in 455.989s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_battery_float_sweep tests.test_battery_float.GrammarFreezeTests",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 5 tests in 0.085s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "git diff --stat c6814dd8 -- joulewise/calibration_bracketing.py joulewise/adapters/powermetrics.py joulewise/powermetrics_fiducial.py joulewise/uncertainty_evidence.py joulewise/reduce.py protocol_v3.json scripts/night_chains configs scripts/paper_anchor_correction_quantified.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The contract's docs/process_traces/2026-09-25-activation-ed17a643/31-integ-137cc9ee/tail.txt is absent from this checkout, so its complete FAIL-line module list could not be independently checked.",
      "needs": "Lead compares the H-5 sweep below with the integration tail."
    },
    {
      "id": "F2",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "RED was reproduced at clean HEAD 9d10cdde, a descendant of requested 346e373f, rather than in a checkout at exactly 346e373f.",
      "needs": ""
    }
  ]
}
```

## Change

- **H-1 — [tests/test_t0_rehearsal.py:684](/Users/edr/code/JouleWise-wt-ed17a643-bfgd/tests/test_t0_rehearsal.py:684):** Moved all three liveness boundaries to 610 s and renamed them. **RED:** the old `600s_plus_1ns` refusal returned `('PASS', None)` instead of `('REFUSE', 'readiness_clock_preflight_refused')`. **GREEN:** `tests.test_t0_rehearsal` — `Ran 32 tests in 15.100s`, `OK`. The remaining `600_000_000_00` matches in `tests/` describe the T0 author-span lower bound or fixture span, not this liveness limit.

- **H-2 — [scripts/validate_powermetrics_fiducial.py:2155](/Users/edr/code/JouleWise-wt-ed17a643-bfgd/scripts/validate_powermetrics_fiducial.py:2155):** Logical-clock battery observations now receive clock stamps and fixture bytes through the observation call. The three logical writer harnesses pass an explicit fixture at [tests/test_calibration_exits.py:4538](/Users/edr/code/JouleWise-wt-ed17a643-bfgd/tests/test_calibration_exits.py:4538), [tests/test_calibration_writer_crash_matrix.py:645](/Users/edr/code/JouleWise-wt-ed17a643-bfgd/tests/test_calibration_writer_crash_matrix.py:645), and [tests/test_validate_powermetrics_fiducial_derivation_only.py:596](/Users/edr/code/JouleWise-wt-ed17a643-bfgd/tests/test_validate_powermetrics_fiducial_derivation_only.py:596). The production call retains real time and real `ioreg`; neither observation moved into the anchor interval. **RED:** `instrument_evidence.json changed under logical producer delay`, with delayed SHA-256 `96a571…3252d932` and baseline `75e346…43b5`. **GREEN:** the unchanged byte-comparison assertion and anchor non-overlap test — `Ran 2 tests in 90.338s`, `OK`; full `tests.test_calibration_exits` — `Ran 48 tests in 495.857s`, `OK`.

- **H-3 — [tests/test_battery_float.py:417](/Users/edr/code/JouleWise-wt-ed17a643-bfgd/tests/test_battery_float.py:417):** Routed Git initialization through `init_git_fixture`. **RED:** maintenance reported `{'test_battery_float.py': (416,)}`. **GREEN:** `tests.test_git_fixture_maintenance` — `Ran 5 tests in 6.797s`, `OK`; `tests.test_battery_float` — `Ran 55 tests in 49.555s`, `OK`.

- **H-4 — [scripts/paper_anchor_correction_quantified.py](/Users/edr/code/JouleWise-wt-ed17a643-bfgd/scripts/paper_anchor_correction_quantified.py):** Restored the producer byte-for-byte from `c6814dd8`, removed its C-2(b) test at [tests/test_revision_five_b_readers.py:61](/Users/edr/code/JouleWise-wt-ed17a643-bfgd/tests/test_revision_five_b_readers.py:61), and recorded the pinned historical-corpus disposition at [tests/test_battery_float_sweep.py:56](/Users/edr/code/JouleWise-wt-ed17a643-bfgd/tests/test_battery_float_sweep.py:56). **RED:** three paper artifact failures, including registry digest AS: expected `3844a8…d303f1`, observed `36cd66…387b0f8`. **GREEN:** `tests.test_paper_round7_artifacts` — `Ran 69 tests in 455.989s`, `OK`; `tests.test_revision_five_b_readers` — `Ran 2 tests in 0.004s`, `OK`; `tests.test_battery_float_sweep` — `Ran 3 tests in 0.055s`, `OK`.

- **H-5 — sweep:** The RED group reported `Ran 72 tests in 60.233s`, `FAILED (failures=6)`. Every available named failure module and identified importer passed after the fixes. Additional exact tails:

| Module | Tail |
|---|---|
| `tests.test_git_fixture_hygiene` | `Ran 7 tests in 0.014s` / `OK` |
| `tests.test_rehearse_t0_unattended` | `Ran 8 tests in 2.998s` / `OK` |
| `tests.test_validate_powermetrics_fiducial` | `Ran 12 tests in 7.668s` / `OK` |
| `tests.test_powermetrics_fiducial` | `Ran 75 tests in 60.944s` / `OK` |
| `tests.test_write_derivation_night_inputs` | `Ran 16 tests in 0.683s` / `OK` |
| `tests.test_calibration_ledger` | `Ran 95 tests in 4.769s` / `OK (skipped=1)` |
| `tests.test_calibration_ledger_custody` | `Ran 62 tests in 46.762s` / `OK` |
| `tests.test_calibration_live_three_window` | `Ran 23 tests in 2.379s` / `OK (skipped=3)` |
| `tests.test_calibration_writer_crash_matrix` | `Ran 20 tests in 240.640s` / `OK` |
| `tests.test_launch_window` | `Ran 38 tests in 470.571s` / `OK` |
| `tests.test_validate_powermetrics_fiducial_derivation_only` | `Ran 27 tests in 203.161s` / `OK` |
| `tests.test_paper_anchor_correction_quantified` | `Ran 12 tests in 0.374s` / `OK` |
| `tests.test_battery_float_consumers` | `Ran 9 tests in 9.240s` / `OK` |

The H-1 through H-4 module tails above are also part of the H-5 sweep. The known `test_sample_quiet_predicate_evidence` load-timing module was excluded as directed.

## Verification notes

The requested `git diff --stat c6814dd8 -- …` pin command produced **no output**. The paper producer’s SHA-256 is `3844a8f1eefb8b898a30b96f524e0af0da3af98fc2e6d0ecb78ea1d1f8d303f1`. `GrammarFreezeTests.test_structural_stage_is_pinned` passed (`Ran 1 test in 0.002s`, `OK`), and `git diff --check` passed. No full discovery was run. Changes remain uncommitted.

## Residual risk

The integration tail cited by the contract is absent from this worktree. The lead should compare its FAIL lines against the modules above before accepting H-5 as exhaustive.