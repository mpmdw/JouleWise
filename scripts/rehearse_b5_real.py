#!/usr/bin/env python3
"""Block-5 HAZARD_PACK REAL-model rehearsal rig (shortened; numbers discarded).

NON-CLAIM. Every pack id, plan id, bracket session and attempt id this rig
creates is prefixed ``REH-``; every byte goes under
``/Users/edr/night-archive/gate-prune/rehearsal-real/`` in a fresh measurement
clone with a copied calibration ledger. Nothing here touches the v5_claim
ledger, a claim evidence root, an ops/stop-* branch, launchd or system
settings. The numbers it produces never feed the paper.

Purpose (Ed, 2026-10-06): find faults in the code on the real hardware. It runs
the same path as the mock rig (rehearsal-r1/rehearse_b5_desk.py)

    plan writer -> driver (scripts/run_night.py HAZARD_PACK, in process)
       -> hazard arm (REAL hardware: ioreg, notify, ps/host CPU, statvfs,
          ntp_adjtime, sudo -n powermetrics cadence probe)
       -> lineage, executed inventory, REAL hazard monitor subprocess
       -> chain (zsh) -> reservation, REAL pre/post fiducial captures
          (sudo -n powermetrics, the sudoers rule that already exists),
          run_campaign -> controller -> REAL MLX model + REAL powermetrics
          telemetry per member, NEG-8 prune + derivation, session status
    -> harvest (scripts/harvest_b5_window.py --prepare-desk)

What is still not real, and why (each one is recorded in <base>/overrides.jsonl
whenever it changes an outcome):

  R1 agent census (driver initial/final/in-chain, arm, arm-at-GO): the real
     pgrep runs and its bytes are recorded; the decision sees "clean"
     (agent sessions are alive at the desk; rehearsal-only switch).
  R2 contention and thermal hazard verdicts (arm): the real module measures and
     judges; a non-PASS verdict is recorded and replaced by PASS. Thresholds
     are never edited. The arm dwell is shortened (contention clean_s/cap_s;
     the CPU limit is untouched).
  R3 controller idle admission (CPU/GPU idle, a contention check inside the
     member): the real evaluator runs and is recorded; admitted is forced.
  R4 display: ``pmset displaysleepnow`` is a no-op (the desk display is never
     slept while Ed may be at it), so display_power_state/screensaver fields of
     the real environment probes are forced to the quiet values; the real
     values are recorded. A non-nominal thermal_pressure in those probes is
     thermal (R2-class): recorded, then forced.
  R5 network time OFF: never run (no systemsetup at the desk); the arm's OFF
     action is ``/bin/echo``. G10 (systemsetup ON/OFF) is replaced by a stub.
  R6 courier and durable record: no-ops (no email, no git push).

Reductions: settle_s 0; arm dwell clean_s/cap_s per --dwell-clean-s/--dwell-cap-s;
per collection stage the first K members (see KEEP below).

Usage:
    python3.13 scripts/rehearse_b5_real.py all --pack alpha --base <dir>
"""

from __future__ import annotations

import argparse
import dataclasses
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

RIG_ROOT = Path(__file__).resolve().parents[1]
if str(RIG_ROOT) not in sys.path:
    sys.path.insert(0, str(RIG_ROOT))

ARCHIVE_ROOT = Path("/Users/edr/night-archive/gate-prune/rehearsal-real")
PYTHON = "/opt/homebrew/bin/python3.13"
CANONICAL_VENV_SITE = "/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages"
DESIGN_DIR = Path("/Users/edr/code/JouleWise-wt-ia-claim/configs/campaigns/v5_claim_25g83")
DESIGN_FILES = ("registration_block5.md", "analysis_plan_block5.md", "flag_catalog.json")
LEDGER_392 = Path("/Users/edr/night-custody/measurement/JouleWise-measurement-20261004T0526Z-g2a-b3w1/runs/"
                  "calibration_observation_ledger.jsonl")
PIN_392 = Path("/Users/edr/night-custody/measurement/JouleWise-measurement-20261004T0526Z-g2a-b3w1/configs/"
               "calibration/calibration_ledger_head.json")
B3W1_PLAN = Path("/Users/edr/night-g2a/d117-g2a-prefill-probe-20261004T1305Z/window-plan")
PACKS = {
    "alpha": ("d117_floor_qwen3-1p7b_v5", "ALPHA"),
    "beta": ("d117_floor_qwen3-8b_v5", "BETA"),
    "gamma": ("d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5", "GAMMA"),
}
BYTES_PER_MEMBER = 190_840_832
THRESHOLDS = {
    "clock": {"t_stream_max_s": 335, "h_ms": 3.7, "frequency_margin_ppm": 0.25, "limit_ms": 5.0,
              "skew_max_ns": 1000000, "residual_max_ns": 1000000, "step_ns": 1000000},
    "battery": {"limit_ma": 200, "max_update_age_s": 180, "max_unobserved_s": 120},
    "thermal": {"max_level": 0, "max_gap_s": 15},
    "contention": {"cpu_limit_s_per_s": 0.05, "interval_s": 30, "clean_s": 600, "cap_s": 2700,
                   "window_interval_s": 10, "aggregate_cpu_limit_s_per_s": None},
    "disk": {"planned_bytes": 22710059008, "headroom_bytes": 21474836480, "low_bytes": 10737418240},
    "instrument": {"frames": 300, "bound_s": 55.0, "median_ms_max": 150.0, "max_ms_max": 200.0},
}
# Members kept per collection stage (by config directory basename); default 1.
KEEP_DEFAULT = {
    "neg8_reference_corpus_v5": 1,
    "02_phase_decode_abba_blocks_01_05": 4,       # one complete A/B/B/A block (ALPHA/BETA)
    "01_decode_contrast_blocks_01_05": 4,         # one complete contrast block, both models (GAMMA)
}
NETWORK_TIME_STUB = ("/bin/echo", "REHEARSAL: network time OFF not run (no systemsetup at the desk)")
GIT_ID = ["-c", "user.name=Rehearsal", "-c", "user.email=rehearsal@example.invalid", "-c", "commit.gpgsign=false"]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def log(base: Path, message: str) -> None:
    line = f"{time.strftime('%Y-%m-%dT%H:%M:%S')} {message}"
    print(line, flush=True)
    with open(base / "rig.log", "a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def record_override(kind: str, **fields) -> None:
    path = os.environ.get("JW_REHR_OVERRIDES")
    if not path:
        return
    row = {"at": time.time(), "pid": os.getpid(), "kind": kind, **fields}
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, sort_keys=True, default=str) + "\n")


def git(root: Path, *args: str) -> str:
    completed = subprocess.run(["git", "-C", str(root), *GIT_ID, *args], capture_output=True, text=True)
    if completed.returncode != 0:
        raise RuntimeError(f"git {args} failed: {completed.stderr}")
    return (completed.stdout or "").strip()


# --------------------------------------------------------------------------
# Measurement-process shim (sitecustomize; active only when JW_REHR_SHIM=1)

SITECUSTOMIZE = r'''
# Real-model rehearsal shim (scripts/rehearse_b5_real.py). Active only when JW_REHR_SHIM=1.
import os, sys
_HB = "/opt/homebrew/Cellar/python@3.13/3.13.1/Frameworks/Python.framework/Versions/3.13/lib/python3.13/sitecustomize.py"
if os.path.exists(_HB):
    exec(compile(open(_HB, encoding="utf-8").read(), _HB, "exec"), {"__name__": "_homebrew_sitecustomize"})
if os.environ.get("JW_REHR_SHIM") == "1":
    import json, time

    def _override(kind, **fields):
        path = os.environ.get("JW_REHR_OVERRIDES")
        if not path:
            return
        row = {"at": time.time(), "pid": os.getpid(), "argv0": (sys.argv or [""])[0], "kind": kind, **fields}
        with open(path, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, sort_keys=True, default=str) + "\n")

    try:
        from joulewise import environment as _env
        _orig_snapshot = _env.collect_environment_snapshot
        _orig_guard = _env.collect_environment_guard_observation
        _QUIET = {"display_power_state": "all_asleep", "screensaver_engaged": False}

        def _force(value, where):   # R4: display never slept at the desk; thermal is R2-class
            real = {key: value.get(key) for key in (*_QUIET, "thermal_pressure", "power_source")}
            forced = []
            for key, quiet in _QUIET.items():
                if value.get(key) != quiet:
                    value[key] = quiet
                    forced.append(key)
            if "thermal_pressure" in value and value.get("thermal_pressure") not in (None, "nominal"):
                value["thermal_pressure"] = "nominal"
                forced.append("thermal_pressure")
            if forced:
                value["rehearsal_forced"] = forced
                value["rehearsal_real"] = real
                _override("environment." + where, forced=forced, real=real)
            return value

        def _snapshot(*args, **kwargs):
            return _force(_orig_snapshot(*args, **kwargs), "snapshot")
        _env.collect_environment_snapshot = _snapshot

        def _guard(*args, **kwargs):
            return _force(_orig_guard(*args, **kwargs), "guard")
        _env.collect_environment_guard_observation = _guard

        # R3: the controller's idle admission (CPU criteria), record-and-continue.
        from joulewise import idle_admission as _ia
        _orig_cpu = _ia.evaluate_cpu_idle_admission

        def _cpu(records, criteria, *, gpu_admitted):
            real = _orig_cpu(records, criteria, gpu_admitted=gpu_admitted)
            if real.get("admitted") is True:
                return real
            _override("idle_admission.cpu", gpu_admitted=gpu_admitted, real=real)
            forced = dict(real)
            forced.update(admitted=True, rehearsal_forced="admitted", rehearsal_real_admitted=real.get("admitted"))
            return forced
        _ia.evaluate_cpu_idle_admission = _cpu
        import joulewise.controller as _ctl
        _ctl.evaluate_cpu_idle_admission = _cpu

        # R3b: the GPU half of idle admission (idle_window_suspect), record-and-continue.
        import dataclasses as _dc
        from joulewise.adapters import powermetrics as _pm
        _orig_idle = _pm.PowermetricsTelemetryAdapter.measure_idle

        def _measure_idle(self, config, context=None):
            baseline = _orig_idle(self, config, context)
            if getattr(baseline, "idle_window_suspect", False) is not False:
                _override("idle_admission.gpu", real_idle_window_suspect=baseline.idle_window_suspect,
                          gpu_idle_ratio_mean=getattr(baseline, "gpu_idle_ratio_mean", None),
                          gpu_idle_ratio_min=getattr(baseline, "gpu_idle_ratio_min", None),
                          power_w_mean=getattr(baseline, "power_w_mean", None))
                baseline = _dc.replace(baseline, idle_window_suspect=False)
            return baseline
        _pm.PowermetricsTelemetryAdapter.measure_idle = _measure_idle
    except Exception as _exc:  # noqa: BLE001
        sys.stderr.write(f"rehearsal shim failed: {type(_exc).__name__}: {_exc}\n")
        raise
'''

FAKE_PMSET = r'''#!/bin/sh
# Rehearsal R4: never sleep the desk display; everything else is the real pmset (reads only).
if [ "$1" = "displaysleepnow" ]; then echo "rehearsal: displaysleepnow suppressed"; exit 0; fi
exec /usr/bin/pmset "$@"
'''

RUN_CAMPAIGN_REDUCED = r'''
"""Rehearsal reduction: the real scripts/run_campaign.py with a truncated member list."""
import importlib.util, json, os, sys
from pathlib import Path

script = Path(sys.argv[1])
spec = importlib.util.spec_from_file_location("run_campaign", script)
module = importlib.util.module_from_spec(spec)
sys.modules["run_campaign"] = module
spec.loader.exec_module(module)
_orig = module.apply_order_manifest
KEEP = json.loads(os.environ.get("JW_REHR_KEEP", "{}"))

def apply_order_manifest(configs, order_entries):
    ordered = _orig(configs, order_entries)
    if not ordered:
        return ordered
    directory = Path(ordered[0]).parent
    keep = int(KEEP.get(directory.name, 1))
    kept = list(ordered)[:keep]
    with open(os.environ["JW_REHR_REDUCTION_LOG"], "a", encoding="utf-8") as handle:
        handle.write(json.dumps({"config_dir": str(directory), "listed": len(ordered), "kept": len(kept),
                                 "kept_configs": [Path(p).name for p in kept]}, sort_keys=True) + "\n")
    return kept

module.apply_order_manifest = apply_order_manifest
sys.argv = [str(script), *sys.argv[2:]]
raise SystemExit(module.main())
'''

PYTHON_WRAPPER = r'''#!/bin/sh
# Real-model rehearsal measurement interpreter: the shim, the reduction, then the real venv python.
SHIM="@SHIM@"
export PYTHONPATH="${PYTHONPATH:+$PYTHONPATH:}$SHIM"
export JW_REHR_SHIM=1
export PATH="$SHIM/bin:$PATH"
REAL="$(dirname "$0")/python3.13"
case "$1" in
  */scripts/validate_powermetrics_fiducial.py) exec "$REAL" "$@" --display-arm-binary "$SHIM/bin/pmset";;
  */scripts/run_campaign.py) exec "$REAL" -B "$SHIM/run_campaign_reduced.py" "$@";;
esac
exec "$REAL" "$@"
'''


def write_shims(base: Path) -> Path:
    shim = base / "shim"
    (shim / "bin").mkdir(parents=True, exist_ok=True)
    (shim / "sitecustomize.py").write_text(SITECUSTOMIZE)
    (shim / "run_campaign_reduced.py").write_text(RUN_CAMPAIGN_REDUCED)
    pmset = shim / "bin" / "pmset"
    pmset.write_text(FAKE_PMSET)
    pmset.chmod(0o755)
    return shim


# --------------------------------------------------------------------------
# prepare


def sealed_inventory(measurement: Path) -> dict:
    roots = ["joulewise", "scripts", *(f"configs/campaigns/{pack}" for pack, _ in PACKS.values())]
    listed = git(measurement, "ls-files", "-z", "--", *roots).split("\0")
    files = {path: sha256_file(measurement / path) for path in listed if path}
    catalog = "configs/campaigns/v5_claim_25g83/flag_catalog.json"
    files[catalog] = sha256_file(measurement / catalog)
    return {"schema_version": "joulewise.b5_sealed_inventory.v1", "status": "REHEARSAL_GENERATED",
            "head": None, "files": dict(sorted(files.items())),
            "rehearsal_note": "generated by scripts/rehearse_b5_real.py (non-claim rehearsal)"}


def prepare(pack: str, base: Path, keep: dict) -> None:
    pack_dir, label = PACKS[pack]
    base.mkdir(parents=True, exist_ok=True)
    log(base, f"prepare {pack} at {base}")
    measurement = base / "measurement"
    if measurement.exists():
        raise SystemExit(f"{measurement} exists; use a fresh --base")
    subprocess.run(["git", "clone", "--quiet", "--depth", "1", f"file://{RIG_ROOT}", str(measurement)], check=True)
    code_head = git(measurement, "rev-parse", "HEAD")
    sealed_dir = measurement / "configs/campaigns/v5_claim_25g83"
    for name in DESIGN_FILES:
        shutil.copy2(DESIGN_DIR / name, sealed_dir / name)
    (sealed_dir / "sealed_inventory.json").write_text(json.dumps(sealed_inventory(measurement), indent=2) + "\n")
    git(measurement, "add", "configs/campaigns/v5_claim_25g83")
    git(measurement, "commit", "-q", "-m", "REH real rehearsal H_claim: code head + registration drafts + inventory")
    h_claim = git(measurement, "rev-parse", "HEAD")
    (measurement / "runs").mkdir()
    shutil.copy2(LEDGER_392, measurement / "runs/calibration_observation_ledger.jsonl")
    shutil.copy2(PIN_392, measurement / "configs/calibration/calibration_ledger_head.json")
    git(measurement, "add", "configs/calibration/calibration_ledger_head.json")
    git(measurement, "commit", "-q", "-m", "REH real rehearsal pin-only commit: copied ledger head (row 392)")
    measurement_head = git(measurement, "rev-parse", "HEAD")
    shim = write_shims(base)
    subprocess.run([PYTHON, "-m", "venv", "--without-pip", str(measurement / ".venv")], check=True)
    site = measurement / ".venv/lib/python3.13/site-packages"
    (site / "rehr_canonical_deps.pth").write_text(CANONICAL_VENV_SITE + "\n")
    wrapper = measurement / ".venv/bin/python"
    wrapper.unlink()
    wrapper.write_text(PYTHON_WRAPPER.replace("@SHIM@", str(shim)))
    wrapper.chmod(0o755)
    inputs_dir = base / "inputs"
    inputs_dir.mkdir()
    for name in ("identity-epoch.json", "t1-bindings.json"):
        shutil.copy2(B3W1_PLAN / name, inputs_dir / name)
    runs_parent = base / "runs-parent"
    runs_parent.mkdir()
    sizing = "configs/campaigns/v5_claim_25g83/sizing_b5.json"
    sizing_value = json.loads((measurement / sizing).read_text())
    sizing_digest = sha256_file(measurement / sizing)
    t0 = (int(time.time()) // 60) * 60
    tag = f"REH-real-{pack}-{time.strftime('%Y%m%dT%H%MZ', time.gmtime(t0))}"
    inputs = {
        "schema": "joulewise.b5_window_plan_inputs.v2",
        "plan_id": tag, "attempt": 1,
        "pack_root": str(measurement / "configs/campaigns" / pack_dir),
        "measurement_root": str(measurement), "measurement_head": h_claim, "repo_head": code_head,
        "custody_root": str(base / "custody"), "runs_parent": str(runs_parent),
        "claim_backup_destination": str(base / "backup-claim"),
        "bound_backup_destination": str(base / "backup-bound"),
        "bracket_session_id": f"{tag}-calibration", "pre_attempt_id": f"{tag}-cal-pre",
        "post_attempt_id": f"{tag}-cal-post",
        "identity_epoch_json": {"path": str(inputs_dir / "identity-epoch.json"),
                                "sha256": sha256_file(inputs_dir / "identity-epoch.json")},
        "t1_bindings_json": {"path": str(inputs_dir / "t1-bindings.json"),
                             "sha256": sha256_file(inputs_dir / "t1-bindings.json")},
        "t0_epoch_s": t0,
        "programmed_span_s": {"seconds": sizing_value["packs"][label]["programmed_span_s"],
                              "source": {"path": sizing, "sha256": sizing_digest},
                              "source_pointer": f"/packs/{label}/programmed_span_s"},
        "T_stream_max_s": {"seconds": sizing_value["packs"][label]["T_stream_max_s"],
                           "source": {"path": sizing, "sha256": sizing_digest},
                           "source_pointer": f"/packs/{label}/T_stream_max_s"},
        "bytes_per_member": BYTES_PER_MEMBER,
        "thresholds": json.loads(json.dumps(THRESHOLDS)),
        "g10": pack == "alpha",
        "registration": {"path": "configs/campaigns/v5_claim_25g83/registration_block5.md",
                         "sha256": sha256_file(sealed_dir / "registration_block5.md")},
    }
    (inputs_dir / "plan-inputs.json").write_text(json.dumps(inputs, indent=2) + "\n")
    sys.path.insert(0, str(measurement))
    from joulewise.b5 import plan as b5_plan
    record = b5_plan.write_window_plan(inputs, settle_s=0)
    (base / "plan-record.json").write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    state = {"pack": pack, "pack_dir": pack_dir, "measurement": str(measurement), "h_claim": h_claim,
             "measurement_head": measurement_head, "code_head": code_head, "shim": str(shim),
             "plan": record["plan"]["path"], "custody": str(base / "custody"), "t0": t0, "keep": keep,
             "tag": tag}
    (base / "state.json").write_text(json.dumps(state, indent=2) + "\n")
    log(base, f"prepared: plan={record['plan']['path']} members={record['member_count']} "
              f"window_max_s={record['window_max_s']} pack_sha256={record['pack_sha256']} "
              f"pack_digest_error={record['pack_digest_error']}")


# --------------------------------------------------------------------------
# run (the driver, in process)


def load_run_night():
    spec = importlib.util.spec_from_file_location("run_night_rehearsal", RIG_ROOT / "scripts/run_night.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def install_driver_overrides(dwell_clean_s: float, dwell_cap_s: float) -> dict:
    """R1, R2, R5 in the driver process. Returns the call counters."""

    from joulewise.b5 import driver as hazard_driver
    from joulewise.hazards import arm as hazard_arm, base as hazard_base, contention, thermal

    calls = {"census_real": 0, "census_overridden": 0, "judge_overridden": 0, "arm": 0}

    real_census = hazard_arm.agent_census

    def census(ctx):                                            # R1 (arm, arm-at-GO)
        result = real_census(ctx)
        calls["census_real"] += 1
        if result.get("clean"):
            return result
        calls["census_overridden"] += 1
        record_override("census.arm", returncode=result.get("returncode"), stdout=result.get("stdout"),
                        detail=result.get("detail"))
        return dict(result, clean=True, rehearsal_real_clean=False,
                    detail="REHEARSAL record-and-continue; real: " + str(result.get("detail")))
    hazard_arm.agent_census = census

    for module in (contention, thermal):                        # R2
        real_judge = module.judge

        def judged(measurement, thresholds, _real=real_judge, _name=module.__name__):
            verdict = _real(measurement, thresholds)
            if verdict.passed:
                record_override("judge.pass", module=_name, observed=verdict.observed)
                return verdict
            calls["judge_overridden"] += 1
            record_override("judge.override", module=_name, status=verdict.status,
                            reasons=list(verdict.reasons), observed=verdict.observed)
            observed = dict(verdict.observed or {})
            observed.update(rehearsal_real_status=verdict.status, rehearsal_real_reasons=list(verdict.reasons))
            return hazard_base.Verdict(verdict.module, hazard_base.PASS,
                                       ("REHEARSAL record-and-continue; real " + verdict.status + ": "
                                        + "; ".join(verdict.reasons),),
                                       verdict.thresholds, observed)
        module.judge = judged

    real_arm_run = hazard_arm.run

    def arm_run(config, seams=None):                            # R5 + dwell reduction
        calls["arm"] += 1
        thresholds = json.loads(json.dumps(config.thresholds))
        original = dict(thresholds["contention"])
        thresholds["contention"]["clean_s"] = dwell_clean_s
        thresholds["contention"]["cap_s"] = dwell_cap_s
        record_override("arm.reduction", contention_original=original,
                        contention_used=thresholds["contention"], network_time_off_argv=list(NETWORK_TIME_STUB))
        config = dataclasses.replace(config, thresholds=thresholds, network_time_off_argv=NETWORK_TIME_STUB)
        return real_arm_run(config, seams)
    hazard_arm.run = arm_run
    hazard_driver.NETWORK_TIME_OFF_ARGV = NETWORK_TIME_STUB
    return calls


def run(pack: str, base: Path, dwell_clean_s: float, dwell_cap_s: float) -> int:
    state = json.loads((base / "state.json").read_text())
    log(base, f"run {pack}: plan {state['plan']}")
    os.environ.update({
        "JW_REHR_SHIM": "0",   # the driver process is not shimmed; its children set 1 via the venv wrapper
        "JW_REHR_OVERRIDES": str(base / "overrides.jsonl"),
        "JW_REHR_REDUCTION_LOG": str(base / "reduction.jsonl"),
        "JW_REHR_KEEP": json.dumps(state["keep"]),
    })
    from joulewise import night_gate
    from joulewise.b5 import driver as hazard_driver

    calls = install_driver_overrides(dwell_clean_s, dwell_cap_s)
    driver = load_run_night()
    real_probes = driver.make_probes()
    calls.update(driver_census=0, driver_census_overridden=0, courier=0, durable_record=0)

    def probe_run(argv):                                        # R1 (driver)
        result = real_probes.run(argv)
        if tuple(argv) != night_gate.AGENT_CENSUS_ARGV:
            return result
        calls["driver_census"] += 1
        if result.exit_code == 1 and result.stdout == "":
            return result
        calls["driver_census_overridden"] += 1
        record_override("census.driver", exit_code=result.exit_code, stdout=result.stdout, stderr=result.stderr)
        return night_gate.ProbeResult(tuple(argv), 1, "", "", result.monotonic_ns)

    driver.make_probes = lambda: night_gate.Probes(
        run=probe_run, now_epoch_s=time.time, monotonic_ns=time.monotonic_ns,
        read_text=lambda path: Path(path).read_text(encoding="utf-8"),
        checkout_head=real_probes.checkout_head, measurement_head=real_probes.measurement_head)

    def durable_record(*_args, **_kwargs):                      # R6
        calls["durable_record"] += 1

    def run_courier(*_args, **_kwargs):                         # R6
        calls["courier"] += 1
        return {"attempted": 1, "sent": True, "heartbeat_seen": True, "last_error": None}

    driver._durable_record = durable_record
    driver.run_courier = run_courier
    driver._resolve_courier_bin = lambda _bin: (Path("/usr/bin/true"), None, None)

    seams = hazard_driver.production_seams(RIG_ROOT)
    g10_source = ("import json, pathlib, sys; night = pathlib.Path(sys.argv[1]); "
                  "(night / 'g10.json').write_text(json.dumps({'result': 'REHEARSAL_STUB', "
                  "'note': 'G10 runs systemsetup; never at the desk'}))")
    seams.g10_argv = lambda night, _t: [sys.executable, "-c", g10_source, str(night)]   # R5
    driver._hazard_seams = lambda: seams
    started = time.time()
    code = driver.run_night(Path(state["plan"]))
    log(base, f"driver exit {code} after {time.time() - started:.0f} s; calls={calls}")
    (base / "run-result.json").write_text(json.dumps({"exit_code": code, "calls": calls,
                                                      "elapsed_s": time.time() - started}, indent=2) + "\n")
    return code


# --------------------------------------------------------------------------
# harvest


def harvest(pack: str, base: Path) -> int:
    state = json.loads((base / "state.json").read_text())
    measurement = Path(state["measurement"])
    env = dict(os.environ)
    env.update({"JW_REHR_SHIM": "1", "PYTHONPATH": f"{RIG_ROOT}:{state['shim']}",
                "JW_REHR_OVERRIDES": str(base / "overrides.jsonl"),
                "PATH": f"{state['shim']}/bin:{env.get('PATH', '')}"})
    argv = [str(measurement / ".venv/bin/python3.13"), "-B", str(RIG_ROOT / "scripts/harvest_b5_window.py"),
            "--plan", state["plan"], "--archive-root", str(base / "archive"), "--prepare-desk"]
    log(base, "harvest: " + " ".join(argv))
    completed = subprocess.run(argv, capture_output=True, text=True, env=env, cwd=str(RIG_ROOT))
    (base / "harvest.stdout").write_text(completed.stdout)
    (base / "harvest.stderr").write_text(completed.stderr)
    log(base, f"harvest exit {completed.returncode}: {completed.stdout.strip()[:2000]}")
    return completed.returncode


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("step", choices=("prepare", "run", "harvest", "all"))
    parser.add_argument("--pack", choices=sorted(PACKS), required=True)
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--keep", default="{}", help="JSON {config_dir_basename: members} merged over the defaults")
    parser.add_argument("--dwell-clean-s", type=float, default=60.0)
    parser.add_argument("--dwell-cap-s", type=float, default=120.0)
    args = parser.parse_args(argv)
    base = args.base.resolve()
    if not str(base).startswith(str(ARCHIVE_ROOT) + "/"):
        raise SystemExit(f"--base must be under {ARCHIVE_ROOT} (non-claim rehearsal root)")
    base.mkdir(parents=True, exist_ok=True)
    keep = {**KEEP_DEFAULT, **json.loads(args.keep)}
    if args.step in ("prepare", "all"):
        prepare(args.pack, base, keep)
    if args.step in ("run", "all"):
        run(args.pack, base, args.dwell_clean_s, args.dwell_cap_s)
    if args.step in ("harvest", "all"):
        return harvest(args.pack, base)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
