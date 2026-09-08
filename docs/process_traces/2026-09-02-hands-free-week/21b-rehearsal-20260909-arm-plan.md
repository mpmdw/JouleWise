# 21b — REHEARSAL_STUB night `rehearsal-20260909`: magistrate ruling on the scout's block, bench pass, and the exact arm-time sequence

Written by headless magistrate activation 1ef89702 at ~01:25 PDT 2026-09-08. NOTHING IS ARMED by this file. The
arm happens only after (a) Ed's arm email has gone out and no NO has arrived, and (b) the interactive session
joulewise-53 has messaged that it stood down (its condition 2: no arming while it or its seats are alive).

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

## Bench pass (2026-09-08 ~01:24 PDT; temporary custody parent, no launchd, real custody untouched)

- `write_night_plan` produced `bench-night_plan.json` (schema v2, t0 1788947760 = 2026-09-09 02:56:00 PDT, window
  900 s, both heads = bench H `4a7a768c`).
- `scripts/install_night_agent.sh --plan … --hour 2 --minute 56 --render-only …` run FROM the disposable checkout:
  `validated pins: repo_head=4a7a768c… measurement_root=/private/tmp/jw-rehearsal-bench-…/checkout
  measurement_head=4a7a768c…`, rc 0; both rendered plists `plutil -lint` OK (copied here).
- `scripts/magistrate_watchdog.py --dry-run` with `MAGISTRATE_WATCHDOG_CUSTODY_ROOT` under the same temp parent
  (so the plan was discovered): `decision=LAUNCHING reason=all launch predicates clear` — a plan whose t0 is tomorrow
  does not hold relaunch.
- The bench worktree and temp custody were removed after copying; nothing under `~/night-custody` was written.

## Exact arm-time sequence (run by the magistrate that arms; every value re-derived at that time)

```zsh
# 0. Preconditions (all must hold): no standdown.request; joulewise-53 has messaged stand-down; Ed's arm email
#    sent and no NO on its thread; no plan under ~/night-custody/*/night_plan.json; now < 2026-09-09 02:00 PDT.
ls ~/night-custody/magistrate/standdown.request 2>/dev/null && exit 1
ls ~/night-custody/*/night_plan.json 2>/dev/null && exit 1
# 1. Rewrite docs/process/NIGHT_HANDBACK.md's three sections (text below) in the magistrate worktree and commit → H.
export DRIVER_SOURCE=/Users/edr/code/JouleWise-wt-magistrate-1ef89702
export H="$(git -C "$DRIVER_SOURCE" rev-parse HEAD)"; git -C "$DRIVER_SOURCE" status --short | grep -q . && exit 1
# 2. Disposable checkout at H (measurement_root for the stub only).
export STUB_CHECKOUT=/private/tmp/joulewise-rehearsal-20260909-checkout; test ! -e "$STUB_CHECKOUT"
git -C "$DRIVER_SOURCE" worktree add --detach "$STUB_CHECKOUT" "$H"
test "$(git -C "$STUB_CHECKOUT" rev-parse HEAD)" = "$H"
# 3. Author the plan (real custody root; the watchdog discovers it as soon as it exists).
export NIGHT_CUSTODY=/Users/edr/night-custody/rehearsal-20260909; test ! -e "$NIGHT_CUSTODY"
cd "$STUB_CHECKOUT" && PYTHONDONTWRITEBYTECODE=1 python3 -B - <<'PY'
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
cd "$STUB_CHECKOUT" && scripts/install_night_agent.sh --plan "$NIGHT_CUSTODY/night_plan.json" --hour 2 --minute 56
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

## NIGHT_HANDBACK.md text for this night (committed as H at arm time; wording fixed here)

**Purpose of this night** — Plan `rehearsal-20260909`, class `REHEARSAL_STUB`, armed by the headless magistrate
(activation 1ef89702, spawned by the relaunch watchdog on 2026-09-08 00:51:55 PDT) for 02:56 local on 2026-09-09
with a 900 s window, inside the 02:45–03:30 belt. It is the fresh post-watchdog rehearsal the state kernel requires
before any real plan (NIGHT-REHEARSAL-01, last acceptance item). The chain is the driver's built-in stub
(`sleep 2; echo REHEARSAL`); no pack, no model, no measurement, no sudo. The plan is v2 and pins its
`measurement_root` to a disposable detached checkout at this commit (`/private/tmp/joulewise-rehearsal-20260909-checkout`),
used only by this stub and removed before any real plan; the measurement checkout of record is untouched. Ed was
emailed the arming notice before the arm; a NO on that thread stands the night down. Expected: `result.json` verdict
`REHEARSAL_ONLY`, chain exit 0; a receipt refusing `night_refused_agent_present` is acceptable for a stub, any other
refusal is a finding. If the agents were installed before 07:00 on 2026-09-08, that morning's dead-man firing stands
down with one log line (the R-7 observable); otherwise this night does not repeat that case.

**Where the results are** — Custody root `/Users/edr/night-custody/rehearsal-20260909/night/` (`result.json`,
`receipt.json` or `refusal.json`, `chain.started`, `chain.exited`, `censuses.jsonl`, `courier.sent`, `courier.json`);
driver log `/Users/edr/night-custody/rehearsal-20260909/night.log`; results branch `night-results/20260909` on
`origin` if the driver's push succeeds (verify, do not presume).

**Next lane** — The relaunched magistrate harvests result, receipt, courier message id and results-branch evidence,
records them under NIGHT-REHEARSAL-01, uninstalls both agents with `--uninstall` from the stub checkout, removes the
stub checkout and plan root, and then sends the stage-1 plan email before any `DIAGNOSTIC_NO_PACK` plan is armed.
Never re-arm the same plan on the same refusal signature twice.

## Arm email (precondition (a)) — SENT

Gmail id `1a0800cdb282c3f1`, 2026-09-08 ~01:27 PDT, subject "JouleWise — ARM REQUEST: rehearsal-20260909
(REHEARSAL_STUB) for 02:56 PDT Tue 9 Sep; launches unless you reply NO". Check that thread for a NO immediately before
step 0 of the arm-time sequence. Precondition (b) (joulewise-53 stand-down message) was still outstanding when this
line was written.

## Handback committed as H; pins on Ed's thread (2026-09-08 ~01:40 PDT)

- H = `ae8f074ffa554707a9eac95995ab8ec03235d118` (NIGHT_HANDBACK.md rewritten for this night). The arm-time sequence
  above uses `H="$(git -C "$DRIVER_SOURCE" rev-parse HEAD)"`; if this branch has moved past `ae8f074f` by arm time
  (it will, by these bookkeeping commits), pin `H=ae8f074ffa554707a9eac95995ab8ec03235d118` EXPLICITLY — the plan must
  pin the commit that rewrote the handback, and the disposable checkout is created at that commit.
- Follow-up on the arm thread with the exact pins (t0, measurement_root, H, class, courier deadline 03:16 PDT):
  Gmail id `1a08012045894ef7`, same thread `1a0800cdb282c3f1`.
- joulewise-53's authority ruling (relaunch-prompt line 19 protects watchdog-owned state and already-armed plans, not
  the documented email-then-arm of a stub) is recorded by that session in the decision log for Ed to see; this
  activation proceeds under it and stops if Ed or a cold gate overturns it. Its condition 4 (no arm until it messages
  stand-down) still binds. pid 48645 (leaked 09-04 test stub magistrate) was retired by joulewise-53; re-check
  `ps -p 48645` at arm time and never signal it from this activation.
