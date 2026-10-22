# Review of PR #500 (fix/2026-10-16-watchdog-b6-bindings, head 42ebf400c)

Reviewer: Opus 5.5, independent and executing (not the author). Date: 2026-10-16.
Worktree: /Users/edr/code/JouleWise-wt-watchdog-b6 (read only; nothing edited, pushed or installed).
Python: /opt/homebrew/bin/python3.13 -B, fresh TMPDIR, JW_B5_SYNTHETIC_ONLY=1. The replay was repeated under
/opt/homebrew/opt/python@3.14/bin/python3.14, the interpreter the installed com.joulewise.magistrate plist uses, with the same result.
The harness is archived at /Users/edr/night-archive/watchdog-b6/review-pr500-harness/ (replay.py, replay_fc.py, allplans.py).
Main baseline: `git archive d79e03549` exported to a temp directory, so the canonical checkout was not touched.

## Verdict: REQUEST-CHANGES

The validator hunk is correct and byte-identical to the lane's. Two problems:

1. The PR fails a test on its own head. It ported the validator hunk without its refusal-census rows.
2. On the real block-6 layout, the PR restores only the launch fence, not the REQUEST/TERM/KILL stand-down.
   Main currently drains a running magistrate session whenever a block-6 plist is installed. With this PR,
   a session already running at t0-180 s is never asked to stop.

## Findings

### BLOCKER-1: `tests.hazards.test_refusal_allowlist` fails on 42ebf400c (passes on main d79e03549)

Executed: `tests.hazards.test_refusal_allowlist` in the PR worktree gives `Ran 23, FAILED (failures=1)`. On the main export it gives `OK (skipped=1)`.
The census reports:
- unlisted: `validate_hazard_window` raise "bindings capture_screen must", count 2, guard 7fc6eff703a81212 (lines 766, 770);
- unlisted: "bindings spare_retries must", count 1, guard 1bda68bdc6dd287e (line 772);
- guard_changed: "bindings must name", listed 61750a625e96e385, now 232d3e13c3a8ee72 (line 759).

Cause: lane commit 2b2bea4cc changed `configs/gates/hazard_refusals.json` in the same commit as the hunk: one row replaced and two rows added, all category INTERNAL with `protects` text.
The PR ported only the code. The lane's three rows carry exactly the guards the PR's code computes, so porting those three JSON lines verbatim fixes it.
CI has not reached this yet: the 12 shards were still pending at review time, and they would fail. The CI-green ledger key cannot be met as the PR stands.

### MAJOR-1: For block-6 plans the watchdog fences new launches but never stands down a running session; this is a regression from main for that case

Where block-6 plans live: lane `joulewise/b6/session_paths.py` puts the plan at `<loop_root.parent>/sessions/<id>/custody/night_plan.json`.
`configs/b6/loop.json` sets loop_root to `/Users/edr/night-b6/loop`, so plans land under `/Users/edr/night-b6/sessions/...`.
The watchdog's `Storage.glob_plans` reads only `/Users/edr/night-custody/*/night_plan.json`. A block-6 plan is therefore visible only through `_installed_agent_plans`, which reads the night and dead-man plists.
In `decide()`, installed plans feed only `installed_agent_fence`, which returns FENCED with adopt=False. Three things use only the globbed plans:
- `active_plans` and the STANDDOWN_* branch;
- `ResidentSupervisor.step()`, through `relevant_standdown_plan`;
- `armed_plans`, `plan_conflicts` and `fenced_checkout_rows`.

Executed replay: the real plan MT-20261016T2114Z (t0 = 1792187100), with the machine-test plists copied into a fake `~/Library/LaunchAgents`.
The plan's night/ directory was simulated per time point; all writes went to the temp directory; signals went to a fake process table.
"Owner" means a magistrate.lock plus a live owned process. For the owner rows, the next actor was run too: the resident `step()`, or on HOLD_UNSAFE the tick's `adopt_recorded_session_for_drain` followed by `step()`.

PR head, installed-only layout (the real block-6 layout):

| time | no owner | owner: decide / actor result |
|---|---|---|
| t0-600 | LAUNCHING | ACTIVE / ACTIVE, no request |
| t0-170 | FENCED (installed_plan) | FENCED adopt=False / **ACTIVE, no standdown.request, no signal** |
| t0-100 | FENCED | same: **no request** |
| t0-70 | FENCED | same: **no SIGTERM** |
| t0+60 (chain.started) | FENCED | same: **no SIGKILL; session alive in the window** |
| completion+60, courier.sent | LAUNCHING (released) | ACTIVE |
| completion+60, courier not sent | FENCED | FENCED / ACTIVE |
| deadman+fresh+60, not sent | LAUNCHING | ACTIVE |

PR head, the same plan copied under the custody glob (the block-5 layout), for contrast:
- t0-170: STANDDOWN_REQUEST, standdown.request written;
- t0-70: STANDDOWN_TERM, SIGTERM;
- t0+60: STANDDOWN_KILL, SIGKILL, then HOLD_CENSUS.

That is the intended ladder, so the ladder code works. It is simply never reached for block-6 plans.

Main d79e03549: every time point gives HOLD_UNSAFE, in both layouts. With an owner, the tick's adopt-drain writes standdown.request, and the drain escalates to TERM after STOP_COOPERATIVE_S = 540 s and to KILL after 600 s.

So the PR replaces "no magistrate at all while a block-6 plist is installed; drain any running one" with "launch freely until t0-180 s, then refuse new launches but leave a running session alone".
The commit message and PR body say the stand-down ladder applies, citing `standdown_phase()` outputs. That pure function does return REQUEST, TERM and KILL at -180, -90 and -60 s (executed), but nothing calls it for an installed-only plan.

Consequence: no wrong number. The t0 census and block-6 agent_pause remain the backstop (watchdog comment LEAD-MARGIN-01: "The unchanged t0 census refuses a surviving tree"). The cost is quiet machine time: a refused or paused arm.

Suggested fix, smallest form: in `decide()` and in `ResidentSupervisor.step()`, treat installed-agent plans as plans for `active_plans`, `relevant_standdown_plan` and `armed_plans`, deduplicated by (plan_id, custody_root) and failing closed on read errors as they do now.
Alternative: extend `glob_plans` to `/Users/edr/night-b6/sessions/*/custody/night_plan.json`.
Add a watchdog-level test that drives an installed-only block-6 plan with an owned session through REQUEST, TERM and KILL.

If the lead decides to merge the fence alone as an interim step, record that the ladder is still missing for block 6. Before each window, also make sure no magistrate session that started before t0-180 s is still running.

### MINOR-1: The block-6 measurement checkout is missing from `fenced_checkouts` for installed-only plans

Executed: at t0-170 in the installed-only layout, `state["fenced_checkouts"]` contains only `__canonical_repo__`.
In the custody-glob layout it also lists the plan's measurement root and head c69917fe...
The magistrate's prompt is rendered from this list, so for block-6 windows it does not name the measurement checkout as fenced. `plan_conflicts` likewise ignores installed plans. The MAJOR-1 fix (feeding installed plans into `armed_plans`) closes this as well.

### MINOR-2: The tests cover the validator but not the watchdog path the PR exists for

The new `tests/test_b5_plan.py` cases test `validate_hazard_window` directly.
Executed against the old validator: `test_block6_optional_bindings_are_accepted` errors, as claimed. `test_block6_binding_defects_are_refused` passes on old code too, as a regression guard should.
No test drives `_installed_agent_plans`, `installed_agent_fence` or `decide()` with a block-6 plan.
The lane's three richer cases in `tests/test_night_gate.py` (fourteen strings still required alongside the optional keys; type checks covering "NaN", "Infinity", "-0.1", "0.1\n", 0.036 and others) were not ported. Port them; they are byte-compatible with this hunk.

### NIT-1: Main's other NightPlan consumers now accept block-6 plans without knowing the two bindings

These consumers are `run_night`, the b5 driver, `harvest_window`, `evidence_night`, `arm_census` and `v5_qualification`. On main nothing reads `capture_screen` or `spare_retries` (grep finds them only in night_gate.py).
No current route runs main's code on a block-6 plan: all four machine-test plists run `/Users/edr/night-custody/measurement/JouleWise-measurement-20261016T1210Z-b6`.
Main's driver runs the pack's pre-rendered chain, checked against its sidecar sha256, and never re-renders it, so even a mistaken run would execute the lane-rendered block-6 screen.
No action is needed beyond knowing it.

## Checks requested

1. **Byte-identity.** The `validate_hazard_window` function body at 42ebf400c is identical to 2b2bea4cc, to the pin b9de23a2c and to the lane head lane/2026-10-16-b6-round2 (awk-extracted bodies, `diff` empty). The +/- hunk lines are identical to 2b2bea4cc's night_gate.py hunk. The lane's watchdog is identical to main's: `git diff d79e03549 lane/... -- scripts/magistrate_watchdog.py` is empty, so MAJOR-1 exists on the lane too.
2. **Block-5 behaviour.** All 458 night_plan.json files under /Users/edr/night-custody, night-b5, night-b6 and night-g2a were parsed with the old and the new validator.
   - 454 give identical outcomes: 452 OK, and 2 refused on missing top-level keys in both.
   - Only the 4 block-6 machine-test plans change, from "bindings must name exactly the fourteen" to OK; these are the only plans carrying the optional keys.
   - A block-5 plan has no optional keys, so `set(bindings) - optional == set(HAZARD_LAUNCH_BINDINGS)` reduces to the old exact check.
3. **Replay.** See MAJOR-1. Fence: clear at t0-600, set at t0-170 through t0+60, released after completion once courier.sent exists.
   Without courier.sent the fence holds to deadman_epoch + COURIER_LOCK_FRESH_S = 1792316520 (t0 + 129420 s, about 36 h). That is by design, but note that the real machine-test courier never wrote courier.sent (courier.json: 4 attempts, sent false).
   Main gives HOLD_UNSAFE at every point.
4. **Test modules in the worktree.** All OK:
   - test_b5_plan: 25 tests
   - test_night_gate: 109
   - test_install_magistrate_watchdog: 10
   - test_magistrate_watchdog: 155
   - test_magistrate_watchdog_cli: 7
   - test_magistrate_watchdog_span: 24
   - test_magistrate_watchdog_yield: 20
   - test_window_lineage: 52 (it reads hazard_refusals.json)

   tests.hazards.test_refusal_allowlist FAILS (BLOCKER-1).
5. **Numbers.** The hunk adds no tolerance or bar. The only numeric rule is a syntactic one: a non-negative decimal string or null. The times used in the replay (180, 90 and 60 s leads; 540 and 60 s drain; 300 s tick) are existing constants, with their derivation in the watchdog's LEAD-MARGIN-01 comment: measured cooperative exits of 20-31 s give about 150 s of margin at REQUEST. This review proposes no new number.

## CI at review time

gate-ledger fails because ledger rows 1, 2, 3 and 5 are still NOT-RUN, which is expected before review. build, changes, fences, installed-wheel and quick pass. The 12 test shards and the exclusive jobs were pending.
