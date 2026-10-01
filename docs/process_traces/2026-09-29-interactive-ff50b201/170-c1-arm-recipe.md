# C1 arm recipe (Revision 6 derivation window), with the harvest and next-arm sections the magistrate reuses

Status: DRAFT written 2026-09-30 from main `67a38879`, read-only. Not executed. The Revision 6 seal (branch `feat/2026-09-30-revision6-seal`) has not merged; every value marked **FILL** is unknown until it does. A step with no command on main is marked **GAP** and is listed in §8. Nothing here arms, installs, runs launchctl, sudo or powermetrics until a human or the orchestrator runs it.

How to read the marks. **FILL** = a value to supply at arm time. **GAP** = no command exists on main (or a command exists but main's code cannot do the step); the gap number points to §8. Every `CHECK:` line in a script is an assertion that stops the script.

Sources this was built from: W1/W2 bench scripts (`docs/process_traces/2026-09-26-activation-22784e38/10-w1-arm/scripts/`, `2026-09-27-activation-3ba66eeb/40-w2-arm/scripts/`), `scripts/gen_derivation_night.py`, `scripts/run_night.py` (`_admit_network_time_off`, `_admit_derivation_clean_dwell`, `_write_start_conditions`), `scripts/harvest_window.py`, `scripts/recover_calibration_ledger.py`, `joulewise/arm_retry.py`, `joulewise/night_gate.py`, `scripts/magistrate_watchdog.py`, the sealable Revision 6 text (`110-rev6-gate/32-revision6-sealable-e1.md`).

## 0. Facts the recipe rests on (each one read from code on main)

- The plan is a v2 `DIAGNOSTIC_NO_PACK` plan (same kind as W1/W2) with `window_max_s` 9000. `gen_derivation_night.py --new-plan` authors a v4 plan that needs a sealed quiet-admission policy and a ruled `cutoff_authority`; none exists (GAP 6). The emit path (`--plan`) accepts a v2 plan and, on main, always requires the Revision 6 start-conditions flags: either `--first-revision6-window-reason TEXT` (first window, null prior) or all four of `--prior-revision6-session`, `--prior-harvest-json`, `--prior-started-epoch-s`, `--prior-terminal-epoch-s` (the prior harvest's `next_window` must authenticate to `NEXT_WINDOW`). Emit, `--verify` and the post-publish `--verify` must each be given the same flags; the manifest `$NIGHT_ROOT/start_conditions_manifest.json` is written once by the first emit and any later difference refuses.
- Session id must match `^d079-epoch-25g83-r6-[0-9]{8}T[0-9]{4}Z$` (the sealed declaration's pattern; the generator enforces it only when the plan's `registration_path` file contains `# Revision 6 (`). This recipe uses the window's t0 in UTC. The plan id, session id, clone and custody paths must not contain `codex`, `claude` or `t3` in any letter case (the driver's census and the clean-dwell script match them anywhere in the process list, including the driver's own command line); step0 checks this.
- Network time: OFF since 2026-09-29T20:34:38Z (`70-ntp-off/receipt-2026-09-29.txt`). The arm owns no OFF step. The driver itself runs `sudo -n /usr/sbin/systemsetup -setusingnetworktime off` at t0 (`run_night._admit_network_time_off`, write-once receipt `night/network_time_off.json`), then runs the 600 s clean dwell (`scripts/prewindow_check.sh --wait --timeout-s N`) during the 600 s OFF settle, then the night gate's own t0 checks, then starts the chain. Sudo is passwordless only for `systemsetup ... off|on` (Ed, 2026-09-29), so the arm cannot read the current state without a password (GAP 8). Registration §5 permits one optional resync (ON, wait, OFF) in the arm step only; it is not needed for correctness and this recipe does not do it.
- The clean dwell refuses while any process-list line contains `codex`, `claude`, `t3`, `mcp-server`, `run_campaign` or `window-chain`. The interactive session, the headless magistrate and a courier all match. If one is alive at t0 the dwell restarts every poll, and after the 45 minute cap (or the remaining start budget) the window becomes a null session.
- Stand-down timing (`scripts/magistrate_watchdog.py`): install close EXCLUDED at t0 - 10 min (`PLAN_LEAD_S` 8 min + `INSTALL_CLOSE_MARGIN_S` 2 min); watchdog REQUEST at t0 - 8 min, TERM at t0 - 6, KILL at t0 - 5 (these act on a watchdog-owned magistrate; the interactive session is not signalled by anyone). The plan span is active from t0 - 8 min to t0 + 9300 s (`window_max_s` + 300 s courier), so harvest (`harvest_window.py` refuses earlier) and the next arm's discovery (`retained_roots` classifies the plan ACTIVE until then) both open at t0 + 9300 s.
- The planner lead floor is `evidence_night.py:101` (`parse_t0("next")` = now + 2400 s, rounded up to a minute). That planner serves `quiet_predicate_evidence`, not this arm; the derivation arm's own code bounds are `authored < t0 - 600` and publication before `t0 - 600`. This recipe takes the 2400 s as the hard floor and uses 3600 s (C1) and 5400 s (C2/C3) as working leads (§1).
- The night gate accepts only a registration whose sha256 is in `night_gate.RULED_REGISTRATIONS` (`_check_registration`); main has D-166 and the QPE-01 protocols, not the Revision 6 file. `harvest_window.py` refuses a Revision 6 harvest unless the plan's `registration_path` file has the same sha256 as `--preregistration-sha256`. Both cannot hold today: GAP 1. Step2 tests the gate half before anything is armed.

## 1. Choose t0 and the times that follow from it

Working lead: C1 `LEAD_S=3600` (orchestrator at the bench), C2/C3 `LEAD_S=5400` (headless magistrate). Hard floor 2400. If the arm is not finished by t0 - 10 min, discard the plan and choose a new t0 (a late publish is refused by `retry_allowed` and by the driver); never edit t0 in a written plan.

```zsh
export LEAD_S=3600     # FILL: 3600 for C1, 5400 for C2/C3, never below 2400
python3 -B - <<'PY'
import math, os, time
from datetime import datetime, timezone
now = time.time()
epoch = math.ceil((now + int(os.environ["LEAD_S"])) / 60) * 60
def ambiguous(e):
    local = datetime.fromtimestamp(e)
    candidates = {local.replace(fold=f).timestamp() for f in (0, 1)}
    return len({c for c in candidates if datetime.fromtimestamp(c) == local}) != 1
while ambiguous(epoch):
    epoch += 60
def show(label, e):
    print(f"{label:34s} {datetime.fromtimestamp(e).astimezone().strftime('%Y-%m-%d %H:%M:%S %Z')}  "
          f"{datetime.fromtimestamp(e, timezone.utc).strftime('%H:%M:%SZ')}  epoch {e}")
print(f"T0_EPOCH_S={epoch}")
show("install close EXCLUDED (t0-10m)", epoch - 600)
show("REQUEST / interactive closed (t0-8m)", epoch - 480)
show("TERM (t0-6m)", epoch - 360)
show("KILL (t0-5m)", epoch - 300)
show("t0: driver starts, OFF + dwell", epoch)
show("chain starts at the earliest (t0+600)", epoch + 600)
show("chain ends about (t0+8280)", epoch + 8280)
show("window end (t0+9000)", epoch + 9000)
show("harvest and next arm open (t0+9300)", epoch + 9300)
PY
```

The printed `T0_EPOCH_S` is the **FILL** for §2. The latest time the interactive session may be open is **t0 - 8 min** (finish every step, send the exit record before t0 - 10 min); it must be closed before t0 in every case, because the dwell starts at t0.

## 2. Bench files (create once; `arm-env.template.zsh` is refilled for each window)

Everything lives in `BENCH=/Users/edr/night-plan-staging/r6-bench`, outside custody discovery and outside every git checkout. There are no tracked Rev 6 step scripts (GAP 5); these heredocs are the only copy, so the magistrate must run them unedited.

```zsh
export BENCH=/Users/edr/night-plan-staging/r6-bench
mkdir -p "$BENCH"
W2=/Users/edr/code/JouleWise/docs/process_traces/2026-09-27-activation-3ba66eeb/40-w2-arm/scripts
# battery_gate() is W2's function, extracted byte for byte (52 lines).
sed -n '/^battery_gate() {/,/^}$/p' "$W2/arm-env.zsh" > "$BENCH/battery-gate.zsh"
test "$(wc -l < "$BENCH/battery-gate.zsh")" -eq 52
# step1 = W2 step1 with its one W2-only basename assertion replaced.
sed 's#^\[\[ "\$MEASUREMENT_ROOT" == .*derivation-w2 \]\] || exit 3#[[ "$MEASUREMENT_ROOT" == /Users/edr/night-custody/measurement/JouleWise-measurement-${T0_UTC}-r6-${WINDOW_LABEL} ]] || exit 3#' \
  "$W2/step1-clone.zsh" > "$BENCH/step1-clone.zsh"
test "$(grep -c 'derivation-w2' "$BENCH/step1-clone.zsh")" -eq 0
# step5 = W2 step5 unchanged.
cp "$W2/step5-verify-and-exit.zsh" "$BENCH/step5-verify-and-exit.zsh"
```

```zsh
cat > "$BENCH/arm-env.template.zsh" <<'EOF_ENV'
#!/bin/zsh
set -euo pipefail
export BENCH=/Users/edr/night-plan-staging/r6-bench
# ---- values substituted by the fill command in section 3 ----
export H='__H__'                       # 40 hex: remote main after the seal merge (and after the prior window's harvest PR for C2/C3)
export T0_EPOCH_S='__T0__'             # section 1
export WINDOW_LABEL='__LABEL__'        # c1 | c2 | c3
export PREREG_SHA256='__PREREG__'      # sha256 of the sealed registration file at H
export PRIOR_SESSION_ID='__PRIOR_SESSION__'       # empty for C1
export PRIOR_HARVEST_JSON='__PRIOR_HARVEST__'     # empty for C1
export PRIOR_STARTED_EPOCH_S='__PRIOR_STARTED__'  # empty for C1
export PRIOR_TERMINAL_EPOCH_S='__PRIOR_TERMINAL__' # empty for C1
export LEDGER_SOURCE='__LEDGER_SOURCE__'
export LEDGER_SOURCE_EXPECTED_SHA256='__LEDGER_SHA__'
# ---- fixed ----
export TZ=America/Los_Angeles PYTHONDONTWRITEBYTECODE=1
unset PYTHONPATH
export CANON=/Users/edr/code/JouleWise
export REMOTE_URL=https://github.com/mpmdw/JouleWise
export REG_PATH='configs/calibration/preregistration_d079_epoch_25g83_rev1.md'
export T0_UTC="$(TZ=UTC date -r "$T0_EPOCH_S" +%Y%m%dT%H%MZ)"
export NIGHT_DATE="$T0_UTC"
export SESSION_ID="d079-epoch-25g83-r6-$T0_UTC"
export PLAN_ID="d079-epoch-25g83-r6-derivation-$WINDOW_LABEL-$T0_UTC"
export EVIDENCE_ROOT_ID="evidence-$PLAN_ID"
export MEASUREMENT_ROOT="/Users/edr/night-custody/measurement/JouleWise-measurement-$T0_UTC-r6-$WINDOW_LABEL"
export PY="$MEASUREMENT_ROOT/.venv/bin/python"
export NIGHT_ROOT="/Users/edr/night-custody/$PLAN_ID"
export STAGE="/Users/edr/night-plan-staging/$PLAN_ID"
export STAGED_PLAN="$STAGE/night_plan.json"
export PLAN="$NIGHT_ROOT/night_plan.json"
export CALIBRATION_PLAN="$NIGHT_ROOT/calibration_plan.json"
export FROZEN_PLAN_REL="configs/campaigns/d117_floor_qwen25_1p5b_v3/calibration_plan.json"
export FROZEN_PLAN_SHA256=9ab4776f3c416284d6d01a5a49587eedcdfbcb8ef61428cdc1046e9b9d74a072
export CALIBRATION_LEDGER="$MEASUREMENT_ROOT/runs/calibration_observation_ledger.jsonl"
export LEDGER_HEAD_PIN="$MEASUREMENT_ROOT/configs/calibration/calibration_ledger_head.json"
export PATH="$MEASUREMENT_ROOT/.venv/bin:$PATH"
export ARM_ATTEMPT=1 ATTEMPT_DIR="$STAGE/arm-attempts/000001"
export FIRST_WINDOW_REASON='C1 is the first session of Revision 6; no earlier Revision 6 session exists, so start conditions (a) and (b) have nothing to test (Revision 6 section 6.2).'
if [[ -n "$PRIOR_SESSION_ID" ]]; then
  MANIFEST_FLAGS=(--prior-revision6-session "$PRIOR_SESSION_ID" --prior-harvest-json "$PRIOR_HARVEST_JSON"
                  --prior-started-epoch-s "$PRIOR_STARTED_EPOCH_S" --prior-terminal-epoch-s "$PRIOR_TERMINAL_EPOCH_S")
else
  MANIFEST_FLAGS=(--first-revision6-window-reason "$FIRST_WINDOW_REASON")
fi
source "$BENCH/battery-gate.zsh"
EOF_ENV
```

```zsh
cat > "$BENCH/step0-discover.zsh" <<'EOF_S0'
#!/bin/zsh
set -euo pipefail
source /Users/edr/night-plan-staging/r6-bench/arm-env.zsh
cd "$CANON" || exit 3
print -- "CHECK: no unfilled placeholder in arm-env.zsh"
if grep -n '__[A-Z_]*__' "$BENCH/arm-env.zsh"; then echo "unfilled placeholder"; exit 3; fi
print -- "CHECK: H, PREREG_SHA256 and T0_EPOCH_S are well formed; t0 is minute aligned and at least 2400 s ahead"
[[ "$H" =~ '^[0-9a-f]{40}$' && "$PREREG_SHA256" =~ '^[0-9a-f]{64}$' && "$T0_EPOCH_S" =~ '^[0-9]+$' ]] || exit 3
(( T0_EPOCH_S % 60 == 0 )) || exit 3
(( T0_EPOCH_S - $(date +%s) >= 2400 )) || { echo "lead below the 2400 s floor"; exit 3; }
print -- "CHECK: session id matches the sealed pattern"
[[ "$SESSION_ID" =~ '^d079-epoch-25g83-r6-[0-9]{8}T[0-9]{4}Z$' ]] || exit 3
print -- "CHECK: no codex, claude or t3 in any id or path (census and clean-dwell substrings, any case)"
for v in "$SESSION_ID" "$PLAN_ID" "$EVIDENCE_ROOT_ID" "$MEASUREMENT_ROOT" "$NIGHT_ROOT" "$STAGE"; do
  l="${(L)v}"
  [[ "$l" != *codex* && "$l" != *claude* && "$l" != *t3* ]] || { echo "census substring in $v"; exit 3; }
done
print -- "CHECK: os_build is 25G83"
test "$(sw_vers -buildVersion)" = 25G83
print -- "CHECK: no com.joulewise.night* label loaded, no plist on disk"
loaded_labels="$(launchctl list | awk '$3 ~ /^com[.]joulewise[.]night/ {print $3}')"
print -r -- "$loaded_labels"; test -z "$loaded_labels"
agent_plists=(~/Library/LaunchAgents/com.joulewise.night*.plist(N))
print -rl -- "${agent_plists[@]}"; (( ${#agent_plists} == 0 )) || exit 3
print -- "CHECK: every /Users/edr/night-custody/*/night_plan.json is terminal (prior window included)"
python3 -B - <<'PY'
import json
from joulewise.evidence_night import retained_roots
result = retained_roots({"roots_under": "/Users/edr"})
for row in result["inventory"]:
    print(json.dumps({**row, "classification": "TERMINAL" if row["classification"] == "retained" else row["classification"]}, sort_keys=True), flush=True)
print("CHECK: result['verdict'] == 'pass'", flush=True)
assert result["verdict"] == "pass", "active or unknown sibling plan (the previous window is active until its t0 + 9300 s)"
PY
test ! -L /Users/edr/night-custody/measurement
mkdir -p /Users/edr/night-custody/measurement
print -- "CHECK: staging directory absent before the first battery observation"
test ! -e "$STAGE"; test ! -L "$STAGE"
mkdir -p "$STAGE"
print -- "CHECK: battery connected, not charging, signed current within 200 mA, gauge age <= 180 s (Revision 6 start condition e)"
battery_gate | tee -a "$STAGE/battery-gate.txt"
echo "STEP0 OK"
EOF_S0
```

```zsh
cat > "$BENCH/step2-desk.zsh" <<'EOF_S2'
#!/bin/zsh
set -euo pipefail
source /Users/edr/night-plan-staging/r6-bench/arm-env.zsh
cd "$MEASUREMENT_ROOT" || exit 3
print -- "CHECK: clone HEAD equals H and the tree is clean"
test "$(git rev-parse HEAD)" = "$H"
test -z "$(git status --porcelain=v1 --untracked-files=all)"
print -- "CHECK: sealed registration digest, sealed declaration, every pin, gate acceptance of the registration"
"$PY" -B - <<'PY'
import hashlib, json, os, re
from pathlib import Path
from scripts.issue_calibration_acceptance_generation import revision_six_declaration
from joulewise import night_gate
from joulewise.powermetrics_fiducial import DETECTION_PROJECTION_CELL_BUDGET
e = os.environ
reg = Path(e["REG_PATH"]); raw = reg.read_bytes(); text = raw.decode()
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
print("CHECK: sha256(registration) == PREREG_SHA256", flush=True)
assert hashlib.sha256(raw).hexdigest() == e["PREREG_SHA256"]
print("CHECK: no unfilled seal pin", flush=True)
assert len(re.findall(r"TO BE PINNED AT S[E]AL", text)) == 0
print("CHECK: declaration parses (refuses unless sealed, pattern, count rule)", flush=True)
d = revision_six_declaration(text); pins = d["pins"]
expect = {"chain_sha256": "scripts/night_chains/calibration_derivation_only.zsh",
          "validator_sha256": "scripts/validate_powermetrics_fiducial.py",
          "prewindow_check_sha256": "scripts/prewindow_check.sh"}
for key, path in expect.items():
    print(f"CHECK: sha256({path}) == pins.{key}", flush=True)
    assert sha(path) == pins[key], key
for path, value in pins["estimator_code_sha256"].items():
    print(f"CHECK: sha256({path}) == pins.estimator_code_sha256", flush=True)
    assert sha(path) == value, path
print("CHECK: both launch templates are the pinned pair", flush=True)
assert sorted(sha(p) for p in ("configs/launchd/com.joulewise.night.plist.template",
                               "configs/launchd/com.joulewise.night-probe.plist.template")) == sorted(pins["launch_template_sha256"])
print("CHECK: pins.cap_cells == the code's cell budget", flush=True)
assert pins["cap_cells"] == DETECTION_PROJECTION_CELL_BUDGET == 1_710_000
if not e["PRIOR_SESSION_ID"]:
    pin = json.loads(Path(e["LEDGER_HEAD_PIN"]).read_text()); first = pins["ledger_head_pin_at_first_window"]
    print("CHECK: first window: committed ledger pin == pins.ledger_head_pin_at_first_window", flush=True)
    assert (pin["sequence"], pin["head_digest"]) == (first["sequence"], first["digest"])
print("CHECK: the night gate would accept this registration (GAP 1: main's RULED_REGISTRATIONS)", flush=True)
assert night_gate.armable_registration(e["PREREG_SHA256"]) is not None, "GAP 1: the gate refuses this registration at t0; do not arm"
print("step2 pins PASS")
PY
mkdir -p "$NIGHT_ROOT" "$STAGE"
test "$(stat -f %d "$NIGHT_ROOT")" = "$(stat -f %d "$STAGE")"
print -- "CHECK: frozen calibration plan digest, byte copy into custody"
test "$(shasum -a 256 "$FROZEN_PLAN_REL" | cut -d' ' -f1)" = "$FROZEN_PLAN_SHA256"
cp "$FROZEN_PLAN_REL" "$CALIBRATION_PLAN"; cmp "$FROZEN_PLAN_REL" "$CALIBRATION_PLAN"
"$PY" scripts/write_derivation_night_inputs.py --out-dir "$NIGHT_ROOT"
print -- "CHECK: live identity epoch equals the sealed declaration's identity epoch"
"$PY" -B - <<'PY'
import json, os
from pathlib import Path
from scripts.issue_calibration_acceptance_generation import revision_six_declaration
from joulewise.calibration_ledger import IDENTITY_EPOCH_FIELDS
e = os.environ
declared = revision_six_declaration(Path(e["REG_PATH"]).read_text())["identity_epoch"]
live = json.loads((Path(e["NIGHT_ROOT"]) / "identity-epoch.json").read_text())
for field in IDENTITY_EPOCH_FIELDS:
    print(f"CHECK: identity {field}: live {live[field]!r} == declared {declared[field]!r}", flush=True)
    assert str(live[field]) == str(declared[field]), field
PY
"$PY" -B - <<'PY'
import os, time
from pathlib import Path
from joulewise.night_gate import NightPlan
from joulewise.night_plan_writer import write_night_plan
e = os.environ
a = int(time.time()); t = int(e["T0_EPOCH_S"])
print("CHECK: t0 minute aligned, 0 <= t0 - authored <= 129600 and authored < t0 - 600", flush=True)
assert t % 60 == 0 and 0 <= t - a <= 129600 and a < t - 600, (t, a)
plan = NightPlan.from_mapping({
    "schema": "joulewise.night_plan.v2", "schema_version": 2,
    "plan_id": e["PLAN_ID"], "receipt_class": "DIAGNOSTIC_NO_PACK",
    "t0_epoch_s": t, "window_max_s": 9000, "authored_epoch_s": a,
    "repo_head": e["H"], "measurement_root": e["MEASUREMENT_ROOT"], "measurement_head": e["H"],
    "chain_path": e["NIGHT_ROOT"] + "/chain.zsh", "chain_sha256_path": e["NIGHT_ROOT"] + "/chain.zsh.sha256",
    "custody_root": e["NIGHT_ROOT"], "registration_path": e["REG_PATH"]})
target = Path(e["STAGED_PLAN"])
assert not target.exists() and not target.is_symlink()
print(write_night_plan(target, plan))
PY
gen() { "$PY" -B scripts/gen_derivation_night.py --plan "$STAGED_PLAN" --session-id "$SESSION_ID" --evidence-root-id "$EVIDENCE_ROOT_ID" --calibration-plan "$CALIBRATION_PLAN" --identity-epoch-json "$NIGHT_ROOT/identity-epoch.json" --t1-bindings-json "$NIGHT_ROOT/t1-bindings.json" "${MANIFEST_FLAGS[@]}" "$@"; }
"$PY" -B scripts/gen_derivation_night.py --check
gen
gen --verify
/bin/zsh -n "$NIGHT_ROOT/chain.zsh"
"$PY" -B scripts/run_night.py preflight --plan "$STAGED_PLAN"
scripts/install_night_agent.sh --plan "$STAGED_PLAN" --python "$PY" --render-only "$STAGE/rendered-agents"
"$PY" -B - <<'PY'
import hashlib, json, os, plistlib
from pathlib import Path
directory = Path(os.environ["STAGE"]) / "rendered-agents"
paths = sorted(directory.glob("*.plist"))
assert {p.name for p in paths} == {"com.joulewise.night.plist", "com.joulewise.night.deadman.plist",
                                   "com.joulewise.night-probe." + os.environ["PLAN_ID"] + ".plist"}
evidence = {}
for path in paths:
    raw = path.read_bytes(); plist = plistlib.loads(raw)
    print(f"CHECK: {path.name} ProcessType == Interactive", flush=True)
    assert plist["ProcessType"] == "Interactive"
    evidence[plist["Label"]] = {"ProcessType": plist["ProcessType"], "rendered_plist_sha256": hashlib.sha256(raw).hexdigest(), "path": str(path)}
(Path(os.environ["STAGE"]) / "render-context.json").write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n")
PY
"$PY" -B scripts/run_night.py schedule --plan "$STAGED_PLAN" > "$STAGE/schedule.json"; cat "$STAGE/schedule.json"
ls -la "$NIGHT_ROOT" "$STAGE"
echo "STEP2 OK"
EOF_S2
```

```zsh
cat > "$BENCH/step3-notice.zsh" <<'EOF_S3'
#!/bin/zsh
set -euo pipefail
source /Users/edr/night-plan-staging/r6-bench/arm-env.zsh
cd "$MEASUREMENT_ROOT" || exit 3
mkdir -p "$STAGE/arm-attempts"; mkdir "$ATTEMPT_DIR"
cp "$STAGED_PLAN" "$ATTEMPT_DIR/plan.json"; print '[]' > "$ATTEMPT_DIR/attempts.json"
cmp "$STAGED_PLAN" "$ATTEMPT_DIR/plan.json"
"$PY" -B -m joulewise.arm_census --plan "$STAGED_PLAN" | tee "$ATTEMPT_DIR/arm-census-1.json"
sleep 30
"$PY" -B -m joulewise.arm_census --plan "$STAGED_PLAN" | tee "$ATTEMPT_DIR/arm-census-2.json"
set +e; /usr/bin/pgrep -lf 'codex|claude|t3' > "$ATTEMPT_DIR/raw-pgrep.txt"; pgrep_rc=$?; set -e
cat "$ATTEMPT_DIR/raw-pgrep.txt"   # expected now: this session and the magistrate only; every one must be gone before t0
"$PY" -B - <<'PY' > "$ATTEMPT_DIR/notice-body.txt"
import hashlib, json, os
from datetime import datetime, timezone
from pathlib import Path
from joulewise.night_gate import NightPlan
from scripts.run_night import schedule
e = os.environ
def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
raw = Path(e["STAGED_PLAN"]).read_bytes(); p = json.loads(raw)
s = schedule(NightPlan.from_mapping(p)); t = p["t0_epoch_s"]
render = json.loads((Path(e["STAGE"]) / "render-context.json").read_text())
pin = json.loads(Path(e["LEDGER_HEAD_PIN"]).read_text())
def stamp(label, v):
    print(f"  {label}: {datetime.fromtimestamp(v).astimezone().isoformat()} = {datetime.fromtimestamp(v, timezone.utc).isoformat()} (epoch {v})")
first = not e["PRIOR_SESSION_ID"]
print("To: claude2.glaring610@passmail.net")
print(f'Subject: NIGHT NOTICE — {p["plan_id"]} (DIAGNOSTIC_NO_PACK) — attempt 1')
print("\nEd,\n")
print("No action is needed unless you want to stop this window; reply NO to this message (or post NO on a directive issue) and it is stopped. Your NO overrides.")
print()
print(f"What this is. Window {e['WINDOW_LABEL'].upper()} of the calibration campaign registered as Revision 6 (sealed registration sha256 {e['PREREG_SHA256']}). "
      "A window is one unattended measurement run: 12 captures of the Mac's power sampler (powermetrics) while the machine idles with no agent or other work on it. "
      "Revision 6 allows windows back to back (no 6 hour gap), up to 3 counting windows plus one replacement; each window's own blind checks decide whether another follows.")
print("Why. Two things are being tested at once: the search limit of 1,710,000 candidate timing positions per capture (raised from 165,000 because 8 of the 24 W1/W2 captures hit the old limit), and whether the 12 or more valid captures the new calibration needs can be collected. The decision after each window is made from counts only, never from the measured values.")
print("Network time is OFF (set 2026-09-29) and the driver re-issues and waits 600 s on it at the window's start; the machine must also be clean for 600 s (no busy daemons, load at most 2.0, AC power, no agent process in the process list) before the chain starts.")
print("First window: no earlier Revision 6 window exists; start conditions (a) and (b) have nothing to test." if first else
      f"Prior window: {e['PRIOR_SESSION_ID']}; its harvest {e['PRIOR_HARVEST_JSON']} decided NEXT_WINDOW (the start-conditions manifest pins that decision by digest).")
print(f"Ledger head at this arm: sequence {pin['sequence']} digest {pin['head_digest']}.")
print("\nKeep every agent session closed and the machine untouched from t0 - 8 minutes through completion. The interactive session must be closed by the REQUEST time below; an announcement does not end a process.")
print("\nTimes (local = UTC):")
for k, v in [("install close EXCLUDED", t-600), ("REQUEST / interactive closed BEFORE", t-480), ("TERM", t-360), ("KILL", t-300),
             ("t0 (driver starts: OFF receipt, 600 s dwell, gate)", t), ("window end", t+9000), ("completion / harvest opens", t+9300), ("daily dead-man", s["deadman_epoch_s"])]:
    stamp(k, v)
print("\nIdentifiers:")
print("  receipt_class: DIAGNOSTIC_NO_PACK   attempt: 1")
print("  plan_id:", p["plan_id"], "\n  session_id:", e["SESSION_ID"])
print("  repo_head = measurement_head = H:", e["H"])
print("  clone:", e["MEASUREMENT_ROOT"], "\n  custody:", e["NIGHT_ROOT"])
print("  plan sha256:", hashlib.sha256(raw).hexdigest(), " authored_epoch_s:", p["authored_epoch_s"])
print("  registration:", e["REG_PATH"], "sha256", e["PREREG_SHA256"])
print("  frozen calibration plan:", e["FROZEN_PLAN_REL"], "sha256", e["FROZEN_PLAN_SHA256"])
for f in [e["CALIBRATION_PLAN"], e["NIGHT_ROOT"]+"/chain.zsh", e["NIGHT_ROOT"]+"/identity-epoch.json", e["NIGHT_ROOT"]+"/t1-bindings.json",
          e["NIGHT_ROOT"]+"/start_conditions_manifest.json", e["MEASUREMENT_ROOT"]+"/scripts/night_chains/calibration_derivation_only.zsh",
          e["MEASUREMENT_ROOT"]+"/scripts/prewindow_check.sh"]:
    print("  ", f, "sha256", digest(f))
for label, item in sorted(render.items()):
    print("  ", label, "ProcessType=Interactive", item["path"], "sha256", item["rendered_plist_sha256"])
print("\nNo model runs. No measured value is read before the session is terminal. A refusal at start is a null session, not a window.")
PY
"$PY" -B - <<'PY'
import hashlib, json, os
from pathlib import Path
d = Path(os.environ["ATTEMPT_DIR"]); raw = (d / "plan.json").read_bytes(); p = json.loads(raw)
n = dict(accepted=False, attempt=1, blocking_causes=[], latest_abort_epoch_s=None, latest_no_epoch_s=None,
         measurement_head=p["measurement_head"], message_id="__MESSAGE_ID__", thread_id="__THREAD_ID__",
         plan_id=p["plan_id"], plan_sha256=hashlib.sha256(raw).hexdigest(), prerequisites_clear=False,
         receipt_class=p["receipt_class"], sent_epoch_s="__SENT_EPOCH__", veto_clear=False)
with (d / "notice.json").open("x") as f:
    json.dump(n, f, indent=2); f.write("\n")
PY
cat "$ATTEMPT_DIR/notice-body.txt"
echo "STEP3 prepared only: send the body by Gmail, then run step3b. OK"
EOF_S3
```

```zsh
cat > "$BENCH/step3b-notice-record.zsh" <<'EOF_S3B'
#!/bin/zsh
# usage: MSG_ID=... THREAD_ID=... SENT_EPOCH_S=... PREREQ_CLEAR=true VETO_CLEAR=true zsh step3b-notice-record.zsh
set -euo pipefail
source /Users/edr/night-plan-staging/r6-bench/arm-env.zsh
: "${MSG_ID:?}" "${THREAD_ID:?}" "${SENT_EPOCH_S:?}" "${PREREQ_CLEAR:?}" "${VETO_CLEAR:?}"
test -s "$ATTEMPT_DIR/notice-evidence.txt"
"$PY" -B - <<'PY'
import json, os
from pathlib import Path
d = Path(os.environ["ATTEMPT_DIR"]); n = json.loads((d / "notice.json").read_text())
n.update(accepted=True, message_id=os.environ["MSG_ID"], thread_id=os.environ["THREAD_ID"],
         sent_epoch_s=float(os.environ["SENT_EPOCH_S"]),
         prerequisites_clear=os.environ["PREREQ_CLEAR"] == "true", veto_clear=os.environ["VETO_CLEAR"] == "true")
(d / "notice.json").write_text(json.dumps(n, indent=2) + "\n")
print(json.dumps(n, indent=2))
PY
EOF_S3B
```

```zsh
cat > "$BENCH/step4-publish-install.zsh" <<'EOF_S4'
#!/bin/zsh
set -euo pipefail
source /Users/edr/night-plan-staging/r6-bench/arm-env.zsh
cd "$MEASUREMENT_ROOT" || exit 3
print -- "CHECK: strictly before install close (t0 - 600 s) with 120 s in hand"
(( $(date +%s) < T0_EPOCH_S - 720 )) || { echo "too late: choose a new t0"; exit 3; }
echo "== pre-publication observations $(date '+%Y-%m-%dT%H:%M:%S%z')"
M=/Users/edr/night-custody/magistrate
print -- "CHECK: no standdown.request"
test ! -e "$M/standdown.request"
if [[ -e "$M/STOP" ]]; then
  # The owner-pause STOP file holds the headless magistrate; it is not a NO on a night.
  # Publication may proceed only with the owner's recorded words authorising this arm (GAP 9).
  print -- "STOP present: $(cat "$M/STOP")"
  test -s "$BENCH/owner-arm-auth.txt" || { echo "STOP present and no owner authorisation recorded in $BENCH/owner-arm-auth.txt"; exit 3; }
  cat "$BENCH/owner-arm-auth.txt"
else
  echo "STOP: absent"
fi
print -- "CHECK: no remote stop branch (ops/stop*)"
test -z "$(git ls-remote "$REMOTE_URL" 'refs/heads/ops/stop*')"
gh issue list --repo mpmdw/JouleWise --label directive --state open --author mpmdw --json number,title,body,author > "$ATTEMPT_DIR/directives-prepub.json"
cat "$ATTEMPT_DIR/directives-prepub.json"   # read every body: any NO or stop is a stop
test -s "$ATTEMPT_DIR/notice-evidence.txt"
test "$(git rev-parse HEAD)" = "$H"
test -z "$(git status --porcelain=v1 --untracked-files=all)"
git fetch origin main
print -- "CHECK: H is an ancestor of origin/main"
git merge-base --is-ancestor "$H" origin/main
cmp "$STAGED_PLAN" "$ATTEMPT_DIR/plan.json"
"$PY" -B scripts/gen_derivation_night.py --plan "$STAGED_PLAN" --session-id "$SESSION_ID" --evidence-root-id "$EVIDENCE_ROOT_ID" --calibration-plan "$CALIBRATION_PLAN" --identity-epoch-json "$NIGHT_ROOT/identity-epoch.json" --t1-bindings-json "$NIGHT_ROOT/t1-bindings.json" "${MANIFEST_FLAGS[@]}" --verify
"$PY" -B - <<'PY'
import json, os, time
from pathlib import Path
from joulewise.night_gate import NightPlan
from scripts.run_night import install_close_epoch
e = os.environ
plan = NightPlan.from_mapping(json.loads(Path(e["STAGED_PLAN"]).read_text()))
assert plan.repo_head == plan.measurement_head == e["H"]
assert plan.measurement_root == e["MEASUREMENT_ROOT"] and plan.custody_root == e["NIGHT_ROOT"]
assert plan.receipt_class == "DIAGNOSTIC_NO_PACK" and plan.window_max_s == 9000
assert plan.chain_path == e["NIGHT_ROOT"] + "/chain.zsh" and plan.chain_sha256_path == plan.chain_path + ".sha256"
assert plan.registration_path == e["REG_PATH"] and plan.t0_epoch_s == int(e["T0_EPOCH_S"])
assert 0 <= time.time() - plan.authored_epoch_s <= 36 * 3600 and 0 <= plan.t0_epoch_s - plan.authored_epoch_s <= 36 * 3600
assert time.time() < install_close_epoch(plan)
assert Path(e["STAGE"]).stat().st_dev == Path(e["NIGHT_ROOT"]).stat().st_dev
print("staged plan checks PASS")
PY
scripts/install_night_agent.sh --render-only "$STAGE/rendered-agents-2" --plan "$STAGED_PLAN" --python "$PY"
"$PY" -B - <<'PY'
import hashlib, json, os
from pathlib import Path
evidence = json.loads((Path(os.environ["STAGE"]) / "render-context.json").read_text())
for label, item in sorted(evidence.items()):
    raw = (Path(os.environ["STAGE"]) / "rendered-agents-2" / f"{label}.plist").read_bytes()
    print(f"CHECK: {label} re-renders to the digest the notice carried", flush=True)
    assert hashlib.sha256(raw).hexdigest() == item["rendered_plist_sha256"]
PY
echo "== final arm census"
"$PY" -B -m joulewise.arm_census --plan "$STAGED_PLAN" | tee "$ATTEMPT_DIR/arm-census-final.json"
print -- "CHECK: second battery gate immediately before publication"
battery_gate | tee -a "$STAGE/battery-gate.txt"
test "$(grep -c '^BATTERY GATE PASS$' "$STAGE/battery-gate.txt")" -eq 2
echo "== publication"
"$PY" -B - <<'PY'
import json, os, time
from pathlib import Path
from joulewise.arm_retry import retry_allowed
from joulewise.night_gate import NightPlan, PLAN_MAX_AGE_S
from scripts.run_night import install_close_epoch
e = os.environ; d = Path(e["ATTEMPT_DIR"]); raw = Path(e["STAGED_PLAN"]).read_bytes()
p = NightPlan.from_mapping(json.loads(raw)); n = json.loads((d / "notice.json").read_text())
attempts = json.loads((d / "attempts.json").read_text())
assert n["attempt"] == int(e["ARM_ATTEMPT"]) and attempts == []
assert not any("__" in str(n[k]) for k in ("message_id", "thread_id", "sent_epoch_s")), "unfilled notice"
context = dict(plan_bytes=raw, saved_plan_bytes=(d / "plan.json").read_bytes(), reviewed_head=e["H"],
               install_close_epoch_s=install_close_epoch(p), plan_max_age_s=PLAN_MAX_AGE_S)
r = retry_allowed(time.time(), context, attempts, n)
print("retry_allowed:", r, flush=True)
if not r.allowed:
    print("REFUSED:", r.reason, "-- staged plan untouched", flush=True); raise SystemExit(3)
target = Path(e["PLAN"])
assert not target.exists() and not target.is_symlink()
os.replace(e["STAGED_PLAN"], target)
print("PUBLISHED", target, time.time())
PY
"$PY" -B scripts/gen_derivation_night.py --plan "$PLAN" --session-id "$SESSION_ID" --evidence-root-id "$EVIDENCE_ROOT_ID" --calibration-plan "$CALIBRATION_PLAN" --identity-epoch-json "$NIGHT_ROOT/identity-epoch.json" --t1-bindings-json "$NIGHT_ROOT/t1-bindings.json" "${MANIFEST_FLAGS[@]}" --verify
echo "== launchd probe $(date '+%H:%M:%S')"
scripts/install_night_agent.sh --plan "$PLAN" --python "$PY" --launchd-probe
cat "$NIGHT_ROOT/night_probe_receipt.json"
"$PY" -B - <<'PY'
import json, os
from pathlib import Path
from joulewise.night_agent_install import LABELS, probe_label
r = json.loads((Path(os.environ["NIGHT_ROOT"]) / "night_probe_receipt.json").read_text())
assert r["schema"] == "joulewise.night_probe_receipt.v2" and r["outcome"] == "ok"
c = r["cadence"]
assert c["passed"] is True and c["count"] == 300 and 0 <= c["elapsed_s"] <= 55 and c["bound_s"] == 55
assert 0 < c["median_ms"] <= 150 and 0 < c["p95_ms"] and 0 < c["max_ms"] <= 200
assert r["ProcessType"] == "Interactive"
assert set(r["launch_context"]) == set(LABELS) | {probe_label(os.environ["PLAN_ID"])}
assert all(i["ProcessType"] == "Interactive" and len(i["rendered_plist_sha256"]) == 64 for i in r["launch_context"].values())
assert r["custody_elapsed_s"] * 3 * 1.5 <= r["custody_budget_s"]
print("PROBE ADMITS")
PY
echo "== install $(date '+%H:%M:%S')"
scripts/install_night_agent.sh --plan "$PLAN" --python "$PY"
launchctl list | grep joulewise
echo "STEP4 OK"
EOF_S4
```

## 3. Run order for one window (C1 shown; C2/C3 differ only in the fill command's prior-window values from §7)

Every step is run from a foreground shell and its whole output kept under `$ATTEMPT_DIR` or the arm record; a nonzero exit or any failed `CHECK:` stops the arm. Do not merge anything to main, and do not run `git fetch`, `pull` or `checkout` in `/Users/edr/code/JouleWise`, from step1 until the window is harvested.

```zsh
# 3.0 Fill (C1 values shown; every FILL must be replaced by its real value)
export NEW_H='FILL: git ls-remote https://github.com/mpmdw/JouleWise refs/heads/main, after the seal has merged'
export NEW_T0='FILL: T0_EPOCH_S from section 1'
export NEW_LABEL=c1
# zsh: write "${NEW_H}:path", never "$NEW_H:path" (zsh reads :c as a modifier; C1's first fill produced the empty-file digest e3b0c442…, caught before step2)
export NEW_PREREG='FILL: shasum -a 256 of the sealed configs/calibration/preregistration_d079_epoch_25g83_rev1.md at NEW_H (git show NEW_H:<path> | shasum -a 256)'
export NEW_PRIOR_SESSION='' NEW_PRIOR_HARVEST='' NEW_PRIOR_STARTED='' NEW_PRIOR_TERMINAL=''
# C1's ledger is W2's: 276 rows, pin 276 (configs/calibration/calibration_ledger_head.json on main). Observed 2026-09-30, re-verify with shasum at step1:
export NEW_LEDGER_SOURCE=/Users/edr/night-custody/measurement/JouleWise-measurement-20260927-derivation-w2/runs/calibration_observation_ledger.jsonl
export NEW_LEDGER_SHA=23f72c37cb2483faa1b31a603996b86d6b7b390ce9460f490699501cfc971c7d
sed -e "s#__H__#$NEW_H#" -e "s#__T0__#$NEW_T0#" -e "s#__LABEL__#$NEW_LABEL#" -e "s#__PREREG__#$NEW_PREREG#" \
    -e "s#__PRIOR_SESSION__#$NEW_PRIOR_SESSION#" -e "s#__PRIOR_HARVEST__#$NEW_PRIOR_HARVEST#" \
    -e "s#__PRIOR_STARTED__#$NEW_PRIOR_STARTED#" -e "s#__PRIOR_TERMINAL__#$NEW_PRIOR_TERMINAL#" \
    -e "s#__LEDGER_SOURCE__#$NEW_LEDGER_SOURCE#" -e "s#__LEDGER_SHA__#$NEW_LEDGER_SHA#" \
    "$BENCH/arm-env.template.zsh" > "$BENCH/arm-env.zsh"
```

```zsh
# 3.1 Owner-pause authorisation (only while /Users/edr/night-custody/magistrate/STOP exists). FILL: Ed's own words and time, verbatim.
print -r -- 'FILL: Ed, <date time>: "<his words authorising this arm>"' > "$BENCH/owner-arm-auth.txt"

zsh "$BENCH/step0-discover.zsh" 2>&1 | tee "$BENCH/step0.$NEW_LABEL.out"      # discovery, census substrings, battery gate 1
zsh "$BENCH/step1-clone.zsh"    2>&1 | tee "$BENCH/step1.$NEW_LABEL.out"      # clone at H, venv on the lock, byte-copy ledger, head == pin
zsh "$BENCH/step2-desk.zsh"     2>&1 | tee "$BENCH/step2.$NEW_LABEL.out"      # pins, identity, plan v2, wrapper + manifest, preflight, render
zsh "$BENCH/step3-notice.zsh"   2>&1 | tee "$BENCH/step3.$NEW_LABEL.out"      # attempt 000001, two census reads, notice body
```

If step2 stops at "GAP 1", do not arm: nothing is published, and the window would be a null session at t0. Escalate to the orchestrator (the seal or a follow-up must make the gate and the harvest agree on the registration).

## 4. The notice (sent by the orchestrator through the Gmail MCP; the magistrate sends its own for C2/C3)

The body is `$ATTEMPT_DIR/notice-body.txt` from step3 (its first two lines are the `To:` and `Subject:` headers: one address only, `claude2.glaring610@passmail.net`, never copper531). What it says, in order: reply NO to stop; what a window is; why these windows (the 1,710,000-cell search limit and the 12-valid-capture need); network time OFF and the 600 s clean dwell; first window or the prior window's session id and harvest file; ledger head sequence and digest; keep every agent session closed from t0 - 8 min; the local and UTC times for install close, REQUEST, TERM, KILL, t0, window end, completion and dead-man; plan, registration, frozen plan, wrapper, manifest, identity, template and render digests.

`retry_allowed` (code) refuses publication without an accepted notice that names a Gmail message id and thread id, so arming a window is itself the change of state that warrants one email; there is no owner waiting period (`NOTICE_LEAD_S` is 0). After the send:

```zsh
# 4.1 Record the acceptance (FILL from the Gmail result), then the NO search, then step3b and step4.
print -r -- 'sent epoch: FILL; message id: FILL; thread id: FILL; accepted body sha256: FILL; unreadable-thread limitation: FILL or none' > "$ATTEMPT_DIR/notice-evidence.txt"
# NO search (Ed replies on whichever thread is newest): Gmail search  from:claude2.glaring610@passmail.net is:unread  across ALL threads; any NO stops here.
# (Gmail down: use the GitHub directive-notice issue fallback of directive 349: message_id = comment id, thread_id = issue number.)
MSG_ID='FILL' THREAD_ID='FILL' SENT_EPOCH_S='FILL' PREREQ_CLEAR=true VETO_CLEAR=true zsh "$BENCH/step3b-notice-record.zsh"
zsh "$BENCH/step4-publish-install.zsh" 2>&1 | tee "$BENCH/step4.$NEW_LABEL.out"   # strictly before t0 - 12 min (it refuses later)
zsh "$BENCH/step5-verify-and-exit.zsh" 2>&1 | tee "$BENCH/step5.$NEW_LABEL.out"
cp "$BENCH/arm-env.zsh" "$STAGE/arm-env.zsh"    # the frozen env for this window: the harvest sources it
```

Set `PREREQ_CLEAR` and `VETO_CLEAR` to `true` only after the observations above and step4's pre-publication block (directive bodies read, no standdown, STOP explained by the authorisation file, no stop branch, no NO anywhere).

## 5. Verify it is armed, record it, close the interactive session

```zsh
source "$STAGE/arm-env.zsh"
launchctl list | grep -E 'com[.]joulewise[.]night'          # exactly com.joulewise.night and com.joulewise.night.deadman (the probe label is removed by the installer)
"$PY" -B scripts/run_night.py schedule --plan "$PLAN"        # t0, install_close, deadman, calendars; t0 must equal T0_EPOCH_S
cmp "$PLAN" "$ATTEMPT_DIR/plan.json"; ( cd "$NIGHT_ROOT" && shasum -a 256 -c chain.zsh.sha256 )
ls -la "$NIGHT_ROOT"; cat "$NIGHT_ROOT/start_conditions_manifest.json"
"$PY" -B - <<'PY'
import os
from scripts.magistrate_watchdog import plan_span_active, Storage
from joulewise.night_gate import NightPlan
import json, time
from pathlib import Path
plan = NightPlan.from_mapping(json.loads(Path(os.environ["PLAN"]).read_text()))
t = plan.t0_epoch_s
print("span active before t0-8m?", plan_span_active(plan, t - 481, Storage(Path(plan.custody_root))), "(expect False)")
print("span active at t0-8m?   ", plan_span_active(plan, t - 480, Storage(Path(plan.custody_root))), "(expect True)")
PY
```

The last check is the plan-span boundary the watchdog uses; both lines must read as expected. Then the arm record (what was armed, every digest above, the notice ids, step outputs) is written to a worktree or branch, not to the canonical checkout while the plan is armed. The interactive session sends its exit line, and Ed closes it by **t0 - 8 min at the latest**; all owned agents and background jobs go with it.

STOP release: `/Users/edr/night-custody/magistrate/STOP` holds the headless magistrate. Remove it only after the interactive session is closed and the plan span has begun (**t0 - 8 min or later**: the watchdog fences relaunch from then, so no magistrate starts before the window ends). Earlier removal can relaunch a magistrate while the arm is still being worked (owner action: `rm /Users/edr/night-custody/magistrate/STOP`). The first magistrate activation after the window finds its terminal state at t0 + 9300 s or later.

## 5.1 Pre-arm admission probe (added 2026-09-30 after C1 refused at t0; run before section 4's notice)

The t0 driver runs the passwordless network-time setter and admits its stdout. Run the same command and the same admission now, so a wording or permission mismatch fails hours before t0. The setter is idempotent and network time stays Off between windows, so this changes no machine state. Its output is a probe, not the window's receipt; the window's one receipt is still written at t0.

```zsh
OUT="$(/usr/bin/sudo -n /usr/sbin/systemsetup -setusingnetworktime off 2>&1)"; RC=$?
print -r -- "rc=$RC stdout=$OUT"
"$PY" -B -c 'import sys; from joulewise.network_time_off import off_stdout_admitted as ok; sys.exit(0 if int(sys.argv[1]) == 0 and ok(sys.argv[2]) else 3)' "$RC" "$OUT" \
  && print "OFF probe admitted" || print "REFUSED: OFF probe not admitted (pre-start: refusal route R3)"
```

## 6. Harvest one window (the magistrate runs this, in this order; it is the light-tier path)

All commands run against the window just finished. `source` its frozen env first. The window is terminal when `night/result.json` and `night/courier.sent` exist and `now > T0_EPOCH_S + 9300` (`night/chain.exited` exists unless the session was null). Run on Opus headless with no other agent alive; no measured value is read.

```zsh
export PLAN_ID='FILL: the window just finished'
source "/Users/edr/night-plan-staging/$PLAN_ID/arm-env.zsh"
cd "$MEASUREMENT_ROOT"
test -f "$NIGHT_ROOT/night/result.json" && test -f "$NIGHT_ROOT/night/courier.sent"
python3 -c 'import os,sys,time; sys.exit(0 if time.time() > int(os.environ["T0_EPOCH_S"]) + 9300 else 1)'
test "$(git -C "$MEASUREMENT_ROOT" rev-parse HEAD)" = "$H"     # the clone is still at H before the pin/verdict commit (harvest then accepts H plus that commit only: GAP 2, fixed in #447)
( cd "$NIGHT_ROOT" && shasum -a 256 -c chain.zsh.sha256 )
RL=("$PY" -B scripts/recover_calibration_ledger.py --ledger "$CALIBRATION_LEDGER" --head-pin "$LEDGER_HEAD_PIN")
PIN_JSON="$("${RL[@]}" terminal-pin --session-id "$SESSION_ID")"; print -r -- "$PIN_JSON"
PIN_SEQ="$(print -r -- "$PIN_JSON" | "$PY" -c 'import json,sys;print(json.load(sys.stdin)["sequence"])')"
PIN_DIG="$(print -r -- "$PIN_JSON" | "$PY" -c 'import json,sys;print(json.load(sys.stdin)["head_digest"])')"
OP="magistrate-$(date +%Y%m%d-%H%M)"; WHY="Harvest $SESSION_ID: terminal session, chain exit recorded, courier sent; desk pin advance to sequence $PIN_SEQ"
"${RL[@]}" advance-head-pin --session-id "$SESSION_ID" --expected-sequence "$PIN_SEQ" --expected-digest "$PIN_DIG" --operator-identity "$OP" --attestation-reason "$WHY"            # dry run   # PIN_ADVANCEMENT_NOT_NEEDED means the pin already equals the ledger head: skip both advance calls
"${RL[@]}" advance-head-pin --session-id "$SESSION_ID" --expected-sequence "$PIN_SEQ" --expected-digest "$PIN_DIG" --operator-identity "$OP" --attestation-reason "$WHY" --execute
"$PY" -B scripts/issue_calibration_acceptance_generation.py battery-verdict --ledger "$CALIBRATION_LEDGER" --head-pin "$LEDGER_HEAD_PIN" \
  --repo-root "$MEASUREMENT_ROOT" --session-id "$SESSION_ID" --preregistration "$REG_PATH" --preregistration-sha256 "$PREREG_SHA256"
#   rc 3 (REFUSED, including a session with no captures = null session): HALT, email the owner, do not arm.
git add configs/calibration/calibration_ledger_head.json "configs/calibration/battery_float_verdicts/$SESSION_ID.json"
git commit -m "Harvest $SESSION_ID: ledger head pin and battery-float verdict"
git push origin "HEAD:refs/heads/harvest/$SESSION_ID"
ARCH="$HOME/night-archive/harvest-$PLAN_ID"
PRIORS=(); for f in ${=PRIOR_HARVEST_LIST:-}; do PRIORS+=(--prior-harvest-record "$f"); done   # FILL PRIOR_HARVEST_LIST (space separated, ledger order) for C2/C3; empty for C1
IDS=(); for s in ${=PRIOR_SESSION_LIST:-} "$SESSION_ID"; do IDS+=(--session-ids "$s"); done       # FILL PRIOR_SESSION_LIST (space separated, ledger order) for C2/C3
"$PY" -B scripts/harvest_window.py --plan "$NIGHT_ROOT/night_plan.json" --custody "$ARCH" \
  --preregistration "$MEASUREMENT_ROOT/$REG_PATH" --preregistration-sha256 "$PREREG_SHA256" "${PRIORS[@]}" "${IDS[@]}"
#   stdout: valid_captures=N next_window=VERDICT. The exit code is 0 for every decision (stop decisions included): read the verdict, not $?.
#   A refusal prints "REFUSED: ..." and exits 3 before anything is uninstalled or published (HALT).
"$PY" -c 'import json,sys; h=json.load(open(sys.argv[1])); print(h["next_window"]["verdict"], h["valid_captures"], h["stop_flags"], h["window_end"]["epoch_s"])' "$ARCH/harvest.json"
```

Land the records (light tier, ruling 52(3); these bytes must be in HEAD's tree of the next clone because the next harvest requires them committed; GAP 3, fixed in #447):

```zsh
"$PY" -B scripts/land_window_records.py --harvest "$ARCH/harvest.json" --repo-root "$MEASUREMENT_ROOT"   # prints the landed paths and the commit sha; rc 3 = REFUSED: HALT. A second run after a successful landing also prints REFUSED (git commit: nothing to commit; Fable 157 Q3-2): check `git log -1` names "Harvest $SESSION_ID: window records" before treating it as a fault
git push origin "HEAD:refs/heads/harvest/$SESSION_ID"
# PR body: Tier: light; Impact (i)-(vi) each "No: records what code decided, changes no code or number (orchestrator ruling 52(3), record 00-session-record.md item 52)";
# rows 1, 4, 5 = N/A (light tier); row 2 = N/A (docs only); row 3 = RUN <head sha>. Never without the ledger (memory: pr-body-gate-ledger-required).
gh pr create --repo mpmdw/JouleWise --base main --head "harvest/$SESSION_ID" --title "Harvest $SESSION_ID" --body-file FILL
gh pr checks "harvest/$SESSION_ID" --repo mpmdw/JouleWise --watch     # CI green on the head
gh pr merge --repo mpmdw/JouleWise --merge FILL-PR-NUMBER   # never squash or rebase: the verdict's adding commit must reach main as itself
```

## 7. Inputs for the next window (run after the PR has merged; prints the `NEW_*` values for §3.0)

```zsh
export PRIOR_PLAN_ID='FILL: plan id of the window just harvested'
ARCH="$HOME/night-archive/harvest-$PRIOR_PLAN_ID"
"$PY" -B - <<'PY'
import json, os
from pathlib import Path
a = Path(os.environ["ARCH"]); h = json.loads((a / "harvest.json").read_text())
assert h["next_window"]["verdict"] == "NEXT_WINDOW", h["next_window"]["verdict"]
start = json.loads((a / "custody-root/night/start_conditions.json").read_text())
assert start["result"] == "admitted" and start["chain_start_admitted"] is not None, "null session: halt"
sid = h["sessions"][-1]["session_id"]
led = h["inventory"]["measurement-runs"]["calibration_observation_ledger.jsonl"]["sha256"]
print(f"export NEW_PRIOR_SESSION='{sid}'")
print(f"export NEW_PRIOR_HARVEST='{a / 'harvest.json'}'")
print(f"export NEW_PRIOR_STARTED='{start['chain_start_admitted']['epoch_s']}'")
print(f"export NEW_PRIOR_TERMINAL='{h['window_end']['epoch_s']}'")
print(f"export NEW_LEDGER_SOURCE='{a / 'measurement-runs/calibration_observation_ledger.jsonl'}'")
print(f"export NEW_LEDGER_SHA='{led}'")
PY
```

Then: `NEW_H` = `git ls-remote https://github.com/mpmdw/JouleWise refs/heads/main` (must contain the merged pin commit: step2 of the next arm and the clone's head-equals-pin check both refuse otherwise), `NEW_LABEL` c2 or c3, `NEW_PREREG` unchanged, `NEW_T0` from §1 with `LEAD_S=5400`, and `PRIOR_HARVEST_LIST` / `PRIOR_SESSION_LIST` for the next harvest are the harvest.json paths and session ids of every earlier window in ledger order. Then run §3 to §5 again. No cold gate, no lens, no new notice beyond the one `retry_allowed` needs.

## 8. GAPs

Status 2026-09-30: GAP 1, 2 and 3 are fixed by PR #447 (night gate admits the sealed registration; harvest accepts H plus the pin/verdict commit; `scripts/land_window_records.py`). The check-8 hazard found at the bench: the ChatGPT desktop app runs `Codex (Renderer)`, `Codex (Service)` and `codex` helpers, which check 8 flags (correctly), so ChatGPT.app must be quit before t0 with the interactive session. `check --preregistration` without `--preregistration-sha256` now exits 5 on the sealed file (Fable 156 Q3-b).


1. **Registration acceptance (blocks the arm at t0).** The night gate accepts only digests in `RULED_REGISTRATIONS` (`joulewise/night_gate.py`); the sealed Revision 6 file is not there, so a plan pointing at it is refused at t0 (`night_refused_registration`, a null session after the OFF receipt and dwell). A plan pointing at the D-166 file passes the gate, but `harvest_window.py` (lines 316-320) then refuses every Revision 6 harvest ("Revision 6 plan registration digest disagrees with harvest"). One of the two must change in the seal or a follow-up before C1 arms: code in a measurement path, full tier. Step2 fails closed on it.
2. **Harvest refuses its own prerequisite (blocks the first harvest, not the arm).** `harvest_window.py` requires the measurement clone's `HEAD` to equal `plan.measurement_head` (= H), while `battery_float.load_committed_verdict` requires the pin and verdict committed at that clone's `HEAD`. After the §6 commit `HEAD` is not H, so the harvest prints "measurement HEAD mismatch". The tests pass because their fixtures commit before building the plan. Needs a code fix (for example: `measurement_head` must be an ancestor of HEAD and the only paths changed since are the pin and the verdict) before C1's harvest. The magistrate must halt on it, never edit.
3. **Landing the window's records.** Committing `r9_window.json`, `start_conditions.json` and `harvest.json` into the repo (needed by the next window's harvest: `_revision_six_committed`) has no command; §6 does it with `cp` and `git`. The path convention is this recipe's.
4. **Notice.** Mail is the Gmail MCP only; no script sends it, and a headless Gmail send has failed before (#349). The GitHub `directive-notice` issue is the ruled fallback only. The NO search (`from:claude2.glaring610@passmail.net is:unread`, all threads) has no command.
5. **Rev 6 step scripts are not tracked.** Only the W1/W2 Revision 5 bench scripts are in the repo; the ones in §2 exist only in this file. Step0 is checked against nothing on main.
6. **No v4 plan.** `--new-plan` needs a sealed quiet-admission policy and a ruled `cutoff_authority`; none is tracked. The v2 route in §2 is what W1/W2 used and Revision 6 §6.2 allows it.
7. **Epoch watch not scripted.** W2's `issue_calibration_acceptance_generation.py check` expectations (rc 3, os_build mismatch, sampler digest lines) belonged to Revision 5; there is no Revision 6 expected-output spec. Step2 replaces it with the declaration comparisons (identity epoch, every pin, cell budget, ledger pin), which are stronger.
8. **Passwordless OFF is tested at arm (corrected 2026-09-30).** The getter needs a password, but the setter is passwordless and idempotent; section 5.1 runs it and admits its stdout. C1 was refused at t0 because this line said it could not be tested and the admission accepted only the On-to-Off wording while the Mac was already Off.
9. **STOP file.** `step4` requires no `standdown.request`, and with the owner-pause STOP present it needs the owner's recorded words (`owner-arm-auth.txt`). Whether the 09-29 instruction to resume work already covers this is Ed's or the orchestrator's call.
10. **Null session timing.** A refused start has no `chain_start_admitted`; no command or rule says what `--prior-started-epoch-s` is after it. §7 stops on it; the brief halts on any null session.
11. **Spacing.** Discovery and harvest both open at t0 + 9300 s; with harvest, PR and CI, the next arm's 5400 s lead and its own t0 the start-to-start interval is about 4 hours, not the 2.5 of the cadence audit, unless `window_max_s` is trimmed (changes plan digests; Ed's call).
