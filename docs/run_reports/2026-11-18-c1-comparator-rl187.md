# C1 comparator RL-187 follow-up

18 November 2026 · Tier 2 · synthetic output evidence

The lead authorized push and CI after RL-187. The ruling is pinned at
`9fffb60141b3dbf6cbff8504dd415e4a806689df`. Section 2.2 supplies the
authoritative mapping from the output-family ledger to the registered
comparison classes. No comparator PR or remote branch existed at intake.
Remote main had advanced from the branch base without a change to any
comparator path. [RL-187 §2](https://github.com/mpmdw/JouleWise/blob/9fffb60141b3dbf6cbff8504dd415e4a806689df/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L21595-L21679)

| Finding | Regression | Result |
|---|---|---|
| A continuous leaf must select one of nine ruled classes | `test_registered_bars_and_mutations` checks 19 raw locations against the nine families. `test_unbound_numeric_refuses_by_logical_name` checks missing and unknown class names. | PASS |
| An asymmetric wire needs a correctly rounded cross-check | `test_lossless_wire_refuses_malformed_representations` checks the reduced rational and integer-nanosecond shapes. The numeric mutation test changes the lossless operand with the left float fixed and changes each left float by one ULP. | PASS |
| Equal printed closure remainders can both be wrong | `test_closure_remainders_are_checked_on_each_side` checks the own-row formula, the zero-whole null branch and exact `closes`. | PASS |
| The AUC exception must bind exactly one value plus the registered marker | `test_auc_registered_mutation_vector` checks both required sides, malformed markers, a legitimate value change, the engine fold count and duplicate selector. `test_auc_null_has_bound_reason` checks the sibling reason. | PASS |
| A sentence can drift while its numerical values stay within bars | `test_sentence_figures_and_each_exact_string_substitution` checks half-even rounding, signed zero, the small-p literal and one substitution for each of count, decimal and p. | PASS |

`configs/analysis/v4/c1_comparator_bars.json` holds the RL-187 families,
closure tolerances and AUC disposition. The two wire schemas bind the exact
locations of the AUC and its fold population. The fold counts and identities
come from the engine-side census. The marker supplies the recompute-side
presence and shape.

The N1 cross-wire equality observes the correctly rounded binary64 value.
Two distinct rationals can round to the same value. An independently bound
exact witness or a matching exact recompute alias can detect a change inside
that rounding interval. The synthetic alias regression exercises that case.

Both Python 3.13.18 and 3.14.6 passed all 15 focused tests. The canonical
sharder discovered and passed both comparator modules. The frozen fixture
replayed the supplied diagnostics, and regenerating the [142-case synthetic
index](2026-11-18-c1-comparator-synthetic-index.jsonl) binds the revised comparator
and the RL-187 bars digest. The engine wire and the ten frozen sources are
outside this changeset.

```sh
PYTHONPATH=tests:. python3.13 -B -m unittest \
  v4_release.test_claim_output_mutations v4_release.test_rl187_comparator -v
PYTHONPATH=tests:. python3.13 -B -m v4_release.test_claim_output_mutations --evidence-index \
  | cmp docs/run_reports/2026-11-18-c1-comparator-synthetic-index.jsonl -
```

## NEEDS_SPEC

The integration and series owners supply the accepted producer and release
pins, the actual full/prefix synthetic pairs and run index, and the valid
captured eligible/no-S control per RL-187 §2.5. The adapter owner binds the
B7 and RL-149 §4 pointers, the release-wire sentence templates and the
metadata AUC reason list and fold census. The next step is a pinned
producer-to-comparator run against those bindings, followed by Opus cold
review for the lead's row 13 decision.
