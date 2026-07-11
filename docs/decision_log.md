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
  evidence pending), `proposed` (recorded, awaiting Ed's ratification),
  `superseded by D-NNN`.
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
| D-030 | `validate-bundle` stays structural by default; `--strict` adds raw-evidence checks | accepted |
| D-031 | Multi-model council review; PR convention for multi-commit sessions (merge authority amended by C-010); D-023 extension + end-of-session consistency sweep | accepted |
| D-032 | `phase_energy_j` is gross-only in summary v0.1 | accepted |
| D-033 | Prompt-content provenance is recorded per run bundle | accepted |
| D-034 | Slice 2O owns the workload program after 2M and 3.0.1; implementation lane reopened by D-042 | accepted |
| D-035 | Replay claims require fresh-process (subprocess-per-stage) isolation | accepted |
| D-036 | Spike verdict codes derive from measured data, never hardcoded | accepted |
| D-037 | Claims ladder (L0-L4) binds reader-facing claim language from 2M onward | accepted |
| D-038 | Analysis plans bind L2/L3 claims to pre-registered comparison rows | accepted |
| D-039 | Workload program v2: substrate first, identification before scale; pre-Window-A allowlist superseded by D-041/D-042 | accepted |
| D-040 | Suite architecture v2: generic suite mechanism, bundle-level replication | accepted |
| D-041 | Benchmark interop via frozen-subset imports and marker-shim energy layer; interop lane remains post-2M + post-P2-010a | accepted |
| D-042 | D-034 implementation lane reopened; suite build may proceed pre-2M | accepted |
| D-043 | Supersession-closure discipline | accepted |
| D-044 | Suite config identity: omission-serialized ref + effective-manifest hash | accepted |
| D-045 | Suite substrate execution semantics (run_suite, statuses, per-item outputs) | accepted |
| D-046 | AP-6 sentinel delivery is ids-native BOS-less at literal equal shape | accepted |
| D-047 | Affine ladder pins: level set, smoke sizing, gate denominators | accepted |
| D-048 | Split program is model-first: pre-registered compositional prediction before split runs | accepted |
| D-049 | Split transfer-energy boundary accounting on discrete-GPU ends | accepted |
| D-050 | Active stop cards and process-trace manifests | accepted |
| D-051 | Advisor status site uses source-derived static pages plus fail-soft live GitHub overlays | accepted |
| D-052 | Capstone scope contract: frozen umbrella headline and contribution ladder | accepted |
| D-053 | Contrast-level statistical inference and the frozen analysis registry | accepted |
| D-054 | False-effect guard floor and unknown-term claim-ceiling policy | accepted |
| D-055 | Research-question registry is the canonical live index | accepted |
| D-056 | Suite order policies and order_row provenance | accepted |
| D-057 | Uncertainty terms: drift is a bound; stable claim-gate reason codes | accepted |
| D-058 | Token-normalization and stack-identity contract adopted | accepted |
| D-059 | Claims-lint mechanical enforcement in CI | accepted |
| D-060 | Depth-before-breadth stop line | accepted (ratified 2026-07-10) |
| D-061 | Review-layer evaluation rule v2 | accepted |
| D-062 | Confirmatory sampling policy (fixed n, demotion) | accepted |
| D-063 | Process architecture v2 (state kernel first) | accepted |

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

Amendment (2026-07-07, P2-013 group 4, C-007 resolution 2): "schema-valid
`summary_metrics.json`" is now enforced by ONE shared summary validator
used by both `BundleReader.is_complete()` and default validation
(`_check_summary`), with required keys per status: a `succeeded` summary
must carry the headline energy fields present AND finite (audit finding
B1 showed a status-only succeeded summary previously counted as complete
and valid, hiding truncated metrics); token-derived and idle-subtracted
metrics stay nullable; failed/unsupported summaries keep their looser
per-status requirements. "Complete" therefore means "contains a summary
that satisfies the per-status contract", not merely "parseable JSON
object". Historical bundles are unaffected: real corpus summaries
already carry the full field set.

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
   AMENDED 2026-07-08 (PR #21, `255a7e6`): the quiescent window is
   MARKER-bounded, not call-bounded — the `sampling_stopped` timestamp is
   stamped immediately after the runtime returns, BEFORE adapter alignment
   capture and `stop_sampling` wind-down, so that controller/adapter
   bookkeeping is outside the reducer's measured window. Item (b)'s
   "until stop_sampling" phrasing predates this and reads call-bounded;
   the stamp is the boundary.

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

Amendment (2026-07-07, P2-013 group 4, C-007 resolution 4): the rail-set
rule is extended to DUPLICATES — at any timestamp on the summed curve,
each manifest rail must appear exactly once; a duplicate rail row at one
timestamp (including the single-rail case) is rejected rather than
summed, since silent double-counting is the same wrong-number failure
mode as undersumming (audit finding B5). Enforcement stays in the one
shared trace-validation path consumed by both `summed_curve()` and
default validation, so all consumers inherit it identically (D-025).

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

AMENDED 2026-07-08 (D-044): the nullable-emission rule gains one scoped
exception — NEW additive suite-only optionals (`suite_manifest_ref`,
`suite_manifest_sha256`) are serialized by OMISSION when None, so every
pre-suite config stays byte-identical and no hash migration occurs. All
pre-existing optionals keep null emission. See D-044.

---

## D-030: `validate-bundle` stays structural by default; `--strict` adds raw-evidence checks

- Date: 2026-07-06
- Status: accepted (from the 2026-07-06 project status review, finding P2)
- Phase: 2 (matters most at Phase 5 dataset publication)

Context: the independent status review demonstrated that the default
validator blesses succeeded bundles whose analysis artifacts no longer
follow from their source evidence - an emptied rail manifest, a tampered
`energy_request_j`, and an unverified powermetrics `power_trace.csv`
derivation all validated clean. Structural checks alone cannot gate a
published dataset.

Options considered:

1. Broaden the default `validate-bundle` to include analysis checks.
   Con: the default is used in CI and on failed/unsupported/incomplete
   bundles, where a fresh reduction is not comparable (failure summaries
   are controller-written from partial evidence); a heavier default also
   makes the structural verb slower and noisier for its most common use.
2. A `--strict` opt-in mode: for `status=succeeded` bundles only, (a)
   the measured window must exist, (b) the summed curve must be
   reducer-consumable (>= 2 in-window samples for a nonzero window), (c)
   powermetrics `power_trace.csv` rows must equal the adapter's
   re-derivation from `raw/powermetrics.plist` plus
   `metadata.device.plist_anchor_offset_s` as parsed analytical values
   (exact timestamps, watts, source, rail, row count, and order; not
   byte-exact CSV spelling and not tolerance-based), and (d)
   `summary_metrics.json` must equal a fresh `reduce_bundle` result
   (exact-key diff reported). Failed/unsupported bundles pass strict
   untouched; non-powermetrics bundles skip the powermetrics sub-check.

Decision: option 2. Default semantics are unchanged; strict mode is the
gate for any "all bundles intended for analysis pass validation" claim -
Phase 5 dataset publication (Stage 5.2) and Phase 4 aggregation intake
should run `validate-bundle --strict`.

Considerations: the raw-to-trace comparison is semantic row equality:
the powermetrics adapter owns plist timestamp and rail semantics, and
CSV formatting is incidental. The re-reduction comparison has one
legacy-additive exception: fresh-only null keys and a missing legacy
`summary_provenance` block are tolerated (A-19), while all stored values
and stored extras remain exact claims. Any other drift - tampering, a
reducer version change, partial rewrites - surfaces as a named key diff.
Strict mode lives in `cli.py`, not the reader: it composes the reader with the
powermetrics adapter and reducer, and the reducer already consumes the
reader (D-025), so putting it in `bundle_read` would create an import
cycle.

Consequences: `validate_bundle(path, strict=False)` keeps its importable
signature; CLI gains `--strict`; the reviewer's two reproductions are
pinned as tests (manifest emptied, summary tampered), along with the
powermetrics raw-to-trace gate; Phase 5 Stage 5.2 should adopt
`--strict` for the published sample bundles.

Amendment (2026-07-10, P2-040 / C-027 adjudication H2): reducer `0.3.0`
defines the corrected nonpositive-window, metric-specific request-gate,
joint-edge-bound, and runtime-observed token-denominator semantics. An
inventory of `runs/` (including the retained main-checkout corpus), test
fixtures, and docs found no retained or published summary artifact recording
reducer `0.2.0`; all `0.2.0` matches were historical or specification prose.
Accordingly there is no `0.2.0` compatibility projection. Strict validation
dispatches solely on the reducer version recorded in the stored summary:
the frozen pre-D-033 legacy identity allowlist retains its existing
provenance-less additive-absence tolerance; recorded `0.3.0` summaries are
compared exactly; recorded `0.2.x` and unknown versions fail with
`unsupported reducer version; re-reduction required`. The presence of a
`summary_provenance` object alone never selects compatibility tolerance.
Succeeded bundles with a nonpositive measured window fail strict admission;
honest failed summaries remain structurally and strictly valid because they
make no successful-measurement claim.

Amendment (2026-07-10, P2-038 / C-028 adjudication): the six exact frozen
legacy identities continue to reconstruct powermetrics traces with
`metadata.device.plist_anchor_offset_s` and the original cumulative-elapsed
algorithm. Current-era powermetrics bundles instead use
`metadata.uncertainty_evidence.clock_anchor.first_sample_end_point_epoch_s`:
the point is the midpoint of the recorded controller-monotonic process-spawn
to first-parse bracket after applying the conservative run wall-minus-
monotonic envelope. Record zero is timestamped at that interval endpoint;
records `i>0` advance by elapsed values `1..i`. Strict mode re-derives the
midpoint and bounds from paired-clock observations and raw plists; plist
whole-second dates are consistency checks only and never tighten the bound.
Amendment (2026-07-10, P2-040 review fix, post-#49 union): reducer `0.3.1`
adds governed output fields `measurement_quality.runtime_cleanup_ok` and
`measurement_quality.remote_cleanup_failed`; `0.3.1` strict
comparison is exact. A stored `0.3.0` summary is compared against a fresh
reduction projected to recorded reducer version `0.3.0`, with absence-only
tolerance for exactly `ADDED_SINCE_0_3_0` (currently
`measurement_quality.runtime_cleanup_ok` and
`measurement_quality.remote_cleanup_failed`); any stored value remains an
exact claim. Legacy and unsupported-version arms are unchanged. From this point,
every governed output-shape addition MUST bump the reducer patch version and
extend the immediately prior frozen version's named absence-tolerance set.
A frozen reducer version is never reused for a changed governed output shape.

Amendment (2026-07-11, P2-041 / Component C5): reducer `0.4.0` renames the
top-level evidence-only surface from `claim_eligibility` to
`window_evidence_precheck`, removes the generic `request` alias from newly
reduced summaries, and retains the metric-specific `gross_request` and
`idle_subtracted_request` entries. Reducer `0.4.0` strict comparison is exact.
Current-era summaries recording reducer `0.3.0` or `0.3.1` require explicit
re-reduction; they are not projected across this semantic rename. The frozen
pre-D-033 legacy identity arm retains its provenance-less additive-absence
tolerance and original raw reconstruction, while recorded `0.2.x` and unknown
versions remain unsupported. Legacy compatibility never authorizes positive
claim readiness. Summary schema remains `0.1`; schema `0.2` remains reserved
for the previously adjudicated composite changes.

Amendment (2026-07-11, P2-044 idle dependence / lead-adjudicated design):
reducer `0.4.1` adds the governed `idle_mean_uncertainty` derivation and changes
`E_idle_mean_j2` to `measured_duration_s^2 *
governed_variance_of_mean_w2`. Current-era reducer `0.4.0` summaries are
rejected as re-reduction-required with no absence projection; the six frozen
legacy identity arms are unchanged. Strict validation fails on a raw/metadata
idle-baseline mismatch. The predeclaration freeze, before Window-A/P2-015
calibration effects are inspected, is:

- Exact method ID and formulas, including autocovariance denominator.
- Powermetrics 10 s bandwidth.
- Median-interval lag conversion.
- IID variance floor and ESS clamps.
- Minimum three-bandwidth trace rule.
- Cadence regularity threshold of 1.25.
- Rail definition: the same CPU+GPU+ANE arithmetic total used by the idle baseline.
- Arithmetic, not time-weighted, mean so the uncertainty matches the current point estimand.
- No trimming, detrending, stationarity “repair,” or adaptive bandwidth.
- Raw/metadata cross-check tolerance and failure behavior.
- Physical-backend applicability.
- `independent_run` covariance scope and the separation from deterministic drift.
- Reducer 0.4.1 and exact P2-037 required-method gate.
- The hand fixtures below.

The frozen method ID is `newey_west_bartlett_10s_iid_floor_v1`. The estimator
uses `L=floor(10/median(interval_s))`, the IID variance floor, ESS clamped to
`[1,n]`, `n >= 3*(L+1)`, and a type-7 linear p95/p05 cadence ratio no greater
than 1.25. Raw/metadata count is exact; mean, sample standard deviation, and
duration use `rel_tol=1e-9` and `abs_tol=1e-12`. Irregular cadence fails closed
without resampling. The policy is powermetrics-v1 only; other physical
backends emit `backend_policy_not_frozen`, and mock remains non-claim-bearing.
ESS is audit-only, never P2-037's paired-block sample size or degrees of
freedom. Any later method change requires a new method ID and reducer version;
historical outputs are never silently recomputed under changed policy.
The P2-044 hand fixtures are implemented in `tests/test_idle_dependence.py`;
P2-037's propagation fixture remains owned by its separate tree.

Amendment (2026-07-11, P2-045 / adjudicated hardening C5): reducer `0.4.2`
adds governed `inter_token_throughput_tokens_s = (N - 1) /
(t_last - t_first)`, where N is the runtime-observed output-token count and the
timestamps are the first and last observed decode-token events. It is null
when N is below two, fewer than two decode timestamps exist, or their span is
zero. This is the steady-state decode/inter-token estimand. The frozen legacy
`throughput_tokens_s` name and value remain unchanged: runtime-observed output
token count divided by the first-to-last decode-token span, which counts N
tokens over N−1 inter-token intervals and therefore exceeds the new metric by
N/(N−1) when the counts agree. Because no existing field changes meaning,
current-era reducer `0.4.1` gets absence-only tolerance for exactly the new
field; a stored value remains an exact claim. Reducer `0.4.2` comparison is
exact, while the `0.4.0`, `0.3.x`, unsupported-version, and six frozen legacy
dispatch arms remain otherwise unchanged. Any change to either formula or
nullability rule requires a new reducer version; frozen versions are never
reused.

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

Application note (2026-07-11, C-028 closeout): advisor and handoff prose must
separate four states that were conflated during the arc: merged software,
an open follow-up PR, a satisfied software gate, and completed live
execution. Test counts are cited with both the exact head and environment
convention: current main 1,220/`skipped=10`; PR #59 worktree
1,224/`skipped=12`; restricted managed-sandbox runs may carry
`skipped=13`. Historical exact tails remain valid only at their recorded
heads. This is an application of D-023/D-031, not a new status authority.

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

(Amended 2026-07-08, D-043 back-annotation: the PR convention's
"the user merges" clause is superseded by Ed's 2026-07-08 standing
self-merge-with-review authority, recorded in C-010; the gate shape
lives in the resume-merge run report and `docs/orchestration.md`.)

Breach addendum (2026-07-09, C-027 whole-project review, MET-001):

Four commits landed directly on main in violation of this decision's PR
convention (only single-commit bookkeeping may bypass a PR):

- a05e54d — campaign scripts + tests (code+tests; 108 insertions).
- 8856c04 — controller/environment implementation + tests (code+tests;
  158 test lines).
- a835c73 — claims linter + 38 test lines inside a 26-file
  "bookkeeping + integration fixes" commit (code+tests mixed into
  bookkeeping).
- 36d5641 — 33-line scripts/build_site.py behavior change, NO tests,
  mixed with deployment output; postdates the then-recorded
  verification head c095c83, so main carried unverified code.

Content classes: three code+tests commits, one untested site-script
change (counterreview corrected the lead's earlier "all four contain
code+tests" overstatement — see review §6 item 2).

Remediation: retroactive independent review queued as RETRO-001
(result file: `docs/reviews/c027/retro_b6_review.md`, pending at the
time of this addendum). Recoverability evidence table:
`docs/reviews/c027/invocation_recoverability_audit.md`. Rule going
forward: integration fixes and site-script behavior changes require
their own PR; this addendum does not amend D-031's text, it records
its breach. History is not rewritten; the commits stand.

---

## D-032: `phase_energy_j` is gross-only in summary v0.1

- Date: 2026-07-07
- Status: accepted
- Phase: 2+

Context: `SummaryMetrics.phase_energy_j` attributes energy to workload
phase windows (`prefill`, `decode`, and later split phases). The reducer
also computes idle-subtracted request energy for the measured window, so
per-phase summaries need an explicit basis before 2M bundles are written.
C-007 decided that idle-subtracted phase attribution is Phase 4 analysis
policy, not a v0.1 bundle-summary contract.

Options considered:

1. Store gross phase energy only in `phase_energy_j`.
2. Store idle-subtracted phase energy in `phase_energy_j`.
3. Store both gross and idle-subtracted phase maps in summary v0.1.

Decision: option 1. `phase_energy_j` is gross joules only in summary
schema v0.1. Idle-subtracted phase attribution is derived later by
Phase 4 analysis policy, with any allocation assumptions stated there.

Considerations: gross phase windows are direct integrations over the
recorded power curve and do not require choosing how to allocate one idle
baseline across unequal or nested phase windows. This keeps the bundle
summary close to evidence while preserving Phase 4 freedom to apply a
documented attribution policy when answering analysis questions.

Consequences: consumers must not read `phase_energy_j` as an
idle-subtracted metric. Phase 4 may derive idle-subtracted phase values
from gross phase energy, idle baseline, and phase durations, but those
derived values are analysis outputs, not summary v0.1 fields.

Revisit when: a future summary schema version adds explicit per-phase
idle-subtracted fields with a named allocation policy.

---

## D-033: Prompt-content provenance is recorded per run bundle

- Date: 2026-07-07
- Status: accepted
- Phase: 2+

Context: The 2O placement council found that config hashes and token
counts do not prove realized prompt content. A tokenizer or generator
revision can produce a different token stream from the same nominal
profile, which would weaken the 2M corpus before later workload
enrichment begins. A-11 pinned the pre-2M workload provenance shape.

Options considered:

1. Rely on the normalized config hash and token counts. Con: misses
   tokenizer/model drift under the same config.
2. Record a text-only prompt hash. Con: insufficient for token-level
   identity because tokenization is part of the workload.
3. Record per-bundle workload provenance with a domain-separated hash of
   canonical JSON prompt token IDs, supplemental text hash, generator
   identity, tokenizer identity/revision/class/vocab size, model source
   and revision, and the output policy actually applied.

Decision: option 3. `metadata.json` gains additive
`workload_provenance` computed by the runtime adapter and written by the
controller. The prompt hash domain is
`joulewise.prompt_token_ids.v1`; campaign sameness is checked by
cross-bundle hash equality, not inferred from campaign membership.

Considerations: the runtime adapter is the point where text/profile
inputs become realized generation inputs, so it owns the provenance
block. The controller only carries and serializes it through
`RuntimeResult`. The block is per bundle (D-005), so repetitions can be
audited independently.

Consequences: new mock and MLX bundles record realized prompt-token
identity, tokenizer/model identity, generator identity, and
`fixed_budget_exact` output policy details. `run_campaign.py` needs no
special logic because it shells normal `joulewise run` executions.
Residual limitation: deleting both `summary_provenance` and
`metadata.workload_provenance` makes a new bundle indistinguishable from
a legacy bundle to strict validation.

Revisit when: a new runtime cannot expose token IDs or tokenizer
identity; that adapter must either add an equivalent audited source or
record a structured unavailable field before its bundles are admitted to
analysis.

---

## D-034: Slice 2O owns the workload program after 2M and 3.0.1

- Date: 2026-07-07
- Status: accepted
- Phase: 2+

Context: Commit `aa665e1` created Phase 2 Slice 2O for workload program
placement after the C-007 follow-on council. The slice owns queue tasks
P2-010 (`affine_mod_ladder_v1`) and P2-012 (`jw_mixed_v1`) as
post-baseline enrichment, not as pre-2M gates.

Options considered:

1. Put workload/prompt enrichment in Phase 4. Con: Phase 4 should
   consume workload dimensions and analysis outputs, not construct the
   workload corpus it analyzes.
2. Start workload enrichment before 2M. Con: delays and contaminates the
   homogeneous baseline milestone.
3. Create a Phase 2 post-baseline slice, 2O, gated after 2M strict-valid
   bundles, P2-013/P2-014, and the Stage 3.0.1 verdict.

Decision: option 3. Slice 2O owns the workload program P2-010 through
P2-012 after 2M and 3.0.1. Phase 4 consumes workload dimensions and
analysis-ready annotations but does not own workload construction.

Considerations: the 2O plan maps prompt/workload types to metrics and
research questions while keeping correctness quarantined as annotation,
not an intelligence-per-joule claim. This sequencing protects the 2M
baseline and keeps later workload expansion additive.

Consequences: P2-010 and P2-012 remain queued behind the 2M corpus and
the Stage 3.0.1 verdict. P2-014(e) is the pre-2M obligation: prompt
content provenance must exist before the campaign so later sameness
claims are auditable.

Revisit when: 2M is skipped or materially re-scoped; then 2O gates and
research-question mapping must be re-approved rather than silently
advanced.

(Amended 2026-07-08, D-043 back-annotation: D-042 reopened the
implementation lane for suite build before 2M; campaign-execution
ordering remains unchanged.)

---

## D-035: Replay claims require fresh-process (subprocess-per-stage) isolation

- Date: 2026-07-07
- Status: accepted
- Phase: 3+

Context: Stage 3.0.1 (verdict `replay_supported`, PR #9) established the
evidence standard that makes a KV-cache replay claim trustworthy: the
prefill/save, load/resume, and monolithic-reference stages each ran in a
fresh OS process, so no in-process cache or object reuse could fake
resume continuity. Promoted from the 3.0.1 stream ledger
(`docs/stream_logs/2026-07-07-kv-spike-301.md`, ratified by the lead
2026-07-07).

Decision: any future replay/persistence claim (3.0.2 llama.cpp, 3.0.3
vLLM, cross-machine variants, and Phase 3 measurement runs that assert
resume equivalence) must isolate the stages being compared in separate
OS processes, with only on-disk artifacts crossing the boundary.
Residual shared state (OS page cache, compiled-kernel caches) is
accepted as timing-only, not correctness-bearing.

Consequences: spike/measurement harnesses inherit the 3.0.1 script's
subprocess-per-stage shape; an in-process "resume" result is not
admissible evidence for a replay verdict.

Revisit when: a runtime cannot be driven per-stage from a fresh process;
that limitation must be recorded in the verdict itself.

---

## D-036: Spike verdict codes derive from measured data, never hardcoded

- Date: 2026-07-07
- Status: accepted
- Phase: 3+

Context: the 3.0.1 script computes `replay_supported` from the measured
token-identity comparison and the size-vs-prediction delta; a regression
flips the verdict to `partial(...)`/`replay_unsupported` with the failing
reason. Promoted from the 3.0.1 stream ledger (ratified by the lead
2026-07-07); aligns with D-015's evidence discipline.

Decision: every Stage 3.0.x feasibility verdict (and any later
feasibility gate) must be COMPUTED by the evidence-producing script from
its recorded measurements, with the failure branch emitting a distinct
verdict plus reason. A verdict string asserted by prose or hardcoded in
a report is not evidence.

Consequences: 3.0.2/3.0.3 spikes reuse this contract; reviewers check
the verdict derivation path as part of the evidence chain.

Revisit when: a verdict genuinely requires human judgment inputs; those
inputs then become recorded fields the code still derives from.

---

## D-037: Claims ladder (L0-L4) binds reader-facing claim language from 2M onward

- Date: 2026-07-08
- Status: accepted
- Phase: 2+

Context: an independent 5.5 critique of the whole project (counter-
reviewed and adjudicated in council C-011) found that the project's
claim discipline lived in scattered prose — the two-claim track, the
detection-floor gate, question-bank quarantines — with no single binding
taxonomy for how strongly a result may be worded. The 2M report is
imminent; wording discipline is cheapest before the first corpus lands.

Options considered:

1. Keep prose discipline + the planned Phase 4 claims index. Con: the
   strongest language can arrive before Phase 4 review catches it — it
   already did once (the flagship report's active-parameter wording,
   demoted by C-005/DOC-007 but resurfacing in derived prose).
2. Full claims index now with per-claim IDs. Con: only six real bundles
   exist; most rows would be placeholders (council: seed it post-2M).
3. Adopt the ladder now as a lightweight binding contract; per-claim IDs
   and mechanical enforcement arrive with the Phase 4 index.

Decision: option 3. `docs/contracts/claims_ladder.md` defines L0
(capability) through L4 (generalized finding) with allowed claim shape,
required evidence, and forbidden language per level, plus two riders:
cross-boundary comparisons are descriptive-only without a named
calibration bundle, and energy-per-output-token claims require
runtime-observed token counts + stop reason + output-policy label
(config-fallback denominators force L0 wording). Phase 4 Stage 4.3
acceptance requires every final-report claim to carry its ladder level.

Consequences: reader-facing docs written from 2M onward cite the level
their evidence supports; the flagship two-point comparison is pinned at
hypothesis-generating (L1 with the confound caveat); reviewers check
wording against the ladder as part of the standard lens rounds.

Revisit when: the Phase 4 claims index lands (mechanical enforcement
may subsume the prose rule), or a claim class appears that the five
levels cannot express.

---

## D-038: Analysis-plans contract binds L2/L3 claims to pre-registered plans

- Date: 2026-07-08
- Status: accepted
- Phase: 2+

Context: the suite-science hardening council (C-014) found that planned
comparisons carried no pre-registered analysis: estimators, floor gates,
sample sizing, and claim ceilings lived in scattered prose, and the
Token-Shape Sufficiency Null (C5-W.1) was unfalsifiable as designed. The
claims ladder (D-037) disciplines wording but not the analysis that
produces the number being worded.

Options considered:

1. Keep discipline in the question bank per question. Con: the bank
   records what a question is, not how its comparison will be analyzed;
   the C-W.1 confound survived three council passes there.
2. Full statistical analysis plan documents per campaign. Con:
   pre-registration theater; prose ritual the loop would stop reading.
3. A compact per-comparison plan table as a contract, with a binding
   rule: no reader-facing L2/L3 claim without a filled plan row.

Decision: option 3. `docs/contracts/analysis_plans.md` defines the plan
schema (metric + window class, unit of analysis + dependence structure,
estimator, inclusion/waiver rules, order/blocking, floor gate =
max(floor_abs, floor_cmp), MDE/n sizing with predeclared top-up,
denominator provenance, holdouts for L3, claim ceiling, disqualifiers,
post-execution manifest links) plus standing reporting rules: phase
metrics are gross-only until phase-idle modeling exists; short-prefill
windows below 3 samples report `not resolvable`; capped cells are
excluded from prompt-slope/rank claims unless realized lengths match;
rank claims require rank gap > comparison MDE; itemized suites
(ladder/mixed items inside one bundle) are never treated as independent
replicates — uncertainty is computed at bundle or block level.

Consequences: six plans seeded (Q4 grid fit, 2M asymmetry, Q5 rank
stability, C5-W.1 equivalence, ladder level-energy guards, content
sentinel); floor fields fill from the P2-015 calibration artifact;
reviewers check L2/L3 wording against plan rows as part of standard
lens rounds.

Revisit when: the Phase 4 claims index lands (plans may merge into it),
or a comparison class appears the schema cannot express.

---

## D-039: Workload program v2 — substrate first, identification before scale

- Date: 2026-07-08
- Status: accepted
- Phase: 2+

Context: C-014 (lead audit + scout + three design lenses + peer
counterreview) found the planned suite could measure things no consumer
cites and claim things no design could support: Q4 unreachable at L3
from the 4-cell 2M grid; P2-015 yielding only an absolute floor while
L2/L3 claims are gated by the comparative MDE; jw_mixed_v1 cross-
category comparisons shape-confounded; the full 64-level scored ladder
having no claims-index consumer; Q4-Q6 having no Phase 4 figure slots.

Decision, five parts (specs live in the amended
`docs/research_question_bank.md`, `docs/phase_2/phase_2_plan.md` 2O, and
`docs/contracts/analysis_plans.md`):

1. P2-010 splits: P2-010a reusable suite substrate (item/level markers,
   `BundleReader.item_windows()`, category/source_manifest/output_policy
   fields, per-item stop/token/response hashes); P2-010b smoke-scale
   ladder whose acceptance is envelope validation. The full scored
   64-level campaign is deferred until C5-1.9 has a named consumer.
2. jw_mixed_v1 runs phased: common-shape identification stratum (all six
   categories at one matched shape) → natural-EOS pilot (>=4
   items/category on reasoning/JSON/chat/multilingual) → full panels
   only if earlier phases show above-floor structure. Supersedes the
   fixed-budget-full-first sequencing from C-005; quarantines intact.
3. New suite element `q4_l3_shape_grid_v1` (AP-1): 4x3 prompt x decode
   grid with predeclared interpolation + extrapolation holdouts,
   categorical-additive fit first — the only planned path to an L3
   claim on current hardware.
4. Quiet-window execution is TWO windows: A = expanded P2-015 floors +
   2M + drift sentinels, then reduce and compute CV/floor/MDE; B = Q4
   grid with n sized from Window A, plus the content-sensitivity
   sentinel. Rationale: MDE-sized n cannot honestly precede the floor
   measurement.
5. P2-015 expands to per-metric/window-class floors (gross request,
   idle-subtracted request, phase, item/level) plus comparative MDE
   tables; `docs/phase_2/detection_floor.md` becomes a per-consumer
   table.

D-034's gate is unchanged: 2O work stays post-2M; the only pre-Window-A
item is P2-021 (drift-sentinel support in the 2M generator), which is 2M
campaign tooling, not workload enrichment.

(Amended 2026-07-08, D-043 back-annotation: this pre-Window-A allowlist
was superseded twice: first by D-041 item 5's amendment, then by D-042.)

Consequences: queue rows P2-015/P2-006/P2-010/P2-012 amended; P2-019,
P2-020, P2-021 added; Phase 4 figure registry gains F9-F12 so Q4-Q6
data has named consumers before it is collected.

Revisit when: Window A results contradict the sizing assumptions, or a
consumer for the full scored ladder appears.

---

## D-040: Suite architecture v2 — one generic suite mechanism, bundle-level replication

- Date: 2026-07-08
- Status: accepted
- Phase: 2+

Context: Ed directed the benchmark toward multi-prompt runs of varying
difficulty and type. Council C-015 (two design lenses + peer
counterreview) designed the architecture; the statistical shape had to
compose with D-038's pseudo-replication rule.

Decision (spec in the question bank's C-015 section):

1. A suite bundle executes k distinct items once each (r_within = 1);
   replication comes from B whole-suite bundles (B >= 5, top-up 10).
   Within-bundle repeats are reserved for sentinel items — they estimate
   order/cache/thermal effects, never independent n. Uncertainty lives
   at bundle/block level (D-038).
2. No per-item micro-cooldowns: back-to-back execution is the named
   session ecology. Order is rotated/Latin-squared across bundles;
   item/block/position/prefix-group/order-seed metadata recorded.
   Suites split into balanced blocks when wall time exceeds ~10-15 min
   OR drift sentinels/floor identifiability degrade. k=24 first default.
3. ONE mechanism: affine ladder, jw_mixed, q4 grid, content sentinel,
   and benchmark imports are all PROFILES over one suite manifest +
   marker/window path. After P2-010a, no workload expansion gets bespoke
   plumbing — new benchmarks are manifests plus generators.
4. P2-010a is capped to the MINIMAL substrate (markers, item_windows(),
   source/category/output-policy fields, per-item token/stop/response
   hashes, order/cache metadata, manifest validation) PLUS the per-item
   validity/status model (succeeded | malformed | capped | runtime_failed
   | below_floor | excluded_from_claim) with aggregation rules for when
   partial suites remain claim-usable. Scorers, import-specific fields,
   and rich difficulty machinery are deferred until profiles need them.
5. Difficulty is first-class quarantined item metadata {axis, value,
   scale, label, source}; shape is not difficulty; the C-004 quarantine
   composes unchanged.

Consequences: P2-010 queue row redefined; suite throughput rises 3-15x
in item coverage while n stays honest at the bundle level; every later
workload (including imports) inherits provenance, windows, and the
status model for free.

Revisit when: P2-010a implementation finds the minimal substrate
insufficient, or a profile genuinely cannot ride the generic mechanism.

---

## D-041: Benchmark interop — frozen-subset imports + marker-shim energy layer

- Date: 2026-07-08
- Status: accepted
- Phase: 2+ (all implementation post-2M per D-034; see stop-line)

Context: Ed directed easy integration of external benchmarks into the
suite and extension of external benchmarks with JouleWise's energy
measurement. C-015 designed both directions.

Decision (specs in the bank C-015 section + adapter_contracts.md):

1. IMPORT: a thin `benchmark_import` manifest freezes identity,
   licensing, contamination, rendering, and quarantine metadata for a
   hash-manifested external-benchmark subset; execution rides P2-010a.
   First target: HumanEval as a plumbing smoke (MIT; 256/512-token
   completions clear the ~9 Hz item-window floor more plausibly than
   short-answer benchmarks); FLORES second (tokenizer/multilingual
   science); MMLU/tinyBenchmarks rejected as first targets.
2. EXPORT: a marker-emitting shim contract — the external harness owns
   prompts, generation semantics, and accuracy artifacts; JouleWise owns
   power capture, bundle assembly, marker validation, and energy
   reduction. P2-022 is a verdict-shaped feasibility spike
   (external_markers_supported | partial | unsupported; D-035/D-036
   inherited) pinned to energy-layer feasibility ONLY.
3. Joined accuracy(theirs)+energy(ours) data may state observed energy
   for marked item/subset windows alongside the external metric
   ARTIFACT; it may never produce JouleWise accuracy claims,
   pass@k-per-joule, leaderboard standing, or intelligence-per-joule.
4. Kill/defer list (C-015; the bank's C-015 section holds the verbatim
   11-entry list, which is authoritative): leaderboard integration, live
   dataset fetching, latest-split support, accuracy scoring beyond
   quarantined annotation, judges/retries/pass@k/benchmark-score
   normalization, full per-harness adapters AND generation-callable
   wrappers as the FIRST export path (the shim comes first; they are
   sequencing kills, not categorical), per-item uncertainty treated as
   independent replication, public energy leaderboards before cross-lab
   replication, any intelligence-per-joule ratio.
5. Sequencing gate AMENDED (D-039 named only P2-021 as the pre-Window-A
   item; this adds the Window-A capture hardening stream, and nothing
   else): only P2-021 and Window-A capture hardening precede P2-015/2M. Substrate, shim spike, imports, q4-grid and
   jw_mixed execution are post-2M unless D-034 is reopened. Stop-line:
   under schedule pressure, interop and suite expansion drop before
   P2-015/2M/Mac characterization — the guaranteed capstone is the
   instrument plus Mac characterization, never the expansion.
   (Amended 2026-07-08 pre-merge: the allowlist names pre-Window-A
   work items; prep steps internal to P2-015, including the lead-run
   tasks-sampler overhead smoke that also validates the 2s env-capture
   settle absorbs the probe burst, are part of P2-015 itself, not
   additional items.)

Consequences: queue gains P2-022/P2-023/P2-024; adapter_contracts.md
gains the shim contract; the bank gains C5-I.1..I.5 and the capability
map; export direction prioritized over import for adoption-per-build-day.

Revisit when: the P2-022 spike returns unsupported/partial, or D-034 is
reopened.

(Amended 2026-07-08, D-043 back-annotation: the revisit clause FIRED by
D-042's reopening. ADJUDICATION RECORDED: D-042 opened only the
suite-BUILD lane; the interop lane (P2-022 shim spike, P2-023 imports)
REMAINS post-2M + post-P2-010a as originally gated.)

---

## D-042: D-034 implementation lane reopened — suite build proceeds pre-2M (owner directive)

- Date: 2026-07-08
- Status: accepted
- Phase: 2+

Context: Ed directed (this session) that the test-prompt suite for
observation/trace generation be actually built with dedicated research
and effort, not only specified. D-034 (reaffirmed by the C-015 gate
amendment) held ALL 2O substrate/suite implementation post-2M; its
revisit clause names exactly this: reopening by decision rather than
silent advancement.

Decision: the IMPLEMENTATION lane of the workload program is open now:
P2-010a substrate, P2-010b smoke ladder, P2-012 phase-1 content
generators, and P2-020 sentinel content generation may proceed as
[AGENT] work before 2M. UNCHANGED: campaign EXECUTION ordering (Window A
P2-015 floors then P2-006 2M first; Window B after), the quiet-machine
clause of the C-015 stop-line (no suite work consumes quiet-machine
time), the minimal-substrate cap (D-040.4), and all quarantines. The
drop-order under schedule pressure also stands: suite build drops before
P2-015/2M/Mac characterization.

Research input: `docs/phase_2/suite_implementation_research.md`
(4 cross-checked reports; amendments are UNRESOLVED review findings the
implementing session adjudicates first).

Consequences: P2-010/P2-012/P2-020 status cells flip to build-unblocked;
the 2O gate paragraph carries a dated amendment note pointing here.

Revisit when: suite build threatens the Window A/2M schedule (drop it),
or 2M lands (gate question dissolves).

---

## D-043: Supersession-closure discipline

- Date: 2026-07-08
- Status: accepted
- Phase: all

Context: a meta-reassessment (5-analyst workflow over the full
council/decision/skill logs) found ~70% of accumulated doc defects were
one mode: a rule superseded while its losing surfaces stayed live (merge
authority x3 surfaces, the pre-2M allowlist x3 versions, topology x3
docs, the decision index ending at D-037, unamended fired revisit
clauses).

Options considered:

1. Continue relying on broad end-of-session consistency sweeps. Con: the
   drift pattern survived repeated sweeps because losing surfaces were
   outside the immediate diff.
2. Require only the winning decision to mention what it supersedes. Con:
   readers landing on the older rule still see a live instruction.
3. Add write-time back-annotation plus a sweep-time supersession check
   keyed by the session's supersessions.

Decision: option 3.

1. WRITE-TIME: any change that supersedes a prior rule MUST, same
   session, append a dated amendment/supersession line to EVERY surface
   stating the losing version, including the superseded decision/council
   entry and its index row.
2. SWEEP-TIME: the end-of-session consistency sweep includes a
   supersession check driven by the session's SUPERSESSIONS (grep the
   superseded wording across both logs, contracts, process docs), not
   only its diff.

Consequences: fired-clause back-annotations above land under this rule;
the sweep prompt gains check five.

Revisit when: if two consecutive sweeps find zero supersession drift, the
sweep-time check may relax to spot-checks.

---

## D-044: Suite config identity — omission-serialized ref + effective-manifest hash

- Date: 2026-07-08
- Status: accepted (suite-build adjudication; A1/A3 dispositions)
- Phase: 2

Context: P2-010a adds `workload_profile.suite_manifest_ref` as a fourth
mutually exclusive prompt source. Under D-029's nullable emission it
would emit `null` into EVERY normalized config, breaking all five pinned
config hashes and therefore run identity (D-001/D-022/D-005) for
logically unchanged configs. Separately, a path-only ref leaves manifest
BYTES outside run identity: two runs with different manifest content at
the same path would share config hash and D-022 suffix.

Options considered:

1. Accept the hash break and repin (uniform dataclass serialization).
   Con: global identity churn for the 6 real corpus bundles' config
   lineage, against D-029's protect-hashes rationale.
2. Serialize the new suite fields by omission when None; keep every
   pre-existing optional null-emitted. Con: one scoped carve-out in
   `to_dict()`; the emitted-keys round-trip test must learn about
   declared omitted optionals.
3. For manifest identity: ref-only config with sameness via
   `metadata.suite.manifest_sha256` (dataset_ref precedent). Con: config
   hash misses manifest bytes — D-022 collision across different
   manifests at the same ref.
4. Config also carries a required manifest hash. Sub-choice: raw file
   bytes vs the canonical EFFECTIVE manifest (defaults materialized) —
   raw bytes would let a future change to code-level defaults alter
   effective semantics without changing identity (counterreview catch).

Decision: options 2 + 4 (effective-hash form). `suite_manifest_ref` and
`suite_manifest_sha256` are BOTH omitted from `to_dict()` when None
(scoped D-029 exception, back-annotated there) and both required
together. `suite_manifest_sha256` is the SHA-256 of the canonical
effective manifest: parsed, schema-validated, pinned defaults
materialized, sorted-key 2-space JSON + newline (D-001 convention).
`_stage_validate` recomputes it from the ref'd file and fails closed on
mismatch (structured failure, in-bundle). The bundle writes the
canonical effective manifest as `suite_manifest.json`; `metadata.suite`
records the same effective hash plus the source file's raw byte hash as
audit evidence. A suite example config gets its own pinned hash in
`tests/test_schemas.py`.

Considerations: manifest bytes now enter run identity through the config
hash; campaign sameness remains hash equality, never membership (D-033
rule). Changing a pinned marker/output default (D-045) changes effective
manifests, hence hashes, hence identity — deliberate.

Revisit when: schema v0.2 export (D-008) restates the serialization
rules; or a third omission-serialized field is proposed (then decide a
general rule instead of accreting exceptions).

---

## D-045: Suite substrate execution semantics

- Date: 2026-07-08
- Status: accepted (suite-build adjudication; A4/A5/A6/A8/C6 + attack-round guards)
- Phase: 2

Context: P2-010a implements the C-015 generic suite substrate; the
execution-architecture report (suite_implementation_research.md §A) is
sound-with-amendments and its adjudicated form needs its contract
choices pinned.

Decision (bundle of pins; alternatives recorded in the research doc's
adjudication section):

1. Item loop lives runtime-side: new `SuiteRuntimeAdapter` protocol with
   `run_suite(config, manifest, context)`; `run_workload` untouched;
   [AMENDED 2026-07-08, oversight round: the signature gained
   keyword-only `order_seed` supplied by the controller so the seed is
   never runtime-derived — `run_suite(config, manifest, context=None, *,
   order_seed)`; see item 6 and adapter_contracts.md];
   controller dispatches when a suite manifest is present and fails fast
   pre-window (`UNSUPPORTED_WORKLOAD` when the runtime lacks the
   protocol; structured FAILED on unreadable/invalid manifest).
2. Manifest is a bundle-root artifact (`suite_manifest.json`, canonical
   effective form per D-044), never embedded in config.
3. Marker events ride the five-key event shape with `phase: "suite"`;
   vocabulary (suite/block/level/item start+end event types and required
   metadata keys) is pinned in `joulewise/suite.py` constants. The
   manifest's `markers:`/`outputs:` blocks are OPTIONAL: absent →
   pinned defaults materialized into the effective manifest; present →
   values must equal the pinned constants; divergent → validation
   error. Changing a default is a suite schema revision, never a silent
   code edit (identity via D-044).
4. Status ownership: runtime assigns `succeeded|malformed|capped|
   runtime_failed` in `item_end`; reducer alone may downgrade to
   `below_floor` (floor seam ships with `floor_source =
   "none_pending_P2-015"`); `excluded_from_claim` is analysis-only and
   is a validation error if seen in events or summaries. FIXED-BUDGET
   UNDERRUN (emitted < planned under `fixed_budget_exact`) is
   `malformed` with `status_reason="fixed_budget_underrun"`; bundle
   validation rejects `succeeded` where `fixed_budget_exact` and
   `emitted_tokens != planned_output_tokens`.
5. Per-item prompt sources are mutually exclusive per item:
   `prompt_text` (materialized at generation time, text path, BOS inside
   budget) | `prompt_token_ids` (ids-native additive path, required by
   D-046 sentinels) | synthetic shape (`shape.planned_prompt_tokens`).
   Per-item prompt identity uses the existing domain-separated token-ID
   hash (`joulewise.prompt_token_ids.v1`, D-033); any `prompt_sha256`
   field name means the token-ID hash.
6. `order_seed` derives deterministically:
   `sha256(suite_seed + "\0" + order_policy + "\0" + str(rep_index))`
   truncation per implementation; recorded in `suite_start` metadata and
   `metadata.suite`; never runtime-chosen.
7. Per-item/block/level energies are GROSS-only (C-014 phase rule); no
   per-item idle subtraction or token-normalized claim metrics.
8. Per-item outputs: single `outputs/suite_items.jsonl`; each line
   carries `item_id`, `item_index`, `status` (+ `status_reason` when
   applicable), `prompt.token_ids_sha256`, `response_text`,
   `response_sha256`, `stop_reason`, `prompt_tokens`, `emitted_tokens`,
   token timestamps. Response TEXT is hereby RATIFIED as a P2-010a scope
   addition to the C-015 minimal sketch (needed for re-reducible
   scoring, D-036/C-004); the bank sketch gets a dated amendment.
9. Reducer summary gains additive `suite_metrics` (not in
   `_SUMMARY_WRITER_KEYS_V0_1`, `summary_provenance` precedent);
   `SUMMARY_REDUCER_VERSION` bumps to `0.2.0`.

Revisit when: composite/split bundles (schema v0.2) touch suite
manifests; or the first real suite campaign contradicts a pin.

---

## D-046: AP-6 sentinel delivery — ids-native, BOS-less, literal equal shape

- Date: 2026-07-08
- Status: accepted (suite-build adjudication; B5 disposition, counterreview-amended)
- Phase: 2

Context: AP-6 requires five equal-shape content conditions. Text-path
prompts realize BOS + 511 content tokens (`add_special_tokens=True`)
while the incumbent repeated-seed stream and the random-token sentinel
are ids-native with no BOS — "equal shape" was not literally true, and
BOS-normalizing the control would change the very incumbent stream
(`_synthetic_prompt_tokens`) whose generalization AP-6 tests.

Options considered:

1. Prepend BOS to ids-native conditions (511 content tokens). Con: the
   control stops being byte-for-byte the incumbent stream.
2. Record BOS presence as covariate, conditions heterogeneous. Con:
   "five equal-shape conditions" would be false as written.
3. Deliver ALL five conditions ids-native without BOS: text-derived
   conditions (natural prose, code-like, multilingual) are generated
   with `add_special_tokens=False` accounting and delivered as token
   ids.

Decision: option 3. Literal equal shape across all five; the control is
exactly the incumbent recipe; `bos_present=false` and
`prompt_source="token_ids"` recorded per condition. BINDING CAVEAT
(counterreview): AP-6 results describe the ids-native no-BOS regime and
do NOT automatically generalize to the AP-4 text path (BOS present,
different delivery); the AP-6 row carries this limit, and a small
text-path bridge (AP-6b) is the named option if Window-B analysis needs
the generalization. jw_mixed category items (AP-4) are unaffected.

Revisit when: AP-6b is proposed, or a model/tokenizer without a stable
ids-native path enters the sentinel set.

---

## D-047: Affine ladder pins — level set, smoke sizing, gate denominators

- Date: 2026-07-08
- Status: accepted (suite-build adjudication; C0/C2/C3/C5/C8/C9 dispositions)
- Phase: 2

Context: the affine-ladder report (suite_implementation_research.md §C)
needed lead ratification of its level-set reading and statistical
corrections from its cross-check.

Decision:

1. Level set is the powers of two `{1, 2, 4, 8, 16, 32, 64}` — the
   bank's "levels 1..64" line is edited to say so (docs fix). Item
   identity keys on the difficulty VALUE (`n_iter`), so smoke items are
   a strict subset of full-ladder items.
2. Smoke ladder (P2-010b): levels `{1, 8, 64}` × 8 items/level + 2
   repeated-seed sentinel executions (suite start/end); k = 24 distinct
   items (C-015 first default holds; the earlier "k=26 / 2-over" claim
   was an accounting error — sentinel executions are within-bundle
   repeats, not distinct items). B = 5 bundles, top-up 10.
   AMENDED 2026-07-08 (AFF-1, review-driven, same session): the sentinel
   is a DEDICATED derived item (`n_iter=1, item_index=8`, id
   `affine_v1_sentinel`) so no ordinary level item carries the sentinel
   tag — duplicating L01/i00 would have corrupted the
   8-distinct-items-per-level denominator. Accounting is therefore
   k = 25 distinct items / 26 executions; every level still has exactly
   8 untagged distinct items. Ledger:
   docs/stream_logs/2026-07-08-affine-ladder.md AFF-1.
3. Gate statistics: under deterministic (greedy) decoding, repeated
   bundles replicate ENERGY only; all token/stop-reason/correctness
   denominators are the 8 DISTINCT items per level. E1's 5% threshold at
   n=8 means ZERO tolerated non-EOS items per level — stated, not
   implied. The report's pooled "40-80 items/level" power framing is
   rejected as pseudo-replication.
4. E5 (early-EOS bias) is advisory and recorded
   `expected_not_evaluable` at smoke sizing (needs ≥10 distinct parsed
   items per class); smoke stays 8 items/level.
5. Sampler pinning (B9, applies suite-wide): the MLX adapter records
   sampler provenance (greedy/temp-0 default made explicit) so "greedy"
   in manifests rests on recorded fact, not an unpinned library default.
6. AP-5 row edit rides this decision: the scored campaign predeclares
   malformed-as-incorrect in the accuracy denominator (reported
   alongside); full-ladder k=112 + sentinels still needs its own
   ratification at campaign time.
7. Threshold defensibility (C7): the ~4%-of-window arithmetic is
   re-anchored on the first smoke bundle's measured level-window energy;
   smoke bundles double as level-window floor-calibration evidence for
   P2-015.

Revisit when: the first smoke bundle's measured item time falls outside
0.11–0.20 s/item (resize per the report's table); or the scored
campaign is scheduled (k-policy ratification).

Amendment (2026-07-09, CP-5 resume, PR #27): the sampler-pinning clause
is superseded — adapters now FAIL CLOSED with `sampler_pin_unverified`
when the sampler cannot be pinned/verified, instead of proceeding
unpinned with a provenance note. Accepted at the CP-6 methodology
adjudication; contract wording updated in
`docs/contracts/adapter_contracts.md` the same session.


---

## D-048: Split program is model-first — pre-registered compositional prediction before split runs

- Date: 2026-07-08
- Status: accepted (C-020 whole-project merit debate; three-pole consensus)
- Phase: 3 (binds Phase 3 design + AP row seeding; framing binds Phase 4)

Context: the C-020 merit debate's decisive arithmetic (KV bytes/token ×
link speed vs measured idle/decode watts) shows the Q1 crossover is
possible but NOT likely uniformly across the planned pairings — a bare
"no crossover found" sweep result would read as predictable. All three
debate poles (session-lead Fable, fresh-Fable, Codex stack) converged
independently on the fix.

Options considered:

1. Keep the crossover sweep as the flagship, report whatever verdict
   lands. Con: the null branch is a shrug; a positive is a point
   observation without a transferable theory.
2. Invert entirely — make the Q4 compositional model the thesis and the
   split sweep mere validation (fresh-Fable's strong form). Con:
   under-weights that the both-end per-stage energy decomposition
   DATASET is itself the first-of-kind artifact regardless of model fit.
3. Synthesis: model-first FRAMING, dataset-first CONTRIBUTION.

Decision: option 3. The program's thesis sentence is: "JouleWise builds
auditable per-stage split-inference energy bundles, then tests whether a
pre-registered compositional model predicts them." Binding mechanics:
(a) BEFORE any split hardware runs, the compositional model (AP-1 Q4
coefficients + measured link-transfer energy + idle floors) produces
pre-registered predicted split-energy curves per pairing/link, recorded
in a seeded analysis-plan row (incl. the named same-boundary headline
pairing, which is L2-eligible calibration-free); (b) Phase 3 acceptance
is reframed as prediction validation: every branch is a result —
confirmed model (predictive tool), quantified unmodeled overhead term
(systems finding), or crossover located where predicted (doubly
credible); (c) a no-crossover verdict is publishable ONLY as successful
prediction or quantified overhead discovery, never presented as a
surprise negative. Design should include at least one pairing/link cell
where the model PREDICTS a crossover, if any exists in the feasible set.

Consequences: `docs/phase_3/phase_3_plan.md` acceptance framing gets a
dated amendment pointing here; the AP row obligation rides the split-prep
queue row; Phase 4 claim wording inherits the thesis sentence.

Revisit when: the 2M-fitted Q4 model fails its own monolithic holdouts
(then the compositional prediction has no validated coefficients and the
sweep reverts to exploratory with that stated).

---

## D-049: Split transfer-energy boundary accounting on discrete-GPU ends

- Date: 2026-07-08
- Status: accepted (C-020; Codex-stack catch, repo-verified)
- Phase: 3

Context: on nvidia-smi-measured ends, board power EXCLUDES the host
CPU/NIC/DRAM work of moving KV bytes over TCP — so "transfer energy"
measured at a discrete-GPU end is near-zero by construction: a silent
undercount in unmeasured silicon, asymmetric across the pairing matrix
(Mac and Jetson boundaries include their NIC/host paths; dGPU boundaries
do not).

Options considered:

1. Ignore — report board-only numbers. Con: cross-pairing transfer
   comparisons silently broken; exactly the boundary sin (D-018) the
   project exists to avoid.
2. Wall-meter (or equivalent host-side measurement of) the GPU host on
   transfer legs so the transfer window has a host-inclusive boundary.
3. Explicitly scope dGPU transfer cells as board-only LOWER BOUNDS in
   the stage accounting, named per cell in the AP row and claim wording.

Decision: option 2 where the meter is available for the leg, option 3
otherwise — never option 1. The per-stage accounting schema must carry a
per-cell boundary label for the transfer stage; the seeded split AP row
(D-048) names which cells are host-inclusive vs board-only lower bounds;
cross-pairing transfer-energy comparisons are permitted only between
like-boundary cells or via the D-018 calibration bridge.

Consequences: split-prep queue row carries this; `docs/contracts/`
boundary docs get the transfer-stage label when the split schema lands
(Phase 3 implementation, not now — R-015 additive rule applies).

Revisit when: the wall/USB-C calibration (Q6) bounds the host-side gap
tightly enough to model it instead of measuring per leg.

---

## D-050: Active stop cards and process-trace manifests

- Date: 2026-07-09
- Status: accepted (user-directed meta-process cleanup after CP-5 pause)
- Phase: cross-project process

Context: CP-5 intentionally paused a live pre-campaign review session
after token spend ran out. The project preserved the necessary resume
facts, but they were split across `RUN_STATE.md`, `TASK_QUEUE.md`, a
stream log, off-repo checkpoint artifacts, and older run-report restart
pointers. That made the handoff recoverable but too easy to bypass.

Options considered:

1. Leave the existing pointers alone. Con: normal "what next" prose can
   compete with an active checkpoint and lead a future agent into lower
   queue work.
2. Move all checkpoint details into the queue. Con: the queue is too
   compact to own dirty worktree/PR/artifact inventory safely.
3. Add an active stop-card layer to `RUN_STATE.md`, with the queue and
   run-report intake explicitly subordinated to it, plus lightweight
   manifests for future delegated runs.

Decision: option 3. An ACTIVE `ACTIVE_STOP_CARD` in `RUN_STATE.md` is
the single restart authority wrapper and overrides normal next-work
sections, queue ranking, playbook missions, and latest-run-report
defaults until cleared. Stop cards must preserve the resume authority,
reason for stop, paused work inventory, status terms, artifact pointers,
first resume action, and clearance criteria. Substantial delegated,
skill, council, or worktree-heavy runs must leave a process trace and,
when large enough, an `invocation_manifest.jsonl`-style pointer map tying
prompts, sessions, outputs, dispositions, and commits/PRs together.

Consequences: CP-5 remains paused and untouched, but future intake now
routes to its exact stream-log authority first. Half-finished work is
not executable unless it has an authority pointer, bounded scope,
acceptance evidence, and a lane. Councils retain their role for
methodology/measurement/claim/hardware decisions but must report yield,
dispositions, and downstream closures. `scripts/codex-bridge` now
implements a local invocation manifest with prompt snapshots, response
snapshots, logs, status files, prompt/output/log hashes, session-id
capture when present, and pending disposition fields.

Revisit when: one full stopped-and-resumed session completes under the
new stop-card rule, or the invocation manifest proves too heavy for
ordinary delegated runs.

Stop-card override addendum (2026-07-09, C-027, MET-001 / REV-5):
during the ACTIVE CP-5 stop card (RUN_STATE at 2c8b267: "Do not start
other queue work"), advisor-site commits bf9ffc5, a1ac0a7, fda79c1,
e6cf431 were produced before CP-5 resumed (later landed via PR #28).
User direction for that work existed and is recorded at
docs/run_reports/2026-07-09-advisor-status-site.md:13, but no override
was recorded on the stop card at the time. Disposition: recorded
retroactively as a USER-DIRECTED OVERRIDE (scope: advisor status site
only; CP-5 state untouched), plus a recording failure — the override
should have been appended to the stop card when work began. Rule
restated: undocumented supersession of an active stop card is
indistinguishable from bypass; overrides are recorded on the card
before the first commit of overriding work. A second override
precedent is recorded here for the same reason: Ed's 2026-07-09 live
directive to begin implementation before spec adjudication (C-027 spec
wave) superseded the recorded DRAFT-pending-adjudication gate —
recorded so undocumented supersession does not recur.

---

## D-051: Advisor status site uses source-derived static pages plus fail-soft live GitHub overlays

- Date: 2026-07-09
- Status: accepted
- Phase: 2 / project communication

Context: the Lakebed status site had a strong static source-derived
observatory and a live freshness banner, but the deployed snapshot could
still be stale exactly where an advisor cares most (`RUN_STATE.md` and
`TASK_QUEUE.md`). The hand-authored Story page also carried moving counts
that had drifted from the generated status pages.

Options considered:

1. Keep the site purely static and rely on the freshness banner. Pro:
   simplest deployment. Con: advisors still read stale body text first.
2. Make Lakebed the new source of truth for project status. Pro: live UI.
   Con: creates a second status database and undermines the repo audit
   trail.
3. Keep repo markdown as the source of truth, generate static pages from
   it, and add fail-soft Lakebed overlays that fetch current GitHub
   markdown for a narrow set of advisor-facing fields.

Decision: option 3. The source-derived static site remains the fallback
and audit surface. Lakebed serves `/api/freshness` for commit drift and
`/api/live-status` for a small parsed live view over
`PROJECT_STATUS.md`, `RUN_STATE.md`, `TASK_QUEUE.md`, and the risk
register. The status page may update top-line fields from this API while
source chips and generated pages continue to show exactly what the baked
snapshot was built from.

Consequences:

- The Story page should avoid volatile counts unless they are generated
  or source-linked.
- Advisor-facing depth belongs in generated status panels: snapshot
  state, advisor asks, campaign readiness, evidence board, and claim
  ceiling.
- Lakebed endpoint aliases should remain server endpoints, because
  Lakebed routes direct HTTP requests to matching `GET` endpoints before
  client routes.
- The live APIs must fail soft and must never hide static provenance.

Revisit when: GitHub raw-content fetch becomes unreliable enough to need
an authenticated token or when a formal advisor portal with user-specific
state is required.

## D-052: Capstone scope contract — frozen umbrella headline and contribution ladder

- Date: 2026-07-09
- Status: accepted
- Phase: cross-phase / claims

Context: review C-023 (finding B4) required one frozen, defensible headline
claim with fallbacks, and the user's 2026-07-09 direction required the
contribution framing to honor the filled measurement matrix as the end-goal
novelty. Stream ledger: `docs/stream_logs/2026-07-09-scope.md` (SC-1).

Decision: `docs/contracts/capstone_scope.md` (PR #30) is the binding scope
contract. Headline: "auditable, boundary-labeled local LLM energy
characterization on named hardware/runtime/model/workload stacks" — an
umbrella scope statement carrying NO global claim level; per-result
ceilings follow D-037. Split inference is a stretch extension gated on a
named method; calibration is required specifically for cross-boundary
quantitative winners. Contribution is argued as a three-rung ladder
(instrument/methodology → filled-matrix scoped empirical coverage →
contingent findings), with auditability as the warrant that makes the
coverage claim believable, not a substitute for it. R-012 remains the
single home of the minimum-viable-capstone floor; the contract adds
reporting stop-lines only.

Consequences: reader-facing wording must trace to this contract; the
related-work check (vs JouleSort, MLPerf Power, ML.ENERGY, Zeus) is a
named precondition for the Rung-2 coverage-novelty claim.

## D-053: Contrast-level statistical inference and the frozen analysis registry

- Date: 2026-07-09
- Status: accepted (ratifies the "pending ratification (C-023 S3)" contract markers)
- Phase: cross-phase / statistical protocol

Context: review C-023 (findings B2 + M1) found the D-014 interval-separation
rule statistically wrong for paired designs and no benchmark-level
multiplicity policy. Stream ledger: `docs/stream_logs/2026-07-09-stats.md`.

Decision (PR #29): claims derive from the confidence interval of the
paired/block difference or named model contrast, never marginal-interval
separation; three-way wording rule (below-floor `not resolvable`;
above-floor non-directional `unresolved`/no directional claim; equivalence
only via a predeclared gate); permutation checks follow the actual
randomization scheme within exchangeable strata (minimum 6 blocks);
leave-one-out influence checks at n<=10 with defined triggers. Analysis
plans gain required fields family_id / claim_role / selection_scope /
multiplicity_rule; the registry is FROZEN before campaign execution with an
enumerated complete contrast_id set (exact Holm/BH denominators); post-hoc
claims are exploratory. AP-1..AP-6 carry seeded family values; AP-5 BH
sweeps are restricted to correctness/metadata (item-window energy stays
exploratory). This amends D-014's protocol wording; D-014's repetition
counts and outlier never-silently-drop rules stand.

Consequences: the claims-index linter (future) refuses L2/L3 without these
fields; campaign execution requires a frozen registry snapshot.

## D-054: False-effect guard floor and unknown-term claim-ceiling policy

- Date: 2026-07-09
- Status: accepted (promotes stream-ledger P15-7)
- Phase: 2 / measurement

Context: C-023 finding B1 (no metrological error budget); counterreview R2
killed the drafted percentile-UCB floor (unidentifiable at n=10: the sample
maximum exceeds the true 95th percentile only 40.1% of the time; a
nonparametric 95/95 bound needs n=59). Stream ledger:
`docs/stream_logs/2026-07-09-p2015.md` (P15-7; P15-2/P15-6 superseded).

Decision (PR #31): `docs/phase_2/detection_floor.md` is the P2-015 design.
Floors are FALSE-EFFECT GUARD FLOORS — max(largest observed absolute
residual/contrast, Student-t prediction bound for one new observation) —
with bootstrap as sensitivity only and a pre-registered small-sample guard
factor at 5<=n<10. Error-budget terms are enumerated per
backend x metric x window class; UNKNOWN terms cap claim level (they do not
block L0/L1 operation). Variance and deterministic bounds propagate
separately (drift is a bound unless a distributional model is justified).
Wall/USB-C PD calibration runbooks are pre-registered as bridge-model fits
(slope/intercept over workload-induced deltas), not absolute-delta
acceptance. Window-B revalidation: stale floors cap affected claims until
topped up.

Consequences: P2-015 campaign sizing is derivable from the economics table
(170-340 bundles); claim tooling must consume floor rows + error-budget
fields per the analysis registry (D-053).

Amendment (2026-07-09, C-027 sweep adjudication): 170 bundles is the
minimum Window-A request/phase subset; 180-340 is the total campaign
including the required Window-B revalidation cell (economics table,
`docs/phase_2/detection_floor.md`). Prose citing either number must name
which scope it means.

## D-055: Research-question registry is the canonical live index

- Date: 2026-07-09
- Status: accepted (promotes stream-ledger RQ-1)
- Phase: cross-phase / research bookkeeping

Context: C-023 finding B3 — the same question existed as promoted Q, banked
item, capability-map row, and C5 tier row with no alias normalization.
Stream ledger: `docs/stream_logs/2026-07-09-rqreg.md`.

Decision (PR #32): `docs/research_question_registry.md` is the canonical
LIVE index of question status, aliases, type, claim ceiling, forbidden
upgrade, AP/campaign owners, gate class, and pre-hardware preparability
(75 rows). `docs/research_question_bank.md` remains the historical and
deliberative record — single-writer split. The registry indexes ratified
council decisions; it never re-decides them. C-023 coverage gaps enter as
`candidate (C-023)` rows.

Consequences: promotion/status changes edit the registry (with the bank
still holding deliberation); front-facing docs point at the registry for
current state; the future claims-index linter consumes registry columns.

## D-056: Suite order policies and order_row provenance

- Date: 2026-07-09
- Status: accepted (promotes stream-ledger P30-1..P30-3; additive amendment to D-045.6)
- Phase: 2 / suite execution

Context: C-015 promised round-robin/Latin-square rotation; the sequencing
spec executed manifest_order (C-023 M2, pre-campaign blocker). Design round
ratified in `docs/stream_logs/2026-07-09-p2030.md` before implementation.

Decision (PR #34): `execution_policy.order_policy` names an operational
policy from the closed set {manifest_order, block_round_robin_v1,
block_latin_square_v1 (Williams row-balanced)}; realized order is the pure
function realized_order(manifest, policy, order_row); order_row is
controller-derived (suite rep index), recorded in metadata.suite alongside
order_seed = sha256(suite_seed, policy, order_row) — the D-045.6 hash
surface gains order_row as a companion, additively. Rotation unit is the
contiguous block run; all-sentinel blocks are position-anchored;
item_index stays manifest identity, position is the realized ordinal.
Strict validation recomputes the expected permutation AND the order_seed
fail-closed when order_row is present; legacy bundles without order_row
stay valid. Pinned generated manifests keep manifest_order byte-identical.
Reports/tooling surface manifest_order wording when rotation is absent.
Within-block item rotation is a named deferred revisit.

Consequences: suite campaigns can execute the C-015 rotation promises with
auditable order provenance; campaign-level config ordering remains
order_manifest.json (a distinct mechanism — see the campaign-packs README
operator note).

## D-057: Uncertainty terms — drift is a bound; claim-gate reason codes are stable vocabulary

- Date: 2026-07-09
- Status: accepted (promotes stream-ledger P29-2/P29-3)
- Phase: 2 / measurement

Context: P2-029 (PR #33) implemented detection_floor.md §3 (D-054).

Decision: (a) idle drift enters uncertainty accounting ONLY as a
deterministic bound (E_drift_bound_j in energy_bound_terms_j, from the
single documented evidence key idle_drift_bound_w) — never as a variance
term unless a distributional model is explicitly justified; no drift
magnitude is ever invented from cooldown flags (cap-hits add
claim-ineligibility reasons instead). (b) The claim_eligibility reason
codes (insufficient_in_window_samples, cadence_ratio_unrecorded/below,
clock_bound_unrecorded/exceeds_quarter_window, drift_term_unknown,
interpolation_bound_unrecorded/exceeds_floor, ...) are STABLE machine
vocabulary: consumers may match on them; changes require a decision-log
amendment. Single bundles are not_estimable; unknown gate inputs fail
machine-readably, never silently pass.

Consequences: claim tooling and the analysis registry consume these codes;
P2-015 floor artifacts plug into the same gate fields.

Amendment (2026-07-10, P2-040 / C-027 adjudication): the stable reason
vocabulary adds `nonpositive_window_duration` (the evaluated window has
duration `<= 0` and cannot bear a claim) and `idle_baseline_unrecorded` (an
idle-subtracted metric was requested without a valid recorded idle baseline).
Request gating is metric-specific: `gross_request` governs
`gross_energy_j` without idle-baseline or drift requirements, while
`idle_subtracted_request` governs `idle_subtracted_energy_j` and requires
both. The `request` gate remains a deprecated alias of
`idle_subtracted_request` through summary schema v0.1; removal waits for
schema v0.2.

Amendment (2026-07-10, P2-041 / C-027 adjudication): the closed v1
analysis/campaign consumer vocabulary is:
`analysis_manifest_invalid`, `analysis_manifest_not_frozen`,
`order_manifest_hash_mismatch`, `config_hash_mismatch`, `bundle_missing`,
`bundle_strict_invalid`, `bundle_status_not_succeeded`,
`metric_missing_or_nonfinite`, `paired_block_incomplete`,
`insufficient_complete_blocks`, `fixed_n_plan_incomplete`,
`window_evidence_precheck_missing`, `campaign_cooldown_evidence_missing`,
`idle_window_suspect`, `idle_window_suspect_unknown`,
`floor_artifact_invalid`, `floor_row_missing`, `floor_row_ambiguous`,
`floor_row_stale`, `floor_transport_inapplicable`, `floor_abs_missing`,
`floor_cmp_missing`, `effect_not_above_floor`,
`interpolation_bound_exceeds_floor`,
`interpolation_bound_exceeds_half_effect`,
`deterministic_bound_obscures_direction`, `required_error_term_unknown`,
`required_covariance_unknown`, `runtime_token_denominator_required`,
`stop_reason_required`, `output_policy_required`,
`tokenizer_identity_mismatch`, `multiplicity_family_incomplete`,
`multiplicity_not_rejected`, `equivalence_margin_not_above_floor`,
`equivalence_not_supported`, `randomization_check_insufficient_blocks`,
`randomization_sensitivity_disagrees`, `loo_verdict_influential`,
`loo_magnitude_influential`, `outcome_dependent_top_up`, and
`legacy_l1_mechanics_only`. Additions or spelling changes require a
versioned amendment. P2-041 copies reducer reasons verbatim, uses the
campaign-specific subset above, and never treats absent/null cooldown state
as recovery. The Component C5 `window_evidence_precheck` migration and
generic-alias removal supersede only D-057's historical field name and the
preceding amendment's alias-retention wording; its metric-specific reason
semantics remain binding.

Amendment (2026-07-11, P2-037 / C-028 analysis-trio adjudication): the
analysis engine adds the following exact closed v1 reason vocabulary. Consumers
may match these strings; additions or semantic changes require another
versioned amendment:

```text
analysis_manifest_invalid
analysis_manifest_not_frozen
order_manifest_hash_mismatch
config_hash_mismatch
bundle_missing
bundle_strict_invalid
bundle_status_not_succeeded
metric_missing_or_nonfinite
paired_block_incomplete
insufficient_complete_blocks
fixed_n_plan_incomplete
window_evidence_precheck_missing
campaign_cooldown_evidence_missing
idle_window_suspect
idle_window_suspect_unknown
floor_artifact_invalid
floor_row_missing
floor_row_ambiguous
floor_row_stale
floor_transport_inapplicable
floor_abs_missing
floor_cmp_missing
effect_not_above_floor
interpolation_bound_exceeds_floor
interpolation_bound_exceeds_half_effect
deterministic_bound_obscures_direction
required_error_term_unknown
required_covariance_unknown
runtime_token_denominator_required
stop_reason_required
output_policy_required
tokenizer_identity_mismatch
multiplicity_family_incomplete
multiplicity_not_rejected
equivalence_margin_not_above_floor
equivalence_not_supported
randomization_check_insufficient_blocks
randomization_sensitivity_disagrees
loo_verdict_influential
loo_magnitude_influential
outcome_dependent_top_up
legacy_l1_mechanics_only
```

Reducer-owned precheck reasons remain copied verbatim. Unknown reasons and
unknown covariance/term provenance fail closed rather than acquiring a local
alias or zero value.

## D-058: Token-normalization and stack-identity contract adopted

- Date: 2026-07-09
- Status: accepted (promotes stream-ledger P31-1)
- Phase: cross-phase / claims

Decision (PR #35): `docs/contracts/token_normalization.md` is binding for
token-denominated metrics and stack identity on all claims-ladder-governed
surfaces: request energy primary; J/token tokenizer-scoped with
runtime-observed denominators; cross-tokenizer/model-family comparisons
require companion denominators (J/char, J/byte, semantic-pair) or must
avoid efficiency-ranking language (enforceable forbidden-phrase list); the
11-field stack-identity table (hardware unit, OS, runtime, kernel/library,
model artifact hash, quantization, tokenizer identity incl.
prompt_source/bos_present, sampler/output policy, batching/concurrency —
always applicable, boundary label, telemetry backend) with the table-wide
rule: every field is a concrete value or an explicit unavailable/unknown;
silent omission is non-compliant.

Consequences: the L4-review stack-confound and J/token-comparability
attacks now have a binding answer; figures/captions compose with
capstone_scope single-unit language.

## D-059: Claims-lint mechanical enforcement in CI

- Date: 2026-07-09
- Status: accepted
- Phase: cross-phase / claims tooling

Decision (PR #37 + integration fix): `scripts/claims_lint.py` is the
mechanical enforcement layer for the claims discipline — AP-row
required-field/registry-field completeness (17-field contract, hard errors
on malformed rows, strict multiplicity forms), registry integrity (closed
sets incl. pre_hardware_preparable, duplicate IDs, AP-owner existence),
campaign-pack draft AP linting (marker-gated; index/README files exempt),
and a warning-only forbidden-language scan. A unittest lints the live repo
in CI: breaking an AP row or the registry fails the build. The linter
satisfies the C-023 cut-line condition for structural claim checks; the
Phase 4 claims-index mode extends this tool rather than a new one.

Consequences: the D-053 freeze discipline and D-055 registry are now
machine-checked.

Amendment (2026-07-11, P2-037): `claims_lint` gains an explicit
`claim-index` mode over the canonical Phase-4 JSONL. It verifies the linked
`joulewise.claim_verdicts.v1` bytes, canonical ID, AP/contrast/role/outcome,
manifest/floor/bundle provenance, D-062 demotion, sensitivity caveats, and
claim-level ceiling. The single pre-P2-037 manual-review L1 row is
grandfathered only under its exact canonical row identity/hash and emits a
warning; it does not become engine-supported evidence.

## D-060: Depth-before-breadth stop line (RATIFIED)

- Date: 2026-07-09; RATIFIED by Ed 2026-07-10 as written (C-028 session,
  live decision; the independent hardening proposal's convergent freeze
  recommendation was noted at ratification)
- Status: **accepted** (C-027 council recommendation; allocates
  Ed-facing work, so Ed ratifies or amends)
- Phase: cross-phase / project management

Proposal (C-027; amends D-041/D-052 sequencing and extends R-012/R-018):
no NEW breadth — new campaign packs, registry expansion, site features,
meta-process growth — until four gates pass:

1. Grading rubric + calendar captured by a hard date; if the program
   stays silent past it, adopt and RECORD a provisional grading contract
   with conservative internal deadlines (external silence triggers scope
   fallback, never indefinite paralysis).
2. Off-machine backup with a restore proof, before any NEW irreplaceable
   campaign evidence is retained (P0-003). Does not block report
   drafting, analysis tooling, or correctness fixes.
3. Window A complete in the C-027 sense: smoke, frozen sampling rule and
   guard factor (P2-039), production uncertainty evidence (P2-038),
   versioned floor artifact, floors, baselines — with the executable
   contrast/claim path (P2-037) before any L2 interpretation.
4. One end-to-end vertical slice: report source skeleton + reproducible
   bundle→analysis→figure→claims-row→report-page path (RPT-001).

Application note (2026-07-11, C-028 closeout): gate 2 is satisfied by the
verified iCloud backup and byte-identical strict-valid restore. The software
prerequisites inside gate 3 are also satisfied: P2-039, P2-038, and the
P2-042→P2-041→P2-037 analysis trio are merged, with reducer dispatch current
through 0.4.2. Gate 3 itself is not complete because Window-A smoke, floors,
and baselines have not executed. That execution is a quiet-machine + Ed
action; no landed-software statement raises its claim level or promotes the
PROVISIONAL NVIDIA pins.

Work that CLOSES these gates, correctness defects, report writing, and
already-obligated hardware preparation are always permitted.

Alternatives considered: status quo (rejected — C-027/NEGSPACE evidence:
six real bundles vs ~6M tokens of same-day breadth work); a blanket
freeze including correctness work (rejected — would block the gates'
own prerequisites).

## D-061: Review-layer evaluation rule v2 (replaces the two-zero-sessions drop rule)

- Date: 2026-07-09
- Status: accepted (C-027; process-layer, within council authority)
- Phase: cross-phase / process instrumentation

Context: the "drop a layer after two zero-catch sessions" rule was
falsified by its own record — integration review returned zero unique
catches twice (C-017, CP-5) and then caught five real cross-stream seams
(C-024). Mechanical application would have deleted the layer immediately
before its highest-value session.

Decision: layer evaluation uses (a) applicability decided by
PRE-DECLARED mechanical predicates (e.g. integration review counts only
when 2+ independently developed streams merge touching a shared
contract/consumer/generated artifact), never post-hoc judgment; (b) an
outcome taxonomy separating accepted-unique-defect / duplicate /
clean-verification / false-positive-suppression — suppression is
valuable but is not a catch; (c) fixed severity weights declared before
the session; (d) three applicable exposures TRIGGER an expected-loss
review decision, never automatic deletion; (e) safety, final-head, and
integration layers are never auto-dropped on zero-defect streaks —
they are judged by expected-loss reduction.

Alternatives considered: keep the two-zero rule (falsified); "three
applicable sessions, severity-weighted" as free-text judgment (rejected
in council — reintroduces the discretion that made the old rule
unfalsifiable).

## D-062: Confirmatory sampling policy — fixed n, explicit demotion, no silent top-ups

- Date: 2026-07-09
- Status: accepted (C-027; scientific protocol, ratifies the RIGOR/STATS
  adjudication; amends the top-up language in
  `docs/contracts/analysis_plans.md` — AP-EDIT applies the text)
- Phase: cross-phase / statistical protocol

Context: the analysis plans repeatedly started at n=5 and added
repetitions when an observed CI was near-floor or unsatisfactory, then
reported ordinary 95% CIs. Outcome-dependent sample growth invalidates
nominal coverage (C-027 RIGOR finding, adjudicated with the peer's
counterreview).

Decision: (a) confirmatory contrasts use n FROZEN before observing that
pack's effects, sized from Window-A variance/MDE evidence — nearer 10
than 5 for near-floor comparisons; (b) predeclare replacement rules for
technically invalid runs (they are not top-ups); (c) any
outcome-dependent top-up permanently DEMOTES that contrast to
exploratory: the original fixed-n analysis is reported regardless of
direction, pooled estimates are never presented as retaining nominal
confirmatory coverage, and no later convenience re-promotes the claim;
(d) a pre-registered two-look alpha-spending design (frozen max n, look
boundaries, spending function) is PERMITTED for a specifically justified
expensive campaign, never the default.

Alternatives considered: full group-sequential machinery as default
(rejected — avoidable defense surface for a capstone); status quo
(rejected — statistically invalid).

## D-063: Process architecture v2 — machine-readable state kernel first

- Date: 2026-07-09
- Status: accepted (C-027; process-layer)
- Phase: cross-phase / process architecture

Context: five core process files grew 3,106 → 4,893 lines with ~9.5k net
process/history lines since orchestration landed; the same-day RUN_STATE
dual next-action drift (C-027 B3) is the demonstrated failure mode of
hand-maintained state mirrors.

Decision (staged; big-bang migration rejected by both council sides):
Stage 1 (DOC-008) = a thin machine-readable state kernel (task id, lane,
status, dependencies, authority pointer, acceptance pointer, stop-card
pointer) from which the RUN_STATE restart block and the live queue view
are GENERATED; PROJECT_STATUS compaction with a status-history archive;
retire `docs/planning_reflection_protocol.md` as standalone intake
(zero credited catches across four recent sessions — its useful fields
fold into queue rows); the two-writer rule and credential-boundary push
procedure move into `docs/orchestration.md`. Stage 2 = per-session
findings/invocations ledgers making "unique catch" a query (extends
D-050). Policy-doc generation comes LAST — supersession requires
semantic judgment (council position, adopted from the peer's argument
over the lead's original ordering).

Alternatives considered: defer the kernel and generate
current_policy.md first (the lead's draft position — REVERSED in
council: it leaves the demonstrated drift mode active); full big-bang
migration (rejected: risks the drift it cures).

---

## Index row

| D-064 | Delegated-invocation compliance surface: tracked per-session JSONL event stream, canonical report envelope, enforced write scope | accepted |

---

## D-064: Delegated-invocation compliance surface — tracked JSONL event stream, report envelope, enforced write scope

- Date: 2026-07-11 (core surface adjudicated 2026-07-10, C-028 H4;
  v3/envelope/scope clauses ratified after landing in the C-028
  infrastructure wave)
- Status: accepted (C-028; process-layer)
- Phase: cross-project process instrumentation

Context: D-050 requires substantial delegated runs to leave a
process trace and an invocation-manifest pointer map. The C-027
audit showed a gitignored bridge manifest cannot serve as
repository-auditable evidence, and that run-report summaries had
collapsed roughly one hundred invocations into zero auditable
per-invocation rows. The D-050 revisit condition fired at
CP-5/C-022 and is adjudicated here through MET-001 option 2 and
C-028 H4. During the C-028 arc the surface was then exercised in
production: a wrapper crash mid-run (lead in-place edit of the
installed runner) and two out-of-scope diffs (p2043-impl,
p2044-fixround) tested the recovery and enforcement semantics now
ratified below.

Decision:

1. **Compliance surface.** One tracked, append-only JSONL manifest
   per substantial session under `docs/process_traces/`, with rows
   for every actual invocation. Failed, capacity-ended, resumed,
   and retried invocations get their own rows; resumes may share a
   model session ID but never an invocation row. Run reports carry
   only counts plus a link to the tracked manifest. The codex-run
   observer index and raw logs remain recovery substrate, never
   the compliance surface; the gitignored bridge manifest remains
   local convenience only.

2. **Manifest v3 is an append-only EVENT STREAM, not a mutable
   ledger.** Three event kinds: `run_started` (wrapper-authored at
   dispatch: prompt hash/bytes, contract, genre, write scope,
   head/branch at start), `run_finished` (wrapper-authored at
   exit: invocation state, report parse validity, semantic
   status/completion, finding/verification counts, scope-violation
   counts, head at end), and `run_consumed` (LEAD-authored at the
   moment the lead dispositions the output: consumed / rejected /
   deferred, with pointer). Consumption events are lead-owned
   exclusively — a wrapper or delegated session never writes them.
   Emitted rows are never mutated, rewritten, or deleted;
   corrections are new rows. When the wrapper dies without writing
   `run_finished`, the LEAD authors a recovery `run_finished` row
   that says so explicitly (`error_stage`, a note naming the
   failure, and any manually-performed classification) — silent
   reconstruction that imitates a normal wrapper row is forbidden.
   Two live defects were found on day one — a resume no-op after a
   NEEDS_SCOPE early-return, and an in-place-edit crash hazard now
   covered by the atomic-mv install rule — and both are recorded
   in the adapter's operational lessons.

3. **claude-codex-report/v1 is the canonical session report.**
   Every delegated session returns the envelope: machine-parsed
   header (run status, completion, finding counts by severity,
   verification results, scope-deviation flags) over a prose body.
   `run_finished` records the parse verdict and the extracted
   counts. A session without a valid envelope is not consumable as
   review or implementation evidence — it is raw substrate pending
   a lead ruling or a re-run. NEEDS_RULING early-returns are
   compliant envelopes, not failures.

4. **WRITE_SCOPE is enforced, not advisory.** Each invocation
   declares its write scope up front; the runner diffs the
   worktree against that scope after the run. On violation the
   runner exits 77, the out-of-scope work is PRESERVED in an
   evidence bundle (status `failed_preserved`) and is never
   landed; the lead inspects the bundle and decides. A session
   that discovers it needs wider scope returns NEEDS_SCOPE as a
   structured request; scope expansion is PROSPECTIVE ONLY — a new
   invocation with the widened scope — never a retroactive
   blessing of an already-out-of-scope diff. WRITE_SCOPE strictly
   overrides any in-repo end-of-work instruction (AGENTS.md
   precedence section, per the CI-002 root cause).

This amends and supersedes only D-050's invocation-manifest
compliance-surface clause. D-050's stop-card authority,
process-trace obligation, and raw-log pointer policy are
unchanged. v2 single-row-per-invocation snapshots remain valid
evidence for pre-v3 invocations; new sessions emit v3.

Alternatives considered:

1. Run-report invocation summary as the surface. Rejected:
   summarization destroyed per-invocation auditability — the exact
   failure MET-001 exists to repair.
2. Gitignored live bridge manifest as the authority. Rejected:
   structurally local-only; unignoring a shared live file creates
   multi-worktree contention and dirty-tree noise.
3. Mutable per-invocation rows updated in place (start → finish →
   disposition on one row). Rejected: in-place mutation destroys
   the append-only audit property, makes wrapper crashes
   indistinguishable from clean rows, and invites silent
   retro-editing; the event stream keeps every state transition
   and its author.
4. Free-form final messages as session reports. Rejected:
   unparseable; counts and scope flags cannot be mechanically
   extracted into `run_finished`.
5. Advisory-only write scope (prompt-level restriction without a
   runner backstop). Rejected: the CI-002 deviation demonstrated
   that in-repo end-of-work instructions override polite prompt
   scoping; enforcement must be structural, with the work
   preserved rather than discarded so enforcement never destroys
   evidence.

Consequences: session closeout must land the tracked manifest(s)
before bookkeeping is declared complete; every `run_started` must
be closed by a wrapper or lead-authored `run_finished` and a
lead-authored disposition, with missing rows recorded as missing,
never inferred from aggregates. D-063 Stage 2 may generate queries
and projections over these files but may not replace the row-level
source. Council-log layer-yield claims (D-061) should cite manifest
rows.

Revisit when: three substantial sessions have landed v3 manifests;
or the one-file-per-session scheme shows material contention or
ambiguity; or `run_consumed` coverage proves too burdensome to
sustain (in which case narrow the event, do not revert to mutable
rows).

---

## Adjudication note (was: drafting notes for the lead)

Lead-adjudicated 2026-07-11: accepted as drafted. The date
(2026-07-11 with the 07-10 H4 parenthetical), the "Status: accepted
(C-028; process-layer)" voice, the clause-2 recovery-row
generalization from the live p2037-fixround recovery row
(`error_stage: wrapper_crash_lead_inplace_edit`), the clause-4
exit-77/`failed_preserved` semantics (verified against the live
p2043-impl / p2044-fixround status files), and the v2-valid-for-
pre-v3 transition sentence all stand. One addition per lead
dictation: the day-one-defects sentence appended to clause 2.
