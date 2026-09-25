# Magistrate proposal: re-scope PR-0's mutation acceptance (Opus 5.5, activation 152c9255)

**Facts, bench-computed from ex-01.** The sweep ran over the ruled scope (R-6): 1,112 mutants, 271 killed, 1 listed as equivalent, 840 unlisted survivors. By function:

| Survivors | Function |
|---:|---|
| 770 | `artifact.py::validate_claim_verdicts` |
| 15 | `multiplicity.py::_validated_family` |
| 12 | `claims.py::evaluate_claim` |
| 11 | `paper_custody.py::_claim_issuance_gate` |
| 10 | `multiplicity.py::adjust_p_values` |
| 8 | `multiplicity.py::_validated_threshold` |
| 6 | `__init__.py::_resolve_contrast_floor` |
| 5 | `multiplicity.py::benjamini_hochberg_adjust` |
| 2 | `epoch_equivalence_check.py::evaluate_session` |
| 1 | `claims.py::ordered_reason_codes` |

By operator: `if`→False 361, `or`-operand deletion 235, `and`-operand deletion 165, if-expression 25, comparison flips 37, comprehension-if 8. R-4 coverage passes: 0 unlisted uncovered arcs.

**Why R-6 as scoped cannot pass in one round.** `validate_claim_verdicts` is a 2,502-line validator. Almost every surviving mutant disables one rejection branch (`if`→False) or one disjunct of a rejection predicate. A branch-disabling mutant is killed only by an input that should be rejected *by that branch*, meaning one crafted invalid artifact per check. The golden's inputs are valid artifacts plus a handful of invalid ones, so the gap is structural. It is not a missing row or two: this is the third same-signature round.

**What the golden is for (WR-7).** It proves that the CG-4 PR moves no v1 *decision*. The CG-4 PR edits decision code (WR-0 to WR-10: claims, multiplicity, the floor selector, the envelope-set evaluator, issuance). The validator's rejection set matters too, but a validator change that newly *rejects* a valid artifact is already caught by the golden's valid-artifact outcomes. What the golden cannot see is a change that newly *accepts* an invalid one.

**Proposal (A).**
- (i) R-6's zero-unlisted-survivor acceptance applies to the decision functions: `evaluate_claim`, `ordered_reason_codes`, every function in `multiplicity.py` that the claim path calls, `_resolve_contrast_floor`, `_claim_issuance_gate` (with R-4's allowlisted unreachable arcs), and `evaluate_session`. That is about 70 survivors to kill with new golden rows, or to prove equivalent.
- (ii) `validate_claim_verdicts` gets a **generated corruption corpus**. For each checked-in valid artifact, deterministically generate single-field corruptions (drop key, wrong type, NaN, sign flip, off-by-one, swapped enum), about 2,000 cases, seeded, with the generator pinned in the golden. The golden records each case's error list. The sweep reports the validator's kill rate and its unlisted survivors as a **disclosed residual** in the PR body, not as a gate.
- (iii) A follow-up lane registers validator-completeness hardening (VALIDATOR-MUTATION-COMPLETENESS-01), so the residual has an owner.

**(B), for comparison:** land PR-0 with R-4 coverage only, and all mutation survivors disclosed. Rejected: the decision functions are exactly what CG-4 edits, and about 70 survivors there is a real gap.
