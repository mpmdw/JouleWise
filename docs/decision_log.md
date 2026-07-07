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
| D-016 | Benchmark model selection | open (provisional small-model pick 2026-07-06; opens 2G only) |
| D-017 | CI scope | accepted |
| D-018 | Per-backend `power_w` definition and rail policy | accepted |
| D-019 | Mock adapters use simulated time via an injectable clock | accepted |
| D-020 | CLI binds `FakeClock` for all-mock runs, `SystemClock` otherwise | accepted |
| D-021 | Controller flushes `events.jsonl` before the reduce stage | accepted |
| D-022 | Auto-generated run-ID suffix is config-hash-derived, not random | accepted |
| D-023 | Per-item phase status lives solely in the exit checklists | accepted |
| D-024 | Adapters receive a `RunContext`, not piecemeal parameters | accepted; implemented (2N.1, 2026-07-06) |
| D-025 | One shared bundle read layer for reducer, report, validation, and aggregation | accepted; implemented (2N.8, 2026-07-06) |
| D-026 | Measured window is bounded by sampling-active marker events | accepted |
| D-027 | Per-rail rows must share per-sample timestamps; misalignment is a structured failure | accepted |
| D-028 | `reduce` verb rewrites `summary_metrics.json` in place (the one sanctioned post-finalize mutation) | accepted |
| D-029 | Config schema declares nullable optionals; serialization (and config hashes) unchanged | accepted |
| D-030 | `validate-bundle` stays structural by default; `--strict` adds re-reduction checks for succeeded bundles | accepted |
| D-031 | Multi-model council review; PR convention for multi-commit sessions; D-023 extension + end-of-session consistency sweep | accepted |

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

**Provisional pick recorded (2026-07-06, user-directed build-out session;
gate = explicit user go-ahead, recorded in the run report):**
Qwen2.5-1.5B-Instruct as the small model, MLX 4-bit artifact
`mlx-community/Qwen2.5-1.5B-Instruct-4bit`, revision
`8b403126fc14f14cfc99bb4cfa72ecbc129ea677`, mirrored locally (R-014) at
`/Users/edr/jw_models/mlx-community/Qwen2.5-1.5B-Instruct-4bit` (839 MB).
Evidence: HF repo verified via API 2026-07-06; loaded and generated on
the M3 Max via Slice 2G (bundle `example-mac-mlx-mock-telemetry`,
265.8 tok/s decode); KV row verified against the mirrored config.json
(28,672 B/token fp16, matches the Phase 3 table). This opens the 2G gate
("closed or provisional") ONLY. Full closure still requires: P1-001
supervisor scope, the mid-model pick (leaning Qwen2.5-7B-Instruct, same
family per criterion 5), a CUDA-target load, and GGUF artifact paths.
The provisional pick is reversible at config level (one model stanza +
pinned hash update).

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

---

## D-024: Adapters receive a `RunContext`, not piecemeal parameters

- Date: 2026-07-06
- Status: accepted; implemented in Slice 2N.1 (2026-07-06)
- Phase: 2

Context: mock adapters get by on `config` (plus `clock` at construction),
but real adapters need more: a place to write raw telemetry evidence
(D-002; powermetrics plist), log/output paths, the run ID, and - in
Phase 3 - the node's role in a split run. Slice 2N.1 originally left the
delivery mechanism open (new parameter vs writer injection vs context
object). An external architecture review (Codex, 2026-07-06) recommended
deciding now, before any real adapter is written against a narrower
seam.

Options considered:

1. Add parameters piecemeal as needs appear (e.g.
   `start_sampling(raw_dir=...)`). Con: every future need is another
   signature break across all adapters and their tests; Phase 3 alone
   would force two more rounds.
2. Inject the `RunBundleWriter` into adapters. Con: hands adapters the
   power to write summaries/finalize - far more authority than they
   need; couples every adapter to the writer's full API.
3. A small immutable `RunContext` dataclass passed to adapter lifecycle
   methods: `config`, `clock`, `run_id`, `bundle_path`, `raw_dir`,
   `logs_dir`, `outputs_dir`, and optional `node_role` (None for
   single-node runs; used by Phase 3 split orchestration).

Decision: option 3. One additive seam that covers the known Phase 2
needs (raw evidence, logs) and the foreseen Phase 3 needs (node role,
composite bundles) without granting adapters bundle-lifecycle authority.

Considerations: the context is data, not capability - adapters get paths
and identity, not the writer; write-order/immutability invariants stay
with the controller and writer. `node_role` rides along as an optional
field now precisely so the v0.2 compatibility check (2N.9) can exercise
it without any schema change (R-015 intact). Mocks accept the context
and ignore what they do not need, keeping one lifecycle code path.

Consequences: `interfaces.py` adapter protocols take a context in their
lifecycle methods (exact placement pinned during 2N.1);
`adapter_contracts.md` updated in the same run; the controller
constructs the context after bundle creation.

Revisit when: a need appears that is per-call rather than per-run (then
a per-call argument is correct, not a context field), or Phase 3's
composite-bundle design (D-008) demands fields that would make the
context mutable - mutability is the line not to cross.

Amendment (2026-07-06, 2N.1 implementation): placement is pinned as a
trailing optional per-method parameter (`context: RunContext | None =
None`) on every adapter lifecycle method, not construction-time
injection. Rationale: the D-014 cooldown gate invokes `measure_idle`
between repetitions when no bundle is open, and direct adapter tests
call methods outside any run; optionality keeps one lifecycle code path
while the controller always supplies the context. Adapters must produce
no raw output when the context is absent. The writer-side counterpart is
`RunBundleWriter.raw_path`/`write_raw` (validated plain file names,
collision-checked, closed by `finalize()`); adapters never receive the
writer - they write into `context.raw_dir` directly.

---

## D-025: One shared bundle read layer for all bundle consumers

- Date: 2026-07-06
- Status: accepted; implemented in Slice 2N.8 (2026-07-06, `joulewise/bundle_read.py`)
- Phase: 2

Context: three code paths already parse bundles independently -
`reduce.py` (trace/events/manifest for metrics), `report.py` (the same
for charts), and `cli.py` `validate-bundle` (structural checks) - and
they have already diverged once: the report sums all rails when the
manifest matches nothing while the reducer excludes/fails (2N.7
finding). Phase 4's `aggregate` verb would be a fourth parser. An
external architecture review (2026-07-06) recommended a shared read
layer before the divergence class grows.

Options considered:

1. Keep per-consumer parsing, fix mismatches as found. Con: the 2N.7
   bug recurs in new forms; every policy (rail manifest, measured
   window, completeness) must be kept aligned by vigilance across four
   files.
2. A shared `BundleReader` (in `joulewise/bundle.py` or a new
   `bundle_read.py`): loads config, metadata, events, power trace, rail
   manifest, measured/phase windows, completion state, and structural
   problems - one implementation of every bundle-interpretation policy;
   consumers apply presentation/reduction on top.
3. Full ORM/database layer now. Con: heavyweight; Phase 4's CSV plan
   plus a possible stdlib-sqlite cache (Stage 4.1 note) already covers
   querying needs.

Decision: option 2. Reducer, report, `validate-bundle`, and (later)
`aggregate` all consume the shared reader; policy questions like "which
rails sum to `power_w`" are answered in exactly one place.

Considerations: this is the code-level analogue of D-023's one-fact-one-
home rule; the reducer's math (`_integrate`, idle subtraction) stays in
`reduce.py` - the reader owns parsing and policy, not metrics. The 2N.7
report/reducer alignment must be implemented BY building on the reader,
not as a spot fix, or the divergence just reappears at the next
consumer.

Consequences: Slice 2N gains item 2N.8; 2N.7 is implemented on top of
it; Phase 4 Stage 4.1's aggregate verb builds on the reader (noted in
the Phase 4 plan).

Revisit when: bundle schema v0.2 lands (the reader is where composite-
bundle reading concentrates), or a consumer needs streaming reads that
the whole-bundle reader cannot serve.

---

## D-026: Measured window is bounded by sampling-active marker events

- Date: 2026-07-06
- Status: accepted (Slice 2N.2)
- Phase: 2

Context: the reducer integrated energy between the `measured_run`
`stage_started` and `stage_completed` events. `stage_started` is stamped
before `thermal_state` and `start_sampling`, and `stage_completed` after
`stop_sampling`, `thermal_state`, and the outputs/trace writes - so under
`SystemClock`, real sampler spawn latency (sudo probe, process start,
first sample) and wind-down cost (process stop, plist parsing) land
inside the integrated window, inflating gross energy, the
idle-subtraction duration, and TTFT. `FakeClock` collapses these
intervals to zero, so the mock suite could never catch it.

Options considered:

1. Reorder the stage boundary: stamp `stage_started(measured_run)` only
   after `start_sampling` confirms. Con: a `start_sampling` failure would
   then be attributed to a stage that never started, breaking the event
   invariant that a failing stage has a `stage_started`; and the stage
   end would still include post-window artifact writes.
2. Explicit `sampling_started`/`sampling_stopped` marker events on the
   `measured_run` phase; the reducer integrates between markers, falling
   back to stage boundaries for pre-2N bundles.

Decision: option 2. `sampling_started` is stamped only after
`start_sampling` returns ok (sampling confirmed active);
`sampling_stopped` is stamped before `stop_sampling` is invoked (the
wind-down happens after the window closes). TTFT is measured from
`sampling_started`. The failure path's best-effort stop records the same
closing marker, so post-hoc re-reduction sees identical window semantics.

Considerations: stage boundaries keep their operational meaning (what the
controller was doing when) while the markers own the measurement
semantics - two facts, two event types. The two marker buffer-appends are
the only in-memory buffer touches inside the D-013 quiescent window
(negligible; nothing touches disk). The stop marker is appended to the
buffer after the runtime events so the stable flush-sort keeps it
bracketing them. Additive event types keep R-015 intact
(`validate-bundle` checks event keys, not a type whitelist).

Consequences: `_measured_window` in `joulewise/reduce.py` prefers the
markers and falls back to stage boundaries; telemetry adapters must not
return from `start_sampling` before sampling is actually running
(recorded in `adapter_contracts.md`); a latency-simulating telemetry test
pins the exclusion.

Revisit when: a real adapter cannot confirm sampling start
synchronously (would need an async readiness probe), or Phase 3 split
runs need per-node windows (D-008 composite bundles).

---

## D-027: Per-rail rows must share per-sample timestamps; misalignment is a structured failure

- Date: 2026-07-06
- Status: accepted (Slice 2N.4)
- Phase: 2

Context: `power(t)` sums `power_w` over the manifest rails grouped by
exact `timestamp_s` equality (D-018). A real multi-rail adapter (e.g.
Jetson rails) emitting per-rail rows with slightly skewed timestamps
would silently produce an interleaved per-rail curve whose integral
badly undersums the true power - a wrong number with no error, the worst
failure mode for a measurement harness. The grouping rule lived only in
a `bundle.py` comment.

Options considered:

1. Bucket timestamps within a tolerance derived from the sampling
   interval. Con: silently rewrites the data; the bucket width is a new
   free parameter; boundary cases (a sample near a bucket edge) move
   energy between samples invisibly.
2. Detect-and-fail: with a multi-rail manifest, every timestamp on the
   summed curve must carry exactly the full manifest rail set; a subset
   is a structured failure naming the timestamp and missing rail(s).

Decision: option 2. The contract is now explicit: a telemetry adapter
emits one row per rail per sample instant, all sharing that instant's
single timestamp (row fan-out per rail, one clock read per sample).
Adapters that sample rails at genuinely different instants must
resample/align before emitting rows - alignment policy belongs to the
adapter that knows its hardware, not to a generic bucketer.

Considerations: honesty over convenience - the project's core promise is
boundary-honest energy numbers, so a detectably wrong sum must fail
loudly (R-015 unaffected: no schema change). Single-rail manifests
cannot misalign; the check costs one set comparison per timestamp.
Enforcement lives in `BundleReader.summed_curve` (D-025), so the
reducer, report, and any future consumer inherit it identically.

Consequences: `adapter_contracts.md` telemetry section documents the
row contract; the reducer converts the reader's misalignment failure
into a structured FAILED summary; skewed/aligned twin fixtures pin both
sides.

Revisit when: a real telemetry backend cannot share one timestamp
across rails at source (then the adapter grows an explicit, tested
alignment step - still adapter-side, not reader-side).

---

## D-028: `reduce` verb rewrites `summary_metrics.json` in place

- Date: 2026-07-06
- Status: accepted (Slice 2N.6)
- Phase: 2

Context: D-002's promise - a reducer bug never re-runs hardware - needs
a user-facing path: `python3 -m joulewise reduce <bundle-dir>`
re-derives the summary from the raw artifacts. D-011 makes
`summary_metrics.json` the completion marker written last by
`finalize()`, and bundles are otherwise immutable evidence (D-010), so
where the re-derived summary lands is a real policy choice.

Options considered:

1. Rewrite `summary_metrics.json` in place. Pro: one summary, every
   consumer (validate-bundle, report, Phase 4 aggregate) keeps working
   unchanged; the summary is by definition derived from the raw
   artifacts, so rewriting it destroys no evidence.
2. Write a versioned name (`summary_metrics.v2.json`). Con: every
   consumer needs a resolution rule for which summary wins; the D-011
   completion marker becomes ambiguous; stale headline numbers linger in
   the canonical file.

Decision: option 1. In-place rewrite is the ONE sanctioned
post-finalize bundle mutation; everything else in a finalized bundle
stays immutable. The verb refuses paths without a `config.json` (exit
2, no write) so evidence is never invented inside an arbitrary
directory; degenerate bundle contents produce a structured FAILED
summary (exit 3); success exits 0 - matching `run`'s exit scheme, with
the same greppable `bundle:` result line.

Considerations: the raw artifacts (config, events, trace, raw/, logs)
remain the evidence of record; the summary is a cache of derivation.
If provenance of a re-reduction ever matters, the harness git commit is
already in `metadata.json` and the rewrite is reproducible from it.

Consequences: `reduce_bundle` returns structured failures for
missing/corrupt `config.json`/`metadata.json` (keeping its docstring's
"never crashes" promise); `run_bundle_layout.md`'s immutability language
gains this exception; CLI help documents the verb.

Revisit when: Phase 4 aggregation needs to distinguish "reduced by
which harness version" across a corpus (then a provenance field inside
the summary - additive, R-015 - beats a versioned file).

---

## D-029: Config schema declares nullable optionals; serialization unchanged

- Date: 2026-07-06
- Status: accepted (Slice 2N.5)
- Phase: 2

Context: `BenchmarkConfig.to_dict()` (dataclass `asdict`) emits `null`
for absent optionals, but the hand-written exported JSON Schema declared
those properties non-nullable - so a bundle's normalized `config.json`
failed external validation against `print-config-schema` output. The
harness's own `from_mapping` tolerated the nulls, hiding the mismatch
from every internal path.

Options considered:

1. Omit-None serialization: `to_dict()` drops null-valued keys. Pro:
   smaller, arguably cleaner artifact. Con: changes the config bytes and
   therefore every config SHA-256 - which is run identity (D-001 bundle
   hash, D-022 run-ID suffixes, D-005 experiment grouping). Acceptable
   only while no real bundles exist, and it buys nothing measurable.
2. Schema declares nullable optionals (`"type": ["string", "null"]`
   etc.), serialization untouched. Pro: hashes stable; an explicit
   `"field": null` and an absent field validate identically; the schema
   now tells external consumers the truth about emitted artifacts.

Decision: option 2 (also what the Phase 2 plan's 2N.5 text pins). Every
optional the emitter can produce as `null` is declared nullable;
numeric constraints (`minimum`) are unaffected by the null arm under
JSON Schema 2020-12.

Considerations: config-hash stability is worth protecting even
pre-hardware - the mock e2e byte-determinism tests (D-022) already
depend on it. A pinned-hash test now guards the serialization: any
future change to `to_dict()` bytes fails loudly and must come back
through this log.

Consequences: `schemas.py` `json_schema()` updated; round-trip tests
assert (a) every null-emitted field is schema-nullable and every
emitted key is schema-known on bare Python, (b) full `jsonschema`
validation where that package happens to be installed (D-009: CI has no
extras), (c) pinned SHA-256 per example config.

Revisit when: schema v0.2 (D-008) - the v0.2 exporter must keep the
nullable-optionals rule; or if a downstream consumer requires
omit-None artifacts (then revisit WITH a hash-migration plan).

---

## D-030: `validate-bundle` stays structural by default; `--strict` adds re-reduction checks

- Date: 2026-07-06
- Status: accepted (from the 2026-07-06 project status review, finding P2)
- Phase: 2 (matters most at Phase 5 dataset publication)

Context: the independent status review demonstrated that the default
validator blesses succeeded bundles whose derived metrics no longer
follow from their raw evidence - an emptied rail manifest and a tampered
`energy_request_j` both validated clean. Structural checks alone cannot
gate a published dataset.

Options considered:

1. Broaden the default `validate-bundle` to include analysis checks.
   Con: the default is used in CI and on failed/unsupported/incomplete
   bundles, where a fresh reduction is not comparable (failure summaries
   are controller-written from partial evidence); a heavier default also
   makes the structural verb slower and noisier for its most common use.
2. A `--strict` opt-in mode: for `status=succeeded` bundles only, (a)
   the measured window must exist, (b) the summed curve must be
   reducer-consumable (>= 2 in-window samples for a nonzero window), and
   (c) `summary_metrics.json` must equal a fresh `reduce_bundle` of the
   raw artifacts (exact-key diff reported). Failed/unsupported bundles
   pass strict untouched.

Decision: option 2. Default semantics are unchanged; strict mode is the
gate for any "all bundles intended for analysis pass validation" claim -
Phase 5 dataset publication (Stage 5.2) and Phase 4 aggregation intake
should run `validate-bundle --strict`.

Considerations: the re-reduction comparison is exact (the reducer is
deterministic over on-disk artifacts, D-002, and JSON round-trips floats
exactly), so any drift - tampering, a reducer version change, partial
rewrites - surfaces as a named key diff. Strict mode lives in `cli.py`,
not the reader: it composes the reader with the reducer, and the reducer
already consumes the reader (D-025), so putting it in `bundle_read`
would create an import cycle.

Consequences: `validate_bundle(path, strict=False)` keeps its importable
signature; CLI gains `--strict`; the reviewer's two reproductions are
pinned as tests (manifest emptied, summary tampered); Phase 5 Stage 5.2
should adopt `--strict` for the published sample bundles.

Revisit when: bundle schema v0.2 lands (composite summaries need their
own strict semantics), or a reducer version bump makes historical
summaries legitimately differ from fresh reductions (then strict needs
a provenance-aware comparison, see D-028's revisit note).

---

## D-031: Multi-model council review, PR convention, and drift controls

- Date: 2026-07-07
- Status: accepted
- Phase: all (process)

Context: the user directed a standing multi-model workflow: Codex
(gpt-5.5) implements and reviews as a near-peer, Claude leads and
verifies on hardware, Opus subagents run fast parallel sweeps, and the
models review each other bidirectionally with discussion of important
findings. The first two councils (see `docs/council_log.md` C-001/C-002)
caught a real blocker in green-tested code and six files of bookkeeping
drift respectively.

Options considered:

1. Single-model implement-and-self-review. Con: C-001 proved a fully
   green suite hid a blocker only adversarial review found.
2. Review without discussion (findings applied verbatim). Con: C-001's
   best fix came from the implementer arguing design back; C-002's
   run_id finding was refined in discussion.
3. Bidirectional council with bounded discussion (adopted): implementer
   ↔ reviewer roles swap per session; confirmed findings get one or two
   discussion rounds; the lead decides and records dissents in the
   council log.

Decision, in three parts:

- **Council process**: as above; sessions recorded in
  `docs/council_log.md` (positions, votes, resolutions — not
  transcripts). The lead (Claude) is the only member that runs real
  hardware; sub-agent "tests green" is never sufficient for
  hardware-adjacent slices.
- **PR convention**: multi-commit sessions land on a feature branch with
  a PR to `main` (one reviewable GitHub diff + CI before merge; the user
  merges). Single-commit bookkeeping may still go straight to main.
- **Drift controls**: D-023 is extended — prose status summaries must
  carry an as-of date and defer to checklist matrix rows (no duplicated
  live gate lists) — and every session ends with a delegated
  docs-consistency sweep before the final bookkeeping commit
  (RUN_STATE end-of-work step 7). Higher-level docs (README,
  PROJECT_STATUS, playbook) are in the sweep's scope explicitly.

Revisit when: council overhead exceeds its catch rate (track via council
log outcomes), or the model roster changes.

Execution topology addendum (2026-07-07, user direction): when a session
has multiple independent workstreams, each stream runs in its own git
worktree on its own branch, owned by a dedicated orchestrator subagent
(Fable) that drives its own Codex thread — the bridge resolves the repo
root per-worktree, so parallel Codex sessions keep separate
`.codex-bridge/` state and `resume --last` pointers. The lead session
stays the integrator: it reviews each stream's diff, runs the council
loop per stream, and lands each as its own PR. Worktrees are skipped for
single-stream sessions (pure overhead). First planned use: the
2M / P2-008 / kv-size batch after the vertical-slice PR merges.

Flagship-model addendum (2026-07-07, user-directed): the user directed the
benchmark be run on "the top of the line model that can run on this
128 GB machine." Research council (web-verified) selected
`mlx-community/Qwen3.5-122B-A10B-4bit` (rev `e9c67b0`, 69.6 GB download,
~72-76 GB inference footprint, 122B MoE / 10B active, Feb 2026
generation; fits without wired-limit changes; expected ~40-45 tok/s on
M3 Max; runners-up gpt-oss-120b-MXFP4 and GLM-4.5-Air recorded in the
run report). This is a SECOND provisional model alongside the small
Qwen2.5-1.5B pick — it does not close D-016 (mid-model/CUDA/GGUF
criteria still open) but extends the provisional set at user direction;
mirrored per R-014.
