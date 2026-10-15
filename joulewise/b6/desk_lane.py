"""The one harvest path, followed by structure checks and verified compression."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import time

from joulewise import desk_compress, session_structure
from joulewise.b5 import chain, plan
from joulewise.b6 import smoke
from joulewise.b6.driver_lane import metadata_path, read, write
from joulewise.b6.lanes import SessionLine, SmokeResult
from joulewise.flags.catalog import load_catalog


# The loop's production runner (scripts/b6_loop.py live_run) gives every call
# without its own timeout 120 s, which would kill a session harvest (about 45
# minutes for a block-5-sized session) and record it as a program fault.
HARVEST_TIMEOUT_S = 4 * 3600


class DeskLane:
    def __init__(self, measurement, loop_root, run=subprocess.run, *, env=None):
        self.measurement, self.root, self.run = Path(measurement), Path(loop_root), run
        self.env = env

    def _advance(self, metadata):
        measurement = Path(metadata["paths"]["measurement"])
        session_id = metadata["inputs"]["bracket_session_id"]
        flags = []
        if metadata.get("lost") and not metadata.get("bracket_aborted"):
            # The job is gone with no terminal record (driver_lane.status), so
            # nothing will ever close this session's bracket. Close it as an
            # abort (the ledger keeps every partial receipt), so the pin can
            # advance and the next session's plan can reserve the ledger.
            from joulewise import calibration_ledger
            try:
                calibration_ledger.abort_bracket_session(measurement / plan.DEFAULT_LEDGER_RELATIVE,
                    session_id=session_id, reason="b6_chain_lost_no_terminal")
                metadata["bracket_aborted"] = True
                flags.append("records.terminal_record_absent")
            except Exception as exc:
                metadata["bracket_abort"] = {"status": "FAILED", "error": type(exc).__name__}
        elif not metadata.get("lost"):
            # A stopped chain may leave either slot open. Complete custody
            # must use the recovery CLI's authenticated refit and screen;
            # every remaining partial receipt is retained by the abort.
            from joulewise import calibration_ledger
            try:
                status = plan.ledger_head_status(measurement)
                resumed = set()
                while session_id in status["open_sessions"]:
                    slot = (status.get("open_session_next_slots") or {}).get(session_id) or {}
                    name = slot.get("next_slot")
                    if slot.get("custody_state") != "complete" or name in resumed:
                        break
                    resumed.add(name)
                    try:
                        night_plan = read(metadata["prepared"]["plan_path"])
                        hazard = night_plan["hazard_window"]
                        tree = read(Path(hazard["pack"]["pack_root"]) / "plan_tree.json")
                        reservation = next(s for s in chain.stage_plan(tree) if s.kind == "bracket_reservation")
                        argv = chain.stage_argv(reservation, hazard["bindings"], tree, measurement)
                        frozen_plan = argv[argv.index("--plan") + 1]
                        result = self.run([str(measurement / ".venv/bin/python"),
                            str(measurement / "scripts/recover_calibration_ledger.py"),
                            "--ledger", str(measurement / plan.DEFAULT_LEDGER_RELATIVE),
                            "--head-pin", str(measurement / plan.HEAD_PIN_RELATIVE),
                            "resume-finalize", "--session-id", session_id, "--slot", name,
                            "--plan", frozen_plan], check=False, capture_output=True, text=True,
                            timeout=120, env=self.env)
                        record = {"slot": name, "rc": result.returncode,
                                  "status": "FINALIZED" if result.returncode == 0 else "FAILED"}
                        if result.returncode:
                            flags.append("records.pin_ledger")
                    except Exception as exc:
                        record = {"slot": name, "status": "FAILED", "error": type(exc).__name__}
                        flags.append("records.pin_ledger")
                    metadata.setdefault("bracket_resume", []).append(record)
                    status = plan.ledger_head_status(measurement)
                if session_id in status["open_sessions"]:
                    night = Path(metadata["paths"].get("custody", measurement)) / "night"
                    stop = next((r.get("reason", r.get("kind")) for r in reversed(chain.stage_journal(night))
                                 if r.get("stage_id") == "chain.stop"), None)
                    stop = stop or read(night / "result.json").get("aborted_reason") or read(
                        night / "hazard_result.json").get("aborted_reason")
                    reason = stop or f"chain_exit:{metadata.get('chain_exit_code', 'unknown')}"
                    calibration_ledger.abort_bracket_session(measurement / plan.DEFAULT_LEDGER_RELATIVE,
                        session_id=session_id, reason=reason)
                    metadata["bracket_aborted"] = True
                    metadata["bracket_abort"] = {"status": "ABORTED", "reason": reason}
            except Exception as exc:
                metadata["bracket_abort"] = {"status": "FAILED", "error": type(exc).__name__}
                flags.append("records.pin_ledger")
        try:
            record = plan.advance_ledger_pin(measurement,
                session_id=session_id, operator_identity="b6-session-desk",
                attestation_reason="chain exit before session harvest" if not metadata.get("lost")
                else "chain lost without a terminal record; bracket session aborted before harvest")
            metadata["pin_advance"] = record
            return flags
        except Exception as exc:
            metadata["pin_advance"] = {"status": "FAILED", "error": type(exc).__name__}
            return flags + ["records.pin_ledger"]

    def evaluate_smoke(self, prepared, done):
        metadata = read(metadata_path(prepared))
        def run(argv, **kwargs):
            return self.run(argv, **{"timeout": HARVEST_TIMEOUT_S, **kwargs, "env": self.env,
                                     "capture_output": True, "text": True})
        report = smoke.desk(smoke.SmokePrepared.from_json(metadata["smoke"]),
                            driver_exit=done.chain_rc, run=run)
        # smoke.desk advances the smoke clone's pin before the shared harvest.
        # The loop holds on these codes and compares them across packs (the
        # same failure on two packs holds the loop), so they name the causes
        # of the status, not every recorded flag of the smoke.
        status, codes = report["status"], set()
        if status == "physics":
            _, physical = smoke._harvest_hooks()
            codes = {code for code in report["flags"] if physical(code)} or {"smoke.physics"}
        elif status == "fail":
            for row in report["stages"]:
                if row["rc"] not in row["success_exit_codes"]:
                    codes.add("stage_failed:" + str(row["stage_id"]))
            if report["driver_exit"] not in (0, 6):
                codes.add(f"driver_exit:{report['driver_exit']}")
            if report["harvest_exit"] not in (0, 6):
                codes.add(f"harvest_exit:{report['harvest_exit']}")
            acceptance = report.get("acceptance") or {}
            if acceptance.get("structural"):
                codes.update(acceptance.get("reasons") or ("acceptance.structural",))
            if report["errors"]:
                codes.add("records.collector_failed")
            codes = codes or {"smoke.failed"}
        return SmokeResult(status, tuple(sorted(codes)))

    def session_desk(self, prepared, done):
        started = time.monotonic()
        path = metadata_path(prepared)
        metadata = read(path)
        paths = {key: Path(value) for key, value in metadata["paths"].items()}
        metadata["chain_exit_code"] = done.chain_rc
        flags = self._advance(metadata)
        write(path, metadata)
        argv = [str(paths["measurement"] / ".venv/bin/python"),
                str(self.measurement / "scripts/harvest_b6_session.py"),
                "--plan", prepared.plan_path, "--archive-root", str(paths["archive"]),
                "--registration-dir", str(self.measurement / "configs/b6/registration"),
                "--pack-records-root", str(self.root / "packs"), "--export-dir", str(paths["export"])]
        if metadata.get("lost"):
            argv.append("--allow-missing-terminal")
        harvest_started = time.monotonic()
        try:
            result = self.run(argv, check=False, capture_output=True, text=True, env=self.env,
                              timeout=HARVEST_TIMEOUT_S)
            harvest_rc = result.returncode
            # Keep program diagnostics local; only structure reaches SessionLine.
            (paths["staging"] / "harvest.stdout").write_text(result.stdout or "")
            (paths["staging"] / "harvest.stderr").write_text(result.stderr or "")
        except (OSError, subprocess.TimeoutExpired):
            harvest_rc = 3
        if harvest_rc not in (0, 2, 3, 4, 5, 6):
            # Any other exit (1 from the live runner's timeout, a signal) is a
            # harvest program fault: pending re-harvest, never a judged session.
            (paths["staging"] / "harvest.exit").write_text(f"{harvest_rc}\n")
            harvest_rc = 3
        harvest_seconds = time.monotonic() - harvest_started
        reg = read(self.measurement / f'configs/b6/packs/{metadata["packs"][0]}/registration.json')
        structure = session_structure.check(archive=paths["archive"], custody=paths["custody"],
            registration=reg, harvest_rc=harvest_rc, runs_roots=metadata["runs_roots"], session_id=prepared.session_id)
        defects = list(structure["reasons"]) if structure["verdict"] in ("STRUCTURE_DEFECT", "NOT_READY") else []
        acceptance = read(paths["archive"] / "derived/b6-acceptance.json") if harvest_rc in (0, 6) else {}
        physical = done.physics_stop or structure["physical_stop"]
        if acceptance.get("physics_stop"):
            physical = physical or acceptance.get("physical_stop_kind") or "physics"
        if metadata.get("lost") or (done.chain_rc != 0 and not physical and not structure["chain_stopped"]):
            defects.append("chain_crashed")
        # The acceptance function's own structural failures (design 13.1: for
        # example a whole stage absent while later stages ran) hold the loop too.
        defects.extend(str(code) for code in acceptance.get("structural_failures") or ())
        structure.update(adapter_structure_defects=sorted(set(defects)))
        structure_path = paths["staging"] / "structure.json"
        write(structure_path, structure)
        catalog = load_catalog(self.measurement / "configs/b6/flag_catalog_b6.json")
        # Never put an energy-derived or otherwise restricted flag code in the
        # loop's public line, including through its pack-level projection.
        for code in acceptance.get("flag_counts", {}):
            if catalog.entry(code).get("blinding") == "STRUCTURE":
                flags.append(code)
        flags.extend(structure["flags"]["STRUCTURE"])
        pack_flags = {}
        for pack, codes in acceptance.get("pack_flags", {}).items():
            pack_flags[pack] = tuple(code for code in codes if catalog.entry(code).get("blinding") == "STRUCTURE")
        compressed_rc, compressed = 4, {"reason": "harvest_pending"}
        if harvest_rc == 0 and acceptance.get("verdict") in ("ACCEPT", "EXCLUDE"):
            compressed_rc, compressed = desk_compress.compress(archive=paths["archive"], custody=paths["custody"],
                runs_roots=metadata["runs_roots"], ledgers=[paths["measurement"] / plan.DEFAULT_LEDGER_RELATIVE],
                after=[structure_path])
        write(paths["staging"] / "compression.json", {"rc": compressed_rc, **compressed})
        counts = {row["stage_id"]: {key: row[key] for key in session_structure.COUNT_FIELDS}
                  for row in structure["per_roster_stage"]}
        return SessionLine(prepared.session_id, tuple(metadata["packs"]), chain_rc=done.chain_rc,
            harvest_rc=harvest_rc, verdict=structure["harvest_verdict"], physics_stop=physical,
            acceptance_verdict=acceptance.get("verdict", "UNAVAILABLE"), counting=acceptance.get("counting") is True,
            excluding_reasons=tuple(sorted({row["code"] for row in acceptance.get("excluding", ())
                if row.get("scope") == "window" and catalog.entry(row["code"]).get("blinding") == "STRUCTURE"})),
            # Only codes the block-6 catalog classes STRUCTURE reach the loop's
            # records and mail, whatever blinding a flag record carried.
            window_flags=tuple(sorted({code for code in flags if catalog.entry(code).get("blinding") == "STRUCTURE"})),
            pack_flags=pack_flags, counts=counts,
            structure_ok=not defects, structure_defects=tuple(sorted(set(defects))),
            minutes={"chain": (structure["chain_seconds"] or 0) / 60, "harvest": harvest_seconds / 60,
                     "desk": (time.monotonic() - started) / 60}, compressed=compressed_rc == 0)

    def reharvest(self, prepared, done):
        """Restore identical source bytes and retain every previous harvest."""
        path = metadata_path(prepared)
        metadata = read(path)
        old = Path(metadata["paths"]["archive"])
        record_dir = Path(str(old) + ".desk")
        if record_dir.exists():
            rc, restored = desk_compress.restore(record_dir=record_dir)
            write(Path(metadata["paths"]["staging"]) / "restore.json", {"rc": rc, **restored})
            if rc:
                raise ValueError("reharvest source restore failed")
        history = metadata.setdefault("harvest_history", [])
        history.append({"archive": str(old), "export": metadata["paths"]["export"]})
        archive_base = Path(history[0]["archive"])
        export_base = Path(history[0]["export"])
        sequence = len(history)
        while Path(str(archive_base) + f".reharvest-{sequence}").exists() or Path(str(export_base) + f".reharvest-{sequence}").exists():
            sequence += 1
        metadata["paths"].update(archive=str(archive_base) + f".reharvest-{sequence}",
                                 export=str(export_base) + f".reharvest-{sequence}")
        write(path, metadata)
        return self.session_desk(prepared, done)
