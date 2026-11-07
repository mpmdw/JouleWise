# ALIGN R0 desk checks

Status: **refused**. Selection data; no R1/hardware-control claim.
Complete R0: **False**. Evidence: live_desk.
Total wall duration: 905.142 seconds.

| Check | Model | Status | Wall seconds |
|---|---|---|---|
| host | host | pass | 0.318 |
| disk | host | diagnostic | 18.474 |
| host-identity | host | pass | 0.300 |
| model-load | D | pass | 13.534 |
| load | D | pass | 86.522 |
| template | D | diagnostic | 0.520 |
| generated | D | pass | 49.819 |
| checkpoint | D | not_required | 0.495 |
| memory | D | pass | 733.005 |
| smc | host | refused | 1.925 |

## host (host)

```json
{
  "check": "host",
  "check_seconds": 0.31789762480184436,
  "note": "Read-only desk readiness; R1 lever adoption and arm readiness require their own gates.",
  "probes": {
    "physical_memory": {
      "status": "pass",
      "stdout": "137438953472\n"
    },
    "pmset_battery": {
      "status": "pass",
      "stdout": "Now drawing from 'AC Power'\n -InternalBattery-0 (id=23265379)\t100%; charged; 0:00 remaining present: true\n"
    },
    "pmset_custom": {
      "status": "pass",
      "stdout": "Battery Power:\n Sleep On Power Button 1\n powermode            0\n standby              1\n ttyskeepawake        1\n hibernatemode        3\n powernap             1\n hibernatefile        /var/vm/sleepimage\n displaysleep         5\n womp                 0\n networkoversleep     0\n sleep                0\n lessbright           1\n tcpkeepalive         1\n disksleep            10\nAC Power:\n Sleep On Power Button 1\n powermode            0\n standby              1\n ttyskeepawake        1\n hibernatemode        3\n powernap             1\n hibernatefile        /var/vm/sleepimage\n displaysleep         0\n womp                 1\n networkoversleep     0\n sleep                0\n tcpkeepalive         1\n disksleep            10\n"
    },
    "pmset_thermal": {
      "status": "pass",
      "stdout": "Note: No thermal warning level has been recorded\nNote: No performance warning level has been recorded\nNote: No CPU power status has been recorded\n"
    },
    "wired_limit": {
      "status": "pass",
      "stdout": "iogpu.wired_limit_mb: 0\n"
    }
  },
  "readiness": {
    "observed_lowpowermode": null,
    "observed_power_mode": "0",
    "on_ac": true,
    "power_mode_ok": true
  },
  "status": "pass"
}
```

## disk (host)

Free after present weights: 84255961088 bytes (R0 report-only; no free-space or offload gate).
W1 arm gate, evaluated separately after R0: ≥80000000000 bytes and configured offload hash matches.
SMC capture: 1800 s; journal estimate: 29491200 bytes.

| Model | Observed bytes | Design download bytes | Difference |
|---|---|---|---|
| D | 29531527104 | 29531521322 | 5782 |
Configured W1 offloads (not verified during R0): [].
W1 two copies: 37.4 GB; D windows two copies: 52.9 GB (rounded planning estimates). D and 30B anchor file hashes are in JSON.

## host-identity (host)

```json
{
  "check": "host-identity",
  "check_seconds": 0.3001242920290679,
  "expected_hw_model": "Mac15,9",
  "hw_memsize": 137438953472,
  "hw_model": "Mac15,9",
  "minimum_memory_bytes": 137438953472,
  "status": "pass"
}
```

## model-load (D)

```json
{
  "check": "model-load",
  "check_seconds": 13.533690584124997,
  "device_info": {
    "architecture": "applegpu_g15s",
    "device_name": "Apple M3 Max",
    "max_buffer_length": 86586540032,
    "max_recommended_working_set_size": 115448725504,
    "memory_size": 137438953472,
    "resource_limit": 499000
  },
  "load": {
    "adapter": "mlx_runtime",
    "detokenizer": {
      "class": "mlx_lm.tokenizer_utils.BPEStreamingDetokenizer",
      "path": "prepared_bpe_shallow_copy"
    },
    "load_wall_time_s": 1.3688220977783203,
    "memory_snapshots": [
      {
        "captured_at_s": 1794016243.200589,
        "label": "prepare_end",
        "mlx_metal": {
          "active_memory_bytes": 28579478536,
          "api_available": true,
          "cache_memory_bytes": 10564,
          "peak_memory_bytes": 28579478536
        },
        "process_rss_bytes": 29152444416
      }
    ],
    "mlx_lm_version": "0.31.3",
    "mlx_version": "0.31.2",
    "model_artifact_identity": {
      "algorithm": "sha256",
      "files": {
        "model-00001-of-00006.safetensors": "c7921fe72af5c961c3c4230ea25068ed6d1e502d5ecb2b4a53b7c9c213effa0c",
        "model-00002-of-00006.safetensors": "e9d93d15495354045da281f102649b99793e5b6ed0e05852c58f46e6616b54a0",
        "model-00003-of-00006.safetensors": "7015f40310c86a18230e28644832b624532333d5dfbf7584e6c62341dbd8975e",
        "model-00004-of-00006.safetensors": "7dc8ae53ed51d153e6b59499cdf004bf6ef15aab6757c7604ed4834774abc2c2",
        "model-00005-of-00006.safetensors": "8817c22c01aebdcde54eac315e9766f705eb512ba7ba84ac47501c663f930ac5",
        "model-00006-of-00006.safetensors": "fce51843fc07e1c67c5ec6d19edb46e4fa8d2b51a1cb6c8316b0a7cc069c0eb4"
      },
      "folded_sha256": "a8d1c5c963787dd9dc524912e05d409172124da773d196e8f5123820b4c36b30",
      "inventory": [
        {
          "path": "model-00001-of-00006.safetensors",
          "resolved_path": "/Users/edr/jw_models/mlx-community/Qwen3.8-27B-8bit/model-00001-of-00006.safetensors",
          "sha256": "c7921fe72af5c961c3c4230ea25068ed6d1e502d5ecb2b4a53b7c9c213effa0c",
          "size_bytes": 5317707581,
          "symlink": false
        },
        {
          "path": "model-00002-of-00006.safetensors",
          "resolved_path": "/Users/edr/jw_models/mlx-community/Qwen3.8-27B-8bit/model-00002-of-00006.safetensors",
          "sha256": "e9d93d15495354045da281f102649b99793e5b6ed0e05852c58f46e6616b54a0",
          "size_bytes": 5354102610,
          "symlink": false
        },
        {
          "path": "model-00003-of-00006.safetensors",
          "resolved_path": "/Users/edr/jw_models/mlx-community/Qwen3.8-27B-8bit/model-00003-of-00006.safetensors",
          "sha256": "7015f40310c86a18230e28644832b624532333d5dfbf7584e6c62341dbd8975e",
          "size_bytes": 5354184694,
          "symlink": false
        },
        {
          "path": "model-00004-of-00006.safetensors",
          "resolved_path": "/Users/edr/jw_models/mlx-community/Qwen3.8-27B-8bit/model-00004-of-00006.safetensors",
          "sha256": "7dc8ae53ed51d153e6b59499cdf004bf6ef15aab6757c7604ed4834774abc2c2",
          "size_bytes": 5337309653,
          "symlink": false
        },
        {
          "path": "model-00005-of-00006.safetensors",
          "resolved_path": "/Users/edr/jw_models/mlx-community/Qwen3.8-27B-8bit/model-00005-of-00006.safetensors",
          "sha256": "8817c22c01aebdcde54eac315e9766f705eb512ba7ba84ac47501c663f930ac5",
          "size_bytes": 5292848464,
          "symlink": false
        },
        {
          "path": "model-00006-of-00006.safetensors",
          "resolved_path": "/Users/edr/jw_models/mlx-community/Qwen3.8-27B-8bit/model-00006-of-00006.safetensors",
          "sha256": "fce51843fc07e1c67c5ec6d19edb46e4fa8d2b51a1cb6c8316b0a7cc069c0eb4",
          "size_bytes": 2845065477,
          "symlink": false
        }
      ],
      "kind": "file_set",
      "root": "/Users/edr/jw_models/mlx-community/Qwen3.8-27B-8bit",
      "status": "ok"
    },
    "model_config_eos_token_id": [
      248046,
      248044
    ],
    "model_config_name": "qwen3_5",
    "model_revision": "815b83c0df8ffd1d1b5244cf75fd6ef14fca9ef9",
    "model_source": "/Users/edr/jw_models/mlx-community/Qwen3.8-27B-8bit",
    "model_source_is_local_path": true,
    "quantization": "int8",
    "transformers_version": "5.12.1",
    "weight_format": "mlx"
  },
  "model": "D",
  "status": "pass"
}
```

## load (D)

```json
{
  "check": "load",
  "check_seconds": 86.5219319590833,
  "coherence_and_echo_are_diagnostics": true,
  "coherent": true,
  "generation_summary": {
    "calls": [
      {
        "arguments_json": "{\"min_occurrences\":2}",
        "name": "analyze_spam_patterns"
      }
    ],
    "decode": "greedy",
    "problems": [],
    "requested_tool": "analyze_spam_patterns",
    "retried": false,
    "seconds": 40.196835459,
    "status": "pass",
    "tokens": 109
  },
  "model": "D",
  "nll_loss_profile": {
    "bins256": [
      4.56392028555274,
      10.333468578755856,
      10.30358424037695,
      7.948755998164415,
      13.199467960745096,
      15.23964163288474,
      15.64854035153985,
      11.057133719325066
    ],
    "fixture_sha256": "792beb565106c53ed77695c7ccbb998b11300b3ba25e485c8c0069dcb710ac42",
    "losses_sha256": "0f6dc989ba2706fef42244aeb922b745fb82bff4e84cab98d2a9ca9927b706f5",
    "model_revision": "815b83c0df8ffd1d1b5244cf75fd6ef14fca9ef9",
    "nll_nats_per_token": 11.03681409591809,
    "schema": "joulewise.align.r0.nll_loss_profile.v1",
    "stack_versions": {
      "mlx": "0.31.2",
      "mlx-lm": "0.31.3",
      "transformers": "5.12.1"
    },
    "targets": 2048
  },
  "nll_loss_profile_sha256": "61170b06734eb41540b71c88f32be069cdf2ba395168bc1ce42ba56fe743e686",
  "nll_mode": "reference",
  "nll_nats_per_token": 11.03681409591809,
  "nll_nonfinite_count": 0,
  "nll_prompt_sha256": "792beb565106c53ed77695c7ccbb998b11300b3ba25e485c8c0069dcb710ac42",
  "nll_reproduction": {
    "status": "not_pinned"
  },
  "nll_targets": 2048,
  "nll_verdict": {
    "bin_deltas": [
      -0.003979714447259752,
      0.08096857875585606,
      -0.02281575962305027,
      0.02395599816441507,
      0.06216796074509645,
      -0.18385836711525982,
      -0.20695964846014903,
      0.03123371932506558
    ],
    "bins256": [
      4.56392028555274,
      10.333468578755856,
      10.30358424037695,
      7.948755998164415,
      13.199467960745096,
      15.23964163288474,
      15.64854035153985,
      11.057133719325066
    ],
    "delta_nats_per_token": -0.02738590408191044,
    "entry": "D",
    "fixture_sha256": "792beb565106c53ed77695c7ccbb998b11300b3ba25e485c8c0069dcb710ac42",
    "loss_profile_sha256": "61170b06734eb41540b71c88f32be069cdf2ba395168bc1ce42ba56fe743e686",
    "max_abs_bin_delta": 0.20695964846014903,
    "mode": "reference",
    "model_revision": "815b83c0df8ffd1d1b5244cf75fd6ef14fca9ef9",
    "nll_nats_per_token": 11.03681409591809,
    "reason": null,
    "reference_bins256": [
      4.5679,
      10.2525,
      10.3264,
      7.9248,
      13.1373,
      15.4235,
      15.8555,
      11.0259
    ],
    "reference_config_sha256": "d62016921f16e937e452a458c740654805a5c0243b15c651139e8faca7eedf95",
    "reference_implementation": "HF transformers 5.22.1, Qwen3_5DecoderLayer, float32 weights and activations (torch MPS), layer-streamed",
    "reference_nll_nats_per_token": 11.0642,
    "reproduction": {
      "status": "not_pinned"
    },
    "status": "pass",
    "targets": 2048,
    "tolerance": {
      "basis": "Observed |mlx - hf32| on this fixture: mean 0.021 (mlx_lm bf16 upstream), 0.029 (fresh 8-bit and the D tensors), 0.028 (R0 chunked path, 11.0368); worst 256-target bin 0.243 (bf16), 0.255 (8-bit/D), 0.193 (R0 chunked). Tolerances are ~3.5x and ~2x the worst observed. Scope: this tier detects gross runtime/artifact faults (wrong or permuted weights, cache/position/target-shift bugs, first/last-layer drops, zeroed or early-layer-scaled tensors, layer swaps); it does NOT detect subtle numeric faults (sibling fault injection: middle-layer skip delta 0.017, logit temperature 1.2, per-vocab logit bias, x1.5 late-layer down_proj scales all pass; docs/align/reviews/2026-11-06-r0-load-reference-executing-review.md). Subtle-numeric faithfulness of D on mlx was established off-Mac by the per-layer HF-vs-MLX comparison (lane/2026-11-06-r0-d-nll-diagnosis @62bc719f7, results/per_layer_divergence_27b.txt). Later drift is caught by the optional exact-reproduction tier ('reproduce'), see docs/align/v4/R0-LOAD-REFERENCE-NOTE.md.",
      "bin_nats_per_token": 0.5,
      "mean_nats_per_token": 0.1
    }
  },
  "perplexity": 62119.42965749579,
  "reasons": [],
  "short_prompt": "What is 19 plus 23? End your answer with the number alone on its own line.",
  "status": "pass"
}
```

## template (D)

Synthetic prefix stable: **False**. B7 is decided by generated evidence.
| Turn | Rewritten prefix tokens | Closed reasoning |
|---|---|---|
| 0 | 12 | True |
| 1 | 12 | True |
| 2 | 12 | True |
| 3 | 12 | True |
| 4 | 12 | True |
| 5 | 12 | True |
| 6 | 12 | True |
| 7 | 12 | True |
| 8 | 12 | True |
| 9 | 12 | True |
| 10 | 12 | True |
| 11 | 12 | True |

## generated (D)

| Turn | Rewritten prefix tokens | Closed reasoning |
|---|---|---|
| 0 | 0 | True |
| 1 | 0 | True |
| 2 | 0 | True |
| 3 | 0 | True |
| 4 | 0 | True |
| 5 | 0 | True |
| 6 | 0 | True |
| 7 | 0 | True |
| 8 | 0 | True |
| 9 | 0 | True |
| 10 | 0 | True |
| 11 | 0 | True |

## checkpoint (D)

```json
{
  "check": "checkpoint",
  "check_seconds": 0.49502366594970226,
  "eligible_transitions": 12,
  "model": "D",
  "rewind_fraction": 0.0,
  "status": "not_required"
}
```

## memory (D)

```json
{
  "bars_are_council_guesses": true,
  "cache_classes": [
    "ArraysCache",
    "ArraysCache",
    "ArraysCache",
    "KVCache",
    "ArraysCache",
    "ArraysCache",
    "ArraysCache",
    "KVCache",
    "ArraysCache",
    "ArraysCache",
    "ArraysCache",
    "KVCache",
    "ArraysCache",
    "ArraysCache",
    "ArraysCache",
    "KVCache",
    "ArraysCache",
    "ArraysCache",
    "ArraysCache",
    "KVCache",
    "ArraysCache",
    "ArraysCache",
    "ArraysCache",
    "KVCache",
    "ArraysCache",
    "ArraysCache",
    "ArraysCache",
    "KVCache",
    "ArraysCache",
    "ArraysCache",
    "ArraysCache",
    "KVCache",
    "ArraysCache",
    "ArraysCache",
    "ArraysCache",
    "KVCache",
    "ArraysCache",
    "ArraysCache",
    "ArraysCache",
    "KVCache",
    "ArraysCache",
    "ArraysCache",
    "ArraysCache",
    "KVCache",
    "ArraysCache",
    "ArraysCache",
    "ArraysCache",
    "KVCache",
    "ArraysCache",
    "ArraysCache",
    "ArraysCache",
    "KVCache",
    "ArraysCache",
    "ArraysCache",
    "ArraysCache",
    "KVCache",
    "ArraysCache",
    "ArraysCache",
    "ArraysCache",
    "KVCache",
    "ArraysCache",
    "ArraysCache",
    "ArraysCache",
    "KVCache"
  ],
  "check": "memory",
  "check_seconds": 733.004888625117,
  "context_cap": 40960,
  "decode_tokens": 6144,
  "errors": [],
  "eval_metadata": false,
  "metadata_arrays_evaluated": 0,
  "metadata_evaluation": "not_requested",
  "model": "D",
  "note": "R1 freezes B_m; this is the council budget floor, with prompt+decode exactly at context cap.",
  "peak_bytes": 37025381468,
  "peak_limit_bytes": 45000000000,
  "positions": 40960,
  "prompt_tokens": 34816,
  "seconds": 732.4916171669029,
  "status": "pass",
  "swap_after_bytes": 9237954,
  "swap_before_bytes": 9237954,
  "token_budget": 6144
}
```

## smc (host)

```json
{
  "argv": [
    "/Users/edr/night-custody/measurement/JouleWise-measurement-20261102-align-pilot2/.venv/bin/python",
    "-B",
    "/Users/edr/night-custody/measurement/JouleWise-measurement-20261102-align-pilot2/scripts/align_smc_enumerate.py",
    "--output",
    "/Users/edr/night-align/r0-v4-20261107T0149Z/smc",
    "--gpu-step",
    "--idle-seconds",
    "300",
    "--load-seconds",
    "900",
    "--recovery-seconds",
    "600"
  ],
  "check": "smc",
  "check_seconds": 1.9248591249343008,
  "exit_code": 3,
  "note": "Idle plus load-step selection; R1 still owns thermal-control qualification.",
  "refusal": "machine occupied or census indeterminate: {'monotonic_s': 2001452.695444833, 'resolved_custody_parents': ['/Users/edr/night-custody'], 'installed_night_agents': [], 'launchctl': {'exit_code': 113, 'stdout': '', 'stderr': 'Bad request.\\nCould not find service \"com.joulewise.night\" in domain for user gui: 501\\n'}, 'agent': {'argv': ('/usr/bin/pgrep', '-a', '-lf', '[c]odex|[c]laude'), 'exit_code': 1, 'stdout': '', 'stderr': '', 'monotonic_ns': 2001452723871416, 'stdout_bytes': None}, 'custody': {'refusals': [], 'warnings': ['stale dead owner: /Users/edr/night-custody/active-campaigns/48968-5cc30d52d8ba1a3ce21cae0eef44607bd09517787a743fe1.json', 'stale dead owner: /Users/edr/night-custody/active-campaigns/38552-6d4194d19d3f296dec02b6c0e288387c856d3fb0f4eaf1c6.json', 'stale dead owner: /Users/edr/night-custody/active-campaigns/78528-54dc846582ea4c4417ea90a0b1135d1ef376abf205bff6bd.json', 'stale dead owner: /Users/edr/night-custody/active-campaigns/38385-f57b820a00858f76999b50a4c2b72b61186e3c3698c51f8e.json', 'stale dead owner: /Users/edr/night-custody/active-campaigns/94658-9ba30bfbc8314b661d7b1766f7287a58aa3e5db086d130aa.json', 'stale dead owner: /Users/edr/night-custody/active-campaigns/36590-d515dea00f46d7127c7415474cb538f5a6699f02adb3206b.json', 'stale dead owner: /Users/edr/night-custody/active-campaigns/57492-83f4f69e1edb3ff283814ea6df1b5dbdb6d21398ce43f995.json', 'stale dead owner: /Users/edr/night-custody/active-campaigns/94330-d2ae1de2d69ceda12cb7111612c52ff69cdf4527ff8791c7.json', 'stale dead owner: /Users/edr/night-custody/active-campaigns/84715-fc788594f075a6c6e5f3fc1d6ed029ecba83965334b4c5c2.json', 'stale dead owner: /Users/edr/night-custody/active-campaigns/98110-82119e421c1adfe7d85534dd65cc795e985a4f6ea93df91d.json', 'stale dead owner: /Users/edr/night-custody/active-campaigns/85784-23e7245d27e40908c925bbcf0a9e2e07571db18fc1ac26a8.json', 'stale dead owner: /Users/edr/night-custody/active-campaigns/68684-a97701da6a451abdd7acb1028bda4f2a8f55e5db525ae057.json', 'stale dead owner: /Users/edr/night-custody/active-campaigns/62346-f06b54684fe6049860045d50d221f7eaa5824c45f3f898c2.json', 'stale dead owner: /Users/edr/night-custody/active-campaigns/36581-4f2687d554cfc5c621f8e054bbeab2f9569cc9e8e0145257.json', 'stale dead owner: /Users/edr/night-custody/active-campaigns/42819-059c083804d959162b41d6002d79aa4217588b66a78db6c1.json', 'stale dead owner: /Users/edr/night-custody/active-campaigns/9065-ddaea9ca1c8d47902412201af6909e62b4f185490055c7fb.json', 'stale dead owner: /Users/edr/night-custody/active-campaigns/13457-ea123397bfc9eb27a25b10b186969d9384505d4b52990cd6.json', 'stale dead owner: /Users/edr/night-custody/active-campaigns/4198-d1982fd3a16dce106aaff200a62b0c38f3cb2e9bd7687fa6.json', 'stale dead owner: /Users/edr/night-custody/active-campaigns/64585-98f9976ae4492ec178efc55b48b0a5ebde8698d0ee46b88c.json', 'stale dead owner: /Users/edr/night-custody/active-campaigns/44242-a4a3b3d783e80574a67d464a4329b6b79a20d00ac903617e.json', 'stale dead owner: /Users/edr/night-custody/active-campaigns/29008-ca38174a3be25cd74ef93b087645d003275a2835352118f1.json', 'stale dead owner: /Users/edr/night-custody/active-campaigns/57389-18ded853892b5f8b06179a02b255cffe72aef8bec545dcc3.json', 'stale dead owner: /Users/edr/night-custody/active-campaigns/68617-90c63d0690d25676b2042671093b08d38aa372622c4b7134.json', 'stale dead owner: /Users/edr/night-custody/active-campaigns/8448-0aded8756d40078e49c424f2ac8a8dfe3579cc5202f63f5b.json', 'stale dead owner: /Users/edr/night-custody/active-campaigns/42718-a3fc390b957b2e81837fed71bf240892d163e5e56a948d9e.json', 'stale dead owner: /Users/edr/night-custody/active-campaigns/42799-b22be68560f29011277ec7b0f34b055750cf4fc902765daf.json', 'stale dead owner: /Users/edr/night-custody/active-campaigns/36480-ca5cf391aa963fbaeb8ff16e0ba9c2664ddc762e489e2a41.json', 'stale dead owner: /Users/edr/night-custody/active-campaigns/50277-21a0f0bcbf88893ee3394da93721c977104693931985caaf.json', 'stale dead owner: /Users/edr/night-custody/active-campaigns/70643-d63d74c20f65a33bb084a0986e54de3e49ab8d81e5b5eca5.json', 'stale dead owner: /Users/edr/night-custody/active-campaigns/84860-ef6cfa75708b67ca0974b734ec381a3999cef4c166269efa.json', 'stale dead owner: /Users/edr/night-custody/active-campaigns/13420-96880f7d9034e020bb9dc5be17ba13aa8c5d5a9c73baa3ca.json', 'stale dead owner: /Users/edr/night-custody/active-campaigns/20687-9164a6725ed6b1ba4399e5f956eb441f57d8556d4928bd94.json', 'stale dead owner: /Users/edr/night-custody/active-campaigns/92296-80421f208f1176236f7e5738119ece03181d2f6fd27b3d47.json', 'stale dead owner: /Users/edr/night-custody/active-campaigns/53642-9239952a38b6006030399a159e37ca407ea02c789c40d1d5.json']}, 'busy': [(18002, 6.0, '/System/Library/Frameworks/CoreServices.framework/Versions/A/Frameworks/Metadata.framework/Versions/A/Support/mdworker_shared -s mdworker -c MDSImporterWorker -m com.apple.mdworker.shared')], 'chains': []}",
  "selection_status": "PROVISIONAL",
  "smc_source_commit": "58525031a",
  "smc_step_budget": {
    "capture_seconds": 1800,
    "journal_bytes_estimate": 29491200,
    "journal_bytes_per_slot_estimate": 16384,
    "journal_estimate_note": "16 KiB per 1 Hz slot; verify actual size after enumeration.",
    "profile": {
      "idle_seconds": 300,
      "load_seconds": 900,
      "recovery_seconds": 600
    },
    "sample_period_seconds": 1,
    "timeout_seconds": 2400
  },
  "status": "refused",
  "stderr": "R0 refused/failed: NotQuiet: outside-tree CPU contention or unmeasured host CPU: {'interval': {'monotonic_ns': [2001451478617229, 2001452657659187], 'monotonic_raw_ns': [2001451478616520, 2001452657657104], 'wall_ns': [1794017114494834000, 1794017115673876500]}, 'error': None, 'elapsed_s': 1.179041958, 'clean': False, 'max_outside': {'pid': 18002, 'command': 'mdworker_shared', 'start': 'Fri Nov 6 18:05:15 2026', 'cpu_s_per_s': 0.10177754844582045}, 'outside_over_limit': [{'pid': 18002, 'command': 'mdworker_shared', 'start': 'Fri Nov 6 18:05:15 2026', 'cpu_s_per_s': 0.10177754844582045}, {'pid': 18001, 'command': 'mdworker_shared', 'start': 'Fri Nov 6 18:05:15 2026', 'cpu_s_per_s': 0.07633316133436534}], 'exited_over_limit': [], 'outside_listed': [{'pid': 18002, 'command': 'mdworker_shared', 'start': 'Fri Nov 6 18:05:15 2026', 'cpu_s_per_s': 0.10177754844582045}, {'pid': 18001, 'command': 'mdworker_shared', 'start': 'Fri Nov 6 18:05:15 2026', 'cpu_s_per_s': 0.07633316133436534}, {'pid': 1, 'command': 'launchd', 'start': 'Wed Oct 14 15:07:52 2026', 'cpu_s_per_s': 0.01696292474134034}, {'pid': 370, 'command': 'mds', 'start': 'Wed Oct 14 15:08:38 2026', 'cpu_s_per_s': 0.008481462372212938}, {'pid': 408, 'command': 'notifyd', 'start': 'Wed Oct 14 15:08:38 2026', 'cpu_s_per_s': 0.00848146237067017}, {'pid': 651, 'command': 'lsd', 'start': 'Wed Oct 14 15:08:47 2026', 'cpu_s_per_s': 0.008481462370489376}, {'pid': 417, 'command': 'cfprefsd', 'start': 'Wed Oct 14 15:08:38 2026', 'cpu_s_per_s': 0.008481462370477323}, {'pid': 631, 'command': 'cfprefsd', 'start': 'Wed Oct 14 15:08:46 2026', 'cpu_s_per_s': 0.008481462370477323}], 'outside_total_cpu_s_per_s': 0.23748094637585326, 'outside_process_count': 725, 'tree_cpu_s_per_s': 0.01696292474097007, 'tree_process_count': 3, 'kernel_task_cpu_s_per_s': None, 'kernel_task_included': True, 'host_busy_cpu_s_per_s': 0.26692677205330567, 'host_idle_cpu_s_per_s': 15.722847928043102, 'host_ticks': {'busy_ticks': 31, 'idle_ticks': 1826, 'cpus': 16, 'ticks_per_s': 100.0, 'elapsed_s': 1.161367208}, 'host_error': None, 'outside_aggregate_cpu_s_per_s': 0.2499638473123356, 'unattributed_cpu_s_per_s': 0.012482900936482327, 'unattributed_resolution_cpu_s_per_s': 13.133213838835639, 'aggregate_limit_s_per_s': 0.05, 'aggregate_over_limit': True, 'unaccounted': [{'pid': 18000, 'command': 'ps', 'start': 'Fri Nov 6 18:05:14 2026', 'reason': 'exited'}], 'raw': [{'name': 'ps.txt', 'sha256': 'b6e052160e7a6b9ed81f74467f9ce82a1fce29ecd37c3e0f803e01dc25570c4d', 'size': 49357, 'path': None}, {'name': 'ps.txt', 'sha256': '5c01f958b38302851f705a028f7aef1f02a566a24647e8a9dad66dac99f9bb31', 'size': 49493, 'path': None}], 'cpu_limit_s_per_s': 0.05, 'aggregate_cpu_limit_s_per_s': 0.05}\n",
  "stdout": "",
  "step_ruling": "docs/align/r0_step_test_ruling.md",
  "timeout_seconds": 2400
}
```
