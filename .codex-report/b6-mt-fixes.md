# Block-6 machine-test fixes

Branch: `fix/2026-10-16-b6-mt-fixes`, created from `origin/lane/2026-10-16-b6-round2`
at `729449fa0` (parent `b9de23a2c`). No merge or PR is authorized or performed.
Implementation commit: `8c42d38a6f58a8e0db37419171b61f51f622a719`.
It was pushed successfully and confirmed by `git ls-remote` on the requested
branch. This report is a separate following documentation commit.

## Confirmed causes and changes

### 1. Every measured smoke member died before producing a bundle

The original committed plan tree and sidecar both name
`2ec3625a31b796e3fa37e2c39f37508618b649d0d9f61ddbd3fdfe2c5a282809`.
The reduced four-run bytes hash to
`ba6b671060f1ce9697922ae863b9928abe5428e30d85f4948d51ae6137b441f4`.
These are exactly the two hashes from MT-20261016T2114Z. `prepare` changed and
committed only the tree. The real `arm_readiness._plan_tree` therefore raised
`readiness_pack_digest_mismatch: plan-tree sidecar does not authenticate exact bytes`.

`smoke.prepare` now writes the GNU-format sidecar from the reduced bytes and
commits both files together, before writing the window plan. The regression
runs real Git clone/commits, real ledger-head validation, real venv/wrapper
creation, real plan writing and real `_plan_tree` on a full disposable
checkout of this repository, retaining all production code, scripts, pack
and member-config files. Its interpreter seam selects the VM's Python. The
controller's real `_authenticate_g2b_pre_slot_attachment` then reaches the
calibration-ledger lookup. Only its preceding launch-locator/writer-lineage
seams and the hardware-finalized slot lookup are supplied by the test.

Authenticated-file audit: the ledger and pin are copied byte-for-byte; the
pin is committed. `calibration_plan.json` and its sidecar are unchanged. The
test checks every `*.sha256` in the pack, the clean committed pack worktree,
the window plan's `plan_tree_sha256`, and its `pack_sha256` against the real
`committed_pack_tree_sha256`. Plan inputs do not contain an independently
supplied pack/tree digest; the writer computes both after the clone commit.
Copied identity inputs have their locators rehashed as before. Venv, runner,
courier and smoke-state files have no authenticated sidecar to update.

The related classification fault was also reproduced: a failed stage plus
`agent.presence` returned `physics`. It now returns `fail` if no member bundle
was produced and there is no explicit physical arm/chain stop. `desk` checks
archived claim/bound bundle metadata to supply that fact. Genuine module
arm refusals are explicitly retained as physical outcomes. The acceptance
record's `physics_stop` boolean also covers incidental member exclusions;
only its `physical_stop_kind` identifies an actual physical stop. A further
regression first failed on that production-shaped record, then passed once
the precedence check used the specific field. Red log:
`/tmp/tmp.o80Q1OqwdT/acceptance-red.log`.

### 2. The agent-presence interval could not pass production flag validation

The driver supplied `monotonic_ns` and `wall_s` but omitted the required
`monotonic_raw_ns` key. `make_flag` rejects that interval; the driver catches
the exception and continues without the flag. The old test harness called
`build_flag`, which constructs records without validating them.

The driver now supplies `monotonic_raw_ns: null`. Agent-pause episode stamps
have no RAW readings, so a RAW pair must not be invented. The entire driver
harness now calls production `make_flag`. Its existing missing-run-clock test
failed before the fix with zero presence flags instead of one; afterward it
checks the real schema-valid flag and real exclusions: overlapping and
unplaced members are excluded, a later member is retained.

Emitter sweep: all three explicit driver interval sites were inspected
(census, monitor restart, agent presence). The first two already
supply RAW pairs or null. The full driver harness validates its emitted
flags. `hazards/battery.py`, `thermal.py`, `clock.py` and `contention.py` return
internal findings, not flag records, and the monitor API has no production
caller emitting those findings directly. The collection/harvest path uses
`b5.harvest`'s joins and `FlagLedger.emit`, which merges partial intervals
with `NULL_INTERVAL`. The new `tests.flags.test_b6_emitters` executes the
real `monitor_joins`, real journal reader and real ledger emitter, then
rebuilds every resulting flag with `make_flag`. It covers battery charging,
thermal pressure, clock frequency change and step overlap with a member,
a capture or neither, disk-low records and missing-evidence disclosures.
Core, acceptance and session writers already use `make_flag`; all flag
modules were run. No hazard emitter fix was needed.

The prompt's `joulewise/harvest.py` does not exist on this base. Its actual
owner is `joulewise/b5/harvest.py`, which was inspected and left unchanged;
no out-of-scope write is needed. The refusal inventory passes unchanged.
No registry test requires a new executing-review row. I have not claimed
an independent review that has not happened; the lead can add the exact
implementation commit `8c42d38a6f58a8e0db37419171b61f51f622a719` to
`configs/b6/executing_reviews.json` after review.

## Machine-test changes

- The smoke courier wrapper executes the clone's production
  `scripts/b6_courier.sh`, including its local request capture, heartbeat and
  `courier.sent` protocol. It sends no mail through an agent.
- Injection waits for an unpaired run-start row and starts the fake agent
  while that run is in flight, instead of waiting for its end. The default
  lifetime now matches the page's 45 s: longer than the 30 s census period,
  with half a period of slack. No measurement tolerance changes.
- A night result arriving during the busy phase reaps those children and
  writes `busy_ended` with reason `night_result` before the exit record.
- Agent-pause detail exposes both the journal check and `flags_written`,
  based on the archived flag file. The CLI prints those checks too.
- `collection ran` checks the reduced plan roster against every member's
  summary, its cap reason and the actual exclusion set. Ordinary and
  agent-overlap members must finish successfully. The intentional cap
  member has production status `failed` plus metadata reason
  `wait_cap_reached`; `skipped` is the wait journal's outcome, not a valid
  bundle status. An arbitrary failed run or a cap flag without its reason
  cannot satisfy this item.
- The machine-test page describes the fixed authentication, courier,
  overlap injection, cleanup and collection checks and calls for a fresh
  pin and Mac run.

## Regression evidence (before and after)

Before-fix replay loads the base commit's production module bytes using
`git show 729449fa0:<path>` and `exec(compile(...), module.__dict__)`, then
runs the current test cases in a fresh Python process. Checkout files are
never rolled back. The 12-case replay produced **6 assertion failures and
6 errors**, all expected. Log: `/tmp/tmp.kBqrsU3Jha/regressions-before.log`.
The strengthened real-venv/real-ledger prepare case was replayed separately
and still failed at the exact `_plan_tree` error:
`/tmp/tmp.QtKsfCW9Vm/real-prepare-before.log`. The final full-checkout
version was separately replayed against the base module: same exact
sidecar error in `/tmp/tmp.uWFPJRxWpR/full-checkout-before.log`. The exact report recipe was
then rerun with the additional incidental-acceptance subcase: 12 cases,
7 assertion failures and 6 errors (one case has two failing subcases), as
expected: `/tmp/tmp.e4VPQSy5yX/report-replay.log`.

| New or strengthened test | Before-fix proof | Fixed result |
|---|---|---|
| `SmokeTests.test_prepare_authenticates_production_tree_and_controller_pre_slot` | Real `_plan_tree` raises the exact sidecar error | Pass; both digests, every sidecar and controller handoff checked |
| `SmokeTests.test_stage_crash_without_bundles_dominates_injected_physics` | `physics != fail` | Pass |
| `SmokeTests.test_19_ledger_copy_guards_and_plan_binding` (courier assertion) | Wrapper has only the old stub, no production courier path | Pass |
| `SmokeTests.test_22_desk_pass_physics_fail_and_index` (stage-physics case) | Real desk returns `physics != fail` | Pass; additional genuine battery-arm refusal guard also passes |
| `B6ReviewRegressionTests.test_presence_interval_without_run_clock_excludes_only_overlaps_and_unknown` with `make_flag` harness | Presence-flag count `0 != 1` | Pass |
| `InjectTests.test_sequence_no_children_during_arm_and_reap_on_cap_then_terminal` | Spawn at synthetic second 3 (end), expected 2 (start) | Pass |
| `InjectTests.test_injects_into_first_open_run_without_waiting_for_an_end` | No children spawned for an open first run | Pass |
| `InjectTests.test_duration_hard_limit_and_early_terminal_cleanup` (terminal check) | No `busy_ended` row (`StopIteration`) | Pass |
| `ReportTests.test_all_records_observed_and_structure_only_print` | Missing `collection ran` item (`KeyError`) | Pass, 16/16 observed |
| `ReportTests.test_collection_rejects_missing_failed_or_unexpected_skip` | Missing collection item (`KeyError`) | Pass for missing, failed and invalid skipped summaries |
| `ReportTests.test_collection_does_not_excuse_a_crash_with_only_a_cap_flag` | Missing collection item (`KeyError`) | Pass |
| `ReportTests.test_agent_detail_names_missing_presence_flag` | Missing `flags_written` detail (`KeyError`) | Pass |
| `CollectionEmitterTests.test_all_monitor_emitters_build_valid_flags` | Passing sweep control; these emitters were already valid | Pass |

Existing resume-fallback timing expectations and synthetic report fixtures
were updated consistently. The synthetic flags now come from `make_flag`
with the real block-6 catalog, and their exclusions from the real
`exclusions.compute`; all four members have bundle-summary records.

## Commands and outcomes

Every test invocation exported a new `TMPDIR=$(mktemp -d)` under `/tmp`
(with neither forbidden substring) and `JW_B5_SYNTHETIC_ONLY=1`. Python
3.13.5 was used with `-B`. The whole suite was not run, as instructed.

| Command / check | Outcome / evidence |
|---|---|
| `git fetch origin lane/2026-10-16-b6-round2:refs/remotes/origin/lane/2026-10-16-b6-round2`; `git switch -c fix/2026-10-16-b6-mt-fixes origin/lane/2026-10-16-b6-round2` | Correct base `729449fa0`; clean initial checkout |
| `mkdir -p /opt/homebrew/bin` before the requested symlink | OS permission denied; VM user is `agent`, no sudo available. User was asked asynchronously to provision `/opt/homebrew/bin/python3.13 -> /usr/bin/python3.13`.  |
| Baseline: `python3.13 -B -m unittest tests.b6.test_smoke tests.test_b6_machine_test tests.test_b5_driver` | 81 tests; 3 existing Linux driver failures, listed below. `/tmp/tmp.NhK0EWhaHL/baseline.log` |
| Final focused: `python3.13 -B -m unittest tests.test_b6_machine_test tests.b6.test_smoke tests.test_b5_driver.B6ReviewRegressionTests tests.flags.test_b6_emitters` | 43 tests pass. `/tmp/tmp.DUKq8G56Lh/final-focused.log` |
| Final full-checkout prepare and arm guard: `python3.13 -B -m unittest tests.b6.test_smoke` | 14 tests pass after final smoke/test changes. `/tmp/tmp.FGBV5DwheJ/full-checkout-prepare.log` |
| `python3.13 -B -m unittest discover -s tests/b6 -t .` | 242 tests; 31 failures and 4 errors from VM interpreter/storage limits, detailed below. `/tmp/tmp.SQKduU39H2/b6.log` |
| Final machine module: `python3.13 -B -m unittest tests.test_b6_machine_test` | 26 tests pass after the final shared-lifetime constant change. `/tmp/tmp.BRciNvgNT4/final-machine.log` |
| `python3.13 -B -m unittest tests.test_b5_driver` | 46 tests; same 3 baseline failures. `/tmp/tmp.p6fGcm1Om2/driver.log` |
| `python3.13 -B -m unittest discover -s tests/flags -t .` | 176 tests, OK (1 skipped). `/tmp/tmp.pOexKwa6Zx/flags.log` |
| `python3.13 -B -m unittest tests.hazards.test_refusal_allowlist tests.test_b6_idle_wait` | 34 tests, OK (1 skipped). `/tmp/tmp.XmyRkHV9ou/allowlist-idle.log` |
| Exact production courier Python body, extracted with `shlex.split` and executed with `/usr/bin/python3.13 -B -c`, real synthetic stdin and driver prompt | Exit 0, `courier.sent` created, local request persisted, `mail_sent=false`. `/tmp/tmp.pEejHnChkD/courier-custody` |
| Real `b6_machine_test.main(['report', '--state', ...])` over the extended fixture, using its recorded synthetic desk result | CLI exit 0; all 16 items observed. `/tmp/tmp.EvGioBm1jW/synthetic-machine-output/out/report.json` |
| `python3.13 -B scripts/fixture_orphan_census.py --fail-on-orphans` | Exit 0; `[]`. `/tmp/tmp.qDQRHA2kyK/final-census.json` (repeated after the long discovery run) |
| `git diff --check` | Pass |
| `git commit -m "Fix block-6 smoke authentication and agent-presence flags"` | Success: `8c42d38a6f58a8e0db37419171b61f51f622a719`; 8 scoped implementation/test/doc files |
| `git push -u origin HEAD:fix/2026-10-16-b6-mt-fixes`; `git ls-remote origin refs/heads/fix/2026-10-16-b6-mt-fixes` | Success; remote confirmed implementation SHA `8c42d38a6f58a8e0db37419171b61f51f622a719`. The following report-only commit is verified in the final handoff. |

The unchanged driver failures are
`LaunchTests.test_disk_low_stops_the_chain_and_is_recorded`,
`LaunchTests.test_survivors_of_a_natural_exit_are_proven_gone_before_the_exit_is_recorded`,
and `UnitTests.test_the_monitor_disk_low_marker_stops_the_chain`.
They return 6 instead of 4/0 both before and after. A focused real-process
probe confirmed `aborted_reason=night_chain_alive`, `chain_exit_code=-15`,
`termination_proven=false`, and no courier invocation: Linux process-group
termination proof, not the changed flag builder or courier. These are
recorded limitations, not claimed green checks. No production termination
policy was weakened to satisfy a VM test.

The block-6 discovery's 31 assertion failures all cite the absent
`/opt/homebrew/bin/python3.13` (loop/chain fixtures fail in `SMOKE_RUN`, and
the production courier exits 127). Of the 4 errors, 3 are `Errno 28` while
the full-pack fixture builds successive cases on the roughly 9 GB `/tmp`
volume. The remaining error is the unchanged compression restore test:
a focused rerun recorded `(3, {'reason': 'restore_space', ...})`, because
its existing 20 GiB reserve exceeds the volume's capacity. Evidence:
`/tmp/tmp.qDQRHA2kyK/restore-diagnosis.log`. Neither that disk policy nor the
unrelated fixture code was changed. These full discovery results are not
represented as green; the final touched modules were also rerun separately.

## Reproduce the before-fix test replay

This is the replay command's procedure (the real-prepare test now includes
its stronger real ledger and venv steps):

```sh
export TMPDIR=$(mktemp -d)
export JW_B5_SYNTHETIC_ONLY=1
python3.13 -B - <<'PY_REPLAY'
import subprocess, unittest
from joulewise.b6 import smoke
from joulewise.b5 import driver
from scripts import b6_machine_test
from tests.b6.test_smoke import SmokeTests
from tests.test_b5_driver import B6ReviewRegressionTests
from tests.test_b6_machine_test import InjectTests, ReportTests
for module, path in ((smoke, 'joulewise/b6/smoke.py'),
                     (driver, 'joulewise/b5/driver.py'),
                     (b6_machine_test, 'scripts/b6_machine_test.py')):
    source = subprocess.run(['git', 'show', '729449fa0:' + path],
        capture_output=True, text=True, check=True).stdout
    exec(compile(source, path, 'exec'), module.__dict__)
cases = [
    (SmokeTests, 'test_prepare_authenticates_production_tree_and_controller_pre_slot'),
    (SmokeTests, 'test_stage_crash_without_bundles_dominates_injected_physics'),
    (SmokeTests, 'test_19_ledger_copy_guards_and_plan_binding'),
    (SmokeTests, 'test_22_desk_pass_physics_fail_and_index'),
    (B6ReviewRegressionTests, 'test_presence_interval_without_run_clock_excludes_only_overlaps_and_unknown'),
    (InjectTests, 'test_sequence_no_children_during_arm_and_reap_on_cap_then_terminal'),
    (InjectTests, 'test_duration_hard_limit_and_early_terminal_cleanup'),
    (InjectTests, 'test_injects_into_first_open_run_without_waiting_for_an_end'),
    (ReportTests, 'test_all_records_observed_and_structure_only_print'),
    (ReportTests, 'test_collection_rejects_missing_failed_or_unexpected_skip'),
    (ReportTests, 'test_collection_does_not_excuse_a_crash_with_only_a_cap_flag'),
    (ReportTests, 'test_agent_detail_names_missing_presence_flag'),
]
result = unittest.TextTestRunner(verbosity=2).run(
    unittest.TestSuite(cls(name) for cls, name in cases))
assert len(result.failures) + len(result.errors) >= len(cases)
PY_REPLAY
```

## Synthetic report and Mac-only observations

The extended fixture produces schema-valid flags, real exclusions, a
production reduced-plan roster, run-clock/presence/wait journals, sampler
attempt/teardown records and per-run summaries. The real report CLI reads
that output tree. It reports all of: agent pause, agent census, runner
pause, fresh idle admission, idle cap, sampler restarts, sampler startup
readings, sampler clean termination and no survivor, meter unplugged,
collection ran, keep-awake, per-run sleep readings, chain exit, smoke desk,
smoke errors absent, harvest exit. All **16/16** are observed. Agent detail
prints `flags_written=True`. These are synthetic observations; the cached
desk outcome and sampler proofs are fixture inputs, not fresh hardware or
a full harvest/collection run on Linux.

Only the quiet Mac can establish the installed launchd night/injector route,
real 30 s census detection during a real member, actual pause/resume and
idle admission at the physical power line, a full cap wait, powermetrics
startup/restarts/termination and absence of real survivors, keep-awake/sleep
behavior, MLX completion and the live harvest/desk outcome. The hardware
run keeps the meter connected: its unplugged item is expected to be
unobserved, while the absent path is observed only in the desk fixture.
No `/Users` paths were used and no live measurement was started here.

## decisions I made

1. Design sections 3.1 and 10 require a pipeline pass and say non-physical
   smoke failures hold the pack, but do not specify precedence for a
   coincident injected physical flag. I used the prompt's permitted rule:
   stage/code failure dominates incidental physical flags when no bundle
   exists; an acceptance `physics_stop` boolean without `physical_stop_kind`
   is still incidental. Explicit physical arm refusals/chain stops retain their physical
   outcome. This is a smoke diagnostic change, not a new collection refusal.
2. Presence episodes have no RAW timestamps; represent that domain as null,
   matching the other production call sites. Do not synthesize readings.
3. Use the existing production, mail-free courier through the generated
   smoke wrapper, so the hardware test exercises the real sentinel protocol.
4. Use the page's existing 45 s fake-agent duration as both defaults. Its
   derivation is the 30 s census period plus half a period of slack; no new
   energy agreement bar, physical threshold or tolerance was introduced.
5. A cap run must carry the controller's failed-summary and cap-reason
   combination. Other planned members must succeed, and only the expected
   overlap/cap exclusions may appear. A flag alone cannot excuse a crash.
6. Keep executing-review evidence honest: the lead review is pending, so no
   row claiming it has happened was added. Inventory guards pass unchanged.
7. Keep the three pre-existing Linux process-proof failures and the protected
   interpreter-path limitation explicit. They do not justify unrelated
   production changes or writes beyond the supplied scope. No NEEDS_RULING
   choice changing a printed number or data-count policy remains.
