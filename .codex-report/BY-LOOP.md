# BY-LOOP — implementation complete; director publication pending

## PROGRESS

- SLICE 5 DONE: F-A/F-B regressions failed before (3 tests / 0.030s / three failures). CLI config lookup by resolved root, duplicate rejection, top-level-only DONE guard and control marker invalidation implemented. Full loop module passed (61 / 9.536s / exit 0); new guard-shaped rehearsal CI test passed (1 / 15.226s / exit 0). Standalone rehearsal passed at /private/tmp/jwtmp-byloop.ZhKeYM: NEXT → PRECHECK → SMOKE_RUN → SMOKE_RUN; packs [bytes-s1-p1]; discovered 12; fake launchctl only. Report refreshed with director results, scoped/sealed diff reviewed.
- NEXT: director review/commit seven scoped changed files, independent updated rehearsal, lane/CI publication and PR #542 CI refresh. No commit or push attempted by this seat.
- OPEN: production BYTES sizing external; SIGKILL cannot execute Python cleanup; independent updated rehearsal/current CI pending. No SCOPE REQUEST. NEEDS_RULING none.

- DIRECTOR NOTES (before slice 5, 2026-10-22 13:50Z). Slice 4 committed as 9e38914c6.
  - DIRECTOR RESULTS, outside the sandbox, fresh /private/tmp TMPDIR per module (copy these into TESTS RUN):
    item 5 live census (scratchpad driver: start one real SupervisorTests case, wait for the monitor's "start"
    journal line, signal the runner only, let it exit, run the census CLI with the new registry):
    unfixed test file (6129d0475) SIGINT -> runner rc -2, census 1 row `hazards-test-real-monitor` ppid 1;
    SIGTERM -> runner rc -15, census 1 row; both orphans then killed by the director. Fixed (slice 4) SIGINT -> rc -2,
    census []; SIGTERM -> rc -2 (handler re-raises as KeyboardInterrupt), census []. pgrep hazard_monitor empty after.
    Regression counterfactual (SupervisorTests.run replaced by a pre-fix run that only sets _supervisors):
    SupervisorCleanupTests 2 FAIL "ProcessLookupError not raised"; census [] afterwards (the regression's own finally
    reaped). Fixed: 2 OK. Modules at 9e38914c6: tests.hazards.test_import_graph 6 OK (the sandbox NULL-vs-GO failure
    was ps denial, now settled); tests.hazards.test_monitor 37 OK in 70.2 s (live classes ran, no skips);
    tests.test_fixture_orphan_census 16 OK (no skips); tests.b6.test_s3_cold_fixes 6 OK; tests.test_b6_mailer 10 OK;
    tests.b6.test_chain_smoke_reduction 1 OK; tests.test_b6_loop 59 OK; tests.b6.test_smoke 22 OK in 85.3 s;
    tests.hazards.test_refusal_allowlist 23 OK (skipped=1). Round desk at 6129d0475 (b6 code unchanged since):
    test_physics_refusal_wait_reprepare_then_retry OK 59.0 s; test_stops_close_bracket_advance_pin_and_reach_next_smoke
    OK 197.0 s; test_lost_session_reaches_desk_and_holds_before_beta OK 47.9 s (the slice-3 SESSION_RUN failure did not
    recur outside the sandbox). Real DONE root read-only check: /Users/edr/night-b6/loop/state.json has exactly one
    `"state"` line (top level, DONE) and 0 of 12 outbox entries pending, so the first updated tick would publish done.idle.
  - FINDING F-A (blocker, director's executing review of the launchd path). The production tick never passes --config:
    configs/launchd/com.joulewise.b6loop.plist.template sets only JW_B6_LOOP_ROOT, and scripts/b6_loop_guard.zsh execs
    `b6_loop.py tick --loop-root "$loop_root"`. scripts/b6_loop.py then reads configs/b6/loop.json whatever the root. So a
    loop installed at /Users/edr/night-b6/loop-bytes would run with loop.json: base_order alpha, beta, gamma first and no
    pack_ids filter, and a fresh root would select alpha and collect a replication pack again. The rehearsal hid this
    because bytes_rehearsal passes `--config` explicitly. FIX (in scope, scripts/b6_loop.py): with no --config, pick the
    configs/b6/loop*.json in the repo root whose "loop_root" equals the resolved loop root; two matches is an error; no
    match keeps configs/b6/loop.json (scratch roots in tests). Every other caller (status, hold, resume, reharvested,
    the wake) goes through the same CLI, so they inherit it. REGRESSIONS: (i) tests/test_b6_loop.py: a temp repo root
    holding copies of both configs with scratch loop_roots (never a /Users/edr path: Mailer and Loop may create files
    under the root); main() with the guard's exact argv (`tick --loop-root <bytes scratch root>`, no --config) and a
    capturing factory receives the BYTES config (pack_ids present, first order entry bytes-s1-p1); the loop.json root
    and an unknown root receive loop.json; two configs claiming one root fail. Show it fails before the fix.
    (ii) bytes_rehearsal: drop `--config`, call scripts/b6_loop.py with the guard's argv shape
    (`--repo-root <measurement> tick --loop-root <root>/loop-bytes`), rewrite the measurement copy's
    configs/b6/loop_bytes.json loop_root to `<root>/loop-bytes` (and its wake_argv to []), and loop.json's loop_root to a
    different scratch path, so a wrong fallback would select alpha and fail the transition/packs asserts.
    (iii) Add one test in tests/b6/test_loop_round_desk.py that calls bytes_rehearsal on a fresh TMPDIR and asserts its
    result (transitions NEXT, PRECHECK, SMOKE_RUN, SMOKE_RUN; packs [bytes-s1-p1]; fake launchctl argv). It runs in CI on
    Linux (the round-desk module has no platform skip), which is this item's cloud rehearsal while Codex Cloud is offline.
  - FINDING F-B (should fix). The guard's DONE regex accepts `"state": "DONE"` at any indent, so a nested key (e.g.
    last_exception.state) plus a stale done.idle would keep a resumed loop dormant: control() never removes done.idle.
    Fix: match only the top-level key (atomic_state writes indent=2, so exactly two leading spaces), and have
    Loop.control unlink done.idle before it writes state for any command. Regression in tests/test_b6_loop.py: state
    NEXT with a nested `"state": "DONE"` line and a stale done.idle -> the guard runs the tick; resume from DONE removes
    done.idle.
  - Then refresh the report: SUMMARY, ITEMS 1/2/5, REHEARSAL (guard-shaped argv), DONE TICK, TESTS RUN (director results
    above plus yours), DECISIONS I MADE, OPEN ISSUES (remove items now settled), NEEDS_RULING. Keep it short; drop the
    superseded slice checkpoints into one line each. Run tests.test_b6_loop and the new round-desk test only
    (round-desk tests take 50-200 s each; the director reruns the rest).
- DIRECTOR NOTES (before slice 4, 2026-10-22 13:25Z; director ran these outside the sandbox):
  - ITEM 5 SOURCE FOUND. pid 43816 was started 10-15 09:41 by the s3-cold lane's ad-hoc runner
    `/Users/edr/code/JouleWise-wt-b6-s3cold-fix/.scratch-fix/run_remaining.py`, which ran every tests/b6 and
    tests/hazards module. Its log `.scratch-fix/logs/after-remaining.log` ends inside
    `tests.hazards.test_monitor.SupervisorTests.test_all_probes_together_cost_at_most_half_a_percent_of_one_core`
    ("Two real monitors side by side for about 40 s") with a KeyboardInterrupt raised in `wait_for`'s
    `time.sleep` (line 697 -> 624): the runner was interrupted mid-test. The leaked custody dir is
    `.scratch-fix/tmp/s3-run/tmpxwija5mv/tmpzvtu2yd3/hazards/monitor` (TMPDIR/setUp tmp/mkdtemp root), matching
    that test's two `tempfile.mkdtemp(dir=self.custody)` roots. Mechanism: unittest re-raises KeyboardInterrupt out of
    `TestCase.run` WITHOUT running tearDown or `addCleanup` callbacks, so `_kill_quietly` never ran; and
    `monitor.Supervisor.start` launches the monitor with `start_new_session=True`, so the runner's process-group
    kill does not reach it; the monitor does not watch its parent, so it ran on as a ppid-1 orphan.
    `joulewise/hazards/monitor.py` and `scripts/hazard_monitor.py` are in the block-5 sealed inventory: do not touch.
  - SCOPE GRANT (director, slice 4): `tests/hazards/test_monitor.py` and `tests/fixture_signatures.json` (neither is in
    the sealed inventory; checked). Fix lives in the test file; `tests/b6/test_s3_cold_fixes.py` needs no change.
  - WHAT TO BUILD (decide details yourself, list them under DECISIONS I MADE):
    (a) In tests/hazards/test_monitor.py make every real `monitor.Supervisor` a SupervisorTests test starts get reaped
        even when the run is interrupted: e.g. track started supervisors on the instance and override
        `SupervisorTests.run` with try/finally that calls `_kill_quietly` on each (finally runs on KeyboardInterrupt;
        addCleanup does not). Also cover SIGTERM (the default signal of wall-clock bounds such as timeout(1)): while
        SupervisorTests runs in the main thread, temporarily turn SIGTERM into an exception so the finally runs, and
        restore the previous handler afterwards. SIGKILL cannot be covered from the test; record it as residual
        (only a parent-death watch in the sealed monitor would cover it).
    (b) A regression in tests/hazards/test_monitor.py: run a SupervisorTests-derived case (class defined inside the
        test, not module level) whose test method starts one real supervisor, records its pid, then raises
        KeyboardInterrupt; assert the KeyboardInterrupt still propagates AND `os.kill(pid, 0)` raises
        ProcessLookupError afterwards (the reaper waits on the child, so no timing bar is needed). Its own finally must
        kill the pid if the assertion fails, so the regression can never leak. Fails-before / passes-after evidence:
        run it against the unfixed class first (stash or temporarily revert your (a) edit), then fixed.
    (c) Census visibility: the census (scripts/fixture_orphan_census.py, sealed; registry tests/fixture_signatures.json,
        not sealed) deliberately ignores production monitor commands, so it cannot see this orphan class today. Add one
        registry row, e.g. id `hazards-test-real-monitor`, matching a real `scripts/hazard_monitor.py --config <path>`
        only when the config path has a tempfile-made component (`tmp` + 8 of [a-z0-9_]) before
        `.../hazards/monitor/config.json`; check by grep that no production custody path is a tempfile name, and
        add a row-matching unit test in tests/test_fixture_orphan_census.py (test-shaped path matches; production-shaped
        paths such as `/Users/edr/night-b6/.../custody/hazards/monitor/config.json` and the existing
        `-m joulewise.hazards.monitor` row do not). The census is a recorded flag, never a refusal; keep it so.
  - The director will prove (c) live after your slice: interrupt the SupervisorTests module mid-test with SIGINT and
    SIGTERM, let the runner exit, then run the census CLI: before your fix it should list a
    `hazards-test-real-monitor` orphan; after, none. You cannot do this in the sandbox (ps denied); do not try.
  - Round-desk cases (`test_physics_refusal_wait_reprepare_then_retry`, `test_stops_close_bracket_advance_pin_and_reach_next_smoke`),
    the lost-session rerun, tests.hazards.test_import_graph and the local rehearsal repeat: the DIRECTOR runs these
    outside the sandbox now. Do not run them in slice 4. Run only tests.hazards.test_monitor (its non-live classes run
    in the sandbox; list any ps/taskpolicy environment failures), tests.test_fixture_orphan_census and
    tests.b6.test_s3_cold_fixes.
## SUMMARY

- Items 1–6 implemented or given their authorized record-only disposition.
- Dedicated BYTES root preserves replication DONE history; guard-shaped CLI selects its twelve-pack config.
- DONE with delivered-outbox marker exits in native zsh before Python; nested DONE values cannot suppress resumed work.
- Anchor-fallback-only rc 1 is explained with negative-case coverage; all other failures remain failures.
- Item 48 LOW remains a sealed-driver false alarm; no scoped relay was found. Duplicate magistrate mail is external/manual.
- Historical monitor interruption leak fixed in test-owned cleanup; director SIGINT/SIGTERM census empty afterward.
- Director module runs pass; slice-5 loop 61 tests and new rehearsal test pass locally. No sealed file changed.
- Director final review, independent updated rehearsal, publication and current CI remain pending.

## LOOP ROOT CHOICE

Dedicated root implemented in configs/b6/loop_bytes.json: `/Users/edr/night-b6/loop-bytes`. Production directory never accessed or created.

Authority: `docs/design/block6_collection_draft.md` §6.1 closes once every pack has its target, and §14 makes the pack the unit of registration, collection and release with a queue of open packs. `docs/registrations/block6_replication_DRAFT.md` §14 S-2 identifies the existing replication loop root. `docs/registrations/bytes_pack_v1.md` §5 fixes twelve independent, fixed, one-session packs and order s1-p1 through s6-p1, then s6-p2 through s1-p2; its authority paragraph requires replication behavior to remain byte-identical.

The dedicated root preserves the replication loop's DONE history and avoids inventing a DONE-to-NEXT reopening rule. Its configuration restricts discovery to the twelve BYTES packs so existing replication registrations cannot be recollected. All twelve belong to the same active BYTES queue. No state under the proposed production path or the existing production root has been read or written by this seat.

## ITEMS

### 1. Twelve-pack loop readiness

configs/b6/loop_bytes.json supplies dedicated root, order and pack_ids; loop.py filters discovery to the twelve BYTES packs. scripts/b6_loop.py honors --config; otherwise it chooses repository configs/b6/loop*.json whose loop_root equals the resolved CLI/environment root. Multiple matches raise ValueError; no match preserves loop.json for legacy/scratch callers. All CLI commands inherit selection. tests/test_b6_loop.py covers BYTES, replication, unknown roots and duplicate matches using scratch paths only.

tests/b6/round_support.py now writes distinct roots into both scratch config copies and uses the guard's exact tick argument shape without --config. tests/b6/test_loop_round_desk.py adds an unskipped Linux-capable rehearsal test. Wrong fallback would select alpha and fail the assertions.

### 2. DONE tick overhead

loop.py publishes done.idle only after successful final mail/wake I/O and no pending outbox entry. scripts/b6_loop_guard.zsh matches exactly two spaces before the top-level state key emitted by atomic_state. Loop.control unlinks done.idle under lock before any state update. Tests cover outbox retry, NEXT with nested DONE and stale marker, and resume marker removal. NEXT without open packs continues discovery for future registrations. Existing DONE roots publish the marker on their first successful updated tick.

### 3. Item 48: smoke yield notice

**Recorded known false alarm; sealed code left unchanged.**

At base `bda481d5a`, `joulewise/b5/driver.py:1418` builds `yield_plan` from dispatch run IDs, not the reduced tree's kept counts. Its `count_stage` compares succeeded members with `_min_valid(role, planned)`, and `YieldTripwire` owns the live notice; `execute` calls `yield_plan` and constructs that tripwire. The smoke reduces dispatch execution after order resolution in `joulewise/b6/smoke.py`, using `configs/b6/smoke_keep.json`; the full order manifests deliberately remain intact.

Consequently the historical 3/10/10/3 plan can classify four successful one-member smoke stages as LOW. Computing a desk-only kept-count summary in smoke.py would not correct the live driver notice. The item brief expressly allows recording the false alarm when notice construction is confined to driver.py. No threshold, printed quantity, exclusion, or block-5 byte is changed. This item is a source-based disposition, not a successful live smoke test. Local relay audit of smoke.py, loop.py and mailer.py found no LOW/yield alert or desk line relaying the driver count; smoke.py uses yield only as a Python generator in _flag_codes. loop smoke desk carries acceptance status/codes and mailer has no yield relay. Keep the recorded false alarm; no alternative printed number was introduced.

### 4. Item 52 / issue 509: explained anchor fallback

Implemented smoke.py campaign-member record reader and stages_succeeded extension; removed desk caller's idle-flags-only gate. Exact dispatch membership, reduction prefix, rc 1, and successful acquisition/strict validation remain required. A member evaluation must name only anchor_fallback_member_unusable, have rerun_required true and child exit 0. Any companion member in that failed stage needs a usable campaign evaluation or a recorded idle skip; other validation, flags and child exits remain failures. Acquisition status can be succeeded while campaign validation fails (scripts/run_campaign.py MemberEvaluation.failed and rerun_required). No energy quantity or acceptance counting rule changed.

Expanded existing real desk/archive regression to exercise positive anchor-only case, extra collection flag, strict validation failure, nonzero child exit and a separate unexplainable companion member. Before production changes: 1 test in 1.123s, FAILED (anchor subcase fail != pass). After final robustness refinement: same test, 2.014s, OK, exit 0. Initial combined module run: 81 tests / 204.993s / exit 1, four failures from attempting evidence recovery for incomplete chains. Caller now requires every exit to be a success or rc 1, preserving existing crash/physical-stop handling. Focused rerun passed: 3 tests / 2.420s / exit 0.

### 5. Leaked hazard monitor

Director traced pid 43816 to the s3-cold ad-hoc runner interrupted inside SupervisorTests.test_all_probes_together_cost_at_most_half_a_percent_of_one_core. unittest propagates KeyboardInterrupt without tearDown/addCleanup; the monitor's new session escapes the runner process group. Production monitor files are sealed and unchanged.

tests/hazards/test_monitor.py tracks both creation sites and reaps in SupervisorTests.run finally. Main-thread SIGTERM temporarily raises KeyboardInterrupt; the previous handler is restored. Real-child regressions assert propagation and ProcessLookupError after reaping, with fallback cleanup. tests/fixture_signatures.json matches real script argv only with a tempfile-shaped path; tests/test_fixture_orphan_census.py covers historical and negative production/module paths. The census test also checks process visibility before spawning its separate fake-meter fixture, preventing a second leak when ps is denied. Census stays a flag, never a refusal.

Director live before: SIGINT/SIGTERM each left one hazards-test-real-monitor ppid-1 census row; director reaped those orphans. After: both census [], pgrep empty. Regression counterfactual: two failures (ProcessLookupError not raised), then two passes; regression fallback cleanup left census []. SIGKILL remains residual because Python finally cannot run.

### 6. Duplicate block-6 close mail

**Recorded; no mailer change. Loop wake is the single owner of the close notice.**

`docs/process_traces/2026-10-21-magistrate-283e9802/RECORD.md`, “Block 6 closed” and “Pruning list”, explicitly identifies the magistrate's manual “email the verdict” instruction as the second sender. `RUN_STATE.md` items 59 and 60 also distinguish the loop wake and that activation. `Loop._next` has one close event; the scoped `joulewise/b6/mailer.py` provides outbox delivery and issue closing, and has no magistrate-specific close dispatcher to prune.

This is a manual orchestration-instruction duplication, so changing the shared mailer would affect the existing loop delivery rather than removing the magistrate's instruction. The historical prose is evidence, not a second executable mailer. No in-scope magistrate sender was identified. The lead should carry loop-wake ownership into the external activation instructions; the requested record-only disposition is used here. No message was sent by this seat.

## REHEARSAL

Slice-5 standalone PASS at /private/tmp/jwtmp-byloop.ZhKeYM, exit 0; CI test PASS (1 / 15.226s, no skips). Exact replay from repository cwd:

```sh
JW_B5_SYNTHETIC_ONLY=1 TMPDIR=$(mktemp -d /private/tmp/jwtmp-byloop.XXXXXX) /opt/homebrew/bin/python3.13 -B - <<'PY'
import json, os
from pathlib import Path
from tests.b6.round_support import bytes_rehearsal
print(json.dumps(bytes_rehearsal(Path(os.environ['TMPDIR'])), indent=2))
PY
```

Helper argv for all three real-entry-point ticks: `scripts/b6_loop.py --repo-root <scratch>/measurement tick --loop-root <scratch>/loop-bytes`, without --config. Layout: measurement/{configs,joulewise,scripts,.git,.venv}, loop-bytes/{state.json,staging}, bin/launchctl, launchctl.argv, rehearsal.json. Both config copies have distinct scratch roots. Twelve registered-shaped synthetic registrations and full plan trees are committed only in scratch. Real open_packs, composition, DriverLane preparation and smoke.prepare execute. Hardware/precheck, transport, stop-ref observation and launch are synthetic seams. Fake launchctl is first on PATH and set as the driver's override; only fake executes, no install/arm.

Observed: NEXT → PRECHECK → SMOKE_RUN → SMOKE_RUN; discovered 12; packs [bytes-s1-p1]; prepared r1-bytes-s1-p1-smoke-0. Plan: loop-bytes/staging/r1-bytes-s1-p1-smoke-0/smoke/bytes-s1-p1-20261022T1340Z/custody/night_plan.json. Isolated clone, reduced tree, copied ledger/pin, wrapper and session.json exist. Fake argv exactly `rehearsal-only r1-bytes-s1-p1-smoke-0` plus newline. Fixture sizing copies ALPHA allowances; max_s=124620 is synthetic, never BYTES C5 evidence. Director independent updated repetition and Linux CI remain pending; cloud shell unavailable.

## DONE TICK

No-Python evidence: test_done_guard_skips_tick_and_resume_invalidates supplies JW_B6_LOOP_TICK as `/usr/bin/touch <scratch>/python-started`. Native zsh exits 0 for top-level DONE plus marker without the sentinel: zero tick executable starts. NEXT with nested last_exception.state DONE creates the sentinel. Resume removes done.idle and reaches NEXT. All pass in final loop module. Director read-only production check found one state line and no pending outbox entries, so first updated tick can publish done.idle; this seat did not access production state.

## TESTS RUN

All tests use repository cwd, JW_B5_SYNTHETIC_ONLY=1, Python -B, and a fresh /private/tmp TMPDIR per invocation. Exact command template (substitute names below):

```sh
JW_B5_SYNTHETIC_ONLY=1 TMPDIR=$(mktemp -d /private/tmp/jwtmp-byloop.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest <module-or-test>
```

Slice 5:

- Pre-fix names: tests.test_b6_loop.LoopTests.test_cli_selects_config_for_guard_loop_root tests.test_b6_loop.LoopTests.test_done_guard_skips_tick_and_resume_invalidates tests.test_b6_loop.LoopTests.test_resume_removes_done_idle_marker: 3 / 0.030s / exit 1 / three expected failures.
- tests.test_b6_loop: 61 / 9.536s / exit 0 / no skips.
- tests.b6.test_loop_round_desk.RoundTests.test_bytes_guard_shaped_rehearsal: 1 / 15.226s / exit 0 / no skips.

Director results supplied before slice 5 (same template, fresh TMPDIR, outside sandbox at 9e38914c6, all exit 0):

| Module | Tests | Notes |
| --- | ---: | --- |
| tests.hazards.test_import_graph | 6 | Prior NULL-vs-GO was ps denial; passes outside. |
| tests.hazards.test_monitor | 37 | 70.2s, live classes ran, no skips. |
| tests.test_fixture_orphan_census | 16 | No skips. |
| tests.b6.test_s3_cold_fixes | 6 | Pass. |
| tests.test_b6_mailer | 10 | Pass. |
| tests.b6.test_chain_smoke_reduction | 1 | Pass. |
| tests.test_b6_loop | 59 | Before two slice-5 additions; current 61 pass above. |
| tests.b6.test_smoke | 22 | 85.3s. |
| tests.hazards.test_refusal_allowlist | 23 | One skip. |

Director individual round-desk tests at 6129d0475 (b6 code unchanged through slice 4), full prefix tests.b6.test_loop_round_desk.RoundTests.: test_physics_refusal_wait_reprepare_then_retry 1 OK / 59.0s; test_stops_close_bracket_advance_pin_and_reach_next_smoke 1 OK / 197.0s; test_lost_session_reaches_desk_and_holds_before_beta 1 OK / 47.9s. Earlier SESSION_RUN failure did not recur outside sandbox. Prior alpha/rotation and resume cases passed locally (136.630s and 136.594s).

Anchor regression fails-before/passes-after is detailed in item 4. Leak director counterfactual: unfixed SIGINT runner rc -2, SIGTERM rc -15, each census one orphan; fixed SIGINT/SIGTERM rc -2 (SIGTERM translated to KeyboardInterrupt), both census [], pgrep empty. SupervisorCleanupTests counterfactual 2 FAIL (ProcessLookupError not raised), fixed 2 OK; own cleanup leaves census []. Local slice-4 interruption regression after fallback hardening: 2 / 0.018s / exit 0. Separate fake-meter visibility regression failed before without spawning; after full census 15 / 0.484s / exit 0 / two ps skips.

Earlier sandbox failures superseded by director passes: monitor 37 / 121.126s / two startup failures (taskpolicy setpriority denied); census ps denied and two skips; import-graph pgrep denied. No behavior weakened to bypass these. Historical checkpoints: slice 1 root/guard/rehearsal; slice 2 anchor fallback; slice 3 modules/fake-meter cleanup; slice 4 historical monitor cleanup. No whole suite, per brief.

## SEALED INVENTORY

682 paths. Local working-tree-inclusive intersection of inventory files with `git diff --name-only bda481d5a` plus `git ls-files --others --exclude-standard`: sealed_paths: 682; changed_overlap: []. No sealed file changed. After director commit, required committed check is `git diff --name-only bda481d5a HEAD` against the same inventory.

Exact check body, run with the same synthetic-only Python -B prefix and fresh TMPDIR:

```python
import json, subprocess
from pathlib import Path
files = set(json.loads(Path('configs/campaigns/v5_claim_25g83/sealed_inventory.json').read_text())['files'])
for label, args in [('committed', ['git','diff','--name-only','bda481d5a','HEAD']),
                    ('working-tree-inclusive', ['git','diff','--name-only','bda481d5a'])]:
    changed = set(subprocess.check_output(args, text=True).splitlines())
    changed.update(subprocess.check_output(['git','ls-files','--others','--exclude-standard'], text=True).splitlines())
    print(label, 'sealed_paths:', len(files), 'changed_overlap:', sorted(files & changed))
    assert not files & changed
```

Slice-5 output: committed sealed_paths: 682 changed_overlap: []; working-tree-inclusive sealed_paths: 682 changed_overlap: []. Exit 0; git diff --check exit 0.

## CI

Local branch by-loop at 9e38914c6 plus uncommitted slice-5 changes. Director publishes lane/2026-10-22-bytes-loop and ci/2026-10-22-bytes-loop. Draft PR #542: https://github.com/mpmdw/JouleWise/pull/542. Current CI unknown; historical cloud pending/gate-ledger results predate implementation. No network, commits or pushes attempted here. New rehearsal test is Linux-capable without platform skip.

## DECISIONS I MADE

- Dedicated BYTES root preserves replication DONE history under governing texts.
- Resolve CLI/environment root to a unique config only absent explicit --config; reject ambiguity, preserve unknown-root fallback.
- Match atomic_state's top-level indentation and invalidate done.idle under control lock.
- Retain narrowly evidenced anchor-fallback explanation and all negative failures.
- Record sealed-driver LOW false alarm and manual magistrate duplication under explicit record-only exceptions.
- Reap test supervisors in run/finally, temporarily translate main-thread SIGTERM, restore handler; SIGKILL remains residual.
- Census registry targets tempfile-shaped script argv only and remains a flag.

## OPEN ISSUES

- Director final diff review, independent updated rehearsal, commit/push and current CI.
- Production BYTES C5 sizing remains external; fixture values are synthetic.
- SIGKILL cannot execute cleanup; production parent-death supervision requires a separate sealed-code decision.

## NEEDS_RULING

none. No scope expansion; director evidence settles live leak acceptance and prior sandbox discrepancies.
