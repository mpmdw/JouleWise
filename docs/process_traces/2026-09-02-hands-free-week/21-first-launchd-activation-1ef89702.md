# 21 — First watchdog-owned launchd activation of a headless magistrate (2026-09-08 00:51:55 PDT; events.jsonl seq 3, epoch 1788853915)

Q-C9 evidence item 1 (RELAUNCH RESUME PLAN, file 00 §2026-09-04 ~20:15). Written by the launched magistrate
itself, activation `1ef89702-8b11-4463-8d6b-3c1400510f1a`, from the primary artifacts copied verbatim into
`21-activation-1ef89702/` (state.json, events.jsonl, magistrate.lock, heartbeat, the relaunch
prompt, the attempts listing, the launchd job print, the pmset sleep tail, and the process census at 00:55, `21-activation-1ef89702/process-census-0055.txt`)
(notice.ack had already been consumed by the watchdog; no copy exists). <!-- F8 -->

## What happened, in order (all times PDT, from events.jsonl)

| seq | from → to | epoch | reason |
|---|---|---|---|
| 1 | BOOT → FENCED | 1788689333 (2026-09-06 03:08:53) | `belt_02:45_03:30` |
| 2 | FENCED → CLOCK_UNCERTAIN | 1788690995 (2026-09-06 03:36:35) | wall and monotonic deltas disagree (closed lid: MAC-SLEEP-01) |
| 3 | CLOCK_UNCERTAIN → LAUNCHING | 1788853915 (2026-09-08 00:51:55) | all launch predicates clear |
| 4 | LAUNCHING → ACTIVE | 1788853915 | spawned activation 1ef89702-8b11-4463-8d6b-3c1400510f1a |

The watchdog recovered from CLOCK_UNCERTAIN on its own once the lid was opened (Ed, 09-08 ~00:40 per `00-DURABLE-STATE.md` CHECKPOINT step 1): state.json
shows `clock_sane_samples: 36` (copied state.json, last_clock epoch_s 1788854247.5 = 00:57:27) <!-- F7 -->, `remote_stop.state: CLEAR` ("stop branch absent; positive control present"),
`backoff_index: 0`, `attempt: 1`. No operator touched the watchdog state, lock, or events.

## MAGISTRATE_WATCHDOG.md §Install handoff step 6 checks (verified from this activation)

- `attempts/1ef89702-8b11-4463-8d6b-3c1400510f1a/` exists with `prompt.md`, `attempt-1.stream.jsonl`,
  `attempt-1.stderr.log` (empty) — listing in `attempts-listing.txt`.
- `magistrate.lock` names pid 84232 (`claude -p …`, supervisor 84229), status ACTIVE, schema
  `joulewise.magistrate_lock.v1`, and carries NO `first_install_adoption` key — the watchdog-owned one-turn
  `-p` magistrate the doc requires.
- launchd job `com.joulewise.magistrate`: `run interval = 300 seconds`, `last exit code = 0`, program
  python3.14 (`launchctl-print.txt`).

Step 6 also says a nonempty census before that tick is a failed handoff (MAGISTRATE_WATCHDOG.md:256); the 00:55 census (`process-census-0055.txt`) was nonempty (joulewise-53 and the bg-job daemon tree), so the handoff is not clean under the doc's own clause until WATCHDOG-CENSUS-01 lands (joulewise-53's lane). <!-- F12 -->

## First acts of the activation (MAGISTRATE_RELAUNCH_PROMPT order)

1. Heartbeat written at epoch 1788853925 (then corrected to the claude pid 84232 at 1788853935; the first write
   carried the Bash child's pid). Nothing reads the heartbeat today (no occurrence in
   scripts/magistrate_watchdog.py; MAGISTRATE_WATCHDOG.md:81 names no fields); activation 1ef89702 wrote `epoch_s`,
   784a764e wrote `ts` — recorded, not resolved. <!-- F13 -->
2. Launch email to Ed accepted by Gmail: message id `1a0800383847cde1`, subject "JouleWise — headless magistrate
   LAUNCHED 00:51 PDT (activation 1ef89702); a second live session is on the same lanes". It carried the one
   pending notice (`transition-2-clock_uncertain`) and the resume list.
3. `notice.ack` written: `{"activation_id":"1ef89702-8b11-4463-8d6b-3c1400510f1a"}` before the 00:55:36 ack event (events.jsonl epoch 1788854136.9). The watchdog's next
   tick consumed it: events.jsonl gained `{"kind": "notice_acknowledged", "notice_ids":
   ["transition-2-clock_uncertain"], "epoch_s": 1788854136.9}` (00:55:36) and state.json now reads
   `notice_pending: []`; the ack file is gone from the custody root. The copied state.json/events.jsonl are the
   post-acknowledgement versions (`clock_sane_samples: 36` at copy time; F7).

## Findings at launch (not defects of the watchdog; recorded for the next handoff)

- TWO MAGISTRATES COEXIST. Ed started an interactive session (`joulewise-53`, session 1d65b6ea, pid 83953) at
  00:46:54 (lstart in `process-census-0055.txt`), five minutes before the watchdog's launch predicates cleared, with the prompt "get back to work,
  fan out". It then created worktrees from the canonical checkout and launched three gpt-6-astra seats
  (WATCHDOG-CENSUS-01 + RESUME-DAEMON-01; T0-ACID-CLOCK-01; a handoff scout). The watchdog's launch predicates
  do not consider an interactive session a reason to hold — consistent with WATCHDOG-CENSUS-01's premise that a
  shared machine always has other `claude` processes, but it means a launch can land on top of a live human-driven
  lead. The headless magistrate messaged that session (cross-session message a869e477) and emailed Ed the
  lane split: the interactive session keeps its claimed seats; the headless one takes only this trace, the
  durable pointer, and rehearsal-stub preparation. joulewise-53 ACCEPTED with four conditions, all
  honoured: the headless magistrate does not edit the watchdog script/installer/doc/tests; ARMS NOTHING (not even
  a rehearsal stub) while joulewise-53 or its seats are alive (it will
  message when it stands down); lands this trace by PR only; sends Ed no further two-magistrate email. joulewise-53
  also claims the RUN_STATE/TASK_QUEUE rows for the three defect IDs and this relaunch, retirement of the resumed
  twin and bg-job daemon, and the trace dir `docs/process_traces/2026-09-08-handoff-redo/`.
- The auto-resumed twin of session 3c46c831 (pid 71607) and the bg-job daemon/spare (71666/71687) were still
  alive and idle (RESUME-DAEMON-01, in flight in joulewise-53). Not signalled by this activation.
- Sleep hold: at launch the only assertion was the interactive session's `caffeinate -i -t 300`. This activation
  started `caffeinate -i -w 84232` (held while the magistrate pid lives). `pmset -g` shows no `sleepdisabled`.
  Last Maintenance Sleep entry: 00:39:32 (`pmset-sleep-tail.txt`).
- pid 48645 (python3.14, alive since 09-04 04:53 per the census; identified as the leaked 09-04 test stub by joulewise-53, not from this census). <!-- F15 -->

## What this does NOT prove

No night was armed; the night LaunchAgents remain uninstalled (`launchctl list` shows only
`com.joulewise.magistrate`). The REHEARSAL_STUB night through the installed watchdog (state-kernel goal after
WATCHDOG-INSTALL-01) is still owed and must go through NIGHT_HANDBACK email-then-arm.

## Next exact action for THIS activation (durable pointer; supersedes nothing in RUN_STATE)

1. Land this trace by PR from branch `bookkeeping/2026-09-08-activation-evidence` (worktree
   `/Users/edr/code/JouleWise-wt-magistrate-1ef89702`).
2. Hold: no arming while joulewise-53 or its seats are alive. When joulewise-53 messages that it has stood down
   AND its watchdog fixes are on main, prepare the REHEARSAL_STUB plan for the next belt (bench rehearsal block in
   MAGISTRATE_WATCHDOG.md as the template; a real `/Users/edr/night-custody/<plan>` root; night agents installed
   per NIGHT_HANDBACK), email Ed the arm request, arm only on no-NO, then exit before the request deadline.
3. Poll `~/night-custody/magistrate/standdown.request` before every slice; on a request, commit/push here, email
   Ed, stop children, exit within nine minutes.
