```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "clean",
  "completion": "complete",
  "summary": "CLEAN: d2e751df matches the ruled changes, adds no unrelated lane changes, and passes the requested checks.",
  "workspace": {
    "base_requested": "3fb98469",
    "base_mode": "exact",
    "head_start": "d2e751dfb5db634bda3152c2cf348adb2ddb7adc",
    "head_end": "d2e751dfb5db634bda3152c2cf348adb2ddb7adc",
    "upstream_end": "25cde215606599e1367fab8356fc05af74926527",
    "branch": "fix/2026-09-24-a291-merge-candidate"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "result": "CLEAN",
    "findings": [],
    "ruled_text": "Exact at the three production lines, import, AST assertions, and regression test body.",
    "other_changes": "Nine paths in the broader 3fb98469..d2e751df comparison came from the earlier main merge; no other post-review paths changed."
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git show --stat --oneline d2e751df && git show --format=fuller --no-ext-diff d2e751df",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "joulewise/scored_packer.py | 6 +++---",
          "tests/test_scored_packer.py | 32 ++++++++++++++++++++++++++++++++",
          "2 files changed, 35 insertions(+), 3 deletions(-)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "2 files changed, 35 insertions\\(\\+\\), 3 deletions\\(-\\)"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "cmp -s <(git diff 3fb98469 e3769062 -- joulewise tests scripts .github) <(git diff 3fb98469 f911fe3e -- joulewise tests scripts .github); echo prior_merge_patch_cmp_exit=$?; git diff --name-status e3769062 f911fe3e -- joulewise tests scripts .github; git merge-base main d2e751df; git status --short --branch",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "prior_merge_patch_cmp_exit=0",
          "25cde215606599e1367fab8356fc05af74926527",
          "## fix/2026-09-24-a291-merge-candidate...origin/fix/2026-09-24-a291-merge-candidate"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "prior_merge_patch_cmp_exit=0"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 -B -m unittest -v tests.test_scored_packer.ScoredPackerTests.test_a291_deep_nesting_refuses_inv_52_not_recursion_error tests.test_scored_packer.ScoredPackerTests.test_inv40_ast_seal_placement tests.test_scored_packer.ScoredPackerTests.test_r4c_derived_structure_ast tests.test_scored_packer.ScoredPackerTests.test_r5b_no_trusted_mutable_cache_ast tests.test_scored_packer.ScoredPackerTests.test_a291_parent_facts_and_conserve_read_the_view_ast tests.test_scored_packer.ScoredPackerTests.test_a291_packer_imports_nothing_from_tests_ast",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 6 tests in 8.507s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 6 tests in .*\\n\\nOK"
      }
    },
    {
      "id": "V4",
      "kind": "smoke",
      "cmd": "python3 -B - <<'PY'\nfrom tests.scored_case_generator import generate_case\nfrom joulewise.scored_packer import _seal\n\ncase = generate_case(291013, 0)\n\ndef deepest(value, depth=0, path='$'):\n    if isinstance(value, dict):\n        children = ((v, f'{path}.{k}') for k, v in value.items())\n    elif isinstance(value, list):\n        children = ((v, f'{path}[{i}]') for i, v in enumerate(value))\n    else:\n        return depth, path\n    return max((deepest(v, depth + 1, p) for v, p in children), default=(depth, path))\n\nfor label, roster in (('first', case.rosters[0]), ('final', case.rosters[-1])):\n    depth, path = deepest(roster)\n    assert _seal(case.reg, roster) is roster\n    print(f'{label}: depth={depth} path={path} blocks={len(roster[\"blocks\"])} envelopes={len(roster[\"envelopes\"])} events={len(roster[\"events\"])} seal=PASS')\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "first: depth=4 path=$.envelopes[9].blocks[2] blocks=60 envelopes=24 events=0 seal=PASS",
          "final: depth=5 path=$.events[9].observations[2].status blocks=62 envelopes=27 events=27 seal=PASS"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "final: depth=5 .* seal=PASS"
      }
    }
  ],
  "flags": []
}
```

## Findings

| ID | Severity | Finding |
|---|---|---|
| — | — | None. |

The nine other changed paths in `git diff 3fb98469 d2e751df -- joulewise tests scripts .github` are `joulewise/arm_retry.py`, `joulewise/night_gate.py`, `scripts/run_night.py`, and `tests/test_{arm_retry,gen_state,magistrate_watchdog,night_gate,night_kinds,run_night}.py`. Their patch was already present at `e3769062`; the later main merge added no changes under those pathspecs.

## Residual risk

A future programming error that raises `RecursionError` inside either catch block would also become `inv_52`. In the current code, the generator’s legal roster shape reaches depth 5 at most; its generated final roster sealed successfully.