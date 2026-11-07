# ALIGN R0 desk checks

Status: **fail**. Selection data; no R1/hardware-control claim.
Complete R0: **False**. Evidence: live_desk.
Total wall duration: 2245.751 seconds.

| Check | Model | Status | Wall seconds |
|---|---|---|---|
| host | host | pass | 0.425 |
| disk | host | diagnostic | 19.578 |
| host-identity | host | pass | 0.409 |
| model-load | D | pass | 13.659 |
| load | D | pass | 86.720 |
| template | D | diagnostic | 0.655 |
| generated | D | pass | 50.961 |
| checkpoint | D | not_required | 0.634 |
| memory | D | pass | 731.885 |
| smc | host | fail | 1310.319 |

## host (host)

```json
{
  "check": "host",
  "check_seconds": 0.4253480830229819,
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

Free after present weights: 84472860672 bytes (R0 report-only; no free-space or offload gate).
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
  "check_seconds": 0.4094000419136137,
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
  "check_seconds": 13.659107041079551,
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
    "load_wall_time_s": 1.3373057842254639,
    "memory_snapshots": [
      {
        "captured_at_s": 1794033202.6742542,
        "label": "prepare_end",
        "mlx_metal": {
          "active_memory_bytes": 28579478536,
          "api_available": true,
          "cache_memory_bytes": 10564,
          "peak_memory_bytes": 28579478536
        },
        "process_rss_bytes": 29158932480
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
  "check_seconds": 86.72013625013642,
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
    "seconds": 39.80895427,
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
  "check_seconds": 0.6344441671390086,
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
  "check_seconds": 731.8849780829623,
  "context_cap": 40960,
  "decode_tokens": 6144,
  "errors": [],
  "eval_metadata": false,
  "metadata_arrays_evaluated": 0,
  "metadata_evaluation": "not_requested",
  "model": "D",
  "note": "R1 freezes B_m; this is the council budget floor, with prompt+decode exactly at context cap.",
  "peak_bytes": 37024627804,
  "peak_limit_bytes": 45000000000,
  "positions": 40960,
  "prompt_tokens": 34816,
  "seconds": 731.2349613339175,
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
    "/Users/edr/night-align/r0-v4-20261107T0631Z/smc",
    "--gpu-step",
    "--idle-seconds",
    "300",
    "--load-seconds",
    "900",
    "--recovery-seconds",
    "600"
  ],
  "check": "smc",
  "check_seconds": 1310.3192920838483,
  "exit_code": 3,
  "note": "Idle plus load-step selection; R1 still owns thermal-control qualification.",
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
  "status": "fail",
  "stderr": "R0 refused/failed: NotQuiet: outside-tree CPU contention or unmeasured host CPU: {'interval': {'monotonic_ns': [2019685108494291, 2019721052743874], 'monotonic_raw_ns': [2019685108493874, 2019721052743374], 'wall_ns': [1794035348124711000, 1794035384068960500]}, 'error': None, 'elapsed_s': 35.944249583, 'clean': False, 'max_outside': {'pid': 547, 'command': 'softwareupdated', 'start': 'Wed Oct 14 15:08:40 2026', 'cpu_s_per_s': 0.07038678034320538}, 'outside_over_limit': [{'pid': 547, 'command': 'softwareupdated', 'start': 'Wed Oct 14 15:08:40 2026', 'cpu_s_per_s': 0.07038678034320538}, {'pid': 834, 'command': 'duetexpertd', 'start': 'Wed Oct 14 15:08:49 2026', 'cpu_s_per_s': 0.06704827692772038}], 'exited_over_limit': [], 'outside_listed': [{'pid': 547, 'command': 'softwareupdated', 'start': 'Wed Oct 14 15:08:40 2026', 'cpu_s_per_s': 0.07038678034320538}, {'pid': 834, 'command': 'duetexpertd', 'start': 'Wed Oct 14 15:08:49 2026', 'cpu_s_per_s': 0.06704827692772038}, {'pid': 3921, 'command': 'XProtectPluginSe', 'start': 'Thu Oct 22 03:08:47 2026', 'cpu_s_per_s': 0.020031020492928396}, {'pid': 415, 'command': 'WindowServer', 'start': 'Wed Oct 14 15:08:38 2026', 'cpu_s_per_s': 0.016414308459486902}, {'pid': 663, 'command': 'cloudd', 'start': 'Wed Oct 14 15:08:47 2026', 'cpu_s_per_s': 0.016136099841523494}, {'pid': 676, 'command': 'ControlCenter', 'start': 'Wed Oct 14 15:08:47 2026', 'cpu_s_per_s': 0.014466848133780992}, {'pid': 838, 'command': 'networkservicepr', 'start': 'Wed Oct 14 15:08:50 2026', 'cpu_s_per_s': 0.011962970572164078}, {'pid': 1281, 'command': 'tipsd', 'start': 'Wed Oct 14 15:10:00 2026', 'cpu_s_per_s': 0.0114065533362509}, {'pid': 687, 'command': 'nsurlsessiond', 'start': 'Wed Oct 14 15:08:47 2026', 'cpu_s_per_s': 0.010015510246467657}, {'pid': 1, 'command': 'launchd', 'start': 'Wed Oct 14 15:07:52 2026', 'cpu_s_per_s': 0.006955215448933413}, {'pid': 8987, 'command': 'trustd', 'start': 'Mon Nov 2 02:25:38 2026', 'cpu_s_per_s': 0.006398798213018455}, {'pid': 44246, 'command': 'biomesyncd', 'start': 'Fri Nov 6 23:09:41 2026', 'cpu_s_per_s': 0.005564172359146731}, {'pid': 641, 'command': 'knowledge-agent', 'start': 'Wed Oct 14 15:08:46 2026', 'cpu_s_per_s': 0.005564172359146612}, {'pid': 635, 'command': 'sysmond', 'start': 'Wed Oct 14 15:08:46 2026', 'cpu_s_per_s': 0.005007755123227503}], 'outside_total_cpu_s_per_s': 0.31910528479700334, 'outside_process_count': 724, 'tree_cpu_s_per_s': 0.05397247188372322, 'tree_process_count': 3, 'kernel_task_cpu_s_per_s': None, 'kernel_task_included': True, 'host_busy_cpu_s_per_s': 0.41842894135956354, 'host_idle_cpu_s_per_s': 15.572289318297111, 'host_ticks': {'busy_ticks': 1504, 'idle_ticks': 55973, 'cpus': 16, 'ticks_per_s': 100.0, 'elapsed_s': 35.943976416}, 'host_error': None, 'outside_aggregate_cpu_s_per_s': 0.3644564694758403, 'unattributed_cpu_s_per_s': 0.045351184678836975, 'unattributed_resolution_cpu_s_per_s': 0.43011072633768455, 'aggregate_limit_s_per_s': None, 'aggregate_over_limit': False, 'unaccounted': [{'pid': 44060, 'command': 'ps', 'start': 'Fri Nov 6 23:09:08 2026', 'reason': 'exited'}], 'raw': [{'name': 'ps.txt', 'sha256': '16f20bc605e0c6bc34531afd65df7d5e315cb6dd4790ca6512ee958727a7b47a', 'size': 49357, 'path': None}, {'name': 'ps.txt', 'sha256': 'b5acc76bfac854b17bda46f5b0d7361bcded0597230ad5e7782f0fde22d9db34', 'size': 49425, 'path': None}], 'cpu_limit_s_per_s': 0.05, 'aggregate_cpu_limit_s_per_s': None, 'aggregate_above_0_05': True, 'regressed_counters': [], 'long_interval': False}\n",
  "stdout": "",
  "step_ruling": "docs/align/r0_step_test_ruling.md",
  "timeout_seconds": 2400
}
```
