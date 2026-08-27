# Draft queued row — COLLECTOR-MANIFEST-SHA-IDENTITY-01

**Status:** DRAFT for the magistrate's registration wave. Not implemented; outside
the S11 fence (the cure lives in `joulewise/analysis_engine/`, owned by the S10
stream). Drafted T26 2026-08-27 per magistrate ruling (2).

**Origin:** S11 contract-lens refuter finding F4, a SPLIT VERDICT — raised by one
lens only (contract conformance) and not corroborated by the execution-lens audit,
so it was recorded rather than applied.

## Goal

Make the analysis-manifest SHA-256 that `scripts/run_campaign.py` now records in
campaign provenance **load-bearing at the claim edge**, instead of attested-but-inert.

PR #213 (S11) added `analysis_manifest_sha256` to campaign provenance alongside the
`analysis_manifest_id` it also began recording. Downstream, the campaign-cooldown
join selects **solely by id**: `joulewise/analysis_engine/inputs.py:2143` and `:2191`
compare `raw.get("analysis_manifest_id") == manifest_id` and never look at the SHA.
The finalized manifest carries the matching byte identity as
`lineage.prospective_manifest_sha256` (`joulewise/analysis_manifest_v3.py`, the
lineage block built at `:3636-3650`), and it too is unread by the join.

The refuter's contract argument, verbatim in substance:
`docs/specs/c027/analysis_engine_trio.md:1859` names
`campaign_cooldown_evidence` "the public reuse point for the **hash-verified**
cooldown join", and `:176` records that "file-byte SHA-256 is recorded by downstream
consumers separately". An id-only join is not hash-verified in the contract's sense.
Two prospective manifests that share an id but differ in bytes — a partially
regenerated pack, a hand-edit after freeze, a restored backup — would join
successfully today.

## Cure

In `joulewise/analysis_engine/inputs.py`, extend the campaign-cooldown join so that a
campaign provenance record is selected only when **both** hold:

1. `analysis_manifest_id == finalized["lineage"]["collection_manifest_id"]` (as today);
2. `analysis_manifest_sha256 == finalized["lineage"]["prospective_manifest_sha256"]`.

A record whose id matches but whose SHA differs must **refuse** under a registered
D-078 reason rather than being silently dropped from the selection — a silent drop
reproduces the exact failure shape S9-01 had (empty join, `campaign_cooldown_evidence_missing`,
no indication of cause).

## Compatibility fence — RULED (magistrate, T26 2026-08-27)

Campaign provenance written before PR #213 has **no** `analysis_manifest_sha256` key,
and 142 pre-existing manifests on disk carry `analysis_manifest_id: null`. The
disposition is ruled, not open:

- **Provenance authored BEFORE #213** (no SHA key): selected on **id alone**. Every
  pre-#213 corpus is non-claim-bearing under D-078 / D-146, so nothing that could
  reach a claim rides the weaker join. This keeps the existing corpus readable
  instead of voiding id-only history.
- **Provenance authored AFTER #213**: the SHA is **required**. Present and equal →
  select. Present and different → **refuse** under a registered D-078 reason. Absent
  → refuse; a post-#213 collector always writes the field, so its absence is
  tampering or truncation, not age.

The implementation therefore needs an authorship discriminator that cannot be forged
by simply omitting the key. Deriving "post-#213" from the absence of the field is
circular. Bind it to something the record already carries and the collector already
writes — the campaign-provenance schema version, the attestation row, or an explicit
authoring-generation marker — and state which in the implementation. This is the
row's one remaining implementation question; the policy above is settled.

## Acceptance evidence

- A campaign provenance whose id matches but whose recorded SHA differs from the
  finalized manifest's `lineage.prospective_manifest_sha256` produces a registered
  refusal, not an empty selection.
- The matching case still selects, with `campaign_cooldown_evidence` returning the
  collected bundles (assertion A2 of `estate11-assertions.md`).
- Pre-#213 provenance (no SHA key) still selects on id alone, pinned by a test naming
  that shape; post-#213 provenance with the SHA absent or different REFUSES, pinned
  separately. The authorship discriminator itself has a test proving it cannot be
  defeated by deleting the SHA key.
- No claim fixture currently passing regresses; if any must be re-fixtured, they land
  in the same change.

## Authority and fences

- Contract: `docs/specs/c027/analysis_engine_trio.md:176`, `:1859-1861`.
- Producer side is already in place: PR #213 (S9-01 / D-158 F-2(c)).
- Fence: sequence after the `_v4` mint closure. This touches the claim-consumption
  path and must not be coupled into a pre-mint change.
