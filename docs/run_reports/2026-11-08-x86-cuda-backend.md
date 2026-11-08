# x86 CUDA backend: handoff for the 2026-11-08 brief

Branch: `x86/2026-11-08-cuda-backend`. Implementation environment: the blinded
Mac sandbox, Python 3.13.18. **DRAFT / PROVISIONAL; fake evidence only.**

## Delivered

- Located ALIGN on the locally available measurement-branch Git objects,
  rather than main. Imported its platform-neutral ChatEndpoint/PowerSampler
  contracts, OpenAI SSE client, runner, records, offline SHADE port, existing
  NVML implementation and attribution helpers from `9c40e4e5d`.
- Added `joulewise/align/linux/{backend,seeds,session}.py`: fresh llama.cpp
  endpoints per member; shared SHADE tool loop; canonical seed and wire-seed
  provenance; server token accounting; structured reasoning, request and
  completion capture; full transcripts; partial failed-request evidence;
  exclusive attempt directories with digests. No uncertain inference retries.
- Added `linux/samplers.py`: RAPL package cumulative energy in joules with raw
  µJ readings/ranges; pluggable AC meter interface; bounded HTTP-JSON meter;
  labelled synthetic CSV replay. The Linux driver always requests a wall
  stream and flags missing, incomplete or failed streams per member.
- Reused the existing ctypes NVML GPU board power/energy sampler unchanged.
  Added additive `rapl_energy` record support and conservative unknown-age
  treatment in attribution. No Apple or R0 source files changed.
- Added `linux/quiet.py`: /proc CPU-tick differences, PID/start-time identity,
  process-tree exclusions, raw receipts, rolling CPU-s/s intervals, largest
  single-process contention judgement, one redo and a retained contended
  second attempt. Unknown CPU observations remain indeterminate tooling faults.
- Added the DRAFT two-pair, benign/sabotage, Qwen3-8B Q4_K_M template and meter
  replay examples under `configs/align/x86/`.
- Wrote [CUDA-BACKEND.md](../x86/CUDA-BACKEND.md), including architecture,
  rig installation/build/serving steps, execution, boundaries and open gates.

Changed-file groups: `joulewise/align/` (shared import plus Linux adapters),
`tests/align/` (synthetic tests/fixtures), `configs/align/x86/`, the x86 runbook,
and this report. The imported test slice omits the NVML preflight-CLI subcheck
and live SHADE-cache conformance checks, whose owning implementations remain
on the measurement branch.

Commits: `ba03c31a9` imports the shared boundary and fixture tests. The second
commit, `feat(align): add draft llama.cpp CUDA pilot and Linux measurement path`,
contains the Linux implementation, RAPL extensions, templates, runbook and
this handoff. Both are local; nothing was pushed.

## Verification

Each unittest module was run separately; no suite/discovery/shard run occurred.
Final targeted results:

| Command | Result |
|---|---|
| `python3.13 -B -m unittest tests.align.test_linux_backend` | 23 passed |
| `python3.13 -B -m unittest tests.align.test_power_nvml` | 18 passed, 1 skipped (optional pynvml package absent; ctypes path tested) |
| `python3.13 -B -m unittest tests.align.test_runner` | 24 passed |
| `python3.13 -B -m unittest tests.align.test_records` | 4 passed |
| `python3.13 -B -m unittest tests.align.test_attribution` | 36 passed |
| `python3.13 -B -m unittest tests.align.test_shade` | 19 passed, synthetic fixture only |
| `python3.13 -B -m compileall -q joulewise tests` | Passed |
| CLI `--validate-only` with synthetic provenance and an unused output path | Passed; no output directory created |
| Git whitespace/source comparison and protected-path review | Passed |

125 unittest cases: **124 passed, 1 optional-dependency skip**. Test execution,
including development reruns, stayed far below 20 minutes. Python 3.11 is not
installed here, so its CI check remains unexecuted. No MLX tests were added;
new code imports no MLX. Lead-side native regression checks on the measurement
branch are `tests.align.test_apple_endpoint` and
`tests.align.test_r0_mlx_native`, on an MLX-capable Mac outside this sandbox.

The new tests exercise an in-memory fake llama.cpp SSE server (no socket),
fake RTX-3050-shaped NVML capability failures, synthetic RAPL/proc files,
HTTP meter field mapping/stale timestamps, missing meters, CSV exhaustion,
request failures, exact seed-law golden, tool history, accounting, reasoning,
artifact round trips/digests, root PID reuse, aggregate-only CPU load, bursts,
and exactly one redo with both attempts retained.

## Limits, uncertainty and next exact step

No hardware was validated. Driver/CUDA/llama.cpp compatibility, actual VRAM
headroom, context/cache behavior, tools and reasoning templates, the chosen
GGUF, CPU/RAPL support, AC meter and Linux thermal/admission policy still need
rig evidence. Server flags are example commands to check against the pinned
build's help, not a tested installation recipe. No emitted token IDs or
cross-engine token-identity claim is supplied.

The existing uint64 logical seed law is preserved. The actual llama.cpp wire
seed is explicitly projected to uint32, with the random-seed sentinel refused;
cross-engine PRNG/output equality is not established. The lead must accept
this portability policy, choose the actual model/meter, and qualify it before
registration. RAPL decreases remain ambiguous wrap/reset observations; NVML
and RAPL are separate physical boundaries from AC wall power. Unqualified
sensor age/accuracy cannot become a finite precision claim.

The quiet guard ports the CPU rule, not the Mac LaunchAgent/custody census.
Its redo decision is post-episode, not a mid-stream cancellation. The pilot has
per-request timeouts but no global run deadline; crash recovery, authenticated
sealing and registered bundle/campaign integration remain lead work. Missing
judges/monitors remain missing and flagged; no v4 transcript was scored.

Next: review the two local commits, provision a pinned local GGUF/server and a
real whole-desktop meter on the rig, fill a local copy of the DRAFT config,
validate it, then have Ed run the clean-rig capability/telemetry qualification
in the runbook. If integrating onto the measurement lane, the shared import
already exists there: integrate the Linux commit with the lead's normal
review and native Apple regression checks before any measurement.

## Boundary compliance

No network access, weight download, real measurement-data read, Block-5
analysis pipeline, GPU load or quiet-Mac capture was performed. Reads of
measurement-branch code used this clone's local Git object access only.
Sealed external paths were not followed. The long analysis job was untouched.
`RUN_STATE.md`, `TASK_QUEUE.md`, `docs/process/state_kernel.json` and
`tests/test_gen_state.py` were not edited; no coordination task was registered.
The user's explicit no-full-suite and coordination-file restrictions override
the generic repository end-of-run checklist for this run.
