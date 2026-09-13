# COLD-EYES PACKET #2 — exact D-079 issued-artifact bytes + execute operation

You are a COLD reviewer, no session context. The issuance IMPLEMENTATION
is fully gauntlet-clean (adversarial audit + 2 delta rounds, final
ACCEPT). This second cold gate rules on the EXACT ISSUED BYTES about to
be written and the EXECUTE operation — the artifact CONTENT did not
exist at the first cold gate (which correctly HELD the incomplete plan).
Verdict: PROCEED or HOLD (with the specific defect). This is the last
check before an irreversible write to the claim-authentication anchor.

## The exact artifact under review

- Emitted deterministically to: /private/tmp/claude-501/-Users-edr-code-JouleWise/df9ee343-36aa-42b0-8bbf-cc7598ecfdb3/scratchpad/d079-issued-artifact.REVIEW.json
  (file SHA-256 316113960c596a6f927987dbdf8f2bca4b0cca9ee4a59a540bbd32bba9048985;
  derivation_sha256 4f6633d5fb89a6e8fd137a834728b843915027b6f0b0afd6c37ae24e65d23f02).
  This is the byte-for-byte content that will replace the current
  schema_fixture in configs/calibration/calibration_acceptance_d079_v2.json.
- Ledger head it authenticates against: sequence 76, head_digest
  08456d5076c18a9a7f758969b02f5b6f7ad9fcc267dd12e2d3778c22458094d7.
- Disposition inventory: 30 valid / 2 systematic-invalid / 6
  ordinary-invalid (the lead-ruled B1 table, sha 5da820aa…), custody
  manifest 99cbf3df…, all 38 iCloud-backup custody copies.

## What the irreversible execute will do

`scripts/calibration_ledger_bootstrap.py --execute` writes
runs/calibration_observation_ledger.jsonl (the 76-receipt chain),
commits the head pin to configs/calibration/calibration_ledger_head.json,
and (with --emit-issued-artifact) writes the reviewed bytes above to the
acceptance-artifact config. Then D-116 records it.

## Your checks (rule each; read the REVIEW.json and primary sources)

1. **Artifact content correctness.** prior_observation_set.observations
   = all 38 content-distinct members with epoch + disposition (30/2/6)?
   cutoff = (76, 08456d50…)? derivation_corpus still n=19 with
   derivation_sha256 3cece3b2… PRESERVED in its sub-field (the
   whole-artifact derivation_sha256 is legitimately the NEW 4f6633d5…)?
   identity_epoch = d079_epoch? artifact_role=issued, claim_eligible
   semantics correct? No Window-B member present (D-113)?
2. **D-109 R2 conformance of the ACTUAL bytes** (not the plan): R2.1
   exact cutoff; R2.3 every content-distinct obs with epoch+disposition
   separate; R2.4 path-independent content identity; R2.7 raw-physics
   dispositions (the 2 systematic members 491995f3, c76f5d1c bound-
   exceeding); R2.8 counting (30 valid < 38, no re-derivation trigger).
3. **B1 disposition ruling** still correct vs docs/decision_log.md D-102
   (spot-verify the 2 systematic members' bounds exceed the
   0.033558756679900 screen).
4. **Execute correctness / reversibility.** Anything about the execute
   order, head-pin commit, or artifact write that is unsound or would
   leave an inconsistent state. (The impl audit confirmed validate-
   before-commit + exit-3; you're checking the OPERATION makes sense
   for THIS data.)
5. Anything else that makes issuing THESE bytes unsound.

## Output
PROCEED or HOLD with per-check findings. If HOLD, the exact defect +
primary evidence. Be exacting: irreversible claim-anchor write.
