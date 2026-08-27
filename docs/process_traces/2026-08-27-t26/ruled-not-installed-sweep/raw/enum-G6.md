# G6 — D-142 .. D-149 "ruled but never installed" enumeration

Repo read-only at `/Users/edr/code/JouleWise`, branch `main`.
Sources read verbatim: `docs/decision_log.md:165-172` (index rows) and
`docs/decision_log.md:8833-8890` (tail bodies). Bodies for D-142..D-149 are
stubs that point back at the index rows; index-row text is treated as
authoritative clause text throughout, per the task brief.

---

### D-142 · clause 1
- clause (verbatim): "D-079 successor identity = OPTION B — `d079_calibration_acceptance_v2_n19_r2` at `configs/calibration/calibration_acceptance_d079_v2_r2.json`"
- source: docs/decision_log.md:165
- status: A
- evidence: configs/calibration/calibration_acceptance_d079_v2_r2.json:3 — `"acceptance_id": "d079_calibration_acceptance_v2_n19_r2"` (file exists, 21791 bytes)
- evidence: joulewise/calibration_bracketing.py:72-77 — `SUCCESSOR_ACCEPTANCE_BOUND_PATH = _CALIBRATION_CONFIG_DIR / "calibration_acceptance_d079_v2_r2.json"`, `SUCCESSOR_ACCEPTANCE_ID = "d079_calibration_acceptance_v2_n19_r2"`, `SUCCESSOR_ACCEPTANCE_BOUND_SHA256 = "3c92dd66…"`
- evidence: joulewise/calibration_bracketing.py:132-141 — `ISSUED_ACCEPTANCE_REGISTRY` keys authentication by the artifact's own `acceptance_id` and pins `file_sha256`, so a caller cannot present one generation's bytes under another's pin
- evidence: configs/campaigns/d117_floor_qwen25_1p5b_v1/generate_configs.py:152 — `SUCCESSOR_ACCEPTANCE_ID = "d079_calibration_acceptance_v2_n19_r2"` (the `_v1`/`_v2` pack generator still pins r2, which is correct: those families are frozen)
- producer: joulewise/calibration_bracketing.py `ISSUED_ACCEPTANCE_REGISTRY` (sha-pinned load path); pack-side producer `configs/campaigns/d117_floor_qwen25_1p5b_v1/generate_configs.py`
- transaction_relevant: yes — the acceptance generation is the estimator pin every `_v*` pack and every arm-readiness check binds to.
- note: NOT superseded — r2 is retained forever as the D-138 n=19 successor generation. D-145 adds r3..r6 as LATER generations and r6 is the LIVE one for the `_v3` family; the two coexist. See D-145 clause 4 and D-147 clause 2.

### D-142 · clause 2
- clause (verbatim): "`decision_ids` unchanged (`["D-102","D-109"]`, D-138 recorded log-side)"
- source: docs/decision_log.md:165
- status: A
- evidence: configs/calibration/calibration_acceptance_d079_v2_r2.json:4 — `"decision_ids": [` … verified by `json.load` to be exactly `['D-102', 'D-109']`
- evidence: configs/calibration/calibration_acceptance_d079_v2_n17_r6.json — same `decision_ids` `['D-102', 'D-109']` (the invariance carries into every later generation)
- producer: scripts/reissue_calibration_acceptance.py (deepcopies the predecessor artifact, so `decision_ids` cannot drift without an explicit edit)
- transaction_relevant: yes — claim-edge provenance field on the pinned acceptance artifact.

### D-142 · clause 3
- clause (verbatim): "executed as the one-commit migration (3e780a1) and the in-place 165k re-supersession (54f990d..75f22a0)"
- source: docs/decision_log.md:165
- status: A
- evidence: `git log --oneline -1 3e780a1` → `3e780a15 D-079 successor ISSUED (d079_calibration_acceptance_v2_n19_r2) + dual-generation live-pin migration`
- evidence: `git log --oneline 54f990d..75f22a0` → `75f22a00 D-134 freeze-0002 PASS: d117_contrast_qwen25_1p5b_vs_7b_v2 … re-minted on the D-138 detection-budget head`, plus `f1532718`, `1e635683`, `c1045aa1`, `84fec290` in the same span
- producer: git history (the commits exist and carry the described work)
- transaction_relevant: no — historical execution record, not a live gate.

### D-142 · clause 4 (EXCLUDED — not an implementation clause)
- clause (verbatim): "STANDING NIGHT LICENSE: \"yes you've got the license for all that makes sense in pursuit of a solid paper\""
- source: docs/decision_log.md:165
- status: n/a — pure authority ruling with no artifact, per the brief's exclusion list. The "RECORDED READING" and its preserved counter-reading are narrative dispositions, likewise excluded.

---

### D-143 · clause 1
- clause (verbatim): "DETECTION-PROJECTION CELL BUDGET 100,000 → 165,000"
- source: docs/decision_log.md:166
- status: A
- evidence: joulewise/powermetrics_fiducial.py:88 — `DETECTION_PROJECTION_CELL_BUDGET = 165_000`
- evidence: joulewise/powermetrics_fiducial.py:915 — `projection_cell_budget: int = DETECTION_PROJECTION_CELL_BUDGET` is the production default of `detect_pulses`
- evidence: scripts/validate_powermetrics_fiducial.py:95, :1673-1679 — the validator imports the constant and REFUSES any `--projection-cell-budget-for-test` above it (`> DETECTION_PROJECTION_CELL_BUDGET`), so the test hook cannot raise the production bound
- evidence: tests/test_powermetrics_fiducial.py:579-590 — `RULED_DETECTION_CELL_BUDGET = 165_000` and `test_detection_cell_budget_is_the_ruled_corpus_calibrated_value` asserts equality; a silent revert fails here
- producer: joulewise/powermetrics_fiducial.py `detect_pulses` (the function that produces the detection record written into calibration evidence)
- transaction_relevant: yes — the detector is a governed estimator source; the budget is part of the acceptance-artifact estimator pin.

### D-143 · clause 2
- clause (verbatim): "165,000 = max + 20.3% headroom, exceeding the whole observed spread"
- source: docs/decision_log.md:166
- status: A
- evidence: joulewise/powermetrics_fiducial.py:80-87 — the in-code corpus-basis comment records median 122,044 / p95 135,513 / max 137,189 and "165,000 clears the observed maximum by 27,811 cells (20.3%) -- more than the entire observed 24,984-cell spread"
- evidence: tests/test_powermetrics_fiducial.py:581, :599-604 — `OBSERVED_CORPUS_MAX_CELLS = 137_189` and `assertGreater(DETECTION_PROJECTION_CELL_BUDGET - OBSERVED_CORPUS_MAX_CELLS, 24_984)`
- producer: same as clause 1; the arithmetic relation is asserted at test time
- transaction_relevant: yes — the basis is what makes the pinned budget defensible at the claim edge.

### D-143 · clause 3
- clause (verbatim): "fail-closed semantics retained"
- source: docs/decision_log.md:166
- status: A
- evidence: joulewise/powermetrics_fiducial.py:534-541 — `_ProjectionWorkBudget.consume_cell` raises `_ProjectionBudgetExhausted` with `trigger="evaluated_cell_budget"` at the bound
- evidence: joulewise/powermetrics_fiducial.py:995-1009 — the handler returns a `FiducialDetection` with `all_pulses_detected=False`, `b_fiducial_s=None`, `fits=()`, `reasons=(DETECTION_NONCONVERGENT,)` — registered invalid evidence, never a partial fit
- evidence: tests/test_powermetrics_fiducial.py:635-639 — asserts exactly that fail-closed shape at the raised budget
- producer: joulewise/powermetrics_fiducial.py `detect_pulses`
- transaction_relevant: yes — a partial fit would be admissible-looking claim evidence.

### D-143 · clause 4
- clause (verbatim): "behavioural kill tests pin the production path" / body: "The in-code corpus-basis comment at `joulewise/powermetrics_fiducial.py` and the behavioural budget tests are the mechanical guards."
- source: docs/decision_log.md:166 and docs/decision_log.md:8840-8847
- status: A
- evidence: tests/test_powermetrics_fiducial.py:606-639 — `test_production_default_budget_spends_past_the_retired_ceiling` runs `detect_pulses` with NO injected budget, asserts the count exceeds 100,000 and stops exactly at `DETECTION_PROJECTION_CELL_BUDGET`
- evidence: tests/test_calibration_writer_crash_matrix.py:1469-1493, :1566-1587 — end-to-end writer-level budget-exhaustion coverage through the validator CLI
- producer: joulewise/powermetrics_fiducial.py; guard is test-side
- transaction_relevant: yes.

### D-143 · clause 5 (finding, not an implementation clause)
- clause (verbatim): "first-light re-derivation IN-BAND (b_fiducial 0.030878 s ∈ [0.022741, 0.033559])"
- source: docs/decision_log.md:166
- status: n/a — narrative finding. NOTE for the caller: the band quoted here is the n=19 band; the current live band under r6 is `[0.02317490442656863, 0.03289849371536248]` (tests/verify_calibration_acceptance_corpus.py:40-46), and docs/process/window-run-cards/shakedown-v3-first-light.md:28-33 already records that the 2026-08-18 first light was in-band only under the SUPERSEDED estimator/band. No action; recorded so the stale interval is not re-quoted.

---

### D-144 · clause 1
- clause (verbatim): "no design implemented without independent Sol/terra AND Opus designs -> bounded debate (2 rounds; 3 for big) -> Fable ruling (ratified spec, disagreements recorded) -> implementation gauntlet -> Fable final review (always)"
- source: docs/decision_log.md:167
- status: B
- evidence: docs/decision_log.md:8848-8856 (body) — "The rule text and its forward-application clause live in `docs/process_traces/2026-08-18-t10-t11-working-notes/trace-notes.md` (section \"ED PROCESS RULE\")"
- evidence: docs/process_traces/2026-08-18-t10-t11-working-notes/trace-notes.md:423 — `## ED PROCESS RULE (2026-08-18 evening): co-design protocol` (the rule text does exist at its declared home)
- evidence (the gap): `grep -rln "D-144" ~/.claude/skills docs/*.md docs/process TASK_QUEUE.md RUN_STATE.md CLAUDE.md` → only `docs/council_log.md`, `docs/decision_log.md`, `docs/process/state_kernel.json`, `TASK_QUEUE.md`, `RUN_STATE.md`. It is NOT in `~/.claude/skills/council/SKILL.md`, `~/.claude/skills/adversarial-review/SKILL.md`, `~/.claude/skills/operation-loop/SKILL.md`, `docs/orchestration.md`, or `docs/agent_playbook.md` — i.e. not in any doc a future session mechanically loads before choosing a design route.
- producer: none found — no gate refuses a design that skipped the two-seat pass; compliance is per-task prose in TASK_QUEUE rows.
- transaction_relevant: yes — D-144 is the named authority for the R1/R2 rulings (D-146/D-147) and for the "BIG per D-144" retention on the live `_v4` transaction row (TASK_QUEUE.md:636).
- note: the ONE home is a dated process-trace note, which is exactly the shape that lets a rule go unread. Its only forward-binding surfaces are per-row Fence/Note strings.

### D-144 · clause 2
- clause (verbatim): "BIG designs (new method identities, schema/contract changes, D-138-class, family-superseding) additionally get one more two-seat pass over the implemented artifact pre-merge with a Fable ruling on its findings. Applies forward."
- source: docs/decision_log.md:167
- status: B
- evidence: docs/process/state_kernel.json:1141-1157 — the D-144 pre-merge seat pass WAS executed and its ruling custodied (`docs/process_traces/2026-08-20-go-session/d144-seatpass-ruling.md`), with SF-1/SF-3/SF-5 follow-ups minted
- evidence: RUN_STATE.md:932 — "FOUR pre-merge gates — canonical FULL GREEN, fresh-pass clean, D-144 seat pass, then the wave itself under D-148.2"
- evidence (the gap): no CI job, no script, no test enforces the seat pass; `grep -rn "D-144" .github` returns nothing and no pre-merge tooling references it
- producer: none found — the merge wave is executed by the lead by hand; nothing refuses a BIG merge lacking a seat-pass ruling.
- transaction_relevant: yes — governs the pre-merge gate of the `_v4` transaction.

---

### D-145 · clause 1
- clause (verbatim): "r3 = `d079_calibration_acceptance_v2_n17_r3` (n=17, screens TIGHTENED) issued via the anchor-v3 arc"
- source: docs/decision_log.md:168
- status: A
- evidence: configs/calibration/calibration_acceptance_d079_v2_n17_r3.json:3 — `"acceptance_id": "d079_calibration_acceptance_v2_n17_r3"`; :497 predecessor `d079_calibration_acceptance_v2_n19_r2`
- evidence: joulewise/calibration_bracketing.py:86-92 — `ANCHOR_V3_ACCEPTANCE_ID` + `ANCHOR_V3_ACCEPTANCE_BOUND_SHA256 = "73f02263…"`
- producer: joulewise/calibration_bracketing.py registry (sha-pinned)
- transaction_relevant: yes.

### D-145 · clause 2
- clause (verbatim): "r4 = science-neutral capture-activation reissue (one pin moved; neutrality PROVEN by direct 19-member estimator replay)"
- source: docs/decision_log.md:168
- status: A
- evidence: configs/calibration/calibration_acceptance_d079_v2_n17_r4.json:495 — the `generation` note records the neutrality replay verbatim ("every physical value matched the r3 record exactly")
- evidence: joulewise/calibration_bracketing.py:102-109 — `ANCHOR_V3_R4_ACCEPTANCE_ID` + sha `dcb3d3ed…`
- evidence: tests/verify_calibration_acceptance_corpus.py:54-57 — r4's expected statistics are declared IDENTICAL to r3's, which is the mechanical form of "science-neutral"
- producer: scripts/reissue_calibration_acceptance.py + the bespoke derive/build route (see clause 3)
- transaction_relevant: yes.

### D-145 · clause 3
- clause (verbatim): "The reissue TOOL compares stored scalars and cannot check v3 generations — bespoke derive/build scripts are the r3/r4 route."
- source: docs/decision_log.md:168
- status: C
- evidence: scripts/reissue_calibration_acceptance.py:250-286 — `_candidate_from_predecessor` overwrites `member["b_fiducial_s"]` from `authentication.observed_b_fiducial_by_member` (the STORED bundle scalars) and then validates through `_valid_acceptance_bound`. There is no branch on `acceptance_id`, no anchor-generation check, and no refusal.
- evidence: `grep -n "v3\|anchor_v3\|n17" scripts/reissue_calibration_acceptance.py` → zero hits across all 606 lines. The stated incapacity is nowhere expressed as a guard.
- producer: scripts/reissue_calibration_acceptance.py — the producer that WRITES a candidate acceptance artifact. Running it against an r3+ predecessor would silently re-stamp anchor-v3 member values with superseded v2 stored lexemes and emit a candidate that passes `_valid_acceptance_bound`. Nothing refuses it.
- transaction_relevant: yes — a wrong acceptance artifact is the estimator pin every `_v3`/`_v4` pack binds at birth.
- note: the only place the incapacity is recorded is the decision-log sentence itself. tests/verify_calibration_acceptance_corpus.py:20-24 knows the distinction (`stored_lexeme_is_member_value` False for anchor-v3) but that script has NO callers (see clause 6) and is not consulted by the reissue tool.

### D-145 · clause 4
- clause (verbatim): "r5 (production capture flip; three pins) and r6 (claim-barrier/taxonomy fix round; two pins) issued the same way, each neutrality-proven by full 19-member replay with zero mismatches; r6 is LIVE (sha 0227bca3…); r5/r4/r3 retained"
- source: docs/decision_log.md:168
- status: A
- evidence: `shasum -a 256 configs/calibration/calibration_acceptance_d079_v2_n17_r6.json` → `0227bca3f826edc7f0a1baf98a394df01d8f48e9609966088870d712f765697d` — matches the ruled prefix exactly
- evidence: joulewise/calibration_bracketing.py:121-128 — `ANCHOR_V3_R6_ACCEPTANCE_ID` + `ANCHOR_V3_R6_ACCEPTANCE_BOUND_SHA256 = "0227bca3f826edc7f0a1baf98a394df01d8f48e9609966088870d712f765697d"`
- evidence (LIVE): configs/campaigns/d117_floor_qwen25_7b_v3/plan_tree.json:18 and .../arm_readiness.sources/acceptance-owner.json:6 — `"acceptance_id": "d079_calibration_acceptance_v2_n17_r6"`; same for `d117_floor_qwen25_1p5b_v3` and `d117_contrast_qwen25_1p5b_vs_7b_v3`
- evidence (retained): configs/calibration/ holds all six generations (`_v2.json`, `_v2_r2.json`, `_n17_r3/r4/r5/r6.json`); joulewise/arm_readiness.py:5390-5397 lists all six as issued ids
- evidence (the reissue TRIGGER is mechanical): joulewise/calibration_bracketing.py:1734-1739 — a mismatch between `_current_estimator_code_sha256()` and the artifact's pinned `estimator_code_sha256` appends `protocol_or_estimator_byte_change`, which is what forced r5 and r6
- producer: joulewise/calibration_bracketing.py registry + the `_v3` pack generators
- transaction_relevant: yes — this is the live claim-path pin.

### D-145 · clause 5
- clause (verbatim): "All generations byte-identical forever."
- source: docs/decision_log.md:168
- status: A
- evidence: joulewise/calibration_bracketing.py:63-128 — each generation carries a literal `…_BOUND_SHA256` constant; :130-141 the registry indexes authentication by `acceptance_id` with `file_sha256`, so presenting one generation's bytes under another's pin fails
- evidence: scripts/reissue_calibration_acceptance.py:310 — `raise ReissueCandidateError("refusing to overwrite the issued predecessor")`
- producer: joulewise/calibration_bracketing.py load path; scripts/reissue_calibration_acceptance.py write path
- transaction_relevant: yes.

### D-145 · clause 6 (T-QUANTILE NOTE)
- clause (verbatim): "acceptance interval statistics use exact closed-form Student-t quantiles (Abramowitz & Stegun 26.7.4, solved by bisection in 60-digit decimal, per the artifact's own `quantile_method`); they are generation-DERIVED (the n=17 df moves them relative to the n=19 era) — derived from the corpus, never copied between generations."
- source: docs/decision_log.md:168
- status: B
- evidence (the record exists): configs/calibration/calibration_acceptance_d079_v2_n17_r6.json:481 — `"quantile_method": "exact even-degree-of-freedom closed form (Abramowitz & Stegun 26.7.4) solved by bisection in 60-digit decimal"` (also r3/r4/r5 at the same line)
- evidence (the derivation is NOT in the tree): `grep -rn "26.7.4\|getcontext\|prec = 60\|60-digit" joulewise scripts` → no hit produces those quantiles. The repo's Student-t machinery is `joulewise/aggregate.py:78 student_t_critical_95` and `joulewise/analysis_engine/distributions.py:15-17` (float, not 60-digit decimal), neither of which produced the acceptance-artifact intervals.
- evidence (nothing reads the field): `grep -rn "quantile_method" joulewise scripts tests configs` returns ONLY the four acceptance JSONs. No producer or validator consumes it.
- evidence (partial check exists but is unwired): tests/verify_calibration_acceptance_corpus.py:129-150 re-derives n, min, max, range, mean and sample_sd in `context.prec = 80` decimal against banked per-generation expectations (r3..r6 all registered, :38-63). It does NOT touch the t-quantile, and `grep -rn "verify_calibration_acceptance_corpus" tests scripts joulewise .github` → NO CALLERS: it is a standalone `argparse` CLI (`main()` at :161), not a unittest, not in CI.
- producer: none found in-tree — the quantiles were computed by bespoke build scripts that were not tracked ("no new tracked tooling", D-147). Re-deriving or falsifying them from the repository is not possible today.
- transaction_relevant: yes — the acceptance interval is the admission comparator every calibration bracket is judged against at the measurement window.

---

### D-146 · clause 1
- clause (verbatim): "p2-038.3 schema+method identity with single-key dispatch"
- source: docs/decision_log.md:169
- status: A
- evidence: joulewise/uncertainty_evidence.py:17 — `SCHEMA_VERSION_V3 = "p2-038.3"`; :29 `SCHEMA_FOR_ANCHOR_METHOD = {…}` is the single method→schema key
- evidence: joulewise/uncertainty_evidence.py:1290-1294 — `ANCHOR_METHOD_DERIVERS = {CLOCK_METHOD_V2: derive_powermetrics_anchor_v2, CLOCK_METHOD_V3: derive_powermetrics_anchor_v3}` with `resolve_anchor_deriver` failing closed on an unregistered method
- producer: joulewise/adapters/powermetrics.py (:1840 "Project parsed records onto the p2-038.3 anchor's native evidence") writes the evidence
- transaction_relevant: yes — capture-time evidence schema.

### D-146 · clause 2
- clause (verbatim): "`clock_anchor_era_inconsistent` cross-check"
- source: docs/decision_log.md:169
- status: A
- evidence: joulewise/cli.py:1252-1257 — `if (schema_version is None and anchor_method is None) or SCHEMA_FOR_ANCHOR_METHOD.get(anchor_method) != schema_version: problems.append("strict: uncertainty evidence: clock_anchor_era_inconsistent")`
- evidence: tests/test_capture_pipeline_era.py:59, :71 — `test_crossed_schema_method_pairs_refuse_before_rederivation` and `test_both_missing_schema_and_method_are_era_inconsistent`
- producer: strict bundle verification in joulewise/cli.py (the gate a bundle must pass to be usable)
- transaction_relevant: yes — consumption edge.

### D-146 · clause 3
- clause (verbatim): "eras retained forever"
- source: docs/decision_log.md:169
- status: A
- evidence: joulewise/uncertainty_evidence.py:29-33 — `SCHEMA_FOR_ANCHOR_METHOD` retains v1/v2 mappings alongside v3; the v2 deriver is still registered at :1290-1293
- evidence: docs/paper/draft-v1.md:327 — "this keeps \(748\) older bundles auditable without making them current evidence"
- producer: joulewise/cli.py strict verify (era-faithful re-derivation)
- transaction_relevant: yes.

### D-146 · clause 4
- clause (verbatim): "era-faithful strict verify (the cli.py:1575 rich-telemetry fail-open is a blocker fixed in the flip commit)"
- source: docs/decision_log.md:169
- status: A
- evidence: joulewise/cli.py:1568-1590 — `_strict_rich_telemetry_problems`: "Rich telemetry must move with its stored current-era anchor method. Stored p2-038.1 bundles keep their legacy native-date reconstruction and are not re-judged; p2-038.2 and p2-038.3 bundles must byte-match a re-derivation from the raw capture at the stored anchor endpoint."
- evidence: joulewise/cli.py:1594-1600 — a missing rich-telemetry file WITHOUT a recorded `rich_telemetry_error` is now a problem, not a silent pass (this is the closed fail-open)
- evidence: tests/test_capture_pipeline_era.py:132 — `test_v3_corrupt_rich_telemetry_is_not_fail_open`; :154 `test_v3_unresolved_rich_telemetry_uses_its_fallback_endpoint`
- producer: joulewise/cli.py strict verify
- transaction_relevant: yes — consumption edge.

### D-146 · clause 5
- clause (verbatim): "ONE shared claim-barrier predicate (`CLAIM_BEARING_ANCHOR_METHODS`) with NEW engine reason `capture_pipeline_superseded`"
- source: docs/decision_log.md:169
- status: A
- evidence: joulewise/uncertainty_evidence.py:1299 — `CLAIM_BEARING_ANCHOR_METHODS = frozenset({CLOCK_METHOD_V3})`; :1302-1324 `capture_pipeline_refusal` returns `None` / `"capture_pipeline_absent"` / `"capture_pipeline_superseded"`
- evidence (real consumers, not a dead validator): joulewise/floor_extraction.py:1928, joulewise/whole_window.py:717, joulewise/analysis_engine/inputs.py:3468, joulewise/calibration_bracketing.py:1271 (`_capture_pipeline_refusal_for_observation`, used at :1314, :1581, :2076, :2081)
- evidence (reason registries): joulewise/floor_extraction.py:191, joulewise/whole_window.py:200, joulewise/analysis_engine/claims.py:136 and :174
- evidence: tests/test_capture_pipeline_era.py:78 `test_claim_barrier_rejects_every_non_v3_stored_method`; :97 `test_claim_barrier_distinguishes_absent_from_superseded_presentation`; tests/test_floor_extraction.py:5767
- producer: joulewise/floor_extraction.py (mint), joulewise/whole_window.py (verdict), joulewise/analysis_engine/inputs.py (claim admission) — all three refuse at the point they would produce claim-bearing state
- transaction_relevant: yes — claim edge.

### D-146 · clause 6
- clause (verbatim): "no era-stamping on controller fallback evidence"
- source: docs/decision_log.md:169
- status: A
- evidence: joulewise/controller.py:2249-2259 — `_capture_failure_fallback_environment` calls `_capture_environment(self._clock, capture_scope="failure_fallback", captured_for_rep=None, settle_s=None)`; no anchor method and no schema version is written
- evidence: `grep -rn "SCHEMA_FOR_ANCHOR_METHOD" joulewise` → only joulewise/cli.py:112/1237/1255/1586 and joulewise/uncertainty_evidence.py:29; controller.py never stamps an era
- producer: joulewise/controller.py `_capture_failure_fallback_environment`
- transaction_relevant: yes — a falsely era-stamped fallback record would look claim-admissible.
- note: this is a negative clause satisfied by absence; I verified the absence rather than a positive guard, so a future edit could reintroduce the stamp without a test failing. Nearest guard is the claim barrier itself (clause 5), which refuses on a missing method rather than admitting it.

### D-146 · clause 7
- clause (verbatim): "ratified union site census incl. `arm_readiness.py` issued-set"
- source: docs/decision_log.md:169
- status: A
- evidence: joulewise/arm_readiness.py:5384-5397 — the issued-set returns membership in `{"d079", …_n19, …_n19_r2, …_n17_r3, …_n17_r4, …_n17_r5, …_n17_r6}` with the comment "Every issued D-079 generation routes as the issued artifact… Earlier ids stay listed so predecessor packs are unaffected"
- evidence: scripts/floor_mint_pinsets/schema_v2.json:182-191 — the same six-id union in the pinset schema enum
- evidence: tests/test_capture_pipeline_era.py:266 — `test_arm_readiness_recognizes_the_r6_v3_acceptance_generation`
- producer: joulewise/arm_readiness.py (arm-readiness evidence author)
- transaction_relevant: yes — arm/arm-readiness.

### D-146 · clause 8
- clause (verbatim): "science-neutral D-079 r5 REQUIRED in the same commit as the flip"
- source: docs/decision_log.md:169
- status: A
- evidence: configs/calibration/calibration_acceptance_d079_v2_n17_r5.json:495 — "SCIENCE-NEUTRAL reissue of d079_calibration_acceptance_v2_n17_r4 at the anchor-v3 production-capture flip head. The capture adapter, strict verification, stored-method dispatch, and fiducial labelling were made era-faithful; governed estimator bytes therefore rotated."
- evidence (mechanical forcing function): joulewise/calibration_bracketing.py:1734-1739 — any drift between current estimator bytes and the pinned `estimator_code_sha256` raises the `protocol_or_estimator_byte_change` trigger, so a flip without a reissue cannot stay silent
- producer: joulewise/calibration_bracketing.py trigger evaluation
- transaction_relevant: yes.
- note: the "same commit" part specifically is historical and unenforceable after the fact; the enforceable residue (an estimator byte change must produce a reissue) IS installed.

---

### D-147 · clause 1
- clause (verbatim): "generation-indexed mint-policy resolver (registry-authoritative, operatives-crosswire refusal)"
- source: docs/decision_log.md:170
- status: A
- evidence: joulewise/calibration_bracketing.py:231-266 — `acceptance_generation_operatives(acceptance_id, *, acceptance=None)` — "Return registered D-102 operatives, refusing an operative crosswire"; raises `ValueError` when a supplied artifact's `decimal_derivation.ratified_operatives.bracket_screen_s` disagrees with the registered generation value
- evidence: joulewise/calibration_bracketing.py:269-290 — `acceptance_bracket_screen_s` and `acceptance_allowance_rule` are the only public renderers, both routed through the resolver
- evidence (no copied literals anywhere in the mint lane): tests/test_mint_policy_resolver_guard.py:10-25 — walks EVERY `*.py` under `joulewise/` and `scripts/` except the registry itself and asserts the two screen literals `0.010818` / `0.009724` appear in none of them
- evidence: tests/test_calibration_bracketing.py:685-706 — `test_attempted_operatives_poisoning_does_not_accept_crosswire`
- producer: `configs/campaigns/d117_*_v3/generate_configs.py` — tests/test_d117_v3_family.py:243-247 asserts the generator source contains `acceptance_allowance_rule(` and `acceptance_pin()["acceptance_id"]` and does NOT contain a literal `"allowance_rule": "max(observed_drift_s,`
- transaction_relevant: yes — mint lane.

### D-147 · clause 2
- clause (verbatim): "immutable `_v3` pack family bound at birth to the LIVE generation (r5 per the ruling as written; r6 in execution — fix-round pin moves forced the r6 reissue)"
- source: docs/decision_log.md:170
- status: A
- evidence: configs/campaigns/d117_floor_qwen25_7b_v3/generate_configs.py:207 — `SUCCESSOR_ACCEPTANCE_ID = "d079_calibration_acceptance_v2_n17_r6"`
- evidence: configs/campaigns/d117_floor_qwen25_7b_v3/plan_tree.json:18 and .../arm_readiness.sources/acceptance-owner.json:6 — `"acceptance_id": "d079_calibration_acceptance_v2_n17_r6"` (same in the 1p5b_v3 and contrast_v3 packs)
- evidence: configs/floor_mint/d117_qwen25_7b_v3_extraction_spec.json and d117_qwen25_1p5b_v3_extraction_spec.json — r6-pinned
- evidence: tests/test_d117_v3_family.py:222-255 — `test_v3_specs_and_plan_trees_bind_r6_via_generation_resolver` checks all six cells of each `_v3` spec and each plan tree's `acceptance_policy.issued_acceptance` against the r6 pin
- producer: `configs/campaigns/d117_*_v3/generate_configs.py`; the test is the producer-side kill
- transaction_relevant: yes — pack mint / arm.

### D-147 · clause 3
- clause (verbatim): "`_v2` packs READ-ONLY including their generators (frozen pack content)"
- source: docs/decision_log.md:170
- status: A
- evidence: tests/test_d117_v3_family.py:284-290 — `test_committed_v2_pack_tree_digests_are_unchanged_at_head` compares `committed_pack_tree_sha256(configs/campaigns/<v2 pack>)` against banked `V2_PACK_TREE_SHA256` for every `_v2` pack; any edit to a `_v2` generator or pack file fails
- producer: git tree; the digest test is the refusal
- transaction_relevant: yes — the `_v2` family is the predecessor half of the freeze chain.

### D-147 · clause 4
- clause (verbatim): "freeze-0003 chained to freeze-0002 (parked step 6 AMENDED — no freeze-0002 re-mints)"
- source: docs/decision_log.md:170
- status: A
- evidence: configs/campaigns/d117_floor_qwen25_7b_v3/arm_readiness.freeze.receipts/freeze-0003.json:129-130 — predecessor block `"path": "arm_readiness.freeze.receipts/freeze-0002.json"`, `"receipt_id": "freeze-0002"`; :145 `"receipt_id": "freeze-0003"`. Same shape in the contrast `_v3` pack (:129-130, :145).
- evidence: configs/campaigns/d117_floor_qwen25_7b_v3/plan_tree.json:37 — the pack pins `arm_readiness.freeze.receipts/freeze-0003.json`, while the `_v2` packs still pin freeze-0002 (d117_floor_qwen25_7b_v2/plan_tree.json:37) — no re-mint occurred
- evidence: docs/process/ed-s5-mint-decision-2026-08-19.md:82-84 — the confirmation table records each `_v2` freeze-0002 sha as the predecessor and each `_v3` freeze-0003 sha; the freeze-0003 sidecar `f232d076…` matches `configs/campaigns/d117_floor_qwen25_7b_v3/arm_readiness.freeze.receipts/freeze-0003.json.sha256:1`
- producer: `scripts/generate_arm_readiness.py freeze --pack-root <v3> --predecessor-pack-root <v2>`
- transaction_relevant: yes — arm-readiness freeze chain.

### D-147 · clause 5
- clause (verbatim): "`_v3` produced by the unedited `_v2` generators then draft-retargeted"
- source: docs/decision_log.md:170
- status: A
- evidence: tests/test_d117_v3_family.py:141 — `test_unedited_v2_generators_emit_v3_successors`
- evidence: tests/test_d117_v3_family.py:193 — `test_check_still_refuses_missing_generator_owned_output`
- producer: `configs/campaigns/d117_*_v2/generate_configs.py` (unedited, digest-frozen per clause 3)
- transaction_relevant: yes.

### D-147 · clause 6
- clause (verbatim): "genesis digest RENAMED only"
- source: docs/decision_log.md:170
- status: AMBIGUOUS
- evidence: `grep -rn "genesis" joulewise scripts configs tests` → the surviving genesis surfaces are joulewise/calibration_bracketing.py:57, :174, :428, :464, :728, :1336, :1444, :1463, :1522 and joulewise/calibration_ledger.py:445, :483, :2023-2036, :2588, :2727-2746 — all describing the retained `schema_fixture_unissued` genesis fixture and its byte-sha pin, none naming a D-147 rename
- producer: n/a
- transaction_relevant: no — a naming-only refactor.
- note: best reading is that an identifier carrying "genesis" was renamed during the R2 execution without any value change. I cannot bind the clause to a specific symbol from the tree at HEAD, and its ONE home (`docs/process_traces/2026-08-19-r1-r2-codesign/14-r2-ruling.md`) was outside the exact line ranges assigned. Recorded rather than guessed.

### D-147 · clause 7
- clause (verbatim): "no new tracked tooling"
- source: docs/decision_log.md:170
- status: AMBIGUOUS
- evidence: `ls scripts | grep -i "reissue\|acceptance"` → only the pre-existing `reissue_calibration_acceptance.py`; no R2-era script appeared
- producer: n/a — a negative constraint on the transaction, satisfiable only by absence
- transaction_relevant: no.
- note: the OBSERVABLE consequence of this clause is D-145 clause 6's gap — the bespoke r3..r6 derive/build scripts were deliberately not tracked, which is why the 60-digit t-quantile derivation cannot be reproduced from the repository. The two should be read together.

### D-147 · clause 8
- clause (verbatim): "binding sequencing S0-S6 with freeze-0003 as the last acceptance-bearing step"
- source: docs/decision_log.md:170
- status: B
- evidence: docs/process/ed-s5-mint-decision-2026-08-19.md:1-12 and :47+ — the S5 step is written out as an exact command sequence with "one commit per step", and the confirmation table at :71 records S5 as EXECUTED
- evidence (the gap): `grep -rn "S0-S6\|freeze-0003" joulewise scripts` → the only script surface is scripts/ed_session/build_rehearsal_env.sh:71-88, which requires and pins **freeze-0002**, not freeze-0003. No script enforces the S0..S6 order or refuses an out-of-order step.
- producer: none found — the sequencing was executed by hand from the ruling's ONE home (`docs/process_traces/2026-08-19-r1-r2-codesign/14-r2-ruling.md`).
- transaction_relevant: yes — the transaction's own step order.
- note: the sequencing was for a completed transaction, so the live exposure is limited; the residual is that `scripts/ed_session/build_rehearsal_env.sh` still hard-pins freeze-0002 while the live `_v3` packs pin freeze-0003, so a rehearsal env built from that script targets the superseded freeze generation.

---

### D-148 · clause 1 (ruling 1, S5 mint route)
- clause (verbatim): "S5 mint route = OPTION B — a narrow `settings.local.json` Bash allow rule for the two freeze scripts, Claude executes under the issued license (NOTE: the harness classifier also blocks Claude from WRITING that rule … so the rule requires Ed's own hands; exact snippet in the S5 packet)"
- source: docs/decision_log.md:171
- status: B
- evidence (the packet exists with the exact snippet): docs/process/ed-s5-mint-decision-2026-08-19.md:24-33 — the four ruled lines, verbatim: `"Bash(python3 scripts/project_identity_pins.py freeze *)"`, `"Bash(python3 scripts/generate_arm_readiness.py freeze *)"`, and the two `cd /Users/edr/JouleWise-measurement-20260818 && …` variants
- evidence (the rule was NOT installed as ruled): .claude/settings.local.json `permissions.allow` contains only the narrower literals `"Bash(python3 scripts/project_identity_pins.py freeze configs/campaigns/d117_floor_qwen25_1p5b_v3)"` (line 16), `"…freeze configs/campaigns/d117_floor_qwen25_1p5b_v3 --help)"` (line 17), `".venv/bin/python3 … freeze configs/campaigns/d117_floor_qwen25_1p5b_v3)"` (line 25), `"Bash(python3 scripts/generate_arm_readiness.py freeze --help)"` (line 27). None of the four ruled wildcard entries is present; only the 1p5b pack is covered, and `generate_arm_readiness.py freeze` is allowed for `--help` only.
- evidence (the outcome was reached another way): docs/process/ed-s5-mint-decision-2026-08-19.md:71 — "Confirmation table (COMPLETE — S5 executed 2026-08-19 under D-148.1, **mints via Ed-approved manual prompts**)"
- producer: `.claude/settings.local.json` (Ed's hands only — the classifier forbids self-granting)
- transaction_relevant: yes — the `_v4` transaction needs the same two freeze scripts at the measurement checkout, and TASK_QUEUE.md:636 still lists "Ed's D-150(1) live permission prompts" as remaining scope.
- note: this is a live operational gap for the `_v4` mint, not a historical one: the ruled route is still unavailable, so the `_v4` freeze mints will again require per-prompt Ed approval unless Ed installs the four lines.

### D-148 · clause 2 (ruling 2, merge waves) — EXCLUDED as pure authority, with one artifact residue
- clause (verbatim): "MERGE WAVES ARE GATE-AUTHORIZED, NOT ED-AUTHORIZED — the rule-4/D-072 gate shape (council/lead review, CI green, fresh pass over post-review commits) is the complete authority for merging; Ed's naming of merges was a harness workaround, never a personal approval gate; the impl→integration→main wave for this transaction is pre-authorized on gates-green"
- source: docs/decision_log.md:171
- status: B (for the recorded gate shape only)
- evidence: RUN_STATE.md:932 — "GATE COUNT, canonical formulation: FOUR pre-merge gates — canonical FULL GREEN, fresh-pass clean, D-144 seat pass, then the wave itself under D-148.2"
- evidence: TASK_QUEUE.md:120 — "merge wave landed on main `5bd7acf` (PR #160) through all four D-148.2 gates"
- evidence (the gap): no CI check, branch-protection rule, or script encodes the four gates; `grep -rn "D-148" .github` returns nothing
- producer: none found — the lead executes `gh pr merge` (allowed by .claude/settings.local.json line 4)
- transaction_relevant: yes — the `_v4` merge wave rides this authority.

### D-148 · clause 3 (ruling 3)
- clause (verbatim): "confirmation table reviewed post-mint"
- source: docs/decision_log.md:171
- status: A
- evidence: docs/process/ed-s5-mint-decision-2026-08-19.md:71-84 — the complete table: live generation r6, r6 sha `0227bca3…`, r5 sha `92b9c060…`, the three `_v2` freeze-0002 predecessor shas, the three S4 evidence rollups, and the three freeze-0003 sha + committed tree digests
- evidence (independently re-verified): the r6 sha in the table equals `shasum -a 256 configs/calibration/calibration_acceptance_d079_v2_n17_r6.json`; the 7b freeze-0003 sha `f232d076…` equals configs/campaigns/d117_floor_qwen25_7b_v3/arm_readiness.freeze.receipts/freeze-0003.json.sha256:1; the contrast sha `f32bd3a8…` equals its sidecar; the three `_v2` freeze-0002 shas equal their sidecars
- producer: docs/process/ed-s5-mint-decision-2026-08-19.md (the document IS the artifact)
- transaction_relevant: yes — exact-byte confirmation is a retained Ed item at the claim edge.

### D-148 · clause 4 (ruling 4, quiet windows)
- clause (verbatim): "QUIET WINDOWS ARE LEAD-DELEGATED — when a measurement window needs no physical presence at the machine, the lead schedules and runs it at its own discretion whenever Ed has the loop running (supersedes the wait-for-Ed-batch posture for non-hands items; hardware/sudo/physical items remain Ed's)"
- source: docs/decision_log.md:171
- status: A
- evidence: docs/process/state_kernel.json:1009-1012 (and the identical blocks at :1060-1063 and :1111-1114 for BETA/GAMMA) — fence label "D-149 standing conditional T-0 GO (2026-08-19)" with rule "…T-0 GO auto-issues per D-149 when its five recorded conditions pass (no-hands windows); hands-required work remains Ed's"
- evidence: TASK_QUEUE.md:578-580 — the same fence string is rendered into the D117-W-ALPHA/BETA/GAMMA rows
- producer: docs/process/state_kernel.json → TASK_QUEUE.md (the kernel is the generator of the fence text)
- transaction_relevant: yes — window scheduling authority.

### D-148 · clause 5 (ruling 5, R1 registry values)
- clause (verbatim): "R1 row-registry reserved values → COUNCIL (Ed defers; run the co-design/council pass when the Codex pool returns, then proceed)"
- source: docs/decision_log.md:171
- status: A
- evidence: TASK_QUEUE.md:120 — "the D-148.5 council ruled FINAL with the values custodied and the INSTALL re-homed to the `_v4` boundary by three executed blockers (byte-pin, V1_GRANDFATHERING, the evidence fuse) — install rides V4-TRANSACTION-01. Custody `docs/process_traces/2026-08-20-go-session/`."
- evidence: RUN_STATE.md:747 — "**D-148.5 REGISTRY COUNCIL IS FINAL**"
- evidence: TASK_QUEUE.md:636 — the `_v4` row carries "registry install (112-path allowlist, code deltas, load closure)" as executable scope with "Authority: [D-148.5 r5 FINAL (cold-ratified with two attached sentences)]"
- producer: the V4-TRANSACTION-01 registry install (pending execution, correctly queued)
- transaction_relevant: yes — the registry install is a step of the `_v4` transaction.

### D-148 · clause 6 (ruling 6, risk-appetite family)
- clause (verbatim): "the risk-appetite family (recorder race / T-0 capture provenance / hostile same-UID injection / forged launch-context) is ACCEPTED AS REGISTERED LIMITATIONS — in-process adversary out of model, per D-139 A1"
- source: docs/decision_log.md:171
- status: A
- evidence: CLAIMS_STATUS.md:15-19 — "(b) The in-process-adversary family (recorder check-to-grant race, T-0 capture provenance, hostile same-UID injection, forged launch-context) is accepted as a registered limitation: the threat model assumes no adversarial process on the measurement machine (D-139 A1). Both belong in the paper's limitations section"
- evidence: docs/paper/draft-v1.md §7 — "**Where the captures came from rests on trusting the operator.**… it cannot prove who created a capture or what unobserved process ran on the machine" (covers provenance / forged launch-context / same-UID injection) and "**A known timing gap between checking a file and using it, accepted rather than repaired.**… Both the check that selects the file and the step that grants the permission identify the file by its path name, and they do so at different moments" (covers the recorder check-to-grant race)
- producer: CLAIMS_STATUS.md and docs/paper/draft-v1.md §7 (the documents ARE the artifacts)
- transaction_relevant: yes — claim edge (paper limitations).

### D-148 · clause 7 (ruling 7, anchor-v2 population)
- clause (verbatim): "the stored anchor-v2 population (748 repo-tree bundles) gets a REGISTERED LIMITATION paragraph: permanently non-claim-bearing on estimator grounds, mechanically enforced by the D-146 barrier"
- source: docs/decision_log.md:171
- status: A
- evidence: CLAIMS_STATUS.md:10-14 — "(a) the stored anchor-v2 population — 748 bundles in the repository tree — is PERMANENTLY non-claim-bearing on estimator grounds (the v2 rate=1 model was falsified); replay/audit value retained forever; enforcement is the mechanical D-146 claim barrier."
- evidence: docs/paper/draft-v1.md:439 — the full paragraph: "**The 748 bundles collected under the retired clock-anchor calculation stay auditable but can never support a claim.**… The exclusion is therefore permanent rather than provisional, and the program enforces it rather than leaving it to convention: no path exists by which one of these bundles is admitted to a claim."
- evidence (the mechanical half): joulewise/uncertainty_evidence.py:1299-1324 (the barrier) with producer-side consumers at joulewise/floor_extraction.py:1928, joulewise/whole_window.py:717, joulewise/analysis_engine/inputs.py:3468
- evidence (the superseded literals were actually removed): CLAIMS_STATUS.md:45 — "The superseded-era replay magnitudes formerly quoted here were removed under the B7 magistrate ruling (D-146 + D-148 cl.7…)"; TASK_QUEUE.md:266 records the same removal from `docs/paper/draft-v1.md`
- producer: joulewise/floor_extraction.py / whole_window.py / analysis_engine/inputs.py refuse at write time; the documentation half is CLAIMS_STATUS.md + draft-v1.md:439
- transaction_relevant: yes — claim edge.

---

### D-149 · clause 1 (the framing clause — the mechanical evaluation)
- clause (verbatim): "T-0 GO is AUTO-ISSUED when ALL of the following hold, evaluated mechanically at T-0 and written into the window's custody record as a GO receipt"
- source: docs/decision_log.md:172
- status: C (for "evaluated mechanically"); the receipt FORM exists as a doc
- evidence (the tooling is explicitly absent): docs/process/d149-go-receipt-template.md:62-66 — "Tooling: a mechanical evaluator script MAY be built to fill C2–C4, but it goes through the ordinary gauntlet first; **until then the issuer fills the receipt by running the runbook commands and attaching outputs.**"
- evidence (registered as unbuilt work): TASK_QUEUE.md:415-420 — "## WO-D149-GO-EVALUATOR (registered 2026-08-19 night) — Build the mechanical evaluator that fills GO-receipt conditions C2-C4…; until it lands the issuer follows the template's runbook by hand."
- evidence: RUN_STATE.md:918-921 — "D-149 GO-receipt tooling: the five GO conditions as a mechanical checklist evaluation (script + receipt template) so every window GO is a written receipt from the first shakedown" — listed as prep work, not as done
- evidence (nothing in the launch path knows about it): `grep -rn "D-149\|d149" scripts joulewise tests` → ZERO hits in code. scripts/launch_window.py:38-60 `_parser()` requires only `--pack-root`, `--arm-receipt`, `--arm-readiness-custody-root`, `--launch-manifest` (+ optional `--lifecycle-event`, `--step6-confirmation-table`, `--expected-confirmation-digest`); scripts/launch_window.py:239-268 `launch()` validates the arm receipt and execve's — no GO-receipt argument, no condition evaluation, no refusal.
- evidence: scripts/prewindow_check.sh:1-26 predates D-149 and describes itself as "a READINESS check, not a measurement gate"; `grep -n "bootsession\|networktime\|census\|verdict\|GO\|receipt" scripts/prewindow_check.sh` finds no D-149 condition.
- producer: scripts/launch_window.py — the script that consumes the launch capability and execve's the window. It is the producer that must refuse a GO without a receipt, and it does not.
- transaction_relevant: yes — this is the arm/window edge, and the `_v4` transaction row (TASK_QUEUE.md:636) makes "shakedown complete with GO receipts" an acceptance criterion.
- note: THIS IS THE D-157 SHAPE. The rule is ruled and templated; the producer never learned it. A window can be launched today with no GO receipt in custody and nothing anywhere refuses.

### D-149 · clause 2 (condition 1)
- clause (verbatim): "a READY-candidate council verdict stands (charter form: no NOT-READY, no UNVERIFIED, ED-QUALIFICATION rows closed) — this clears WINDOW-COUNCIL-GATE per its recorded clearance rule"
- source: docs/decision_log.md:172
- status: C
- evidence (the form exists as prose): docs/process/d149-go-receipt-template.md:16-19 — "C1 READY-candidate council verdict stands / verdict path / form check: no NOT-READY: [ ] no UNVERIFIED: [ ] ED-QUAL rows closed: [ ] / verdict sha256"
- evidence (the gate is text-only): docs/process/state_kernel.json:1012 — the fence is a `"rule"` string; TASK_QUEUE.md:578 renders it into the row's Fence field. No code reads it.
- evidence: `grep -rn "WINDOW-COUNCIL-GATE\|NOT-READY\|ED-QUALIFICATION" joulewise scripts` → no code surface; the charter is docs/process/instrument-readiness-audit-charter.md, consumed by humans
- producer: scripts/launch_window.py — no `--council-verdict` argument, no verdict sha check
- transaction_relevant: yes — this is the gate that blocks every claim window.

### D-149 · clause 3 (condition 2)
- clause (verbatim): "the frozen pack's arm ceremony passes every gate with freshness horizons honored"
- source: docs/decision_log.md:172
- status: A
- evidence: joulewise/arm_readiness_evidence_t0.py:49-50 — `_VOLATILE_EVIDENCE_VALIDITY_NS = 20 * 60 * 1_000_000_000` and `_NONVOLATILE_EVIDENCE_VALIDITY_NS = 6 * 60 * 60 * 1_000_000_000` (the 20-minute and 6-hour horizons the template's C2 line quotes)
- evidence: joulewise/arm_readiness_evidence_t0.py:1767-1777 `_validity_horizon_ns` refuses an unclassified kind; :2005-2007 applies `validity_origin + _validity_horizon_ns(item.kind)`
- evidence: joulewise/arm_readiness_evidence_t0.py:2022-2026 — HEAD/tree/pack re-check plus a SECOND boot probe, refusing `evidence_author_t0_input_changed` if anything moved during derivation
- evidence: scripts/launch_window.py:113-141 — `validate_arm_receipt` then `_verify_arm_receipt`, refusing `launch_consumption_invalid` on an invalid receipt and refusing if the authenticated receipt changed during assembly
- producer: joulewise/arm_readiness_evidence_t0.py (evidence author) and scripts/launch_window.py (launch-time verification)
- transaction_relevant: yes.

### D-149 · clause 4 (condition 3)
- clause (verbatim): "the machine is quiet: census clean, fleet quiesced, no interactive use, single writer"
- source: docs/decision_log.md:172
- status: C
- evidence (runbook only): docs/process/d149-go-receipt-template.md:21-26 (C3 checkboxes) and :50-56 — "C3: census per the T11 driver pattern (docs/process_traces/2026-08-18-t10-t11-working-notes/shakedown-driver.sh is the model…)"; the census is a per-session shell pattern in a dated trace directory, not a tracked gate
- evidence (the quiet-guard subsystem is NOT promoted): joulewise/quiet_guard.py:835-847 `arm_refusal()` returns `failure_mapping("live_promotion_disabled", "Commit 1 has no production promotion capability")` — the single-writer/lease machinery exists but cannot arm in production
- evidence (no integration): `grep -rn "quiet_guard\|QuietGuard" joulewise scripts` outside the module itself finds only scripts/quiet_guard.py (its own CLI), scripts/quiet_guard_privileged.py, scripts/setup_quiet_guard.sh (installer). scripts/launch_window.py never imports it.
- evidence: scripts/prewindow_check.sh checks idle-triggered daemons (XProtect et al.), which is a partial and unrelated overlap; it is not called by launch_window.py and its own header says it "never waives, relaxes, or substitutes for the campaign's own environment and CPU admission gates"
- producer: scripts/launch_window.py — no census argument, no quiesce check, no single-writer attestation
- transaction_relevant: yes — a contaminated window produces bytes the verdict edge later refuses, after the campaign has run.
- note: `joulewise/quiet_guard.py` is a validator-shaped module with no production caller — a B-by-the-brief's-rule at best, and its own code says it is disabled, so C is the conservative call.

### D-149 · clause 5 (condition 4)
- clause (verbatim): "boot-session and clock-discipline checks pass at T-0"
- source: docs/decision_log.md:172
- status: B
- evidence (boot session IS mechanical, at the arm ceremony): joulewise/arm_readiness_evidence_t0.py:441 — `("/usr/sbin/sysctl", "-n", "kern.bootsessionuuid")`; :447 `_require_boot_session_id`; :493, :532, :621, :1878, :1885 compare every receipt and source against `context.boot_session_id`; :2024-2026 re-probes and refuses if the boot session changed during derivation
- evidence (clock discipline is NOT mechanical): docs/process/d149-go-receipt-template.md:28-31 — "C4… network time: OFF (evidence: <command output attached>)"; RUN_STATE.md:868 — "`-getusingnetworktime` — required before any D-149 auto-GO window"; TASK_QUEUE.md:643 (A80 T0-UNATTENDED-01) — "The sudoers -getusingnetworktime item remains observability-only; hardware/sudo/physical items remain Ed's hands"
- evidence (the gap at the launch producer): scripts/launch_window.py performs no boot-session or network-time check of its own; the boot binding is enforced only by the arm receipt it validates, and the network-time state is never read by any code (`grep -rn "usingnetworktime" joulewise scripts` → no hit)
- producer: joulewise/arm_readiness_evidence_t0.py enforces boot session at arm time; NOTHING enforces clock discipline at T-0
- transaction_relevant: yes — an actively-steered wall clock is the exact defect that refused two of nineteen calibration members (D-145 / draft-v1.md:161).

### D-149 · clause 6 (condition 5)
- clause (verbatim): "the D-078 no-retry discipline binds — a refused capture ends that lane with diagnosis, never re-arm-and-hope"
- source: docs/decision_log.md:172
- status: B
- evidence (documented): docs/process/d149-go-receipt-template.md:33-35 (C5) and :57-59 — "C5: no evidence — it is the issuer's binding acknowledgment"; docs/process/window-run-cards/shakedown-v3-first-light.md §"Refusal handling (D-078 binds)" — "Any refusal (budget, anchor, admission) ENDS the block. Diagnose from the recorded reason read-only; no re-arm without a diagnosed, removed [cause]"; RUN_STATE.md:1269
- evidence (partial mechanism): scripts/launch_window.py:262-264 — "Successful execve never returns. There is deliberately no child process, wait path, or automatic retry after the capability's linearization point"; scripts/launch_window.py:192-238 — the handoff token is a one-use capability
- evidence (the gap): nothing refuses a FRESH arm ceremony after a refused capture. `grep -rn "no_retry\|no-retry\|re-arm" joulewise scripts` → no code surface. The one-use capability prevents replaying one launch, not re-arm-and-hope.
- producer: joulewise/arm_readiness_evidence_t0.py / scripts/generate_arm_readiness.py would have to refuse a re-arm on a lane with a recorded refusal; neither does
- transaction_relevant: yes — re-arm-and-hope after a refusal is a selection effect at the claim edge.

### D-149 · clause 7 (retained Ed items)
- clause (verbatim): "REMAINS ED'S: anything needing hands (cables, backlight, reboots, new sudo), claim publication, exact-byte confirmation."
- source: docs/decision_log.md:172
- status: A
- evidence: docs/process/state_kernel.json:1012 — "hands-required work remains Ed's" in each window fence; TASK_QUEUE.md:578-580 renders it
- evidence: TASK_QUEUE.md:643 — "hardware/sudo/physical items remain Ed's hands (r4-6…)"
- evidence: TASK_QUEUE.md:636 — step-6 exact-byte confirmation is carried as an explicit acceptance item under the D-150b delegation
- producer: docs/process/state_kernel.json (fence generator)
- transaction_relevant: yes.

### D-149 · clause 8 (ONE home)
- clause (verbatim): "ONE home for the GO-receipt form: `docs/process/d149-go-receipt-template.md`."
- source: docs/decision_log.md:172
- status: A
- evidence: docs/process/d149-go-receipt-template.md exists (3000 bytes, 2026-08-20) and carries the full five-condition receipt block plus the evidence runbook
- evidence (it is referenced, not duplicated): docs/process/window-run-cards/shakedown-v3-first-light.md:9-11 — "## Preconditions (all five D-149 GO conditions; receipt per the template) / docs/process/d149-go-receipt-template.md — filled, custodied, GO."; TASK_QUEUE.md:418 cites it as authoritative
- producer: the document itself
- transaction_relevant: yes.
- note: `grep -rln "GO RECEIPT\|D-149 T-0 GO" docs/process_traces docs/process` finds only the template plus two ruling/packet mentions — NO filled GO receipt exists in any custody record yet, consistent with no window having run under D-149.

### D-149 · clause 9 (kernel fences)
- clause (verbatim): "Supersedes the per-window \"separate perishable T-0 GO from Ed\" fence for no-hands windows; kernel fences updated this commit."
- source: docs/decision_log.md:172
- status: A
- evidence: docs/process/state_kernel.json:1009-1012, :1060-1063, :1111-1114 — all three D117-W-ALPHA/BETA/GAMMA fences carry label "D-149 standing conditional T-0 GO (2026-08-19)" and the amended rule text
- evidence: TASK_QUEUE.md:578-580 and :689-690 — the amended fence string is rendered into the queue rows
- producer: docs/process/state_kernel.json → `scripts/gen_state.py` renders TASK_QUEUE.md (allow-listed at .claude/settings.local.json line 20)
- transaction_relevant: yes.
