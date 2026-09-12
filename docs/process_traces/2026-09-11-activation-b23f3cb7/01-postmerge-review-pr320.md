```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "No code integration defect found; two documentation follow-ups and one sandbox-blocked live-probe test remain.",
  "workspace": {
    "base_requested": "baf7b900",
    "base_mode": "exact",
    "head_start": "baf7b900d2185ae29cd972b423722a03f8f40bfd",
    "head_end": "baf7b900d2185ae29cd972b423722a03f8f40bfd",
    "upstream_end": "baf7b900d2185ae29cd972b423722a03f8f40bfd",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "outcome": "FOLLOW-UP NEEDED",
    "lanes": ["PASS-route runbook", "post-merge bookkeeping", "lead-owned identity-probe verification"],
    "findings": [
      {
        "id": "F1",
        "severity": "should_fix",
        "path": "docs/phase_2/derivation_night_runbook.md",
        "line": 1695,
        "summary": "PASS instructions omit the implemented continuation preparation, issuance/registry pin, and authentication-check path."
      },
      {
        "id": "F2",
        "severity": "nit",
        "path": "RUN_STATE.md",
        "line": 13,
        "summary": "Current checkpoint and kernel-generated queue still describe the merged continuation PR as unlanded or unopened."
      }
    ],
    "focused_tests": {
      "modules": 30,
      "tests": 1554,
      "failures": 1,
      "errors": 0,
      "skipped": 8
    }
  },
  "verification": [
    {
      "id": "V1",
      "kind": "lint",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 scripts/gen_state.py --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -m unittest tests.test_epoch_continuation",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 63 tests in 70.927s", "", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK$"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -m unittest tests.test_validate_powermetrics_fiducial",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 12 tests in 9.388s", "", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK$"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -m unittest tests.test_validate_powermetrics_fiducial_derivation_only",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 13 tests in 85.787s", "", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK$"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -m unittest tests.test_write_derivation_night_inputs",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 16 tests in 0.884s", "", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK$"}
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -m unittest tests.test_d078_reason_registry",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 14 tests in 0.112s", "", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK$"}
    },
    {
      "id": "V7",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -m unittest tests.test_arm_readiness_evidence_author",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 24 tests in 367.426s", "", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK$"}
    },
    {
      "id": "V8",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -m unittest tests.test_arm_readiness_evidence_author.ArmReadinessEvidenceAuthorTests.test_suite_timeout_kills_delayed_grandchild_process_group",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 1 test in 3.312s", "", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK$"}
    },
    {
      "id": "V9",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -m unittest tests.test_issue_calibration_acceptance_generation",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["AssertionError: None is not an instance of <class 'str'>", "Ran 114 tests in 131.028s", "FAILED (failures=1)"]},
      "expected": {"exit_code": 0, "tail_regex": "OK$"}
    },
    {
      "id": "V10",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -m unittest tests.test_issue_calibration_acceptance_generation.DeskEpochWatchTests.test_live_probes_report_this_machine_against_the_active_epoch",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["AssertionError: None is not an instance of <class 'str'>", "Ran 1 test in 0.075s", "FAILED (failures=1)"]},
      "expected": {"exit_code": 0, "tail_regex": "OK$"}
    },
    {
      "id": "V11",
      "kind": "smoke",
      "cmd": "/usr/sbin/sysctl -n kern.osversion",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["sysctl: sysctl fmt -1 1024 1: Operation not permitted"]},
      "expected": {"exit_code": 0, "tail_regex": "\\S+"}
    }
  ],
  "flags": [
    {
      "id": "E1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The issuer live-probe test fails because sandbox sysctl access is denied. The isolated test reproduces the failure; both the probe and test are unchanged by #320.",
      "needs": "Lead rerun the isolated live-probe test in a session with permitted identity-probe access."
    },
    {
      "id": "R1",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "The full suite was deliberately not run. Continued-epoch behavior was verified with synthetic evidence; no hardware campaign or continuation issuance was performed.",
      "needs": ""
    }
  ]
}
```

## Findings

**F1 — SHOULD_FIX: connect the PASS runbook to the implemented transaction.**  
`docs/phase_2/derivation_night_runbook.md:1695` still instructs the operator to land the “SMALLEST change” if freshness blocks continuation. Lines 1698–1699 describe the addendum as what licenses ordinary capture, but omit the issued continuation artifact, registry pin, and authentication check required by the new contract.

Command:

```sh
rg -n -o 'If the epoch-freshness[^|]+|What licenses ordinary capture is the|D-102 continuation addendum, once it lands' docs/phase_2/derivation_night_runbook.md
```

Output identifies lines **1695, 1698, 1699**. Searching this runbook and `docs/process/*.md` for `issue_epoch_continuation` returns no matches. Link the continuation contract and distinguish preparation, governed issuance/pinning, and `check`. This is an operational gap; the code continues to refuse without the pin.

**F2 — NIT: refresh pre-merge checkpoint and queue descriptions after accepting this review.**

Command:

```sh
rg -n -o 'still in the gate on its branch|NOT yet a PR|PR not yet opened|continuation mechanism \(S10\) in the gate on its branch' RUN_STATE.md TASK_QUEUE.md docs/process/state_kernel.json
```

Output:

```text
RUN_STATE.md:13:still in the gate on its branch
RUN_STATE.md:15:NOT yet a PR
docs/process/state_kernel.json:41:continuation mechanism (S10) in the gate on its branch
docs/process/state_kernel.json:2388:PR not yet opened
TASK_QUEUE.md:793:continuation mechanism (S10) in the gate on its branch
TASK_QUEUE.md:797:PR not yet opened
TASK_QUEUE.md:967:continuation mechanism (S10) in the gate on its branch
TASK_QUEUE.md:971:PR not yet opened
```

Update kernel-owned status and regenerate its views. No incorrectly named continuation script was found in the requested documentation.

**No BLOCKER or code integration defect found.**

- Helper calls are at `calibration_bracketing.py:2058`, `validate_powermetrics_fiducial.py:409`, and `issue_epoch_continuation.py:324`. The artifact reader is called by `load_epoch_continuations` and the continuation CLI’s `check`. Snapshot and registry-only refusal behavior matches the changed contracts.
- No production consumer requires the former four-key `screen_basis` or rejects the additive `acceptance_preflight`. The issuer, S1 writer, night chain, and generator retain compatible ledger and identity structures.
- The original-epoch-only issuer desk watch at `scripts/issue_calibration_acceptance_generation.py:271` is explicitly deferred by the contract and already tracked as `ISSUER-CHECK-CONTINUATION-AWARE-01`.
- `git diff a6ddb2ab baf7b900 -- joulewise scripts` is empty. The CI-defined kernel check at `.github/workflows/ci.yml:34` passes, though it cannot detect factually stale kernel text.
- The PR body was retrieved through the connected GitHub reader after the requested `gh` command failed to connect. The terminal review and full 4,314-line diff were read.

Tests ran sequentially using:

```sh
PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -m unittest tests.<module>
```

The grep-selected set includes all **23 direct-import modules**, all touched test modules, and seven additional textual matches. Counts:

| Module (`tests.` prefix omitted) | Tests | Result |
|---|---:|---|
| test_arm_readiness_evidence_author | 24 | PASS |
| test_analysis_finalizer | 16 | PASS |
| test_analysis_integration | 116 | PASS |
| test_authentication_io | 22 | PASS |
| test_bracket_binding_cli | 19 | PASS |
| test_calibration_bracketing | 92 | PASS, 1 skip |
| test_calibration_exits | 47 | PASS |
| test_calibration_ledger | 92 | PASS, 1 skip |
| test_calibration_ledger_custody | 29 | PASS |
| test_calibration_live_three_window | 23 | PASS, 3 skips |
| test_calibration_writer_crash_matrix | 20 | PASS |
| test_custody_mode_inventory | 7 | PASS |
| test_d078_reason_registry | 14 | PASS |
| test_d117_v3_family | 5 | PASS |
| test_epoch_continuation | 63 | PASS |
| test_epoch_equivalence_check | 26 | PASS |
| test_floor_extraction | 170 | PASS |
| test_floor_mint_pinsets_schema | 1 | PASS |
| test_issue_calibration_acceptance_generation | 114 | 1 environment failure |
| test_mint_floor_artifact_generalized | 83 | PASS, 2 skips |
| test_mint_policy_resolver_guard | 1 | PASS |
| test_powermetrics_fiducial | 75 | PASS |
| test_reissue_calibration_acceptance | 6 | PASS |
| test_run_campaign | 293 | PASS |
| test_schemas | 40 | PASS, 1 skip |
| test_validate_powermetrics_fiducial | 12 | PASS |
| test_validate_powermetrics_fiducial_derivation_only | 13 | PASS |
| test_whole_window | 58 | PASS |
| test_whole_window_selection | 57 | PASS |
| test_write_derivation_night_inputs | 16 | PASS |
| **Total** | **1,554** | **1 failure, 0 errors, 8 skips** |

Logs and per-module results: [results.jsonl](/tmp/pr320-integration-baf7b900/results.jsonl).

## Residual risk

The issuer failure is at `tests/test_issue_calibration_acceptance_generation.py:346`: `os_build` is `None` because `sysctl` returns `Operation not permitted`. The isolated test reproduces it. This is an environment verification gap, not a #320 regression.

For the previously reported readiness timeout: the earlier attempt reportedly failed once and passed in isolation. **This run passed the entire 24-test module and the isolated timeout test.**

No full-suite replay or hardware validation was performed. No repository files changed; HEAD and `origin/main` remain `baf7b900`, with a clean worktree.

**VERDICT: FOLLOW-UP NEEDED — PASS-route runbook; post-merge bookkeeping; lead-owned identity-probe verification.**