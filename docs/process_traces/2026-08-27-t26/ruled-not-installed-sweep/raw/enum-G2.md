# S9 sweep — G2 enumeration (D-122, D-123, D-124 + all amendments, D-125)

Repo read-only at `/Users/edr/code/JouleWise`, branch `main`.
Index rows read: `docs/decision_log.md:147-150`.
Bodies read verbatim: 7905-7935, 7936-7965, 7966-8004, 8005-8059, 8060-8111,
8112-8137, 8331-8350, 8351-8371.

---

## D-122 — prefill contrast in scope, 256-token prospectively frozen arm on gamma

### D-122 · clause 1 (index row + body): the arm is PROSPECTIVELY FROZEN
- clause (verbatim): "the contrast window (gamma) grows a prospectively frozen 256-token prefill ABBA arm" (index row) / "which is acceptable because the arm is PROSPECTIVELY FROZEN and the claim machinery fails closed."
- source: docs/decision_log.md:147 and docs/decision_log.md:7920-7921
- status: **B — INSTALLED, NO PRODUCER-SIDE CHECK** (this is the D-157 shape, on the D-157 arm)
- evidence:
  - `configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/analysis_manifest_v3.json:1026-1040` — the prefill_p256 contrast cell carries three `"status": "EMPTY"` slots: `"TODO(lead authority): ratify prefill inferential test"`, `"TODO(lead authority): ratify prefill multiplicity family"`, `"TODO(lead authority): ratify a 256-token prefill floor or transport rule"`.
  - `configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/generate_configs.py:973-987` — the generator *emits* those EMPTY slots for `test`, `family_alpha`, `multiplicity`, `family_m` on cell `d117-sw-prefill-p256-contrast-qwen25-1p5b-vs-7b`.
  - `configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/analysis_manifest_v3.json:2` — `"schema_version": "joulewise.analysis_manifest.v3.prospective"`; grep for `freeze_status` in that file returns NOTHING, so the manifest is not marked frozen either.
  - `joulewise/analysis_manifest_v3.py:1376-1385` `_contains_unresolved_slot` returns True for `"EMPTY"` / `TODO(` values; `joulewise/analysis_manifest_v3.py:1904-1932` raises `analysis_prospective_unresolved_slot` and `analysis_prospective_not_frozen`. So the *consumer* refuses these bytes.
  - **The "no callers" grep:** `grep -rn "validate_prospective_analysis_manifest_v3" --include="*.py" .` → only `joulewise/analysis_manifest_v3.py:2838` (inside `build_prospective_analysis_manifest_v3`, itself called only from `tests/test_analysis_manifest_v3.py:490`), `:3759` (inside `finalize_prospective_analysis_manifest_v3`), `:3876` (finalized-lineage revalidation), plus `tests/test_analysis_manifest_v3.py`. **No script in `scripts/` calls it.** `grep -rn "analysis_manifest_v3\|prospective" scripts/*.py` shows only `scripts/finalize_analysis_manifest.py:45` (the claim edge).
- producer: `configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/generate_configs.py` (`floor_cells()` ~:958-988 and `analysis_manifest()` ~:1540-1560). It writes the unresolved slots and never runs the prospective validator; no freeze/readiness script runs it either.
- transaction_relevant: **yes** — this is the gamma `_v4` mint / arm-readiness / consumption-edge path; a 310-minute gamma night collected against these bytes would be refused at `finalize_analysis_manifest.py` after the fact.
- note: D-139 (docs/decision_log.md:164) later ruled exactly these values (Holm family, alpha=0.05, m=2, decode+prefill_p256, two-sided; dedicated p256 floor). The generator was never updated — that is D-157's finding, and it is reconfirmed here from the D-122 side.

### D-122 · clause 2: gamma's pack gains the 256-token prefill ABBA arm
- clause (verbatim): "Gamma's campaign pack gains a 256-token prefill ABBA arm"
- source: docs/decision_log.md:7924
- status: **A**
- evidence:
  - `configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/generate_configs.py:475-488` — `STAGE_SPECS` carries `03_prefill_p256_contrast_blocks_01_05` and `04_prefill_p256_contrast_blocks_06_10`, `measurement_arm: "prefill_p256"`, blocks 1-5 and 6-10.
  - `.../generate_configs.py:698-713` — `prefill_family_definition()` pins `"prompt_tokens": 256`, `"metric": "phase_energy_j.prefill"`, ABBA alias relation.
  - `.../generate_configs.py:723-739` — producer-side refusal: `raise ValueError(f"prefill family {arm} is invalid: ...")` if `validate_condition_family_definition` rejects the emitted family.
  - pack bytes: `.../analysis_manifest_v3.json:45,56,81,89` — the four p256 stage/condition-family rows exist on disk.
- producer: the gamma `generate_configs.py`; the pack directories `03_*`/`04_*` exist.
- transaction_relevant: yes — the arm itself is the transaction.

### D-122 · clause 3: "frozen prompt"
- clause (verbatim): "(frozen prompt, frozen member/minute budget …)"  [prompt half]
- source: docs/decision_log.md:7924-7925
- status: **B — INSTALLED, NO PRODUCER-SIDE CHECK (and self-declared unratified)**
- evidence:
  - `configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/prefill_prompt_candidate.json:4` — `"candidate_status": "PROPOSED-PENDING-LEAD-RATIFICATION"`; `:6` `"prompt_text": "TODO(lead): no named authority pins text"`; `:22` `"lead_rerun_required_before_ratification": true`.
  - `.../generate_configs.py:83` — `PROMPT_STATUS = "PROPOSED-PENDING-LEAD-RATIFICATION"`, stamped into every prefill member config at `:1019-1023` (`prompt-status=` tag).
  - No tokenizer is ever run: `grep -rln "planned_token_count\|token_count_basis\|LOCAL-TOKENIZER"` hits only the ten pack generators and `tests/test_d117_decode_contrast_plan.py`. Nothing in `joulewise/` or `scripts/` verifies the prompt really tokenizes to 256 tokens.
  - Contrast (this is the shape an A looks like): `configs/campaigns/d117_floor_qwen25_1p5b_v3/generate_configs.py:719-738` `load_p256_prompt_text()` raises on six distinct drifts ("p256 prompt artifact bytes drifted", "…UTF-8 hash differs from the Q1 pin", "…does not declare 256 planned tokens", "…shared-tokenizer pin drifted"). The **floor** packs treat this artifact as Q1-RATIFIED and pin it by byte SHA (`:96-99` points at the `_v1` pack copy); the **gamma** pack that owns the artifact still declares it unratified.
- producer: gamma `generate_configs.py` `prompt_candidate()` :755-778 — emits the bytes, no check.
- transaction_relevant: **yes** — the p256 prompt is the measured stimulus of the funded arm, and the alpha/beta floor packs already consume it as ratified while its own pack calls it a candidate.

### D-122 · clause 4: "frozen member/minute budget"; "Night budget grows"
- clause (verbatim): "(… frozen member/minute budget …). Night budget grows"
- source: docs/decision_log.md:7925-7926
- status: **A**
- evidence:
  - `configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/generate_configs.py:1804-1831` — `runtime_budget` with `decode.minutes_with_margin 168.0`, `prefill_p256.core_minutes_before_margin 110.0` / `minutes_with_20_percent_margin 130.0`, interior-reference augmentation 10.0/12.0, `combined_minutes_with_margin: 310.0`, `combined_derivation: "168.0 + 130.0 + 12.0"`, `member_replacement_authority: False`.
  - test that would fail if removed: `tests/test_d117_decode_contrast_plan.py:2365` — `self.assertEqual(budget["combined_minutes_with_margin"], 310.0)`.
- producer: gamma `generate_configs.py` `plan_tree()`.
- transaction_relevant: yes — window duration.

### D-122 · clause 5: "lands in the U7 pack under the adopted stage_launch.v1 contract"
- clause (verbatim): "lands in the U7 pack under the adopted stage_launch.v1 contract"
- source: docs/decision_log.md:7925-7926
- status: **A**
- evidence: `tests/test_d117_decode_contrast_plan.py:2328-2335` — `test_stage_launch_recipes_and_runtime_budgets_cover_both_arms` asserts `stage["launch"]["schema_version"] == "joulewise.stage_launch.v1"` for the gamma pack's stages (both arms).
- producer: gamma `generate_configs.py` plan-tree stage nodes.
- transaction_relevant: yes — launch path.

### D-122 · clause 6: "the operator packet states the new duration"
- clause (verbatim): "the operator packet states the new duration."
- source: docs/decision_log.md:7926-7927
- status: **C — NOT INSTALLED**
- evidence (what I looked at):
  - `ls docs/process/window-run-cards/` → a single file, `shakedown-v3-first-light.md`. There is no gamma run card.
  - `grep -rn "310" docs/process/rehearsal-operator-card.md docs/process/phase2-transaction-runsheet.md docs/phase_2/window_runbook.md docs/process/ed-evening-checklist.md docs/process_traces/2026-08-22-t20/real-transaction-runbook.md` → **no hits**. The 310-minute figure appears nowhere outside the pack and its test.
  - `docs/phase_2/window_runbook.md:138-142` — the budgeting table still reads "Start references | 3 …", "Midpoint reference | 1 …", "End references | 3 …" (= seven references), while the gamma pack plans nine (`planned_reference_bundles: 9`, three start + singles after members 20/40/60 + three end) precisely because of D-122's interior-reference augmentation (`generate_configs.py:1817-1826`), and `docs/paper/draft-v1.md:226` already states the nine-reference schedule. The operator-facing runbook is stale against the D-122 pack.
  - `grep -n "gamma\|GAMMA" docs/phase_2/window_runbook.md` → only :265, :791, :843, none carrying a duration.
- producer: none found — no operator packet/run card for the gamma window exists.
- transaction_relevant: **yes** — measurement-window operation; the operator has no document stating the ~5.2 h duration or the nine-reference cadence.

### D-122 · clause 7: prefill FLOOR cells ride alpha/beta
- clause (verbatim): "Prefill FLOOR cells continue to ride alpha/beta unchanged (D-117)."
- source: docs/decision_log.md:7928
- status: **A** (for "ride alpha/beta"); the word "unchanged" is superseded
- evidence:
  - `configs/campaigns/d117_floor_qwen25_1p5b_v3/generate_configs.py:52` — `PLAN_ID = "plan-d117-floor-qwen25-1p5b-decode-p128-prefill-rider-v3"`.
  - `.../d117_floor_qwen25_1p5b_v3/generate_configs.py:556-568` — stages `04_phase_prefill_p256_absolute`, `05/06_phase_prefill_p256_abba_blocks_*`; `:679-713` both `prefill_family_definition()` (p128) and `p256_family_definition()` (p256) exist.
  - `configs/campaigns/d117_floor_qwen25_7b_v3/generate_configs.py:397` — artifact cell `d117-qwen25-7b-prefill-p256-floor-v3`.
- producer: the alpha/beta floor pack generators.
- transaction_relevant: yes — floors feed the gamma consumption edge.
- note: "unchanged" no longer holds — D-139 (docs/decision_log.md:164) ruled a **dedicated p256 floor** and the alpha/beta packs now carry p256 floor cells in addition to the p128 rider. The clause's "ride alpha/beta" survives; its "unchanged" is superseded by D-139.

### D-122 · clause 8: the verdict refuses if the contrast lands below the bar
- clause (verbatim): "If the collected contrast lands below the decision bar, the verdict refuses per doctrine"
- source: docs/decision_log.md:7929-7930
- status: **A**
- evidence: `joulewise/analysis_engine/claims.py:104` and `:187` — `"effect_not_above_floor"` is a registered outcome-precedence refusal code, alongside `floor_cmp_missing`, `floor_transport_inapplicable`, `interpolation_bound_exceeds_floor`.
- producer: the analysis engine is itself the producer of the verdict.
- transaction_relevant: yes — claim edge.

### D-122 · clause 9: the marginality analysis publishes
- clause (verbatim): "and the marginality analysis publishes as prospective sizing evidence — never a quiet omission."
- source: docs/decision_log.md:7930-7931
- status: **A**
- evidence:
  - `docs/paper/draft-v1.md:399` — the sizing arithmetic is published in the body including the honest gap: "The current design file contains neither that fresh floor nor the claim-side bound, and the historical proportional projection is not an authorized current effect… the arithmetic is `TODO-EVIDENCE[…]`… If the contrast does not clear its gates, the protocol reports the refusal rather than omitting the arm."
  - `docs/paper/draft-v1.md:433` — the limitations section carries the same marginality statement ("An older short-prompt model-size diagnostic suggested marginal clearance … it was neither a fresh measurement nor an issued refusal. The fresh contrast can still be refused.").
- producer: `docs/paper/draft-v1.md`.
- transaction_relevant: yes — claim edge / publication.

### D-122 · clause 10: the D-117 "decode-only by default" clause is superseded
- clause (verbatim): "The D-117 clause \"contrast decode-only by default; 256-tok arm stays Ed's option\" is SUPERSEDED by this exercise of that option."
- source: docs/decision_log.md:7932-7933
- status: **C — NOT INSTALLED** (documentation clause)
- evidence: `docs/decision_log.md:142` — the D-117 index row still reads "contrast decode-only by default (≥256-token prefill arm stays Ed's open option)" with no superseded marker and no pointer to D-122. `grep -n "^### D-117" docs/decision_log.md` → only one amendment section, `:8710` "frozen readiness slots do not hash future arm bytes", unrelated.
- producer: the decision log itself.
- transaction_relevant: no — decision-log hygiene; a reader/generator author consulting D-117 alone would still read "decode-only".

---

## D-123 — reported-energy cells + signal-size doctrine + attribution debate

### D-123 · clause 1a: alpha/beta packs pre-register reported phase-energy means
- clause (verbatim): "The alpha/beta packs pre-register reader-facing phase-energy means alongside the floor cells — same 50 members, zero added collection"
- source: docs/decision_log.md:7941-7943
- status: **A**
- evidence:
  - `configs/campaigns/d117_floor_qwen25_1p5b_v3/generate_configs.py:1616` — `"reported_energy_cells": reported_cells,` in the emitted extraction spec; `:2102` the same in the second emission site.
  - `configs/campaigns/d117_floor_qwen25_1p5b_v3/generate_configs.py:2090-2099` — the p256 reported cell: `"reducer": "arithmetic_mean_over_fixed_member_universe.v1"`, `"expected_n": 50`, `"missing_or_invalid_member": "refuse_reported_mean"`, `"numeric_value": None`.
  - pack bytes on disk: `configs/campaigns/d117_floor_qwen25_1p5b_v3/calibration_plan.json:1177` and `configs/floor_mint/d117_qwen25_1p5b_v3_extraction_spec.json:1504`.
  - tests that would fail if removed: `tests/test_d117_floor_qwen25_1p5b_plan.py:1265-1273` (three cells, reducer, expected_n 50, member order equals physical order, `numeric_value is None`); `tests/test_d117_floor_qwen25_7b_plan.py:1384`.
- producer: the alpha/beta `generate_configs.py`.
- transaction_relevant: yes — alpha/beta pack bytes consumed by the floor mint.

### D-123 · clause 1b: conditional on the pack-gate check proving floor computation byte-identical
- clause (verbatim): "conditional on the pack-gate check proving the addition leaves every floor computation byte-identical."
- source: docs/decision_log.md:7943-7944
- status: **B — INSTALLED, NO PRODUCER-SIDE CHECK**
- evidence:
  - The producer *emits* the projection pin: `configs/campaigns/d117_floor_qwen25_1p5b_v3/generate_configs.py:1617-1623` — `"reported_energy_registration": {"authority": "D-123", "procedure_only": True, "floor_projection_sha256": canonical_sha256(cells), "no_semantics_change_rule": "Floor extraction consumes only cells; reported_energy_cells is a disjoint registered projection over the same physical bundle universe."}`.
  - The check exists only in the pack test: `tests/test_d117_floor_qwen25_1p5b_plan.py:1283-1292` `test_reporting_section_does_not_change_floor_output` — deletes `reported_energy_cells` + `reported_energy_registration` and asserts `validate_extraction_spec` output equality and `canonical_sha256(spec["cells"]) == spec["reported_energy_registration"]["floor_projection_sha256"]`.
  - **The "no callers" grep:** `grep -rn "floor_projection_sha256\|reported_energy_registration" --include="*.py" .` → only the six pack generators and the two pack test files. **No code in `joulewise/` or `scripts/` ever reads `floor_projection_sha256`.**
  - `joulewise/floor_extraction.py:979-1080` `validate_extraction_spec` never inspects `reported_energy_cells` or `reported_energy_registration` at all — it reads `schema_version` and `cells` only. So the mint neither validates the reported cells nor re-proves the byte-identity claim.
- producer: `scripts/mint_floor_artifact.py` / `scripts/mint_floor_artifact_generalized.py` consume the extraction spec; neither verifies the projection pin.
- transaction_relevant: **yes** — floor mint. The test asserts validator-output equality, not that the *minted floor bytes* are unchanged; the mint has no check at all.

### D-123 · clause 2: signal-size doctrine
- clause (verbatim): "future designs default to sized-up signals unless sizing destabilizes a proven design or breaks comparability with pinned claims."
- source: docs/decision_log.md:7948-7954
- status: NOT AN IMPLEMENTATION CLAUSE (standing design preference, no artifact demanded). Its one named exercise — the D-122 256-token arm — is covered above.
- transaction_relevant: no.

### D-123 · clause 3: attribution debate ordered and recorded
- clause (verbatim): "If the answer is \"no headroom beyond signal sizing,\" that is recorded and the question closes."
- source: docs/decision_log.md:7955-7959
- status: **A**
- evidence: `docs/process_traces/2026-08-08-attribution-debate/CONSULT-RESPONSE.md:1-20` — the record exists and closes the question in the ruled words: "For marginal phase-energy MEANS: signal sizing is the only in-scope lever… The question CLOSES for means." The sibling `COMMONMODE-REPLAY.md` is the evidence file D-124 cites, and `joulewise/detection_floor.py:125-127` pins that path as `_COMMON_MODE_EVIDENCE_REFERENCE`.
- producer: the process-trace directory.
- transaction_relevant: no — it is the record of a closed question; its ABBA-contrast half became D-124.

### D-123 · clause 4: overnight license
- source: docs/decision_log.md:7960-7963
- status: NOT AN IMPLEMENTATION CLAUSE (a spent authority grant).

---

## D-124 — common-mode contrast estimator (body 7966-8004)

### D-124 · clause 1: the TWO-SHARED-EDGE estimator is what is promoted
- clause (verbatim): "the TWO-SHARED-EDGE estimator (the replay's own soundness objection to the 1-D shared-shift form is sustained)"
- source: docs/decision_log.md:7981-7983
- status: **A**
- evidence: `joulewise/detection_floor.py:114` `COMMON_MODE_ESTIMATOR_ID = "d124_two_shared_edge_common_mode.v1"`; `:136-138` `"shared_parameters": ["onset_shift_s", "offset_shift_s"]` (two edges, not one).
- producer: `joulewise/floor_mint_estimator.py:497-546` — the mint's estimator path.
- transaction_relevant: yes — floor mint / claim edge.

### D-124 · clause 2: named estimator identity
- clause (verbatim): "named estimator identity"
- source: docs/decision_log.md:7989
- status: **A**
- evidence: `joulewise/detection_floor.py:483-490` `two_shared_edge_common_mode_registration()` returns `estimator_id`, `version`, `parameter_sha256`; `joulewise/floor_mint_estimator.py:278-283` refuses at the mint when the authenticated spec's registration is not byte-equal to the canonical one ("authenticated spec common-mode registration is not canonical").
- producer: `scripts/mint_floor_artifact_generalized.py:58` imports `floor_mint_estimator`; `scripts/mint_floor_artifact.py:59` likewise.
- transaction_relevant: yes.

### D-124 · clause 3: named stationarity/transfer assumption WITH evidence and its honest limit, carried into the paper's limitations
- clause (verbatim): "named block-timescale stationarity/transfer assumption WITH the bracket-calibration evidence (onset/offset spans) and its honest limit (the historical corpus records bounds, not realized member-level errors) carried into the paper's limitations"
- source: docs/decision_log.md:7990-7993
- status: **A**
- evidence:
  - `joulewise/detection_floor.py:500-512` — `stationarity_transfer_assumption` with `assumption_id "d124_block_timescale_shared_edges_stationarity_transfer_v1"`, `evidence_reference` = COMMONMODE-REPLAY.md, `evidentiary_limit` = "The historical corpus records bounds, not realized member-level boundary errors."
  - test that would fail if removed: `tests/test_detection_floor.py:1213-1218` asserts both the evidence reference and the exact limit wording.
  - paper: `docs/paper/draft-v1.md:453` — "…Exact-arithmetic tests found no understatement in 4,096 generated cases, but that validates the calculation, not the physical premise: calibration bounds possible errors and does not observe each run's realized error. Every result using shared errors must therefore disclose the block-timescale sharing assumption."
- producer: `detection_floor.two_shared_edge_common_mode_registration` + paper §7.
- transaction_relevant: yes.

### D-124 · clause 4: pre-registration in the D-117 pack bytes before any claim-bearing data
- clause (verbatim): "pre-registration before any claim-bearing data" / "its identity is pre-registered in the D-117 pack bytes"
- source: docs/decision_log.md:7985 and 7993
- status: **A**
- evidence:
  - `configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/calibration_plan.json:117` and `:528` — `"parameter_sha256": "dd61d38811ddadb2aecb8df4a533b715c8ca74bb031896d09688c9b76b69ed38"` on both contrast cells; same value in all three `_v1/_v2/_v3` gamma packs and in every `configs/floor_mint/*_extraction_spec.json` (`:205, :704, :1203`).
  - live code agrees: `python3 -c "from joulewise.detection_floor import COMMON_MODE_PARAMETER_SHA256; print(...)"` → `dd61d38811ddadb2aecb8df4a533b715c8ca74bb031896d09688c9b76b69ed38`.
  - producer refusal: `joulewise/floor_mint_estimator.py:79-92` `_assert_common_mode_contract()` raises if `detection_floor.COMMON_MODE_PARAMETER_SHA256` differs from the mint-reviewed pin; `:268-276` refuses a `pending` registration outright.
- producer: gamma/alpha/beta `generate_configs.py` (which call `two_shared_edge_common_mode_registration()` directly) + the mint.
- transaction_relevant: yes.

### D-124 · clause 5: identical covariance treatment on calibration floor blocks and the consuming contrast
- clause (verbatim): "identical covariance treatment on calibration floor blocks and the consuming science contrast"
- source: docs/decision_log.md:7994-7995
- status: **A**
- evidence: `joulewise/detection_floor.py:515-518` — `covariance_treatment`, `calibration_treatment`, `consuming_contrast_treatment` are all bound to the single constant `_COMMON_MODE_COVARIANCE_TREATMENT` (`:128-130`), plus `"identical_covariance_treatment_required": True`; `:530-536` `validate_common_mode_estimator_registration` accepts only a mapping byte-equal to that dict, and the mint calls it at `joulewise/floor_mint_estimator.py:278`.
- producer: the mint.
- transaction_relevant: yes.

### D-124 · clause 6: D-102 never-zero allowance applied exactly once inside the shared operative bound
- clause (verbatim): "D-102 never-zero allowance applied exactly once inside the shared operative bound"
- source: docs/decision_log.md:7995-7996
- status: **A**
- evidence: `joulewise/detection_floor.py:575-600` `registered_common_mode_operative_bound()` — docstring "Recover the shared bound only when D-102 was embedded exactly once. … A missing, zero, duplicated, or differently embedded allowance is a typed refusal; callers may not silently substitute the independent-member estimator", refusal code `common_mode_allowance_application_invalid` (`:117`, `:585`). Registration records `"allowance": {"rule": …, "embedding_count": 1, "embedded_in": "shared_operative_bound_s"}` at `:519-523`.
- producer: `joulewise/floor_mint_estimator.py:507` calls `detection_floor.registered_common_mode_operative_bound(bracket)` on the mint path.
- transaction_relevant: yes.

### D-124 · clause 7: issued acceptance artifact not reopened, no raw calibration corpus voided
- clause (verbatim): "the issued acceptance artifact is not reopened and no raw calibration corpus is voided"
- source: docs/decision_log.md:7997-7998
- status: **B — INSTALLED, NO PRODUCER-SIDE CHECK**
- evidence: `joulewise/detection_floor.py:524-525` — `"issued_acceptance_artifact_reopened": False, "raw_calibration_corpus_voided": False` are declared *flags* inside the registration dict and are enforced only through whole-dict equality (`:530-536`). They are assertions about history, not checks on any writer; nothing computes them.
- producer: none — this is a self-declared property.
- transaction_relevant: yes (calibration custody), but the clause is historically satisfied: the six acceptance editions `configs/calibration/calibration_acceptance_d079_v2{,_r2,_n17_r3..r6}.json` are all retained (`joulewise/calibration_bracketing.py:130-170`).

### D-124 · clause 8: fallback to the worst-case default if the unit or pre-registration fails
- clause (verbatim): "if either fails, contrasts fall back to the worst-case default and the paper says so."
- source: docs/decision_log.md:7986-7987
- status: **A**
- evidence: `joulewise/floor_mint_estimator.py:257-262` — an absent estimator or `detection_floor.METHOD_ID` selects `_DEFAULT_PATH`, and a registration present on the default path is a hard refusal ("common-mode registration cannot authorize the default estimator path"); `:263-267` any other estimator id refuses ("unsupported authenticated spec estimator"). Paper: `docs/paper/draft-v1.md:223` — "The comparative calculation fixed for the current floor cells is the conservative composition above… Section 7 defines the narrower calculation…".
- producer: the mint's `_select_estimator_path`.
- transaction_relevant: yes.

### D-124 · clause 9 (Sequencing): the implementing unit lands BEFORE pack freeze; the packs name the estimator identity
- clause (verbatim): "the implementing unit rides AFTER the trust branch merges (shared floor_extraction/estimator surface) and BEFORE pack freeze (the packs name the estimator identity)."
- source: docs/decision_log.md:8000-8002
- status: **A**
- evidence: same pack bytes as clause 4 — `configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/calibration_plan.json:117,528` carry `floor_estimator_registration` including `estimator_id`/`parameter_sha256`, and the packs' freeze receipts are minted (`configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/arm_readiness.freeze.receipts/`).
- transaction_relevant: yes.

### D-124 · clause 10: FLOOR-COMMONMODE-01's kernel row sharpens to this form
- clause (verbatim): "FLOOR-COMMONMODE-01's kernel row sharpens to this form."
- source: docs/decision_log.md:8002-8003
- status: **A** (work item completed and closed)
- evidence: `TASK_QUEUE.md:129` and `:227` record `WO-MINT-ESTIMATOR-VOCAB — COMPLETED (e11b1ad, 2026-08-12)` as the D-133 cl.4 prerequisite for the estimator lane; `RUN_STATE.md:1638` — "#140 WO-MINT-ESTIMATOR-VOCAB — gate COMPLETE".
- transaction_relevant: yes.

---

## D-124 amendment — 2026-08-10: strict-noncollapse domain (8005-8059)

### D-124-A1 · clause 1: exact on a registered strict-noncollapse domain, refuses outside it
- clause (verbatim): "the estimator is **exact on a registered strict-noncollapse domain and refuses outside it**."
- source: docs/decision_log.md:8012-8014
- status: **D — SUPERSEDED (in its "exact" wording), mechanism A**
- evidence: the amendment's own Erratum at docs/decision_log.md:8078-8082 states the sentence "exact on the registered strict-noncollapse domain" was "incorrect as written — falsified by the round-2 audit", and the FCM-R4 amendment (docs/decision_log.md:8060-8072) supersedes the unconditional upper-bound sentences again. The *domain-refusal mechanism* is installed: `joulewise/detection_floor.py:550-565` `_common_mode_window_is_strictly_noncollapsed`.
- note: superseder = the FCM-R4 amendment, `docs/decision_log.md:8060-8111`, and the ALT-D120 completion at `docs/decision_log.md:8351-8371`.

### D-124-A1 · clause 2: outward-rounded noncollapse proof for every admitted A1/B1/B2/A2 window
- clause (verbatim): "Every admitted A1/B1/B2/A2 member window must prove, with outward float rounding (`nextafter(start+B) < nextafter(end-B)`), that no joint shift within the authenticated bound B can collapse it"
- source: docs/decision_log.md:8014-8018
- status: **A**
- evidence: `joulewise/detection_floor.py:550-565` — `latest_start = math.nextafter(start + bound, math.inf)`, `earliest_end = math.nextafter(end - bound, -math.inf)`, `return latest_start < earliest_end`; non-finite or non-positive bound returns False (refuse). Test: `tests/test_detection_floor.py:1240-1244` `test_window_domain_thresholds_and_all_abba_positions` exercises the exact `2.0 * bound` threshold and its `nextafter` neighbours.
- producer: `joulewise/floor_extraction.py:500-620` (block-input builder) → `joulewise/floor_mint_estimator.py:538-546` on the mint path.
- transaction_relevant: yes.

### D-124-A1 · clause 3: typed refusal `common_mode_nonseparable_window_domain`, never estimated, no silent fallback
- clause (verbatim): "geometry outside the domain refuses with the typed reason `common_mode_nonseparable_window_domain` and is never estimated (no silent fallback — a cell not registered for this estimator uses the worst-case composition and says so)."
- source: docs/decision_log.md:8018-8022
- status: **A**
- evidence: `joulewise/detection_floor.py:118` registers the code in `COMMON_MODE_REFUSAL_CODES`; `joulewise/floor_extraction.py:211` registers it in the cell refusal vocabulary; `tests/test_detection_floor.py:1236-1238` asserts it is in BOTH `COMMON_MODE_REFUSAL_CODES` and `CELL_REFUSAL_CODES`. No-silent-fallback dispatch: `joulewise/floor_mint_estimator.py:257-267` (see D-124 clause 8). Paper discloses it: `docs/paper/draft-v1.md:453` "It refuses a block with nonseparable windows or any geometry outside that domain."
- producer: the mint's estimator dispatch.
- transaction_relevant: yes.

### D-124-A1 · clause 4: registered parameter dict pins the rule/precondition/refusal reason; the hash rotates; old registrations fail validation
- clause (verbatim): "The registered parameter dict now pins `shared_extrema_rule = separable_onset_offset_exact_sweep_on_strict_noncollapse_domain`, the domain precondition, and the refusal reason, so `COMMON_MODE_PARAMETER_SHA256` CHANGES and the previous registration object fails validation"
- source: docs/decision_log.md:8027-8034
- status: **D — SUPERSEDED** for the pinned literal value; **A** for the mechanism
- evidence:
  - the literal value ruled here is NOT what the code pins: `joulewise/detection_floor.py:140-143` now pins `"shared_extrema_rule": "separable_onset_offset_excursion_composition_about_swept_zero_point_on_strict_noncollapse_domain"` — changed by the FCM-R4 round.
  - the precondition and refusal reason ARE pinned as ruled: `joulewise/detection_floor.py:154-160` `"shared_extrema_domain_precondition": "all_admitted_abba_member_windows_outward_rounding_prove_start_plus_bound_lt_end_minus_bound"`, `"shared_extrema_domain_refusal_reason": "common_mode_nonseparable_window_domain"`.
  - the rotation/rejection mechanism is installed and tested: `tests/test_detection_floor.py:1220-1234` `test_superseded_full_registrations_are_rejected` rejects six superseded hashes.
- note: superseder = the FCM-R4 amendment (`docs/decision_log.md:8060-8111`) and the ALT-D120 completion (`docs/decision_log.md:8351-8371`).

### D-124-A1 · clause 5: outward numerical enclosure on composed extrema
- clause (verbatim): "Composed extrema carry an outward numerical enclosure so float summation direction cannot reopen an understatement route"
- source: docs/decision_log.md:8022-8024
- status: **A** (as re-scaled by the erratum)
- evidence: `joulewise/detection_floor.py:567-572` `_common_mode_outward` (four-ULP outward walk); `joulewise/detection_floor.py:161-163` pins `"shared_extrema_numerical_enclosure_rule": "outward_enclosure_64u_times_floored_member_envelope_integral_sum"`; `joulewise/floor_extraction.py:451-485` composes about the zero point with `abs(zero_point)` in the floored scale set and `math.fsum((zero_centred_width, abs(zero_point - delta)))`.
- note: the erratum (docs/decision_log.md:8083-8091) records that the FIRST implementation (bbf7bdd) scaled the enclosure to the contrast magnitude and was defective; the current member-envelope scaling is what is installed.
- transaction_relevant: yes.

### D-124-A1 · clause 6: claim-path geometry margins are a freeze-gate checklist item checked at collection
- clause (verbatim): "Q8 p256 evidence will be checked at collection, not inferred" / erratum: "margins are a freeze-gate checklist item at collection."
- source: docs/decision_log.md:8035-8038 and 8107-8111
- status: **A** (mechanism installed; recording, not refusing)
- evidence:
  - `joulewise/window_duration_margins.py` exists; `scripts/record_window_duration_margins.py` exists; `tests/test_window_duration_margins.py:219, 431, 680, 729, 807, 890, 1003` exercise derive/record/validate/render.
  - the operative runbook carries it as a numbered step: `docs/phase_2/window_runbook.md:1878-1900` "## 11. Record duration margins, back up, then extract in the same custody session" invoking `scripts/record_window_duration_margins.py`, and `:1978` requires "the comparative-cell window-duration-margin receipt path and SHA-256" in the close-out record.
  - the three ruled additions are written down at `docs/strategy/2026-08-09-pack-freeze-plan.md:129-138` (record each cell's minimum margin at collection; re-evaluate p128 prefill estimator selection at regeneration; run the same margin math for the Q8 p256 cells).
- producer: `scripts/record_window_duration_margins.py`, run by the operator at close-out.
- transaction_relevant: yes — measurement window / claim edge.
- note: addition (2) — "at pack regeneration, evaluate whether the p128 prefill cells should select the worst-case default estimator instead of D-124 given the margin (a magistrate/Ed call at freeze, not now)" — is an open Ed/magistrate gate with no code and no checklist row in an operator-facing document; it lives only in the strategy doc.

### D-124-A1 · clause 7: the paper's limitations carry the applicability limit
- clause (verbatim): "The paper's limitations carry the applicability limit."
- source: docs/decision_log.md:8038-8039
- status: **A**
- evidence: `docs/paper/draft-v1.md:453` (full paragraph "When timing errors may be shared within a block…"), with its evidence pointer at `:454` → `configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/arm_readiness.evidence/evidence-estimator-identity.json`. Fill-registry guard: `docs/paper/results-fill-registry.md:278` — `STOP_FILL if the estimator registration is absent, names a different estimator, or the cell refused with common_mode_nonseparable_window_domain`.
- transaction_relevant: yes — claim edge.

---

## D-124 amendment — 2026-08-10: FCM-R4 zero point, third erratum, tolerance audit (8060-8111)

### D-124-A2 · clause 1: `z` is an explicit registered input, present by exact equality in both sweeps
- clause (verbatim): "Round 4 makes the zero-shift contrast `z` an explicit registered input. It must be present by exact equality in both onset and offset sweeps."
- source: docs/decision_log.md:8072-8074
- status: **A**
- evidence: `joulewise/floor_extraction.py:323-329` — `zero_point = contrast(0.0, 0.0)` is carried structurally, and each sweep reuses it at `shift_s == 0.0`; `joulewise/floor_extraction.py:577` — `if zero_point not in onset or zero_point not in offset:` refuses. Registration pins the structural rule at `joulewise/detection_floor.py:144-149` `"shared_extrema_zero_point_rule": "zero_point_is_carried_structurally_by_the_registered_builder_as_the_shift_zero_index_never_supplied_or_matched_by_value_and_direct_keyword_inputs_are_unregistered"`.
- producer: `joulewise/floor_mint_estimator.py:538-546` (mint path calls the registered builder).
- transaction_relevant: yes.

### D-124-A2 · clause 2: extrema composed about z; `|z - delta|` added outward exactly once, separate from the `64u * S_env` pad whose floored scale set includes `|z|`
- clause (verbatim): "Extrema are composed as signed excursions about `z`; the emitted shared half-width adds `|z - delta|` outward exactly once, separately from the unchanged `64u * S_env` member-envelope pad, whose floored scale set now includes `|z|`."
- source: docs/decision_log.md:8074-8078
- status: **A**
- evidence: `joulewise/floor_extraction.py:451-485` — signature takes `zero_point`; `:461` includes `abs(zero_point)` in the floored scale set; `:467-470` compose min/max excursions as `(min(onset), -zero_point, min(offset), -zero_point)` / `(max(...), -zero_point, ...)`; `:485` `math.fsum((zero_centred_width, abs(zero_point - delta)))` — added exactly once. Registration pins it: `joulewise/detection_floor.py:150-153` `"shared_extrema_centre_offset_rule": "abs_zero_point_minus_block_delta_added_outward_exactly_once_separate_from_the_numerical_enclosure"`.
- transaction_relevant: yes.

### D-124-A2 · clause 3: divergence outside the isclose band refuses with `common_mode_zero_point_divergence_out_of_domain`
- clause (verbatim): "A mismatch outside the existing `isclose(rel_tol=1e-9, abs_tol=1e-12)` band refuses with `common_mode_zero_point_divergence_out_of_domain`; this is a pure provenance guard and is not load-bearing for soundness."
- source: docs/decision_log.md:8078-8081
- status: **A**
- evidence: `joulewise/detection_floor.py:120` registers the code; `joulewise/floor_extraction.py:211` registers it in the cell vocabulary; `joulewise/floor_extraction.py:602-608` raises it. Registration pins the reason at `joulewise/detection_floor.py:164-166`.
- transaction_relevant: yes.

### D-124-A2 · clause 4: the round-3 candidate is a named negative regression
- clause (verbatim): "The intuitive round-3 arithmetic plus `|z-delta|` candidate was tried and refuted: it fails the independent about-zero exact bar on FCM-R3-01 and remains a named negative regression."
- source: docs/decision_log.md:8081-8085
- status: **A**
- evidence: `tests/test_r4_acceptance_oracle.py:17` — module docstring "committed as a named negative regression"; `:361-385` `test_fcm_r3_01_counterexample_is_covered` — "The exact FCM-R3-01 case must now be covered on both bars… `|delta - zero|` added once -- FAILS BAR 1 on the FCM-R3-01 case".
- transaction_relevant: yes — soundness regression on the mint arithmetic.

### D-124-A2 · clause 5: real trimmed recompute fixtures committed under the 256 KB cap
- clause (verbatim): "Real trimmed recompute fixtures for a5 decode blocks b02 (nonzero measured divergence) and b01 (zero divergence) are committed under `tests/fixtures/fcm_r4_real_blocks/` within the 256 KB cap."
- source: docs/decision_log.md:8085-8088
- status: **A**
- evidence: `ls tests/fixtures/fcm_r4_real_blocks/` → `measured_pair.json`, `PROVENANCE.md`, and the eight bundle dirs `p2015-df-cmp-abba-ph-decode-b01-{a1,a2,b1,b2}` and `-b02-{a1,a2,b1,b2}`. `du -sk` → 188 KB, under the 256 KB cap.
- transaction_relevant: no — test fixtures.

### D-124-A2 · clause 6: the registered parameter hash is `4d1c544f…`; superseded hashes are rejected by regression
- clause (verbatim): "The registered parameter hash is `4d1c544fe3a52148c7d379f4c50ade4ac3b64211d817cd1438a2365973291981`. All superseded hashes (`ea4aa669...`, `9d964cfb...`, and `977189cd...`) are rejected by regression."
- source: docs/decision_log.md:8089-8093
- status: **D** for the pinned value; **A** for the rejection mechanism
- evidence: the live hash is `dd61d38811ddadb2aecb8df4a533b715c8ca74bb031896d09688c9b76b69ed38` (computed from `joulewise.detection_floor.COMMON_MODE_PARAMETER_SHA256`, definition at `joulewise/detection_floor.py:178-186`). `4d1c544f…` is itself now in the rejected set: `tests/test_detection_floor.py:1220-1234` rejects all six of `ea4aa669…`, `9d964cfb…`, `977189cd…`, `4d1c544f…`, `973c9bfc…`, `dea20dc0…`.
- note: superseder = the ALT-D120 completion amendment (rounds 5-10), `docs/decision_log.md:8351-8371`.

### D-124-A2 · clause 7: the four input-surface tolerance acceptances and their single-sourcing assumptions
- clause (verbatim): "These are the complete tolerance acceptances on the registered arithmetic path. The production caller single-sourcing statements are assumptions of the upper-bound claim; direct callers must preserve them." (table rows: sweep bound vs bracket bound `rel=0, abs=1e-12 s`; `b_fiducial_s` vs `operative_b_fiducial_s` alias; recorded allowance string vs passed `calibration_drift_allowance_s`; operative bound vs endpoint plus allowance)
- source: docs/decision_log.md:8095-8104
- status: **A** for the single-sourcing statement about `extract_comparative_cell`
- evidence: `joulewise/floor_mint_estimator.py:507` — `detection_floor.registered_common_mode_operative_bound(bracket)` is called ONCE and its float is passed onward to the sweep builder (`:538`) and estimator (`:545`); `joulewise/detection_floor.py:575-600` is the single authority that reconstructs the bound and refuses a missing/zero/duplicated/differently-embedded allowance (`common_mode_allowance_application_invalid`).
- transaction_relevant: yes — floor mint arithmetic.
- note: the table's *dispositions* ("No discrepancy term: production is exactly single-sourced") are assumption statements about callers, not machine checks; a future direct caller that re-derives the bound independently would silently break the upper-bound claim. Nothing prevents that.

### D-124-A2 · clause 8: no published replay number changes; the value remains 1.869502 J
- clause (verbatim): "No published replay number changes; the six-decimal value remains `1.869502 J`."
- source: docs/decision_log.md:8109-8111
- status: **A**
- evidence: `docs/paper/draft-v1.md:453` — "No current comparative result is issued, so no magnitude from the older replay appears here." The number is not published in the paper at all, so the clause holds vacuously and correctly.
- transaction_relevant: yes — claim edge.

---

## D-124 relicense — 2026-08-11 (8331-8350)

### D-124-R · clause 1: the pre-committed stopping rule
- clause (verbatim): "**Pre-committed stopping rule (binding, no further deliberation): if the repair round's delta re-audit finds ANY exact-arithmetic understatement at an admitted input — any mechanism, any magnitude — the unit drops to the worst-case default estimator (freeze-plan Q7 reversed, both floor packs' comparative cells re-specced to METHOD_ID) without another round.**"
- source: docs/decision_log.md:8341-8348
- status: **D — SUPERSEDED (fired and then lifted)**
- evidence: the ALT-D120 completion amendment at `docs/decision_log.md:8353-8356` — "Round 5 (structural registered-input record) fired the stopping rule below; D-132 revived the work and the D-133 cold gate ruled ALT-D120". Superseders: D-132 (`docs/decision_log.md:157`) and D-133 (`docs/decision_log.md:158`).
- note: the counterfactual it protected is not installed anywhere as a mechanism — nothing in code would re-spec both floor packs' comparative cells to `METHOD_ID`. That is correct, since the rule was spent and reversed by D-132/D-133; the packs today name the D-124 estimator (see D-124 clause 4).
- transaction_relevant: yes (it governed the estimator that mints the comparative floors), but spent.

### D-124-R · clause 2: the refuter-authored acceptance oracle may be amended only by its author
- clause (verbatim): "the refuter-authored acceptance oracle may be amended only by its author."
- source: docs/decision_log.md:8349-8350
- status: **C — NOT INSTALLED** (as a mechanical check)
- evidence: `tests/test_r4_acceptance_oracle.py` exists and is the oracle, but nothing in the repo enforces authorship: no CODEOWNERS entry (`ls .github/CODEOWNERS` — absent), no test asserting the oracle file's SHA. The council-log record `docs/council_log.md:3367` says the oracle was "committed at `ed8715b` before implementation, the implementer forbidden to edit it, byte-verified untouched by the delta auditor" — a one-time human verification, not a standing check.
- producer: none.
- transaction_relevant: no — a process control on the review lane, not on transaction bytes.

---

## D-124 amendment — 2026-08-11: FCM-01 ALT-D120 completion (8351-8371)

### D-124-A3 · clause 1: the public registered surface deleted
- clause (verbatim): "the public registered surface deleted (round 6-7)"
- source: docs/decision_log.md:8360-8361
- status: **A**
- evidence: `joulewise/detection_floor.py:167-172` pins `"registered_result_provenance_rule": "registration_is_declared_only_in_the_committed_preregistered_extraction_spec_no_admitted_report_or_artifact_vocabulary_represents_a_registered_result"`, and `tests/test_detection_floor.py:1205-1212` asserts that exact string. The registration survives only as pre-registration in committed spec bytes (see D-124 clause 4).
- transaction_relevant: yes.

### D-124-A3 · clause 2: total recursive vocabulary refusal + strict duplicate-key JSON parsing at every admitted-byte entry
- clause (verbatim): "total recursive vocabulary refusal + strict duplicate-key JSON parsing at every admitted-byte entry (round 8)"
- source: docs/decision_log.md:8361-8363
- status: **A**
- evidence: `joulewise/authentication_io.py:138-144` `_duplicate_key` raises `v2_authentication_duplicate_json_key`; `:175-190` `_reserved_vocabulary_path` recurses through mappings and lists; `:196-215` refuses unless `allow_governed_spec_vocabulary`; `:201-204` wires `object_pairs_hook=_duplicate_key`, `parse_constant=_nonfinite_number`, `parse_float=_finite_float`, `parse_int=_finite_int`. Sibling duplicate-key guards: `joulewise/analysis_manifest_v3.py:1304`, `joulewise/calibration_bracketing.py:712`, `joulewise/calibration_ledger.py:1899`.
- producer: every admitted-byte load path.
- transaction_relevant: yes.

### D-124-A3 · clause 3: complete finite-number policy (overflow-to-inf)
- clause (verbatim): "complete finite-number policy (overflow-to-inf) plus the last two census-miscovered parsers (round 10, ACCEPTED clean by its delta — no findings)"
- source: docs/decision_log.md:8364-8366
- status: **A**
- evidence: `joulewise/authentication_io.py:155-170` — `if not math.isfinite(parsed):` refuse, and `finite_projection = math.isfinite(float(parsed))` catches integers that overflow to `inf` on projection; wired at `:202-204`.
- transaction_relevant: yes.

### D-124-A3 · clause 4: the O3 delta cleared the relocated arithmetic terminally
- clause (verbatim): "The O3 full delta cleared the relocated arithmetic TERMINALLY: zero exact understatements in 4,096 independent rational-arithmetic cases plus a 1,536-case differential."
- source: docs/decision_log.md:8366-8368
- status: **A** (published as the paper's stated evidence)
- evidence: `docs/paper/draft-v1.md:453` — "Exact-arithmetic tests found no understatement in \(4{,}096\) generated cases, but that validates the calculation, not the physical premise". `tests/test_r4_acceptance_oracle.py` is the committed oracle.
- transaction_relevant: yes.

### D-124-A3 · clause 5: consumption of the tighter floor gates on WO-MINT-ESTIMATOR-VOCAB
- clause (verbatim): "Consumption of the tighter floor still gates on WO-MINT-ESTIMATOR-VOCAB (D-133 cl.4)."
- source: docs/decision_log.md:8369-8370
- status: **A** (gate satisfied)
- evidence: `TASK_QUEUE.md:129` — "Merged via #140 (`e11b1ad`): shared estimator dispatcher and full mint-site authentication/equality coverage landed, satisfying the D-133 clause 4 prerequisite"; `TASK_QUEUE.md:227` "## WO-MINT-ESTIMATOR-VOCAB — COMPLETED (`e11b1ad`, 2026-08-12…)"; `RUN_STATE.md:1638` "gate COMPLETE"; `docs/decision_log.md:8927` "D-133 clause 4 conditional: EXECUTE. PR #140".
- producer: `joulewise/floor_mint_estimator.py` dispatch at all three mint sites.
- transaction_relevant: yes.

---

## D-125 — Ed's morning ratification batch (8112-8137)

### D-125 · clause 1: FLOOR-COMMONMODE-01 lands through the full gate BEFORE pack freeze so the estimator identity pre-registers in pack bytes
- clause (verbatim): "FLOOR-COMMONMODE-01's implementation must land through the full gate BEFORE pack freeze so the estimator identity pre-registers in pack bytes."
- source: docs/decision_log.md:8119-8121
- status: **A**
- evidence: `configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/calibration_plan.json:117,528` carry the full `floor_estimator_registration` with `parameter_sha256 dd61d388…`, matching live code; the same pin is in all six `configs/floor_mint/*_extraction_spec.json` at `:205,:704,:1203`. Producer-side refusal on drift: `joulewise/floor_mint_estimator.py:79-92` and `:277-283`. Freeze receipts exist under each pack's `arm_readiness.freeze.receipts/`.
- producer: pack generators + the mint.
- transaction_relevant: yes.

### D-125 · clause 2a: screens/ceilings become lineage-monotone t-family envelopes with the genesis screen as a lower bound
- clause (verbatim): "screens/ceilings become lineage-monotone t-family envelopes inheriting the genesis screen 0.010818 as a lower bound — the allowance can only strengthen."
- source: docs/decision_log.md:8125-8127
- status: **C — NOT INSTALLED**
- evidence (what I looked at):
  - `grep -rn "envelope" --include="*.py" joulewise/calibration_bracketing.py joulewise/calibration_ledger.py` → **no hits**. There is no envelope, no monotonicity comparison, and no `max(screen, genesis)` anywhere.
  - What exists instead is a flat per-generation registry: `joulewise/calibration_bracketing.py:193-224` `_D102_N19_DERIVATION` (`"bracket_screen_s": "0.010818"`) and `_D102_N17_DERIVATION` (`:211 "bracket_screen_s": "0.009724"`); `:231-266` `acceptance_generation_operatives()` returns the generation's registered dict verbatim (it refuses a *crosswire* — a supplied value disagreeing with the registered one — but never compares generations); `:269-279` `acceptance_bracket_screen_s()` returns it unchanged; `:281-290` `acceptance_allowance_rule()` renders `max(observed_drift_s,{screen})`.
  - **The live generation's screen is BELOW the ruled genesis lower bound:** `joulewise/calibration_bracketing.py:172-173` — `ACTIVE_ACCEPTANCE_ID = ANCHOR_V3_R6_ACCEPTANCE_ID` ("the LIVE surface: what production loads when no artifact is named"), and `:225-227` maps r5/r6 to `_D102_N17_DERIVATION`, i.e. `0.009724 < 0.010818`.
- producer: `joulewise/calibration_bracketing.py` — the module that resolves the never-zero allowance the mint embeds in every operative bound.
- transaction_relevant: **yes** — the bracket screen is the D-102 never-zero allowance floor inside `registered_common_mode_operative_bound`, so it sets every comparative floor the `_v4` mint issues.
- note: this is NOT a clean D. The mechanism that replaced it was ruled by D-145 (`docs/decision_log.md:168`, "r3 = `d079_calibration_acceptance_v2_n17_r3` (n=17, screens TIGHTENED)") and D-147 (`docs/decision_log.md:170`, mint-lane fan-out: generation-indexed mint-policy resolver), whose design record states the conflict explicitly — `docs/process_traces/2026-08-19-r1-r2-codesign/05-r2-design-terra.md:31` "The static 0.010818 checks conflict with r4's n=17 derivation. Route screen and rule through the supplied authenticated acceptance", `:184` "n19/r2 accepts `0.010818`; n17/r4 accepts `0.009724`; every cross-generation mismatch refuses", `:196` "Flat `0.010818 → 0.009724` migration: rejected." — and `docs/process_traces/2026-08-19-r1-r2-codesign/14-r2-ruling.md:57-61` orders a guard test forbidding the literals in kernel sources, implemented at `tests/test_mint_policy_resolver_guard.py:24-25` (`assertNotIn("0.010818", source)` / `assertNotIn("0.009724", source)` over every `joulewise/` and `scripts/` file except the policy registry). So a *different* mechanism was deliberately installed, but **no decision states that D-125's "the allowance can only strengthen" / genesis-lower-bound rule is vacated**, and in effect the live successor screen is 10% weaker than the ruled floor. Recorded as C rather than D so the magistrate rules on it.
- I checked and did NOT find: any `min`/`max` against a genesis constant in `joulewise/calibration_bracketing.py`, `joulewise/calibration_ledger.py`, `joulewise/detection_floor.py`, `joulewise/floor_mint_estimator.py`, `scripts/mint_floor_artifact*.py`; any monotonicity assertion in `tests/` (`grep -rn "0.010818"` in tests returns only n19-era fixture literals, e.g. `tests/test_d117_v3_family.py:27` `N19_ALLOWANCE_RULE = "max(observed_drift_s,0.010818)"`).

### D-125 · clause 2b: D-117 clause 1 is AMENDED for successor artifacts
- clause (verbatim): "**D-117 clause 1 is AMENDED for successor artifacts** from \"every mint uses max(drift, 0.010818)\" to \"genesis lower bound + lineage-envelope rule\""
- source: docs/decision_log.md:8128-8130
- status: **C — NOT INSTALLED** (documentation clause)
- evidence: `docs/decision_log.md:7686-7688` — D-117's body still reads, unamended, "the never-zero `A_s = max(observed_drift_s, 0.010818)` allowance (D-102 pin 3) BINDS every mint under this entry." `grep -n "^### D-117" docs/decision_log.md` → the only amendment section is `:8710` "frozen readiness slots do not hash future arm bytes", which is unrelated. Neither D-117's body nor its index row (`:142`) carries the D-125 amendment or a pointer to it.
- producer: the decision log.
- transaction_relevant: **yes** — a reader (or a generator author) consulting D-117 for the mint rule reads the superseded literal, and the live code disagrees with it (clause 2a).

### D-125 · clause 2c: the genesis literal remains binding for every mint under the issued artifact
- clause (verbatim): "the genesis literal remains binding as the floor and for every mint under the issued artifact."
- source: docs/decision_log.md:8130-8132
- status: **A** for "for every mint under the issued [n=19] artifact"; **C** for "as the floor" across successors (same evidence as clause 2a)
- evidence: `joulewise/calibration_bracketing.py:62` `PREDECESSOR_ACCEPTANCE_ID = "d079_calibration_acceptance_v2_n19"` and `:74` `SUCCESSOR_ACCEPTANCE_ID = "…_n19_r2"` both resolve through `_D102_GENERATION_DERIVATIONS` to `_D102_N19_DERIVATION` with `bracket_screen_s "0.010818"` (`:199`), and `acceptance_generation_operatives` (`:255-265`) raises on any supplied value disagreeing with the registered one. Tests pin it: `tests/test_d117_floor_qwen25_1p5b_plan.py:1408,1434-1436`.
- producer: `joulewise/calibration_bracketing.py` + the mint.
- transaction_relevant: yes.

### D-125 · clause 3: the 40-hour window plan of record
- clause (verbatim): "The plan of record is `docs/strategy/2026-08-08-40h-plan.md`; RUN_STATE points to it as the resume script across /clear."
- source: docs/decision_log.md:8134-8136
- status: **A**
- evidence: `docs/strategy/2026-08-08-40h-plan.md` exists (8133 bytes); `RUN_STATE.md:1785` — "**THE PLAN OF RECORD IS `docs/strategy/2026-08-08-40h-plan.md` — read…".
- producer: RUN_STATE.md.
- transaction_relevant: no — a spent scheduling window.

---

## Counts

| status | count |
|---|---|
| A | 27 |
| B | 4 |
| C | 5 |
| D | 4 |
| not an implementation clause | 2 |

Transaction-relevant B: D-122 cl.1 (prospectively frozen), D-122 cl.3 (frozen
prompt), D-123 cl.1b (pack-gate byte-identity check), D-124 cl.7 (issued
artifact untouched — self-declared flag).
Transaction-relevant C: D-122 cl.6 (operator packet duration), D-125 cl.2a
(lineage envelope / genesis lower bound), D-125 cl.2b (D-117 cl.1 amendment
never written into D-117), D-125 cl.2c-successor-half.
Non-transaction C: D-122 cl.10 (D-117 index row never marked superseded),
D-124-R cl.2 (oracle authorship control).
