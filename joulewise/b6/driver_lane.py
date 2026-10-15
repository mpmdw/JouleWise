"""Session preparation and launchd handover; no collection is a loop child."""
from __future__ import annotations

from dataclasses import asdict, replace
import datetime as dt
import json
import math
import os
import re
from pathlib import Path
import subprocess
import time

from joulewise.b5 import plan
from joulewise.b6 import desk_identity, plan_inputs, registration, session_paths, smoke as smoke_module
from joulewise.b6.lanes import Done, LaneMissing, Prepared, Refused, Running
from joulewise.session_structure import CHAIN_STOP_EXITS, PHYSICAL_STOP_CODES, _physical

LABELS = ("com.joulewise.night", "com.joulewise.night.deadman")
ARM_UNMEASURED_REFUSES = frozenset({"instrument"})  # joulewise.b5.driver, not imported at the desk


def process_group_alive(pgid):
    """A signal-0 probe of the chain's process group; it signals nothing."""
    if type(pgid) is not int or pgid <= 1:
        return False
    try:
        os.killpg(pgid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True
PHYSICAL_STOPS = dict(PHYSICAL_STOP_CODES)


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
                 block_root=None, roots=None, launchctl_bin="launchctl", env=None, group_alive=None):
        self.measurement, self.root = Path(measurement).resolve(), Path(loop_root).resolve()
        self.run, self.clock = run, clock
        self.config = config if config is not None else read(self.measurement / "configs/b6/loop.json")
        self.block_root, self.roots, self.launchctl_bin = block_root, roots, str(launchctl_bin)
        self.env = env
        self.group_alive = group_alive or process_group_alive

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

    def _job_pending_or_running(self, label, metadata):
        """True while the night job may still produce a terminal record.

        The night job is a calendar job: launchd keeps it loaded after its one
        run ends, so "loaded" alone is not "running". It counts as ended when
        launchd reports at least one run, no running process, and the chain's
        process group (night/chain.started pgid) is gone.
        """
        result = self.run([self.launchctl_bin, "print", f"gui/{os.getuid()}/{label}"],
                          check=False, capture_output=True, text=True, timeout=10, env=self.env)
        started = read(Path(metadata["paths"]["custody"]) / "night/chain.started")
        if result.returncode != 0:
            # _job raises unless launchd says the job is absent.
            return self._job(label) or self.group_alive(started.get("pgid"))
        text = result.stdout or ""
        runs = re.search(r"^\s*runs = (\d+)\s*$", text, re.M)
        running = re.search(r"^\s*state = running\s*$", text, re.M) or re.search(r"^\s*pid = \d+\s*$", text, re.M)
        if running or runs is None or int(runs.group(1)) == 0:
            return True
        return self.group_alive(started.get("pgid"))

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
            # A durable plan plus a completed install (or a job launchd holds,
            # or a terminal record) is the launch idempotency key, even across
            # a crash between installer completion and publication of loop
            # state. A plan whose install never completed was never launched:
            # install it now while its t0 still leaves the installer its 300 s,
            # else stop and say so (the loop holds; a resume gets a new id).
            metadata = self._adopt_plan(path, metadata, prepared)
            terminal = Path(prepared.terminal_path).exists()
            if metadata.get("install_rc") == 0 or terminal or self._job(LABELS[0]):
                return Running(str(path))
            t0 = read(prepared.plan_path).get("t0_epoch_s")
            if type(t0) not in (int, float) or t0 - self.clock() < 300:
                raise RuntimeError("plan written but its night job was never installed; t0 has passed")
            return self._install_and_record(path, metadata)
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
        return self._install_and_record(path, metadata)

    def _adopt_plan(self, path, metadata, prepared):
        """Recover what a crash between the plan write and the metadata write lost.

        The plan records t0 and both runs roots; the desk compresses the roots
        named here, and the installer reads t0 from the plan itself.
        """
        plan_record = read(prepared.plan_path)
        bindings = (plan_record.get("hazard_window") or {}).get("bindings") or {}
        roots = [bindings[key] for key in ("claim_runs_root", "bound_runs_root") if isinstance(bindings.get(key), str)]
        changed = False
        if roots and set(metadata.get("runs_roots") or ()) != set(roots):
            metadata["runs_roots"], changed = roots, True
        if "t0_epoch_s" not in metadata.get("inputs", {}) and "t0_epoch_s" in plan_record:
            metadata.setdefault("inputs", {})["t0_epoch_s"] = plan_record["t0_epoch_s"]
            changed = True
        if changed:
            write(path, metadata)
        return metadata

    def _install_and_record(self, path, metadata):
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
            # chain.started means a process launched, not necessarily that its
            # first stage ran. The reservation is that first stage (§1.6).
            from joulewise.b5.chain import stage_journal
            journal = stage_journal(night)
            stage_started = any(row.get("kind") in ("bracket_reservation", "campaign_collection", "calibration_capture")
                                for row in journal)
            arm = hazard.get("arm") or read(Path(metadata["paths"]["custody"]) / "hazards/arm.json")
            hazards = []
            if not stage_started:
                reason = _physical(result.get("aborted_reason"))
                if reason and reason != "hazard":
                    hazards.append(reason)
                if arm.get("go") is False or arm.get("decision") in ("REFUSE", "REFUSED", "NO_GO"):
                    for module, verdict in (arm.get("verdicts") or {}).items():
                        status = verdict.get("status") if isinstance(verdict, dict) else verdict
                        # The driver also refuses an UNMEASURED instrument
                        # (b5.driver.ARM_UNMEASURED_REFUSES): the sampler.
                        if status == "REFUSE" or (status == "UNMEASURED" and module in ARM_UNMEASURED_REFUSES):
                            if module in ("clock", "battery", "thermal", "contention", "disk", "instrument", "agents"):
                                hazards.append(module)
                    # The arm's own agent censuses (before the dwell and at GO)
                    # refuse with every module PASS; their record names them.
                    record = read(Path(metadata["paths"]["custody"]) / "hazards/arm.json")
                    censuses = (record.get("census"), record.get("census_at_go"),
                                arm.get("census"), arm.get("census_at_go"))
                    if (any(isinstance(c, dict) and c.get("clean") is False for c in censuses)
                            or record.get("refused_at") in ("census", "census_at_go")
                            or any(str(r).startswith("agent census") or "agent process present" in str(r)
                                   for r in arm.get("reasons") or ())):
                        hazards.append("agent")
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
                stop_kind = stop.get("reason", stop.get("kind")) if stop else CHAIN_STOP_EXITS.get(rc)
                reason = PHYSICAL_STOPS.get(stop_kind)
            return Done(rc if type(rc) is int else (0 if result.get("verdict") == "GO" else 1), reason)
        if self._job_pending_or_running(LABELS[0], metadata):
            return handle
        # No terminal, and either launchd no longer holds the job or the job's
        # one run has ended, and the chain's process group is gone: retain all
        # bytes, desk with a structural crash (design 13.1), then hold before
        # another pack can arm.
        self._uninstall(path, metadata)
        metadata["lost"] = True
        write(path, metadata)
        return Done(1, None)
