```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "clean",
  "completion": "complete",
  "summary": "Executed census-cure checks a–h; no new defects; 297 focused tests passed; workspace clean.",
  "workspace": {
    "base_requested": "93870527",
    "base_mode": "exact",
    "head_start": "07681e95fa53fd7c80a02ea661d15b2a7ffe604d",
    "head_end": "07681e95fa53fd7c80a02ea661d15b2a7ffe604d",
    "upstream_end": "07681e95fa53fd7c80a02ea661d15b2a7ffe604d",
    "branch": "int/2026-09-08-d176-seats-2-3"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {"findings": []},
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/private/tmp python3 -B /tmp/d176_delta_audit.py > /tmp/d176-delta-harness.log 2>&1",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["AUDIT_HARNESS_PASS"]},
      "expected": {"exit_code": 0, "tail_regex": "AUDIT_HARNESS_PASS"}
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/private/tmp python3 -B -m unittest tests.test_arm_readiness.CensusCureLaunchTests tests.test_arm_readiness.PackNightConsumerTests tests.test_arm_readiness_schemas tests.test_rehearse_t0_unattended tests.test_run_night tests.test_magistrate_watchdog tests.test_night_gate tests.test_launch_window.PackNightLaunchBoundaryTests > /tmp/d176-delta-suite.log 2>&1",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 297 tests in 30.771s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git diff --check 93870527 07681e95; python3 -B -c 'import subprocess; s=subprocess.check_output([\"git\",\"status\",\"--short\"]); assert s == b\"\", repr(s); print(\"WORKTREE_CLEAN\"); print(subprocess.check_output([\"git\",\"rev-parse\",\"HEAD\",\"@{upstream}\",\"main\"]).decode(), end=\"\"); print(subprocess.check_output([\"git\",\"branch\",\"--show-current\"]).decode(), end=\"\")'",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["WORKTREE_CLEAN", "07681e95fa53fd7c80a02ea661d15b2a7ffe604d", "07681e95fa53fd7c80a02ea661d15b2a7ffe604d", "99a42edbbb08098b7e4a0835e9e2f15cc51cd0b5", "int/2026-09-08-d176-seats-2-3"]},
      "expected": {"exit_code": 0, "tail_regex": "WORKTREE_CLEAN"}
    }
  ],
  "flags": []
}
```

## Findings

None. Executed results below; refusal codes are `launch_go_receipt_invalid` unless stated otherwise.

- **(a) PASS/KILLED:** Actual running checkout clears the real resolver with shipped inventory. Planting it into temporary inventory refuses at gate and consumer: `rehearsal_roots_not_disjoint: measurement_root`. A named temporary Git checkout with `runs/` passes both boundaries using real inventory authentication.
- **(b) KILLED:** Another checkout as measurement root refuses at both boundaries: `measurement_root: launcher is not the planned clone`.
- **(c) KILLED:** Uninventoried checkout lacking the reviewed basename prefix refuses at both boundaries: `rehearsal_clone_prefix_invalid: measurement_root`.
- **(d) KILLED:** Real local Git commit deleting an inventory entry refuses pre-ARM preparation with `production-root census incomplete`; gate and full consumption refuse with `rehearsal_roots_not_disjoint`. No consumption receipt is written. A stale measurement-head pin separately raises `ValueError: measurement_head: checkout differs from plan`.
- **(e) KILLED:** Independently planting inventory `custody_root` and `ledger_path` equal to rehearsal custody triggers DISJOINT refusal at both boundaries: `rehearsal_roots_not_disjoint`.
- **(f) PASS:** `DIAGNOSTIC_NO_PACK` parses through the real watchdog loader and yields `FENCED`; driver emits diagnostic `GO`, reaches one chain spawn, and returns 0. Inventory-reader and resolver call counts remain zero.
- **(g) PASS:** Integrated driver→ARM→GO→launcher→consumption→replay fixture passes within the 297-test suite.
- **(h) PASS:** Exact source bytes match `main` for watchdog, T-0 author, ARM mint/verifier, `validate_receipt`, receipt/condition keys, condition IDs, and statuses.

Also confirmed no `CLONE_DERIVED` specifications and complete resolution of every shipped non-null custody/ledger locator.

## Residual risk

Software fixtures retain synthetic ARM/T-0/probe/process boundaries; this is not live rehearsal validation. Temporary launcher coordinates are injected, while Git inventory authentication and census resolution execute real code. The actual checkout lacks `runs/`; the temporary checkout covers that existence case. All writes stayed under `/tmp`; final `git status --short` was asserted empty.