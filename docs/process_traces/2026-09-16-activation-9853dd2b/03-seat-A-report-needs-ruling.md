```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "NEEDS_RULING: stage-1 registry changes are prepared, but mandatory commits require Git metadata writes denied by the sandbox.",
  "workspace": {
    "base_requested": "3015cb392b5d97b89e88d8dda2aaf67ea40b8b48",
    "base_mode": "exact",
    "head_start": "3015cb392b5d97b89e88d8dda2aaf67ea40b8b48",
    "head_end": "3015cb392b5d97b89e88d8dda2aaf67ea40b8b48",
    "upstream_end": "3015cb392b5d97b89e88d8dda2aaf67ea40b8b48",
    "branch": "feat/2026-09-16-reserve-hang-core"
  },
  "pathspec": [
    "joulewise/calibration_exits.py",
    "tests/test_calibration_exits.py",
    "docs/contracts/calibration_ledger_append.md",
    "docs/phase_2/window_runbook.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "partial",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_calibration_exits.RefusalInventoryTests.test_generated_contract_projection_and_runbook_anchors_are_fresh",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          ".",
          "----------------------------------------------------------------------",
          "Ran 1 test in 0.001s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V2",
      "kind": "other",
      "cmd": "git add joulewise/calibration_exits.py tests/test_calibration_exits.py docs/contracts/calibration_ledger_append.md docs/phase_2/window_runbook.md && git commit -m 'Register the operational custody timeout refusal'",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 128,
        "tail": [
          "fatal: Unable to create '/Users/edr/code/JouleWise/.git/worktrees/JouleWise-wt-rh-core/index.lock': Operation not permitted"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Register the operational custody timeout refusal"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git diff --check && git diff --stat && git status --short && git log --oneline 3015cb39..HEAD && git rev-parse HEAD origin/main && git branch --show-current",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "4 files changed, 10 insertions(+)",
          " M docs/contracts/calibration_ledger_append.md",
          " M docs/phase_2/window_runbook.md",
          " M joulewise/calibration_exits.py",
          " M tests/test_calibration_exits.py",
          "3015cb392b5d97b89e88d8dda2aaf67ea40b8b48",
          "3015cb392b5d97b89e88d8dda2aaf67ea40b8b48",
          "feat/2026-09-16-reserve-hang-core"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "feat/2026-09-16-reserve-hang-core"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "blocking",
      "text": "Normal git add failed before staging. Worktree Git metadata resides beneath the frozen canonical root, outside writable sandbox roots. No bypass was attempted; no commits were created.",
      "needs": "Lead must provide a runner permitting ordinary Git metadata writes for this worktree, or explicitly waive worker commits and own them."
    },
    {
      "id": "F2",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "NEEDS_RULING: required per-stage commits cannot be performed under current filesystem permissions. Options are resume with narrowly authorized Git metadata access, or continue without worker commits. Recommend the former.",
      "needs": "Resolve the Git metadata authority/environment conflict and resume this session."
    },
    {
      "id": "F3",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "Only the generated projection check passed. The new parameterized public-CLI witness is registered but depends on the unimplemented custody-budget flag. Stages 2–7, requested combined suite, quick tier, compileall, and counterfactual evidence remain incomplete. Final tree contains four authorized uncommitted files.",
      "needs": "After resolving F1, finish the implementation and run all requested verification before acceptance."
    }
  ]
}
```