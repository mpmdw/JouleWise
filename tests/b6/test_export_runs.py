import contextlib
import csv
import io
import json
import math
import tempfile
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
                self.assertTrue(math.isclose(float(row["phase_decode_j"]), 10 * 1.1 * .99))
                self.assertTrue(math.isclose(float(row["idle_variance_of_mean_w2"]), 2 * (1.1 * .99) ** 2))

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
                    self.assertTrue(math.isclose(float(row["phase_decode_j"]), 10, rel_tol=1e-12))
                    self.assertTrue(math.isclose(float(row["idle_variance_of_mean_w2"]), 2, rel_tol=1e-12))
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
