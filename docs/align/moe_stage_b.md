# MoE Stage B: routing visibility in power

Status: design and synthetic validation lane; no hardware measurement or detection claim.

Stage A asks whether routing statistics separate conditions. Stage B asks whether a
measured power feature preserves enough of that difference. Power counts work; it
cannot identify reasoning performed within a fixed forward pass.

## Physical model

Use layer-qualified expert identities. Permanently resident experts consume no
offload traffic. An offloaded expert consumes its stored tensor bytes on a cache
miss; cache hits consume no additional offload traffic. A miss contributes
`bytes * joules_per_byte` and occupies `bytes / bandwidth_bytes_per_second`.
Both coefficients are inputs tied to a named memory path and calibration source.
The model isolates this incremental traffic energy from compute and idle power.

All-resident routing with fixed top-k is the negative control: changing expert
identities moves no additional bytes in this model. A routing-dependent signal
requires a change in locality or residency, not merely different expert IDs.

`RouterLog` contains phases and routing order but no timestamps or batch boundaries.
A lane-local timing adapter will retain those assumptions and flags without
changing the shared records contract. Decode-only conclusions must not silently
treat token-serial prefill as a faithful batched-prefill model.

## Upstream implementation checked

Checked the current public llama.cpp source at commit
[`a37cc46104eb50900d5ab4a9ba02a0abdac039db`](https://github.com/ggml-org/llama.cpp/tree/a37cc46104eb50900d5ab4a9ba02a0abdac039db).

- [`common/arg.cpp`](https://github.com/ggml-org/llama.cpp/blob/a37cc46104eb50900d5ab4a9ba02a0abdac039db/common/arg.cpp)
  defines `--cpu-moe`, `--n-cpu-moe N` (first N layers),
  `-ot` / `--override-tensor`, and `--moe-cache-mib N`.
- [`src/llama-moe-cache.cpp`](https://github.com/ggml-org/llama.cpp/blob/a37cc46104eb50900d5ab4a9ba02a0abdac039db/src/llama-moe-cache.cpp)
  implements a shared segmented LRU cache for compatible layers, promotes hits
  before fills, protects all experts in the current request from eviction, and
  bypasses cache planning for sufficiently large batches. A plain LRU estimate
  must not be represented as an exact replay of this policy.
- [`src/llama-graph.cpp`](https://github.com/ggml-org/llama.cpp/blob/a37cc46104eb50900d5ab4a9ba02a0abdac039db/src/llama-graph.cpp)
  exposes selected expert IDs through the evaluation tensor `ffn_moe_topk`.
  [`include/llama.h`](https://github.com/ggml-org/llama.cpp/blob/a37cc46104eb50900d5ab4a9ba02a0abdac039db/include/llama.h)
  has `cb_eval`; the eval-callback example demonstrates the callback seam.

CPU offload with the MoE GPU cache disabled is **not** equivalent to uploading
every selected expert over PCIe. The CPU executes host-resident work and
activation transfers also matter. On Jetson the CPU and GPU share DRAM, so a
CPU/GPU placement change is not a discrete-GPU PCIe weight-transfer experiment.

## Sensor and decision plan

A local simulator is needed: the spine has no `sensor_sim.py`. It will average
the actual time profile over each sensor's acquisition window, then sample and
quantize. The requested NVML comparison is a 25 ms window every 100 ms, with
phase sweeps exposing unseen activity and aliasing. INA3221 cadence, conversion
window and power quantum remain configurable from the deployed rail setup.

Recover a known routing statistic using decode energy per token, its variance,
and token-frequency spectral features. Keep task groups separate in validation.
A parameterized Stage A effect and statistical design determine the correlation
Stage B would require; neither a synthetic correlation nor a nominal sensor
quantum establishes physical detectability.

The completed lane will include runnable end-to-end synthetic episodes,
calibrated-parameter instructions for the Jetson Orin Nano Super and RTX 3080 Ti,
and an explicit conditional go/no-go decision.
