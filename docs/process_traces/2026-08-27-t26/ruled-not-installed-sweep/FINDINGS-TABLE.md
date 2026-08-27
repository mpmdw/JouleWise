# S9 sweep — the census

**460 implementation clauses** enumerated across D-117..D-157 and the
unattributed tail sections of the same era. Baseline: code identical to
`origin/main` `0dd3b6dc`; docs at `f4eac40b`.

## Counts

| Status | Count | Share |
| --- | ---: | ---: |
| **A** — installed and checked at the producer | 300 | 65% |
| **B** — installed, NO producer-side check (the D-157 shape) | 69 | 15% |
| **C** — not installed | 53 | 12% |
| **D** — superseded by a later ruling | 31 | 7% |
| AMBIGUOUS / UNVERIFIED | 7 | 2% |

**One clause in four (122 of 460) is ruled but not enforced where the bytes are
made.** That is the number this sweep was run to produce.

## By group

| Group | Scope | A | B | C | D | Other |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| G1 | D-117 … D-121 | 13 | 5 | 8 | 2 | 1 |
| G2 | D-122 … D-125 | 27 | 4 | 5 | 4 | 0 |
| G3 | D-126 … D-132 | 15 | 5 | 9 | 4 | 1 |
| G4 | D-133, D-134 | 27 | 4 | 0 | 3 | 3 |
| G5 | D-135 … D-141 | 28 | 4 | 6 | 3 | 0 |
| G6 | D-142 … D-149 | 25 | 7 | 4 | 0 | 2 |
| G7 | D-150 … D-157 | 35 | 15 | 14 | 0 | 0 |
| G8 | tail `:8946-9270` (consumption edge, freeze-evidence lifecycle) | 50 | 22 | 3 | 6 | 0 |
| G9 | tail `:9271-9665` (launch binding, recorder authz, T-0 provenance) | 55 | 2 | 1 | 3 | 0 |
| G10 | tail `:9693-10176` (launch-binding F2/F3, successor generator) | 25 | 1 | 3 | 6 | 0 |
| | **Total** | **300** | **69** | **53** | **31** | **7** |

## Reading the shape of the distribution

Three facts sit in these numbers, and none of them is "the project is sloppy."

**1. The best-enforced decisions and the worst sit in the same session.**
D-124's estimator lane is 27-of-31 A, with genuine mint-side refusals
(`joulewise/floor_mint_estimator.py:79-92,257-283`), typed domain refusals, hash
rotation with a six-hash rejection regression, and committed real fixtures.
D-122's gamma pack generator — same transaction, same week — carries three
`"status": "EMPTY"` slots and a prompt marked `TODO(lead)`. The difference is not
care; it is whether a producer-side check got written at the same time as the rule.

**2. The B pile clusters in one place: the consumption edge.** G8 alone accounts
for 22 of the 69 Bs, and **16 of those are individual refusal reason codes** from
the D-078 analysis-manifest registry — `analysis_prospective_schema_invalid`,
`analysis_prospective_unknown_key`, `analysis_prospective_not_frozen`,
`analysis_prospective_identity_mismatch`, `analysis_prospective_plan_tree_mismatch`,
`analysis_prospective_source_hash_mismatch`, `analysis_prospective_unsafe_path`,
`analysis_prospective_member_cover_mismatch`,
`analysis_prospective_block_cover_mismatch`,
`analysis_prospective_contrast_cover_mismatch`,
`analysis_prospective_family_invalid`,
`analysis_prospective_multiplicity_invalid`,
`analysis_prospective_floor_dependency_unresolved`,
`analysis_prospective_unresolved_slot`, `analysis_prospective_internal_error`, and
the placeholder-attachment rejection. Every one is a refusal the consumer will
raise and the producer will never anticipate.

This is not sixteen separate defects. It is **one architectural fact**: the
prospective validator is consumer-only. D-157 R-2 already ruled the cure — the
freeze/readiness path must run the validator and refuse the mint on any finding —
so **W-10 closes this entire block of sixteen at once.** The sweep's contribution
here is the size: it tells you what W-10 is worth.

**3. `D` is not always a clean supersession.** Several clauses were superseded in
practice without the decision log being amended, so a reader consulting the
original entry gets a number the live code disagrees with. Two examples, both
detailed in the per-group files: D-125 ruled that D-117 clause 1 "is AMENDED",
and D-117 still carries the superseded literal at `docs/decision_log.md:7686-7688`;
D-134 clause 3 names `d117_row_registry_v1.json` as "the SOLE row authority",
while production loads v2 (`joulewise/arm_readiness.py:88`) under a magistrate
ruling that was never given a decision-log index row at all.

## Per-group detail

Full clause-by-clause blocks — verbatim clause text, status, `file:line`
evidence, the named producer, and transaction relevance — are in `raw/`:

| File | Group |
| --- | --- |
| `raw/enum-G1.md` … `raw/enum-G7.md` | the numbered decisions, one file per group |
| `raw/enum-G8-sol-report.md`, `raw/enum-G9-sol-report.md`, `raw/enum-G10-sol-report.md` | the tail-section groups |
| `raw/refutation-dossier.md` | the three bench-assembled candidates handed to the refuters |
| `raw/refuter-R1-execution-cand3.md` | execution lens on the collector finding |
| `raw/refuter-R3-contract-cand1-cand2.md` | contract lens on the finalizer route and the `window.env` contradiction |
| `raw/SHARED-BRIEF.md` | the binding brief every enumeration seat ran under |

### A custody note on G8, G9 and G10

Those three seats ran read-only and completed their enumeration, but the sandbox
refused their authorized report write, so their per-clause files do not exist.
What is preserved is each seat's structured final report — counts, the
transaction-relevant B and C clauses verbatim, and its verification record. The
per-clause `file:line` detail behind their **A** verdicts is therefore not
custodied, and any of those three groups' A verdicts should be treated as
unaudited if it ever becomes load-bearing. The B and C findings, which are what
the sweep was run for, came through intact.

This is itself an instance of the thing being swept for: an authorized write
scope that the runner accepted and the sandbox refused, with no check catching
the mismatch at launch.
