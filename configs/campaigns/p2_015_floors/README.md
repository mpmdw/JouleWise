# Historical P2-015 campaign

The generated campaign and its generator are retired. Retrieve them from
`archive/process-traces-before-release-prune-2026-11-08:configs/campaigns/p2_015_floors/`
using the instructions in `docs/ARCHIVE.md`.

`calibration_plan.json` and `calibration_plan.sha256` remain byte-for-byte:
current v5 reference configs still bind that plan. Its historical
`order_manifest` field names the archived manifest; it does not make the
old campaign current. Historical membership tests read the archive directly.

`00_neg8_start/p2015-neg8-reference-start.json` remains a live NEG8 test input.
Use the current v5 packs for current collection work; see `CANONICAL.md`.
