# Custody seam (D-173) — magistrate terminal review (apex read)

Read: the public surface of joulewise/paper_custody.py (five typed refs; five Verified* and five Fixture*
result types over one private _CustodyResult; capability mint; _FamilySpec; the closed _ISSUANCE_GATES registry
with the D-165 close-out and claim-evidence gates; _validate_floor_acceptance; open_paper_input overloads and
_open_paper_input_impl), joulewise/paper_rendering.py in full (the _issued_renderer boundary: exact type identity,
capability check on value and evidence, family and production mode, grant validation before any payload access;
five renderers; __all__ = the registry), the function-level footprint of the other modules (dominance_closeout's
validate_d165_paper_sources and closed refusal codes; analysis_manifest_v3, authentication_io, whole_window
additions), the contract narrowing text, and traces 01–16 (two refuter pairs, six fix rounds, six deltas,
one cold gate 21/22/23 with D-173 adopted as amended, astra design spec 11).

Design-level questions. (1) Can a fixture value reach prose by omission? No: renderers accept only the exact
issuing type and refuse fixture siblings before touching the payload; the astra execution refuter (13) drove
25 fixture/renderer pairs and 90 public construction routes to refusal with zero output. (2) Can production
issue without a registered gate? No: null/unknown gate ids refuse (issuance_gate_unregistered), a raising gate
refuses, grant/subject mismatches refuse; the registry is closed and hashed into the receipt digest. (3) Does
the contract state the actual threat model? Yes: the narrowing text is verbatim per gate 23 (ordinary attribute
access to the token; module-private constructors; D-161 ordinary-operator scope), test-pinned. (4) Frozen
bytes: v1 fixture map bytes preserved; supply map v2 adds mode/gate/subjects/source census; nothing issued
changes. (5) Pending, disclosed: the D-173 SCOPE clause (registry rows naming families) is paper-side work; the
production git_blob role lands on the desk day; REFUSAL-CARRIER-01 waits on the readiness cut. (6) Overbuild:
the gate registry is what gate 23 ratified; Opus (14) found none beyond four small AMENDs, cured in round 6.

Bench (this session): tests.test_paper_custody, test_paper_rendering, test_authentication_io,
test_d165_dominance_closeout green after the main merge.

Verdict: LANDABLE (fixture-only, non-issuing; no supplier or publication gate is passed by this merge).
Full-suite replay on the merged head recorded before merge.
