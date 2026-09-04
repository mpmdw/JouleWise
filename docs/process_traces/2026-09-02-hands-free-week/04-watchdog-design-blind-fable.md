# Blind Fable design seat — the magistrate relaunch watchdog (`com.joulewise.magistrate`)

Seat: fresh Fable, no loop context. Sources: the brief; audit `01-audit-night-loop.md` §2, §3, §5 (B8, B10), §6 item 3 (worktree `JouleWise-wt-decode-id`); `scripts/run_night.py`, `scripts/install_night_agent.sh`, `joulewise/night_gate.py`, `configs/launchd/com.joulewise.night.plist.template`, `docs/process/NIGHT_HANDBACK.md`, `docs/process/NIGHT_COURIER_PROMPT.md` (all at main 33290b8b in `JouleWise-wt-watchdog-consult`); ruling STAGE1 R-3/R-9; D-127, D-161, D-169. Everything marked **[bench]** was executed this session and is pasted under *Executed evidence* at the end; everything marked **[not executed]** is inference.

Vocabulary used below, built once:
- **census** — the command `/usr/bin/pgrep -lf "codex|claude|t3"`; "empty" means exit status 1 and no output (`night_gate.py:34`, `:388-410`). It matches the *substring* anywhere in any process's full argv, but BSD `pgrep` never reports its own ancestors (`state_kernel.json:2492`; **[bench]** a non-ancestor python process carrying `/x/claude/y` in argv IS reported).
- **plan** — `/Users/edr/night-custody/<plan_id>/night_plan.json` with `t0_epoch_s`, `window_max_s`, `custody_root`, `repo_head` (**[bench]** tonight: t0 = 1788429360 = 2026-09-03 02:56 PDT, window 900 s, repo_head 33290b8b = current main).
- **night span** of a plan — the wall-clock interval `[t0 − 1800 s, t0 + window_max_s + 300 s + 2400 s]`: 30 min stand-down margin before t0; after t0 the driver's own budget (`COURIER_DEADLINE_S = 300`, `run_night.py:45`) plus the courier's worst case (4 attempts × 300 s + 60/180/600 s backoff ≈ 35 min, `run_night.py:46-47`, `:745-805`). The span closes EARLY when `<custody_root>/night/courier.sent` exists, because that file is the courier's "email accepted" record (`NIGHT_COURIER_PROMPT.md:16-17`) and the dead-man treats it as "night over" (`run_night.py:1309-1313`).
- **fixed fence** — local time in `[02:45, 03:30)` or the minute `07:00`. This is the brief's number; it is not in code (**[bench]** grep of `docs/process`, `joulewise`, `scripts`, `configs` finds no `02:45`/`03:30` constant). The 07:00 minute is `DEADMAN_HOUR/MINUTE` (`run_night.py:48-49`).
- **stand-down** — the driving session ending, by its own choice or by being killed, so that the census is empty at t0.
- **lock** — `~/night-custody/magistrate/magistrate.lock`, a JSON file `{supervisor_pid, child_pid, child_pgid, epoch_s, session_id}`; "live" means the supervisor pid answers `kill -0` — the exact predicate the courier lock already uses (`run_night.py:670-694`).

---

## 1. Topology — recommend ONE calendar/interval-driven poller that forks a per-launch supervisor

**Recommendation: a `StartInterval` 300 s user LaunchAgent (`com.joulewise.magistrate`) running `scripts/magistrate_watchdog.py poll`.** Each firing is stateless in the launchd sense: read inputs, decide, at most one action, exit within seconds. When the decision is LAUNCH, the poller forks a **supervisor** (same script, `supervise` subcommand) into its own session (`setsid`), and the supervisor spawns `claude -p …`, waits on it, enforces the stand-down kill and hang kill, and writes the exit record. The supervisor survives the poller's exit because launchd only reaps "remaining processes with the same process group ID as the job" (`man launchd.plist`, AbandonProcessGroup **[bench]**) and a `setsid` child has a new group — the same mechanism the night driver already relies on for its courier (`subprocess.Popen(..., start_new_session=True)`, `run_night.py:756-759`; proven 09-02: the driver returned at 02:57:27 and the courier kept writing until 03:03, audit §2 item 1).

Why this shape:
- The census must be re-evaluated at every decision, and the only thing that can re-evaluate it after every kind of death (session crash, usage-limit exit, watchdog crash) is a timer that fires regardless of prior state. That is D-127 §4's "independent launchd fallback timer as the second wake layer" applied to the loop itself (audit §6 item 3).
- `StartInterval` misses a firing while the job is still running (`man launchd.plist` StartInterval) — harmless because the poll exits in seconds; the long-lived part is the forked supervisor, which launchd does not count as the job.
- No `KeepAlive`: the night installer refuses templates containing it (`install_night_agent.sh:35-38`); the same convention keeps the watchdog from being restarted by launchd in a loop.
- The poller's argv (`/usr/bin/env python3 …/magistrate_watchdog.py poll`) contains none of `codex`, `claude`, `t3`, so it can never be a census hit for the NIGHT driver's census, which runs in a different process tree. **The `claude` binary path therefore must never appear in the watchdog's argv** — it goes in a plist `EnvironmentVariables` entry or is resolved inside the script (env is invisible to `pgrep -f`).

Rejected 1 — **`WatchPaths` (e.g. on `courier.sent`)**: the man page itself says modifications "can be missed" and event monitoring is "highly race-prone" (**[bench]** `man launchd.plist` WatchPaths). Failure modes: (a) a missed event = no relaunch until a human; (b) a usage-limit exit produces no filesystem event at all, so backoff/retry has no trigger; (c) `courier.sent` is per-night, so a watch list must be rewritten at every arm — one more HEAD-pinned artifact of the kind that already bit the uninstall path (audit F9).

Rejected 2 — **extending the courier baton**: the courier is a single-turn `claude -p` with six tools (`run_night.py:52-54`, `:610-631`) whose prompt ends "Continue with the handback's next lane under the standing loop rules" (`NIGHT_COURIER_PROMPT.md:19`). Failure modes: (a) no wake source if it dies after `courier.sent` — the driver unlinks the lock and returns without tracking it (`run_night.py:812-814`; audit F3); (b) it arms night N+1 alone, which is a rule-11 "window commitment" by a lieutenant-class actor with no gate (audit §2, B10); (c) a courier that fails 4 times leaves the loop dead with no email (audit §3 row 1). Keep the courier exactly as it is for the night email; do not make it the loop.

Considered and parked — **`claude --bg`** (**[bench]** `claude --help`: "Start the session in the background and return immediately… `claude attach`, `logs`, `stop`, `rm`"; `claude respawn` restarts a background session "so it runs the current Claude Code version"). This is structurally the better vehicle for a persistent `/loop` (ScheduleWakeup is "session-scoped" — binary string at `strings` line 231335, **[bench]**) and it has a built-in answer to binary updates. Whether it starts from launchd with no TTY, how a first prompt is delivered, and whether it honours `--allowedTools` are **[not executed]**. Design below uses `-p`; §6 names one bench experiment to promote `--bg` if it works.

## 2. State machine

### Inputs (all read fresh at every poll; nothing cached across polls except `state.json`)

| # | Input | Source | Read how |
|---|---|---|---|
| I1 | plans | `/Users/edr/night-custody/*/night_plan.json` | parse with `night_gate.NightPlan.from_mapping` (`night_gate.py:182`); keep plans with `now − 36 h < t0 < now + 48 h` (36 h = `PLAN_MAX_AGE_S`, `night_gate.py:50`) |
| I2 | night records | `<custody_root>/night/{chain.started, chain.exited, courier.sent}` | existence; `chain.started` holds `pgid` (`run_night.py:360-368`, `_read_started_pgid :1290`) |
| I3 | census | `night_gate.agent_census(run_night.make_probes())` (`run_night.py:267`) | import the production predicate; never re-spell it (R-3) |
| I4 | clock | `time.time()` and `datetime.now()` local | same clock as the gate's `_clock_value(probes, "epoch")` (`night_gate.py:553`) |
| I5 | stop switch | (a) remote: `git ls-remote --exit-code https://github.com/mpmdw/JouleWise.git refs/heads/magistrate-stop` → exit 0 = STOP (**[bench]** anonymous HTTPS works, exit 2 when absent); (b) local: `~/night-custody/magistrate/STOP` exists | 20 s timeout on (a); a network failure is "unknown", logged, treated as NOT stopped (D-161: the only adversary here is Ed's own network) |
| I6 | lock | `~/night-custody/magistrate/magistrate.lock` | live iff `supervisor_pid` answers `kill -0`; a dead supervisor with a live `child_pid` is the ORPHAN case |
| I7 | last exit | `~/night-custody/magistrate/exit.json` (written by the supervisor) | `{exit_code, class, reason, epoch_s, launch_epoch_s}` |
| I8 | state | `~/night-custody/magistrate/state.json` | `{state, since_epoch_s, next_eligible_epoch_s, consecutive_failures, owed_notices: [...]}`; unparsable → renamed `state.json.corrupt-<epoch>`, treated as IDLE |
| I9 | canonical HEAD | `git -C /Users/edr/code/JouleWise rev-parse HEAD` | compared to each armed plan's `repo_head` → `head_matches_plan` (informational; the gate refuses `night_plan_stale` on mismatch, `night_gate.py:599-609`) |

### States

`IDLE` · `RUNNING` (lock live) · `ORPHAN` (child alive, supervisor dead) · `HELD_FENCE` (fixed fence or a night span open, or `chain.started` without `chain.exited`) · `HELD_STOP` (I5) · `HELD_CENSUS` (census non-empty with no lock — something else is alive; e.g. Ed's own session, a leftover shell) · `BACKOFF` (`now < next_eligible_epoch_s`).

### Transitions (evaluated top to bottom at each poll; first match wins)

```
1. stop switch set (I5)
     lock live      → SIGTERM child pgid; supervisor does the rest → state HELD_STOP, notice "stopped_by_ed"
     no lock        → state HELD_STOP (no launch)
2. lock live (I6)                                   → state RUNNING (no action; supervisor owns the child)
3. lock dead, child_pid alive                      → fork `supervise --adopt <child_pid> <pgid>` → state RUNNING, notice "supervisor_adopted"
4. lock dead, child dead                            → unlink lock (stale); fall through
5. fixed fence, or any plan span open, or chain.started w/o chain.exited
                                                    → state HELD_FENCE (no launch)
6. census non-empty                                 → state HELD_CENSUS (no launch); log the first 20 lines
7. now < next_eligible_epoch_s                      → state BACKOFF (no launch)
8. otherwise                                        → LAUNCH: write standdown.json, fork supervisor,
                                                       write lock, append launches.jsonl, state RUNNING
```

The census is checked AFTER the fence so that a poll inside a night span never even runs `pgrep` concurrently with the driver's 30-s census loop (`CENSUS_INTERVAL_S = 30`, `run_night.py:43`) — pgrep is read-only, so this is tidiness, not correctness; the correctness argument against racing the gate is the 30-min margin: no launch decision is taken inside `[t0−30 min, span end]`, and the ≤ 300 s poll period plus a ≤ 60 s launch means the last possible launch is at t0 − 30 min − 0 s and the stand-down kill at t0 − 30 min happens in the supervisor, not in a poll.

### Every write the mechanism makes (all under `~/night-custody/magistrate/`, outside the repo)

| Writer | File | When |
|---|---|---|
| poller | `state.json` | every poll (atomic rename) |
| poller | `watchdog.log` | one line per poll: state, reason, next eligible |
| poller | `standdown.json` | at launch and refreshed every poll while RUNNING: `{armed_plans:[{plan_id,t0,standdown_epoch,span_end,head_matches_plan}], stop:bool, launch_epoch_s, owed_notices}` — the session's only view of the schedule |
| poller | `magistrate.lock` | at launch (O_EXCL, same pattern as `_acquire_courier_lock`, `run_night.py:703-716`) |
| poller | `launches.jsonl` | append `{event:"launch", epoch, binary_realpath, session_id, prev_exit_class}` |
| supervisor | `launch-<epoch>.out`, `.err` | child's stdio (stream-json lines) |
| supervisor | `launches.jsonl` | append `standdown_sigterm`, `standdown_sigkill`, `hang_kill`, `residual_kill {pids}`, `exit` |
| supervisor | `exit.json` | at child exit: `{exit_code, class, reason, duration_s, forced:bool}`; then unlink lock |
| session (via prompt) | `magistrate.heartbeat` | first act, then every loop iteration (liveness proof, D-127 §4) |
| session | `unsent-<epoch>.md` | only if Gmail MCP is unavailable |
| nothing | the repo, plans, night custody records | the watchdog never touches them |

### Where the stand-down lives — recommend: authoritative in the supervisor (SIGTERM at t0−30 min), cooperative in the session (exit by t0−40 min)

- Authoritative = supervisor, because (a) rule 11's stated reason: stopping is the one judgment the loop-immersed agent demonstrably cannot make from inside, so the kill must sit outside it; (b) it is mechanical and bench-testable with a stand-in child (§6); (c) whether `ScheduleWakeup` fires at all in a `-p` session is **[not executed]**, so a self-check that depends on it cannot be the only layer (D-127 §4: "never one mechanism").
- Cooperative = the prompt (§3) tells the session to re-read `standdown.json` every iteration and, with < 40 min left, to commit, push, email "standing down", `ScheduleWakeup stop` (the loop-end call R-9 names; **[bench]** the tool's description in the binary: "To end the loop, call this tool with `stop: true`"), and exit. A cooperative exit lands in `[t0−60, t0−30]` and is classified `ok_standdown`; the supervisor then has nothing to kill.
- Supervisor kill sequence at `standdown_epoch = min(t0) − 1800 s` over all armed plans (re-read from disk every 60 s — a plan can be authored AFTER launch, by this very session): `killpg(child_pgid, SIGTERM)`; wait 120 s; `killpg(SIGKILL)`; then run the census once and, for each remaining hit that is a known family — argv basename `claude` or `codex`, `codex mcp-server`, or a `/bin/zsh -c source ~/.claude/shell-snapshots/…` shell (audit F5 shows these are the real residue) — SIGTERM then SIGKILL after 10 s; anything else matching only on a substring (a `t3` path, an unrelated app) is logged, not killed, and left to the gate. Record `forced: true` if the SIGTERM path ran at all. The census cleanup step is explicitly the operator's instruction (Ed 09-02: the magistrate MAY kill its own session and codex children) — D-161 says not to defend against Ed, and this is the opposite: doing what Ed asked.

## 3. The launch command, the prompt, and the cadence question

### Binary resolution (in the supervisor, never in argv)
`~/.local/bin/claude` → `os.path.realpath` (**[bench]** today `…/versions/2.1.259`); if the symlink dangles, the newest `~/.local/share/claude/versions/*` that is a regular executable file; record the realpath in `launches.jsonl`. This is audit §6 item 5 applied to the magistrate; the night plists still pin a version string (**[bench]** both plists carry `--courier-bin …/versions/2.1.259`) — that stays the night installer's problem.

### Command (built by the supervisor; `<>` are substitutions)

```
<realpath of ~/.local/bin/claude> -p "<prompt below, rendered>" \
  --model fable --effort high \
  --output-format stream-json --verbose \
  --permission-mode auto --permission-prompts none \
  --allowedTools "Read,Glob,Grep,Bash,Edit,Write,Agent,WebFetch,WebSearch,ScheduleWakeup,mcp__claude_ai_Gmail__send_message,mcp__codex__codex,mcp__codex__codex-reply" \
  --disallowedTools "Bash(launchctl *),Bash(sudo *),Bash(git push --force*)" \
  --name magistrate-<launch_epoch> --session-id <uuid4>
cwd = /Users/edr/code/JouleWise ; env PATH=/Users/edr/.local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin
stdout → launch-<epoch>.out ; stderr → launch-<epoch>.err ; start_new_session=True
```
Flag facts **[bench]** from `claude -p --help`: `--model` accepts the alias `fable`; `--effort` levels include `high`; `--output-format stream-json` is `--print`-only; `--permission-prompts none` = "anything that would prompt is denied automatically; the permission mode still decides everything else" (so nothing can hang waiting for a human); `--allowedTools`/`--disallowedTools` take comma lists with `Bash(pattern)` forms; `-n/--name` and `--session-id <uuid>` exist (the id lets a human `claude --resume <id>` later); `--fallback-model` exists but is NOT used — an Opus fallback would seat a lieutenant as magistrate silently (rule 11). Whether `stream-json` needs `--verbose` in 2.1.259 is **[not executed]**; the courier's known-good shape is `-p <prompt> --output-format text --allowedTools <list>` (`run_night.py:622-630`), so the first rehearsal should fall back to that if stream-json misbehaves. `--permission-mode auto` matches `~/.claude/settings.json` `defaultMode: auto` (**[bench]**); the courier passes no mode and still edited, pushed and emailed on 09-02 (handback :40-42), so `auto` + explicit `--allowedTools` is a superset of a proven shape. The `mcp__claude_ai_Gmail__send_message` tool is the courier's own route (`run_night.py:52-54`) and is proven under launchd (message id `1a0618d143537010`, `NIGHT_HANDBACK.md:41`).

### Prompt (`docs/process/MAGISTRATE_RELAUNCH_PROMPT.md`, rendered by the supervisor; 22 lines)

```
You are the JouleWise magistrate (Fable), relaunched headless by com.joulewise.magistrate at {launch_iso} (launch #{n}; previous session ended: {prev_exit_class} — {prev_exit_reason}). Ed is away; nobody is at the machine. CLAUDE.local.md rules 1–11 bind.
First act, before reading anything else: write {home}/magistrate.heartbeat containing your pid and `date +%s`. Then read {home}/standdown.json: it names every armed plan, its t0, YOUR STAND-DOWN EPOCH (t0 − 30 min), whether the canonical checkout HEAD still equals the plan's repo_head, the stop-switch state, and the notices owed to Ed.
Second act: email Ed (claude.ai.copper531@passmail.net) in plain words, one message: that you relaunched, why the last session ended, every owed notice, and what you will do until stand-down. If mcp__claude_ai_Gmail__send_message is unavailable, write the same text to {home}/unsent-{launch_epoch}.md and continue.
Resume the standing mandate from the repo alone: RUN_STATE.md's top entry, the durable pause file it points to (git fetch and read the branch it names if the file is not on main), then docs/process/NIGHT_HANDBACK.md. Never read another session's scratchpad.
Work the pause file's lanes in its order under /loop, self-paced. Commit and push every completed step; leave nothing unpushed for more than one step.
Work in linked worktrees. While standdown.json lists an armed plan, do not pull, checkout, reset or commit in /Users/edr/code/JouleWise: the night gate refuses night_plan_stale when that checkout's HEAD differs from the plan's repo_head. If head_matches_plan is false, the night WILL refuse; re-arm only by the NIGHT_HANDBACK procedure and say so in your email.
A dirty tree you did not create is evidence: commit it to wip/relaunch-{launch_epoch} and report it; never reset or checkout over it.
Re-read {home}/standdown.json at every loop iteration and touch {home}/magistrate.heartbeat. When fewer than 40 minutes remain to the stand-down epoch: finish the current step, commit, push, update RUN_STATE.md's top pointer, email Ed "standing down for {plan_id} at {t0_iso}", end the loop with ScheduleWakeup stop:true, and exit. The supervisor kills you at the stand-down epoch regardless; being killed mid-step is a defect you report at the next launch.
If standdown.json.stop is true or {home}/STOP exists: commit, push, email "stopped by Ed", exit.
Before you exit for any reason: end every codex session and every run_in_background shell you started; the next night's census must find nothing of yours.
Waits longer than two minutes go through ScheduleWakeup, never a sleeping shell. Never touch launchd, plists, sudoers, or the night custody records except through the handback procedure. Never merge or arm a night without the gate shape your rules require.
```

### Cadence in a headless session
`ScheduleWakeup` exists as a tool (**[bench]** binary strings: `tools:ScheduleWakeup`; description "Schedule when to resume work in /loop dynamic mode"; "Session-scoped cron tasks (CronCreate, ScheduleWakeup, /loop) that will wake this session later"). Whether a `-p` process stays alive to be woken after its turn ends is **[not executed]** — the help text says `-p` "Print response and exit". Design assumption: **it does not**, and the fallback the brief names is the base design: a `-p` session is ONE loop iteration (which may still run for hours across many tool calls); when it exits `ok`, the poller relaunches after one cool-off poll (300 s) whenever the census is empty and no lock is held. The cadence of the loop is therefore `max(session length, 300 s)`, and the prompt's "re-read standdown.json every iteration" degrades gracefully to "once per launch" — the supervisor's kill covers the rest. If the first rehearsal shows `ScheduleWakeup` firing inside `-p` (observable: stream-json events after a scheduled wake in `launch-<epoch>.out`), nothing in the design changes; the session simply lasts longer.

## 4. Usage-limit behaviour and backoff

Facts: the account is subscription-bound with a 5-hour window (memory; the T30 pause entry in `RUN_STATE.md:13` says "usage window exhausted"). The exact error text a `-p` session prints on exhaustion is **[not executed]**; the classifier below is regex-based and conservative.

Supervisor exit classification, from the exit code plus the last `result` event / last 2 KB of stderr:

| class | signature | next_eligible | consecutive counter |
|---|---|---|---|
| `ok` | exit 0, result without `is_error` | now + 300 s | reset |
| `ok_standdown` | exit within `[t0−60 min, t0−30 min]` | span end (poller holds anyway) | reset |
| `usage_limit` | `is_error` and /usage limit|rate limit|resets? (at|in)|quota/i | the parsed reset time if present, else now + 60 min; while the class repeats, stay at 60 min (the window resets on a fixed clock; polling faster cannot help, and each failed launch costs one ~10 s process) | +1 |
| `auth` | /not logged in|oauth|token expired|401/i | now + 6 h; notice owed | +1 |
| `binary_missing` | spawn ENOENT / exit 127 | now + 60 min; re-resolve next poll | +1 |
| `hang_killed` | supervisor killed for silence | now + 300 s; after 3 consecutive → 60 min | +1 |
| `killed_standdown` / `stopped_by_ed` | supervisor/stop path | span end / until stop clears | reset |
| `other_error` | anything else | 15 → 30 → 60 min (cap) | +1 |

Machine cost bound: worst case one failed `claude` process per hour; no busy loop is possible because the poller runs at most every 300 s and launches at most once per poll.

Email discipline — **one notice per state transition, delivered at the next opportunity, never per attempt**: the poller appends a transition to `state.json.owed_notices` only when `class` changes (RUNNING→BACKOFF(usage_limit) once, not on each of the six hourly retries; BACKOFF→RUNNING once). The watchdog itself cannot email — it is not a Claude session and there is no other outbound route on this machine (GitHub notifications do not fire for your own commits/issues, and Ed can only receive email). So the notices ride in the NEXT successful session's first email ("relaunched 06:10 after usage-limit backoff since 01:05, 5 attempts") and, as a floor, the night courier's email keeps arriving independently every night. This is honest about the one gap: during a long backoff Ed hears nothing until it clears. Optional (not recommended for v1, D-161): mirror `state.json` to a pushed single-file branch `magistrate-status` so Ed can *pull* the state from a phone.

## 5. Failure table

| Scenario | Detection | Containment | Who hears |
|---|---|---|---|
| Watchdog poll crashes (traceback, bad `state.json`) | launchd re-fires in 300 s; traceback in `launchd.magistrate.err`; corrupt state renamed and treated as IDLE; the session's prompt reports `watchdog.log` age > 15 min in its email | each poll is independent; a persistently crashing poll launches nothing — the night driver and courier are unaffected (separate agents) | relaunch email if a launch still happens; otherwise only the nightly courier email and the ABSENCE of relaunch emails |
| Supervisor dies, child lives | poll step 3: lock supervisor pid dead, child pid alive | fork `supervise --adopt` (polls `kill -0` on the child instead of `waitpid`, kills by pgid at stand-down) | next relaunch email ("supervisor_adopted") |
| Session hangs forever | supervisor: no new byte on `launch-<epoch>.out` AND `magistrate.heartbeat` older than 60 min | SIGTERM, 120 s, SIGKILL; class `hang_killed`; 3 in a row → 60-min backoff (same-signature rule) | next relaunch email |
| Session exits mid-fix, dirty worktree | prompt's opening `git status`/`git worktree list`; `exit.json` class ≠ ok_standdown | watchdog never touches git; prompt: commit to `wip/relaunch-<epoch>`, never reset/checkout (near-loss 2026-09-01 memory); note the gate does not check cleanliness, only HEAD (`night_gate.py:599-609`) | relaunch email |
| Two magistrates alive | impossible by construction from the watchdog: O_EXCL lock AND census-empty precondition; a second `claude` (Ed's own, remote) makes the census non-empty → HELD_CENSUS, no launch | none needed; log the census lines | `watchdog.log`; the night refuses `night_refused_agent_present` if it persists (R-3) |
| Clock skew / network time toggled off in windows (D-127 §3) | none needed for the watchdog: it uses the same wall clock as the gate (`night_gate.py:553`) so both shift together; 30-min margin ≫ any drift; a backward jump making `since_epoch_s` future-dated → log and treat as IDLE | fixed fence + span margins; the gate's own C4 boot/clock check (`ORDER`, `night_gate.py:90-100`) still guards the night | gate refusal email via courier if the clock is really wrong |
| `claude` auto-update moves the binary (hit the courier 09-02) | supervisor resolves `~/.local/bin/claude` at EVERY launch, records realpath; ENOENT → `binary_missing` | never pin a version in the plist; a running session keeps its already-open old binary; `claude respawn` exists for `--bg` sessions (**[bench]**) | next relaunch email lists the binary path change |
| Gmail MCP unavailable in the session (observed this session: the Gmail MCP server disconnected mid-run) | prompt: write `unsent-<epoch>.md` | courier prompt gets one line: "send any `~/night-custody/magistrate/unsent-*.md` and delete them" | courier email next morning |
| Plan authored after launch (the session arms tonight's night) | supervisor re-reads plans every 60 s | stand-down epoch recomputed; `standdown.json` refreshed each poll so the session sees it | — |
| Chain overruns `window_max_s` (audit F2, unbounded today) | `chain.started` without `chain.exited` → HELD_FENCE regardless of span end | no launch until the chain exits (fail-closed: this is the physics fence) | courier/dead-man path; the watchdog only waits |
| Residual shells after a forced kill (audit F5: `~/.claude/shell-snapshots` argv matches `claude`) | supervisor's post-kill census | kill known families only; log the rest | `launches.jsonl` `residual_kill`; relaunch email |
| Stop switch set while running | poll step 1 | SIGTERM child pgid; class `stopped_by_ed`; no relaunch until the branch is deleted / file removed | session emails "stopped by Ed" if it gets the cooperative window; otherwise silence is the intended outcome |

## 6. Test plan (bench, no real night)

CLI affordances for testing (all in `magistrate_watchdog.py`): `--home DIR` (default `~/night-custody/magistrate`), `--custody-glob` (default `/Users/edr/night-custody/*/night_plan.json`), `--now EPOCH` (pinned clock), `--census-cmd` (override argv; default the production tuple), `--stop-url` (default the HTTPS ls-remote; `none` to skip), `--child-cmd` (stand-in for the claude command; the default is the real one), `--dry-run` (print the decision, write nothing). Unit tests inject probes exactly as `tests/test_run_night.py` does (`_probe`, `_green_results`, `tests/test_run_night.py:27-40`), `unittest` style, pinned clock (the 09-02 audit's "unpinned clock, red on any UTC runner" blocker applies).

`tests/test_magistrate_watchdog.py`:
1. `test_fixed_fence_boundaries` — 02:44:59 launchable, 02:45:00 held, 03:29:59 held, 03:30:00 not held by fence, 07:00:30 held, 07:01:00 not.
2. `test_plan_span_holds_and_courier_sent_closes_early` — t0−1801 launchable; t0−1800 held; t0+window+2700 held; with `courier.sent` present at t0+window+400 → launchable (fence permitting).
3. `test_chain_started_without_exited_holds_past_span_end`.
4. `test_ignores_plans_older_than_36h_or_beyond_48h`.
5. `test_stop_switch_remote_branch` (fake ls-remote exit 0 → HELD_STOP; with live lock → SIGTERM sent to the recorded pgid — assert on a spawned `sleep` group).
6. `test_stop_switch_local_file`; `test_stop_check_network_failure_is_not_stop`.
7. `test_census_nonempty_blocks_launch` (probe returns one line, exit 0).
8. `test_live_lock_blocks_launch`; `test_stale_lock_reaped`; `test_orphan_child_adopted`.
9. `test_argv_has_no_census_words` — assert none of `codex|claude|t3` in the poller's and supervisor's argv; the child's argv may contain them.
10. `test_launch_writes_lock_standdown_launch_record` (and `head_matches_plan` computed against a fake HEAD).
11. `test_supervisor_standdown_sigterm_then_sigkill` — stand-in child `python3 -c "signal.signal(SIGTERM, SIG_IGN); sleep"`; assert SIGKILL after grace, `exit.json.forced == True`, lock unlinked.
12. `test_supervisor_hang_kill_on_silence_and_stale_heartbeat`.
13. `test_exit_classification_table` — one case per row of §4, including the reset-time parse.
14. `test_backoff_schedule_and_single_notice_per_transition`.
15. `test_binary_resolution_symlink_then_newest_version` (tmp dirs).
16. `test_render_plist_no_keepalive_startinterval_path_env` — reuse the `plistlib` style already imported in `test_run_night.py:9`.
17. `test_supervisor_rereads_plans_after_launch` (plan appears at +60 s; stand-down epoch moves).

The ONE end-to-end rehearsal (≈50 min, no Claude launched): tmp home, `--child-cmd "python3 -c 'import time; time.sleep(7200)'"`, fake plan with `t0 = now + 35 min`, `--stop-url none`, real census. Run `poll` by hand every minute (or bootstrap the plist with `--home` pointed at the tmp dir): T−35 → LAUNCH (stand-in running, lock live); T−30 → supervisor SIGTERMs, `exit.json` class `killed_standdown`; T−29 poll → HELD_FENCE; touch `courier.sent` at T+5 → next poll LAUNCH again; create `STOP` → SIGTERM → HELD_STOP; remove `STOP` → LAUNCH. Read `launches.jsonl` end to end. The real-Claude proof is then tonight's already-armed `REHEARSAL_STUB` (`rehearsal-20260903`, t0 02:56): install the plist, have the standing session stand down cooperatively at 02:16 (T−40), and read three observables at 07:30: `launches.jsonl` (standdown → relaunch after `courier.sent`), the 02:56 census record in `night/censuses.jsonl` EMPTY (the first ever C3 pass), and the relaunch email. One extra bench experiment worth 10 minutes: `claude --bg "<prompt>"` from a `launchctl submit`-free shell with stdin closed, to see whether `--bg` works without a TTY [not executed]; if it does, the supervisor's child becomes `--bg` + `claude logs` polling and the loop cadence question disappears.

## 7. Minimal file list and estimate

| File | Purpose | Sol-hours |
|---|---|---|
| `scripts/magistrate_watchdog.py` | `poll`, `supervise [--adopt]`, `render`, `self-test`; ~450 lines; imports `night_gate.agent_census`, `run_night.make_probes/_pid_is_live/_json_bytes` | 5 |
| `configs/launchd/com.joulewise.magistrate.plist.template` | below | 0.5 |
| `scripts/install_magistrate_agent.sh` | render + `bootstrap`/`bootout` `gui/$(id -u)`, `--uninstall`, `--render-only`; NO `repo_head` check (this agent is not per-night) | 1 |
| `docs/process/MAGISTRATE_RELAUNCH_PROMPT.md` | the §3 prompt, templated like `NIGHT_COURIER_PROMPT.md` | 0.5 |
| `tests/test_magistrate_watchdog.py` | §6 items 1–17 | 4 |
| `docs/process/MAGISTRATE_WATCHDOG.md` | mechanism doc to the replication bar (inputs, states, every write, the kill sequence, the failure table) | 1.5 |
| `docs/process/NIGHT_COURIER_PROMPT.md` | +1 line (send `unsent-*.md`) | 0.1 |
| `docs/decision_log.md` | D-171 "magistrate relaunch watchdog" — process rule, via cold gate, Ed approves install by email | lead |
| Total | | ≈ 12.5 Sol-hours + ~2 lead-hours (review, bench rehearsal, install email) |

Plist skeleton (`@@` rendered by the installer):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>com.joulewise.magistrate</string>
  <key>ProgramArguments</key><array>
    <string>/usr/bin/env</string><string>python3</string>
    <string>@@REPO@@/scripts/magistrate_watchdog.py</string><string>poll</string>
  </array>
  <key>WorkingDirectory</key><string>@@REPO@@</string>
  <key>EnvironmentVariables</key><dict>
    <key>PATH</key><string>/Users/edr/.local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
    <key>JW_MAGISTRATE_HOME</key><string>/Users/edr/night-custody/magistrate</string>
    <key>JW_MAGISTRATE_CWD</key><string>/Users/edr/code/JouleWise</string>
  </dict>
  <key>StartInterval</key><integer>300</integer>
  <key>RunAtLoad</key><false/>
  <key>StandardOutPath</key><string>/Users/edr/night-custody/magistrate/launchd.magistrate.out</string>
  <key>StandardErrorPath</key><string>/Users/edr/night-custody/magistrate/launchd.magistrate.err</string>
</dict></plist>
```
(No `KeepAlive`; no `claude` path anywhere in `ProgramArguments`; `/opt/homebrew/bin` present so `gh`, `jq`, `codex`, `node` resolve inside the session — audit F11.)

Python skeleton (structure only; every function is named so the tests above have a target):

```python
#!/usr/bin/env python3
"""com.joulewise.magistrate: poll → (launch|hold), supervise → (wait|kill), never touch the repo."""
import argparse, json, os, signal, subprocess, sys, time, uuid
from datetime import datetime, timedelta
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from joulewise.night_gate import NightPlan, agent_census
from scripts.run_night import make_probes, _pid_is_live, _json_bytes, COURIER_DEADLINE_S

STANDDOWN_S = 1800; COURIER_SLACK_S = 2400; POLL_S = 300
FENCE = ((2, 45), (3, 30)); DEADMAN_MINUTE = (7, 0)
STOP_URL = "https://github.com/mpmdw/JouleWise.git"; STOP_REF = "refs/heads/magistrate-stop"
KILL_FAMILIES = ("claude", "codex", "/.claude/shell-snapshots/")

def load_plans(glob, now): ...            # NightPlan.from_mapping; keep now-36h < t0 < now+48h
def span(plan): ...                       # (t0-STANDDOWN_S, t0+window_max_s+COURIER_DEADLINE_S+COURIER_SLACK_S)
def night_over(plan): ...                 # (custody/night/courier.sent).exists()
def chain_open(plan): ...                 # chain.started exists and not chain.exited
def in_fixed_fence(local_dt): ...
def stop_requested(home, url): ...        # local STOP file or `git ls-remote --exit-code url STOP_REF` == 0; timeout 20 s
def lock_state(home): ...                 # None | ("live", rec) | ("orphan", rec) | ("stale", rec)
def census_empty(probes): ...             # agent_census(probes)[1] is None
def resolve_binary(): ...                 # realpath(~/.local/bin/claude) or newest versions/* executable
def head_matches(plan, repo): ...         # git rev-parse HEAD == plan.repo_head
def decide(inputs) -> Decision: ...       # the ordered rules of §2; pure, unit-testable
def write_standdown(home, plans, stop, notices): ...
def launch(home, plans, binary, cwd, child_cmd=None): ...   # fork+setsid supervisor; O_EXCL lock; launches.jsonl
def poll(args): ...                       # gather inputs → decide → act once → state.json + watchdog.log
def render_prompt(home, launch_epoch, n, prev): ...         # MAGISTRATE_RELAUNCH_PROMPT.md substitutions
def child_argv(binary, prompt): ...       # §3 flag list
def supervise(args): ...                  # spawn child (start_new_session), loop 60 s: re-read plans, standdown kill,
                                          # hang kill (out mtime + heartbeat), stop kill; on exit classify → exit.json; unlink lock
def classify(exit_code, out_tail, err_tail, t0s, launched_at, killed_reason) -> (cls, reason): ...
def residual_kill(probes, keep_pids): ... # known families only; log others
def render_plist(template, out, repo, home): ...
def self_test(args): ...                  # dry-run decide() against live inputs; prints the decision
```

## 8. Pushback on the constraints

1. **"Email Ed at each stand-down" cannot be guaranteed on the forced path.** The watchdog is not a Claude session; the only outbound routes are a Claude session's Gmail MCP (the courier's route, `run_night.py:52-54`) and GitHub, which does not notify you of your own actions. A forced stand-down (SIGTERM) therefore produces no email at that moment unless an agent is launched inside the span, which the constraints forbid. Recommend accepting: cooperative stand-downs email themselves (T−40); forced ones are reported in the next relaunch email and are visible in the courier's morning email if one line is added to the courier prompt. Alternative if Ed insists: permit one ≤ 120 s `-p` emailer at T−30, killed unconditionally by T−25 — I would not build it (D-161: gold-plating against a gap Ed will see six hours later anyway).
2. **"Gmail MCP from inside the relaunched session vs the courier's route" is a false choice** — they are the same mechanism (the courier IS a `claude -p` session using `mcp__claude_ai_Gmail__send_message`). Use the relaunched session because it alone knows the state to report; there is no third route. The Gmail MCP disconnected during this very consult session, so the prompt's `unsent-<epoch>.md` fallback is not theoretical.
3. **The fixed 02:45–03:30 fence is a number nobody owns in code.** It is derived from tonight's 02:56 t0, which is a plan value, not a constant. Keep it in the watchdog as a config constant with the brief as its citation, and let the plan span be the real fence; when a plan is armed at another hour the fixed fence is simply irrelevant, and when NO plan is on disk the fixed fence is the only thing protecting a night nobody recorded — which is exactly the case the gate would refuse anyway. It is cheap, so keep it, but say in the doc that the span is the mechanism and the fence is a belt.
4. **"Resume from the repo alone (RUN_STATE.md pointer + the durable pause file)" is not satisfiable on main today.** `RUN_STATE.md:13-16` points at `docs/process_traces/2026-09-02-decode-identity-set/39-pause-state-2026-09-02.md` "on branch fix/2026-09-02-decode-identity-set"; **[bench]** that file does not exist on main and exists only in `JouleWise-wt-decode-id` (branch head fc52bda6, pushed). The prompt therefore says "fetch and read the branch the pointer names". Better: pause files land on main — but any commit to the canonical checkout while a plan is armed makes the night refuse `night_plan_stale` (`night_gate.py:599-609`; audit F1/B7; the handback's own warning `NIGHT_HANDBACK.md:65-70`). This is the same conflict as item 5 and has the same cure.
5. **Installing the watchdog itself moves HEAD and stales tonight's plan.** The plist points at `/Users/edr/code/JouleWise/scripts/magistrate_watchdog.py`; landing that file on main after the 20:16 re-arm changes HEAD from 33290b8b and the gate refuses. Either re-arm once more after landing (the handback procedure, done once today already) or — the structural fix the audit's item 1 already names — pin plans to the measurement checkout, not the dev tree. I would push for the latter as a cold-gate item alongside this design: it removes the daytime-merge trap from the magistrate's whole working day, not just from the install.
6. **The census predicate is too loose for a relaunching magistrate** (audit F5: any `run_in_background` shell matches `claude` on the snapshot path; `t3` matches any argv containing those two characters). The watchdog inherits it by design (R-3, "same census the gate uses") and copes with the residual-kill step; but the right fix is the ruled change to process identity across `night_gate.py:34` and `arm_readiness_evidence_t0.py:1312` (audit §6 item 4). Until then, expect HELD_CENSUS holds caused by nothing but leftovers, and expect the 07:00 minute of the fence to be the only reason the watchdog never tries to launch while the dead-man's courier lock is fresh (`COURIER_LOCK_FRESH_S`, `run_night.py:47`).
7. **`-p` as the base is a cadence compromise.** If `--bg` works headless, it is a persistent session with `/loop`, `attach` for a human, and `respawn` for binary updates — three of this design's harder problems solved by the product. Spend ten bench minutes on it before Sol builds the supervisor's hang detector around stream-json.
8. **Kill-switch path.** The brief asks for "the cheapest remote-actionable path"; it is a GitHub BRANCH named `magistrate-stop` (create from the repository's branch dropdown on a phone; delete it to re-arm), read by anonymous HTTPS `git ls-remote` every poll — no auth, no agent, no checkout, no email parsing (**[bench]** exit 2 today). An email-based switch would need a Claude session to read Gmail every poll: a launch inside the fence just to check whether to launch.

---

## Executed evidence (this session, read-only; commands and pasted outputs)

- `claude --version` → `2.1.259 (Claude Code)`; `which -a claude` → `/Users/edr/.local/bin/claude -> /Users/edr/.local/share/claude/versions/2.1.259` (symlink dated Sep 2 19:51); `ls ~/.local/share/claude/versions/` → `2.1.251 2.1.252 2.1.259`.
- `claude -p --help` (full text read): flags cited in §3 present verbatim — `--model`, `--effort <low|medium|high|xhigh|max>`, `--output-format <text|json|stream-json>` "(only works with --print)", `--permission-mode <acceptEdits|auto|bypassPermissions|manual|dontAsk|plan>`, `--permission-prompts <host|none>` with the quoted "nobody: anything that would prompt is denied automatically" text, `--allowedTools`, `--disallowedTools`, `--fallback-model` "(only works with --print)", `-n, --name`, `--session-id <uuid>`, `--bg, --background` "Start the session in the background and return immediately. Prints the id that `claude attach`, `logs`, `stop` and `rm` take", `-p, --print` "Print response and exit". `claude --help` Commands: `agents`, `attach <id>`, `logs <id>`, `respawn [id]` ("Restart a background session… so it runs the current Claude Code version"), `stop|kill <id>`.
- `strings -n 6 …/versions/2.1.259 | grep -n -i schedulewakeup` → `191508:tools:ScheduleWakeup`, `192142:ScheduleWakeup`, `193433:ScheduleWakeupInputError`, `231335:Session-scoped cron tasks (CronCreate, ScheduleWakeup, /loop) that will wake this session later. Empty array when none are scheduled.`, `295519: …"Schedule when to resume work in /loop dynamic mode — the user invoked /loop without an interval…"`, `295521: …"To end the loop, call this tool with `stop: true` (omit every other field) — the loop ends immediately and no further wakeups fire."`
- `ls -la ~/Library/LaunchAgents | grep joule` → `com.joulewise.night.plist`, `com.joulewise.night.deadman.plist` (both 20:16 today). Both `ProgramArguments` carry `--courier-bin /Users/edr/.local/share/claude/versions/2.1.259`; night `StartCalendarInterval` 02:56, deadman 07:00; `RunAtLoad false`; no `KeepAlive`; `EnvironmentVariables.PATH = /Users/edr/.local/bin:/usr/bin:/bin:/usr/sbin:/sbin`. `launchctl print gui/501/com.joulewise.night` → `state = not running`, `runs = 0`, `inherited environment = { SSH_AUTH_SOCK => … }`, calendar trigger `Hour 2 Minute 56`. `launchctl list | grep joule` → both loaded, last exit 0.
- `/Users/edr/night-custody/rehearsal-20260903/night_plan.json` → `t0_epoch_s 1788429360` (`date -r` → `Thu Sep 3 02:56:00 PDT 2026`), `window_max_s 900`, `authored_epoch_s 1788405403`, `repo_head 33290b8b…`, `receipt_class REHEARSAL_STUB`. `night.log` (110 bytes) = the 07:00 stand-down line. `rehearsal-20260902/night/censuses.jsonl` → 1 record; its `stdout` has 1136 lines; no line contains `run_night` or `pgrep` (the driver did not see itself); first line is the zsh PR-watcher matching on `~/.claude/shell-snapshots/`.
- Census probe: `python3 -c 'import time; time.sleep(6)' /tmp/x/claude/y --courier-bin /Users/edr/.local/share/claude/versions/2.1.259 &` then `/usr/bin/pgrep -lf "codex|claude|t3"` → the python process IS listed (pid 3121, full argv), plus `1723 claude` (this seat's parent), the codex mcp-server pairs and `codex-code-mode-host`; exit 0. `date` → `Wed Sep 2 20:44:26 PDT 2026`.
- `man launchd.plist` (col -b): `StartInterval` "If the job is running during an interval firing, that interval firing will likewise be missed"; `WatchPaths` "highly discouraged… highly race-prone… entirely possible for modifications to be missed"; `AbandonProcessGroup` "When a job dies, launchd kills any remaining processes with the same process group ID as the job. Setting this key to true disables that behavior."; `RunAtLoad` "should be avoided"; `ThrottleInterval` default 10 s.
- `git -C /Users/edr/code/JouleWise remote -v` → `https://github.com/mpmdw/JouleWise` (fetch/push). `git ls-remote --exit-code https://github.com/mpmdw/JouleWise.git refs/heads/magistrate-stop` → exit 2 (absent); `… refs/heads/main` → `33290b8b…`. `gh auth status` → logged in as mpmdw (keyring).
- `git -C /Users/edr/code/JouleWise worktree list` → 19 worktrees incl. `JouleWise-wt-decode-id fc52bda6 [fix/2026-09-02-decode-identity-set]`; `ls docs/process_traces/2026-09-02-decode-identity-set/39-pause-state-2026-09-02.md` at main → "No such file or directory"; same path in `JouleWise-wt-decode-id` → exists (4818 bytes, Sep 2 16:50); `git status --short` there → clean.
- `~/.claude/settings.json` → `permissions.defaultMode: "auto"`, `model: "fable"`, `effortLevel: "high"`. `.claude/settings.local.json` allow list includes `Bash(launchctl:*)`, `Bash(pkill:*)`, `Bash(gh pr merge:*)`.
- Repo greps: `scripts/night_gate.py` does not exist (the gate is `joulewise/night_gate.py`, 1036 lines); `AGENT_CENSUS_ARGV = ("/usr/bin/pgrep", "-lf", "codex|claude|t3")` at `night_gate.py:34`; `ORDER` at `:90-100`; `PLAN_MAX_AGE_S = 36*60*60` at `:50`; window check `:551-571`, stale checks `:594-609`, census call `:611`; `run_night.py` constants `:43-49` (`CENSUS_INTERVAL_S 30`, `COURIER_DEADLINE_S 300`, `COURIER_BACKOFF_S (60,180,600)`, `COURIER_LOCK_FRESH_S`, `DEADMAN_HOUR 7`, `COURIER_ALLOWED_TOOLS`), `_resolve_courier_bin :571-597`, `_courier_argv :610-631`, lock helpers `:670-716`, `run_courier :718-815`, `dead_man :1301-1322`; `install_night_agent.sh:35-38` KeepAlive refusal, `:40-45` repo_head == HEAD check; `configs/launchd/com.joulewise.night.plist.template` read in full; `state_kernel.json:2492` "the driver did NOT see its own --courier-bin claude argv — bench prediction confirmed (BSD pgrep excludes its ancestors)". No `02:45`/`03:30`/`ScheduleWakeup` constant in `scripts`, `joulewise`, `configs`, `docs/process` (only prose mentions in `NIGHT_HANDBACK.md:30`).
- Not executed: any `claude`/`codex` launch; `--bg` without a TTY; `stream-json`+`--verbose` behaviour; the usage-limit error text; whether `ScheduleWakeup` fires inside `-p`.
