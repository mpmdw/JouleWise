import contextlib
import csv
import io
import json
import math
import os
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


def seal_reference_inputs(archive):
    paths = sorted(p for parent in (archive / "sources", archive / "withheld/reductions")
                   for p in parent.rglob("*") if p.is_file() and p.name != "SHA256SUMS")
    (archive / "sources/SHA256SUMS").write_text("".join(
        hashlib.sha256(p.read_bytes()).hexdigest() + "  "
        + (str(p.relative_to(archive / "sources")) if p.is_relative_to(archive / "sources")
           else "../" + str(p.relative_to(archive))) + "\n" for p in paths))
    write_json(archive / "harvest.json", {"outputs": {
        str(p.relative_to(archive)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted((archive / "derived").rglob("*"))
        if p.is_file() and p.name != "b6-acceptance.json"}})


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
        write_json(bundle / "metadata.json", {"device": {"telemetry": "mock", "rail_manifest": ["mock"]}})
        (bundle / "power_trace.csv").write_text("timestamp_s,power_w,rail,source\n" +
            "".join(f"{i},10,mock,mock\n" for i in range(21)))
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
    write_json(archive / "sources/pack/registration.json", {"pack_id": "desk-pack"})
    write_json(root / "plan.json", plan)
    seal_reference_inputs(archive)
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

    def test_bytes_reference_request_columns_integrate_interphase_gaps_and_unblind(self):
        for run in ("ref", "corpus"):
            bundle = self.archive / "sources/claim-runs" / run
            write_json(bundle / "metadata.json", {"device": {"telemetry": "mock", "rail_manifest": ["mock"]}})
            (bundle / "power_trace.csv").write_text(
                "timestamp_s,power_w,rail,source\n" +
                "".join(f"{i},10,mock,mock\n" for i in range(21)))
        result = self.export(pack_registration={"blinding_group": "bytes", "bytes_pass": 1})
        from joulewise.bytes_analysis import _released_rows
        released = _released_rows(self.rows(result), self.root / "packs/bytes/blinding", blinded=False)
        references = [r for r in released if r["role"] in ("start", "corpus")]
        self.assertEqual(len(references), 2)
        for row in references:
            # Four 2 s phases span 14 s, with three 2 s gaps. The old summary
            # columns remain the reducer's sampling-window values.
            self.assertAlmostEqual(row["gross_energy_j"], 40)
            self.assertAlmostEqual(row["reference_request_gross_j"], 140)
            self.assertAlmostEqual(row["reference_request_idle_subtracted_j"], 98)
            self.assertEqual(float(row["reference_request_duration_s"]), 14)

    def test_bytes_reference_without_request_inputs_is_disclosed(self):
        for run in ("ref", "corpus"):
            path = self.archive / "withheld/reductions" / (run + ".summary_metrics.rereduced.json")
            doc = json.loads(path.read_bytes())
            doc.pop("idle_baseline")
            write_json(path, doc)
        seal_reference_inputs(self.archive)
        result = self.export(pack_registration={"blinding_group": "bytes", "bytes_pass": 1})
        references = [r for r in self.rows(result) if r["role"] in ("start", "corpus")]
        self.assertEqual(len(references), 2)
        for row in references:
            self.assertTrue(all(row[key] == "" for key in export_runs.REFERENCE_REQUEST_COLUMNS))
            self.assertIn(export_runs.REFERENCE_UNAVAILABLE, row["flag_codes"])
        self.assertEqual(json.loads(result.sidecar_path.read_bytes())["flag_counts"][export_runs.REFERENCE_UNAVAILABLE], 2)

    def test_reference_storage_and_parse_errors_stop_export_with_cause(self):
        from joulewise.desk_restore import StorageStop
        bundle = self.archive / "sources/claim-runs/ref"
        trace = bundle / "power_trace.csv"
        original = trace.read_bytes()
        trace.write_text("timestamp_s,power_w,rail,source\nnot,a,number,x\n")
        with self.assertRaisesRegex(StorageStop, "reference bytes.*ref.*power_trace.csv.*digest mismatch"):
            self.export(pack_registration={"blinding_group": "bytes"})
        trace.unlink()
        with self.assertRaisesRegex(StorageStop, "power_trace.csv"):
            self.export(pack_registration={"blinding_group": "bytes"})
        trace.write_bytes(original)
        summary = self.archive / "withheld/reductions/ref.summary_metrics.rereduced.json"
        summary.write_text("bad summary bytes")
        with self.assertRaisesRegex(StorageStop, "reference bytes.*summary_metrics"):
            self.export(pack_registration={"blinding_group": "bytes"})

    def test_only_authenticated_registered_absences_are_disclosed(self):
        for absence in ("tokenize", "decode", "idle_baseline", "idle_null", "nonfinite_idle"):
            with self.subTest(absence=absence), tempfile.TemporaryDirectory() as tmp:
                archive, reg, plan, _ = archive_fixture(Path(tmp))
                if absence in ("tokenize", "decode"):
                    path = archive / "sources/claim-runs/ref/events.jsonl"
                    kind = "phase_start" if absence == "tokenize" else "phase_end"
                    events = [json.loads(line) for line in path.read_text().splitlines()]
                    path.write_text("".join(json.dumps(e) + "\n" for e in events
                                            if (e.get("phase"), e.get("event_type")) != (absence, kind)))
                else:
                    path = archive / "withheld/reductions/ref.summary_metrics.rereduced.json"
                    summary = json.loads(path.read_bytes())
                    if absence == "idle_baseline":
                        summary.pop("idle_baseline")
                    elif absence == "idle_null":
                        summary["idle_baseline"] = None
                    else:
                        summary["idle_baseline"]["power_w_mean"] = float("nan")
                    write_json(path, summary)
                args = (archive, plan, reg, Path(tmp) / "packs", Path(tmp) / "out")
                with self.assertRaisesRegex(export_runs.StorageStop, "digest mismatch"):
                    export_runs.export(*args, pack_registration={"blinding_group": "bytes"})
                seal_reference_inputs(archive)
                result = export_runs.export(*args, pack_registration={"blinding_group": "bytes"})
                row = next(r for r in self.rows(result) if r["run_id"] == "ref")
                self.assertIn(export_runs.REFERENCE_UNAVAILABLE, row["flag_codes"])
                self.assertTrue(all(row[c] == "" for c in export_runs.REFERENCE_REQUEST_COLUMNS))

    def test_collected_reference_custody_faults_stop_before_publication(self):
        cases = {
            "bundle": lambda a: (write_json(a / "withheld/member-assessments.json", {
                "members": {"ref": {"status": "succeeded"}}}), shutil.rmtree(a / "sources/claim-runs/ref")),
            "inventory": lambda a: (a / "sources/SHA256SUMS").unlink(),
            "config": lambda a: (a / "sources/claim-runs/ref/config.json").write_text("{bad"),
            "status": lambda a: (a / "sources/claim-runs/ref/status.json").write_text("{bad"),
            "status_list": lambda a: write_json(a / "sources/claim-runs/ref/status.json", []),
            "metadata_list": lambda a: write_json(a / "sources/claim-runs/ref/metadata.json", []),
            "summary": lambda a: (a / "withheld/reductions/ref.summary_metrics.rereduced.json").write_text("null"),
        }
        for name, mutate in cases.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                archive, reg, plan, _ = archive_fixture(root)
                mutate(archive)
                with self.assertRaises(export_runs.StorageStop) as stopped:
                    export_runs.export(archive, plan, reg, root / "packs", root / "out",
                                       pack_registration={"blinding_group": "bytes"})
                if name == "bundle":
                    self.assertIn(str(archive / "sources/claim-runs/ref"), str(stopped.exception))
                self.assertFalse((root / "out").exists())

    def test_listed_bundle_disappearing_does_not_mask_a_status_disagreement(self):
        write_json(self.archive / "withheld/member-assessments.json", {"members": {
            "ref": {"status": "failed", "present": True}}})
        shutil.rmtree(self.archive / "sources/claim-runs/ref")
        with self.assertRaisesRegex(export_runs.StorageStop, "bundle directory missing"):
            self.export(pack_registration={"blinding_group": "bytes"})

    def test_listed_original_status_can_positively_establish_a_failed_collection(self):
        status = self.archive / "sources/claim-runs/ref/status.json"
        write_json(status, {"status": {"state": "failed"}})
        with self.assertRaisesRegex(export_runs.StorageStop, "status.json.*digest mismatch"):
            self.export(pack_registration={"blinding_group": "bytes"})
        seal_reference_inputs(self.archive)
        row = next(r for r in self.rows(self.export(pack_registration={"blinding_group": "bytes"}))
                   if r["run_id"] == "ref")
        self.assertEqual(row["status"], "failed")
        self.assertNotIn(export_runs.REFERENCE_UNAVAILABLE, row["flag_codes"])

    def test_harvest_roster_failure_disagreeing_with_verified_success_stops(self):
        path = self.archive / "derived/roster.json"
        roster = json.loads(path.read_bytes())
        next(m for m in roster["members"] if m["run_id"] == "ref")["status"] = "failed"
        write_json(path, roster)
        seal_reference_inputs(self.archive)
        with self.assertRaisesRegex(export_runs.StorageStop, "harvested status 'failed'.*verified source status 'succeeded'"):
            self.export(pack_registration={"blinding_group": "bytes"})

    def test_reference_assessment_and_verified_source_status_must_agree_both_ways(self):
        for harvested, source in (("failed", "succeeded"), ("succeeded", "failed")):
            with self.subTest(harvested=harvested, source=source):
                write_json(self.archive / "sources/claim-runs/ref/status.json", {"status": {"state": source}})
                write_json(self.archive / "withheld/member-assessments.json", {"members": {"ref": {"status": harvested}}})
                seal_reference_inputs(self.archive)
                with self.assertRaisesRegex(export_runs.StorageStop, "reference status ref:.*disagrees"):
                    self.export(pack_registration={"blinding_group": "bytes"})

    def test_assessment_cannot_mask_a_roster_status_disagreement(self):
        path = self.archive / "derived/roster.json"
        roster = json.loads(path.read_bytes())
        next(m for m in roster["members"] if m["run_id"] == "ref")["status"] = "failed"
        write_json(path, roster)
        write_json(self.archive / "withheld/member-assessments.json", {"members": {
            "ref": {"status": "succeeded"}}})
        seal_reference_inputs(self.archive)
        with self.assertRaisesRegex(export_runs.StorageStop, "harvested status 'failed'.*verified source status 'succeeded'"):
            self.export(pack_registration={"blinding_group": "bytes"})

    def test_unlisted_shadow_or_multiple_listed_reference_bundles_stop(self):
        for listed in (False, True):
            with self.subTest(listed=listed), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                archive, reg, plan, _ = archive_fixture(root)
                target = archive / "sources/bound-runs/ref"
                shutil.copytree(archive / "sources/claim-runs/ref", target)
                if listed:
                    seal_reference_inputs(archive)
                with self.assertRaisesRegex(export_runs.StorageStop, "found 2|unlisted bundle directories"):
                    export_runs.export(archive, plan, reg, root / "keys", root / "out",
                                       pack_registration={"blinding_group": "bytes"})
                self.assertFalse((root / "out").exists())

    def test_every_present_reference_input_requires_an_inventory_entry(self):
        for name in ("config.json", "metadata.json", "status.json", "events.jsonl", "power_trace.csv",
                     "raw/powermetrics.plist", "instrument_calibration/events.jsonl"):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                archive, reg, plan, _ = archive_fixture(root)
                path = archive / "sources/claim-runs/ref" / name
                path.parent.mkdir(parents=True, exist_ok=True)
                if not path.exists():
                    path.write_text("unlisted raw bytes")
                inventory = archive / "sources/SHA256SUMS"
                inventory.write_text("".join(line + "\n" for line in inventory.read_text().splitlines()
                                             if not line.endswith("  claim-runs/ref/" + name)))
                with self.assertRaisesRegex(export_runs.StorageStop, "no SHA256SUMS proof"):
                    export_runs.export(archive, plan, reg, root / "keys", root / "out",
                                       pack_registration={"blinding_group": "bytes"})

    def test_finder_metadata_is_ignored_but_every_other_unlisted_file_stops(self):
        bundle = self.archive / "sources/claim-runs/ref"
        baseline = self.rows(self.export(pack_registration={"blinding_group": "bytes"}))
        for directory in (bundle, bundle / "raw"):
            directory.mkdir(exist_ok=True)
            (directory / ".DS_Store").write_bytes(b"Finder metadata")
        self.assertEqual(self.rows(self.export(pack_registration={"blinding_group": "bytes"})), baseline)
        (bundle / ".DS_Store").unlink()  # APFS may treat case variants as the same existing name.
        for name in (".DS_Store.zst", ".ds_store", ".DS_Store.backup", "notes.txt"):
            with self.subTest(name=name):
                path = bundle / name
                path.write_bytes(b"unlisted bytes")
                with self.assertRaises(export_runs.StorageStop):
                    self.export(pack_registration={"blinding_group": "bytes"})
                path.unlink()

    def test_partial_reference_requires_verified_harvest_missing_summary_evidence(self):
        bundle = self.archive / "sources/claim-runs/ref"
        (bundle / "status.json").unlink()
        (self.archive / "withheld/reductions/ref.summary_metrics.rereduced.json").unlink()
        self.record["excluding"].append({"scope": "member", "run_id": "ref", "code": "member.bytes_missing"})
        write_json(self.archive / "derived/b6-acceptance.json", self.record)
        flag_path = self.archive / "derived/flags.jsonl"
        flag = {"code": "member.bytes_missing", "scope": {"run_id": "ref"}, "interval": None,
                "flag_id": "partial-ref", "observed": {"files_missing": ["summary_metrics.json"]}}
        seal_reference_inputs(self.archive)
        with self.assertRaisesRegex(export_runs.StorageStop, "no verified source status"):
            self.export(pack_registration={"blinding_group": "bytes"})
        flag_path.write_text(json.dumps(flag) + "\n")
        with self.assertRaisesRegex(export_runs.StorageStop, "flags.jsonl.*digest mismatch"):
            self.export(pack_registration={"blinding_group": "bytes"})
        seal_reference_inputs(self.archive)
        # The verified missing-summary outcome also outranks a stale success
        # assessment: it proves the collection ended without a usable record.
        write_json(self.archive / "withheld/member-assessments.json", {"members": {"ref": {"status": "succeeded"}}})
        row = next(r for r in self.rows(self.export(pack_registration={"blinding_group": "bytes"}))
                   if r["run_id"] == "ref")
        self.assertEqual(row["status"], "member.bytes_missing")
        self.assertIn("member.bytes_missing", row["flag_codes"])
        self.assertEqual(row["excluded"], "True")
        self.assertTrue(all(not row[c] for c in export_runs.REFERENCE_REQUEST_COLUMNS))
        self.record["excluding"] = []
        write_json(self.archive / "derived/b6-acceptance.json", self.record)
        write_json(bundle / "status.json", {"status": {"state": "succeeded"}})
        seal_reference_inputs(self.archive)
        row = next(r for r in self.rows(self.export(pack_registration={"blinding_group": "bytes"}))
                   if r["run_id"] == "ref")
        self.assertEqual(row["status"], "member.bytes_missing")
        self.assertEqual(row["excluded"], "False")
        self.assertTrue(all(not row[c] for c in export_runs.REFERENCE_REQUEST_COLUMNS))
        # Acceptance alone cannot supply the harvest's missing-summary proof.
        receipt_path = self.archive / "harvest.json"
        receipt = json.loads(receipt_path.read_bytes())
        receipt["outputs"].pop("derived/flags.jsonl")
        write_json(receipt_path, receipt)
        with self.assertRaisesRegex(export_runs.StorageStop, "flags.jsonl.*no harvest.json digest"):
            self.export(pack_registration={"blinding_group": "bytes"})

    def test_lost_listed_summary_is_not_a_partial_collection(self):
        bundle = self.archive / "sources/claim-runs/ref"
        (bundle / "status.json").unlink()
        write_json(bundle / "summary_metrics.json", {"status": "succeeded"})
        (self.archive / "derived/flags.jsonl").write_text(json.dumps({
            "code": "member.bytes_missing", "scope": {"run_id": "ref"}, "interval": None,
            "flag_id": "partial-ref", "observed": {"files_missing": ["summary_metrics.json"]}}) + "\n")
        seal_reference_inputs(self.archive)
        (bundle / "summary_metrics.json").unlink()
        with self.assertRaisesRegex(export_runs.StorageStop, "summary_metrics.json.*FileNotFoundError"):
            self.export(pack_registration={"blinding_group": "bytes"})

    def test_uncollected_exclusion_cannot_contradict_harvest_success(self):
        for witness in ("roster", "assessment"):
            with self.subTest(witness=witness), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                archive, reg, plan, record = archive_fixture(root)
                shutil.rmtree(archive / "sources/claim-runs/ref")
                record["excluding"].append({"scope": "member", "run_id": "ref", "code": "member.bytes_missing"})
                write_json(archive / "derived/b6-acceptance.json", record)
                if witness == "roster":
                    path = archive / "derived/roster.json"
                    roster = json.loads(path.read_bytes())
                    next(m for m in roster["members"] if m["run_id"] == "ref")["status"] = {"state": "succeeded"}
                    write_json(path, roster)
                else:
                    write_json(archive / "withheld/member-assessments.json", {"members": {"ref": {"status": "succeeded"}}})
                seal_reference_inputs(archive)
                with self.assertRaisesRegex(export_runs.StorageStop, "members without listed bundles.*ref"):
                    export_runs.export(archive, plan, reg, root / "keys", root / "out",
                                       pack_registration={"blinding_group": "bytes"})

    def test_bytes_s1_p1_smoke_keeps_uncollected_reference_rows(self):
        from joulewise.b6 import acceptance, smoke
        tree = json.loads((Path(__file__).resolve().parents[2] /
                           "configs/campaigns/bytes-s1-p1/plan_tree.json").read_bytes())
        stages, roles = acceptance._stage_roles(tree)
        reference_stages = {stages[run] for run in roles if roles[run] in export_runs.REFERENCE_ROLES}
        keep = {stage["stage_id"]: int(stage["stage_id"] in reference_stages)
                for stage in tree["stage_graph"] if stage["kind"] == "campaign_collection"}
        reduced = smoke.reduce_tree(tree, keep)
        template = self.root / "reference-template"
        shutil.copytree(self.archive / "sources/claim-runs/ref", template)
        summary = (self.archive / "withheld/reductions/ref.summary_metrics.rereduced.json").read_bytes()
        shutil.rmtree(self.archive / "sources/claim-runs")
        shutil.rmtree(self.archive / "withheld/reductions")
        members, kept = [], set()
        for stage in reduced["stage_graph"]:
            if stage["kind"] != "campaign_collection":
                continue
            runs = [run for run in stages if stages[run] == stage["stage_id"]]
            kept.add(runs[0])
            for run in runs:
                members.append({"run_id": run, "stage_id": stage["stage_id"], "units": []})
            run = runs[0]
            shutil.copytree(template, self.archive / "sources/claim-runs" / run)
            path = self.archive / "withheld/reductions" / (run + ".summary_metrics.rereduced.json")
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(summary)
        self.record.update(pack_id="bytes-s1-p1", excluding=[])
        self.plan["pack_id"] = "bytes-s1-p1"
        write_json(self.archive / "derived/b6-acceptance.json", self.record)
        write_json(self.archive / "derived/roster.json", {"pack_id": "bytes-s1-p1", "members": list(reversed(members))})
        tree_path = self.archive / "sources/pack/plan_tree.json"
        write_json(tree_path, reduced)
        write_json(self.archive / "sources/pack/smoke-registered-tree.json", tree)
        seal_reference_inputs(self.archive)
        rows = self.rows(self.export(pack_registration={"pack_id": "bytes-s1-p1", "blinding_group": "bytes"}))
        self.assertEqual(len(rows), 25)
        self.assertEqual([r["run_id"] for r in rows], [m["run_id"] for m in members])
        self.assertEqual(sum(bool(r["reference_request_gross_j"]) for r in rows), 4)
        for row in rows:
            if row["run_id"] not in kept:
                self.assertEqual(row["status"], "uncollected")
                self.assertEqual(row["excluded"], "False")
                self.assertTrue(all(not row[c] for c in export_runs.REFERENCE_REQUEST_COLUMNS))
        dropped = next(m["run_id"] for m in members if m["run_id"] not in kept)
        for witness in ("roster", "assessment"):
            with self.subTest(success_witness=witness):
                roster = {"pack_id": "bytes-s1-p1", "members": [dict(m) for m in members]}
                if witness == "roster":
                    next(m for m in roster["members"] if m["run_id"] == dropped)["status"] = "succeeded"
                else:
                    write_json(self.archive / "withheld/member-assessments.json", {
                        "members": {dropped: {"status": {"state": "succeeded"}}}})
                write_json(self.archive / "derived/roster.json", roster)
                seal_reference_inputs(self.archive)
                with self.assertRaisesRegex(export_runs.StorageStop, "members without listed bundles"):
                    self.export(pack_registration={"blinding_group": "bytes"})
        (self.archive / "withheld/member-assessments.json").unlink()
        write_json(self.archive / "derived/roster.json", {"pack_id": "bytes-s1-p1", "members": members})
        seal_reference_inputs(self.archive)
        # An edited, unverified smoke keep cannot authorize an absence.
        reduced["smoke_reduction"]["keep"][members[0]["stage_id"]] = 0
        write_json(tree_path, reduced)
        with self.assertRaisesRegex(export_runs.StorageStop, "plan_tree.json.*digest mismatch"):
            self.export(pack_registration={"blinding_group": "bytes"})
        # An inline plan fallback has no archived checksum witness and cannot
        # grant the smoke exception even when its keep data have the right shape.
        tree_path.unlink()
        inventory = self.archive / "sources/SHA256SUMS"
        inventory.write_text("".join(line + "\n" for line in inventory.read_text().splitlines()
                                    if not line.endswith("  pack/plan_tree.json")))
        reduced["smoke_reduction"]["keep"][members[0]["stage_id"]] = 1
        self.plan["plan_tree"] = reduced
        with self.assertRaisesRegex(export_runs.StorageStop, "smoke: no archived checksum witness"):
            self.export(pack_registration={"blinding_group": "bytes"})

    def test_acceptance_excluded_uncollected_reference_is_printed_if_projection_omits_it(self):
        import dataclasses
        shutil.rmtree(self.archive / "sources/claim-runs/ref")
        self.record["excluding"].append({"scope": "member", "run_id": "ref", "code": "member.bytes_missing"})
        write_json(self.archive / "derived/b6-acceptance.json", self.record)
        seal_reference_inputs(self.archive)
        evidence = export_runs.evidence_from_archive(self.archive, self.plan, self.reg)
        evidence = dataclasses.replace(evidence, stages=tuple(dataclasses.replace(stage,
            members=tuple(m for m in stage.members if m.run_id != "ref")) for stage in evidence.stages))
        row = next(r for r in self.rows(self.export(evidence=evidence, pack_registration={"blinding_group": "bytes"}))
                   if r["run_id"] == "ref")
        self.assertEqual(row["status"], "uncollected")
        self.assertEqual(row["excluded"], "True")
        self.assertIn("member.bytes_missing", row["exclusion_codes"])
        self.assertTrue(all(not row[c] for c in export_runs.REFERENCE_REQUEST_COLUMNS))
        write_json(self.archive / "withheld/member-assessments.json", {"members": {"ref": {"status": "failed"}}})
        row = next(r for r in self.rows(self.export(evidence=evidence, pack_registration={"blinding_group": "bytes"}))
                   if r["run_id"] == "ref")
        self.assertEqual(row["status"], "uncollected")

    def test_registered_smoke_prints_references_from_removed_stages(self):
        from joulewise.b6 import acceptance, smoke
        repo = Path(__file__).resolve().parents[2]
        tree = json.loads((repo / "configs/campaigns/bytes-s1-p1/plan_tree.json").read_bytes())
        stages, roles = acceptance._stage_roles(tree)
        keep = json.loads((repo / "configs/b6/smoke_keep.json").read_bytes())["bytes-s1-p1"]
        reduced = smoke.reduce_tree(tree, keep)
        template = self.root / "reference-template"
        shutil.copytree(self.archive / "sources/claim-runs/ref", template)
        summary = (self.archive / "withheld/reductions/ref.summary_metrics.rereduced.json").read_bytes()
        shutil.rmtree(self.archive / "sources/claim-runs")
        shutil.rmtree(self.archive / "withheld/reductions")
        members, reference_order = [], []
        for stage in tree["stage_graph"]:
            if stage["kind"] != "campaign_collection":
                continue
            runs = [run for run in stages if stages[run] == stage["stage_id"]]
            for i, run in enumerate(runs):
                # Real harvests use input ids here and do not record roles.
                members.append({"run_id": run, "stage_id": "roster-input", "units": []})
                if roles[run] in export_runs.REFERENCE_ROLES:
                    reference_order.append(run)
                if i < keep.get(stage["stage_id"], 0):
                    shutil.copytree(template, self.archive / "sources/claim-runs" / run)
                    path = self.archive / "withheld/reductions" / (run + ".summary_metrics.rereduced.json")
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(summary)
        self.record.update(pack_id="bytes-s1-p1", excluding=[])
        self.plan["pack_id"] = "bytes-s1-p1"
        write_json(self.archive / "derived/b6-acceptance.json", self.record)
        roster_path = self.archive / "derived/roster.json"
        write_json(roster_path, {"members": list(reversed(members))})
        write_json(self.archive / "sources/pack/plan_tree.json", reduced)
        original = self.archive / "sources/pack/smoke-registered-tree.json"
        write_json(original, tree)
        seal_reference_inputs(self.archive)
        rows = self.rows(self.export(pack_registration={"blinding_group": "bytes"}))
        refs = [row for row in rows if row["role"] in export_runs.REFERENCE_ROLES]
        self.assertEqual([row["run_id"] for row in refs], reference_order)
        self.assertEqual(len(refs), 25)
        self.assertEqual(sum(row["status"] == "uncollected" for row in refs), 23)
        self.assertEqual([int(row["order_index"]) for row in rows],
                         sorted({int(row["order_index"]) for row in rows}))
        for row in refs:
            if row["status"] == "uncollected":
                self.assertTrue(all(row[c] == "" for c in export_runs.REFERENCE_REQUEST_COLUMNS))
        removed = next(run for run in reference_order if stages[run] in reduced["smoke_reduction"]["removed"])
        for witness in ("roster", "assessment"):
            with self.subTest(non_success_witness=witness):
                roster = {"members": [dict(m) for m in members]}
                if witness == "roster":
                    next(m for m in roster["members"] if m["run_id"] == removed)["status"] = "failed"
                else:
                    write_json(self.archive / "withheld/member-assessments.json",
                               {"members": {removed: {"status": "failed"}}})
                write_json(roster_path, roster)
                seal_reference_inputs(self.archive)
                row = next(r for r in self.rows(self.export(pack_registration={"blinding_group": "bytes"}))
                           if r["run_id"] == removed)
                self.assertEqual(row["status"], "uncollected")
        (self.archive / "withheld/member-assessments.json").unlink()
        for witness in ("roster", "assessment"):
            with self.subTest(witness=witness):
                roster = {"members": [dict(m) for m in members]}
                if witness == "roster":
                    next(m for m in roster["members"] if m["run_id"] == removed)["status"] = "succeeded"
                else:
                    write_json(self.archive / "withheld/member-assessments.json",
                               {"members": {removed: {"status": "succeeded"}}})
                write_json(roster_path, roster)
                seal_reference_inputs(self.archive)
                with self.assertRaisesRegex(export_runs.StorageStop, "members without listed bundles.*" + removed):
                    self.export(pack_registration={"blinding_group": "bytes"})
        (self.archive / "withheld/member-assessments.json").unlink()
        # Even a lost roster entry cannot silently erase a planned reference.
        write_json(roster_path, {"members": [m for m in members if m["run_id"] != removed]})
        seal_reference_inputs(self.archive)
        row = next(r for r in self.rows(self.export(pack_registration={"blinding_group": "bytes"}))
                   if r["run_id"] == removed)
        self.assertEqual(row["status"], "uncollected")
        # An unrelated default-branch results clone is never a witness.
        other = self.archive / "sources/night-custody/results-clone/configs/campaigns/bytes-s1-p1/plan_tree.json"
        conflicting = json.loads(json.dumps(tree))
        next(stage for stage in conflicting["stage_graph"]
             if stage["stage_id"] == stages[removed])["expected_count"] -= 1
        self.assertEqual(smoke.reduce_tree(conflicting, keep), reduced)
        write_json(other, conflicting)
        seal_reference_inputs(self.archive)
        self.assertEqual(self.rows(self.export(pack_registration={"blinding_group": "bytes"})), rows)
        # A present custody witness must reproduce the archived reduction.
        inconsistent = {**tree, "witness_probe": "different top-level bytes"}
        write_json(original, inconsistent)
        seal_reference_inputs(self.archive)
        with self.assertRaisesRegex(export_runs.StorageStop, "reference membership smoke.*inconsistent"):
            self.export(pack_registration={"blinding_group": "bytes"})
        original.write_text("{}")
        with self.assertRaisesRegex(export_runs.StorageStop, "smoke-registered-tree.json.*digest mismatch"):
            self.export(pack_registration={"blinding_group": "bytes"})
        seal_reference_inputs(self.archive)
        with self.assertRaisesRegex(export_runs.StorageStop, "reference membership smoke: KeyError.*stage_graph"):
            self.export(pack_registration={"blinding_group": "bytes"})
        original.unlink()
        seal_reference_inputs(self.archive)
        result = self.export(pack_registration={"blinding_group": "bytes"})
        legacy_refs = [r for r in self.rows(result) if r["role"] in export_runs.REFERENCE_ROLES]
        surviving_refs = [r for r in refs if stages[r["run_id"]] not in reduced["smoke_reduction"]["removed"]]
        self.assertEqual({r["run_id"] for r in legacy_refs}, {r["run_id"] for r in surviving_refs})
        self.assertEqual(sum(r["status"] == "uncollected" for r in legacy_refs), 4)
        for row in legacy_refs:
            if row["status"] == "uncollected":
                self.assertTrue(all(row[c] == "" for c in export_runs.REFERENCE_REQUEST_COLUMNS))
        session = json.loads(result.sidecar_path.read_bytes())
        self.assertEqual(session["removed_stage_references"], "unwitnessed")
        self.assertEqual(session["removed_stage_ids"], reduced["smoke_reduction"]["removed"])
        self.assertTrue(session["non_claim"])
        # Both physical presence and a digest entry forbid the legacy fallback:
        # an unlisted witness or a lost listed witness is a storage condition.
        write_json(original, tree)
        with self.assertRaisesRegex(export_runs.StorageStop, "smoke-registered-tree.json.*no SHA256SUMS proof"):
            self.export(pack_registration={"blinding_group": "bytes"})
        seal_reference_inputs(self.archive)
        original.unlink()
        with self.assertRaisesRegex(export_runs.StorageStop, "smoke-registered-tree.json.*FileNotFoundError"):
            self.export(pack_registration={"blinding_group": "bytes"})
        with self.assertRaisesRegex(export_runs.StorageStop, "smoke-registered-tree.json.*FileNotFoundError"):
            export_runs.export(Path(os.path.relpath(self.archive)), self.plan, self.reg,
                               self.root / "packs", self.root / "out",
                               pack_registration={"blinding_group": "bytes"})
        seal_reference_inputs(self.archive)
        original.symlink_to("missing-witness.json")
        with self.assertRaisesRegex(export_runs.StorageStop, "smoke-registered-tree.json.*FileNotFoundError"):
            self.export(pack_registration={"blinding_group": "bytes"})
        original.unlink()
        compressed = Path(str(original) + ".zst")
        compressed.write_bytes(b"invalid compressed witness")
        with self.assertRaisesRegex(export_runs.StorageStop, "smoke-registered-tree.json"):
            self.export(pack_registration={"blinding_group": "bytes"})
        compressed.unlink()
        # With every reference stage removed, an inline reduced tree cannot
        # bypass membership merely because no surviving stage assigns roles.
        reference_stages = {stages[run] for run in reference_order}
        self.plan["plan_tree"] = smoke.reduce_tree(tree, {
            stage: count for stage, count in keep.items() if stage not in reference_stages})
        (self.archive / "sources/pack/plan_tree.json").unlink()
        seal_reference_inputs(self.archive)
        with self.assertRaisesRegex(export_runs.StorageStop, "smoke: no archived checksum witness"):
            self.export(pack_registration={"blinding_group": "bytes"})

    def test_plain_planned_reference_absent_from_roster_requires_acceptance_exclusion(self):
        tree_path = self.archive / "sources/pack/plan_tree.json"
        tree = json.loads(tree_path.read_bytes())
        tree["external_inputs"] = {"manifests": [{"input_id": "start_reference",
            "members": [{"run_id": "ref"}]}]}
        tree["stage_graph"][0]["input_ref"] = {"input_id": "start_reference"}
        write_json(tree_path, tree)
        roster_path = self.archive / "derived/roster.json"
        roster = json.loads(roster_path.read_bytes())
        roster["members"] = [m for m in roster["members"] if m["run_id"] != "ref"]
        write_json(roster_path, roster)
        shutil.rmtree(self.archive / "sources/claim-runs/ref")
        seal_reference_inputs(self.archive)
        with self.assertRaisesRegex(export_runs.StorageStop, "members without listed bundles.*ref"):
            self.export(pack_registration={"blinding_group": "bytes"})
        self.record["excluding"].append({"scope": "member", "run_id": "ref", "code": "member.bytes_missing"})
        write_json(self.archive / "derived/b6-acceptance.json", self.record)
        row = next(r for r in self.rows(self.export(pack_registration={"blinding_group": "bytes"}))
                   if r["run_id"] == "ref")
        self.assertEqual(row["status"], "uncollected")
        self.assertEqual(row["excluded"], "True")
        self.assertTrue(all(row[c] == "" for c in export_runs.REFERENCE_REQUEST_COLUMNS))

    def test_bundle_without_inventory_entries_stops(self):
        bundle = self.archive / "sources/claim-runs/ref"
        inputs = export_runs._ReferenceInputs(self.archive)
        inputs.digests = {p: digest for p, digest in inputs.digests.items() if not p.is_relative_to(bundle)}
        with self.assertRaisesRegex(export_runs.StorageStop, "no inventory entries"):
            inputs.check_bundle(bundle)

    def test_nested_symlink_inputs_need_digests_and_cycles_stop(self):
        bundle = self.archive / "sources/claim-runs/ref"
        external = self.root / "instrument"
        external.mkdir()
        (external / "events.jsonl").write_text("unlisted instrument bytes")
        (bundle / "instrument_calibration").symlink_to(external, target_is_directory=True)
        with self.assertRaisesRegex(export_runs.StorageStop, "instrument_calibration/events.jsonl.*no SHA256SUMS proof"):
            self.export(pack_registration={"blinding_group": "bytes"})
        (bundle / "instrument_calibration").unlink()
        (bundle / "raw").symlink_to(bundle, target_is_directory=True)
        with self.assertRaisesRegex(export_runs.StorageStop, "directory cycle"):
            self.export(pack_registration={"blinding_group": "bytes"})

    def test_negative_assessment_needs_verified_source_status(self):
        write_json(self.archive / "sources/claim-runs/ref/status.json", {})
        write_json(self.archive / "withheld/member-assessments.json", {"members": {"ref": {"status": "failed"}}})
        seal_reference_inputs(self.archive)
        with self.assertRaisesRegex(export_runs.StorageStop, "no verified source status"):
            self.export(pack_registration={"blinding_group": "bytes"})

    def test_every_desk_export_requires_the_source_inventory(self):
        (self.archive / "sources/SHA256SUMS").unlink()
        with self.assertRaisesRegex(export_runs.StorageStop, "SHA256SUMS.*FileNotFoundError"):
            self.export(non_claim=True)

    def test_original_runs_fallback_cannot_replace_a_missing_archived_reference(self):
        original = self.root / "original-runs"
        shutil.copytree(self.archive / "sources/claim-runs/ref", original / "ref")
        write_json(self.archive / "withheld/member-assessments.json", {
            "members": {"ref": {"status": "succeeded"}}})
        self.plan["claim_runs_root"] = str(original)
        shutil.rmtree(self.archive / "sources/claim-runs/ref")
        with self.assertRaisesRegex(export_runs.StorageStop, "bundle directory missing from archive"):
            self.export(pack_registration={"blinding_group": "bytes"})

    def test_external_original_is_never_a_reference_candidate(self):
        original = self.root / "original-runs"
        shutil.copytree(self.archive / "sources/claim-runs/ref", original / "ref")
        (original / "ref/status.json").write_text("corrupted external original")
        self.plan["claim_runs_root"] = str(original)
        rows = self.rows(self.export(pack_registration={"blinding_group": "bytes"}))
        ref = next(row for row in rows if row["run_id"] == "ref")
        self.assertEqual(ref["status"], "succeeded")
        self.assertTrue(ref["reference_request_gross_j"])

    def test_copied_custody_alias_cannot_escape_archived_sources(self):
        for depth in (2, 3):
            with self.subTest(depth=depth), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                archive, reg, plan, _ = archive_fixture(root)
                relative = Path(*([".."] * depth), "escaped-runs")
                alias = archive / "sources/night-custody" / relative
                outside = Path(os.path.abspath(alias))
                shutil.copytree(archive / "sources/claim-runs/ref", outside / "ref")
                (outside / "ref/status.json").write_text("unlisted outside bytes")
                plan.update(custody_root=str(root / "custody"),
                            claim_runs_root=str(root / "custody" / relative))
                result = export_runs.export(archive, plan, reg, root / "keys", root / "out",
                                            pack_registration={"blinding_group": "bytes"})
                ref = next(row for row in self.rows(result) if row["run_id"] == "ref")
                self.assertEqual(ref["status"], "succeeded")
                self.assertTrue(ref["reference_request_gross_j"])

    def test_plan_binding_inside_archived_sources_remains_a_candidate(self):
        inside = self.archive / "sources/other-runs"
        inside.mkdir()
        shutil.move(self.archive / "sources/claim-runs/ref", inside / "ref")
        self.plan["claim_runs_root"] = str(inside)
        seal_reference_inputs(self.archive)
        ref = next(row for row in self.rows(self.export(pack_registration={"blinding_group": "bytes"}))
                   if row["run_id"] == "ref")
        self.assertEqual(ref["status"], "succeeded")
        self.assertTrue(ref["reference_request_gross_j"])

    def test_missing_listed_plan_tree_cannot_reclassify_a_reference(self):
        tree_path = self.archive / "sources/pack/plan_tree.json"
        tree = json.loads(tree_path.read_bytes())
        tree["external_inputs"] = {"manifests": [{"input_id": "start_reference",
                                                  "members": [{"run_id": "ref"}]}]}
        tree["stage_graph"][0]["input_ref"] = {"input_id": "start_reference"}
        write_json(tree_path, tree)
        roster_path = self.archive / "derived/roster.json"
        roster = json.loads(roster_path.read_bytes())
        next(member for member in roster["members"] if member["run_id"] == "ref").pop("role")
        write_json(roster_path, roster)
        seal_reference_inputs(self.archive)
        tree_path.unlink()
        with self.assertRaisesRegex(export_runs.StorageStop, "plan_tree.json.*FileNotFoundError"):
            self.export(pack_registration={"blinding_group": "bytes"})
        self.assertFalse((self.root / "out").exists())

    def test_recorded_derived_outputs_are_verified_before_rows(self):
        for name in ("roster.json", "flags.jsonl", "code-identity.json"):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                archive, reg, plan, _ = archive_fixture(root)
                with (archive / "derived" / name).open("a") as stream:
                    stream.write(" ")
                with self.assertRaisesRegex(export_runs.StorageStop, name + ".*harvest.json digest mismatch"):
                    export_runs.export(archive, plan, reg, root / "keys", root / "out")
                self.assertFalse((root / "out").exists())

    def test_roster_and_flags_require_recorded_harvest_digests(self):
        for relative in ("derived/roster.json", "derived/flags.jsonl"):
            with self.subTest(relative=relative), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                archive, reg, plan, _ = archive_fixture(root)
                receipt = archive / "harvest.json"
                doc = json.loads(receipt.read_bytes())
                doc["outputs"].pop(relative)
                write_json(receipt, doc)
                with self.assertRaisesRegex(export_runs.StorageStop, relative + ".*no harvest.json digest"):
                    export_runs.export(archive, plan, reg, root / "keys", root / "out")
                self.assertFalse((root / "out").exists())

    def test_reference_membership_is_cross_checked_both_ways(self):
        for missing in ("roster", "inventory", "acceptance", "duplicate", "roster_and_inventory"):
            with self.subTest(missing=missing), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                archive, reg, plan, _ = archive_fixture(root)
                tree_path = archive / "sources/pack/plan_tree.json"
                tree = json.loads(tree_path.read_bytes())
                tree["external_inputs"] = {"manifests": [{"input_id": "start_reference",
                    "members": [{"run_id": "ref"}]}]}
                tree["stage_graph"][0]["input_ref"] = {"input_id": "start_reference"}
                write_json(tree_path, tree)
                if missing in ("roster", "duplicate", "roster_and_inventory"):
                    path = archive / "derived/roster.json"
                    roster = json.loads(path.read_bytes())
                    if missing in ("roster", "roster_and_inventory"):
                        roster["members"] = [m for m in roster["members"] if m["run_id"] != "ref"]
                    else:
                        roster["members"].append(next(m for m in roster["members"] if m["run_id"] == "ref"))
                    write_json(path, roster)
                seal_reference_inputs(archive)
                if missing in ("inventory", "roster_and_inventory"):
                    path = archive / "sources/SHA256SUMS"
                    path.write_text("".join(line + "\n" for line in path.read_text().splitlines()
                                             if "  claim-runs/ref/" not in line))
                evidence = export_runs.evidence_from_archive(archive, plan, reg)
                if missing == "acceptance":
                    from dataclasses import replace
                    evidence = replace(evidence, stages=tuple(replace(stage, members=tuple(
                        m for m in stage.members if m.run_id != "ref")) for stage in evidence.stages))
                with self.assertRaisesRegex(export_runs.StorageStop, "reference membership"):
                    export_runs.export(archive, plan, reg, root / "keys", root / "out",
                                       evidence=evidence, pack_registration={"blinding_group": "bytes"})
                self.assertFalse((root / "out").exists())

    def test_post_harvest_exclusion_remains_a_row_with_its_code(self):
        self.record["excluding"].append({"scope": "member", "run_id": "ref", "code": "member.bytes_missing"})
        result = self.export(acceptance_record=self.record, pack_registration={"blinding_group": "bytes"})
        ref = next(row for row in self.rows(result) if row["run_id"] == "ref")
        self.assertEqual(ref["excluded"], "True")
        self.assertIn("member.bytes_missing", ref["exclusion_codes"].split(";"))

    def test_optional_assessment_digest_is_checked_when_recorded(self):
        path = self.archive / "withheld/member-assessments.json"
        write_json(path, {"members": {}})
        receipt = self.archive / "harvest.json"
        doc = json.loads(receipt.read_bytes())
        doc["outputs"]["withheld/member-assessments.json"] = hashlib.sha256(path.read_bytes()).hexdigest()
        write_json(receipt, doc)
        path.write_text('{"members": {"ref": {"status": "failed"}}}')
        with self.assertRaisesRegex(export_runs.StorageStop, "member-assessments.json.*harvest.json digest mismatch"):
            self.export(pack_registration={"blinding_group": "bytes"})

    def test_parseable_but_invalid_request_records_stop_even_with_matching_digests(self):
        bundle = self.archive / "sources/claim-runs/ref"
        summary_path = self.archive / "withheld/reductions/ref.summary_metrics.rereduced.json"
        original = summary_path.read_bytes()
        for value in (None, [], "summary", {"idle_baseline": "missing"}, {"summary_provenance": "bad"}):
            with self.subTest(value=value):
                write_json(summary_path, value)
                seal_reference_inputs(self.archive)
                with self.assertRaisesRegex(export_runs.StorageStop, "ValueError:.*object"):
                    self.export(pack_registration={"blinding_group": "bytes"})
        summary_path.write_bytes(original)
        events = bundle / "events.jsonl"
        events.write_text(events.read_text() + json.dumps({"phase": "tokenize", "event_type": "phase_start",
                                                          "timestamp_s": 0}) + "\n")
        seal_reference_inputs(self.archive)
        with self.assertRaisesRegex(export_runs.StorageStop, "request markers must be unique"):
            self.export(pack_registration={"blinding_group": "bytes"})

    def test_reducer_exceptions_and_unresolved_contexts_are_storage_stops(self):
        import joulewise.reduce as reducer
        from types import SimpleNamespace
        for error in (RuntimeError("raw/powermetrics.plist exploded"),
                      AttributeError("instrument_calibration/ invalid"),
                      reducer._ReduceError("power_trace.csv mismatch")):
            with self.subTest(error=error), patch.object(reducer, "_derive_anchor_context", side_effect=error):
                with self.assertRaisesRegex(export_runs.StorageStop, type(error).__name__ + ": " + str(error)):
                    self.export(pack_registration={"blinding_group": "bytes"})
        for context in (SimpleNamespace(unresolved=True, detail="new_failure_class"),
                        SimpleNamespace(unresolved=False, telemetry_is_powermetrics=True, curve=None,
                                        detail="raw_capture_unavailable")):
            with self.subTest(context=context), patch.object(reducer, "_derive_anchor_context", return_value=context):
                with self.assertRaisesRegex(export_runs.StorageStop, "anchor context"):
                    self.export(pack_registration={"blinding_group": "bytes"})

    def test_curve_must_cover_both_request_edges(self):
        trace = self.archive / "sources/claim-runs/ref/power_trace.csv"
        for points in (range(9), range(1, 21)):
            with self.subTest(points=points):
                trace.write_text("timestamp_s,power_w,rail,source\n"
                                 + "".join(f"{i},10,mock,mock\n" for i in points))
                seal_reference_inputs(self.archive)
                with self.assertRaisesRegex(export_runs.StorageStop, "curve support.*does not cover request"):
                    self.export(pack_registration={"blinding_group": "bytes"})

    def test_registered_summary_absence_needs_a_listed_digest(self):
        summary = self.archive / "withheld/reductions/ref.summary_metrics.rereduced.json"
        write_json(summary, {"phase_energy_j": {}})
        seal_reference_inputs(self.archive)
        inventory = self.archive / "sources/SHA256SUMS"
        inventory.write_text("".join(line for line in inventory.read_text().splitlines(keepends=True)
                                     if "ref.summary_metrics.rereduced.json" not in line))
        with self.assertRaisesRegex(export_runs.StorageStop, "input has no SHA256SUMS proof"):
            self.export(pack_registration={"blinding_group": "bytes"})
        write_json(self.archive / "sources/claim-runs/ref/summary_metrics.json", {"phase_energy_j": {}})
        seal_reference_inputs(self.archive)
        inventory.write_text("".join(line for line in inventory.read_text().splitlines(keepends=True)
                                     if "ref.summary_metrics.rereduced.json" not in line))
        row = next(r for r in self.rows(self.export(pack_registration={"blinding_group": "bytes"}))
                   if r["run_id"] == "ref")
        self.assertIn(export_runs.REFERENCE_UNAVAILABLE, row["flag_codes"])
        write_json(summary, {"phase_energy_j": {}, "idle_baseline": {"power_w_mean": 3}})
        with self.assertRaisesRegex(export_runs.StorageStop, "summary_metrics.*digest mismatch"):
            self.export(pack_registration={"blinding_group": "bytes"})

    def test_interval_curve_cannot_leave_an_uncovered_request_gap(self):
        trace = self.archive / "sources/claim-runs/ref/power_trace.csv"
        trace.write_text("timestamp_s,power_w,rail,source,interval_start_s,interval_end_s\n"
                         "4,10,mock,mock,0,4\n14,10,mock,mock,6,14\n")
        seal_reference_inputs(self.archive)
        with self.assertRaisesRegex(export_runs.StorageStop, "curve support has a gap"):
            self.export(pack_registration={"blinding_group": "bytes"})

    def test_interval_curve_allows_epoch_rounding_but_stops_a_real_gap(self):
        epoch = 1_790_000_000.0
        events = self.archive / "sources/claim-runs/ref/events.jsonl"
        rows = [json.loads(line) for line in events.read_text().splitlines()]
        for row in rows:
            row["timestamp_s"] += epoch
        events.write_text("".join(json.dumps(row) + "\n" for row in rows))
        trace = self.archive / "sources/claim-runs/ref/power_trace.csv"
        for gap, stops in ((math.ulp(epoch), False), (5e-6, False), (9e-6, False),
                           (11e-6, False), (14e-6, True), (.001, True)):
            with self.subTest(gap=gap):
                trace.write_text("timestamp_s,power_w,rail,source,interval_start_s,interval_end_s\n"
                                 f"{epoch + 4},10,mock,mock,{epoch},{epoch + 4}\n"
                                 f"{epoch + 20},10,mock,mock,{epoch + 4 + gap},{epoch + 20}\n")
                seal_reference_inputs(self.archive)
                if stops:
                    with self.assertRaisesRegex(export_runs.StorageStop, "curve support has a gap"):
                        self.export(pack_registration={"blinding_group": "bytes"})
                else:
                    result = self.export(pack_registration={"blinding_group": "bytes"})
                    ref = next(row for row in self.rows(result) if row["run_id"] == "ref")
                    self.assertEqual(float(ref["reference_request_duration_s"]), 14)

    def test_interval_gaps_bound_summed_request_energy_at_its_peak_power(self):
        trace = self.archive / "sources/claim-runs/ref/power_trace.csv"
        cases = (
            # Each row is (supports with powers, expected stop). The lead's
            # 0.13 mJ ceiling gives 13 us at 10 W and 4 1/3 us at 30 W.
            ([(0, 4, 10), (4.000011, 14, 10)], False),
            ([(0, 4, 30), (4.000005, 14, 30)], True),
            ([(0, 4, 10), (4.000008, 8, 10), (8.000008, 14, 10)], True),
            ([(0, 4, 10), (4.000005, 8, 10), (8, 14, 30)], True),
            ([(-2, -1, 1000), (0, 4, 10), (4.000011, 14, 10), (15, 16, 1000)], False),
            ([(0.000005, 14 - 0.000005, 10)], False),
            ([(0.000008, 14 - 0.000008, 10)], True),
        )
        for supports, stops in cases:
            with self.subTest(supports=supports):
                trace.write_text("timestamp_s,power_w,rail,source,interval_start_s,interval_end_s\n" +
                                 "".join(f"{right},{power},mock,mock,{left},{right}\n"
                                         for left, right, power in supports))
                seal_reference_inputs(self.archive)
                if stops:
                    with self.assertRaisesRegex(export_runs.StorageStop, "summed uncovered.*P_max.*0.13 mJ"):
                        self.export(pack_registration={"blinding_group": "bytes"})
                else:
                    self.export(pack_registration={"blinding_group": "bytes"})

    def test_standalone_export_prints_exception_type_and_cause_at_exit_five(self):
        args = ["--archive", str(self.archive), "--plan", str(self.root / "plan.json"),
                "--registration-dir", str(self.reg), "--pack-records-root", str(self.root / "packs"),
                "--export-dir", str(self.root / "out")]
        for error in (ValueError("pack registration unresolved: diagnostic"),
                      export_runs.StorageStop("raw/powermetrics.plist missing"),
                      AttributeError("summary.json: missing object field")):
            stderr = io.StringIO()
            with self.subTest(error=error), patch.object(b6_export_runs, "export", side_effect=error), \
                 contextlib.redirect_stderr(stderr):
                self.assertEqual(b6_export_runs.main(args), 5)
            # A storage stop names its own cause code ("refused: restore_refused: ..."),
            # the form every entry point has printed since FIX-573i; other faults name their class.
            expected = (f"refused: {error}" if isinstance(error, export_runs.StorageStop)
                        else f"{type(error).__name__}: {error}")
            self.assertIn(expected, stderr.getvalue())

    def test_harvest_prints_every_export_value_error_cause(self):
        from scripts import harvest_b6_session as program
        from types import SimpleNamespace
        from joulewise.reduce import _ReduceError
        args = ["--plan", str(self.root / "plan.json"), "--archive-root", str(self.archive),
                "--registration-dir", str(self.reg), "--pack-records-root", str(self.root / "packs"),
                "--export-dir", str(self.root / "out")]
        for error in (ValueError("blinding session binding unreadable: custody.json"),
                      ValueError("pack registration unresolved: diagnostic"),
                      export_runs.StorageStop("raw/powermetrics.plist missing"),
                      _ReduceError("power_trace.csv differs from raw evidence"),
                      AttributeError("summary.json: missing object field")):
            stderr = io.StringIO()
            with patch.object(program, "resolve_inputs"), patch.object(program, "harvest", return_value={}), \
                 patch.object(program, "accept_archive", return_value=(SimpleNamespace(record=self.record), None)), \
                 patch.object(program, "export", side_effect=error), contextlib.redirect_stderr(stderr):
                self.assertEqual(program.main(args), 5)
            # A storage stop names its own cause code ("refused: restore_refused: ..."),
            # the form every entry point has printed since FIX-573i; other faults name their class.
            expected = (f"refused: {error}" if isinstance(error, export_runs.StorageStop)
                        else f"{type(error).__name__}: {error}")
            self.assertIn(expected, stderr.getvalue())

    def test_reference_missing_markers_are_disclosed(self):
        bundle = self.archive / "sources/claim-runs/ref"
        events = bundle / "events.jsonl"
        events.write_text("\n".join(line for line in events.read_text().splitlines() if 'tokenize' not in line))
        seal_reference_inputs(self.archive)
        result = self.export(pack_registration={"blinding_group": "bytes"})
        row = next(r for r in self.rows(result) if r["run_id"] == "ref")
        self.assertIn(export_runs.REFERENCE_UNAVAILABLE, row["flag_codes"])
        self.assertEqual(row["reference_request_duration_s"], "")

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
                # Smallest printed energy half-width: 0.013 J, so 1% is
                # 1.3e-4 J. At 10 J this bar is 1e-5 J, above 1e6 x
                # double noise (2.2e-9 J); the near-zero floor is 1e-6 J.
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
            # At 10 J the bar is 1e-5 J: above 1e6 x float noise
            # (2.2e-9 J), below 1% of the printed 0.013 J half-width
            # (1.3e-4 J). The near-zero absolute floor is 1e-6 J.
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
                # At 10 J, 1e-6 relative gives 1e-5 J, between 1e6 x
                # float noise (2.2e-9 J) and 1% of the smallest printed
                # half-width (0.013 J -> 1.3e-4 J); floor 1e-6 J near zero.
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
                # Energy at 10.89 J: bar 1.089e-5 J, above float noise x
                # 1e6 (2.4e-9 J), below 1% of 0.013 J (1.3e-4 J);
                # floor 1e-6 J. Variance has no printed W^2 half-width:
                # COMMON gives 1e-6 relative / 1e-6 W^2 absolute, above
                # float noise x 1e6 at 2.4 W^2 (5.3e-10 W^2).
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
                    # Energy at 10 J: 1e-5 J bar lies between float noise x
                    # 1e6 (2.2e-9 J) and 1% of 0.013 J (1.3e-4 J), with
                    # floor 1e-6 J. Variance has no W^2 half-width: COMMON
                    # gives 1e-6 relative / 1e-6 W^2 absolute, above float
                    # noise x 1e6 at 2 W^2 (4.4e-10 W^2).
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
