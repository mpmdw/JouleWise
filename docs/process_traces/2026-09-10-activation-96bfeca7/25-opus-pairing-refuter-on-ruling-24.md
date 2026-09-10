# Opus contract-lens refuter paired with cold-gate ruling 24 — filed by the lead from the agent's final message (2026-09-10 ~05:40 PDT)

Summary (verbatim): every operative clause that decides admit/refuse is TRUE of the code; the exact coverage edge (12 ULP admits, 13 ULP refuses at six readings) reproduces. No blockers. Three should_fix: A2's "a missing sample refuses under every policy" is FALSE in the schema's policy space (sustained_window_s = 210 s / subwindow_s = 0.001 parses; 210,001 readings -> term 0.10014 s >= one sample; physically unreachable, prose-only); A1's "a positive elapsed interval" understates the code (non-bool INTEGER elapsed_ns; a float 30e9 refuses); A2's release predicate is not replicable because "duration-weighted idle-power mean" is unbuilt and its weights are clipped overlaps. Plus W1 "Strict reduction" unbuilt (one occurrence in the document). Nits: C4 "worst case" overclaims (Sterbenz: the subtraction is exact; the rounding is in the endpoints, code charges 2x); C3 NaN duration credited nothing, not the whole interval; C2 file-level refusals omitted; W3 and/or ambiguity. Design ruling (i) UPHELD with the condition that the last A2 sentence be scoped to the window it was computed for; recorded dissent-worthy point: only option (ii) buys a policy-independent statement.

| id | severity | sentence | verdict |
|---|---|---|---|
| C5 | should_fix | "a missing sample refuses under every policy" | FALSE as a universal (210 s / 1 ms policy parses) |
| C1 | should_fix | "a positive elapsed interval" | understates: non-bool int elapsed_ns |
| W2 | should_fix | "duration-weighted idle-power mean" | weights are clipped overlaps; unbuilt at first use |
| W1 | should_fix | "Strict reduction" | unbuilt term of art (single occurrence) |
| C4 | nit | "the worst case of the rounding in the subtractions" | attribution wrong; 2x conservative |
| C3 | nit | "no positive duration is credited its whole capture interval" | NaN credited nothing |
| C2 | nit | file-level refusals omitted | incomplete |
| W3 | nit | "and ... refuses outright" | ambiguous conjunction |

Writing-standard lens: A2 builds ten of ten terms; A1 leaks "Strict reduction". Replicable: yes for the completion test; no for the full release predicate (W2); mostly for the admission predicates (C1, C2).

Lead disposition: all eight applied as fix round 4 on the sweep branch (prose only; code unchanged per the ruling's option i). The magistrate does not overrule the cold ruling; the pairing refuter's amendments are applied under it. Final text goes to a third-model (Astra xhigh) clause-by-clause delta check before the terminal review.
