#!/usr/bin/env python3
"""Offline re-grade a Qwen4 gold work directory (finished or in progress) under the current gate.

No worker, framework runtime, or network access is used, and no report verdict
is trusted: every case's saved worker evidence is authenticated and all trace
metrics and unit verdicts are recomputed by the current comparators.

Evidence accepted per case:

* ``v2``: the fingerprint-bound inventory of both workers' requests, results
  and arrays (``evidence_digest``), exactly as ``--resume`` requires.
* ``legacy-npy``: reports written before that inventory existed.  The listed
  ``*.npy`` hashes must equal the case's arrays exactly, and each side's
  ``result.json`` may only name its own canonically named ``<trace>.npy`` files
  (so a result map cannot alias a trace).  When the work directory holds a
  streaming ``manifest.json`` every array of a completed unit must also match
  the independently recorded unit artifact hashes there (a unit still running
  has no record yet and is reported ``INCOMPLETE``).

The work directory is read-only: nothing under it is written, locked, or
removed.  Results go to ``--output`` (default ``WORK/regate.json``; required,
and outside WORK, for a streaming work directory, which may be live).
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from joulewise.align.qwen4_gold.core import IndexedCheckpoint, digest, sha256, write_json  # noqa: E402
from joulewise.align.qwen4_gold.runner import Harness, artifacts, reusable  # noqa: E402


class Checkpoints:
    """Norm weights from the first of several local checkpoints/views holding them."""

    def __init__(self, roots):
        self.items = [IndexedCheckpoint(Path(r).resolve()) for r in roots]
        self.config, self.prefix = self.items[0].config, self.items[0].prefix

    def read(self, name, *a, **kw):
        for item in self.items:
            # A restaged view keeps the full index but holds only its unit's tensors.
            if name in item.weight_map and (item.root / item.weight_map[name]).is_file():
                try:
                    item.info(name)
                except Exception:  # noqa: BLE001 - tensor absent from this view's shard
                    continue
                return item.read(name, *a, **kw)
        raise KeyError(f"norm weight not in any supplied checkpoint/view: {name}")


def verify_views(roots, manifest):
    """Byte-check checkpoint views against a streaming manifest's derived shards."""
    checked = {}
    for root in (Path(r).resolve() for r in roots):
        for key, row in (manifest or {}).get("derived_shards", {}).items():
            parent = Path(key).parent
            if parent.parent.name == "views" and parent.name == root.name and (root / Path(key).name).is_file():
                if sha256(root / Path(key).name) != row["sha256"]:
                    raise SystemExit(f"checkpoint view differs from the run's recorded shard: {root / Path(key).name}")
                checked[str(root / Path(key).name)] = row["sha256"]
    return checked


def authenticate(case, report, work, manifest_artifacts):
    """Return (evidence kind, reason) for the case's worker evidence."""
    fp = report.get("fingerprint")
    if not fp:
        return None, "no fingerprint"
    if "evidence_digest" in report:
        return ("v2", None) if reusable(case / "report.json", fp) else (None, "v2 evidence inventory failed")
    expected = report.get("artifacts") or {}
    actual = {str(p.relative_to(case)): sha256(p) for p in sorted(case.rglob("*.npy"))}
    if not expected or expected != actual:
        return None, "legacy npy inventory differs from the case arrays"
    for side in ("reference", "mlx"):
        result = case / side / "result.json"
        if not result.is_file():
            return None, f"missing {side}/result.json"
        traces = json.loads(result.read_text()).get("traces", {})
        if any(f != f"{name}.npy" or f"{side}/{f}" not in expected for name, f in traces.items()):
            return None, f"{side}/result.json trace map is not canonical"
    kind = "legacy-npy"
    if manifest_artifacts is not None:
        for name, checksum in actual.items():
            if manifest_artifacts.get(str((case / name).relative_to(work))) != checksum:
                return None, f"array not recorded in manifest: {name}"
        kind += "+manifest"
    return kind, None


def regate_work(work, checkpoint, manifest=None):
    work = Path(work).resolve()
    parity = work / "parity" if (work / "parity").is_dir() else work
    harness = object.__new__(Harness)
    harness.checkpoint = checkpoint
    units = {}
    for unit_dir in sorted(p for p in parity.iterdir() if p.is_dir() and (
            p.name.startswith("layer-") or p.name in {"embed", "final", "head"})):
        unit = (unit_dir.name[6:].lstrip("0") or "0") if unit_dir.name.startswith("layer-") else unit_dir.name
        # Units still running have no manifest record yet: npy inventory only.
        recorded = (manifest or {}).get("units", {}).get(unit, {}).get("artifacts")
        cases = []
        for case in sorted(p for p in unit_dir.iterdir() if p.is_dir() and ".attempt-" not in p.name):
            path = case / "report.json"
            if not path.is_file():
                continue  # In progress (or never started): not evidence yet.
            if not (case / "mlx").is_dir():
                cases.append({"case": case.name, "status": "NOT_COMPARED"})
                continue
            old = json.loads(path.read_text())
            kind, reason = authenticate(case, old, work, recorded)
            if kind is None:
                cases.append({"case": case.name, "status": "EVIDENCE_ERROR", "reason": reason})
                continue
            if not (case / "mlx/result.json").is_file():
                cases.append({"case": case.name, "status": "MLX_ERROR", "evidence": kind})
                continue
            fp = old["fingerprint"]
            dtype = "bf16" if "-bf16-" in case.name else "fp32"
            mode = case.name.rsplit("-", 1)[-1]
            fresh = harness.grade_saved(unit, dtype, case, fp, mode, old.get("random_scale"))
            fresh["evidence"] = kind
            fresh["artifacts"] = artifacts(case)
            fresh["evidence_digest"] = digest({"fingerprint": fp, "artifacts": fresh["artifacts"]})
            fresh["recorded_status"] = old.get("status")  # informative only
            cases.append(fresh)
        compared = [c for c in cases if c["status"] != "NOT_COMPARED"]
        summary = parity / f"{unit_dir.name}.json"
        expected = json.loads(summary.read_text()).get("expected_cases") if summary.is_file() else None
        if not compared:
            status = "REFERENCE_CHAIN_ONLY"
        elif len(compared) == len(cases) == expected and all(c["status"] == "PASS" for c in compared):
            status = "PASS"
        elif any(c["status"] != "PASS" for c in compared):
            status = "FAILED"
        else:
            status = "INCOMPLETE"
        units[unit] = {"unit": unit, "status": status, "expected_cases": expected,
                       "completed_cases": len(compared), "cases": cases}
    graded = [u for u in units.values() if u["status"] != "REFERENCE_CHAIN_ONLY"]
    return {"schema": "qwen4-gold/regate-v2", "work_dir": str(work), "units": units,
            "status": "PASS" if graded and all(u["status"] == "PASS" for u in graded) else "INCOMPLETE_OR_FAILED"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--work-dir", required=True, help="streaming WORK (containing parity/) or a runner --output")
    parser.add_argument("--checkpoint", required=True, action="append",
                        help="local checkpoint/view containing compared norm weights; repeat for several views")
    parser.add_argument("--manifest", help="streaming manifest (default WORK/manifest.json when present)")
    parser.add_argument("--output")
    args = parser.parse_args(argv)
    work = Path(args.work_dir).resolve()
    manifest_path = Path(args.manifest) if args.manifest else work / "manifest.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.is_file() else None
    streaming = manifest is not None or (work / "driver.lock").exists()
    if streaming and not args.output:
        parser.error("streaming work directories may be live: pass --output outside WORK")
    output = Path(args.output).resolve() if args.output else work / "regate.json"
    if streaming and work in output.parents:
        parser.error("--output must be outside a streaming work directory")
    views = verify_views(args.checkpoint, manifest)
    result = regate_work(work, Checkpoints(args.checkpoint), manifest)
    result["checkpoint_views_verified"] = views
    write_json(output, result)
    for unit, row in result["units"].items():
        counts = {}
        for case in row["cases"]:
            counts[case["status"]] = counts.get(case["status"], 0) + 1
        print(f"{unit}: {row['status']} ({row['completed_cases']}/{row['expected_cases']} cases: {counts})")
    print(f"overall: {result['status']} -> {output}")
    return 0 if result["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
