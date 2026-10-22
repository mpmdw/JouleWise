# BY-LOOP — complete; lead-verified

## PROGRESS

- Slices 1-5 (local codex-run-v3, gpt-6.1-sol high; Codex Cloud gave no shell twice): 9de9ae0a5, b8a25c2e1,
  6129d0475, 9e38914c6, ceac3ad86. Director notes that steered slices 4 and 5 (item 5 source, scope grant
  tests/hazards/test_monitor.py + tests/fixture_signatures.json, findings F-A and F-B) are summarised in ITEMS and
  DIRECTOR VERIFICATION; the full notes are in the lane history at ceac3ad86.
- Lead fix after slice 5: CI shard 7 failed on fba44874a because bytes_rehearsal committed its scratch git fixture
  without an identity (CI runners have none). tests/b6/round_support.py now sets the same local fixture identity
  Round already uses. See DIRECTOR VERIFICATION 2.
- NEEDS_RULING none. No scope request open.

## SUMMARY

- Items 1–6 implemented or given their authorized record-only disposition.
- Dedicated BYTES root preserves replication DONE history; guard-shaped CLI selects its twelve-pack config.
- DONE with delivered-outbox marker exits in native zsh before Python; nested DONE values cannot suppress resumed work.
- Anchor-fallback-only rc 1 is explained with negative-case coverage; all other failures remain failures.
- Item 48 LOW remains a sealed-driver false alarm; no scoped relay was found. Duplicate magistrate mail is external/manual.
- Historical monitor interruption leak fixed in test-owned cleanup; director SIGINT/SIGTERM census empty afterward.
- Director module runs pass; slice-5 loop 61 tests and new rehearsal test pass locally. No sealed file changed.
- Director (lead) verification at ceac3ad86: see DIRECTOR VERIFICATION at the end; rehearsal repeated locally, every targeted module and all six round-desk tests pass outside the sandbox; CI on ci/2026-10-22-bytes-loop.

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

Observed: NEXT → PRECHECK → SMOKE_RUN → SMOKE_RUN; discovered 12; packs [bytes-s1-p1]; prepared r1-bytes-s1-p1-smoke-0. Plan: loop-bytes/staging/r1-bytes-s1-p1-smoke-0/smoke/bytes-s1-p1-20261022T1340Z/custody/night_plan.json. Isolated clone, reduced tree, copied ledger/pin, wrapper and session.json exist. Fake argv exactly `rehearsal-only r1-bytes-s1-p1-smoke-0` plus newline. Fixture sizing copies ALPHA allowances; max_s=124620 is synthetic, never BYTES C5 evidence. Director repetition and Linux CI: see DIRECTOR VERIFICATION.

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

Lane lane/2026-10-22-bytes-loop; CI-only branch ci/2026-10-22-bytes-loop = the lane head merged with BY-INT's
pass-1 head da27be7b9 and main 81db9f355 (git merge-tree --write-tree, then git commit-tree; no conflicts).
Draft PR #542 (https://github.com/mpmdw/JouleWise/pull/542) follows the CI branch. First CI run (fba44874a, lane
ceac3ad86): 19 of 20 test jobs green; shard 7 failed in tests.b6.test_loop_round_desk.test_bytes_guard_shaped_rehearsal
(git commit exit 128, no identity on the runner); gate-ledger red as expected for a draft. Fixed in the lead commit
that follows ceac3ad86; the CI result for the rebuilt CI branch is in DIRECTOR VERIFICATION 2. The new rehearsal
test has no platform skip, so the Linux CI shards run it (this item's cloud rehearsal while Codex Cloud gave no
shell).

## DECISIONS I MADE

- Dedicated BYTES root preserves replication DONE history under governing texts.
- Resolve CLI/environment root to a unique config only absent explicit --config; reject ambiguity, preserve unknown-root fallback.
- Match atomic_state's top-level indentation and invalidate done.idle under control lock.
- Retain narrowly evidenced anchor-fallback explanation and all negative failures.
- Record sealed-driver LOW false alarm and manual magistrate duplication under explicit record-only exceptions.
- Reap test supervisors in run/finally, temporarily translate main-thread SIGTERM, restore handler; SIGKILL remains residual.
- Census registry targets tempfile-shaped script argv only and remains a flag.

## OPEN ISSUES

- Install step (arm-time, not done here): render configs/launchd/com.joulewise.b6loop.plist.template with __LOOP_ROOT__=/Users/edr/night-b6/loop-bytes; the CLI now selects configs/b6/loop_bytes.json from that root. Same label as the replication job, which is DONE. Install only after the BYTES packs are registered: until then a fresh BYTES root sits in NEXT and each 300 s tick starts Python (NEXT with no open pack is not dormant by design, so a later registration is discovered).
- Production BYTES C5 sizing remains external; fixture values are synthetic.
- SIGKILL cannot execute cleanup; production parent-death supervision requires a separate sealed-code decision.

## NEEDS_RULING

none. No scope expansion; director evidence settles live leak acceptance and prior sandbox discrepancies.

## DIRECTOR VERIFICATION (lead, Opus 5.5, outside the sandbox, 2026-10-22)

Every command: repository cwd, `JW_B5_SYNTHETIC_ONLY=1`, a fresh `/private/tmp` TMPDIR per invocation,
`/opt/homebrew/bin/python3.13 -B`. No launchctl, no install, no arm; the real loop root was only read
(state.json state lines, outbox delivery fields).

- Finding F-A (blocker, found by the lead reading the launchd path, fixed in slice 5): the plist sets only
  JW_B6_LOOP_ROOT and the guard execs `b6_loop.py tick --loop-root <root>` without --config, so a loop at
  /Users/edr/night-b6/loop-bytes would have read configs/b6/loop.json. Counterfactual, slice-5 tests on the
  pre-fix code (6129d0475): the guard-shaped rehearsal opened `r1-alpha` with packs [alpha] (a replication pack
  collected again); test_cli_selects_config_for_guard_loop_root got loop.json for the BYTES root. Both pass at
  ceac3ad86. F-B counterfactual: nested-DONE guard case and resume-marker case fail pre-fix, pass after.
- Rehearsal, local, at ceac3ad86: `bytes_rehearsal` on /private/tmp/jwtmp-byloop-reh.63NiFv, exit 0:
  transitions NEXT, PRECHECK, SMOKE_RUN, SMOKE_RUN; 12 discovered; packs [bytes-s1-p1]; smoke prepared
  r1-bytes-s1-p1-smoke-0 (plan under loop-bytes/staging/r1-bytes-s1-p1-smoke-0/smoke/.../custody/night_plan.json);
  fake launchctl argv log exactly `rehearsal-only r1-bytes-s1-p1-smoke-0`.
- DONE tick, direct: scratch root with atomic_state DONE (plus a nested last_exception.state DONE) and done.idle;
  guard run with JW_B6_LOOP_TICK as a recorder: rc 0, tick not started. Same root without done.idle: tick started.
- Item 5 live: unfixed test file, runner interrupted after the monitor's start journal line: SIGINT -> 1 census row
  `hazards-test-real-monitor` (ppid 1), SIGTERM -> 1 row; fixed: SIGINT and SIGTERM -> census []. Regression
  counterfactual (pre-fix run): 2 FAIL "ProcessLookupError not raised"; fixed 2 OK; census [] and
  `pgrep -fl hazard_monitor` empty after every run.
- Modules at ceac3ad86 / 9e38914c6 (b6 code unchanged between them except slice 5's loop files, rerun at ceac3ad86):
  tests.test_b6_loop 61 OK; tests.b6.test_smoke 22 OK; tests.test_b6_mailer 10 OK; tests.b6.test_chain_smoke_reduction
  1 OK; tests.b6.test_s3_cold_fixes 6 OK; tests.test_fixture_orphan_census 16 OK (no skips); tests.hazards.test_monitor
  37 OK (live classes ran); tests.hazards.test_import_graph 6 OK; tests.hazards.test_refusal_allowlist 23 OK (1 skip).
  Round desk at ceac3ad86, one test per run: bytes_guard_shaped_rehearsal OK 12.6 s; alpha_smoke_session_desk_and_beta_rotation
  OK 41.8 s; physics_refusal_wait_reprepare_then_retry OK 50.9 s; stops_close_bracket_advance_pin_and_reach_next_smoke
  OK 168.4 s; lost_session_reaches_desk_and_holds_before_beta OK 35.6 s; resume_after_hold_continues_real_round OK 43.0 s.
- Sealed inventory, committed: `git diff --name-only bda481d5a ceac3ad86` (13 paths) intersect 682 sealed paths = [].
  `git diff --check bda481d5a ceac3ad86` exit 0.

## DIRECTOR VERIFICATION 2 (lead, Opus 5.5, 2026-10-22 15:52-16:10Z, outside the sandbox)

Same conditions as above (repository cwd via the runner, `JW_B5_SYNTHETIC_ONLY=1`, fresh `/private/tmp` TMPDIR
per invocation, `/opt/homebrew/bin/python3.13 -B`, no launchctl, no install, no arm). The Mac was running other
lanes' Sol seats (load average 30-38).

- CI shard 7 fix (tests/b6/round_support.py only). Emulating a runner with no git identity
  (GIT_CONFIG_GLOBAL = a file holding only `user.useConfigOnly = true`, GIT_CONFIG_NOSYSTEM=1, no GIT_* identity
  variables): at ceac3ad86 test_bytes_guard_shaped_rehearsal ERROR, `git ... commit -qm synthetic BYTES rehearsal`
  exit 128 (the CI failure); with the fix 1 OK in 14.0 s.
- Rehearsal repeated locally with the fix (`bytes_rehearsal` on /private/tmp/jwtmp-byloop-reh.gPXZV4, exit 0):
  transitions NEXT, PRECHECK, SMOKE_RUN, SMOKE_RUN; 12 packs discovered; packs [bytes-s1-p1]; smoke prepared
  r1-bytes-s1-p1-smoke-0 with plan loop-bytes/staging/r1-bytes-s1-p1-smoke-0/smoke/bytes-s1-p1-20261022T1554Z/
  custody/night_plan.json; fake launchctl argv log exactly `rehearsal-only r1-bytes-s1-p1-smoke-0`.
- DONE tick: scratch roots written by loop.atomic_state. DONE (with a nested last_exception.state DONE) plus
  done.idle: guard rc 0, recorder tick not started, /usr/bin/time 0.00 s user and sys. NEXT with the same nested
  value plus done.idle: tick started. DONE without done.idle: tick started (the first updated tick publishes it).
- stages_succeeded on real block-6 smoke data (read-only replay of the desk's stage computation over the ten
  /Users/edr/night-b6/loop/staging/*-smoke-0 sessions; statuses only, no energy values read out): nine sessions
  have every in-chain stage at a success exit, so the function is not called. r2-alpha-smoke-0 has one stage
  (alpha-science-prefill-p2048-absolute) at rc 1 whose only member has harvested status succeeded and campaign
  class anchor; before the change stages_succeeded returned False (the recorded smoke status was fail, the
  10-19 hold that item 52 calls wrong), after it returns True. The negative cases (other flag, strict-validation
  failure, nonzero child exit, an unexplained companion member, idle-skip variants) stay failures in
  tests.b6.test_smoke (22 OK).
- Item 5 live, fixed test file: runner of tests.hazards.test_monitor.SupervisorTests interrupted once 2 real
  monitor children were seen: SIGINT runner rc -2, SIGTERM runner rc -2 (translated); census [] and no child
  alive after either. Counterfactual with the 6129d0475 test file in a scratch worktree: SIGINT left 2
  `hazards-test-real-monitor` rows at ppid 1, SIGTERM (rc -15) left 2; the director killed them; no monitor of
  either tree alive afterwards. Census [] before and after every module run below.
- Modules with the fix, run in parallel: tests.test_b6_loop 61 OK; tests.b6.test_smoke 22 OK;
  tests.test_fixture_orphan_census 16 OK; tests.hazards.test_import_graph 6 OK; tests.hazards.test_refusal_allowlist
  23 OK (1 skip); tests.test_b6_mailer 10 OK; tests.b6.test_chain_smoke_reduction 1 OK; tests.b6.test_s3_cold_fixes
  6 OK. tests.hazards.test_monitor: 37 OK once, and twice 36 OK with
  SupervisorTests.test_all_probes_together_cost_at_most_half_a_percent_of_one_core failing its 80 s wait for five
  cost records from the background-QoS monitor (starved at load average 30-38). That test alone passed at base
  bda481d5a and at this head back to back under the same load; this lane changed only how its supervisors are
  registered for reaping, not its timing. Environmental, not chased.
- Sealed inventory on the lead commit: `git diff --name-only bda481d5a HEAD` (13 paths, the same 13 as at
  ceac3ad86) intersect 682 sealed paths = []. `git diff --check` clean.
