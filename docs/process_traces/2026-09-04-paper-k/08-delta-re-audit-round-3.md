```json
{"schema":"claude-codex-report/v1","genre":"review","status":"findings","completion":"complete","summary":"NOT CLEAN: Discussion A loses its model-pair antecedent.","workspace":{"base_requested":"1dcf45bf","base_mode":"exact","head_start":"1dcf45bf52ccfae9f615666f2469c275ef8095e0","head_end":"1dcf45bf52ccfae9f615666f2469c275ef8095e0","upstream_end":"1dcf45bf52ccfae9f615666f2469c275ef8095e0","branch":"feat/2026-09-04-paper-k"},"pathspec":["docs/process_traces/2026-09-04-paper-k/08-delta-re-audit-round-3.md"],"unowned_dirty":[],"verdict":{"result":"NOT CLEAN","findings":[{"id":"R3-F1","severity":"should_fix","location":"docs/paper/draft-v2-skeleton.md:1174","title":"Orphaned verdict referent"}]},"verification":[{"id":"V1","kind":"test","cmd":"R7F_CORPUS_ROOT=/Users/edr/code/JouleWise PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_first_use_ledger","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["OK"]},"expected":{"exit_code":0,"tail_regex":"OK$"}},{"id":"V2","kind":"lint","cmd":"R7F_CORPUS_ROOT=/Users/edr/code/JouleWise PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_terms_lint","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["OK"]},"expected":{"exit_code":0,"tail_regex":"OK$"}},{"id":"V3","kind":"test","cmd":"R7F_CORPUS_ROOT=/Users/edr/code/JouleWise PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_select_outcome_branches","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["OK"]},"expected":{"exit_code":0,"tail_regex":"OK$"}}],"flags":[]}
```

## Findings

**R3-F1 — should_fix.** Draft 1174: “Independently of the ratio disposition, its authenticated token-generation verdict is [FILL:DS-32] and its authenticated prompt-processing verdict is [FILL:PG-08].” F3 deleted the preceding Qwen3-pair antecedent. Selected A never shows B's intact antecedent.

New sentence: “Independently of the ratio disposition, the fixed Qwen3-8B-versus-Qwen3-1.7B comparison's authenticated token-generation verdict is [FILL:DS-32] and its authenticated prompt-processing verdict is [FILL:PG-08].” Lead applies this sentence and obtains a delta check.

Cure ledger (current draft lines; IDs from 05/06): faithful or better factual cures; no additional first-use defect found beyond R3-F1.

| Prior finding | New text and disposition |
|---|---|
| 05 BL-1 | 831: “degrees of freedom, with two-sided \(p=1.29\times10^{-6}\).” 839–840 now pairs and orders that same value against 0.041. Correct rounding; recomputation below. |
| 05 BL-2 / 06 F5 | 854–857 replaces the orphaned alias with “formed from the repeat standard error already defined for this gross phase-energy path”. Actual first use at 1246–1247: “For this path, the **total standard error** equals the modeled repeat standard error, with no additional stochastic metrology variance.” Ledger 1898 follows it. |
| 05 BL-3 / 06 F2 | 29/35/41: “JouleWise assigns energy to each part as average power times overlap duration; moving the dividing time reallocates energy without changing the request total.” Next sentence builds pulses, domain and division of “each largest bound by its recorded-time value”. A/B use completed tense; Refusal says “would recalculate”/“divide”. B names its nonzero operand; complete bounds match detection_floor.py:861–915. |
| 05 BL-3 continued | 60–66 defines allocation by interval share: “The **timing envelope** is the range of assigned energies over the registered timing domain, conditional on the **held-average reconstruction**, which holds each record at its reported average.” Conclusions 1418/1424/1430 add “phase energy—average power times overlap duration” and repeat the held-average gloss. Ledger adds three rows. |
| 05 SF-1 | 846–849 identifies the sheet's stipulated 0.2-J metrology SE: “That composition example is not a campaign input.” 1270–1275 limits zero metrology to the gross phase path and calls the sheet “an arithmetic check of the composition, not a campaign input.” Matches sheet and builder. |
| 05 SF-2 | 105–108: inserted-gap definition ends “is registered as future diagnostic work; this paper did not run it.” Proposed meaning preserved; consistent with 1205 and 1328–1329. |
| 05 SF-3 | Registry 226–227 and four comparative rows 243/251/259/267 disclose “SUPPLIER_PENDING: producer emits .v1 until the D-165 relabel lands” (note adds “the”). Producer confirms .v1. |
| 05 SF-4 | 75–77: “the eight records lying wholly inside contribute 8 J, and the two records the window only partly covers contribute between 0 and 1 J each.” Rebuild: 1 J/record; 8+[0,1]+[0,1]=[8,10] J. Separately, 10×(0.9±0.02)=[8.8,9.2] J. |
| 05 N-1 | Selector Abstract counts: A 243/250, B 244/250, Refusal 218/250 (comments/labels removed). |
| 05 N-2 | Ledger 1847 now says “calibration data used to build a comparator floor”, matching first use at 293–296. |
| 05 N-3 | test_paper_terms_lint.py:163 replaces exact 131 with `self.assertGreaterEqual(draft.count("[FILL:"), 1)`. Census separately verifies 131. |
| 05 N-4 | Registry 886/895 restores both column anchors: “under `Sizing sum F+B; signed clearance`”. |
| 06 F1 | 41/910/1190/1430 require a “verified failed production-window record bound to the affected model and window”; absent/invalid sources select “the methods/diagnostics fallback”. Each says “Independently authenticated, unaffected model-comparison verdicts remain reportable.” Registry 926 forbids invented failures/reasons, retains zero-denominator refusals and DS-32/PG-08. Selected Refusal retains both Table 3 verdict slots. |
| 06 F3 | 1174: “At the observed sample sizes, the registered perturbation calculations at least doubled every required component's point-only bound; this result does not establish how additional repeats would change those ratios.” Exact proposed cure of permanent dominance; neighboring R3-F1 remains. |
| 06 F4 | Caption 925 defines an “operational resolution guard for assigned-energy differences” and “F+B—floor plus deterministic widening—as a non-gating planning diagnostic, neither necessary nor sufficient for acceptance.” SVG 89–91 matches, retains separate gates, and forbids interval-versus-sum comparison. XML valid. |
| 06 F6 | Redundant sentence deleted; 485–486 retains “The current named bracket screen—the minimum pre/post allowance retained from the calibration corpus—is 9.724 ms.” Fingerprint/padding moves remain undone; 07 explicitly limits the accepted nit to deletion. |

Arithmetic: mean=5 J; squared-deviation sum=17.64 J²; s=1.4; SE=1.4/√10=0.4427188724; t=11.2938487863; ν=9. Two-sided p=I_[9/(9+t²)](4.5,0.5)=1.28854294284577e-6. Independent Simpson integration of (256/(35π))∫₀^atan(3/t) sin⁸θ dθ (10,000 panels) agrees to 14 significant digits. Printed 1.29e-6 and Holm's 0.025/0.05 comparisons are correct.

Invariants: 131 fills; 24 parent-identical outcome-marker lines; three complete groups; nine transfer sentences become three per selected draft. Footer: “Terms inventoried: 264; FAILS: 0.” Tests pass 11+4+4 sequentially. No affirmative physical phase-energy containment, common-time robustness, transfer result, F+B gate, unrestricted largest-false/apparent-effect, or permanent-dominance claim survives. Null/anchor containment remains separately qualified.

Same-signature: rounds 1–2 late-construction and stale-instruction cures remain closed, including the transfer-gating note. R3-F1 adds an orphaned referent. No further orphaned gloss, undeclared synonym, singular/plural mismatch, unused alias, stale ledger vocabulary or synonym drift found.

## Residual risk

Expanded fills need the existing word-cap check. SVG checked as XML/text, without rendering. Supplier v2 remains separately owned. No discovery, live collection, campaign generator, model launcher or out-of-scope write ran. Ruling 43 read from sibling ratification tree.
