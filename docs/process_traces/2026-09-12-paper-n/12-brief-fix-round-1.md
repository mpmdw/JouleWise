# Fix contract — Paper-N round 1 (advisor-readiness pass on the merged article)

SESSION_MODE: delegated
WRITE_SCOPE: ["docs/paper/draft-v2-skeleton.md","docs/paper/protocol/first-use-audit-ledger.md","tests/test_paper_terms_lint.py","tests/test_paper_first_use_ledger.py","tests/fixtures/d165_rationale_allowlist.json"]

Branch `feat/2026-09-12-paper-n` in this worktree (base origin/main dbe6c675). Land ONE commit
"Paper-N fix round 1: <one line>" with every edit below; write your report to
`docs/process_traces/2026-09-12-paper-n/13-fix-round-1-astra-report.md`. Sandbox has no network.
Always run Python as `python3 -B` (no __pycache__), and do NOT run `docs/paper/build/build_paper.py`
(its output is out of scope); the lead builds at the bench.

## Read first, in this order

1. `docs/process_traces/2026-09-12-paper-n/11-pin-census-opus.md` — every mechanical pin on the
   draft and the legitimate way to update each. The paper is heavily pinned; an edit that breaks a
   pin is only acceptable when you update the pin the way that record prescribes (ledger `home`
   cells, terms-lint required constructions, first-use cure paragraphs, the d165 allowlist line
   number). NEVER touch `docs/paper/fill-rehearsal/select_outcome_branches.py`: the
   ABSTRACT_HEADLINE and CONCLUSION_HEADLINE strings stay verbatim, exactly once each.
2. `02-review-fact-astra-report.md` (F1–F10), `04-review-pedagogy-opus.md` (B-1..3, S-1..14,
   N-1..7, RO-1..9, F-1..4), `06-blind-fable-advisor-read.md` (Asks 1–12),
   `08-litread-verify-opus.md` (S1, S2, nits). The dispositions below are the lead's; where a
   record's proposed cure conflicts with a pin, the pin wins and you say so in the report.

## Hard rules

- The scope is frozen (D-174): no new experiments, no new numerals. NO new number may enter the
  main text unless it is already printed elsewhere in the draft; derived fractions (Ask 6) are
  written in words ("more than half", "roughly a quarter") without digits. No registry edits.
- Every numeral the pin census marks non-roundable or replay-fenced keeps its exact literal.
  Where a 17-digit literal is unreadable in prose (Ask 7: `2.92078162242509999197`,
  `10.164834757777545 ms`, `0.030067931757111657 s`, `0.0000010000000000000002`), keep the literal
  and add a rounded reading in front of it in this exact shape: "about 30.1 ms (retained as
  0.030067931757111657 s for byte-exact replay)". Never delete or alter the literal itself; the §4
  worked-arithmetic line 588 and its stamp spans are untouchable.
- HTML comments (`<!-- … -->` registry tokens, `[FILL:PE-01]`) survive every move: when a paragraph
  moves, its comment moves with it, byte-identical. The 228 retired locators must not reappear.
- Figures: SVGs are pinned generator outputs; do not edit them. Text-side cures only.
- Do not restyle passages no finding names. Sentence-level edits; moved paragraphs move verbatim
  unless a finding names the change.

## Edits (ordered; each item names its source)

### A. Page-one honesty (Ask 1, Ask 10, RO-4)
A1. Abstract: keep both headline strings verbatim, both model names and the three count phrases
    the terms lint requires, and stay ≤ 250 words. Within that, add one sentence: "This paper
    specifies the sensitivity calculation and demonstrates it on synthetic inputs; it reports no
    sensitivity ratio on measured inference data." Cut glossary sentences from the abstract to make
    room only where the first-use ledger permits (the abstract is a ledger home for 13 rows —
    re-home those rows to §1 where the same gloss already exists, or keep the sentence). Replace
    "phase-energy dominance" (RO-4) with the plain form given in RO-4.
A2. §1 first paragraph: add the same no-measured-ratio sentence once, and one sentence: "The raw
    captures behind the historical numbers are retained under project custody and are not
    released; the synthetic examples are the only fully reproducible part." (Ask 10; §7 keeps its
    fuller statement.) Add the raw-capture sentence to §5 "Further limitations" as well.

### B. Introduction compression (Ask 9, RO-3, S-3, S-4, S-14, Ask 11, RO-9)
B1. §1 lines ~108–160 (from "A **configuration cell**…" through the R_cm paragraph): compress to
    (i) the cell definition, (ii) the three-row estimand table, (iii) one sentence: "JouleWise bounds
    each floor source separately; Section 3 gives the construction, and no floor value is published
    in this paper", (iv) the short-prefill paragraph. Move the definitions of point-only value,
    moved-edge limit, independent-edge ratio R, energy-allowance sign and R_cm to §3 immediately
    before their first use (RO-3), re-homing their ledger rows.
B2. One name for the floor: delete "the **detection floor** in the advisor's terminology" and
    "the artifacts call the final gate value … the **cell floor**"; keep exactly ONE term for the
    final gate value wherever §3 needs it (prefer "detection floor"; if the terms lint pins "cell
    floor", keep "cell floor" and drop the other). Delete "in the artifacts" / "in the advisor's
    terminology" everywhere (S-4). Protocol P.3 gets its link once (S-3 cure) and the small-sample
    multiplier sentence from S-3.
B3. Move the synthetic enclosure paragraph (§1 ~66–73, with its Figure A1 sentence) to §3 directly
    after the 1.20 J / 1.80 J Figure 1 example; replace "it is reported, never composed into any
    bound" with "it is shown for contrast and is not added to any result in this paper" (Ask 11).
B4. RO-9 wording at §1 ~146.
B5. §2 window paragraph (~214–232): keep stage / admitted / entry check / reference runs / A/B/B/A
    member definitions (they describe the measured window); delete the whole-window allowance,
    energy family, reference-trajectory excursion and issued repeatability bound sentences (they
    produce no number here) and replace them with one sentence: "A separately measured whole-window
    allowance, defined in the prospective comparison protocol, is not used by any value in this
    paper." Re-home or retire their ledger rows per the census.

### C. Section 2 as a physical procedure (Ask 3, RO-1, B-3, S-6, S-10, RO-5, N-1, N-2, N-3)
C1. The first paragraph of "Bracketed pulse-train algorithm" (~191): reduce the integrity
    bookkeeping to one sentence ("Every input to a capture — the calibration artifacts, the frozen
    reservation plan, and the capture's own manifest — is fingerprinted, and any mismatch refuses
    the capture; Appendix A.4 lists the identifiers and refusal names."); move the removed
    sentences (with `validation_manifest_sha256`, `instrument_calibration_invalid`,
    `joulewise/reduce.py`, `PLAN_HASH_MISMATCH`, `ISSUED_ACCEPTANCE_REGISTRY`,
    `GENESIS_FIXTURE_ACCEPTANCE_SHA256`, etc.) verbatim into Appendix A.4 (or A.5 if A.4 is the
    wrong home) as a new paragraph. Ledger rows homed there re-home with them.
C2. RO-1 reorder: the numeric-rules paragraph (~193–202) moves after the detector paragraph
    (~204), opening "The checks above use the following fixed numbers. Define resting power…".
C3. B-2 / F10: rename resting power to \(P_{\mathrm{rest}}\) in every §2 and A.3.5 occurrence
    (keep \(b\) for the operative timing bound only). Update the quiet-record threshold formula
    accordingly.
C4. B-3: define the fit loss at its first use with the Opus cure wording, using the loss's true
    unit from A.3.5 (verify it there); reconcile "amplitude" → "pulse height" everywhere (S-7).
C5. S-10 rectangle clause; RO-5 "allowed region" definition moved to ~204 and unbolded in the
    Figure 2 caption; N-1, N-2, N-3 as written.
C6. F3: at ~204 add "in exact arithmetic" to the lower-bound sentence and, in A.3.5, one sentence
    disclosing that the floating-point search has no independently established directed-rounding
    containment guarantee; historical values unchanged.
C7. F6 (three cures): the 17-capture selection rule beside the table (two exclusions and their
    criterion, from A.3.8); the t-rule identified as the registered independent equal-variance
    normal-model convention without claiming empirical 99% coverage; network-time refusal
    attributed to prospective admission. Ask 12: add the two sentences (what a pre/post
    difference above the threshold would physically indicate; conditional on the retained corpus
    being representative, untested). F10: "unrounded" → "retained SD operand".

### D. Section 3 completeness (F1, F2, F8, Ask 8, S-9, S-13, S-8)
D1. F1: before ~333, insert the member-domain construction and the floor-input endpoints exactly
    as F1's minimal cure states (raw envelope vs symmetric interval; breakpoint rule; coverage
    refusal). F2: the strict noncollapse rule and the local-width definitions before their
    calculations; cross-reference §4 for the three-record rule.
D2. Ask 8: open the R_cm subsection with one plain sentence contrasting R and R_cm ("R asks how
    much the bound grows when every run's edges move independently; R_cm asks how much it grows
    when one direction of energy allowance is applied to every block at once and each block's own
    edges then move to their worst local corner"); move the outward-rounding/padding paragraph
    (p = 64·ulp·M, ~434–437) and Table 4 to Appendix A (new subsection A.3.9 or the closest home),
    with F8's padded-q_j definition and the two-role source-map correction applied there.
D3. S-9 (E^L/E^U and block index j declared), S-13 (rename pad to `pad`, r_{jm} to λ_{jm}), S-8
    ("excursion" only for milliseconds; "energy swings" at ~408; "spread" at ~228 if that sentence
    survives B5).

### E. Section 4/5/8 honesty and redundancy (Ask 4, 5, 6; F4, F5, F7; S-1, S-2, S-5; §8 dedupe)
E1. F4 qualification at ~176 ("For adjacent phases sharing the moved boundary…", plus the
    separately stamped historical windows and possible gap, one sentence).
E2. F5: apply all seven table cures verbatim (§1:95–97, §4:608, A.3.5:1181, A.3.5:1176,
    §5:848–852, §4:697–698 + §8:936, §4:750–751). The §8 sentence is terms-lint pinned: update the
    pin.
E3. F7 at ~588: replace ONLY the first sentence as F7 prescribes; the literals stay byte-exact.
E4. Ask 4: in A.3.5 two sentences (σ sat at its 1-mW floor on the retained capture; the accepted
    region is therefore a tolerance set whose width depends on the 5% and 1-mW constants, which
    were not varied) and one sentence in §5 "Further limitations"; describe the plateau scatter in
    words only (no new digits).
E5. Ask 5: one short paragraph in §5: 59 of 59 onsets late and 49 of 59 offsets early is a
    one-directional pattern; two candidate explanations (GPU start latency after the command;
    sampler window stamping) are named, neither tested; no correction is applied; the symmetric
    ±b domain therefore includes the bias and is wider on the side the bias does not occupy.
E6. Ask 6: after the medians in §4, one sentence in words: a per-edge allowance of a few tens of
    milliseconds is more than half of a 136-ms phase across both edges and roughly a quarter of a
    281-ms phase; and one sentence that the three-record minimum guards only against a split
    supported by two straddling averages, not against a timing envelope comparable to the phase
    energy. (Digits already printed nearby — 0.1365 s, 0.2815 s — may be referred to as "the
    1.5B median" / "the 7B median"; write no new digits.)
E7. S-1, S-2, S-5 glosses; RO-2 abstract wording; RO-8 source-map sentence moved before first use.
E8. §8: delete the second record-support restatement (~936–938, "Record identifiability depended
    … each.") after E2's rewording of ~936 — keep exactly one statement of the counts in §8 (the
    pinned CONCLUSION_HEADLINE stays); update the terms-lint pin the census names.

### F. Figures and related work (B-1, F-2, F-4, RO-7, S-11, S-12, N-5, N-7; LITREAD S1/S2)
F1. B-1 cure at ~178 verbatim. F-2: caption says "fitted edge excursion in milliseconds (the
    axis label)". F-4/S-12: "(labelled the admission gate in Figure A2)". RO-7/S-11: renumber the
    two §3 figures to Figures 2 and 3 and the existing Figures 2 and 3 to 4 and 5, updating every
    cross-reference; A1/A2 stay in the appendix with the RO-6 one-clause statement at each citing
    site. N-5: leave file names (pinned) and add nothing. N-7 as written.
F2. LITREAD S1: "independently" → "against the GPU's own hardware energy counter" (read 08 §S1 for
    the exact sentence); S2: scope the [6] absence claim to the published paper.
F3. F9's three related-work cures verbatim.

### G. Not done in this round (record as such)
Retitling (Ask 1's alternative) — Ed's call; the abstract sentence covers honesty. Promoting A1/A2 to
main-text figures (RO-6) — figure budget. Any SVG change. Any new digit.

## Acceptance (paste exact tails)

1. The full local paper-check command list from record 11 §3 (with its env vars), all passing,
   plus `python3 -B docs/paper/build/check_markdown.py docs/paper/draft-v2-skeleton.md` rc 0.
2. `R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -B -m unittest tests.test_paper_first_use_ledger
   tests.test_paper_terms_lint tests.test_paper_replay_fence tests.test_paper_round7_artifacts
   tests.test_paper_build tests.test_select_outcome_branches tests.test_check_paper_replay_fence
   tests.test_paper_rendering tests.test_paper_comparison_placements
   tests.test_paper_successor_migration` — OK.
3. `scripts/check_paper_replay_fence.py --corpus-root /Users/edr/code/JouleWise` — same COMPARED /
   MISMATCHES 0 census as before your edits (record the before and after lines).
4. Abstract word count ≤ 250 (state the count). `git diff --stat` and, in the report, a table
   mapping every finding id above to DONE / DONE-WITH-PIN-EDIT (name the pin) / NOT DONE (why).

Report: claude-codex-report/v1, genre implementation, envelope under 8000 bytes, then the table and
the exact tails. If an item cannot be done without breaking a pin the census says must not move,
skip it, mark NOT DONE with the pin named, and continue with everything else.
