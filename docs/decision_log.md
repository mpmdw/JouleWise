# Decision Log

This is the canonical record of design decisions for JouleWise. Every decision
that binds later work, trades off real alternatives, or would otherwise need to
be re-derived by a future agent gets an entry here.

## How To Use This Log

- Before implementing anything non-trivial, check whether a decision here
  already covers it. Do not silently re-decide settled questions.
- When you make a new decision of this kind during a run, add an entry, link it
  from the run report, and reference its ID (`D-NNN`) in the code review or doc
  that applies it.
- Statuses: `accepted` (binding until revisited), `open` (criteria defined,
  evidence pending), `superseded by D-NNN`.
- Every entry must include Options Considered and Considerations. A decision
  without recorded alternatives is not auditable.
- Revisit triggers are part of the contract: when a trigger fires, the decision
  must be re-examined, not quietly worked around.

## Index

| ID | Title | Status |
|---|---|---|
| D-001 | Run bundles store normalized `config.json`, not YAML | accepted |
| D-002 | Telemetry sampling via subprocess + file, no controller threading | accepted |
| D-003 | Timestamp and clock-alignment policy | accepted |
| D-004 | `powermetrics` privilege workflow | accepted |
| D-005 | One bundle per repetition, grouped by experiment manifest | accepted |
| D-006 | Dashboard v1 is a static HTML report generator | accepted |
| D-007 | YAML config input is deferred | accepted |
| D-008 | Split runs arrive via schema v0.2 (`run_kind` + `split_plan`) | accepted |
| D-009 | Dependency policy: stdlib core, optional extras | accepted |
| D-010 | Run ID scheme | accepted |
| D-011 | `summary_metrics.json` is the bundle completion marker | accepted |
| D-012 | Failure-reason to run-status mapping | accepted |
| D-013 | Controller-as-DUT mitigation for Mac-local runs | accepted |
| D-014 | Statistical protocol for repeated runs | accepted |
| D-015 | Split-mechanism priority and same-runtime rule | accepted |
| D-016 | Benchmark model selection | open |
| D-017 | CI scope | accepted |
| D-018 | Per-backend `power_w` definition and rail policy | accepted |
| D-019 | Mock adapters use simulated time via an injectable clock | accepted |
| D-020 | CLI binds `FakeClock` for all-mock runs, `SystemClock` otherwise | accepted |
| D-021 | Controller flushes `events.jsonl` before the reduce stage | accepted |
| D-022 | Auto-generated run-ID suffix is config-hash-derived, not random | accepted |
| D-023 | Per-item phase status lives solely in the exit checklists | accepted |

---

## D-001: Run bundles store normalized `config.json`, not YAML

- Date: 2026-06-09
- Status: accepted
- Phase: 2+

Context: `docs/contracts/run_bundle_layout.md` originally specified `config.yaml`
as the normalized config artifact, but the package is intentionally
zero-dependency and the stdlib has no YAML parser. The Phase 1 CLI already
rejects non-JSON configs.

Options considered:

1. Keep `config.yaml` in the bundle and add PyYAML as a core dependency.
   Pro: human-friendly artifact. Con: breaks the zero-dependency core for a
   cosmetic gain; the bundle copy is machine-written anyway.
2. Store both `config.yaml` (if input was YAML) and `config.json`. Pro:
   preserves the authored artifact. Con: two sources of truth in the bundle;
   normalization questions; still needs the dependency.
3. Store normalized `config.json` only. Pro: stdlib `json` round-trips it; the
   bundle copy is for machines and reducers, not for authoring; deterministic
   key ordering enables config hashing. Con: marginally less pleasant to read.

Decision: option 3. The bundle stores `config.json`, written with sorted keys
and a recorded SHA-256 hash in `metadata.json`.

Considerations: the bundle's job is auditability and reduction, not authoring
ergonomics. Sorted-key JSON gives us a stable config hash for free, which
Phase 4 aggregation uses to group runs. Human authoring comfort is a separate
question handled by D-007.

Consequences: `run_bundle_layout.md` updated; the bundle writer (Slice 2A)
writes JSON; config hashing is defined as SHA-256 over the sorted-key,
2-space-indented JSON encoding.

Revisit when: D-007 introduces YAML input, or a downstream consumer needs the
originally-authored file preserved.

---

## D-002: Telemetry sampling via subprocess + file, no controller threading

- Date: 2026-06-09
- Status: accepted
- Phase: 2+

Context: power sampling must run concurrently with the workload. The
`TelemetryAdapter` contract already has `start_sampling`/`stop_sampling`, but
nothing specified the concurrency mechanism.

Options considered:

1. Python threads inside the controller polling the telemetry source. Pro:
   single process. Con: GIL interaction with an in-process runtime (MLX
   generation) can distort sample timing; threading bugs are the classic
   source of flaky harnesses; the controller would be doing work during the
   measured window (see D-013).
2. `asyncio` event loop. Pro: no threads. Con: forces async contracts onto all
   adapters for one use case; same in-process timing concern.
3. Each telemetry adapter spawns its native sampler as a subprocess that
   writes to a file in the bundle; `start_sampling` launches it,
   `stop_sampling` terminates it and parses the file. Mock telemetry simply
   synthesizes samples. Pro: real backends (`powermetrics`, `nvidia-smi
   -lms`) are already long-running sample-emitting processes, so this matches
   their grain; the controller sleeps during the measured window; the raw
   backend output is preserved verbatim in the bundle as source of truth.
   Con: process lifecycle management per backend; parsing happens after the
   fact.

Decision: option 3.

Considerations: the deciding factors are measurement integrity (controller
does nothing during the measured window) and auditability (the raw sampler
output lands in `raw/` untouched, and `power_trace.csv` is derived from it,
so a parsing bug can be fixed and re-reduced without re-running hardware).
This also keeps the v1 controller single-threaded and therefore simple to
reason about and test.

Consequences: every real telemetry adapter defines: spawn command, raw output
path under `raw/`, stop mechanism, and a parser raw -> `PowerSample` rows.
The controller never reads samples mid-run; live progress display is out of
scope for v1.

Revisit when: a backend appears that cannot run as a file-writing subprocess,
or sub-second live feedback becomes a requirement.

---

## D-003: Timestamp and clock-alignment policy

- Date: 2026-06-09
- Status: accepted
- Phase: 2 (single node), 3 (multi node)

Context: every event and power sample carries `timestamp_s`. Reducers join
events to traces by time. Phase 3 joins traces across two machines, so clock
error becomes energy-attribution error.

Options considered:

1. Monotonic clock only. Pro: immune to wall-clock steps. Con: meaningless
   across processes and machines; cannot align controller, sampler subprocess,
   and remote nodes.
2. Wall clock (epoch UTC) only. Pro: universal meaning. Con: NTP steps/slew
   can distort intervals mid-run.
3. Epoch UTC (`time.time()`) as the canonical `timestamp_s` everywhere, with
   per-process monotonic-vs-wall offset recorded in metadata, NTP sync state
   recorded per node, and controller-mediated marker events bounding
   cross-node offset for split runs.

Decision: option 3.

Considerations: at our sampling rates (~1-10 Hz) the precision we need is
tens of milliseconds; LAN NTP holds well under that. The marker procedure
(controller timestamps a no-op command on the remote node immediately before
and after each remote stage; round-trip halving bounds the offset) gives a
recorded, per-run error bound rather than an assumption. Monotonic-only would
make multi-process correlation impossible, and our samplers are separate
processes by D-002.

Consequences: `metadata.json` gains `clock` fields (ntp_synced, estimated
offset bound, method). The methodology doc gets a Clock Synchronization
section (done in the same change as this entry). Reducers must treat
cross-node intervals shorter than the recorded offset bound as unreliable and
flag them in measurement quality.

Revisit when: sampling moves to >=100 Hz (wall meters with fast export) or a
target cannot run NTP.

---

## D-004: `powermetrics` privilege workflow

- Date: 2026-06-09
- Status: accepted
- Phase: 2

Context: Phase 1 evidence shows `/usr/bin/powermetrics` exists and "must be
invoked as the superuser". Automated benchmark runs need a non-interactive,
auditable way to obtain that privilege. Hard rule inherited from Phase 1:
document the privilege workflow, never bypass it in code.

Options considered:

1. Run the whole controller as root. Pro: simple. Con: massively
   over-privileged; everything the harness writes becomes root-owned; worst
   auditability.
2. Interactive `sudo` prompt at run start. Pro: zero configuration. Con:
   breaks unattended/repeated runs (sudo timeout mid-experiment), and an
   agent cannot answer the prompt.
3. A `sudoers` rule scoped to exactly `/usr/bin/powermetrics` (NOPASSWD) for
   the benchmark user, installed once by the user, documented in the
   Phase 1 exit checklist's instrumentation section. Controller pre-checks
   capability with
   `sudo -n /usr/bin/powermetrics -n 1 -i 100` style probe and fails with
   structured `permission_denied` if absent.
4. A setuid wrapper binary. Con: writing setuid programs to avoid a sudoers
   line is strictly worse on every axis.

Decision: option 3, with option 2 documented as the manual fallback for
one-off runs.

Considerations: the scoped sudoers rule grants exactly one binary, owned by
Apple, that only reads telemetry. The pre-check converts a mid-run privilege
failure into an up-front structured failure, which the Phase 1 contract
(structured outcomes, not crashes) requires. Passwords never appear in code,
configs, or logs.

Consequences: the powermetrics adapter (Slice 2H) always invokes via
`sudo -n`; the Phase 1 exit checklist's instrumentation section gains the
exact sudoers line for the user to install during the 2026-06-10 auth
session; `permission_denied` failures tell the operator precisely what to
add.

Revisit when: macOS changes powermetrics privilege requirements, or the
measurement machine is shared and the owner declines the sudoers rule (then
runs become operator-attended, option 2).

---

## D-005: One bundle per repetition, grouped by experiment manifest

- Date: 2026-06-09
- Status: accepted
- Phase: 2+

Context: `workload_profile.repetitions` exists in the config schema but
nothing defined whether N repetitions produce one bundle or N bundles.

Options considered:

1. One bundle containing N sub-runs. Pro: one directory per experiment. Con:
   every artifact (trace, events, summary) needs an internal rep dimension;
   the "bundle = one measured run" invariant breaks; partial failure of rep 3
   of 5 makes bundle status ambiguous; reducers get conditional logic
   everywhere.
2. One bundle per repetition, plus an experiment manifest
   (`runs/experiments/<experiment_id>.json`) listing member bundle IDs, the
   shared config hash, and creation time. Pro: bundle invariant stays "one
   bundle = one measured run = one status"; per-rep failure is naturally
   isolated; Phase 4 aggregation walks manifests. Con: more directories; the
   manifest is one more artifact to maintain.

Decision: option 2. Bundle IDs of members are `<experiment_id>__r<N>`.

Considerations: the strongest argument is statistical hygiene in Phase 4 -
each repetition is an independent observation with its own quality fields
(thermal drift, dropped samples), and forcing that independence into the
directory structure prevents accidental cross-rep contamination in reducers.
Partial experiments (3 of 5 reps succeeded) stay representable without a
special bundle state.

Consequences: controller gains an experiment loop (Slice 2F); cooldown gates
between reps live at the experiment level; `run_bundle_layout.md` documents
the manifest.

Revisit when: never expected; this is structural.

---

## D-006: Dashboard v1 is a static HTML report generator

- Date: 2026-06-09
- Status: accepted
- Phase: 2 (v1), 4 (figures)

Context: the original Phase 2 checklist said "dashboard v1 as a read-only run
browser" with no definition. Any web stack is a large dependency and
maintenance surface for a single-user research artifact.

Options considered:

1. Flask/FastAPI web app. Pro: interactive. Con: server process, dependency
   tree, session management for zero concurrent users; classic capstone time
   sink; violates "polish after vertical slice" rule in spirit.
2. Jupyter notebooks only. Pro: flexible. Con: not a "run browser"; execution
   state is not reproducible evidence; poor handoff artifact.
3. `python3 -m joulewise report runs/ --output report/` generating static
   HTML: an index table of runs plus a per-run page with metadata, summary
   metrics, and a power-trace chart with phase shading. Charts rendered by
   matplotlib (Agg) to PNG/SVG. No JavaScript build, no server; open the
   files in a browser.

Decision: option 3. Matplotlib becomes the first real dependency, isolated in
the `[analysis]` extra (D-009), which Phase 4 needs regardless.

Considerations: the dashboard's actual job in this project is (a) sanity-check
runs during data collection and (b) show the supervisor progress. Static
generation serves both, is testable (assert files exist and contain expected
strings), and produces committable artifacts. Interactivity has no identified
user.

Consequences: Slice 2J implements it; `report` fails with a helpful message
if matplotlib is missing; notebooks remain available for exploration but are
never the source of report figures (see Phase 4 plan).

Revisit when: a real interactive need appears (e.g., live monitoring of long
sweeps in Phase 3) - and then prefer extending the generator before adopting
a server.

---

## D-007: YAML config input is deferred

- Date: 2026-06-09
- Status: accepted
- Phase: 2+

Context: the CLI is JSON-only; one doc claimed YAML preference. Related to,
but distinct from, D-001 (bundle artifact format).

Options considered:

1. Add PyYAML now. Con: first core dependency, motivated by zero observed
   pain; example configs are short.
2. Defer: JSON-only input until a human actually authors enough configs for
   YAML comments/anchors to matter; then add PyYAML behind a `[yaml]` extra
   with YAML accepted at the CLI boundary only (immediately normalized to the
   JSON-backed schema).

Decision: option 2.

Considerations: Phase 2-3 configs will mostly be generated (sweeps), not
hand-authored. The cost of adding YAML later is one loader function; the cost
of adding it now is a permanent dependency and a second on-disk dialect to
test.

Consequences: CLI error message keeps stating the position ("YAML planned");
docs stop calling YAML "preferred".

Revisit when: the Phase 3 experiment matrix produces hand-edited config
sprawl that JSON makes painful.

---

## D-008: Split runs arrive via schema v0.2 (`run_kind` + `split_plan`)

- Date: 2026-06-09
- Status: accepted (design), implementation in Phase 3 Stage 3.1
- Phase: 3

Context: `BenchmarkConfig` v0.1 has exactly one `hardware_target`, so a
disaggregated run (prefill node + decode node + interconnect) is currently
inexpressible. Discovering this mid-Phase-3 would force a rushed schema
change after data collection had started.

Options considered:

1. Generalize `hardware_target` to a list of targets with role tags. Pro:
   maximally general (N-way splits someday). Con: validation becomes
   conditional on role combinations; every consumer must handle lists; we
   have no N>2 use case.
2. Add optional `run_kind: monolithic | transfer_bench | split_offline |
   split_live` (default `monolithic`) plus an optional `split_plan` object
   with named roles: `prefill_target`, `decode_target` (full HardwareTarget
   objects), and a `transfer` block (method: `file_scp` | `tcp_stream`,
   staging dir, link label). `transfer_bench` runs get a `transfer_bench`
   block (payload sizes, port) and reuse the two-target shape. Validation
   rules are explicit per run_kind (e.g., `hardware_target` required for
   monolithic, forbidden when `split_plan` present).
3. Separate config schema/file type for split runs. Con: two schemas to
   version, validate, and document; shared fields drift.

Decision: option 2, as schema_version 0.2, designed and implemented at the
start of Phase 3 (Stage 3.1) before any split data is collected. v0.1
configs remain valid: absent `run_kind` means `monolithic`.

Considerations: named roles match the experiment's fixed two-stage structure
and keep validation rules enumerable and testable. Backward compatibility by
defaulting preserves all Phase 2 configs and bundles. Designing now but
implementing at Phase 3 start avoids speculative code while eliminating the
mid-phase surprise.

Consequences: phase labels gain `deserialize`; the composite bundle layout
(nodes/prefill, nodes/decode) accompanies it; reducers learn per-stage
decomposition. All documented in the Phase 3 plan.

Revisit when: an N>2 pipeline experiment is actually proposed.

---

## D-009: Dependency policy: stdlib core, optional extras

- Date: 2026-06-09
- Status: accepted
- Phase: all

Context: the repo is zero-dependency by design ("Phase 1 can run without
dependency installation"). Phases 2-4 need MLX (Mac runtime), matplotlib
(reports/figures), and likely pandas (aggregation).

Options considered:

1. Add dependencies to core as needed. Con: `python3 -m joulewise run` on a
   bare machine stops working; CI and the mock path inherit heavy installs;
   the Phase 5 "new user runs one local benchmark from the README" promise
   gets harder.
2. Keep core stdlib-only forever. Con: re-implementing plotting/dataframes is
   absurd.
3. Stdlib-only core (schemas, controller, mock adapters, bundle writer,
   reducer v1, CLI), with extras: `[mac]` = mlx, mlx-lm; `[analysis]` =
   matplotlib (+ pandas when Phase 4 lands); `[yaml]` = pyyaml (when D-007
   triggers). Adapters import their backend lazily and return structured
   `runtime_unavailable` / `telemetry_unavailable` failures when the extra
   is absent.

Decision: option 3.

Considerations: the mock vertical slice is the project's portability proof
and CI substrate; keeping it dependency-free keeps it fast and unbreakable.
Lazy imports turn missing extras into the structured failures the contract
already requires, which doubles as a test of the failure paths.

Consequences: `pyproject.toml` gains `[project.optional-dependencies]`; CI
(D-017) installs nothing; docs state which extra each command needs.

Revisit when: a stdlib-only requirement becomes the bottleneck for core
correctness (not convenience).

---

## D-010: Run ID scheme

- Date: 2026-06-09
- Status: accepted
- Phase: 2+

Context: bundle directories need unique, sortable, informative names. The
config has an optional `run_id` field.

Options considered:

1. UUID4. Pro: unique. Con: opaque; directory listings become unreadable;
   sorting is meaningless.
2. Monotonic counter. Con: requires global state; collides across machines.
3. `<UTC timestamp>__<target_id>__<workload_name>__<4 hex chars>`, e.g.
   `20260610T142233Z__macbook_m3_max__smoke_short__a1b2`. Components
   sanitized to `[a-z0-9_-]`. If the config supplies `run_id`, it is used
   verbatim after sanitization, with a collision check that fails the run
   rather than overwriting (bundles are immutable evidence). Repetition
   members append `__r<N>` (D-005).

Decision: option 3.

Considerations: timestamp prefix makes `ls runs/` chronological; embedded
target/workload makes manual triage possible without opening files; the hex
suffix prevents same-second collisions; refusing to overwrite enforces the
"bundles are evidence" rule mechanically.

Consequences: bundle writer owns ID generation and sanitization; tests cover
collision behavior.

Revisit when: never expected.

---

## D-011: `summary_metrics.json` is the bundle completion marker

- Date: 2026-06-09
- Status: accepted
- Phase: 2+

Context: a crashed or killed run must be distinguishable from a completed one
by artifact inspection alone.

Options considered:

1. Write into `runs/<id>.partial/` and rename on completion. Pro: atomic.
   Con: a crash leaves `.partial` dirs whose artifacts (events up to the
   crash) are exactly what you want to inspect, but tooling now needs to know
   two names; rename breaks any open file handles on some platforms.
2. A `_COMPLETE` sentinel file. Pro: explicit. Con: one more artifact that
   says nothing else.
3. Define the writing order so `summary_metrics.json` is always written last,
   after all other artifacts are flushed, and define "complete bundle" as
   "directory containing a schema-valid `summary_metrics.json`". The final
   event in `events.jsonl` is `run_finalized`.

Decision: option 3.

Considerations: the summary is already mandatory and already last in data-flow
order (it is derived from everything else), so the invariant costs nothing.
`validate-bundle` (Slice 2E) checks it; aggregation (Phase 4) skips
directories without it and logs them as incomplete. Failed runs still get a
summary (status=failed) per D-012, so "incomplete" specifically means
"harness died", which is the signal we want.

Consequences: bundle writer enforces write order; reducers never run on
incomplete bundles.

Revisit when: never expected.

---

## D-012: Failure-reason to run-status mapping

- Date: 2026-06-09
- Status: accepted
- Phase: 2+

Context: `RunStatus` has `succeeded | failed | unsupported` and
`FailureReason` has eight codes, but nothing defined which reasons produce
which status. The distinction matters: `unsupported` is a *finding* the
capstone reports (hardware applicability results); `failed` is a *defect or
environment problem* to fix.

Options considered:

1. Let each adapter pick the status. Con: inconsistent semantics across
   backends; the same condition becomes a finding on one target and a bug on
   another.
2. A fixed mapping table owned by the controller:
   - `unsupported`: `did_not_fit`, `format_unavailable`,
     `unsupported_workload`, `runtime_unavailable`, `telemetry_unavailable`
     (structural incompatibility of the hardware/runtime/model/workload
     combination).
   - `failed`: `permission_denied`, `transport_unavailable`, `unknown_error`
     (operational problems that a configuration or environment change should
     fix).

Decision: option 2.

Considerations: the dividing principle is "would we publish this outcome as a
result?" A model that does not fit in 8 GB VRAM is a result; a missing
sudoers line is not. `permission_denied` is deliberately `failed` because it
is always fixable per D-004. `runtime_unavailable` is deliberately
`unsupported` because by D-009 it means "this target composition lacks this
backend", which is an applicability statement; if it occurs because an extra
simply was not installed on a machine that supports it, the run report should
say so and the run be repeated - the controller cannot distinguish these, so
the human/agent in the loop must.

Consequences: controller implements the table; tests pin it; the known
ambiguity on `runtime_unavailable` is documented in the Phase 2 plan and
flagged in run reports when it occurs.

Revisit when: a reason code appears that the table misclassifies in practice;
amend the table and this entry rather than special-casing in adapters.

---

## D-013: Controller-as-DUT mitigation for Mac-local runs

- Date: 2026-06-09
- Status: accepted
- Phase: 2

Context: in the Mac vertical slice the controller process runs on the same
machine that `powermetrics` measures. Controller activity during the measured
window pollutes the power trace; this is a measurement-validity threat no
checklist previously named.

Options considered:

1. Ignore it. Con: silently biases the flagship measurements.
2. Run the controller from a second machine over SSH even for the Mac. Pro:
   clean separation. Con: requires the SSH transport before the first real
   vertical slice, inverting the planned order; the Mac is the only always
   available device.
3. Co-residency protocol: (a) idle baseline is measured with the controller
   resident and quiescent, so the controller's floor load is inside the
   baseline that gets subtracted; (b) during the measured window the
   controller does nothing but a blocking wait on the runtime (no logging, no
   polling - log records are buffered in memory and flushed after
   `stop_sampling`); (c) the runtime adapter for local runs executes in the
   same process by design, so its cost *is* the workload; (d) document
   residual risk: controller wake-ups are zero by construction, and any OS
   background activity affects idle and load windows alike.

Decision: option 3 for Phase 2, with option 2 recorded as the upgrade path
once the SSH transport exists (re-run a subset and compare).

Considerations: idle subtraction already exists in the methodology; making
the controller part of the measured system's *idle* state is the cheapest way
to cancel its first-order effect. Deferred logging is essential - a single
log line during a 1 Hz window is a visible artifact.

Consequences: controller gains an explicit quiescent-wait mode and deferred
log flush; methodology doc gains a Controller Co-Residency section; the
comparison run is queued as a Phase 3-era validation task.

Revisit when: the SSH-based comparison shows a measurable delta, in which
case Mac headline numbers move to remote-controlled runs.

---

## D-014: Statistical protocol for repeated runs

- Date: 2026-06-09
- Status: accepted (draft to be ratified against real variance data at Phase 4
  Stage 4.0)
- Phase: 2 (collection), 4 (analysis)

Context: acceptance criteria say "repeated runs report variance" and
"uncertainty intervals" with no method defined. Choosing after seeing data
invites motivated choices; choosing now and ratifying with documented
reasoning is auditable.

Options considered (per element):

- Repetitions: n=3 (cheap, wide CIs) vs n=5 (headline-defensible, ~2.8x t
  multiplier instead of ~4.3x at 95%) vs n>=10 (hardware time we may not
  have). Chosen: n>=5 for headline comparisons, n>=3 minimum elsewhere,
  recorded per experiment.
- Interval: normal z (wrong at small n) vs Student t (standard at small n,
  assumes rough normality) vs bootstrap percentile (assumption-light but
  unstable at n=5). Chosen: report mean, sample stddev, and 95% t-interval;
  run a bootstrap sensitivity check in Phase 4 and report both where they
  disagree materially.
- Outliers: silent removal (never), keep-all (can bury a real artifact), flag
  via modified z-score on MAD > 3.5 and *report with and without, with the
  physical cause investigated and documented*. Chosen: the latter; a flagged
  point with no identified cause is kept in headline numbers.
- Ordering: condition blocks (thermal drift confounds with condition) vs
  round-robin interleaving (decorrelates slow drift; more model reloads).
  Chosen: round-robin across conditions where reload cost permits, with the
  executed order recorded in the experiment manifest; where blocks are
  operationally forced, that is recorded too.
- Thermal equilibrium between reps: fixed sleep (blind) vs temperature
  threshold (sensor availability varies by target) vs idle-power recovery
  gate. Chosen: idle-power recovery - wait until a rolling 30 s idle-power
  mean returns to within 10% of the run's recorded idle baseline, with a
  5-minute cap (cap hit => recorded in measurement quality).

Decision: as chosen above; figures always show raw points alongside
aggregates.

Considerations: every element was picked to survive a hostile question in a
capstone defense: "why n=5", "why t", "did you drop points", "did thermal
state drift". The idle-power gate was chosen over temperature because it uses
the instrument we always have (the power meter itself) and directly measures
the quantity whose drift would bias us.

Consequences: methodology doc gains the Statistical Protocol section;
controller implements the cooldown gate (Slice 2F); Phase 4 Stage 4.0
ratifies or amends with observed variance, updating this entry's status.

Revisit when: Phase 4 Stage 4.0, mandatorily.

---

## D-015: Split-mechanism priority and same-runtime rule

- Date: 2026-06-09
- Status: accepted
- Phase: 3

Context: the headline experiment splits prefill and decode across machines,
which requires moving KV-cache state. KV tensors are runtime-specific
(layout, dtype, quantization, RoPE handling), and not every runtime can
export or import them. This is the project's largest feasibility risk
(R-004, R-005).

Options considered:

1. Live KV streaming between runtimes first (Splitwise-style). Pro: closest
   to the inspiration paper. Con: hardest variant of the riskiest component;
   no public stable path in vLLM, none at all across heterogeneous runtimes;
   a failure here late in the schedule sinks the phase.
2. Cross-runtime transfer via a translation layer (e.g., vLLM prefill ->
   MLX decode). Con: deep model-internals work, research-grade in itself,
   out of scope for a measurement capstone.
3. Feasibility-ordered ladder with a guaranteed floor:
   a. *Synthetic transfer microbenchmark* (always feasible): move
      KV-sized payloads between nodes with both-end power sampling. Yields
      transfer energy/time vs payload size vs link speed regardless of any
      runtime's cooperation.
   b. *Offline replay* (primary mechanism): same runtime family on both
      ends; prefill on node A, persist the prompt cache to a file, transfer
      it, resume decode from it on node B. Candidate paths: mlx-lm prompt
      cache save/load; llama.cpp `--prompt-cache` session files; vLLM
      expected unsupported for file replay (spike confirms).
   c. *Live split* (stretch): socket streaming during a run, only attempted
      after (b) produces publishable data.
   Rule: same runtime (and pinned version) on both ends of any real KV
   transfer; cross-runtime KV portability is explicitly out of scope, and
   heterogeneous *hardware* pairs are achieved with a portable runtime
   (llama.cpp) where its backends allow.

Decision: option 3.

Considerations: the ladder converts an existential risk into a bounded one:
even if every runtime spike fails, (a) plus Phase 2 homogeneous baselines
still supports an analytical split-energy model (prefill energy measured on
A, decode energy measured on B via replay-or-monolithic decomposition,
transfer energy measured synthetically), which is an honest, defensible
capstone result. Each rung up improves directness of measurement. The
same-runtime rule eliminates the one problem (tensor portability across
engines) that no amount of harness engineering can fix on schedule.
Open question carried into the spikes: llama.cpp session-file portability
across *backends/platforms* (CUDA-save -> Metal-load) is unverified and gets
its own spike with an explicit verdict.

Consequences: Phase 3 plan is structured around the ladder (Stage 3.0
spikes before any hardware scheduling); the KV-size analytical model feeds
payload sizes for (a); verdict codes per runtime are recorded in
`docs/phase_3/kv_feasibility.md`.

Revisit when: a spike contradicts an assumption (then the ladder re-ranks,
documented), or vLLM's disaggregation API stabilizes early enough to matter.

---

## D-016: Benchmark model selection

- Date: 2026-06-09
- Status: open (criteria fixed now; closure requires Phase 1 supervisor scope
  plus Phase 2 install evidence)
- Phase: 2+

Context: every cross-target comparison needs identical model(s). The example
config's `qwen-placeholder` must become a real decision before Slice 2G.

Selection criteria (fixed now):

1. Must run on all primary targets: MLX-format weights available (or
   convertible) for Mac; GGUF available for llama.cpp paths; vLLM-loadable
   for the CUDA path.
2. Must fit the smallest VRAM targets at the chosen quantization: 8 GB
   (RTX 3050, Orin Nano) with headroom for KV at experiment prompt lengths.
3. KV-per-token small enough that transfer payloads span an interesting
   range (see Phase 3 KV table) but large enough to exercise the
   interconnect.
4. Open weights with a license permitting academic benchmarking and local
   mirroring (R-014: mirror weights locally once chosen).
5. Prefer one small + one mid model from the same family to separate
   model-size effects from family effects.

Candidate set (to be narrowed with evidence): Qwen2.5-1.5B-Instruct,
Qwen2.5-7B-Instruct, Llama-3.2-1B-Instruct, Llama-3.2-3B-Instruct,
Llama-3.1-8B-Instruct.

Options considered (shape of the decision): single model (cleanest matrix,
no size axis) vs small+mid pair (size axis, double hardware time) vs per-
target best model (incomparable - rejected outright).

Decision pending; leaning small+mid pair from one family, final call
recorded here with per-runtime artifact paths and exact revisions when
closed.

Closure evidence required: supervisor scope notes (P1-001); successful load
on Mac MLX (Slice 2G) and one CUDA target; recorded weight artifact
paths/revisions; KV-size table row computed for the chosen models.

Revisit when: a chosen model's weights become unavailable or a target cannot
load it (then the recorded fallback candidate is promoted).

---

## D-017: CI scope

- Date: 2026-06-09
- Status: accepted
- Phase: all

Context: the GitHub remote has no CI; agents benefit from remote green-check
evidence, and Phase 5 promises a reproducible mock path.

Options considered:

1. No CI. Con: "tests pass" claims rest on local runs in handoff notes.
2. Full matrix with extras (mlx cannot install on Linux runners; GPU absent).
   Con: impossible or meaningless for hardware paths.
3. Core-only CI: ubuntu runner, Python 3.11 and 3.14 (oldest supported per
   `pyproject.toml`, plus the version observed in local development),
   `python -m unittest discover -s tests` plus CLI smoke
   (`validate-config` on both example configs). Later phases extend it with
   the mock-bundle end-to-end run and `validate-bundle` once those exist.

Decision: option 3.

Considerations: the stdlib-only core (D-009) is exactly the testable surface
on a hosted runner; hardware adapters are validated by run bundles, not CI.
Two Python versions catch the realistic compat risks (3.11 floor vs 3.14
local) at trivial cost.

Consequences: `.github/workflows/ci.yml` added; Phase 2 Slice 2E adds the
mock end-to-end step to it; README badges optional, not required.

Revisit when: a self-hosted runner with GPU/Mac hardware ever materializes
(unlikely; not planned).

---

## D-018: Per-backend `power_w` definition and rail policy

- Date: 2026-06-09
- Status: accepted
- Phase: 2+

Context: `power_trace.csv` has `power_w`, `source`, and optional `rail`
columns, but "power" means different physical boundaries on different
backends (SoC subsystems vs GPU board vs module input vs wall AC). Without a
fixed definition, cross-target comparisons silently compare different
quantities.

Options considered:

1. One `power_w` row per sample, backend decides what it means. Con: loses
   per-rail information; the meaning varies invisibly.
2. Per-rail rows only, reducers sum everything. Con: "everything" differs by
   backend; accidental double counting (e.g., a backend reporting both
   package and per-subsystem rails).
3. Per-rail rows preserved as reported, plus a per-backend *rail manifest*
   that names exactly which rails sum to the backend's canonical `power_w`
   for reduction, and a methodology table stating each backend's physical
   measurement boundary. powermetrics: cpu_power + gpu_power + ane_power
   (SoC subsystem proxy; excludes display, storage, PSU losses). nvidia-smi:
   board power as reported (GPU board only; excludes host). jetson_rails:
   VDD_IN preferred (module input) with the actually-used rail recorded.
   wall_meter: AC wall power (full system).

Decision: option 3.

Considerations: per-rail rows keep raw fidelity (Apple's per-subsystem split
is itself interesting data); the manifest makes the summation auditable and
fixable post hoc; the boundary table converts an implicit comparability
problem into an explicit, reportable limitation - cross-target absolute
comparisons must state boundaries, and wall-meter deltas (when the meter
exists, P1-003) calibrate the gap.

Consequences: telemetry adapters declare their rail manifest in
`device_metadata`; reducer sums per the manifest; methodology gains the
Measurement Boundaries section; the limitations section of the final report
inherits the boundary table.

Revisit when: a backend exposes a strictly better boundary (e.g., macOS adds
package-level wall-equivalent reporting).

---

## D-019: Mock adapters use simulated time via an injectable clock

- Date: 2026-06-09
- Status: accepted
- Phase: 2

Context: reducer correctness tests need traces and events whose expected
energy is computable in closed form; the controller needs real time for real
runs. If mocks sleep through real seconds, tests get slow and flaky; if the
controller special-cases mocks, the lifecycle under test diverges from the
real one.

Options considered:

1. Mocks sleep in real time. Con: a 30 s idle window makes the test suite
   unusable; timestamp jitter breaks exact assertions.
2. Controller branches on mock backends. Con: the code path being tested is
   no longer the production path.
3. A minimal `Clock` protocol (`now() -> float`, `sleep(seconds)`) injected
   into the controller; `SystemClock` for real runs, `FakeClock` that
   advances instantly for tests and mock runs. Mock adapters compute
   deterministic timestamps/samples from the config and the injected clock;
   the controller code path is identical in both modes.

Decision: option 3.

Considerations: this is the standard seam for time-dependent systems; it
keeps the mock vertical slice fast (CI, D-017), exact (reducer tests assert
energy to the float), and honest (same controller code). The mock telemetry
trace is specified in Slice 2B as piecewise-constant power levels per
lifecycle stage so trapezoidal integration has a closed-form expectation.

Consequences: controller and adapters take a clock parameter; no module ever
calls `time.time()`/`time.sleep()` directly except `SystemClock`.

Revisit when: never expected.

---

## D-020: CLI binds `FakeClock` for all-mock runs, `SystemClock` otherwise

- Date: 2026-06-12
- Status: accepted
- Phase: 2

Context: D-019 created the clock seam but left open which clock the
`run` verb binds. With `SystemClock`, a mock end-to-end run sleeps
through real idle/warmup seconds and produces nondeterministic
timestamps; the mock path's whole value (fast CI substrate, exact
closed-form expectations, byte-identical reruns) depends on simulated
time.

Options considered:

1. Always `SystemClock`. Pro: one rule. Con: mock e2e takes wall-clock
   seconds in CI for no measurement benefit; timestamps differ per run,
   so determinism can only be asserted in unit tests, never on real CLI
   artifacts.
2. An explicit `--fake-clock` flag. Pro: caller control. Con: the flag
   would be mandatory-in-practice for mock runs and dangerous-if-misused
   for real runs (simulated timestamps in a hardware bundle would corrupt
   evidence silently).
3. Selection by composition at the CLI boundary: `FakeClock` if and only
   if both `runtime_backend` and `telemetry_backend` are `mock`,
   `SystemClock` otherwise. The clock kind is recorded in
   `metadata.json` (`clock.kind`), so every bundle states which time base
   produced it.

Decision: option 3.

Considerations: this is not the controller-branches-on-mocks anti-pattern
D-019 rejected - the controller code path is identical; only the injected
dependency differs, chosen at the outermost boundary. Mixed compositions
(e.g. Slice 2G's real MLX runtime + mock telemetry) correctly get
`SystemClock`, because real workload execution needs real time even when
power is synthetic. Library callers of `run_benchmark` always pass their
own clock explicitly; the rule binds only the CLI default.

Consequences: `cli.py`'s `run` verb implements the rule with a comment
citing this entry; the CI mock end-to-end step is effectively instant;
`metadata.json` discloses the time base per bundle.

Revisit when: a mixed mock/real composition needs simulated time, or a
test needs to drive the CLI with a seeded clock (then add the explicit
flag from option 2 with a refuse-on-real-telemetry guard).

---

## D-021: Controller flushes `events.jsonl` before the reduce stage

- Date: 2026-06-12
- Status: accepted
- Phase: 2

Context: the controller buffers all events in memory and flushes them
only at `_finish()` (D-013 deferred logging keeps the measured window
quiescent). Slice 2D's reducer is a pure function over the on-disk bundle
artifacts (D-002), including `events.jsonl`, and the controller calls it
during the reduce stage - which originally ran *before* the buffered
events were written. The reducer would have read an empty `events.jsonl`
(no measured-run window, no token events). The 2C author flagged this for
2D.

Options considered:

1. Pass the in-memory events to the reducer directly. Con: breaks the
   D-002 contract that `reduce_bundle(path)` is pure over on-disk
   artifacts - the same function is reused by `validate-bundle` and the
   report generator, which only have the files; two code paths would
   diverge.
2. Flush `events.jsonl` once, before the reducer runs in the reduce
   stage, and have `_finish()` (the failure paths included) flush only if
   not already flushed. `finalize()` still appends `run_finalized` last
   and writes `summary_metrics.json` last (D-011 unchanged).

Decision: option 2. The flush is a delta flush keyed on a flushed-count,
not a strict one-shot: the reduce stage's own `stage_completed` event is
buffered *after* the in-reduce flush, so a strict one-shot would drop it
and break the event-sequence contract. Each `_flush_events` call appends
only events buffered since the previous flush, stable-sorted within the
batch; later batches are strictly later in time, so global order holds.

Considerations: this keeps the reducer honest (pure over files, so a
reducer bug is fixed by re-reducing the bundle, never by re-running
hardware) while preserving D-011 (summary still last) and D-013 (the
flush happens in the reduce stage, well after `stop_sampling`).

Consequences: `events.jsonl` exists and is complete (minus the trailing
`run_finalized`) at reduce time; failure paths, which never reach reduce,
still flush their buffered events exactly once in `_finish()`.

Revisit when: events grow large enough that buffering the whole run in
memory is a problem (then stream to a temp file and swap on finalize).

---

## D-022: Auto-generated run-ID suffix is config-hash-derived, not random

- Date: 2026-06-12
- Status: accepted (refines D-010)
- Phase: 2

Context: D-010 specified the auto-generated run ID as
`<ts>__<target>__<workload>__<4 hex>` with the 4-hex suffix from
`secrets.token_hex(2)` to prevent same-second collisions. A random suffix
makes the run ID - which is embedded in the `run_started` event and in
`metadata.json` - differ across otherwise-identical runs, violating the
Slice 2B acceptance criterion "identical config + clock seed =>
byte-identical events" for any valid config that omits `run_id` (the
adversarial review confirmed this empirically).

Options considered:

1. Keep `secrets.token_hex(2)`. Con: breaks the determinism criterion for
   the no-`run_id` case; the byte-identity guarantee then silently
   depends on the operator always supplying a `run_id`.
2. Drop the suffix entirely. Con: loses cross-config disambiguation when
   two different configs share a target/workload/second.
3. Derive the 4-hex suffix from the config's content hash (first 4 hex of
   the SHA-256 over the canonical config bytes, the same bytes that feed
   `config_sha256`). Deterministic per config; different configs get
   different suffixes; identical configs get identical IDs.

Decision: option 3. The suffix is `config_sha256[:4]`.

Considerations: this satisfies the determinism criterion (identical
config + clock => byte-identical run ID, events, and metadata) while
keeping cross-config disambiguation. The residual collision case -
identical config, same UTC second, same runs dir - now produces the same
ID and is refused by the immutable-evidence rule (D-010: never overwrite
a bundle), which is the correct response to "you are about to write a
second bundle for the identical config in the same second". Repetitions
never collide: the experiment runner assigns distinct `__rN` run IDs
(D-005/D-010), each a supplied `run_id` that bypasses the generated form.

Consequences: `generate_run_id` computes the suffix from the config hash;
`metadata.run_id` and the `run_started` event are now deterministic for a
fixed config; a run-benchmark-level determinism regression test pins it.

Revisit when: a use case genuinely needs two same-config same-second
bundles in one directory without the experiment runner (then reintroduce
a disambiguator, e.g. a monotonic counter rather than randomness, to keep
determinism).

---

## D-023: Per-item phase status lives solely in the exit checklists

- Date: 2026-07-05
- Status: accepted
- Phase: all

Context: project status was being recorded on six surfaces (phase plan
headers and per-step lines, exit checklists, `AGENT_PLAN.md` checkboxes,
`TASK_QUEUE.md`, `RUN_STATE.md`, `PROJECT_STATUS.md`). The 2026-07-05
planning audit found same-day drift from the 2026-06-12 run:
`phase_1_plan.md` still marked the Hailo verdict and readiness review
"open" after the checklist closed them, and `phase_2_plan.md`'s header
still read "planned" with 7 of 13 slices complete. The replication
exceeded one operator's update discipline on the project's busiest day,
which is exactly when drift is most misleading.

Options considered:

1. Keep all six surfaces and try harder. Con: already failed empirically;
   discipline does not scale with excitement or fatigue.
2. Exit checklists become the single per-item status authority; phase
   plan files carry no status (header points at the checklist; per-step
   status lines removed); `AGENT_PLAN.md` keeps a coarse checkbox mirror
   updated at slice/phase closes; `TASK_QUEUE.md`/`RUN_STATE.md` remain
   work-selection and handoff views (different content, not duplicated
   status); `PROJECT_STATUS.md` remains the derived advisor summary.
3. Generate a status dashboard from one machine-readable source. Con:
   tooling investment the project does not need yet; a script is its own
   maintenance surface.

Decision: option 2. The evidence matrix in
`docs/phase_N/phase_N_exit_checklist.md` is the only place a per-item
status is asserted; every other document either points there or mirrors
coarsely and says so.

Considerations: plans stay useful as timeless specs (objectives, gates,
design, acceptance) that do not rot when work completes; the checklist
was already the evidence dossier, so status naturally colocates with the
evidence that justifies it; the coarse `AGENT_PLAN.md` mirror is retained
because it is the cross-phase index agents read first, and its checkbox
grain (one line per slice) is cheap to keep honest. The same audit drove
a companion dedup: `phase_2_plan.md` owns each gated slice's
what/when/done while the hardware guide owns the how, replacing the
previous near-verbatim duplication.

Consequences: all five plan headers now read "Status: tracked in the
exit checklist"; `phase_1_plan.md` per-step status lines removed; the
source-of-truth map in `AGENT_PLAN.md` updated to name the checklists as
status authority; plan/guide duplication for slices 2G-2M cut to
pointers.

Revisit when: the `AGENT_PLAN.md` coarse mirror is found drifted again -
then replace the mirror with a generated table (option 3) rather than
adding discipline.
