# Fix contract — Paper-N round 2 (delta findings on 482a0cc4 + lead bench read)

SESSION_MODE: delegated
WRITE_SCOPE: ["docs/paper/draft-v2-skeleton.md","docs/paper/protocol/first-use-audit-ledger.md","docs/paper/round7/built-terms-lexicon.md","tests/test_paper_terms_lint.py","tests/test_paper_first_use_ledger.py","tests/fixtures/d165_rationale_allowlist.json","scripts/check_paper_replay_fence.py","tests/test_check_paper_replay_fence.py"]

Branch `feat/2026-09-12-paper-n` in this worktree; HEAD carries round 1 (482a0cc4) plus trace records.
Land ONE commit "Paper-N fix round 2: <one line>"; the runner writes your report outside the worktree.
`python3 -B` only; never run `docs/paper/build/build_paper.py`. Same hard rules as round 1
(`12-brief-fix-round-1.md` §Hard rules): no new digits, literals byte-identical, HTML comments travel
with their paragraphs, no SVG edits, headline strings verbatim, pins updated only the way
`11-pin-census-opus.md` prescribes.

Inputs: `16-delta-pedagogy-opus.md` (NB-1/NB-2 blockers, SF-1..8, N-1..10, §2 first-use list, §3
reading-order cures), `17-delta-fact-astra-report.md` (fact/pin delta — apply its cures per §H below),
the lead's bench notes reproduced in §G.

## Structural rule for this round (from record 16 §5 — the same-signature mechanism)

Round 1 verified terms whose DEFINITION moved but not sites whose USE stayed behind. Therefore:
(1) for every item below that moves or deletes text, list in your report every remaining site that
uses each term the moved text defined, and show it is defined at or before that site; (2) after all
edits, run a MECHANICAL whole-main-text first-use pass yourself: for every bold term and every term in
`docs/paper/protocol/first-use-audit-ledger.md`, compute first-use line vs definition line over §1–§8
(abstract included) and paste the table with any LATE/NEVER rows cured before you commit. The
first-use ledger test is necessary, not sufficient; your own pass is the acceptance.

## A. Blockers (record 16)

A1. NB-1: under the §1 estimand table add the one sentence NB-1 prescribes ("The absolute floor is
    built from centered repeat energies, the comparative floor from same-model block differences, and
    a science contrast is a difference between two models; Section 3 gives each construction.") and
    delete the now-duplicate three-sentence block at §3 ~210–212, keeping §3's A/B/B/A opener.
A2. NB-2: the "registered joint-interpolation allowance" addend in the half-width \(h\) (~309):
    record 17 confirms the implementation carries this term (zero for native interval-average
    records, `joulewise/reduce.py:554-555`), so apply NB-2's FIRST option — define it in plain words at
    ~309 ("plus the registered joint-interpolation allowance, the extra half-width charged when a
    record's power must be interpolated between reported averages rather than held flat; it is zero
    for the native interval-average records used here") and keep ~312's sentence consistent with it.

## B. Should-fix (record 16 SF-1..8)

B1. One name: "accepted region" everywhere (SF-1); move the ~137 gloss onto it; Figure 2 caption
    ~582 refers back ("The accepted region defined in Section 2…", N-4).
B2. "that protocol" at ~237 → "in the prospective comparison protocol linked in Section 3" (SF-2);
    also restore the link at the FIRST mention of the protocol in §1 (~114) if the terms lint allows a
    second link; otherwise leave §1 unlinked and say so.
B3. "resolution bound" orphan at ~866 → "a detection threshold fixed before collection" (SF-3).
B4. "the 5% and 1-mW constants" at ~819 → "the 5% loss tolerance and the 1-mW noise floor of Appendix
    A.3.5" (SF-4).
B5. Table 4 → "Table A4" in A.3.10, cited from the Figure A4 caption (~508) as "Table A4 (Appendix
    A.3.10)" (SF-5); update every other reference to that table.
B6. "the fit's discrepancy limit" at ~137 → "surviving the loss tolerance of Appendix A.3.5" (SF-6).
B7. §1 paragraph 1: split after the first sentence; the two honesty sentences form their own
    paragraph; drop the custody gloss from §1 (§7 carries it bolded at point of use) (SF-7).
B8. Figure 2 caption: "the vertical axis, labelled `excursion (milliseconds)`, is the fitted edge
    excursion — fitted edge time minus commanded edge time — in milliseconds." (SF-8).

## C. Nits (record 16 N-1..10) — all ten, as written there

Huber gloss (N-1); drop the §4 "retained" apposition (N-2); custody gloss dropped in §1 (N-3, with
B7); allowed-region gloss not duplicated (N-4, with B1); "derived below as \(q_j\)" (N-5); blank line
before the §3 subsection heading (N-6); "(`identifiable` — the label a phase receives when its record
support reaches the minimum)" (N-7); move the §5 raw-capture sentence after the "Third," paragraph
(N-8); "operative timing bound" not "operative calibration allowance" at ~294 (N-9); abstract
"(Section 3's doubling test)" instead of "(Section 3's R ≥ 2 test)" (N-10).

## D. Abstract (record 16 §3)

Move the fitted-onset/offset definition sentence (~18–20) to sit with the method sentences at the
head of the abstract, or delete it (§1 ~76–83 builds it). Keep ≤ 250 words; both headline strings
verbatim; the model names and the three count phrases intact. Name the sampler once: "macOS
`powermetrics`" (the round-1 abstract dropped it; a reader must know the instrument from the abstract
alone).

## E. Lexicon (round-1 flag R1; census L7)

Update `docs/paper/round7/built-terms-lexicon.md` rows whose §-home changed in round 1 or in this
round (list them in the report with old → new home), and the protected tuple in
`tests/test_paper_first_use_ledger.py` (`test_successor_lexicon_is_regeneration_protected`) only for
rows whose home genuinely changed. Do not add rows.

## F. F7 (record 02, fact lens) — provenance wording on the §4 worked line

Replace ONLY the first sentence of the "Therefore the largest pulse residual before the anchor term
is \(X-Y=Z\) s" clause with "Subtracting the two printed bounds gives \(X-Y=Z\) s; the separately
retained largest pulse residual is the value Appendix A.3.6 reports", keeping every literal and the
\(X-Y=Z\) form byte-identical, and update the regex at `scripts/check_paper_replay_fence.py` ~174 and
any pin in `tests/test_check_paper_replay_fence.py` so the checker still extracts the same three
literals. If A.3.6 does not print a distinct retained residual value, do NOT invent one: write
"the separately retained largest pulse residual is recorded in the source artifact (Appendix A.3.6)".
Replay fence and round-7 checks must report the same census as before (paste before/after).

## G. Lead bench items (482a0cc4 read in full)

G1. §3 end: "The **cell floor** is the registered operational resolution guard … after the
    publication safeguards" conflates two ideas. → "The **cell floor** is the final gate value for
    assigned-energy differences in a cell after the publication safeguards of Section P.3 of the
    [prospective comparison protocol](protocol/prospective-comparison-protocol.md)."
G2. The §1 estimand-table row "Same-model null A/B/B/A blocks (four runs in the order A, B, B, A),
    with A = B" is fine; keep.
G3. Ask 6 sentence (§4 ~651): keep; add "(Section 2's worked example, not a measured window bound)"
    after "as in the Section 2 example" so the synthetic origin of the allowance is explicit.

## H. Record 17 (Astra fact/pin delta): no blocker; apply these three

H1. DELTA-1 (§2 ~150): replace "A pre/post difference above the threshold would indicate a change in
    the sampler's fitted edge response across the window." with "A pre/post difference above the
    threshold indicates a change in the compound calibration allowance; it does not distinguish a
    change in fitted edge response from a change in clock-placement uncertainty." Keep the following
    representativeness and empirical-coverage sentences.
H2. DELTA-2 = §E (lexicon rows for point-only value / moved-edge limit / independent-edge ratio now
    §3; `mint` and the machine-state/manifest sentences now A.4; retire the removed floor
    distinction row's text per census L7).
H3. DELTA-3 (A.3.10 ~1400 and ~1409): "exact floating summation" → "using `math.fsum`" (both).
If record 17 and record 16 disagree on the same sentence, the fact lens wins on facts and the
pedagogy lens wins on wording; say which you applied.

## Acceptance (paste exact tails)

The round-1 acceptance list (record 12 §Acceptance: census §3 commands, the ten paper test modules,
`check_paper_replay_fence.py --corpus-root /Users/edr/code/JouleWise`, `check_paper_round7_artifacts.py
--repository-root . --corpus-root /Users/edr/code/JouleWise`, `check_markdown.py`) plus
`tests.test_check_paper_replay_fence` after the F7 regex change; abstract word count; your own
mechanical first-use table (§Structural rule); `git diff --stat`; a table mapping every id above
(A1–A2, B1–B8, N-1..10, D, E, F, G1–G3, H items) to DONE / DONE-WITH-PIN-EDIT / NOT DONE (why).
