# Design consult — the magistrate relaunch watchdog (`com.joulewise.magistrate`)

Read-only Opus seat, contract lens. Bench: 2026-09-02 20:46–21:05 PDT, worktree
`/Users/edr/code/JouleWise-wt-watchdog-consult` detached at `33290b8b`. Facts
marked **[bench]** were executed this session; every other claim about existing
code carries a `file:line` cite; anything I could not execute is marked
**[not executed]**. No repo file, custody file, plist, or launchctl state was
written. This is design input, not a ruling (rule 11).

---

## 0. Four bench facts that change the design before question 1

**B-1 — `pgrep` does not see its own caller's ancestors. [bench]**
Three experiments, this session:

| experiment | result |
|---|---|
| decoy `python3 … --courier-bin /Users/edr/.local/share/claude/versions/2.1.259` run as a *sibling*, censused from another shell | **matched** (pid 3239) |
| the same argv, but the process runs the census **itself** (`subprocess.run(("/usr/bin/pgrep","-lf","codex\|claude\|t3"))`) | **not in its own output** (pid 3589) |
| census invoked through `/bin/sh -c` so the caller is the *grandparent* | grandparent still **absent** (pid 4009); its two children, one in a new session (`start_new_session=True`) and one in the same session, both **present** |

Confirming case: my own ancestry is `4117 zsh → 1536 claude → 1282 -zsh →
1278 login → 1212 Terminal`; `pgrep -lf "codex|claude|t3"` run from that shell
lists a *different* session (`1723 claude`) but neither `1536` nor `4117`.
[bench]

Consequences, all load-bearing:
1. The night driver is exempt from its own census — which is why the 09-02
   `censuses.jsonl` holds 24 process rows and none of them is `run_night.py`,
   even though the installed plist's `ProgramArguments` contain the literal
   string `/Users/edr/.local/share/claude/versions/2.1.259` (`~/Library/
   LaunchAgents/com.joulewise.night.plist`, read this session) which *does*
   match the pattern. The audit's §1 census description is right about the
   predicate and silent about this exemption; it is a real property the design
   may rely on.
2. A watchdog that runs the census itself is likewise invisible to it, so the
   brief's constraint "launch only when the census is EMPTY … so the design
   cannot race the gate" is *implementable* — the watchdog does not
   self-refuse.
3. **New finding (rehearsal integrity):** a night driver started *by hand from
   inside a Claude Code session* is blind to that session, because the session
   is its ancestor. Every "run the driver at the bench to see it refuse" check
   is therefore weaker than it looks, and the Q6 fake-census test must spawn the
   decoy as a **sibling or child**, never as an ancestor. Worth its own finding
   line against `night_gate.py:388-415` and R-3
   (`MAGISTRATE-RULING-UNATTENDED-STAGE1.md:72-82`: "the census is the driver's
   first act and uses the production predicate").

**B-2 — the census currently matches a GUI app Ed may leave running. [bench]**
`pgrep -lf "codex|claude|t3"` right now returns, besides the expected agents:

```
4079 /Applications/ChatGPT.app/Contents/Frameworks/Codex Framework.framework/…/Helpers/Codex (Servi…
4096 /Applications/ChatGPT.app/Contents/Resources/codex -c features.code_mode_host=true app-server …
4038 /usr/bin/tar -xJf node-runtime.tar.xz -C /Users/edr/.cache/codex-runtimes/…
```

ChatGPT.app's own "Codex Framework" helpers match `codex`. If ChatGPT.app is
left open while Ed is away, **every real night refuses**
`night_refused_agent_present` (`night_gate.py:415`) and no watchdog can fix it,
because killing a GUI app Ed left running is not a decision a lieutenant-class
actor should take. This belongs in the stand-down email as an explicit ask.
It also strengthens audit F5 with a case that is not a stray shell.

**B-3 — the courier-binary prune is live, and the current install survives it. [bench]**
`~/.local/share/claude/versions/` held `2.1.248, 2.1.251, 2.1.252, 2.1.259` at
the audit's 20:05 reading (`01-audit-night-loop.md:293`); at 20:46 it holds
`2.1.251, 2.1.252, 2.1.259` (dir mtime 20:21) — a version was pruned inside
16 minutes. The installed plist still pins a version *file*
(`--courier-bin …/versions/2.1.259`), but its rendered
`PATH=/Users/edr/.local/bin:/usr/bin:/bin:/usr/sbin:/sbin` now makes the
fallback work: under exactly that PATH, `shutil.which("claude")` →
`/Users/edr/.local/bin/claude` [bench]. So audit F6 is cured *for this
install* by the 20:16 re-render, and the surviving rule for anything new is:
**pin the symlink, never a version file** (`_resolve_courier_bin`,
`run_night.py:571-596`, falls back to `which` only when the pinned path is
absent).

**B-4 — the armed state is valid right now, and it is one commit from dying. [bench]**
`git -C /Users/edr/code/JouleWise rev-parse HEAD` = `33290b8b…` = the plan's
`repo_head` (`/Users/edr/night-custody/rehearsal-20260903/night_plan.json`).
The gate compares the plan's `repo_head` to `probes.checkout_head()`, which is
`git -C REPO_ROOT rev-parse HEAD` with `REPO_ROOT = Path(__file__).parents[1]`
= `/Users/edr/code/JouleWise` (`run_night.py:23`, `:270-274`;
`night_gate.py:599-609`). **Any commit or pull the relaunched magistrate makes
on the canonical checkout's `main` refuses the night it is supposed to be
driving.** That is audit F1/B7, and a relaunch watchdog makes it *more* likely,
not less, because the whole point is that a session is running unattended
between nights. Git worktrees each carry their own `HEAD` file, so work done in
`/Users/edr/code/JouleWise-wt-*` does not move the canonical HEAD
[design fact; not executed as a differential test this session] — this is the
cheap cure and it must be written into the launch prompt.

---

## 1. Topology — recommend a polling `StartInterval` LaunchAgent

**Recommendation: one user LaunchAgent, `com.joulewise.magistrate`,
`StartInterval 300` + `RunAtLoad true`, whose program is a short-lived tick
(`scripts/magistrate_watchdog.py tick`) that reads state, decides, acts, and
exits in seconds.** It is a supervisor, not a session host: the session it
launches is detached (`start_new_session=True`) and outlives the tick, exactly
as the driver treats the courier (`run_night.py:755-759`).

Why polling wins here: every input the decision depends on is a *level*, not an
event — is a session alive, is a fence open, is a chain still running, has the
usage window reopened, has Ed pushed the stop flag. None of those produce a
filesystem event on this machine, and the two most important ones (a session
dying; a usage window reopening at an unknown hour) produce no local signal at
all. A 5-minute poll costs one Python start per 5 minutes and bounds the
"loop is dead" gap to 5 minutes.

**Rejected — `StartCalendarInterval` (a fixed daily relaunch time).** Failure
mode: it converts a *liveness* problem into a *schedule* problem. A session
that dies at 04:10 (usage window exhausted, `claude` crash, OOM) stays dead
until the next calendar fire; over a week away that is the difference between
losing 20 minutes and losing 20 hours. Second failure mode: launchd coalesces
missed calendar fires after sleep/shutdown, so a machine that hiccups can skip
the relaunch entirely — the same replay hazard R-6 already had to guard against
(`MAGISTRATE-RULING-UNATTENDED-STAGE1.md:113-117`).

**Rejected — `WatchPaths`.** Two failure modes, both fatal. (a) The events we
need are absent: no file is written when a session dies or when a rate limit
lifts, so the job would never fire in exactly the cases it exists for.
(b) The events that *do* exist fire at the worst moment: watching the custody
root means firing while the driver writes `chain.started`, `censuses.jsonl`,
`receipt.json` — i.e. during capture, when starting an agent breaches the
zero-agent fence (D-127 §2, `decision_log.md:8240-8244`). A watchdog whose
trigger is "the night wrote a file" is a watchdog that wakes up inside the
night. `WatchPaths` is also edge-triggered and famously lossy on rapid writes
[not executed].

**Rejected — extending the courier baton.** The courier is structurally the
wrong actor and the audit proves it: it is one `-p` turn with no wake source
after it ends (`01-audit-night-loop.md:146-148`); the driver returns without
terminating it and unlinks its lock (`run_night.py:792-798`, `:812-814`), so
after `courier.sent` nothing tracks it and the dead-man cannot see it
(`dead_man` checks `courier.sent` first and skips, `run_night.py:1309-1313`);
and it already performs rule-11-forbidden irreversible actions unsupervised —
on 09-02 it uninstalled the agents, authored the next plan, emailed the arming
notice and re-installed the agents (`01-audit-night-loop.md:89-90`, F3 at
`:223`). Loading "and also keep the loop alive forever" onto that actor deepens
F3. Keep the courier as the *night-report* baton it is; make relaunch a
separate, dumb, non-agent mechanism. This also honours D-127 §4's closing
sentence — "independent launchd fallback timer as the second wake layer. Never
one mechanism" (`decision_log.md:8254-8260`).

---

## 2. State machine

### 2.1 Inputs (all read every tick; none cached across ticks except the state file)

| input | source | notes |
|---|---|---|
| `plans` | glob `~/night-custody/*/night_plan.json` | schema `joulewise.night_plan.v1`; keys per `night_gate.py:102-114` |
| `now` | `time.time()` (epoch) + `time.monotonic()` for durations | never compare wall-clock deltas across a tick |
| `census` | `/usr/bin/pgrep -lf "codex|claude|t3"` run by the watchdog itself (`night_gate.AGENT_CENSUS_ARGV`, `:34`) | B-1: the watchdog and its ancestors are exempt; the session it launched is visible |
| `chain state` | `<custody>/night/chain.started` exists && `chain.exited` absent | the dead-man's own liveness test, `run_night.py:1338-1340`; needed because there is **no runtime bound on the chain** (audit F2, `run_night.py:436-480`) so the clock alone cannot tell you the night is over |
| `courier.sent` | `<custody>/night/courier.sent` | `run_night.py:731`; gate for post-night relaunch |
| `stop flag (remote)` | `git ls-remote --exit-code origin refs/heads/ops/stop-magistrate` | rc 0 = STOP, rc 2 = absent [bench: rc=2 now]; no clone, no fetch, does not touch the canonical checkout |
| `stop flag (local)` | `~/night-custody/STOP` | for the bench and for the session itself to self-arrest |
| `lock` | `~/night-custody/magistrate.lock` = `{pid, pgid, start_epoch_s, launched_epoch_s, session_dir}` | liveness proved by `os.kill(pid,0)` **and** matching process start time (PID-reuse guard) |
| `state` | `~/night-custody/watchdog/state.json` | `{state, since_epoch_s, backoff_index, last_notified_state, consecutive_failures}` |

### 2.2 The fence predicate (the single most important function)

```
fence_open(now, plans) :=
      any plan p with:  p.t0 - LEAD_S  <=  now  <=  p.t0 + p.window_max_s + COURIER_SLACK_S
   or any plan p with:  chain_running(p)                       # F2: no runtime bound
   or  DEADMAN_HOUR:DEADMAN_MINUTE <= now_local < +1 minute    # 07:00, run_night.py:48-49
   or  HARD_BELT_START <= now_local <= HARD_BELT_END           # 02:45–03:30, the brief's belt
```

`LEAD_S = 2700` (45 min, see §8.4), `COURIER_SLACK_S = COURIER_DEADLINE_S +
sum(COURIER_BACKOFF_S) = 300 + 840 = 1140 s` — both constants imported from
`run_night.py:45-46`, never re-typed, so a change there cannot silently
desynchronise the watchdog. Note `_completion_epoch_s` (`run_night.py:900-901`)
only adds `COURIER_DEADLINE_S`; the watchdog must be *more* conservative than
the driver because the driver's own retries can run 35 minutes past it
(`run_courier`, `:745-805`).

### 2.3 States and transitions

| state | meaning | leaves to | on what |
|---|---|---|---|
| `IDLE` | no session, nothing blocking | `LAUNCHING` | not `fence_open`, no stop flag, no live lock, backoff expired |
| `LAUNCHING` | `Popen` issued, waiting for `session.heartbeat` | `RUNNING` / `BACKOFF` | heartbeat file within `HEARTBEAT_DEADLINE_S = 300` (reuses R-7's proven liveness shape, `run_night.py:632-668`) / else terminate group, classify exit |
| `RUNNING` | session alive, lock fresh | `STANDDOWN_REQUESTED` / `IDLE` / `DEGRADED` | fence opens in `LEAD_S` / session exited cleanly / lifetime > `SESSION_MAX_S` |
| `STANDDOWN_REQUESTED` | request file written, grace running | `STANDDOWN_FORCING` / `FENCED` | grace elapsed (t0−30 min) / session exited on its own |
| `STANDDOWN_FORCING` | SIGTERM → 120 s → SIGKILL on the session's process group | `FENCED` / `DEGRADED` | census clean of the launched group / anything still alive |
| `FENCED` | a night span or chain is open; launching is forbidden | `IDLE` | fence closed **and** (`courier.sent` present or no plan for tonight) |
| `BACKOFF` | last launch failed; waiting | `IDLE` | backoff timer expired |
| `STOPPED` | Ed's stop flag present | `IDLE` | flag removed (branch deleted) |
| `DEGRADED` | an invariant the watchdog may not resolve alone | — | terminal until a human or a session clears it; keeps polling and re-pushing status, never launches |

Every transition appends one line to `watchdog.log` and rewrites `state.json`.

### 2.4 Every write it makes (exhaustive — nothing under the repo working tree)

1. `~/night-custody/watchdog/state.json` (rewritten atomically: temp + `os.replace`)
2. `~/night-custody/watchdog/watchdog.log` (append-only)
3. `~/night-custody/magistrate.lock` (create / refresh / unlink)
4. `~/night-custody/magistrate/<launch_epoch>/` — `session.out`, `session.err`,
   `standdown.request`, `session.heartbeat` (written by the session), `exit.json`
5. `~/night-custody/watchdog/notices/<epoch>-<state>.md` — the email queue
6. a push of `state.json` + the last 200 log lines to branch
   `ops/watchdog-status`, from a **shallow clone under the custody root**, never
   by checking out a branch in the development tree — copying `_durable_record`
   (`run_night.py:512-568`) precisely because R-7 forbids moving the HEAD R-6
   binds (`MAGISTRATE-RULING-UNATTENDED-STAGE1.md:128-132`)

It writes **nothing** into `/Users/edr/code/JouleWise` — no commit, no
untracked file (the seat-launch rule about `unowned_dirty` applies to any
process putting files in a tree an agent will run in).

### 2.5 Where stand-down lives — recommendation: **request by file, force by signal; the watchdog owns the deadline**

Do **not** put the deadline inside the session. R-9 already assigns stand-down
to the magistrate — "(3) **ends the loop** (`ScheduleWakeup stop`) and the
session" (`MAGISTRATE-RULING-UNATTENDED-STAGE1.md:159-168`) — and the audit's
verdict on that clause is the whole reason we are here: "**NO CODE does this.
Nothing kills agents; the gate only REFUSES.** [GAP by design]"
(`01-audit-night-loop.md:44-46`). A self-check inside the session is a promise
by the actor least able to keep it: a session wedged in a Sol fix round, blocked
on a network call, or waiting on a subagent cannot honour a deadline, and the
cost of missing it is the entire night (`night_gate.py:415`).

Two-phase, and the phases have different owners:

- **t0 − 45 min — request (session's job).** Watchdog writes
  `standdown.request` (JSON: `t0`, `force_epoch_s`, `plan_id`). The launch
  prompt makes polling that file a standing obligation. The session must:
  stop new work, commit/push open work **in its worktree only**, write its
  resume pointer to `~/night-custody/magistrate/resume.md` (custody, *not* the
  repo — writing `RUN_STATE.md` on `main` would move canonical HEAD and refuse
  the night, B-4), send the stand-down email, then exit.
- **t0 − 30 min — force (watchdog's job).** `killpg(SIGTERM)` on the recorded
  pgid, 120 s, then `SIGKILL` — the existing `_terminate_process_group`
  (`run_night.py:320-348`) is the reference implementation. Then re-census; if
  anything the watchdog launched is still alive, or if a census hit remains that
  the watchdog did *not* launch (Ed's Terminal, ChatGPT.app per B-2), go
  `DEGRADED`, queue a notice, push the status branch, and do not launch again.

The watchdog must never kill a process it did not launch. That is the D-161
line: refusing to reap a stranger process defends against nothing hostile, but
killing one is irreversible, and rule 11 puts irreversible actions outside a
lieutenant's authority.

**`ScheduleWakeup` in `-p` mode: unknown. [not executed]** I was barred from
running any `claude` command, and the string `ScheduleWakeup` appears exactly
once in the whole repo — inside R-9 itself
(`MAGISTRATE-RULING-UNATTENDED-STAGE1.md:163`) — with no code, test, or doc
behind it. Treat it as unavailable in headless mode until someone runs
`claude --help` at the bench. The design above does not need it.

---

## 3. The launch command

```python
ARGV = (
    "/Users/edr/.local/bin/claude",          # the SYMLINK, never a version file (B-3)
    "-p", PROMPT,                            # passed in argv, as the courier does (:621-629)
    "--output-format", "text",
    "--model", "opus",
    "--permission-mode", "acceptEdits",
    "--allowedTools",
    "Read,Glob,Grep,Bash,Edit,Write,TodoWrite,Task,"
    "mcp__claude_ai_Gmail__send_message,mcp__codex__codex,mcp__codex__codex-reply",
)
Popen(ARGV, cwd="/Users/edr/code/JouleWise-wt-magistrate",
      stdout=out_fh, stderr=err_fh, start_new_session=True)
```

Notes and flags I could not verify:
- `--permission-mode acceptEdits` plus an explicit `--allowedTools` allowlist is
  the widest posture I would propose without an Ed ruling.
  `--dangerously-skip-permissions` / `bypassPermissions` is the analogue of the
  Codex `danger-full-access` that `CLAUDE.md` forbids on the bridge; if the
  narrow posture proves unworkable, that is an Ed decision, not a lieutenant's.
  **Exact flag spellings [not executed] — verify with `claude --help` before
  install.**
- `cwd` — I recommend a dedicated worktree, **not** the dev checkout the brief
  names, for the B-4 reason: the gate reads
  `git -C /Users/edr/code/JouleWise rev-parse HEAD`, so a session whose cwd is
  that tree is one `git pull` away from refusing its own night. See §8.6.
- No `--max-turns`: a `-p` turn should be allowed to run for hours. Bound it
  from outside instead (`SESSION_MAX_S`, §5).
- Codex MCP tools are included because the magistrate's job is to direct Sol
  (doctrine rule 8). Bridge depth stays one hop: this is a *top-level* `claude`
  started by a Python supervisor under launchd, not by a Codex session
  (`CLAUDE.md`: "a Claude-originated Sol session must not call Claude by MCP").

### The prompt (`docs/process/MAGISTRATE_RELAUNCH_PROMPT.md`, 24 lines)

```
You are the JouleWise magistrate, relaunched unattended by the watchdog. Ed is
away until ~2026-09-09 and cannot touch this machine. Nobody will answer you.

First act, before anything else: write {session_dir}/session.heartbeat with your
pid and `date +%s`. Second act: email Ed at claude.ai.copper531@passmail.net,
plain words, subject "magistrate relaunched" — say the time, the armed plan id
(or none), and what you intend to work on. Then read, in order:
@@REPO@@/RUN_STATE.md (the T30 pointer at the top names the durable pause file);
that pause file; @@REPO@@/docs/process/NIGHT_HANDBACK.md.

Standing mandate: D-128/D-169 — drive the loop toward a defensible paper, with
the unattended lane first. Every gate in CLAUDE.local.md still binds; you are
lieutenant-class, so the rule-11 forbidden list applies in full: no merges, no
process rules, no cadence changes, no arming or re-arming a night, no
uninstalling launch agents, nothing irreversible. Queue those for Ed by email.

HARD CONSTRAINT while any night plan is armed: never commit, pull, rebase, or
check out anything in /Users/edr/code/JouleWise. Its HEAD is what the night gate
compares to the plan; moving it refuses the night. Work only in a worktree.

Poll {session_dir}/standdown.request every few minutes. When it appears: stop,
commit and push open work in your worktree, write your resume pointer to
/Users/edr/night-custody/magistrate/resume.md, email Ed that you are standing
down, and EXIT. You have 15 minutes; after that you are killed.
```

### Does `/loop` cadence survive a headless session? No — and it does not need to.

`claude -p` is one turn (`01-audit-night-loop.md:146-148`: "A `-p` session is
one turn. When it ends there is no wake source"). One turn is not one tool call,
though: a `-p` turn can run hundreds of tool calls for hours, which is what
makes this viable at all. So the cadence is **supervision, not scheduling**: the
watchdog guarantees *a* session exists whenever it is legal for one to exist,
and each session runs until it finishes its work, hits the stand-down, or dies.
That is the brief's own stated fallback, and it is the primary design, not a
consolation prize. `ScheduleWakeup` remains [not executed / unverified] and is
not in the critical path.

---

## 4. Usage-limit backoff

The failure signature: `claude -p` exits non-zero, quickly, and writes a
rate-limit message to stdout/stderr. Classification at exit, in this order:

1. **Clean** — session wrote `exit.json` with a reason → reset `backoff_index`,
   go `IDLE`, relaunch at the next tick if nothing blocks.
2. **Usage-limited** — exit non-zero **and** the captured output matches a
   rate-limit pattern (`limit`, `rate limit`, `usage`, case-insensitive; **exact
   string [not executed]** — capture it during the first live backoff and pin it
   then). Enter `BACKOFF` with the *long* ladder.
3. **Fast failure** — exit non-zero within `120 s` and no heartbeat → treat as
   auth/binary/config failure. Short ladder, and after 3 consecutive ones go
   `DEGRADED` (a broken binary is not cured by waiting).
4. **Late failure** — exit non-zero after a heartbeat and > 20 min of life →
   reset the ladder to index 0 (the session did real work; this is not a
   systemic block).

Ladders (jittered ±10 % so ticks do not phase-lock):
`long = [15 m, 30 m, 60 m, 60 m, …]` capped at 60 min;
`short = [5 m, 15 m, 30 m]` then `DEGRADED`.

Cost of the worst case: one `claude` process start per hour, ~5 s each. That is
not "burning the machine", and the 5-hour window means a 60-minute cap
rediscovers availability within ~20 % of a window.

**Notification discipline: one message per state *change*, never per attempt.**
`state.json` carries `last_notified_state`; a notice is queued only when
`state != last_notified_state`. Because a watchdog cannot send email at all
(§8.2), a notice queued while no session can start reaches Ed by the durable
channel: the `ops/watchdog-status` branch push, readable from a phone — exactly
R-7's "durable record, no agent" layer
(`MAGISTRATE-RULING-UNATTENDED-STAGE1.md:128-132`). The next session that does
start drains `notices/` into one email as its second act.

---

## 5. Failure table

| failure | detection | containment | who hears |
|---|---|---|---|
| **Watchdog dies mid-tick** | launchd re-runs the job at the next `StartInterval` (crash of a short-lived job is not fatal to the schedule) [not executed] | tick is idempotent: every action is guarded by a file predicate re-read at entry, so a half-finished tick re-decides from scratch | nobody directly; `state.json` mtime staleness is visible in the pushed status branch, and the launch prompt tells the session to report a stale watchdog |
| **Watchdog job unloaded / plist removed** | nothing local detects it | none — this is the single point of failure | the night courier still emails after each night; the absence of relaunch emails is the signal. Accept it: adding a watchdog-for-the-watchdog is the gold-plating D-161 warns about (`decision_log.md:207`) |
| **Session hangs forever** (alive, no progress) | `SESSION_MAX_S = 4 h` from `launched_epoch_s`, plus heartbeat mtime not advancing (prompt requires touching it hourly) | `STANDDOWN_REQUESTED` → forced kill → `IDLE` → fresh session | notice queued; next session emails; status branch updated |
| **Session exits mid-fix, dirty worktree** | `exit.json` absent + non-zero exit | watchdog **does not** clean, revert, or `git checkout` anything — that is how uncommitted work is lost (memory `mutation-probe-on-uncommitted-work`). It records the worktree path and the `git status --porcelain` output into the notice, and the next session inherits the mess with instructions to commit-or-stash before anything else | next session's email |
| **Two magistrates alive** | (a) `magistrate.lock` with pid **and** process start time (PID reuse guard); (b) a census that lists a `claude` the watchdog did not launch; (c) launchd will not start a second instance of the same job while one runs [not executed] | never launch while the lock is live; if the census shows a stranger `claude` outside the fence, that is Ed's or a stale session — go `DEGRADED`, do not kill | notice + status branch |
| **Clock skew / DST** | all fence arithmetic in epoch seconds; only the 07:00 dead-man minute and the 02:45–03:30 belt are local-time, computed with `zoneinfo` | a skew that moves t0 also moves the gate's own `night_window_expired` check (`night_gate.py:561-571`), so the two stay consistent; the night gate additionally binds boot UUID + clocks (`night_refused_boot_clock`, ORDER `:98`) | refusal email via the courier |
| **`claude` auto-update moves the binary** | resolve `~/.local/bin/claude` every tick and `os.access(X_OK)`; record the resolved target in `state.json` | pin the **symlink**, never a version file (B-3: a version was pruned within 16 minutes this evening); if the symlink is missing, `DEGRADED` immediately — do not guess a version | notice + status branch. Same defect as audit F6 (`01-audit-night-loop.md:226`); do not re-introduce it |
| **Night chain overruns its window** (audit F2) | `chain.started` without `chain.exited` keeps `fence_open` true regardless of the clock | watchdog simply never launches; it does not kill the chain (that is the driver's and dead-man's business, and F8 says neither does) | courier/dead-man path |
| **Ed's ChatGPT.app or Terminal left open** (B-2) | census shows a hit the watchdog did not launch, inside the fence | cannot cure; `DEGRADED` before t0 so the notice goes out *before* the night is lost rather than after | stand-down email must name the apps to quit |

---

## 6. Bench test plan (no real night)

**Testability requirement:** every constant above (`LEAD_S`, `SESSION_MAX_S`,
backoff ladders, `HEARTBEAT_DEADLINE_S`, custody root, `claude` path, the
census argv, the `git` binary) is injected — a `Config` dataclass in the pure
module, exactly R-2's split (pure `joulewise/…` library, thin `scripts/…`
driver, `MAGISTRATE-RULING-UNATTENDED-STAGE1.md:50-64`). Tests never spawn
`claude`.

Unit tests (`tests/test_magistrate_watchdog.py`):
1. `fence_open` — before/at/inside/after `[t0-LEAD, completion+slack]`; the
   07:00 minute; the 02:45–03:30 belt; multiple plans; a plan with
   `chain.started` and no `chain.exited` fences regardless of clock; a plan
   whose `t0` is a week old does not fence.
2. Constants are *imported* from `run_night.py`, not re-typed — assert
   `COURIER_SLACK_S == COURIER_DEADLINE_S + sum(COURIER_BACKOFF_S)` and that the
   dead-man minute equals `DEADMAN_HOUR/DEADMAN_MINUTE` (`run_night.py:45-49`).
   This is the regression that catches the F10 class of doc/code drift.
3. Census parsing — empty (`exit 1`, empty stdout, per `night_gate.py:405-406`)
   vs hits; multi-line argv blobs (the 09-02 record has 1136 lines for 24
   processes [bench]) parse to 24 process rows, not 1136.
4. Lock: fresh/stale/PID-reuse (same pid, different start time → stale).
5. Exit classification: all four classes of §4, with captured-output fixtures.
6. Backoff ladder: indices, cap, jitter bounds, reset on late failure.
7. Stop flag: `ls-remote` rc 0 / rc 2 / network error (a network error is **not**
   a stop — fail *open* for a liveness switch, per D-161: the adversary here is
   nobody).
8. Launch argv builder: symlink pin, allowlist, cwd, `start_new_session`.
9. Notification dedup: N ticks in one state → exactly one notice.
10. Every write path is under the injected custody root — an assertion that no
    test wrote inside a git work tree.

Fake-census test, written correctly per B-1: the decoy must be spawned as a
**child** of the test (`start_new_session=True`), never as an ancestor of the
process invoking `pgrep`, or the test passes vacuously.

**The one end-to-end rehearsal (~25 min, no `claude`, no real night):**
temp custody root; a fake plan with `t0 = now + 10 min`, `window_max_s = 120`;
`LEAD_S` compressed to 300 s and the force grace to 60 s by config; the session
binary replaced with a stub shell script that writes `session.heartbeat`, then
polls `standdown.request`, then sleeps. Drive real ticks and assert the observed
sequence: `IDLE → LAUNCHING → RUNNING → STANDDOWN_REQUESTED` (stub exits
cleanly) `→ FENCED` (no launch attempted for the whole fake window)
`→ IDLE → RUNNING`. Then re-run the same rehearsal with a stub that *ignores*
the request, and assert `STANDDOWN_FORCING` kills the group and the census is
clean before t0. Then a third pass with the stop flag set: assert `STOPPED` and
zero launches. Only after those three passes does anything get installed.

---

## 7. Files to build, and cost

| file | what | size |
|---|---|---|
| `joulewise/magistrate_watchdog.py` | pure logic: `Config`, `fence_open`, state machine, exit classification, backoff, argv builder. No `subprocess` at import (R-2). | ~320 lines |
| `scripts/magistrate_watchdog.py` | the tick driver: probes, `Popen`, signals, atomic writes, shallow-clone status push (adapt `_durable_record`, `run_night.py:512-568`), `tick` / `--dry-run` / `--status` subcommands | ~300 lines |
| `configs/launchd/com.joulewise.magistrate.plist.template` | label `com.joulewise.magistrate`, `StartInterval 300`, `RunAtLoad true`, no `KeepAlive` (the installer already refuses a template containing it — `install_night_agent.sh:35-38` — keep that check) | ~35 lines |
| `scripts/install_magistrate_agent.sh` | render + `launchctl bootstrap gui/501` + verify + `--uninstall`; **no** `repo_head` check (audit F9 shows that check makes uninstall fail after a day of merges) | ~90 lines |
| `docs/process/MAGISTRATE_RELAUNCH_PROMPT.md` | the §3 prompt, with `{session_dir}` / `@@REPO@@` substitution mirroring `_courier_argv` (`run_night.py:610-620`) | 24 lines |
| `tests/test_magistrate_watchdog.py` | §6 units + the three rehearsal drivers | ~500 lines |
| `docs/process/UNATTENDED_WATCHDOG.md` | one doc: topology, states, constants table, the operator card (how Ed stops it from a phone) | ~120 lines |
| decision-log entry + `state_kernel.json` row | the process rule this creates, under `UNATTENDED-LAUNCH-01` | — |

**Estimate: 8–11 Sol-hours** — WO-A pure module + units 2–3 h (xhigh); WO-B
driver, installer, plist 2–3 h (xhigh); WO-C prompt + doc + rehearsal harness
1–2 h (high); audit + two fix rounds + delta re-audit 3 h. Elapsed ~1.5 days
with the streams fanned out, and the three bench rehearsals plus lead-side live
verification (doctrine rule 1) are the lead's, not Sol's.

---

## 8. Push-back on the constraints

**8.1 "Launch only when the agent census is EMPTY" — too strong; narrow it to
the fence.** [bench, B-2] The census matches ChatGPT.app's Codex helpers and any
leftover Claude Code background shell (audit F5, `01-audit-night-loop.md:206`).
Applied literally, the watchdog would refuse to start a session at 14:00 on a
Wednesday because a GUI app is open — defending against nothing, since no gate
runs at 14:00. The constraint's stated purpose ("so the design cannot race the
gate") is only meaningful inside the night span. **Recommend:** census-empty is
required only when `fence_open` is within `LEAD_S` of a plan, or when a chain is
running; outside that, the only launch conditions are "no live lock, no stop
flag, backoff expired". This is the D-161 prune shape applied to a new
mechanism instead of an old one (`decision_log.md:207`).

**8.2 "Email Ed at each launch and each stand-down (Gmail MCP … or the
courier's route — say which)" — neither, quite: the watchdog cannot send email
at all.** R-7's forcing constraint is still true — "No file in the repo can send
email" (`MAGISTRATE-RULING-UNATTENDED-STAGE1.md:125-127`), and Gmail MCP exists
only inside a Claude session. So: **the session sends both emails, and the
watchdog's channel is the pushed status branch.** Launch email = the relaunched
session's second act, after `session.heartbeat` (heartbeat first, so liveness is
proved by a file the watchdog can see even if the email fails — the courier's
proven ordering, `NIGHT_COURIER_PROMPT.md:3-5`). Stand-down email = the
session's last act before exiting, while it is still alive. The only case with
no email is the one where no session can start — and that is exactly the case
the durable branch exists for.

**8.3 Kill switch — the cheapest remote-actionable path is a branch, not a
file, and not email.** `git ls-remote --exit-code origin
refs/heads/ops/stop-magistrate` returns rc 0 if it exists, rc 2 if not [bench:
rc=2 now]. Ed can create that ref from the GitHub mobile web UI or a push, with
no clone and no local access. Critically it **does not move `main`**, so it
cannot trigger the `night_plan_stale` refusal the way a commit to `main` would
(B-4, `night_gate.py:599-609`) — which rules out the obvious "commit a STOP file
to main" design. Email as a kill switch is not implementable: reading mail
requires a session, and the thing being stopped is the session.

**8.4 30 minutes is too tight for a real night; split it.** A stub night's
window is 900 s, but a real capture is hours and a session may be mid-Sol-round
with unpushed work. **Recommend `LEAD_S = 45 min` for the request and t0−30 min
for the forced kill** — the brief's 30 minutes survives as the hard deadline,
with 15 minutes of grace in front of it. Ed's cadence decision is then only
about the request time.

**8.5 The watchdog does not cure F3, and should not pretend to.** Relaunching a
session is a *liveness* mechanism. "Who arms night N+1, under which gate"
(audit B10, `01-audit-night-loop.md:249`) remains open, and a relaunched
magistrate arming its own next night is the same rule-11 problem the courier
already has — window commitments and irreversible actions are on the
lieutenant-forbidden list. **Recommend the watchdog's charter explicitly exclude
arming**, and the launch prompt forbid it (§3), leaving arming to the
Ed-email-then-arm pattern already written into the handback
(`NIGHT_HANDBACK.md:70-76`). Otherwise this consult ships an automated
rule-11 violation.

**8.6 `cwd = /Users/edr/code/JouleWise` is the one constraint I would change
outright.** [bench, B-4] The gate reads that tree's HEAD; the session's mandate
(D-128 rule 7: push green commits promptly) moves it; the collision is not
hypothetical — it already killed tonight's original arming
(`NIGHT_HANDBACK.md:19-24`) and is audit F1/B7. Give the session a dedicated
worktree (`/Users/edr/code/JouleWise-wt-magistrate`), forbid touching the
canonical checkout while a plan is armed, and treat the audit's own first
recommendation — pin the plan to the measurement checkout
(`01-audit-night-loop.md:256-261`) — as the real cure. Until that lands, the
prompt's HARD CONSTRAINT paragraph is the only thing standing between an
unattended week and seven refused nights.

**8.7 Rulings this design touches (rule 11 flags, for the cold gate).**
- **R-9** (`:159-168`) assigns stand-down to the magistrate and to Ed's
  behaviour. §2.5 moves the *deadline and the force* to a machine actor. That is
  a reinterpretation of a ruling, so mandatory cold gate. R-9's suspension of the
  turn-end wake-source rule also needs rewording: the LaunchAgent is no longer
  the wake source only "on armed nights" — it becomes the standing one.
- **R-3** (`:72-82`) fixes the census predicate as production-identical. This
  design *reuses* it unchanged (good), but B-1 shows the predicate has an
  undocumented ancestor exemption, and B-2 shows it matches a GUI app. Both
  belong in the R-3 record whether or not the census is retightened (audit
  recommendation 4, `:275-279`).
- **D-127 §4** (`decision_log.md:8254-8260`) specifies preflight → launch →
  liveness proof → bounded retries → independent launchd fallback. This design
  is that shape with the launcher promoted from "the window's final step" to a
  standing timer — an extension, not a contradiction, but say so explicitly.
- **D-127 §2 / D-128 §3**: the zero-agent capture fence is untouched; §2.2's
  fence predicate is strictly *more* conservative than the driver's own.
- **D-169** (`decision_log.md:215`) makes this the top lane and names
  `UNATTENDED-LAUNCH-01` as the owning row — file it there, not as a new stream.
- **D-161** (`:207`): the stop flag fails *open* on a network error, the
  watchdog never kills a process it did not launch, and there is no
  watchdog-for-the-watchdog. Those are the three places I deliberately did not
  fail closed, because the only adversary would be the trusted operator.

---

## Executed evidence (this session, read-only)

- `pgrep` ancestor exemption: decoy sibling pid 3239 matched; self-censusing
  process pid 3589 absent from its own output; grandparent pid 4009 absent when
  `pgrep` was invoked via `/bin/sh -c`, while its new-session child 3618 and
  same-session child 3619 both matched; my own ancestry (`4117 zsh → 1536
  claude`) absent from a census that lists another session's `1723 claude`.
- `/usr/bin/pgrep -lf "codex|claude|t3"` at 20:46 lists ChatGPT.app's
  `Codex Framework` helpers (4079, 4080, 4096, 4099, 4100) and a
  `codex-runtimes` `tar` (4038).
- `/Users/edr/night-custody/rehearsal-20260902/night/censuses.jsonl`: one
  record, `exit_code 0`, 1136 stdout lines = 24 process rows; no `run_night.py`
  row; `result.json` `census_count 1`; `courier.json` `{attempted 1, sent true}`;
  `night.log` 02:56:00 started → REFUSED → 02:56:02 `REHEARSAL_ONLY` → 02:56:16
  push → 02:57:25 courier sent → 02:57:27 push.
- `~/Library/LaunchAgents/com.joulewise.night.plist`: `--courier-bin
  /Users/edr/.local/share/claude/versions/2.1.259`,
  `PATH=/Users/edr/.local/bin:/usr/bin:/bin:/usr/sbin:/sbin`, 02:56,
  `RunAtLoad false`, no `KeepAlive`; `launchctl list | grep joulewise` →
  `com.joulewise.night`, `com.joulewise.night.deadman`, both exit 0.
- `~/.local/share/claude/versions/` = `2.1.251, 2.1.252, 2.1.259` (dir mtime
  20:21); `~/.local/bin/claude → versions/2.1.259` (19:51);
  `PATH=/Users/edr/.local/bin:… python3 -c 'shutil.which("claude")'` →
  `/Users/edr/.local/bin/claude`.
- `git -C /Users/edr/code/JouleWise rev-parse HEAD` = `33290b8b…` = the plan's
  `repo_head`; `git worktree list` shows the canonical checkout plus 7+ linked
  worktrees.
- `git ls-remote --exit-code origin refs/heads/ops/stop-magistrate` → rc 2.
- Repo-wide grep for `ScheduleWakeup` → one hit, in R-9's text only.

**Not executed:** any `claude` or `codex` invocation (so `-p` flag spellings,
`ScheduleWakeup` availability in headless mode, and the rate-limit message
string are unverified); launchd `StartInterval` overlap/coalescing behaviour;
a differential test that a worktree commit leaves the canonical HEAD unmoved.
