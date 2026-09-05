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
| R-016 | Measurement-corpus loss (`runs/` has no backup path) | 2-5 | low | high | mitigated (2026-07-10: iCloud Drive destination live, fresh restore test passed; re-verify before each window — eviction caveat) |
| R-017 | Repo on iCloud-synced Desktop (EPERM lock recurrence) | all | low | medium | mitigated (repo moved 2026-07-05; residual: session launch paths) |
| R-018 | Agent-loop self-expansion consumes calendar without grader-facing output | all | medium | high | mitigated-in-policy (D-060 RATIFIED 2026-07-10; enforcement = queue discipline + spend guardrails, WO-022/R2, `docs/orchestration.md` §Spend guardrails) |
| R-019 | Pack-generator check-then-write boundary admits post-validation symlink substitution | 2+ | low | high | registered residual (D-141(i), cold gate 2026-08-18) |
| R-020 | Freeze loader accepts a hand-authored v1-schema receipt inside a `_v2` pack | 2+ | low | medium | registered residual (D-141(ii), delta-8 ratified 2026-08-18) |
| R-021 | Unattended-night automation fails while the operator is away | campaign | medium | high | mitigated-in-progress (D-169/D-171; rehearsal evidence in `RUN_STATE.md`) |
| R-022 | Unknown paper and evaluator dates leave no defensible schedule margin | paper | high until dates are recorded | high | open; `ED-DATES-01` owns the missing inputs |

## R-001: Supervisor approval delayed or scope shifts

- Phase: 1. Likelihood: medium. Impact: high (wrong deliverable built).
- Trigger: advisor feedback changes the permitted paper scope, required
  evidence, or evaluator acceptance bar; or those requirements remain
  unrecorded when a claim-bearing campaign decision depends on them.
- Status note: the Mac instrument and the real `powermetrics` evidence path
  exist. The live uncertainty is no longer whether Slice 2N may start; it is
  whether the `_v5` campaign and planned paper answer the advisor's required
  scope. Task `ED-DATES-01` still owns that external acceptance record.
- Mitigation: keep campaign claims inside the registered question and results-
  fill contracts; obtain the advisor/calendar answers through `ED-DATES-01` before
  making a schedule- or scope-dependent promise.
- Fallback: if the advisor narrows scope, preserve the admitted Mac campaign
  and remove unsupported extensions. Hardware purchases, borrowing, or new
  measurement scope remain blocked until explicitly approved.
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
  (`ED-DATES-01`) makes the window a tracked date.
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

## R-012: Schedule compression against the live campaign and paper

- Phase: campaign and paper. Likelihood: medium. Impact: high (a defensible
  result can still miss its academic deadline).
- Trigger: the evaluator dates become known with less runway than the live
  `_v5` sequence needs, or a prerequisite prevents the next campaign stage
  from entering its governed machine-state lane.
- Mitigation: `ED-DATES-01` records the real dates; `docs/milestones.md` shows the
  live dependency sequence; the state kernel prevents later work from
  borrowing an unmet gate.
- Descope ladder for the live paper, in decision-owned order:
  1. If G2-a cannot support a prefill arm, publish the D-166 refusal and do
     not lower the selection rule after observing the probes.
  2. If the registered timing-dominance test fails, withdraw the dominance
     sentence under D-165 and report only what the admitted component results
     support.
  3. Defer remote-hardware, split-inference, and broader stress-test extensions
     before cutting the governed Mac campaign's evidence and audit trail.
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

## R-016: Measurement-corpus loss or unavailable backup

- Phase: campaign and paper. Likelihood: low. Impact: high (the active corpus
  is gitignored working data; a disk failure, eviction, or errant delete can
  remove the evidence the defense needs, and hardware re-collection may not
  fit the remaining access window).
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
- **Protocol upgraded (2026-07-10/11, P0-003 closed; addendum 2026-07-16
  closing a summary-row/body drift found by the resumption audit).** The
  interim same-disk destination above is superseded: the external
  destination is iCloud Drive, live with a fresh backup + restore test
  passed (evidence: `docs/run_reports/2026-07-11-c028-continuation.md`
  §11, "The P0-003 iCloud measurement-corpus backup and restore gate is
  satisfied"). The 2026-07-06 entry above is retained as history.
  Standing caveat: iCloud eviction — re-verify the destination is
  materialized (fresh restore test) before each measurement window.
- Boundary clarification: this is a sanctioned **backup copy** outside the
  repository. It does not authorize running the live repository or the active
  measurement corpus from an iCloud-synchronized directory. R-017 continues
  to require those working paths to remain local and unsynchronized.
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
- This does not conflict with R-016: R-016 permits a separate iCloud backup
  copy; R-017 forbids an iCloud-synchronized live checkout or active corpus.
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
- Mitigation: D-060 depth-before-breadth stop line (RATIFIED by Ed
  2026-07-10) extended by the WO-022/R2 spend guardrails
  (`docs/orchestration.md` §Spend guardrails, 2026-07-15); RPT-001
  vertical slice; the C-027 correctness rows ranked ahead of all
  breadth work.
- Owner: lead (queue discipline + guardrail checkpoints), Ed (HARD
  bands and structure).

## R-019: Pack-generator check-then-write boundary admits post-validation symlink substitution

- Phase: 2+. Likelihood: low. Impact: high (a substituted write target could
  place generated pack bytes outside the intended pack root).
- Status: **REGISTERED RESIDUAL (2026-08-18)**, ratified at the
  freeze-semantics cold gate (D-141(i); composed verdict holding 5, record
  `docs/process_traces/2026-08-18-freeze-semantics-coldgate/`). Exploiting it
  requires a concurrent process racing the desk-time generation, which is
  excluded by single-operator generation discipline — D-139 A1 is cited **by
  analogy** here; A1's own scope is the measurement environment, not the
  generation desk. The *accidental* class is CLOSED: 16-case
  refuse-before-any-write coverage. Code comments are not registration; this
  row is.
- Trigger (reopening, cold ruling C-B1a): any threat-model revision admitting
  concurrent adversarial local processes, or multi-operator / shared-machine
  pack generation.
- Mitigation: single-operator desk-time generation discipline; the
  refuse-before-any-write validation set; the generators' preserve-mode
  default plus the successor-identity-only non-preserve shape.
- Fallback: implement the dirfd / `O_NOFOLLOW` write boundary (delta-4's F2
  remedy demand, formally SUPERSEDED at this gate per C-B1b) and regenerate;
  no published evidence depends on the current boundary.
- Owner: agent (boundary code + reopening watch), Ed (threat-model scope).

## R-020: Freeze loader accepts a hand-authored v1-schema receipt inside a `_v2` pack

- Phase: 2+. Likelihood: low. Impact: medium (chain authentication keys on
  the receipt schema, so a v1-schema receipt inside a successor pack would
  bypass the predecessor binding).
- Status: **REGISTERED RESIDUAL (2026-08-18)** under the trusted-operator
  model (D-141(ii)). Delta-8 attacked and ratified it: no crash path and no
  current-tooling path produces that state — mint selects the v2 schema
  before writing, and plan-tree updates are atomic. Reaching it requires a
  hand-authored receipt placed by the operator.
- Trigger: any tooling path that can emit or leave behind a v1-schema freeze
  receipt in a `_v2` (or later) pack; or a threat model that stops trusting
  the operator with pack-root contents.
- Mitigation: `_load_freeze_reference`'s schema-keyed chain authentication is
  reached only after the receipt is authenticated against the plan-tree pin;
  mint is v2-selecting pre-write; plan-tree attachment updates are atomic.
- Fallback: key the chain check on the pack generation (pack ID suffix)
  rather than the receipt schema, and re-verify the family's receipts; no
  published receipt is affected.
- Owner: agent.

## R-021: Unattended-night automation fails while the operator is away

- Phase: campaign. Likelihood: medium. Impact: high (a quiet-machine window
  may fail to start, run past its boundary, or fail to leave a trustworthy
  morning record).
- Trigger: the scheduler does not fire; the watchdog cannot establish the
  night's completion; an agent process is present at arm time; the plan points
  at a different checkout revision; or the results branch and morning notice
  do not agree.
- Mitigation: D-169 puts the unattended lane before the transaction. D-171
  adds the external supervisor and stand-down rule. The retained rehearsal
  evidence in `RUN_STATE.md` demonstrates scheduler launch, agent-present
  refusal, results-branch delivery, and morning notice; real collection still
  waits on the current plan-pin and supervisor gates.
- Fallback: refuse the night without reusing its arm, preserve the signed
  outcome, and require a fresh governed plan after the cause is identified.
  Never convert an unattended failure into an attended or retried claim run by
  convenience.
- Owner: lead (plan and evidence), user (the privileged installation step when
  a ruling requires it).

## R-022: Unknown paper and evaluator dates leave no defensible schedule margin

- Phase: paper. Likelihood: high until dates are recorded. Impact: high.
- Trigger: `ED-DATES-01` remains open while campaign or paper work is prioritized by
  an assumed submission, meeting, demonstration, or reproducibility date.
- Mitigation: `docs/milestones.md` records unknown dates as unknown and keeps
  the campaign order separate from calendar promises. `ED-DATES-01` obtains the
  evaluator's required figures, demonstration expectation, reproducibility
  threshold, and final dates.
- Fallback: protect the admitted `_v5` evidence chain and use the D-165/D-166
  withdrawal branches; defer extension claims before weakening metrology or
  inventing a date.
- Owner: user (external dates and evaluator requirements), lead (honest
  schedule and descope once those inputs exist).
