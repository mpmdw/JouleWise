"""J4's W/R/H drop sets and collection import fence, synthetic references only."""
import contextlib
from dataclasses import replace
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from joulewise import whole_window as ww
from joulewise.b5 import harvest
from joulewise.neg8_survivors import neg8_reference_strict_invalid


class Neg8ParityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from tests import test_neg8_survivors as support
        from tests import test_harvest_b5_window as hb
        support.VerdictWriterSurvivorTests.setUpClass()
        cls.support, cls.hb = support, hb

    def test_three_drop_sets_writer_replay_frozen_harvest(self):
        helper = self.support.VerdictWriterSurvivorTests()
        with tempfile.TemporaryDirectory(prefix="s3-parity-") as temporary:
            helper.root = Path(temporary)
            members = helper.references((8.0, 8.02, 7.98), (8.01,), (8.01, 8.03, 7.99))
            rows = []
            for kind in ("clean", "triangle", "reduction_mismatch", "validator_raises", "status_failed",
                         "summary_absent", "summary_malformed", "energy_unreadable", "physics", "timeout", "abort", "identity"):
                with self.subTest(kind=kind):
                    root = Path(temporary) / kind
                    root.mkdir()
                    target = "neg8-end-r3"
                    candidates = []
                    manifests = []
                    problems = {target: ["synthetic reduction mismatch"]} if kind == "reduction_mismatch" else {}
                    for member in members:
                        summary = dict(member.summary)
                        status = member.status
                        summary["status"] = status
                        if member.bundle_id == target:
                            if kind == "status_failed":
                                status, summary = "failed", {"status": "failed"}
                            elif kind in {"summary_absent", "summary_malformed"}:
                                status, summary = None, None
                            elif kind == "energy_unreadable":
                                summary.pop("energy_anchor_shift_envelopes")
                        bundle = root / member.bundle_id
                        bundle.mkdir()
                        for name, value in (("config.json", {"run_id": member.bundle_id}), ("metadata.json", member.metadata)):
                            (bundle / name).write_text(json.dumps(value))
                        if summary is not None:
                            (bundle / "summary_metrics.json").write_text(json.dumps(summary))
                        elif kind == "summary_malformed" and member.bundle_id == target:
                            (bundle / "summary_metrics.json").write_text("{malformed")
                        manifests.append({"execution": "invoked", "run_id": member.bundle_id, "bundle_ids": [member.bundle_id],
                            "role": member.declared_role, "sentinel_position": member.sentinel_position,
                            "canonical_neg8_workload": True, "scientific_config_sha256": "d" * 64})
                        invalid = member.bundle_id == target and kind in {"triangle", "reduction_mismatch", "validator_raises"}
                        candidates.append(replace(member, bundle_path=bundle, status=status, summary=summary,
                            strict_valid=not invalid, validation_problems=("synthetic strict failure",) if invalid else ()))
                    # Drive the real writer's member-selection function too,
                    # including its exception path, before its core evaluator.
                    rc = helper.run_campaign
                    def writer_validator(path, **_kwargs):
                        if Path(path).name == target and kind == "validator_raises":
                            raise RuntimeError("synthetic strict validator failure")
                        return problems.get(Path(path).name, [])
                    with mock.patch.object(rc, "validate_bundle", side_effect=writer_validator), \
                            mock.patch.object(rc, "custody_telemetry_identity", side_effect=lambda path, **kwargs:
                                SimpleNamespace(custody_bound_config=Path(path).name == target and kind == "triangle",
                                                triangle_agrees=not (Path(path).name == target and kind == "triangle"))):
                        candidates = [rc._whole_window_member(rc.WholeWindowMemberSource(member.bundle_path,
                            run_id=member.bundle_id, role=member.declared_role, sentinel_position=member.sentinel_position,
                            scientific_config_sha256="d" * 64, canonical_neg8_workload=True), {}) for member in candidates]
                    stored = helper.bracket(candidates)
                    writer = {item["bundle_id"]: item["reason"] for item in stored.get("reference_losses", [])}
                    excluded = {member.bundle_id for member in candidates if not member.usable}
                    self.assertEqual(set(writer), excluded)
                    manifests = [{"members": manifests}]
                    policy = stored["policy"]
                    def triangle(path, *_args):
                        return Path(path).name == target and kind == "triangle"
                    def validator(path, **_kwargs):
                        if Path(path).name == target and kind == "validator_raises":
                            raise RuntimeError("synthetic strict validator failure")
                        return problems.get(Path(path).name, [])
                    def strict(bundle, path):
                        return neg8_reference_strict_invalid(path, validator=validator).invalid
                    exclude = {target: {"physics": "contention.request_overlap", "timeout": "member.timeout",
                        "abort": "member.admission_aborted", "identity": "model.identity_mismatch"}[kind]} \
                        if kind in {"physics", "timeout", "abort", "identity"} else {}
                    frozen = object.__new__(harvest._Harvest)
                    frozen.inputs = SimpleNamespace(claim_runs_root=root)
                    frozen.flags = SimpleNamespace(records=[{"code": code, "scope": {"level": "member", "run_id": bundle}}
                        for bundle, code in exclude.items()])
                    frozen.roster = {"members": [{"run_id": member.bundle_id, "neg8_slot": member.sentinel_position}
                        for member in candidates]}
                    frozen.neg8_reference_source = {"source": "verdict_source_manifests"}
                    frozen._neg8_sources = lambda _row, _root: (manifests, True, policy)
                    harvest_exclude = frozen._neg8_reference_losses({"idle_admission_core": {"neg8_bracket": stored}})
                    with contextlib.ExitStack() as stack:
                        stack.enter_context(mock.patch.object(ww, "_custody_strict_invalid", side_effect=triangle))
                        stack.enter_context(mock.patch.object(ww, "_scientific_config_identity", return_value=("d" * 64, True)))
                        stack.enter_context(mock.patch.object(ww, "_reference_energy_evidence", side_effect=lambda path, *_args, **_kwargs:
                            (ww._neg8_writer_reference_energy(next(m.summary for m in candidates if m.bundle_id == Path(path).name)) + (None,))))
                        stack.enter_context(mock.patch.object(ww, "build_neg8_freshness_observation", return_value=None))
                        options = dict(current=True, point_drift=True, return_bracket=True,
                            drift_bound_artifact=helper._drift_bound())
                        replay, problem = ww._derived_neg8_decision(manifests, root, policy, strict_invalid=strict,
                            stored_strict_losses={bundle for bundle, reason in writer.items() if reason == "strict_invalid"},
                            unlisted_strict_invalid="refuse", **options)
                        # Frozen harvest callback's value, plus its evaluator's
                        # own triangle leg; not just the callback by itself.
                        harvested, hproblem = ww._derived_neg8_decision(manifests, root, policy,
                            strict_invalid=lambda bundle, _path: next(m for m in candidates if m.bundle_id == bundle).strict_valid is False,
                            exclude_bundle_ids=harvest_exclude, unreadable_energy="lost", **options)
                    self.assertIsNone(problem)
                    self.assertIsNone(hproblem)
                    replay_losses = {item["bundle_id"]: item["reason"] for item in replay.get("reference_losses", [])}
                    harvest_losses = {item["bundle_id"]: item["reason"] for item in harvested.get("reference_losses", [])}
                    only = set(exclude) | {bundle for bundle, reason in harvest_losses.items() if reason in {"energy_unreadable", "bundle_absent"}}
                    comparable = set(harvest_losses) - only
                    self.assertEqual(set(writer), set(replay_losses), "reference_drop_parity_failed")
                    self.assertEqual(set(writer), comparable, "reference_drop_parity_failed")
                    rows.append({"case": kind, "W": writer, "R": replay_losses, "H": harvest_losses, "parity": "passed"})
            (Path(temporary) / "parity.json").write_text(json.dumps(rows, indent=2, sort_keys=True) + "\n")
            print("S3_PARITY_ROWS", len(rows), "PASS")

    def test_endpoint_mirror_equal_to_frozen_harvest(self):
        self.assertEqual(ww._NEG8_BOUND_DEPENDENT_FIELDS, harvest._NEG8_BOUND_DEPENDENT_FIELDS)
        values = [{"estimand": "same", "claim_families": {"gross_energy": {"start": {"point": 1}, "drift_allowance_j": None}}},
            {"estimand": "same", "claim_families": {}, "start_gross_j": None}, {}, None]
        for stored in values:
            for derived in values[:-1]:
                for unreadable in (False, True):
                    self.assertEqual(ww._neg8_reproduces(derived, stored, energy_unreadable=unreadable),
                        harvest._neg8_reproduces(derived, stored, energy_unreadable=unreadable))

    def test_import_fence(self):
        for module in ("scripts.run_campaign", "joulewise.b5.harvest"):
            code = "import importlib,sys; importlib.import_module(" + repr(module) + "); " + \
                "assert 'joulewise.neg8_survivors' not in sys.modules; " + \
                "assert not any(m == 'joulewise.b5_analysis' or m.startswith('joulewise.b5_analysis.') for m in sys.modules); print('IMPORT_FENCE_PASS')"
            result = subprocess.run([sys.executable, "-c", code], text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.strip(), "IMPORT_FENCE_PASS")


if __name__ == "__main__":
    unittest.main()
