# Arm runbook — rehearsal-20260911

Prepared 2026-09-09 against `7ca2908f66819d534ebc53e3786f32106f6de5ba`.
This is an unexecuted runbook for the arming magistrate, not an arm record.
Authority: [synthesis 65](65-magistrate-synthesis-second-stub-night.md),
[ruling 61](61-coldgate-ruling-second-stub-night.md) N1–N6/Q3,
[refuter 62](62-coldgate-opus-refuter-second-stub-night.md), and D-175.
The two blocks adapt the amended sequence in [21b](../2026-09-02-hands-free-week/21b-rehearsal-20260909-arm-plan.md);
the final record follows [21h](../2026-09-02-hands-free-week/21h-rehearsal-20260909-arm-record.md).
This document applies those decisions to this night; it adds no standing rule.

## Pins and preconditions (step 0)

H is the full hash of the **main commit that rewrites NIGHT_HANDBACK for this
night**, a descendant of `a52810c9`. It is not today's detached HEAD or the
latest bookkeeping HEAD. Set it from the committed handback notice when it
exists. The consolidated notice must have been sent after H and before the
move, with all pins and the harvest criteria below. Record its message/thread
IDs; never reuse the previous night's IDs as evidence. A relayed NO aborts.
Synthesis 65 says a headless activation cannot re-read the email thread: a NO
arrives through its next prompt or an interactive session. Record that
limitation rather than claiming a Gmail read that did not happen.

| Pin | Value |
|---|---|
| Plan/class | `rehearsal-20260911` / `REHEARSAL_STUB` |
| Install window | 2026-09-10 03:00–06:30 PDT; complete installation within it |
| First dead-man firing | 2026-09-10 07:00 PDT, epoch `1789048800` |
| First night firing, t0 | 2026-09-11 02:56 PDT, epoch `1789120560` |
| Window | `900` seconds |
| Courier deadline | `1789121760`, 2026-09-11 03:16 PDT (`t0 + 900 + 300`) |
| Exit boundary | `1789119060`, 2026-09-11 02:31 PDT (`t0 − 25 minutes`) |
| Relaunch belt | 2026-09-11 02:45–03:30 PDT |
| Both heads | `repo_head = measurement_head = H` |
| Measurement root | `/private/tmp/joulewise-rehearsal-20260911-checkout` |
| Custody root | `/Users/edr/night-custody/rehearsal-20260911` |
| Results branch | `night-results/20260911`, if pushed successfully |

Before cutting the checkout: `standdown.request` absent, no discoverable plan,
`launchctl list | grep joulewise` shows only `com.joulewise.magistrate`, and
`pgrep -fl "codex|claude|t3"` shows only the arming session's own processes.
Here **own** means the current activation PID from `magistrate.lock` and its
currently attached descendants: its foreground tool shell, the census Python
process and any still-attached tool transport. Prove that the lock PID is an
ancestor of the census process. A prior activation, interactive Claude/Codex,
T3 session, another seat, daemon, spare, pty host, resumed twin, or orphan
reparented to PID 1 is not own, even if this session originally launched it.
Stop own delegated seats and background work before the final census (21b
step 3b). Do not signal foreign processes. This night's requested precondition
is the raw only-own census; the older 21b classifier's informational app-helper
exceptions are not silently treated as own here.

## Block A — checkout, staged authoring and validation (steps 1–3)

Use foreground zsh tool calls. Set `H` to the notice's full commit hash before
each block; tool-shell exports do not persist. `DRIVER_SOURCE` below is the
linked magistrate worktree used by 21b, not the canonical checkout. Preserve
H's reachability on main/origin and never move the measurement checkout after
authoring. The future arming activation must have write authority for its
record and durable pointer; this documentation task does not perform them.

The watchdog reads every sibling **`*/night_plan.json`**
(`MAGISTRATE_WATCHDOG.md:21`), meaning `~/night-custody/*/night_plan.json`
in production. Both `/private/tmp` staging directories below are outside it.

The exact checkout command from 21b is:
`git -C "$DRIVER_SOURCE" worktree add --detach "$STUB_CHECKOUT" "$H"`.
Its writer argv is `PYTHONDONTWRITEBYTECODE=1 python3 -B - <<'PY'`, importing
`NightPlan` and `write_night_plan`. `joulewise/night_plan_writer.py` exposes
that function; it has no CLI parser/main, so `python3 -m
joulewise.night_plan_writer` is not a plan-authoring command.

```zsh
set -euo pipefail
: "${H:?Set H to the full committed handback hash from the notice}"
export H DRIVER_SOURCE=/Users/edr/code/JouleWise-wt-magistrate-1ef89702
export STUB_CHECKOUT=/private/tmp/joulewise-rehearsal-20260911-checkout
export NIGHT_CUSTODY=/Users/edr/night-custody/rehearsal-20260911
export STAGE=/private/tmp/joulewise-rehearsal-20260911-staging
export SCRATCH=/private/tmp/joulewise-rehearsal-20260911-validate
export PYTHONDONTWRITEBYTECODE=1
for p in "$STAGE" "$SCRATCH" "$STUB_CHECKOUT" "$NIGHT_CUSTODY"; do
  test ! -e "$p" && test ! -L "$p"
done
mkdir "$STAGE" "$SCRATCH"
# Capture foreground output, including failures; a missing final rc=0 is not success.
exec > >(tee "$STAGE/arm-blockA-output.txt") 2>&1
cat > "$STAGE/preconditions.py" <<'PY'
import json, os, subprocess, time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

zone = ZoneInfo("America/Los_Angeles")
now = time.time()
start = datetime(2026, 9, 10, 3, 0, tzinfo=zone).timestamp()
end = datetime(2026, 9, 10, 6, 30, tzinfo=zone).timestamp()
print("arm clock:", now, datetime.fromtimestamp(now, zone).isoformat(), flush=True)
assert start <= now < end, "outside 03:00–06:30 PDT install window"
assert datetime.fromtimestamp(1789120560).strftime('%Y-%m-%d %H:%M') == '2026-09-11 02:56', 'system local time differs from the pinned launchd time'
parent = Path('/Users/edr/night-custody')
stop = parent/'magistrate/standdown.request'
assert not stop.exists() and not stop.is_symlink(), "standdown requested"
assert not list(parent.glob('*/night_plan.json')), "existing plan"
services = subprocess.run(['launchctl', 'list'], capture_output=True, text=True, check=True)
matches = [line for line in services.stdout.splitlines() if 'joulewise' in line]
print('launchctl list | grep joulewise:', *matches, sep='\n', flush=True)
assert [line.split()[-1] for line in matches] == ['com.joulewise.magistrate']
me = json.loads((parent/'magistrate/magistrate.lock').read_text())['pid']
raw = subprocess.run(['ps', '-axo', 'pid=,ppid=,command='], capture_output=True, text=True, check=True).stdout
rows = {int(a): (int(b), c) for line in raw.splitlines() if line.strip()
        for a, b, c in [line.strip().split(None, 2)]}
def ancestors(pid):
    seen = set()
    while pid in rows and pid != 1 and pid not in seen:
        seen.add(pid)
        yield pid
        pid = rows[pid][0]
assert me in set(ancestors(os.getpid())), 'lock PID is not this census ancestor'
probe = subprocess.run(['pgrep', '-fl', 'codex|claude|t3'], capture_output=True, text=True)
print('pgrep -fl "codex|claude|t3" rc=', probe.returncode, flush=True)
print(probe.stdout, end='', flush=True)
print(probe.stderr, end='', flush=True)
assert probe.returncode in (0, 1), 'census failed'
hits = [int(line.split(None, 1)[0]) for line in probe.stdout.splitlines() if line.strip()]
foreign = [pid for pid in hits if me not in set(ancestors(pid))]
for pid in hits:
    print('census ancestry:', pid, list(ancestors(pid)), rows.get(pid), flush=True)
print('foreign agent matches:', foreign, flush=True)
assert not foreign, 'foreign or unclassifiable process; preserve it and abort'
PY
python3 -B "$STAGE/preconditions.py"
git -C "$DRIVER_SOURCE" cat-file -e "$H^{commit}"
test "$(git -C "$DRIVER_SOURCE" rev-parse "$H^{commit}")" = "$H"
git -C "$DRIVER_SOURCE" merge-base --is-ancestor a52810c9 "$H"
remote_main="$(git -C "$DRIVER_SOURCE" ls-remote --exit-code origin refs/heads/main)"
remote_main_head="${remote_main%%$'\t'*}"
# Fail closed if the remote object is unavailable locally; resolve before arming.
git -C "$DRIVER_SOURCE" merge-base --is-ancestor "$H" "$remote_main_head"
git -C "$DRIVER_SOURCE" show "$H:docs/process/NIGHT_HANDBACK.md"
# Inspect the displayed handback against the sent notice before continuing.
git -C "$DRIVER_SOURCE" worktree add --detach "$STUB_CHECKOUT" "$H"
test "$(git -C "$STUB_CHECKOUT" rev-parse HEAD)" = "$H"
cd "$STUB_CHECKOUT"
PYTHONDONTWRITEBYTECODE=1 python3 -B - <<'PY'
import os, time
from dataclasses import replace
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from joulewise.night_gate import NightPlan
from joulewise.night_plan_writer import write_night_plan

root = Path(os.environ['NIGHT_CUSTODY'])
stage = Path(os.environ['STAGE'])
scratch = Path(os.environ['SCRATCH'])
t0 = datetime(2026, 9, 11, 2, 56, tzinfo=ZoneInfo('America/Los_Angeles')).timestamp()
assert t0 == 1789120560
now = time.time()
assert now < t0 - 25 * 60
plan = NightPlan(plan_id='rehearsal-20260911', receipt_class='REHEARSAL_STUB',
    t0_epoch_s=t0, window_max_s=900, authored_epoch_s=now,
    repo_head=os.environ['H'], measurement_head=os.environ['H'],
    measurement_root=os.environ['STUB_CHECKOUT'], custody_root=str(root),
    chain_path=str(root/'chain.zsh'), chain_sha256_path=str(root/'chain.zsh.sha256'),
    registration_path='configs/campaigns/d117_contrast_v5/d166_dominance_criterion_registration.json')
twin_root = scratch/'custody'
twin = replace(plan, custody_root=str(twin_root), chain_path=str(twin_root/'chain.zsh'),
               chain_sha256_path=str(twin_root/'chain.zsh.sha256'))
print(write_night_plan(stage/'night_plan.json', plan))
print(write_night_plan(scratch/'night_plan.json', twin))
PY
scripts/install_night_agent.sh --plan "$SCRATCH/night_plan.json" --hour 2 --minute 56 --render-only "$SCRATCH/render"
/usr/bin/plutil -lint "$SCRATCH/render/com.joulewise.night.plist"
/usr/bin/plutil -lint "$SCRATCH/render/com.joulewise.night.deadman.plist"
python3 -B - <<'PY'
import json, os
from pathlib import Path
real = json.loads((Path(os.environ['STAGE'])/'night_plan.json').read_bytes())
twin = json.loads((Path(os.environ['SCRATCH'])/'night_plan.json').read_bytes())
diff = {k for k in real.keys() | twin.keys() if real.get(k) != twin.get(k)}
print('plan differing fields:', sorted(diff))
assert diff == {'custody_root', 'chain_path', 'chain_sha256_path'}
assert not Path(os.environ['NIGHT_CUSTODY']).exists()
PY
print 'block A rc=0'
```

The `--plan` above names the **staged validation twin**, not the real staged
plan. This is the explicit 21b amendment / 21c ruling B requirement 3:
`--render-only` still executes `mkdir -p "$custody_root/night"`
(`install_night_agent.sh:123–125`). The twin keeps that write outside real
custody. Its only differing fields must be the three printed custody paths.
The real plan is revalidated during install. A bare `--render-only` without
its output directory is not the installer's supported argv (usage line 5).

Verified pin checks (`install_night_agent.sh:81–96`) compare `repo_head` to
the **driver checkout HEAD** and `measurement_head` to the HEAD of
`measurement_root`. Exact refusal strings are `plan repo_head does not match
driver checkout HEAD` and `plan measurement_head does not match measurement
checkout HEAD`. The installer also parses the plan, rejects future/stale
authorship, requires an executable courier, and refuses existing night
records. Success prints `validated pins: repo_head=... measurement_root=...
measurement_head=...`. Rendering does not prove the live night gate passes.

## Between blocks — step 3b and notice evidence

Stop all own delegated seats and background tasks, including a keepalive
Monitor, using the session's own task controls. Record the actions and tool
results; do not invent TaskStop IDs or retired PIDs. Inspect
`ps -axo pid,ppid,command | grep -E 'claude (daemon run|bg-spare|bg-pty-host)|--resume'`
as in 21b; a match needs ancestry classification and a foreign session aborts.
Record the consolidated notice's send evidence and any relayed NO. Complete
Block B, the record, commit/push and exit in the same turn after this point.

## Block B — measurements, final census, move, install, inspect (steps 4–7)

Re-set H from the same notice before this block. The recording probes below
are arm-time observations, not capture validation. The timer argv comes from
`44-coldgate-charge-replay-verdict.md:5`; no timing threshold is added.

```zsh
set -euo pipefail
: "${H:?Set the same full committed handback hash as Block A}"
export H DRIVER_SOURCE=/Users/edr/code/JouleWise-wt-magistrate-1ef89702
export STUB_CHECKOUT=/private/tmp/joulewise-rehearsal-20260911-checkout
export NIGHT_CUSTODY=/Users/edr/night-custody/rehearsal-20260911
export STAGE=/private/tmp/joulewise-rehearsal-20260911-staging
export SCRATCH=/private/tmp/joulewise-rehearsal-20260911-validate
export PYTHONDONTWRITEBYTECODE=1
test -f "$STAGE/night_plan.json"
exec > >(tee "$STAGE/arm-blockB-output.txt") 2>&1
grep -Fx 'block A rc=0' "$STAGE/arm-blockA-output.txt"
cd "$STUB_CHECKOUT"
test "$(git rev-parse HEAD)" = "$H"
test -z "$(git status --short)"
remote_main="$(git -C "$DRIVER_SOURCE" ls-remote --exit-code origin refs/heads/main)"
remote_main_head="${remote_main%%$'\t'*}"
git -C "$DRIVER_SOURCE" merge-base --is-ancestor "$H" "$remote_main_head"
test ! -e "$NIGHT_CUSTODY" && test ! -L "$NIGHT_CUSTODY"
pmset -g batt
pmset -g custom
python3 -c "import time; t=time.perf_counter(); [time.sleep(0.05) for _ in range(20)]; print((time.perf_counter()-t)/20)"
print 'Powermode recorded, not gated for this stub. A green stub says nothing about the capture-timeout seam.'
# Record current device IDs; unlike 21b's historical value, these are live.
test "$(stat -f %d "$STAGE")" = "$(stat -f %d /Users/edr/night-custody)"
python3 -B "$STAGE/preconditions.py"
# Final census/window/standdown check immediately precedes publication and install.
mkdir -p "$NIGHT_CUSTODY"
python3 -c 'import os,sys; os.replace(sys.argv[1], sys.argv[2]); print("moved", sys.argv[2])' "$STAGE/night_plan.json" "$NIGHT_CUSTODY/night_plan.json"
date '+install-start epoch=%s local=%Y-%m-%dT%H:%M:%S%z'
if ! scripts/install_night_agent.sh --plan "$NIGHT_CUSTODY/night_plan.json" --hour 2 --minute 56; then
  print 'ABORT: install failed after publication; preserve this transcript'
  scripts/install_night_agent.sh --plan "$NIGHT_CUSTODY/night_plan.json" --hour 2 --minute 56 --uninstall
  # 21b's rollback of this newly authored plan; retain the attempted bytes in staging.
  cp "$NIGHT_CUSTODY/night_plan.json" "$STAGE/failed-night_plan.json"
  rm "$NIGHT_CUSTODY/night_plan.json"
  exit 1
fi
date '+install-end epoch=%s local=%Y-%m-%dT%H:%M:%S%z'
launchctl list | grep joulewise
python3 -B - <<'PY'
import os, plistlib, subprocess, time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
root = Path(os.environ['STUB_CHECKOUT'])
plan = str(Path(os.environ['NIGHT_CUSTODY'])/'night_plan.json')
rows = subprocess.run(['launchctl', 'list'], capture_output=True, text=True, check=True).stdout
labels = {line.split()[-1] for line in rows.splitlines() if line.split()}
assert {'com.joulewise.night', 'com.joulewise.night.deadman'} <= labels
for label, mode, hour, minute in [('com.joulewise.night', 'run', 2, 56),
                                  ('com.joulewise.night.deadman', 'dead-man', 7, 0)]:
    p = Path('/Users/edr/Library/LaunchAgents')/(label+'.plist')
    with p.open('rb') as f:
        data = plistlib.load(f)
    print(label, 'calendar=', data['StartCalendarInterval'], 'program=', data['ProgramArguments'],
          'cwd=', data['WorkingDirectory'], flush=True)
    assert data['StartCalendarInterval'] == {'Hour': hour, 'Minute': minute}
    assert data['WorkingDirectory'] == str(root)
    assert data['ProgramArguments'][:6] == ['/usr/bin/env', 'python3', str(root/'scripts/run_night.py'), mode, '--plan', plan]
    assert data['RunAtLoad'] is False
zone = ZoneInfo('America/Los_Angeles')
now = time.time()
assert datetime(2026, 9, 10, 3, 0, tzinfo=zone).timestamp() <= now < datetime(2026, 9, 10, 6, 30, tzinfo=zone).timestamp()
print('install verified epoch=', now, flush=True)
print('expected dead-man=1789048800; night=1789120560; courier deadline=1789121760', flush=True)
PY
cp "$NIGHT_CUSTODY/night_plan.json" "$STAGE/arm-night_plan.json"
python3 -B - <<'PY'
import json, os
from pathlib import Path
root = Path(os.environ['NIGHT_CUSTODY'])/'night'
print('post-install night/ baseline:', json.dumps([
    {'name': p.name, 'size': p.lstat().st_size, 'mtime_ns': p.lstat().st_mtime_ns}
    for p in sorted(root.iterdir())], indent=2))
PY
print 'block B rc=0'
```

The `os.replace` Python one-liner is quoted unchanged from 21b. The preceding
device check is necessary for that atomic rename; do not replace a failed
cross-device move with a copy. On any failed block, preserve its output and
report where it stopped. Preserve pre-existing paths. The post-move install
failure branch uninstalls this attempt's agents and unpublishes this attempt's
plan as in 21b; if verification fails after install, report the installed
state and use that same uninstall/unpublish procedure before leaving a
failed arm. Do not remove an armed checkout while either agent remains loaded.

## Record and exit (step 8)

Create the 21h-shaped arm record in the arming activation's authorized linked
bookkeeping worktree. Include the actual activation ID/PID, record timestamp,
install start/end epochs, H, expected first firing epochs, the frozen triple
`(rehearsal-20260911, /private/tmp/joulewise-rehearsal-20260911-checkout, H)`,
notice IDs/send time and NO-channel limitation, Block A and B outputs/rc,
step-3b stop results, both census outputs/ancestry, power source, each powermode,
timer result, rendered/installed plist evidence, the byte copy of the armed
plan and the initial `night/` inventory. State explicitly: **a green stub says
nothing about the capture-timeout seam**. Record facts with artifact pointers,
not expected values presented as observations.

Copy staging evidence and rendered plists before deleting scratch. Set the
following paths to the arming activation's allocated, authorized record paths
before running the commands; no future trace filename or branch is presumed
to be available. `BOOKKEEPING_ROOT` is a linked worktree, never the disposable
measurement checkout or canonical repo. `ARM_RECORD` and `ARM_EVIDENCE` are
repository-relative; `BOOKKEEPING_BRANCH` is its authorized bookkeeping branch.

```zsh
set -euo pipefail
: "${BOOKKEEPING_ROOT:?authorized linked worktree}"
: "${BOOKKEEPING_BRANCH:?authorized bookkeeping branch}"
: "${ARM_RECORD:?allocated repository-relative arm record path}"
: "${ARM_EVIDENCE:?allocated repository-relative artifact directory}"
cd "$BOOKKEEPING_ROOT"
test "$(git branch --show-current)" = "$BOOKKEEPING_BRANCH"
test ! -e "$ARM_EVIDENCE"
mkdir -p "$ARM_EVIDENCE"
cp /private/tmp/joulewise-rehearsal-20260911-staging/arm-* "$ARM_EVIDENCE/"
cp -R /private/tmp/joulewise-rehearsal-20260911-validate/render "$ARM_EVIDENCE/"
# Use the activation's file editor to write ARM_RECORD with the fields above,
# and update the existing durable pointer with H, the frozen triple and harvest action:
export DURABLE_POINTER=docs/process_traces/2026-09-02-hands-free-week/00-DURABLE-STATE.md
test -f "$ARM_RECORD"
git diff --check
git diff -- "$ARM_RECORD" "$DURABLE_POINTER"
git status --short
git add -- "$ARM_RECORD" "$ARM_EVIDENCE" "$DURABLE_POINTER"
git diff --cached --stat
# Review the index: only this arm's authorized record, artifacts and pointer may be staged.
git commit -m 'Record rehearsal-20260911 arm and harvest pointer'
git push origin "$BOOKKEEPING_BRANCH"
git ls-remote --exit-code origin "refs/heads/$BOOKKEEPING_BRANCH"
```

Compare the remote hash to the new bookkeeping commit; record a push failure
honestly. H stays the original handback commit as bookkeeping advances.
The durable pointer carries the record location, frozen triple and exact
next action: harvest this night, assess items 5/6, uninstall from its checkout,
then remove the stub checkout and plan root after evidence preservation.
The magistrate relaunch prompt's frozen-checkout list keeps that triple until
completion (`MAGISTRATE_WATCHDOG.md:102`). End the activation with no own
background work. Do not wait resident until t0: synthesis 65 assigns the
09-11 stand-down to the watchdog. No commit, push, install or cleanup in
these blocks was executed while drafting this document.

## Expected observations and harvest acceptance

At approximately 07:00 PDT on **09-10** (epoch `1789048800`), `night.log`
must contain the driver's exact message, prefixed by its ISO local timestamp:

```text
dead-man fired before the night's completion epoch 1789121760; standing down
```

`run_night.py:958–959` defines that completion epoch as t0 plus window plus
courier deadline; `dead_man` emits the message at lines 1740–1747 and returns
without writing a refusal/courier record. This first pre-night launchd firing
is distinct from `_next_deadman_epoch(t0)`, which computes the later recovery
dead-man on t0's date. The quoted epoch in the message is completion, not the
dead-man's firing time.

Harvest the custody `night/{result.json,receipt.json,refusal.json,courier.sent,courier.json}`
as applicable and `night.log`; verify the results branch on origin. Preserve
the arm-time directory inventory and the pre-t0 record timestamps so item 5
is tested, not inferred from a green result. Synthesis 65 requires:

- The 09-10 dead-man stand-down line precedes the 09-11 `night gate verdict=`
  line, and `night/` holds nothing from that dead-man firing. Record any
  deviation; do not silently exempt a file from this wording.
- A green `receipt.json` verdict is exactly `REHEARSAL_ONLY`, with C5 measured
  `chain_stub: built_in_stub_by_design`, `chain_sha256: null` and
  `expected_chain_sha256: null`. Refuter 62 spells out C1/C3/C4/C5 `PASS`,
  C2 `NOT_APPLICABLE` (`no_pack_by_design`); expected `result.json` is
  `REHEARSAL_ONLY` with `chain_exit_code: 0`.
- A `night_refused_agent_present` receipt can close item 5 only if its
  dead-man evidence passes; item 6 remains open. Any other refusal is a
  finding to cure first. Do not infer a refused receipt from launchd exit 3:
  the normal completed stub branch sets that status regardless of the gate
  verdict (`run_night.py:1672–1675`).
- The courier deadline is 03:16 PDT on 09-11, epoch `1789121760`. Preserve
  send evidence; a send record alone does not verify inbox delivery.

After harvest, follow 21h/21i's post-completion removal practice (61 N6), from
the pinned disposable checkout:

```zsh
cd /private/tmp/joulewise-rehearsal-20260911-checkout
scripts/install_night_agent.sh --plan /Users/edr/night-custody/rehearsal-20260911/night_plan.json --hour 2 --minute 56 --uninstall
```

Preserve the evidence before removing the checkout and plan root. Never reuse
this stub root for a real plan. Item 1's `cold_start.json` derivation remains
desk work; this night does not close it.

## Fact table — checked source locations

Line numbers below refer to the inspected base, with 65/61/62 read from the
lead worktree `/Users/edr/code/JouleWise-wt-magistrate-1ef89702` as instructed.
They must accompany the lead's landing; those three files were absent from
this detached checkout at drafting time.

| Fact | Source line(s) |
|---|---|
| New stub ID, no measurement/sudo, fresh roots | synthesis 65:13–14 |
| t0/window/deadline/exit boundary/belt | synthesis 65:15–16 |
| H is handback main commit; cured ancestry; disposable root | synthesis 65:17–19 |
| Custody/results branch | synthesis 65:20 |
| Morning-before install bounds and first dead-man epoch | synthesis 65:21–26 |
| Power/timer recorded, capture seam unproved | synthesis 65:27–28; timer argv in charge 44:5 |
| Receipt/dead-man acceptance; exit 3 not refusal | synthesis 65:29–32; run_night.py:1672–1675 |
| Notice after H/before move; item 1 separate | synthesis 65:33–34 |
| Successor may arm, NO relay limitation, exit after record | synthesis 65:38–41 |
| Watchdog glob; fence arithmetic; frozen checkout list | MAGISTRATE_WATCHDOG.md:21, 42–52, 102 |
| Exact worktree command, writer argv and registration path | 21b:177, 188–209 |
| Twin validation and three-path equivalence | 21b:210–226; 21c:217–227; installer:123–125 |
| Step 3b own tasks/orphans; final census | 21b:231–240, 256–290 |
| mkdir + exact os.replace; install; record/exit | 21b:293–304; 21h:6–14, 25–33 |
| Writer is function only; validates mapping and atomically writes | night_plan_writer.py:18–74 |
| Installer argv, schema/age, pins, courier, records, agents | install_night_agent.sh:5, 43–103, 181–216 |
| Program paths, daily hour/minute, RunAtLoad false, output paths | configs/launchd/com.joulewise.night.plist.template:7–39 |
| Dead-man timestamp/message/completion arithmetic | run_night.py:142–145, 945–959, 1727–1747 |
| C5 stub marker and null digest fields | joulewise/night_gate.py:1043–1052 |
| Green row statuses/result and pre-night evidence interpretation | refuter 62:142–143; ruling 61:130–138 |
| Eight arming conditions and no real reuse | docs/decision_log.md:11145–11154 |

## UNVERIFIED

- H and the new notice's message/thread IDs are not available in this drafting
  session. Their exact values, remote reachability and send ordering must be
  established by the lead before arming; no old hash/ID is substituted.
- The combined blocks, current process tree, future install/power/timer
  readings, device equality, rendered plists, actual firing times, receipt,
  courier and remote push have not been executed here. Script inspection and
  the prior arm evidence establish command shapes, not this night's results.
- Literal absence of all `night/` writes at the pre-night firing needs live
  inspection. The installer creates `night/`; the plist directs launchd
  stdout/stderr to `night/launchd.deadman.out` and `.err`. `dead_man` itself
  writes only the stand-down line on its early branch, but script inspection
  cannot establish whether launchd creates or changes those stream files at
  firing. Preserve the baseline and report any conflict with synthesis 65's
  literal acceptance to the magistrate; this runbook does not relax it.
- The writer has no command-line authoring interface, so an assumed
  `python3 -m joulewise.night_plan_writer --...` argv is unsupported. Use the
  verified imported function shown above. The new orchestration blocks have
  not been live-rehearsed; the future activation's own task-stop and file-editor
  calls depend on its actual task IDs and allocated bookkeeping paths.

## Addendum (2026-09-09 09:20 PDT, magistrate 2145630c) — H and notice ids

H = `57ddad20226c6921d81a87b9d78e61950c14a74f` (main; the NIGHT_HANDBACK rewrite commit). Consolidated notice: Gmail message
`1a086f4174733bfb`, thread `1a0800cdb282c3f1`, sent 09:15 PDT 2026-09-09 (after H, before any move). Use these in step 0.

## Addendum 2 (2026-09-09 ~17:05 PDT, consistency sweep 106 F5/F6)

Item 1 (cold_start.json / COURIER_DEADLINE_S) is CLOSED (derivation 70 + capture 104); nothing in this runbook depends on it. Chronology labels in this file and in synthesis 65 ("~09:20", "~09:35") were the lead's clock estimates written before the containing commit 57ddad20 (09:15:04 PDT committer time); treat committer times as authoritative.
