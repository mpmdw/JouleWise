# Delta re-audit of fix round 2 at fc21ab3b (terra xhigh, direct run), verbatim

```json
{
  "schema":"claude-codex-report/v1",
  "genre":"review",
  "status":"findings",
  "completion":"complete",
  "summary":"Round-2 cures execute, but two adopted kill-switch contract deviations leave the cold gate NOT LANDABLE.",
  "workspace":{"base_requested":"b93f5ffb","base_mode":"exact","head_start":"fc21ab3b0114d820c1b1173600b482412d355266","head_end":"fc21ab3b0114d820c1b1173600b482412d355266","upstream_end":"fc21ab3b0114d820c1b1173600b482412d355266","branch":"feat/2026-09-03-magistrate-watchdog"},
  "pathspec":[],
  "unowned_dirty":[],
  "verdict":{"landing":"NOT LANDABLE","findings":[
    {"id":"F3","severity":"blocker","title":"STOP glob still conflicts with adopted row 6","evidence":"File 15 requires refs/heads/ops/stop-magistrate*; code and guide use refs/heads/ops/stop*. File 04 proposes the wider glob as a possible cure, but does not record an adopted amendment, so the guide's claimed amendment is unsupported by the supplied authorities."},
    {"id":"R1","severity":"blocker","title":"F2 cure delays remote stop recognition by up to five minutes","evidence":"File 15 requires the remote positive-control/stop probe each poll. ResidentSupervisor caches CLEAR and refreshes only every 300 s; executed probe showed a fresh STOPPED result was not called at elapsed 0 and state remained ACTIVE."}
  ]},
  "verification":[
    {"id":"V1","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_magistrate_watchdog.SupervisorTests.test_notice_ack_is_consumed_before_child_exit tests.test_magistrate_watchdog.SupervisorTests.test_sleeping_remote_probe_cannot_delay_plan_term_or_kill tests.test_magistrate_watchdog.SupervisorTests.test_clock_uncertain_resident_drains_with_monotonic_deadlines","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 3 tests in 0.013s","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 3 tests in .*\\n\\nOK"}},
    {"id":"V2","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_magistrate_watchdog","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 36 tests in 0.072s","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 36 tests in .*\\n\\nOK"}},
    {"id":"V3","kind":"smoke","cmd":"First fenced dry-run block in docs/process/MAGISTRATE_WATCHDOG.md, executed verbatim with a fresh $TMPDIR root","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["decision=HOLD_CENSUS reason=production census non-empty inside plan span","WOULD_SPAWN none"]},"expected":{"exit_code":0,"tail_regex":"WOULD_SPAWN none"}},
    {"id":"V4","kind":"inspection","cmd":"git diff --check b93f5ffb -- scripts/magistrate_watchdog.py tests/test_magistrate_watchdog.py docs/process/MAGISTRATE_WATCHDOG.md","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[]},"expected":{"exit_code":0,"tail_regex":"^$"}}
  ],
  "flags":[
    {"id":"G1","kind":"lead_ruling","level":"blocking","text":"The supplied authorities conflict on STOP_REF_GLOB; no supplied adopted ruling authorizes the wider glob or five-minute resident cadence.","needs":"Record a later ruling, or align code/docs with file-15 row 6 and re-audit the stop path."},
    {"id":"G2","kind":"residual_risk","level":"nonblocking","text":"No real no-TTY session, install, launchd load, or destructive twin-adoption rehearsal was run.","needs":"Lead-controlled gates remain required before installation."}
  ]
}
```

## Findings

| Severity | ID | Finding |
|---|---|---|
| blocker | F3 | The current `refs/heads/ops/stop*` deliberately differs from file-15’s adopted `refs/heads/ops/stop-magistrate*`. File 04’s N2 is a refuter recommendation, not an adopted amendment. |
| blocker | R1 | The asynchronous F2 solution preserves deadline timing but changes the remote stop switch from “each poll” to at most once per five minutes. A fresh STOPPED probe was not called at elapsed 0; the resident stayed `ACTIVE`. |

## Executed cure evidence

| Item | Result |
|---|---|
| F1 | Child exit with matching `notice.ack`: `notice_pending=[]`, persisted `[]`, acknowledgment absent. |
| F2 | Injected `sleep(30)` probe: TERM at 0.000933 s and KILL at 0.001857 s; both under 10 s. |
| F4 | Documented temp-custody dry run passed: plist valid, `HOLD_CENSUS`, only `WOULD_WRITE`, `WOULD_SPAWN none`, no custody root. |
| F5 | Resident clock skew: `CLOCK_UNCERTAIN`, no launch, request, TERM, then KILL. |
| F6 | Atomic temporary-file inventory is now documented. |

Mutation replays all failed as required:

| Mutation | Failing test(s) |
|---|---|
| `TERM_LEAD_S=17*60` | `test_plan_fence_boundaries_request_term_kill_and_completion` |
| Ladder rung `7199` | `test_usage_backoff_ladder_and_activation_jitter` |
| Request step dropped | `test_cooperative_exit_after_request_never_signals`; `test_ignored_request_gets_term_then_kill_and_census` |
| Positive control ignored | `test_stop_branch_present_absent_and_positive_control_failure` |
| Belt flipped | `test_fixed_belt_is_half_open` |

Same-signature statement: file-04 findings are not reproduced; file-05 F1, F2 deadline behavior, F4, F5, and F6 are closed. File-05 F3 remains, and R1 is a distinct stop-cadence regression introduced by its F2 cure.

## Residual risk

The real no-TTY, launchd, install, and twin-adoption gates remain intentionally unexecuted.
---

## Magistrate disposition (2026-09-04 02:20 PDT)

F3 (stop glob `refs/heads/ops/stop*` vs file 15 row 6 `ops/stop-magistrate*`) and R1 (remote-stop recognition delayed up to one 300 s tick because the F2 cure moved the network probe out of the resident enforcement loop) are both deliberate magistrate rulings, not code defects: the glob was widened on the execution refuter's N2 (a prefix typo must not be silent), and a one-tick latency on Ed's remote emergency lever is acceptable under D-161 (the kill switch is not a physics fence; the resident loop must never block on the network). Both are recorded as dated amendments to file 15 rows 4 and 6 on main so the object matches the ruled text; the cold gate reads the amended rulings. The code is otherwise LANDABLE per this delta's own execution table.
