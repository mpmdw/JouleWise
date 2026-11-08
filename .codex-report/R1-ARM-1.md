```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "R1 arm route and synthetic verification are implemented; filesystem policy blocks commit/push, and unchanged shared checks retain failures.",
  "workspace": {
    "base_requested": "d9d1098c619856d624214dc5fde14013aafc4312",
    "base_mode": "exact",
    "head_start": "d9d1098c619856d624214dc5fde14013aafc4312",
    "head_end": "d9d1098c619856d624214dc5fde14013aafc4312",
    "upstream_end": null,
    "branch": "lane/2026-11-08-r1-arm"
  },
  "pathspec": ["scripts/arm_align_r1.py", "joulewise/align/r1_arm.py", "tests/align/test_r1_arm.py", "tests/align/test_v4_kit.py", "tests/align/test_r1_runtime.py", "docs/align/r1_arm_runbook.md", ".codex-report/R1-ARM-1.md"],
  "unowned_dirty": [],
  "verdict": {"implementation": "implemented", "acceptance": "pending_verification"},
  "verification": [
    {"id":"V1","kind":"test","cmd":"env TMPDIR=/tmp/jw-r1arm-tmp JW_B5_SYNTHETIC_ONLY=1 /opt/homebrew/bin/python3.13 -B -m unittest tests.align.test_r1_arm","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
    {"id":"V2","kind":"test","cmd":"env TMPDIR=/tmp/jw-r1arm-tmp JW_B5_SYNTHETIC_ONLY=1 /opt/homebrew/bin/python3.13 -B -m unittest tests.align.test_v4_kit tests.align.test_r1_runtime","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
    {"id":"V3","kind":"suite","cmd":"env TMPDIR=/tmp/jw-r1arm-tmp JW_B5_SYNTHETIC_ONLY=1 /opt/homebrew/bin/python3.13 -B -m unittest tests.test_run_night tests.align.test_r1_rehearsal","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["FAILED (failures=3, errors=2, skipped=9)"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
    {"id":"V4","kind":"inspection","cmd":"git -C /Users/edr/code/JouleWise-wt-r1-arm diff 9c40e4e5d --stat -- pyproject.toml env/mac-measurement-lock.txt env/analysis-lock.txt","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[]},"expected":{"exit_code":0,"tail_regex":"^$"}},
    {"id":"V5","kind":"lint","cmd":"git -C /Users/edr/code/JouleWise-wt-r1-arm diff --check HEAD","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[]},"expected":{"exit_code":0,"tail_regex":"^$"}},
    {"id":"V6","kind":"test","cmd":"env TMPDIR=/tmp/jw-r1arm-tmp JW_B5_SYNTHETIC_ONLY=1 /opt/homebrew/bin/python3.13 -B -m unittest tests.test_run_night.BindSupervisionProcessTests.test_blocked_journal_never_blocks_deadline_or_grants_go tests.test_run_night.HazardPackPrimitiveTests.test_dead_man_stops_the_hazard_monitor_a_dead_driver_left_running tests.test_run_night.HazardPackPrimitiveTests.test_natural_exit_census_proves_survivors_gone_before_recording_the_exit tests.test_run_night.HazardPackPrimitiveTests.test_supervision_stop_terminates_the_group_and_returns_its_refusal tests.test_run_night.Ruling76DriverTests.test_observer_faults_do_not_change_success_or_failure_chain_rc","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["FAILED (failures=2, errors=2)"]},"expected":{"exit_code":0,"tail_regex":"OK"}}
  ],
  "flags": [
    {"id":"F1","kind":"verification_gap","level":"nonblocking","text":"Five failures/errors remain in the unchanged tests.test_run_night module; details and replay are below.","needs":"Lead owns disposition and final verification; CI runs the full suite."},
    {"id":"F2","kind":"environment","level":"nonblocking","text":"The sandbox denies process-table access. End-to-end tests explicitly substitute synthetic process censuses, hardware, collectors and transport; real signals and R1 driver/lock/restore paths run.","needs":"Verify live process census/termination on the measurement Mac."},
    {"id":"F3","kind":"residual_risk","level":"nonblocking","text":"R1 allocation is explicitly unsized without an operator-sourced estimate; existing disk headroom/live floor remain. The unchanged hazard interrupt path can retain diagnostic monitor/meter processes until dead-man recovery.","needs":"Review arm.json capacity flag and monitor custody at the live gate."},
    {"id":"F4","kind":"environment","level":"blocking","text":"git add failed with exit 128: the parent repository Git metadata is outside writable roots, so index.lock creation is forbidden. No commit or push occurred; escalation/bypass is unavailable.","needs":"Lead must stage the seven scoped files, commit and push lane/2026-11-08-r1-arm from a session permitted to write the parent Git metadata."}
  ]
}
```

## Change

Implemented **(a), one `HAZARD_PACK` window around the existing R1 chain**.
No shared runtime/launcher/watchdog code, thermal gate, kit number or dependency
file changed. `scripts/arm_align_r1.py` supplies prepare, render, install and
uninstall; installation delegates to the existing installer. The library
authors the plan, R1 input inventory and wrapper. The report was written before
the requested Git transaction. Staging then failed on the parent repository's
protected `index.lock`; HEAD is unchanged, and no commit or push occurred.
The exact remaining commands are below.

### Route evidence and rejected options

- `scripts/run_night.py:724` exports `NIGHT_DIR`, `MEASUREMENT_ROOT`, pinned
  interpreter and head. `:4550` dispatches the hazard branch;
  `joulewise/b5/driver.py:26` describes its single-chain launch. No member
  collection is required. R1's original chain remains the payload.
- The plan declares **Automatic, 0**. `scripts/run_night.py:4482` holds the
  outer host lock only for plan 2; at `:4535` it hands that lock to a plan-2
  chain. R1 is different: `scripts/align_r1_rehearsal.py:1593` constructs its
  own host lock and `:1621` acquires it. Selecting 0 avoids an outer holder
  blocking that admission. The synthetic interrupt test proves a concurrent
  lock acquisition fails during B, then succeeds after teardown.
- `scripts/magistrate_watchdog.py:797` reads both installed plists' absolute
  `--plan` paths independently of directory scanning. `:1294` fences the
  plan span, including an open chain after its nominal end. The shared
  installer already publishes both plists; no second watchdog fence is needed.
  The fence/stand-down timing is `:81–101` (REQUEST 180 s, TERM 90 s, KILL 60 s
  before t0). The t0 census is still the backstop for surviving agents.
- The daily dead-man calendar is safe for the long window:
  `scripts/run_night.py:2188` derives the real end; `:5045` returns before
  completion without resolving a courier or stopping the chain. The test
  renders real plists, feeds them to the watchdog reader, checks the second
  day fence, and invokes the real early dead-man path.
- Rejected **(b)**: `joulewise/night_gate.py:2197` and `:2216` require an
  admitted registration digest for `DIAGNOSTIC_NO_PACK`. R1 has none. Inventing
  a registration or weakening that branch would add authority and code without
  solving a problem the existing hazard branch already solves.
- Rejected **(c)**: the requested base contains neither `launch_align_r0.py`
  nor its runbook. On `origin/main`, `scripts/launch_align_r0.py:23–27` uses a
  separate desk fence and a 12-hour cap, shorter than R1's required floor.
  Porting/expanding it would add a launch/fence lifecycle and duplicate the
  environment/power integration. The installed-plan path already works.

The first replay exposed an actual integration issue: the W1 tree has no
`identity_pin_projection`, so `window_lineage.py:957` classified it unusable
and the driver refused before launch. The author now writes an **R1-only
inventory of actual input/template bytes** (`r1_arm.py:68`), rather than
pretending the pending W1 tree is an executable R1 pack. No inventory refusal
was relaxed. The real lineage publication is exercised in the replay.

### Magistrate commands and notice

The exact ordered procedure, including host preparation, notice text and
render inspection, is [the runbook](../docs/align/r1_arm_runbook.md). Its main
commands are reproduced here; do not execute them from a build seat.

```zsh
export M=/Users/edr/night-custody/measurement/JouleWise-measurement-20261102-align-pilot2
git -C "$M" status --short --branch
git -C "$M" fetch origin refs/heads/lane/2026-11-08-r1-arm
git -C "$M" switch --detach FETCH_HEAD
git -C "$M" rev-parse HEAD
export PY="$M/.venv/bin/python"
"$PY" -B -c 'from importlib.metadata import version; print(*(version(x) for x in ("mlx","mlx_lm","transformers")))'
export S="/Users/edr/night-align/r1-$(date -u +%Y%m%dT%H%M%SZ)"
export T0="$("$PY" -B -c 'import math,os,sys,time; sys.path.insert(0,os.environ["M"]); from scripts import run_night,magistrate_watchdog; print(60*math.ceil((time.time()+magistrate_watchdog.PLAN_LEAD_S+run_night.INSTALL_CLOSE_MARGIN_S+180)/60))')"
"$PY" -B "$M/scripts/arm_align_r1.py" prepare --measurement-root "$M" --custody-root "$S" --t0 "$T0"
"$PY" -B "$M/scripts/arm_align_r1.py" render --custody-root "$S" --output "$S/rendered"
cat "$S/arm.json"
# Send the notice described below, then install as the final action.
"$PY" -B "$M/scripts/arm_align_r1.py" install --custody-root "$S"
# Exit every agent session. LaunchAgent wakes run_night at t0.
# After terminal collection and live verification:
"$PY" -B "$M/scripts/arm_align_r1.py" uninstall --custody-root "$S"
```

This deliberately advances the existing `9c40e4e5d` checkout with a
non-fast-forward detached checkout, preserving its pinned venv
(`mlx 0.31.2`, `mlx_lm 0.31.3`, `transformers 5.12.1`). No dependency file differs
against that head. Clear the synthetic runtime/host-state/replay variables
listed in the runbook. Do not overwrite local work or reinstall dependencies.

The whole-minute example t0 derives its lead from the existing 180-second
watchdog lead, 120-second install-close margin, and the existing session
installer's 180-second execution allowance (`scripts/bytes_h_session.py:435`).
Select it only when review and notice are ready. Prefer a post-maintenance
quiet start; a more-than-day ceiling cannot avoid every scheduled task, so
item 202(4)'s lead notification applies if quiet segments cannot avoid them.

**Ceiling: 105,127 s = 96,427 + 3,300 + 2 × (1,800 + 600) + 600.** The floor is
origin/main RUN_STATE 215–216. The arm cap is `b5/plan.py:59`; bookend and close
budgets are `b5/chain.py:180–189`. A final session-status-sized allowance covers
the R1 harvest/result writes. This includes admission because the driver's
t0-based deadline includes it (`run_night.py:1160`). The normal shutdown grace
stays 300 s. Extra load redos can reach the ceiling; no assertion that all
possible repeated contaminations fit is made. The stale runtime display and
`test_r1_round7_science.py` are untouched.

Ed's notice states checkout/head, custody, Pacific/UTC t0, ceiling and shutdown
grace, early completion, no agents at t0, AC/not-charging, external SSD
unplugged, no other work, automatic Security Responses retained, possible
scheduled-job retries/refusal and lead notification, R1-owned High Power and
Automatic restore, diagnostic meter/GPU residual, capacity-estimate flag, and
the promised terminal report. No mail was sent by this build seat. The
existing file-only `scripts/b6_courier.sh:3` is passed explicitly: no agent
courier is introduced.

### Production-shaped synthetic transcript

`tests/align/test_r1_arm.py:293` drives the **real run_night hazard branch →
generated wrapper → unchanged zsh R1 chain → real R1 driver → executable
ALIGN_R1_RUNTIME synthetic runtime**. The runtime uses the existing
`test_r1_rehearsal.FakeWorld` fields. Hardware, agent census, monitor, collectors,
transport and process-table boundaries are synthetic; clock batch waiting is
disabled in the test shim. Real lineage publication, subprocesses, driver
signals, flock, persistent markers and final result writes execute. The
sandbox denies `ps`; fixture process tables are explicit, not live proof.

Stable transcript summary (temporary paths vary):

```text
normal:    exit=0,   r1_status=complete, NIGHT_DIR=<custody>/night,
           MEASUREMENT_ROOT=<measurement>, r1_result.json and r1_slots.json written,
           power_mode=0, both power markers absent, host_lock_reacquired=true
interrupt: SIGTERM while high-power-aba-b is active, competing host lock blocked,
           exit=130, r1_status=aborted, r1_result.json written,
           power_mode=0, both markers absent, host_lock_reacquired=true,
           chain.exited present
```

Both synthetic diagnostic bookends deliberately exit 7; R1 still completes,
and each leaves `r1.bookend_failed` in its own record. The meter supervision
journal is present. No real `sudo`, `pmset -c`, model, telemetry sampling or
LaunchAgent installation occurred.

### Item 202(4): scheduled macOS jobs

**No scheduler-name-triggered immediate night refusal or mid-segment dwell.**
Software Update's scans (23:09/05:09/11:09/17:09), midnight `/tmp` cleanup,
trustkit's four-hourly xx:31 signatures, XProtect around 05:40 and 12:53
maintenance are treated like any other background process.

- Quiet segment start avoids 11:45–13:15, based on its own bound
  (`align_r1_rehearsal.py:980`, `:1073`). This can wait through an encounter;
  it does not pause a segment already running.
- The runtime load journal excludes only its own process tree and records the
  rest (`r1_runtime_contract.py`, `LoadJournal`; contract prose lines 49–56).
  `align_r1_rehearsal.py:869` requires load >0.5 core for 60 consecutive samples.
  `:1088` rejects/repeats that attempt; heavy redos first release against the
  soak (`:1065`, `:1074`). Shorter/lower load is recorded without this redo.
- After two redos, continued contamination **refuses R1** (`:159`, `:1107`).
  Missing/gappy load evidence can also refuse (`:879`). A pure G0 timeout is
  separately INCONCLUSIVE with one retry for step D/designed states
  (`:1273`), not the generic response to a scheduled task.
- The outer monitor's 5% per-process contention is journaled/flagged
  (`hazards/monitor.py:581–601`); the in-window supervision stop paths concern
  disk/instrument outage (`b5/driver.py:2550–2588`), not a scheduled task name.
  At arm time the existing physical contention dwell can refuse at its cap.

Therefore the magistrate cannot promise that these jobs merely wait or always
produce INCONCLUSIVE. If the quiet-sensitive schedule cannot avoid them, item
202(4) requires notifying the lead before arming. No measurement rule was
changed to make this arm possible.

### Meter and decisions I made

KM003C **does run**: `b5/driver.py:745` builds its command and `:2457` starts it
through the existing supervisor. Exit 0 (meter absent) is final, and it never
vetoes R1. No extra reader was added. Item 212 R11-3 says v4's registered
residual stays GPU energy; R1 does not depend on this meter for its outputs.

Decisions made from the governing code/text:

1. Reuse the single-chain hazard route and installed-plan watchdog fence;
   declare 0 and leave the R1 driver in charge of its host lock/transitions.
2. Reuse **ALIGN pilots' clock hold**, `b6/plan_inputs.py:21–24` (registered S-7,
   `docs/registrations/block6_replication_DRAFT.md:856`): 5 ms/span minus
   0.25 ppm, placement judged per run. Do not copy the obsolete B5 3.7 ms hold:
   at the conservative 5,764-second R1 span it would refuse even zero drift
   (5.141 ms). A regression checks the real measured-rate predicate at zero
   and at 1 ppm. No new scientific tolerance was invented.
3. Publish an actual R1 input inventory; do not launch W1 or manufacture an
   admitted R1 registration. Bookends are ordinary independent diagnostic
   D-109 observations, with failures recorded. A >24-hour R1 cannot claim
   coverage from W1's 24-hour reserved bracket (`b5/chain.py:221`). No R1 work
   is truncated to that bracket horizon and no claim eligibility is granted.
4. Use the corrected retry floor and explicit scaffold/close/harvest allowances;
   preserve the existing deadline stop and every R1 measurement behavior.
5. Keep an absent R1 footprint estimate explicitly unsized (0 estimated bytes),
   retaining existing 20 GiB headroom/10 GiB live floor (`hazards/disk.py:37`).
   Permit a sourced estimate; do not reuse B5's unrelated per-member size.
6. Preserve pending-R0 rejection properties using temporary kits/templates with
   values reset to pending. Both upstream fills remain intact.

**NEEDS_RULING: none. NEEDS_SCOPE: none.** The supplied task directly selects
this bounded [AGENT] implementation; Mission M0 found no active stop card.
No other agent/Claude was called. RUN_STATE/TASK_QUEUE and lead-owned reports
were preserved under the exhaustive write scope.

## Verification notes

**Git handoff is blocked by this session's filesystem policy.** The requested
`git add` returned exit 128:

```text
fatal: Unable to create '/Users/edr/code/JouleWise/.git/worktrees/JouleWise-wt-r1-arm/index.lock': Operation not permitted
```

The metadata lives outside the writable worktree root; approval escalation
is disabled. No bypass was attempted. A lead with access to the parent Git
metadata must finish the already-authorized transaction:

```zsh
git -C /Users/edr/code/JouleWise-wt-r1-arm add -- scripts/arm_align_r1.py joulewise/align/r1_arm.py tests/align/test_r1_arm.py tests/align/test_v4_kit.py tests/align/test_r1_runtime.py docs/align/r1_arm_runbook.md .codex-report/R1-ARM-1.md
git -C /Users/edr/code/JouleWise-wt-r1-arm commit -m "Add the ALIGN R1 LaunchAgent arm route"
git -C /Users/edr/code/JouleWise-wt-r1-arm push -u origin lane/2026-11-08-r1-arm
```

Counts: new arm module **4/4**; snapshot modules **149/149** (v4 kit 116,
R1 runtime 33). Required shared modules: **391 run**, **377 passed**, **9 skipped**,
**3 failures, 2 errors** (run_night 318, R1 rehearsal 73). This is **544 tests**
across the five permitted modules, including skips. Full suite was not run,
as requested; CI owns it.

The five failures/errors are in the unchanged `tests.test_run_night`:

- `BindSupervisionProcessTests.test_blocked_journal_never_blocks_deadline_or_grants_go`:
  existing external 8-second fixture watchdog expires.
- `HazardPackPrimitiveTests.test_dead_man_stops_the_hazard_monitor_a_dead_driver_left_running`:
  monitor wait times out; process identity/census cannot be established here.
- `HazardPackPrimitiveTests.test_natural_exit_census_proves_survivors_gone_before_recording_the_exit`
  and `test_supervision_stop_terminates_the_group_and_returns_its_refusal`:
  group absence is not proven in this sandbox.
- `Ruling76DriverTests.test_observer_faults_do_not_change_success_or_failure_chain_rc`:
  the existing observer raises `SystemExit(19)` through the deliberately
  re-raising driver path (R8-1/D8-1); the old test expects it swallowed.

The shared production files and shared test files are byte-identical to the
requested base. Their failures were not repaired by changing unrelated
measurement/observer behavior. An isolated five-case replay reproduced the
two census failures and two errors; the 8-second journal timing case passed
(5 run, 1 pass, 2 failures, 2 errors). Logs: `/tmp/jw-r1arm-tmp/shared-tests.log`,
`shared-failures-replay.log`, `snapshot-tests.log`, `r1-arm-tests.log`.
Initial harness-only failures (temporary fixture missing identity pins,
pending-sensor shape, W1 inventory, denied process census) were corrected;
none is hidden by a skip. The new harness now supplies explicit synthetic
censuses, and its child handles are reaped even on interrupt.

## Residual risk

Live arming and final verification remain the magistrate's. The shared
hazard interrupt path can leave its diagnostic monitor/meter alive until
dead-man recovery (already disclosed at integration report line 1191); this
route does not change that shared behavior. The sandbox replay proves the
R1 driver's restore with synthetic process census, not live hardware custody.
Unsized disk allocation and independent diagnostic bookends are explicitly
recorded; no W1/claim calibration or meter validation is claimed.
