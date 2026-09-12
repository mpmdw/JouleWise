# Cold-gate ruling — packet 23 (Paper-N, after two fix rounds)

Judge: cold Fable 5.1, single non-interactive session, doctrine-free checkout
`/Users/edr/code/JouleWise-wt-paper-n-cold` at `e3285e67d6b616b020b95eaf1caf2e8089f240ff`
(confirmed with `git rev-parse HEAD` before any file was opened). Packet digest read from
`PACKET.sha`: `a868269a0b008269`. No background task, watcher, or subagent was started; every
probe ran in the foreground. No file in the checkout was modified. Wall time ≈ 5 minutes
(14:20–14:25 PDT).

## Contamination disclosure

Files opened, in order:

1. `23-coldgate-packet/00-PACKET.md` (whole).
2. `23-coldgate-packet/PACKET.sha` (whole).
3. `23-coldgate-packet/21-delta2-pedagogy-opus.md` (whole).
4. `docs/paper/draft-v2-skeleton.md` at `e3285e67`, by `sed -n` / `grep -n` only, lines 12, 41,
   40–43, 103–110, 144–152, 195–232, 233–262, 241, 330–336, 512–522, 550, 572, 576–592, 656–660,
   1223–1227; section-header list; greps for `false difference`, `center`, `exceed|threshold`
   (lines 9–921), `Table A4`, `edge allowance`, `frozen`, `custody`.
5. `docs/paper/draft-v2-skeleton.md` at `482a0cc4` via `git show`, lines 100–112 and 205–215.
6. `docs/paper/figures/figA4_shared_signs.svg`, line 15 and a grep for `Table 4`.
7. `docs/paper/protocol/first-use-audit-ledger.md`: header lines 1–30, rows 93–97, last 5 lines,
   grep for `false-difference` and `center`.
8. `docs/paper/round7/built-terms-lexicon.md`: header lines 1–25, rows 63–66 and 128–131, greps
   for `false difference` and `center`.
9. `git diff 482a0cc4..e3285e67 -- docs/paper/draft-v2-skeleton.md`, deleted lines only, and
   `git diff --stat` over `docs/paper/`.

Not opened: packet records 04, 06, 12, 13, 16, 17, 18, 19, `lead-bench-notes-round1.md`; any
process doc, decision log, RUN_STATE, TASK_QUEUE, memory file, test file, or figures README; no
git history beyond the three named commits.

Harness-injected context I did not request: the session system prompt carried the user's global
`~/.claude/CLAUDE.md` (including a "Writing standard" section that states a first-use test) and
the auto-memory index `MEMORY.md` (one-line pointers only; no memory file was opened). I note that
the injected first-use test coincides with the packet's own replication bar, so it did not move
any ruling below, but a reader should know it was in context.

## Q1 ruling — disposition (a): lead bench edit, then land

**Choice: (a).** Reasons:

- Every item in record 21 §4 is one clause or one sentence at a site already open. I checked each
  against the draft at `e3285e67` (table below): the sites are where the record says, and no cure
  adds a numeral, moves text, or touches an SVG.
- The escalation rule says the next spend after two same-signature rounds is a consult, not round
  three. This gate is that consult. A third delegated round (b) would re-run the exact mechanism
  that failed twice, because the fixer's blind spot is uses outside the draft file and declarations
  left behind by deletions, and the rule that closes it (Q3) is not yet installed.
- (c) is wrong in order, not in substance: the structural change (Q3) governs future *delegated*
  contracts. It does not need to precede a bench edit whose every site this ruling has already
  read after-the-fact. Install Q3 before the next delegated prose round, not before this landing.

**Count.** Record 21 §4 lists 1 + 5 + 6 = 12 items as written, not eleven. I reject nit 3 (the
record itself marks it optional), which leaves eleven applied edits. Ten are in the draft; one is
ledger row 95. Nothing in the lexicon changes (see SF-5).

**Conditions on the bench edit.** One commit; then re-run the paper checks (abstract word count,
literal byte-identity, the first-use ledger test) — I did not run them (NOT EXECUTED, by the
constraints). The ledger footer stays at 262 because row 95 is rewritten, not added. The landing
record must quote the after-edit text of lines 108, 110, 150, 197, 218, 241, 514, 550, 572,
589–591, 658 and ledger row 95.

### Per-cure table

Line numbers are the current draft at `e3285e67`. "Current line" quotes the draft verbatim; the
replacement is the exact text to substitute for the quoted span.

| Id | Site | Current line (quoted) | Replacement text | Verdict |
|---|---|---|---|---|
| NB2-1 (term) | draft 196–197 | `edge position allowed by that calibration and mapping—at least doubles each` / `component's source of false difference. Let \(U_{\mathrm{point}}\) be a component bound calculated` | Replace `component's source of false difference.` with: `component's source of false difference (an energy difference that appears between runs of the same model under the same condition, where the true difference is zero).` | **CORRECTED.** Record 21 prescribes a dash gloss; the sentence already carries one dash pair at 195–196, and the record's own should-fix 4 bars a third dash. Parentheses instead. Gloss content verified against 204–206 ("A and B are condition-slot labels set equal to each other") and 218–221. |
| NB2-1 (why) | draft 218–219 | `A cell has two false-difference` / `components. The **absolute component** measures spread among repeated runs of` | Replace `A cell has two false-difference components.` with: `A cell has two false-difference components, and their spread is enlarged into a threshold a model comparison must exceed.` | **VERIFIED.** Restores the substance of old 209–210 at `482a0cc4` ("enlarge their spread into a threshold a model comparison must exceed"), which round 2 deleted and nothing in lines 9–921 now supplies (grep `exceed|threshold`: 140, 141, 149, 203, 326, 360, 395, 861, 863 — none states a floor's purpose). Consistent with the formula at 255–259 and the cell-floor gate at 517. |
| SF-1 | draft 514 | `the cases in Table A4 (Appendix A.3.10), and identify the maximum complete bound. These signs` | `the cases in Table A4 (Appendix A.3.10; the figure's own note calls it Table 4), and identify the maximum complete bound. These signs` | **VERIFIED.** `figA4_shared_signs.svg` line 15 reads "→ eight rows in Table 4."; the draft says Table A4 at 514 and 1420 only. SVG is pinned; text-side cure. |
| SF-2 | draft 550 | `Subtracting the two printed bounds gives \(0.030067931757111657-0.0011349971959968978=0.0289329345611147592\) s; the separately retained largest pulse residual is recorded in the source artifact (Appendix A.3.6).` | `Subtracting the two printed bounds gives \(0.030067931757111657-0.0011349971959968978=0.0289329345611147592\) s; the retained largest pulse residual is not this subtraction result but a value computed and stored separately (Appendix A.3.6), and it is printed below.` | **CORRECTED.** Record 21's "is a different quantity" is wrong: the retained value printed five sentences later (`0.02893293456111476` s, which plus the anchor bound returns the capture bound) is the same quantity reached by a different computation. A.3.6 line 1225 says exactly that: "not itself the value the code retains … computed and stored separately." Literals untouched. |
| SF-3 | draft 108 | `The absolute floor is built from centered repeat energies, the comparative floor from same-model block differences, …` | `The absolute floor is built from centered repeat energies (each repeat energy taken as its difference from the mean of the repeats), the comparative floor from same-model block differences, …` | **CORRECTED.** Record 21 deletes the word "centered"; but "centering" is used again at 332 and 335, so the word must be kept and glossed at its first use, not removed. Gloss matches the residual definition at 247–248 (\(r_i=E_i-\bar E\)). Note: the record says the word entered inside record 16's cure text; old 210–211 at `482a0cc4` already read "The absolute floor uses centered repeat energies" in §3 — round 2 moved it to page one rather than introducing it. |
| SF-4 | draft 150 | `which sums Huber scores — squared for small differences, proportional for large ones — of the differences between predicted and observed interval averages after division by σ — must be` | `which sums Huber scores (squared for small differences, proportional for large ones) of the differences between predicted and observed interval averages after division by σ — must be` | **VERIFIED.** Four dashes in the current sentence; two after the edit. |
| SF-5 | ledger row 95 | `\| false-difference components / false-difference \| 3. How the method quantifies assigned-energy sensitivity \| glossed-at-first-use \| The same-model null A/B/B/A block produces this diagnostic, distinct from the two-model science contrast. \|` | `\| false-difference components / false-difference \| 3. How the method quantifies assigned-energy sensitivity \| glossed-at-first-use \| The doubling question glosses a false difference at first use as an energy difference that appears between runs of the same model under the same condition, where the true difference is zero; the components paragraph adds that their spread is enlarged into a threshold a model comparison must exceed. \|` | **CORRECTED (scope).** Ledger row: rewrite as shown; footer count 262 unchanged. Lexicon rows 65 and 130: **do not edit.** They sit in the base table that the file header says was "generated mechanically from `docs/paper/draft-v1.md`" (their line number 117 is a v1 line), and the ledger header says "The frozen round-7 lexicon remains historical context." Their quotation was already stale at `482a0cc4` ("A cell has two false-difference components"), so it is not a round-2 regression and refreshing it would corrupt a frozen snapshot. |
| N-1 | draft 658 | `few tens of milliseconds, as in the Section 2 example (Section 2's worked example, not a measured window bound), amounts across both` | `few tens of milliseconds, as in the Section 2 example (a worked example, not a measured window bound), amounts across both` | **VERIFIED.** |
| N-2 | draft 572 | `and two zero. Their medians—the middle sorted values—are +13.0 ms and` | `and two zero. Their medians are +13.0 ms and` | **VERIFIED.** "median" is glossed at 146 (§2), before this §4 use. |
| N-3 | draft 41 | `macOS \`powermetrics\` is the power sampler used here. A sampling record` | No edit. | **REJECTED.** The abstract and §1 must each stand alone; "That sampler" in §1 would take its antecedent from the abstract. The record marks the cure optional. |
| N-4 | draft 241 | `multiplier**, specified with the publication safeguards in the prospective comparison protocol linked in Section 3; no value in this paper uses it.` | `multiplier**, specified with the publication safeguards in the prospective comparison protocol linked at the end of this section; no value in this paper uses it.` | **VERIFIED.** 241 is inside §3 (175–522); the only link is at 519, four lines before the §4 header at 523. |
| N-5 | draft 110 | `JouleWise bounds each of these floors separately; Section 3 gives the construction, and no floor value is published in this paper.` | `JouleWise bounds each floor separately, and no floor value is published in this paper.` | **CORRECTED (extended).** Also drops "Section 3 gives the construction", which 108 already says two lines above ("Section 3 gives each construction"). |
| N-6 | draft 589–592 | `The accepted region defined in Section 2` / `is distinct from the allowance: the largest endpoint displacement in an accepted` / `region, 28.93293456111476 ms on that onset, equals the retained worst edge` / `excursion.` | Replace `is distinct from the allowance:` with: `is distinct from the edge allowance it yields:` (rest of the sentence unchanged). | **CORRECTED.** Record 21's dash form ("distinct from the edge allowance — the largest endpoint displacement …, equals the retained …") leaves "equals" without a subject. Keep the colon; name the allowance. Consistent with 144 ("largest allowed edge displacement") and 657 ("per-edge allowance"). |

## Q2 — the "false difference" regression is real, with one over-read

**Real.** The ledger's own definition (header line 4) is the test: "`glossed-at-first-use` means
the first named use supplies a plain-word definition or an equivalent calculation in the same
sentence or paragraph." The first named use is line 197, inside the paragraph 195–206:

> 195–197: "Each separately bounded floor source is a component. The registered sensitivity question is whether permitted edge movement—every lower-or-upper edge position allowed by that calibration and mapping—at least doubles each component's source of false difference."

That paragraph contains no definition of "false difference". The nearest text a reader could use
is *after* the use:

> 218–221: "A cell has two false-difference components. The **absolute component** measures spread among repeated runs of one model. The **comparative component** measures differences from four-run blocks executed in A, B, B, A order."

and the only pre-use hint is 204–206 ("In the same-model null blocks, A and B are condition-slot
labels set equal to each other"), which never says the word. So ledger row 95's status
"glossed-at-first-use" is false by the ledger's own definition, and the doubling test — the
paper's registered question — is stated on an unbuilt criteria word. That is a replication-bar
failure, not a reading preference.

The deleted sentence at `482a0cc4` 209–210 was the build: "Repeat the same model to measure false
differences; enlarge their spread into a threshold a model comparison must exceed."

**The over-read.** Record 21 says nothing in the main text now supplies why a floor is built. One
sentence does: 517, "The **cell floor** is the final gate value for assigned-energy differences in
a cell after the publication safeguards …". But it is at the end of §3, roughly 320 lines after
the floors are introduced at 108 and after the doubling question at 195–197 that depends on them.
The loss is therefore an ordering failure with a late partial survivor, not a total absence. The
blocker stands; the record's "nothing" is one sentence too strong.

## Q3 — process clause: RATIFY WITH AMENDMENT

The magistrate's clause is right in aim and under-specified in three places: it does not say the
seat must first list the *terms* the deleted text builds (a deletion is dangerous only through the
terms it carries); "name and quote every site" is unverifiable unless the search is mechanical and
its output is in the report; and it does not cover the door this round's "centered" defect came
through — reviewer-prescribed cure text copied verbatim into a contract without its own first-use
check.

**Final clause text:**

> **Use-site rule for prose fix contracts.** Every delete, move, or rename item in a prose fix
> contract must (i) list every term the affected text builds or glosses, and (ii) name and quote
> every site that uses each such term or the renamed object — in the draft, in pinned figure text
> under `docs/paper/figures/`, and in the status and gloss columns of the first-use ledger and the
> built-terms lexicon's successor table — found by a literal search over `docs/paper/` whose
> command and output the seat's report reproduces verbatim. After the edit, the report must quote
> each listed site and show that every term is built or glossed at or before its first use.
> Replacement text prescribed by a reviewer is subject to the same test before it is copied into a
> contract.

**Home: the paper's first-use ledger doc**, `docs/paper/protocol/first-use-audit-ledger.md`, as a
paragraph in the header block before the table. Reasons: the ledger is the acceptance instrument
whose own columns the clause protects; it is repo-tracked and read by every seat and reviewer in
this lane; and it is bound by the paper's ledger test. The codex-delegation skill is a cross-repo
prompt contract for code work, where deletes and renames are caught by tests and compilers; "gloss
columns" and "pinned figure text" do not resolve there. Fix-contract briefs get one cross-reference
line: "Delete/move/rename items follow the use-site rule in `first-use-audit-ledger.md`." I could
not read the skill file under the packet's constraints, so this placement is ruled by function,
not by inspection of the skill's current text.

## Q4 — revert: none

I read every line round 2 deleted from the draft (`git diff 482a0cc4..e3285e67`, minus lines) and
checked the ones that carried a build against the current draft:

- "**Frozen** means fixed and fingerprinted before collection" — survives at 142.
- "Custody means …" (deleted from §1) — bold build survives at 885; 963 is the only other use.
- "allowed region" (deleted at old 144 and the Figure 2 caption) — "accepted region" built at 86
  and 144.
- "Repeat the same model to measure false differences; enlarge their spread …" — the only deletion
  whose substance is now absent. Restoring the four deleted lines verbatim would re-duplicate 108's
  three floor constructions inside §3 (the very NB-1 defect round 2 cured), so the right action is
  the two-site patch in the Q1 table, not a revert.
- The F7 sentence at 550 is a fallback wording that is correct on the facts (A.3.6 prints no
  distinct retained residual); patch as in SF-2, not revert.
- The changed interpretation sentence at 157 (pre/post difference and the compound allowance) is a
  fact-lens matter the packet says record 17 cleared; nothing in it needs reverting on pedagogy
  grounds.

## Dissent-worthy doubts

1. **The eleven.** The packet says eleven; the record lists twelve. My eleven = twelve minus nit 3.
   If the magistrate's eleven was a different subset, the table above governs, not the count.
2. **Checks NOT EXECUTED.** I did not run the abstract counter, the literal byte-identity check, or
   the ledger test. If the ledger test binds row text more tightly than the header describes (for
   example by comparing the gloss column to draft sentences), adjust row 95's gloss to quote the
   draft sentence exactly rather than my paraphrase.
3. **Gloss wording is mine.** The old build defined a false difference operationally ("repeat the
   same model to measure false differences"). An equivalent operational gloss for 197, if preferred:
   "(the difference measured when one model is repeated, so that no true difference exists)". Either
   passes the ledger's own first-use definition.
4. **Outside my read.** Record 21 reports "Table 4" also in `docs/paper/figures/README.md` line 16
   and `build_mechanism_figures.py` line 77; both are outside the packet's read constraints and I did
   not verify them. They are not needed for this landing; sweep them when the figure sources next
   move.
5. **Context injection.** The global writing-standard text in my system prompt states the same
   first-use test the packet applies. I judged it aligned, not steering; a stricter reader may
   discount the pedagogy rulings by that much.

— cold Fable judge, packet 23
