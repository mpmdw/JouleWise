"""R12 scheduler of the pinned loop and its real production lane adapters.

This is generator code. It never constructs a lane result or edits session
records. Scheduling, clocks, machine observations and installer return values
are inputs; every transition and attempt is written by the pinned loop.
"""
from __future__ import annotations

import json
from pathlib import Path


def seed_calibration(root, clock, sources, source):
    """Obtain the initial ledger through a pinned reduced driver, not a fixture record."""
    import datetime as dt
    import hashlib
    from joulewise.b5 import plan
    from joulewise.b6 import smoke, plan_inputs
    from scripts.write_derivation_night_inputs import _derive_planned_vectors
    from scripts.run_night import run_night
    ledger = source / plan.DEFAULT_LEDGER_RELATIVE
    if ledger.exists() and ledger.stat().st_size:
        return
    ledger.parent.mkdir(parents=True, exist_ok=True)
    ledger.touch()
    identities = {}
    epoch, t1 = _derive_planned_vectors(plan.POWER_POLICY)
    for name, value in (("identity-epoch.json", epoch), ("t1-bindings.json", t1)):
        path = root / "inputs" / name
        path.write_text(json.dumps(value, sort_keys=True) + "\n")
        identities[name] = {"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    parent = root / "seed-inputs"
    (parent / "runs").mkdir(parents=True)
    inputs = plan_inputs.build(source, source / "configs/b6/registration", "d117_floor_qwen3-1p7b_v5",
        "R12-seed", identities, custody_root=parent / "custody", runs_parent=parent / "runs",
        claim_backup=parent / "backup-claim", bound_backup=parent / "backup-bound", run=sources.subprocess_run)
    tree = json.loads((source / "configs/campaigns/d117_floor_qwen3-1p7b_v5/plan_tree.json").read_text())
    first = next(row for row in tree["stage_graph"] if row["kind"] == "campaign_collection")
    head = sources.subprocess_run(["git", "-C", str(source), "rev-parse", "HEAD"], capture_output=True,
                                   text=True, check=True).stdout.strip()
    seed = smoke.prepare("d117_floor_qwen3-1p7b_v5", head, source, root / "prerequisite",
        plan_inputs=inputs, fp={}, state_root=root / "seed-state", now=dt.datetime.now(dt.timezone.utc),
        run=sources.subprocess_run, defer_plan=True, keep={first["stage_id"]: 1})
    seed_inputs = json.loads((seed.smoke_dir / "smoke-state.json").read_text())["plan_inputs"]
    seed_inputs["t0_epoch_s"] = 60 * ((int(clock.time()) + 479) // 60)
    record = plan.write_window_plan(seed_inputs, now=clock.time)
    clock.sleep(seed_inputs["t0_epoch_s"] - clock.time())
    rc = run_night(Path(record["plan"]["path"]))
    print("prerequisite_driver", rc, flush=True)
    if rc not in (0, 6):
        raise RuntimeError("prerequisite chain did not finish")
    plan.advance_ledger_pin(seed.measurement, session_id=seed.bracket_session_id,
        operator_identity="R12 synthetic prerequisite", attestation_reason="real synthetic prerequisite ended")
    # The pinned copier supplies a prior ledger input to the new source
    # checkout. Source capture bytes stay untouched at their original paths.
    copied = smoke.copy_ledger(seed.measurement, source, root)
    sources.subprocess_run(["git", "-C", str(source), "add", plan.HEAD_PIN_RELATIVE], check=True)
    sources.subprocess_run(["git", "-C", str(source), "-c", "commit.gpgsign=false", "commit", "-qm",
                           "Import chain-written synthetic prerequisite pin"], check=True)
    (root / "seed-receipt.json").write_text(json.dumps({"driver_rc": rc,
        "smoke": seed.to_json(), "copied_input_paths": list(copied)}, indent=2) + "\n")


def loop_fixture(root, clock, pack="alpha"):
    from runtime import install_sources, source_root
    from joulewise.b6.loop import Loop
    from joulewise.b6 import precheck
    from joulewise.b6.lanes import Lanes
    from joulewise.b6.precheck_lane import PrecheckLane
    from joulewise.b6.driver_lane import DriverLane
    from joulewise.b6.desk_lane import DeskLane
    from joulewise.b6.analysis_lane import AnalysisLane, HarvestLane
    from joulewise.b6.pack_registration import open_packs
    from joulewise.hazards.base import Context

    source = source_root(root)
    sources = install_sources(root, clock)
    def run(argv, **kwargs):
        return sources.subprocess_run(argv, **{"capture_output": True, "text": True, **kwargs})
    seed_calibration(root, clock, sources, source)
    loop_root = root / "loop"
    config = json.loads((source / "configs/b6/loop.json").read_text())
    config.update(loop_root=str(loop_root), base_order=[pack], wake_argv=[])
    rejected = []
    regs = {reg.pack_id: reg for reg in open_packs(source, run=run,
                                                rejected=lambda path, reasons: rejected.append([path, reasons]))
            if reg.pack_id == pack}
    if not regs:
        raise ValueError("no open synthetic registration: " + repr(rejected))
    seams = precheck.Seams(frequency_reader=sources.frequency_reader,
        stat=sources.stat, statvfs=sources.statvfs, host_reader=sources.host_reader,
        smc_read=None, orphan_collect=lambda: [])
    lanes = Lanes(
        PrecheckLane(source, loop_root, run, block_root=root, seams=seams,
                     context_factory=lambda out: Context(run=sources.run, clocks=clock, raw_dir=out.parent / "raw")),
        DriverLane(source, loop_root, run, config=config, clock=clock.time,
                   block_root=root, group_alive=lambda pgid: False),
        DeskLane(source, loop_root, run), HarvestLane(), AnalysisLane())
    loop = Loop(source, loop_root, config=config, regs=regs, lanes=lanes,
                clock=clock.time, run=run)
    scheduled = set()
    for tick in range(80):
        loop.tick()
        state = loop.read_state()
        print("loop", tick, state["state"], flush=True)
        if state["state"] in {"HOLD_LOOP", "DONE"}:
            return 0 if state["state"] == "DONE" else 2
        if state.get("attempts"):
            return 0
        session = state.get("session") or {}
        prefix = "smoke_" if state["state"] == "SMOKE_RUN" else ""
        prepared = session.get(prefix + "prepared")
        if prepared and session.get(prefix + "handle") and prepared["plan_path"] not in scheduled:
            from scripts.run_night import run_night
            plan_path = Path(prepared["plan_path"])
            plan = json.loads(plan_path.read_text())
            scheduled.add(str(plan_path))
            clock.sleep(max(0, plan["t0_epoch_s"] - clock.time()))
            code = run_night(plan_path)
            print("scheduled_driver", code, str(plan_path), flush=True)
        if state["state"] == "ARM_WAIT":
            clock.sleep(max(0, session["notice_sent"] + 1800 - clock.time()))
        if state["state"] == "WAIT_PHYSICS":
            return 3
    raise RuntimeError("development tick bound reached")
