# G2-a arm recipe (measurement block 3, registration G2A-25G83-B3), with harvest and verdict handling

Status: written 2026-10-03 by the block-3 design seat (Opus 5.5), from the block-2 recipe
(`docs/process_traces/2026-10-02-design-block2/40-g2a-arm-recipe.md`), which armed `w1` and `w2`.
For the headless magistrate:
run the sections exactly, unedited, filling only the values marked **FILL**. It reuses the proven
Revision 6 bench (`/Users/edr/night-plan-staging/r6-bench`, recipe
`docs/process_traces/2026-09-29-interactive-ff50b201/170-c1-arm-recipe.md`) wherever the step is the
same; every difference is a G2-a fact. Nothing here runs sudo (except the passwordless OFF probe of
§5.1), launchctl outside the installer, or powermetrics. Every `CHECK:` line stops the script.

## 0. Facts the recipe rests on

- The window is one `DIAGNOSTIC_NO_PACK` v2 plan whose registration (for the night gate) is the D-166
  file `configs/campaigns/d117_contrast_v5/d166_dominance_criterion_registration.json` (sha256
  `dfe55f8d…c265`, in `night_gate.RULED_REGISTRATIONS`). The block's own rules are the sealed
  registration `configs/campaigns/g2a_prefill_probe_25g83/registration_block3.md`; its sha256 at H
  must equal the seal record's (`docs/process_traces/2026-10-03-design-block3/52-seal-record.md`).
- One command authors plan, chain and sidecar: `scripts/gen_g2_phase_d.py --new-g2a-window` (lane
  G2A-NIGHT-25G83-01, PR #458; block-3 lane G2A-B3-RETRY-BACKOFF-01). The chain carries
  `NIGHT_PROGRAMMED_SPAN_S` (**18,868 s** at the block-3 lane, PR #465) and exports `POLICY` as the block-3
  campaign policy `configs/campaign_policies/quiet_mac_p2_g2a_b3.json` (the production policy plus
  `idle_admission.retry_backoff_s` = 300: a member whose first idle check fails waits 300 s before
  its one retry). The driver admits the chain with the physical start conditions (OFF receipt and
  600 s settle on both clocks, clean dwell, night gate) and no Revision 6 manifest.
- `WINDOW_MAX_S` = span + 2700 rounded up to a minute = **21,600 s** at that span (§1 computes it
  from the code at H). Harvest opens at `t0 + WINDOW_MAX_S + 300`.
- Ledger seed for `b3w1`: block 2 `w2`'s re-harvest terminal ledger
  `/Users/edr/night-archive/harvest-d117-g2a-prefill-probe-20261003T1748Z-r2/derived/terminal-ledger.jsonl`,
  392 rows, file sha256 `84bb9aee4a9358c13491832e12e9e504c02fb838d1a167974a235e8d2942475b`; the
  committed pin at H (sequence 392, PR #464) must equal its head (the clone step checks with the
  production loader). For the recovery window the seed is the previous block-3 window's archived
  terminal ledger, whose pin advance is merged first (§7).
- Arm head: `SEAL_H` is the sealed H, the first main commit containing both PR #465 and the
  block-3 seal record; the RUN_STATE block-3 HANDOFF names it (the seal record cannot contain its
  own merge sha). The arm head `H` is remote main; it may differ from `SEAL_H` only as
  registration §12 allows. step2 checks it: every file in
  `git diff --name-only SEAL_H H` is under `docs/` or `tests/`, is `RUN_STATE.md`, `TASK_QUEUE.md` or
  `configs/calibration/calibration_ledger_head.json`, or is named under the seal record's heading
  `## H′ extensions` (only lines of the exact form ``- `path` ``, or the single word `none`; it lists gated fixes that make code agree with the registration; `none` at the seal). H′ pin tables never go inside that section; each goes under its own `## H′ n pins` heading (refuter D1).
- Probe inputs are built at the desk by `scripts/generate_g2a_probe_inputs.py build-probes` (5 small,
  1 large per rung) and bound by `bind-window` to this window's ids: window id = `PLAN_ID`, bracket
  session = `PLAN_ID-calibration`, evidence root = `evidence-PLAN_ID` (the harvest checks these).
- Ids and paths must not contain `codex`, `claude` or `t3` in any letter case (census and clean-dwell
  substrings); the authoring command refuses them.
- Network time: the driver's OFF setter run at t0 is the window's receipt (registration §5). §5.1's
  probe runs the same command early so a wording or permission problem fails before t0.
- The interactive-session rule (RUN_STATE handoff step 4): if the census finds an interactive Claude
  session alive at arm time, the arm notice tells Ed plainly to `/exit` it before **t0 − 8 min**.

## 1. Choose t0 and compute the window

```zsh
export LEAD_S=5400     # headless magistrate working lead; never below 2400
export SPAN_S=18868     # NIGHT_PROGRAMMED_SPAN_S at the block-3 lane; step2 refuses if the code at H needs another value
python3 -B - <<'PY'
import math, os, time
from datetime import datetime, timezone
span = int(os.environ["SPAN_S"]); window = math.ceil((span + 2700) / 60) * 60
now = time.time(); epoch = math.ceil((now + int(os.environ["LEAD_S"])) / 60) * 60
def ambiguous(e):
    local = datetime.fromtimestamp(e)
    return len({c for c in {local.replace(fold=f).timestamp() for f in (0, 1)} if datetime.fromtimestamp(c) == local}) != 1
while ambiguous(epoch):
    epoch += 60
def show(label, e):
    print(f"{label:40s} {datetime.fromtimestamp(e).astimezone().strftime('%Y-%m-%d %H:%M:%S %Z')}  epoch {e}")
print(f"T0_EPOCH_S={epoch}\nWINDOW_MAX_S={window}")
show("install close EXCLUDED (t0-10m)", epoch - 600)
show("REQUEST / interactive closed (t0-8m)", epoch - 480)
show("t0: driver OFF receipt + dwell", epoch)
show("latest chain start", epoch + window - span)
show("window end", epoch + window)
show("harvest opens (window end + 300)", epoch + window + 300)
PY
```

## 2. Bench files (create once; `arm-env.template.zsh` is refilled per window)

```zsh
export BENCH=/Users/edr/night-plan-staging/g2a-b3-bench
export R6=/Users/edr/night-plan-staging/r6-bench
mkdir -p "$BENCH"
# Reused byte for byte from the Revision 6 bench (generic steps): battery gate, notice record, verify-and-exit.
for f in battery-gate.zsh step3b-notice-record.zsh step5-verify-and-exit.zsh; do
  sed 's#/Users/edr/night-plan-staging/r6-bench/arm-env.zsh#/Users/edr/night-plan-staging/g2a-b3-bench/arm-env.zsh#' "$R6/$f" > "$BENCH/$f"
done
test "$(wc -l < "$BENCH/battery-gate.zsh")" -eq 52
grep -c 'r6-bench' "$BENCH"/*.zsh && exit 3 || true
```

```zsh
cat > "$BENCH/arm-env.template.zsh" <<'EOF_ENV'
#!/bin/zsh
set -euo pipefail
export BENCH=/Users/edr/night-plan-staging/g2a-b3-bench
# ---- values substituted by the fill command in section 3 ----
export H='__H__'                         # 40 hex: remote main containing the block-3 seal record
export SEAL_H='__SEAL_H__'               # 40 hex: the sealed H named in the RUN_STATE block-3 HANDOFF
export T0_EPOCH_S='__T0__'               # section 1
export WINDOW_MAX_S='__WINDOW__'         # section 1
export WINDOW_LABEL='__LABEL__'          # b3w1 for the first window, b3w2 for the recovery window
export REG_SHA256='__REG__'              # sha256 of the sealed registration at H (= seal record)
export LEDGER_SOURCE='__LEDGER_SOURCE__'
export LEDGER_SOURCE_EXPECTED_SHA256='__LEDGER_SHA__'
# ---- fixed ----
export TZ=America/Los_Angeles PYTHONDONTWRITEBYTECODE=1
unset PYTHONPATH
export CANON=/Users/edr/code/JouleWise
export REMOTE_URL=https://github.com/mpmdw/JouleWise
export REG_PATH='configs/campaigns/g2a_prefill_probe_25g83/registration_block3.md'
export D166_REG_PATH='configs/campaigns/d117_contrast_v5/d166_dominance_criterion_registration.json'
export T0_UTC="$(TZ=UTC date -r "$T0_EPOCH_S" +%Y%m%dT%H%MZ)"
export NIGHT_DATE="$T0_UTC"
export PLAN_ID="d117-g2a-prefill-probe-$T0_UTC"
export SESSION_ID="$PLAN_ID-calibration"
export EVIDENCE_ROOT_ID="evidence-$PLAN_ID"
export MEASUREMENT_ROOT="/Users/edr/night-custody/measurement/JouleWise-measurement-$T0_UTC-g2a-$WINDOW_LABEL"
export PY="$MEASUREMENT_ROOT/.venv/bin/python"
export NIGHT_ROOT="/Users/edr/night-custody/$PLAN_ID"
export G2A_ROOT="/Users/edr/night-g2a/$PLAN_ID"
export STAGE="/Users/edr/night-plan-staging/$PLAN_ID"
export STAGED_PLAN="$STAGE/night_plan.json"
export PLAN="$NIGHT_ROOT/night_plan.json"
export CALIBRATION_LEDGER="$MEASUREMENT_ROOT/runs/calibration_observation_ledger.jsonl"
export LEDGER_HEAD_PIN="$MEASUREMENT_ROOT/configs/calibration/calibration_ledger_head.json"
export POLICY="$MEASUREMENT_ROOT/configs/campaign_policies/quiet_mac_p2_g2a_b3.json"
export SEAL_RECORD='docs/process_traces/2026-10-03-design-block3/52-seal-record.md'
export PANEL="$MEASUREMENT_ROOT/configs/model_panels/qwen3_4bit.json"
export PATH="$MEASUREMENT_ROOT/.venv/bin:$PATH"
export ARM_ATTEMPT=1 ATTEMPT_DIR="$STAGE/arm-attempts/000001"
source "$BENCH/battery-gate.zsh"
EOF_ENV
```

```zsh
cat > "$BENCH/step0-discover.zsh" <<'EOF_S0'
#!/bin/zsh
set -euo pipefail
source /Users/edr/night-plan-staging/g2a-b3-bench/arm-env.zsh
cd "$CANON" || exit 3
print -- "CHECK: no unfilled placeholder in arm-env.zsh"
if grep -n '__[A-Z_]*__' "$BENCH/arm-env.zsh"; then echo "unfilled placeholder"; exit 3; fi
print -- "CHECK: H, REG_SHA256, T0_EPOCH_S, WINDOW_MAX_S well formed; t0 minute aligned and >= 2400 s ahead"
[[ "$H" =~ '^[0-9a-f]{40}$' && "$SEAL_H" =~ '^[0-9a-f]{40}$' && "$REG_SHA256" =~ '^[0-9a-f]{64}$' && "$T0_EPOCH_S" =~ '^[0-9]+$' && "$WINDOW_MAX_S" =~ '^[0-9]+$' ]] || exit 3
(( T0_EPOCH_S % 60 == 0 && WINDOW_MAX_S % 60 == 0 )) || exit 3
(( T0_EPOCH_S - $(date +%s) >= 2400 )) || { echo "lead below the 2400 s floor"; exit 3; }
print -- "CHECK: no codex, claude or t3 in any id or path (any case)"
for v in "$PLAN_ID" "$SESSION_ID" "$EVIDENCE_ROOT_ID" "$MEASUREMENT_ROOT" "$NIGHT_ROOT" "$G2A_ROOT" "$STAGE"; do
  l="${(L)v}"; [[ "$l" != *codex* && "$l" != *claude* && "$l" != *t3* ]] || { echo "census substring in $v"; exit 3; }
done
print -- "CHECK: os_build is 25G83"
test "$(sw_vers -buildVersion)" = 25G83
print -- "CHECK: no com.joulewise.night* label loaded, no plist on disk"
loaded_labels="$(launchctl list | awk '$3 ~ /^com[.]joulewise[.]night/ {print $3}')"
print -r -- "$loaded_labels"; test -z "$loaded_labels"
agent_plists=(~/Library/LaunchAgents/com.joulewise.night*.plist(N))
(( ${#agent_plists} == 0 )) || { print -rl -- "${agent_plists[@]}"; exit 3; }
print -- "CHECK: every /Users/edr/night-custody/*/night_plan.json is terminal"
python3 -B - <<'PY'
import json
from joulewise.evidence_night import retained_roots
result = retained_roots({"roots_under": "/Users/edr"})
for row in result["inventory"]:
    print(json.dumps(row, sort_keys=True), flush=True)
assert result["verdict"] == "pass", "active or unknown sibling plan"
PY
for p in "$MEASUREMENT_ROOT" "$NIGHT_ROOT" "$G2A_ROOT" "$STAGE"; do test ! -e "$p"; test ! -L "$p"; done
mkdir -p /Users/edr/night-custody/measurement /Users/edr/night-g2a "$STAGE"
test ! -L /Users/edr/night-custody/measurement; test ! -L /Users/edr/night-g2a
print -- "CHECK: battery connected, not charging, signed current within 200 mA, gauge age <= 180 s"
battery_gate | tee -a "$STAGE/battery-gate.txt"
echo "STEP0 OK"
EOF_S0
```

```zsh
cat > "$BENCH/step1-clone.zsh" <<'EOF_S1'
#!/bin/zsh
set -euo pipefail
source /Users/edr/night-plan-staging/g2a-b3-bench/arm-env.zsh
remote_main="$(git ls-remote --exit-code "$REMOTE_URL" refs/heads/main)"
print -- "CHECK: remote main equals H"
test "${remote_main%%$'\t'*}" = "$H"
stage_entries=("$STAGE"/*(DN)); (( ${#stage_entries} == 1 )) && [[ "${stage_entries[1]:t}" == battery-gate.txt ]] || exit 3
grep -q 'BATTERY GATE PASS' "$STAGE/battery-gate.txt" || exit 3
git clone -q --no-hardlinks "$REMOTE_URL" "$MEASUREMENT_ROOT"
git -C "$MEASUREMENT_ROOT" checkout -q --detach "$H"
cd "$MEASUREMENT_ROOT" || exit 3
test "$(git rev-parse HEAD)" = "$H"
python3.13 -m venv .venv
"$PY" -m pip install -q -c env/mac-measurement-lock.txt -e ".[mac]"
"$PY" -m pip install -q -c env/mac-measurement-lock.txt charset-normalizer requests urllib3
print -- "CHECK: installed packages equal env/mac-measurement-lock.txt"
diff -u <(grep -Ev '^(#|[[:space:]]*$)' env/mac-measurement-lock.txt | sort) <("$PY" -m pip freeze --exclude-editable | sort)
mkdir -p "$MEASUREMENT_ROOT/runs"
test ! -e "$CALIBRATION_LEDGER"; test -f "$LEDGER_SOURCE"; test ! -L "$LEDGER_SOURCE"
print -- "CHECK: sha256 of LEDGER_SOURCE equals LEDGER_SOURCE_EXPECTED_SHA256"
test "$(shasum -a 256 "$LEDGER_SOURCE" | cut -d' ' -f1)" = "$LEDGER_SOURCE_EXPECTED_SHA256"
rsync -a --checksum "$LEDGER_SOURCE" "$CALIBRATION_LEDGER"; cmp "$LEDGER_SOURCE" "$CALIBRATION_LEDGER"
"$PY" -B - <<'PY'
import json, os
from pathlib import Path
from joulewise.calibration_ledger import load_calibration_ledger_snapshot
root = Path(os.environ["MEASUREMENT_ROOT"]); pin = Path(os.environ["LEDGER_HEAD_PIN"]); p = json.loads(pin.read_text())
s = load_calibration_ledger_snapshot(Path(os.environ["CALIBRATION_LEDGER"]), pin, repo_root=root,
                                     require_committed_pin=True, verify_custody=True, mode="read_replay")
print("CHECK: no ledger refusal and head == committed pin", flush=True)
assert not s.refusal_reasons, s.refusal_reasons
assert (s.head_sequence, s.head_digest) == (p["sequence"], p["head_digest"])
print("authenticated head-equals-pin", s.head_sequence)
PY
test -z "$(git status --porcelain=v1 --untracked-files=all)"
echo "STEP1 OK"
EOF_S1
```

```zsh
cat > "$BENCH/step2-desk.zsh" <<'EOF_S2'
#!/bin/zsh
set -euo pipefail
source /Users/edr/night-plan-staging/g2a-b3-bench/arm-env.zsh
cd "$MEASUREMENT_ROOT" || exit 3
print -- "CHECK: clone HEAD equals H and the tree is clean"
test "$(git rev-parse HEAD)" = "$H"; test -z "$(git status --porcelain=v1 --untracked-files=all)"
print -- "CHECK: sealed registration digest; D-166 registration armable; seal record names the same digest"
test "$(shasum -a 256 "$REG_PATH" | cut -d' ' -f1)" = "$REG_SHA256"
grep -q "$REG_SHA256" docs/process_traces/2026-10-03-design-block3/52-seal-record.md
print -- "CHECK: SEAL_H carries the seal record and PR #465; H differs from SEAL_H only as registration §12 allows"
git cat-file -e "$SEAL_H:$SEAL_RECORD"
git merge-base --is-ancestor 295fe1516c950ac0a49f4c389e84a027bba5c473 "$SEAL_H"
git merge-base --is-ancestor "$SEAL_H" "$H"
for f in ${(f)"$(git diff --name-only "$SEAL_H" "$H")"}; do
  case "$f" in
    docs/phase_2/window_runbook.md|docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md)
      awk '/^## H′ extensions[[:space:]]*$/{x=1;next} /^#/{x=0} x' "$SEAL_RECORD" | sed -n 's/^- `\(.*\)`$/\1/p' | grep -qxF -- "$f" \
        || { echo "H changes a pinned chain-source document outside registration §12: $f"; exit 3; } ;;
    docs/*|tests/*|RUN_STATE.md|TASK_QUEUE.md|configs/calibration/calibration_ledger_head.json) ;;
    *) awk '/^## H′ extensions[[:space:]]*$/{x=1;next} /^#/{x=0} x' "$SEAL_RECORD" | sed -n 's/^- `\(.*\)`$/\1/p' | grep -qxF -- "$f" \
         || { echo "H differs from SEAL_H outside registration §12: $f"; exit 3; } ;;
  esac
done
print -- "CHECK: block-3 policy digest equals the seal record; retry backoff 300 parses"
grep -q "$(shasum -a 256 "$POLICY" | cut -d' ' -f1)" "$SEAL_RECORD"
"$PY" -B -c 'import json,sys; from joulewise.schemas import CampaignPolicy as C; p=C.from_mapping(json.load(open(sys.argv[1]))); assert p.idle_admission.retry_backoff_s == 300, p.idle_admission' "$POLICY"
"$PY" -B -c 'import hashlib,sys; from joulewise import night_gate as g; d=hashlib.sha256(open(sys.argv[1],"rb").read()).hexdigest(); assert d == g.D166_REGISTRATION_SHA256 and g.armable_registration(d) is not None' "$D166_REG_PATH"
print -- "CHECK: screen literals derive from the live acceptance; span literal; window covers span + 2700"
"$PY" -B scripts/gen_g2_phase_d.py --check
SPAN="$("$PY" -B -c 'from scripts.gen_g2_phase_d import NIGHT_PROGRAMMED_SPAN_S as s; print(s)')"
(( WINDOW_MAX_S == (SPAN + 2700 + 59) / 60 * 60 )) || { echo "WINDOW_MAX_S is not the registered span + 2700 rounded up to a minute"; exit 3; }
print -- "CHECK: probe inputs built and bound to this window (ids are the harvest's)"
"$PY" -B scripts/generate_g2a_probe_inputs.py build-probes --root "$G2A_ROOT" --panel "$PANEL" --small-members 5 --large-members 1
"$PY" -B scripts/generate_g2a_probe_inputs.py bind-window --root "$G2A_ROOT" \
  --ledger "$CALIBRATION_LEDGER" --head-pin "$LEDGER_HEAD_PIN" --campaign-policy "$POLICY" --power-policy ac_high_power \
  --window-id "$PLAN_ID" --session-id "$SESSION_ID" --evidence-root-id "$EVIDENCE_ROOT_ID"
"$PY" -B scripts/generate_g2a_probe_inputs.py check --root "$G2A_ROOT" --panel "$PANEL" \
  --ledger "$CALIBRATION_LEDGER" --head-pin "$LEDGER_HEAD_PIN" --campaign-policy "$POLICY"
print -- "CHECK: one command authors the staged plan, chain and sidecar"
mkdir -p "$NIGHT_ROOT"
test "$(stat -f %d "$NIGHT_ROOT")" = "$(stat -f %d "$STAGE")"
"$PY" -B scripts/gen_g2_phase_d.py --new-g2a-window "$STAGED_PLAN" --t0-epoch-s "$T0_EPOCH_S" --window-max-s "$WINDOW_MAX_S" \
  --plan-id "$PLAN_ID" --measurement-root "$MEASUREMENT_ROOT" --measurement-head "$H" \
  --night-root "$NIGHT_ROOT" --g2a-root "$G2A_ROOT" | tee "$STAGE/authoring.txt"
/bin/zsh -n "$NIGHT_ROOT/chain.zsh"
( cd "$NIGHT_ROOT" && shasum -a 256 -c chain.zsh.sha256 )
print -- "CHECK: the chain exports the block-3 policy, once"
test "$(grep -c '^export POLICY=.*quiet_mac_p2_g2a_b3[.]json' "$NIGHT_ROOT/chain.zsh")" = 1
! grep -n 'quiet_mac_p2_production[.]json' "$NIGHT_ROOT/chain.zsh"
"$PY" -B scripts/run_night.py preflight --plan "$STAGED_PLAN"
print -- "CHECK: argv-only inspection mutates nothing"
before="$(find "$G2A_ROOT" "$NIGHT_ROOT" "$MEASUREMENT_ROOT/runs" -exec stat -f '%N %z %m' {} + | sort | shasum -a 256)"
MEASUREMENT_HEAD="$H" NIGHT_RESERVATION_ARGV_ONLY=1 NIGHT_VERIFY_ONLY=1 /bin/zsh "$NIGHT_ROOT/chain.zsh" > "$STAGE/reservation-argv.nul"
after="$(find "$G2A_ROOT" "$NIGHT_ROOT" "$MEASUREMENT_ROOT/runs" -exec stat -f '%N %z %m' {} + | sort | shasum -a 256)"
test "$before" = "$after"; test -s "$STAGE/reservation-argv.nul"
scripts/install_night_agent.sh --plan "$STAGED_PLAN" --python "$PY" --render-only "$STAGE/rendered-agents"
"$PY" -B - <<'PY'
import hashlib, json, os, plistlib
from pathlib import Path
directory = Path(os.environ["STAGE"]) / "rendered-agents"
paths = sorted(directory.glob("*.plist"))
assert {p.name for p in paths} == {"com.joulewise.night.plist", "com.joulewise.night.deadman.plist",
                                   "com.joulewise.night-probe." + os.environ["PLAN_ID"] + ".plist"}, [p.name for p in paths]
evidence = {}
for path in paths:
    raw = path.read_bytes(); plist = plistlib.loads(raw)
    assert plist["ProcessType"] == "Interactive", path
    evidence[plist["Label"]] = {"ProcessType": plist["ProcessType"], "rendered_plist_sha256": hashlib.sha256(raw).hexdigest(), "path": str(path)}
(Path(os.environ["STAGE"]) / "render-context.json").write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n")
PY
"$PY" -B scripts/run_night.py schedule --plan "$STAGED_PLAN" > "$STAGE/schedule.json"; cat "$STAGE/schedule.json"
echo "STEP2 OK"
EOF_S2
```

```zsh
cat > "$BENCH/step3-notice.zsh" <<'EOF_S3'
#!/bin/zsh
set -euo pipefail
source /Users/edr/night-plan-staging/g2a-b3-bench/arm-env.zsh
cd "$MEASUREMENT_ROOT" || exit 3
mkdir -p "$STAGE/arm-attempts"; mkdir "$ATTEMPT_DIR"
cp "$STAGED_PLAN" "$ATTEMPT_DIR/plan.json"; print '[]' > "$ATTEMPT_DIR/attempts.json"; cmp "$STAGED_PLAN" "$ATTEMPT_DIR/plan.json"
"$PY" -B -m joulewise.arm_census --plan "$STAGED_PLAN" | tee "$ATTEMPT_DIR/arm-census-1.json"
sleep 30
"$PY" -B -m joulewise.arm_census --plan "$STAGED_PLAN" | tee "$ATTEMPT_DIR/arm-census-2.json"
set +e; /usr/bin/pgrep -lf 'codex|claude|t3' > "$ATTEMPT_DIR/raw-pgrep.txt"; set -e
cat "$ATTEMPT_DIR/raw-pgrep.txt"
"$PY" -B - <<'PY' > "$ATTEMPT_DIR/notice-body.txt"
import hashlib, json, os
from datetime import datetime, timezone
from pathlib import Path
from joulewise.night_gate import NightPlan
from scripts.run_night import schedule
e = os.environ
raw = Path(e["STAGED_PLAN"]).read_bytes(); p = json.loads(raw); s = schedule(NightPlan.from_mapping(p)); t = p["t0_epoch_s"]; w = p["window_max_s"]
pin = json.loads(Path(e["LEDGER_HEAD_PIN"]).read_text())
pgrep = Path(e["ATTEMPT_DIR"], "raw-pgrep.txt").read_text()
interactive = any(("claude" in line.lower()) and ("codex" not in line.lower()) and (" -p " not in line) and ("--print" not in line) for line in pgrep.splitlines())
def stamp(label, v):
    print(f"  {label}: {datetime.fromtimestamp(v).astimezone().strftime('%Y-%m-%d %H:%M %Z')} (epoch {v})")
print("To: claude2.glaring610@passmail.net")
print(f'Subject: NIGHT NOTICE — {p["plan_id"]} (G2-a prefill probe, block 3, DIAGNOSTIC_NO_PACK) — attempt 1')
print("\nEd,\n")
if interactive:
    print("ACTION NEEDED: an interactive Claude session is open on the measurement Mac. Please /exit it before "
          f"{datetime.fromtimestamp(t - 480).astimezone().strftime('%H:%M %Z')} (t0 - 8 min); the window refuses to start while it is alive.\n")
print("Otherwise no action is needed. Reply NO to this message to stop this window; your NO overrides.")
print()
print("What this is. The G2-a probe window of measurement block 3 (sealed registration "
      f"{e['REG_PATH']}, sha256 {e['REG_SHA256']}). Between two pulse calibrations, the Mac runs Qwen3-1.7B five times and Qwen3-8B once "
      "at each of four prompt lengths (512, 1024, 2048, 4096 tokens), and counts how many 100 ms power records overlap each prefill phase. "
      "The shortest length at which all five small-model members show at least five overlapping records becomes Paper B's prefill length (rule D-166). "
      "A member whose first idle check fails waits 300 s before its one retry (the block-3 change). No energy is computed and nothing here is a claim.")
print("Network time stays OFF; the driver re-issues OFF at t0 and waits 600 s with the machine clean before the chain starts.")
print(f"Ledger head at this arm: sequence {pin['sequence']}.")
print("\nTimes:")
for k, v in [("install close", t - 600), ("interactive sessions closed BEFORE", t - 480), ("t0", t),
             ("window end", t + w), ("harvest opens", t + w + 300), ("daily dead-man", s["deadman_epoch_s"])]:
    stamp(k, v)
print("\nIdentifiers:")
print("  plan_id:", p["plan_id"], " plan sha256:", hashlib.sha256(raw).hexdigest())
print("  H:", e["H"], "\n  clone:", e["MEASUREMENT_ROOT"], "\n  custody:", e["NIGHT_ROOT"], "\n  probe root:", e["G2A_ROOT"])
print("  chain sha256:", hashlib.sha256(Path(e["NIGHT_ROOT"], "chain.zsh").read_bytes()).hexdigest())
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

`step4-publish-install.zsh` is the Revision 6 step4 with its two `gen_derivation_night.py` lines
replaced by the G2-a chain checks, the window length taken from the fill, and the plan's
registration compared with the D-166 file (the night gate's registration for this plan):

```zsh
sed -e 's#/Users/edr/night-plan-staging/r6-bench/arm-env.zsh#/Users/edr/night-plan-staging/g2a-b3-bench/arm-env.zsh#' \
    -e 's#^"\$PY" -B scripts/gen_derivation_night.py --plan "\$STAGED_PLAN" .*$#( cd "$NIGHT_ROOT" \&\& shasum -a 256 -c chain.zsh.sha256 ); "$PY" -B scripts/gen_g2_phase_d.py --check#' \
    -e 's#^"\$PY" -B scripts/gen_derivation_night.py --plan "\$PLAN" .*$#( cd "$NIGHT_ROOT" \&\& shasum -a 256 -c chain.zsh.sha256 ); "$PY" -B scripts/run_night.py preflight --plan "$PLAN"#' \
    -e 's#plan.window_max_s == 9000#plan.window_max_s == int(e["WINDOW_MAX_S"])#' \
    -e 's#plan.registration_path == e\["REG_PATH"\]#plan.registration_path == e["D166_REG_PATH"]#' \
    "$R6/step4-publish-install.zsh" > "$BENCH/step4-publish-install.zsh"
print -- "CHECK: no derivation-only command and no r6-bench path left in step4"
! grep -n 'gen_derivation_night\|r6-bench\|== 9000' "$BENCH/step4-publish-install.zsh"
grep -c 'gen_g2_phase_d.py --check' "$BENCH/step4-publish-install.zsh" | grep -qx 1
grep -c 'run_night.py preflight --plan "$PLAN"' "$BENCH/step4-publish-install.zsh" | grep -qx 1
grep -c 'e\["D166_REG_PATH"\]' "$BENCH/step4-publish-install.zsh" | grep -qx 1
```

## 3. Run order for one window

Every step runs in a foreground shell; keep each output under `$BENCH/stepN.<label>.out`. A nonzero
exit or a failed `CHECK:` stops the arm; a fixable cause goes through refusal route R3 (fix, gated PR,
re-arm with a new t0), never halt-and-email.

```zsh
# 3.0 Fill
export NEW_H='FILL: git ls-remote https://github.com/mpmdw/JouleWise refs/heads/main (must contain the block-3 seal record)'
export NEW_SEAL_H='FILL: the sealed H named in the RUN_STATE block-3 HANDOFF'
export NEW_T0='FILL: T0_EPOCH_S from section 1'
export NEW_WINDOW='FILL: WINDOW_MAX_S from section 1'
export NEW_LABEL=b3w1      # b3w2 for the recovery window
export NEW_REG='FILL: the sha256 in docs/process_traces/2026-10-03-design-block3/52-seal-record.md at NEW_H'
export NEW_LEDGER_SOURCE=/Users/edr/night-archive/harvest-d117-g2a-prefill-probe-20261003T1748Z-r2/derived/terminal-ledger.jsonl   # b3w1; §7 for b3w2
export NEW_LEDGER_SHA=84bb9aee4a9358c13491832e12e9e504c02fb838d1a167974a235e8d2942475b   # b3w1; for b3w2: shasum -a 256 of the new source
sed -e "s#__H__#$NEW_H#" -e "s#__SEAL_H__#$NEW_SEAL_H#" -e "s#__T0__#$NEW_T0#" -e "s#__WINDOW__#$NEW_WINDOW#" -e "s#__LABEL__#$NEW_LABEL#" \
    -e "s#__REG__#$NEW_REG#" -e "s#__LEDGER_SOURCE__#$NEW_LEDGER_SOURCE#" -e "s#__LEDGER_SHA__#$NEW_LEDGER_SHA#" \
    "$BENCH/arm-env.template.zsh" > "$BENCH/arm-env.zsh"
zsh "$BENCH/step0-discover.zsh" 2>&1 | tee "$BENCH/step0.$NEW_LABEL.out"
zsh "$BENCH/step1-clone.zsh"    2>&1 | tee "$BENCH/step1.$NEW_LABEL.out"
zsh "$BENCH/step2-desk.zsh"     2>&1 | tee "$BENCH/step2.$NEW_LABEL.out"
zsh "$BENCH/step3-notice.zsh"   2>&1 | tee "$BENCH/step3.$NEW_LABEL.out"
```

## 4. Notice, publication, install

Send `$ATTEMPT_DIR/notice-body.txt` with the Gmail MCP (`mcp__claude_ai_Gmail__send_message`, one
address: `claude2.glaring610@passmail.net`). The body already carries the `/exit` instruction when
step3 saw an interactive session; if the magistrate itself knows of one the census missed, add the
same sentence. Then exactly the Revision 6 recipe §4 (170, "4.1"): notice evidence, NO search
(`from:claude2.glaring610@passmail.net is:unread`, all threads), step3b, step4, step5, and
`cp "$BENCH/arm-env.zsh" "$STAGE/arm-env.zsh"`.

```zsh
print -r -- 'sent epoch: FILL; message id: FILL; thread id: FILL; accepted body sha256: FILL; unreadable-thread limitation: FILL or none' > "$ATTEMPT_DIR/notice-evidence.txt"
MSG_ID='FILL' THREAD_ID='FILL' SENT_EPOCH_S='FILL' PREREQ_CLEAR=true VETO_CLEAR=true zsh "$BENCH/step3b-notice-record.zsh"
zsh "$BENCH/step4-publish-install.zsh" 2>&1 | tee "$BENCH/step4.$NEW_LABEL.out"   # strictly before t0 - 12 min
zsh "$BENCH/step5-verify-and-exit.zsh" 2>&1 | tee "$BENCH/step5.$NEW_LABEL.out"
cp "$BENCH/arm-env.zsh" "$STAGE/arm-env.zsh"
```

## 5. Verify, record, exit

As Revision 6 recipe §5: `launchctl list | grep -E 'com[.]joulewise[.]night'` shows exactly the
night and dead-man labels; `run_night.py schedule --plan "$PLAN"` matches; plan bytes equal the
attempt copy; the chain sidecar verifies. Write the arm record (paths, shas, notice ids, step outputs)
on a branch in a worktree, never in the canonical checkout while armed. Every agent, the magistrate
included, exits before **t0 − 8 min**.

### 5.1 Pre-arm OFF probe (run before the notice)

```zsh
OUT="$(/usr/bin/sudo -n /usr/sbin/systemsetup -setusingnetworktime off 2>&1)"; RC=$?
print -r -- "rc=$RC stdout=$OUT"
"$PY" -B -c 'import sys; from joulewise.network_time_off import off_stdout_admitted as ok; sys.exit(0 if int(sys.argv[1]) == 0 and ok(sys.argv[2]) else 3)' "$RC" "$OUT" \
  && print "OFF probe admitted" || print "REFUSED: OFF probe not admitted (refusal route R3)"
```

## 6. Harvest (first activation at or after `t0 + WINDOW_MAX_S + 300`)

```zsh
export PLAN_ID='FILL: the window just finished'
source "/Users/edr/night-plan-staging/$PLAN_ID/arm-env.zsh"
cd "$MEASUREMENT_ROOT"
test -f "$NIGHT_ROOT/night/result.json" && test -f "$NIGHT_ROOT/night/courier.sent"
python3 -c 'import os,sys,time; sys.exit(0 if time.time() > int(os.environ["T0_EPOCH_S"]) + int(os.environ["WINDOW_MAX_S"]) + 300 else 1)'
test "$(git rev-parse HEAD)" = "$H"
ARCH="$HOME/night-archive/harvest-$PLAN_ID"
"$PY" -B scripts/harvest_g2a_window.py --plan "$PLAN" --archive-root "$ARCH" --operator-identity "magistrate-$(date +%Y%m%d-%H%M)"
#   stdout: verdict=SELECT|RECOVER|NULL|REFUSED, member totals, paths and sha256s. Exit 3 only for REFUSED.
"$PY" -c 'import json,sys; h=json.load(open(sys.argv[1])); print(h["verdict"], h["cause_codes"], h.get("selection"))' "$ARCH/harvest.json"
```

Then uninstall the night agents from the clone (`scripts/install_night_agent.sh --uninstall --plan "$PLAN" --python "$PY"`,
capture rc) and land the records (light tier: records what code decided, changes no code or number):
on a branch `harvest/$PLAN_ID` from the clone, commit the advanced `configs/calibration/calibration_ledger_head.json`
(if the harvest advanced it), and copy into `docs/process_traces/2026-10-03-design-block3/windows/$PLAN_ID/`
the archive's `harvest.json` and `SHA256SUMS`, plus `derived/selection.json` for SELECT. The other
derived files (bracket assessment, counts, summary, network-time report) hold measured values and
stay in the archive. Push,
open the PR with the light-tier ledger (rows 1, 4, 5 `N/A (light tier)`, row 2 `N/A (docs only)` unless
the pin file counts as config, then RUN the suite; row 3 the head sha), CI green, `gh pr merge --merge`.
The RUN_STATE line for the harvest carries paths, shas and the verdict only; the selected rung is
read from `selection.json` by the next design seat, never typed into RUN_STATE by the magistrate.

## 7. What each verdict means next

| Verdict | Next |
|---|---|
| SELECT | Block 3 is complete. Email Ed once (block complete, selection record path and sha). Launch a design seat (RUN_STATE item 7) for the desk day (rung pin from `derived/selection.json`, `_v5` pack generation, re-proof) and the next block. Block 2's archives may then be read as diagnostics only (registration §10). |
| RECOVER, `capture_made` true, first time | Name the cause from `harvest.json` cause codes and member `clock_anchor_status` fields plus bracket/admission evidence only (registration §10: never an overlap count or a summary row). If `harvest.json` lists at least 5 members whose `clock_anchor_status` is other than `not recorded` and more than half of those are other than `bounded`: the block stops in its END STATE (below). Otherwise arm one recovery window (label `b3w2`) after any removable cause is removed through R3. |
| RECOVER, `capture_made` true, on `b3w2` | The block stops in its END STATE (below). |
| END STATE (registration §7) | No further probe. `_v5` prefill length is 4096 by the end state; the `_v5` pre-registration binds the registration's sha256 and each block-3 window's `harvest.json` sha256 in place of a selection record. Record it (session record, RUN_STATE: paths, shas, "END STATE"), email Ed once, launch a design seat (RUN_STATE item 7) for the desk day at 4096. |
| RECOVER, `capture_made` false | Counts like NULL for the allowance (registration §7). |
| NULL | Re-arm with a new t0 (fresh plan id, same label) once the named cause is gone. The same refusal reason code in the driver's result record twice in a row: consult (Sol 6.1 plus Opus), not a third arm. |
| Every later window | Arm head H′ = remote main; step2 checks that it differs from `SEAL_H` only as registration §12 allows (pin advances, docs/tests/RUN_STATE/TASK_QUEUE commits, or files named in the seal record's H′ section, which lists any gated fix that makes code agree with the registration). Ledger seed = the previous block-3 harvest's archived `$ARCH/derived/terminal-ledger.jsonl` once its pin advance is merged (registration §3); `NEW_LEDGER_SHA` = its `shasum -a 256`; for a NULL window that opened no session, the previous seed is unchanged. |
| REFUSED | Tooling fault: fix through R3 (gated PR), re-run the harvest into a fresh archive root. |

## 8. Gaps

1. The light-tier harvest landing (§6) has no script for G2-a; the Revision 6 `land_window_records.py`
   is derivation-specific. The commands above are the procedure.
2. `install_night_agent.sh --launchd-probe` on a G2-a chain is exercised by tests (#458 R4) but not yet
   on the real launchd; step4 runs it, and a refusal there is an R3 fix before t0, costing only the t0.
