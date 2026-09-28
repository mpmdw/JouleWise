# S1 R3-2 triage: the lead's confirmation (in progress)

Activation d528efb2, 2026-09-28 ≈03:25 PDT. The script's proposal is `table-proposal.md`: 164 outcomes on the integration tree `0c469057`, classified against main's tree (`e7c8bcc6`, code-identical to `9eab16f8`). This note records the lead's readings so far. A row stays unconfirmed until it is named here.

## Confirmed readings

1. **Paper supply-map pin outcomes: 23 rows, outside the cap.** `test_paper_custody` 16, `test_paper_rendering` 6, `test_paper_reported_energy` 1. The error is "stale supply-map receipt digest: reported_energy_parents / d165_closeout". These are the G9 outcomes the ruling repins at step 5 (S1-REGRESSION-01 §5; A3 R2-5). No seat touches them.

2. **Gate-fix "pair not bound" rows: 37 rows, class "bind + pair".** They are the 44 IDs the gate fix turned, less the rows listed in item 3 and the three NEW rows. The script marked them NOBUNDLE because on main these tests never reach `custody_telemetry_identity`. On the candidate they now fail with `battery_float_evidence_missing (pair not bound (config.json does not re-validate / digest …))`. The round-1 and round-2 repairs wrote a pair into bundles whose `config.json` is not digest-bound to `metadata.config_sha256`. Before the gate fix that was invisible; after it, correctly refused. The modules and counts:
   - `test_mint_floor_artifact` 14;
   - `test_floor_mint_estimator` 11–12;
   - `test_mint_floor_artifact_generalized` 2 of 7 so far (the other 5 are still to be read);
   - `test_whole_window` 3;
   - `test_launch_window` 3;
   - `test_window_duration_margins` 1.

   **Repair (T1 form, no parity):** bind first (helper H `rebind_config`), then `write_passing_pair`; assertions byte-identical. This is the §4.3 cure ("the bundle that is meant to pass is built with a bound config"). Two of those files are §E-excluded minter files (`test_mint_floor_artifact*.py`). Only fixture construction may change there, which this is.

3. **Rows that were environmental (confirmed): both PASS when re-run alone on `0c469057` under the guard (03:30 PDT), so they are load flakes and outside the repair:**
   - `test_night_gate` (`'?? partial.py' not found in ''`): a git-status assertion; the integration tree may differ from a clean checkout.
   - `test_arm_readiness_lifecycle…race…`: a concurrency test that also failed in the D-138 census under load.

4. **NEW (3):** S1's own `test_bfgs_window_consumers` rows named in §4.3 (`test_passing_pair_returns_verdict`, `test_recorded_member_digests_precede_status_refusals`, `test_aggregate_authenticates_failed_member_before_numbers`). Repair: build the passing bundle with `real=True` (or bind the fixture), assertions byte-identical (ruling §4.3). Seat H3's scope covers this file.

## Still to confirm (next activation)

- **T5 (57, all `test_analysis_integration`):** the class the ruling calls unproven. Its pilot (R3-3) decides whether seat H3 needs the replay keyword.
- **T2 (33):** confirm that none has a mock-refusal subject (T3). Candidates by name: none flagged by the script.
- **T6 (5, `test_analysis_integration`):** mixed exempt; NEEDS_RULING under the cap.
- **T1 (3):** pair alone.
- The remaining 5 rows of `test_mint_floor_artifact_generalized`.

Then R3-3, the pilot: one each of T2, T4 (or "bind + pair"), and T5 in scratch, each with the planted "charging pair" turning it RED.

## Confirmed at the bench, 2026-09-28 ≈09:45–10:30 PDT (activation d528efb2, items 120–121)

5. **T2 (29 test IDs, 33 outcomes): confirmed T2, none T3.** An AST scan of each test body finds no mention of mock telemetry, mock configs, `production_predicate`, exemption or `telemetry_claim_ineligible`. The ID list is `87-bench-rules/t2-ids.txt`.
6. **T1, `test_floor_cpu_ledger_rejects_duplicates_reordering_mismatch_and_absence`: stays T1.** In scratch, the fixture's final bundle gets `run_id` plus `write_passing_pair`, and the test is GREEN. With the charging pair it is RED (`environment_admission_missing`; the floor's CPU-admission check does not admit a bundle whose pair fails).
7. **The remaining rows of `test_mint_floor_artifact_generalized` (6 IDs, 7 outcomes) are bind + pair.** On the candidate `f0766620` every one fails with `battery_float_evidence_missing (pair not bound (config.json does not re-validate: schema_version must be a non-empty string))`.
8. **Rule 7, second-switch eligibility.** On main's tree (`e7c8bcc6`), a recorder logged every answer of `_current_strict_summary` for the 7 T5a and 4 F IDs (`87-bench-rules/rule7-*`). The answer was **False for every bundle, in all 11 tests** (214–642 calls each). All 11 are eligible under rule 7.
9. **Rule 8 (never the test's own subject).** An AST scan of each test and the class methods it calls finds no function on the second-form list and no reason that only the second form's right-hand branch can raise. There is one exception: `test_incomplete_pair_is_listed_and_never_converted_to_unpaired_samples_with_production_telemetry_identity` patches `joulewise.analysis_engine.inputs.AuthenticatedConsumptionSession`, the class whose `_prepare` is on the list. **It is withheld from the second list (conservative).** It gets the first form only; if it stays RED, it goes to the per-ID gate.
10. **Rule 10.** P-3 (an F ID) passes without the second switch, so F IDs get the first form only unless seat A shows a need. Rule 7 already allows all four, so the lead can grant quickly.
