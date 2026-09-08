# Successor paper comparison rendering contract — S6 increment 1

Status: typed design and executable **SYNTHETIC, NON-ISSUING** scenarios only.
This does not activate comparison branches, fill the paper, or extend issuance.
The current selector accepts `METHODS_DIAGNOSTIC`; the A/B/REFUSAL instructions
in `docs/paper/fill-rehearsal/branch-selection.md` describe a historical surface,
not active groups. Neither that selector nor the skeleton is changed here.

## Authority and unresolved bindings

Owning sources: [registry](../paper/results-fill-registry.md), especially
floor-cell branches, DS-25–DS-33, PG-01–PG-08, OB-01 and OR-01;
[prospective protocol](../paper/protocol/prospective-comparison-protocol.md)
P.3 and its direction rule; and [D-173](paper_supply_custody.md).
D-166's exhausted-ladder split remains binding. D-174's retired submission
placements are not reinstated by this contract.

**S1 dependency:** actual section/table/paragraph anchors, occurrence counts,
placement census, characterization-prefix wording, and successor token names
where absent are UNBOUND. Historical Table 3, Abstract, Sections 4/7/10 and
DS-32/PG-08 are semantic references, not permission to restore those sites.
**S3 dependency:** quantity meaning, units, precision, normalization, source-field
mapping, and interval/clearance display vocabulary are UNBOUND until supplied
by S3. Existing mathematical gates are preserved; synthetic joule values below
are illustrative, not an S3 quantity ruling. The executable fixtures use
logical slots and symbolic outcomes, never professor-facing prose.
An UNBOUND field cannot be defaulted, guessed, or used for issuance.

## Typed input boundary

Eventual empirical suppliers MUST call `joulewise.paper_custody.open_paper_input`
with the family-specific reference allowed by D-173, consume its frozen verified
result and subject-specific grants, and preserve provenance. No dictionary,
fixture, cached prevalidation, or synthetic status flag establishes authority.
Missing supplier coverage requires a separately scoped adoption; this contract
adds no family, grant, production gate, or capability constructor.

The following are semantic records, not new public custody types:

| Input | Required typed members and invariants |
|---|---|
| Binding | S1 placement census and S3 quantity contract, each bound authority reference or explicit UNBOUND |
| Evidence state | tagged union `verified(value, provenance)` / `unavailable` / `invalid`; absence is never an issued refusal |
| FloorCell | model, window, phase (`decode`/`prefill`), component (`absolute`/`comparative`), identity/prompt binding; both validated component records; tagged `exact`, `no_exact_floor`, or `terminal_refusal`; operative floor and separately labelled point diagnostics, each with S3 binding; governed reason for either non-exact branch |
| Comparison | phase, model-pair/window/workload identity, preregistered direction, signed estimate, measurement interval endpoints, decision interval endpoints, claim floor, claim-side bound, branch-explicit clearance or shortfall, magnitude and direction outcomes, two-member Holm family, canonical authenticated verdict |
| PrefillSelection | authenticated G2-a selection and matching prompt pin; selected length; exhausted-ladder flag; minimum overlapping-record count and reducer result |
| RatioDisposition | complete authenticated close-out: A, B or issued refusal; full required independent and comparative shared-error census; failed component identities for B; reason and affected subjects for refusal |
| Stop | one stage (`before comparison` / `at close-out`), affected model/window/verdict identities, issued reason and governing verified source; explicit unavailable/invalid alternatives carry no issued reason |
| Characterization | collected result / verified not-collected / unavailable / invalid; independent of ratio and comparison dispositions |
| RenderRequest | all above, canonical repeated-verdict bindings, abstract after all substitutions, optional governing precedence reference; no caller-selected scientific conclusion |

Floor absence/nullness does not prove `no_exact_floor`. Unknown terminal codes,
malformed metadata, or an unvalidated component reject the transaction.
Point-only diagnostics must never be labelled the published claim floor.

## Logical placement and token contract

| Logical slot | Required content; physical placement remains S1 UNBOUND |
|---|---|
| floor(model, phase, component) | exact operative floor or evidenced branch reason; diagnostics separately labelled; existing `TERMINAL_REFUSAL_REASON_*`, `NO_EXACT_FLOOR_REASON_*`, `AVAILABLE_DIAGNOSTIC_CLAUSE_*`, `POINT_DIAGNOSTIC_CLAUSE_*` are registry references |
| decode comparison | all Comparison quantities; DS-25–DS-31 references; `[FILL:DS-32]` canonical verdict |
| prefill comparison | corresponding PG-01–PG-08 quantities and DS-33 identity; `[PREFILL_LENGTH]` remains unbound without G2-a; missing numeric token family remains UNBOUND |
| repeated model verdict | `[FILL:DS-32]` and `[FILL:PG-08]`: one canonical conservative string per authenticated verdict, repeated byte-for-byte at every S1-authorized occurrence, including surviving table slots |
| ratio | A only for complete evaluable census with every required ratio >=2; B only for complete evaluable census with at least one <2; `[FILL:OB-01]` lists every failing component; neither implies a model direction |
| refusal | `[FILL:OR-01]`: exactly one governed stage and its reason and affected identities, or explicit source unavailable/invalid with no invented issued reason |
| characterization | not-collected prefix only where the characterization row is discussed; collected suppresses it; missing evidence is not not-collected; independent of A/B/refusal |

Magnitude passage is strictly `abs(estimate) > floor`; equality fails. Direction
requires both intervals wholly on the preregistered side of zero and Holm
passage. Sign disagreement, zero contact and Holm failure forbid a directional
claim even after magnitude passage. F+B is planning-only, not an acceptance
threshold. The renderer projects authenticated outcomes; the synthetic gate
oracle checks consistency and does not become the production analysis engine.

D-166: exhausted ladder selects 4096. Count <3 preserves reducer refusal
`not_resolvable_sample_count`. Counts 3 or 4 preserve the resolvable reducer
result AND the distinct pre-registration refusal `below the pre-registered
count floor of 5`. Never merge these branches or reduce Holm's family from two.
An independently licensed decode result remains represented with either branch.

OR-01 has two ordered stages: before comparison, then at close-out. A verified
production-window non-admission can support the former; a verified close-out
refusal (including zero denominator) can support the latter. Missing/invalid
inputs support only unavailable/invalid fallback, not empirical failure.
Two simultaneously supplied stages require an explicit governing precedence
binding; this increment leaves that binding UNBOUND and rejects such fixtures.
It does not invent automatic earliest-stage-wins semantics. Contradictory
reasons or outcomes reject even if a stage order is known. Unaffected verified
model results survive a scoped refusal or unavailable close-out input.

## Transaction and scenario acceptance

Validate the complete input/identity census, evidence states, dependencies,
branch consistency, all repeated strings, all tokens and the fully substituted
Abstract (<=250 words) before any output publication. Stage the entire artifact
privately, validate again, then publish atomically. Unexpected failure at any
point must leave no newly emitted paper prose and preserve existing output.
Never stream an early section while later fields remain unchecked. A complete
artifact explicitly containing an unaffected decode result and a scoped refusal
is successful selective reporting; a prefix left by a failed write is not.

`tests.test_paper_comparison_contract` is the executable non-issuing matrix.
Its symbolic outputs explicitly carry `SYNTHETIC_NON_ISSUING`, S1/S3 UNBOUND,
and empty paper prose. Fixture-local dataclasses cannot obtain capabilities;
no production custody or renderer module is imported or called.

| Scenario family | Expected symbolic result |
|---|---|
| A and B crossed with each independently valid decode/prefill outcome | ratio retained independently; directional, magnitude-failed, sign-failed and Holm-failed model outcomes retained exactly |
| Verified production-window non-admission | before-comparison stop with exact synthetic reason and affected identity |
| Verified close-out refusal | at-close-out stop; unaffected model results retained |
| Unavailable or invalid evidence | explicit fallback, no issued reason; surviving comparison retained |
| Prefill-only count refusal (<3; 3; 4) | distinct D-166 branch and reducer status; decode survives; Holm size two |
| Conflicting stages or repeated verdict strings | invalid fixture, no output |
| Strict floor equality; sign disagreement; Holm failure | no directional claim |
| Final Abstract 250 / 251 words | valid / invalid |
| Late failure after staging | no committed output or paper prose |

Counterfactual outputs must be rejected: A forcing a directional model claim;
missing evidence becoming an issued refusal; loss of unaffected decode;
conflicting repeated verdicts; a 251-word Abstract; partial emission after late
failure. Tests compare explicit expected records and deliberately corrupt each
of these properties, rather than accepting arbitrary fixture prose.

## Separately scoped issuing implementation requirements

1. Obtain S1's authoritative placement census and resolve S3 quantity semantics;
   bind every currently UNBOUND field without restoring retired placements by
   inference. Resolve multi-stage precedence through the lead if needed.
2. Complete supplier adoption through D-173 `open_paper_input`; add reviewed
   coverage for floors, comparisons, G2-a, characterization and negative evidence
   where current issuing projections/grants are insufficient. Never promote
   fixtures or register a production gate as part of this increment.
3. Implement the typed aggregate adapter, exact identity/census and evidence
   checks, floor branches, both comparison token families and canonical verdict
   projection. Preserve independent ratio and model outcomes and D-166 splits.
4. Implement S1's placement/token census, characterization prefix, OR-01,
   conservative unavailable fallback, unaffected-result survival and exact
   repeated strings; reject unknown or unresolved markers.
5. Implement transactional publication with late-failure and existing-output
   preservation checks; enforce the final Abstract word guard with the approved
   paper tokenizer. Fixture whitespace words are only synthetic boundary cases.
6. Run issuing-boundary rejection tests, production-capability and supplier
   integration tests, scenario counterfactuals and lead-owned final verification
   under a new scope before any issuing renderer or paper fill is claimed done.
