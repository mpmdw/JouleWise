# Block 5 independent-recompute coverage

Date: 2026-11-06. Scope: the sealed Block 5 registration and analysis plan, the L9 cold rulings, and the two programs proposed by DLE-1/DLE-2. This audit used synthetic fixtures only. “Compute” means independently derives a value rather than copying L9; “compare” means an explicit union-key comparison row, not merely a step-11 leaf exemption.

## Authority and census method

The registered numeric spine is finite and explicit: reported cells (§4), floors (§5), dominance (§6), contrasts and descriptive magnitudes (§7), disclosures and sensitivities (§8), and the print table (§9) [PLAN 201-276, 282-339, 339-492, 492-695]. The exclusion input is the analysed attempt's sealed `exclusions.json`; nothing else may exclude after collection [PLAN 77-91]. The registration classifies exclusions into PACK/CODE/MODEL identity, CALIBRATION, NEG8, INSTRUMENT, CLOCK_SYSTEMATIC, MEMBER_VALIDITY, PHYSICS_IN_SPAN, ROSTER, and RECORDS [REG 3650-3658], with validity, physics, window, and roster rules expanded in §§6.3-6.7 [REG 3682-4237].

The later rulings are part of the census: J5 says contrast floors include each floor window's drift allowance and identifies every consumer [RULING 117-127]; J6 fixes `B_max`, `b_sens(W)`, all re-extracted floor forms, and the sensitivity contrast path [RULING 140-160]; J8 fixes leave-one-out pairing when the partner contrast lost the quad [RULING 181-193]; X1 forbids any excluded reference from remaining in the deciding screen and requires the pre-number tripwire [ERRATUM 13-38]. J2/J3 add the reference-config and kept-member membership tripwires [RULING 53-91], while J7 fixes archived-ledger authentication [RULING 161-179]. D-078 supplies the exact edge-envelope/metrology discipline used by §4/§5; the plan registers the exact corner maximum rather than the old approximation [PLAN 233-256].

Line locations below are the post-fix tree.

## Coverage matrix: estimands, quantities, families, and sensitivities

| Registered item (all emitted scalar subfields included) | Authority | Independent recompute | Comparator | Result / gap |
|---|---|---|---|---|
| Kept attempt, member/unit selection; repeat/quad ids; `n_r`, `n_b`, kept quads | PLAN 68-91, 499-503 | selection and declared-count checks at `scripts/independent_recompute_b5.py:2636-2660,2710-2741`; full exclusions re-derivation at 533-652 and 2630 | exact kept-unit and block-union rows at `scripts/compare_b5_recompute.py:2237-2297`; re-derivation status at 3468 | **Covered.** Comparator checks both selection and re-derived-exclusion agreement. |
| Per-member overlap energy and anchor-shift envelope (`point/lower/upper/max_abs_delta`) under `b_op` | PLAN 221-247; D-078 rule as PLAN 233-256 | overlap/envelope at `scripts/independent_recompute_b5.py:213-242`; per-member phase values at 1063-1072 | selected member energies at comparator 1847-1886; envelope-derived aggregate fields through reported/floor rows | **Covered for every quantity consumed by an estimand.** Raw envelope endpoints are diagnostic inputs, not registered printed outputs. |
| Reported-cell mean; `s_r`, `s_b`, variance, df, t, `h`, three bound-kind averages, `B`, lower/upper; bundle count | PLAN 224-247, 273-276 | `reported_estimate` and `make_reported`, recompute 1040-1119 | projection values and internals, comparator 2704-2732 | **Covered.** |
| Reported-cell per-token energy and realized token denominator | PLAN 248-254 | recompute 1097-1119 | comparator 2726 and disclosure/fill coverage rules 3637-3644 | **Covered.** |
| Attribution floor: maximum/minimum member edge bound and attaining member | PLAN 255-257 | recompute 1091-1119 | numeric maximum/minimum at comparator 2724-2726; attaining id is provenance-routed/exempted | **Numeric quantity covered**; attaining identity is not arithmetic. |
| p42 non-resolution and refusal code | PLAN 289-293, 637-638 | expected-unresolvable status at recompute 2652-2655 | exact status/code consistency at comparator 2736 and 2874-2900 | **Covered.** |
| D-054 absolute and comparative point floor: max deviation, prediction, sample SD, unguarded floor | PLAN 295-304 | recompute 1153-1164 | comparator floor families 1940-2044 | **Covered.** |
| Small-sample guard `g(n)` and guarded floor | PLAN 302-304 | recompute 1173-1210 | comparator 1940-2044 | **Covered.** |
| Exact 2^n corner widening, operative unguarded/guarded floors | PLAN 306-309 | recompute 1166-1210 | comparator 1940-2044 | **Covered.** |
| D-124 comparative shared/local width and common-mode numerator | PLAN 310-317 | recompute 1129-1149 and 1417-1456 | comparator floor components and closeout ratios 1940-2044, 2050-2180 | **Covered.** |
| Gross NEG-8 allowance, half-allowance floor composition, source, seven registered bound terms, survivor and corpus counts | PLAN 233-244, 601-622 | recompute 659-674, 674-689, 767-935 | comparator 3266-3284; coverage map 3723-3733 | **Covered.** Internal idle-subtracted companion terms are not claim quantities. |
| J5 floor composition: guarded + floor-window allowance; absolute/comparative/minted gate and armwise maximum | RULING 117-127; PLAN 319-337 | recompute 1417-1456 | comparator 1940-2044, 2223-2228 and coverage 3658-3690 | **Covered.** |
| Dominance: eight `R`, four `R_cm`, numerators, denominators, n, pass tests, failed set, branch A/B | PLAN 339-361 | recompute 2672-2699 | comparator 2050-2180 | **Covered.** |
| GAMMA paired `d_k`, `dbar`, `s_d`, SE, t*, p, metrology interval, deterministic `D` and its terms, decision interval | PLAN 362-414 | recompute 1248-1266, 1396-1410, 2708-2741 | comparator 2206-2239 | **Covered.** |
| Holm m=2 adjusted p, reject word, raw-p order | PLAN 404-414 | recompute 1268-1278 and 2736-2741 | comparator 2229-2237, 2375 | **Covered.** |
| Claim outcome, direction, floor-clearance, ceiling/readiness | PLAN 415-478 | recompute 1281-1315, 2736-2744 | threshold-aware word comparisons at comparator 2235-2260, 2368-2375 | **Covered.** |
| J8 leave-one-quad-out: each estimate, p/Holm p, intervals, floor word, influence triggers, ceiling and magnitude movement | RULING 181-193; PLAN 430-478 | recompute 1305-1360 | comparator 2268-2357 and 3212-3235 | **Covered.** |
| Descriptive phase-energy ratio and interval | PLAN 479-486 | recompute 1362-1383 | comparator 3197-3205 | **Covered.** |
| Descriptive per-token contrast and metrology/decision intervals | PLAN 487-490 | recompute 1362-1383 | comparator 3206-3211 | **Covered.** |
| Cross-window `G`, `h_G`, `F`, `h_F`, delta and agreement word | PLAN 573-578 | recompute 1385-1394, 2745-2748 | comparator 3150-3157 | **Covered.** |
| Decision interval versus floor | PLAN 580-584 | recompute 1281-1285, 2743-2744 | comparator step-11 binding and contrast rows 2239-2254 | **Covered.** |
| Load-correlated exclusion sensitivity: restored unit counts and same cell estimator (`mean`, `h`, `B`, endpoints, n); GAMMA paired estimator (`n`, mean, SD, SE, t, interval) | PLAN 526-540 | recompute 2749-2782 | **new:** comparator 3042-3063, 3144-3190, 3212-3225; coverage bindings 3669-3672, 3703-3710, 3736-3739 | **Gap closed.** Previously explicitly exempted as “not compared”; synthetic fault test now proves both cell and contrast values disagree. |
| Battery-assist cell pair and counts; GAMMA no-assist contrast and interval | PLAN 541-565 | recompute 2783-2796 | comparator 3042-3052, 3158-3196 | **Covered.** |
| J6 `B_max`, terminal sequence T, attaining sequence, each `b_op`, `b_sens=max`, widened reported cells/floors/D/outcomes and equality-to-primary invariants | RULING 140-160 | recompute 2233-2335 | comparator 2677-2916 | **Covered.** |
| Whole-machine §8.2 per member: meter gross/baseline/delta, battery term/count, rail and machine delta, rho, sample/window counts; model order statistics and central band | PLAN 646-694 | recompute 1467-1868 and 2042-2229 | comparator 3365-3444 | **Covered when the registered meter record is supplied; missing record is an explicit disagreement.** |
| Excluded-screen-reference alternative allowance sensitivity | X1 plus registered blind post-plan ruling, audit inventory | recompute 2464-2507 | comparator 3000-3024 (relation words and values) | **Covered.** |
| Scaled NEG-8 allowance sensitivity and BETA-inclusive removed-session floor | registered blind rulings listed by care audit 138-140 | recompute 2338-2463 and 2525-2624 | comparator 2990-3030 and dedicated disclosure comparisons 3000-3030 | **Covered as non-primary sensitivity/diagnostic.** |
| Single-step reconstruction diagnostic | registered blind ruling listed by care audit 138-140; explicitly diagnostic | recompute 1870-2010 | comparator routes diagnostic leaves only where L9 emits them | **Not a registered estimand; no release gap.** |

## Exclusion matrix

The correct unit of coverage is the catalog effect, not hand-copying dozens of code names. The registration makes the sealed catalog plus pure exclusion function authoritative [REG 1381-1410, 3575-3658]; the plan forbids analysis-time exclusions [PLAN 77-91]. The recompute independently rebuilds the roster/spans/catalog result and compares the decision-bearing keys (`reasons`, kept/dropped units, counts, claim usability) at `scripts/independent_recompute_b5.py:533-757`. The comparator requires exact status `agrees` at `scripts/compare_b5_recompute.py:3468`. Thus every code in these registered families is covered:

| Family/effect | Registered scope | Coverage and residual |
|---|---|---|
| PACK_IDENTITY, CODE_IDENTITY, MODEL_IDENTITY | window (one underivable model case is member) | Full exclusion re-derivation + exact status. |
| CALIBRATION, CLOCK_SYSTEMATIC | window | Full re-derivation; bracket numeric values independently checked (`b_op`, J6). |
| NEG8 | window, plus disclosed reference/corpus losses and GAMMA midpoint pack reason | Full re-derivation; screen, allowance, seven terms, counts independently compared. |
| INSTRUMENT, MEMBER_VALIDITY, PHYSICS_IN_SPAN | member | Full re-derivation and exact kept units; three load-correlated codes additionally covered by the restored sensitivity above. |
| ROSTER | ignored bundle/member/window depending code | Full re-derivation; ignored-bundle labels that remove no unit are structural, not estimands. |
| RECORDS / malformed-flag conservative codes | disclose/member/window depending code | Full re-derivation; disclosure-only prose and hashes are custody checks, not quantities. |
| X1 excluded reference, J2 config mismatch, J3 kept member outside writer membership, GAMMA lost midpoint | pre-number stop / pack reason | Recomputation flags and stop set at recompute 57-66 and window checks 706-757; comparator compares exclusion agreement and expected selection. |
| Minimum five units per stratum | cell/window and estimator availability | recompute 1071-1079, 1173-1181, 2715-2720; exact p42/below-minimum words in comparator 2736, 2874-2900. |

## Remaining gaps (explicitly not release arithmetic)

1. The recompute does not independently reproduce disclosure-only monitor CPU, hazard samples, battery-temperature stage series, host busy CPU, attempt-history prose, or catalog-family text. Those are registered disclosures but not estimands; the comparator coverage map names them as structural/provenance leaves rather than pretending they were independently derived (`scripts/compare_b5_recompute.py:3493-3523,3740-3836`). They remain dependent on authenticated L9/harvest records. This is a **disclosure-integrity gap**, not a numeric agreement gap, and should be retained in the DLE-1 risk statement.
2. A load-sensitivity producer refusal code remains uncovered: the independent recompute emits structural flags rather than L9's internal refusal vocabulary (`scripts/compare_b5_recompute.py:3736-3740`). A refusal means the registered descriptive line has no value; it never gates or replaces a primary value [PLAN 526-540]. The comparator now compares its status and every value when computable.
3. Input judgments remain hash-trusted rather than independently re-derived: attempt/member selection, stored anchors `m/s`, calibration fits, and harvest verdict inputs. This is exactly the lean-path boundary identified by the care audit [CARE 141-143, 198-200], and is why digest census and later heavy audit remain necessary.

## Change and synthetic proof

The sole decision-quantity gap found was the load-correlated sensitivity. `independent_recompute_b5.py` already computed it, but the comparator deliberately exempted its entire numeric subtree. The comparator now adds it to the union-key expected-check table, compares every registered numeric field and restored count, and binds every step-11 copy to an agreeing row. The recompute also gives the GAMMA restored estimator an explicit independently derived status. The producer-shaped synthetic fixture includes one restored ALPHA cell and one restored GAMMA contrast; its mutation test changes one value in each and requires `reported_cell_j` and `contrast_j` disagreement.
