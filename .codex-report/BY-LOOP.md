# BY-LOOP — local implementation in progress

## PROGRESS

- DONE (prior committed slice 9de9ae0a5): dedicated BYTES root, guard/no-tick sentinel, scratch rehearsal, item 48 relay audit and record-only item 6 disposition. Clean tree at this slice start; descendant baseline confirmed.
- IMPLEMENTED item 4: smoke.py reads campaign member evaluations for anchor-only rc 1 explanation; desk caller no longer requires idle flags. Expanded existing exact-dispatch desk regression with anchor-only and three rejection cases. Fails-before: 1 test, anchor subcase failed (`fail != pass`), 1.123s, exit 1. Passes-after: 1 test, 1.615s, exit 0. Companion-member rejection added and passed; focused final regression PASS (2.014s); full combined run completed 81 tests / 204.993s, four failures from attempting recovery on incomplete/crashed chains. Fixed caller to attempt only when all failing exits are exactly rc 1. Final focused regression rerun: 3 tests / 2.420s / exit 0 (anchor matrix, incidental-physics crash controls, named physical stops).
- CURRENT slice 3: clean start b8a25c2e179dd6e76c9890e00d3ba016230ae919. Final loop module PASS: 59 tests / 25.019s / exit 0. Final smoke module PASS: 22 tests / 183.653s / exit 0. Round-desk alpha/session/rotation PASS: 1 test / 136.630s / exit 0; resume PASS: 1 test / 136.594s / exit 0. Lost-session FAIL: exception:RuntimeError:SESSION_RUN instead of structure_defect, 1 test / 85.125s / exit 1. Diagnostic rerun PASS: 1 test / 126.950s / exit 0; HOLD_DIAGNOSTIC None and both INSTALL_STDERR entries empty. Earlier failure not reproduced; retain as unresolved transient, do not claim it fixed. All test sessions from this slice are finished. Prior session 60415 cannot be recovered in this fresh tool session. No DIRECTOR NOTES present at intake.
- NEXT: run tests.b6.test_loop_round_desk.RoundTests.test_physics_refusal_wait_reprepare_then_retry, then test_stops_close_bracket_advance_pin_and_reach_next_smoke (one case per invocation, budget the four-stop loop). Retain lost-session first-fail/rerun-pass discrepancy for lead verification. Continue identifying historical item 5 runner; no scope expansion identified yet. Run each module (each module gets its own fresh TMPDIR); trace item 5 with bounded candidates. No whole suite. Do not call launchctl or access production state.
- DIRECTOR REQUEST: preserve/read any archived s3-cold scratch runner command or script that launched the historical .scratch-fix/tmp/s3-run monitor; no tracked s3-run source found. Do not expand scope without an identified path.
- OPEN: process visibility blocked in this sandbox: pgrep exits 3 (`sysmond service not found`); /bin/ps denied. No monitor child started by this slice. Cannot claim leak reproduction/census. Production BYTES sizing remains external. Director owns commits/pushes/CI. No scope request yet.

- Slice 3 hygiene finding (separate from historical real monitor): live orphan-census test spawned a fake meter BEFORE learning ps is denied, then skipped while its cleanup also required ps. Added a pre-spawn inventory check plus regression; fails-before 1 test / 0.190s / exit 1, with spawn trapped (no child created). Full post-fix census PASS: 15 tests / 0.484s / exit 0 / 2 skips (sandbox ps). Historical hazard-monitor source still unproven.

## SUMMARY

- Status: PARTIAL local implementation. Dedicated BYTES queue, CLI config-root selection, DONE guard and scratch rehearsal passed. Item 4 final loop/smoke runs passed. Census now checks process visibility before creating a fake orphan. Two round-desk cases and the historical real-monitor leak remain pending.
- Base confirmed through connected GitHub: `bda481d5af510b29dde4976f172a20170a42c955`.
- BY-INT's lane head still equals that base; no base movement was observed.
- No earlier BY-LOOP lane branch existed when checked.
- Governing block-6 and BYTES registration texts were read; a dedicated BYTES root is the implementation choice below.
- Item 48's live yield notice is built inside the sealed block-5 driver; the authorized known-false-alarm disposition is recorded.
- The duplicate close notice is traced to the magistrate's manual step; loop wake remains the chosen single owner.
- Only scoped production/test/config/report files changed; production registrations, measurement state and sealed files remain untouched.
- Final loop module: 59 tests passed; final smoke module: 22 tests passed. Rehearsal passed. Two round-desk cases passed; lost-session failure and historical monitor leak remain open.

## LOOP ROOT CHOICE

Dedicated root implemented in configs/b6/loop_bytes.json: `/Users/edr/night-b6/loop-bytes`. Production directory never accessed or created.

Authority: `docs/design/block6_collection_draft.md` §6.1 closes once every pack has its target, and §14 makes the pack the unit of registration, collection and release with a queue of open packs. `docs/registrations/block6_replication_DRAFT.md` §14 S-2 identifies the existing replication loop root. `docs/registrations/bytes_pack_v1.md` §5 fixes twelve independent, fixed, one-session packs and order s1-p1 through s6-p1, then s6-p2 through s1-p2; its authority paragraph requires replication behavior to remain byte-identical.

The dedicated root preserves the replication loop's DONE history and avoids inventing a DONE-to-NEXT reopening rule. Its configuration restricts discovery to the twelve BYTES packs so existing replication registrations cannot be recollected. All twelve belong to the same active BYTES queue. No state under the proposed production path or the existing production root has been read or written by this seat.

## ITEMS

### 1. Twelve-pack loop readiness

Implemented configs/b6/loop_bytes.json with dedicated root, twelve-pack order and explicit pack_ids. loop.py filters discovery to those ids; scripts/b6_loop.py uses selected config root after CLI/environment override. Tests cover discovery and root precedence. tests/b6/round_support.py adds real-entry-point rehearsal helper.

Observed: the default order already includes all twelve BYTES packs, DONE remains terminal in `Loop.tick`, and a fresh root starts at NEXT. Production BYTES registrations at the base remain draft; synthetic rehearsal copies must be explicitly registered-shaped and committed only in scratch.

### 2. DONE tick overhead

Implemented loop.py done.idle publication after successful final mail/wake I/O and an empty pending outbox (delivery or close). Native-zsh guard reads DONE and marker then exits before Python. Explicit state change lets it fall through. NEXT with no open packs still discovers future registrations. Existing DONE roots get the marker on first successful updated tick.

### 3. Item 48: smoke yield notice

**Recorded known false alarm; sealed code left unchanged.**

At base `bda481d5a`, `joulewise/b5/driver.py:1418` builds `yield_plan` from dispatch run IDs, not the reduced tree's kept counts. Its `count_stage` compares succeeded members with `_min_valid(role, planned)`, and `YieldTripwire` owns the live notice; `execute` calls `yield_plan` and constructs that tripwire. The smoke reduces dispatch execution after order resolution in `joulewise/b6/smoke.py`, using `configs/b6/smoke_keep.json`; the full order manifests deliberately remain intact.

Consequently the historical 3/10/10/3 plan can classify four successful one-member smoke stages as LOW. Computing a desk-only kept-count summary in smoke.py would not correct the live driver notice. The item brief expressly allows recording the false alarm when notice construction is confined to driver.py. No threshold, printed quantity, exclusion, or block-5 byte is changed. This item is a source-based disposition, not a successful live smoke test. Local relay audit of smoke.py, loop.py and mailer.py found no LOW/yield alert or desk line relaying the driver count; smoke.py uses yield only as a Python generator in _flag_codes. loop smoke desk carries acceptance status/codes and mailer has no yield relay. Keep the recorded false alarm; no alternative printed number was introduced.

### 4. Item 52 / issue 509: explained anchor fallback

Implemented smoke.py campaign-member record reader and stages_succeeded extension; removed desk caller's idle-flags-only gate. Exact dispatch membership, reduction prefix, rc 1, and successful acquisition/strict validation remain required. A member evaluation must name only anchor_fallback_member_unusable, have rerun_required true and child exit 0. Any companion member in that failed stage needs a usable campaign evaluation or a recorded idle skip; other validation, flags and child exits remain failures. Acquisition status can be succeeded while campaign validation fails (scripts/run_campaign.py MemberEvaluation.failed and rerun_required). No energy quantity or acceptance counting rule changed.

Expanded existing real desk/archive regression to exercise positive anchor-only case, extra collection flag, strict validation failure, nonzero child exit and a separate unexplainable companion member. Before production changes: 1 test in 1.123s, FAILED (anchor subcase fail != pass). After final robustness refinement: same test, 2.014s, OK, exit 0. Initial combined module run: 81 tests / 204.993s / exit 1, four failures from attempting evidence recovery for incomplete chains. Caller now requires every exit to be a success or rc 1, preserving existing crash/physical-stop handling. Focused rerun passed: 3 tests / 2.420s / exit 0.

### 5. Leaked hazard monitor

Historical real monitor not fixed or reproduced: process visibility is denied in this local sandbox. Read `tests/b6/test_s3_cold_fixes.py`, `tests/test_fixture_orphan_census.py`, and `tests/b6/support.py`. The named cold-fix module has no direct Popen call at the base, so the originating process must be traced through its exercised seams or the broader s3-cold execution before asserting a cause. Do not claim the leak is repaired merely because the module contains no direct spawn. Slice 3 found a separate fake-meter leak in the census test itself: it spawned before discovering that ps was denied, then skipped while cleanup also required ps. tests/test_fixture_orphan_census.py now probes inventory before spawning; a trapped-spawn regression failed before and passes afterward. Full census: 15 tests / 0.484s / exit 0 / two environment skips. This prevents new sandbox fake-meter orphans but does not identify or fix historical pid 43816; its process proof remains outstanding.

### 6. Duplicate block-6 close mail

**Recorded; no mailer change. Loop wake is the single owner of the close notice.**

`docs/process_traces/2026-10-21-magistrate-283e9802/RECORD.md`, “Block 6 closed” and “Pruning list”, explicitly identifies the magistrate's manual “email the verdict” instruction as the second sender. `RUN_STATE.md` items 59 and 60 also distinguish the loop wake and that activation. `Loop._next` has one close event; the scoped `joulewise/b6/mailer.py` provides outbox delivery and issue closing, and has no magistrate-specific close dispatcher to prune.

This is a manual orchestration-instruction duplication, so changing the shared mailer would affect the existing loop delivery rather than removing the magistrate's instruction. The historical prose is evidence, not a second executable mailer. No in-scope magistrate sender was identified. The lead should carry loop-wake ownership into the external activation instructions; the requested record-only disposition is used here. No message was sent by this seat.

## REHEARSAL

Local PASS, scratch root /private/tmp/jwtmp-byloop.VDqS8u. Replay from repository root:

```sh
JW_B5_SYNTHETIC_ONLY=1 TMPDIR=$(mktemp -d /tmp/jwtmp-byloop.XXXXXX) /opt/homebrew/bin/python3.13 -B - <<'PY'
import os
from pathlib import Path
from tests.b6.round_support import bytes_rehearsal
print(bytes_rehearsal(Path(os.environ['TMPDIR'])))
PY
```

Exit 0. Layout: measurement/{configs,joulewise,scripts,.git,.venv}, loop.json, loop-bytes/{state.json,staging}, bin/launchctl, launchctl.argv, rehearsal.json. Twelve registered-shaped synthetic registrations and full plan/config trees committed only in scratch. Three calls through real scripts/b6_loop.py via runpy; real open_packs, composition, DriverLane preparation and smoke.prepare. Hardware identity/precheck, transport, stop-ref network observation and launch are synthetic seams. Fake first on PATH and driver.launchctl_bin set to it. Launch executes only fake; no install/arm.

Observed: NEXT → PRECHECK → SMOKE_RUN → SMOKE_RUN. Discovered 12; selected bytes-s1-p1; prepared r1-bytes-s1-p1-smoke-0. Isolated smoke clone, reduced tree, copied ledger/pin, wrapper and session.json exist. Deferred plan path ends smoke/bytes-s1-p1-20261022T0758Z/custody/night_plan.json. Fake argv log: `rehearsal-only r1-bytes-s1-p1-smoke-0`.

Fixture sizing copies ALPHA allowances explicitly; max_s=124620 is a synthetic formula result, not BYTES sizing evidence. Production C5 sizing is absent and remains external. First attempt repeated NEXT because runner omitted capture_output/text defaults; fixed runner and replay passed. Director independent repetition remains outstanding.

## DONE TICK

Native-zsh DONE plus done.idle fast path skips the tick executable. test_done_guard_skips_tick_and_resume_invalidates supplies JW_B6_LOOP_TICK as harmless touch of python-started sentinel: guard exits 0 in DONE with no sentinel, then creates sentinel with state NEXT. Marker published only after successful final I/O; first updated DONE tick creates it, subsequent ticks skip Python.

## TESTS RUN

Repository cwd; each command uses fresh TMPDIR and synthetic-only:

```sh
JW_B5_SYNTHETIC_ONLY=1 TMPDIR=$(mktemp -d /tmp/jwtmp-byloop.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.test_b6_loop
```

Initial run exit 0: 57 tests in 32.572s, OK (before DONE guard addition). Final rerun exit 0: 58 tests in 23.646s, OK; no skips.

```sh
JW_B5_SYNTHETIC_ONLY=1 TMPDIR=$(mktemp -d /tmp/jwtmp-byloop.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.test_b6_loop.LoopTests.test_dedicated_bytes_config_limits_discovery_and_starts_next tests.test_b6_loop.LoopTests.test_cli_config_root_and_explicit_override tests.test_b6_loop.LoopTests.test_done_guard_skips_tick_and_resume_invalidates
```

Exit 0: 3 tests in 0.076s, OK, no skips. Rehearsal above exit 0. No whole suite. Stages/leak fails-before/passes-after pending.

`pgrep -fl hazard_monitor`: exit 3; `sysmon request failed with error: sysmond service not found`; `pgrep: Cannot get process list`. No processes killed. Need usable process evidence for leak investigation.

After final outbox refinement: `JW_B5_SYNTHETIC_ONLY=1 TMPDIR=$(mktemp -d /tmp/jwtmp-byloop.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.test_b6_loop.LoopTests.test_done_dormancy_waits_for_outbox_retry tests.test_b6_loop.LoopTests.test_done_guard_skips_tick_and_resume_invalidates`: exit 0, 2 tests in 0.032s, OK. `git diff --check`: exit 0.

## SEALED INVENTORY

682 paths. Local working-tree-inclusive intersection of inventory files with `git diff --name-only bda481d5a` plus `git ls-files --others --exclude-standard`: sealed_paths: 682; changed_overlap: []. No sealed file changed. After director commit, required committed check is `git diff --name-only bda481d5a HEAD` against the same inventory.

## CI

Draft PR **#542**, `ci/2026-10-22-bytes-loop` against main, titled “CI: BYTES loop readiness (BY-LOOP)”: https://github.com/mpmdw/JouleWise/pull/542.

Checkpoint `c2a7dd5025079c2ab01bc5aaf2ea845434171c2b` was verified as the exact head of both lane and CI branch through connected GitHub. Its CI workflow was observed pending (run 39743424315); gate-ledger completed with failure (run 39743424387). The failure reason was not inspected; no claim of green checks is made. The earlier report checkpoint had both workflows in progress. This final commit changes only the report and is fast-forwarded to the CI branch as well. No code-readiness result is claimed; the PR body explicitly says implementation and execution remain blocked. Do not merge.

## DECISIONS I MADE

- Use a dedicated BYTES root rather than reopening the replication loop, for the governing reasons above; implementation and scratch rehearsal are complete.
- Record item 48's known live LOW false alarm under the brief's explicit sealed-driver exception.
- Keep loop wake as the single owner of close notification; record the external/manual magistrate duplication without changing the shared mailer.
- Preserve cloud source findings; local slice now supplies filesystem execution evidence.
- Do not substitute unit-only, remote source-reading or historical evidence for the required synthetic real-entry-point rehearsal.

## OPEN ISSUES

- Item 4 implemented with focused regressions passed; remaining round-desk runs/failure and historical item 5 leak remain pending; final smoke passed. Item 48 relay audit complete; recorded false alarm retained.
- Prior slice completed mailer, chain reduction, cold fixes and refusal census; final loop/smoke and updated orphan census now pass. Two round-desk cases remain unrun, lost-session failed, and import-graph GO verification is blocked by sandbox pgrep.
- Production BYTES C5 sizing absent; scratch values are synthetic only.
- Director independent rehearsal, final review, commit/push and CI refresh outstanding.

## NEEDS_RULING

none. Historical monitor source remains unidentified; process visibility and external CI/live gates remain lead-owned.

### Local slice 2 verification checkpoint

Every test command used JW_B5_SYNTHETIC_ONLY=1 and Python `/opt/homebrew/bin/python3.13 -B -m unittest`, with fresh `TMPDIR=$(mktemp -d /tmp/jwtmp-byloop.XXXXXX)` per invocation. Exact module suffixes and observed results:

- `tests.b6.test_smoke.SmokeTests.test_desk_idle_loss_requires_exact_dispatch_records_and_campaign_exit`: before exit 1 / 1 test / 1.123s; after exit 0 / 1 test / 2.014s (includes final companion-member rejection).
- `tests.test_b6_mailer`: exit 0, 10 tests, 0.075s, OK.
- `tests.b6.test_chain_smoke_reduction`: exit 0, 1 test, 0.071s, OK.
- `tests.b6.test_s3_cold_fixes`: exit 0, 6 tests, 0.236s, OK.
- `tests.hazards.test_import_graph`: exit 1, 6 tests, 6.969s; arm decision NULL != GO (sandbox hardware/process seam; investigate before disposition).
- `tests.hazards.test_refusal_allowlist`: exit 0, 23 tests, 79.883s, OK (skipped=1).
- `tests.test_fixture_orphan_census`: exit 0, 14 tests, 0.599s, OK (skipped=2; sandbox process visibility).
- `tests.b6.test_smoke.SmokeTests.test_22_desk_pass_physics_fail_and_index -v`: exit 0, 1 test, 0.522s, OK.
- `tests.test_b6_loop tests.b6.test_smoke`: exit 1 / 81 tests / 204.993s / four smoke failures before final caller correction; invocation inadvertently shared TMPDIR across these two modules, so independent final per-module runs required. Four failures visible in smoke portion; loop portion had no reported failures.
- `tests.b6.test_smoke`: independent exit 1 / 22 tests / 190.360s, same four pre-fix failures as combined run; final caller guard regression passed afterward. Full final module rerun remains due.
- `tests.b6.test_loop_round_desk`: pending session 60415.
- Focused existing clone/ledger tests: 2 tests / 1.963s / exit 0.

`pgrep -fl hazard_monitor` before test investigation: exit 3 / sysmond service not found / Cannot get process list. `/bin/ps -axww -o pid=,ppid=,command=` denied (operation not permitted). Historical source confirms pid 43816 used `.scratch-fix/tmp/s3-run` in s3cold checkout, but no spawning test positively identified. No process killed by this slice. No leak-fix claim.

Final sealed check: 682 paths; changed_overlap: [] (working-tree-inclusive diff from bda481d5a plus untracked paths). git diff --check exit 0.

### Local slice 3 verification checkpoint

All test commands use repository cwd, `JW_B5_SYNTHETIC_ONLY=1 TMPDIR=$(mktemp -d /private/tmp/jwtmp-byloop.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest`, with one fresh TMPDIR per invocation.

- `tests.test_b6_loop`: exit 0 / 59 tests / 25.019s / OK.
- `tests.b6.test_loop_round_desk.RoundTests.test_alpha_smoke_session_desk_and_beta_rotation`: exit 0 / 1 test / 136.630s / OK.
- `tests.test_fixture_orphan_census.FixtureOrphanCensusTests.test_unavailable_inventory_skips_before_starting_an_orphan`: before fix exit 1 / 1 test / 0.190s. Spawning was trapped, so no orphan was created by this reproduction.
- `tests.test_fixture_orphan_census`: after fix exit 0 / 15 tests / 0.484s / OK (skipped=2; ps unavailable).

Import-graph failure diagnosis (no change to production hazard behavior): `JW_B5_SYNTHETIC_ONLY=1 TMPDIR=$(mktemp -d /private/tmp/jwtmp-byloop.XXXXXX) /opt/homebrew/bin/python3.13 -B -` calling `Rig(Path(os.environ['TMPDIR'])).run()` returned NULL solely because instrument group census exited 3: sysmond service not found / Cannot get process list. The real child returned 0 and 300 fixture frames; group_gone remained false. This verifies the sandbox cause, not a GO run. Director must rerun tests.hazards.test_import_graph with process visibility.

Static leak audit: tests/test_b5_driver.py Harness injects fake_monitor_argv and registers process_reaper; p3 imports that Harness. Gate-prune integration validates monitor argv but does not launch it. Battery tests inspect source only. Magistrate tests inject spawn. Round support prevents run_night execution in installer preflight. tests/test_b6_machine_test.py traps real Popen/run in Case.setUp. No tracked test or script contains s3-run; historical record names a .scratch-fix/tmp/s3-run path. The originating historical runner has not been identified; do not attribute the census fake-meter issue to pid 43816. No real hazard monitor started in this slice, no unowned process signalled.

Sealed check, exit 0: parse `configs/campaigns/v5_claim_25g83/sealed_inventory.json` files, intersect with `git diff --name-only bda481d5a` plus untracked files; output `sealed_paths: 682`, `changed_overlap: []`. `git diff --check`: exit 0.

Slice 3 completed results (same exact command prefix above):

- `tests.b6.test_smoke`: exit 0 / 22 tests / 183.653s / OK.
- `tests.b6.test_loop_round_desk.RoundTests.test_resume_after_hold_continues_real_round`: exit 0 / 1 test / 136.594s / OK.
- `tests.b6.test_loop_round_desk.RoundTests.test_lost_session_reaches_desk_and_holds_before_beta`: exit 1 / 1 test / 85.125s. Expected structure_defect; got exception:RuntimeError:SESSION_RUN. Investigating, not accepted as an environment failure yet.

Committed sealed check also passed: `git diff --name-only bda481d5a HEAD` intersected with sealed inventory files yields `committed sealed_paths: 682`, `committed changed_overlap: []`. Current slice writes only report and tests/test_fixture_orphan_census.py; no commits or pushes attempted.

Lost-session diagnostic rerun, exit 0 / 1 test / 126.950s / OK. Exact replay (repository cwd):

```sh
JW_B5_SYNTHETIC_ONLY=1 TMPDIR=$(mktemp -d /private/tmp/jwtmp-byloop.XXXXXX) /opt/homebrew/bin/python3.13 -B - <<'PY'
import unittest
from tests.b6.round_support import Round
original = Round.until
def observed(self, *args, **kwargs):
    result = original(self, *args, **kwargs)
    if self.state()['state'] == 'HOLD_LOOP':
        print('HOLD_DIAGNOSTIC:', self.state().get('last_exception'), flush=True)
        for path in self.loop_root.rglob('install.stderr'):
            print('INSTALL_STDERR:', path.read_text(), flush=True)
    return result
Round.until = observed
suite = unittest.defaultTestLoader.loadTestsFromName('tests.b6.test_loop_round_desk.RoundTests.test_lost_session_reaches_desk_and_holds_before_beta')
result = unittest.TextTestRunner().run(suite)
raise SystemExit(not result.wasSuccessful())
PY
```

Observed HOLD_DIAGNOSTIC None, two empty INSTALL_STDERR entries. No behavior substitution; diagnostics only wrap Round.until. Earlier exception hold not reproduced, source unresolved. No claim of a fix or environmental explanation for that earlier failure.
