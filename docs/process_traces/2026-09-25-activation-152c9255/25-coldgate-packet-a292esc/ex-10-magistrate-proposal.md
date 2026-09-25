# Magistrate proposal: A292 escalation (Opus 5.5, activation 152c9255)

**Trigger.** Two consecutive rounds failed with the same signature: domain-operand mutants surviving because no witness exercises them. The first sweep left 19 domain-operand survivors. Fix round 1 hand-added witnesses and closed 16. Three remain (M033, M045, M050), because the added witnesses fail an earlier key-set check and never reach the deleted type operand. A third round of hand-written rows is the anti-pattern.

**P1 (structural cure): generated one-fault witnesses.**
- The harness gains a deterministic generator. For every validated record type (capture window, score row, and the nested `energy_bound_terms_j`) and for every predicate in E2's domain definition, it starts from a *valid* record and violates exactly one predicate while keeping every other predicate satisfied. That includes the key-set-preserving wrong container: a list holding exactly the valid key names, and a mapping whose values have the wrong type.
- The expected refusal code is derived from E2's check order, never from the reducer.
- Acceptance is mechanical: the M8 sweep over `joulewise/scored_reduce.py` reports zero non-equivalent survivors, with each equivalent mutant listed with its proof.
- The generator lives in the harness (tests plus oracle), written by the harness seat; the implementation seat never reads it.

**P2 (ruling gap, typed disposition for extreme values).** E2 admits finite nonnegative integers of any size. Two crashes follow: `10**1000` J reaches `math.fsum` and raises OverflowError, and `10**5000` breaks canonical-JSON hashing, raising ValueError. Both are untyped.
- Proposal, sized to the instrument (the sensible-gates directive): every energy field (`gross_j` and each term of `energy_bound_terms_j`) must satisfy 0 ≤ v ≤ 1e12 J, else `window_domain`.
- Reason: one block on this machine is order 10²–10⁴ J, so 1e12 J is eight or more orders of magnitude above anything physical. The bound refuses only impossible values, never a real measurement.
- Integer anchors are subject to the same bound. This amends E2's domain text and is labelled as an amendment.
- Aggregate overflow then becomes impossible, since at most (number of windows) × 1e12 ≪ 1.8e308. Lane A292-AGGREGATE-OVERFLOW-01 closes with this ruling.
