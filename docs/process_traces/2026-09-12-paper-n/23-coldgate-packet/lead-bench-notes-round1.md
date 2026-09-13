Lead bench read of 482a0cc4 (full draft diff, 864 lines) — items for round 2:
1. Abstract no longer names the sampler; name `powermetrics` once (words available: 238/250).
2. §3 end: "The **cell floor** is the registered operational resolution guard … after the publication safeguards" conflates the old resolution-bound (before safeguards) with the cell floor (final gate value after them). Cure: "The **cell floor** is the final gate value for assigned-energy differences in a cell after the publication safeguards of Section P.3 of the [protocol]."
3. Figure A4 caption (main text ~508) still says "enumerate the cases in Table 4"; Table 4 now lives in Appendix A.3.10 → "Table 4 in Appendix A.3.10".
4. Figure 2 caption: "the vertical axis is fitted edge excursion in milliseconds (the axis label)" → "the vertical axis, labelled 'excursion (milliseconds)', is the signed fitted lag: fitted edge time minus command time".
5. Abstract "(Section 3's R ≥ 2 test)" uses the symbol R before any definition → "(the twofold test of Section 3)".
6. §1 first mention of the prospective comparison protocol lost its link (link now only at §3 end) → restore the link at first mention if the lint allows two links, else keep.
7. Lexicon L7: docs/paper/round7/built-terms-lexicon.md rows for moved terms (seat flag R1) + the protected tuple in tests/test_paper_first_use_ledger.py.
8. F7 (fact lens): §4 worked line first sentence + checker regex scripts/check_paper_replay_fence.py:174 — provenance mislabel; do it with the regex updated and tests/test_check_paper_replay_fence.py adjusted if it pins the sentence.
Verified at the bench: Ask 6 arithmetic (2×38.724/136.5 = 57 % "more than half"; /281.5 = 28 % "roughly a quarter") holds; E5 hedged; A.3.5 σ-floor sentence matches Table A3 (41.08 W vs 42.55 W predicted ≈ 1.5 W scatter, "of order a watt"); DG-027 literal retained; the two headline strings intact (select_outcome --check-rendered PASS).
