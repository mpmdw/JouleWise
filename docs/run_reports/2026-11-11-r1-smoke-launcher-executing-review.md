# Executing review: agent-free R1 follow-up smoke launcher (2026-11-11)

Reviewer: Opus 5.5, independent executing cold seat (not the author; Sol built the branch). Target
`ops/2026-11-11-r1-smoke-launcher` @ `ff6cd1756`, base `9b4817f36`. Sol's report:
`docs/run_reports/2026-11-11-r1-smoke-launcher.md`. Motivation read first:
`docs/process_traces/2026-11-11-r1-followup-smoke/MAGISTRATE-REFUSAL-aa8a5a95.md` on `origin/main`. No code was changed.

**Blinding and host safety.** Code, rulings and synthetic fixtures only. No Block 6, BYTES held-out or v4 outcome
path was opened. No real host-setting command ran: every run imported the test host-command guard, every
`pmset`, `sudo`, `launchctl`, `pgrep`, `mount` and `diskutil` call went to a fake, and the fake host logged no
unexpected command. The only real external commands were `git` (condition 13 reads committed blobs) and `/bin/ps`
(read-only orphan census). `scripts/test_timings.json` was not touched.

**How it was run.** Worktrees `/Volumes/JW-EXT/jw-wt/rev-r1-launcher` (head), `...-base` (base) and `...-merge`
(trial merge and in-place mutant sandbox), all removed afterwards. `TMPDIR=/Volumes/JW-EXT/scratch/rev-r1-launcher`,
`nice -n 10 python3.13 -B`, one module at a time. The Air ran at load average about 86 on 10 cores throughout, so
wall times are not timing evidence and the 8 s fixture timeouts in the desk-fence suite flaked (see Tests).

## Verdict: ADMIT-WITH-FIXES. Do not use until H-1 is fixed.

The agent-free handoff, the feed wiring, the stop rules, the cleanup and the bindings are sound. I exercised them end
to end through the real launcher, the unchanged shell wrapper, a synthetic launchd and the real runner source with
every host interaction faked. All 19 injected failures behaved as specified except one (M-1), and all 9 mutants
were killed. R0 is unchanged: its runner spec and plist are byte-identical at base and head.

One defect is blocking:

- **H-1. The runner caps Part B at 1,800 s.** Part B legitimately needs up to about 4,400 s plus close: a fresh
  admission of up to 1,800 s, then the post-G0 watchdog of 2,600 s. As written, the runner will kill almost any real
  Part B partway through its D step, so the smoke could never deliver the Part B coverage and selection table.

Three findings are MEDIUM. M-1: the Automatic restore runs on every exit and ignores a foreign W1 high-power
marker. M-2: the 60 s volume census during capture is not night practice. M-3: there is a known merge conflict with
presign in `hazard_refusals.json`. The LOW items are hygiene. With H-1 fixed, the minimum fence deadline is about
7,450 s, so the 7,200 s in Sol's report is too short. **Use 9,000 s.**

## (a) R0 is unchanged

- **Bytes.** I ran `launch` at base and head with the same arguments, a fixed UUID and a fake `launchctl` that
  refuses `bootstrap`, so the job directory stays behind. I then compared the job's `runner.json` and plist after
  normalising the temp root and the PID. Both default R0 (`--keep-going`) and `--checks smc,battery --no-keep-going`
  give **identical `runner.json` and identical plist bytes** at base and head. Script:
  `scratch/rev-r1-launcher/r0eq/r0eq.py`.
- **Behaviour (code reading).** The R0 branch of `run_until_deadline` still does `sleep_display`, `time.sleep(dwell)`,
  the deadline re-check, `Popen(runner, env={…DISPLAY_PREP_ENV…})` and `wait(timeout=remaining)`. The terminate wait
  is still `5` s for R0 (`R1_CLEANUP_GRACE_S if r1_smoke else 5`). The fence lifecycle (`launch`/`handoff`/`clear`
  and the shell wrapper) is unchanged; the shell is byte-identical. There are two harmless differences. The spec is
  now parsed once before the dwell, so a malformed spec refuses (rc 2) without dwelling. `--config` is no longer
  argparse-required, and a missing R0 config now refuses in `launch()` with rc 2 before any fence is published.
- **Tests.** `tests.test_magistrate_desk_fence` gave 42 tests at both base and head, with 3 and 5 failures
  respectively. All of them were `wait_for` 8 s timeouts or "R0 desk deadline already passed" on a 13 s deadline,
  caused by load. I re-ran all 7 failing tests in isolation at head: 6 pass. The remaining one,
  `test_spotlight_resumes_and_runner_is_reaped_before_deadline` (deadline `now+13`), fails the same way at base.
  `tests.test_magistrate_watchdog` (158 tests) has one error at both base and head: the merge-commit digest test hits
  a subprocess timeout under load, and it is the same at both.

## (b) Agent-free

- Nothing in the r1-smoke path runs before `handoff` returns. `launch` only writes the fence and plist and
  bootstraps; the wrapper's first action is `handoff`, which waits until the magistrate PID is gone. It then runs
  `preflight`, Spotlight STOP and `run`. The runner, and with it the meter, censuses and parts, exists only after
  that. This is the same shell and the same handoff as R0.
- **Synthetic witness.** In every scenario the harness kept the stand-in magistrate alive for 2 to 4 s after launch,
  recorded the exit time, and then checked the runner's first host probe and its `start-meter` step. Every
  non-mutant run had all of them after the exit (`output_before_magistrate_exit: false`). M1 (skip the wait) and M2
  (no wait on the handoff in the shell) both put the probes and meter start 0.2 to 1.8 s **before** the magistrate
  exited, and the harness flagged both. If the magistrate never exits (`--exit-wait-seconds 5`), the handoff times
  out: there is no output directory, no part runs, the fence is cleared and the job is unloaded.
- **Dwell.** The launcher skips its own sleep and dwell for R1. The runner does `read_power` → `display`
  (`launcher.sleep_display`) → `dwell` (`launcher.display_dwell_seconds()`, 300 s, polling the feeds) → Part A.
  The synthetic receipt timeline (dwell seam set to 3 s) has the feeds at 0.22 to 0.45 s, display at 0.45 to 0.60 s,
  dwell at 0.60 to 3.61 s, then Part A starting at 3.61 s. The measured dwell was 3.005 s. M7 (skip dwell) is killed.
  The production LaunchAgent env carries only PATH and LC_ALL, so the dwell test seam cannot leak into a real run.
- The runner's agent census (`[c]odex|[c]laude`, own tree excluded, ancestors judged by executable) runs at feed
  start and every 30 s through dwell and both parts. A wrong `MAGISTRATE_PID` therefore still refuses before Part A
  (F-agent-present, F-agent-during-dwell). The meter does start about 0.2 s before that first census (L-8).

## (c) Feeds use the night's code paths

- **KM003C.** `driver.production_seams(ROOT).meter_argv(MonitorRequest(...))`, which is the same function the
  HAZARD driver calls (`driver.py:2602-2607`). The synthetic run captured the real argv:
  `[<python>, -B, <repo>/scripts/km003c_monitor.py, --out, <OUT>/hazards/meter/stream-001.jsonl]`. That is the same
  plain-QoS monitor, the same create-once stream naming, and the DC-in meter the night records. The supervisor is
  `driver.MonitorSupervisor(name=METER_NAME)` with the default `restart_on_clean_exit=True`, as the night sets
  explicitly. Readiness uses `driver.await_meter_ready` + `MeterLiveness`, so a fresh sample batch is required; this
  is stricter than the night, which only probes at arm. With a meter that never streams (F-meter-no-dcin), the
  supervisor restarted it, journaled `crash_loop`, refused with "no fresh DC-in sample batch" and left no orphan. The
  supervisor differs from the night's in one respect: `identity=` is not passed (L-5).
- **Agent census.** `run_night.agent_census` (= `night_gate.agent_census`, `own_tree_root=os.getpid()` as in
  `driver.HazardCensus`) and `run_night._append_census`, on `CENSUS_INTERVAL_S` = 30 s. The journal row format is
  the night's.
- **Volume census.** `align_r1_rehearsal.VolumeWatch.census` → `external_volume.census` + `arm_check` (status
  `off`), which is the R1 driver's code. The cadence is not the night's (M-2).
- All three are cooperative producers in the runner's loop and spawn no process of their own beyond the bounded
  probe subprocesses. Synthetic receipts show `meter_supervision.jsonl`, the streams, `censuses.jsonl` and
  `volume_censuses.jsonl`, with post-stop SHA-256 values that Sol's receipt-check snippet verified.

## (d) Order, stop rules, cleanup: injected failures

Each row is one full synthetic handoff: the real launcher and shell, a fake launchd, the real runner source, and
faked hosts. Every row had a receipt, the restore step and all three feed stops, no owned meter or part PID alive,
no process naming the fixture root alive, the fence removed and the service unloaded.

| Injection | Stopped at | rc | Parts run | Notes |
|---|---|---|---|---|
| Battery power | `ac_power` | 2 | none | no meter started |
| `com.joulewise.night.align-r1` loaded | `night_agents` | 2 | none | no meter started |
| Condition-13 drift (thermal_gates blob) | `condition13` | 2 | none | real `verify_r1_executed_sources`; passes at HEAD |
| Soak file removed | `soak_reference` | 2 | none | |
| Meter never streams | `start-meter` | 2 | none | 5 streams, crash_loop journaled |
| Agent present at start | `start-agents` | 2 | none | |
| External volume (smbfs) | `start-volumes` | 2 | none | |
| AC powermode 2 | `read_power` | 2 | none | no display sleep |
| Agent appears during dwell | `dwell` | 2 | none | |
| Part A exits 3 | `part-A` | 3 | A only | B never started; A's rc preserved |
| Part B exits 4 | `part-B` | 4 | A, B | |
| Part A over its cap (cap 3 s) | `part-A` | 2 | A only | group torn down |
| SIGTERM to the job during A | `part-A` | 143 | A only | full cleanup, receipt written |
| Restore setter fails | `restore` | 2 | A, B | later feed stops still ran |
| Host night lock held by another | `restore` | 2 | A, B | **no** `sudo pmset` issued |
| Work deadline (fence now+395 s) | `part-A` | 2 | A only | text misleading (L-3) |
| Magistrate never exits | handoff | n/a | none | no output dir; fence cleared |
| Part leaves a same-group child | — | 0 | A, B | child killed by group proof |
| **Foreign W1 marker + night agent** | `night_agents` | 2 | none | **`sudo pmset -c powermode 0` issued (M-1)** |
| Part B longer than the cap (scaled: cap 4 s, B 6 s) | `part-B` | 2 | A, B | **demonstrates H-1** |

No retry or extension path exists. The only loop is over `("A", "B")` with `step(..., fatal=True)`.

## (e) Deadline arithmetic

The runner stops work at `deadline − 370 s` (`WORK_RESERVE_S = 2×180+10`). Its own cleanup bound is part-group
proof ≤ 70 s, restore ≤ 30 s (sudo 10 s plus a read with one retry, 2×10 s), and meter stop ≤ 22 s, plus a
normally instant group re-proof. That is about 125 s, inside the 180 s before the outer `wait` times out at
`deadline − 190 s`. The outer launcher then allows another 180 s of TERM grace before KILL at `deadline − 10 s`.
The reserve is adequate.

The parts' own caps:

- **Part A.** The kit enforces 1,800 s from its own `started` (admission plus close). The runner's 1,800 s also
  counts kit start-up, including its condition-13 re-check (L-2).
- **Part B** is a fresh run: predecessor + G0 ≤ 1,800 s (`r1_runtime.py:1679-1682`), then the post-G0 watchdog of
  quiet 300 + re-armed turn 1,580 + recovery 600 + close 120 = **2,600 s** (`r1_runtime.py:113-119, 1687-1691`;
  RL-84 P-5; kit report F-4). Its legitimate worst case is therefore about 4,400 s plus the kit's table step. The
  runner gives it `min(PART_LIMIT_S=1800, work_remaining)` (H-1).

The minimum fence deadline is the sum of: magistrate exit ≤ 180 (`--exit-wait-seconds`), launcher preflight and
Spotlight ≈ 30, runner preflight and feed start ≤ 120 (generous: up to 15 s per probe, 20 s meter readiness, volume
census), dwell 300, Part A, Part B, and the 370 s reserve.

- **As written:** 180+30+120+300+1,800+1,800+370 = **4,600 s**. The report's 7,200 s covers this, but the code
  as written truncates Part B.
- **After the H-1 fix** (A cap 1,920 = 1,800+120; B cap 4,520 = 1,800+2,600+120):
  180+30+120+300+1,920+4,520+370 = **7,440 s**. **Use `DEADLINE = now + 9000`** for about 1,500 s of slack. That is
  well under `MAX_DESK_SECONDS` (12 h). The watchdog stays fenced only until the job clears its fence, not for the
  whole 9,000 s.

## (f) Mutants (executed in the end-to-end harness)

Each mutant ran through the real launcher, shell, fake launchd and runner. Launcher and shell mutants were applied
to copies in the fixture root; runner mutants were applied to the runner source at exec time. None was committed.

| # | Mutant | Result | Witness |
|---|---|---|---|
| M1 | Skip the magistrate wait (`while pid_alive(...)` → `while False`) | KILLED | first host probe and meter start 1.0 to 1.8 s before the magistrate exit |
| M2 | Start the runner and meter before the wait completes (drop the shell's `wait` on handoff) | KILLED | probes 1.1 s before exit |
| M3 | Run B after A fails (`step("part-"+which, run_part, fatal=False)`, A rc 3) | KILLED | "Part B ran after Part A failed" (receipt rc also became 0) |
| M4 | Skip the restore | KILLED | no `restore` step, no setter call |
| M5a | Leak the meter (skip supervisor stop and group proof) | KILLED | meter PID alive afterwards |
| M5b | Leak a census process (census helper spawned per feed, never stopped) | KILLED | 2 fixture-rooted processes alive |
| M5c | Leak the part group (`proven = True` for the part) | KILLED | same-group child alive |
| M6 | Drop the receipt | KILLED | no `runner_receipt.json` |
| M7 | Skip the dwell | KILLED | Part A started without a completed dwell |

Sol's own in-module mutant suite (11 mutants) also passes as part of `tests.align.test_r1_smoke_launcher`.
**Note (L-7):** I applied M1 in place in a scratch worktree, and Sol's R1 end-to-end test
(`test_real_launchagent_handoff_runs_engine_and_cleans_on_term`) **still passed**. Its only check is
`assertFalse(h.output.exists())` immediately after `launch`, which is a race. The repository suite still kills M1
through the R0 test `test_magistrate_exit_timeout_refuses_without_pausing`, because the handoff is shared, but the
R1 module has no witness of its own.

## (g) Bindings

`scripts/run_align_r1_smoke.py` is added to `_NAMED_ARTIFACTS` immediately after `scripts/launch_align_r0.py`, and
to the unsigned receipt template (`"…": null`) next to it. This is the same treatment the launcher has: strict,
bound, and named because the runner is launched by path from `runner.json`, which a static walk cannot follow.
`identity_pins.json`, `plan_tree.json`, `inputs.json`, `r1_runtime.json` and `scripts/align_r1_followup_kit.py`
have no diff. **No condition-13 path is touched**: `git diff 9b4817f36 ff6cd1756 -- <the ten R1_EXECUTED_SOURCES>`
is empty. `tests.align.test_v4_executed_closure` passes (6 tests) and `tests.test_host_command_sites` passes (2).
The `test_timings.json` change is a single inserted line.

## (h) Exact magistrate command sequence

These commands were verified against a synthetic root. I ran the condition-13 one-liner for real in the head
worktree; it printed `ff6cd1756dcfce51a823cc0af59a8ce4af6c94ad`. I ran the `launch` invocation with exactly these
flags in the harness, adding only fake `--launchctl-bin/--pmset-bin/--pgrep-bin/--kill-bin`, and it returned 0 and
printed `next: exit the magistrate session now`. I ran the receipt check unchanged against the synthetic output:
OK. Changes from Sol's sequence: an explicit checkout of the merged commit, a check of `MAGISTRATE_PID`, and the
9,000 s deadline. **Run this only on a commit that contains the H-1 fix.**

Start and check, while the magistrate is still alive:

```sh
cd /Users/edr/code/jw-wt/r1-followup-smoke
git fetch origin && git checkout --detach <MERGED_PRESIGN_SHA_WITH_H1_FIX>
REPO="$PWD"
: "${PY:?Set PY to the existing pinned measurement-venv interpreter (do not resolve the symlink)}"
: "${MAGISTRATE_PID:?Set to the PID of this magistrate's own claude process}"
ps -o pid=,comm= -p "$MAGISTRATE_PID"     # must show the claude process, not a tool shell
CUSTODY="${MAGISTRATE_WATCHDOG_CUSTODY_ROOT:-/Users/edr/night-custody/magistrate}"
SOAK=/Users/edr/night-align/r1-20261111T043229Z/night/align-r1/soak_reference.json
OUT="$REPO/.desk/r1-followup-smoke-$("$PY" -B -c 'import time; print(time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()))')"
git status --short --branch
test -z "$(git status --porcelain)"
git merge-base --is-ancestor 9b4817f36 HEAD
"$PY" -B -c 'from pathlib import Path; import subprocess; from joulewise.align.apple import v4_registration as r; root=Path.cwd(); head=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip(); print(r.verify_r1_executed_sources(root,{"executed_commit":head}))'
test ! -e /Users/Shared/JouleWise/host-power/high-power.marker   # no armed W1 High Power (required until M-1 is fixed)
"$PY" -B scripts/launch_align_r0.py preflight --disk-path "$REPO"
DEADLINE="$("$PY" -B -c 'import time; print(time.time()+9000)')"
```

Run, as the magistrate's last action:

```sh
"$PY" -B scripts/launch_align_r0.py launch \
  --runner-kind r1-smoke --repo "$REPO" --python-bin "$PY" \
  --output "$OUT" --soak-reference "$SOAK" --disk-path "$REPO" \
  --custody-root "$CUSTODY" --magistrate-pid "$MAGISTRATE_PID" \
  --deadline "$DEADLINE" --exit-wait-seconds 180 --start-wait-seconds 30
echo "$OUT"   # record for the next activation
```

Require exit 0 and `"next": "exit the magistrate session now"` with a claimed fence (fence `pid` ≠
`MAGISTRATE_PID`). Then **exit the magistrate session at once** and make sure no other `claude`/`codex` process is
running on the MBP; the runner's census refuses otherwise. Nobody polls during the capture.

Check, on the next activation after the fence is gone:

```sh
"$PY" -B - "$OUT" <<'PY'
import hashlib, json, sys
from pathlib import Path
root = Path(sys.argv[1])
r = json.loads((root / "runner_receipt.json").read_text())
print(json.dumps({k: r[k] for k in ("rc", "parts", "error") if k in r}, sort_keys=True))
print([(s["name"], s["rc"]) for s in r["steps"]])
assert r["rc"] == 0 and r["parts"] == {"A": True, "B": True}
for feed in r["feeds"].values():
    assert feed["stop"]["proven_stopped"]
    for f in feed["files"]:
        with (root / f["path"]).open("rb") as h:
            assert hashlib.file_digest(h, "sha256").hexdigest() == f["sha256"]
PY
test ! -e "$CUSTODY/desk_fence.json"; launchctl list | grep -c 'com.joulewise.align-r0' || true   # expect 0
```

Also read the job's `stdout.log`/`stderr.log` under `$CUSTODY/r0-launches/<token>/`. A failed or partial smoke
goes back to the lead: do not retry a part, do not extend it, and do not reuse `OUT`.

## Findings

### HIGH

**H-1. Part B is capped at 1,800 s; its own bound is about 4,400 s.** `run_align_r1_smoke.py:31, 293` applies
`PART_LIMIT_S = 1800` to both parts. Part B is a fresh run: admission ≤ 1,800 s, then the 2,600 s post-G0 watchdog
that RL-84 P-5 confirmed and the kit's delta review admitted (F-4: "Restoring 1,200 s … is killed"). The launcher
reintroduces a tighter total cap than the one F-4 removed. The scaled demonstration (cap 4 s, B needs 6 s) gives
`TimeoutError: Part B exceeded its single 4 s budget`. The refusal record's "Part B up to 1,800 s more" estimate is
superseded by RL-84 P-5.

**Fix:**
- Use per-part caps. A: 1,800 + 120 s, so the kit's own 1,800 s verdict decides. B: 1,800 +
  `r1_runtime.smoke_post_g0_budget(quiet, deadman)["total"]` + 120 s, which is 4,520 s with the current config.
  Derive B's cap from config, or pin it with a test against the config.
- Before starting a part, refuse if `work_remaining()` is less than that part's full cap. Do not start a part that
  is bound to be truncated.
- Add a witness that B may run past 1,800 s.
- Raise the documented deadline to 9,000 s.

### MEDIUM

**M-1. The Automatic restore ignores a foreign W1 high-power marker and runs on every exit.**
`restore_power()` takes the host lock and calls `powermode.restore_automatic()` unconditionally. It does so even
when the runner refused before touching anything: battery, a loaded night agent, condition 13, the soak file, or
powermode 2. The runner never changes the power mode itself. If a W1 night is armed, its marker is present and its
High Power is set, but no lock is held until admission. That is exactly the case the `night_agents` refusal exists
for, and the smoke's cleanup would then reset that night to Automatic.

Demonstrated: with a foreign `high-power.marker` and `com.joulewise.night.align-r1` loaded, the runner refused at
`night_agents` and then issued `sudo -n /usr/bin/pmset -c powermode 0`. The established helper
`powermode.restore_owed` leaves a marker another session owns alone.

**Fix:** under the lock, if `powermode.host_marker_path()` exists, do not restore; record `foreign_marker_left`.
Alternatively, restore only after `read_power` has run, and add the marker check in either case.

**M-2. The volume census polls every 60 s during capture, which no night does.** `VolumeFeed.interval = 60`
runs `/sbin/mount` plus `diskutil info -plist` for every `/dev/disk*` mount (about 8 on an MBP) once a minute,
through dwell and both parts. The R1 driver censuses volumes at t0, before each runtime invocation, and before
registration (`align_r1_rehearsal.py:483, 1671, 1863`); HAZARD nights have no in-window volume census. Since the
smoke's purpose is to validate sampler/Tf08 coverage and the thermal gates, it should not add a periodic `diskutil`
load that the night will not have.

**Fix:** census at feed start, immediately before Part A, immediately before Part B, and at close. The agent census
at 30 s matches the night and should stay.

**M-3. Merge conflict with presign (RL-86) in `configs/gates/hazard_refusals.json`.** A trial `git merge` of
`origin/ops/2026-11-11-w1-presign` (`9e6fc0ad4`) into `ff6cd1756` conflicts in three hunks. No other file conflicts;
the R7-2 change to `align_r1_rehearsal.py` does not touch `VolumeWatch`, which is all the runner uses.

1. The not-scanned reason vocabulary: presign adds `v4_desk`; this branch adds `r1_smoke_existing_dependency`.
2. Module scope: presign maps `align_r0_checks.py → desk` and `align_v4_session.py → v4_desk`; this branch maps
   four modules to `r1_smoke_existing_dependency`.
3. Site rows: presign lists all 24 `launch_align_r0.py` keys with RL-86 wording, plus watchdog, driver and
   timing_receipts rows.

Resolution guidance:

- Keep both reasons.
- Take presign's `desk` for `align_r0_checks.py`. Keep `r1_smoke_existing_dependency` for `align_r1_rehearsal.py`,
  `align_r1_followup_kit.py` and `v4_registration.py`; presign scopes none of the three.
- Take presign's launcher rows, but set the `launch | ValueError|measurement checkout runner` guard to
  `cef3647b206ff276`, and add the new `launch | ValueError|r smoke requires` row and the 16 `run_align_r1_smoke.py`
  rows.
- Re-run `tests.hazards.test_refusal_allowlist` on the merge, and have the RL-86 owner sign off on the new rows'
  `protects` text.

### LOW

- **L-1.** An unmeasured agent census (a probe error such as a `pgrep` timeout under load) is a refusal that aborts
  a running part. The night's in-window `HazardCensus` retries unmeasured censuses and only refuses on a positive.
  Refusing on a positive is correct; consider the night's retry policy for unmeasured probes during a 75-minute B.
- **L-2.** Part A's runner cap counts kit start-up, which includes the kit's own condition-13 verify, while the
  kit's 1,800 s counts from its own `started`. The runner can therefore kill an A that the kit would pass. Fixed by
  the A margin in H-1.
- **L-3.** A work-deadline truncation is recorded as `Part A exceeded its single 1800 s budget`
  (F-work-deadline). Report which bound fired.
- **L-4.** The plist sets no `ExitTimeOut`. On an external stop (manual `bootout`, logout or shutdown), launchd's
  default of about 20 s before SIGKILL would cut R1's teardown of up to 180 s and orphan the meter and part sessions.
  The deadline path is unaffected, because the launcher, not launchd, times out. Consider `ExitTimeOut ≥ 400` for
  r1-smoke plists only, which keeps R0's plist bytes unchanged.
- **L-5.** The meter `MonitorSupervisor` is built without `identity=run_night.observe_identity`, which the night
  passes. As a result, `meter_supervision.jsonl` start rows lack `start_time`.
- **L-6.** `display()` hard-codes `/usr/bin/pmset` and ignores the launcher's `--pmset-bin`. This is a test-seam
  inconsistency only. `--checks/--keep-going` are accepted and silently ignored for r1-smoke.
- **L-7.** The R1 end-to-end test has no non-racy witness for the magistrate wait (see (f)). Add one: keep the
  owner alive past the dwell seam and assert that there is no output directory and no meter journal.
- **L-8.** The meter starts about 0.2 s before the first agent census. Starting the agent feed first would make a
  wrong `MAGISTRATE_PID` refuse before the meter starts. No part could run either way.

## Tests at head (`nice -n 10 python3.13 -B -m unittest <module>`, serial)

| Module | Result |
|---|---|
| `tests.align.test_r1_smoke_launcher` | 24 tests OK (29 s), including Sol's 11 in-module mutants |
| `tests.align.test_r1_followup` | 12 tests OK (102 s) |
| `tests.test_magistrate_desk_fence` (R0 launcher) | base 42 with 3 F, head 42 with 5 F, all load timeouts; 6 of 7 pass alone at head; the 7th fails identically at base |
| `tests.test_magistrate_watchdog` | 158 tests; 1 error at both base and head (subprocess timeout under load) |
| `tests.hazards.test_refusal_allowlist` | 23 tests, 2 F, 1 skip, at both base and head. The site difference is **identical** at base and head (same keys: driver `_run_hazard_night_body` re-raise, watchdog `_decide`/`decide`/`_launch_fence` FENCED/HOLD_UNSAFE, harvest `archive_copy_mismatch` guard). Scope gaps shrink at head. None involves the launcher or runner; presign's RL-86 rows address them (M-3). |
| `tests.test_host_command_sites` | 2 tests OK |
| `tests.align.test_v4_executed_closure` | 6 tests OK |

The harness, scenario driver and logs are in `/Volumes/JW-EXT/scratch/rev-r1-launcher/` (`harness/`, `logs/`,
`r0eq/`, `kept/normal-keep/`).
