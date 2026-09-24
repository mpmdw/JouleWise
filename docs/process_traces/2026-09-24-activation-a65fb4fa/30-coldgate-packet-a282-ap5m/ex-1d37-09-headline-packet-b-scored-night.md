# 09 — Headline packet B: a scored-campaign night kind (design seat, Opus 5.5, read-only)

Read at main `313efcca` (worktree `wt-1d3796d5-consult`). No code was run and no model was loaded. File:line citations are at that head. Every duration, rate and count marked **(planning)** is an estimate until the sizing pilot measures it.

## 0. Answers first

1. **Reuse the idle night's skeleton and its power recorder. Reuse the MLX suite adapter unchanged for generation. Do not run the desk controller inside the night.** Each envelope is a fixed 600 s powermetrics capture taken by the idle collector's `PowerRecorder`. (An **envelope** is one continuous power capture. Its **interior** is the 480 s span that starts 60 s after capture start, the 60 s being the **offset**.) In the interior a worker process runs one model through `MlxRuntimeAdapter.run_suite`, which already stamps item, level and per-token events on the wall clock (`joulewise/adapters/mlx_runtime.py:438-690`); energy is the anchored frames integrated over those windows with the idle kind's `align_frames`/`integrate` (`scripts/sample_quiet_predicate_evidence.py:294-332, 359-472`).
2. **The claim numerator is level-window energy, not envelope energy and not a sum of per-item energies.** A **level window** runs from the first item's start marker to the last item's end marker for one contiguous run of same-level items. Joules per correct answer for one cell (model × thinking arm × MATH level) = Σ level-window energy over that cell's windows ÷ correct answers in the cell. The offset, the post-block tail and any unused interior are idle padding and never reach the numerator. AP-5 already says this (`docs/contracts/analysis_plans.md:268`): per-item windows are audit evidence, not independent energy replicates.
3. **Items are packed into envelopes by predicted decode seconds, never by cell.** A cell is cut into fixed **sub-blocks** (ordered slices of one level's items, identical for both models). A pure packer assigns whole sub-blocks to envelopes. Planning figures: 64 thinking-off items on the 8B ≈ 700 s, so a level needs two sub-blocks of 32; the 1.7B fits two or three levels per envelope.
4. **The night framework is idle-kind-shaped in about fifteen places** (§1.3). Replace the scattered `== "quiet_predicate_evidence"` literals with one kind table before adding the second kind.
5. **The first scored night is the sizing pilot** (disjoint pilot pool, its own ruled registration; it may set only caps, sub-block size and pitch), preceded by a bench dry run of every stage except live powermetrics.

## 1. What exists

### 1.1 Model-run measurement paths

| Path | Where | Reusable in a night? |
|---|---|---|
| Desk controller: validate → prepare → idle_baseline → warmup → measured_run → idle_drift_sentinel → cleanup → reduce, one bundle per run | `joulewise/controller.py:849-866`, `run_benchmark` 238-351 | **Not as the envelope engine.** Its powermetrics window starts after idle baseline and warm-up (`controller.py:1222-1287`): no fixed offset/interior/tail, and its campaign-policy/cooldown/admission gates never ran unattended. Keep it as the desk route. |
| D-013 "controller-as-DUT" rule: nothing but the runtime inside the measured window; events buffered and flushed afterwards | `controller.py:13-23, 1263-1266` | **Yes, as a rule.** The worker keeps every record in memory until the recorder stops. |
| MLX suite adapter: per-item `item_start`/`item_end`, per-item prefill/decode phase events, per-token `timestamp_s` + `token_id`, `suite_items.jsonl` rows with `response_text`, `status` (`succeeded`/`capped`/`malformed`/`runtime_failed`), `emitted_token_ids` | `mlx_runtime.py:438-690`, token records ~845; marker schema `joulewise/suite.py:18-136` | **Yes, unchanged.** It runs in the worker. `prepare` (load and identity) and `warmup` (`mlx_runtime.py:230-375`) run in the gap before the envelope. |
| Suite ordering: `block_latin_square_v1` (Williams rows) | `suite.py:1261-1376` | **Yes**, for level order inside envelopes. |
| Reducer level/block/item windows and identifiability | `joulewise/reduce.py:3853-3950`, precheck 640-670 | **Pattern only** (reads bundles); the scored reducer is cross-checked against it on a fixture. |
| Idle collector: `PowerRecorder` at 100 ms, rate-aware clock anchor v3.1, exact-integer interior integration, network-time provenance | `sample_quiet_predicate_evidence.py:721-837, 294-332, 440-472` | **Yes.** It is the instrument path proven on 09-22 (twelve envelopes, anchors bounded, interiors complete: `docs/process/NIGHT_HANDBACK.md:995`). |
| Idle executor: settle, network time OFF, pitch schedule, drift abort, busy-core recorder, non-observer abort, group cleanup, per-envelope `log show` attestation, outcome/refusal records | `joulewise/quiet_predicate_campaign.py:1483-1722` | **Yes, factored** (import, never copy). |
| GSM8K scored import: selection, rendered prompts, annotations, `SCORER_ID`, four-way outcome rule, exact-set scorer over `suite_items.jsonl` rows | `joulewise/benchmark_import.py:41-100, 908-1072`; `scripts/gen_gsm8k_scored.py` | **Pattern for the MATH importer (parallel seat).** Scoring runs at harvest, after the last capture. |
| Model identity: panel pins (revision, tokenizer and chat-template digests), weight-tree digest | `configs/model_panels/qwen3_4bit.json`; `mlx_runtime.py:85-150`; `joulewise/provenance.py:176` | **Yes.** Note that the panel pins `enable_thinking: "false"` and only a thinking-off rendering pinset. The thinking-on arm needs a second pinset (importer seat). |
| Calibration-ledger session (`calibration_ledger.py:1-21`) and measurement pack (`TRANSACTION_PACK`, `night_gate.py:916-1185`, `scripts/launch_window.py`) | — | **No.** `probe_payload_kind` refuses a payload kind co-exported with `CALIBRATION_LEDGER` (`night_gate.py:149-161`); the pack's census row has never passed unattended (`RUN_STATE.md:178`). The scored kind is `DIAGNOSTIC_NO_PACK` and mints no floors. |

### 1.2 How binding works today (keep it)

A ruled registration pins protocol values and the zsh chain source, never Python (`night_gate.py:1-12, 91-121`); Python is pinned by `measurement_head` plus a sealed manifest of per-file digests (`quiet_predicate_campaign.py:83-181`) whose digest is a wrapper literal, and the wrapper's digest is in the plan. The `NightPlan` v2 keys are closed (`night_gate.py:253`). **Everything new therefore binds through the manifest and the registration, with no plan-schema change.**

### 1.3 Idle-only assumptions (each needs a kind branch)

- `evidence_night.py:24` single `KIND`. `:319` `prepare` refuses any other kind. `:154-162, 214, 226, 381, 1390` hard-code the `qpe01-pilot-n1-` plan-id prefix and root suffix. `:456-469` author the plan from `quiet_predicate_campaign.PROTOCOL_PATH` with `window_max_s=9000`. `:479` calls `gen_evidence_night.py`. `:234-270` `sealed_candidate` imports the idle manifest functions. `:272-316` notice text says "No model … runs". `:1083-1117` spend corecaptured and machine-quiet only on the idle kind.
- `night_gate.py:81` single `EVIDENCE_CHAIN_PATH`. `:149-161` recognise only `quiet_predicate_evidence`/`calibration`. `:1354-1366` authenticate the chain source only for the idle kind. `:1505, 1546` scope the corecaptured and 30 s non-observer predicates to it. `:1678` gives the registration defect text.
- `quiet_predicate_campaign.py:145-162` `manifest_for` demands the idle protocol and 9000 s.
- `scripts/gen_evidence_night.py:41, 53` fix the kind.
- `joulewise/night_agent_install.py:795-800, 1165-1195` send non-idle kinds to the calibration-reservation branch.
- `scripts/run_night.py:998-1053` list the idle files in the artifact list. `:1210-1216` courier text. `:1318-1373` `_evidence_cleanup_error` is idle-only. `:3686-3690` verify-only probe branch.
- `scripts/magistrate_watchdog.py:851-869` zero-capture disk facts return False for any third kind. That is safe, but it means a scored zero-capture refusal never releases.
- `arm_retry.py:60, 333` and `NIGHT_COURIER_PROMPT.md:46-53` hold idle-specific texts.

## 2. Envelope design

**Per-slot timeline (planning).** A slot is one envelope plus the gap that precedes it.

| Phase | Worker | Recorder | Counts toward J/correct? |
|---|---|---|---|
| Gap before envelope (pitch − 600 s) | spawn; `prepare` (load from warm page cache; tokenizer and template pin check); `warmup` (4 tokens, `mlx_runtime.py:56`) plus one fixed warm-up prompt; reports ready | off | no |
| Envelope 0–60 s (offset) | idle, model resident | on | no; the last 30 s form the **pre-block idle reference** |
| 60–540 s (interior) | runs the envelope's sub-blocks back to back | on | only inside level windows |
| After the last item, to 600 s | idle | on | no; the last 30 s (or all of it if shorter) form the **post-block idle reference** |
| After recorder stop | writes records, exits | off | — |

A worker not ready at envelope start is excluded (`load_after_envelope_start`), so load never happens inside a capture. One worker process per envelope, one model, cleanup proven per envelope as in the idle kind; the chain reads each weight tree once before the settle so loads come from page cache. **Pitch ≈ 660 s (planning)**, set from the pilot's journaled load, warm-up, cleanup and attestation wall times. With settle 600 s: 600 + 11 × 660 + 600 = 8,460 s ≤ 9,000 s, so **12 envelopes per window (planning)**.

**Packing by decode seconds.** For each (model, arm, level), the pilot supplies decode seconds per token (upper value), prefill seconds, and the p95 emitted tokens per item. The predicted duration of a sub-block is Σ(prefill + p95 tokens × s/token). The packer takes sub-blocks in the pre-registered order and places each in the current envelope if the running total is ≤ 480 s − 30 s guard; otherwise it opens a new envelope. It is first-fit, deterministic and pure, and its output, the **roster**, is hashed. Sub-block size is one registered integer per (model, arm), equal across levels, and the same item slices are used for both models so every sub-block is paired.

**Overrun rule.** Levels are not pooled mid-envelope. If an item is still running at 600 s − 5 s, the worker aborts it. Its sub-block is then **void**: its energy is excluded and the whole sub-block is re-queued once, at the end of the night's roster if budget remains, otherwise into the successor night's roster. Greedy decoding reproduces the same tokens, so the re-run is the same work. The whole sub-block is re-run, never only the surviving items, because dropping long items would bias both accuracy and J/correct downward. A second overrun of the same sub-block marks it `not_estimable`. Every overrun is reported.

**Caps and truncation.** One output cap per arm is pinned in the registration. Constraint: cap × s/token_upper(8B) + prefill ≤ 480 s − guard. At a planning 45 tok/s that is about 19k tokens. A capped item without a parseable answer is `truncated` and counts as incorrect (D-047.6, `benchmark_import.py:951-953`). A cell with more than 20% truncations is labelled cap-bound. Thinking tokens are split from answer tokens offline, at the `</think>` token id in `emitted_token_ids`.

**Attribution.** Internal item boundaries cancel inside a level window; only its two outer edges carry error, at worst one 100 ms frame × the load step ≈ 2 J per edge at 20 W (planning), against level windows of ≈10³–10⁴ J. Per-item energies (descriptive, with identifiability) feed the physical fit E = fixed + a·prompt tokens + b·generated tokens. That fit is not a claim input. The reported numbers are gross joules and **net** joules, where net = gross − the mean of the two idle references × window duration. Gross versus net as the primary is ruling R2. Envelope utilisation (Σ level windows ÷ 480 s) is reported.

**Order and heat.** The unit that gets ordered is the envelope. Models alternate as a **palindrome** over the night's envelopes. ABBA is the four-envelope case. A palindrome gives each model the same mean position for any counts (3 × 1.7B, 8 × 8B: B A B B B A B B B A B), so linear thermal drift cancels in the model contrast. Level order across a model's envelopes follows Williams rows (`suite.py:1359-1376`). Covariates per envelope: pre-block idle power, `pmset -g therm`, start drift. One arm per night; arms alternate across nights.

**Exclusions.** The idle vocabulary carries over (`pilot_protocol_v3.json` `exclusions`), including `non_observer_process_busy` with its two-consecutive abort. The scored kind adds `load_after_envelope_start`, `worker_error`, `model_identity_mismatch`, `sub_block_overrun` and `interior_support_incomplete_over_level_window`. Support is checked over each level window, not only over the interior.

## 3. Chain, driver and gate changes

- **Kind table** (`joulewise/night_kinds.py`): per kind the chain path, executor, manifest functions, plan-id prefix, root suffix, `window_max_s` source, notice renderer, courier files and zero-capture predicate. Idle behaviour stays byte-identical (unchanged idle tests prove it).
- **Payload kind** `scored_campaign`, set by `export NIGHT_PAYLOAD_KIND=scored_campaign` in `scripts/night_chains/scored_campaign.zsh`. `probe_payload_kind` accepts it and still refuses repeats, unknown kinds and any co-export of `CALIBRATION_LEDGER`.
- **What the night pins.** The **registration** pins the kind, `chain_source_sha256`, settle, envelope, offset, interior, tail guard, pitch, start-drift abort and maximum, power interval, `window_max_s`, exclusions, the non-observer rule, the energy rail, per-arm caps, the sub-block size, the packer and guard, the overrun rule, the ordering rule, the idle-reference definitions, the estimator with the ≥3-correct guard and merge order, the Holm family, and a fixed n (D-062). Each `RULED_REGISTRATIONS` entry gains `payload_kind`. The **scored evidence manifest** (`joulewise.night_scored_manifest.v1`) pins the tracked-file digests (below), the roster-slice digest, the suite-manifest and annotations digests, `selected_item_ids_sha256`, the prompt-template id and digest per arm, the rendering pinset ids, `scorer_id`, and, per model, the panel entry plus the `model_artifact_identity` tree digest.
- **Arm check** (`evidence_night.check`). Corecaptured and machine-quiet run for both evidence kinds. New rows: weight-tree digests equal the manifest (about 5 s of hashing, planning); tokenizer and template pins; clone venv imports `mlx`/`mlx_lm` (verify-only, no load); free disk for outputs.
- **t0 gate** (`night_gate`). C5 authenticates the scored chain source against `measurement_head`. C1 refuses a registration whose `payload_kind` differs from the chain's. The C3 corecaptured and 30 s non-observer predicates run for both evidence kinds. The gate still pins no Python and does not hash weights. The chain re-verifies weights before the settle, and a mismatch there is a zero-capture refusal.
- **Driver and courier.** Scored outputs sit under `night/scored/` (walked by the existing `os.walk` pattern) plus `night/scored_envelopes.jsonl`, `scored_processes.jsonl`, `scored_outcome.json` and `scored_cleanup.json`, all added to `_artifact_list`. `_evidence_cleanup_error` and the courier text are generalised by kind. The courier reports envelopes attempted and retained, voided sub-blocks, per-cell counts, accuracy, truncations and gross J/correct, watermarked PROVISIONAL; claim numbers are recomputed at the desk from the archive by the same pure reducer.
- **Watchdog.** For the scored kind, zero capture means: no `chain.started`, `night/scored` absent or empty, `scored_envelopes.jsonl` absent or empty, and no worker process journaled. Coordinate with the A277 zero-capture evidence writer (in flight, record 06).

## 4. Per-item records

A worker keeps everything in memory during the envelope and writes `night/scored/envelope-NN/items.jsonl` after the recorder stops. Each row holds:

- identity: `item_id`, `level`, `sub_block_id`, `position`, `model_id`, `arm`, `prompt_sha256`
- tokens: `prompt_tokens`, `emitted_tokens`, `thinking_tokens`, `answer_tokens`
- runtime result: `stop_reason`, `status`, `truncated` (status `capped`), `response_text`, `response_sha256`, `emitted_token_ids`
- timing: `item_start_epoch_s`, `first_token_epoch_s`, `item_end_epoch_s`, plus a `ClockStamp` (wall time bracketed by two monotonic reads) at each level-window edge

At harvest the executor adds `extracted_answer`, `outcome` (correct/incorrect/truncated/malformed) and `scorer_id` from the pinned MATH scorer. It also adds the anchored descriptive `energy_gross_j` and `identifiability` per item.

**Binding to the capture.** Each envelope directory holds the raw plist, the recorder's `session.json` (anchor, `recorder_kind`, network-time provenance) and the worker's rows, which carry the recorder session id and envelope index. Windows are integrated on the anchored wall timeline, valid only under the network-time-OFF record and per-envelope attestation. `levels.jsonl` holds per level window: edges, gross/net joules, native sample count, complete-support flag, item ids and exclusions.

## 5. Files, tests, gate

**New:** `joulewise/night_kinds.py`; `joulewise/scored_campaign.py` (verify/run/record/refuse, manifest, execute); `joulewise/scored_worker.py`; `joulewise/scored_packing.py` (pure); `joulewise/scored_reduce.py` (pure: windows, idle references, exclusions, scoring join, J/correct and the decomposition J/token × tokens/attempt ÷ accuracy, guards); `scripts/night_chains/scored_campaign.zsh`; `scripts/build_scored_roster.py`; `configs/campaigns/<headline>/pilot_registration_v1.json` plus roster slices.

**Modified:** `joulewise/night_gate.py`, `joulewise/evidence_night.py`, `scripts/gen_evidence_night.py` (table-driven), `joulewise/night_agent_install.py`, `scripts/run_night.py`, `scripts/magistrate_watchdog.py`, `joulewise/arm_retry.py`, `joulewise/quiet_predicate_campaign.py` (export shared helpers only), `docs/process/NIGHT_COURIER_PROMPT.md`, `docs/process/NIGHT_HANDBACK.md`.

**Manifest paths for the scored kind:** registration, chain source, every new module above, `adapters/mlx_runtime.py`, `adapters/suite_control.py`, `suite.py`, `sample_quiet_predicate_evidence.py`, `quiet_admission.py`, `quiet_predicate_campaign.py`, `uncertainty_evidence.py`, `adapters/powermetrics.py`, `night_gate.py`, `night_agent_install.py`, `run_night.py`, suite manifests, annotations, the MATH scorer.

**Regressions:** (1) packed predicted work never exceeds 480 − guard, with every `max`/`min` cut to each operand (operand-collapse rule); (2) roster deterministic and identical across models; (3) palindrome and Williams balance; (4) synthetic frames of known power: level-window energy exact, and offset, tail and slack move the numerator by exactly 0 J; (5) the estimator refuses an envelope or interior numerator; (6) <3 correct gives the registered merge or `not_estimable`; (7) an overrun voids and re-queues the whole sub-block exactly once; (8) truncated counts incorrect, thinking-token split; (9) the worker writes nothing before the recorder stops; (10) `load_after_envelope_start`; (11) all idle tests unchanged, scored kind accepted, ambiguous or ledger co-export refused, registration kind mismatch refused; (12) machine predicates run for the scored kind at arm and t0; (13) scored zero-capture facts; (14) courier and artifact lists; (15) `scored_reduce` cross-checked against `reduce._suite_level_metrics` on one fixture.

**Gate status: claim-bearing, full shape.** Reducers, plan writers, admission predicates and registrations are on the fixed list (synthesis item 5): an Opus lens, Sol refuters, a cold Fable pass, a delta re-audit per fix round, and a full local replay on the integration tree. Nothing here was run.

## 6. Sequencing

1. **PR A, kind table (no behaviour change).** Full gate, because it touches `night_gate`. It can start now.
2. **Parallel, prerequisites:** the MATH importer (manifests, annotations, scorer, a disjoint pilot pool, and a thinking-on rendering pinset) and the AP-5 amendment. The amendment must name the scored-envelope level window as the evidence unit where AP-5 says "strict-valid bundles" (`analysis_plans.md:270`), in addition to allowing MATH levels as the difficulty axis.
3. **PR B, scored kind** (packer, reducer, worker, executor, chain, arm, gate and courier branches), built on A and the importer.
4. **Bench dry run, everything but live powermetrics.** Prepare, then check with a fixture `launchctl` (`rehearsal_ready`, `evidence_night.py:1124`), then the real render and the real driver, then the chain with `EVIDENCE_POWER_RECORDER_REPLAY` (archived frames; refused in any armed night by `run_night.py:581-596` and at harvest as `REPLAY_NEVER_EVIDENCE`) and the real MLX worker on a two-envelope mini-roster under a dry-run registration absent from `RULED_REGISTRATIONS` (so it can never arm), then harvest, scoring, summary and courier render. Bench only, never in a window.
5. **Pilot registration cold gate, then the first scored night, the 16-item sizing pilot.** Both models, both arms, pilot items only, watermarked PILOT, never pooled (D-062). It measures s/token, tokens per item per level and arm, cap hits, and load and gap wall times.
6. **Headline registration.** The pilot parameters are derived by the pre-registered formula. A cold gate checks the arithmetic mechanically. Then the thinking-on nights (primary for the crossover question) and the thinking-off nights (the decomposition baseline). Planning: thinking-off at 64 per level ≈ 11 envelopes ≈ one window.

## 7. Open rulings

- **R1 Route.** Idle collector plus MLX worker (recommended) versus one controller bundle per envelope (no offset or tail; gates untested unattended).
- **R2 Primary numerator.** Gross (recommended: what the machine spent while answering) or net of the in-envelope idle reference. Both are reported.
- **R3 Greedy in thinking-on.** The Qwen3 model card advises against greedy decoding in thinking mode (repetition loops). Greedy plus a cap-bound label, or pinned seeded sampling shown deterministic on MLX. Decide before the pilot.
- **R4 Pilot size.** 16 items per level (recommended; per-level lengths are what packing needs) or 16 items in total.
- **R5 Registrations.** Two ruled registrations (pilot, then headline with a mechanical gate), or a single registration with the formula and a sizing receipt.
- **R6 Overrun re-queue.** Within the same night first, or always to the successor night.
- **R7 Energy rail.** `rail_sum_w` (the anchor's rail) versus `combined_w`/DRAM. It must match the floors Paper B cites.
- **R8 Floors** carry over only on matching identity pins; level windows sit far above the ≈5 J bar, per-item descriptives do not.
- **R9 Successor.** Whether D-182's zero-capture successor applies to the scored kind unchanged, and what a post-capture abort permits.
- **R10 Mixing arms in one night.** Recommended: never.
