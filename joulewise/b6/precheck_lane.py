"""P1/P2: combine campaign checks and offer only the bounded desk remedy."""
from __future__ import annotations

from dataclasses import replace
import json
import os
from pathlib import Path
import subprocess

from joulewise.b6 import precheck, session_paths
from joulewise.b6.lanes import Exclusion, Hazard, PrecheckResult
from joulewise.hazards.base import Completed, Context
from scripts import fixture_orphan_census


def probe_runner(run):
    def probe(argv, timeout_s):
        argv = tuple(map(str, argv))
        try:
            value = run(argv, check=False, capture_output=True, timeout=timeout_s,
                        env={**os.environ, "LC_ALL": "C", "GIT_OPTIONAL_LOCKS": "0",
                             "PYTHONDONTWRITEBYTECODE": "1"})
            stdout = value.stdout.encode() if isinstance(value.stdout, str) else value.stdout or b""
            stderr = value.stderr.encode() if isinstance(value.stderr, str) else value.stderr or b""
            return Completed(argv, value.returncode, stdout, stderr)
        except subprocess.TimeoutExpired as exc:
            return Completed(argv, None, exc.stdout or b"", exc.stderr or b"", timed_out=True)
        except OSError as exc:
            return Completed(argv, None, b"", b"", error=f"{type(exc).__name__}: {exc}")
    return probe


class PrecheckLane:
    def __init__(self, measurement_root, loop_root, run, *, block_root=None, check=precheck.run_precheck,
                 context_factory=None, seams=None):
        self.measurement, self.root = Path(measurement_root), Path(loop_root)
        self.run_tool, self.check, self.block_root = run, check, block_root
        self.context_factory, self.seams = context_factory, seams

    def _context(self, out):
        return self.context_factory(out) if self.context_factory else Context(
            run=probe_runner(self.run_tool), raw_dir=out.parent / "raw")

    def run(self, layout, plan_path):
        from joulewise.flags.catalog import load_catalog
        paths = session_paths.for_session(self.measurement, self.root, layout.session_id, block_root=self.block_root)
        inputs_path = paths.staging / "plan-inputs.json"
        if inputs_path.exists():
            inputs = json.loads(inputs_path.read_text())
            paths = replace(paths, custody=Path(inputs["custody_root"]), runs_parent=Path(inputs["runs_parent"]),
                            backup_claim=Path(inputs["claim_backup_destination"]),
                            backup_bound=Path(inputs["bound_backup_destination"]))
        parent = paths.staging / "precheck"
        parent.mkdir(parents=True, exist_ok=True)
        attempt = 1
        while (parent / f"{attempt:06}").exists():
            attempt += 1
        current = parent / f"{attempt:06}"
        current.mkdir()
        hazards, exclusions, flags, remedies, fingerprints = [], [], set(), set(), {}
        thin = False
        catalog = load_catalog(self.measurement / "configs/b6/flag_catalog_b6.json")
        for pack in layout.packs:
            reg = json.loads((self.measurement / f"configs/b6/packs/{pack}/registration.json").read_text())
            campaign = Path(reg["plan_tree_ref"]).parent.name
            out = current / pack / "precheck.json"
            ctx = self._context(out)
            seams = self.seams or precheck.Seams()
            if self.seams is None:
                def observed_orphans():
                    result = ctx.run(tuple(fixture_orphan_census.PS_ARGV), ctx.probe_timeout_s)
                    if not result.ok:
                        raise ValueError("orphan census unavailable")
                    return fixture_orphan_census.census(result.stdout.decode(), fixture_orphan_census.load_signatures())
                seams = replace(seams, orphan_collect=observed_orphans)
            result = self.check(campaign, self.measurement, self.root, out=out,
                                registration_dir=self.measurement / precheck.REGISTRATION_RELATIVE,
                                disk_targets=session_paths.disk_targets(paths, stat=seams.stat),
                                ctx=ctx, seams=seams)
            # Design 3.3: orphaned registered fixtures (parent pid 1, this uid)
            # are reaped by the pre-check, after a fresh census (precheck F6).
            fingerprints[pack] = result["fingerprint"]
            thin |= (result.get("margin") or {}).get("status") == "thin"
            flags.update(row if isinstance(row, str) else row["code"] for row in result["predicted_flags"])
            for row in result["would_refuse"]:
                hazard = row["hazard"]
                hazards.append(Hazard(hazard, json.dumps(row, sort_keys=True)))
                if hazard in ("disk", "instrument", "sampler") or row.get("code") == "clock.rate":
                    remedies.add(hazard)
            certain = result.get("certain_exclusion") or {}
            for reason in certain.get("reasons", []):
                code = str(reason).split(":", 1)[0]
                if code == "model.hash_mismatch":
                    code = "model.files_differ_from_registered"
                elif code == "plan.dispatch_unresolved":
                    code = "precheck.certain_exclusion"
                if code not in catalog.codes:
                    code = "precheck.certain_exclusion"
                exclusions.append(Exclusion(code, pack))
        return PrecheckResult(tuple(hazards), tuple(exclusions), thin, tuple(sorted(flags)),
                              {"packs": fingerprints}, tuple(sorted(remedies)))

    def remedy(self, hazard):
        if hazard != "disk":
            # No production-context sampler relaunch entry point exists.
            return False
        improved = False
        from joulewise import desk_compress
        base = Path(self.block_root or self.root.parent) / "sessions"
        for record in sorted(base.glob("*/session.json")):
            try:
                metadata = json.loads(record.read_text())
                paths = metadata["paths"]
                custody, archive = Path(paths["custody"]), Path(paths["archive"])
                if not (custody / "night/chain.exited").is_file() or not (archive / "harvest.json").is_file():
                    continue
                after = Path(paths["staging"]) / "structure.json"
                if not after.is_file():
                    continue
                rc, result = desk_compress.compress(archive=archive, custody=custody,
                    runs_roots=metadata.get("runs_roots", []),
                    ledgers=[Path(paths["measurement"]) / "runs/calibration_observation_ledger.jsonl"], after=[after])
                improved |= rc == 0 and result.get("files", 0) > 0
            except (OSError, ValueError, KeyError, TypeError):
                continue
        return improved
