# Magistrate synthesis — relaunch watchdog designs (files 03 Opus, 04 blind Fable, 09 Sol), 2026-09-02 21:20 PDT

Three seats answered the brief (file 02). This records agreement, forks, and
what the magistrate proposes to the cold gate. Nothing here is installed.

## 1. Agreement (all three)
- One user LaunchAgent `com.joulewise.magistrate`, a Python supervisor that
  exits fast unless it owns a live child; no KeepAlive, no daemon, no sudo.
- Spawn through the stable symlink `/Users/edr/.local/bin/claude` (the
  courier's version-path pin was pruned within 16 minutes on 2026-09-02).
- The watchdog cannot send email; only a Claude session can (Gmail MCP).
  Launch email = the session's second act after a heartbeat file; stand-down
  email = its last act. Forced stand-downs and usage-exhaustion states are
  queued as `notice_pending` and reported by the next session's first email.
- Usage-limit backoff with one event per state transition, never per attempt.
- Kill only a process group the watchdog itself recorded; an unowned census
  hit is a hold, never a kill.
- The gate module is `joulewise/night_gate.py` (the brief's `scripts/` path
  was wrong); the watchdog imports the production `agent_census`, never a
  copy of the regex.
- The night plan pins the dev tree's HEAD, so any main push stales an armed
  plan (it did today). Structural cure = pin plans to the measurement
  checkout (audit file `2026-09-02-fresh-fable-audit/01` §6 item 1). Until
  that lands, the relaunch prompt forbids git operations in the canonical
  checkout while a plan is armed.
- Arming nights stays outside the watchdog's charter.

## 2. Forks and the magistrate's proposal

| Fork | Opus | blind Fable | Sol | Proposed |
|---|---|---|---|---|
| Poll | StartInterval 300, no WatchPaths | StartInterval 300 + setsid supervisor | StartInterval 60 + WatchPaths | **300 s, no WatchPaths** (man page: race-prone; may fire during capture) |
| Spawn | `claude -p` stream-json | `-p`, flags `--bg` as a 10-min experiment | `-p` | **`claude --bg`** as base: this magistrate session itself runs as a background job with `/loop` + `ScheduleWakeup` working, and `claude agents/attach/logs/stop/respawn` exist (Fable bench). `-p` is the fallback if `--bg` cannot start under launchd without a TTY. First build step is that bench proof. |
| Census scope | empty required only within LEAD of a plan or while a chain runs (§8.1) | as gate | as gate | **Opus 8.1** — D-161 shape; outside a fence no gate runs, and ChatGPT/Codex helpers of the session's own seats would otherwise block every daytime relaunch. The watchdog's own argv must not match the census (binary via env var). |
| Stand-down | request t0−45, force t0−30 | cooperative exit t0−40, TERM t0−30 | drain t0−40, TERM boundary−5, KILL −4 | **request file at t0−20 min; SIGTERM t0−5; SIGKILL t0−4** (Ed: "30 min seems too much"; the chain's own quiet prep settles 180 s after t0). Cooperative path: commit in worktrees, email, stop Codex children, exit. |
| Kill switch | branch `ops/stop-magistrate` via `git ls-remote --exit-code` | branch `magistrate-stop` | root file `MAGISTRATE_STOP` on main via `gh api` | **branch** — a file on main moves HEAD and stales the plan; the branch is phone-creatable, anonymous HTTPS, no HEAD move. Name `ops/stop-magistrate`. |
| Session cwd | dedicated worktree | canonical | canonical | **canonical checkout** — memory and the private doctrine load by path there; a worktree loses both. The HEAD trap is cured by the plan-pin lane (queued at cold-gate priority), and by the prompt's hard rule meanwhile. |
| Interlock with `run_night` | — | — | shared advisory lock so census+spawn is atomic vs gate census+chain | **deferred** — touches the night driver, which must not change before tonight's rehearsal; v1 never launches inside a fence, so the race window is the poll interval outside any plan span. Queued as a follow-up row. |

## 3. Fence predicate (proposed, exhaustive)
Launch is refused while any of: (a) a plan on disk has `t0 − 20 min ≤ now ≤ completion`, where completion = `t0 + window_max_s` extended while `chain.started` exists without `chain.exited`, then until `courier.sent` exists or 35 min after `chain.exited`; (b) local time is in the 07:00 minute; (c) local time is in 02:45–03:30 (config belt, brief-cited); (d) the stop branch exists; (e) an owned child is alive or `magistrate.lock` is held; (f) backoff has not expired; (g) inside (a)'s span the production census is non-empty. All writes go under `~/night-custody/magistrate/`, none under any repo tree.

## 4. Install handoff
D-171 item 4 authorizes install after gauntlet + cold gate; Ed reads email and does not reply. Handoff: this session commits a durable state, emails Ed the install notice, installs, and exits voluntarily at the next stand-down request; every later magistrate is watchdog-owned.

## 5. Rule-11 flags carried to the gate
R-9 reinterpretation (stand-down deadline moves to a machine actor); D-127 §4 launcher extended to a standing timer; census-scope narrowing vs R-3 "production-identical"; the watchdog charter's exclusion of arming; the plan-pin change as a precondition or a follow-up.
