# DRAFT: x86 / CUDA ALIGN replication backend

Status: **DRAFT, fixture-tested, PROVISIONAL. No Linux rig, GPU, real meter,
model weights or live SHADE cache was used to validate this path.** This is
an engineering replication pilot, outside the registered Apple and Block-5
programs. It cannot establish a cross-platform energy effect or close a live
hardware gate.

## Architecture and source boundary

ALIGN's episode boundary already exists: `ChatEndpoint.chat(...) -> ChatResult`,
`AgentTask`, and `PowerSampler.start()/stop()` in
`joulewise/align/interfaces.py`. The platform-neutral `runner.run_episode`
owns the tool loop, task reset, turn accounting, partial failures, transcripts,
and sampler lifecycle. `ShadeTask` owns the pinned public environments and
benign/sabotage prompts. All of these are reused, rather than reimplemented.

This clone's main branch did not contain ALIGN. The shared modules and their
fixture tests were brought from locally available Git object
`9c40e4e5d` (`origin/lane/2026-11-05-align-pilot10-benign`). This is a **file
subset**, not a merge of the measurement branch. The original modules' code
is retained except for adding `rapl_energy` as a cumulative source and applying
the existing unknown-counter-age sensitivity treatment to that new source.
The copied NVML tests omit their separate preflight-CLI subcheck, whose CLI is
outside this subset; copied SHADE tests omit live-cache opt-in checks, leaving
only synthetic fixtures. No Apple source file is modified.

The Apple boundary was checked in local Git objects:

- `r0_mlx.MlxBackend` wraps `MlxRuntimeAdapter` and `apple.endpoint.MlxEndpoint`.
  Its NLL, memory and Metal diagnostics are Apple R0 checks, not episode-backend
  requirements. CUDA does not pretend to implement or pass them.
- `apple.workload.EpisodeRuntime` and the Apple pilot/v4 session scripts manage
  the registered Apple lifecycle and bundle format. They remain unchanged and
  are not invoked by this driver.
- `linux.backend.LlamaCppEndpoint` implements the **same ChatEndpoint protocol**
  using the shared OpenAI SSE parser. `LlamaCppBackend` creates a fresh endpoint
  and offline pinned task per member. `linux.session` drives the shared episode
  runner and adds Linux capture, quiet receipts, and exclusive attempt logging.

```text
Linux DRAFT session -> pinned ShadeTask + shared run_episode
                     -> LlamaCppEndpoint -> local llama-server -> CUDA
                     -> existing NvmlSampler (GPU board)
                     -> RaplSampler (CPU package)
                     -> WallMeterSampler (AC whole system, always requested)
                     -> LinuxQuietGuard (/proc cumulative CPU-s/s)
                     -> separate immutable-by-convention attempt directories
```

### Generation, seeds and logging

The endpoint requests streaming usage, preserves tool-call IDs/arguments and
reasoning aliases, and never retries an uncertain request. A missing `[DONE]`,
server stream error, timeout or missing mandatory token accounting is retained
as a failed request with its partial result. Partial tool calls are not executed.
Optional inline `<think>` parsing is explicit; the original inline text survives
in raw usage. Reasoning token counts missing from the server stay unknown and
flagged; they are never estimated from words or subtracted from total decode.

`context_tokens` is the server-reported cached prefix, `prefill_tokens` is prompt
minus cached, and `decode_tokens` includes reasoning. Missing cached counts and
reasoning counts keep the shared runner's flagged-zero convention. No tokenizer
queries or judge model calls occur inside the measured episode. The draft has
no judge endpoint: scores that require one remain missing with task flags.

The existing pilot-4 laws are retained verbatim as pure functions:

```text
episode64 = leading64(SHA256(JSON(["align-p4-v1", model_id, thinking, pair, seed_index])))
turn64    = leading64(SHA256(JSON(["align-p4-turn-v1", episode64, turn_index])))
server32  = turn64 & 0xffffffff
```

Task reset and Episode.seed retain the seed **index**. Benign/sabotage members
share their pair's seeds; the model tag is explicit. Each turn records the
canonical 64-bit seeds, index, and actual 32-bit wire seed. The random-seed
sentinel `0xffffffff` is refused. This projection is a portability choice for
llama.cpp, **not an assertion of identical PRNG state or output across MLX and
CUDA**. Use the same model tag to reproduce logical Apple seeds; the draft
8B model uses a new tag. The test includes an existing Apple golden seed.

`cache_prompt: false` requests fresh prompt work. A fresh Python endpoint does
not itself evict server KV state. Before using energy comparisons, verify the
pinned server's cache behavior, template rendering, reasoning extraction, tools,
seed width, and sampling settings. There is one server slot and no concurrent
client. The pilot does not record exact token IDs or certify MLX's prefix-cache
equivalence; do not mix its energies into Apple registered analyses.

Each attempt writes `config.json`, `episode.json` (including traces, raw readings,
usage and flags), `turns.jsonl`, `transcript.jsonl`, `quiet.json`, and a SHA-256
`manifest.json`. The full transcript includes system prompts, tool results,
and separated reasoning. Per-turn raw usage also retains the actual request
body and structured content/reasoning/tool calls, avoiding reliance on text
delimiters to recover reasoning. Files are exclusive and flushed/synced; an existing
output directory is refused. This is a standalone engineering artifact, not the
registered run-bundle/custody protocol. A crash can leave a partial directory;
preserve it and use a new output path. The manifest detects later edits but is
not an authenticated seal. No monitor is configured and no v4 transcript is
scored by this driver.

## Measurement adapters and boundaries

| Adapter | Native observation | Important limits |
|---|---|---|
| Existing `NvmlSampler` | mW board power and optional mJ cumulative GPU energy via NVML | Lazy ctypes binding to `libnvidia-ml.so.1`; unsupported energy/instant/average channels are empty with reasons. No A100/H100 timing assumptions are borrowed for an RTX 3050. |
| `RaplSampler` | `energy_uj` and `max_energy_range_uj` in powercap sysfs | Selects package domains only, deduplicates sysfs aliases, excludes overlapping core/uncore subdomains. Cumulative joules plus exact raw integer µJ survive. |
| `WallMeterSampler` + `HttpJsonWallMeter` | AC watts from a bounded HTTP GET returning JSON | Configurable dotted power field and optional strictly advancing numeric source timestamp. Host query midpoints are receipt-time proxies; sensor age/averaging/latency need qualification. No redirects or ambient proxies. |
| `WallMeterSampler` + `CsvReplayWallMeter` | Interpolated synthetic `elapsed_s,power_w` CSV | For tests/rehearsal only; exhaustion is a flagged failure and every member is labelled `wall_meter.synthetic_replay`. |

NVML board power, RAPL package energy, and AC wall energy are **separate
boundaries** (D-018); never sum them into a claimed whole-system number or compare
their absolute values as equivalent. Powercap availability depends on the rig's
CPU and Linux permissions. RAPL is a hardware/firmware estimate, not an AC meter.

RAPL counter decreases are preserved as `counter_decreased_wrap_or_reset`.
No automatic unwrapping is done: a reset cannot safely be called a wrap, and
multiple wraps between polls are unobservable. The shared attribution code
flags decreases and carries unknown counter age as infinite timing sensitivity.
Raw adapter data is the evidence; usable energy intervals need rig qualification.
Polling rate is not sensor update rate or accuracy. HTTP/RAPL query brackets,
errors, and native payloads survive in trace notes. Dropped polls are gaps,
never zero-filled. A blocked worker is bounded at stop and cannot be restarted
while it is still active.

**Every member requests the wall stream**, even with `wall_meter: null`.
Missing/unreadable streams are retained as empty traces and
`wall_meter.missing_stream`. Coverage and errors give `wall_meter.partial_coverage`
and `wall_meter.stream_errors`; a member with those flags is not a clean
two-boundary measurement. A bad meter endpoint does not silently remove the
channel or masquerade as zero power. The meter make/model, accuracy, update
rate, absolute freshness and transfer function are still TBD. Without a source
timestamp, a constant stale HTTP value cannot be distinguished from steady power.

## Linux quiet guard

`LinuxQuietGuard` reads `/proc/<pid>/stat` cumulative user+system ticks and
`SC_CLK_TCK`. PID plus start ticks prevents PID-reuse subtraction. It records
raw snapshots, per-process CPU-s/s, aggregate outside-tree CPU, process churn,
and query times. The capture and explicitly configured llama-server PID trees
are excluded from contention, and those roots must remain present with the
same identities. Unreadable snapshots, missing roots and counter regressions
are tooling faults (`indeterminate`), not quiet observations.

The R0-L3-style rule is implemented for this draft pilot:

- More than 0.05 CPU-s/s for a single outside process is recorded and flagged.
- At least 0.5 CPU-s/s in the largest single outside process over consecutive
  touching/overlapping census windows spanning at least 60 s is sustained.
  Aggregate-only load never triggers a redo. The largest process may differ
  across windows, matching the ruled window test.
- The original member gets **one redo** after sustained contention. Both
  attempts survive in separate directories. A sustained second attempt is
  retained as `contended`; ordinary contention never aborts.

Windows are at least 30 s at a 5 s polling cadence, as in the R0 implementation.
A 30 s pre-episode CPU observation dwell covers short episodes. The redo is
decided after the episode; there is no mid-inference HTTP cancellation. This
can cost extra compute versus R0's immediate SMC-capture stop. Process births
and exits between snapshots are unaccounted, disclosed and member-flagged.

This ports **CPU observation and redo policy**, not the Mac's LaunchAgent,
armed-window or custody/agent census. It has no authority to change the Mac
rule or certify Linux claim readiness. Ed must run a clean rig with agents
closed, and settle Linux admission/thermal gates before a registered campaign.

## What Ed must install and qualify on the rig

Nothing below was executed in this sandbox. Use the rig's distribution and
record exact versions; these commands are examples for a locally provisioned
llama.cpp checkout and GGUF, not a download procedure.

1. A Linux NVIDIA driver supporting the actual RTX 3050, with NVML
   (`libnvidia-ml.so.1`) and a working `nvidia-smi`. Record the device UUID,
   driver, GPU firmware, power limit, clocks and persistence settings.
2. A CUDA toolkit/compiler supported by that driver and the pinned llama.cpp
   checkout; a C/C++ toolchain, CMake, and its required build dependencies.
   A Python CUDA framework is not needed for this server path.
3. A pinned local llama.cpp checkout, built with CUDA, and a locally provisioned
   **8B instruct GGUF Q4_K_M** artifact. The example chooses Qwen3-8B. Record its
   provenance/license and exact SHA-256, plus llama.cpp commit, build options,
   chat template and server argv. No model downloading is implemented.
4. Python 3.11 or 3.13. The client/samplers are stdlib-only; install the pinned
   SHADE source's Python dependencies separately, outside measurement time.
   Provision the verified offline SHADE cache at
   `<shade_cache>/6614e77191c1f8e2d0c44c123c6f915905ebafae`. The existing port
   verifies both its commit and the complete blob manifest; fetching is disabled.
5. Read permission on the CPU's package `energy_uj`, `name`, and
   `max_energy_range_uj` powercap files. Grant narrowly outside measurement;
   do not run the whole harness as root. Verify `/proc` CPU observability.
6. A real AC wall meter covering the **whole desktop**, with a trusted HTTP
   bridge or another `WallMeterAdapter.read()` implementation. The generic
   bridge response is `{"power_w": 120.5, "timestamp_s": 1794000000.0}`.
   Decide whether display/network equipment is inside the measured boundary,
   record it, and calibrate the meter independently of NVML/RAPL.

Example build and serving commands, **on the rig only**:

```sh
cmake -S ./llama.cpp -B ./llama.cpp/build -DGGML_CUDA=ON -DCMAKE_BUILD_TYPE=Release
cmake --build ./llama.cpp/build --target llama-server -j2
./llama.cpp/build/bin/llama-server \
  --model ./models/Qwen3-8B-Q4_K_M.gguf --alias qwen3-8b-q4km \
  --host 127.0.0.1 --port 8080 --ctx-size 4096 --n-gpu-layers 99 \
  --parallel 1 --jinja
```

Check the pinned build's `--help`: flags/template/reasoning-parser behavior are
version-dependent. Start conservatively at 4096 context and one slot. Full
offload plus KV/workspace must actually fit the 8 GB card; 4-bit weights alone
do not prove that. Qualify context overflow, GPU offload, prompt-cache behavior
and server seed handling using tiny synthetic requests before loading study
tasks. If the rig requires partial CPU offload, record the exact layer split;
it changes the physical workload. Bind the server and meter bridge locally
unless Ed explicitly configures an isolated trusted network.

Copy `configs/align/x86/pilot.draft.json` to a local pilot config. Fill in
`server_pid`, exact GGUF SHA-256, llama.cpp commit, offline cache path and rig
provenance. Set the actual meter URL/fields. The supplied null identity values
deliberately fail validation. The draft is 2 task pairs × 2 seed indices ×
benign/sabotage = 8 members before any redos. The 1024-token per-turn cap,
40-turn limit and server context are **unqualified planning choices**; promote
none of them to a registered design without a capability/context pilot.

```sh
python3.13 -B -m joulewise.align.linux.session ./pilot.local.json \
  --output ./runs/x86-pilot-001 --validate-only
# Close agents and other clients, then run in a clean rig session:
python3.13 -B -m joulewise.align.linux.session ./pilot.local.json \
  --output ./runs/x86-pilot-001
```

`--validate-only` opens no devices, server, cache or output directory. For a
synthetic meter rehearsal, replace the whole `wall_meter` object with
`configs/align/x86/wall-meter-replay.draft.json`; it does not replace the
requirement for live AC data. `wall_meter: null` exercises missing-stream flags.
The driver has bounded individual HTTP requests, not a global run deadline;
supervise it externally on the rig and preserve incomplete attempt directories.

## Verification and remaining decisions

The implementation tests use an in-memory fake SSE server, fake ctypes NVML,
synthetic sysfs and `/proc`, fake HTTP meter responses, and CSV replay. They do
not bind sockets, contact a server, fetch SHADE, download weights, or use GPUs.

```sh
python3.13 -B -m unittest tests.align.test_linux_backend
python3.13 -B -m unittest tests.align.test_power_nvml
python3.13 -B -m unittest tests.align.test_runner
python3.13 -B -m unittest tests.align.test_records
python3.13 -B -m unittest tests.align.test_attribution
python3.13 -B -m unittest tests.align.test_shade
```

Before measurements, Ed/lead must qualify the actual 3050's supported channels,
NVML sensor behavior, powercap permissions/wrap period, whole-desktop AC meter,
clock alignment, quiet sampling overhead, driver/CUDA/server pins, actual GPU
offload/VRAM headroom, template/tools/reasoning, determinism and capability of
the selected 8B quantization. This implementation does not answer those with
fake evidence. The existing native Apple endpoint/R0 tests
(`tests.align.test_apple_endpoint`, `tests.align.test_r0_mlx_native` on the
measurement branch) must be run by the lead on the MLX-capable Mac if integrating
with that branch; MLX cannot execute in this sandbox. New Linux code imports no
MLX and adds no native MLX tests.

Open decisions: meter hardware/export protocol and trust/accuracy; CPU model
and package domains; actual GGUF artifact and license; model capability at this
quantization; allowable context/turn/episode budget; treatment of projected seed
collisions and lack of emitted token IDs; judge/monitor placement after capture;
Linux AC/thermal/admission and cooldown policy; energy attribution/calibration
and registration of replication statistics. These belong to the lead before
claim-bearing use. Block-5 data and its analysis pipeline remain outside this
work.
