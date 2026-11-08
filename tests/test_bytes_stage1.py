"""BYTES stage 1 driver (scripts/bytes_stage1.py) on a synthetic, production-shaped campaign.

Synthetic data only: the R6 twelve-sub-pack campaign of tests/fixtures/bytes/campaign.py,
exported through the real block-6 exporter with grouped blinding and withheld stores.
"""
from __future__ import annotations

import csv
import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from joulewise import bytes_analysis as ba
from joulewise.b6 import blinding
from scripts import bytes_stage1 as s1
from tests.desk_restore_support import ample_space_command

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests/fixtures/bytes"
_spec = importlib.util.spec_from_file_location("bytes_campaign_stage1", FIXTURES / "campaign.py")
_campaign = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_campaign)

WORK = {}


def setUpModule():
    WORK["dir"] = tempfile.TemporaryDirectory(prefix="bytes-stage1-")
    root = Path(WORK["dir"].name) / "campaign"
    manifest = _campaign.archive_campaign(root, non_claim=False, release="none", subpack_sessions=True)
    (root / "manifest.json").write_text(json.dumps(manifest) + "\n")
    WORK.update(root=root, manifest=manifest)


def tearDownModule():
    WORK["dir"].cleanup()


def copy_export(name):
    target = Path(WORK["dir"].name) / name
    shutil.copytree(WORK["root"] / "export", target / "export", symlinks=True)
    # Keep each sidecar's relative withheld locator valid beside the copy.
    shutil.copytree(WORK["root"] / "private-keys", target / "private-keys", symlinks=True)
    return target / "export"


def rewrite_csv(path, edit):
    with path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        header, rows = list(reader.fieldnames), list(reader)
    header, rows = edit(header, rows)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=header)
        writer.writeheader()
        writer.writerows(rows)


def fit_release(root):
    """The synthetic configurations are not registered packs, so release by verbatim copy,
    as tests/test_bytes_agreement.py run_both does; the CLI uses b6_release_subset.release."""
    private = root / "private-keys/bytes/blinding"

    def release(_pack_records_root, keys, out):
        out.mkdir(parents=True)
        for name in sorted({"pack.json", *(blinding._config_filename(k) for k in keys)}):
            shutil.copyfile(private / name, out / name)
        return {"stage": "fit", "keys": keys}
    return release


class CensusTests(unittest.TestCase):
    def test_clean_export_passes_and_reads_no_energy(self):
        record, reasons = s1.census([WORK["root"] / "export"])
        self.assertEqual(reasons, [])
        self.assertEqual(record["verdict"], "OK")
        self.assertEqual(sorted(s["pack_id"] for s in record["sessions"]), sorted(s1.PACKS))
        visible = {m for s in record["sessions"] for m in s["visible_science_models"]}
        self.assertTrue(visible <= blinding.FIT_MODELS)
        self.assertEqual(visible, set(blinding.FIT_MODELS))
        self.assertTrue(all(s["withheld_store_present"] for s in record["sessions"]))
        printed = json.dumps(record)
        for column in ("phase_decode_j", "idle_power_w", "dur_decode_s", "gross_energy_j"):
            self.assertNotIn(column, printed)

    def test_visible_heldout_row_refuses(self):
        export = copy_export("heldout-visible")
        table = next(export.rglob("bytes-s1-p1.runs.csv"))

        def plant(header, rows):
            science = next(r for r in rows if r["role"] == "science")
            rows.append({**science, "run_id": "planted", "model_name": "Qwen3-32B-4bit"})
            return header, rows
        rewrite_csv(table, plant)
        record, reasons = s1.census([export])
        self.assertEqual(record["verdict"], "REFUSED")
        self.assertTrue(any("held-out row" in r and "bytes-s1-p1" in r for r in reasons), reasons)

    def test_clock_column_and_missing_session_refuse(self):
        export = copy_export("clock-and-missing")
        rewrite_csv(next(export.rglob("bytes-s2-p2.runs.csv")),
                    lambda header, rows: (header + ["run_start_utc"], [{**r, "run_start_utc": "x"} for r in rows]))
        for path in export.rglob("bytes-s6-p1.*"):
            path.unlink()
        _record, reasons = s1.census([export])
        self.assertTrue(any("clock column" in r for r in reasons), reasons)
        self.assertTrue(any(r == "no session for: bytes-s6-p1" for r in reasons), reasons)

    def test_missing_withheld_store_is_reported(self):
        export = copy_export("withheld-missing")
        sidecar = next(export.rglob("bytes-s3-p1.session.json"))
        locator = json.loads(sidecar.read_text())["blinding"]["withheld"]["path"]
        (sidecar.parent / locator).unlink()
        record, reasons = s1.census([export])
        self.assertTrue(any("withheld store missing" in r for r in reasons), reasons)
        row = next(s for s in record["sessions"] if s["session_id"] == "bytes-s3-p1")
        self.assertFalse(row["withheld_store_present"])


class ManifestTests(unittest.TestCase):
    def test_registered_models_plus_twelve_sessions_in_pass_order(self):
        sessions = [(s["session_id"], s["archive"], WORK["root"] / "export") for s in WORK["manifest"]["sessions"]]
        manifest = s1.build_manifest(list(reversed(sessions)))
        registered = json.loads((ROOT / "configs/bytes/bytes_manifest.json").read_text())
        self.assertEqual(manifest["models"], registered["models"])
        self.assertNotIn("synthetic", manifest)
        self.assertEqual([(s["pass_id"], s["pack_id"]) for s in manifest["sessions"]],
                         [(int(p[-1]), p) for p in s1.PACKS])
        self.assertTrue(all(s["test7_passed"] is False for s in manifest["sessions"]))
        ba.validate_manifest(manifest)

    def test_archive_and_export_must_name_the_same_session(self):
        sessions = [(s["session_id"], s["archive"], WORK["root"] / "export") for s in WORK["manifest"]["sessions"]]
        swapped = [(sessions[0][0], sessions[1][1], sessions[0][2])] + sessions[1:]
        with self.assertRaisesRegex(s1.Stage1Error, "archive acceptance names"):
            s1.build_manifest(swapped)
        with self.assertRaisesRegex(s1.Stage1Error, "exactly one session"):
            s1.build_manifest(sessions[:-1])


class RunTests(unittest.TestCase):
    def test_pre_commit_sequence_writes_agreeing_predictions(self):
        root = WORK["root"]
        out = Path(WORK["dir"].name) / "stage1-run"
        code, summary = s1.run_stage1(root / "manifest.json", [root / "export"], root / "private-keys", out,
                                      release_fn=fit_release(root), wrap=ample_space_command)
        self.assertEqual((code, summary["verdict"]), (0, "READY_TO_COMMIT"), json.dumps(summary, indent=1))
        exits = summary["exits"]
        self.assertEqual((exits["a-blinded"], exits["t-blinded"], exits["a-fit"], exits["t-1"]), (0, 0, 0, 0))
        self.assertNotEqual(exits["a-fit-nokeys"], 0)
        self.assertNotEqual(exits["t-1-nokeys"], 0)
        for stage in ("blinded_agreement", "stage1_agreement"):
            self.assertEqual(summary[stage]["above_bar"], 0, summary[stage]["above_bar_fields"])
            self.assertGreater(summary[stage]["compared"], 0)
        predictions = out / "out/a-fit/predictions.json"
        self.assertEqual(summary["predictions_sha256"], s1.sha256_file(predictions))
        frozen = json.loads(predictions.read_text())
        self.assertEqual(frozen["bytes_analysis_sha256"], s1.REGISTERED_ESTIMATOR_SHA256)
        self.assertEqual(frozen["manifest_sha256"], summary["manifest_sha256"])
        self.assertEqual(sorted(summary["release"]["keys"]), sorted(
            {"neg8_reference", *(m["config_key"] for m in WORK["manifest"]["models"] if m["role"] == "fit")}))
        # Nothing held out was produced or released before the commitment.
        self.assertFalse(any((out / "out").glob("a-held*")))
        self.assertFalse(any((out / "out").glob("t-2*")))
        self.assertTrue(json.loads((out / "stage1-summary.json").read_text())["verdict"] == "READY_TO_COMMIT")

    def test_refuses_existing_output_and_unregistered_estimator(self):
        root = WORK["root"]
        existing = Path(WORK["dir"].name) / "exists"
        existing.mkdir()
        with self.assertRaisesRegex(s1.Stage1Error, "new directory"):
            s1.run_stage1(root / "manifest.json", [root / "export"], root / "private-keys", existing)
        original = s1.REGISTERED_ESTIMATOR_SHA256
        s1.REGISTERED_ESTIMATOR_SHA256 = "0" * 64
        try:
            with self.assertRaisesRegex(s1.Stage1Error, "not the registered"):
                s1.run_stage1(root / "manifest.json", [root / "export"], root / "private-keys",
                              Path(WORK["dir"].name) / "never")
        finally:
            s1.REGISTERED_ESTIMATOR_SHA256 = original
        self.assertFalse((Path(WORK["dir"].name) / "never").exists())

    def test_registered_estimator_digest_matches_registration(self):
        self.assertEqual(s1.sha256_file(ROOT / "joulewise/bytes_analysis.py"), s1.REGISTERED_ESTIMATOR_SHA256)
        text = (ROOT / "docs/registrations/bytes_pack_v1.md").read_text(encoding="utf-8")
        self.assertIn(s1.REGISTERED_ESTIMATOR_SHA256, text)


if __name__ == "__main__":
    unittest.main()
