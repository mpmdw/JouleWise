# OLMo dense/MoE pair verification — D-016 (2026-07-16)

Machine: Ed's Mac (darwin 25.5.0). Repo venv: /Users/edr/code/JouleWise/.venv (mlx-lm 0.31.3, python 3.13, huggingface_hub 1.22.0, transformers present w/o torch).
Disk check before download: 496 GiB free on /System/Volumes/Data; total download ~19 GiB — ample headroom, proceeded.
Memo consulted first: docs/process_traces/2026-07-16-axi-sd-web-verification/memo.md §1 (pair `olmo-1b__olmoe-1b7b`).
mlx-community preference check: memo names 4-bit conversions ONLY for the OLMoE **0125** generation (not candidate 0924) and NO dense OLMo-1B conversion (UNVERIFIED-negative) → HF originals mirrored for both arms.

## Artifacts mirrored (pinned to memo-verified revisions)

- Dense: `allenai/OLMo-1B-0724-hf` @ `d7cbab742d80589e714b1a2d7f838dcd21cbe143`
  → /Users/edr/jw_models/allenai/OLMo-1B-0724-hf (5.1 GB, 2 F32 safetensors shards)
- MoE: `allenai/OLMoE-1B-7B-0924` @ `6d84c48581ece794365f2b8e9cfb043c68ade9c5`
  → /Users/edr/jw_models/allenai/OLMoE-1B-7B-0924 (13.8 GB, 3 BF16 safetensors shards)

Command (each arm):
```
/Users/edr/code/JouleWise/.venv/bin/hf download <repo> --revision <sha> --local-dir /Users/edr/jw_models/<repo>
```
Both completed exit 0.

## SHA-256 manifests

- /private/tmp/claude-501/-Users-edr-code-JouleWise/bed4bf7f-6ed5-4914-83fa-40cb7132e5a6/scratchpad/manifest-OLMo-1B-0724-hf.sha256
- /private/tmp/claude-501/-Users-edr-code-JouleWise/bed4bf7f-6ed5-4914-83fa-40cb7132e5a6/scratchpad/manifest-OLMoE-1B-7B-0924.sha256

### OLMo-1B-0724-hf
```
d40e08d04a0efefe634158b8585412cb333b8019966c3f788bdae49074ce634e  config.json
e9a6fc6755330e6da09ba04b1137c4db0744faafc0fa609ff378fd6989518295  generation_config.json
0c3e846f50db22b38cd06e3628b0bfe10f814e01217a5ac837dd2aa39ae18121  model-00001-of-00002.safetensors
0b45bdac8c7291f3b566d201ba39560d7d1696bbe43a6a0b50666c052c5b42a1  model-00002-of-00002.safetensors
fef1fef6deb95bc610ad6feda0063c91e0a766ed1e4610e26d6d2c7a9f14de33  model.safetensors.index.json
b77491e270c6fcc5b2ecf22370f7318a6a18d3cabea09ba7bab92e9bf12656c2  special_tokens_map.json
78a839c7851f14f9fb30e664c2b46166dc0628f2900679e5ec160656f702edff  tokenizer_config.json
a094266ac6c4982efba277bc251349a5a6d6ad37efb39a2a90f53d8be2a40a40  tokenizer.json
```

### OLMoE-1B-7B-0924
```
3643aa880d2f1c9b418156269ae791c73e5612d6b6b6fde0724d927cf89b6335  config.json
d77272ffaa7e62a904e8e130bb25ab11585bd4a5026e388d6d682e4b82892ce2  generation_config.json
5e3cff7e367794685c241169072c940d200918617d5e2813f1c387dff52d845e  model-00001-of-00003.safetensors
15ef5c730ee3cfed7199498788cd2faf337203fc74b529625e7502cdd759f4a7  model-00002-of-00003.safetensors
a9abac4ac1b55c9adabac721a02fa39971f103eea9a65c310972b1246de76e04  model-00003-of-00003.safetensors
0e2e1e0d8d357ac7af817cff28410c3dbad398f060c517a433e4076b2aae5579  model.safetensors.index.json
b77491e270c6fcc5b2ecf22370f7318a6a18d3cabea09ba7bab92e9bf12656c2  special_tokens_map.json
78a839c7851f14f9fb30e664c2b46166dc0628f2900679e5ec160656f702edff  tokenizer_config.json
a094266ac6c4982efba277bc251349a5a6d6ad37efb39a2a90f53d8be2a40a40  tokenizer.json
```

**G2 evidence:** `tokenizer.json`, `tokenizer_config.json`, `special_tokens_map.json` are byte-identical across arms (identical SHA-256) — tokenizer compatibility confirmed at the artifact level, stronger than the memo's config-field comparison.

## MLX load smokes (mlx-lm 0.31.3, repo venv)

### Dense arm — FAILS (memo G4 risk CONFIRMED)
```
$ .venv/bin/python -c "from mlx_lm import load, generate; m,t=load('/Users/edr/jw_models/allenai/OLMo-1B-0724-hf'); print(generate(m,t,prompt='Energy is',max_tokens=8))"
To run olmo install ai2-olmo: pip install ai2-olmo
EXIT=1
```
mlx-lm dispatches on `model_type: "olmo"` → `mlx_lm/models/olmo.py`, which `sys.exit(1)`s without the `ai2-olmo` (`hf_olmo`) package.

**Installing ai2-olmo would NOT fix it** — proven by stubbing `hf_olmo` and parsing the real `-hf` config against olmo.py's ModelArgs:
```
TypeError ModelArgs.__init__() missing 5 required positional arguments: 'd_model', 'n_layers', 'mlp_hidden_size', 'n_heads', and 'embedding_size'
```
olmo.py targets the ORIGINAL AI2 config schema; the `-hf` `OlmoForCausalLM` checkpoint is unloadable by mlx-lm 0.31.3 regardless. Options: local model-class shim, mlx conversion from the non-hf `allenai/OLMo-1B-0724` + ai2-olmo, or a different dense arm.

Verdict: **fails-with-unsupported-config-schema** (import gate: missing ai2-olmo; deeper gate: -hf config keys unparseable).

### MoE arm — as-published FAILS on a missing config default; loads with a one-knob override
As-published:
```
$ .venv/bin/python -c "... load('/Users/edr/jw_models/allenai/OLMoE-1B-7B-0924') ..."
TypeError: ModelArgs.__init__() missing 1 required positional argument: 'rms_norm_eps'
EXIT=1
```
Root cause: the 0924 `config.json` omits `rms_norm_eps` (verified: key absent from file). HF transformers' `OlmoeConfig` defaults it to **1e-05** (verified in repo venv); mlx-lm's olmoe ModelArgs makes it required.

With the HF-default supplied as an mlx-lm `model_config` override:
```
$ .venv/bin/python -c "from mlx_lm import load, generate; m,t=load('/Users/edr/jw_models/allenai/OLMoE-1B-7B-0924', model_config={'rms_norm_eps': 1e-05}); print(repr(generate(m,t,prompt='Energy is',max_tokens=8)))"
'the ability to do work.\n\n'
EXIT=0
```
Verdict: **loads-and-generates** (coherent completion) with `model_config={'rms_norm_eps': 1e-05}`; **fails-with-TypeError-missing-rms_norm_eps** exactly as published. The override value is the documented HF default, not a guess. (Equivalent durable fix: add the key to the local config.json copy — NOT done, mirror left byte-identical to upstream.)

## Per-arm verdicts

| Arm | Repo @ rev | MLX 0.31.3 smoke | Verdict |
|---|---|---|---|
| Dense | allenai/OLMo-1B-0724-hf @ d7cbab7 | FAIL (ai2-olmo gate; config schema unparseable even past it) | G4 risk CONFIRMED — unloadable without conversion or shim |
| MoE | allenai/OLMoE-1B-7B-0924 @ 6d84c48 | PASS with rms_norm_eps=1e-05 override; FAIL as-published | Loadable with one documented-default knob |

Anomalies beyond the memo: (1) MoE arm is not clean out-of-the-box either (memo marked only the dense path unverified); (2) tokenizer files byte-identical across arms (positive G2 surprise).

Not done here per rules: no repo writes, no measurements, no [QUIET-MAC]. The decisive load commands above are ready for lead re-run verbatim.
