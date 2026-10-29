"""Source-less verdict recovery, with in-memory bytes and real catalog authentication.

The screen and loss selection are real.  Bundle reduction, scientific
identity and freshness observations are synthetic seams, as in the existing
NEG-8 survivor tests.  No fixture or temporary file is written.
"""
from __future__ import annotations

import contextlib
import copy
import hashlib
import json
import subprocess
import sys
import types
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from joulewise import campaign_provenance as cp
from joulewise import whole_window as ww
from joulewise.b5 import harvest as h
from tests.test_neg8_survivors import BINDINGS, RULING_CORPUS, bound_artifact

REPO = Path(__file__).resolve().parents[1]
BASE = "224a264c5faaae90cdf56118df37e773a932700b"
STAMP = "1970-01-01T00:33:20Z"


def sealed_harvest():
    raw = subprocess.run(["git", "show", f"{BASE}:joulewise/b5/harvest.py"], cwd=REPO,
                         check=True, capture_output=True).stdout
    module = types.ModuleType("_b5_sources_sealed_harvest")
    module.__file__ = h.__file__
    sys.modules[module.__name__] = module
    exec(compile(raw, h.__file__, "exec"), module.__dict__)
    return module


class SourceRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.root = Path("/synthetic-b5-sources")
        self.runs = self.root / "runs"
        self.files = {}
        self.policy_sha = hashlib.sha256(
            (REPO / "configs/campaign_policies/quiet_mac_p2_production.json").read_bytes()).hexdigest()
        self.bound = bound_artifact(RULING_CORPUS)
        self.ids = {slot: [f"{slot}-{i}" for i in range(count)]
                    for slot, count in (("start", 3), ("midpoint", 1), ("end", 3))}
        self.points = {run_id: 100.0 for ids in self.ids.values() for run_id in ids}
        self.energy_reads = []
        self.triangle_invalid = set()
        self.extra_roster = []
        self.plan = {"t0_epoch_s": h.ERRATUM_2_ADMITTED_AT_EPOCH_S + 1}
        for ids in self.ids.values():
            for run_id in ids:
                self.put(self.runs / run_id / "config.json", {"run_id": run_id})
                self.put(self.runs / run_id / "summary_metrics.json", self.summary(run_id))
                self.put(self.runs / run_id / "metadata.json", {"run_id": run_id})
        for slot, ids in self.ids.items():
            self.manifest(slot, ids)
        self.row = {"campaign_policy": {"sha256": self.policy_sha}, "timestamp": STAMP,
                    "evaluation_scope": {"completed_at": STAMP}, "bundle_ids": list(self.points),
                    "source_campaign_manifests": [], "row_provenance": {"source_campaign_manifests": []},
                    "idle_admission_core": {"conditions": ["neg8_bracket_missing",
                                                           "whole_window_campaign_membership_unresolved"],
                                            "neg8_bracket": {"decision": "failed", "conditions": [
                                                "neg8_bracket_missing", "neg8_bracket_reference_invalid"],
                                                             "claim_families": {}}}}
        real_read, real_dir, real_file, real_exists = Path.read_bytes, Path.is_dir, Path.is_file, Path.exists
        real_glob = Path.glob
        real_iterdir = Path.iterdir

        def inside(path):
            return path == self.root or self.root in path.parents

        def read(path):
            if not inside(path):
                return real_read(path)
            if path not in self.files:
                raise FileNotFoundError(str(path))
            return self.files[path]

        def is_dir(path):
            return any(path in item.parents for item in self.files) if inside(path) else real_dir(path)

        def glob(path, pattern, **kwargs):
            if not inside(path):
                return real_glob(path, pattern, **kwargs)
            return iter(item for item in sorted(self.files) if item.parent == path and item.match(pattern))

        def iterdir(path):
            if not inside(path):
                return real_iterdir(path)
            return iter(sorted({path / item.relative_to(path).parts[0]
                                for item in self.files if path in item.parents}))

        def write(path, value):
            if path in self.files:
                raise FileExistsError(str(path))
            return hashlib.sha256(self.put(path, value)).hexdigest()

        def energy(path, **kwargs):
            self.energy_reads.append(path.name)
            value = self.points[path.name]
            return {"point_j": value, "lower_j": value - .01, "upper_j": value + .01}, value - 36, None

        self.stack = contextlib.ExitStack()
        self.addCleanup(self.stack.close)
        for name, function in (("read_bytes", read), ("is_dir", is_dir), ("glob", glob), ("iterdir", iterdir),
                               ("is_file", lambda path: path in self.files if inside(path) else real_file(path)),
                               ("exists", lambda path: path in self.files or is_dir(path)
                                if inside(path) else real_exists(path))):
            self.stack.enter_context(mock.patch.object(Path, name, function))
        self.write = write
        self.stack.enter_context(mock.patch.object(h, "write_json_once", write))
        self.stack.enter_context(mock.patch.object(ww, "_current_strict_summary",
                                                   lambda summary, path=None: bool(summary and
                                                                                  summary.get("status") == "succeeded")))
        self.stack.enter_context(mock.patch.object(ww, "_custody_strict_invalid",
                                                   lambda path, *args: path.name in self.triangle_invalid))
        self.stack.enter_context(mock.patch.object(ww, "_scientific_config_identity", return_value=("d" * 64, True)))
        self.stack.enter_context(mock.patch.object(ww, "_reference_energy_evidence", energy))
        self.stack.enter_context(mock.patch.object(ww, "build_neg8_freshness_observation", return_value={
            "evaluated_at_s": 2000, "binding_status": "resolved", "bindings": BINDINGS}))
        self.stack.enter_context(mock.patch.object(ww, "_is_hazard_runs_root", return_value=False))
        self.hazard_root = self.stack.enter_context(mock.patch(
            "joulewise.window_lineage.is_hazard_runs_root", return_value=True))

    def put(self, path, value):
        raw = (json.dumps(value, sort_keys=True) + "\n").encode()
        self.files[path] = raw
        return raw

    def summary(self, run_id, status="succeeded"):
        point = self.points[run_id]
        return {"status": status, "gross_energy_j": point, "idle_subtracted_energy_j": point - 36,
                "energy_anchor_shift_envelopes": {"/gross_energy_j": {
                    "point_j": point, "lower_j": point - .01, "upper_j": point + .01}}}

    def manifest(self, slot, ids, name=None, policy_sha=None, execution="invoked", sentinel_position=None):
        name = name or slot
        path = self.runs / "campaign_manifests" / f"{name}.json"
        value = {"schema_version": cp.CAMPAIGN_PROVENANCE_SCHEMA_V2, "session_id": name,
                 "campaign_policy": {"sha256": policy_sha or self.policy_sha}, "members": [
                     {"run_id": run_id, "bundle_ids": [run_id], "execution": execution,
                      "role": "science" if slot == "science" else f"neg8_daily_reference_{slot}",
                      "canonical_neg8_workload": True,
                      "scientific_config_sha256": "d" * 64} for run_id in ids]}
        for member in value["members"]:
            if execution == "existing":
                member.update({"config": "existing.json", "outcome": "usable"})
            if sentinel_position is not None:
                member["sentinel_position"] = sentinel_position
        raw = self.put(path, value)
        attestation = cp.campaign_provenance_attestation(
            manifest_path=path, raw_manifest_bytes=raw, manifest=value, timestamp=STAMP)
        log = self.runs / "campaign_log.jsonl"
        self.files[log] = self.files.get(log, b"") + (json.dumps(attestation) + "\n").encode()
        return path

    def basis(self, included=None, paths=None):
        included = list(self.points) if included is None else included
        paths = paths or {}
        self.row["bundle_ids"] = included
        self.row["evaluation_scope"].update({"runs_root": str(self.runs), "started_at": STAMP})
        occurrences = []
        for run_id in included:
            relative = paths.get(run_id, run_id)
            occurrence = {"bundle_id": run_id, "bundle_path": relative}
            for name, field in (("config.json", "config_sha256"), ("metadata.json", "metadata_sha256"),
                                ("summary_metrics.json", "summary_sha256")):
                occurrence[field] = hashlib.sha256(self.files[self.runs / relative / name]).hexdigest()
            occurrences.append(occurrence)
        self.row["evaluation_basis"] = ww.build_evaluation_basis(
            policy_sha256=self.policy_sha, member_occurrences=occurrences, calibration_bracket=None)

    def harvest(self, module=h, losses=(), invalid=(), clean=True, ensure_trigger=True, ensure_basis=True):
        # Most recovery cases exercise an absent science member, which triggers
        # item 0(d) without adding a reference loss or changing the screen shape.
        if ensure_trigger and not any(
                not (self.runs / bundle_id).is_dir()
                for manifest in h._claim_campaign_manifests_as_written(self.runs)
                for member in manifest["members"] if member["execution"] == "invoked"
                for bundle_id in member["bundle_ids"]):
            self.manifest("science", ["science-absent"], name="absent-science")
        if ensure_basis and "evaluation_basis" not in self.row:
            included = [run_id for run_id in self.points
                        if all(self.runs / run_id / name in self.files
                               for name in ("config.json", "metadata.json", "summary_metrics.json"))]
            self.basis(included)
        run = object.__new__(module._Harvest)
        run.inputs = SimpleNamespace(claim_runs_root=self.runs, bound_runs_root=None, plan=self.plan)
        run.roster = {"members": [{"run_id": run_id, "neg8_slot": slot}
                                  for slot, ids in self.ids.items() for run_id in ids]
                                  + [{"run_id": "end-spare", "spare_slot": "end"}] + self.extra_roster}
        run.members = {run_id: {"strict_valid": run_id not in invalid, "present": True, "status": "succeeded"}
                       for run_id in self.points}
        run.flags = SimpleNamespace(records=[{"code": code, "scope": {"level": "member", "run_id": run_id}}
                                             for run_id, code in losses])
        run.emit = lambda code, **kwargs: run.flags.records.append({"code": code, **kwargs})
        run.neg8, run.outputs = {"derived_from": "registered_corpus"}, {}
        run.neg8_clean_bound = self.bound if clean else None
        run.neg8_clean_bound_required = True
        run.derived, run.withheld = self.root / "derived", self.root / "withheld"
        run.archive = self.root
        return run

    def screen(self, run, row=None):
        source = run.neg8_screen(row or self.row)
        record = json.loads(self.files[run.derived / "neg8-screen.json"])
        return source, record

    def add_bundleless_spare(self):
        self.manifest("end", ["end-spare"], name="spare")

    def test_sealed_writer_loses_all_sources_for_an_absent_invoked_spare(self):
        from scripts import run_campaign as writer

        with mock.patch.object(writer._window_lineage, "is_hazard_runs_root", return_value=True):
            baseline = writer._whole_window_campaign_membership(
                self.runs, self.policy_sha, self.runs / "campaign_log.jsonl")
            self.assertEqual(len(baseline.source_manifests), 3)
            self.assertTrue(all(source.role for source in baseline.sources))
            self.add_bundleless_spare()
            self.assertEqual(len(cp.load_authenticated_campaign_catalog(self.runs)), 4)
            broken = writer._whole_window_campaign_membership(
                self.runs, self.policy_sha, self.runs / "campaign_log.jsonl")
        self.assertEqual(broken.source_manifests, ())
        self.assertEqual(len(broken.sources), 7)
        self.assertTrue(all(source.role is None for source in broken.sources))
        self.assertIn("whole_window_campaign_membership_unresolved", broken.conditions)
        self.assertEqual(ww.source_manifest_descriptors(self.runs, broken.source_manifests), [])
        evaluations = [writer.MemberEvaluation(
            bundle_id=source.path.name, bundle_path=source.path, config_name="synthetic.json",
            status="succeeded", strict_valid=True, declared_role=source.role,
            summary=json.loads(self.files[source.path / "summary_metrics.json"]),
            metadata=json.loads(self.files[source.path / "metadata.json"])) for source in broken.sources]
        binding = writer.load_campaign_policy(REPO / "configs/campaign_policies/quiet_mac_p2_production.json")
        core = writer._idle_admission_core_evaluation(
            evaluations, binding, whole_window=True, runs_root=self.runs,
            neg8_drift_bound=self.bound, evaluation_timestamp_s=2000).core
        self.assertEqual(core["neg8_bracket"]["decision"], "failed")
        self.assertIn("neg8_bracket_missing", core["neg8_bracket"]["conditions"])
        self.assertEqual(core["neg8_bracket"]["claim_families"], {})

    def test_a_bundleless_blocked_spare_does_not_erase_the_writers_sources(self):
        from scripts import run_campaign as writer

        self.manifest("end", ["end-spare"], name="spare", execution="blocked_before_invoke")
        with mock.patch.object(writer._window_lineage, "is_hazard_runs_root", return_value=True):
            membership = writer._whole_window_campaign_membership(
                self.runs, self.policy_sha, self.runs / "campaign_log.jsonl")
        self.assertEqual(len(membership.source_manifests), 4)
        self.assertEqual(len(membership.sources), 7)
        self.assertEqual(membership.conditions, ())

    def test_bundleless_spare_and_empty_sources_screen_survivors(self):
        self.add_bundleless_spare()
        self.put(self.runs / "end-2" / "summary_metrics.json", self.summary("end-2", "failed"))
        losses = [("start-2", "contention.request_overlap"), ("end-2", "member.admission_aborted")]
        old = sealed_harvest()
        with mock.patch.object(old, "write_json_once", self.write):
            old_source, old_record = self.screen(self.harvest(old, losses=losses))
        self.assertEqual(old_source, "screen_failed")
        self.assertFalse(old_record["rescreen"]["evaluated"])
        self.assertEqual(old_record["rescreen"]["problems"], ["source_manifests_unrecorded"])
        for path in list(self.files):
            if self.root / "derived" in path.parents or self.root / "withheld" in path.parents:
                del self.files[path]
        run = self.harvest(losses=losses)
        source, record = self.screen(run)
        self.assertEqual(source, "survivor_rescreen")
        self.assertTrue(record["rescreen"]["evaluated"])
        self.assertEqual(record["rescreen"]["survivors"]["reference_counts"],
                         {"start": 2, "midpoint": 1, "end": 2})
        self.assertEqual(record["harvest_reference_losses"]["end-spare"], "bundle_absent")
        self.assertEqual(record["rescreen"]["reference_source"]["source"],
                         "claim_campaign_manifests_authenticated")
        self.assertEqual(record["bound_used"], "corpus_physics_clean")
        self.assertNotIn("end-spare", self.energy_reads)
        self.assertNotIn("start-2", self.energy_reads)
        self.assertNotIn("end-2", self.energy_reads)

    def test_roleless_evaluation_basis_does_not_erase_failed_and_absent_references(self):
        self.add_bundleless_spare()
        self.put(self.runs / "end-2" / "summary_metrics.json", self.summary("end-2", "failed"))
        included = [run_id for run_id in self.points if run_id != "end-2"]
        self.row["bundle_ids"] = included
        self.row["evaluation_scope"].update({"runs_root": str(self.runs), "started_at": STAMP})
        occurrences = []
        for run_id in included:
            occurrence = {"bundle_id": run_id, "bundle_path": run_id}
            for name, field in (("config.json", "config_sha256"), ("metadata.json", "metadata_sha256"),
                                ("summary_metrics.json", "summary_sha256")):
                occurrence[field] = hashlib.sha256(self.files[self.runs / run_id / name]).hexdigest()
            occurrences.append(occurrence)
        self.row["evaluation_basis"] = ww.build_evaluation_basis(
            policy_sha256=self.policy_sha, member_occurrences=occurrences, calibration_bracket=None)
        self.assertIsNotNone(ww._validated_evaluation_basis(self.row, self.runs))
        source, record = self.screen(self.harvest(losses=[("start-2", "contention.request_overlap")]))
        self.assertEqual(source, "survivor_rescreen")
        self.assertEqual(record["rescreen"]["survivors"]["reference_counts"],
                         {"start": 2, "midpoint": 1, "end": 2})
        self.assertEqual({item["bundle_id"]: item["reason"]
                          for item in record["rescreen"]["survivors"]["reference_losses"]},
                         {"start-2": "contention.request_overlap", "end-2": "status_not_succeeded",
                          "end-spare": "bundle_absent"})

    def test_invalid_evaluation_basis_is_not_rescued(self):
        self.row["evaluation_basis"] = {"member_occurrences": [], "sha256": "0" * 64}
        source, record = self.screen(self.harvest(losses=[("start-2", "contention.request_overlap")]))
        self.assertEqual(source, "screen_failed")
        self.assertEqual(record["rescreen"]["problems"], ["evaluation_basis_invalid"])

    def test_fewer_than_two_survivors_still_fail(self):
        self.add_bundleless_spare()
        run = self.harvest(losses=[("start-1", "contention.request_overlap"),
                                   ("start-2", "contention.request_overlap")])
        source, record = self.screen(run)
        self.assertEqual(source, "screen_failed")
        self.assertTrue(record["rescreen"]["evaluated"])
        failed = next(flag for flag in run.flags.records if flag["code"] == "neg8.screen_failed")
        self.assertEqual(failed["observed"]["reason"], "references_insufficient")

    def test_statistic_exceeding_bound_still_fails(self):
        for run_id in self.ids["end"]:
            self.points[run_id] = 110.0
            self.put(self.runs / run_id / "summary_metrics.json", self.summary(run_id))
        source, record = self.screen(self.harvest())
        self.assertEqual(source, "screen_failed")
        self.assertIn(ww.CONDITION_NEG8_GROSS_POINT_DRIFT_EXCEEDED, record["rescreen"]["conditions"])

    def test_more_references_than_planned_still_fail(self):
        self.points["end-extra"] = 100.0
        self.put(self.runs / "end-extra" / "config.json", {"run_id": "end-extra"})
        self.put(self.runs / "end-extra" / "summary_metrics.json", self.summary("end-extra"))
        self.put(self.runs / "end-extra" / "metadata.json", {"run_id": "end-extra"})
        self.manifest("end", ["end-extra"], name="extra")
        self.extra_roster.append({"run_id": "end-extra", "spare_slot": "end"})
        source, record = self.screen(self.harvest())
        self.assertEqual(source, "screen_failed")
        self.assertIn("neg8_bracket_reference_invalid", record["rescreen"]["conditions"])

    def test_unreadable_energy_reference_is_lost_before_reduction(self):
        summary = self.summary("start-2")
        del summary["energy_anchor_shift_envelopes"]
        self.put(self.runs / "start-2" / "summary_metrics.json", summary)
        source, record = self.screen(self.harvest())
        self.assertEqual(source, "survivor_rescreen")
        self.assertEqual(record["harvest_reference_losses"]["start-2"], "energy_unreadable")
        self.assertNotIn("start-2", self.energy_reads)

    def test_unauthenticated_manifest_still_fails(self):
        self.add_bundleless_spare()
        path = self.runs / "campaign_manifests" / "spare.json"
        self.files[path] += b" "  # current bytes no longer match the writer's attestation
        source, record = self.screen(self.harvest(losses=[("start-2", "contention.request_overlap")]))
        self.assertEqual(source, "screen_failed")
        self.assertEqual(record["rescreen"]["problems"], ["source_manifest_unauthenticated"])
        self.assertEqual(self.energy_reads, [])

    def test_policy_difference_still_fails(self):
        self.manifest("end", ["end-spare"], name="spare", policy_sha="0" * 64)
        source, record = self.screen(self.harvest(losses=[("start-2", "contention.request_overlap")]))
        self.assertEqual(source, "screen_failed")
        self.assertEqual(record["rescreen"]["problems"], ["source_manifest_policy_differs"])

    def test_strict_and_custody_invalid_references_are_lost(self):
        self.triangle_invalid.add("start-2")
        run = self.harvest(invalid=["end-2"])
        source, record = self.screen(run)
        self.assertEqual(source, "survivor_rescreen")
        losses = record["rescreen"]["survivors"]["reference_losses"]
        self.assertEqual({item["bundle_id"]: item["reason"] for item in losses},
                         {"start-2": "strict_invalid", "end-2": "strict_invalid"})
        self.assertNotIn("start-2", self.energy_reads)
        self.assertNotIn("end-2", self.energy_reads)

    def test_recovery_requires_a_clean_bound(self):
        run = self.harvest(clean=False)
        run.neg8_clean_bound_required = False
        run.neg8_collected_bound = self.bound
        source, record = self.screen(run)
        self.assertEqual(source, "screen_failed")
        self.assertEqual(record["rescreen"]["problems"], ["clean_bound_unavailable"])

    def test_recorded_sources_are_byte_identical_to_the_sealed_harvest(self):
        old = sealed_harvest()
        descriptors = [{"path": str(path.relative_to(self.runs)), "sha256": hashlib.sha256(raw).hexdigest()}
                       for path, raw in sorted(self.files.items()) if path.parent == self.runs / "campaign_manifests"]
        row = copy.deepcopy(self.row)
        row["row_provenance"]["source_campaign_manifests"] = descriptors
        sources = h.verdict_neg8_sources(row, self.runs)
        self.assertNotIsInstance(sources, str)
        bracket, problem = ww._derived_neg8_decision(
            sources[0], self.runs, sources[2], current=True, point_drift=True,
            drift_bound_artifact=self.bound, return_bracket=True, freshness_evaluated_at_s=2000)
        self.assertIsNone(problem)
        row["idle_admission_core"] = {"conditions": [], "neg8_bracket": bracket}
        snapshots = []
        for module in (old, h):
            for path in list(self.files):
                if self.root / "derived" in path.parents or self.root / "withheld" in path.parents:
                    del self.files[path]
            with mock.patch.object(module, "write_json_once", self.write):
                run = self.harvest(module, losses=[("start-2", "contention.request_overlap")])
                run.inputs.plan = None  # recorded sources bypass the prospective gate
                source, _ = self.screen(run, row)
                run.neg8_allowance(row, source)
                snapshots.append((source, copy.deepcopy(run.flags.records),
                                  {str(path): raw for path, raw in self.files.items()
                                   if run.derived in path.parents or run.withheld in path.parents}))
        self.assertEqual(snapshots[0], snapshots[1])

    def test_invalid_recorded_digest_is_never_rescued_by_catalog(self):
        self.row["row_provenance"]["source_campaign_manifests"] = [{
            "path": "campaign_manifests/start.json", "sha256": "0" * 64}]
        source, record = self.screen(self.harvest(losses=[("start-2", "contention.request_overlap")]))
        self.assertEqual(source, "screen_failed")
        self.assertEqual(record["rescreen"]["problems"], ["source_manifest_unauthenticated"])

    def test_missing_source_field_and_absent_bracket_use_authenticated_catalog(self):
        self.row.pop("row_provenance")
        self.row["idle_admission_core"]["neg8_bracket"] = None
        source, record = self.screen(self.harvest())
        self.assertEqual(source, "survivor_rescreen")
        self.assertTrue(record["rescreen"]["evaluated"])

    def test_malformed_source_descriptor_does_not_switch_sources(self):
        self.row["row_provenance"]["source_campaign_manifests"] = [{"path": "../elsewhere"}]
        source, record = self.screen(self.harvest(losses=[("start-2", "contention.request_overlap")]))
        self.assertEqual(source, "screen_failed")
        self.assertEqual(record["rescreen"]["problems"], ["source_manifest_path_invalid"])

    def test_duplicate_invoked_member_does_not_switch_to_a_smaller_set(self):
        self.manifest("start", ["start-0"], name="duplicate")
        source, record = self.screen(self.harvest(losses=[("start-2", "contention.request_overlap")]))
        self.assertEqual(source, "screen_failed")
        self.assertEqual(record["rescreen"]["problems"], ["source_manifest_members_invalid"])

    def test_legacy_pair_cannot_pass_catalog_recovery(self):
        for path in list(self.files):
            if self.runs in path.parents:
                del self.files[path]
        for slot in ("start", "end"):
            run_id = self.ids[slot][0]
            self.put(self.runs / run_id / "config.json", {"run_id": run_id})
            self.put(self.runs / run_id / "summary_metrics.json", self.summary(run_id))
            self.put(self.runs / run_id / "metadata.json", {"run_id": run_id})
            self.manifest(slot, [run_id])
        source, record = self.screen(self.harvest())
        self.assertEqual(source, "screen_failed")
        self.assertEqual(record["rescreen"]["survivors"]["survivor_screen"], "references_insufficient")
        self.assertTrue(record["rescreen"]["survivors"]["midpoint_lost"])

    def cannot_run(self, run, word):
        source, record = self.screen(run)
        self.assertEqual(source, "screen_failed")
        self.assertFalse(record["rescreen"]["evaluated"])
        self.assertEqual(record["rescreen"]["problems"], [word])
        expected = {"source": "claim_campaign_manifests_unauthenticated",
                    "verdict_sources_problem": "source_manifests_unrecorded", "campaign_sources_problem": word}
        self.assertEqual(record["rescreen"]["reference_source"], expected)
        failed = next(flag for flag in run.flags.records if flag["code"] == "neg8.screen_failed")
        self.assertEqual(failed["observed"]["reference_source"], expected)
        run.neg8_allowance(self.row, source)
        allowance = json.loads(self.files[run.archive / ww.NEG8_HARVEST_ALLOWANCE_RECORD])
        self.assertEqual(allowance["reference_source"], expected)

    def test_program_gate_constants_and_order(self):
        self.assertEqual(h.ERRATUM_2_ADMITTED_AT, "2026-10-10T16:30:00Z")
        self.assertEqual(h._epoch_s(h.ERRATUM_2_ADMITTED_AT), h.ERRATUM_2_ADMITTED_AT_EPOCH_S)
        run = self.harvest()
        with mock.patch.object(h, "claim_neg8_sources") as catalog:
            for plan in (None, {}, {"hazard_window": {"t0_epoch_s": h.ERRATUM_2_ADMITTED_AT_EPOCH_S + 1}},
                         *({"t0_epoch_s": value} for value in (
                             h.ERRATUM_2_ADMITTED_AT_EPOCH_S - 1, h.ERRATUM_2_ADMITTED_AT_EPOCH_S,
                             None, True, "1791649801", float("nan"), float("inf")))):
                with self.subTest(plan=plan):
                    run.inputs.plan = plan
                    self.assertEqual(run._neg8_sources(self.row, self.runs), "recovery_predates_erratum")
            catalog.assert_not_called()
            run.inputs.plan = self.plan
            run._neg8_sources(self.row, self.runs)
            catalog.assert_called_once()

    def test_ungoverned_t0_discloses_cannot_run(self):
        run = self.harvest(clean=False)
        run.inputs.plan = {"t0_epoch_s": h.ERRATUM_2_ADMITTED_AT_EPOCH_S}
        self.hazard_root.return_value = False
        self.cannot_run(run, "recovery_predates_erratum")

    def test_non_hazard_root_is_first_item_zero_failure(self):
        run = self.harvest()
        self.hazard_root.return_value = False
        self.row["idle_admission_core"]["conditions"] = ["whole_window_campaign_membership_ambiguous"]
        self.cannot_run(run, "runs_root_not_hazard")

    def test_stored_membership_must_be_unresolved_without_ambiguity_or_refusal(self):
        run = self.harvest()
        for conditions in ([], ["whole_window_campaign_membership_ambiguous"],
                           ["whole_window_campaign_membership_unresolved",
                            "whole_window_campaign_membership_ambiguous"],
                           ["whole_window_campaign_membership_unresolved",
                            ww.REASON_CAMPAIGN_OCCURRENCE_SUPERSESSION_MULTIPLE_ROWS]):
            with self.subTest(conditions=conditions):
                self.row["idle_admission_core"]["conditions"] = conditions
                self.assertEqual(run._neg8_sources(self.row, self.runs), "membership_condition_not_unresolved")

    def test_no_absent_invoked_member_precedes_ambiguity_and_supersession(self):
        run = self.harvest(ensure_trigger=False)
        for name in ("config.json", "summary_metrics.json"):
            self.files[self.runs / "second-directory" / name] = self.files[self.runs / "start-0" / name]
        self.files[self.runs / "campaign_log.jsonl"] += b'{"record_type":"campaign_occurrence_supersession"}\n'
        self.cannot_run(run, "no_absent_invoked_member")

    def test_ambiguous_second_directory_precedes_supersession(self):
        run = self.harvest()
        for name in ("config.json", "summary_metrics.json"):
            self.files[self.runs / "second-directory" / name] = self.files[self.runs / "start-0" / name]
        self.files[self.runs / "campaign_log.jsonl"] += b'{"record_type":"campaign_occurrence_supersession"}\n'
        self.cannot_run(run, "invoked_member_ambiguous")

    def test_occurrence_supersession_row_even_without_id_blocks_recovery(self):
        run = self.harvest()
        self.files[self.runs / "campaign_log.jsonl"] += (
            json.dumps({"schema_version": ww.OCCURRENCE_SUPERSESSION_SCHEMA}) + "\n").encode()
        self.cannot_run(run, "occurrence_supersession_present")

    def test_v1_manifest_cannot_supply_recovery(self):
        run = self.harvest()
        path = self.runs / "campaign_manifests" / "start.json"
        value = json.loads(self.files[path])
        value["schema_version"] = cp.CAMPAIGN_PROVENANCE_SCHEMA_V1
        self.put(path, value)
        self.cannot_run(run, "source_manifest_schema_v1")

    def test_empty_catalog_is_unrecorded(self):
        run = self.harvest()
        for path in list(self.files):
            if path.parent == self.runs / "campaign_manifests":
                del self.files[path]
        self.cannot_run(run, "source_manifests_unrecorded")

    def test_all_v1_catalog_without_log_is_schema_v1(self):
        run = self.harvest()
        for path in list(self.files):
            if path.parent == self.runs / "campaign_manifests":
                manifest = json.loads(self.files[path])
                manifest["schema_version"] = cp.CAMPAIGN_PROVENANCE_SCHEMA_V1
                self.put(path, manifest)
        del self.files[self.runs / "campaign_log.jsonl"]
        self.cannot_run(run, "source_manifest_schema_v1")

    def test_reference_outside_roster_or_at_wrong_slot_cannot_run(self):
        run = self.harvest()
        run.roster["members"] = [member for member in run.roster["members"] if member["run_id"] != "start-0"]
        self.assertEqual(run._neg8_sources(self.row, self.runs), "reference_not_in_roster")
        run.roster["members"].append({"run_id": "start-0", "spare_slot": "end"})
        self.cannot_run(run, "reference_not_in_roster")

    def test_surviving_reference_outside_basis_cannot_run(self):
        self.basis([run_id for run_id in self.points if run_id != "start-0"])
        run = self.harvest()
        self.assertIsNotNone(ww._validated_evaluation_basis(self.row, self.runs))
        self.cannot_run(run, "reference_not_in_verdict_basis")
        self.assertNotIn("start-0", self.energy_reads)

    def test_survivor_hash_mismatch_against_valid_basis_cannot_run(self):
        for changed in ("config.json", "metadata.json", "summary_metrics.json"):
            with self.subTest(changed=changed):
                for name in ("config.json", "metadata.json", "summary_metrics.json"):
                    value = json.loads(self.files[self.runs / "start-0" / name])
                    if name == "config.json":
                        value["run_id"] = "basis-copy"
                    if name == changed:
                        value["basis_copy_marker"] = True
                    self.put(self.runs / "basis-copy" / name, value)
                self.basis(paths={"start-0": "basis-copy"})
                run = self.harvest()
                self.assertIsNotNone(ww._validated_evaluation_basis(self.row, self.runs))
                self.assertEqual(run._neg8_sources(self.row, self.runs)[1], True)
                self.assertEqual(run._neg8_basis_reference_check(self.row, self.runs)("start-0", self.runs / "start-0"),
                                 "reference_not_in_verdict_basis")
        self.cannot_run(run, "reference_not_in_verdict_basis")
        self.assertNotIn("start-0", self.energy_reads)

    def test_changed_bytes_at_basis_path_are_evaluation_basis_invalid(self):
        run = self.harvest()
        self.files[self.runs / "start-0" / "metadata.json"] += b" "
        self.cannot_run(run, "evaluation_basis_invalid")

    def test_missing_basis_cannot_run(self):
        self.cannot_run(self.harvest(ensure_basis=False), "evaluation_basis_invalid")

    def test_lost_reference_need_not_be_in_basis(self):
        self.basis([run_id for run_id in self.points if run_id != "start-0"])
        run = self.harvest(losses=[("start-0", "contention.request_overlap")])
        source, record = self.screen(run)
        self.assertEqual(source, "survivor_rescreen")
        self.assertTrue(record["rescreen"]["evaluated"])
        self.assertNotIn("start-0", self.energy_reads)

    def test_recovery_disclosure_in_allowance_is_exact(self):
        run = self.harvest()
        source, record = self.screen(run)
        expected = {"source": "claim_campaign_manifests_authenticated",
                    "verdict_sources_problem": "source_manifests_unrecorded"}
        self.assertEqual(record["rescreen"]["reference_source"], expected)
        run.neg8_allowance(self.row, source)
        allowance = json.loads(self.files[run.archive / ww.NEG8_HARVEST_ALLOWANCE_RECORD])
        self.assertEqual(allowance["reference_source"], expected)
        self.assertEqual(allowance["source"], "survivor_rescreen")
        self.assertEqual(allowance["survivor_bracket"], record["survivor_bracket"])

    def test_missing_clean_bound_disclosure_is_exact(self):
        run = self.harvest(clean=False)
        run.neg8_clean_bound_required = False
        run.neg8_collected_bound = self.bound
        self.cannot_run(run, "clean_bound_unavailable")

    def test_recovery_never_uses_collected_or_stored_bound(self):
        self.row["idle_admission_core"]["neg8_bracket"]["drift_bound_artifact"] = self.bound
        run = self.harvest(clean=False)
        run.neg8_clean_bound_required = False
        run.neg8_collected_bound = self.bound
        self.cannot_run(run, "clean_bound_unavailable")

    def test_basis_check_compares_each_of_the_three_hashes(self):
        run = self.harvest()
        valid = ww._validated_evaluation_basis(self.row, self.runs)
        self.assertIsNotNone(valid)
        for field in ("config_sha256", "metadata_sha256", "summary_sha256"):
            with self.subTest(field=field):
                basis = copy.deepcopy(valid)
                next(item for item in basis["member_occurrences"]
                     if item["bundle_id"] == "start-0")[field] = "0" * 64
                with mock.patch.object(ww, "_validated_evaluation_basis", return_value=basis):
                    check = run._neg8_basis_reference_check(self.row, self.runs)
                self.assertEqual(check("start-0", self.runs / "start-0"),
                                 "reference_not_in_verdict_basis")
                self.assertIsNone(check("start-1", self.runs / "start-1"))

        check = run._neg8_basis_reference_check(self.row, self.runs)
        read = Path.read_bytes
        for name in ("config.json", "metadata.json", "summary_metrics.json"):
            with self.subTest(unreadable=name):
                unreadable = self.runs / "start-0" / name

                def read_with_failure(path):
                    if path == unreadable:
                        raise PermissionError(str(path))
                    return read(path)

                with mock.patch.object(Path, "read_bytes", read_with_failure):
                    self.assertEqual(check("start-0", self.runs / "start-0"),
                                     "reference_not_in_verdict_basis")
                    self.assertIsNone(check("start-1", self.runs / "start-1"))

    def test_insufficient_shape_midpoint_lost_matches_survivors(self):
        self.put(self.runs / "midpoint-0" / "summary_metrics.json", self.summary("midpoint-0", "failed"))
        run = self.harvest(losses=[("start-1", "contention.request_overlap"),
                                   ("start-2", "contention.request_overlap")])
        source, record = self.screen(run)
        self.assertEqual(source, "screen_failed")
        survivors = record["rescreen"]["survivors"]
        self.assertEqual(survivors["reference_counts"], {"start": 1, "midpoint": 0, "end": 3})
        self.assertTrue(survivors["midpoint_lost"])
        self.assertEqual(survivors["planned_reference_counts"], {"start": 3, "midpoint": 1, "end": 3})
        self.assertEqual(survivors["survivor_screen"], "references_insufficient")

    def test_no_surviving_reference_still_runs_current_shape_evaluator(self):
        run = self.harvest(losses=[(run_id, "contention.request_overlap") for run_id in self.points])
        source, record = self.screen(run)
        self.assertEqual(source, "screen_failed")
        self.assertTrue(record["rescreen"]["evaluated"])
        self.assertEqual(record["rescreen"]["survivors"]["reference_counts"],
                         {"start": 0, "midpoint": 0, "end": 0})
        self.assertTrue(record["rescreen"]["survivors"]["midpoint_lost"])
        self.assertEqual(self.energy_reads, [])

    def test_insufficient_shape_with_surviving_midpoint_records_midpoint_not_lost(self):
        self.add_bundleless_spare()
        run = self.harvest(losses=[("start-2", "contention.request_overlap"),
                                   ("end-1", "contention.request_overlap"),
                                   ("end-2", "member.admission_aborted")])
        source, record = self.screen(run)
        self.assertEqual(source, "screen_failed")
        survivors = record["rescreen"]["survivors"]
        self.assertEqual(survivors["reference_counts"], {"start": 2, "midpoint": 1, "end": 1})
        self.assertFalse(survivors["midpoint_lost"])
        self.assertEqual(survivors["survivor_screen"], "references_insufficient")
        self.assertNotIn("neg8.midpoint_lost", {flag["code"] for flag in run.flags.records})

    def test_noninvoked_references_never_count(self):
        self.manifest("start", ["existing-reference"], name="existing", execution="existing")
        self.manifest("midpoint", ["blocked-reference"], name="blocked", execution="blocked_before_invoke")
        source, record = self.screen(self.harvest())
        self.assertEqual(source, "survivor_rescreen")
        self.assertEqual(set(self.energy_reads), set(self.points))
        self.assertEqual(len(self.energy_reads), 7)
        self.assertEqual(record["harvest_reference_losses"], {})

    def test_malformed_present_source_list_never_enters_recovery(self):
        run = self.harvest()
        for value in (None, {}, "", 0, "malformed"):
            with self.subTest(value=value):
                self.row["row_provenance"]["source_campaign_manifests"] = value
                with mock.patch.object(h, "claim_neg8_sources") as catalog:
                    self.assertEqual(run._neg8_sources(self.row, self.runs), "source_manifests_unrecorded")
                    catalog.assert_not_called()

    def test_absent_spare_reason_and_retry_counts(self):
        self.add_bundleless_spare()
        self.put(self.runs / "end-2" / "summary_metrics.json", self.summary("end-2", "failed"))
        run = self.harvest(losses=[("end-spare", "member.timeout")])
        source, _ = self.screen(run)
        self.assertEqual(source, "survivor_rescreen")
        disclosed = next(flag for flag in run.flags.records if flag["code"] == "neg8.reference_lost")
        lost = next(item for item in disclosed["observed"]["lost"] if item["run_id"] == "end-spare")
        self.assertEqual(lost["reason"], "bundle_absent")
        self.assertEqual(lost["retry"], {"spares_measured": [], "spares_succeeded": []})

    def test_role_position_disagreement_fails_the_screen(self):
        self.manifest("start", self.ids["start"], sentinel_position="end")
        # The new snapshot is authenticated; remove its stale attestation so
        # only the reference-role error is under test.
        log = self.runs / "campaign_log.jsonl"
        rows = [json.loads(line) for line in self.files[log].splitlines()]
        self.files[log] = b"".join((json.dumps(row) + "\n").encode() for index, row in enumerate(rows)
                                  if index != 0)
        source, record = self.screen(self.harvest())
        self.assertEqual(source, "screen_failed")
        self.assertTrue(record["rescreen"]["evaluated"])
        self.assertIn("neg8_bracket_reference_invalid", record["rescreen"]["conditions"])

    def test_extra_member_with_disagreeing_role_fails_a_full_shape(self):
        self.points["odd"] = 100.0
        for name in ("config.json", "metadata.json"):
            self.put(self.runs / "odd" / name, {"run_id": "odd"})
        self.put(self.runs / "odd" / "summary_metrics.json", self.summary("odd"))
        self.manifest("start", ["odd"], name="odd", sentinel_position="end")
        source, record = self.screen(self.harvest())
        self.assertEqual(source, "screen_failed")
        self.assertIn("neg8_bracket_reference_invalid", record["rescreen"]["conditions"])

    def test_policy_unregistered_cannot_run(self):
        run = self.harvest()
        self.row["campaign_policy"]["sha256"] = "0" * 64
        self.cannot_run(run, "policy_unregistered")

    def test_roster_reference_with_unrecognized_role_fails_the_screen(self):
        path = self.runs / "campaign_manifests/start.json"
        manifest = json.loads(self.files[path])
        manifest["members"][0]["role"] = None
        raw = self.put(path, manifest)
        attestation = cp.campaign_provenance_attestation(
            manifest_path=path, raw_manifest_bytes=raw, manifest=manifest, timestamp=STAMP)
        self.files[self.runs / "campaign_log.jsonl"] += (json.dumps(attestation) + "\n").encode()
        source, record = self.screen(self.harvest())
        self.assertEqual(source, "screen_failed")
        self.assertTrue(record["rescreen"]["evaluated"])
        self.assertIn("neg8_bracket_reference_invalid", record["rescreen"]["conditions"])
        self.assertNotIn("start-0", self.energy_reads)

    def test_unsafe_bundle_id_cannot_run(self):
        self.manifest("science", ["../unsafe"], name="unsafe")
        self.cannot_run(self.harvest(), "source_manifest_members_invalid")

    def test_duplicate_absent_id_in_one_manifest_cannot_run(self):
        self.manifest("science", ["absent", "absent"], name="duplicates")
        self.cannot_run(self.harvest(), "source_manifest_members_invalid")

    def test_authenticated_manifest_path_outside_root_cannot_run(self):
        run = self.harvest()
        real = ww._safe_source_path
        with mock.patch.object(ww, "_safe_source_path", side_effect=lambda root, text:
                               None if text == "campaign_manifests/end.json" else real(root, text)):
            self.cannot_run(run, "source_manifest_path_invalid")

    def test_summary_unreadable_is_lost_before_reduction(self):
        del self.files[self.runs / "start-0/summary_metrics.json"]
        self.basis([run_id for run_id in self.points if run_id != "start-0"])
        source, record = self.screen(self.harvest())
        self.assertEqual(source, "survivor_rescreen")
        loss = next(item for item in record["rescreen"]["survivors"]["reference_losses"]
                    if item["bundle_id"] == "start-0")
        self.assertEqual(loss["reason"], "summary_unreadable")
        self.assertNotIn("start-0", self.energy_reads)

    def test_stored_neg8_conditions_decide_nothing_on_recovery(self):
        self.row["idle_admission_core"]["conditions"] += ["neg8_bracket_abs_delta_exceeded"]
        self.row["idle_admission_core"]["neg8_bracket"]["conditions"] += ["neg8_bracket_idle_sub_abs_delta_exceeded"]
        source, record = self.screen(self.harvest())
        self.assertEqual(source, "survivor_rescreen")
        self.assertEqual(record["rescreen"]["conditions"], [])

    def test_recorded_unauthenticated_sources_and_missing_bound_are_byte_identical(self):
        old = sealed_harvest()
        self.row["row_provenance"]["source_campaign_manifests"] = [
            {"path": "campaign_manifests/start.json", "sha256": "0" * 64}]
        snapshots = []
        for module in (old, h):
            for path in list(self.files):
                if self.root / "derived" in path.parents or self.root / "withheld" in path.parents:
                    del self.files[path]
            with mock.patch.object(module, "write_json_once", self.write):
                run = self.harvest(module, clean=False)
                source, _ = self.screen(run)
                run.neg8_allowance(self.row, source)
                snapshots.append((source, copy.deepcopy(run.flags.records),
                                  {str(path): raw for path, raw in self.files.items()
                                   if run.derived in path.parents or run.withheld in path.parents}))
        self.assertEqual(snapshots[0], snapshots[1])


if __name__ == "__main__":
    unittest.main()
