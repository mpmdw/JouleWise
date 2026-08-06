# COLD-EYES ISSUANCE PACKET — D-079 calibration acceptance artifact + ledger genesis import

You are a COLD reviewer: no prior context from the session that produced
this. Rule under rule-11 on whether this IRREVERSIBLE issuance is correct
to EXECUTE. The human principal (Ed) has authorized the issuance decision;
your job is NOT whether to issue but whether the assembled artifact is
CORRECT — mechanical/correctness errors a loop-immersed agent can't see.
Verdict: PROCEED or HOLD (with the specific defect). Read primary sources
yourself; do not trust this packet's numbers without checking.

## What is about to happen (irreversible)

1. `scripts/calibration_ledger_bootstrap.py --execute` writes the real
   `configs/calibration/calibration_observation_ledger` (currently
   absent; head pin at genesis seq 0 / all-zeros).
2. The printed head pin (seq 76, head below) is committed to
   `configs/calibration/calibration_ledger_head.json`.
3. `configs/calibration/calibration_acceptance_d079_v2.json` flips
   `artifact_role` schema_fixture_unissued → issued, cutoff = (seq 76,
   head), prior_observation_set filled per the ledger's import-marked
   prefix.
4. A decision-log entry (D-116) records the issuance.

This artifact is the authentication anchor for ALL future floor-mint
claims. An error here silently taints every downstream claim.

## Assembled facts (VERIFY each against the cited primary source)

- Disposition table: `/private/tmp/d079-ledger-dispositions.json`,
  sha256 `5da820aa5c649e5991b934230cd75e8c99daa8dcea22f3f1b3e3db89c80f2a6a`,
  38 members = 30 valid / 2 systematic-invalid / 6 ordinary-invalid.
- The 2 systematic-invalid members (`20260726T000039-491995f3`,
  `20260801T064830-c76f5d1c`) were lead-ruled systematic (bounds exceed
  the 0.033558756679900 preflight screen; D-102 names the first a
  systematic failure). VERIFY this ruling against
  `docs/decision_log.md` D-102 and the verification report's per-member
  physics (report: `docs/process_traces/2026-08-05-d079-issuance/VERIFICATION-REPORT.md`).
- Custody manifest: `/private/tmp/d079-custody-manifest.lead.json`,
  sha256 `99cbf3df7aef3b81839f40272a529eb137bf2f21276e2a1d07788c764035f078`,
  lead-regenerated (byte-identical to the delegated generation).
- Candidate head: `08456d5076c18a9a7f758969b02f5b6f7ad9fcc267dd12e2d3778c22458094d7`
  at sequence 76. REPRODUCE it yourself with a dry-run (read-only,
  writes nothing):
  `python3 scripts/calibration_ledger_bootstrap.py --disposition-table /private/tmp/d079-ledger-dispositions.json --expected-table-sha256 5da820aa5c649e5991b934230cd75e8c99daa8dcea22f3f1b3e3db89c80f2a6a --custody-manifest /private/tmp/d079-custody-manifest.lead.json --expected-custody-manifest-sha256 99cbf3df7aef3b81839f40272a529eb137bf2f21276e2a1d07788c764035f078 --checkout-root /Users/edr`
- derivation_corpus stays n=19, derivation_sha256
  `3cece3b2c816476887613c3c25d8d186dbefa61047275c5b157d32980249da9d`
  (unchanged; the issuance edits the acceptance file so its OWN file
  hash changes — that is expected, the n=19 statistics do not).
- Binding requirements: D-109 R1.4 + R2.1-8 (docs/decision_log.md).
- The bootstrap code passed a 4-round adversarial gaunttet ending in an
  ACCEPT delta audit (record:
  `/private/tmp/claude-501/-Users-edr-code-JouleWise/df9ee343-36aa-42b0-8bbf-cc7598ecfdb3/scratchpad/ledgerboot-delta4.md`).

## Your checks (rule and report each)

1. Reproduce the head. Does it equal 08456d50…@76? If not → HOLD.
2. Spot-verify the B1 disposition ruling: are the two systematic-invalid
   members genuinely bound-exceeding per the raw physics in the
   verification report, and is systematic-invalid the correct ledger
   disposition (vs valid) under D-102's screen? A wrong disposition
   changes the head and the corpus-doubling count.
3. D-109 R2 conformance of the plan: prior_observation_set completeness
   (all 38 content-distinct, epoch+disposition), content identity from
   primary-byte hashes, the import marker excluded from post-cutoff
   populations, cutoff = exact (seq, head).
4. Any reason the genesis import should NOT be the authoritative ledger
   (root-universe completeness now that custody is manifest-pinned;
   the manifest references iCloud-backup copies for 22 members — is that
   acceptable provenance for the authoritative ledger, or must those
   copies live in the primary checkout first?).
5. Anything else that would make this issuance unsound.

## Output

A clear PROCEED or HOLD with per-check findings and the reproduced head.
If HOLD, name the exact defect and the primary evidence. This is the
last check before an irreversible write to the claim-authentication
anchor — be exacting.
