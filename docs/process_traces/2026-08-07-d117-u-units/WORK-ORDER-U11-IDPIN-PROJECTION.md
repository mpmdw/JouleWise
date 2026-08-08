# Work order U11 — arm-time identity pin projection (registered 2026-08-07)

**Registered by the magistrate under MAGISTRATE-DISPOSITIONS.md §U5-U7
amendment 4, which ordered this registration BEFORE U5 runs.** The apex
U5-U7 examination (FABLE-EXAM-U5U7.md) found this gap; the disposition
adopted it as a new work order. This file is the charter; it creates the
owner the amendment said was missing.

## The night-killer this closes

Nothing charters the tool that computes the projected
`runtime_identity_sha256`, `model_artifact_sha256`, and
`config_set_sha256` that are frozen into a pack's pinset at ARM TIME.
A wrong projection means clean night data that is PERMANENTLY
UNMINTABLE, because pins cannot be re-declared after collection. Ranked
second of the three highest night-loss risks (worst consequence: an
irrecoverable floor night).

## Scope

Charter and implement the projection path that computes, at arm time,
the three identity pins a window's pinset freezes:

1. **Derivation, not entry:** each pin is DERIVED by the tool from the
   artifact it names (runtime environment, model artifact bytes, config
   set bytes) — never typed by the operator. Same rule class as the
   trust closure (D117-POSTCOLLECTION-TRUST-01): caller-supplied
   provenance strings are not trusted.
2. **Pre-flight equality proof:** at arm time the tool must demonstrate
   that the projected pins EQUAL the values the morning mint will
   rederive — by invoking the same derivation functions the mint/
   extractor use (shared module, not a reimplementation). A projection
   the mint cannot reproduce refuses the arm.
3. **Receipt:** the projection emits a record (inputs, derived values,
   derivation code identity) custodied with the pack, so a morning
   mismatch is diagnosable to its cause (environment drifted vs
   projection bug) rather than a bare refusal.
4. **Refusal vectors:** unreadable/missing artifact, dirty runtime
   environment vs the plan's declared identity, projection/mint
   derivation divergence, pinset already frozen with different values.

## Dependencies and sequencing

- Blocks: ARMING of any U5-U7 pack (packs may GENERATE now; no pack may
  ARM until its identity pins came from this tool).
- Depends on: U3 pinset v2 (landed, PR #112) for the pinset field
  definitions; D117-POSTCOLLECTION-TRUST-01 for the shared-derivation
  rule it must match.
- Sibling rule: R1 (no second-paper work touches the mint/pinset/
  detection_floor file set until U10 closes) does not block this order —
  it IS capstone-critical-path work, but its mint-side edits must ride
  with or after D117-POSTCOLLECTION-TRUST-01's landing, not conflict
  with it.

## Acceptance

- The three pins for a synthetic pack are derived, receipt-emitted, and
  proven equal to the mint-side rederivation in a regression.
- A deliberately perturbed artifact (one byte) flips the projection and
  the arm refuses with the named vector.
- No operator-typed identity string anywhere on the arm path.
