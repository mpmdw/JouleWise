# BY-P6 phase B: battery-term integration and B2

Worktree HEAD at intake: `bb78384c2c92009a48085cd6376ea09d3bfbc850`.
Pending merge: `cf960e97e3f7a9b7bae97a5b0f2a274362828cf1` (#573).
The lead stages and commits; the worker does not mutate the worktree index.
All temporary fixtures, logs and scratch repositories are under
`/private/tmp/by-p6b/run-20261024`. No measurement or archive write is performed.

M0: no active stop card or global selection gate; this explicit [AGENT]
phase-B delegation supplies the task and authority. Generated state and queue
files remain lead-owned. The overall brief, phase-A resolutions, P0 rulings,
registration and both PR descriptions were read. `gh pr view` could not reach
api.github.com; the connected GitHub reader supplied both current descriptions.

## Hunk table with authority

Hunk numbers refer to the original conflict blocks saved in scratch at intake.

| File | Hunk | Both sides and resolution | Authority |
| --- | ---: | --- | --- |
| `joulewise/bytes_analysis.py` | 1 | Keep phase A's explanatory F15 comment; #573 has no replacement text. Keep all compatible restore wrappers and the exported-status check from the automatic merge. | #574 F15; #573 rounds e–i storage rule |
| `joulewise/external/km003c_parse.py` | 1 | Keep both imports: phase A's Student-t helper and #573's compressed-byte reader. `load` retains #573's reader; samples and clock-fit arithmetic remain phase A's native authority. | #573 F4; #574 round d/e; phase-B explicit reader ruling |
| `scripts/bytes_twin.py` | 1 | Keep `common` on too-few-fit-points return, preserving #574's current/voltage arrays, poll interval and independent alignment state. | #574 native parity; phase-A combined BAT-2 ruling |
| same | 2 | Keep `common` on successful parsing for the same reason. Remove the older duplicate `timing` construction introduced by the automatic merge. | #574 round d/e |
| same | 3 | Keep integer-nanosecond `battery_terms` and nullable current-only marker, replacing #573's older floating-window battery functions. | #574 integer windows; BAT-2 §4; phase-A combined ruling |
| same | 4 | Keep phase-A join, missing-bundle/span reasons, selected-stream and marker fallback logic; wrap `member_spans` in #573's independent `_readable_bundle`. | #574 parity/reasons; #573 restore-or-stop |
| same | 5 | Keep phase-A join's edge and offset calculations. | #574/Addendum 9; no additional arithmetic change |
| same | 6 | Keep phase-A request energy, idle terms, marker reasons and evaluated-stream fallback. | #574; BAT-2 §4; phase A |
| same | 7 | Keep invalid-energy gate; discard obsolete `_decode_battery_assist` selector. | #574 F15; phase-A decoded marker representation |
| same | 8 | Keep phase-A per-selection estimator, flags and evaluated-marker counts. | #574 coverage/parity; BAT-2 diagnostic |
| same | 9 | Keep phase-A per-selection without-assisted calculation and reasons. | #574 and phase-A combined semantics |
| same | 10 | Keep phase-A withheld-store argument and blinded-stage disclosure; add #573's independent `StorageStop` catch before `Exception`. | #574 B4/staging; #573 rounds g–i |
| `tests/test_bytes_agreement.py` | 1 | Keep all 16 phase-A campaigns and add #573's compressed campaign in the five-component tuple format. The two extra phase-A battery variants remain separate replays. | #574 complete coverage; #573 F4 |
| same | 2 | Keep both named validity-failure fixture forms. | Both PRs' F15 regressions |
| same | 3 | Keep truncation and withheld-store fixtures plus real compression after export. | #574 marker/B4; #573 storage campaign |
| same | 4 | Keep whole-sample flip oracle and all five compressed refusal variants. | Addendum 9; #573 rounds c–i |
| same | 5 | Keep #573's nine-repeat validity assertion and phase-A fit/heldout diagnostic expectation. Blinded diagnostics stay not evaluated. | #573 unresolved anchor fixture; #574 stage/reason rules |
| `tests/test_bytes_twin.py` | 1 | Keep phase-A quantity test base and #573's four closed-form battery examples; adapt only their fixture representation/call names to `battery_terms`. All scientific expected values are unchanged. | Both reviewed PRs; no new tolerance |
| same | 2 | Keep #573's seven independent storage-reader cases and phase-A meter test base. | #573 F4/c–i; #574 tests |
| same | 3 | Keep both harvest-assist disclosure and decode-assist count assertions using phase A's per-selection shape. | BAT-2: harvest flag discloses, decoded current selects |

The automatic merge also inserted #573's obsolete battery code around the
twin conflict blocks. Whole reviewed phase-A functions (`parse_meter_stream`,
`dc_join`, `_kept`, `compute_cell`) were retained, then the independent custody
wrapper was applied at the read seam. No scientific arithmetic is newly chosen.
The twin imports only standard-library modules and owns its `StorageStop(BaseException)`.

The output-field inventory includes the compressed campaign and an explicit
provenance exemption for `predictions.json/desk_restore_sha256`, with the
existing exact source-digest regression cited. New numerical fields are not
exempted. Appendix A follows #573's new DISCLOSE entry: 204 disclose-only,
41 member-excluding and 19 session-excluding codes; exclusion effects do not change.

## Decisions I made

- Applied the PRs as a compatible union: native samples/fit points and independent
  twin arithmetic from #574; verified restore-or-stop behavior from #573.
- Retained integer marker windows, current-only nullable evaluation and pass-specific
  reasons from phase A. No threshold, bar, unit membership or estimator method is new.
- Kept #573's additional unresolved-anchor fixture in the defects campaign and
  all storage refusal variants; adapted older test data structures to the retained API.
- Treated the restore source digest as provenance, with its exact primary-only
  test, rather than requiring the independent twin to import production restore code.
- Applied P0 ruling 9 as amended to §1, §18 and §19: the known-bytes test is after
  pass-1 collection, before stage-1 unblinding, in its own non-claim checkout.
- Replaced the stale pending generator/revision note using the current generator
  and its successful exact-byte check. C4 runtime/frozen projection evidence is separate.

The execution evidence and prospective scope request follow.

## Execution evidence

Safety environment for every test/check process: `TMPDIR=/private/tmp/by-p6b/run-20261024 JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1`; interpreter `/opt/homebrew/bin/python3.13 -B`. No whole suite, cold-pass FullRoundTests, measurement, launchctl, install or arming was run. Raw evidence remains read-only.

The first agreement run covered 45 tests, all 17 table-defined campaigns and all five compressed refusal variants. It had one test-seam error: the unreadable-stream mock denied unrelated custody reads that #573 now propagates. The mock now targets only the meter file; all 16 marker-path tests passed on rerun. A complete 45-test agreement rerun is also recorded below. The two additional phase-A battery variants supply the 19-campaign total. Under-bar differences are not classified.

| Run | Exact observed tail | Disposition |
| --- | --- | --- |
| `agreement-final` | `----------------------------------------------------------------------; Ran 45 tests in 488.711s; ; OK` | PASS |
| `agreement-marker-rerun` | `----------------------------------------------------------------------; Ran 16 tests in 0.077s; ; OK` | PASS |
| `twin` | `----------------------------------------------------------------------; Ran 98 tests in 27.809s; ; OK` | PASS |
| `focused` | `----------------------------------------------------------------------; Ran 310 tests in 1263.976s; ; FAILED (errors=1, skipped=10)` | FAIL |
| `analysis` | `----------------------------------------------------------------------; Ran 106 tests in 1355.108s; ; OK` | PASS |
| `native-storage` | `----------------------------------------------------------------------; Ran 52 tests in 192.250s; ; OK` | PASS |
| `registration-prose` | `----------------------------------------------------------------------; Ran 1 test in 0.001s; ; OK` | PASS |
| `fix573i-fixture-diagnostic` | `----------------------------------------------------------------------; Ran 1 test in 0.001s; ; OK` | PASS |

The focused run covers `tests.test_bytes_coverage_map`, `tests.test_bytes_gates`, `tests.b6.test_bytes_packs`, `tests.test_b6_registration`, `tests.b6.test_plan_inputs`, all four `tests.test_fix573[fghi]_restore` modules, `tests.test_restore_run_to_scratch` and `tests.test_harvest_b5_window`. The primary analysis module includes its conditional 400-draw/world coverage and its separate 60 native synthetic campaigns. Native/storage covers `tests.external.test_km003c_parse` and `tests.test_desk_compressed_readers`. Exact commands and logs are retained in the scratch root and machine-readable verification record.

| Check | Tail / result |
| --- | --- |
| `repin-post-b2` | `  scripts/run_campaign.py;   scripts/run_night.py;   scripts/test_timings.json;   scripts/validate_powermetrics_fiducial.py; PASS 16 pin families current` |
| `state` | `(no output; exit 0)` |
| `plan-trees-initial` | `verified 12 BYTES draft registrations and 12 fixed pass trees` |
| `configs` | `verified 500 BYTES science configs (10 models x 50)` |
| `refusal-census` | ` "stale": [],;  "miscounted": [],;  "guard_changed": [],;  "scope_gaps": []; }` |

`git diff --check`: exit 0. The named pin check prints the existing sealed-inventory divergence warning; it still reports `PASS 16 pin families current`. No pin was rewritten by hand. Scientific parser, marker and estimator function ASTs are identical to phase A (scratch `arithmetic-audit.json`); `joulewise/reduce.py` is byte-identical to origin/main at SHA-256 `7b9c0d28869040229e113ea2d40ecc69966075fd34052fbb51cfaffbd9ff9fcc`.

### Agreement per campaign

| Campaign | Compared | Equal | Under bar | Above bar |
| --- | ---: | ---: | ---: | ---: |
| `bytes` | 416077 | 408793 | 7284 | 0 |
| `compressed` | 346417 | 340014 | 6403 | 0 |
| `defects` | 355637 | 349026 | 6611 | 0 |
| `edge_locked` | 346417 | 340166 | 6251 | 0 |
| `marker_incomplete` | 20540 | 18176 | 2364 | 0 |
| `late_start` | 220743 | 214881 | 5862 | 0 |
| `empty_payload_n` | 416077 | 408795 | 7282 | 0 |
| `replayed_batch` | 416077 | 408765 | 7312 | 0 |
| `replayed_tail` | 416077 | 408681 | 7396 | 0 |
| `first_batch_tail_replayed` | 416077 | 408849 | 7228 | 0 |
| `minimum` | 336000 | 329116 | 6884 | 0 |
| `resident` | 346417 | 340162 | 6255 | 0 |
| `time` | 346417 | 339968 | 6449 | 0 |
| `polls_only` | 20448 | 17970 | 2478 | 0 |
| `header_closed` | 20448 | 18129 | 2319 | 0 |
| `invalid_anchor` | 345937 | 339555 | 6382 | 0 |
| `withheld` | 286518 | 280642 | 5876 | 0 |
| `battery_instant` | 417517 | 410231 | 7286 | 0 |
| `battery_delayed` | 416077 | 408784 | 7293 | 0 |

Compressed variants: truncated events frame, flipped metadata frame, compressed non-JSON metadata, short scratch reserve and missing custody journal all terminate both programs with named `restore_refused` causes and no output verdict/prediction. No above-bar attribution is required. The defects campaign retains #573's extra invalid-anchor repeat (nine kept repeats in that cell).

### Real-archive parser parity

Every row compares actual fit endpoints, coefficients/statistics, poll times, selected SMC view and marker windows/inputs. Native/twin full samples and the primary's exact selected samples plus edge neighbours agree. The changed native `load` also equals the pre-#573 plain-text read semantics on all four files. Each file was only read.

| Stream | Native / primary / twin fit points | Polls | Marker windows / SMC observations | Full / selected primary samples | Differences |
| --- | --- | ---: | --- | --- | ---: |
| h-20261021T185555Z custody | 93532 / 93532 / 93532 | 93533 | 95 / 7598 | 935345 / 467975 | 0 |
| h-20261021T185555Z archive | 93532 / 93532 / 93532 | 93533 | 95 / 7598 | 935345 / 467975 | 0 |
| h2-20261023T144711Z custody | 76115 / 76115 / 76115 | 76116 | 73 / 5683 | 761159 / 365413 | 0 |
| h2-20261023T144711Z archive | 76115 / 76115 / 76115 | 76116 | 73 / 5683 | 761159 / 365413 | 0 |

Exact source-file SHA-256 (custody and archive copies match): H `009d0e688678cb4c887f42e5007dbb671772ce78b5607b011014d23db3417389`; BY-H2 `b94f5fe67649f3a5755f0663ddedba7f1b69097a21dbada365c7c77db484651a`. Full fit-point, poll, sample and marker-input digests are in `P6-PHASE-B-ARCHIVE-PARITY.json`. Tail: `REAL PARITY: 4 streams; 0 differences`.

### B2 SHA and 400-draw coverage

`joulewise/bytes_analysis.py`: **`94e9c9f86297bad4883ba0347be3d9feb05f847ce4f22dce41cd944ee800b56b`**. §13 records this exact agreeing digest; §9 reproduces the following counts and fractions. The generator and all estimator versions remain unchanged pending the scope request below; every pack remains draft.

| World | Boundary | Fit | HC3 95% | OLS 95% | HC3 ruled-k | OLS ruled-k | k |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| bytes | rails | simple | 388/400 (0.9700) | 387/400 (0.9675) | 397/400 (0.9925) | 395/400 (0.9875) | 9 |
| bytes | rails | extended | 394/400 (0.9850) | 397/400 (0.9925) | 400/400 (1.0000) | 399/400 (0.9975) | 9 |
| bytes | DC input | simple | 388/400 (0.9700) | 387/400 (0.9675) | 397/400 (0.9925) | 395/400 (0.9875) | 9 |
| bytes | DC input | extended | 394/400 (0.9850) | 397/400 (0.9925) | 400/400 (1.0000) | 399/400 (0.9975) | 9 |
| bytes | rest | simple | 388/400 (0.9700) | 387/400 (0.9675) | 397/400 (0.9925) | 397/400 (0.9925) | 11 |
| bytes | rest | extended | 394/400 (0.9850) | 397/400 (0.9925) | 400/400 (1.0000) | 399/400 (0.9975) | 11 |
| time | rails | simple | 377/400 (0.9425) | 380/400 (0.9500) | 397/400 (0.9925) | 397/400 (0.9925) | 9 |
| time | rails | extended | 389/400 (0.9725) | 381/400 (0.9525) | 398/400 (0.9950) | 399/400 (0.9975) | 9 |
| time | DC input | simple | 377/400 (0.9425) | 380/400 (0.9500) | 397/400 (0.9925) | 397/400 (0.9925) | 9 |
| time | DC input | extended | 389/400 (0.9725) | 381/400 (0.9525) | 398/400 (0.9950) | 399/400 (0.9975) | 9 |
| time | rest | simple | 377/400 (0.9425) | 380/400 (0.9500) | 398/400 (0.9950) | 397/400 (0.9925) | 11 |
| time | rest | extended | 389/400 (0.9725) | 381/400 (0.9525) | 398/400 (0.9950) | 399/400 (0.9975) | 11 |
| resident | rails | simple | 400/400 (1.0000) | 400/400 (1.0000) | 400/400 (1.0000) | 400/400 (1.0000) | 9 |
| resident | rails | extended | 399/400 (0.9975) | 321/400 (0.8025) | 400/400 (1.0000) | 395/400 (0.9875) | 9 |
| resident | DC input | simple | 400/400 (1.0000) | 400/400 (1.0000) | 400/400 (1.0000) | 400/400 (1.0000) | 9 |
| resident | DC input | extended | 399/400 (0.9975) | 321/400 (0.8025) | 400/400 (1.0000) | 395/400 (0.9875) | 9 |
| resident | rest | simple | 400/400 (1.0000) | 400/400 (1.0000) | 400/400 (1.0000) | 400/400 (1.0000) | 11 |
| resident | rest | extended | 399/400 (0.9975) | 321/400 (0.8025) | 400/400 (1.0000) | 396/400 (0.9900) | 11 |

Minimum HC3 plain-95% is **377/400 = 0.9425**, so the registered 0.93 floor does not fire. The table is the executed conditional p03 redraw diagnostic, not a live-hardware or native-offset coverage claim.

### Hazard environment failures

`tests/hazards`: `Ran 312 tests in 125.204s`; `FAILED (failures=27, skipped=9)`. All 21 failing method IDs (27 subtest/failure entries) exactly match phase A's recorded environment failures. `/usr/bin/pgrep` independently exits 3 with `sysmon request failed with error: sysmond service not found` and `pgrep: Cannot get process list`. The instrument refuses because it cannot prove the fixture capture process group absent, preventing later fake arm stages. No safety check was shimmed or bypassed. The lead must rerun these tests where process enumeration works.

| Method | Failure entries |
| --- | ---: |
| `tests.hazards.test_arm.ArmTests.test_a_battery_current_that_starts_during_the_dwell_refuses_at_the_final_read` | 1 |
| `tests.hazards.test_arm.ArmTests.test_agent_that_starts_during_the_dwell_gets_no_go` | 1 |
| `tests.hazards.test_arm.ArmTests.test_charging_that_starts_during_the_dwell_refuses_at_the_final_read` | 1 |
| `tests.hazards.test_arm.ArmTests.test_clock_step_during_the_dwell_refuses` | 1 |
| `tests.hazards.test_arm.ArmTests.test_contending_daemon_times_the_dwell_out` | 1 |
| `tests.hazards.test_arm.ArmTests.test_frequency_word_change_at_the_end_of_the_dwell_refuses` | 1 |
| `tests.hazards.test_arm.ArmTests.test_go_records_a_clean_census_taken_after_the_final_reads` | 1 |
| `tests.hazards.test_arm.ArmTests.test_go_records_the_smc_current_beside_the_registry_cross_check` | 1 |
| `tests.hazards.test_arm.ArmTests.test_network_time_off_output_is_recorded_not_judged` | 1 |
| `tests.hazards.test_arm.ArmTests.test_quiet_float_mac_arms_go_in_the_registered_order` | 1 |
| `tests.hazards.test_arm.ArmTests.test_record_only_collectors_never_change_the_decision` | 1 |
| `tests.hazards.test_arm.ArmTests.test_unmeasured_refuses_at_arm_only_for_the_instrument` | 5 |
| `tests.hazards.test_arm.ArmTests.test_without_the_smc_the_arm_judges_the_registry_and_records_the_fallback` | 1 |
| `tests.hazards.test_arm_identity.ArmIdentityTests.test_empty_epoch_list_never_refuses` | 1 |
| `tests.hazards.test_arm_identity.ArmIdentityTests.test_failed_read_is_recorded_and_never_refuses` | 3 |
| `tests.hazards.test_arm_identity.ArmIdentityTests.test_judged_identity_proceeds_to_go` | 1 |
| `tests.hazards.test_arm_identity.ArmIdentityTests.test_no_expected_epochs_reads_no_identity` | 1 |
| `tests.hazards.test_import_graph.ImportGraphTests.test_a_complete_arm_and_monitor_run_load_no_retired_module` | 1 |
| `tests.hazards.test_instrument.CadenceProbeTests.test_block3_interactive_capture_at_130_ms_passes` | 1 |
| `tests.hazards.test_instrument.CadenceProbeTests.test_privilege_prefix_is_prepended_to_the_adapter_command` | 1 |
| `tests.hazards.test_instrument.ProductionCommandTests.test_timeout_kills_the_capture_group` | 1 |

## Remaining slots and NEEDS_SCOPE

- **C4 runtime/identity projections** (§5/§18): final executed interpreter, tokenizer, quantization/runtime stack and frozen projection receipts remain unobserved. File identities and launch declarations do not satisfy that slot; BY-PIN owns it.
- **Known-bytes stream outcome** (§1/§18): required quiet-Mac measurement in its own non-claim checkout, after pass-1 collection and before stage-1 unblinding, per P0 ruling 9 as amended. No live result is invented.
- **B2 estimator-version propagation** (§13/§18): agreeing digest and coverage are filled; six pass-1 pack versions remain null pending the prospective scope expansion below.
- **Release-time stage-1 commit** (§11): intentionally supplied at held-out release, not a pre-first-t0 missing slot (P0 ruling 7).

P_limit/contention measurability, test-7 scale, clock holds, disk and C5 sizing use the already-ruled fallbacks/receipts and are filled; missing optional diagnostics are not silently substituted. Whole-suite verification on the final laptop tree, registration cold gate/commit and per-sub-pack smoke fingerprints remain lead/operator gates of §19.

Requested additional paths (exact-file semantics):

- `tests/b6/test_bytes_packs.py`
- `tests/test_fix573i_restore.py`
- `configs/campaigns/bytes-s1-p2/plan_tree.json`
- `configs/campaigns/bytes-s2-p2/plan_tree.json`
- `configs/campaigns/bytes-s3-p2/plan_tree.json`
- `configs/campaigns/bytes-s4-p2/plan_tree.json`
- `configs/campaigns/bytes-s5-p2/plan_tree.json`
- `configs/campaigns/bytes-s6-p2/plan_tree.json`

Reason/failure: `BytesPackTests.test_estimators_name_the_analysis_stage_functions_with_version_slot_while_draft` currently requires every estimator list to equal the shared all-null `plans.ESTIMATORS` (line 119) and explicitly `assertIsNone(entry["version"])` (line 123), contradicting the requested six non-null pass-1 versions. `scripts/bytes_plan_trees.py` also binds its exact own file SHA into every pass tree, so editing that allowed source necessarily stales the six unlisted pass-2 trees at `/generator/sha256` (the exact-byte generator fence at test line 73 checks all twelve). This dependency was identified before any generator/pin write; the current static generator checks remain green.

Smallest change after approval: bind the exact agreeing SHA for pass 1 in the already-authorized generator; preserve draft statuses and pass-2 null versions; update those two test assertions to check the pass-specific value and live source digest; regenerate the six pass-1 registrations/trees plus only the generator self-digest in each six pass-2 tree. Use the named registry writer only if its check requests it. No member, threshold, arithmetic, order, collection timing, exclusion or printed scientific number changes.

Completed independent work: five conflict files resolved, automatic older-arithmetic merge fragments removed, compatible storage code/tests retained, field map updated, archive parity and coverage reproduced, B2 source digest/coverage and amended §19 recorded. Blocked: generator/registration version propagation, the incomplete restore-i argument fixture, and their final acceptance checks. The completed focused run also found `EntryPointTests.test_twin_independent_storage_stop_escapes_data_handler` in the unlisted `tests/test_fix573i_restore.py:180`: its fake `SimpleNamespace` lacks the retained twin CLI fields, so it errors with `AttributeError: ... stage` before the storage-stop seam. Smallest additional fixture change: add `stage="blinded"`, `stage1_commit=None`, `manifest=None`, and mock `read_manifest` to return `{}` around this injected `read_export` stop. A scratch-only execution of exactly that proposed fixture correction passes (`Ran 1 test in 0.001s; OK`), with the production program unchanged. This is diagnostic evidence, not a claim that the unedited test passes. No requested out-of-scope file was written. No staging or commit was attempted.

Next exact step: the lead prospectively expands WRITE_SCOPE by the eight paths above (or applies that bounded remainder), then resumes this seat to perform generator propagation and its focused checks. The lead also reruns the 21 process-enumeration-dependent methods, reviews the full diff, stages the resolved files and commits the pending merge.

## Final workspace audit

HEAD end remains `bb78384c2c92009a48085cd6376ea09d3bfbc850`; upstream is the same. `origin/main` is `eee6984afac996297859f87b4315a7f9647afb6e`. Write-scope audit passes: 12 session paths; all 67 other pre-existing merge paths retain their original status and no new unowned path exists. Conflict markers are absent; the five index entries intentionally remain unmerged for the lead to stage. `P6-PHASE-B-VERIFICATION.json` records 18 exact commands/observations, including the first corrected agreement error and the scratch-only restore-i diagnostic.
