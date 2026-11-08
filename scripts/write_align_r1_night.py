#!/usr/bin/env python3
"""Write (and desk-check) the ALIGN v4 R1 night: one run_night plan around the unchanged R1 chain.

Route (docs/align/R1-ARM-RUNBOOK-opus.md): a ``DIAGNOSTIC_NO_PACK`` night whose
registration is the ruled, chain-bound ``configs/align/v4/r1_night_registration.json``
(``night_gate.RULED_REGISTRATIONS``) and whose payload kind is ``align_v4_r1``
(``joulewise.night_kinds``). ``run_night`` therefore runs, unchanged, every
admission it runs for a calibration night before it launches anything:

* the agent census, the AC powermode admission (plan 0; an R1 High Power
  marker left by a crash is restored first), the dead-man overrun check;
* network time OFF and the 600 s settle, overlapped with the D-134 clean dwell
  (``scripts/prewindow_check.sh --wait``: 600 s continuous, <= 5 % CPU per
  contaminating process, load <= 2.0, 45 min cap) and the start-conditions
  record;
* C1 the ruled registration, which binds the R1 chain's SHA-256; C3 HID, AC,
  battery float, display setting, load and thermal; C4 the clock; C5 the window,
  plan freshness, a clean measurement checkout at ``measurement_head``, the
  wrapper against its sidecar and the R1 chain source against both the
  committed blob and the wrapper's pinned digest;
* then the chain once, under the in-chain agent census and the wall-clock
  deadline ``t0 + window_max_s + 300 s`` with a proven process-group stop, and
  the result record and courier.

The wrapper this script renders adds what no run_night class gives a
non-hazard night: the KM003C wall meter (``scripts/km003c_monitor.py``, the
same program and stream layout the HAZARD_PACK driver supervises), display
sleep plus a 300 s dwell (R0-L3), a re-check of the R1 chain digest, and a
refusal of both installer inspection modes. It never edits or replaces the R1
chain: it runs ``scripts/night_chains/align_r1_rehearsal.zsh`` from the
measurement checkout as a child and returns its exit code.

``check`` is the desk control for this plan (``run_night --dry-arm`` takes only
HAZARD_PACK plans): it runs the gate's static checks (C5 start, chain identity,
C1 registration) with the real probes at the plan's t0, without launching.
"""
from __future__ import annotations

import argparse
from dataclasses import replace
from datetime import datetime, timedelta
import hashlib
import json
import math
import os
from pathlib import Path
import shlex
import subprocess
import sys
import time
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from joulewise import night_gate  # noqa: E402
from joulewise.night_kinds import kind_row  # noqa: E402

KIND = "align_v4_r1"
ROW = kind_row(KIND)
REGISTRATION_PATH = ROW.protocol_path
CHAIN_SOURCE_PATH = ROW.chain_source_path
METER_PROGRAM = "scripts/km003c_monitor.py"
PMSET_BIN = "/usr/bin/pmset"
SHASUM_BIN = "/usr/bin/shasum"
BATCH_WINDOW_START = (11, 45)   # R1 driver OS_BATCH_WINDOW_LOCAL (ruling 8)
BATCH_ZONE = ZoneInfo("America/Los_Angeles")   # R1 driver LOCAL_ZONE (tests pin the equality)
SIZING_SCHEMA = "joulewise.align_v4_r1_night_sizing.v1"
EXIT_INSPECTION_REFUSED = 64
EXIT_CHAIN_SOURCE_CHANGED = 65


class R1NightError(ValueError):
    pass


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def read_registration(measurement_root: Path) -> tuple[dict, str]:
    raw = (Path(measurement_root) / REGISTRATION_PATH).read_bytes()
    digest = _sha256(raw)
    if night_gate.armable_registration(digest) is None:
        raise R1NightError(f"{REGISTRATION_PATH} sha256 {digest} is not a ruled, armable registration")
    value = json.loads(raw)
    if value.get("night_kind") != KIND or value.get("chain_source_path") != CHAIN_SOURCE_PATH:
        raise R1NightError("registration does not name the align_v4_r1 kind and the R1 chain")
    return value, digest


def _batch_starts(t0: float, end: float) -> list[float]:
    """Every 11:45 in [t0, end] in the R1 driver's own zone (its ruling 8 clock)."""
    day = datetime.fromtimestamp(t0, BATCH_ZONE).date() - timedelta(days=1)
    starts = []
    while True:
        moment = datetime(day.year, day.month, day.day, *BATCH_WINDOW_START, tzinfo=BATCH_ZONE).timestamp()
        if moment > end:
            return starts
        if moment >= t0:
            starts.append(moment)
        day += timedelta(days=1)


def size_window(t0_epoch_s: float, sizing: dict) -> dict:
    """RUN_STATE items 215/216: the redo floor plus this route's own bracket, close and harvest.

    The 96,427 s floor already carries one 11,164 s batch-window encounter;
    each further local 11:45 the window can reach adds one more (item 216:
    "11,164 s per segment that can touch 11:45-13:15"). Iterated to a fixed point.
    """
    route = {name: int(sizing[name]) for name in (
        "admission_allowance_s", "display_dwell_s", "meter_allowance_s",
        "calibration_brackets_allowance_s", "harvest_allowance_s", "close_allowance_s")}
    base = int(sizing["r1_floor_s"]) + sum(route.values())
    extra_encounters = 0
    for _ in range(8):
        window = 60 * math.ceil((base + extra_encounters * int(sizing["batch_encounter_s"])) / 60)
        crossings = len(_batch_starts(t0_epoch_s, t0_epoch_s + window))
        wanted = max(0, crossings - 1)
        if wanted == extra_encounters:
            break
        extra_encounters = wanted
    else:  # pragma: no cover - the window is < 48 h, so at most two crossings
        raise R1NightError("window sizing did not converge")
    return {"schema": SIZING_SCHEMA, "authority": sizing["authority"], "r1_floor_s": int(sizing["r1_floor_s"]),
            "route_allowances_s": route, "batch_window_crossings": crossings,
            "extra_batch_encounters": extra_encounters,
            "batch_encounter_s": int(sizing["batch_encounter_s"]), "window_max_s": window,
            "programmed_span_s": window - route["admission_allowance_s"],
            "latest_chain_start_after_t0_s": route["admission_allowance_s"]}


def render_wrapper(*, plan_id: str, chain_source_sha256: str, programmed_span_s: int,
                   display_dwell_s: int, pmset_bin: str = PMSET_BIN) -> bytes:
    q = shlex.quote
    text = f"""#!/bin/zsh
# ALIGN v4 R1 night wrapper. GENERATED by scripts/write_align_r1_night.py; never edit.
# run_night launches this file once, after its DIAGNOSTIC_NO_PACK admission, the
# ruled chain-bound registration (configs/align/v4/r1_night_registration.json)
# and the C5 source check of the R1 chain. It adds the KM003C meter, display
# sleep and a dwell, then runs the unchanged R1 chain as a child and returns its
# exit code. Everything it starts lives in run_night's chain process group, so the
# window deadline and an interrupt stop it with the chain.
export NIGHT_PAYLOAD_KIND={KIND}
export EVIDENCE_CHAIN_SOURCE_SHA256={chain_source_sha256}
export NIGHT_PROGRAMMED_SPAN_S={int(programmed_span_s)}
export JOULEWISE_NIGHT_PLAN_ID={q(plan_id)}
export ALIGN_R1_DISPLAY_DWELL_S={int(display_dwell_s)}
export ALIGN_R1_PMSET_BIN={q(pmset_bin)}
set -u
zmodload zsh/datetime

if [[ -n "${{NIGHT_VERIFY_ONLY:-}}" || -n "${{NIGHT_RESERVATION_ARGV_ONLY:-}}" ]]; then
  print -u2 -- "align-v4-r1 wrapper: installer inspection modes are refused; nothing ran"
  exit {EXIT_INSPECTION_REFUSED}
fi
: "${{NIGHT_DIR:?run_night must supply NIGHT_DIR}}"
: "${{MEASUREMENT_ROOT:?run_night must supply MEASUREMENT_ROOT}}"
: "${{PY:?run_night must supply PY}}"
SOURCE="$MEASUREMENT_ROOT/{CHAIN_SOURCE_PATH}"
METER="$MEASUREMENT_ROOT/{METER_PROGRAM}"
CUSTODY="${{NIGHT_DIR:h}}"
METER_DIR="$CUSTODY/hazards/meter"
METER_STOP="$NIGHT_DIR/r1-meter.stop"
RECORD="$NIGHT_DIR/r1_wrapper.jsonl"
METER_PID=""

note() {{
  print -r -- "{{\\"epoch_s\\":$EPOCHREALTIME,$1}}" >> "$RECORD"
}}

stop_meter() {{
  [[ -n "$METER_PID" ]] || return 0
  : > "$METER_STOP"
  local waited=0
  while kill -0 "$METER_PID" 2>/dev/null && (( waited < 150 )); do
    sleep 0.1; waited=$(( waited + 1 ))
  done
  if kill -0 "$METER_PID" 2>/dev/null; then
    kill -TERM "$METER_PID" 2>/dev/null
    note "\\"event\\":\\"meter_stop\\",\\"forced\\":true"
  else
    note "\\"event\\":\\"meter_stop\\",\\"forced\\":false"
  fi
  wait "$METER_PID" 2>/dev/null
  METER_PID=""
}}

on_signal() {{
  trap '' HUP INT TERM
  note "\\"event\\":\\"signal\\",\\"signal\\":\\"$1\\""
  stop_meter
  exit $2
}}
trap 'on_signal HUP 129' HUP
trap 'on_signal INT 130' INT
trap 'on_signal TERM 143' TERM

note "\\"event\\":\\"start\\",\\"plan_id\\":\\"$JOULEWISE_NIGHT_PLAN_ID\\",\\"pid\\":$$"

# The R1 chain source must still be the bytes the registration binds.
actual="$({SHASUM_BIN} -a 256 "$SOURCE" 2>/dev/null)"
actual="${{actual%% *}}"
if [[ "$actual" != "$EVIDENCE_CHAIN_SOURCE_SHA256" ]]; then
  note "\\"event\\":\\"refused\\",\\"reason\\":\\"chain_source_changed\\",\\"actual\\":\\"$actual\\""
  exit {EXIT_CHAIN_SOURCE_CHANGED}
fi

# The KM003C wall meter (Ed 2026-11-07: every measurement captures it), the
# program and stream layout the HAZARD_PACK driver uses. A clean exit (meter
# absent, or stopped) is final; a crash restarts after 30 s.
mkdir -p "$METER_DIR"
(
  trap - HUP INT TERM
  n=1
  while [[ ! -e "$METER_STOP" ]]; do
    out="$(printf '%s/stream-%03d.jsonl' "$METER_DIR" "$n")"
    while [[ -e "$out" ]]; do n=$(( n + 1 )); out="$(printf '%s/stream-%03d.jsonl' "$METER_DIR" "$n")"; done
    "$PY" -B "$METER" --out "$out" --stop-file "$METER_STOP"
    rc=$?
    print -r -- "{{\\"epoch_s\\":$EPOCHREALTIME,\\"event\\":\\"meter_exit\\",\\"stream\\":$n,\\"rc\\":$rc}}" >> "$RECORD"
    (( rc == 0 )) && break
    for i in {{1..300}}; do [[ -e "$METER_STOP" ]] && break; sleep 0.1; done
  done
) &
METER_PID=$!
note "\\"event\\":\\"meter_started\\",\\"pid\\":$METER_PID"

# R0-L3: display asleep, then a dwell before the first census-checked segment.
"$ALIGN_R1_PMSET_BIN" displaysleepnow
note "\\"event\\":\\"displaysleepnow\\",\\"rc\\":$?,\\"dwell_s\\":$ALIGN_R1_DISPLAY_DWELL_S"
sleep "$ALIGN_R1_DISPLAY_DWELL_S"
note "\\"event\\":\\"dwell_end\\""

/bin/zsh "$SOURCE"
rc=$?
note "\\"event\\":\\"r1_chain_exit\\",\\"rc\\":$rc"
stop_meter
note "\\"event\\":\\"end\\",\\"rc\\":$rc"
exit $rc
"""
    return text.encode("utf-8")


def _git_head(root: Path) -> str:
    return subprocess.run(["/usr/bin/git", "-C", str(root), "rev-parse", "HEAD"], check=True,
                          capture_output=True, text=True).stdout.strip()


def write(measurement_root, custody_root, t0_epoch_s, *, repo_root=ROOT, repo_head=None,
          measurement_head=None, plan_id=None, now=time.time, pmset_bin=PMSET_BIN,
          display_dwell_s=None) -> dict:
    """Create the night's custody once: plan, wrapper, sidecar and sizing record.

    ``pmset_bin`` and ``display_dwell_s`` are synthetic-test seams only; the
    command line always renders /usr/bin/pmset and the registered dwell.
    """
    measurement = Path(measurement_root).absolute()
    custody = Path(custody_root).absolute()
    registration, registration_sha256 = read_registration(measurement)
    source_raw = (measurement / CHAIN_SOURCE_PATH).read_bytes()
    if _sha256(source_raw) != registration["chain_source_sha256"]:
        raise R1NightError("the measurement checkout's R1 chain is not the bytes the registration binds")
    if registration.get("ac_powermode") != 0:
        raise R1NightError("the R1 night plan admits Automatic (0) only; R1 sets High Power itself")
    t0 = float(t0_epoch_s)
    if t0 % 60:
        raise R1NightError("t0 must fall on a whole minute (run_night.schedule)")
    authored = float(now())
    if t0 <= authored:
        raise R1NightError("t0 must be in the future")
    if custody.exists() and any(custody.iterdir()):
        raise R1NightError("custody_root must be absent or empty; a night never reuses custody")
    sizing = size_window(t0, registration["sizing"])
    plan_id = plan_id or ROW.plan_id_prefix + datetime.fromtimestamp(t0).strftime("%Y%m%dT%H%M")
    dwell = int(registration["display"]["dwell_s"] if display_dwell_s is None else display_dwell_s)
    wrapper = render_wrapper(plan_id=plan_id, chain_source_sha256=registration["chain_source_sha256"],
                             programmed_span_s=sizing["programmed_span_s"], display_dwell_s=dwell,
                             pmset_bin=pmset_bin)
    chain_path = custody / "chain.zsh"
    plan_value = {
        "schema": night_gate.PLAN_SCHEMA, "schema_version": night_gate.PLAN_SCHEMA_VERSION,
        "plan_id": plan_id, "receipt_class": ROW.receipt_class,
        "t0_epoch_s": t0, "window_max_s": sizing["window_max_s"], "authored_epoch_s": authored,
        "repo_head": repo_head or _git_head(Path(repo_root)),
        "measurement_root": str(measurement),
        "measurement_head": measurement_head or _git_head(measurement),
        "chain_path": str(chain_path), "chain_sha256_path": str(chain_path) + ".sha256",
        "custody_root": str(custody), "registration_path": REGISTRATION_PATH,
    }
    night_gate.NightPlan.from_mapping(plan_value)   # the driver's own parser
    custody.mkdir(parents=True, exist_ok=True)
    records = {}
    for name, raw in (("chain.zsh", wrapper),
                      ("chain.zsh.sha256", f"{_sha256(wrapper)}  chain.zsh\n".encode()),
                      ("night_plan.json", (json.dumps(plan_value, indent=2, sort_keys=True) + "\n").encode()),
                      ("r1_night_sizing.json", (json.dumps(dict(sizing, registration_sha256=registration_sha256),
                                                           indent=2, sort_keys=True) + "\n").encode())):
        path = custody / name
        with path.open("xb") as stream:
            stream.write(raw)
        os.chmod(path, 0o700 if name == "chain.zsh" else 0o600)
        records[name] = {"path": str(path), "sha256": _sha256(raw)}
    return {"plan": records["night_plan.json"], "chain": records["chain.zsh"], "sizing": sizing,
            "registration_sha256": registration_sha256, "plan_id": plan_id}


def check(plan_path, *, probes=None) -> dict:
    """Desk control before t0: the gate's static checks with the real probes, now = t0."""
    plan = night_gate.NightPlan.from_mapping(json.loads(Path(plan_path).read_text()))
    if plan.receipt_class != ROW.receipt_class or plan.ac_powermode not in (None, 0):
        raise R1NightError("not an align_v4_r1 plan (class DIAGNOSTIC_NO_PACK, AC powermode 0)")
    if night_gate.probe_payload_kind(Path(plan.chain_path).read_text()) != KIND:
        raise R1NightError("the plan's chain does not declare the align_v4_r1 payload kind")
    if probes is None:
        from scripts import run_night
        probes = run_night.make_probes()
    probes = replace(probes, now_epoch_s=lambda: plan.t0_epoch_s)
    rows = night_gate._initial_conditions(plan.receipt_class)
    evidence: list = []
    for gate in (night_gate._check_static_start, night_gate._check_chain_identity, night_gate._check_registration):
        refused = gate(plan, probes, rows, evidence)
        if refused is not None:
            return {"verdict": "REFUSED", "refusal": {"reason": refused.refusal.reason,
                                                      "detail": refused.refusal.detail}}
    return {"verdict": "STATIC_PASS", "plan_id": plan.plan_id,
            "conditions": {k: rows[k].status for k in ("C1", "C5")},
            "registration": rows["C1"].measured.get("registration_label"),
            "chain_source_sha256": rows["C5"].measured.get("chain_source_sha256"),
            "t0_local": datetime.fromtimestamp(plan.t0_epoch_s).isoformat(),
            "window_max_s": plan.window_max_s}


def _t0(value: str) -> float:
    try:
        return float(value)
    except ValueError:
        return datetime.fromisoformat(value).timestamp()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    w = sub.add_parser("write")
    w.add_argument("--measurement-root", type=Path, required=True)
    w.add_argument("--custody-root", type=Path, required=True)
    w.add_argument("--t0", required=True, help="epoch seconds or a local ISO time, on a whole minute")
    c = sub.add_parser("check")
    c.add_argument("--plan", type=Path, required=True)
    s = sub.add_parser("size")
    s.add_argument("--measurement-root", type=Path, default=ROOT)
    s.add_argument("--t0", required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "write":
            out = write(args.measurement_root, args.custody_root, _t0(args.t0))
        elif args.command == "size":
            out = size_window(_t0(args.t0), read_registration(args.measurement_root)[0]["sizing"])
        else:
            out = check(args.plan)
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        print(f"write_align_r1_night: refused: {error}", file=sys.stderr)
        return 2
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0 if out.get("verdict", "OK") != "REFUSED" else 3


if __name__ == "__main__":
    raise SystemExit(main())
