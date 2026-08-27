# Opus seat — THREAT-MODEL-PRUNE-01 (Opus 5, read-only, blind). Verbatim (definitive answer).

**Definitive answer — supersedes my two interim ones.** All three code sweeps are in (`joulewise/` 81 files / 3,128 raises; `scripts/` 65 files; `tests/` 153 modules + 3 workflows).

## The reframe — and it changes the prune

D-161's operative test cannot be *"is the defended actor the trusted operator?"* Under a single-operator threat model **every** actor is the trusted operator, and that test retires most of the instrument. The C-sweep confirms it: refusals whose only actor is the operator are not a handful of tripwires but a pervasive posture across ~30 modules — all of `quiet_guard_process.py:59-368`, `sampler_teardown.py:279-362`, the 88 `readiness_identity_artifact_unreadable` sites in `identity_pins.py`, the `bundle.py:83` immutability family, `authentication_io.py:142-623`.

The test that actually separates them is:

> **Does this catch a MISTAKE the operator could plausibly make, or only a DELIBERATE act?**

Fail-closed stays for mistakes — that *is* "tamper-evident for the operator's own benefit." It goes for deliberate-only. Two examples one line apart in the same file: `cli.py:1915` (reduce output landing inside an immutable input bundle) is a mistake anyone makes at 2 a.m. — **keep**. `authentication_io.py:215` (`forbidden key 'estimator_registration'` — an input file declaring itself a registered estimator) has no accidental path — **retire**.

## A — PHYSICS/EVIDENCE (keep; no prunes proposed)

`CELL_REFUSAL_CODES` `floor_extraction.py:170-212` (~44); `REDUCER_REASON_CODES` `analysis_engine/claims.py:39-73` (31); `TRANSPORT_REASON_CODES` `detection_floor.py:293` (15); `detection_floor.py:667` (`n<5`), `:679`, `:1307`, `:1522`; `_RUNBOOK_ARTIFACT_REASON_CODES` `arm_readiness_evidence_t0.py:146-161`; `powermetrics_fiducial.py:200-238` (clock-stamp evidence); `adapters/powermetrics.py:1237-1404`; `quiet_guard.py` `processes_remain` / `independent_census_nonzero`; histsem evidence-unavailability (`arm_readiness.py:3095,3655,3025`); `scripts/prewindow_check.sh:80-204`, `quiet_window_clock.sh:78-102`, `ed_session/*.sh`; `run_campaign.py:2017-2025`. `_EVIDENCE_VALIDITY_NS` 24 h (`arm_readiness_evidence.py:45`).

## B — PRE-REGISTRATION (keep; no prunes proposed)

`PROSPECTIVE_REFUSAL_CODES` `analysis_manifest_v3.py:303-321` + `FINALIZED_*:322-331`; `AUTHORIZED_PLANNED_N_BLOCKS` / `REGISTRY_FREEZE_BASIS` `analysis_manifest.py:158-159`; `multiplicity.py:25-151` (m, Holm/BH); `ratio.py:271` ("form must be frozen before analysis"); `sensitivity.py:69-171`; `outcome_dependent_top_up` `analysis_engine/__init__.py:732,1038`; `calibration_bracketing.py:246-259`; `generate_matrix.py:459`; `axi_decode_config.py:29`; the whole transport vocabulary (floors not transported); `tests/test_axi_analysis_manifest.py:275` and `analysis_manifest_v3.py:43-58` — **pins on pre-registered plans are B, not C**; `scripts/check_paper_replay_fence.py:571,605`; `shard_tests` split/vanished-id fail-closed.

## C — split by the mistake/deliberate test

**C-mistake — KEEP fail-closed** (the majority, and the answer to "why is there so much C"): `bundle.py:83` immutability family ("raw evidence is immutable"); `cli.py:1900,1915,1921,1927`; `analysis_engine/__init__.py:135,141`; `detection_floor.py:2611` and every duplicate-JSON-key / duplicate-slot / duplicate-block-id guard (`inputs.py:217,236`, `registry.py:165`, `floor_extraction.py:2176,2553`, `calibration_bracketing.py:712`); `reduce.py` `power_trace.csv`-vs-raw family; `gensuite/__init__.py:173-178` (`BANK_HASH`); `floor_mint_estimator.py:85-107`; `scripts/setup_quiet_guard.sh:14-16,88` (three digests before **root** execution — a privilege boundary, not an evidence one); `scripts/generate_arm_readiness.py:170,175` (defends against the tool's own bug); `arm_readiness.py:11649-11672` and `whole_window.py:3609-3617,5247-5254` (forged-lane / forged-row guards protect *published* claims); `salvage_dangler.py` symlink/inode family.

**C-deliberate — PRUNE.** Ranked in (i).

## (i) Ranked prune list — top 15

1. **HISTPACK-PROMISOR-NOFETCH-01** (`WAVE-ROWS.md:16`; S3 D4) — retire unbuilt. Largest saving because the cost is unspent.
2. `histsem_pinset_mismatch`, `arm_readiness.py:3733-3736` → WARN after S14.
3. `histsem_post_authoring_delta_unexpected`, `:3772-3777` → WARN.
4. `PINSET_SHA256`, `tests/test_receipt_histsem.py:42` (`:196,:248`) → "no *unreviewed* update".
5. **Custody-tool `.sha256` sidecars**, `tests/test_family_marker.py:788-794`, enforced `arm_readiness.py:11019` `tool_mismatch` — a **fourth** tripwire ED-ITEMS never listed; fold into the S14 lane.
6. Per-file digest tables on the three packs (`test_d117_floor_qwen25_1p5b_plan.py:473-478` "exactly 154 files"; `test_d117_decode_contrast_plan.py:828-830` "135 files"; `test_d117_floor_qwen25_7b_plan.py:470-475`) → retire; `test_arm_readiness_registry.py:375` already regenerates every pack and proves the same fact.
7. `FROZEN_GENERATOR_SHA256` (`:1034`, `contrast:2225`) → retire.
8. `test_gen_state.py:346` / `:496-497` (`EXPECTED_IDS`, `len==108`) → WARN. Cost: four `main` CI failures on 2026-08-26/27 (`TASK_QUEUE.md:109`).
9. `gen_state.py --check` hard-fail on all 8 CI cells (`ci.yml:25-26`) → WARN, keep the check.
10. Source-text greps `tests/test_receipt_histsem.py:169-193,198` → retire; keep the behavioural test at `:386`.
11. `authentication_io.py:215,375,380,623` (`forbidden_json_key`, `input_changed`, AST direct-read lint) → retire.
12. `quiet_guard_process.py` + `sampler_teardown.py:279-362` → WARN-AND-RECORD *wholesale*: D-148(6) already accepted the recorder race and same-UID injection as registered limitations, so this code enforces a risk the project has ruled out of model.
13. `identity_pins.py:1168,1176,1187` (hashing the *source file* of pinned callables) → retire.
14. `ci.yml:112,123-134,188-205` literal timing pins (`2036.0`, `[145.911, 2005.0]`) → derive, don't pin.
15. Doc↔code prose tripwires (`tests/test_docs_freshness.py:187-254`, `test_bridge.py:1568-1630`, `test_d078_reason_registry.py:121-233`) → WARN.

**Landing procedure — this is not a one-line edit.** Three meta-guards enforce reason-code totality: `tests/test_reason_code_partition.py:183` (every code in exactly one of DATA/CONTRACT/**DEAD**/LOCK), `:201` (live codes need a real emitter), `:214` (DEAD codes must have none); plus `tests/test_calibration_exits.py:1532` (every code needs an executed witness) and `test_d078_reason_registry.py:107`. Good news: **`DEAD_REASON_CODES` (`reason_kinds.py:54-59`) is the mechanical retirement lane.** RETIRE is *cheaper* than WARN-AND-RECORD, which keeps the code live and needs a non-refusing emitter. Prefer retire wherever the finding has no consumer.

## (ii) Must NOT prune before `_v4`

**Items 2–5 and 10** — the whole `HISTSEM_REASON_CODES` current-side set. The frozen runbook names them: C10 step 2 asserts *"the `_v1` pinset member is byte-unchanged"* before `PINSET_MINT_HEAD` (`real-transaction-runbook.md:762-768`); the fixation commit's sole content is the `hS` literal plus its loud-fail guard in `tests/test_receipt_histsem.py` (`:184-185`, `:1283`); E4 recomputes `hS` from the mint-head bytes (`:1032`); CI runs `verify_receipt_histsem.py --require-published` (`ci.yml:28`). Estate 11 replays **49** refusal assertions from the frozen runsheet, including `histsem_pinset_absent` at `s0-runsheet-r4.md:3902`.

**Also hold 6–9 and 14** — estate 11's §4 probe battery compares against those pack digests, and `gen_state.py --check` plus the shard timing pins are green CI steps the clone proof passes through; moving them mid-cut re-baselines the estate.

**Safe now: 1, 11, 12, 13, 15** — none appears in the runbook or runsheet. Item 12 is the biggest immediate win and is already ruled: D-148(6) accepted exactly these as registered limitations, so downgrading them installs a decision Ed made on 2026-08-19. D-161(1)'s S14 lane is correctly sequenced precisely because it *adds* a lane without altering any refusal.

## (iii) The §7 sentence

Replace the opening of `docs/paper/draft-v1.md:310`:

> The repository is tamper-**evident for the operator's own benefit — a way to catch one's own mistakes — not tamper-proof against anyone**; it assumes a single trusted operator, so every gate below defends against error and post-hoc choice, never against an adversary.

## (iv) Strongest argument that a specific C item is really A or B

**`histsem_pinset_mismatch` is B in disguise.** The contract's normative honest limit (`docs/contracts/receipt_histsem_verifier.md:194-198`) says `pack_generator_check_status: PASS` proves *the plan-pinned generator regenerated the authenticated historical pack coordinate* — a claim meaningful only relative to a **fixed** coordinate. Drop the current-side pin and an honest operator who regenerates a pack gets a clean PASS against the *new* bytes: the verifier authenticates whatever is present. That is not tampering; it is the post-hoc substrate substitution D-161 explicitly keeps fail-closed, arrived at by accident. W-10 is this week's existence proof — the gamma `_v3` pack really was regenerated.

**The rebuttal, and the asymmetry it forces.** The pre-registration anchor is not `current_pack_sha256`; it is `historical_pack_tree_sha256` at the recorded `head_commit`, which Git already fixes and which `histsem_historical_digest_mismatch` (`arm_readiness.py:3763-3766`) enforces independently, backed by `histsem_historical_tree_not_pre_authoring` (`:3767`). So the correct prune is **asymmetric: keep the historical-side equality fail-closed (B); downgrade only the current-side equality and the delta list to WARN.** Every pre-registration property survives; the four-tripwire hand-repair loop that blocked the mint twice does not.

**Opportunity cost.** S9 found **122 of 460 ruled clauses (27%) with no producer-side check** (`ruled-not-installed-sweep/FINDINGS-TABLE.md:17`), 16 of them D-078 analysis-manifest refusal codes. The C tripwires cost almost nothing in CI (`test_receipt_histsem` 28.7 s, `test_gen_state` 2.2 s of an 8,144 s suite); their entire cost is operator round-trips and mint blockages. Prune C for the unblocking — then spend the freed enforcement budget on the 122, where the failure is silent.
