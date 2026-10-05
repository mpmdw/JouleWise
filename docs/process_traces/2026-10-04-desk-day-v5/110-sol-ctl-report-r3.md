```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Implemented plan-pinned auxiliary G2-b attachment eligibility; all requested tests pass; canonical verification remains incomplete.",
  "workspace": {
    "base_requested": "32ee573a",
    "base_mode": "exact",
    "head_start": "32ee573a060bd65b493947fe4182f167c8a39b0a",
    "head_end": "32ee573a060bd65b493947fe4182f167c8a39b0a",
    "upstream_end": "32ee573a060bd65b493947fe4182f167c8a39b0a",
    "branch": "feat/2026-10-05-controller-g2b-attach-battery"
  },
  "pathspec": [
    "joulewise/controller.py",
    "joulewise/bundle.py",
    "tests/test_controller_g2b_attachment.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp/dd5-ctl3 PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_controller_g2b_attachment tests.test_g2a_calibration_attachment tests.test_controller tests.test_controller_retry_backoff tests.test_controller_battery_float tests.test_battery_float tests.test_battery_float_sweep tests.test_battery_float_consumers > /tmp/dd5-ctl3/focused.log 2>&1",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["OK"]},
      "expected": {"exit_code": 0, "tail_regex": "(?m)^OK$"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "TMPDIR=/tmp/dd5-ctl3 PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_controller_g2b_attachment.G2bAttachmentTests.test_auxiliary_directories_are_read_from_authenticated_plan tests.test_controller_g2b_attachment.G2bAttachmentTests.test_floor_plan_manifest_descriptors_assign_auxiliary_roots > /tmp/dd5-ctl3/plan-variants.log 2>&1",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["OK"]},
      "expected": {"exit_code": 0, "tail_regex": "(?m)^OK$"}
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "TMPDIR=/tmp/dd5-ctl3 PYTHONDONTWRITEBYTECODE=1 python3 /tmp/dd5-ctl3/check_plan_inputs.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Verified 57 tracked auxiliary configs across 3 plan trees: expected roots accepted; wrong roots refused."]
      },
      "expected": {"exit_code": 0, "tail_regex": "Verified 57 tracked auxiliary configs across 3 plan trees"}
    },
    {
      "id": "V4",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp/dd5-ctl3 PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests > /tmp/dd5-ctl3/full-suite.log 2>&1",
      "cwd": ".",
      "observed": {"result": "not_run", "exit_code": 130, "tail": ["KeyboardInterrupt"]},
      "expected": {"exit_code": 0, "tail_regex": "(?m)^OK"}
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
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The additional canonical suite was started, then interrupted to keep this delegated round bounded. It has no completed verdict. All specified tests passed.",
      "needs": "Lead: complete canonical verification before merge."
    }
  ]
}
```

## Change

Auxiliary configs now qualify through their authenticated plan’s external-member path and SHA-256, dispatched stage and assigned root. Both eligibility paths share the CLI source-equality check. Directory names are read from the plan.

All 12 bound-corpus configs and 7 window references ATTACH. Wrong roots, unpinned paths, changed bytes, differing running configs and invalid CLI sources are REFUSED. Round 2’s F1 regressions remain green.

**Clause map — delta**

C = `joulewise/controller.py`; B = `joulewise/bundle.py`; T = `tests/test_controller_g2b_attachment.py`.

| Production site | Biting assertion | Counterfactual |
|---|---|---|
| C:622 | T:192, `test_tracked_bound_corpus_and_all_window_references_attach` | Remove auxiliary eligibility |
| C:564 | T:212, `test_unpinned_auxiliary_path_is_refused` | Remove path comparison |
| C:565 | T:219, `test_pinned_auxiliary_with_changed_bytes_is_refused` | Remove digest comparison |
| C:584 | T:204, `test_auxiliary_in_wrong_root_is_refused` | Remove root-role comparison |
| B:91, B:97 | T:231, `test_auxiliary_requires_run_cli_and_nonsymlink_source` | Remove command or symlink guard |
| B:110 | T:225, `test_auxiliary_running_config_must_equal_cli_file` | Remove config equality |
| C:556 | T:239, `test_auxiliary_directories_are_read_from_authenticated_plan` | Hard-code current directories |

Changes are uncommitted; HEAD and upstream remain `32ee573a`.

## Verification notes

The requested combined run passed 258 tests; the two supplemental plan-format tests also passed. The canonical suite was interrupted and remains a lead verification gate.

Next: review the uncommitted delta for PR #482 and complete canonical verification.

## Residual risk

Evidence uses tracked config bytes and real stored calibration bytes with synthetic launch custody. Live G2-b validation remains lead-owned.