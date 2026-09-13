OpenAI Codex v0.146.1
--------
workdir: /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
model: gpt-5.6-sol
provider: openai
approval: never
sandbox: workspace-write [workdir, /tmp, $TMPDIR]
reasoning effort: high
reasoning summaries: none
session id: 019fdd0d-49c1-7f80-b88b-66d7b26453af
--------
user
PAPER-PROPOSAL DEVELOPMENT SESSION (one of a 20-direction parallel fan-out).

You are developing ONE candidate research-paper direction for the JouleWise project
into a full, reviewable proposal. Work read-mostly; do NOT create or modify any files —
your final message IS the deliverable. You may read any repo file.

== PROJECT BRIEF (state as of 2026-08-07) ==
JouleWise is Ed's undergraduate CS capstone: treating Apple's `powermetrics` software
power counter as a calibrated scientific instrument for phase-resolved (prefill vs
decode), single-request LLM inference energy on one named M3 Max stack (MLX, Qwen2.5
family, 4-bit). Core findings/machinery to date: in-window bracketed pulse-train
calibration of timing attribution; the instrument is ATTRIBUTION-LIMITED (~1 J per
phase member from ~30 ms edge uncertainty × ~33 W swings; repetition cannot average it
away), not noise-limited; detection floors composed from repeatability + worst-case
attribution + measured never-zero drift, published labelled; TWO separate claim gates
(floor clearance; interval-supported direction) with a practical ~5 J sizing bar for
phase contrasts; fail-closed collection protocol (pre-registration, admission gates,
ABBA counterbalancing, hash-bound custody chains, refusal log as evidence). MVP paper
draft is complete-in-structure (docs/paper/draft-v1.md) with demonstration values
pending. The claim path (decision D-117, adopted today): THREE fresh prospective quiet
windows — 1.5B decode floor, 7B decode floor, 1.5B-vs-7B decode contrast — each
live-bracketed under an issued calibration-acceptance regime; prefill floor cells ride
the floor windows; a 256-token prefill contrast arm is an open option (128-token
prefill contrast is MARGINAL vs the bar — custodied desk check).
Steps from here: 3 quiet-mac nights (operator bookends only) + desk work (window plans,
mint pinsets, extraction specs, regression) → mint floors → populate the paper →
capstone submission; then an ICPE-class version.

== CONTEXT AND CONSTRAINTS ==
- Advisor: Suzanne Rivoire (JouleSort co-author) — sets a real metrology bar; plain
  language required in reader-facing text.
- Venue ladder: capstone (CSCSU-class) → ICPE full research track is the realistic
  ambitious target; top-tier only if a mechanism/split research bet lands.
- Hardware: M3 Max MacBook Pro 128 GB (the instrumented unit); an RTX 3080 Ti desktop
  rig; optional Jetsons; a Yokogawa WT310E wall meter is NOT owned but may be BORROWED
  from the advisor's lab (claim C8 ratified the wall-meter axis as future work).
- Measurement economics: each claim window is a 2-4 h quiet night with operator
  bookends; effects must clear the two gates (~5 J practical sizing for phase
  contrasts on this stack; workload LENGTH is the free lever since attribution error
  is ~duration-independent).
- Ed's ORIGINAL research goals (pre-metrology-pivot, still wanted long-term):
  mechanism-level energy profiling as a third metrics axis alongside quality+latency —
  speculative decoding, multi-token prediction (MTP), mixture-of-experts (MoE)
  routing, KV/attention variants (e.g. KDA), and SPLIT/disaggregated inference across
  consumer devices; a modular harness where every experiment axis (model, inference
  technique, workload, size) is swappable; energy-honest leaderboard/reporting
  critique. Repo context worth reading: docs/strategy/2026-08-06-impressiveness-roadmap.md,
  docs/research_question_registry.md, docs/research_question_bank.md,
  docs/paper/draft-v1.md (esp. §§3-5), CLAIMS_STATUS.md, docs/decision_log.md (D-117,
  at end of file).

== YOUR DELIVERABLE (final message, markdown, ~600-1200 words) ==
1. TITLE + one-sentence thesis.
2. PROJECT-BRIEF-AND-STEPS paragraph: half a page restating the current project state
   and the concrete steps from today to THIS paper (audience: Ed deciding what to
   fund with nights/desk time).
3. CONTRIBUTIONS (3-5, numbered, each falsifiable).
4. EXPERIMENT PLAN sized against the instrument: cells, contrasts, expected effect
   magnitudes vs the ~5 J sizing bar (estimate from public knowledge + repo
   diagnostics you can find; state which effects might NOT clear and what the refusal
   would mean), number of quiet windows needed, desk-work list, any new harness
   capability required (and whether it violates the frozen single-request boundary).
5. HARDWARE/INSTRUMENT needs (owned / borrowed / new; wall-meter dependency yes/no).
6. VENUE fit + why (capstone chapter? ICPE? workshop?), and how it BUILDS ON the MVP
   paper (shared method sections, what's new).
7. RISKS + KILL CRITERIA (what desk evidence would kill it before spending a night).
8. RELATION TO ED'S ORIGINAL GOALS: which original axis it serves, or state plainly
   that it does not.
Be concrete and quantitative wherever possible; flag every number you are unsure of.

== HARD CONSTRAINT (Ed, binding) ==
Every proposal MUST turn the EXISTING material into a solid scientific paper: the
calibrated instrument and its custody/fail-closed protocol machinery, the
attribution-limited finding, the banked diagnostics, the data the three D-117 windows
will produce (decode floors for 1.5B and 7B, prefill floor riders, the decode
contrast), and modest extensions collectible on the owned hardware under the SAME
instrument discipline. Do NOT propose work that abandons the instrument or needs
apparatus/data without a concrete path (the borrowed WT310E wall meter is allowed
where justified as an extension of existing material). If your assigned direction
cannot honestly be built from existing material, SAY SO PLAINLY and shrink it to the
version that can — a smaller honest paper beats an unmoored ambitious one.

== REQUIRED READING (read these in the repo before writing anything) ==
docs/paper/draft-v1.md (the whole draft — every proposal must state what it reuses
from it); CLAIMS_STATUS.md; the D-117 entry at the end of docs/decision_log.md;
docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md (exactly what the three
windows produce, budgets, mint machinery); docs/strategy/2026-08-06-impressiveness-roadmap.md;
docs/research_question_registry.md; docs/research_question_bank.md;
docs/process_traces/2026-08-07-prefill-feasibility/SYNTHESIS.md.

== YOUR ASSIGNED DIRECTION (cross-runtime-contrast) ==
Cross-runtime same-boundary contrast: MLX vs llama.cpp, same model artifact class, same powermetrics boundary — runtime efficiency claims under the floor discipline.

codex
I’ll develop the narrow, instrument-compatible MLX-versus-llama.cpp proposal. I’m first grounding every claim in the complete MVP draft, D-117 freeze materials, and the repo’s current decision/queue state; I’ll keep this entirely read-only.
exec
/bin/zsh -lc "sed -n '1,260p' docs/agent_playbook.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
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

1. Read only the targeted `RUN_STATE.md` sections: `ACTIVE_STOP_CARD`
   if present, "Current Project Status", "Known Workspace State", and
   "What Is Next". If the stop card is ACTIVE, it overrides this
   playbook and the task queue until cleared.
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

exec
/bin/zsh -lc "sed -n '1,260p' TASK_QUEUE.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
# JouleWise Task Queue

This is the live queue for JouleWise work. When the user gives a new task, first
triage it here instead of assuming it should happen immediately.

## Intake Rule For New Tasks

For every new user task:

1. Read `RUN_STATE.md`.
2. Read this file.
3. Check `git status --short --branch`.
4. Review the last 2-3 commits with `git log --oneline --decorate -3`.
5. Check relevant handoffs in `docs/run_reports/`.
6. If `RUN_STATE.md` contains an ACTIVE `ACTIVE_STOP_CARD`, that card
   outranks this queue. Execute or preserve the card's resume/cleanup
   instructions before considering any lower-ranked work.
7. Decide whether the task is:
   - urgent workspace hygiene,
   - Phase 1 evidence work,
   - Phase 2 implementation prep,
   - later-phase research work,
   - documentation/reporting,
   - or unrelated/new scope.
8. Place or update the task in the queue with priority, rationale, evidence,
   and blockers.
9. If executing it now, say why it outranks the current top task.
10. Closure rule (D-023): a row may move to Completed only after the
    corresponding phase exit-checklist matrix row already shows the same
    status with dated evidence, and the Completed row's evidence cell
    must cite that matrix row (file + item id). If no matrix row exists
    for the work, say so explicitly in the evidence cell.

## Priority Scale

- **P0 Safety**: prevents accidental data loss, bad commits, broken handoffs, or
  corrupted repo state.
- **P1 Phase Gate**: required to close the current phase or unblock the next
  phase responsibly.
- **P2 Next Slice**: next implementation slice after current phase gates are
  adequately planned or closed.
- **P3 Research Expansion**: useful experiment or feature, but not needed for
  current gate.
- **P4 Polish**: quality-of-life, dashboard polish, formatting, cleanup, or
  presentation work.

## Ranking Factors

Rank higher when a task:

- Prevents accidental loss or bad Git history.
- Produces evidence for the current phase exit checklist.
- Removes ambiguity for multiple later steps.
- Is required before physical hardware time is spent.
- Is cheap to verify and reduces future confusion.
- Matches the current phase better than jumping ahead.

Rank lower when a task:

- Depends on unavailable hardware or supervisor input.
- Is a later-phase feature.
- Adds polish before a runnable vertical slice exists.
- Produces code without a clear run-bundle or test artifact.

## Ready/Shelf Rule

A partially built or proposed task is **READY** only when it has:

- one authority document or stream-log pointer,
- bounded files/modules or a bounded artifact target,
- explicit acceptance evidence or a verification command,
- no hidden hardware/user/token-budget dependency, and
- a named lane (`[AGENT]`, `[QUIET-MAC]`, or `[ED-EXTERNAL]`).

If any of those are missing, keep the item as a shelved concept or
planning note instead of letting it compete with executable queue work.
Half-finished work should be resumed only through its authority pointer
and stop-card/checkpoint state, not by inference from prose summaries.

## Machine-State Lanes (adopted C-007, 2026-07-07)

Every task carries a lane; a session picks the top task COMPATIBLE with
its machine state, not the top task absolutely:

- **[QUIET-MAC]** — measurement campaigns only: no agent fleet, no Codex
  load, idle gate will flag contamination.
- **[AGENT]** — code, docs, feasibility spikes; safe during agent-heavy
  sessions.
- **[ED-EXTERNAL]** — needs the user: advisor, calendar, device access,
  purchases, destinations.

## Historical Queue Snapshot (superseded 2026-07-15)

The former hand-authored live table was removed because it duplicated kernel
tasks. Dated completion and disposition history remains below; the generated
Current Queue region is the sole live work-selection view.

## Completed Queue Items

| ID | Priority | Completed | Task | Evidence |
|---|---|---|---|---|
| COLDGATE-VALIDATOR-01 | P2 Next Slice | 2026-08-05 | Build `scripts/validate_gate_packet.py` as a deliberately validation-time-only cold-gate packet validator | Merged via PR #103 (`b730d89`). Full evidence chain: rule-11 escalation consult after three same-signature F3 rounds -> Option D adopted (attestation subsystem deleted; receipt v2 declares `binding_scope=validation_time_observation_only` and `judge_handoff_bound=false`; `--receipt-out` removed; fence-aware CommonMark scans; `--help` exit-0) -> xhigh delta re-audit FAIL with two live-proved blockers (malformed-digest receipt leak; phantom-fence duplicate suppression) -> fixes (`3835288`) -> final delta ACCEPT with zero introduced defects -> CI green. Records: `docs/process_traces/2026-08-05-cgv-f3-consult/`. NOTE: validator PASS is NOT launch authorization; operational use is blocked on `COLDGATE-HANDOFF-01`. |
| WINB-R06-DISPOSITION-01 | P1 Phase Gate | 2026-08-05 | Dispose of the Window-B r06 evidence gap under the D-112 removal-channel ruling | **ABANDONED_FOR_FRESH_COLLECTION** under D-113 (Ed ruled channel (c)); no Window B re-evaluation or claim consumption will occur and the original FAILED verdict stands. The unpinned `current_environment_refusals` sub-branch is retained as unresolved historical residue, nonblocking. Evidence: D-113 + `docs/process_traces/2026-08-05-d113-rigor-consult/`. |
| CAL-BRACKET-D079-01 | P1 Phase Gate | 2026-08-05 | Implement D-079 calibration acceptance v2 in the bracket selector (derived screen, freshness refusal, budgeted excess allowance, evaluation-basis recording, floor/claim propagation) per the D-109 A-min-with-reservation ruling | No matrix row exists in `docs/phase_2/phase_2_exit_checklist.md` for this repair; merged via PR #100 (`f75d12b`) at the audited head `4280ebd` under D-072 with Ed's explicit go (2026-08-05; merge-permission rule added, restoring mechanical self-merge). Full gauntlet: D-109 implementation + fix round 1 (B2+S1) + rule-11-gated fix round 2 (B1 closed both dimensions, delta re-audit CLEAN) + integration-collision resolution per D-109 addendum II (reviewed signature-pin amendment, guard hardening incl. the repr-'None' default-spoof regression the delta re-audit proved live); lead integration-tree replay `Ran 2487 tests OK (skipped=82)` exit-0 unpiped; PR CI green. Records: `docs/process_traces/2026-08-04-calbracket-integration-collision/`, `docs/process_traces/2026-08-03-calbracket-b1-gate/`, D-109 + addenda, C-048. D-110 re-mint condition (a) is satisfied; MINT-GENERALIZE-01 stays blocked on (b) issuance + (c) validator widening; T3-AMEND-01 unblocks as the first desk item after |
| T3-AMEND-01 | P1 Phase Gate | 2026-08-05 | Bridge-protocol §4/§6/§7/§8 + skills amendments carrying every amendment from the t3-doctrine gate synthesis | No matrix row exists in `docs/phase_2/phase_2_exit_checklist.md` for this doctrine-bookkeeping row; merged via PR #101 (`906ddf9`) under D-072 after the full gauntlet: Sol high draft round -> two independent lenses (amendment fidelity; contract consistency + consumer drift) -> adjudicated fix round -> delta re-audit FAIL (2 blockers: a §10/WO-020 quiet-mac consumption contradiction introduced by a lead bench edit, and §8 overclaiming a mechanically-enforced reverse-consult eligibility the adapter cannot deliver) -> bounded design consult + fixes -> final delta ACCEPT zero blockers. All 32 synthesis-ancestry amendments land exactly once (`docs/process_traces/2026-08-05-t3-amend/AMENDMENT-MAP.md`), with non-normative proposals separated. §8 now states the honest shape: mechanical header acceptance is not proof of top-level status, the transitional rule is convention not enforcement, and a transitional consult result is NON-AUTHORITY-BEARING (fail-closed at consumption); real enforcement is bound to the follow-on `T3-PROV-SCHEMA-01`. A lens split on late-contamination ancestry was adjudicated at the primary source (registry Convening procedure §2), not by vote. Lead replay `tests.test_bridge` 62 OK exit-0 unpiped at every head; CI 6/6 green on the merged head. Contract stays `bridge-protocol/v1.1`; the v1.2 bump is recorded as a recommendation |
| D100-BII-BINDING-01 | P1 Phase Gate | 2026-08-03 | Close the b-ii capture-identity fixes D-106 ruled (window B re-evaluation was hard-blocked on this row) | Closed under D-108 (Ed deferral to the joint magistrate+Sol consult, C-042): clause (c) nested-content grammar RETIRED as a license precondition; (a) interval containment + the D-107 false-refusal repairs landed via PR #99 (`32d72fd`, gauntlet: Sol xhigh impl -> focused audit 1 blocker F1 -> lead bench fix -> delta re-audit ACCEPT zero findings; lead full suite 2403 OK at `751e6ee`; CI 5/5); (b) the hash-sealed closure-manifest pin was already landed; (d) repaired-tool digest-bound re-record executed at merged HEAD `32d72fd` over ALL THREE D-087 occurrences (22 artifacts each, per-file sha256 manifests, licensed 3/3; banked `.desk/coldgate_d100_bii/d108-clause-d-rerecord.json`); L-A' executable derivation + probe transcript BANKED with live probes (.desk/coldgate_d100_bii/LA-PRIME-BANKED.md); window B re-evaluation UNBLOCKED |
| NVIDIA-RETENTION-FLAKE-01 | P2 Next Slice | 2026-08-03 | Fix the test-isolation/load-sensitivity defect in tests/test_nvidia_node_integration.py (RuntimeError: retention record disappeared under suite ordering) | Root-caused to the fixed shared `DEFAULT_RETENTION_ROOT`; closed test-side (node_client.py untouched) via hermetic per-test retention roots + a registry-clients-do-not-share-manifest regression; assertions preserved (re-indented); 20x interleaved stress zero retention-disappearance failures; lead suite `Ran 2437 OK (skipped=82)`; merged via PR #97 (`a32977e`) with green CI 5/5 under D-072. The production DEFAULT_RETENTION_ROOT hardening (concurrent-client collision vs next-session reclamation) is deferred as `NODE-CUSTODY-DEFAULT-01` (non-blocking) |
| MET-DANGLER-DISPOSITION-01 | P1 Phase Gate | 2026-08-02 | Implement the D-100 ruling as one audited repair commit (uniform dangler disposition, mechanical exclusion license, salvage_dangler_exclusion_v1 semantics dispatch, membership repairs, R1-R8 + R5a/R5b regressions) | No matrix row exists in `docs/phase_2/phase_2_exit_checklist.md` for this repair; merged via PR #94 at the audited head `05d99b6` (merge `bc2ab19`) under D-106 clause 1 and the checkpoint's ruled CI fallback (the branch's pull_request CI never scheduled, GitHub-side); three independent audits + cold gate D-106 + lead suite `Ran 2396` OK unmasked at the audited head with mapping pins hash-identical; the D-078 registry amendment landed with the merge; the b-ii residual is DECIDABLE and open as `D100-BII-BINDING-01` (D-106 clause 3) with window B re-evaluation hard-blocked on it |
| MEMBERSHIP-READER-FAILOPEN-01 | P0 Safety | 2026-08-02 | Close the latent fail-open in whole-window membership reading (malformed supersession catalog entries and unreadable/wrong-schema manifests silently skipped) | No matrix row exists; folded into the D-100 repair per the D-100 addendum (reader fail-open fold) and closed with PR #94 (`bc2ab19`): malformed records fail the affected candidate group per the D-093 visibility contract, with valid-plus-malformed same-bundle regressions |
| MANIFEST-CONTRAST-01 | P1 Phase Gate | 2026-08-02 | Unfreeze the analysis-manifest path gating every contrast claim (analysis-manifest v3 per the D-095 adopted design, embedded authenticated floor bytes per the embedded-floor-bytes ruling) | No matrix row exists; merged via PR #95 at the audited head `e94d4a7` (v3 module + dispatcher, v1/v2 byte-frozen, governed ABBA derivation, cross_stack_armwise_max.v1, D-093 scan hook); decisive independent audit CLEAN zero findings at that head; lead gates suite 2374 OK with pins hash-identical and v1 blob-identical; integration-tree full suite at the composed 94+95 merge; the gated contrast claim now rides MINT-GENERALIZE-01 (D-088 cl.3(c)) then the D-095 chain |
| COOLDOWN-JOIN-GAUNTLET-01 | P1 Phase Gate | 2026-08-02 | Run the cooldown-join refusal contract through its own gauntlet (C1-C5, both blocker fixtures, QA-10C) | No matrix row exists in `docs/phase_2/phase_2_exit_checklist.md` for this gauntlet; commits 1-2 landed via PR #91 (`67d268a`); commit 3 landed via PR #93 (`cb860e1`, 2026-08-02) as the composed D-097 change hardened through five audited fix rounds, a custody micro-commit, and cold gates D-103/D-104/D-105 (six independent audits; suite 2352 OK; 57/57 + 47/47 mapping pins hash-identical at every head); the D-088 standing conditions and D-093 scans LIFT per this row's contract; residual recognizer-exactness blockers registered non-downgradable in `C3-RECOGNIZER-EXACT-01` (D-105, a new ruling — not QA-10A/B precedent) |
| QA-10A-JOIN-OMISSION | P0 Safety | 2026-08-02 | Close the cooldown-join result-map omission | No matrix row exists; closed as contract C1 inside the gauntlet (result-map completeness landed in PR #91 commit `75e9f29`; fixture refuses; final closure with the gauntlet via PR #93) |
| QA-10B-EXISTING-RETRY | P0 Safety | 2026-08-02 | Close the cooldown-join existing-retry launder | No matrix row exists; closed by the D-094 counting domain (PR #91 `e749c95`) + the commit-3 writer outcome emission and truth-table row (PR #93); the QA-10B fixture refuses through the one-row fast path; Opus refuter dissent from D-088 remains on the record |
| MET-VERDICT-ADJ-01 | P1 Phase Gate | 2026-08-01 | Adjudicate the whole-window verdict machinery over the two salvage-shaped metrology windows (three question groups: dangling quarantined occurrences, deviation post-cal bracket selection, window B membership resolution) | No matrix row exists in `docs/phase_2/phase_2_exit_checklist.md` for this adjudication; independent read-only Sol xhigh audit over the mechanically assembled packet (bench-verified on every load-bearing claim), classifications: (a) CONTRACT GAP, (b) MACHINERY DEFECT with correct retry rejection, (c) CORRECT-for-B plus one latent fail-open; group (a) went to the rule-11 mandatory cold gate (cold Fable + bounded factual follow-up + Opus contract refuter) and synthesized as **D-100**; repairs queued as `MET-DANGLER-DISPOSITION-01`, `CAL-BRACKET-D079-01`, `MEMBERSHIP-READER-FAILOPEN-01`; both FAILED verdicts stand as issued (window A permanently — immutable T1-incompatible retry; window B re-evaluation licensed under D-100 conditions only, and since 2026-08-02 HARD-BLOCKED on `D100-BII-BINDING-01` per D-106 clause 3); packet + audit + rulings retained at `.desk/adjudication_packet_20260801/`, session records `docs/run_reports/2026-08-01-metrology-window-b.md` (collection) + `docs/run_reports/2026-08-01-desk-adjudication-session.md` (adjudication → D-100) |
| COOLDOWN-JOIN-DA1-01 | P1 Phase Gate | 2026-07-31 | Close DA-1 at the reader boundary so a malformed supersession record can no longer be dropped pre-ambiguity, making valid+malformed same-bundle resolve instead of refuse (D-093 boundary-fix contract) | No matrix row exists in `docs/phase_2/phase_2_exit_checklist.md` for this join-contract defect; closed inside the gauntlet's commit 2 (`e749c95`) as D-093 required — the supersession reader returns recognizable raw candidates with validation results (`supersession_entry_validation_results`; `None` = global fail-closed), so the join owns raw-record visibility at the reader boundary; the V4-driver regression (valid exact record + corrupted same-bundle clone) REFUSES and the malformed-clone ambiguity regression fails on parent `75e9f29`; independently audited read-only Sol xhigh, and the final delta re-audit passed with zero findings at the head merged as PR #91 (`67d268a`), session record `docs/run_reports/2026-07-31-claims-desk-session.md`; the D-093 raw-vs-validated scan on every claim consumption persists until `COOLDOWN-JOIN-GAUNTLET-01` fully closes |
| P2-015 | P2 Next Slice | 2026-07-31 | Collect the first claim-grade Window A floors under the claim-window run-book (bracketed calibration, start triplet, midpoint reference, end triplet) | No matrix row exists in `docs/phase_2/phase_2_exit_checklist.md` for this collection gate; claim-grade floors collected across windows a9/a10 plus C and D; mint #1 (1.5B decode floor 7.377086 J) is mainline via PR #88 (`da83337`), session record `docs/run_reports/2026-07-30-mint-merge-coldgate.md`; the 7B floor window passed 2026-07-29 and the contrast window passed 2026-07-31 (`docs/run_reports/2026-07-31-contrast-window-collection.md`); the seven hard dependents (AXI-SE, P2-006, P2-010, P2-024, P2-035, P2-047A/B) are satisfied against that evidence |
| STACK-ID-BIND-01 | P1 Phase Gate | 2026-07-30 | Align claim-side stack identity with the mint so real MLX bundles bind (`folded_sha256` `file_set` artifacts) | No matrix row exists in `docs/phase_2/phase_2_exit_checklist.md` for this claim-binding defect; FIX-7 (`7f2c108`) closed the `folded_sha256` shape plus four further derivation divergences with a parity regression and a directory-shaped end-to-end fixture; lead re-verified claim binding against a real a10 production bundle at `7f2c108`+; merged in PR #88 (`da83337`); session record `docs/run_reports/2026-07-30-mint-merge-coldgate.md` |
| FLOOR-LABEL-01 | P1 Phase Gate | 2026-07-27 | Attribution-limited floors become a labelled claim path instead of a refusal (D-078 clause 11) | No matrix row exists in `docs/phase_2/phase_2_exit_checklist.md` for this attribution-limit adjudication; merged at `3055315` (2026-07-27) through the full D-072 gate; the single-count discipline (effective clearable effect = floor + claim-side bound) is carried into every publishing artifact per D-078 clause 11 |
| CODEX-BRIDGE-PET | P4 Polish | 2026-07-18 | Make the native Codex pet reflect Claude Code background Sol work without changing adaptive effort routing | No phase exit-checklist row exists for this personal bridge UI integration; actual `scripts/codex-bridge` route traced, app-owned thread follower implemented, live Sol/high app-thread smoke `019f77a9-2827-7de1-accf-ac2eda21927e`, focused IPC/termination tests, and report `docs/run_reports/2026-07-18-claude-codex-pet-observer.md` |
| P2-015-SMOKE | P2 Next Slice | 2026-07-17 | Complete the pre-Window-A production-shaped campaign shakedown through doctor, strict validation, reducer 0.4.2, strict revalidation, campaign verdict split, and approved backup; keep extra samplers disabled pending DF-TELEM | No matrix row exists in `docs/phase_2/phase_2_exit_checklist.md` for this precondition; `production_uncertainty_v1` PASSED on merged main at `runs/window_a_shakedown_final` (`request_eligible: true`, reasons `[]`, strict pre+post reduce passed, backup exit 0), pinned in `docs/phase_2/detection_floor.md`; the extra-sampler overhead layer is deferred with DF-TELEM and remains required before enabling extra samplers |
| CAL-REBRACKET-01 | P1 Phase Gate | 2026-07-26 | Implement the governed max(B_pre,B_post) consumption flow so bracketed claim windows are consumable when the post-calibration bound dominates the minted one | No matrix row exists for this consumption gate; merged PR #86 (`7b12f20`) after 3 implementation rounds + 3 independent adversarial audits converging clean; design ruled D2+ (consumption-time authenticated re-derivation, no persisted derived summaries) after two parallel independent consults; replay: windows a9 (7 members) and a10 (37) reach passing consumption with every member widened and point deltas exactly zero; lead full suite 2164 passed / 21 skipped at the rebased head, CI green on all five checks |
| P2-038 | P2 Next Slice | 2026-07-17 | Close the production-uncertainty live tail with a true MLX + `/usr/bin/powermetrics` production-shaped shakedown through strict validation, reducer 0.4.2, strict revalidation, request-eligibility gating, and approved backup | No matrix row exists in `docs/phase_2/phase_2_exit_checklist.md` for this hardening gate; `production_uncertainty_v1` PASSED on merged main at `runs/window_a_shakedown_final` (`request_eligible: true`, reasons `[]`, strict pre+post reduce passed, backup exit 0); drain fixes PR #72 + PR #74; exact `caffeinate -is` command and display-sleep environment pin recorded in `docs/phase_2/detection_floor.md` |
| AXI-SC | P2 Next Slice | 2026-07-17 | AXI stream S-C leg 1: pinned mlx-lm speculative-decode/MTP feasibility spike — verdict `unsupported_for_joulewise` (external draft: `event_observability`; native MTP: `native_mtp_generation`); Mac energy leg not minted, with explicit runtime-upgrade revisit triggers | No matrix row exists in a phase exit checklist for this spike; PR #73 merged; lead-run live probes with evidence + SHA-256 (`docs/process_traces/2026-07-17-axi-sc-live-probes/`); negative applicability verdict filed in `docs/specs/axi/sc_spec_decode_verdict.md`; vLLM leg remains fixture-first PROVISIONAL and outside this filing |
| AXI-SB | P2 Next Slice | 2026-07-16 | AXI stream S-B: pinned mlx-lm static-batch feasibility spike — verdict `supported` (mlx-lm 0.31.3 BatchGenerator path; true B>1 execution with full per-request observability); Mac C5-2.2 leg minted per D-070; follow-on adapter row AXI-SB-ADAPTER minted at rank 4 | No matrix row exists in a phase exit checklist for this spike; PR #70 merged (self-merge under Ed's 2026-07-16 delegation; CI green); lead-run live probes B∈{2,4} with evidence + SHA-256 (`docs/process_traces/2026-07-16-axi-sb-live-probes/`); anti-gaming lens -> fix -> delta 2 blockers (9th fix-rounds-inject-defects datum) -> micro-round -> lead termination (post-hardening live re-probe `supported` at controller_evidence_validation); verdict doc `docs/specs/axi/sb_static_batch_verdict.md`; ledger `docs/stream_logs/2026-07-16-axi-sb.md` |
| SPLIT-AP | P2 Next Slice | 2026-07-16 | Split pre-registration freeze (adjudicated Part I, D-067-reconciled): gross-only primary estimand and headline; both monolithic references mandatory (Holm, intersection-union); pinned idle-sub calculation with D-067 reporting restriction; D-048 predictor over all five gross components; named open gates OPEN-GATE-SPLITAP-PACK-LINT + OPEN-SPLIT-PRED-FIXED-COMPOSITION | No matrix row exists in a phase exit checklist for this pre-registration stream; PR #69 merged `9db4546` (self-merge under Ed's 2026-07-16 delegation; CI green); Sol xhigh impl -> xhigh counterreview -> fix -> delta (caught lead-pinned predictor blocker) -> micro-round -> focused delta -> bench fix -> MR1 -> lead termination; ledger `docs/stream_logs/2026-07-16-split-ap.md` (SPLITAP-1..10) |
| SITE-02 | P4 Polish | 2026-07-16 | Close SITE-01 D1/D2 deferrals: loud structured Lakebed discovery (env + OS-path, exact-version refusal incl. wrong-before-correct PATH ordering, never silent estimator fallback) + node decode regression executing the EMITTED TypeScript via pinned esbuild; D2 guaranteed in CI (release-chain focused step) | No matrix row exists in a phase exit checklist for this site-tooling task; PR #68 merged `2778ed2` (self-merge under Ed's 2026-07-16 delegation; D2 step verified executed in the release-chain CI log, `Ran 1 test ... OK`); Sol high impl -> bug+test lenses -> fix -> delta -> micro-round -> lead termination; ledger `docs/stream_logs/2026-07-16-site-02.md` (SITE02-1..5) |
| AXI-SA | P2 Next Slice | 2026-07-16 | AXI stream S-A: burst-decode metric-semantics contract implementation, stages 0-7 (versioned request-scoped emission events, proposal/acceptance counters, speculation identity, sibling analysis manifest with frozen AP-SPEC denominators, output-identity gate, mock spec adapter last) | No matrix row exists in a phase exit checklist for this contract stream; spec `docs/specs/axi/sa_burst_decode_contract.md` is the authority; Sol xhigh impl, xhigh checker FAIL 5 blockers -> fix -> xhigh delta FAIL 2 -> micro-round -> lead termination (canonical 1626 OK, mock spec-decode e2e replayed at the lead bench); PR #67 merged `7593259` (self-merge under Ed's 2026-07-16 in-session delegation; CI-only portability fix `0914374` reviewed fresh, CI green 5/5); run report `docs/run_reports/2026-07-14-audit-resume-axi.md` |
| AXI-S0 | P2 Next Slice | 2026-07-15 | AXI stream S-0: advisor-facing doc alignment (gross basis+boundary on every number, D-067 attributed rationale, harness/benchmark split, five-axis Q4 agenda, C-023-IDLE-STATIONARITY note, DRIFT.md refresh) | No matrix row exists in a phase exit checklist for this docs stream; kernel row completed (AXI-SA dep satisfied); Sol high impl, fresh checker FAIL 4 majors -> fix round -> delta PASS; freshness+suite green; run report `docs/run_reports/2026-07-14-audit-resume-axi.md` |
| SITE-01 | P2 Next Slice | 2026-07-13 | Site capsule under the 1 MiB Lakebed cap + live redeploy | No matrix row exists in a phase exit checklist for this site-tooling task; PR #63 (gzip shards, measured-artifact postcondition); delta re-audit no-blockers (D3 fixed, D1/D2 → SITE-02); live deploy ACCEPTED at 854,349 B, routes 5/5 200, freshness 14/14 current; reports `2026-07-12-agent-lane-triple.md` + `2026-07-13-restart-merge-deploy.md` |
| P2-028 | P2 Next Slice | 2026-07-13 | Response-hash determinism gate (`joulewise determinism-gate`) | No matrix row exists in `docs/phase_2/phase_2_exit_checklist.md` for this post-checklist gate task; PR #62 + DRA-001 malformed-identity fix; both retained corpus groups formally `determinism_supported`; ledger P2028-1..5; same two reports |
| P2-049 | P3 Hardening Candidates | 2026-07-13 | analysis_manifest.py explicit-root-or-fail-closed resolution (C-028 SF3) | No matrix row exists in a phase exit checklist for this hardening task; PR #61 (lens CLEAN, replay 1261 OK); installed-wheel CI now smokes the refusal (XSI-1 fix on main); same two reports |
| CODEX-BRIDGE-3 | P0 Safety | 2026-07-13 | bridge-protocol/v1.1 for maximum co-work (Ed-directed): discussion lane, session-open/close wrappers, tolerant envelope, per-call reverse effort, peer channels + proposal diffs | PR #65 MERGED `d285989` (Ed-named merge); merged-main suite 1387 OK lead-run; 3 lenses + 3 delta re-audits, findings 13→6→2→1; suite 1387 OK; CI green at `8b96bd4`; D-065; report `2026-07-13-bridge-v11.md` |
| CODEX-BRIDGE-2 | P0 Safety | 2026-07-12 | Make the Claude Code ↔ Sol/Fable bridge bidirectional with adaptive Sol effort (`high` default; xhigh/ultra only by trigger) and a hard one-hop guard | Claude → Sol live `/codex` token `JOULEWISE_SOL_HIGH_GUARDED_OK`, thread `019f5a2a-2f4a-7b33-8a6d-b44dcc5a7a26`; Sol → Fable live `consult_fable` token `JOULEWISE_FABLE_MCP_OK`, thread `019f5a26-d8a6-7993-b48d-8131d88748b9`; protocol checker + 4 focused tests; report `2026-07-12-claude-sol-bridge.md` |
| INT-59 | P2 Next Slice | 2026-07-11 | Bounded integration-review cleanup/ratio-readiness follow-up | No matrix row exists in `docs/phase_2/phase_2_exit_checklist.md` for this integration-review follow-up; PR #59 MERGED 2026-07-11; post-merge main canonical 1,258 OK/10 skipped at `194ea39` (lead-run) |
| DOC-008 | P2 Next Slice | PARTIAL — REOPENED 2026-07-15 | Machine-readable state kernel (schema v3, `AUTHORITATIVE_WORK_SELECTION_STATE` for work selection only) generating the RUN_STATE restart block + live queue view | PR #60's 2026-07-11 completion record is reopened by WO-021 because the original spec conditions were only partially satisfied; phase A adds global gates, independent-oracle fidelity checks, CI drift enforcement, and DOC-010's two-part fence. DOC-008 may not return to complete until every condition in `docs/specs/c027/doc-008_state_kernel.md` §1.1 lands. |
| C-028 | P0/P1 integration arc | 2026-07-11 | Close the #41-#58 hardening + analysis-engine arc; clear the stop card while tracking #59 separately | `docs/run_reports/2026-07-11-c028-continuation.md`; council C-028; D-064; main canonical 1,220 OK/10 skipped; corpus 6/6 |
| C028-SWEEP | P4 consistency | 2026-07-11 | C-002/D-023 end-of-arc consistency sweep and advisor-doc refresh | Same dated C-028 report closeout addendum; `claims_lint --mode all`; diff/scope checks |
| P2-015-PREP | P2 Next Slice | 2026-07-09 | P2-015 detection-floor design doc — combined floors, error budget, telemetry trust, and calibration runbooks | No matrix row exists in `docs/phase_2/phase_2_exit_checklist.md` for this design-doc task; `docs/phase_2/detection_floor.md`; D-054; PR #31; run report `docs/run_reports/2026-07-09-spec-fleshing-wave1.md` |
| P2-029 | P2 Next Slice | 2026-07-09 | Reducer/aggregator uncertainty propagation and claim gates | No matrix row exists in `docs/phase_2/phase_2_exit_checklist.md` for this post-checklist implementation task; D-057; PR #33; run report `docs/run_reports/2026-07-09-spec-fleshing-wave2.md` |
| P2-030 | P2 Next Slice | 2026-07-09 | Ordering executability: rotation policies and order provenance | No matrix row exists in `docs/phase_2/phase_2_exit_checklist.md` for this post-checklist implementation task; D-056; PR #34; run report `docs/run_reports/2026-07-09-spec-fleshing-wave2.md` |
| P2-031 | P2 Next Slice | 2026-07-09 | Token-normalization contract and stack-identity table | No matrix row exists in `docs/phase_2/phase_2_exit_checklist.md` for this post-checklist contract task; D-058; PR #35; `docs/contracts/token_normalization.md`; run report `docs/run_reports/2026-07-09-spec-fleshing-wave2.md` |
| P2-032 | P2 Next Slice | 2026-07-09 | Campaign packs: Q1-Q3 split suite, Q6 rail-vs-wall, and C5-2.3 KV economics | No matrix row exists in `docs/phase_2/phase_2_exit_checklist.md` for this campaign-pack task; PR #36; `docs/campaign_packs/`; run report `docs/run_reports/2026-07-09-spec-fleshing-wave2.md` |
| P2-034 | P2 Next Slice | 2026-07-09 | Broad campaign packs: C5-2.7/2.8, replication runbook, and C5-I.1..I.5 | No matrix row exists in `docs/phase_2/phase_2_exit_checklist.md` for this campaign-pack task; PR #39; six packs in `docs/campaign_packs/`; pack lint errors=0; run report `docs/run_reports/2026-07-09-p2034-broad-packs.md` |
| CODEX-BRIDGE | P0 Safety | 2026-07-09 | Make the Claude Code → Codex bridge durable, full-session capable, and process-safe | Root `AGENTS.md`; tracked Claude subagent + `/codex` command; protocol checker; Claude-approved live `codex` + same-thread `codex-reply` smoke; report `2026-07-09-claude-codex-mcp-bridge.md` |
| RESUME-CP5 | P0 Safety | 2026-07-09 | Resume and complete the CP-5 pre-campaign review session | 7 PRs merged (#22..#28); stop card CLEARED; CP-6 dispositions in the stream log; run report `2026-07-09-cp5-resume.md`; suite 822 OK |
| P2-026 | P2 Next Slice | 2026-07-09 | D-033 strict legacy-bypass close (frozen six-identity allowlist) | PR #22; live-gated 6/6 corpus + tamper-fails + spoof probe fails closed |
| P2-025 | P2 Next Slice | 2026-07-09 | Campaign-runner expected-vs-realized prompt-hash check (+ runtime/validator closure) | PRs #24 + #27; fail-closed with type-discriminated sidecar inference; live-gated classifier truth table; 48/48 real-tokenizer closures |
| P2-010b-GATE | P2 Next Slice | 2026-07-09 | Envelope-gate analysis script (E1-E4 + E5 advisory, D-036 verdicts, CLI) | PR #23; live-gated on the real mock affine bundle incl. refusal cases |
| P2-027-TOOLING | P2 Next Slice | 2026-07-09 | Bundle-pack publication tooling (pack + one-command verify) | PR #25; live pack→verify→tamper→verify(2) |
| CAPTURE-HARDENING | P2 Next Slice | 2026-07-09 | Pre-campaign capture: output token IDs, fail-closed sampler pin (D-047 amendment), model weight hashing, env versions, hash-domain closure | PR #27; live MLX gate incl. two full jw_mixed suite runs |
| P2-012-MANIFESTS | P2 Next Slice | 2026-07-09 | Tokenizer identity widening + real-tokenizer manifest regeneration | PR #26; byte-identical double-regen; counts 512/512 |
| ADVISOR-SITE | P4 Polish | 2026-07-09 | Advisor status site + suite_next draft-spec packet landing (D-051) | PR #28; stop-card sha-verified intact; site regenerated with real renderer |
| P2-018 | P4 Polish | 2026-07-08 | Deploy the site as a shareable Lakebed capsule with live GitHub freshness | Live at https://quiet-signal-6af8833395.lakebed.app; `scripts/pack_capsule.py` + `site_capsule/`; per-source drift vs `main`, fails soft; run report `2026-07-08-lakebed-deploy.md` |
| P2-021 | P2 Next Slice | 2026-07-08 | Drift sentinels + block-position covariates in the 2M generator | PR #15 (merged 8765ee1); fail-loud sentinel manifest; campaign-log covariate echo; run report `2026-07-08-suite-science-expansion.md` |
| P2-017 | P2 Next Slice | 2026-07-08 | Honest per-source site provenance stamps | PR #13 site-observatory rewrite: `git log -1 -- <source>` per page + `+ uncommitted` dirty marker; parser-tested; run report `2026-07-08-site-observatory.md` |
| P2-011 | P2 Next Slice | 2026-07-07 | D-014 cross-repetition uncertainty (aggregate engine + manifest enrichment) | PR #6; lead-verified real n=3 experiment, byte-identical re-derivation; run report 2026-07-07-parallel-streams-session.md; C-006 trace |
| P2-008 | P2 Next Slice | 2026-07-07 | Mock telemetry × SystemClock strictly-interior stamping | PR #5; live-verified at 1 Hz real-MLX; 20 Hz workaround retired |
| P2-009 | P2 Next Slice | 2026-07-07 | Rich telemetry + idle-quality gate + environment capture | PR #4 + INT-002 (8856c04); idle gate first live true positive |
| 2M-TOOLING | P2 Next Slice | 2026-07-07 | Campaign matrix generator + resumable sequential runner | PR #3 + INT-001 (a05e54d); dry-run/resume/crash flows lead-verified |
| KV-SIZE | P3 Research Expansion | 2026-07-07 | Stage 3.0.0 kv-size helper (module + CLI verb) | PR #2; anchors verified against both mirrored models |
| FLAGSHIP-001 | P2 Next Slice | 2026-07-07 | User-directed flagship benchmark: Qwen3.5-122B-A10B-4bit on the M3 Max | 3/3 strict-valid bundles: ~304.0 J gross / ~298.7 J idle-sub per 512-tok request, 582-585 mJ/generated-output-token idle-sub (mean 583.4), 46 tok/s, gross CV 0.3% within one warm-cache session; legacy L1 (bases corrected 2026-07-09, C-027); run report `2026-07-07-flagship-qwen35-122b.md`; first Q4 data point |
| P1-002 | P1 Phase Gate | 2026-07-06 | Mac-local Phase 1 telemetry/runtime evidence — sample captured, fields pinned, D-004 sudoers installed + `sudo -n` verified, MLX installed | Phase 1 exit checklist instrumentation section; fixture committed; live 2I run |
| P2-003 | P2 Next Slice | 2026-07-06 | Mac MLX + powermetrics vertical slice (2G, 2H, 2I) — **first real energy numbers** | Commits `3eb0acd`/`26dca41`/`b4d4173`; 3/3 strict-valid bundles: ~47.2 J gross / ~44.4 J idle-sub per 512-token request, 79.4-90.5 mJ/generated-output-token idle-sub (mean 86.8), 257 tok/s, TTFT ~94 ms; legacy L1 (bases corrected 2026-07-09, C-027; the old 77-88 figure used the prompt+output denominator); run reports 2026-07-06 (buildout, 2H, 2I) |
| P0-002 | P0 Safety | 2026-07-06 | Measurement-corpus backup protocol (R-016) — interim destination per user direction | `scripts/backup_runs.sh`; restore test green (`validate-bundle` on restored copy); protocol in R-016; follow-up P0-003 tracks the real destination |
| P3-001 | P3 Research Expansion | 2026-07-06 | Background/related-work draft (Phase 4 Stage 4.6) | `docs/phase_4/related_work_draft.md`: 11 sources, independently verified citations, positioning claims honestly adjusted (claims 1-2 narrowed, claim 3 stands) |
| 2G (P2-003 part) | P2 Next Slice | 2026-07-06 | MLX runtime adapter — first real generation traces on the M3 Max | Commit `3eb0acd`; succeeded bundle `example-mac-mlx-mock-telemetry` (TTFT 81.5 ms, 265.8 tok/s, `--strict` valid); suite 230 OK both interpreters; implemented by Codex via `scripts/codex-bridge`, reviewed + live-verified by Claude |
| DOC-006 | P2 Next Slice | 2026-07-06 | Independent status-review intake (user-directed): all three findings verified and fixed — P1 event-timestamp hardening, P2 `validate-bundle --strict` (D-030), P3 adapter raw-write helper | Review `2026-07-06-project-status-review.md`; fixes run report `2026-07-06-status-review-fixes.md`; 226 tests OK |
| P2-007 | P2 Next Slice | 2026-07-06 | Slice 2N pre-hardware hardening (all nine items, three commits) | Run report `2026-07-06-slice-2n-pre-hardware-hardening.md`; D-024..D-029; 216 tests OK; exit-checklist 2N row closed |
| DOC-005 | P4 Polish | 2026-07-06 | External architecture review intake (user-directed): D-024 RunContext, D-025 shared bundle reader, node-worker protocol contract, 2N items 8-9 | Run report `2026-07-06-architecture-review-intake.md`; `docs/contracts/node_worker_protocol.md` |
| DOC-004 | P4 Polish | 2026-07-05 | Agent playbook (user-directed): per-mission execution guides for all remaining steps | `docs/agent_playbook.md`; pointers in `README.md`/`AGENT_PLAN.md`; Stage 4.6 seeded with named competitor set |
| P0-001 | P0 Safety | 2026-07-05 | Move repo off iCloud-synced Desktop (R-017) | New path `~/code/CapstoneRivoire/Capstone`; git + suite verified green at the new location; recorded in `RUN_STATE.md` |
| DOC-003 | P4 Polish | 2026-07-05 | Docs/meta-layer cleanup (user-directed): drift fixes, D-023 status consolidation, plan/guide dedup, R-016/R-017, Slice 2N + Stage 4.6 planned | Run report `2026-07-05-docs-meta-cleanup.md`; D-023; risk register updated |
| P2-001 | P2 Next Slice | 2026-06-12 | Mock vertical slice: slices 2A-2E | Harness runs end-to-end; `validate-bundle` green; CI mock e2e step added; 169 tests. `joulewise/{bundle,clock,controller,reduce,cli}.py` + `adapters/`; run report `2026-06-12-phase-2-mock-vertical-slice.md` |
| P2-002 | P2 Next Slice | 2026-06-12 | Repetitions + experiment manifests (slice 2F) | `run_experiment` + cooldown gate; 3-rep + kill-after-rep-2 + cooldown tests; manifest per D-005. Same run report |
| P2-J | P2 Next Slice | 2026-06-12 | Static report generator (slice 2J) | `joulewise/report.py`; matplotlib behind `[analysis]`; graceful structured failure when absent; tests skip cleanly without the extra |
| P1-005 | P1 Phase Gate | 2026-06-12 | Hailo feasibility verdict | `unsupported_workload` from official-source desk research; recorded in the Phase 1 exit checklist Hailo section |
| P1-007 | P1 Phase Gate | 2026-06-12 | Phase 2 readiness review | Recorded in the Phase 1 exit checklist; verdict "mock-first Phase 2 may begin" |
| Q-000 | P0 Safety | 2026-06-09 | Resolve the local `Energy_Benchmark_Architecture.docx` deletion decision | User confirmed the Word doc was unrelated; deletion committed in `a5d7404` |
| PLAN-001 | P1 Phase Gate | 2026-06-09 | Build evidence-shaped plans for Phases 2-5 (user-directed) | Per-phase plan + exit-checklist docs; `docs/decision_log.md` (D-001..D-019); `docs/risk_register.md`; `docs/milestones.md`; methodology/bundle-layout amendments; `AGENT_PLAN.md` restructured as index; run report `docs/run_reports/2026-06-09-phase-2-5-planning-buildout.md` |
| CI-001 | P2 Next Slice | 2026-06-09 | Add core-tests CI workflow (D-017) | `.github/workflows/ci.yml`; extended 2026-06-12 with the mock end-to-end run |
| DOC-001 | P4 Polish | 2026-06-09 | Unify Phase 1 doc scheme with Phases 2-5 (user-directed) | `docs/phase_1/` reduced to `phase_1_plan.md` + `phase_1_exit_checklist.md`; contracts moved to `docs/contracts/`; run report `docs/run_reports/2026-06-09-phase-1-doc-unification.md` |
| DOC-002 | P4 Polish | 2026-06-09 | Add advisor-facing status/plan/architecture doc + audit original sketch (user-directed) | Root `PROJECT_STATUS.md`; run report `docs/run_reports/2026-06-09-advisor-status-doc.md` |

## Shelved Follow-Ups With Triggers (C-027 disposition ledger — REV-10)

- **SOL-FAST-TIER (verified 2026-08-03, Ed aside):** Codex FAST MODE
  works on live Sol calls: `-c service_tier=fast` accepted at the bench
  (documented: 1.5x speed, 2.5x ChatGPT-credit consumption on GPT-5.6;
  `/fast on` interactively; persist via config `service_tier="fast"` +
  `[features].fast_mode=true`). `-c service_tier=priority` (API
  priority tier) also accepted. `~/.codex/config.toml` stays pinned
  `default`; NOT built into any process per Ed. Trigger: latency-
  critical Sol runs (live debugging, Ed-waiting consults) may pass the
  flag per-call; any standing default change is Ed's call (2.5x quota
  burn interacts with the usage-pressure memory).

Previously promised follow-ups whose queue rows had silently died; each
now has an explicit disposition:

- D-013 SSH-controlled vs co-resident controller comparison — SHELF,
  trigger: first 2K live session (validation cell rides that session).
- Empirical corpus for the 0.40 GPU-idle contamination threshold — SHELF,
  trigger: Window-A calibration data exists (P2-015 output feeds it).
- `dvfm_states` slimming option — SHELF, trigger: bundle-size pain during
  the 2M campaign; otherwise declined as premature.
- Cold-load / model-load-energy capture — DECLINED for the capstone scope
  (CP-5 deferral made permanent unless an AP row claims it; warm-cache
  protocol is the declared scope).

- CI-003 developer polish (console script, macOS CI job, Ruff, coverage thresholds) — SHELF, trigger: G6-equivalent reference release (hardening adjudication C10).
- DOC-010 historical-archive audit — SHELF, trigger: DOC-008 state kernel proven in use (hardening adjudication C11).

## Current Do-Not-Do-Yet List

- (satisfied 2026-06-12) The mock bundle/reducer path and report generator
  now exist; dashboard/report work is no longer blocked.
- (satisfied 2026-06-12) The mock lifecycle is runnable, so live
  MLX/powermetrics implementation may proceed once its hardware gates open
  (P1-002 + D-016); follow `docs/phase_2/hardware_slice_implementation_guide.md`.
- (resolved 2026-06-12) Hailo feasibility has a verdict
  (`unsupported_workload`); do not implement a Hailo backend — report it as
  an applicability finding.
- Do not implement schema v0.2 before Phase 3 Stage 3.1 (design is fixed in
  D-008; implementation waits).
- Phase 3 DESK feasibility spikes (Stage 3.0.x) may run now — their gate
  (2G/2I + model) is open. Do not start Phase 3 DATA collection, hardware
  pairings, or borrow-window scheduling before 2M baselines and the Stage
  3.0 verdicts exist (C-007 wording fix; was previously stated as a
  blanket Phase 3 hold that contradicted the queue).
- Do not schedule the 3080 Ti borrow window before Stage 3.0 verdicts and the
  rehearsed runbook exist (R-006).
- Do not start Phase 3 live-split work (3.3) before offline replay (3.2) has
  produced data.
- Do not close D-016 (model selection) without P1-001 supervisor scope or an
  explicit user go-ahead.
- (satisfied 2026-07-06) Slice 2N landed; 2G/2H may start once their own
  gates (D-016 + `[mac]` install; privileged sample + D-004 sudoers) open —
  build on the post-2N seams (RunContext raw evidence, D-026 markers,
  D-027 rail rows, 2N.3 observed-token fallback).

## Queue Maintenance

At the end of substantial work:

- Update live status, rank, dependencies, and new tasks in
  `docs/process/state_kernel.json`.
- Remove terminal tasks from the kernel only after their owning completion
  evidence supports closure; preserve the dated Completed row here.
- Run `python3 scripts/gen_state.py`; never hand-edit generated queue or
  restart rows.
- Keep hand-authored edits here to policy, completed/history records, and
  non-selection context.

## Intake Batch Owed To The Kernel (2026-07-30/31)

**PARTIALLY FOLDED 2026-07-30.** Six rows —
`COOLDOWN-JOIN-GAUNTLET-01`, `QA-10A-JOIN-OMISSION`,
`QA-10B-EXISTING-RETRY`, `MINT-GENERALIZE-01`, `MANIFEST-CONTRAST-01`,
and `SUPERSESSION-DUP-REFUSAL-01` — were folded into
`docs/process/state_kernel.json` on 2026-07-30; their staged rows were

exec
/bin/zsh -lc "sed -n '1,260p' RUN_STATE.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
# JouleWise Run State

This file is the single running pointer for the project: the one doc to
read to get back here. Session records live in `docs/run_reports/` and
`docs/process_traces/`; deliberation lives in `docs/council_log.md`;
policy lives in `docs/decision_log.md`. The three dated restart docs
`docs/process_traces/RESUME-2026-07-26.md`, `RESUME-2026-07-27.md`, and
`RESUME-2026-07-28.md` are now point-in-time session records only — each
carries a superseded banner, and everything still current in them is
folded in below. Do not create another dated restart doc; update this
file instead.

Last updated: 2026-08-07 — **LIVE SESSION (14h Ed window). Read this
block first;** the 2026-08-06 checkpoint below is executed history.

## ⏳ 2026-08-07 — paper-first session (LIVE; interim block, refreshed mid-flight)

**Ed's directives this session:** (1) abandon t3 work; (2) MVP capstone
paper FIRST, rest later; (3) 14h autonomous window; (4) three quiet
nights + desk work accepted as the path → **D-117 transcribed+pushed**
(D-110 re-mint order superseded; three prospective windows; prefill
floors ride floor windows; contrast decode-only; 256-tok prefill arm
still Ed's option); (5) Workflow license for non-serial desk work.

**DONE this session (all pushed):** checkpoint resume items 2-4 —
T3-CHAR-PAIR r01/r02 analysis banked (`fc48b1b`, dormant floor 0.192 W,
NON-CLAIM); prefill feasibility scout MARGINAL-at-128-tok custodied
(`docs/process_traces/2026-08-07-prefill-feasibility/`); C-049 marathon
council record (`03841c8`); skill-usage log; D-117 (`dbb9685`);
CLAIMS_STATUS un-staled (`a1f0e19`).

**IN FLIGHT (harvest, do not re-run):** (a) paper fix round on branch
`impl/paper-mvp-complete` — Sol xhigh, WRITE_SCOPE
docs/paper/draft-v1.md, closing round-2 findings (lens A 3 blockers:
tense, two-gate rule collapse, prefill-marginality misstatement; lens B
11; F-BIB-1) — review records + bibliography audit custodied on the
branch (`3542265`, `1892edc`); on harvest: lead diff gate → delta
re-audit → PR → merge on green (D-072). (b) Plan-freeze design consult
(Sol xhigh, read-only, scratchpad desk worktree) for the three-window
packet → on return: lead ratify → enforced-scope implementation units →
adversarial review → PR(s). Then: three-night operator packet for Ed;
end-of-session sweep + run report.

**Worktrees:** `<session-scratchpad>/desk` (main, bookkeeping) — prune
at close. Main tree holds `impl/paper-mvp-complete`.

## ✅ CHECKPOINT 2026-08-06 late — machine-move stop (resume script)

**Nothing in flight; nothing unpushed after this commit.** All background
jobs harvested; consult custodied; campaign logs sha-verified untouched.

**STATE IN ONE BREATH:** PR #109 merged (`c537386`); first consumption
attempt proved the historical re-mint structurally closed at main (see
AFTERNOON block + `docs/process_traces/2026-08-06-d110-remint-fork/`);
Sol xhigh + magistrate recommend Option 2 (three fresh prospective
windows); **Ed has NOT yet ruled** — he was probing costs when the
session stopped.

**Ed's in-thread directives this exchange (record, not yet decision-log):**
1. **MVP claim scope: "a little more than just decode, at least
   decode/prefill."** Magistrate's proposed shape (not yet Ed-acked):
   prefill FLOOR cells ride both fresh floor windows cheaply; a prefill
   CONTRAST first gets a labelled non-claim desk feasibility check from
   historical diagnostics against the D-078 ~5 J effective bar — if it
   clears, the contrast window grows a prefill ABBA arm; if not, prefill
   floors are claimed, contrast stays decode-only, and the infeasibility
   becomes a limitations paragraph.
2. **Ed challenged the zero-agent window rule** ("why can't you be
   running quietly?"). Owed answer components, for the successor: (a)
   physics at our bar — a bursty resident agent stack at ~0.1–0.5 W over
   minute-scale members is joules-to-tens-of-joules gross vs a ~5 J
   effective bar; idle subtraction cancels only the steady part; every
   CLAIM window to date was zero-agent; the app-resident mode was only
   ever used for fenced NON-claim characterization. (b) The banked
   `runs_char_t3appup_20260804_r01/_r02` captures exist precisely to
   QUANTIFY the dormant-app delta — **desk analysis queued (protocol
   §Analysis: mean/p95 package power from rich_telemetry_idle.jsonl)**;
   run it and give Ed a NUMBER. (c) The honest reframe: the binding
   presence constraint is §5A's sudo (network-time toggle), not the
   zero-agent rule; the agent-armed window design (QUIET-GUARD two-phase
   handoff, commits 2–4 + a scoped sudoers rule for the two systemsetup
   commands) exists and was descoped by Ed's OWN ruling as not worth the
   security-critical code — reopenable on his word if three fresh
   windows change his calculus.
3. Ed confirmed understanding that Option 2 = recollect the science
   windows (~3 windows, bookend-presence only) while everything else
   (instrument arc, acceptance rule, tooling, process record) stands.

**RESUME ORDER for the successor:**
1. If Ed has ruled the fork → transcribe the decision (supersede/amend
   D-110 + D-113 rewire per SYNTHESIS.md) and start the Option-2 desk
   queue (AFTERNOON block bottom). If not ruled → he owes: fork ruling,
   prefill-contrast shape ack, three-nights scheduling.
2. T3-CHAR-PAIR r01/r02 desk analysis (the dormant-app number) — cheap,
   answers his live question, informs any zero-agent-rule revisit.
3. Prefill-contrast feasibility desk check from historical diagnostics
   (labelled, non-claim).
4. End-of-session bookkeeping STILL OWED from the marathon session:
   consistency sweep, council log, skill-usage log.

## ⏳ 2026-08-06 AFTERNOON — re-mint fork: historical consumption is closed at main; Ed's ruling owed

**PR #109 merged on green** under D-072 at the gate-reviewed head
`d85b4f9` (no post-review commits; ledger + custody backup verified
byte-identical to the checkpoint sha before merge). `d079recon`
worktree + local branch pruned. All three D-110 conditions were thereby
satisfied — and the FIRST consumption attempt exposed a structural
block.

**THE FINDING (full record:
`docs/process_traces/2026-08-06-d110-remint-fork/` — DIAGNOSIS,
consult prompt+response, SYNTHESIS):** no historical window (a10,
window-C, old window-D, 7B-floor, contrast — all pre-genesis) can pass
authenticated max-bracket consumption at merged main. The issued ledger
holds only import-marked receipts; candidate discovery excludes imports
by design (CAL-BRACKET arc `63f43a68`, retained through issuance);
future live receipts cannot causally bracket past windows. Every
refusal was fail-closed; campaign logs sha-verified untouched (backups
in `~/JouleWise-window-custody/d110-remint-20260806/log_backups/`).

**Sol xhigh pre-decision consult (run `20260806T165843Z-10884`) +
magistrate CONCUR: Option 2 — supersede the D-110 historical re-mint
with THREE compact prospective windows** (fresh 1.5B decode floor,
fresh 7B decode floor, fresh contrast; each live-bracketed under the
issued regime, ~3 h class each). Chain: historical corpus → issued
acceptance rule → live brackets → prospective floors → contrast.
Option 1 (finite-allowlist historical candidacy) preserved as a
cold-gated contingency only — semantics sketch is in the consult
response. The consult verified all five historical bracket pairs exist
physically (drifts 0.000167–0.003680 s, under the 0.010818 s screen) —
the objection is provenance completeness, not causality.

**ED OWES (his ruling moots a cold gate — apex authority):**
1. Ratify superseding D-110's re-mint order with prospective
   replacement (+ the D-113 dependency rewire the consult flags).
2. MVP claim scope: decode contrast only, or more phase cells?
3. Three quiet-mac nights scheduling appetite (§5A each).

**Desk work unblocked regardless (consult §4, queue for the successor):**
freeze the three window plans + budgets (new immutable identifiers —
"Window D" name is taken); 1.5B decode-only floor plan from the proven
10-absolute/40-null design; generalized mint pinsets w/ per-plan
six-decimal literals (the D-084 literal `7.377086` refuses any
corrected mint under EVERY option — closure is per-plan supply via the
generalized path); freeze extraction specs/order manifests/
evidence-root ids/contrast manifest; synthetic three-window live-ledger
integration regression; D-102 successor-artifact packet; results/
methods prose with placeholders.

**Session ops notes:** verdict/extraction tooling gotchas (relative
`--runs-dir` path-doubling; verdict >2 min; stale `campaign.lock` on a
killed run) are recorded in the trace DIAGNOSIS. End-of-session
bookkeeping (consistency sweep, council log, skill-usage log) still
OWED.

## ✅ CHECKPOINT 2026-08-06 morning — executed by the afternoon session above

**IMMEDIATE RESUME ACTION (one live item):**
1. **PR #109 (`impl/d079-issuance`) — merge on green, then RE-MINT.**
   This PR ISSUES the D-079 calibration acceptance artifact (the
   authentication anchor for all floor-mint claims): D-116, issued
   config (fixture→issued, file sha `316113960c…`), committed head-pin
   (seq 76 / head `08456d50…`), cold-gate custody, + a 5-file test
   reconciliation. It cleared its FULL gauntlet (two rule-11 cold gates,
   adversarial audit + 3 delta rounds, exact-bytes dual cold review,
   zero-regression reconciliation + coverage-preservation audit ACCEPT).
   At checkpoint: CI running. **On green → self-merge under D-072**
   (it's the completed gate shape). If a successor finds it already
   merged, skip to the re-mint.

**THE AUTHORITATIVE LEDGER — do not lose (survives /clear as a file):**
- `runs/calibration_observation_ledger.jsonl` — the 76-receipt genesis
  chain, **git-ignored** (local custody artifact), sha256
  `aa80684848d0ce156ed2d14df47472006175840eda17f9025eff9754af694e3f`.
  BACKED UP at `~/JouleWise-window-custody/d079-issuance-20260806/`
  (byte-identical). Deterministic from the custodied inputs
  (`docs/process_traces/2026-08-06-d079-issuance-coldgate/ISSUANCE-*`,
  on the PR branch → main after merge) + raw evidence. The committed
  head-pin (in the config) is the D-109 R1.4 trust anchor; the ledger
  file itself is a custody artifact. **Must stay backed up before the
  re-mint consumes it.**

**THE RE-MINT (task 8, the payoff — next after PR #109):**
- D-110 conditions now ALL satisfied: (a) PR #100, (c) PR #105, (b) THIS
  issuance. MINT-GENERALIZE-01 UNBLOCKED. Next: ONE custody session —
  governed a10 phase-floor extraction
  (`configs/floor_mint/a10_extraction_spec.json`, ~20 min) THEN mint #1
  re-derivation under the corrected selector, embedding the never-zero
  `A_s = max(observed_drift_s, 0.010818)` allowance (D-102 pin 3 /
  D-110). Same custody session (FLOOR-BIND-01 fence). Claim-critical →
  full gauntlet. Output: non-empty claims table (CLAIMS_STATUS §1) +
  the labelled a10 phase floors (D-078 cl.11) + the 1.5B-vs-7B decode
  contrast (frozen metric `phase_energy_j.decode`, NOT the 146.73 J
  diagnostic). THIS is the MVP demonstration (Phase 3 measured data).

**AFTER THE RE-MINT:** paper results section (task 12, results C-v +
limitations from the minted numbers) → assemble A+ MVP draft (methods
already on main: `docs/paper/draft-v1.md`).

**This session's landed work (all merged to main + pushed):** PR #102
Codex Fast Mode (`CODEX_SERVICE_TIER=fast`), #103 coldgate validator,
#104 registration batch, #106 ledger-bootstrap infra, #107 QUIET-GUARD
commit 1, #108 issuance consumer; decisions D-113 (Window B terminally
claim-retired), D-115 (quiet-guard Q2 authority), D-116 (D-079 issuance,
on PR #109). Two rule-11 escalation consults (CGV F3 closure, QG census
Option C) — records in `docs/process_traces/`.

**Ed's standing directives this session (all durable — memory + here):**
- **Priority stack (BINDING):** P1 the A+ MVP paper, P2 the ICPE
  version, P3 modularity for future inference-technique research
  questions — P3 SACRIFICED if it costs P1/P2. (memory
  `paper-first-priority-stack`.)
- **Syllabus (advisor Rivoire — JouleSort author, sets the metrology
  bar; memory `advisor-rivoire-joulesort`):** Phase 1 (system) DONE;
  Phase 2 (outline+related-work) DONE (draft-v1 on main); **Phase 3
  (>=1 experimental section WITH measured data) = LIVE TARGET** = the
  re-mint demonstration; Phase 4 full paper.
- **Venue ceiling:** ICPE full research track is the realistic ambitious
  target (best fit + Rivoire's community); top-tier only if a mechanism/
  split research bet lands. Full ranked roadmap:
  `docs/strategy/2026-08-06-impressiveness-roadmap.md`.
- **Wall meter:** D-092 ratified it as claim C8; Yokogawa WT310E (~$2935
  new, ~$1-1.5k used), get Ethernet; BORROW from Rivoire's lab first;
  TWO (one per machine) only for the split-inference stretch (both boxes
  colocating). NOT required for the A+ MVP.
- **Sol effort:** high/xhigh per complexity (cap lifted); Fast Mode
  (2.5x credits) on xhigh via `scripts/codex-bridge` only (codex-run-v3
  does not read it — do not modify Ed's personal wrapper).

**Cleanup for the successor:** one scratchpad worktree remains
(`…/scratchpad/d079recon` on `impl/d079-issuance`) — prune after PR #109
merges. The end-of-session bookkeeping (task 9: consistency sweep,
council log, skill-usage log) is still OWED — do it after the re-mint.
Nothing critical is unpushed; main is clean.

---

Last updated: 2026-08-05 LATE NIGHT — Fable magistrate session resumed
from the NIGHT checkpoint. Read the LATE-NIGHT block first; the NIGHT
and EVENING blocks below it are still-valid history.

## ⏳ 2026-08-05 LATE NIGHT — Fable resume: all 4 audits harvested, D-115 adjudicated, two Sol rounds in flight

**Harvest complete** — all four checkpoint audits finished and are
copied to `.desk/2026-08-05-checkpoint-audits/` (cgv-audit-A/B,
qg-audit-A/B; qg-audit-B's `.status` semantic fields failed to parse but
its report envelope is present, final, and well-formed — wrapper
artifact, noted).

**COLDGATE-VALIDATOR-01** — cgv-audit-B (oversight/prune lens) reframes
F3 entirely: B1 blocker (PASS receipt does not bind the judge to the
validated bytes — post-validation exhibit substitution), S1 fenced-
heading false refusals, S2 --help receipt violation, and a prune
recommendation to DELETE the attestation privacy subsystem F3 lives in
(free-text attestation fields discriminate no registry invariant). Per
the rule-11 escalation trigger, a **Sol design consult is IN FLIGHT**
(read-only, high — rule-10 tier is xhigh, Ed's Sol-HIGH-only directive
controls, deviation recorded) on: closure shape (refuse-all-slashes vs
allowlist vs delete-the-subsystem), B1 scope (in-branch vs CGV-HARDEN-01
sibling row), S1/S2 disposition, regression vectors. Magistrate's

exec
/bin/zsh -lc 'git status --short --branch' in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
## main...origin/main

exec
/bin/zsh -lc 'wc -l "docs/paper/draft-v1.md" "CLAIMS_STATUS.md" "docs/decision_log.md" "docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md" "docs/strategy/2026-08-06-impressiveness-roadmap.md" "docs/research_question_registry.md" "docs/research_question_bank.md" "docs/process_traces/2026-08-07-prefill-feasibility/SYNTHESIS.md"' in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
     194 docs/paper/draft-v1.md
     179 CLAIMS_STATUS.md
    7566 docs/decision_log.md
     489 docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md
     214 docs/strategy/2026-08-06-impressiveness-roadmap.md
     134 docs/research_question_registry.md
    1095 docs/research_question_bank.md
      33 docs/process_traces/2026-08-07-prefill-feasibility/SYNTHESIS.md
    9904 total

exec
/bin/zsh -lc "sed -n '1,240p' docs/paper/draft-v1.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
exec
/bin/zsh -lc "sed -n '1,120p' docs/process_traces/2026-08-07-prefill-feasibility/SYNTHESIS.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
# Prefill-contrast feasibility desk check — synthesis (2026-08-07)

Sol scout (read-only, high, gpt-5.6-sol) over historical diagnostics;
prompt + full response in this directory. ALL NUMBERS NON-CLAIM /
DIAGNOSTIC.

**Verdict: MARGINAL at the historical 128-token workload.** Best-evidence
matched ABBA diagnostic (decode-contrast window's off-manifest prefill
field, 20v20 members, identical prompt hash): 7B−1.5B prefill delta
5.809930 J point vs the ~5 J practical bar (D-078 cl.11 / D-083 wording
control — two separately enforced gates, not one summed threshold);
composed contrast half-width ~1.81 J puts the interval lower edge ~4.0 J,
BELOW the bar. Independent cross-window subtraction corroborates
(5.903 J).

**Length is the lever:** 1.5B prefill scales ~proportionally with prompt
length (128→4096 tokens predicts within ~3.3%); a prospectively frozen
256-token prompt projects ~11.6 J (~2.3× bar). NO long-prompt 7B corpus
exists — the projection is an extrapolation and workload resizing is a
preregistration decision (estimand change).

**Recommended default (scout + magistrate CONCUR):** claim prefill
FLOORS; keep the model contrast decode-only; state the 128-token
marginality as a limitation. The 256-token contrast is Ed's ruling
(needs_ruling row): +~110 core minutes, likely splits into its own
window.

**Consumed by:** the MVP paper draft §7 "Prospective workload sizing"
(qualitative, no diagnostic joules quoted per the draft's
no-demo-values discipline) and the pending fork/window planning.
Scout flags F1 (D-083 wording preserved), F2 (no long-prompt 7B
evidence), F3 (CLAIMS_STATUS staleness vs D-116 — check before window
freeze) all noted.

 succeeded in 0ms:
# JouleWise: Detection Floors for LLM Inference Energy Measurement on Consumer Silicon

## 1. Introduction

Energy numbers for large language model (LLM) inference now appear in leaderboards, systems papers, product comparisons, and policy debates. Published estimates for apparently similar queries can differ by an order of magnitude, yet the numbers are rarely accompanied by an error bar that says how small a difference the measurement method can actually distinguish. This omission is especially consequential on consumer hardware. Apple's `powermetrics` utility makes processor power estimates available without a laboratory meter and is therefore attractive for repeated experiments, but, to our knowledge, it has not been validated in published work as an instrument for separating the energy of LLM inference phases. Apple describes its outputs as estimates; treating them as exact readings can turn timing uncertainty at a phase boundary into a spurious energy difference.

The core difficulty is physical as much as statistical. Energy is the integral of power over time. An experiment may repeat consistently and still assign energy to the wrong phase if a power sample near the boundary between prompt processing and token generation is placed on the wrong side. Averaging more repetitions reduces random scatter but does not remove that attribution error. Slow changes in thermal or background state can add a second false difference over a long collection session.

We argue that a software power counter should be treated as a scientific instrument rather than as a logging convenience. The instrument must be calibrated in the same session in which it is used; each reported result must carry a detection floor, meaning the smallest false effect that the calibrated method could plausibly produce under the stated conditions; and the analysis must decline a directional claim when the observed effect cannot clear that floor and its own measurement uncertainty. JouleWise implements this discipline for phase-resolved, single-request LLM inference on one named Apple-silicon machine and software stack. The runtime emits the phase boundaries because it drives the workload, while `powermetrics` supplies the power samples integrated between those boundaries.

This scope is deliberately narrow. A measurement characterizes one physical unit, operating-system build, runtime and library stack, model artifact, quantization, tokenizer, sampling policy, single-request execution policy, telemetry backend, and measurement boundary. It does not establish that an Apple hardware class or vendor is more efficient than another platform. Without an external power meter, absolute values remain internal to the named `powermetrics` system-on-chip boundary; same-boundary contrasts can still be scientifically useful when they pass the calibration and floor gates. Gross joules per request are the primary energy metric. Joules per prompt or output token are tokenizer-scoped companion metrics and are never treated as tokenizer-independent work units.

This paper makes the following contributions:

1. (C-i) an in-window calibration method that measures timing-attribution error for phase-resolved energy integration;
2. (C-ii) detection floors composed from measured repeatability, worst-case attribution, and measured drift — published with every result;
3. (C-iii) a fail-closed collection protocol (admission gates, ABBA ordering, custody chains, pre-registration) with its refusal log as evidence;
4. (C-iv) full instrument characterization: linearity, null response across magnitudes, empirical floor verification, phase-attribution causal consistency, drift/settle;
5. (C-v) demonstration measurements: phase-resolved J/token for two model sizes with a pre-registered contrast [+ quantization ladder if window budget allows];
6. (C-vi) open tool + hash-bound reproducible artifacts.

## 2. Background and the gap

### Energy-benchmarking rules

The first relevant lineage is formal energy benchmarking. MLPerf Power and the associated Standard Performance Evaluation Corporation methodology treat uncertainty and validity as properties of each measured run. They require a qualified analyzer, uncertainty evaluated at the observed load, fixed measurement ranges, synchronized clocks, sufficiently long intervals, invalid-sample accounting, and explicit treatment of battery-backed systems [MLPerfPower]. These rules establish an important principle: a benchmark result is not valid merely because the meter has a specification sheet. The evidence recorded during the run must show that the measurement operated inside its accepted conditions. These standards, however, assume external instruments and data-center-style workloads; they do not provide a method for validating phase boundaries reported by a software counter on a consumer system.

### Software-counter validation

The second lineage validates software-visible energy counters against external power. Intel's Running Average Power Limit (RAPL) counters have been studied through lag alignment, regression against wall power, counter-resolution tests, sampler-overhead audits, and thermal controls [RAPLInAction]. Jay and Ostapenco's CCGRID 2023 study likewise shows that the gap between a software meter and wall power can depend on load rather than behave as one fixed offset, and it refrains from component-level conclusions when no reference instrument observes the component [JayOstapenco]. This work provides a strong model for whole-machine scale validation. It does not define a detection limit for a reported effect, does not validate `powermetrics` on Apple silicon, and cannot by itself establish whether software samples were assigned to the correct LLM phase. A wall meter observes a total; phase attribution needs a separate timing experiment.

### LLM energy studies

The third lineage measures LLM energy across models, hardware, and workloads. TokenPowerBench reports prompt-processing and token-generation energy with phase-appropriate token denominators; ML.ENERGY, Silicon Showdown, and Intelligence-per-Watt broaden empirical coverage across deployed systems [TokenPowerBench; MLENERGY; SiliconShowdown; IntelligencePerWatt]. This breadth makes inference energy visible, but the nearest studies do not jointly characterize counter timing, repeatability, drift, and the minimum resolvable effect. Phase labels are consequently easy to read as exact even when the method does not report the boundary events, alignment uncertainty, or a floor below which a difference should be refused.

The specific gap is therefore not another energy table. To our knowledge, no published work combines phase-resolved LLM energy on consumer silicon, a per-measurement error budget, and validation of `powermetrics` timing attribution under its named measurement boundary (as distinct from validating its absolute counter gain or whole-system energy scale, which would require an external meter). JouleWise fills that gap by making instrument characterization and refusal behavior the primary result; model comparisons are demonstrations of what the characterized instrument can and cannot resolve.

## 3. In-window calibration method (C-i)

### Measurement model and boundary

JouleWise measures one sequential request at a time. Prompt processing (often called *prefill*) converts the input sequence into the model's internal state; token generation (often called *decode*) produces output tokens from that state. Because the experiment controls the runtime, it records the start and stop of these phases directly in the runtime event stream rather than inferring them from shapes in the power trace. The reducer then integrates the named `powermetrics` system-on-chip power channels between each pair of phase events using trapezoidal integration.

The runtime and the telemetry sampler do not share a perfect clock. Operating-system launch latency, timestamp anchoring, and the sampler's averaging behavior can shift an apparent edge. A phase-energy estimate must therefore be an interval, not only a point. The calibration asks a concrete question: if software commands a load pulse at a known time, how far can the rising and falling edges of that pulse appear displaced in the sampled power trace?

### Bracketed pulse-train calibration

Immediately before and after every claim-bearing collection window—that is, a window eligible to support a reader-facing scientific claim—JouleWise runs a fresh pulse-train calibration under the same machine, operating-system, power-supply, and telemetry state as the science workload. The current protocol commands 59 graphics-processor matrix-multiplication pulses. Their durations are fixed in advance, their gaps follow a deterministic low-discrepancy schedule rather than a single repeated period, and quiet baselines of at least 4.5 seconds separate the fitted regions. The varied schedule reduces the risk that the calibration accidentally locks to the telemetry sampler's cadence. The 59-pulse design supports the pre-registered nonparametric 95/95 bound: a conservative bound intended to cover at least 95% of the calibration population with 95% confidence under the stated transfer assumptions.

For each pulse, the estimator compares the commanded interval with the observed power plateau and fits the start-edge and stop-edge lags independently. This distinction matters. A common shift of both edges may leave pulse energy nearly unchanged, while an early start combined with a late stop can add energy at both boundaries. The calibration therefore retains a bound for the instrument's edge-placement error rather than collapsing the evidence to one best-fit lag.

Each science member, meaning one recorded workload run, also carries a local bound on how its runtime clock is anchored to the trace, including the observed span between wall time and a monotonic clock that is not adjusted by network synchronization. For a reported phase, the analysis combines the member-local common shift, the calibration edge bound, and the clock-span term. It evaluates the energy integral at all four combinations of early and late start and stop edges, while scanning the allowed common shift exactly. The minimum and maximum of those integrals form the admissible energy interval. The physical intuition is simple: the interval asks how much energy could move into or out of the phase if both boundaries were placed at their most adverse calibrated positions.

The pre- and post-window calibrations form a bracket around the measurements. Both must be authenticated, fresh, and causally outside the science interval. The operative bound is the larger of the two. Separately, the absolute difference between the pre- and post-window calibrations is screened against a derived bracket-drift limit of about 10.82 ms: a small repeatability-only excess is propagated into every floor and claim, while an identified systematic defect cannot be absorbed by that budget. If the post-window bound is larger than the one used when a member was first reduced, the member must be re-reduced through the pre-specified path with the wider bound or it cannot support a claim; metadata is never patched to make the bounds agree. A pre-flight level screen also runs before the first science member. It rejects a calibration whose fitted lag is outside the previously characterized family, such as a graphics-processor frequency ramp that the pulse model could mistake for a timing shift. A retry is allowed only after a specific cause is identified and removed, within the retry count frozen before collection. Repeating merely until a favorable calibration appears would be selection on the outcome.

This procedure validates timing attribution, not the gain of the power counter. The pulses are graphics-processor matrix multiplications under a relatively light central-processor load, so transfer of their timing bound to sustained mixed-load inference is an explicit assumption. The in-session bracket, empirical floor probes in Section 6, and stack-specific labels constrain that assumption; only an external meter could additionally validate the absolute whole-system scale.

## 4. Detection-floor composition (C-ii)

A *detection floor* is a practical guard against false observed effects for one declared condition family: the same telemetry backend, metric, window type, workload profile, and stack identity. One such family forms a measurement cell. The floor is not a claim that a population percentile has been estimated exactly. JouleWise computes separate absolute and comparative floors and takes their maximum for the cell. An absolute floor measures how far repeated measurements of the same condition wander from their mean. A comparative floor measures the apparent difference between labels that are deliberately made identical and collected in A/B/B/A order.

### Repeatability and false-comparison guards

For an absolute cell with energies \(E_i\), residuals \(r_i=E_i-\bar E\), sample standard deviation \(s_r\), and \(n\) valid bundles, the point guard is

\[
F_{\mathrm{abs,point}}=\max\left(\max_i |r_i|,
t_{0.975,n-1}s_r\sqrt{1+1/n}\right).
\]

For \(n\) valid null-comparison blocks with within-block deltas \(\delta_i\), the corresponding guard is

\[
F_{\mathrm{cmp,point}}=\max\left(\max_i |\delta_i|,
|\bar\delta|+t_{0.975,n-1}s_\delta\sqrt{1+1/n}\right).
\]

The observed maximum protects against a false effect already seen; the Student-*t* prediction term protects against one additional observation under the repeatability model. Small samples receive a pre-registered guard factor, and fewer than five valid bundles or blocks are treated only as development evidence, not as a claim gate. Items within one bundle are not counted as independent repetitions.

### Worst-case timing attribution

Point repeatability is not the full floor. Each energy value is an interval from the timing calibration in Section 3. The floor computation evaluates the complete point-floor estimator over the joint corners of all member intervals that pass the admission and evidence gates, then takes the largest value. For a null A/B/B/A block, the four signed member intervals are propagated through the contrast together. This corner calculation is deliberately conservative: a systematic boundary-placement error is not independent Gaussian noise, so adding it in root-sum-square form would understate the worst case. The published floor is no smaller than the largest accepted attribution width.

This calculation revealed a stable and important limitation of the present instrument. Ordinary repeatability is smaller than the uncertainty caused by placing samples at phase edges: approximately one joule can be assigned to the wrong phase when a roughly 30 ms timing uncertainty meets a power change of roughly 33 W. The instrument is therefore *attribution-limited*, not *noise-limited*. More repetitions can refine the repeatability term, but they cannot average away this boundary-placement limit.

### Measured, never-zero drift allowance

Drift is a slow change in the machine or measurement response over the collection window. It is measured rather than assumed away. Each prospective window includes three fixed reference runs at the start, one at the midpoint, and three at the end. Gross energy and idle-subtracted energy are treated as separate claim families (idle-subtracted energy is gross energy minus the measured idle mean power multiplied by the phase duration). For each family, the protocol derives a repeatability bound from a settled reference corpus and measures the largest excursion among the start mean, midpoint, and end mean. The allowance is

\[
A_{\mathrm{drift}}=\max(\text{observed start/mid/end excursion},
\text{derived reference-repeatability bound}).
\]

Consequently, a passing drift screen never means zero drift. The allowance remains positive even in an exceptionally stable window, and the midpoint protects against an interior excursion that similar endpoints would miss. No duration-scaling law is applied because the available evidence does not identify a physical law relating drift to elapsed time.

For each absolute or comparative component, the guarded, corner-widened value is increased once by its matching drift allowance. The operative floor for a cell is then

\[
F_{\mathrm{cell}}=\max(F_{\mathrm{abs}},F_{\mathrm{cmp}}),
\]

not their sum. Cross-window components keep their own calibration basis and allowance; an allowance is never added again at the cell or reporting level. Operative floor values and their full decomposition for each demonstration stack are withheld here until the corrected artifacts are issued: **[RESULT PENDING RE-MINT]**.

### LABELLED publication and the effective decision bar

When timing attribution dominates, the floor remains publishable only through the **LABELLED** path. Every artifact and reader-facing result must identify the limit as attribution-limited, publish the corner-widened value rather than the smaller point diagnostic, retain the point-only repeatability number as a non-publishing diagnostic, and carry `floor_source = E_clock_anchor_shift_bound_j`. This field names energy uncertainty caused by shifting the phase edges within the calibrated clock-anchor bound as the dominant term. The label prevents a precise repeatability number from masquerading as the instrument's total resolving power.

The floor is only one side of a claim decision. The calibrated floor bounds a false effect produced by the calibration condition; the confidence or decision interval for the particular measured contrast separately carries that contrast's timing-attribution uncertainty. These are distinct uses of the same physical uncertainty and both are required. The effective bar is therefore

\[
\text{effective clearable effect}=F_{\mathrm{cell}}+B_{\mathrm{claim}},
\]

where \(B_{\mathrm{claim}}\) is the claim-side measurement bound. For the measured phase-contrast regime, this combined bar is approximately 5 J. Neither term may be removed as an apparent double count. Effects below the floor are reported as *not resolvable*, not as zero, equal, or evidence of no difference. A directional claim is made only when the effect and its interval clear the applicable bar.

## 5. Fail-closed collection protocol (C-iii)

*Fail-closed* means that missing, inconsistent, stale, or contaminated evidence produces a refusal rather than an optimistic default. The collection unit is one uninterrupted two-to-four-hour window with one power state, one instrument identity, fresh calibration before and after, a fresh drift-bound corpus, and one verdict over the exact member set. Work that does not fit with at least a 20% failure margin is split prospectively into another independently calibrated window.

### Pre-registration and admission

Before quiet time, the operator freezes the run identifiers, membership, stage order, comparison definitions, calibration retry count, acceptance thresholds, extraction specification, code revision, and an initially empty waiver list. Every configuration is validated and dry-run against a fresh output root. These choices are made before outcomes are visible. Pre-registration here is executable: the launcher and final verifier check the frozen values rather than relying on a narrative promise.

Each stage then passes admission gates immediately before measurement. The approved power supply and power policy must be unchanged; displays must be asleep; the screensaver and low-power mode must be off; thermal pressure must be nominal; and central- and graphics-processor activity must meet the quiet-state criteria. Known background work is allowed to finish before the window, followed by a settling interval, rather than being ignored during analysis. Runtime and telemetry identities, clock anchoring, sample cadence, calibration freshness, and post-run environment observations are also checked. No environment override can produce a claim-bearing member.

### Counterbalanced order

Comparisons use A/B/B/A blocks, abbreviated **ABBA**. Conditions A and B are measured in the order A, B, B, A, with ordinary cooldown between members. Averaging the two outer A observations and the two inner B observations cancels a linear time trend within the block to first order. For null-floor calibration, A and B are aliases of the exact same configuration and payload, so any nonzero block delta is a false comparative effect. For scientific contrasts, the A and B definitions are frozen in advance, and the contrast is computed within each block before blocks are aggregated. ABBA reduces common drift; it does not replace the measured whole-window drift allowance.

### Evidence custody and refusals

Every member is a self-contained bundle of configuration, raw power trace, runtime events, environment observations, and derived summary. Cryptographic hashes bind those files to the campaign manifest. Failed or interrupted artifacts are never deleted or overwritten. An occupied retry slot is moved to a quarantine area outside the active runs root; the exact member is recollected only under an allowed retry; and an append-only supersession record names which occurrence governs. Two present bundles for one occurrence refuse. The final whole-window verdict binds the exact member-occurrence set, calibration bracket, policy, and drift evidence by hash, so a later consumer cannot silently select a more favorable subset.

Collection does not continue indefinitely through environmental interruptions. Each stage attempt stops at its first member failure, and after the same cause fails a window stage for the third time the window itself closes rather than being retried; in actual operation, nights with three environmental member interruptions were closed and preserved as salvage rather than repeatedly retried. The surviving data may remain diagnostic, but it becomes claim-bearing only if the pre-registered verdict and extraction rules accept the exact resulting basis. This abandon-after-three rule limits outcome-dependent retrying and makes the cost of a noisy environment visible.

The custody chain continues after collection. The immutable corpus is backed up before extraction. The extractor re-authenticates member hashes, required files and cross-file consistency, calibration identity, environment admission, complete campaign membership, cooldown evidence, phase metric identity, and the whole-window drift allowance. It excludes or refuses a cell according to the frozen rules; missing uncertainty never becomes zero. The current artifact boundary is stated honestly: until floor artifacts are independently bound to their source extraction, a claim-bearing floor must be produced by protocol-controlled extraction in the same controlled custody session as the analysis that consumes it. A standalone floor file is not independently claim-licensing.

The refusal log is part of the evaluation, not an embarrassment to omit. It records contaminated members, out-of-family calibration, stale drift evidence, unresolved clock anchors, duplicate occurrences, and below-floor effects. In one real end-of-night case, the governed re-evaluation refused a window because a member's internal clock alignment could not be resolved. Independent adjudication found that refusal correct. The result remained non-claim-bearing: an example of the fail-closed design working as intended, not a software defect to be bypassed.

## 6. Instrument characterization (C-iv)

Instrument characterization asks whether the complete measurement system behaves predictably when driven by signals whose qualitative answer is known in advance. The workload is therefore a test signal, not yet the scientific finding. All tests retain the same calibration, admission, custody, and floor rules as the later demonstration measurements. Existing campaign fragments are not promoted where the governing whole-window verdict did not pass; the table marks the required claim-bearing results explicitly.

| Property | Characterization method | What a passing result would establish | Claim-bearing result |
|---|---|---|---|
| Linearity | Hold the prompt profile fixed and ramp the requested output from 128 to 2048 tokens. Regress gross request and decode energy on the runtime-observed output count; inspect residual structure as well as the fitted slope. | Energy responds proportionally over the tested dynamic range, and the fitted per-token slope can serve as the known-effect standard for floor probes on this stack. It would not establish linearity outside the tested range or on another stack. | **[PENDING WINDOW C]** |
| Null response across magnitudes | Run identical A-equals-B ABBA blocks at short, medium, and long output magnitudes. Evaluate the paired deltas against zero and against the predicted decision envelopes. | The comparison path does not create a directional effect merely because total energy or duration changes, and false contrasts across the tested range are contained by the error model. A non-significant result alone is insufficient; the interval must be interpreted relative to the floor. | **[PENDING WINDOW C]** |
| Empirical floor verification | Use the pre-registered linearity slope to create micro-deltas with predicted effects near 0.5, 1, 1.5, and 3 times the declared floor. Test positive and negative directions in counterbalanced blocks. | Sub-floor effects are refused while sufficiently super-floor effects clear in both directions. This is an operational check of the detection boundary, not a validation of the counter's absolute gain. | **[PENDING WINDOW C]** |
| Phase-attribution causal consistency | First compare the sum of separately integrated phase energies with the gross energy over their enclosing request. Then vary output length while holding prompt tokens fixed and fit the slope of prefill energy against output length. | Phase accounting is additive within its stated boundaries, and energy assigned to prefill does not acquire a systematic dependence on work that occurs later in decode. Together these tests challenge both missing energy and cross-phase leakage. | **[PENDING WINDOW C]** |
| Drift and settling | Place long controlled holds and fixed reference workloads through the window, including start, midpoint, and end references. After operator or stage activity, repeat the reference while recording the time required for thermal and admission observables to stabilize; compare it with the 180 s operating convention. | The measured drift trajectory is contained by the published allowance, and the chosen settling time is supported or revised from observed recovery rather than convenience. Endpoint agreement alone is not enough if the midpoint reveals curvature. | **[PENDING WINDOW C]** |
| Between-session stability | Repeat calibrations, null blocks, and floor cells across at least three sessions or days with the full stack identity recorded. | The calibration and floor are stable enough to reuse only under their declared freshness and identity rules, or reveal that a new session must mint a new floor. | **[PENDING WINDOW C]** |

Linearity and the null ladder test complementary failure modes. A smooth response can still carry an offset, and a zero-centered null can coexist with a nonlinear scale. The micro-delta experiment then closes the loop by using the measured slope to place effects deliberately below and above the declared decision boundary. Success requires the instrument to refuse the former and resolve the latter in both directions; merely observing larger effects with larger workloads is not sufficient.

The causal tests address the most important phase-specific risk. Additivity checks conservation inside the declared request boundary: phase intervals should reconcile with the enclosing total, subject to explicitly labeled setup or gap intervals. Causal invariance checks direction: holding the prompt fixed while increasing later decode work should not change energy attributed to earlier prefill. A nonzero prefill slope would indicate boundary leakage, shared-state coupling that invalidates the simple phase model, or both; it would narrow the claim rather than be explained away.

Temporal characterization separates slow drift from thermal settling. Start, midpoint, and end references expose whole-window curvature, while post-transition references estimate how long the system takes to return to its admitted state after operator activity or stage churn. Repetition across days tests whether one session's calibration is representative under identical recorded bindings. Internal channel-sum versus package reconciliation is retained as a secondary consistency check. External wall-power regression remains conditional on a suitable meter and would validate totals only; the pulse experiment remains the evidence for phase splitting.

Every resulting figure and table will identify the physical unit, operating-system version and build, runtime and relevant library versions, model artifact hash, quantization, tokenizer identity, sampler and output policy, configured and realized batch/concurrency policy, measurement boundary, and telemetry backend. Silent omission is not permitted. Measurements support stack-specific conclusions only; independent replication or a calibrated boundary bridge would be required for hardware-class, vendor-class, or cross-boundary rankings.

## 7. Demonstration results (C-v)

**[RESULT PENDING RE-MINT]**

This section will report phase-resolved gross joules per request for two model sizes, with tokenizer-scoped joules per prompt token and per output token as companion metrics. It will contain the pre-registered same-boundary model-size contrast, its interval, the complete floor decomposition, the claim-side bound, the effect-to-floor ratio, and the final resolvable/unresolved verdict. No demonstration energy value from the superseded mint is carried into this draft. A quantization ladder will be included only if it is collected under its own stack-specific floors and the frozen window budget permits it.

## 8. Related work

### LLM inference energy measurement

TokenPowerBench provides one of the closest reporting structures: it separates prompt-processing and token-generation energy, uses phase-appropriate token denominators, and groups results by context length [TokenPowerBench]. Its disclosed method, however, does not specify the boundary events, alignment rule, repetition and variance protocol, idle baseline, or external validation, and continuous batching makes an “active phase” label difficult to interpret when requests overlap. JouleWise adopts phase-specific reporting but restricts its primary scope to one sequential request, where runtime-emitted phase boundaries are well posed and can be calibrated.

The Illusion of Power Capping in LLM Decode samples graphics-processor power, integrates those samples, repeats configurations, and cross-checks sufficiently long operations against a separate hardware energy counter [IllusionPowerCapping]. This is a stronger measurement template than an unqualified software reading. Its counter agreement, run-to-run variation, snapshot fallback, and timing alignment nevertheless remain separate diagnostics rather than one bound on the reported effect, and its long sweeps do not use a drift-control ordering. JouleWise composes those classes of uncertainty into a decision rule for each contrast.

Apple-focused system comparisons reinforce the need for boundary labels. Silicon Showdown compares a graphics-board boundary on one platform with a whole-system-on-chip `powermetrics` boundary on Apple hardware, while runtimes and precision stacks also differ [SiliconShowdown]. Intelligence-per-Watt and ML.ENERGY similarly emphasize breadth across deployed inference configurations [IntelligencePerWatt; MLENERGY]. Such studies answer valuable systems questions, but unlike boundaries and software stacks cannot by themselves support a hardware-class causal ranking. JouleWise therefore makes the named stack and measurement boundary part of every result and prioritizes within-boundary effects.

### Software power counters and measurement standards

RAPL in Action established a validation agenda for commodity software counters: align lag before comparing streams, model wall power rather than assuming identity, account for temporal correlation, warm the system, measure sampler overhead, and inspect update granularity, overflow, jitter, and timestamp behavior [RAPLInAction]. Jay and Ostapenco likewise regress software readings against wall power and show that disagreement varies with load; they avoid claims about subtotals that the reference meter cannot observe [JayOstapenco]. JouleWise follows this epistemic boundary. A future external meter could test total gain and load dependence, but it would not validate how a total is divided between prefill and decode. The in-window pulse train addresses that distinct question.

MLPerf Power and SPEC require load-specific analyzer uncertainty, fixed ranges, clock synchronization, minimum intervals, invalid-sample accounting, and controlled battery behavior [MLPerfPower]. JouleWise translates their per-run reject-on-missing-evidence principle to a consumer software counter. The difference is that its principal uncertainty is not only an analyzer specification; it includes whether samples at a software-defined phase edge belong inside or outside the integral.

### Metrology and experimental discipline

Prospective paired minimum-detectable-effect methods estimate the smallest effect a planned paired study has adequate statistical power to find. They size the study from the variance of paired differences and can impose a one-way prior ratchet: observed variability may raise the planned threshold but may not lower it after outcomes are seen [PairedMDE]. JouleWise uses that logic for prospective workload sizing, but it does not treat the worst-case attribution term as independent random noise. Root-sum-square composition would be anti-conservative for a systematic edge-placement bound. Instead, the analysis maximizes over calibrated edge positions, measures drift with bracketed references, and publishes the resulting floor with the effect.

This emphasis changes the role of failed runs. A rejected admission, stale calibration, contaminated member, or below-floor contrast is evidence about the instrument's operating domain. Hash-bound raw traces, runtime events, configurations, supersessions, verdicts, and pre-registration records make that evidence re-reducible. The refusal is retained rather than disappearing behind a final average.

### Split and disaggregated inference

Split, or disaggregated, inference places prompt processing and token generation on different devices and transfers intermediate state between them. Revisiting Disaggregation Energy reports that the energy outcome depends on load, baseline, and transfer conditions on its evaluated two-graphics-processor node [RevisitingDisaggregationEnergy]. DualScale studies phase placement and per-phase power control on homogeneous server hardware [DualScale]. Prima.cpp includes whole-run energy and communication accounting but not a per-stage energy split [PrimaCPP], while SplitZip characterizes lossless transfer compression without making an energy claim [SplitZip].

JouleWise does not claim a new split scheduler in this paper. Split inference is instead a demanding future demonstration of the instrument because it introduces two physical boundaries, a transfer interval, and clock alignment across devices. A valid comparison would have to measure both ends, name each boundary, and clear a pre-registered floor or calibrated bridge. Whether splitting saves energy remains an empirical outcome; the reusable contribution is a method that can issue, qualify, or refuse the result.

exec
/bin/zsh -lc "sed -n '1,220p' CLAIMS_STATUS.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
# Claims Status

**The single standing home for "what can we actually claim right now."**
Every scientific number the project can publish, is holding, or must not
repeat — with its exact validity state and blocker. Refresh this file
whenever claim-bearing state changes (a verdict, a mint, a merge in the
D-095 chain, an adjudication); quote verdicts as issued, never
reinterpreted. Companion docs: `RUN_STATE.md` (session pointer),
`WINDOW_STATUS.md` (machine state), `docs/decision_log.md` (policy).

Last updated: **2026-08-07** (D-117: the historical re-mint path is
SUPERSEDED — structurally closed at main after the D-116 issuance
(candidate discovery excludes import-marked receipts by design); the
claim path forward is THREE PROSPECTIVE WINDOWS — fresh 1.5B decode
floor, fresh 7B decode floor, fresh decode contrast — live-bracketed
under the issued acceptance regime, with prefill floor cells riding
both floor windows. Prior "re-mint conditions" in this file are
historical: D-109 landed (PR #100), issuance executed (D-116, PR #109),
validator pin widening landed (PR #105). Full record:
`docs/process_traces/2026-08-06-d110-remint-fork/`.)

Earlier header (2026-08-03 night, for the record): D-108/D-109 ruled +
executed; D-110 made mint #1 retroactively NON-CLAIM-BEARING; window B
re-evaluation STOPPED → D-112; mint-1 re-derivability proven
byte-identical; report: `docs/run_reports/2026-08-03-16h-runway.md`.

---

## 1. VALID — minted, mainline, citable

**NONE at this checkpoint.** D-110 (2026-08-03, sweep finding RT-1)
made mint #1 and every number derived from it retroactively
non-claim-bearing: its floors embed a never-zero allowance of ZERO
where D-102 pin 3 mandates +max(drift, 0.010818 s) (~+43% on the a10
operative bound). The previously-listed values (operative 7.377086 J;
a10 components 3.823787 / 3.592138 J; window C comparative 7.377086 J)
move to §5 until the re-mint. The DERIVATION toolchain itself is
proven honest: the full pinned replay (2026-08-03) reproduced both
extraction reports, the artifact, and the statement BYTE-IDENTICAL
(`docs/process_traces/2026-08-03-q1-remint-bytecompare/`). The taint is
semantic (the selector the era used), not derivational.
**2026-08-07 (D-117):** the historical re-mint order is SUPERSEDED —
all three former re-mint conditions completed (D-109 via PR #100;
issuance via D-116/PR #109; pin widening via PR #105) and the FIRST
consumption attempt then proved historical consumption structurally
closed at main. Replacement: three prospective windows (D-117 cl.2);
the never-zero allowance correction binds their mints. All four PASSED
window verdicts remain untainted (sweep RT-5), but pre-genesis windows
CANNOT be claim-consumed — their role is diagnostic and
rule-establishing only.

**Standing measurement fact (D-078 cl.11, Ed-ratified):** the instrument
is attribution-limited (~1 J), not noise-limited (~0.3 J). Floors
publish LABELLED with the widened number; the effective clearable
effect for phase contrasts is floor + claim-side bound ≈ 5 J. No
instrument-tightening program.

## 2. EVIDENCE-BEARING — collected and verdict-PASSED, awaiting a specific gate

| Candidate claim | Value (prose-only until gated) | Window / verdict | Blocker |
|---|---|---|---|
| **7B decode floors (Qwen2.5-7B)** | absolute 6.294380135190098 J / comparative 13.998036715259254 J (absolute-cell member mean 192.386233 J, n=10 — always name the cell) | `window_7bfloor_20260729`, **PASSED**, governed extraction clean | **RE-SCOPED by D-117 (2026-08-07):** `window_7bfloor_20260729` is pre-genesis and cannot be claim-consumed; these values are DIAGNOSTIC and design inputs for the fresh 7B floor window (D-117 cl.2). The prior D-110 condition chain completed and was then superseded. |
| **1.5B-vs-7B decode contrast** (demonstration study #1) | **Registered claim metric (frozen v3 manifest): `phase_energy_j.decode`, 7B−1.5B = 141.29 J per block.** The widely-quoted 146.730349 J (σ 0.241 J, n=10 ABBA) is the `idle_subtracted_energy_j` whole-request DIAGNOSTIC — quote it only labelled as such, never as the claim (sweep DC-1; both reproduce byte-exactly from disk). | `window_contrast_20260730`, **PASSED** | **RE-SCOPED by D-117 (2026-08-07):** `window_contrast_20260730` is pre-genesis and cannot be claim-consumed; values are DIAGNOSTIC and the design template for the fresh contrast window (D-117 cl.2). The D-095 chain now runs through the prospective windows' mints. |

## 3. COLLECTED — verdicts FAILED as-issued; adjudication RULED (D-100, 2026-08-01)

The machinery adjudication is complete (MET-VERDICT-ADJ-01 → D-100 cold-
gate synthesis). Both verdicts **stand as issued, permanently by
construction**: any licensed re-evaluation appends a NEW row under
`consumption_semantics_id: salvage_dangler_exclusion_v1` with a new
pinned basis; the original FAILED rows are never edited and govern
default consumption. Outcomes per window:

- **Window A: permanently non-claim-bearing.** Its only post-cal retry
  binds a T1-incompatible power-policy identity (immutable evidence; the
  machinery's rejection was CORRECT), so no calibration bracket can ever
  form. C1 re-collects in a future window.
- **Window B: TERMINALLY CLAIM-RETIRED (D-113, Ed ruling 2026-08-05):
  RETAINED_IMMUTABLE / PERMANENTLY_NON_CLAIM_BEARING.** Ed chose
  abandonment over salvage ("soundness and quality of the project and
  claims above all"): no re-evaluation or claim consumption will ever
  occur; the WB-specific D-100/D-106/D-108 license chain is retired
  (general machinery survives for other windows);
  `WINB-R06-DISPOSITION-01` closes ABANDONED_FOR_FRESH_COLLECTION;
  labelled read-only forensic/diagnostic use remains permitted ("Window
  B, original verdict FAILED, D-113 claim-retired, non-claim
  evidence"). Every still-desired WB claim component re-collects fresh
  beginning Window C — no WB member enters a replacement claim basis.
  The F7 scope question is ANSWERED: whole-window voiding is affirmed
  as the current semantics (a cell-scoped alternative only via the
  D-083 cold gate; not built). Historical record of the 2026-08-03
  attempt below. The whole chain executed: D-108 ruled
  (clause (c) retired), row `D100-BII-BINDING-01` CLOSED (PR #99 +
  clause-(d) three-occurrence digest-bound re-record), closure +
  membership-binding artifacts authored and dry-authorized, D-093 scan
  clean 1/1, frozen corpus verified byte-identical (210+4 files, zero
  mismatches). The governed re-evaluation then REFUSED pre-verdict:
  survivor consumption failed on `mtadd-p2048o0128-r06`'s
  collection-time clock-anchor failure (`native_intersection_empty`) —
  the cold gate ruled this CORRECT fail-closed machinery (classification
  (i), convergent instruments; record
  `docs/process_traces/2026-08-03-winB-reeval-stop/`). No licensed
  channel removes r06 (exclusion cap spent on r08; not a dangler;
  waivers forbidden), and the NEG-8 drift bound expired 2026-08-02, so
  no PASS path exists under the license as drawn. Original FAILED
  verdict untouched. The WB NEG-8 bound re-mint obligation is MOOT
  under D-113; the near-run-time freshness rule continues to bind
  every future window (runbook + D-078, by cross-reference).

| Paper claim | Campaign | Collected | State after D-100 |
|---|---|---|---|
| **C1 — linearity** | `linearity_ramp` | **40/40** (window A) | DEAD for claims (window A permanent FAIL); re-collect (window C/D); data usable as design input (micro_delta slope) + corroboration diagnostics only |
| **C2 — null ladder** | `null_ladder` | o0128 + o0512 collected in window B — **returned to uncollected-for-claim state (D-113)**; o2048 never collected | Re-collect ALL of C2 fresh (window C, or split per the frozen plan); no WB member enters a replacement claim basis |
| **C3 — micro-delta** | `micro_delta` | not collected | Plan is draft-pending-slope by design; slope fit may consume window A ramp as DESIGN input (not a claim) |
| **C4 — additivity** | `additivity_shapes` | 23/24 single-root collected in window B — **returned to uncollected-for-claim state (D-113)**; 21/24 window-A corroborating remain labelled non-claim diagnostics | Re-collect C4 fresh (window C/D per the frozen plan). F7 ANSWERED by D-113: whole-window voiding affirmed as current semantics; no cell-scoped salvage |
| **C5 — long holds** | `long_holds` | not collected → window C | — |

## 4. Standing gates on EVERY claim consumption

1. ~~D-088 cl.3(c) three-check bench scan~~ — **LIFTED 2026-08-02**: the
   cooldown-join gauntlet closed (commit 3 merged, PR #93 `cb860e1`);
   the landed machinery now enforces these properties structurally
   (result-map completeness, counting domain, authenticated v2
   discrimination).
2. ~~D-093 raw-vs-validated supersession-record scan~~ — **LIFTED
   2026-08-02** with the gauntlet's close per its row contract; the
   validated reader boundary (PR #91) plus the commit-3 authenticated
   catalog own raw-record visibility permanently.
3. Verdicts consumed as issued; overrides only via the cold-gate path
   with written dissent Ed sees. (UNCHANGED — permanent.)
4. NEW (D-105): while `C3-RECOGNIZER-EXACT-01` is open, the tail
   recognizer's accepted set may only shrink, and the custody sidecar +
   writer-side key assertion may not be weakened.

## 5. DO NOT QUOTE — retired, void, or wrong-as-stated

- **ALL mint #1 floors as claims (D-110, 2026-08-03): operative
  7.377086 J, a10 components 3.823787 / 3.592138 J, window C
  comparative 7.377086 J** — retroactively non-claim-bearing (zero
  allowance where D-102 pin 3 mandates +max(drift, 0.010818 s));
  citable again only after the ruled re-mint under the repaired
  selector.
- **146.730349 J as "the contrast claim"** — it is the
  idle_subtracted_energy_j whole-request diagnostic; the registered
  claim metric is phase_energy_j.decode = 141.29 J (sweep DC-1). Either
  number only as prose with its metric named, neither as a gated claim
  yet.

- **3.17 / 2.94 J** floors — pre-allowance attribution-width
  diagnostics only (D-079 cl.5).
- **3.592138 J as "the decode floor"** — it is the isolated absolute
  component; the operative floor is 7.377086 J (D-084).
- **4.923 J item / 24.62 J suite** comparative floors — Ventura
  screensaver contamination artifacts (2026-07-17 campaign).
- Old window B (`04_phase_prefill_abba`) figures — verdict FAILED
  (`instrument_calibration_mismatch`, GPU DVFM ramp aliasing), corpus
  preserved but not claim-bearing.
- All pre-repair (pre-D-078) powermetrics corpora for claim use —
  time-anchor defect (D-078 soundness gate).
- Window A/B metrology numbers as claims — see §3 (verdicts FAILED as
  issued; window A permanently dead for claims; window B only via a NEW Ed ruling (D-112: the re-evaluation was performed 2026-08-03 and correctly refused; license exhausted as drawn).
- **Window A C1 linearity figures in any claim context** — the corpus
  is design-input/diagnostic only, permanently (D-100 + the immutable
  T1-incompatible retry).

## 6. Instrument findings queued for the paper (not claims yet)

- **Clock-anchor knife-edge** (2026-08-01 Sol consult, accepted): at
  197 s capture length the native-second intersection margin is ~±1 ms
  and the unmodeled wall/monotonic rate (~−12 ppm ≈ 2.3 ms/capture)
  exceeds it; pass/fail is quantization-phase luck. Desk item:
  rate-aware anchor design; directly publishable as a metrology
  limitation/finding.
- **Quiet-state definition**: validated windows now include suspended
  cloud sync (bird-SIGSTOP protocol) — claims describe that controlled
  state, not an arbitrary unattended Mac.
- **Operator-session streaming hazard**: the operating session's own
  output streaming can fail a member's idle admission (window B
  failure #3) — a reproducible environmental-validity observation.

exec
/bin/zsh -lc 'tail -n 260 docs/decision_log.md' in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
   duplication of thresholds into this entry. A Window C mint is a
   fresh mint, not a re-mint.
7. **Fresh-claim reset.** Every still-desired Window-B claim component
   routes to fresh collection beginning with Window C; no Window B
   member counts toward replacement claims (C2's o0128/o0512 and C4's
   Window-B members return to uncollected-for-claim state).
   MET-WINDOW-C-01 must be re-scoped from its remainder-only shape to a
   fresh-claim plan; if the full replacement exceeds the runbook's
   2-4 hour envelope with references, calibrations, and >=20% failure
   margin, it splits prospectively across windows C and D rather than
   compressing the night.
8. **STANDING PRINCIPLE (Ed's prerogative, operationalized):** for
   irreversible claim-bearing collection, schedule pressure, sunk cost,
   and convenience never justify weakening a soundness gate; unknown or
   unresolved known-failure state is NO-GO; when salvage and fresh
   collection differ materially in epistemic quality and fresh
   collection is feasible, fresh collection is the default. PAIRED
   GUARDRAIL (anti-rigor-spiral, with D-078): more data or more process
   is required only when it closes a named validity threat or
   materially improves a planned claim — smaller independent windows, a
   narrower claim, or no claim may be MORE rigorous than
   over-collection. Escalation stays event-driven (repeated known
   failure, new producer for a refusal spelling, identity-epoch change,
   consumer failure after clean collection); no new recurring
   ceremonies. Mechanization is ONE hard start fence on the
   claim-window task (a reviewed frozen-plan readiness record + every
   hard dependency satisfied, verified by the ordinary launcher), not a
   new governance subsystem.
9. **Window C readiness: NO-GO until the consult's precondition gates
   are green** (consult record Q4, the ONE home for the full list):
   frozen fresh scope with runtime budget; desk toolchain + D-078 chain
   complete on merged main including the ISSUED D-079 acceptance
   artifact and the D-110 (b)+(c) re-mint chain; instrument/machine
   identity gates including the 140 W adapter discrepancy and a fresh
   §5A; quiet-guard status used honestly (installed-INACTIVE is not a
   Window C control; the proven zero-agent guarded-shell path with
   independent census is the default); and one frozen GO/NO-GO
   checklist with no in-night policy decisions. The runbook
   §5A-vs-§13.1 member-level clock-retry inconsistency must be resolved
   BEFORE the plan freeze; rigor-first default is NO member-level
   anchor retry without a prospective ruling.

**Consult dissents recorded (adopted):** kept-local-never-consumed was
rejected in favor of claim-retired-with-labelled-forensic-use; the
strict F7 answer is semantics-confirmation, not causal-scope truth;
D-110 condition (c) is readiness assurance for Window C, not
contamination physics; an installed-inactive quiet guard contributes
nothing to the Window C assurance case.

**Consequences.** CLAIMS_STATUS Window B section gains the terminal
labels; kernel row WINB-R06-DISPOSITION-01 retires as ABANDONED (same
session, after in-flight read-only sessions clear); MET-WINDOW-C-01
re-scope and the claim-window start fence register as queued work;
RUN_STATE's parked-decisions list drops D-113.

## D-114: T3-CHAIN DESCOPE — t3 stays the interactive control plane; t3-resident-during-measurement-windows is DROPPED (Ed directive, supersedes the 2026-08-03 T3-DRIVE priority)

**Date:** 2026-08-05 (Ed, in-thread, during the desk session).
**Status:** RATIFIED by the directive's own author. This reverses Ed's
2026-08-03 ~23:55 T3-DRIVE-PRIORITY directive. Under rule 11 a
lieutenant may not self-exempt from a standing priority; that
constraint does not bind Ed reversing his own instruction, so no cold
gate was convened. The lead proposed the descope shape; Ed ruled.

**Question.** The t3-drive chain (host-wide quiet lease, refuse-at-arm,
resident watcher, t3 handoff/relaunch, README banner projection, plus
an app-up/app-down characterization pair to decide app-adjacent window
admissibility) had grown a root-owned, sudo-capable, credential-bearing
surface — a 7-blocker focused audit on commit 1 alone, and a design
consult showing the credential could not be honestly removed without
also revising Q10/Q11/Q13/Q19/Q24 as a set. Ed: "is the juice worth the
squeeze for a UX improvement of using t3 as a control plane?" and "I am
tired of wasting time on this control plane stuff and want to get back
to the project."

**Ruling.**
1. **KEEP — t3 as the INTERACTIVE control plane.** Ed drives sessions
   from t3, including remotely and away from the measurement machine.
   This costs nothing and requires no guard machinery.
2. **DROP — t3 resident during measurement windows.** Claim windows
   return to the proven path: quit t3, ordinary guarded shell, zero
   agent sessions, fresh §5A, walk away. Every successful claim window
   to date used exactly this path. The app-up admissibility question is
   therefore MOOT, not answered.
3. **QUIET-GUARD-01 re-scoped to COMMIT 1 ONLY** — the host-wide quiet
   lease and process census, installed-INACTIVE. Retained on non-t3
   merit: it gives the ordinary guarded-shell launcher a MECHANICAL
   refuse-at-arm census, replacing today's procedural eyeballing. Its
   seven audit blockers are still fixed to the safety bar before it
   lands (it is root-adjacent regardless of who calls it).
4. **SHELVED:** QUIET-GUARD commits 2-4 (launcher interception, t3
   handoff + resident watcher, t3-relaunch + banner projection + all
   credential handling); T3-CHAR-PAIR-01 (BOTH arms — the r03 re-capture
   and the app-DOWN arm); WO-T3-VIS-01; SEC5A-REMOTE-01 (its
   programmatic substrate lived in the dropped scope).
5. **T3-DRIVE-PRIORITY gate LIFTED** (`active_global_gates: []`); the
   project queue is ungated. The two in-flight t3-adjacent desk items
   (T3-AMEND-01 doctrine bookkeeping, COLDGATE-VALIDATOR-01) finish
   because both are cheap, near-complete, and independently useful.
6. **Q13's degraded tail is ACCEPTED as an edge case** (Ed, explicit):
   if a relaunch fails and no session returns, there is no remote
   signal. A failed relaunch requires physical presence anyway, so
   local discovery at next login is sufficient. This retires the
   requirement that motivated the unattended-push credential.
7. **Q10 (guard git identity WITH unattended push) is SUPERSEDED** —
   moot under the descope; no credential enters any guard path.

**Design record preserved for any future revival** (from the 2026-08-05
credential consult, before the descope was ruled): a credentialed
network pusher running DURING a quiet window contradicts the window's
defining property. The correct shape is credentials only at the
unprivileged interactive boundary (pre-arm and post-window pushes), a
PRE-ARMED SERVER-SIDE DEAD-MAN ALARM for the no-return case (which also
catches total host death), a dedicated non-login service UID rather
than HOME-restore env scrubbing (root is otherwise ambiently
credential-reachable via git helpers / SSH / Keychain), and a banner
that can only truthfully say ARMING_REQUESTED pre-window.

**Consequences.** The successor's queue is the science queue: the two
open soundness-sweep blockers (RT-1 mint-floor understatement; voided
numbers on README/PROJECT_STATUS), the a10 phase-floor extraction, and
MINT-GENERALIZE-01 — whose D-110 condition (a) was satisfied the same
day by the CAL-BRACKET merge (PR #100, `f75d12b`).

## D-115: Quiet-guard Q2 setup authority is a FIXED INSTALLATION CAPABILITY, not general root authority (Commit-1 packet entry; renumbered from the contract's proposed D-114 marker)

**Date:** 2026-08-05 (lead adjudication, Fable magistrate session).
**Status:** ADJUDICATED under Ed's standing Q2 license (2026-08-05
ratification batch: Q2 proceeds on lead defaults subject to Ed veto).
**Numbering note:** the Commit-1 worker proposed this entry as D-114
inside `docs/contracts/quiet_guard.md` (it does not own the decision
log, correctly). D-114 was consumed the same day by the T3-CHAIN
DESCOPE, so this entry is D-115; the contract marker renumbers to
D-115 in the Commit-1 fix round. **Packet-letter deviation, ruled:**
the IMPL-PACKET file map places this entry in Commit 1's delta, but
the branch forked before D-114 landed and an in-branch append would
manufacture a merge conflict in this file; the entry lands on main and
is merged back into `impl/quiet-guard`, which satisfies the packet's
purpose (binding authority exists before the capability merges) with
cleaner custody.

**Question.** Q2 asked what authority the one-time
`scripts/setup_quiet_guard.sh` sudo session exercises when it creates
the root-owned quiet-guard state under
`/Library/Application Support/JouleWise/quiet-guard/`.

**Ruling.**
1. **Capability boundary.** The setup script exercises a fixed
   installation capability: create the root-owned state/install
   directories, install the fixed-command privileged helper and the
   narrow `sudoers.d` command aliases, and write `live_promotion=false`.
   It confers NO general root authority; nothing outside that
   enumerated set is licensed. Normal guard operation is `sudo -n`
   against the fixed command aliases only, and the helper drops to the
   invoking uid/gid before any agent child executes.
2. **Binding conditions on the capability** (from the 2026-08-05
   adversarial audits qg-audit-A/B; the capability is not validly
   exercised without them):
   a. **Fresh interactive authorization** — the installer must
      invalidate any cached sudo timestamp (`sudo -k`) before
      requesting authorization, so a cached ticket can never silently
      convert repository state into root-executed code.
   b. **Authenticated content** — what is installed must be
      authenticated against pinned digests of the reviewed artifacts
      (or an equivalently strong provenance check), not merely parsed
      for syntactic validity; root-staging closes copy races but does
      not authenticate what was staged.
   c. **Real interpreter isolation** — the installed helper runs with
      genuine isolation guarantees (no site initialization, no
      user-site, no environment hooks: `-I`-equivalent), matching the
      contract's isolation claim.
3. **Inactive by construction.** Commit 1 installs INACTIVE:
   `live_promotion=false`, `arm` refuses (`t3_char_pair_verdict_missing`),
   and no launcher, chain, watcher, or projection code is in scope
   (D-114 descope). Activation requires a separate, later, Ed-visible
   step and is not licensed by this entry.

**Consequences.** The Commit-1 fix round renumbers the contract marker
and implements conditions 2a-2c with discriminating regressions; the
QUIET-GUARD-01 row cannot land while any condition lacks enforcement.

## D-116: D-079 calibration acceptance artifact ISSUED; ledger genesis import executed (D-110 condition (b) SATISFIED)

**Date:** 2026-08-06 (Fable magistrate, overnight; issuance pre-authorized by Ed 2026-08-05 conditional on the gate passing).
**Status:** EXECUTED. This retires the schema fixture and issues the authoritative calibration acceptance artifact — the anchor all future floor-mint claims authenticate against. D-110 re-mint condition (b) ("R2 backfill verified, ledger bootstrapped, head pinned") is now SATISFIED; (a) was satisfied by PR #100, (c) by PR #105. **MINT-GENERALIZE-01 is UNBLOCKED for the re-mint.**

**What was written.**
- `runs/calibration_observation_ledger.jsonl` — the 76-receipt genesis historical-import chain (git-ignored local custody artifact, sha256 `aa80684848d0ce156ed2d14df47472006175840eda17f9025eff9754af694e3f`; deterministic from the custodied inputs below + the raw evidence; MUST be backed up per the runbook before the re-mint consumes it).
- `configs/calibration/calibration_ledger_head.json` — the repo-committed head pin (sequence 76, head_digest `08456d5076c18a9a7f758969b02f5b6f7ad9fcc267dd12e2d3778c22458094d7`), the D-109 R1.4 anti-rollback trust anchor.
- `configs/calibration/calibration_acceptance_d079_v2.json` — flipped `schema_fixture_unissued` → **issued** (file sha256 `316113960c596a6f927987dbdf8f2bca4b0cca9ee4a59a540bbd32bba9048985`, whole-core `derivation_sha256` `4f6633d5fb89a6e8fd137a834728b843915027b6f0b0afd6c37ae24e65d23f02`; `claim_eligible=true`). Emitted deterministically (not hand-edited) from the historical-import finalizations.
- Reproducibility inputs custodied at `docs/process_traces/2026-08-06-d079-issuance-coldgate/` (disposition table sha `5da820aa…`, custody manifest sha `99cbf3df…`, execute summary, ledger sha).

**Disposition inventory (B1 lead-ruled).** 30 valid / 2 systematic-invalid / 6 ordinary-invalid. The two systematic-invalid members (`20260726T000039-491995f3`, `20260801T064830-c76f5d1c`) have bounds `0.035435840879704805` / `0.0350400833260715`, both exceeding the ratified pre-flight screen `0.033558756679900`; D-102 (§~6298) explicitly names the first a systematic failure "never budgetable." R2.8 counting: 30 valid < 38 threshold, so issuance does NOT itself trigger corpus-doubling re-derivation (eight further valid same-epoch observations would; R2.8's literal "six further" was conditioned on the superseded 32-valid candidate). derivation_corpus preserved byte-identical at n=19 (its fixture whole-core digest was `3cece3b2…`; that value is NOT carried into the issued artifact — embedding it would fail the loader). All 38 custody locators are iCloud-backup copies (raw evidence is git-ignored by repo convention; integrity rests on the committed hash chain, not the custody pointer).

**Window-B completeness note (soundness-critical, for any reviewer asking "why Window-B in the anchor?").** The `prior_observation_set` correctly includes 6 `window_metrologyB` **calibration fiducial** observations (2 valid: `e0ce33f5`, `8c3bfe9e`), as mandated by D-109 R2.3/R2.8 completeness (every content-distinct governed CALIBRATION observation). This is NOT a D-113 violation: D-113 retired Window B's WINDOW CLAIM consumption (its null-ladder/additivity science members), not the calibration fiducials collected in that period; the general calibration machinery survives per D-113. These fiducials are EXCLUDED from the frozen n=19 threshold basis (which is Window-A-only) and do not influence the bound.

**Gate history (the process earned its keep on the anchor).** Two rule-11 cold gates. Cold gate #1 (on the plan) HELD correctly — the naive JSON-edit plan had no issued-artifact consumer (F1) and would have invalidated the whole-core digest (F2). That forced a real consumer implementation, which then ran the full C-028 gauntlet: adversarial audit (consumer proven false-ACCEPT-resistant; 3 emission/execute blockers incl. ledger-commit-BEFORE-artifact-validation) → fix → delta (exit-3 masking) → fix → final delta ACCEPT. Cold gate #2 (on the exact bytes): both lenses PROCEED on CONTENT (head/dispositions/B1/R2 all independently reproduced); HOLD on sequencing only — the consumer had to land on main before writing the issued artifact, else the anchor bricks. Resolved by merging PR #108 first, then executing against consumer-present main, with the co-landing verification (`_valid_acceptance_bound(issued)=True`) confirmed post-write. Full records: `docs/process_traces/2026-08-06-d079-issuance-coldgate/`.

**Consequences.** MINT-GENERALIZE-01 (b) satisfied; the re-mint (a10 extraction + mint #1 re-derivation under the corrected selector, embedding the D-102 pin-3 never-zero drift allowance) is the next step — the path to a non-empty claims table. The runs/ ledger must be custody-backed before the re-mint consumes it.

## D-117: D-110's historical re-mint order SUPERSEDED — prospective three-window replacement (Option 2) adopted; D-113 readiness rewired

**Date:** 2026-08-07 (Ed directive, in-thread; transcribed by the Fable
magistrate. Ed, verbatim: "if i recall for a paper ready at the quality
needed we need 3 more machine quiet nights and a lot of desk work",
with an explicit go to "execute all the deskwork" — read together with
his 2026-08-06 in-thread MVP-scope directive "a little more than just
decode, at least decode/prefill". His ruling moots a cold gate: apex
authority per rule 11.)
**Status:** ADOPTED. Full technical record:
`docs/process_traces/2026-08-06-d110-remint-fork/` (DIAGNOSIS: the
structural closure live-reproduced at `c537386`; Sol xhigh consult run
`20260806T165843Z-10884`; SYNTHESIS: magistrate concurrence).

1. **The D-110 clause-3 re-mint order (historical a10 consumption under
   the corrected selector) is SUPERSEDED.** The issued ledger holds only
   import-marked receipts; candidate discovery excludes imports by
   design; future live receipts cannot causally bracket past windows.
   The order is structurally unsatisfiable at main, not merely
   inconvenient. D-110's OTHER holdings STAND untouched: mint #1 and
   derivatives remain non-claim-bearing, and the never-zero
   `A_s = max(observed_drift_s, 0.010818)` allowance (D-102 pin 3)
   BINDS every mint under this entry.
2. **Replacement: three compact prospective claim windows** — fresh
   1.5B decode floor, fresh 7B decode floor, fresh 1.5B-vs-7B contrast
   — each with fresh §5A, live pre/post calibration receipts appended
   to the issued ledger, own verdict + head-pin + custody. Claims
   chain: historical corpus → issued D-079 acceptance rule → live
   brackets → prospective floors → prospective contrast. Honest
   framing preserved from the consult: historical data establish the
   RULE; live receipts bracket all claim-bearing science.
3. **Scope (Ed's decode/prefill directive):** prefill FLOOR cells ride
   both floor windows (cheap, same members' prefill phase). The model
   contrast is DECODE-ONLY by default: the 2026-08-07 desk feasibility
   check (`docs/process_traces/2026-08-07-prefill-feasibility/`) found
   the 128-token prefill contrast MARGINAL against the effective bar
   (interval overlaps it). A prospectively frozen ≥256-token prefill
   contrast arm remains an OPEN ED OPTION (estimand change +
   ~110 core minutes, likely its own window) — not adopted here.
4. **D-113 rewire:** its readiness dependency on the historical re-mint
   completing is REMOVED. The three-window P1 closure PRECEDES the
   broader MET-WINDOW-C-01 C2/C4/C5 replacement campaign (grounds:
   Ed's paper-first priority stack, 2026-08-06).
5. **Naming:** "Window D" is unavailable (collides with
   `runs_window_d_20260726` and D-113's reserved terminology); the
   three windows receive new immutable plan/root identifiers at plan
   freeze.
6. **Option 1 (finite-allowlist historical candidacy) is PRESERVED as
   a versioned contingency ONLY**, requiring a rule-11 cold gate before
   any implementation (semantics sketch: consult response §3). The
   historical corpora remain untouched on disk, non-claim-bearing per
   D-110 cl.1, logs sha-verified.
7. **Unblocked desk queue** (consult §4): freeze three window plans +
   budgets; 1.5B decode floor plan from the proven 10-absolute/40-null
   design; generalized mint pinsets with per-plan six-decimal literals
   (the D-084 hard literal `7.377086` refuses any corrected mint under
   every option — closure is per-plan supply via the generalized path);
   extraction specs / order manifests / evidence-root ids / contrast
   manifest; synthetic three-window live-ledger integration regression;
   D-102 successor-artifact packet; results/methods prose placeholders.

exec
/bin/zsh -lc "sed -n '1,110p' docs/paper/draft-v1.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
# JouleWise: Detection Floors for LLM Inference Energy Measurement on Consumer Silicon

## 1. Introduction

Energy numbers for large language model (LLM) inference now appear in leaderboards, systems papers, product comparisons, and policy debates. Published estimates for apparently similar queries can differ by an order of magnitude, yet the numbers are rarely accompanied by an error bar that says how small a difference the measurement method can actually distinguish. This omission is especially consequential on consumer hardware. Apple's `powermetrics` utility makes processor power estimates available without a laboratory meter and is therefore attractive for repeated experiments, but, to our knowledge, it has not been validated in published work as an instrument for separating the energy of LLM inference phases. Apple describes its outputs as estimates; treating them as exact readings can turn timing uncertainty at a phase boundary into a spurious energy difference.

The core difficulty is physical as much as statistical. Energy is the integral of power over time. An experiment may repeat consistently and still assign energy to the wrong phase if a power sample near the boundary between prompt processing and token generation is placed on the wrong side. Averaging more repetitions reduces random scatter but does not remove that attribution error. Slow changes in thermal or background state can add a second false difference over a long collection session.

We argue that a software power counter should be treated as a scientific instrument rather than as a logging convenience. The instrument must be calibrated in the same session in which it is used; each reported result must carry a detection floor, meaning the smallest false effect that the calibrated method could plausibly produce under the stated conditions; and the analysis must decline a directional claim when the observed effect cannot clear that floor and its own measurement uncertainty. JouleWise implements this discipline for phase-resolved, single-request LLM inference on one named Apple-silicon machine and software stack. The runtime emits the phase boundaries because it drives the workload, while `powermetrics` supplies the power samples integrated between those boundaries.

This scope is deliberately narrow. A measurement characterizes one physical unit, operating-system build, runtime and library stack, model artifact, quantization, tokenizer, sampling policy, single-request execution policy, telemetry backend, and measurement boundary. It does not establish that an Apple hardware class or vendor is more efficient than another platform. Without an external power meter, absolute values remain internal to the named `powermetrics` system-on-chip boundary; same-boundary contrasts can still be scientifically useful when they pass the calibration and floor gates. Gross joules per request are the primary energy metric. Joules per prompt or output token are tokenizer-scoped companion metrics and are never treated as tokenizer-independent work units.

This paper makes the following contributions:

1. (C-i) an in-window calibration method that measures timing-attribution error for phase-resolved energy integration;
2. (C-ii) detection floors composed from measured repeatability, worst-case attribution, and measured drift — published with every result;
3. (C-iii) a fail-closed collection protocol (admission gates, ABBA ordering, custody chains, pre-registration) with its refusal log as evidence;
4. (C-iv) full instrument characterization: linearity, null response across magnitudes, empirical floor verification, phase-attribution causal consistency, drift/settle;
5. (C-v) demonstration measurements: phase-resolved J/token for two model sizes with a pre-registered contrast [+ quantization ladder if window budget allows];
6. (C-vi) open tool + hash-bound reproducible artifacts.

## 2. Background and the gap

### Energy-benchmarking rules

The first relevant lineage is formal energy benchmarking. MLPerf Power and the associated Standard Performance Evaluation Corporation methodology treat uncertainty and validity as properties of each measured run. They require a qualified analyzer, uncertainty evaluated at the observed load, fixed measurement ranges, synchronized clocks, sufficiently long intervals, invalid-sample accounting, and explicit treatment of battery-backed systems [MLPerfPower]. These rules establish an important principle: a benchmark result is not valid merely because the meter has a specification sheet. The evidence recorded during the run must show that the measurement operated inside its accepted conditions. These standards, however, assume external instruments and data-center-style workloads; they do not provide a method for validating phase boundaries reported by a software counter on a consumer system.

### Software-counter validation

The second lineage validates software-visible energy counters against external power. Intel's Running Average Power Limit (RAPL) counters have been studied through lag alignment, regression against wall power, counter-resolution tests, sampler-overhead audits, and thermal controls [RAPLInAction]. Jay and Ostapenco's CCGRID 2023 study likewise shows that the gap between a software meter and wall power can depend on load rather than behave as one fixed offset, and it refrains from component-level conclusions when no reference instrument observes the component [JayOstapenco]. This work provides a strong model for whole-machine scale validation. It does not define a detection limit for a reported effect, does not validate `powermetrics` on Apple silicon, and cannot by itself establish whether software samples were assigned to the correct LLM phase. A wall meter observes a total; phase attribution needs a separate timing experiment.

### LLM energy studies

The third lineage measures LLM energy across models, hardware, and workloads. TokenPowerBench reports prompt-processing and token-generation energy with phase-appropriate token denominators; ML.ENERGY, Silicon Showdown, and Intelligence-per-Watt broaden empirical coverage across deployed systems [TokenPowerBench; MLENERGY; SiliconShowdown; IntelligencePerWatt]. This breadth makes inference energy visible, but the nearest studies do not jointly characterize counter timing, repeatability, drift, and the minimum resolvable effect. Phase labels are consequently easy to read as exact even when the method does not report the boundary events, alignment uncertainty, or a floor below which a difference should be refused.

The specific gap is therefore not another energy table. To our knowledge, no published work combines phase-resolved LLM energy on consumer silicon, a per-measurement error budget, and validation of `powermetrics` timing attribution under its named measurement boundary (as distinct from validating its absolute counter gain or whole-system energy scale, which would require an external meter). JouleWise fills that gap by making instrument characterization and refusal behavior the primary result; model comparisons are demonstrations of what the characterized instrument can and cannot resolve.

## 3. In-window calibration method (C-i)

### Measurement model and boundary

JouleWise measures one sequential request at a time. Prompt processing (often called *prefill*) converts the input sequence into the model's internal state; token generation (often called *decode*) produces output tokens from that state. Because the experiment controls the runtime, it records the start and stop of these phases directly in the runtime event stream rather than inferring them from shapes in the power trace. The reducer then integrates the named `powermetrics` system-on-chip power channels between each pair of phase events using trapezoidal integration.

The runtime and the telemetry sampler do not share a perfect clock. Operating-system launch latency, timestamp anchoring, and the sampler's averaging behavior can shift an apparent edge. A phase-energy estimate must therefore be an interval, not only a point. The calibration asks a concrete question: if software commands a load pulse at a known time, how far can the rising and falling edges of that pulse appear displaced in the sampled power trace?

### Bracketed pulse-train calibration

Immediately before and after every claim-bearing collection window—that is, a window eligible to support a reader-facing scientific claim—JouleWise runs a fresh pulse-train calibration under the same machine, operating-system, power-supply, and telemetry state as the science workload. The current protocol commands 59 graphics-processor matrix-multiplication pulses. Their durations are fixed in advance, their gaps follow a deterministic low-discrepancy schedule rather than a single repeated period, and quiet baselines of at least 4.5 seconds separate the fitted regions. The varied schedule reduces the risk that the calibration accidentally locks to the telemetry sampler's cadence. The 59-pulse design supports the pre-registered nonparametric 95/95 bound: a conservative bound intended to cover at least 95% of the calibration population with 95% confidence under the stated transfer assumptions.

For each pulse, the estimator compares the commanded interval with the observed power plateau and fits the start-edge and stop-edge lags independently. This distinction matters. A common shift of both edges may leave pulse energy nearly unchanged, while an early start combined with a late stop can add energy at both boundaries. The calibration therefore retains a bound for the instrument's edge-placement error rather than collapsing the evidence to one best-fit lag.

Each science member, meaning one recorded workload run, also carries a local bound on how its runtime clock is anchored to the trace, including the observed span between wall time and a monotonic clock that is not adjusted by network synchronization. For a reported phase, the analysis combines the member-local common shift, the calibration edge bound, and the clock-span term. It evaluates the energy integral at all four combinations of early and late start and stop edges, while scanning the allowed common shift exactly. The minimum and maximum of those integrals form the admissible energy interval. The physical intuition is simple: the interval asks how much energy could move into or out of the phase if both boundaries were placed at their most adverse calibrated positions.

The pre- and post-window calibrations form a bracket around the measurements. Both must be authenticated, fresh, and causally outside the science interval. The operative bound is the larger of the two. Separately, the absolute difference between the pre- and post-window calibrations is screened against a derived bracket-drift limit of about 10.82 ms: a small repeatability-only excess is propagated into every floor and claim, while an identified systematic defect cannot be absorbed by that budget. If the post-window bound is larger than the one used when a member was first reduced, the member must be re-reduced through the pre-specified path with the wider bound or it cannot support a claim; metadata is never patched to make the bounds agree. A pre-flight level screen also runs before the first science member. It rejects a calibration whose fitted lag is outside the previously characterized family, such as a graphics-processor frequency ramp that the pulse model could mistake for a timing shift. A retry is allowed only after a specific cause is identified and removed, within the retry count frozen before collection. Repeating merely until a favorable calibration appears would be selection on the outcome.

This procedure validates timing attribution, not the gain of the power counter. The pulses are graphics-processor matrix multiplications under a relatively light central-processor load, so transfer of their timing bound to sustained mixed-load inference is an explicit assumption. The in-session bracket, empirical floor probes in Section 6, and stack-specific labels constrain that assumption; only an external meter could additionally validate the absolute whole-system scale.

## 4. Detection-floor composition (C-ii)

A *detection floor* is a practical guard against false observed effects for one declared condition family: the same telemetry backend, metric, window type, workload profile, and stack identity. One such family forms a measurement cell. The floor is not a claim that a population percentile has been estimated exactly. JouleWise computes separate absolute and comparative floors and takes their maximum for the cell. An absolute floor measures how far repeated measurements of the same condition wander from their mean. A comparative floor measures the apparent difference between labels that are deliberately made identical and collected in A/B/B/A order.

### Repeatability and false-comparison guards

For an absolute cell with energies \(E_i\), residuals \(r_i=E_i-\bar E\), sample standard deviation \(s_r\), and \(n\) valid bundles, the point guard is

\[
F_{\mathrm{abs,point}}=\max\left(\max_i |r_i|,
t_{0.975,n-1}s_r\sqrt{1+1/n}\right).
\]

For \(n\) valid null-comparison blocks with within-block deltas \(\delta_i\), the corresponding guard is

\[
F_{\mathrm{cmp,point}}=\max\left(\max_i |\delta_i|,
|\bar\delta|+t_{0.975,n-1}s_\delta\sqrt{1+1/n}\right).
\]

The observed maximum protects against a false effect already seen; the Student-*t* prediction term protects against one additional observation under the repeatability model. Small samples receive a pre-registered guard factor, and fewer than five valid bundles or blocks are treated only as development evidence, not as a claim gate. Items within one bundle are not counted as independent repetitions.

### Worst-case timing attribution

Point repeatability is not the full floor. Each energy value is an interval from the timing calibration in Section 3. The floor computation evaluates the complete point-floor estimator over the joint corners of all member intervals that pass the admission and evidence gates, then takes the largest value. For a null A/B/B/A block, the four signed member intervals are propagated through the contrast together. This corner calculation is deliberately conservative: a systematic boundary-placement error is not independent Gaussian noise, so adding it in root-sum-square form would understate the worst case. The published floor is no smaller than the largest accepted attribution width.

This calculation revealed a stable and important limitation of the present instrument. Ordinary repeatability is smaller than the uncertainty caused by placing samples at phase edges: approximately one joule can be assigned to the wrong phase when a roughly 30 ms timing uncertainty meets a power change of roughly 33 W. The instrument is therefore *attribution-limited*, not *noise-limited*. More repetitions can refine the repeatability term, but they cannot average away this boundary-placement limit.

### Measured, never-zero drift allowance

Drift is a slow change in the machine or measurement response over the collection window. It is measured rather than assumed away. Each prospective window includes three fixed reference runs at the start, one at the midpoint, and three at the end. Gross energy and idle-subtracted energy are treated as separate claim families (idle-subtracted energy is gross energy minus the measured idle mean power multiplied by the phase duration). For each family, the protocol derives a repeatability bound from a settled reference corpus and measures the largest excursion among the start mean, midpoint, and end mean. The allowance is

\[
A_{\mathrm{drift}}=\max(\text{observed start/mid/end excursion},
\text{derived reference-repeatability bound}).
\]

Consequently, a passing drift screen never means zero drift. The allowance remains positive even in an exceptionally stable window, and the midpoint protects against an interior excursion that similar endpoints would miss. No duration-scaling law is applied because the available evidence does not identify a physical law relating drift to elapsed time.

For each absolute or comparative component, the guarded, corner-widened value is increased once by its matching drift allowance. The operative floor for a cell is then

\[
F_{\mathrm{cell}}=\max(F_{\mathrm{abs}},F_{\mathrm{cmp}}),
\]

not their sum. Cross-window components keep their own calibration basis and allowance; an allowance is never added again at the cell or reporting level. Operative floor values and their full decomposition for each demonstration stack are withheld here until the corrected artifacts are issued: **[RESULT PENDING RE-MINT]**.

### LABELLED publication and the effective decision bar

When timing attribution dominates, the floor remains publishable only through the **LABELLED** path. Every artifact and reader-facing result must identify the limit as attribution-limited, publish the corner-widened value rather than the smaller point diagnostic, retain the point-only repeatability number as a non-publishing diagnostic, and carry `floor_source = E_clock_anchor_shift_bound_j`. This field names energy uncertainty caused by shifting the phase edges within the calibrated clock-anchor bound as the dominant term. The label prevents a precise repeatability number from masquerading as the instrument's total resolving power.

The floor is only one side of a claim decision. The calibrated floor bounds a false effect produced by the calibration condition; the confidence or decision interval for the particular measured contrast separately carries that contrast's timing-attribution uncertainty. These are distinct uses of the same physical uncertainty and both are required. The effective bar is therefore


exec
/bin/zsh -lc "sed -n '111,230p' docs/paper/draft-v1.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
\[
\text{effective clearable effect}=F_{\mathrm{cell}}+B_{\mathrm{claim}},
\]

where \(B_{\mathrm{claim}}\) is the claim-side measurement bound. For the measured phase-contrast regime, this combined bar is approximately 5 J. Neither term may be removed as an apparent double count. Effects below the floor are reported as *not resolvable*, not as zero, equal, or evidence of no difference. A directional claim is made only when the effect and its interval clear the applicable bar.

## 5. Fail-closed collection protocol (C-iii)

*Fail-closed* means that missing, inconsistent, stale, or contaminated evidence produces a refusal rather than an optimistic default. The collection unit is one uninterrupted two-to-four-hour window with one power state, one instrument identity, fresh calibration before and after, a fresh drift-bound corpus, and one verdict over the exact member set. Work that does not fit with at least a 20% failure margin is split prospectively into another independently calibrated window.

### Pre-registration and admission

Before quiet time, the operator freezes the run identifiers, membership, stage order, comparison definitions, calibration retry count, acceptance thresholds, extraction specification, code revision, and an initially empty waiver list. Every configuration is validated and dry-run against a fresh output root. These choices are made before outcomes are visible. Pre-registration here is executable: the launcher and final verifier check the frozen values rather than relying on a narrative promise.

Each stage then passes admission gates immediately before measurement. The approved power supply and power policy must be unchanged; displays must be asleep; the screensaver and low-power mode must be off; thermal pressure must be nominal; and central- and graphics-processor activity must meet the quiet-state criteria. Known background work is allowed to finish before the window, followed by a settling interval, rather than being ignored during analysis. Runtime and telemetry identities, clock anchoring, sample cadence, calibration freshness, and post-run environment observations are also checked. No environment override can produce a claim-bearing member.

### Counterbalanced order

Comparisons use A/B/B/A blocks, abbreviated **ABBA**. Conditions A and B are measured in the order A, B, B, A, with ordinary cooldown between members. Averaging the two outer A observations and the two inner B observations cancels a linear time trend within the block to first order. For null-floor calibration, A and B are aliases of the exact same configuration and payload, so any nonzero block delta is a false comparative effect. For scientific contrasts, the A and B definitions are frozen in advance, and the contrast is computed within each block before blocks are aggregated. ABBA reduces common drift; it does not replace the measured whole-window drift allowance.

### Evidence custody and refusals

Every member is a self-contained bundle of configuration, raw power trace, runtime events, environment observations, and derived summary. Cryptographic hashes bind those files to the campaign manifest. Failed or interrupted artifacts are never deleted or overwritten. An occupied retry slot is moved to a quarantine area outside the active runs root; the exact member is recollected only under an allowed retry; and an append-only supersession record names which occurrence governs. Two present bundles for one occurrence refuse. The final whole-window verdict binds the exact member-occurrence set, calibration bracket, policy, and drift evidence by hash, so a later consumer cannot silently select a more favorable subset.

Collection does not continue indefinitely through environmental interruptions. Each stage attempt stops at its first member failure, and after the same cause fails a window stage for the third time the window itself closes rather than being retried; in actual operation, nights with three environmental member interruptions were closed and preserved as salvage rather than repeatedly retried. The surviving data may remain diagnostic, but it becomes claim-bearing only if the pre-registered verdict and extraction rules accept the exact resulting basis. This abandon-after-three rule limits outcome-dependent retrying and makes the cost of a noisy environment visible.

The custody chain continues after collection. The immutable corpus is backed up before extraction. The extractor re-authenticates member hashes, required files and cross-file consistency, calibration identity, environment admission, complete campaign membership, cooldown evidence, phase metric identity, and the whole-window drift allowance. It excludes or refuses a cell according to the frozen rules; missing uncertainty never becomes zero. The current artifact boundary is stated honestly: until floor artifacts are independently bound to their source extraction, a claim-bearing floor must be produced by protocol-controlled extraction in the same controlled custody session as the analysis that consumes it. A standalone floor file is not independently claim-licensing.

The refusal log is part of the evaluation, not an embarrassment to omit. It records contaminated members, out-of-family calibration, stale drift evidence, unresolved clock anchors, duplicate occurrences, and below-floor effects. In one real end-of-night case, the governed re-evaluation refused a window because a member's internal clock alignment could not be resolved. Independent adjudication found that refusal correct. The result remained non-claim-bearing: an example of the fail-closed design working as intended, not a software defect to be bypassed.

## 6. Instrument characterization (C-iv)

Instrument characterization asks whether the complete measurement system behaves predictably when driven by signals whose qualitative answer is known in advance. The workload is therefore a test signal, not yet the scientific finding. All tests retain the same calibration, admission, custody, and floor rules as the later demonstration measurements. Existing campaign fragments are not promoted where the governing whole-window verdict did not pass; the table marks the required claim-bearing results explicitly.

| Property | Characterization method | What a passing result would establish | Claim-bearing result |
|---|---|---|---|
| Linearity | Hold the prompt profile fixed and ramp the requested output from 128 to 2048 tokens. Regress gross request and decode energy on the runtime-observed output count; inspect residual structure as well as the fitted slope. | Energy responds proportionally over the tested dynamic range, and the fitted per-token slope can serve as the known-effect standard for floor probes on this stack. It would not establish linearity outside the tested range or on another stack. | **[PENDING WINDOW C]** |
| Null response across magnitudes | Run identical A-equals-B ABBA blocks at short, medium, and long output magnitudes. Evaluate the paired deltas against zero and against the predicted decision envelopes. | The comparison path does not create a directional effect merely because total energy or duration changes, and false contrasts across the tested range are contained by the error model. A non-significant result alone is insufficient; the interval must be interpreted relative to the floor. | **[PENDING WINDOW C]** |
| Empirical floor verification | Use the pre-registered linearity slope to create micro-deltas with predicted effects near 0.5, 1, 1.5, and 3 times the declared floor. Test positive and negative directions in counterbalanced blocks. | Sub-floor effects are refused while sufficiently super-floor effects clear in both directions. This is an operational check of the detection boundary, not a validation of the counter's absolute gain. | **[PENDING WINDOW C]** |
| Phase-attribution causal consistency | First compare the sum of separately integrated phase energies with the gross energy over their enclosing request. Then vary output length while holding prompt tokens fixed and fit the slope of prefill energy against output length. | Phase accounting is additive within its stated boundaries, and energy assigned to prefill does not acquire a systematic dependence on work that occurs later in decode. Together these tests challenge both missing energy and cross-phase leakage. | **[PENDING WINDOW C]** |
| Drift and settling | Place long controlled holds and fixed reference workloads through the window, including start, midpoint, and end references. After operator or stage activity, repeat the reference while recording the time required for thermal and admission observables to stabilize; compare it with the 180 s operating convention. | The measured drift trajectory is contained by the published allowance, and the chosen settling time is supported or revised from observed recovery rather than convenience. Endpoint agreement alone is not enough if the midpoint reveals curvature. | **[PENDING WINDOW C]** |
| Between-session stability | Repeat calibrations, null blocks, and floor cells across at least three sessions or days with the full stack identity recorded. | The calibration and floor are stable enough to reuse only under their declared freshness and identity rules, or reveal that a new session must mint a new floor. | **[PENDING WINDOW C]** |

Linearity and the null ladder test complementary failure modes. A smooth response can still carry an offset, and a zero-centered null can coexist with a nonlinear scale. The micro-delta experiment then closes the loop by using the measured slope to place effects deliberately below and above the declared decision boundary. Success requires the instrument to refuse the former and resolve the latter in both directions; merely observing larger effects with larger workloads is not sufficient.

The causal tests address the most important phase-specific risk. Additivity checks conservation inside the declared request boundary: phase intervals should reconcile with the enclosing total, subject to explicitly labeled setup or gap intervals. Causal invariance checks direction: holding the prompt fixed while increasing later decode work should not change energy attributed to earlier prefill. A nonzero prefill slope would indicate boundary leakage, shared-state coupling that invalidates the simple phase model, or both; it would narrow the claim rather than be explained away.

Temporal characterization separates slow drift from thermal settling. Start, midpoint, and end references expose whole-window curvature, while post-transition references estimate how long the system takes to return to its admitted state after operator activity or stage churn. Repetition across days tests whether one session's calibration is representative under identical recorded bindings. Internal channel-sum versus package reconciliation is retained as a secondary consistency check. External wall-power regression remains conditional on a suitable meter and would validate totals only; the pulse experiment remains the evidence for phase splitting.

Every resulting figure and table will identify the physical unit, operating-system version and build, runtime and relevant library versions, model artifact hash, quantization, tokenizer identity, sampler and output policy, configured and realized batch/concurrency policy, measurement boundary, and telemetry backend. Silent omission is not permitted. Measurements support stack-specific conclusions only; independent replication or a calibrated boundary bridge would be required for hardware-class, vendor-class, or cross-boundary rankings.

## 7. Demonstration results (C-v)

**[RESULT PENDING RE-MINT]**

This section will report phase-resolved gross joules per request for two model sizes, with tokenizer-scoped joules per prompt token and per output token as companion metrics. It will contain the pre-registered same-boundary model-size contrast, its interval, the complete floor decomposition, the claim-side bound, the effect-to-floor ratio, and the final resolvable/unresolved verdict. No demonstration energy value from the superseded mint is carried into this draft. A quantization ladder will be included only if it is collected under its own stack-specific floors and the frozen window budget permits it.

## 8. Related work

### LLM inference energy measurement

TokenPowerBench provides one of the closest reporting structures: it separates prompt-processing and token-generation energy, uses phase-appropriate token denominators, and groups results by context length [TokenPowerBench]. Its disclosed method, however, does not specify the boundary events, alignment rule, repetition and variance protocol, idle baseline, or external validation, and continuous batching makes an “active phase” label difficult to interpret when requests overlap. JouleWise adopts phase-specific reporting but restricts its primary scope to one sequential request, where runtime-emitted phase boundaries are well posed and can be calibrated.

The Illusion of Power Capping in LLM Decode samples graphics-processor power, integrates those samples, repeats configurations, and cross-checks sufficiently long operations against a separate hardware energy counter [IllusionPowerCapping]. This is a stronger measurement template than an unqualified software reading. Its counter agreement, run-to-run variation, snapshot fallback, and timing alignment nevertheless remain separate diagnostics rather than one bound on the reported effect, and its long sweeps do not use a drift-control ordering. JouleWise composes those classes of uncertainty into a decision rule for each contrast.

Apple-focused system comparisons reinforce the need for boundary labels. Silicon Showdown compares a graphics-board boundary on one platform with a whole-system-on-chip `powermetrics` boundary on Apple hardware, while runtimes and precision stacks also differ [SiliconShowdown]. Intelligence-per-Watt and ML.ENERGY similarly emphasize breadth across deployed inference configurations [IntelligencePerWatt; MLENERGY]. Such studies answer valuable systems questions, but unlike boundaries and software stacks cannot by themselves support a hardware-class causal ranking. JouleWise therefore makes the named stack and measurement boundary part of every result and prioritizes within-boundary effects.

### Software power counters and measurement standards

RAPL in Action established a validation agenda for commodity software counters: align lag before comparing streams, model wall power rather than assuming identity, account for temporal correlation, warm the system, measure sampler overhead, and inspect update granularity, overflow, jitter, and timestamp behavior [RAPLInAction]. Jay and Ostapenco likewise regress software readings against wall power and show that disagreement varies with load; they avoid claims about subtotals that the reference meter cannot observe [JayOstapenco]. JouleWise follows this epistemic boundary. A future external meter could test total gain and load dependence, but it would not validate how a total is divided between prefill and decode. The in-window pulse train addresses that distinct question.

MLPerf Power and SPEC require load-specific analyzer uncertainty, fixed ranges, clock synchronization, minimum intervals, invalid-sample accounting, and controlled battery behavior [MLPerfPower]. JouleWise translates their per-run reject-on-missing-evidence principle to a consumer software counter. The difference is that its principal uncertainty is not only an analyzer specification; it includes whether samples at a software-defined phase edge belong inside or outside the integral.

### Metrology and experimental discipline

Prospective paired minimum-detectable-effect methods estimate the smallest effect a planned paired study has adequate statistical power to find. They size the study from the variance of paired differences and can impose a one-way prior ratchet: observed variability may raise the planned threshold but may not lower it after outcomes are seen [PairedMDE]. JouleWise uses that logic for prospective workload sizing, but it does not treat the worst-case attribution term as independent random noise. Root-sum-square composition would be anti-conservative for a systematic edge-placement bound. Instead, the analysis maximizes over calibrated edge positions, measures drift with bracketed references, and publishes the resulting floor with the effect.

This emphasis changes the role of failed runs. A rejected admission, stale calibration, contaminated member, or below-floor contrast is evidence about the instrument's operating domain. Hash-bound raw traces, runtime events, configurations, supersessions, verdicts, and pre-registration records make that evidence re-reducible. The refusal is retained rather than disappearing behind a final average.

### Split and disaggregated inference

Split, or disaggregated, inference places prompt processing and token generation on different devices and transfers intermediate state between them. Revisiting Disaggregation Energy reports that the energy outcome depends on load, baseline, and transfer conditions on its evaluated two-graphics-processor node [RevisitingDisaggregationEnergy]. DualScale studies phase placement and per-phase power control on homogeneous server hardware [DualScale]. Prima.cpp includes whole-run energy and communication accounting but not a per-stage energy split [PrimaCPP], while SplitZip characterizes lossless transfer compression without making an energy claim [SplitZip].

JouleWise does not claim a new split scheduler in this paper. Split inference is instead a demanding future demonstration of the instrument because it introduces two physical boundaries, a transfer interval, and clock alignment across devices. A valid comparison would have to measure both ends, name each boundary, and clear a pre-registered floor or calibrated bridge. Whether splitting saves energy remains an empirical outcome; the reusable contribution is a method that can issue, qualify, or refuse the result.

exec
/bin/zsh -lc "sed -n '1,220p' CLAIMS_STATUS.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
# Claims Status

**The single standing home for "what can we actually claim right now."**
Every scientific number the project can publish, is holding, or must not
repeat — with its exact validity state and blocker. Refresh this file
whenever claim-bearing state changes (a verdict, a mint, a merge in the
D-095 chain, an adjudication); quote verdicts as issued, never
reinterpreted. Companion docs: `RUN_STATE.md` (session pointer),
`WINDOW_STATUS.md` (machine state), `docs/decision_log.md` (policy).

Last updated: **2026-08-07** (D-117: the historical re-mint path is
SUPERSEDED — structurally closed at main after the D-116 issuance
(candidate discovery excludes import-marked receipts by design); the
claim path forward is THREE PROSPECTIVE WINDOWS — fresh 1.5B decode
floor, fresh 7B decode floor, fresh decode contrast — live-bracketed
under the issued acceptance regime, with prefill floor cells riding
both floor windows. Prior "re-mint conditions" in this file are
historical: D-109 landed (PR #100), issuance executed (D-116, PR #109),
validator pin widening landed (PR #105). Full record:
`docs/process_traces/2026-08-06-d110-remint-fork/`.)

Earlier header (2026-08-03 night, for the record): D-108/D-109 ruled +
executed; D-110 made mint #1 retroactively NON-CLAIM-BEARING; window B
re-evaluation STOPPED → D-112; mint-1 re-derivability proven
byte-identical; report: `docs/run_reports/2026-08-03-16h-runway.md`.

---

## 1. VALID — minted, mainline, citable

**NONE at this checkpoint.** D-110 (2026-08-03, sweep finding RT-1)
made mint #1 and every number derived from it retroactively
non-claim-bearing: its floors embed a never-zero allowance of ZERO
where D-102 pin 3 mandates +max(drift, 0.010818 s) (~+43% on the a10
operative bound). The previously-listed values (operative 7.377086 J;
a10 components 3.823787 / 3.592138 J; window C comparative 7.377086 J)
move to §5 until the re-mint. The DERIVATION toolchain itself is
proven honest: the full pinned replay (2026-08-03) reproduced both
extraction reports, the artifact, and the statement BYTE-IDENTICAL
(`docs/process_traces/2026-08-03-q1-remint-bytecompare/`). The taint is
semantic (the selector the era used), not derivational.
**2026-08-07 (D-117):** the historical re-mint order is SUPERSEDED —
all three former re-mint conditions completed (D-109 via PR #100;
issuance via D-116/PR #109; pin widening via PR #105) and the FIRST
consumption attempt then proved historical consumption structurally
closed at main. Replacement: three prospective windows (D-117 cl.2);
the never-zero allowance correction binds their mints. All four PASSED
window verdicts remain untainted (sweep RT-5), but pre-genesis windows
CANNOT be claim-consumed — their role is diagnostic and
rule-establishing only.

**Standing measurement fact (D-078 cl.11, Ed-ratified):** the instrument
is attribution-limited (~1 J), not noise-limited (~0.3 J). Floors
publish LABELLED with the widened number; the effective clearable
effect for phase contrasts is floor + claim-side bound ≈ 5 J. No
instrument-tightening program.

## 2. EVIDENCE-BEARING — collected and verdict-PASSED, awaiting a specific gate

| Candidate claim | Value (prose-only until gated) | Window / verdict | Blocker |
|---|---|---|---|
| **7B decode floors (Qwen2.5-7B)** | absolute 6.294380135190098 J / comparative 13.998036715259254 J (absolute-cell member mean 192.386233 J, n=10 — always name the cell) | `window_7bfloor_20260729`, **PASSED**, governed extraction clean | **RE-SCOPED by D-117 (2026-08-07):** `window_7bfloor_20260729` is pre-genesis and cannot be claim-consumed; these values are DIAGNOSTIC and design inputs for the fresh 7B floor window (D-117 cl.2). The prior D-110 condition chain completed and was then superseded. |
| **1.5B-vs-7B decode contrast** (demonstration study #1) | **Registered claim metric (frozen v3 manifest): `phase_energy_j.decode`, 7B−1.5B = 141.29 J per block.** The widely-quoted 146.730349 J (σ 0.241 J, n=10 ABBA) is the `idle_subtracted_energy_j` whole-request DIAGNOSTIC — quote it only labelled as such, never as the claim (sweep DC-1; both reproduce byte-exactly from disk). | `window_contrast_20260730`, **PASSED** | **RE-SCOPED by D-117 (2026-08-07):** `window_contrast_20260730` is pre-genesis and cannot be claim-consumed; values are DIAGNOSTIC and the design template for the fresh contrast window (D-117 cl.2). The D-095 chain now runs through the prospective windows' mints. |

## 3. COLLECTED — verdicts FAILED as-issued; adjudication RULED (D-100, 2026-08-01)

The machinery adjudication is complete (MET-VERDICT-ADJ-01 → D-100 cold-
gate synthesis). Both verdicts **stand as issued, permanently by
construction**: any licensed re-evaluation appends a NEW row under
`consumption_semantics_id: salvage_dangler_exclusion_v1` with a new
pinned basis; the original FAILED rows are never edited and govern
default consumption. Outcomes per window:

- **Window A: permanently non-claim-bearing.** Its only post-cal retry
  binds a T1-incompatible power-policy identity (immutable evidence; the
  machinery's rejection was CORRECT), so no calibration bracket can ever
  form. C1 re-collects in a future window.
- **Window B: TERMINALLY CLAIM-RETIRED (D-113, Ed ruling 2026-08-05):
  RETAINED_IMMUTABLE / PERMANENTLY_NON_CLAIM_BEARING.** Ed chose
  abandonment over salvage ("soundness and quality of the project and
  claims above all"): no re-evaluation or claim consumption will ever
  occur; the WB-specific D-100/D-106/D-108 license chain is retired
  (general machinery survives for other windows);
  `WINB-R06-DISPOSITION-01` closes ABANDONED_FOR_FRESH_COLLECTION;
  labelled read-only forensic/diagnostic use remains permitted ("Window
  B, original verdict FAILED, D-113 claim-retired, non-claim
  evidence"). Every still-desired WB claim component re-collects fresh
  beginning Window C — no WB member enters a replacement claim basis.
  The F7 scope question is ANSWERED: whole-window voiding is affirmed
  as the current semantics (a cell-scoped alternative only via the
  D-083 cold gate; not built). Historical record of the 2026-08-03
  attempt below. The whole chain executed: D-108 ruled
  (clause (c) retired), row `D100-BII-BINDING-01` CLOSED (PR #99 +
  clause-(d) three-occurrence digest-bound re-record), closure +
  membership-binding artifacts authored and dry-authorized, D-093 scan
  clean 1/1, frozen corpus verified byte-identical (210+4 files, zero
  mismatches). The governed re-evaluation then REFUSED pre-verdict:
  survivor consumption failed on `mtadd-p2048o0128-r06`'s
  collection-time clock-anchor failure (`native_intersection_empty`) —
  the cold gate ruled this CORRECT fail-closed machinery (classification
  (i), convergent instruments; record
  `docs/process_traces/2026-08-03-winB-reeval-stop/`). No licensed
  channel removes r06 (exclusion cap spent on r08; not a dangler;
  waivers forbidden), and the NEG-8 drift bound expired 2026-08-02, so
  no PASS path exists under the license as drawn. Original FAILED
  verdict untouched. The WB NEG-8 bound re-mint obligation is MOOT
  under D-113; the near-run-time freshness rule continues to bind
  every future window (runbook + D-078, by cross-reference).

| Paper claim | Campaign | Collected | State after D-100 |
|---|---|---|---|
| **C1 — linearity** | `linearity_ramp` | **40/40** (window A) | DEAD for claims (window A permanent FAIL); re-collect (window C/D); data usable as design input (micro_delta slope) + corroboration diagnostics only |
| **C2 — null ladder** | `null_ladder` | o0128 + o0512 collected in window B — **returned to uncollected-for-claim state (D-113)**; o2048 never collected | Re-collect ALL of C2 fresh (window C, or split per the frozen plan); no WB member enters a replacement claim basis |
| **C3 — micro-delta** | `micro_delta` | not collected | Plan is draft-pending-slope by design; slope fit may consume window A ramp as DESIGN input (not a claim) |
| **C4 — additivity** | `additivity_shapes` | 23/24 single-root collected in window B — **returned to uncollected-for-claim state (D-113)**; 21/24 window-A corroborating remain labelled non-claim diagnostics | Re-collect C4 fresh (window C/D per the frozen plan). F7 ANSWERED by D-113: whole-window voiding affirmed as current semantics; no cell-scoped salvage |
| **C5 — long holds** | `long_holds` | not collected → window C | — |

## 4. Standing gates on EVERY claim consumption

1. ~~D-088 cl.3(c) three-check bench scan~~ — **LIFTED 2026-08-02**: the
   cooldown-join gauntlet closed (commit 3 merged, PR #93 `cb860e1`);
   the landed machinery now enforces these properties structurally
   (result-map completeness, counting domain, authenticated v2
   discrimination).
2. ~~D-093 raw-vs-validated supersession-record scan~~ — **LIFTED
   2026-08-02** with the gauntlet's close per its row contract; the
   validated reader boundary (PR #91) plus the commit-3 authenticated
   catalog own raw-record visibility permanently.
3. Verdicts consumed as issued; overrides only via the cold-gate path
   with written dissent Ed sees. (UNCHANGED — permanent.)
4. NEW (D-105): while `C3-RECOGNIZER-EXACT-01` is open, the tail
   recognizer's accepted set may only shrink, and the custody sidecar +
   writer-side key assertion may not be weakened.

## 5. DO NOT QUOTE — retired, void, or wrong-as-stated

- **ALL mint #1 floors as claims (D-110, 2026-08-03): operative
  7.377086 J, a10 components 3.823787 / 3.592138 J, window C
  comparative 7.377086 J** — retroactively non-claim-bearing (zero
  allowance where D-102 pin 3 mandates +max(drift, 0.010818 s));
  citable again only after the ruled re-mint under the repaired
  selector.
- **146.730349 J as "the contrast claim"** — it is the
  idle_subtracted_energy_j whole-request diagnostic; the registered
  claim metric is phase_energy_j.decode = 141.29 J (sweep DC-1). Either
  number only as prose with its metric named, neither as a gated claim
  yet.

- **3.17 / 2.94 J** floors — pre-allowance attribution-width
  diagnostics only (D-079 cl.5).
- **3.592138 J as "the decode floor"** — it is the isolated absolute
  component; the operative floor is 7.377086 J (D-084).
- **4.923 J item / 24.62 J suite** comparative floors — Ventura
  screensaver contamination artifacts (2026-07-17 campaign).
- Old window B (`04_phase_prefill_abba`) figures — verdict FAILED
  (`instrument_calibration_mismatch`, GPU DVFM ramp aliasing), corpus
  preserved but not claim-bearing.
- All pre-repair (pre-D-078) powermetrics corpora for claim use —
  time-anchor defect (D-078 soundness gate).
- Window A/B metrology numbers as claims — see §3 (verdicts FAILED as
  issued; window A permanently dead for claims; window B only via a NEW Ed ruling (D-112: the re-evaluation was performed 2026-08-03 and correctly refused; license exhausted as drawn).
- **Window A C1 linearity figures in any claim context** — the corpus
  is design-input/diagnostic only, permanently (D-100 + the immutable
  T1-incompatible retry).

## 6. Instrument findings queued for the paper (not claims yet)

- **Clock-anchor knife-edge** (2026-08-01 Sol consult, accepted): at
  197 s capture length the native-second intersection margin is ~±1 ms
  and the unmodeled wall/monotonic rate (~−12 ppm ≈ 2.3 ms/capture)
  exceeds it; pass/fail is quantization-phase luck. Desk item:
  rate-aware anchor design; directly publishable as a metrology
  limitation/finding.
- **Quiet-state definition**: validated windows now include suspended
  cloud sync (bird-SIGSTOP protocol) — claims describe that controlled
  state, not an arbitrary unattended Mac.
- **Operator-session streaming hazard**: the operating session's own
  output streaming can fail a member's idle admission (window B
  failure #3) — a reproducible environmental-validity observation.

exec
/bin/zsh -lc "sed -n '1,250p' docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Complete D-117 freeze design: three prospective windows fit the envelope, but live-ledger sessions, multi-cell minting, and D-102 successor generation must land before any arm.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": "dbb9685669ac76ea65bf458b78eeb98d94bc6a80",
    "head_end": "94a24e562290b59f7b40908315bbae7a032ea47e",
    "upstream_end": "94a24e562290b59f7b40908315bbae7a032ea47e",
    "branch": "main"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "title": "The current ledger cannot safely reserve both bookend observations under one unchanged committed head",
        "detail": "The append path requires the physical ledger head to equal the committed pin before each reservation. Finalizing the pre observation advances the physical head, so an ordinary post reservation cannot occur without an intervening pin advance or a new bracket-session capability.",
        "recommendation": "Implement an atomic two-slot bracket-session capability plus exact postcollection bracket binding before freezing arm packets."
      },
      {
        "id": "F2",
        "severity": "blocker",
        "title": "The generalized mint is still decode-only and single-plan/single-cell",
        "detail": "The current generalized path hard-checks phase_energy_j.decode and a decode phase target. It cannot mint the two prefill riders or D-095's required combined multi-cell, multi-plan floor artifact.",
        "recommendation": "Introduce pinset v2 with per-plan component pins and an aggregate four-cell artifact pinset."
      },
      {
        "id": "F3",
        "severity": "blocker",
        "title": "No usable D-102 successor-artifact path exists for a live-prefixed ledger",
        "detail": "The issued acceptance artifact is exact-byte pinned and prior-set verification assumes the issuance corpus. A valid range-expanding live observation could therefore stop a campaign before member one or prevent its verdict.",
        "recommendation": "Pre-build and cold-gate a deterministic successor builder, registry, live-prefix verification, and trigger-time operator procedure."
      },
      {
        "id": "F4",
        "severity": "should_fix",
        "title": "The referenced prefill-feasibility synthesis is absent at the inspected HEAD",
        "detail": "docs/process_traces/2026-08-07-prefill-feasibility/SYNTHESIS.md does not exist in this worktree even though RUN_STATE says the trace was custodied.",
        "recommendation": "Recover or commit the trace before lead ratification; this memo uses D-117's adopted summary as authority."
      },
      {
        "id": "F5",
        "severity": "should_fix",
        "title": "Current queue rows still encode superseded C/D and D-110 gates",
        "detail": "TASK_QUEUE.md still presents MET-WINDOW-C-01 and MINT-GENERALIZE-01 under terminology and blockers superseded by D-117.",
        "recommendation": "Regenerate queue/state views from the owning state kernel after the plan-freeze decision is ratified."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git status --short --branch && git rev-parse HEAD && git rev-parse '@{upstream}'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## main...origin/main",
          "94a24e562290b59f7b40908315bbae7a032ea47e",
          "94a24e562290b59f7b40908315bbae7a032ea47e"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "94a24e562290b59f7b40908315bbae7a032ea47e$"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "test -f docs/decision_log.md && test -f docs/process_traces/2026-08-06-d110-remint-fork/CONSULT-RESPONSE.md && test ! -e docs/process_traces/2026-08-07-prefill-feasibility/SYNTHESIS.md",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    }
  ],
  "flags": [
    {
      "id": "FLAG1",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "main advanced concurrently from dbb9685 to 94a24e5 during the read-only consult; the final state was re-inspected and remained clean.",
      "needs": "Freeze implementation scopes against 94a24e5 or a later explicitly reviewed head."
    },
    {
      "id": "FLAG2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "No suites were run because this was a read-only design consult with no implementation.",
      "needs": "Each implementation unit below carries focused and canonical-suite obligations."
    }
  ]
}
```

## Findings

### F1 — Live-ledger bookending is not yet armable (blocker)

D-116’s issued ledger is the correct trust root, and D-117 correctly requires fresh live pre/post observations. The obstacle is mechanical: the present append path requires the physical ledger head to match the committed pin when reserving an attempt. Once the pre observation is finalized, that equality no longer holds for an ordinary post reservation.

The best design is an atomic `calibration_window_bracket_session.v1` capability:

1. At the pre-bookend, under a clean committed head, append one receipt reserving exactly two immutable slots: `pre` and `post`, each with its attempt ID, plan ID/SHA, evidence-root ID, expected time role, and shared session ID.
2. Finalize the pre slot before member one.
3. Leave the post slot prospectively open without treating it as an unresolved candidate or permitting claim evaluation.
4. Finalize or explicitly abort the post slot at the closing bookend.
5. Commit the terminal ledger head once, then issue an exact `calibration_bracket_binding.v1` mapping the frozen plan and evidence root to the two finalized content/receipt digests.
6. Candidate discovery still examines the complete live candidate universe; the binding selects the claimed pair but cannot hide extra candidates.

This is preferable to a source commit after the pre observation: that would mutate the repository and readiness head inside every quiet-window procedure. Two ordinary reservations appended in advance are also inferior because the outstanding post reservation would look unresolved unless ledger semantics were widened anyway.

Base plans should freeze calibration retry count at zero. A failed pre observation aborts before member one and closes the unused post slot; a failed post makes the physical attempt non-claim-bearing. If the lead wants one cause-removal retry, the session capability needs additional prospectively numbered slots and deterministic selection semantics before freeze—never an improvised retry.

Ideal no-failure receipt evolution from the issued sequence-76 head is three receipts per window—session capability, pre finalization, post finalization—ending at sequence 85 after all three windows. Exact sequence numbers are arm-time facts, not desk-frozen plan literals.

### F2 — The mint path needs a real v2, not another widened literal list (blocker)

The current mechanism is `scripts/floor_mint_pinsets/mint1.json` plus `scripts/mint_floor_artifact_generalized.py`. It already embodies the right principle—plans supply hard pins and the mint compares rather than derives—but it remains structurally limited:

- one plan and one artifact cell;
- `phase_energy_j.decode` only;
- `["phase","decode"]` only;
- no aggregate artifact over independently collected plans.

D-095 requires one multi-cell floor artifact whose 1.5B and 7B cells remain independently stack-scoped. D-117 adds prefill cells to both floor plans. The correct closure is therefore one four-cell artifact, not two loosely associated artifacts:

| Cell | Producer | Metric | Scientific family |
|---|---|---|---|
| 1.5B decode | 1.5B floor plan | `phase_energy_j.decode` | existing `df-ph-decode` |
| 1.5B prefill rider | 1.5B floor plan | `phase_energy_j.prefill` | new exact rider family |
| 7B decode | 7B floor plan | `phase_energy_j.decode` | D-085 `df-ph-decode-qwen25-7b` |
| 7B prefill rider | 7B floor plan | `phase_energy_j.prefill` | new exact rider family |

Each producer gets a component pinset; an aggregate pinset hard-checks both components and mints `d117-qwen25-phase-floor-set-v1`. Gamma consumes the two decode cells through D-095’s predeclared transport groups. It does not relabel contrast configs as floor configs.

### F3 — The D-102 successor packet is a pre-arm dependency (blocker)

A valid pre calibration can expand the observed range or approach the valid-observation limit. The issued artifact cannot absorb that live prefix today. The campaign therefore needs the following on disk and cold-gated before its first §5A arm:

- deterministic successor builder and validator;
- authenticated acceptance registry mapping acceptance ID to exact artifact SHA, derivation SHA, cutoff receipt, parent acceptance ID, and parent ledger head;
- generalized prior-set validation over a complete authenticated import-plus-live prefix;
- exact Decimal arithmetic, rounding, budget, prediction, and screen reproduction from D-079;
- a dry-run fixture that produces exact successor bytes and expected head pin;
- trigger-disposition logic that judges the range-expanding observation under the prior artifact before incorporating it into the successor;
- operator commands for pre-trigger and post-trigger branches.

I recommend deriving a successor from all content-distinct, valid, same-epoch observations through the chosen cutoff. Systematic, ordinary-invalid, aborted, or unresolved attempts remain recorded but excluded. The lead should explicitly ratify that corpus rule because D-102 establishes the successor obligation but does not fully spell out this live-prefix derivation policy.

At the pre bookend, a range expansion stops the chain before member one: close or preserve the bracket session according to the frozen state machine, commit the current ledger head, build and authenticate the successor, revalidate, then proceed. A post range expansion follows the same process after science but before the verdict. Systematic mismatch is a refusal, never something a successor can launder.

### F4 — Referenced trace missing (should-fix)

The named `docs/process_traces/2026-08-07-prefill-feasibility/SYNTHESIS.md` is absent at `94a24e5`. D-117 itself records the adopted conclusion, so this memo treats the following as governing:

- floor prefill cells ride the floor-window decode members;
- gamma remains decode-only;
- the historical 128-token prefill contrast was marginal;
- a prospectively frozen 256-token contrast remains Ed’s option.

The missing trace prevents verification of any additional numerical assumptions it may contain. In particular, this memo does not freeze a 256-token runtime or effect-size target.

### F5 — Queue terminology is superseded (should-fix)

`TASK_QUEUE.md` still carries `MET-WINDOW-C-01`, prospective “C/D” splitting, and an old `MINT-GENERALIZE-01` D-110 blocker. Those rows cannot govern this work. D-117 clause 5 owns the namespace, and the live `RUN_STATE.md` block now recognizes that ruling. The queue should be regenerated after ratification, not manually interpreted during arm readiness.

### Ranked design decisions and rejected alternatives

1. **Use a two-slot ledger session capability and exact bracket binding.** Rejected: implicit reuse of neighboring observations, mid-window Git pin commits, or pre-reserving ordinary unresolved observations.

2. **Mint one four-cell floor artifact through pinset v2.** Rejected: two unrelated floor artifacts, summing arm floors, or weakening D-095’s independently stack-scoped maximum.

3. **Freeze zero calibration retries in the base plans.** Rejected: unbounded cause-removal retries and post hoc choice among observations. A retry-enabled variant requires a different capability state machine before freeze.

4. **Make prefill a metric rider over the exact decode members.** Rejected: copying the old dedicated 4096-prompt/64-output prefill workload, because that would add members and estimate a different condition. Post hoc extraction without a pre-registered cell is also insufficient.

5. **Treat the 256-token contrast as a fourth window plan.** Rejected: appending it to gamma later, which would change gamma’s plan SHA, member universe, order, multiplicity, runtime, and verdict basis.

6. **Use semantic immutable identifiers without dates or letters.** Rejected: `Window D`, C/D, and date-derived identities. Attempt dates belong in custody metadata, not scientific identity.

7. **Use a two-stage pin freeze.** Desk time freezes every knowable identifier, schema, member list, hash, and rule. Six-decimal operative values freeze only after governed collection and extraction. Rejected: placeholder literals presented as valid pins or any mint-time derivation.

### Proven template lineage

The templates are scientific and structural sources, not claim evidence.

| Plan | Files treated as the proven template | What is reused |
|---|---|---|
| 1.5B floor | `configs/campaigns/p2_015_floors/calibration_plan.json`; its SHA sidecar and generator; `02_phase_absolute/p2015-df-ph-decode-abs-r01.json` through `r10.json`; `05_phase_decode_abba/`’s forty decode configs and manifest; root `order_manifest.json`; `configs/floor_mint/a10_extraction_spec.json`; `configs/floor_mint/window_c_extraction_spec.json` | Exact Qwen2.5-1.5B stack identity, 10 absolute members, ten fixed A/B/B/A null blocks, runtime/config conventions, extraction shape |
| 7B floor | Entire `configs/campaigns/qwen25_7b_decode_floor_v1/`, including plan, SHA, generator, root/stage manifests, ten absolute configs, and two twenty-member ABBA halves | Ratified D-085 condition family, Qwen2.5-7B model identity, 10+40 design, midpoint split |
| Decode contrast | Entire `configs/campaigns/splitwise_decode_v1/`, particularly the plan, generator, forty configs, root/stage manifests, condition families, and `analysis_manifest_v3.json` | A=1.5B, B=7B, ten ABBA blocks, B−A orientation, v3 estimator and cross-stack floor rule |
| Operational references | `configs/campaigns/neg8_reference_corpus/` and the existing start/mid/end reference manifests | Twelve-member same-window NEG8 binding plus 3/1/3 references |

The old `02_phase_absolute/order_manifest.json` contains thirty interleaved decode, prefill, and short-prefill configs. It must not be copied as the new absolute manifest. Only its ten decode configs are the alpha source; the new ten-entry manifest is regenerated and independently hashed.

Historical results are diagnostic inputs only. No old evidence-root ID, calibration bracket, member output, or operative floor literal enters a prospective claim basis.

### Immutable identifier proposal

| Placeholder | Frozen plan ID | Evidence-root ID | Physical root |
|---|---|---|---|
| W-alpha | `plan-d117-floor-qwen25-1p5b-decode-p128-prefill-rider-v1` | `evidence-d117-floor-qwen25-1p5b-v1` | `runs_d117_floor_qwen25_1p5b_v1` |
| W-beta | `plan-d117-floor-qwen25-7b-decode-p128-prefill-rider-v1` | `evidence-d117-floor-qwen25-7b-v1` | `runs_d117_floor_qwen25_7b_v1` |
| W-gamma | `plan-d117-contrast-qwen25-1p5b-vs-7b-decode-v1` | `evidence-d117-contrast-qwen25-1p5b-vs-7b-v1` | `runs_d117_contrast_qwen25_1p5b_vs_7b_v1` |

Each also gets a separately named bound root ending in `_bound`. Failed physical attempts receive custody attempt suffixes outside the scientific ID; the clean evidence root is never silently reused.

### Common order-manifest contract

Every root manifest should bind:

- plan ID, exact plan SHA, generator SHA, and model/runtime revisions;
- ordered stage records with exact stage-manifest ID, SHA, expected member count, predecessor, and successor;
- exact relative config paths and config SHAs—no globs or directory discovery;
- ordinal, member ID, ABBA block and slot where applicable;
- fixed reference and NEG8 manifests;
- the prefill rider mapping for floor members;
- frozen attempt policy, including zero calibration retries and no outcome-driven top-ups;
- evidence-root ID and expected fresh physical path;
- hashes of condition families, extraction spec, and analysis manifest;
- arm-time attachment slots for the readiness record, session capability, and actual receipt identifiers without modifying frozen plan bytes.

An ABBA stage manifest records each block as `A1,B1,B2,A2`. Splitting blocks 1–5 and 6–10 around the midpoint reference does not reset block numbering.

### Per-window plans

#### Alpha — 1.5B decode floor plus prefill rider

| Stage | Members | Order |
|---|---:|---|
| Pre calibration | 1 live observation | Finalize reserved `pre` slot before science |
| Same-window bound corpus | 12 | Frozen NEG8 order, then bound evaluation |
| Start references | 3 | Frozen triplet |

exec
/bin/zsh -lc "sed -n '251,540p' docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
| Absolute floor | 10 | `abs-r01` through `abs-r10` |
| Null half 1 | 20 | ABBA blocks 1–5 |
| Midpoint reference | 1 | Frozen midpoint |
| Null half 2 | 20 | ABBA blocks 6–10 |
| End references | 3 | Frozen triplet |
| Post calibration | 1 live observation | Finalize reserved `post` slot |
| Closeout | 0 science members | Terminal head pin, bracket binding, verdict, dual-root backup |

Science count is 50; operational captures are 12 bound, 7 references, and 2 calibrations. The prefill rider adds no member and no runtime.

The rider is a new condition family over the same 128-prompt/512-output decode bundles. It must pre-register `phase_energy_j.prefill`, phase precheck `["phase","prefill"]`, exact tokenizer/model/config identity, the same ten absolute members and forty null members, its estimator, n=10 block basis, and both absolute and comparative floor rules. It is not the old dedicated prefill condition.

The extraction spec contains four cells: decode absolute, decode comparative, prefill absolute, and prefill comparative. It names 100 cell-member references but exactly 50 unique bundles. Each cell supplies an exact member list, config hash list, expected n, condition-family hash, metric key, phase precheck, order-manifest pin, calibration basis, and evidence-root ID. Missing prefill phases, fallback values, or member discovery outside the list are fatal.

#### Beta — 7B decode floor plus prefill rider

The schedule is identical to alpha: pre calibration; 12 NEG8; start 3; absolute 10; ABBA blocks 1–5; midpoint 1; blocks 6–10; end 3; post calibration.

The decode condition remains D-085’s `df-ph-decode-qwen25-7b`; the fresh plan does not rename settled scientific semantics. The new prefill-rider family pins `phase_energy_j.prefill` over the exact 7B decode members and stack revision.

Its extraction contract is the same four-cell/50-unique-bundle shape as alpha. Old 7B values—absolute 6.294380… J and comparative 13.998036… J—are budget/design diagnostics only and are not pre-registered pins.

#### Gamma — 1.5B-versus-7B decode contrast

| Stage | Members | Order |
|---|---:|---|
| Pre calibration | 1 live observation | Finalize `pre` slot |
| Same-window bound corpus | 12 | Frozen NEG8 order, then bound evaluation |
| Start references | 3 | Frozen triplet |
| Contrast half 1 | 20 | ABBA blocks 1–5 |
| Midpoint reference | 1 | Frozen midpoint |
| Contrast half 2 | 20 | ABBA blocks 6–10 |
| End references | 3 | Frozen triplet |
| Post calibration | 1 live observation | Finalize `post` slot |
| Closeout | 0 science members | Pin, binding, verdict, backup, then analysis |

The frozen manifest remains decode-only:

- A is the exact 1.5B stack; B is the exact 7B stack.
- Metric is exactly `phase_energy_j.decode`.
- Estimand orientation is B−A.
- Design is ten A/B/B/A blocks, n=10 block estimates.
- Estimator is `abba_block_arm_mean_difference_t_v1`.
- Test is two-sided at family alpha 0.05, with the positive direction stated as the scientific hypothesis rather than used to change the test.
- `equivalence_margin` and `mde` remain null unless prospectively ruled otherwise.
- Floor rule remains `cross_stack_armwise_max.v1`: independently resolve the 1.5B and 7B decode cells and take their maximum, never their sum.
- Claim-side anchor bounds remain separate from the detection-floor operation.
- The finalized analysis basis pins the exact forty member paths, config hashes, stack identities, floor artifact bytes, calibration binding, and evidence root.

### Runtime evidence and budgets

Historical evidence in `docs/phase_2/splitwise_decode_campaign.md` §4 supplies:

- 1.5B decode member: 92.7 s, measured n=40;
- 1.5B reference member: 90.5 s, measured n=7;
- 7B decode member: approximately 97 s from the measured/probed anchor;
- 1.5B/7B mixed ABBA half: about 31.6 min raw member time.

The stage allowances incorporate the configured 30-second idle, warmup/teardown, stage arm overhead, and cooldown conventions. The pre-calibration allowance includes the required 180-second post-admin settle. The separate ten-minute untouched quiet-idle gate is added before applying the 20% margin.

| Component, minutes | Alpha | Beta | Gamma |
|---|---:|---:|---:|
| Pre calibration bracket | 8 | 8 | 8 |
| 12 NEG8 bound members | 22 | 22 | 22 |
| Bound evaluation | 1 | 1 | 1 |
| Start 3 references | 8 | 8 | 8 |
| Absolute 10 | 19 | 20 | — |
| ABBA blocks 1–5 | 34 | 36 | 35 |
| Midpoint reference | 5 | 5 | 5 |
| ABBA blocks 6–10 | 34 | 36 | 35 |
| End 3 references | 8 | 8 | 8 |
| Post calibration bracket | 8 | 8 | 8 |
| Campaign subtotal | 147 | 152 | 130 |
| Untouched pre-arm idle | 10 | 10 | 10 |
| Base occupancy | 157 | 162 | 140 |
| With 20% failure margin | **188.4** | **194.4** | **168.0** |
| Hours | **3.14 h** | **3.24 h** | **2.80 h** |
| 2–4 h envelope | Pass | Pass | Pass |

The margin is time headroom, not authority to add members, replace a cap-hit observation, or top up an unfavorable result. The fixed manifest and frozen failure policy decide scientific validity.

### §5A operator bookends

Before each window:

1. Verify the reviewed plan/readiness record, fresh empty roots, model artifacts, charger/AC state, power policy, OS/tool identity, empty waiver set, and current acceptance artifact.
2. Verify the physical ledger head equals the authenticated committed pin.
3. Correct the clock against the trusted source, record the correction and `usingnetworktime` state, turn network time off, and settle for at least 180 seconds.
4. Establish zero-agent/zero-output-streaming conditions and complete ten untouched minutes of daemon idle.
5. Append the exact two-slot bracket session capability.
6. Capture and finalize the pre observation; run the acceptance and D-102 trigger probe.
7. Only after every gate is green, emit the one-line arm message and walk away.

At the closing bookend:

1. Capture the post observation before changing power, network-time, or workload state.
2. Finalize the post slot or write the governed failure/abort closure.
3. Commit and authenticate the terminal ledger head.
4. Emit the exact bracket binding and whole-window verdict from one immutable ledger snapshot.
5. Back up evidence and bound roots with verified return code and hashes.
6. Restore network time and record the restoration only after measurement completion and custody closeout.

### Prefill floor claim eligibility

A rider is claim-eligible only if desk freeze already binds:

- exact metric and phase path;
- exact workload parameters, model/tokenizer revision, seeds, quantization, runtime, sampling, and telemetry mode;
- absolute and comparative member lists and order manifests;
- exact condition-family ID and hash;
- n and estimator;
- calibration cell, acceptance artifact role, and D-110 allowance rule;
- extraction failure behavior;
- allowed consumer families.

For each metric, the operative floor is the maximum of independently evaluated absolute and comparative components. Apply D-110 once as `A_s = max(observed_drift, 0.010818)`. Never sum components and never borrow a decode floor for prefill.

### Two-stage mint freeze

**Desk-frozen pin requirements**

For each floor plan, freeze:

- plan ID, declared SHA, sidecar SHA, and actual artifact SHA;
- evidence-root ID;
- four intended cell roles across the two plans;
- condition-family IDs/hashes;
- metric and phase-precheck paths;
- absolute and comparative order-manifest IDs/hashes;
- extraction-spec SHA and exact members;
- expected counts;
- model/runtime/config hashes;
- calibration acceptance artifact ID/SHA/derivation rule;
- D-110 never-zero allowance rule;
- aggregate artifact ID and transport allowlists.

These live in a non-mintable `pin_requirements.v2` artifact. Unresolved values must be structurally absent or explicitly marked unresolved; the file cannot satisfy the final pinset schema.

**Postcollection-frozen pins**

After passed verdicts and governed extraction, freeze separately for each of the four cells:

- absolute and comparative evaluation-basis SHA/count;
- exact accepted pre/post receipt and content digests;
- bracket-binding SHA and terminal ledger head;
- observed drift and applied allowance;
- extraction-report SHA;
- absolute, comparative, and operative values;
- the operative literal formatted independently as exactly six decimals using the repository’s `.6f` convention.

The lead independently recomputes each six-decimal literal from primary extraction bytes. The mint only compares supplied literals and hashes; it does not calculate them. The old `7.377086` literal is never reused.

Gamma has no producer mint. Its consumer pinset instead binds the exact combined floor artifact bytes, the two decode-cell IDs, its plan/order/analysis manifests, and its finalized evaluation basis.

### Synthetic three-window live-ledger regression

The fixture begins with the exact issued-ledger semantics: 76 receipts, including 38 historical import observations—30 valid, 2 systematic, 6 ordinary-invalid. Candidate discovery must exclude every import-marked observation.

The no-failure live extension adds three bracket capabilities and six finalized live observations. From one immutable final snapshot, the regression must prove:

- exactly six live candidates and zero imported candidates;
- alpha, beta, and gamma each bind only their own pre/post pair;
- all six are same-epoch, causal, fresh, within protocol and T1 limits;
- no neighboring endpoint can substitute for a bound endpoint;
- all three verdicts use the same complete candidate universe;
- the ideal terminal sequence is 85 under the proposed three-receipt session model;
- the D-110 never-zero allowance remains active.

Required refusal vectors:

- import-marker removal, import leakage, or candidate-discovery regression;
- missing, duplicate, reordered, or conflicting session/finalization receipts;
- open or abandoned session without a governed closure;
- physical-head/pin mismatch, rollback, fork, or uncommitted terminal head;
- omitted, added, duplicated, off-ledger, or content-substituted observations;
- missing, tampered, swapped, or cross-window bracket binding;
- noncausal endpoint, stale endpoint, T1 failure, protocol failure, or epoch mismatch;
- systematic classification;
- one range-expanding live observation requiring a successor;
- the observation-count boundary reaching the D-102 limit;
- a successor whose prior set omits or changes an authenticated prefix.

### Optional 256-token prefill contrast

Clean attachment inside frozen gamma is impossible. Adding the arm changes the workload, metric family, members, order, runtime, multiplicity, plan digest, evidence root, and verdict basis.

If Ed adopts it, create a fourth independently frozen, independently calibrated plan and evidence root. It may attach later only in a higher-level synthesis/claim packet that references gamma and the new prefill result as sibling artifacts. Gamma’s bytes remain unchanged.

The floor riders here use the prefill phase of the 128-prompt decode workload. They do not automatically transport to a prospectively defined 256-token contrast. The fourth plan needs either exact matching prefill floor cells or a separately predeclared and justified transport rule. No placeholder members or plan ID should be added to gamma now.

### Freeze order and lead gates

1. **Ruling gate:** lead accepts the session-capability semantics, zero-retry policy, successor corpus rule, four-cell artifact shape, and fourth-window treatment.
2. **Toolchain gate:** ledger session/binding, successor builder, pinset v2, multi-cell mint, prefill metric support, and three-window regression all land and pass focused plus canonical suites.
3. **Desk freeze gate:** generate all three campaign packs; freeze identifiers, model revisions, configs, manifests, condition families, extraction/analysis specs, budgets, failure policy, and hashes. Six-decimal values do not yet exist.
4. **Per-window arm gate:** attach current clean head, acceptance artifact, physical/committed ledger equality, fresh roots, exact environment preflight, empty waivers, §5A evidence, and bracket-session identifiers.
5. **Pre-science trigger gate:** finalize the pre observation and either accept it, issue a governed successor, or abort before member one.
6. **Post-window gate:** finalize post, commit terminal head, issue bracket binding, verdict, and verified backup.
7. **Floor mint gate:** after alpha and beta pass, run governed four-cell extraction, independently freeze literals, mint the combined artifact, and require `validate_floor_artifact` to return no findings.
8. **Gamma claim gate:** pass the whole-window verdict, finalize the v3 basis, run D-093 root scanning, resolve both decode arm floors from exact combined-artifact bytes, and apply the armwise maximum.

### Work-order list with enforced WRITE_SCOPE units

| Unit | Exact write scope | Invariants and tests | Dependency |
|---|---|---|---|
| U1 — ledger session and binding | `joulewise/calibration_ledger.py`; `joulewise/calibration_bracketing.py`; `scripts/reserve_calibration_window_bracket.py`; `tests/test_calibration_ledger.py`; `tests/test_calibration_bracketing.py` | Two immutable slots, one-use finalization, governed abort, no unresolved-candidate leakage, exact binding, head/pin refusals. Focused ledger/bracketing tests plus full suite. | Foundation; independent of U3 |
| U2 — D-102 successor engine | `joulewise/calibration_bracketing.py`; `scripts/build_calibration_acceptance_successor.py`; `configs/calibration/calibration_acceptance_registry.json`; `tests/test_calibration_acceptance_successor.py` | Complete authenticated live prefix, deterministic bytes, parent ancestry, exact Decimal derivation, range/count triggers, systematic refusal. Focused cold-gate fixtures plus full suite. | Sequential after U1 because of shared bracketing semantics |
| U3 — pinset v2 and multi-cell mint | `scripts/mint_floor_artifact_generalized.py`; `scripts/floor_mint_pinsets/schema_v2.json`; `joulewise/detection_floor.py`; `tests/test_mint_floor_artifact_generalized.py` | Decode and prefill metrics, per-plan component pins, aggregate four-cell pins, no derived literals, no cross-stack sum, v1 compatibility. Focused parity/refusal tests plus full suite. | Independent of U1/U2 |
| U4 — three-window ledger regression | `tests/fixtures/calibration_live_three_window/**`; `tests/test_calibration_live_three_window.py` | Exact issuance fixture, import exclusion, six live candidates, three causal bindings, successor and refusal vectors. | After U1 and U2 |
| U5 — alpha campaign pack | `configs/campaigns/d117_floor_qwen25_1p5b_v1/**`; `configs/floor_mint/d117_qwen25_1p5b_extraction_spec.json`; `tests/test_d117_floor_qwen25_1p5b_plan.py` | Exact 10+40 schedule, split midpoint, two metric riders, 50 unique bundles, fresh IDs, deterministic regeneration. | After U3 schema/IDs freeze; parallel with U6 |
| U6 — beta campaign pack | `configs/campaigns/d117_floor_qwen25_7b_v1/**`; `configs/floor_mint/d117_qwen25_7b_extraction_spec.json`; `tests/test_d117_floor_qwen25_7b_plan.py` | Same as U5, retaining D-085 stack/family identity. | After U3; parallel with U5 |
| U7 — gamma campaign pack | `configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v1/**`; `tests/test_d117_decode_contrast_plan.py` | Forty ABBA members, decode-only metric, B−A orientation, v3 estimator, exact four-cell artifact consumer pins, no prefill placeholder. | After U3 floor cell/transport IDs freeze |
| U8 — operator/readiness packet | `docs/phase_2/window_runbook.md`; `scripts/validate_frozen_plan_readiness.py`; `tests/test_frozen_plan_readiness.py` | §5A sequence, session capability, pre-trigger successor gate, fresh roots, empty waivers, terminal binding/pin/backup. | After U1, U2, U5–U7 |
| U9 — state and custody bookkeeping | `docs/process/state_kernel.json`; `RUN_STATE.md`; `TASK_QUEUE.md`; `CLAIMS_STATUS.md`; `docs/run_reports/2026-08-07-d117-plan-freeze.md` | D-117 vocabulary, no C/D plan references, exact frozen digests, generated-view consistency. | Lead-owned, after all desk artifacts pass |
| U10 — postcollection pin closure | `scripts/floor_mint_pinsets/d117_qwen25_1p5b_v2.json`; `scripts/floor_mint_pinsets/d117_qwen25_7b_v2.json`; `scripts/floor_mint_pinsets/d117_qwen25_phase_floor_set_v2.json`; `results/floor_artifacts/d117_qwen25_phase_floor_set_v1.json`; `results/floor_artifacts/d117_qwen25_phase_floor_set_v1.sha256` | Only postcollection facts; independent literal recomputation; exact receipt/binding/head pins; validator returns no findings. | Sequential after alpha and beta pass |

Every unit should run its focused tests and `python3 -m unittest discover -s tests`. Shared files make U1→U2 sequential; U1 and U3 can proceed independently. U5 and U6 can proceed independently after U3 freezes the vocabulary. U7 waits for final floor-cell and transport identifiers. U10 is deliberately absent from the desk freeze.

### What the lead should double-check

- Recover the missing prefill-feasibility trace and compare its exact 256-token assumptions with this fourth-window conclusion.
- Ratify the two-slot ledger capability against D-109/D-116, especially whether an open post slot may exist during the pre-science successor probe.
- Decide explicitly between zero calibration retries and a prospectively numbered retry-capability variant.
- Ratify the D-102 successor corpus rule: all content-distinct valid same-epoch observations through the cutoff.
- Confirm that D-085’s 7B decode family ID is preserved and contrast transport uses allowlists rather than relabeling configs.
- Confirm pinset v2 supports multiple producer plans while preserving byte-for-byte v1 behavior.
- Verify the 20% allowance does not become permission for member replacement or result-driven top-up.
- Recheck full model revisions, local artifact hashes, runtime version, charger identity, and post-move environment at each arm.
- Independently calculate all four `.6f` operative literals from primary extraction bytes.
- Verify every one of the fifty floor bundles actually contains the registered prefill phase; a missing phase must fail extraction.
- Ensure gamma takes the maximum of the two decode arm floors, never their sum, and retains separate claim-side anchor bounds.
- Ensure the 128-prompt prefill riders are not presented as a floor for a later 256-token contrast without exact transport evidence.
- Regenerate the active queue from the state kernel so superseded C/D and D-110 gates cannot be mistaken for arm authority.
- Freeze against the final reviewed repository head; this consult began at `dbb9685` and ended cleanly at concurrently advanced `94a24e5`.

## Residual risk

No live timings, calibration observations, successor generation, or mint replay were performed. Runtime estimates therefore inherit historical-machine variance; the 20% margin is the current mitigation.

The absent feasibility synthesis limits review of the optional 256-token arm. Its attachment architecture is sound, but its member count, runtime, estimand, and floor transport remain intentionally unfrozen.
exec
/bin/zsh -lc "sed -n '1,250p' docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Complete D-117 freeze design: three prospective windows fit the envelope, but live-ledger sessions, multi-cell minting, and D-102 successor generation must land before any arm.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": "dbb9685669ac76ea65bf458b78eeb98d94bc6a80",
    "head_end": "94a24e562290b59f7b40908315bbae7a032ea47e",
    "upstream_end": "94a24e562290b59f7b40908315bbae7a032ea47e",
    "branch": "main"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "title": "The current ledger cannot safely reserve both bookend observations under one unchanged committed head",
        "detail": "The append path requires the physical ledger head to equal the committed pin before each reservation. Finalizing the pre observation advances the physical head, so an ordinary post reservation cannot occur without an intervening pin advance or a new bracket-session capability.",
        "recommendation": "Implement an atomic two-slot bracket-session capability plus exact postcollection bracket binding before freezing arm packets."
      },
      {
        "id": "F2",
        "severity": "blocker",
        "title": "The generalized mint is still decode-only and single-plan/single-cell",
        "detail": "The current generalized path hard-checks phase_energy_j.decode and a decode phase target. It cannot mint the two prefill riders or D-095's required combined multi-cell, multi-plan floor artifact.",
        "recommendation": "Introduce pinset v2 with per-plan component pins and an aggregate four-cell artifact pinset."
      },
      {
        "id": "F3",
        "severity": "blocker",
        "title": "No usable D-102 successor-artifact path exists for a live-prefixed ledger",
        "detail": "The issued acceptance artifact is exact-byte pinned and prior-set verification assumes the issuance corpus. A valid range-expanding live observation could therefore stop a campaign before member one or prevent its verdict.",
        "recommendation": "Pre-build and cold-gate a deterministic successor builder, registry, live-prefix verification, and trigger-time operator procedure."
      },
      {
        "id": "F4",
        "severity": "should_fix",
        "title": "The referenced prefill-feasibility synthesis is absent at the inspected HEAD",
        "detail": "docs/process_traces/2026-08-07-prefill-feasibility/SYNTHESIS.md does not exist in this worktree even though RUN_STATE says the trace was custodied.",
        "recommendation": "Recover or commit the trace before lead ratification; this memo uses D-117's adopted summary as authority."
      },
      {
        "id": "F5",
        "severity": "should_fix",
        "title": "Current queue rows still encode superseded C/D and D-110 gates",
        "detail": "TASK_QUEUE.md still presents MET-WINDOW-C-01 and MINT-GENERALIZE-01 under terminology and blockers superseded by D-117.",
        "recommendation": "Regenerate queue/state views from the owning state kernel after the plan-freeze decision is ratified."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git status --short --branch && git rev-parse HEAD && git rev-parse '@{upstream}'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## main...origin/main",
          "94a24e562290b59f7b40908315bbae7a032ea47e",
          "94a24e562290b59f7b40908315bbae7a032ea47e"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "94a24e562290b59f7b40908315bbae7a032ea47e$"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "test -f docs/decision_log.md && test -f docs/process_traces/2026-08-06-d110-remint-fork/CONSULT-RESPONSE.md && test ! -e docs/process_traces/2026-08-07-prefill-feasibility/SYNTHESIS.md",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    }
  ],
  "flags": [
    {
      "id": "FLAG1",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "main advanced concurrently from dbb9685 to 94a24e5 during the read-only consult; the final state was re-inspected and remained clean.",
      "needs": "Freeze implementation scopes against 94a24e5 or a later explicitly reviewed head."
    },
    {
      "id": "FLAG2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "No suites were run because this was a read-only design consult with no implementation.",
      "needs": "Each implementation unit below carries focused and canonical-suite obligations."
    }
  ]
}
```

## Findings

### F1 — Live-ledger bookending is not yet armable (blocker)

D-116’s issued ledger is the correct trust root, and D-117 correctly requires fresh live pre/post observations. The obstacle is mechanical: the present append path requires the physical ledger head to match the committed pin when reserving an attempt. Once the pre observation is finalized, that equality no longer holds for an ordinary post reservation.

The best design is an atomic `calibration_window_bracket_session.v1` capability:

1. At the pre-bookend, under a clean committed head, append one receipt reserving exactly two immutable slots: `pre` and `post`, each with its attempt ID, plan ID/SHA, evidence-root ID, expected time role, and shared session ID.
2. Finalize the pre slot before member one.
3. Leave the post slot prospectively open without treating it as an unresolved candidate or permitting claim evaluation.
4. Finalize or explicitly abort the post slot at the closing bookend.
5. Commit the terminal ledger head once, then issue an exact `calibration_bracket_binding.v1` mapping the frozen plan and evidence root to the two finalized content/receipt digests.
6. Candidate discovery still examines the complete live candidate universe; the binding selects the claimed pair but cannot hide extra candidates.

This is preferable to a source commit after the pre observation: that would mutate the repository and readiness head inside every quiet-window procedure. Two ordinary reservations appended in advance are also inferior because the outstanding post reservation would look unresolved unless ledger semantics were widened anyway.

Base plans should freeze calibration retry count at zero. A failed pre observation aborts before member one and closes the unused post slot; a failed post makes the physical attempt non-claim-bearing. If the lead wants one cause-removal retry, the session capability needs additional prospectively numbered slots and deterministic selection semantics before freeze—never an improvised retry.

Ideal no-failure receipt evolution from the issued sequence-76 head is three receipts per window—session capability, pre finalization, post finalization—ending at sequence 85 after all three windows. Exact sequence numbers are arm-time facts, not desk-frozen plan literals.

### F2 — The mint path needs a real v2, not another widened literal list (blocker)

The current mechanism is `scripts/floor_mint_pinsets/mint1.json` plus `scripts/mint_floor_artifact_generalized.py`. It already embodies the right principle—plans supply hard pins and the mint compares rather than derives—but it remains structurally limited:

- one plan and one artifact cell;
- `phase_energy_j.decode` only;
- `["phase","decode"]` only;
- no aggregate artifact over independently collected plans.

D-095 requires one multi-cell floor artifact whose 1.5B and 7B cells remain independently stack-scoped. D-117 adds prefill cells to both floor plans. The correct closure is therefore one four-cell artifact, not two loosely associated artifacts:

| Cell | Producer | Metric | Scientific family |
|---|---|---|---|
| 1.5B decode | 1.5B floor plan | `phase_energy_j.decode` | existing `df-ph-decode` |
| 1.5B prefill rider | 1.5B floor plan | `phase_energy_j.prefill` | new exact rider family |
| 7B decode | 7B floor plan | `phase_energy_j.decode` | D-085 `df-ph-decode-qwen25-7b` |
| 7B prefill rider | 7B floor plan | `phase_energy_j.prefill` | new exact rider family |

Each producer gets a component pinset; an aggregate pinset hard-checks both components and mints `d117-qwen25-phase-floor-set-v1`. Gamma consumes the two decode cells through D-095’s predeclared transport groups. It does not relabel contrast configs as floor configs.

### F3 — The D-102 successor packet is a pre-arm dependency (blocker)

A valid pre calibration can expand the observed range or approach the valid-observation limit. The issued artifact cannot absorb that live prefix today. The campaign therefore needs the following on disk and cold-gated before its first §5A arm:

- deterministic successor builder and validator;
- authenticated acceptance registry mapping acceptance ID to exact artifact SHA, derivation SHA, cutoff receipt, parent acceptance ID, and parent ledger head;
- generalized prior-set validation over a complete authenticated import-plus-live prefix;
- exact Decimal arithmetic, rounding, budget, prediction, and screen reproduction from D-079;
- a dry-run fixture that produces exact successor bytes and expected head pin;
- trigger-disposition logic that judges the range-expanding observation under the prior artifact before incorporating it into the successor;
- operator commands for pre-trigger and post-trigger branches.

I recommend deriving a successor from all content-distinct, valid, same-epoch observations through the chosen cutoff. Systematic, ordinary-invalid, aborted, or unresolved attempts remain recorded but excluded. The lead should explicitly ratify that corpus rule because D-102 establishes the successor obligation but does not fully spell out this live-prefix derivation policy.

At the pre bookend, a range expansion stops the chain before member one: close or preserve the bracket session according to the frozen state machine, commit the current ledger head, build and authenticate the successor, revalidate, then proceed. A post range expansion follows the same process after science but before the verdict. Systematic mismatch is a refusal, never something a successor can launder.

### F4 — Referenced trace missing (should-fix)

The named `docs/process_traces/2026-08-07-prefill-feasibility/SYNTHESIS.md` is absent at `94a24e5`. D-117 itself records the adopted conclusion, so this memo treats the following as governing:

- floor prefill cells ride the floor-window decode members;
- gamma remains decode-only;
- the historical 128-token prefill contrast was marginal;
- a prospectively frozen 256-token contrast remains Ed’s option.

The missing trace prevents verification of any additional numerical assumptions it may contain. In particular, this memo does not freeze a 256-token runtime or effect-size target.

### F5 — Queue terminology is superseded (should-fix)

`TASK_QUEUE.md` still carries `MET-WINDOW-C-01`, prospective “C/D” splitting, and an old `MINT-GENERALIZE-01` D-110 blocker. Those rows cannot govern this work. D-117 clause 5 owns the namespace, and the live `RUN_STATE.md` block now recognizes that ruling. The queue should be regenerated after ratification, not manually interpreted during arm readiness.

### Ranked design decisions and rejected alternatives

1. **Use a two-slot ledger session capability and exact bracket binding.** Rejected: implicit reuse of neighboring observations, mid-window Git pin commits, or pre-reserving ordinary unresolved observations.

2. **Mint one four-cell floor artifact through pinset v2.** Rejected: two unrelated floor artifacts, summing arm floors, or weakening D-095’s independently stack-scoped maximum.

3. **Freeze zero calibration retries in the base plans.** Rejected: unbounded cause-removal retries and post hoc choice among observations. A retry-enabled variant requires a different capability state machine before freeze.

4. **Make prefill a metric rider over the exact decode members.** Rejected: copying the old dedicated 4096-prompt/64-output prefill workload, because that would add members and estimate a different condition. Post hoc extraction without a pre-registered cell is also insufficient.

5. **Treat the 256-token contrast as a fourth window plan.** Rejected: appending it to gamma later, which would change gamma’s plan SHA, member universe, order, multiplicity, runtime, and verdict basis.

6. **Use semantic immutable identifiers without dates or letters.** Rejected: `Window D`, C/D, and date-derived identities. Attempt dates belong in custody metadata, not scientific identity.

7. **Use a two-stage pin freeze.** Desk time freezes every knowable identifier, schema, member list, hash, and rule. Six-decimal operative values freeze only after governed collection and extraction. Rejected: placeholder literals presented as valid pins or any mint-time derivation.

### Proven template lineage

The templates are scientific and structural sources, not claim evidence.

| Plan | Files treated as the proven template | What is reused |
|---|---|---|
| 1.5B floor | `configs/campaigns/p2_015_floors/calibration_plan.json`; its SHA sidecar and generator; `02_phase_absolute/p2015-df-ph-decode-abs-r01.json` through `r10.json`; `05_phase_decode_abba/`’s forty decode configs and manifest; root `order_manifest.json`; `configs/floor_mint/a10_extraction_spec.json`; `configs/floor_mint/window_c_extraction_spec.json` | Exact Qwen2.5-1.5B stack identity, 10 absolute members, ten fixed A/B/B/A null blocks, runtime/config conventions, extraction shape |
| 7B floor | Entire `configs/campaigns/qwen25_7b_decode_floor_v1/`, including plan, SHA, generator, root/stage manifests, ten absolute configs, and two twenty-member ABBA halves | Ratified D-085 condition family, Qwen2.5-7B model identity, 10+40 design, midpoint split |
| Decode contrast | Entire `configs/campaigns/splitwise_decode_v1/`, particularly the plan, generator, forty configs, root/stage manifests, condition families, and `analysis_manifest_v3.json` | A=1.5B, B=7B, ten ABBA blocks, B−A orientation, v3 estimator and cross-stack floor rule |
| Operational references | `configs/campaigns/neg8_reference_corpus/` and the existing start/mid/end reference manifests | Twelve-member same-window NEG8 binding plus 3/1/3 references |

The old `02_phase_absolute/order_manifest.json` contains thirty interleaved decode, prefill, and short-prefill configs. It must not be copied as the new absolute manifest. Only its ten decode configs are the alpha source; the new ten-entry manifest is regenerated and independently hashed.

Historical results are diagnostic inputs only. No old evidence-root ID, calibration bracket, member output, or operative floor literal enters a prospective claim basis.

### Immutable identifier proposal

| Placeholder | Frozen plan ID | Evidence-root ID | Physical root |
|---|---|---|---|
| W-alpha | `plan-d117-floor-qwen25-1p5b-decode-p128-prefill-rider-v1` | `evidence-d117-floor-qwen25-1p5b-v1` | `runs_d117_floor_qwen25_1p5b_v1` |
| W-beta | `plan-d117-floor-qwen25-7b-decode-p128-prefill-rider-v1` | `evidence-d117-floor-qwen25-7b-v1` | `runs_d117_floor_qwen25_7b_v1` |
| W-gamma | `plan-d117-contrast-qwen25-1p5b-vs-7b-decode-v1` | `evidence-d117-contrast-qwen25-1p5b-vs-7b-v1` | `runs_d117_contrast_qwen25_1p5b_vs_7b_v1` |

Each also gets a separately named bound root ending in `_bound`. Failed physical attempts receive custody attempt suffixes outside the scientific ID; the clean evidence root is never silently reused.

### Common order-manifest contract

Every root manifest should bind:

- plan ID, exact plan SHA, generator SHA, and model/runtime revisions;
- ordered stage records with exact stage-manifest ID, SHA, expected member count, predecessor, and successor;
- exact relative config paths and config SHAs—no globs or directory discovery;
- ordinal, member ID, ABBA block and slot where applicable;
- fixed reference and NEG8 manifests;
- the prefill rider mapping for floor members;
- frozen attempt policy, including zero calibration retries and no outcome-driven top-ups;
- evidence-root ID and expected fresh physical path;
- hashes of condition families, extraction spec, and analysis manifest;
- arm-time attachment slots for the readiness record, session capability, and actual receipt identifiers without modifying frozen plan bytes.

An ABBA stage manifest records each block as `A1,B1,B2,A2`. Splitting blocks 1–5 and 6–10 around the midpoint reference does not reset block numbering.

### Per-window plans

#### Alpha — 1.5B decode floor plus prefill rider

| Stage | Members | Order |
|---|---:|---|
| Pre calibration | 1 live observation | Finalize reserved `pre` slot before science |
| Same-window bound corpus | 12 | Frozen NEG8 order, then bound evaluation |
| Start references | 3 | Frozen triplet |

exec
/bin/zsh -lc "sed -n '1,220p' CLAIMS_STATUS.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
# Claims Status

**The single standing home for "what can we actually claim right now."**
Every scientific number the project can publish, is holding, or must not
repeat — with its exact validity state and blocker. Refresh this file
whenever claim-bearing state changes (a verdict, a mint, a merge in the
D-095 chain, an adjudication); quote verdicts as issued, never
reinterpreted. Companion docs: `RUN_STATE.md` (session pointer),
`WINDOW_STATUS.md` (machine state), `docs/decision_log.md` (policy).

Last updated: **2026-08-07** (D-117: the historical re-mint path is
SUPERSEDED — structurally closed at main after the D-116 issuance
(candidate discovery excludes import-marked receipts by design); the
claim path forward is THREE PROSPECTIVE WINDOWS — fresh 1.5B decode
floor, fresh 7B decode floor, fresh decode contrast — live-bracketed
under the issued acceptance regime, with prefill floor cells riding
both floor windows. Prior "re-mint conditions" in this file are
historical: D-109 landed (PR #100), issuance executed (D-116, PR #109),
validator pin widening landed (PR #105). Full record:
`docs/process_traces/2026-08-06-d110-remint-fork/`.)

Earlier header (2026-08-03 night, for the record): D-108/D-109 ruled +
executed; D-110 made mint #1 retroactively NON-CLAIM-BEARING; window B
re-evaluation STOPPED → D-112; mint-1 re-derivability proven
byte-identical; report: `docs/run_reports/2026-08-03-16h-runway.md`.

---

## 1. VALID — minted, mainline, citable

**NONE at this checkpoint.** D-110 (2026-08-03, sweep finding RT-1)
made mint #1 and every number derived from it retroactively
non-claim-bearing: its floors embed a never-zero allowance of ZERO
where D-102 pin 3 mandates +max(drift, 0.010818 s) (~+43% on the a10
operative bound). The previously-listed values (operative 7.377086 J;
a10 components 3.823787 / 3.592138 J; window C comparative 7.377086 J)
move to §5 until the re-mint. The DERIVATION toolchain itself is
proven honest: the full pinned replay (2026-08-03) reproduced both
extraction reports, the artifact, and the statement BYTE-IDENTICAL
(`docs/process_traces/2026-08-03-q1-remint-bytecompare/`). The taint is
semantic (the selector the era used), not derivational.
**2026-08-07 (D-117):** the historical re-mint order is SUPERSEDED —
all three former re-mint conditions completed (D-109 via PR #100;
issuance via D-116/PR #109; pin widening via PR #105) and the FIRST
consumption attempt then proved historical consumption structurally
closed at main. Replacement: three prospective windows (D-117 cl.2);
the never-zero allowance correction binds their mints. All four PASSED
window verdicts remain untainted (sweep RT-5), but pre-genesis windows
CANNOT be claim-consumed — their role is diagnostic and
rule-establishing only.

**Standing measurement fact (D-078 cl.11, Ed-ratified):** the instrument
is attribution-limited (~1 J), not noise-limited (~0.3 J). Floors
publish LABELLED with the widened number; the effective clearable
effect for phase contrasts is floor + claim-side bound ≈ 5 J. No
instrument-tightening program.

## 2. EVIDENCE-BEARING — collected and verdict-PASSED, awaiting a specific gate

| Candidate claim | Value (prose-only until gated) | Window / verdict | Blocker |
|---|---|---|---|
| **7B decode floors (Qwen2.5-7B)** | absolute 6.294380135190098 J / comparative 13.998036715259254 J (absolute-cell member mean 192.386233 J, n=10 — always name the cell) | `window_7bfloor_20260729`, **PASSED**, governed extraction clean | **RE-SCOPED by D-117 (2026-08-07):** `window_7bfloor_20260729` is pre-genesis and cannot be claim-consumed; these values are DIAGNOSTIC and design inputs for the fresh 7B floor window (D-117 cl.2). The prior D-110 condition chain completed and was then superseded. |
| **1.5B-vs-7B decode contrast** (demonstration study #1) | **Registered claim metric (frozen v3 manifest): `phase_energy_j.decode`, 7B−1.5B = 141.29 J per block.** The widely-quoted 146.730349 J (σ 0.241 J, n=10 ABBA) is the `idle_subtracted_energy_j` whole-request DIAGNOSTIC — quote it only labelled as such, never as the claim (sweep DC-1; both reproduce byte-exactly from disk). | `window_contrast_20260730`, **PASSED** | **RE-SCOPED by D-117 (2026-08-07):** `window_contrast_20260730` is pre-genesis and cannot be claim-consumed; values are DIAGNOSTIC and the design template for the fresh contrast window (D-117 cl.2). The D-095 chain now runs through the prospective windows' mints. |

## 3. COLLECTED — verdicts FAILED as-issued; adjudication RULED (D-100, 2026-08-01)

The machinery adjudication is complete (MET-VERDICT-ADJ-01 → D-100 cold-
gate synthesis). Both verdicts **stand as issued, permanently by
construction**: any licensed re-evaluation appends a NEW row under
`consumption_semantics_id: salvage_dangler_exclusion_v1` with a new
pinned basis; the original FAILED rows are never edited and govern
default consumption. Outcomes per window:

- **Window A: permanently non-claim-bearing.** Its only post-cal retry
  binds a T1-incompatible power-policy identity (immutable evidence; the
  machinery's rejection was CORRECT), so no calibration bracket can ever
  form. C1 re-collects in a future window.
- **Window B: TERMINALLY CLAIM-RETIRED (D-113, Ed ruling 2026-08-05):
  RETAINED_IMMUTABLE / PERMANENTLY_NON_CLAIM_BEARING.** Ed chose
  abandonment over salvage ("soundness and quality of the project and
  claims above all"): no re-evaluation or claim consumption will ever
  occur; the WB-specific D-100/D-106/D-108 license chain is retired
  (general machinery survives for other windows);
  `WINB-R06-DISPOSITION-01` closes ABANDONED_FOR_FRESH_COLLECTION;
  labelled read-only forensic/diagnostic use remains permitted ("Window
  B, original verdict FAILED, D-113 claim-retired, non-claim
  evidence"). Every still-desired WB claim component re-collects fresh
  beginning Window C — no WB member enters a replacement claim basis.
  The F7 scope question is ANSWERED: whole-window voiding is affirmed
  as the current semantics (a cell-scoped alternative only via the
  D-083 cold gate; not built). Historical record of the 2026-08-03
  attempt below. The whole chain executed: D-108 ruled
  (clause (c) retired), row `D100-BII-BINDING-01` CLOSED (PR #99 +
  clause-(d) three-occurrence digest-bound re-record), closure +
  membership-binding artifacts authored and dry-authorized, D-093 scan
  clean 1/1, frozen corpus verified byte-identical (210+4 files, zero
  mismatches). The governed re-evaluation then REFUSED pre-verdict:
  survivor consumption failed on `mtadd-p2048o0128-r06`'s
  collection-time clock-anchor failure (`native_intersection_empty`) —
  the cold gate ruled this CORRECT fail-closed machinery (classification
  (i), convergent instruments; record
  `docs/process_traces/2026-08-03-winB-reeval-stop/`). No licensed
  channel removes r06 (exclusion cap spent on r08; not a dangler;
  waivers forbidden), and the NEG-8 drift bound expired 2026-08-02, so
  no PASS path exists under the license as drawn. Original FAILED
  verdict untouched. The WB NEG-8 bound re-mint obligation is MOOT
  under D-113; the near-run-time freshness rule continues to bind
  every future window (runbook + D-078, by cross-reference).

| Paper claim | Campaign | Collected | State after D-100 |
|---|---|---|---|
| **C1 — linearity** | `linearity_ramp` | **40/40** (window A) | DEAD for claims (window A permanent FAIL); re-collect (window C/D); data usable as design input (micro_delta slope) + corroboration diagnostics only |
| **C2 — null ladder** | `null_ladder` | o0128 + o0512 collected in window B — **returned to uncollected-for-claim state (D-113)**; o2048 never collected | Re-collect ALL of C2 fresh (window C, or split per the frozen plan); no WB member enters a replacement claim basis |
| **C3 — micro-delta** | `micro_delta` | not collected | Plan is draft-pending-slope by design; slope fit may consume window A ramp as DESIGN input (not a claim) |
| **C4 — additivity** | `additivity_shapes` | 23/24 single-root collected in window B — **returned to uncollected-for-claim state (D-113)**; 21/24 window-A corroborating remain labelled non-claim diagnostics | Re-collect C4 fresh (window C/D per the frozen plan). F7 ANSWERED by D-113: whole-window voiding affirmed as current semantics; no cell-scoped salvage |
| **C5 — long holds** | `long_holds` | not collected → window C | — |

## 4. Standing gates on EVERY claim consumption

1. ~~D-088 cl.3(c) three-check bench scan~~ — **LIFTED 2026-08-02**: the
   cooldown-join gauntlet closed (commit 3 merged, PR #93 `cb860e1`);
   the landed machinery now enforces these properties structurally
   (result-map completeness, counting domain, authenticated v2
   discrimination).
2. ~~D-093 raw-vs-validated supersession-record scan~~ — **LIFTED
   2026-08-02** with the gauntlet's close per its row contract; the
   validated reader boundary (PR #91) plus the commit-3 authenticated
   catalog own raw-record visibility permanently.
3. Verdicts consumed as issued; overrides only via the cold-gate path
   with written dissent Ed sees. (UNCHANGED — permanent.)
4. NEW (D-105): while `C3-RECOGNIZER-EXACT-01` is open, the tail
   recognizer's accepted set may only shrink, and the custody sidecar +
   writer-side key assertion may not be weakened.

## 5. DO NOT QUOTE — retired, void, or wrong-as-stated

- **ALL mint #1 floors as claims (D-110, 2026-08-03): operative
  7.377086 J, a10 components 3.823787 / 3.592138 J, window C
  comparative 7.377086 J** — retroactively non-claim-bearing (zero
  allowance where D-102 pin 3 mandates +max(drift, 0.010818 s));
  citable again only after the ruled re-mint under the repaired
  selector.
- **146.730349 J as "the contrast claim"** — it is the
  idle_subtracted_energy_j whole-request diagnostic; the registered
  claim metric is phase_energy_j.decode = 141.29 J (sweep DC-1). Either
  number only as prose with its metric named, neither as a gated claim
  yet.

- **3.17 / 2.94 J** floors — pre-allowance attribution-width
  diagnostics only (D-079 cl.5).
- **3.592138 J as "the decode floor"** — it is the isolated absolute
  component; the operative floor is 7.377086 J (D-084).
- **4.923 J item / 24.62 J suite** comparative floors — Ventura
  screensaver contamination artifacts (2026-07-17 campaign).
- Old window B (`04_phase_prefill_abba`) figures — verdict FAILED
  (`instrument_calibration_mismatch`, GPU DVFM ramp aliasing), corpus
  preserved but not claim-bearing.
- All pre-repair (pre-D-078) powermetrics corpora for claim use —
  time-anchor defect (D-078 soundness gate).
- Window A/B metrology numbers as claims — see §3 (verdicts FAILED as
  issued; window A permanently dead for claims; window B only via a NEW Ed ruling (D-112: the re-evaluation was performed 2026-08-03 and correctly refused; license exhausted as drawn).
- **Window A C1 linearity figures in any claim context** — the corpus
  is design-input/diagnostic only, permanently (D-100 + the immutable
  T1-incompatible retry).

## 6. Instrument findings queued for the paper (not claims yet)

- **Clock-anchor knife-edge** (2026-08-01 Sol consult, accepted): at
  197 s capture length the native-second intersection margin is ~±1 ms
  and the unmodeled wall/monotonic rate (~−12 ppm ≈ 2.3 ms/capture)
  exceeds it; pass/fail is quantization-phase luck. Desk item:
  rate-aware anchor design; directly publishable as a metrology
  limitation/finding.
- **Quiet-state definition**: validated windows now include suspended
  cloud sync (bird-SIGSTOP protocol) — claims describe that controlled
  state, not an arbitrary unattended Mac.
- **Operator-session streaming hazard**: the operating session's own
  output streaming can fail a member's idle admission (window B
  failure #3) — a reproducible environmental-validity observation.

exec
/bin/zsh -lc "sed -n '1,260p' docs/strategy/2026-08-06-impressiveness-roadmap.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
exec
/bin/zsh -lc "sed -n '1,180p' docs/research_question_registry.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
# Research Question Registry

Purpose: this is the canonical live index for JouleWise research questions,
capability claims, application ideas, and methodology artifacts. It normalizes
aliases, status, claim ceilings, owners, gates, and pre-hardware readiness so
claims and campaign plans can point to one row. Promotion rules are unchanged
from `docs/research_question_bank.md`: promotion still requires a named RQ slot
in `PROJECT_STATUS.md`, a data plan that does not displace queue ranks above
it, and scope fit.

Maintenance rule: registry rows are LIVE state. The research question bank
remains the historical and deliberative record, including council wording,
kills, quarantines, and amendments. Single-writer split: update this registry
for current indexing and cross-references; update the bank only when recording
new deliberation history.

Column legend:

- `canonical_id`: stable row key for the live index.
- `aliases`: other IDs, names, or capability-map labels for the same question.
- `question_type`: one of `research question`, `capability claim`,
  `application idea`, or `methodology artifact`.
- `status`: `promoted`, `banked`, `candidate`, `killed`, `answered-L1`, or
  the review-specific `candidate (C-023)`.
- `claim_ceiling`: highest claim level currently allowed by the bank, review,
  or capability map, before future evidence upgrades.
- `forbidden_upgrade`: short reminder of language the row cannot support.
- `AP owner`: analysis-plan owner if already named; otherwise `none-yet`.
- `campaign owner`: queue row, phase, or campaign owner if already named.
- `gate_class`: dominant gate class: `hardware`, `software`, `floor`,
  `substrate`, or `coordination`.
- `pre_hardware_preparable`: `fully`, `analysis-plan-only`, or `no`.
- `one-line note`: indexing note, not a re-adjudication.

## Registry Table

| canonical_id | aliases | question_type | status | claim_ceiling | forbidden_upgrade | AP owner | campaign owner | gate_class | pre_hardware_preparable | one-line note |
|---|---|---|---|---|---|---|---|---|---|---|
| Q1 | Split reduces energy | research question | promoted | L2 boundary-labeled; stronger only with calibration | no uncalibrated cross-boundary total-energy winner | none-yet | Phase 3 split; P1-004; P1-006 | hardware | fully | Central split question; total energy must be decomposed and boundary-labeled. |
| Q2 | Link bandwidth sensitivity | research question | promoted | L2 | no nominal-link crossover without measured links | none-yet | Phase 3 split; P1-004 | hardware | fully | Clean interconnect sensitivity question; link throughput and transfer energy must be measured. |
| Q3 | Split energy-latency Pareto | research question | promoted | L2 | no Pareto claim without frozen set and latency metric | none-yet | Phase 3 split | hardware | fully | Requires a fixed comparison set and latency metric per figure. |
| Q4 | Fixed-vs-marginal energy model; C5-2.14 cache-policy coefficient rider | research question | promoted | L3 | no holdout-prediction claim without AP-1 floor and residual checks | AP-1 | P2-019 q4_l3_shape_grid_v1 | floor | analysis-plan-only | Strongest predictive science row; includes compositional split-energy prediction only when transfer terms exist. C5-2.14 is a candidate rider capped at L2, earliest PF, with no coefficient-direction claim below P2-015 floors ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| Q5 | Ranking stability | research question | promoted | L2 | no uncalibrated cross-device winner; no ranking where gap below MDE | AP-3 | 2M; Window B grid | floor | analysis-plan-only | Promoted within-machine ranking question; workload-axis analogue C5-W.3 remains a separate candidate row. |
| Q6 | Boundary sensitivity; C5-2.10 boundary-directional bias quantification | research question | promoted | L2; L4 only with replication | no wall/rail conclusion flip claim without paired boundary plan | none-yet | P1-003 wall meter; F11 | hardware | fully | Registry indexes C5-2.10 as the C5 elaboration of promoted Q6. |
| RQ-METHOD-FLOOR | Detection floor; noise floor; short-difference resolvability; phase/item identifiability flags; RQ-AXI-MODULE-ATTRIBUTION-NONCLAIM | methodology artifact | banked | L1 methodology | no below-floor effect language except `not resolvable`; no module-energy fraction or regression-slope attribution | none-yet | P2-015 | floor | analysis-plan-only | Methodology centerpiece and prerequisite for most comparative claims; the candidate module-attribution nonclaim attaches here at earliest NS instead of becoming a row ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| C5-1.11 | Dark silicon; rail utilization; ANE-dark finding | research question | candidate | L2 structural | no true silicon-energy fraction from modeled rails | none-yet | P2-009 rich telemetry; C5-1.8 runtime grid | software | analysis-plan-only | Measures modeled-rail utilization structure, not physical absolute rail truth. |
| C5-1.3 | CPU:GPU phase division; rail/DVFS phase signatures; prefill/decode power asymmetry | research question | candidate | L2 structural | no short-phase joules when windows are under-resolved | none-yet | 2M with P2-009 | floor | analysis-plan-only | Merges the banked CPU:GPU phase question with C5-1.3 telemetry framing. |
| RQ-KV-GROWTH | KV-growth decode drift; C5-2.12; RQ-AXI-ATTN-CONTEXT-SLOPE | research question | banked | L1/L2 chunked | no per-token joule claims; no attention-vs-FFN fraction from context slopes | none-yet | none | floor | analysis-plan-only | Candidate riders, earliest PF: bounded-window KV marginal slope and named-artifact attention/context slope; both retain chunked-window/floor discipline and stay attached rather than becoming independent rows ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| C5-1.5 | Cooldown recovery as thermal characterization; cooldown-recovery curves | research question | candidate | L1/L2 | no claim that power recovery proves thermal-state equality | none-yet | none | floor | analysis-plan-only | Turns cooldown tails and cap-hit rates into reportable methodology evidence. |
| C5-1.10 | Failure frontier | research question | candidate | L1/L2 descriptive | no silent discard of failures; no population claim from one memory class | none-yet | none | software | analysis-plan-only | Structured `unsupported`, fit, swap, throttle, and cap-hit outcomes become data. |
| C5-1.7 | Cold-start / keep-warm energy; reload-vs-resident scheduling | research question | banked | L2 after harness extension | no breakeven without load-window and resident-idle sampling | none-yet | none | software | analysis-plan-only | Review and bank both identify reload-vs-resident as the same question. |
| C5-1.9 | Energy-per-correct-answer vs difficulty; MoE-vs-dense controlled ladder | research question | banked | L2 after envelope and denominator guards | no intelligence-per-joule; no `difficulty causes energy` | AP-5 | P2-010a plus P2-010b plus later scored campaign | substrate | analysis-plan-only | Correctness remains quarantined annotation under the C-004/C-014 rules. |
| C5-2.5 | Speculative-decoding energy; C5-2.5b proposal-work rider; C5-2.5c break-even rider | research question | banked | L2 | no efficiency claim without output equivalence and accepted-token accounting | none-yet | none | software | analysis-plan-only | C5-2.5c is the primary PF Q4 rider, C5-2.5b its PF secondary, and C5-2.5d the mandatory PF contamination control; C5-2.5a remains a deferred NS bank rider. `C-023-OUTPUT-IDENTITY` binds all efficiency contrasts ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| RQ-POWER-MODE | Power-mode Pareto | research question | banked | L2 possible | no OS-mode conclusion until power mode is a first-class config field | none-yet | none | software | analysis-plan-only | Waits on config/environment capture for OS power modes. |
| RQ-INTELLIGENCE-PER-JOULE | General joules-per-solved-task; intelligence-per-joule | research question | killed | none | no general intelligence-per-joule ratio | none-yet | none | substrate | no | Killed/quarantined by C-003/C-004; controlled ladder is the surviving minimal form. |
| RQ-AUDITABLE-EVIDENCE | Can JouleWise produce auditable local-LLM energy evidence? | capability claim | answered-L1 | L0/L1 | no physical calibration claim from strict validation alone | none-yet | existing Mac/MLX/powermetrics bundles | software | no | Artifact contribution, not a research question. |
| RQ-QWEN25-SMOKE | Qwen2.5-1.5B smoke consumption | capability claim | answered-L1 | L1 | no comparative scaling claim from smoke result | none-yet | 2026-07-06 2I | software | no | Legit instrument observation for one named stack/workload. |
| RQ-QWEN35-SMOKE | Qwen3.5-122B-A10B smoke consumption | capability claim | answered-L1 | L1 | no comparative scaling claim from n=3 | none-yet | 2026-07-07 flagship addendum | software | no | Legit instrument observation for one named stack/workload. |
| RQ-TWO-MODEL-ACTIVE-NONCLAIM | Did the two observed models demonstrate active-parameter scaling? | capability claim | answered-L1 | L1 hypothesis only | no active-parameter scaling claim | none-yet | 122B addendum; capability map | floor | no | Negative guard: two points are consistent with a hypothesis but do not support scaling. |
| RQ-SHORT-PREFILL-RESOLVABILITY | Are short prefill phase joules resolvable?; RQ-AXI-MODULE-ATTRIBUTION-NONCLAIM | methodology artifact | answered-L1 | L1 `not resolvable` | no standalone short-prefill joule result; no relabeling request phases as module phases | none-yet | Phase 4 observation | floor | no | Existing cadence precedent owns the candidate module-attribution guard, earliest NS; no separate methodology row ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| RQ-MLX-KV-REPLAY | Same-machine MLX KV replay token identity and size prediction; C5-2.13 | capability claim | answered-L1 | L1 feasibility | no cross-machine portability claim | none-yet | Stage 3.0.1 | software | no | The L1 feasibility result remains answered; candidate C5-2.13, earliest PF and capped at L2, attaches the same-machine energy-crossover rider without cross-stack generalization ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| RQ-MAC-BASELINES | Per-profile Mac baselines | capability claim | candidate | L1 per condition | no novelty or comparison claim without AP/floor | none-yet | 2M | floor | analysis-plan-only | Necessary baseline corpus, not a headline by itself. |
| RQ-SHAPE-ENERGY | Workload shape changes request energy | research question | candidate | L2 | no causal token-shape claim beyond AP-2 contrasts | AP-2 | 2M | floor | analysis-plan-only | Distinct from Q4 because it describes shape contrasts rather than holdout prediction. |
| C5-1.1 | Active-parameter energy scaling | research question | candidate | L2 pairwise only unless larger predeclared model set | no active+total+KV regression on 4-6 models | none-yet | P2-024 shortlist | floor | analysis-plan-only | C-014 caps the tempting wording; registry hygiene, not re-adjudication. |
| C5-1.2 | Context-length energy scaling; C5-2.12; RQ-AXI-ATTN-CONTEXT-SLOPE | research question | candidate | L2/L3 if modeled | no short-prompt phase point claims; no wall implication from SoC rails | none-yet | none | floor | analysis-plan-only | Natural local-inference question with chunked phase limits; the two candidate PF riders remain capped at L2 and forbid module attribution from context-associated slopes ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| C5-1.4 | DVFS residency as throttling early-warning | research question | candidate | L2 if prediction rule fixed | no prediction claim without horizon and rule | none-yet | none | software | analysis-plan-only | Convert characterization to a predeclared warning rule before claiming prediction. |
| C5-1.6 | Sampling-strategy energy overhead | research question | candidate | L2 if above floor | no telemetry-perturbation claim from this row | none-yet | P2-024 shortlist | floor | analysis-plan-only | Bank row is greedy vs temperature/top-p/beam overhead, not sampler instrumentation cost. |
| C5-1.8 | Runtime energy attribution; same-silicon kernel-layer provenance rider | research question | candidate | L2 stack-vs-stack | no `belongs to runtime` or `belongs to kernel layer` language when artifacts/formats differ; no runtime-agnostic kernel claim | none-yet | P2-024 shortlist | floor | analysis-plan-only | Candidate NV provenance rider stays inside the stack-conditioned comparison; it does not mint C5-1.13 ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| C5-1.12 | Quantization benefit decomposition, Mac leg | research question | candidate | L2 | no quantization efficiency claim without output divergence reporting | none-yet | P2-024 shortlist | floor | analysis-plan-only | Splits benefit into lower watts vs shorter time on one stack/family. |
| C5-W.1 | Category beyond token counts; Token-Shape Sufficiency Null | research question | candidate | L2 | no category effect below floor or without shape control | AP-4 | jw_mixed_v1 after P2-010a | substrate | analysis-plan-only | Strong null-or-effect design for workload-category residuals. |
| C5-W.2 | Thinking-token inflation | research question | candidate | L2 | no cognition claim; attribute only to emitted-token/stop distributions | none-yet | jw_mixed_v1 natural-EOS pilot | substrate | analysis-plan-only | Operational-cost view for reasoning models under natural EOS. |
| C5-W.3 | Category energy-ranking stability; workload-axis Q5 analogue | research question | candidate | L2 | no category ranking claim where rank gap is below MDE or without workload-expansion gate | none-yet | jw_mixed_v1 workload expansion | substrate | analysis-plan-only | Workload-axis analogue of promoted Q5, not the same ratified question; asks whether code/long-context/reasoning categories flip model/quant ordering. |
| C5-I.3 | C5-W.4; FLORES tokenizer fertility tax | research question | candidate | L2 | no tokenizer efficiency ranking without semantic and token-matched legs | none-yet | FLORES after HumanEval smoke | substrate | fully | C5-I.3 and C5-W.4 are the same FLORES fertility question. |
| C5-I.1 | External benchmark energy signatures | research question | candidate | L2 | no benchmark capability or accuracy claim | none-yet | import/export contracts | substrate | fully | Needs matched shape/output policy before family-level energy signatures. |
| C5-I.2 | Published-difficulty strata vs energy | research question | candidate | L1 association; L2 only if preplanned repeated bundles | no `difficulty causes energy` | none-yet | import/export contracts | substrate | fully | Weak/secondary because source difficulty labels are heterogeneous. |
| C5-I.4 | Harness overhead floor | methodology artifact | candidate | L1/L2 | no item energy claim when harness overhead dominates unnoticed | none-yet | P2-022 shim | substrate | fully | Methodology question for marked external harnesses. |
| C5-I.5 | Prompt-template energy sensitivity | research question | candidate | L2 | no prompt-quality or capability claim | none-yet | import/export contracts | substrate | fully | Same external item, canonical vs JouleWise-rendered prompt format. |
| RQ-CONTENT-SENTINEL | Synthetic prompt content sentinel; fixed-shape content sensitivity | research question | candidate | L2 | no content-effect claim unless realized shape/stop policy stays matched and effect clears floor; no broad content-neutrality claim beyond the five tested AP-6 conditions | AP-6 | P2-020 content sentinel | substrate | analysis-plan-only | Tests whether synthetic prompt content matters at fixed shape under the AP-6 ids-native no-BOS sentinel design. |
| RQ-ENERGY-VARIANCE | Sampling-induced energy variance; energy-at-risk per prompt; lucky-short-reasoning variance | research question | candidate | L2 within boundary | no intelligence-per-joule or correctness-causal claim (C-004 quarantine); variance claims need repeated-bundle n sized for variance estimation and floor-gated residuals; per-bundle sampler seeds must be recorded | none-yet | none (post-floor; reasoning model on current Mac feasible) | floor | analysis-plan-only | Ed-added 2026-07-09 row: distribution (not just mean) of request energy for a fixed hard prompt under sampling; decomposable into reasoning-length vs residual variance via recorded output token IDs + deterministic replay of sampled paths (P2-025 capture + 3.0.1 replay make paths replayable). |
| RQ-SESSION-SHAPE | Session-shape energy | research question | candidate | L2/L3 depending holdout | no app-session prediction without holdout validation | none-yet | suite profiles after P2-010a | substrate | analysis-plan-only | Tests whether Q4 coefficients compose in realistic session ecology. |
| RQ-ORDER-POSITION | Order-position effects | methodology artifact | candidate | L2 | no category/thermal inference without executable order policy | none-yet | suite profiles after ordering executability | substrate | analysis-plan-only | Drift/order probe; not a headline result. |
| RQ-CACHE-PREFIX | Cache/prefix economics; C5-2.13 | research question | candidate | L2 | no bundled cache-state conclusion without exact cache policy; no crossover generalization beyond the measured prompt-length ladder | none-yet | none | software | analysis-plan-only | Covers prefix reuse, resident state, and prompt-cache warmth; candidate C5-2.13 attaches a same-machine/same-stack energy crossover at earliest PF ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| RQ-AXI-HYBRID-PAIR | Named hybrid (SSM/attention)-vs-pure-transformer pair | research question | candidate | L2 pair-specific characterization | no architecture-class efficiency generalization, causal SSM-mechanism attribution, or tokenizer-blind ranking from one named pair | none-yet | post-floors named-pair campaign | floor | analysis-plan-only | Earliest PF; floor-gated and bindingly worded as “this named pair”; controlled-pair availability remains NEEDS-WEB ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| RQ-EXTERNAL-MARKED-RUNNER | External marked-runner energy layer | capability claim | candidate | L1/L2 with AP row | no accuracy, leaderboard, pass@k, or capability interpretation | none-yet | P2-022 | substrate | fully | Export-layer feasibility becomes research only when overhead/energy comparisons are specified. |
| RQ-HUMANEVAL-IMPORT-SMOKE | HumanEval import smoke | capability claim | candidate | L0/L1 | no coding-capability, pass@k, or accuracy claim | none-yet | P2-023 | substrate | no | Plumbing smoke for frozen external subset provenance. |
| C5-2.1 | Quantization decomposition, cross-stack | research question | candidate | L2 | no cross-boundary quant winner without calibration | none-yet | P1-006 CUDA/3050 manifests | hardware | fully | Extends C5-1.12 to CUDA/GGUF legs. |
| C5-2.2 | Batch size and prefill/decode energy split | research question | candidate | L2 | no serving conclusion without latency-bound policy | none-yet | P1-006 CUDA/3050 manifests | hardware | fully | Strong systems question for serving-style hardware and batching backend. |
| C5-2.3 | Predicted-vs-measured KV economics | research question | candidate | L2 | no KV economics claim without measured payload/link/deserialization terms | none-yet | P1-004 plus P1-006 | hardware | fully | One of the strongest Phase 3 questions; useful even if live split fails. |
| C5-2.4 | KV-cache quantization end-to-end; C5-2.11 on-device MLX leg | research question | candidate | L2 | no byte-saving equals energy-saving claim | none-yet | none | software | analysis-plan-only | Transfer leg still depends on cache portability; candidate C5-2.11 is the PF on-device MLX-scoped leg and also binds output-equivalence evidence ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| C5-2.11 | On-device quantized-KV energy | research question | candidate | L2, per-boundary, MLX-scoped | no byte-saving-equals-energy-saving claim; no cross-runtime generalization from MLX alone; no quality-neutrality claim without C-023-style output-equivalence evidence | none-yet | post-floors Mac cache-policy campaign | floor | analysis-plan-only | Earliest PF; indexed under C5-2.4/C5-1.12/C-023-QUALITY-EQUIV-QUANT and runnable without the transfer leg ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| C5-2.6 | Request coalescing under latency bound | research question | candidate | L2 | no scheduler optimum without arrival trace and latency policy | none-yet | none | hardware | analysis-plan-only | Useful but drifts toward scheduler research. |
| C5-2.7 | Device perf/W rankings with runtime held constant; kernel-provenance rider | research question | candidate | L2 within boundary; L4 with second unit/calibration | no generic hardware or cross-vendor kernel-API ranking from heterogeneous boundaries | none-yet | P1-006; 3080 Ti borrow window | hardware | fully | Candidate NV rider records attention-kernel/BLAS/graph provenance and remains per-boundary at L2; NEEDS-WEB feasibility stays open ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| C5-2.8 | Placement-policy optimality from Q4 coefficients | research question | candidate | L2/L3 | no optimal-placement claim without measured split validation cells | none-yet | Phase 3 full set | hardware | fully | Uses Q4 coefficients plus measured transfer costs to choose placement. |
| C5-2.9 | Local-vs-datacenter crossover economics | research question | candidate | scenario result only | no measured-equivalent cloud comparison | none-yet | P1-003 plus P1-004 | hardware | analysis-plan-only | Surviving scenario form of the carbon-label kill. |
| C5-3.1 | Machine-to-machine variance; generalizability floor | research question | candidate | L4 enabler | no population claim from one unit | none-yet | second M-series unit | hardware | fully | Cheapest route from stack-specific to replication-aware claims. |
| C5-3.2 | Battery-path energy and modeled-rail validation | research question | candidate | L2/L4 bridge | no full-system claim from modeled rails alone | none-yet | USB-C PD analyzer | hardware | fully | Complements AC wall meter with a second physical boundary. |
| C5-3.3 | Cross-ISA NPU/SoC comparison; backend-provenance rider | research question | candidate | L4 only after replication | no broad cross-ISA claim before platform-specific adapter study; no NVIDIA-vs-AMD efficiency claim from single units or heterogeneous boundaries | none-yet | new platform adapters | hardware | analysis-plan-only | Candidate PC provenance rider is capped at L1 and records backend identity now; it creates no AMD science commitment ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| C5-3.4 | Phone-class edge inference | capability claim | candidate | L0/L1 first | no promised phone science before telemetry feasibility | none-yet | phone feasibility | hardware | no | Feasibility verdict may be the result. |
| C5-3.5 | Cross-lab replication | methodology artifact | candidate | L4 enabler | no public benchmark credibility claim without replication | none-yet | external lab coordination | coordination | fully | Coordination-gated credibility layer. |
| C-023-TELEMETRY-PERTURBATION | Telemetry perturbation cost | methodology artifact | candidate (C-023) | L1/L2 floor component | no near-floor claim without telemetry-on/off ABBA check | none-yet | P2-015 component | floor | analysis-plan-only | New coverage-gap row; distinct from C5-1.6 sampling-strategy overhead. |
| C-023-VERSION-DRIFT | OS/runtime version-drift forensics; OS/driver/runtime update forensics | research question | candidate (C-023) | L1/L2 stack-conditioned | no version regression claim without before/after pinned bundles | none-yet | none | software | analysis-plan-only | Turns version churn into a named science/application row. |
| C-023-MARKER-JITTER | Marker/window jitter sensitivity; sampler-phase jitter sensitivity | methodology artifact | candidate (C-023) | L1 methodology; blocker for phase/item claims | no phase/item joule claim without jitter/sampler-phase sensitivity bound | none-yet | P2-015 or claim gate | floor | analysis-plan-only | Quantifies reducer sensitivity to timestamp jitter and sampler phase offset. |
| C-023-OUTPUT-IDENTITY | Output-token identity effects; binding gate for C5-2.5a/b/c/d | methodology artifact | candidate (C-023) | L1/L2 depending comparison | no quant/runtime/spec-decoding efficiency claim without equivalence or divergence report | none-yet | none | software | analysis-plan-only | Fixed output-token count is not fixed decoded work; binding for the PF/NS speculative-decoding riders admitted by D-075 ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| C-023-IDLE-STATIONARITY | Idle-baseline stationarity | methodology artifact | candidate (C-023) | L1 methodology | no idle-subtracted conclusion without idle model-choice sensitivity | none-yet | P2-015 component | floor | analysis-plan-only | D-067 CLOSED the headline-basis question: gross energy within the named boundary is primary. This row stays alive only to test how idle-model choice affects conclusions in the labeled within-device SECONDARY view. |
| C-023-QUALITY-EQUIV-QUANT | Quality-equivalent quantization comparisons; C5-2.11 gate | research question | candidate (C-023) | L2 after equivalence rule | no quantization efficiency or quality-neutrality claim without AP-level equivalence rule | none-yet | none | software | analysis-plan-only | C5-2.11's candidate PF on-device KV leg binds this gate; footprint savings alone do not establish energy or quality neutrality ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| C-023-COEFF-TRANSPORT | Coefficient transport synthetic-to-realistic; energy model portability across workload mixtures | research question | candidate (C-023) | L2/L3 depending holdout | no realistic-session prediction from synthetic grid without transport validation | none-yet | suite traces after Q4 | substrate | analysis-plan-only | Explicitly tests Q4 coefficient transport from synthetic grids to realistic app traces. |
| APP-PROMPT-PROFILER | Prompt/template energy profiler | application idea | candidate | internal L1/L2 only | no prompt-quality claim | none-yet | none | software | analysis-plan-only | Product-facing use of prompt/template energy sensitivity. |
| APP-BUNDLE-POWER-BUG | Attach-a-bundle power-bug repro | application idea | candidate | L0/L1 support workflow | no general bug diagnosis without reproduced bundle | none-yet | none | software | analysis-plan-only | Uses bundle completeness as a maintainer repro artifact. |
| APP-CI-ENERGY-GATES | CI energy-regression gates | application idea | candidate | internal L1/L2 after floors | no CI failure threshold below detection floor | none-yet | P2-015 prerequisite | floor | analysis-plan-only | Needs floors, env snapshots, and baseline-refresh policy. |
| APP-VENDOR-PRESS-AUDIT | Vendor/press claim audit | application idea | candidate | boundary-named L1/L2 | no absolute device-energy verdict without calibration | none-yet | none | hardware | analysis-plan-only | Can audit specific boundary/workload claims, not universal efficiency. |
| APP-MODEL-CARDS | Practitioner energy model cards / leaderboard | application idea | candidate | internal only until L4 replication | no public leaderboard before cross-lab replication | none-yet | C5-3.5 prerequisite | coordination | analysis-plan-only | Internal table can exist; public version is killed until replication. |
| APP-TEACHING-INSTRUMENT | Teaching instrument | application idea | candidate | pedagogical L0/L1 | no research generalization from teaching bundles | none-yet | none | software | analysis-plan-only | Uses bundles for methodology labs on boundaries, floors, and uncertainty. |
| APP-STANDARDS-CONTRIBUTION | Bundle contract as standards contribution | application idea | candidate | methodology artifact proposal | no claim to be the standard | none-yet | none | coordination | analysis-plan-only | Exports the artifact format and validation discipline. |
| APP-CARBON-LABELS | Carbon labels | application idea | killed | none | no carbon label without wall meter and grid assumptions | none-yet | none | hardware | no | Killed as product label; C5-2.9 is the surviving scenario question. |
| APP-BATTERY-RUNTIME | Battery-runtime estimates without calibration | application idea | killed | none | no battery-runtime estimate without system-level calibration | none-yet | none | hardware | no | Explicitly deferred/killed by the application shortlist. |
| APP-LOCAL-CLOUD-ROUTING | Local-vs-cloud routing product | application idea | killed | none | no routing product while cloud side is unmeasured | none-yet | none | hardware | no | Killed product form; scenario analysis remains C5-2.9. |

## Attribution Limits

The rows whose historical wording most invited over-attribution are:

- `C5-1.1`: active-parameter energy scaling. The C-014 amendment caps
  4-6-model designs at descriptive L2 pairwise contrasts unless the model set
  grows enough for a predeclared one-covariate fit, and forbids fitting
  active+total+KV covariates on 4-6 model points. The claims ladder also
  prevents L1 active-parameter-scaling language; the capability map records
  the current two-model observation as a non-claim.
- `C5-1.8`: runtime energy attribution. The bank already says comparisons
  where formats force different artifacts are stack-vs-stack comparisons.
  The registry therefore forbids wording that energy "belongs to the runtime"
  unless the artifact/runtime identity problem is actually controlled.

This subsection is hygiene for claims indexing. It does not re-adjudicate the
ratified C-014/C-015 bank decisions.

 succeeded in 0ms:
```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "The strongest feasibility-weighted path is a clean C/D metrology campaign, external wall validation, and an evaluation-ready artifact before adding one hypothesis-driven expansion.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": "665fd5821f74e579071fba9ddd9717b77ded6a01",
    "head_end": "665fd5821f74e579071fba9ddd9717b77ded6a01",
    "upstream_end": "665fd5821f74e579071fba9ddd9717b77ded6a01",
    "branch": "main"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "title": "The paper's claim-bearing experimental spine is not yet complete",
        "detail": "D-110 still withholds the floor and contrast artifacts pending issuance/remint, while D-113 requires fresh Window C collection, prospectively split into D if needed."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "title": "D-041 is not the mechanism-level fence",
        "detail": "D-041 governs external-benchmark import/export and limits the export shim to an energy layer; AXI mechanism studies are governed primarily by D-070, D-075, their analysis plans, and runtime feasibility verdicts."
      },
      {
        "id": "F3",
        "severity": "should_fix",
        "title": "Venue and calendar ambition remain unbound",
        "detail": "The report deadline, colloquium, 3080 Ti window, and venue-specific evidence-by dates remain TBD, preventing rational allocation of measurement nights."
      },
      {
        "id": "F4",
        "severity": "nit",
        "title": "The requested methods draft is not on main",
        "detail": "docs/paper/draft-v1.md exists on impl/paper-draft-v1 but is absent from main; the branch version was inspected for this review."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git status --short --branch && git rev-parse HEAD && git rev-parse --abbrev-ref HEAD && git rev-parse --abbrev-ref --symbolic-full-name '@{upstream}' 2>/dev/null || true",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "665fd5821f74e579071fba9ddd9717b77ded6a01",
          "main",
          "origin/main"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "665fd5821f74e579071fba9ddd9717b77ded6a01\\nmain\\norigin/main"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "test ! -e docs/paper/draft-v1.md && git cat-file -e impl/paper-draft-v1:docs/paper/draft-v1.md && printf 'draft_main=absent\\ndraft_branch=present\\n'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "draft_main=absent",
          "draft_branch=present"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "draft_main=absent\\ndraft_branch=present"
      }
    }
  ],
  "flags": [
    {
      "id": "FL1",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "The prompt identifies docs/paper/draft-v1.md as current, but it is present only on the impl/paper-draft-v1 branch.",
      "needs": "Lead should integrate or otherwise disposition the paper-draft branch."
    },
    {
      "id": "FL2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "No test suite was run because this was a read-only strategic synthesis with no repository modifications.",
      "needs": ""
    }
  ]
}
```

## Findings

### F1 — Finish the claim-bearing metrology spine before expanding

The instrument and its evidence machinery are unusually mature, but the paper still lacks a complete claim-bearing characterization result. The 1.5B/7B contrast passed collection gates and is a compelling preliminary demonstration, yet D-110 prevents formal use until the issuance/remint chain completes. D-113 then requires fresh Window C collection—split into D if necessary—without importing any retired Window B member. See [D-113](/Users/edr/code/JouleWise/docs/decision_log.md:7240) and the [current paper outline](/Users/edr/code/JouleWise/docs/run_reports/2026-07-30-paper-outline-v1.md:1).

That is the critical path. A broad paper with incomplete C1–C6 evidence will look less serious than a narrower paper that cleanly demonstrates linearity, null response, empirical floor behavior, additivity, drift/settling, and between-session stability.

D-113’s rigor-first posture forbids:

- Salvaging failed A/B data into replacement claim cells.
- Excluding an inconvenient member after seeing results.
- Compressing an oversized campaign into one night.
- Weakening calibration, whole-window, clock, or custody gates for schedule reasons.
- Adding process or repetitions without a named validity threat or material claim benefit.

It explicitly permits—and often prefers—smaller independent windows, narrower claims, and cutting an expansion.

### F2 — Exact D-041 ruling and the real mechanism fence

D-041 is titled “Benchmark interop — frozen-subset imports + marker-shim energy layer.” It fences:

- External benchmark imports to hash-frozen subsets with identity, licensing, and contamination records.
- Export to a marker-emitting shim where the external harness owns prompts, generation semantics, and accuracy; JouleWise owns capture, bundle assembly, marker validation, and energy reduction.
- Joined reporting to observed energy beside the external metric artifact—never JouleWise accuracy, pass@k-per-joule, leaderboard standing, or intelligence-per-joule.
- Implementation to after 2M and P2-010a, unless D-034 is explicitly reopened.
- Interop expansion to be cut before core Mac characterization under schedule pressure.

Thus, “unfencing D-041” would require completing 2M and P2-010a—or an explicit decision reopening D-034/D-041 sequencing—then passing P2-022’s marker feasibility spike and writing an analysis-plan row before any L2 claim. It still would not authorize mechanism attribution.

The KDA/speculative-decode/MTP/MoE program is instead governed by D-070/D-075 and the AXI contracts:

- Post-core/floor sequencing.
- L2 ceiling for named studies unless Q4’s independent L3 machinery applies.
- Direct observability rather than inference from configuration.
- Output/quality-equivalence controls.
- Named forbidden generalizations.

The current feasibility facts matter:

- External-draft speculative generation exists, but pinned `mlx-lm` lacks actual proposal counts and decode-step emission boundaries.
- Native MTP is unsupported: the pinned runtime does not execute the heads.
- KDA/hybrid comparisons currently involve cross-model confounding and unverified long-context execution.
- MoE mechanism language requires auditable routing evidence; otherwise the claim must remain a named-model energy comparison, not routing attribution.
- No tracked repository document uses “KDA” as a governed project axis; it appears in the nonbinding mechanism-literature sweep, not D-041.

### Ranked roadmap

Planning estimates below assume the current 2–4-hour claim-window protocol, at least 20% failure margin, and physical Ed preparation through §5A.

| Rank | Expansion | Why it impresses reviewers | Estimated effort and Ed-present sessions | Dependencies and principal risk | Decision required |
|---:|---|---|---|---|---|
| **1** | **Complete C1–C7 cleanly: remint, fresh C/D, and stability** | Converts the strongest idea—the instrument and its refusal behavior—into actual evidence. This is the difference between an elaborate methodology and a metrology paper. | **3–6 weeks after desk gates; 2 mandatory nights plus 1 contingency/short stability session.** | D-079 issued artifact; D-110 remint; reviewed frozen-plan record; fresh §5A; C/D split if scope cannot fit. Risk: another environmental or clock refusal. | Reserve the core nights now and prohibit breadth work from consuming them. |
| **2** | **External wall-meter validation of totals, C8** | Directly addresses the obvious reviewer question: “Does `powermetrics` agree with physical input power?” It materially upgrades absolute-scale credibility. | **4–8 weeks; 1 pilot plus 1 confirmatory session.** The confirmatory run may share a later frozen campaign only after the importer and protocol pass independently. | Professional AC analyzer, safe inline fixture, synchronized export, fixed ranges, load-specific uncertainty, battery charge neutralization, held-out regression. It validates totals only—not phase allocation. | D-092 already decided “yes”; Ed/advisor must now authorize purchase/loan, budget, and an evidence-by date. |
| **3** | **Artifact-evaluation-quality release** | Hash-bound raw-to-figure reproducibility is a genuine differentiator and unusually well aligned with JouleWise’s thesis. Reviewers can verify refusals and re-derive results rather than trust screenshots. | **4–6 weeks; 0 measurement nights.** | Sanitized raw-bundle subset, one-command validation/reduction/figure path, locked environment, quick/full tracks, immutable archive/DOI, clear hardware-free replay. Risk: privacy, dataset size, and Mac-only collection requirements. | Decide whether the target is merely open source or formal ICPE-style artifact evaluation, and which evidence may be public. |
| **4** | **Designed workload-shape matrix with held-out prediction—Q4/L3** | A predictive fixed-plus-marginal model validated on held-out cells is substantially more serious than “we ran more prompts.” It can earn L3 rather than another collection of L1/L2 points. | **6–10 weeks; approximately 2–3 nights.** | P2-006 baseline sizing, AP-1, 4×3 grid, predeclared holdouts, residual/sensitivity analysis, floor audit. Risk: the simple model may fail its holdouts—which must be reported honestly. | Fund the full designed matrix or omit the predictive claim; do not replace it with opportunistic workload breadth. |
| **5** | **Quality-gated BF16/Q8/Q4 quantization ladder** | A clean same-family ladder with error bars and output-divergence reporting can adjudicate the reported q4-vs-q8 anomaly. Strong workshop demonstration; moderate novelty. | **4–8 weeks; 1–2 nights.** Quality screening can run outside quiet windows. | One frozen source revision, reproducible conversions, 256-item quality gate, 32-item energy subset, stack-specific floors. Risk: quality may not be equivalent or quantization may alter cadence beyond existing calibration support. | Choose the model family before conversion; accept a quality/energy trade-off result if equivalence fails. |
| **6** | **Second-unit replication after multi-day same-unit stability** | This is the clearest path beyond single-machine claims and toward L4. It demonstrates that the artifact and calibration method transfer, not merely that one laptop is stable. | **4–8 weeks once access exists; 2 sessions on the second unit, 0–2 Ed-present depending on operator.** | A second comparable Apple unit, frozen stack or explicitly modeled version difference, independent calibration and artifact execution. Risk: OS/hardware drift may make it replication-aware rather than directly pooled. | Secure a second unit/collaborator or explicitly retain the single-unit ceiling. |
| **7** | **One mechanism-level study, conditional on a hard feasibility gate** | **Highest scientific ceiling.** A controlled batch-1 speculative-decode or MTP energy result could be genuinely novel; KDA/context slope or MoE routing is also interesting if attribution is identifiable. | **2–3-week desk feasibility gate; if passed, another 6–12 weeks and roughly 2 nights.** | New/forked runtime instrumentation, direct proposal/acceptance events, output identity/equivalence, mechanism-specific AP and floors. MTP currently cannot execute; KDA is confounded; MoE routing visibility is uncertain. | Pick exactly one mechanism and a kill date. Recommended first choice: external-draft speculative decode, because it offers the cleanest same-target on/off contrast if observability can be added. |
| **8** | **Split inference: synthetic transfer plus one offline split pairing** | Demonstrates the instrument under two boundaries, a transfer interval, and cross-device clocks. A complete per-stage bundle is impressive even without a crossover. | **2–4 months; roughly 3–5 two-device measurement sessions.** Live split adds more and should remain stretch. | Schema v0.2, remaining replay verdicts, two-node telemetry, clock bounds, transfer bench, 3080 Ti window, two links, wall/host boundary or lower-bound wording. Risk is high and the engineering can dominate the paper. | Commit only to synthetic transfer plus offline replay; authorize live split separately after offline results. |
| **9** | **Additional model families, generic workloads, Jetsons** | Useful corroboration, but mostly incremental unless each addition tests a predeclared hypothesis or provides independent replication. More rows do not overcome the single-unit or boundary limitations. | **3–8 weeks and 1–2 nights per coherent axis/device.** | New model lineage, adapter, quality and floor cells; Jetson remains optional and remote pins are provisional. | Add only a model or device that changes the claim—not merely the size of a results table. |

For the wall-meter path, the right class is a calibrated bench AC power analyzer, not an inexpensive consumer plug. A concrete baseline is the Yokogawa WT310E: its manufacturer lists 10 readings/s, USB export, 0.1%-of-reading plus 0.05%-of-range basic accuracy, high crest-factor capability, and a **$2,935 base US price** before calibration/fixture costs. Actual suitability still depends on calculating uncertainty at the Mac’s observed load and using a safe inline fixture. Borrowing an in-calibration unit from an engineering lab is preferable to spending several thousand dollars. [Yokogawa WT310E specifications and current price](https://tmi.yokogawa.com/us/solutions/products/power-analyzers/digital-power-meter-wt300e/).

### Venue ambition

| Tier | What the current/expanded project can support | What should be present |
|---|---|---|
| **CSCSU** | After remint and clean C/D, this should be a strong undergraduate-conference submission. The latest published rules allow technical papers and extensive experimentation, with **5 pages including references**. [CSCSU 2026 guidance](https://cscsu-conference.github.io/) | C1–C6 core, one demonstration, crisp limitations, compact artifact pointer. Wall validation and split are not necessary. |
| **EuroMLSys/HotCarbon workshop** | The natural near-term research target. EuroMLSys’s latest call uses 6 pages excluding references; HotCarbon uses 5 pages excluding references and no appendix. [EuroMLSys](https://euromlsys.eu/), [HotCarbon CFP](https://hotcarbon.org/cfp) | Clean metrology core, model contrast, wall validation if available, and polished artifact. EuroMLSys is the better technical-method fit; HotCarbon needs a stronger sustainability-metrics argument. |
| **ICPE Emerging/WIP** | Appropriate if the core is strong but external validation, replication, or the broader predictive evaluation remains incomplete. The 2026 track used a 6-page format. [ICPE Emerging Research](https://icpe2026.spec.org/tracks-and-submissions/emerging-research-track/) | Validated core, transparent open gaps, early artifact, and a credible expansion plan. |
| **ICPE full research track** | Plausible over months, but not yet supported by the current evidence. ICPE 2027 lists research and artifact tracks but their details and dates remain TBA. The 2026 research track used 10 pages and judged novelty, technical quality, and scientific soundness; 2026’s reported full-paper acceptance rate was 28%. [ICPE 2027](https://icpe2027.spec.org/tracks-and-submissions/research-paper-track/), [2026 research criteria](https://icpe2026.spec.org/tracks-and-submissions/research-paper-track/), [acceptance history](https://icpe.spec.org/past-conferences/) | C1–C8, cross-day stability, artifact-ready release, and at least one deeper contribution: held-out Q4 prediction, second-unit replication, or a successful mechanism study. Split is not required. |

ICPE’s artifact track is especially aligned: it asks for documented, consistent, complete, exercisable artifacts, permanent archival availability, and practical setup/reproduction instructions. [ICPE artifact-evaluation criteria](https://icpe2026.spec.org/tracks-and-submissions/artifact-evaluation-track/).

### Critical path to the strongest defensible version

1. **Now:** finish D-079 issuance and the D-110 remint chain; integrate or disposition the draft branch; set actual calendar and venue evidence-by dates.
2. **In parallel:** borrow/order the wall analyzer and build its importer, synchronization, and held-out validation protocol without assuming it will arrive in time.
3. **First hardware block:** freeze and collect Window C, then D if the complete replacement cannot fit with the required margin. Add a third short day/session only if needed for the stated stability claim.
4. **Immediately after each passing window:** produce the governed artifacts, deterministic figures, claim-index entries, and experimental prose. Do not wait for all expansions before writing.
5. **Artifact block:** publish a sanitized, hash-bound raw-to-figure package with a fast hardware-free reproduction path and archival DOI.
6. **Second hardware block:** run external wall validation.
7. **Choose one expansion:** Q4 held-out prediction for the strongest ICPE case; quantization for the safest workshop enhancement; or mechanism work only if its short feasibility gate passes.
8. **Only then consider split inference.** Start it only if the 3080 Ti window is dated and the transfer/offline-replay path is rehearsed before hardware access.
9. **Freeze the dataset early:** reserve at least six weeks before submission for figures, claims audit, paper compression, artifact dry runs, and advisor review.

The strongest realistic paper is therefore: **C1–C8 metrology + the already-collected 1.5B/7B demonstration + one designed extension + an independently usable artifact.** That is more coherent and defensible than a larger model/device matrix or an unfinished split system.

### F3 — Five decisions Ed/advisor must make

1. **Venue and publication sequence.** Choose CSCSU-only, workshop-first, or ICPE-full ambition, and verify whether a workshop publication may later be extended for ICPE. Build a 10-page master manuscript even if the first submission is shorter.

2. **Physical measurement budget.** Recommended commitment: **5–7 Ed-present sessions**—C, D, one contingency/stability repeat, wall pilot/confirmation, and one extension. An ICPE-full attempt with Q4 and second-unit work likely needs **8–10 total sessions** across operators.

3. **Meter execution.** D-092 has already answered “yes.” The remaining decision is: borrow versus buy, approximately $3,000-class budget, calibration/fixture responsibility, and a cutoff date after which C8 is cleanly removed.

4. **Mechanism ambition.** Do not ask simply “unfence D-041.” Decide whether to retain D-070’s all-five-axis commitment or narrow it to one paper-worthy study. Recommended rule: two-to-three-week feasibility gate for speculative-decode observability; if it fails, return immediately to Q4/quantization.

5. **External hardware priority.** Decide whether scarce coordination goes to a second Apple unit, the 3080 Ti split study, or Jetsons. Recommendation: second-unit replication first, 3080 Ti second, Jetsons last.

### F4 — Draft-state correction

The methods draft was inspected from `impl/paper-draft-v1` at commit `af0b7195`; it is one commit ahead of and one commit behind `main`. It already reflects the right rigor: result placeholders remain pending remint, all characterization rows are pending Window C, and the split section is framed as future demonstration work. It should be integrated deliberately so the paper itself becomes the continuously updated claim-state surface.

## Residual risk

- The mechanism-literature sweep is explicitly desk research, not governed project evidence. Any “first measured” novelty claim needs a fresh literature search immediately before submission.
- Venue formats and deadlines cited above are current published 2026 rules or incomplete 2027 pages; 2027 calls may change.
- Measurement-night estimates are planning ranges, not validated campaign runtimes.
- Wall validation cannot establish phase attribution, and one external meter does not create cross-device generality.
- Even an excellent single-Mac study remains stack-specific under the claims ladder unless second-unit or cross-lab replication lands.
exec
/bin/zsh -lc "sed -n '1,180p' docs/research_question_registry.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
# Research Question Registry

Purpose: this is the canonical live index for JouleWise research questions,
capability claims, application ideas, and methodology artifacts. It normalizes
aliases, status, claim ceilings, owners, gates, and pre-hardware readiness so
claims and campaign plans can point to one row. Promotion rules are unchanged
from `docs/research_question_bank.md`: promotion still requires a named RQ slot
in `PROJECT_STATUS.md`, a data plan that does not displace queue ranks above
it, and scope fit.

Maintenance rule: registry rows are LIVE state. The research question bank
remains the historical and deliberative record, including council wording,
kills, quarantines, and amendments. Single-writer split: update this registry
for current indexing and cross-references; update the bank only when recording
new deliberation history.

Column legend:

- `canonical_id`: stable row key for the live index.
- `aliases`: other IDs, names, or capability-map labels for the same question.
- `question_type`: one of `research question`, `capability claim`,
  `application idea`, or `methodology artifact`.
- `status`: `promoted`, `banked`, `candidate`, `killed`, `answered-L1`, or
  the review-specific `candidate (C-023)`.
- `claim_ceiling`: highest claim level currently allowed by the bank, review,
  or capability map, before future evidence upgrades.
- `forbidden_upgrade`: short reminder of language the row cannot support.
- `AP owner`: analysis-plan owner if already named; otherwise `none-yet`.
- `campaign owner`: queue row, phase, or campaign owner if already named.
- `gate_class`: dominant gate class: `hardware`, `software`, `floor`,
  `substrate`, or `coordination`.
- `pre_hardware_preparable`: `fully`, `analysis-plan-only`, or `no`.
- `one-line note`: indexing note, not a re-adjudication.

## Registry Table

| canonical_id | aliases | question_type | status | claim_ceiling | forbidden_upgrade | AP owner | campaign owner | gate_class | pre_hardware_preparable | one-line note |
|---|---|---|---|---|---|---|---|---|---|---|
| Q1 | Split reduces energy | research question | promoted | L2 boundary-labeled; stronger only with calibration | no uncalibrated cross-boundary total-energy winner | none-yet | Phase 3 split; P1-004; P1-006 | hardware | fully | Central split question; total energy must be decomposed and boundary-labeled. |
| Q2 | Link bandwidth sensitivity | research question | promoted | L2 | no nominal-link crossover without measured links | none-yet | Phase 3 split; P1-004 | hardware | fully | Clean interconnect sensitivity question; link throughput and transfer energy must be measured. |
| Q3 | Split energy-latency Pareto | research question | promoted | L2 | no Pareto claim without frozen set and latency metric | none-yet | Phase 3 split | hardware | fully | Requires a fixed comparison set and latency metric per figure. |
| Q4 | Fixed-vs-marginal energy model; C5-2.14 cache-policy coefficient rider | research question | promoted | L3 | no holdout-prediction claim without AP-1 floor and residual checks | AP-1 | P2-019 q4_l3_shape_grid_v1 | floor | analysis-plan-only | Strongest predictive science row; includes compositional split-energy prediction only when transfer terms exist. C5-2.14 is a candidate rider capped at L2, earliest PF, with no coefficient-direction claim below P2-015 floors ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| Q5 | Ranking stability | research question | promoted | L2 | no uncalibrated cross-device winner; no ranking where gap below MDE | AP-3 | 2M; Window B grid | floor | analysis-plan-only | Promoted within-machine ranking question; workload-axis analogue C5-W.3 remains a separate candidate row. |
| Q6 | Boundary sensitivity; C5-2.10 boundary-directional bias quantification | research question | promoted | L2; L4 only with replication | no wall/rail conclusion flip claim without paired boundary plan | none-yet | P1-003 wall meter; F11 | hardware | fully | Registry indexes C5-2.10 as the C5 elaboration of promoted Q6. |
| RQ-METHOD-FLOOR | Detection floor; noise floor; short-difference resolvability; phase/item identifiability flags; RQ-AXI-MODULE-ATTRIBUTION-NONCLAIM | methodology artifact | banked | L1 methodology | no below-floor effect language except `not resolvable`; no module-energy fraction or regression-slope attribution | none-yet | P2-015 | floor | analysis-plan-only | Methodology centerpiece and prerequisite for most comparative claims; the candidate module-attribution nonclaim attaches here at earliest NS instead of becoming a row ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| C5-1.11 | Dark silicon; rail utilization; ANE-dark finding | research question | candidate | L2 structural | no true silicon-energy fraction from modeled rails | none-yet | P2-009 rich telemetry; C5-1.8 runtime grid | software | analysis-plan-only | Measures modeled-rail utilization structure, not physical absolute rail truth. |
| C5-1.3 | CPU:GPU phase division; rail/DVFS phase signatures; prefill/decode power asymmetry | research question | candidate | L2 structural | no short-phase joules when windows are under-resolved | none-yet | 2M with P2-009 | floor | analysis-plan-only | Merges the banked CPU:GPU phase question with C5-1.3 telemetry framing. |
| RQ-KV-GROWTH | KV-growth decode drift; C5-2.12; RQ-AXI-ATTN-CONTEXT-SLOPE | research question | banked | L1/L2 chunked | no per-token joule claims; no attention-vs-FFN fraction from context slopes | none-yet | none | floor | analysis-plan-only | Candidate riders, earliest PF: bounded-window KV marginal slope and named-artifact attention/context slope; both retain chunked-window/floor discipline and stay attached rather than becoming independent rows ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| C5-1.5 | Cooldown recovery as thermal characterization; cooldown-recovery curves | research question | candidate | L1/L2 | no claim that power recovery proves thermal-state equality | none-yet | none | floor | analysis-plan-only | Turns cooldown tails and cap-hit rates into reportable methodology evidence. |
| C5-1.10 | Failure frontier | research question | candidate | L1/L2 descriptive | no silent discard of failures; no population claim from one memory class | none-yet | none | software | analysis-plan-only | Structured `unsupported`, fit, swap, throttle, and cap-hit outcomes become data. |
| C5-1.7 | Cold-start / keep-warm energy; reload-vs-resident scheduling | research question | banked | L2 after harness extension | no breakeven without load-window and resident-idle sampling | none-yet | none | software | analysis-plan-only | Review and bank both identify reload-vs-resident as the same question. |
| C5-1.9 | Energy-per-correct-answer vs difficulty; MoE-vs-dense controlled ladder | research question | banked | L2 after envelope and denominator guards | no intelligence-per-joule; no `difficulty causes energy` | AP-5 | P2-010a plus P2-010b plus later scored campaign | substrate | analysis-plan-only | Correctness remains quarantined annotation under the C-004/C-014 rules. |
| C5-2.5 | Speculative-decoding energy; C5-2.5b proposal-work rider; C5-2.5c break-even rider | research question | banked | L2 | no efficiency claim without output equivalence and accepted-token accounting | none-yet | none | software | analysis-plan-only | C5-2.5c is the primary PF Q4 rider, C5-2.5b its PF secondary, and C5-2.5d the mandatory PF contamination control; C5-2.5a remains a deferred NS bank rider. `C-023-OUTPUT-IDENTITY` binds all efficiency contrasts ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| RQ-POWER-MODE | Power-mode Pareto | research question | banked | L2 possible | no OS-mode conclusion until power mode is a first-class config field | none-yet | none | software | analysis-plan-only | Waits on config/environment capture for OS power modes. |
| RQ-INTELLIGENCE-PER-JOULE | General joules-per-solved-task; intelligence-per-joule | research question | killed | none | no general intelligence-per-joule ratio | none-yet | none | substrate | no | Killed/quarantined by C-003/C-004; controlled ladder is the surviving minimal form. |
| RQ-AUDITABLE-EVIDENCE | Can JouleWise produce auditable local-LLM energy evidence? | capability claim | answered-L1 | L0/L1 | no physical calibration claim from strict validation alone | none-yet | existing Mac/MLX/powermetrics bundles | software | no | Artifact contribution, not a research question. |
| RQ-QWEN25-SMOKE | Qwen2.5-1.5B smoke consumption | capability claim | answered-L1 | L1 | no comparative scaling claim from smoke result | none-yet | 2026-07-06 2I | software | no | Legit instrument observation for one named stack/workload. |
| RQ-QWEN35-SMOKE | Qwen3.5-122B-A10B smoke consumption | capability claim | answered-L1 | L1 | no comparative scaling claim from n=3 | none-yet | 2026-07-07 flagship addendum | software | no | Legit instrument observation for one named stack/workload. |
| RQ-TWO-MODEL-ACTIVE-NONCLAIM | Did the two observed models demonstrate active-parameter scaling? | capability claim | answered-L1 | L1 hypothesis only | no active-parameter scaling claim | none-yet | 122B addendum; capability map | floor | no | Negative guard: two points are consistent with a hypothesis but do not support scaling. |
| RQ-SHORT-PREFILL-RESOLVABILITY | Are short prefill phase joules resolvable?; RQ-AXI-MODULE-ATTRIBUTION-NONCLAIM | methodology artifact | answered-L1 | L1 `not resolvable` | no standalone short-prefill joule result; no relabeling request phases as module phases | none-yet | Phase 4 observation | floor | no | Existing cadence precedent owns the candidate module-attribution guard, earliest NS; no separate methodology row ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| RQ-MLX-KV-REPLAY | Same-machine MLX KV replay token identity and size prediction; C5-2.13 | capability claim | answered-L1 | L1 feasibility | no cross-machine portability claim | none-yet | Stage 3.0.1 | software | no | The L1 feasibility result remains answered; candidate C5-2.13, earliest PF and capped at L2, attaches the same-machine energy-crossover rider without cross-stack generalization ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| RQ-MAC-BASELINES | Per-profile Mac baselines | capability claim | candidate | L1 per condition | no novelty or comparison claim without AP/floor | none-yet | 2M | floor | analysis-plan-only | Necessary baseline corpus, not a headline by itself. |
| RQ-SHAPE-ENERGY | Workload shape changes request energy | research question | candidate | L2 | no causal token-shape claim beyond AP-2 contrasts | AP-2 | 2M | floor | analysis-plan-only | Distinct from Q4 because it describes shape contrasts rather than holdout prediction. |
| C5-1.1 | Active-parameter energy scaling | research question | candidate | L2 pairwise only unless larger predeclared model set | no active+total+KV regression on 4-6 models | none-yet | P2-024 shortlist | floor | analysis-plan-only | C-014 caps the tempting wording; registry hygiene, not re-adjudication. |
| C5-1.2 | Context-length energy scaling; C5-2.12; RQ-AXI-ATTN-CONTEXT-SLOPE | research question | candidate | L2/L3 if modeled | no short-prompt phase point claims; no wall implication from SoC rails | none-yet | none | floor | analysis-plan-only | Natural local-inference question with chunked phase limits; the two candidate PF riders remain capped at L2 and forbid module attribution from context-associated slopes ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| C5-1.4 | DVFS residency as throttling early-warning | research question | candidate | L2 if prediction rule fixed | no prediction claim without horizon and rule | none-yet | none | software | analysis-plan-only | Convert characterization to a predeclared warning rule before claiming prediction. |
| C5-1.6 | Sampling-strategy energy overhead | research question | candidate | L2 if above floor | no telemetry-perturbation claim from this row | none-yet | P2-024 shortlist | floor | analysis-plan-only | Bank row is greedy vs temperature/top-p/beam overhead, not sampler instrumentation cost. |
| C5-1.8 | Runtime energy attribution; same-silicon kernel-layer provenance rider | research question | candidate | L2 stack-vs-stack | no `belongs to runtime` or `belongs to kernel layer` language when artifacts/formats differ; no runtime-agnostic kernel claim | none-yet | P2-024 shortlist | floor | analysis-plan-only | Candidate NV provenance rider stays inside the stack-conditioned comparison; it does not mint C5-1.13 ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| C5-1.12 | Quantization benefit decomposition, Mac leg | research question | candidate | L2 | no quantization efficiency claim without output divergence reporting | none-yet | P2-024 shortlist | floor | analysis-plan-only | Splits benefit into lower watts vs shorter time on one stack/family. |
| C5-W.1 | Category beyond token counts; Token-Shape Sufficiency Null | research question | candidate | L2 | no category effect below floor or without shape control | AP-4 | jw_mixed_v1 after P2-010a | substrate | analysis-plan-only | Strong null-or-effect design for workload-category residuals. |
| C5-W.2 | Thinking-token inflation | research question | candidate | L2 | no cognition claim; attribute only to emitted-token/stop distributions | none-yet | jw_mixed_v1 natural-EOS pilot | substrate | analysis-plan-only | Operational-cost view for reasoning models under natural EOS. |
| C5-W.3 | Category energy-ranking stability; workload-axis Q5 analogue | research question | candidate | L2 | no category ranking claim where rank gap is below MDE or without workload-expansion gate | none-yet | jw_mixed_v1 workload expansion | substrate | analysis-plan-only | Workload-axis analogue of promoted Q5, not the same ratified question; asks whether code/long-context/reasoning categories flip model/quant ordering. |
| C5-I.3 | C5-W.4; FLORES tokenizer fertility tax | research question | candidate | L2 | no tokenizer efficiency ranking without semantic and token-matched legs | none-yet | FLORES after HumanEval smoke | substrate | fully | C5-I.3 and C5-W.4 are the same FLORES fertility question. |
| C5-I.1 | External benchmark energy signatures | research question | candidate | L2 | no benchmark capability or accuracy claim | none-yet | import/export contracts | substrate | fully | Needs matched shape/output policy before family-level energy signatures. |
| C5-I.2 | Published-difficulty strata vs energy | research question | candidate | L1 association; L2 only if preplanned repeated bundles | no `difficulty causes energy` | none-yet | import/export contracts | substrate | fully | Weak/secondary because source difficulty labels are heterogeneous. |
| C5-I.4 | Harness overhead floor | methodology artifact | candidate | L1/L2 | no item energy claim when harness overhead dominates unnoticed | none-yet | P2-022 shim | substrate | fully | Methodology question for marked external harnesses. |
| C5-I.5 | Prompt-template energy sensitivity | research question | candidate | L2 | no prompt-quality or capability claim | none-yet | import/export contracts | substrate | fully | Same external item, canonical vs JouleWise-rendered prompt format. |
| RQ-CONTENT-SENTINEL | Synthetic prompt content sentinel; fixed-shape content sensitivity | research question | candidate | L2 | no content-effect claim unless realized shape/stop policy stays matched and effect clears floor; no broad content-neutrality claim beyond the five tested AP-6 conditions | AP-6 | P2-020 content sentinel | substrate | analysis-plan-only | Tests whether synthetic prompt content matters at fixed shape under the AP-6 ids-native no-BOS sentinel design. |
| RQ-ENERGY-VARIANCE | Sampling-induced energy variance; energy-at-risk per prompt; lucky-short-reasoning variance | research question | candidate | L2 within boundary | no intelligence-per-joule or correctness-causal claim (C-004 quarantine); variance claims need repeated-bundle n sized for variance estimation and floor-gated residuals; per-bundle sampler seeds must be recorded | none-yet | none (post-floor; reasoning model on current Mac feasible) | floor | analysis-plan-only | Ed-added 2026-07-09 row: distribution (not just mean) of request energy for a fixed hard prompt under sampling; decomposable into reasoning-length vs residual variance via recorded output token IDs + deterministic replay of sampled paths (P2-025 capture + 3.0.1 replay make paths replayable). |
| RQ-SESSION-SHAPE | Session-shape energy | research question | candidate | L2/L3 depending holdout | no app-session prediction without holdout validation | none-yet | suite profiles after P2-010a | substrate | analysis-plan-only | Tests whether Q4 coefficients compose in realistic session ecology. |
| RQ-ORDER-POSITION | Order-position effects | methodology artifact | candidate | L2 | no category/thermal inference without executable order policy | none-yet | suite profiles after ordering executability | substrate | analysis-plan-only | Drift/order probe; not a headline result. |
| RQ-CACHE-PREFIX | Cache/prefix economics; C5-2.13 | research question | candidate | L2 | no bundled cache-state conclusion without exact cache policy; no crossover generalization beyond the measured prompt-length ladder | none-yet | none | software | analysis-plan-only | Covers prefix reuse, resident state, and prompt-cache warmth; candidate C5-2.13 attaches a same-machine/same-stack energy crossover at earliest PF ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| RQ-AXI-HYBRID-PAIR | Named hybrid (SSM/attention)-vs-pure-transformer pair | research question | candidate | L2 pair-specific characterization | no architecture-class efficiency generalization, causal SSM-mechanism attribution, or tokenizer-blind ranking from one named pair | none-yet | post-floors named-pair campaign | floor | analysis-plan-only | Earliest PF; floor-gated and bindingly worded as “this named pair”; controlled-pair availability remains NEEDS-WEB ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| RQ-EXTERNAL-MARKED-RUNNER | External marked-runner energy layer | capability claim | candidate | L1/L2 with AP row | no accuracy, leaderboard, pass@k, or capability interpretation | none-yet | P2-022 | substrate | fully | Export-layer feasibility becomes research only when overhead/energy comparisons are specified. |
| RQ-HUMANEVAL-IMPORT-SMOKE | HumanEval import smoke | capability claim | candidate | L0/L1 | no coding-capability, pass@k, or accuracy claim | none-yet | P2-023 | substrate | no | Plumbing smoke for frozen external subset provenance. |
| C5-2.1 | Quantization decomposition, cross-stack | research question | candidate | L2 | no cross-boundary quant winner without calibration | none-yet | P1-006 CUDA/3050 manifests | hardware | fully | Extends C5-1.12 to CUDA/GGUF legs. |
| C5-2.2 | Batch size and prefill/decode energy split | research question | candidate | L2 | no serving conclusion without latency-bound policy | none-yet | P1-006 CUDA/3050 manifests | hardware | fully | Strong systems question for serving-style hardware and batching backend. |
| C5-2.3 | Predicted-vs-measured KV economics | research question | candidate | L2 | no KV economics claim without measured payload/link/deserialization terms | none-yet | P1-004 plus P1-006 | hardware | fully | One of the strongest Phase 3 questions; useful even if live split fails. |
| C5-2.4 | KV-cache quantization end-to-end; C5-2.11 on-device MLX leg | research question | candidate | L2 | no byte-saving equals energy-saving claim | none-yet | none | software | analysis-plan-only | Transfer leg still depends on cache portability; candidate C5-2.11 is the PF on-device MLX-scoped leg and also binds output-equivalence evidence ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| C5-2.11 | On-device quantized-KV energy | research question | candidate | L2, per-boundary, MLX-scoped | no byte-saving-equals-energy-saving claim; no cross-runtime generalization from MLX alone; no quality-neutrality claim without C-023-style output-equivalence evidence | none-yet | post-floors Mac cache-policy campaign | floor | analysis-plan-only | Earliest PF; indexed under C5-2.4/C5-1.12/C-023-QUALITY-EQUIV-QUANT and runnable without the transfer leg ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| C5-2.6 | Request coalescing under latency bound | research question | candidate | L2 | no scheduler optimum without arrival trace and latency policy | none-yet | none | hardware | analysis-plan-only | Useful but drifts toward scheduler research. |
| C5-2.7 | Device perf/W rankings with runtime held constant; kernel-provenance rider | research question | candidate | L2 within boundary; L4 with second unit/calibration | no generic hardware or cross-vendor kernel-API ranking from heterogeneous boundaries | none-yet | P1-006; 3080 Ti borrow window | hardware | fully | Candidate NV rider records attention-kernel/BLAS/graph provenance and remains per-boundary at L2; NEEDS-WEB feasibility stays open ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| C5-2.8 | Placement-policy optimality from Q4 coefficients | research question | candidate | L2/L3 | no optimal-placement claim without measured split validation cells | none-yet | Phase 3 full set | hardware | fully | Uses Q4 coefficients plus measured transfer costs to choose placement. |
| C5-2.9 | Local-vs-datacenter crossover economics | research question | candidate | scenario result only | no measured-equivalent cloud comparison | none-yet | P1-003 plus P1-004 | hardware | analysis-plan-only | Surviving scenario form of the carbon-label kill. |
| C5-3.1 | Machine-to-machine variance; generalizability floor | research question | candidate | L4 enabler | no population claim from one unit | none-yet | second M-series unit | hardware | fully | Cheapest route from stack-specific to replication-aware claims. |
| C5-3.2 | Battery-path energy and modeled-rail validation | research question | candidate | L2/L4 bridge | no full-system claim from modeled rails alone | none-yet | USB-C PD analyzer | hardware | fully | Complements AC wall meter with a second physical boundary. |
| C5-3.3 | Cross-ISA NPU/SoC comparison; backend-provenance rider | research question | candidate | L4 only after replication | no broad cross-ISA claim before platform-specific adapter study; no NVIDIA-vs-AMD efficiency claim from single units or heterogeneous boundaries | none-yet | new platform adapters | hardware | analysis-plan-only | Candidate PC provenance rider is capped at L1 and records backend identity now; it creates no AMD science commitment ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| C5-3.4 | Phone-class edge inference | capability claim | candidate | L0/L1 first | no promised phone science before telemetry feasibility | none-yet | phone feasibility | hardware | no | Feasibility verdict may be the result. |
| C5-3.5 | Cross-lab replication | methodology artifact | candidate | L4 enabler | no public benchmark credibility claim without replication | none-yet | external lab coordination | coordination | fully | Coordination-gated credibility layer. |
| C-023-TELEMETRY-PERTURBATION | Telemetry perturbation cost | methodology artifact | candidate (C-023) | L1/L2 floor component | no near-floor claim without telemetry-on/off ABBA check | none-yet | P2-015 component | floor | analysis-plan-only | New coverage-gap row; distinct from C5-1.6 sampling-strategy overhead. |
| C-023-VERSION-DRIFT | OS/runtime version-drift forensics; OS/driver/runtime update forensics | research question | candidate (C-023) | L1/L2 stack-conditioned | no version regression claim without before/after pinned bundles | none-yet | none | software | analysis-plan-only | Turns version churn into a named science/application row. |
| C-023-MARKER-JITTER | Marker/window jitter sensitivity; sampler-phase jitter sensitivity | methodology artifact | candidate (C-023) | L1 methodology; blocker for phase/item claims | no phase/item joule claim without jitter/sampler-phase sensitivity bound | none-yet | P2-015 or claim gate | floor | analysis-plan-only | Quantifies reducer sensitivity to timestamp jitter and sampler phase offset. |
| C-023-OUTPUT-IDENTITY | Output-token identity effects; binding gate for C5-2.5a/b/c/d | methodology artifact | candidate (C-023) | L1/L2 depending comparison | no quant/runtime/spec-decoding efficiency claim without equivalence or divergence report | none-yet | none | software | analysis-plan-only | Fixed output-token count is not fixed decoded work; binding for the PF/NS speculative-decoding riders admitted by D-075 ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| C-023-IDLE-STATIONARITY | Idle-baseline stationarity | methodology artifact | candidate (C-023) | L1 methodology | no idle-subtracted conclusion without idle model-choice sensitivity | none-yet | P2-015 component | floor | analysis-plan-only | D-067 CLOSED the headline-basis question: gross energy within the named boundary is primary. This row stays alive only to test how idle-model choice affects conclusions in the labeled within-device SECONDARY view. |
| C-023-QUALITY-EQUIV-QUANT | Quality-equivalent quantization comparisons; C5-2.11 gate | research question | candidate (C-023) | L2 after equivalence rule | no quantization efficiency or quality-neutrality claim without AP-level equivalence rule | none-yet | none | software | analysis-plan-only | C5-2.11's candidate PF on-device KV leg binds this gate; footprint savings alone do not establish energy or quality neutrality ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| C-023-COEFF-TRANSPORT | Coefficient transport synthetic-to-realistic; energy model portability across workload mixtures | research question | candidate (C-023) | L2/L3 depending holdout | no realistic-session prediction from synthetic grid without transport validation | none-yet | suite traces after Q4 | substrate | analysis-plan-only | Explicitly tests Q4 coefficient transport from synthetic grids to realistic app traces. |
| APP-PROMPT-PROFILER | Prompt/template energy profiler | application idea | candidate | internal L1/L2 only | no prompt-quality claim | none-yet | none | software | analysis-plan-only | Product-facing use of prompt/template energy sensitivity. |
| APP-BUNDLE-POWER-BUG | Attach-a-bundle power-bug repro | application idea | candidate | L0/L1 support workflow | no general bug diagnosis without reproduced bundle | none-yet | none | software | analysis-plan-only | Uses bundle completeness as a maintainer repro artifact. |
| APP-CI-ENERGY-GATES | CI energy-regression gates | application idea | candidate | internal L1/L2 after floors | no CI failure threshold below detection floor | none-yet | P2-015 prerequisite | floor | analysis-plan-only | Needs floors, env snapshots, and baseline-refresh policy. |
| APP-VENDOR-PRESS-AUDIT | Vendor/press claim audit | application idea | candidate | boundary-named L1/L2 | no absolute device-energy verdict without calibration | none-yet | none | hardware | analysis-plan-only | Can audit specific boundary/workload claims, not universal efficiency. |
| APP-MODEL-CARDS | Practitioner energy model cards / leaderboard | application idea | candidate | internal only until L4 replication | no public leaderboard before cross-lab replication | none-yet | C5-3.5 prerequisite | coordination | analysis-plan-only | Internal table can exist; public version is killed until replication. |
| APP-TEACHING-INSTRUMENT | Teaching instrument | application idea | candidate | pedagogical L0/L1 | no research generalization from teaching bundles | none-yet | none | software | analysis-plan-only | Uses bundles for methodology labs on boundaries, floors, and uncertainty. |
| APP-STANDARDS-CONTRIBUTION | Bundle contract as standards contribution | application idea | candidate | methodology artifact proposal | no claim to be the standard | none-yet | none | coordination | analysis-plan-only | Exports the artifact format and validation discipline. |
| APP-CARBON-LABELS | Carbon labels | application idea | killed | none | no carbon label without wall meter and grid assumptions | none-yet | none | hardware | no | Killed as product label; C5-2.9 is the surviving scenario question. |
| APP-BATTERY-RUNTIME | Battery-runtime estimates without calibration | application idea | killed | none | no battery-runtime estimate without system-level calibration | none-yet | none | hardware | no | Explicitly deferred/killed by the application shortlist. |
| APP-LOCAL-CLOUD-ROUTING | Local-vs-cloud routing product | application idea | killed | none | no routing product while cloud side is unmeasured | none-yet | none | hardware | no | Killed product form; scenario analysis remains C5-2.9. |

## Attribution Limits

The rows whose historical wording most invited over-attribution are:

- `C5-1.1`: active-parameter energy scaling. The C-014 amendment caps
  4-6-model designs at descriptive L2 pairwise contrasts unless the model set
  grows enough for a predeclared one-covariate fit, and forbids fitting
  active+total+KV covariates on 4-6 model points. The claims ladder also
  prevents L1 active-parameter-scaling language; the capability map records
  the current two-model observation as a non-claim.
- `C5-1.8`: runtime energy attribution. The bank already says comparisons
  where formats force different artifacts are stack-vs-stack comparisons.
  The registry therefore forbids wording that energy "belongs to the runtime"
  unless the artifact/runtime identity problem is actually controlled.

This subsection is hygiene for claims indexing. It does not re-adjudicate the
ratified C-014/C-015 bank decisions.

exec
/bin/zsh -lc "sed -n '1,220p' docs/research_question_bank.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
# Research Question Bank

Candidate research questions the instrument can answer, beyond the named
set in `PROJECT_STATUS.md`. Populated from council sessions C-003/C-004
(2026-07-07; see `docs/council_log.md` for positions and votes). Promotion
out of the bank requires: a named RQ slot in `PROJECT_STATUS.md`, a data
plan that does not displace queue ranks above it, and (post P1-001) scope
fit. Killed ideas stay recorded with their cause of death.

Canonical live index: `docs/research_question_registry.md`. The registry is
the current index for aliases, status, claim ceilings, owners, and gates; this
bank remains the historical and deliberative record.

## Promoted 2026-07-07 (now Q4-Q6 in PROJECT_STATUS)

- **Q4 Fixed-vs-marginal energy model** — fit
  `E = fixed + prefill(prompt_tokens) + decode(output_tokens)` per
  target/model/quantization; predicts which workloads flatter which
  devices and enables compositional split-energy prediction (predict
  split-run energy from monolithic coefficients + transfer measurements,
  validate on a subset) — the method that makes Q1 answerable at scale.
  Subsumes the prefill-scaling-exponent question. L3 wording requires AP-1
  in `docs/contracts/analysis_plans.md` (2026-07-08, C-014).
- **Q5 Ranking stability** — do within-machine rankings survive workload
  changes (prompt/output/quantization regimes), or where do they flip?
  Cross-device extension is hardware-gated. Uses the 2M matrix directly
  as a substrate; rank wording follows AP-3 in
  `docs/contracts/analysis_plans.md` (2026-07-08, C-014).
- **Q6 Boundary sensitivity** — do conclusions change when measured at
  platform rails vs AC wall power? (Gated on the wall meter, P1-003/R-007;
  reframes calibration as a research result.)

## Methodology centerpiece (deliberately NOT a numbered RQ — C-003 vote)

- **Detection floor / noise floor**: the smallest idle-subtracted energy
  difference each target/telemetry backend can honestly resolve. Observed
  motivation: idle baseline stddev (5.4 W) exceeded its mean (3.5 W) in
  the first real capture. Pairs with the reducer feature all council
  members converged on: **phase/item identifiability flags** (windows with
  fewer than N samples report a flag, not a bare joule value).

## Banked (viable, not yet promoted)

- **Dark silicon / rail utilization**: what fraction of a SoC's rails does
  a runtime energize? (Measured: ANE at 0.0 W through 512 tokens of MLX
  decode — the most quotable standalone finding to date.)
- **CPU:GPU energy division by phase**: does the rail mix shift between
  compute-bound prefill and memory-bound decode? Upstream of split
  economics.
- **KV-growth decode drift**: does per-token energy rise with sequence
  position? Valid only in CHUNKED form — token cadence (~4 ms) far
  outruns the power sampler (~113 ms); no per-token joule claims.
- **Cooldown recovery as thermal characterization**: recovery time vs
  preceding run intensity; cap-hit rates (observed: one 305 s cap-hit vs a
  117 s recovery in the first flagship experiment).
- **Failure frontier**: structured `unsupported` bundles as data — which
  model/quant/context combinations fit, fail, or throttle. Competitors
  discard their failures.
- **Cold-start / keep-warm energy**: model-load joules and the reload-vs-
  resident breakeven. Needs sampling outside the current measured window
  (harness extension).
- **Energy-per-correct-answer vs difficulty** (C-004): instrumented by the
  `affine_mod_ladder_v1` scored workload profile (see below). Claim shape
  pinned by the council: "energy per correct answer rises as accuracy
  falls under a controlled per-attempt energy envelope" — difficulty is
  DESIGNED to hold token budget approximately constant, and observed
  token/stop-reason distributions must be reported to verify residual
  EOS/output-length effects are negligible (wrong-answers-terminate-early
  would bias the curve's magnitude). NOT "difficulty causes energy."
  Amendment 2026-07-08 (C-014): before any scored campaign, an
  envelope-validation smoke gate must show level-invariant emitted-token
  and stop-reason distributions; energy/correct also requires the binomial
  guard in AP-5 (`docs/contracts/analysis_plans.md`). The full 64-level
  scored campaign is deferred until C5-1.9 has a claims-index/figure
  consumer.
- **Speculative-decoding energy**: joules per accepted token with/without
  a draft model. Needs runtime support + quality-equivalence controls.
- **Power-mode Pareto**: energy-latency tradeoff across OS power modes;
  wait until power mode is a first-class config/environment field.
- **Deferred (C-003/C-004 unanimous): general joules-per-solved-task /
  intelligence-per-joule** — drags in accuracy-evaluation policy before
  the measurement dataset matures, and sits in Intelligence per Watt's
  lane where JouleWise is least differentiated. The quarantined ladder
  profile above is the minimal version that survives.

## Instrument expansions adopted by C-004 (queue P2-009 / P2-010)

- **P2-009 rich telemetry (land FIRST — zero capture cost):** parse the
  already-captured-but-discarded plist fields — per-cluster E/P-core DVFS
  residency histograms, per-core frequencies/idle/parking, GPU
  freq/dvfm_states/idle_ratio/sw-requested-vs-achieved state, vendor
  combined_power as a cross-check — plus per-bundle environment snapshots
  (battery/charger state, Low Power Mode, memory pressure, load, display
  state; all sudo-free). Evidence this matters: decode pins the GPU at
  1380 MHz / idle_ratio 0.0 / ~22 W, and the contaminated idle window was
  mechanically visible in `gpu.idle_ratio` (first half at 13 W / 1363 MHz
  before true idle) — parsing it turns our contamination anecdote into an
  automated idle-quality gate. Opt-in `rich_telemetry` tier later: the
  `tasks` sampler (per-process attribution — the direct answer to
  background contamination), disk/network samplers.
- **P2-010 scored workload suite v1:** `affine_mod_ladder_v1` per the
  C-004 design (seed-deterministic SHA-256-derived modular recurrences;
  difficulty = iteration count with prompt shape and answer length fixed;
  exact-integer scoring; levels `{1, 2, 4, 8, 16, 32, 64}`, 16 items/level;
  suite-per-bundle with item/level marker events; level-window energy
  primary; per-item flagged unidentifiable below minimum samples;
  correctness lives in stdlib `joulewise/workloads.py`, scored by the
  reducer so summaries stay re-reducible). Quarantine rules (C-004):
  one optional workload profile, correctness as annotation, no
  "difficulty causes energy" claims. Amendment 2026-07-08 (C-014):
  P2-010 splits into P2-010a suite substrate and P2-010b smoke ladder;
  the full scored ladder remains deferred as above.
  Amendment 2026-07-08 (D-047.1): the level set is the ratified
  powers-of-two set above, not a linear 1..64 sweep.

# Suite architecture v2, benchmark interop, and capability map (Council C-015, 2026-07-08)

## Suite mechanism

C-015 adopts one suite mechanism for benchmark breadth: a suite CAMPAIGN is
`B` whole-suite bundles x `k` distinct items; each suite bundle executes
its `k` items once (`r_within = 1`).
Replication is the count of whole-suite bundles (`B >= 5`, top-up to
`B = 10` near the floor). Item windows inside one bundle are breadth and
attribution evidence, not independent `n` (D-038/AP rules).

Within-bundle repeats are reserved for sentinel items. They estimate
order/cache/thermal effects and same-session repeatability; they never
inflate `n` (C-015). There are no per-item micro-cooldowns by default:
back-to-back execution is a named session ecology, not a flaw. Order
rotates round-robin or Latin-square across bundles, with `item_index`,
`block_index`, `position`, `prev_item`, `prefix_group`, and `order_seed`
recorded (C-015).

Split a suite into balanced blocks when measured wall time exceeds roughly
10-15 minutes or when drift sentinels / floor identifiability degrade.
The first default is `k = 24`; mature panels may use `k = 48` only after
Window A floors and drift checks are clean (C-015). Throughput arithmetic:
`suite_items_per_hour = 3600 * k / (load + idle + cooldown + k * item_runtime)`,
which buys roughly 3-15x item coverage versus one-item bundles, while
`B` remains the `n` and items remain breadth (C-015).

Architectural line: after P2-010a, no workload expansion gets bespoke
marker/window plumbing. New benchmarks are manifests plus generators.
`affine_mod_ladder_v1`, `jw_mixed_v1`, `q4_l3_shape_grid_v1`, the content
sentinel, and benchmark imports are all profiles of the same suite
manifest, marker, and window mechanism (C-015).

## Minimal substrate scope

P2-010a is capped to the minimal generic substrate (C-015): suite/item/block/level
markers, `BundleReader.item_windows()`, source/category/output-policy
fields, per-item token/stop/response hashes, order/cache metadata, manifest
validation, and the per-item validity/status model below. Future
`docs/contracts/run_bundle_layout.md` fields for suite/item/block/level
markers and per-item outputs land with implementation, not in this docs batch
(C-015).

P2-010a status enum:

- `succeeded`
- `malformed`
- `capped`
- `runtime_failed`
- `below_floor`
- `excluded_from_claim`

Aggregation rules (C-015): a block or suite remains claim-usable when the
predeclared aggregation level has enough `succeeded` item windows, paired
markers validate, strict bundle validation passes, and failed/excluded
items are reported rather than silently dropped. `below_floor` items may
contribute only to block/suite-level windows, not item-level joule claims.
`malformed`, `capped`, and `runtime_failed` items remain provenance and
failure-frontier evidence but do not enter numeric claim denominators
unless an AP row predeclares that status as part of the endpoint.
`excluded_from_claim` is an explicit analysis decision with a reason and
does not make the surrounding strict-valid bundle unusable by itself.

Deferred from P2-010a (C-015): scorers, import-specific fields, and rich
difficulty machinery until suite profiles need them.

## `suite_manifest` field sketch

Trimmed P2-010a substrate scope (C-015):

```yaml
schema_version
suite_id
suite_profile
suite_revision
suite_seed
generator:
  name
  version
  parameters_hash
analysis_contract:
  independent_unit
  primary_window_class
  allowed_aggregation_levels
execution_policy:
  order_policy
  within_bundle_repeats
  cooldown_policy
  cache_policy
  warmup_policy
  default_output_policy
source_manifest:
  source_id
  source_kind
  revision
  subset_id
  subset_sha256
  license
  contamination_note
items:
  - item_id
    item_type
    category
    difficulty:
      axis

exec
/bin/zsh -lc "sed -n '221,440p' docs/research_question_bank.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
      value
      scale
      label
      source
      quarantine_note
    shape:
      planned_prompt_tokens
      planned_output_tokens
      prompt_level
      decode_level
    source:
      source_item_id
      source_sha256
      prompt_template_id
      license
      contamination_note
    grouping:
      condition_id
      block_id
      level_id
      prefix_group_id
    output_policy
    status_policy
    tags
markers:
  suite_start_event
  suite_end_event
  block_start_event
  block_end_event
  level_start_event
  level_end_event
  item_start_event
  item_end_event
outputs:
  per_item_response_hash
  per_item_token_count
  per_item_stop_reason
  per_item_status
```

Amendments 2026-07-08 (D-044/D-045/D-046): the sketch is historical and
receives these additive pins. `outputs` gains `per_item_response_text`,
with response text carried in `outputs/suite_items.jsonl` (D-045.8).
`markers` and `outputs` are optional in authored manifests, materialized
to pinned defaults, validated when present, and included in the canonical
effective-manifest hash (D-044/D-045.3). Items gain an additive,
mutually-exclusive `prompt_token_ids` source for ids-native sentinels,
with per-item prompt identity using the D-033 token-ID hash
(D-045.5/D-046).

Deferred fields (C-015): `scoring.scorer_id`,
`scoring.expected_answer_hash`, `scoring.correctness_quarantine`, import-
specific source fields, and richer grouping/difficulty structures such as
`pair_id` and `holdout_role` until a profile and AP row need them.
AP-5's smoke-ladder acceptance already requires level-window energy, so
the deferral condition is met at birth (verification catch, C-015).

## Difficulty metadata rule

Difficulty is first-class quarantined item metadata (C-015):
`{axis, value, scale, label, source}`. Shape is not difficulty:
`q4_l3_shape_grid_v1` prompt/decode cells stay under `shape`, not
`difficulty`. Difficulty metadata enables stratified analysis and envelope
checks; it never licenses "difficulty causes energy" or
intelligence-per-joule wording, and the C-004 quarantine composes.

## Benchmark import

`benchmark_import` is a thin source-to-suite manifest that composes with
the C-005 frozen-subset discipline: hash-manifested subsets, never
"latest split" (C-015). Field sketch:

```text
schema_version
manifest_id
suite_profile
source_benchmark:
  source_id
  name
  upstream_url
  citation
  license_id
  license_text_sha256
  redistribution_policy
  revision_or_commit
  retrieval_date
  source_archive_sha256
  source_split
contamination:
  note
  known_public_benchmark
  intended_use
  prohibited_claims
subset:
  selection_rule
  selection_rule_sha256
  selector_version
  selected_item_ids
  selected_item_ids_sha256
  canonical_subset_json_sha256
prompt_mapping:
  prompt_template_id
  prompt_template_sha256
  source_fields_used
  render_policy
  rendered_prompt_sha256_policy
  output_policy
expected_answer:
  source_field
  stored_as
  expected_answer_sha256
  quarantine: true
  scorer_allowed: false
items:
  suite_item_id
  source_item_id
  source_row_sha256
  source_position
  type_label
  difficulty_label
  difficulty_source
  category
  level
  prompt_template_id
  expected_answer_sha256
  license_override
  contamination_override
  shape_hints
  tags
```

First target: HumanEval as a plumbing smoke import, not a difficulty or
accuracy paper (C-015). Rationale: MIT license, small recognizable corpus,
contamination is explicit and quarantined, 256/512-token code completions
clear the observed ~9 Hz item-window floor more plausibly than one-letter
answers, and `difficulty_label = none/source_not_provided` is acceptable
for a plumbing smoke. MMLU and tinyBenchmarks are rejected as first import
targets because they drag the project toward short-answer score estimation
or benchmark-score estimation. FLORES is the second import target for
tokenizer/multilingual science (C5-W.4/C5-I.3), not the first plumbing
target (C-015).

Claims unlocked by imports (C-015): L0 "JouleWise can freeze and execute an
external benchmark subset as suite items with auditable provenance"; L1
"on a named stack/boundary/output policy, external-shaped items produced
observed item/subset energy and token/stop distributions"; L2 only after an
AP row and repeated strict-valid bundles. Never claim accuracy, pass@k,
capability, benchmark-score standing, or intelligence per joule from this
layer (C-015/C-004).

## Export / energy layer

C-015 adopts a marker-emitting shim for export. The external harness owns
prompts, generation semantics, accuracy artifacts, and metric artifacts.
JouleWise owns power capture, bundle assembly, marker validation, and
energy reduction. The full contract lives in
`docs/contracts/adapter_contracts.md`.

P2-022 is a verdict-shaped feasibility spike (C-015) with verdicts:

- `external_markers_supported`
- `partial(<limitation>)`
- `external_markers_unsupported`

(contract home: docs/contracts/adapter_contracts.md)

P2-022 inherits D-035 subprocess isolation and D-036 computed-verdict
discipline. Its scope is pinned to energy-layer feasibility only (C-015):
3+ marked items, external result artifact hashed, strict bundle valid, no
accuracy interpretation, no leaderboard join, no pass@k-energy ratio, and
no general adapter framework. Any L2 energy comparison from the shim needs
strict bundles, repeated runs, same or calibrated boundary, and an AP row
(C-015).

## Kill / defer

Kill or defer:

- leaderboard integration.
- live dataset fetching.
- "latest split" support.
- JouleWise accuracy scoring beyond quarantined annotation.
- external judge calls, retries, pass@k, or benchmark-score normalization.
- full adapter per harness as the first export path.
- generation-callable wrapper as the first export path.
- MMLU/tinyBenchmarks as first import.
- public energy model-card leaderboard before cross-lab replication.
- per-item uncertainty treated as independent replication.
- any intelligence-per-joule ratio.

## New questions

Interop questions adopted by C-015:

- **C5-I.1 External benchmark energy signatures:** Do imported benchmark
  families have distinguishable energy profiles after matching token shape
  and output policy? Ceiling L2, no capability claim.
- **C5-I.2 Published-difficulty strata vs energy:** Do source-provided
  difficulty or published accuracy strata correlate with energy/stop
  behavior? Ceiling L1 association unless preplanned repeated-bundle L2;
  never "difficulty causes energy."
- **C5-I.3 FLORES tokenizer fertility tax:** For semantic-matched vs
  token-matched FLORES items, how much energy follows tokenizer fertility
  by script/language? Ceiling L2.
- **C5-I.4 Harness overhead floor:** For external harnesses, when does
  harness/process overhead dominate item energy? Ceiling L1/L2
  measurement-method result.
- **C5-I.5 Prompt-template energy sensitivity:** For the same external
  item, how much does canonical vs JouleWise-rendered prompt format change
  energy? Ceiling L2.

Architecture-unlocked candidates, recorded post-2O/post-floor and not
promised campaign work (C-015):

- **Session-shape energy:** does a realistic mixed session cost what
  fixed+prompt+decode coefficients predict, or is there a session overhead
  term?
- **Order-position effects:** how much does energy drift by item position
  after controlling for shape and category?
- **Cache/prefix economics:** what is the joule benefit of prefix reuse,

exec
/bin/zsh -lc "sed -n '441,660p' docs/research_question_bank.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
  resident model state, or prompt-cache warmth versus cold independent
  requests?
- **Reload-vs-resident scheduling:** at what item/session length does
  suite-style batching dominate one-request bundles in total energy and
  wall time?

## Capability map by claim ceiling

### Today

| Question | Ceiling | Ladder-compliant claim template | Campaign | Weakest assumption |
|---|---:|---|---|---|
| Can JouleWise produce auditable local-LLM energy evidence? | L0/L1 | "The harness can execute `<target/runtime/telemetry>` and preserve config, metadata, events, raw power trace, raw telemetry, outputs, and reducer summary in a strict-valid run bundle." | Existing Mac/MLX/powermetrics bundles; strict bundle layout. | Strict validation proves re-derivation of recorded evidence, not independent hardware rerun. |
| What did Qwen2.5-1.5B consume on the M3 Max for the 512-output-token smoke workload? | L1 | "On `M3 Max / MLX / powermetrics SoC rails`, under `<workload/output policy>`, Qwen2.5-1.5B-4bit observed `<mean gross J>` request energy, `<TTFT>`, and `<throughput>` across 3 strict-valid bundles." | 2026-07-06 2I: about 47 J gross, about 94 ms TTFT, about 257 tok/s, gross CV 1.4%. | Idle-subtracted result is contaminated in rep 1; use gross for the cleanest current instrument result. |
| What did Qwen3.5-122B-A10B consume on the same workload? | L1 | "On `M3 Max / MLX / powermetrics SoC rails`, under the same 512-output-token workload, Qwen3.5-122B-A10B-4bit observed `<mean gross J>` request energy, `<TTFT>`, and `<throughput>` across 3 strict-valid bundles." | 2026-07-07: about 304 J gross, about 270 ms TTFT, about 46 tok/s, gross CV 0.3%. | L1 only; n=3 is below comparative protocol. |
| Did the two observed models demonstrate active-parameter scaling? | No; L1 hypothesis only | "The two observed Mac/MLX/powermetrics points are consistent with a fixed/marginal decode-time hypothesis, but they do not support an active-parameter scaling claim." | 122B addendum and claims-ladder downgrade. | Model size, architecture, quantization, and runtime details are confounded. |
| Are short prefill phase joules resolvable at current powermetrics cadence? | L1 "not resolvable" | "On `M3 Max / MLX / powermetrics`, short-prefill phase energy for `<~94 ms window>` is not resolvable at the observed sampling cadence and must not be reported as a standalone joule result." | Observed about 8.8-8.9 Hz; Phase 4 says about 94 ms prefill has fewer than one sample. | Sampler cadence remains near current observed rate. |
| Can same-machine MLX KV replay preserve token identity and size prediction? | L1 feasibility result | "On this M3 Max / mlx-lm stack, prompt-cache replay was supported for `<prompt length>`: resumed greedy decode matched monolithic tokens and measured cache size was within `<delta>` of the KV-size prediction." | Stage 3.0.1: 1024/2048 prompt cache, 64/64 tokens identical, +0.018%/+0.009% size delta. | Same machine/same venv only; not cross-machine portability. |

### After Window A

| Question | Ceiling | Ladder-compliant claim template | Campaign | Weakest assumption |
|---|---:|---|---|---|
| What is the detection floor per metric/window? | L1 methodology result | "For `<target/backend/metric/window class>`, differences below `<floor>` J are not resolvable; supported comparisons use `max(floor_abs_j, floor_cmp_j)`." | P2-015 calibration. | Calibration machine state is representative of later quiet campaigns. |
| What are per-profile Mac baselines? | L1 per condition | "On `M3 Max / MLX / powermetrics`, `<model>` under `<profile>` observed `<energy_request_j>`, `<gross J>`, `<mJ/output-token>`, `<TTFT>`, and `<throughput>` with 95% t-intervals over n=5." | 2M: `short_short`, `long_short`, `short_long`, `mid_mid`. | Output-token denominator and output policy must be runtime-observed/pinned. |
| Does workload shape change request energy on one stack? | L2 | "Within `M3 Max / MLX / powermetrics`, `<profile A>` differed from `<profile B>` for `<model>` by `<effect>` on `<metric/window>`, with n=5 per condition, CIs, manifest order, and effect above floor." | 2M + AP-2. | Drift sentinels and block-position metadata LANDED 2026-07-08 (PR #15). |
| Is prefill/decode power asymmetry visible at long context? | L2 | "Within `M3 Max / MLX / powermetrics`, `long_short` and `short_long` differed in gross phase-window power/energy structure by `<effect>`, above the Window A floor; short-prefill windows remain not resolvable." | 2M/AP-2. | Phase claims are gross-only until phase-idle modeling exists. |
| Do same-boundary efficiency rankings flip across 2M profiles? | L2 | "Within `M3 Max / MLX / powermetrics`, `<condition A>` ranked above `<condition B>` for `<metric>` on `<shape>` only where rank gap exceeded comparison MDE; otherwise the result is an unresolved tie." | 2M + AP-3. | Two-model/four-shape grid may produce unresolved ties rather than rank claims. |
| Do rail/DVFS signatures differ by phase? | L2 structural, not absolute rail truth | "Within `M3 Max / MLX / powermetrics`, rich telemetry showed `<GPU/CPU/ANE/DVFS>` structure differed between `<phase/profile>` and `<phase/profile>`; the claim is about modeled-rail structure, not full-system watts." | 2M with P2-009 rich telemetry. | Powermetrics rails are modeled SoC subsystems, not wall power. |

### After Window B + substrate

| Question | Ceiling | Ladder-compliant claim template | Campaign | Weakest assumption |
|---|---:|---|---|---|
| Can Q4 fit fixed + prompt + decode energy terms? | L3 | "For `<target/model/quant/policy>`, the categorical model `E = fixed + prompt_level + decode_level` predicted held-out cells `(512,256)` and `(4096,512)` within `<error>` after floor and residual checks." | P2-019 `q4_l3_shape_grid_v1`, AP-1. | Holdouts may fail or effects may be below floor, forcing L1/L2 downgrade. |
| Do rankings stay stable on the full shape grid? | L2 | "Within the same boundary, `<model/quant/runtime A>` ranked above `<B>` on `<shape/metric>` only where rank gap exceeded comparison MDE; otherwise unresolved tie." | Window B grid + AP-3. | Rank gaps may be smaller than MDE. |
| Does synthetic prompt content matter at fixed shape? | L2 | "At equal shape, `<content condition>` differed from repeated-seed control by `<delta>` on request energy, with n sized from Window A and above floor." | P2-020 content sentinel, AP-6. | Realized shape/stop policy must stay matched. |
| Does category explain energy beyond token counts? | L2 | "On the common `512/256 fixed_budget_exact` stratum, category residual after controlling for shape was `<delta>`; equivalence/null only if the residual CI lies entirely within ±2% of request energy AND the 2% margin exceeds max(floor_abs_j, floor_cmp_j) (AP-4 gate)." | `jw_mixed_v1` identification core after P2-010a; AP-4. | Small category deltas may be below floor. |
| Does natural-EOS "thinking" inflate reasoning-model energy? | L2 | "For `<reasoning model>`, natural-EOS reasoning requests consumed `<delta>` more request energy than fixed-budget controls, attributable to observed emitted-token/stop-reason distributions, not hidden correctness filtering." | `jw_mixed_v1` natural-EOS pilot. | Output-length inflation must be observed cleanly; no accuracy/judge claim. |
| Is multilingual tokenizer fertility an energy tax? | L2 | "For `<script/language>`, semantic-matched energy differed from token-matched controls by `<delta>`; token-matched null/effect reported separately." | `jw_mixed_v1` multilingual legs; FLORES after HumanEval smoke. | Source licensing and tokenizer-shape matching must be exact. |
| Energy per correct answer under controlled envelope? | L2, only after P2-010b/full scored run | "On the controlled affine ladder, `<model class>` observed `<energy_per_correct>` at `<level band>` only where level-window energy cleared floor and the correctness denominator guard passed; no intelligence-per-joule claim." | P2-010a substrate + P2-010b smoke + later scored campaign; AP-5. | Envelope validation and binomial guard can force `not estimable`. |
| External marked-runner energy layer? | L1/L2 with AP row | "External harness `<X>` version `<Y>` reported metric artifact `<Z>`; JouleWise measured energy for the same marked item/subset windows." | P2-022 shim spike, then AP-covered repetitions only. | Harness markers must pair, stay inside measured windows, and preserve hashed result artifacts. |
| HumanEval import smoke? | L0/L1 | "JouleWise froze and executed a HumanEval subset as suite items with auditable provenance and observed item/subset energy under a named output policy." | P2-023 after P2-022. | Plumbing smoke only; no pass@k, accuracy, or coding-capability interpretation. |

P2-022 shim and P2-023 HumanEval rows are post-2M + substrate (Window B not required).

### Hardware-gated

| Question | Ceiling | Ladder-compliant claim template | Campaign | Weakest assumption |
|---|---:|---|---|---|
| Does split inference reduce energy? | L2 boundary-labeled; stronger with wall calibration | "For `<device pair/link/model/shape>`, split total energy `<prefill + serialize + transfer + deserialize + decode>` was `<less/greater>` than the better monolithic reference by `<delta>`, with boundaries named and calibration status stated." | Phase 3 split; Q1/F4/F5. | Cross-boundary sums are descriptive unless calibrated. |
| How sensitive is split energy to link speed? | L2 | "For `<payload/model/pair>`, changing `<1GbE/2.5GbE/10GbE>` changed transfer energy/time by `<delta>` and moved/did not move the crossover within the measured range." | P1-004 links + transfer bench. | Link throughput must be measured, not assumed. |
| What is the split energy-latency Pareto frontier? | L2 | "Within `<comparison set>`, `<configuration>` is Pareto-frontier because no measured alternative had both lower energy/token and lower `<latency metric>`." | Phase 3 + F6. | Latency metric choice must be fixed per figure. |
| Does measurement boundary change conclusions? | L2; L4 only with replication | "For `<condition pair>`, the conclusion under platform rails `<matched/flipped>` under `wall_meter AC` by `<delta>`." | P1-003 wall meter; Q6/F11. | Wall-meter synchronization/export quality. |
| Do KV-size predictions match measured transfer economics? | L2 | "For `<runtime/model/link>`, analytic KV size predicted serialized payload within `<error>` and transfer energy/GiB within `<interval>`." | P1-004 + P1-006; C5-2.3. | Runtime cache format must be portable or explicitly scoped. |
| Do device rankings generalize beyond one machine? | L2 within boundary; L4 with second unit/calibration | "Across named `<units/stacks>`, `<finding>` replicated under stated workloads and boundaries; cross-boundary quantitative ranking uses named calibration bundles." | P1-006 devices, second unit, wall/USB-C, cross-lab. | Unit-to-unit variance may dominate current floors. |
| Local-vs-datacenter full-system crossover? | Scenario result, not measured-equivalent cloud claim | "Under documented external datacenter-energy assumptions and local `wall_meter AC` measurement, local request energy was `<less/greater>` than the modeled remote alternative for `<workload>`." | Wall meter + network leg; C5-2.9. | Cloud-side energy remains assumption-based, not measured by JouleWise. |

C-015 records three unscheduled cheap campaigns as a select-after-floors
shortlist, not stealth scope: C5-1.6 sampler ABBA, C5-1.12 quantization
benefit decomposition, and C5-1.8 runtime energy attribution. Queue row
P2-024 owns the post-Window-A selection.


# Hardware-gated research agenda — steelmanned potential (Council C-005)

Drafted 2026-07-07 by council C-005 (session shape B; see
`docs/council_log.md` C-005 for positions, adjudications, and dissents).
Format follows `docs/research_question_bank.md`: candidate questions, not
promotions — promotion still requires a named RQ slot in
`PROJECT_STATUS.md`, a data plan that does not displace queue ranks, and
scope fit. IDs here are `C5-<tier>.<n>` to avoid colliding with Q1-Q6.

Every question below survived a devil's-advocate (examiner) round; the
scoping is deliberate, not decorative. Standing kills re-affirmed and
inherited by everything here: no per-token joule claims (~9 Hz sampler vs
~4 ms token cadence — chunked windows only), no unqualified absolute-joule
claims from modeled rails, no general intelligence-per-joule, claim
wording "on this M3 Max / MLX / powermetrics" until a second unit or lab
exists, and present-tense capability claims only for landed code (P2-010 scored suite is QUEUED,
not landed (D-014/P2-011 aggregation and P2-009 telemetry LANDED 2026-07-07)).
(Amendment 2026-07-08: the P2-010 substrate + affine core + generator
engine are now LANDED (PRs #17-#20, D-044..D-047); still not landed:
envelope-gate script, real-tokenizer manifests, all suite campaigns.)

## Why this instrument matters (steelman preamble, examiner-scoped)

**Auditability is the differentiator, not topic novelty.** Energy
benchmarks exist (MLPerf Power; TokenPowerBench; ML.ENERGY-style
datacenter work) — what does not exist is local-inference joules/token
that a skeptic can re-derive: JouleWise publishes self-contained bundles
where config, raw power trace, vendor telemetry, event log, and outputs
are preserved and `validate-bundle --strict` proves the summary re-reduces
identically from raw evidence. Energy tables are otherwise unauditable at
exactly the step that matters.

**Energy per request is becoming the binding constraint on local AI.**
Battery, thermal envelope, and sustained throughput all reduce to joules
per completed request. Latency says whether a local model feels fast
once; `energy_request_j` with uncertainty says whether it can run all day.
The instrument already resolves this at CV 0.3-1.4% across repetitions.

**Apple-Silicon unified memory is a clean window into the memory-bound
decode regime.** The measured 1.5B vs 122B-MoE pair showed energy/token
numerically aligning with the active-parameter ratio while decode power
stayed nearly flat (~23.5 → ~27.5 W). That is hypothesis-generating, not
a scaling result (see C5-1.1), but it demonstrates that the instrument can
see the shape of the regime that throughput benchmarks cannot.

**Negative results are structured data.** did-not-fit, throttle,
contaminated-idle, and cap-hit outcomes produce complete `unsupported` or
quality-flagged bundles. Competitors discard their failures; here the
feasibility frontier is itself a reportable dataset (this is how a
negative Hailo verdict stays a finding).

**The benchmark can referee efficiency claims.** Quantization, runtime,
and architecture "efficiency" claims mix latency, memory, and energy with
no common accounting. Typed configs + one reducer + named measurement
boundaries make within-boundary refereeing possible today and boundary-
labeled cross-target comparisons possible with planned hardware.

**Q4's fixed-vs-marginal model turns benchmark data into engineering
budgets.** `E = fixed + prefill(p) + decode(d)` per target/model/quant
lets an app team budget a workload distribution (an agent session, a RAG
pipeline) from benchmark coefficients — the bridge from instrument to
battery-life engineering.

**The split study is a first-of-kind edge measurement.** Prefill/decode
disaggregation is argued from datacenter throughput; nobody has measured
the ENERGY crossover on local links with both-end power sampling and
per-stage decomposition (prefill/serialize/transfer/deserialize/decode).
Either verdict — crossover exists or doesn't in range — is publishable.
(Examiner note, recorded as standing tension: this is also the most
hardware-gated item in the agenda; the feasibility-first Phase 3 ladder
is the mitigation.)

**The infrastructure outlives any single result.** Every future target is
forced through the same contract (config → bundle → strict re-reduction →
boundary-named summary). The M3 Max numbers are the demo; the reusable
referee is the contribution.

## TIER 1 — answerable with current hardware (M3 Max alone)

Landed software (P2-009 rich telemetry, P2-011 uncertainty
aggregation, 2M campaign tooling — all 2026-07-07) is available;
queued software (P2-010 scored suite) is assumed where noted; no new
hardware. (Amendment 2026-07-08: the suite substrate/ladder-core/
generators are landed, PRs #17-#20; campaign execution still pending.) Throughput reality: ~30-75 bundles/hour makes n=10-20 designs
cheap.

- **C5-1.1 Active-parameter energy scaling (the honest version of the
  122B observation).** Does decode energy/token scale with active rather
  than total parameters across dense and MoE models on one pinned stack?
  Measure on the named M3 Max / MLX / powermetrics SoC-rail boundary:
  gross decode-window joules, mean power, and throughput across 4-6 model
  points (dense 1.5B/7B/14B bridge + ≥2 MoE), same quant recipe, pinned MLX
  version, fixed shapes, n≥5 interleaved; fit gross mJ/token ~ active_params
  (+ total-param/KV covariates) with intervals. Any idle-subtracted result is
  a labeled within-device secondary sensitivity view, not the scaling
  headline (D-067).
  Hardware: now. Methodology: runtime is part of the condition — rerun
  after MLX updates as a separate condition. Threat: model families
  differ in more than active params; the dense bridge and quant pinning
  carry the inference. Who cares: efficient-ML and MoE architecture
  researchers; local-inference benchmark authors. Amendment 2026-07-08
  (C-014): with 4-6 model points, this supports descriptive L2 pairwise
  contrasts only unless the model set grows enough for a predeclared
  one-covariate fit; never fit active+total+KV covariates on 4-6 model
  points.

- **C5-1.2 Context-length energy scaling.** Where does measured energy
  stop being linear in prompt length? Measure: prefill/decode energy over
  prompt 128→8192 (fixed decode 64/256), n≥5; unsupported cells recorded.
  Hardware: now. Methodology: chunked windows; short-prompt prefill
  reported "unresolved at sampler resolution", never 0.03 J-style point
  claims. Threat: SoC boundary underrepresents unified-memory traffic —
  directional bias for long-context (examiner #11); flag pending Q6
  calibration. Who cares: long-context model teams, serving researchers.

- **C5-1.3 Phase-resolved compute-vs-memory signatures (uses landed P2-009 telemetry).**
  Does the rail mix and DVFS residency shift between compute-bound
  prefill and memory-bound decode, and how does the shift move with model
  size/quant? Measure: per-phase CPU:GPU energy division, GPU
  frequency/dvfm residency, idle_ratio across the 2M matrix. Hardware:
  now. Methodology: promotes the banked "CPU:GPU division by phase" item
  with the telemetry that makes it cheap. Threat: modeled rails — claims
  are about STRUCTURE (ratios, shifts), not absolute rail watts. Who
  cares: Apple/Metal/MLX performance engineers, systems-paper authors.

- **C5-1.4 DVFS residency as a throttling early-warning (uses landed P2-009 telemetry).**
  Do residency histograms and idle_ratio drift predict throttling before
  energy/throughput visibly degrade under sustained inference? Measure:
  20-60 min sustained blocks; per-rep energy, residency, cap-hit rates,
  recovery slopes; n≥5 blocks. Hardware: now. Methodology: cooldown-gate
  records and interleaving separate warmup, drift, and throttling.
  Threat: one chassis/ambient; report as within-target characterization.
  Who cares: laptop-inference tool builders, mobile/edge systems
  researchers, thermal-management teams.

- **C5-1.5 Cooldown-recovery curves and the energy tail (promotes banked
  item).** Recovery time and excess idle joules vs preceding run
  intensity; is the tail material to honest energy/request accounting?
  Measure: post-run recovery traces after an intensity ladder; time-to-
  baseline, cap-hit rate, excess joules; n≥5. Hardware: now. Threat:
  ambient sensitivity — record environment snapshots (P2-009). Who
  cares: on-device serving teams, benchmark methodology authors.

- **C5-1.6 Sampling-strategy energy overhead (power-gated).** Does
  temperature/top-p/beam sampling cost measurable energy beyond
  deterministic decoding at fixed output length? Measure: greedy vs
  sampled at fixed decode caps, recorded stop reasons; PRECONDITION:
  measured detection floor first; n≥10 paired ABBA. Hardware: now.
  Threat: plausibly below floor at n=5 — the null ("sampler choice is
  energy-free at this resolution") is the likely and still-reportable
  result. Who cares: runtime maintainers, generation-defaults tuning.

- **C5-1.7 Keep-warm vs reload breakeven (promotes banked cold-start
  item; harness extension).** Model-load joules, resident idle-power
  delta, cold-vs-warm TTFT → breakeven interarrival time per
  model/quant. Measure: load-window sampling (extension: measure outside

exec
/bin/zsh -lc "sed -n '661,880p' docs/research_question_bank.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
  current window), idle-resident deltas, n≥5. Hardware: now. Threat:
  idle-resident delta may be near the detection floor for small models;
  report identifiability. Model-load/warmup trace capture was reviewed and
  DEFERRED by C-015 (R2 items 14-15); it must land before any C5-1.7
  corpus. Who cares: desktop-assistant and agent-framework teams,
  serverless-inference researchers.

- **C5-1.8 Runtime energy attribution.** How much of measured inference
  energy belongs to the runtime, not the model? Same model artifact
  (where format permits) across MLX vs llama.cpp-Metal vs ollama on the
  same machine. Measure: energy/token, power, TTFT, rail mix over a
  shared shape grid, n≥5; artifact hashes and versions pinned. Hardware:
  now. Methodology: where formats force different artifacts (MLX vs
  GGUF), the comparison is stack-vs-stack, stated as such. Threat:
  version churn — this question is BUILT on the pinning discipline
  rather than wounded by it. Who cares: runtime maintainers, local-LLM
  users, model publishers choosing release formats.

  **2026-07-17 kernel-provenance rider (D-075).** Status: **candidate**;
  earliest phase: **NV**. On the 3080 Ti, same model artifact where format
  permits: llama.cpp-CUDA vs vLLM (TensorRT-LLM gated on Ampere-support
  verification) — how much energy variance tracks kernel-library identity vs
  runtime scheduler? Ceiling: **L2 stack-vs-stack**. Forbidden upgrade: **no
  `belongs to the kernel layer` language when artifacts/formats differ; no
  runtime-agnostic kernel claims**. This is an amendment to C5-1.8, not a new
  C5-1.13 thesis. Evidence: [2026-07-17 extension-axis
  evaluation](process_traces/2026-07-17-extension-axes/).

- **C5-1.9 MoE-vs-dense energy per correct answer, quarantined (needs
  P2-010).** Under the controlled-envelope ladder, do MoE and dense
  models at similar quality bands differ in energy per correct answer?
  Measure: affine_mod_ladder_v1 level-window energy + exact scoring;
  token/stop-reason distributions reported (EOS-bias audit). Hardware:
  now. Methodology: C-004 quarantine binds — correctness is an
  annotation; claim template "on this controlled ladder", never
  intelligence-per-joule. Who cares: MoE architecture teams, benchmark-
  methodology reviewers.

- **C5-1.10 The failure frontier as an energy dataset (promotes banked
  item).** Which model × quant × context cells fit, fail, swap, or
  throttle on 128 GB unified memory — with pre-failure energy and memory
  pressure recorded? Measure: full matrix including structured
  `unsupported` bundles, env snapshots. Hardware: now. Threat: one
  memory configuration; frame as the 128 GB-class frontier. Who cares:
  model release engineers, hardware buyers, benchmark authors.

- **C5-1.11 Dark-silicon rail utilization, systematized (promotes banked
  item; needs P2-009).** What fraction of the SoC's rails does each
  runtime/model pair energize (ANE-dark being the first quotable
  instance)? Measure: per-rail energy share and residency by phase
  across the runtime grid of C5-1.8. Hardware: now. Threat: modeled
  rails — report utilization structure, cross-checked against vendor
  combined_power. Who cares: accelerator vendors, runtime implementers.

- **C5-1.12 Quantization benefit decomposition, Mac leg.** For MLX quant
  variants of one family (4/8-bit), how much energy benefit is lower
  power vs shorter time? Measure: decode energy, mean power, throughput
  per quant at fixed shapes, n≥5. Hardware: now (extends to Tier 2 for
  CUDA/GGUF legs). Threat: quant recipes change outputs — greedy-diff
  and report divergence. Who cares: quantization researchers, edge
  deployment teams.

## Workload/query-set expansion (first-class topic, Tier 1 hardware)

Today's workloads are single-prompt fixed-shape grids plus the queued
affine ladder. (Amendment 2026-07-08: the affine ladder CORE is landed,
PRs #17-#20; the envelope-gate script and smoke campaign remain queued.) The council's workload lens designed the expansion; the
examiner frame was applied up front: at fixed token shape, most category
differences may collapse into token counts — that null is itself a
publishable result, named here the **Token-Shape Sufficiency Null**.

**Category taxonomy and expected energy mechanisms.** Six categories,
each with a mechanistic reason energy could differ and an honest
distinguishability call:
chat/instruction (high output-length variance under natural EOS; expected
NULL at fixed shape — the ecological baseline); code generation
(decode-heavy, distinct stop-reason behavior; near-null at fixed budget
unless tokenizer throughput differs on code tokens); summarization/
long-context (prefill-heavy, KV growth — YES, distinguishable via prefill
energy/TTFT/phase mix); reasoning/CoT (thinking-token inflation on
reasoning models — YES, the category effect most likely to be large,
directly measurable on the already-benchmarked Qwen3.5-122B); structured
JSON extraction (early valid-close stops make short answers cheap —
collapses at fixed envelope; probes EOS bias); multilingual (tokenizer
fertility differs sharply by script — YES when semantically matched,
expected null when token-matched; run BOTH, the pair separates fertility
from semantics).

**Realistic-vs-synthetic discipline (hybrid, both by design).**
Deterministic seed-derived synthetic profiles are the CONTROLS
(reproducible, shape-matched, redistribution-safe); pinned realistic
exemplars are the ecological probes (licensing/contamination/tokenizer
caveats recorded per source). Every realistic category runs in two modes:
`fixed_budget_exact` (greedy, EOS suppressed, fixed max_tokens — the
headline category-at-fixed-shape comparison) and `natural_eos` (greedy,
EOS allowed, stop reasons recorded — the operational-cost view). EOS-bias
rule inherited from C-004: natural termination is a workload property,
not a fairness control; wrong/short/refusal answers looking energy-cheap
must be visible in stop-reason distributions, never hidden.

**Sources to pin (hash-manifested frozen subsets, never "latest split"):**
LMSYS-Chat-1M for chat SHAPE distributions (terms-gated, not for
redistribution — derive synthetic shapes from it); HumanEval/MBPP-style
code prompts (MIT, contaminated — prompt exemplars only, no accuracy
claims); public-domain/government texts + synthetic needle controls for
summarization; GSM8K/MMLU-style items for reasoning shapes (MIT on HF,
contaminated — shape not correctness); synthetic fixed-schema records for
JSON; FLORES-200 for multilingual (CC BY-SA, parallel sentences enable
the semantic-matched leg). Where licenses are uncertain, synthetic wins.

**Concrete recommendation — `jw_mixed_v1` (adopt as the first official
workload expansion).** Amendment 2026-07-08 (C-014): this supersedes the
C-005 fixed-budget-full-first sequencing; the C-005 category/source
discipline otherwise remains intact. Phase 1 is the identification core:
all 6 categories at the common-shape identification stratum, `512/256`
`fixed_budget_exact`, synthetic + realistic where licensing is clean.
Phase 2 is a natural-EOS pilot with >=4 items/category on reasoning, JSON,
chat, and multilingual. Phase 3 is the full category panels, gated on
above-floor structure from Phases 1-2. The original full panel remains the
expansion target after the gate: 6 categories x 8 items = 48 items per
target/model/quant, n=5, categories interleaved round-robin, with the
C-005 category shapes (chat 512/256; code 4x512/256 + 4x1024/512;
summarization 4096/256; reasoning 512/512; JSON extraction 1024/128;
multilingual FLORES 8 languages semantic-matched then token-matched
512/256; ~240 bundles = 3-8 hours per target/model/quant at observed
throughput) unless the Phase 1/2 gate amends them. Harness needs (all additive): `workload_profile.category` +
`source_manifest` + sha256 + per-item `output_policy` fields; category as
a campaign-matrix axis alongside shape (never instead of it); per-item
stop reason/emitted-token/response hash in outputs; reuse P2-010a item
windows + identifiability flags; aggregation waits on P2-011. Out of
scope stays out: no accuracy evals, no judges, no retries — correctness
only as quarantined annotation. Category claims follow AP-4 in
`docs/contracts/analysis_plans.md`.
Amendment 2026-07-08 (D-046 and deferred-binding B6 disposition):
`jw.multiling` synthetic is phase-1 control material, not a C5-W.4 FLORES
replacement; the FLORES 6-vs-8 language count and token-matched
substitution decision are deferred to the FLORES/source session.

**Questions it unlocks (Tier 1):**

- **C5-W.1 Does category explain energy beyond token counts?** Paired
  synthetic controls vs realistic exemplars at identical shape; either a
  category effect or the Token-Shape Sufficiency Null — both reportable.
  Threat: small deltas need the detection floor first (examiner #2). The
  reportable comparison is AP-4 in `docs/contracts/analysis_plans.md`,
  using the common-shape stratum and the predeclared equivalence margin
  from C-014. Who cares: benchmark authors, app engineers budgeting
  features.
- **C5-W.2 Does thinking-token inflation dominate reasoning-model request
  energy?** Fixed-budget vs natural-EOS on the reasoning flagship;
  measures the energy price of "thinking" as output-length inflation.
  Who cares: reasoning-model teams, agent builders choosing modes.
- **C5-W.3 Is category energy-ranking stable across models and quants?**
  The workload-axis analogue of Q5; do code/long-context/reasoning flip
  the ordering? Who cares: procurement, model-selection tooling.
- **C5-W.4 Tokenizer fertility as an energy tax.** Semantic-matched vs
  token-matched multilingual pairs isolate joules attributable to
  tokenizer choice per script. Who cares: multilingual deployment,
  tokenizer designers.


## TIER 2 — unlocked by already-planned hardware gates

Gates by name: P1-006 device access (owned RTX 3050; Jetson Orin Nano),
the 3080 Ti borrow window (Phase 3 interconnect sweep only), P1-003 wall
meter decision (R-007), P1-004 network topology (1GbE / 2.5GbE / optional
10GbE).

- **C5-2.1 Quantization decomposition, cross-stack.** C5-1.12 extended
  to llama.cpp-CUDA/vLLM on the 3050: is the time-vs-watts split of
  quantization benefit hardware-dependent? Gate: P1-006. Threat:
  nvidia-smi board boundary ≠ SoC boundary — within-target decomposition
  first, cross-target only boundary-labeled. Who cares: quantization and
  runtime teams.

- **C5-2.2 Batch size and the prefill/decode energy split.** Does
  static batching reshape gross energy/request and the phase split under
  an interactive latency bound? Measure: B in {1,2,4,8,16}, group gross
  energy and gross joules/request within the named target/telemetry
  boundary, latency distribution, and structured memory-fit failures.
  The Mac leg is MINTED (2026-07-16: AXI-SB verdict `supported` on pinned
  mlx-lm 0.31.3, lead-run B∈{2,4} live probes with full per-request
  observability — `docs/specs/axi/sb_static_batch_verdict.md`); execution
  still requires the follow-on batch adapter row, P2-015 floors, and its own
  scheduled quiet-Mac block. The serving-style leg remains gated on P1-006.
  Continuous batching is a post-capstone extension (D-070).
  Who cares: serving researchers, scheduler developers.

- **C5-2.3 Predicted-vs-measured KV economics.** Does the analytic
  kv-size model predict serialized cache size, transfer energy, and
  deserialize energy? Measure: transfer joules/GiB both ends over
  payload ladder 16 MiB-2 GiB per link; deserialize windows; predicted
  vs actual deltas calibrate the model. Gates: P1-004 links + any second
  node (P1-006). Methodology: both-end sampling, clock-offset bounds
  flagged; this is the instrument's designed home turf. Who cares:
  disaggregated-inference researchers, KV-cache system builders.

- **C5-2.4 KV-cache quantization end-to-end.** Does q8_0 cache save
  energy after serialize/deserialize overhead, or only bytes? Gates:
  P1-006 + P1-004 (llama.cpp cache portability spike verdict). Who
  cares: llama.cpp maintainers, KV-compression researchers.

- **C5-2.5 Speculative decoding joules per ACCEPTED token (promotes
  banked item).** With/without draft model at output equivalence.
  Measure: total joules, acceptance rate, joules/accepted-token, n≥5.
  Gate: runtime support (MLX or 3050 stack). Methodology: the
  accepted-token denominator is the trap the harness's token accounting
  defuses. Who cares: speculative-decoding researchers, runtime teams.

  **2026-07-17 DSpark/DFlash candidate riders (D-075).** These remain
  riders on C5-2.5, not four independent theses; every effect is floor-gated
  and `C-023-OUTPUT-IDENTITY` is binding. Evidence for all four:
  [2026-07-17 extension-axis
  evaluation](process_traces/2026-07-17-extension-axes/).

  - **C5-2.5a — cross-method contrast.** Status: **candidate (deferred
    rider)**; earliest phase: **NS**. At matched target model, quantization,
    prompt roster, and output equivalence, do a fixed-K block-diffusion
    drafter (DFlash) and a variable-K confidence-scheduled drafter (DSpark)
    differ in gross request energy and gross J/committed-output-token on the

exec
/bin/zsh -lc "sed -n '881,1120p' docs/research_question_bank.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
    same MLX stack? Ceiling: **L2**. Forbidden upgrade: **No cross-method
    efficiency generalization beyond the measured target/runtime/tokenizer
    pair; accepted-draft J/token stays a mechanism diagnostic, never the
    on/off efficiency denominator (token_normalization.md D-037 rider).** It
    stays out of the committed standalone set until a prospective
    cross-mechanism design is affordable.

  - **C5-2.5b — proposal-work secondary.** Status: **candidate**; earliest
    phase: **PF**. Is proposal length an energy knob: holding drafter and
    target fixed, does gross J/committed-output-token vary systematically
    with realized mean proposed-K (DFlash block-size sweep 8/16 vs DSpark's
    dynamic schedule), i.e. does per-round proposed work enter the Q4
    coefficients? Ceiling: **L2**. Forbidden upgrade: **No claim that
    K-scheduling saves energy in general; result scoped to one
    runtime/target/boundary, and realized per-round tokens_proposed must be
    runtime-observed, never inferred from the configured cap.**

  - **C5-2.5c — primary Q4 break-even rider.** Status: **candidate**;
    earliest phase: **PF**. Drafter-overhead economics: at what aggregate
    acceptance rate does spec-on gross energy break even with spec-off for
    each drafter class (block-diffusion vs semi-autoregressive vs native MTP
    if a supported runtime lands), at matched output? Ceiling: **L2**.
    Forbidden upgrade: **No serving-system or cross-hardware generalization
    from one pair; the MTP arm is contingent on an AXI-SC supported verdict
    and is a separate frozen family (FAM-AXI-SPEC-NATIVE-MTP), never pooled
    with draft_model arms.**

  - **C5-2.5d — mandatory contamination control.** Status: **candidate**;
    earliest phase: **PF**. Hybrid-lookup contamination bound: how much does
    mlx-dspark's drafter-free n-gram lookup path (on by default) shift
    measured gross energy and acceptance accounting vs `--no-lookup-drafts`,
    quantified as an attribution-contamination diagnostic? Ceiling: **L2
    (diagnostic/methods row)**. Forbidden upgrade: **No mechanism-yield or
    efficiency claim from mixed-origin rounds; the row exists to justify the
    mode pin, not to rank lookup vs drafter.**

- **C5-2.6 Energy-optimal request coalescing under a latency bound.**
  Replayed arrival traces × coalescing windows → joules/request vs
  p95 latency Pareto. Gate: P1-006. Who cares: edge gateways, serving
  schedulers.

- **C5-2.7 Device perf/W rankings with runtime held constant (extends
  Q5, doesn't duplicate it).** Same llama.cpp build/model/quant across
  M3 Max / 3050 / Orin (+3080 Ti in window): do rankings survive
  workload changes when the RUNTIME variable is removed? Gates: P1-006,
  borrow window. Threat: boundary heterogeneity — ranking claims are
  per-boundary until wall-calibrated (C5-2.9). Who cares: hardware
  reviewers, edge procurement.

  **2026-07-17 kernel-provenance rider (D-075).** Status: **candidate**;
  earliest phase: **NV**. When the runtime is held constant (same llama.cpp
  build/model/quant) across M3 Max Metal and 3080 Ti CUDA, does recorded
  kernel-layer identity (attention kernel, BLAS backend, graph mode) explain
  residual energy structure beyond device? Ceiling: **L2 within each
  measurement boundary; per-boundary only until wall-calibrated (C5-2.9)**.
  Forbidden upgrade: **no cross-vendor kernel-API efficiency ranking; no
  cross-device winner across heterogeneous boundaries**. Evidence:
  [2026-07-17 extension-axis
  evaluation](process_traces/2026-07-17-extension-axes/).

- **C5-2.8 Placement-policy optimality from Q4 coefficients.** Can
  fitted fixed+marginal coefficients + measured transfer costs choose
  the energy-optimal prefill/decode placement, validated against
  measured splits? Gates: full Phase 3 set (P1-006, P1-004, borrow
  window). Methodology: modeled-vs-measured labeled; composite bundles.
  Who cares: disaggregated-serving and placement-policy researchers.

- **C5-2.9 Local-vs-datacenter crossover economics (survivor of the
  carbon-label kill).** When is a local request energy-cheaper than
  shipping it out — full-system watts, transfer included, datacenter
  side as DOCUMENTED published-figure assumptions, never measured-
  equivalent? Gates: P1-003 wall meter (+P1-004 for transfer leg).
  Methodology: the wall meter is what makes the local side full-system
  honest; boundary-directional bias (examiner #11) is why SoC rails
  alone can't carry this. Who cares: sustainability-of-ML community,
  enterprise local-vs-cloud deciders.

- **C5-2.10 Boundary-directional bias quantification (elevates Q6).**
  Not just "does the boundary change conclusions" but WHICH comparisons
  flip: memory-heavy vs compute-heavy conditions should diverge
  rail-vs-wall differently. Gate: P1-003. Methodology: pairs with
  C5-1.2/C5-2.3 threat notes; turns their caveat into a measured
  correction. Who cares: every downstream consumer of cross-target
  numbers; measurement-methodology reviewers.

- **C5-2.11 On-device quantized-KV energy.** Status: **candidate**;
  earliest phase: **PF**. Does quantized KV cache (`kv_bits` 8/4, mlx-lm)
  reduce gross request energy for long-context decode on-device, or only
  memory footprint? Ceiling: **L2, per-boundary, MLX-scoped; un-gated variant
  of C5-2.4 (no transfer leg, runnable on the D-073 fleet now)**. Forbidden
  upgrade: **No byte-saving-equals-energy-saving claim (inherits C5-2.4's
  ban); no cross-runtime generalization from MLX alone; no quality-neutrality
  claim without C-023-style output-equivalence evidence**. Attachments:
  C5-2.4, C5-1.12, and C-023-QUALITY-EQUIV-QUANT. Evidence: [2026-07-17
  extension-axis evaluation](process_traces/2026-07-17-extension-axes/).

- **C5-2.12 Bounded-window KV marginal-slope rider.** Status:
  **candidate**; earliest phase: **PF**. Does a bounded evicting window
  (`RotatingKVCache` via `max_kv_size`) flatten the marginal J/token slope
  over long generations versus an unbounded step-growing `KVCache`? Ceiling:
  **L2 in chunked windows only (RQ-KV-GROWTH discipline: token cadence
  outruns power sampling)**. Forbidden upgrade: **No per-token joule claims
  below the cadence/sampling floor; no output-equivalence assumption —
  eviction changes generations, so contrasts are work-matched, never
  output-matched**. This is an amendment under C5-1.2/RQ-KV-GROWTH, not an
  independent thesis. Evidence: [2026-07-17 extension-axis
  evaluation](process_traces/2026-07-17-extension-axes/).

- **C5-2.13 Serialized prompt-cache crossover rider.** Status:
  **candidate**; earliest phase: **PF**. Is save+load+replay of a serialized
  prompt cache energy-cheaper than re-prefill at prompt length N on the same
  machine, and where is the crossover? Ceiling: **L2 same-machine,
  same-stack (promotes answered-L1 RQ-MLX-KV-REPLAY to an energy claim)**.
  Forbidden upgrade: **No cross-machine or cross-stack portability claim
  (RQ-MLX-KV-REPLAY's existing ban); no generalization beyond the measured
  prompt-length ladder**. This is an amendment under RQ-CACHE-PREFIX and
  RQ-MLX-KV-REPLAY, not an independent thesis. Evidence: [2026-07-17
  extension-axis evaluation](process_traces/2026-07-17-extension-axes/).

- **C5-2.14 Q4 cache-policy coefficient rider.** Status: **candidate**;
  earliest phase: **PF**. Do KV-cache-policy contrasts move the fitted Q4
  coefficients in the predicted direction (marginal per-token term down
  under quantized KV, fixed term unchanged)? Ceiling: **L2; L3 only through
  Q4/AP-1's existing holdout machinery (D-070 clause 5)**. The candidate
  rider itself remains capped at L2. Forbidden upgrade: **No new-thesis
  framing — this is a Q4 stress test, not a KV-energy model; no
  coefficient-direction claim below P2-015 detection floors**. Evidence:
  [2026-07-17 extension-axis
  evaluation](process_traces/2026-07-17-extension-axes/).

## TIER 3 — requiring new acquisitions (hardware class + rough cost tier)

- **C5-3.1 Machine-to-machine variance / generalizability floor.** A
  second M-series unit (used M1/M2/M4, ~$500-1500) answers the
  examiner's sharpest structural attack: which Tier-1 findings replicate
  on a second box, and what is unit-to-unit variance relative to the
  detection floor? Also unlocks chassis-thermal comparisons (Air vs Pro
  fanless/fanned envelopes). This is the cheapest purchase that converts
  "on this M3 Max" claims into population claims.

- **C5-3.2 Battery-path energy and modeled-rail validation.** A USB-C PD
  power analyzer (~$100-300) measures DC input on battery-excluded runs
  and cross-checks powermetrics' modeled rails at a second physical
  boundary — a cheap partial answer to the modeled-vs-measured attack,
  complementary to the AC wall meter.

- **C5-3.3 Cross-ISA NPU/SoC comparison.** AMD Ryzen-AI mini-PC and/or
  Snapdragon-X laptop (~$800-2000 each): do the dark-silicon and
  active-param-scaling structures hold beyond Apple's stack? Requires
  one new telemetry adapter per platform (the adapter contract is the
  deliverable that makes this tractable).

  **2026-07-17 backend-provenance rider (D-075).** Status: **candidate**;
  earliest phase: **PC**. Record kernel/backend build provenance
  (CUDA/Metal/HIP target, kernel library ids) in all bundles now so a
  post-capstone AMD/ROCm replication leg is comparable without re-running the
  NVIDIA/Mac corpus. Candidate-rider ceiling: **L1 feasibility**; the parent
  row's separate L4 replication posture is not an intake upgrade. Forbidden
  upgrade: **no NVIDIA-vs-AMD efficiency claim from single
  units or heterogeneous boundaries; no cross-ISA claim before a
  platform-specific adapter study**. Evidence: [2026-07-17 extension-axis
  evaluation](process_traces/2026-07-17-extension-axes/).

- **C5-3.4 Phone-class edge inference.** One flagship phone
  (~$800-1200) + llama.cpp/MLX-swift: the actual battery-constrained
  edge story. Honest note: telemetry access on phones is the hard part;
  a feasibility verdict (possibly `unsupported`) is itself the
  publishable first result, exactly like Hailo.

- **C5-3.5 Cross-lab replication (zero hardware, the credibility
  acquisition).** A second lab runs the frozen suite from published
  bundles + configs. Gates every public-facing application (leaderboard,
  standard, audit service); costs coordination, not money.

## Unexpected-applications shortlist (beyond papers)

Ranked by usefulness × lowest extra work; every public-facing one carries
the internal-first ladder from the examiner round.

1. **Prompt/template energy profiler** — product engineers measure the
   joule cost of system-prompt/RAG-template variants; ~3-8 person-days
   (prompt-matrix configs + diff report); rides per-request joules +
   phase attribution. Available now.
2. **Attach-a-bundle power-bug repro** — runtime maintainers receive
   "model got slow/hot" reports as reproducible bundles; ~5-10 days
   (issue template + doc); rides bundle completeness. Available now;
   mundane and high-leverage.
3. **CI energy-regression gates** for MLX/llama.cpp — nightly pinned-host
   run fails on mJ/token regressions; ~5-15 days; rides strict
   validation + config hashing. PRECONDITIONS (examiner): measured
   detection floor as the threshold unit, env snapshots (P2-009),
   baseline-refresh policy across OS updates.
4. **Vendor/press claim audit** — "efficient" claims answered with
   boundary-named measured bundles; ~5-10 days. Defensible as "on this
   boundary, this workload"; overclaims if framed as absolute device
   energy without wall calibration.
5. **Practitioner energy model cards / leaderboard** — joules/token with
   uncertainty next to quality scores; ~5-10 days internal. Ladder:
   internal table → published methodology → cross-lab public table
   (C5-3.5); public version is KILLED until then.
6. **OS/driver/runtime update forensics** — before/after bundles detect
   power-behavior regressions from macOS/MLX updates (DVFS residency
   makes it mechanistic); ~5-15 days; stronger with landed P2-009 rich telemetry.
7. **Teaching instrument** — a measurement-methodology lab course (idle
   subtraction, boundaries, uncertainty, negative results) with bundles
   as graded artifacts; ~5-12 days.
8. **Bundle contract as a standards contribution** — the run-bundle
   layout + boundary table + strict validator packaged as a proposed
   artifact format for edge-LLM energy (MLPerf-Power-adjacent); ~15-30
   days. Export the methodology; do not claim to BE the standard.

Deferred/killed applications: carbon LABELS (needs wall meter + grid
assumptions; see C5-2.9 for the surviving question), battery-runtime
estimates without system-level calibration, local-vs-cloud ROUTING as a
product (cloud side unmeasurable today).

exec
/bin/zsh -lc "sed -n '441,550p' docs/research_question_bank.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
  resident model state, or prompt-cache warmth versus cold independent
  requests?
- **Reload-vs-resident scheduling:** at what item/session length does
  suite-style batching dominate one-request bundles in total energy and
  wall time?

## Capability map by claim ceiling

### Today

| Question | Ceiling | Ladder-compliant claim template | Campaign | Weakest assumption |
|---|---:|---|---|---|
| Can JouleWise produce auditable local-LLM energy evidence? | L0/L1 | "The harness can execute `<target/runtime/telemetry>` and preserve config, metadata, events, raw power trace, raw telemetry, outputs, and reducer summary in a strict-valid run bundle." | Existing Mac/MLX/powermetrics bundles; strict bundle layout. | Strict validation proves re-derivation of recorded evidence, not independent hardware rerun. |
| What did Qwen2.5-1.5B consume on the M3 Max for the 512-output-token smoke workload? | L1 | "On `M3 Max / MLX / powermetrics SoC rails`, under `<workload/output policy>`, Qwen2.5-1.5B-4bit observed `<mean gross J>` request energy, `<TTFT>`, and `<throughput>` across 3 strict-valid bundles." | 2026-07-06 2I: about 47 J gross, about 94 ms TTFT, about 257 tok/s, gross CV 1.4%. | Idle-subtracted result is contaminated in rep 1; use gross for the cleanest current instrument result. |
| What did Qwen3.5-122B-A10B consume on the same workload? | L1 | "On `M3 Max / MLX / powermetrics SoC rails`, under the same 512-output-token workload, Qwen3.5-122B-A10B-4bit observed `<mean gross J>` request energy, `<TTFT>`, and `<throughput>` across 3 strict-valid bundles." | 2026-07-07: about 304 J gross, about 270 ms TTFT, about 46 tok/s, gross CV 0.3%. | L1 only; n=3 is below comparative protocol. |
| Did the two observed models demonstrate active-parameter scaling? | No; L1 hypothesis only | "The two observed Mac/MLX/powermetrics points are consistent with a fixed/marginal decode-time hypothesis, but they do not support an active-parameter scaling claim." | 122B addendum and claims-ladder downgrade. | Model size, architecture, quantization, and runtime details are confounded. |
| Are short prefill phase joules resolvable at current powermetrics cadence? | L1 "not resolvable" | "On `M3 Max / MLX / powermetrics`, short-prefill phase energy for `<~94 ms window>` is not resolvable at the observed sampling cadence and must not be reported as a standalone joule result." | Observed about 8.8-8.9 Hz; Phase 4 says about 94 ms prefill has fewer than one sample. | Sampler cadence remains near current observed rate. |
| Can same-machine MLX KV replay preserve token identity and size prediction? | L1 feasibility result | "On this M3 Max / mlx-lm stack, prompt-cache replay was supported for `<prompt length>`: resumed greedy decode matched monolithic tokens and measured cache size was within `<delta>` of the KV-size prediction." | Stage 3.0.1: 1024/2048 prompt cache, 64/64 tokens identical, +0.018%/+0.009% size delta. | Same machine/same venv only; not cross-machine portability. |

### After Window A

| Question | Ceiling | Ladder-compliant claim template | Campaign | Weakest assumption |
|---|---:|---|---|---|
| What is the detection floor per metric/window? | L1 methodology result | "For `<target/backend/metric/window class>`, differences below `<floor>` J are not resolvable; supported comparisons use `max(floor_abs_j, floor_cmp_j)`." | P2-015 calibration. | Calibration machine state is representative of later quiet campaigns. |
| What are per-profile Mac baselines? | L1 per condition | "On `M3 Max / MLX / powermetrics`, `<model>` under `<profile>` observed `<energy_request_j>`, `<gross J>`, `<mJ/output-token>`, `<TTFT>`, and `<throughput>` with 95% t-intervals over n=5." | 2M: `short_short`, `long_short`, `short_long`, `mid_mid`. | Output-token denominator and output policy must be runtime-observed/pinned. |
| Does workload shape change request energy on one stack? | L2 | "Within `M3 Max / MLX / powermetrics`, `<profile A>` differed from `<profile B>` for `<model>` by `<effect>` on `<metric/window>`, with n=5 per condition, CIs, manifest order, and effect above floor." | 2M + AP-2. | Drift sentinels and block-position metadata LANDED 2026-07-08 (PR #15). |
| Is prefill/decode power asymmetry visible at long context? | L2 | "Within `M3 Max / MLX / powermetrics`, `long_short` and `short_long` differed in gross phase-window power/energy structure by `<effect>`, above the Window A floor; short-prefill windows remain not resolvable." | 2M/AP-2. | Phase claims are gross-only until phase-idle modeling exists. |
| Do same-boundary efficiency rankings flip across 2M profiles? | L2 | "Within `M3 Max / MLX / powermetrics`, `<condition A>` ranked above `<condition B>` for `<metric>` on `<shape>` only where rank gap exceeded comparison MDE; otherwise the result is an unresolved tie." | 2M + AP-3. | Two-model/four-shape grid may produce unresolved ties rather than rank claims. |
| Do rail/DVFS signatures differ by phase? | L2 structural, not absolute rail truth | "Within `M3 Max / MLX / powermetrics`, rich telemetry showed `<GPU/CPU/ANE/DVFS>` structure differed between `<phase/profile>` and `<phase/profile>`; the claim is about modeled-rail structure, not full-system watts." | 2M with P2-009 rich telemetry. | Powermetrics rails are modeled SoC subsystems, not wall power. |

### After Window B + substrate

| Question | Ceiling | Ladder-compliant claim template | Campaign | Weakest assumption |
|---|---:|---|---|---|
| Can Q4 fit fixed + prompt + decode energy terms? | L3 | "For `<target/model/quant/policy>`, the categorical model `E = fixed + prompt_level + decode_level` predicted held-out cells `(512,256)` and `(4096,512)` within `<error>` after floor and residual checks." | P2-019 `q4_l3_shape_grid_v1`, AP-1. | Holdouts may fail or effects may be below floor, forcing L1/L2 downgrade. |
| Do rankings stay stable on the full shape grid? | L2 | "Within the same boundary, `<model/quant/runtime A>` ranked above `<B>` on `<shape/metric>` only where rank gap exceeded comparison MDE; otherwise unresolved tie." | Window B grid + AP-3. | Rank gaps may be smaller than MDE. |
| Does synthetic prompt content matter at fixed shape? | L2 | "At equal shape, `<content condition>` differed from repeated-seed control by `<delta>` on request energy, with n sized from Window A and above floor." | P2-020 content sentinel, AP-6. | Realized shape/stop policy must stay matched. |
| Does category explain energy beyond token counts? | L2 | "On the common `512/256 fixed_budget_exact` stratum, category residual after controlling for shape was `<delta>`; equivalence/null only if the residual CI lies entirely within ±2% of request energy AND the 2% margin exceeds max(floor_abs_j, floor_cmp_j) (AP-4 gate)." | `jw_mixed_v1` identification core after P2-010a; AP-4. | Small category deltas may be below floor. |
| Does natural-EOS "thinking" inflate reasoning-model energy? | L2 | "For `<reasoning model>`, natural-EOS reasoning requests consumed `<delta>` more request energy than fixed-budget controls, attributable to observed emitted-token/stop-reason distributions, not hidden correctness filtering." | `jw_mixed_v1` natural-EOS pilot. | Output-length inflation must be observed cleanly; no accuracy/judge claim. |
| Is multilingual tokenizer fertility an energy tax? | L2 | "For `<script/language>`, semantic-matched energy differed from token-matched controls by `<delta>`; token-matched null/effect reported separately." | `jw_mixed_v1` multilingual legs; FLORES after HumanEval smoke. | Source licensing and tokenizer-shape matching must be exact. |
| Energy per correct answer under controlled envelope? | L2, only after P2-010b/full scored run | "On the controlled affine ladder, `<model class>` observed `<energy_per_correct>` at `<level band>` only where level-window energy cleared floor and the correctness denominator guard passed; no intelligence-per-joule claim." | P2-010a substrate + P2-010b smoke + later scored campaign; AP-5. | Envelope validation and binomial guard can force `not estimable`. |
| External marked-runner energy layer? | L1/L2 with AP row | "External harness `<X>` version `<Y>` reported metric artifact `<Z>`; JouleWise measured energy for the same marked item/subset windows." | P2-022 shim spike, then AP-covered repetitions only. | Harness markers must pair, stay inside measured windows, and preserve hashed result artifacts. |
| HumanEval import smoke? | L0/L1 | "JouleWise froze and executed a HumanEval subset as suite items with auditable provenance and observed item/subset energy under a named output policy." | P2-023 after P2-022. | Plumbing smoke only; no pass@k, accuracy, or coding-capability interpretation. |

P2-022 shim and P2-023 HumanEval rows are post-2M + substrate (Window B not required).

### Hardware-gated

| Question | Ceiling | Ladder-compliant claim template | Campaign | Weakest assumption |
|---|---:|---|---|---|
| Does split inference reduce energy? | L2 boundary-labeled; stronger with wall calibration | "For `<device pair/link/model/shape>`, split total energy `<prefill + serialize + transfer + deserialize + decode>` was `<less/greater>` than the better monolithic reference by `<delta>`, with boundaries named and calibration status stated." | Phase 3 split; Q1/F4/F5. | Cross-boundary sums are descriptive unless calibrated. |
| How sensitive is split energy to link speed? | L2 | "For `<payload/model/pair>`, changing `<1GbE/2.5GbE/10GbE>` changed transfer energy/time by `<delta>` and moved/did not move the crossover within the measured range." | P1-004 links + transfer bench. | Link throughput must be measured, not assumed. |
| What is the split energy-latency Pareto frontier? | L2 | "Within `<comparison set>`, `<configuration>` is Pareto-frontier because no measured alternative had both lower energy/token and lower `<latency metric>`." | Phase 3 + F6. | Latency metric choice must be fixed per figure. |
| Does measurement boundary change conclusions? | L2; L4 only with replication | "For `<condition pair>`, the conclusion under platform rails `<matched/flipped>` under `wall_meter AC` by `<delta>`." | P1-003 wall meter; Q6/F11. | Wall-meter synchronization/export quality. |
| Do KV-size predictions match measured transfer economics? | L2 | "For `<runtime/model/link>`, analytic KV size predicted serialized payload within `<error>` and transfer energy/GiB within `<interval>`." | P1-004 + P1-006; C5-2.3. | Runtime cache format must be portable or explicitly scoped. |
| Do device rankings generalize beyond one machine? | L2 within boundary; L4 with second unit/calibration | "Across named `<units/stacks>`, `<finding>` replicated under stated workloads and boundaries; cross-boundary quantitative ranking uses named calibration bundles." | P1-006 devices, second unit, wall/USB-C, cross-lab. | Unit-to-unit variance may dominate current floors. |
| Local-vs-datacenter full-system crossover? | Scenario result, not measured-equivalent cloud claim | "Under documented external datacenter-energy assumptions and local `wall_meter AC` measurement, local request energy was `<less/greater>` than the modeled remote alternative for `<workload>`." | Wall meter + network leg; C5-2.9. | Cloud-side energy remains assumption-based, not measured by JouleWise. |

C-015 records three unscheduled cheap campaigns as a select-after-floors
shortlist, not stealth scope: C5-1.6 sampler ABBA, C5-1.12 quantization
benefit decomposition, and C5-1.8 runtime energy attribution. Queue row
P2-024 owns the post-Window-A selection.


# Hardware-gated research agenda — steelmanned potential (Council C-005)

Drafted 2026-07-07 by council C-005 (session shape B; see
`docs/council_log.md` C-005 for positions, adjudications, and dissents).
Format follows `docs/research_question_bank.md`: candidate questions, not
promotions — promotion still requires a named RQ slot in
`PROJECT_STATUS.md`, a data plan that does not displace queue ranks, and
scope fit. IDs here are `C5-<tier>.<n>` to avoid colliding with Q1-Q6.

Every question below survived a devil's-advocate (examiner) round; the
scoping is deliberate, not decorative. Standing kills re-affirmed and
inherited by everything here: no per-token joule claims (~9 Hz sampler vs
~4 ms token cadence — chunked windows only), no unqualified absolute-joule
claims from modeled rails, no general intelligence-per-joule, claim
wording "on this M3 Max / MLX / powermetrics" until a second unit or lab
exists, and present-tense capability claims only for landed code (P2-010 scored suite is QUEUED,
not landed (D-014/P2-011 aggregation and P2-009 telemetry LANDED 2026-07-07)).
(Amendment 2026-07-08: the P2-010 substrate + affine core + generator
engine are now LANDED (PRs #17-#20, D-044..D-047); still not landed:
envelope-gate script, real-tokenizer manifests, all suite campaigns.)

## Why this instrument matters (steelman preamble, examiner-scoped)

**Auditability is the differentiator, not topic novelty.** Energy
benchmarks exist (MLPerf Power; TokenPowerBench; ML.ENERGY-style
datacenter work) — what does not exist is local-inference joules/token
that a skeptic can re-derive: JouleWise publishes self-contained bundles
where config, raw power trace, vendor telemetry, event log, and outputs
are preserved and `validate-bundle --strict` proves the summary re-reduces
identically from raw evidence. Energy tables are otherwise unauditable at
exactly the step that matters.

**Energy per request is becoming the binding constraint on local AI.**
Battery, thermal envelope, and sustained throughput all reduce to joules
per completed request. Latency says whether a local model feels fast
once; `energy_request_j` with uncertainty says whether it can run all day.
The instrument already resolves this at CV 0.3-1.4% across repetitions.

**Apple-Silicon unified memory is a clean window into the memory-bound
decode regime.** The measured 1.5B vs 122B-MoE pair showed energy/token
numerically aligning with the active-parameter ratio while decode power
stayed nearly flat (~23.5 → ~27.5 W). That is hypothesis-generating, not
a scaling result (see C5-1.1), but it demonstrates that the instrument can
see the shape of the regime that throughput benchmarks cannot.

**Negative results are structured data.** did-not-fit, throttle,

exec
/bin/zsh -lc "sed -n '551,660p' docs/research_question_bank.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
contaminated-idle, and cap-hit outcomes produce complete `unsupported` or
quality-flagged bundles. Competitors discard their failures; here the
feasibility frontier is itself a reportable dataset (this is how a
negative Hailo verdict stays a finding).

**The benchmark can referee efficiency claims.** Quantization, runtime,
and architecture "efficiency" claims mix latency, memory, and energy with
no common accounting. Typed configs + one reducer + named measurement
boundaries make within-boundary refereeing possible today and boundary-
labeled cross-target comparisons possible with planned hardware.

**Q4's fixed-vs-marginal model turns benchmark data into engineering
budgets.** `E = fixed + prefill(p) + decode(d)` per target/model/quant
lets an app team budget a workload distribution (an agent session, a RAG
pipeline) from benchmark coefficients — the bridge from instrument to
battery-life engineering.

**The split study is a first-of-kind edge measurement.** Prefill/decode
disaggregation is argued from datacenter throughput; nobody has measured
the ENERGY crossover on local links with both-end power sampling and
per-stage decomposition (prefill/serialize/transfer/deserialize/decode).
Either verdict — crossover exists or doesn't in range — is publishable.
(Examiner note, recorded as standing tension: this is also the most
hardware-gated item in the agenda; the feasibility-first Phase 3 ladder
is the mitigation.)

**The infrastructure outlives any single result.** Every future target is
forced through the same contract (config → bundle → strict re-reduction →
boundary-named summary). The M3 Max numbers are the demo; the reusable
referee is the contribution.

## TIER 1 — answerable with current hardware (M3 Max alone)

Landed software (P2-009 rich telemetry, P2-011 uncertainty
aggregation, 2M campaign tooling — all 2026-07-07) is available;
queued software (P2-010 scored suite) is assumed where noted; no new
hardware. (Amendment 2026-07-08: the suite substrate/ladder-core/
generators are landed, PRs #17-#20; campaign execution still pending.) Throughput reality: ~30-75 bundles/hour makes n=10-20 designs
cheap.

- **C5-1.1 Active-parameter energy scaling (the honest version of the
  122B observation).** Does decode energy/token scale with active rather
  than total parameters across dense and MoE models on one pinned stack?
  Measure on the named M3 Max / MLX / powermetrics SoC-rail boundary:
  gross decode-window joules, mean power, and throughput across 4-6 model
  points (dense 1.5B/7B/14B bridge + ≥2 MoE), same quant recipe, pinned MLX
  version, fixed shapes, n≥5 interleaved; fit gross mJ/token ~ active_params
  (+ total-param/KV covariates) with intervals. Any idle-subtracted result is
  a labeled within-device secondary sensitivity view, not the scaling
  headline (D-067).
  Hardware: now. Methodology: runtime is part of the condition — rerun
  after MLX updates as a separate condition. Threat: model families
  differ in more than active params; the dense bridge and quant pinning
  carry the inference. Who cares: efficient-ML and MoE architecture
  researchers; local-inference benchmark authors. Amendment 2026-07-08
  (C-014): with 4-6 model points, this supports descriptive L2 pairwise
  contrasts only unless the model set grows enough for a predeclared
  one-covariate fit; never fit active+total+KV covariates on 4-6 model
  points.

- **C5-1.2 Context-length energy scaling.** Where does measured energy
  stop being linear in prompt length? Measure: prefill/decode energy over
  prompt 128→8192 (fixed decode 64/256), n≥5; unsupported cells recorded.
  Hardware: now. Methodology: chunked windows; short-prompt prefill
  reported "unresolved at sampler resolution", never 0.03 J-style point
  claims. Threat: SoC boundary underrepresents unified-memory traffic —
  directional bias for long-context (examiner #11); flag pending Q6
  calibration. Who cares: long-context model teams, serving researchers.

- **C5-1.3 Phase-resolved compute-vs-memory signatures (uses landed P2-009 telemetry).**
  Does the rail mix and DVFS residency shift between compute-bound
  prefill and memory-bound decode, and how does the shift move with model
  size/quant? Measure: per-phase CPU:GPU energy division, GPU
  frequency/dvfm residency, idle_ratio across the 2M matrix. Hardware:
  now. Methodology: promotes the banked "CPU:GPU division by phase" item
  with the telemetry that makes it cheap. Threat: modeled rails — claims
  are about STRUCTURE (ratios, shifts), not absolute rail watts. Who
  cares: Apple/Metal/MLX performance engineers, systems-paper authors.

- **C5-1.4 DVFS residency as a throttling early-warning (uses landed P2-009 telemetry).**
  Do residency histograms and idle_ratio drift predict throttling before
  energy/throughput visibly degrade under sustained inference? Measure:
  20-60 min sustained blocks; per-rep energy, residency, cap-hit rates,
  recovery slopes; n≥5 blocks. Hardware: now. Methodology: cooldown-gate
  records and interleaving separate warmup, drift, and throttling.
  Threat: one chassis/ambient; report as within-target characterization.
  Who cares: laptop-inference tool builders, mobile/edge systems
  researchers, thermal-management teams.

- **C5-1.5 Cooldown-recovery curves and the energy tail (promotes banked
  item).** Recovery time and excess idle joules vs preceding run
  intensity; is the tail material to honest energy/request accounting?
  Measure: post-run recovery traces after an intensity ladder; time-to-
  baseline, cap-hit rate, excess joules; n≥5. Hardware: now. Threat:
  ambient sensitivity — record environment snapshots (P2-009). Who
  cares: on-device serving teams, benchmark methodology authors.

- **C5-1.6 Sampling-strategy energy overhead (power-gated).** Does
  temperature/top-p/beam sampling cost measurable energy beyond
  deterministic decoding at fixed output length? Measure: greedy vs
  sampled at fixed decode caps, recorded stop reasons; PRECONDITION:
  measured detection floor first; n≥10 paired ABBA. Hardware: now.
  Threat: plausibly below floor at n=5 — the null ("sampler choice is
  energy-free at this resolution") is the likely and still-reportable
  result. Who cares: runtime maintainers, generation-defaults tuning.

- **C5-1.7 Keep-warm vs reload breakeven (promotes banked cold-start
  item; harness extension).** Model-load joules, resident idle-power
  delta, cold-vs-warm TTFT → breakeven interarrival time per
  model/quant. Measure: load-window sampling (extension: measure outside

exec
/bin/zsh -lc "sed -n '661,770p' docs/research_question_bank.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
  current window), idle-resident deltas, n≥5. Hardware: now. Threat:
  idle-resident delta may be near the detection floor for small models;
  report identifiability. Model-load/warmup trace capture was reviewed and
  DEFERRED by C-015 (R2 items 14-15); it must land before any C5-1.7
  corpus. Who cares: desktop-assistant and agent-framework teams,
  serverless-inference researchers.

- **C5-1.8 Runtime energy attribution.** How much of measured inference
  energy belongs to the runtime, not the model? Same model artifact
  (where format permits) across MLX vs llama.cpp-Metal vs ollama on the
  same machine. Measure: energy/token, power, TTFT, rail mix over a
  shared shape grid, n≥5; artifact hashes and versions pinned. Hardware:
  now. Methodology: where formats force different artifacts (MLX vs
  GGUF), the comparison is stack-vs-stack, stated as such. Threat:
  version churn — this question is BUILT on the pinning discipline
  rather than wounded by it. Who cares: runtime maintainers, local-LLM
  users, model publishers choosing release formats.

  **2026-07-17 kernel-provenance rider (D-075).** Status: **candidate**;
  earliest phase: **NV**. On the 3080 Ti, same model artifact where format
  permits: llama.cpp-CUDA vs vLLM (TensorRT-LLM gated on Ampere-support
  verification) — how much energy variance tracks kernel-library identity vs
  runtime scheduler? Ceiling: **L2 stack-vs-stack**. Forbidden upgrade: **no
  `belongs to the kernel layer` language when artifacts/formats differ; no
  runtime-agnostic kernel claims**. This is an amendment to C5-1.8, not a new
  C5-1.13 thesis. Evidence: [2026-07-17 extension-axis
  evaluation](process_traces/2026-07-17-extension-axes/).

- **C5-1.9 MoE-vs-dense energy per correct answer, quarantined (needs
  P2-010).** Under the controlled-envelope ladder, do MoE and dense
  models at similar quality bands differ in energy per correct answer?
  Measure: affine_mod_ladder_v1 level-window energy + exact scoring;
  token/stop-reason distributions reported (EOS-bias audit). Hardware:
  now. Methodology: C-004 quarantine binds — correctness is an
  annotation; claim template "on this controlled ladder", never
  intelligence-per-joule. Who cares: MoE architecture teams, benchmark-
  methodology reviewers.

- **C5-1.10 The failure frontier as an energy dataset (promotes banked
  item).** Which model × quant × context cells fit, fail, swap, or
  throttle on 128 GB unified memory — with pre-failure energy and memory
  pressure recorded? Measure: full matrix including structured
  `unsupported` bundles, env snapshots. Hardware: now. Threat: one
  memory configuration; frame as the 128 GB-class frontier. Who cares:
  model release engineers, hardware buyers, benchmark authors.

- **C5-1.11 Dark-silicon rail utilization, systematized (promotes banked
  item; needs P2-009).** What fraction of the SoC's rails does each
  runtime/model pair energize (ANE-dark being the first quotable
  instance)? Measure: per-rail energy share and residency by phase
  across the runtime grid of C5-1.8. Hardware: now. Threat: modeled
  rails — report utilization structure, cross-checked against vendor
  combined_power. Who cares: accelerator vendors, runtime implementers.

- **C5-1.12 Quantization benefit decomposition, Mac leg.** For MLX quant
  variants of one family (4/8-bit), how much energy benefit is lower
  power vs shorter time? Measure: decode energy, mean power, throughput
  per quant at fixed shapes, n≥5. Hardware: now (extends to Tier 2 for
  CUDA/GGUF legs). Threat: quant recipes change outputs — greedy-diff
  and report divergence. Who cares: quantization researchers, edge
  deployment teams.

## Workload/query-set expansion (first-class topic, Tier 1 hardware)

Today's workloads are single-prompt fixed-shape grids plus the queued
affine ladder. (Amendment 2026-07-08: the affine ladder CORE is landed,
PRs #17-#20; the envelope-gate script and smoke campaign remain queued.) The council's workload lens designed the expansion; the
examiner frame was applied up front: at fixed token shape, most category
differences may collapse into token counts — that null is itself a
publishable result, named here the **Token-Shape Sufficiency Null**.

**Category taxonomy and expected energy mechanisms.** Six categories,
each with a mechanistic reason energy could differ and an honest
distinguishability call:
chat/instruction (high output-length variance under natural EOS; expected
NULL at fixed shape — the ecological baseline); code generation
(decode-heavy, distinct stop-reason behavior; near-null at fixed budget
unless tokenizer throughput differs on code tokens); summarization/
long-context (prefill-heavy, KV growth — YES, distinguishable via prefill
energy/TTFT/phase mix); reasoning/CoT (thinking-token inflation on
reasoning models — YES, the category effect most likely to be large,
directly measurable on the already-benchmarked Qwen3.5-122B); structured
JSON extraction (early valid-close stops make short answers cheap —
collapses at fixed envelope; probes EOS bias); multilingual (tokenizer
fertility differs sharply by script — YES when semantically matched,
expected null when token-matched; run BOTH, the pair separates fertility
from semantics).

**Realistic-vs-synthetic discipline (hybrid, both by design).**
Deterministic seed-derived synthetic profiles are the CONTROLS
(reproducible, shape-matched, redistribution-safe); pinned realistic
exemplars are the ecological probes (licensing/contamination/tokenizer
caveats recorded per source). Every realistic category runs in two modes:
`fixed_budget_exact` (greedy, EOS suppressed, fixed max_tokens — the
headline category-at-fixed-shape comparison) and `natural_eos` (greedy,
EOS allowed, stop reasons recorded — the operational-cost view). EOS-bias
rule inherited from C-004: natural termination is a workload property,
not a fairness control; wrong/short/refusal answers looking energy-cheap
must be visible in stop-reason distributions, never hidden.

**Sources to pin (hash-manifested frozen subsets, never "latest split"):**
LMSYS-Chat-1M for chat SHAPE distributions (terms-gated, not for
redistribution — derive synthetic shapes from it); HumanEval/MBPP-style
code prompts (MIT, contaminated — prompt exemplars only, no accuracy
claims); public-domain/government texts + synthetic needle controls for
summarization; GSM8K/MMLU-style items for reasoning shapes (MIT on HF,
contaminated — shape not correctness); synthetic fixed-schema records for
JSON; FLORES-200 for multilingual (CC BY-SA, parallel sentences enable
the semantic-matched leg). Where licenses are uncertain, synthetic wins.


exec
/bin/zsh -lc "sed -n '771,880p' docs/research_question_bank.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
**Concrete recommendation — `jw_mixed_v1` (adopt as the first official
workload expansion).** Amendment 2026-07-08 (C-014): this supersedes the
C-005 fixed-budget-full-first sequencing; the C-005 category/source
discipline otherwise remains intact. Phase 1 is the identification core:
all 6 categories at the common-shape identification stratum, `512/256`
`fixed_budget_exact`, synthetic + realistic where licensing is clean.
Phase 2 is a natural-EOS pilot with >=4 items/category on reasoning, JSON,
chat, and multilingual. Phase 3 is the full category panels, gated on
above-floor structure from Phases 1-2. The original full panel remains the
expansion target after the gate: 6 categories x 8 items = 48 items per
target/model/quant, n=5, categories interleaved round-robin, with the
C-005 category shapes (chat 512/256; code 4x512/256 + 4x1024/512;
summarization 4096/256; reasoning 512/512; JSON extraction 1024/128;
multilingual FLORES 8 languages semantic-matched then token-matched
512/256; ~240 bundles = 3-8 hours per target/model/quant at observed
throughput) unless the Phase 1/2 gate amends them. Harness needs (all additive): `workload_profile.category` +
`source_manifest` + sha256 + per-item `output_policy` fields; category as
a campaign-matrix axis alongside shape (never instead of it); per-item
stop reason/emitted-token/response hash in outputs; reuse P2-010a item
windows + identifiability flags; aggregation waits on P2-011. Out of
scope stays out: no accuracy evals, no judges, no retries — correctness
only as quarantined annotation. Category claims follow AP-4 in
`docs/contracts/analysis_plans.md`.
Amendment 2026-07-08 (D-046 and deferred-binding B6 disposition):
`jw.multiling` synthetic is phase-1 control material, not a C5-W.4 FLORES
replacement; the FLORES 6-vs-8 language count and token-matched
substitution decision are deferred to the FLORES/source session.

**Questions it unlocks (Tier 1):**

- **C5-W.1 Does category explain energy beyond token counts?** Paired
  synthetic controls vs realistic exemplars at identical shape; either a
  category effect or the Token-Shape Sufficiency Null — both reportable.
  Threat: small deltas need the detection floor first (examiner #2). The
  reportable comparison is AP-4 in `docs/contracts/analysis_plans.md`,
  using the common-shape stratum and the predeclared equivalence margin
  from C-014. Who cares: benchmark authors, app engineers budgeting
  features.
- **C5-W.2 Does thinking-token inflation dominate reasoning-model request
  energy?** Fixed-budget vs natural-EOS on the reasoning flagship;
  measures the energy price of "thinking" as output-length inflation.
  Who cares: reasoning-model teams, agent builders choosing modes.
- **C5-W.3 Is category energy-ranking stable across models and quants?**
  The workload-axis analogue of Q5; do code/long-context/reasoning flip
  the ordering? Who cares: procurement, model-selection tooling.
- **C5-W.4 Tokenizer fertility as an energy tax.** Semantic-matched vs
  token-matched multilingual pairs isolate joules attributable to
  tokenizer choice per script. Who cares: multilingual deployment,
  tokenizer designers.


## TIER 2 — unlocked by already-planned hardware gates

Gates by name: P1-006 device access (owned RTX 3050; Jetson Orin Nano),
the 3080 Ti borrow window (Phase 3 interconnect sweep only), P1-003 wall
meter decision (R-007), P1-004 network topology (1GbE / 2.5GbE / optional
10GbE).

- **C5-2.1 Quantization decomposition, cross-stack.** C5-1.12 extended
  to llama.cpp-CUDA/vLLM on the 3050: is the time-vs-watts split of
  quantization benefit hardware-dependent? Gate: P1-006. Threat:
  nvidia-smi board boundary ≠ SoC boundary — within-target decomposition
  first, cross-target only boundary-labeled. Who cares: quantization and
  runtime teams.

- **C5-2.2 Batch size and the prefill/decode energy split.** Does
  static batching reshape gross energy/request and the phase split under
  an interactive latency bound? Measure: B in {1,2,4,8,16}, group gross
  energy and gross joules/request within the named target/telemetry
  boundary, latency distribution, and structured memory-fit failures.
  The Mac leg is MINTED (2026-07-16: AXI-SB verdict `supported` on pinned
  mlx-lm 0.31.3, lead-run B∈{2,4} live probes with full per-request
  observability — `docs/specs/axi/sb_static_batch_verdict.md`); execution
  still requires the follow-on batch adapter row, P2-015 floors, and its own
  scheduled quiet-Mac block. The serving-style leg remains gated on P1-006.
  Continuous batching is a post-capstone extension (D-070).
  Who cares: serving researchers, scheduler developers.

- **C5-2.3 Predicted-vs-measured KV economics.** Does the analytic
  kv-size model predict serialized cache size, transfer energy, and
  deserialize energy? Measure: transfer joules/GiB both ends over
  payload ladder 16 MiB-2 GiB per link; deserialize windows; predicted
  vs actual deltas calibrate the model. Gates: P1-004 links + any second
  node (P1-006). Methodology: both-end sampling, clock-offset bounds
  flagged; this is the instrument's designed home turf. Who cares:
  disaggregated-inference researchers, KV-cache system builders.

- **C5-2.4 KV-cache quantization end-to-end.** Does q8_0 cache save
  energy after serialize/deserialize overhead, or only bytes? Gates:
  P1-006 + P1-004 (llama.cpp cache portability spike verdict). Who
  cares: llama.cpp maintainers, KV-compression researchers.

- **C5-2.5 Speculative decoding joules per ACCEPTED token (promotes
  banked item).** With/without draft model at output equivalence.
  Measure: total joules, acceptance rate, joules/accepted-token, n≥5.
  Gate: runtime support (MLX or 3050 stack). Methodology: the
  accepted-token denominator is the trap the harness's token accounting
  defuses. Who cares: speculative-decoding researchers, runtime teams.

  **2026-07-17 DSpark/DFlash candidate riders (D-075).** These remain
  riders on C5-2.5, not four independent theses; every effect is floor-gated
  and `C-023-OUTPUT-IDENTITY` is binding. Evidence for all four:
  [2026-07-17 extension-axis
  evaluation](process_traces/2026-07-17-extension-axes/).

  - **C5-2.5a — cross-method contrast.** Status: **candidate (deferred
    rider)**; earliest phase: **NS**. At matched target model, quantization,
    prompt roster, and output equivalence, do a fixed-K block-diffusion
    drafter (DFlash) and a variable-K confidence-scheduled drafter (DSpark)
    differ in gross request energy and gross J/committed-output-token on the

codex
The repo’s own research registry already places this direction at an L2 “stack-versus-stack” ceiling: if MLX and llama.cpp require different serialized weights, the honest claim cannot be “energy belongs to the runtime.” I’m now checking whether a same-source, matched-quantization design is technically attainable and how many additional nights it would actually cost.
exec
/bin/zsh -lc "sed -n '111,230p' docs/paper/draft-v1.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
exec
/bin/zsh -lc "rg -n -i 'llama\\.cpp|llama_cpp|gguf|mlx|runtime energy|runtime.*contrast|phase.*event|prefill|decode' docs joulewise adapters configs tests | head -n 500" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
\[
\text{effective clearable effect}=F_{\mathrm{cell}}+B_{\mathrm{claim}},
\]

where \(B_{\mathrm{claim}}\) is the claim-side measurement bound. For the measured phase-contrast regime, this combined bar is approximately 5 J. Neither term may be removed as an apparent double count. Effects below the floor are reported as *not resolvable*, not as zero, equal, or evidence of no difference. A directional claim is made only when the effect and its interval clear the applicable bar.

## 5. Fail-closed collection protocol (C-iii)

*Fail-closed* means that missing, inconsistent, stale, or contaminated evidence produces a refusal rather than an optimistic default. The collection unit is one uninterrupted two-to-four-hour window with one power state, one instrument identity, fresh calibration before and after, a fresh drift-bound corpus, and one verdict over the exact member set. Work that does not fit with at least a 20% failure margin is split prospectively into another independently calibrated window.

### Pre-registration and admission

Before quiet time, the operator freezes the run identifiers, membership, stage order, comparison definitions, calibration retry count, acceptance thresholds, extraction specification, code revision, and an initially empty waiver list. Every configuration is validated and dry-run against a fresh output root. These choices are made before outcomes are visible. Pre-registration here is executable: the launcher and final verifier check the frozen values rather than relying on a narrative promise.

Each stage then passes admission gates immediately before measurement. The approved power supply and power policy must be unchanged; displays must be asleep; the screensaver and low-power mode must be off; thermal pressure must be nominal; and central- and graphics-processor activity must meet the quiet-state criteria. Known background work is allowed to finish before the window, followed by a settling interval, rather than being ignored during analysis. Runtime and telemetry identities, clock anchoring, sample cadence, calibration freshness, and post-run environment observations are also checked. No environment override can produce a claim-bearing member.

### Counterbalanced order

Comparisons use A/B/B/A blocks, abbreviated **ABBA**. Conditions A and B are measured in the order A, B, B, A, with ordinary cooldown between members. Averaging the two outer A observations and the two inner B observations cancels a linear time trend within the block to first order. For null-floor calibration, A and B are aliases of the exact same configuration and payload, so any nonzero block delta is a false comparative effect. For scientific contrasts, the A and B definitions are frozen in advance, and the contrast is computed within each block before blocks are aggregated. ABBA reduces common drift; it does not replace the measured whole-window drift allowance.

### Evidence custody and refusals

Every member is a self-contained bundle of configuration, raw power trace, runtime events, environment observations, and derived summary. Cryptographic hashes bind those files to the campaign manifest. Failed or interrupted artifacts are never deleted or overwritten. An occupied retry slot is moved to a quarantine area outside the active runs root; the exact member is recollected only under an allowed retry; and an append-only supersession record names which occurrence governs. Two present bundles for one occurrence refuse. The final whole-window verdict binds the exact member-occurrence set, calibration bracket, policy, and drift evidence by hash, so a later consumer cannot silently select a more favorable subset.

Collection does not continue indefinitely through environmental interruptions. Each stage attempt stops at its first member failure, and after the same cause fails a window stage for the third time the window itself closes rather than being retried; in actual operation, nights with three environmental member interruptions were closed and preserved as salvage rather than repeatedly retried. The surviving data may remain diagnostic, but it becomes claim-bearing only if the pre-registered verdict and extraction rules accept the exact resulting basis. This abandon-after-three rule limits outcome-dependent retrying and makes the cost of a noisy environment visible.

The custody chain continues after collection. The immutable corpus is backed up before extraction. The extractor re-authenticates member hashes, required files and cross-file consistency, calibration identity, environment admission, complete campaign membership, cooldown evidence, phase metric identity, and the whole-window drift allowance. It excludes or refuses a cell according to the frozen rules; missing uncertainty never becomes zero. The current artifact boundary is stated honestly: until floor artifacts are independently bound to their source extraction, a claim-bearing floor must be produced by protocol-controlled extraction in the same controlled custody session as the analysis that consumes it. A standalone floor file is not independently claim-licensing.

The refusal log is part of the evaluation, not an embarrassment to omit. It records contaminated members, out-of-family calibration, stale drift evidence, unresolved clock anchors, duplicate occurrences, and below-floor effects. In one real end-of-night case, the governed re-evaluation refused a window because a member's internal clock alignment could not be resolved. Independent adjudication found that refusal correct. The result remained non-claim-bearing: an example of the fail-closed design working as intended, not a software defect to be bypassed.

## 6. Instrument characterization (C-iv)

Instrument characterization asks whether the complete measurement system behaves predictably when driven by signals whose qualitative answer is known in advance. The workload is therefore a test signal, not yet the scientific finding. All tests retain the same calibration, admission, custody, and floor rules as the later demonstration measurements. Existing campaign fragments are not promoted where the governing whole-window verdict did not pass; the table marks the required claim-bearing results explicitly.

| Property | Characterization method | What a passing result would establish | Claim-bearing result |
|---|---|---|---|
| Linearity | Hold the prompt profile fixed and ramp the requested output from 128 to 2048 tokens. Regress gross request and decode energy on the runtime-observed output count; inspect residual structure as well as the fitted slope. | Energy responds proportionally over the tested dynamic range, and the fitted per-token slope can serve as the known-effect standard for floor probes on this stack. It would not establish linearity outside the tested range or on another stack. | **[PENDING WINDOW C]** |
| Null response across magnitudes | Run identical A-equals-B ABBA blocks at short, medium, and long output magnitudes. Evaluate the paired deltas against zero and against the predicted decision envelopes. | The comparison path does not create a directional effect merely because total energy or duration changes, and false contrasts across the tested range are contained by the error model. A non-significant result alone is insufficient; the interval must be interpreted relative to the floor. | **[PENDING WINDOW C]** |
| Empirical floor verification | Use the pre-registered linearity slope to create micro-deltas with predicted effects near 0.5, 1, 1.5, and 3 times the declared floor. Test positive and negative directions in counterbalanced blocks. | Sub-floor effects are refused while sufficiently super-floor effects clear in both directions. This is an operational check of the detection boundary, not a validation of the counter's absolute gain. | **[PENDING WINDOW C]** |
| Phase-attribution causal consistency | First compare the sum of separately integrated phase energies with the gross energy over their enclosing request. Then vary output length while holding prompt tokens fixed and fit the slope of prefill energy against output length. | Phase accounting is additive within its stated boundaries, and energy assigned to prefill does not acquire a systematic dependence on work that occurs later in decode. Together these tests challenge both missing energy and cross-phase leakage. | **[PENDING WINDOW C]** |
| Drift and settling | Place long controlled holds and fixed reference workloads through the window, including start, midpoint, and end references. After operator or stage activity, repeat the reference while recording the time required for thermal and admission observables to stabilize; compare it with the 180 s operating convention. | The measured drift trajectory is contained by the published allowance, and the chosen settling time is supported or revised from observed recovery rather than convenience. Endpoint agreement alone is not enough if the midpoint reveals curvature. | **[PENDING WINDOW C]** |
| Between-session stability | Repeat calibrations, null blocks, and floor cells across at least three sessions or days with the full stack identity recorded. | The calibration and floor are stable enough to reuse only under their declared freshness and identity rules, or reveal that a new session must mint a new floor. | **[PENDING WINDOW C]** |

Linearity and the null ladder test complementary failure modes. A smooth response can still carry an offset, and a zero-centered null can coexist with a nonlinear scale. The micro-delta experiment then closes the loop by using the measured slope to place effects deliberately below and above the declared decision boundary. Success requires the instrument to refuse the former and resolve the latter in both directions; merely observing larger effects with larger workloads is not sufficient.

The causal tests address the most important phase-specific risk. Additivity checks conservation inside the declared request boundary: phase intervals should reconcile with the enclosing total, subject to explicitly labeled setup or gap intervals. Causal invariance checks direction: holding the prompt fixed while increasing later decode work should not change energy attributed to earlier prefill. A nonzero prefill slope would indicate boundary leakage, shared-state coupling that invalidates the simple phase model, or both; it would narrow the claim rather than be explained away.

Temporal characterization separates slow drift from thermal settling. Start, midpoint, and end references expose whole-window curvature, while post-transition references estimate how long the system takes to return to its admitted state after operator activity or stage churn. Repetition across days tests whether one session's calibration is representative under identical recorded bindings. Internal channel-sum versus package reconciliation is retained as a secondary consistency check. External wall-power regression remains conditional on a suitable meter and would validate totals only; the pulse experiment remains the evidence for phase splitting.

Every resulting figure and table will identify the physical unit, operating-system version and build, runtime and relevant library versions, model artifact hash, quantization, tokenizer identity, sampler and output policy, configured and realized batch/concurrency policy, measurement boundary, and telemetry backend. Silent omission is not permitted. Measurements support stack-specific conclusions only; independent replication or a calibrated boundary bridge would be required for hardware-class, vendor-class, or cross-boundary rankings.

## 7. Demonstration results (C-v)

**[RESULT PENDING RE-MINT]**

This section will report phase-resolved gross joules per request for two model sizes, with tokenizer-scoped joules per prompt token and per output token as companion metrics. It will contain the pre-registered same-boundary model-size contrast, its interval, the complete floor decomposition, the claim-side bound, the effect-to-floor ratio, and the final resolvable/unresolved verdict. No demonstration energy value from the superseded mint is carried into this draft. A quantization ladder will be included only if it is collected under its own stack-specific floors and the frozen window budget permits it.

## 8. Related work

### LLM inference energy measurement

TokenPowerBench provides one of the closest reporting structures: it separates prompt-processing and token-generation energy, uses phase-appropriate token denominators, and groups results by context length [TokenPowerBench]. Its disclosed method, however, does not specify the boundary events, alignment rule, repetition and variance protocol, idle baseline, or external validation, and continuous batching makes an “active phase” label difficult to interpret when requests overlap. JouleWise adopts phase-specific reporting but restricts its primary scope to one sequential request, where runtime-emitted phase boundaries are well posed and can be calibrated.

The Illusion of Power Capping in LLM Decode samples graphics-processor power, integrates those samples, repeats configurations, and cross-checks sufficiently long operations against a separate hardware energy counter [IllusionPowerCapping]. This is a stronger measurement template than an unqualified software reading. Its counter agreement, run-to-run variation, snapshot fallback, and timing alignment nevertheless remain separate diagnostics rather than one bound on the reported effect, and its long sweeps do not use a drift-control ordering. JouleWise composes those classes of uncertainty into a decision rule for each contrast.

Apple-focused system comparisons reinforce the need for boundary labels. Silicon Showdown compares a graphics-board boundary on one platform with a whole-system-on-chip `powermetrics` boundary on Apple hardware, while runtimes and precision stacks also differ [SiliconShowdown]. Intelligence-per-Watt and ML.ENERGY similarly emphasize breadth across deployed inference configurations [IntelligencePerWatt; MLENERGY]. Such studies answer valuable systems questions, but unlike boundaries and software stacks cannot by themselves support a hardware-class causal ranking. JouleWise therefore makes the named stack and measurement boundary part of every result and prioritizes within-boundary effects.

### Software power counters and measurement standards

RAPL in Action established a validation agenda for commodity software counters: align lag before comparing streams, model wall power rather than assuming identity, account for temporal correlation, warm the system, measure sampler overhead, and inspect update granularity, overflow, jitter, and timestamp behavior [RAPLInAction]. Jay and Ostapenco likewise regress software readings against wall power and show that disagreement varies with load; they avoid claims about subtotals that the reference meter cannot observe [JayOstapenco]. JouleWise follows this epistemic boundary. A future external meter could test total gain and load dependence, but it would not validate how a total is divided between prefill and decode. The in-window pulse train addresses that distinct question.

MLPerf Power and SPEC require load-specific analyzer uncertainty, fixed ranges, clock synchronization, minimum intervals, invalid-sample accounting, and controlled battery behavior [MLPerfPower]. JouleWise translates their per-run reject-on-missing-evidence principle to a consumer software counter. The difference is that its principal uncertainty is not only an analyzer specification; it includes whether samples at a software-defined phase edge belong inside or outside the integral.

### Metrology and experimental discipline

Prospective paired minimum-detectable-effect methods estimate the smallest effect a planned paired study has adequate statistical power to find. They size the study from the variance of paired differences and can impose a one-way prior ratchet: observed variability may raise the planned threshold but may not lower it after outcomes are seen [PairedMDE]. JouleWise uses that logic for prospective workload sizing, but it does not treat the worst-case attribution term as independent random noise. Root-sum-square composition would be anti-conservative for a systematic edge-placement bound. Instead, the analysis maximizes over calibrated edge positions, measures drift with bracketed references, and publishes the resulting floor with the effect.

This emphasis changes the role of failed runs. A rejected admission, stale calibration, contaminated member, or below-floor contrast is evidence about the instrument's operating domain. Hash-bound raw traces, runtime events, configurations, supersessions, verdicts, and pre-registration records make that evidence re-reducible. The refusal is retained rather than disappearing behind a final average.

### Split and disaggregated inference

Split, or disaggregated, inference places prompt processing and token generation on different devices and transfers intermediate state between them. Revisiting Disaggregation Energy reports that the energy outcome depends on load, baseline, and transfer conditions on its evaluated two-graphics-processor node [RevisitingDisaggregationEnergy]. DualScale studies phase placement and per-phase power control on homogeneous server hardware [DualScale]. Prima.cpp includes whole-run energy and communication accounting but not a per-stage energy split [PrimaCPP], while SplitZip characterizes lossless transfer compression without making an energy claim [SplitZip].

JouleWise does not claim a new split scheduler in this paper. Split inference is instead a demanding future demonstration of the instrument because it introduces two physical boundaries, a transfer interval, and clock alignment across devices. A valid comparison would have to measure both ends, name each boundary, and clear a pre-registered floor or calibrated bridge. Whether splitting saves energy remains an empirical outcome; the reusable contribution is a method that can issue, qualify, or refuse the result.

exec
/bin/zsh -lc "rg --files | rg '("'^adapters/|runtime|llama|mlx|campaign|phase)'"' | head -n 400" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
rg: adapters: No such file or directory (os error 2)
tests/test_quiet_guard_process.py:169:    def test_pid_zero_kernel_fixture_decodes_inventories_and_derives_candidates(self) -> None:
tests/test_quiet_guard_process.py:182:        decoded = SysctlDarwinProcessReader.decode_kernel_table(payload)
tests/test_quiet_guard_process.py:196:        self.assertEqual(table, decoded)
tests/test_quiet_guard_process.py:249:                SysctlDarwinProcessReader.decode_kernel_table(payload)
tests/test_quiet_guard_process.py:336:    def test_exact_decoder_preserves_true_argv_boundaries(self) -> None:
tests/test_axi_mock_spec.py:18:from joulewise.axi_decode_config import TargetTokenizerIdentity
tests/test_axi_mock_spec.py:224:            "synchronization_policy": "barrier_before_prefill",
tests/test_axi_mock_spec.py:332:            (None, "exact_token_match", "matched_decoded_work", []),
docs/phase_1/phase_1_exit_checklist.md:41:  `sudo -n` verified, MLX installed and generating (see instrumentation
docs/phase_1/phase_1_exit_checklist.md:56:| Mac runtime (MLX) | complete (2026-07-06) | Install path decided; install or documented procedure | Instrumentation section below (installed in `.venv`, versions pinned, real generation verified via Slice 2G) |
docs/phase_1/phase_1_exit_checklist.md:95:- Can the Hailo toolchain compile any autoregressive decoder-only model?
docs/phase_1/phase_1_exit_checklist.md:98:- Is there a supported runtime path for repeated token-by-token decode?
docs/phase_1/phase_1_exit_checklist.md:118:- A documented compile attempt of a real decoder-only LLM on the 8-class
docs/phase_1/phase_1_exit_checklist.md:125:  zero decoder-only LLMs; its transformers are all vision/embedding
docs/phase_1/phase_1_exit_checklist.md:134:  Whisper encoder-decoder demo; only the decoder-only autoregressive
docs/phase_1/phase_1_exit_checklist.md:139:Per-question answers: toolchain cannot compile decoder-only models (parse
docs/phase_1/phase_1_exit_checklist.md:141:attention only, no KV-cache access pattern; no token-by-token decode
docs/phase_1/phase_1_exit_checklist.md:147:Pi 5 + Hailo-8L, compile any small decoder-only ONNX (GPT-2/TinyLlama)
docs/phase_1/phase_1_exit_checklist.md:188:controller node; prefill node; decode node; switch model (or direct
docs/phase_1/phase_1_exit_checklist.md:238:10GbE is in scope; identify controller/prefill/decode nodes per
docs/phase_1/phase_1_exit_checklist.md:255:- Runtime target: MLX. Telemetry target: powermetrics. Transport: local.
docs/phase_1/phase_1_exit_checklist.md:272:  - Python import checks: `mlx` and `mlx_lm` not installed in the current
docs/phase_1/phase_1_exit_checklist.md:280:python3 -c "import importlib.util; print(importlib.util.find_spec('mlx') is not None)"
docs/phase_1/phase_1_exit_checklist.md:310:  - [x] MLX install path decided (dedicated venv, `[mac]` extra) —
docs/phase_1/phase_1_exit_checklist.md:313:  - [x] MLX/MLX-LM installed or installation procedure documented —
docs/phase_1/phase_1_exit_checklist.md:314:    `mlx` 0.31.2, `mlx_lm` 0.31.3, `transformers` 5.12.1. Compat
docs/phase_1/phase_1_exit_checklist.md:315:    finding: `transformers` 5.13.0 breaks `mlx_lm` 0.31.3 at import
docs/phase_1/phase_1_exit_checklist.md:317:    pins `mlx-lm>=0.31.3` + `transformers<5.13`. Real generation
docs/phase_1/phase_1_exit_checklist.md:319:    (`example-mac-mlx-mock-telemetry`, 265.8 tok/s through the full
docs/phase_1/phase_1_exit_checklist.md:331:- Runtime target: vLLM (llama.cpp-CUDA fallback per Slice 2K). Telemetry:
docs/phase_1/phase_1_exit_checklist.md:339:  - [ ] vLLM install path (or llama.cpp-CUDA decision recorded).
docs/phase_1/phase_1_exit_checklist.md:390:Phase 2 must NOT start with: live MLX/powermetrics integration,
joulewise/quiet_guard_process.py:29:# byte-accurate kinfo_proc rows at these offsets so decoder drift fails closed.
joulewise/quiet_guard_process.py:405:    """Decode Darwin KERN_PROC_ALL and exact candidate sysctl material."""
joulewise/quiet_guard_process.py:493:    def _decode_row(payload: bytes, offset: int = 0) -> KernelProcessRecord:
joulewise/quiet_guard_process.py:508:    def decode_kernel_table(cls, payload: bytes) -> KernelProcessTable:
joulewise/quiet_guard_process.py:512:            cls._decode_row(payload, offset)
joulewise/quiet_guard_process.py:528:            return self.decode_kernel_table(payload)
joulewise/quiet_guard_process.py:556:        row = self._decode_row(payload)
joulewise/quiet_guard_process.py:578:        executable = payload[cursor:executable_end].decode("utf-8", "surrogateescape")
joulewise/quiet_guard_process.py:587:            arguments.append(payload[cursor:end].decode("utf-8", "surrogateescape"))
configs/floor_mint/a10_extraction_spec.json:5:      "cell_id": "df-ph-prefill-absolute",
configs/floor_mint/a10_extraction_spec.json:7:      "metric": "phase_energy_j.prefill",
configs/floor_mint/a10_extraction_spec.json:11:          "slot": "p2015-df-ph-prefill-abs-r01",
configs/floor_mint/a10_extraction_spec.json:12:          "bundle_id": "p2015-df-ph-prefill-abs-r01"
configs/floor_mint/a10_extraction_spec.json:15:          "slot": "p2015-df-ph-prefill-abs-r02",
configs/floor_mint/a10_extraction_spec.json:16:          "bundle_id": "p2015-df-ph-prefill-abs-r02"
configs/floor_mint/a10_extraction_spec.json:19:          "slot": "p2015-df-ph-prefill-abs-r03",
configs/floor_mint/a10_extraction_spec.json:20:          "bundle_id": "p2015-df-ph-prefill-abs-r03"
configs/floor_mint/a10_extraction_spec.json:23:          "slot": "p2015-df-ph-prefill-abs-r04",
configs/floor_mint/a10_extraction_spec.json:24:          "bundle_id": "p2015-df-ph-prefill-abs-r04"
configs/floor_mint/a10_extraction_spec.json:27:          "slot": "p2015-df-ph-prefill-abs-r05",
configs/floor_mint/a10_extraction_spec.json:28:          "bundle_id": "p2015-df-ph-prefill-abs-r05"
configs/floor_mint/a10_extraction_spec.json:31:          "slot": "p2015-df-ph-prefill-abs-r06",
configs/floor_mint/a10_extraction_spec.json:32:          "bundle_id": "p2015-df-ph-prefill-abs-r06"
configs/floor_mint/a10_extraction_spec.json:35:          "slot": "p2015-df-ph-prefill-abs-r07",
configs/floor_mint/a10_extraction_spec.json:36:          "bundle_id": "p2015-df-ph-prefill-abs-r07"
configs/floor_mint/a10_extraction_spec.json:39:          "slot": "p2015-df-ph-prefill-abs-r08",
configs/floor_mint/a10_extraction_spec.json:40:          "bundle_id": "p2015-df-ph-prefill-abs-r08"
configs/floor_mint/a10_extraction_spec.json:43:          "slot": "p2015-df-ph-prefill-abs-r09",
configs/floor_mint/a10_extraction_spec.json:44:          "bundle_id": "p2015-df-ph-prefill-abs-r09"
configs/floor_mint/a10_extraction_spec.json:47:          "slot": "p2015-df-ph-prefill-abs-r10",
configs/floor_mint/a10_extraction_spec.json:48:          "bundle_id": "p2015-df-ph-prefill-abs-r10"
configs/floor_mint/a10_extraction_spec.json:53:      "cell_id": "df-ph-decode-absolute",
configs/floor_mint/a10_extraction_spec.json:55:      "metric": "phase_energy_j.decode",
configs/floor_mint/a10_extraction_spec.json:57:      "condition_family_id": "df-ph-decode",
configs/floor_mint/a10_extraction_spec.json:60:          "condition_family_id": "df-ph-decode",
configs/floor_mint/a10_extraction_spec.json:63:            "condition_family_id": "df-ph-decode",
configs/floor_mint/a10_extraction_spec.json:65:              "name": "df_ph_decode",
configs/floor_mint/a10_extraction_spec.json:72:              "metric": "phase_energy_j.decode",
configs/floor_mint/a10_extraction_spec.json:83:          "slot": "p2015-df-ph-decode-abs-r01",
configs/floor_mint/a10_extraction_spec.json:84:          "bundle_id": "p2015-df-ph-decode-abs-r01"
configs/floor_mint/a10_extraction_spec.json:87:          "slot": "p2015-df-ph-decode-abs-r02",
configs/floor_mint/a10_extraction_spec.json:88:          "bundle_id": "p2015-df-ph-decode-abs-r02"
configs/floor_mint/a10_extraction_spec.json:91:          "slot": "p2015-df-ph-decode-abs-r03",
configs/floor_mint/a10_extraction_spec.json:92:          "bundle_id": "p2015-df-ph-decode-abs-r03"
configs/floor_mint/a10_extraction_spec.json:95:          "slot": "p2015-df-ph-decode-abs-r04",
configs/floor_mint/a10_extraction_spec.json:96:          "bundle_id": "p2015-df-ph-decode-abs-r04"
configs/floor_mint/a10_extraction_spec.json:99:          "slot": "p2015-df-ph-decode-abs-r05",
configs/floor_mint/a10_extraction_spec.json:100:          "bundle_id": "p2015-df-ph-decode-abs-r05"
configs/floor_mint/a10_extraction_spec.json:103:          "slot": "p2015-df-ph-decode-abs-r06",
configs/floor_mint/a10_extraction_spec.json:104:          "bundle_id": "p2015-df-ph-decode-abs-r06"
configs/floor_mint/a10_extraction_spec.json:107:          "slot": "p2015-df-ph-decode-abs-r07",
configs/floor_mint/a10_extraction_spec.json:108:          "bundle_id": "p2015-df-ph-decode-abs-r07"
configs/floor_mint/a10_extraction_spec.json:111:          "slot": "p2015-df-ph-decode-abs-r08",
configs/floor_mint/a10_extraction_spec.json:112:          "bundle_id": "p2015-df-ph-decode-abs-r08"
configs/floor_mint/a10_extraction_spec.json:115:          "slot": "p2015-df-ph-decode-abs-r09",
configs/floor_mint/a10_extraction_spec.json:116:          "bundle_id": "p2015-df-ph-decode-abs-r09"
configs/floor_mint/a10_extraction_spec.json:119:          "slot": "p2015-df-ph-decode-abs-r10",
configs/floor_mint/a10_extraction_spec.json:120:          "bundle_id": "p2015-df-ph-decode-abs-r10"
configs/floor_mint/a10_extraction_spec.json:125:      "cell_id": "df-ph-short-prefill-absolute",
configs/floor_mint/a10_extraction_spec.json:127:      "metric": "phase_energy_j.prefill",
configs/floor_mint/a10_extraction_spec.json:131:          "slot": "p2015-df-ph-short-prefill-abs-r01",
configs/floor_mint/a10_extraction_spec.json:132:          "bundle_id": "p2015-df-ph-short-prefill-abs-r01"
configs/floor_mint/a10_extraction_spec.json:135:          "slot": "p2015-df-ph-short-prefill-abs-r02",
configs/floor_mint/a10_extraction_spec.json:136:          "bundle_id": "p2015-df-ph-short-prefill-abs-r02"
configs/floor_mint/a10_extraction_spec.json:139:          "slot": "p2015-df-ph-short-prefill-abs-r03",
configs/floor_mint/a10_extraction_spec.json:140:          "bundle_id": "p2015-df-ph-short-prefill-abs-r03"
configs/floor_mint/a10_extraction_spec.json:143:          "slot": "p2015-df-ph-short-prefill-abs-r04",
configs/floor_mint/a10_extraction_spec.json:144:          "bundle_id": "p2015-df-ph-short-prefill-abs-r04"
configs/floor_mint/a10_extraction_spec.json:147:          "slot": "p2015-df-ph-short-prefill-abs-r05",
configs/floor_mint/a10_extraction_spec.json:148:          "bundle_id": "p2015-df-ph-short-prefill-abs-r05"
configs/floor_mint/a10_extraction_spec.json:151:          "slot": "p2015-df-ph-short-prefill-abs-r06",
configs/floor_mint/a10_extraction_spec.json:152:          "bundle_id": "p2015-df-ph-short-prefill-abs-r06"
configs/floor_mint/a10_extraction_spec.json:155:          "slot": "p2015-df-ph-short-prefill-abs-r07",
configs/floor_mint/a10_extraction_spec.json:156:          "bundle_id": "p2015-df-ph-short-prefill-abs-r07"
configs/floor_mint/a10_extraction_spec.json:159:          "slot": "p2015-df-ph-short-prefill-abs-r08",
configs/floor_mint/a10_extraction_spec.json:160:          "bundle_id": "p2015-df-ph-short-prefill-abs-r08"
configs/floor_mint/a10_extraction_spec.json:163:          "slot": "p2015-df-ph-short-prefill-abs-r09",
configs/floor_mint/a10_extraction_spec.json:164:          "bundle_id": "p2015-df-ph-short-prefill-abs-r09"
configs/floor_mint/a10_extraction_spec.json:167:          "slot": "p2015-df-ph-short-prefill-abs-r10",
configs/floor_mint/a10_extraction_spec.json:168:          "bundle_id": "p2015-df-ph-short-prefill-abs-r10"
tests/test_environment.py:223:            if distribution == "mlx":
tests/test_environment.py:232:            snapshot["python_packages"]["mlx"],
tests/test_environment.py:236:            snapshot["python_packages"]["mlx-lm"],
tests/test_environment.py:246:            if distribution == "mlx":
tests/test_environment.py:260:                "mlx": {"present": True, "version": "1.2.3"},
tests/test_environment.py:261:                "mlx-lm": {"present": False, "version": None},
tests/test_environment.py:308:            {"mlx", "mlx-lm", "transformers"},
tests/test_environment.py:606:                self.assertEqual(set(value), {"mlx", "mlx-lm", "transformers"})
tests/test_environment.py:661:                self.assertEqual(set(value), {"mlx", "mlx-lm", "transformers"})
tests/test_cli.py:177:                "mlx_lm.stream_generate"
tests/test_cli.py:190:            self.assertIn("decode token-event count 8 does not equal emitted_tokens 7", output)
tests/test_audit_bundle_validation.py:291:                "phase": "decode",
tests/test_audit_bundle_validation.py:292:                "message": "decode started",
tests/test_audit_bundle_validation.py:317:                "phase": "decode",
tests/test_audit_bundle_validation.py:318:                "message": f"{event_type} decode",
tests/test_audit_bundle_validation.py:322:                (0.25, "phase_start", "prefill"),
tests/test_audit_bundle_validation.py:323:                (0.5, "phase_start", "decode"),
tests/test_audit_bundle_validation.py:324:                (1.25, "phase_end", "prefill"),
tests/test_audit_bundle_validation.py:325:                (1.5, "phase_end", "decode"),
configs/floor_mint/window_c_extraction_spec.json:5:      "cell_id": "df-cmp-abba-ph-decode",
configs/floor_mint/window_c_extraction_spec.json:7:      "metric": "phase_energy_j.decode",
configs/floor_mint/window_c_extraction_spec.json:9:      "condition_family_id": "df-ph-decode",
configs/floor_mint/window_c_extraction_spec.json:12:          "condition_family_id": "df-ph-decode",
configs/floor_mint/window_c_extraction_spec.json:15:            "condition_family_id": "df-ph-decode",
configs/floor_mint/window_c_extraction_spec.json:17:              "name": "df_ph_decode",
configs/floor_mint/window_c_extraction_spec.json:24:              "metric": "phase_energy_j.decode",
configs/floor_mint/window_c_extraction_spec.json:33:          "condition_family_id": "df-ph-decode",
configs/floor_mint/window_c_extraction_spec.json:36:            "condition_family_id": "df-ph-decode",
configs/floor_mint/window_c_extraction_spec.json:38:              "name": "df_ph_decode",
configs/floor_mint/window_c_extraction_spec.json:45:              "metric": "phase_energy_j.decode",
configs/floor_mint/window_c_extraction_spec.json:56:          "block_id": "df-cmp-abba-ph-decode-b01",
configs/floor_mint/window_c_extraction_spec.json:58:            "A1": "p2015-df-cmp-abba-ph-decode-b01-a1",
configs/floor_mint/window_c_extraction_spec.json:59:            "B1": "p2015-df-cmp-abba-ph-decode-b01-b1",
configs/floor_mint/window_c_extraction_spec.json:60:            "B2": "p2015-df-cmp-abba-ph-decode-b01-b2",
configs/floor_mint/window_c_extraction_spec.json:61:            "A2": "p2015-df-cmp-abba-ph-decode-b01-a2"
configs/floor_mint/window_c_extraction_spec.json:65:          "block_id": "df-cmp-abba-ph-decode-b02",
configs/floor_mint/window_c_extraction_spec.json:67:            "A1": "p2015-df-cmp-abba-ph-decode-b02-a1",
configs/floor_mint/window_c_extraction_spec.json:68:            "B1": "p2015-df-cmp-abba-ph-decode-b02-b1",
configs/floor_mint/window_c_extraction_spec.json:69:            "B2": "p2015-df-cmp-abba-ph-decode-b02-b2",
configs/floor_mint/window_c_extraction_spec.json:70:            "A2": "p2015-df-cmp-abba-ph-decode-b02-a2"
configs/floor_mint/window_c_extraction_spec.json:74:          "block_id": "df-cmp-abba-ph-decode-b03",
configs/floor_mint/window_c_extraction_spec.json:76:            "A1": "p2015-df-cmp-abba-ph-decode-b03-a1",
configs/floor_mint/window_c_extraction_spec.json:77:            "B1": "p2015-df-cmp-abba-ph-decode-b03-b1",
configs/floor_mint/window_c_extraction_spec.json:78:            "B2": "p2015-df-cmp-abba-ph-decode-b03-b2",
configs/floor_mint/window_c_extraction_spec.json:79:            "A2": "p2015-df-cmp-abba-ph-decode-b03-a2"
configs/floor_mint/window_c_extraction_spec.json:83:          "block_id": "df-cmp-abba-ph-decode-b04",
configs/floor_mint/window_c_extraction_spec.json:85:            "A1": "p2015-df-cmp-abba-ph-decode-b04-a1",
configs/floor_mint/window_c_extraction_spec.json:86:            "B1": "p2015-df-cmp-abba-ph-decode-b04-b1",
configs/floor_mint/window_c_extraction_spec.json:87:            "B2": "p2015-df-cmp-abba-ph-decode-b04-b2",
configs/floor_mint/window_c_extraction_spec.json:88:            "A2": "p2015-df-cmp-abba-ph-decode-b04-a2"
configs/floor_mint/window_c_extraction_spec.json:92:          "block_id": "df-cmp-abba-ph-decode-b05",
configs/floor_mint/window_c_extraction_spec.json:94:            "A1": "p2015-df-cmp-abba-ph-decode-b05-a1",
configs/floor_mint/window_c_extraction_spec.json:95:            "B1": "p2015-df-cmp-abba-ph-decode-b05-b1",
configs/floor_mint/window_c_extraction_spec.json:96:            "B2": "p2015-df-cmp-abba-ph-decode-b05-b2",
configs/floor_mint/window_c_extraction_spec.json:97:            "A2": "p2015-df-cmp-abba-ph-decode-b05-a2"
configs/floor_mint/window_c_extraction_spec.json:101:          "block_id": "df-cmp-abba-ph-decode-b06",
configs/floor_mint/window_c_extraction_spec.json:103:            "A1": "p2015-df-cmp-abba-ph-decode-b06-a1",
configs/floor_mint/window_c_extraction_spec.json:104:            "B1": "p2015-df-cmp-abba-ph-decode-b06-b1",
configs/floor_mint/window_c_extraction_spec.json:105:            "B2": "p2015-df-cmp-abba-ph-decode-b06-b2",
configs/floor_mint/window_c_extraction_spec.json:106:            "A2": "p2015-df-cmp-abba-ph-decode-b06-a2"
configs/floor_mint/window_c_extraction_spec.json:110:          "block_id": "df-cmp-abba-ph-decode-b07",
configs/floor_mint/window_c_extraction_spec.json:112:            "A1": "p2015-df-cmp-abba-ph-decode-b07-a1",
configs/floor_mint/window_c_extraction_spec.json:113:            "B1": "p2015-df-cmp-abba-ph-decode-b07-b1",
configs/floor_mint/window_c_extraction_spec.json:114:            "B2": "p2015-df-cmp-abba-ph-decode-b07-b2",
configs/floor_mint/window_c_extraction_spec.json:115:            "A2": "p2015-df-cmp-abba-ph-decode-b07-a2"
configs/floor_mint/window_c_extraction_spec.json:119:          "block_id": "df-cmp-abba-ph-decode-b08",
configs/floor_mint/window_c_extraction_spec.json:121:            "A1": "p2015-df-cmp-abba-ph-decode-b08-a1",
configs/floor_mint/window_c_extraction_spec.json:122:            "B1": "p2015-df-cmp-abba-ph-decode-b08-b1",
configs/floor_mint/window_c_extraction_spec.json:123:            "B2": "p2015-df-cmp-abba-ph-decode-b08-b2",
configs/floor_mint/window_c_extraction_spec.json:124:            "A2": "p2015-df-cmp-abba-ph-decode-b08-a2"
configs/floor_mint/window_c_extraction_spec.json:128:          "block_id": "df-cmp-abba-ph-decode-b09",
configs/floor_mint/window_c_extraction_spec.json:130:            "A1": "p2015-df-cmp-abba-ph-decode-b09-a1",
configs/floor_mint/window_c_extraction_spec.json:131:            "B1": "p2015-df-cmp-abba-ph-decode-b09-b1",
configs/floor_mint/window_c_extraction_spec.json:132:            "B2": "p2015-df-cmp-abba-ph-decode-b09-b2",
configs/floor_mint/window_c_extraction_spec.json:133:            "A2": "p2015-df-cmp-abba-ph-decode-b09-a2"
configs/floor_mint/window_c_extraction_spec.json:137:          "block_id": "df-cmp-abba-ph-decode-b10",
configs/floor_mint/window_c_extraction_spec.json:139:            "A1": "p2015-df-cmp-abba-ph-decode-b10-a1",
configs/floor_mint/window_c_extraction_spec.json:140:            "B1": "p2015-df-cmp-abba-ph-decode-b10-b1",
configs/floor_mint/window_c_extraction_spec.json:141:            "B2": "p2015-df-cmp-abba-ph-decode-b10-b2",
configs/floor_mint/window_c_extraction_spec.json:142:            "A2": "p2015-df-cmp-abba-ph-decode-b10-a2"
tests/test_validate_gate_packet.py:113:        receipt = json.loads(completed.stdout.decode("utf-8"))
tests/test_validate_gate_packet.py:216:        with self.assertRaises(json.JSONDecodeError):
tests/test_validate_gate_packet.py:217:            json.loads(completed.stdout.decode("utf-8"))
tests/test_validate_gate_packet.py:284:                receipt = json.loads(output.decode("utf-8"))
tests/test_validate_gate_packet.py:551:                receipt = json.loads(completed.stdout.decode("utf-8"))
tests/test_validate_gate_packet.py:582:                receipt = json.loads(completed.stdout.decode("utf-8"))
tests/test_validate_gate_packet.py:647:                receipt = json.loads(completed.stdout.decode("utf-8"))
tests/test_validate_gate_packet.py:690:                receipt = json.loads(completed.stdout.decode("utf-8"))
tests/test_pack_capsule.py:31:def decode_gzip_base64(value):
tests/test_pack_capsule.py:32:    return gzip.decompress(base64.b64decode(value)).decode("utf-8")
tests/test_pack_capsule.py:35:def decode_ts_string_expression(expression):
tests/test_pack_capsule.py:302:        emitted_shared = decode_ts_string_expression(shared_expr)
tests/test_pack_capsule.py:305:        emitted_shards = [decode_ts_string_expression(match.group("expr")) for match in expression_re.finditer(shard_block)]
tests/test_pack_capsule.py:313:        shared = json.loads(decode_gzip_base64(emitted_shared))
tests/test_pack_capsule.py:314:        decoded_pages = {}
tests/test_pack_capsule.py:316:            decoded_pages.update(json.loads(decode_gzip_base64(shard)))
tests/test_pack_capsule.py:317:        self.assertEqual(decoded_pages, {"/process-fetch.html": original})
tests/test_pack_capsule.py:321:        reconstructed = decoded_pages["/process-fetch.html"].replace(
tests/test_pack_capsule.py:328:        self.assertLessEqual(stats["first_request_decode"], pack_capsule.MAX_FIRST_REQUEST_DECODE_BYTES)
tests/test_pack_capsule.py:339:    def test_real_server_decoder_roundtrips_emitted_shard_and_rejects_corruption(self):
tests/test_pack_capsule.py:353:                    "const names=['atob','btoa','ReadableStream','DecompressionStream','TextDecoder'];"
tests/test_pack_capsule.py:391:            harness_path = temp_path / "decode-harness.ts"
tests/test_pack_capsule.py:392:            compiled_path = temp_path / "decode-harness.mjs"
tests/test_pack_capsule.py:405:            decoder_start = server_source.index("function base64ToBytes")
tests/test_pack_capsule.py:406:            decoder_end = server_source.index("\nlet decodedShared", decoder_start)
tests/test_pack_capsule.py:407:            decoder_source = server_source[decoder_start:decoder_end]
tests/test_pack_capsule.py:409:                r"^const decodedShards = .+;$", server_source, flags=re.MULTILINE
tests/test_pack_capsule.py:425:                + decoder_source
tests/test_pack_capsule.py:432:const decoded = await loadShard(route.shard);
tests/test_pack_capsule.py:433:const page = decoded["/known.html"];
tests/test_pack_capsule.py:434:if (typeof page !== "string") throw new Error("known page missing after decode");
tests/test_pack_capsule.py:441:decodedShards.clear();
tests/test_pack_capsule.py:448:if (!corruptRaised) throw new Error("corrupted shard decoded without error");
tests/test_pack_capsule.py:449:if (decodedShards.has(route.shard)) throw new Error("failed shard remained cached");
tests/test_pack_capsule.py:487:            base64.b64encode(known_html.encode("utf-8")).decode("ascii"),
tests/test_pack_capsule.py:543:    def test_runtime_decode_budget_fails_closed(self):
tests/test_pack_capsule.py:544:        pack_capsule.enforce_runtime_decode_budget(
tests/test_pack_capsule.py:545:            {"first_request_decode": pack_capsule.MAX_FIRST_REQUEST_DECODE_BYTES}
tests/test_pack_capsule.py:548:            pack_capsule.enforce_runtime_decode_budget(
tests/test_pack_capsule.py:549:                {"first_request_decode": pack_capsule.MAX_FIRST_REQUEST_DECODE_BYTES + 1}
tests/test_pack_capsule.py:922:                encoded = base64.b64encode(source).decode("ascii")
tests/test_pack_capsule.py:1151:        self.assertEqual(inlined.count(base64.b64encode(b"same-font").decode("ascii")), 1)
tests/test_pack_capsule.py:1209:    def test_server_decodes_bounded_shards_and_reinserts_shared_freshness(self):
tests/test_pack_capsule.py:1231:        self.assertIn('throw new Error("gzip decode read bound reached");', server)
tests/test_codex_bridge_observer.py:104:            except json.JSONDecodeError:
tests/goldens/d078_r01_reducer_052.json:2:  "decode_latency_s": 0.23061418533325195,
tests/goldens/d078_r01_reducer_052.json:54:    "/phase_energy_j/decode": {
tests/goldens/d078_r01_reducer_052.json:74:    "/phase_energy_j/prefill": {
tests/goldens/d078_r01_reducer_052.json:153:      "decode": "identifiable",
tests/goldens/d078_r01_reducer_052.json:155:      "prefill": "not_resolvable_sample_count",
tests/goldens/d078_r01_reducer_052.json:167:    "decode": 4.746097552270651,
tests/goldens/d078_r01_reducer_052.json:169:    "prefill": 2.9164673801465035,
tests/goldens/d078_r01_reducer_052.json:223:      "decode": {
tests/goldens/d078_r01_reducer_052.json:285:      "prefill": {
tests/goldens/d078_r01_reducer_052.json:359:        "decode_phase_output_throughput_tokens_s"
tests/test_bundle.py:222:    def event(self, event_type: str = "stage_started", phase: str = "validate") -> RuntimeEvent:
tests/test_bundle.py:227:            message=f"{phase} {event_type}",
tests/goldens/axi_controller_request_events.jsonl:3:{"event_type":"phase_start","message":"prefill started","metadata":{"batch_group_id":null,"request_event_ordinal":2,"request_id":"request-000","request_input_id":"prompt-000","request_ordinal":0,"request_phase_ordinal":0,"request_roster_sha256":"502b0c4577aee495623a33332a26be956b8b3d01d1cb3d0d225382f6bc2130f9","scheduler_step_id":null,"source_identity":"mock"},"phase":"prefill","timestamp_s":1001.1}
tests/goldens/axi_controller_request_events.jsonl:4:{"event_type":"phase_end","message":"prefill ended","metadata":{"batch_group_id":null,"request_event_ordinal":3,"request_id":"request-000","request_input_id":"prompt-000","request_ordinal":0,"request_phase_ordinal":0,"request_roster_sha256":"502b0c4577aee495623a33332a26be956b8b3d01d1cb3d0d225382f6bc2130f9","scheduler_step_id":null,"source_identity":"mock"},"phase":"prefill","timestamp_s":1001.6}
tests/goldens/axi_controller_request_events.jsonl:5:{"event_type":"phase_start","message":"decode started","metadata":{"batch_group_id":null,"request_event_ordinal":4,"request_id":"request-000","request_input_id":"prompt-000","request_ordinal":0,"request_phase_ordinal":1,"request_roster_sha256":"502b0c4577aee495623a33332a26be956b8b3d01d1cb3d0d225382f6bc2130f9","scheduler_step_id":null,"source_identity":"mock"},"phase":"decode","timestamp_s":1001.8}
tests/goldens/axi_controller_request_events.jsonl:6:{"event_type":"decode_emission","message":"decode emission","metadata":{"batch_group_id":null,"decode_step_ordinal":0,"emitted_count":2,"emitted_token_ids":[10,11],"emitted_token_ids_sha256":"f671a4f1da57e650c97f6ed69bc4f11148add2067f2702d5ad8c346dc81325f4","output_token_start_ordinal":0,"request_event_ordinal":5,"request_id":"request-000","request_input_id":"prompt-000","request_ordinal":0,"request_roster_sha256":"502b0c4577aee495623a33332a26be956b8b3d01d1cb3d0d225382f6bc2130f9","scheduler_step_id":"step-000","source_identity":"mock","target_emitted_count":1,"tokens_accepted":1,"tokens_proposed":2},"phase":"decode","timestamp_s":1002.0}
tests/goldens/axi_controller_request_events.jsonl:7:{"event_type":"token","message":"token callback","metadata":{"batch_group_id":null,"decode_step_ordinal":0,"output_token_ordinal":0,"request_event_ordinal":6,"request_id":"request-000","request_input_id":"prompt-000","request_ordinal":0,"request_roster_sha256":"502b0c4577aee495623a33332a26be956b8b3d01d1cb3d0d225382f6bc2130f9","scheduler_step_id":"step-000","source_identity":"mock","timestamp_provenance":"runtime_per_token_callback","token_id":10},"phase":"decode","timestamp_s":1002.0}
tests/goldens/axi_controller_request_events.jsonl:8:{"event_type":"token","message":"token callback","metadata":{"batch_group_id":null,"decode_step_ordinal":0,"output_token_ordinal":1,"request_event_ordinal":7,"request_id":"request-000","request_input_id":"prompt-000","request_ordinal":0,"request_roster_sha256":"502b0c4577aee495623a33332a26be956b8b3d01d1cb3d0d225382f6bc2130f9","scheduler_step_id":"step-000","source_identity":"mock","timestamp_provenance":"runtime_per_token_callback","token_id":11},"phase":"decode","timestamp_s":1002.1}
tests/goldens/axi_controller_request_events.jsonl:9:{"event_type":"decode_emission","message":"decode emission","metadata":{"batch_group_id":null,"decode_step_ordinal":1,"emitted_count":1,"emitted_token_ids":[12],"emitted_token_ids_sha256":"7ee6707f942ff845b80748bbc66fab08a138fd716383cbf15319cff9c9efc4cd","output_token_start_ordinal":2,"request_event_ordinal":8,"request_id":"request-000","request_input_id":"prompt-000","request_ordinal":0,"request_roster_sha256":"502b0c4577aee495623a33332a26be956b8b3d01d1cb3d0d225382f6bc2130f9","scheduler_step_id":"step-001","source_identity":"mock","target_emitted_count":0,"tokens_accepted":1,"tokens_proposed":2},"phase":"decode","timestamp_s":1002.5}
tests/goldens/axi_controller_request_events.jsonl:10:{"event_type":"token","message":"token callback","metadata":{"batch_group_id":null,"decode_step_ordinal":1,"output_token_ordinal":2,"request_event_ordinal":9,"request_id":"request-000","request_input_id":"prompt-000","request_ordinal":0,"request_roster_sha256":"502b0c4577aee495623a33332a26be956b8b3d01d1cb3d0d225382f6bc2130f9","scheduler_step_id":"step-001","source_identity":"mock","timestamp_provenance":"runtime_per_token_callback","token_id":12},"phase":"decode","timestamp_s":1002.5}
tests/goldens/axi_controller_request_events.jsonl:11:{"event_type":"phase_end","message":"decode ended","metadata":{"batch_group_id":null,"request_event_ordinal":10,"request_id":"request-000","request_input_id":"prompt-000","request_ordinal":0,"request_phase_ordinal":1,"request_roster_sha256":"502b0c4577aee495623a33332a26be956b8b3d01d1cb3d0d225382f6bc2130f9","scheduler_step_id":null,"source_identity":"mock"},"phase":"decode","timestamp_s":1002.8}
tests/test_controller.py:86:        ("phase_start", "prefill"),
tests/test_controller.py:87:        ("phase_end", "prefill"),
tests/test_controller.py:88:        ("phase_start", "decode"),
tests/test_controller.py:90:    + [("token", "decode")] * 8
tests/test_controller.py:92:        ("phase_end", "decode"),
tests/test_controller.py:1128:        sequence = [(event["event_type"], event["phase"]) for event in events]
tests/test_controller.py:1158:        self.assertEqual(set(summary.phase_energy_j), {"prefill", "decode"})
tests/test_controller.py:2503:        bundle_dir = self.runs_root / "synthetic-prefill-node"
tests/test_controller.py:2509:            run_id="synthetic-prefill-node",
tests/test_controller.py:2514:            node_role="prefill",
tests/test_controller.py:2516:        self.assertEqual(context.node_role, "prefill")
tests/test_controller.py:2584:            "decode_latency_s",
tests/test_controller.py:2620:            "decode_latency_s",
tests/test_aggregate.py:23:    "decode_latency_s",
tests/test_aggregate.py:418:            _summary(1.0, phase_energy_j={"prefill": 10.0, "decode": 20.0}),
tests/test_aggregate.py:423:            _summary(2.0, phase_energy_j={"prefill": 12.0}),
tests/test_aggregate.py:428:        self.assertIn("phase_energy_j.prefill", aggregate["metrics"])
tests/test_aggregate.py:429:        self.assertIn("phase_energy_j.decode", aggregate["metrics"])
tests/test_aggregate.py:431:            aggregate["metrics"]["phase_energy_j.prefill"]["repetitions"], 2
tests/test_aggregate.py:435:        prefill = aggregate["metrics"]["phase_energy_j.prefill"]
tests/test_aggregate.py:436:        self.assertAlmostEqual(prefill["mean"], 11.0, places=12)
tests/test_aggregate.py:437:        self.assertAlmostEqual(prefill["stddev"], expected_stddev, places=12)
tests/test_aggregate.py:438:        self.assertAlmostEqual(prefill["lower"], 11.0 - expected_half_width, places=12)
tests/test_aggregate.py:439:        self.assertAlmostEqual(prefill["upper"], 11.0 + expected_half_width, places=12)
tests/test_aggregate.py:440:        self.assertEqual(aggregate["metrics"]["phase_energy_j.decode"]["repetitions"], 1)
tests/test_aggregate.py:441:        self.assertEqual(aggregate["metrics"]["phase_energy_j.decode"]["mean"], 20.0)
tests/test_aggregate.py:443:            aggregate["metrics"]["phase_energy_j.decode"]["missing"],
tests/test_aggregate.py:503:                "decode_latency_s": 1.5,
tests/test_aggregate.py:519:                "decode_latency_s": 2.5,
tests/test_aggregate.py:536:            "decode_latency_s": 2.0,
tests/test_aggregate.py:552:            _summary(1.0, phase_energy_j={"prefill": 10.0, "decode": "bad"}),
tests/test_aggregate.py:557:            _summary(2.0, phase_energy_j={"decode": 5.0}),
tests/test_aggregate.py:564:        prefill = aggregate["metrics"]["phase_energy_j.prefill"]
tests/test_aggregate.py:565:        decode = aggregate["metrics"]["phase_energy_j.decode"]
tests/test_aggregate.py:567:        self.assertTrue(prefill["partial_metric"])
tests/test_aggregate.py:568:        self.assertEqual(prefill["repetitions"], 1)
tests/test_aggregate.py:570:            prefill["missing"],
tests/test_aggregate.py:573:        self.assertTrue(decode["partial_metric"])
tests/test_aggregate.py:574:        self.assertEqual(decode["repetitions"], 1)
tests/test_aggregate.py:576:            decode["missing"],
tests/test_axi_schemas.py:10:from joulewise.axi_decode_config import (
tests/test_axi_schemas.py:26:    DecodeCounterRollup,
tests/test_axi_schemas.py:29:    RequestDecodeMetric,
tests/test_axi_schemas.py:52:    rollup = DecodeCounterRollup(
tests/test_axi_schemas.py:59:    request = RequestDecodeMetric(
tests/test_axi_schemas.py:64:        decode_duration_s=2.0,
tests/test_axi_schemas.py:66:        decode_phase_output_throughput_tokens_s=1.5,
tests/test_axi_schemas.py:67:        decode_emission_event_count=2,
tests/test_axi_schemas.py:68:        decode_counter_rollup=rollup,
tests/test_axi_schemas.py:82:        decode_latency_s=2.0,
tests/test_axi_schemas.py:99:                "decode": "identifiable",
tests/test_axi_schemas.py:103:        phase_energy_j={"decode": 6.0},
tests/test_axi_schemas.py:105:        decode_counter_rollup=rollup,
tests/test_axi_schemas.py:109:        decode_phase_output_throughput_tokens_s=1.5,
tests/test_axi_schemas.py:110:        decode_emission_event_rate_events_s=1.0,
tests/test_axi_schemas.py:111:        decode_emission_burst_size_mean_tokens=1.5,
tests/test_axi_schemas.py:112:        decode_emission_burst_size_p50_tokens=1.5,
tests/test_axi_schemas.py:113:        decode_emission_burst_size_p95_tokens=1.95,
tests/test_axi_schemas.py:114:        decode_emission_burst_size_max_tokens=2,
tests/test_axi_schemas.py:115:        request_decode_metrics=[request],
tests/test_axi_schemas.py:121:        import joulewise.axi_decode_config as axi_config
tests/test_axi_schemas.py:154:            ("batch.sync", lambda v: v["batch_policy"].__setitem__("synchronization_policy", "barrier_before_prefill")),
tests/test_axi_schemas.py:240:        emission_path = GOLDEN / "axi_decode_emission.json"
tests/test_axi_schemas.py:259:        event = load(GOLDEN / "axi_decode_emission.json")
tests/test_axi_schemas.py:264:        event = load(GOLDEN / "axi_decode_emission.json")
tests/test_axi_schemas.py:271:                "scheduler_step_id", "decode_step_ordinal",
tests/test_axi_schemas.py:285:        event = load(GOLDEN / "axi_decode_emission.json")
tests/test_axi_schemas.py:330:        object.__setattr__(changed.decode_counter_rollup, "acceptance_rate", 0.0)
tests/test_axi_schemas.py:341:        self.assertFalse(schema["$defs"]["decode_counter_rollup"]["additionalProperties"])
tests/test_axi_schemas.py:342:        self.assertFalse(schema["$defs"]["request_decode_metric"]["additionalProperties"])
tests/test_axi_schemas.py:355:        payload["decode_counter_rollup"]["mean_rate"] = 0.5
docs/phase_1/phase_1_plan.md:23:the Mac MLX + powermetrics vertical slice.
docs/phase_1/phase_1_plan.md:109:identified; MLX/MLX-LM not installed. The rest needs a local user auth
docs/phase_1/phase_1_plan.md:122:decide and record the MLX install path (dedicated venv, `[mac]` extra).
docs/phase_1/phase_1_plan.md:130:Fallback: if MLX installation is not approved, record `pending_install`
docs/phase_1/phase_1_plan.md:164:Actions: record the physical topology (controller/prefill/decode nodes,
docs/phase_1/phase_1_plan.md:221:install blocker (vLLM vs llama.cpp-CUDA per the 2K fallback); telemetry
tests/test_generate_matrix.py:17:    (ROOT / "configs" / "examples" / "mac_mlx_local.json", "qwen25-1p5b"),
tests/test_generate_matrix.py:18:    (ROOT / "configs" / "examples" / "mac_mlx_qwen35_122b.json", "qwen35-122b"),
tests/test_mint_floor_artifact.py:68:        "runtime_version": "mlx-test",
tests/test_mint_floor_artifact.py:75:        "measurement_boundary_label": "phase-decode",
tests/test_mint_floor_artifact.py:82:    def _mlx_file_set_evidence() -> tuple[dict, dict]:
tests/test_mint_floor_artifact.py:90:        raw_config, metadata = self._mlx_file_set_evidence()
tests/test_mint_floor_artifact.py:105:    def test_mint_and_claim_stack_identity_are_bit_identical_for_mlx_file_set(
tests/test_mint_floor_artifact.py:108:        raw_config, metadata = self._mlx_file_set_evidence()
tests/test_mint_floor_artifact.py:119:        self.assertIn("mlx_version", prepare)
tests/test_mint_floor_artifact.py:142:        raw_config, metadata = self._mlx_file_set_evidence()
tests/test_mint_floor_artifact.py:168:        raw_config, metadata = self._mlx_file_set_evidence()
tests/test_mint_floor_artifact.py:177:        prepare["version"] = prepare["mlx_version"]
tests/test_mint_floor_artifact.py:188:        raw_config, metadata = self._mlx_file_set_evidence()
tests/test_mint_floor_artifact.py:198:        prepare.pop("mlx_version", None)
tests/test_mint_floor_artifact.py:199:        prepare.pop("mlx_lm_version", None)
tests/test_mint_floor_artifact.py:215:        raw_config, metadata = self._mlx_file_set_evidence()
tests/test_mint_floor_artifact.py:659:                "phase_energy_j": {"decode": float(index)},
tests/test_mint_floor_artifact.py:661:                    "/phase_energy_j/decode": {
tests/test_mint_floor_artifact.py:673:                        "decode": {
tests/test_mint_floor_artifact.py:816:                    "phase_energy_j": {"decode": metric_value},
tests/test_mint_floor_artifact.py:818:                        "/phase_energy_j/decode": {
tests/test_mint_floor_artifact.py:830:                            "decode": {
tests/test_mint_floor_artifact.py:944:    def test_authenticated_replay_does_not_import_prefill_refusal(
tests/test_mint_floor_artifact.py:952:                    ("phase", "prefill"): (
tests/test_mint_floor_artifact.py:965:                    "phase_energy_j": {"decode": 10.0},
tests/test_mint_floor_artifact.py:1000:                    ("phase", "decode"): (
tests/test_mint_floor_artifact.py:1013:                    "phase_energy_j": {"decode": 10.0},
tests/test_mint_floor_artifact.py:1490:            "phase_energy_j": {"decode": row["metric_value_j"]},
tests/test_mint_floor_artifact.py:1492:                "/phase_energy_j/decode": {
tests/test_mint_floor_artifact.py:1675:            summary["phase_energy_j"]["decode"] += 1.0
configs/floor_mint/condition_family_df_ph_decode.json:3:  "condition_family_id": "df-ph-decode",
configs/floor_mint/condition_family_df_ph_decode.json:5:    "name": "df_ph_decode",
configs/floor_mint/condition_family_df_ph_decode.json:12:    "metric": "phase_energy_j.decode",
tests/test_cli_run.py:60:    "example-mac-mlx-local__r1",
tests/test_cli_run.py:190:            ("mlx", "mock", SystemClock),
tests/test_cli_run.py:191:            ("mlx", "powermetrics", SystemClock),
tests/test_calibration_bracketing.py:109:Pd5+u&9OGGUFmh7S}7qm?)S5gd3@($!bZLZ%3zN{o`Eye+1*UM5*tj*_5>G;>ly+(56r%&5FoXDBP3qZ1_taJhsb@o>;hVnRvN(L
tests/test_calibration_bracketing.py:162:    raw = zlib.decompress(base64.b85decode(encoded))
tests/test_calibration_bracketing.py:1110:        changed["mlx_version"] = "different-but-exactly-t1-matched"
docs/phase_1/2k_live_verification_checklist.md:78:   not viable on this node, record the decision point for llama.cpp-CUDA
joulewise/report.py:229:_PHASE_COLORS = {"prefill": "#f4a259", "decode": "#5b8e7d"}
joulewise/report.py:237:    summary excluded. The D-026 measured window and the ``prefill``/``decode``
joulewise/report.py:386:    except (OSError, UnicodeDecodeError):
joulewise/report.py:393:        except json.JSONDecodeError:
tests/test_mock_adapters.py:153:            "decode_level": "short",
tests/test_mock_adapters.py:241:        self.assertEqual(len(events), 12)  # 4 phase events + 8 token events
tests/test_mock_adapters.py:243:            [(event.event_type, event.phase) for event in events],
tests/test_mock_adapters.py:244:            [("phase_start", "prefill"), ("phase_end", "prefill"), ("phase_start", "decode")]
tests/test_mock_adapters.py:245:            + [("token", "decode")] * 8
tests/test_mock_adapters.py:246:            + [("phase_end", "decode")],
tests/test_mock_adapters.py:259:        # run end: 1000 + 32 ms prefill + 8 x 10 ms decode
tests/test_mock_adapters.py:417:        item_phase_events = [
tests/test_mock_adapters.py:421:            and event.phase in {"prefill", "decode"}
tests/test_mock_adapters.py:423:        for event in item_phase_events:
tests/test_mock_adapters.py:866:    def test_mlx_runtime_failure_names_backend_and_mac_extra(self) -> None:
tests/test_mock_adapters.py:867:        config = make_config(hardware_target={"runtime_backend": "mlx"})
tests/test_mock_adapters.py:877:        self.assertIn("mlx", failure.message)
tests/test_mock_adapters.py:880:    def test_resolves_mlx_runtime_adapter_without_importing_mlx_lm(self) -> None:
tests/test_mock_adapters.py:881:        config = make_config(hardware_target={"runtime_backend": "mlx"})
tests/test_mock_adapters.py:884:        self.assertEqual(adapter.name, "mlx")
tests/test_mock_adapters.py:899:        for backend in ("llama_cpp", "hailo"):
tests/test_experiment.py:1546:    def test_cli_decoded_non_object_anchor_writes_terminal_verdict(self) -> None:
configs/examples/mock_axi_spec.json:57:    "joulewise.axi_decode_config.v1"
tests/goldens/axi_summary_v061.json:3:  "decode_counter_rollup": {
tests/goldens/axi_summary_v061.json:10:  "decode_emission_burst_size_max_tokens": 2,
tests/goldens/axi_summary_v061.json:11:  "decode_emission_burst_size_mean_tokens": 1.5,
tests/goldens/axi_summary_v061.json:12:  "decode_emission_burst_size_p50_tokens": 1.5,
tests/goldens/axi_summary_v061.json:13:  "decode_emission_burst_size_p95_tokens": 1.95,
tests/goldens/axi_summary_v061.json:14:  "decode_emission_event_rate_events_s": 2.0,
tests/goldens/axi_summary_v061.json:15:  "decode_latency_s": 0.5,
tests/goldens/axi_summary_v061.json:16:  "decode_phase_output_throughput_tokens_s": 3.0,
tests/goldens/axi_summary_v061.json:65:      "decode": "not_resolvable_sample_count",
tests/goldens/axi_summary_v061.json:67:      "prefill": "not_resolvable_sample_count"
tests/goldens/axi_summary_v061.json:78:    "decode": 10.0,
tests/goldens/axi_summary_v061.json:79:    "prefill": 5.0
tests/goldens/axi_summary_v061.json:81:  "request_decode_metrics": [
tests/goldens/axi_summary_v061.json:87:      "decode_counter_rollup": {
tests/goldens/axi_summary_v061.json:94:      "decode_duration_s": 1.0,
tests/goldens/axi_summary_v061.json:95:      "decode_emission_event_count": 2,
tests/goldens/axi_summary_v061.json:96:      "decode_phase_output_throughput_tokens_s": 3.0,
tests/goldens/axi_summary_v061.json:157:      "decode": {
tests/goldens/axi_summary_v061.json:187:      "prefill": {
configs/analysis_registry/slice_2m_ap2.v1.json:34:      "metric_tag": "gross_prefill",
configs/analysis_registry/slice_2m_ap2.v1.json:35:      "name": "phase_energy_j.prefill",
configs/analysis_registry/slice_2m_ap2.v1.json:41:      "metric_tag": "gross_decode",
configs/analysis_registry/slice_2m_ap2.v1.json:42:      "name": "phase_energy_j.decode",
tests/test_axi_sb_spike.py:34:            "prefill_started": True,
tests/test_axi_sb_spike.py:35:            "prefill_ended": True,
tests/test_axi_sb_spike.py:36:            "decode_started": True,
tests/test_axi_sb_spike.py:37:            "decode_ended": True,
tests/test_axi_sb_spike.py:103:        versions = {"mlx-lm": spike.EXPECTED_MLX_LM, "mlx": spike.EXPECTED_MLX}
tests/test_axi_sb_spike.py:119:    def test_import_is_mlx_free(self) -> None:
tests/test_axi_sb_spike.py:120:        self.assertNotIn("mlx", spike.__dict__)
tests/test_axi_sb_spike.py:121:        self.assertNotIn("mlx_lm", spike.__dict__)
tests/test_axi_sb_spike.py:155:    def test_missing_per_request_phase_hooks_is_event_observability_failure(self) -> None:
tests/test_axi_sb_spike.py:212:        versions = {"mlx-lm": spike.EXPECTED_MLX_LM, "mlx": spike.EXPECTED_MLX}
tests/test_axi_sb_spike.py:238:            versions = {"mlx-lm": spike.EXPECTED_MLX_LM, "mlx": spike.EXPECTED_MLX}
tests/test_axi_sb_spike.py:278:            versions = {"mlx-lm": spike.EXPECTED_MLX_LM, "mlx": spike.EXPECTED_MLX}
tests/test_axi_sb_spike.py:329:            versions = {"mlx-lm": spike.EXPECTED_MLX_LM, "mlx": spike.EXPECTED_MLX}
tests/test_axi_sb_spike.py:394:        mlx = ModuleType("mlx")
tests/test_axi_sb_spike.py:395:        mlx.__path__ = []  # type: ignore[attr-defined]
tests/test_axi_sb_spike.py:396:        mlx_core = ModuleType("mlx.core")
tests/test_axi_sb_spike.py:397:        mlx_core.metal = SimpleNamespace(is_available=lambda: True)  # type: ignore[attr-defined]
tests/test_axi_sb_spike.py:398:        mlx_core.get_peak_memory = lambda: 1  # type: ignore[attr-defined]
tests/test_axi_sb_spike.py:399:        mlx.core = mlx_core  # type: ignore[attr-defined]
tests/test_axi_sb_spike.py:400:        mlx_lm = ModuleType("mlx_lm")
tests/test_axi_sb_spike.py:401:        mlx_lm.__path__ = []  # type: ignore[attr-defined]
tests/test_axi_sb_spike.py:402:        mlx_lm.load = lambda _model: (fake_model, FakeTokenizer())  # type: ignore[attr-defined]
tests/test_axi_sb_spike.py:403:        mlx_lm_generate = ModuleType("mlx_lm.generate")
tests/test_axi_sb_spike.py:404:        mlx_lm_generate.BatchGenerator = FakeBatchGenerator  # type: ignore[attr-defined]
tests/test_axi_sb_spike.py:405:        mlx_lm.generate = mlx_lm_generate  # type: ignore[attr-defined]
tests/test_axi_sb_spike.py:409:            "mlx": mlx,
tests/test_axi_sb_spike.py:410:            "mlx.core": mlx_core,
tests/test_axi_sb_spike.py:411:            "mlx_lm": mlx_lm,
tests/test_axi_sb_spike.py:412:            "mlx_lm.generate": mlx_lm_generate,
tests/test_axi_sb_spike.py:436:            versions = {"mlx-lm": spike.EXPECTED_MLX_LM, "mlx": spike.EXPECTED_MLX}
tests/test_p2038_production_path.py:3:This CI test uses a mock runtime only to avoid an MLX dependency. Telemetry is
tests/test_p2038_production_path.py:108:        "python_packages": {"mlx": {"version": "p2038-test-mlx"}},
tests/test_p2038_production_path.py:164:        "mlx_version": "p2038-test-mlx",
tests/test_p2038_production_path.py:381:            lifecycle = [(event["event_type"], event["phase"]) for event in events]
tests/test_p2038_production_path.py:663:            event_rows = [json.loads(line) for line in originals["events"].decode().splitlines()]
joulewise/powermetrics_fiducial.py:17:up to one cadence of bias); MLX dispatch/fence latency stays inside the bound
joulewise/powermetrics_fiducial.py:91:    "mlx_version",
joulewise/powermetrics_fiducial.py:173:            for line in events_raw.decode("utf-8").splitlines()
joulewise/powermetrics_fiducial.py:176:    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
joulewise/powermetrics_fiducial.py:227:                "kind": "mlx_matmul",
joulewise/powermetrics_fiducial.py:255:                "MLX dispatch/fence latency stays inside the bound, never subtracted",
joulewise/powermetrics_fiducial.py:271:            "kind": "mlx_matmul",
joulewise/powermetrics_fiducial.py:305:            "MLX dispatch/fence latency stays inside the bound, never subtracted",
joulewise/powermetrics_fiducial.py:998:        text = events_jsonl.decode("utf-8")
joulewise/powermetrics_fiducial.py:999:    except UnicodeDecodeError as exc:
joulewise/powermetrics_fiducial.py:1019:        except json.JSONDecodeError as exc:
joulewise/powermetrics_fiducial.py:1319:    """Drive one GPU pulse of preallocated FP16 MLX matmuls with fencing.
joulewise/powermetrics_fiducial.py:1321:    Returns the number of fenced matmuls issued. Requires ``mlx`` (live
joulewise/powermetrics_fiducial.py:1327:    import mlx.core as mx  # noqa: PLC0415 - live-run-only dependency
joulewise/powermetrics_fiducial.py:1344:    import mlx.core as mx  # noqa: PLC0415 - live-run-only dependency
docs/strategy/2026-08-06-impressiveness-roadmap.md:134:The KDA/speculative-decode/MTP/MoE program is instead governed by D-070/D-075 and the AXI contracts:
docs/strategy/2026-08-06-impressiveness-roadmap.md:144:- External-draft speculative generation exists, but pinned `mlx-lm` lacks actual proposal counts and decode-step emission boundaries.
docs/strategy/2026-08-06-impressiveness-roadmap.md:162:| **7** | **One mechanism-level study, conditional on a hard feasibility gate** | **Highest scientific ceiling.** A controlled batch-1 speculative-decode or MTP energy result could be genuinely novel; KDA/context slope or MoE routing is also interesting if attribution is identifiable. | **2–3-week desk feasibility gate; if passed, another 6–12 weeks and roughly 2 nights.** | New/forked runtime instrumentation, direct proposal/acceptance events, output identity/equivalence, mechanism-specific AP and floors. MTP currently cannot execute; KDA is confounded; MoE routing visibility is uncertain. | Pick exactly one mechanism and a kill date. Recommended first choice: external-draft speculative decode, because it offers the cleanest same-target on/off contrast if observability can be added. |
docs/strategy/2026-08-06-impressiveness-roadmap.md:201:4. **Mechanism ambition.** Do not ask simply “unfence D-041.” Decide whether to retain D-070’s all-five-axis commitment or narrow it to one paper-worthy study. Recommended rule: two-to-three-week feasibility gate for speculative-decode observability; if it fails, return immediately to Q4/quantization.
tests/test_analysis_manifest_v3.py:27:CAMPAIGN_DIR = ROOT / "configs" / "campaigns" / "splitwise_decode_v1"
tests/test_analysis_manifest_v3.py:137:    def test_real_mlx_metadata_file_set_folded_sha256_normalizes(self) -> None:
tests/goldens/axi_decode_emission.json:2:  "event_type": "decode_emission",
tests/goldens/axi_decode_emission.json:3:  "message": "mock decode emission",
tests/goldens/axi_decode_emission.json:6:    "decode_step_ordinal": 0,
tests/goldens/axi_decode_emission.json:25:  "phase": "decode",
tests/test_mlx_runtime.py:1:"""CI-safe tests for the MLX runtime adapter (Slice 2G)."""
tests/test_mlx_runtime.py:16:from joulewise.adapters.mlx_runtime import (
tests/test_mlx_runtime.py:17:    MlxRuntimeAdapter,
tests/test_mlx_runtime.py:18:    _mlx_metal_memory,
tests/test_mlx_runtime.py:41:from scripts import spike_mlx_prompt_cache
tests/test_mlx_runtime.py:52:            "name": "fake-mlx-model",
tests/test_mlx_runtime.py:54:            "source": "/tmp/fake-mlx-model",
tests/test_mlx_runtime.py:55:            "weight_format": "mlx",
tests/test_mlx_runtime.py:61:            "runtime_backend": "mlx",
tests/test_mlx_runtime.py:65:            "name": "fake_mlx_smoke",
tests/test_mlx_runtime.py:94:class FakeMlxLm:
tests/test_mlx_runtime.py:135:class FakeMlxLmWithSampler(FakeMlxLm):
tests/test_mlx_runtime.py:203:            "decode_level": "short",
tests/test_mlx_runtime.py:225:            "suite_id": "mlx_suite",
tests/test_mlx_runtime.py:226:            "suite_profile": "mlx_suite_v1",
tests/test_mlx_runtime.py:267:class MlxRuntimeTests(unittest.TestCase):
tests/test_mlx_runtime.py:268:    def prepared_adapter(self, pieces: list[str]) -> tuple[MlxRuntimeAdapter, FakeMlxLm]:
tests/test_mlx_runtime.py:269:        adapter = MlxRuntimeAdapter(FakeClock(start=1000.0))
tests/test_mlx_runtime.py:270:        fake_mlx = FakeMlxLm(pieces)

 succeeded in 0ms:
scripts/run_campaign.py
docs/phase_1/phase_1_exit_checklist.md
docs/phase_1/phase_1_plan.md
docs/phase_1/2k_live_verification_checklist.md
scripts/spike_mlx_prompt_cache.py
joulewise/adapters/mock_runtime.py
joulewise/adapters/vllm_runtime.py
joulewise/adapters/mock_spec_runtime.py
joulewise/adapters/mlx_runtime.py
docs/phase_2/splitwise_decode_campaign.md
docs/phase_2/phase_2_plan.md
docs/phase_2/window_runbook.md
docs/phase_2/splitwise_replication_roadmap.md
docs/phase_2/phase_2_exit_checklist.md
docs/phase_2/hardware_slice_implementation_guide.md
docs/phase_2/refusal_scope_spec.md
docs/phase_2/floor_mint_contract.md
docs/phase_2/window_c_operator_checklist.md
docs/phase_2/detection_floor.md
docs/phase_2/suite_implementation_research.md
joulewise/campaign_provenance.py
tests/test_mlx_runtime.py
tests/test_run_campaign.py
tests/test_vllm_runtime.py
tests/fixtures/campaign_policy_test.json
configs/examples/mac_mlx_local.json
configs/examples/mac_mlx_mock_telemetry.json
configs/examples/mac_mlx_qwen35_122b.json
docs/phase_3/phase_3_plan.md
docs/phase_3/kv_feasibility.md
docs/phase_3/phase_3_exit_checklist.md
docs/stream_logs/2026-07-08-precampaign-review.md
docs/phase_5/phase_5_plan.md
docs/phase_5/phase_5_exit_checklist.md
docs/phase_4/related_work_draft.md
docs/phase_4/phase_4_exit_checklist.md
docs/phase_4/claims_index.md
docs/phase_4/phase_4_plan.md
docs/run_reports/2026-06-09-phase-2-5-planning-buildout.md
docs/run_reports/2026-06-12-phase-2-mock-vertical-slice.md
docs/run_reports/2026-06-09-phase-1-planning-audit.md
docs/run_reports/2026-07-10-p2041-campaign-verdict-split.md
docs/run_reports/2026-06-09-phase-1-scaffold-and-rename.md
docs/run_reports/2026-06-09-task-queue-and-phase-1-continuation.md
docs/run_reports/2026-06-09-phase-1-local-evidence.md
docs/run_reports/2026-06-09-phase-1-doc-unification.md
docs/campaign_packs/c5_2_7_device_perf_w_rankings.md
docs/campaign_packs/c5_3_1_3_5_replication.md
docs/campaign_packs/c5_i_1_i_2_i_5_import_family.md
docs/campaign_packs/README.md
docs/campaign_packs/q6_c5_2_10_rail_vs_wall.md
docs/campaign_packs/c5_i_3_flores_fertility.md
docs/campaign_packs/split_suite_q1_q2_q3.md
docs/campaign_packs/c5_2_3_kv_economics.md
docs/campaign_packs/c5_i_4_harness_overhead_floor.md
docs/campaign_packs/c5_2_8_placement_optimality.md
configs/campaigns/p2_015_floors/calibration_plan.sha256
configs/campaigns/p2_015_floors/05_phase_decode_abba/p2015-df-cmp-abba-ph-decode-b05-a2.json
configs/campaigns/p2_015_floors/05_phase_decode_abba/p2015-df-cmp-abba-ph-decode-b10-a1.json
configs/campaigns/p2_015_floors/05_phase_decode_abba/p2015-df-cmp-abba-ph-decode-b03-b1.json
configs/campaigns/p2_015_floors/05_phase_decode_abba/p2015-df-cmp-abba-ph-decode-b09-a1.json
configs/campaigns/p2_015_floors/05_phase_decode_abba/p2015-df-cmp-abba-ph-decode-b06-b2.json
configs/campaigns/p2_015_floors/05_phase_decode_abba/p2015-df-cmp-abba-ph-decode-b02-b1.json
configs/campaigns/p2_015_floors/05_phase_decode_abba/p2015-df-cmp-abba-ph-decode-b08-a1.json
configs/campaigns/p2_015_floors/05_phase_decode_abba/p2015-df-cmp-abba-ph-decode-b07-b2.json
configs/campaigns/p2_015_floors/05_phase_decode_abba/p2015-df-cmp-abba-ph-decode-b04-a2.json
configs/campaigns/p2_015_floors/05_phase_decode_abba/p2015-df-cmp-abba-ph-decode-b01-a1.json
configs/campaigns/p2_015_floors/05_phase_decode_abba/p2015-df-cmp-abba-ph-decode-b10-b1.json
configs/campaigns/p2_015_floors/05_phase_decode_abba/order_manifest.json
configs/campaigns/p2_015_floors/05_phase_decode_abba/p2015-df-cmp-abba-ph-decode-b05-b2.json
configs/campaigns/p2_015_floors/05_phase_decode_abba/p2015-df-cmp-abba-ph-decode-b06-a2.json
configs/campaigns/p2_015_floors/05_phase_decode_abba/p2015-df-cmp-abba-ph-decode-b09-b1.json
configs/campaigns/p2_015_floors/05_phase_decode_abba/p2015-df-cmp-abba-ph-decode-b03-a1.json
configs/campaigns/p2_015_floors/05_phase_decode_abba/p2015-df-cmp-abba-ph-decode-b07-a2.json
configs/campaigns/p2_015_floors/05_phase_decode_abba/p2015-df-cmp-abba-ph-decode-b08-b1.json
configs/campaigns/p2_015_floors/05_phase_decode_abba/p2015-df-cmp-abba-ph-decode-b02-a1.json
configs/campaigns/p2_015_floors/05_phase_decode_abba/p2015-df-cmp-abba-ph-decode-b01-b1.json
configs/campaigns/p2_015_floors/05_phase_decode_abba/p2015-df-cmp-abba-ph-decode-b04-b2.json
configs/campaigns/p2_015_floors/05_phase_decode_abba/p2015-df-cmp-abba-ph-decode-b01-b2.json
configs/campaigns/p2_015_floors/05_phase_decode_abba/p2015-df-cmp-abba-ph-decode-b04-b1.json
configs/campaigns/p2_015_floors/05_phase_decode_abba/p2015-df-cmp-abba-ph-decode-b07-a1.json
configs/campaigns/p2_015_floors/05_phase_decode_abba/p2015-df-cmp-abba-ph-decode-b08-b2.json
configs/campaigns/p2_015_floors/05_phase_decode_abba/p2015-df-cmp-abba-ph-decode-b02-a2.json
configs/campaigns/p2_015_floors/05_phase_decode_abba/p2015-df-cmp-abba-ph-decode-b06-a1.json
configs/campaigns/p2_015_floors/05_phase_decode_abba/p2015-df-cmp-abba-ph-decode-b09-b2.json
configs/campaigns/p2_015_floors/05_phase_decode_abba/p2015-df-cmp-abba-ph-decode-b03-a2.json
configs/campaigns/p2_015_floors/05_phase_decode_abba/p2015-df-cmp-abba-ph-decode-b10-b2.json
configs/campaigns/p2_015_floors/05_phase_decode_abba/p2015-df-cmp-abba-ph-decode-b05-b1.json
configs/campaigns/p2_015_floors/05_phase_decode_abba/p2015-df-cmp-abba-ph-decode-b04-a1.json
configs/campaigns/p2_015_floors/05_phase_decode_abba/p2015-df-cmp-abba-ph-decode-b01-a2.json
configs/campaigns/p2_015_floors/05_phase_decode_abba/p2015-df-cmp-abba-ph-decode-b02-b2.json
configs/campaigns/p2_015_floors/05_phase_decode_abba/p2015-df-cmp-abba-ph-decode-b08-a2.json
configs/campaigns/p2_015_floors/05_phase_decode_abba/p2015-df-cmp-abba-ph-decode-b07-b1.json
configs/campaigns/p2_015_floors/05_phase_decode_abba/p2015-df-cmp-abba-ph-decode-b03-b2.json
configs/campaigns/p2_015_floors/05_phase_decode_abba/p2015-df-cmp-abba-ph-decode-b09-a2.json
configs/campaigns/p2_015_floors/05_phase_decode_abba/p2015-df-cmp-abba-ph-decode-b06-b1.json
configs/campaigns/p2_015_floors/05_phase_decode_abba/p2015-df-cmp-abba-ph-decode-b05-a1.json
configs/campaigns/p2_015_floors/05_phase_decode_abba/p2015-df-cmp-abba-ph-decode-b10-a2.json
configs/campaigns/p2_015_floors/10_df_telem_onoff_unavailable/README.md
configs/campaigns/exploratory_2026_07_17/03_qwen35-122b/order_manifest.json
configs/campaigns/exploratory_2026_07_17/03_qwen35-122b/exploratory-20260717-qwen35-122b.json
configs/campaigns/qwen25_7b_decode_floor_v1/calibration_plan.sha256
configs/campaigns/p2_015_floors/11_neg8_end/p2015-neg8-reference-end.json
configs/campaigns/p2_015_floors/11_neg8_end/order_manifest.json
configs/campaigns/p2_015_floors/calibration_plan.json
configs/campaigns/p2_015_floors/backup_icloud.sh
configs/campaigns/p2_015_floors/order_manifest.json
configs/campaigns/p2_015_floors/generate_configs.py
configs/campaigns/metrology_v1/README.md
configs/campaigns/metrology_v1/_shared.py
configs/campaigns/neg8_reference_corpus/neg8-refcorpus-r02.json
configs/campaigns/neg8_reference_corpus/neg8-refcorpus-r03.json
configs/campaigns/neg8_reference_corpus/order_manifest.json
configs/campaigns/neg8_reference_corpus/neg8-refcorpus-r04.json
configs/campaigns/neg8_reference_corpus/neg8-refcorpus-r12.json
configs/campaigns/neg8_reference_corpus/neg8-refcorpus-r08.json
configs/campaigns/neg8_reference_corpus/neg8-refcorpus-r09.json
configs/campaigns/neg8_reference_corpus/neg8-refcorpus-r05.json
configs/campaigns/neg8_reference_corpus/README.md
configs/campaigns/neg8_reference_corpus/neg8-refcorpus-r10.json
configs/campaigns/neg8_reference_corpus/neg8-refcorpus-r06.json
configs/campaigns/qwen25_7b_decode_floor_v1/01_phase_decode_absolute/sw7bfloor-df-ph-decode-abs-r02.json
configs/campaigns/qwen25_7b_decode_floor_v1/01_phase_decode_absolute/sw7bfloor-df-ph-decode-abs-r03.json
configs/campaigns/qwen25_7b_decode_floor_v1/01_phase_decode_absolute/sw7bfloor-df-ph-decode-abs-r04.json
configs/campaigns/qwen25_7b_decode_floor_v1/01_phase_decode_absolute/order_manifest.json
configs/campaigns/qwen25_7b_decode_floor_v1/01_phase_decode_absolute/sw7bfloor-df-ph-decode-abs-r08.json
configs/campaigns/qwen25_7b_decode_floor_v1/01_phase_decode_absolute/sw7bfloor-df-ph-decode-abs-r09.json
configs/campaigns/qwen25_7b_decode_floor_v1/01_phase_decode_absolute/sw7bfloor-df-ph-decode-abs-r05.json
configs/campaigns/qwen25_7b_decode_floor_v1/01_phase_decode_absolute/sw7bfloor-df-ph-decode-abs-r10.json
configs/campaigns/qwen25_7b_decode_floor_v1/01_phase_decode_absolute/sw7bfloor-df-ph-decode-abs-r06.json
configs/campaigns/qwen25_7b_decode_floor_v1/01_phase_decode_absolute/sw7bfloor-df-ph-decode-abs-r07.json
configs/campaigns/qwen25_7b_decode_floor_v1/01_phase_decode_absolute/sw7bfloor-df-ph-decode-abs-r01.json
configs/campaigns/window_references/start_triplet/neg8-window-start-r3.json
configs/campaigns/qwen25_7b_decode_floor_v1/calibration_plan.json
configs/campaigns/window_references/start_triplet/neg8-window-start-r2.json
configs/campaigns/qwen25_7b_decode_floor_v1/order_manifest.json
configs/campaigns/window_references/start_triplet/order_manifest.json
configs/campaigns/qwen25_7b_decode_floor_v1/generate_configs.py
configs/campaigns/window_references/start_triplet/neg8-window-start-r1.json
configs/campaigns/metrology_v1/long_holds/calibration_plan.json
configs/campaigns/metrology_v1/long_holds/order_manifest.json
configs/campaigns/neg8_reference_corpus/derivation/settled_corpus.json
configs/campaigns/neg8_reference_corpus/neg8-refcorpus-r07.json
configs/campaigns/neg8_reference_corpus/neg8-refcorpus-r11.json
configs/campaigns/neg8_reference_corpus/neg8-refcorpus-r01.json
configs/campaigns/window_references/midpoint/order_manifest.json
configs/campaigns/window_references/midpoint/neg8-window-midpoint.json
configs/campaigns/window_references/README.md
configs/campaigns/p2_015_floors/03_request_abba/p2015-df-cmp-abba-rq-b05-b2.json
configs/campaigns/p2_015_floors/03_request_abba/p2015-df-cmp-abba-rq-b10-b1.json
configs/campaigns/p2_015_floors/03_request_abba/p2015-df-cmp-abba-rq-b03-a1.json
configs/campaigns/p2_015_floors/03_request_abba/p2015-df-cmp-abba-rq-b06-a2.json
configs/campaigns/p2_015_floors/03_request_abba/p2015-df-cmp-abba-rq-b09-b1.json
configs/campaigns/p2_015_floors/03_request_abba/p2015-df-cmp-abba-rq-b02-a1.json
configs/campaigns/p2_015_floors/03_request_abba/p2015-df-cmp-abba-rq-b07-a2.json
configs/campaigns/p2_015_floors/03_request_abba/p2015-df-cmp-abba-rq-b08-b1.json
configs/campaigns/p2_015_floors/03_request_abba/p2015-df-cmp-abba-rq-b04-b2.json
configs/campaigns/p2_015_floors/03_request_abba/p2015-df-cmp-abba-rq-b01-b1.json
configs/campaigns/p2_015_floors/03_request_abba/p2015-df-cmp-abba-rq-b10-a1.json
configs/campaigns/p2_015_floors/03_request_abba/order_manifest.json
configs/campaigns/p2_015_floors/03_request_abba/p2015-df-cmp-abba-rq-b05-a2.json
configs/campaigns/p2_015_floors/03_request_abba/p2015-df-cmp-abba-rq-b09-a1.json
configs/campaigns/p2_015_floors/03_request_abba/p2015-df-cmp-abba-rq-b06-b2.json
configs/campaigns/p2_015_floors/03_request_abba/p2015-df-cmp-abba-rq-b03-b1.json
configs/campaigns/p2_015_floors/03_request_abba/p2015-df-cmp-abba-rq-b08-a1.json
configs/campaigns/p2_015_floors/03_request_abba/p2015-df-cmp-abba-rq-b07-b2.json
configs/campaigns/p2_015_floors/03_request_abba/p2015-df-cmp-abba-rq-b02-b1.json
configs/campaigns/p2_015_floors/03_request_abba/p2015-df-cmp-abba-rq-b01-a1.json
configs/campaigns/p2_015_floors/03_request_abba/p2015-df-cmp-abba-rq-b04-a2.json
configs/campaigns/p2_015_floors/03_request_abba/p2015-df-cmp-abba-rq-b01-a2.json
configs/campaigns/p2_015_floors/03_request_abba/p2015-df-cmp-abba-rq-b04-a1.json
configs/campaigns/p2_015_floors/03_request_abba/p2015-df-cmp-abba-rq-b08-a2.json
configs/campaigns/p2_015_floors/03_request_abba/p2015-df-cmp-abba-rq-b07-b1.json
configs/campaigns/p2_015_floors/03_request_abba/p2015-df-cmp-abba-rq-b02-b2.json
configs/campaigns/p2_015_floors/03_request_abba/p2015-df-cmp-abba-rq-b09-a2.json
configs/campaigns/p2_015_floors/03_request_abba/p2015-df-cmp-abba-rq-b06-b1.json
configs/campaigns/p2_015_floors/03_request_abba/p2015-df-cmp-abba-rq-b03-b2.json
configs/campaigns/p2_015_floors/03_request_abba/p2015-df-cmp-abba-rq-b10-a2.json
configs/campaigns/p2_015_floors/03_request_abba/p2015-df-cmp-abba-rq-b05-a1.json
configs/campaigns/p2_015_floors/03_request_abba/p2015-df-cmp-abba-rq-b04-b1.json
configs/campaigns/p2_015_floors/03_request_abba/p2015-df-cmp-abba-rq-b01-b2.json
configs/campaigns/p2_015_floors/03_request_abba/p2015-df-cmp-abba-rq-b02-a2.json
configs/campaigns/p2_015_floors/03_request_abba/p2015-df-cmp-abba-rq-b07-a1.json
configs/campaigns/p2_015_floors/03_request_abba/p2015-df-cmp-abba-rq-b08-b2.json
configs/campaigns/p2_015_floors/03_request_abba/p2015-df-cmp-abba-rq-b03-a2.json
configs/campaigns/p2_015_floors/03_request_abba/p2015-df-cmp-abba-rq-b06-a1.json
configs/campaigns/p2_015_floors/03_request_abba/p2015-df-cmp-abba-rq-b09-b2.json
configs/campaigns/p2_015_floors/03_request_abba/p2015-df-cmp-abba-rq-b05-b1.json
configs/campaigns/p2_015_floors/03_request_abba/p2015-df-cmp-abba-rq-b10-b2.json
configs/campaigns/qwen25_7b_decode_floor_v1/02_phase_decode_abba_blocks_01_05/sw7bfloor-df-cmp-abba-ph-decode-b03-b1.json
configs/campaigns/qwen25_7b_decode_floor_v1/02_phase_decode_abba_blocks_01_05/sw7bfloor-df-cmp-abba-ph-decode-b05-a2.json
configs/campaigns/qwen25_7b_decode_floor_v1/02_phase_decode_abba_blocks_01_05/sw7bfloor-df-cmp-abba-ph-decode-b01-a1.json
configs/campaigns/qwen25_7b_decode_floor_v1/02_phase_decode_abba_blocks_01_05/sw7bfloor-df-cmp-abba-ph-decode-b04-a2.json
configs/campaigns/qwen25_7b_decode_floor_v1/02_phase_decode_abba_blocks_01_05/sw7bfloor-df-cmp-abba-ph-decode-b02-b1.json
configs/campaigns/qwen25_7b_decode_floor_v1/02_phase_decode_abba_blocks_01_05/sw7bfloor-df-cmp-abba-ph-decode-b03-a1.json
configs/campaigns/qwen25_7b_decode_floor_v1/02_phase_decode_abba_blocks_01_05/order_manifest.json
configs/campaigns/qwen25_7b_decode_floor_v1/02_phase_decode_abba_blocks_01_05/sw7bfloor-df-cmp-abba-ph-decode-b05-b2.json
configs/campaigns/qwen25_7b_decode_floor_v1/02_phase_decode_abba_blocks_01_05/sw7bfloor-df-cmp-abba-ph-decode-b04-b2.json
configs/campaigns/qwen25_7b_decode_floor_v1/02_phase_decode_abba_blocks_01_05/sw7bfloor-df-cmp-abba-ph-decode-b01-b1.json
configs/campaigns/qwen25_7b_decode_floor_v1/02_phase_decode_abba_blocks_01_05/sw7bfloor-df-cmp-abba-ph-decode-b02-a1.json
configs/campaigns/qwen25_7b_decode_floor_v1/02_phase_decode_abba_blocks_01_05/sw7bfloor-df-cmp-abba-ph-decode-b02-a2.json
configs/campaigns/qwen25_7b_decode_floor_v1/02_phase_decode_abba_blocks_01_05/sw7bfloor-df-cmp-abba-ph-decode-b04-b1.json
configs/campaigns/qwen25_7b_decode_floor_v1/02_phase_decode_abba_blocks_01_05/sw7bfloor-df-cmp-abba-ph-decode-b01-b2.json
configs/campaigns/qwen25_7b_decode_floor_v1/02_phase_decode_abba_blocks_01_05/sw7bfloor-df-cmp-abba-ph-decode-b05-b1.json
configs/campaigns/qwen25_7b_decode_floor_v1/02_phase_decode_abba_blocks_01_05/sw7bfloor-df-cmp-abba-ph-decode-b03-a2.json
configs/campaigns/qwen25_7b_decode_floor_v1/02_phase_decode_abba_blocks_01_05/sw7bfloor-df-cmp-abba-ph-decode-b02-b2.json
configs/campaigns/qwen25_7b_decode_floor_v1/02_phase_decode_abba_blocks_01_05/sw7bfloor-df-cmp-abba-ph-decode-b01-a2.json
configs/campaigns/qwen25_7b_decode_floor_v1/02_phase_decode_abba_blocks_01_05/sw7bfloor-df-cmp-abba-ph-decode-b04-a1.json
configs/campaigns/qwen25_7b_decode_floor_v1/02_phase_decode_abba_blocks_01_05/sw7bfloor-df-cmp-abba-ph-decode-b05-a1.json
configs/campaigns/qwen25_7b_decode_floor_v1/02_phase_decode_abba_blocks_01_05/sw7bfloor-df-cmp-abba-ph-decode-b03-b2.json
configs/campaigns/qwen25_7b_decode_floor_v1/README.md
configs/campaigns/metrology_v1/long_holds/02_idle_extended/mtidle-i0120-r01.json
configs/campaigns/metrology_v1/long_holds/02_idle_extended/order_manifest.json
configs/campaigns/metrology_v1/long_holds/02_idle_extended/mtidle-i0300-r01.json
configs/campaigns/metrology_v1/long_holds/02_idle_extended/mtidle-i0600-r01.json
configs/campaigns/metrology_v1/long_holds/generate_configs.py
configs/campaigns/metrology_v1/long_holds/README.md
configs/campaigns/p2_015_floors/00_neg8_start/order_manifest.json
configs/campaigns/p2_015_floors/00_neg8_start/p2015-neg8-reference-start.json
configs/campaigns/window_references/end_triplet/neg8-window-end-r2.json
configs/campaigns/window_references/end_triplet/neg8-window-end-r3.json
configs/campaigns/window_references/end_triplet/order_manifest.json
configs/campaigns/window_references/end_triplet/neg8-window-end-r1.json
configs/campaigns/exploratory_2026_07_17/02_qwen3-4b/order_manifest.json
configs/campaigns/exploratory_2026_07_17/02_qwen3-4b/exploratory-20260717-qwen3-4b.json
configs/campaigns/qwen25_7b_decode_floor_v1/03_phase_decode_abba_blocks_06_10/sw7bfloor-df-cmp-abba-ph-decode-b09-a1.json
configs/campaigns/qwen25_7b_decode_floor_v1/03_phase_decode_abba_blocks_06_10/sw7bfloor-df-cmp-abba-ph-decode-b06-b2.json
configs/campaigns/qwen25_7b_decode_floor_v1/03_phase_decode_abba_blocks_06_10/sw7bfloor-df-cmp-abba-ph-decode-b10-a1.json
configs/campaigns/qwen25_7b_decode_floor_v1/03_phase_decode_abba_blocks_06_10/sw7bfloor-df-cmp-abba-ph-decode-b08-a1.json
configs/campaigns/qwen25_7b_decode_floor_v1/03_phase_decode_abba_blocks_06_10/sw7bfloor-df-cmp-abba-ph-decode-b07-b2.json
configs/campaigns/qwen25_7b_decode_floor_v1/03_phase_decode_abba_blocks_06_10/order_manifest.json
configs/campaigns/qwen25_7b_decode_floor_v1/03_phase_decode_abba_blocks_06_10/sw7bfloor-df-cmp-abba-ph-decode-b06-a2.json
configs/campaigns/qwen25_7b_decode_floor_v1/03_phase_decode_abba_blocks_06_10/sw7bfloor-df-cmp-abba-ph-decode-b09-b1.json
configs/campaigns/qwen25_7b_decode_floor_v1/03_phase_decode_abba_blocks_06_10/sw7bfloor-df-cmp-abba-ph-decode-b10-b1.json
configs/campaigns/qwen25_7b_decode_floor_v1/03_phase_decode_abba_blocks_06_10/sw7bfloor-df-cmp-abba-ph-decode-b07-a2.json
configs/campaigns/qwen25_7b_decode_floor_v1/03_phase_decode_abba_blocks_06_10/sw7bfloor-df-cmp-abba-ph-decode-b08-b1.json
configs/campaigns/qwen25_7b_decode_floor_v1/03_phase_decode_abba_blocks_06_10/sw7bfloor-df-cmp-abba-ph-decode-b07-a1.json
configs/campaigns/qwen25_7b_decode_floor_v1/03_phase_decode_abba_blocks_06_10/sw7bfloor-df-cmp-abba-ph-decode-b08-b2.json
configs/campaigns/qwen25_7b_decode_floor_v1/03_phase_decode_abba_blocks_06_10/sw7bfloor-df-cmp-abba-ph-decode-b10-b2.json
configs/campaigns/qwen25_7b_decode_floor_v1/03_phase_decode_abba_blocks_06_10/sw7bfloor-df-cmp-abba-ph-decode-b06-a1.json
configs/campaigns/qwen25_7b_decode_floor_v1/03_phase_decode_abba_blocks_06_10/sw7bfloor-df-cmp-abba-ph-decode-b09-b2.json
configs/campaigns/qwen25_7b_decode_floor_v1/03_phase_decode_abba_blocks_06_10/sw7bfloor-df-cmp-abba-ph-decode-b08-a2.json
configs/campaigns/qwen25_7b_decode_floor_v1/03_phase_decode_abba_blocks_06_10/sw7bfloor-df-cmp-abba-ph-decode-b07-b1.json
configs/campaigns/qwen25_7b_decode_floor_v1/03_phase_decode_abba_blocks_06_10/sw7bfloor-df-cmp-abba-ph-decode-b10-a2.json
configs/campaigns/qwen25_7b_decode_floor_v1/03_phase_decode_abba_blocks_06_10/sw7bfloor-df-cmp-abba-ph-decode-b09-a2.json
configs/campaigns/qwen25_7b_decode_floor_v1/03_phase_decode_abba_blocks_06_10/sw7bfloor-df-cmp-abba-ph-decode-b06-b1.json
configs/campaigns/exploratory_2026_07_17/01_olmoe-1b-7b/order_manifest.json
configs/campaigns/exploratory_2026_07_17/01_olmoe-1b-7b/exploratory-20260717-olmoe-1b-7b.json
configs/campaigns/metrology_v1/linearity_ramp/calibration_plan.json
configs/campaigns/metrology_v1/linearity_ramp/order_manifest.json
configs/campaigns/metrology_v1/linearity_ramp/generate_configs.py
configs/campaigns/metrology_v1/linearity_ramp/README.md
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/p2015-df-cmp-abba-ph-short-prefill-b10-b1.json
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/p2015-df-cmp-abba-ph-short-prefill-b05-b2.json
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/p2015-df-cmp-abba-ph-short-prefill-b09-b1.json
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/p2015-df-cmp-abba-ph-short-prefill-b06-a2.json
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/p2015-df-cmp-abba-ph-short-prefill-b03-a1.json
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/p2015-df-cmp-abba-ph-short-prefill-b08-b1.json
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/p2015-df-cmp-abba-ph-short-prefill-b07-a2.json
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/p2015-df-cmp-abba-ph-short-prefill-b02-a1.json
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/p2015-df-cmp-abba-ph-short-prefill-b01-b1.json
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/p2015-df-cmp-abba-ph-short-prefill-b04-b2.json
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/p2015-df-cmp-abba-ph-short-prefill-b05-a2.json
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/order_manifest.json
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/p2015-df-cmp-abba-ph-short-prefill-b10-a1.json
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/p2015-df-cmp-abba-ph-short-prefill-b03-b1.json
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/p2015-df-cmp-abba-ph-short-prefill-b06-b2.json
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/p2015-df-cmp-abba-ph-short-prefill-b09-a1.json
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/p2015-df-cmp-abba-ph-short-prefill-b02-b1.json
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/p2015-df-cmp-abba-ph-short-prefill-b07-b2.json
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/p2015-df-cmp-abba-ph-short-prefill-b08-a1.json
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/p2015-df-cmp-abba-ph-short-prefill-b04-a2.json
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/p2015-df-cmp-abba-ph-short-prefill-b01-a1.json
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/p2015-df-cmp-abba-ph-short-prefill-b04-a1.json
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/p2015-df-cmp-abba-ph-short-prefill-b01-a2.json
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/p2015-df-cmp-abba-ph-short-prefill-b02-b2.json
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/p2015-df-cmp-abba-ph-short-prefill-b07-b1.json
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/p2015-df-cmp-abba-ph-short-prefill-b08-a2.json
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/p2015-df-cmp-abba-ph-short-prefill-b03-b2.json
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/p2015-df-cmp-abba-ph-short-prefill-b06-b1.json
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/p2015-df-cmp-abba-ph-short-prefill-b09-a2.json
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/p2015-df-cmp-abba-ph-short-prefill-b05-a1.json
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/p2015-df-cmp-abba-ph-short-prefill-b10-a2.json
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/p2015-df-cmp-abba-ph-short-prefill-b01-b2.json
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/p2015-df-cmp-abba-ph-short-prefill-b04-b1.json
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/p2015-df-cmp-abba-ph-short-prefill-b08-b2.json
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/p2015-df-cmp-abba-ph-short-prefill-b07-a1.json
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/p2015-df-cmp-abba-ph-short-prefill-b02-a2.json
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/p2015-df-cmp-abba-ph-short-prefill-b09-b2.json
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/p2015-df-cmp-abba-ph-short-prefill-b06-a1.json
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/p2015-df-cmp-abba-ph-short-prefill-b03-a2.json
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/p2015-df-cmp-abba-ph-short-prefill-b10-b2.json
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/p2015-df-cmp-abba-ph-short-prefill-b05-b1.json
configs/campaigns/metrology_v1/linearity_ramp/condition_families/condition_family_mt_q15_decode_p0128_o0512.json
configs/campaigns/metrology_v1/linearity_ramp/condition_families/condition_family_mt_q15_decode_p0128_o0256.json
configs/campaigns/metrology_v1/linearity_ramp/condition_families/condition_family_mt_q15_decode_p0128_o0128.json
configs/campaigns/metrology_v1/linearity_ramp/condition_families/condition_family_mt_q15_decode_p0128_o2048.json
configs/campaigns/metrology_v1/linearity_ramp/condition_families/condition_family_mt_q15_decode_p0128_o1024.json
configs/campaigns/qwen25_7b_decode_floor_v1/condition_families/condition_family_df_ph_decode_qwen25_7b.json
docs/process_traces/2026-07-17-axi-sc-live-probes/axi-sc-mlx-draft.jsonl
configs/campaigns/p2_015_smoke/production_shakedown/order_manifest.json
configs/campaigns/p2_015_floors/08_optional_long_request_absolute/p2015-df-rq-long-prompt-abs-r02.json
configs/campaigns/p2_015_smoke/production_shakedown/p2038_production_shakedown.json
configs/campaigns/p2_015_floors/01_request_absolute_core/p2015-df-rq-mid-abs-r03.json
configs/campaigns/p2_015_floors/01_request_absolute_core/p2015-df-rq-short-abs-r01.json
configs/campaigns/p2_015_floors/01_request_absolute_core/p2015-df-rq-mid-abs-r02.json
configs/campaigns/p2_015_floors/01_request_absolute_core/p2015-df-rq-mid-abs-r09.json
configs/campaigns/p2_015_floors/01_request_absolute_core/order_manifest.json
configs/campaigns/p2_015_floors/01_request_absolute_core/p2015-df-rq-mid-abs-r05.json
configs/campaigns/p2_015_floors/01_request_absolute_core/p2015-df-rq-short-abs-r06.json
configs/campaigns/p2_015_floors/01_request_absolute_core/p2015-df-rq-short-abs-r10.json
configs/campaigns/p2_015_floors/01_request_absolute_core/p2015-df-rq-short-abs-r07.json
configs/campaigns/p2_015_floors/01_request_absolute_core/p2015-df-rq-mid-abs-r04.json
configs/campaigns/p2_015_floors/01_request_absolute_core/p2015-df-rq-mid-abs-r08.json
configs/campaigns/p2_015_floors/01_request_absolute_core/p2015-df-rq-short-abs-r08.json
configs/campaigns/p2_015_floors/01_request_absolute_core/p2015-df-rq-short-abs-r04.json
configs/campaigns/p2_015_floors/01_request_absolute_core/p2015-df-rq-mid-abs-r07.json
configs/campaigns/p2_015_floors/01_request_absolute_core/p2015-df-rq-mid-abs-r10.json
configs/campaigns/p2_015_floors/01_request_absolute_core/p2015-df-rq-mid-abs-r06.json
configs/campaigns/p2_015_floors/01_request_absolute_core/p2015-df-rq-short-abs-r05.json
configs/campaigns/p2_015_floors/01_request_absolute_core/p2015-df-rq-short-abs-r09.json
configs/campaigns/p2_015_floors/01_request_absolute_core/p2015-df-rq-short-abs-r02.json
configs/campaigns/p2_015_floors/01_request_absolute_core/p2015-df-rq-mid-abs-r01.json
configs/campaigns/p2_015_floors/01_request_absolute_core/p2015-df-rq-short-abs-r03.json
configs/campaigns/p2_015_floors/08_optional_long_request_absolute/p2015-df-rq-long-decode-abs-r04.json
configs/campaigns/p2_015_floors/08_optional_long_request_absolute/p2015-df-rq-long-prompt-abs-r10.json
configs/campaigns/p2_015_floors/08_optional_long_request_absolute/p2015-df-rq-long-decode-abs-r08.json
configs/campaigns/p2_015_floors/08_optional_long_request_absolute/p2015-df-rq-long-prompt-abs-r06.json
configs/campaigns/p2_015_floors/08_optional_long_request_absolute/p2015-df-rq-long-prompt-abs-r07.json
configs/campaigns/p2_015_floors/08_optional_long_request_absolute/p2015-df-rq-long-decode-abs-r09.json
configs/campaigns/p2_015_floors/08_optional_long_request_absolute/p2015-df-rq-long-decode-abs-r05.json
configs/campaigns/p2_015_floors/08_optional_long_request_absolute/p2015-df-rq-long-decode-abs-r02.json
configs/campaigns/p2_015_floors/08_optional_long_request_absolute/p2015-df-rq-long-decode-abs-r03.json
configs/campaigns/p2_015_floors/08_optional_long_request_absolute/p2015-df-rq-long-prompt-abs-r01.json
configs/campaigns/p2_015_floors/08_optional_long_request_absolute/order_manifest.json
configs/campaigns/p2_015_floors/08_optional_long_request_absolute/p2015-df-rq-long-prompt-abs-r04.json
configs/campaigns/p2_015_floors/08_optional_long_request_absolute/p2015-df-rq-long-prompt-abs-r05.json
configs/campaigns/p2_015_floors/08_optional_long_request_absolute/p2015-df-rq-long-decode-abs-r07.json
configs/campaigns/p2_015_floors/08_optional_long_request_absolute/p2015-df-rq-long-prompt-abs-r09.json
configs/campaigns/p2_015_floors/08_optional_long_request_absolute/p2015-df-rq-long-prompt-abs-r08.json
configs/campaigns/p2_015_floors/08_optional_long_request_absolute/p2015-df-rq-long-decode-abs-r10.json
configs/campaigns/p2_015_floors/08_optional_long_request_absolute/p2015-df-rq-long-decode-abs-r06.json
configs/campaigns/p2_015_floors/08_optional_long_request_absolute/p2015-df-rq-long-prompt-abs-r03.json
configs/campaigns/p2_015_floors/08_optional_long_request_absolute/p2015-df-rq-long-decode-abs-r01.json
configs/campaigns/metrology_v1/linearity_ramp/01_ramp/mtlin-o2048-r06.json
configs/campaigns/metrology_v1/linearity_ramp/01_ramp/mtlin-o0512-r06.json
configs/campaigns/metrology_v1/linearity_ramp/01_ramp/mtlin-o0256-r06.json
configs/campaigns/metrology_v1/linearity_ramp/01_ramp/mtlin-o1024-r07.json
configs/campaigns/metrology_v1/linearity_ramp/01_ramp/mtlin-o0128-r01.json
configs/campaigns/metrology_v1/linearity_ramp/01_ramp/mtlin-o1024-r06.json
configs/campaigns/metrology_v1/linearity_ramp/01_ramp/mtlin-o0256-r07.json
configs/campaigns/metrology_v1/linearity_ramp/01_ramp/mtlin-o0512-r07.json
configs/campaigns/metrology_v1/linearity_ramp/01_ramp/mtlin-o2048-r07.json
configs/campaigns/metrology_v1/linearity_ramp/01_ramp/mtlin-o1024-r01.json
configs/campaigns/metrology_v1/linearity_ramp/01_ramp/order_manifest.json
configs/campaigns/metrology_v1/linearity_ramp/01_ramp/mtlin-o0128-r06.json
configs/campaigns/metrology_v1/linearity_ramp/01_ramp/mtlin-o0256-r01.json
configs/campaigns/metrology_v1/linearity_ramp/01_ramp/mtlin-o0512-r01.json
configs/campaigns/metrology_v1/linearity_ramp/01_ramp/mtlin-o2048-r01.json
configs/campaigns/metrology_v1/linearity_ramp/01_ramp/mtlin-o0128-r07.json
configs/campaigns/metrology_v1/linearity_ramp/01_ramp/mtlin-o0128-r04.json
configs/campaigns/metrology_v1/linearity_ramp/01_ramp/mtlin-o1024-r03.json
configs/campaigns/metrology_v1/linearity_ramp/01_ramp/mtlin-o0128-r08.json
configs/campaigns/metrology_v1/linearity_ramp/01_ramp/mtlin-o0256-r02.json
configs/campaigns/metrology_v1/linearity_ramp/01_ramp/mtlin-o0512-r02.json
configs/campaigns/metrology_v1/linearity_ramp/01_ramp/mtlin-o2048-r02.json
configs/campaigns/metrology_v1/linearity_ramp/01_ramp/mtlin-o2048-r03.json
configs/campaigns/metrology_v1/linearity_ramp/01_ramp/mtlin-o0512-r03.json
configs/campaigns/metrology_v1/linearity_ramp/01_ramp/mtlin-o0256-r03.json
configs/campaigns/metrology_v1/linearity_ramp/01_ramp/mtlin-o1024-r02.json
configs/campaigns/metrology_v1/linearity_ramp/01_ramp/mtlin-o0128-r05.json
configs/campaigns/metrology_v1/linearity_ramp/01_ramp/mtlin-o0256-r04.json
configs/campaigns/metrology_v1/linearity_ramp/01_ramp/mtlin-o0512-r04.json
configs/campaigns/metrology_v1/linearity_ramp/01_ramp/mtlin-o2048-r04.json
configs/campaigns/metrology_v1/linearity_ramp/01_ramp/mtlin-o0128-r02.json
configs/campaigns/metrology_v1/linearity_ramp/01_ramp/mtlin-o0256-r08.json
configs/campaigns/metrology_v1/linearity_ramp/01_ramp/mtlin-o1024-r05.json
configs/campaigns/metrology_v1/linearity_ramp/01_ramp/mtlin-o0512-r08.json
configs/campaigns/metrology_v1/linearity_ramp/01_ramp/mtlin-o2048-r08.json
configs/campaigns/metrology_v1/linearity_ramp/01_ramp/mtlin-o1024-r04.json
configs/campaigns/metrology_v1/linearity_ramp/01_ramp/mtlin-o0128-r03.json
configs/campaigns/metrology_v1/linearity_ramp/01_ramp/mtlin-o2048-r05.json
configs/campaigns/metrology_v1/linearity_ramp/01_ramp/mtlin-o0512-r05.json
configs/campaigns/metrology_v1/linearity_ramp/01_ramp/mtlin-o1024-r08.json
configs/campaigns/metrology_v1/linearity_ramp/01_ramp/mtlin-o0256-r05.json
configs/campaigns/metrology_v1/linearity_ramp/calibration_plan.sha256
configs/campaigns/splitwise_decode_v1/calibration_plan.json
configs/campaigns/splitwise_decode_v1/order_manifest.json
configs/campaigns/splitwise_decode_v1/generate_configs.py
configs/campaigns/p2_015_floors/02_phase_absolute/p2015-df-ph-decode-abs-r05.json
configs/campaigns/p2_015_floors/02_phase_absolute/p2015-df-ph-short-prefill-abs-r07.json
configs/campaigns/p2_015_floors/02_phase_absolute/p2015-df-ph-prefill-abs-r09.json
configs/campaigns/p2_015_floors/02_phase_absolute/p2015-df-ph-decode-abs-r09.json
configs/campaigns/p2_015_floors/02_phase_absolute/p2015-df-ph-prefill-abs-r05.json
configs/campaigns/p2_015_floors/02_phase_absolute/p2015-df-ph-prefill-abs-r04.json
configs/campaigns/p2_015_floors/02_phase_absolute/p2015-df-ph-decode-abs-r08.json
configs/campaigns/p2_015_floors/02_phase_absolute/p2015-df-ph-short-prefill-abs-r10.json
configs/campaigns/p2_015_floors/02_phase_absolute/p2015-df-ph-prefill-abs-r08.json
configs/campaigns/p2_015_floors/02_phase_absolute/p2015-df-ph-short-prefill-abs-r06.json
configs/campaigns/p2_015_floors/02_phase_absolute/p2015-df-ph-decode-abs-r04.json

exec
/bin/zsh -lc 'git log --oneline --decorate -3' in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
de9e879 (HEAD -> main, origin/main, origin/HEAD, impl/d117-u3-pinset-v2, impl/d117-u1-ledger-session) D-117 plan-freeze: Sol xhigh design memo custodied + magistrate ratification (gates 1-8 adopted; U1-U10 work orders; 3 toolchain blockers before any arm); prefill-feasibility trace recovered onto main (design-consult F4)
94a24e5 RUN_STATE interim block: 2026-08-07 live session — resume items cleared, D-117 adopted, paper fix round + plan-freeze consult in flight
a1f0e19 CLAIMS_STATUS un-staled per D-117: re-mint conditions historical (all completed then superseded), pre-genesis windows re-scoped to diagnostic/rule-establishing, claim path = three prospective windows

exec
/bin/zsh -lc "sed -n '1,320p' joulewise/adapters/mlx_runtime.py" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
"""MLX runtime adapter for local Apple Silicon generation (Slice 2G).

The core package remains stdlib-only: this module is importable without MLX,
and ``mlx_lm`` is imported only inside ``prepare``. Tests exercise the workload
mapping and event shape with fakes, while real runs use the same adapter path.
"""

from __future__ import annotations

import importlib
import inspect
import json
import operator
import os
import subprocess
from collections.abc import Iterable
from dataclasses import dataclass
from importlib import metadata as importlib_metadata
from pathlib import Path
from typing import Any

from joulewise.adapters.suite_control import SuiteItemResult, execute_suite
from joulewise.clock import Clock
from joulewise.interfaces import (
    AdapterFailure,
    AdapterResult,
    RunContext,
    RuntimeEvent,
    RuntimeResult,
)
from joulewise.provenance import (
    PROMPT_TOKEN_IDS_HASH_DOMAIN,
    fixed_budget_outcome_name,
    folded_model_artifact_sha256,
    normalized_sha256_hex,
    output_policy,
    prompt_provenance,
    sha256_hex,
    suite_prompt_plan_class,
    suite_prompt_rollup,
)
from joulewise.schemas import BenchmarkConfig, FailureReason
from joulewise.suite import (
    ITEM_END,
    ITEM_START,
    SUITE_PHASE,
    ItemStatus,
    SuiteItem,
    SuiteManifest,
)

DEFAULT_OUTPUT_TOKENS = 8
WARMUP_TOKENS = 4
SYNTHETIC_PROMPT_SEED = "JouleWise synthetic prompt token sequence."


@dataclass(frozen=True)
class _GenerationRecord:
    events: list[RuntimeEvent]
    token_records: list[dict[str, float | int]]
    text: str
    stop_condition: str
    prompt_tokens: int
    output_tokens: int
    sampler_provenance: dict[str, Any]
    prompt_token_ids: list[int]
    prompt_text: str | None
    output_token_ids: list[int]


class MlxRuntimeAdapter:
    """RuntimeAdapter implementation backed by ``mlx_lm``."""

    name = "mlx"

    def __init__(self, clock: Clock) -> None:
        self._clock = clock
        self._mlx_lm: Any | None = None
        self._model: Any | None = None
        self._tokenizer: Any | None = None
        self._model_config: dict[str, Any] | None = None
        self._model_artifact_identity: dict[str, Any] | None = None

    def prepare(
        self, config: BenchmarkConfig, context: RunContext | None = None
    ) -> AdapterResult:
        source = config.model.source
        if not source:
            return AdapterResult(
                ok=False,
                failure_reason=FailureReason.RUNTIME_UNAVAILABLE,
                message=(
                    "runtime backend 'mlx' requires model.source to be a local "
                    "MLX model path; install the [mac] extra and configure a "
                    "local mirror to avoid network downloads"
                ),
            )

        try:
            mlx_lm = self._import_mlx_lm()
        except ImportError as exc:
            return AdapterResult(
                ok=False,
                failure_reason=FailureReason.RUNTIME_UNAVAILABLE,
                message=(
                    "runtime backend 'mlx' is not installed; install the "
                    "[mac] extra (pip install 'joulewise[mac]'). If MLX cannot "
                    f"be installed on this host, use another runtime. Import "
                    f"error: {exc}"
                ),
            )
        except Exception as exc:  # noqa: BLE001 - imports can fail during backend init
            return AdapterResult(
                ok=False,
                failure_reason=FailureReason.RUNTIME_UNAVAILABLE,
                message=(
                    "runtime backend 'mlx' could not initialize; install/use "
                    "the [mac] extra on an Apple Silicon session with GPU "
                    f"access. {type(exc).__name__}: {exc}"
                ),
            )

        start_s = self._clock.now()
        try:
            loaded = mlx_lm.load(
                source,
                revision=config.model.revision,
                return_config=True,
            )
        except Exception as exc:  # noqa: BLE001 - structured adapter failure (D-012)
            return AdapterResult(
                ok=False,
                failure_reason=FailureReason.RUNTIME_UNAVAILABLE,
                message=(
                    "runtime backend 'mlx' could not load the configured local "
                    f"model source {source!r}; install/use the [mac] extra and "
                    f"verify the local mirror is complete. {type(exc).__name__}: {exc}"
                ),
            )
        end_s = self._clock.now()

        self._mlx_lm = mlx_lm
        self._model, self._tokenizer, self._model_config = loaded

        self._model_artifact_identity = model_artifact_identity(source)
        metadata = {
            "adapter": "mlx_runtime",
            "mlx_lm_version": _module_or_distribution_version(mlx_lm, "mlx-lm"),
            "mlx_version": _distribution_version("mlx"),
            "transformers_version": _distribution_version("transformers"),
            "model_source": str(Path(source).expanduser()),
            "model_source_is_local_path": Path(source).expanduser().exists(),
            "model_revision": config.model.revision,
            "load_wall_time_s": end_s - start_s,
            "weight_format": config.model.weight_format,
            "quantization": config.quantization.name,
            "model_artifact_identity": self._model_artifact_identity,
        }
        if isinstance(self._model_config, dict):
            metadata["model_config_name"] = self._model_config.get("model_type")
            metadata["model_config_eos_token_id"] = self._model_config.get("eos_token_id")
        metadata["memory_snapshots"] = [self._memory_snapshot("prepare_end")]
        return AdapterResult(ok=True, metadata=metadata)

    def warmup(
        self, config: BenchmarkConfig, context: RunContext | None = None
    ) -> AdapterResult:
        if self._mlx_lm is None or self._model is None or self._tokenizer is None:
            return AdapterResult(
                ok=False,
                failure_reason=FailureReason.RUNTIME_UNAVAILABLE,
                message="runtime backend 'mlx' warmup called before prepare succeeded",
            )
        prompt, _, _ = self._prompt_for_workload(config)
        try:
            for _ in self._mlx_lm.stream_generate(
                self._model,
                self._tokenizer,
                prompt,
                max_tokens=WARMUP_TOKENS,
            ):
                pass
        except Exception as exc:  # noqa: BLE001 - structured adapter failure (D-012)
            return AdapterResult(
                ok=False,
                failure_reason=FailureReason.RUNTIME_UNAVAILABLE,
                message=f"runtime backend 'mlx' warmup failed: {type(exc).__name__}: {exc}",
            )
        return AdapterResult(ok=True)

    def run_workload(
        self, config: BenchmarkConfig, context: RunContext | None = None
    ) -> RuntimeResult:
        if self._mlx_lm is None or self._model is None or self._tokenizer is None:
            raise RuntimeError("runtime backend 'mlx' run_workload called before prepare")

        max_tokens = config.workload_profile.output_tokens or DEFAULT_OUTPUT_TOKENS
        # The encode runs INSIDE the tokenize phase window (prepare_prompt is
        # called between the tokenize markers) so per-phase attribution covers
        # the real tokenization work on a live clock.
        record = self._generate(
            None,
            [],
            None,
            max_tokens,
            suppress_eos=True,
            prepare_prompt=lambda: self._prompt_for_workload(config),
        )
        prompt_token_ids = record.prompt_token_ids
        prompt_text = record.prompt_text
        tokens_jsonl = "".join(
            json.dumps(token_record, sort_keys=True) + "\n"
            for token_record in record.token_records
        )
        return RuntimeResult(
            events=record.events,
            output_artifacts={
                "response.txt": record.text,
                "tokens.jsonl": tokens_jsonl,
            },
            token_count=record.prompt_tokens + record.output_tokens,
            output_token_count=record.output_tokens,
            workload_provenance={
                "prompt": prompt_provenance(prompt_token_ids, text=prompt_text),
                "generator": {
                    "name": "mlx_lm.stream_generate",
                    "version": _module_or_distribution_version(self._mlx_lm, "mlx-lm"),
                },
                "sampler": record.sampler_provenance,
                "tokenizer": _tokenizer_identity(self._tokenizer, config),
                "model": {
                    "source": config.model.source,
                    "revision": config.model.revision,
                    "artifact_identity": self._model_artifact_identity,
                },
                "response": {
                    "emitted_token_ids": record.output_token_ids,
                },
                "output_policy": output_policy(
                    fixed_budget_outcome_name(
                        requested_tokens=max_tokens,
                        emitted_tokens=record.output_tokens,
                        stop_condition=record.stop_condition,
                    ),
                    requested_tokens=max_tokens,
                    emitted_tokens=record.output_tokens,
                    stop_condition=record.stop_condition,
                ),
            },
        )

    def run_suite(
        self,
        config: BenchmarkConfig,
        manifest: SuiteManifest,
        context: RunContext | None = None,
        *,
        order_seed: str,
        order_row: int | None = None,
    ) -> RuntimeResult:
        if self._mlx_lm is None or self._model is None or self._tokenizer is None:
            raise RuntimeError("runtime backend 'mlx' run_suite called before prepare")
        self._sampler_for_generation()
        suite_identity = _suite_identity(manifest)
        control = execute_suite(
            manifest,
            backend_name="mlx",
            order_seed=order_seed,
            order_row=order_row,
            event_factory=self._event,
            run_item=lambda item, item_index, position, previous_item_id, events: (
                self._run_suite_item(
                    item,
                    item_index,
                    position,
                    previous_item_id,
                    events,
                    suite_identity=suite_identity,
                )
            ),
        )
        sampler_provenance = self._sampler_provenance_unavailable(
            "no suite item generation attempted"
        )
        for item_result in control.item_results:
            # First real record wins: an item whose generation never started
            # returns the unavailable sentinel and must not mask an earlier
            # item's pinned sampler provenance (the sampler is constant).
            if item_result.backend_metadata["sampler_recorded"]:
                sampler_provenance = item_result.backend_metadata["sampler_provenance"]
                break
        return RuntimeResult(
            events=control.events,
            output_artifacts={"suite_items.jsonl": control.output_jsonl},
            token_count=control.total_prompt_tokens + control.total_output_tokens,
            output_token_count=control.total_output_tokens,
            workload_provenance={
                "prompt": suite_prompt_rollup(
                    control.prompt_hashes, control.total_prompt_tokens
                ),
                "suite": control.suite_provenance,
                "generator": {
                    "name": "mlx_lm.stream_generate",
                    "version": _module_or_distribution_version(self._mlx_lm, "mlx-lm"),
                },
                "sampler": sampler_provenance,
                "tokenizer": _tokenizer_identity(self._tokenizer, config),
                "model": {
                    "source": config.model.source,
                    "revision": config.model.revision,
                    "artifact_identity": self._model_artifact_identity,
                },
                "output_policy": output_policy(
                    manifest.execution_policy.default_output_policy,
                    requested_tokens=control.total_planned_output_tokens,
                    emitted_tokens=control.total_output_tokens,
                    stop_condition="suite_completed",
                ),
            },
        )

exec
/bin/zsh -lc "rg -n 'class .*Runtime|RuntimeAdapter|MLX|mlx|llama|runtime_type|runtime:' joulewise tests docs/contracts configs/examples pyproject.toml | head -n 500" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
pyproject.toml:17:mac = ["mlx-lm>=0.31.3", "transformers<5.13"]
configs/examples/mac_mlx_local.json:3:  "run_id": "example-mac-mlx-local-512t",
configs/examples/mac_mlx_local.json:7:    "source": "/Users/edr/jw_models/mlx-community/Qwen2.5-1.5B-Instruct-4bit",
configs/examples/mac_mlx_local.json:9:    "weight_format": "mlx",
configs/examples/mac_mlx_local.json:19:    "runtime_backend": "mlx",
docs/contracts/claims_ladder.md:37:  where it matters, for example `M3 Max / MLX / powermetrics SoC rails`,
docs/contracts/claims_ladder.md:69:- Two strict-valid Mac/MLX/powermetrics points that differ in model size,
tests/test_controller.py:169:class ExplodingRuntime:
tests/test_controller.py:203:class InterruptingCleanupRuntime:
tests/test_controller.py:226:    def __init__(self, runtime: InterruptingCleanupRuntime) -> None:
tests/test_controller.py:832:class MetadataRuntime:
tests/test_controller.py:858:class MetadataRuntimeRegistry:
tests/test_controller.py:872:class CollidingMetadataRuntime:
tests/test_controller.py:898:class CollidingMetadataRuntimeRegistry:
tests/test_controller.py:931:class CleanupOutcomeRuntime:
configs/examples/nvidia_vllm_ssh.json:6:    "family": "llama",
joulewise/powermetrics_fiducial.py:17:up to one cadence of bias); MLX dispatch/fence latency stays inside the bound
joulewise/powermetrics_fiducial.py:91:    "mlx_version",
joulewise/powermetrics_fiducial.py:227:                "kind": "mlx_matmul",
joulewise/powermetrics_fiducial.py:255:                "MLX dispatch/fence latency stays inside the bound, never subtracted",
joulewise/powermetrics_fiducial.py:271:            "kind": "mlx_matmul",
joulewise/powermetrics_fiducial.py:305:            "MLX dispatch/fence latency stays inside the bound, never subtracted",
joulewise/powermetrics_fiducial.py:1319:    """Drive one GPU pulse of preallocated FP16 MLX matmuls with fencing.
joulewise/powermetrics_fiducial.py:1321:    Returns the number of fenced matmuls issued. Requires ``mlx`` (live
joulewise/powermetrics_fiducial.py:1327:    import mlx.core as mx  # noqa: PLC0415 - live-run-only dependency
joulewise/powermetrics_fiducial.py:1344:    import mlx.core as mx  # noqa: PLC0415 - live-run-only dependency
docs/contracts/token_normalization.md:131:| Runtime + version | Runtime or serving stack name and version, for example MLX, vLLM, llama.cpp, mock, or adapter-specific runtime. | `metadata.runtime`; `metadata.environment.python_packages` for Python package versions such as `mlx`, `mlx-lm`, and `transformers`; `metadata.adapters.runtime` for additive adapter metadata. |
tests/test_calibration_bracketing.py:1110:        changed["mlx_version"] = "different-but-exactly-t1-matched"
configs/examples/mac_mlx_mock_telemetry.json:3:  "run_id": "example-mac-mlx-mock-telemetry",
configs/examples/mac_mlx_mock_telemetry.json:7:    "source": "/Users/edr/jw_models/mlx-community/Qwen2.5-1.5B-Instruct-4bit",
configs/examples/mac_mlx_mock_telemetry.json:9:    "weight_format": "mlx",
configs/examples/mac_mlx_mock_telemetry.json:19:    "runtime_backend": "mlx",
configs/examples/mac_mlx_mock_telemetry.json:22:    "notes": "Slice 2G bring-up: real MLX runtime with mock telemetry. Since P2-008, mock telemetry stamps samples strictly inside the sampling span with a two-sample interior floor, so any power_hz works; 20 Hz kept for sampling-density realism."
configs/examples/mac_mlx_mock_telemetry.json:42:    "tags": ["phase2", "mac", "mlx", "mock-telemetry"]
docs/contracts/adapter_contracts.md:162:- Run prefill-only workload when supported (Phase-3-future: no shipped RuntimeAdapter implements or is required to implement this yet; binding form lands with Phase 3 Stage 3.1/3.2 schema v0.2).
docs/contracts/adapter_contracts.md:171:- `mlx`
docs/contracts/adapter_contracts.md:176:- `llama_cpp`
docs/contracts/adapter_contracts.md:182:`SuiteRuntimeAdapter.run_suite(config, manifest, context, *, order_seed,
docs/contracts/adapter_contracts.md:215:  model, and sampler. MLX adapters must pin greedy/temp-0 by constructing the
docs/contracts/adapter_contracts.md:216:  installed `mlx_lm` sampler and passing it to `stream_generate`; if the
docs/contracts/adapter_contracts.md:242:(MLX uses `add_special_tokens=True`, so BOS is inside the planned prompt
docs/contracts/adapter_contracts.md:539:powermetrics binary sha256, sampling interval, anchor-method version, MLX
configs/examples/mac_mlx_qwen35_122b.json:3:  "run_id": "example-mac-mlx-qwen35-122b-512t",
configs/examples/mac_mlx_qwen35_122b.json:7:    "source": "/Users/edr/jw_models/mlx-community/Qwen3.5-122B-A10B-4bit",
configs/examples/mac_mlx_qwen35_122b.json:9:    "weight_format": "mlx",
configs/examples/mac_mlx_qwen35_122b.json:20:    "runtime_backend": "mlx",
tests/test_environment.py:223:            if distribution == "mlx":
tests/test_environment.py:232:            snapshot["python_packages"]["mlx"],
tests/test_environment.py:236:            snapshot["python_packages"]["mlx-lm"],
tests/test_environment.py:246:            if distribution == "mlx":
tests/test_environment.py:260:                "mlx": {"present": True, "version": "1.2.3"},
tests/test_environment.py:261:                "mlx-lm": {"present": False, "version": None},
tests/test_environment.py:308:            {"mlx", "mlx-lm", "transformers"},
tests/test_environment.py:606:                self.assertEqual(set(value), {"mlx", "mlx-lm", "transformers"})
tests/test_environment.py:661:                self.assertEqual(set(value), {"mlx", "mlx-lm", "transformers"})
docs/contracts/run_bundle_layout.md:17:`stop_condition: "requested_tokens_emitted"`; an MLX underrun is recorded in
docs/contracts/run_bundle_layout.md:215:  version evidence for `mlx`, `mlx-lm`, and `transformers` as additive
docs/contracts/run_bundle_layout.md:349:`phase_start`/`phase_end` records. MLX runs may emit non-overlapping
docs/contracts/run_bundle_layout.md:428:identity plus generator, tokenizer, model, and sampler provenance. For MLX
docs/contracts/run_bundle_layout.md:430:installed `mlx_lm` sampler API was pinned or unavailable (D-047.5).
docs/contracts/run_bundle_layout.md:1007:MLX runtime adapters may record additive memory snapshots at prepare end and
docs/contracts/run_bundle_layout.md:1009:MLX Metal memory stats (`active_memory_bytes`, `cache_memory_bytes`,
docs/contracts/run_bundle_layout.md:1010:`peak_memory_bytes`) when the installed MLX version exposes them. Runtime
docs/contracts/run_bundle_layout.md:1015:measured window and preserves MLX Metal peak fidelity because
docs/contracts/run_bundle_layout.md:1017:snapshot inside the sampled workload window. If MLX exposes a Metal API object
docs/contracts/run_bundle_layout.md:1019:`errors.mlx_metal: "getters_unavailable"` rather than presenting all-null
tests/test_mint_floor_artifact.py:68:        "runtime_version": "mlx-test",
tests/test_mint_floor_artifact.py:82:    def _mlx_file_set_evidence() -> tuple[dict, dict]:
tests/test_mint_floor_artifact.py:90:        raw_config, metadata = self._mlx_file_set_evidence()
tests/test_mint_floor_artifact.py:105:    def test_mint_and_claim_stack_identity_are_bit_identical_for_mlx_file_set(
tests/test_mint_floor_artifact.py:108:        raw_config, metadata = self._mlx_file_set_evidence()
tests/test_mint_floor_artifact.py:119:        self.assertIn("mlx_version", prepare)
tests/test_mint_floor_artifact.py:142:        raw_config, metadata = self._mlx_file_set_evidence()
tests/test_mint_floor_artifact.py:168:        raw_config, metadata = self._mlx_file_set_evidence()
tests/test_mint_floor_artifact.py:177:        prepare["version"] = prepare["mlx_version"]
tests/test_mint_floor_artifact.py:188:        raw_config, metadata = self._mlx_file_set_evidence()
tests/test_mint_floor_artifact.py:198:        prepare.pop("mlx_version", None)
tests/test_mint_floor_artifact.py:199:        prepare.pop("mlx_lm_version", None)
tests/test_mint_floor_artifact.py:215:        raw_config, metadata = self._mlx_file_set_evidence()
docs/contracts/powermetrics_fiducial.md:23:- Workload: preallocated 4096x4096 FP16 MLX matmuls; buffers allocated
docs/contracts/powermetrics_fiducial.md:25:  honest. MLX dispatch/fence latency stays IN the bound and is never
docs/contracts/powermetrics_fiducial.md:78:  use the same hardware, OS build, powermetrics binary, MLX version, sampling
docs/contracts/powermetrics_fiducial.md:144:(`powermetrics_native_second_censored_intersection_v1`), `mlx_version`,
docs/contracts/powermetrics_fiducial.md:152:`sampling_interval_ms`, `anchor_method_version`, `mlx_version`,
joulewise/environment.py:226:            "mlx": _package_version_record("mlx"),
joulewise/environment.py:227:            "mlx-lm": _package_version_record("mlx-lm"),
docs/contracts/measurement_methodology.md:272:- During the measured window the controller only blocks on the runtime: no
tests/test_axi_sb_spike.py:103:        versions = {"mlx-lm": spike.EXPECTED_MLX_LM, "mlx": spike.EXPECTED_MLX}
tests/test_axi_sb_spike.py:119:    def test_import_is_mlx_free(self) -> None:
tests/test_axi_sb_spike.py:120:        self.assertNotIn("mlx", spike.__dict__)
tests/test_axi_sb_spike.py:121:        self.assertNotIn("mlx_lm", spike.__dict__)
tests/test_axi_sb_spike.py:212:        versions = {"mlx-lm": spike.EXPECTED_MLX_LM, "mlx": spike.EXPECTED_MLX}
tests/test_axi_sb_spike.py:238:            versions = {"mlx-lm": spike.EXPECTED_MLX_LM, "mlx": spike.EXPECTED_MLX}
tests/test_axi_sb_spike.py:278:            versions = {"mlx-lm": spike.EXPECTED_MLX_LM, "mlx": spike.EXPECTED_MLX}
tests/test_axi_sb_spike.py:329:            versions = {"mlx-lm": spike.EXPECTED_MLX_LM, "mlx": spike.EXPECTED_MLX}
tests/test_axi_sb_spike.py:394:        mlx = ModuleType("mlx")
tests/test_axi_sb_spike.py:395:        mlx.__path__ = []  # type: ignore[attr-defined]
tests/test_axi_sb_spike.py:396:        mlx_core = ModuleType("mlx.core")
tests/test_axi_sb_spike.py:397:        mlx_core.metal = SimpleNamespace(is_available=lambda: True)  # type: ignore[attr-defined]
tests/test_axi_sb_spike.py:398:        mlx_core.get_peak_memory = lambda: 1  # type: ignore[attr-defined]
tests/test_axi_sb_spike.py:399:        mlx.core = mlx_core  # type: ignore[attr-defined]
tests/test_axi_sb_spike.py:400:        mlx_lm = ModuleType("mlx_lm")
tests/test_axi_sb_spike.py:401:        mlx_lm.__path__ = []  # type: ignore[attr-defined]
tests/test_axi_sb_spike.py:402:        mlx_lm.load = lambda _model: (fake_model, FakeTokenizer())  # type: ignore[attr-defined]
tests/test_axi_sb_spike.py:403:        mlx_lm_generate = ModuleType("mlx_lm.generate")
tests/test_axi_sb_spike.py:404:        mlx_lm_generate.BatchGenerator = FakeBatchGenerator  # type: ignore[attr-defined]
tests/test_axi_sb_spike.py:405:        mlx_lm.generate = mlx_lm_generate  # type: ignore[attr-defined]
tests/test_axi_sb_spike.py:409:            "mlx": mlx,
tests/test_axi_sb_spike.py:410:            "mlx.core": mlx_core,
tests/test_axi_sb_spike.py:411:            "mlx_lm": mlx_lm,
tests/test_axi_sb_spike.py:412:            "mlx_lm.generate": mlx_lm_generate,
tests/test_axi_sb_spike.py:436:            versions = {"mlx-lm": spike.EXPECTED_MLX_LM, "mlx": spike.EXPECTED_MLX}
tests/test_axi_mock_spec.py:13:    MockSpecRuntimeAdapter,
tests/test_axi_mock_spec.py:22:from joulewise.interfaces import AxiCancelledProposalCounters, RuntimeAdapter
tests/test_axi_mock_spec.py:69:            MockSpecRuntimeAdapter(
tests/test_axi_mock_spec.py:126:        adapter = MockSpecRuntimeAdapter(FakeClock())
tests/test_axi_mock_spec.py:127:        self.assertIsInstance(adapter, RuntimeAdapter)
tests/test_axi_mock_spec.py:146:                result = MockSpecRuntimeAdapter(FakeClock(start=1000.0)).run_workload(
tests/test_axi_mock_spec.py:199:                result = MockSpecRuntimeAdapter(
tests/test_axi_mock_spec.py:230:        result = MockSpecRuntimeAdapter(FakeClock(start=1000.0)).run_workload(config)
tests/test_axi_mock_spec.py:286:                result = MockSpecRuntimeAdapter(
tests/test_axi_sc_spike.py:28:        "generate_path": "/fake/mlx_lm/generate.py",
tests/test_axi_sc_spike.py:31:        "qwen3_5_path": "/fake/mlx_lm/models/qwen3_5.py",
tests/test_axi_sc_spike.py:67:        "runtime_backend": "mlx-lm",
tests/test_axi_sc_spike.py:68:        "runtime_version": spike.EXPECTED_MLX_LM,
tests/test_axi_sc_spike.py:238:        versions = {"mlx-lm": spike.EXPECTED_MLX_LM, "mlx": spike.EXPECTED_MLX}
tests/test_axi_sc_spike.py:256:    def test_import_is_mlx_free(self) -> None:
tests/test_axi_sc_spike.py:257:        self.assertNotIn("mlx", spike.__dict__)
tests/test_axi_sc_spike.py:258:        self.assertNotIn("mlx_lm", spike.__dict__)
tests/test_axi_sc_spike.py:448:                "mlx-lm": spike.EXPECTED_MLX_LM,
tests/test_axi_sc_spike.py:449:                "mlx": spike.EXPECTED_MLX,
tests/test_axi_sc_spike.py:482:                "mlx-lm": spike.EXPECTED_MLX_LM,
tests/test_axi_sc_spike.py:483:                "mlx": spike.EXPECTED_MLX,
tests/test_axi_sc_spike.py:554:        mlx = ModuleType("mlx")
tests/test_axi_sc_spike.py:555:        mlx.__path__ = []  # type: ignore[attr-defined]
tests/test_axi_sc_spike.py:556:        mlx_core = ModuleType("mlx.core")
tests/test_axi_sc_spike.py:557:        mlx_core.metal = SimpleNamespace(is_available=lambda: True)  # type: ignore[attr-defined]
tests/test_axi_sc_spike.py:558:        mlx.core = mlx_core  # type: ignore[attr-defined]
tests/test_axi_sc_spike.py:559:        mlx_lm = ModuleType("mlx_lm")
tests/test_axi_sc_spike.py:560:        mlx_lm.load = fake_load  # type: ignore[attr-defined]
tests/test_axi_sc_spike.py:561:        mlx_lm.stream_generate = fake_stream_generate  # type: ignore[attr-defined]
tests/test_axi_sc_spike.py:562:        modules = {"mlx": mlx, "mlx.core": mlx_core, "mlx_lm": mlx_lm}
tests/test_axi_sc_spike.py:638:        mlx = ModuleType("mlx")
tests/test_axi_sc_spike.py:639:        mlx.__path__ = []  # type: ignore[attr-defined]
tests/test_axi_sc_spike.py:640:        mlx_core = ModuleType("mlx.core")
tests/test_axi_sc_spike.py:641:        mlx_core.metal = SimpleNamespace(is_available=lambda: True)  # type: ignore[attr-defined]
tests/test_axi_sc_spike.py:642:        mlx.core = mlx_core  # type: ignore[attr-defined]
tests/test_axi_sc_spike.py:643:        mlx_lm = ModuleType("mlx_lm")
tests/test_axi_sc_spike.py:644:        mlx_lm.load = fake_load  # type: ignore[attr-defined]
tests/test_axi_sc_spike.py:645:        mlx_lm.stream_generate = fake_stream_generate  # type: ignore[attr-defined]
tests/test_axi_sc_spike.py:646:        modules = {"mlx": mlx, "mlx.core": mlx_core, "mlx_lm": mlx_lm}
tests/test_cli_run.py:60:    "example-mac-mlx-local__r1",
tests/test_cli_run.py:190:            ("mlx", "mock", SystemClock),
tests/test_cli_run.py:191:            ("mlx", "powermetrics", SystemClock),
joulewise/bundle_read.py:131:            "example-mac-mlx-local__r1",
joulewise/bundle_read.py:135:            "example-mac-mlx-local__r2",
joulewise/bundle_read.py:139:            "example-mac-mlx-local__r3",
joulewise/bundle_read.py:143:            "example-mac-mlx-qwen35-122b-512t__r1",
joulewise/bundle_read.py:147:            "example-mac-mlx-qwen35-122b-512t__r2",
joulewise/bundle_read.py:151:            "example-mac-mlx-qwen35-122b-512t__r3",
joulewise/cli.py:982:    is_mlx_single = (
joulewise/cli.py:985:        and generator.get("name") == "mlx_lm.stream_generate"
joulewise/cli.py:1030:        is_mlx_single
joulewise/cli.py:1039:    if is_mlx_single and name in {FIXED_BUDGET_EXACT, FIXED_BUDGET_INCOMPLETE}:
joulewise/interfaces.py:186:class RuntimeEvent:
joulewise/interfaces.py:287:class AxiRuntimeResult:
joulewise/interfaces.py:297:class RuntimeResult:
joulewise/interfaces.py:337:class RuntimeAdapter(Protocol):
joulewise/interfaces.py:364:class SuiteRuntimeAdapter(RuntimeAdapter, Protocol):
joulewise/publication_privacy.py:305:class PrivacyAuditError(RuntimeError):
tests/test_detection_floor.py:321:        "runtime_version": "mlx 1.0",
tests/test_detection_floor.py:2013:        ] = "mlx 1.0-mutated"
joulewise/analysis_manifest_v3.py:66:        "model_tag": "qwen25-1p5b-mlx",
joulewise/analysis_manifest_v3.py:77:                "backend": "mlx",
joulewise/analysis_manifest_v3.py:79:                    "/Users/edr/jw_models/mlx-community/"
joulewise/analysis_manifest_v3.py:86:            "runtime": {"name": "mlx", "adapter": "mlx_runtime", "version": None},
joulewise/analysis_manifest_v3.py:98:                    "/Users/edr/jw_models/mlx-community/"
joulewise/analysis_manifest_v3.py:102:                "weight_format": "mlx",
joulewise/analysis_manifest_v3.py:119:        "model_tag": "qwen25-7b-mlx",
joulewise/analysis_manifest_v3.py:130:                "backend": "mlx",
joulewise/analysis_manifest_v3.py:132:                    "/Users/edr/jw_models/mlx-community/Qwen2.5-7B-Instruct-4bit"
joulewise/analysis_manifest_v3.py:138:            "runtime": {"name": "mlx", "adapter": "mlx_runtime", "version": None},
joulewise/analysis_manifest_v3.py:150:                    "/Users/edr/jw_models/mlx-community/Qwen2.5-7B-Instruct-4bit"
joulewise/analysis_manifest_v3.py:153:                "weight_format": "mlx",
tests/test_experiment.py:94:class FloatRuntime:
tests/test_experiment.py:99:class EqRuntime:
tests/test_experiment.py:459:class _KillingRuntime:
tests/test_experiment.py:1134:        class PowerFlippingRuntime:
joulewise/reduce.py:1610:    mlx = packages.get("mlx") if isinstance(packages, dict) else None
joulewise/reduce.py:1616:        "mlx_version": mlx.get("version") if isinstance(mlx, dict) else None,
tests/test_env_locks.py:20:CANONICAL_BUNDLE_METADATA = REPO_ROOT / "runs" / "example-mac-mlx-local__r1" / "metadata.json"
tests/test_env_locks.py:61:            "mlx": prepare["mlx_version"],
tests/test_env_locks.py:62:            "mlx-lm": prepare["mlx_lm_version"],
joulewise/schemas.py:207:class RuntimeBackend(str, Enum):
joulewise/schemas.py:209:    MLX = "mlx"
joulewise/schemas.py:211:    LLAMA_CPP = "llama_cpp"
tests/test_mock_adapters.py:13:    MockRuntimeAdapter,
tests/test_mock_adapters.py:27:    RuntimeAdapter,
tests/test_mock_adapters.py:183:        self.assertIsInstance(MockRuntimeAdapter(FakeClock()), RuntimeAdapter)
tests/test_mock_adapters.py:192:class MockRuntimeTests(unittest.TestCase):
tests/test_mock_adapters.py:195:        self.runtime = MockRuntimeAdapter(self.clock)
tests/test_mock_adapters.py:831:        self.assertIsInstance(adapter, RuntimeAdapter)
tests/test_mock_adapters.py:866:    def test_mlx_runtime_failure_names_backend_and_mac_extra(self) -> None:
tests/test_mock_adapters.py:867:        config = make_config(hardware_target={"runtime_backend": "mlx"})
tests/test_mock_adapters.py:877:        self.assertIn("mlx", failure.message)
tests/test_mock_adapters.py:880:    def test_resolves_mlx_runtime_adapter_without_importing_mlx_lm(self) -> None:
tests/test_mock_adapters.py:881:        config = make_config(hardware_target={"runtime_backend": "mlx"})
tests/test_mock_adapters.py:884:        self.assertEqual(adapter.name, "mlx")
tests/test_mock_adapters.py:899:        for backend in ("llama_cpp", "hailo"):
joulewise/controller.py:101:    RuntimeAdapter,
joulewise/controller.py:104:    SuiteRuntimeAdapter,
joulewise/controller.py:225:    ) -> tuple[RuntimeAdapter | None, AdapterResult | None]: ...
joulewise/controller.py:777:        self._runtime: RuntimeAdapter | None = None
joulewise/controller.py:2320:    def _validate_suite_manifest_if_present(self, runtime: RuntimeAdapter) -> None:
joulewise/controller.py:2324:        if not isinstance(runtime, SuiteRuntimeAdapter) or not callable(
tests/test_bundle_read.py:49:from joulewise.adapters.mock_runtime import MockRuntimeAdapter
tests/test_bundle_read.py:436:class RuntimeCleanupQualityTests(ReaderTestCase):
tests/test_bundle_read.py:600:        runtime = MockRuntimeAdapter(FakeClock(start=1.0))
joulewise/determinism_gate.py:90:_PACKAGE_IDENTITIES = ("mlx", "mlx-lm", "transformers")
tests/test_powermetrics_fiducial.py:575:            "mlx_version": "0.30.0",
tests/test_suite_control_parity.py:1:"""Literal contract fixtures defending mock/MLX suite-control parity."""
tests/test_suite_control_parity.py:10:from joulewise.adapters.mlx_runtime import MlxRuntimeAdapter
tests/test_suite_control_parity.py:11:from joulewise.adapters.mock_runtime import MockRuntimeAdapter
tests/test_suite_control_parity.py:22:        "weight_format": "mlx",
tests/test_suite_control_parity.py:307:EXPECTED_MLX_PROMPT_PROVENANCE = {
tests/test_suite_control_parity.py:328:    __version__ = "literal-mlx-1"
tests/test_suite_control_parity.py:435:        self.mock = MockRuntimeAdapter(FakeClock(start=1000.0))
tests/test_suite_control_parity.py:436:        self.mlx = MlxRuntimeAdapter(FakeClock(start=1000.0))
tests/test_suite_control_parity.py:437:        self.mlx._mlx_lm = LiteralMlxLm()
tests/test_suite_control_parity.py:438:        self.mlx._model = object()
tests/test_suite_control_parity.py:439:        self.mlx._tokenizer = LiteralTokenizer()
tests/test_suite_control_parity.py:447:        mlx_result = self.mlx.run_suite(
tests/test_suite_control_parity.py:452:        return mock_result, mlx_result
tests/test_suite_control_parity.py:455:        mock_result, mlx_result = self.run_backends()
tests/test_suite_control_parity.py:457:        for result in (mock_result, mlx_result):
tests/test_suite_control_parity.py:488:        self.assertEqual(_item_start_projection(mock_result), _item_start_projection(mlx_result))
tests/test_suite_control_parity.py:489:        self.assertEqual(_item_end_projection(mock_result), _item_end_projection(mlx_result))
tests/test_suite_control_parity.py:492:        mock_result, mlx_result = self.run_backends()
tests/test_suite_control_parity.py:494:        mlx_records = _records(mlx_result)
tests/test_suite_control_parity.py:503:        for records in (mock_records, mlx_records):
tests/test_suite_control_parity.py:513:        self.assertEqual(mlx_records[2]["status_reason"], "prompt_ids_mismatch")
tests/test_suite_control_parity.py:516:            mlx_records[3]["status_reason"],
tests/test_suite_control_parity.py:524:            mlx_result.workload_provenance["generator"],
tests/test_suite_control_parity.py:525:            {"name": "mlx_lm.stream_generate", "version": "literal-mlx-1"},
tests/test_suite_control_parity.py:533:                "class": "MockRuntimeAdapter",
tests/test_suite_control_parity.py:538:            mlx_result.workload_provenance["tokenizer"],
tests/test_suite_control_parity.py:540:                "backend": "mlx",
tests/test_suite_control_parity.py:552:            mlx_result.workload_provenance["prompt"],
tests/test_suite_control_parity.py:553:            EXPECTED_MLX_PROMPT_PROVENANCE,
tests/test_mlx_runtime.py:1:"""CI-safe tests for the MLX runtime adapter (Slice 2G)."""
tests/test_mlx_runtime.py:16:from joulewise.adapters.mlx_runtime import (
tests/test_mlx_runtime.py:17:    MlxRuntimeAdapter,
tests/test_mlx_runtime.py:18:    _mlx_metal_memory,
tests/test_mlx_runtime.py:22:from joulewise.adapters.mock_runtime import MockRuntimeAdapter
tests/test_mlx_runtime.py:41:from scripts import spike_mlx_prompt_cache
tests/test_mlx_runtime.py:52:            "name": "fake-mlx-model",
tests/test_mlx_runtime.py:54:            "source": "/tmp/fake-mlx-model",
tests/test_mlx_runtime.py:55:            "weight_format": "mlx",
tests/test_mlx_runtime.py:61:            "runtime_backend": "mlx",
tests/test_mlx_runtime.py:65:            "name": "fake_mlx_smoke",
tests/test_mlx_runtime.py:225:            "suite_id": "mlx_suite",
tests/test_mlx_runtime.py:226:            "suite_profile": "mlx_suite_v1",
tests/test_mlx_runtime.py:267:class MlxRuntimeTests(unittest.TestCase):
tests/test_mlx_runtime.py:268:    def prepared_adapter(self, pieces: list[str]) -> tuple[MlxRuntimeAdapter, FakeMlxLm]:
tests/test_mlx_runtime.py:269:        adapter = MlxRuntimeAdapter(FakeClock(start=1000.0))
tests/test_mlx_runtime.py:270:        fake_mlx = FakeMlxLm(pieces)
tests/test_mlx_runtime.py:271:        adapter._mlx_lm = fake_mlx
tests/test_mlx_runtime.py:274:        return adapter, fake_mlx
tests/test_mlx_runtime.py:277:        adapter = MlxRuntimeAdapter(FakeClock())
tests/test_mlx_runtime.py:280:            raise ImportError("no module named mlx_lm")
tests/test_mlx_runtime.py:282:        adapter._import_mlx_lm = raise_import_error  # type: ignore[method-assign]
tests/test_mlx_runtime.py:290:        adapter, fake_mlx = self.prepared_adapter(["x", "y"])
tests/test_mlx_runtime.py:301:        prompt = fake_mlx.calls[0]["prompt"]
tests/test_mlx_runtime.py:304:        self.assertEqual(fake_mlx.calls[0]["max_tokens"], 2)
tests/test_mlx_runtime.py:305:        self.assertEqual(fake_mlx.calls[0]["eos_token_ids_during_call"], set())
tests/test_mlx_runtime.py:410:                    ("mono_meta.json", {"mlx_lm_version": "test", "mlx_version": "test"}),
tests/test_mlx_runtime.py:416:                    spike_mlx_prompt_cache, "predict_cache_bytes", return_value=100
tests/test_mlx_runtime.py:418:                    report = spike_mlx_prompt_cache.assemble_report(
tests/test_mlx_runtime.py:444:                    "message": "mlx tokenization started",
tests/test_mlx_runtime.py:451:                    "message": "mlx tokenization completed",
tests/test_mlx_runtime.py:458:                    "message": "mlx generation setup started",
tests/test_mlx_runtime.py:465:                    "message": "mlx generation setup completed",
tests/test_mlx_runtime.py:475:                    "message": "mlx prefill started",
tests/test_mlx_runtime.py:487:                    "message": "mlx prefill completed",
tests/test_mlx_runtime.py:494:                    "message": "mlx decode started",
tests/test_mlx_runtime.py:506:                    "message": "mlx token 0",
tests/test_mlx_runtime.py:513:                    "message": "mlx token 1",
tests/test_mlx_runtime.py:520:                    "message": "mlx token 2",
tests/test_mlx_runtime.py:527:                    "message": "mlx decode completed",
tests/test_mlx_runtime.py:538:        adapter = MlxRuntimeAdapter(FakeClock(start=1000.0))
tests/test_mlx_runtime.py:539:        fake_mlx = FakeMlxLm(["A"])
tests/test_mlx_runtime.py:545:        fake_mlx.load = fake_load  # type: ignore[attr-defined]
tests/test_mlx_runtime.py:546:        adapter._import_mlx_lm = lambda: fake_mlx  # type: ignore[method-assign]
tests/test_mlx_runtime.py:553:                "mlx_metal": {
tests/test_mlx_runtime.py:599:        adapter, fake_mlx = self.prepared_adapter(["A"])
tests/test_mlx_runtime.py:602:        generated_prompt = fake_mlx.calls[0]["prompt"]
tests/test_mlx_runtime.py:610:        adapter, fake_mlx = self.prepared_adapter(["A", "B"])
tests/test_mlx_runtime.py:659:        self.assertEqual(fake_mlx.calls[0]["prompt"], [7, 8, 9])
tests/test_mlx_runtime.py:660:        self.assertEqual(fake_mlx.calls[1]["prompt"], [1, 10, 11])
tests/test_mlx_runtime.py:661:        self.assertEqual(len(fake_mlx.calls[2]["prompt"]), 4)
tests/test_mlx_runtime.py:662:        self.assertEqual(fake_mlx.calls[0]["eos_token_ids_during_call"], set())
tests/test_mlx_runtime.py:663:        self.assertEqual(fake_mlx.calls[1]["eos_token_ids_during_call"], {99})
tests/test_mlx_runtime.py:664:        self.assertEqual(fake_mlx.calls[2]["eos_token_ids_during_call"], set())
tests/test_mlx_runtime.py:683:    def test_mock_and_mlx_suite_realized_plans_match_under_rotation(self) -> None:
tests/test_mlx_runtime.py:691:        mlx_adapter, _ = self.prepared_adapter(["A", "B", "C"])
tests/test_mlx_runtime.py:692:        mock_adapter = MockRuntimeAdapter(FakeClock(start=1000.0))
tests/test_mlx_runtime.py:694:        mlx_result = mlx_adapter.run_suite(
tests/test_mlx_runtime.py:714:        mlx_item_indices = item_start_indices(mlx_result)
tests/test_mlx_runtime.py:715:        self.assertEqual(mlx_item_indices, item_start_indices(mock_result))
tests/test_mlx_runtime.py:717:        mlx_records = [
tests/test_mlx_runtime.py:719:            for line in mlx_result.output_artifacts["suite_items.jsonl"].splitlines()
tests/test_mlx_runtime.py:721:        self.assertTrue(all("position" in record for record in mlx_records))
tests/test_mlx_runtime.py:722:        self.assertEqual([record["item_index"] for record in mlx_records], mlx_item_indices)
tests/test_mlx_runtime.py:723:        self.assertEqual([record["position"] for record in mlx_records], [0, 1, 2])
tests/test_mlx_runtime.py:726:        adapter = MlxRuntimeAdapter(FakeClock(start=1000.0))
tests/test_mlx_runtime.py:727:        fake_mlx = FakeMlxLm(["A"], fail_call_indices={1})
tests/test_mlx_runtime.py:728:        adapter._mlx_lm = fake_mlx
tests/test_mlx_runtime.py:856:        adapter = MlxRuntimeAdapter(FakeClock(start=1000.0))
tests/test_mlx_runtime.py:857:        adapter._mlx_lm = NoSamplerMlx(["A"])
tests/test_mlx_runtime.py:871:        adapter = MlxRuntimeAdapter(FakeClock(start=1000.0))
tests/test_mlx_runtime.py:872:        fake_mlx = FakeMlxLm(["A"])
tests/test_mlx_runtime.py:873:        fake_mlx.make_sampler = None  # type: ignore[assignment]
tests/test_mlx_runtime.py:874:        adapter._mlx_lm = fake_mlx
tests/test_mlx_runtime.py:889:                "reason": "mlx_lm sampler API unavailable",
tests/test_mlx_runtime.py:894:        adapter = MlxRuntimeAdapter(FakeClock(start=1000.0))
tests/test_mlx_runtime.py:895:        fake_mlx = FakeMlxLm(["A"])
tests/test_mlx_runtime.py:896:        fake_mlx.make_sampler = None  # type: ignore[assignment]
tests/test_mlx_runtime.py:897:        fake_mlx.sample_utils = SimpleNamespace(make_sampler=None)
tests/test_mlx_runtime.py:898:        adapter._mlx_lm = fake_mlx
tests/test_mlx_runtime.py:913:                "reason": "mlx_lm sampler API unavailable",
tests/test_mlx_runtime.py:922:        adapter = MlxRuntimeAdapter(FakeClock(start=1000.0))
tests/test_mlx_runtime.py:923:        adapter._mlx_lm = BadSamplerMlx(["A"])
tests/test_mlx_runtime.py:938:                "reason": "mlx_lm sampler API unavailable",
tests/test_mlx_runtime.py:948:        adapter = MlxRuntimeAdapter(FakeClock(start=1000.0))
tests/test_mlx_runtime.py:949:        fake_mlx = FakeMlxLmWithSampler(["A"])
tests/test_mlx_runtime.py:950:        adapter._mlx_lm = fake_mlx
tests/test_mlx_runtime.py:966:            fake_mlx.samplers_built,
tests/test_mlx_runtime.py:969:        self.assertIsNotNone(fake_mlx.calls[0]["sampler"])
tests/test_mlx_runtime.py:970:        self.assertIsNotNone(fake_mlx.calls[1]["sampler"])
tests/test_mlx_runtime.py:973:        # Installed mlx_lm exposes make_sampler under sample_utils, not
tests/test_mlx_runtime.py:975:        adapter = MlxRuntimeAdapter(FakeClock(start=1000.0))
tests/test_mlx_runtime.py:976:        fake_mlx = FakeMlxLmWithSampler(["A"])
tests/test_mlx_runtime.py:977:        fake_mlx.sample_utils = SimpleNamespace(make_sampler=fake_mlx.make_sampler)
tests/test_mlx_runtime.py:978:        fake_mlx.make_sampler = None  # type: ignore[assignment]
tests/test_mlx_runtime.py:979:        adapter._mlx_lm = fake_mlx
tests/test_mlx_runtime.py:986:        self.assertEqual(sampler["api"], "mlx_lm.sample_utils.make_sampler")
tests/test_mlx_runtime.py:993:        adapter = MlxRuntimeAdapter(clock)
tests/test_mlx_runtime.py:994:        fake_mlx = FakeMlxLm(["A"])
tests/test_mlx_runtime.py:995:        adapter._mlx_lm = fake_mlx
tests/test_mlx_runtime.py:1046:        adapter = MlxRuntimeAdapter(FakeClock(start=1000.0))
tests/test_mlx_runtime.py:1047:        fake_mlx = FakeMlxLmWithSampler(["A"])
tests/test_mlx_runtime.py:1048:        adapter._mlx_lm = fake_mlx
tests/test_mlx_runtime.py:1088:        with patch("joulewise.adapters.mlx_runtime.subprocess.run", side_effect=fake_run):
tests/test_mlx_runtime.py:1098:        with patch("joulewise.adapters.mlx_runtime.subprocess.run", side_effect=fake_run):
tests/test_mlx_runtime.py:1102:    def test_mlx_metal_memory_success(self) -> None:
tests/test_mlx_runtime.py:1104:        fake_core = ModuleType("mlx.core")
tests/test_mlx_runtime.py:1110:        previous = sys.modules.get("mlx.core")
tests/test_mlx_runtime.py:1111:        sys.modules["mlx.core"] = fake_core
tests/test_mlx_runtime.py:1114:                _mlx_metal_memory(errors),
tests/test_mlx_runtime.py:1124:                sys.modules.pop("mlx.core", None)
tests/test_mlx_runtime.py:1126:                sys.modules["mlx.core"] = previous
tests/test_mlx_runtime.py:1129:    def test_mlx_metal_memory_missing_api(self) -> None:
tests/test_mlx_runtime.py:1131:        fake_core = ModuleType("mlx.core")
tests/test_mlx_runtime.py:1132:        previous = sys.modules.get("mlx.core")
tests/test_mlx_runtime.py:1133:        sys.modules["mlx.core"] = fake_core
tests/test_mlx_runtime.py:1136:                _mlx_metal_memory(errors),
tests/test_mlx_runtime.py:1146:                sys.modules.pop("mlx.core", None)
tests/test_mlx_runtime.py:1148:                sys.modules["mlx.core"] = previous
tests/test_mlx_runtime.py:1151:    def test_mlx_metal_memory_available_api_without_values_records_error(self) -> None:
tests/test_mlx_runtime.py:1153:        fake_core = ModuleType("mlx.core")
tests/test_mlx_runtime.py:1159:        previous = sys.modules.get("mlx.core")
tests/test_mlx_runtime.py:1160:        sys.modules["mlx.core"] = fake_core
tests/test_mlx_runtime.py:1163:                _mlx_metal_memory(errors),
tests/test_mlx_runtime.py:1173:                sys.modules.pop("mlx.core", None)
tests/test_mlx_runtime.py:1175:                sys.modules["mlx.core"] = previous
tests/test_mlx_runtime.py:1176:        self.assertEqual(errors["mlx_metal"], "getters_unavailable")
tests/test_mlx_runtime.py:1177:        self.assertEqual(errors["mlx_metal.get_active_memory"], "non_numeric")
tests/test_mlx_runtime.py:1178:        self.assertEqual(errors["mlx_metal.get_cache_memory"], "non_numeric")
tests/test_mlx_runtime.py:1179:        self.assertIn("RuntimeError: boom", errors["mlx_metal.get_peak_memory"])
tests/test_analysis_claims.py:763:    def _bind_mlx_file_set_floor(
tests/test_analysis_claims.py:897:        binding = self._bind_mlx_file_set_floor(metadata)
tests/test_analysis_claims.py:937:                binding = self._bind_mlx_file_set_floor(metadata)
tests/test_analysis_integration.py:313:def _real_mlx_identity_inputs(arm_id: str) -> tuple[dict, dict]:
tests/test_analysis_integration.py:314:    """Adapt a real MLX metadata boundary to either frozen v3 arm."""
tests/test_analysis_integration.py:367:        raw_config, metadata = _real_mlx_identity_inputs(entry["arm_id"])
tests/test_axi_analysis_manifest.py:282:                    str(ROOT / "configs" / "examples" / "mac_mlx_local.json"),
tests/test_rpt001_report_slice.py:52:        expected = "LEGACY-M3MAX-QWEN25-1P5B-MLX"
tests/test_rpt001_report_slice.py:53:        self.assertEqual(make_figures.STACK_IDS["example-mac-mlx-local"], expected)
tests/test_rpt001_report_slice.py:55:        self.assertNotIn("LEGACY-M3MAX-QWEN25-15B-MLX", REPO.joinpath(
tests/test_rpt001_report_slice.py:192:            member = "example-mac-mlx-local__r1"
tests/test_rpt001_report_slice.py:216:                {"example-mac-mlx-local": {"members": [member], "cooldown": []}},
tests/test_rpt001_report_slice.py:297:            [f"example-mac-mlx-local__r{i}" for i in (1, 2, 3)]
tests/test_rpt001_report_slice.py:298:            + [f"example-mac-mlx-qwen35-122b-512t__r{i}" for i in (1, 2, 3)],
joulewise/quiet_guard.py:144:class GuardError(RuntimeError):
tests/test_cli.py:177:                "mlx_lm.stream_generate"
tests/test_gensuite.py:368:    def test_repeated_seed_mirrors_mlx_recipe(self) -> None:
tests/test_gensuite.py:384:    def test_repeated_seed_mirrors_mlx_runtime_recipe(self) -> None:
tests/test_gensuite.py:386:            mlx_runtime = importlib.import_module("joulewise.adapters.mlx_runtime")
tests/test_gensuite.py:388:            self.skipTest(f"mlx runtime not importable: {exc}")
tests/test_gensuite.py:396:        self.assertEqual(mlx_runtime._synthetic_prompt_tokens(tokenizer, 512), expected)
tests/test_p2038_production_path.py:3:This CI test uses a mock runtime only to avoid an MLX dependency. Telemetry is
tests/test_p2038_production_path.py:108:        "python_packages": {"mlx": {"version": "p2038-test-mlx"}},
tests/test_p2038_production_path.py:164:        "mlx_version": "p2038-test-mlx",
tests/test_axi_controller_events.py:45:class FakeAxiRuntime:
tests/test_vllm_runtime.py:17:    VllmRuntimeAdapter,
tests/test_vllm_runtime.py:34:            "family": "llama",
tests/test_vllm_runtime.py:35:            "source": "/models/tinyllama",
tests/test_vllm_runtime.py:175:class VllmRuntimeAdapterTests(unittest.TestCase):
tests/test_vllm_runtime.py:188:        adapter = VllmRuntimeAdapter(FakeClock(), client)  # type: ignore[arg-type]
tests/test_vllm_runtime.py:200:        self.assertEqual(task["runtime"]["model"]["source"], "/models/tinyllama")
tests/test_vllm_runtime.py:205:            "tinyllama-tinyllama-1-1b-chat-v1-0-joulewise",
tests/test_vllm_runtime.py:209:        adapter = VllmRuntimeAdapter(
tests/test_vllm_runtime.py:229:        adapter = VllmRuntimeAdapter(
tests/test_vllm_runtime.py:253:            adapter = VllmRuntimeAdapter(FakeClock(), client)  # type: ignore[arg-type]
tests/test_vllm_runtime.py:299:            adapter = VllmRuntimeAdapter(FakeClock(), client)  # type: ignore[arg-type]
tests/test_vllm_runtime.py:320:            adapter = VllmRuntimeAdapter(FakeClock(), client)  # type: ignore[arg-type]
tests/test_vllm_runtime.py:341:            adapter = VllmRuntimeAdapter(FakeClock(), FakeClient([task]))  # type: ignore[arg-type]
tests/test_vllm_runtime.py:351:        adapter = VllmRuntimeAdapter(
tests/test_vllm_runtime.py:382:            adapter = VllmRuntimeAdapter(FakeClock(), FakeClient([result]))  # type: ignore[arg-type]
tests/test_vllm_runtime.py:401:        adapter = VllmRuntimeAdapter(FakeClock(), client)  # type: ignore[arg-type]
tests/test_schemas.py:47:    "mac_mlx_local.json": "e9878c0ed7735eb48293581b0944c1f5e1d08e67c9b77f0fafd8c4c265020f3e",
tests/test_schemas.py:48:    "mac_mlx_mock_telemetry.json": "4023dee935eb17d1a4da1f2bd90af9404de2eca33f1df9c41382e4750fd93eda",
tests/test_schemas.py:49:    "mac_mlx_qwen35_122b.json": "100d76977dffab1ae841124c4708727ac45ab793bbe0061dd87a6d9f54dbb97a",
tests/test_schemas.py:332:        self.assertIn("mlx", schema["$defs"]["hardware_target"]["properties"]["runtime_backend"]["enum"])
tests/test_analysis_manifest_v3.py:137:    def test_real_mlx_metadata_file_set_folded_sha256_normalizes(self) -> None:
tests/test_generate_matrix.py:17:    (ROOT / "configs" / "examples" / "mac_mlx_local.json", "qwen25-1p5b"),
tests/test_generate_matrix.py:18:    (ROOT / "configs" / "examples" / "mac_mlx_qwen35_122b.json", "qwen35-122b"),
tests/test_doctor.py:27:BASE_CONFIG = ROOT / "configs" / "examples" / "mac_mlx_local.json"
tests/test_doctor.py:52:            "mlx": {"present": True, "version": "0.29.0"},
tests/test_doctor.py:97:            "/Users/edr/jw_models/mlx-community/Qwen2.5-1.5B-Instruct-4bit",
tests/test_audit_amplification.py:33:    "example-mac-mlx-local__r1",
joulewise/adapters/mock_runtime.py:14:- ``model.name == "mock-unsupported"`` makes :meth:`MockRuntimeAdapter.prepare`
joulewise/adapters/mock_runtime.py:33:from joulewise.adapters.mock_spec_runtime import MockSpecRuntimeAdapter
joulewise/adapters/mock_runtime.py:69:class MockRuntimeAdapter:
joulewise/adapters/mock_runtime.py:70:    """Deterministic, clock-driven implementation of ``RuntimeAdapter``."""
joulewise/adapters/mock_runtime.py:76:        self._mock_spec = MockSpecRuntimeAdapter(clock)
joulewise/adapters/mock_runtime.py:176:                    "class": "MockRuntimeAdapter",
joulewise/adapters/mock_runtime.py:241:                    "class": "MockRuntimeAdapter",
tests/test_reduce.py:213:        "mlx_version": "0.31.2",
tests/test_reduce.py:1470:            "example-mac-mlx-qwen35-122b-512t__r1",
tests/test_reduce.py:3742:            ("mlx_version", "999.0"),
tests/fixtures/cooldown_join/real_7b_v1_existing_manifest.json:196:        "mlx": {
tests/fixtures/cooldown_join/real_7b_v1_existing_manifest.json:200:        "mlx-lm": {
tests/test_run_campaign.py:2022:            "python_packages": {"mlx": {"version": "test"}},
joulewise/adapters/__init__.py:13:Implemented backends in this slice: runtime ``mock``, ``mlx``, and remote
joulewise/adapters/__init__.py:24:from joulewise.adapters.mock_runtime import MockRuntimeAdapter
joulewise/adapters/__init__.py:29:    RuntimeAdapter,
joulewise/adapters/__init__.py:43:    "MlxRuntimeAdapter",
joulewise/adapters/__init__.py:44:    "MockRuntimeAdapter",
joulewise/adapters/__init__.py:49:    "VllmRuntimeAdapter",
joulewise/adapters/__init__.py:57:    if name == "MlxRuntimeAdapter":
joulewise/adapters/__init__.py:58:        module = importlib.import_module("joulewise.adapters.mlx_runtime")
joulewise/adapters/__init__.py:59:        return module.MlxRuntimeAdapter
joulewise/adapters/__init__.py:66:    if name == "VllmRuntimeAdapter":
joulewise/adapters/__init__.py:68:        return module.VllmRuntimeAdapter
joulewise/adapters/__init__.py:119:) -> tuple[RuntimeAdapter | None, AdapterResult | None]:
joulewise/adapters/__init__.py:123:        return MockRuntimeAdapter(clock), None
joulewise/adapters/__init__.py:124:    if backend == RuntimeBackend.MLX:
joulewise/adapters/__init__.py:126:            module = importlib.import_module("joulewise.adapters.mlx_runtime")
joulewise/adapters/__init__.py:130:                "runtime backend 'mlx' could not import its adapter; the MLX "
joulewise/adapters/__init__.py:134:        return module.MlxRuntimeAdapter(clock), None
joulewise/adapters/__init__.py:146:        return module.VllmRuntimeAdapter(clock, client), None
tests/fixtures/d078_r01/metadata.json:9:            "mlx_metal": {
tests/fixtures/d078_r01/metadata.json:19:      "name": "mlx",
tests/fixtures/d078_r01/metadata.json:21:        "adapter": "mlx_runtime",
tests/fixtures/d078_r01/metadata.json:27:            "mlx_metal": {
tests/fixtures/d078_r01/metadata.json:36:        "mlx_lm_version": "0.31.3",
tests/fixtures/d078_r01/metadata.json:37:        "mlx_version": "0.31.2",
tests/fixtures/d078_r01/metadata.json:45:          "root": "/Users/edr/jw_models/mlx-community/Qwen2.5-1.5B-Instruct-4bit",
tests/fixtures/d078_r01/metadata.json:51:        "model_source": "/Users/edr/jw_models/mlx-community/Qwen2.5-1.5B-Instruct-4bit",
tests/fixtures/d078_r01/metadata.json:55:        "weight_format": "mlx"
tests/fixtures/d078_r01/metadata.json:224:        "mlx": {
tests/fixtures/d078_r01/metadata.json:228:        "mlx-lm": {
tests/fixtures/d078_r01/metadata.json:387:      "mlx": {
tests/fixtures/d078_r01/metadata.json:391:      "mlx-lm": {
tests/fixtures/d078_r01/metadata.json:562:    "source": "/Users/edr/jw_models/mlx-community/Qwen2.5-1.5B-Instruct-4bit",
tests/fixtures/d078_r01/metadata.json:563:    "weight_format": "mlx"
tests/fixtures/d078_r01/metadata.json:719:      "name": "mlx_lm.stream_generate",
tests/fixtures/d078_r01/metadata.json:730:        "root": "/Users/edr/jw_models/mlx-community/Qwen2.5-1.5B-Instruct-4bit",
tests/fixtures/d078_r01/metadata.json:734:      "source": "/Users/edr/jw_models/mlx-community/Qwen2.5-1.5B-Instruct-4bit"
tests/fixtures/d078_r01/metadata.json:817:      "api": "mlx_lm.sample_utils.make_sampler",
tests/fixtures/d078_r01/metadata.json:824:      "backend": "mlx",
tests/fixtures/d078_r01/metadata.json:826:      "identifier": "/Users/edr/jw_models/mlx-community/Qwen2.5-1.5B-Instruct-4bit",
tests/fixtures/d078_r01/events.jsonl:3:{"timestamp_s": 1784491073.446031, "event_type": "stage_completed", "phase": "validate", "message": "stage validate completed", "metadata": {"transport": "local", "runtime": "mlx", "telemetry": "powermetrics"}}
tests/fixtures/d078_r01/events.jsonl:12:{"timestamp_s": 1784491122.808466, "event_type": "phase_start", "phase": "tokenize", "message": "mlx tokenization started", "metadata": {}}
tests/fixtures/d078_r01/events.jsonl:13:{"timestamp_s": 1784491122.8088698, "event_type": "phase_end", "phase": "tokenize", "message": "mlx tokenization completed", "metadata": {"prompt_tokens": 128}}
tests/fixtures/d078_r01/events.jsonl:14:{"timestamp_s": 1784491122.808873, "event_type": "phase_start", "phase": "generation_setup", "message": "mlx generation setup started", "metadata": {}}
tests/fixtures/d078_r01/events.jsonl:15:{"timestamp_s": 1784491122.8089159, "event_type": "phase_end", "phase": "generation_setup", "message": "mlx generation setup completed", "metadata": {"requested_output_tokens": 64, "eos_suppressed": true}}
tests/fixtures/d078_r01/events.jsonl:16:{"timestamp_s": 1784491122.8089201, "event_type": "phase_start", "phase": "prefill", "message": "mlx prefill started", "metadata": {"phase_boundary_method": "first_token", "prompt_tokens": 128, "requested_output_tokens": 64, "eos_suppressed": true}}
tests/fixtures/d078_r01/events.jsonl:17:{"timestamp_s": 1784491122.941777, "event_type": "phase_end", "phase": "prefill", "message": "mlx prefill completed", "metadata": {"phase_boundary_method": "first_token"}}
tests/fixtures/d078_r01/events.jsonl:18:{"timestamp_s": 1784491122.941782, "event_type": "phase_start", "phase": "decode", "message": "mlx decode started", "metadata": {"phase_boundary_method": "first_token", "max_tokens": 64, "eos_suppressed": true, "original_eos_token_ids": [151645]}}
tests/fixtures/d078_r01/events.jsonl:19:{"timestamp_s": 1784491122.941783, "event_type": "token", "phase": "decode", "message": "mlx token 0", "metadata": {"index": 0}}
tests/fixtures/d078_r01/events.jsonl:20:{"timestamp_s": 1784491122.945257, "event_type": "token", "phase": "decode", "message": "mlx token 1", "metadata": {"index": 1}}
tests/fixtures/d078_r01/events.jsonl:21:{"timestamp_s": 1784491122.9489322, "event_type": "token", "phase": "decode", "message": "mlx token 2", "metadata": {"index": 2}}
tests/fixtures/d078_r01/events.jsonl:22:{"timestamp_s": 1784491122.9525492, "event_type": "token", "phase": "decode", "message": "mlx token 3", "metadata": {"index": 3}}
tests/fixtures/d078_r01/events.jsonl:23:{"timestamp_s": 1784491122.9561632, "event_type": "token", "phase": "decode", "message": "mlx token 4", "metadata": {"index": 4}}
tests/fixtures/d078_r01/events.jsonl:24:{"timestamp_s": 1784491122.9598238, "event_type": "token", "phase": "decode", "message": "mlx token 5", "metadata": {"index": 5}}
tests/fixtures/d078_r01/events.jsonl:25:{"timestamp_s": 1784491122.963487, "event_type": "token", "phase": "decode", "message": "mlx token 6", "metadata": {"index": 6}}
tests/fixtures/d078_r01/events.jsonl:26:{"timestamp_s": 1784491122.967139, "event_type": "token", "phase": "decode", "message": "mlx token 7", "metadata": {"index": 7}}
tests/fixtures/d078_r01/events.jsonl:27:{"timestamp_s": 1784491122.970811, "event_type": "token", "phase": "decode", "message": "mlx token 8", "metadata": {"index": 8}}

exec
/bin/zsh -lc 'rg --files joulewise | sort' in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
exec
/bin/zsh -lc "sed -n '1,300p' docs/contracts/adapter_contracts.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
joulewise/__init__.py
joulewise/__main__.py
joulewise/adapters/__init__.py
joulewise/adapters/local_transport.py
joulewise/adapters/mlx_runtime.py
joulewise/adapters/mock_runtime.py
joulewise/adapters/mock_spec_runtime.py
joulewise/adapters/mock_telemetry.py
joulewise/adapters/node_client.py
joulewise/adapters/node_worker.py
joulewise/adapters/nvidia_smi.py
joulewise/adapters/powermetrics.py
joulewise/adapters/ssh_transport.py
joulewise/adapters/suite_control.py
joulewise/adapters/vllm_runtime.py
joulewise/aggregate.py
joulewise/analysis_engine/__init__.py
joulewise/analysis_engine/artifact.py
joulewise/analysis_engine/claims.py
joulewise/analysis_engine/distributions.py
joulewise/analysis_engine/estimators.py
joulewise/analysis_engine/inputs.py
joulewise/analysis_engine/multiplicity.py
joulewise/analysis_engine/ratio.py
joulewise/analysis_engine/registry.py
joulewise/analysis_engine/sensitivity.py
joulewise/analysis_manifest.py
joulewise/analysis_manifest_v3.py
joulewise/axi_decode_config.py
joulewise/bundle.py
joulewise/bundle_read.py
joulewise/calibration_bracketing.py
joulewise/calibration_ledger.py
joulewise/campaign_provenance.py
joulewise/cli.py
joulewise/clock.py
joulewise/controller.py
joulewise/cooldown.py
joulewise/cooldown_anchor.py
joulewise/detection_floor.py
joulewise/determinism_gate.py
joulewise/doctor.py
joulewise/envelope_gate.py
joulewise/environment.py
joulewise/environment_admission.py
joulewise/floor_extraction.py
joulewise/gensuite/__init__.py
joulewise/idle_admission.py
joulewise/idle_dependence.py
joulewise/interfaces.py
joulewise/kv_size.py
joulewise/load_transition_alignment.py
joulewise/output_identity.py
joulewise/powermetrics_fiducial.py
joulewise/provenance.py
joulewise/publication_privacy.py
joulewise/quiet_guard.py
joulewise/quiet_guard_process.py
joulewise/reduce.py
joulewise/report.py
joulewise/salvage_dangler.py
joulewise/schemas.py
joulewise/suite.py
joulewise/uncertainty_evidence.py
joulewise/validation.py
joulewise/whole_window.py
joulewise/workloads.py

 succeeded in 0ms:
# Adapter Contracts

Living cross-phase contract, drafted in Phase 1; the executable form is
`joulewise/interfaces.py`. The benchmark separates runtime work from
telemetry measurement. A target is a composition of transport, runtime
adapter, and telemetry adapter.

## Run Context (D-024, Slice 2N.1)

Every adapter lifecycle method takes a trailing optional
`context: RunContext | None = None` parameter. The `RunContext` is an
immutable dataclass the controller constructs once per run, after bundle
creation: `config`, `clock`, `run_id`, `bundle_path`, `raw_dir`,
`logs_dir`, `outputs_dir`, and optional `node_role` (None for single-node
runs; reserved for Phase 3 split orchestration).

Rules:

- Context is data, not capability: adapters receive paths and identity,
  never the bundle writer. Write-order and immutability invariants stay
  with the controller and `RunBundleWriter`.
- The controller always passes the context. Out-of-run invocations - the
  D-014 cooldown gate's `measure_idle` between repetitions, direct adapter
  tests - pass `None`; adapters must tolerate a missing context by
  producing no raw output (one lifecycle code path either way).
- Raw evidence (D-002): a telemetry adapter preserves its native sampler
  output verbatim under `context.raw_dir` (e.g. the powermetrics plist),
  via `joulewise.bundle.write_raw_artifact(context, name, data)` - the
  helper enforces the plain-file-name and no-overwrite rules without
  handing the adapter the bundle writer. Adapters must not write `raw/`
  paths directly (2026-07-06 status review P3).
- Adapters must ignore context fields they do not need.

## Measured-Window Markers (D-026, Slice 2N.2)

The controller emits `sampling_started` (stamped only after
`start_sampling` returns ok - sampling confirmed active) and
`sampling_stopped` (stamped before `stop_sampling` is invoked) events on
the `measured_run` phase. The reducer integrates energy between these
markers, so sampler spawn latency (sudo probe, process start, first
sample) and wind-down cost (process stop, output parsing) never land
inside the measured window. Telemetry adapters therefore must:

- Return from `start_sampling` only once sampling is actually running.
- Do stop-side parsing inside `stop_sampling` (after the window closes),
  not lazily during the window.

## External marked-runner (energy-layer shim) contract (C-015)

The C-015 export path is a marker-emitting shim, not a full benchmark
adapter framework. The external harness owns prompts, generation semantics,
accuracy artifacts, and metric artifacts. JouleWise owns power capture,
bundle assembly, marker validation, and energy reduction.

Contract fields:

```text
shim_schema_version
invocation:
  harness_name
  harness_version
  command_argv_sha256
  working_dir_sha256_or_null
  environment_allowlist
  benchmark_name
  benchmark_revision
  subset_id
  external_results_path
  external_results_sha256
events:
  timestamp_s
  event_type: item_start | item_end | harness_start | harness_end
  phase
  message
  metadata:
    run_id
    harness_item_id
    item_index
    benchmark_name
    subset_id
    prompt_sha256_or_null
    output_sha256_or_null
    external_metric_record_id_or_null
    status
    error_type_or_null
    token_counts_if_reported
    timestamp_source
validation:
  require_paired_item_markers
  require_monotonic_timestamps
  require_markers_inside_measured_window
  require_no_overlapping_items_unless_declared
  require_external_results_hash
```

Shim events ride the existing run-bundle event shape: the only top-level
event keys are `timestamp_s`, `event_type`, `phase`, `message`, and
`metadata`. Harness-specific data, benchmark item IDs, prompt/output hashes,
external metric IDs, status, errors, and any token counts reported by the
harness stay inside `metadata` (C-015).

Validation rules for C-015/P2-022: item markers must pair; timestamps must
be monotonic; all item markers must fall inside the measured window; item
windows must not overlap unless the shim declares an overlapping execution
mode; the external result artifact must be preserved and hashed; and strict
bundle validation plus reduction must succeed before any energy result is
claim-bearing.

Permitted claim shapes (C-015):

- "External harness X version Y reported metric artifact Z; JouleWise
  measured energy for the same marked item/subset windows."
- L1 observed energy for an external harness run under a named stack,
  measurement boundary, subset, and output policy.
- L2 energy comparisons only with strict bundles, repeated runs, same
  boundary or calibrated boundary, and AP coverage.

Forbidden claims (C-015/C-004):

- JouleWise-computed accuracy unless a future quarantined scorer explicitly
  exists.
- Intelligence per joule, pass@k per joule, or "more capable per watt."
- Leaderboard standing from joined accuracy(theirs)+energy(ours).
- Item-window statistical independence.
- Any pass@k, retry, judge, or benchmark-score normalization claim from the
  shim layer.

The P2-022 feasibility spike launches the external runner as a subprocess
and inherits D-035 fresh-process isolation. Its verdict is computed, not
hand-labeled, per D-036, from marker pairing, timestamp placement,
subprocess exit status, external result hash presence, strict bundle
validity, and reduction success. Verdict codes are
`external_markers_supported`, `partial(<limitation>)`, and
`external_markers_unsupported`.

## Transport Adapter

Transport answers where commands execute.

Required behavior:

- Run a command locally or over SSH.
- Copy artifacts into the controller's run bundle.
- Report connection metadata.
- Return structured failure on unreachable hosts.

Initial transports:

- `local`
- `ssh`

## Runtime Adapter

Runtime answers how a model workload is executed.

Required behavior:

- Prepare runtime environment.
- Load or initialize model.
- Warm up workload.
- Run full request.
- Run prefill-only workload when supported (Phase-3-future: no shipped RuntimeAdapter implements or is required to implement this yet; binding form lands with Phase 3 Stage 3.1/3.2 schema v0.2).
- Run decode-only or replay workload when supported (Phase-3-future: same gating as prefill-only; the contract does not promise split modes the current adapters cannot express).
- Emit phase events.
- Emit output artifacts.
- Cleanup.

Initial runtimes:

- `mock`
- `mlx`
- `vllm`

Candidate runtimes:

- `llama_cpp`
- `hailo`

## Suite Runtime Adapter (D-045/D-046/D-047.5)

A runtime that can execute a materialized suite manifest implements
`SuiteRuntimeAdapter.run_suite(config, manifest, context, *, order_seed,
order_row=None)`. The controller dispatches to this method only when
`workload_profile.suite_manifest_ref` is set and validation has loaded the
manifest. `run_workload` remains the single-prompt contract. `order_seed` is
controller-derived (D-045.6), never runtime-chosen; adapters must use the
supplied value in suite markers and workload provenance rather than deriving a
seed from `run_id`.

2026-07-09 (P2-030): `order_row` is the controller-derived companion to
`order_seed` for operational suite order policies. It is `0` for single runs
and the one-based `__rN` repetition index for experiment members. Runtimes
execute the pure realized order defined by `joulewise.suite.realized_order`
from the manifest policy and `order_row`; they do not choose or randomize the
row.

`run_suite` obligations:

- Iterate the realized suite order and emit suite, block, level, and item
  markers with the vocabulary and required metadata keys pinned in
  `joulewise/suite.py`. For `manifest_order` the realized order is manifest
  order. For rotated policies, `item_index` remains the manifest index,
  `position` is the realized execution ordinal, and `prev_item` is execution
  honest.
- Contain per-item generation exceptions: the item receives `item_end` with
  `status: "runtime_failed"` and a diagnostic `status_reason`, then the loop
  continues. Suite-level machinery failures may still raise out of
  `run_suite`.
- Write exactly one per-item output artifact, `outputs/suite_items.jsonl`.
  Each line carries the item id/index, status and optional status reason,
  `prompt_source`, `bos_present`, prompt token-ID hash block, response
  text/hash, stop reason, prompt/output token counts, and token timestamps
  (D-045.8/AP-6). Suites do not emit `response.txt`.
- Preserve workload provenance for suite identity, generator, tokenizer,
  model, and sampler. MLX adapters must pin greedy/temp-0 by constructing the
  installed `mlx_lm` sampler and passing it to `stream_generate`; if the
  sampler cannot be constructed or verified, measured single-prompt and suite
  generation fail closed with the named adapter error
  `sampler_pin_unverified`.

Runtime status assignment:

```text
condition                                           item_end.status
generation completed fixed_budget_exact and emitted == planned_output_tokens
                                                    succeeded
generation completed fixed_budget_exact and emitted < planned_output_tokens
                                                    malformed
                                                    status_reason=fixed_budget_underrun
generation completed natural_eos and emitted == planned_output_tokens
                                                    capped
generation completed natural_eos and emitted < planned_output_tokens
                                                    succeeded
per-item generation exception                       runtime_failed
```

Only the reducer may assign `below_floor`; `excluded_from_claim` is
analysis-only and invalid in runtime events or summaries (D-045.4).

Prompt-source handling is per item and mutually exclusive. `prompt_text` is
encoded at generation time with adapter-normal special-token behavior
(MLX uses `add_special_tokens=True`, so BOS is inside the planned prompt
budget). `prompt_token_ids` is ids-native and delivered exactly as listed,
with no BOS added; this is required for D-046 sentinel conditions.
Absent text and ids use a synthetic prompt with
`shape.planned_prompt_tokens`. Any field named `prompt_sha256` means the
domain-separated token-ID hash, not a text hash.

For prompt-text items with a SHA-256-shaped `source.source_sha256`, runtimes
compare the realized prompt token-ID hash against `source_sha256`; if it does
not match, they may accept `sha256(prompt_text)` as a text-domain manifest.
Any other value fails the item closed as `malformed` with
`status_reason: "prompt_ids_mismatch"`. For planned prompt token counts,
`jw_mixed_v1` prompt-text items are budgeted and a realized/planned mismatch
is fatal; affine ladder prompt-text items are nominal and receive an advisory
annotation instead.

`suite_items.jsonl.prompt_source` is one of `prompt_text`, `token_ids`, or
`synthetic`. `bos_present` records whether BOS is present in the realized
prompt. For text-path adapters, when the tokenizer exposes a BOS id this is
`add_special_tokens=True` and first realized id equals the tokenizer BOS id;
when the tokenizer does not expose BOS identity, `bos_present` records the
honest encode-mode proxy (`add_special_tokens=True`). Ids-native and
synthetic suite prompts record `false` unless a future adapter explicitly
materializes BOS as part of those sources.

## Telemetry Adapter

Telemetry answers how power and thermal state are measured.

Required behavior:

- Report device metadata, including the rail manifest: the exact rail
  names whose per-timestamp sum defines the backend's canonical
  `power_w` (D-018). Rail manifest entries are strings; non-string entries
  are rejected by the bundle reader rather than coerced.
- Measure idle baseline.
- Start power sampling.
- Stop power sampling.
- Emit raw power samples.
- Report thermal state when available.
- Return structured failure if telemetry permission is missing.

Rail-row timestamp contract (D-027, Slice 2N.4): one sample instant is
one clock read, fanned out to one row per manifest rail, all carrying
that instant's single `timestamp_s`. A manifest rail may appear at most
once for a given timestamp; duplicate `(timestamp_s, rail)` rows are
invalid, including single-rail manifests. With a multi-rail manifest, a
timestamp carrying only a subset of the manifest rails is a
misalignment: the shared bundle reader raises a structured failure (the
reducer reports FAILED; the report omits the chart) and default bundle
validation reports the same trace-policy problem rather than silently
producing an interleaved, undersummed, or double-counted curve. An
adapter whose hardware samples rails at genuinely different instants
must resample/align to shared timestamps before emitting rows -
alignment policy belongs to the adapter that knows its hardware.

Powermetrics NUL-framed plist parsing is lenient only for the final
unparseable frame, and only after at least one complete frame parsed
successfully. The adapter preserves the raw plist verbatim, drops that final

exec
/bin/zsh -lc "sed -n '1,120p' configs/examples/mac_mlx_local.json && sed -n '1,220p' joulewise/adapters/registry.py" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
exec
/bin/zsh -lc "sed -n '180,260p' joulewise/schemas.py" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 exited 1 in 0ms:
{
  "schema_version": "0.1",
  "run_id": "example-mac-mlx-local-512t",
  "model": {
    "name": "Qwen2.5-1.5B-Instruct-4bit",
    "family": "qwen2.5",
    "source": "/Users/edr/jw_models/mlx-community/Qwen2.5-1.5B-Instruct-4bit",
    "revision": "8b403126fc14f14cfc99bb4cfa72ecbc129ea677",
    "weight_format": "mlx",
    "context_window": 32768
  },
  "quantization": {
    "name": "int4",
    "bits": 4
  },
  "hardware_target": {
    "id": "macbook_m3_max",
    "transport": "local",
    "runtime_backend": "mlx",
    "telemetry_backend": "powermetrics",
    "device_kind": "apple_silicon_unified_memory",
    "notes": "Phase 2 first real vertical slice. Decode is sized to ~2 s so the measured window spans many real 10 Hz powermetrics intervals (a 64-token/0.3 s window is unmeasurable: sampler startup exceeds it; 2I bring-up finding 2026-07-06)."
  },
  "workload_profile": {
    "name": "smoke_short_prompt_medium_decode",
    "prompt_text": "Summarize why idle-subtracted energy matters for LLM inference benchmarking.",
    "output_tokens": 512,
    "repetitions": 3,
    "warmup_runs": 1
  },
  "interconnect": {
    "name": "local"
  },
  "sampling": {
    "power_hz": 10.0,
    "idle_seconds": 30.0,
    "warmup_seconds": 5.0
  },
  "run_metadata": {
    "project": "capstone-joulewise",
    "operator": "jon",
    "tags": ["phase1", "mac", "smoke"]
  }
}
sed: joulewise/adapters/registry.py: No such file or directory

 succeeded in 0ms:
    "interconnect": frozenset({"name", "link_speed_mbps", "notes"}),
    "sampling": frozenset({"power_hz", "idle_seconds", "warmup_seconds"}),
    "run_metadata": frozenset(
        {"project", "operator", "ambient_temp_c", "notes", "tags"}
    ),
}


def _unknown_config_key_warnings(data: dict[str, Any]) -> tuple[ConfigKeyWarning, ...]:
    paths = [str(key) for key in data if key not in _CONFIG_KEYS_BY_PATH[""]]
    for section, allowed in _CONFIG_KEYS_BY_PATH.items():
        if not section:
            continue
        value = data.get(section)
        if not isinstance(value, dict):
            # The owning from_mapping method raises SchemaError; do not inspect
            # child keys of a value that is not a typed object.
            continue
        paths.extend(f"{section}.{key}" for key in value if key not in allowed)
    return tuple(ConfigKeyWarning(path) for path in sorted(paths))


class TransportKind(str, Enum):
    LOCAL = "local"
    SSH = "ssh"


class RuntimeBackend(str, Enum):
    MOCK = "mock"
    MLX = "mlx"
    VLLM = "vllm"
    LLAMA_CPP = "llama_cpp"
    HAILO = "hailo"


class TelemetryBackend(str, Enum):
    MOCK = "mock"
    POWERMETRICS = "powermetrics"
    NVIDIA_SMI = "nvidia_smi"
    JETSON_RAILS = "jetson_rails"
    WALL_METER = "wall_meter"


class RunStatus(str, Enum):
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    UNSUPPORTED = "unsupported"


class PromptTokenEvidencePolicy(str, Enum):
    """Validated policy for text-suite prompt-token integrity evidence."""

    REQUIRED = "required"
    EXEMPT_AFFINE_GENERATED_TEXT = "exempt_affine_generated_text"


class CampaignPolicyProfile(str, Enum):
    """Claim posture selected by a hash-bound campaign policy sidecar."""

    PRODUCTION = "production"
    EXPLORATORY = "exploratory"


class AdmissionFailureAction(str, Enum):
    """Controller action after the bounded idle-admission retry is exhausted."""

    ABORT = "abort"
    FLAG = "flag"


class EnergyEvidence(str, Enum):
    """Admission state for request-energy evidence in a succeeded summary."""

    AVAILABLE = "available"
    ABSENT = "absent"


class FailureReason(str, Enum):
    DID_NOT_FIT = "did_not_fit"
    RUNTIME_UNAVAILABLE = "runtime_unavailable"
    TELEMETRY_UNAVAILABLE = "telemetry_unavailable"

exec
/bin/zsh -lc "rg -n 'phase_start|phase_end|prefill|decode|tokenize|def _generate' joulewise/adapters/mlx_runtime.py" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
80:        self._tokenizer: Any | None = None
143:        self._model, self._tokenizer, self._model_config = loaded
168:        if self._mlx_lm is None or self._model is None or self._tokenizer is None:
178:                self._tokenizer,
194:        if self._mlx_lm is None or self._model is None or self._tokenizer is None:
198:        # The encode runs INSIDE the tokenize phase window (prepare_prompt is
199:        # called between the tokenize markers) so per-phase attribution covers
230:                "tokenizer": _tokenizer_identity(self._tokenizer, config),
261:        if self._mlx_lm is None or self._model is None or self._tokenizer is None:
307:                "tokenizer": _tokenizer_identity(self._tokenizer, config),
503:    def _generate(
518:            self._event("phase_start", "tokenize", "mlx tokenization started")
521:            # Single-prompt path: the encode happens here, inside the tokenize
523:            # carries the prompt hash), so their tokenize window is residual.
528:                "phase_end",
529:                "tokenize",
536:                "phase_start",
545:                "phase_end",
554:        prefill_metadata: dict[str, Any] = {
561:            prefill_metadata.update(
566:                "phase_start",
567:                "prefill",
568:                "mlx prefill started",
569:                prefill_metadata,
584:                self._tokenizer,
590:                    prefill_end_metadata: dict[str, Any] = {
593:                    decode_start_metadata: dict[str, Any] = {
604:                        prefill_end_metadata.update(
611:                        decode_start_metadata.update(
620:                            "phase_end",
621:                            "prefill",
622:                            "mlx prefill completed",
623:                            prefill_end_metadata,
628:                            "phase_start",
629:                            "decode",
630:                            "mlx decode started",
631:                            decode_start_metadata,
650:                        phase="decode",
667:            decode_metadata: dict[str, Any] = {
674:                decode_metadata.update({"item_id": item_id, "item_index": item_index})
676:                "phase_end",
677:                "prefill",
678:                "mlx prefill completed without emitted tokens",
685:                    event_type="phase_start",
686:                    phase="decode",
687:                    message="mlx decode started without emitted tokens",
688:                    metadata=decode_metadata,
692:        decode_end_metadata: dict[str, Any] = {
698:            decode_end_metadata.update({"item_id": item_id, "item_index": item_index})
701:                "phase_end",
702:                "decode",
703:                "mlx decode completed",
704:                decode_end_metadata,
733:        self._tokenizer = None
759:            token_ids = _encode(self._tokenizer, profile.prompt_text, add_special_tokens=True)
762:            prompt_tokens = _synthetic_prompt_tokens(self._tokenizer, profile.prompt_tokens)
766:            token_ids = _encode(self._tokenizer, prompt, add_special_tokens=True)
770:                self._tokenizer,
781:            token_ids = _encode(self._tokenizer, item.source.prompt_text, add_special_tokens=True)
787:                _bos_present(self._tokenizer, token_ids, add_special_tokens=True),
793:            self._tokenizer,
890:        original = _tokenizer_eos_ids(self._tokenizer)
894:            setattr(self._tokenizer, "eos_token_ids", set())
895:        except Exception:  # noqa: BLE001 - some tokenizer wrappers may not expose this
903:            setattr(self._tokenizer, "eos_token_ids", eos_ids)
923:def _encode(tokenizer: Any, text: str, *, add_special_tokens: bool) -> list[int]:
925:        encoded = tokenizer.encode(text, add_special_tokens=add_special_tokens)
927:        encoded = tokenizer.encode(text)
996:def _bos_present(tokenizer: Any, token_ids: list[int], *, add_special_tokens: bool) -> bool:
1000:        bos_token_id = getattr(tokenizer, "bos_token_id")
1005:    # Honest proxy when the tokenizer does not expose BOS identity: record the
1006:    # encode mode that asked the tokenizer to prepend adapter-normal specials.
1010:def _synthetic_prompt_tokens(tokenizer: Any, target_tokens: int) -> list[int]:
1011:    seed = _encode(tokenizer, SYNTHETIC_PROMPT_SEED, add_special_tokens=False)
1013:        seed = _encode(tokenizer, "JouleWise", add_special_tokens=False)
1098:def _tokenizer_eos_ids(tokenizer: Any) -> set[int] | None:
1099:    if tokenizer is None:
1102:        value = getattr(tokenizer, "eos_token_ids")
1118:def _tokenizer_identity(tokenizer: Any, config: BenchmarkConfig) -> dict[str, Any]:
1121:        "identifier": _tokenizer_identifier(tokenizer, config),
1123:        "class": type(tokenizer).__name__,
1124:        "vocab_size": _tokenizer_vocab_size(tokenizer),
1128:def _tokenizer_identifier(tokenizer: Any, config: BenchmarkConfig) -> str | None:
1130:        value = getattr(tokenizer, attr, None)
1136:def _tokenizer_vocab_size(tokenizer: Any) -> int | None:
1137:    value = getattr(tokenizer, "vocab_size", None)
1140:    get_vocab = getattr(tokenizer, "get_vocab", None)
1144:        except Exception:  # noqa: BLE001 - tokenizer wrappers vary
1149:        size = len(tokenizer)
1150:    except Exception:  # noqa: BLE001 - tokenizer wrappers vary

exec
/bin/zsh -lc "sed -n '1,260p' joulewise/adapters/__init__.py" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
"""Adapter registry: backend enum -> adapter factory (decisions D-009, D-019).

The controller resolves adapters exclusively through this registry. Each
resolver returns a ``(adapter, failure)`` pair in which exactly one element
is non-None: a backend with a registered implementation yields the adapter;
any other backend yields a structured ``AdapterResult`` failure naming the
backend - the registry never raises. Unavailable backends map to
``runtime_unavailable`` / ``telemetry_unavailable`` / ``transport_unavailable``
so the controller's status mapping (D-012) applies uniformly. Real backends
land here in later slices (2G, 2H, 2K, 2L) behind lazy imports per the
stdlib-core/extras policy (D-009).

Implemented backends in this slice: runtime ``mock``, ``mlx``, and remote
``vllm``; telemetry ``mock``, ``powermetrics``, and remote ``nvidia_smi``;
transport ``local`` and ``ssh``. Clock-driven adapters receive the injected
:class:`joulewise.clock.Clock` (D-019).
"""

from __future__ import annotations

import importlib

from joulewise.adapters.local_transport import LocalTransport
from joulewise.adapters.mock_runtime import MockRuntimeAdapter
from joulewise.adapters.mock_telemetry import MockTelemetryAdapter
from joulewise.clock import Clock, SystemClock
from joulewise.interfaces import (
    AdapterResult,
    RuntimeAdapter,
    TelemetryAdapter,
    TransportAdapter,
)
from joulewise.schemas import (
    BenchmarkConfig,
    FailureReason,
    RuntimeBackend,
    TelemetryBackend,
    TransportKind,
)

__all__ = [
    "LocalTransport",
    "MlxRuntimeAdapter",
    "MockRuntimeAdapter",
    "MockTelemetryAdapter",
    "NvidiaSmiTelemetryAdapter",
    "PowermetricsTelemetryAdapter",
    "SshTransport",
    "VllmRuntimeAdapter",
    "resolve_runtime",
    "resolve_telemetry",
    "resolve_transport",
]


def __getattr__(name: str) -> object:
    if name == "MlxRuntimeAdapter":
        module = importlib.import_module("joulewise.adapters.mlx_runtime")
        return module.MlxRuntimeAdapter
    if name == "PowermetricsTelemetryAdapter":
        module = importlib.import_module("joulewise.adapters.powermetrics")
        return module.PowermetricsTelemetryAdapter
    if name == "SshTransport":
        module = importlib.import_module("joulewise.adapters.ssh_transport")
        return module.SshTransport
    if name == "VllmRuntimeAdapter":
        module = importlib.import_module("joulewise.adapters.vllm_runtime")
        return module.VllmRuntimeAdapter
    if name == "NvidiaSmiTelemetryAdapter":
        module = importlib.import_module("joulewise.adapters.nvidia_smi")
        return module.NvidiaSmiTelemetryAdapter
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def _backend_name(backend: object) -> str:
    return str(getattr(backend, "value", backend))


def _failure(reason: FailureReason, message: str) -> tuple[None, AdapterResult]:
    return None, AdapterResult(ok=False, failure_reason=reason, message=message)


def _remote_node_client(config: BenchmarkConfig, clock: Clock):
    target = config.hardware_target
    if target.transport != TransportKind.SSH:
        return _failure(
            FailureReason.TRANSPORT_UNAVAILABLE,
            "remote node adapters require transport 'ssh'",
        )
    if not target.host:
        return _failure(
            FailureReason.TRANSPORT_UNAVAILABLE,
            "remote node adapters require hardware_target.host for ssh transport",
        )
    try:
        transport_module = importlib.import_module("joulewise.adapters.ssh_transport")
        client_module = importlib.import_module("joulewise.adapters.node_client")
    except ImportError as exc:
        return _failure(
            FailureReason.TRANSPORT_UNAVAILABLE,
            f"remote node transport/client could not import: {exc}",
        )
    try:
        transport = transport_module.SshTransport(clock, target.host)
        client = client_module.NodeWorkerClient(
            transport,
            clock,
        )
    except Exception as exc:  # noqa: BLE001 - registry resolution stays structured
        return _failure(
            FailureReason.TRANSPORT_UNAVAILABLE,
            f"remote node client could not be constructed: {exc}",
        )
    return client, None


def resolve_runtime(
    config: BenchmarkConfig, clock: Clock
) -> tuple[RuntimeAdapter | None, AdapterResult | None]:
    """Resolve the configured runtime backend to an adapter or a failure."""
    backend = config.hardware_target.runtime_backend
    if backend == RuntimeBackend.MOCK:
        return MockRuntimeAdapter(clock), None
    if backend == RuntimeBackend.MLX:
        try:
            module = importlib.import_module("joulewise.adapters.mlx_runtime")
        except ImportError as exc:
            return _failure(
                FailureReason.RUNTIME_UNAVAILABLE,
                "runtime backend 'mlx' could not import its adapter; the MLX "
                "runtime requires the [mac] extra "
                f"(pip install 'joulewise[mac]'; D-009): {exc}",
            )
        return module.MlxRuntimeAdapter(clock), None
    if backend == RuntimeBackend.VLLM:
        client, failure = _remote_node_client(config, clock)
        if client is None:
            return None, failure
        try:
            module = importlib.import_module("joulewise.adapters.vllm_runtime")
        except ImportError as exc:
            return _failure(
                FailureReason.RUNTIME_UNAVAILABLE,
                f"runtime backend 'vllm' could not import its adapter: {exc}",
            )
        return module.VllmRuntimeAdapter(clock, client), None
    return _failure(
        FailureReason.RUNTIME_UNAVAILABLE,
        f"runtime backend '{_backend_name(backend)}' has no registered adapter",
    )


def resolve_telemetry(
    config: BenchmarkConfig, clock: Clock
) -> tuple[TelemetryAdapter | None, AdapterResult | None]:
    """Resolve the configured telemetry backend to an adapter or a failure."""
    backend = config.hardware_target.telemetry_backend
    if backend == TelemetryBackend.MOCK:
        return MockTelemetryAdapter(clock), None
    if backend == TelemetryBackend.POWERMETRICS:
        try:
            module = importlib.import_module("joulewise.adapters.powermetrics")
        except ImportError as exc:
            return _failure(
                FailureReason.TELEMETRY_UNAVAILABLE,
                "telemetry backend 'powermetrics' could not import its adapter: "
                f"{exc}",
            )
        return module.PowermetricsTelemetryAdapter(clock), None
    if backend == TelemetryBackend.NVIDIA_SMI:
        client, failure = _remote_node_client(config, clock)
        if client is None:
            return None, failure
        try:
            module = importlib.import_module("joulewise.adapters.nvidia_smi")
        except ImportError as exc:
            return _failure(
                FailureReason.TELEMETRY_UNAVAILABLE,
                f"telemetry backend 'nvidia_smi' could not import its adapter: {exc}",
            )
        return module.NvidiaSmiTelemetryAdapter(clock, client), None
    return _failure(
        FailureReason.TELEMETRY_UNAVAILABLE,
        f"telemetry backend '{_backend_name(backend)}' has no registered adapter",
    )


def resolve_transport(
    config: BenchmarkConfig,
) -> tuple[TransportAdapter | None, AdapterResult | None]:
    """Resolve the configured transport kind to an adapter or a failure."""
    transport = config.hardware_target.transport
    if transport == TransportKind.LOCAL:
        return LocalTransport(), None
    if transport == TransportKind.SSH:
        if not config.hardware_target.host:
            return _failure(
                FailureReason.TRANSPORT_UNAVAILABLE,
                "transport 'ssh' requires hardware_target.host",
            )
        try:
            module = importlib.import_module("joulewise.adapters.ssh_transport")
            return module.SshTransport(SystemClock(), config.hardware_target.host), None
        except ImportError as exc:
            return _failure(
                FailureReason.TRANSPORT_UNAVAILABLE,
                f"transport 'ssh' could not import its adapter: {exc}",
            )
        except Exception as exc:  # noqa: BLE001 - registry resolution stays structured
            return _failure(
                FailureReason.TRANSPORT_UNAVAILABLE,
                f"transport 'ssh' could not be constructed: {exc}",
            )
    return _failure(
        FailureReason.TRANSPORT_UNAVAILABLE,
        f"transport '{_backend_name(transport)}' has no registered adapter",
    )

web search: 
web search: site:github.com/ggml-org/llama.cpp Qwen2.5 support Metal prompt eval timing llama_decode ...
web search: 
web search: 
exec
/bin/zsh -lc "sed -n '170,230p' docs/paper/draft-v1.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
### LLM inference energy measurement

TokenPowerBench provides one of the closest reporting structures: it separates prompt-processing and token-generation energy, uses phase-appropriate token denominators, and groups results by context length [TokenPowerBench]. Its disclosed method, however, does not specify the boundary events, alignment rule, repetition and variance protocol, idle baseline, or external validation, and continuous batching makes an “active phase” label difficult to interpret when requests overlap. JouleWise adopts phase-specific reporting but restricts its primary scope to one sequential request, where runtime-emitted phase boundaries are well posed and can be calibrated.

The Illusion of Power Capping in LLM Decode samples graphics-processor power, integrates those samples, repeats configurations, and cross-checks sufficiently long operations against a separate hardware energy counter [IllusionPowerCapping]. This is a stronger measurement template than an unqualified software reading. Its counter agreement, run-to-run variation, snapshot fallback, and timing alignment nevertheless remain separate diagnostics rather than one bound on the reported effect, and its long sweeps do not use a drift-control ordering. JouleWise composes those classes of uncertainty into a decision rule for each contrast.

Apple-focused system comparisons reinforce the need for boundary labels. Silicon Showdown compares a graphics-board boundary on one platform with a whole-system-on-chip `powermetrics` boundary on Apple hardware, while runtimes and precision stacks also differ [SiliconShowdown]. Intelligence-per-Watt and ML.ENERGY similarly emphasize breadth across deployed inference configurations [IntelligencePerWatt; MLENERGY]. Such studies answer valuable systems questions, but unlike boundaries and software stacks cannot by themselves support a hardware-class causal ranking. JouleWise therefore makes the named stack and measurement boundary part of every result and prioritizes within-boundary effects.

### Software power counters and measurement standards

RAPL in Action established a validation agenda for commodity software counters: align lag before comparing streams, model wall power rather than assuming identity, account for temporal correlation, warm the system, measure sampler overhead, and inspect update granularity, overflow, jitter, and timestamp behavior [RAPLInAction]. Jay and Ostapenco likewise regress software readings against wall power and show that disagreement varies with load; they avoid claims about subtotals that the reference meter cannot observe [JayOstapenco]. JouleWise follows this epistemic boundary. A future external meter could test total gain and load dependence, but it would not validate how a total is divided between prefill and decode. The in-window pulse train addresses that distinct question.

MLPerf Power and SPEC require load-specific analyzer uncertainty, fixed ranges, clock synchronization, minimum intervals, invalid-sample accounting, and controlled battery behavior [MLPerfPower]. JouleWise translates their per-run reject-on-missing-evidence principle to a consumer software counter. The difference is that its principal uncertainty is not only an analyzer specification; it includes whether samples at a software-defined phase edge belong inside or outside the integral.

### Metrology and experimental discipline

Prospective paired minimum-detectable-effect methods estimate the smallest effect a planned paired study has adequate statistical power to find. They size the study from the variance of paired differences and can impose a one-way prior ratchet: observed variability may raise the planned threshold but may not lower it after outcomes are seen [PairedMDE]. JouleWise uses that logic for prospective workload sizing, but it does not treat the worst-case attribution term as independent random noise. Root-sum-square composition would be anti-conservative for a systematic edge-placement bound. Instead, the analysis maximizes over calibrated edge positions, measures drift with bracketed references, and publishes the resulting floor with the effect.

This emphasis changes the role of failed runs. A rejected admission, stale calibration, contaminated member, or below-floor contrast is evidence about the instrument's operating domain. Hash-bound raw traces, runtime events, configurations, supersessions, verdicts, and pre-registration records make that evidence re-reducible. The refusal is retained rather than disappearing behind a final average.

### Split and disaggregated inference

Split, or disaggregated, inference places prompt processing and token generation on different devices and transfers intermediate state between them. Revisiting Disaggregation Energy reports that the energy outcome depends on load, baseline, and transfer conditions on its evaluated two-graphics-processor node [RevisitingDisaggregationEnergy]. DualScale studies phase placement and per-phase power control on homogeneous server hardware [DualScale]. Prima.cpp includes whole-run energy and communication accounting but not a per-stage energy split [PrimaCPP], while SplitZip characterizes lossless transfer compression without making an energy claim [SplitZip].

JouleWise does not claim a new split scheduler in this paper. Split inference is instead a demanding future demonstration of the instrument because it introduces two physical boundaries, a transfer interval, and clock alignment across devices. A valid comparison would have to measure both ends, name each boundary, and clear a pre-registered floor or calibrated bridge. Whether splitting saves energy remains an empirical outcome; the reusable contribution is a method that can issue, qualify, or refuse the result.

codex
# Same Silicon, Different Stack: Floor-Gated MLX–llama.cpp Inference Energy on an M3 Max

**Thesis:** On one fixed M3 Max and `powermetrics` boundary, MLX and llama.cpp can be compared honestly as complete runtime–artifact stacks only when each stack has its own calibrated floor and the paired contrast separately clears both the floor and directional-interval gates.

## Project brief and steps

JouleWise already has the scientific core of this paper: an in-window pulse-train calibration for phase-boundary attribution; the finding that roughly 30 ms of edge uncertainty across roughly 33 W makes the instrument attribution-limited at about 1 J per phase member; separately enforced floor-clearance and interval-supported-direction gates, producing an effective phase-contrast sizing bar near 5 J; and a fail-closed protocol built around pre-registration, admission checks, ABBA ordering, live brackets, immutable custody, and publishable refusals. The [MVP draft](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/paper/draft-v1.md>) supplies essentially all method, metrology, related-work, and limitations prose. First execute D-117 unchanged: the approximately 3.14 h 1.5B MLX floor window, 3.24 h 7B MLX floor window, and 2.80 h MLX model-size contrast window, with prefill floors riding the first two. Mint those four phase-floor cells and populate the MVP. Then perform a read-only/daytime feasibility stage for llama.cpp: pin one llama.cpp commit and Metal build; derive a GGUF 4-bit artifact and the MLX 4-bit artifact from the same Qwen2.5-7B-Instruct source revision; implement and validate real prefill/decode markers; and run explicitly non-claim pilot comparisons. If the desk gate passes, collect one approximately 3.3 h llama.cpp 7B floor window and one approximately 3.0–3.5 h MLX-versus-llama.cpp ABBA contrast window. Thus the proposal costs **five quiet nights from today—three already required by D-117 plus two new nights**—and perhaps 2–4 weeks of desk engineering. It does not displace or weaken the MVP: if the extension dies, the original paper remains intact.

## Contributions

1. **A calibrated cross-runtime result:** determine whether the 7B llama.cpp-minus-MLX decode-energy contrast at 128 prompt/512 output tokens clears the applicable armwise floor and retains one direction over its complete interval.

2. **A falsifiable artifact-parity protocol:** both arms must share the upstream checkpoint revision, tokenizer and chat-template hashes, realized prompt token IDs, output cap, greedy policy, batch size one, and warm-cache policy. Any mismatch refuses the contrast.

3. **Runtime-specific floor transport:** demonstrate that the D-117 MLX floor can be reused only for its exact registered MLX cell, while llama.cpp receives an independently minted decode and prefill floor. The contrast uses the maximum of the two decode floors, never their sum.

4. **An honest stack-attribution result:** quantify output-token divergence and conversion differences so that the conclusion remains “MLX-stack versus llama.cpp-stack,” not the stronger and unsupported claim that energy causally “belongs to the runtime.”

## Experiment plan

The primary model is Qwen2.5-7B-Instruct, nominal 4-bit, because the historical diagnostic 7B decode-cell mean is about **192.39 J** for 512 output tokens. Therefore 3%, 5%, and 10% stack differences correspond to approximately **5.77, 9.62, and 19.24 J**. These are planning calculations, not predictions. The comparison becomes difficult only when the stacks are within roughly **2.6%**. Public project documentation establishes that llama.cpp supports Metal on Apple silicon and several 4-bit formats, while MLX-LM supports Apple-silicon inference and its own model conversion/quantization path; it does **not** provide a trustworthy paired energy estimate for this exact machine and workload. [llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/README.md), [llama.cpp quantization](https://github.com/ggml-org/llama.cpp/blob/master/tools/quantize/README.md), [MLX-LM](https://github.com/ml-explore/mlx-lm).

| New window | Registered cells | Design | Estimated time |
|---|---|---:|---:|
| llama.cpp floor | 7B decode plus free prefill rider | 10 absolute members + ten 4-member null ABBA blocks, brackets and references | ~3.3 h, uncertain |
| Runtime contrast | MLX versus llama.cpp, 7B | ten 4-member ABBA blocks; B−A; decode primary, prefill secondary | ~3.0–3.5 h, uncertain |

The 128-token prefill contrast is likely below 5 J and is deliberately a refusal-prone secondary result; no directional prefill claim is expected. If decode also fails, the result is “no stack difference resolvable for this workload,” never equality. A 1024-token fallback would approximately double decode energy while leaving edge error roughly duration-independent, but it changes the floor family and therefore requires **three new windows**—new MLX floor, llama.cpp floor, and contrast. That escalation needs a fresh funding decision.

New harness work is substantial but bounded: a persistent, pinned llama.cpp C-API runner; Metal/build provenance; runtime-native monotonic phase events; token and output traces; adapter cleanup/failure handling; model-conversion manifests; and multi-runtime floor/contrast consumers. It preserves the frozen boundary: warm model, batch one, concurrency one, one sequential request. A queued `llama-server` experiment would introduce scheduler and IPC confounds and is out of scope.

## Hardware and instrument needs

Owned M3 Max, approved charger, existing `powermetrics` calibration system, and additional local storage for the source checkpoint plus MLX and GGUF derivatives are sufficient. The RTX 3080 Ti and Jetsons are irrelevant. The Yokogawa wall meter is **not a dependency**: it could later validate whole-machine totals, but it cannot validate prefill/decode allocation.

## Venue fit and relationship to the MVP

This is a strong capstone paper and credible EuroMLSys/energy-systems workshop submission. It improves the ICPE story by showing that the instrument can referee a practical runtime choice, but one model, one unit, and two non-identical quantized formats are probably insufficient for an ICPE full-paper centerpiece without replication or wall validation. Sections 1–6 and most of Section 8 of the MVP are reused; the new material is artifact matching, the llama.cpp adapter validation, runtime-specific floors, and the cross-stack result.

## Risks and kill criteria

Kill the extension before any quiet night if:

- llama.cpp cannot emit authenticated, clock-compatible prefill/decode boundaries;
- prompt token IDs or chat-template semantics differ;
- Metal offload, fixed-budget output, or warm-cache state cannot be pinned;
- phase sums do not reconcile with the request boundary;
- the daytime pilot’s conservative lower effect estimate is below **7.5 J**—an intentionally uncertain margin above the approximately 5 J bar;
- paired variance implies ten ABBA blocks are underpowered;
- D-117’s MLX floor cannot legally transport to the exact contrast cell.

## Relation to Ed’s original goals

This directly serves the original **runtime-efficiency/energy-as-a-third-axis** goal and exercises the intended swappable-runtime harness. It does not yet address speculative decoding, MTP, MoE routing, KV mechanisms, or split inference; instead, it establishes the disciplined cross-runtime comparison substrate those later mechanisms require.
tokens used
142,773
# Same Silicon, Different Stack: Floor-Gated MLX–llama.cpp Inference Energy on an M3 Max

**Thesis:** On one fixed M3 Max and `powermetrics` boundary, MLX and llama.cpp can be compared honestly as complete runtime–artifact stacks only when each stack has its own calibrated floor and the paired contrast separately clears both the floor and directional-interval gates.

## Project brief and steps

JouleWise already has the scientific core of this paper: an in-window pulse-train calibration for phase-boundary attribution; the finding that roughly 30 ms of edge uncertainty across roughly 33 W makes the instrument attribution-limited at about 1 J per phase member; separately enforced floor-clearance and interval-supported-direction gates, producing an effective phase-contrast sizing bar near 5 J; and a fail-closed protocol built around pre-registration, admission checks, ABBA ordering, live brackets, immutable custody, and publishable refusals. The [MVP draft](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/paper/draft-v1.md>) supplies essentially all method, metrology, related-work, and limitations prose. First execute D-117 unchanged: the approximately 3.14 h 1.5B MLX floor window, 3.24 h 7B MLX floor window, and 2.80 h MLX model-size contrast window, with prefill floors riding the first two. Mint those four phase-floor cells and populate the MVP. Then perform a read-only/daytime feasibility stage for llama.cpp: pin one llama.cpp commit and Metal build; derive a GGUF 4-bit artifact and the MLX 4-bit artifact from the same Qwen2.5-7B-Instruct source revision; implement and validate real prefill/decode markers; and run explicitly non-claim pilot comparisons. If the desk gate passes, collect one approximately 3.3 h llama.cpp 7B floor window and one approximately 3.0–3.5 h MLX-versus-llama.cpp ABBA contrast window. Thus the proposal costs **five quiet nights from today—three already required by D-117 plus two new nights**—and perhaps 2–4 weeks of desk engineering. It does not displace or weaken the MVP: if the extension dies, the original paper remains intact.

## Contributions

1. **A calibrated cross-runtime result:** determine whether the 7B llama.cpp-minus-MLX decode-energy contrast at 128 prompt/512 output tokens clears the applicable armwise floor and retains one direction over its complete interval.

2. **A falsifiable artifact-parity protocol:** both arms must share the upstream checkpoint revision, tokenizer and chat-template hashes, realized prompt token IDs, output cap, greedy policy, batch size one, and warm-cache policy. Any mismatch refuses the contrast.

3. **Runtime-specific floor transport:** demonstrate that the D-117 MLX floor can be reused only for its exact registered MLX cell, while llama.cpp receives an independently minted decode and prefill floor. The contrast uses the maximum of the two decode floors, never their sum.

4. **An honest stack-attribution result:** quantify output-token divergence and conversion differences so that the conclusion remains “MLX-stack versus llama.cpp-stack,” not the stronger and unsupported claim that energy causally “belongs to the runtime.”

## Experiment plan

The primary model is Qwen2.5-7B-Instruct, nominal 4-bit, because the historical diagnostic 7B decode-cell mean is about **192.39 J** for 512 output tokens. Therefore 3%, 5%, and 10% stack differences correspond to approximately **5.77, 9.62, and 19.24 J**. These are planning calculations, not predictions. The comparison becomes difficult only when the stacks are within roughly **2.6%**. Public project documentation establishes that llama.cpp supports Metal on Apple silicon and several 4-bit formats, while MLX-LM supports Apple-silicon inference and its own model conversion/quantization path; it does **not** provide a trustworthy paired energy estimate for this exact machine and workload. [llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/README.md), [llama.cpp quantization](https://github.com/ggml-org/llama.cpp/blob/master/tools/quantize/README.md), [MLX-LM](https://github.com/ml-explore/mlx-lm).

| New window | Registered cells | Design | Estimated time |
|---|---|---:|---:|
| llama.cpp floor | 7B decode plus free prefill rider | 10 absolute members + ten 4-member null ABBA blocks, brackets and references | ~3.3 h, uncertain |
| Runtime contrast | MLX versus llama.cpp, 7B | ten 4-member ABBA blocks; B−A; decode primary, prefill secondary | ~3.0–3.5 h, uncertain |

The 128-token prefill contrast is likely below 5 J and is deliberately a refusal-prone secondary result; no directional prefill claim is expected. If decode also fails, the result is “no stack difference resolvable for this workload,” never equality. A 1024-token fallback would approximately double decode energy while leaving edge error roughly duration-independent, but it changes the floor family and therefore requires **three new windows**—new MLX floor, llama.cpp floor, and contrast. That escalation needs a fresh funding decision.

New harness work is substantial but bounded: a persistent, pinned llama.cpp C-API runner; Metal/build provenance; runtime-native monotonic phase events; token and output traces; adapter cleanup/failure handling; model-conversion manifests; and multi-runtime floor/contrast consumers. It preserves the frozen boundary: warm model, batch one, concurrency one, one sequential request. A queued `llama-server` experiment would introduce scheduler and IPC confounds and is out of scope.

## Hardware and instrument needs

Owned M3 Max, approved charger, existing `powermetrics` calibration system, and additional local storage for the source checkpoint plus MLX and GGUF derivatives are sufficient. The RTX 3080 Ti and Jetsons are irrelevant. The Yokogawa wall meter is **not a dependency**: it could later validate whole-machine totals, but it cannot validate prefill/decode allocation.

## Venue fit and relationship to the MVP

This is a strong capstone paper and credible EuroMLSys/energy-systems workshop submission. It improves the ICPE story by showing that the instrument can referee a practical runtime choice, but one model, one unit, and two non-identical quantized formats are probably insufficient for an ICPE full-paper centerpiece without replication or wall validation. Sections 1–6 and most of Section 8 of the MVP are reused; the new material is artifact matching, the llama.cpp adapter validation, runtime-specific floors, and the cross-stack result.

## Risks and kill criteria

Kill the extension before any quiet night if:

- llama.cpp cannot emit authenticated, clock-compatible prefill/decode boundaries;
- prompt token IDs or chat-template semantics differ;
- Metal offload, fixed-budget output, or warm-cache state cannot be pinned;
- phase sums do not reconcile with the request boundary;
- the daytime pilot’s conservative lower effect estimate is below **7.5 J**—an intentionally uncertain margin above the approximately 5 J bar;
- paired variance implies ten ABBA blocks are underpowered;
- D-117’s MLX floor cannot legally transport to the exact contrast cell.

## Relation to Ed’s original goals

This directly serves the original **runtime-efficiency/energy-as-a-third-axis** goal and exercises the intended swappable-runtime harness. It does not yet address speculative decoding, MTP, MoE routing, KV mechanisms, or split inference; instead, it establishes the disciplined cross-runtime comparison substrate those later mechanisms require.
