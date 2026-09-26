```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Round-3 fixes and regressions are implemented within scope; the strict C8 guard exposes nine existing out-of-scope calls.",
  "workspace": {
    "base_requested": "26ab7234",
    "base_mode": "exact",
    "head_start": "26ab72342e7200ebf0494f6e627bbb56e14f266c",
    "head_end": "26ab72342e7200ebf0494f6e627bbb56e14f266c",
    "upstream_end": "26ab72342e7200ebf0494f6e627bbb56e14f266c",
    "branch": "feat/2026-09-26-bfgs-s0-helper-fence"
  },
  "pathspec": [
    "joulewise/battery_float.py",
    "joulewise/evidence_night.py",
    "tests/test_battery_float.py",
    "tests/test_battery_float_consumers.py",
    "tests/test_battery_float_sweep.py",
    "tests/test_evidence_night.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "partial",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_battery_float tests.test_battery_float_consumers tests.test_battery_float_sweep",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["", "----------------------------------------------------------------------", "Ran 114 tests in 88.428s", "", "FAILED (failures=1)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_evidence_night tests.test_night_kinds",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [".....................................................................................................................................................................................", "----------------------------------------------------------------------", "Ran 181 tests in 350.892s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_issue_calibration_acceptance_generation",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["", "----------------------------------------------------------------------", "Ran 156 tests in 170.388s", "", "FAILED (failures=1)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V4",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_validate_powermetrics_fiducial_derivation_only",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["....", "----------------------------------------------------------------------", "Ran 27 tests in 207.653s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V5",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_run_night",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [".......................................................................................................................sss....................................................ssssss", "----------------------------------------------------------------------", "Ran 237 tests in 92.834s", "", "OK (skipped=9)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK \\(skipped=9\\)"}
    },
    {
      "id": "V6",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_epoch_continuation",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["....................................................................", "----------------------------------------------------------------------", "Ran 68 tests in 57.081s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "scope_deviation",
      "level": "blocking",
      "text": "The dictated C8 rule flags nine pre-existing dataclasses.replace calls across four production files outside WRITE_SCOPE. V1 fails only at the production-tree guard.",
      "needs": "Expand scope to the four requested files or issue a new ruling for these existing calls."
    },
    {
      "id": "F2",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "C10's no-skipped, no-exemption, and unreadable-kind behavior already passes at 26ab7234; honest guards for those properties cannot be RED on that base.",
      "needs": "Rule whether baseline-green C10 guards satisfy the universal RED-proof instruction."
    },
    {
      "id": "F3",
      "kind": "environment",
      "level": "nonblocking",
      "text": "V3's sole failure is test_live_probes_report_this_machine_against_the_active_epoch: sandbox sysctl evidence leaves os_build as None.",
      "needs": "Lead reruns the live probe outside this sandbox."
    }
  ],
  "scope_expansion": {
    "requested_paths": [
      "joulewise/arm_readiness_evidence_t0.py",
      "joulewise/night_gate.py",
      "scripts/run_night.py",
      "scripts/validate_powermetrics_fiducial.py"
    ],
    "reason": "C8 requires flagging every dataclasses.replace call in a production module importing battery_float; these files contain the nine existing calls.",
    "blocked_work": "Make the strict production-tree guard green.",
    "minimal_change": "Refactor or relocate those nine replacements while preserving their current behavior."
  }
}
```

## Change

- **C1–C4, C9; amendments 21–23:** [battery_float.py](/Users/edr/code/JouleWise-wt-bfgs-s0-6bec2aa6/joulewise/battery_float.py) now refuses unreadable journals, symlinked raw paths, duplicate JSON keys, invalid probe exit codes, malformed spans, and malformed or reversed pair stamps. Quiet refusal spans use the ruled start stamp and empty journal.
- **C5–C6, C10:** [evidence_night.py](/Users/edr/code/JouleWise-wt-bfgs-s0-6bec2aa6/joulewise/evidence_night.py) records a normal failed fence when a kind lacks `battery_brackets` and rejects stale `check.json` files without a passing fence row. Dedicated tests cover the skipped-state and unreadable-kind paths.
- **C7–C8, C11:** The [source-pin test](/Users/edr/code/JouleWise-wt-bfgs-s0-6bec2aa6/tests/test_battery_float.py) now covers 39 transitive definitions, including `_signed`; the ten original pins are unchanged. The [consumer guard](/Users/edr/code/JouleWise-wt-bfgs-s0-6bec2aa6/tests/test_battery_float_consumers.py) detects the four forgery forms and the ruled factory calls. The [phase sweep](/Users/edr/code/JouleWise-wt-bfgs-s0-6bec2aa6/tests/test_battery_float_sweep.py) resolves all three aliased import forms.
- **Amendments 20, 24–25, 27:** Added the monotonic conversion and refusal constant, `bundle_sha256`, the two status factories, and capture identity binding. C12 follows amendment 24; C13 follows amendment 27. [T15 regressions](/Users/edr/code/JouleWise-wt-bfgs-s0-6bec2aa6/tests/test_battery_float.py) cover these paths. No change was needed in `night_kinds.py`.

## Verification notes

Against an archived **26ab7234** checkout with the new tests overlaid, T15 reported `Ran 15 tests in 0.110s` and `FAILED (failures=19, errors=7)`. The RED cases include malformed and unreadable journals (C1), span and stamp defects (C2/22/23), symlink traversal (C3), duplicate keys in all five JSON inputs (C4), `False` and `0.0` exit codes (C9), missing conversion and refusal constants (20), missing bundle digest and factories (24/25), and capture identity mismatches (27). Separate capture identity subtests produced three failures and one error on that base. Fence tests produced `FAILED (failures=1, errors=1)` for the missing attribute and stale check (C5–C6).

The base pin table has ten entries and **no `_signed` pin** (C7). Its guard returned `[]` for each of the four C8 forgeries and a factory call. Its phase sweep accepted injected `bf.observe`, `x.observe`, and `o` calls with an invalid phase (C11). C10’s requested properties were already true at the base, so their new tests are guards rather than RED regressions.

V1’s only current failure is the strict C8 tree guard: nine existing replacement calls in the four requested out-of-scope files. V3’s only failure is the stated sandbox live-probe result. `git diff --check` passed. No commit or full-suite run was made.

## Residual risk

**NEEDS_SCOPE:** The lead must expand the allowlist for the four production files in the envelope, or rule a different treatment of their existing `dataclasses.replace` calls. The lead also needs to rule on the impossible baseline-RED demand for C10.