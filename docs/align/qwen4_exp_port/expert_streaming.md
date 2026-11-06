# Optional routed-expert streaming reference

This is the P10 quality-reference path. It is deliberately **off by default** and
must not be used for JouleWise energy measurements: storage traffic is part of
its latency and power. The normal resident `SwitchLinear` graph is unchanged
unless the converted artifact contains an enabled `expert_streaming` config.

## Conversion and operation

```bash
python scripts/align_convert_qwen4_exp.py HF_CHECKPOINT MLX_ARTIFACT \
  --profile bf16 --expert-streaming-cache-gb 32
```

A value of zero (the default) writes the ordinary fully resident artifact.
With a positive value, the converter writes one fixed-record bf16 expert file
per decoder layer and omits routed-expert tensors from the resident MLX weight
shards. The budget is divided equally among layers. Each layer owns an LRU;
one miss is one `pread`, followed by bf16 materialization, and eviction drops
the only MLX arrays owning those bytes. `model.expert_streaming_counters()`
returns `{layer: {hits, misses, bytes_read}}`. Counters are cumulative and make
storage behavior auditable. The path is a slow near-lossless reference, not a
throughput implementation. A future q8 record codec can use the same fixed
record/LRU contract; the initial implementation intentionally refuses profiles
other than bf16 rather than silently changing numerical quality.

## Released-model memory and I/O math

The released text config has 512 routed experts in each of 48 layers,
`hidden_size=2560`, `moe_intermediate_size=512`, and top-10 routing. One expert
contains gate, up, and down matrices:

`3 * 2560 * 512 = 3,932,160` parameters, or **7.50 MiB bf16**. An affine q8
record would be about **3.87 MiB** with group-64 scale and bias overhead. Thus
24,576 experts occupy **180.0 GiB bf16** (about 193.3 GB) or approximately
**92.8 GiB q8** (99.6 GB), before non-expert weights. A 32 GiB cache holds about
4,369 bf16 experts, averaging 91 per layer.

Ignoring compute and filesystem overhead, top-10 routing reads
`48 * 10 * record_bytes * miss_rate` per token. The resulting SSD ceilings are:

| format | hit rate | bytes/token | 3 GB/s | 6 GB/s |
|---|---:|---:|---:|---:|
| bf16 | 90% | 377 MB | 8.0 tok/s | 15.9 tok/s |
| bf16 | 95% | 189 MB | 15.9 tok/s | 31.8 tok/s |
| bf16 | 99% | 37.7 MB | 79.5 tok/s | 159 tok/s |
| q8 (projected) | 90% | 195 MB | 15.4 tok/s | 30.8 tok/s |
| q8 (projected) | 95% | 97.4 MB | 30.8 tok/s | 61.6 tok/s |
| q8 (projected) | 99% | 19.5 MB | 154 tok/s | 308 tok/s |

These are optimistic bandwidth bounds. Random-read latency, evaluation of MLX
arrays, cache churn, and model compute reduce observed throughput. Report the
per-layer counters with any quality comparison so the assumed hit rate is not
mistaken for a measurement.
