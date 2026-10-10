CONTAMINATION DISCLOSURE: before this charge, this session had read nothing about this project by my own action; the harness injected the two CLAUDE.md files (global and the worktree's) and the auto-memory index MEMORY.md (one-line pointers only, no memory bodies) into the system prompt. I opened no RUN_STATE.md, docs/orchestration.md, decision log, memory file or doctrine during the pass. Read for the pass: ERRATUM.md sections 1 to 6, the `order`/`precede` lines of RULING.md (grep only), the diff 224a264c5..d435547e2, harvest.py, whole_window.py, campaign_provenance.py, window_lineage.py, run_campaign.py and registration lines 4118 to 4130, the four test files, sol-fix.md (first 120 lines) and sol-fix2.md. No blinded root was opened or listed; the only real data touched was the open rehearsal archive under gate-prune/ (recorded-source window), through the implementer's comparison test.

# Cold pass (Fable 5.1) on d435547e2 against Erratum 2, sections 4 and 5

Working directory read-only; probes ran on copies under /Users/edr/.jwtmp/fable-pass/ (repo, repo2). Structure only below: no energy, power, duration or member name.

## Executed

| Probe | Result |
|---|---|
| Epoch arithmetic: `datetime(2026,10,10,16,30,tzinfo=UTC).timestamp()` and the inverse | 1791649800 ↔ 2026-10-10T16:30:00+00:00, matches harvest.py:87-88 |
| `tests.test_harvest_b5_sources` from the working directory | 51 tests OK (1.2 s) |
| Same module from the scratch copy (baseline for mutants) | 51 tests OK |
| `tests.test_harvest_b5_rehearsal_compare` with B5_REHEARSAL_COMPARE=1, from the second scratch copy, against the open rehearsal archive (verdict records 9 sources) | 1 test OK; derived byte identity, withheld byte identity, emitted flags equal, archived derived identity all PASS; 4 derived records, 7 recorded reductions |
| 20 mutation probes (table below) | 19 killed, 1 survived (F1) |
| Real plan structure (rehearsal plan, not blinded): top-level `t0_epoch_s` present, int | gate reachable on real plans; that plan is ungoverned as expected |

NOT EXECUTED: anything over a governed or blinded window (forbidden); the whole suite (forbidden); a real-bytes check that the runner's manifest `role`/`sentinel_position` spellings resolve through `_neg8_position` to the roster's `neg8_slot`/`spare_slot` strings (blinded; relied on by the worked example and shown on the rehearsal's recorded-source manifests, which evaluated).

## Findings

No BLOCKER found.

**F1 SHOULD-FIX (test asserts too little, item 5).** tests/test_harvest_b5_sources.py:181 (`harvest()` always sets `run.neg8_clean_bound_required = True`), used by `test_recovery_requires_a_clean_bound` (line 381) and `test_missing_clean_bound_disclosure_is_exact` (line 615). Mutant M13 removed the recovery clause at harvest.py:5418 (`if bound is None and (recovery or getattr(self, "neg8_clean_bound_required", False))` → `if bound is None and getattr(...)`) and the module stayed OK, because the fixture's always-on flag forces the clean bound anyway. The program is correct as written: the clause matters exactly when `neg8_corpus_physics` returns early (harvest.py:5578-5582, in-window bound underived or not a mapping), where the flag stays False; in that case the mutant would fall to the `elif` at 5421-5426 and name `collected_bound_unavailable` instead of `clean_bound_unavailable` (no other bound exists there, so no screen could pass). Minimal fix (test only): in both tests set `run.neg8_clean_bound_required = False` and `run.neg8_collected_bound = self.bound` before `cannot_run(...)`, so only item 5's own clause can produce `clean_bound_unavailable`.

**N1 NOTE (word precedence, item 1 vs item 0(d)-(f)).** harvest.py:1197-1203 authenticates the catalog (item 1) between 0(c) and 0(d) (1207-1217), so a root where the catalog does not authenticate and 0(d) would also fail reports `source_manifest_unauthenticated`, not `no_absent_invoked_member`. The text orders 0(b)-(f) among themselves and does not fix item 1's place relative to them; (d)-(f) need the members, which the implementer takes from the authenticated catalog. Both outcomes are "cannot run".

**N2 NOTE (word precedence, item 7(b) vs items 2 and 3).** harvest.py:1224 checks `evaluation_basis_invalid` before the per-manifest path/policy/members checks (1229-1241) and the roster check (1243-1253). Word only; every branch is "cannot run".

**N3 NOTE (item 0(a) read narrowly).** harvest.py:5219-5220 enters the recovery for an absent key, a non-mapping `row_provenance`, or an empty list. A present `null` or non-list value goes to `verdict_neg8_sources` (1130-1131), which returns `source_manifests_unrecorded` with no `campaign_sources_problem` key and no recovery. The text's parenthetical ("the pinned program's problem `source_manifests_unrecorded`") covers that value too; the implementer's reading is the stricter one and `test_malformed_present_source_list_never_enters_recovery` encodes it. The sealed writer writes a list (run_campaign.py:8122, 8590), so no real verdict reaches this branch.

**N4 NOTE (stricter than item 3, whole_window.py:4985-4992).** With `require_replicated_endpoints`, an invoked member whose role resolves to no position is marked `invalid_role` (screen failed, `neg8_bracket_reference_invalid`) when its role starts with `neg8_daily_reference`, or it carries a `sentinel_position`, or its run id / bundle id is a roster reference id (the `required_reference_ids` set built at harvest.py:5469-5474). Item 3 defines a reference by `_neg8_position` and says members resolving to none of the three positions are invalid "as today"; today `None` is skipped (a science member). The extension cannot pass a drifting window; it can only fail a window whose manifest mislabels a planned reference, which the text would instead count as a lost reference. Covered by `test_roster_reference_with_unrecognized_role_fails_the_screen`.

**N5 NOTE (item 8, words outside the closed list).** harvest.py:5506-5512 copies `problems[0]` into `campaign_sources_problem`. On the recovery path that word can be `rederivation_failed:<x>` (evaluator problems the text does not enumerate, e.g. `provenance` from the scientific-identity check at whole_window.py:5102-5111), `rederivation_raised:<Exception>`, `rederivation_invalid`, or `evaluation_time_unrecorded` (5437). Each is "cannot run" as today. Separately, if `claim_neg8_sources` raises inside `_neg8_reference_losses` (5140-5144) the source object is `{"source": "claim_campaign_manifests_unauthenticated", "verdict_sources_problem": "sources_raised:<Exc>"}` with no `campaign_sources_problem` key; the screen still cannot run (the second call in `_neg8_rescreen` raises again into `rederivation_raised`).

**N6 NOTE (rehearsal comparison is opt-in).** tests/test_harvest_b5_rehearsal_compare.py:44 skips without `B5_REHEARSAL_COMPARE=1`, so a plain suite or CI run reports a skip, not a pass; the pin's gate record must cite an executed run. Executed here: PASS. It compares what it claims: the three NEG-8 stages (`neg8_corpus_physics`, `neg8_screen`, `neg8_allowance`) under the pinned and working modules over the same read-only copy, all written bytes (derived and withheld) and all emitted flags, plus the derived bytes against the archive; it asserts the screen evaluated and passed and that recorded reductions were replayed, so it cannot pass vacuously when run. The diff's reach outside those stages is `_derived_neg8_decision`'s three new keyword arguments, whose defaults leave every other caller (the row validator) unchanged (whole_window.py:4881-4883, 4985, 5098, 5223).

**N7 NOTE (item 0(c) by prefix).** harvest.py:1195 matches refusal reasons by the prefix `campaign_occurrence_`. The writer's refusal reasons are the three `campaign_occurrence_supersession_*` constants (whole_window.py:110-118, run_campaign.py:7615), carried into `idle_admission_core.conditions` at run_campaign.py:8496-8499; no other writer condition has the prefix. Exact.

## Item-by-item verification against the admitted text

- **Gate (section 5).** Constants harvest.py:87-88 verified. `_neg8_sources` (5217-5235): 0(a) at 5219-5220, then the clock at 5222-5227 (bool, non-number, non-finite, missing plan and `t0 <= epoch` all → `recovery_predates_erratum`; strict `>` required to pass), then `claim_neg8_sources`, whose first check is 0(b) (1190). `claim_neg8_sources` has one call site (5229) and no caller in scripts/. An ungoverned attempt cannot reach the recovery; the test with hazard-root False and `t0 == epoch` returns the gate word (`test_ungoverned_t0_discloses_cannot_run`), and M2 (gate deleted) fails 12 cases.
- **0(b)-(f).** 1190, 1192-1196, 1207-1217, in the text's order among themselves; (d) and (e) use `ordinary_present_bundle_paths`; (f) uses `_is_recognizable_occurrence_supersession` over the raw log rows (a row with no bundle id counts, as the text's "no occurrence-supersession row" requires).
- **1.** `load_authenticated_campaign_catalog` None → `source_manifest_unauthenticated`; empty → `source_manifests_unrecorded`; any non-v2 → `source_manifest_schema_v1` (1197-1203).
- **2.** `policy_unregistered` 1219-1222; per manifest `source_manifest_path_invalid`, `source_manifest_policy_differs`, `source_manifest_members_invalid` (occurrence duplicates within and across manifests, unsafe ids, member wire) 1229-1241.
- **3.** Roster check 1243-1253: every invoked member with a resolved position must have `(run_id, position)` and every `(bundle_id, position)` in the roster's `neg8_slot`/`spare_slot` pairs. Non-invoked members skipped here and in the evaluator (whole_window.py:4976-4977).
- **4.** `bundle_absent` from `runs_root / <id>` `.is_dir()` on the manifest-named references only, overriding every other reason (5157-5158, 5210-5212). In the evaluator the harvest's losses are read first (`excluded[bundle_id]`, 5040-5050), then `summary_unreadable`, `status_not_succeeded`, `strict_invalid` (triangle or the harvest's `members[...].strict_valid is False` callback), then `energy_unreadable`; a lost reference `continue`s before 7(b) and before any energy read (5089-5131). M12 and M20 confirm the losses reach the evaluator.
- **5.** 5418-5420: recovery with no clean bound → `clean_bound_unavailable`; the `elif` that reaches the collected bound and the stored bracket's bound (5421-5426) is unreachable while `recovery` is true. (Test gap F1.)
- **6.** 5476-5480: `current=True` (from `claim_neg8_sources`), `point_drift=True`, `drift_bound_artifact=bound` (clean), `exclude_bundle_ids=dict(exclude)`, `unreadable_energy="lost"`, `require_replicated_endpoints=True`. Endpoint minimum override whole_window.py:5223-5234 with realised counts, planned {3,1,3}, losses, `midpoint_lost = not references["midpoint"]`, `references_insufficient`; the legacy pair (`legacy_pair` at 5169, requires no loss) is caught by the same override (M14; `test_legacy_pair_cannot_pass_catalog_recovery`). Excess references and an exceeded statistic remain the evaluator's own conditions (tests at lines 327, 335).
- **7.** (a) item 1; (b) `_neg8_basis_reference_check` 5244-5266 on survivors only, fresh SHA-256 of the three files against `config_sha256`/`metadata_sha256`/`summary_sha256` of the validated basis's `member_occurrences`, invoked at whole_window.py:5098-5101 after every loss test and before the energy read; `reference_not_in_verdict_basis` and `evaluation_basis_invalid` pass through unprefixed (5484-5487); (c) item 3. The stored bracket: `_neg8_reproduces` skipped (5490), `stored_strict_losses` not passed on the catalog call (5466-5467), no second `rederive` (5495), stored conditions ignored (`conditions_beyond_bound_underived` suppressed at 5415; `test_stored_neg8_conditions_decide_nothing_on_recovery`).
- **8.** Objects and keys exact in `rescreen.reference_source` (5506-5512), `observed.reference_source` of `neg8.screen_failed` (5053-5056), and `reference_source` beside `source` in neg8-allowance.json (5085-5089); the `cannot_run` helper (test line 456) and `test_recovery_disclosure_in_allowance_is_exact` check all three. `neg8.reference_lost` names an absent spare `bundle_absent` with `spares_measured []`, `spares_succeeded []` (`_neg8_lost_rows` 5277-5316; `test_absent_spare_reason_and_retry_counts`).
- **Unchanged.** Recorded sources: `_neg8_sources` else-branch (5236-5240) is the pinned selection and the pinned source object; `recovery`/`catalog_rescreen` are false so every new branch in `neg8_screen`, `_neg8_rescreen`, `neg8_allowance` and `_neg8_reference_losses` (`absent = set()`) is inert; the evaluator's new keywords default off. Verified by the executed rehearsal comparison, by `test_recorded_sources_are_byte_identical_to_the_sealed_harvest`, and by M17 (widening 0(a) to every row breaks five tests including both byte-identity tests). Recorded sources that do not authenticate: same else-branch, `test_recorded_unauthenticated_sources_and_missing_bound_are_byte_identical`.
- **Item 9.** Not in this change, as charged.

## Mutation probes (module `tests.test_harvest_b5_sources`, 51 tests, baseline OK)

| Id | File:line mutated | Mutation | Result |
|---|---|---|---|
| M1 | harvest.py:5226 | `t0 <= EPOCH` → `t0 < EPOCH` | FAILED: test_program_gate_constants_and_order, test_ungoverned_t0_discloses_cannot_run |
| M2 | harvest.py:5222-5229 | gate deleted, `claim_neg8_sources` always called | FAILED (12): same two tests |
| M3 | harvest.py:1190-1191 | 0(b) hazard check deleted | FAILED: test_non_hazard_root_is_first_item_zero_failure |
| M4 | harvest.py:1193 | 0(c) `_ambiguous` clause deleted | FAILED: test_stored_membership_must_be_unresolved_without_ambiguity_or_refusal |
| M5 | harvest.py:1195 | 0(c) refusal-reason clause deleted | FAILED: same test |
| M6 | harvest.py:1208-1209 | 0(d) deleted | FAILED: test_no_absent_invoked_member_precedes_ambiguity_and_supersession |
| M7 | harvest.py:1210-1211 | 0(e) deleted | FAILED: test_ambiguous_second_directory_precedes_supersession |
| M8 | harvest.py:1215-1216 | 0(f) deleted | FAILED: test_occurrence_supersession_row_even_without_id_blocks_recovery |
| M9 | harvest.py:1201-1202 | item 1 schema-v2 check deleted | FAILED: test_v1_manifest_cannot_supply_recovery, test_all_v1_catalog_without_log_is_schema_v1 |
| M10 | harvest.py:1253 | item 3 `return "reference_not_in_roster"` → pass | FAILED: test_reference_outside_roster_or_at_wrong_slot_cannot_run |
| M11 | whole_window.py:5098 | item 7(b) survivor check disabled | FAILED: test_surviving_reference_outside_basis_cannot_run, test_survivor_hash_mismatch_against_valid_basis_cannot_run |
| M12 | harvest.py:5212 | item 4 `bundle_absent` loss removed | FAILED (2 failures, 1 error): test_absent_spare_reason_and_retry_counts, test_bundleless_spare_and_empty_sources_screen_survivors, test_roleless_evaluation_basis_does_not_erase_failed_and_absent_references |
| M13 | harvest.py:5418 | item 5 `recovery or` removed | **OK (survived)** → F1 |
| M14 | whole_window.py:5223 | item 6 endpoint-minimum override disabled | FAILED: test_insufficient_shape_midpoint_lost_matches_survivors, test_legacy_pair_cannot_pass_catalog_recovery, test_no_surviving_reference_still_runs_current_shape_evaluator |
| M15 | whole_window.py:5232 | `midpoint_lost` hard-coded False | FAILED: same three |
| M16 | harvest.py:1237 | item 2 within-manifest duplicate check removed | FAILED: test_duplicate_absent_id_in_one_manifest_cannot_run |
| M17 | harvest.py:5220 | 0(a) widened to every row | FAILED (5): both byte-identity tests, test_invalid_recorded_digest_is_never_rescued_by_catalog, test_malformed_present_source_list_never_enters_recovery, test_malformed_source_descriptor_does_not_switch_sources |
| M18 | harvest.py:5490 | stored-bracket comparison re-enabled on recovery (sanity) | FAILED (17 failures, 2 errors) |
| M19 | harvest.py:1197-1198 | catalog None treated as empty | FAILED: test_unauthenticated_manifest_still_fails |
| M20 | harvest.py:5481 | harvest losses not passed to the recovery's exclusion pass | FAILED (6) incl. test_bundleless_spare_and_empty_sources_screen_survivors, test_lost_reference_need_not_be_in_basis |

Copies restored after each mutant; final baseline OK. Nothing in the working directory was written.

## Disposition

No way found for the changed program to pass the NEG-8 screen, or to supply an allowance, that the admitted text would remove. Recorded-source handling is byte-identical to 224a264c5 on the real rehearsal copy and on the fixtures. The gate constant, its epoch and its order are as specified and fail closed. The disclosure objects are exact. One test gap (F1, item 5) is recommended for a test-only fix; it leaves no number or claim at risk under the program as written. Notes N1 to N7 are recording only.

PASS
