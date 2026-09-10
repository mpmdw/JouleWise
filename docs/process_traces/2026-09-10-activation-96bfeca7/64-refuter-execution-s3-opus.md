# S3 EXECUTION-LENS REFUTER REPORT — lane ACCEPTANCE-EPOCH-25G83-01

**Verdict: MERGEABLE.** No blocker, no should-fix that is closable inside S3's footprint. Two follow-ups recorded for the S2 landing and one nit.

## Summary (5 lines)

1. Every claim in the seat's report that I could execute, I executed and it held: `FOCUSED_RC=0` (136 tests), byte-identity across HEAD and `7c4366ec` for all six issued artifacts plus the genesis fixture (`IDENTITY_DIFF_RC=0`), and 16/16 mutations killed with the anchors re-derived independently rather than reusing `/tmp/s3_mutations.py`.
2. I closed the seat's own declared coverage gap: the four consumer modules it did not run (`test_analysis_finalizer`, `test_analysis_integration`, `test_floor_extraction`, `test_run_campaign`) are rc 0 — 595 further tests. Eleven consumer modules total, all rc 0.
3. The A-5 counterfactual reproduces exactly as the addendum specifies: with the skip removed at the `registered_valid` universe only, `calibration_ledger_off_ledger_artifact` fires and the anti-withholding equality breaks.
4. The `session_id` row-schema decision is sound by execution: the prefix matcher does compare the artifact's declared `session_id` against the ledger row's `bracket_session_id` (relabelling the ledger row to a foreign session refuses), and import-only artifacts keep an exact four-key schema — adding a fifth key to r6, even as `null` on every row, refuses.
5. The one polarity worth naming: `_observation_session_kind` fails **open** on a missing kind (missing → `bracket` → row admitted as an endpoint). That is correct for historical rows and is the only safe reading, but it means a field-name mismatch with seat S2 would silently evaporate the barrier with no test failing — `session_kind` does not yet exist anywhere in `calibration_ledger.py` (grep count 0).

## Findings

| id | severity | file:line | claim | reproduction |
|---|---|---|---|---|
| E1 | cleared | `configs/calibration/*` | Every issued artifact + genesis loads byte-identically at HEAD and `7c4366ec` | `/tmp/s3ref_identity.py`, `diff /tmp/s3ref-old.json /tmp/s3ref-new.json` → `IDENTITY_DIFF_RC=0` |
| E2 | cleared | `joulewise/calibration_bracketing.py` (16 sites) | Every new/generalized check has a killing test | `/tmp/s3ref_mutate.py` + `/tmp/s3ref_m15.py`, 16/16 KILLED, `restored: True` |
| E3 | cleared | `:1629`, `:1941`, `:2452` | Removing the skip at ONE site only breaks the anti-withholding equality | M14/M15/M16 below, verbatim tracebacks |
| E4 | cleared | `:1692`, `:1711-1717` | `session_id` is ledger-bound, not self-asserted | `test_live_prefix_binds_every_row_to_the_session_it_declares` + M13 |
| E5 | cleared | `:600-614`, `:709-733` | Import-only artifacts keep the exact four-key prior-row schema | probe P1/P1b: r6 + `session_id` → `_valid_acceptance_bound` False |
| E6 | cleared | footprint | Only two files changed; the three fixture test files untouched | `git diff --name-only 7c4366ec..HEAD` = 2 files; `git diff --stat` over the three = empty |
| E7 | cleared | `tests/verify_calibration_acceptance_corpus.py` | Its rc=1 is environmental, not a regression | same traceback at `7c4366ec` modulo repo-root path |
| E8 | should_fix (S2 landing, not this diff) | `:1534-1558` | Barrier fails open on a field-name mismatch with seat S2 | `grep -c session_kind joulewise/calibration_ledger.py` → `0`; both barrier tests use duck types |
| E9 | nit | `:2415-2433` | A fourth site of the same universe (`superseded_observations`) carries no derivation skip | code read + `_capture_pipeline_refusal_for_observation` at `:1580-1591` |
| E10 | nit | `:913` vs `:218`/`:340` | The `screen_rule` dispatch is unreachable in production today | probe P5: `_REGISTERED_SCREEN_RULES` has one member, so `:340` refuses first |
| E11 | nit | `:1534-1558` | `bracket_session_by_id` is a plain `@property` rebuilt once per observation | `calibration_ledger.py:383-388` |
| E12 | nit (report fidelity) | seat report | Two self-description errors | `git log -1` shows HEAD is a commit; test count is 18+2, not 18+3 |

## Detail, with verbatim rcs

### (1) Test execution

The brief's exact command, rc captured in a shell variable:

```
FOCUSED_RC=0
Ran 136 tests in 4.685s
OK (skipped=4)
```

Adjacent consumers, each module run alone, rc each:

```
test_calibration_ledger              rc=0 :: Ran  72 tests in   2.896s OK (skipped=1)
test_mint_floor_artifact_generalized rc=0 :: Ran  83 tests in  25.406s OK (skipped=2)
test_whole_window                    rc=0 :: Ran  58 tests in  20.986s OK
test_whole_window_selection          rc=0 :: Ran  57 tests in 106.067s OK
test_check_window_provenance         rc=0 :: Ran  36 tests in  12.812s OK
test_custody_mode_inventory          rc=0 :: Ran   7 tests in  34.893s OK
test_arm_readiness                   rc=0 :: Ran  71 tests in  36.670s OK
```

The four the seat declared as its residual gap — I ran them; the gap is closed:

```
test_analysis_finalizer   rc=0 :: Ran  16 tests in  16.004s OK
test_analysis_integration rc=0 :: Ran 116 tests in  47.143s OK
test_floor_extraction     rc=0 :: Ran 170 tests in  21.983s OK
test_run_campaign         rc=0 :: Ran 293 tests in 226.645s OK
```

I enumerated consumers myself by grep over `scripts/ joulewise/ tests/` for `_valid_acceptance_bound`, `_prior_set_matches_import_cutoff_prefix`, `discover_calibration_candidates`, `calibration_bracket_for_bundles`, `_D102_GENERATION_DERIVATIONS`. The seat's list was complete; `test_arm_readiness` exists and passes.

### (2) Byte identity — E1

I did not trust the seat's in-repo regression. I extracted the baseline tree with `git archive 7c4366ec | tar -x -C /tmp/s3ref-old` and ran one script (`/tmp/s3ref_identity.py`) against both trees, comparing per artifact: file sha256, `load_calibration_acceptance_bound` result identity to the raw JSON, a sha256 of the canonically-serialized loaded mapping, `_valid_acceptance_bound`, and `acceptance_generation_operatives`. Plus the genesis fixture built by each tree's own test helper.

```
NEW_RC=0   OLD_RC=0   IDENTITY_DIFF_RC=0
```

`diff -r configs/calibration /tmp/s3ref-old/configs/calibration` is also empty: no issued byte moved. All six artifacts (v2, v2_r2, r3, r4, r5, r6) plus genesis load to the identical mapping with identical operatives at both commits.

### (3) Mutation matrix — E2

Reverted at the production call site in a scratch tree (`/tmp/s3ref-mut`, from `git archive HEAD`), one at a time, each restored before the next; the script asserts each anchor occurs exactly once and prints `restored: True`. Full module (70 tests) run per mutation, so I see every killing test, not just the named one. The repository worktree was never modified.

| Mutation | rc | killing test(s) |
|---|---|---|
| M1 catalog ids ← literal `{"d079_epoch"}` | 1 | 4 tests incl. `test_two_epoch_catalog_admits_and_an_unregistered_catalog_refuses` |
| M2 `len(target_epoch_ids) != 1` deleted | 1 | `test_catalog_that_names_no_entry_equal_to_the_bound_identity_refuses` |
| M3 per-row `epoch_id` ← literal | 1 | 3 tests incl. `test_corpus_purity_refuses_a_member_row_from_another_epoch` |
| M4 prior size / cutoff seq ← `38` / `2*len` | 1 | 3 tests incl. `test_registered_cutoff_sequence_is_read_from_the_row_not_a_literal` |
| M5 `_registered_generation_row_is_complete` guard deleted | 1 | `test_generation_row_missing_a_fence_refuses_rather_than_defaulting` |
| M6 purity loop deleted | 1 | `test_corpus_purity_refuses_a_member_row_from_another_epoch` |
| M7 completeness block disabled (`if False:`) | 1 | 4 completeness tests |
| M8 exclusion reasons ← any `str` | 1 | `test_completeness_refuses_an_unregistered_exclusion_reason` |
| M9 outside-the-registration refusal deleted | 1 | `test_valid_same_epoch_row_outside_the_registration_refuses_issuance` |
| M10 screen-rule dispatch deleted | 1 | `test_unimplemented_screen_rule_refuses_instead_of_falling_back` |
| M11 `live_prefix_allowed = True` | 1 | `test_import_only_prefix_still_refuses_a_single_live_row` |
| M12 terminal-disposition clause deleted | 1 | `test_live_prefix_admits_finalized_rows_and_refuses_unresolved_ones` |
| M13 `session_id` never compared (both tuple sides) | 1 | `test_live_prefix_binds_every_row_to_the_session_it_declares` |
| M14 skip removed at `discover_calibration_candidates` ONLY | 1 | `test_derivation_night_row_never_becomes_a_claim_endpoint` |
| M15 skip removed at `registered_valid` ONLY | 1 | both barrier tests (see below) |
| M16 skip removed at `calibration_bracket_for_bundles` ONLY | 1 | `test_derivation_night_row_is_skipped_by_the_bundles_universe_count` |

**16/16 KILLED, `restored: True`.** Note on method: my first M15 anchor matched twice, because the 8-space `and not _is_derivation_kind_observation(...)` string is a substring of the 12-space form at the bundles site. I re-anchored on `\n` + 8 spaces (`anchor count: 1`) and it killed. That is an artifact of my patching, not a defect in the diff — but it is worth recording that the three call sites are textually near-identical, which is exactly the shape that lets a future edit move two of three.

Independent of the seat, I confirm its disclosure on M10: the dispatch at `:913` is unreachable while `_REGISTERED_SCREEN_RULES` holds one member, because `_registered_generation_row_is_complete` (`:340`) refuses the unknown name first. It kills only under an artificially widened vocabulary. That is defense-in-depth that becomes live the moment a second rule is registered — correct to keep, recorded as E10 so nobody later reads the mutation table as proving a reachable fence.

### (4) The endpoint barrier, one site at a time — E3

M15 (skip removed at the `registered_valid` universe ONLY) reproduces A-5's counterfactual verbatim:

```
FAIL: test_derivation_night_row_never_becomes_a_claim_endpoint
AssertionError: 'calibration_ledger_off_ledger_artifact' unexpectedly found in ('calibration_ledger_off_ledger_artifact',)

FAIL: test_derivation_night_row_is_skipped_by_the_bundles_universe_count
AssertionError: 'failed' != 'passed'
Ran 70 tests in 0.474s
FAILED (failures=2, skipped=1)
```

The equality is exact, so the row present in the registered universe but absent from discovery refuses the window off-ledger. M14 and M16 each break it from the other direction at their own site. The three sites are genuinely coupled and all three are needed.

### (5) The `session_id` row-schema decision — E4, E5

Yes, the comparison is real. `_prior_set_matches_import_cutoff_prefix` appends `(row.get("session_id"),)` to the expected tuple and `(observation.bracket_session_id,)` to the observed tuple, both only under `live_prefix_allowed`. `test_live_prefix_binds_every_row_to_the_session_it_declares` relabels the **ledger** row's `bracket_session_id` to a foreign session id and asserts refusal — the counterfactual input is on the ledger side, which is the right one; M13 kills it. So `registration_session_ids` is ledger-bound, not self-asserted, and the completeness check ranges over a registration the ledger corroborates.

Import-only artifacts are untouched. Executed probes against the real r6 bytes:

```
P0 r6 baseline valid: True
P0 r6 prior-row key set: ['attempt_id', 'content_id', 'disposition', 'epoch_id']
P0 r6 prior row count: 38 | cutoff seq: 76 | catalog: ['d079_epoch']
P1  r6 + session_id:null on ONE row   -> valid? False
P1b r6 + session_id on EVERY row      -> valid? False
P2  unregistered per-row epoch_id     -> valid? False
P3  catalog entry != identity         -> valid? False
P4a import_plus_live + empty registration_session_ids -> row complete? False
P4b import_only + a registration session              -> row complete? False
P4c bool masquerading as cutoff_sequence              -> row complete? False
P4d unregistered screen_rule                          -> row complete? False
```

The schema is an exact set equality, so the fifth key is admitted only for `import_plus_live` and refused everywhere else — S4 must emit it, and no predecessor can grow it. The `bool(session_ids) is (mode == import_plus_live)` biconditional at `:344-352` is a real fence in both directions (P4a/P4b), which the seat did not claim and I confirm.

### (6) Footprint and hidden behaviour — E6, E7, E8, E9, E11

**Footprint.** `git diff --name-only 7c4366ec..HEAD` lists exactly `joulewise/calibration_bracketing.py` and `tests/test_calibration_bracketing.py`; `git status --porcelain` is empty; `git diff --stat` over `test_calibration_live_three_window.py`, `test_paper_first_use_ledger.py`, `test_floor_mint_pinsets_schema.py` and `verify_calibration_acceptance_corpus.py` is empty. The seat's NEEDS_SCOPE "none" is confirmed by execution: those three modules pass unmodified inside the 136-test focused run.

**Corpus verifier (E7).** I ran it at HEAD and at `7c4366ec` on the same r6 artifact. Both exit rc=1 with the same `FileNotFoundError: .../runs_window_a_20260722`; normalising the repo-root prefix, the two logs are byte-identical → `VERIFIER_FAILURE_IDENTICAL_MODULO_PATH`. Environmental, not a regression. It still needs a canonical-checkout run before the transaction.

**No hidden change for bracket-kind sessions.** `grep -c session_kind joulewise/calibration_ledger.py` → `0`. The field does not exist yet, so on today's ledger `_observation_session_kind` returns `bracket` for every row and `_is_derivation_kind_observation` is uniformly False: the barrier is a production no-op until S2 lands, which is why 11 consumer modules are green. `bracket_session_by_id` does exist as a snapshot property (`calibration_ledger.py:383`), so the middle limb of the fallback chain will not `AttributeError`. `prior_row_by_content_id` cannot be shadowed by a duplicate: `:735-738` already refuses `len(prior_ids) != len(set(prior_ids))`.

**E8 (the one I would carry forward).** The fallback is fail-open by construction: a missing kind reads as `bracket`, so a derivation row whose kind S2 stamps under a different key name (`kind`, `kind_id`, nested) is admitted as a claim endpoint and **every test still passes**, because both barrier tests supply the attribute themselves on a `SimpleNamespace`/`replace`d duck type. Nothing in this diff can close that — S3 is declared to depend on no seat, and the constant it would bind to does not exist. The fix belongs at S2's landing, verbatim: *"S2's landing must add a regression that a row belonging to a real `CalibrationBracketSession` of kind `derivation` is skipped at all three sites, and `calibration_bracketing.DERIVATION_SESSION_KIND` must be asserted equal to the ledger module's own constant rather than re-declared."* I record it here so the integration tree, not the merge of this diff, is where it is checked.

**E9, the fourth site.** The seat found a third site the ruling did not enumerate; there is a fourth in the same function, `superseded_observations` (`:2415-2433`), which selects on the same universe predicate but with `_capture_pipeline_refusal_for_observation(...) is not None`, and it feeds `result["diagnostics"]` and can append `capture_pipeline_superseded` to the refusal reasons when `not candidates`. It carries no derivation skip. I sized it and it is a nit, not a blocker: that predicate keys on `anchor_method_version != ACTIVE_CAPTURE_ANCHOR_METHOD` (`:1580-1591`), which is era-global, so derivation rows become superseded exactly when every other row does — no asymmetry can arise. The consequence after a future anchor-method rotation is diagnostics noise (derivation rows listed as superseded on every window), which is consistent with addendum nit N-3's "an estimator-code rotation mid-campaign also voids derivation captures."

**E11.** `_observation_session_kind` reaches `ledger_snapshot.bracket_session_by_id`, a plain `@property` that rebuilds a `MappingProxyType` over a fresh dict on each access, once per observation → O(rows × sessions). Negligible at 76 rows and it is the same order as the pre-existing inline `any(... for session in ledger_snapshot.bracket_sessions)` two lines above it at the bundles site, so this introduces no new complexity class. Worth a `functools.cached_property` some day, not now.

**E12, report fidelity.** Two small self-description errors. The report states "No git write of any kind: the diff is left in the working tree", but HEAD is commit `3f498026` (Ed R, Thu Sep 10 09:04:53 2026 -0700) carrying exactly these two files with a clean tree — whoever committed it, the report no longer describes the artifact's state. And "18 tests and three methods added to `CalibrationBracketingTests`" is 18 + **two** (`test_derivation_night_row_never_becomes_a_claim_endpoint`, `test_derivation_night_row_is_skipped_by_the_bundles_universe_count`): the module goes 50 → 70 tests, +20, and the diff adds exactly 20 `def test_` lines. Neither affects the code.

## Verdict

**MERGEABLE.**

Nothing in this diff needs to change before it lands. The generalization is faithful — every literal the ruling names is now a registered field, the predecessors validate byte-identically under proof, the two new corpus fences (purity, completeness) both kill, the prefix mode is generation-keyed with the import-only fence intact, and the endpoint barrier is installed at all three coupled sites with a one-site-only counterfactual for each. The seat's three self-declared judgement calls all survive execution: the `session_id` fifth key is ledger-bound and confined to `import_plus_live`; the third universe site is real and would otherwise have refused every window on the machine forever; the single implemented `screen_rule` is fail-closed.

Carried forward, not blocking this merge:

1. **(E8, at S2's landing)** "S2's landing must add a regression that a row belonging to a real `CalibrationBracketSession` of kind `derivation` is skipped at all three sites, and `calibration_bracketing.DERIVATION_SESSION_KIND` must be asserted equal to the ledger module's own constant rather than re-declared." The barrier is fail-open on a field-name mismatch and no current test would notice.
2. **(E9, at S4 or the integration tree)** Decide explicitly whether `superseded_observations` (`:2415-2433`) should carry the derivation skip; today it cannot cause an asymmetry, after an anchor-method rotation it produces diagnostics noise.
3. **(E7, before the D-138 transaction)** `tests/verify_calibration_acceptance_corpus.py` still needs one canonical-checkout run; it cannot execute from a linked worktree at either commit.
