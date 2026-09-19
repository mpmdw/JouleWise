```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "clean",
  "completion": "complete",
  "summary": "C1-C5 satisfied: no contract findings; ten regressions pass, six refusal regressions detect deletion of the head-check call, and historical custody bytes are unchanged.",
  "workspace": {
    "base_requested": "b3abce08",
    "base_mode": "descendant",
    "head_start": "842e5b39997f53ac8fcec96ec6fe2add6d9df496",
    "head_end": "842e5b39997f53ac8fcec96ec6fe2add6d9df496",
    "upstream_end": "b3abce08f388cb061ebf65ed8e7249ad286fae7d",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "counts": {"blocker": 0, "should_fix": 0, "nit": 0},
    "findings": []
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python /tmp/b1-contract-inspection.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "PASS identical generator edit hunks",
          "PASS five refusals; unused return; three unchanged drift rows precede call; preserve branch unchanged",
          "PASS custody: 10 other d117 generators, 9 committed plan trees, all 3 contrast_v5 files byte-identical to base",
          "PASS all five frozen-path test modules and shared historical fixture unchanged",
          "PASS clean detached worktree at requested head; diff --check"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "PASS clean detached worktree at requested head; diff --check"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python -m unittest -v tests.test_generator_head_pin_relation > /tmp/b1-contract-regression.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 10 tests in 61.774s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python /tmp/b1-contract-delete-call.py > /tmp/b1-contract-delete-call.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "DETECTED test_acceptance_cutoff_digest_must_match_generator_binding",
          "DETECTED test_equal_sequence_with_different_digest_refuses",
          "DETECTED test_missing_or_extra_keys_refuse_shape",
          "DETECTED test_non_integer_sequence_refuses_shape",
          "DETECTED test_rolled_back_pin_refuses_before_any_write",
          "DETECTED test_schema_mismatch_refuses",
          "SURVIVES test_acceptance_byte_drift_refuses_before_head_check",
          "SURVIVES test_advanced_pin_emits_identical_bytes_to_cutoff",
          "SURVIVES test_check_subprocess_uses_real_committed_pin_without_fixture",
          "SURVIVES test_manifest_issued_head_is_exactly_the_acceptance_binding",
          "MUTANT tests=10 failed_methods=6 failures=28 errors=0",
          "PASS deletion detected by exactly six refusal regressions"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "PASS deletion detected by exactly six refusal regressions"}
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python scripts/fixture_orphan_census.py --fail-on-orphans",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 2,
        "tail": ["{\"error\": \"PermissionError: [Errno 1] Operation not permitted: 'ps'\"}"]
      },
      "expected": {"exit_code": 0, "tail_regex": ".*"}
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "git status --short --branch && git rev-parse HEAD origin/main && git diff --check b3abce08 HEAD",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## HEAD (no branch)",
          "842e5b39997f53ac8fcec96ec6fe2add6d9df496",
          "b3abce08f388cb061ebf65ed8e7249ad286fae7d"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "b3abce08f388cb061ebf65ed8e7249ad286fae7d"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "Session-end fixture census could not observe processes because the sandbox denied ps; no clean census is claimed.",
      "needs": "Lead replay fixture_orphan_census.py --fail-on-orphans where process observation is available."
    }
  ]
}
```

## Findings

None.

**C1 — Conforms to the adjudicated shape.** Both generator edit hunks are identical. The [helper](/Users/edr/code/JouleWise-wt-b1refc-d0b83820/configs/campaigns/d117_floor_qwen3-1p7b_v5/generate_configs.py:2477) has five distinct refusals:

| Condition | Exact message template |
|---|---|
| Invalid object, key set, or sequence type | `ledger head pin shape invalid` |
| Acceptance cutoff binding mismatch | `acceptance ledger cutoff drifted: {acceptance_path}` |
| Schema mismatch | `ledger head pin schema mismatch: {pin_path}` |
| Sequence below cutoff | `ledger head pin behind the acceptance cutoff: {pin_path}` |
| Equal sequence, different digest | `ledger head pin diverged from the acceptance cutoff: {pin_path}` |

The call at line 2546 immediately follows the drift loop, before regeneration writes. Its return value is discarded. The manifest at line 2921 emits only the constant acceptance binding. Boolean/string sequences receive the refuter’s incorporated shape refusal.

**C2 — The comment is explicit and true.** Lines 2479–2484 assign higher-sequence fork detection to runtime evaluation and state that generation does not attempt it. The [ledger loader](/Users/edr/code/JouleWise-wt-b1refc-d0b83820/joulewise/calibration_ledger.py:2600) verifies committed pin bytes, physical-head agreement, and baseline membership through line 2631; the [chain parser](/Users/edr/code/JouleWise-wt-b1refc-d0b83820/joulewise/calibration_ledger.py:1509) checks sequence and predecessor links. Both generators pass the pin through [the runtime `--head-pin` argument](/Users/edr/code/JouleWise-wt-b1refc-d0b83820/configs/campaigns/d117_floor_qwen3-1p7b_v5/generate_configs.py:1622).

**C3 — No affected consumer or custody change.** The complete tracked-file search outside `configs/` and `docs/` returned 247 occurrences of the two search terms. `issued_ledger_head` appears only in two queue descriptions and the new regression assertion; other `file_sha256` references concern unrelated artifacts. Production acceptance-policy readers consume acceptance fields, not the removed head-file digest.

Byte comparisons against `b3abce08` confirm that all nine frozen generators, all nine committed `plan_tree.json` files, and all three files under `d117_contrast_v5` are unchanged.

**C4 — Fences retained.** Generation refuses rollback below the cutoff. Policy, acceptance, and settled-corpus byte checks remain unchanged and precede the head check. Preserve/echo branches are unchanged. All five frozen-path test modules and their shared historical fixture remain intact.

The [label mapping](/Users/edr/code/JouleWise-wt-b1refc-d0b83820/scripts/check_campaign_generator_core_parity.py:19) confirms ALPHA→Qwen3-1.7B v5 and BETA→Qwen3-8B v5. Their live-generator fixture was removed correctly. The v5 test helper retains its clone and working-tree generator copies while removing the historical head-byte write.

**C5 — Required coverage is present; refusal checks are discriminating.** In the [new regression module](/Users/edr/code/JouleWise-wt-b1refc-d0b83820/tests/test_generator_head_pin_relation.py:69), ruling items 1–7 and 9 map respectively to tests beginning at lines 69, 87, 97, 105, 116, 139, 165, and 183. Item 8 remains in the unchanged frozen-path tests. Line 124 covers malformed key sets and non-object shapes; line 155 additionally tests acceptance-cutoff binding.

All ten tests passed. Deleting the call at generator line 2546 in disposable copies caused the six refusal regressions named in V3 to fail. Four tests survive deletion: acceptance drift, advanced-pin byte identity, manifest shape, and real-pin CLI checking. Those establish separate required properties; none alone establishes head-check enforcement. No vacuous refusal regression was found.

## Residual risk

The broader suites, remaining mutation oracles, and CLI experiments under X1–X5 belong to the execution lens and are not claimed here. Frozen-path preservation was verified by source and byte comparison, without replaying those suites.

No repository files changed. Next: lead combines this contract review with execution-lens evidence and resolves the census observation gap.