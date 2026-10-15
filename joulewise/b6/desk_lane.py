"""The one harvest path, followed by structure checks and verified compression."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import time

from joulewise import desk_compress, session_structure
from joulewise.b5 import plan
from joulewise.b6 import smoke
from joulewise.b6.driver_lane import metadata_path, read, write
from joulewise.b6.lanes import SessionLine, SmokeResult
from joulewise.flags.catalog import load_catalog


class DeskLane:
    def __init__(self, measurement, loop_root, run=subprocess.run, *, env=None):
        self.measurement, self.root, self.run = Path(measurement), Path(loop_root), run
        self.env = env

    def _advance(self, metadata):
        try:
            record = plan.advance_ledger_pin(Path(metadata["paths"]["measurement"]),
                session_id=metadata["inputs"]["bracket_session_id"], operator_identity="b6-session-desk",
                attestation_reason="chain exit before session harvest")
            metadata["pin_advance"] = record
            return []
        except Exception as exc:
            metadata["pin_advance"] = {"status": "FAILED", "error": type(exc).__name__}
            return ["records.pin_ledger"]

    def evaluate_smoke(self, prepared, done):
        metadata = read(metadata_path(prepared))
        def run(argv, **kwargs):
            return self.run(argv, **{**kwargs, "env": self.env, "capture_output": True, "text": True})
        report = smoke.desk(smoke.SmokePrepared.from_json(metadata["smoke"]),
                            driver_exit=done.chain_rc, run=run)
        # smoke.desk advances the smoke clone's pin before the shared harvest.
        codes = set(report["flags"])
        if report["errors"]:
            codes.add("records.collector_failed")
        return SmokeResult(report["status"], tuple(sorted(codes)))

    def session_desk(self, prepared, done):
        started = time.monotonic()
        path = metadata_path(prepared)
        metadata = read(path)
        paths = {key: Path(value) for key, value in metadata["paths"].items()}
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
            result = self.run(argv, check=False, capture_output=True, text=True, env=self.env)
            harvest_rc = result.returncode
            # Keep program diagnostics local; only structure reaches SessionLine.
            (paths["staging"] / "harvest.stdout").write_text(result.stdout or "")
            (paths["staging"] / "harvest.stderr").write_text(result.stderr or "")
        except OSError:
            harvest_rc = 3
        harvest_seconds = time.monotonic() - harvest_started
        reg = read(self.measurement / f'configs/b6/packs/{metadata["packs"][0]}/registration.json')
        structure = session_structure.check(archive=paths["archive"], custody=paths["custody"],
            registration=reg, harvest_rc=harvest_rc, runs_roots=metadata["runs_roots"], session_id=prepared.session_id)
        defects = list(structure["reasons"]) if structure["verdict"] in ("STRUCTURE_DEFECT", "NOT_READY") else []
        if metadata.get("lost") or (done.chain_rc != 0 and not done.physics_stop and not structure["chain_stopped"]):
            defects.append("chain_crashed")
        structure.update(adapter_structure_defects=sorted(set(defects)))
        structure_path = paths["staging"] / "structure.json"
        write(structure_path, structure)
        acceptance = read(paths["archive"] / "derived/b6-acceptance.json")
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
        compressed_rc, compressed = desk_compress.compress(archive=paths["archive"], custody=paths["custody"],
            runs_roots=metadata["runs_roots"], ledgers=[paths["measurement"] / plan.DEFAULT_LEDGER_RELATIVE],
            after=[structure_path])
        write(paths["staging"] / "compression.json", {"rc": compressed_rc, **compressed})
        counts = {row["stage_id"]: {key: row[key] for key in session_structure.COUNT_FIELDS}
                  for row in structure["per_roster_stage"]}
        return SessionLine(prepared.session_id, tuple(metadata["packs"]), chain_rc=done.chain_rc,
            harvest_rc=harvest_rc, verdict=structure["harvest_verdict"], physics_stop=done.physics_stop or structure["physical_stop"],
            window_flags=tuple(sorted(set(flags))), pack_flags=pack_flags, counts=counts,
            structure_ok=not defects, structure_defects=tuple(sorted(set(defects))),
            minutes={"chain": (structure["chain_seconds"] or 0) / 60, "harvest": harvest_seconds / 60,
                     "desk": (time.monotonic() - started) / 60}, compressed=compressed_rc == 0)
