# ALIGN R0 desk checks

Status: **fail**. Selection data; no R1/hardware-control claim.
Complete R0: **False**. Evidence: live_desk.
Total wall duration: 75.546 seconds.

| Check | Model | Status | Wall seconds |
|---|---|---|---|
| host | host | pass | 0.320 |
| disk | host | diagnostic | 18.837 |
| host-identity | host | pass | 0.302 |
| model-load | D | pass | 13.538 |
| load | D | fail | 42.358 |

## host (host)

```json
{
  "check": "host",
  "check_seconds": 0.3200990839395672,
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

Free after present weights: 84073951232 bytes (R0 report-only; no free-space or offload gate).
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
  "check_seconds": 0.30178045807406306,
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
  "check_seconds": 13.538043584208935,
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
    "load_wall_time_s": 1.380091905593872,
    "memory_snapshots": [
      {
        "captured_at_s": 1793984642.265701,
        "label": "prepare_end",
        "mlx_metal": {
          "active_memory_bytes": 28579478536,
          "api_available": true,
          "cache_memory_bytes": 10564,
          "peak_memory_bytes": 28579478536
        },
        "process_rss_bytes": 29149872128
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
  "check_seconds": 42.35838962509297,
  "coherence_and_echo_are_diagnostics": true,
  "coherent": true,
  "model": "D",
  "nll_limit": 3.0,
  "nll_nats_per_token": 11.036814212799072,
  "nll_prompt_sha256": "792beb565106c53ed77695c7ccbb998b11300b3ba25e485c8c0069dcb710ac42",
  "nll_targets": 2048,
  "perplexity": 62119.43691807623,
  "short_prompt": "What is 19 plus 23? End your answer with the number alone on its own line.",
  "status": "fail"
}
```
