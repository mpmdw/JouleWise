# 1. Topology

## Recommendation

Use one user LaunchAgent, label `com.joulewise.magistrate`, with `RunAtLoad`,
`StartInterval = 60`, and `WatchPaths` on `/Users/edr/night-custody` and
`/Users/edr/code/JouleWise/RUN_STATE.md`. Each launch runs a Python supervisor.
If it starts a headless magistrate, that supervisor remains alive, watches the
child and the clocks, and enforces stand-down; otherwise it exits quickly. No
`KeepAlive`, no root daemon, and no second scheduler.

This is the best of the three choices because:

- `StartInterval` is the independent wake layer: a clean one-turn `claude -p`
  exit, a watchdog crash, a usage-limit exit, or a missed `WatchPaths` event is
  reconsidered on the next minute.
- `WatchPaths` makes a newly authored plan or changed restart pointer visible
  promptly; it is an accelerator, not the sole clock.
- The supervisor can hold an owned-process record while `claude -p` is alive
  and can use the union of all plan intervals, not a calendar guess.
- The night driver already uses a Python parent that starts the chain in its
  own session and polls the production census while the chain lives
  (`scripts/run_night.py:392-480`). Reusing that supervision shape is smaller
  and more reviewable than putting loop semantics in launchd.
- D-127 requires launch, liveness proof, bounded retry/backoff, and an
  independent launchd wake layer (`docs/decision_log.md:8254-8260`); D-169
  makes this unattended lane the priority
  (`docs/decision_log.md:10463-10474`).

The gate module is `joulewise/night_gate.py`, not `scripts/night_gate.py`; the
driver imports `NightPlan`, `agent_census`, and `evaluate_night` from that
module (`scripts/run_night.py:28-37`). The watchdog must import and call the
same `agent_census`, whose exact command and empty result are defined at
`joulewise/night_gate.py:34` and `joulewise/night_gate.py:388-415`. It must not
copy or reinterpret the regex.

## Rejected alternatives

1. **One calendar-only job that starts a polling loop — reject.** A single
   daily wake has a one-day recovery latency if the process dies after that
   wake. Its time must also be rewritten whenever plan timing changes. The
   current night jobs demonstrate that calendar entries are plan-specific
   (`configs/launchd/com.joulewise.night.plist.template:25-31`), while plans
   carry arbitrary `t0_epoch_s` and `window_max_s`
   (`joulewise/night_gate.py:168-179`). A permanent poller with `KeepAlive`
   also makes quiet-window behavior harder to audit than a one-minute
   re-evaluation that becomes silent inside a fence.

2. **Extend the courier baton — reject.** The existing courier is a one-turn
   `claude -p` invocation with text output and a fixed tool list
   (`scripts/run_night.py:610-629`). `run_courier` treats `courier.sent` as
   success, then releases `courier.lock` in `finally`
   (`scripts/run_night.py:718-814`), even though the prompt tells the courier
   to continue the next lane after writing that marker
   (`docs/process/NIGHT_COURIER_PROMPT.md:14-19`). Thus `courier.sent` proves
   the email, not continued loop ownership. If the continuation dies there is
   no next wake; if it remains alive after the lock disappears, it can become
   the next night's census adversary. The independent watchdog should consume
   `courier.sent`, not overload its meaning. This is the audit's F3/B10
   finding
   (`/Users/edr/code/JouleWise-wt-decode-id/docs/process_traces/2026-09-02-fresh-fable-audit/01-audit-night-loop.md:138-180,223-249`).

## launchd plist skeleton

`[not executed — design skeleton; installation is cold-gated]`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.joulewise.magistrate</string>

  <key>ProgramArguments</key>
  <array>
    <string>/usr/bin/python3</string>
    <string>/Users/edr/code/JouleWise/scripts/magistrate_watchdog.py</string>
    <string>supervise</string>
    <string>--repo</string>
    <string>/Users/edr/code/JouleWise</string>
    <string>--custody-parent</string>
    <string>/Users/edr/night-custody</string>
    <string>--state-dir</string>
    <string>/Users/edr/Library/Application Support/JouleWise/magistrate</string>
  </array>

  <key>WorkingDirectory</key>
  <string>/Users/edr/code/JouleWise</string>

  <key>EnvironmentVariables</key>
  <dict>
    <key>PATH</key>
    <string>/Users/edr/.local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
    <key>PYTHONDONTWRITEBYTECODE</key>
    <string>1</string>
  </dict>

  <key>RunAtLoad</key>
  <true/>
  <key>StartInterval</key>
  <integer>60</integer>
  <key>WatchPaths</key>
  <array>
    <string>/Users/edr/night-custody</string>
    <string>/Users/edr/code/JouleWise/RUN_STATE.md</string>
  </array>
  <key>ThrottleInterval</key>
  <integer>30</integer>
  <key>ProcessType</key>
  <string>Background</string>

  <key>StandardOutPath</key>
  <string>/Users/edr/Library/Logs/JouleWise/magistrate.out</string>
  <key>StandardErrorPath</key>
  <string>/Users/edr/Library/Logs/JouleWise/magistrate.err</string>
</dict>
</plist>
```

The installer creates the two parent directories, renders this template, runs
`plutil -lint`, and supports `--render-only` before it offers install. It must
not call `launchctl` until the cold gate is green and Ed's approval email has
been recorded. The present night installer already separates render-only from
bootstrap (`scripts/install_night_agent.sh:67-72,137-159`); use the same
shape. This report is design input, not approval.

# 2. Exact state machine

## Inputs and safety calculations

On every decision, while holding an advisory `watchdog.lock`, read:

1. **All plans:** `/Users/edr/night-custody/*/night_plan.json`, parsed with
   `NightPlan.from_mapping`. The existing parser requires an exact key set and
   validates the plan class, clocks, positive window, HEAD, and paths
   (`joulewise/night_gate.py:102-114,168-250`). A malformed plan makes safety
   unknowable, so it causes `HOLD_UNSAFE` and a deduplicated pending alert.
2. **Civil and monotonic clocks:** civil time in `America/Los_Angeles` decides
   fences; monotonic time decides retry and kill timeouts. Store the last pair.
   If the two deltas differ by more than 60 seconds, enter `CLOCK_UNCERTAIN`
   until two consecutive one-minute samples agree.
3. **Fixed fences:** treat 02:45:00 through the end of the 03:30 minute as
   `[02:45:00, 03:31:00)`, and the 07:00 minute as
   `[07:00:00, 07:01:00)`, local time.
4. **Plan fences:** for every valid plan use the closed interval
   `[t0_epoch_s - 1800, t0_epoch_s + window_max_s + 300]`. The 300 seconds is
   the current courier deadline (`scripts/run_night.py:42-49`), and the driver
   uses `t0 + window_max_s + COURIER_DEADLINE_S` as its completion epoch
   (`scripts/run_night.py:900-901`). The union of fixed and plan fences is
   `unsafe_now`. Equality is unsafe.
5. **Production census:** call `agent_census(make_probes())`. Launch is allowed
   only for exit 1 plus empty stdout, exactly as production requires
   (`joulewise/night_gate.py:388-415`). A hit is never killed merely because it
   matched the census.
6. **Remote stop:** query the GitHub contents API for root file
   `MAGISTRATE_STOP` on `main`, using the already authenticated `gh` client:
   `gh api repos/mpmdw/JouleWise/contents/MAGISTRATE_STOP?ref=main`. HTTP 200
   means stopped; 404 means not stopped. This does not fetch or move the dev
   checkout. On transport/auth error retain the last known value and emit only
   one transition event. `[not executed — proposed remote-control probe]`
7. **Courier state:** for the most recent plan at or before `now`, read
   `<custody_root>/night/courier.sent`. The present dead-man also treats this
   marker as the completed-notification gate (`scripts/run_night.py:1301-1321`).
8. **Owned session:** read `magistrate.lock`, containing `activation_id`, PID,
   PGID, process-start token, binary path/version, mode, and launch epoch.
   Validate PID, PGID, start token, and executable before signaling. A PID
   mismatch is stale state, not authority to kill a process.
9. **Durable service state:** read `state.json`: state, activation ID,
   attempt number, next-attempt monotonic deadline, usage-backoff level,
   pending/sent notice IDs, last clock pair, last stop observation, and last
   error signature.

## Shared launch interlock: the race closure

The census alone is not a mutex. Add one advisory lock at
`/Users/edr/night-custody/.agent-launch.lock` and use it in both paths:

- The watchdog holds it while it reloads plans and clocks, proves
  `unsafe_now == false`, runs the exact production census, creates
  `magistrate.lock`, and spawns `claude`.
- `scripts/run_night.py` holds the same lock from immediately before
  `evaluate_night` through the once-only `chain.started` claim and child
  spawn. Today the driver evaluates the gate at `scripts/run_night.py:1106-1109`
  and claims/spawns later at `scripts/run_night.py:1198-1228`; the proposed
  lock closes that interval.

Temporal exclusion (no magistrate in the preceding 30 minutes) is the main
protection; the shared lock closes the last-moment plan/install and simultaneous
fire race. A cold-gate mutation test must prove that removing either side of
the lock allows the adversarial schedule.

## States and transitions

| State | Entry / action | Exit | Writes |
|---|---|---|---|
| `BOOT` | Acquire nonblocking `watchdog.lock`; read state, plans, stop, lock, and clocks. If another supervisor holds the lock, exit 0. | `STOPPED`, `HOLD_UNSAFE`, `WAIT_CENSUS`, `BACKOFF`, `STARTING`, or `ACTIVE`. | None unless recovery changes state. |
| `STOPPED` | Remote `MAGISTRATE_STOP` is present. If an owned PGID exists, terminate it; never signal an unowned census hit. Do not launch a notifier. | When a later successful remote check sees 404, create a new activation and go to `READY`. | One atomic `state.json` replacement and one event on entry/exit; owned lock removal only after the PGID is gone. |
| `CLOCK_UNCERTAIN` | Wall/monotonic deltas disagree. This is a physics/timing boundary, so launch fails closed. Drain an owned session if a plan might be near. | Two consecutive sane samples, then recompute from scratch. | Transition only; no per-tick writes. |
| `DRAINING` | Begins 10 minutes before the earliest plan-unsafe boundary (normally t0-40). `checkpoint` returns `STAND_DOWN`. The session must make state durable, email Ed, stop Codex children, and exit. At boundary-5 min send SIGTERM to the validated owned PGID; at boundary-4 min send SIGKILL if needed. If no stand-down email was acknowledged, census is empty, and at least 3 minutes remain, start one notification-only `claude -p`, hard-bounded to finish one minute before the boundary. | Production census is empty and notice is sent/pending; then `HOLD_UNSAFE`. | State/event transitions, notice acknowledgement, attempt output, owned lock lifecycle. |
| `HOLD_UNSAFE` | Inside any fixed or plan fence, or any plan is malformed. No census, GitHub call, network, state rewrite, email, or agent launch. Exit silently so the quiet interval gets no periodic output. | First tick outside every fence goes to `WAIT_COURIER` or `READY`. | None while unsafe. The transition was recorded before entry when possible. |
| `WAIT_COURIER` | Latest completed plan is still inside its slack, or its courier/chain lock is live. Let the existing courier/dead-man own result delivery. | `courier.sent` appears -> `READY`; after plan fence ends with no marker -> `RECOVER_COURIER`. | Transition only. |
| `RECOVER_COURIER` | Outside every fence, acquire the shared launch lock, recheck census, then launch the top-level magistrate in recovery mode. Its first work is the existing handback/result email; it writes `courier.sent` only after Gmail accepts the email, matching the current prompt contract (`docs/process/NIGHT_COURIER_PROMPT.md:7-17`). | On marker/heartbeat -> `ACTIVE`; on failure -> `BACKOFF`. | Same as `STARTING`, plus `courier.sent` written by the agent only after accepted email. |
| `WAIT_CENSUS` | No valid owned lock, but the exact census is nonempty. Record at most once per distinct bounded census digest. Never broad-kill. | Empty census -> `READY`; an owned orphan group -> validate and drain it. | One transition/digest change only. |
| `READY` | Stop absent, clocks sane, outside fences/drain lead, courier settled, backoff expired, no owned child. | Under the shared lock, re-read every input and either remain/redirect or go `STARTING`. | None before the launch transaction. |
| `STARTING` | Atomically create `magistrate.lock`, start `claude -p` in a new process group, and supervise it. Its first tool act must acknowledge heartbeat. | Heartbeat within 60 s -> `ACTIVE`; otherwise TERM/KILL owned group -> `BACKOFF`. | Lock, attempt stream/stderr logs, heartbeat, state, event. |
| `ACTIVE` | A validated owned group and heartbeat exist. Keep the Python supervisor alive; poll plans/stop/clocks every 15 s and stream-output mtime every 60 s. A logical activation persists across clean one-turn fallback relaunches. | Drain/stop takes precedence; clean one-turn exit -> `READY` under same activation; usage error or start failure -> `BACKOFF`; four-hour hard lifetime -> terminate and `BACKOFF`. | Transition/attempt completion only, not each poll. |
| `BACKOFF` | No child. Generic failures use 2, 5, 15, 30, then 60 minutes capped; recognized usage exhaustion uses §4. Safety transitions override the timer. | Timer expires outside fences -> `READY`. | State/event only when level or error signature changes. |

## Every watchdog write

The watchdog writes only below
`~/Library/Application Support/JouleWise/magistrate/`, except for the shared
custody lock and launchd's two log files:

- `watchdog.lock`: opened for `flock`; stable zero-byte coordination file.
- `state.json`: atomic temp-write, file `fsync`, `os.replace`, directory
  `fsync`; rewritten on transitions, not polls.
- `events.jsonl`: append+`fsync` once per transition, distinct error signature,
  signal, launch, exit, and notice acknowledgement.
- `magistrate.lock`: O_EXCL JSON claim; retained until the whole owned PGID is
  proven gone, then unlinked and directory-fsynced.
- `heartbeat.json`: atomic first-action liveness acknowledgement, keyed by
  activation and attempt.
- `attempts/<activation>-<attempt>.stream.jsonl` and `.stderr.log`: exact child
  output; no secrets or prompt text are copied into `events.jsonl`.
- `/Users/edr/night-custody/.agent-launch.lock`: stable zero-byte shared lock.
- `~/Library/Logs/JouleWise/magistrate.{out,err}`: launchd diagnostics; the
  supervisor stays silent on ordinary unsafe ticks.

It does **not** edit a plan, `RUN_STATE.md`, the durable pause, the dev
worktree, `courier.sent`, or `MAGISTRATE_STOP`. The relaunched top-level agent
may edit/push under the standing mandate and normal gates. Its durable
resumption source is the repo: `RUN_STATE.md` declares itself the single
running pointer (`RUN_STATE.md:1-11`) and currently points to a pushed durable
pause with the exact branch/worktree and resume sequence (`RUN_STATE.md:13-32`;
the pointed file explains that everything needed is committed or
re-derivable at
`/Users/edr/code/JouleWise-wt-decode-id/docs/process_traces/2026-09-02-decode-identity-set/39-pause-state-2026-09-02.md:1-30`).

## Stand-down ownership

**Recommend watchdog-owned hard stand-down, with cooperative session duties.**
`ScheduleWakeup` is advisory: if present, the session uses it to call
`checkpoint`, make a durable pause, email Ed, stop its Codex children, and
exit. The safety proof does not depend on that tool. The external supervisor
owns the no-later-than boundary and TERM/KILL of only its recorded PGID.

This supersedes the old behavioral dependency on Ed. R-9 currently says the
magistrate stops its loop/session and Ed closes interactive apps
(`docs/process_traces/2026-09-01-unattended/MAGISTRATE-RULING-UNATTENDED-STAGE1.md:159-168`),
while Ed's 2026-09-02 ruling now permits the magistrate to terminate its own
session and Codex children. The watchdog must never kill arbitrary matches
from `pgrep`; those remain a refusal. The first install handoff is: current
magistrate makes the pause durable, emails Ed, installs only after his email
approval, then exits voluntarily. Thereafter every killable magistrate is a
watchdog-owned PGID.

## Python skeleton

`[not executed — design skeleton]`

```python
def supervise(cfg, probes):
    with try_flock(cfg.state_dir / "watchdog.lock") as owned:
        if not owned:
            return 0
        state = load_state(cfg)
        plans = load_all_plans(cfg.custody_parent, NightPlan.from_mapping)
        now = probes.clock_pair()
        child = validate_owned_group(read_magistrate_lock(cfg))

        if inside_any_fence(now.wall, plans):
            # Deliberately silent and read-only during a quiet fence.
            return 0

        stop = cached_remote_stop_probe(state, probes.gh_api)
        if stop.is_set:
            terminate_owned_only(child, state)
            transition_once(state, "STOPPED")
            return 0

        if clock_uncertain(state.last_clock, now):
            terminate_if_plan_could_be_near(child, plans, state)
            transition_once(state, "CLOCK_UNCERTAIN")
            return 0

        deadline = earliest_unsafe_start(plans, now.wall)
        if child and now.wall >= deadline - DRAIN_LEAD_S:
            cooperative_then_forced_standdown(child, deadline, state)
            return 0
        if child:
            return monitor_child_until_exit_or_boundary(child, plans, state)

        if backoff_active(state, now.monotonic):
            return 0
        mode = courier_recovery_mode(plans, now.wall)  # normal/recovery/hold
        if mode == "hold":
            return 0

        with blocking_flock(cfg.custody_parent / ".agent-launch.lock"):
            plans = load_all_plans(cfg.custody_parent, NightPlan.from_mapping)
            now = probes.clock_pair()
            if inside_or_near_any_fence(now.wall, plans, DRAIN_LEAD_S):
                return 0
            census, refusal = agent_census(make_probes())
            if refusal is not None:
                transition_on_digest(state, "WAIT_CENSUS", census.stdout)
                return 0
            child = spawn_new_process_group(build_claude_argv(mode), cfg.repo)
            claim_magistrate_lock_exclusive(child, state, mode)

        return monitor_start_then_child(child, plans, state)
```

# 3. Launch command, prompt, and headless cadence

## Command

Use the stable symlink, not its resolved version target:

`[not executed — proposed launch command; no Claude process was spawned from this delegated Codex session]`

```sh
cd /Users/edr/code/JouleWise
exec /Users/edr/.local/bin/claude -p "$MAGISTRATE_PROMPT" \
  --model fable \
  --effort high \
  --name joulewise-magistrate \
  --output-format stream-json \
  --verbose \
  --permission-mode dontAsk \
  --permission-prompts none \
  --allowedTools "Read,Glob,Grep,Bash,Edit,Write,Task,Skill,ScheduleWakeup,mcp__codex__codex,mcp__codex__codex-reply,mcp__claude_ai_Gmail__send_message"
```

The supervisor sets `cwd=/Users/edr/code/JouleWise`, the PATH from the plist,
`MAGISTRATE_ACTIVATION_ID`, `MAGISTRATE_ATTEMPT_ID`, and
`MAGISTRATE_MODE=normal|recovery|notify`, and starts a new process group. It
parses/archives stream JSON so a final usage-limit error is classifiable.

Why these flags:

- `fable`, effort `high`: capable lead with bounded spend; a later model change
  is a reviewed configuration change, not auto-selected by the script.
- `dontAsk` plus no permission-prompt host: headless calls cannot block on a
  nonexistent approver. Only the explicit tool list is available; there is no
  bypass mode.
- `stream-json`: machine-readable completion/error and output-activity
  evidence. The existing courier uses `text` output
  (`scripts/run_night.py:621-629`); the watchdog needs more observability.
- The Gmail tool spelling is already exercised by the courier allowlist
  (`scripts/run_night.py:50-52`). The project Codex server is declared in
  `.mcp.json:1-15`, and its child sessions have reverse-Claude disabled there
  (`.mcp.json:7-12`), preserving the one-hop rule.

The installed CLI was inspected as `2.1.259`; `claude --help` showed `-p`,
`--model`, `--effort`, `--output-format`, `--allowedTools`,
`--permission-mode`, and `--permission-prompts`. The command itself and its
permission behavior still require the cold-gate rehearsal. `[not executed]`

## Relaunch prompt (22 lines; hard ceiling 25)

```text
You are the top-level JouleWise magistrate, not a delegated child.
Work from /Users/edr/code/JouleWise and the repository alone.
First act: run `python3 scripts/magistrate_watchdog.py heartbeat --activation "$MAGISTRATE_ACTIVATION_ID"`.
Read `AGENTS.md`, then `RUN_STATE.md`.
Follow RUN_STATE's current durable-pause pointer exactly, including its named branch/worktree.
If the pointed file is absent here, read it with `git show` or from that worktree.
Never resume from `/tmp`, `/private/tmp`, a transcript, or another scratchpad.
Run Mission M0 and obey active stop cards and machine-state lanes.
Resume D-128/D-169: drive the experiment, analysis, review, and paper loop.
Preserve existing dirty work; inspect it before editing; never reset or clean it.
You may spawn Codex children under the bridge contract; remain the top-level lead.
Do not start or continue any `[QUIET-MAC]` work while any agent is alive.
Before each work block and consequential write, run `python3 scripts/magistrate_watchdog.py checkpoint`.
If it prints `STAND_DOWN`, stop new work, make current state durable in the repository, and push it.
Send Ed the pending stand-down email with Gmail, then acknowledge it through the watchdog.
Stop all Codex children and exit before the printed deadline.
If a launch notice is pending, email Ed once for this activation and acknowledge it.
If a prior night lacks `courier.sent`, perform the courier handback first and mark sent only after email acceptance.
Perform one bounded, reviewable work slice; do not merge or install without their normal gates.
If ScheduleWakeup works in `-p` mode, use it only through the watchdog's next-safe deadline.
Otherwise end cleanly after the slice; StartInterval will relaunch when safe.
End by running `python3 scripts/magistrate_watchdog.py checkpoint` and recording durable state.
```

## Does `/loop` survive `-p`?

Unknown. `claude --help` says `-p/--print` prints a response and exits, and the
help output does not establish that `ScheduleWakeup` keeps a print-mode process
alive. Testing it would require launching Claude, which this Claude-originated
Codex bridge is forbidden to do. `[not executed]`

Therefore `ScheduleWakeup` is an optimization only. The guaranteed fallback is
the LaunchAgent's next `StartInterval`: whenever the prior process group is
gone, no lock is held, backoff has expired, the exact census is empty, courier
state is settled, and every fence is open, it launches a fresh repo-resuming
turn. The `activation_id` remains stable across these fallback turns until a
stand-down, so notices and backoff are deduplicated.

# 4. Usage-limit behavior

Parse the final stream-JSON/error text into `usage_exhausted` only on a
reviewed set of exact CLI error signatures. Unknown nonzero exits use generic
backoff, never an optimistic usage classification.

For `usage_exhausted`:

1. Terminate/reap the owned PGID and preserve all dirty work.
2. Enter `BACKOFF_USAGE`; attempts occur after 15 minutes, 30 minutes,
   60 minutes, 2 hours, then every 2 hours. Add deterministic 0-120-second
   jitter from the activation ID so retries do not align with the 07:00 job.
3. Never retry inside drain/fence time. A newly observed plan preempts backoff
   into stand-down.
4. Write one event when entering `BACKOFF_USAGE`, one if the error signature
   changes, and one when heartbeat proves recovery. Do not append per-tick
   events.
5. Queue one `usage_backoff` notice in `state.json`. The next successfully
   started session includes it in its single activation/recovery email; no
   email is attempted on each failed launch.
6. Reset the level only after a successful heartbeat plus a completed tool
   action, not merely process creation.

The current durable pause shows usage exhaustion is a real operating state and
is explicitly designed for repo-only succession (`RUN_STATE.md:13-32`). The
literal requirement to email while the account cannot start either the
magistrate or Claude-based courier is impossible; §8 states the necessary
contract clarification.

# 5. Failure table

| Failure | Detection | Containment / recovery | Who hears |
|---|---|---|---|
| Watchdog invocation dies | launchd sees its main process exit; the next 60-second interval starts a new invocation. New invocation finds `magistrate.lock` and validates the group rather than spawning blindly. | `watchdog.lock`, owned-lock validation, production census, and shared launch interlock prevent a duplicate. If the child survived, the new supervisor adopts observation of the recorded PGID; if identity is uncertain it never signals and enters `WAIT_CENSUS`. | Next successful activation email includes a detected tick gap. If launchd itself is disabled or repeatedly cannot execute Python, nobody hears remotely under the approved channels; local launchd stderr is the only evidence. |
| Session hangs forever | No clean exit; hard lifetime reaches four hours, or a drain deadline approaches. Stream log inactivity is diagnostic only, not sufficient by itself to kill a reasoning/tool call. | TERM then KILL only the validated owned PGID; retain the lock until every group member is gone; preserve worktree; generic backoff. Plan drain always overrides the four-hour limit. | Cooperative session emails if it reaches checkpoint. Otherwise a pre-fence notification-only turn attempts the deduplicated stand-down email; if Claude cannot start, notice is deferred and explicitly pending. |
| Session exits mid-fix, dirty worktree remains | Child exit plus `git status --porcelain=v2` from the canonical dev checkout. | Never reset, clean, stash, or switch the dirty tree. Record only path/status summary, wait generic 2 minutes, then launch the same logical activation with the dirty summary; prompt reads RUN_STATE/durable pause and inspects the diff first. Current M0 also requires workspace inspection (`docs/agent_playbook.md:68-72`). | No new launch email for a same-activation fallback; next state-change email includes the interruption. |
| Two magistrates appear | O_EXCL `magistrate.lock`, nonblocking `watchdog.lock`, exact census, and PID/PGID inventory. The shared night/watchdog lock makes census+spawn atomic relative to gate census+chain spawn. | Never launch the second. Kill only a group whose lock identity proves watchdog ownership; an unowned Claude/Codex/T3 process remains a census hold. The production gate already refuses any nonempty census (`joulewise/night_gate.py:611-619`). | One deduplicated `duplicate_or_unowned_agent` notice at next safe successful email; local event immediately. |
| Clock jumps/skews | Compare elapsed wall time to elapsed monotonic time; >60-second disagreement or invalid local-time conversion enters `CLOCK_UNCERTAIN`. | Fail closed for launch because fence timing is physics/evidence-adjacent. Drain a known child conservatively if any plan might be within 40 minutes; require two sane one-minute samples before release. | Active session is asked to email during drain; otherwise next successful session sends the queued notice. |
| Claude auto-update changes/prunes the binary | Before spawn, `lstat` `/Users/edr/.local/bin/claude`, resolve only for diagnostics, verify the symlink target is executable, and capture `claude --version`; spawn through the symlink path. | Never persist a version-file path. If symlink is missing/broken, enter generic backoff; do not guess a newest version. Current installer resolves the symlink to a version target (`scripts/install_night_agent.sh:50-56`), and the current driver falls back through PATH only when a requested path is missing (`scripts/run_night.py:571-596`); the watchdog avoids that pin/prune failure class. | If no Claude binary can run, neither Gmail-MCP route can send; local event now, deferred email after recovery. The exact 2026-09-02 failure class is documented in the audit (`/Users/edr/code/JouleWise-wt-decode-id/docs/process_traces/2026-09-02-fresh-fable-audit/01-audit-night-loop.md:207,226`). |
| Remote stop appears | Successful GitHub API response 200 for `MAGISTRATE_STOP`, with commit SHA recorded. | Enter `STOPPED`, terminate only the owned group, suppress all future launches until a later successful 404. No email is required to honor a stop. | Ed caused it; local event records it. A later restart email cites the stop and clearing SHAs. |
| Remote-stop query fails | `gh api` nonzero/timeout/auth failure. | Preserve last known stop value; exponential network-probe backoff, one error transition. Do not mutate or fetch the checkout. | Next successful agent email; no immediate route if both GitHub and Claude are unavailable. |
| `courier.sent` never appears | Plan fence has ended, no live chain/courier lock, marker absent. | Outside all fences and the 07:00 minute, launch one recovery-mode top-level session. It performs the result handback first and writes the marker only after accepted Gmail delivery. Existing dead-man retries only after the calculated completion epoch (`scripts/run_night.py:1314-1321,1375-1406`). | Recovery email is both the missing results notice and the relaunch notice, clearly labelled. |

# 6. Bench test plan

No test below was run in this design-only seat. Each is `[not executed]`.
Tests inject wall/monotonic clocks, census results, process table, filesystem,
GitHub responses, Gmail acknowledgements, and process spawning. No real Claude,
email, signal, night, or measurement is used in unit tests.

## Unit tests (`tests/test_magistrate_watchdog.py`)

- `[not executed]` `test_fixed_fence_boundaries_include_0245_through_0330_and_0700_minute`
- `[not executed]` `test_plan_fence_is_t0_minus_1800_through_window_plus_courier_deadline`
- `[not executed]` `test_union_of_all_plans_blocks_launch_and_malformed_plan_holds_unsafe`
- `[not executed]` `test_dry_run_performs_no_writes_spawns_signals_network_or_email`
- `[not executed]` `test_exact_production_census_function_is_called_and_hit_blocks_launch`
- `[not executed]` `test_o_excl_claim_and_watchdog_flock_allow_exactly_one_magistrate`
- `[not executed]` `test_stale_pid_or_start_token_is_never_signaled`
- `[not executed]` `test_owned_group_gets_term_then_kill_and_lock_survives_until_group_empty`
- `[not executed]` `test_new_plan_preempts_active_session_into_drain_before_t0_minus_1800`
- `[not executed]` `test_no_output_state_or_network_write_occurs_while_unsafe`
- `[not executed]` `test_courier_sent_holds_then_recovery_launches_only_after_slack`
- `[not executed]` `test_usage_error_backoff_caps_at_two_hours_and_notice_is_deduplicated`
- `[not executed]` `test_generic_error_backoff_and_successful_heartbeat_reset`
- `[not executed]` `test_dirty_worktree_is_preserved_and_reported_to_successor_prompt`
- `[not executed]` `test_wall_monotonic_jump_holds_until_two_sane_samples`
- `[not executed]` `test_remote_stop_200_stops_404_releases_and_failure_uses_cache`
- `[not executed]` `test_claude_spawn_uses_stable_symlink_without_resolving_version_target`
- `[not executed]` `test_prompt_is_at_most_25_lines_and_has_repo_only_resume_sources`
- `[not executed]` `test_plist_has_label_interval_watchpaths_and_no_keepalive_or_sudo`

## Interlock tests (`tests/test_run_night.py`)

- `[not executed]` `test_night_holds_agent_launch_lock_from_gate_census_through_chain_spawn`
- `[not executed]` `test_watchdog_and_night_adversarial_schedule_never_both_launch`
- `[not executed]` mutation: remove the night-side lock and prove the
  adversarial test fails.
- `[not executed]` mutation: remove the watchdog-side lock and prove the same
  test fails.

## Required scenario fixtures

1. `[not executed]` **Fake plan t0 in 10 minutes:** because `now` is already
   inside `[t0-30 min, ...]`, `--dry-run` must report `HOLD_UNSAFE`, `launch=false`,
   and an empty write plan.
2. `[not executed]` **Fake census hit:** injected output
   `123 claude -p ...` must report `WAIT_CENSUS`; spawn and signal call counts
   remain zero.
3. `[not executed]` **Stop file:** injected GitHub 200 must stop an owned fake
   PGID and suppress launch; 404 on a later tick creates a new activation; API
   failure retains the cached stopped state.

## One end-to-end rehearsal

`[not executed — must run only after the cold gate and Ed's email approval to install]`

1. Create a temporary custody/state root and a fake executable named `claude`
   that emits valid stream JSON, invokes the watchdog heartbeat subcommand,
   records argv/environment, and exits; it never contacts an API.
2. Render `com.joulewise.magistrate.plist` with `--dry-run`, temp roots, injected
   clock file, injected census file, injected GitHub response file, and the fake
   binary. Validate with `plutil -lint`.
3. Bootstrap the user LaunchAgent. First set fake t0 to +10 minutes: observe
   `HOLD_UNSAFE`, zero spawn, zero state mutation during the fence. Then move
   the fake clock beyond window+300: observe exactly one fake launch and one
   heartbeat. Add a fake census hit: observe no second launch. Add the fake
   stop file: observe owned fake group termination and no relaunch.
4. Wait through two `StartInterval` ticks to prove idempotence and no email/
   signal/spawn beyond the expected fake calls.
5. Boot out and remove only the temp plist/state. Preserve the rehearsal log as
   cold-gate evidence. Do not call `scripts/run_night.py run`; this is not a
   measurement-night rehearsal.

# 7. Minimal build list and estimate

| Path | Change | Sol-hours |
|---|---|---:|
| `scripts/magistrate_watchdog.py` | Supervisor, state machine, dry-run/injected probes, heartbeat/checkpoint/ack subcommands, owned-PGID handling, GitHub stop probe, CLI parser | 4.0 |
| `configs/launchd/com.joulewise.magistrate.plist.template` | User LaunchAgent above | 0.5 |
| `scripts/install_magistrate_agent.sh` | Render-only, lint, install/uninstall, absolute paths, cold-gate receipt argument | 1.0 |
| `docs/process/MAGISTRATE_RELAUNCH_PROMPT.md` | Exact <=25-line prompt | 0.25 |
| `tests/test_magistrate_watchdog.py` | State/failure/dry-run/plist/CLI tests | 3.5 |
| `scripts/run_night.py` | Shared launch-interlock acquisition across gate census through chain spawn | 0.75 |
| `tests/test_run_night.py` | Adversarial interlock and mutation-sensitive regressions | 1.0 |
| `docs/process/NIGHT_HANDBACK.md` | One section: watchdog ownership, stop-file procedure, notice semantics, cold-gate/install evidence pointer | 0.5 |
| **Total implementation** | Excludes review/cold-gate waiting and Ed's approval latency | **11.5 Sol-hours** |

No routine `MAGISTRATE_STOP` file is added: absence means run; Ed creates it
in a pushed `main` commit to stop and deletes it in a later pushed commit to
resume. No night plan schema change is required. The production-census helper
is reused, not duplicated.

The build then requires the normal process-mechanism cold gate, focused tests,
canonical suite, adversarial review of signal/lock races, a dry-run plist
rehearsal, and Ed's explicit email approval before user-level installation.
`[not executed]`

# 8. Pushbacks and required contract clarifications

1. **Treat “email at each launch” as one email per logical activation, not per
   OS process attempt.** With `claude -p` fallback, multiple fresh processes
   may implement one between-night activation. Emailing on every retry conflicts
   directly with the requested one-email-per-state-change anti-spam rule.
   Recommendation: a new `activation_id` is created only when leaving a quiet
   stand-down/stop for active work; retries and clean one-turn continuations
   keep the ID and do not resend. Notification-only courier processes are not
   magistrate activations.

2. **Unconditional immediate email is impossible when Claude usage is exhausted
   or the Claude binary is absent.** Both allowed routes—Gmail MCP inside the
   magistrate and the current courier—require starting Claude. The watchdog
   cannot truthfully guarantee an email in exactly the failures where Claude
   cannot start. Recommendation: require durable `notice_pending` plus send on
   the next successful start. If immediate out-of-band delivery is mandatory,
   Ed must separately authorize and provision a non-Claude mail/webhook
   credential; do not bury one in this mechanism.

3. **Define the fixed-fence endpoints explicitly.** This design conservatively
   includes the entire 03:30 minute. If “02:45-03:30” instead means the
   half-open interval ending at 03:30:00, the cold gate should say so and tests
   should pin it. An ambiguous endpoint is not acceptable in a launch guard.

4. **The phone kill switch is eventually consistent, not magic.** A pushed
   `MAGISTRATE_STOP` is the cheapest remote-actionable path because Ed already
   can push and it needs no inbox listener or new credential. It depends on
   GitHub reachability and the machine's existing `gh` authentication. Retaining
   the last known value on network failure follows D-161's instruction not to
   turn trusted-operator controls into elaborate refusal machinery
   (`docs/decision_log.md:10358-10369`). If Ed needs a hard real-time stop
   guarantee during a GitHub outage, that is a new external control-plane
   requirement.

5. **Do not make `ScheduleWakeup` part of the safety case until a headless
   rehearsal proves it.** The watchdog's process-group deadline and repeating
   launchd wake are the proof-bearing mechanisms; `ScheduleWakeup` may improve
   graceful handoff but may not weaken them.

6. **Do not force-kill unowned census hits.** Hands-free operation does not
   justify turning the loose production census into broad process-kill
   authority. Only the watchdog-owned, identity-validated PGID is killable.
   Anything else remains `WAIT_CENSUS`/night refusal, preserving R-3's exact
   predicate and evidence behavior
   (`docs/process_traces/2026-09-01-unattended/MAGISTRATE-RULING-UNATTENDED-STAGE1.md:72-82`).

## Verification status

Executed read-only inspection:

- `git status --short --branch` and `git rev-parse HEAD` in the consult
  worktree: detached clean HEAD `33290b8bbe82b126037101edf8f15cdf96c920da`.
- `git status --porcelain=v2 --branch` and `git rev-parse HEAD` in
  `/Users/edr/code/JouleWise`: clean `main` at the same HEAD.
- Read the controlling AGENTS/bridge contract, M0 intake, decisions D-127,
  D-161, D-169, R-3/R-9, fresh audit sections 2/3/5 B8+B10/6 item 3, target
  code/docs, current durable pause, and both current plan JSON files.
- `claude --version`: `2.1.259 (Claude Code)`; `claude --help` inspected the
  proposed CLI flags. No Claude session was launched.
- `readlink /Users/edr/.local/bin/claude` ->
  `/Users/edr/.local/share/claude/versions/2.1.259`; inspected installed version
  files and found 2.1.251, 2.1.252, 2.1.259.
- `date -r` confirmed plan t0 values as 2026-09-02 and 2026-09-03 at 02:56 PDT.
- `plutil -lint` on the two already installed night plists: both OK.
- `ls` inspected the two already installed night plists; no `launchctl` command
  was run.

Not executed:

- `[not executed]` no test suite or proposed test; this seat changed no repo
  code and the requested output is a design report.
- `[not executed]` no `launchctl`, install, uninstall, signal, email, GitHub API,
  network install, Claude launch, quiet measurement, or night driver command.
- `[not executed]` no proposed plist, script, prompt, state machine, or remote
  stop path exists until implementation and cold-gate approval.

## Recommendation

Adopt the WatchPaths+StartInterval topology as design input, with the shared
night/watchdog launch interlock and watchdog-owned hard stand-down as
non-negotiable safety clauses. Rule activation-scoped email deduplication and
deferred notice during total Claude outage explicitly. Then implement the
eight-path minimal set, run the mutation-sensitive race tests and fake
LaunchAgent rehearsal, pass the process cold gate, obtain Ed's email approval,
and only then install `com.joulewise.magistrate`.
