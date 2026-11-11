# Block 6 registration §17 entries: draft for the research lead's review (2026-11-10)

**What this file is.** The drafted §17 change-log entries for `docs/registrations/block6_replication_DRAFT.md`
(called **REG** below) that research-lead ruling RL-6 (b) orders and RL-24 seat 5 assigns. It is a draft. Nothing
here is entered in REG yet, and REG is unchanged by the commit that adds this file. REG §17 ends with the
2026-10-17 activation entry (`2a4e5149c`).

**The rulings it implements.** RL-6 (b), RL:146-153:

> - (b) The registration's §17 entries are entered now. The default for each is the recommended option of the
>   2026-11-07 Block 6 design audit (`origin/research/2026-11-07-block6-design` @ `07b9f704b`), entered verbatim
>   and labelled with that commit and "entered after the Block 5 unseal". DLE-2's owed entry cites its adoption
>   date, 2026-11-06. Where that audit gave no recommendation, or where the lead or I depart from it, the entry
>   is labelled "decided after Block 5 outcomes were known", and where the choice changes a printed number the
>   alternative is printed beside it, as the registration's §12.4 already requires. If the audit run has not
>   finished when the numbers would be released, the release holds. I review the drafted entries before they are
>   entered.

RL-24 seat 5: "Verbatim from the 2026-11-07 audit's recommended options and DLE-2, each labelled; its decisions 7
(second half), 8 and 9 set out as options". Acceptance: "Every entry quotes its source with commit and line; no
option chosen where the audit chose none". Review: the research lead rules decisions 7, 8 and 9 by 13 November; one
Sol executing refuter by 14 November.

**Sources and how they are cited.**

| Alias | File | Commit | Notes |
|---|---|---|---|
| AUD | `docs/research-audits/2026-11-07/block6-design.md` | `07b9f704b` (2026-11-07 16:53:41 -0800) | On `origin/research/2026-11-07-block6-design`; merged into `research/2026-11-07-audit-burn` (PR #695, open) at `1572b2e62`. The blob (`9ebf356d2e3b`) is identical on both. Not on `main` |
| RL | `docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md` | `5de56400f` (`origin/audit/2026-11-10-fable`) | The research lead's rulings; not on `main` |
| DLE | `docs/analysis/b5/DEVIATION-LOG.md` | `60d3225ee` (`origin/main`) | DLE-2 entered at `422576dc5` (2026-11-06); its text is byte-identical to `d8c17dff4` (2026-11-06 15:17 PST) |

`AUD:489` means line 489 of AUD at `07b9f704b`. Every block quotation from AUD, DLE and RL below is copied from
those bytes by a script, line for line; the only change is the `> ` prefix.

**The label every entry carries.** "Entered after the Block 5 unseal (2026-11-08); text drafted pre-unseal on
2026-11-07." For the DLE-2 entry the drafting date is DLE-2's adoption date, 2026-11-06, as RL-6 (b) says.

**Signing statement, for entry.** AUD:483 says each entry "is signed blind, extending the DLE signing statement to
block 6". That statement can no longer be made about Block 5: Block 5 was unsealed on 2026-11-08 (`RUN_STATE.md` item
231). The statement these entries carry is RL-6's own blind-status line, verbatim (RL:168-169):

> **Blind status.** Blind to Block 6: nothing of it has been read. **Not blind to Block 5**, whose outcome words
> the replication word compares against. The date in (d) was chosen from engineering state only.

Drafter's disclosure (Opus 5.5, seat 5): I read no Block 6 outcome, result file or restricted path. I read the
registration, the audits, the rulings, the deviation log and `RUN_STATE.md`; in doing so I saw Block 5's released
outcome words and headline numbers (`RUN_STATE.md` item 232). Every entry text below was written on 2026-11-06 or
2026-11-07, before the unseal; I wrote only the framing, the notes and the option layouts.

**Status words.** **Default** means the audit's recommended option, or its text where no decision is attached, to be
entered as drafted once reviewed. **AWAITING RESEARCH-LEAD RULING** means the audit chose no option; the options are
set out and none is chosen.

**How the entries get into REG (proposed, for the research lead).** After the research lead's review and rulings and the refuter's check, each entry is
appended to REG §17 as one dated line in the existing style, pointing at this file for the full text, and the slot
rows it fills (S-13, S-14, S-15, S-9, S-11) are updated in the same commit. That commit is a separate PR.

---

## Map: the audit's eleven decisions and where each lands

| Decision (AUD §1) | Audit recommendation | Entry | Status in this draft |
|---|---|---|---|
| 1. Production architecture (AUD:95-113) | (c), with C3 mandatory | §17-R1 | Default |
| 2. S-13 printed precision (AUD:114-134) | Strictest value per family | §17-R2 | Default |
| 3. Amendment deadline (AUD:135-139) | Before the Block 5 unseal | §17-R0 | Missed; RL-6 (b) enters the set after the unseal. See the review points |
| 4. The D5 r4 lane (AUD:140-143) | Push, review, tag `b5/analysis-r4` | §17-R4 | Default (the tag now exists) |
| 5. Audit unfinished at release (AUD:144-145) | Hold | §17-R1 | Default (RL-6 (b) says the same) |
| 6. Coverage, family by family (AUD:146-152) | (b) count-type, (a) both whole-machine lines | §17-R3 | Default |
| 7. S-15 and §10's whole-machine Q (AUD:153-156) | None | §17-R8 | **AWAITING RESEARCH-LEAD RULING** |
| 8. Estimand wording (AUD:157-161) | None | §17-R9, four items | **AWAITING RESEARCH-LEAD RULING** |
| 9. Host and read path (AUD:162-166) | None | §17-R11, read path | **AWAITING RESEARCH-LEAD RULING** |
| 10. L9-ENV-3 mirror deletion (AUD:167-168) | Hold it | none | Not registration text (code precondition C5) |
| 11. One structure-only probe (AUD:169-176) | Run it, counts only | none | Not registration text; an action for the lead |

---

## §17-DLE2. The production program for blocks 6 onward (DLE-2, owed)

- **Label.** Entered after the Block 5 unseal (2026-11-08); text adopted pre-unseal on 2026-11-06 (DLE-2).
- **Status.** Default (RL-6 (b): "DLE-2's owed entry cites its adoption date, 2026-11-06").
- **Source.** DLE:140-193 @ `60d3225ee`; entered at `422576dc5`. The entry DLE-2 says is owed:

> - **Conditions and follow-ups.**
>   - **Block-6 registration.** Block 6's registration file must carry this change as a dated §17 entry, checked by
>     one executing refuter, by its own rule. That entry is owed. This log does not edit the block-6 draft.

- **Entry text (verbatim, DLE:142 and DLE:149-158).**

> - **Status.** ADOPTED, 2026-11-06.

> - **Change.**
>   1. For blocks 6 onward, the lean recompute (`scripts/independent_recompute_b5.py`, with its member pool) is the
>      production path.
>   2. The collection-time input judgments are bound by content hash to the harvest record (the step-0 census), not
>      re-derived. They are: the clock anchors (m, s), the calibration fits (b_pre, b_post), the exclusions and the
>      NEG-8 record. This is D-188 item 2 (DL:12245) applied to them, and ED-RULING item 6, option (b).
>   3. The heavy L9 pipeline runs once per block as an audit, off the critical path, with fewer workers. It never gates
>      a release unless it disagrees.
>   4. **Disagreement rule, as drafted in CARE §2.5 item 3.** Any family outside its bar holds the release. A blind seat
>      traces it, structure only. Which side prints is decided by the defect found, never by the value.

- **Effect on estimands (verbatim, DLE:164-165).**

> - **Effect on estimands.** None. No estimand, estimator, decision rule or threshold changes. Block 5's registered
>   arithmetic is unchanged for block 6. Only the program that produces the numbers changes.

- **Conditions carried with it (verbatim, DLE:169-182).**

>   - **Coverage before block-6 production.** As a production path, the recompute must print every quantity the
>     block-6 analysis plan registers.
>     - The quantities it does not compute today are in `docs/analysis/b5/LEAN-COVERAGE-AUDIT.md` §2: monitor cost,
>       arm and host summaries, battery phase, subject and temperature lines, and the full reference, attempt and G10
>       history.
>     - Each must either be added to the lean program or be named in the block-6 plan as supplied by the heavy audit
>       run.
>     - Until then, those lines come from the audit run.
>   - **Agreement gate.** Before the lean path is production for block 6, CARE §2.5 item 1 must hold. That is exit 0
>     on the block-5 dry-run custody (DLE-1 stage (c)), with every family agreeing and 0 unmapped, and again on the
>     first counting block-6 session.
>   - **Ties at thresholds.** The comparator's half of the tie rule is the FS3 rule (RS lines 589-602). The paper's half
>     is the lead's FS3 note.
> - Block-6 sessions must also be blinded at signing.

- **Drafting note (not entry text).** §17-R1 below amends items 1 and 3 of this entry for Block 6. AUD's decision 1
  sets "(b) DLE-2 literally" against "(c) Seat 2's proportionate path" (AUD:98-105) and recommends (c). DLE-2's two
  open review points (DLE:183-193) are answered by §17-R1 (the audit-unfinished rule, the strict-refusal surface)
  and by C3 inside §17-R6.

---

## §17-R0. Framing entry

- **Label.** Entered after the Block 5 unseal (2026-11-08); text drafted pre-unseal on 2026-11-07.
- **Status.** Default, except the two clauses listed under the review points below.
- **Source.** AUD:489 @ `07b9f704b`, with the section preamble AUD:483-485 and decision 3, AUD:135-139.

> - Each entry is signed blind, extending the DLE signing statement to block 6, and is checked by one executing refuter.
> - No entry changes registered arithmetic.
> - The order is what blocks what.

> | # | Amendment | From | Resolves |
> |---|---|---|---|
> | R0 | **Framing entry.** Block 6 is collected and blinded, and these entries are made under §12.4 before release. The signer states that no block-5 or block-6 outcome has been seen. The deadline is decision 3. | seat 2 #1 | §0 premise |

- **Decision 3, as the audit wrote it (AUD:135-139).**

> 3. **Amendment deadline.** REG §12.4 allows §17 entries while block 6 is blinded, that is, up to the block-6 release.
>    Both seats prefer a deadline before the block-5 unseal, and seat 1 would register "no amendments after". After the
>    unseal the signer has seen block-5 outcomes, so a blind statement is no longer credible.
>    **Recommendation:** land R1-R12 before the block-5 unseal. After it, allow only entries that fix a tooling defect
>    and choose no rule, labelled as such.

---

## §17-R1. Production program and second side (decisions 1 and 5)

- **Label.** Entered after the Block 5 unseal (2026-11-08); text drafted pre-unseal on 2026-11-07.
- **Status.** Default: decision 1's recommended option (c) with C3, and decision 5's recommended hold.
- **Source.** AUD:490 @ `07b9f704b`; decision 1 at AUD:95-113; decision 5 at AUD:144-145.

> | # | Amendment | From | Resolves |
> |---|---|---|---|
> | R1 | **Production program and second side** (decision 1). Name the printing program by path and digest, and pin the block-5 script digest it loads. Redefine §12.3 items 3-4: what "analysis programs" and "independent recompute" now are. Replace §13's release re-run with DLE-1-style digest re-verification plus an input census, and drop the determinism repeats. Disagreement rule: a hold, decided by the defect found (CARE §2.5 item 3). Add the audit-unfinished rule (decision 5). The disagreement surface includes strict refusals. Restate DLE-2's agreement gate on the first counting block-6 session. Correct §1.10 and `CANONICAL.md:48`. | seat 1 A1; seat 2 #2, #3 | F1 |

- **Decision 1, the recommended option filled in (AUD:95-113).**

> 1. **Production architecture.** This gates R1, R3, R4, R11 and R12. The options:
>    - **(a) REG §13 as written.** L9 with an `AnalysisBlock` seam plus the B6-AN-1 driver prints the numbers; the lean
>      program checks them.
>    - **(b) DLE-2 literally.** The lean program prints, and the heavy L9 pipeline audits once. This still needs the seam.
>    - **(c) Seat 2's proportionate path.**
>      - RC-B6-1 prints, with the member pool added and the block-5 script's digest pinned.
>      - The second side for the block-6 layer is three pieces: the twins already on `main`, a small stdlib checker for
>        counting, pairing and §10-§11, and the reducer cross-check promoted to a gate. The twins are
>        `joulewise/twins/harvest_twin.py` (REG §1.7-1.8) and `joulewise/twins/engine_twin.py` (REG §9.4). The
>        reducer cross-check is `stored_energy_mismatch`, I:479.
>      - The L9 audit becomes optional, recorded as a §17 deviation.
>
>    **Synthesis recommendation: (c), with C3 mandatory.** C3 re-derives exclusions under the block-6 catalog.
>    - (c) is the only option whose parts exist today.
>    - C3 keeps one independent re-derivation of the collection-time judgments. Without it, DLE-2's own open review
>      point applies: the audit run would be "the only check of those judgments" (DLE:184-188).
>    - Options (a) and (b) both need the L9 seam: binding sites across `whole_window.py`, `floor_extraction.py`,
>      `floor_mint_estimator.py`, `b5_analysis/context.py`, `bracket.py`, the mint script and `disclosures.py`
>      (DESIGN §4.2, :312-360). They also need an equivalence replay that takes hours.

- **Decision 5, the recommended option filled in (AUD:144-145).**

> 5. **If the audit has not finished at release.** Either hold (seat 2), or release labelled provisional (seat 1 offers
>    both; DLE:189-191). **Recommendation: hold.** It is simpler, and it removes the provisional-labelling surface.

- **C3, made mandatory by decision 1 (AUD:509).**

> | # | Precondition | From |
> |---|---|---|
> | C3 | Re-derive block-6 exclusions in the lean program (R6). | seat 2 C3 |

- **Drafting notes (not entry text).** RL-6 (b) states the same hold ("If the audit run has not finished when the
  numbers would be released, the release holds"). RL-24 seat 7 builds option (c). Under (c) the "printing program"
  of R1 is RC-B6-1 (`scripts/independent_recompute_b6.py` on `lane/2026-10-27-recompute-b6`); its path and digest
  are filled when seat 7's code is pinned (S-14).

---

## §17-R2. S-13 made definite (decision 2)

- **Label.** Entered after the Block 5 unseal (2026-11-08); text drafted pre-unseal on 2026-11-07.
- **Status.** Default: decision 2's recommended table.
- **Source.** AUD:491 @ `07b9f704b`; decision 2 at AUD:114-134.

> | # | Amendment | From | Resolves |
> |---|---|---|---|
> | R2 | **S-13 made definite** (decision 2). One printed-precision table, pinned by digest. One comparator code path. The registered run set for run phase energies. The FS3 tie rule in that path. Coverage defined as a registry of REG-printed quantities, with unmatched or absent keys failing closed. Strike the placeholder set, or make `load_bars` refuse any set with `placeholder: true`. | seat 1 A2; seat 2 #4 | F2 |

- **Decision 2, the recommended option filled in (AUD:114-134).**

> 2. **S-13 printed precision.** This gates R2. Pick one table and one comparator code path.
>
>    **Recommendation: keep S-13's rule and register the parameter it lacks.** Use the strictest value per family across
>    the three tables:
>
>    | Family | Decimals |
>    |---|---|
>    | J | 5 |
>    | ratios (R, R_cm, the factor, the energy ratio) | 4 |
>    | per-token | 8 |
>    | t | 3 |
>    | p | 4 |
>    | b_op (s) | 6 |
>    | counts and words | exact, with the FS3 rule |
>    | run phase energy | 1 mJ (unchanged) |
>
>    - This supersedes lead decision 1 of 2026-10-27. RC-B6-1.md:147-152 says Ed may override that decision before the
>      release.
>    - Seat 1's option (a), adopting block 5's coded 1e-6 relative bars, does not satisfy S-13's wording. Above about
>      5 J they are looser than a 5-decimal half-unit: 26 J × 1e-6 = 2.6e-5 J, against 5e-6 J.
>    - The strictest table is still far above float noise. DESIGN :962-980 derives 2.2e-7 J at 1,000 J.

---

## §17-R3. Printed-quantity table (decision 6)

- **Label.** Entered after the Block 5 unseal (2026-11-08); text drafted pre-unseal on 2026-11-07.
- **Status.** Default: decision 6's recommended split.
- **Source.** AUD:492 @ `07b9f704b`; decision 6 at AUD:146-152.

> | # | Amendment | From | Resolves |
> |---|---|---|---|
> | R3 | **Printed-quantity table** (decision 6). For every §9.5-§11.4 quantity, the seven DLE-2 families, the §8.2 request-level whole-machine line and §9.5 item 7, give the producer(s), comparator family and bar. Where there is one producer, label it "not independently recomputed", or "copied from record, bound by digest", as item 83 ruling 3 did for block 5. State whether B5-PLAN §8.2's request-level line is registered for block 6. | seat 1 A3; seat 2 #5 | F4 |

- **Decision 6, the recommended option filled in (AUD:146-152).**

> 6. **Coverage, family by family.** This applies to the seven DLE-2 families, the request-level and per-phase
>    whole-machine lines, and §9.5 item 7. For each, choose one:
>    - **(a)** computed by the production program and compared; or
>    - **(b)** "copied from the harvest or acceptance record, bound by digest, not recomputed", with the item-83
>      ruling-3 hand check.
>
>    **Recommendation:** (b) for count-type disclosures, (a) for both whole-machine lines.

---

## §17-R4. S-14 contents (decision 4)

- **Label.** Entered after the Block 5 unseal (2026-11-08); text drafted pre-unseal on 2026-11-07.
- **Status.** Default.
- **Source.** AUD:493 @ `07b9f704b`; decision 4 at AUD:140-143.

> | # | Amendment | From | Resolves |
> |---|---|---|---|
> | R4 | **S-14 contents.** For any L9 use, a base at or after `b5/analysis-r4` (D1 fix, D5b, D5 two-mode rule). The blind dry run runs floor binding on all three GAMMA units with their real pairs and prints per-cell bound flags (structure only). "All serving cells unbound" is a tooling refusal class, never an outcome. An exit 3 counts as completion only if a structure-only probe shows the refused resolutions are not binding failures. | seat 1 A4; seat 2 #6 | F3, F10.4 |

- **Decision 4, as the audit wrote it (AUD:140-143).**

> 4. **The D5 r4 lane.**
>    - Push `lane/2026-11-07-b5-analysis-r4` (`7db6fb9a3`, local only), review it and tag `b5/analysis-r4`.
>    - Any L9 use for block 6 must be based at or after that tag.
>    - The fix's two-mode rule needs a block-6-shaped fixture (R12).

- **Drafting note (not entry text).** The tag `b5/analysis-r4` exists on origin and points at `ab1e0098d`, the
  analysis commit of the Block 5 release check (`RUN_STATE.md` item 231; DLE-5 status line).

---

## §17-R5. b_op for block 6

- **Label.** Entered after the Block 5 unseal (2026-11-08); text drafted pre-unseal on 2026-11-07.
- **Status.** Default (no decision attached; the audit's text).
- **Source.** AUD:494 @ `07b9f704b`.

> | # | Amendment | From | Resolves |
> |---|---|---|---|
> | R5 | **b_op for block 6.** Both programs recompose b_op from each session's captures under `configs/b6/registration/acceptance.json` (`ea130c87…`, s_bracket 10.818 ms). The harvest's stored bracket, made under block 5's acceptance, is disclosed only and enters no number. A difference from the acceptance record's `calibration` b_op beyond 1e-6 relative is a refusal, never a flag or a fallback. | seat 1 A5 | F7 |

---

## §17-R6. Exclusions and counting

- **Label.** Entered after the Block 5 unseal (2026-11-08); text drafted pre-unseal on 2026-11-07.
- **Status.** Default (no decision attached; decision 1 makes its code side, C3, mandatory).
- **Source.** AUD:495 @ `07b9f704b`.

> | # | Amendment | From | Resolves |
> |---|---|---|---|
> | R6 | **Exclusions and counting.** The sealed `joulewise.flags.exclusions.compute` with catalog digest `b5bce6c6…` and no pack-scoped window reasons. Counting from `derived/b6-acceptance.json` and the loop record. `claim_usable` is never read. Both programs refuse on disagreement. Tested on r2-gamma's structure. | seat 1 A6; seat 2 C3 | F6 |

---

## §17-R7. Session index and pairing table, registered as structure

- **Label.** Entered after the Block 5 unseal (2026-11-08); text drafted pre-unseal on 2026-11-07.
- **Status.** Default (no decision attached).
- **Source.** AUD:496 @ `07b9f704b`; the pairing table it cites is AUD:271-272.

> | # | Amendment | From | Resolves |
> |---|---|---|---|
> | R7 | **Session index and pairing table, registered as structure.** The nine session ids, rounds and t0 order. The pairing table of F3 (fixed by counting alone, REG §6.2). The tie rule: earlier t0. | seat 1 A7 | F10.7 |

> - **The exposure.** The pairing is GAMMA r1 ↔ (ALPHA r1, BETA r1), r2 ↔ (ALPHA r3, BETA r2) and r3 ↔ (ALPHA r3,
>   BETA r3), with ALPHA r4 floor-only (DESIGN :626-631). So the binder runs three times over cross-session roots.

---

## §17-R8. S-15 fill (decision 7): AWAITING RESEARCH-LEAD RULING

- **Label.** Entered after the Block 5 unseal (2026-11-08); text drafted pre-unseal on 2026-11-07. Once ruled, the
  parts the audit left open also carry "decided after Block 5 outcomes were known" (RL-6 (b)).
- **Status.** **AWAITING RESEARCH-LEAD RULING** (RL-24 seat 5; due 13 November). No option is chosen here.
- **Source.** AUD:497 @ `07b9f704b`; decision 7 at AUD:153-156.

> | # | Amendment | From | Resolves |
> |---|---|---|---|
> | R8 | **S-15 fill** (decision 7). DESIGN §8's meter-only per-phase definition (BAT-2 settled as meter-only, REG:1030-1035), with both producers named or the line labelled single-implementation. Block 5's per-phase value: computed after the block-5 release by block-6 code, or "block 5: not computed". | seat 1 A8; seat 2 #6 | F10.2 |

- **Decision 7, as the audit wrote it (AUD:153-156).**

> 7. **S-15 and §10's whole-machine Q.**
>    - Adopt DESIGN §8's meter-only per-phase definition. Label it single-implementation, or name a second producer.
>    - Then rule on block 5's side of §10. Either block 5's per-phase value is computed after the block-5 release by
>      block-6 code (a new block-5 number), or §10 prints "block 5: not computed".

- **The options, set out.** The first sentence of decision 7 is written as an instruction ("Adopt DESIGN §8's
  meter-only per-phase definition") and R8's text carries it, so the definition is drafted as the default. The
  research lead may treat it as open too. The two choices the audit leaves open:

  **7a. Who produces the per-phase line.**
  - 7a-i. Label it single-implementation.
  - 7a-ii. Name a second producer.

  **7b. Block 5's side of §10 (RL-24: "7 (second half)").**
  - 7b-i. Block 5's per-phase value is computed after the Block 5 release by Block 6 code: a new Block 5 number.
  - 7b-ii. §10 prints "block 5: not computed".

- **What each seat proposed, for the record (not a recommendation of the audit).**
  - Seat 1, A8 (AUD:695):

> | A8 | **S-15 fill.** Adopt a written per-phase whole-machine definition (DESIGN §8 is the candidate), name both producers, label block 5's per-phase value as computed after the block-5 release by the block-6 code. | F9.1 | New disclosure line only |

  - Seat 2, item 6, S-15 (AUD:905):

>    - S-15: the meter-only definition of design §8, labelled as a single-implementation descriptive line (or name a second implementation).

  - The finding behind it, F10.2 (AUD:415-418):

> 2. **§9.5 item 5 / S-15** (REG:1028-1035, :1208).
>    - REG says the per-phase whole-machine definition is "the one committed for block 5". But B5-PLAN §8.2 is
>      request-level ("the harvest computes no phase-level figures", `analysis_plan_block5.md:654`).
>    - The per-phase line exists only in the recompute (DESIGN §0 item 5), and DESIGN §8 is the candidate definition.

- **Bears on a printed number?** 7b-i creates a Block 5 number that Block 5's release did not print. 7a and 7b-ii
  change no number.

---

## §17-R9. Estimand text (decision 8): four items AWAITING RESEARCH-LEAD RULING

- **Label.** Entered after the Block 5 unseal (2026-11-08); text drafted pre-unseal on 2026-11-07. Once ruled, the
  four open items also carry "decided after Block 5 outcomes were known" (RL-6 (b)).
- **Status.** Split. The parts of R9 that decision 8 does not cover are the default: the §10 edge cases
  (non-computable Q left out, with n reduced and named; n = 1 prints "not defined"; "block 5: not computed") and
  "§11.2 excludes binding-defect `not_estimable`". The four items of decision 8 are **AWAITING RESEARCH-LEAD RULING**
  (due 13 November). No option is chosen here.
- **Source.** AUD:498 @ `07b9f704b`; decision 8 at AUD:157-161; findings F10.1, F10.3, F10.4 and F10.6 at
  AUD:410-429.

> | # | Amendment | From | Resolves |
> |---|---|---|---|
> | R9 | **Estimand text** (decision 8). §9.5 item 3's T weighting and E_ref/T_ref basis. A §10 label for the s_bracket regime difference, with a labelled block-6-only summary beside it. The §10 edge cases (non-computable Q left out, with n reduced and named; n = 1 prints "not defined"; "block 5: not computed"). §11.2 excludes binding-defect `not_estimable`. J6 line in or out. | seat 1 A9; seat 2 #7 | F10 |

- **Decision 8, as the audit wrote it (AUD:157-161).**

> 8. **Estimand wording.** Rule on four items:
>    - §9.5 item 3's T: estimator-1 weights (DESIGN) or the plain mean over kept members (RC-B6-1).
>    - The E_ref/T_ref basis.
>    - The J6 timing-bound sensitivity line: in or out.
>    - A §10 label for the block-5/block-6 s_bracket difference.

- **The options, set out.**

  **8a. §9.5 item 3's T** (REG:1018: "E and T are the cell's estimator-1 mean and mean phase length").
  - 8a-i. Estimator-1 weights: 0.2 × the repeat mean + 0.8 × the quad-run mean (DESIGN :659-662).
  - 8a-ii. The plain mean over kept repeat and quad members (RC-B6-1:560-561).

  **8b. The E_ref/T_ref basis** (REG:1018-1019: "E_ref, T_ref the means over the surviving references that set the
  allowance").
  - 8b-i. State it as the start, midpoint and end references' request energy and length, which both implementations
    use (F10.1, AUD:413-414). Seat 2's reason: "When the bound term binds, the corpus sets the allowance" (AUD:817).
  - 8b-ii. Leave REG:1018-1019's wording as registered.

  **8c. The J6 timing-bound sensitivity line.**
  - 8c-i. In: printed for Block 6, as L9 run unchanged would print it.
  - 8c-ii. Out: not printed for Block 6, as RC-B6-1 drops it (open issue 5).

  **8d. A §10 label for the Block 5/Block 6 s_bracket difference.** R9's text puts "a labelled block-6-only summary
  beside it". The audit gives no label wording, and the label's wording is the research lead's.

- **The findings behind it (verbatim).**

> 1. **§9.5 item 3, T** (REG:1016-1018). DESIGN :659-662 uses estimator-1 weights: 0.2 × the repeat mean + 0.8 × the
>    quad-run mean. RC-B6-1:560-561 uses the plain mean over repeat and quad members. The two are identical only for a
>    complete cell: 10 repeats and 10 quads of 4 give 10/50 = 0.2 and 40/50 = 0.8. Any cell with unequal losses
>    differs. The text should also state the E_ref/T_ref basis exactly: the start, midpoint and end references'
>    request energy and length.

> 3. **§10** (REG:1058-1078).
>    - Its floor summaries mix two s_bracket regimes. Block 5 used 14.531 ms and block 6 uses 10.818 ms, which REG
>      sizes at up to 3.713 ms, or 0.175 J of floor (REG:378-387). Seat 2's "about 0.17 J" matches.
>    - Three edge cases are unregistered: Q not computable, n = 1, and "block 5: not computed". The 2026-10-27 lead
>      ruling fixed their wording in the driver (`RUN_STATE.md:310`), not in REG.
> 4. **§11.2.** When the cause is a binding defect (F3), a `not_estimable` block-6 session prints "not replicated". The
>    dry-run completion criterion has to exclude that case.

> 6. **The J6 timing-bound sensitivity line** (RC-B6-1 open issue 5) is not in REG §9.5, but L9 run unchanged would
>    print it. Rule it in or out.

- **Bears on a printed number?** 8a: yes. "The two are identical only for a complete cell" and "Any cell with
  unequal losses differs" (AUD:411-413). This affects only §9.5 item 3's scaled-allowance line, one of the labelled
  lines "none of which changes a registered number" (REG:1012). 8b: possibly, through E_ref and T_ref, on that same
  line. 8c: it adds or removes a labelled line. 8d: no number changes.

---

## §17-R10. S-9, S-11 and S-8

- **Label.** Entered after the Block 5 unseal (2026-11-08); text drafted pre-unseal on 2026-11-07.
- **Status.** Default.
- **Source.** AUD:499 @ `07b9f704b`.

> | # | Amendment | From | Resolves |
> |---|---|---|---|
> | R10 | **S-9, S-11 and S-8.** Merge PR #529's §17 entry, or enter it again. Register that P_x, T_phase, E_add and the removal counts are hazard structure, computed and reported before the dry run. The production path implements the E_add alternative and the P* desk exclusion, including GAMMA's per-model P*. Name the E_add code as part of S-14. | seat 1 A10; seat 2 #6, #8 | F6, F10.5 |

- **Drafting note (not entry text).** PR #529 (`lane/2026-10-22-b6-s9-s11`) is still open as of 2026-11-10. This
  draft does not read its values.

---

## §17-R11. Inputs and reading (decision 9): read path AWAITING RESEARCH-LEAD RULING

- **Label.** Entered after the Block 5 unseal (2026-11-08); text drafted pre-unseal on 2026-11-07. Once ruled, the
  read path also carries "decided after Block 5 outcomes were known" (RL-6 (b)).
- **Status.** Split. Default: the citation of tag `b6/collection` and the S-3, S-4 and S-18 digests, the
  vendoring into S-14, input authentication, and `trace_plist_missing` as a STOP. **AWAITING RESEARCH-LEAD RULING**
  (decision 9, due 13 November): "one named path" for reading `.zst`, and the host. No option is chosen here.
- **Source.** AUD:500 @ `07b9f704b`; decision 9 at AUD:162-166; the options at F5, AUD:327-331.

> | # | Amendment | From | Resolves |
> |---|---|---|---|
> | R11 | **Inputs and reading.** Cite tag `b6/collection` (`f31aca19f`) and the S-3, S-4 and S-18 digests, and vendor those files into S-14. The production path authenticates its inputs: the archive `SHA256SUMS`, the `harvest.json` and acceptance digests, and the desk-compression rows, checking decompressed SHA-256. It reads `.zst` through one named path (decision 9). `trace_plist_missing` stays a STOP. | seat 1 A11; seat 2 C1 | F5, F8, F12 |

- **Decision 9, as the audit wrote it (AUD:162-166).**

> 9. **Host and read path.**
>    - The host: this Air has 54 GiB free now, against 32.75-38.82 GiB per session decompressed. The MBP belongs to the
>      magistrate.
>    - The read path: stdlib `compression.zstd` streaming, `desk_compress.read_bytes` (needs the zstd binary), or an
>      APFS in-place restore.

- **The options, set out.**

  **9a. The read path** (F5, AUD:327-331):

> - **Options.**
>   - `compression.zstd` streaming, with a SHA-256 check against the desk record. It is stdlib in Python 3.14.6, present
>     on this Air, but python3.13, which the runbooks pin, lacks it (verified).
>   - `desk_compress.read_bytes`.
>   - An APFS in-place restore per unit (DESIGN §0 item 8). B6-AN-1 A7 exercised it on synthetic trees only.

  **9b. The host.**
  - 9b-i. The Air.
  - 9b-ii. The MBP, which "belongs to the magistrate" (AUD:164).

- **Facts recorded since 2026-11-07 (not a ruling).** RL-11 recommends that the magistrate make "one custody copy of
  the Block 6 sessions to the Air", and RL-24 lists "the Block 6 custody copy to the Air by 15 November" as an MBP
  desk step. Whether that settles 9b is the research lead's call. AUD's free-disk figure (54 GiB) is from
  2026-11-07 and has not been re-measured for this draft.
- **Bears on a printed number?** No, provided each decompressed file is checked against its recorded SHA-256, as R11
  requires.

---

## §17-R12. Fixtures before S-14 is cut

- **Label.** Entered after the Block 5 unseal (2026-11-08); text drafted pre-unseal on 2026-11-07.
- **Status.** Default.
- **Source.** AUD:501 @ `07b9f704b`.

> | # | Amendment | From | Resolves |
> |---|---|---|---|
> | R12 | **Fixtures before S-14 is cut.** Production-shaped synthetic sessions generated by the real chain at `f31aca19f` (DESIGN §16). They must cover: waited runs with attempt-N telemetry; wait-cap and budget skips; `anchor_not_bounded` members; campaign logs that mix executed-member rows and the trailing whole-window evaluation row; compressed campaign logs and plists; and one cross-session GAMMA unit. | seat 1 A12; seat 2 C4 | F3, F11 |

---

## Points for the research lead's review (not rulings; not among decisions 7, 8 and 9)

1. **R0's signer statement.** R0 says "The signer states that no block-5 or block-6 outcome has been seen"
   (AUD:489). That is not true after 2026-11-08. This draft puts RL-6's blind-status line in its place (above). The
   research lead confirms or rewords.
2. **R0's deadline (decision 3).** The recommended deadline, "land R1-R12 before the block-5 unseal" (AUD:138),
   was missed. RL-6 (b) enters the set after the unseal, which departs from decision 3. By RL-6 (b)'s own rule a
   departure is labelled "decided after Block 5 outcomes were known". This draft proposes that label for R0's
   deadline clause only, for the research lead to confirm.
3. **Decision 3's second half.** "After it, allow only entries that fix a tooling defect and choose no rule,
   labelled as such" (AUD:138-139). Read literally, it would bar R1-R12 and the rulings on 7, 8 and 9. RL-6 (b)
   supersedes it for this set. Whether it governs entries after this set is the research lead's call.
4. **R1's "Correct §1.10 and `CANONICAL.md:48`".** The CANONICAL row correction is also NBD B6-02's proposal, and
   RL-24 seat 1 edits `CANONICAL.md`. It is not drafted here, to avoid colliding with that seat.
