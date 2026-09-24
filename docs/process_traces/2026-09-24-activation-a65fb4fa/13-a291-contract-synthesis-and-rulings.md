# 13 — A291 contract: magistrate synthesis of record 02 (Opus 5.5 draft) and record 09 (Sol 6.0 high contract lens)

Magistrate: Opus 5.5, activation a65fb4fa. These rulings cover only REPRESENTATION choices (R class) and adopt the lens's corrections of predicates against ruled text. Every choice that adds to, weakens or reinterprets a ruled sentence (S class) goes to a cold Fable gate with a paired Opus refuter. The magistrate does not decide those, though it states a proposed disposition for the judge.

## Lens findings accepted (the v2 contract must install them)
- F01 INV-03: ban copies of registered VALUES, not key names; the roster's own `schema` and the ruled derived fields are allowed.
- F02 / OP-04: `item_set_sha256` preimage is the FLAT id list in level order, then registered order within level (literal 45/10 §Q3 text).
- F03 INV-05: `claim_ready` false in pilot; consumers refuse non-claim-ready outside pilot; no requirement that registered producers emit true. OP-10 is NOT a conflict (lens L5 agreed): the derived flag is ruled (21/10 D4) and is not a copy.
- F04 INV-09: compare string keys to `{str(l) for l in LEVELS}`.
- F05 INV-10/12: the invariant is membership equality across models and parent relationships. Slicing rule and block_id syntax move to a separate representation contract (§2), which is OP-06 and goes to the gate.
- F06 / F16a: add a PLACEMENT record `{block_id, attempt, stage, reserved_s, envelope_index}`. Capacity is checked per envelope against the reservations of the placements it actually ran (OP-21: active and voided). "Alone" applies only to the whole-block-retry placement.
- F07 / OP-24: a pending block is not a counted window. Distinguish PLANNED minima (checked at pack and requeue) from EXECUTED minima (checked at reduce entry on counted evidence). The executed `spread_exceeded` is determined at reduce entry.
- F08 INV-35: check (a) each innocent reschedule is linked to a culprit event in the same envelope; (b) each item has at most two culprit events; then (c) the aggregate bound.
- F11: every magistrate row needs an executed violating witness on every closed path, using entry or exit injection where it cannot be reached naturally. Any `n/a` is an exception for the gate (OP-28).
- F12: INV-13's row obligation moves to A292. INV-17 requires contiguous indices (OP-27, R). INV-21 (initial `reserved_s`) and INV-36 (attempt increments) become proposed contract, S class, for the gate (OP-22).
- F13 / OP-23: drift position uses the envelope of the COUNTED attempt, per the ruled text. The pack-time lever is a separate "planned" computation. Refusal versus flag after capture goes to the gate.
- F14: whether a zero elapsed time is allowed for a cut-off goes to the gate. Completed-single and whole-block completed outcomes get their own rows once OP-14/15 are ruled.
- F15: add rows for M8-era per-cell balance (08 F1 with the later tolerance), the whole-block completed outcome (`late`, culprit), the completed-single outcome, and constant-sweep obligations.
- OP-07: accept finite JSON numbers as given; digests are over the exact accepted representation (lens pick). No float-only narrowing.
- OP-31: no plausibility warnings in the checker's violation output (lens pick).
- R-class picks agreed by both seats and ruled here: OP-02, OP-08, OP-09, OP-11, OP-20, OP-21, OP-25, OP-27, OP-32, OP-33.

## Magistrate representation rulings on the digest chain (F09, F10, OP-12, OP-13)
- Preimage rule: the roster digest is `canonical_json_sha256` of the roster with the top-level `sha256`, the top-level `registered_sha256`, and every event's `sha256` removed.
- `event.sha256` equals the resulting roster's top-level `sha256` computed by that rule. It is the ruled "resulting sha256" and is not circular.
- `registered_sha256`: a root roster (no events) carries `registered_sha256 == sha256`. Every descendant carries the root's `sha256`. `reduce` asserts `registered_sha256 == pack(registration, predicted_decode_s)["sha256"]` uniformly, with NO root exception (lens F10 satisfied). Excluding it from the preimage weakens nothing, because it is itself verified against a re-pack.
- `parent_sha256` is dropped; `events` is the chain.
The gate is asked to confirm these as representation (Q-list item "digest chain").

## S class, for the cold gate (both seats' picks go in the charge)
OP-01 (constants with no CARRIED home), OP-03, OP-05, OP-06, OP-14, OP-15, OP-16, OP-17, OP-18, OP-19, OP-22, OP-23 (post-capture drift consequence), OP-24 (when the executed spread is final), OP-26, OP-28 (the `n/a` escape), OP-29 (who owns the `reduce` entry witness), OP-30, OP-34 (whether R11 binds), F14 (zero elapsed), and the digest-chain confirmation.
