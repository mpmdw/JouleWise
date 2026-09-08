# 21b — REHEARSAL_STUB night `rehearsal-20260909`: magistrate ruling on the scout's block, bench pass, and the exact arm-time sequence

Written by headless magistrate activation 1ef89702 at 01:05:11 PDT (commit 4ac5d981; F1/F2) 2026-09-08. NOTHING IS ARMED by this file. The
arm happens only after (a) Ed's arm email has gone out and no NO has arrived, and (b) the interactive session
joulewise-53 has messaged that it stood down (its condition 2: no arming while it or its seats are alive).

## Timeline of record (from commit and Gmail timestamps; the approximate times earlier in this file were 15–30 min ahead of the artifacts and are corrected in place)

<!-- F1/F2: primary-source chronology, replacing the self-reported clock. -->
| event | time PDT | source |
|---|---|---|
| launch email 1ef89702 (1a0800383847cde1) | 00:55:08 | Gmail internalDate 1788854108 |
| commit 67cbf5fe (trace 21) | 00:57:32 | git committer date |
| commit 4a7a768c (21a scout) | 01:02:02 | git |
| bench plan authored | 01:04:01 | bench-night_plan.json authored_epoch_s 1788854641.57 |
| commit 4ac5d981 (21b created) | 01:05:11 | git |
| ARM EMAIL 1a0800cdb282c3f1 | 01:05:21 | Gmail internalDate 1788854721 |
| commit f9679fb4 (arm email id recorded) | 01:05:39 | git |
| commit ae8f074f = H (handback rewritten) | 01:10:44 | git |
| pins follow-up email 1a08012045894ef7 | 01:10:59 | Gmail internalDate 1788855059 |
| commit b0c88632 | 01:11:22 | git |
| commit a8cc6e68 (cold-gate AMEND relayed) | 01:20:08 | git |
| commit 2987a626 | 01:20:19 | git |
| activation 1ef89702 terminated | 01:33:28 | events.jsonl seq 5 epoch 1788856408.777 |
| activation 784a764e spawned | 01:41:58 | events.jsonl seq 8 epoch 1788856918.677 |
| commits 9a15338e / a6bff232 / 83b3ec5e | 01:48:16 / 01:48:47 / 02:01:16 | git |
| commit dbd49c1d (21c: ruling B recorded) | 02:03:37 | git |
| commit 0f3390c9 (fix round 1 landed) | 02:10:06 | git |
| commit 82622e70 (magistrate review of the landing) | 02:11:53 | git |

The first arm email (01:05:21) preceded H (01:10:44) by 5 min 23 s; the pins follow-up (01:10:59) followed H by 15 s;
whether D-175 cond. 1 is satisfied on the follow-up or requires a new arm notice after H is REFERRED to the
synthesis author (joulewise-53) by activation 784a764e; NO ARM until that ruling is recorded here. <!-- F1 -->

Ruling now recorded: joulewise-53 selected Option B at 02:03 PDT (recorded in commit dbd49c1d), as recorded in
`21c-ref-295-opus-contract.md` §Ruling of record on F1. ONE consolidated arm notice must be sent on thread
`1a0800cdb282c3f1` AFTER this fix round is committed. H stays `ae8f074f` for conditions 2 and 6. That notice must
restate every pin verbatim (t0 epoch and local time, measurement_root, measurement_head ae8f074f, receipt class
REHEARSAL_STUB, courier deadline, custody_root), say "launches unless NO", and include the corrected primary-source
timeline (arm email, H, pins follow-up, new notice) and the correction of the earlier times. The NO window runs
from that notice. NO ARM pending that notice and all other conditions; never before t0 − 60 min
(01:56 PDT 2026-09-09, epoch 1788944160) or joulewise-53's stand-down message. CONSOLIDATED NOTICE SENT: Gmail id `1a080d1adf46c7b2`,
internalDate 1788867620 = 04:40:20 PDT 2026-09-08, on thread `1a0800cdb282c3f1`, after fix round 0f3390c9 and the delta cures
(content head 083ce8ae; ledger head 1ae91b4d). The NO window runs from it. Nothing is armed. <!-- F1 -->

## Ruling on the scout's NEEDS_RULING (21a, F1)

The scout is right that the watchdog bench's fake nonexistent measurement root (`MAGISTRATE_WATCHDOG.md` bench block)
cannot pass `scripts/install_night_agent.sh:88` (`git -C "$measurement_root" rev-parse HEAD`). Precedent does not
resolve it: the only prior rehearsals (`rehearsal-20260902/03`) were v1 plans with no `measurement_root`. The
measurement checkout of record (`/Users/edr/JouleWise-measurement-20260813`) sits at `eeb4e133`, which predates the
v2 plan pin and has no `night_plan_writer.py`; moving it is a measurement-checkout move I will not make for a stub.

RULING (operational, within the documented rules; not a process change): the stub's `measurement_root` is a
DISPOSABLE DETACHED GIT CHECKOUT under `/private/tmp/`, created from the magistrate worktree at the handback commit
H, used only by this rehearsal, and deleted with the plan root before any real plan (the doc's "fake roots must never
be reused by a real plan" intent is preserved; the installer's pin checks are satisfied honestly; no measurement
checkout is touched). `registration_path` is the real repo-relative registration the 09-03 plan used
(`configs/campaigns/d117_contrast_v5/d166_dominance_criterion_registration.json`) so the gate's C1 authentication
has a real file to read (21a risk 5). Ed's arm email states this choice explicitly; Ed's NO overrides.

Order of record (PD-1): the arm email (01:05:21) was sent under this operational ruling before the cold-gate AMEND and the D-175 synthesis (a8cc6e68, 01:20:08) existed; nothing was armed; D-175 later ratified the substance. <!-- F10 -->

## Bench pass (2026-09-08 01:04:01 PDT (bench authored_epoch_s 1788854641.57; F1/F2); temporary custody parent, no launchd, real custody untouched)

- `write_night_plan` produced `bench-night_plan.json` (schema v2, t0 1788947760 = 2026-09-09 02:56:00 PDT, window
  900 s, both heads = bench H `4a7a768c`).
- `scripts/install_night_agent.sh --plan … --hour 2 --minute 56 --render-only …` run FROM the disposable checkout:
  `validated pins: repo_head=4a7a768c… measurement_root=/private/tmp/jw-rehearsal-bench-…/checkout
  measurement_head=4a7a768c…`, rc 0; both rendered plists `plutil -lint` OK (copied here).
- `scripts/magistrate_watchdog.py --dry-run` with `MAGISTRATE_WATCHDOG_CUSTODY_ROOT` under the same temp parent
  (so the plan was discovered): `decision=LAUNCHING reason=all launch predicates clear` — a plan whose t0 is tomorrow
  does not hold relaunch.
- The bench worktree and temp custody were removed after copying; nothing under `~/night-custody` was written.

## Original arm-time sequence (historical; superseded in full by the amended sequence below)

```zsh
# F4/F5: historical sequence only; the amended sequence stages the whole validation.
print "ABORT: superseded sequence; use the amended sequence below"; exit 1
# 0. Preconditions (all must hold): no standdown.request; joulewise-53 has messaged stand-down; Ed's arm email
#    sent and no NO on its thread; no plan under ~/night-custody/*/night_plan.json; now < 2026-09-09 02:00 PDT.
test ! -e ~/night-custody/magistrate/standdown.request || { print "ABORT: standdown requested"; exit 1; } # F4
plans=(~/night-custody/*/night_plan.json(N))
test ${#plans} -eq 0 || { print "ABORT: existing plan"; exit 1; } # F4
# 1. Historical handback rewrite is complete at H; do not rewrite or re-pin H. (F1/F9)
export DRIVER_SOURCE=/Users/edr/code/JouleWise-wt-magistrate-1ef89702
export H=ae8f074ffa554707a9eac95995ab8ec03235d118 # pinned H, never current branch HEAD
git -C "$DRIVER_SOURCE" cat-file -e "$H^{commit}" || { print "ABORT: H unavailable"; exit 1; } # F4
worktree_status=$(git -C "$DRIVER_SOURCE" status --short) || { print "ABORT: git status failed"; exit 1; }
test -z "$worktree_status" || { print "ABORT: dirty driver checkout"; exit 1; }
# 2. Disposable checkout at H (measurement_root for the stub only).
export STUB_CHECKOUT=/private/tmp/joulewise-rehearsal-20260909-checkout; test ! -e "$STUB_CHECKOUT" || { print "ABORT: stub checkout exists"; exit 1; } # F4
git -C "$DRIVER_SOURCE" worktree add --detach "$STUB_CHECKOUT" "$H" || { print "ABORT: checkout creation failed"; exit 1; } # F4
test "$(git -C "$STUB_CHECKOUT" rev-parse HEAD)" = "$H" || { print "ABORT: checkout pin mismatch"; exit 1; } # F4
# 3. Author the plan (real custody root; the watchdog discovers it as soon as it exists).
export NIGHT_CUSTODY=/Users/edr/night-custody/rehearsal-20260909; test ! -e "$NIGHT_CUSTODY" || { print "ABORT: real custody exists"; exit 1; } # F4
cd "$STUB_CHECKOUT" || { print "ABORT: checkout unavailable"; exit 1; }
PYTHONDONTWRITEBYTECODE=1 python3 -B - <<'PY' || { print "ABORT: plan authoring failed"; exit 1; }
import os, time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from joulewise.night_gate import NightPlan
from joulewise.night_plan_writer import write_night_plan
root = Path(os.environ["NIGHT_CUSTODY"]); H = os.environ["H"]
t0 = datetime(2026, 9, 9, 2, 56, 0, tzinfo=ZoneInfo("America/Los_Angeles")).timestamp(); assert t0 == 1788947760
now = time.time(); assert now < t0 - 25 * 60
plan = NightPlan(plan_id="rehearsal-20260909", receipt_class="REHEARSAL_STUB", t0_epoch_s=t0, window_max_s=900,
    authored_epoch_s=now, repo_head=H, measurement_root=os.environ["STUB_CHECKOUT"], measurement_head=H,
    chain_path=str(root/"chain.zsh"), chain_sha256_path=str(root/"chain.zsh.sha256"), custody_root=str(root),
    registration_path="configs/campaigns/d117_contrast_v5/d166_dominance_criterion_registration.json")
print(write_night_plan(root/"night_plan.json", plan))
PY
# 4. Install both night agents FROM the disposable checkout (the installer derives the driver checkout from its own path).
cd "$STUB_CHECKOUT" || { print "ABORT: checkout unavailable"; exit 1; }
scripts/install_night_agent.sh --plan "$NIGHT_CUSTODY/night_plan.json" --hour 2 --minute 56 || { print "ABORT: agent install failed"; exit 1; }
launchctl list | grep -E "com.joulewise.night" ; cat "$NIGHT_CUSTODY/night_plan.json"
# 5. Push H (branch), record the arm (plan json copy, launchctl list, email id) in this trace dir, commit, push.
# 6. Stop every Codex child and background process; end the loop; exit. The LaunchAgent is the wake source.
#    Request boundary 02:31 PDT 2026-09-09 (TERM 02:40, KILL 02:41; belt 02:45–03:30).
```

Morning after (the next activation, from the RELAUNCH prompt's frozen triple
`["rehearsal-20260909", "/private/tmp/joulewise-rehearsal-20260909-checkout", "<H>"]`): harvest
`$NIGHT_CUSTODY/night/{result.json,receipt.json,refusal.json,courier.sent,courier.json}` and `night.log`, verify branch
`night-results/20260909` on origin, record under NIGHT-REHEARSAL-01, then
`cd $STUB_CHECKOUT && scripts/install_night_agent.sh --plan $NIGHT_CUSTODY/night_plan.json --hour 2 --minute 56 --uninstall`,
then remove the stub checkout (`git worktree remove`) and the plan root before any real plan. Accept only
`night_refused_agent_present` as a receipt refusal; any other refusal is a finding.

## NIGHT_HANDBACK.md text for this night

Authoritative text: `git show ae8f074f:docs/process/NIGHT_HANDBACK.md` (committed 01:10:44). The draft that stood here preceded H; H adds, relative to that draft: the thread id, the courier deadline 03:16 PDT (t0 + 1200 s = 1788948960), the install-FROM-checkout sentence, and the pointer to 21b. The draft is removed to avoid two versions. <!-- F9 -->

## Arm email (precondition (a)) — SENT

Gmail id `1a0800cdb282c3f1`, 2026-09-08 01:05:21 PDT (Gmail internalDate 1788854721; F1/F2), subject "JouleWise — ARM REQUEST: rehearsal-20260909
(REHEARSAL_STUB) for 02:56 PDT Tue 9 Sep; launches unless you reply NO". Check that thread for a NO immediately before
step 0 of the arm-time sequence. Precondition (b) (joulewise-53 stand-down message) was still outstanding when this
line was written.

## Handback committed as H; pins on Ed's thread (2026-09-08 01:10:44 PDT, H; pins follow-up 01:10:59 PDT; recorded in b0c88632 at 01:11:22 PDT; F1/F2)

- H = `ae8f074ffa554707a9eac95995ab8ec03235d118` (NIGHT_HANDBACK.md rewritten for this night). The arm-time sequence
  uses the fixed handback pin even when this branch has moved past `ae8f074f`: pin `H=ae8f074ffa554707a9eac95995ab8ec03235d118` EXPLICITLY — the plan must
  pin the commit that rewrote the handback, and the disposable checkout is created at that commit.
- Follow-up on the arm thread with the exact pins (t0, measurement_root, H, class, courier deadline 03:16 PDT):
  Gmail id `1a08012045894ef7`, same thread `1a0800cdb282c3f1`.
- joulewise-53's authority ruling (relaunch-prompt line 19 protects watchdog-owned state and already-armed plans, not
  the documented email-then-arm of a stub) is recorded by that session in the decision log for Ed to see; this
  activation proceeds under it and stops if Ed or a cold gate overturns it. Its condition 4 (no arm until it messages
  stand-down) still binds. pid 48645 (leaked 09-04 test stub magistrate) was retired by joulewise-53; re-check
  `ps -p 48645` at arm time and never signal it from this activation.

## AMENDED arm-time sequence (cold gate AMEND on rehearsal-arming authority, relayed by joulewise-53, 01:20:08 PDT (commit a8cc6e68; F1/F2); supersedes the entire earlier sequence)

Full ruling text: `docs/process_traces/2026-09-08-handoff-redo/09-coldgate-packet-rehearsal-authority/13-magistrate-synthesis.md`
(branch `feat/2026-09-08-relaunch-prompt-line19`, D-175 PR by joulewise-53). Eight conditions; (1) satisfied when the consolidated post-fix notice is sent on thread `1a0800cdb282c3f1` (ruling B, 21c; see Timeline of record), (4) satisfied by that same notice, which precedes the move, (6) satisfied while this branch or main
holds `ae8f074f`, (7)/(8) are conduct rules. Conditions (2), (3), (5) change the mechanics:

```zsh
# 0. Preconditions: no standdown.request; joulewise-53 has messaged stand-down; no NO on thread 1a0800cdb282c3f1;
#    consolidated post-fix notice recorded above; 01:56 PDT <= now < 02:15 PDT on 2026-09-09 (floor: the ruling's
#    t0 - 60 min; ceiling: leaves >= 16 min to record, commit, push and exit before the 02:31 request boundary);
#    no plan under ~/night-custody/*/night_plan.json. (F1; window widened by the magistrate at 0f3390c9 review)
test ! -e ~/night-custody/magistrate/standdown.request || { print "ABORT: standdown requested"; exit 1; } # F4
plans=(~/night-custody/*/night_plan.json(N))
test ${#plans} -eq 0 || { print "ABORT: existing plan"; exit 1; } # F4
export H=ae8f074ffa554707a9eac95995ab8ec03235d118           # the handback commit; pinned EXPLICITLY (cond. 1)
export DRIVER_SOURCE=/Users/edr/code/JouleWise-wt-magistrate-1ef89702
git -C "$DRIVER_SOURCE" cat-file -e "$H^{commit}" || { print "ABORT: H unavailable"; exit 1; } # F4; cond. 6
now=$(date +%s); test "$now" -ge 1788944160 -a "$now" -lt 1788945300 || { print "ABORT: outside the arm window 01:56-02:15 PDT 2026-09-09 (t0-3600 .. t0-2460)"; exit 1; } # delta N5: enforced floor (ruling B) and ceiling
if ps -p 48645 >/dev/null 2>&1; then print "ABORT: leaked 09-04 python stub pid 48645 alive (not matched by the census regex)"; exit 1; fi # delta N11
# 1. Disposable checkout at H (measurement_root; the installer must be run FROM it).
export STUB_CHECKOUT=/private/tmp/joulewise-rehearsal-20260909-checkout; test ! -e "$STUB_CHECKOUT" || { print "ABORT: stub checkout exists"; exit 1; } # F4
git -C "$DRIVER_SOURCE" worktree add --detach "$STUB_CHECKOUT" "$H" || { print "ABORT: checkout creation failed"; exit 1; } # F4
test "$(git -C "$STUB_CHECKOUT" rev-parse HEAD)" = "$H" || { print "ABORT: checkout pin mismatch"; exit 1; } # F4
# 2. Author to a STAGING path the watchdog glob (~/night-custody/*/night_plan.json) does not match (cond. 2).
export NIGHT_CUSTODY=/Users/edr/night-custody/rehearsal-20260909; test ! -e "$NIGHT_CUSTODY" || { print "ABORT: real custody exists"; exit 1; } # F4   # cond. 3: no prior record
export STAGE=/private/tmp/joulewise-rehearsal-20260909-staging
test ! -e "$STAGE" || { print "ABORT: staging path exists"; exit 1; } # F4
mkdir -p "$STAGE" || { print "ABORT: staging creation failed"; exit 1; } # F4
export SCRATCH=/private/tmp/joulewise-rehearsal-20260909-validate; test ! -e "$SCRATCH" || { print "ABORT: scratch path exists"; exit 1; } # N10: fixed path so block B can re-derive it
mkdir -p "$SCRATCH" || { print "ABORT: scratch creation failed"; exit 1; }
# F5/N3: On any abort after step 1: git -C "$DRIVER_SOURCE" worktree remove --force "$STUB_CHECKOUT"; rm -rf "$STAGE" "$SCRATCH" (only paths this attempt created).
cd "$STUB_CHECKOUT" || { print "ABORT: checkout unavailable"; exit 1; }
PYTHONDONTWRITEBYTECODE=1 python3 -B - <<'PY' || { print "ABORT: plan authoring failed"; exit 1; }
import os, time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from joulewise.night_gate import NightPlan
from joulewise.night_plan_writer import write_night_plan
root = Path(os.environ["NIGHT_CUSTODY"]); H = os.environ["H"]; stage = Path(os.environ["STAGE"])
t0 = datetime(2026, 9, 9, 2, 56, 0, tzinfo=ZoneInfo("America/Los_Angeles")).timestamp(); assert t0 == 1788947760
now = time.time(); assert now < t0 - 25 * 60
plan = NightPlan(plan_id="rehearsal-20260909", receipt_class="REHEARSAL_STUB", t0_epoch_s=t0, window_max_s=900,
    authored_epoch_s=now, repo_head=H, measurement_root=os.environ["STUB_CHECKOUT"], measurement_head=H,
    chain_path=str(root/"chain.zsh"), chain_sha256_path=str(root/"chain.zsh.sha256"), custody_root=str(root),
    registration_path="configs/campaigns/d117_contrast_v5/d166_dominance_criterion_registration.json")
# F5: same authored timestamp and every non-custody field; only three paths differ.
from dataclasses import replace
scratch = Path(os.environ["SCRATCH"]); twin_root = scratch/"custody"
twin = replace(plan, custody_root=str(twin_root), chain_path=str(twin_root/"chain.zsh"),
    chain_sha256_path=str(twin_root/"chain.zsh.sha256"))
print(write_night_plan(stage/"night_plan.json", plan))      # REAL plan, staged and undiscoverable
print(write_night_plan(scratch/"night_plan.json", twin))    # VALIDATION TWIN, never armed
PY
# 3. Validate the TWIN only (F5; cond. 2 covers the whole validation). Stated deviation (delta N9): D-175 cond. 2 literally
#    says `--plan <staged>`; ruling B requirement 3 (21c) authorizes validating the twin instead, and the json diff below
#    proves the twin and the staged real plan differ only in the three custody paths.
# install_night_agent.sh:119-122 creates custody_root/night under SCRATCH, never real custody.
cd "$STUB_CHECKOUT" || { print "ABORT: checkout unavailable"; exit 1; }
scripts/install_night_agent.sh --plan "$SCRATCH/night_plan.json" --hour 2 --minute 56 --render-only "$SCRATCH/render" || { print "ABORT: twin validation failed"; exit 1; }
/usr/bin/plutil -lint "$SCRATCH/render/com.joulewise.night.plist" || { print "ABORT: night plist invalid"; exit 1; }
/usr/bin/plutil -lint "$SCRATCH/render/com.joulewise.night.deadman.plist" || { print "ABORT: deadman plist invalid"; exit 1; }
python3 - <<'PY' || { print "ABORT: twin differs outside custody paths"; exit 1; }
import json, os, sys
from pathlib import Path
real = json.loads((Path(os.environ["STAGE"])/"night_plan.json").read_bytes())
twin = json.loads((Path(os.environ["SCRATCH"])/"night_plan.json").read_bytes())
allowed = {"custody_root", "chain_path", "chain_sha256_path"}
diff = {k for k in real.keys() | twin.keys() if k not in real or k not in twin or real[k] != twin[k]}
print("plan differing fields:", sorted(diff))
sys.exit(0 if diff == allowed else 1)
PY
```

**Between the blocks (manual steps, executed by the arming magistrate with its own tools; the whole-block paste
must stop here — delta N10):**

- 3b (F6, delta N8). Stop every Codex child (`codex-run-v3` seats are reparented to pid 1 and would be foreign) and
  every background task of this session, INCLUDING its own keepalive Monitor (a direct child of the session pid — see
  `21b-rehearsal-20260909-bench/pass3-process-tree-keepalive.txt` — stopped with TaskStop). Confirm
  `ps -axo pid,ppid,command | grep -E "claude (daemon run|bg-spare|bg-pty-host)|--resume"` prints nothing (joulewise-53
  retires those before its stand-down; this session never signals them). A reparented process of this session's own
  is reported foreign by step 4 and MUST abort the arm — fail-closed by design, no allowlist. The arm then continues
  in the SAME turn (no wake source is needed after this point: block B, record, commit, push, exit).
- 5 (cond. 4). Re-check Ed's thread `1a0800cdb282c3f1` for a NO (Gmail `get_thread`); a NO aborts here, before any
  write under `~/night-custody`.

```zsh
# Block B (re-derive every variable; tool shells do not persist exports)
export H=ae8f074ffa554707a9eac95995ab8ec03235d118 DRIVER_SOURCE=/Users/edr/code/JouleWise-wt-magistrate-1ef89702
export STUB_CHECKOUT=/private/tmp/joulewise-rehearsal-20260909-checkout NIGHT_CUSTODY=/Users/edr/night-custody/rehearsal-20260909
export STAGE=/private/tmp/joulewise-rehearsal-20260909-staging SCRATCH=/private/tmp/joulewise-rehearsal-20260909-validate
test -f "$STAGE/night_plan.json" || { print "ABORT: staged plan missing (block A did not complete)"; exit 1; }
now=$(date +%s); test "$now" -ge 1788944160 -a "$now" -lt 1788945300 || { print "ABORT: outside the arm window 01:56-02:15 PDT 2026-09-09 (t0-3600 .. t0-2460)"; exit 1; } # D2
test ! -e ~/night-custody/magistrate/standdown.request || { print "ABORT: standdown requested"; exit 1; } # D4
plans=(~/night-custody/*/night_plan.json(N)); test ${#plans} -eq 0 || { print "ABORT: existing plan"; exit 1; } # D4
test "$(git -C "$STUB_CHECKOUT" rev-parse HEAD)" = "$H" || { print "ABORT: checkout pin mismatch"; exit 1; }
test ! -e "$NIGHT_CUSTODY" || { print "ABORT: real custody exists"; exit 1; }
# 4. Census immediately before the move (cond. 5): every codex|claude|t3 match must be this magistrate's own tree.
python3 - <<'PY' || { print "ABORT: foreign census or census failure"; exit 1; } # F3/F4
import json, os, subprocess, sys
# F3: derive the live activation from its lock.
me = json.load(open(os.path.expanduser("~/night-custody/magistrate/magistrate.lock")))["pid"]
ps = subprocess.run(["ps","-axo","pid=,ppid=,command="], capture_output=True, text=True, check=True).stdout.splitlines()
rows = [(int(l.split(None,2)[0]), int(l.split(None,2)[1]), l.split(None,2)[2] if len(l.split(None,2))>2 else "") for l in ps if l.strip()]
parent = {p:pp for p,pp,_ in rows}
def mine(p):
    while p and p != 1:
        if p == me: return True
        p = parent.get(p, 1)
    return False
import re
foreign = [(p,c[:90]) for p,pp,c in rows if re.search(r"codex|claude|t3", c) and not mine(p) and "ps -axo" not in c]
print("foreign census matches:", foreign); sys.exit(1 if foreign else 0)
PY
# (step 5, the NO check, was executed between the blocks.)
# 6. THE MOVE: atomic rename into the plan directory (same volume as /private/tmp — verified: both device 16777233 per stat -f %d).
# F5: the real custody root is first created by this mkdir immediately before os.replace.
mkdir -p "$NIGHT_CUSTODY" || { print "ABORT: real custody creation failed"; exit 1; } # F4
python3 -c 'import os,sys; os.replace(sys.argv[1], sys.argv[2]); print("moved", sys.argv[2])' "$STAGE/night_plan.json" "$NIGHT_CUSTODY/night_plan.json" || { print "ABORT: atomic move failed"; exit 1; }
# 7. Install both agents FROM the stub checkout with --hour/--minute == t0 local (cond. 3).
cd "$STUB_CHECKOUT" || { print "ABORT: checkout unavailable"; exit 1; }
scripts/install_night_agent.sh --plan "$NIGHT_CUSTODY/night_plan.json" --hour 2 --minute 56 || { print "ABORT: agent install failed AFTER the move — un-publishing the plan this session authored (D-175 line 19 (a) / cond. 8)"; scripts/install_night_agent.sh --plan "$NIGHT_CUSTODY/night_plan.json" --hour 2 --minute 56 --uninstall || true; rm -f "$NIGHT_CUSTODY/night_plan.json"; rmdir "$NIGHT_CUSTODY/night" "$NIGHT_CUSTODY" 2>/dev/null; launchctl list | grep -E "com.joulewise.night" || true; exit 1; } # delta N4 / D1 / D5
launchctl list | grep -E "com.joulewise.night"; rm -rf "$STAGE" "$SCRATCH"
# 8. Record (plan json copy, launchctl list, census output) in this trace dir; commit; push. Stop every child and
#    background process; exit. Request boundary 02:31 PDT 2026-09-09 = t0 − 25 min (cond. 7).
```
On any abort: `git -C "$DRIVER_SOURCE" worktree remove --force "$STUB_CHECKOUT"; rm -rf "$STAGE" "$SCRATCH"` — remove only the
checkout/scratch/staging paths this attempt created (delta N3); if an existence guard found a pre-existing path, preserve it. The real custody root stays untouched before step 6. <!-- F5 -->

## Bench pass 2 (activation 784a764e; first run recorded by commit 82622e70 at 02:11:53 PDT without copied artifacts — delta N2; re-run with artifacts captured under `21b-rehearsal-20260909-bench/pass2-*`, time and epoch in `pass2-bench-output.txt`; scratch paths only)

Steps 1–3 of the amended sequence were executed verbatim with every path redirected to a `mktemp -d` parent
(`/private/tmp/jw-bench-arm.XXXXXX`): a detached worktree at H=`ae8f074f` as `STUB_CHECKOUT`, `NIGHT_CUSTODY` under the
scratch parent (never the real custody root), `STAGE` and `SCRATCH` under it. Observed: `write_night_plan` wrote both the
real staged plan and the validation twin (author rc 0); `scripts/install_night_agent.sh … --render-only` run FROM the H
checkout printed `validated pins: repo_head=ae8f074f… measurement_root=<scratch>/checkout measurement_head=ae8f074f…`
(rc 0); both rendered plists `plutil -lint` OK; the json diff reported `plan differing fields: ['chain_path',
'chain_sha256_path', 'custody_root']` (rc 0); the fake real custody path did NOT exist afterwards, while
`<SCRATCH>/custody/night` did exist (the installer's `mkdir -p "$custody_root/night"`, which is exactly why the twin is
validated instead of the real plan). The bench worktree and parent were removed; `ls ~/night-custody` afterwards shows
only `magistrate`, `magistrate-bench`, `retired-v1`. Steps 4–8 were NOT executed (they arm).
- Artifacts of the re-run: `pass2-bench-output.txt` (full transcript with start/finish times), `pass2-real-staged-night_plan.json`,
  `pass2-twin-night_plan.json`, `pass2-render-com.joulewise.night.plist`, `pass2-render-com.joulewise.night.deadman.plist`.

Cond. 8: any later re-arm or removal of THIS plan by a headless session repeats steps 2–7; everything else on plans,
night records and launchd stays barred by relaunch-prompt line 19 (as amended by D-175).

## Activation succession (2026-09-08 01:48:16 PDT (commit 9a15338e); F2; written by activation 784a764e)

- Activation 1ef89702 (pid 84232) was terminated at 01:33:28 PDT (events.jsonl seq 5, epoch 1788856408): it ended its last turn holding only monitors and a
  45-minute timer, and Claude Code's headless `-p` mode terminates a session 600 s after a turn ends while background
  tasks remain (`attempts/1ef89702-…/attempt-1.stderr.log`: "Background tasks still running after 600s; terminating.
  Set CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=0 to wait indefinitely."). The watchdog recorded `clean activation exit`
  (events seq 5, IDLE), `backoff has not expired` (seq 6, BACKOFF, 300 s), then spawned activation
  `784a764e-12b2-4c9a-a96d-9b8690d6abad` (seq 7–8, 01:41:58 PDT, epoch 1788856918; lock pid 83086, supervisor 83075; `attempt: 2`).
- Consequence for this plan: the arming party is whichever headless activation is live when preconditions (a)+(b)
  hold. The NIGHT_HANDBACK text at H names activation 1ef89702 as the author of the arm request (true: emails
  `1a0800cdb282c3f1`/`1a08012045894ef7` were sent by it); the arm itself is executed and recorded by the live
  activation, whose id and pid go into the arm record (step 8). No re-pin: H stays `ae8f074f`.
- Step 4 derives `me` from the lock the live activation holds; never a constant. <!-- F3/F14 -->
- Relaunch churn (finding for the watchdog owner, joulewise-53; not a process change by this activation): with the
  600 s ceiling, a headless magistrate that ends its turn while waiting is relaunched every ~10 min (5-min backoff +
  ceiling) and each relaunch sends Ed a mandated launch email. Activation 784a764e therefore keeps itself alive with
  a bounded background poll (standdown.request, `~/night-custody/*/night_plan.json`, joulewise-53's pid, a 7-minute
  tick) instead of ending its turn idle; that poll is a direct child of the session pid and is stopped at step 3b
  before the census (delta N8). Launch email for 784a764e: Gmail `1a080326c4d2f147`.
- joulewise-53's answers (cross-session message, 01:48 PDT (recorded in a6bff232 at 01:48:47); F2): (a) the arm-time census must treat the Claude bg-job
  daemon 71666, bg-pty-hosts 71596/71682, bg-spare 71687 and the resumed twin 71607 as foreign matches that must be
  gone; joulewise-53 retires them itself as its last act before stand-down (`claude daemon stop --any`, then verify
  no `claude daemon run|bg-spare|bg-pty-host|--resume` process remains) and states the result in its stand-down
  message; this activation never signals them. The step-4 regex `codex|claude|t3` already matches every one of those
  command lines (all carry `claude` in the binary path or argv), AND the ancestry walk reports them foreign
  because they are reparented to pid 1, which is the intended abort — a non-empty foreign list aborts the arm. <!-- F6 --> (b) PR #296's synthesis (D-175) is the ruling of record for line 19 and the eight conditions
  before it merges. Expected stand-down: ~1–2 h after 01:48 PDT (F2), addressed to joulewise-magistrate-784a764e-12b, with
  the main SHAs of whatever merged (census/daemon branch at 298da021 was in delta re-audit 2 + Opus final-head review).
