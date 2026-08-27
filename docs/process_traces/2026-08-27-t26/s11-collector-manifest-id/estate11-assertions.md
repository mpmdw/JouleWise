# Estate-11 / pipeline-smoke assertions for the collection path (S11)

**Status:** adopted verbatim by the magistrate, T26 2026-08-27.
**Why these exist:** the S-0 clone proof stops at the mint. It does not execute
`scripts/run_campaign.py`, so nothing in it would have caught S9-01 — the collector
never recording which analysis manifest a campaign was collected under. Every
assertion below is a producer-against-real-consumer check of the kind D-158 F-3
identifies as the general detector for this defect class.

Each assertion names what is checked, where the bytes come from, and what its
failure would have caught.

## A1 — the identity is recorded, and it is the pack's own

After a real science-stage collection, every file in
`<runs_root>/campaign_manifests/*.json` carries:

- `analysis_manifest_id` **non-null**, and exactly equal to the `manifest_id` of the
  `analysis_manifest_v3.json` at the pack root the stage belongs to;
- `analysis_manifest_sha256` equal to the SHA-256 of that file's exact bytes.

Catches: the original S9-01 defect (142/142 manifests on disk carry null), and any
future regression where the collector records *an* id that is not *this pack's* id.

## A2 — the join actually joins

With the finalized manifest produced for that same pack,
`campaign_cooldown_evidence(runs_root, finalized["lineage"]["collection_manifest_id"])`
returns a **non-empty** selection covering the collected bundles.

Catches: the consumer-side half of S9-01. The equality filters at
`joulewise/analysis_engine/inputs.py:2143` and `:2191` select on exact id match; a
null or foreign id yields `{}` and the whole campaign silently disappears from the
claim edge. Asserting non-emptiness is the only check that fails when the two sides
disagree, because both sides individually look healthy.

## A3 — no bundle lands on `campaign_cooldown_evidence_missing`

No bundle in the collection is ruled ineligible for reason
`campaign_cooldown_evidence_missing` (`inputs.py:3443`).

Catches: the observable symptom S9-01 would have produced on the first claim
attempt after a spent collection window — every bundle ineligible, with nothing in
the collection logs indicating why.

## A4 — null-bound stages still collect (the F3 regression guard)

Every legitimately null-bound stage collected in the same window still records
`analysis_manifest_id: null` and **does not refuse**. At minimum:

- `configs/campaigns/neg8_reference_corpus`
- `configs/campaigns/window_references/{start_triplet,midpoint,end_triplet}`
- the D117 floor packs (`d117_floor_qwen25_1p5b_v*`, `d117_floor_qwen25_7b_v*`)
- `configs/campaigns/qwen25_7b_decode_floor_v1`
- `configs/campaigns/metrology_v1`

Catches: over-reach in the cure itself. A fix round on this stream added a
production-profile "no marker → refuse" rule; the delta re-audit and a lead bench
check found it would refuse all thirteen committed packs above. The window runbook
runs its reference and floor stages under
`configs/campaign_policies/quiet_mac_p2_production.json`
(`docs/phase_2/window_runbook.md:1495`), so that rule would have refused the window
chain's own stages. Null is contractually the calibration/reference case
(`docs/specs/c027/analysis_engine_trio.md:1859-1861`); this assertion is what keeps
a future tightening from forgetting it.

## A5 — the gamma pack carries an identity at all

The `_v4` gamma pack's `analysis_manifest_v3.json` has a top-level `manifest_id`
matching `^am-[0-9a-f]{64}$` and equal to `calculate_manifest_id` of its own content.

Catches: today's state. The committed gamma manifest has **no `manifest_id` key at
all** — it is a draft, and W-10 regenerates it. Under the S11 cure the collector
correctly refuses such a pack, so this assertion is the pre-window signal that W-10
actually landed, rather than discovering it on the night.
