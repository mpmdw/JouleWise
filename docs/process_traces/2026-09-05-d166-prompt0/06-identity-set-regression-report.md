```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Option (b): retain intended D-166 singleton production identity; restore two real declared identities in the synthetic fixture; 13/19/44 tests pass.",
  "workspace": {
    "base_requested": "3d3b4ba2",
    "base_mode": "exact",
    "head_start": "3d3b4ba2ff15490ce2a86683c35fe0e5eebc867c",
    "head_end": "3d3b4ba2ff15490ce2a86683c35fe0e5eebc867c",
    "upstream_end": "afd75e3f71f9fe0a5ac77a18d2c8aea191ca3248",
    "branch": "feat/2026-09-05-paper-l"
  },
  "pathspec": [
    "tests/test_analysis_inputs.py",
    "tests/test_d117_contrast_v5_pack.py",
    "docs/process_traces/2026-09-05-d166-prompt0/06-identity-set-regression-report.md"
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
      "cmd": "PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -m unittest tests.test_analysis_inputs.FrozenConsumerIdentitySetTests",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "AssertionError: 1 != 2",
          "----------------------------------------------------------------------",
          "Ran 13 tests in 27.800s",
          "",
          "FAILED (failures=6)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -m unittest tests.test_analysis_inputs.FrozenConsumerIdentitySetTests",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "----------------------------------------------------------------------",
          "Ran 13 tests in 62.649s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 13 tests in [0-9.]+s\\n\\nOK$"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -m unittest tests.test_analysis_inputs",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "----------------------------------------------------------------------",
          "Ran 19 tests in 58.989s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 19 tests in [0-9.]+s\\n\\nOK$"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -m unittest tests.test_d117_contrast_v5_pack",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "----------------------------------------------------------------------",
          "Ran 44 tests in 15.603s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 44 tests in [0-9.]+s\\n\\nOK$"
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
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 - <<'PY'\nimport collections, json, subprocess, sys, tempfile, types\nfrom pathlib import Path\nfrom tests.test_d117_contrast_v5_pack import D117ContrastV5PackTests, GENERATOR\nfrom joulewise.identity_pins import scientific_config_identity, scientific_config_identity_sha256\n\ndef leaves(value, prefix=''):\n    if isinstance(value, dict):\n        return {k: v for key, child in value.items() for k, v in leaves(child, f'{prefix}.{key}' if prefix else key).items()}\n    if isinstance(value, list):\n        return {k: v for index, child in enumerate(value) for k, v in leaves(child, f'{prefix}[{index}]').items()}\n    return {prefix: json.dumps(value, sort_keys=True)}\n\nwith tempfile.TemporaryDirectory(prefix='d166-identity-diagnosis-') as temporary:\n    fixture = D117ContrastV5PackTests(); fixture.setUp()\n    pin = fixture.write_prefill_pin(Path(temporary))\n    for revision in ('9baf62df10a87753207951a750b5e0bf74d5432f', 'HEAD'):\n        if revision == '9baf62df10a87753207951a750b5e0bf74d5432f':\n            module = types.ModuleType('d166_baseline_diagnosis')\n            module.__file__ = str(GENERATOR)\n            sys.modules[module.__name__] = module\n            source = subprocess.check_output(['git', 'show', f'{revision}:configs/campaigns/d117_contrast_v5/generate_configs.py'], text=True)\n            exec(compile(source, str(GENERATOR), 'exec'), module.__dict__)\n            fixture.generator = module\n        else:\n            fixture.setUp()\n        fixture.configure(pin)\n        generator = fixture.generator\n        runs, _ = generator.build_runs()\n        configs = [generator.config_for(run, 'a' * 64) for run in runs if run['arm'] == 'A' and run['measurement_arm'] == 'decode']\n        counts = collections.Counter(scientific_config_identity_sha256(c) for c in configs)\n        raw = [leaves(c) for c in configs]\n        scientific = [leaves(scientific_config_identity(c)) for c in configs]\n        varied = lambda rows: {k: len({r[k] for r in rows}) for k in rows[0] if len({r[k] for r in rows}) > 1}\n        result = {'configs': len(configs), 'distinct_scientific_identities': len(counts), 'multiplicities': sorted(counts.values()), 'varying_raw_fields': varied(raw), 'varying_scientific_fields': varied(scientific), 'decode_prompt_tags': sorted({t for c in configs for t in c['run_metadata']['tags'] if t.startswith('decode-prompt=')})}\n        print(revision, json.dumps(result, sort_keys=True))\n        print(revision, 'declared_manifest_counts', [row['declared_member_count'] for row in generator.decode_declared_suite_manifest_set('A')])\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "9baf62df10a87753207951a750b5e0bf74d5432f {\"configs\": 20, \"decode_prompt_tags\": [\"decode-prompt=falsifiability\", \"decode-prompt=interest_math\", \"decode-prompt=kyoto_itinerary\", \"decode-prompt=pantry_dinner\", \"decode-prompt=plant_diagnosis\", \"decode-prompt=sky_color\", \"decode-prompt=weather_climate\", \"decode-prompt=web_request\"], \"distinct_scientific_identities\": 8, \"multiplicities\": [2, 2, 2, 2, 2, 2, 4, 4], \"varying_raw_fields\": {\"run_id\": 20, \"run_metadata.tags[11]\": 8, \"run_metadata.tags[7]\": 10, \"run_metadata.tags[9]\": 2, \"workload_profile.suite_manifest_ref\": 8, \"workload_profile.suite_manifest_sha256\": 8}, \"varying_scientific_fields\": {\"run_metadata.tags[7]\": 8, \"workload_profile.suite_manifest_ref\": 8, \"workload_profile.suite_manifest_sha256\": 8}}",
          "9baf62df10a87753207951a750b5e0bf74d5432f declared_manifest_counts [4, 4, 2, 2, 2, 2, 2, 2]",
          "HEAD {\"configs\": 20, \"decode_prompt_tags\": [\"decode-prompt=sky_color\"], \"distinct_scientific_identities\": 1, \"multiplicities\": [20], \"varying_raw_fields\": {\"run_id\": 20, \"run_metadata.tags[7]\": 10, \"run_metadata.tags[9]\": 2}, \"varying_scientific_fields\": {}}",
          "HEAD declared_manifest_counts [20]"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "HEAD declared_manifest_counts \\[20\\]$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "origin/main moved concurrently from 9baf62df10a87753207951a750b5e0bf74d5432f to afd75e3f71f9fe0a5ac77a18d2c8aea191ca3248; worktree HEAD did not move. V5 pins the original baseline.",
      "needs": ""
    }
  ]
}
```

## Change

Chose **(b), repair the synthetic pack**. D-166's collapse is intended; restoring prompt rotation or introducing per-run scientific differences in the production generator would contradict the fixed-prompt rule. The generator and supersession JSON are unchanged by this session.

The dated D-166 addendum (`docs/decision_log.md:10999`) requires prompt 0 of `real_prompts_v1` in every decode block in both model arms. Trace 02 explicitly records one used prompt-0 manifest with 20 members per arm. The dependency census and reviews 01–05 were read; production generation, custody and clone proof remain the separately deferred post-G2-a work.

The source mechanism is `decode_prompt_index` (`generate_configs.py:1398`) feeding `build_runs` and `config_for` (`:1705`, `:1899`). Before D-166, the first two blocks select different prompts; after it, every block selects `sky_color`. An in-memory comparison loaded the original main generator from pinned Git object `9baf62df10a87753207951a750b5e0bf74d5432f` and the current generator, configured both with the same temporary prefill pin, and used the same placeholder plan SHA to isolate the assignment change:

| A/decode inventory property | Original main | Requested branch |
|---|---|---|
| Config members | 20 | 20 |
| Distinct scientific config identities | 8 | 1 |
| Declared manifest member counts, in prompt order | 4, 4, 2, 2, 2, 2, 2, 2 | 20 |
| Distinct `workload_profile.suite_manifest_ref` | 8 | 1 |
| Distinct `workload_profile.suite_manifest_sha256` | 8 | 1 |
| Distinct `decode-prompt=` tag values | 8 | 1 (`decode-prompt=sky_color`) |

Those last three fields are exactly the fields that varied in the normalized scientific configs on original main. On this branch, **no normalized scientific field varies** within A/decode. Raw configs still differ in `run_id`, `calibration-abba-block-id=`, and `calibration-abba-sequence-index=`. `suite_seed` also changed from `d166-block-prompt-cycle-v1` to `d166-fixed-prompt-zero-v1`, changing the manifest digests prospectively; it supplies no distinction between repeats of the same manifest. Model, quantization, runtime, hardware, sampling, common workload, output budget and remaining scientific tags were already common within the arm.

`scientific_config_identity` (`joulewise/identity_pins.py:233`) schema-types the config, drops `run_id`, filters the exact bookkeeping tags, and retains the suite bindings and `decode-prompt=` tag. The identity-pin contract §§2, 4 and 6 (`docs/contracts/identity_pin_projection.md:59`, `:108`, `:351`, `:483`) explicitly requires one scientific identity per manifest class, with the number of distinct identities equal to the number of declared manifests. The singleton config-set digest is the member hash itself; counts remain enforced by the inventory census. Thus scientific identity is **not supposed to distinguish the 20 ordinary fixed-zero repeats**.

The consumer agrees: `_frozen_consumer_identity_set` (`joulewise/analysis_engine/inputs.py:3875`, inventory loop `:4043`) authenticates launch pack digest, U8/projection receipts, plan binding and inventoried bytes, derives a set of config hashes, and compares its fold to `config_set_sha256`. `_floor_request_or_refusal` (`:4078`) requires evidence identities to be a subset of the frozen set, rejects undeclared multi-identity legacy evidence, and allows exact-cell matching only for a singleton. A test that substitutes `1` for the old assertion would no longer exercise those multi-identity branches.

The repaired fixture explicitly declares two manifest classes in each decode arm, ten members each, before generation and freeze. The second class uses a separately named suite containing the **identical prompt-zero payload**. Only its `suite_id` differs, giving a genuinely different full-manifest digest and config suite reference. Configs in the second five-block half bind that manifest; their prompt assignment, prompt tags, token IDs, output policy and common scientific config remain identical. The fixture reuses one otherwise unused manifest slot under an explicit fixture filename. The regular generation pipeline builds all dependent config hashes, order/analysis manifests and plan-tree inventories from these inputs; the real identity projection then freezes them. No hash function, identity normalizer, frozen consumer gate or validator is bypassed.

This is an explicitly synthetic multi-manifest extension, not a claim that the ordinary D-166 generator emits two identities or that a new prompt population is authorized. The contract binds entire declared manifest identities, including separately named manifests of the same payload. The positive regression now checks both authenticated hashes, equality of the frozen and evidence sets, equality of normalized configs after removing only suite bindings, and equality of manifests after removing only their distinct suite IDs. Both existing two-identity assertions remain. The ordinary-generator regression separately pins 20 distinct run IDs but one scientific identity and one 20-member manifest class per arm.

## Verification notes

V0 reproduced six failures among the 13 identity-set tests, all at the original `_generated_transport_case` assertion `len(configs) == 2` (`tests/test_analysis_inputs.py:472` at the starting HEAD): missing-lineage evidence, real-gate transport, stale receipt bytes, plan/receipt config-set mismatch, named legacy multi-identity refusal, and forged launch-tree binding. V1–V3 are the post-fix runs, executed sequentially with the required corpus root. Their exact tails are in the envelope. No discovery suite or additional test target ran. The initial inline diagnostic had a delimiter typo and did not execute; the corrected, pinned replay is V5.

The worktree started clean and remained at the requested HEAD. `origin/main` moved concurrently from `9baf62df10a87753207951a750b5e0bf74d5432f`; the comparison was therefore replayed against that immutable original baseline. No workspace commit, push, agent launcher, measurement collection, production pack or out-of-scope repository write was performed. Git commits made by the authorized test fixtures were confined to their temporary repositories.

Lead next exact step: review this bounded fixture diff and the executed evidence at `3d3b4ba2`, then carry the fix through the lead's integration review.

## Residual risk

Verification is synthetic desk evidence. Runtime/model probes remain fixture-backed as before; these results do not discharge the production regeneration, live identity, custody or clone-proof gates.

