```json
{
  "schema": "claude-codex-report/v1",
  "genre": "scout",
  "status": "findings",
  "completion": "complete",
  "summary": "INDEPENDENT: PR #281 adds the two floor producers but does not implement the shared-core invariant; retarget the extraction to the three live _v5 generators instead of merging this branch unchanged.",
  "workspace": {
    "base_requested": "origin/main",
    "base_mode": "exact",
    "head_start": "bf67155c024aeaeacece29e0a755f76b9b9f8606",
    "head_end": "bf67155c024aeaeacece29e0a755f76b9b9f8606",
    "upstream_end": "ec8f780337326f82feb1848a972c4746612da6cc",
    "branch": "feat/2026-09-04-fan-GENERATOR-CORE-01"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/GENERATOR-CORE-01/02-supersession-scout.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "classification": "INDEPENDENT",
    "rows": [
      {
        "row": "Retarget the shared helper extraction onto current main",
        "action": "start_now",
        "wait_for": "",
        "collision_surface": "contrast generator plus both PR #281 floor generators and their parity tests"
      },
      {
        "row": "Modify the nine authenticated historical generator snapshots",
        "action": "do_not_start",
        "wait_for": "",
        "collision_surface": "hash-pinned historical pack trees"
      },
      {
        "row": "Merge bf67155c unchanged",
        "action": "do_not_start",
        "wait_for": "",
        "collision_surface": "stale 10-generator census, stale floor-producer ruling, and main-only contrast hardening"
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "python3 - <<'PY'\nimport ast\nimport subprocess\nhelpers = {'render_json', 'sha256_bytes', 'sidecar_bytes', 'actual_pack_paths', 'validate_generation_write_boundary'}\npaths = ('configs/campaigns/d117_contrast_v5/generate_configs.py', 'configs/campaigns/d117_floor_qwen3-1p7b_v5/generate_configs.py', 'configs/campaigns/d117_floor_qwen3-8b_v5/generate_configs.py')\nassert subprocess.run(['git', 'cat-file', '-e', 'origin/main:joulewise/campaign_generator_core.py'], capture_output=True).returncode != 0\nfor path in paths:\n    tree = ast.parse(subprocess.check_output(['git', 'show', f'origin/main:{path}'], text=True))\n    local = {node.name for node in tree.body if isinstance(node, ast.FunctionDef)}\n    assert helpers <= local\nbranch = ast.parse(open('joulewise/campaign_generator_core.py', encoding='utf-8').read())\nassert helpers <= {node.name for node in branch.body if isinstance(node, ast.FunctionDef)}\nprint('BEHAVIOR_MAP_OK main_shared_core=absent main_local_generators=3 branch_shared_core=present')\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "BEHAVIOR_MAP_OK main_shared_core=absent main_local_generators=3 branch_shared_core=present"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "BEHAVIOR_MAP_OK main_shared_core=absent main_local_generators=3 branch_shared_core=present"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "No tests run: preflight prohibited tests unless a specific inspection claim required one.",
      "cwd": ".",
      "observed": {
        "result": "not_run",
        "exit_code": 0,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    },
    {
      "id": "V3",
      "kind": "lint",
      "cmd": "python3 -c \"import json,pathlib; p=pathlib.Path('docs/process_traces/2026-09-04-fanout/GENERATOR-CORE-01/02-supersession-scout.md'); t=p.read_text(encoding='utf-8'); e=t.index(chr(10)+chr(96)*3, 8); b=t[8:e]; json.loads(b); assert len(b.encode('utf-8')) <= 8192; assert all(line == line.rstrip() for line in t.splitlines()); print('REPORT_OK pathspec=1')\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "REPORT_OK pathspec=1"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "REPORT_OK pathspec=1"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "The branch test hard-codes ten D-117 generators and classifies every non-contrast generator as historical; origin/main now has twelve, including two live PR #281 floor generators.",
      "needs": "Retarget the census before landing."
    },
    {
      "id": "F2",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "The identity-class factory has no production caller in this branch and only a synthetic downgrade test, so its parity across contrast and floor preserve/freeze paths is not established.",
      "needs": "Either wire it into all three live generators with exact behavior tests or omit it from the first extraction."
    }
  ]
}
```

INDEPENDENT

PR #281 supplies ALPHA/BETA floor-generation behavior, but it does so with two new 3,350-line generators that each retain local `render_json`, `sha256_bytes`, `sidecar_bytes`, `actual_pack_paths`, `validate_generation_write_boundary`, and `GenerationIdentity`. `origin/main` has no `joulewise.campaign_generator_core`. It therefore satisfies “floor producers exist,” not GENERATOR-CORE-01's behavioral acceptance that a new producer uses one shared implementation.

The branch is not mergeable unchanged. Main also hardened GAMMA after the branch point (`render_suite_manifest_bytes`, declared suite-manifest census, exact identity-unit roster), and the branch's test assumes 10 generators and treats all 9 non-GAMMA files as immutable history. Main now has 12: 9 historical snapshots and 3 live `_v5` generators.

## Scheduling matrix

| Row | action | wait_for | collision surface |
|---|---|---|---|
| Shared byte/write helpers | start_now | — | Carry `render_json`/`make_render_json`, SHA and sidecar helpers, inventory, and write-boundary validation; import them from all three live generators. Extend `test_unfrozen_d117_generator_uses_the_one_shared_write_core` to those exact three; retain the symlink-boundary tests. |
| Output preservation | start_now | shared-helper wiring | Extend `check_campaign_generator_core_parity.py` from GAMMA to ALPHA/BETA/GAMMA against pre-extraction `origin/main`; compare every non-self-bound emitted byte. Keep `test_generators_are_deterministic_closed_and_checkable` for the two floors and the existing GAMMA pack test. |
| Historical snapshots | do_not_start | — | Keep the nine hash-pinned generators byte-identical; change the custody test to enumerate those nine explicitly rather than “everything except contrast.” |
| Identity factory | wait_for | production wiring design | The branch's `make_generation_identity_class` is unused. Cover current/successor/downgrade/preserve/frozen behavior in each live generator before carrying it; otherwise omit this hunk initially. |
| Spec/parity prose | wait_for | current topology | Rewrite the stale “next generators unmerged” and 10-generator claims; do not carry those passages verbatim. |

## Critical path

Shared-helper wiring precedes three-generator byte parity. Parity and the existing ALPHA/BETA/GAMMA focused suites precede any landing. The historical-snapshot row has no dependency and remains untouched throughout.
