# Block 6 registration §17 entries: draft, ruled by the research lead (2026-11-10)

**What this file is.** The drafted §17 change-log entries for `docs/registrations/block6_replication_DRAFT.md`
(called **REG** below) that research-lead ruling RL-6 (b) orders and RL-24 seat 5 assigns. The research lead ruled
the audit's open decisions 7, 8 and 9 and the drafter's flags in RL-25 (2026-11-10 20:07 PST, RL:643-730), and
admitted this draft with edits; those edits are applied below. The Sol executing refuter's report (`docs/run_reports/2026-11-10-b6-s17-refuter.md`) raised
five findings, S17-01 to S17-05; the research lead accepted all five and ruled 7b in RL-30 (RL:855-930), and those
dispositions are applied below. It is still a draft: nothing here is entered in REG by it, the later PR that enters the
entries goes to the research lead (RL-30), and REG is unchanged by the commits that add this file. REG §17 ends with the
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

**RL-25's label and principle, verbatim (RL:648-656).**

> Every ruling here carries the label **"decided after Block 5 outcomes were known"**, as RL-6 (b) requires.
> I have seen Block 5's released per-phase whole-machine values and its scaled-allowance line
> (`RESULTS.md` §4.4, §4.5). The choices below rest on the registered text and on which program computes what.
> None was made by looking at what a value would favour.
>
> **One principle for all three decisions.** Where the Block 5 release's pinned program already computes a
> quantity, Block 6 uses that program's rule, found by reading its code, and no Block 5 number is computed anew.
> That is item 37's "block 5's registered arithmetic unchanged" applied to the labelled lines. Where no Block 5
> rule exists, the registered text decides, and where it is silent the line is not added.

**Sources and how they are cited.**

| Alias | File | Commit | Notes |
|---|---|---|---|
| AUD | `docs/research-audits/2026-11-07/block6-design.md` | `07b9f704b` (2026-11-07 16:53:41 -0800) | On `origin/research/2026-11-07-block6-design`; merged into `research/2026-11-07-audit-burn` (PR #695, open) at `1572b2e62`. The blob (`9ebf356d2e3b`) is identical on both. Not on `main` |
| RL | `docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md` | `ce4d42571` (`origin/audit/2026-11-10-fable`) | The research lead's rulings; not on `main`. Lines 1-775 are byte-identical to `9f536d876` and lines 1-640 to `5de56400f`, which earlier drafts cited |
| DLE | `docs/analysis/b5/DEVIATION-LOG.md` | `60d3225ee` (`origin/main`) | DLE-2 entered at `422576dc5` (2026-11-06); its text is byte-identical to `d8c17dff4` (2026-11-06 15:17 PST) |

`AUD:489` means line 489 of AUD at `07b9f704b`. Every block quotation from AUD, DLE and RL below is copied from
those bytes by a script, line for line; the only change is the `> ` prefix. The one exception is the signing statement
below, which is extracted from RL:701-704 and reflowed (refuter finding S17-05).

**The label every entry carries.** "Entered after the Block 5 unseal (2026-11-08); text drafted pre-unseal on
2026-11-07." For the DLE-2 entry the drafting date is DLE-2's adoption date, 2026-11-06, as RL-6 (b) says.

**Signing statement, for entry.** AUD:483 says each entry "is signed blind, extending the DLE signing statement to
block 6". That statement can no longer be made about Block 5: Block 5 was unsealed on 2026-11-08 (`RUN_STATE.md` item
231). RL-25 flag 1 fixes the statement these entries carry. The block below is extracted from RL:701-704 and
reflowed: the numbered introducer and the outer quotation marks are removed, and the words are unchanged (S17-05,
RL:909).

> Signed blind to Block 6: neither the signer nor the drafter has seen a Block 6 energy, floor, ratio, contrast or
> outcome word. Not blind to Block 5, whose released outcome words and numbers both have seen. Entry texts marked
> 'drafted pre-unseal' are quoted from texts dated 2026-11-06 and 2026-11-07.

Drafter's disclosure (Opus 5.5, seat 5): I read no Block 6 outcome, result file or restricted path. I read the
registration, the audits, the rulings, the deviation log and `RUN_STATE.md`; in doing so I saw Block 5's released
outcome words and headline numbers (`RUN_STATE.md` item 232). Every entry text below was written on 2026-11-06 or
2026-11-07, before the unseal, except the RL-25 rulings, which are quoted from the research lead's log; I wrote only
the framing and the notes.

**Status words.** **Default** means the audit's recommended option, or its text where no decision is attached, to be
entered as drafted. **Ruled (RL-25)** means the audit chose no option and the research lead ruled it in RL-25; such
an entry, or the ruled part of it, also carries "decided after Block 5 outcomes were known" (RL:648). Changes made
under RL-30 carry the same label (RL:858-859).

**Kind.** Every entry names its kind, using RL-30's classification (S17-01, RL:878-887), verbatim:

> Each entry gains a **Kind** line:
>
> - slot fill: R2 (S-13's missing parameter), R4 (S-14), R8 (S-15), R10 (S-9, S-11, S-8);
> - clarification, no number changes: R5, R6, R7, and R9's items 8b, 8d and the §10 and §11.2 edge cases;
> - interpretation of a labelled line, with the alternative printed beside: R9's item 8a; nothing added: 8c;
> - tooling or coverage: R3, R11, R12;
> - **deviation from the registered release procedure**: R1 with §17-DLE2. They change which program prints the
>   numbers and how agreement is shown (§12.3 items 3 and 4, §13). They change no estimator. What shows that the
>   printing program computes the registered arithmetic is DLE-2's agreement gate: exit 0 on the Block 5 dry-run
>   custody with every family agreeing, and again on the first counting Block 6 session.

R0: framing entry (RL-34).

**How the entries get into REG (proposed, for the research lead).** After the research lead's review and rulings and the refuter's check, each entry is
appended to REG §17 as one dated line in the existing style, pointing at this file for the full text, and the slot
rows it fills (S-13, S-14, S-15, S-9, S-11) are updated in the same commit. That commit is a separate PR.

---

## Map: the audit's eleven decisions and where each lands

| Decision (AUD §1) | Audit recommendation | Entry | Status in this draft |
|---|---|---|---|
| 1. Production architecture (AUD:95-113) | (c), with C3 mandatory | §17-R1 | Default |
| 2. S-13 printed precision (AUD:114-134) | Strictest value per family | §17-R2 | Default |
| 3. Amendment deadline (AUD:135-139) | Before the Block 5 unseal | §17-R0 | Missed; RL-25 flags 3 and 5 rule later entries and the deviation line; RL-30 (S17-01) sets the deadline clause |
| 4. The D5 r4 lane (AUD:140-143) | Push, review, tag `b5/analysis-r4` | §17-R4 | Default (the tag now exists) |
| 5. Audit unfinished at release (AUD:144-145) | Hold | §17-R1 | Default (RL-6 (b) says the same) |
| 6. Coverage, family by family (AUD:146-152) | (b) count-type, (a) both whole-machine lines | §17-R3 | Default |
| 7. S-15 and §10's whole-machine Q (AUD:153-156) | None | §17-R8 | Ruled (RL-25, RL-30): 7a-i; 7b settled at the S-14 pin by seat 7's two tests, else 7b-ii |
| 8. Estimand wording (AUD:157-161) | None | §17-R9, four items | Ruled (RL-25): 8a-i, 8b-i, 8c out, 8d label |
| 9. Host and read path (AUD:162-166) | None | §17-R11, read path | Ruled (RL-25): 9a `desk_compress.read_bytes`; 9b the Air |
| 10. L9-ENV-3 mirror deletion (AUD:167-168) | Hold it | none | Not registration text (code precondition C5) |
| 11. One structure-only probe (AUD:169-176) | Run it, counts only | none | Not registration text; an action for the lead |

---

## §17-DLE2. The production program for blocks 6 onward (DLE-2, owed)

- **Label.** Entered after the Block 5 unseal (2026-11-08); text adopted pre-unseal on 2026-11-06 (DLE-2).
- **Kind.** Deviation from the registered release procedure, with §17-R1 (RL-30, RL:884-887).
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
- **Precedence (RL-30, S17-04, RL:906-907).** For exclusions, item 2's "not re-derived" is superseded by C3 and
  §17-R6, which re-derive Block 6's exclusions under the Block 6 catalog. The DLE-2 quotation above stays as it is.

---

## §17-R0. Framing entry

- **Label.** Entered after the Block 5 unseal (2026-11-08); text drafted pre-unseal on 2026-11-07. The deadline
  clause is ruled (RL-30, S17-01) and carries "decided after Block 5 outcomes were known".
- **Kind.** Framing entry. It states once that this set was entered after the Block 5 unseal (RL-25 flag 5). It changes no rule, no number and no procedure. (RL-34)
- **Status.** Default, with two clauses as ruled: the signer statement is RL-25 flag 1's (in the header above), and
  the deadline clause is RL-30's (S17-01), which replaces RL-25 flag 2's wording. By RL-25 flag 5, R0 with that clause
  is the one deviation line for the late entries.
- **Source.** AUD:489 @ `07b9f704b`, with the section preamble AUD:483-485 and decision 3, AUD:135-139; RL-25 flags
  2, 3 and 5 at RL:705-711 and RL:715-716; RL-30 S17-01 at RL:867-876.

> - Each entry is signed blind, extending the DLE signing statement to block 6, and is checked by one executing refuter.
> - No entry changes registered arithmetic.
> - The order is what blocks what.

> | # | Amendment | From | Resolves |
> |---|---|---|---|
> | R0 | **Framing entry.** Block 6 is collected and blinded, and these entries are made under §12.4 before release. The signer states that no block-5 or block-6 outcome has been seen. The deadline is decision 3. | seat 2 #1 | §0 premise |

- **The deadline clause, as entered (RL-30, S17-01, RL:867-876), verbatim.** It replaces RL-25 flag 2's wording,
  which said §12.4 "allows entries until the Block 6 release"; RL-30 corrects that.

> **S17-01 (authority): fix. This corrects my own wording in RL-25 flag 2.** §12.4 does not "allow entries until
> the release". The registration's header says a change after its commit is a dated §17 entry with its reason,
> and §12.4 says what such a change may touch: never registered arithmetic; a §8 rule found wrong, with the
> original result beside it. R0's deadline clause becomes:
>
> > "The audit's deadline, before the Block 5 unseal, was not met. These entries are made after it. Each is a
> > dated §17 entry with its reason, as this registration's header requires for any change after its commit. None
> > changes registered arithmetic (§12.4). Each names its kind: a slot fill this registration owes; a
> > clarification that changes no number; a tooling or coverage entry; or a deviation from the registered release
> > procedure of §12.3 and §13. Decided after Block 5 outcomes were known."

- **RL-25 flags 2 (superseded by RL-30 as to the clause's wording), 3 and 5 (verbatim, RL:705-711 and RL:715-716).**

> 2. *R0's deadline.* Yes. R0's deadline clause reads: "The audit's deadline, before the Block 5 unseal, was not
>    met. These entries are made after it, under §12.4, which allows entries until the Block 6 release. Decided
>    after Block 5 outcomes were known."
> 3. *Later entries.* The second half of the audit's decision 3 governs from the day this set is entered: only
>    an entry that fixes a tooling defect and chooses no rule, labelled as such. Anything else needs a
>    research-lead ruling, carries "decided after Block 5 outcomes were known", and prints the alternative where
>    a number changes.

> 5. *One deviation line for the late entries.* R0, with flag 2's clause, is that line. No separate entry. Paper
>    1's deviation list names it.

- **Decision 3, as the audit wrote it (AUD:135-139).**

> 3. **Amendment deadline.** REG §12.4 allows §17 entries while block 6 is blinded, that is, up to the block-6 release.
>    Both seats prefer a deadline before the block-5 unseal, and seat 1 would register "no amendments after". After the
>    unseal the signer has seen block-5 outcomes, so a blind statement is no longer credible.
>    **Recommendation:** land R1-R12 before the block-5 unseal. After it, allow only entries that fix a tooling defect
>    and choose no rule, labelled as such.

---

## §17-R1. Production program and second side (decisions 1 and 5)

- **Label.** Entered after the Block 5 unseal (2026-11-08); text drafted pre-unseal on 2026-11-07.
- **Kind.** Deviation from the registered release procedure (§12.3 items 3 and 4, §13), with §17-DLE2. It changes which
  program prints the numbers and how agreement is shown, and no estimator; DLE-2's agreement gate shows that the
  printing program computes the registered arithmetic (RL-30, RL:884-887).
- **Status.** Default: decision 1's recommended option (c) with C3, and decision 5's recommended hold. RL-25 flag 6
  adds the L9-audit wording below, which carries "decided after Block 5 outcomes were known".
- **Source.** AUD:490 @ `07b9f704b`; decision 1 at AUD:95-113; decision 5 at AUD:144-145; RL-25 flag 6 at
  RL:717-719.

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

- **The L9 audit under option (c), as ruled (RL-25 flag 6, RL:717-719), verbatim.**

> 6. *R1's audit wording.* Under option (c) the L9 audit is optional. "The audit run" in RL-6 (b) means the
>    registered second side of option (c). Whether an L9 audit is run is decided and recorded before the blind
>    dry run; if one is started, the release holds until it finishes.

- **Drafting notes (not entry text).** RL-6 (b) states the same hold ("If the audit run has not finished when the
  numbers would be released, the release holds"). RL-24 seat 7 builds option (c). Under (c) the "printing program"
  of R1 is RC-B6-1 (`scripts/independent_recompute_b6.py` on `lane/2026-10-27-recompute-b6`); its path and digest
  are filled when seat 7's code is pinned (S-14).

---

## §17-R2. S-13 made definite (decision 2)

- **Label.** Entered after the Block 5 unseal (2026-11-08); text drafted pre-unseal on 2026-11-07.
- **Kind.** Slot fill: S-13's missing parameter (RL-30, RL:880).
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
- **Kind.** Tooling or coverage (RL-30, RL:883).
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

- **Exception (RL-30, S17-03, RL:902-904), verbatim.** It carries "decided after Block 5 outcomes were known".

> **S17-03 (R3 against R8): fix.** R3 states the exception: the request-level whole-machine line is computed and
> compared; the per-phase line is single-implementation under R8. Calling one function from both sides is not a
> second producer.

- **As entered.** The request-level whole-machine line is computed and compared under decision 6 (a). The per-phase
  whole-machine line is single-implementation under §17-R8 and is not compared.

---

## §17-R4. S-14 contents (decision 4)

- **Label.** Entered after the Block 5 unseal (2026-11-08); text drafted pre-unseal on 2026-11-07.
- **Kind.** Slot fill: S-14 (RL-30, RL:880).
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
- **Kind.** Clarification; no number changes (RL-30, RL:881).
- **Status.** Default (no decision attached; the audit's text).
- **Source.** AUD:494 @ `07b9f704b`.

> | # | Amendment | From | Resolves |
> |---|---|---|---|
> | R5 | **b_op for block 6.** Both programs recompose b_op from each session's captures under `configs/b6/registration/acceptance.json` (`ea130c87…`, s_bracket 10.818 ms). The harvest's stored bracket, made under block 5's acceptance, is disclosed only and enters no number. A difference from the acceptance record's `calibration` b_op beyond 1e-6 relative is a refusal, never a flag or a fallback. | seat 1 A5 | F7 |

---

## §17-R6. Exclusions and counting

- **Label.** Entered after the Block 5 unseal (2026-11-08); text drafted pre-unseal on 2026-11-07.
- **Kind.** Clarification; no number changes (RL-30, RL:881).
- **Status.** Default (no decision attached; decision 1 makes its code side, C3, mandatory).
- **Source.** AUD:495 @ `07b9f704b`.

> | # | Amendment | From | Resolves |
> |---|---|---|---|
> | R6 | **Exclusions and counting.** The sealed `joulewise.flags.exclusions.compute` with catalog digest `b5bce6c6…` and no pack-scoped window reasons. Counting from `derived/b6-acceptance.json` and the loop record. `claim_usable` is never read. Both programs refuse on disagreement. Tested on r2-gamma's structure. | seat 1 A6; seat 2 C3 | F6 |

---

## §17-R7. Session index and pairing table, registered as structure

- **Label.** Entered after the Block 5 unseal (2026-11-08); text drafted pre-unseal on 2026-11-07.
- **Kind.** Clarification; no number changes (RL-30, RL:881).
- **Status.** Default (no decision attached).
- **Source.** AUD:496 @ `07b9f704b`; the pairing table it cites is AUD:271-272.

> | # | Amendment | From | Resolves |
> |---|---|---|---|
> | R7 | **Session index and pairing table, registered as structure.** The nine session ids, rounds and t0 order. The pairing table of F3 (fixed by counting alone, REG §6.2). The tie rule: earlier t0. | seat 1 A7 | F10.7 |

> - **The exposure.** The pairing is GAMMA r1 ↔ (ALPHA r1, BETA r1), r2 ↔ (ALPHA r3, BETA r2) and r3 ↔ (ALPHA r3,
>   BETA r3), with ALPHA r4 floor-only (DESIGN :626-631). So the binder runs three times over cross-session roots.

---

## §17-R8. S-15 fill (decision 7): ruled (RL-25)

- **Label.** Entered after the Block 5 unseal (2026-11-08); text drafted pre-unseal on 2026-11-07. The decision-7
  parts are ruled and carry "decided after Block 5 outcomes were known" (RL:648).
- **Kind.** Slot fill: S-15 (RL-30, RL:880).
- **Status.** Ruled (RL-25, RL-30). The first sentence stays the default, with its source made exact; 7a-i; 7b is
  settled at the S-14 pin by seat 7's two acceptance tests, and if it is not shown by then, 7b-ii applies without a
  further ruling (RL-30). The program digest and the differences are listed below (RL-30, S17-02).
- **Source.** AUD:497 @ `07b9f704b`; decision 7 at AUD:153-156; RL-25 decision 7 at RL:658-670; RL-30 at
  RL:861-865, RL:889-900 and RL:911-922; refuter finding S17-02 and its "Decision 7b" section in
  `docs/run_reports/2026-11-10-b6-s17-refuter.md`.

> | # | Amendment | From | Resolves |
> |---|---|---|---|
> | R8 | **S-15 fill** (decision 7). DESIGN §8's meter-only per-phase definition (BAT-2 settled as meter-only, REG:1030-1035), with both producers named or the line labelled single-implementation. Block 5's per-phase value: computed after the block-5 release by block-6 code, or "block 5: not computed". | seat 1 A8; seat 2 #6 | F10.2 |

- **Decision 7, as the audit wrote it (AUD:153-156).**

> 7. **S-15 and §10's whole-machine Q.**
>    - Adopt DESIGN §8's meter-only per-phase definition. Label it single-implementation, or name a second producer.
>    - Then rule on block 5's side of §10. Either block 5's per-phase value is computed after the block-5 release by
>      block-6 code (a new block-5 number), or §10 prints "block 5: not computed".

- **The ruling, verbatim (RL:658-670).**

> **Decision 7 (R8, slot S-15).**
>
> - *First sentence.* It stays the default, with its source made exact. Registration §9.5 item 5 says the
>   definition "is the one committed for block 5". That is the per-phase whole-machine computation the Block 5
>   release executed, in `scripts/independent_recompute_b5.py` at the release-pinned digest. DESIGN §8 is entered
>   as its written statement. Where the two differ, the pinned code governs and the entry lists each difference.
> - *7a: single implementation* (7a-i). The line prints with the label "single implementation; not independently
>   recomputed". If a second producer is ever added, it enters as a tooling entry and the line is then compared.
> - *7b: neither option as written.* Block 5's side of §10 for this quantity is the value its own release
>   produced, which exists. This holds on one condition, settled by structure before any Block 6 number is read:
>   Block 6's line is produced by the same pinned Block 5 function. If that function cannot produce Block 6's
>   line unchanged, 7b-ii applies and §10 prints "block 5: not computed" for this quantity. 7b-i is refused: no
>   Block 5 number is computed by Block 6 code.

- **The pinned program (RL-30, RL:861-865), verbatim.**

> **Release digest, confirmed as far as git can.** `scripts/independent_recompute_b5.py` has SHA-256
> `d49103e884ccae47242b8efb91ea1f5764e4505a4ad5e54558cc42a399a2e4e0` at `02ef89f5c`, the commit the release
> check ran from (`RUN_STATE.md` item 229), at `ab1e0098d` and on `main`. Item 229 and `RESULTS.md` record the
> release recompute as `d49103e8…`. The Block 5 re-derivation reader (RL-24 seat 4) confirms the full digest from
> the release check's own record.

- **The differences and how they are ruled (RL-30, S17-02, RL:889-900), verbatim.**

> **S17-02 (R8 lists no differences and no digest): fix.** R8 names the digest above and lists the differences
> the refuter found. They are ruled as follows. "Unchanged" in RL-25's 7b condition means the arithmetic call
> chain: `machine_member`, `sampled_gross`, `phase_machine_mean` with `diagnostic_estimate` and
> `reported_estimate`, and the edge-shift corner logic inside `add_machine`. Labels and disclosures around that
> chain follow the Block 6 registration:
>
> - the flag is the registered one (§9.5 item 5: a phase whose request shows the battery assisting the adapter),
>   taken from the harvest's `battery.assist` member flag; the pinned program's battery-activity count prints as
>   it does;
> - no without-assisted per-phase value is added: §9.5 item 2 applies to the estimates of the Block 5 plan, and
>   item 5 asks only for the flag;
> - the boundary sentence printed is the registration's.

- **The differences the refuter listed** (`docs/run_reports/2026-11-10-b6-s17-refuter.md`, S17-02; I is
  `scripts/independent_recompute_b5.py` at the digest above, DESIGN is `docs/design/b6_analysis_additions.md` at
  `bb9669b69`), each with RL-30's disposition:
  1. **Battery flag.** I counts request battery *activity* from any nonzero B0AC (I:1999-2004, :2318-2321) and carries
     the archived `meter.battery_activity` flag (I:2457-2462). DESIGN (:730-745, :845) and REG §9.5 item 5 use the
     registered `battery.assist` rule. *Ruled:* the flag is the registered one, taken from the harvest's
     `battery.assist` member flag; the pinned program's battery-activity count prints as it does.
  2. **Without-assisted per-phase value.** DESIGN asks for one; I's per-phase wrapper (I:2509-2537) has none.
     *Ruled:* none is added; §9.5 item 2 applies to the Block 5 plan's estimates and item 5 asks only for the flag.
  3. **Boundary sentence.** I's boundary string (I:79-81) differs from REG's literal sentence (REG:1035-1036) and from
     DESIGN's appended sentence (:743-745). *Ruled:* the boundary sentence printed is the registration's.

- **7b, as ruled (RL-30, RL:911-922), verbatim.**

> **Decision 7b.** The condition can hold and does not yet. So:
>
> - The Block 6 analysis-path seat (RL-24 seat 7) wires the pinned functions in. Every arithmetic step of the
>   per-phase line, the edge-shift corners included, executes from the script at the pinned digest. The seat
>   supplies decompressed, hash-checked meter streams and the session's bounds from outside; it may place those
>   streams in a temporary directory so the pinned code's own reader runs. It does not copy or rewrite the
>   arithmetic.
> - Acceptance: a test that the loaded script's SHA-256 is the pinned digest, and a test that on one synthetic
>   session the Block 6 per-phase output equals the Block 5 program's own output on the same input.
> - This is settled at the S-14 pin, before any Block 6 number is read. If it is not shown by then, 7b-ii
>   applies without a further ruling: §10 prints "block 5: not computed" for this quantity, and Block 5's
>   released values print only in their own table.

- **As entered.** The per-phase line prints with the label "single implementation; not independently recomputed"
  (RL-25, 7a-i). Its arithmetic is the call chain of `scripts/independent_recompute_b5.py` at SHA-256
  `d49103e884ccae47242b8efb91ea1f5764e4505a4ad5e54558cc42a399a2e4e0`: `machine_member`, `sampled_gross`,
  `phase_machine_mean` with `diagnostic_estimate` and `reported_estimate`, and the edge-shift corner logic inside
  `add_machine`. DESIGN §8 is its written statement; where the two differ, the pinned code governs, and the three
  differences above are disposed of as RL-30 rules. §10's Block 5 value for this quantity is Block 5's released value
  if, at the S-14 pin, seat 7 shows both tests: the loaded script's SHA-256 is the pinned digest, and on one synthetic
  session the Block 6 per-phase output equals the Block 5 program's own output on the same input. Otherwise 7b-ii
  applies without a further ruling: §10 prints "block 5: not computed" for this quantity, and Block 5's released values
  print only in their own table. No Block 5 number is computed by Block 6 code.
- **The finding behind it, F10.2 (AUD:415-418).**

> 2. **§9.5 item 5 / S-15** (REG:1028-1035, :1208).
>    - REG says the per-phase whole-machine definition is "the one committed for block 5". But B5-PLAN §8.2 is
>      request-level ("the harvest computes no phase-level figures", `analysis_plan_block5.md:654`).
>    - The per-phase line exists only in the recompute (DESIGN §0 item 5), and DESIGN §8 is the candidate definition.

---

## §17-R9. Estimand text (decision 8): ruled (RL-25)

- **Label.** Entered after the Block 5 unseal (2026-11-08); text drafted pre-unseal on 2026-11-07. The four
  decision-8 items are ruled and carry "decided after Block 5 outcomes were known" (RL:648).
- **Kind.** Split (RL-30, RL:881-882). Items 8b and 8d and the §10 and §11.2 edge cases: clarification, no number
  changes. Item 8a: interpretation of a labelled line, with the alternative printed beside. Item 8c: nothing added.
- **Status.** The parts of R9 that decision 8 does not cover are the default: the §10 edge cases (non-computable Q
  left out, with n reduced and named; n = 1 prints "not defined"; "block 5: not computed") and "§11.2 excludes
  binding-defect `not_estimable`". The four items of decision 8 are ruled (RL-25): 8a-i, 8b-i, 8c out (8c-ii), and the
  8d label text.
- **Source.** AUD:498 @ `07b9f704b`; decision 8 at AUD:157-161; findings F10.1, F10.3, F10.4 and F10.6 at
  AUD:410-429; RL-25 decision 8 at RL:672-687.

> | # | Amendment | From | Resolves |
> |---|---|---|---|
> | R9 | **Estimand text** (decision 8). §9.5 item 3's T weighting and E_ref/T_ref basis. A §10 label for the s_bracket regime difference, with a labelled block-6-only summary beside it. The §10 edge cases (non-computable Q left out, with n reduced and named; n = 1 prints "not defined"; "block 5: not computed"). §11.2 excludes binding-defect `not_estimable`. J6 line in or out. | seat 1 A9; seat 2 #7 | F10 |

- **Decision 8, as the audit wrote it (AUD:157-161).**

> 8. **Estimand wording.** Rule on four items:
>    - §9.5 item 3's T: estimator-1 weights (DESIGN) or the plain mean over kept members (RC-B6-1).
>    - The E_ref/T_ref basis.
>    - The J6 timing-bound sensitivity line: in or out.
>    - A §10 label for the block-5/block-6 s_bracket difference.

- **The ruling, verbatim (RL:672-687).**

> **Decision 8 (R9).**
>
> - *8a: estimator-1 weights* (8a-i). The registered sentence names "the cell's estimator-1 mean", and the same
>   weights form E and the cell's bound B. Where the plain-mean factor would differ (a cell with unequal losses),
>   it prints beside the registered one, labelled.
> - *8b: stated exactly* (8b-i): E_ref and T_ref are the means of the start, midpoint and end references'
>   request energy and length. This is a clarification to what both programs do; no alternative prints.
> - *8c: out* (8c-ii). The J6 line is not among §9.5's eight labelled lines. A line is not added to a
>   registration after the block it replicates was unsealed. If an optional L9 audit run prints it, it stays in
>   that run's output.
> - *8d: the label.* "Block 5's floors were formed under its own calibration acceptance (minimum bracket
>   allowance 14.531 ms) and Block 6's under its own (10.818 ms). The difference, up to 3.713 ms of timing bound
>   and up to 0.175 J of floor by the registration's sizing, comes from the registered rule and not from the
>   machine. The summary over Block 6 sessions alone is printed beside the summary over all sessions." It sits on
>   every §10 row whose quantity contains the operative timing bound: floors, attribution floors, the bound B,
>   D, intervals, decision intervals and floor gates.

- **Alternatives printed beside.** 8a: where the plain-mean factor differs (a cell with unequal losses), it prints
  beside the registered one, labelled. 8b: none ("no alternative prints"). 8c: none; the J6 line stays in an optional
  L9 audit run's output if one prints it. 8d: the Block-6-only summary prints beside the all-sessions summary.

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

---

## §17-R10. S-9, S-11 and S-8

- **Label.** Entered after the Block 5 unseal (2026-11-08); text drafted pre-unseal on 2026-11-07.
- **Kind.** Slot fill: S-9, S-11 and S-8 (RL-30, RL:880).
- **Status.** Default.
- **Source.** AUD:499 @ `07b9f704b`.

> | # | Amendment | From | Resolves |
> |---|---|---|---|
> | R10 | **S-9, S-11 and S-8.** Merge PR #529's §17 entry, or enter it again. Register that P_x, T_phase, E_add and the removal counts are hazard structure, computed and reported before the dry run. The production path implements the E_add alternative and the P* desk exclusion, including GAMMA's per-model P*. Name the E_add code as part of S-14. | seat 1 A10; seat 2 #6, #8 | F6, F10.5 |

- **Drafting note (not entry text).** PR #529 (`lane/2026-10-22-b6-s9-s11`) is still open as of 2026-11-10. This
  draft does not read its values.

---

## §17-R11. Inputs and reading (decision 9): ruled (RL-25)

- **Label.** Entered after the Block 5 unseal (2026-11-08); text drafted pre-unseal on 2026-11-07. The read path and
  host are ruled and carry "decided after Block 5 outcomes were known" (RL:648).
- **Kind.** Tooling or coverage (RL-30, RL:883).
- **Status.** Default: the citation of tag `b6/collection` and the S-3, S-4 and S-18 digests, the vendoring into S-14,
  input authentication, and `trace_plist_missing` as a STOP. Ruled (RL-25): the "one named path" is
  `desk_compress.read_bytes` (the `zstd` binary, streamed, with each file's decompressed SHA-256 checked against the
  desk-compression record before a byte is parsed; a missing binary or a digest mismatch is a STOP; the binary's path
  and version go in the run record), and the host is the Air, from a custody copy verified against the archive's
  `SHA256SUMS`.
- **Source.** AUD:500 @ `07b9f704b`; decision 9 at AUD:162-166; the options at F5, AUD:327-331; RL-25 decision 9 at
  RL:689-697.

> | # | Amendment | From | Resolves |
> |---|---|---|---|
> | R11 | **Inputs and reading.** Cite tag `b6/collection` (`f31aca19f`) and the S-3, S-4 and S-18 digests, and vendor those files into S-14. The production path authenticates its inputs: the archive `SHA256SUMS`, the `harvest.json` and acceptance digests, and the desk-compression rows, checking decompressed SHA-256. It reads `.zst` through one named path (decision 9). `trace_plist_missing` stays a STOP. | seat 1 A11; seat 2 C1 | F5, F8, F12 |

- **Decision 9, as the audit wrote it (AUD:162-166).**

> 9. **Host and read path.**
>    - The host: this Air has 54 GiB free now, against 32.75-38.82 GiB per session decompressed. The MBP belongs to the
>      magistrate.
>    - The read path: stdlib `compression.zstd` streaming, `desk_compress.read_bytes` (needs the zstd binary), or an
>      APFS in-place restore.

- **The ruling, verbatim (RL:689-697).**

> **Decision 9 (R11).**
>
> - *9a: `desk_compress.read_bytes`.* The `zstd` binary, streamed, with each file's decompressed SHA-256 checked
>   against the desk-compression record before a byte is parsed. A missing binary or a digest mismatch is a STOP.
>   The binary's path and version go in the run record. Not `compression.zstd`: it needs Python 3.14 and would
>   change the interpreter under every number. Not an in-place restore: it was exercised only on synthetic trees
>   and needs the disk a streamed read does not.
> - *9b: the Air* (9b-i), from a custody copy verified against the archive's `SHA256SUMS`. The MBP stays with the
>   magistrate.

- **The options the audit listed (F5, AUD:327-331).**

> - **Options.**
>   - `compression.zstd` streaming, with a SHA-256 check against the desk record. It is stdlib in Python 3.14.6, present
>     on this Air, but python3.13, which the runbooks pin, lacks it (verified).
>   - `desk_compress.read_bytes`.
>   - An APFS in-place restore per unit (DESIGN §0 item 8). B6-AN-1 A7 exercised it on synthetic trees only.

---

## §17-R12. Fixtures before S-14 is cut

- **Label.** Entered after the Block 5 unseal (2026-11-08); text drafted pre-unseal on 2026-11-07.
- **Kind.** Tooling or coverage (RL-30, RL:883).
- **Status.** Default.
- **Source.** AUD:501 @ `07b9f704b`.

> | # | Amendment | From | Resolves |
> |---|---|---|---|
> | R12 | **Fixtures before S-14 is cut.** Production-shaped synthetic sessions generated by the real chain at `f31aca19f` (DESIGN §16). They must cover: waited runs with attempt-N telemetry; wait-cap and budget skips; `anchor_not_bounded` members; campaign logs that mix executed-member rows and the trailing whole-window evaluation row; compressed campaign logs and plists; and one cross-session GAMMA unit. | seat 1 A12; seat 2 C4 | F3, F11 |

---

## RL-25's dispositions of the drafter's flags

The first draft (`93c48941f`) raised four review points: R0's signer statement, R0's deadline, decision 3's second
half, and R1's `CANONICAL.md:48` correction. RL-25 disposes of the flags as follows (RL:699-719), verbatim. Flags 1, 2,
3, 5 and 6 are applied above (header, §17-R0, §17-R1); flag 4 is applied to DLE-10 in
`docs/analysis/b5/DEVIATION-LOG.md`.

> **The drafter's flags.**
>
> 1. *Signing statement.* Confirmed in substance, reworded for the entries: "Signed blind to Block 6: neither the
>    signer nor the drafter has seen a Block 6 energy, floor, ratio, contrast or outcome word. Not blind to
>    Block 5, whose released outcome words and numbers both have seen. Entry texts marked 'drafted pre-unseal'
>    are quoted from texts dated 2026-11-06 and 2026-11-07."
> 2. *R0's deadline.* Yes. R0's deadline clause reads: "The audit's deadline, before the Block 5 unseal, was not
>    met. These entries are made after it, under §12.4, which allows entries until the Block 6 release. Decided
>    after Block 5 outcomes were known."
> 3. *Later entries.* The second half of the audit's decision 3 governs from the day this set is entered: only
>    an entry that fixes a tooling defect and chooses no rule, labelled as such. Anything else needs a
>    research-lead ruling, carries "decided after Block 5 outcomes were known", and prints the alternative where
>    a number changes.
> 4. *The DLE-10 sentence.* "A replication of this experiment in nine further sessions on later days (Block 6)
>    was registered before any Block 5 number was seen and has been collected. Its results are sealed and are not
>    yet released." On a slide: "Replication collected (nine sessions, registered blind); not yet released."
> 5. *One deviation line for the late entries.* R0, with flag 2's clause, is that line. No separate entry. Paper
>    1's deviation list names it.
> 6. *R1's audit wording.* Under option (c) the L9 audit is optional. "The audit run" in RL-6 (b) means the
>    registered second side of option (c). Whether an L9 audit is run is decided and recorded before the blind
>    dry run; if one is started, the release holds until it finishes.

R1's `CANONICAL.md:48` correction stays with the seats that edit `CANONICAL.md`; this file does not draft it.

**RL-25 on this PR, for gate-ledger row 4 (RL:721-730), verbatim.**

> **PR #710, for gate-ledger row 4: ADMIT, with these edits.** Apply the rulings above to the §17 draft and
> update its status words. Replace DLE-10's "The required sentence" paragraph with flag 4's wording. Append to
> DLE-6 the scope lines of RL-27 (1) and (2). The quotations I checked against my own text are exact. The Sol
> refuter then checks the §17 draft as amended.
>
> **Reason.** These were the choices the pre-unseal audit left open, so no pre-unseal text can settle them. The
> principle keeps them from becoming a second analysis of Block 5.
>
> **Blind status.** Blind to Block 6: nothing of it has been read. Not blind to Block 5, including the two
> lines these decisions touch.

## RL-30: the refuter's five findings and 7b

The Sol executing refuter's report is `docs/run_reports/2026-11-10-b6-s17-refuter.md` (reviewed head `b3c048767`).
RL-30 accepts all five findings. Where each is applied:

| Finding | RL-30 | Applied in |
|---|---|---|
| S17-01 (authority) | RL:867-887 | §17-R0 deadline clause; a **Kind** line on every entry; the Kind list in the header |
| S17-02 (R8 digest and differences) | RL:861-865, RL:889-900 | §17-R8 |
| S17-03 (R3 against R8) | RL:902-904 | §17-R3, Exception |
| S17-04 (DLE-2 item 2) | RL:906-907 | §17-DLE2, Precedence |
| S17-05 (the reflowed quotation) | RL:909 | the header's source note and signing statement |
| 7b | RL:911-922 | §17-R8 |

**RL-30 on this PR, its reason and blind status (RL:924-930), verbatim.**

> **PR #710, gate-ledger rows 4 and 5: ADMIT** once the five dispositions and the 7b text are applied. It is a
> draft; nothing is entered in the registration by it. The later PR that enters the entries comes to me.
>
> **Reason.** The refuter is right on each point, and on the first it caught an overstatement of mine. An entry
> log that says which kind of thing each entry is can be checked; one that claims a blanket permission cannot.
>
> **Blind status.** Blind to Block 6. Not blind to Block 5.
