# Adapted from JouleWise-data 6039fff; exercised by ReviewerProbeTests.
"""Production-shaped harness for the BYTES analysis review.

Builds a campaign with the repository's own tests.test_bytes_analysis.archive_campaign (real mock
reducer -> harvest archive layout -> native B6 exporter), lets a probe plant defects in the archive,
then runs scripts/bytes_analyze.py exactly as an operator would: --stage fit, then --stage heldout
with the committed predictions. Must be run with cwd = the JouleWise checkout.
"""
from __future__ import annotations

import contextlib
import io
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, ".")
from joulewise import bytes_analysis as ba  # noqa: E402
from joulewise.external import km003c_parse as kp  # noqa: E402
from scripts import bytes_analyze  # noqa: E402
from tests.test_bytes_analysis import archive_campaign  # noqa: E402


def build(root: Path, world="bytes", seed=1100):
    root.mkdir(parents=True, exist_ok=True)
    manifest = archive_campaign(root, world=world, seed=seed)
    save_manifest(root, manifest)
    return manifest


def save_manifest(root, manifest):
    (root / "manifest.json").write_text(json.dumps(manifest) + "\n")


def archive(manifest, pass_id):
    return Path(next(s["archive"] for s in manifest["sessions"] if s["pass_id"] == pass_id))


def run_ids(manifest, pass_id, model):
    roster = ba.read_json(archive(manifest, pass_id) / "derived/roster.json")
    cell = next(m for m in manifest["models"] if m["model"] == model)["cell_ids"][0]
    return [m["run_id"] for m in roster["members"] if any(u["cell_id"] == cell for u in m.get("units", []))]


def edit_json(path, fn):
    value = ba.read_json(path)
    fn(value)
    Path(path).write_text(json.dumps(value) + "\n")


def exclude(manifest, pass_id, run_id, code, *, emit_flag=True):
    def fn(acc):
        acc["excluding"].append({"scope": "member", "run_id": run_id, "code": code})
        if emit_flag:
            acc["emitted_flags"].append({"scope": {"run_id": run_id}, "code": code})
    edit_json(archive(manifest, pass_id) / "derived/b6-acceptance.json", fn)


def flag(manifest, pass_id, run_id, code):
    edit_json(archive(manifest, pass_id) / "derived/b6-acceptance.json",
              lambda acc: acc["emitted_flags"].append({"scope": {"run_id": run_id}, "code": code}))


def stored_summary(manifest, pass_id, run_id):
    return archive(manifest, pass_id) / "withheld/reductions" / (run_id + ".summary_metrics.rereduced.json")


def bundle(manifest, pass_id, run_id):
    return archive(manifest, pass_id) / "sources/claim-runs" / run_id


def rewrite_stream(manifest, pass_id, fn):
    """fn(list_of_(watts, tick)) -> new list; re-encodes batches like archive_campaign."""
    path = archive(manifest, pass_id) / "sources/night-custody/hazards/meter/stream-001.jsonl"
    lines = [json.loads(s) for s in path.read_text().splitlines() if s.strip()]
    header, trailer = lines[0], lines[-1]
    batches = lines[1:-1]
    return path, header, batches, trailer


def run(root: Path, out_name="out", *, two_stage=True):
    """Run the CLI. Returns (exit codes, stderr text, out dir)."""
    out_fit, out_held = root / (out_name + "-fit"), root / (out_name + "-heldout")
    for d in (out_fit, out_held):
        if d.exists():
            shutil.rmtree(d)
    err = io.StringIO()
    codes = []
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
        codes.append(bytes_analyze.main(["--export", str(root / "export"), "--manifest", str(root / "manifest.json"),
                                         "--stage", "fit", "--out", str(out_fit)]))
        if codes[-1] == 0 and two_stage:
            codes.append(bytes_analyze.main(["--export", str(root / "export"), "--manifest", str(root / "manifest.json"),
                                             "--stage", "heldout", "--predictions", str(out_fit / "predictions.json"),
                                             "--out", str(out_held)]))
    return codes, err.getvalue().strip(), out_held


def table(out, name):
    return ba.read_json(out / (name + ".json"))


def words(out, selection="primary", basis="gross primary"):
    return {(r["boundary"], r["model"]): r["word"] for r in table(out, "h1")
            if r["selection"] == selection and r["basis"] == basis and r["role"] == "heldout" and r.get("pass_id", "mean") == "mean"}
