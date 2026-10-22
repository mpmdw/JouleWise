import contextlib
import csv
import io
import json
import math
import shutil
import tempfile
import subprocess
import sys
import types
import hashlib
import unittest
from pathlib import Path
from unittest.mock import patch

from joulewise.b6 import blinding, export_runs
from scripts import b6_export_runs, b6_unblind
from tests.b6.support import registration_dir, write_json


def archive_fixture(root):
    archive = root / "archive"
    reg = registration_dir(root)
    plan = {"pack_id": "desk-pack", "session_id": "desk-session", "chain_exit_code": 0}
    members = []
    for index, (run, stage, role, model, condition, status) in enumerate([
        ("ref", "references", "start", "reference", "reference-key", "succeeded"),
        ("corpus", "references", "corpus", "reference", "reference-key", "succeeded"),
        *[(f"q{i}", "science", "science", "floor", "null-key", "succeeded") for i in range(4)],
        ("gamma-a", "science", "science", "model-a", "gamma-a", "succeeded"),
        ("gamma-b", "science", "science", "model-b", "gamma-b", "succeeded"),
        ("failed", "science", "science", "floor", "null-key", "failed"),
    ]):
        members.append({"run_id": run, "stage_id": stage, "role": role,
                        "units": [{"cell_id": "cell", "stratum": "repeat", "unit_id": run}]})
        bundle = archive / "sources/claim-runs" / run
        write_json(bundle / "metadata.json", {})
        write_json(bundle / "status.json", {"status": {"state": status}})
        tags = ["df-condition=" + condition]
        if run.startswith("q"):
            tags += ["calibration-abba-block-id=quad", "calibration-abba-label=" + "ABBA"[int(run[1:])]]
        write_json(bundle / "config.json", {"model": {"name": model},
                   "workload_profile": {"name": "desk", "output_tokens": 7}, "run_metadata": {"tags": tags}})
        events = [{"event_type": "run_started", "timestamp_s": 1791936000}]
        for i, phase in enumerate(export_runs.PHASES):
            events.extend([{"event_type": "phase_start", "phase": phase, "timestamp_s": i * 4},
                           {"event_type": "phase_end", "phase": phase, "timestamp_s": i * 4 + 2,
                            "metadata": {"prompt_tokens": 11} if phase == "tokenize" else
                            {"emitted_tokens": 7, "requested_output_tokens": 7} if phase == "decode" else {}}])
        (bundle / "events.jsonl").write_text("".join(json.dumps(event) + "\n" for event in events))
        write_json(archive / "withheld/reductions" / (run + ".summary_metrics.rereduced.json"), {
            "phase_energy_j": dict.fromkeys(export_runs.PHASES, 10), "gross_energy_j": 40,
            "idle_subtracted_energy_j": 30, "energy_request_j": 30,
            "energy_bound_terms_j": {term + "_j": 2 for term in export_runs.BOUND_TERMS},
            "idle_baseline": {"duration_s": 60, "power_w_mean": 3},
            "idle_mean_uncertainty": {"governed_variance_of_mean_w2": 2}, "ttft_s": .25, "decode_latency_s": .1})
    write_json(archive / "sources/pack/plan_tree.json", {"science": [m for m in members if m["role"] == "science"], "stage_graph": [
        {"stage_id": "references", "kind": "campaign_collection", "expected_count": 2},
        {"stage_id": "science", "kind": "campaign_collection", "expected_count": 7}]})
    # Intentionally store the roster backwards; the stage walk sets export order.
    write_json(archive / "derived/roster.json", {"pack_id": "desk-pack", "attempt": 2,
        "members": list(reversed(members)), "cells": [{"cell_id": "cell", "strata": ["repeat"]}]})
    write_json(archive / "derived/code-identity.json", {"executed_head": None})
    (archive / "derived/flags.jsonl").write_text("")
    write_json(archive / "withheld/spans.json", {"spans": {}})
    record = {"pack_id": "desk-pack", "session_id": "desk-session", "verdict": "EXCLUDE", "counting": False,
        "flag_counts": {"member.status_not_succeeded": 1}, "excluding": [
            {"scope": "member", "run_id": "failed", "code": "member.status_not_succeeded"}],
        "emitted_flags": [], "calibration": {"operative_bound_s": "0.05"}, "neg8": {"corpus_clean_n": 1}}
    write_json(archive / "derived/b6-acceptance.json", record)
    write_json(root / "plan.json", plan)
    return archive, reg, plan, record


class ExportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.archive, self.reg, self.plan, self.record = archive_fixture(self.root)

    def export(self, **kwargs):
        return export_runs.export(self.archive, self.plan, self.reg, self.root / "packs", self.root / "out", **kwargs)

    def rows(self, result):
        with result.csv_path.open() as stream:
            return list(csv.DictReader(stream))

    def test_replication_csv_and_sidecar_bytes_equal_verified_base(self):
        # Bit identity is the registered property for alpha/beta/gamma. Execute
        # B1's actual exporter against the same fixture and stored factors.
        source = subprocess.run(["git", "show", "d924e7acf:joulewise/b6/export_runs.py"],
                                capture_output=True, text=True, check=True).stdout
        legacy = types.ModuleType("_b4_legacy_export")
        sys.modules[legacy.__name__] = legacy
        self.addCleanup(sys.modules.pop, legacy.__name__)
        exec(compile(source, "<B1-export>", "exec"), legacy.__dict__)
        for pack in ("alpha", "beta", "gamma"):
            self.record["pack_id"] = self.plan["pack_id"] = pack
            before = legacy.export(self.archive, self.plan, self.reg, self.root / "packs", self.root / "out",
                                   acceptance_record=self.record)
            expected = (before.csv_path.read_bytes(), before.sidecar_path.read_bytes())
            after = self.export(acceptance_record=self.record)
            self.assertEqual((after.csv_path.read_bytes(), after.sidecar_path.read_bytes()), expected)

    def test_group_withholds_offset_rows_and_only_publishes_counts_and_key_digests(self):
        # Four null runs are the registered fit model; gamma configurations
        # and the absent/failed model are held out by default.
        for run in ("q0", "q1", "q2", "q3"):
            path = self.archive / "sources/claim-runs" / run / "config.json"
            config = json.loads(path.read_text())
            config["model"]["name"] = "Qwen3-4B-4bit"
            write_json(path, config)
        write_json(self.archive / "sources/pack/registration.json", {"blinding_group": "bytes", "bytes_pass": 1})
        result = self.export()
        rows = self.rows(result)
        self.assertEqual({r["run_id"] for r in rows}, {"ref", "corpus", "q0", "q1", "q2", "q3"})
        self.assertNotIn("run_start_utc", rows[0])
        self.assertEqual({r["pass_id"] for r in rows}, {"1"})
        sidecar = json.loads(result.sidecar_path.read_text())
        info = sidecar["blinding"]["withheld"]
        self.assertEqual(set(info), {"path", "row_count", "config_key_sha256"})
        self.assertEqual(info["row_count"], 3)
        store = (result.csv_path.parent / info["path"]).resolve()
        self.assertTrue(store.is_relative_to(self.root / "packs/bytes"))
        with store.open() as stream:
            withheld = list(csv.DictReader(stream))
        self.assertEqual({r["run_id"] for r in withheld}, {"gamma-a", "gamma-b", "failed"})
        self.assertEqual(sum(info["config_key_sha256"].values()), len(withheld))
        for row in withheld:
            digest = hashlib.sha256(row["config_key"].encode()).hexdigest()
            self.assertIn(digest, info["config_key_sha256"])
            self.assertNotIn("run_start_utc", row)
            if row["status"] == "succeeded":
                factor = blinding.stored_factor(self.root / "packs/bytes/blinding", row["config_key"])
                # No printed half-width: COMMON's 1e-6 relative (absolute J near zero),
                # above 1e6 x double noise: 2.2e-16 x 1e6 = 2.2e-10 relative.
                self.assertTrue(math.isclose(float(row["phase_decode_j"]) / factor, 10, rel_tol=1e-6, abs_tol=1e-6))
        # Re-export uses the same keys and row bytes, rather than a fresh draw.
        before = store.read_bytes()
        self.export(pack_registration={"blinding_group": "bytes", "bytes_pass": 1})
        self.assertEqual(store.read_bytes(), before)

    def test_group_non_claim_smoke_still_withholds_and_blinds(self):
        result = self.export(non_claim=True, pack_registration={"blinding_group": "bytes", "bytes_pass": 1})
        rows = self.rows(result)
        self.assertEqual({r["run_id"] for r in rows}, {"ref", "corpus"})
        self.assertNotIn("run_start_utc", rows[0])
        self.assertNotIn("non_claim", rows[0])
        sidecar = json.loads(result.sidecar_path.read_text())
        self.assertTrue(sidecar["non_claim"])
        self.assertTrue(sidecar["blinding"]["applied"])
        self.assertEqual(sidecar["blinding"]["withheld"]["row_count"], 7)
        # Unchanged release reader divides the offsets even though the session
        # is explicitly non-claim in its sidecar.
        from joulewise.bytes_analysis import _released_rows
        released = _released_rows(rows, self.root / "packs/bytes/blinding", blinded=False)
        for row in released:
            # No printed half-width: 1e-6 relative / absolute J near zero;
            # above 1e6 x 2.2e-16 = 2.2e-10 relative double noise.
            self.assertTrue(math.isclose(row["phase_decode_j"], 10, rel_tol=1e-6, abs_tol=1e-6))

    def test_group_unblind_uses_registered_order_and_flags_missing_store(self):
        result = self.export(pack_registration={"blinding_group": "bytes", "bytes_pass": 1})
        args = ["--export", str(result.csv_path), "--pack-records-root", str(self.root / "packs"),
                "--blinding-group", "bytes"]
        precommit = self.root / "precommit.csv"
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(b6_unblind.main(args + ["--out", str(precommit)]), 0)
        with precommit.open() as stream:
            self.assertEqual({r["run_id"] for r in csv.DictReader(stream)}, {"ref", "corpus"})
        released = self.root / "released.csv"
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(b6_unblind.main(args + ["--stage1-commit", "a" * 40, "--out", str(released)]), 0)
        with released.open() as stream:
            rows = list(csv.DictReader(stream))
        # Registered plan: two references, four quads, two gamma rows, one failed.
        self.assertEqual([r["run_id"] for r in rows], ["corpus", "ref", "q0", "q1", "q2", "q3", "gamma-a", "gamma-b", "failed"])
        for row in rows:
            if row["status"] == "succeeded":
                # No printed half-width: 1e-6 relative / absolute J near zero;
                # above 1e6 x 2.2e-16 = 2.2e-10 relative double noise.
                self.assertTrue(math.isclose(float(row["phase_decode_j"]), 10, rel_tol=1e-6, abs_tol=1e-6))
        info = json.loads(result.sidecar_path.read_text())["blinding"]["withheld"]
        (result.csv_path.parent / info["path"]).unlink()
        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            self.assertEqual(b6_unblind.main(args + ["--stage1-commit", "a" * 40,
                                                    "--out", str(self.root / "missing.csv")]), 0)
        self.assertEqual(json.loads(stdout.getvalue())["flags"], ["bytes.withheld_missing"])

    def test_rows_energies_tokens_durations_and_failed_run(self):
        with patch.object(blinding, "_draw", side_effect=lambda bounds: 1.1 if bounds == blinding.PACK_RANGE else .99):
            result = self.export()
        rows = self.rows(result)
        self.assertEqual(len(rows), 9)
        self.assertEqual([row["stage_id"] for row in rows[:2]], ["references"] * 2)
        self.assertEqual([row["run_id"] for row in rows[2:]], ["q0", "q1", "q2", "q3", "gamma-a", "gamma-b", "failed"])
        self.assertEqual({row["run_id"] for row in rows}, {m["run_id"] for m in json.loads((self.archive / "derived/roster.json").read_text())["members"]})
        for row in rows:
            self.assertEqual(row["prompt_tokens"], "11")
            self.assertEqual(row["emitted_tokens"], "7")
            self.assertEqual(row["dur_prefill_s"], "2")
            self.assertEqual(row["idle_baseline_s"], "60")
            self.assertTrue(row["run_start_utc"].endswith("+00:00"))
            if row["status"] == "failed":
                self.assertTrue(all(row[key] == "" for key in export_runs.ENERGIES))
                self.assertEqual(row["excluded"], "True")
            else:
                # No printed half-width: COMMON 1e-6 relative / absolute J or W2
                # near zero, above 1e6 x 2.2e-16 = 2.2e-10 relative double noise.
                self.assertTrue(math.isclose(float(row["phase_decode_j"]), 10 * 1.1 * .99, rel_tol=1e-6, abs_tol=1e-6))
                self.assertTrue(math.isclose(float(row["idle_variance_of_mean_w2"]), 2 * (1.1 * .99) ** 2, rel_tol=1e-6, abs_tol=1e-6))

    def test_null_quads_and_references_share_offsets_gamma_models_do_not(self):
        draws = iter([1.1, .99, .98, 1.02, 1.01])
        with patch.object(blinding, "_draw", side_effect=lambda _bounds: next(draws)):
            rows = self.rows(self.export())
        quads = [row for row in rows if row["run_id"].startswith("q")]
        self.assertEqual(len({row["phase_decode_j"] for row in quads}), 1)
        refs = [row for row in rows if row["role"] in ("start", "corpus")]
        self.assertEqual(len({row["phase_decode_j"] for row in refs}), 1)
        gamma = [row for row in rows if row["run_id"].startswith("gamma")]
        self.assertNotEqual(gamma[0]["phase_decode_j"], gamma[1]["phase_decode_j"])

    def test_two_sessions_reference_key_ignores_first_missing_bundle(self):
        first = self.rows(self.export())
        archive, reg, plan, record = archive_fixture(self.root / "second")
        shutil.rmtree(archive / "sources/claim-runs/corpus")
        record["session_id"] = plan["session_id"] = "second-session"
        second = self.rows(export_runs.export(archive, plan, reg, self.root / "packs", self.root / "out",
                                             acceptance_record=record))
        refs = [row for row in first + second if row["run_id"] == "ref"]
        self.assertEqual(len(refs), 2)
        self.assertEqual({row["config_key"] for row in refs}, {export_runs.REFERENCE_KEY})
        # Exact serialization: identical energies and the identical stored reference factor.
        self.assertEqual(refs[0]["gross_energy_j"], refs[1]["gross_energy_j"])
        self.assertEqual(next(row for row in second if row["run_id"] == "corpus")["config_key"], export_runs.REFERENCE_KEY)

    def test_unblind_missing_key_fault_names_file_without_writing(self):
        result = self.export()
        key_dir = self.root / "wrong-empty-keys"
        output = self.root / "unblinded.csv"
        for missing in ("pack", "config"):
            if missing == "config":
                key_dir.mkdir()
                (key_dir / "pack.json").write_text('{"factor":1.11713}')
            before = {p.name: p.read_bytes() for p in key_dir.iterdir()} if key_dir.exists() else {}
            with contextlib.redirect_stdout(io.StringIO()) as stdout, contextlib.redirect_stderr(io.StringIO()) as stderr:
                self.assertEqual(b6_unblind.main(["--export", str(result.csv_path), "--key-dir", str(key_dir),
                                                "--out", str(output)]), 1)
            self.assertEqual(stdout.getvalue(), "")
            self.assertIn(str(key_dir / ("pack.json" if missing == "pack" else "config-")), stderr.getvalue())
            self.assertNotIn("1.11713", stderr.getvalue())
            self.assertFalse(output.exists())
            after = {p.name: p.read_bytes() for p in key_dir.iterdir()} if key_dir.exists() else {}
            self.assertEqual(before, after)

    def test_corrupt_export_key_fault_is_bounded_and_names_file(self):
        key = self.root / "packs/desk-pack/blinding/pack.json"
        key.parent.mkdir(parents=True)
        key.write_text("")
        argv = ["--archive", str(self.archive), "--plan", str(self.root / "plan.json"),
                "--registration-dir", str(self.reg), "--pack-records-root", str(self.root / "packs"),
                "--export-dir", str(self.root / "out")]
        with patch.object(blinding, "DECODE_RETRY_TIMEOUT_S", .01), \
             contextlib.redirect_stdout(io.StringIO()) as stdout, contextlib.redirect_stderr(io.StringIO()) as stderr:
            self.assertEqual(b6_export_runs.main(argv), 5)
        self.assertEqual(stdout.getvalue(), "")
        self.assertIn(str(key), stderr.getvalue())
        self.assertEqual(key.read_text(), "")
        self.assertFalse((self.root / "out").exists())

    def test_csv_sidecar_stdout_hide_offset_and_unblind_round_trips(self):
        argv = ["--archive", str(self.archive), "--plan", str(self.root / "plan.json"),
                "--registration-dir", str(self.reg), "--pack-records-root", str(self.root / "packs"),
                "--export-dir", str(self.root / "out")]
        with patch.object(blinding, "_draw", side_effect=lambda bounds: 1.11713 if bounds == blinding.PACK_RANGE else .99437), \
             contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(b6_export_runs.main(argv), 0)
        result = json.loads(out.getvalue())
        payload = Path(result["csv"]).read_text() + Path(result["session"]).read_text() + out.getvalue()
        self.assertTrue(all(repr(value) not in payload for value in (1.11713, .99437, 1.11713 * .99437)), "offset leaked")
        unblinded = self.root / "unblinded.csv"
        with contextlib.redirect_stdout(io.StringIO()) as unblind_stdout:
            self.assertEqual(b6_unblind.main(["--export", result["csv"], "--key-dir",
                str(self.root / "packs/desk-pack/blinding"), "--out", str(unblinded)]), 0)
        self.assertTrue(all(repr(value) not in unblind_stdout.getvalue() for value in (1.11713, .99437)), "offset leaked")
        with unblinded.open() as stream:
            for row in csv.DictReader(stream):
                if row["status"] == "succeeded":
                    # No printed half-width: 1e-6 relative / absolute J or W2 near
                    # zero; above 1e6 x 2.2e-16 = 2.2e-10 relative double noise.
                    self.assertTrue(math.isclose(float(row["phase_decode_j"]), 10, rel_tol=1e-6, abs_tol=1e-6))
                    self.assertTrue(math.isclose(float(row["idle_variance_of_mean_w2"]), 2, rel_tol=1e-6, abs_tol=1e-6))
        sidecar = json.loads(Path(result["session"]).read_text())
        self.assertEqual(sidecar["blinding"]["applied"], True)
        self.assertFalse(Path(sidecar["blinding"]["key_dir"]).is_absolute())

    def test_non_claim_has_no_key_draw_and_reexport_replaces(self):
        with patch.object(blinding, "factor", side_effect=AssertionError("non-claim drew offset")):
            result = self.export(non_claim=True)
            self.export(non_claim=True)
        self.assertFalse((self.root / "packs").exists())
        self.assertTrue(all(row["non_claim"] == "True" for row in self.rows(result)))
        self.assertEqual(json.loads(result.sidecar_path.read_text())["blinding"]["applied"], False)
