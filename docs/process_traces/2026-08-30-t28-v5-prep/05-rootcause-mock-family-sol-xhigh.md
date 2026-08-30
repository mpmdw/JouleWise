```json
{
  "schema": "claude-codex-report/v1",
  "genre": "root_cause",
  "status": "findings",
  "completion": "complete",
  "summary": "Confirmed: round 1 added nullable model pins whose nulls are omitted from normalized config but emitted in metadata, causing all newly produced unpinned AP-2 bundles to be excluded as config_hash_mismatch before pairing.",
  "workspace": {
    "base_requested": "origin/main@62be575169e485ee255acea4b6f5adac6ba8a8a9",
    "base_mode": "informational",
    "head_start": "7f4492c56e886dc162110c86d252096de926ba1a",
    "head_end": "7f4492c56e886dc162110c86d252096de926ba1a",
    "upstream_end": "7a5c4ad6124e449b996d52c6fdcc0d683ca3c60b",
    "branch": "feat/v5-ladder-prep"
  },
  "pathspec": [],
  "unowned_dirty": [
    "configs/campaigns/d117_contrast_v5/generate_configs.py",
    "docs/campaign_packs/d117_contrast_v5.md",
    "joulewise/analysis_manifest_v3.py",
    "tests/test_analysis_manifest_v3.py",
    "tests/test_d117_contrast_v5_pack.py"
  ],
  "verdict": {
    "cause": "confirmed",
    "remediation": "proposed"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "python3 -c 'import json; from dataclasses import asdict; from pathlib import Path; from joulewise.schemas import BenchmarkConfig; c=BenchmarkConfig.from_mapping(json.loads(Path(\"configs/examples/mock_local.json\").read_text())); expected=c.to_dict()[\"model\"]; emitted=asdict(c.model); fixed={k:v for k,v in emitted.items() if k not in {\"tokenizer_json_sha256\",\"chat_template_sha256\"} or v is not None}; print(\"before_equal=\"+str(emitted==expected)); print(\"after_guard_equal=\"+str(fixed==expected))'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "before_equal=False",
          "after_guard_equal=True"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "before_equal=False.*after_guard_equal=True"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git diff --name-only a3756ad1..03d3de3f; for rev in a3756ad1 03d3de3f; do git rev-parse \"$rev:joulewise/analysis_manifest_v3.py\"; done",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "tests/test_mlx_runtime.py",
          "tests/test_schemas.py",
          "22123b66e07eded1ec2249f868bfbbc506f4b8d6",
          "22123b66e07eded1ec2249f868bfbbc506f4b8d6"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "22123b66e07eded1ec2249f868bfbbc506f4b8d6"
      }
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_analysis_integration",
      "cwd": ".",
      "observed": {
        "result": "not_run",
        "exit_code": 1,
        "tail": [
          "FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/edr/code/JouleWise-wt-s15']"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 102 tests.*OK"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The read-only sandbox exposes no writable temporary directory, so the established 102-test failure could not be replayed here.",
      "needs": "After applying the fix, rerun the mandatory adjacency suites in a writable bench."
    },
    {
      "id": "F2",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "Git objects show that a3756ad1 and 03d3de3f contain the identical analysis_manifest_v3.py blob; the prefill parameterization entered at 767eeaae and was present, but not changed, in round 1.",
      "needs": "Attribute the regression specifically to the 03d3de3f schemas.py serialization interaction."
    }
  ]
}
```

## Causal chain

1. The test fixture generates a real Slice-2M/AP-2 mock campaign: 30 bundles and a `joulewise.analysis_manifest.v1` manifest with five blocks and 24 AP-2 contrasts, including `long_short-minus-short_short` ([test setup](/Users/edr/code/JouleWise-wt-s15/tests/test_analysis_integration.py:1534), [AP-2 registry](/Users/edr/code/JouleWise-wt-s15/configs/analysis_registry/slice_2m_ap2.v1.json:48)).

2. `load_manifest` dispatches that manifest to the v1 validator at [inputs.py:584](/Users/edr/code/JouleWise-wt-s15/joulewise/analysis_engine/inputs.py:584). It never enters `_validate_prospective_analysis_manifest_v3_unchecked`; the parameterized d117 arm selection is confined to the prospective-v3 validator at [analysis_manifest_v3.py:2074](/Users/edr/code/JouleWise-wt-s15/joulewise/analysis_manifest_v3.py:2074) and [analysis_manifest_v3.py:2336](/Users/edr/code/JouleWise-wt-s15/joulewise/analysis_manifest_v3.py:2336).

3. Before `03d3de3f`, `ModelConfig` had six fields. Both serializers therefore produced the same model mapping:

   - normalized `config.json`: `BenchmarkConfig.to_dict()`
   - `metadata.json`: `asdict(self._config.model)`

4. Round 1 added `tokenizer_json_sha256` and `chat_template_sha256` as nullable `ModelConfig` fields at [schemas.py:729](/Users/edr/code/JouleWise-wt-s15/joulewise/schemas.py:729). To preserve legacy D-001 config bytes, `BenchmarkConfig.to_dict()` deletes those keys when null at [schemas.py:1044](/Users/edr/code/JouleWise-wt-s15/joulewise/schemas.py:1044). The unchanged controller instead emits the raw dataclass at [controller.py:2111](/Users/edr/code/JouleWise-wt-s15/joulewise/controller.py:2111).

   Consequently, an unpinned mock bundle now contains:

   ```text
   config.model:   six legacy keys
   metadata.model: the same six keys + tokenizer_json_sha256:null
                                      + chat_template_sha256:null
   ```

5. The loader canonicalizes `config.json` through `BenchmarkConfig.to_dict()` at [inputs.py:2466](/Users/edr/code/JouleWise-wt-s15/joulewise/analysis_engine/inputs.py:2466), then requires literal equality with `metadata.model` at [inputs.py:2551](/Users/edr/code/JouleWise-wt-s15/joulewise/analysis_engine/inputs.py:2551). The two extra null keys make that comparison false.

6. `_read_bundle` converts the false result into `config_hash_mismatch` and excludes the bundle at [inputs.py:2735](/Users/edr/code/JouleWise-wt-s15/joulewise/analysis_engine/inputs.py:2735). This reason is slightly misleading: source/config normalized hashes still match; the failing subcheck is realized-model metadata equality at line 2741.

7. Every AP-2 condition and sentinel bundle is excluded. `_prepare_contrast` therefore finds no usable numeric pairs at [analysis engine:868](/Users/edr/code/JouleWise-wt-s15/joulewise/analysis_engine/__init__.py:868), creates zero observations, and passes `block_ids=()` to `randomization_check` at [analysis engine:1042](/Users/edr/code/JouleWise-wt-s15/joulewise/analysis_engine/__init__.py:1042).

8. The manifest’s named strata still assign the five real IDs. Comparing those assignments with the empty observation-derived ID set raises at [sensitivity.py:103](/Users/edr/code/JouleWise-wt-s15/joulewise/analysis_engine/sensitivity.py:103). Thus the frozen manifest blocks were not erased; the eligible paired-observation set was emptied.

Blast radius:

- Every newly controller-produced, unpinned bundle consumed through `load_analysis_inputs` is affected, independent of backend or model name.
- This includes AP-2 v1 families, registered bundles, replacements, and top-ups. The same `_read_bundle` path also serves legacy and finalized v3 manifests.
- Prospective d117 v5 members carrying both non-null pins are unaffected: normalized config and metadata both retain the two keys.
- Pre-round-1 retained fixtures are unaffected because their config and metadata both have the legacy six-key shape. The tracked `d078_r01` and `d117_v2_production` pairs have that form.
- A legacy/unpinned configuration rerun after round 1 is affected. No tracked `runs/**/config.json` artifacts exist in this worktree, so out-of-repository retained runs require a separate inventory.
- No other test module exercises this exact real-controller-to-analysis-loader seam. `tests.test_analysis_finalizer` handcrafts metadata from the already-normalized config, while `tests.test_controller` only checks the model name. Those suites stayed green because they bypassed or under-asserted the mismatch.

## Remediation

The minimal prospective fix is to make controller metadata use the same canonical model representation as `config.json`:

```python
extra["model"] = dict(self._config.to_dict()["model"])
```

This replaces `asdict(self._config.model)` at `controller.py:2111`.

That existing `to_dict()` guard supplies the required scoping:

- both pins absent/null → omit both, restoring every legacy/non-d117/mock family;
- both pins present → retain and authenticate both, preserving d117 v5;
- the prospective-v3 arm logic remains unchanged: legacy `prefill_p256`, or exactly one ruled ladder arm (`p512`, `p1024`, `p2048`, `p4096` under amended D-166).

If any post-`03d3de3f` unpinned bundles were durably retained, the producer fix is not retroactive. For those only, add a compatibility normalization at the realized-identity boundary that removes exactly these two keys only when their values are null. Non-null pins must remain exact; do not weaken the comparison generally.

Mandatory minimum adjacency for every `analysis_manifest_v3.py` change:

```text
tests.test_analysis_manifest_v3
tests.test_analysis_finalizer
tests.test_analysis_integration
tests.test_pipeline_smoke_tail
tests.test_collector_analysis_manifest_id
```

For arm-vocabulary/generator changes, also require:

```text
tests.test_d117_contrast_v5_pack
tests.test_d117_gamma_d139a2_families
```

For a round that also changes `schemas.py`, controller metadata, or runtime identity—as this one did—also require:

```text
tests.test_schemas
tests.test_controller
tests.test_mlx_runtime
```

Add a focused controller assertion that `metadata["model"] == config["model"]`, plus an assertion in the mock pipeline that no bundle acquires `config_hash_mismatch`. The full 102-test integration suite must pass; d117-only golden matrices are not an acceptable substitute.

## Disproved alternatives

- **Prefill-arm parameterization:** not causal. It entered at `767eeaae`, which the lead established as green; `a3756ad1` and `03d3de3f` have the identical `analysis_manifest_v3.py` blob. AP-2 v1 dispatch never calls its prospective validator.
- **MLX runtime pin enforcement:** not causal. The failing family uses `mock_runtime`; MLX preparation is never reached.
- **The v5 generator:** not causal. It writes only the d117 v5 pack and cannot mutate the independently generated AP-2 temporary fixture.
- **Randomization validation:** correct downstream refusal. It detects the contradiction created after all eligible observations disappeared; it did not empty the blocks.
- **Manifest corruption:** disproved. The manifest still carries `block-2m-mock-model-r01..r05`; only the observation-derived `block_ids` argument is empty.

## Residual risk

The fix remains unimplemented by instruction. The focused suite must be rerun in a writable environment, and any durable bundles collected after `03d3de3f` without pins should be inventoried before deciding whether the narrow consumer compatibility normalization is needed.