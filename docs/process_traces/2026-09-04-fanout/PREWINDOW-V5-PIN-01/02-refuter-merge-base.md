```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "The selector retarget works and its direct rollback is caught, but the new source-parsing regression can pass while the CLI still executes the retired family.",
  "workspace": {
    "base_requested": "098ad945",
    "base_mode": "exact",
    "head_start": "098ad9459329254bf46b409b497bd430c1241089",
    "head_end": "098ad9459329254bf46b409b497bd430c1241089",
    "upstream_end": "ec8f780337326f82feb1848a972c4746612da6cc",
    "branch": "feat/2026-09-04-fan-PREWINDOW-V5-PIN-01"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/PREWINDOW-V5-PIN-01/02-refuter-merge-base.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "gauntlet": "NOT LANDABLE",
    "findings": [
      {
        "id": "R1",
        "severity": "blocker",
        "location": "tests/test_capture_t0_step.py:894",
        "text": "The new regression parses all selector-looking source lines into a dict instead of executing the CLI. A later unreachable selector table overrides the executed assignments in that dict, so the test can pass while --window still selects the retired _v2 roots; it does not establish the required live-versus-stale execution behavior.",
        "counterfactual": "In a temp copy, restore all three executed _v2 assignments and add an unreachable case table containing the expected _v5 assignments. bash -n and the new test both pass; with an occupied live alpha root, the mutated CLI exits 0 and prints READY because it still executes the stale alpha selector."
      }
    ]
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
        "tail": ["Ran 32 tests in 49.008s", "", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 32 tests in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "lint",
      "cmd": "bash -n scripts/prewindow_check.sh && git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git diff --name-only $(git merge-base origin/main HEAD)..HEAD and compare with the implementation report WRITE_SCOPE plus the four magistrate-owned state paths",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "outside_scope=",
          "magistrate_owned_delta="
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "outside_scope=\\nmagistrate_owned_delta="
      }
    },
    {
      "id": "V4",
      "kind": "other",
      "cmd": "In /tmp/jw-prewindow-refuter.TYOZ8V, restore the three executed selectors to _v2, then run python3 -m unittest tests.test_capture_t0_step.CaptureT0StepTests.test_prewindow_runs_prefixes_accept_live_family_and_refuse_stale_family",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 1,
        "tail": ["Ran 1 test in 0.002s", "", "FAILED (failures=1)"]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED \\(failures=1\\)"
      }
    },
    {
      "id": "V5",
      "kind": "other",
      "cmd": "In the reverted temp copy, add an unreachable case table with the three live selectors, then run bash -n scripts/prewindow_check.sh && python3 -m unittest tests.test_capture_t0_step.CaptureT0StepTests.test_prewindow_runs_prefixes_accept_live_family_and_refuse_stale_family",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 0,
        "tail": ["Ran 1 test in 0.001s", "", "OK"]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED"
      }
    },
    {
      "id": "V6",
      "kind": "smoke",
      "cmd": "Run the spoofed temp CLI with controlled ps/uptime/pmset/df and an occupied runs_d117_floor_qwen3-1p7b_v5 root: /bin/bash scripts/prewindow_check.sh --window alpha",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 0,
        "tail": [
          "OK    runs roots absent or empty for window alpha under measurement checkout /private/tmp/jw-prewindow-refuter.TYOZ8V",
          "READY."
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "BLOCK runs roots already exist for window alpha"
      }
    },
    {
      "id": "V7",
      "kind": "smoke",
      "cmd": "Restore the landed script in the temp copy and rerun the controlled occupied-live-root alpha probe",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 1,
        "tail": [
          "BLOCK runs roots already exist for window alpha: /private/tmp/jw-prewindow-refuter.TYOZ8V/runs_d117_floor_qwen3-1p7b_v5",
          "NOT READY. Fix the BLOCK lines above, or re-run with --wait."
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "BLOCK runs roots already exist for window alpha"
      }
    }
  ],
  "flags": []
}
```

## Findings

R1 — blocker — `tests/test_capture_t0_step.py:894-927`: the landed literals are correct, and reverting only those literals makes the new test fail. The regression nevertheless observes regex-selected source text, not the selector the shell executes. A syntactically valid, unreachable second `case` with the live values makes `dict(re.findall(...))` retain those later values while the first, executed `case` remains `_v2`. Under that mutation the test passed, and the CLI returned `READY` while an occupied live-family alpha root existed. Replace or supplement this with a CLI-driven regression using controlled command fixtures and real live/stale root inputs; it must fail when the executed selector is reverted even if dead matching text remains.

Evidence: HEAD was exactly `098ad9459329254bf46b409b497bd430c1241089`. The mission merge base was `b0ed6991c11f3a515ad293760c6dfc031adda8e1`; its three-path delta exactly matched the implementation report's WRITE_SCOPE. `RUN_STATE.md`, `TASK_QUEUE.md`, `docs/process/state_kernel.json`, and `docs/decision_log.md` had no delta. Both claimed test modules passed (32 tests), shell syntax passed, and the direct rollback counterfactual failed as intended.

No previous refuter verdict was present in the mission directory or reachable Git history. The explicitly relevant non-staleness re-tests therefore stand on executed evidence: false-counterfactual concern is closed by V4; spoofable CLI observation remains open by V5; accepted occupied live-root behavior exists only under that spoof and is confirmed by V6; the landed production script itself correctly refuses the occupied live root by V7. No trusted-mutable-ID defect was found: the expected live IDs are read from the governed registry, but the missing execution binding remains R1.

## Residual risk

The focused preflight covered only the two claimed modules and alpha for the adversarial CLI probe. The same shared parser and selector structure serves beta and gamma, so R1 applies to all three; no whole-suite or quiet-machine work was run.
