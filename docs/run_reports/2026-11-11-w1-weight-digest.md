# Weight digest (RL-62)

Seat: `w1-weight-digest`. Branch: `ops/2026-11-11-w1-weight-digest`.
Base: `2f223032b` (W-1/W-2 armcheck rounds 1–4). The initial worktree was clean.
This explicit RL-62 brief selects bounded AGENT work; no active stop card was
found. Coordination state and kernel tasks are lead-owned and were not edited.

Read the armcheck report, session script, M0, applicable repository conventions,
and the requested verbatim extracts from the local audit ref: the model-weights
gap, RL-53, RL-35 item 4, RL-37, and state-machine sections 0, 4.3, 4.5 and 8.1.
Read the speed toolbox from `origin/main`; no throughput optimization, batching,
cross-prepare cache, or changed measured work is introduced.
The RL-53 extraction also emitted W-4 through W-8 and the following header,
beyond the requested W-3 endpoint. These were policy paragraphs; no study
files or outcome records were opened. The weight-gap extraction used the exact
requested command.

## Implementation and scope

`scripts/align_v4_session.py` is the only changed bound file. After the shared
prepare has staged its plan, `weight_digest_preflight` enumerates the actual
`pilot._member_rows`. It calls the kit's existing
`bytes_h_session.align_unit_id(model_id, run_id)`; it invents no unit names.
It reads the selected session's registered `model_artifact_inventory.json`.
For W1 this is `configs/campaigns/align_v4/registration`; the series generator
projects the same registered identities onto later windows' run IDs using
`align_v4_kit._identities` (`align_v4_series.py:418–429`). The selected
`registration_dir` is also the locator the shared prepare/member reader uses.
No inventory root is resolved or inspected while building this mapping.

Each distinct root is passed once per prepare to the existing R0
`joulewise.provenance.model_artifact_identity`. The function is injectable as
`weight_identity_fn` on prepare and `identity_fn` on the helper. Status must be
`ok`, kind must be `file_set`, and both the folded digest and the complete lexical
per-file map must match **every** unit sharing the root. Root and unit traversal
are sorted. Added/missing/changed shard names are retained without shard bytes.
There is no new fold arithmetic.

The one new prepare-state key, `weight_digest_preflight`, contains source,
`prepared_at_epoch_s`, overall `ok`/reasons and per-root units, registered and
observed folded digests, file count, total bytes, elapsed seconds and `ok`.
Prepare writes `session.json` before raising a weight refusal, following the
existing privilege-preflight pattern. Weight failure skips the subsequent
frequency preflight. Existing earlier physical-presence/kit refusals remain
unchanged. The shared prepare can raise for a missing shard/row or unreadable
tree before staging any state. A narrow exception path now checks the already
generated selected plan/inventory in that case. If weights fail, it writes an
`INPUTS_ONLY` refusal state with the same weight-evidence key, then raises the
weight refusal. If the weights match, the original exception is re-raised.
Other physical gates and every existing nonempty session are preserved.

The install path's existing `pre_dwell` copies that entire block verbatim into
the arm staging record under `weight_digests`, including its prepare time.
A recorded failed weight preflight also refuses install. Old/by-hand sessions
with no block record exactly `{"source":"not_recorded_by_prepare"}` and are
not refused for that absence. Install never calls the weight identity function.

`--weight-digests-attested PATH` accepts the following JSON structure (synthetic
values below). `attested_by` must name a person; the timestamp is optional and
is preserved if supplied. Every planned registered root must appear, and both
values must equal every corresponding registered unit's digest. Missing/extra
roots, missing units, unreadable/malformed input, a blank name or a mismatch
refuse and are persisted in the arm record before the installer runs.

```json
{
  "attested_by": "Operator name",
  "attested_at_epoch_s": 1234,
  "roots": {
    "/synthetic/model": {
      "registered_folded_sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
      "observed_folded_sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    }
  }
}
```

The arm records this as `source: "attested"`; this is named manual attestation,
not a cryptographic signature or a new hash of the model at install.

### Why prepare cannot run the arm's dwell

`prepare` calls `pilot.prepare` → `bytes_h_session.prepare`, which stages the
measurement view/plan and returns state; those functions do not call install,
`arm_checks`, `pre_dwell` or a dwell stamp. The new hash is in this prepare path.
Separately, `install` calls `_arm_and_install` → `arm_checks`; its `pre_dwell`
hook reads any attestation and writes the arm record, then `arm_checks` takes
the existing `dwell_start` stamp as its final step. The test makes any call to
`arm_checks` from prepare fail. Existing post-stamp installer/watchdog timing
and all measured records, flags, verdicts, windows and receipt checks are unchanged.

### Refusals and their records

* `weight_digest_preflight: digest_mismatch: <unit> <root basename>`
* `weight_digest_preflight: file_set_differs: <root basename>`
* `weight_digest_preflight: unavailable: <root basename>: <reason>`
* `weight_digest_preflight: no_inventory_row: <unit>`

These live in `session.json`'s `weight_digest_preflight.reasons` and are raised
after that state write. File-map differences additionally retain sorted
`file_set_diff.{added,missing,changed}` in the per-root entry. Inventory read/
shape errors use the unavailable prefix naming `model_artifact_inventory.json`.
Attestation structural/read errors use `unavailable: attestation: <reason>`;
attested mismatches/missing units use the same digest/missing-row codes above.
Attested or previously recorded prepare failures are also copied into the
existing arm staging `reasons` and refuse through the existing arm exception.
No flag or cause catalog was changed.

## PREQUAL and fixture isolation

Unbound `joulewise/align/w1_prequal.py` now provides the explicit synthetic
`FakeHost.weight_identity` seam. Its normal arm fixture builds tiny fake shard
trees and a matching synthetic inventory, and records the synthetic prepare
preflight. The default-registered W1 check `weight-digest-preflight` drives
production prepare and the install CLI with the existing synthetic host seams.
It requires a matching prepare/arm control, then changes the fake digest and
requires persisted prepare refusal plus install refusal with no installer call.
It uses the existing CHECKS registry/CLI; no bound dispatcher was edited.

Unrelated frequency/series fixtures explicitly fake the new preflight so they
cannot follow registered model paths. The real identity witness hashes only a
tiny temporary `model.safetensors` and an added `extra.bin`; all other new
identity tests use fakes. No real model tree or cache was accessed.

A required importer, `tests.align.test_r0_host`, had an optional native-test
decorator that called `is_file()` on an absolute sealed custody path at import.
Source inspection caught it before that importer ran. Its decorator now checks
only `JW_R0_LIVE_SMC=1`; the native method remains optional and unchanged. The
serial test launcher unsets all `JW_*` opt-ins. No real custody metadata is
needed to import the module. This is a test-isolation repair, not R0 evidence.

No new test module was added, so `scripts/test_timings.json` is unchanged.
No subagents or network tools were used. There was no measurement collection,
model download, real host command, quiet-window task, or access to real restricted
or night custody. All execution evidence is synthetic; native qualification and
the cold review remain lead-owned.

## Failing-first evidence

Test-only commit `cc52d3707` precedes implementation `5a21f5511`. The new session
tests were run against base production in one module invocation:

```text
python3.13 -B -m unittest \
  tests.align.test_v4_arm_watchdog_check.WeightDigestTests \
  tests.align.test_v4_arm_watchdog_check.ArmIntegrationTests.test_weight_digests_from_prepare_are_carried_verbatim_without_hashing \
  tests.align.test_v4_arm_watchdog_check.ArmIntegrationTests.test_legacy_prepare_records_not_recorded_without_refusal_or_hashing \
  tests.align.test_v4_arm_watchdog_check.ArmIntegrationTests.test_attested_weight_digests_are_validated_and_carried_without_hashing \
  tests.align.test_v4_arm_watchdog_check.ArmIntegrationTests.test_bad_weight_attestations_refuse_in_persisted_arm_before_install \
  tests.align.test_v4_arm_watchdog_check.ArmIntegrationTests.test_weight_attestation_cli_option_is_forwarded
AttributeError: module 'scripts.align_v4_session' has no attribute 'weight_digest_preflight'
KeyError: 'weight_digests'
AssertionError: ValueError not raised
error: unrecognized arguments: --weight-digests-attested .../attestation.json
Ran 16 tests in 0.477s
FAILED (failures=7, errors=20)

python3.13 -B -m unittest tests.align.test_w1_prequal.ArmCliTests.test_named_weight_digest_check_passes_matching_and_trips_mismatch
AssertionError: 'weight-digest-preflight' not found in ...
Ran 1 test in 3.941s
FAILED (failures=1)
```

The unavailable statuses, wrong kind, per-file add/remove/rename/hash changes,
each shared unit, root deduplication and order independence are separate tests
or subtests. The arm tests cover all three evidence sources, bad attestations,
CLI forwarding, persisted refusal and an identity function that raises if an
arm ever calls it. The test-only red commit contains the complete commands'
test method names. Red logs are in `/private/tmp/w1-weight-digest-checks/`.
The initial red shell wrappers used zsh's read-only `status` variable after
unittest completed; the unittest logs were intact. Subsequent wrappers use
`task_test_rc`.

A final code-review witness found the early shared-prepare ordering gap above.
Test-only commit `6a73700d3` precedes its fix. Against the first implementation:

```text
python3.13 -B -m unittest tests.align.test_v4_arm_watchdog_check.WeightDigestTests.test_early_model_presence_or_row_refusal_also_records_weight_evidence
AssertionError: "weight_digest_preflight: file_set_differs" does not match "models missing: synthetic"
PermissionError: synthetic unreadable shard
KeyError: 'tiny-two'
Ran 1 test in 0.007s
FAILED (failures=2, errors=2)
```

The fix covers missing/renamed shards, an upstream unreadable-tree error, and
an upstream missing-row error. The same test verifies existing session bytes
are never overwritten. After the fix, the final focused command below passed:

```text
python3.13 -B -m unittest tests.align.test_v4_arm_watchdog_check.WeightDigestTests tests.align.test_v4_arm_watchdog_check.ArmIntegrationTests
Ran 28 tests in 0.948s
OK
```

Focused green results before the broader sweep:

```text
python3.13 -B -m unittest tests.align.test_v4_arm_watchdog_check.WeightDigestTests tests.align.test_v4_arm_watchdog_check.ArmIntegrationTests
Ran 27 tests in 0.830s
OK

python3.13 -B -m unittest tests.align.test_w1_prequal.ArmCliTests.test_named_weight_digest_check_passes_matching_and_trips_mismatch
Ran 1 test in 23.679s
OK
```

## Serial regression results

Every command below has prefix `python3.13 -B -m unittest`; only the explicitly
requested trio was grouped. A fresh temporary HOME, synthetic host-state
store, empty system/global Git config, no lazy fetch, offline model settings
and unset `JW_*` opt-ins isolate each invocation. Source text search found
56 importer modules; every one was attempted, plus dynamic closure and the
PREQUAL driver. No full suite or pytest was run.

The serial tranche took 1005.020 seconds wall time: 11 passing commands,
2 failing commands and 43 timeouts. The 53-test armcheck pass and 36-test trio
pass **precede the final early-presence fix**. A bounded trio retry after that
fix is reported below; final closure/registration verification is incomplete.
No stale trace or receipt digest failure was emitted by the completed trio,
so there is no EXPECTED digest message to quote. These fixture results do not
authenticate a native STRICT receipt.

Each TIMEOUT is an incomplete module, with no passing final count inferred.
Most importers received a 12-second cap to attempt the full requested inventory
within the hard aggregate budget; the first changed modules received 25/45/90
seconds and the first trio 300 seconds. Exact argv, output logs, importer list
and process timings are in `/private/tmp/w1-weight-digest-checks/`.

| Module(s), after command prefix | Result | Process wall (s) |
|---|---|---:|
| `tests.align.test_v4_arm_watchdog_check` | PASS; 53 tests | 57.833 |
| `tests.align.test_v4_executed_closure` `tests.align.test_v4_dynamic_closure` `tests.align.test_v4_registration` | PASS; 36 tests | 267.265 |
| `tests.test_w1_reliability_r3` | PASS; 14 tests | 8.072 |
| `tests.align.test_v4_series` | TIMEOUT | 25.583 |
| `tests.align.test_v4_series_e2e` | TIMEOUT | 25.266 |
| `tests.align.test_w1_prequal` | TIMEOUT | 45.255 |
| `tests.align.test_harvest_off` | TIMEOUT | 12.380 |
| `tests.align.test_harvest_off_review_sol1` | TIMEOUT | 12.674 |
| `tests.align.test_harvest_off_review_sol2` | TIMEOUT | 12.489 |
| `tests.align.test_km003c` | PASS; 25 tests | 11.142 |
| `tests.align.test_merge_c84_sol` | TIMEOUT | 12.404 |
| `tests.align.test_r0_host` | TIMEOUT | 12.282 |
| `tests.align.test_r11_delta3_sol1` | TIMEOUT | 12.504 |
| `tests.align.test_r11_delta3_sol2` | TIMEOUT | 12.084 |
| `tests.align.test_r11_delta4_sol1` | TIMEOUT | 12.204 |
| `tests.align.test_r11_delta4_sol2` | TIMEOUT | 12.400 |
| `tests.align.test_r11_delta5_sol1` | TIMEOUT | 12.323 |
| `tests.align.test_r11_delta5_sol2` | TIMEOUT | 12.260 |
| `tests.align.test_r11_delta6_sol1` | TIMEOUT | 12.460 |
| `tests.align.test_r11_delta6_sol2` | TIMEOUT | 12.464 |
| `tests.align.test_r11_delta_sol1` | PASS; 8 tests | 8.820 |
| `tests.align.test_r11_delta_sol2` | PASS; 6 tests | 10.373 |
| `tests.align.test_r1_round6_exec_review` | FAIL; 9 tests | 6.232 |
| `tests.align.test_r1_round6_power` | FAIL; 25 tests | 6.322 |
| `tests.align.test_r1_round7_install` | TIMEOUT | 12.201 |
| `tests.align.test_r1_round7_power` | TIMEOUT | 12.461 |
| `tests.align.test_r1_round8` | TIMEOUT | 12.348 |
| `tests.align.test_smoke_delta3_sol1` | TIMEOUT | 12.155 |
| `tests.align.test_smoke_delta3_sol2` | TIMEOUT | 12.421 |
| `tests.align.test_smoke_delta4_sol1` | TIMEOUT | 12.194 |
| `tests.align.test_smoke_delta4_sol2` | TIMEOUT | 12.372 |
| `tests.align.test_smoke_delta_sol1` | TIMEOUT | 12.482 |
| `tests.align.test_smoke_delta_sol2` | TIMEOUT | 12.498 |
| `tests.align.test_smoke_review_sol1` | TIMEOUT | 14.159 |
| `tests.align.test_smoke_review_sol2` | TIMEOUT | 12.296 |
| `tests.align.test_timing_receipts` | TIMEOUT | 13.712 |
| `tests.align.test_v4_dc_sealing` | PASS; 2 tests | 4.882 |
| `tests.align.test_v4_disclosure_only_desk` | TIMEOUT | 12.107 |
| `tests.align.test_v4_kit` | TIMEOUT | 12.454 |
| `tests.align.test_v4_next_arm_packet` | TIMEOUT | 12.351 |
| `tests.align.test_v4_next_arm_packet_opus_witnesses` | TIMEOUT | 12.384 |
| `tests.align.test_v4_powermode_record` | PASS; 9 tests | 6.714 |
| `tests.align.test_v4_r11` | PASS; 27 tests | 6.725 |
| `tests.align.test_v4_record_binding` | TIMEOUT | 12.277 |
| `tests.align.test_v4_series_r20` | TIMEOUT | 12.217 |
| `tests.align.test_v4_w1_blockers` | TIMEOUT | 12.371 |
| `tests.align.test_v4_w1_synthetic` | TIMEOUT | 12.301 |
| `tests.align.test_w1_kit_r10` | TIMEOUT | 12.260 |
| `tests.align.test_w1_smoke` | TIMEOUT | 12.325 |
| `tests.align.test_w1bm_sol1` | TIMEOUT | 12.673 |
| `tests.align.test_w1bm_sol2` | TIMEOUT | 12.341 |
| `tests.test_w1_reliability_r2` | TIMEOUT | 12.355 |
| `tests.test_w1_reliability_r4` | TIMEOUT | 12.515 |
| `tests.test_w1_reliability_r5` | PASS; 7 tests | 10.765 |
| `tests.test_w1_reliability_r7` | PASS; 10 tests | 6.319 |
| `tests.align.test_v4_prequal` | TIMEOUT | 12.177 |

The first `test_r1_round6_power` run also exposed the CLI fixture's expected
kwargs missing `weight_digests_attested: None`. That expectation was updated
and the exact forwarding witness re-run green below. Other failures were
preserved, not relabelled EXPECTED:

```text
FAIL: test_a_never_launched_w1_night_is_restored_by_its_dead_man
AssertionError: 'ac powermode exit restore (dead_man)' not found in ...
  actual prefix: ac powermode close: restore Automatic; network time unchanged:

ERROR: test_install_holds_the_lock_until_it_returns
ERROR: test_session_start_restores_a_foreign_marker_and_keeps_its_own
ERROR: test_the_w1_marker_is_host_level_and_names_its_session
TypeError: FakeArmHost.__call__() got an unexpected keyword argument 'check'

ERROR: test_a_failing_gate_refuses_the_arm_and_the_real_gate_is_the_default
ERROR: test_a_passing_gate_is_recorded_and_the_installer_runs
ERROR: test_arm_without_a_disk_config_is_refused_before_the_installer
KeyError: 'plan_path'
```

A separate read-only baseline witness evaluates the base session source from
`git show 2f223032b:scripts/align_v4_session.py` in that module's namespace,
then runs the dead-man test, one fake-host error and one missing-plan error.
It reproduces the same three diagnostics (3 tests, 1 failure/2 errors).
No checkout is changed. The complete final round-6-power repeat still has
six errors after the CLI expectation fix; these are not weight-digest
refusals. The lead must disposition these baseline failures before admission.

Final isolated follow-ups (the base witness deliberately reports the same
failures; it is not a green regression result):

| Command after `python3.13 -B` | Result | Process wall (s) |
|---|---|---:|
| `/private/tmp/w1-weight-digest-checks/run_base_witness.py` | FAIL; 3 tests | 6.929 |
| `-m unittest tests.align.test_v4_kit.W1DiskGateTests.test_cli_install_requires_and_forwards_the_disk_config` | PASS; 1 tests | 3.629 |
| `-m unittest tests.align.test_r0_host.R0HostTest.test_erratum5_real_capture_has_uncensored_onset_and_prints_flags` | PASS; 1 tests; native replay skipped | 1.560 |
| `-m unittest tests.align.test_r1_round6_power` | FAIL; 25 tests | 6.074 |
| `-m unittest tests.align.test_v4_executed_closure tests.align.test_v4_dynamic_closure tests.align.test_v4_registration` | TIMEOUT | 50.408 |

The final trio retry timed out after 50 seconds with no completed result;
its earlier 36-test pass is not claimed for the final early-refusal diff.
The final round-6-power run was 25 tests with 6 errors (the CLI assertion now
passes). The R0 follow-up was one explicitly skipped native test, proving the
module imports without that test probing real custody; it is not a live replay.
The exact CLI forwarding witness passed.

The main serial tranche plus final tail commands account for 1073.620 seconds
of process wall time. The short red/green focused invocations add roughly
40–60 seconds, keeping total test execution below the approximately 20-minute
cap. No more tests were started after these bounded follow-ups.



## Diff, commits and native handoff

Diff from `2f223032b` (added/deleted lines):

| File | + / - | Change |
|---|---:|---|
| `scripts/align_v4_session.py` (only bound file) | 138 / 3 | Prepare digest/refusal evidence, early-presence failure path, arm carry/attestation |
| `joulewise/align/w1_prequal.py` (unbound) | 57 / 2 | Synthetic inventory/identity seam and named mismatch check |
| `tests/align/test_v4_arm_watchdog_check.py` | 270 / 2 | Digest, staging, arm, attestation, upstream-refusal and preservation witnesses |
| `tests/align/test_w1_prequal.py` | 8 / 0 | Named PREQUAL check witness |
| `tests/align/test_v4_series.py` | 2 / 0 | Explicit synthetic weight preflight |
| `tests/align/test_v4_series_e2e.py` | 2 / 0 | Explicit synthetic weight preflight |
| `tests/test_w1_reliability_r3.py` | 1 / 0 | Explicit synthetic weight preflight |
| `tests/align/test_v4_kit.py` | 1 / 1 | New optional CLI kwarg expectation |
| `tests/align/test_r0_host.py` | 3 / 2 | Avoid optional custody metadata read at import |
| This report | new | Evidence, results, limitations and exact handoff |

Local commits: `cc52d3707` (initial red tests), `5a21f5511` (implementation
and isolated fixtures), `dfa17e312` (optional R0 import isolation),
`6a73700d3` (early-presence red witness and final CLI/weight fixtures).
The final early-refusal fix and this report are committed together afterwards.
No push.

All nine changed Python files compile in memory; `git diff --check` passes.
Protected coordination/protocol/registration/receipt/trace/watchdog/driver paths
and `scripts/test_timings.json` have no diff. No raw evidence was changed.
The new tests only touch temporary synthetic files.

Next exact step: finish the final trio and all TIMEOUT modules above, one
module at a time under a fresh authorized budget and the same isolation;
disposition the two baseline-failing modules, then cold-review and
integrate/register the final bytes before remote native qualification.


After integrating the batch, the lead owns cold review, the single deviation
row, trace regeneration and STRICT re-registration. This seat changes none of
those artifacts and does not admit the batch.

The lead must run these native checks remotely on the measurement Mac, in a
lead-controlled qualification session with no quiet measurement or agent load:

1. Run real prepare for each applicable W1/series plan against its registered
   weights. Verify all planned units/roots, folded and per-file equality, file
   counts/bytes, elapsed times, and persisted prepare timestamps. This seat has
   not checked the actual models or measured their hashing latency.
2. Use disposable synthetic qualification weights/inventory to change a shard,
   add/remove/rename one, and force unreadable/changing/enumeration failure.
   Verify each refusal and the state write; never mutate production weights.
3. Install a matching prepared qualification session; verify the arm carries
   the exact block and its old prepare time, no model I/O at arm, and digest
   work ending before the dwell path. Preserve the existing meter/watchdog/
   frequency/restore gates.
4. Exercise matching and mismatching named manual attestations, and the legacy
   no-block case. Require the mismatch refusal before any installer call and
   the exact legacy source marker without a new refusal for absence alone.
5. Run PREQUAL and W1 smoke on the final registered bytes. Resume or disposition
   any incomplete regression modules listed above before admission/cut-off.

No MLX code changed; there is no new native MLX test from this delta. Fixture
passes do not qualify installed host behavior or real model identity. No new
science or naming ruling is requested. Incomplete final regression coverage,
the reproduced baseline failures and native qualification remain lead-owned.
