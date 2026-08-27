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

## Compatibility fence

Campaign provenance written before PR #213 has **no** `analysis_manifest_sha256` key,
and 142 pre-existing manifests on disk carry `analysis_manifest_id: null`. The cure
must therefore distinguish three cases explicitly, not two:

- SHA present and equal → select;
- SHA present and different → refuse with a registered reason;
- SHA absent (pre-#213 provenance) → the row predates the field. Decide and record
  whether these are selected on id alone (backward-compatible, keeps the current
  claim corpus readable) or refused (fail-closed, but voids id-only history). This
  is the row's one design-bearing question and belongs in the ruling, not in the
  implementation.

## Acceptance evidence

- A campaign provenance whose id matches but whose recorded SHA differs from the
  finalized manifest's `lineage.prospective_manifest_sha256` produces a registered
  refusal, not an empty selection.
- The matching case still selects, with `campaign_cooldown_evidence` returning the
  collected bundles (assertion A2 of `estate11-assertions.md`).
- The absent-SHA case behaves per the ruled disposition, pinned by a test naming the
  pre-#213 provenance shape.
- No claim fixture currently passing regresses; if any must be re-fixtured, they land
  in the same change.

## Authority and fences

- Contract: `docs/specs/c027/analysis_engine_trio.md:176`, `:1859-1861`.
- Producer side is already in place: PR #213 (S9-01 / D-158 F-2(c)).
- Fence: sequence after the `_v4` mint closure. This touches the claim-consumption
  path and must not be coupled into a pre-mint change.
