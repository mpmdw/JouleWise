# Phase 2 Hardware-Slice Implementation Guide

Audience: the next implementing agent (or human) who picks up the **gated**
Phase 2 slices once their hardware/evidence gates open. The mock vertical
slice (2A-2F, 2J) is done and committed; this guide turns the higher-level
`phase_2_plan.md` slice sections into code-level, pinned-API detail in the
same style that the mock slices were specified, so you can implement against
locked contracts without re-deriving the design.

Read first, every time:

- `docs/phase_2/phase_2_plan.md` - the slice you are doing, plus the
  "Cross-Slice Contracts" and "Intended Module Map" sections.
- The **shipped** code your slice plugs into (read the actual source, not
  this summary): `joulewise/adapters/__init__.py` (the registry seam),
  `joulewise/adapters/mock_runtime.py` + `mock_telemetry.py`
  (the adapter shape to mirror), `joulewise/controller.py` (lifecycle and
  how adapters are driven), `joulewise/reduce.py` (what metadata/trace shape
  the reducer consumes), `joulewise/bundle.py` (artifact writer).
- `docs/contracts/measurement_methodology.md` (boundaries, clocks, idle
  subtraction) and `docs/contracts/run_bundle_layout.md`.
- `docs/decision_log.md` decisions cited per slice below.

Standing rules (inherited from the mock slices):

- **Stdlib-only core; backends behind extras (D-009).** Real backend
  libraries (`mlx_lm`, `matplotlib`, ...) are imported **lazily inside the
  adapter method that needs them**, never at module top level. A missing
  import becomes a structured `runtime_unavailable` / `telemetry_unavailable`
  `AdapterResult`, not an `ImportError`. CI installs no extras and must stay
  green: every hardware test either runs without the backend (structured-
  failure path, fixture parsing) or is `skipUnless`-gated on the import.
- **Clock discipline (D-003/D-019).** Every timestamp is an epoch-UTC float
  from the injected `joulewise.clock.Clock`. Real adapters receive the clock
  in their constructor (the registry passes it: see `resolve_runtime`/
  `resolve_telemetry`). `SystemClock` is the only caller of `time.time()`.
  Real runs use `SystemClock` (the CLI binds it whenever any backend is not
  mock, per D-020), so real workload time is real; you still read it through
  the injected clock so the lifecycle code path is identical to the mock's.
- **Raw evidence first (D-002).** Each real telemetry adapter spawns its
  native sampler as a subprocess writing a raw file under `<bundle>/raw/`,
  preserved verbatim; `power_trace.csv` is *derived* from it. A parser bug is
  fixed and the bundle re-reduced (`reduce_bundle`) without re-running
  hardware. The controller never reads samples mid-window.
- **Rail manifest (D-018).** Each telemetry adapter declares
  `device_metadata()["rail_manifest"]` = the exact list of `rail` values the
  reducer sums to the canonical `power_w`. The reducer already reads this key
  path (`metadata["device"]["rail_manifest"]`); match it.
- **Unsupported is a result, not a crash (D-012).** Structural
  incompatibility => `did_not_fit` / `runtime_unavailable` /
  `telemetry_unavailable` (status `unsupported`, a publishable finding).
  Fixable operational problems => `permission_denied` /
  `transport_unavailable` / `unknown_error` (status `failed`).
- **One slice per session.** Tests green, evidence captured in a run report
  and the Phase 2 applicability table, `RUN_STATE.md`/`TASK_QUEUE.md`
  updated. Do not start a gated slice whose gate is unmet.

The registry seam you extend (already shaped for this):
`joulewise/adapters/__init__.py` resolves backend enums to adapters. Each new
real backend adds one branch to `resolve_runtime` / `resolve_telemetry` /
`resolve_transport` returning either `(adapter, None)` or, when the backend's
library/host is unavailable, `(None, AdapterResult(ok=False, ...))`. The
controller drives whatever it gets through the identical lifecycle, so a real
runtime composes with mock telemetry and vice versa - exploit that for
incremental bring-up (e.g. real MLX + mock telemetry before 2H exists).

---

## Slice 2G: MLX Runtime Adapter

**Gate:** a chosen model (D-016 closed or provisional) **and** `mlx_lm`
installed in a Mac venv (`pip install 'joulewise[mac]'`; R-003). Until then,
the registry's `mlx` branch already returns the correct
`runtime_unavailable` naming the `[mac]` extra - that path is testable now
and must keep working.

**New files:** `joulewise/adapters/mlx_runtime.py`, `tests/test_mlx_runtime.py`.
**Touch:** `joulewise/adapters/__init__.py` (wire the `mlx` branch to the real
adapter behind a lazy import), `pyproject.toml` (`[mac]` extra already lists
`mlx-lm`; confirm the pin), `configs/examples/mac_mlx_local.json` (set the
chosen model once D-016 closes).

**Pinned adapter (`MlxRuntimeAdapter`, constructor takes `clock`; `name = "mlx"`):**

- `prepare(config)`: lazily `import mlx_lm` inside the method; on `ImportError`
  return `AdapterResult(ok=False, failure_reason=RUNTIME_UNAVAILABLE,
  message=...)` naming the `[mac]` extra and distinguishing "not installed"
  from "cannot install" in the run report (D-009/D-012 ambiguity note). On
  success, load the model+tokenizer (`mlx_lm.load(...)`), recording load
  wall-time (via the clock), the resolved model path/revision, and `mlx`/
  `mlx_lm` versions into `AdapterResult.metadata` (the controller stores it
  under `metadata.adapters.runtime.prepare_metadata`). Hold the loaded
  model/tokenizer on the instance.
- `warmup(config)`: one short generation (a handful of tokens) to force lazy
  graph/Metal compilation, discarded; strictly before the measured window
  (the controller already calls warmup before `start_sampling`).
- `run_workload(config)`: stream generation capturing a wall timestamp
  (`clock.now()`) per emitted token. Emit the event taxonomy:
  `phase_start"/"prefill"`, then at first token `phase_end"/"prefill"` +
  `phase_start"/"decode"` (boundary approximation `phase_boundary_method:
  "first_token"` recorded in metadata - exact prefill timing upgrades this
  later with no schema change), a `token` event per token
  (`metadata={"index": i}`), `phase_end"/"decode"`. Write
  `outputs/response.txt` (full text) and `outputs/tokens.jsonl` (one
  `{"index","timestamp_s"}` per token). Return `RuntimeResult(token_count=
  prompt+output, output_token_count=output, ...)`.
- **Workload mapping:** `prompt_text` used directly; `prompt_tokens` without
  text => deterministic synthetic prompt of that many tokens (tokenizer-
  measured); `output_tokens` => `max_tokens` with EOS handling recorded
  (suppress-and-record, so the measured decode length is the configured one).
- `cleanup(config)`: drop references to the model so Metal frees memory.

**Tests (run WITHOUT mlx in CI):** the structured-failure path (monkeypatch
the import to raise => `runtime_unavailable` naming `[mac]`); workload mapping
with a fake tokenizer (prompt-token synthesis is deterministic); event-shape
unit test driving a fake streamer that yields N tokens (assert the
prefill/decode/token event sequence and monotonic timestamps). A **manual
smoke procedure** (commands + expected artifacts) is documented for the real
Mac and executed when hardware time exists; capture `response.txt` + the token
timeline in a run report.

**Acceptance:** real generation produces a complete bundle (with mock
telemetry if 2H is not done - composition is the point); token timeline
monotonic; `ttft_s > 0` and `< total`.

**Fallback (R-003):** if MLX cannot install/run, a `llama.cpp`-Metal adapter
becomes the Mac runtime (subprocess to a `llama-cli`-style binary, GGUF
weights); update the plan and log the decision. The composition contract is
unchanged.

---

## Slice 2H: powermetrics Telemetry Adapter

**Gate:** a captured **privileged** `powermetrics` sample whose field names
are recorded in the Phase 1 exit checklist instrumentation section (the
parser pins to the *captured sample*, not to docs/memory - macOS versions
vary), plus the D-004 scoped sudoers rule installed
(`<user> ALL=(root) NOPASSWD: /usr/bin/powermetrics`). The privileged sample
is captured during the user's local auth session; do not start the parser
without it.

**New files:** `joulewise/adapters/powermetrics.py`,
`tests/test_powermetrics.py` (+ a fixture file built from the captured
sample under `tests/fixtures/`). **Touch:** `joulewise/adapters/__init__.py`
(wire the `powermetrics` branch).

**Pinned adapter (`PowermetricsTelemetryAdapter`, constructor takes `clock`;
`name = "powermetrics"`):**

- **Spawn (D-002/D-004):** `sudo -n /usr/bin/powermetrics -i <interval_ms>
  --samplers cpu_power,gpu_power,ane_power,thermal --format plist -o
  <bundle>/raw/powermetrics.plist`, interval derived from
  `sampling.power_hz`. `start_sampling` launches it (capturing the `Popen`);
  `stop_sampling` terminates the sudo process (sudo relays SIGTERM to the
  child), confirms child exit, retains the raw file verbatim, then parses it.
- **Capability pre-check at `prepare`-equivalent** (telemetry has no
  `prepare`; do it in `device_metadata` or a lazy check inside
  `start_sampling`): probe `sudo -n /usr/bin/powermetrics -n 1 -i 100 ...`;
  failure => `AdapterResult(ok=False, failure_reason=PERMISSION_DENIED,
  message=<the exact sudoers line to install>)`. This converts a mid-run
  privilege failure into an up-front structured `failed` (D-004).
- **Parsing:** powermetrics plist streams are NUL-separated plist documents
  (confirm framing against the captured sample - this is why the slice is
  gated); parse with stdlib `plistlib`. Emit one `PowerSample` per rail
  (`cpu_power`, `gpu_power`, `ane_power`, watts after mW conversion) per
  sample (D-018). `device_metadata` declares `rail_manifest =
  ["cpu_power","gpu_power","ane_power"]` as the canonical sum.
- **`measure_idle`:** a bounded `-n <count>` invocation sized to
  `sampling.idle_seconds`; mean/stddev computed from parsed samples;
  `telemetry_backend = TelemetryBackend.POWERMETRICS`.
- **`thermal_state`:** parse the `thermal` sampler (pressure level) into
  `ThermalState` before/after the window.

**Tests (run WITHOUT a Mac in CI):** parser correctness against the fixture
(rails, mW->W, sample count, timestamps); rail-manifest content; idle
mean/stddev on a known fixture; the `permission_denied` path when `sudo -n`
fails (monkeypatch the probe). A **real-machine smoke** records an idle
baseline + a measured window in a run report.

**Acceptance:** real samples flow `raw -> parsed -> trace -> reducer`;
`observed_sampling_hz` within 20% of requested at 1-10 Hz; permission-denied
path yields the documented structured failure.

**Fallback:** if plist framing fights back, `--format text` parsing of the
same fields (same contract, uglier parser); if sudo policy is refused,
R-002 fallbacks (operator-attended runs).

---

## Slice 2I: Mac Vertical Slice Integration (the flagship demo)

**Gate:** 2F, 2G, 2H all done. No new module - this is an integration +
evidence slice.

**Actions:** run `mac_mlx_local.json` end-to-end (`python3 -m joulewise run
configs/examples/mac_mlx_local.json`); then a 3-repetition experiment
(`repetitions: 3` => the 2F experiment runner + cooldown gate, which is now a
**real** idle-power-recovery gate, not the mock skip); verify D-013 conduct
(deferred logging on, controller quiescent during the window);
`validate-bundle` green on all bundles; generate the report (2J). Set the Mac
row of the Phase 2 applicability table to `supported` (or record the blocking
finding).

**Acceptance (Phase 2 headline, instantiated):** one command -> complete Mac
bundle; 3 reps report mean/stddev via the manifest with cooldown gates
recorded; sanity: idle mean < measured mean, `ttft < total`, energy/token
within an order of magnitude of public Apple-Silicon LLM figures (a sanity
bound, recorded in the report).

---

## Slice 2K: NVIDIA/vLLM + nvidia-smi + SSH Transport

**Gate:** P1-006 NVIDIA evidence (SSH reachable; `nvidia-smi` power queries
work; vLLM installable; VRAM documented). Do not start on assumption.

**New files:** `joulewise/adapters/ssh_transport.py`,
`joulewise/adapters/vllm_runtime.py`, `joulewise/adapters/nvidia_smi.py`, a
self-contained remote runner script (shipped to the node), and matching
tests. **Touch:** the registry (`ssh` transport, `vllm` runtime, `nvidia_smi`
telemetry branches).

**Design center - the remote-runner protocol (reused by 2L and Phase 3):**
the runtime adapter ships a self-contained runner script to the node, runs it
with a JSON args file, and collects an artifacts dir (events JSON, output
text, token timeline, runner log, exit code) back into the bundle. The runner
depends only on the remote env (vLLM); the `joulewise` package is **not**
installed remotely.

**Pinned pieces:**

- **SSH transport** (`name = "ssh"`): wrap `ssh`/`scp` subprocesses (no
  paramiko, D-009); `run_command` with timeout + structured
  `transport_unavailable` on unreachable host; `collect_artifact` via `scp`;
  `connection_metadata` records host, user, and round-trip marker timing
  (D-003 clock-offset bound).
- **nvidia-smi telemetry** (`name = "nvidia_smi"`): remote
  `nvidia-smi --query-gpu=timestamp,power.draw,temperature.gpu
  --format=csv,noheader,nounits -lms <interval>` started in background with a
  pidfile, stopped by pid kill, CSV collected to `raw/`, parsed to trace
  rows; `rail_manifest = ["gpu_board"]` (D-018 boundary: board power only,
  host CPU/DRAM excluded - record the limitation).
- **Clock (D-003):** marker events before/after remote stages bound node
  clock offset; record the bound in metadata; the reducer flags cross-node
  intervals shorter than the bound (relevant in Phase 3, not single-node 2K).

**Tests (CI-safe):** local-loopback fake transport; CSV-fixture parsing for
nvidia-smi; runner-script arg handling. Real-node smoke when P1-006 evidence
exists; record a remote bundle in a run report; fill the applicability table.

**Acceptance:** one command on the controller produces a complete bundle for
the remote 3050 target; structured failures for unreachable host / missing
nvidia-smi demonstrated.

**Fallback:** if vLLM is too heavy for 8 GB (R-006 cousin), `llama.cpp`-CUDA
becomes this target's runtime (also satisfies D-015's portability
preference); log the decision.

---

## Slice 2L: Orin Adapter

**Gate:** P1-006 Orin evidence (SSH, runtime choice, telemetry mechanism).

Mirror 2K with Orin specifics: runtime via the 2K remote-runner protocol
(llama.cpp-CUDA or a vendor stack - pick with evidence, log the decision);
telemetry preferring INA3221 sysfs polling (VDD_IN rail, D-018) via a tiny
remote poller, falling back to `tegrastats` parsing, with a wall-meter last
resort (R-008). One complete bundle from the device; applicability table +
Phase 1 Orin rows updated.

**Fallback (R-008):** runtime-only target, or drop to stretch.

---

## Slice 2M: Homogeneous Baselines + Qualitative Reproduction

**Gate:** 2I plus at least one of {2K, 2L} (two targets minimum for the
cross-target table; Mac-only is the degraded-but-publishable floor, R-012).

**New:** a config-matrix generator script under `scripts/`, and
`docs/phase_2/baseline_results.md` (the summary doc with figures). The
workload matrix (per target x model, from D-016):

| Profile | prompt_tokens | output_tokens | reps |
|---|---|---|---|
| short_short | 128 | 64 | 5 |
| long_short (prefill-heavy) | 4096* | 64 | 5 |
| short_long (decode-heavy) | 128 | 512 | 5 |
| mid_mid | 1024 | 256 | 5 |

*capped at model context / target memory; the capped value is recorded.

**Protocol:** D-014 in full (n>=5, round-robin interleaving where reload cost
permits, cooldown gates, raw points kept); per-target idle characterization
(5-minute idle trace) once per session.

**Acceptance:** energy/token and energy/request with 95% t-intervals per
target x profile; prefill-heavy vs decode-heavy show the expected power
asymmetry **or** the deviation is reported with the traces (acceptance is
"measured and explained", not "matched expectations"); every attempted
target x model ends `supported` or a recorded structured failure.

---

## Cross-cutting: closing D-016 (model selection) before 2G/2K

D-016 is a decision step, not code, and it gates 2G/2K install targets. Apply
its fixed criteria (runs on all primary targets; fits the smallest VRAM at
the chosen quantization; KV-per-token in an interesting transfer range; open
weights permitting academic use + local mirroring; prefer one small + one mid
model from one family). Record in the decision log: chosen model(s), exact
revisions, per-runtime artifact paths (MLX repo, GGUF file, HF repo for
vLLM), KV bytes/token (for the Phase 3 table), and the fallback candidate;
mirror weights locally (R-014). Requires P1-001 supervisor scope (or explicit
user say-so) and a disk-space check. The candidate set
(Qwen2.5-1.5B/7B-Instruct, Llama-3.2-1B/3B-Instruct, Llama-3.1-8B-Instruct)
is narrowed with load evidence on Mac MLX + one CUDA target.

---

## Suggested order when gates open

1. Close **D-016** (unblocks install targets).
2. **2G** with mock telemetry (real generation, synthetic power) - proves the
   MLX adapter in isolation.
3. **2H** against the captured fixture, then on the real Mac.
4. **2I** integration + 3-rep variance (the flagship demo).
5. **2K** (first remote target) when P1-006 NVIDIA evidence exists, then
   **2L** for Orin.
6. **2M** baselines across whatever targets reached `supported`.

Each step ends with: tests green, a dated run report, the applicability table
updated, and `RUN_STATE.md`/`TASK_QUEUE.md` advanced.
