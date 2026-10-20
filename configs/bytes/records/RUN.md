# BYTES item G: KV records (Mac, no power capture)

Date: 2026-10-20, runs 16:04-16:10 PDT (kv and headers via `scripts/bytes_manifest.py`, runner script and log saved beside this file as `runner.sh`, `runner_log.txt`).

Interpreter for `kv`: `/Users/edr/code/JouleWise/.venv/bin/python` (Python 3.13), mlx 0.31.2, mlx-lm 0.31.3 (read from importlib.metadata). The brief named `/opt/homebrew/bin/python3.13`, but it has no mlx (`ModuleNotFoundError: No module named 'mlx'`; python3.11/3.12/3.14 also have none). The canonical venv is the interpreter `configs/b6/registration/identity_pins.json` pins, and it carries exactly the stated versions. It was only executed (PYTHONDONTWRITEBYTECODE=1), nothing in the canonical checkout was written. Header records are stdlib-only; the unit test below used `/opt/homebrew/bin/python3.13`.

Model directories: the BYTES configs (`configs/campaigns/bytes-s*-p1`, `bytes_v1/roster.json`) name HF snapshot paths for Qwen3-1.7B-4bit, Qwen3-4B-4bit and Qwen3-8B-4bit that DO NOT EXIST on this Mac (the `models--mlx-community--Qwen3-4B-4bit` cache holds only `refs/main`, no snapshots). The same-named copies under `/Users/edr/jw_models/mlx-community/` exist and their `.cache/huggingface/trees/<hash>.json` file names equal the roster revisions, so those were used with `--revision` set to the roster revision. For the other six the configs' own paths exist and were used. `--revision` for each came from `roster.json` (the snapshot hash).

Not done: Qwen3-8B-8bit. The configs name `/Users/edr/jw_models/mlx-community/Qwen3-8B-8bit`; that directory does not exist on this Mac and no copy was found in `~/.cache/huggingface/hub`. Nothing was downloaded (not authorised by the brief). Consequently only nine of ten kv records exist, `merge` was NOT run to write `configs/bytes/bytes_manifest.json`, and no manifest is committed.

## Qwen3-8B-8bit findings
- Revision: not determinable locally (no local copy, no refs). Remote metadata read-only (HF API, `https://huggingface.co/api/models/mlx-community/Qwen3-8B-8bit`, 2026-10-20 ~16:06): sha `48a0b75b1ae72503e21e1558d040bc227510ff06`, lastModified 2025-04-28T22:26:57Z. This is the current main, not a pinned download; it is not a locally verified revision.
- group_size and bits: not readable from a local config.json (no local copy). Remote `raw/main/config.json` (same date) shows `quantization = {'group_size': 64, 'bits': 8}` and `quantization_config = {'group_size': 64, 'bits': 8}`. So the assumed 64 is confirmed against the remote main config, not against any local file; it still needs checking against the downloaded copy.

## Dry run of merge (nine models, NOT committed)
`merge` over the nine existing header and kv records, writing to `/tmp` only, exited 0 and printed one difference line per model (W_bytes minus the pilot `read_meas_GB`, in bytes; the pilot column excludes KV):
```
{"W_minus_pilot_bytes": 0.0, "comparison": "W versus pilot read_meas_GB (pilot column excludes KV)", "model": "llama-3.3-70b-instruct-4bit", "pilot_read_meas_GB": 39.0973568}
{"W_minus_pilot_bytes": 0.0, "comparison": "W versus pilot read_meas_GB (pilot column excludes KV)", "model": "qwen3-1.7b-4bit", "pilot_read_meas_GB": 0.968002688}
{"W_minus_pilot_bytes": 0.0, "comparison": "W versus pilot read_meas_GB (pilot column excludes KV)", "model": "qwen3-14b-4bit", "pilot_read_meas_GB": 7.87021088}
{"W_minus_pilot_bytes": 0.0, "comparison": "W versus pilot read_meas_GB (pilot column excludes KV)", "model": "qwen3-30b-a3b-4bit", "pilot_read_meas_GB": 1.711355008}
{"W_minus_pilot_bytes": 0.0, "comparison": "W versus pilot read_meas_GB (pilot column excludes KV)", "model": "qwen3-32b-4bit", "pilot_read_meas_GB": 17.992094528}
{"W_minus_pilot_bytes": 0.0, "comparison": "W versus pilot read_meas_GB (pilot column excludes KV)", "model": "qwen3-4b-4bit", "pilot_read_meas_GB": 2.262921632}
{"W_minus_pilot_bytes": 4.76837158203125e-07, "comparison": "W versus pilot read_meas_GB (pilot column excludes KV)", "model": "qwen3-8b-4bit", "pilot_read_meas_GB": 4.257673472}
{"W_minus_pilot_bytes": 0.0, "comparison": "W versus pilot read_meas_GB (pilot column excludes KV)", "model": "qwen3-next-80b-a3b-instruct-4bit", "pilot_read_meas_GB": 2.031833728}
{"W_minus_pilot_bytes": 0.0, "comparison": "W versus pilot read_meas_GB (pilot column excludes KV)", "model": "qwen3.5-122b-a10b-4bit", "pilot_read_meas_GB": 5.070253248}
```

## Per model

### Qwen3-1.7B-4bit
- model_dir: `/Users/edr/jw_models/mlx-community/Qwen3-1.7B-4bit`
- revision (from --revision, matches record): `3b1b1768f8f8cf8351c712464f906e86c2b8269e`; header record revision `3b1b1768f8f8cf8351c712464f906e86c2b8269e`
- wall time (headers + kv, runner log): 11 s
- KV_bytes: 264241152.0
- cache_bytes after prefill: 234881024; after last token: 293601280
- (occupied_length, allocated_capacity) per layer, after prefill: [(2048, 2048)]
- (occupied_length, allocated_capacity) per layer, after last token: [(2560, 2560)]
- cache class per layer, after prefill: {'KVCache': 28}; after last token: {'KVCache': 28}
- layers: 28; prompt_tokens 2048, output_tokens 512, decode_forward_passes 512
- W_bytes (headers): 968002688.0; R_bytes: 968001536

### Qwen3-4B-4bit
- model_dir: `/Users/edr/jw_models/mlx-community/Qwen3-4B-4bit`
- revision (from --revision, matches record): `4dcb3d101c2a062e5c1d4bb173588c54ea6c4d25`; header record revision `4dcb3d101c2a062e5c1d4bb173588c54ea6c4d25`
- wall time (headers + kv, runner log): 15 s
- KV_bytes: 339738624.0
- cache_bytes after prefill: 301989888; after last token: 377487360
- (occupied_length, allocated_capacity) per layer, after prefill: [(2048, 2048)]
- (occupied_length, allocated_capacity) per layer, after last token: [(2560, 2560)]
- cache class per layer, after prefill: {'KVCache': 36}; after last token: {'KVCache': 36}
- layers: 36; prompt_tokens 2048, output_tokens 512, decode_forward_passes 512
- W_bytes (headers): 2262921632.0; R_bytes: 2262920192

### Qwen3-8B-4bit
- model_dir: `/Users/edr/jw_models/mlx-community/Qwen3-8B-4bit`
- revision (from --revision, matches record): `545dc4251c05440727734bcd94334791f6ab0192`; header record revision `545dc4251c05440727734bcd94334791f6ab0192`
- wall time (headers + kv, runner log): 20 s
- KV_bytes: 339738624.0
- cache_bytes after prefill: 301989888; after last token: 377487360
- (occupied_length, allocated_capacity) per layer, after prefill: [(2048, 2048)]
- (occupied_length, allocated_capacity) per layer, after last token: [(2560, 2560)]
- cache class per layer, after prefill: {'KVCache': 36}; after last token: {'KVCache': 36}
- layers: 36; prompt_tokens 2048, output_tokens 512, decode_forward_passes 512
- W_bytes (headers): 4257673472.0; R_bytes: 4607731712

### Qwen3-14B-4bit
- model_dir: `/Users/edr/.cache/huggingface/hub/models--mlx-community--Qwen3-14B-4bit/snapshots/a4d9b2df59d2c150bef02fcbe0d91046b7ca33a4`
- revision (from --revision, matches record): `a4d9b2df59d2c150bef02fcbe0d91046b7ca33a4`; header record revision `a4d9b2df59d2c150bef02fcbe0d91046b7ca33a4`
- wall time (headers + kv, runner log): 32 s
- KV_bytes: 377487360.0
- cache_bytes after prefill: 335544320; after last token: 419430400
- (occupied_length, allocated_capacity) per layer, after prefill: [(2048, 2048)]
- (occupied_length, allocated_capacity) per layer, after last token: [(2560, 2560)]
- cache class per layer, after prefill: {'KVCache': 40}; after last token: {'KVCache': 40}
- layers: 40; prompt_tokens 2048, output_tokens 512, decode_forward_passes 512
- W_bytes (headers): 7870210880.0; R_bytes: 8307783680

### Qwen3-30B-A3B-4bit
- model_dir: `/Users/edr/.cache/huggingface/hub/models--mlx-community--Qwen3-30B-A3B-4bit/snapshots/d388dead1515f5e085ef7a0431dd8fadf0886c57`
- revision (from --revision, matches record): `d388dead1515f5e085ef7a0431dd8fadf0886c57`; header record revision `d388dead1515f5e085ef7a0431dd8fadf0886c57`
- wall time (headers + kv, runner log): 19 s
- KV_bytes: 226492416.0
- cache_bytes after prefill: 201326592; after last token: 251658240
- (occupied_length, allocated_capacity) per layer, after prefill: [(2048, 2048)]
- (occupied_length, allocated_capacity) per layer, after last token: [(2560, 2560)]
- cache class per layer, after prefill: {'KVCache': 48}; after last token: {'KVCache': 48}
- layers: 48; prompt_tokens 2048, output_tokens 512, decode_forward_passes 512
- W_bytes (headers): 1711355008.0; R_bytes: 17174622208

### Qwen3-32B-4bit
- model_dir: `/Users/edr/.cache/huggingface/hub/models--mlx-community--Qwen3-32B-4bit/snapshots/bcaaf7f538adf166c1080a2befdb4f6019f66639`
- revision (from --revision, matches record): `bcaaf7f538adf166c1080a2befdb4f6019f66639`; header record revision `bcaaf7f538adf166c1080a2befdb4f6019f66639`
- wall time (headers + kv, runner log): 62 s
- KV_bytes: 603979776.0
- cache_bytes after prefill: 536870912; after last token: 671088640
- (occupied_length, allocated_capacity) per layer, after prefill: [(2048, 2048)]
- (occupied_length, allocated_capacity) per layer, after last token: [(2560, 2560)]
- cache class per layer, after prefill: {'KVCache': 64}; after last token: {'KVCache': 64}
- layers: 64; prompt_tokens 2048, output_tokens 512, decode_forward_passes 512
- W_bytes (headers): 17992094528.0; R_bytes: 18429667328

### Llama-3.3-70B-Instruct-4bit
- model_dir: `/Users/edr/.cache/huggingface/hub/models--mlx-community--Llama-3.3-70B-Instruct-4bit/snapshots/de2dfaf56839b7d0e834157d2401dee02726874d`
- revision (from --revision, matches record): `de2dfaf56839b7d0e834157d2401dee02726874d`; header record revision `de2dfaf56839b7d0e834157d2401dee02726874d`
- wall time (headers + kv, runner log): 128 s
- KV_bytes: 754974720.0
- cache_bytes after prefill: 671088640; after last token: 838860800
- (occupied_length, allocated_capacity) per layer, after prefill: [(2048, 2048)]
- (occupied_length, allocated_capacity) per layer, after last token: [(2560, 2560)]
- cache class per layer, after prefill: {'KVCache': 80}; after last token: {'KVCache': 80}
- layers: 80; prompt_tokens 2048, output_tokens 512, decode_forward_passes 512
- W_bytes (headers): 39097356800.0; R_bytes: 39688355840

### Qwen3-Next-80B-A3B-Instruct-4bit
- model_dir: `/Users/edr/.cache/huggingface/hub/models--mlx-community--Qwen3-Next-80B-A3B-Instruct-4bit/snapshots/d8a069bfa8ae87d3d468412e1034acae19b5892b`
- revision (from --revision, matches record): `d8a069bfa8ae87d3d468412e1034acae19b5892b`; header record revision `d8a069bfa8ae87d3d468412e1034acae19b5892b`
- wall time (headers + kv, runner log): 26 s
- KV_bytes: 133890048.0
- cache_bytes after prefill: 127598592; after last token: 140181504
- (occupied_length, allocated_capacity) per layer, after prefill: [(2048, 2048), (None, None)]
- (occupied_length, allocated_capacity) per layer, after last token: [(2560, 2560), (None, None)]
- cache class per layer, after prefill: {'ArraysCache': 36, 'KVCache': 12}; after last token: {'ArraysCache': 36, 'KVCache': 12}
- layers: 48; prompt_tokens 2048, output_tokens 512, decode_forward_passes 512
- W_bytes (headers): 2031833728.0; R_bytes: 44844060160

### Qwen3.5-122B-A10B-4bit
- model_dir: `/Users/edr/jw_models/mlx-community/Qwen3.5-122B-A10B-4bit`
- revision (from --revision, matches record): `e9c67b08899964be5fdd069bb1b4bc8907fe68f5`; header record revision `e9c67b08899964be5fdd069bb1b4bc8907fe68f5`
- wall time (headers + kv, runner log): 42 s
- KV_bytes: 210272256.0
- cache_bytes after prefill: 203980800; after last token: 216563712
- (occupied_length, allocated_capacity) per layer, after prefill: [(2048, 2048), (None, None)]
- (occupied_length, allocated_capacity) per layer, after last token: [(2560, 2560), (None, None)]
- cache class per layer, after prefill: {'ArraysCache': 36, 'KVCache': 12}; after last token: {'ArraysCache': 36, 'KVCache': 12}
- layers: 48; prompt_tokens 2048, output_tokens 512, decode_forward_passes 512
- W_bytes (headers): 5070253248.0; R_bytes: 68690732544

mlx 0.31.2 mlx-lm 0.31.3
Notes on the table: `(None, None)` in the per-layer occupied/allocated pair belongs to the ArraysCache (recurrent-state) layers, which carry no offset or key tensor; the set shows the two layer kinds present. Wall time is headers plus kv per model, from `runner_log.txt` (the kv step includes model load, a 4-token warmup, a 5 s sleep, and the measured prefill+512 decode passes).

## Tests
`tests/test_bytes_manifest.py` (the only test module naming bytes_manifest): `python3.13 -m unittest tests.test_bytes_manifest` with PYTHONPATH set to the worktree, JW_B5_SYNTHETIC_ONLY=1, TMPDIR=/tmp/af419-kv-tmp/t: Ran 15 tests, OK. (An earlier mis-specified `discover -s tests -p test_bytes_manifest.py` command also ran a broader set of 342 tests in the worktree by accident, errors=2 from `tests.flags` import of `test_b6_emitters`; this is not a result of record.)
