# FCM-01 rounds 5-10 — full D-124-chain amendment notes (moved from the decision log for site-capsule budget)

These are the verbatim round-by-round amendment notes. The decision log carries a compact summary pointing here; nothing is lost.

### D-124 amendment — 2026-08-11: round-5 structural registered input

Round 5 narrows the registered surface to a frozen block-input record produced
by the module-private registered builder. The builder receives authenticated
bundle-derived contrast evidence, evaluates the `(0.0, 0.0)` contrast itself
once, evaluates both enumerated shift grids, and records each positive
shift-`0.0` position; the registered estimator takes the zero point only from
those recorded positions and accepts no caller-supplied zero designator. The
legacy keyword surface remains available for the byte-frozen independent
oracle, with its admission and arithmetic unchanged, but every result from that
surface is unregistered and the extraction gate refuses it for a registered
cell. Both surfaces route through one arithmetic core, so the oracle continues
to bar the arithmetic used by registered estimates. The registered zero-point
rule is now
`zero_point_is_carried_structurally_by_the_registered_builder_as_the_shift_zero_index_never_supplied_or_matched_by_value_and_direct_keyword_inputs_are_unregistered`;
the resulting parameter hash is
`973c9bfc5a4d5984b5db6eeba5d054613d86a0bd69ae1f8a56c5fad5d7a453b7`,
and the outgoing round-4 hash joins the three earlier superseded registrations.

The claims-with-assumptions form remains: **over inputs constructed by the
registered builder from authenticated bundle evidence, the emitted width
bounds the exact admissible width outward, up to the disclosed member-envelope
pad and the disclosed zero-point discrepancy term, under the documented
single-sourcing assumptions for the bracket bounds in the audit table above.**
Python privacy is conventional rather than enforced: underscore names and the
frozen dataclass do not cryptographically prevent deliberate fabrication, so a
construction-site inventory test pins the intended one-builder/one-production-
caller discipline. Evidence faithfulness upstream of the builder remains an
assumption, not a result of this structural repair.


