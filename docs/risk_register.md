# Risk Register

Living register of risks that could sink, delay, or weaken the capstone.
Review at the start of every phase and whenever a trigger fires; update
statuses at the end of substantial runs alongside `RUN_STATE.md`.

Conventions:

- Likelihood/Impact: low / medium / high, judged against the current phase.
- Trigger: the observable event that means the risk is materializing.
- Mitigation: what we do *now* to reduce likelihood or impact.
- Fallback: what we do *if it happens* - every fallback must preserve a
  publishable result, even if smaller.
- Owner: `user` for actions needing human/lab/supervisor access, `agent` for
  repo work.

## Summary

| ID | Risk | Phase | Likelihood | Impact | Status |
|---|---|---|---|---|---|
| R-001 | Supervisor approval delayed or scope shifts | 1 | medium | high | open |
| R-002 | powermetrics sudo workflow not approved on measurement Mac | 2 | low | high | closed-residual |
| R-003 | MLX install or model-load failure on Mac | 2 | low | medium | closed-residual |
| R-004 | KV persist/resume unsupported in a target runtime | 3 | medium | high | open |
| R-005 | llama.cpp cache files not portable across machines/backends | 3 | medium | high | open |
| R-006 | 3080 Ti borrow window slips or shrinks | 3 | medium | medium | open |
| R-007 | No wall meter available | 1-4 | medium | medium | open |
| R-008 | Orin telemetry inaccessible | 2-3 | medium | low | open |
| R-009 | Hailo cannot run LLM-shaped workloads | 1 | high | low | open (by design) |
| R-010 | Controller-as-DUT contamination on Mac runs | 2 | high (unmitigated) | medium | mitigated by D-013 |
| R-011 | Benchmark network cannot be isolated | 3 | medium | medium | open |
| R-012 | Schedule: five phases vs fixed academic deadlines | all | medium | high | open |
| R-013 | Thermal throttling confounds measurements | 2-4 | medium | medium | mitigated by D-014 |
| R-014 | Model weights become unavailable or gated | 2+ | low | medium | open |
| R-015 | Schema changes after data collection starts | 2+ | low | high | mitigated |
| R-016 | Measurement-corpus loss (`runs/` has no backup path) | 2-5 | low | high | mitigated-interim (protocol + restore test 2026-07-06; final destination pending user) |
| R-017 | Repo on iCloud-synced Desktop (EPERM lock recurrence) | all | low | medium | mitigated (repo moved 2026-07-05; residual: session launch paths) |
| R-018 | Agent-loop self-expansion consumes calendar without grader-facing output | all | medium | high | open (C-027; D-060 stop line proposed as mitigation) |

## R-001: Supervisor approval delayed or scope shifts

- Phase: 1. Likelihood: medium. Impact: high (wrong deliverable built).
- Trigger: Phase 2 implementation slices ready to start (2A-2F complete)
  with P1-001 still open; or any supervisor communication contradicting
  `AGENT_PLAN.md` scope.
- Status note (2026-07-05): the first trigger fired 2026-06-12 (2A-2F
  completed with P1-001 still open). The mitigation is holding as
  designed - all work since has been hardware-independent and
  harness-shaped (mock slice, docs, Slice 2N is next and is also
  ungated) - and the fallback ("continue only mock/local work; hardware
  purchases/borrows blocked-on-approval") is effectively in force.
- Mitigation: the queue keeps P1-001 ranked first; all work until approval
  stays hardware-independent and harness-shaped (valuable under any scope);
  the Phase 1 exit checklist lists the exact questions to put to the
  supervisor so one meeting can close the gate.
- Fallback: if approval stalls past mock-slice completion, continue only
  mock/local work and mark every hardware purchase or borrow decision
  blocked-on-approval.
- Owner: user.

## R-002: powermetrics sudo workflow not approved on measurement Mac

- Phase: 2. Likelihood: low (user controls the machine; a local auth
  session needs rescheduling - the planned 2026-06-10 slot passed without
  one). Impact: high (no Mac telemetry = no flagship vertical slice).
- Status: closed-residual (2026-07-08). The working Mac slice completed
  2G/2H/2I on 2026-07-06 with privileged powermetrics capture and
  strict-valid bundles; revisit for new macOS/MLX/powermetrics versions or
  new Mac hardware.
- Trigger: scoped sudoers rule (D-004) cannot be installed, or privileged
  sample capture fails after the auth session.
- Mitigation: D-004 defines a minimal, single-binary sudoers rule with the
  exact line documented in the Phase 1 exit checklist's instrumentation
  section; interactive-sudo manual fallback documented for attended runs.
- Fallback: attended runs with interactive sudo (operator present per
  experiment); if even that is unacceptable, the Mac becomes
  runtime-supported/telemetry-blocked and the first real slice moves to the
  first available CUDA target - recorded as a finding, not hidden.
- Owner: user (install rule), agent (pre-check + structured failure).

## R-003: MLX install or model-load failure on Mac

- Phase: 2. Likelihood: low. Impact: medium (delays flagship slice).
- Status: closed-residual (2026-07-08). The working Mac slice completed
  2G/2H/2I on 2026-07-06 with MLX generation and strict-valid bundles;
  revisit for new MLX/mlx-lm versions or new Mac hardware.
- Trigger: `pip install mlx mlx-lm` fails, or the chosen model (D-016) has
  no working MLX artifact.
- Mitigation: install into a dedicated venv with versions recorded in run
  bundles; model criteria (D-016) require known MLX availability before
  selection; smoke-test load before scheduling measurement sessions.
- Fallback: llama.cpp with the Metal backend as the Mac runtime (already a
  planned runtime for split portability under D-015); the MLX adapter then
  becomes optional rather than flagship.
- Owner: agent (with user approving installs).

## R-004: KV persist/resume unsupported in a target runtime

- Phase: 3. Likelihood: medium overall (high for vLLM file-based replay,
  low for llama.cpp, low-medium for mlx-lm). Impact: high if unmitigated -
  this is the project's central feasibility risk.
- Trigger: a Stage 3.0 spike returns `replay_unsupported` for a runtime
  needed by a planned pairing.
- Mitigation: D-015's feasibility ladder - spikes run *before* any split
  hardware time is scheduled; pairings are planned only on runtimes with
  `replay_supported` verdicts; the synthetic transfer microbenchmark
  (Stage 3.1) is independent of all runtime cooperation and guarantees a
  crossover dataset.
- Fallback: analytical composition - measured prefill energy (node A) +
  measured synthetic transfer energy (payload sized by the KV model) +
  measured decode energy (node B) bounds the split cost honestly; the report
  states the composition method explicitly.
- Owner: agent.

## R-005: llama.cpp cache files not portable across machines/backends

- Phase: 3. Likelihood: medium (session files are version- and
  model-sensitive; cross-backend CUDA-save -> Metal-load is unverified).
  Impact: high for *heterogeneous* pairings specifically.
- Trigger: Stage 3.0.2's cross-machine restore test fails or produces
  divergent output.
- Mitigation: the spike tests cross-machine restore explicitly, with pinned
  identical llama.cpp versions and identical GGUF files on both ends, before
  any heterogeneous experiment is scheduled.
- Fallback: restrict offline-replay pairings to same-platform pairs
  (GPU->GPU in the borrow window, Orin->Orin); cover heterogeneous pairs
  with the analytical composition (R-004 fallback); report the portability
  finding itself - it is a legitimate disaggregation-practicality result.
- Owner: agent.

## R-006: 3080 Ti borrow window slips or shrinks

- Phase: 3. Likelihood: medium. Impact: medium (loses GPU->GPU pairing, not
  the phase).
- Trigger: window not scheduled by Phase 3 Stage 3.2 completion; or window
  arrives before split tooling is ready.
- Mitigation: all split tooling reaches rehearsed-on-available-hardware state
  before the window (the Phase 3 plan keeps a borrow-window runbook so
  borrow time is execution-only, no debugging); calendar mapping task
  (P1-008) makes the window a tracked date.
- Fallback: GPU->GPU pairing drops to single-GPU prefill/decode phase
  decomposition plus analytical composition; 3050<->Orin and Orin<->Orin
  remain.
- Owner: user (scheduling), agent (runbook readiness).

## R-007: No wall meter available

- Phase: 1-4. Likelihood: medium. Impact: medium (boundary calibration and
  Pi/Hailo coverage lost; per-target results stand).
- Trigger: P1-003 resolves "unavailable".
- Mitigation: P1-003 is a Phase 1 gate precisely so this resolves before it
  matters; D-018's boundary table makes results honest without a meter.
- Fallback: report within-target comparisons (always boundary-consistent)
  as primary; flag cross-target absolute comparisons with the boundary
  caveat; targets with no platform telemetry (Pi) become
  telemetry-unavailable findings.
- Owner: user.

## R-008: Orin telemetry inaccessible

- Phase: 2-3. Likelihood: medium (rail sysfs paths vary by L4T version).
  Impact: low (one target of several).
- Trigger: P1-006 evidence shows neither INA3221 sysfs nor tegrastats usable.
- Mitigation: two candidate mechanisms documented before hardware time;
  wall-meter fallback if R-007 resolves positively.
- Fallback: Orin runs runtime-only (latency/throughput) marked
  telemetry-unavailable, or drops to a stretch target.
- Owner: user (access), agent (adapter).

## R-009: Hailo cannot run LLM-shaped workloads

- Phase: 1. Likelihood: high. Impact: low - *by design*: the plan treats
  Hailo as a feasibility investigation whose negative verdict is itself a
  reportable applicability finding.
- Status: **realized as expected, 2026-06-12** — verdict
  `unsupported_workload`. The trigger fired (a non-`supported` verdict),
  the by-design mitigation held, and the outcome is the publishable
  applicability finding the plan anticipated. No schedule impact.
- Trigger: feasibility checklist closes with any non-`supported` verdict.
  (Fired 2026-06-12.)
- Mitigation: none needed; the verdict-code structure in the Phase 1 exit
  checklist's Hailo section makes the outcome publishable either way. Do
  not spend implementation effort on a Hailo backend (the verdict is now
  recorded; the standing do-not-do-yet rule becomes "report, don't
  implement").
- Fallback: Pi 5 CPU-only llama.cpp with wall-meter telemetry becomes an
  optional low-power data point if the meter exists; otherwise Pi/Hailo
  appears only in the applicability table.
- Owner: user (device access), agent (verdict documentation - done).

## R-010: Controller-as-DUT contamination on Mac runs

- Phase: 2. Likelihood: high if unmitigated. Impact: medium (biased flagship
  numbers).
- Status: mitigated by D-013 (idle baseline includes resident quiescent
  controller; deferred logging; blocking wait during measured window).
- Trigger (residual): SSH-controlled comparison runs (once transport exists)
  show a delta beyond run-to-run variance.
- Fallback: move Mac headline measurements to remote-controlled runs.
- Owner: agent.

## R-011: Benchmark network cannot be isolated

- Phase: 3. Likelihood: medium (campus/home network constraints unknown
  until P1-004 closes). Impact: medium (noisy transfer measurements).
- Trigger: P1-004 topology answer shows shared links only.
- Mitigation: prefer direct node-to-node cabling (no switch) for 1GbE/2.5GbE
  point-to-point tests - removes the isolation question entirely for
  two-node experiments; record link conditions per run in the bundle.
- Fallback: run sweeps off-hours, repeat n>=5, report observed throughput
  alongside nominal link speed (the bundle already records measured
  throughput per D-008's transfer block).
- Owner: user (hardware), agent (recording).

## R-012: Schedule: five phases vs fixed academic deadlines

- Phase: all. Likelihood: medium. Impact: high (capstones fail by calendar,
  not by code).
- Trigger: any phase exceeding its (to-be-set) calendar budget; colloquium
  or report dates announced (P1-008) leaving less runway than the plan
  assumes.
- Mitigation: P1-008 maps phases to real dates as soon as the user supplies
  them (`docs/milestones.md` holds the skeleton); every phase defines a
  hardware-independent floor and a descope ladder so cutting is a decision,
  not a scramble.
- Descope ladder (worst-case minimum viable capstone, in cut order):
  1. Drop live split (3.3) - already stretch.
  2. Drop 10GbE and one model size.
  3. Drop heterogeneous replay pairs (keep synthetic transfer + analytical
     composition).
  4. Drop Orin/Pi targets (keep Mac + one CUDA).
  5. Floor: mock harness + Mac vertical slice + homogeneous baselines +
     synthetic interconnect sweep + analytical split model. This is still a
     complete, defensible benchmark-plus-study.
- Owner: user (dates), agent (floor discipline).

## R-013: Thermal throttling confounds measurements

- Phase: 2-4. Likelihood: medium (high on passively-cooled Orin/Pi).
  Impact: medium (rep-to-rep drift, biased late reps).
- Status: mitigated by D-014 (idle-power recovery gate between reps,
  thermal_drift_c in measurement quality, interleaved ordering) - residual
  risk on targets without thermal sensors.
- Trigger: thermal_drift_c trending across reps, or cooldown cap hits
  recorded in bundles.
- Fallback: longer cooldowns, active cooling notes recorded in run metadata,
  or excluding throttled reps *with documented cause* per D-014.
- Owner: agent.

## R-014: Model weights become unavailable or gated

- Phase: 2+. Likelihood: low. Impact: medium (mid-project model swap breaks
  comparability).
- Trigger: chosen model's hub entry gated/removed; license terms change.
- Mitigation: D-016 requires mirroring chosen weights to local storage
  immediately on selection, with revisions and hashes recorded.
- Fallback: promote the recorded fallback candidate; re-run affected
  baselines (the config hash separates old/new data cleanly).
- Owner: agent.

## R-015: Schema changes after data collection starts

- Phase: 2+. Likelihood: low. Impact: high (existing bundles unreadable or
  silently misread).
- Status: mitigated structurally.
- Mitigation: schema_version field exists from v0.1; D-008 plans the only
  anticipated breaking-shape change (v0.2) *before* split data collection;
  output-schema additions are additive-only (the JSON schema does not forbid
  additional properties); `validate-bundle` pins what a valid bundle means
  per version.
- Trigger: any proposed non-additive change to a schema with bundles already
  on disk.
- Fallback: a dated migration note in this repo plus a one-shot migration
  script; never edit bundles in place (they are evidence).
- Owner: agent.

## R-016: Measurement-corpus loss (runs/ has no backup path)

- Phase: 2-5. Likelihood: low. Impact: high (the dataset behind every
  claim is a gitignored directory on one disk; a disk failure or an
  errant delete erases the evidence the defense rests on, and hardware
  re-collection needs access windows that may not recur).
- Trigger: first real (non-mock) bundle written; any data-affecting
  incident (disk error, iCloud eviction anomaly, accidental delete).
- Mitigation: before the first real measurement session (gate on 2I data
  collection, tracked as queue task P0-002), define and record the backup
  protocol here: destination (external disk and/or cloud location outside
  the repo), cadence (after every measurement session), method (rsync of
  `runs/` plus experiment manifests), and a restore test performed once.
  Configs + manifests already make re-collection well-defined; backups
  make it unnecessary.
- **Protocol recorded (2026-07-06, P0-002 closed interim).** Destination:
  `~/JouleWise-backup` — a user-directed INTERIM location on the same
  disk ("cursory... I'll handle that later"); it protects against errant
  deletes but not disk failure, so the user still owes an external/cloud
  destination for full mitigation. Cadence: after every measurement
  session. Method: `scripts/backup_runs.sh [RUNS_DIR] [DEST]` (rsync -a,
  never `--delete`; dated UTC log line per invocation appended to
  `DEST/backup.log`). Restore test performed 2026-07-06: mock bundle
  backed up, restored to a temp dir, `validate-bundle` green on the
  restored copy. Swapping in the final destination is a one-argument
  change (or edit the script default) plus one fresh restore test.
- Fallback: re-run affected experiments from their configs (the config
  hash separates old/new data cleanly per D-005/D-010); report any
  unrecoverable gap honestly in the exclusion log.
- Owner: user (destination/media), agent (protocol doc + restore test).

## R-017: Repo lives on iCloud-synced Desktop (EPERM lock recurrence)

- Phase: all. Likelihood: low (mitigated; was high while on Desktop).
  Impact: medium (blocks work sessions mid-run; small integrity risk
  around eviction during writes).
- Status: **mitigated 2026-07-05** - the repo moved off the synced
  Desktop (current canonical path: `~/code/JouleWise`; the interim
  `~/code/CapstoneRivoire/Capstone` path recorded here was itself later
  renamed - corrected 2026-07-09, C-027). P0-001 complete; git + suite
  verified green at the new path. Residual exposure: agent sessions
  launched from the stale Desktop path (delete the leftover
  `~/Desktop/CapstoneRivoire` husk after relaunching from the new
  path), and any future placement of repo or `runs/` data under an
  iCloud-synced directory - do not.
- Trigger: any `Operation not permitted` on read/readdir inside the repo
  with the iCloud file provider (`bird`) active.
- History: first incident 2026-06-12 (documented in `RUN_STATE.md`);
  recurred 2026-07-05 mid-run - `docs/`, `joulewise/`, `tests/`, `.git`,
  and the repo root EPERM-locked intermittently during an active iCloud
  full-sync, clearing and re-locking per subtree. Both incidents match
  iCloud "Optimize Mac Storage" behavior on `~/Desktop/`. The move
  landed the same day as the second incident.
- Fallback: if a lock ever strikes again, wait for it to clear (both
  incidents did), then re-verify with the test suite before continuing;
  the remote (`origin/main`) bounds code loss to the working tree.
- Owner: user (launch paths), agent (post-lock verification discipline).

## R-018: The agent loop itself as a schedule and scope risk

- Phase: all. Likelihood: medium. Impact: high (capstones fail by
  calendar, R-012).
- Registered by C-027 (NEGSPACE lens finding accepted in council): the
  multi-agent workflow can remain locally productive - packs, registries,
  meta-process, site work - while the graded deliverable path (rubric,
  report source, backup, real corpus, figures) stays starved. Same-day
  evidence at registration: ~6M tokens of breadth work vs six real
  corpus bundles, no report source, same-disk backup.
- Trigger: an agent-heavy work block that produces neither a new real
  evidence bundle nor a report/figure increment.
- Mitigation: proposed D-060 depth-before-breadth stop line (awaiting
  Ed); RPT-001 vertical slice; the C-027 correctness rows ranked ahead
  of all breadth work.
- Owner: lead (queue discipline), Ed (D-060 ratification).
