# GAMMA-CLAIM-RENDERER-01 seat landing report

Base: `96a9446f` on `feat/2026-09-04-gamma-claim-renderer`. This is a fixture-only implementation of magistrate ruling R2; it issues no measurement value and makes no paper claim.

## Contract landed

- Production claim artifacts now emit `joulewise.claim_verdicts.v2`. Each contrast has the required closed sibling `claim_side_bound = {role, source_term_name, value_j, composition_rule, single_count_discipline_rule_id}`. `value_j` must exactly equal the sole `E_clock_anchor_shift_bound_j` term. The v1 schema and its exact contrast key set remain accepted only on the read path.
- The renderer accepts pinned source bytes only: the v2 content ID, G2-a record SHA-256, and prompt-pin SHA-256 must match caller-held authority pins. It validates the complete v2 artifact (including its embedded floor bytes), the G2-a closed rule/outcome, the prompt-pin join, exact decode/prefill IDs, four ordered arm-floor records, claim/Holm consistency, and the preserved prefill overlap census.
- The sole fixture is explicitly `fixture_only=true`, `measurement_values=false`, and `claim_bearing=false`; its supported/floor-failure/direction-failure/absent-verdict/count-2/count-4 variants are synthetic.

## Field → row → rendered string

| Authenticated field or derivation | Registry row | Renderer output |
|---|---|---|
| `floor.active_floor_j + claim_side_bound.value_j`; `abs(estimator.estimate) - (F+B)` | DS-28 | `F+B = <S_decode_joint_J> J; signed clearance = <C_decode_sizing_signed_clearance_J> J` |
| decode `claim_side_bound.value_j` | DS-29 | exact numeric `B_decode_claim_J` |
| `abs(estimator.estimate) > floor.active_floor_j`, cross-checked to reasons | DS-30 | `passes — \|estimate\| > armwise cell floor` or `does not pass — \|estimate\| ≤ armwise cell floor` |
| fully composed endpoints, registered positive direction | DS-31 | `passes — the fully composed interval lies wholly above zero` or `does not pass — the fully composed interval does not lie wholly above zero` |
| decode `claim_evaluation`, both gates, Holm and readiness | DS-32 plus seven registered placements | ruled `supported` / `not supported` text; absent verdict is byte-exact `not evaluated — required token-generation verdict absent` |
| selected prefill `floor.active_floor_j`, equal to ordered A/B arm maximum | DS-33 | exact numeric `F_claim_prefill_p[PREFILL_LENGTH]_armwise_max_J` |
| selected prefill `estimator.estimate` | PG-01 | exact signed numeric value |
| selected prefill `decision_interval.{lower,upper}` | PG-02 | `<lower>, <upper>` |
| selected prefill `F+B`; signed sizing clearance | PG-04 | `F+B = <S_prefill...joint_J> J; signed clearance = <C_prefill...sizing_signed_clearance_J> J` |
| selected prefill `claim_side_bound.value_j` | PG-05 | exact numeric `B_prefill...claim_J` |
| selected prefill magnitude/floor relation | PG-06 | same ruled floor-gate phrases as DS-30 |
| selected prefill fully composed interval | PG-07 | same ruled direction-gate phrases as DS-31 |
| selected prefill `claim_evaluation` plus authenticated overlap census | PG-08 plus seven registered placements | ruled verdict text; absent verdict is byte-exact `not evaluated — required prompt-processing verdict absent` |

D-166 remains distinct: count below 3 renders `not supported — not resolvable (issued reasons: not_resolvable_sample_count)`; count 3–4 renders byte-exact `not supported — below the pre-registered count floor of 5 (reducer result remained resolvable at observed overlap count <n>)`.

## Red → green and mutation evidence

Acceptance was run red before the module existed:

```text
ModuleNotFoundError: No module named 'joulewise.results_fill_gamma'
Ran 1 test in 0.000s
FAILED (errors=1)
```

The final symbolic-2048 table test mutates every field it exposes in the requested classes—46 digest/content-identity occurrences, 41 census occurrences, and 53 outcome/status occurrences—and every mutation returns `STOP_FILL`. It also covers wrong/duplicate identity, v2 bound mismatch, equivalence, both gate failures, both exact Refusal sentences, D-166 counts 2 and 4, repeated-placement byte identity, and pseudotoken elimination.

## Test tails

```text
python3 -m unittest tests.test_analysis_engine_artifact
..
Ran 2 tests in 0.119s
OK
```

```text
python3 -m unittest tests.test_results_fill_gamma
.
Ran 1 test in 0.217s
OK
```

```text
R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -m unittest tests.test_paper_first_use_ledger tests.test_paper_terms_lint
.............
Ran 13 tests in 2.768s
OK
```

The user preflight forbade the whole suite, so it was not run. Read-only inspection found one required integration follow-up outside this seat's write scope: `tests/test_analysis_integration.py:1578-1582` pins the former v1 producer's claim-verdict ID and rendered SHA-256. The mandated v2 sibling changes both bytes, so those two expectations require a lead-approved refresh before the broader suite can be green. No commit was created.
