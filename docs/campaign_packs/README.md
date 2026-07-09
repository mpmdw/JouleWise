# Campaign Packs

Purpose: these packs are pre-hardware campaign artifacts. They let the
operator plug in hardware, fill only device-pair/link placeholders, freeze the
analysis registry, and execute with minimal design work.

`configs/campaign_packs/` does not exist yet. Plug-in-day execution must first
create that directory and materialize each filled in-doc JSON template into a
named config file under it; the template placeholders are intentionally not
committed as runnable starter configs.

## Index

P2-032 landed the five core hardware-gated packs:

| Pack | Consumers | File |
|---|---|---|
| Split inference suite | Q1 split reduces energy; Q2 link bandwidth sensitivity; Q3 split energy-latency Pareto | `docs/campaign_packs/split_suite_q1_q2_q3.md` |
| Rail-vs-wall boundary sensitivity | Q6 / C5-2.10 | `docs/campaign_packs/q6_c5_2_10_rail_vs_wall.md` |
| Predicted-vs-measured KV economics | C5-2.3 | `docs/campaign_packs/c5_2_3_kv_economics.md` |

P2-034 adds the broader campaign packs that D-059 made lintable:

| Pack | Consumers | File |
|---|---|---|
| Device perf/W rankings with runtime revision held constant | C5-2.7 | `docs/campaign_packs/c5_2_7_device_perf_w_rankings.md` |
| Placement-policy optimality from Q4 coefficients | C5-2.8 | `docs/campaign_packs/c5_2_8_placement_optimality.md` |
| Second-unit and cross-lab replication | C5-3.1; C5-3.5 | `docs/campaign_packs/c5_3_1_3_5_replication.md` |
| Benchmark import family | C5-I.1; C5-I.2; C5-I.5 | `docs/campaign_packs/c5_i_1_i_2_i_5_import_family.md` |
| FLORES tokenizer fertility tax | C5-I.3 | `docs/campaign_packs/c5_i_3_flores_fertility.md` |
| Harness overhead floor | C5-I.4 | `docs/campaign_packs/c5_i_4_harness_overhead_floor.md` |

Import/export split: C5-I.1/I.2/I.5 are `benchmark_import` source-manifest
packs. C5-I.4 is the export/marker-shim overhead pack and depends on P2-022
verdict branches. FLORES remains separate from the generic import family
because C5-I.3 needs semantic-matched plus token-matched legs, token
normalization captions, FLORES licensing, and the deferred D-046/B6 source
session decisions.

Historical P2-032 cut-line note retained for supersession context:

The broader `TASK_QUEUE.md` rank-0d list is deliberately excluded from this
stream: C5-2.7/2.8, C5-3.1/3.5, and C5-I.1..C5-I.5 are not authored here.
(Superseded 2026-07-09, D-059: the claims linter landed the same day — `scripts/claims_lint.py`; the broad C5-I interop packs are now queued as P2-034 and every draft AP row must pass `--mode pack`.) Original exclusion note: The broad C5-I interop packs stay excluded until the claims-index linter
exists, because those packs need machine-enforced frozen-contrast,
source-provenance, and item-window claim guards before they are safe to turn
into campaign templates.

## Contract Relationship

Every pack carries a DRAFT AP row shaped by
`docs/contracts/analysis_plans.md`. DRAFT means not frozen: the rows become
claim-bearing only when the analysis registry freezes before campaign
execution, per the Analysis Registry amendment and D-053. Each DRAFT row
includes `family_id`, `claim_role`, `selection_scope`, and
`multiplicity_rule`, but the final `contrast_id` set, manifest hash, bundle
hashes, Holm/BH denominator, and linked manifests are filled at registry
freeze time.

The pack templates consume these frozen contracts:

- Analysis-plan fields and frozen-registry rules:
  `docs/contracts/analysis_plans.md`.
- Claim ceilings and exact forbidden upgrades:
  `docs/research_question_registry.md`.
- Claim wording caps: `docs/contracts/claims_ladder.md`.
- Single-unit caption language: `docs/contracts/capstone_scope.md`.
- Bundle and composite-bundle layout:
  `docs/contracts/run_bundle_layout.md`.
- Window names, split-stage accounting, measurement boundaries, clock-offset
  markers, and ordering rules:
  `docs/contracts/measurement_methodology.md`.
- Floor rows and false-effect guard semantics:
  `docs/phase_2/detection_floor.md`.

Operator ordering note: `order_manifest.json` controls whole
config/bundle execution order across a campaign. Intra-suite block and item
order are separate: they are controlled by `suite_manifest.json`
`execution_policy.order_policy` plus the controller-derived `order_row`
recorded for each suite member.

## Known Pre-Hardware Gaps

The current JouleWise CLI supports `validate-config`,
`print-config-schema`, `print-output-schema`, `kv-size`, `run`,
`validate-bundle`, `reduce`, `report`, and `envelope-gate`. Transfer-bench,
schema v0.2 split configs, split orchestration, composite-bundle validation,
wall-meter import, and reduced cross-bundle split/KV result scripts are still
PLANNED under the Phase 3 design or hardware-gated queue owners named inside
each pack.

`docs/phase_2/detection_floor.md` currently names request, phase prefill,
phase decode, item, and level floor rows, but not dedicated `transfer`,
`serialize`, or `deserialize` split-stage floor rows. The packs therefore
name all existing exact floor rows they can consume and cap any standalone
transfer/deserialize L2/L3 claim until P2-015 adds those rows or the frozen AP
row names an accepted AP-specific bound.
