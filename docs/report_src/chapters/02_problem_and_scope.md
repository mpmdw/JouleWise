# Problem and scope

<!-- jw:contract-sources
docs/contracts/capstone_scope.md
-->

NOTE (RPT-001 slice): the D-052 frozen headline claim and stop-lines are
authoritative in `docs/contracts/capstone_scope.md`. The transclusion
mechanism ({{jw:include-section ...}}) is not yet implemented in the
assembler; until it is, this chapter references the contract rather than
mirroring its exact wording, to avoid drift.

Scope is stack-bound: every measurement names its exact hardware unit,
runtime, model artifact, quantization, and measurement boundary. Explicit
non-claims: no cross-stack efficiency ranking, no model-size scaling law, no
tokenizer-blind per-token comparison, no representativeness beyond the exact
physical unit measured.

The minimum-viable fallback story is the instrument itself: even if the
production measurement matrix yields no interesting contrast, a validated,
reproducible energy-measurement harness with honest uncertainty reporting is
the deliverable. Split inference remains a gated stretch extension, not part
of the graded scope.
