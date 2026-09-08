```json
{
  "schema": "claude-codex-report/v1",
  "genre": "scout",
  "status": "findings",
  "completion": "partial",
  "summary": "Watchdog recovered during intake; redo instructions are stale, first-night wiring remains incomplete, and independent silent-success paths exist. PID 48645 identification is blocked by process-table access.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": "d8ad6c15d48a41ad9e562ce9845bf8fb874826bb",
    "head_end": "d8ad6c15d48a41ad9e562ce9845bf8fb874826bb",
    "upstream_end": "d8ad6c15d48a41ad9e562ce9845bf8fb874826bb",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "rows": [
      {"id":"R1","action":"needs_ruling","subject":"Replace unconditional redo with recovery-aware handoff"},
      {"id":"R2","action":"needs_ruling","subject":"Resolve headless rehearsal authority and supply executable night handback"},
      {"id":"R3","action":"start_now","subject":"Use activation-bound acknowledgement and progress evidence"},
      {"id":"R4","action":"wait_for","subject":"Verify cooperative descendant cleanup","wait_for":"WATCHDOG-CENSUS-01 and RESUME-DAEMON-01 integration"},
      {"id":"R5","action":"wait_for","subject":"Identify PID 48645","wait_for":"Lead process-table observation"},
      {"id":"R6","action":"do_not_start","subject":"Real unattended window","wait_for":"Reviewed REHEARSAL_STUB courier evidence"}
    ]
  },
  "verification": [
    {
      "id":"V1","kind":"inspection",
      "cmd":"git status --short --branch; git rev-parse HEAD",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["## HEAD (no branch)","d8ad6c15d48a41ad9e562ce9845bf8fb874826bb"]},
      "expected":{"exit_code":0,"tail_regex":"d8ad6c15d48a41ad9e562ce9845bf8fb874826bb"}
    },
    {
      "id":"V2","kind":"inspection",
      "cmd":"launchctl print gui/$(id -u)/com.joulewise.magistrate | rg 'state =|runs =|last exit code|run interval'",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["\trun interval = 300 seconds"]},
      "expected":{"exit_code":0,"tail_regex":"run interval = 300 seconds"}
    },
    {
      "id":"V3","kind":"inspection",
      "cmd":"/bin/ps -p 48645 -o pid,ppid,lstart,command",
      "cwd":".",
      "observed":{"result":"fail","exit_code":127,"tail":["zsh:1: operation not permitted: /bin/ps"]},
      "expected":{"exit_code":0,"tail_regex":"48645"}
    }
  ],
  "flags": [
    {
      "id":"F1","kind":"verification_gap","level":"blocking",
      "text":"Sandbox denied ps; PID 48645 executable, custody root, open locks, and current descendants are unverified.",
      "needs":"Lead supplies read-only full argv and open-file observation for PID 48645."
    },
    {
      "id":"F2","kind":"environment","level":"nonblocking",
      "text":"Live custody changed independently: activation 1ef89702-8b11-4463-8d6b-3c1400510f1a launched and notice_acknowledged was recorded.",
      "needs":"Reconcile the current activation before following stale redo instructions."
    }
  ]
}
```

## Scheduling matrix

Ranked by qualitative likelihood × cost. These exclude the three already-assigned defects except where their fixes need an integration boundary.

| Row | action | wait_for | collision surface |
|---|---|---|---|
| R1: stale redo procedure | needs_ruling | Current-owner reconciliation | Existing resident, exclusive lock, canonical checkout |
| R2: first-night handback | needs_ruling | R1 | Relaunch prompt, rehearsal authority, night installer |
| R3: acceptance evidence | start_now | None; inspect current evidence | Acknowledgement consumption, heartbeat, attempt logs |
| R4: descendant cleanup | wait_for | Census/daemon fixes | Cooperative exit and frozen reaper inventory |
| R5: PID 48645 | wait_for | Lead’s process observation | Possible orphan supervisor or test process |
| R6: real window | do_not_start | R2–R5 and reviewed stub courier | Machine-wide quiet gate |

**Current facts answering questions 1 and 4**

The watchdog **does recover automatically**. `scripts/magistrate_watchdog.py:998–1019` resets the sane counter on each disagreement and releases `CLOCK_UNCERTAIN` after two consecutive sane comparisons. An in-memory probe returned:

```text
CLOCK 1 held True sane 1
CLOCK 2 held False sane 2
```

`clock_sane_samples: 1` means one consecutive sane comparison since the latest reset—not one tick in 45 hours. Transition-only logging (`:1032–1033`) also means an unchanged `events.jsonl` cannot establish missing ticks.

Live evidence supersedes the brief:

- `events.jsonl:3–4`: recovery and launch at **September 8, 00:51:55 PDT**.
- New child **84232**, supervisor **84229**, activation `1ef89702-8b11-4463-8d6b-3c1400510f1a`.
- Across observations, sane samples advanced **10 → 23 → 28**, consistent with the resident’s ten-second loop.
- Launchd reports **111 runs**, last exit **0**, interval **300 seconds**. Its short parent exits after `fork()` (`:2078–2080`); the resident inherits the service lock. Thus `-` PID/exit 0 is compatible with healthy supervision, and later lock-busy ticks also return 0 (`:2177–2179`).
- Backoff deadlines are **0**, boot identifier **null**, `clock_drain=false`, `resident_hold_drain=null`. None currently blocks launch. The old PID-4453 lock has already been replaced.
- `pmset -g custom` showed AC `sleep 0`; assertions showed lid-open activity. The observed caffeinate assertion was only **300 seconds**, so its existence alone does not establish all-night coverage. No procedure change is recommended against Ed’s ruling.

Replay:

```sh
nl -ba scripts/magistrate_watchdog.py | sed -n '998,1019p;2075,2102p;2177,2181p'
launchctl print gui/$(id -u)/com.joulewise.magistrate
cat ~/night-custody/magistrate/state.json ~/night-custody/magistrate/events.jsonl
pmset -g custom
pmset -g assertions
```

**1. Very high × high: the redo procedure now targets the wrong lifecycle state.**

The latest checkpoint still instructs deletion of the dead-4453 lock and interactive reinstallation (`00-DURABLE-STATE.md:510–517`). The watchdog has already recovered and owns a different activation. Repeating step 4 encounters `O_EXCL` on the existing lock (`install_magistrate_watchdog.sh:271`); deleting the current lock instead would destroy valid ownership.

There are further repeatability traps:

- Step 0 requires current HEAD to have exactly two parents (`MAGISTRATE_WATCHDOG.md:97–99`). Canonical HEAD `d8ad6c15` currently has **one** parent.
- Step 2 repeats moves of already-retired directories (`:119–127`).
- Both inventory and installer require an interactive Claude ancestor; a normal watchdog `-p` activation cannot reinstall itself (`magistrate_watchdog.py:872–880,925–929`; installer `:114–128`).

Demonstration:

```sh
git -C /Users/edr/code/JouleWise log -1 --format='%H %P'
cat ~/night-custody/magistrate/magistrate.lock
nl -ba docs/process_traces/2026-09-02-hands-free-week/00-DURABLE-STATE.md | sed -n '498,519p'
nl -ba scripts/install_magistrate_watchdog.sh | sed -n '114,128p;269,285p'
```

**Minimal cure:** the lead first selects **observe recovered activation** versus **controlled replacement**. Make the restart instructions conditional on current PID/start/activation evidence. Pin the reviewed installation revision explicitly rather than manufacture an unrelated merge solely to satisfy step 0.

**2. High × high: first-night intent exists, but its executable handback and authority conflict.**

Question 3: **observable headless activity is wired and has happened**—heartbeat, tool calls, and an acknowledged launch notice. **The first-night stub is not yet wired on this machine.**

The live sibling plan glob is empty, and the only installed JouleWise LaunchAgent plist is the magistrate. The watchdog observes plans; it does not install night agents or run their stub.

The resume plan says to arm a stub through `NIGHT_HANDBACK.md` (`00-DURABLE-STATE.md:265–266`), but that document still describes **September 3** and its old custody paths (`NIGHT_HANDBACK.md:26–49,54–88`). The relaunch prompt simultaneously directs email-then-arm (`:11–13`) and prohibits altering **plans or launchd configuration except heartbeat/ack** (`:19`). That is a lead-owned authority conflict.

The watchdog’s fake-root examples are stand-down fixtures, not installable nights: the night installer requires a real measurement checkout and matching HEAD (`install_night_agent.sh:80–94`).

Demonstration:

```sh
find "$HOME/night-custody" -mindepth 2 -maxdepth 2 -name night_plan.json -print
ls "$HOME/Library/LaunchAgents/"*joulewise*
nl -ba docs/process/MAGISTRATE_RELAUNCH_PROMPT.md
nl -ba docs/process/NIGHT_HANDBACK.md | sed -n '24,95p'
nl -ba scripts/install_night_agent.sh | sed -n '80,94p'
```

**Minimal cure:** rule narrowly on who may author/install the rehearsal, provide a current dated handback with real checkout pins, and install both night agents. Require the night driver’s own courier evidence. Its launch argv differs from the magistrate’s (`run_night.py:635–665`), so magistrate email success cannot substitute.

**3. High × medium: acceptance can falsely fail on a consumed ack, or falsely pass on mere process creation.**

Step 6 accepts a new attempt directory and non-adoption lock (`MAGISTRATE_WATCHDOG.md:256`). Those prove spawning, not useful work. `classify_exit(0, "")` returns `clean` (`magistrate_watchdog.py:1115–1117`); no heartbeat/progress deadline is enforced by the resident.

Conversely, a successful acknowledgment is deliberately **deleted** after consumption (`:1081–1107`). During this audit, the launch activation recorded `notice_acknowledged` in `events.jsonl:5`; `notice.ack` was absent afterward. An acceptance check demanding that file still exist would reject success.

Demonstration:

```sh
nl -ba scripts/magistrate_watchdog.py | sed -n '1081,1119p;1681,1693p'
tail -1 ~/night-custody/magistrate/events.jsonl
ls -l ~/night-custody/magistrate/notice.ack
```

**Minimal cure:** accept activation-bound `notice_acknowledged` evidence after consumption; inspect the corresponding accepted Gmail tool result. Require heartbeat identity and a bounded work/rehearsal outcome. Treat exit 0 and a fresh state-file timestamp as process health only.

**4. Medium-high × high: cooperative exit silently drops descendant accountability.**

`_finish_child()` removes the lock and durable session identity as soon as the root exits. If `standdown.request` exists, it records `FENCED` without any process-tree or census check (`magistrate_watchdog.py:1450–1487`). A child surviving its parent can therefore outlive a reported completed stand-down.

The independent in-memory probe produced:

```text
COOPERATIVE_EXIT FENCED census_calls=0 ownership_cleared True
```

This is a separate lifecycle defect from the reaper’s overly broad final census. The reaper also freezes `owned` before TERM and never discovers new descendants during its 540-second wait (`MAGISTRATE_WATCHDOG.md:177–181,211–235`). Narrowing its final census must not turn “recorded pairs absent” into “whole evolving tree gone.”

Demonstration:

```sh
nl -ba scripts/magistrate_watchdog.py | sed -n '1450,1487p;1684,1689p'
nl -ba docs/process/MAGISTRATE_WATCHDOG.md | sed -n '177,235p'
```

**Minimal cure:** retain observed descendant identities through root exit and verify their absence before releasing ownership/reporting completion. Add a regression where the root exits cooperatively while a child survives or reparents. Preserve the global quiet census for actual night admission.

**5. Unresolved likelihood × high: PID 48645 remains unclassified.**

I cannot responsibly identify it as a harmless fixture or competing production supervisor. Direct `ps` was denied. Retained evidence at `attempt-1.stream.jsonl:60` shows PPID **1**, start **September 4, 04:53:15**, and a truncated Python command ending at `/var`. Neither handoff inventory records PID 48645.

There are retained watchdog mutation directories under the supplied temporary root, but that is insufficient to bind this PID to any particular test. Current state progress proves it is **not presently monopolizing the production service lock**; it does not rule out another custody root, independent spawning, or resource interference.

Lead-side demonstration, **not executed successfully here**:

```sh
ps -ww -p 48645 -o pid,ppid,lstart,command
lsof -nP -p 48645
```

**Minimal cure:** bind full argv, working directory, custody root and open lock inode to its provenance. Only then classify it and decide cleanup. Do not adopt or signal it merely because its filename says watchdog.

**6. Medium × high: a supervisor replacement can miss required clock-drain enforcement.**

A resident seeing clock uncertainty latches a drain (`magistrate_watchdog.py:1691–1713`). But a short tick seeing the same uncertainty returns before inspecting ownership (`:1199–1200`), and `tick()` only performs durable replacement-drain adoption for `HOLD_UNSAFE` (`:2064–2076`).

If the resident disappears during continuing clock uncertainty, its live child may remain unsupervised until the clock recovers. An active plan’s deadlines do not rescue this path because clock refusal precedes plan enforcement.

Demonstration:

```sh
nl -ba scripts/magistrate_watchdog.py | sed -n '1196,1207p;1691,1713p;2064,2076p'
```

**Minimal cure:** extend replacement-supervisor recovery to the clock-drain case, preserving original deadlines and PID/start ownership. This concerns watchdog enforcement, not the already-assigned T-0 fixture clock defect.

**7. Medium × medium: installer rollback restores a file but can leave the prior service unloaded.**

The installer boots out the old job before bootstrapping the replacement (`install_magistrate_watchdog.sh:300–303`). On failure, cleanup restores the old plist bytes (`:163–178`) but does not bootstrap that restored service. “Rollback” therefore need not restore operation.

Demonstration:

```sh
nl -ba scripts/install_magistrate_watchdog.sh | sed -n '163,181p;299,308p'
```

**Minimal cure:** record whether the previous job was loaded, restore that loaded state on failed replacement, and verify it—or report explicitly that recovery requires reloading.

**8. Lower likelihood × high: unreadable state does not actually hold launches.**

`load_state()` attaches `state_error` and sets `HOLD_UNSAFE` for invalid state (`magistrate_watchdog.py:518–533`), but `decide()` never consumes `state_error`. With otherwise-clear fixture predicates, the in-memory probe returned:

```text
STATE_ERROR LAUNCHING
```

Loss of durable ownership followed by a daytime launch is particularly concerning because the daytime path intentionally does not require an empty machine-wide census.

Demonstration:

```sh
rg -n 'state_error' scripts/magistrate_watchdog.py
nl -ba scripts/magistrate_watchdog.py | sed -n '518,533p;1189,1267p'
```

**Minimal cure:** make state-read/schema failure an explicit decision hold until ownership is reconciled; do not silently treat it as a fresh boot.

**9. Lower likelihood × high: descendant signaling loses PID/start identity.**

Root ownership uses PID plus start time, but `stable_descendants()` retains only integer PIDs across snapshots and `signal_owned_tree()` sends signals without per-descendant start-token revalidation (`magistrate_watchdog.py:1316–1349`). A short-lived descendant’s PID can be reused between observation and signal.

Demonstration:

```sh
nl -ba scripts/magistrate_watchdog.py | sed -n '1316,1349p'
```

**Minimal cure:** retain each descendant’s start token and revalidate immediately before signaling, as the handoff reaper already attempts for its recorded pairs.

## Critical path

Reconcile the **already-recovered activation** before any reinstall or lock cleanup. Its launch acknowledgment is now recorded; absence of `notice.ack` is expected after consumption.

Integrate the census/daemon fixes with cooperative-descendant verification, classify PID 48645, then resolve the rehearsal-authoring conflict and supply the current pinned night handback. Only the installed stub night’s own result and courier evidence can close the first-night gate.

No files were modified, no processes were signaled, and no watchdog tick, installer, night run, or hardware measurement was invoked. The remaining audit blocker is live identification of PID 48645.