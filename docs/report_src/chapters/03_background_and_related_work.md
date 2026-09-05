# Background and related work

<!-- Source distillation: docs/phase_4/related_work_draft.md. The seven
RPT-002 intake sources were VERIFIED_AGAINST_PRIMARY on 2026-07-11. -->

## Why energy, why phases, and why local systems

JouleWise inherits two established ideas rather than presenting either as
new. JouleSort made an explicit system boundary and true-energy accounting
central to fair cross-system comparison [@joulesort2007]. Splitwise showed
that prompt processing (prefill) and token generation (decode) have different
resource behavior and can be assigned to separate serving pools
[@splitwise-isca2024]. JouleWise takes the measurement-boundary discipline
from the former and the phase decomposition from the latter.

The resulting project is deliberately narrower than a general datacenter
serving system. It measures named local deployment stacks and records what
each telemetry backend includes through a rail manifest. A cross-vendor
result is therefore a comparison between complete deployable stacks unless
model artifact, numerical format, runtime behavior, and workload have been
controlled tightly enough to support a hardware-effect interpretation.

## Disaggregated serving

DistServe separates prefill and decode so each phase can be provisioned
against its own latency objective [@distserve]. Mooncake organizes production
serving around disaggregated KV-cache storage and transfer [@mooncake]. These
systems establish that phase separation and KV movement are mature serving
concerns. They do not make JouleWise the originator of disaggregation; they
motivate its intended consumer/edge measurement application.

For JouleWise, a split configuration is not judged against a weak baseline
chosen after observing results. The intended study freezes monolithic and
split alternatives, records endpoint energy separately, names any excluded
network or switch boundary, and treats runtime, kernels, model format, and
quantization as part of the tested stack. A future split result must also
distinguish prefill, serialization, transfer, deserialization, and decode
rather than assigning the entire request to a single opaque total.

## Energy measurement and inference benchmarks

MLPerf Power and Zeus provide two important methodological reference points.
MLPerf Power uses explicit system-level power rules and publishes measurement
workflow artifacts for covered benchmark classes [@mlperf_power]. Zeus shows
how software telemetry can support energy measurement and optimization across
several hardware backends [@zeus]. JouleWise does not claim to originate
explicit boundaries or raw power data. Its narrower artifact goal is a
self-contained per-run bundle linking raw telemetry, a recorded trace,
timestamped events, output, stack metadata, and derived metrics so the
recorded evidence can be re-reduced without rerunning hardware.

Recent inference benchmarks jointly cover several adjacent dimensions.
TokenPowerBench attributes power samples to inference phases
[@tokenpowerbench]. The ML.ENERGY Benchmark automates inference-energy
measurement and optimization [@mlenergy_benchmark]. Intelligence per Watt
combines task capability with local-inference energy observations
[@intelligence_per_watt]. Bench360 treats energy as one dimension of a wider
local-inference benchmark [@bench360]. *Where Do the Joules Go?* frames
inference energy as a diagnosis problem rather than a single leaderboard
number [@chung2026joules]. Together, these works mean that JouleWise should
not claim novelty for measuring LLM energy, phase-aware telemetry, local
benchmarking, or trace-capable tooling in isolation.

## 2026 positioning intake and novelty boundary

The lead verified seven additional positioning anchors against primary
records on 2026-07-11. *Revisiting Disaggregated Large Language Model Serving
for Performance and Energy Implications* finds that load, its two-full-vLLM
colocated baseline, and PCIe-P2P/CPU-memory/NVMe transfer choices affect
**performance**, while disaggregation's energy penalty remains essentially
unconditional under the paper's pynvml, RAPL, and IPMI J/token accounting.
The result is limited to one two-A100 PCIe Gen3 node
[@revisiting-disaggregation-energy-2026]. *DualScale* combines phase-aware
placement with per-phase DVFS, but its evidence is homogeneous—sixteen H100s
across two InfiniBand-connected nodes—and GPU-only, using 10 ms NVML power
rather than node- or cluster-level energy [@dualscale-2026].

Prima.cpp v3's Appendix A.13 establishes local heterogeneous multi-device
energy evaluation as fact: it reports whole-run Wh per 1K output tokens from
device-side software counters, including communication within that accounting,
but no wall-power or per-stage prefill/decode energy split [@prima-cpp-2025].
JouleWise's niche is **per-stage both-end split, boundary-labeled discipline,
re-reducible bundles**.

*SplitZip* reports bitwise-lossless KV compression and online
encode/transfer/decode performance costs; it reports no energy measurement,
so it cannot support a codec-energy claim. Its code is released under CC BY
4.0 [@splitzip-2026]. *Systematic Characterization of LLM Quantization*
confirms task-, workload-, method-, and GPU-dependent performance, energy, and
quality interactions, but its J/token boundary is GPU-only on A100/H100
datacenter systems, excludes CPU/host energy, and has no released artifact
[@systematic-quantization-2025].

*Sustainable LLM Inference for Edge AI* evaluates 28 Ollama models and
weight-only quantization on a **single Raspberry Pi 4, CPU-only**, with a
Joulescope JS110 measuring the whole-device DC input. It reports mean plus or
minus standard deviation, with run count unstated and no confidence intervals,
so this report makes no rigorous-uncertainty claim for it. Datasets and scripts
are stated available, but the referenced repository was unresolvable and the
release was not verified [@sustainable-edge-ai-2025].

*Silicon Showdown* is an **ecosystem-as-deployed** Apple/NVIDIA comparison,
not a controlled hardware comparison: TensorRT-LLM/NVFP4 or llama.cpp/GGUF is
unmatched to MLX native 4-bit, and PyNVML GPU-board power is unmatched to
powermetrics whole-SoC power. Its **up-to-23x Apple efficiency headline
therefore crosses unmatched stacks and measurement boundaries**. It reports no
accuracy/quality evaluation and releases no artifact
[@silicon-showdown-2026].

JouleWise therefore **does not claim to originate energy-aware disaggregated
inference generally**, nor local heterogeneous multi-device energy evaluation.
Its bounded positioning niche is **per-stage both-end split, boundary-labeled
discipline, re-reducible bundles**. This is not a priority claim or a claim
that the present report has completed split execution.

## Remaining limits on related-work claims

The source survey does not erase the report's evidence limits. The retained
historical corpus is **VOIDED permanently for claim use** under the
[root README void disposition](../../../README.md#current-state) and supplies
no current report results or observations; the report has not completed a
split-inference campaign. Per-rail boundaries are not automatically
wall-equivalent, one physical unit cannot support hardware-class
generalization, and cross-runtime comparisons remain deployable-stack
comparisons. The seven RPT-002 source records are primary-verified, but their
heterogeneous boundaries and differing evidence shapes still forbid a
hardware-only ranking or an unqualified novelty claim.
