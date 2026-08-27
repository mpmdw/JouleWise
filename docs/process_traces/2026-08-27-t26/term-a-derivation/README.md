# TERM A / TERM B desk derivation and self-consistency proof

Ordered by the T26 paper-goal magistrate ruling, Addendum 2 item 26(i): TERM A is
derived at the desk from the emitted per-cell repeatability statistics, and the
derivation is PROVEN by reproducing the emitted diagnostic byte-for-value in every
cell where the code does emit it — "a Sol xhigh + blind Fable check each".

Two seats ran BLIND to each other on the same question.

- `01-sol-xhigh-seat.md` — the Sol xhigh seat, with its executed proof script and output.
- `02-blind-fable-seat.md` — the blind Fable seat, with its independently written proof.

## What the two seats agreed on, without contact

- **The TERM A identity**, per component record (`cells[].absolute`, `cells[].comparative`):

      A_unguarded = max( max_abs_residual_j (absolute) | max_abs_delta_j (comparative),
                         prediction_component_j )
      A_guarded   = guard_factor * A_unguarded

- **The conditionality that forces a desk derivation.** The `point_floor_diagnostic`
  container is attached only when the dominance predicate is already true, and the
  validator forbids it when the predicate is false. A cell where the claim FAILS
  therefore carries no emitted TERM A, so the falsifier cannot be read off an artifact.
- **The proof passes.** Both seats reproduced every emitted diagnostic they could find
  exactly, and both confirmed container presence matches the recomputed predicate.
- **The component-to-cell aggregation is specified NOWHERE** in code or contract.
- **TERM B is ambiguous** between the code's literal predicate comparand (not emitted)
  and the emitted corner-widened floor, and the drift-widened `floor_gate_j` is a third
  quantity that tests a different proposition because its drift allowance is not a
  timing term.

## Where they differed

The Sol seat located more emitting artifacts than the blind seat and so ran a larger
proof; the blind seat additionally found that a 2026-07-24 diagnostic trace carries
fields named `point_unguarded_floor_j` / `point_guarded_floor_j` that are NOT point-only
values — the generating script serialises them after corner widening. Nothing in that
trace can serve as a second proof source, and its labels would mislead anyone citing
them as scatter floors. That is a standalone finding for the magistrate.

## Open, and blocking the registry rows

1. The aggregation operator for a per-cell TERM A.
2. Which quantity TERM B denotes for the comparison.

Both are NEEDS-RULING. The eight registry rows in
`docs/paper/results-fill-registry.md` are `STOP_FILL` until they are ruled.
