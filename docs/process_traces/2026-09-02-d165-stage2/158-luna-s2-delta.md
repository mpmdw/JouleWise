```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Ruling 153a is implemented and all requested verification passes; one explicitly ruling-open R-7 nit remains recorded.",
  "workspace": {
    "base_requested": "28501410",
    "base_mode": "exact",
    "head_start": "285014107998e076ab7836bb801a2573ae97bd6c",
    "head_end": "285014107998e076ab7836bb801a2573ae97bd6c",
    "upstream_end": "6296ce93130ab1ae221a0767b7431bb0af252867",
    "branch": "HEAD (no branch)"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "N1",
        "severity": "nit",
        "summary": "R-7 explicitly leaves runtime-split ''.join assembly outside the compiled-constant census; the join mutant passed.",
        "file": "tests/test_d165_dominance_closeout.py",
        "line": 662
      }
    ],
    "rulings": {
      "R-5": "done-as-ruled",
      "R-6": "done-as-ruled",
      "R-7": "done-as-ruled; join form recorded open",
      "R-8": "done-as-ruled for the active production route",
      "R-9": "recorded process deviation; no code action",
      "R-10": "done-as-ruled",
      "R-11": "done-as-ruled"
    }
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git diff --stat 6296ce93 28501410",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["6 files changed, 210 insertions(+), 119 deletions(-)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "6 files changed"}
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git show 6296ce93:configs/campaigns/d117_contrast_v5/generate_configs.py | cmp - configs/campaigns/d117_contrast_v5/generate_configs.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["generator_cmp_rc=0"]},
      "expected": {"exit_code": 0, "tail_regex": "generator_cmp_rc=0"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "TMPDIR=/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/codex-d165-audit/r5-clean-tmp /Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_mint_floor_artifact_generalized.V2PinsetAndMintTests.test_zero_denominator_replay_refuses_without_outputs",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 1 test", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 1 test.*OK"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "TMPDIR=<r5-mutant-tmp> /Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_mint_floor_artifact_generalized.V2PinsetAndMintTests.test_zero_denominator_replay_refuses_without_outputs",
      "cwd": "<r5-mutant>",
      "observed": {"result": "pass", "exit_code": 1, "tail": ["AssertionError: True is not false", "FAILED (failures=1)"]},
      "expected": {"exit_code": 1, "tail_regex": "True is not false"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "TMPDIR=<r7-mutant-tmp> /Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_d165_dominance_closeout.D165DominanceCloseoutTests.test_stage2_sidecar_ownership_ast_census",
      "cwd": "<r7-concat-and-fstring-mutants>",
      "observed": {"result": "pass", "exit_code": 1, "tail": ["literal unexpectedly found in _probe_drift.py", "FAILED (failures=1)"]},
      "expected": {"exit_code": 1, "tail_regex": "unexpectedly found.*_probe_drift.py"}
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "TMPDIR=<r7-join-tmp> /Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_d165_dominance_closeout.D165DominanceCloseoutTests.test_stage2_sidecar_ownership_ast_census",
      "cwd": "<r7-join-mutant>",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 1 test", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 1 test.*OK"}
    },
    {
      "id": "V7",
      "kind": "test",
      "cmd": "TMPDIR=<r7-nested-tmp> /Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_d165_dominance_closeout.D165DominanceCloseoutTests.test_stage2_sidecar_ownership_ast_census",
      "cwd": "<r7-nested-script-mutant>",
      "observed": {"result": "pass", "exit_code": 1, "tail": ["unexpectedly found.*scripts/nested/_probe_drift.py", "FAILED (failures=1)"]},
      "expected": {"exit_code": 1, "tail_regex": "scripts/nested/_probe_drift.py"}
    },
    {
      "id": "V8",
      "kind": "test",
      "cmd": "TMPDIR=<r8-clean-tmp> /Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_mint_floor_artifact_generalized.V2PinsetAndMintTests.test_common_mode_full_cli_path_writes_bound_exact_artifact",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 1 test", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 1 test.*OK"}
    },
    {
      "id": "V9",
      "kind": "test",
      "cmd": "TMPDIR=<r8-mutant-tmp> /Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_mint_floor_artifact_generalized.V2PinsetAndMintTests.test_common_mode_full_cli_path_writes_bound_exact_artifact",
      "cwd": "<r8-mutant>",
      "observed": {"result": "pass", "exit_code": 1, "tail": ["AssertionError: MintError not raised", "FAILED (failures=1)"]},
      "expected": {"exit_code": 1, "tail_regex": "MintError not raised"}
    },
    {
      "id": "V10",
      "kind": "test",
      "cmd": "TMPDIR=<n4-mutant-tmp> /Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_d165_dominance_closeout.D165DominanceCloseoutTests.test_stage2_builder_uses_floor_identity_and_default_shape",
      "cwd": "<n4-malformation-removed-mutant>",
      "observed": {"result": "pass", "exit_code": 1, "tail": ["AssertionError: ValueError not raised", "FAILED (failures=1)"]},
      "expected": {"exit_code": 1, "tail_regex": "ValueError not raised"}
    },
    {
      "id": "V11",
      "kind": "suite",
      "cmd": "TMPDIR=/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/codex-d165-audit/suite-tmp /Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_d165_dominance_closeout tests.test_floor_mint_estimator tests.test_mint_floor_artifact_generalized tests.test_analysis_manifest_v3 tests.test_analysis_finalizer tests.test_detection_floor",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 360 tests", "OK (skipped=2)"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 360 tests.*OK"}
    },
    {
      "id": "V12",
      "kind": "suite",
      "cmd": "TMPDIR=/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/codex-d165-audit/d117-tmp /Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_d117_contrast_v5_pack",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 28 tests", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 28 tests.*OK"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "Runtime-split join assembly is intentionally outside R-7's compiled-constant census.",
      "needs": ""
    },
    {
      "id": "F2",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "mint_multi_cell_authenticated_artifact passes no sink, but has no non-test repository callers; direct external use would bypass the active selection refusal.",
      "needs": ""
    }
  ]
}
```

## Findings

BLOCKER: None.

SHOULD-FIX: None.

NIT:

- N1 — R-7 explicitly leaves runtime-split `join` assembly uncaught; the mutant passed. Recursive `scripts/**` and `joulewise/**` walks are active and nested-script mutants are killed.

## Ruling verdicts

| Ruling | Verdict |
|---|---|
| R-5 | Done. Common-mode zero denominator reaches `closeout_input_malformed` at `dominance_closeout.py:541-547`; no common-mode refused shape remains. Remaining `refused` hits are independent/closeout records. |
| R-6 | Done. The phase-0 docstring states the whole-file digest and nine path-sensitive inputs at `test_mint_floor_artifact_generalized.py:6950`; fixed path and loud contention remain as ruled. |
| R-7 | Done. Compiled `co_consts` census covers recursive `rglob` paths at `test_d165_dominance_closeout.py:662-678`. |
| R-8 | Done for production. CLI → `mint_multi_cell_floor_artifact` → active mint (`scripts/mint_floor_artifact_generalized.py:3984-4016`) → `_build_v2_artifacts` with sink (`:4071-4084`) → selection refusal (`:2992-2998`). The no-sink helper at `:3333-3356` has no non-test repository callers. |
| R-9 | Recorded process deviation; no code change required. |
| R-10 | Done. The contract now says the refusal occurs at first “selection” (`docs/contracts/d165_dominance_closeout.md:203-205`), restores consumer fail-closed prose (`:277-279`), and the N4 mutation raises as required. |
| R-11 | Done. Compatibility is narrowed to “Legacy D-134-form four-row packs”; pre-D-134 packs are explicitly outside the promise (`docs/contracts/d165_dominance_closeout.md:268-271`). |

The hand-built old nine-key refused replay result was rejected by the validator with `extra keys ['refusal_reason', 'status']`. The new zero-denominator regression asserts no sidecar and no `floor.json`; its premature-sidecar mutant fails exactly on that assertion. No stage-1/stage-2 pinned behavior regressed.

## Residual risk

No real models or hardware were exercised, per scope. A direct external caller of `mint_multi_cell_authenticated_artifact` could bypass R-8’s active-mint guard, but no production call path in this repository reaches it.