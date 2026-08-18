# DESIGN CONSULT — WO-FREEZE-NUMBERING (chain-monotonic freeze-0002 + predecessor bindings)

WRITE_SCOPE: []

One-round design consult with explicit license to disagree. Your design
opinion is the primary deliverable; a cross-model implementer builds against
the ratified version.

## Mandate

Ed's D-139 A3 (decision_log, "Phase-2 reserved approvals ... APPROVED")
requires the successor (_v2) packs to freeze with **chain-monotonic
`freeze-0002` receipts carrying explicit predecessor bindings** to the v1
packs' freeze-0001 receipts. Verified reality: `generate_freeze_receipt`
(joulewise/arm_readiness.py, `number = 1` at ~:3472, `"supersedes": None`
~:3486, idempotent early-return ~:3419-3428, second-receipt refusal
~:3429-3432) cannot mint it. The transaction runsheet's step-4 claim of "NO
code edits" is false; this work order is mandated. A cold gate tonight
(scratchpad/coldgate-freeze-semantics/14-composed-verdict.md, holding 7)
registered this WO and ruled that your design round may adopt receipt-chain
machinery on its own merits — with the constraint that serialized pack bytes
NEVER transition post-mint (holding 1) and freeze remains fail-closed.

## Read before designing

- joulewise/arm_readiness.py: generate_freeze_receipt, _load_freeze_reference,
  scan_receipt_namespace (arm-side supersession chain semantics ~:2095-2108),
  the arm-receipt predecessor-binding construction (~:4122-4131), vocabulary
  readiness_receipt_superseded, plan_arm_readiness_attachment
  (committed_receipts[-1] selection ~:1951).
- docs/process/phase2-transaction-runsheet.md steps 4-5.
- The R1 freeze-lifecycle cold-gate note that receipt numbering semantics
  belong in the freeze-receipt v2 schema
  (docs/process_traces/2026-08-15-r1-freeze-lifecycle-consult/coldgate-adjudicator-ruling.md ~:61).
- scratchpad/coldgate-freeze-semantics/14-composed-verdict.md (holdings 1, 7).
  Scratchpad root: /private/tmp/claude-501/-Users-edr-code-JouleWise/d6206bd4-5fa1-4141-9529-e3e811ea7da4/scratchpad/

## Questions to rule on (numbered D-items; cite file:line, confirm anchors resolve)

1. What does "chain-monotonic freeze-0002" correctly MEAN here: per-pack
   receipt namespaces stay at their own 0001 with a cross-pack predecessor
   binding, or a family-level monotonic counter where the successor pack's
   first receipt is literally freeze-0002? Derive from D-139 A3's text, the
   R1 ruling, and the schema's existing semantics; state the reading you
   adopt and why.
2. Schema: what does the freeze-receipt v2 schema carry — predecessor pack
   id/receipt sha/plan sha? A family/lineage id? Where does validation live
   (mint-time, _load_freeze_reference, both)? Fail-closed behavior when the
   predecessor is absent/unreadable/REFUSE-status?
3. Should arm-side supersession semantics extend to freeze receipts, or is
   predecessor-binding-without-supersession the smaller correct design
   (the v1 receipt is NOT superseded — its pack remains a valid historical
   record; the v2 receipt is a NEW pack's first freeze)? Rule explicitly.
4. Blast radius: enumerate every touch point (mint, load, scan, attachment
   builder, schema constant, existing v1 receipts' continued validity,
   tests). Minimal design that satisfies A3 without destabilizing the three
   committed v1 freeze-0001 receipts.
5. The regression set: mint-time chain validation, predecessor-absent
   refusal, v1-receipt continued authentication, idempotency, and whatever
   your design makes load-bearing.
6. Anything in A3's approved wording you judge UNDERSPECIFIED enough to need
   an Ed ruling rather than a design choice — name it explicitly.

## Output

claude-codex-report/v1 envelope, genre review. D-items, I-items (mechanical
bar), R-items (regressions), explicit disagreements, and the runsheet
corrections the design implies.
