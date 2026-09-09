# Cold-gate packet: paper S3 — what quantity does claim_side_bound_j denote, and by which licensed join?

Assembled mechanically by the interactive magistrate at 2026-09-08 ~12:10 PDT from the brief-writer scout (trace 90 §Ruling packet — S3), verbatim below. Rule-11 trigger: a design-bearing contract decision that would issue claim-bearing numbers. Checkout = paper integration head e241e0b7 (S1/S6 contracts present: docs/contracts/paper_comparison_placements.md, docs/contracts/paper_comparison_rendering.md, docs/contracts/paper_supply_custody.md; registry docs/paper/results-fill-registry.md; crosswalk exhibit at docs/process_traces/2026-09-08-handoff-redo/75-*).

## Ruling packet — S3

**Question:** What exact paper quantity does `claim_side_bound_j` denote, how is it derived from the estimator’s deterministic terms, and which prospectively registered source-cell join licenses each contrast?

**Evidence:**

- `joulewise/analysis_engine/claim_side_bound.py:1`: the wire is expressly a non-issuing scaffold.
- `joulewise/analysis_engine/claim_side_bound.py:48`: source cells must equal explicit manifest registration; missing registration refuses.
- `joulewise/analysis_engine/claim_side_bound.py:57`: candidate arithmetic symmetrically expands the metrology-aware interval.
- `joulewise/analysis_engine/estimators.py:141`: paired estimates distinguish stochastic/deterministic layers and expose deterministic total plus decision interval.
- `docs/contracts/paper_supply_custody.md:302`: candidate validation is not an adopted producer contract; the CE gate remains unregistered.

**Options and failures avoided:**

| Option | Decision required | Failure avoided |
|---|---|---|
| A — Adopt the candidate scalar wire | Prove the scalar equals the relevant existing deterministic total, with exact units, composition, and ordered cell join | A sidecar whose arithmetic passes but whose quantity is unrelated to the actual claim decision |
| B — Adopt a richer component/endpoints wire | Specify named contributions or endpoint treatment and derive displayed totals from them | Loss of necessary provenance or unjustified symmetric widening |
| C — Defer the side-bound display | Keep affected claim placements stopped pending a complete contract | Shipping plausible but unlicensed numbers |

**Recommendation:** Gate A on an explicit estimator-to-sidecar derivation. If equality and provenance cannot be demonstrated, choose B. C is the safe interim disposition; candidate validation alone cannot decide between A and B.

**Cold-gate decision fields:**

- Adopted quantity/formula and authoritative producer:
- Relationship to stochastic interval and already-applied deterministic widening:
- Exact contrast → ordered source-cell registration authority:
- Serialization/version and arithmetic tolerances:
- Required floor/reader/manifest/acceptance bindings:
- Mutation cases proving no omitted term, double widening, or guessed join:
- Approved implementation scope and clause-to-test map:

**Blocked work:** S3 producer, CE gate registration, and claim-bearing S6 output. No frozen manifest/schema is modified by this packet.

## Charge
Fill every cold-gate decision field above with a ruling (A, B, or C, or a combination), each grounded in a file:line you read at this checkout (joulewise/analysis_engine/claim_side_bound.py, joulewise/analysis_engine/estimators.py, docs/contracts/paper_supply_custody.md §candidate validation, the S6 rendering contract's claim-floor rows, the protocol docs/paper/protocol/prospective-comparison-protocol.md). State the failure-mode test for the ruled option: can a displayed side-bound ever differ from the quantity the claim decision actually used, or be widened twice? Write NOT EXECUTED for anything you cannot verify. Write the ruling to ./coldgate-packet/10-coldgate-fable-ruling.md (under 900 words, numbered decisions matching the field list, one-line verdict last).
