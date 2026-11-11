# File prune g2: historical campaigns

Branch: `ops/2026-11-10-file-prune-g2-campaigns`, based on g1 `98bc99fd4`.
Local-only, offline, source/metadata work. No coordination or frozen B5 source
edits, model downloads, pipeline execution or measurement collection.

## Deletions and KEEP decisions

Removed 297 of the 300 original files under
`configs/campaigns/p2_015_floors/`: obsolete generated members/manifests,
generator, campaign specification, backup script and historical README.
Every deleted blob matches
`archive/process-traces-before-release-prune-2026-11-08:<path>` exactly.
The brief's `configs/p2_015_floors/` spelling is not a tracked directory;
the actual pack is under `configs/campaigns/`.

KEEP, byte-identical:

- `calibration_plan.json`: current v5 reference configs pin it.
- `calibration_plan.sha256`: its original integrity sidecar.
- `00_neg8_start/p2015-neg8-reference-start.json`: mixed live NEG8 tests in
  `tests/test_run_campaign.py` still read it.
- All nine complete D117 Qwen2.5 v1/v2/v3 packs (1,329 files): the historical
  receipt/histsem verifier reads and hashes current predecessor packs and
  freeze receipts; v5's chain reaches v3 and earlier generations. V1 is also
  named by original B5 identity/registration sources; the Block4 draft names
  v3. These are real reader bindings, not a reason to delete by glob.
- Every v5 pack, old-format reader, ALIGN/BYTES/B6/x86/port input, and original
  calibration/registration remains untouched.

`docs/ops/FILE-PRUNE-G2.tsv` lists each deletion and each retained unit with
its reason. A new pack README explains the three retained original inputs
and how to retrieve the retired pack; it is not a new campaign.

## Reader migration and edited files

The root, phase-absolute and phase-decode historical order manifests are
still test oracles, now read directly from qualified archive tag:path blobs
by `tests/archived_campaign.py`. Missing tag/blob is an error; there is no
network fetch, fallback oracle or copied replacement data. Existing
membership/run-ID assertions and original digest literals are unchanged.

Edited `tests/test_d117_floor_qwen25_1p5b_plan.py` and
`tests/test_floor_extraction.py` only at these historical manifest reads.
Retired the six generator-only `CampaignSpecificationTests` methods and
their helper/constants/imports from `tests/test_modularity.py`; its two
`ClosedSetRegistryTests` remain. Updated that module's timing-map value from
0.448 to 0.104 seconds using the observed isolated run (including import).
Qualified historical directory/generator examples in
`docs/phase_2/window_runbook.md` and `splitwise_decode_campaign.md`.
Updated `CANONICAL.md` and regenerated `configs/pins/registry.json`.

No scanned refusal source or number-bearing implementation was removed.
`configs/gates/hazard_refusals.json` and number-coverage tables therefore
remain unchanged; the refusal census validates the retained scope. Old
bundle/extraction readers and specifications remain available.

## Verification

Python 3.13 commands used the supplementary path/network guard and synthetic
TMPDIR described in the g1 report, one unittest selection at a time:

- `tests.test_modularity`: 2 PASS, 0.104 seconds including import.
- `tests.test_floor_extraction.FloorMintSpecValidationTests.test_specs_match_pinned_order_manifests_and_membership_shape`:
  1 PASS; historical metadata only, no real-capture fixture replay.
- `tests.test_d117_floor_qwen25_1p5b_plan.D117FloorQwen251p5BPlanTests.test_ids_are_fresh_and_arm_pins_are_projection_owned`:
  1 PASS.
- `tests.hazards.test_refusal_allowlist`: 23 tests OK, one existing optional-design
  skip, 13.6 seconds.
- `tests.b5_analysis.test_frozen_files`: 4 PASS.
- `tests.test_b5_seal_landing`: 9 PASS.
- `tests.test_docs_freshness`: 31 PASS.
- `python3 -m compileall -q joulewise scripts tests`: PASS.
- `python3 -B scripts/repin.py --write registry`: completed; `--check`: PASS,
  16 families current. No protected number was repinned from changed bytes.
- Per-deletion source grep: zero live/unqualified narrative hits; 301 qualified
  archive hits and 297 inventory/history hits. `.github`, scanners, imports,
  manifests and string paths were included.
- `git diff --check`: PASS.

Independent read-only review by `prune_readers_review` traced the predecessor
reader chain and all fixed P2-015 readers, identified the three manifest
migrations and the runbook citations, and confirmed the proposed bounded
retirement. Final diff and authority decisions remain this seat's. Static
source searching cannot prove absence of arbitrary computed loaders; none
was found in the fixed-pack source closure.

No full suite was run; CI owns that gate. No native MLX/hardware claim is
made. All g1 deferrals remain: B5 analysis/whole-window mirror, remote stack,
site/report pipeline, scored lane, ALIGN v4, BYTES, B6, x86 and port work.
Next exact step: g3 from this tip, integrating #668 with a reader-only
compatibility surface for protected callers.
