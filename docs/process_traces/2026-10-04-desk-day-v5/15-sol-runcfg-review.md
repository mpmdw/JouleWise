```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "REVIEW: FAIL — real runner serialization and tamper refusals pass, but the second plan-tree read can escape the original tree digest binding.",
  "workspace": {
    "base_requested": "ee749c39",
    "base_mode": "exact",
    "head_start": "ee749c391883fcb3669bca16a50cfbef34b361a8",
    "head_end": "ee749c391883fcb3669bca16a50cfbef34b361a8",
    "upstream_end": "8fa002f77db7af1e261a30e3787e38af2ab5e946",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "line": "REVIEW: FAIL",
    "findings": [
      {
        "id": "F1",
        "severity": "should_fix",
        "label": "MAJOR",
        "file": "joulewise/window_duration_margins.py",
        "line": 512,
        "summary": "The second plan-tree read is not bound to the tree_sha returned by _pack_inventory when the symlink target changes.",
        "evidence": "Retargeting plan_tree.json between reads registers the second tree under a different resolved identity. Its changed science config_path is accepted, and a pin-matching replacement source passes _observe_member.",
        "recommendation": "Reuse the tree parsed by _pack_inventory, or compare the second read's digest against its returned tree_sha.",
        "verification": "V3"
      }
    ],
    "executed_member": {
      "bundle_id": "d117f15-df-cmp-abba-ph-decode-b01-a1",
      "source": "configs/campaigns/d117_floor_qwen25_1p5b_v1/02_phase_decode_abba_blocks_01_05/d117f15-df-cmp-abba-ph-decode-b01-a1.json",
      "source_sha256": "2882f759096b1d30aab65962ca20288b7472b4041280e099956a4e64e4c6b81a",
      "run_sha256": "689e9a532aa8ae9c9415cf0b146c6a91415139cadefa806e62782df5bf7b396d",
      "result": "passed _observe_member with five overlapping power intervals"
    }
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m pytest -q -p no:cacheprovider tests/test_window_duration_margins.py tests/test_custody_mode_inventory.py > /tmp/dd5-rcreview/focused.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["49 passed, 37 subtests passed in 396.41s (0:06:36)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "49 passed, 37 subtests passed"
      }
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/dd5-rcreview/replay.py > /tmp/dd5-rcreview/replay.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["COMPLETE runner replay and inventory counterfactuals"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "COMPLETE runner replay and inventory counterfactuals"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/dd5-rcreview/tree_binding_check.py > /tmp/dd5-rcreview/tree_binding_check.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["AssertionError: source paths accepted from a second plan tree whose digest differs from pack_tree_sha256"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-rcreview /Users/edr/code/JouleWise/.venv/bin/python -B -m pytest -q -p no:cacheprovider tests/test_custody_mode_inventory.py::CustodyModeInventoryTests::test_read_replay_inventory > /tmp/dd5-rcreview/custody-allowlist.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["1 passed in 20.66s"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "1 passed"
      }
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "rg -l 'joulewise[.]window_duration_margins|scripts/record_window_duration_margins[.]py|from scripts import record_window_duration_margins' tests --glob '*.py'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["tests/test_window_duration_margins.py"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^tests/test_window_duration_margins.py$"
      }
    }
  ],
  "flags": []
}
```

## Findings

**REVIEW: FAIL**

**F1 — MAJOR:** [window_duration_margins.py:512](/Users/edr/code/JouleWise-wt-dd5-rcreview/joulewise/window_duration_margins.py:512) rereads the tree and ignores its digest. The authentication registry keys reads by resolved path; retargeting `plan_tree.json` creates a new identity, bypassing the first-digest comparison. I reproduced changed science-path selection from an unpinned second tree, followed by successful member observation. V3 exits 1. Reuse the verified tree or explicitly compare the second digest with `tree_sha`.

The real generated floor config passed through `BenchmarkConfig.from_mapping`, `RunBundleWriter.create/write_metadata`, and unpatched `_observe_member`. One-field source edits and post-run config edits refused, including edits with rebound metadata. Different source bytes that normalize identically also refused because the source pin remains exact.

The writer computes the metadata hash directly at [bundle.py:950](/Users/edr/code/JouleWise-wt-dd5-rcreview/joulewise/bundle.py:950) and emits it at [metadata:1098](/Users/edr/code/JouleWise-wt-dd5-rcreview/joulewise/bundle.py:1098). [controller.py:3387](/Users/edr/code/JouleWise-wt-dd5-rcreview/joulewise/controller.py:3387) uses identical serialization; the writer does not call that helper.

Missing/null/list downstream contracts, missing/duplicate registered science rows, traversal, absolute paths, and escaping source symlinks all refused. Ordinary tree changes between reads refused. No custody allowlist update is needed: the new read adds no replay-mode opt-in. All **49 requested tests passed**, plus 37 subtests; no additional importing test modules were found. Worktree unchanged.

## Residual risk

The execution probe used real generated config bytes and production bundle serialization with fixture telemetry. It did not perform live hardware collection.