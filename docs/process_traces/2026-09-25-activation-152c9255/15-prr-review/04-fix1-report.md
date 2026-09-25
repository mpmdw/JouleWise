```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Applied the PR-R fix-round rulings within write scope; the requested test run has one sandbox-dependent live-probe failure.",
  "workspace": {
    "base_requested": "3c52518dbe9d9541d0134f628a4dfbc4d0465465",
    "base_mode": "exact",
    "head_start": "3c52518dbe9d9541d0134f628a4dfbc4d0465465",
    "head_end": "3c52518dbe9d9541d0134f628a4dfbc4d0465465",
    "upstream_end": "c034a56ff6684a28fc3c5af32c7da3e01c7e0e95",
    "branch": "feat/2026-09-25-acc-registration-rev5"
  },
  "pathspec": [
    "configs/calibration/observation_dispositions.json",
    "configs/calibration/preregistration_d079_epoch_25g83_rev1.md",
    "docs/calibration/acc_25g83_rev5_simulation.md",
    "docs/decision_log.md",
    "joulewise/calibration_bracketing.py",
    "scripts/issue_calibration_acceptance_generation.py",
    "scripts/sim_acc_25g83_rev5.py",
    "tests/test_acc_25g83_rev5.py",
    "tests/test_issue_calibration_acceptance_generation.py",
    "tests/test_preregistration_chain_digest.py"
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
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_acc_25g83_rev5 tests.test_preregistration_chain_digest",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 17 tests in 10.711s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 17 tests.*OK"}
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_issue_calibration_acceptance_generation tests.test_calibration_bracketing tests.test_reissue_calibration_acceptance tests.test_preregistration_chain_digest tests.test_acc_25g83_rev5 tests.test_calibration_cadence_report tests.test_calibration_exits tests.test_gen_state",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["AssertionError: None is not an instance of <class 'str'>", "Ran 326 tests in 574.193s", "FAILED (failures=1, skipped=1)"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 326 tests.*OK"}
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 scripts/gen_state.py --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "python3 - <<'PY'\nimport hashlib, subprocess\nfrom pathlib import Path\npaths = ('joulewise/powermetrics_fiducial.py', 'joulewise/uncertainty_evidence.py', 'joulewise/adapters/powermetrics.py', 'joulewise/reduce.py')\nfor path in paths:\n    old = subprocess.check_output(('git', 'show', f'c034a56f:{path}'))\n    new = Path(path).read_bytes()\n    print(f'{path} {hashlib.sha256(new).hexdigest()} {\"MATCH\" if old == new else \"MISMATCH\"}')\nassert all(subprocess.check_output(('git', 'show', f'c034a56f:{path}')) == Path(path).read_bytes() for path in paths)\nPY",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["joulewise/powermetrics_fiducial.py 386e825440e02bb0720e7b74f0f7503d785fb543a08c45386014eeb4216bab92 MATCH", "joulewise/uncertainty_evidence.py b583f35affb33394532424295ac70261b895e1b6f2faa6ec87ee89c79cd94ae8 MATCH", "joulewise/adapters/powermetrics.py 70f47086b2445e88d0cb25ed2d47751dfd99843d0cf1e149f2fe630c5116e5e4 MATCH", "joulewise/reduce.py 7b9c0d28869040229e113ea2d40ecc69966075fd34052fbb51cfaffbd9ff9fcc MATCH"]},
      "expected": {"exit_code": 0, "tail_regex": "joulewise/reduce.py [0-9a-f]{64} MATCH"}
    },
    {
      "id": "V5",
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
      "kind": "environment",
      "level": "blocking",
      "text": "The restored live sysctl test fails because this sandbox returns no os_build; its assertion receives None.",
      "needs": "Lead rerun the live-probe test where macOS sysctl is available."
    }
  ]
}
```

## Change

Bound all 11 dispositions to the dated decision ID, restored the unique preregistration pin guard, made seal fixtures work across placeholder replacement, and applied the remaining in-scope code, text, and test fixes. The branch remains uncommitted.

## Verification notes

The requested test run’s sole failure is the restored live identity probe. The four pinned files are byte-identical to c034a56f.

## Residual risk

PR-L pin sealing and the ruling file’s landing on main remain lead-owned merge gates.