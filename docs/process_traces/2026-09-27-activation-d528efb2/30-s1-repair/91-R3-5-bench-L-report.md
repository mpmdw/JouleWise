```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Bind + pair applied to the bench rows of six modules: 29 of 31 test IDs (38 of 40 outcomes) GREEN and RED under the charging pair; 2 IDs returned NEEDS_RULING (a pinned digest that bind + pair must move; a test whose own tamper now meets the gate first).",
  "workspace": {
    "base_requested": "cdfb27ce",
    "base_mode": "exact",
    "head_start": "cdfb27ce1396fa98f8d20963cfdbbe7675d6ad66",
    "head_end": "76711800",
    "upstream_end": "origin/fix/2026-09-28-s1-r3-L",
    "branch": "fix/2026-09-28-s1-r3-L"
  },
  "pathspec": [
    "tests/test_mint_floor_artifact.py",
    "tests/test_mint_floor_artifact_generalized.py",
    "tests/test_whole_window.py",
    "tests/test_launch_window.py"
  ],
  "unowned_dirty": [],
  "verdict": {"implementation": "partial", "acceptance": "needs_ruling"},
  "flags": [
    {
      "id": "F1", "kind": "lead_ruling", "level": "blocking",
      "text": "tests.test_mint_floor_artifact_generalized.V2PinsetAndMintTests.test_phase0_base_floor_bytes_are_pinned: the test pins SHA-256 5a244411… over the scenario's floor.json. Bound physical configs and pairs change every member's bundle and config digest, and so floor.json: new digest 9da51bb7…. Leaf diff against main (9eab16f8): 609 leaves changed, all SHA-256 strings (bundle_sha256 200, config_sha256 200, provenance bundle_sha256s 200, extraction_report.sha256 8, calibration_plan.sha256 1); no numeric leaf changed, no key added or removed. The refusing check is the test's own assertEqual on the pinned digest.",
      "needs": "A ruling to move the pin (A3's leaf-diff rule would admit it by the diff above), or another disposition. An assertion change is outside bind + pair."
    },
    {
      "id": "F2", "kind": "lead_ruling", "level": "blocking",
      "text": "tests.test_window_duration_margins.WindowDurationMarginsTests.test_member_config_mismatch_refuses_without_output: the bundle is already bound and paired in setUp. The test itself appends one byte to a member's config.json and expects the margins recorder's own member_config_mismatch refusal. Since the gate fix, the battery gate (joulewise.bundle_read.authenticate_window_members, called at window_duration_margins.py:950) refuses the unbound config first: WindowBatteryRefusal battery_float_evidence_missing (pair not bound (config.json digest does not match metadata.config_sha256)). Bind + pair cannot cure a test whose subject is the tamper.",
      "needs": "A ruling. Executed option (scratch probe, not committed): after the tamper, set metadata.config_sha256 to the new bytes' digest and write a passing pair; the gate then passes, the recorder refuses member_config_mismatch against the pack pin, GREEN; with a charging pair it is RED, battery_float_confounded. That changes the test body (not its assertion) and sets a digest by hand, so it is not the ruled class form. The other option is to assert the gate refusal (an assertion change)."
    },
    {
      "id": "F3", "kind": "lead_note", "level": "nonblocking",
      "text": "tests.test_launch_window.CeremonySkipConsumerTests.test_malformed_and_mismatched_lineage_codes_reach_every_consumer is on PARITY_TEST_IDS (T2) but goes GREEN by bind + pair alone, with no exemption_parity call. The first-form grant is unused by this ID (rule 10's spirit).",
      "needs": "The lead may withdraw it from PARITY_TEST_IDS in tests/bfgs_fixtures.py (outside this WRITE_SCOPE)."
    },
    {
      "id": "F4", "kind": "deviation", "level": "nonblocking",
      "text": "The process guard refuses a process start when any whitespace/shell-separated argv token has basename powermetrics, sudo or ioreg, not when the argv merely contains the substring. The literal substring rule blocked `git show HEAD:joulewise/adapters/powermetrics.py` 8 times in the first base run of test_mint_floor_artifact_generalized (logged); that run's results were discarded and the refined guard used for every run reported here. It still blocks `sudo -n /usr/bin/powermetrics`, `/usr/bin/powermetrics …`, `sh -c '…; sudo …'`, `ioreg -l` and os.posix_spawn/os.exec*/os.spawn*/os.system/os.popen equivalents (self-test executed). Its block log was empty after every reported run."
    },
    {
      "id": "F6", "kind": "environment", "level": "blocking",
      "text": "The P0 fence (06f93b87) cherry-pick, which the lieutenant permitted as one separate commit, was started in the L worktree. It conflicted only on import-adjacent lines in tests/test_run_campaign.py, tests/test_whole_window.py and tests/test_window_duration_margins.py. Those were resolved in the working tree by keeping both sides; all three files parse, and the resolved diff stat equals 06f93b87's (5 files, +580). Finishing the cherry-pick (stage + continue + message amend) was DENIED by the Claude Code auto-mode permission classifier ('Modify Shared Resources'). A following whole-module run of test_whole_window / test_window_duration_margins / test_sampler_launch_fence was also DENIED by the classifier. Neither was retried. The worktree is left MID-CHERRY-PICK: HEAD is 76711800; tests/sampler_launch_fence.py and tests/test_sampler_launch_fence.py are staged, and the three UU files are resolved but unstaged.",
      "needs": "The lieutenant or user either completes it (`git add` the three files, then `git cherry-pick --continue`) or runs `git cherry-pick --abort`. The whole-module runs of test_whole_window and test_window_duration_margins are still owed."
    },
    {
      "id": "F5", "kind": "cap", "level": "nonblocking",
      "text": "Condition 2 (cap 10 surprises): F1 and F2 were not marked NEEDS_RULING before seats started, so both count. With seat B's 3 (item 125) that is 5 of 10 by this report's count; seat A's re-run is not counted here. Conditions 8 and 9 are untouched: no ID was added to either parity list and no switch was used."
    }
  ]
}
```

# S1 round 3, bench rows "bind + pair" (P3, Opus 5.5 worker, 2026-09-28)

## What was done

The ruled form (addendum S1-REPAIR-ROUTE-01-A1 §5.2, class table row "bind + pair": bind first, then the pair, no switch, assertions byte-identical) was applied to every row that fails on `cdfb27ce` in the six modules item 122 gives to the lead's bench.

**The defect.** Rounds 1 and 2 already called `rebind_config` and then `write_passing_pair`, but on hand-written configs such as `{"run_id": …, "hardware_target": {"telemetry_backend": "powermetrics"}}`. Those are not a schema-valid `BenchmarkConfig`. Since the gate fix (`601a06c5`), a pair counts only under a config that re-validates, hashes to `metadata.config_sha256` and names a physical backend (`joulewise/bundle_read.py:511-543`). Every failing outcome in the six modules on `cdfb27ce` (40 outcomes, 31 IDs) refused with `battery_float_evidence_missing (pair not bound (config.json does not re-validate: schema_version must be a non-empty string))`. The one exception is the duration-margins row (F2).

**The repair (bind).** Each file gets a helper `_physical_config(config)`. It takes the physical template `tests/fixtures/d078_r01/config.json` (the template A1 §4.3 names for the T2 fixture form), clears the template's own tags, and lays the test's own `run_id`, `run_metadata` and `hardware_target` keys over it. The test's config is written through this helper. The existing `rebind_config` then binds it and sets the backend label, and the existing `write_passing_pair` writes the pair. Only fixture construction changed. No test body gained a switch, and no assertion line changed (`git diff -U0 | grep assert` is empty for every commit). The helper is duplicated per file because `tests/bfgs_fixtures.py` is outside this WRITE_SCOPE. The module-level/`setUpModule` areas of `test_whole_window.py` and `test_window_duration_margins.py` are untouched.

**The plant (RED).** `plant_run.py` replaces `write_passing_pair` with `bfgs_fixtures.write_charging_pair` in every loaded `tests.*` module that imported it. This is needed because the estimator and generalized IDs build their bundles through `tests.test_mint_floor_artifact` fixtures such as `_window_c_tree`. A first plant run replaced the name only in the target module; the generalized refusal-matrix ID then stayed green, because its bundles come from the other module. That run is superseded.

## Per module

| Module | IDs / outcomes failing on `cdfb27ce` | GREEN after bind + pair | Module run | Plant: RED with `battery_float_confounded` | Commit |
|---|---|---|---|---|---|
| `test_mint_floor_artifact` | 12 / 14 | 12 / 14 | 40 tests OK | 14 / 14 | `d79573bc` |
| `test_mint_floor_artifact_generalized` | 6 / 7 | 5 / 6 | 83 run: 80 ok, 2 skip, 1 fail (F1) | 7 / 7 | `1a2ab1d8` |
| `test_floor_mint_estimator` | 7 / 12 | 7 / 12 (no edit to this file; its fixtures come from the two minter modules) | 37 tests OK | 12 / 12 | none needed |
| `test_whole_window` (by ID only) | 3 / 3 | 3 / 3; all 9 IDs of `LaunchLineageWholeWindowTests` OK | not run whole (fence absent) | 3 / 3 | `a44f788f` |
| `test_launch_window` | 2 / 3 | 2 / 3 (no `exemption_parity`; F3) | 38 tests OK (594 s) | 3 / 3 | `76711800` |
| `test_window_duration_margins` (by ID only) | 1 / 1 | 0: NEEDS_RULING (F2) | not run whole (fence absent) | n/a (RED before and after) | none |
| **Total** | **31 / 40** | **29 / 38** | | **39 / 39** of the rows run | |

### IDs (prefix `tests.`)

`test_mint_floor_artifact` (all GREEN, all RED under the plant):
- `AuthenticationTests.test_allowance_must_be_derivable_and_contain_metric_family` (2 sub-tests)
- `AuthenticationTests.test_allowance_rederivation_reasserts_campaign_log_custody`
- `AuthenticationTests.test_authenticated_replay_does_not_import_prefill_refusal`
- `AuthenticationTests.test_authenticated_replay_rejects_unrecorded_target_envelope`
- `AuthenticationTests.test_missing_report_semantics_is_not_guessed`
- `AuthenticationTests.test_no_argument_mint_consumer_does_not_infer_salvage_dispatch`
- `AuthenticationTests.test_report_spec_and_source_bytes_authenticate_before_gate`
- `AuthenticationTests.test_substituted_comparative_allowance_is_rejected` (2 sub-tests)
- `BinderTests.test_b4_cache_free_rebinding_preserves_stored_salvage_semantics`
- `BinderTests.test_binder_accepts_production_window_with_window_a_plan`
- `BinderTests.test_binder_rejects_source_byte_substitution`
- `BinderTests.test_missing_evidence_root_mapping_fails`

`test_mint_floor_artifact_generalized`:
- `FullPathTests.test_binding_and_exclusive_write_refuse_at_full_path`: GREEN / RED
- `FullPathTests.test_mint1_full_path_is_byte_identical_to_review_pinned_mint_core`: GREEN / RED
- `FullPathTests.test_truthful_7b_fixture_mints_through_full_path`: GREEN / RED
- `V2PinsetAndMintTests.test_common_mode_full_cli_path_writes_bound_exact_artifact`: GREEN / RED
- `V2PinsetAndMintTests.test_default_authentication_seam_refusal_matrix_is_closed_and_identical` (sub-tests `semantics`, `one_ulp`): GREEN / RED. It is cured by the `test_mint_floor_artifact` edit, whose `_window_c_tree` builds its bundles.
- `V2PinsetAndMintTests.test_phase0_base_floor_bytes_are_pinned`: **NEEDS_RULING (F1)**. It reaches the gate and passes it; it fails only on the pinned digest. It is RED (`battery_float_confounded`) under the plant.

`test_floor_mint_estimator` (all GREEN, all RED): `BinderTests.test_actual_core_absolute_width_attack_fails_pre_fix_control`, `…test_actual_core_common_mode_bind_completes_and_returns_strict_hashes`, `…test_actual_core_comparative_hash_attack_fails_pre_fix_control`, `…test_actual_pinned_binder_refusal_gates_run_on_common_mode_copy` (6 sub-tests), `…test_default_binding_is_exactly_the_pinned_binder`, `…test_default_binding_retains_pinned_one_e_minus_twelve_tolerance`, `…test_post_131_stack_unavailable_and_both_roots_refuse`.

`test_whole_window` (all GREEN, all RED): `LaunchLineageWholeWindowTests.test_neg8_bound_authenticates_every_member_and_seals_full_lineage`, `…test_neg8_bound_refuses_marker_without_direct_receipts`, `…test_neg8_bound_refuses_mixed_full_lineages`. The bind sits in `_write_neg8_corpus`, which only these three call, and not in the module-wide `_evidence_bundle`.

`test_launch_window` (all GREEN, all RED): `CeremonySkipConsumerTests.test_analysis_input_refuses_missing_launch_consumption`, `…test_malformed_and_mismatched_lineage_codes_reach_every_consumer` (sub-tests `analysis` × 2 codes). The bind sits in the class's `setUp`. All 5 tests of the class are OK.

`test_window_duration_margins`: `WindowDurationMarginsTests.test_member_config_mismatch_refuses_without_output`: **NEEDS_RULING (F2)**.

## Stop rules (i)–(v) and rules 1–11

- (i) No production file was edited. No injection point or environment hook was added.
- (ii) No run ID was added to the historical set.
- (iii) No historical bundle was copied or exempted.
- (iv) Only the four committed test files changed, all inside the WRITE_SCOPE.
- (v) Every pair is written by `write_passing_pair`/`write_charging_pair` after `rebind_config`. Their `_bound_nonmock` check refuses an unbound or mock config, and none refused.
- No `exemption_parity` was used, and no ID was added to either list.
- The only stand-ins are the tests' own pre-existing ones.

## Commands (worktree `/Users/edr/code/JouleWise-wt-s1r3-L-d528efb2`; `S=…/scratchpad/p3`)

- Guard: `PYTHONPATH=$S/guard` (`sitecustomize.py`, sha256 prefix `98e991a1`), `TMPDIR=$S/tmp/`, `/opt/homebrew/bin/python3 -B`, stdin closed.
- Module runs: `python3 -B 30-s1-repair/run_module_ids.py tests.<module> $S/{base,after}/<module>.json`. The base run is at `cdfb27ce`, the after run at the commit.
- By-ID runs (whole_window, duration margins): `python3 -B -m unittest <ids>` and `python3 -B $S/plant_run.py --green tests.test_whole_window <ids-file> …`.
- Plant: `python3 -B $S/plant_run.py tests.<module> $S/<module>.ids $S/after/<module>.plant.json` (sha256 prefix `5ed4f32e`). The JSON has per-outcome `battery_reasons` and the last line of the traceback.
- F1 evidence: `$S/dump_phase0.py` was run in a detached main worktree `/Users/edr/code/JouleWise-wt-p3main-opus0928` (`9eab16f8`, read-only use) and on the L head. Outputs: `$S/after/phase0-floor-{main,L}.json` and the leaf diff `$S/after/phase0-leafdiff.txt`.
- F2 evidence: `$S/probe_wdm_rebound_tamper.py` (GREEN) and `--charging` (RED, `battery_float_confounded`). Logs: `$S/after/probe_wdm*.log`.

## Not done / not run

- `test_whole_window` and `test_window_duration_margins` were not run as whole modules. The fence was absent during the work. When it arrived, the cherry-pick could not be finished and the whole-module run was refused by the permission classifier (F6). Only the IDs above were run, under the guard.
- `test_run_campaign` is not in this scope.
- The full suite was not run.
