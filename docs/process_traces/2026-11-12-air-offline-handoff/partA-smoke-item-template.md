285. **Laptop lead (interactive session 52877569, Opus 5.5), __STAMP__: MAGISTRATE: run the RL-89 Part A smoke on `__SHORT__`: a FRESH TV0h/Th0C idle soak, then Part A only (`--fresh-soak --parts A`). It runs on the final bytes for tonight's R1 follow-up night. No prepare, no arm. The launch is your LAST action, and you exit at once. LAUNCH BEFORE 11:05 PST: the soak refuses if it would end after 11:45, the start of the OS batch window. If it is too late, wait until after 13:15 and launch then.**

```pointer
owner: magistrate
wait: none
deadline: __DEADLINE_ISO__
on_early_or_refused: any refusal or failure goes back to the lead. Do not retry, do not extend, and do not reuse OUT. If Part A's G0 does not release inside 1,200 s, NOTHING arms; report it, since it goes to the research lead (RL-89)
next_observable: the next activation runs the check below and reports it (rc, parts, soak, G0 outcome and duration, sensors) by email and as RUN_STATE 286
```

- **Why (RL-89, RL-94, at `audit/2026-11-10-fable` f89488aec).** Item 282's Part B table failed selection only because the runtime config's `r0_classified_keys` held six transcribed keys, not R0's set. R0's `smc/r0.json` (sha256 `e6231a8f…769b`) classes 60 keys eligible as die or heatsink, and Th0C is heatsink-eligible. The pair for the night is **s_fast TV0h, s_slow Th0C**, and Tf08 is still recorded.
  - The config fix is the only condition-13 change.
  - The Part B table was regenerated from item 281's saved segment without re-measuring. It is accepted (`1fdd980c…eba3`; the old table `6b05379d…f373` is kept), and the ruling file is `docs/run_reports/2026-11-12-rl89/sensor_ruling_rl89.json`.
  - **Part B is NOT re-run** (RL-89).
  - The only soak reference on disk (R1 night) has no Th0C, so this smoke takes its own fresh 1,800 s idle soak, under RL-94. It is this smoke's reference only; the night runs its own soak.
- **Smoke commit `__SHORT__`:** presign `22f438fd3` plus the RL-89 stack, each piece reviewed:
  - `bfd25fc72`: config; the 60 keys are script-generated from r0.json.
  - `1590f0f4f`: the regenerated table and ruling file.
  - `06b706065`: the deviation row.
  - `e0d3d407d`: the runner's `--fresh-soak` and `--parts A`, smoke-only.
  - `384449027`: the RL-94 kit fix. W1 records R0's Tf08 via `r0_picks`.
  - Fable cold executing review: __REVIEW__.
  - __PMNOTE__
- **PASS condition (RL-89):** Part A's G0 on TV0h/Th0C at 1.0/1.0 °C bands RELEASES inside 1,200 s.
- **High Power marker:** if `/Users/Shared/JouleWise/host-power/high-power.marker` exists, STOP and report. Leave `night.lock` as found.

**Start and check (while you are still alive):**

```sh
git -C /Users/edr/code/JouleWise fetch origin
cd /Users/edr/code/jw-wt/r1-followup-smoke
git checkout --detach __SHORT__
test "$(git rev-parse HEAD)" = __FULL__
REPO="$PWD"
: "${PY:?Set PY to the existing pinned measurement-venv interpreter (do not resolve the symlink)}"
: "${MAGISTRATE_PID:?Set to the PID of this magistrate's own claude process}"
ps -o pid=,comm= -p "$MAGISTRATE_PID"     # must show the claude process, not a tool shell
CUSTODY="${MAGISTRATE_WATCHDOG_CUSTODY_ROOT:-/Users/edr/night-custody/magistrate}"
OUT="$REPO/.desk/r1-followup-smoke-$("$PY" -B -c 'import time; print(time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()))')"
test -z "$(git status --porcelain)"
"$PY" -B -c 'from pathlib import Path; import subprocess; from joulewise.align.apple import v4_registration as r; root=Path.cwd(); head=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip(); print(r.verify_r1_executed_sources(root,{"executed_commit":head}))'
# RL-89 Mac check: the config's 60 keys equal r0.json's eligible rows (sha verified first)
# RL-89 item 4 arm check (read-only). Run from the night checkout at the reviewed commit.
R0=/Users/edr/night-align/r0-v4-20261108T0550Z/smc/r0.json
"$PY" -I -B - "$R0" "$REPO/configs/align/v4/r1_runtime.json" <<'PY'
import hashlib, json, sys
EXPECT = "e6231a8f3e6ab6177bbedbf12b878c958a7b4d4331e36472c74c2a192588769b"
raw = open(sys.argv[1], "rb").read()
got = hashlib.sha256(raw).hexdigest()
assert got == EXPECT, f"REFUSE: r0.json sha256 {got} != {EXPECT}"        # 1. sha first
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
"$PY" -B -m unittest tests.align.test_r1_smoke_launcher.LauncherTests.test_r1_smoke_plist_runs_interactive_like_the_night_templates   # must be OK
test ! -e /Users/Shared/JouleWise/host-power/high-power.marker
"$PY" -B scripts/launch_align_r0.py preflight --disk-path "$REPO"
DEADLINE="$("$PY" -B -c 'import time; print(time.time()+7200)')"
```

The RL-89 check must print `RL-89 MAC CHECK OK … 60 16 44` and the config sha256 `95825997f7fd50e3a86342c059bd1eba2cc37139684c76eed35f0ca6ed0a1dad`. Anything else means STOP.

**Run (your last action):**

```sh
"$PY" -B scripts/launch_align_r0.py launch \
  --runner-kind r1-smoke --repo "$REPO" --python-bin "$PY" \
  --output "$OUT" --fresh-soak --parts A --disk-path "$REPO" \
  --custody-root "$CUSTODY" --magistrate-pid "$MAGISTRATE_PID" \
  --deadline "$DEADLINE" --exit-wait-seconds 180 --start-wait-seconds 30
echo "$OUT"
```

Require exit 0 and `"next": "exit the magistrate session now"` with a claimed fence (fence `pid` ≠ `MAGISTRATE_PID`). Then exit at once, with no other `claude`/`codex` process running.

**Check (next activation, after the fence is gone):**

```sh
"$PY" -B - "$OUT" <<'PY'
import hashlib, json, sys
from pathlib import Path
root = Path(sys.argv[1])
r = json.loads((root / "runner_receipt.json").read_text())
print(json.dumps({k: r.get(k) for k in ("rc", "parts", "parts_requested", "fresh_soak", "error")}, sort_keys=True))
print([(s["name"], s["rc"]) for s in r["steps"]])
soak = [s for s in r["steps"] if s["name"] == "soak"]
print("soak", soak and soak[0].get("rc"), soak and soak[0].get("result", {}).get("soak_reference_sha256"))
assert r["rc"] == 0 and r["parts"] == {"A": True, "B": False} and r.get("fresh_soak") is True
assert soak and soak[0]["rc"] == 0
assert [s["name"] for s in r["steps"]].count("close-volumes") == 1
for feed in r["feeds"].values():
    assert feed["stop"]["proven_stopped"]
    for f in feed["files"]:
        with (root / f["path"]).open("rb") as h:
            assert hashlib.file_digest(h, "sha256").hexdigest() == f["sha256"]
PY
find "$OUT" -name smoke_part_a.json -exec "$PY" -B -c 'import json,sys; g=json.load(open(sys.argv[1])); print(sys.argv[1], g["g0"].get("outcome"), g["g0"].get("duration_s"), g.get("admission_s"))' {} \;
test ! -e "$CUSTODY/desk_fence.json"; launchctl list | grep -c 'com.joulewise.align-r0' || true   # expect 0
```

PASS means: the receipt asserts hold, and step D's `smoke_part_a.json` shows G0 `released` with `duration_s` ≤ 1,200. Report:
- the G0 duration and its deciding condition;
- release minus reference for fast and slow (and for Tf08, if recorded);
- the soak reference sha256 and its two bands.

A G0 `timeout` means NOTHING arms; it goes to the research lead. Also run `plutil -p "$CUSTODY"/r0-launches/<token>/*.plist | grep ProcessType`, which must show `Interactive`.

