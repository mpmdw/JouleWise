# Sol seat — _v5 model-ladder design (gpt-5.6-sol xhigh, read-only; relayed). Verbatim.

Sol thread `01a04b20-fcb9-77b1-be6e-cdf3fcd8341d` (read-only, xhigh, no edits; working tree clean). Sol's answer verbatim:

## Positions

1. **Design space.** A claim-bearing ladder is not consumable today without code changes. The engine already supports arbitrary Holm families provided `m == len(pvalues)` (`joulewise/analysis_engine/multiplicity.py:19-31,49-78`; `joulewise/analysis_engine/__init__.py:1303-1357`). Thus both fixed-reference and adjacent-pair designs can be represented as \(k-1\) B−A contrasts in one Holm family, \(m=k-1\). Adjacent pairs match "each step resolved or refused"; fixed-reference contrasts do not establish every step.

   The validator refuses either because it requires exactly four condition slots, exactly two decode/prefill contrasts, ten blocks and forty members per contrast, and exactly 80 runs/20 blocks (`joulewise/analysis_manifest_v3.py:2030-2158,2275-2389,2508-2527,2596-2629`). Separate m=1 pair campaigns would run today, but would not be the preregistered ladder family.

   A monotone-trend kind is also refused: `analysis_type` must equal `comparative_contrast`, every estimate must be B−A, and the estimator itself is pairwise (`joulewise/analysis_manifest_v3.py:2128-2158`; `joulewise/analysis_engine/estimators.py:450-512`). Pairwise generalization: 2–3 Sol-days—new generator; generalize `_validate_prospective_analysis_manifest_v3_unchecked`, finalization/semantic projection and `frozen_family_block_strata`; add tests. Trend: 5–7 Sol-days—also change `analysis_engine/inputs.py`, `estimators.py`, dispatch in `__init__.py`, `claims.py`, and artifact validation.

2. **Floors and nights.** Decode-only means five model-specific cells and five floor mints; decode+p256 means ten cell floors, acquired by five existing-style two-arm producer nights. Current floor aggregation itself hard-codes two producers, two cells per producer, and four aggregate cells, so a five-model pinset needs generalization (`joulewise/detection_floor.py:2277-2331,2520-2547`; `scripts/floor_mint_pinsets/schema_v2.json:650-711,938-959`).

   At fixed \(n=10\), each floor night is 100 science + 12 bound + 7 reference = **119 bundles**, plus two calibration observations, about 377–389 minutes (`configs/campaigns/d117_floor_qwen25_1p5b_v3/generate_configs.py:2103-2108,2448-2457`). Each present-format pair night is 80 + 12 + 9 = **101 bundles**, plus two calibrations, about 310 minutes (`configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/generate_configs.py:997-1001,1804-1831`).

   Therefore:

   - Four sizes: 4 floor + 3 pair brackets = **7 nights**, 779 bundles + 14 calibration observations.
   - Five sizes: 5 floor + 4 pair brackets = **9 nights**, 999 bundles + 18 calibration observations.

   Exact reuse of `_v4` floors could reduce incremental nights only if cell identity and admissibility remain exact. D-062 does not justify choosing five merely to fit the calendar; it says near-floor work should be nearer ten than five (`docs/decision_log.md:3316-3344`). V3 pins ten globally and per contrast (`joulewise/analysis_manifest_v3.py:34,2152,2525`). Confirmatory \(n=5\) requires a newly justified and frozen analysis version.

3. **Resolvable workload.** Retained decode rates are approximately 0.376 J/token for 7B and 0.098 J/token for 1.5B (`CLAIMS_STATUS.md:116-117`; `docs/run_reports/2026-07-30-sweep-mechanisms.md:66`). Assuming decode-energy difference scales linearly with parameter gap, the smallest 1B rung gives
   \((0.376-0.098)/5.5=0.0505\) J/token; \(5/0.0505≈99\) tokens. Thus **128-token decode is the mathematical minimum** (~6.5 J); **256 tokens is the defensible choice** (~12.9 J margin), while `_v4`'s 512 is conservative.

   Prefill is poor for adjacent resolution: the observed 7B−1.5B p128 difference is 5.81 J, with p256 projected to 11.62 J (`docs/paper/draft-v1.md:258-272`). Linear scaling predicts only ~2.1 J at p256 for the 1B rung; roughly p606, practically p768/p1024, is needed. Prefer decode-only.

4. **Models.** Local 4-bit MLX artifacts were verified for 0.5B, 1.5B and 7B; 3B and 14B are absent locally and lack repository identity pins. They are acquisition candidates, not contract-ready until mirrored with exact revision/hash under D-016 (`docs/decision_log.md:905-946`). Existing pins cover 1.5B/7B, vocabulary 151,643 (`joulewise/analysis_manifest_v3.py:68-170`). Fourteen-billion 4-bit weights are roughly 7–9 GB, so 128 GB memory is not limiting. Local `tokenizer.json` hashes match for 0.5B/1.5B/7B; the frozen p256 evidence only proves identical IDs for 1.5B/7B (`configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/prefill_prompt_candidate.json:11-20`). Re-run exact-ID hashing for 3B/14B.

5. **Paper gain.** Strongest honest sentence: "Across five preregistered Qwen2.5 4-bit sizes on one fixed decode workload, every adjacent size increase was either floor-clearing and positive or explicitly refused." This extends C5-1.1 into a predeclared pairwise ladder, not a fitted scaling law; it does **not** answer RQ-SHAPE-ENERGY because workload shape is held fixed (`docs/research_question_registry.md:63-69`).

   Impressiveness per night: **(1) inserted-gap fiducial**, because it directly closes the paper's transfer-assumption limitation (`docs/paper/draft-v1.md:292-318`); **(2) one-model 4-bit/8-bit axis**, although quality equivalence becomes a gate; **(3) five-size ladder**, because it costs nine full windows, needs two new artifact pins, and its smallest rungs may refuse.

6. **Plan.** During `_v4`, desk-only: choose adjacent/decode-only; mirror and pin 3B/14B; verify token IDs; generalize manifest and floor-pinset cardinalities; generate synthetic packs; run prospective/finalized validator, engine, refusal, Holm and full-suite gauntlets; freeze \(n=10\), exact bytes and readiness. Perform no measurements while agents are active. Earliest start is the first clean quiet window after `_v4` closes—realistically **Monday night, 2026-09-07**; Sunday 09-06 only if `_v4` is already fully closed.

## Disagreements

A global trend test is less suitable than adjacent contrasts: it can declare monotonicity while concealing an unresolved rung, contrary to the requested stepwise labeling.

## Open questions

The lead must rule on `_v4` floor reuse, 256 versus retained 512 decode, and whether nine full windows are acceptable.

## Recommendation

Freeze an adjacent, decode-only, Holm \(m=4\), \(n=10\) design—but execute it only if exact `_v4` reuse reduces the incremental schedule to the available week; otherwise run the inserted-gap fiducial first.

BRIDGE_REPORT_V1
{"status":"DISCUSSION","summary":"Read-only design ruling: current v3 requires code generalization for a ladder; adjacent decode-only Holm m=4 at n=10 is the strongest ladder design, but a full five-size pack costs nine calibrated nights.","pathspec":[],"verification":["Inspected generator, validator, engine, floor, registry, decision-log, and paper sources","git status --short --branch: clean"],"flags":["no_edits"]}
