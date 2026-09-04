# Paper seat E — pedagogy-lens refuter (Sol xhigh refuter + Claude wrapper adjudication), 2026-09-03

Verdict: FALSIFIED on the pedagogy lens — numbers and tests are clean; the why-chain and one term collision are not. Lines refer to `docs/paper/draft-v2-skeleton.md` at `0857bd59`.

| Sev | Lines | Defect | Fix shape |
|---|---|---|---|
| BLOCKER | 942-947, 964; SVG 39/77 | Prose says "alignment decides whether a support crosses a phase edge"; the worked example is a 0.121 s phase vs ~121 ms records. In the SVG the upper phase is 185 px wide and the lower 310 px (records 190 px), so the three-overlap row shows a MUCH LONGER phase, not the same phase shifted — a professor concludes "length, not alignment". The text never states the mechanism (three overlaps need the phase to cover one whole intervening record, i.e. a record shorter than the phase, plus alignment); the IQRs (952-955) are printed but never used. | Lower row: same-width phase, middle record drawn narrower and labelled "record widths vary"; one prose sentence linking record-width spread to the three-overlap cases. |
| BLOCKER | 933, 966 vs 307, 764 | "not resolvable" is bolded and glossed at 764 as "the estimate does not clear the cell floor"; the added sentences reuse the same words for "fewer than three overlapping records". Same term, two mechanisms, no bridge. | Distinguish the record-count refusal from §4's floor refusal. |
| should-fix | 948, 968, 975, 974 | "retained", "diagnostic-era", "non-claim-bearing", "prospective demonstration" first-used without a gloss. | In-line plain glosses. |
| should-fix | 968-970 | Population unidentified (which configuration, prompt-length class, window); registry says `stack=1.5B`, "historical a10". | Registry-backed identification in plain words; retired family name may not appear. |
| should-fix | 919, 921, 932, 937, 951, 1000 | Synonym drift: sampling record / sampler record / record support / interval averages / three-record rule / three-record minimum / lexicon "support interval". | One name per object; equate once. |
| should-fix | 950-951 | "Across all 406 sampler records in that run" — the artifact population is the retained `power_trace.csv` of R03P. | "in that run's retained power trace". |
| nit | 955-958 | tiling claim is qualitative (artifact rule: within 0.000001 s; largest gap 0.0000004 s over 100/405 boundaries). | Optionally cite the artifact's tolerance. |
| nit | 933-934, 945 | "insufficient time support" unglossed; "every rectangle is labelled" false for background/frame rects. | "records"; "every drawn mark". |
| info | 145-147 | §1 "overlap"/"three-record minimum" gloss arrives ~780 lines later — pre-existing §1 text, outside this diff; recorded as the Sol refuter's dissent. | none on this branch |

Checks replayed by the wrapper: every number traces (DG-067..077; 406/120.9186/5.9508 and 405/120.9224/5.8949 match `dg071-dg075-statistics.json` exactly; both artifact SHA-256s match); SVG overlap counts computed from coordinates are 2 and 3; figure numbering consistent (fig4 exists); conclusion/not-conclusion sentences present; paper suite `Ran 68 tests ... OK (skipped=3)`; the ledger test is green only because it matches literal alternatives ("not resolvable" ≠ "resolvability"), so the collision is invisible to it.
