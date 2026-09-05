```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Replaced the spoofable selector-source assertion with an executed-CLI live-versus-retired regression that survives the refuter's dead-table counterfactual.",
  "workspace": {
    "base_requested": "098ad945",
    "base_mode": "exact",
    "head_start": "098ad9459329254bf46b409b497bd430c1241089",
    "head_end": "098ad9459329254bf46b409b497bd430c1241089",
    "upstream_end": "098ad9459329254bf46b409b497bd430c1241089",
    "branch": "feat/2026-09-04-fan-PREWINDOW-V5-PIN-01"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/PREWINDOW-V5-PIN-01/03-sol-fix-round-1-report.md",
    "tests/test_capture_t0_step.py"
  ],
  "unowned_dirty": [
    "docs/process_traces/2026-09-04-fanout/PREWINDOW-V5-PIN-01/02-refuter-merge-base.md"
  ],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_capture_t0_step tests.test_prewindow_check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 32 tests in 39.862s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 32 tests in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "other",
      "cmd": "tmp_root=$(mktemp -d /tmp/jw-prewindow-fix1.XXXXXX) && mkdir -p \"$tmp_root/tests\" \"$tmp_root/scripts\" \"$tmp_root/configs/arm_readiness\" && cp tests/test_capture_t0_step.py \"$tmp_root/tests/test_capture_t0_step.py\" && cp scripts/prewindow_check.sh \"$tmp_root/scripts/prewindow_check.sh\" && cp configs/arm_readiness/d117_row_registry_v2.json \"$tmp_root/configs/arm_readiness/d117_row_registry_v2.json\" && sed -i.bak -e 's/runs_d117_floor_qwen3-1p7b_v5/runs_d117_floor_qwen25_1p5b_v2/' -e 's/runs_d117_floor_qwen3-8b_v5/runs_d117_floor_qwen25_7b_v2/' -e 's/runs_d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/runs_d117_contrast_qwen25_1p5b_vs_7b_v2/' \"$tmp_root/scripts/prewindow_check.sh\" && PYTHONPATH=. python3 \"$tmp_root/tests/test_capture_t0_step.py\" CaptureT0StepTests.test_prewindow_runs_prefixes_accept_live_family_and_refuse_stale_family; rc=$?; printf 'counterfactual_exit=%s\\n' \"$rc\"; exit \"$rc\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 1,
        "tail": [
          "Ran 1 test in 0.892s",
          "",
          "FAILED (failures=6)",
          "counterfactual_exit=1"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED \\(failures=6\\)\\ncounterfactual_exit=1"
      }
    },
    {
      "id": "V3",
      "kind": "lint",
      "cmd": "bash -n scripts/prewindow_check.sh && git diff --check",
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

## Change

R1 is cured at `tests/test_capture_t0_step.py:884`: the regression no longer parses selector-looking source lines into a dictionary. It copies the real shell script into a temporary measurement checkout, appends the refuter's syntactically valid but unreachable live-selector `case` table, supplies controlled `ps`, `uptime`, `pmset`, and `df` commands, and executes `/bin/bash scripts/prewindow_check.sh --window <profile>` for alpha, beta, and gamma.

Finding → cure → location:

| Finding | Cure | File:line |
|---|---|---|
| R1 blocker: dead matching text could override the source parser while the shell executed `_v2`. | Execute the copied CLI with the dead live table present; require each occupied live root to exit 1 with `BLOCK`/`NOT READY`, and require each retired-only occupied root to exit 0 with `READY`. | `tests/test_capture_t0_step.py:884` |
| R1 named counterfactual: restored `_v2` assignments plus an unreachable `_v5` table returned `READY` for an occupied live alpha root. | Replayed that exact mutation in a temporary copy. The live probes returned 0 instead of 1 and the retired probes returned 1 instead of 0, producing six assertion failures. | `tests/test_capture_t0_step.py:911`, `tests/test_capture_t0_step.py:956` |
| Production selector behavior must remain the ruled literal-only retarget. | No production change in this round; the executed alpha/beta/gamma selectors remain the live `_v5` prefixes. | `scripts/prewindow_check.sh:53` |

No new admission lane or gate semantic was introduced.

Magistrate-owned closure text (not applied here):

`| PREWINDOW-V5-PIN-01 | P1 Phase Gate | 2026-09-04 | Retarget the prewindow check's window pin from the retired campaign family to the live one. | COMPLETE after fix round 1: the alpha, beta, and gamma selectors name the registered Qwen3 _v5 runs roots, and an executed-CLI regression proves occupied live roots refuse while occupied retired-only roots do not block even when unreachable source text contains the expected live selectors. Evidence: docs/process_traces/2026-09-04-fanout/PREWINDOW-V5-PIN-01/03-sol-fix-round-1-report.md. |`

Remove `/tasks/PREWINDOW-V5-PIN-01` from `docs/process/state_kernel.json` when installing that completed row, then regenerate `TASK_QUEUE.md` and `RUN_STATE.md`. The current kernel acceptance sentence saying a live-family root “passes” and a stale-family root “refuses” should be corrected during that owned transaction to the occupied-root behavior demonstrated above.

## Verification notes

Per the preflight rule, only the two landing-related test modules were run; the repository-wide suite was not run. The counterfactual command's exit 1 is the expected successful mutation kill.
