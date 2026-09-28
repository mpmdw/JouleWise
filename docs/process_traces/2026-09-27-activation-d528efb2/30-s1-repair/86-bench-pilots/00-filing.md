# S1 round 3: pilots P-1, P-2, P-3 at the bench (lead, scratch, nothing committed)

Activation d528efb2, 2026-09-28 ≈09:00–09:40 PDT. The pilots are ruled in addendum S1-REPAIR-ROUTE-01-A1 §5.3 (`83-coldgate-pilot-ruling.md`).

**Setup:**
- Scratch worktree `JouleWise-wt-s1bench-d528efb2`, detached at `f0766620` (seat H3's commit on `fix/2026-09-28-s1-r3-H3`).
- The diff is `scratch.diff`. It contains:
  1. the three pilot IDs added to `PARITY_TEST_IDS`, and to `PARITY_SECOND_FORM_TEST_IDS`;
  2. `install_passing_analysis_whole_window` rewritten to A1 §4.3's text (label, template config, metadata, `rebind_config`, `write_passing_pair`), with the reference-replacement loop of `setUpClass` removed. There is only one such loop, covering both positions; A1 says "two loops";
  3. each pilot test wrapped in `exemption_parity(self.id())`;
  4. for P-3 only, the T4 build: each declared evidence root receives copies of the floor-member bundles `cell-1-*` from the class corpus. These are produced bundles, already bound and paired;
  5. a debug print (`BENCH_REASONS`) in P-1, used for the off-second-list reading.
- The harness is `pilot.sh`, with two plants: `plant_charging.py` writes a charging pair (`write_charging_pair`) onto every bundle the test module produces and onto the reference pairs; `plant_offsecond.py` empties the second list.
- A first attempt planted charging through the builder's battery runner. The controller itself then refused (`strict bundle run failed`), so the plant moved to after the bundles are produced.

| Pilot | Test | GREEN | Charging pair | Off the second list |
|---|---|---|---|---|
| **P-1** | `…AnalysisIntegrationTests.test_real_controller_unpinned_model_is_included_by_loader` | **OK**; `included`, no reasons | **RED**: `battery_float_confounded` (30 bundles) | **RED**: exactly the six reasons of A1 §3.2 (adapter_continuity_failed, cpu_admission_core_failed, environment_admission_failed, environment_admission_missing, whole_window_verdict_conflict, whole_window_verdict_provenance_invalid) |
| **P-2** | `…test_complete_strict_current_bundle_set_derives_deterministic_fail_closed_artifact_with_production_telemetry_identity` (25 sub-tests) | **OK** | **RED**: `battery_float_confounded` (30) | not required |
| **P-3** | `…test_claim_output_separation_preserves_declared_root_and_ignores_surplus_symlink` | **OK** after the T4 build. Before it: `missing required artifact: metadata.json` for `a10/cell-1-r0` | **RED**: `battery_float_confounded` (30) | **OK: the second switch is NOT needed.** Rule 10 applies: F IDs get the second switch only if rule 7 grants it. |

**Verdict: P-1, P-2 and P-3 all hold.** Stop condition 6a is not met. T5a proceeds to seat A under rules 7–9. F proceeds by the T4 rule, then the first form only, unless rule 7 grants the second.

**Owed before any ID is granted:**
- the rule 7 recorder on main's tree, which gives the second-switch IDs;
- the rule 9 coverage census (switched-on tests for `_current_core_rederivation_reasons`, one refusal and one acceptance);
- the T1 bench check;
- the confirmation of the remaining 5 rows of `test_mint_floor_artifact_generalized` and the T2/M rows.
