# BY-PREP-P generation and verification commands

These commands were prepared by source inspection. They have **not run in this seat**: the selected cloud workspace never became usable during the investigation. Run them from the integrated BYTES lane, with windows paused. They write only under .codex-report/by-prep-p. They do not register, prepare, install, arm, harvest again, or edit a frozen H session.

## 1. Stage frozen H desk inputs

Use an existing checkout of mpmdw/JouleWise-data at DATA. Its branch analysis/bytes-h-desk-20261022 contains the pinned commit below. On the Mac the recorded data checkout is /Users/edr/code/JouleWise-data. On Cloud choose its actual path.

~~~sh
cd /workspace/JouleWise
PY=python3
DATA=/path/to/JouleWise-data
OUT="$PWD/.codex-report/by-prep-p/replay"
export PY DATA OUT
export PYTHONDONTWRITEBYTECODE=1 JW_B5_SYNTHETIC_ONLY=1
mkdir -p "$OUT/source" "$OUT/tmp"
git -C "$DATA" cat-file -e 8db1b40d64d8c543e7a9bee4fd9ced0da63d4b0b
git -C "$DATA" archive 8db1b40d64d8c543e7a9bee4fd9ced0da63d4b0b bytes-h-desk-20261022 | tar -x -C "$OUT/source"
~~~

If that commit is absent, fetch only the named data branch into the data checkout first. Read-only raw inputs are:

- export/bytes-h-20261021T185555335572Z-calibration.runs.csv and matching .session.json;
- MEASUREMENTS.json;
- tables/indep_runs.json (per-run one-copy allocated bytes, **not** retained_bytes divided by two);
- tables/fixed_inputs.json (measured stage overhead; fixed time is a lower bound).

The code/kit/trees for reproducing this report are at JouleWise 1c458d71d8a048e24b6c3a6b402fe3c34d9f57c3. If the integrated tree changes, regenerate and review all affected rows instead of expecting old integers to stay fixed.

## 2. Augment a copy with already measured raw-byte receipts

No model execution or power measurement is needed. The source independent extraction explicitly defines raw_bytes as inode-deduplicated POSIX st_blocks*512 over the raw bundle. It is the same byte domain C5 requires. Never infer it from the two-copy retained_bytes.

~~~sh
TMPDIR="$(mktemp -d "$OUT/tmp/augment.XXXXXX")" "$PY" -B - <<'PY'
import copy, json, os
from decimal import Decimal
from pathlib import Path
out = Path(os.environ["OUT"])
src = out / "source/bytes-h-desk-20261022"
original = (src / "MEASUREMENTS.json").read_text()
m = json.loads(original)
ind = {r["run_id"]: r for r in json.loads((src / "tables/indep_runs.json").read_text())}
timed = 0
for rid, r in m["runs"].items():
    if r["stream_s"] is None:
        r["raw_allocated_bytes"] = None
        continue
    source = ind[rid]
    for key in ("request_s", "member_wall_s", "stream_s"):
        assert r[key] == source[key], (rid, key)
    value = source["raw_bytes"]
    assert type(value) is int and value >= 0, rid
    r["raw_allocated_bytes"] = value
    timed += 1
text = json.dumps(m, indent=2, sort_keys=True, allow_nan=False) + "\n"
# Preserve the original measured decimal values through serialization.
before = json.loads(original, parse_float=Decimal)
after = json.loads(text, parse_float=Decimal)
for rid, row in before["runs"].items():
    for key in ("request_s", "member_wall_s", "stream_s", "thermal_level"):
        assert row[key] == after["runs"][rid][key], (rid, key)
(out / "MEASUREMENTS.raw.json").write_text(text)
# A separate draft exposes the measured fixed-time lower bound. Never relabel
# these as complete receipts or change the frozen original MEASUREMENTS.json.
draft = copy.deepcopy(m)
fixed = json.loads((src / "tables/fixed_inputs.json").read_text())
draft["sizing"] = {k: fixed[k] for k in ("fixed_desk_s", "collection_stage_overhead_s")}
draft["by_prep_p_note"] = "DRAFT: fixed_desk_s lower bound; verdict/backup unmeasured; soak margin incomplete"
(out / "MEASUREMENTS.sizing-draft.json").write_text(
    json.dumps(draft, indent=2, sort_keys=True, allow_nan=False) + "\n")
print("timed raw-byte joins:", timed)
print("original measured values preserved; original input unchanged")
print("draft fixed_desk_s:", draft["sizing"]["fixed_desk_s"])
print("draft collection_stage_overhead_s:", draft["sizing"]["collection_stage_overhead_s"])
PY
~~~

Expected evidence: 95 timed joins; fixed_desk_s 1185 and collection_stage_overhead_s 44.44705606997013. Exact identity, rather than a tolerance, is the property of copying an existing recorded value.

## 3. Run current C5 on both copies

The first output derives P and stream bounds without pretending that missing sizing receipts exist; programmed_span_s stays null. The second derives the explicitly labelled time draft using the table above. Both still expose the stopped H session's completeness and thermal failures. Exit 2 with a newly written JSON is computed failure, not a program fault; exit 1 without a new JSON is not a usable candidate. Do not demand a zero exit or remove flagged rows to obtain it.

~~~sh
RUNS="$OUT/source/bytes-h-desk-20261022/export/bytes-h-20261021T185555335572Z-calibration.runs.csv"
export RUNS
rc=0
TMPDIR="$(mktemp -d "$OUT/tmp/c5-raw.XXXXXX")" "$PY" -B scripts/bytes_gates.py \
  --runs "$RUNS" --measurements "$OUT/MEASUREMENTS.raw.json" \
  --kit-plan configs/campaigns/bytes_mac_check/collection_plan.json \
  --committed-sizing configs/campaigns/bytes_mac_check/registration/sizing_b5.json \
  --disk-evidence "$OUT/source/bytes-h-desk-20261022/tables/disk_h.json" \
  --out "$OUT/C5.raw.json" > "$OUT/C5.raw.log" 2>&1 || rc=$?
printf 'C5 raw exit=%s\n' "$rc"
tail -n 8 "$OUT/C5.raw.log"
rc=0
TMPDIR="$(mktemp -d "$OUT/tmp/c5-draft.XXXXXX")" "$PY" -B scripts/bytes_gates.py \
  --runs "$RUNS" --measurements "$OUT/MEASUREMENTS.sizing-draft.json" \
  --kit-plan configs/campaigns/bytes_mac_check/collection_plan.json \
  --committed-sizing configs/campaigns/bytes_mac_check/registration/sizing_b5.json \
  --disk-evidence "$OUT/source/bytes-h-desk-20261022/tables/disk_h.json" \
  --out "$OUT/C5.sizing-draft.json" > "$OUT/C5.sizing-draft.log" 2>&1 || rc=$?
printf 'C5 draft exit=%s\n' "$rc"
tail -n 8 "$OUT/C5.sizing-draft.log"
~~~

## 4. Materialize and validate six report-only draft rows

This creates an isolated copy of the registration sizing document in the report directory. It leaves the real configs/b6/registration/sizing_b5.json untouched. The outer draft row adds pack_id; C5.sessions does not supply that field itself. A top-level required_free_bytes without disk_derivation is insufficient.

~~~sh
TMPDIR="$(mktemp -d "$OUT/tmp/rows.XXXXXX")" "$PY" -B - <<'PY'
import json, math, os
from pathlib import Path
from joulewise.b6 import plan_inputs, precheck, registration
root = Path.cwd()
out = Path(os.environ["OUT"])
c5 = json.loads((out / "C5.sizing-draft.json").read_text())
sized = json.loads((root / "configs/b6/registration/sizing_b5.json").read_text())
draft_reg = out / "registration-draft"
draft_reg.mkdir(exist_ok=True)
expected = [73814147037, 75981813519, 79464395095, 85140886637, 75849013177, 62811368483]
for i, expected_p in enumerate(expected, 1):
    pack = f"bytes-s{i}-p1"
    s = c5["sessions"][pack]
    assert s["programmed_span_s"] is not None
    assert s["T_stream_max_s"] is not None
    assert plan_inputs.valid_disk_terms(s["disk_derivation"]), pack
    assert s["disk_derivation"]["required_free_bytes"] == expected_p, pack
    sized["packs"][pack] = {
        "pack_id": pack,
        "programmed_span_s": s["programmed_span_s"],
        "T_stream_max_s": s["T_stream_max_s"],
        "disk_derivation": s["disk_derivation"],
        "measured_margin": c5["measured_margin"],
        "measured_margin_complete": False,
        "registration_ready": False,
        "note": "DRAFT ONLY: incomplete soaks and fixed-time lower bound",
    }
(draft_reg / "sizing_b5.json").write_text(json.dumps(sized, indent=2, sort_keys=True) + "\n")
registration.load_sizing(draft_reg)
for i in range(1, 7):
    pack = f"bytes-s{i}-p1"
    row = sized["packs"][pack]
    inputs = {"pack_root": str(root / "configs/campaigns" / pack),
              "spare_retries": False, "thresholds": {"disk": {}}}
    plan_inputs.encode_disk_budget(inputs, row["disk_derivation"])
    b = inputs["disk_budget"]
    assert 3 * b["member_count"] * b["bytes_per_member"] + b["headroom_bytes"] == b["required_free_bytes"]
    limits = precheck.thresholds_for(root, pack, draft_reg)["disk"]
    assert limits["largest_session_bytes"] == b["required_free_bytes"]
    assert limits["headroom_bytes"] == 0
    print(pack, "P", b["required_free_bytes"], "n", b["member_count"],
          "q", b["bytes_per_member"], "headroom", b["headroom_bytes"],
          "smoke_share", limits["smoke_bytes"], "exact")
print("6/6 report-only rows validated; nothing registered")
PY
~~~

The expected P check is exact because integer-byte identity is the property. If the source lane, allowance form or inputs changed, inspect and rederive the expected table; never adjust a comparison bar.

## 5. Production-shaped synthetic diagnostic through real functions

Optional verification for the implementing seat when the shell is available. This uses the existing 123-member synthetic fixture helper, actual export_runs.export, current C5, actual tree-derived native encoding, and the real disk hazard functions. No unittest suite is invoked, no new test is written, and no live identity/disk measurement or install occurs. Each synthetic number comes from the existing fixture; no measured threshold is selected here.

~~~sh
TMPDIR="$(mktemp -d "$OUT/tmp/synthetic.XXXXXX")" "$PY" -B - <<'PY'
import csv, tempfile
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
from tests.test_bytes_gates import synthetic_harvest
from scripts import bytes_gates
from joulewise.b6 import plan_inputs
from joulewise.hazards import base, disk
with tempfile.TemporaryDirectory() as td:
    result, measured = synthetic_harvest(Path(td))
    with result.csv_path.open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    c5 = bytes_gates.calculate(deepcopy(rows), bytes_gates.read(result.sidecar_path),
                              deepcopy(measured), bytes_gates.read(bytes_gates.KIT))
    assert len(rows) == 123
    checked = 0
    for pack, row in c5["sessions"].items():
        if not pack.endswith("-p1"):
            continue
        terms = row["disk_derivation"]
        assert plan_inputs.valid_disk_terms(terms)
        inputs = {"pack_root": str(Path.cwd() / "configs/campaigns" / pack),
                  "spare_retries": False, "thresholds": {"disk": {}}}
        plan_inputs.encode_disk_budget(inputs, terms)
        b = inputs["disk_budget"]
        native = 3 * b["member_count"] * b["bytes_per_member"] + b["headroom_bytes"]
        assert native == terms["required_free_bytes"]
        for free, wanted in ((native - 1, base.REFUSE), (native, base.PASS)):
            reading = disk.measure(base.Context(), targets=[{"path": "/synthetic", "copies": 1}],
                statvfs=lambda p: SimpleNamespace(f_bavail=free, f_frsize=1, f_blocks=2*native),
                stat=lambda p: SimpleNamespace(st_dev=1))
            verdict = disk.judge(reading, {"planned_bytes": native, "headroom_bytes": 0})
            assert verdict.status == wanted
        checked += 1
    print("synthetic export rows:", len(rows))
    print("pass-1 C5/native/disk boundaries:", checked, "exact")
PY
~~~

This is a diagnostic of export/C5/encoding/hazard arithmetic. It does not prove DriverLane launch, the native plan writer, Mac hardware, or the missing registration/launch authority. BY-C5's existing all-twelve native-plan evidence is cited separately in the report.

## 6. Operator and registration handoff

After the lead has settled and registered the actual complete or explicitly qualified allowance inputs, BY-SLOTS/BY-PIN must edit the owning paths, regenerate tree-dependent pins, and run their required focused checks. Those paths are outside this report seat's write scope.

A byte-only pin audit is agent work. If actual local model-file rehashing is wanted, use the callable derive() in configs/campaigns/bytes_mac_check/registration/derive_identity_pins.py and redirect its returned documents into a report destination; its CLI writes the kit registration, so do not run that CLI in this report seat. BY-G's appendix shows the pass-tree variant. Neither hashing nor the bytes manifest supplies runtime measurements.

For live disk availability on the actual session volume, this read-only snapshot is agent-doable while paused. Replace SESSION_VOLUME with the actual planned session parent; do not substitute Cloud disk space. It is a timestamped observation, not the arm's later receipt.

~~~sh
SESSION_VOLUME=/Users/edr/night-b6
export SESSION_VOLUME
TMPDIR="$(mktemp -d "$OUT/tmp/free.XXXXXX")" "$PY" -B - <<'PY'
import datetime, os
p = os.environ["SESSION_VOLUME"]
v = os.statvfs(p)
print(datetime.datetime.now(datetime.timezone.utc).isoformat(), p,
      "free_bytes", v.f_bavail * v.f_frsize, "purgeable_excluded")
PY
~~~

Do not collect soaks, captures, floors, a stream probe or test 7 with an agent active. The lead's separate quiet-Mac session owns those measurements. No launch command is included here: prepare/launch must first use the registered integrated measurement checkout and its authentic ledger, real bindings and smoke authority.
