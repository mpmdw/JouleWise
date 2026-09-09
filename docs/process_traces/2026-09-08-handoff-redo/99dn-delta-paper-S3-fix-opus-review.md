**Contract-lens delta refutation — S3 fix round, `/Users/edr/code/JouleWise-wt-paper-S3`, HEAD `9760ee53` (`git diff ed44276a HEAD`).** Read-only; nothing written; tree clean after every probe.

Executed: `python3 -m unittest tests.test_claim_side_bound tests.test_paper_custody tests.test_paper_comparison_placements` → **74 OK**; `run_kills.py --s3` → **20/20 killed, 9 distinct guards**, bytes restored; supply-map non-digest diff lines = **0**.

### Per-finding

- **B1 PASS.** `claim_side_bound.py:127-131` routes non-J units through `ratio.validate_ratio_estimand` (`ratio.py:267-284`, exact `RATIO_ESTIMAND_KEYS` + `RATIO_FORMS`); `:134` reads `ratio["form"]`; `:157` copies the object verbatim. `paper_custody.py:792` adds the owner to the census; `test_paper_custody.py:947-948` pins it. Mutation probe: deleting the `validate_ratio_estimand` call **kills** `test_ratio_requires_exact_b8_object`.
- **B2 PARTIAL** — see new findings N-B1/N-S1. The rewritten `test_ratio_in_j_cell` (`tests/test_claim_side_bound.py:156-176`) does use the real schema: `ratio_estimand()` from `test_analysis_manifest`, asserted against `RATIO_ESTIMAND_KEYS` and its owner, with three substitute J-typed row keys and the unit→J relabel. `_UNITS` (`claim_side_bound.py:24`) equals `{r["unit"] for r in estimands}` in **both** `ap_spec_draft_front.v2.json` and `ap_spec_native_mtp_front.v2.json` (verified).
- **S3 PASS.** `:135` keys the join on `(estimand_kind, tuple(sources))`; contract `paper_claim_side_bound.md:88-95` records the companion exemption; positive case `test_companion_estimands_share_ordered_cells` accepts 3 contrasts over `["a","b","a"]` and still refuses a same-kind duplicate.
- **S4 PASS.** All three twins now carry the identical string: `paper_comparison_placements.md:75-76`, `results-fill-registry.md:1207-1208`, `paper_supply_custody.md:452-453`; `test_claim_tables_pin_v2_verdict_resolution_join` pins it in all three.
- **N4 PASS, honest.** `run_kills.py:140` computes `len({old …})` = 9 from data; 11 mutations share `if row != source:`, 2 share the cell-copy guard (20−10−1=9 ✓). Contract `:152-155` states it.
- **N5 PASS.** `deterministic_terms` consistent across `:20,:158,:220`, contract `:54`, registry `:1141`, and tests; the name matches prevailing engine vocabulary (`estimators.py:98`).
- **F1 PASS.** `_decimal` (`:72-76`) wraps both call sites (`:81`, `:89`); `test_extreme_exponents_refuse_through_both_apis` covers both tokens × three fields × both APIs; code enumerated at contract `:133`. Reverting the `except` **kills** it.

### New findings

**N-B1 — BLOCKER — `claim_side_bound.py:24,125`: the unit vocabulary is pinned to the wrong artifact class and refuses the repo's only mandated ratio unit.** `_UNITS` is drawn from AP-spec *estimand* units, but S3 reads a **`joulewise.claim_verdicts.v1`** contrast metric. Bench-verified: `validate_claim_verdicts` imposes *no* unit vocabulary (accepts `J/token`, `J/committed_output_token`, `J/parsecs` alike), while the repo's only enforced ratio-unit rule is `joulewise/analysis_manifest.py:1320-1321` and `:397` — `ratio estimands require 'J/token'` — and `tests/test_analysis_claims.py:1721-1723` builds exactly that verdict shape. So S3 refuses (`unit_mismatch`) a ratio verdict conformant to the only rule that exists. My prior finding 2's claim that `"J/token"` hits only S3 was **wrong**; correct by dated addendum. Cure needs a ruling, not a patch: name the verdict-side unit authority for v3-era ratio contrasts, then pin `_UNITS` to it.

**N-S1 — SHOULD-FIX — `claim_side_bound.py:125`, `tests/test_claim_side_bound.py:166-170`: the membership guard has no behavioural coverage.** Mutation probe removing ` or unit not in _UNITS`: the **full 74-test module passes**. The test's four refusal cases all carry `ratio_estimand=None`, so the B8 branch catches them. Cure: add `unit="J/token"` **with a valid B8 mapping** (asserts `unit_mismatch`), plus a `units_membership` entry in `S3_MUTATIONS` → 21 mutations over 10 guards.

**Process:** N-B1 is the *same signature* as B2 — the unit vocabulary, wrong twice. Standing trigger: consult, not round three.

**VERDICT: LAND-WITH-FIXES** — B1/S3/S4/N4/N5/F1 are cured and mutation-proved; N-S1 is a same-round test addition; N-B1 must go to the magistrate before DS-29 binds.
