# Magistrate ruling 31c — who owns the replay operands the close-out authenticates

Date: 2026-09-01. Seat: Fable magistrate. Input: report 31 (Sol xhigh fix
round on `feat/d165-dominance-closeout-core`, `31-sol-fix-12-closeout.md`),
which landed every ruled item except L-F1 and returned `NEEDS_RULING`:
the finalized manifest records each block's identity and member
positions (`joulewise/analysis_manifest_v3.py:3167`) and the aggregate
floor artifact's path + digest (`:3649`), but not the per-block replay
operands (`delta_j`, shared/local width, replay sign). The D-168 wording
"lineage-bound to the finalized manifest (manifest sha256, block ids,
per-block operands)" therefore names an operand comparison that has no
manifest side to compare against.

## Ruling

Sol's option 2, made concrete by the pattern the manifest already uses.

1. **The sidecar is a manifest attachment, authenticated by digest, the
   same way the floor artifact is.** The finalized manifest's `evidence`
   block (`analysis_manifest_v3.py:3630-3655`) gains one entry in the
   existing shape:
   `"dominance_replay_sidecar": {"path", "sha256", "schema_version",
   "sidecar_id"}`. The finalizer hashes the sidecar bytes and records
   its identity; it never reads a ratio, sign, or branch — the same
   outcome-blind boundary it keeps for the floor artifact today.
2. **Per-block operand equality against the manifest is struck** from
   D-168's binding clause. Hashing the sidecar's bytes into the
   finalized manifest authenticates every operand in it at once; a
   second copy of the operands inside the manifest would be redundant
   and would push measurement values into a record that is meant to
   seal identities. What the close-out still checks structurally:
   the sidecar's block-id set per contrast equals the manifest's
   `blocks[].block_id` set for that contrast (`:3167`), and the
   sidecar's cell census equals the manifest's contrast census.
3. **Division of work across the kernel rows** (D-168 clause 5 rows,
   PR #252):
   - `D165-CLOSEOUT-CORE-01` (this branch) implements the CONSUMER
     side only: the builder takes `--finalized-manifest`; the close-out
     records `finalized_manifest_sha256` (sha256 of the manifest file
     bytes) and `replay_sidecar_sha256`; it refuses with
     `manifest_lacks_replay_sidecar` when the `evidence` entry is
     absent, `replay_sidecar_digest_mismatch` when the sidecar bytes do
     not hash to the recorded digest, `replay_sidecar_identity_mismatch`
     when `sidecar_id`/`schema_version` differ, and
     `manifest_block_membership_mismatch` when the block-id sets differ.
     Each refusal selects neither branch (D-168 clause 2).
   - `D165-SIDECAR-EMIT-01` wires the PRODUCER side: the mint emits the
     sidecar through the one sanctioned adapter, and the finalizer
     (`analysis_manifest_v3.py`, out of this branch's scope) records the
     attachment. Its acceptance gains: "finalized manifest carries the
     `dominance_replay_sidecar` evidence entry".
   - `D165-E2E-REPLAY-01` proves the whole chain from committed fixtures.
4. **Test fixture for the consumer side, this round:** obtain the
   finalized manifest through the production finalizer (as report 31
   already does, L-F4), then add the `dominance_replay_sidecar` evidence
   entry in the test and write the augmented manifest to disk — the
   close-out hashes the file bytes it is given, so no manifest self-hash
   needs recomputing. The test file states in one comment that the
   entry is injected pending D165-SIDECAR-EMIT-01. The four blocked
   regressions become: wrong manifest digest (a manifest edited after
   the close-out recorded it), forged self-consistent sidecar (digest
   differs from the manifest's record), sidecar from another campaign
   (block-id set differs), and absent evidence entry.

## Why this line and not the others

Option 1 (extend `blocks[]` with operands) moves measurement values into
the identity-sealing record and forces a manifest schema revision for a
value the sidecar already carries. Option 3 (re-derive operands from
bundles at close-out time) makes the close-out a second reducer and puts
the D-165 arithmetic in two homes. Under D-161 the adversary defended
here is honest drift — a sidecar from a different run or a manifest
edited after the fact — not a forger; a digest recorded by the
outcome-blind finalizer is exactly the cheap, fail-closed wire for that.

Dissent invited: the delta re-audit of the round-2 fix carries an
explicit license to contest this ruling on the record.
