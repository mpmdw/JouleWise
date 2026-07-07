# Related Work Draft (Stage 4.6)

- Status: **draft**
- Date: 2026-07-06
- Provenance: generated as part of queue item **P3-001** (Stage 4.6 desk
  work; ungated per the Phase 4 plan).
- Acceptance target (Stage 4.6): the report's background chapter must be
  assemblable from this draft plus `docs/contracts/measurement_methodology.md`
  **without new research**; the "why energy, why split, why now" story is
  sourced here, not asserted.
- Every source below passed an independent verification pass; corrections
  from that pass are already applied in the text. Citations are listed with
  resolvable IDs in the Citations section.

## 1. Scope and positioning claims

This survey covers the four areas named in the Stage 4.6 scope list:
(a) JouleWise's naming lineage and framing (JouleSort for energy-efficiency
benchmarking, Splitwise for prefill/decode disaggregation — the direct
motivator); (b) disaggregated LLM inference systems (DistServe, Mooncake);
(c) energy measurement methodology for ML systems (MLPerf Power, Zeus),
tied back to JouleWise's own methodology decisions D-018 (measurement
boundaries and rail manifests), D-013 (controller co-residency and idle
subtraction), and D-014 (statistical protocol); and (d) the closest recent
local-LLM energy benchmarks from the 2026-07-05 landscape search
(TokenPowerBench, the ML.ENERGY Benchmark, Intelligence per Watt, Bench360,
"Where Do the Joules Go?").

JouleWise's three distinguishing claims against this set, assessed
honestly in Section 6 against the surveyed evidence, are:

1. **Boundary-honest cross-device methodology** (D-018): every energy
   number names its physical measurement boundary via a per-backend rail
   manifest, and cross-target comparisons state boundary differences
   explicitly.
2. **Auditable raw run bundles**: each run preserves its raw power trace,
   event log, model output, and metadata as a self-contained,
   re-reducible artifact — not leaderboard summary numbers.
3. **Split-inference energy on local interconnects**: measured energy of
   prefill/decode-disaggregated inference across heterogeneous local
   devices, decomposed into prefill / serialize / transfer / deserialize /
   decode phases.

## 2. Naming lineage and framing

### JouleSort (SIGMOD 2007)

JouleSort establishes the first widely adopted holistic, system-level
energy-efficiency benchmark: an external sort of randomly permuted
100-byte records at three scale classes (10GB, 100GB, 1TB), scored in
SortedRecs/Joule, intended to compare systems "from clusters to
handhelds." Its lasting methodological contribution is a set of explicit
energy-measurement rules: (1) system boundary — all power measured at the
wall, including power-supply conversion losses for AC and DC systems;
every hardware component used during the sort (idle or otherwise, or
unused but not physically separable) must be inside the measurement;
battery-powered devices must show net change in stored energy no greater
than zero Joules at 95% confidence or include the difference;
(2) environment — 20-25 C inlet temperature, with attached cooling devices
counted; (3) energy use — true (real, not apparent) power sampled via a
digital meter between system and wall (they used a Brand Electronics
20-1850CI at 1 Hz, +/-1.5%), power factor reported, minimum of three
consecutive runs reported and averaged with 95%-confidence winner
determination, borrowing draft SPECpower minimum-meter requirements.
Empirically, the authors measured wall power on heterogeneous machines (a
Xeon DL360G3 server, a Transmeta Efficeon blade, a Core 2 Duo laptop, plus
balanced custom builds) and demonstrated their winning 100GB system — a
deliberately balanced machine pairing a commodity mobile Core 2 Duo CPU
with 13 laptop drives on server-class PCI-e I/O running NSort — achieving
~11,300 records/Joule at 100GB, over 3.5x the estimated prior-year best,
showing that energy-optimal hardware differs sharply from datacenter
norms. (The name "CoolSort" for this machine appears in the subsequent
sortbenchmark.org winner listing and follow-up publications, not in the
SIGMOD 2007 paper itself, which calls it only "our winning 100GB JouleSort
system.") JouleSort became the Joule categories of the industry Sort
Benchmark (sortbenchmark.org), whose rules require +/-1% meters,
computer-synchronized 1 Hz sampling, and five-run averages with standard
deviation.

*Relation:* JouleWise is JouleSort's direct naming and methodological
descendant: it adopts JouleSort's core stance that fair cross-system
energy comparison requires an explicitly defined measurement boundary and
true-energy accounting, and extends it from whole-system wall-plug sorting
to per-device rail manifests on modern heterogeneous local hardware (Apple
Silicon, consumer NVIDIA, Jetson Orin); what JouleSort left open — and
JouleWise measures — is LLM inference as the workload, split
prefill/decode inference energy across local interconnects, and
preservation of raw power traces and event logs (JouleSort/Sort Benchmark
reporting is run-averaged summary numbers with standard deviations, not
auditable raw artifacts).

### Splitwise (ISCA 2024)

Splitwise establishes that the two phases of generative LLM inference —
compute-intensive prompt (prefill) processing and memory-bound token
generation (decode) — have sharply different latency, throughput, memory,
and power characteristics, and that serving efficiency improves by
splitting the phases onto separate machine pools with phase-appropriate
hardware. Using production traces from two Azure LLM inference services
(released publicly via the Azure Public Dataset on GitHub and a Zenodo
artifact), the authors characterize both phases on DGX-A100 and DGX-H100
machines, reporting GPU power draw normalized to TDP and per-request
energy in watt-hours; a key power finding is that token generation
tolerates >50% GPU power capping (700W to 350W) with almost no latency
impact, while prefill is power-sensitive. They design a layer-wise
asynchronous KV-cache transfer over datacenter InfiniBand (200 Gbps A100 /
400 Gbps H100, with NVLink intra-machine and MSCCL++), keeping transfer
overhead under 7% of prompt time (5-8 ms non-overlapped). Cluster-level
provisioning under iso-cost and iso-power constraints yields up to 1.4x
higher throughput at 20% lower cost, or 2.35x throughput at the same cost
and power budget.

*Relation:* JouleWise takes Splitwise's prefill/decode disaggregation as
its direct research motivator but transplants it from homogeneous
datacenter clusters with InfiniBand to heterogeneous local hardware (Apple
Silicon, consumer NVIDIA GPUs, Jetson Orin) over local interconnects, and
measures what Splitwise left open: the actual end-to-end energy of split
inference, with boundary-honest per-device measurement rather than
TDP-normalized GPU power draw — and where Splitwise publishes workload
traces, JouleWise additionally preserves raw power traces and event logs
as auditable run bundles.

## 3. Disaggregated LLM inference

### DistServe (OSDI 2024)

DistServe establishes prefill/decode disaggregation as a first-class LLM
serving architecture: it assigns the prefill and decoding phases to
different GPUs, eliminating prefill-decode interference and allowing each
phase's parallelism and resource allocation to be tuned independently
against its own latency SLO (TTFT for prefill, TPOT for decode). It
introduces "goodput" (maximum request rate served per GPU while meeting
both TTFT and TPOT SLOs) as the optimization target and a bandwidth-aware
placement algorithm that co-locates prefill/decode instances to exploit
intra-node NVLink for KV-cache handoff. Evaluated on a datacenter cluster
of 4 nodes with 32 NVIDIA A100-80GB SXM GPUs (NVLink intra-node, 25 Gbps
cross-node) serving OPT-13B/66B/175B, it shows up to 7.4x higher goodput
or 12.6x tighter SLOs than colocated baselines (e.g., vLLM), and measures
that KV-cache transmission accounts for under 0.1% of total latency, with
>95% of requests delayed <30 ms even at 25 Gbps. All metrics are
latency/throughput-based; the paper reports no energy or power
measurements. Code is released at github.com/LLMServe/DistServe.

*Relation:* JouleWise adopts DistServe's prefill/decode disaggregation as
its research application but transplants it from homogeneous datacenter
A100 clusters to heterogeneous local hardware over consumer-grade local
interconnects, and asks the question DistServe leaves entirely open: what
disaggregation costs in energy, measured with boundary-honest per-device
instrumentation and auditable raw traces rather than latency/throughput
summaries. (DistServe's finding that KV-cache transfer is <0.1% of latency
at 25 Gbps is a useful latency-side baseline for JouleWise's
local-interconnect energy question, Q2.)

### Mooncake (FAST 2025, Best Paper)

Mooncake is the production serving platform behind Moonshot AI's Kimi LLM
service and establishes the KVCache-centric prefill/decode disaggregated
architecture at datacenter scale: prefill and decode run on separate GPU
clusters, and a disaggregated, multi-tier KVCache pool is built from
otherwise-underutilized CPU, DRAM, and SSD resources across the GPU fleet,
moved by a high-bandwidth Transfer Engine over datacenter interconnects
(RDMA/RoCE at 4x200 Gbps and 8x400 Gbps, reaching 87-190 GB/s). A
KVCache-centric global scheduler maximizes effective throughput under
latency SLOs (TTFT/TBT) with prediction-based early rejection under
overload. Evaluation is on NVIDIA datacenter GPU clusters using throughput
and SLO-attainment metrics: up to 525% throughput gain in simulated
long-context scenarios and ~75% more requests served under real production
workloads, running across thousands of nodes serving 100B+ tokens/day. The
paper measures no energy or power whatsoever. The project open-sources the
Transfer Engine, Mooncake Store, and anonymized production request traces
(arrival times, input/output token counts) with a KVCache hit-rate
simulator.

*Relation:* Mooncake supplies the architectural template JouleWise's
research application adopts — prefill/decode disaggregation with KVCache
transfer between stages — but at datacenter scale over RDMA, optimized
purely for throughput/SLO with no energy accounting; JouleWise ports this
split-inference pattern to heterogeneous consumer/edge devices on local
interconnects and measures precisely what Mooncake leaves open: the energy
cost of disaggregation, with boundary-honest per-device measurement.

## 4. Energy measurement of ML systems

This section ties directly to JouleWise's methodology decisions: D-018
(per-backend `power_w` definition, rail manifests, and the measurement
boundary table), D-013 (controller co-residency and idle-baseline
treatment), and D-014 (repetitions, intervals, outlier policy, thermal
gating).

### MLPerf Power (arXiv 2024; companion artifact labeled HPCA 2025)

MLPerf Power defines the industry-consortium (20+ organizations)
methodology for measuring the energy efficiency of ML systems across five
orders of magnitude, from microwatt TinyML boards to megawatt datacenter
training clusters, and reports 1,841 reproducible measurements from 60
systems using MLPerf benchmark workloads. Its core methodological
commitment is full-system power measurement at an explicit boundary: for
inference (datacenter/edge divisions) power is measured as total AC power
"at the wall" using SPEC PTDaemon-driven power analyzers (the submission
rules mandate total-SUT, wall-side measurement — "the power consumption
must be measured at the system level," with "any other means of power
measurement submission" disallowed — which excludes per-rail and DC-side
measurement by construction rather than by naming it; in the v1.0-v2.0
rounds only Yokogawa analyzers were supported, with the broader
PTDaemon/SPEC device list noted as future support), TDP/vendor-rating
proxies rejected, and no battery or alternate power storage permitted
upstream of the PSUs; for Tiny, the entire device including always-on
components is instrumented with micro-power equipment and hardware-pin
start/stop signaling via an isolating I/O manager; for training,
node-level telemetry (IPMI/Redfish) covers compute nodes and interconnect
fabric (cooling excluded as future work; where direct switch measurement
is not possible, estimated interconnect power values are allowed).
Reported metrics are samples/joule, energy per inference, and
energy-to-train. Submission rules require all workflow logs — LoadGen
performance logs plus the Director's PTDaemon power measurement logs for
both ranging and testing phases, along with analyzer configuration
(analyzer_table) and power-management settings files — and accepted
submissions are published in public MLCommons GitHub results repositories.
Mobile/battery-powered device power (a category relevant to laptops and
phones) is explicitly not supported, and the rules state that the power
measurement flow "does not apply to disaggregated systems in this version
of the submission." The paper analyzes performance-vs-energy trade-offs
(e.g., quantization, accelerator scaling) across the covered scales.
(Venue note: arXiv shows no journal reference; the first author's
companion repo is titled MLPerf-Power-HPCA-2025, consistent with HPCA 2025
acceptance — verify the final venue before camera-ready citation.)

*Relation:* JouleWise adopts MLPerf Power's core commitments — explicit
measurement boundaries, calibrated instrumentation, and published run
artifacts — but targets exactly the gap MLPerf Power leaves open:
heterogeneous local/consumer devices (Apple Silicon Macs fall under the
unsupported battery/mobile-adjacent category; MLPerf's single AC-wall
boundary forbids the per-rail measurements needed to compare SoCs with
integrated memory against discrete-GPU PCs), which JouleWise addresses
with per-device rail manifests (D-018) instead of a uniform wall boundary;
MLPerf Power also has no notion of split prefill/decode inference or
interconnect energy — indeed its rules explicitly exclude disaggregated
systems from the power flow — which is JouleWise's research application.

### Zeus (NSDI 2023; ml.energy project)

Zeus (NSDI 2023) establishes that common DNN training practices waste GPU
energy and introduces an online exploration-exploitation framework with
just-in-time energy profiling that co-tunes job-level (batch size) and
GPU-level (power limit) knobs for recurring training jobs, achieving
15.3-75.8 percent energy savings on NVIDIA GPUs. The accompanying
open-source Zeus library (ml.energy) has since become the de facto
software instrumentation layer for ML energy measurement: it reads NVML
energy counters on Volta+ NVIDIA GPUs (polling instantaneous power on
older ones), AMDSMI on AMD GPUs, RAPL for Intel/AMD CPU package and DRAM
energy, Apple Silicon's private IOReport "Energy Model" channels (1 mJ
cumulative counters per SoC subsystem), and Jetson on-chip
CPU/GPU/total-chip sensors. It scopes measurements with
begin_window()/end_window() markers with automatic CPU/GPU synchronization
for PyTorch/JAX, exposes timestamped power timelines via
PowerMonitor.get_power_timeline(), and supports multi-node power streaming
(PowerStreamingClient aggregating SSE streams from per-machine zeusd
daemons). Its focus is training-time optimization and per-process
software-counter measurement, not a cross-device inference benchmark.

*Relation:* JouleWise adopts the Zeus-style software-counter
instrumentation approach (NVML on NVIDIA, IOReport-class counters on Apple
Silicon, Jetson rails) as one layer of its stack, but measures what Zeus
leaves open: energy of prefill/decode-disaggregated inference over local
interconnects, with an explicit per-device rail manifest (D-018) that
makes measurement boundaries comparable across heterogeneous devices, and
auditable raw run bundles rather than programmatic in-process readings —
Zeus documents what each backend's counter covers per device, yet does not
normalize or declare comparability of those boundaries across device
types, and its published results are summary numbers, not raw trace
artifacts.

## 5. Recent local-LLM energy benchmarks (the 2026-07-05 landscape set)

These are the closest recent works; per the Phase 4 plan, the related-work
section must position against each.

### TokenPowerBench (AAAI 2026)

TokenPowerBench is presented as the first lightweight, extensible
benchmark framework dedicated to LLM-inference power consumption. It
combines (a) a declarative configuration interface over models, prompts,
and inference engines, (b) a measurement layer that captures GPU power via
NVML/DCGM, CPU/DRAM power via Intel RAPL, and node/system power via IPMI
or rack PDUs, all without dedicated external power meters, and (c) a
phase-aligned metrics pipeline that timestamps every power sample and
attributes energy to the prefill and decode stages of each request.
Experiments run on a datacenter-class 8-node cluster of 4x NVIDIA H100
(94 GB) per node with dual Xeon Gold 6426Y CPUs, using Ray for multi-node
tensor/pipeline-parallel serving of 15+ open models (Llama, Falcon, Qwen,
Mistral, 1B-405B). Key empirical findings: long prompts raise the prefill
energy share while large batches raise the decode share; for the Llama-3
70B model, energy per token drops ~25% from batch 32 to 256 with
diminishing returns; FP8 cuts energy ~30% vs FP16 for Llama-3 405B; and
scaling Llama-3 from 1B to 70B raises energy per token ~7.3x. The
framework is released open source with CSV/JSON result export plus
optional cost and carbon estimation (no repository URL appears in the
paper text).

*Relation:* JouleWise adopts TokenPowerBench's core idea of phase-aligned
prefill/decode energy attribution but targets what it leaves open:
heterogeneous *local* hardware (Apple Silicon, consumer NVIDIA, Jetson
Orin) rather than homogeneous H100 datacenter nodes, explicit
boundary-honest per-device rail manifests rather than whatever
NVML/RAPL/IPMI report, and energy of prefill/decode-disaggregated split
inference over local interconnects, which TokenPowerBench does not measure
(its multi-node runs are parallelized serving of one model, not
phase-disaggregated serving across devices). Honesty note: because
TokenPowerBench's export format is trace-capable (phase-tagged power
samples as CSV/JSON), JouleWise should not claim novelty on trace-capable
*tooling* — the distinct claim is published, auditable raw run bundles for
its reported results.

### The ML.ENERGY Benchmark (NeurIPS D&B 2025, Spotlight)

The ML.ENERGY Benchmark establishes an automated, reproducible methodology
for measuring per-request inference energy of generative AI services at
datacenter scale. It benchmarks roughly 40 model architectures (Llama,
Phi, Mistral/Mixtral, Stable Diffusion variants, etc.) across 6 task
families (LLM chat/code, visual chat, text-to-image, text-to-video,
image-to-video) served with vLLM and Diffusers on flagship NVIDIA
A100-40GB and H100-80GB GPUs (AWS p4d/p5 instances). Energy is measured
GPU-only in software via the authors' Zeus library (NVML counters), with a
defined accounting convention: for LLMs, per-token energy during the
"steady state" (saturated batch) multiplied by average output tokens per
request; for diffusion models, batch energy divided equally among
requests. It publishes results on the public ML.ENERGY Leaderboard and
releases the benchmark harness open-source, and adds automated
optimization recommendations (Pareto-frontier analysis over time-energy
tradeoffs) showing up to ~40-44% energy savings under latency constraints.

*Relation:* JouleWise adopts the same core motivation (standardized,
automated LLM inference energy benchmarking) and, like ML.ENERGY, builds
on software power-counter measurement, but targets exactly what ML.ENERGY
leaves open: heterogeneous local hardware rather than homogeneous
datacenter NVIDIA GPUs, explicit per-device rail manifests instead of a
single GPU-only NVML boundary (the paper is boundary-transparent, but only
for one vendor, and acknowledges excluding CPU/DRAM and non-NVIDIA
hardware), raw power-trace/event-log run bundles instead of leaderboard
summary numbers, and split prefill/decode inference energy over local
interconnects, which ML.ENERGY does not cover.

### Intelligence per Watt (arXiv preprint, Nov 2025)

This paper proposes "intelligence per watt" (IPW) — task accuracy per unit
power — as a metric for whether local AI can serviceably offload cloud
inference demand. It profiles 20+ local LMs (<=20B active parameters) on 8
accelerators spanning local and cloud hardware (Apple Mac Studio M4 Max;
NVIDIA Quadro RTX 6000, RTX 6000 Ada, A100 40GB SXM4, H200 SXM, GH200,
B200; AMD MI300X — with SambaNova SN40L evaluated additionally in the
results tables beyond the abstract's 8-accelerator count) against 1M
real-world single-turn chat and reasoning queries, recording per-query
accuracy (win rate vs. frontier models), energy, latency, and power. Power
measurement is device-specific software telemetry sampled at ~50 ms: NVML
on NVIDIA, powermetrics on Apple Silicon, ROCm SMI on AMD, with energy
computed by numerical integration over each query (prefill + decode, batch
size 1 to isolate intrinsic model-accelerator efficiency). Headline
findings: local models answer 88.7% of single-turn queries accurately, IPW
improved 5.3x from 2023-2025, and local accelerators show at least 1.4x
lower IPW than cloud accelerators. The authors release an open-source IPW
profiling harness (github.com/HazyResearch/intelligence-per-watt) with a
Rust gRPC energy-monitoring service, but publish neither raw power traces
nor cross-vendor measurement-boundary definitions. (Note: its "local"
NVIDIA devices are workstation cards — Quadro RTX 6000, RTX 6000 Ada — not
GeForce consumer GPUs, and no Jetson-class devices are included.)

*Relation:* JouleWise adopts the same energy-per-useful-work framing and
overlapping local hardware (Apple Silicon) but targets exactly what IPW
leaves open: IPW mixes powermetrics, NVML, and ROCm SMI readings without
stating whether they capture comparable boundaries (GPU rail vs. package
vs. wall), reports summary numbers rather than auditable raw run bundles,
and explicitly excludes disaggregated serving — whereas JouleWise
contributes per-device rail manifests (D-018), preserved raw traces/event
logs, and prefill/decode split-inference energy over local interconnects.

### Bench360 (arXiv preprint, Nov 2025, rev. Jan 2026)

Bench360 is a benchmarking framework for local (self-hosted) LLM inference
that jointly evaluates task quality and system behavior — latency
(TTFT/TPOT/GL), throughput (TPS/SPS), startup time, energy, and amortized
GPU cost per request — across models, quantization levels, and four
inference engines (vLLM, SGLang, LMDeploy, HuggingFace TGI) under three
usage scenarios (single-stream, batch with sizes 16-128, and server with
Poisson arrivals). Task quality is measured per task as Accuracy (MMLU),
F1 (SQuAD v2), ROUGE-L (CNN/DailyMail), and Execution Accuracy (Spider);
AST-match and the ATL/GL metric names appear in the tool documentation
rather than the paper body. Experiments run on three NVIDIA datacenter
GPUs (L4, A10, A30) under a 24 GB VRAM constraint meant to reflect
realistic local deployments. Energy is measured GPU-only via NVIDIA NVML
polling; the authors explicitly scope the boundary to the GPU "since it
dominates LLM inference" and cite NVML error bounds below 5%. Evaluation
is restricted to single-GPU deployments; multi-GPU inference and CPU
offloading are stated as unexplored limitations. Code is released at
github.com/slinusc/bench360, and each run emits per-query logs (details/),
GPU/CPU/power readings (readings/), and per-experiment summary CSVs
(run_report/) — but the authors do not publish the raw traces or logs from
the paper's own experiments (the repo's experiments/ directory contains
only four YAML config files, with no results data or dataset link), so
auditability is a capability of the tool for future runs, not a published
raw-data bundle for the reported results.

*Relation:* JouleWise shares Bench360's local-inference framing and its
inclusion of energy as a first-class metric, but extends it in exactly the
dimensions Bench360 leaves open: truly heterogeneous local hardware (Apple
Silicon, consumer NVIDIA, Jetson Orin rather than three NVIDIA datacenter
GPUs), boundary-honest cross-device measurement via per-device rail
manifests instead of a GPU-only NVML boundary, published auditable raw run
bundles for its reported results, and energy of split prefill/decode
inference over local interconnects, which Bench360 explicitly does not
evaluate (single-GPU only).

### "Where Do the Joules Go?" (arXiv preprint, Jan 2026)

A large-scale measurement study of generative-AI inference time and energy
spanning 46 models, 7 tasks, and 1,858 configurations, run exclusively on
NVIDIA H100 and B200 datacenter GPUs. Serving is done with
production-representative stacks (vLLM 0.11.1 for LLMs/MLLMs, xDiT 0.4.5
for diffusion models) with batch-size sweeps at BF16, and energy is
measured GPU-only via the Zeus library (NVML-based), computing
energy-per-token from steady-state totals — CPU, DRAM, and whole-node
power are explicitly out of scope, justified by GPUs accounting for 50-70%
of datacenter power. Headline findings are order-of-magnitude variations:
25x energy differences across LLM task types, >100x between video and
image generation, and 3-5x from GPU utilization differences. Beyond the
numbers, the paper contributes a diagnosis framework: a causal model
(their Figure 10) mapping configuration knobs through latent factors
(memory pressure, utilization, compute volume) to time/energy outcomes,
plus analyses of static-power wastage and time-energy tradeoff frontiers.
Its careful attribution methodology (steady-state windows, static-power
accounting, causal knob-to-metric framework) is the strongest
methodological overlap with JouleWise and worth citing as the
datacenter-side analogue of energy diagnosis. (Caveat: a fresh preprint,
submitted 2026-01-29; an artifact release could appear later.)

*Relation:* JouleWise adopts this paper's diagnostic framing (attributing
where joules go rather than reporting single leaderboard numbers) but
targets exactly what it scopes out: heterogeneous local/edge hardware
instead of homogeneous H100/B200, whole-device boundary-honest rail
manifests instead of GPU-only NVML readings, and energy of
prefill/decode-disaggregated inference over local interconnects, which
this work does not study — and JouleWise's auditable raw run bundles
contrast with this paper's summary-level reporting.

## 6. Positioning assessment (honest audit of the three claims)

For each distinguishing claim, this section states plainly whether any
surveyed source undercuts it, using the per-source claim flags from the
verified survey data, and gives the adjusted, defensible version.

### Claim 1: Boundary-honest cross-device methodology (D-018)

**Partially undercut — two sources carry this flag as TRUE.** JouleSort's
central methodological contribution is precisely an explicit
measurement-boundary specification designed to be comparable across
heterogeneous systems (wall-measured whole system including PSU losses,
mandatory inclusion of all participating or inseparable components, a
battery net-energy-change rule at 95% confidence for DC/mobile devices,
inlet-temperature and cooling rules). MLPerf Power likewise defines an
explicit, rule-enforced boundary (total system AC power at the wall; for
Tiny, the whole device including always-on components) comparable across
heterogeneous submitted systems.

**Adjusted, defensible claim:** JouleWise does not originate the concept
of an explicit, cross-system measurement boundary — JouleSort and MLPerf
Power both do, and the background chapter must credit them. JouleWise's
honest differentiation is *granularity, device coverage, and workload*:
both prior boundaries are a single whole-system AC wall plug per
system-under-test, whereas JouleWise provides per-device *rail manifests*
(D-018) with a named boundary table, on device classes where a uniform
wall boundary is unavailable or non-comparable — Apple Silicon SoC
subsystems, GPU board power, Jetson module input — calibrated against a
wall meter where one exists. MLPerf Power's rules mandate total-SUT
wall-side measurement (which excludes per-rail/DC-side approaches by
construction) and exclude battery-powered/mobile-adjacent devices
entirely, so the per-rail, heterogeneous-local-device boundary methodology
remains open and is what JouleWise claims. No surveyed source among the
recent local-LLM benchmarks (TokenPowerBench, ML.ENERGY, Intelligence per
Watt, Bench360, "Where Do the Joules Go?") defines or reconciles
cross-device boundaries; Intelligence per Watt in particular mixes
powermetrics/NVML/ROCm SMI without stating comparability, which is the
gap D-018 closes.

### Claim 2: Auditable raw run bundles

**Partially undercut — one source genuinely publishes raw power logs, and
two publish raw workload traces.** MLPerf Power's submission rules require
all power-workflow logs (Director's PTDaemon power logs for both ranging
and testing phases, LoadGen logs, analyzer_table, power_settings), and
accepted submissions are published in public MLCommons GitHub results
repositories — so raw per-run power logs of the reported results are
publicly auditable there (caveats: the headline leaderboard surfaces only
summary samples/joule numbers, and PTDaemon itself is under a members-only
SPEC EULA). Splitwise and Mooncake both released production *workload*
traces (request arrivals, token counts) — genuine raw artifacts, but
request-level replay data, not power measurements. Bench360's harness can
emit per-run power readings, but the authors did not publish the raw
traces from their own experiments (flag corrected to false in
verification).

**Adjusted, defensible claim:** JouleWise cannot claim to be the first or
only project publishing raw power data — MLPerf Power's public results
repositories already do that for its covered system classes. The
defensible version: JouleWise publishes *self-contained, re-reducible
per-run bundles* — raw power trace, timestamped event log with phase
labels, model output, device metadata including the rail manifest, and
derived summary — such that any summary number can be re-derived from raw
evidence with one command (`reduce`, D-028) and validated against a fresh
re-reduction (`validate-bundle --strict`, D-030), on heterogeneous local
device classes that MLPerf Power excludes, for a workload (split LLM
inference) no surveyed source publishes raw measurement artifacts for. The
chapter should explicitly acknowledge MLPerf Power's log publication and
the Splitwise/Mooncake trace releases, and distinguish workload traces
from measurement-run artifacts.

### Claim 3: Split-inference energy on local interconnects

**Not undercut — no surveyed source carries this flag as TRUE.** The
closest approaches: Splitwise measures per-phase GPU power (TDP-normalized)
and per-request watt-hours and runs power-capping experiments, but on
datacenter DGX clusters over InfiniBand, and its iso-power/iso-cost
results are cluster provisioning optimizations, not measured end-to-end
energy of the disaggregated pipeline including interconnect transfer.
TokenPowerBench attributes energy to prefill and decode phases per
request, but on monolithic (model-parallel) serving of one model, not
phase-disaggregated serving across devices. DistServe and Mooncake measure
disaggregated serving but report no energy or power at all. MLPerf Power's
rules explicitly exclude disaggregated systems from the power-measurement
flow. Intelligence per Watt explicitly isolates single-accelerator,
batch-1 runs.

**Defensible claim, as stated with one precision:** no surveyed work
measures the end-to-end energy of prefill/decode-disaggregated LLM
inference — on *any* interconnect, datacenter or local — decomposed into
prefill / serialize / transfer / deserialize / decode stages with
both-end power measurement. JouleWise's claim is safe and should be
phrased at that strength, while crediting Splitwise and TokenPowerBench as
the nearest energy-adjacent predecessors on the phase-energy side and
DistServe/Mooncake on the architecture side.

## 7. Unresolved sources

None. All eleven surveyed sources resolved (citation verified, full text
or authoritative record fetched) in the verification pass. No source had
to be dropped or carried as unresolved.

## 8. Citations

All sources retrieved and verified 2026-07-06 (verification pass built on
the 2026-07-05 landscape search).

| Key | Citation | Resolvable ID |
|---|---|---|
| joulesort2007 | Rivoire, Shah, Ranganathan, Kozyrakis. "JouleSort: A Balanced Energy-Efficiency Benchmark." SIGMOD 2007, pp. 365-376. | https://doi.org/10.1145/1247480.1247522 |
| splitwise-isca2024 | Patel, Choukse, Zhang, Shah, Goiri, Maleki, Bianchini. "Splitwise: Efficient Generative LLM Inference Using Phase Splitting." ISCA 2024. | arXiv:2311.18677; DOI:10.1109/ISCA59077.2024.00019 |
| distserve | Zhong, Liu, Chen, Hu, Zhu, Liu, Jin, Zhang. "DistServe: Disaggregating Prefill and Decoding for Goodput-optimized Large Language Model Serving." OSDI 2024. | arXiv:2401.09670 |
| mooncake | Qin, Li, He, Zhang, Wu, Zheng, Xu. "Mooncake: A KVCache-centric Disaggregated Architecture for LLM Serving." USENIX FAST 2025 (Best Paper); extended in ACM ToS (DOI 10.1145/3773772). | arXiv:2407.00079 |
| mlperf_power | Tschand, Rajan, Idgunji, et al. (26 authors, MLCommons Power WG). "MLPerf Power: Benchmarking the Energy Efficiency of Machine Learning Systems from Microwatts to Megawatts for Sustainable AI." arXiv 2024 (v2 Feb 2025); companion artifact labeled HPCA 2025 — verify final venue before camera-ready. | arXiv:2410.12032 |
| zeus | You, Chung, Chowdhury. "Zeus: Understanding and Optimizing GPU Energy Consumption of DNN Training." NSDI 2023; ml.energy open-source project. | arXiv:2208.06102 |
| tokenpowerbench | Niu, Zhang, Li, Zhao, Wang, Wang, Chen. "TokenPowerBench: Benchmarking the Power Consumption of LLM Inference." AAAI 2026 (Main Track). | arXiv:2512.03024 |
| mlenergy_benchmark | Chung, Ma, Wu, Liu, Kweon, Xia, Wu, Chowdhury. "The ML.ENERGY Benchmark: Toward Automated Inference Energy Measurement and Optimization." NeurIPS D&B 2025 (Spotlight). | arXiv:2505.06371 |
| intelligence_per_watt | Saad-Falcon, Narayan, et al. (Stanford Hazy Research). "Intelligence per Watt: Measuring Intelligence Efficiency of Local AI." arXiv preprint, Nov 2025. | arXiv:2511.07885 |
| bench360 | Stuhlmann, Argerich, Fürst. "Bench360: Benchmarking Local LLM Inference from 360 Degrees." arXiv preprint, Nov 2025 (rev. Jan 2026). | arXiv:2511.16682 |
| chung2026joules | Chung, Wu, Ma, Chowdhury. "Where Do the Joules Go? Diagnosing Inference Energy Consumption." arXiv preprint, Jan 2026 (ML.ENERGY Initiative, U. Michigan). | arXiv:2601.22076 |

## 9. Assembly notes for Stage 5.5

Mapping from this draft to the future background chapter:

- **Chapter opening ("why energy, why split, why now")**: Section 1's
  scope paragraph + the JouleSort and Splitwise establishes-paragraphs
  (Section 2) source the naming story and the phase-asymmetry motivation;
  "why now" is sourced by the Section 5 cluster (five closely related
  benchmarks within ~14 months) plus Splitwise's power-capping finding.
- **Background: disaggregated serving**: Section 3 verbatim; cite
  DistServe's <0.1% KV-transfer-latency figure next to the Q2 framing
  (latency-cheap does not imply energy-cheap on consumer links).
- **Background: energy measurement methodology**: Section 4 + the
  methodology doc's Measurement Boundaries table (D-018), Controller
  Co-Residency (D-013), and Statistical Protocol (D-014) sections. The
  MLPerf Power paragraph is the anchor for the boundary discussion; the
  Zeus paragraph anchors the software-counter instrumentation layer.
- **Related-work positioning table**: build directly from the claim-flag
  matrix implicit in Section 6 (three claims x eleven sources); the adjusted
  claim wordings in Section 6 are the ones to use in the report —
  do NOT use the stronger unadjusted forms for claims 1 and 2.
- **Limitations cross-reference**: the report's limitations section
  (Stage 4.4) inherits the D-018 boundary table; Section 6 Claim 1's
  credit to JouleSort/MLPerf Power belongs there too.
- **Citation hygiene before camera-ready**: confirm MLPerf Power's final
  venue (HPCA 2025 expected); check whether "Where Do the Joules Go?"
  (fresh preprint) and Bench360 have since been published or released
  artifacts; attribute the "CoolSort" name to sortbenchmark.org, not the
  SIGMOD paper.
