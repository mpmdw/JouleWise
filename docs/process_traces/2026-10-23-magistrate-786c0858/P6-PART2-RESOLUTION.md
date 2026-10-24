# BY-P6 phase A, part 2: origin/main merge resolution

Local build seat; synthetic checks only. Staging and committing remain lead-owned.

## Hunk resolutions

| Conflict | Lane / main | Resolution and authority |
|---|---|---|
| scripts/digest_pin_census.py, sole conflicting ERA_RECORDS hunk | Lane makes the block-5 inventory historical at /head with ^/files/; main adds the stricter inventory scope and registration era rules. | Keep the lane comment/rationale and main implementation: inventory ^/files/.+$, exact 682 literals; registration scopes 11 / 7 / 1. Keep all auto-merged ordinal literal pointers, scoped counts, zero-match checks, ancestor-of-HEAD validation, inventory/H_claim equality and seal-divergence warning. PR #576 makes this the reviewed superset of the lane behavior; P6 brief step 3 requires both. |
| configs/pins/registry.json, every conflicting registry hunk | Independently generated lane/main registries. | Select origin/main in full, then regenerate through scripts/repin.py --write registry. No manual JSON changes. P6 brief step 3 and the part-2 prompt require generation. |

PR #576 description read through the connected GitHub tool after gh could not reach api.github.com: https://github.com/mpmdw/JouleWise/pull/576. PR #565 confirmed the meter modules to exercise.

## Repin families

Regenerated: `registry`. Both initial and final checks passed all 16 families and named no stale family. Registry generation reported 35,893 literals in 3,096 files, with 23,538 checked Kind-P rows. The seal-divergence warning is expected under #576.

```sh
export TMPDIR=/private/tmp/by-p6/sol-part2-20261023 JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1
/opt/homebrew/bin/python3.13 -B scripts/repin.py --write registry
```

## Decisions I made

- Main's era rules subsume the lane's inventory rule; preserve the lane's rationale while retaining the reviewed stricter counts and safeguards.
- Use origin/main as the generated-registry seed and regenerate only registry; no stale family required any other writer.
- Make the six Git-fixture temp sites in the two allowed test files honor external TMPDIR, while retaining an outside-worktree fallback when TMPDIR points inside the checkout.
- Use JW_B5_B3W1_ROOT under the scratch root for the integration command so archived block-3 replay stays outside this synthetic-only run.

## Check and test tails

### repin

```sh
export TMPDIR=/private/tmp/by-p6/sol-part2-20261023 JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1
/opt/homebrew/bin/python3.13 -B scripts/repin.py --check
```

Observed exit: 0; pass. Log: `/private/tmp/by-p6/sol-part2-20261023/repin-final.log`.

```text
PASS 16 pin families current
```

### state

```sh
export TMPDIR=/private/tmp/by-p6/sol-part2-20261023 JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1
/opt/homebrew/bin/python3.13 -B scripts/gen_state.py --check
```

Observed exit: 0; pass. Log: `/private/tmp/by-p6/sol-part2-20261023/gen-state.log`.

```text
```

### plan_trees

```sh
export TMPDIR=/private/tmp/by-p6/sol-part2-20261023 JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1
/opt/homebrew/bin/python3.13 -B scripts/bytes_plan_trees.py --check
```

Observed exit: 0; pass. Log: `/private/tmp/by-p6/sol-part2-20261023/bytes-plan-trees.log`.

```text
verified 12 BYTES draft registrations and 12 fixed pass trees
```

### configs

```sh
export TMPDIR=/private/tmp/by-p6/sol-part2-20261023 JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1
/opt/homebrew/bin/python3.13 -B configs/campaigns/bytes_v1/generate_configs.py --check
```

Observed exit: 0; pass. Log: `/private/tmp/by-p6/sol-part2-20261023/bytes-configs.log`.

```text
verified 500 BYTES science configs (10 models x 50)
```

### refusals

```sh
export TMPDIR=/private/tmp/by-p6/sol-part2-20261023 JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1
/opt/homebrew/bin/python3.13 -B -m tests.hazards.refusal_census
```

Observed exit: 0; pass. Log: `/private/tmp/by-p6/sol-part2-20261023/refusal-census.log`.

```text
{
 "unlisted": [],
 "stale": [],
 "miscounted": [],
 "guard_changed": [],
 "scope_gaps": []
}
```

### agreement

```sh
export TMPDIR=/private/tmp/by-p6/sol-part2-20261023 JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1
/opt/homebrew/bin/python3.13 -B -m unittest tests.test_bytes_agreement
```

Observed exit: 0; pass. Log: `/private/tmp/by-p6/sol-part2-20261023/agreement.log`.

```text
Ran 39 tests in 659.643s
OK
```

### battery_variants

```sh
export TMPDIR=/private/tmp/by-p6/sol-part2-20261023 JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1
PYTHONPATH=. /opt/homebrew/bin/python3.13 -B /private/tmp/by-p6/sol-part2-20261023/part2-battery-agreement.py
```

Observed exit: 0; pass. Log: `/private/tmp/by-p6/sol-part2-20261023/battery-variants.log`.

```text
pass-1 battery variants: PASS (2 campaigns; 0 fields above the bar)
```

### hazards

```sh
export TMPDIR=/private/tmp/by-p6/sol-part2-20261023 JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1
/opt/homebrew/bin/python3.13 -B -m unittest discover -s tests/hazards -t .
```

Observed exit: 1; fail. Log: `/private/tmp/by-p6/sol-part2-20261023/hazards.log`.

```text
Ran 312 tests in 144.515s
FAILED (failures=27, skipped=9)
```

### integration

```sh
export TMPDIR=/private/tmp/by-p6/sol-part2-20261023 JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 JW_B5_B3W1_ROOT=/private/tmp/by-p6/sol-part2-20261023/no-local-archive
/opt/homebrew/bin/python3.13 -B -m unittest tests.test_harvest_b5_window tests.test_custody_durability tests.test_bundle tests.test_audit_bundle_validation tests.external.test_km003c_parse tests.test_harvest_b5_p3harv tests.external.test_km003c_monitor tests.b6.test_plan_inputs tests.test_b6_registration
```

Observed exit: 0; pass. Log: `/private/tmp/by-p6/sol-part2-20261023/integration.log`.

```text
Ran 415 tests in 707.876s
OK (skipped=11)
```

### pins

```sh
export TMPDIR=/private/tmp/by-p6/sol-part2-20261023 JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1
/opt/homebrew/bin/python3.13 -B -m unittest tests.test_repin tests.test_digest_pin_census
```

Observed exit: 0; pass. Log: `/private/tmp/by-p6/sol-part2-20261023/pin-tests.log`.

```text
Ran 59 tests in 122.436s
OK
```

### twin_coverage

```sh
export TMPDIR=/private/tmp/by-p6/sol-part2-20261023 JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1
/opt/homebrew/bin/python3.13 -B -m unittest tests.test_bytes_twin tests.test_bytes_coverage_map
```

Observed exit: 0; pass. Log: `/private/tmp/by-p6/sol-part2-20261023/twin-coverage.log`.

```text
Ran 93 tests in 813.451s
OK
```

### analysis.MarkerPassReasonTests

```sh
export TMPDIR=/private/tmp/by-p6/sol-part2-20261023 JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1
/opt/homebrew/bin/python3.13 -B -m unittest tests.test_bytes_analysis.MarkerPassReasonTests
```

Observed exit: 0; pass. Log: `/private/tmp/by-p6/sol-part2-20261023/analysis-MarkerPassReasonTests.log`.

```text
Ran 2 tests in 0.000s
OK
```

### analysis.H1WorkedExamples

```sh
export TMPDIR=/private/tmp/by-p6/sol-part2-20261023 JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1
/opt/homebrew/bin/python3.13 -B -m unittest tests.test_bytes_analysis.H1WorkedExamples
```

Observed exit: 0; pass. Log: `/private/tmp/by-p6/sol-part2-20261023/analysis-H1WorkedExamples.log`.

```text
Ran 6 tests in 0.001s
OK
```

### analysis.H2WorkedExamples

```sh
export TMPDIR=/private/tmp/by-p6/sol-part2-20261023 JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1
/opt/homebrew/bin/python3.13 -B -m unittest tests.test_bytes_analysis.H2WorkedExamples
```

Observed exit: 0; pass. Log: `/private/tmp/by-p6/sol-part2-20261023/analysis-H2WorkedExamples.log`.

```text
Ran 4 tests in 0.002s
OK
```

### analysis.MeterWorkedExamples

```sh
export TMPDIR=/private/tmp/by-p6/sol-part2-20261023 JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1
/opt/homebrew/bin/python3.13 -B -m unittest tests.test_bytes_analysis.MeterWorkedExamples
```

Observed exit: 0; pass. Log: `/private/tmp/by-p6/sol-part2-20261023/analysis-MeterWorkedExamples.log`.

```text
Ran 6 tests in 0.003s
OK
```

### analysis.BatteryRulingWorkedExamples

```sh
export TMPDIR=/private/tmp/by-p6/sol-part2-20261023 JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1
/opt/homebrew/bin/python3.13 -B -m unittest tests.test_bytes_analysis.BatteryRulingWorkedExamples
```

Observed exit: 0; pass. Log: `/private/tmp/by-p6/sol-part2-20261023/analysis-BatteryRulingWorkedExamples.log`.

```text
Ran 3 tests in 0.001s
OK
```

### analysis.RegisteredArithmeticTests

```sh
export TMPDIR=/private/tmp/by-p6/sol-part2-20261023 JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1
/opt/homebrew/bin/python3.13 -B -m unittest tests.test_bytes_analysis.RegisteredArithmeticTests
```

Observed exit: 0; pass. Log: `/private/tmp/by-p6/sol-part2-20261023/analysis-RegisteredArithmeticTests.log`.

```text
Ran 3 tests in 1.497s
OK
```

### analysis.BoundaryAndStagingTests

```sh
export TMPDIR=/private/tmp/by-p6/sol-part2-20261023 JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1
/opt/homebrew/bin/python3.13 -B -m unittest tests.test_bytes_analysis.BoundaryAndStagingTests
```

Observed exit: 0; pass. Log: `/private/tmp/by-p6/sol-part2-20261023/analysis-BoundaryAndStagingTests.log`.

```text
Ran 10 tests in 55.691s
OK
```

### analysis.ProductionArchiveTests

```sh
export TMPDIR=/private/tmp/by-p6/sol-part2-20261023 JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1
/opt/homebrew/bin/python3.13 -B -m unittest tests.test_bytes_analysis.ProductionArchiveTests
```

Observed exit: 0; pass. Log: `/private/tmp/by-p6/sol-part2-20261023/analysis-ProductionArchiveTests.log`.

```text
Ran 4 tests in 88.283s
OK
```

### analysis.CampaignWordRates

```sh
export TMPDIR=/private/tmp/by-p6/sol-part2-20261023 JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1
/opt/homebrew/bin/python3.13 -B -m unittest tests.test_bytes_analysis.CampaignWordRates
```

Observed exit: 0; pass. Log: `/private/tmp/by-p6/sol-part2-20261023/analysis-CampaignWordRates.log`.

```text
Ran 1 test in 861.258s
OK
```

### analysis.Addendum4RegressionTests

```sh
export TMPDIR=/private/tmp/by-p6/sol-part2-20261023 JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1
/opt/homebrew/bin/python3.13 -B -m unittest tests.test_bytes_analysis.Addendum4RegressionTests
```

Observed exit: 0; pass. Log: `/private/tmp/by-p6/sol-part2-20261023/analysis-Addendum4RegressionTests.log`.

```text
Ran 14 tests in 168.793s
OK
```

### analysis.Addendum7RegressionTests

```sh
export TMPDIR=/private/tmp/by-p6/sol-part2-20261023 JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1
/opt/homebrew/bin/python3.13 -B -m unittest tests.test_bytes_analysis.Addendum7RegressionTests
```

Observed exit: 0; pass. Log: `/private/tmp/by-p6/sol-part2-20261023/analysis-Addendum7RegressionTests.log`.

```text
Ran 13 tests in 21.095s
OK
```

### analysis.ReviewerProbeTests

```sh
export TMPDIR=/private/tmp/by-p6/sol-part2-20261023 JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1
/opt/homebrew/bin/python3.13 -B -m unittest tests.test_bytes_analysis.ReviewerProbeTests
```

Observed exit: 0; pass. Log: `/private/tmp/by-p6/sol-part2-20261023/analysis-ReviewerProbeTests.log`.

```text
Ran 1 test in 58.304s
OK
```

### analysis.Q1WithheldCensusTests

```sh
export TMPDIR=/private/tmp/by-p6/sol-part2-20261023 JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1
/opt/homebrew/bin/python3.13 -B -m unittest tests.test_bytes_analysis.Q1WithheldCensusTests
```

Observed exit: 0; pass. Log: `/private/tmp/by-p6/sol-part2-20261023/analysis-Q1WithheldCensusTests.log`.

```text
Ran 4 tests in 0.003s
OK
```

### analysis.SubsetReleaseChainTests

```sh
export TMPDIR=/private/tmp/by-p6/sol-part2-20261023 JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1
/opt/homebrew/bin/python3.13 -B -m unittest tests.test_bytes_analysis.SubsetReleaseChainTests
```

Observed exit: 0; pass. Log: `/private/tmp/by-p6/sol-part2-20261023/analysis-SubsetReleaseChainTests.log`.

```text
Ran 2 tests in 53.918s
OK
```

### analysis.Q1MissingFilesCLIChainTests

```sh
export TMPDIR=/private/tmp/by-p6/sol-part2-20261023 JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1
/opt/homebrew/bin/python3.13 -B -m unittest tests.test_bytes_analysis.Q1MissingFilesCLIChainTests
```

Observed exit: 0; pass. Log: `/private/tmp/by-p6/sol-part2-20261023/analysis-Q1MissingFilesCLIChainTests.log`.

```text
Ran 3 tests in 33.197s
OK
```

### analysis.Q2CommitmentCLIChainTests

```sh
export TMPDIR=/private/tmp/by-p6/sol-part2-20261023 JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1
/opt/homebrew/bin/python3.13 -B -m unittest tests.test_bytes_analysis.Q2CommitmentCLIChainTests
```

Observed exit: 0; pass. Log: `/private/tmp/by-p6/sol-part2-20261023/analysis-Q2CommitmentCLIChainTests.log`.

```text
Ran 1 test in 23.953s
OK
```

### analysis.BatteryCampaignTests

```sh
export TMPDIR=/private/tmp/by-p6/sol-part2-20261023 JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1
/opt/homebrew/bin/python3.13 -B -m unittest tests.test_bytes_analysis.BatteryCampaignTests
```

Observed exit: 0; pass. Log: `/private/tmp/by-p6/sol-part2-20261023/analysis-BatteryCampaignTests.log`.

```text
Ran 23 tests in 94.361s
OK
```

### analysis.ReviewInputTests

```sh
export TMPDIR=/private/tmp/by-p6/sol-part2-20261023 JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1
/opt/homebrew/bin/python3.13 -B -m unittest tests.test_bytes_analysis.ReviewInputTests
```

Observed exit: 0; pass. Log: `/private/tmp/by-p6/sol-part2-20261023/analysis-ReviewInputTests.log`.

```text
Ran 3 tests in 16.438s
OK
```

## Agreement campaigns

The 18-campaign charge is the 16 table-defined campaigns plus battery_instant and battery_delayed, as the part-1 handoff states. The part-1 replay script was copied under the TMPDIR root; only its JSON output destination changed, preserving the part-1 results.

| Campaign | Compared | Equal | Under bar | Above bar |
|---|---:|---:|---:|---:|
| bytes | 416077 | 408763 | 7314 | 0 |
| defects | 356117 | 349479 | 6638 | 0 |
| edge_locked | 346417 | 340119 | 6298 | 0 |
| marker_incomplete | 20540 | 18053 | 2487 | 0 |
| late_start | 220743 | 214983 | 5760 | 0 |
| empty_payload_n | 416077 | 408755 | 7322 | 0 |
| replayed_batch | 416077 | 408728 | 7349 | 0 |
| replayed_tail | 416077 | 408782 | 7295 | 0 |
| first_batch_tail_replayed | 416077 | 408764 | 7313 | 0 |
| minimum | 336000 | 329122 | 6878 | 0 |
| resident | 346417 | 340135 | 6282 | 0 |
| time | 346417 | 340056 | 6361 | 0 |
| polls_only | 20448 | 17943 | 2505 | 0 |
| header_closed | 20448 | 17958 | 2490 | 0 |
| invalid_anchor | 345937 | 339552 | 6385 | 0 |
| withheld | 286518 | 280570 | 5948 | 0 |
| battery_instant | 417517 | 410219 | 7298 | 0 |
| battery_delayed | 416077 | 408850 | 7227 | 0 |

18 campaign summaries recorded.

## Sandbox-only hazard failures

27 failed assertions across 21 test methods; 9 skips. The capture process-group census returns census_exit_3 / sysmond service not found / pgrep: Cannot get process list. This causes the instrument to refuse before later assertions, including the default Rig used by the import-graph test; the timeout test also cannot prove group_gone. A separate synthetic diagnostic confirmed both paths without changing production or test behavior.

| Test method | Failed assertions / subtests |
|---|---:|
| tests.hazards.test_arm.ArmTests.test_a_battery_current_that_starts_during_the_dwell_refuses_at_the_final_read | 1 |
| tests.hazards.test_arm.ArmTests.test_agent_that_starts_during_the_dwell_gets_no_go | 1 |
| tests.hazards.test_arm.ArmTests.test_charging_that_starts_during_the_dwell_refuses_at_the_final_read | 1 |
| tests.hazards.test_arm.ArmTests.test_clock_step_during_the_dwell_refuses | 1 |
| tests.hazards.test_arm.ArmTests.test_contending_daemon_times_the_dwell_out | 1 |
| tests.hazards.test_arm.ArmTests.test_frequency_word_change_at_the_end_of_the_dwell_refuses | 1 |
| tests.hazards.test_arm.ArmTests.test_go_records_a_clean_census_taken_after_the_final_reads | 1 |
| tests.hazards.test_arm.ArmTests.test_go_records_the_smc_current_beside_the_registry_cross_check | 1 |
| tests.hazards.test_arm.ArmTests.test_network_time_off_output_is_recorded_not_judged | 1 |
| tests.hazards.test_arm.ArmTests.test_quiet_float_mac_arms_go_in_the_registered_order | 1 |
| tests.hazards.test_arm.ArmTests.test_record_only_collectors_never_change_the_decision | 1 |
| tests.hazards.test_arm.ArmTests.test_unmeasured_refuses_at_arm_only_for_the_instrument | 5 |
| tests.hazards.test_arm.ArmTests.test_without_the_smc_the_arm_judges_the_registry_and_records_the_fallback | 1 |
| tests.hazards.test_arm_identity.ArmIdentityTests.test_empty_epoch_list_never_refuses | 1 |
| tests.hazards.test_arm_identity.ArmIdentityTests.test_failed_read_is_recorded_and_never_refuses | 3 |
| tests.hazards.test_arm_identity.ArmIdentityTests.test_judged_identity_proceeds_to_go | 1 |
| tests.hazards.test_arm_identity.ArmIdentityTests.test_no_expected_epochs_reads_no_identity | 1 |
| tests.hazards.test_import_graph.ImportGraphTests.test_a_complete_arm_and_monitor_run_load_no_retired_module | 1 |
| tests.hazards.test_instrument.CadenceProbeTests.test_block3_interactive_capture_at_130_ms_passes | 1 |
| tests.hazards.test_instrument.CadenceProbeTests.test_privilege_prefix_is_prepended_to_the_adapter_command | 1 |
| tests.hazards.test_instrument.ProductionCommandTests.test_timeout_kills_the_capture_group | 1 |

Diagnostic: `/private/tmp/by-p6/sol-part2-20261023/pgrep-diagnostic.log`.

## Registry reproducibility

A second generation after all source/test edits was byte-identical. No stale family or further writer was needed.

```text
Registry regeneration byte-identical: True
Registry SHA-256: e0384bf59b2272186a71e7da73c82fa76a9403eda486ac02a45c912328211da2
```

## Workspace and reducer

HEAD start: `9954864830f7643206d5e8d0ffb9b14cd33105d2`; HEAD end: `9954864830f7643206d5e8d0ffb9b14cd33105d2`.

origin/main: `e9aab7ba100a8401468bedcf2d61bd7e9df0ffac`.

`joulewise/reduce.py` is byte-identical to origin/main. SHA-256: `7b9c0d28869040229e113ea2d40ecc69966075fd34052fbb51cfaffbd9ff9fcc`.

Pre-existing paths changed by this session: `configs/pins/registry.json`, `scripts/digest_pin_census.py`, `tests/test_digest_pin_census.py`, `tests/test_repin.py`.

Unowned changes relative to initial snapshots: [].

Conflict markers removed; the two index entries remain unmerged until the lead stages them. No worktree staging or commit was attempted.

Full machine-readable commands and observations: `/private/tmp/by-p6/sol-part2-20261023/verification-full.json`.

## Next exact step

Lead reruns the listed hazard tests with process enumeration available, reviews and stages the four code/registry/test paths, and commits the pending merge. P6 brief steps 6-8 remain with the lead.
