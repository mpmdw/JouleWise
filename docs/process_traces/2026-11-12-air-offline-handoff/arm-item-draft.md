<!--
DRAFT for the orchestrator (laptop lead). Not posted. Not pushed.
Written 2026-11-12 ~07:30 PST by a drafting seat (Opus 5.5) from origin/main 055c8fdfc (RUN_STATE 286),
presign bb6394f2b, audit/2026-11-10-fable cc8825611. Read notes.md beside this file first:
B1 (arm route) is closed by fix/2026-11-12-r1fu-arm-route @ 683dfe654, pending its cold review, CI and the bundled second Part A smoke.
Placeholders: __ITEM__ (RUN_STATE number), __HHMM__ (post time, from `date`), __NIGHT_SHA__ (40-hex),
__SMOKE_ITEM__ (the Part A smoke item that passed at __NIGHT_SHA__).
-->

__ITEM__. **Laptop lead (interactive session 52877569, Opus 5.5), 2026-11-12 __HH:MM__ PST: MAGISTRATE: ARM tonight's ALIGN v4 R1 follow-up night on `__NIGHT_SHA__`, with t0 NO LATER THAN 19:26 PST (RL-72). The arm has three parts in this order: the RL-89 arm checks, the D-7 packet step (delete, prepare, record the SHA-256), then plan, notice and install. The install is your LAST action, and then you exit at once. If any check below fails, or t0 cannot be 19:26 or earlier, NOTHING arms. Report it to the lead.**

```pointer
owner: magistrate
wait: none
deadline: 2026-11-12T18:30:00-08:00
on_early_or_refused: any failed check, refused prepare, install rc≠0 or a t0 later than 19:26 PST means nothing arms; do not retry, do not move t0 past 19:26, mail the lead. A REFUSED result within t0+10 min: restore (uninstall, powermode 0) and mail Ed and the lead at once
next_observable: commit on main adding docs/process_traces/2026-11-12-r1-followup-night/MAGISTRATE-ARM-<activation>.md (plan id, t0, window_max_s, custody $S, prepare packet SHA-256, every check line below) and an arm notice to Ed before install; after the night, RUN_STATE from the next activation per "After the night"
```

The 18:30 deadline is the latest START of this activation. It leaves time for `prepare`'s weight hashing (see "Timing"), the notice and the 15-minute notice lead before a 19:26 t0.

### Why, and what authorizes it

- **RL-89** (`audit/2026-11-10-fable` @ `cc8825611`, `RESEARCH-LEAD-DECISIONS.md`):
  - The pair is **TV0h / Th0C**, and **Tf08 is recorded**.
  - "I authorize the night on those conditions; the lead does not come back to me if they are all met."
  - The conditions are:
    - the reviewed config commit;
    - the regenerated table, accepted;
    - Part A passed at the commit;
    - the Mac 60-key check;
    - the ruling file `validate_sensor_ruling` reads;
    - D-7 and D-8.
  - The ruling file is `docs/run_reports/2026-11-12-rl89/sensor_ruling_rl89.json`: `research_lead_ruling` RL-89, `authorizes_night` true, table `smoke_part_b.rl89.json` sha256 `1fdd980c…eba3`.
- **RL-59, RL-64, RL-72:**
  - D members gate against a reference captured in a D member (step-D, after an ordinary 30B predecessor).
  - The cap is 1,200 s for every R1 gate.
  - A timeout in a step kind runs flagged; gated D and X-G keep W1's stop.
  - Two whole-unit load redos.
  - `window_max_s` 126,480 s (RL-72 E2).
  - The arm has "t0 no later than 19:26 PST on its day".
- **RL-84** P-1 to P-5:
  - the predecessor runs no sidecar;
  - Tf08 is recorded in every sidecar member;
  - per-key coverage;
  - ten condition-13 paths;
  - the smoke bounds are watchdogs.
- **RL-94:** the night runs **its own idle soak**. Pass no soak reference. Item 286's soak (`b45801a5…`) was the smoke's reference only.
- **RL-90:** what the report prints for every G0 (see "After the night").
- **RL-91 / RL-96:** the powermetrics orphan wrapper rides tonight only if it is in `__NIGHT_SHA__`. Otherwise the night runs without it, and the report says what RL-91 requires.
- **RL-89 margin disposition, fixed before the night:** suppose the night's confirmation fails ONLY on Th0C's return time (>300 s). The pick stands if step-D's G0 released and every per-turn gate (G1, H) that ran on the pair released inside its cap. Any other failed clause goes to the research lead.

### Final bytes and the Part A smoke that covers them

Fill in exactly one row and delete the other.

| `__NIGHT_SHA__` | What it is | Part A smoke that covers it |
|---|---|---|
| `bb6394f2bf290550b43a87efecb15d581839b845` | presign = `22f438fd3` + the RL-89/RL-94 stack + its review | **Item 286** (magistrate 882ff176): PASSED. Fresh soak `b45801a5…`. G0 RELEASED in 727.7 s at 1.0/1.0 °C on TV0h/Th0C. Receipt rc 0 |
| `<presign after the arm-route port 683dfe654 + #740 + #739>` | adds PR #740 (tests, docs, full-profile trace) and PR #739 (the RL-96 powermetrics reap wrapper) | **Item __SMOKE_ITEM__**: a second Part A smoke (`--fresh-soak --parts A`), launched after 13:15, PASSED at exactly this sha: G0 released ≤1,200 s on TV0h/Th0C, receipt rc 0 |

RL-89 requires Part A "on the final night bytes", and a commit that differs from the smoked commit in any byte is not covered. If the follow-up arm route (notes B1) has to land on presign, it changes the commit. Then row 2 applies even without #739/#740. Bundle them, so one smoke covers all of it.

### D-7 and D-8, and how this item discharges them

- **D-7 (MEDIUM, before the arm).** A prepare packet left at the fixed path by an earlier night of the same commit is accepted, because the packet carries no plan, night or date. (Source: `docs/run_reports/2026-11-11-r1-followup-kit-delta-coldreview.md`, round 5.)
  - The procedural route is fixed in `docs/align/r1_runtime_contract.md` ("Arm step for the packet"):
    1. delete any `$MEASUREMENT_ROOT/.align-r1-prepare.json`;
    2. run `align_r1_followup_kit.py prepare` on the final commit, with the real weight-digest and installed-stack preflights, and record its SHA-256 in the arm notice;
    3. arm, then compare the arm record's packet SHA-256 with step 2's. A mismatch is a refused arm.
  - Steps 1 and 2 are in "D-7 packet" below.
  - Step 3 has two parts:
    - an immediate re-hash before you exit;
    - the binding comparison against `r1_result.json` `prepare_packet.sha256`. The driver writes that record only at its terminal write, so the next activation runs it (see "After the night").
- **D-8 (LOW, test gap).** No test stopped the chain from honouring an inherited `ALIGN_R1_PREPARE_PACKET`.
  - It is discharged in the bytes: `tests/align/test_r1_rehearsal.py` (decoy-variable assertion, "D-8 (Fable kit delta review)") is present at `bb6394f2b`.
  - The chain sets the variable unconditionally (`align_r1_rehearsal.zsh`, `ALIGN_R1_PREPARE_PACKET="$MEASUREMENT_ROOT/.align-r1-prepare.json"`).
  - Nothing to run. The unset line below is belt-and-braces.

### Host state the lead expects (verify each; any difference is a STOP)

- **Nothing armed.** Only `com.joulewise.magistrate` is loaded. There is no `com.joulewise.night*` plist and no `com.joulewise.align-r0*` label, and no desk fence (RL-36 / item 261).
- **The High Power marker is absent.** No `/Users/Shared/JouleWise/host-power/high-power.marker`, and no `$M/.align-r1-high-power`. Never delete either by hand.
- **`night.lock` is stale, and the arm does not refuse on it.**
  - The file reads `{"pid": 77434, "role": "r1-smoke-close"}`, or a later smoke close's pid.
  - `HostLock` (`joulewise/align/apple/powermode.py`) is an exclusive `flock`. The JSON inside is a "diagnostic only" holder note. A file whose writer is dead does not block `acquire()`, and every smoke since item 274 acquired the lock over such a file and rewrote it (pids 52565 → 50618 → 58535 → 77434).
  - So: **leave it as found. Do NOT delete or edit it.** Deleting a flocked file while any process holds it splits the lock into two inodes.
  - Verify only that its pid is dead, that no process has it open, and that edr owns it (block below). If the pid is alive or `lsof` shows a holder, STOP.
- **Network time.** It is OFF, and the kernel frequency word reads 0 (items 251, 256, 262, 284).
  - If it is ON, or the word is not 0, run item 251's remedy before arming:
    1. `sudo -n systemsetup -setusingnetworktime off`;
    2. `/Users/edr/night-custody/magistrate/settle-b274d857/probe/zero.py` as root;
    3. re-read the word as 0.
  - Never turn network time ON before the arm.
- **Power and volumes.** AC power, battery charged and not charging, AC-profile powermode 0, no external volume mounted.
- **No other work and no agent.** No agent other than this session, and no BYTES desk job, powermetrics, `km003c_monitor` or `hazard_monitor` process. A BYTES desk job may have run from about 09:00; it must have finished.

### Timing (t0)

- **Upper bound:** `T0MAX` = 2026-11-12 19:26:00 PST = epoch **1794540360** (03:26Z 11-13), from RL-72.
  - Derivation (lead inference; it matches to the second): the no-redo phase subtotal is 58,711.9616 s. So 19:26:00 + 58,712 s = 11:44:32 on 11-13, just before the 11:45 start of the OS batch window.
  - A later t0 would put the no-redo night across the batch window.
- **Lower bound:**
  - t0 ≥ now + 15 min (the route's `ARM_NOTICE_S`), rounded up to a whole minute. The shared calendar needs whole minutes.
  - The install must finish before the installer cutoff, t0 − 300 s (the watchdog's 180 s plan lead plus the 120 s install-close margin).
- **The batch window (ruling 8).** The driver admits a quiet segment only if its bound ends before 11:45 or starts after 13:15 local, and it waits out the 5,400 s blackout itself.
  - The window budgets **two** encounters, and a third refuses (`r1_runtime_contract.md`).
  - From any t0 ≤ 19:26 on 11-12, `[t0, t0 + 126,480 s)` contains one 11:45 (11-13). Nothing to do. Do not pick a t0 to dodge scheduled jobs; the driver's redo rule handles them.
- **Prepare cost.**
  - `prepare` hashes every registered weight root (the 27B, the 30B and the NEG-8 reference) through `model_artifact_identity`.
  - It has never run natively (kit report, round 5: "No real weights or installed-stack qualification was attempted").
  - Allow 20 minutes. If it is still running at 19:05, it cannot meet t0 ≤ 19:26 with the 15-minute notice. STOP and report.

### Start and checks (while you are still alive)

```sh
export M=/Users/edr/night-custody/measurement/JouleWise-measurement-20261102-align-pilot2
export PY="$M/.venv/bin/python"               # the pinned measurement venv; do not resolve the symlink
NIGHT_SHA=__NIGHT_SHA__                        # full 40-hex
T0MAX=1794540360                               # 2026-11-12 19:26:00 PST (RL-72)
: "${MAGISTRATE_PID:?Set to the PID of this magistrate's own claude process}"
ps -o pid=,comm= -p "$MAGISTRATE_PID"           # must show the claude process
CUSTODY="${MAGISTRATE_WATCHDOG_CUSTODY_ROOT:-/Users/edr/night-custody/magistrate}"
unset JOULEWISE_HOST_STATE_DIR ALIGN_R1_RUNTIME ALIGN_R1_INPUTS ALIGN_R1_REGISTRATION ALIGN_R1_PREPARE_PACKET
unset EVIDENCE_POWER_RECORDER_REPLAY NIGHT_VERIFY_ONLY NIGHT_RESERVATION_ARGV_ONLY

# 1. Nothing armed, no fence, no marker, no stray process (RL-36, item 261)
launchctl list | grep com.joulewise                         # expect exactly one line: com.joulewise.magistrate
ls ~/Library/LaunchAgents | grep -c '^com\.joulewise\.night' || true      # expect 0
test ! -e "$CUSTODY/desk_fence.json"
test ! -e /Users/Shared/JouleWise/host-power/high-power.marker
test ! -e "$M/.align-r1-high-power"
ls -la /Users/Shared/JouleWise/host-power/                 # expect night.lock only
pgrep -fl 'powermetrics|km003c_monitor|hazard_monitor' || true             # expect none
pgrep -fl 'claude|codex' || true                           # expect only this session (and its MCP adapter children)
pgrep -fl 'bytes_' || true                                  # expect no BYTES desk job

# 2. Stale night.lock: verify, never delete (flock; the JSON is a diagnostic note)
LOCK=/Users/Shared/JouleWise/host-power/night.lock
cat "$LOCK"
LPID="$("$PY" -I -B -c 'import json,sys; print(json.load(open(sys.argv[1]))["pid"])' "$LOCK")"
if ps -p "$LPID" >/dev/null 2>&1; then echo "STOP: night.lock pid $LPID is alive"; fi
test -z "$(lsof -t "$LOCK" 2>/dev/null)"                    # no process holds it open
stat -f '%Su %Sp' "$LOCK"                                   # expect edr -rw-------

# 3. Power, volumes, sudo rules, network time
pmset -g batt                                               # AC Power; 100%; charged / not charging
pmset -g custom | sed -n '/AC Power/,$p' | grep -i powermode   # expect 0
diskutil list external                                      # expect nothing
sudo -n -l | grep -F '/usr/bin/pmset -c powermode 0'
sudo -n -l | grep -F '/usr/bin/pmset -c powermode 2'        # the chain refuses without both
sudo -n systemsetup -getusingnetworktime                    # expect "Network Time: Off"
"$PY" -I -B -c 'import sys; sys.path.insert(0, sys.argv[1]); from joulewise.kernel_clock import read_kernel_frequency as r; f=r(); print(f); assert f["raw_word"] == 0, "STOP: frequency word not 0 (item 251 remedy first)"' "$M"
df -g /Users/edr

# 4. Measurement checkout to the night commit (item 256 pattern: fetch + detach, venv kept)
git -C "$M" status --short --branch
PKT_OLD="$M/.align-r1-prepare.json"; [ -e "$PKT_OLD" ] && shasum -a 256 "$PKT_OLD"   # record it if one exists
test -z "$(git -C "$M" status --porcelain | grep -v '^?? \.align-r1-prepare\.json$')"
git -C "$M" fetch origin
git -C "$M" switch --detach "$NIGHT_SHA"
test "$(git -C "$M" rev-parse HEAD)" = "$NIGHT_SHA"
git -C "$M" merge-base --is-ancestor bb6394f2bf290550b43a87efecb15d581839b845 HEAD   # RL-89/RL-94 stack present
git -C "$M" merge-base --is-ancestor 683dfe654 HEAD                                 # the ported follow-up arm route
"$PY" -B -c 'import mlx.core,mlx_lm,transformers; from importlib.metadata import version; print(*(version(x) for x in ("mlx","mlx_lm","transformers")))'   # 0.31.2 0.31.3 5.12.1
M_REAL="$(cd "$M" && pwd -P)"                              # the plan records the resolved path; the chain derives the packet path from it
cd "$M_REAL"
"$PY" -B -c 'from pathlib import Path; import subprocess; from joulewise.align.apple import v4_registration as r; root=Path.cwd(); head=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip(); print(r.verify_r1_executed_sources(root,{"executed_commit":head}))'
```

**RL-89 arm checks (all three must pass).**

```sh
# (a) RL-89 item 4: the Mac 60-key check (verbatim from item 285; sha of r0.json first)
R0=/Users/edr/night-align/r0-v4-20261108T0550Z/smc/r0.json
"$PY" -I -B - "$R0" "$M_REAL/configs/align/v4/r1_runtime.json" <<'PY'
import hashlib, json, sys
EXPECT = "e6231a8f3e6ab6177bbedbf12b878c958a7b4d4331e36472c74c2a192588769b"
raw = open(sys.argv[1], "rb").read()
got = hashlib.sha256(raw).hexdigest()
assert got == EXPECT, f"REFUSE: r0.json sha256 {got} != {EXPECT}"
rows = [r for r in json.loads(raw)["response"]["ranking"]
        if r["class"] in ("die", "heatsink") and r["eligible"] is True]
keys, classes = [r["key"] for r in rows], {r["key"]: r["class"] for r in rows}
config = json.load(open(sys.argv[2]))
assert config["sensors"]["r0_sha256"] == EXPECT, "REFUSE: config r0_sha256"
assert len(keys) == 60 and len(set(keys)) == 60, f"REFUSE: {len(keys)} eligible rows"
assert config["r0_classified_keys"] == keys, "REFUSE: r0_classified_keys != r0.json eligible rows (ranking order)"
assert config["r0_classes"] == classes, "REFUSE: r0_classes != r0.json classes"
s = config["sensors"]
assert (s["s_fast"], s["s_slow"], s["record_keys"]) == ("TV0h", "Th0C", ["Tf08"]), f"REFUSE: sensors {s}"
assert classes["Th0C"] == "heatsink" and classes["TV0h"] == "die"
print("RL-89 MAC CHECK OK", got, len(keys), sum(c == "die" for c in classes.values()),
      sum(c == "heatsink" for c in classes.values()),
      hashlib.sha256(open(sys.argv[2], "rb").read()).hexdigest())
PY

# (b) the ruling file through the kit's own validate_sensor_ruling, plus the config sha and night constants
"$PY" -I -B - "$M_REAL" <<'PY'
import hashlib, json, sys
from pathlib import Path
root = Path(sys.argv[1]); sys.path.insert(0, str(root))
from scripts import align_r1_followup_kit as kit
from joulewise.align.apple import r1_runtime as rt
cfg_path = root / "configs/align/v4/r1_runtime.json"
cfg_sha = hashlib.sha256(cfg_path.read_bytes()).hexdigest()
assert cfg_sha == "95825997f7fd50e3a86342c059bd1eba2cc37139684c76eed35f0ca6ed0a1dad", f"REFUSE: config sha {cfg_sha}"
config, _ = rt.load_config(cfg_path)
ruling = json.loads((root / "docs/run_reports/2026-11-12-rl89/sensor_ruling_rl89.json").read_bytes())
assert ruling["research_lead_ruling"] == "RL-89" and ruling["authorizes_night"] is True
table_raw = (root / ruling["smoke_part_b_path"]).read_bytes()
table_sha = hashlib.sha256(table_raw).hexdigest()
assert table_sha == "1fdd980c91ceca6ee3907191b499f0108ca84b8709648a638bd49808a298eba3", f"REFUSE: table {table_sha}"
sel = kit.validate_sensor_ruling(config, ruling, table_sha, json.loads(table_raw))   # raises on any mismatch
assert (sel["ok"], sel["s_fast"], sel["s_slow"]) == (True, "TV0h", "Th0C"), sel
assert config["g0_timeout_s"] == 1200 and config["slow_band_floor_c"] == 1.0
assert config["r0_picks"] == {"s_fast": "TV0h", "s_slow": "Tf08"}
print("RL-89 RULING OK", table_sha, sel["s_fast"], sel["s_slow"], cfg_sha)
PY

# (c) RL-96 term 5: only if the wrapper is in the night commit. List, never run.
if git -C "$M_REAL" cat-file -e HEAD:joulewise/adapters/powermetrics_reap.py 2>/dev/null; then
  sudo -n -l /bin/kill; echo "sudo-kill-list rc=$?"           # must be rc=0 and print /bin/kill
  sudo -n -l /bin/kill -KILL 1 >/dev/null; echo "argv-shape rc=$?"   # the wrapper's argv shape; must be 0
else
  echo "wrapper NOT in night commit: RL-91 reporting applies after the night"
fi
```

(a) must print `RL-89 MAC CHECK OK e6231a8f…769b 60 16 44 95825997f7fd50e3a86342c059bd1eba2cc37139684c76eed35f0ca6ed0a1dad`. (b) must print `RL-89 RULING OK 1fdd980c…eba3 TV0h Th0C 95825997…1dad`. (c), when the wrapper is in, must show rc=0 twice. Anything else means STOP.

### D-7 packet (steps 1 and 2)

```sh
PKT="$M_REAL/.align-r1-prepare.json"
if [ -e "$PKT" ]; then shasum -a 256 "$PKT"; rm -- "$PKT"; fi        # D-7 step 1: a fresh packet only
test ! -e "$PKT"
test -z "$(git -C "$M_REAL" status --porcelain)"                     # clean before prepare
"$PY" -B scripts/align_r1_followup_kit.py prepare --output "$PKT" \
  --sensor-ruling docs/run_reports/2026-11-12-rl89/sensor_ruling_rl89.json \
  --smoke-table docs/run_reports/2026-11-12-rl89/smoke_part_b.rl89.json
echo "prepare rc=$?"
PKT_SHA="$(shasum -a 256 "$PKT" | cut -d' ' -f1)"; echo "PACKET_SHA256 $PKT_SHA"   # D-7 step 2: goes in the arm notice and the trace
"$PY" -I -B - "$PKT" "$NIGHT_SHA" <<'PY'
import json, sys
p = json.load(open(sys.argv[1]))
assert p["schema"] == "joulewise.align.r1_followup_prepare.v1" and p["status"] == "FOR_LEAD_ARM", p.get("status")
assert p["executed_commit"] == sys.argv[2]
assert p["weight_digests"]["ok"] is True and p["runtime_stack"]["ok"] is True
assert p["window_max_s"] == 126480 and p["programmed_span_s"] == 108768 and p["overhead_s"] == 9000
assert p["sensors"]["s_fast"] == "TV0h" and p["sensors"]["s_slow"] == "Th0C" and p["sensors"]["record_keys"] == ["Tf08"]
assert p["chain_script"] == "scripts/night_chains/align_r1_rehearsal.zsh" and len(p["bound_files"]) == 10
print("PACKET OK", {r: round(v.get("elapsed_s", 0), 1) for r, v in p["weight_digests"]["roots"].items()})
PY
git -C "$M_REAL" status --porcelain          # expect exactly: ?? .align-r1-prepare.json
```

If `prepare` refuses, it writes a `"status": "REFUSED"` packet with both check results at `$PKT` (mode `x`) and raises.
- STOP. Leave the file in place and report its reasons verbatim.
- Do not delete it and re-run without the lead.

### Plan, notice, install (the arm)

> **Arm route (B1, closed by the port).** `scripts/arm_align_r1.py` / `joulewise/align/r1_arm.py` are ported onto presign by `fix/2026-11-12-r1fu-arm-route` @ `683dfe654` (bundled into `__NIGHT_SHA__` with #739 and #740). The port sizes the window to RL-72 E2: span 108,768 s, `window_max_s` 126,480 s for every t0. The plan omits `ac_powermode` (absent means 0), and `arm.json` records the D-7 packet SHA-256. `__NIGHT_SHA__` must contain `683dfe654`.

```sh
export S="/Users/edr/night-align/r1fu-$(date -u +%Y%m%dT%H%M%SZ)"        # fresh custody root
T0="$("$PY" -B -c 'import math,time; print(60*math.ceil((time.time()+15*60)/60))')"
test "$T0" -le "$T0MAX" || echo "STOP: earliest t0 $(date -r "$T0") is after 19:26 PST (RL-72): do not arm"
"$PY" -B "$M_REAL/scripts/arm_align_r1.py" size --t0 "$T0"
"$PY" -B "$M_REAL/scripts/arm_align_r1.py" prepare --measurement-root "$M_REAL" --custody-root "$S" --t0 "$T0"
cat "$S/arm.json"
"$PY" -I -B -c 'import json,sys; a=json.load(open(sys.argv[1])); assert a["prepare_packet"]["sha256"] == sys.argv[2], a["prepare_packet"]; assert a["window_max_s"] == 126480; print("D-7 ARM RECORD OK", a["prepare_packet"]["sha256"])' "$S/arm.json" "$PKT_SHA"
"$PY" -I -B - "$S/night_plan.json" "$NIGHT_SHA" "$T0" "$M_REAL" <<'PY'
import json, sys
p = json.load(open(sys.argv[1])); sha, t0, root = sys.argv[2], int(sys.argv[3]), sys.argv[4]
assert p["plan_id"].startswith("align-r1-"), p["plan_id"]           # run_night reads night/align-r1/r1_result.json for this kind
assert p["receipt_class"] == "HAZARD_PACK"
assert p["repo_head"] == p["measurement_head"] == sha and p["measurement_root"] == root
assert p["t0_epoch_s"] == t0 <= 1794540360
assert p["hazard_window"]["programmed_span_s"] >= 108768, "RL-72 E2 span"
assert p["window_max_s"] >= 126480, "RL-72 E2 window"
assert "ac_powermode" not in p, "the follow-up route omits it (absent = 0; main's watchdog rejects the key)"
print("PLAN OK", p["plan_id"], t0, p["window_max_s"], "latest end epoch", t0 + p["window_max_s"] + 300)
PY
"$PY" -B "$M_REAL/scripts/arm_align_r1.py" render --custody-root "$S" --output "$S/rendered"
plutil -p "$S/rendered/com.joulewise.night.plist" | grep -E 'ProcessType|Hour|Minute|Day|Month|night_plan'   # ProcessType must be Interactive
plutil -p "$S/rendered/com.joulewise.night.deadman.plist" | grep -E 'Hour|Minute'
df -g /Users/edr | tee "$S/df-arm.txt"
```

**Arm notice to Ed, BEFORE install.** Use the ordinary Gmail route, as items 249, 251 and 256 did, and write `notice.ack`. Content:
- ALIGN v4 R1 **follow-up** rehearsal (non-claim) on Mac15,9;
- commit `__NIGHT_SHA__` and the Part A item that covers it;
- custody `$S`;
- t0 in PST and UTC;
- the ceiling (`window_max_s` + 300 s grace) and the latest end time;
- **prepare packet SHA-256 `$PKT_SHA` (D-7)**;
- the RL-89 check lines (a) and (b);
- wrapper in or out;
- network time Off, word 0;
- "keep the Mac on AC, no external volume, display asleep, no agents or other work until the latest end".

```sh
"$PY" -B "$M_REAL/scripts/arm_align_r1.py" install --custody-root "$S"; echo "install rc=$?"
launchctl print "gui/$(id -u)/com.joulewise.night" | head -5
launchctl print "gui/$(id -u)/com.joulewise.night.deadman" | head -5
test "$(shasum -a 256 "$PKT" | cut -d' ' -f1)" = "$PKT_SHA" && echo "D-7 packet unchanged since prepare"
pmset displaysleepnow
```

Require all of these:
- install rc 0;
- both labels loaded;
- the packet unchanged;
- the install finished before t0 − 300 s.

If install refuses or rc ≠ 0:
- run `"$PY" -B "$M_REAL/scripts/arm_align_r1.py" uninstall --custody-root "$S"`;
- confirm powermode 0;
- record and mail the lead. Do not retry.

Then write the trace, commit it to main from the canonical root (not `$M`), and exit at once with no other `claude` or `codex` process alive.

**From install until `chain.exited`:**
- no git operation in `$M` (not even status or fetch);
- no SSH sessions to the MBP;
- no agent alive on the MBP;
- no desk job.

The wrapper pins the chain source by a SHA-256 literal, and `night/r1_wrapper.jsonl` records the display dwell.

### Deadline alarms (for the Air watcher and the next activation)

With T0 = the installed `t0_epoch_s` and W = the installed `window_max_s` (≥ 126,480):

| Alarm | When | Condition | Action |
|---|---|---|---|
| Arm missed | 19:26 PST (T0MAX) | no arm trace, or no `com.joulewise.night` loaded | the night does not run today; lead decides |
| Early refusal | T0 + 10 min | `night-results/<plan_id>` ref or `$S/night/result.json` shows a refusal; `chain.started` absent | restore (uninstall, powermode 0) and mail Ed and the lead at once (item 250 (3)) |
| Likely redo (soft) | about T0 + 70,000 s (no-redo subtotal 58,712 + overhead 9,000 + hazard admission ≤ 3,300). At t0 19:26 that is about 14:53 PST 11-13 | no `chain.exited` | not a fault: inside bounds; note only |
| Ceiling | **T0 + W + 300 s**. At t0 19:26 and W 126,480 that is **06:39:00 PST Sat 11-14** | no `chain.exited` / no result | deadman/restore path; mail Ed and the lead |

The Air watcher keys on `chain_exit_code` and `r1_result.json` `status`, never on `result.json` `verdict`, which reads GO for a refused chain (A-01).

The ported plan omits `ac_powermode`, so the main-line watchdog parses it (checked: main's `NightPlan.from_mapping` accepts the ported plan and rejects it with the key). The watchdog's fence and relaunch then behave normally after `chain.exited`. The Air watcher still owns the alarms above.

### After the night (next activation, after `chain.exited`)

```sh
# S = custody root from the arm trace; PKT_SHA from the arm trace
"$PY" -I -B - "$S" "$PKT_SHA" <<'PY'
import json, sys
from pathlib import Path
s = Path(sys.argv[1]); r = json.loads((s / "night/align-r1/r1_result.json").read_text())
print("status", r.get("status"), "error", r.get("error"))                            # FIRST, before anything else
c = json.loads((s / "night/chain.exit-census.json").read_text()) if (s / "night/chain.exit-census.json").exists() else {}
print("chain exit_code", c.get("exit_code"))
pp = r.get("prepare_packet") or {}
print("D-7 packet", pp.get("sha256"), "==", sys.argv[2], pp.get("sha256") == sys.argv[2])  # mismatch = refused arm (D-7 step 3)
PY
```

Then follow runbook §4:
1. uninstall;
2. `pmset -g custom` must show powermode 0 (Automatic);
3. no stray `km003c_monitor.py`, `hazard_monitor.py` or root `powermetrics`;
4. KM003C capture present (Ed's rule: every measurement captures DC-in);
5. record, and mail Ed.

**Leave network time OFF.** W1 follows, and turning it ON re-creates the frequency-word hazard (item 251). Do not touch R1 custody. Report the following, temperatures and structure only (R1 is a rehearsal; no v4 outcome exists):

1. **RL-90, for every G0:**
   - its duration;
   - **which condition decided it** (band or slope);
   - release minus reference for **TV0h, Th0C and Tf08**. Item 286 notes that the G0 release record holds only fast and slow. Take Tf08 at release from the member's sidecar journal (`record_keys`); if it is absent, print null with the reason.
   - One paragraph on what differs between this kit and the 11-10/11 R1 night whose D gates timed out:
     - the reference captured in step-D, not R_op (RL-59);
     - an ordinary 30B predecessor;
     - 1,200 s caps on every gate;
     - timeout-runs flagged (RL-72 E3);
     - the TV0h/Th0C pair;
     - the 1.000 s inventory grid (RUN_STATE 280);
     - the per-key coverage bar (RL-84 P-3).
2. **RL-78 / RL-90:** Tf08 at each sidecar member's start minus the step-D window reference. **RL-64:** how far inside its band every release sat.
3. **RL-89 margin disposition.** Read the thermometry bar and `r1.sensor_inadmissible`.
   - If the only failed clause is Th0C's return time, report whether step-D's G0 released and whether every G1/H on the pair released inside its cap. The pick stands only if all did.
   - Any other failed clause, or any of those gates timing out, goes to the research lead.
4. **RL-72 E4 A-B-A bars:**
   - each leg's release sample lies inside every other leg's G0 band;
   - B's slow capture lies within 0.5 °C of the A1–A2 range.
   A failure makes the adoption inconclusive, and it goes to the research lead.
5. **RL-91.** If the wrapper was out:
   - did any idle capture time out?
   - was a root `powermetrics` alive outside a member's own capture at any census?
   If it was in: the `capture_reaps` records.
   - **Ticker:** per member, the count of ticks that follow the previous tick by under 0.5 s. Where that is over 1% of the member's ticks, also print its time-weighted load statistics.
6. Flags `r1.g0_timeout_run`, `r1.g0_cap_saturated` and `inconclusive_segments`, with their counts.
7. The lead's desk: `align_r1_followup_kit.py desk --run-dir "$S/night/align-r1"` (temperature-only; the lead's to run). Commit nothing from `r1_slots.json`: the slots go to the research lead.

### Stop or refuse rules (summary)

Do not arm, and mail the lead, if any of these holds:
- a check line is missing or differs;
- `__NIGHT_SHA__` is not the commit the cited Part A smoke passed at;
- the earliest t0 is after 19:26 PST;
- the wrapper is in and the `sudo -n -l /bin/kill` listing fails;
- `prepare` refuses;
- a marker is present;
- a non-magistrate `com.joulewise` label is loaded;
- network time is ON, or the word is not 0, after the item-251 remedy;
- an external volume is mounted;
- any agent or desk job is alive;
- the `night.lock` pid is alive or `lsof` shows a holder;
- install rc ≠ 0;
- the packet re-hash differs.

Do not re-run Part B, do not reuse a smoke soak, and do not edit any condition-13 file.
