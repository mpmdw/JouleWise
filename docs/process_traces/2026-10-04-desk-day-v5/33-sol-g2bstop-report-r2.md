```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Updated the termination regression; all requested checks completed with only the confirmed pre-existing timeout.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": "00947ca2eee989c71204dfe850f0ff574bffa690",
    "head_end": "00947ca2eee989c71204dfe850f0ff574bffa690",
    "upstream_end": "00947ca2eee989c71204dfe850f0ff574bffa690",
    "branch": "feat/2026-10-04-g2b-one-block-stop"
  },
  "pathspec": [
    "tests/test_check_window_provenance.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-g2bstop2 python3 -m unittest -v tests.test_check_window_provenance tests.test_run_campaign_max_blocks tests.test_gen_g2_phase_d tests.test_run_campaign > /tmp/dd5-g2bstop2/requested-tests.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["FAILED (errors=1)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^OK(?: \\(skipped=\\d+\\))?$"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "cd /tmp/dd5-g2bstop2/base && PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-g2bstop2 python3 -m unittest -v tests.test_run_campaign.RunCampaignTests.test_campaign_provenance_records_first_run_exemption_and_unknown_mock_gate > /tmp/dd5-g2bstop2/baseline-first-run.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["FAILED (errors=1)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^OK$"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-g2bstop2 python3 scripts/gen_g2_phase_d.py --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["PASS generated Phase D matches pinned runbook bytes"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^PASS generated Phase D matches pinned runbook bytes$"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git diff --check",
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
      "id": "V5",
      "kind": "other",
      "cmd": "git add -- tests/test_check_window_provenance.py",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 128,
        "tail": [
          "fatal: Unable to create '/Users/edr/code/JouleWise/.git/worktrees/JouleWise-wt-dd5-g2bstop/index.lock': Operation not permitted"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    }
  ],
  "flags": [
    {
      "id": "F2",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "The first-run provenance test timed out after 60 seconds both in an isolated archive of 8fa002f77db7af1e261a30e3787e38af2ab5e946 and in the requested branch run. Left unchanged as instructed.",
      "needs": ""
    },
    {
      "id": "F3",
      "kind": "environment",
      "level": "nonblocking",
      "text": "Sandbox denied Git index.lock creation. The authorized change remains unstaged and uncommitted; nothing was pushed.",
      "needs": ""
    }
  ]
}
```

## Change

Replaced SIGINT/130 assertions with rc 3, `--max-blocks 1`, and the terminal `max_blocks_reached` contract for one complete strict-valid A/B/B/A block. Retained every other assertion.

The checker itself contains no SIGINT/130 expectation, so it required no change.

## Verification notes

All 325 requested tests completed: 324 passed; the sole error was the 60-second timeout reproduced at `8fa002f7`. The generator check passed. Validation used the requested modules for this assertion-only change.

Git staging was denied by the sandbox, so changes remain uncommitted. Nothing was pushed; no processes were detached.