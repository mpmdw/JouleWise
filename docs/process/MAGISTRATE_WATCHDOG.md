# Magistrate relaunch watchdog

`com.joulewise.magistrate` is a user LaunchAgent that evaluates a short Python tick at load and every 300 seconds. A safe tick forks a new session and leaves a resident supervisor running at 10-second resolution. The service never writes a repository tree. Its default mutable root is `~/night-custody/magistrate/`; `MAGISTRATE_WATCHDOG_CUSTODY_ROOT` or `--custody-root` may replace that root for a rehearsal.

## Safety model and state machine

The tick reads every sibling `*/night_plan.json` with the production `NightPlan.from_mapping`, the associated `night/chain.started`, `night/chain.exited`, and `night/courier.sent` markers, the local service state and locks, the local `STOP` file, the remote stop refs, local civil time, monotonic time, and the process table. Inside a plan span it invokes the exact production `agent_census`; outside a span, an unrelated census hit does not prevent daytime work. A live `magistrate.lock` is validated by both PID and the process's start-time token so PID reuse grants no authority.

The durable states are:

- `BOOT`/`IDLE`: no current decision or a clean activation ended.
- `LAUNCHING`: launch predicates passed and a resident supervisor is being forked.
- `ACTIVE`: the recorded child PID and start time are live. If its prior supervisor disappeared, the next LaunchAgent tick adopts observation of that exact process; it does not spawn a second session.
- `STANDDOWN_REQUESTED`, `STANDDOWN_TERM`, and the terminal `FENCED`/`HOLD_CENSUS`: the resident supervisor executes the request, TERM, KILL, and verification sequence below.
- `FENCED`: a plan span, the 02:45–03:30 belt, or the 07:00 minute forbids launch.
- `HOLD_CENSUS`/`HOLD_UNSAFE`: an in-span census hit, malformed plan, unavailable process table, surviving owned process, or other fail-closed condition forbids launch. Census matches are reported and never used as kill targets.
- `NETWORK_UNCERTAIN`: the positive-control or stop-ref probe was not conclusive; this is not equivalent to a cleared switch.
- `CLOCK_UNCERTAIN`: wall and monotonic deltas disagree by more than 60 seconds (or go backwards). Launch remains held until two consecutive sane samples.
- `BACKOFF_USAGE`/`BACKOFF`: a classified usage failure or a generic launch failure is waiting for eligibility.
- `STOP_REQUESTED`/`STOPPED`: the local file or remote branch has stopped launches; an already-owned child receives a nine-minute cooperative request before TERM and, 60 seconds later, KILL.

Every state transition appends exactly one transition event. Re-evaluating the same state does not append another transition. Census and signal observations are separate typed events.

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

For the earliest relevant plan, the resident supervisor re-reads plans at most every 10 seconds and enforces:

| Boundary | Action |
|---|---|
| `t0 - 25 min` | Atomically create `standdown.request`; the session stops new work, commits and pushes only in worktrees, emails Ed, stops its children, and exits. |
| `t0 - 16 min` | Walk the recorded PID's complete PPID descendant tree until stable and send TERM to every descendant, then the root. |
| `t0 - 15 min` | If still live, repeat the tree walk and send KILL to every descendant, then the root. Never substitute `killpg`. |
| immediately after KILL | Re-check PID+start-time ownership, invoke the production census, and enter `FENCED` only if the owned process is gone and the census is empty; otherwise retain ownership where applicable and write a `HOLD_CENSUS` report. |

The process-tree walk is deliberately independent of process groups because an agent host can escape its parent's PGID. Only descendants of the validated lock PID are signaled. An unrelated census hit is evidence for a hold, never authority to signal.

## Kill switch

Every poll first proves remote transport with anonymous `git ls-remote --exit-code` against `refs/heads/main`, then probes the glob `refs/heads/ops/stop*`. Control rc 0 plus stop rc 2 means clear; a stop match means stopped. Control rc 128, any other nonzero control result, a stop-probe result other than 0/2, timeout, or exception means `NETWORK_UNCERTAIN`, never clear. The commands disable credential helpers and terminal prompts and never fetch or mutate a checkout.

The local switch is `~/night-custody/magistrate/STOP`. It works without GitHub and wins over the remote result. Removing both switches permits a later safe launch; neither switch can rescue a wedged watchdog process, and there is intentionally no watchdog-for-the-watchdog.

On GitHub mobile, create a branch named exactly `ops/stop-magistrate` from `main` to stop, and delete that branch to clear. Any branch under the wider `ops/stop*` glob also stops, so a shortened or suffixed emergency name is fail-safe. Do not prune any matching operational branch while it is acting as the switch.

## Exit classification, backoff, and notices

Nonzero output is classified as `usage_exhausted` only by the reviewed case-insensitive signatures for “usage limit”, “spend limit”, “rate limit”/`rate_limit`, exhausted/exceeded quota, a limit/usage reset time, and `HTTP 429`. Unknown nonzero output is generic failure, never optimistically treated as usage exhaustion.

Usage retries are 15, 30, 60, 120, then 120 minutes, plus a deterministic 0–120 second jitter derived from the activation id. A new plan fence always outranks backoff. Generic failures use the closest file-09 ladder (2, 5, 15, 30, then 60 minutes); this file-15-silent selection is recorded as a `lead_ruling` flag in the build report. A forced stand-down or first transition into usage backoff queues one `notice_pending` record. The next successful activation places all pending records in its first email and writes `notice.ack` only after Gmail accepts; the supervisor then clears the delivered records. The watchdog has no independent email credential.

## Complete write inventory

The program guards every write path against the configured custody root. The mechanism creates only:

- `watchdog.lock`: stable advisory service-lock inode.
- `state.json`: atomic durable state, clocks, backoff, activation, transition sequence, and `notice_pending`.
- `events.jsonl`: fsynced transition, census, signal, and supervisor-adoption events.
- `magistrate.lock`: exclusive launch claim, then the child PID, exact start token, activation, symlink path, and version; removed only after the child exit is proved.
- `standdown.request`: atomic request and exact plan deadlines.
- `attempts/<activation>/prompt.md`, `attempt-<n>.stream.jsonl`, and `attempt-<n>.stderr.log`.
- `heartbeat` and an optional unsent-email record, written by the relaunched session under its prompt.
- `notice.ack`, written by the session after its first email is accepted and consumed by the supervisor.
- `launchd.out` and `launchd.err`, written by launchd at paths rendered in the plist.

No status branch, checkout, plan, night result, `courier.sent`, or repository file is written by the service. The relaunched magistrate remains separately authorized to work in linked worktrees under repository rules.

## Install handoff

Installation is authorized only after the built-artifact gauntlet and cold gate pass. The acting magistrate emails Ed the install notice, quotes the D-171 authorization and the stop instructions above, then installs without waiting for a reply. The installer must be run from that magistrate session: it walks its own ancestry, records the highest owning session process with PID+start time in `magistrate.lock`, and refuses installation when it cannot identify that tree.

That seeded lock is the one-time file-15 row-10 exception. The first resident supervisor adopts the current Terminal-hosted magistrate tree, including its descendants, instead of launching a second magistrate. At the first stand-down, the cooperative path is preferred; if necessary the same PPID-tree TERM/KILL enforcement reaches the interactive twin and the daemon/spares within its ruled owned tree. After it exits, every later owned magistrate begins as the watchdog's one-turn `-p` child.

The first real window must not be armed until plans pin the measurement checkout and the night agents are installed from it. Rehearsal stubs may follow watchdog installation, with re-arm after any relevant HEAD move. Arming itself remains outside this watchdog's charter and always uses the email-then-arm handback; Ed's NO overrides.

## Bench rehearsal (no real night)

Run all rehearsal outputs under a fresh temporary directory, never under the repository, `~/Library/LaunchAgents`, or the default custody root:

```sh
tmp_root="$(mktemp -d "${TMPDIR:-/tmp}/magistrate-watchdog.XXXXXX")"
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_magistrate_watchdog -v
scripts/install_magistrate_watchdog.sh --render-only "$tmp_root/render"
/usr/bin/plutil -lint "$tmp_root/render/com.joulewise.magistrate.plist"
MAGISTRATE_WATCHDOG_CUSTODY_ROOT="$tmp_root/custody/magistrate" scripts/magistrate_watchdog.py --dry-run
```

Before an actual install, also run the owed launchd/no-TTY `-p` bench using only a temporary LaunchAgent and temporary custody. Record heartbeat-before-email, stream-json completion, prompt-denial behavior under `--permission-mode auto`, the post-exit production census, and whether `--permission-prompts none` is required. Do not install until those observables and the row-10 first-tree adoption have passed review.
