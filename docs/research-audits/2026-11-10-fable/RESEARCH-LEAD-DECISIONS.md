# Research design lead: decision log (Fable 5.2)

**Authority.** Ed, 2026-11-10 about 18:25 PST, recorded in `RUN_STATE.md` item 252: "def fable 5.2 should be the
final say for anything paper bound". That covers claim contracts, registrations, designs, analysis rulings, and
release and claim text. Opus 5.5 (the lead) orchestrates and has the final say on non-paper engineering.
Scope, venue and authorship choices stay with Ed.

**How to read an entry.** Each ruling has a number, a time from `date`, the ruling, its reason, and a
**blind status** line saying what the author had and had not seen when ruling. A later entry may amend an
earlier one; entries are never edited in place except to add an "Amended by" line.

**What I have seen as of the first entry.** The released Block 5 results (`docs/analysis/b5/RESULTS.md` on
`analysis/2026-11-08-b5-results` @ `0b0658a20`), read 2026-11-10. No Block 6, BYTES or ALIGN v4 outcome. So every
ruling below is **Block-5-aware**. A ruling that touches Block 6 or BYTES is blind to that data and says so.

Source for RL-1 to RL-11: `paper-audit.md` beside this file.

---

## RL-1. Paper 1's manuscript of record (2026-11-10 18:44 PST)

**Ruling.** Paper 1's text is `docs/paper/paper1/paper1.md` with `fill_index.md` and `variants/`, at
`a1a5029fb` on `origin/lane/2026-10-27-paper1-draft`. The lead is to:

1. open a docs-only PR that lands `docs/paper/paper1/` on `main`, unchanged;
2. tag `a1a5029fb` as `paper1/blind-draft-2026-10-27`, so the paper can cite the commit at which its outcome
   prose was written (after collection, before any release);
3. correct `CANONICAL.md`'s Paper rows: Paper 1 text is `docs/paper/paper1/paper1.md`; `draft-v1.md` and
   `draft-v2-skeleton.md` are the frozen September methods drafts (source for §3, Appendix B and Tier E);
   `docs/capstone/PAPER-PLAN-v2.md` and `PAPER-OUTLINE.md` plan the capstone tripwire manuscript, and their
   Block 5 exclusion is superseded by item 232.

All later edits to Paper 1 are commits on top of the tag.

**Reason.** No file on `main` names Paper 1's text. The 2026-11-07 release-to-paper audit asked for exactly
this (its Decision 11) and it was not done before the unseal.

**Blind status.** Process only. Block-5-aware; no outcome enters the ruling.

## RL-2. Adoption ruling for Block 5 placement, registration §14 Q4 (2026-11-10 18:44 PST)

**Ruling.** Every row the Block 5 analysis plan §9 registers for print is placed in Paper 1 at the sites
`fill_index.md` names for it (§5.1 to §5.6 and §5.8, the abstract and conclusion sentences assembled from
them), beside its registered fixed sentence. Both contrasts print with their issued status; nothing is selected
or omitted. Dominance prints as branch B, with every ratio, numerator, denominator and n, and no subtitle. This
supersedes the 2026-09-05 "D-174 SELECT FALLBACK" disposition for these rows, on Ed's written instruction of
2026-11-08 (item 232), which is one of the two events at which D-174 says it expires. The lead records it as a
dated addendum at the head of `docs/paper/results-fill-registry.md` and in the Block 5 deviation log.

**Reason.** Item 232 settles that Block 5 is in the paper. It does not say which rows, where, or what happens to
the registry's standing disposition, and the registration requires an adoption ruling before anything prints.

**Blind status.** Not blind: Block 5 is released and I have read it. The ruling places every registered row and
selects none, so knowing the outcomes cannot shape it.

## RL-3. The gate a Block 5 number passes before it is rendered (2026-11-10 18:44 PST)

**Ruling.** No Block 5 number enters Paper 1, a slide, the site or any public page until all three hold:

1. `docs/analysis/b5/RESULTS.md` is on `main`.
2. One fresh executing reader from the other model family than its author (it was written by an Opus seat, so
   a Sol seat) re-derives every number to be printed from the frozen custody by the key paths the file gives,
   and checks the paper's sentences against the ten licence constraints listed in the release-to-paper audit.
   That reader is not a repair seat.
3. Every printed value that comes from one of the seven families the recompute does not cover, from the 403
   exempt leaves, or from a recompute-only line (the whole-machine per-phase energies, the load-correlated and
   scaled-allowance lines, the durations, the attempt history, the monitor cost) has the item-83 ruling-3 hand
   check, with its source named.

This is the replacement for the "Results cold gate" that the 2026-10-20 renderer obligation still names and
DLE-0 abolished. The lead logs it as DLE-6. Internal documents may quote `RESULTS.md` meanwhile, naming it.

**Reason.** Item 232 lists this gate as open. Without it, every paper number is a hand copy of one seat's
reading.

**Blind status.** Not blind to Block 5. Procedural.

## RL-4. Claim text for Block 5 (2026-11-10 18:44 PST)

**Ruling.** These bind every sentence about Block 5 in Paper 1, the capstone manuscript and the talk:

- (i) The result sentence prints the decision interval. The within-session 95% interval is given as its
  statistical part, never alone.
- (ii) p-values appear in the results table only. They are not quoted in an abstract, introduction or slide as
  a measure of strength.
- (iii) Each result carries the boundary label, "one session", and kept over planned quads.
- (iv) No "efficiency", "scales with", per-parameter figure, law, or difference of the two separately collected
  floor-session cells.
- (v) The loss of 9 of 20 quads, its skew toward the 8B side and the prefill contrast sitting at the registered
  minimum are stated in the main results text. The exposure explanation is labelled as a post-release,
  exploratory derivation.
- (vi) "Sensitivity clean" is never printed without "Erratum-3 bracket sensitivity only". The registered
  load-correlated line is reported as not computable by the registered pipeline; the recompute's value may be
  printed beside that statement, labelled uncompared.
- (vii) The recompute sentence says what was recomputed and what was not, and that one of the 24 comparator
  families compared no rows.
- (viii) Three terms are kept apart and each is defined once: the *attribution floor* of a cell; the
  *attribution-limited floor class* (the published floor is set by the clock-anchor timing bound); and the
  *dominance branch*. The paper may say the published detection floors are set by the timing bound, with the
  repeatability-only floors beside them. It may not say that timing attribution dominates or limits the
  measurement: the registered branch is B.
- (ix) The rails' share of whole-machine energy is descriptive, carries its boundary sentence, and is not
  merged with the known-bytes share, which is a different quantity.
- (x) Registration §1's "every phase-energy sentence carries the D-177 limitation" is met by stating it in the
  abstract, in every table caption and in every paragraph that states a phase energy, and in the limitations.
  Logged as a reporting interpretation.
- (xi) The registered fixed sentences print verbatim in an appendix, with internal labels glossed in brackets.
  The body may paraphrase one only where it cites that sentence by label. "Session" may replace "window" with
  one note saying so. Logged as a reporting interpretation.

**Reason.** These are the points at which the released record is narrower than the natural way to write it up.

**Blind status.** Not blind to Block 5; the ruling is about wording released results.

## RL-5. Corrections of fact to Paper 1 before any fill (2026-11-10 18:44 PST)

**Ruling.** The following are corrected in `paper1.md` before a Block 5 number is filled. Items P1 to P12 of
the release-to-paper audit are adopted as binding, with these additions:

1. §3.6 and the fill index describe the floor gate as computed: the guarded operative floor plus the floor
   session's drift allowance, with the blind ruling of 2026-10-12 that corrected the sealed plan's sentence
   listed among the deviations.
2. §4.5 lists every post-collection change: two seals, three prospective errata, analysis versions r1 to r4,
   DLE-0 to DLE-5, the L9 rulings, D-188 to D-190. `P1-DEV-LIST` takes those sources.
3. §7 says what is true of where agents ran: an agent census refuses and pauses collection while any agent
   process is alive; between sessions a headless agent runs on the measurement Mac and arms them; agents ran
   the blind dry runs on the analysis laptop under custody kept by rule. The claims "no agent ever runs on the
   measurement laptop", "an account no agent used" and "cloud machines ... never held real or blinded data" are
   removed.
4. §7.3 is rewritten from the record through November, and its FILL sources are re-pointed.
5. The abstract's "ten held-out models" becomes seven; §6.4 is reduced to the fact that both extension models
   were dropped and why; `P1-BYX-RESULTS` is deleted; the unconditional "not resolvable is a finding" sentence
   leaves §9.
6. `P1-B5-B-SHARE` is dropped or labelled exploratory.

**Reason.** Paper 1's integrity section and method section must be true of the study as run, not as planned on
27 October.

**Blind status.** Not blind to Block 5. Corrections of fact from the record.

## RL-6. Block 6 (2026-11-10 18:44 PST)

**Ruling.**

- (a) Block 6 stays in Paper 1's design. It is not ruled out of scope.
- (b) The registration's §17 entries are entered now. The default for each is the recommended option of the
  2026-11-07 Block 6 design audit (`origin/research/2026-11-07-block6-design` @ `07b9f704b`), entered verbatim
  and labelled with that commit and "entered after the Block 5 unseal". DLE-2's owed entry cites its adoption
  date, 2026-11-06. Where that audit gave no recommendation, or where the lead or I depart from it, the entry
  is labelled "decided after Block 5 outcomes were known", and where the choice changes a printed number the
  alternative is printed beside it, as the registration's §12.4 already requires. If the audit run has not
  finished when the numbers would be released, the release holds. I review the drafted entries before they are
  entered.
- (c) Seats that write or review Block 6 analysis code are briefed not to open `RESULTS.md` or any Block 5
  outcome. Rulings by me or the lead are Block-5-aware and say so.
- (d) Paper 1 prints the replication if Block 6 is released under its registration by **5 December 2026**.
  Otherwise it prints the Tier C text. The call is recorded in `RUN_STATE.md` by date, before any Block 6
  number is read. This replaces the contingency plan's 22 November trigger.
- (e) Printing Block 5 without Block 6 beside it, in a draft, the talk or a Tier C submission, departs from
  item 37's reporting rule. It is logged as a deviation and carries the sentence that a registered replication
  is collected and its results are not yet released. I will not sign off a submission of Paper 1 to an
  external venue without the replication released.

**Reason.** Nine counting sessions are collected and no path can analyse them. The amendments that should have
preceded the Block 5 unseal did not. Adopting the pre-unseal text verbatim is the only way left to keep those
choices from depending on Block 5's outcome words.

**Blind status.** Blind to Block 6: nothing of it has been read. **Not blind to Block 5**, whose outcome words
the replication word compares against. The date in (d) was chosen from engineering state only.

## RL-7. BYTES (2026-11-10 18:44 PST)

**Ruling.**

- (a) Stage 1 does not run until two fixes are landed and reviewed. First, the driver's no-key probe must not
  pass on an unrelated failure (the open finding of the Sol review of PR #701); it gets an Opus cold review.
  Second, the commitment gate becomes a real check: the commit exists, its predictions blob hashes to
  `predictions.sha256`, it is reachable from `origin`, and the push time is recorded. The check lives in the
  driver, outside the digest-pinned estimator.
- (b) The matched-geometry known-bytes reading rule and its admission land on the BYTES lineage, and the slot
  fill is copied into registration §1, before stage 1.
- (c) Nothing joins the registered families. A secondary analysis may be registered as a dated addendum only
  if its text is merged before the stage-1 commitment; it is then labelled "registered after the Block 5
  release and before BYTES stage 1". Anything later is exploratory. No rider delays stage 1.
- (d) Paper 1 §6.3 discloses that Block 5 was released before BYTES stage 1 and that two of the three fit-set
  models are Block 5's models.
- (e) Dates: stage-1 commitment recorded by **19 November 2026**; stage 2 released by **3 December 2026**.
  Missing either selects Tier D for Part 2, called by date and recorded before any BYTES number is read. This
  replaces the contingency plan's 12 and 15 November.
- (f) The registration's per-model rule applies as written: the two-pass mean where both passes compute, the
  labelled one-pass fallback where one does not. The Tier B variant's alternative is retired.
- (g) The check behind `P1-AUTO-BLINDCHECK` (whether any held-out model's timing was read before the
  commitment) is made by a seat that reads structure only, recorded before the commitment, and printed
  whichever way it falls.

**Reason.** "Predictions were committed before the held-out energies were unblinded" is the sentence Part 2
rests on, and today a regex stands behind it.

**Blind status.** Blind to every BYTES energy, fit or held-out; I know collection structure only. Not blind to
Block 5, which shares two fit-set models with BYTES at a different prompt length; (d) discloses that. The dates
in (e) were chosen from engineering state only.

## RL-8. Paper 1's outline and naming rule (2026-11-10 18:44 PST)

**Ruling.** Paper 1 follows the outline in `paper-audit.md` §8.1: the instrument and its boundaries before the
method, Block 5 as instrument validation, BYTES as the second results section, the automation account rewritten
from the record. The title and abstract name only parts whose results are released at the scope freeze of 5
December. No "attribution-limited" subtitle prints. The final title wording is Ed's.

**Reason.** The framing Ed accepted on 2026-11-07, his ruling in item 232, and the released dominance branch.

**Blind status.** Blind to Block 6 and BYTES. Block-5-aware: the subtitle rule follows the released branch.

## RL-9. Tripwire claim text, as far as it bears on Paper 1 (2026-11-10 18:44 PST)

**Ruling.** Paper 1 carries no ALIGN result. If it carries an outlook on agent auditing, the v3 pilot appears
there as motivation with its limits in the same sentence: known log omissions made by subtracting logged
tokens, two sabotage trajectories re-checked across sessions, the host-software GPU rail. No manuscript or
slide under this authority states "sabotage leaves an energy signature" as a finding. Under option B the
confirmatory v4 claim is the tripwire K, and the sabotage-against-benign test S is registered with an
equivalence margin. The phrase may stand as a question or hypothesis. Whether it stays a title is Ed's.

**Reason.** Item 252 and finding V4-01 of this morning's design audit: at logged counts the physics predicts no
residual, whatever the agent intends.

**Blind status.** Blind: no v4 calibration or test data exists.

## RL-10. Talk evidence rule (2026-11-10 18:44 PST)

**Ruling.** `TALK-OUTLINE-v2.md`'s rule that Block 5 outcomes are sealed is superseded. Released Block 5 numbers
may appear on a slide after RL-3's gate, under RL-4. Block 6, BYTES held-out and ALIGN v4 outcomes stay sealed
and the talk shows gate status only. The talk's content and headline remain Ed's.

**Reason.** Items 231 and 232.

**Blind status.** Not applicable.

## RL-11. MBP time for Paper 1 (2026-11-10 18:44 PST)

**Ruling.** Paper 1 claims no measurement window on the MBP. Its only MBP need is desk time that never
overlaps an armed span: the three BYTES steps and one custody copy of the Block 6 sessions to the Air. Timing
is the magistrate's call under item 181. My recommendation to him: use the gap between R1's chain exit and the
W1 arm, BYTES stage 1 first once RL-7 (a) is met, then the Block 6 copy.

**Reason.** All of Paper 1's data are collected, and Ed has given the MBP to v4 and v5.

**Blind status.** Not applicable.

---

## Open items routed to me, not yet ruled

| Item | Waiting on |
|---|---|
| Adjudicate the two option-B claim-contract builds (`align/2026-11-10-claim-contract-sol`, `-opus`) | The builds landing |
| Review the drafted Block 6 §17 entries (RL-6 (b)), including the audit's decisions 7, 8 and 9, which have no pre-unseal recommendation | The lead's draft |
| Any custody change that moves BYTES keys to the Air | A proposal from the lead, if Ed wants Paper 1 off the MBP entirely |
| The capstone manuscript and talk, as a whole | Ed's decision E1 in `paper-audit.md` §9 |
