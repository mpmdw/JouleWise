```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Retargeted the shared campaign-generator core to all three live D-117 v5 producers with empty non-self-bound byte diffs and a bypass counterfactual.",
  "workspace": {
    "base_requested": "f7d94d3b",
    "base_mode": "exact",
    "head_start": "f7d94d3b49f2494d7188849e5e32e532a4cffa32",
    "head_end": "f7d94d3b49f2494d7188849e5e32e532a4cffa32",
    "upstream_end": "7da20e28e795ac9aac41f774e4f5f7fa0ef29f5c",
    "branch": "feat/2026-09-04-fan-GENERATOR-CORE-01"
  },
  "pathspec": [
    "configs/campaigns/d117_contrast_v5/generate_configs.py",
    "configs/campaigns/d117_floor_qwen3-1p7b_v5/generate_configs.py",
    "configs/campaigns/d117_floor_qwen3-8b_v5/generate_configs.py",
    "docs/process_traces/2026-09-04-fanout/GENERATOR-CORE-01/03-sol-retarget-report.md",
    "docs/specs/generator_core.md",
    "joulewise/campaign_generator_core.py",
    "scripts/check_campaign_generator_core_parity.py",
    "tests/test_campaign_generator_core.py"
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
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_campaign_generator_core_parity.py --baseline-ref f7d94d3b",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "PARITY_DIFF_EMPTY generator=ALPHA files=120",
          "PARITY_DIFF_EMPTY generator=BETA files=120",
          "PARITY_DIFF_EMPTY generator=GAMMA files=112",
          "PARITY_OK generators=3 files=352 excluded=['generate_configs.py', 'plan_tree.json', 'plan_tree.sha256'] baseline=f7d94d3b"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "PARITY_DIFF_EMPTY generator=ALPHA files=120[\\s\\S]*PARITY_DIFF_EMPTY generator=BETA files=120[\\s\\S]*PARITY_DIFF_EMPTY generator=GAMMA files=112[\\s\\S]*PARITY_OK generators=3 files=352"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "set -o pipefail; PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_campaign_generator_core tests.test_d117_contrast_v5_pack tests.test_d117_floor_qwen3_v5_generate tests.test_issue_g2a_prefill_prompt_pin 2>&1 | tail -n 4 | sed -E 's/^Ran ([0-9]+) tests in .+$/Ran \\1 tests/'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "----------------------------------------------------------------------",
          "Ran 69 tests",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 69 tests[\\s\\S]*OK"
      }
    },
    {
      "id": "V3",
      "kind": "lint",
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
    }
  ],
  "flags": []
}
```

## Change

ALPHA, BETA, and GAMMA now import one shared implementation of canonical JSON
rendering, byte hashing and sidecars, pack inventory, and the generation
write-boundary validator. Main's reviewed GAMMA suite-manifest and exact-roster
hardening remains intact. The nine historical generators are untouched and
explicitly enumerated as custody snapshots.

The baseline and worktree producers generated into paired temporary roots. The
non-self-bound diff was empty for all 352 compared files. The only exclusions
were `generate_configs.py`, `plan_tree.json`, and `plan_tree.sha256`: the first
contains the changed import, while the latter two authenticate that source.

The named counterfactual is
`test_counterfactual_local_write_boundary_cannot_bypass_shared_core`: restoring
a local validator or another extracted helper in any one live producer fails
both function-object identity and AST local-definition checks.

## Verification notes

Per the preflight ruling, verification ran only the generator-focused test
modules selected by the `d117_contrast_v5` grep; the repository-wide suite was
not run. The unused draft identity factory was removed instead of being wired
without the scout-required five-state behavior proof; producer identity policy
and all scientific pins remain local and unchanged.
