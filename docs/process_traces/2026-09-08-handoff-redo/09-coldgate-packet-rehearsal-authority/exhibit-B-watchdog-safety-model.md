# Magistrate relaunch watchdog

`com.joulewise.magistrate` is a user LaunchAgent that evaluates a short Python tick at load and every 300 seconds. A safe tick forks a new session and leaves a resident supervisor running at 10-second resolution. The service never writes a repository tree. Its default mutable root is `~/night-custody/magistrate/`; `MAGISTRATE_WATCHDOG_CUSTODY_ROOT` or `--custody-root` may replace that root for a rehearsal.

## Safety model and state machine

The tick reads every sibling `*/night_plan.json` with the production `NightPlan.from_mapping`, the associated `night/chain.started`, `night/chain.exited`, and `night/courier.sent` markers, the local service state and locks, the local `STOP` file, the remote stop refs, local civil time, monotonic time, and the process table. A v2 plan carries both schema `joulewise.night_plan.v2` and integer `schema_version: 2`; a missing or different version is malformed. Only a decoded mapping whose complete key shape exactly matches the golden retired-v1 fixture is ignored, with a `plan_retired_v1` event; a v1 label attached to any v2-only key is not retired evidence. Unreadable JSON holds as `night_plan_unreadable`; an invalid v2 or future authorship holds as `night_plan_malformed`. Each diagnostic is keyed by the activation id and spawn epoch, plan directory, kind, and detail digest, so changed failures and later activations are reported independently. Every spawn mints a fresh activation id and spawn epoch. The watchdog's valid-plan set intentionally contains every plan the night gate could run and may conservatively contain a stale plan the gate would refuse. Inside a valid-v2 plan span the watchdog invokes the exact production `agent_census`; outside a span, an unrelated census hit does not prevent daytime work. A live `magistrate.lock` is validated by both PID and the process's start-time token so PID reuse grants no authority.

The durable states are:

- `BOOT`/`IDLE`: no current decision or a clean activation ended.
- `LAUNCHING`: launch predicates passed and a resident supervisor is being forked.
- `ACTIVE`: the recorded child PID, start time, and activation are live in both `state.json` and `magistrate.lock`. If its prior supervisor disappeared, the next LaunchAgent tick adopts observation of that exact process; it does not spawn a second session.
- `STANDDOWN_REQUESTED`, `STANDDOWN_TERM`, and the terminal `FENCED`/`HOLD_CENSUS`: the resident supervisor executes the request, TERM, KILL, and verification sequence below.
- `FENCED`: a plan span, the 02:45–03:30 belt, or the 07:00 minute forbids launch.
- `HOLD_CENSUS`/`HOLD_UNSAFE`: an in-span census hit, unavailable process table, unreadable or malformed current plan, armed-plan conflict, surviving owned process, or other fail-closed condition forbids launch. Only the exact golden retired-v1 shape is ignored. A resident that observes an unreadable, malformed, future-authored, or conflicting plan records `resident_drain_started` with the reason and irreversibly runs the same nine-minute/TERM/one-minute/KILL ladder. If that supervisor dies, each replacement tick validates and records `resident_adopted`, performs the next due ladder action, and persists the stage for the following tick; no later launch occurs until a fresh tick sees that plan hold clear. Census matches are reported and never used as kill targets.
- `NETWORK_UNCERTAIN`: the positive-control or stop-ref probe was not conclusive; this is not equivalent to a cleared switch.
- `CLOCK_UNCERTAIN`: wall and monotonic deltas disagree by more than 60 seconds (or go backwards). A tick never launches; a resident requests stand-down and completes its nine-minute/TERM/one-minute/KILL drain on monotonic time. Once that conservative drain begins, later sane samples do not cancel it.
- `BACKOFF_USAGE`/`BACKOFF`: a classified usage failure or a generic launch failure is waiting for eligibility. The persisted deadline is a wall-clock epoch paired with the current boot identifier; a different boot discards it and records `backoff_reset_after_reboot`.
- `STOP_REQUESTED`/`STOPPED`: the local file or remote branch has stopped launches; an already-owned child receives a nine-minute cooperative request before TERM and, 60 seconds later, KILL.

Every state transition appends exactly one transition event. Re-evaluating the same state does not append another transition. Census, signal, drain-start, and plan diagnostics are separate typed events. Plan events use `plan_dir` (never the plan-declared `custody_root`) and are de-duplicated only for an identical activation-id/spawn-epoch/plan-directory/kind/detail-digest key.

## Fence and deadlines

All plan arithmetic is epoch seconds. Only the fixed belt and dead-man minute use `datetime.now().astimezone()` local time.

For each valid plan:

1. The plan span begins at the closed boundary `t0 - 25 minutes`.
2. It remains open through the closed completion boundary `t0 + window_max_s + COURIER_DEADLINE_S`.
3. After completion it closes when `night/courier.sent` exists. Without that marker it remains open through the closed boundary `_next_deadman_epoch(t0) + COURIER_LOCK_FRESH_S`.
4. At any time, `chain.started` without `chain.exited` extends the span without a clock limit.
5. During that span the exact production census must be empty before the state can be merely `FENCED`. A nonempty or failed census is `HOLD_CENSUS` and is never killed as an unowned match.

The local fixed fences are half-open: `[02:45:00, 03:30:00)` and `[07:00:00, 07:01:00)`. Equality at the plan-span start, completion, and dead-man-plus-lock-fresh boundaries is unsafe.

Inside either fixed fence, a live PID+start-time-owned session whose resident supervisor is absent remains fenced: the short tick returns `FENCED` with `adopt=False` and does not launch or adopt a supervisor. Re-adoption waits until the fixed fence clears, at most 45 minutes for the belt and at most one minute for the 07:00 fence.

For the earliest relevant parseable plan, the resident supervisor re-reads plans and evaluates its stand-down phase on every poll, including while a clock or unsafe-plan drain is latched. Each drain action is due at the earlier of its cooperative-ladder time and the plan boundary, so REQUEST is no later than `t0 - 25 min`, TERM no later than `t0 - 16 min`, and KILL no later than `t0 - 15 min`. Plan and local-clock enforcement runs before any remote-stop cache lookup, and no network operation runs on this path:

| Boundary | Action |
|---|---|
| `t0 - 25 min` | Atomically create `standdown.request`; the session stops new work, commits and pushes only in worktrees, emails Ed, stops its children, and exits. |
| `t0 - 16 min` | Walk the recorded PID's complete PPID descendant tree until stable and send TERM to every descendant, then the root. |
| `t0 - 15 min` | If still live, repeat the tree walk and send KILL to every descendant, then the root. Never substitute `killpg`. |
| immediately after KILL | Re-check PID+start-time ownership, invoke the production census, and enter `FENCED` only if the owned process is gone and the census is empty; otherwise retain ownership where applicable and write a `HOLD_CENSUS` report. |

The process-tree walk is deliberately independent of process groups because an agent host can escape its parent's PGID. Only descendants of the validated lock PID are signaled. An unrelated census hit is evidence for a hold, never authority to signal.

### Replacement-supervisor drain handoff

Every successful spawn or ordinary supervisor adoption copies the complete owned-session record into `state.json`: PID, exact start-time token, activation, and launch metadata. If an unreadable, malformed, future-authored, or conflicting plan produces `HOLD_UNSAFE` after the resident supervisor has disappeared, the short tick compares that durable PID/start pair with the current process table before doing anything else to the child. A match appends `resident_adopted{pid,start_time,activation}` and executes one bounded drain step. The first such tick atomically creates `standdown.request`, records `resident_drain_started`, and persists `resident_hold_drain.stage = REQUEST`; later launchd ticks reuse the original request timestamps and persist `TERM` and `KILL` as those thresholds become due. They never rewrite the request time or restart the nine-minute allowance.

If the PID is absent or its start token differs, the tick records `already_gone`, clears the durable session identity, and sends no signal. Thus PID reuse cannot inherit either adoption or signal authority. The ordinary 10-second resident loop and replacement-tick recovery share the same `STOP_COOPERATIVE_S = 540` and `STOP_TERM_GRACE_S = 60` ladder; only their polling cadence differs.

## Kill switch

Every launchd tick that acquires the service lock first proves remote transport with anonymous `git ls-remote --exit-code` against `refs/heads/main`, then probes the glob `refs/heads/ops/stop*`. It seeds the resident with that observation. While a child is resident, one daemon thread refreshes the cached observation at most every five minutes; a slow or unreachable GitHub probe never blocks the 10-second enforcement loop, and no second probe begins while one is live. Control rc 0 plus stop rc 2 means clear; a stop match means stopped. Control rc 128, any other nonzero control result, a stop-probe result other than 0/2, timeout, or exception means `NETWORK_UNCERTAIN`, never clear. The commands disable credential helpers and terminal prompts and never fetch or mutate a checkout.

The local switch is `~/night-custody/magistrate/STOP`. It works without GitHub and wins over the remote result. Removing both switches permits a later safe launch; neither switch can rescue a wedged watchdog process, and there is intentionally no watchdog-for-the-watchdog. Because this is a user LaunchAgent, it does not load before GUI login after a reboot; unattended reboot before login is an accepted limitation for this week because Ed's machine stays logged in. Operational liveness is strict: no `state.json` write for more than 15 minutes means the watchdog is dead, and the courier email for the next window must say so.

On GitHub mobile, create a branch named exactly `ops/stop-magistrate` from `main` to stop, and delete that branch to clear. Any branch under the wider `ops/stop*` glob also stops, so a shortened or suffixed emergency name is fail-safe. This width is the magistrate's 2026-09-03 ruling on execution-refuter N2 in `docs/process_traces/2026-09-03-watchdog-build/04-refuter-execution-2b4476cb.md`; it amends the narrower file-15 row-6 text. Do not prune any matching operational branch while it is acting as the switch.

## Exit classification, backoff, and notices

Nonzero output is classified as `usage_exhausted` only by the reviewed case-insensitive signatures for “usage limit”, “spend limit”, “rate limit”/`rate_limit`, exhausted/exceeded quota, a limit/usage reset time, and `HTTP 429`. Unknown nonzero output is generic failure, never optimistically treated as usage exhaustion.

Usage retries are 15, 30, 60, 120, then 120 minutes, plus a deterministic 0–120 second jitter derived from the activation id. A new plan fence always outranks backoff. Generic failures use the closest file-09 ladder (2, 5, 15, 30, then 60 minutes); this file-15-silent selection is recorded as a `lead_ruling` flag in the build report. A forced stand-down or first transition into usage backoff queues one `notice_pending` record. The next successful activation places all pending records in its first email and writes `notice.ack` only after Gmail accepts; the supervisor then clears the delivered records. The watchdog has no independent email credential.

6. Read the verification log from an observer after the magistrate exits. The already-proved launchd path (`docs/process_traces/2026-09-02-hands-free-week/17n-bench-launchd-spawn.md` on main) means the next five-minute tick must create the first watchdog-owned one-turn `-p` magistrate. Verify a new `attempts/<activation>/` and a `magistrate.lock` without `first_install_adoption`; a nonempty census before that tick or absence of the new attempt after it is a failed handoff.

The first real window must not be armed until a reviewed v2 plan pins its measurement checkout and both night agents have been installed FROM that plan's `measurement_root` at `measurement_head`. Rehearsal stubs may follow watchdog installation, with re-arm after any relevant HEAD move, but their documented `/private/tmp/...` measurement roots are deliberately fake and must never be reused by a real plan. Remove every `REHEARSAL_STUB` plan root before arming any real plan. After arming, neither the development checkout nor the measurement checkout may be moved as fenced above. Arming itself remains outside this watchdog's charter and always uses the email-then-arm handback; Ed's NO overrides.

## Bench rehearsal (no real night)

Run the focused checks and create a fake `REHEARSAL_STUB` plan at `t0 = now + 10 minutes` under a fresh temporary custody parent. The Python block prints the exact `t0`; it does not write the repository or the default custody root:
