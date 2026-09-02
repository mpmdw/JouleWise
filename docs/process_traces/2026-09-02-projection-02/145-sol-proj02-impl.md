```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Implemented the realized-prefill identity-projection catcher with legacy gating, per-config freeze/arm verification, seven ruled regressions, and six killed mutants.",
  "workspace": {
    "base_requested": "c5fa8a495e3a0ec74fd13bc7c1dd613626cee6f6",
    "base_mode": "exact",
    "head_start": "c5fa8a495e3a0ec74fd13bc7c1dd613626cee6f6",
    "head_end": "c5fa8a495e3a0ec74fd13bc7c1dd613626cee6f6",
    "upstream_end": null,
    "branch": "feat/v5-prefill-realized-projection-02"
  },
  "pathspec": [
    "joulewise/identity_pins.py",
    "joulewise/adapters/mlx_runtime.py",
    "tests/test_identity_pins.py",
    "tests/test_mlx_runtime.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V0",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_identity_pins tests.test_mlx_runtime",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 68 tests in 4.287s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 68 tests[\\s\\S]*OK"}
    },
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_identity_pins tests.test_mlx_runtime",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 75 tests in 5.391s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 75 tests[\\s\\S]*OK"}
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_arm_readiness_evidence_t0 tests.test_arm_readiness tests.test_bundle_read tests.test_d117_contrast_v5_pack",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 215 tests in 198.010s", "OK (skipped=7)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 215 tests[\\s\\S]*OK \\(skipped=7\\)"}
    },
    {
      "id": "M1",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_mlx_runtime.MlxRuntimeTests.test_identity_projection_metadata_realizes_registered_prompt_with_collection_encoder",
      "cwd": "/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/v5-prefill-realized-projection-02/mutants-01/m1",
      "observed": {
        "result": "pass",
        "exit_code": 1,
        "tail": ["AssertionError: [('registered projection prompt', False)] != [('registered projection prompt', True)]"]
      },
      "expected": {"exit_code": 1, "tail_regex": "False.*True"}
    },
    {
      "id": "M2",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_identity_pins.PromptRealizationProjectionTests.test_freeze_checks_every_registered_config",
      "cwd": "/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/v5-prefill-realized-projection-02/mutants-01/m2",
      "observed": {
        "result": "pass",
        "exit_code": 1,
        "tail": ["AssertionError: IdentityPinProjectionError not raised"]
      },
      "expected": {"exit_code": 1, "tail_regex": "IdentityPinProjectionError not raised"}
    },
    {
      "id": "M3",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_identity_pins.PromptRealizationProjectionTests.test_freeze_mismatch_names_all_differing_fields",
      "cwd": "/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/v5-prefill-realized-projection-02/mutants-01/m3",
      "observed": {
        "result": "pass",
        "exit_code": 1,
        "tail": ["AssertionError: ['token_count', 'token_hash_domain'] != ['token_count', 'token_ids_sha256', 'token_hash_domain']"]
      },
      "expected": {"exit_code": 1, "tail_regex": "token_ids_sha256"}
    },
    {
      "id": "M4",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_identity_pins.PromptRealizationProjectionTests.test_freeze_mismatch_names_all_differing_fields",
      "cwd": "/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/v5-prefill-realized-projection-02/mutants-01/m4",
      "observed": {
        "result": "pass",
        "exit_code": 1,
        "tail": ["AssertionError: ['token_count', 'token_ids_sha256'] != ['token_count', 'token_ids_sha256', 'token_hash_domain']"]
      },
      "expected": {"exit_code": 1, "tail_regex": "token_hash_domain"}
    },
    {
      "id": "M5",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_mlx_runtime.MlxRuntimeTests.test_identity_projection_metadata_omits_realization_without_expectation",
      "cwd": "/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/v5-prefill-realized-projection-02/mutants-01/m5",
      "observed": {
        "result": "pass",
        "exit_code": 1,
        "tail": ["AssertionError: Items in the first set but not the second: 'prompt_realization'"]
      },
      "expected": {"exit_code": 1, "tail_regex": "prompt_realization"}
    },
    {
      "id": "M6",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_identity_pins.PromptRealizationProjectionTests.test_arm_reverification_refuses_each_prompt_realization_drift",
      "cwd": "/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/v5-prefill-realized-projection-02/mutants-01/m6",
      "observed": {
        "result": "pass",
        "exit_code": 1,
        "tail": ["AssertionError: 'PASS' != 'REFUSE'", "FAILED (failures=3)"]
      },
      "expected": {"exit_code": 1, "tail_regex": "PASS.*REFUSE"}
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git status --porcelain",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          " M joulewise/adapters/mlx_runtime.py",
          " M joulewise/identity_pins.py",
          " M tests/test_identity_pins.py",
          " M tests/test_mlx_runtime.py"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "joulewise/identity_pins.py[\\s\\S]*tests/test_mlx_runtime.py"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "No real Qwen tokenizer/model was loaded; P-8's throwaway _v5 freeze-and-arm validation remains deliberately lead-controlled.",
      "needs": "Magistrate runs the ruled real-tokenizer throwaway freeze/arm before any campaign night."
    }
  ]
}
```

## Change

- `joulewise/adapters/mlx_runtime.py:315-349` conditionally realizes registered prompt text through `_prompt_for_workload` and `prompt_provenance`.
- `joulewise/identity_pins.py:1256-1403,1440-1696` validates realization rows, prepares once, projects all expectation-bearing configs in inventory order, compares all three fields, binds rows into probe metadata, and emits per-config checks.
- `tests/test_mlx_runtime.py:450-527` covers the collection encoder and exact legacy adapter key set.
- `tests/test_identity_pins.py:98-287,1148-1422` extends fixtures and adds projection, freeze, arm, legacy-key, unavailable-hook, and check-envelope coverage.

P-1 through P-7:

- P-1: MLX uses `_prompt_for_workload` at `mlx_runtime.py:341-348`; its registered-text branch remains `_encode(..., add_special_tokens=True)` at `:940-946`.
- P-2: conditional adapter emission is `mlx_runtime.py:341`; conditional probe emission is `identity_pins.py:1400-1402`. Legacy metadata/check keys are hard-coded at `tests/test_identity_pins.py:1174-1218`.
- P-3: all typed expectation-bearing configs are collected at `identity_pins.py:1470-1474` and passed through one `_runtime_probe_metadata` invocation at `:1483-1487`; prepare/cleanup bracket the per-config projector loop at `:1310-1375`.
- P-4: unavailable or ill-typed rows use `readiness_identity_artifact_unreadable` at `identity_pins.py:1256-1279,1490-1516`; mismatch uses `readiness_identity_environment_dirty` and names every differing field at `:1531-1550`. The refusal frozenset remains unchanged at `:38-46`.
- P-5: ordered rows enter `probe_metadata` at `identity_pins.py:1685`; per-config four-key PASS checks are `:1552-1562,1696`. Receipt and receipt-unit schemas remain unchanged at `:97-145`.
- P-6: freeze derives before writes at `identity_pins.py:1989-1998`; arm re-derives at `:2101-2170` and retains the existing authenticated REFUSE-receipt path.
- P-7: no-expectation projection retains exactly the six legacy probe keys and one legacy four-key check. No issued receipt was rewritten; source-hash derivation remains at `identity_pins.py:1148-1200`.

## Tests and counterfactuals

- Collection encoder: registered fake prompt; counterfactual `add_special_tokens=False`.
- Legacy omission: config without expectation; counterfactual unconditional `prompt_realization`.
- Every config: member 2 alone has an off-by-one count.
- Complete mismatch detail: member 1 differs in count, ids hash, and domain.
- Arm re-verification: count, ids hash, and domain drift independently; each must REFUSE without changing pack bytes.
- Unavailable realization: missing realization metadata and a runtime with no projection hook.
- Check envelope: two registered configs require two ordered prompt checks; every check contains `shared_mint_projection` and has `expected == observed`.

Focused count increased from 68 to 75. The D-078 closed-vocabulary tests remained unchanged and passed.

## Mutants

All six were executed from isolated copies under the specified scratch directory:

- M1 `add_special_tokens=False`: killed by the encoder-call assertion.
- M2 `configs[0]` only: killed because member-2 drift no longer raised.
- M3 ignore `token_ids_sha256`: killed by the complete differing-field assertion.
- M4 ignore `token_hash_domain`: killed by the same complete-field assertion.
- M5 unconditional realization emission: killed by the exact legacy key-set assertion.
- M6 trust frozen PASS at arm: killed for all three drift subtests by `PASS != REFUSE`.

## Verification notes

No failures or deviations. `git diff --check` passed, both required named-module groups passed, and final status contains only the four allowlisted files.

## Disagreement

No disagreement with P-1 through P-7. A narrower dedicated realization hook could avoid repeating the sampler probe per config, but it would add a new adapter surface; the ruled existing projection hook is the smaller change.

## Residual risk

The real Qwen tokenizer check was intentionally not run. P-8’s throwaway `_v5` freeze/arm remains the magistrate’s next exact step.