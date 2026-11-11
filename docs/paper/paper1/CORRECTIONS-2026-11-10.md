# Paper 1 factual corrections, 10 November 2026

Seat `p1-seat6`, branch `docs/2026-11-10-paper1-corrections`, based on
`origin/main` at `a9dd335b38e6777afcd31c4dc0a812e4bc9906e0`.
This checklist is the item-to-hunk record for RL-5 and RL-24 seat 6.
It does not certify a release, comparison, reader check, tier selection or review.

No result was filled and no realised outcome branch was selected. The only deleted
placeholder is `P1-BYX-RESULTS`, explicitly retired by RL-5 item 5. Every other
placeholder id and its occurrence count is preserved, including `P1-BYX-STATUS`
(now limited to structural drop-decision identifiers) and `P1-B5-B-SHARE`
(labelled exploratory). Main-paper section headings and their order are unchanged.

## Source keys

All sources are committed repository text. Paths in those texts to data outside
this clone were treated as text and were not followed.

| Key | Exact source |
|---|---|
| RL | `origin/audit/2026-11-10-fable` at `24b549f25ace51f1cf7059f913503930419db316`, `docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md`: RL-5, lines 115-139; RL-24, lines 598-639. RL-24 assigns the full automation rewrite to seat 9 and title/restructure to seat 10. |
| PA | Same ref and commit, `docs/research-audits/2026-11-10-fable/paper-audit.md`: C-1–C-11 at lines 136-146; prose register at 260-287; F-01–F-23 at 304-328; stale-text register at 334-351. |
| R2P | `origin/research/2026-11-07-b5-release-to-paper` at `79d8e2dbb5137ccf4e95ac1d0aa32013072252d0`, `docs/research-audits/2026-11-07/b5-release-to-paper.md`: adopted synthesis P1–P12, lines 458-475; Decision 10(i), lines 150-153. The appended Opus report numbers a different issue P12; both are mapped below. |
| SEAL | At base `a9dd335b3`, `docs/process_traces/2026-10-07-block5-seal/SEAL_RECORD.md`: Erratum 1/second seal at 379-406; Errata 2 and 3 at Addenda 3 and 4, beginning 478 and 535. |
| J5 | At base, `docs/process_traces/2026-10-block5/l9-rulings/RULING.md`:117-136, especially the corrected sentence at 134 and disclosure at 136; `RUN_STATE.md` item 33(b), line 58. |
| DLE | At base, `docs/analysis/b5/DEVIATION-LOG.md`: DLE-0 at 38, DLE-1 at 71, DLE-2 at 140, DLE-3 at 228, DLE-4 at 368, DLE-5 at 511; later reporting entries DLE-6–DLE-10 at 711, 776, 831, 859, 888. D5b is at 252-278. Superseded CARE drafts with reused entry numbers are not treated as adopted changes. |
| DL | At base, `docs/decision_log.md`: D-188 at 12239, D-189 at 12251, D-190 at 12263; D-178 at 11674; D-165 at 10736. |
| BARS | At base, `configs/analysis/b5/recompute_bars.json`, `source`, `rule`, and each named `families` entry; `RUN_STATE.md` item 83 ruling 1, cited by that file. These are policy constants, not measured differences. |
| COVER | At base, `docs/analysis/b5/LEAN-COVERAGE-AUDIT.md`:70-82 (seven incomplete disclosure families), 84-96 (computed but not compared), 107-121 (stored judgments and authentication limits). |
| CODE | At base, `joulewise/detection_floor.py`:1534-1536 and 1818-1838 (drift addition and cell gate); `joulewise/analysis_engine/claims.py`:144-203 and 333-382 (reason sets and outcome precedence). Read as code only; no execution on data. |
| PROCESS | At base, `RUN_STATE.md` item 108 at 465, items 71-76 from 267, item 181 at 2659; `configs/campaigns/v5_claim_25g83/registration_block5.md`:4853 (custody by rule). PA C-7 and R2P P4 identify the agent-location contradiction. |
| EXT | PA §4.2/F-18 (Nemotron: no loadable build; both dropped); `RUN_STATE.md`:902 (Qwen3.8-27B dropped under the extension-first rule). No model or session file was opened. |
| BY-DESIGN | `origin/lane/2026-11-07-bytes-stage1` at `912cf8c3a`, `docs/registrations/bytes_pack_v1.md`:297 (invented-energy worked example and four-decimal pilot regressors); PA §4.2 confirms the three-fit/seven-held-out design. |
| BLIND | `paper1/blind-draft-2026-10-27^{commit}` resolves locally to `a1a5029fb2cc0f9b0541f154d0d9d23f56e8aebb`; R2P P5 and RL-1 distinguish the draft's branch prose from registered fixed sentences. No tag was changed. |

## Exact hunk locators

`H01`–`H32` are searchable `FACT Hxx` comments in the changed source files.
They identify a logical correction even when Git combines adjacent corrections
into one diff hunk. The generated index's rows are located by placeholder id;
the generated figure is located by its exact replacement labels. Compare with:

```sh
git diff a9dd335b3 -- docs/paper/paper1
```

| Hunk | Location and change | Source |
|---|---|---|
| H01 | `paper1.md:40` — `paper1.md`, abstract: core recomputation with stored judgments; replication collected and blinded. | COVER; PA C-3/C-11. |
| H02 | `paper1.md:49` — `paper1.md`, abstract and contribution 3: seven held-out models; commitment stated as required ordering. | RL-5(5); PA §4.2; BY-DESIGN. |
| H03 | `paper1.md:98` — `paper1.md` §1.2: distinguish pre-data rules, disclosed changes and pre-release draft prose. | R2P P3/P5/P7; BLIND. |
| H04 | `paper1.md:110` — `paper1.md` contribution 2: collected, sealed replication; remove the unconditional publishability/resolution gloss. | PA C-10/C-11; RL-5(5). |
| H05 | `paper1.md:391` — `paper1.md` §3.6, floor-gate paragraph: guarded operative value plus the floor session's whole gross drift allowance; diagnostics kept separate. | J5; CODE. |
| H06 | `paper1.md:421` — `paper1.md` §3.7, closing paragraph: attribution floor, floor class and dominance branch are distinct. | PA C-2/F-10; RL-4(viii). |
| H07 | `paper1.md:572` — `paper1.md` §4.3, first paragraph: two seals, prospective errata, governing pins. | SEAL; RL-5(2). |
| H08 | `paper1.md:633` — `paper1.md` §4.4, closing collection-status paragraph: early close and counting-session structure; numerical results still sealed. | PA §4.2/C-11; DLE-10. |
| H09 | `paper1.md:675` — `paper1.md` §4.5: actual arm/harvest mechanisms; enumerated changes; expanded, unfilled `P1-DEV-LIST`. | R2P P6/P7; SEAL; J5; DLE; DL. |
| H10 | `paper1.md:691` — `paper1.md` §4.6, structural-read disclosure: floor-resolution status/reason read and subsequent D5b ruling. | R2P P8/Decision 10(i); DLE:252-278. |
| H11 | `paper1.md:701` — `paper1.md` §4.6, dry-run/release paragraph: numerical output produced before release, exposed structure only, verified byte for byte at release. | R2P P2; DLE-1. |
| H12 | `paper1.md:727` — `paper1.md` §4.7 and `P1-RECOMPUTE`; §5.8 `P1-RECOMPUTE-SUMMARY`: scope, seven gaps, required reader checks, correct per-family Block-5 bars, separate Block-6 bars. | R2P P1/P3; BARS; COVER; DLE-0/DLE-6. |
| H13 | `paper1.md:787` — `paper1.md` §5.2, sentence after `P1-B5-INTERVAL-PARTS`: `P1-B5-B-SHARE` retained as exploratory. | R2P P9; RL-5(6). |
| H14 | `paper1.md:810` — `paper1.md` Table 3 caption: both form values include drift after guarding; identify terms to disclose. | J5(e); CODE; RL-5(1). |
| H15 | `paper1.md:887` — `paper1.md` §5.5.4–5.5.5: reason-bound placeholder and four-code gloss table; invalid binding cannot be an empirical negative. | R2P P11; DLE D5b; DL D-178/D-189; CODE. |
| H16 | `paper1.md:1183` — `paper1.md` §6.4: two sentences recording both drops and reasons; `P1-BYX-STATUS` remains unfilled. In §6.5 delete the extension-results paragraph and `P1-BYX-RESULTS` only. | RL-5(5); EXT. |
| H17 | `paper1.md:1310` — `paper1.md` §7.1 and Figure 5 caption: actual local/cloud work, headless agent between measurement sessions, agent dry runs under custody by rule. | RL-5(3); PROCESS; R2P P4. |
| H18 | `paper1.md:1353` — `paper1.md` §7.2 items 1, 5, 7: harvest identity mechanism, recompute scope, pre-release prose provenance. Item 2's BYTES commitment is a requirement. | R2P P3/P5/P6; BARS; COVER; BLIND; PA §4.2. |
| H19 | `paper1.md:1367` — `paper1.md` §7.3, first bullet: temporal census rule replaces the permanent agent-free laptop claim. | RL-5(3); PROCESS. |
| H20 | `paper1.md:1459` — `paper1.md` §8 BYTES and automation paragraphs: extensions dropped; draft prose did not predate collection. | EXT; R2P P5; BLIND. |
| H21 | `paper1.md:1468` — `paper1.md` §9, first paragraph: dominance compares widening with repeatability; replication remains blinded. | PA C-2/C-11. |
| H22 | `paper1.md:1473` — `paper1.md` §9.C: unconditional resolution sentence removed. §9 closing methods sentence now distinguishes registered sentences and pre-release prose. | RL-5(5); R2P P5/P11; PA C-10. |
| H23 | `build_fill_index.py:23` — `build_fill_index.py`, `source()`: floor drift; exploratory share; structural extension source; November process pointers; deviation, release/availability and separate recompute-bar sources. Regenerated `fill_index.md` rows with those ids. | RL-5; R2P P1/P7/P9/P12; J5; DLE; BARS; COVER; PROCESS; EXT. |
| H24 | `figures/build_figures.py:134` — `figures/build_figures.py`, Figure 5 block; generated `fig_p1_pipeline.svg`: `DEVELOPMENT (cloud + local)`, headless lead between sessions, no agent during collection, custody-rule analysis, dry-run byte verification and separate checks. | RL-5(3); PROCESS; R2P P2/P4; DLE-1. |
| H25 | `variants/tierC_block6_addendum.md:12` — `variants/tierC_block6_addendum.md`, abstract clause: same bounded recomputation scope as the main draft. | R2P P3; COVER. |
| H26 | `variants/tierB_bytes_one_pass.md:6` — `variants/tierB_bytes_one_pass.md`, opening comment: historical contingency, collection complete, usability still per model; current scope-freeze date. | PA F-20/§6; RL-7(f); RL-24. |
| H27 | `variants/tierB_bytes_one_pass.md:13` — Same variant, abstract: seven held-out models, required commitment, per-model fallback. | RL-5(5); PA §4.2; RL-7(f). |
| H28 | `variants/tierB_bytes_one_pass.md:26` — Same variant, collection/analysis/results-opening/limitations: per-model one- or two-usable-pass rule, not uniform one-pass analysis; stale open question removed. | RL-7(f); PA F-20; main draft §6.3 registered per-model definition. |
| H29 | `variants/tierB_bytes_one_pass.md:32` — Same variant, extension clauses: both drops and structural source-id placeholders. | RL-5(5); EXT. |
| H30 | `paper1.md:1171` — `paper1.md` §6.3 blinding/commitment paragraphs: registered ordering rather than an assertion of a completed commitment. | PA §4.2/F-08; RL-7(a); RL-24 seat 3. |
| H31 | `paper1.md:1485` — `paper1.md`, evidence/code-availability placeholder: release-event/custody locator, record digest and bundle manifest are required at fill, with none supplied here. | R2P synthesis P12. |
| H32 | `paper1.md:1124` — `paper1.md` §6.3, after the synthetic worked example: identify the registration's four-decimal pilot inputs rather than rounded Table 7 values. All existing synthetic numbers unchanged. | PA F-22; BY-DESIGN:297. |

## Adopted 7 November items P1–P12

| Item | Hunk or no-change disposition |
|---|---|
| P1: wrong recompute tolerance | H12, H23; correct family bars, separate Block 6 S-13, both recompute placeholders repointed. |
| P2: release order | H11; DLE-1 also listed in H09/H23. |
| P3: blanket recompute claims | H01/H03/H12/H18/H25; incomplete families and stored judgments explicitly named; separate checks required, not claimed complete. |
| P4: agent-free account/cloud-only work | H17/H19/H24; actual custody-by-rule and activity timing. |
| P5: every outcome sentence predated data | H03/H18/H20/H22; tagged blind-draft provenance verified locally. |
| P6: code mismatch supposedly refused at arm | H09/H18; identity arm check and harvest exclusion/fault distinguished. |
| P7: missing deviations and D5b timing | H07/H09/H23; all requested history and later reporting entries included; pre-release structural read disclosed. |
| P8: structural status read omitted | H10, with D5b chronology in H09. |
| P9: unregistered B share | H13/H23; preserved as exploratory without a value. |
| P10: title ruling | No change needed in this seat: RL-8/RL-24 seat 10 owns working title and restructure. The contingent subtitle remains an unselected placeholder; H06 prevents conflating it with floor class. This is an explicit handoff, not title approval. |
| P11: resolution gloss versus non-estimability | H15/H22; gloss table separates four pertinent codes and branches; generic floor absence is not substituted for the issued reason. Other codes keep their registered glosses. |
| P12, adopted synthesis: evidence locators at print | H31/H23; add required fields to unfilled availability/release metadata. No change needed to the superseded `draft-v2-skeleton.md` in this seat; actual locators and their verification belong to the authorized fill/release work. |
| P12 in appended Opus report: wrong index bars | H12/H23, also covered by synthesis P1. This duplicate numbering is not silently dropped. |

## The eleven 10 November statements

| Item | Hunk or no-change disposition |
|---|---|
| C-1: title/subtitle | No change needed in this seat: title belongs to seat 10; subtitle stays an unfilled contingent slot. No dominance result was used to choose text. |
| C-2: three different attribution/dominance terms | H06/H21; definitions separated without classifying any measured cell or selecting a branch. |
| C-3: every headline number from raw records | H01/H03/H12/H18/H25; coverage limitations and stored judgments. |
| C-4: Block-6 bars attributed to Block 5 | H12/H23. |
| C-5: analysis supposedly ran after release | H11/H24; pre-release L9 bytes verified at release. |
| C-6: no post-collection arithmetic/program changes | H07/H09/H23; distinguish estimator definitions from implementation, interpretation and reporting changes. |
| C-7: where agents ran | H17/H19/H24. Full historical evaluation remains seat 9's work. |
| C-8: draft branch prose supposedly registered before data | H03/H18/H20/H22; BLIND tag verified, no tag creation required. |
| C-9: omitted permitted status/reason read | H10/H09. |
| C-10: unconditional non-resolution gloss | H04/H15/H22; remove the conclusion claim; retain only reason-specific method interpretations. |
| C-11: replication presented as an analysed result | H01/H04/H08/H11/H21; collected structure and sealed results distinguished. Section 5.7 result templates and all their placeholders remain unselected. Tier adoption and the fixed DLE-10 reporting sentence are lead/fill work under RL-6(e), not performed here. |

## Remaining prose-register statements (PA §4.2)

| Statement | Hunk or no-change disposition |
|---|---|
| Abstract: held-out count and unverified completed commitment | H02/H27/H30. |
| Abstract: phase-attribution limitation | No change needed: PA marks it supported; no instrument validation claim added. |
| §3.1 machine/adapter/sampler constants | No change needed: PA marks them supported by item 211; no hardware check performed here. |
| §3.2 record minimum and short-prompt limitation | No change needed: PA marks supported; no measurement rerun. |
| §3.3 pulse count, sizing rationale and timing formula | No change needed: PA's design/arithmetic check supports these; no calibration value read. |
| §3.6 incomplete floor gate | H05/H14/H23; formula corrected, no audit floor value copied. |
| §3.7 branch rule | No change needed to the rule: all required ratios still determine the branch; H06 separates definitions. No branch selected. |
| §3.8/§3.10 estimators and claims ladder | No change needed to registered definitions; H15 corrects reason interpretation at the branch sites. |
| §4.3 seal history / arm mechanism | H07/H09/H18. |
| §4.4 replication close | H08; only released collection structure stated. |
| §4.5–§4.7 change/blinding/recompute claims | H09–H12/H23. |
| §6.2 Table 7 ranges | No change needed at this no-fill stage: PA says the printed table matches checked manifest rows. Reconciliation of the registration's range sentence from the frozen manifest remains at fill; no new value derived. |
| §6.3 coverage experiment | No change needed: PA verifies the design's synthetic coverage statement. |
| §6.3 commitment and worked-example inputs | H30/H32. |
| §6.4 extensions | H16/H29. |
| §7 process history | H17–H19/H23/H24 remove the identified false claims. No full historical rewrite in this seat: RL-24 seat 9 owns it. |
| §8 additional empirical limitations | No change needed in this no-result seat: empirical magnitudes and outcome-dependent limitations require the authorized source-reader/fill work (seats 4/12). Existing limitations retained; definitions and provenance corrected in H20. |
| §9 framing and unconditional resolution claim | H21/H22. Larger introduction/conclusion rewriting belongs to Ed/seat 13. |
| References 22–27 | No change needed in this seat: RL-24 seat 14 owns the primary-source bibliography audit; network is forbidden here. |

## All PA finding ids

This table also records findings whose remedy is explicitly outside seat 6.
“No change needed in this seat” does not mark an external gate complete.

| Finding | Hunk or no-change disposition |
|---|---|
| F-01 manuscript choice | No change needed: RL-24 records Ed's scope decision; no competing manuscript selected here. |
| F-02 draft not landed/tagged | No change needed: seat 1's draft is present on the base, and BLIND tag peels to the named commit. No push/tag mutation authorized by this no-network task. |
| F-03 floor drift | H05/H14/H23; only formula/metadata, no measured example. |
| F-04 missing print gate | H12/H23 state required separate checks. No change needed to gate state: seats 4/12 and the research lead own completion. |
| F-05 placement adoption | No change needed: RL-24 seat 8 owns registration/registry entries; base already includes DLE-7. No slot filled or registry status changed here. |
| F-06 contradictory prose | C-1–C-11 and R2P mappings above. |
| F-07 Block-6 analysis/§17 work | No change needed: seats 5/7 and later RL-25/RL-30 own this; no sealed analysis or runnable-path claim made. H08/H11 state sealed status. |
| F-08 BYTES stage-1 prerequisites | H02/H18/H27/H30 state requirements without claiming commitment; gate implementation remains seat 3. |
| F-09 contingency dates | H26 corrects the touched Tier-B header. No change needed to broader scheduling records in this seat: RL-6/RL-7/RL-24 and the lead own date calls; coordination state is expressly write-protected. |
| F-10 terms conflated | H06/H21. |
| F-11 Block-5 release before BYTES fit stage / overlap disclosure | No change needed to empirical disclosure here: RL-7(d) and authorized BYTES stage/fill work own it; no fitted line or commitment printed. |
| F-12 load-correlated line not compared | H12/H23 name the gap; actual independent check remains seat 4. |
| F-13 §7 source cutoff | H23 repoints process sources through November; H19 corrects the identified current rule. Full reconstruction and evidence adjudication remain seat 9, not declared done. |
| F-14 other paper-plan milestones | No change needed: outside `paper1.md` factual corrections; lead planning/state responsibility. |
| F-15 BYTES riders | No change needed: RL-7(c), BYTES registration work; no rider invented here. |
| F-16 D-177 repetition interpretation | No change needed to reporting policy here: RL-24 seat 8 owns it and base includes DLE-8. Existing limitation statements retained. |
| F-17 held-out model count | H02/H27. |
| F-18 dropped extensions | H16/H20/H23/H29; only results placeholder retired by express ruling. |
| F-19 verbatim fixed sentences | H03/H18/H20/H22 correct provenance. No change needed to appendix arrangement in this seat: DLE-9 and seats 8/10/fill own verbatim reporting/gloss placement. |
| F-20 partial-pass question moot | H26/H28; per-model rule restored. No change needed to dated `DRAFT_NOTES.md`: it remains a 27 October record, and the current disposition is here. |
| F-21 manifest range discrepancy | No change needed before fill: recompute from the frozen manifest in authorized fill work; no alternate range inserted. |
| F-22 rounded synthetic inputs | H32 identifies the exact example inputs; all synthetic output numbers retained. |
| F-23 stale CANONICAL production-program row | No change needed in this seat: Block-6 production-path owner/lead under RL-6; no CANONICAL edit authorized by the factual-corrections brief. |

## PA §6 stale-text register and other boundaries

| Audit statement(s) | Hunk or no-change disposition |
|---|---|
| `PAPER-PLAN-v2.md` Block-5 exclusion/sealed gate row; “no Block-5 result”; acceptance checklist | No change needed here: RL-1/seat 1 owns supersession in that other manuscript's plan. This seat imports no results. |
| Same plan: v4 variant A timing; old §10 content; old Fable role | No change needed here: outside Paper 1 factual corrections and subject to sealed v4 work/lead planning. No v4 data was opened for this correction. |
| `TALK-OUTLINE-v2.md` sealed-results rule | No change needed here: seat 1/lead talk ownership. |
| `research-strategy.md` framing; `AGENDA.md` checkpoint provenance and old fixed-window count | No change needed here: strategy/schedule sources, not manuscript facts being corrected. Lead responsibility; no state edit or task registration. |
| CANONICAL Paper rows | No change needed: seat 1's landing is already the base prerequisite; this seat does not retag or push. |
| Registry header / placement | No change needed here: seat 8/lead; DLE-7 exists at base. |
| Contingency-plan November triggers | No change needed to that plan here: RL-24/lead date ownership; H26 updates the touched historical variant instruction only. |
| P1 §6.4 extension status; Tier B incomplete pass 2 | H16/H26/H28/H29. |
| Item 37 side-by-side reporting obligation | No change needed to the ruling here: DLE-10 at base records the deviation. H08/H11/H21 do not claim replication release; final Tier-C wording is authorized fill/lead work. |
| PA §4.3 pilot-vs-manifest byte accounting | No change needed: Table 7's existing manifest values were not replaced by outline/pilot values. H32 identifies the synthetic example's distinct pilot inputs explicitly. |
| PA §4.3 whole-machine/sensitivity values and exploratory lessons | No change needed: no such value imported; separate reader/fill work owns checks and exploratory labels. |
| PA §7 objections and §8 outline | No change needed as new result/narrative work: their factual-method counterparts are mapped above. New experiments, replication analysis, outcome selection and restructuring are outside this seat. |

## Regeneration and review handoff

Before editing, `python3 -I docs/paper/paper1/build_fill_index.py` reproduced the
base index unchanged: 236 occurrences, 215 in the main draft, 219 ids, 174 new ids.
After corrections its output **changed**: 235 occurrences, 214 in the main draft,
218 ids, 173 new ids. The count difference is exactly the expressly deleted
`P1-BYX-RESULTS`; source descriptions and line locations also changed. A second
generation must be byte-identical. Figure 5 is regenerated from its source;
the other four generated schematics are unchanged.

Required next step: **Opus re-derives every changed factual sentence against the
sources above, then the research lead reviews.** No independent review is claimed
by this checklist. Seat 9 receives the limited §7 corrections and November source
pointers; seat 10 receives unchanged section structure and an unresolved title
handoff. Release readers and fill owners retain every numerical gate.
