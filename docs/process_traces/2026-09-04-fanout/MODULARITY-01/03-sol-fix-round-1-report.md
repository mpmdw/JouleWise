```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Cured all four MODULARITY-01 refuter blockers with exact counterfactual regressions and a green focused suite.",
  "workspace": {
    "base_requested": "99155bb4d00c95d494b508fb37ae1fa8ab79017f",
    "base_mode": "exact",
    "head_start": "99155bb4d00c95d494b508fb37ae1fa8ab79017f",
    "head_end": "99155bb4d00c95d494b508fb37ae1fa8ab79017f",
    "upstream_end": "99155bb4d00c95d494b508fb37ae1fa8ab79017f",
    "branch": "feat/2026-09-04-fan-MODULARITY-01"
  },
  "pathspec": [
    "configs/campaigns/p2_015_floors/generate_configs.py",
    "docs/design/modularity_01.md",
    "docs/process_traces/2026-09-04-fanout/MODULARITY-01/03-sol-fix-round-1-report.md",
    "joulewise/analysis_manifest.py",
    "joulewise/detection_floor_registry.py",
    "tests/test_modularity.py"
  ],
  "unowned_dirty": [
    "docs/process_traces/2026-09-04-fanout/MODULARITY-01/02-refuter-merge-base.md"
  ],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_modularity tests.test_analysis_manifest tests.test_generate_matrix tests.test_detection_floor tests.test_floor_extraction",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 382 tests in 15.292s",
          "OK (skipped=1)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 382 tests[\\s\\S]*OK \\(skipped=1\\)$"
      }
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "tmp=$(mktemp -d); printf '{\"stale\":true}\\n' > \"$tmp/stale.json\"; python3 configs/campaigns/p2_015_floors/generate_configs.py --campaign-spec configs/campaigns/p2_015_floors/campaign_spec.json --out-dir \"$tmp\"; rc=$?; if test -f \"$tmp/stale.json\"; then stale=yes; else stale=no; fi; count=$(find \"$tmp\" -type f | wc -l | tr -d ' '); printf 'EXIT_CODE=%s STALE_SURVIVES=%s FILE_COUNT=%s\\n' \"$rc\" \"$stale\" \"$count\"; test \"$rc\" -eq 2 && test \"$stale\" = yes && test \"$count\" -eq 1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "campaign specification error: output directory <TMP> is not empty; refusing to mix generated and pre-existing files",
          "EXIT_CODE=2 STALE_SURVIVES=yes FILE_COUNT=1"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "EXIT_CODE=2 STALE_SURVIVES=yes FILE_COUNT=1$"
      }
    },
    {
      "id": "V3",
      "kind": "lint",
      "cmd": "python3 -m py_compile configs/campaigns/p2_015_floors/generate_configs.py joulewise/analysis_manifest.py joulewise/detection_floor_registry.py tests/test_modularity.py",
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
    }
  ],
  "flags": []
}
```

## Change

| Finding | Cure | File:line | Exact regression |
|---|---|---|---|
| `MOD-R2-001` | The current generator now refuses `n < 5` and any pattern other than the issued A1/B1/B2/A2 positions with A/B/B/A labels. This follows the magistrate ruling to keep the issued estimator and defer new patterns to an authenticated sibling. | `configs/campaigns/p2_015_floors/generate_configs.py:30`, `:142`, `:191` | `tests/test_modularity.py:162` supplies `n=1`; `:175` supplies `X1/Y1/Z1`. Both assert exit 2 before output. |
| `MOD-R2-002` | A non-default, nonempty output root is refused before campaign assembly or writes, so stale JSON cannot coexist with a successful generation. | `configs/campaigns/p2_015_floors/generate_configs.py:690` | `tests/test_modularity.py:192` creates `stale.json`, then proves exit 2, byte preservation, and exactly one surviving file. |
| `MOD-R2-003` | The frozen v1 registry digest is now source-pinned independently of the editable adjacent checksum. A same-ID declaration rewrite requires a reviewed new registry identity. This is the refuter's equivalent immutable-authority option and preserves historical artifact bytes. | `joulewise/detection_floor_registry.py:18`, `:117` | `tests/test_modularity.py:239` adds `phase_energy_j.score` and `successor_window`, updates the adjacent digest, and proves the loader still refuses on the immutable trust anchor. |
| `MOD-R2-004` | AP-2-linked validation extracts the four profiles from the real `selection_scope`, derives all unordered combinations, and requires exact once-only coverage. No Python tuple duplicates the registry declarations. | `joulewise/analysis_manifest.py:555` | `tests/test_modularity.py:221` keeps the real AP-2 row but replaces six pairs with only `short_short` versus `long_short`; validation now refuses. |

The design record now states the governed minimum, issued-estimator boundary,
clean custom-output rule, immutable v1 registry authority, and the magistrate's
adopted follow-on rulings. No new magistrate-owned state row is needed for these
four cures; the already-recorded P3 follow-on rows remain unchanged.

## Verification notes

An exploratory all-direct-import diagnostic caught artifact-hash churn from an
interim provenance-writing approach. That approach was removed in favor of the
refuter-authorized immutable trust anchor before V1-V4; final artifact bytes and
the detection-floor implementation have no session delta. The repository-wide
suite was not run, per the preflight rule.
