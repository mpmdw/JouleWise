# Contract-lens refutation — S2 reported energy, HEAD `720b166c` (`git diff e241e0b7 HEAD`)

**Executed this session:** `python3 -m unittest tests.test_paper_reported_energy tests.test_d117_floor_qwen25_1p5b_plan tests.test_paper_rendering` (45 OK) and `tests.test_paper_custody` (29 OK); `registration_sha256` recomputed = `d89011db…`/`88e0f5c1…`, matching `paper_reported_energy.md` and the plan-test pins.

## (1) Clause-by-clause installation — all eight accounted for

1–7 are **installed and enforced**, not merely described. Verified: no post-collection filter, `refuse_reported_mean` and the 50-row/`strict_valid` refusal (`paper_reported_energy.py:230,243`, tested `test_49_member_mean_refuses`); `expected_n: 50`; 20/10/10 units (`:92`); `V = 0.2²s_r²/10 + 0.8²s_b²/10`, ν=9, t=2.262157162798205 (`:20,250-251`), pooled form killed by `test_…not_pooled`; B = Σ kind averages with exact-key absent-kind refusal (`:238,252-253`); floor beside, `attribution_floor_composed: False` and endpoints invariant under a 1000 J floor (`:267`); prediction term excluded by name (`:18`, two mutations killed); new `phase_ratio_estimand` sibling with the B8 `validate_ratio_estimand` untouched and rejecting it; fail-closed denominators refusing the ratio only; registrations in **both** generators bound to `cell_id`, pinned by `tests/test_d117_floor_qwen25_1p5b_plan.py:1632-1681`; X5 rows RETIRED_FALLBACK in both tables with no placement restored; D-179 faithful to 1–7.

**F1 (should-fix).** Clause 8's named follow-up **BRIDGE-BASELINE-ANCHORS-01 exists nowhere** outside the synthesis — not in `TASK_QUEUE.md`, not in any doc. This is the ruled-not-installed pattern; magistrate-owned, not S2's, but it leaves the ruling incomplete.

## (2) The new contract as a closed specification

Not yet replicable from the text alone.

**F2 (should-fix) `paper_reported_energy.md:52` vs `paper_reported_energy.py:248`.** The doc states the estimator as `m = 0.2 mean(r) + 0.8 mean(b)`; the code computes `statistics.fmean(energy)`. Algebraically identical (I checked: both 42.5 on the fixture) but **not bitwise guaranteed**, and `_validate_projection` compares exact digests (`:275`). A replicator following the contract can fail recomputation. Name `fmean` over the ordered 50 as canonical, note the equivalence.

**F3 (should-fix) `paper_reported_energy.md:88-92`.** "All four surfaces" is never mapped to the bundle fields. The real surfaces are `workload_provenance.prompt.realized_token_count`, `tokenize.end_metadata.prompt_tokens`, `prefill.start_metadata.prompt_tokens`, `workload_observed.token_count-output_token_count` (`bundle_read.py:1037-1041`) — and the middle two are **tuples** there, while the normalized schema demands one int (`paper_reported_energy.py:194-196`). The collapse rule is unspecified.

**F4 (should-fix).** Refusal *codes* are not closed. D-173 uses `paper_custody_*`; the new owner raises bare `ValueError` with prose, and the contract enumerates only `runtime_observed_denominator_invalid` (`:101`). Nothing pins the energy-cell refusal vocabulary.

**F5 (should-fix) — contradicts `paper_supply_custody.md:206-208` and `paper_comparison_rendering.md:65-67`.** Both say the **only** pending production role is `…qwen3-1p7b.v5`; the landing adds `production.reported_energy_parents.qwen3-8b.v5` to `supply_map.json` and updates neither sentence. That supply-map addition is also outside every clause of the synthesis.

**F6 (should-fix).** X5 census divergence: `paper_supply_custody.md:455-458` now reads "five fields defined in paper_reported_energy.md … RETIRED_FALLBACK", while the duplicate census at `paper_comparison_placements.md:71-74` still reads "exact field names/member joins UNRESOLVED … PROPOSED_STOP_FILL". Two contracts, one census, now disagreeing (S1 lane may own the fix; flag it to integration).

## (3) D-173 custody seam — clean

No path takes evidence outside `open_paper_input`. `_synthetic_projection` is reachable only from `_validate_fixture_documents` (`paper_custody.py:1298`) and the `mode == "test_fixture_non_issuing"` branch at `:1471`; `output_type` is the fixture type there, so a fixture can never present as production. **`_ISSUANCE_GATES` (`:655-657`) holds only `d165_closeout`** — the reported-energy production gate is absent and `_run_issuance_gate` refuses `paper_custody_issuance_gate_unregistered`. `supply_map.json` production entries live in `pending_roles` with **no digests** and all `roles` are `test_fixture_non_issuing`; `pending_roles` grants no lookup. Receipt churn across five families is correctly explained by the two `common`-census owners changing.

**F7 (should-fix) `paper_rendering.py:42`.** The renderer was rewired to `reported_energy_projection`, a key **only the fixture branch adds**. Its declared type `VerifiedReportedEnergyParents` can therefore never carry it, so the body is unreachable, has no positive test (only the refusal assertion at `test_paper_reported_energy.py:283`), and would fail with an uncaught `StopIteration` from `_field` (`:36-37`) rather than a closed refusal.

**F8 (nit) `tests/test_paper_custody.py:955-971`.** `test_production_git_blob_coverage` hardcodes the 1p7b role; the new 8b pending entry is unasserted.

## (4) Registration-before-spec fence — described, only half mechanical

**F9 (should-fix).** Three artefacts exist: the `registration_ordering` string, the digest in both generators/contract, and `assertFalse(SPEC_REL.exists())` (`plan test:1680`) — a self-breaking tripwire. But `registration_sha256` is a pure function of code constants and binds no time; the actual "predates" proof is prose ("the lead must establish…", `paper_reported_energy.md:26-29`). Specify the mechanical check: the commit adding the spec blob must be a descendant of the commit introducing `registration_sha256`, and the spec's digest must equal `registration_sha256(model)`.

## (5) New defects

**F10 (nit) `paper_reported_energy.py:198`.** Decode cells require the four *prompt* surfaces to agree and `prompt > 0`, though decode's denominator is `output`. Stricter than clause 5; a prompt-surface disagreement will silently refuse a valid decode ratio.

**F11 (nit) `:257`.** `n_bundles` is the literal `50`, not `cell["expected_n"]`; clause 1 says `[N_bundles]` renders `expected_n` (equal today by validation).

**F12 (nit).** D-179 skips D-176–D-178, which exist nowhere; and the index row (`decision_log.md:222`) carries none of the substance neighbouring rows do.

## Verdict

**LAND-WITH-FIXES** — clauses 1–7 are faithfully installed and the custody seam holds; fix F5/F6 (cross-contract contradictions the landing created), F2/F3/F4 (contract replicability), F7 (renderer rewired to an unreachable key), F9 (ordering fence), and register F1 before the ruling is closed.
