"""Author an R1-only HAZARD_PACK; reuse the night installer and driver."""
from __future__ import annotations

import hashlib
from datetime import datetime, timedelta
import json
import math
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import time
from zoneinfo import ZoneInfo

from joulewise.b5 import chain, plan as b5_plan
from joulewise.b6.plan_inputs import CLOCK_THRESHOLDS
from joulewise.hazards.arm import default_thresholds
from joulewise.night_gate import NightPlan


KIT = Path("configs/campaigns/align_v4")
# origin/main RUN_STATE items 215-216 supersede the runtime's display-only
# total: R6-2 retries plus corrected step-D/batch encounter, rounded up.
R1_RETRY_FLOOR_S = 96_427
# Reuse the existing stage wall budgets, rather than timing a happy path.
BOOKEND_S = chain.STAGE_WALL_BUDGET_S["pre_calibration_capture"]  # 1,800 s each
CLOSE_S = chain.STAGE_WALL_BUDGET_S["session_status_record"]  # 600 s teardown allowance each
HARVEST_S = CLOSE_S  # one existing session-status budget for final manifest/result writes
# The arm itself is inside run_night's t0-based deadline too (not extra time
# before it). Its existing cap must therefore be added, as must both bookends.
BASE_WINDOW_S = R1_RETRY_FLOOR_S + b5_plan.T0_STAGE_CAP_S + 2 * (BOOKEND_S + CLOSE_S) + HARVEST_S
BATCH_ENCOUNTER_S = 11_164  # RUN_STATE item 216; the floor includes the first encounter
DISPLAY_DWELL_S = 300  # R0-L3 / RUN_STATE items 206, 209: re-run 11 passing dwell
ARM_NOTICE_S = 15 * 60  # R1-ARM-FIX-1: choose t0 at least 15 minutes ahead
BATCH_ZONE = ZoneInfo("America/Los_Angeles")  # R1 ruling 8 local batch clock
CHAIN_SOURCE = Path("scripts/night_chains/align_r1_rehearsal.zsh")


def crossing_size(t0, base_s):
    """Item 216 fixed point, counting local 11:45 in the half-open window.

    The daily encounter adds less than even a DST-shortened day, so this
    monotone iteration converges without an arbitrary iteration limit.
    """
    window_s = base_s
    while True:
        day = datetime.fromtimestamp(t0, BATCH_ZONE).date()
        crossings = []
        while True:
            epoch = datetime(day.year, day.month, day.day, 11, 45, tzinfo=BATCH_ZONE).timestamp()
            if epoch >= t0 + window_s:
                break
            if epoch >= t0:
                crossings.append(epoch)
            day += timedelta(days=1)
        extra = max(0, len(crossings) - 1)
        wanted = base_s + extra * BATCH_ENCOUNTER_S
        if wanted == window_s:
            return {"base_s": base_s, "batch_crossings_epoch_s": crossings,
                    "batch_window_crossings": len(crossings), "extra_batch_encounters": extra,
                    "batch_encounter_s": BATCH_ENCOUNTER_S, "extra_batch_s": extra * BATCH_ENCOUNTER_S,
                    "window_max_s": window_s}
        window_s = wanted


def size_window(t0):
    terms = {"r1_retry_floor_s": R1_RETRY_FLOOR_S, "hazard_arm_s": b5_plan.T0_STAGE_CAP_S,
             "bookends_s": 2 * BOOKEND_S, "close_s": 2 * CLOSE_S, "harvest_s": HARVEST_S,
             "display_dwell_s": DISPLAY_DWELL_S}
    # No extra meter allowance: the existing hazard driver supervises it,
    # including startup/close, within the unchanged arm/close budgets above.
    return dict(crossing_size(t0, sum(terms.values())), base_terms_s=terms)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    path = Path(path)
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write("\n")


def prepare(measurement_root, custody_root, t0, *, planned_bytes=0, now=None):
    """Create a fresh plan without executing a probe, chain or launchctl."""
    from scripts import align_r1_rehearsal as r1, run_night

    measurement = Path(measurement_root).expanduser().resolve(strict=True)
    custody = Path(custody_root).expanduser().resolve()
    clock = time.time() if now is None else now
    if t0 < clock + ARM_NOTICE_S:
        raise ValueError("t0 must leave at least 15 minutes for the arm notice")
    sizing = size_window(t0)
    head = subprocess.check_output(["git", "-C", str(measurement), "rev-parse", "HEAD"], text=True).strip()
    config = json.loads((measurement / "configs/align/v4/r1_runtime.json").read_text())
    # Longest single segment (not the whole night): a continuous sampler can
    # cover the member's startup, G0, quiet/preheat, decode, recovery and close.
    stream_s = math.ceil(max(r1.segment_bounds(config["g0_timeout_s"], config["step"]["deadman_s"]).values()))
    thresholds = default_thresholds()  # six existing physical modules; no new tolerances
    # Same hold as ALIGN pilots through bytes_h_session -> b6.plan_inputs
    # (block-6 registration S-7): 5 ms / stream - 0.25 ppm, h=0 at arm;
    # placement is judged from each run's own fit. B5's superseded 3.7 ms
    # placement term plus even ZERO rate would be 5.141 ms at 5,764 s and
    # would refuse every R1. Reuse the pilot rule, not a new tolerance.
    thresholds["clock"].update(CLOCK_THRESHOLDS)
    thresholds["clock"]["t_stream_max_s"] = stream_s
    # Zero means no footprint estimate was supplied. Keep the shared 20 GiB
    # arm headroom and 10 GiB live floor, and disclose the unsized allocation.
    thresholds["disk"]["planned_bytes"] = planned_bytes
    plan_id = "align-r1-" + time.strftime("%Y%m%dT%H%MZ", time.gmtime(t0))
    pack = custody / "align-r1-runtime"
    # R1 has no W1 members. Give the shared lineage reader an honest inventory
    # of this route's actual inputs, rather than the pending W1 plan tree
    # (which has no identity_pin_projection and is refused by that reader).
    inventory = [Path("configs/align/v4/r1_runtime.json"),
                 KIT / "registration/inputs.json",
                 *[Path(p) for p in config["templates"].values()]]
    tree = {"non_claim": True, "plan": {"plan_id": plan_id},
            "arm_attachments": {"identity_pin_projection": {"identity_units": [{
                "config_inventory": [{"path": p.as_posix(), "sha256": digest(measurement / p)}
                                     for p in inventory]}]}}}
    tree_raw = (json.dumps(tree, indent=2, sort_keys=True) + "\n").encode()
    claim, bound = custody / "runs", custody / "bound"
    bindings = {
        "repo_root": str(measurement),
        "ledger_path": str(measurement / "runs/calibration_observation_ledger.jsonl"),
        "claim_runs_root": str(claim), "bound_runs_root": str(bound),
        "operator_log_root": str(custody / "operator-logs"),
        "pre_calibration_dir": str(custody / "bookends/pre"),
        "post_calibration_dir": str(custody / "bookends/post"),
        # No backup is performed here. All targets are on the same internal
        # volume; the driver's existing disk target accounting stays in use.
        "claim_backup_destination": str(custody), "bound_backup_destination": str(custody),
        "bracket_session_id": plan_id, "pre_attempt_id": plan_id + "-pre",
        "post_attempt_id": plan_id + "-post",
        "identity_epoch_json": str(custody / "not-applicable.identity-epoch.json"),
        "t1_bindings_json": str(custody / "not-applicable.t1-bindings.json"),
    }
    wrapper = wrapper_bytes(measurement, custody)
    window = {
        "schema": "joulewise.hazard_window.v1", "attempt": 1,
        # This inventory is R1-only; no W1 stage graph is launched.
        "pack": {"pack_id": pack.name, "pack_root": str(pack), "pack_sha256": None,
                 "plan_tree_sha256": hashlib.sha256(tree_raw).hexdigest(),
                 "pack_plan_id": tree["plan"]["plan_id"], "window_id": plan_id,
                 "evidence_root_id": plan_id},
        "bracket_session_id": plan_id, "bindings": bindings,
        "runs_roots": {"claim": str(claim), "bound": str(bound)},
        "T_stream_max_s": stream_s, "planned_bytes": planned_bytes,
        # R1 is one chain, with no W1 campaign members or yield denominator.
        "member_count": 0, "thresholds": thresholds, "g10": False,
        "programmed_span_s": R1_RETRY_FLOOR_S, "t0_stage_cap_s": b5_plan.T0_STAGE_CAP_S,
        "settle_s": 0,  # the hazard arm dwells; R1 owns its soak and releases
        "window_env": {"path": str(custody / "window.env"), "sha256": hashlib.sha256(b"").hexdigest()},
        "registration": None,
        "chain_deviations": ["R1 single chain; no W1 members, reservation, G10 or W1 harvest",
                             "Independent diagnostic calibration bookends; no claim-eligible paired bracket"],
        "disk_volumes": [str(custody)],
        "stages": [{"stage_id": "align-r1", "kind": "r1_rehearsal", "ordinal": 1,
                    "expected_count": 0, "in_chain": True}],
    }
    mapping = {
        "schema": "joulewise.night_plan.v5", "schema_version": 5,
        "plan_id": plan_id, "receipt_class": "HAZARD_PACK", "ac_powermode": 0,
        "t0_epoch_s": t0, "window_max_s": sizing["window_max_s"], "authored_epoch_s": clock,
        "repo_head": head, "measurement_root": str(measurement), "measurement_head": head,
        "chain_path": str(custody / "chain.zsh"), "chain_sha256_path": str(custody / "chain.zsh.sha256"),
        "custody_root": str(custody), "registration_path": None, "hazard_window": window,
    }
    plan = NightPlan.from_mapping(mapping)
    scheduling = run_night.schedule(plan)
    # Preparation errors concern executable instructions, not new measurement
    # refusals. The shared installer enforces its own cutoff again at install.
    if clock >= scheduling["install_close_epoch_s"]:
        raise ValueError("t0 leaves no shared installer handback interval; choose a later whole minute")
    custody.mkdir(parents=True, exist_ok=False)
    pack.mkdir()
    (pack / "plan_tree.json").write_bytes(tree_raw)
    for relative in inventory:
        target = pack / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(measurement / relative, target)
    claim.mkdir()
    bound.mkdir()
    (custody / "window.env").write_bytes(b"")
    (custody / "chain.zsh").write_bytes(wrapper)
    (custody / "chain.zsh.sha256").write_bytes(chain.sidecar_bytes(wrapper, "chain.zsh"))
    write(custody / "night_plan.json", mapping)
    record = {"schema": "joulewise.align.r1_arm.v1", "plan": str(custody / "night_plan.json"),
              "plan_sha256": digest(custody / "night_plan.json"), "schedule": scheduling,
              "window_max_s": sizing["window_max_s"], "derivation": sizing,
              "flags": (["disk.allocation_unsized; shared headroom and live disk floor remain"] if not planned_bytes else [])}
    write(custody / "arm.json", record)
    return record


def wrapper_bytes(measurement, custody):
    q = shlex.quote
    script = q(str(Path(measurement) / "scripts/arm_align_r1.py"))
    source = Path(measurement) / CHAIN_SOURCE
    source_sha256 = digest(source)
    # Do not exec: a successful chain is followed by the post bookend. On a
    # signal the whole group receives TERM, and no fresh bookend is started.
    # The original chain and driver retain their power restore traps/lock.
    return ("#!/bin/zsh -f\nset -u\ntrap 'exit 130' HUP INT TERM\n"
            ': "${NIGHT_DIR:?}" "${MEASUREMENT_ROOT:?}" "${PY:?}"\n'
            # Literal, not a mutable sidecar/environment pin. Do this before
            # display sleep, dwell, bookends or the R1 chain (agreement D5).
            f'actual="$(/usr/bin/shasum -a 256 {q(str(source))} 2>/dev/null)"\n'
            f'if [[ "${{actual%% *}}" != {q(source_sha256)} ]]; then\n'
            '  print -u2 -- "R1 chain source changed; refusing before wrapper work"\n'
            '  exit 65\nfi\n'
            f'"$PY" -B {script} _display-dwell --custody-root {q(str(custody))} || exit $?\n'
            f'"$PY" -B {script} _bookend --custody-root {q(str(custody))} --slot pre\n'
            f'/bin/zsh -f {q(str(source))}\n'
            'r1_rc=$?\n'
            f'"$PY" -B {script} _bookend --custody-root {q(str(custody))} --slot post\n'
            'exit "$r1_rc"\n').encode()


def display_dwell(custody_root, *, run=subprocess.run, sleep=time.sleep, now=time.time):
    """R0-L3 display preparation, with failure recorded as a non-veto flag."""
    record = Path(custody_root) / "night/r1_wrapper.jsonl"
    def note(event, **fields):
        with record.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(dict(event=event, epoch_s=now(), **fields), sort_keys=True) + "\n")
    try:
        rc = run(["/usr/bin/pmset", "displaysleepnow"], check=False).returncode
        note("displaysleepnow", exit_code=rc, flag=None if rc == 0 else "r1.display_sleep_failed")
    except OSError as error:
        note("displaysleepnow", error=str(error), flag="r1.display_sleep_failed")
    note("dwell_start", dwell_s=DISPLAY_DWELL_S)
    sleep(DISPLAY_DWELL_S)
    note("dwell_end", dwell_s=DISPLAY_DWELL_S)
    return 0


def bookend(custody_root, slot, *, run=subprocess.run):
    """Independent D-109 diagnostic capture; a failure is recorded, never a veto.

    R1 can exceed the claim bracket's 24 h horizon. Do not pretend that a W1
    reservation or claim calibration covers this night, or truncate R1 to it.
    """
    custody = Path(custody_root)
    plan = json.loads((custody / "night_plan.json").read_text())
    measurement = Path(plan["measurement_root"])
    command = [sys.executable, "-B", str(measurement / "scripts/validate_powermetrics_fiducial.py"),
               "--allow-live", "--power-policy", "ac_automatic", "--sleep-display-before-capture",
               "--output-root", str(custody / "bookends" / slot)]
    argv = [sys.executable, "-B", "-c", chain.BUDGET_HELPER, str(BOOKEND_S),
            str(chain.BUDGET_GRACE_S), str(chain.BUDGET_EXPIRED_RC), "--", *command]
    directory = custody / "bookends"
    directory.mkdir(exist_ok=True)
    with (directory / (slot + ".stdout")).open("x") as stdout, \
            (directory / (slot + ".stderr")).open("x") as stderr:
        result = run(argv, stdout=stdout, stderr=stderr, check=False)
    write(directory / (slot + ".json"), {"slot": slot, "argv": command, "exit_code": result.returncode,
                                       "flag": None if result.returncode == 0 else "r1.bookend_failed"})
    return 0


def installer_argv(custody_root, *, uninstall=False, render_only=None):
    plan_path = Path(custody_root).resolve() / "night_plan.json"
    plan = json.loads(plan_path.read_text())
    measurement = Path(plan["measurement_root"])
    argv = [str(measurement / "scripts/install_night_agent.sh"), "--plan", str(plan_path),
            "--python", str(measurement / ".venv/bin/python"),
            "--courier-bin", str(measurement / "scripts/b6_courier.sh")]
    if uninstall:
        argv.append("--uninstall")
    if render_only is not None:
        argv += ["--render-only", str(Path(render_only).resolve())]
    return argv
