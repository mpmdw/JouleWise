"""Synthetic audit probes; never capture hardware or call privileged setters.

Unrelated live/physics validators are fixture boundaries. The orchestration,
source census, roster, receipt reader, temporal budget and process census
under investigation remain the real production functions.
"""
from contextlib import ExitStack
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

from joulewise import arm_readiness as ar
from joulewise import network_time_off as off, v5_qualification as q
from scripts import harvest_v5_g2b_window as h, run_night as driver
from tests import test_harvest_v5_g2b_window as harvest_tests
put = harvest_tests.put
from tests import test_arm_readiness as arm_tests
from tests.test_night_gate import make_plan


class G2bHarness:
    def __init__(self):
        self.case = harvest_tests.G2bStructureTests()
        self.case.setUp()
        c = self.case
        c.install_verdict()
        self.root = c.base
        self.night_root = self.root / "night-custody"
        self.night = self.night_root / "night"
        put(self.night / "chain.started", {"pgid": 999999})
        put(self.night / "chain.exited", {"exit_code": 0})
        put(self.night_root / "night_plan.json", {})
        self.bound = self.root / "bound"
        put(self.bound / "campaign_manifests/bound.json", {"members": [{"bundle_ids": ["bound0"]}]})
        put(self.bound / "bound0/metadata.json", {})
        self.chain = self.root / "chain.zsh"
        self.chain.write_text("exit 0\n")
        self.sidecar = self.root / "chain.sha256"
        self.sidecar.write_text(q.sha(self.chain) + "\n")
        self.plan = SimpleNamespace(receipt_class="TRANSACTION_PACK", plan_id="s1-fixture", custody_root=str(self.night_root),
            measurement_root=str(h.ROOT), measurement_head="a" * 40,
            chain_path=str(self.chain), chain_sha256_path=str(self.sidecar),
            pack_night={"pack_id": "d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5", "pack_root": str(c.pack)})
        self.terminal = self.night / "transcript/post-bracket-terminal-boundary.json"
        put(self.terminal, {})
        put(self.night_root / "qualification-plan-record.json", {
            "terminal_boundary_path": str(self.terminal)})
        self.go = {"authorization": c.authorization, "boot_session_id": "fixture-boot"}
        for name in ("acceptance", "go", "consumption", "battery-boundaries"):
            put(self.root / f"{name}.json", {})
        put(self.root / "events.json", c.events)
        put(c.custody / "prospective/calibration_plan.json", {"plan_id": "frozen", "evidence_root_id": "evidence"})
        self.off_path = (self.night_root / self.plan.pack_night["pack_id"] /
                         "arm_readiness.t0.inputs" / off.RECEIPT_BASENAME)
        self.off_value = {"schema": off.SCHEMA, "argv": list(off.OFF_ARGV), "exit_code": 0,
            "stdout": "Network Time is already off\n", "stderr": "", "plan_id": self.plan.plan_id,
            "window_id": "frozen-window", "boot_id": "fixture-boot", "epoch_s": 1000., "monotonic_s": 1000.}
        put(self.off_path, self.off_value)
        meta = q.read(c.runs / c.ids[0] / "metadata.json")
        meta["battery_float"] = {"pre": {"wall_time_s": 1601., "monotonic_before_ns": 1601_000_000_000}}
        put(c.runs / c.ids[0] / "metadata.json", meta)
        self.input_path = self.root / "inputs.json"
        put(self.input_path, {"schema": h.INPUT_SCHEMA, "occurrence": "s1",
            "plan": q.reference(self.night_root / "night_plan.json"), "custody_root": str(c.custody),
            "policy": q.reference(h.ROOT / "configs/campaign_policies/quiet_mac_p2_production.json"),
            "acceptance": q.reference(self.root / "acceptance.json"), "bound_runs_root": str(self.bound),
            "terminal_boundary": q.reference(self.terminal),
            "go": q.reference(self.root / "go.json"), "consumption": q.reference(self.root / "consumption.json"),
            "battery_boundaries": q.reference(self.root / "battery-boundaries.json"),
            "desk_producer_events": q.reference(self.root / "events.json"),
            "auxiliary_bundle_ids": [], "bound_bundle_ids": ["bound0"]})
        self.args = SimpleNamespace(inputs=self.input_path, inputs_sha256=q.sha(self.input_path),
            archive_root=self.root / "archive-1", scratch_root=self.root, prepare_desk=False, previous_harvest=None)
        self.stack = ExitStack()
        self.desk = self.stack.enter_context(mock.patch.object(h, "desk_check", return_value=True))
        for obj, name, value in (
            (q, "load_plan", self.plan), (h, "authenticate_launch", self.go),
            # This harness covers STOP/OFF and harvest transport. The complete
            # native G10 custody tree is replayed separately by the X4 tests.
            (q, "g10_sources", {}),
            (h, "validate_whole_window_verdict_row", SimpleNamespace(authentic=True)),
            (h, "frozen_identity", ({"plan_id": "frozen"}, {}, {"window_id": "frozen-window", "evidence_root_id": "evidence"})),
            (h, "bracket_assessment", (SimpleNamespace(refusal_reasons=()), {}, {}, [])),
            (q, "battery_boundaries", True),
            (h, "battery_attempts", (True, [(c.ids[0], c.runs / c.ids[0])])),
            (h.brackets, "calibration_bracket_for_bundles", ({"status": "passed"}, ())),
        ):
            self.stack.enter_context(mock.patch.object(obj, name, return_value=value))
        self.stack.enter_context(mock.patch.object(h, "l10_a", side_effect=self.l10))

    def l10(self, custody, destination, bundle_ids, head, **kwargs):
        put(destination / "l10-a/record.json", {"status": "PASS"})
        return [{"run_id": bid, "valid": True, "clock_anchor_status": "bounded"}
                for bid in [*bundle_ids, "bound0"]], []

    def run(self):
        return h.harvest(self.args, clear=lambda *a, **k: True)

    def close(self):
        self.stack.close()
        self.case.doCleanups()


class HarvestReplayTests(unittest.TestCase):
    def fixture(self):
        fixture = G2bHarness()
        self.addCleanup(fixture.close)
        return fixture

    def test_pack_off_only_at_producer_path_and_pack_window_identity(self):
        f = self.fixture()
        self.assertFalse((f.night / off.RECEIPT_BASENAME).exists())
        plan = make_plan("TRANSACTION_PACK", custody_root=str(f.night_root), pack_night=f.plan.pack_night)
        self.assertEqual(q.off_receipt_path(plan), f.off_path)
        self.assertEqual(driver._chain_environment(plan, f.night)["JOULEWISE_NETWORK_TIME_OFF_RECEIPT"], str(f.off_path))
        result = f.run()
        self.assertEqual(result["verdict"], "PASS", result)
        wrong = dict(f.off_value, window_id=f.plan.plan_id)
        put(f.off_path, wrong)
        f.args.archive_root = f.root / "wrong-window"
        self.assertEqual(f.run()["verdict"], "REFUSED")

    def test_external_events_census_is_identical_across_reharvest(self):
        f = self.fixture()
        put(f.night / off.RECEIPT_BASENAME, dict(f.off_value, window_id=f.plan.plan_id))
        f.desk.side_effect = RuntimeError("transient tool fault")
        self.assertEqual(f.run()["verdict"], "REFUSED")
        original = (f.args.archive_root / "harvest.json").read_bytes()
        f.desk.side_effect = None
        f.args.previous_harvest = f.args.archive_root
        f.args.archive_root = f.root / "archive-2"
        self.assertEqual(f.run()["verdict"], "PASS")
        for name in ("replay-locators.json", "derived/desk-producer-events.json"):
            first = q.read(f.args.previous_harvest / name)
            second = q.read(f.args.archive_root / name)
            if name == "replay-locators.json":
                for document in (first, second):
                    for row in document["sources"]:
                        row.pop("archived_path")
            self.assertEqual(first, second)
        self.assertEqual(original, (f.args.previous_harvest / "harvest.json").read_bytes())

    def test_prepared_events_survive_refusal_before_launch_authentication(self):
        f = self.fixture()
        inputs = q.read(f.input_path); inputs.pop("desk_producer_events")
        put(f.input_path, inputs); f.args.inputs_sha256 = q.sha(f.input_path)
        f.args.prepare_desk = True
        with mock.patch.object(h, "prepare_desk", return_value=f.case.events) as prepare, \
             mock.patch.object(h, "authenticate_launch", side_effect=q.HarvestRefusal("transient_launch_tool_fault")):
            self.assertEqual(f.run()["verdict"], "REFUSED")
            prepare.assert_called_once()
        events = (f.args.archive_root / "derived/desk-producer-events.json").read_bytes()
        first = (f.args.archive_root / "harvest.json").read_bytes()
        f.args.previous_harvest = f.args.archive_root
        f.args.archive_root = f.root / "archive-2"; f.args.prepare_desk = False
        with mock.patch.object(h, "prepare_desk", side_effect=AssertionError("must not rerun producers")):
            result = f.run()
        self.assertEqual(result["verdict"], "PASS", result)
        self.assertEqual(events, (f.args.archive_root / "derived/desk-producer-events.json").read_bytes())
        self.assertEqual(first, (f.args.previous_harvest / "harvest.json").read_bytes())

    def test_prepare_fault_publishes_refusal_without_escaping(self):
        f = self.fixture(); f.args.prepare_desk = True
        with mock.patch.object(h, "prepare_desk", side_effect=KeyError("broken_tool")):
            result = f.run()
        self.assertEqual(result["verdict"], "REFUSED")
        self.assertEqual(q.read(f.args.archive_root / "harvest.json"), result)
        self.assertTrue((f.args.archive_root / "replay-locators.json").is_file())


class HistoricalArmReplayTests(unittest.TestCase):
    def fixture(self):
        case = arm_tests.PackNightConsumerTests(); case.setUp()
        self.addCleanup(case.doCleanups)
        case.consume()
        return case

    def test_harvester_does_not_derive_arm_again_at_later_head(self):
        case = self.fixture(); f = case.fixture
        plan_data = q.read(case.inputs["night_plan"])
        plan = SimpleNamespace(plan_id=plan_data["plan_id"], custody_root=str(f.custody), pack_night=plan_data["pack_night"])
        with mock.patch.object(ar, "reviewed_main", side_effect=AssertionError("today's head must not be read")), \
             mock.patch.object(ar, "_derive_arm_semantics_for_verification", side_effect=AssertionError("ARM is historical")):
            self.assertEqual(h.authenticate_launch(plan, case.inputs["go_receipt"], case.consumption)["purpose"], "G2B_SHAKEDOWN")

    def test_historical_expiry_replay_passes_after_window_completion(self):
        case = self.fixture(); f = case.fixture
        plan_data = q.read(case.inputs["night_plan"])
        plan = SimpleNamespace(plan_id=plan_data["plan_id"], custody_root=str(f.custody), pack_night=plan_data["pack_night"])
        with mock.patch.object(ar.time, "monotonic_ns", return_value=f.arm["valid_until_monotonic_ns"] + 10800 * 10**9):
            self.assertEqual(h.authenticate_launch(plan, case.inputs["go_receipt"], case.consumption)["purpose"], "G2B_SHAKEDOWN")

    def test_historical_replay_passes_from_other_checkout(self):
        case = self.fixture()
        self.assertEqual(case.verify(require_current_boot=False)["status"], "PASS")
        with mock.patch.object(ar, "__file__", str(Path(case.fixture.temporary.name) / "other/joulewise/arm_readiness.py")):
            self.assertEqual(case.verify(require_current_boot=False)["status"], "PASS")

    def test_live_replay_still_rejects_other_checkout_and_expired_arm(self):
        case = self.fixture()
        with mock.patch.object(ar, "__file__", str(Path(case.fixture.temporary.name) / "other/joulewise/arm_readiness.py")):
            with self.assertRaisesRegex(ar.LaunchLineageError, "launcher is not the planned clone"):
                case.verify()
        with mock.patch.object(ar.time, "monotonic_ns", return_value=case.fixture.arm["valid_until_monotonic_ns"] + 10800 * 10**9):
            with self.assertRaises(ar.LaunchLineageError):
                case.verify()

    def test_historical_launcher_root_may_be_absent_but_must_be_absolute_and_no_symlinks(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            missing = root / "offloaded-measurement-clone"
            self.assertEqual(ar._authenticate_launcher_identity(str(missing), live=False), missing)
            with self.assertRaisesRegex(ar.LaunchLineageError, "resolution_error"):
                ar._authenticate_launcher_identity(str(missing), live=True)
            with self.assertRaisesRegex(ar.LaunchLineageError, "measurement_root"):
                ar._authenticate_launcher_identity("relative/clone", live=False)
            link = root / "linked"; link.symlink_to(root, target_is_directory=True)
            with self.assertRaisesRegex(ar.LaunchLineageError, "measurement_root"):
                ar._authenticate_launcher_identity(str(link / "absent"), live=False)


class AcceptanceBaselineTests(unittest.TestCase):
    def test_real_376_row_prefix_replays_baseline_and_bad_cutoff_fails_closed(self):
        from joulewise import calibration_bracketing as brackets, calibration_ledger as ledger
        from joulewise.schemas import CalibrationBracketingPolicy
        from scripts import check_window_provenance as checker
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            acceptance_path = h.ROOT / "configs/calibration/calibration_acceptance_d079_v2_n24_25g83_r2.json"
            acceptance = brackets.load_calibration_acceptance_bound(acceptance_path)
            cutoff = acceptance["ledger_cutoff"]
            # The preserved ledger's governed 376-row prefix is read-only.
            import base64, zlib, hashlib
            archive = Path(__file__).parent / "fixtures/v5_qualification_harvest/acceptance-prefix-376.jsonl.zlib.b85"
            prefix = zlib.decompress(base64.b85decode(archive.read_bytes()))
            self.assertEqual(hashlib.sha256(prefix).hexdigest(), "3c9b6844e22958a6ba0eaee28cfab63642f3d0310f15b9bbc9e82363a2d772fb")
            ledger_path = root / "ledger.jsonl"
            ledger_path.write_bytes(prefix)
            pin = root / "pin.json"; put(pin, {"sequence": cutoff["sequence"], "head_digest": cutoff["head_digest"], "ledger_schema": ledger.LEDGER_SCHEMA})
            args = SimpleNamespace(calibration_ledger=ledger_path, head_pin=pin, acceptance=acceptance_path)
            boundary = root / "terminal-boundary.json"
            put(boundary, {"session_id": "baseline-probe", "session_state": "finalized",
                "pin_relation": "physical_ahead", "refusal_code": "calibration_ledger_head_mismatch",
                "terminal_head_pin_candidate": q.read(pin)})
            args.terminal_boundary_record = boundary
            snapshot, _candidate = checker._ratified_g2_boundary_snapshot(args, {"session_id": "baseline-probe"})
            self.assertEqual(snapshot.baseline_sequence, cutoff["sequence"])
            self.assertEqual(snapshot.baseline_digest, cutoff["head_digest"])
            policy = CalibrationBracketingPolicy(require_bracket=True, calibration_bracket_max_drift_s=0.05)
            evaluate = lambda view: brackets.evaluate_calibration_bracket([], window_start_s=1., window_end_s=2., bindings={}, policy=policy, ledger_snapshot=view)[1]
            self.assertNotIn("calibration_ledger_baseline_missing", evaluate(snapshot))
            missing = ledger.load_calibration_ledger_snapshot(ledger_path, pin, require_committed_pin=False, verify_custody=False, mode="read_replay")
            self.assertIn("calibration_ledger_baseline_missing", evaluate(missing))
            put(pin, {"sequence": 0, "head_digest": ledger.GENESIS_DIGEST, "ledger_schema": ledger.LEDGER_SCHEMA})
            self.assertIn("calibration_ledger_baseline_missing", checker._acceptance_replay_snapshot(args).refusal_reasons)
    def test_f52_replays_production_endpoint_descriptors_with_real_cutoff(self):
        import base64, hashlib, zlib
        from tests import test_check_window_provenance as fixtures
        from joulewise import whole_window as window, calibration_ledger as ledger
        from joulewise.calibration_bracketing import build_calibration_bracket_binding
        with tempfile.TemporaryDirectory() as temporary:
            fx = fixtures._install_s11_checker_fixture(Path(temporary).resolve())
            pin = fx["root"] / "calibration_ledger_head.json"
            snapshot = ledger.load_calibration_ledger_snapshot(fx["ledger_path"], pin, require_committed_pin=False, verify_custody=False)
            old = snapshot.bracket_session_by_id["synthetic-session"]
            observations = old.finalized_slots
            archive = Path(__file__).parent / "fixtures/v5_qualification_harvest/acceptance-prefix-376.jsonl.zlib.b85"
            fx["ledger_path"].write_bytes(zlib.decompress(base64.b85decode(archive.read_bytes())))
            acceptance = h.brackets.load_calibration_acceptance_bound()
            cutoff = acceptance["ledger_cutoff"]
            put(pin, {"sequence": cutoff["sequence"], "head_digest": cutoff["head_digest"], "ledger_schema": ledger.LEDGER_SCHEMA})
            slots = {slot: {"attempt_id": observation.attempt_id, "custody_locator": observation.custody_locator,
                "identity_epoch": dict(observation.identity_epoch), "t1_bindings": dict(observation.t1_bindings)}
                for slot, observation in observations.items()}
            ledger.append_bracket_session_receipt(fx["ledger_path"], session_id=old.session_id, window_id=old.window_id,
                plan_id=old.plan_id, plan_sha256=old.plan_sha256, evidence_root_id=old.evidence_root_id,
                runs_root=fx["runs_root"], slots=slots, head_pin_path=pin, require_committed_pin=False)
            for slot, observation in observations.items():
                ledger.finalize_bracket_session_slot(fx["ledger_path"], session_id=old.session_id, slot=slot, disposition="valid",
                    custody_locator=observation.custody_locator, artifact_sha256=dict(observation.artifact_sha256),
                    identity_epoch=dict(observation.identity_epoch), t1_bindings=dict(observation.t1_bindings),
                    capture_wall_time_s="99.0" if slot == "pre" else "111.0", exact_bound_lexeme_s="0.025")
            terminal = ledger.terminal_head_pin_for_session(fx["ledger_path"], session_id=old.session_id); put(pin, terminal)
            boundary = q.read(fx["terminal_boundary_record"]); boundary["terminal_head_pin_candidate"] = terminal
            put(fx["terminal_boundary_record"], boundary)
            snapshot = ledger.load_calibration_ledger_snapshot(fx["ledger_path"], pin, require_committed_pin=False, verify_custody=False)
            binding = build_calibration_bracket_binding(snapshot, session_id=old.session_id, window_id=old.window_id,
                plan_id=old.plan_id, plan_sha256=old.plan_sha256, evidence_root_id=old.evidence_root_id, runs_root=fx["runs_root"])
            put(fx["bracket_path"], binding)
            selected = snapshot.bracket_session_by_id[old.session_id]
            def descriptor(slot):
                observation = selected.finalized_slots[slot]
                return {"attempt_id": observation.attempt_id, "content_id": observation.content_id,
                    "ledger_receipt_digest": observation.receipt_digest, "bracket_slot": slot,
                    "bracket_session_id": observation.bracket_session_id, "bracket_window_id": observation.bracket_window_id,
                    "bracket_plan_id": observation.bracket_plan_id, "bracket_plan_sha256": observation.bracket_plan_sha256,
                    "bracket_evidence_root_id": observation.bracket_evidence_root_id, "bracket_runs_root": observation.bracket_runs_root,
                    "b_fiducial_s": 0.025}
            for meta in fx["runs_root"].glob("*/metadata.json"):
                value = q.read(meta); value["instrument_calibration"]["bindings"] = dict(selected.finalized_slots["pre"].t1_bindings)
                put(meta, value)
                events = [{"phase": "measured_run", "event_type": event, "timestamp_s": stamp, "message": "", "metadata": {}}
                          for event, stamp in (("sampling_started", 100.), ("sampling_stopped", 110.))]
                (meta.parent / "events.jsonl").write_text("".join(json.dumps(event) + "\n" for event in events))
            row = q.read(fx["verdict_path"])
            bracket = row["idle_admission_core"]["instrument_calibration_bracket"]
            bracket.update(pre=descriptor("pre"), post=descriptor("post"))
            basis = row["evaluation_basis"]
            for occurrence in basis["member_occurrences"]:
                occurrence["metadata_sha256"] = q.sha(fx["runs_root"] / occurrence["bundle_path"] / "metadata.json")
            basis["calibration_bracket_set"] = window._calibration_bracket_basis(bracket)
            basis["sha256"] = window.canonical_sha256({key: value for key, value in basis.items() if key != "sha256"})
            raw = (json.dumps(row, sort_keys=True) + "\n").encode()
            fx["verdict_path"].write_bytes(raw); (fx["runs_root"] / "campaign_log.jsonl").write_bytes(raw)
            seen = []; real = window.calibration_bracket_for_bundles
            def observe(*args, **kwargs):
                assessment, reasons = real(*args, **kwargs)
                seen.append((kwargs["ledger_snapshot"].baseline_sequence, reasons))
                return assessment, reasons
            argv = fixtures._normal_argv(fx)
            if "--acceptance" in argv:
                argv[argv.index("--acceptance") + 1] = str(h.brackets.DEFAULT_ACCEPTANCE_BOUND_PATH)
            with mock.patch.object(window, "calibration_bracket_for_bundles", side_effect=observe):
                _code, output = fixtures._run(argv)
            self.assertTrue(seen, "F5-2 must replay the endpoint descriptors: " + output)
            self.assertTrue(all(sequence == 376 for sequence, _reasons in seen), seen)
            self.assertTrue(all("calibration_ledger_baseline_missing" not in reasons for _sequence, reasons in seen), seen)



class NoMockDeskHeadTests(unittest.TestCase):
    def setUp(self):
        from scripts import v5_s1_desk_closeout as desk
        from joulewise import calibration_ledger as ledger
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve(); self.measurement = self.root / "measurement"
        # Exact production pack, config inventories and chain-source bytes.
        shutil.copytree(h.ROOT / "configs", self.measurement / "configs")
        for relative in (desk.RUNSHEET, "docs/phase_2/window_runbook.md"):
            target = self.measurement / relative; target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(h.ROOT / relative, target)
        self.pin = self.measurement / "configs/calibration/calibration_ledger_head.json"
        self.pin.write_bytes(ar.render_json({"sequence": 0, "head_digest": ledger.GENESIS_DIGEST, "ledger_schema": ledger.LEDGER_SCHEMA}))
        self.git("init", "-q"); self.git("add", "."); self.commit("fixture production config snapshot")
        self.head = self.git("rev-parse", "HEAD").strip()
        self.pack = self.measurement / "configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5"
        self.sources = {name: str(self.root / name) for name in ("custody", "claim_runs", "bound_runs")}
        for path in self.sources.values(): Path(path).mkdir()
        claim = Path(self.sources["claim_runs"])
        (claim / "campaign_log.jsonl").write_text('{"record_type":"idle_admission_whole_window_verdict"}\n')
        (Path(self.sources["custody"]) / "source.json").write_text('{}\n')
        science, _, _, _ = desk.writer.pack_roster(self.pack, "s1")
        expected = {"claim_runs": {r["run_id"] for r in science}, "bound_runs": set()}
        tree, _ = ar._plan_tree(self.pack)
        stages = desk.writer.dispatched_stages(self.pack, tree["stage_graph"], science[0]["stage_id"])
        for stage in stages:
            if stage["kind"] != "campaign_collection" or stage["stage_id"] == science[0]["stage_id"]:
                continue
            paths = [arg["value"] for command in stage["launch"]["commands"] for arg in command["argv_template"]["arguments"]
                     if arg["kind"] == "repo_path" and arg["value"].startswith("configs/campaigns/")]
            role = "bound_runs" if stage.get("input_ref", {}).get("input_id") == "neg8_bound_corpus" else "claim_runs"
            for config in h.run_campaign.discover_configs(self.measurement / paths[0]):
                expected[role].add(q.read(config)["run_id"])
        for role, ids in expected.items():
            for identity in ids: (Path(self.sources[role]) / identity).mkdir()
        self.plan = SimpleNamespace(measurement_root=str(self.measurement), pack_night={"pack_root": str(self.pack),
            "pack_sha256": ar.committed_pack_tree_sha256(self.pack)})
        self.record = {"head": self.head, "desk_sources": self.sources}

    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.measurement), *args], text=True, stderr=subprocess.PIPE)

    def commit(self, message):
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-qm", message)

    def test_pin_only_h_pin_passes_real_phase_g_without_moving_live_clone(self):
        from scripts import v5_s1_desk_closeout as desk
        from joulewise import calibration_ledger as ledger
        before_pack = q.tree_hash(self.pack)
        self.pin.write_bytes(ar.render_json({"sequence": 3, "head_digest": "a" * 64, "ledger_schema": ledger.LEDGER_SCHEMA}))
        self.git("add", "configs/calibration/calibration_ledger_head.json"); self.commit("fixture H_pin")
        head_pin = self.git("rev-parse", "HEAD").strip()
        result = desk.phase_g(self.plan, self.record)
        self.assertEqual(result["head"], head_pin)
        self.assertEqual(result["head_extension"]["changed_paths"], ["configs/calibration/calibration_ledger_head.json"])
        self.assertEqual(result["head_extension"]["terminal_head_pin"], q.read(self.pin))
        self.assertEqual(self.git("rev-parse", "HEAD").strip(), head_pin)
        self.assertEqual(q.tree_hash(self.pack), before_pack)
        self.assertEqual(self.git("status", "--porcelain"), "")

    def test_pack_refresh_or_executable_change_is_not_h_pin(self):
        from scripts import v5_s1_desk_closeout as desk
        other = self.measurement / "extra-script.py"; other.write_text('pass\n')
        self.git("add", "."); self.commit("fixture forbidden extension")
        with self.assertRaisesRegex(ValueError, "not pin-only"):
            desk.phase_g(self.plan, self.record)
        other.write_text('changed\n')
        with self.assertRaisesRegex(ValueError, "modified measurement checkout"):
            desk.phase_g(self.plan, self.record)
    def test_deleted_pin_is_refused_as_a_structural_error(self):
        from scripts import v5_s1_desk_closeout as desk
        self.pin.unlink(); self.git("add", "-u"); self.commit("fixture missing pin")
        with self.assertRaisesRegex(ValueError, "pin is unavailable"):
            desk.phase_g(self.plan, self.record)



class OffWitnessTests(unittest.TestCase):
    def test_permitted_setter_witness_and_unavailable_or_state_changing_results(self):
        from scripts import produce_t0_rehearsal_bundle as producer
        from joulewise import t0_rehearsal as t0
        for code, stdout, expected in ((0, "  NETWORK Time is already OFF\n", True),
                (0, "Network Time is already off.\n", True),
                (0, "setUsingNetworkTime: Off\n", False), (1, "Network Time is already off", False),
                (0, "Network Time: Off", False)):
            with mock.patch.object(t0, "observed_run", return_value=subprocess.CompletedProcess([], code, stdout, "")) as run:
                if expected:
                    observation = producer.observe_network_time_off()
                    self.assertEqual(observation["argv"], list(off.OFF_ARGV))
                    self.assertEqual(" ".join(observation["stdout"].split()).casefold().rstrip(".").rstrip(), "network time is already off")
                else:
                    with self.assertRaisesRegex(ValueError, "OFF observation"):
                        producer.observe_network_time_off()
            self.assertEqual(run.call_args.args[0], list(off.OFF_ARGV))
