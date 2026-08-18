# COLD GATE — freeze-status byte semantics for successor packs (2026-08-18)

## Convening trigger (mandatory, rule 11)

The magistrate proposes to (i) rule auditor delta-5's blocker B2 NOT A
DEFECT, reversing that audit's DO_NOT_MERGE verdict component, and (ii)
record a superseding amendment to one sentence of the adopted structural
consult (its D-6). Reversal/reinterpretation of a prior verdict is a
mandatory cold-gate trigger. A second downgrade in the same stream (B1 →
registered residual under the D-139 A1 threat model) is included for
ratification review.

## Question presented

After a D-134 freeze receipt is minted over an emitted successor (_v2)
pack, must the pack's SERIALIZED draft_status fields and README bytes ever
transition to frozen-status text (delta-5 B2's expectation, derived from
consult ruling D-6), or does the ratified doctrine — "receipts govern over
descriptive bytes; frozen bytes are never repaired" (M-2 gate amendment,
prior cold gate, packet file 05) — make the committed receipt authoritative
over unchanged descriptive draft bytes, exactly as already accepted for the
three v1 packs frozen 2026-08-13 (packet file 06)?

## Dispositive new evidence (packet file 07, executed, not asserted)

The freeze receipt's pack_identity pins plan_sha256 = SHA-256 of
calibration_plan.json bytes; calibration_plan.json itself contains
draft_status (an enumerated transition site) and embeds the SHA of another
status-bearing artifact. Therefore ANY serialized transition invalidates
the receipt: _load_freeze_reference refuses unconditionally at the
dry-run/arm/verify gates (readiness_freeze_receipt_mismatch), and
generate_freeze_receipt hardwires number=1 / supersedes:None (no re-mint).
Executed end-to-end by the round-5 implementer (Opus 5): full coherent
frozen-status regeneration, committed → REFUSED; re-mint attempt →
mutated:false. The specified B2 fix would make every successor pack
PERMANENTLY UNARMABLE.

## Options before the gate

(a) MAGISTRATE-PROPOSED: B2 not-a-defect. The consult's D-6 sentence
    ("the intentional draft→frozen transition happens once during the
    governed freeze transaction", read by delta-5 as serialized-byte
    transition) receives a dated superseding amendment: the transition IS
    the receipt + plan-tree attachment; descriptive bytes stay as
    generated; dynamic target_status + the fail-closed post-freeze
    regeneration guard are the M-2 "freeze-aware" behavior for future
    packs. v1 precedent applies unchanged to v2.
(b) Two-phase freeze with superseding receipts (schema has `supersedes`;
    vocabulary has readiness_receipt_superseded) — an arm_readiness.py
    contract change enabling serialized transition without breaking pins.
(c) Transition only receipt-unpinned artifacts (README text), leaving
    plan-embedded status fields draft.

## Also before the gate

1. B1 disposition ratification: post-validation symlink substitution =
   registered residual (requires a concurrent adversarial process; D-139
   A1 + single-operator discipline exclude it; check-then-write with
   resolved-ancestor validation is the accepted boundary). Round-4/5 added
   16-case refusal coverage and the in-code rationale comments.
2. If (a) is adopted: stream closes at commit 0cb9bf2 (subject to the
   pending verification audit), and the amendment text for D-6 plus the
   already-recorded D-5 decision-log correction land together at the merge
   gate.

## Packet inventory

02 consult ruling (Sol) — adopted in full 2026-08-17, incl. D-6.
03 delta-4 audit — found the symlink class; S3 first flagged the modeled
   freeze transition.
04 delta-5 audit — B1/B2 blockers, DO_NOT_MERGE, mutation probes all
   killed, conformance trace complete.
05 M-2 gate-amendment decision-log excerpt (prior cold gate's upheld core).
06 Runbook D-134 excerpt: v1 precedent (receipt authoritative over legacy
   draft wording; "do not repair those committed bytes").
07 Round-5 implementer report (Opus 5): the executed circularity proof and
   the constraint chain with resolved anchors.

The adjudicator rules on the QUESTION and the two dispositions; it does
not owe deference to the magistrate's proposal and may adopt (b), (c), or
a shape not listed. Its ruling is paired with refuter reports before the
magistrate composes the verdict.
