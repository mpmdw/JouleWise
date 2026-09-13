# Cold-gate packet 23 — Opus CONTRACT-LENS refuter (paired with the cold Fable judge)

Role: contract lens. Read-only. Source of truth for every claim below:
`/Users/edr/code/JouleWise-wt-paper-n-ref` at `e3285e67d6b616b020b95eaf1caf2e8089f240ff`
(confirmed with `git log --oneline -3` before any file was opened: HEAD = e3285e67 "Paper-N fix
round 2: cure the term-before-definition residue…", parent 73f7ac9f).

## 0. Contamination disclosure

Files opened in this session, all read-only, nothing modified in the reference checkout:

- `docs/process_traces/2026-09-12-paper-n/23-coldgate-packet/00-PACKET.md`
- `docs/process_traces/2026-09-12-paper-n/23-coldgate-packet/21-delta2-pedagogy-opus.md`
- `docs/process_traces/2026-09-12-paper-n/23-coldgate-packet/12-brief-fix-round-1.md`
- `docs/paper/draft-v2-skeleton.md` at `e3285e67` (selected line ranges and whole-file greps)
- `docs/paper/draft-v2-skeleton.md` at `482a0cc4` and at `dbe6c675` (via `git show`, greps only —
  the two other commits the packet names)
- `docs/paper/protocol/first-use-audit-ledger.md`
- `docs/paper/round7/built-terms-lexicon.md`
- `docs/paper/figures/figA4_shared_signs.svg`, `docs/paper/figures/README.md` (text greps)

Not opened, by the packet's constraints: packet files 04, 06, 13, 16, 17, 18, 19,
`lead-bench-notes-round1.md`; record 11 (the pin census — **not in the packet directory**, see the
limitation below); any process doc, decision log, RUN_STATE, TASK_QUEUE, memory; any git history
beyond the three named commits.

**Limitation that bounds every pin verdict below.** The pin census (record 11) is not in the packet,
and `tests/test_paper_terms_lint.py`, `tests/test_paper_first_use_ledger.py`,
`tests/fixtures/d165_rationale_allowlist.json` and
`docs/paper/fill-rehearsal/select_outcome_branches.py` are outside the constraint list, so I did
not read them. My pin verdicts therefore rest on (a) record 12's "Hard rules" restatement, (b) the
draft's own HTML comments and replay-fence notes, (c) the ledger's and lexicon's own stated
semantics, and (d) whole-file greps. Where a verdict depends on a file I could not read I say so
and name the acceptance command that closes it. Two commands from record 12 §Acceptance are the
mechanical closure for every NAMED risk below and must be re-run at the bench after the edits:
the unittest list in item 2, and `scripts/check_paper_replay_fence.py` in item 3.

Nothing was run against the draft except `python3 -B` one-liners over text I had already read.

---

## Correction to the question as posed

The packet asks for "the eleven open cures in record 21 §4". Record 21 §4 lists **1 blocker + 5
should-fix + 6 nits = twelve** items. Record 21's own recommendation covers only six of them
("apply NB2-1 plus should-fix 1–5, re-read only the eight edited sentences plus ledger row 95, and
land"), leaving the six nits undisposed. The table below rules on all twelve and marks which are
in the land-now set. A disposition that says "eleven" will leave one item unadjudicated whichever
way it is read; that is itself the contract defect the cold gate should close.

---

## Q1. The twelve cures — verified against the draft at e3285e67

Legend: **pin risk NONE** = I verified by grep/read that the prescribed edit cannot disturb any pin
I can see from the constraint list. **NAMED** = a specific pin is in reach; the risk and its closing
command are named. All twelve edits are inside existing wrapped source lines and add or remove no
line, no numeral, no HTML comment, no bold term and no table row; none is inside the abstract
(lines 9–32) or §8 (900–921), so the `ABSTRACT_HEADLINE` / `CONCLUSION_HEADLINE` verbatim strings
and the three count phrases are untouched by the whole set.

| # | Cure id | Pin risk | Verdict and corrected text |
|---|---|---|---|
| 1 | **NB2-1(a)** — build "false difference" at its first use, draft 197 | **NONE** for the pin; **CORRECTED** for the text | Real (Q2). Record 21's text — "…— the apparent energy difference produced by runs that differ in no condition" — **reproduces the defect record 21 files as its own should-fix 4**: the host sentence at 195–197 already carries an em-dash pair ("—every lower-or-upper edge position allowed by that calibration and mapping—"), so the prescribed appositive makes four dashes in one sentence. Use parentheses, and add **no bold** (a new bold term would enter record 21's own Pass A inventory with no ledger row). **Corrected text**, replacing `component's source of false difference.` at 197: `component's source of false difference (the apparent energy difference between runs that differ in no experimental condition).` |
| 2 | **NB2-1(b)** — restore the floor's purpose at draft 218–219 | **NONE** | Real (Q2). Record 21's text — "A cell has two false-difference components, and their spread is enlarged into a threshold a model comparison must exceed" — leaves *whose* spread ambiguous: 219–220 immediately uses "spread" for the absolute component alone ("measures spread among repeated runs of one model"), so "their spread" reads as the components' spread rather than the false differences'. It also drops the component→floor link that 108 and 110 have just built. **Corrected text**, replacing `A cell has two false-difference\ncomponents.`: `A cell has two false-difference components; the spread of each is enlarged into the floor a model comparison must exceed.` ("floor" is built at 108 and used at 110, both before 218.) |
| 3 | **SF-1** — Figure A4 caption vs the pinned SVG's "Table 4", draft 514 | **NAMED** (terms lint) | Real and verified at the primary artifact: `figures/figA4_shared_signs.svg` line 15 text node reads `…→ eight rows in Table 4.`, while 514 reads `the cases in Table A4 (Appendix A.3.10)`. The cure re-introduces the literal string `Table 4` into the draft, which record 21 itself observed had been driven to zero occurrences; if round 2 pinned that absence in the terms lint, this trips it. The shape is precedented in the same draft at 164 — `the **entry check** (labelled the admission gate in Figure A2)` — so quoting the figure's own label is the house style, not an invention. **Text as record 21 gives it**, at 514: `the cases in Table A4 (Appendix A.3.10; the figure's note calls it Table 4)`. **Closing command:** `tests.test_paper_terms_lint` in acceptance item 2. `docs/paper/figures/README.md` line 16 also still says "Table 4"; it was not in round 1's WRITE_SCOPE and stays a sweep item, not a bench edit. |
| 4 | **SF-2** — the F7 sentence's misdirection, draft 550 | **NAMED** (replay fence) **and CORRECTED** | The defect is real. But record 21's text — "the separately retained largest pulse residual **is a different quantity**, computed and stored separately" — **contradicts the appendix it cites**. A.3.6 (1225) says: "That difference is what the two published numbers give when subtracted; it is **not itself the value the code retains** for the worst edge excursion, which is computed and stored separately." That is the same physical quantity obtained two ways (…47592 by subtraction, …476 retained), not a different quantity. Publishing "a different quantity" in §4 would create a fresh text/appendix conflict of exactly the class this round is curing. **Corrected text**, replacing `the separately retained largest pulse residual is recorded in the source artifact (Appendix A.3.6).`: `the value the code retains for the worst edge excursion is computed and stored separately (Appendix A.3.6) and is given below.` **Pin:** line 550 sits under the replay-fence comment at 553 ("requires every literal above to be the same double it re-derives") and record 12's hard rule "the §4 worked-arithmetic line 588 and its stamp spans are untouchable", which record 12 §E3 licensed for text-side change of this sentence only. The corrected text alters no literal and no stamp row. **Closing command:** acceptance item 3, `scripts/check_paper_replay_fence.py --corpus-root …`, same COMPARED / MISMATCHES 0 census. |
| 5 | **SF-3** — "centered" unbuilt at 108 and 335 | **NONE** | Verified: `grep -n "center\|centre"` over the main text returns 108, 332, 335 only, and none defines it; 332/335 use "centering" as a property of the formula, not a definition. "mean" is already in use at 108 ("mean B energy minus mean A energy") and at 146 as the gloss of median, so the cure introduces no further unbuilt word. **Text as record 21 gives it**, at 108: `The absolute floor is built from repeat energies after each is expressed as its difference from their mean, the comparative floor from…`. |
| 6 | **SF-4** — four dashes around the Huber gloss, draft 150 | **NONE** | Verified verbatim at 150. The sentence carries the B-3 acceptance criterion, so the ambiguity is load-bearing. Ledger row 255 homes "Huber loss" in A.3, and the cure changes no term, only punctuation. **Text as record 21 gives it:** `sums Huber scores (squared for small differences, proportional for large ones) of the differences…`. |
| 7 | **SF-5** — the ledger/lexicon certify a deleted gloss | **NAMED**, and **HALF THE CURE MUST BE REFUSED** | The ledger half is right and necessary: row 95 status is `glossed-at-first-use`, which the ledger's own header defines as "the first named use supplies a plain-word definition or an equivalent calculation in the same sentence or paragraph" — falsified at first use (197). Cure row 95's Definition column to a **paraphrase**, in the style of every neighbouring row, not a draft quote: `The first use glosses it as the apparent energy difference between runs that differ in no experimental condition; the same-model null A/B/B/A block produces this diagnostic, distinct from the two-model science contrast.` Row count and the footer "Terms inventoried: 262" are unchanged. **The lexicon half is a misdiagnosis and must not be done.** `built-terms-lexicon.md` rows 65 and 130 sit under the heading `## Draft-v1 generated base`, whose columns are `term / first line / how detected / line (first 80 chars)`; the file header states "The base table was generated mechanically from `docs/paper/draft-v1.md` by `scripts/paper_terms_lint.py`", and the ledger header states "The frozen round-7 lexicon remains historical context; this ledger owns the current single-draft reading order." Those rows are a frozen 80-character excerpt of **draft-v1 line 117** — they were never a claim about draft-v2 and are not stale. "Refreshing the two lexicon build quotations to the draft's wording" would overwrite generated provenance with hand text and desynchronise the base table from its generator, and the same header says the test binds "this hand-maintained **successor** table", not the base. **Refuse; record the refusal.** |
| 8 | **N-1** — tautological parenthesis at 658 | **NONE** | Verified verbatim. **Text as given:** `as in the Section 2 example (a worked example, not a measured window bound)`. |
| 9 | **N-2** — duplicated median gloss at 572 | **NONE** | Verified. Ledger row 278 homes "medians" in "Bracketed pulse-train algorithm" (140–207); the surviving gloss at 146 is inside that home, so deleting the §4 duplicate is ledger-consistent, and the +13.0 / −5.5 literals stay. **Text as given:** `Their medians are +13.0 ms and −5.5 ms`. Note for the bench: row 278's Definition column still describes the §4 site ("for the 59-value series each is its 30th sorted lag"); it is a disposition note, not a quote, so it may stand. |
| 10 | **N-3** — the sampler sentence verbatim at 12 and 41 | **NONE**, but **DROP** | Record 21 marks it optional. Its prescribed replacement is also under-specified and, applied literally, self-duplicating: 41–42 currently read "macOS `powermetrics` is the power sampler used here. A sampling record reports average power between recorded start and end times.", and the cure text "That sampler emits one record reporting average power between recorded start and end times." restates the *second* sentence while deleting the first. It also leaves "That sampler" pointing 29 lines back into the abstract. Abstract-to-intro repetition is conventional. **Recommend: do not apply.** If the lead insists, the only safe form keeps the name: `The \`powermetrics\` sampler emits one sampling record per interval, reporting average power between recorded start and end times.` replacing **both** sentences at 41–42. |
| 11 | **N-4** — self-referential pointer at 241 | **NONE** | Verified: 241 is inside §3 (175–522) and the link is at 519, the last citation of the section. **Text as given:** `linked at the end of this section`. |
| 12 | **N-5** — "these floors" folds in the science contrast, 110 | **NONE** | Verified: 108 names two floors *and* a science contrast; 110 then says "each of these floors". **Text as given:** `JouleWise bounds each floor separately`. |
| — | **N-6** — "the allowance" bare at 589–590 | **NONE**, but **PRESCRIBED TEXT IS UNGRAMMATICAL — DROP or use the minimal form** | The draft reads: "The accepted region defined in Section 2 is distinct from the allowance: the largest endpoint displacement in an accepted region, 28.93293456111476 ms on that onset, equals the retained worst edge excursion." The colon already supplies the definition in the same sentence, so the ledger's `glossed-at-first-use` standard is met and the defect is stylistic. Record 21's cure replaces the colon with an em dash — "distinct from the edge allowance — the largest endpoint displacement in an accepted region, …" — which strands the finite verb "equals" with no subject. It also coins "edge allowance", which collides with "a per-edge allowance" at 657 and "energy allowance" at 380/391/429/512/515: a new synonym pair, which is record 21's own SF-1 defect class. **Recommend: do not apply.** If the lead wants the antecedent named, the one-word minimal form keeps the colon and coins nothing: `is distinct from the allowance it yields: the largest endpoint displacement…`. |

**Land-now set — rows 1, 2, 3, 4, 5, 6, 7 (ledger half only), 8, 9, 11, 12:** eleven edits, being
ten draft edits at nine sites (NB2-1 takes two, at 197 and 218–219) plus one ledger row.
**Refused:** the lexicon half of SF-5. **Dropped as net-negative:** N-3 and N-6.

**Answer to Q1: (a), the lead applies them at the bench — with the four corrections above.**
Why: every surviving item is one clause inside a line that is already open, changes no numeral
(verified: the whole round 2 added **zero** new numeral tokens, see Q4), moves no paragraph, adds
no line, and edits no SVG. Each is smaller than the contract needed to delegate it, which is the
bench-vs-session threshold on its face. (b) is refused because the escalation trigger is met and a
third delegated round is precisely the spend the trigger forbids; (c) is refused because the
structural change Q3 asks for is a clause, not a topology change, and it can be ratified in the
same turn as the bench edit rather than blocking it. The one condition on (a): **record 21's
prescribed text is not safe to copy verbatim** — four of its twelve prescriptions are wrong
(1, 2, 4, and the lexicon half of 7) and two are net-negative (N-3, N-6). That is the same failure
mode record 21 itself diagnoses in should-fix 3, one record later, and it is the reason a bench
edit must be a *read*, not a paste.

---

## Q2. Is "false difference" genuinely unbuilt?

**Yes. Not an over-reading — it fails the ledger's own written standard, and I verified both limbs
mechanically.**

*The term.* Over the whole draft at e3285e67, `grep -n "false difference\|false-difference\|false
differences"` returns exactly two lines:

> 195–197: "The registered sensitivity question is whether permitted edge movement—every lower-or-upper edge position allowed by that calibration and mapping—at least doubles each **component's source of false difference**."

> 218–219: "A cell has two **false-difference** components."

Neither says what makes a difference false. At the base `dbe6c675` the same grep returned four
lines, two of which built it — line 113 ("Repeat the same model to measure false differences;
enlarge their spread into a threshold a model comparison must exceed.") and line 126 ("block
produces a false-difference diagnostic"). At `482a0cc4` the build still stood at line 209. Round 2
deleted it with the duplicate §3 block. The replacement at 108 carries the three floor
*constructions* and not the build.

The decisive contract fact is the ledger's own definition, not a reviewer's taste.
`first-use-audit-ledger.md` line 3 defines the status that row 95 asserts:

> "`glossed-at-first-use` means the first named use supplies a plain-word definition or an equivalent calculation **in the same sentence or paragraph**."

Row 95 asserts that status for "false-difference components / false-difference". The first named use
is 197; 197's sentence and paragraph supply no definition and no equivalent calculation. The row is
false against the instrument's own criterion. The ledger further states "Any uncured first use is a
failure" and prints "FAILS: 0" — so the draft currently ships a certificate it does not satisfy.
That is worse than a prose defect: it is the acceptance instrument certifying its own blind spot.

*The why.* Record 21's second limb also holds. I ran `exceed|threshold` over lines 9–921: the hits
are 148/149 (the quiet-record plateau check), 157 (the pre/post calibration threshold), 211 (the
forcing problem for the **doubling test**, not the floors), 368 (the R = 2 threshold), and 869/871
(related work). Nothing in the main text says a floor is a threshold a model comparison must clear.
The one partial rescue record 21 does not mention is line 517 — "The **cell floor** is the final
gate value for assigned-energy differences in a cell" — which supplies a purpose, but for a
different object (the cell floor, after the protocol's publication safeguards), 309 lines after the
first use at 208 and in a passage the reader reaches only after the whole apparatus. It does not
rescue 197–221, and I do not count it against the finding.

**Verdict: NB2-1 is a real replication-bar failure on both limbs, and it is a REGRESSION — the text
existed at 482a0cc4 and the round deleted it.**

---

## Q3. The proposed process clause — AMEND

Proposed: *"Every delete, move or rename item in a prose fix contract must name and quote every site
that USES the deleted build or the renamed object — in the draft, in pinned figure text, and in the
ledger/lexicon gloss columns — and the seat's report must show each site defined at or before use
after the edit."*

**Refutation, on three counts.**

1. **"Name every site that USES the deleted build" is not mechanically enforceable as written.**
   Knowing which uses depend on a deleted *build* requires knowing what the deleted text built —
   a semantic judgement. The lead cannot enumerate it when authoring the contract any more reliably
   than the seat can when executing it, and round 2 is the proof: the lead's contract 18 already
   carried a structural rule about use sites, and the blocker went through anyway. A clause that
   asks an agent to be careful is the mechanism that already failed twice.
2. **The "move" arm is redundant.** Round 2's whole-text mechanical first-use pass drove LATE to 0
   for the first time in the series, independently reproduced by record 21's Pass A and Pass B.
   Moves are covered. Spending contract length on them buys no new catch and dilutes the arm that
   does.
3. **It misses one of the three defects of the round it is written to prevent.** SF-3 ("centered",
   unbuilt at 108) entered through an **addition** — record 16's own prescribed cure text, copied
   verbatim into contract 18. No delete/move/rename rule catches it. The clause as proposed would
   have caught NB2-1 and SF-1 and missed SF-3 — two of three.

**What would actually have caught each defect** (I checked each against the draft):

| Round-2 defect | Caught by the proposed clause? | Caught by the amended clause below? |
|---|---|---|
| NB2-1 (deleted build, "false differences") | Yes, if the seat exercised judgement | **Yes, mechanically** — "false differences" occurs in removed line 209 and still occurs at 197 and 218 after the edit; a set intersection, no judgement |
| SF-1 ("Table 4" rename not propagated to the pinned SVG and figures README) | Yes, if "pinned figure text" was read as the whole paper tree | **Yes** — one `grep -rn 'Table 4' docs/paper/` returns the SVG line 15 and README line 16 |
| SF-3 ("centered" introduced by the reviewer's own prescribed text) | **No** | **Yes** — the prescribed-text arm |
| Round-1 NB-1 / NB-2 / "resolution bound" / "the 5% constants" (uses left behind by a move) | Yes | Already closed by the existing whole-text first-use pass; not re-legislated |

**Amended clause (ratify this text instead):**

> **Delete/rename sweep (mechanical; a prose fix contract that deletes or renames text must require
> it, and the seat's report must paste both outputs).**
> (a) *Deleted builds.* From `git diff <base>..HEAD -- <draft>`, take every bolded term, every
> ledger term and every hyphenated term of art that occurs in a **removed** line. `grep -n` each
> over the post-edit draft. Any term that still occurs is a defect unless the report quotes its
> surviving build and the ledger row that certifies it.
> (b) *Renames.* For every renamed object, `grep -rn '<old string>' docs/paper/` over the whole
> paper tree — draft, figure SVG text, figure READMEs, the first-use ledger, the built-terms
> lexicon, and the protocol. Every hit is either updated, or — where the hit is a pinned generator
> output that must not be edited — cured text-side in the draft and quoted in the report.
>
> **Prescribed-text rule (authoring, binds the lead not the seat).** Verbatim replacement text that
> a review record prescribes carries no first-use exemption: before it enters a contract, the lead
> runs it through the same first-use test as the draft. A reviewer's cure is draft text the moment
> it is commissioned.

Both arms are greps with pasteable output; neither asks anyone to be careful.

**Where it should live.** Not the `codex-delegation` skill: that skill is the general delegation
contract and this rule is prose-specific, so it would be dead weight in every non-paper seat and
would be skimmed past in the ones that need it. Not *only* the ledger doc either, because the
prescribed-text rule binds the lead's authoring step, which the ledger does not govern. **Split it:**
arm (a) and arm (b) belong in `docs/paper/protocol/first-use-audit-ledger.md` as named acceptance
checks beside the existing status definitions — that is where the mechanical gate already lives,
where its vocabulary (`glossed-at-first-use`, "Any uncured first use is a failure") is defined, and
where the next round will look. The prescribed-text rule belongs wherever prose fix contracts are
authored; I could not read the process docs, so I defer the exact file to the magistrate and rule
only on the shape. Putting all of it in the ledger would be acceptable and is better than putting
any of it in `codex-delegation`.

---

## Q4. Anything to REVERT rather than patch?

**None.** Named, with the checks I ran:

- **The A1 deletion (old 209–211).** Do *not* revert. The deletion of the duplicate §3 block was
  correct and closed NB-1; only two clauses inside it were load-bearing, and cures 1 and 2 restore
  both at the sites of use. A revert would reinstate the duplicate the round was commissioned to
  remove.
- **No-new-numeral rule (D-174), the hard rule most likely to have been broken silently.** I
  checked it mechanically rather than trusting either report: over the full files, the set of
  numeral tokens in the draft at `e3285e67` minus the set at `482a0cc4` is **empty**; the only
  token removed is `4,` (from "Table 4, " → "Table A4"). Round 2 introduced **zero** new numerals.
  Nothing to revert on that rule, and the twelve cures above add none either.
- **The replay-fenced spans.** Line 550's literals and the five stamp rows at 540–546 are
  byte-identical to `482a0cc4`; the round's F7 change was wording only, inside the one sentence
  record 12 §E3 licensed.
- **Headline strings and the three count phrases.** No cure in the land-now set touches lines 9–32
  or 900–921, so the pin is out of reach of this bench edit. I could not read
  `select_outcome_branches.py` (outside the constraint list); record 12's acceptance item 2
  (`tests.test_select_outcome_branches`) is the closure.
- **The one thing that would otherwise have been reverted by mistake:** the two `built-terms-lexicon.md`
  base rows (65, 130). Record 21's should-fix 5 asks for them to be rewritten. That would not be a
  patch but a silent destruction of generated draft-v1 provenance — see Q1 row 7. **Refuse it.**
  This is the item the packet's Q4 was worth asking for.

---

## Recommendation

**Land after bench edit** — apply the ten items above with the four corrections (cures 1, 2, 4 and
the ledger-only half of 7), drop N-3 and N-6, refuse the lexicon half of SF-5 and record the
refusal, ratify the amended Q3 clause into the first-use ledger doc in the same commit, then
re-run record 12's acceptance items 2 and 3 before pushing. No third delegated round; no consult
beyond this one.
