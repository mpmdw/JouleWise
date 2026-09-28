"""Battery authentication of every named window member."""

from __future__ import annotations

import json
import hashlib
import ast
import contextlib
import io
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import traceback
import unittest
from unittest.mock import patch

from joulewise import battery_float
from joulewise.battery_float import CustodyFailure, CustodyUnreadable
from joulewise.bundle import RunBundleWriter
from joulewise.bundle_read import WindowBatteryRefusal, authenticate_window_members
from joulewise.detection_floor import complete_bundle_sha256
from joulewise.clock import FakeClock
from tests.test_bundle_read import load_config

NAMED_RESIDUALS = {"joulewise/analysis_manifest_v3.py"}


class WindowMembersTests(unittest.TestCase):
    def pair_bundle(self, root: Path, run_id: str, *, charging: bool = False,
                    failed_probe: bool = False, real: bool = False) -> Path:
        hardware = json.loads((Path(__file__).parents[1] / "configs/examples/mock_local.json").read_text())["hardware_target"]
        if real:
            hardware["telemetry_backend"] = "powermetrics"
        writer = RunBundleWriter.create(root, load_config(run_id=run_id,
            hardware_target=hardware), FakeClock())
        pair = {}
        for phase, stamps in (("pre", (10, 20)), ("post", (90, 100))):
            relative = f"raw/battery_float.{phase}.ioreg"
            fixture = ("charging-synthetic-from-real.ioreg" if charging and phase == "pre"
                       else "float.ioreg")
            raw = (Path(__file__).parent / "fixtures/battery_float" / fixture).read_bytes()
            if failed_probe and phase == "post":
                raw = b""
            (writer.path / relative).write_bytes(raw)
            ticks = iter(stamps)
            pair[phase], _ = battery_float.observe(
                phase=f"bundle_{phase}", raw_path=relative, session_id=run_id,
                wall_time_s=1790373526, monotonic_ns=lambda ticks=ticks: next(ticks),
                runner=lambda argv, raw=raw: subprocess.CompletedProcess(
                    argv, 1 if failed_probe and phase == "post" else 0, raw, b""
                ),
            )
        writer.write_metadata({"battery_float": pair})
        rows = (
            ("stage_started", "idle_baseline", 30),
            ("stage_completed", "idle_drift_sentinel", 80),
        )
        (writer.path / "events.jsonl").write_text("".join(json.dumps({
            "timestamp_s": float(stamp), "event_type": event_type,
            "phase": phase, "message": "", "metadata": {"monotonic_ns": stamp},
        }) + "\n" for event_type, phase, stamp in rows))
        return writer.path

    def mock_bundle(self, root: Path, run_id: str) -> Path:
        writer = RunBundleWriter.create(root, load_config(run_id=run_id), FakeClock())
        writer.write_metadata({"battery_float": {
            "pre": None, "post": None, "not_applicable": "mock",
        }})
        return writer.path

    def test_12a_1_mixed_passing_real_still_refuses_mock(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            mock = self.mock_bundle(root, "mock")
            real = self.pair_bundle(root, "real", real=True)
            with self.assertRaises(WindowBatteryRefusal) as caught:
                authenticate_window_members((("mock", mock), ("real", real)),
                                            admit_mock_window=True)
            self.assertEqual([(row["label"], row["status"])
                              for row in caught.exception.members],
                             [("mock", "not_applicable")])  # all->any RED
            charging = self.pair_bundle(root, "charging", charging=True, real=True)
            missing = self.pair_bundle(root, "missing", failed_probe=True, real=True)
            with self.assertRaises(WindowBatteryRefusal) as all_refused:
                authenticate_window_members(
                    (("mock", mock), ("charging", charging), ("missing", missing)),
                    admit_mock_window=True)
            self.assertEqual([(row["label"], row["status"])
                              for row in all_refused.exception.members], [
                ("mock", "not_applicable"),
                ("charging", "battery_float_confounded"),
                ("missing", "battery_float_evidence_missing"),
            ])

    def test_12a_2_historical_member_blocks_mock_admission(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            mock = self.mock_bundle(Path(tmp), "mock")
            historical = Path(__file__).parent / "fixtures/d078_r01"
            with self.assertRaises(WindowBatteryRefusal) as caught:
                authenticate_window_members((("mock", mock), ("historical", historical)),
                                            admit_mock_window=True)
            self.assertEqual(caught.exception.members[0]["label"], "mock")
            self.assertEqual(caught.exception.members[0]["status"], "not_applicable")

    def test_12a_3_empty_obligation_returns_empty(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            writer = RunBundleWriter.create(Path(tmp), load_config(run_id="early"), FakeClock())
            writer.write_metadata({"battery_float": {
                "pre": None, "post": None, "not_reached": "prepare",
            }})
            self.assertEqual(authenticate_window_members(
                (("early", writer.path),), admit_mock_window=True), {})

    def test_12a_5_changed_mock_config_refuses(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            mock = self.mock_bundle(Path(tmp), "mock")
            config = mock / "config.json"
            config.write_bytes(config.read_bytes() + b" ")
            with self.assertRaises(WindowBatteryRefusal) as caught:
                authenticate_window_members((("mock", mock),), admit_mock_window=True)
            self.assertEqual(caught.exception.members[0]["status"],
                             "battery_float_evidence_missing")
            self.assertIn("not bound", " ".join(caught.exception.members[0]["reasons"]))

    def test_12a_6_nonmock_marker_refuses(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            real = self.pair_bundle(Path(tmp), "real", real=True)
            metadata_path = real / "metadata.json"
            metadata = json.loads(metadata_path.read_text())
            metadata["battery_float"] = {"pre": None, "post": None,
                                         "not_applicable": "mock"}
            metadata_path.write_text(json.dumps(metadata))
            with self.assertRaises(WindowBatteryRefusal) as caught:
                authenticate_window_members((("real", real),), admit_mock_window=True)
            self.assertEqual(caught.exception.members[0]["status"],
                             "battery_float_evidence_missing")

    def test_12a_7_missing_metadata_still_raises_custody(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            mock = self.mock_bundle(root, "mock")
            missing = root / "missing"
            missing.mkdir()
            with self.assertRaises(CustodyUnreadable) as caught:
                authenticate_window_members((("mock", mock), ("missing", missing)),
                                            admit_mock_window=True)
            self.assertEqual(caught.exception.window_member, "missing")

    def test_12a_10_mixed_aggregate_refuses_before_member_read(self) -> None:
        from joulewise import aggregate
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.mock_bundle(root, "mock")
            self.pair_bundle(root, "real", real=True)
            with patch.object(aggregate, "_read_member", side_effect=AssertionError(
                "per-member read happened before whole-set gate")) as read:
                with self.assertRaises(WindowBatteryRefusal) as caught:
                    aggregate.aggregate_experiment(root, {"members": ["mock", "real"]},
                                                   admit_mock_window=True)
            read.assert_not_called()
            self.assertEqual(caught.exception.members[0]["status"], "not_applicable")

    def test_12a_8_mock_records_visible_but_analysis_refused(self) -> None:
        from joulewise.analysis_engine.inputs import load_analysis_inputs
        from joulewise.controller import run_experiment
        from joulewise.environment import subprocess as environment_subprocess
        from tests.test_experiment import make_config, fake_environment_run
        import tests.test_run_campaign as campaign_test

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            experiment_root = root / "experiment-runs"
            with patch.object(environment_subprocess, "run", side_effect=fake_environment_run):
                manifest_path, members = run_experiment(
                    make_config("mock-experiment", repetitions=2),
                    experiment_root, FakeClock(),
                )
            experiment = json.loads(manifest_path.read_text())
            self.assertEqual(experiment["aggregate"]["battery_float_members"],
                             {path.name: "not_applicable" for path, _ in members})

            config_dir = root / "campaign-configs"
            runs_dir = root / "campaign-runs"
            config_dir.mkdir()
            manifest = campaign_test.write_strict_analysis_campaign(config_dir, runs_dir)
            evidence = {entry["run_id"]: "recovered" for entry in manifest["entries"]}
            evidence[manifest["entries"][0]["run_id"]] = "first_run_exempt"
            campaign_test.write_prior_campaign_provenance(
                runs_dir, evidence, campaign_test.analysis_manifest_id(config_dir))
            probe = root / "identity-probe"
            probe.write_text("#!/bin/sh\nprintf 'Tue Sep 8 01:02:03 2026 S\\n'\n")
            probe.chmod(0o755)
            with patch.dict(os.environ, {
                "JOULEWISE_CUSTODY_PARENT": str(root / "custody"),
                "JOULEWISE_ADDITIONAL_CUSTODY_PARENTS": "[]",
                "JOULEWISE_IDENTITY_PROBE": str(probe),
            }):
                completed = campaign_test.run_campaign(config_dir, runs_dir)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            rows = campaign_test.read_all_jsonl(runs_dir / "campaign_log.jsonl")
            completion = rows[-1]
            self.assertEqual(completion["record_type"], "campaign_verdict")
            self.assertTrue(completion["battery_float_members"])
            self.assertEqual(set(completion["battery_float_members"].values()),
                             {"not_applicable"})
            self.assertTrue({entry["run_id"] for entry in manifest["entries"]}
                            .issubset(completion["battery_float_members"]))
            self.assertEqual(completion["claim_readiness"]["verdict"],
                             "ready_for_analysis")
            artifact = root / "analysis-artifact.json"
            with self.assertRaises(WindowBatteryRefusal) as caught:
                load_analysis_inputs(config_dir / "analysis_manifest.json", runs_dir,
                                     root / "floor-artifact.json",
                                     strict_validator=lambda *_: ())
            self.assertEqual({row["label"] for row in caught.exception.members},
                             {entry["run_id"] for entry in manifest["entries"]})
            self.assertFalse(artifact.exists())

    def test_12a_11_axi_paired_entry_gate_stays_strict(self) -> None:
        import scripts.run_campaign as campaign
        import tests.test_run_campaign as campaign_test

        config_root = Path(__file__).parent / "fixtures/axi_ap_spec"
        state = campaign.load_analysis_manifest(config_root)
        self.assertIsNotNone(state)
        binding = campaign.load_campaign_policy(str(campaign_test.TEST_CAMPAIGN_POLICY))
        entries = sorted(state.raw["entries"], key=lambda row: row["order_index"])
        dispatched = iter(entries)

        def child(command, *, env, outer_authentication, bundle_paths):
            entry = next(dispatched)
            bundle_path = bundle_paths[0]
            config_path = campaign._resolve_analysis_reference(config_root, entry["config"])
            from joulewise.schemas import BenchmarkConfig
            config = json.loads(config_path.read_text())
            config["run_id"] = bundle_path.name
            writer = RunBundleWriter.create(
                bundle_path.parent, BenchmarkConfig.from_mapping(config), FakeClock())
            writer.write_metadata({"battery_float": {
                "pre": None, "post": None, "not_applicable": "mock",
            }})
            (writer.path / "summary_metrics.json").write_text('{"status":"succeeded"}\n')
            return subprocess.CompletedProcess(command, 0)

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            runs = root / "runs"
            log = runs / "campaign_log.jsonl"
            probe = root / "identity-probe"
            probe.write_text("#!/bin/sh\nprintf 'Tue Sep 8 01:02:03 2026 S\\n'\n")
            probe.chmod(0o755)
            from joulewise.measurement_liveness import Identity
            with (patch.dict(os.environ, {
                      "JOULEWISE_CUSTODY_PARENT": str(root / "custody"),
                      "JOULEWISE_ADDITIONAL_CUSTODY_PARENTS": "[]",
                      "JOULEWISE_IDENTITY_PROBE": str(probe),
                  }),
                  patch.object(campaign, "observe_identity",
                               return_value=Identity("LIVE", "Tue Sep 8 01:02:03 2026")),
                  patch.object(campaign, "run_authenticated_campaign_child", side_effect=child),
                  patch.object(campaign, "campaign_environment_preflight",
                               return_value={"admitted": True}),
                  patch.object(campaign, "campaign_cooldown_before_member",
                               return_value={"result": "recovered"}),
                  patch.object(campaign, "validate_bundle", side_effect=lambda *_args, **_kwargs: [])):
                self.assertIs(campaign.run_axi_spec_campaign.__globals__["validate_bundle"],
                              campaign.validate_bundle)
                with self.assertRaises(WindowBatteryRefusal) as caught:
                    campaign.run_axi_spec_campaign(
                        campaign.argparse.Namespace(
                            dry_run=False, cli_cmd=None, arm_quiet_mode=False,
                            arm_countdown_s=0, environment_override=None,
                        ), state, runs_dir=runs, policy_binding=binding, log_path=log)
            self.assertEqual(len(caught.exception.members), len(entries))
            self.assertEqual({row["status"] for row in caught.exception.members},
                             {"not_applicable"})
            self.assertFalse((runs / "axi_attempt_evidence" / state.manifest_id /
                              "attempt_ledger.jsonl").exists())
            if log.exists():
                rows = [json.loads(line) for line in log.read_text().splitlines()]
                self.assertFalse([row for row in rows if row.get("record_type") in {
                    "campaign_verdict", "idle_admission_whole_window_verdict"}])

    def test_12a_4_strict_window_consumers_refuse_mock(self) -> None:
        from joulewise import aggregate, floor_extraction, window_duration_margins
        from joulewise.calibration_ledger import CalibrationLedgerSnapshot, LEDGER_SCHEMA
        from joulewise.whole_window import AuthenticatedConsumptionSession
        import scripts.extract_detection_floors as floor_cli
        import scripts.mint_floor_artifact as mint
        import scripts.run_campaign as campaign
        from joulewise.analysis_engine.inputs import load_analysis_inputs
        import tests.test_run_campaign as campaign_test

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bundle = self.mock_bundle(root, "mock")
            spec = {"cells": [{"members": [{"bundle_id": "mock"}]}]}
            snapshot = CalibrationLedgerSnapshot(
                ledger_schema=LEDGER_SCHEMA, ledger_path=root / "ledger.jsonl",
                head_sequence=0, head_digest="a" * 64, receipts=(),
                observations=(), refusal_reasons=(),
            )
            policy = campaign.load_campaign_policy(
                str(Path(__file__).parent / "fixtures/campaign_policy_test.json")).policy
            cases = []
            cases.append(("aggregate/make_figures", lambda:
                aggregate.aggregate_experiment(root, {"members": ["mock"]})))
            session = AuthenticatedConsumptionSession(
                root, {"mock"}, calibration_ledger_snapshot=snapshot)
            cases.append(("whole_window._prepare", lambda:
                session._prepare(bundle_paths={"mock": bundle}, policy=policy)))
            cases.append(("floor_extraction", lambda:
                floor_extraction.extract_cells(root, spec,
                    calibration_ledger_snapshot=snapshot)))
            spec_path = root / "extraction-spec.json"
            spec_path.write_text(json.dumps(spec))
            floor_output = root / "floor-extraction.json"
            cases.append(("extract_detection_floors.main", lambda:
                floor_cli.main(["--runs-root", str(root), "--spec", str(spec_path),
                                "--out", str(floor_output)])))
            pack = root / "pack"
            pack.mkdir()
            cases.append(("window_duration_margins", lambda:
                window_duration_margins.derive_window_duration_margins(
                    repository_root=Path(__file__).parents[1], pack_root=pack,
                    runs_root=root, pack_identity="fixture")))
            report_path = root / "mint-report.json"
            report_path.write_text(json.dumps({
                "schema_version": mint.EXTRACTION_SCHEMA_VERSION,
                "spec_schema_version": mint.EXTRACTION_SPEC_SCHEMA_VERSION,
                "spec_membership_refusals": [], "idle_admission_refusals": [],
                "runs_root": str(root),
            }))
            order_path = root / "mint-order.json"
            order_path.write_text("{}")
            plan_path = root / "mint-plan.json"
            plan_path.write_text("{}")
            mint_paths = mint.ComponentPaths(
                evidence_root_id="fixture", evidence_root=root,
                report_path=report_path, spec_path=spec_path,
                order_manifest_path=order_path, calibration_cell_id="cell",
                expected_kind="absolute",
            )
            mint_output = root / "mint-floor.json"
            cases.append(("mint_floor_artifact", lambda:
                mint.mint_floor_artifact(
                    artifact_id="fixture", floor_path=mint_output,
                    statement_path=root / "statement.json",
                    calibration_plan_path=plan_path,
                    calibration_plan_relative_path="mint-plan.json",
                    absolute_paths=mint_paths, comparative_paths=mint_paths,
                    project_commit="a" * 40, project_tree_state="clean",
                    strict_validator=lambda *_: (),
                    calibration_ledger_snapshot=snapshot)))
            for name, call in cases:
                with self.subTest(consumer=name):
                    if name == "floor_extraction":
                        context = patch.object(floor_extraction,
                                               "validate_extraction_spec", return_value=[])
                    elif name == "window_duration_margins":
                        context = contextlib.ExitStack()
                        context.enter_context(patch.object(window_duration_margins,
                            "_pack_inventory", return_value=("a", "b", [object()])))
                        context.enter_context(patch.object(window_duration_margins,
                            "_resolve_member_paths", return_value={"mock": bundle}))
                    elif name == "mint_floor_artifact":
                        context = contextlib.ExitStack()
                        context.enter_context(patch.object(mint,
                            "validate_extraction_spec", return_value=[]))
                        context.enter_context(patch.object(mint,
                            "_target_spec_cell", return_value={}))
                        context.enter_context(patch.object(mint,
                            "_target_report_cell", return_value={}))
                        context.enter_context(patch.object(mint,
                            "_report_members", return_value=([], {})))
                        context.enter_context(patch.object(mint,
                            "_verify_report_widths", return_value=None))
                        context.enter_context(patch.object(mint,
                            "_spec_member_ids", return_value={"mock"}))
                    else:
                        context = contextlib.nullcontext()
                    with context, self.assertRaises(WindowBatteryRefusal) as caught:
                        call()
                    self.assertEqual([(row["label"], row["status"])
                                      for row in caught.exception.members],
                                     [("mock", "not_applicable")])
            self.assertFalse(floor_output.exists())
            self.assertFalse(mint_output.exists())

            config_dir = root / "analysis-configs"
            analysis_runs = root / "analysis-runs"
            config_dir.mkdir()
            campaign_test.write_strict_analysis_campaign(config_dir, analysis_runs)
            with self.assertRaises(WindowBatteryRefusal) as caught:
                load_analysis_inputs(config_dir / "analysis_manifest.json",
                                     analysis_runs, root / "unused-floor.json",
                                     strict_validator=lambda *_: ())
            self.assertEqual({row["status"] for row in caught.exception.members},
                             {"not_applicable"})
            self.assertFalse((root / "analysis-artifact.json").exists())

    def test_passing_pair_returns_verdict(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle = self.pair_bundle(Path(tmp), "passing")
            verdicts = authenticate_window_members((("passing", bundle),))
            self.assertEqual(verdicts["passing"].status, "pass")
            self.assertEqual(len(verdicts["passing"].bundle_sha256), 64)

    def test_recorded_member_digests_precede_status_refusals(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            good = self.pair_bundle(root, "recorded-good")
            (good / "summary_metrics.json").write_text("{}\n")
            recorded = {name: hashlib.sha256((good / name).read_bytes()).hexdigest()
                        for name in ("config.json", "metadata.json", "summary_metrics.json")}
            self.assertEqual(authenticate_window_members(
                (("recorded", good, recorded),))["recorded"].status, "pass")
            linked = root / "linked-recorded"
            linked.symlink_to(good, target_is_directory=True)
            with self.assertRaises(CustodyUnreadable):
                authenticate_window_members((("recorded-link", linked, recorded),))
            prospective = self.pair_bundle(root, "prospective")
            metadata = json.loads((prospective / "metadata.json").read_text())
            del metadata["battery_float"]
            (prospective / "metadata.json").write_text(json.dumps(metadata))
            (good / "summary_metrics.json").write_bytes(
                (good / "summary_metrics.json").read_bytes() + b" ")
            with self.assertRaises(CustodyFailure) as caught:
                authenticate_window_members((("prospective", prospective),
                                             ("recorded", good, recorded)))
            self.assertIs(type(caught.exception), CustodyFailure)
            self.assertEqual(caught.exception.window_member, "recorded")
            self.assertEqual(caught.exception.failures[0]["artifact"], "summary_metrics.json")
            (good / "config.json").unlink()
            with self.assertRaises(CustodyUnreadable) as caught:
                authenticate_window_members((("recorded", good, recorded),))
            self.assertEqual(caught.exception.window_member, "recorded")
            shutil.rmtree(good)
            with self.assertRaises(CustodyUnreadable) as caught:
                authenticate_window_members((("recorded", good, recorded),))
            self.assertEqual(caught.exception.window_member, "recorded")

    def test_recorded_digest_mismatch_is_custody(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle = self.pair_bundle(Path(tmp), "digest-mismatch")
            (bundle / "summary_metrics.json").write_text("{}\n")
            recorded = {name: hashlib.sha256((bundle / name).read_bytes()).hexdigest()
                        for name in ("config.json", "metadata.json", "summary_metrics.json")}
            (bundle / "summary_metrics.json").write_text("{} \n")
            with self.assertRaises(CustodyFailure) as caught:
                authenticate_window_members((("digest-mismatch", bundle, recorded),))
            self.assertIs(type(caught.exception), CustodyFailure)
            self.assertEqual(caught.exception.window_member, "digest-mismatch")
            self.assertEqual(caught.exception.failures[0]["artifact"],
                             "summary_metrics.json")

    def test_recorded_member_paths_need_a_nonnull_digest(self) -> None:
        from joulewise.whole_window import recorded_member_paths
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            basis = {"member_occurrences": [
                {"bundle_path": "written", "config_sha256": "a" * 64,
                 "metadata_sha256": None, "summary_sha256": None},
                {"bundle_path": "unwritten", "config_sha256": None,
                 "metadata_sha256": None, "summary_sha256": None},
            ]}
            (root / "campaign_log.jsonl").write_text(json.dumps({
                "record_type": "idle_admission_whole_window_verdict",
                "evaluation_basis": basis,
            }) + "\n")
            self.assertEqual(recorded_member_paths(root), frozenset({"written"}))

    def test_collection_evaluate_member_does_not_gate_charging(self) -> None:
        from scripts.run_campaign import ConfigInfo, MemberEvaluation, evaluate_member
        with tempfile.TemporaryDirectory() as tmp:
            bundle = self.pair_bundle(Path(tmp), "charging-collection", charging=True)
            info = ConfigInfo(path=bundle / "config.json", run_id=bundle.name,
                              raw_run_id=bundle.name, repetitions=1)
            evaluation = evaluate_member(bundle, info=info, waivers={})
            self.assertIsInstance(evaluation, MemberEvaluation)

    def test_finalized_axi_attempt_ledger_keeps_absent_bundle_in_gate(self) -> None:
        from joulewise.whole_window import recorded_axi_attempt_members
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            rows_dir = root / "axi_attempt_evidence" / "manifest" / "ledger_rows"
            rows_dir.mkdir(parents=True)
            (rows_dir / "attempt.jsonl").write_text(json.dumps({
                "entry_id": "entry", "attempt_ordinal": 1, "run_id": "run",
            }) + "\n")
            members = recorded_axi_attempt_members(root)
            self.assertEqual(members, [(
                "entry__a1__run",
                root / "axi_attempt_bundles" / "manifest" / "entry" / "a1" / "run",
            )])
            self.assertEqual(recorded_axi_attempt_members(root, {"manifest"}), members)
            self.assertEqual(recorded_axi_attempt_members(root, {"other"}), [])
            with self.assertRaises(CustodyUnreadable) as caught:
                authenticate_window_members(members)
            self.assertEqual(caught.exception.window_member, "entry__a1__run")

    def test_confounded_and_probe_missing_both_refuse(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            members = (
                ("charging", self.pair_bundle(root, "charging", charging=True)),
                ("probe", self.pair_bundle(root, "probe", failed_probe=True)),
            )
            with self.assertRaises(WindowBatteryRefusal) as caught:
                authenticate_window_members(members)
            self.assertEqual(
                [(row["label"], row["status"]) for row in caught.exception.members],
                [("charging", "battery_float_confounded"),
                 ("probe", "battery_float_evidence_missing")],
            )

    def test_missing_recorded_raw_is_custody_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle = self.pair_bundle(Path(tmp), "lost-raw")
            (bundle / "raw/battery_float.post.ioreg").unlink()
            with self.assertRaises(CustodyFailure):
                authenticate_window_members((("lost-raw", bundle),))

    def test_two_prospective_members_are_both_named(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            members = []
            for label in ("a", "b"):
                bundle = self.pair_bundle(root, label)
                config_path = bundle / "config.json"
                config = json.loads(config_path.read_text())
                config["hardware_target"]["telemetry_backend"] = "powermetrics"
                config_path.write_text(json.dumps(config))
                metadata_path = bundle / "metadata.json"
                metadata = json.loads(metadata_path.read_text())
                metadata["config_sha256"] = hashlib.sha256(config_path.read_bytes()).hexdigest()
                del metadata["battery_float"]
                metadata_path.write_text(json.dumps(metadata))
                members.append((label, bundle))
            with self.assertRaises(WindowBatteryRefusal) as caught:
                authenticate_window_members(members)
            self.assertEqual([(row["label"], row["status"], row["bundle_sha256"])
                              for row in caught.exception.members],
                             [(label, "battery_float_evidence_missing", complete_bundle_sha256(path))
                              for label, path in members])

    def test_digest_bound_invalid_config_is_window_status_refusal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            writer = RunBundleWriter.create(
                Path(tmp), load_config(run_id="invalid-bound-window"), FakeClock()
            )
            writer.write_metadata({})
            config_path = writer.path / "config.json"
            config_path.write_text("[]")
            metadata_path = writer.path / "metadata.json"
            metadata = json.loads(metadata_path.read_text())
            metadata["config_sha256"] = hashlib.sha256(config_path.read_bytes()).hexdigest()
            metadata_path.write_text(json.dumps(metadata))
            with self.assertRaises(WindowBatteryRefusal) as caught:
                authenticate_window_members((("invalid-bound-window", writer.path),))
            self.assertEqual(caught.exception.members[0]["label"], "invalid-bound-window")
            self.assertEqual(caught.exception.members[0]["status"], "battery_float_evidence_missing")
            self.assertRegex(
                caught.exception.members[0]["reasons"][0],
                r"^prospective bundle \(config\.json does not re-validate",
            )

    def test_confounded_then_prospective_names_both(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            charging = self.pair_bundle(root, "charging", charging=True)
            prospective = self.pair_bundle(root, "prospective")
            config_path = prospective / "config.json"
            config = json.loads(config_path.read_text())
            config["hardware_target"]["telemetry_backend"] = "powermetrics"
            config_path.write_text(json.dumps(config))
            metadata_path = prospective / "metadata.json"
            metadata = json.loads(metadata_path.read_text())
            metadata["config_sha256"] = hashlib.sha256(config_path.read_bytes()).hexdigest()
            del metadata["battery_float"]
            metadata_path.write_text(json.dumps(metadata))
            with self.assertRaises(WindowBatteryRefusal) as caught:
                authenticate_window_members((("charging", charging), ("prospective", prospective)))
            self.assertEqual([(row["label"], row["status"]) for row in caught.exception.members],
                             [("charging", "battery_float_confounded"),
                              ("prospective", "battery_float_evidence_missing")])

    def test_custody_second_member_has_label_note_and_original_failures(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = self.pair_bundle(root, "good")
            second = self.pair_bundle(root, "bad")
            (second / "raw/battery_float.post.ioreg").unlink()
            with self.assertRaises(CustodyFailure) as direct:
                battery_float.authenticate_bundle(second)
            with self.assertRaises(CustodyFailure) as caught:
                authenticate_window_members((("good", first), ("member-7", second)))
            exc = caught.exception
            self.assertIs(type(exc), CustodyFailure)
            self.assertEqual(exc.window_member, "member-7")
            self.assertIn("window member: member-7", exc.__notes__)
            self.assertIn("member-7", "".join(traceback.format_exception(exc)))
            self.assertEqual(exc.failures, direct.exception.failures)

    def test_historical_member_returns_digest_bound_verdict(self) -> None:
        bundle = Path(__file__).parent / "fixtures/d078_r01"
        verdicts = authenticate_window_members((("historical", bundle),))
        self.assertEqual(verdicts["historical"].status, "unobserved_historical")
        self.assertEqual(len(verdicts["historical"].bundle_sha256), 64)

    def test_all_nonpass_members_are_named(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            members = []
            for label in ("mock-a", "mock-b"):
                writer = RunBundleWriter.create(root, load_config(run_id=label), FakeClock())
                writer.write_metadata({"battery_float": {
                    "pre": None, "post": None, "not_applicable": "mock",
                }})
                members.append((label, writer.path))
            with self.assertRaises(WindowBatteryRefusal) as caught:
                authenticate_window_members(members)
            self.assertEqual([row["label"] for row in caught.exception.members],
                             ["mock-a", "mock-b"])
            self.assertTrue(all(row["status"] == "not_applicable" and
                                len(row["bundle_sha256"]) == 64
                                for row in caught.exception.members))

    def test_not_reached_has_no_obligation_without_baseline_start(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            writer = RunBundleWriter.create(Path(tmp), load_config(run_id="early"), FakeClock())
            writer.write_metadata({"battery_float": {
                "pre": None, "post": None, "not_reached": "prepare",
            }})
            self.assertEqual(authenticate_window_members((("early", writer.path),)), {})

    def test_not_reached_with_baseline_start_refuses(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            writer = RunBundleWriter.create(Path(tmp), load_config(run_id="late"), FakeClock())
            writer.write_metadata({"battery_float": {
                "pre": None, "post": None, "not_reached": "warmup",
            }})
            (writer.path / "events.jsonl").write_text(json.dumps({
                "timestamp_s": 1.0, "event_type": "stage_started",
                "phase": "idle_baseline", "message": "", "metadata": {"monotonic_ns": 1},
            }) + "\n")
            with self.assertRaises(WindowBatteryRefusal) as caught:
                authenticate_window_members((("late", writer.path),))
            self.assertEqual(caught.exception.members[0]["label"], "late")
            self.assertEqual(caught.exception.members[0]["status"],
                             "battery_float_evidence_missing")

    def test_unreadable_second_metadata_is_custody(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            first = Path(tmp) / "first"
            second = Path(tmp) / "second"
            writer = RunBundleWriter.create(Path(tmp), load_config(run_id="first"), FakeClock())
            writer.write_metadata({"battery_float": {
                "pre": None, "post": None, "not_applicable": "mock",
            }})
            second.mkdir()
            (second / "metadata.json").write_text("{")
            with self.assertRaisesRegex(CustodyUnreadable, "second") as caught:
                authenticate_window_members((("first", first), ("second", second)))
            self.assertEqual(caught.exception.window_member, "second")

    def test_aggregate_authenticates_failed_member_before_numbers(self) -> None:
        from joulewise.aggregate import aggregate_experiment
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.pair_bundle(root, "passing")
            failed = self.pair_bundle(root, "failed", charging=True)
            (failed / "summary_metrics.json").write_text(json.dumps({"status": "failed"}))
            with self.assertRaises(WindowBatteryRefusal) as caught:
                aggregate_experiment(root, {"members": ["passing", "failed"]})
            self.assertEqual([(row["label"], row["status"])
                              for row in caught.exception.members],
                             [("failed", "battery_float_confounded")])

    def test_aggregate_exposes_historical_battery_state(self) -> None:
        from joulewise.aggregate import aggregate_experiment
        fixtures = Path(__file__).parent / "fixtures"
        result = aggregate_experiment(fixtures, {"members": ["d078_r01"]})
        self.assertEqual(result["battery_float_members"],
                         {"d078_r01": "unobserved_historical"})

    def test_campaign_helper_includes_superseded_ordinary_and_axi_attempts(self) -> None:
        from scripts.run_campaign import (
            OrdinaryOccurrenceResolution, WholeWindowMemberSource,
            WholeWindowMembershipResolution, _authenticate_whole_window_members,
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            selected = self.pair_bundle(root, "selected")
            superseded = self.pair_bundle(root, "superseded", charging=True)
            membership = WholeWindowMembershipResolution(
                sources=(WholeWindowMemberSource(path=selected),),
                source_manifests=(), conditions=(), occurrence_supersessions=(),
                occurrence_resolutions=(OrdinaryOccurrenceResolution(
                    bundle_id="selected", status="selected", present_paths=(selected, superseded)
                ),),
            )
            with self.assertRaises(WindowBatteryRefusal) as caught:
                _authenticate_whole_window_members(membership, root)
            self.assertIn(str(superseded), [row["label"] for row in caught.exception.members])
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base = root / "axi_attempt_bundles" / "manifest" / "entry"
            (base / "a1").mkdir(parents=True)
            (base / "a2").mkdir(parents=True)
            old = self.pair_bundle(base / "a1", "old", charging=True)
            selected = self.pair_bundle(base / "a2", "selected")
            membership = WholeWindowMembershipResolution(
                sources=(WholeWindowMemberSource(path=selected),),
                source_manifests=(), conditions=(), occurrence_supersessions=(),
            )
            with self.assertRaises(WindowBatteryRefusal) as caught:
                _authenticate_whole_window_members(membership, root)
            self.assertIn(str(old), [row["label"] for row in caught.exception.members])

    def test_eight_consumer_modules_call_reader_gate_without_battery_import(self) -> None:
        root = Path(__file__).resolve().parents[1]
        paths = (
            "joulewise/whole_window.py", "joulewise/analysis_engine/inputs.py",
            "joulewise/floor_extraction.py", "joulewise/aggregate.py",
            "joulewise/window_duration_margins.py", "scripts/mint_floor_artifact.py",
            "scripts/extract_detection_floors.py", "scripts/run_campaign.py",
        )
        for relative in paths:
            with self.subTest(path=relative):
                tree = ast.parse((root / relative).read_text())
                calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)
                         and ((isinstance(node.func, ast.Name)
                               and node.func.id == "authenticate_window_members")
                              or (isinstance(node.func, ast.Attribute)
                                  and node.func.attr == "authenticate_window_members"))]
                self.assertTrue(calls, relative)
                self.assertFalse(any(
                    (isinstance(node, ast.ImportFrom) and
                     ("battery_float" in (node.module or "") or
                      any(alias.name == "battery_float" for alias in node.names)))
                    or (isinstance(node, ast.Import) and any(
                        "battery_float" in alias.name for alias in node.names))
                    for node in ast.walk(tree)
                ), relative)

    def test_consumer_broad_handlers_pass_gate_exceptions_unchanged(self) -> None:
        root = Path(__file__).resolve().parents[1]
        paths = (
            "joulewise/whole_window.py", "joulewise/analysis_engine/inputs.py",
            "joulewise/floor_extraction.py", "joulewise/aggregate.py",
            "joulewise/window_duration_margins.py", "scripts/mint_floor_artifact.py",
            "scripts/extract_detection_floors.py", "scripts/run_campaign.py",
        )
        for relative in paths:
            tree = ast.parse((root / relative).read_text())
            self.assertTrue(any(
                isinstance(node, ast.ImportFrom)
                and node.module == "joulewise.bundle_read"
                and any(alias.name == "GATE_EXCEPTIONS" for alias in node.names)
                for node in ast.walk(tree)), relative)
            for node in ast.walk(tree):
                if not isinstance(node, ast.Try):
                    continue
                broad = [handler for handler in node.handlers if handler.type is None
                         or any(isinstance(part, ast.Name) and part.id in
                                {"RuntimeError", "Exception", "BaseException"}
                                for part in ast.walk(handler.type))]
                if not broad or all(isinstance(handler.body[-1], ast.Raise)
                                    and handler.body[-1].exc is None for handler in broad):
                    continue
                first = node.handlers[0]
                self.assertIsInstance(first.type, ast.Name, (relative, node.lineno))
                self.assertEqual(first.type.id, "GATE_EXCEPTIONS", (relative, node.lineno))
                self.assertEqual(len(first.body), 1, (relative, node.lineno))
                self.assertIsInstance(first.body[0], ast.Raise, (relative, node.lineno))
                self.assertIsNone(first.body[0].exc, (relative, node.lineno))

    def test_only_named_ninth_module_converts_gate_exceptions(self) -> None:
        root = Path(__file__).resolve().parents[1]
        consumers = {
            "joulewise/whole_window.py", "joulewise/analysis_engine/inputs.py",
            "joulewise/floor_extraction.py", "joulewise/aggregate.py",
            "joulewise/window_duration_margins.py", "scripts/mint_floor_artifact.py",
            "scripts/extract_detection_floors.py", "scripts/run_campaign.py",
        }
        names = subprocess.check_output(
            ["git", "ls-files", "joulewise", "scripts"], cwd=root, text=True
        ).splitlines()
        residuals = set()
        for relative in names:
            if not relative.endswith(".py") or relative in consumers:
                continue
            tree = ast.parse((root / relative).read_text())
            for statement in ast.walk(tree):
                if not isinstance(statement, ast.Try):
                    continue
                calls = [node for line in statement.body for node in ast.walk(line)
                         if isinstance(node, ast.Call)]
                if not any((isinstance(call.func, ast.Name) and call.func.id in
                            {"authenticate_window_members", "_prepare"}) or
                           (isinstance(call.func, ast.Attribute) and call.func.attr in
                            {"authenticate_window_members", "_prepare"})
                           for call in calls):
                    continue
                for handler in statement.handlers:
                    broad = handler.type is None or any(
                        isinstance(part, ast.Name) and part.id in
                        {"RuntimeError", "Exception", "BaseException"}
                        for part in ast.walk(handler.type))
                    reraises = (isinstance(handler.body[-1], ast.Raise)
                                and handler.body[-1].exc is None)
                    if broad and not reraises:
                        residuals.add(relative)
        self.assertEqual(residuals, NAMED_RESIDUALS)

    def test_claim_readiness_has_no_tracked_external_reader(self) -> None:
        root = Path(__file__).resolve().parents[1]
        names = subprocess.check_output(
            ["git", "ls-files", "joulewise", "scripts"], cwd=root, text=True
        ).splitlines()
        readers = {relative for relative in names if relative.endswith(".py")
                   and "claim_readiness" in (root / relative).read_text()}
        self.assertEqual(readers, {"scripts/run_campaign.py"})


class ProductionSupersessionGateTests(unittest.TestCase):
    def _upgrade(self, bundle: Path, *, charging: bool = False) -> None:
        metadata_path = bundle / "metadata.json"
        metadata = json.loads(metadata_path.read_text())
        run_id = json.loads((bundle / "config.json").read_text())["run_id"]
        (bundle / "raw").mkdir(exist_ok=True)
        pair = {}
        for phase, stamps in (("pre", (10, 20)), ("post", (90, 100))):
            relative = f"raw/battery_float.{phase}.ioreg"
            fixture = ("charging-synthetic-from-real.ioreg" if charging and phase == "pre"
                       else "float.ioreg")
            raw = (Path(__file__).parent / "fixtures/battery_float" / fixture).read_bytes()
            (bundle / relative).write_bytes(raw)
            ticks = iter(stamps)
            pair[phase], _ = battery_float.observe(
                phase=f"bundle_{phase}", raw_path=relative, session_id=run_id,
                wall_time_s=1790373526, monotonic_ns=lambda ticks=ticks: next(ticks),
                runner=lambda argv, raw=raw: subprocess.CompletedProcess(argv, 0, raw, b""),
            )
        metadata["battery_float"] = pair
        metadata["run_id"] = run_id
        metadata["config_sha256"] = hashlib.sha256((bundle / "config.json").read_bytes()).hexdigest()
        metadata_path.write_text(json.dumps(metadata) + "\n")
        (bundle / "events.jsonl").write_text("".join(json.dumps({
            "timestamp_s": float(stamp), "event_type": event,
            "phase": phase, "message": "", "metadata": {"monotonic_ns": stamp},
        }) + "\n" for event, phase, stamp in (
            ("stage_started", "idle_baseline", 30),
            ("stage_completed", "idle_drift_sentinel", 80),
        )))

    def _fixture(self, *, charging: bool = False):
        import tests.test_run_campaign as campaign_tests
        case = campaign_tests.IdleAdmissionCoreVerdictTests(
            "test_campaign_core_callers_keep_replacement_custody_replay_only")
        case.setUp()
        self.addCleanup(case.doCleanups)
        binding = case._binding()
        self._drift_bound = case._write_drift_bound()
        _members, work_id, quarantine = case._retry_occurrence_fixture(binding)
        for path in (case.root / work_id, quarantine):
            self._upgrade(path, charging=charging and path == quarantine)
        for path in case.root.iterdir():
            if (path / "metadata.json").is_file() and path.name != work_id:
                self._upgrade(path)
        return case.root, binding, work_id, quarantine

    def _record(self, root, binding, work_id, quarantine):
        from scripts import run_campaign as campaign
        args = campaign.parse_args([
            "--record-supersession", work_id, "--quarantine-path", str(quarantine),
            "--reason", "failed member moved before retry", "--runs-dir", str(root),
            "--campaign-policy", str(binding.path),
        ])
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(campaign.run_record_supersession(args), 0)

    def _verdict(self, root, binding):
        from scripts import run_campaign as campaign
        args = campaign.parse_args([
            "--whole-window-verdict", "--runs-dir", str(root),
            "--campaign-policy", str(binding.path),
            "--neg8-drift-bound", str(self._drift_bound),
        ])
        with (contextlib.redirect_stdout(io.StringIO()),
              patch.object(campaign, "validate_bundle", return_value=[]),
              patch.object(campaign, "calibration_bracket_for_bundles", return_value=(
                  {"schema_version": "joulewise.instrument_calibration_bracket.v1",
                   "status": "passed", "pre": {"evidence_sha256": "a" * 64},
                   "post": {"evidence_sha256": "b" * 64},
                   "b_fiducial_s": 0.02}, ()))):
            return campaign.run_whole_window_verdict(args)

    def test_production_quarantine_battery_or_custody_refuses_before_row(self) -> None:
        from joulewise.whole_window import (supersession_record_field_valid,
                                            supersession_entry_validation_results)
        for scenario in ("charging", "deleted", "altered", "charged_deleted"):
            with self.subTest(scenario=scenario):
                root, binding, work_id, quarantine = self._fixture(
                    charging=scenario in {"charging", "charged_deleted"})
                self._record(root, binding, work_id, quarantine)
                log = root / "campaign_log.jsonl"
                before = log.read_text()
                entries, valid = supersession_entry_validation_results(root, log)
                self.assertEqual(valid, [True])
                if scenario in {"deleted", "charged_deleted"}:
                    shutil.rmtree(quarantine)
                elif scenario == "altered":
                    with (quarantine / "summary_metrics.json").open("ab") as handle:
                        handle.write(b" ")
                if scenario != "charging":
                    self.assertTrue(supersession_record_field_valid(entries[0], root))
                    self.assertEqual(supersession_entry_validation_results(root, log)[1], [False])
                expected = (WindowBatteryRefusal if scenario == "charging" else
                            CustodyFailure if scenario == "altered" else CustodyUnreadable)
                with self.assertRaises(expected) as caught:
                    self._verdict(root, binding)
                if scenario == "charging":
                    self.assertTrue(any(row["label"].startswith("superseded:") and
                                        row["status"] == "battery_float_confounded"
                                        for row in caught.exception.members))
                else:
                    self.assertTrue(caught.exception.window_member.startswith("superseded:"))
                if scenario == "altered":
                    self.assertIs(type(caught.exception), CustodyFailure)
                    self.assertEqual(caught.exception.failures[0]["artifact"],
                                     "summary_metrics.json")
                self.assertEqual(log.read_text(), before)

    def test_helper_authenticates_selected_and_quarantined_together(self) -> None:
        from scripts.run_campaign import (
            OrdinaryOccurrenceResolution, WholeWindowMemberSource,
            WholeWindowMembershipResolution, _authenticate_whole_window_members,
        )
        for charging in (False, True):
            with self.subTest(charging=charging):
                root, binding, work_id, quarantine = self._fixture(charging=charging)
                self._record(root, binding, work_id, quarantine)
                selected = root / work_id
                membership = WholeWindowMembershipResolution(
                    sources=(WholeWindowMemberSource(path=selected),),
                    source_manifests=(), conditions=(), occurrence_supersessions=(),
                    occurrence_resolutions=(OrdinaryOccurrenceResolution(
                        bundle_id=work_id, status="selected", present_paths=(selected,)
                    ),),
                )
                if charging:
                    with self.assertRaises(WindowBatteryRefusal) as caught:
                        _authenticate_whole_window_members(membership, root)
                    self.assertEqual(len(caught.exception.members), 1)
                    self.assertTrue(caught.exception.members[0]["label"].startswith("superseded:"))
                else:
                    verdicts = _authenticate_whole_window_members(membership, root)
                    self.assertEqual(len(verdicts), 2)
                    self.assertEqual({verdict.status for verdict in verdicts.values()}, {"pass"})
                    self.assertTrue(any(label.startswith("superseded:") for label in verdicts))

    def test_helper_reports_selected_and_superseded_statuses_in_one_refusal(self) -> None:
        from scripts.run_campaign import (
            OrdinaryOccurrenceResolution, WholeWindowMemberSource,
            WholeWindowMembershipResolution, _authenticate_whole_window_members,
        )
        root, binding, work_id, quarantine = self._fixture(charging=True)
        self._record(root, binding, work_id, quarantine)
        selected = root / work_id
        metadata_path = selected / "metadata.json"
        metadata = json.loads(metadata_path.read_text())
        del metadata["battery_float"]
        metadata_path.write_text(json.dumps(metadata) + "\n")
        membership = WholeWindowMembershipResolution(
            sources=(WholeWindowMemberSource(path=selected),),
            source_manifests=(), conditions=(), occurrence_supersessions=(),
            occurrence_resolutions=(OrdinaryOccurrenceResolution(
                bundle_id=work_id, status="selected", present_paths=(selected,)
            ),),
        )
        with self.assertRaises(WindowBatteryRefusal) as caught:
            _authenticate_whole_window_members(membership, root)
        self.assertEqual({row["status"] for row in caught.exception.members},
                         {"battery_float_evidence_missing", "battery_float_confounded"})

    def test_unrecorded_retry_and_malformed_record_do_not_pass(self) -> None:
        root, binding, _work_id, _quarantine = self._fixture()
        self.assertEqual(self._verdict(root, binding), 1)
        row = json.loads((root / "campaign_log.jsonl").read_text().splitlines()[-1])
        self.assertNotEqual(row["status"], "passed")
        self.assertIn("whole_window_campaign_membership_unresolved",
                      row["idle_admission_core"]["conditions"])

        root, binding, work_id, quarantine = self._fixture()
        self._record(root, binding, work_id, quarantine)
        log = root / "campaign_log.jsonl"
        entry = json.loads(log.read_text().splitlines()[0])
        entry["reason"] += " changed"
        log.write_text(json.dumps(entry) + "\n")
        self.assertEqual(self._verdict(root, binding), 1)
        row = json.loads(log.read_text().splitlines()[-1])
        self.assertNotEqual(row["status"], "passed")
        self.assertIn("whole_window_campaign_membership_ambiguous",
                      row["idle_admission_core"]["conditions"])

    def test_field_valid_rejects_inside_quarantine_after_path_normalization(self) -> None:
        from joulewise.whole_window import (supersession_entry_sha256,
                                            supersession_record_field_valid)
        root, binding, work_id, quarantine = self._fixture()
        self._record(root, binding, work_id, quarantine)
        entry = json.loads((root / "campaign_log.jsonl").read_text().splitlines()[0])
        entry["quarantine"]["path"] = str(root / ".." / root.name / "inside")
        entry["entry_sha256"] = supersession_entry_sha256(entry)
        self.assertFalse(supersession_record_field_valid(entry, root))

    def test_prior_verdict_recorded_member_cannot_disappear_from_next_gate(self) -> None:
        root, binding, work_id, quarantine = self._fixture()
        self._record(root, binding, work_id, quarantine)
        log = root / "campaign_log.jsonl"
        recorded = {"bundle_path": work_id,
                    "config_sha256": None,
                    "metadata_sha256": hashlib.sha256(
                        (root / work_id / "metadata.json").read_bytes()).hexdigest(),
                    "summary_sha256": None}
        with log.open("a") as handle:
            handle.write(json.dumps({
                "record_type": "idle_admission_whole_window_verdict",
                "evaluation_basis": {"member_occurrences": [recorded]},
            }) + "\n")
        before = log.read_text()
        shutil.rmtree(root / work_id)
        with self.assertRaises(CustodyUnreadable) as caught:
            self._verdict(root, binding)
        self.assertEqual(caught.exception.window_member, str(root / work_id))
        self.assertEqual(log.read_text(), before)

    def test_analysis_loader_authenticates_recorded_deleted_member(self) -> None:
        import tests.test_analysis_integration as fixture
        from joulewise.analysis_engine.inputs import load_analysis_inputs
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config_dir, runs_root = root / "configs", root / "runs"
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(fixture.generate_matrix([
                    "--base", str(fixture.BASE_CONFIG), "--model-tag", "mock-model",
                    "--out-dir", str(config_dir),
                ]), 0)
            with patch("joulewise.bundle._capture_source_state",
                       return_value=dict(fixture.CLEAN_SOURCE_STATE)):
                for config in sorted(config_dir.glob("*.json")):
                    if config.name in fixture.SIDECARS:
                        continue
                    with (contextlib.redirect_stdout(io.StringIO()),
                          contextlib.redirect_stderr(io.StringIO())):
                        self.assertEqual(fixture.main([
                            "run", str(config), "--runs-dir", str(runs_root)]), 0)
                    run_id = json.loads(config.read_text())["run_id"]
                    fixture.install_explicit_mock_sampler(runs_root / run_id)
            floor_path = root / "floor.json"
            floor_path.write_text(json.dumps(fixture.make_artifact(), indent=2) + "\n")
            manifest_path = config_dir / "analysis_manifest.json"
            manifest = json.loads(manifest_path.read_text())
            bundle_ids = sorted(entry["run_id"] for entry in manifest["entries"])
            fixture.install_passing_analysis_whole_window(
                runs_root, bundle_ids, source_name="analysis-whole-window-source")
            log = runs_root / "campaign_log.jsonl"
            rows = [json.loads(line) for line in log.read_text().splitlines()]
            for row in rows:
                if row.get("record_type") == "idle_admission_whole_window_verdict":
                    row["evaluation_basis"] = {"member_occurrences": [
                        {"bundle_path": bundle_id,
                         "config_sha256": hashlib.sha256(
                             (runs_root / bundle_id / "config.json").read_bytes()).hexdigest(),
                         "metadata_sha256": None, "summary_sha256": None}
                        for bundle_id in bundle_ids]}
            log.write_text("".join(json.dumps(row) + "\n" for row in rows))
            victim = bundle_ids[1]
            shutil.rmtree(runs_root / victim)
            with self.assertRaises(CustodyUnreadable) as caught:
                load_analysis_inputs(
                    manifest_path, runs_root, floor_path,
                    strict_validator=fixture.validate_bundle,
                )
            self.assertEqual(caught.exception.window_member, victim)


if __name__ == "__main__":
    unittest.main()
