# Campaign Packs

Purpose: these packs are pre-hardware campaign artifacts. They let the
operator plug in hardware, fill only device-pair/link placeholders, freeze the
analysis registry, and execute with minimal design work.

## Cut-Line

This stream intentionally covers only five core hardware-gated packs:

| Pack | Consumers | File |
|---|---|---|
| Split inference suite | Q1 split reduces energy; Q2 link bandwidth sensitivity; Q3 split energy-latency Pareto | `docs/campaign_packs/split_suite_q1_q2_q3.md` |
| Rail-vs-wall boundary sensitivity | Q6 / C5-2.10 | `docs/campaign_packs/q6_c5_2_10_rail_vs_wall.md` |
| Predicted-vs-measured KV economics | C5-2.3 | `docs/campaign_packs/c5_2_3_kv_economics.md` |

The broader `TASK_QUEUE.md` rank-0d list is deliberately excluded from this
stream: C5-2.7/2.8, C5-3.1/3.5, and C5-I.1..C5-I.5 are not authored here.
The broad C5-I interop packs stay excluded until the claims-index linter
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

## Known Pre-Hardware Gaps

The current JouleWise CLI supports `validate-config`, `kv-size`, `run`,
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
