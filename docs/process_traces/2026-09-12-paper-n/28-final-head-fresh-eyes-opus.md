# Record 28 — fresh-eyes final-head review (gate row 10), PR #331

Reviewer: Opus 5 (1M), fresh session, read-only.
Worktree: `/Users/edr/code/JouleWise-wt-paper-n`, HEAD `be87d551` (confirmed with `git rev-parse HEAD`
before any file was opened); code-final head `0fa5fa60`; review delta `e3285e67..0fa5fa60`.
`git diff --stat 0fa5fa60..be87d551` = records 25 and 27 only, no code.

**Verdict: no blocker. Two should-fix (both record-side / test-coverage, neither touching the
draft's prose or any literal), six nits. The ten draft edits, the ledger row, the lexicon row, the
fence change and the new test all match the ruling and the synthesis at the stated sites, and the
draft gained no quantitative numeral.**

## Contamination disclosure

Opened, read-only, in this order: the review delta (`git diff --stat`, then the substantive diff
restricted to the six changed files); `24-coldgate-fable-ruling-23.md`; `27-magistrate-synthesis-gate-23.md`;
`25-coldgate-opus-refuter-23.md`; `22-delta2-fact-astra-report.md` (head, through the R2-1/R2-2
cures and the F1–F10 closure table); `docs/paper/draft-v2-skeleton.md` (the ten edited regions plus
whole-file greps for `spread`, `median`, `allowance`, `reservation plan`, section headers, the §3
protocol link); `docs/paper/draft-v1.md` (the worked-arithmetic paragraph only);
`docs/paper/protocol/first-use-audit-ledger.md` (header 1–32, rows 65 and 105, footer);
`docs/paper/round7/built-terms-lexicon.md` (header and successor table 1–30);
`scripts/check_paper_replay_fence.py` (`_search`, `_paragraph`, `extract_draft_literals`);
`tests/test_paper_replay_fence.py` (class `DraftLiteralExtractionTests`);
`tests/test_paper_first_use_ledger.py` (`LEXICON_REQUIRED_TERMS`, table-header and footer checks).

Executed (all read-only, all `python3 -B`, nothing written outside this report): fence extraction
against both committed drafts in-process; a whole-file count of the new alternation's matches in
each draft; a numeral-token set difference between `e3285e67` and `0fa5fa60` for the draft, the
ledger and the lexicon; a membership check of every `LEXICON_REQUIRED_TERMS` string against the
lexicon file. **NOT EXECUTED, by the brief:** `build_paper.py`, and the full paper suite (being
replayed separately). I did not re-run the lead's bench acceptance in record 27; I take its
transcript as reported and my findings do not depend on it.

Harness-injected context I did not request: the session system prompt carried the user's global
`~/.claude/CLAUDE.md` (whose "Writing standard" section states the same first-use / replication bar
the packet applies), the JouleWise `CLAUDE.md` + `CLAUDE.local.md` doctrine, and the `MEMORY.md`
index (one-line pointers; no memory file opened). As with the cold judge, the injected first-use
test coincides with the packet's own bar, so it steered nothing below; a reader should know it was
in context. I also carry the parent's framing that this is a final-head gate on a landed round; I
re-derived every verdict from the files rather than from that framing.

## Per-item table

| # | Item | Verdict | Evidence (final head) |
|---|---|---|---|
| 1a | Ten draft edits match the ruling/synthesis text exactly at the stated sites | **PASS** | Quoted below, site by site. |
| 1b | No site missed; N-3 correctly not applied | **PASS** | Judge's land set = 10 draft + ledger row 95; all present. Line 41 ("macOS `powermetrics` is the power sampler used here.") is untouched — N-3 REJECTED by the judge, dropped by the refuter. |
| 1c | Nothing else changed in the draft | **PASS** | `git diff e3285e67..0fa5fa60 -- docs/paper/draft-v2-skeleton.md` = 10 hunks, 23 changed lines, all ten cures; `git show --stat 0fa5fa60` = exactly 6 files (draft, ledger, lexicon, fence script, two test files), 36 insertions / 15 deletions. The two deleted `*.manifest.jsonl` files and the `00-DURABLE-STATE.md` update in the wider range come from earlier commits (`62df220f`, "untrack two runner manifests committed by mistake"), not from the round-3 commit. |
| 2a | Fence regex keeps exactly-one-match | **PASS** | `_search` (line 120–124) is unchanged and still raises `FenceError` unless `len(matches) == 1`; the two prefixes are a **non-capturing** group `(?:…|…)`, so groups 1–3 still bind the minuend/subtrahend/result. Whole-file match count of the new pattern: draft-v2 = 1, draft-v1 = 1. |
| 2b | Both drafts extract | **PASS** | In-process: `draft-v2-skeleton.md EXTRACTED 22`, `draft-v1.md EXTRACTED 22`, and the two literal dicts are **fully equal** (`a == b` → True, zero differing keys) — the V13 failure record 22 reported (`residual subtraction: expected exactly one anchor match, found 0`) is cured. |
| 2c | New test exercises the frozen `docs/paper/draft-v1.md` | **PASS** | `test_frozen_v1_draft_still_extracts` reads `ROOT / "docs" / "paper" / "draft-v1.md"` — the committed frozen file, not a fixture or a mutated string — and asserts extraction succeeds. See nit N-a for a free strengthening. |
| 3a | Use-site rule carries record 27's merged intent | **PASS with a nit** | Judge's clause text present in full; refuter arm (a) present as "(for a deletion: the terms in the removed lines that still occur in the post-edit draft)"; arm (b) present as "found by a literal search over `docs/paper/` whose command and output the seat's report reproduces verbatim"; prescribed-text rule present as its own sentence. Nit N-f: the judge's "the report **must** quote … and show" became indicative "the report quotes … and shows". |
| 3b | Paragraph sits before the table | **PASS** | Ledger lines 17–26; the table header `\| Term \| First reader-facing home \| Status \| Definition or disposition \|` follows at line 28. Footer still reads "Terms inventoried: 262; FAILS: 0." — row 105 was rewritten, not added, as the judge required. |
| 4 | Lexicon row 23 and the protected tuple agree | **PASS** | Lexicon line 23 home = `§2 (reservation plan) / A.4 (the rest)`; `LEXICON_REQUIRED_TERMS` carries the byte-identical row prefix. All nine tuple strings verified present in the lexicon file by literal membership. The compound-home format is house style (`\| measured contrast / custody / Figure P1 \| protocol P.3 / §7 \|`). See nit N-d for the residual ledger/lexicon divergence. |
| 5 | First-use check on the edited sentences | **PASS** | No term is now used before it is built. Detail below. |
| 6 | New numerals in the diff | **PASS (one non-quantitative token, disclosed)** | Draft numeral-token delta `e3285e67 → 0fa5fa60`: **added `{'4': 1}`, removed `{'3': 2, '2': 1}`**. The single added token is the figure label in SF-1's "the figure's own note calls it Table 4", which the judge ruled and which quotes the pinned `figA4_shared_signs.svg` line 15 verbatim; it is a cross-reference identifier, not a measured quantity. Zero new quantitative digits, consistent with D-174 and record 22's rule. (Outside the draft: the lexicon gained `2` in "§2", the ledger gained the clause's own gate id and date "23, 2026-09-12".) |

### Item 1 — the ten draft edits, quoted at the final head

| Cure | Final-head line | New text (quoted) | Source it must match |
|---|---|---|---|
| SF-3 | 108 | "The absolute floor is built from centered repeat energies (each repeat energy taken as its difference from the mean of the repeats), the comparative floor from same-model block differences," | ruling SF-4/SF-3 replacement, verbatim |
| N-5 | 110 | "JouleWise bounds each floor separately, and no floor value is published in this paper." | ruling N-5 "CORRECTED (extended)", verbatim |
| SF-4 | 150 | "which sums Huber scores (squared for small differences, proportional for large ones) of the differences between predicted and observed interval averages after division by σ — must be" | ruling SF-4, verbatim; dash count in that sentence drops from four to two |
| NB2-1 (term) | 197 | "component's source of false difference (an energy difference that appears between runs of the same model under the same condition, where the true difference is zero)." | ruling NB2-1(term), verbatim; record 27 "judge's text" |
| NB2-1 (why) | 218–220 | "A cell has two false-difference / components; the spread of each is enlarged into a threshold a model comparison / must exceed. The **absolute component** measures spread among repeated runs of" | record 27's merged text (judge's clause + refuter's "the spread of each"), verbatim |
| N-4 | 242 | "multiplier**, specified with the publication safeguards in the prospective comparison protocol linked at the end of this section;" | ruling N-4, verbatim. Independently re-verified: 242 is inside §3 (headers at 175 and 524) and the only protocol link is at 520, four lines before the §4 header. |
| SF-1 | 515 | "the cases in Table A4 (Appendix A.3.10; the figure's own note calls it Table 4), and identify the maximum complete bound." | ruling SF-1, verbatim (judge's "the figure's own note", not the refuter's shorter "the figure's note") |
| SF-2 | 551 | "; the retained largest pulse residual is not this subtraction result but a value computed and stored separately (Appendix A.3.6), and it is printed below." | ruling SF-2, verbatim; record 27 "judge's text". Consistent with A.3.6 at 1226 ("not itself the value the code retains … computed and stored separately"). No literal in the paragraph moved — the 22 extracted literals are unchanged and identical to draft-v1's. |
| N-2 | 573 | "and two zero. Their medians are +13.0 ms and" | ruling N-2, verbatim |
| N-6 | 591 | "is distinct from the allowance it yields: the largest endpoint displacement in an accepted" | record 27's explicit synthesis ("distinct from the allowance it yields:" — antecedent supplied, no new term), **not** the judge's "the edge allowance it yields"; the deviation is the recorded resolution of judge-vs-refuter on N-6, and it avoids coining "edge allowance" beside "per-edge allowance" at 659. Colon kept, so "equals" keeps its subject. |
| N-1 | 659 | "as in the Section 2 example (a worked example, not a measured window bound)" | ruling N-1, verbatim |
| SF-5 (ledger) | ledger 105 | "The doubling question glosses a false difference at first use as an energy difference that appears between runs of the same model under the same condition, where the true difference is zero; the components paragraph adds that the spread of each is enlarged into a threshold a model comparison must exceed." | ruling SF-5, with "their spread" → "the spread of each" so the row quotes the draft as landed. Deviation is required by the synthesis and is strictly more accurate. |
| SF-5 (lexicon) | — | not edited | Both seats refused the lexicon base-row half (generated draft-v1 provenance). Confirmed: lexicon rows in the `Draft-v1 generated base` section are untouched; the only lexicon change is successor row 23 (R2-2). |

### Item 5 — first-use check over the edited sentences

- **"centered" (108)** — was unbuilt at its first use; now glossed in the same clause ("each repeat
  energy taken as its difference from the mean of the repeats"). Later uses at 332/335 follow it.
  "mean" is already in use in the same sentence ("mean B energy minus mean A energy").
- **"false difference" (197)** — the blocker. `grep -n "false difference\|false-difference"` returns
  197 and 218 only; 197 now carries the gloss, 218 follows it. Row 105's `glossed-at-first-use`
  status is now true against the ledger's own definition ("the first named use supplies a plain-word
  definition … in the same sentence or paragraph"). Regression closed.
- **"threshold" (219)** — on the ledger's `audience-vocabulary` list (header line 5, explicitly
  enumerated), so no build is owed; it is also already used at 149 and 157.
- **"spread" (219)** — first occurrence moves one clause earlier than before, from 220 to 219. The
  operational gloss ("measures spread among repeated runs of one model") is the next sentence, same
  paragraph, which satisfies the ledger's stated same-paragraph standard. No cure owed; recorded as
  nit N-c so the next round does not re-litigate it.
- **"median" (573)** — N-2 deleted the duplicate gloss; the surviving build is at 146 ("the median
  (the middle sorted value, or the mean of the two middle values for an even count)"), 427 lines
  earlier and in §2. Safe.
- **"the allowance it yields" (591)** — supplies the missing antecedent without coining a term;
  "allowance" is long in use (23, 123, 173, 233, 298, 314 …) and the colon still defines the
  quantity in the same sentence.
- **"Table 4" (515)** — quotes the pinned SVG's own label, in the house style already used at 164
  ("the **entry check** (labelled the admission gate in Figure A2)"). No new term of art.
- 110, 150, 242, 551, 659 introduce no term at all (deletion, punctuation, pointer rewording,
  clarification, de-tautologising).

## Findings

### Blockers

**None.**

### Should-fix

**SF-28-1 — record 27's "after-edit text the judge required quoted" block quotes pre-edit line
numbers, so eight of its thirteen quotes do not show the cured text; one is empty and one is
missing.** The judge's landing condition was explicit: "The landing record must quote the after-edit
text of lines 108, 110, 150, 197, 218, 241, 514, 550, 572, 589–591, 658 and ledger row 95."
NB2-1(why) inserted one line at 219, so every site after 218 shifted by +1 in the landed file.
Record 27's block was harvested at the old numbers against the new file, with these results:

| Record 27 label | What record 27 quotes | The line the cure actually changed |
|---|---|---|
| 241 | "energy at its recorded value. The later factor is the **small-sample" (unchanged line 241) | 242, "…linked at the end of this section" |
| 514 | "The lower rows apply one shared sign and one local sign per block, enumerate" (unchanged line 514) | 515, "…the figure's own note calls it Table 4" |
| 550 (F7 sentence) | **empty** — the entry runs straight into the next bullet ("- 550 (F7 sentence): - ledger row 95: 105:\|…") | 551, the whole SF-2 sentence |
| 572 | "onset lags are all positive; 49 of 59 offset lags are negative, eight positive," (unchanged line 572) | 573, "Their medians are +13.0 ms and" |
| 589 / 590 | two unchanged lines; **591 is absent** | 591, "is distinct from the allowance it yields:" |
| 658 | "in the retained a10 sample described below (DG-071). A per-edge allowance of a" (unchanged 658) | 659, "(a worked example, not a measured window bound)" |

Only 108, 110, 150, 197 and 218/219 actually display cured text, and each of those is truncated
mid-word at ~180 characters ("Section 3 g", "predicte", "true difference i"). The **edits
themselves are correct** — I verified all ten against the ruling and the synthesis independently,
above — so this is an audit-record defect, not a draft defect. It matters because the quote block is
the artifact a later reader (or Ed) uses to confirm the landing without re-running the diff, and as
it stands it certifies less than it appears to.
*Minimal cure:* append a dated addendum to record 27 (or add it to this record's lane) quoting the
final-head lines 108, 110, 150, 197, 218–220, 242, 515, 551, 573, 591, 659 and ledger line 105
untruncated. The table in Item 1 above already contains that text and can be transcribed verbatim.

**SF-28-2 — widening the fence regex removed the only mechanical guard against the F7 sentence
regressing to the v1 wording inside draft-v2, and nothing replaces it.** Before the change, the
fence's single anchor `Subtracting the two printed bounds gives` was, incidentally, also a pin on the
round-2 F7 prose cure. The two-prefix alternation is the right fix for R2-1, but it now accepts
`Therefore the largest pulse residual before the anchor term is …` in **either** draft, so a future
edit could restore the misdirecting v1 phrasing to draft-v2 and every fence check would still pass.
`grep -rn "Subtracting the two printed bounds\|is not this subtraction result"` over `tests/`,
`scripts/` and `docs/paper/` returns only the script's own regex and the draft line itself — no test
pins the cured sentence. This is not a blocker (the cure is landed and correct; the literals are
byte-identical and separately fenced), but the class of defect just cured is now unfenced.
*Minimal cure:* one assertion in `DraftLiteralExtractionTests`, e.g.
`self.assertIn("is not this subtraction result but a value computed and stored separately", self.text)`
— optionally with `self.assertNotIn("largest pulse residual before the anchor term is", self.text)`
so the v1 prefix stays v1-only.

### Nits

**N-a.** `test_frozen_v1_draft_still_extracts` asserts key-set equality plus one value
(`subtraction_result`). I verified that the two literal dicts are **fully equal** at this head
(`extract_draft_literals(v1) == extract_draft_literals(v2)` → True, zero differing keys), so
`self.assertEqual(v1_literals, self.literals)` is strictly stronger at zero cost and would catch a
v1/v2 literal divergence that the current pair of assertions lets through. One-line change.

**N-b.** 219 restores the deleted build's own wording ("enlarged into a threshold a model comparison
must exceed", verbatim from `482a0cc4` line 209–210), which is what the blocker asked for. It does
not take the refuter's suggested "into **the floor** a model comparison must exceed", so the reader
is still not told that this threshold *is* the floor built at 108–110; the identification arrives
only at 517 ("The **cell floor** is the final gate value…"), ~300 lines later. No action required —
the judge's text was chosen deliberately in record 27 — but if a future pass wants the component→floor
link, this is the one-word site.

**N-c.** "spread" now first occurs at 219 without its operational qualifier, which arrives in the
next sentence (220). It passes the ledger's same-paragraph standard, so no cure is owed; recorded so
a later pedagogy lens does not re-open it as a finding.

**N-d.** Ledger row 65 still homes the whole five-term group ("declared machine state /
instrument-validation manifest / reservation plan / calibration ledger / calibration-acceptance
file") at "Bracketed pulse-train algorithm" (§2), while lexicon row 23 now reads "§2 (reservation
plan) / A.4 (the rest)". R2-2's cure is exactly as prescribed and strictly reduces the divergence
(the two instruments now agree on the reservation plan, where they previously disagreed on all
five), but the two files still disagree about the other four members' first-use home. Sweep item,
not a landing defect.

**N-e.** Two blank lines separate `test_internal_check_catches_a_perturbed_difference` from the new
method inside the class (one extra). Cosmetic; no lint gate in the repo enforces it.

**N-f.** The installed use-site clause states the post-edit obligation in the indicative ("the
report quotes each listed site and shows every term built or glossed at or before its first use")
where the judge's ratified text used "must quote … must show", and it compresses the
prescribed-text sentence ("carries no exemption" vs "is subject to the same test" — both arms are
present). The merged paragraph is complete on substance (judge's clause + refuter arm (a) as the
deletion parenthetical + refuter arm (b) as the literal `docs/paper/` search + the prescribed-text
rule); restoring "must" would make the obligation unambiguous to a seat skimming it.

## Same-signature statement

**No same signature, and the standing escalation trigger is NOT met by this round.** The signature
of rounds 1 and 2 was *a prose edit leaving live uses of a term whose build it removed* (round 2's
NB2-1 on "false difference"; round 1's NB-1/NB-2 residue) and, secondarily, *the acceptance
instrument certifying a status it did not satisfy* (round 2's ledger row 95 asserting
`glossed-at-first-use` at an unbuilt first use). Round 3 reproduces neither in the paper text: I
re-ran the first-use test over all twelve edits and found no term used before it is built, the
`false difference` grep returns exactly the two sites with the gloss now first, and the numeral-token
set difference is `{'4'} added / {'3','3','2'} removed` — one figure label, zero quantities.

The one echo worth naming is **SF-28-1**, which belongs to the *family* of round 2's SF-5 — an
artifact asserting more verification than it performed — but it is one instance in a record, not a
repeat in the same instrument, and the underlying edits are correct. On the two-consecutive-rounds
rule that is a single occurrence, so the next spend is the two-line cure, not a consult. Both
should-fix items are mechanical, land in one commit, and neither requires re-running the paper suite
beyond `tests.test_paper_replay_fence`.

— Opus 5 fresh-eyes reviewer, gate row 10, final head `be87d551` / code-final `0fa5fa60`
