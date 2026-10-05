```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "REVIEW: FAIL — 11 restore-ON rewordings pass the new clock-policy row; requested tests and historical compatibility checks pass.",
  "workspace": {
    "base_requested": "85d67b12",
    "base_mode": "exact",
    "head_start": "3180dafb81eb1b73a9265cb533746eb825fa7df5",
    "head_end": "3180dafb81eb1b73a9265cb533746eb825fa7df5",
    "upstream_end": "85d67b129ba4202fe968e177a3f5d166076250ea",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "result": "FAIL",
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "path": "joulewise/arm_readiness_evidence.py",
        "line": 848,
        "title": "Contradictory restore-ON instructions bypass the doctrine guard",
        "evidence": "11 of 19 inserted restore instructions derive clock.network_time_policy.v1 and evaluate the freeze clock-policy row as PASS.",
        "recommendation": "Reject these contradictions and add adversarial regressions before merging."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "env TMPDIR=/tmp/dd5-dprev PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -m pytest -q -p no:cacheprovider -o cache_dir=/tmp/dd5-dprev/pc tests/test_arm_readiness_evidence.py tests/test_arm_readiness_schemas.py tests/test_receipt_histsem.py tests/test_arm_readiness_registry.py tests/test_docs_freshness.py > /tmp/dd5-dprev/pytest.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["176 passed, 1 skipped, 9 warnings, 1080 subtests passed in 4305.87s (1:11:45)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "176 passed, 1 skipped, .*1080 subtests passed"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "env TMPDIR=/tmp/dd5-dprev PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python /tmp/dd5-dprev/probe.py > /tmp/dd5-dprev/probe.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["SUMMARY: 25 cases; 11 unexpected PASS"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^SUMMARY: 25 cases; 0 unexpected PASS$"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "env TMPDIR=/tmp/dd5-dprev PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -m pytest -q -p no:cacheprovider -o cache_dir=/tmp/dd5-dprev/pc tests/test_arm_readiness_evidence_author.py::ArmReadinessEvidenceAuthorTests::test_authored_evidence_makes_synthetic_pack_freeze_pass > /tmp/dd5-dprev/freeze.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["1 passed, 3 warnings, 3 subtests passed in 134.10s (0:02:14)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "1 passed, .*3 subtests passed"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git diff --exit-code 85d67b12 3180dafb -- tests/fixtures docs/process_traces configs/arm_readiness/d117_row_registry_v1.json configs/arm_readiness/legacy_receipt_histsem_pinset_v1.json configs/campaigns",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "git diff --stat 85d67b12 3180dafb -- tests/fixtures configs docs/process_traces",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          " configs/arm_readiness/d117_row_registry_v2.json | 12 ++++++------",
          " 1 file changed, 6 insertions(+), 6 deletions(-)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "1 file changed, 6 insertions"
      }
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "rg -n 'clock\\.restore_recipe' scripts joulewise configs docs/phase_2 | sort > /tmp/dd5-dprev/restore-census.log && tail -n 3 /tmp/dd5-dprev/restore-census.log",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "docs/phase_2/window_runbook.md:640:harmless. The live v2 registry prospectively replaces `clock.restore_recipe`",
          "joulewise/arm_readiness.py:1158:    \"clock.restore_recipe.v1\": \"DOCTRINE_PIN\",",
          "joulewise/arm_readiness.py:974:    \"clock.restore_recipe.v1\": {"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "clock\\.restore_recipe\\.v1"
      }
    }
  ],
  "flags": []
}
```

## Findings

REVIEW: FAIL

**F1 — BLOCKER:** The [restore guard](/Users/edr/code/JouleWise-wt-dd5-dprev/joulewise/arm_readiness_evidence.py:848) accepts contradictory ON instructions while emitting `restore_on_after_window: false` and a PASS freeze clock-policy row. This falsely certifies the doctrine intended to prevent clock steps.

All 11 slipped variants follow; `\n` denotes a tested line break:

- `After the window closes, turn network time back on.`
- `Turn network time back on after the window closes.`
- `Set network time ON again after close-out.`
- `After close-out, set network time ON again.`
- `After both backups, turn **network time** back\n  **ON**.`
- ``Set `network time` **ON** again\n  after **close-out**.``
- `Re-enable "automatic network time" after the window.`
- `Enable automatic network time after the window.`
- `On completion of the verdict and backups, switch network time on.`
- `After completing backups, set using network time to ON.`
- ``After the window closes, run `/usr/bin/sudo -n /usr/sbin/systemsetup -setusingnetworktime on`.``

Reproduction: [probe script](/tmp/dd5-dprev/probe.py), [case results](/tmp/dd5-dprev/probe-results.json). Fix the guard and add regressions before merging.

Other checks passed:

- Current-runbook synthetic freeze and ARM re-derivation pass. Removing each of the five required doctrine clauses refuses.
- Historical restore predicates and the archival corpus verify; historical receipt, fixture, registry-v1 and pin bytes are unchanged.
- No searched live consumer requires `clock.restore_recipe` for a new freeze.
- Requested suite: **176 passed, 1 skipped; 1,080 subtests passed**. Additional end-to-end freeze test passed.

No repository files changed; HEAD and worktree remain unchanged. All launched checks have finished.

## Residual risk

These were procedural and fixture checks. The full readiness suite and live hardware verification remain lead-owned.