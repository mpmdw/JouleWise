STATUS: DONE

# CUSTODY-T1: tests must never publish into the real ~/night-custody

Branch `lane/2026-10-30-custody-test-isolation` from origin/main `4c26b2e2c`. Pushed; no PR. Only tests/** (outside tests/b5_analysis/**) and this report changed. joulewise/** and scripts/** are untouched, so production custody defaults are unchanged. Only synthetic test fixtures were run or read; no block-5/6/BYTES data was opened or searched.

## SUMMARY

At origin/main, three test modules ran campaigns with `JOULEWISE_CUSTODY_PARENT` unset. They resolved `custody_parent()` to `$HOME/night-custody` and published 16 `active-campaigns` entries there over a full run. The modules are `test_axi_controller_events`, `test_axi_mock_spec` and `test_collector_analysis_manifest_id`. The third does it through a `scripts/run_campaign.py` child that inherits the environment. Each campaign removes its entry when it exits normally, but the `active-campaigns/` directory stays behind. A killed or crashed test would leave its entry for the census, the quiet guard and the stale-lock reclaim to read.

All three modules, plus `test_hazard_whole_window_verdict` (which drives `run_campaign.main`), now point the variable at a per-test temporary parent through the new helper `tests/custody_isolation.py`. The helper restores the previous environment on cleanup.

A new guard, `tests/test_custody_isolation_guard.py`, does four things:
- It fails when any test module drives a custody writer or reader without isolating the custody parent.
- It pins the modules the probe observed reaching `custody_parent()`.
- It proves the helper's scope and that it restores the environment.
- It proves the production default is still `$HOME/night-custody`.

I ran CI's own test steps with HOME at a decoy that holds an empty `night-custody/`. The decoy stayed empty.

## C1: the two named modules

Change: `from tests.custody_isolation import isolate_custody_parent`, and a `setUp` that calls `isolate_custody_parent(self)`. It is added to `AxiControllerEventTests` (tests/test_axi_controller_events.py) and `AxiMockSpecTests` (tests/test_axi_mock_spec.py). The scope is per test: `patch.dict(os.environ, ...)` plus `addCleanup`, the same mechanism as test_run_campaign.py:101, but registered on the test rather than the module. Commit `f29ea82c5`.

Evidence, from the scratch probe described under C2:
- **origin/main:**
  - Decoy `$HOME/night-custody/active-campaigns` was created by both modules.
  - The probe logged 6 `publish_campaign` paths under the decoy. 2 came from `test_campaign_prebundle_process_failure_retains_identity_receipt_and_row` and `test_campaign_zero_exit_without_finalized_bundle_is_dispatch_failure`. 4 came from `test_v2_campaign_refuses_eligible_receipt_after_bundle_store_deletion` and `test_v2_campaign_writes_complete_immutable_ledger_and_pair_reports`.
- **Branch:**
  - `PASS tests.test_axi_controller_events s=4 decoy_entries=0`
  - `PASS tests.test_axi_mock_spec s=15 decoy_entries=0`
  - All 6 `custody_parent()` and 6 `publish_campaign` calls had the variable set.

## C2: every other module

### Method

The instrumentation was scratch only and was not committed. A `sitecustomize.py` on `PYTHONPATH` wrapped `joulewise.measurement_liveness.custody_parent` and `publish_campaign` as soon as the module was imported. It also set `JW_PROBE_TEST` from `TestResult.startTest`, so child processes that inherit the environment were attributed to the right test id.

A scratch runner then ran every discovered module (458, including tests/b5_analysis) in its own interpreter through `shard_tests.run_shard((module,), 1, 1)`. Each run had:
- HOME set to a per-module decoy that contained an empty `night-custody/`
- both custody variables removed
- TMPDIR under /tmp

The run was at origin/main, in a separate worktree.

### Result at origin/main

Calls with the variable unset (every one of them published into the decoy):

| Module | `custody_parent()` | `publish_campaign` | Route |
|---|---|---|---|
| test_axi_controller_events | 2 | 2 | in process |
| test_axi_mock_spec | 4 | 4 | in process |
| test_collector_analysis_manifest_id | 10 | 10 | 18 rows from the `scripts/run_campaign.py` child |

The test_collector_analysis_manifest_id calls came from 9 tests:
- `test_collector_fixture_run_records_v3_manifest_identity_and_sha256`
- `test_cross_id_campaign_log_append_refuses_without_mutation`
- `test_cross_id_existing_bundle_reuse_refuses_before_bundle`
- `test_deeply_nested_stage_collects_with_canonical_identity`
- `test_exploratory_calibration_without_v3_marker_stays_null`
- `test_finalized_v3_collection_identity_selects_collector_cooldown_only`
- `test_production_collection_without_any_analysis_marker_stays_null`
- `test_same_id_resume_adopts_bundle_missing_provenance_member`
- `test_splitwise_decode_v1_finalized_marker_preserves_null_collection`

Calls that already had the variable set, so were already isolated:
- test_measurement_liveness: 60
- test_run_campaign: 81
- test_run_campaign_hazard_flags: 25
- test_run_campaign_max_blocks: 1
- test_run_campaign_p2_rc: 21

Decoys holding anything after the run, out of 458:

```
probe-base/homes/tests.test_axi_controller_events/night-custody/active-campaigns
probe-base/homes/tests.test_axi_mock_spec/night-custody/active-campaigns
probe-base/homes/tests.test_collector_analysis_manifest_id/night-custody/active-campaigns
```

`/root/night-custody` (pwd fallback for a child without HOME) was never created.

### Paths the probe could not observe

I analysed these statically.

1. **`python3 joulewise/measurement_liveness.py` run as `__main__`.** The only caller is `scripts/window_status.sh`. Its only test, `test_window_status_guard`, sets the variable.
2. **zsh-gated modules.** `/bin/zsh` is absent in this container, and apt cannot reach its mirrors. I did not configure apt through the agent proxy: that action was denied, and I did not try another route. The affected modules are b5_chain, b5_driver*, run_night, gen_derivation_night, install_night_agent, night_agent_install, neg8_survivors, magistrate_watchdog, v5_qualification_plan and others. None of them can reach the real custody registry:
   - b5 chains call `scripts/run_campaign.py` inside a `fake_window` measurement root, which installs `FAKE_RUN_CAMPAIGN` (tests/fixtures/b5_plan/fake_window.py:238).
   - neg8_survivors stubs `run_stage`.
   - No committed `scripts/night_chains/*.zsh` references run_campaign, measurement_liveness or window_status.
   - test_run_night calls `census(parents=[...])` with explicit parents.
   - run_night.py imports only `observe_identity`, `pending_launch_closed` and `_start_token`.
3. **Static scan.** `test_hazard_whole_window_verdict` calls `run_campaign.main(["--whole-window-verdict", ...])`. The probe saw no custody call from it, but `main()` can reach custody. It is isolated per test so the scan rule stays uniform: any test that drives run_campaign isolates.

### Fixes

- `tests/test_collector_analysis_manifest_id.py`: per-test `setUp` isolation. The `run_campaign.py` child inherits the patched environment.
- `tests/test_hazard_whole_window_verdict.py`: one line at the top of the existing `setUp`.

Commit `be1bcc408`.

## C3: guard, and the choice

**Chosen:** a shared helper plus a guard test, `tests/test_custody_isolation_guard.py`.

**Why not a tests-package default.** It would not run.
- CI's ordinary shards and `scripts/quick_suite.py` import each test file as a top-level module through `scripts/shard_tests.py` (`_unittest_import_name`), as `unittest discover -s tests` does. tests/ has no `__init__.py`, and creating one would not be imported on that path.
- The shared runners live in scripts/, which is outside WRITE_SCOPE.
- `scripts/quick_suite.py` already sets the variable for its workers. CI's ordinary shard step (`shard_tests.run_units`) and the exclusive jobs do not, and those are the routes where the leak happens.

**Why not a dynamic guard.** One that re-runs the reaching modules under a decoy HOME would add minutes per run. That is too costly to keep in an ordinary shard.

**What the guard checks:**
1. `test_every_module_that_reaches_custody_isolates_it` scans every tests/**/test_*.py. If a module's source matches a custody-reach marker, the module must call `isolate_custody_parent(` or name `JOULEWISE_CUSTODY_PARENT` / `CUSTODY_PARENT_ENV`. The markers are:
   - `run_axi_spec_campaign(`
   - `publish_campaign(`
   - `custody_parent()`
   - `run_campaign[_module].main(`
   - the shared `run_campaign` runner imported from tests.test_run_campaign
   - `str(ROOT|REPO_ROOT|REPOSITORY / "scripts/run_campaign.py")` used as an argv element
   - `window_status.sh` / `measurement_liveness.py`
2. `test_observed_reaching_modules_are_still_isolated_and_still_scanned` covers the nine modules the probe saw reach custody, plus the window_status caller. Each must still isolate, and each must still be recognised by at least one marker. That keeps the scan's recall checked against the observed ground truth.
3. `IsolationHelperTests` checks the helper:
   - The per-test parent lies under `tempfile.gettempdir()` and not under `~/night-custody`.
   - A real `publish_campaign` lands in `<parent>/active-campaigns`.
   - After cleanup both variables are unset again, and a previous value is restored exactly.
   - Module scope registers module cleanups.
   - The temp directory is removed.
4. `ProductionDefaultTests.test_custody_parent_default_is_unchanged` proves that with the variable unset `custody_parent()` is `$HOME/night-custody`, and that a set value is still expanded. It also checks the environment-variable names.

**Counterfactual.** I ran the guard against the origin/main tree, with a scratch copy of the two new files that was removed afterwards. It failed:

```
AssertionError: {'test_axi_controller_events.py': ['axi sp[193 chars]in']} != {}
- {'test_axi_controller_events.py': ['axi spec campaign'],
-  'test_axi_mock_spec.py': ['axi spec campaign'],
-  'test_collector_analysis_manifest_id.py': ['shared run_campaign runner'],
-  'test_hazard_whole_window_verdict.py': ['run_campaign main']} : these test modules can reach custody_parent() without JOULEWISE_CUSTODY_PARENT; call tests.custody_isolation.isolate_custody_parent
...
MODULE FAIL tests.test_custody_isolation_guard tests=6 failures=4 errors=0 skipped=0 seconds=1.093
```

On the branch: `MODULE PASS tests.test_custody_isolation_guard tests=6 failures=0 errors=0 skipped=0 seconds=1.058`.

## VERIFICATION

### Command

A scratch driver ran the exact `python - <<'PY'` bodies extracted from .github/workflows/ci.yml on branch HEAD `be1bcc408` (unshallowed clone):
- the ordinary shard step with `SHARD_COUNT=12`, `SHARD_INDEX=1..12`
- `python -m unittest -v tests.test_calibration_exits`
- the crash-matrix step with `SHARD_INDEX=1..2`

Four jobs ran at a time. Environment:
- HOME=/tmp/jwverify/home, containing an empty `night-custody/` and a copy of the container's .gitconfig
- TMPDIR/TEMP/TMP=/tmp/jwverify/tmp, which contains no float-like token
- `JOULEWISE_CUSTODY_PARENT` and `JOULEWISE_ADDITIONAL_CUSTODY_PARENTS` removed
- Python 3.11.17

### Exact tails

```
SHARD SUMMARY index=1/12 modules=1 tests=36 failures=0 errors=0 skipped=0 result=PASS
SHARD SUMMARY index=2/12 modules=42 tests=1368 failures=18 errors=29 skipped=55 result=FAIL
SHARD SUMMARY index=3/12 modules=42 tests=916 failures=4 errors=26 skipped=19 result=FAIL
SHARD SUMMARY index=4/12 modules=42 tests=805 failures=0 errors=1 skipped=22 result=FAIL
SHARD SUMMARY index=5/12 modules=41 tests=1109 failures=34 errors=13 skipped=10 result=FAIL
SHARD SUMMARY index=6/12 modules=42 tests=1074 failures=15 errors=2 skipped=14 result=FAIL
SHARD SUMMARY index=7/12 modules=42 tests=769 failures=23 errors=41 skipped=13 result=FAIL
SHARD SUMMARY index=8/12 modules=42 tests=1244 failures=3 errors=128 skipped=28 result=FAIL
SHARD SUMMARY index=9/12 modules=42 tests=861 failures=0 errors=7 skipped=8 result=FAIL
SHARD SUMMARY index=10/12 modules=43 tests=892 failures=12 errors=11 skipped=30 result=FAIL
SHARD SUMMARY index=11/12 modules=42 tests=1180 failures=4 errors=0 skipped=9 result=FAIL
SHARD SUMMARY index=12/12 modules=43 tests=1366 failures=17 errors=1 skipped=50 result=FAIL
SHARD SUMMARY index=1/2 modules=1 tests=1 failures=0 errors=0 skipped=0 result=PASS
SHARD SUMMARY index=2/2 modules=1 tests=19 failures=0 errors=0 skipped=0 result=PASS
test_calibration_exits:
Ran 48 tests in 240.863s
FAILED (failures=5)
```

### Touched modules, all passing under this run

```
MODULE PASS tests.test_custody_isolation_guard tests=6 failures=0 errors=0 skipped=0 seconds=1.058
MODULE PASS tests.test_axi_controller_events tests=7 failures=0 errors=0 skipped=0 seconds=0.568
MODULE PASS tests.test_axi_mock_spec tests=11 failures=0 errors=0 skipped=0 seconds=4.995
MODULE PASS tests.test_collector_analysis_manifest_id tests=16 failures=0 errors=0 skipped=0 seconds=52.529
MODULE PASS tests.test_hazard_whole_window_verdict tests=20 failures=0 errors=0 skipped=0 seconds=38.203
```

### Decoy listing after the run

```
$ find /tmp/jwverify/home/night-custody | sort
/tmp/jwverify/home/night-custody
$ ls -la /tmp/jwverify/home/night-custody
total 8
drwxr-xr-x 2 root root 4096 Oct 30 10:03 .
drwxr-xr-x 3 root root 4096 Oct 30 10:03 ..
$ ls /root/night-custody
ls: cannot access '/root/night-custody': No such file or directory
```

The decoy is empty. At origin/main, the same decoy setup received 16 published entries and the `active-campaigns/` directory (C2).

### Failing modules

34 ordinary modules failed. Every one of them also failed at origin/main in the probe run, so no failure is new on the branch:

```
b5_analysis.{test_deadline_observer,test_deadline_tripwire,test_dry_run,test_floor_kept_units,test_release_equality,test_sensitivity_guard,test_shared_physics_cache}
test_b5_chain test_b5_chain_prune2 test_b5_driver test_b5_driver_p2 test_b5_driver_p3
test_calibration_ledger_historical_custody_report test_d117_fixture_transport
test_gen_derivation_night test_gen_g2a_window test_install_magistrate_watchdog
test_install_night_agent test_magistrate_watchdog test_magistrate_watchdog_yield
test_neg8_survivors test_night_agent_install test_night_kinds test_quiet_guard
test_quiet_predicate_campaign test_receipt_histsem test_run_night test_s0_line_audit_guard
test_v5_block4_composed test_v5_block4_replay test_v5_block4_x12a test_v5_block4_x12b
test_v5_qualification_plan test_v5_s1_desk_closeout
```

The dominant cause is the environment:
- 230 `FileNotFoundError ... '/bin/zsh'` lines. CI installs zsh; this container cannot.
- Python 3.11 lacks `sys.monitoring`.
- `ValueError: backup command failed`.
- An exact float comparison: `0.049999999999999996 != 0.05`.
- Privilege text expected by test_quiet_guard.

The same 5 test_calibration_exits failures appear at origin/main. 13 more modules failed at origin/main only because the clone was shallow at the time (pin commits missing) and pass after `git fetch --unshallow`.

## FILES CHANGED

- tests/custody_isolation.py (new): the `isolate_custody_parent(case=None)` helper.
- tests/test_custody_isolation_guard.py (new): the C3 guard, 6 tests.
- tests/test_axi_controller_events.py: C1, `setUp` isolation.
- tests/test_axi_mock_spec.py: C1, `setUp` isolation.
- tests/test_collector_analysis_manifest_id.py: C2, `setUp` isolation.
- tests/test_hazard_whole_window_verdict.py: C2 static rule, isolation in the existing `setUp`.
- .codex-report/CUSTODY-T1.md: this report.

## DECISIONS

- **Per-test scope over per-module scope.** Every test gets a fresh registry, so one test's leftover entry cannot change another test's census. The helper also supports module scope (`isolate_custody_parent()` from `setUpModule`), matching test_run_campaign.py:101. The existing module-level setups were left as they are.
- **The helper sets `JOULEWISE_ADDITIONAL_CUSTODY_PARENTS="[]"` as well.** The census also reads that variable, and the existing patterns at test_run_campaign.py:101 and test_run_campaign_hazard_flags.py:64 set it.
- **Static guard plus pinned ground truth, not a package default or a dynamic re-run.** The reasons are under C3. The scan over-approximates: any module driving run_campaign must isolate, even if it doesn't currently reach custody. Isolation is cheap and harmless.
- **`str(<repo root> / "scripts/run_campaign.py")` argv only.** The scan marker is limited to that form. Source reads (`read_text`), digest pins and fake-window measurement roots (b5_chain, b5_driver) are not custody reach and are not flagged.

## OPEN ISSUES

1. **zsh-gated paths were not exercised dynamically here.** Static analysis (C2, "Paths the probe could not observe") finds no custody reach on them. A run on a host with `/bin/zsh` and the decoy HOME would confirm it; the scratch runner can be reproduced from the C2 method.
2. **The full suite is not green in this container**, for environment reasons only. The failure set is identical to origin/main's, listed above. CI on ubuntu-latest with zsh installed and a supported Python is the authority for green.
3. **Other HOME-relative production defaults are not routed through `custody_parent()`.** Examples: `arm_readiness` `night_custody_parent` HOME_RELATIVE, and literal `/Users/edr/night-custody/...` constants in night_gate, evidence_night and gen_g2_phase_d. They were out of scope. Neither the probe nor the decoy HOME showed a test writing through them. The decoy stayed empty, so no test wrote under `$HOME/night-custody` by any route during the verification run.
4. **The scan is a source-shape heuristic.** A new test that reaches custody through an indirect helper not matched by the markers would get past check 1. Check 2 only protects the observed set. Re-running the C2 probe after large test additions closes that gap.
