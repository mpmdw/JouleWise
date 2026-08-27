# G4 enumeration — D-133 and D-134 (+ their amendments)

Scope read verbatim: `docs/decision_log.md` lines 158-159, 8471-8530, 8531-8623,
8624-8668, 8733-8784, 8921-8945, 9472-9500 (and the contiguous D-078 launch
amendment at 9500-9527, read because 9472-9500 ends mid-sentence at "the D-078
vocabulary registered below"), 9666-9692.

## Non-implementation clauses skipped (per brief §Definitions)

- D-133 (1) fallback-merge sequencing / "FCM-01 may not gate it thereafter" — pure
  merge-authority ruling, no artifact.
- D-133 (3) "A FULL fresh delta is owed on the branch head… any exact understatement
  drops the estimator PERMANENTLY" — audit-obligation + conditional authority rule.
- D-133 "Flagged to Ed (schedule call, not ruled)" — explicitly not ruled.
- D-124/D-133 impl note "F11 scope and inventory" WRITE_SCOPE amendment and
  "F11(c) must be re-executed by the lead" — session-scoped process authority.
- D-133 cl.4 ratification item 3 ("Window night: TONIGHT (2026-08-12)") — schedule.
- D-134 clause 9's "historical process traces are preserved and superseded by
  decision, never edited in place" is carried inside clause 9's block below.

---

### D-133 · clause C1 (disposition (2), ALT-D120)
- clause (verbatim): "FCM-01 continues as an unmerged desk thread under ALT-D120: DELETE the serialized registration vocabulary (CellReport.as_row stops emitting it; removed from _D117_MINT_FLOOR_OPTIONAL_KEYS and _CMP_OPTIONAL_KEYS; self-equality branch deleted) so both demonstrated forgeries become closed-profile unknown-key REFUSALS — the D-120 precedent (delete vocabulary, don't authenticate it)."
- source: docs/decision_log.md:8500-8507
- status: A
- evidence: joulewise/floor_extraction.py:1487-1492 — `_D117_MINT_FLOOR_OPTIONAL_KEYS = {"whole_window_drift_allowance_j", "whole_window_drift_allowance_provenance", "drift_widened_unguarded_floor_j", "drift_widened_guarded_floor_j"}`; no `estimator_registration`.
- evidence: joulewise/detection_floor.py:1891-1897 — `_CMP_OPTIONAL_KEYS = _ATTRIBUTION_LIMIT_RECORD_KEYS` = {floor_source, floor_limit_class, point_floor_diagnostic, single_count_discipline}; no `estimator_registration`.
- evidence: joulewise/floor_extraction.py:1304-1409 — `CellReport.as_row` builds `row`/`floor_row` and never writes an `estimator_registration` key; the sibling property at :1299-1302 returns `None` with the docstring "Registration exists only on extraction-owned report instances."
- evidence: joulewise/floor_extraction.py:1560-1566 — `validate_admitted_report_vocabulary` emits `"extraction report: forbidden key 'estimator_registration' at {path}"` (report side).
- evidence: joulewise/detection_floor.py:4164-4172 — artifact side: `"artifact: forbidden key 'estimator_registration' at {path}"`.
- evidence: joulewise/analysis_engine/inputs.py:279,313-317 and joulewise/analysis_engine/registry.py:197,225-231 — the analysis-input and AP-SPEC admission parsers refuse the key too.
- evidence (test): tests/test_floor_extraction.py:534-544 — `test_closed_profile_rejects_injected_estimator_registration` pins the exact refusal string.
- producer: `joulewise/floor_extraction.py::CellReport.as_row` (report bytes) and `scripts/mint_floor_artifact_generalized.py` via `detection_floor` artifact validators (artifact bytes).
- transaction_relevant: yes — the `_v4` mint's report/artifact admission profile.

### D-133 · clause C2 (disposition (2), provenance correction + sha rotation)
- clause (verbatim): "The false round-6 provenance claim (\"registered results exist only as governed extraction artifacts\") is corrected to what the design enforces, with a sixth parameter-sha rotation."
- source: docs/decision_log.md:8507-8511
- status: A
- evidence: joulewise/detection_floor.py:171-176 — `_COMMON_MODE_PARAMETERS["registered_result_provenance_rule"] = "registration_is_declared_only_in_the_committed_preregistered_extraction_spec_no_admitted_report_or_artifact_vocabulary_represents_a_registered_result"` — the corrected wording, matching what C1 enforces.
- evidence: joulewise/detection_floor.py:178-187 — `COMMON_MODE_PARAMETER_SHA256` is *derived* by hashing `_COMMON_MODE_PARAMETER_DOMAIN + b"\0" + canonical json(_COMMON_MODE_PARAMETERS)`, so editing that string mechanically rotates the sha; it is not a hand-typed literal that can drift.
- evidence: joulewise/floor_mint_estimator.py:89 — the mint dispatcher refuses a spec cell whose `registration["parameter_sha256"]` differs from the derived constant.
- evidence (test): tests/test_d117_decode_contrast_plan.py:2273-2280 — pack cells' `floor_estimator_registration` and its `parameter_sha256` are asserted equal to the canonical registration.
- producer: `joulewise/detection_floor.py::two_shared_edge_common_mode_registration` (:487-493), consumed by each pack's `generate_configs.py`.
- transaction_relevant: yes — the pinned estimator identity the `_v4` mint authenticates.

### D-133 · clause C3 (disposition (4), conditional re-spec + queue registration)
- clause (verbatim): "Packs re-spec back to the tighter estimator only if ALT-D120 + the full delta + the mint-estimator vocabulary workstream (new, D-118-gated, registered in TASK_QUEUE) all land before the freeze wave."
- source: docs/decision_log.md:8512-8515
- status: A
- evidence: TASK_QUEUE.md:129 — "| WO-MINT-ESTIMATOR-VOCAB | P2 Next Slice | 2026-08-12 | Add spec-authoritative governed estimator dispatch at all three v2 mint sites | … Merged via #140 (`e11b1ad`) …, satisfying the D-133 clause 4 prerequisite."
- evidence: TASK_QUEUE.md:227 — "## WO-MINT-ESTIMATOR-VOCAB — COMPLETED (`e11b1ad`, 2026-08-12; registered 2026-08-11)".
- producer: TASK_QUEUE.md (the registration artifact the clause names).
- transaction_relevant: yes — gated the floor value the `_v4` packs carry.

### D-133 · clause C4 (disposition (5), debts enter the ledger)
- clause (verbatim): "Debts surfaced, not discharged: the FLOOR-COMMONMODE-01 BANKED UNGATED 425f75f audit debt and the fallback's previously-unstated gate status enter the ledger."
- source: docs/decision_log.md:8516-8518
- status: A
- evidence: TASK_QUEUE.md:287 — "- FLOOR-COMMONMODE-01 BANKED UNGATED 425f75f: full magistrate audit +".
- evidence: TASK_QUEUE.md:290 — "- Fallback gate history: respec/d124-withdrawn had NO gate record before".
- producer: TASK_QUEUE.md.
- transaction_relevant: no — audit-debt bookkeeping, not a mint/arm/window/claim byte.

### D-133 · clause C5 (bench-verified fact: claim-path binding)
- clause (verbatim): "the production claim path binds `expected_sha256` + `expected_artifact_id`, which the delta's V3 reproduction omitted."
- source: docs/decision_log.md:8489-8491
- status: A
- evidence: joulewise/analysis_engine/inputs.py:856-857 — parameters `expected_sha256`/`expected_artifact_id`.
- evidence: joulewise/analysis_engine/inputs.py:869 — `if expected_sha256 is not None and digest != expected_sha256:` (refusal).
- evidence: joulewise/analysis_engine/inputs.py:884 — `if expected_artifact_id is not None and artifact_id != expected_artifact_id:` (refusal).
- evidence: joulewise/analysis_engine/artifact.py:1037-1038 — the claim path supplies both: `expected_sha256=floor_link.get("file_sha256")`, `expected_artifact_id=floor_id`.
- producer: `joulewise/analysis_engine/artifact.py` (claim-edge floor loading).
- transaction_relevant: yes — claim edge.

### D-133 · clause C6 (bench-verified fact: mint had zero estimator vocabulary)
- clause (verbatim): "the pinned mint scripts contain ZERO estimator vocabulary — the tighter two-shared-edge floor cannot reach a minted artifact this cycle under any disposition without new D-118-gated mint work"
- source: docs/decision_log.md:8482-8485
- status: D
- evidence: docs/decision_log.md:8925-8936 — "**D-133 clause 4 conditional: EXECUTE.** PR #140 (WO-MINT-ESTIMATOR-VOCAB) merged at `e11b1ad`… both floor packs re-spec to the tighter **1.869502 J** floor".
- evidence: scripts/mint_floor_artifact_generalized.py:58 — `from joulewise import floor_mint_estimator as mint_estimator`; :2441, :3989 are live estimator call sites. The stated condition ("new D-118-gated mint work") was met, so the fact is superseded by design, not violated.
- producer: n/a (finding of fact, deliberately overtaken).
- transaction_relevant: yes — describes the `_v4` mint's estimator capability.
- note: superseded by the D-133 cl.4 execution ratification, docs/decision_log.md:8925.

### D-133 cl.4 ratification · clause C7 (pack re-spec to the tighter floor)
- clause (verbatim): "both floor packs re-spec to the tighter **1.869502 J** floor (vs the 8.611855 J default) via a separate generator run + gate before FREEZE."
- source: docs/decision_log.md:8931-8933
- status: A
- evidence: configs/campaigns/d117_floor_qwen25_1p5b_v3/generate_configs.py:1493-1494 — the PRODUCER emits `"estimator": COMMON_MODE_ESTIMATOR_ID` and `"estimator_registration": two_shared_edge_common_mode_registration()` into the extraction spec cell (the sole mint authority).
- evidence: configs/campaigns/d117_floor_qwen25_1p5b_v3/calibration_plan.json — contains `d124_two_shared_edge_common_mode` (3 occurrences; same in `_7b_v3` and the contrast `_v3` pack).
- evidence: configs/campaigns/d117_floor_qwen25_1p5b_v3/arm_readiness.sources/estimator-identity.json — `check_id: estimator_registry_projection`, `status: PASS`, `derived_estimator_ids: ["d054_false_effect_guard.v1", "d124_two_shared_edge_common_mode.v1"]`, `estimator_id_derived_from_frozen_plan: true`, `cli_estimator_id_accepted: false`.
- evidence: I re-hashed all five files that evidence source pins (detection_floor.py, floor_mint_estimator.py, mint_floor_artifact_generalized.py, analysis_manifest_v3.py, the pack's calibration_plan.json) — all five match the recorded sha256 in the working tree today.
- evidence: joulewise/floor_mint_estimator.py:244-278 — mint-side registration authentication (`validate_common_mode_estimator_registration`).
- evidence (test): tests/test_detection_floor.py:841 and tests/test_floor_extraction.py:4438 — `assertEqual(round(<floor>.guarded_floor_j, 6), 1.869502)` on both the raw and governed-extraction lineages.
- producer: each pack's `configs/campaigns/*/generate_configs.py`.
- transaction_relevant: yes — this is the floor value the `_v4` mint will issue verdicts against.

### D-133 cl.4 ratification · clause C8 (paper swap)
- clause (verbatim): "The paper swap is mechanical via PR #133's merged conditional-insert block."
- source: docs/decision_log.md:8933-8934
- status: B
- evidence: TASK_QUEUE.md:266 — row `CONDITIONAL-INSERT-TIGHTER-FLOOR | P1 Phase Gate | [AGENT] | **LIVE — trigger pending** | Lead | First post-freeze mint under the frozen `d124_two_shared_edge_common_mode.v1` selector`; the block exists but is applied BY HAND ("apply the complete … replacement block in `docs/paper/draft-v1.md` as one paper-consistency transaction", "Do not apply a partial swap").
- evidence: same row — "Re-anchored 2026-08-24 (magistrate ruling…): commit c732cec's pedagogy rewrite had staled five of the six `REPLACE EXACT` anchors" — i.e. the "mechanical" block has already silently decayed once against a moving draft, and the Section 6 insert is now marked **VOID**.
- evidence: `grep -n "8.611855\|1.869502" docs/paper/draft-v1.md` returns NOTHING — both literals were removed from the paper per the B7 ruling, so the block's substitution targets no longer include those numbers.
- evidence (missing check): no script, test, or CI job references `CONDITIONAL-INSERT-TIGHTER-FLOOR`; `grep -rn "CONDITIONAL-INSERT" joulewise scripts tests .github` finds nothing outside TASK_QUEUE.md and process traces.
- producer: none found — the mint (`scripts/mint_floor_artifact_generalized.py`) produces the artifact but has no hook that flags or applies the paper swap at its trigger.
- transaction_relevant: yes — claim edge; the swap is what makes the minted floor's value true in the published prose.
- note: the missing check is at the mint/finalization producer — nothing at first-post-freeze-mint time fires the trigger or refuses a paper whose anchors have staled.

### D-133 cl.4 ratification · clause C9 (Q8 quiet-window budgets)
- clause (verbatim): "**Q8 quiet-window budgets: RATIFIED as computed.** The p256 cells are REAL new bundles (50→100 members/pack, PR #138): **~6.28 h per 1.5B pack / ~6.48 h per 7B pack, 20% margin included** — now the planning numbers for window arming."
- source: docs/decision_log.md:8937-8941
- status: B
- evidence: docs/strategy/2026-08-14-70h-plan.md:77 — "- WINDOW 1 — ALPHA (1.5B floor, ~6.28h): arm at Ed's first available tap".
- evidence: docs/strategy/2026-08-14-70h-plan.md:84 — "- WINDOW 2 — BETA (7B floor, ~6.48h): arm after ALPHA's close-out; same".
- evidence (missing check): `grep -n "budget\|hours\|duration_h" joulewise/window_duration_margins.py` returns nothing; the numbers appear nowhere in docs/phase_2/window_runbook.md, docs/process/phase2-transaction-runsheet.md, docs/process/ed-evening-checklist.md, or any pack byte. RUN_STATE.md:1682 carries them only as a historical ratification note.
- producer: none found — the pack generator that sets members/pack (100) does not derive or assert an expected wall-clock budget, and no arm-readiness row checks the arming window against it.
- transaction_relevant: yes — measurement window / arm planning.
- note: the missing check is at the pack generator (`configs/campaigns/*/generate_configs.py`) and/or `joulewise/window_duration_margins.py`; a member-count change would silently invalidate the ratified budget.

### D-124/D-133 implementation note · clause C10 (three mint dispatch sites)
- clause (verbatim): "WO-MINT-ESTIMATOR-VOCAB added per-cell v2 mint dispatch at postcollection equality, frozen artifact construction, and final evidence binding."
- source: docs/decision_log.md:8533-8535
- status: A
- evidence: scripts/mint_floor_artifact_generalized.py:2440-2455 — postcollection equality site: `recomputed = mint_estimator.recompute_comparative_estimate(...)`.
- evidence: scripts/mint_floor_artifact_generalized.py:2611-2617 — frozen-object construction from the recomputation (`V2CellRecomputation(estimator_path=recomputed.estimator_path, …)`).
- evidence: scripts/mint_floor_artifact_generalized.py:3988-3989 — final evidence binding: `mint_estimator.bind_v2_floor_artifact_evidence(...)`.
- producer: `scripts/mint_floor_artifact_generalized.py` (the `_v4` mint).
- transaction_relevant: yes — the mint itself.

### D-124/D-133 implementation note · clause C11 (identity absent downstream)
- clause (verbatim): "The sole authority is the authenticated comparative extraction-spec cell; estimator and registration identity remain absent from reports, artifacts, pinsets, and provenance."
- source: docs/decision_log.md:8535-8538
- status: A
- evidence: reports — joulewise/floor_extraction.py:1560-1566 (`validate_admitted_report_vocabulary`), called at :1607 from `validate_d117_mint_consumption_report`.
- evidence: artifacts — joulewise/detection_floor.py:4164-4172.
- evidence: pinset/labelled admissions — joulewise/floor_extraction.py:1780-1791 (`{label}: forbidden key 'estimator_registration' at …`, applied by `_strict_admission_json_file`).
- evidence: analysis provenance/manifest — joulewise/analysis_engine/inputs.py:313-317 and joulewise/analysis_engine/registry.py:225-231.
- evidence: sole authority — joulewise/floor_mint_estimator.py:244-245 reads `estimator_registration` ONLY from `spec_cell`; scripts/mint_floor_artifact_generalized.py:3476 gates on `authenticated.spec_cell.get("estimator")`.
- evidence (test): tests/test_window_duration_margins.py:412-441 — `test_gamma_estimator_registration_refuses_publicly_without_receipt` refuses a forged `contrasts[0].estimator_registration`.
- producer: `scripts/mint_floor_artifact_generalized.py` + `joulewise/floor_extraction.py`.
- transaction_relevant: yes — mint and claim edge admission profiles.

### D-124/D-133 implementation note · clause C12 (regression coverage list)
- clause (verbatim): "Regressions cover spec swaps, report-vocabulary and opposite-width mismatches, a negative control at each dispatch site, equality/U10 repair, one-ULP common-mode understatement, mixed-selector ordering, default-byte preservation, registered refusal without fallback, and no-output refusal."
- source: docs/decision_log.md:8538-8542
- status: AMBIGUOUS
- evidence: tests/test_mint_floor_artifact_generalized.py:7920-7940 — the differential/refusal matrix with per-case labels ("verdict-basis", "member-bytes", …) exists and pins exact refusal prefixes.
- evidence: tests/test_floor_mint_estimator.py and tests/test_detection_floor.py exist and were named in the F11 inventory (docs/decision_log.md:8611-8615).
- producer: n/a (test-suite obligation).
- transaction_relevant: yes — these are the `_v4` mint's regressions.
- note: AMBIGUOUS because the clause names nine coverage *themes* rather than nine named tests. I confirmed the matrices exist and that specific themes (report-vocabulary, opposite-width, evaluation-basis) are pinned, but I did not verify a distinct test for each of the nine themes; doing so needs a per-theme mapping the decision does not supply. I am not calling this A on partial evidence.

### D-124/D-133 implementation note · clause C13 (pinned-core sha)
- clause (verbatim): "At prepared integration head `a798f2bc2a33187ee8f0b7f9d5ad7836a7faca02`, the pinned core `scripts/mint_floor_artifact.py` has SHA-256 `79229aa2757f70a277c870fc50d0672d70952035f982da26ba5211eb7df8ba16`. It is byte-identical to the prepared post-#131 upstream parent `60d9e42a8204c3a117a577ddb4680fcb30814a26` and to the current `origin/main` copy."
- source: docs/decision_log.md:8546-8552
- status: D
- evidence: `shasum -a 256 scripts/mint_floor_artifact.py` today = `cc1362ce0aac6642fe2ceafd99d47ebefc5358ab7b01338c946b7711f94052e3` — the file has legitimately moved on.
- evidence: docs/decision_log.md:9472-9499 — the D-134/D-137 launcher-binding amendment (2026-08-15) added launch-lineage authentication at the mint boundary; `grep -l launch_consumption_missing` confirms scripts/mint_floor_artifact.py now carries those codes, which is why the sha changed.
- producer: n/a (a point-in-time gate fact, not a standing rule).
- transaction_relevant: yes — the pinned mint core.
- note: superseded by the D-134/D-137 launcher-binding amendment, docs/decision_log.md:9472, and its D-078 companion at docs/decision_log.md:9500. No standing artifact pins the old sha, so nothing is broken — but nothing re-pins the new one either.

### D-124/D-133 implementation note · clause C14 (F6: evaluation-basis refusal identity)
- clause (verbatim): "Component/pin gating now fires earlier, before estimator dispatch, with the exact refusal `producer[0].decode.absolute: evaluation basis sha256 mismatch`; the regression pins that complete prefix."
- source: docs/decision_log.md:8562-8566
- status: A
- evidence: scripts/mint_floor_artifact_generalized.py:1969 — `raise MintError(f"{label}: evaluation basis sha256 mismatch")`.
- evidence (test): tests/test_mint_floor_artifact_generalized.py:7924-7931 — the "verdict-basis" case asserts the regex `r"producer\[0\]\.decode\.absolute: " r"evaluation basis sha256 mismatch"`, i.e. the complete prefix as ruled.
- producer: `scripts/mint_floor_artifact_generalized.py`.
- transaction_relevant: yes — mint refusal identity.

### D-124/D-133 implementation note · clause C15 (F6: recomputation-refusal normalization)
- clause (verbatim): "At the postcollection `except ValueError` site, a spec-selected estimator selection/recomputation refusal is deliberately normalized to `postcollection_evidence_mismatch: comparative estimator recomputation refused: <original cause>`."
- source: docs/decision_log.md:8570-8574
- status: A
- evidence: scripts/mint_floor_artifact_generalized.py:2456-2460 — `except ValueError as exc: raise MintError("postcollection_evidence_mismatch: comparative estimator " f"recomputation refused: {exc}") from exc`, immediately after the `recompute_comparative_estimate` call at :2441.
- producer: `scripts/mint_floor_artifact_generalized.py`.
- transaction_relevant: yes — mint refusal identity.
- note: no regression pins this exact string — `grep -rn "estimator recomputation refused" tests` returns nothing. The clause itself asserts only the normalization (unlike C14 it does not promise a regression), so this is A on the producer, with the coverage gap recorded.

### D-124/D-133 implementation note · clause C16 (additive fail-closed refusals)
- clause (verbatim): "New common-mode refusals are additive and fail closed: exact report-width/type mismatch, frozen-object construction mismatch, and exact artifact-width/type mismatch."
- source: docs/decision_log.md:8586-8588
- status: A
- evidence: scripts/mint_floor_artifact_generalized.py:2461-2484 — report-width comparison ending in `"widths differ exactly from the authenticated spec-selected estimator"`.
- evidence: scripts/mint_floor_artifact_generalized.py:2595-2612 — `_require_postcollection_evidence_equal` over the frozen-object field list before constructing `V2CellRecomputation`.
- evidence: joulewise/floor_mint_estimator.py:330-384 — `_authenticate_mint_launch_lineage`/artifact-side equality at the binder; the binder refuses before output writing (docs/decision_log.md:8583-8584).
- producer: `scripts/mint_floor_artifact_generalized.py`.
- transaction_relevant: yes — mint.

---

### D-134 · clause 1 (two-stage receipts)
- clause (verbatim): "Readiness splits into a pack-pinned, non-authorizing FREEZE RECEIPT and an external, pack-binding ARM RECEIPT."
- source: docs/decision_log.md:8636-8637
- status: A
- evidence: joulewise/arm_readiness.py:47,52,56 — `FREEZE_RECEIPT_SCHEMA = "joulewise.arm_readiness_freeze_receipt.v1"`, `FREEZE_RECEIPT_V2_SCHEMA = "…freeze_receipt.v2"`, `ARM_RECEIPT_SCHEMA = "joulewise.arm_readiness_receipt.v1"`.
- evidence: joulewise/arm_readiness.py:2345-2349 — freeze receipt must have `receipt_kind == "freeze"` AND `arm_disposition == "NOT_APPLICABLE"` (the non-authorizing half, enforced).
- evidence: joulewise/arm_readiness.py:2404-2412 — `validate_arm_receipt` requires `receipt_kind == "arm"` and `mode == "arm"`.
- evidence: joulewise/arm_readiness.py:2442-2443 — the arm receipt carries a `freeze_receipt` reference (pack-binding, external).
- evidence: the frozen packs carry `arm_readiness.freeze.receipts/freeze-000N.json` (all nine `configs/campaigns/d117_*` packs); the arm receipts live outside the pack under the window custody root (docs/process/rehearsal-operator-card.md:104).
- producer: `joulewise/arm_readiness.py` freeze/arm generators, driven by `scripts/generate_arm_readiness.py`.
- transaction_relevant: yes — arm/arm-readiness.

### D-134 · clause 2 (hash cycle broken)
- clause (verbatim): "Frozen bytes declare the future arm-receipt schema and governed namespace — never its future path/sha value (the hash cycle is broken by declaring slots, not hashing future bytes)."
- source: docs/decision_log.md:8638-8640
- status: A
- evidence: joulewise/arm_readiness.py:4039-4051 — `plan_arm_readiness_attachment` returns exactly `{contract_id, required_before_arm, row_registry, freeze_receipt, arm_receipt_namespace, pack_digest_algorithm}` with `"arm_receipt_namespace": "arm_readiness.receipts/arm-<4+ digits>.json"` — structurally incapable of emitting an arm-receipt path or sha.
- evidence: configs/campaigns/d117_floor_qwen25_1p5b_v3/generate_configs.py:215-219 — the pack generator obtains its slot from exactly that function.
- evidence (test): tests/test_arm_readiness_registry.py:224-225 — for every profile, `serialized = json.dumps(slot, sort_keys=True); assertNotIn("arm_receipt_path", serialized); assertNotIn("arm_receipt_sha256", serialized)`.
- producer: `joulewise/arm_readiness.py::plan_arm_readiness_attachment` → `configs/campaigns/*/generate_configs.py`.
- transaction_relevant: yes — pack mint bytes + arm.

### D-134 · clause 3 (sole row authority) — **DIVERGED**
- clause (verbatim): "`d117_row_registry_v1.json` is the SOLE row authority for ALPHA, BETA, and GAMMA; Markdown matrices are checked views."
- source: docs/decision_log.md:8640-8642
- status: B
- evidence: joulewise/arm_readiness.py:88 — `ROW_REGISTRY_RELATIVE_PATH = Path("configs/arm_readiness/d117_row_registry_v2.json")` — production loads **v2**, not the ruled v1.
- evidence: tests/test_arm_readiness_schemas.py:442 — the test PINS v2: `assertEqual(readiness.ROW_REGISTRY_RELATIVE_PATH.as_posix(), "configs/arm_readiness/d117_row_registry_v2.json")`.
- evidence: docs/process_traces/2026-08-20-go-session/MAGISTRATE-RULING.md:122-131 — "**Outer id/path — RULED (Opus amendment adopted…):** outer id `d117-row-registry-v2`, path `configs/arm_readiness/d117_row_registry_v2.json`, with the ROW_REGISTRY_RELATIVE_PATH code delta (:80) in the same commit… The old v1 file STAYS IN-TREE at its current path, unreferenced, as `_v3`'s archival companion, with a test pin on its sha (d248fdc5…39a2e5)."
- evidence: `grep -n "row_registry_v2\|row-registry-v2\|2026-08-20-go-session" docs/decision_log.md` returns NOTHING. The 2026-08-20 go-session ruling that repointed the registry is **not indexed in the decision log at all**, and D-134 clause 3 still reads "v1" unamended.
- evidence: the "Markdown = checked views" half IS mechanically checked — tests/test_arm_readiness_registry.py:34-36 loads `docs/phase_2/{alpha,beta,gamma}_arm_readiness.md` and :105 `test_markdown_row_id_parity_exactly_once_for_each_profile` enforces parity against the registry.
- producer: `joulewise/arm_readiness.py::load_registry` (single-authority loader) — the mechanism is producer-side; the ruled *value* is not.
- transaction_relevant: yes — arm-readiness row authority for the `_v4` transaction.
- note: I am NOT marking this D because the brief requires a superseding decision with a `docs/decision_log.md:LINE`, and there is none — the amendment lives only in a process trace. The frozen `_v1.._v3` packs' `plan_tree.json` and freeze receipts still name v1 (e.g. configs/campaigns/d117_floor_qwen25_1p5b_v3/plan_tree.json:42), which is the *intended* archival-coordinate design per that ruling, but a reader working from the decision log alone would conclude production loads v1. **Recommend an index-row/backfill amendment of the D-154 kind (docs/decision_log.md:181 precedent).**

### D-134 · clause 4 (UNKNOWN prohibited)
- clause (verbatim): "UNKNOWN is prohibited in receipts; missing live evidence is REFUSE; NOT_APPLICABLE only by registered predicates."
- source: docs/decision_log.md:8643-8644
- status: A
- evidence: joulewise/arm_readiness.py:250-253 — the closed sets: `APPLICABILITIES = frozenset({"REQUIRED", "NOT_APPLICABLE"})`, `ROW_VERDICTS = frozenset({"PASS", "REFUSE", "NOT_APPLICABLE"})`, `ARM_DISPOSITIONS = frozenset({"GO", "NO_GO", "NOT_APPLICABLE"})`. No UNKNOWN member exists.
- evidence: joulewise/arm_readiness.py:1533-1538 — `if (item["applicability"] == "NOT_APPLICABLE") != (item["verdict"] == "NOT_APPLICABLE"): raise … "readiness_row_applicability_invalid"`.
- evidence: joulewise/arm_readiness.py:5356-5367 — `applicability_for_row` returns NOT_APPLICABLE only from registered rules (`clock_route == "HELPER"`, `successor_acceptance`), otherwise raises `readiness_row_applicability_invalid` on an unknown rule.
- evidence (test): tests/test_arm_readiness_schemas.py:1211 — `assertNotIn("UNKNOWN", READINESS_REASON_CODES)`; tests/test_arm_readiness_registry.py:113 — `test_only_registered_conditional_rules_can_be_not_applicable`.
- producer: `joulewise/arm_readiness.py` receipt generators.
- transaction_relevant: yes — arm.

### D-134 · clause 5 (receipt hygiene + assurance qualifier)
- clause (verbatim): "Exact-key, no-self-hash receipts; committed-pack verification; semantic supersession; D-120's single-authority assurance qualifier."
- source: docs/decision_log.md:8645-8646
- status: A
- evidence: exact-key — joulewise/arm_readiness.py:2405 `_require_exact_keys(value, ARM_RECEIPT_KEYS, "arm receipt")`, :2458 for dry-run, :2335 for freeze; unknown keys raise `readiness_unknown_key`.
- evidence: committed-pack verification — joulewise/arm_readiness.py:4006-4018 — the producer reads `git show HEAD:<path>` for both the receipt and its `.sha256` sidecar and raises `readiness_freeze_receipt_mismatch` if the committed bytes differ from the working tree.
- evidence: semantic supersession — joulewise/arm_readiness.py:157 `readiness_receipt_superseded`; :1375 `_validate_supersedes`; :2377, :2452 call it on freeze and arm receipts; :425 the v2 successor replaces `supersedes` with an authenticated `predecessor`.
- evidence: assurance qualifier — joulewise/arm_readiness.py:118-121 — `ASSURANCE = {"model": "single_authority_hash_bound_replay.v1", "independent_attestation": False}`.
- evidence (test): tests/test_arm_readiness_registry.py:199-216 — reads each committed freeze receipt via `git show`, re-validates it, and asserts the GNU sidecar bytes match.
- producer: `joulewise/arm_readiness.py` (freeze/arm generators), `scripts/generate_arm_readiness.py`.
- transaction_relevant: yes — arm.

### D-134 · clause 6 (derive-never-enter)
- clause (verbatim): "Derive-never-enter: every row verdict, applicability, digest, identity pin, and evidence binding is derived; operators supply paths and irreducible attestations, never conclusions."
- source: docs/decision_log.md:8647-8649
- status: D
- evidence: docs/decision_log.md:9666-9668 — "### D-134 amendment — 2026-08-15: T-0 derive-never-enter is a production ceremony, not producer attestation. This amendment supersedes D-134 clause 6…"
- producer: n/a.
- transaction_relevant: yes — arm-readiness evidence authoring.
- note: superseded by the D-134 amendment at docs/decision_log.md:9666. See clause A-T0 below for the replacement's status.

### D-134 · clause 7 (dry-run never authorizes)
- clause (verbatim): "Dry-run PASS is same-head rehearsal evidence only; it bypasses no freeze refusal and can never occupy the arm slot."
- source: docs/decision_log.md:8650-8651
- status: A
- evidence: joulewise/arm_readiness.py:57 — `DRY_RUN_RECEIPT_SCHEMA = "joulewise.arm_readiness_dry_run_receipt.v1"`; :272 the namespace regex is `dry-run-(\d{4,})\.json`, a different namespace from `arm-\d{4,}.json`.
- evidence: joulewise/arm_readiness.py:2463-2469 — `receipt_kind == "dry_run"` and `mode == "dry_run"` and `arm_disposition == "NOT_APPLICABLE"` are all required.
- evidence: joulewise/arm_readiness.py:8008-8010 — `raise …("readiness_dry_run_used_as_arm_record", "dry-run cannot be used as an arm receipt")`; :8028-8030 `"only an arm receipt may verify"`; :11243 `"dry-run cannot verify as arm authority"`.
- evidence: joulewise/arm_readiness.py:2501 — the dry-run receipt must carry the closed `omitted_live_domains` list, i.e. it declares what it did NOT check.
- producer: `joulewise/arm_readiness.py::generate_dry_run_receipt` (:7204) writes into `arm_readiness.dry_run.receipts` (:7220-7221), a namespace the arm path refuses.
- transaction_relevant: yes — arm.

### D-134 · clause 8 (ledger reservation + atomic single-launch capability)
- clause (verbatim): "A live ledger-reservation row is added, and the impossible pre-launch \"single foreground launch\" row is replaced by an atomically consumable single-launch capability (exactly one consumer succeeds; replay and stale predecessors refuse)."
- source: docs/decision_log.md:8652-8655
- status: A
- evidence: joulewise/arm_readiness.py:937 — predicate `t0.ledger_reservation.v1`; :1012 kind `LEDGER_RESERVATION`; :5991-5992 row `t0.ledger_reservation` → refusal `readiness_ledger_preflight_refused`; emitted at :7261.
- evidence: joulewise/arm_readiness.py:970 — predicate `t0.single_launch_capability.v1`; :1018 kind `LAUNCH_RECIPE`; :5993-5994 row `t0.single_launch_capability` → `readiness_launch_capability_unavailable`, emitted at :7487-7489.
- evidence: joulewise/arm_readiness.py:4794 — the atomic primary: `descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)` — no-clobber create is the linearization point.
- evidence: joulewise/arm_readiness.py:8094 and :9057 — `raise …("readiness_record_consumed", "launch capability was already consumed")` (replay refusal).
- evidence (test): tests/test_launch_window.py:77 — `test_eight_launchers_make_one_claim_and_one_execve`; :136 `test_anonymous_fd_handoff_is_one_use`.
- producer: `joulewise/arm_readiness.py::_consume_launch_capability` (:8852), reached only from `scripts/launch_window.py::launch`.
- transaction_relevant: yes — arm → window launch.

### D-134 · clause 9 (enumerated doctrine amendments)
- clause (verbatim): "The enumerated live doctrine is amended (runbook §5C/§5A, D-117 attachment-slot clarification, refusal-registry amendment, operator packet ARM sequence, 40h-plan B2/B5, state-kernel fence wording); historical process traces are preserved and superseded by decision, never edited in place."
- source: docs/decision_log.md:8656-8659
- status: AMBIGUOUS
- evidence: runbook §5C — docs/phase_2/window_runbook.md:759 "## 5C. D-117 manual arming and quiet handoff (cold-gate ruling 2026-08-08)"; :618-622 "Do **not** hand-count a settle here. §5C removed the separate pre-launch…"; :1293 "The six §5C wrapper calls are the sole live execution route".
- evidence: attachment slot — joulewise/arm_readiness.py:4039-4051 (clause 2 above), `contract_id = "D-134"` asserted at tests/test_arm_readiness_registry.py:174.
- evidence: refusal-registry amendment — docs/decision_log.md:8733-8784 (the 46-code block), verified at clause A-D078 below.
- evidence: operator packet ARM sequence — docs/process/rehearsal-operator-card.md:93-110 (E-9b → ARM → verify → consume, with the literal commands).
- evidence: state-kernel fences — docs/process/state_kernel.json:58,90,132,… `"fences": [...]` arrays exist.
- producer: documents (hand-authored).
- transaction_relevant: yes — the live arm ceremony doctrine.
- note: AMBIGUOUS. Five of the six named surfaces show amended text I read. I could NOT locate a "40h-plan" document (`docs/strategy/` carries a **70h** plan, `docs/strategy/2026-08-14-70h-plan.md`) — the 40h plan appears to have been replaced rather than amended, so its "B2/B5" items are unverifiable at the named artifact. Also, none of these six doctrine surfaces has a mechanical check that they stay amended; they are prose.

### D-134 · clause 10 (test obligations bind before any arm)
- clause (verbatim): "The full mutation/lifecycle/namespace/replay/U11-integration/three-profile test obligations bind before any D-117 arm."
- source: docs/decision_log.md:8660-8661
- status: A
- evidence: lifecycle — tests/test_arm_readiness_lifecycle.py exists; :790, :817, :964 exercise consumption/replay/lock outcomes.
- evidence: namespace/replay — tests/test_arm_readiness_registry.py:185-188 asserts the arm-receipt namespace value/regex; tests/test_launch_window.py:136 `test_anonymous_fd_handoff_is_one_use`, :144 `test_direct_chain_entry_without_inherited_fd_refuses`.
- evidence: U11 integration — tests/test_arm_readiness_integration.py:186 "synthetic U11 receipt already exists", :404 `IdentityPinProjectionError(code, "synthetic U11 refusal")`.
- evidence: three-profile — tests/test_arm_readiness_registry.py:34-36 (`PROFILES` = ALPHA/BETA/GAMMA markdown) and :140-235, which loops `for profile, pack_name in PACKS.items()` over all three.
- evidence: mutation — docs/council_log.md:3512 records "lens B's mutation census killed 21 of 25 with 4 regression gaps" and the fix round; there is no standalone `tests/test_*mutation*.py`, the census being a delegated review artifact rather than a committed suite.
- producer: n/a (test-suite obligation).
- transaction_relevant: yes — gates the arm.

### D-134 · clause 11 (sole production entrypoint) — first half
- clause (verbatim): "The sole production entrypoint performs consume → revalidate → `execve`"
- source: docs/decision_log.md:9484-9485
- status: A
- evidence: scripts/launch_window.py:237-264 — `launch()` does `_install_handoff(token)` → `_consume_launch_capability(...)` → `verify_consumed_launch(...)` → argv equality check → `os.execve(argv[0], argv, dict(os.environ))`, with `raise LaunchLineageError("launch_consumption_invalid", "execve returned after consuming the launch")` behind it.
- evidence: scripts/generate_arm_readiness.py:151 — the retired standalone `consume` verb points at "scripts/launch_window.py for the reviewed consume-to-exec route".
- evidence (test): tests/test_launch_window.py:395-420 — `test_standalone_consume_cli_is_retired_with_launcher_guidance` asserts exit 2, `reason_codes == ["readiness_usage_invalid"]`, and that the detail names `scripts/launch_window.py`.
- evidence (test): tests/test_launch_window.py:325 `test_honest_launcher_consumes_verifies_and_reaches_execve`; :171 `test_execve_failure_is_one_burned_attempt_without_retry`.
- producer: `scripts/launch_window.py::launch`.
- transaction_relevant: yes — window launch.

### D-134 · clause 11 (Ed invokes personally) — second half
- clause (verbatim): "Ed invokes it personally after inspecting ARM `PASS`/`GO`, and no automated verdict invokes it."
- source: docs/decision_log.md:9485-9486
- status: B
- evidence: docs/process/rehearsal-operator-card.md:110 — the literal single `scripts/launch_window.py …` command Ed types; :95 "proceed immediately to ARM, verify, Ed inspection, then the one launcher invocation"; :15 "E-9a/E-9b/ARM/verify/E-10 | ED-FIRST".
- evidence (missing check): `grep -rn "launch_window.py" scripts joulewise .github configs docs/process` finds only scripts/generate_arm_readiness.py:151 (a guidance string) and the operator card — so no automated caller exists **today**, but nothing refuses one tomorrow.
- evidence: the decision itself concedes the gap — docs/decision_log.md:9476 "Python does not authenticate its caller." and :9477-9479 "The atomic no-clobber primary is the single-use enforcement. The consumption receipt alone does not prove a launch."
- producer: none found — `scripts/launch_window.py::launch` has no operator-identity or interactivity check.
- transaction_relevant: yes — window launch authorization.
- note: the missing check is at `scripts/launch_window.py::launch`. This is an accepted, decision-stated ceremony limitation rather than an oversight, but it is a B by the brief's definition: doctrine + operator card only, no producer-side refusal.

### D-134 · clause 12 (consumption irrevocable, append-only)
- clause (verbatim): "Consumption is irrevocable. Start, settle, and completion are append-only successor receipts; absence or any post-claim failure never reopens the capability."
- source: docs/decision_log.md:9487-9489
- status: A
- evidence: joulewise/arm_readiness.py:4794 — `os.O_CREAT | os.O_EXCL` write; a second write to the same path cannot succeed.
- evidence: joulewise/arm_readiness.py:9528, :9538 — `start` and `settle` validated with `missing_code="launch_lifecycle_incomplete"`; :9626-9629 `raise LaunchLineageError("launch_lifecycle_incomplete", "launch completion receipt is absent")`.
- evidence: joulewise/arm_readiness.py:9631-9638 — completion must chain: `completion["predecessor"] != settle_ref or completion["consumption"] != consumption_ref or completion["issued_at_monotonic_ns"] < settle["issued_at_monotonic_ns"]` → `launch_consumption_invalid`, "completion receipt predecessor/order differs".
- evidence: joulewise/arm_readiness.py:8094, :9057 — a re-consume attempt gets `readiness_record_consumed`, never a reopened capability.
- evidence: scripts/launch_window.py:262-266 — "Successful execve never returns. There is deliberately no child process, wait path, or automatic retry after the capability's linearization point."
- evidence (test): tests/test_launch_window.py:171 `test_execve_failure_is_one_burned_attempt_without_retry`.
- producer: `joulewise/arm_readiness.py::_consume_launch_capability`.
- transaction_relevant: yes — window launch.

### D-134 · clause 13 (five downstream stages authenticate lineage)
- clause (verbatim): "Collection, post-hoc reduction, whole-window verdict, extraction, and mint independently authenticate launch lineage using the D-078 vocabulary registered below."
- source: docs/decision_log.md:9490-9493
- status: A
- evidence: collection — joulewise/bundle.py:49-50,87-147 — `_writer_launch_lineage` calls `authenticate_campaign_launch_lineage`, gated by `launch_lineage_required(config.to_dict())`; :1056-1062 refuses caller-supplied `launch_lineage` ("launch_lineage is writer-owned and cannot be caller supplied"). Also scripts/run_campaign.py.
- evidence: post-hoc reduction — joulewise/cli.py:1845-1849 — `_cmd_reduce` calls `authenticate_bundle_launch_lineage(bundle_path, require_completion=False)` and returns exit 2 on `LaunchLineageError` BEFORE reducing.
- evidence: whole-window verdict — joulewise/whole_window.py:33-34, and `authenticate_window_launch_lineage` defined at whole_window.py:2489.
- evidence: extraction — joulewise/floor_extraction.py:75 imports `authenticate_bundle_launch_lineage`; :1442, :1511 admit `launch_lineage` as a member key; :1627-1631 type-refuses it.
- evidence: mint — joulewise/floor_mint_estimator.py:27, :330-384 `_authenticate_mint_launch_lineage`, with `"launch_lineage_conflict: copied extraction lineage differs from …"` at :376.
- evidence (test): tests/test_launch_window.py:1204 `test_analysis_input_refuses_missing_launch_consumption`, :1215 `test_whole_window_refuses_missing_launch_consumption`, :1223 `test_floor_extraction_refuses_missing_launch_consumption`, :1238 `test_malformed_and_mismatched_lineage_codes_reach_every_consumer`, :1287 `test_mixed_valid_consumptions_refuse_at_aggregate_boundary`.
- producer: each stage's own writer (bundle.py, cli.py, whole_window.py, floor_extraction.py, floor_mint_estimator.py).
- transaction_relevant: yes — the whole consumption edge.

### D-134 · clause 14 (release-gate test classes)
- clause (verbatim): "Crash injection, race, ceremony-bypass, mutation, and every-downstream-stage tests are release gates for this mechanism."
- source: docs/decision_log.md:9494-9495
- status: A
- evidence: race — tests/test_launch_window.py:77 `test_eight_launchers_make_one_claim_and_one_execve`.
- evidence: crash injection — tests/test_launch_window.py:171 `test_execve_failure_is_one_burned_attempt_without_retry`.
- evidence: ceremony bypass — tests/test_launch_window.py:144 `test_direct_chain_entry_without_inherited_fd_refuses`; :395 the retired standalone consume CLI.
- evidence: every-downstream-stage — tests/test_launch_window.py:1204-1300 (see clause 13).
- evidence: mutation — tests/test_arm_readiness.py and tests/test_arm_readiness_lifecycle.py carry the mutation/crash vocabulary; the mutation census itself is custodied as a review artifact (docs/council_log.md:3512), not a committed suite.
- producer: n/a (test-suite obligation).
- transaction_relevant: yes — window launch.

---

### D-078 registry amendment (2026-08-12) · clause A-D078a (the closed 46)
- clause (verbatim): "The readiness layer owns the following closed 46-code vocabulary. The type labels are `STRUCTURE`, `CUSTODY`, `GIT`, `LIFECYCLE`, `POLICY`, `IDENTITY`, and `ENVIRONMENT`; upstream evidence receipts retain their own closed detail codes."
- source: docs/decision_log.md:8733-8737 (list at 8738-8781)
- status: A
- evidence: I extracted all 46 spellings from the decision text and searched the tree: 44 appear literally in joulewise/arm_readiness.py; the remaining two (`readiness_identity_projection_mint_divergence`, `readiness_identity_receipt_namespace_anomalous`) appear in joulewise/identity_pins.py:42,44 and joulewise/arm_readiness_evidence.py:2039-2040 — consistent with the decision's own note that the IDENTITY block "is imported unchanged from the D-131 identity-pin projection decision."
- evidence: joulewise/arm_readiness.py:123-230 — the seven typed frozensets `STRUCTURE_REASON_CODES`, `CUSTODY_REASON_CODES`, `GIT_REASON_CODES`, … exactly matching the seven ruled type labels.
- evidence (test): tests/test_arm_readiness_schemas.py:482 references `readiness.READINESS_REASON_CODES`; :1209 `assertEqual(len(READINESS_REASON_CODES), 55)` — the closed set has since grown from 46 to 55 by later additive amendments (e.g. `readiness_successor_chain_invalid` at :1190), and the count is pinned so growth cannot be silent.
- producer: `joulewise/arm_readiness.py` — every refusal raises with a code drawn from these sets.
- transaction_relevant: yes — arm-readiness refusal vocabulary.

### D-078 registry amendment (2026-08-12) · clause A-D078b (lock unreachability pinned)
- clause (verbatim): "`readiness_lock_unavailable` is defensive forward-compatibility and is currently unreachable on the atomic-consume path, which acquires no lock: every race loser receives `readiness_record_consumed`. A test pins that unreachability so any future emission is a loud contract change rather than a silent one."
- source: docs/decision_log.md:8761-8767
- status: A
- evidence: tests/test_arm_readiness_lifecycle.py:790 — `self.assertNotIn("readiness_lock_unavailable", outcomes)`.
- evidence: tests/test_arm_readiness_lifecycle.py:817 — `self.assertNotEqual(replay.exception.reason_code, "readiness_lock_unavailable")`.
- evidence: joulewise/arm_readiness.py:4794 — the consume path uses `O_CREAT|O_EXCL` and acquires no lock, as the clause states; :8094/:9057 give the race loser `readiness_record_consumed`.
- producer: `joulewise/arm_readiness.py::_consume_launch_capability`.
- transaction_relevant: yes — arm/launch.

### D-078 registry amendment (2026-08-12) · clause A-D078c (nothing licenses ARM)
- clause (verbatim): "Every one of these 46 spellings only refuses. No readiness code, type label, `PASS`, `GO`, `READY`, `clean`, or `ready` licenses ARM, physical launch, or a scientific claim. This amendment composes with D-120's unchanged single-authority assurance qualifier; it does not add an independent witness."
- source: docs/decision_log.md:8779-8784
- status: A
- evidence: tests/test_arm_readiness_schemas.py:1210 — `self.assertNotIn("GO", READINESS_REASON_CODES)`; :1211 `assertNotIn("UNKNOWN", …)`; :1216 `assertNotIn("clock_probe_failed", …)` (keeps upstream detail codes out of the readiness set, as ruled).
- evidence: joulewise/arm_readiness.py:118-121 — `ASSURANCE = {"model": "single_authority_hash_bound_replay.v1", "independent_attestation": False}` — the D-120 qualifier, explicitly declaring no independent witness.
- producer: `joulewise/arm_readiness.py`.
- transaction_relevant: yes — arm authorization semantics.

### D-078 registry amendment (2026-08-15, launch-consumption) · clause A-D078d
- clause (verbatim): "The following six exact spellings are registered at collection, post-hoc reduction, bound derivation, whole-window verdict, extraction, and mint boundaries; no synonym, generic provenance downgrade, or latest-wins interpretation is permitted"
- source: docs/decision_log.md:9503-9506 (list at 9508-9521)
- status: A
- evidence: all six spellings exist in code — `launch_consumption_missing` (joulewise/{floor_mint_estimator,whole_window,arm_readiness}.py, scripts/{launch_window,validate_powermetrics_fiducial,mint_floor_artifact}.py); `launch_consumption_invalid`; `launch_binding_mismatch`; `launch_lineage_conflict`; `launch_lifecycle_incomplete` (joulewise/arm_readiness.py:212,9092,9528,9538,9616,9629); `launch_handoff_invalid` (scripts/launch_window.py:212,253,258).
- evidence: joulewise/arm_readiness.py:9626-9629 — the ruled semantics ("completion is absent at verdict, extraction, or mint") is enforced by `require_completion` + `launch_lifecycle_incomplete`; the per-stage callers reach it through `authenticate_window_launch_lineage` (joulewise/whole_window.py:2489) and `authenticate_bundle_launch_lineage` (joulewise/arm_readiness.py:9902).
- evidence (test): tests/test_launch_window.py:1238 `test_malformed_and_mismatched_lineage_codes_reach_every_consumer` — the "reach every consumer" obligation is a named regression.
- producer: `joulewise/arm_readiness.py::authenticate_launch_lineage` (:9385) and its per-stage wrappers.
- transaction_relevant: yes — consumption edge and claim edge.

### D-134 amendment 2026-08-15 (T-0) · clause A-T0a (honest contract)
- clause (verbatim): "Derive-never-enter is a production-interface and ceremony rule, not independent producer attestation. When faithfully invoked, the production CLI derives row values, command captures, timestamps, identities, and digests; operators supply only paths and the registered irreducible observations (at E-4, exactly two: the independent-clock UTC literal and the pasted prior network-time state output)."
- source: docs/decision_log.md:9670-9678
- status: A
- evidence: scripts/capture_t0_step.py:7-10 — the module docstring states exactly this: "registered irreducible observations (the independent-clock UTC literal and the pasted prior network-time state output). v1 does not defend against …".
- evidence: scripts/capture_t0_step.py:1029-1032 — the ENTIRE CLI surface is `step_id` + `--pack-root` + `--custody-root` + `--window-plan-root`: paths only. There is no clock-injection or execution-injection parameter, matching the amendment's "Removing production clock and execution injection parameters".
- evidence: scripts/capture_t0_step.py:46,51 — the two operator inputs are namespaced as `network-time-prior-state` / "Paste Ed's exact interactive prior network-time output"; :781-803 refuse when it is absent or inexact.
- evidence: scripts/author_arm_readiness_evidence.py:29-31 — "The authoring CLI keeps the ruled --pack-root-only surface" — `parser.add_argument("--pack-root", required=True, type=Path)` is the only argument.
- evidence: joulewise/arm_readiness_evidence_t0.py:516-551 — the independent-clock attestation is schema-checked, staleness-checked, and skew-checked (`f"independent clocks differ by {difference:.6f} seconds"`), i.e. the irreducible observation is bounded, not trusted blind.
- producer: `scripts/capture_t0_step.py` + `joulewise/arm_readiness_evidence_t0.py`.
- transaction_relevant: yes — arm-readiness T-0 evidence.

### D-134 amendment 2026-08-15 (T-0) · clause A-T0b (registered limitation)
- clause (verbatim): "**REGISTERED LIMITATION (v1):** T-0 capture provenance is TRUSTED-OPERATOR — deliberate fabrication by the operator is not defended against; the real binding to a real quiet window is the human §5A tap + the terminal-review attestation + the single-operator assumption, all STATED as the limitation."
- source: docs/decision_log.md:9688-9692
- status: A
- evidence: docs/phase_2/window_runbook.md:976 — "**TRUSTED-OPERATOR**: deliberate operator fabrication is not defended".
- evidence: docs/phase_2/window_runbook.md:1077 — "record of the trusted-operator ceremony, not mechanically independent".
- evidence: scripts/capture_t0_step.py:9 — "v1 does not defend against …" in the tool's own docstring.
- evidence: docs/decision_log.md:171 (D-148 cl.6) — "the risk-appetite family (recorder race / T-0 capture provenance / hostile same-UID injection / forged launch-context) is ACCEPTED AS REGISTERED LIMITATIONS".
- producer: docs/phase_2/window_runbook.md + scripts/capture_t0_step.py docstring.
- transaction_relevant: yes — the claim edge inherits this limitation.
- note: the limitation is stated in the runbook and the tool, and ratified by D-148 cl.6. I did NOT find it stated in `docs/paper/draft-v1.md`; the amendment says "all STATED as the limitation" without naming the paper, so I read the runbook+tool as satisfying it. If the intent was paper-side, this becomes a C at the paper.

### D-134 amendment 2026-08-15 (T-0) · clause A-T0c (the removed overclaim)
- clause (verbatim): "The previously claimed property that a human cannot hand-produce acceptable historical T-0 capture bytes is **NOT enforced**. Removing production clock and execution injection parameters is misuse resistance, not a security boundary or independent proof of producer origin."
- source: docs/decision_log.md:9683-9687
- status: A
- evidence: scripts/capture_t0_step.py:1029-1032 — the injection parameters are gone (four path-only arguments; see A-T0a).
- evidence: joulewise/arm_readiness_evidence_t0.py:885 — `"OPERATOR_ATTESTATION"` still appears as a declared evidence source, i.e. the code does NOT pretend operator origin is proven — consistent with the amendment's honest posture (and with docs/council_log.md:3488, which records the original forgery finding this amendment answers).
- producer: `scripts/capture_t0_step.py`.
- transaction_relevant: yes — arm-readiness T-0 evidence.
