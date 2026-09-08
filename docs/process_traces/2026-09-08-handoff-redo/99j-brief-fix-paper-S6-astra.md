WRITE_SCOPE: ["docs/contracts/paper_comparison_rendering.md","tests/test_paper_comparison_contract.py"]

# Fix-round brief — PAPER-S6 contract, Opus contract-review findings (gpt-6-astra, medium)
HEAD = ce4a3ee4 (your landing). Opus review (trace 98 in the canonical checkout; the text is also at the absolute
path /Users/edr/code/JouleWise/docs/process_traces/2026-09-08-handoff-redo/98-ref-paper-S6-opus-contract-review.md —
read it with cat): LAND-WITH-FIXES. Cure F1-F4 (required), F5-F7 (cheap, do them):
F1 `:31-36, :130-133` — name the D-173 supply-map families/roles the issuing renderer will need, each marked
EXISTING (with its exact role name from configs/paper_supply/supply_map.json and docs/contracts/paper_supply_custody.md)
or NEW; state explicitly that G2-a is not a family but the `g2a_selection` input role inside Reported energy, and
that characterization has NO family today (an issuing renderer needs a NEW family, to be adopted under S1/S3).
F2 `:47` — replace the retired "comparative shared-error census" with the D-165 addendum vocabulary
("comparative shared-energy-sign / local-corner components"); grep the file for any other retired D-165 term.
F3 `:47, :64`; tests `:73, :129` — state the D-168 census: exactly eight ordinary/independent ratios and four
comparative R_cm; make the fixture arity match (no hard-coded 2-tuple) or, if the synthetic fixture deliberately
uses a reduced census, say so in the contract AND in the fixture docstring, with the production count stated.
F4 first-use: expand `F+B` (= floor_j + claim_side_bound_j per joulewise/detection_floor.py planning_sizing_expression)
at first use; name the two Holm family members (decode + prefill_p256; D-139 A2 / D-166); gloss "reducer",
"operative floor" vs "point diagnostics", "G2-a", "exhausted ladder" (with the unit of 4096), "clearance or
shortfall", "authenticated" (mechanism), "subject-specific grants", "conservative" at first use; gloss
METHODS_DIAGNOSTIC and the DS/PG/OB/OR row ids on first mention (F7).
F5 use `assertRaisesRegex` with the named rule for each of the six counterfactuals. F6 exercise "contradictory
reasons or outcomes reject even when a stage order is known" independently of the arity guard.
Acceptance = `tests.test_paper_comparison_contract` to a log with rc + `python3
docs/paper/fill-rehearsal/select_outcome_branches.py --check-rendered docs/paper/draft-v2-skeleton.md` rc 0. No
`git commit`; never the repository-wide suite; header < 8192 bytes; genre implementation verdict keys.
