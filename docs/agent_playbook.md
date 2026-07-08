# Agent Playbook: Ordered Missions

Audience: an agent (or human) told "go do the next step" with no other
context. This file turns the project's plans into self-contained,
executable missions. Each mission says what to read, what to do, how to
verify, and what to update afterward.

Division of labor (D-023 discipline — do not duplicate):

- **This file owns:** the operational wrapper per mission (read-first
  lists, execution order, verification commands, handoff checklists) and
  the code-level pointers from the 2026-07-05 external code review that
  exist nowhere else.
- **It points to:** `docs/phase_N/phase_N_plan.md` for objectives, gates,
  acceptance criteria, and fallbacks; `docs/phase_2/
  hardware_slice_implementation_guide.md` for hardware-slice pinned APIs;
  `docs/decision_log.md` for settled decisions; the phase exit checklists
  for current per-item status.
- **No status lives here.** To find out what is already done, read
  `RUN_STATE.md` and the exit checklists. To find out what outranks what,
  read `TASK_QUEUE.md`. If this playbook and a plan disagree, the plan
  wins; fix the drift in the same run.

## How To Pick A Mission

1. Run Mission M0 (preflight) — always.
2. Take the highest-ranked task in `TASK_QUEUE.md` whose gate is open.
3. Find its mission below and execute it. One mission per session unless
   the first finishes early and cleanly.

Gate summary (check the queue/checklists for live status; this is just
the dependency shape):

```text
ungated, any time:      M1 (Slice 2N), M2 (backup protocol prep), M3 (related work)
needs user/advisor:     M4 (D-016 model selection), and the P1 evidence gates
needs D-016 + install:  M5 (2G MLX)
needs auth session:     M6 (2H powermetrics)
needs M5+M6:            M7 (2I Mac slice — the flagship)
needs P1-006 evidence:  M8 (2K/2L remote-target live validation;
                         2K fixture-first stack merged 2026-07-08 via PR #11)
needs M7:               M9 (2M baselines)
post-docs branch:       M10 Stage 3.0.1 verdict is replay_supported
                         after lead live re-verification
needs 2M baselines:     M10 later pairing-feasibility matrix + split runs
```

---

## Mission M0: Preflight (every session)

1. Read only the targeted `RUN_STATE.md` sections: "Current Project
   Status", "Known Workspace State", and "What Is Next".
2. Read `TASK_QUEUE.md`'s Current Queue and Do-Not-Do-Yet list.
3. Read the selected mission's own read-first list. Read `AGENT_PLAN.md`
   only at phase starts or when the project structure changes. Consult
   `docs/decision_log.md` by targeted decision ID, not as a whole-file
   intake step.
   If the session involves delegation, review, or multi-stream work, also
   read `docs/orchestration.md` (the process layer) — not optional for
   landing code.
4. Check workspace state with `git status --short --branch`; inspect
   recent commits only when the handoff or mission needs them.
5. `python3 -m unittest discover -s tests` — expect `Ran <N> tests` (N per `RUN_STATE.md` Current Verification; `, OK
   (skipped=10)` with zero expected failures as of 2026-07-08 after
   P2-013/P2-014 and the C-011 rigor mechanics. The skips are the `[analysis]`-extra chart tests plus one
   optional-jsonschema test. A red suite is itself the mission: stop and fix
   or report.
6. Review `docs/risk_register.md` at phase starts, before hardware tasks,
   when a trigger fires, or if >14 days passed since the last run report
   with no break recorded in `docs/milestones.md`.
7. At session end, always: update `RUN_STATE.md`, update `TASK_QUEUE.md`,
   write a dated run report in `docs/run_reports/`, update the phase exit
   checklist for anything that closed, and `PROJECT_STATUS.md` if
   advisor-visible state changed. Commit when the user asks or has
   standing-approved it.

Environment cautions:

- The repo must stay at a non-iCloud path (`~/code/...`; R-017). If you
  see `Operation not permitted` on reads inside the repo, stop, wait for
  the lock to clear, re-run the suite, and record the incident.
- CI installs no extras; every new test must pass on a bare Python
  (lazy imports, `skipUnless` for optional deps — D-009).
- Schema changes are additive-only until v0.2 (R-015/D-008).

---

## Mission M1: Slice 2N — Pre-Hardware Hardening (queue P2-007)

**Gate:** none. **Spec + acceptance:** `docs/phase_2/phase_2_plan.md`
Slice 2N. This mission adds the code-level route for each work item,
sourced from the 2026-07-05 external code review. Line numbers are from
commit `ae48abe` — re-locate by symbol name if the files have moved on.

Read first: `phase_2_plan.md` Slice 2N + Cross-Slice Contracts;
`joulewise/bundle.py`, `controller.py`, `reduce.py`, `interfaces.py`
(skim whole files — they are small and the invariants interlock).

2N is one mission but NOT one sitting: it touches adapter interfaces,
controller timing, reducer behavior, report parsing, CLI, schema export,
and validation policy. Work item-by-item with the suite green after each,
and land it as roughly three commits so a failure bisects cleanly:

- **Commit A — the adapter seam:** 2N.1 (RunContext + raw evidence),
  2N.2 (measured-window boundaries). Both touch controller/interfaces.
- **Commit B — the read layer:** 2N.8 (BundleReader), with 2N.4 (rail
  contract), 2N.7 (report alignment), and 2N.6's structured read
  failures implemented on top of it. 2N.6's CLI verb rides along.
- **Commit C — schema + metrics:** 2N.5 (schema round-trip), 2N.3
  (token-count fallback), 2N.9 (v0.2 compatibility note).

If a session ends mid-slice, a completed commit group is a clean
handoff point — say which group landed in `RUN_STATE.md`.

Per-item detail (each item = tests green before the next; items 1+2
change the controller/adapter contract and go first):

### 2N.1 `RunContext` seam + raw evidence

- Today: `RunBundleWriter._ensure_layout` creates `raw/` (bundle.py
  ~line 160) but no method writes into it, and adapters never see the
  bundle path — so a real telemetry adapter cannot honor D-002 ("raw
  file retained verbatim").
- Change: implement **D-024** (already decided — read it first): an
  immutable `RunContext` dataclass (config, clock, run_id, bundle_path,
  raw_dir, logs_dir, outputs_dir, optional node_role=None) constructed
  by the controller after bundle creation and passed to adapter
  lifecycle methods (exact placement — per-method parameter vs
  construction-time — is yours to pin; record the choice as a D-024
  amendment note). Add `RunBundleWriter.raw_path(name)`/`write_raw` as
  the writer-side counterpart (validated, collision-checked). Update
  `docs/contracts/adapter_contracts.md` in the same run. Do NOT hand
  adapters the writer itself — D-024 rejects that option; context is
  data, not capability.
- Tests: mock telemetry writes a fixture raw file via the context;
  bundle contains it; immutability (no overwrite after finalize); the
  no-raw-output mock path still passes; mocks ignore unused context
  fields (single lifecycle code path preserved).

### 2N.2 Measured window excludes sampler startup

- Today: `stage_started(measured_run)` is timestamped before
  `thermal_state` and `start_sampling` (controller.py ~lines 346-357),
  and the reducer integrates from that stage-start. Under `SystemClock`,
  sampler spawn latency (sudo probe, process start, first sample) lands
  inside the measured window — inflating gross energy, idle-subtraction
  duration, and TTFT. `FakeClock` collapses the interval to zero, so the
  existing suite cannot catch it.
- Change: open the measured window only after sampling is confirmed
  started (reorder), or emit explicit `sampling_started`/
  `sampling_stopped` marker events and make the reducer integrate
  between markers. Keep the D-013 quiescent rule intact (controller only
  blocks on the runtime inside the window). Record the choice
  (decision-log entry; it pins reducer semantics).
- Tests: a fake telemetry adapter whose `start_sampling` advances the
  injected clock by a simulated latency; assert the reducer's window
  excludes it (energy and TTFT unchanged vs a zero-latency run).

### 2N.3 Reducer token-count fallback

- Today: `energy_token_j` requires `workload_profile.prompt_tokens` from
  config (reduce.py ~lines 302, 511-521); a `prompt_text`-only config
  (like `configs/examples/mac_mlx_local.json`) silently yields `None`
  for the headline per-token metric, even though the runtime's observed
  `token_count`/`output_token_count` are already written to
  `metadata.json` (controller.py ~lines 532-536).
- Change: reducer falls back to observed counts from metadata; record
  which source was used (additive optional summary/quality field, e.g.
  `token_count_source: "config" | "runtime_observed"` — R-015 allows
  additive).
- Tests: prompt_text-only bundle produces non-None `energy_token_j`
  with source `runtime_observed`; config-supplied counts still win;
  neither present → None (unchanged).

### 2N.4 Rail-summation timestamp contract

- Today: `_summed_curve` groups rails by exact float `timestamp_s`
  equality (reduce.py ~lines 129-131). A real adapter emitting per-rail
  rows with slightly skewed timestamps silently produces an interleaved
  per-rail curve and badly undersummed energy — wrong number, no error.
- Change: either (a) detect misalignment (per-timestamp rail set !=
  manifest) and return a structured reduction failure naming the rail
  and skew, or (b) bucket timestamps within a tolerance derived from the
  sampling interval. Decide, log the decision, and document the
  contract in `docs/contracts/adapter_contracts.md` (today it is only a
  bundle.py comment).
- Tests: skewed-timestamp fixture → structured failure (or correct
  bucketed sum); aligned fixture unchanged to 9 decimals.

### 2N.5 Config schema accepts emitted configs

- Today: `BenchmarkConfig.to_dict()` emits `null` for absent optionals
  (`asdict`), but the hand-written exported JSON Schema declares those
  properties non-nullable (e.g. `quantization.bits`, schemas.py ~line
  379) — a bundle's normalized `config.json` fails validation against
  `print-config-schema` output.
- Change: pick one — (a) omit-None serialization (cleaner artifact;
  changes config bytes and therefore config hashes — acceptable ONLY
  while no real bundles exist, so decide now), or (b) schema declares
  nullable optionals. Either way: decision-log entry, and a round-trip
  test.
- Tests: every emitted normalized example config validates against the
  exported schema. CI has no `jsonschema` package (D-009): either write
  the check against the specific fields (nullability + required keys) or
  gate a full-validator test behind `skipUnless(jsonschema)`. Also
  assert config-hash stability with a pinned expected hash so future
  serialization changes fail loudly.

### 2N.6 Post-hoc `reduce` verb + structured reducer failures

- Today: `reduce_bundle` is importable but has no CLI verb, and raises
  uncaught `FileNotFoundError`/`JSONDecodeError` on missing/corrupt
  `config.json`/`metadata.json` (reduce.py ~lines 341-352) despite its
  docstring's "never crashes" claim. The "a reducer bug never re-runs
  hardware" story needs a user-facing path.
- Change: `python3 -m joulewise reduce <bundle-dir>` — re-derives and
  rewrites `summary_metrics.json` (document that this is the one
  sanctioned post-finalize mutation, or write to a versioned name —
  check D-011 and log the choice); degenerate inputs return structured
  failures. Match `run`'s exit-code scheme (0/2/3) and one greppable
  result line.
- Tests: reduce a valid bundle → identical metrics; corrupt/missing
  artifacts → structured failure + correct exit code; CLI help updated.

### 2N.7 Report/reducer rail-policy alignment (via 2N.8)

- Today: the report's trace chart falls back to summing ALL rails when
  the manifest is empty or matches nothing (report.py ~lines 187-209),
  while the reducer excludes non-manifest rails or fails — a chart can
  display energy the summary excluded.
- Change: do 2N.8 first, then implement both consumers' rail policy in
  the shared reader (D-025 is explicit: no spot fix). The report must
  never contradict the summary.
- Tests: manifest-mismatch bundle renders with the aligned behavior;
  normal bundle chart unchanged.

### 2N.8 Shared bundle read layer (`BundleReader`)

- Today: `reduce.py`, `report.py`, and `cli.py`'s `validate-bundle`
  each parse bundles independently; they have already diverged once
  (2N.7). Phase 4's `aggregate` would be a fourth parser.
- Change: implement **D-025** (read it first): a `BundleReader` — in
  `joulewise/bundle.py` or a new `joulewise/bundle_read.py` — owning
  parsing and interpretation policy: config, metadata, events, power
  trace, rail manifest, measured/phase windows, completion state,
  structural problems. Port the three existing consumers onto it;
  metrics math stays in `reduce.py`. This naturally absorbs parts of
  2N.4 (rail timestamp contract) and 2N.6 (structured read failures) —
  sequence them together.
- Tests: existing reducer/report/validate suites keep passing unchanged
  (the port is behavior-preserving except where 2N.4/2N.7 deliberately
  change policy); reader-level tests for completion state and window
  extraction on happy/corrupt fixtures.

### 2N.9 Schema v0.2 compatibility check (design-only, no code required)

- Read D-008 (`run_kind`/`split_plan` design), the composite-bundle
  block in `docs/contracts/run_bundle_layout.md`, and Phase 3 Stage 3.1.
- Check: would the RunContext fields (esp. `node_role`) and the
  BundleReader API survive composite/split bundles without redesign?
  Optionally add a synthetic test constructing a RunContext with
  `node_role="prefill"` to prove nothing chokes.
- Deliverable: a findings paragraph in the run report; amend
  D-008/D-024/D-025 if a conflict surfaced. Explicitly NO schema change
  (R-015).

**Done when:** all Slice 2N acceptance criteria in the plan hold, suite
green, new tests cover each item, decision-log entries exist for every
contract choice (D-024/D-025 are pre-decided — implement them; expect
~2 more for the 2N.2 window semantics and 2N.5 serialization choices),
`adapter_contracts.md` updated, exit-checklist 2N row closed with
evidence, run report written.

---

## Mission M2: Measurement-Corpus Backup Protocol (queue P0-002)

**Gate:** none to draft; needs one user input (destination). Must be
closed before the first real (non-mock) measurement session (R-016).

1. Read R-016 in `docs/risk_register.md` — the protocol fields it
   requires (destination, cadence, method, restore test).
2. Ask the user for the backup destination (external disk path and/or
   cloud location outside the repo). Do not guess.
3. Implement `scripts/backup_runs.sh` (or `.py`): rsync-style copy of
   `runs/` + `runs/experiments/` manifests to the destination, with a
   dated log line appended to the backup location; idempotent; safe to
   run after every measurement session.
4. Perform one restore test: back up a mock bundle, delete the local
   copy (of the COPY, in a temp dir — never the original), restore,
   `validate-bundle` green on the restored bundle.
5. Record the protocol in R-016's mitigation text (that is its
   designated home), close P0-002 in the queue, run report.

---

## Mission M3: Background / Related-Work Draft (queue P3-001, Stage 4.6)

**Gate:** none — desk work, may run any time. **Spec + source list:**
`docs/phase_4/phase_4_plan.md` Stage 4.6 (includes the named 2025-26
works from the 2026-07-05 landscape search and the positioning claims to
argue).

1. Read Stage 4.6 and the positioning bullet (TokenPowerBench,
   ML.ENERGY, Intelligence per Watt, Bench360, "Where Do the Joules
   Go?", MLPerf Power, Zeus, Splitwise, DistServe, Mooncake, JouleSort).
2. For each source: fetch/read it; write one paragraph of what it
   establishes and one sentence of how JouleWise relates. Record a
   resolvable citation (arXiv ID/DOI/URL, retrieved date).
3. Verify the three distinguishing claims honestly against what you
   read — if a source DOES cover local split-inference energy or
   boundary-honest cross-device methodology, that is a finding: record
   it and adjust the positioning rather than ignoring it.
4. Deliverable: `docs/phase_4/related_work_draft.md`. Close the 4.6
   exit-checklist row only when the plan's acceptance holds ("background
   chapter can be assembled from this draft without new research").

---

## Mission M4: Close D-016 Model Selection (queue P2-004)

**Gate:** P1-001 supervisor scope OR an explicit user go-ahead recorded
in the run report. Never close it silently (Do-Not-Do-Yet list).
**Criteria + candidate set:** D-016 in `docs/decision_log.md`.
**Checkpoint description:** `phase_2_plan.md` "Model Selection
Checkpoint (Before 2G)".

1. Confirm the gate (ask the user if ambiguous).
2. Apply D-016's five fixed criteria to its candidate set. Check disk
   space before choosing mirror paths.
3. Verify artifact availability per runtime NOW (MLX community repo,
   GGUF file, HF repo) — links rot; record exact revisions/hashes.
4. Mirror weights locally (R-014) and record where.
5. Compute KV bytes/token for the chosen models and add the rows to the
   Phase 3 KV table (`docs/phase_3/phase_3_plan.md`).
6. Close D-016 in the decision log (status accepted, with everything its
   "Closure evidence required" paragraph lists); update
   `configs/examples/mac_mlx_local.json` to the chosen model; queue +
   run report.

---

## Mission M5: Slice 2G — MLX Runtime Adapter (part of queue P2-003)

**Gate, acceptance, fallback:** `phase_2_plan.md` Slice 2G (gate: D-016
closed or provisional + `[mac]` extra installed). **Pinned
implementation spec:** `hardware_slice_implementation_guide.md` §2G —
follow it exactly; it names the files, adapter API, event emission, and
CI-safe tests.

Wrapper notes beyond the guide:

- Land Slice 2N first (Do-Not-Do-Yet list) — 2G builds on the post-2N
  seams (notably 2N.3's observed-token fallback).
- Bring-up order: real MLX runtime + MOCK telemetry first (composition
  is the point of the adapter split); a complete bundle from that
  pairing is this mission's smoke evidence.
- The install itself (venv, `pip install 'joulewise[mac]'`) needs user
  approval per R-003; record versions in the run report.
- Handoff: applicability-table row updated, run report with the smoke
  bundle path and token-timeline evidence, exit-checklist 2G row.

## Mission M6: Slice 2H — powermetrics Telemetry Adapter

**Gate, acceptance, fallback:** `phase_2_plan.md` Slice 2H (gate: the
privileged sample captured in the Phase 1 exit checklist instrumentation
section + D-004 sudoers rule installed — a user auth session provides
both). **Pinned implementation spec:** guide §2H.

Wrapper notes:

- If the gate is closed but the captured sample is not yet in the exit
  checklist, capturing/recording it IS step one of this mission (with
  the user present for sudo).
- Build the parser fixture from the captured sample verbatim; commit the
  fixture under `tests/fixtures/`.
- The raw plist must land via the 2N.1 `write_raw` seam — if that seam
  is missing, do M1 first, not a workaround.
- Handoff: fixture tests in CI; a real idle baseline + measured window
  from the Mac in a run report; exit-checklist rows (Phase 1
  instrumentation checkboxes + Phase 2 2H row).

## Mission M7: Slice 2I — Mac Vertical Slice (the flagship)

**Gate, actions, acceptance:** `phase_2_plan.md` Slice 2I (gate: 2F +
2G + 2H). Guide §2I has the literal commands.

Wrapper notes:

- This is an evidence mission, not a coding mission. If code changes are
  needed to make it pass, that is a finding — record it, fix it, and
  note the fix in the run report.
- Before the 3-rep experiment: confirm the D-013 conduct checklist
  (deferred logging, controller quiescent) and watch the D-014 cooldown
  gate behavior on real hardware — if the gate caps out every rep
  (idle power too noisy for the 10% band), record it and flag D-014 for
  its Phase 4 ratification rather than tuning silently.
- Check reduce time on real traces; if noticeable, the 2N `bisect` note
  fires (upgrade `_integrate`'s linear scan).
- Handoff: bundle paths, summary metrics, 3-rep variance in the run
  report; applicability table Mac row → `supported`; `PROJECT_STATUS.md`
  refresh (this is the most advisor-visible milestone in the project).

## Mission M8: Slices 2K/2L — Remote Targets

**Gate, acceptance, fallbacks:** `phase_2_plan.md` Slices 2K/2L (gate:
P1-006 access evidence per target — do not start on assumption).
**Pinned spec (SSH transport, remote-runner protocol, telemetry):**
guide §2K/§2L.

Wrapper notes:

- 2K status as of 2026-07-08: the NVIDIA fixture-first implementation is
  MERGED (PR #11: protocol v1, SSH transport, `nvidia-smi` + vLLM
  adapters, registry wiring). Do not mark protocol pins non-provisional
  until the P1-006 live evidence script
  (`docs/phase_1/2k_live_verification_checklist.md`) has contacted real
  hardware.
- P1-006 evidence-gathering (SSH reachability, `nvidia-smi` power query,
  VRAM) is itself recordable work if the user provides access during the
  session: capture command outputs into the Phase 1 exit checklist
  instrumentation section first, then implement.
- The remote runner is a project-wide contract, not an SSH detail:
  `docs/contracts/node_worker_protocol.md` owns the conceptual shape
  (controller sends JSON task → node worker executes → returns
  artifacts/events/status) and lists Phase 3's requirements. Pin the
  wire-level details INTO that contract as you implement 2K — it is
  reused by 2L and all of Phase 3, so decisions here bind later work.
- One target per session (2K, then 2L).

## Mission M9: Slice 2M — Homogeneous Baselines

**Gate, workload matrix, protocol, acceptance:** `phase_2_plan.md`
Slice 2M (gate: 2I; Mac-only is the documented floor).

Wrapper notes:

- Backup protocol (M2) must be in place before this mission's data
  collection — it produces the first corpus worth protecting.
- Build the config-matrix generator script first, validate the whole
  matrix with `validate-config` before any hardware time.
- Interleave conditions per D-014 where model-reload cost permits;
  record executed order in the experiment manifests.
- Handoff: manifests + bundles; `docs/phase_2/baseline_results.md` with
  variance and the prefill/decode comparison; back up the corpus; run
  report.

## Mission M10: Phase 3 Stage 3.0 — KV Feasibility Spikes

**Gate, stage detail, verdict codes:** `docs/phase_3/phase_3_plan.md`
Stage 3.0 and the Phase 3 readiness gate in the Phase 2 exit checklist
(needs 2I; baselines for any pairing you plan to schedule). Do not
schedule the 3080 Ti borrow window before these verdicts exist (R-006).

Wrapper notes:

- Run the spikes in the plan's order (kv-size helper → mlx-lm →
  llama.cpp same-machine → llama.cpp cross-machine → vLLM time-boxed).
  The helper's predictions get checked against actual file sizes — both
  numbers go in `docs/phase_3/kv_feasibility.md`.
- Every spike ends in a verdict code, including `replay_unsupported` —
  negative verdicts are deliverables (D-015), not failures.
- Consolidate verdicts before proposing any hardware pairings.

---

## After Any Mission

The M0 step-6 handoff list, plus: if you changed an adapter or bundle
contract, `docs/contracts/` must already reflect it (same run); if you
made a choice between real alternatives, the decision log must already
hold it. A mission whose bookkeeping is missing is not done.
