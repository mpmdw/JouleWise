# VERIFICATION — D-079/D-102 acceptance-artifact issuance prep: R2 backfill inventory (read-only)

## Role and bounds

Read-only verification session in the main JouleWise checkout. WRITE_SCOPE:
none — modify nothing. Your report is the deliverable; it becomes the
evidence packet for a lead+Ed-gated issuance decision. Do not issue,
bootstrap, or edit any artifact or ledger file.

## Context

MINT-GENERALIZE-01 clause (b) requires the calibration acceptance
artifact to be ISSUED: "R2 backfill verified, ledger bootstrapped, head
pinned" (D-110 re-mint condition (b), docs/decision_log.md ~:7106-7112).
The artifact today is a schema fixture:
`configs/calibration/calibration_acceptance_d079_v2.json`
(`artifact_role: schema_fixture_unissued`, acceptance_id
`d079_calibration_acceptance_v2_n19`). The paired ledger
`configs/calibration/calibration_ledger_head.json` is at sequence 0 with
an all-zeros head digest (not yet bootstrapped).

The BINDING issuance requirements are D-109 R1 clause 4 and R2 clauses
1-8 (docs/decision_log.md ~:7024 and ~:7049-7078). Read them VERBATIM
first; they control over everything in this prompt. Key elements as the
lead understands them (verify against the actual text and flag any
divergence): cutoff = exact ledger sequence + head digest;
derivation_corpus stays the n=19; prior_observation_set must contain
every content-distinct governed calibration observation with epoch and
disposition; content identity comes from canonical primary-byte hashes;
the 32-valid/6-invalid same-epoch inventory is a backfill CANDIDATE
whose every member needs raw-physics + hash verification; ANY unresolved
member BLOCKS issuance; a 38-total counting rule feeds the D-102
corpus-doubling trigger.

## Task

1. Transcribe D-109 R2 clauses 1-8 (and R1 cl.4) into your report
   verbatim, each with a per-clause verification plan.
2. Locate the 32-valid/6-invalid backfill candidate inventory (search
   the decision log around D-109, configs/calibration/, and the D-109
   process traces; RUN_STATE.md history may name it). State exactly
   where it lives and its content identity.
3. For EVERY member (all 38): verify against primary evidence on disk —
   the raw calibration observation bundles (runs_recal* and any other
   governed calibration corpora), checking (a) the member's canonical
   primary-byte hash matches the raw bytes, (b) its raw-physics validity
   per the criteria the R2 text names (or the criteria referenced from
   the D-079/D-102 calibration acceptance design), (c) its epoch and
   disposition labels. Verdict per member: VERIFIED-VALID /
   VERIFIED-INVALID (matching the inventory's own labeling) /
   UNRESOLVED (with the exact reason and what evidence is missing).
4. Compute what the bootstrap ledger content would be: the exact
   prior_observation_set, the sequence number, and the head digest
   derivation (show the algorithm from the schema/contract; do NOT
   write any file).
5. Confirm the derivation_corpus n=19 is unchanged and its
   derivation_sha256 still matches the artifact's pinned value.
6. Apply the 38-total counting rule to the D-102 corpus-doubling
   trigger and state the result.

## Output

claude-codex-report/v1 envelope. Verdict: ISSUANCE-READY (all members
resolved, ledger content computed) / BLOCKED (list every unresolved
member and why) / DIVERGENCE (the R2 text differs from this prompt's
understanding — quote it). Include the per-member table, the computed
ledger bootstrap content, and file:line/sha evidence throughout. Flag
anything ambiguous rather than resolving it yourself — ambiguity
resolution is the lead's. Emit the report as your FINAL MESSAGE.
