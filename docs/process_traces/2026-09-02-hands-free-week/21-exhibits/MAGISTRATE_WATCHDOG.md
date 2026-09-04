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

## Complete write inventory

The program guards every write path against the configured custody root. The mechanism creates only:

- `watchdog.lock`: stable advisory service-lock inode.
- `state.json`: atomic durable state, clocks, wall-epoch/boot-identified backoff, activation id and spawn epoch, complete resident-session identity, resident-drain stage, transition sequence, and `notice_pending`.
- `events.jsonl`: fsynced transition, census, signal, resident-drain-start, plan-diagnostic, supervisor-adoption, replacement `resident_adopted`, `already_gone`, and `backoff_reset_after_reboot` events.
- `magistrate.lock`: exclusive launch claim, then the child PID, exact start token, activation id and spawn epoch, symlink path, and version; removed only after the child exit is proved.
- `standdown.request`: atomic request and exact plan deadlines.
- `attempts/<activation>/prompt.md`, `attempt-<n>.stream.jsonl`, and `attempt-<n>.stderr.log`.
- `heartbeat` and an optional unsent-email record, written by the relaunched session under its prompt.
- `notice.ack`, written by the session after its first email is accepted and consumed by the supervisor.
- `launchd.out` and `launchd.err`, written by launchd at paths rendered in the plist.
- Transient atomic replacements named `.<target>.<pid>.<uuid>.tmp` beside any target written through the atomic writer; each is normally replaced into its target after fsync, while a process crash can leave the temporary file for inspection.

No status branch, checkout, plan, night result, `courier.sent`, or repository file is written by the service. The relaunched magistrate remains separately authorized to work in linked worktrees under repository rules; its prompt adds no service write path. At each launch, `@@FENCED_CHECKOUTS@@` is rendered as a deterministic JSON list containing the canonical repository and every authored, not-completed v2 plan's canonical measurement root and head. The prompt forbids Git operations in the canonical root and forbids moving every listed measurement root. Overlapping armed spans at different roots, or one canonical measurement root pinned at two heads, hold as `plan_conflict`; non-overlapping spans at different roots compose and all remain fenced. A post-arm move invalidates the pin and requires a re-arm with a re-pinned plan. Arming also obligates the session to end its loop and exit by the request deadline. The relaunched session may not ratify or amend process rules, decision-log entries, or skill doctrine; rule 11 routes those decisions to the cold gate or Ed.

## Install handoff

Installation is authorized only after the built-artifact gauntlet and cold gate pass. The acting magistrate emails Ed the install notice, quotes the D-171 authorization and the stop instructions above, then follows this checklist without waiting for a reply. Do not arm any plan during this handoff.

1. In the magistrate session, stop every background task and wait for each stop to complete. Repeat the session's background-task listing until it is empty; do not proceed while any Codex child, task, monitor, or background shell remains active.

2. Preserve the two retired-v1 custody trees below a directory the watchdog's one-level plan glob cannot reach:

   ```zsh
   mkdir -p "$HOME/night-custody/retired-v1"
   for name in rehearsal-20260902 rehearsal-20260903; do
     test -d "$HOME/night-custody/$name"
     test ! -e "$HOME/night-custody/retired-v1/$name"
     mv "$HOME/night-custody/$name" "$HOME/night-custody/retired-v1/$name"
   done
   ```

3. First `cd /Users/edr/code/JouleWise`, the canonical checkout, then from the Terminal-hosted interactive magistrate record the exact handoff inventory. The read-only helper places the interactive twin and its ancestry-closed descendants in `owned`; PPID-1 command-shape matches and their descendants are only `unclassified_candidates`. It excludes the helper's transient call chain and rejects a headless `claude -p` ancestor. Inspect every candidate. Promote one only by repeating the command with its exact `--adopt-pid P --start T`; that explicit adoption and its descendants then appear in `owned` with provenance. Keep PID, start-time, command, and provenance together so PID reuse can be rejected:

   ```zsh
   cd /Users/edr/code/JouleWise
   handoff_epoch="$(date +%s)"
   handoff_file="$HOME/night-custody/magistrate/handoff-$handoff_epoch.json"
   mkdir -p "$HOME/night-custody/magistrate"
   scripts/magistrate_watchdog.py handoff-inventory > "$handoff_file"
   python3 -m json.tool "$handoff_file"
   # Only after explicit operator classification, if a candidate is truly owned:
   scripts/magistrate_watchdog.py handoff-inventory \
     --adopt-pid "$candidate_pid" --start "$candidate_start" > "$handoff_file"
   ```

4. Install from that same magistrate session and canonical checkout. The installer refuses any other resolved script repository or Git top level, renders the literal canonical checkout into both plist paths, and pins the installing `python3` process's absolute `sys.executable`. It seeds `magistrate.lock` with the interactive twin's PID and start token so the first resident observes it instead of launching a second session:

   ```zsh
   scripts/install_magistrate_watchdog.sh --install
   python3 -m json.tool "$HOME/night-custody/magistrate/magistrate.lock"
   ```

   If the exclusive lock seed fails, the installer removes the plist written by that attempt. Inspect the existing lock and remove it only after confirming that its PID/start owner is not live; then repeat the whole install step.

5. Have the magistrate start this detached, non-agent reaper. It imports the installed implementation from the recorded absolute checkout, revalidates each `(pid,start_time)` immediately before each signal, signals only `owned` with the interactive root last, waits the full `STOP_COOPERATIVE_S`, re-snapshots after TERM and KILL, and requires every recorded pair absent independently of the final census. Absence is success; a changed start token is PID reuse and is skipped. The watchdog never signals an unclassified or census PID. The final JSON receipt records every per-PID outcome, survivor, census, and verdict:

   ```zsh
   watchdog_checkout="$(/usr/bin/git rev-parse --show-toplevel)"
   /usr/bin/nohup /usr/bin/python3 - "$handoff_file" "$watchdog_checkout" > "$handoff_file.verify.log" 2>&1 <<'PY' &
   import json
   import os
   import signal
   import subprocess
   import sys
   import time
   from pathlib import Path

   checkout = str(Path(sys.argv[2]).resolve(strict=True))
   sys.path.insert(0, checkout)
   from scripts.magistrate_watchdog import STOP_COOPERATIVE_S, production_census

   inventory = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
   owned = inventory["owned"]
   expected = {row["pid"]: row["start_time"] for row in owned}
   root = inventory["interactive_pid"]
   ordered = [row["pid"] for row in owned if row["pid"] != root] + [root]
   outcomes = {str(pid): "recorded" for pid in ordered}

   def snapshot():
       result = subprocess.run(
           ("/bin/ps", "-axo", "pid=,ppid=,lstart=,command="),
           check=True, capture_output=True, text=True,
       )
       rows = {}
       for line in result.stdout.splitlines():
           parts = line.strip().split(None, 7)
           if len(parts) == 8:
               rows[int(parts[0])] = " ".join(parts[2:7])
       return rows

   def signal_matching(pid, signum):
       observed = snapshot().get(pid)
       if observed is None:
           outcomes[str(pid)] = "already_gone"
           return
       if observed != expected[pid]:
           outcomes[str(pid)] = "reused_skipped"
           return
       try:
           os.kill(pid, signum)
       except ProcessLookupError:
           outcomes[str(pid)] = "already_gone"
       else:
           outcomes[str(pid)] = "term_sent" if signum == signal.SIGTERM else "kill_sent"

   for pid in ordered:
       signal_matching(pid, signal.SIGTERM)
   after_term = snapshot()
   time.sleep(STOP_COOPERATIVE_S)
   for pid in ordered:
       signal_matching(pid, signal.SIGKILL)
   after_kill = snapshot()

   deadline = time.monotonic() + 30
   while True:
       final_snapshot = snapshot()
       survivors = [pid for pid, start in expected.items()
                    if final_snapshot.get(pid) == start]
       if not survivors or time.monotonic() >= deadline:
           break
       time.sleep(1)
   for pid in survivors:
       outcomes[str(pid)] = "survivor"
   for pid, start in expected.items():
       if pid not in survivors and outcomes[str(pid)] == "term_sent":
           outcomes[str(pid)] = "termed"
       elif pid not in survivors and outcomes[str(pid)] == "kill_sent":
           outcomes[str(pid)] = "killed"
   census = production_census()
   verdict = "pass" if not survivors and census.empty else "fail"
   print(json.dumps({
       "schema": "joulewise.magistrate_handoff_receipt.v1",
       "checkout": checkout,
       "owned": owned,
       "outcomes": outcomes,
       "after_term": {str(pid): after_term.get(pid) for pid in expected},
       "after_kill": {str(pid): after_kill.get(pid) for pid in expected},
       "survivors": survivors,
       "census": census.__dict__,
       "verdict": verdict,
   }, sort_keys=True), flush=True)
   raise SystemExit(0 if verdict == "pass" else 4)
   PY
   disown
   ```

6. Read the verification log from an observer after the magistrate exits. The already-proved launchd path (`docs/process_traces/2026-09-02-hands-free-week/17n-bench-launchd-spawn.md` on main) means the next five-minute tick must create the first watchdog-owned one-turn `-p` magistrate. Verify a new `attempts/<activation>/` and a `magistrate.lock` without `first_install_adoption`; a nonempty census before that tick or absence of the new attempt after it is a failed handoff.

The first real window must not be armed until a reviewed v2 plan pins its measurement checkout and both night agents have been installed FROM that plan's `measurement_root` at `measurement_head`. Rehearsal stubs may follow watchdog installation, with re-arm after any relevant HEAD move, but their documented `/private/tmp/...` measurement roots are deliberately fake and must never be reused by a real plan. Remove every `REHEARSAL_STUB` plan root before arming any real plan. After arming, neither the development checkout nor the measurement checkout may be moved as fenced above. Arming itself remains outside this watchdog's charter and always uses the email-then-arm handback; Ed's NO overrides.

## Bench rehearsal (no real night)

Run the focused checks and create a fake `REHEARSAL_STUB` plan at `t0 = now + 10 minutes` under a fresh temporary custody parent. The Python block prints the exact `t0`; it does not write the repository or the default custody root:

```sh
tmp_root="$(mktemp -d "${TMPDIR:-/tmp}/magistrate-watchdog.XXXXXX")"
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_magistrate_watchdog -v
scripts/install_magistrate_watchdog.sh --render-only "$tmp_root/render"
/usr/bin/plutil -lint "$tmp_root/render/com.joulewise.magistrate.plist"
BENCH_CUSTODY="$tmp_root/custody" python3 - <<'PY'
import os
import time
from pathlib import Path

from joulewise.night_gate import NightPlan
from joulewise.night_plan_writer import write_night_plan

custody = Path(os.environ["BENCH_CUSTODY"])
plan_root = custody / "fake-night"
plan_root.mkdir(parents=True)
now = time.time()
t0 = now + 10 * 60
plan = NightPlan(
    plan_id="watchdog-bench-now-plus-10m",
    receipt_class="REHEARSAL_STUB",
    t0_epoch_s=t0,
    window_max_s=600,
    authored_epoch_s=now,
    repo_head="0" * 40,
    measurement_root="/private/tmp/joulewise-watchdog-bench-fake-measurement",
    measurement_head="0" * 40,
    chain_path=str(plan_root / "chain.sh"),
    chain_sha256_path=str(plan_root / "chain.sh.sha256"),
    custody_root=str(plan_root),
    registration_path=str(plan_root / "registration.json"),
)
write_night_plan(plan_root / "night_plan.json", plan)
print(f"t0_epoch_s={t0:.6f}")
PY
MAGISTRATE_WATCHDOG_CUSTODY_ROOT="$tmp_root/custody/magistrate" \
  PYTHONDONTWRITEBYTECODE=1 scripts/magistrate_watchdog.py --dry-run
test ! -e "$tmp_root/custody/magistrate"
```

At the first instant, `now = t0 - 10 minutes`, so the plan span is already closed against launch. With the implementing/reviewing agent still live, the exact expected decision is `HOLD_CENSUS`; on an agent-free bench it is `FENCED`. In both cases the transcript must end in `WOULD_SPAWN none`, every mutation is printed only as `WOULD_WRITE`, and the final `test` proves no custody root was created. At `t0 - 25 minutes` an owned resident would enter `STANDDOWN_REQUEST`; at `t0 - 16 minutes`, `STANDDOWN_TERM`; and at `t0 - 15 minutes`, KILL followed by `FENCED` only when ownership and the production census are empty. Those three exact boundary instants are injected and pinned by `test_plan_fence_boundaries_request_term_kill_and_completion` and the resident supervisor tests.

The no-TTY spawn bench is already recorded, including the exact argv and four stream-json records, in `docs/process_traces/2026-09-03-watchdog-build/02-bench-headless-spawn.md`. To replay it without a TTY, from the canonical checkout run this bounded command; it starts one real print-mode session, so run it only in the magistrate-authorized bench:

```sh
NO_TTY_OUT="$tmp_root/no-tty.stream.jsonl" NO_TTY_ERR="$tmp_root/no-tty.stderr" \
python3 - <<'PY'
import os
import subprocess
from pathlib import Path

prompt = "Reply with exactly the single word OK and nothing else. Do not use any tool."
argv = [
    "/Users/edr/.local/bin/claude", "-p", prompt,
    "--output-format", "stream-json", "--verbose",
    "--permission-mode", "auto", "--permission-prompts", "none",
    "--model", "fable", "--effort", "low", "--allowedTools",
    "Read,Glob,Grep,Bash,Edit,Write,Agent,Task,Skill,ScheduleWakeup,SendMessage,ListAgents,TaskCreate,TaskUpdate,TaskList,mcp__claude_ai_Gmail__send_message,mcp__codex__codex,mcp__codex__codex-reply",
    "-n", "watchdog-argv-bench",
]
with Path(os.environ["NO_TTY_OUT"]).open("wb") as out, Path(os.environ["NO_TTY_ERR"]).open("wb") as err:
    result = subprocess.run(
        argv, cwd="/Users/edr/code/JouleWise", stdin=subprocess.DEVNULL,
        stdout=out, stderr=err, start_new_session=True, timeout=240, check=False,
    )
raise SystemExit(result.returncode)
PY
grep -F '"text":"OK"' "$tmp_root/no-tty.stream.jsonl"
grep -F '"stop_reason":"end_turn"' "$tmp_root/no-tty.stream.jsonl"
test ! -s "$tmp_root/no-tty.stderr"
```

Expected: exit 0, one assistant `OK`, terminal `end_turn`, no permission prompt or stderr. Preserve the output with the bench record; do not install if any expectation differs.

The first-tree adoption rehearsal is a separate, lead-controlled install gate. Its named twin is the **Terminal-hosted interactive magistrate session plus the `claude daemon` and all spares it parents**. In an observer Terminal, capture the exact production census and tree before install:

```sh
python3 - <<'PY'
from scripts.magistrate_watchdog import production_census
print(production_census())
PY
/bin/ps -axo pid=,ppid=,lstart=,command= | grep -E '[c]laude|[c]odex|[t]3'
```

Expected before: `empty=False`, with the Terminal-hosted interactive root, its `claude daemon`, and its spares visible. From that interactive magistrate session—not from the observer—run the authorized installation, then inspect the exclusive adoption record from the observer:

```sh
scripts/install_magistrate_watchdog.sh --install
python3 -m json.tool "$HOME/night-custody/magistrate/magistrate.lock"
```

Expected lock: `first_install_adoption=true`; its PID/start token names the Terminal-hosted interactive root, and the first `supervisor_adopted` event names the same activation without a second launch. Arm only a reviewed `REHEARSAL_STUB` so its first stand-down exercises that tree. The cooperative request should make the interactive session stop its children and exit; if ignored, the resident must TERM every validated descendant at `t0 - 16 minutes` and KILL survivors at `t0 - 15 minutes`. After the stand-down, rerun the observer commands above. Expected after: `CensusObservation(empty=True, ...)`, no Terminal-hosted twin, no `claude daemon`, no spares, `magistrate.lock` absent, and a final `FENCED` transition. Any survivor is `HOLD_CENSUS` and fails the rehearsal. Do not arm a real window until this before/after record passes review.

After the lock and adoption event pass inspection, the exact rehearsal arm below sets `t0 = now + 26 minutes`: the request is due about one minute later, TERM about ten minutes later, and KILL about eleven minutes later. Run it only with the observer recording and after the lead authorizes this destructive twin stand-down:

```sh
ADOPTION_PLAN_ROOT="$HOME/night-custody/watchdog-adoption-rehearsal" python3 - <<'PY'
import json
import os
import time
from pathlib import Path

from joulewise.night_gate import NightPlan
from joulewise.night_plan_writer import write_night_plan

root = Path(os.environ["ADOPTION_PLAN_ROOT"])
root.mkdir(parents=True, exist_ok=False)
now = time.time()
plan = NightPlan(
    plan_id="first-tree-adoption-rehearsal",
    receipt_class="REHEARSAL_STUB",
    t0_epoch_s=now + 26 * 60,
    window_max_s=60,
    authored_epoch_s=now,
    repo_head="0" * 40,
    measurement_root="/private/tmp/joulewise-watchdog-adoption-fake-measurement",
    measurement_head="0" * 40,
    chain_path=str(root / "chain.sh"),
    chain_sha256_path=str(root / "chain.sh.sha256"),
    custody_root=str(root),
    registration_path=str(root / "registration.json"),
)
write_night_plan(root / "night_plan.json", plan)
print(json.dumps({"plan_id": plan.plan_id, "t0_epoch_s": plan.t0_epoch_s}))
PY
```
