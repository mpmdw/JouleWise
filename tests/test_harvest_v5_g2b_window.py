"""Discriminating fixture checks for s1 custody, order, blindness and L10-A."""
import copy
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock
from contextlib import redirect_stdout

from joulewise import arm_readiness as readiness, battery_float, v5_qualification as q
from scripts import harvest_v5_g2b_window as h
from tests.test_analysis_finalizer import install_synthetic_finalization_fixture, _make_sliced_one_block_verdict
from tests.test_battery_float import raw as battery_raw, UPDATE

SCRATCH = Path(tempfile.gettempdir())


def put(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(readiness.render_json(value))


class G2bStructureTests(unittest.TestCase):
    def setUp(self):
        SCRATCH.mkdir(exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(dir=SCRATCH)
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name).resolve()
        self.custody = self.base / "custody"
        self.runs = self.custody / "runs"
        self.pack = self.base / "pack"
        self.runs.mkdir(parents=True)
        self.pack.mkdir()
        self.ids = ["science-A1", "science-B1", "science-B2", "science-A2"]
        self.order_path = self.pack / "first/order.json"
        put(self.order_path, {"manifest_id": "order-1", "executed_order": [
            {"run_id": rid, "block_index": 1, "arm": arm} for rid, arm in zip(self.ids, "ABBA")]})
        self.prospective = {"stage_manifests": [{"index": 1, "subcampaign_id": "first-science",
            "manifest_id": "order-1", "manifest_path": "first/order.json", "manifest_sha256": q.sha(self.order_path)}]}
        put(self.pack / "analysis_manifest_v3.json", self.prospective)
        self.campaign_path = self.runs / "campaign_manifests/first.json"
        put(self.campaign_path, {"config_dir": "first-science", "members": [
            {"run_id": rid, "bundle_ids": [rid]} for rid in self.ids]})
        for rid in self.ids:
            put(self.runs / rid / "metadata.json", {"run_id": rid,
                "uncertainty_evidence": {"clock_anchor": {"status": "bounded"}}})
            put(self.runs / rid / "summary_metrics.json", {"status": "succeeded"})
        self.night = self.base / "night"
        self.night.mkdir()
        put(self.night / "chain.exited", {"exit_code": 0})
        self.authorization = {"path": "/fixture/authorization.json", "sha256": "a" * 64}
        self.stop = {"record_type": "campaign_stop", "schema_version": h.run_campaign.CAMPAIGN_STOP_SCHEMA,
            "stop_reason": "max_blocks_reached", "exit_code": 3, "completed_blocks": 1,
            "last_block_index": 1, "last_block_members": self.ids,
            "block_limit": {"max_blocks": 1, "source": "authorization", "authorization": self.authorization,
                            "purpose": "G2B_SHAKEDOWN"}}
        self.log = self.runs / "campaign_log.jsonl"
        self.log.write_bytes(readiness.render_json(self.stop).replace(b"\n", b" ") + b"\n")

    def test_frozen_four_in_order(self):
        ids, sha, causes = h.science_roster(self.pack, self.runs)
        self.assertEqual(ids, self.ids)
        self.assertEqual(sha, q.sha(self.order_path))
        self.assertEqual(causes, [])

    def test_swapped_or_missing_manifest_member_kills_acceptance(self):
        original = q.read(self.campaign_path)
        for mutate in (lambda rows: rows.reverse(), lambda rows: rows.pop()):
            data = copy.deepcopy(original)
            mutate(data["members"])
            put(self.campaign_path, data)
            self.assertIn("science_roster_or_order_mismatch", h.science_roster(self.pack, self.runs)[2])

    def test_fifth_and_partial_unlisted_science_bundle_kill_acceptance(self):
        for name in ("fifth", "partial"):
            (self.runs / name).mkdir()
            self.assertIn("fifth_partial_or_missing_science_bundle", h.science_roster(self.pack, self.runs)[2])
            (self.runs / name).rmdir()
        shutil.rmtree(self.runs / self.ids[0])
        self.assertIn("fifth_partial_or_missing_science_bundle", h.science_roster(self.pack, self.runs)[2])

    def test_wrong_stop_and_outer_rc_are_distinct(self):
        self.assertEqual(h.stop_codes(self.runs, self.night, self.ids, self.authorization), [])
        for code in (0, 130, 2):
            row = {**self.stop, "exit_code": code}
            self.log.write_text(json.dumps(row) + "\n")
            self.assertIn("governed_one_block_stop_invalid", h.stop_codes(self.runs, self.night, self.ids, self.authorization))
        self.log.write_text(json.dumps(self.stop) + "\n")
        put(self.night / "chain.exited", {"exit_code": 3})
        self.assertEqual(h.stop_codes(self.runs, self.night, self.ids, self.authorization), ["outer_chain_not_successful"])

    def install_verdict(self):
        row = {"record_type": "idle_admission_whole_window_verdict", "bundle_ids": self.ids, "status": "passed"}
        raw = (json.dumps(row, sort_keys=True) + "\n").encode()
        (self.runs / "whole-window-verdict.json").write_bytes(raw)
        self.log.write_bytes(self.log.read_bytes() + raw)
        put(self.runs / "bracket-binding.json", {"fixture": True})
        self.events = {"schema": h.ORDER_SCHEMA, "runs_root": str(self.runs), "events": [
            {"producer": "build_bracket_binding", "started_ns": 1, "completed_ns": 2, "exit_code": 0,
             "output_sha256": q.sha(self.runs / "bracket-binding.json")},
            {"producer": "whole_window_verdict", "started_ns": 3, "completed_ns": 4, "exit_code": 0,
             "output_sha256": q.sha(self.runs / "whole-window-verdict.json"),
             "binding_input_sha256": q.sha(self.runs / "bracket-binding.json")} ]}
        return raw

    def test_preexisting_duplicate_verdict_refused_without_append(self):
        raw = self.install_verdict()
        self.log.write_bytes(self.log.read_bytes() + raw)
        before = self.log.read_bytes()
        with self.assertRaisesRegex(q.HarvestRefusal, "verdict_count"):
            h.authoritative_row(self.runs)
        self.assertEqual(before, self.log.read_bytes())

    def test_exact_row_copy_and_binding_order_hash_proof(self):
        self.install_verdict()
        h.authenticate_order(self.events, self.runs)
        bad = copy.deepcopy(self.events)
        bad["events"].reverse()
        with self.assertRaisesRegex(q.HarvestRefusal, "producer_order"):
            h.authenticate_order(bad, self.runs)
        bad = copy.deepcopy(self.events)
        bad["events"][1]["started_ns"] = 1
        with self.assertRaisesRegex(q.HarvestRefusal, "producer_order"):
            h.authenticate_order(bad, self.runs)
        put(self.runs / "bracket-binding.json", {"changed": True})
        with self.assertRaisesRegex(q.HarvestRefusal, "producer_order"):
            h.authenticate_order(self.events, self.runs)
        (self.runs / "whole-window-verdict.json").write_text("{}\n")
        with self.assertRaisesRegex(q.HarvestRefusal, "copy_not_exact"):
            h.authoritative_row(self.runs)

    def committed_gamma(self):
        """Exact git-show bytes, never fields added to calibration_plan.json."""
        source = Path(__file__).parent / "fixtures/v5_qualification_harvest/committed_gamma"
        manifest = q.read(source / "SOURCE.json")
        for name, digest in manifest["files"].items():
            self.assertEqual(q.sha(source / name), digest)
            for target in (self.pack / name, self.custody / "prospective" / name):
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source / name, target)
        frozen, tree, identity = h.frozen_identity(self.custody, pack=self.pack)
        self.assertTrue({"window_id", "evidence_root_id", "active_acceptance", "calibration_ledger"}.isdisjoint(frozen))
        session = SimpleNamespace(session_id="recorded-session", state="finalized", runs_root=str(self.runs),
            plan_id=frozen["plan_id"], plan_sha256=q.sha(self.pack / "calibration_plan.json"),
            window_id=identity["window_id"], evidence_root_id=identity["evidence_root_id"],
            finalized_slots={"pre": SimpleNamespace(disposition="valid"), "post": SimpleNamespace(disposition="valid")})
        return SimpleNamespace(refusal_reasons=(), bracket_session_by_id={session.session_id: session}), session

    def test_acceptance_cutoff_not_seed_and_failed_post_endpoint(self):
        snapshot, live = self.committed_gamma()
        put(self.runs / "bracket-binding.json", {"session_id": live.session_id})
        acceptance = h.ROOT / "configs/calibration/calibration_acceptance_d079_v2_n24_25g83_r2.json"
        plan = SimpleNamespace(measurement_root=str(h.ROOT), plan_id="occurrence-id",
                               pack_night={"pack_root": str(self.pack)})
        # Mock seam: ledger replay supplies finalized synthetic physical slots;
        # plan-tree and acceptance bindings use the real committed bytes.
        with mock.patch.object(h, "load_calibration_ledger_snapshot", return_value=snapshot) as load, \
             mock.patch.object(h.brackets, "validate_calibration_bracket_binding", return_value=(object(), object())) as validate:
            self.assertEqual(h.bracket_assessment(self.custody, plan, None, acceptance)[3], [])
            self.assertNotIn("baseline_sequence", load.call_args_list[0].kwargs)
            self.assertEqual(load.call_args_list[1].kwargs["baseline_sequence"], 376)
            self.assertTrue(all(call.kwargs["verify_custody"] for call in load.call_args_list))
            self.assertEqual(validate.call_args.kwargs["window_id"], live.window_id)
            live.finalized_slots["post"].disposition = "failed"
            self.assertIn("acceptance_bracket_endpoint_not_passed", h.bracket_assessment(self.custody, plan, None, acceptance)[3])
            live.window_id = "wrong"
            self.assertEqual(h.bracket_assessment(self.custody, plan, None, acceptance)[3], ["bracket_session_not_complete"])
        tree_path = self.custody / "prospective/plan_tree.json"
        tree = q.read(tree_path); tree["window_identity"]["window_id"] = "wrong"; put(tree_path, tree)
        with self.assertRaisesRegex(q.HarvestRefusal, "frozen_pack_copy_mismatch"):
            h.bracket_assessment(self.custody, plan, None, acceptance)

    def test_physical_ledger_is_authenticated_without_invented_plan_seed(self):
        from joulewise import calibration_ledger
        self.committed_gamma()
        ledger = self.custody / "calibration/calibration_observation_ledger.jsonl"
        ledger.parent.mkdir(parents=True)
        ledger.write_bytes(b"")
        pin = ledger.parent / "calibration_ledger_head.json"
        put(pin, {"ledger_schema": calibration_ledger.LEDGER_SCHEMA, "sequence": 0,
                  "head_digest": calibration_ledger.GENESIS_DIGEST})
        # No authenticator is replaced: genesis supplies no qualifying endpoint.
        snapshot = h.physical_snapshot(self.custody, self.base)
        self.assertEqual(snapshot.refusal_reasons, ())
        self.assertEqual(dict(snapshot.bracket_session_by_id), {})
        ledger.write_text("malformed physical ledger\n")
        with self.assertRaisesRegex(q.HarvestRefusal, "physical_ledger_custody_invalid"):
            h.physical_snapshot(self.custody, self.base)

    def test_five_anchor_majority_preserves_threshold_and_strict_majority(self):
        member = lambda status: {"clock_anchor_status": status}
        self.assertFalse(h.clock_majority([member("unbounded")] * 4)["triggered"])
        self.assertTrue(h.clock_majority([member("unbounded")] * 3 + [member("bounded")] * 2)["triggered"])
        self.assertFalse(h.clock_majority([member("unbounded")] * 3 + [member("bounded")] * 3)["triggered"])
        self.assertEqual(h.clock_majority([member("unbounded")] * 4 + [member("not recorded")])["recorded"], 4)
        self.assertFalse(q.disposition("s1", "RECOVER", ["instrument_physics"])["s2_eligible"])
        self.assertTrue(q.disposition("s2", "RECOVER", ["tooling"])["end_state"])

    def test_provenance_requires_nr14_and_exact_allowed_a4_skip(self):
        def run(stdout):
            result = subprocess.CompletedProcess([], 0, stdout, "")
            return h.desk_check(self.custody, self.pack, self.base / "terminal.json",
                                self.base / f"transcripts-{len(list(self.base.glob('transcripts-*')))}",
                                runner=lambda *a, **k: result)
        self.assertTrue(run("PASS NR14-LAYOUT okay\nSKIP S11-A4 present_stages=0 assertion_not_exercised\n"))
        self.assertFalse(run("SKIP S11-A4 present_stages=0 assertion_not_exercised\n"))
        self.assertFalse(run("PASS NR14-LAYOUT okay\nSKIP S11-A4 other\n"))
        self.assertFalse(run("PASS NR14-LAYOUT okay\nPASS S11-A4 okay\nFAIL S11-A5 secret metric\n"))

    def test_battery_consumer_visits_failed_superseded_and_bracket_attempts(self):
        bound = self.custody / "bound-runs"
        bound.mkdir()
        put(bound / "failed-old/metadata.json", {})
        put(self.runs / "superseded-old/metadata.json", {})
        put(self.custody / "calibration/rejected-pre/instrument_evidence.json", {})
        visited = []
        def bundle(path):
            visited.append(path.name)
            return SimpleNamespace(status="battery_float_confounded" if path.name == "failed-old" else "pass")
        with mock.patch.object(h.battery_float, "authenticate_bundle", side_effect=bundle), \
             mock.patch.object(h.battery_float, "authenticate_capture", return_value=SimpleNamespace(status="pass")) as capture:
            passed, paths = h.battery_attempts(self.custody, bound)
        self.assertFalse(passed)
        self.assertIn("superseded-old", visited)
        self.assertIn("failed-old", visited)
        self.assertEqual(len(paths), 7)
        capture.assert_called_once_with(self.custody / "calibration/rejected-pre")

    def test_refused_g2b_copy_reharvest_preserves_record_and_rejects_changed_bytes(self):
        sources = {"g2b": self.custody}
        first = self.base / "archive-1"
        q.archive_sources(sources, first)
        q.write(first / "harvest.json", {"schema": h.SCHEMA, "verdict": "REFUSED"})
        original = (first / "harvest.json").read_bytes()
        q.archive_sources(sources, self.base / "archive-2", previous=first)
        self.assertEqual((first / "harvest.json").read_bytes(), original)
        (self.runs / "mutated").write_text("changed")
        with self.assertRaisesRegex(q.HarvestRefusal, "source_bytes_changed"):
            q.archive_sources(sources, self.base / "archive-3", previous=first)

    def test_prepare_desk_calls_binding_before_verdict_and_never_reappends(self):
        frozen = self.custody / "prospective/calibration_plan.json"
        snapshot, session = self.committed_gamma()
        ledger = self.custody / "calibration/calibration_observation_ledger.jsonl"
        pin = self.custody / "calibration/calibration_ledger_head.json"
        ledger.parent.mkdir(parents=True)
        ledger.write_text("fixture-ledger\n")
        put(pin, {})
        measurement = self.base / "measurement"
        (measurement / "runs").mkdir(parents=True)
        (measurement / "configs/calibration").mkdir(parents=True)
        shutil.copy2(ledger, measurement / "runs/calibration_observation_ledger.jsonl")
        shutil.copy2(pin, measurement / "configs/calibration/calibration_ledger_head.json")
        calls = []
        def runner(argv, **kwargs):
            calls.append(argv)
            if any(str(item).endswith("build_bracket_binding.py") for item in argv):
                put(self.runs / "bracket-binding.json", {"fixture": True})
            else:
                self.assertTrue((self.runs / "bracket-binding.json").exists())
                raw = (json.dumps({"record_type": "idle_admission_whole_window_verdict",
                                   "status": "passed", "bundle_ids": self.ids}) + "\n").encode()
                self.log.write_bytes(self.log.read_bytes() + raw)
                (self.runs / "whole-window-verdict.json").write_bytes(raw)
            return subprocess.CompletedProcess(argv, 0, "UNFILTERED-TAIL secret metric", "")
        with mock.patch.object(h, "validate_whole_window_verdict_row", return_value=SimpleNamespace(authentic=True)), \
             mock.patch.object(h, "load_calibration_ledger_snapshot", return_value=snapshot):
            events = h.prepare_desk(self.custody, frozen, self.base / "policy.json", measurement,
                                    self.base / "transcripts", runner=runner)
        self.assertEqual([event["producer"] for event in events["events"]], ["build_bracket_binding", "whole_window_verdict"])
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[0][calls[0].index("--session-id") + 1], session.session_id)
        self.assertEqual(calls[0][calls[0].index("--window-id") + 1], session.window_id)
        self.assertEqual(calls[0][calls[0].index("--evidence-root-id") + 1], session.evidence_root_id)
        self.assertIn("--whole-window-verdict", calls[1])
        with self.assertRaisesRegex(q.HarvestRefusal, "authentication_only"):
            h.prepare_desk(self.custody, frozen, self.base / "policy.json", measurement,
                           self.base / "repeat", runner=runner)
        self.assertEqual(len(calls), 2)

    def test_null_archives_missing_go_and_live_pending_group_overrides_null(self):
        night_root = self.base / "night-custody"
        (night_root / "night").mkdir(parents=True)
        chain = self.base / "chain.zsh"
        chain.write_text("exit 0\n")
        sidecar = self.base / "chain.sha256"
        sidecar.write_text(q.sha(chain) + "\n")
        plan_path = night_root / "night_plan.json"
        put(plan_path, {"fixture": True})
        acceptance = self.base / "acceptance.json"
        policy = self.base / "policy.json"
        put(acceptance, {})
        put(policy, {})
        bound = self.base / "bound"
        bound.mkdir()
        plan = SimpleNamespace(plan_id="s1-fixture", custody_root=str(night_root), measurement_head="a" * 40,
            chain_path=str(chain), chain_sha256_path=str(sidecar),
            pack_night={"pack_id": "d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5", "pack_root": str(self.pack)})
        input_path = self.base / "inputs.json"
        put(input_path, {"schema": h.INPUT_SCHEMA, "occurrence": "s1", "plan": q.reference(plan_path),
            "custody_root": str(self.custody), "policy": q.reference(policy), "acceptance": q.reference(acceptance),
            "bound_runs_root": str(bound)})
        args = SimpleNamespace(inputs=input_path, inputs_sha256=q.sha(input_path), archive_root=self.base / "null",
            scratch_root=self.base, prepare_desk=False, previous_harvest=None)
        with mock.patch.object(q, "load_plan", return_value=plan):
            record = h.harvest(args)
        self.assertEqual(record["verdict"], "NULL")
        self.assertTrue((args.archive_root / "SHA256SUMS").is_file())
        put(night_root / "night/launch.pending", {"schema": "joulewise.launch_pending.v1", "pid": 54321,
            "pgid": 54321, "start_time": "fixture", "plan_id": "s1-fixture", "attempt_id": "one", "epoch_s": 1.0})
        args.archive_root = self.base / "live-pending"
        with mock.patch.object(q, "load_plan", return_value=plan), mock.patch.object(q.os, "killpg", return_value=None):
            # Bind the injected syscall explicitly; group_clear's default was
            # captured on import and must never contact a real process group.
            record = h.harvest(args, clear=lambda night, **kw: q.group_clear(night, killpg=q.os.killpg, **kw))
        self.assertEqual(record["verdict"], "REFUSED")
        self.assertEqual(record["cause_codes"], ["launcher_group_alive"])


class BatteryBoundaryTests(unittest.TestCase):
    def test_non_pass_and_raw_digest_mismatch_use_real_battery_reader(self):
        SCRATCH.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
            root = Path(tmp).resolve()
            mapping = {"schema": "joulewise.v5_qualification_battery_boundaries.v1", "plan_id": "plan", "observations": {}}
            for role in ("arm", "publication", "t0"):
                raw_path = root / f"{role}.ioreg"
                raw_path.write_bytes(battery_raw())
                stored, _ = battery_float.observe(phase=q.BATTERY_BOUNDARY_PHASES[role], wall_time_s=UPDATE + 1, monotonic_ns=lambda: 1,
                    plan_id="plan", runner=lambda argv: subprocess.CompletedProcess(argv, 0, raw_path.read_bytes(), b""))
                path = root / f"{role}.json"
                put(path, stored)
                mapping["observations"][role] = {"record": q.reference(path), "raw": q.reference(raw_path)}
            manifest = root / "boundaries.json"
            put(manifest, mapping)
            self.assertTrue(q.battery_boundaries(manifest, q.sha(manifest), "plan"))
            raw_path.write_bytes(battery_raw("charging-synthetic-from-real.ioreg"))
            stored, _ = battery_float.observe(phase="t0", wall_time_s=UPDATE + 1, monotonic_ns=lambda: 1,
                plan_id="plan", runner=lambda argv: subprocess.CompletedProcess(argv, 0, raw_path.read_bytes(), b""))
            put(path, stored)
            mapping["observations"]["t0"] = {"record": q.reference(path), "raw": q.reference(raw_path)}
            put(manifest, mapping)
            self.assertFalse(q.battery_boundaries(manifest, q.sha(manifest), "plan"))
            raw_path.write_bytes(battery_raw())
            with self.assertRaisesRegex(q.HarvestRefusal, "digest_mismatch"):
                q.battery_boundaries(manifest, q.sha(manifest), "plan")


class FoldedL10Tests(unittest.TestCase):
    def setUp(self):
        SCRATCH.mkdir(exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(dir=SCRATCH)
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name).resolve()
        self.custody = self.base / "source"
        self.custody.mkdir()
        # Real finalizer/provenance-consumer fixture, not a production corpus.
        self.fixture = install_synthetic_finalization_fixture(self.custody)
        _make_sliced_one_block_verdict(self.fixture)
        self.fixture["floor_path"].unlink()
        shutil.copytree(self.fixture["prospective_path"].parent, self.custody / "prospective")
        shutil.copy2(self.fixture["plan_tree_path"], self.custody / "prospective/plan_tree.json")
        (self.custody / "calibration").mkdir()
        shutil.copy2(self.fixture["ledger_path"], self.custody / "calibration/calibration_observation_ledger.jsonl")
        shutil.copy2(self.fixture["bracket_path"], self.custody / "runs/bracket-binding.json")
        shutil.copy2(self.fixture["verdict_path"], self.custody / "runs/whole-window-verdict.json")
        self.ids = q.read(self.fixture["verdict_path"])["bundle_ids"]
        self.dest = self.base / "harvest"
        (self.dest / "withheld").mkdir(parents=True, mode=0o700)

    def invoke(self, runner=subprocess.run, reducer=None):
        reducer = reducer or (lambda path: q.read(path / "summary_metrics.json"))
        return h.l10_a(self.custody, self.dest, self.ids, "a" * 40, runner=runner,
                       validator=lambda path, strict: [], reducer=reducer)

    def expected_runner(self, *args, **kwargs):
        return subprocess.CompletedProcess(args[0], 0,
            f"PASS FINALIZE-REFUSAL observed={{{h.FINALIZER_REASON}}} expected={{{h.FINALIZER_REASON}}}\nSUMMARY pass=1 skip=0 fail=0\n", "")

    def test_old_output_dir_is_noncanonical_and_recorded_as_fail(self):
        def old_command(argv, **kwargs):
            old = list(argv)
            staging = Path(old[old.index("--custody-root") + 1])
            output = staging / "analysis-output"
            output.mkdir()
            old[old.index("--output-dir") + 1] = str(output)
            return subprocess.run(old, **kwargs)
        before = q.tree_hash(self.custody)
        _members, causes = self.invoke(runner=old_command)
        self.assertIn("l10_finalizer_not_exact_singleton", causes)
        record = q.read(self.dest / "l10-a/record.json")
        self.assertEqual(record["observed_reason_codes"], ["analysis_finalization_noncanonical"])
        self.assertEqual(record["status"], "FAIL")
        self.assertNotIn("needs_ruling", record)
        self.assertEqual(record["proof_scope"], "L10_A_G2B_CONTRACT_PREFIX")
        self.assertEqual(q.tree_hash(self.custody), before)
        self.assertEqual(record["g2b_tree_before"], record["g2b_tree_after"])

    def test_actual_finalizer_staging_root_reaches_exact_member_cover_without_source_writes(self):
        before = q.tree_hash(self.custody)
        def real_command(argv, **kwargs):
            staging = Path(argv[argv.index("--custody-root") + 1])
            self.assertEqual(Path(argv[argv.index("--output-dir") + 1]), staging)
            self.assertFalse((staging / "analysis-output").exists())
            return subprocess.run(argv, **kwargs)
        # The finalizer fixture has no clock anchors. Isolate that independent
        # member gate while executing the real checker and finalizer unchanged.
        with mock.patch.object(h, "anchor_status", return_value="bounded"):
            _members, causes = self.invoke(runner=real_command)
        self.assertEqual(causes, [])
        record = q.read(self.dest / "l10-a/record.json")
        self.assertEqual(record["status"], "PASS")
        self.assertEqual(record["observed_reason_codes"], [h.FINALIZER_REASON])
        self.assertNotIn("needs_ruling", record)
        self.assertTrue(record["floors_empty_before_after"])
        self.assertEqual(record["g2b_tree_before"], record["g2b_tree_after"])
        self.assertEqual(record["staged_tree_sha256"], record["g2b_tree_before"])
        self.assertEqual(q.tree_hash(self.custody), before)

    def test_wrong_finalizer_singleton_and_success_do_not_pass(self):
        for stdout in ("", "PASS FINALIZE-REFUSAL observed={analysis_finalization_attachment_missing}\n",
                       f"PASS FINALIZE-REFUSAL observed={{{h.FINALIZER_REASON},extra}}\n",
                       self.expected_runner([]).stdout + "gross_energy_j=314159\n"):
            self.dest = self.base / f"harvest-{len(list(self.base.glob('harvest-*')))}"
            (self.dest / "withheld").mkdir(parents=True)
            result = subprocess.CompletedProcess([], 0, stdout, "")
            _members, causes = self.invoke(runner=lambda *a, **k: result)
            self.assertIn("l10_finalizer_not_exact_singleton", causes)
            record = q.read(self.dest / "l10-a/record.json")
            self.assertEqual(record["status"], "FAIL")
            self.assertNotIn(b"314159", (self.dest / "l10-a/record.json").read_bytes())

    def test_floor_staged_before_or_during_finalizer_is_refused(self):
        (self.custody / "floors/forbidden.json").write_text("{}")
        with self.assertRaisesRegex(q.HarvestRefusal, "floors_not_empty"):
            self.invoke()
        (self.custody / "floors/forbidden.json").unlink()
        self.dest = self.base / "next-harvest"
        (self.dest / "withheld").mkdir(parents=True)
        def floor_in_scratch(argv, **kwargs):
            staged = Path(argv[argv.index("--custody-root") + 1])
            (staged / "floors/forbidden.json").write_text("{}")
            return self.expected_runner(argv, **kwargs)
        with self.assertRaisesRegex(q.HarvestRefusal, "floors_not_empty"):
            self.invoke(runner=floor_in_scratch)

    def test_source_tree_mutation_during_finalizer_is_refused(self):
        def mutate(argv, **kwargs):
            (self.custody / "runs/tampered").write_text("changed")
            return self.expected_runner(argv, **kwargs)
        with self.assertRaisesRegex(q.HarvestRefusal, "source_tree_mutated"):
            self.invoke(runner=mutate)

    def test_nested_metric_and_unfiltered_log_tail_are_withheld(self):
        def reduce(path):
            print("UNFILTERED TAIL energy and per-member duration")
            return {"nested": {"gross_energy_j": 314159, "phase": {"power_w": 271828, "duration_s": 161803}}}
        out = io.StringIO()
        with redirect_stdout(out):
            self.invoke(runner=self.expected_runner, reducer=reduce)
        public = (self.dest / "l10-a/record.json").read_bytes()
        for secret in (b"314159", b"271828", b"161803", b"UNFILTERED"):
            self.assertNotIn(secret, public)
        self.assertEqual(out.getvalue(), "")
        self.assertIn(b"314159", (self.dest / "withheld/s1-reductions.json").read_bytes())
        self.assertIn("UNFILTERED", (self.dest / "withheld/l10-a/transcripts" / f"{self.ids[0]}-reduce.txt").read_text())


if __name__ == "__main__":
    unittest.main()


class RecoverNoScienceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.night = self.root / 'night'; self.night.mkdir()
        self.pack = self.root / 'pack'; self.pack.mkdir()
        self.runs = self.root / 'runs'; self.runs.mkdir()
        put(self.night / 'chain.started', {'monotonic_ns': 100})
        put(self.pack / 'plan_tree.json', {'science': [{'run_id': f'science-{i:02}'} for i in range(80)]})
        self.failure = self.root / 'tooling-failure.json'
        self.value = {'schema': 'joulewise.v5_pre_science_tooling_failure.v1', 'plan_id': 's1-attempt',
            'cause_code': 'night_chain_launch_failed', 'cause_class': 'tooling', 'monotonic_ns': 101, 'seam': 'launch'}
        put(self.failure, self.value)
        self.inputs = {'auxiliary_bundle_ids': ['start-reference'], 'pre_science_tooling_failure': q.reference(self.failure)}
        self.plan = SimpleNamespace(plan_id='s1-attempt')

    def classify(self):
        return h.recover_no_science(self.inputs, self.plan, self.night, self.pack, self.runs)

    def test_registered_post_start_tooling_failure_is_no_science_without_s2_spend(self):
        result = self.classify()
        self.assertEqual(result['verdict'], 'RECOVER')
        self.assertEqual(result['recovery_classification'], 'recover_no_science')
        self.assertFalse(result['consumes_s2'])
        self.assertFalse(result['science_bytes_present'])
        # Auxiliary samplers are allowed; ruling 76 binds the first SCIENCE sampler.
        put(self.runs / 'start-reference/metadata.json', {'fixture': 'auxiliary'})
        self.assertEqual(self.classify()['recovery_classification'], 'recover_no_science')

    def test_even_partial_science_directory_precludes_no_science(self):
        (self.runs / 'science-00').mkdir()
        self.assertIsNone(self.classify())

    def test_failure_before_or_at_chain_start_is_not_the_ruled_recover(self):
        for stamp in (99, 100):
            put(self.failure, dict(self.value, monotonic_ns=stamp))
            self.inputs['pre_science_tooling_failure'] = q.reference(self.failure)
            with self.subTest(stamp=stamp), self.assertRaisesRegex(q.HarvestRefusal, 'not_after_chain_start'):
                self.classify()

    def test_missing_named_cause_and_physical_fault_do_not_grant_rearm(self):
        inputs = dict(self.inputs); inputs.pop('pre_science_tooling_failure')
        self.assertIsNone(h.recover_no_science(inputs, self.plan, self.night, self.pack, self.runs))
        put(self.failure, dict(self.value, cause_class='instrument_physics'))
        self.inputs['pre_science_tooling_failure'] = q.reference(self.failure)
        with self.assertRaisesRegex(q.HarvestRefusal, 'failure_invalid'):
            self.classify()

    def test_harvest_no_science_needs_no_post_bracket_and_preserves_custody(self):
        night_custody = self.root / 'night-custody'; night_custody.mkdir()
        self.night.rename(night_custody / 'night')
        self.night = night_custody / 'night'
        g2b = self.root / 'g2b'; g2b.mkdir()
        self.runs.rename(g2b / 'runs'); self.runs = g2b / 'runs'
        bound = self.root / 'bound'; bound.mkdir()
        plan_path = night_custody / 'night_plan.json'; put(plan_path, {'fixture': 'plan'})
        policy = self.root / 'policy.json'; put(policy, {'fixture': 'policy'})
        acceptance = self.root / 'acceptance.json'; put(acceptance, {'fixture': 'acceptance'})
        chain = self.root / 'chain.zsh'; chain.write_text('exit 1\n')
        sidecar = self.root / 'chain.sha256'; sidecar.write_text(q.sha(chain))
        plan = SimpleNamespace(plan_id='s1-attempt', custody_root=str(night_custody),
            chain_path=str(chain), chain_sha256_path=str(sidecar), measurement_head='a' * 40,
            pack_night={'pack_root': str(self.pack), 'pack_id': 'd117_contrast_qwen3-1p7b_vs_qwen3-8b_v5'})
        inputs = dict(self.inputs, schema=h.INPUT_SCHEMA, occurrence='s1', plan=q.reference(plan_path),
            custody_root=str(g2b), policy=q.reference(policy), acceptance=q.reference(acceptance), bound_runs_root=str(bound))
        input_path = self.root / 'inputs.json'; put(input_path, inputs)
        args = SimpleNamespace(inputs=input_path, inputs_sha256=q.sha(input_path),
            archive_root=self.root / 'archive', prepare_desk=False, previous_harvest=None, scratch_root=self.root)
        before = q.tree_hash(night_custody)
        with mock.patch.object(q, 'load_plan', return_value=plan):
            result = h.harvest(args, clear=lambda *a, **k: True)
        self.assertEqual(result['verdict'], 'RECOVER')
        self.assertEqual(result['recovery_classification'], 'recover_no_science')
        self.assertFalse(result['end_state'])
        self.assertFalse(result['consumes_s2'])
        self.assertEqual(before, q.tree_hash(night_custody))
        self.assertFalse((args.archive_root / 'l10-a').exists())

    def test_observation_producer_fault_is_never_g2b_recover_no_science(self):
        put(self.failure, dict(self.value, cause_code='qualification_observation_producer_fault'))
        self.inputs['pre_science_tooling_failure'] = q.reference(self.failure)
        with self.assertRaisesRegex(q.HarvestRefusal, 'not_g2b_recovery'):
            self.classify()
