# Magistrate ruling on report 49 (F+B v2 fixture review), 2026-09-05

**Question (report 49):** may the explicit fixture review update the producer-pin and producer-set
constants in `tests/test_mint_floor_artifact_generalized.py` solely because the PR #292 v2 single-count
discipline object changed the synthetic component bytes, although the constants' comment says they move
with a D-079 issuance and the r6 acceptance identity and both digests are unchanged?

**Ruling: YES, option 1, under five conditions.** The D-079 comment records one cause of movement, not the
only one. Each producer plan embeds its component artifact SHA-256, so a reviewed change to the component
contract necessarily moves the producer self-hashes; refusing that would freeze the fixture to v1 bytes
that two refuters (files 44 and 45) already found NOT REFUTED as superseded. The pins stay independent
because they are re-derived with the fixture oracles, never with the mint code under test.

Conditions:

1. **Byte-diff justification per constant.** For every golden constant that moves (component, producer,
   producer-set, CLI component, phase-0 base floor bytes, default-only v2 golden output, or any other),
   the report records a diff of the old fixture bytes against the new ones showing that the ONLY change is
   the v1→v2 single-count discipline object (and hashes that embed it). Any constant whose diff shows
   anything else is NOT re-pinned; the seat stops with NEEDS_RULING naming that constant.
2. **Acceptance unchanged, asserted in code.** The regression asserts that every producer plan's
   `calibration_acceptance` fields are byte-identical before and after the re-pin
   (acceptance_id d079_calibration_acceptance_v2_n17_r6, artifact_sha256 0227bca3…, derivation_sha256
   18d09aa9…).
3. **Oracle discipline.** Component and CLI component pins are re-derived with `_fixture_artifact_sha256`
   (indented JSON plus terminal newline); producer and producer-set pins with `_fixture_canonical_sha256`
   (compact canonical JSON). Values observed from production diagnostics are inputs to check against,
   never the recorded pins.
4. **Comment amended, not replaced.** The constants' comment keeps the D-079 sentence and adds: pins also
   move with a reviewed component-contract change; first instance 2026-09-05, PR #292 v2 single-count
   discipline object, which constants moved and why.
5. **Counterfactual regression.** One regression that fails when the fixture carries the v1 discipline
   bytes and passes with v2, named for the production call site
   `joulewise/arm_readiness_evidence.py::_derive_mint_trust → _run_suite`.

Acceptance: the full mint test module (83 tests), both relocation tests
(`tests/test_arm_readiness_dry_run` … `survives_repository_relocation`, `tests/test_launch_window` …
`accepts_relocation_and_refuses_content_change`) and `tests/test_single_count_discipline_matrix` pass,
tails pasted. Then the PR takes a fresh non-author delta before rows 9/11/12.
