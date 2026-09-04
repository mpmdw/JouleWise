# Qwen3 `_v5` floor-generator landing report

Date: 2026-09-03  
Seat: Sol xhigh, resumed implementation seat  
Base: `b4cc8e50d76947d8c6ac69278087e0d2df7f0d18` (exact)  
Disposition: **PARTIAL — NEEDS_RULING**

## Outcome

The two generator implementations and their temp-tree/linkage tests are
complete and green. The predecessor's generators were audited against the two
`_v3` floor generators, the Qwen3 panel, the `_v5` contrast generator, the
identity-pin projection contract, the live family roster, D-164 through D-167,
and ruling 171a. Their pair diff is structurally parallel: the differences are
model/profile/run-ID substitutions. The test module was strengthened in this
resumed seat to make the ruling clauses bite directly.

The committed pack trees were **not generated**. No issued G2-a
`joulewise.prefill_prompt_pin.v2` bundle exists in the checkout, and both exact
root commands fail closed before writing. R-7 settles `N=512`; it does not
provide the selected prompt text, token IDs, token-ID digest, prompt ladder,
or selection record that D-166 and the G2-a loader rulings require. The
synthetic bundle in the test is explicitly fixture evidence and was not used
to create production pack bytes.

## Files produced

- `configs/campaigns/d117_floor_qwen3-1p7b_v5/generate_configs.py`
- `configs/campaigns/d117_floor_qwen3-8b_v5/generate_configs.py`
- `tests/test_d117_floor_qwen3_v5_generate.py`
- `docs/process_traces/2026-09-02-v5-floor-generator/01-sol-landing-report.md`

Expected generated files such as `calibration_plan.json`, phase directories,
`plan_tree.json`, and arm-readiness sidecars are absent because generation
refused the missing authority input. Each floor directory contains only its
generator at this stopping point.

## Audit findings and settled choices

1. Model identities are the exact admitted Qwen3 panel rows: Qwen3-1.7B-4bit
   and Qwen3-8B-4bit, with their panel revisions and byte-identical tokenizer
   digest. This is settled by D-164 and `configs/model_panels/qwen3_4bit.json`.
2. `N=10`, the six science stages, the ten absolute plus ten A/B/B/A block
   shape per measured workload, sampling, reference cadence, and no-retry
   envelope are retained from the `_v3` floor pair. This is not a new member
   count or stress-envelope choice: D-164 calls `_v5` the "same frozen design."
3. Every comparative floor cell installs D-165's `R >= 2` registration,
   per-component/all-must-pass policy, absolute-common-mode
   `not_applicable` disposition, and mandatory comparative `R_cm` disclosure
   with the `< 2` withdrawal.
4. Decode uses the panel's index-0 real prompt rendered through the Qwen3 chat
   template, thinking off, greedy forced 512. This is D-166 plus ruling 171a
   R-6; no prompt rotation was introduced in either floor.
5. Prefill uses `p512` and accepts prompt bytes only through an issued,
   hash-bound G2-a pin bundle. This is D-166 plus ruling 171a R-7. The
   generator deliberately has no fallback prompt synthesis.
6. `PLAN_PROFILE` is ALPHA for 1.7B and BETA for 8B. The temp-generated GAMMA
   tree resolves both floor plans and the production family-marker validator
   accepts the exact ALPHA/BETA/GAMMA roster. This follows D-167 and the
   installed registry; the test's freeze-0004 fields are clearly synthetic
   schema fixtures and are not a claim that draft packs are frozen.

No campaign member count, stress envelope, prompt text, or selected token IDs
were invented in this seat.

## Executed evidence

Baseline manifest:

```text
$ shasum -a 256 .codex-bridge/baselines/inv-20260902-v5-floorgen-01.json
cb310e57870c838575e7491b8c2bae4cfea2f3d0c21d4d7eda0f4d930b7cde39  .codex-bridge/baselines/inv-20260902-v5-floorgen-01.json
```

Required ALPHA generator command:

```text
$ PYTHONDONTWRITEBYTECODE=1 python3 configs/campaigns/d117_floor_qwen3-1p7b_v5/generate_configs.py
generation failed: prefill_prompt_pin_unresolved: pass --prefill-prompt-pin with the issued G2-a pin
[exit 1]
```

Required BETA generator command:

```text
$ PYTHONDONTWRITEBYTECODE=1 python3 configs/campaigns/d117_floor_qwen3-8b_v5/generate_configs.py
generation failed: prefill_prompt_pin_unresolved: pass --prefill-prompt-pin with the issued G2-a pin
[exit 1]
```

Focused temp-generation, two-generation byte identity, contrast linkage, and
roster test:

```text
$ PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_d117_floor_qwen3_v5_generate
.....
----------------------------------------------------------------------
Ran 5 tests in 6.249s

OK
```

The focused test generates each floor twice into separate temp roots, compares
the complete file maps byte-for-byte, runs each generator's `--check` path,
generates GAMMA in the same temp root, resolves the two
`../<pack>/calibration_plan.json` paths and plan IDs, exercises
`_plan_profile` for all three profiles, and passes
`validate_family_publication_marker` without `roster_mismatch`.

All arm-readiness modules plus the family marker, v3-family, and both prior
floor-plan modules:

```text
$ PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_arm_readiness tests.test_arm_readiness_dry_run tests.test_arm_readiness_evidence tests.test_arm_readiness_evidence_author tests.test_arm_readiness_evidence_packauth tests.test_arm_readiness_evidence_t0 tests.test_arm_readiness_integration tests.test_arm_readiness_lifecycle tests.test_arm_readiness_pack_digest tests.test_arm_readiness_registry tests.test_arm_readiness_schemas tests.test_family_marker tests.test_d117_v3_family tests.test_d117_floor_qwen25_1p5b_plan tests.test_d117_floor_qwen25_7b_plan
...
----------------------------------------------------------------------
Ran 384 tests in 833.500s

OK (skipped=20)
```

Dedicated `_v5` contrast-pack module:

```text
$ PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_d117_contrast_v5_pack
............................
----------------------------------------------------------------------
Ran 28 tests in 4.196s

OK
```

Generator pair structural diff:

```text
$ diff -u configs/campaigns/d117_floor_qwen3-1p7b_v5/generate_configs.py configs/campaigns/d117_floor_qwen3-8b_v5/generate_configs.py | diffstat
 generate_configs.py |  262 ++++++++++++++++++++++++++--------------------------
 1 file changed, 131 insertions(+), 131 deletions(-)
```

Final workspace scope inspection:

```text
$ git -C /Users/edr/code/JouleWise-wt-floorgen status --short
?? configs/campaigns/d117_floor_qwen3-1p7b_v5/
?? configs/campaigns/d117_floor_qwen3-8b_v5/
?? docs/process_traces/2026-09-02-v5-floor-generator/
?? tests/test_d117_floor_qwen3_v5_generate.py
```

All four paths are within the exhaustive write scope. A file inventory under
the two pack directories found exactly the two generator files and no partial
generated tree.

## Clause map

Quotes in the last column are verbatim from the named authority.

| Clause | Production site | Biting assertion | Counterfactual one-site edit | Authority phrase (verbatim) |
|---|---|---|---|---|
| D-164 / ALPHA model | `configs/campaigns/d117_floor_qwen3-1p7b_v5/generate_configs.py:552-561`, panel equality gate `:850-890` | `tests/test_d117_floor_qwen3_v5_generate.py:389-406` | Change ALPHA `MODEL.name`, source, revision, tokenizer SHA, or chat-template SHA; the temp-tree model assertion fails (and the generator's panel gate refuses). | `docs/decision_log.md:10398-10401`: "`mlx-community/Qwen3-1.7B-4bit` / `mlx-community/Qwen3-8B-4bit`, tokenizer.json byte-identical across the pair." |
| D-164 / BETA model | `configs/campaigns/d117_floor_qwen3-8b_v5/generate_configs.py:552-561`, panel equality gate `:850-890` | `tests/test_d117_floor_qwen3_v5_generate.py:389-406` | Change BETA `MODEL.name`, source, revision, tokenizer SHA, or chat-template SHA; the same assertions fail. | `docs/decision_log.md:10398-10401`: "do qwen 3" and the exact pair quoted above. |
| D-164 / same frozen design, ALPHA | `configs/campaigns/d117_floor_qwen3-1p7b_v5/generate_configs.py:66`, stages `:583-614`, plan `:2584-2586`, count `:2669-2674` | `tests/test_d117_floor_qwen3_v5_generate.py:275-281,312-319,346-349` | Change `N` to 9 or remove one stage member; the 100-file/count/fixed-N assertions fail. | `docs/decision_log.md:10400-10401`: "generation `_v5` of the same frozen design". |
| D-164 / same frozen design, BETA | `configs/campaigns/d117_floor_qwen3-8b_v5/generate_configs.py:66`, stages `:583-614`, plan `:2584-2586`, count `:2669-2674` | `tests/test_d117_floor_qwen3_v5_generate.py:275-281,312-319,346-349` | Change `N` or the BETA stage shape; the same deterministic count assertions fail. | `docs/decision_log.md:10400-10401`: "generation `_v5` of the same frozen design". |
| D-165 / ALPHA dominance gate | `configs/campaigns/d117_floor_qwen3-1p7b_v5/generate_configs.py:723-769`, installed at `:2631,:2648,:2665` | `tests/test_d117_floor_qwen3_v5_generate.py:315-344` | Change threshold to 1.99, comparison away from `greater_than_or_equal`, or `all_must_pass` false; the per-cell assertion fails. | `docs/decision_log.md:10408-10411`: "the dominance RATIO **R ≥ 2** (per component, per cell) is pre-registered into the `_v5` pack". |
| D-165 / BETA dominance gate | `configs/campaigns/d117_floor_qwen3-8b_v5/generate_configs.py:723-769`, installed at `:2631,:2648,:2665` | `tests/test_d117_floor_qwen3_v5_generate.py:315-344` | Make the same one-site registration edit in BETA; its generated cell assertion fails. | `docs/decision_log.md:10408-10411`: "common-mode R_cm is mandatory disclosure and R_cm < 2 withdraws the dominance sentence." |
| D-165 / common-mode dispositions, both generators | ALPHA `generate_configs.py:740-769`; BETA `generate_configs.py:740-769` | `tests/test_d117_floor_qwen3_v5_generate.py:327-344` | Change absolute common mode to `reportable`, comparative status away from `mandatory`, or withdrawal text away from `R_cm < 2.0`; the exact-object assertion fails. | `docs/decision_log.md:10415-10420`: "absolute R_cm is registered `not_applicable`" / "comparative R_cm stays mandatory". |
| D-166 / ALPHA decode workload | ALPHA decode manifest `generate_configs.py:934-1014`, rendering/assignment `:1017-1047`, config reference `:1437-1444` | `tests/test_d117_floor_qwen3_v5_generate.py:352-374,447-468` | Add a second manifest item, select a non-index-0 prompt, enable thinking, or change forced output length; an exact assertion fails. | `docs/decision_log.md:10430-10432`: "real pinned prompts through the Qwen3 chat template, thinking off, greedy, forced 512". |
| D-166 / BETA decode workload | BETA decode manifest `generate_configs.py:934-1014`, rendering/assignment `:1017-1047`, config reference `:1437-1444` | `tests/test_d117_floor_qwen3_v5_generate.py:352-374,447-468` | Apply the same one-site edit in BETA; its temp-generated tree assertion fails. | `docs/decision_log.md:10430-10432`: same phrase as the prior row. |
| D-166 / prefill source authority | **NOT PINNED: no issued G2-a record/pin exists.** Both loaders validate a closed bundle at `generate_configs.py:1052-1234` and refuse synthesis at `:2466-2475`, but no production prompt bytes can be emitted. | Fail-closed assertions `tests/test_d117_floor_qwen3_v5_generate.py:224-263` | Add fallback/synthetic prompt creation when no pin is passed; `test_generators_do_not_synthesize_a_missing_g2a_prompt_pin` fails. | `docs/decision_log.md:10431-10432`: "prefill length fixed from the G2 shakedown record". |
| R-6 / ALPHA one decode manifest, index 0 | ALPHA `generate_configs.py:934-1014,1034-1047,1437-1444`, projection unit `:2172-2179,:2289-2328` | `tests/test_d117_floor_qwen3_v5_generate.py:352-374,408-425,459-468` | Emit a second suite manifest/item or point one decode config at another manifest; the singleton/ref-set/projection assertions fail. | `06-ruling-171a.md:79-82`: "ONE prompt manifest per floor unit (single identity)" and "rotation's index-0 manifest". |
| R-6 / BETA one decode manifest, index 0 | BETA `generate_configs.py:934-1014,1034-1047,1437-1444`, projection unit `:2172-2179,:2289-2328` | `tests/test_d117_floor_qwen3_v5_generate.py:352-374,408-425,459-468` | Apply the same one-site second-manifest or non-index-0 edit in BETA; its assertions fail. | `06-ruling-171a.md:79-84`: same phrases plus "Rotating floors ... is a new ruling." |
| R-7 / ALPHA p512 | ALPHA `generate_configs.py:67,140,830-847,1422-1433,2330-2361` | `tests/test_d117_floor_qwen3_v5_generate.py:375-387,413-430` | Change `PREFILL_LENGTH` or the projection-unit suffix to p256; token-count and ordered unit assertions fail. | `06-ruling-171a.md:88-91`: "record (512 for `_v5`; the `prefill_p256` literals in this clause, in U8, and in the D-165 census example were `_v3`-era values and are superseded by `<N>`)." |
| R-7 / BETA p512 | BETA `generate_configs.py:67,140,830-847,1422-1433,2330-2361` | `tests/test_d117_floor_qwen3_v5_generate.py:375-387,413-430` | Make the same p256/count edit in BETA; its generated unit/count assertion fails. | `06-ruling-171a.md:86-90`: same phrase as the prior row. |
| R-7 / GAMMA four ordered units | Existing consumer production site `configs/campaigns/d117_contrast_v5/generate_configs.py:2551-2596` | `tests/test_d117_floor_qwen3_v5_generate.py:493-504` | Reorder units or rename one `prefill_p512` unit; the exact ordered-list assertion fails. | `06-ruling-171a.md:86-91`: "GAMMA retains exactly four ordered units: `A/decode`, `A/prefill_p<N>`, `B/decode`, `B/prefill_p<N>`". |
| Contrast floor-plan linkage | Existing consumer site `configs/campaigns/d117_contrast_v5/generate_configs.py:2532-2547`; floor IDs ALPHA `generate_configs.py:106`, BETA `generate_configs.py:106` | `tests/test_d117_floor_qwen3_v5_generate.py:499-515` | Change either floor plan ID or `../<pack>/calibration_plan.json` path; resolution or ID/SHA assertions fail. | `06-ruling-171a.md:91-92`: "A references the smaller model's producer plan and B the larger's". |
| D-167 / live family roster | Floor profile sites ALPHA `generate_configs.py:156`, BETA `generate_configs.py:156`; production roster `joulewise/arm_readiness.py:10875-10891`; registry `configs/arm_readiness/d117_row_registry_v2.json:532-536` | `tests/test_d117_floor_qwen3_v5_generate.py:521-573,575-625` | Change one profile/pack ID in either generator, registry, or marker fixture; `_plan_profile` or `validate_family_publication_marker` raises `roster_mismatch`. | `docs/decision_log.md:10437`: "the live campaign is the `_v5` Qwen3 pair" and "`_v5` rows are installed". |
| D-167 / desk-day generation after G2-a | **NOT PINNED: the G2-a pin is absent, so the ruled desk-day pack-generation step cannot execute.** | Generator fail-closed assertion `tests/test_d117_floor_qwen3_v5_generate.py:240-263` | Synthesize a pin or permit generation without the G2-a record; the assertion fails. | `docs/decision_log.md:10437`: "G2-a probe evening, the desk day (rung pin + pack generation + throwaway-clone re-proof)". |
| D-166 / `_v6` GSM8K leg | **NOT PINNED: explicitly outside these `_v5` floor generators and outside this task's scope.** | N/A | N/A | `docs/decision_log.md:10432-10433`: "Ed's scored GSM8K leg is `_v6`". |

## NEEDS_RULING (verbatim return)

NEEDS_RULING

Question: Which authoritative `joulewise.prefill_prompt_pin.v2` bundle should be used to generate the `_v5` floor packs, given that no issued G2-a record exists in this worktree?

Options considered: (1) Run the ruled G2-a probe/selector/issuer chain and resume this seat with the issued pin bundle; this preserves D-166/D-167 provenance. (2) Issue an explicit lead ruling that replaces the G2-a source for these pack bytes and supplies a named, hash-bound prompt bundle; this unblocks desk generation but changes campaign design/provenance. (3) Authorize the synthetic test fixture as production input; rejected because it contains fabricated token IDs and fixture-only selection evidence.

Recommendation: Choose option (1). R-7 already fixes `N=512`, while the ruled G2-a chain is the authority for the exact prompt text, token IDs, ladder, and selection record; using it avoids inventing campaign bytes.

Blocked work: In-place generation of both committed pack trees; a second in-place regeneration and byte-identity comparison; successful no-argument `--check`; and the committed-tree-versus-fresh-generation assertion. The two generator implementations, temp-tree determinism/linkage tests, roster validation, and all independent verification are complete.

No `NEEDS_SCOPE` return was raised. No out-of-scope path was modified.

## Next exact step

The lead should provide the issued G2-a pin bundle (pin JSON plus its bound
prompt ladder and selection record) or answer the ruling above, then resume
this same seat. The first resumed commands are the two required root generator
commands, followed immediately by a second regeneration/`--check`, the focused
test, the arm-readiness modules, and `git status --short`.

---

## Magistrate ruling on the NEEDS_RULING (2026-09-03 20:55 PDT)

Option (1) is ruled: the `_v5` floor packs are generated from the issued
`joulewise.prefill_prompt_pin.v2` bundle that the G2-a probe/selector/issuer
chain produces on the G2-a night; generation happens on the desk day after
it, exactly as D-167(2) sequences. No synthetic or lead-supplied prompt bytes
enter a production pack. This lane therefore lands the two generators, the
strengthened tests and this record now; the pack trees land on the desk day
with `--prefill-prompt-pin <issued pin>` and a second in-place regeneration
plus byte-identity comparison, as the seat specified under "Blocked work".
The bridge lease shape (directory paths recorded `exact`) is a lease
artefact, not a scope violation: the wrapper's enforced `**` scope passed
with zero violations and every write is inside the four allowlisted subtrees.
The seat's envelope listed both generators as modified this session; their
bytes are the predecessor's (mtimes 2026-09-02 21:55) — recorded.

## Fix-round addendum (2026-09-03)

Audit finding 5 is corrected to read: “Prefill uses `p512` and accepts prompt
bytes only through a G2-a pin bundle hash-bound to the G2-a selection record.”
The generator now parses the record's required selection semantics after
verifying its digest.

### Magistrate addendum (2026-09-03): p42 rider provenance

The p42 prefill rider is the D-164 carry-over of the `_v3` decode-prompt-length rider (p128 there); its length is the panel's index-0 rendering with thinking off (42 token ids, tail [151667, 271, 151668, 271]), refused on panel mismatch (`decode_index_zero_rendering_mismatch`); it does not enter GAMMA's four units.

## Fix-round-2 addendum (2026-09-03)

The six `_v3` condition-family drift refusals (source-byte and domain-hash
pins for decode, prefill, and the selected prefill-length family) are absent
from the `_v5` floor generators by design while the packs remain authoring
drafts. They stay absent only until `V5-DESK-DAY-01` freezes the generated
packs. After that freeze, follow-up kernel row `FLOOR-V5-DRIFT-REPIN-01` must (Row registration is a bookkeeping change on main, launched 2026-09-03 23:05 PDT; until it merges the row is queued, not registered.)
restore all six drift refusals against the frozen family bytes; the magistrate
registers that row.

Ruling 171a R-7 fixes these floor drafts at 512 tokens and they fail closed on
any other G2-a selection. Consequently, if G2-a selects a rung above 512,
both `_v5` floor packs require re-authoring before either can be generated or
armed; no loader fallback silently rebases them to the selected rung.
