```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "clean",
  "completion": "complete",
  "summary": "The mission-only merge-base delta is scope-clean, its focused checks pass, and the strengthened regression discriminates every governed process alternative.",
  "workspace": {
    "base_requested": "b0ed6991c11f3a515ad293760c6dfc031adda8e1",
    "base_mode": "exact",
    "head_start": "f847ff420a852c0ad65e725b6ca5e94b41670c49",
    "head_end": "f847ff420a852c0ad65e725b6ca5e94b41670c49",
    "upstream_end": "a39e33a20561eed48381fa91d42e7c7bfcdd3adb",
    "branch": "feat/2026-09-04-fan-PREWINDOW-REGEX-01"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/PREWINDOW-REGEX-01/02-refuter-merge-base.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "gauntlet": "LANDABLE",
    "findings": []
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "base=$(git merge-base origin/main HEAD); git diff --name-status \"$base\"..HEAD; git diff --exit-code \"$base\"..HEAD -- RUN_STATE.md TASK_QUEUE.md docs/process/state_kernel.json docs/decision_log.md && printf 'state paths: no delta\\n'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "A\tdocs/process_traces/2026-09-04-fanout/PREWINDOW-REGEX-01/01-sol-report.md",
          "M\ttests/test_prewindow_check.py",
          "state paths: no delta"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "state paths: no delta$"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_prewindow_check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 1 test in 0.979s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK$"
      }
    },
    {
      "id": "V3",
      "kind": "lint",
      "cmd": "/bin/bash -n scripts/prewindow_check.sh",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "ok=1; for spec in 'old-pattern::codex exec|codex-run|run_campaign|window-chain' 'drop-codex::claude|t3|mcp-server|run_campaign|window-chain' 'drop-claude::codex|t3|mcp-server|run_campaign|window-chain' 'drop-t3::codex|claude|mcp-server|run_campaign|window-chain' 'drop-mcp-server::codex|claude|t3|run_campaign|window-chain'; do label=${spec%%::*}; replacement=${spec#*::}; tmp=$(mktemp -d /private/tmp/prewindow-regex-cf.XXXXXX) || exit 2; git archive HEAD tests/test_prewindow_check.py scripts/prewindow_check.sh | tar -x -C \"$tmp\"; REPLACEMENT=\"$replacement\" perl -0pi -e 's/codex\\|claude\\|t3\\|mcp-server\\|run_campaign\\|window-chain/$ENV{REPLACEMENT}/' \"$tmp/scripts/prewindow_check.sh\"; (cd \"$tmp\" && python3 -m unittest discover -s tests -p 'test_prewindow_check.py') >/dev/null 2>&1; mutation_rc=$?; printf '%s test_exit=%s\\n' \"$label\" \"$mutation_rc\"; [ \"$mutation_rc\" -eq 1 ] || ok=0; done; [ \"$ok\" -eq 1 ]",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "old-pattern test_exit=1",
          "drop-codex test_exit=1",
          "drop-claude test_exit=1",
          "drop-t3 test_exit=1",
          "drop-mcp-server test_exit=1"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "drop-mcp-server test_exit=1$"
      }
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "ok=1; for spec in 'drop-codex::claude|t3|mcp-server|run_campaign|window-chain' 'drop-t3::codex|claude|mcp-server|run_campaign|window-chain'; do label=${spec%%::*}; replacement=${spec#*::}; tmp=$(mktemp -d /private/tmp/prewindow-regex-old.XXXXXX) || exit 2; git archive b0ed6991c11f3a515ad293760c6dfc031adda8e1 tests/test_prewindow_check.py scripts/prewindow_check.sh | tar -x -C \"$tmp\"; REPLACEMENT=\"$replacement\" perl -0pi -e 's/codex\\|claude\\|t3\\|mcp-server\\|run_campaign\\|window-chain/$ENV{REPLACEMENT}/' \"$tmp/scripts/prewindow_check.sh\"; (cd \"$tmp\" && python3 -m unittest discover -s tests -p 'test_prewindow_check.py') >/dev/null 2>&1; mutation_rc=$?; printf 'old-test-%s test_exit=%s\\n' \"$label\" \"$mutation_rc\"; [ \"$mutation_rc\" -eq 0 ] || ok=0; done; [ \"$ok\" -eq 1 ]",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "old-test-drop-codex test_exit=0",
          "old-test-drop-t3 test_exit=0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "old-test-drop-t3 test_exit=0$"
      }
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "base=$(git merge-base origin/main HEAD); git diff --check \"$base\"..HEAD",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    }
  ],
  "flags": []
}
```

## Findings

None. The merge-base delta contains only `tests/test_prewindow_check.py` and the seat report, both within the seat's declared scope. `RUN_STATE.md`, `TASK_QUEUE.md`, `docs/process/state_kernel.json`, and `docs/decision_log.md` have no delta.

The focused module and the claimed shell syntax check pass. The four independent counterfactual inputs are `codex app-server`, `claude daemon`, `t3 worker`, and `mcp-server`: deleting the corresponding alternative from the script in a temporary copy makes the new test fail with the observed count dropping from four to three. Restoring the former narrow pattern makes the script report `READY` and the test fail. Conversely, the merge-base test remains green when either `codex` or `t3` is removed, reproducing the old false-green and proving that the mission delta cures it.

No previous refuter verdict is present in this mission directory. Accordingly, there is no prior mission-specific spoofable-CLI, mutable-identifier, or occupied-root blocker to re-test; the false-counterfactual concern evidenced by the seat report is cured.

## Residual risk

None within the reviewed mission delta. Live quiet-machine execution remains lead-owned and was neither needed nor permitted for this fixture-only refinement.
