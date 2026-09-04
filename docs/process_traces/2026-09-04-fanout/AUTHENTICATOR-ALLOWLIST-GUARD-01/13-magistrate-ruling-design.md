# Magistrate ruling — AUTHENTICATOR-ALLOWLIST-GUARD-01 design (2026-09-04)

After three same-signature occurrences and a three-seat design consult (Sol 09, Opus 10 with the fourth escape, blind Fable 11) adjudicated in packet 12, the packet's recommendations 1–5 are ADOPTED:

1. **Authority root in code:** the closed governed-artifact set is an in-code constant with the explicit eight-family structure (Opus 10's enumeration) — no self-authenticating digest layer, no data-driven proof dispatcher; existing proof paths stay owners.
2. **PASS freeze paths:** exact-key `successor_freeze_receipt_ids` = `{ALPHA,BETA,GAMMA} → "freeze-<4+ digits>"`; bump only `R1_LIFECYCLE_REGISTRY_SCHEMA` to `.v2`; registry ids and the outer row-registry schema unchanged; `_family_member` consumes the same per-profile value.
3. **Totality:** exactly two valid states — both derivation fields are exact three-profile maps deriving the 112 paths, or both are `ED_RESERVED:*` deriving `()`; any mixed state refuses; candidate equality is unconditional (the reserved state accepts only `[]`). This closes escape four.
4. **The one test:** `test_allowlist_derivation_is_total_across_id_and_placeholder_state` with subtests (A) fresh id + extra path refuses, (B) fully reserved record + non-empty candidate under `require_resolved=False` refuses; three recorded kills (restore the two-conjunct gate; disable resolved equality; delete reserved-empty equality), each turning the same method red.
5. **Record:** a new decision number, status `open (installs via AUTHENTICATOR-ALLOWLIST-GUARD-01)`, pointing back to D-151 without rewriting it; adopted only after the production clause map and the three kills land (D-170). The ruling-ready text in packet 12 §"Ruling-ready agreed text" is the contract of record.

The parked status lifts for ONE re-scope implementation round under this ruling; the same-signature count resets because acceptance now names the counterfactual inputs and the mutation kills. Test-side: the lifecycle/evidence tests that re-implemented the derivation by string substitution are replaced by assertions against the production derivation.
