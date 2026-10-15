"""Session preparation and launchd handover; no collection is a loop child."""
from __future__ import annotations

from dataclasses import asdict, replace
import datetime as dt
import json
import math
import os
from pathlib import Path
import subprocess
import time

from joulewise.b5 import plan
from joulewise.b6 import desk_identity, plan_inputs, registration, session_paths, smoke as smoke_module
from joulewise.b6.lanes import Done, LaneMissing, Prepared, Refused, Running
from joulewise.session_structure import _physical

LABELS = ("com.joulewise.night", "com.joulewise.night.deadman")
PHYSICAL_STOPS = {"sampler_down": "sampler", "disk_exhausted": "disk", "thermal_emergency": "thermal",
                  "session_time_limit": "time_limit", "agent_pause_beyond_2h": "agent-pause-budget",
                  "operative_bound_above_stop": "calibration.operative_bound_above_stop"}


def read(path, default=None):
    try:
        value = json.loads(Path(path).read_text())
        return value if isinstance(value, dict) else ({} if default is None else default)
    except (OSError, ValueError):
        return {} if default is None else default


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    temporary.replace(path)


def metadata_path(prepared):
    return Path(prepared.plan_path).parent.parent / "session.json"


class DriverLane:
    def __init__(self, measurement, loop_root, run=subprocess.run, *, config=None, clock=time.time,
                 block_root=None, roots=None, launchctl_bin="launchctl", env=None):
        self.measurement, self.root = Path(measurement).resolve(), Path(loop_root).resolve()
        self.run, self.clock = run, clock
        self.config = config if config is not None else read(self.measurement / "configs/b6/loop.json")
        self.block_root, self.roots, self.launchctl_bin = block_root, roots, str(launchctl_bin)
        self.env = env

    def prepare_session(self, layout, rendered, *, smoke, keep, staging_root):
        if layout.fixed_bytes is None or len(layout.packs) != 1 or not layout.campaign_id:
            return LaneMissing("driver:modular")
        stage = session_paths.safe_path(staging_root)
        pointer = stage / "prepared.json"
        if pointer.is_file():
            return Prepared(**read(pointer))
        stage.mkdir(parents=True, exist_ok=True)
        paths = session_paths.for_session(self.measurement, self.root, layout.session_id,
            block_root=self.block_root, staging_root=stage, roots=self.roots)
        # Recover a crash after the prepared record, before its staging pointer.
        candidates = [paths.custody.parent / "session.json", *sorted((stage / "smoke").glob("*/session.json"))]
        for candidate in candidates:
            record = read(candidate)
            if record.get("session_id") == layout.session_id and record.get("prepared"):
                write(pointer, record["prepared"])
                return Prepared(**record["prepared"])
        paths.custody.parent.mkdir(parents=True, exist_ok=True)
        paths.runs_parent.mkdir(parents=True, exist_ok=True)
        identities, notes = desk_identity.collect(self.measurement, stage / "inputs", run=self.run)
        reg = self.measurement / registration.DEFAULT_DIR_RELATIVE
        inputs = plan_inputs.build(self.measurement, reg, layout.campaign_id, layout.session_id, identities,
            custody_root=paths.custody, runs_parent=paths.runs_parent, claim_backup=paths.backup_claim,
            bound_backup=paths.backup_bound, run=self.run)
        fp = {}
        checks = sorted((self.root / "staging" / layout.session_id.split("-smoke-")[0] / "precheck").glob("*/*/precheck.json"))
        if checks:
            fp = read(checks[-1]).get("fingerprint", {})
        smoke_record = None
        if smoke:
            prepared_smoke = smoke_module.prepare(layout.campaign_id, inputs["measurement_head"],
                self.measurement, stage / "smoke", plan_inputs=inputs, fp=fp, state_root=self.root,
                now=dt.datetime.fromtimestamp(self.clock(), dt.timezone.utc), run=self.run,
                registration_dir=reg, defer_plan=True, keep=keep)
            smoke_record = prepared_smoke.to_json()
            inputs = read(prepared_smoke.smoke_dir / "smoke-state.json")["plan_inputs"]
            paths = replace(paths, measurement=prepared_smoke.measurement, custody=prepared_smoke.custody,
                runs_parent=Path(inputs["runs_parent"]), backup_claim=Path(inputs["claim_backup_destination"]),
                backup_bound=Path(inputs["bound_backup_destination"]), archive=prepared_smoke.smoke_dir / "archive",
                export=prepared_smoke.smoke_dir / "export")
        prepared = Prepared(layout.session_id, str(paths.plan), str(paths.terminal), plan_inputs.window_max_s(inputs))
        metadata = {"session_id": layout.session_id, "packs": list(layout.packs), "campaign_id": layout.campaign_id,
            "paths": paths.json(), "inputs": inputs, "notes": notes, "smoke": smoke_record,
            "prepared": asdict(prepared), "runs_roots": []}
        write(metadata_path(prepared), metadata)
        write(stage / "plan-inputs.json", inputs)
        write(pointer, asdict(prepared))
        return prepared

    def _job(self, label):
        result = self.run([self.launchctl_bin, "print", f"gui/{os.getuid()}/{label}"],
                          check=False, capture_output=True, text=True, timeout=10, env=self.env)
        if result.returncode == 0:
            return True
        signature = f'Could not find service "{label}" in domain for user gui: {os.getuid()}'
        if result.returncode == 113 and signature in (result.stderr or "").splitlines():
            return False
        # A failed census is not proof the job has gone.
        raise RuntimeError("launchd job state unavailable")

    def _installer(self, metadata, *, uninstall=False):
        paths = metadata["paths"]
        measurement = Path(paths["measurement"])
        argv = [str(self.measurement / "scripts/install_night_agent.sh"), "--plan", metadata["prepared"]["plan_path"],
                "--python", str(measurement / ".venv/bin/python"), "--courier-bin",
                str(self.measurement / "scripts/b6_courier.sh"), "--launchctl-bin", self.launchctl_bin]
        if uninstall:
            argv.append("--uninstall")
        return self.run(argv, check=False, capture_output=True, text=True, timeout=180, env=self.env)

    def launch(self, prepared):
        path = metadata_path(prepared)
        metadata = read(path)
        if Path(prepared.plan_path).exists():
            # A durable plan is the launch idempotency key, even across a crash
            # between installer completion and publication of loop state.
            return Running(str(path))
        inputs = dict(metadata["inputs"])
        lead = self.config.get("launch_lead_s", 420)
        if type(lead) not in (int, float) or lead < 300:
            raise ValueError("launch_lead_s must leave the installer's 300 seconds")
        inputs["t0_epoch_s"] = 60 * math.ceil((self.clock() + lead) / 60)
        # A previous smoke may have advanced the source checkout's ledger pin.
        inputs["measurement_head"] = smoke_module._git(Path(inputs["measurement_root"]), "rev-parse", "HEAD", run=self.run)
        if not metadata["smoke"]:
            inputs["repo_head"] = inputs["measurement_head"]
        record = plan.write_window_plan(inputs, now=self.clock)
        if record["window_max_s"] != prepared.max_s:
            raise ValueError("prepared and written window_max_s disagree")
        metadata.update(inputs=inputs, runs_roots=list(record["runs_roots"].values()), install_attempted=True)
        write(path, metadata)
        installed = self._installer(metadata)
        metadata["install_rc"] = installed.returncode
        (Path(metadata["paths"]["staging"]) / "install.stdout").write_text(installed.stdout or "")
        (Path(metadata["paths"]["staging"]) / "install.stderr").write_text(installed.stderr or "")
        write(path, metadata)
        if installed.returncode:
            raise RuntimeError("night job install failed; retained plan prevents a duplicate install")
        return Running(str(path))

    def _uninstall(self, path, metadata):
        if metadata.get("uninstalled"):
            return
        result = self._installer(metadata, uninstall=True)
        metadata["uninstall_rc"] = result.returncode
        metadata["uninstalled"] = result.returncode == 0
        write(path, metadata)
        if result.returncode:
            raise RuntimeError("night job uninstall failed")

    def status(self, handle):
        path = Path(handle.handle)
        metadata = read(path)
        night = Path(metadata["paths"]["custody"]) / "night"
        terminal = night / "result.json"
        if terminal.exists():
            self._uninstall(path, metadata)
            result, hazard = read(terminal), read(night / "hazard_result.json")
            # chain.started means a process launched, not necessarily that a
            # measured stage ran. Arm/t0 physics can still refuse before it.
            from joulewise.b5.chain import stage_journal
            journal = stage_journal(night)
            measured = any(row.get("kind") in ("campaign_collection", "calibration_capture") for row in journal)
            arm = hazard.get("arm") or read(Path(metadata["paths"]["custody"]) / "hazards/arm.json")
            hazards = []
            if not measured and not (night / "chain.started").exists():
                reason = _physical(result.get("aborted_reason"))
                if reason and reason != "hazard":
                    hazards.append(reason)
                if arm.get("go") is False or arm.get("decision") in ("REFUSE", "REFUSED", "NO_GO"):
                    for module, verdict in (arm.get("verdicts") or {}).items():
                        if (verdict.get("status") if isinstance(verdict, dict) else verdict) == "REFUSE":
                            if module in ("clock", "battery", "thermal", "contention", "disk", "instrument", "agents"):
                                hazards.append(module)
                    for module, readings in (arm.get("hazards") or {}).items():
                        if module in ("clock", "battery", "thermal", "contention", "disk", "instrument") and any(
                                (row.get("verdict") or {}).get("status") == "REFUSE" for row in readings):
                            hazards.append(module)
            if hazards:
                return Refused(tuple(sorted(set(hazards))))
            rc = read(night / "chain.exited").get("exit_code", result.get("chain_exit_code"))
            reason = _physical(result.get("aborted_reason"))
            if reason == "hazard":
                reason = None  # the generic arm record does not identify physics
            if reason is None:
                stop = next((row for row in reversed(journal) if row.get("stage_id") == "chain.stop"), {})
                reason = PHYSICAL_STOPS.get(stop.get("reason", stop.get("kind")))
            return Done(rc if type(rc) is int else (0 if result.get("verdict") == "GO" else 1), reason)
        if self._job(LABELS[0]):
            return handle
        # No job and no terminal: retain all bytes, desk with a structural
        # crash (design 13.1), then hold before another pack can arm.
        self._uninstall(path, metadata)
        metadata["lost"] = True
        write(path, metadata)
        return Done(1, None)
