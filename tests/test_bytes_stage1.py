"""BYTES stage 1 driver (scripts/bytes_stage1.py) on a synthetic, production-shaped campaign.

Synthetic data only: the R6 twelve-sub-pack campaign of tests/fixtures/bytes/campaign.py,
exported through the real block-6 exporter with grouped blinding and withheld stores.
"""
from __future__ import annotations

import csv
import importlib.util
import contextlib
import io
import json
import os
import pathlib
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

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

    def test_missing_withheld_store_is_a_flag_not_a_refusal(self):
        # Registration section 11 item 4: a missing withheld file is never a refusal.
        export = copy_export("withheld-missing")
        sidecar = next(export.rglob("bytes-s3-p1.session.json"))
        locator = json.loads(sidecar.read_text())["blinding"]["withheld"]["path"]
        (sidecar.parent / locator).unlink()
        record, reasons = s1.census([export])
        self.assertEqual(reasons, [])
        self.assertEqual(record["verdict"], "OK")
        self.assertTrue(any("bytes.withheld_missing" in w and "bytes-s3-p1" in w for w in record["warnings"]),
                        record["warnings"])
        row = next(s for s in record["sessions"] if s["session_id"] == "bytes-s3-p1")
        self.assertFalse(row["withheld_store_present"])

    def test_heldout_config_key_under_a_fit_model_name_refuses(self):
        # Review of #701, F1: the model_name column alone must not decide.
        export = copy_export("heldout-config-key")
        table = next(export.rglob("bytes-s1-p1.runs.csv"))

        def plant(header, rows):
            science = next(r for r in rows if r["role"] == "science")
            rows.append({**science, "run_id": "planted-key",
                         "config_key": "Qwen3-32B-4bit|bytes_synthetic_2048_decode_512|512"})
            return header, rows
        rewrite_csv(table, plant)
        _record, reasons = s1.census([export])
        self.assertTrue(any("held-out row" in r and "bytes-s1-p1" in r for r in reasons), reasons)

    def test_withheld_layout_store_under_the_export_root_is_never_opened(self):
        # Review of #701, F2: withheld/<pack_id>/<session_id>.runs.csv, parent is the pack id.
        export = copy_export("withheld-layout")
        table = next(export.rglob("bytes-s1-p1.runs.csv"))
        store = export / "withheld" / "bytes-s1-p1" / table.name
        store.parent.mkdir(parents=True)
        shutil.copyfile(table, store)
        table.unlink()
        opened = []
        real_open = pathlib.Path.open

        def spy(self, *args, **kwargs):
            opened.append(str(self))
            return real_open(self, *args, **kwargs)
        with mock.patch.object(pathlib.Path, "open", spy):
            _record, reasons = s1.census([export])
        self.assertEqual([p for p in opened if "/withheld/" in p], [])
        self.assertTrue(any("bytes-s1-p1" in r and "needs both" in r for r in reasons), reasons)

    def test_any_clock_like_column_refuses_and_durations_do_not(self):
        # Review of #701, F3: registration section 11 item 2, "run_start_utc or any other clock".
        for name in ("run_end_utc", "recorded_at_utc", "event_timestamp", "wall_time", "epoch_s"):
            with self.subTest(column=name):
                export = copy_export("clock-" + name)
                rewrite_csv(next(export.rglob("bytes-s2-p2.runs.csv")),
                            lambda header, rows, name=name: (header + [name], [{**r, name: "x"} for r in rows]))
                _record, reasons = s1.census([export])
                self.assertTrue(any("clock column" in r and name in r for r in reasons), reasons)
        self.assertEqual(s1.clock_columns(["dur_decode_s", "ttft_s", "idle_baseline_s",
                                           "bound_E_clock_anchor_shift_bound_j", "abba_label"]), [])


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


class CommandLineTests(unittest.TestCase):
    """The commands the plan's magistrate steps paste (census, manifest), through main()."""

    def test_census_and_manifest_commands(self):
        import contextlib
        import io
        root = WORK["root"]
        out = Path(WORK["dir"].name) / "cli"
        out.mkdir()
        with contextlib.redirect_stdout(io.StringIO()) as printed:
            self.assertEqual(s1.main(["census", "--export", str(root / "export"), "--out", str(out / "census.json")]), 0)
        self.assertEqual(json.loads((out / "census.json").read_text())["verdict"], "OK")
        self.assertIn('"verdict": "OK"', printed.getvalue())
        argv = ["manifest", "--out", str(out / "manifest.json")]
        for session in WORK["manifest"]["sessions"]:
            argv += ["--session", f"{session['session_id']}={session['archive']}:{root / 'export'}"]
        with contextlib.redirect_stdout(io.StringIO()) as printed:
            self.assertEqual(s1.main(argv), 0)
        manifest = json.loads((out / "manifest.json").read_text())
        self.assertEqual(len(manifest["sessions"]), 12)
        self.assertEqual(json.loads(printed.getvalue())["sha256"], ba.digest(manifest))
        with contextlib.redirect_stderr(io.StringIO()) as error:
            self.assertEqual(s1.main(argv), 1)   # never overwrites
        self.assertIn("exists", error.getvalue())


class RunTests(unittest.TestCase):
    def test_pre_commit_sequence_writes_agreeing_predictions(self):
        root = WORK["root"]
        out = Path(WORK["dir"].name) / "stage1-run"
        code, summary = s1.run_stage1(root / "manifest.json", [root / "export"], root / "private-keys", out,
                                      release_fn=fit_release(root), wrap=ample_space_command,
                                      check_registered_models=False)
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

    def test_missing_withheld_store_does_not_stop_run_and_is_recorded(self):
        # Review of #701, F4: the CLI run continues; the summary carries the flag.
        export = copy_export("run-withheld-missing")
        sidecar = next(export.rglob("bytes-s3-p1.session.json"))
        (sidecar.parent / json.loads(sidecar.read_text())["blinding"]["withheld"]["path"]).unlink()
        seen = {}

        def fake_run(manifest, exports, records, out, **kwargs):
            seen.update(kwargs)
            return 0, {"verdict": "READY_TO_COMMIT", "exit": 0}
        out = Path(WORK["dir"].name) / "run-withheld-out"
        with mock.patch.object(s1, "run_stage1", fake_run), contextlib.redirect_stdout(io.StringIO()):
            rc = s1.main(["run", "--manifest", "m.json", "--export", str(export),
                          "--pack-records-root", "x", "--out", str(out)])
        self.assertEqual(rc, 0)
        self.assertTrue(any("bytes.withheld_missing" in w for w in seen["census_warnings"]), seen)

    def test_manifest_models_and_sessions_are_checked_against_the_registration_and_census(self):
        # Review of #701, LOW: relabelled models, or sessions the census did not see, stop the run.
        root = WORK["root"]
        registered = json.loads((ROOT / "configs/bytes/bytes_manifest.json").read_text())
        sessions = [(s["session_id"], s["archive"], root / "export") for s in WORK["manifest"]["sessions"]]
        manifest = s1.build_manifest(sessions)
        path = Path(WORK["dir"].name) / "reg-manifest.json"
        path.write_text(json.dumps(manifest))
        census_ids = [s["session_id"] for s in manifest["sessions"]]
        with self.assertRaisesRegex(s1.Stage1Error, "manifest sessions differ"):
            s1.run_stage1(path, [root / "export"], root / "private-keys", Path(WORK["dir"].name) / "r-sess",
                          census_sessions=census_ids[:-1])
        swapped = json.loads(json.dumps(manifest))
        for model in swapped["models"]:
            if model["model"] == "Qwen3-14B-4bit":
                model["role"] = "fit"
            elif model["model"] == "Qwen3-1.7B-4bit":
                model["role"] = "heldout"
        swapped_path = Path(WORK["dir"].name) / "swapped-manifest.json"
        swapped_path.write_text(json.dumps(swapped))
        ba.validate_manifest(swapped)   # the relabelling passes validate_manifest alone
        with self.assertRaisesRegex(s1.Stage1Error, "manifest models differ"):
            s1.run_stage1(swapped_path, [root / "export"], root / "private-keys", Path(WORK["dir"].name) / "r-model")
        self.assertEqual(manifest["models"], registered["models"])

    def test_summary_is_written_when_the_comparer_raises(self):
        # Review of #701, LOW: a raising comparer must not lose the record.
        root = WORK["root"]
        out = Path(WORK["dir"].name) / "comparer-raises"
        import tests.test_bytes_agreement as agreement

        def boom(_root):
            raise RuntimeError("comparer exploded")
        with mock.patch.object(agreement, "compare_campaign", boom):
            with self.assertRaisesRegex(RuntimeError, "comparer exploded"):
                s1.run_stage1(root / "manifest.json", [root / "export"], root / "private-keys", out,
                              release_fn=fit_release(root), wrap=ample_space_command,
                              check_registered_models=False)
        summary = json.loads((out / "stage1-summary.json").read_text())
        self.assertEqual(summary["verdict"], "ABORTED_ON_ERROR")
        self.assertIn("comparer exploded", summary["error"])
        self.assertFalse((out / "released-keys").exists())

    def test_registered_estimator_digest_matches_registration(self):
        self.assertEqual(s1.sha256_file(ROOT / "joulewise/bytes_analysis.py"), s1.REGISTERED_ESTIMATOR_SHA256)
        text = (ROOT / "docs/registrations/bytes_pack_v1.md").read_text(encoding="utf-8")
        self.assertIn(s1.REGISTERED_ESTIMATOR_SHA256, text)


class ReleaseGateTests(unittest.TestCase):
    """Execution faults must never authorize the first fit-key release."""

    def simulate(self, *, exits=None, faults=None, products=True, substantive=True, fit_products=True, actual_comparer=False):
        from tests.test_bytes_agreement import Recorder, compare_campaign
        import subprocess
        exits, faults = exits or {}, faults or {}
        temp = tempfile.TemporaryDirectory(prefix="bytes-release-gate-")
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        manifest = json.loads((ROOT / "configs/bytes/bytes_manifest.json").read_text())
        manifest["sessions"] = [{"session_id": p, "pack_id": p, "pass_id": int(p[-1]),
                                 "archive": str(root / p)} for p in s1.PACKS]
        path = root / "manifest.json"
        path.write_text(json.dumps(manifest))
        released = []
        fit_key = next(m["config_key"] for m in manifest["models"] if m["role"] == "fit")

        def child(command, **kwargs):
            out = Path(command[command.index("--out") + 1])
            tag = out.name.removesuffix(".json")
            stdout, stderr = "", ""
            if tag == "a-fit-nokeys":
                stderr = "BYTES analysis refused: configuration still blinded: " + fit_key + "\n"
            elif tag == "t-1-nokeys":
                stdout = "refused: blinding key missing or unreadable: " + str(root / "run/no-keys/pack.json") + "\n"
            elif products:
                if tag.startswith("a-"):
                    out.mkdir(parents=True)
                    names = (["blinded_pass_estimates", "model_estimates", "h1", "h2", "moe", "unavailable", "analysis_record"]
                             if tag == "a-blinded" else ["fit_pass_estimates", "predictions"])
                    for name in names:
                        if name == "fit_pass_estimates" and not fit_products:
                            continue
                        (out / (name + ".json")).write_text("[]\n")
                    if tag == "a-fit":
                        (out / "predictions.sha256").write_text(s1.sha256_file(out / "predictions.json") + "\n")
                else:
                    out.parent.mkdir(parents=True, exist_ok=True)
                    out.write_text("{}\n")
            stdout, stderr = faults.get(tag, (stdout, stderr))
            return subprocess.CompletedProcess(command, exits.get(tag, 1 if tag.endswith("nokeys") else 0), stdout, stderr)

        def comparer(_root):
            record = Recorder()
            if substantive:
                for stage in ("blinded", "fit"):
                    for group in ("cell/synthetic", "neg8/synthetic"):
                        record.exact(stage, group, "synthetic", 1, 1)
                record.exact("fit-commit", "commit/synthetic", "synthetic", 1, 1)
            return record

        def release(_root, keys, out):
            released.extend(keys)
            return {"stage": "fit", "keys": keys}

        with mock.patch.object(s1.subprocess, "run", side_effect=child), \
                mock.patch.object(s1, "_git_state", return_value=("synthetic", False)), \
                mock.patch("tests.test_bytes_agreement.compare_campaign", side_effect=compare_campaign if actual_comparer else comparer):
            result = s1.run_stage1(path, [root / "export"], root, root / "run", release_fn=release)
        return result, released

    def test_no_key_faults_stop_before_release(self):
        for exits, faults in [
            ({"t-1-nokeys": 2}, {}),
            ({"a-fit-nokeys": 2, "t-1-nokeys": 2}, {}),
            ({"a-fit-nokeys": -9}, {}),
            ({"a-fit-nokeys": 0}, {}),
            ({}, {"a-fit-nokeys": ("", "BYTES analysis refused: unrelated failure\n")}),
            ({}, {"t-1-nokeys": ("refused: unrelated failure\n", "")}),
            ({}, {"a-fit-nokeys": ("", "")}),
            ({}, {"t-1-nokeys": ("", "Traceback: synthetic\n")}),
        ]:
            with self.subTest(exits=exits, faults=faults):
                (code, summary), released = self.simulate(exits=exits, faults=faults)
                self.assertEqual(released, [], summary)
                self.assertNotEqual(code, 0)

    def test_missing_blinded_products_stop_before_release(self):
        (code, summary), released = self.simulate(products=False)
        self.assertEqual(released, [], summary)
        self.assertNotEqual(code, 0)

    def test_actual_comparer_cannot_admit_missing_blinded_products(self):
        (code, summary), released = self.simulate(products=False, actual_comparer=True)
        self.assertEqual(released, [], summary)
        self.assertNotEqual(code, 0)

    def test_exit_only_agreement_stops_before_release(self):
        (code, summary), released = self.simulate(substantive=False)
        self.assertEqual(released, [], summary)
        self.assertNotEqual(code, 0)

    def test_missing_fit_products_cannot_be_ready_to_commit(self):
        (code, summary), released = self.simulate(fit_products=False)
        self.assertTrue(released)
        self.assertNotEqual(summary["verdict"], "READY_TO_COMMIT")
        self.assertNotEqual(code, 0)

    def test_intended_missing_key_refusals_allow_fit_release(self):
        (code, summary), released = self.simulate()
        self.assertTrue(released)
        self.assertEqual((code, summary["verdict"]), (0, "READY_TO_COMMIT"))


if __name__ == "__main__":
    unittest.main()
