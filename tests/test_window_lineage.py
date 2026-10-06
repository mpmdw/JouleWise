"""HAZARD_PACK launch lineage (lane L3): the chokepoint on a mock window.

What is real here: the measurement code at every lineage call site
(bundle writer, controller pre-slot attachment, run_campaign preflight and
child check, whole_window, the reduce CLI, floor extraction, analysis inputs,
the calibration writer), the calibration ledger, git, and a REAL block-3
Revision-5 pre-calibration capture (tests/fixtures/controller_g2b/block3-pre).
What is faked: the workload and sampler (mock adapters), the night driver's
two terminal records (written by hand), and the hazard arm decision file
(a stand-in; lane L1 owns it).  No ARM receipt exists anywhere, and the ARM
replay functions are replaced by recording sentinels for the whole module.
"""

from __future__ import annotations

import copy
import gzip
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import ExitStack, redirect_stderr, redirect_stdout
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from joulewise import (
    adapters,
    arm_readiness,
    bundle as bundle_module,
    calibration_ledger as ledger,
    cli,
    controller,
    whole_window,
    window_lineage,
)
from joulewise.analysis_engine import inputs as analysis_inputs
from joulewise.bundle import BundleError
from joulewise.calibration_bracketing import REVISION_FIVE_EPOCH
from joulewise.clock import FakeClock
from joulewise.floor_extraction import _evaluate_member
from joulewise.schemas import BenchmarkConfig, CampaignPolicy, RunStatus
from scripts import run_campaign
from scripts import validate_powermetrics_fiducial as calibration_writer
from tests.git_fixture import init_git_fixture

ROOT = Path(__file__).resolve().parents[1]
CAPTURE_FIXTURE = ROOT / "tests/fixtures/controller_g2b/block3-pre"
ALPHA_TREE = ROOT / "configs/campaigns/d117_floor_qwen3-1p7b_v5/plan_tree.json"
EVIDENCE = json.loads(gzip.decompress((CAPTURE_FIXTURE / "instrument_evidence.json.gz").read_bytes()))
SESSION_ID = EVIDENCE["battery_float"]["pre"]["session_id"]
PRE_ATTEMPT = EVIDENCE["validation_id"]
POST_ATTEMPT = "fixture-post"
PACK_ID = "hazard_fixture_v5"
PLAN_ID = "plan-hazard-fixture-v5"
WINDOW_ID = "plan-hazard-fixture-v5"
TAG = "launch_lineage_required"

# The ARM replay chain.  A hazard window must never reach any of these.
ARM_SENTINELS = (
    "_replay_consumed_arm",
    "_replay_consumed_go",
    "_read_launch_consumption",
    "_read_lifecycle_receipt",
    "_authenticated_pack_config_inventory",
)


def _git(repo: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-C", str(repo), "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
         "-c", "commit.gpgsign=false", *args],
        check=True, capture_output=True,
    )


def _member_config(run_id: str, *, tagged: bool) -> BenchmarkConfig:
    value = json.loads((ROOT / "configs/examples/mock_local.json").read_bytes())
    value["run_id"] = run_id
    tags = [tag for tag in value["run_metadata"]["tags"] if tag != TAG]
    value["run_metadata"]["tags"] = [*tags, TAG] if tagged else tags
    return BenchmarkConfig.from_mapping(value)


def _write_config(path: Path, config: BenchmarkConfig) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(config.to_dict()) + "\n")
    return path


def build_window(base: Path, *, session_id: str = SESSION_ID, publish: bool = True) -> SimpleNamespace:
    """A measurement checkout with one pack, a bracket session and the lineage."""

    base = base.resolve()
    w = SimpleNamespace(base=base)
    w.repo = base / "measurement"
    w.pack = w.repo / "configs/campaigns" / PACK_ID
    w.pack.mkdir(parents=True)
    w.member_path = _write_config(w.pack / "members/member.json", _member_config("hazard-member", tagged=True))
    w.plain_path = _write_config(w.pack / "members/plain.json", _member_config("hazard-plain", tagged=False))
    w.unregistered_path = w.pack / "members/unregistered.json"
    w.unregistered_path.write_bytes(w.member_path.read_bytes())
    w.calibration_config = w.pack / "calibration-acceptance.json"
    w.calibration_config.write_bytes(window_lineage.render_json(
        {"schema_version": "synthetic.calibration_acceptance.v1", "run_metadata": {"tags": [TAG]}}))
    plan_path = w.pack / "calibration_plan.json"
    plan_path.write_text(json.dumps({"plan_id": PLAN_ID}) + "\n")
    w.plan_sha = hashlib.sha256(plan_path.read_bytes()).hexdigest()
    inventory = [
        {"path": path.relative_to(w.pack).as_posix(), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
        for path in (w.member_path, w.plain_path, w.calibration_config)
    ]
    alpha = json.loads(ALPHA_TREE.read_bytes())
    tree = {
        "plan": {"path": "calibration_plan.json", "plan_id": PLAN_ID, "actual_sha256": w.plan_sha},
        "arm_attachments": {"identity_pin_projection": {"identity_units": [
            {"config_inventory": inventory[:2]}, {"config_inventory": inventory[2:]}]}},
        # Real ALPHA external inputs and stage dispatch, so auxiliary members
        # are matched to their runs root exactly as in the block-5 pack.
        "external_inputs": alpha["external_inputs"],
        "stage_graph": alpha["stage_graph"],
    }
    w.auxiliary = [external for external in alpha["external_inputs"]["manifests"] if external.get("members")]
    for external in w.auxiliary:
        for member in external["members"]:
            raw = (ROOT / member["path"]).read_bytes()
            assert hashlib.sha256(raw).hexdigest() == member["sha256"], member["path"]
            target = w.repo / member["path"]
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
    tree_raw = arm_readiness.render_json(tree)
    (w.pack / "plan_tree.json").write_bytes(tree_raw)
    (w.pack / "plan_tree.sha256").write_bytes(
        arm_readiness.gnu_sidecar(hashlib.sha256(tree_raw).hexdigest(), "plan_tree.json"))
    w.pin = w.repo / "configs/calibration/calibration_ledger_head.json"
    w.pin.parent.mkdir(parents=True)
    w.pin.write_text(json.dumps({"sequence": 0, "head_digest": ledger.GENESIS_DIGEST,
                                 "ledger_schema": ledger.LEDGER_SCHEMA}) + "\n")
    w.ledger = w.repo / "runs/calibration_observation_ledger.jsonl"
    init_git_fixture(w.repo, "-q")
    _git(w.repo, "add", "configs")
    _git(w.repo, "commit", "-qm", "hazard fixture pack")

    w.claim = base / "runs_hazard_fixture_v5"
    w.bound = base / "runs_hazard_fixture_v5_bound"
    w.custody = base / "custody"
    for directory in (w.claim, w.bound, w.custody / "hazards"):
        directory.mkdir(parents=True)
    w.night = w.custody / "night"
    w.arm_decision = w.custody / "hazards/arm.json"
    w.arm_decision.write_text('{"decision": "GO", "stand_in": "lane L1 owns this file"}\n')
    w.capture = w.claim / "instrument_validation" / PRE_ATTEMPT
    provenance = json.loads((CAPTURE_FIXTURE / "provenance.json").read_bytes())
    for name, descriptor in provenance["files"].items():
        raw = gzip.decompress((CAPTURE_FIXTURE / (name + ".gz")).read_bytes())
        assert hashlib.sha256(raw).hexdigest() == descriptor["sha256"]
        target = w.capture / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)

    ledger.append_bracket_session_receipt(
        w.ledger, head_pin_path=w.pin, repo_root=w.repo, session_id=session_id,
        window_id=WINDOW_ID, plan_id=PLAN_ID, plan_sha256=w.plan_sha,
        evidence_root_id="hazard-fixture-evidence", runs_root=w.claim,
        session_kind=ledger.SESSION_KIND_BRACKET,
        slots={slot: {"attempt_id": PRE_ATTEMPT if slot == "pre" else POST_ATTEMPT,
                      "custody_locator": str(w.capture if slot == "pre" else w.claim / "instrument_validation" / POST_ATTEMPT),
                      "identity_epoch": REVISION_FIVE_EPOCH, "t1_bindings": EVIDENCE["bindings"]}
               for slot in ("pre", "post")})
    ledger.claim_bracket_session_slot(w.ledger, session_id=session_id, slot="pre", attempt_id=PRE_ATTEMPT)
    ledger.finalize_bracket_session_slot(
        w.ledger, session_id=session_id, slot="pre", disposition="valid",
        custody_locator=str(w.capture), artifact_sha256=ledger.artifact_hashes(w.capture),
        identity_epoch=REVISION_FIVE_EPOCH, t1_bindings=EVIDENCE["bindings"],
        capture_wall_time_s=str(EVIDENCE["capture_wall_time_s"]),
        exact_bound_lexeme_s=str(EVIDENCE["b_fiducial_s"]))
    w.published = None
    if publish:
        w.published = publish_lineage(w)
        w.lineage = w.published["launch_lineage"]
    return w


def publish_lineage(w: SimpleNamespace) -> dict:
    return window_lineage.publish_window_lineage(
        pack_root=w.pack, pack_id=PACK_ID, plan_id=PLAN_ID, window_id=WINDOW_ID,
        bracket_session_id=SESSION_ID, pre_attempt_id=PRE_ATTEMPT, post_attempt_id=POST_ATTEMPT,
        claim_runs_root=w.claim, bound_runs_root=w.bound, custody_root=w.custody,
        arm_decision_path=w.arm_decision)


def write_night_records(w: SimpleNamespace) -> None:
    w.night.mkdir(exist_ok=True)
    (w.night / "chain.exited").write_text('{"exit_code": 0, "epoch_s": 1.0, "monotonic_ns": 1}\n')
    (w.night / "result.json").write_text('{"schema": "joulewise.unattended_night_result.v1", "verdict": "GO"}\n')


def remove_night_records(w: SimpleNamespace) -> None:
    shutil.rmtree(w.night, ignore_errors=True)


class _MockWorkloadRegistry:
    def resolve_runtime(self, config, clock):
        return adapters.resolve_runtime(config, clock)

    def resolve_transport(self, config):
        return adapters.resolve_transport(config)

    def resolve_telemetry(self, config, clock):
        telemetry, failure = adapters.resolve_telemetry(config, clock)
        digest = EVIDENCE["bindings"]["powermetrics_sha256"]
        telemetry.device_metadata = lambda config, context=None: {
            "rail_manifest": ["mock"], "powermetrics": {"executable_sha256": digest}}
        return telemetry, failure


def run_member(w: SimpleNamespace, config_path: Path, *, root: Path | None = None,
               config: BenchmarkConfig | None = None):
    config = config or BenchmarkConfig.from_mapping(json.loads(config_path.read_bytes()))
    policy = CampaignPolicy.from_mapping(json.loads(
        (ROOT / "configs/campaign_policies/quiet_mac_exploratory.json").read_bytes()))
    # Mock workload and sampler: this exercises attachment and lineage, not
    # a live display or idle gate.
    policy = replace(policy, idle_admission=replace(policy.idle_admission, enabled=False))
    with patch.object(sys, "argv", ["joulewise", "run", str(config_path)]), \
            patch.dict(os.environ, {}, clear=True):
        return controller.run_benchmark(
            config, root or w.claim, FakeClock(start=1700000000),
            registry=_MockWorkloadRegistry(), environment_snapshot=None, campaign_policy=policy,
            campaign_environment_preflight={"snapshot": {
                "power_source": "AC Power", "power": {"external_connected": True}, "low_power_mode": False}},
            instrument_calibration_dir=w.capture, instrument_power_policy="ac_high_power")


def load_auxiliary(w: SimpleNamespace, path: Path, root: Path):
    config = BenchmarkConfig.from_mapping(json.loads(path.read_bytes()))
    with patch.object(sys, "argv", ["joulewise", "run", str(path)]), \
            patch.dict(os.environ, {}, clear=True):
        return controller._load_instrument_calibration_attachment(
            w.capture, power_policy="ac_high_power",
            runtime_powermetrics_sha256=EVIDENCE["bindings"]["powermetrics_sha256"],
            runtime_power_policy="ac_high_power", runs_root=root, config=config)


class _SentinelMixin:
    """Replace the ARM replay chain with recording sentinels."""

    sentinel_calls: list

    @classmethod
    def _start_sentinels(cls) -> ExitStack:
        cls.sentinel_calls = []
        stack = ExitStack()
        for name in ARM_SENTINELS:
            def sentinel(*_args, _name=name, **_kwargs):
                cls.sentinel_calls.append(_name)
                raise AssertionError(f"hazard window reached arm_readiness.{_name}")
            stack.enter_context(patch.object(arm_readiness, name, side_effect=sentinel))
        return stack


class HazardWindowCallSiteTests(_SentinelMixin, unittest.TestCase):
    """Every lineage call site, on one mock window with one real member bundle."""

    @classmethod
    def setUpClass(cls) -> None:
        tmp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(tmp.cleanup)
        cls.addClassCleanup(cls._start_sentinels().close)
        cls.w = build_window(Path(tmp.name))
        cls.lineage = cls.w.lineage
        cls.bundle, cls.summary = run_member(cls.w, cls.w.member_path)

    def setUp(self) -> None:
        self.w = type(self).w
        self.addCleanup(remove_night_records, self.w)

    def tearDown(self) -> None:
        self.assertEqual(type(self).sentinel_calls, [], "a hazard path reached the ARM replay")

    # bundle.py:128 and controller.py:610, through controller.run_benchmark

    def test_controller_collects_science_member_with_hazard_lineage_and_pre_slot(self) -> None:
        self.assertEqual(self.summary.status, RunStatus.SUCCEEDED, self.summary.failure_message)
        metadata = json.loads((self.bundle / "metadata.json").read_bytes())
        self.assertEqual(metadata["extra"]["launch_lineage"], self.lineage)
        claim_locator = self.w.claim / window_lineage.LOCATOR_BASENAME
        self.assertEqual(metadata["extra"]["launch_lineage_locator_sha256"],
                         hashlib.sha256(claim_locator.read_bytes()).hexdigest())
        attachment = metadata["instrument_calibration"]["g2b_pre_slot"]
        self.assertEqual(attachment["session_id"], SESSION_ID)
        self.assertEqual(attachment["plan_sha256"], self.w.plan_sha)
        self.assertEqual(attachment["launch_lineage_locator_sha256"],
                         metadata["extra"]["launch_lineage_locator_sha256"])
        self.assertGreater(metadata["instrument_calibration"]["verified_effective_b_fiducial_s"], 0)

    def test_bundle_writer_lineage_returns_stamp_and_locator_digest(self) -> None:
        config = BenchmarkConfig.from_mapping(json.loads(self.w.member_path.read_bytes()))
        with patch.object(sys, "argv", ["joulewise", "run", str(self.w.member_path)]):
            lineage, digest = bundle_module._writer_launch_lineage(self.w.claim, config)
        self.assertEqual(lineage, self.lineage)
        self.assertEqual(digest, self.w.published["locators"]["claim_runs_root"]["sha256"])

    def test_auxiliary_members_attach_only_in_their_plan_bound_root(self) -> None:
        # One full (slow, real-capture) attach per root; every input is
        # refused in the other root.
        attach = {"neg8_bound", "start_reference"}
        for external in self.w.auxiliary:
            root = self.w.bound if external["external_input_id"] == "neg8_bound" else self.w.claim
            wrong = self.w.claim if root == self.w.bound else self.w.bound
            path = self.w.repo / external["members"][0]["path"]
            with self.subTest(input=external["external_input_id"]):
                self.assertFalse(arm_readiness.launch_lineage_required(json.loads(path.read_bytes())))
                if external["external_input_id"] in attach:
                    attachment = load_auxiliary(self.w, path, root)
                    self.assertEqual(attachment.metadata["g2b_pre_slot"]["session_id"], SESSION_ID)
                with self.assertRaisesRegex(ValueError, "revision_five"):
                    load_auxiliary(self.w, path, wrong)

    # run_campaign.py:1899 and the child-bundle check

    def test_run_campaign_preflight_block_limit_and_child_check(self) -> None:
        authentication = run_campaign.authenticate_campaign_writer_preflight(
            [self.w.member_path], self.w.claim)
        self.assertEqual(authentication["launch_lineage"], self.lineage)
        self.assertEqual(authentication["root_role"], "claim_runs_root")
        # The block-limit reader follows launch -> go -> authorization; the
        # HAZARD_PACK purpose applies no limit.
        self.assertIsNone(run_campaign.campaign_block_limit(None, authentication, [], []))
        binding = run_campaign._authenticated_campaign_block_limit(authentication)
        self.assertEqual(binding["purpose"], window_lineage.HAZARD_PURPOSE)
        run_campaign.authenticate_campaign_child_launch_lineage(authentication, [self.bundle])

    def test_run_campaign_refuses_mixed_tagged_and_untagged_selection(self) -> None:
        with self.assertRaises(arm_readiness.LaunchLineageError) as caught:
            run_campaign.authenticate_campaign_writer_preflight(
                [self.w.member_path, self.w.plain_path], self.w.claim)
        self.assertEqual(caught.exception.reason_code, "launch_binding_mismatch")

    # cli.py:1845 and strict validation

    def test_strict_validation_passes_and_rereduction_is_byte_identical(self) -> None:
        self.assertEqual(cli.validate_bundle(self.bundle, strict=True), [])
        output = self.w.base / "rereduced.json"
        self.addCleanup(lambda: output.unlink(missing_ok=True))
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            exit_code = cli.main(["reduce", str(self.bundle), "--output", str(output)])
        self.assertEqual(exit_code, 0, err.getvalue())
        rederived = json.loads(output.read_bytes())
        self.assertEqual(rederived.pop("launch_lineage"), self.lineage)
        self.assertEqual((json.dumps(rederived, indent=2, sort_keys=True) + "\n").encode(),
                         (self.bundle / "summary_metrics.json").read_bytes())

    # whole_window.py:2454 (member set), :2533 (calibrations), :2576 (bound)

    def test_whole_window_member_set_requires_driver_completion_records(self) -> None:
        reasons = whole_window.launch_lineage_refusal_reasons(
            self.w.claim, {self.bundle.name}, require_completion=False)
        self.assertEqual(reasons, ())
        reasons = whole_window.launch_lineage_refusal_reasons(
            self.w.claim, {self.bundle.name}, require_completion=True)
        self.assertEqual(reasons, ("launch_lifecycle_incomplete",))
        write_night_records(self.w)
        self.assertEqual(whole_window.launch_lineage_refusal_reasons(
            self.w.claim, {self.bundle.name}, require_completion=True), ())
        self.assertEqual(whole_window._authenticated_bundle_launch_lineage_set(
            [self.bundle], require_completion=True), self.lineage)

    def _calibration_bracket(self) -> dict:
        bracket: dict = {}
        for role in ("pre", "post"):
            custody = self.w.base / f"calibration-evidence-{role}"
            custody.mkdir(exist_ok=True)
            raw = json.dumps({"launch_lineage": self.lineage}).encode()
            (custody / "instrument_evidence.json").write_bytes(raw)
            bracket[role] = {"relative_path": str(custody), "evidence_sha256": hashlib.sha256(raw).hexdigest()}
        return bracket

    def test_whole_window_calibrations_and_bound_share_the_member_lineage(self) -> None:
        bracket = self._calibration_bracket()
        write_night_records(self.w)
        self.assertEqual(whole_window._calibration_launch_lineages(bracket, require_completion=True),
                         (self.lineage, self.lineage))
        self.assertEqual(whole_window._authenticate_whole_window_launch_sources(
            copy.deepcopy(self.lineage), calibration_bracket=bracket,
            drift_bound_artifact={"launch_lineage": self.lineage},
            require_completion=True, require_bound=True), self.lineage)
        foreign = copy.deepcopy(self.lineage)
        foreign["window_id"] = "another-window"
        with self.assertRaises(arm_readiness.LaunchLineageError) as caught:
            whole_window._authenticate_whole_window_launch_sources(
                copy.deepcopy(self.lineage), calibration_bracket=bracket,
                drift_bound_artifact={"launch_lineage": foreign},
                require_completion=True, require_bound=True)
        self.assertEqual(caught.exception.reason_code, "launch_lineage_conflict")

    # whole_window.py:3642 (NEG-8 mint) and :1727 (NEG-8 bound validation)

    def test_neg8_mint_authenticates_every_member_and_bound_validates(self) -> None:
        root = self.w.base / "neg8-corpus"
        root.mkdir()
        locator_digest = self.w.published["locators"]["claim_runs_root"]["sha256"]
        members = []
        for index in range(10):
            path = root / f"member-{index}"
            path.mkdir()
            (path / "config.json").write_text(json.dumps({"run_metadata": {"tags": [TAG]}}) + "\n")
            (path / "metadata.json").write_text(json.dumps({"extra": {
                "launch_lineage": self.lineage, "launch_lineage_locator_sha256": locator_digest}}) + "\n")
            (path / "summary_metrics.json").write_text("{}\n")
            members.append({"bundle_id": path.name, "bundle_path": path.name})
        manifest = root / "neg8-corpus.json"
        manifest.write_text(json.dumps({
            "schema_version": "joulewise.neg8_reference_corpus.v1", "corpus_id": "hazard-corpus",
            "freeze_status": "settled_reference", "condition_id": "df-rq-mid", "members": members}) + "\n")

        def reference(path: Path):
            value = 10.0 + float(path.name.rsplit("-", 1)[1])
            return {"point_j": value, "lower_j": value, "upper_j": value}, value - 1.0, None

        # Only the non-lineage member gates are stubbed (these synthetic
        # members carry no energies); the lineage gate at :3642 is real.
        with ExitStack() as stack:
            for target, kwargs in (
                ("_custody_strict_invalid", {"return_value": False}),
                ("_current_strict_summary", {"return_value": True}),
                ("_scientific_config_identity", {"return_value": ("d" * 64, True)}),
                ("_reference_energy_evidence", {"side_effect": reference}),
                ("neg8_freshness_bindings_from_metadata", {"return_value": {
                    "os_build": "fixture-os", "power_supply_identity_sha256": "e" * 64,
                    "calibration_identity_sha256": "f" * 64}}),
                ("_bundle_evidence_sha256", {"return_value": "1" * 64}),
            ):
                stack.enter_context(patch.object(whole_window, target, **kwargs))
            spy = stack.enter_context(patch.object(
                whole_window, "authenticate_bundle_launch_lineage",
                wraps=whole_window.authenticate_bundle_launch_lineage))
            artifact = whole_window.mint_neg8_drift_bound_artifact(root, manifest)
            self.assertEqual(spy.call_count, 10)
            broken = json.loads((root / "member-3/metadata.json").read_bytes())
            del broken["extra"]["launch_lineage"]["window_context"]
            (root / "member-3/metadata.json").write_text(json.dumps(broken) + "\n")
            with self.assertRaisesRegex(ValueError, "launch_consumption_invalid"):
                whole_window.mint_neg8_drift_bound_artifact(root, manifest)
        self.assertEqual(artifact["launch_lineage"], self.lineage)
        self.assertTrue(whole_window.validate_neg8_drift_bound_artifact(artifact))
        tampered = copy.deepcopy(artifact)
        tampered["launch_lineage"]["pack_sha256"] = "not-a-digest"
        self.assertFalse(whole_window.validate_neg8_drift_bound_artifact(tampered))

    # floor_extraction.py:1944

    def test_floor_extraction_member_requires_completion_only(self) -> None:
        def evaluate():
            return _evaluate_member(
                slot="member", bundle_id=self.bundle.name, block_id=None, position=None,
                runs_root=self.w.claim, metric="gross_energy_j", window_class="request",
                cooldowns={}, hash_bundles=False, strict_validator=lambda _path, _strict: ())

        self.assertIn("launch_lifecycle_incomplete", evaluate().reasons)
        write_night_records(self.w)
        member = evaluate()
        self.assertFalse([reason for reason in member.reasons if reason.startswith("launch_")], member.reasons)
        self.assertEqual(member.launch_lineage, self.lineage)

    # analysis_engine/inputs.py:2790 (bundle) and :927 (floor artifact)

    def test_analysis_inputs_read_bundle_carries_pack_identity(self) -> None:
        source_config = json.loads(self.w.member_path.read_bytes())
        entry = {"entry_id": "e1", "run_id": source_config["run_id"]}
        evidence = analysis_inputs._read_bundle(
            entry, self.bundle, self.w.claim, source_config, lambda _path, _strict=True: [])
        self.assertEqual(evidence.launch_lineage["launch_lineage"], self.lineage)
        self.assertEqual(evidence.launch_lineage["pack_root"], str(self.w.pack.resolve()))
        self.assertEqual(evidence.launch_lineage["pack_sha256"],
                         arm_readiness.committed_pack_tree_sha256(self.w.pack))
        self.assertEqual(analysis_inputs._require_common_launch_lineage((evidence,)), self.lineage)

    def test_analysis_inputs_floor_artifact_reauthenticates_hazard_lineage(self) -> None:
        from joulewise import detection_floor
        from tests.test_detection_floor import make_artifact

        artifact = make_artifact()
        artifact["provenance"]["launch_lineage"] = self.lineage
        raw = (json.dumps(artifact, sort_keys=True, allow_nan=False) + "\n").encode()
        real_validate = detection_floor.validate_floor_artifact

        def validate_without_carrier_schema(value):
            # detection_floor's carrier validator (another lane's file) knows
            # only the ARM lineage schema; validate everything else for real.
            stripped = copy.deepcopy(value)
            stripped["provenance"].pop("launch_lineage", None)
            return real_validate(stripped)

        with patch.object(analysis_inputs, "validate_floor_artifact", validate_without_carrier_schema):
            with self.assertRaisesRegex(analysis_inputs.AnalysisInputError, "launch_lifecycle_incomplete"):
                analysis_inputs.authenticate_floor_artifact_bytes(raw)
            write_night_records(self.w)
            admitted = analysis_inputs.authenticate_floor_artifact_bytes(raw)
        self.assertEqual(admitted.value["provenance"]["launch_lineage"], self.lineage)

    # validate_powermetrics_fiducial.py:984

    def test_calibration_writer_binds_session_slot_and_attempt(self) -> None:
        output_root = self.w.claim / "instrument_validation"
        for slot, attempt in (("pre", PRE_ATTEMPT), ("post", POST_ATTEMPT)):
            with self.subTest(slot=slot):
                authenticated = calibration_writer.authenticate_calibration_writer_launch_lineage(
                    output_root, session_id=SESSION_ID, slot=slot, attempt_id=attempt,
                    source_config_path=self.w.calibration_config)
                self.assertEqual(authenticated["launch_lineage"], self.lineage)
                self.assertEqual(authenticated["selected_config_sha256"],
                                 hashlib.sha256(self.w.calibration_config.read_bytes()).hexdigest())
                self.assertEqual(calibration_writer.reconcile_calibration_writer_launch_lineage(
                    authenticated, output_root, session_id=SESSION_ID, slot=slot, attempt_id=attempt,
                    source_config_path=self.w.calibration_config), authenticated)
        for kwargs in ({"session_id": "foreign-session", "attempt_id": PRE_ATTEMPT},
                       {"session_id": SESSION_ID, "attempt_id": POST_ATTEMPT}):
            with self.subTest(**kwargs), self.assertRaises(ValueError) as caught:
                calibration_writer.authenticate_calibration_writer_launch_lineage(
                    output_root, slot="pre", source_config_path=self.w.calibration_config, **kwargs)
            self.assertEqual(caught.exception.reason_code, "launch_binding_mismatch")

    def test_collection_after_chain_exit_is_refused(self) -> None:
        write_night_records(self.w)
        with self.assertRaises(arm_readiness.LaunchLineageError) as caught:
            arm_readiness.authenticate_campaign_launch_lineage(
                self.w.claim, config_paths=(self.w.member_path,))
        self.assertEqual(caught.exception.reason_code, "launch_binding_mismatch")
        with self.assertRaises(ValueError) as caught:
            calibration_writer.authenticate_calibration_writer_launch_lineage(
                self.w.claim / "instrument_validation", session_id=SESSION_ID, slot="post",
                attempt_id=POST_ATTEMPT, source_config_path=self.w.calibration_config)
        self.assertEqual(caught.exception.reason_code, "launch_binding_mismatch")

    def test_collection_is_refused_on_either_driver_record_alone(self) -> None:
        # chain.exited lands before the G10 tail (network time ON, clock
        # step); result.json only after it.  Each alone must stop collection.
        for name in ("chain.exited", "result.json"):
            with self.subTest(record=name):
                remove_night_records(self.w)
                self.w.night.mkdir()
                (self.w.night / name).write_text("{}\n")
                with self.assertRaises(arm_readiness.LaunchLineageError) as caught:
                    arm_readiness.authenticate_campaign_launch_lineage(
                        self.w.claim, config_paths=(self.w.member_path,))
                self.assertEqual(caught.exception.reason_code, "launch_binding_mismatch")
                self.assertIn(name, str(caught.exception))
                config = BenchmarkConfig.from_mapping(json.loads(self.w.member_path.read_bytes()))
                with patch.object(sys, "argv", ["joulewise", "run", str(self.w.member_path)]), \
                        self.assertRaisesRegex(BundleError, "launch_binding_mismatch"):
                    bundle_module._writer_launch_lineage(self.w.claim, config)

    # Analysis from a different checkout (memo 3.2, 3.6)

    def test_analysis_from_a_different_checkout_passes(self) -> None:
        write_night_records(self.w)
        other = self.w.base / "other-checkout"
        shutil.copytree(ROOT / "joulewise", other / "joulewise",
                        ignore=shutil.ignore_patterns("__pycache__"))
        program = (
            "import json, sys\n"
            "from pathlib import Path\n"
            "import joulewise\n"
            "from joulewise import arm_readiness, whole_window\n"
            "bundle = Path(sys.argv[1])\n"
            "context = arm_readiness.authenticate_bundle_launch_lineage(bundle, require_completion=True)\n"
            "reasons = whole_window.launch_lineage_refusal_reasons("
            "bundle.parent, {bundle.name}, require_completion=True)\n"
            "print(json.dumps({'module': joulewise.__file__, 'lineage': context['launch_lineage'],"
            " 'reasons': list(reasons)}))\n"
        )
        site = [entry for entry in sys.path if entry.endswith("site-packages")]
        completed = subprocess.run(
            [sys.executable, "-B", "-c", program, str(self.bundle)], cwd=other,
            env={**os.environ, "PYTHONPATH": os.pathsep.join([str(other), *site])},
            capture_output=True, text=True, check=False)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        result = json.loads(completed.stdout.splitlines()[-1])
        self.assertTrue(Path(result["module"]).resolve().is_relative_to(other.resolve()))
        self.assertEqual(result["lineage"], self.lineage)
        self.assertEqual(result["reasons"], [])

    # Records audit: a clean window has no findings

    def test_audit_of_the_published_window_is_clean(self) -> None:
        write_night_records(self.w)
        self.assertEqual(window_lineage.audit_window_lineage(
            claim_runs_root=self.w.claim, bound_runs_root=self.w.bound,
            bundle_paths=[self.bundle]), [])


class HazardWindowRefusalTests(_SentinelMixin, unittest.TestCase):
    """What the hazard path still refuses: wrong config bytes, a foreign pre-slot."""

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.addCleanup(self._start_sentinels().close)
        self.base = Path(tmp.name)

    def tearDown(self) -> None:
        self.assertEqual(type(self).sentinel_calls, [], "a hazard path reached the ARM replay")

    def test_flipped_config_byte_is_refused_at_every_collection_gate(self) -> None:
        w = build_window(self.base)
        raw = bytearray(w.member_path.read_bytes())
        raw[raw.index(b"hazard-member")] ^= 0x01  # "hazard-member" -> "iazard-member"
        w.member_path.write_bytes(bytes(raw))
        config = BenchmarkConfig.from_mapping(json.loads(w.member_path.read_bytes()))
        with self.assertRaises(arm_readiness.LaunchLineageError) as caught:
            arm_readiness.authenticate_campaign_launch_lineage(w.claim, config_paths=(w.member_path,))
        self.assertEqual(caught.exception.reason_code, "launch_binding_mismatch")
        self.assertIn("not in the pack's committed inventory", str(caught.exception))
        with self.assertRaises(arm_readiness.LaunchLineageError):
            run_campaign.authenticate_campaign_writer_preflight([w.member_path], w.claim)
        with patch.object(sys, "argv", ["joulewise", "run", str(w.member_path)]), \
                self.assertRaisesRegex(BundleError, "launch_binding_mismatch"):
            bundle_module._writer_launch_lineage(w.claim, config)
        # Through the controller: the pre-slot route admits no unauthenticated
        # member, so the run is refused before any bundle directory exists.
        with self.assertRaisesRegex(ValueError, "revision_five"):
            run_member(w, w.member_path, config=config)
        self.assertFalse((w.claim / config.run_id).exists())
        self.assertEqual(sorted(p.name for p in w.claim.iterdir()),
                         [".joulewise-launch-lineage.json", ".joulewise-launch-lineage.json.sha256",
                          "instrument_validation"])

    def test_unregistered_tagged_config_is_refused(self) -> None:
        w = build_window(self.base)
        with self.assertRaises(arm_readiness.LaunchLineageError) as caught:
            arm_readiness.authenticate_campaign_launch_lineage(w.claim, config_paths=(w.unregistered_path,))
        self.assertEqual(caught.exception.reason_code, "launch_binding_mismatch")

    def test_plan_tree_changed_after_publication_is_refused(self) -> None:
        w = build_window(self.base)
        tree = w.pack / "plan_tree.json"
        tree.write_bytes(tree.read_bytes() + b"\n")
        with self.assertRaises(arm_readiness.LaunchLineageError) as caught:
            arm_readiness.authenticate_campaign_launch_lineage(w.claim, config_paths=(w.member_path,))
        self.assertIn("plan_tree_sha256", str(caught.exception))

    def test_foreign_bracket_session_pre_slot_is_refused(self) -> None:
        # The ledger's open session is not the one the lineage names.
        w = build_window(self.base, session_id="foreign-session")
        with self.assertRaises(ledger.CalibrationLedgerError):
            run_member(w, w.member_path)
        self.assertFalse((w.claim / "hazard-member").exists())

    def test_config_symlink_is_refused_even_to_registered_bytes(self) -> None:
        w = build_window(self.base)
        for link in (w.pack / "members/link.json", self.base / "outside-link.json"):
            with self.subTest(link=link.name):
                link.symlink_to(w.member_path)
                with self.assertRaises(arm_readiness.LaunchLineageError) as caught:
                    arm_readiness.authenticate_campaign_launch_lineage(w.claim, config_paths=(link,))
                self.assertEqual(caught.exception.reason_code, "launch_binding_mismatch")
                self.assertIn("symlink", str(caught.exception))

    def test_conflicting_duplicate_inventory_rows_are_refused(self) -> None:
        pack = self.base / "pack"
        pack.mkdir()
        row = {"path": "members/a.json", "sha256": "a" * 64}

        def tree_sha(units: list) -> str:
            raw = window_lineage.render_json({"arm_attachments": {"identity_pin_projection": {
                "identity_units": [{"config_inventory": rows} for rows in units]}}})
            (pack / "plan_tree.json").write_bytes(raw)
            return hashlib.sha256(raw).hexdigest()

        agreeing = tree_sha([[row], [dict(row)]])
        self.assertEqual(window_lineage.config_inventory(pack, agreeing), {"members/a.json": "a" * 64})
        conflicting = tree_sha([[row], [{**row, "sha256": "b" * 64}]])
        with self.assertRaises(window_lineage.HazardLineageError) as caught:
            window_lineage.config_inventory(pack, conflicting)
        self.assertEqual(caught.exception.reason_code, "launch_binding_mismatch")
        self.assertIn("two digests", str(caught.exception))

    def test_collection_after_reboot_is_refused_but_unreadable_boot_is_not(self) -> None:
        w = build_window(self.base)
        other_boot = "00000000-0000-4000-8000-000000000000"
        with patch.object(window_lineage, "current_boot_session_id", return_value=other_boot), \
                self.assertRaises(arm_readiness.LaunchLineageError) as caught:
            arm_readiness.authenticate_campaign_launch_lineage(w.claim, config_paths=(w.member_path,))
        self.assertEqual(caught.exception.reason_code, "launch_binding_mismatch")
        with patch.object(window_lineage, "current_boot_session_id", return_value=None):
            context = arm_readiness.authenticate_campaign_launch_lineage(
                w.claim, config_paths=(w.member_path,))
        self.assertEqual(context["launch_lineage"], w.lineage)


class DispatchTests(_SentinelMixin, unittest.TestCase):
    """Schema dispatch: hazard values never touch the ARM chain; ARM values do."""

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.w = build_window(Path(tmp.name))
        self.addCleanup(self._start_sentinels().close)

    def test_replay_consumed_arm_is_never_reached_from_any_entry_point(self) -> None:
        w = self.w
        bundle = w.claim / "stamped"
        bundle.mkdir()
        (bundle / "config.json").write_text(json.dumps({"run_metadata": {"tags": [TAG]}}) + "\n")
        (bundle / "metadata.json").write_text(json.dumps({"extra": {
            "launch_lineage": w.lineage,
            "launch_lineage_locator_sha256": w.published["locators"]["claim_runs_root"]["sha256"]}}) + "\n")
        locator = w.claim / window_lineage.LOCATOR_BASENAME
        results = [
            arm_readiness.authenticate_launch_lineage(w.lineage, require_completion=False),
            arm_readiness.authenticate_launch_lineage(
                w.lineage, require_completion=False, expected_pack_root=w.pack,
                require_current_boot=True, require_completion_absent=True),
            arm_readiness.authenticate_campaign_launch_lineage(w.claim, config_paths=(w.member_path,)),
            arm_readiness.authenticate_campaign_launch_lineage(w.bound),
            arm_readiness.authenticate_bundle_launch_lineage(bundle, require_completion=False),
        ]
        located, digest = arm_readiness._read_launch_lineage_locator(locator, expected_root=w.claim)
        self.assertEqual(located["launch_lineage"], w.lineage)
        self.assertEqual(digest, hashlib.sha256(locator.read_bytes()).hexdigest())
        self.assertEqual(self.sentinel_calls, [])
        self.assertEqual(results[2]["root_role"], "claim_runs_root")
        self.assertEqual(results[3]["root_role"], "bound_runs_root")
        for result in (results[0], results[1], results[4]):
            self.assertEqual(result["arm_context"]["bracket_session_id"], SESSION_ID)
            self.assertEqual(result["arm_context"]["pre_attempt_id"], PRE_ATTEMPT)
            self.assertEqual(result["launch_lineage"], w.lineage)

    def test_sentinel_is_wired_an_arm_schema_lineage_reaches_it(self) -> None:
        # Positive control: an ARM-schema value still takes the ARM chain.
        arm_lineage = {
            "schema_version": arm_readiness.LAUNCH_LINEAGE_SCHEMA,
            "collection_boot_session_id": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
            "pack_id": "pack-1", "plan_id": "plan-1", "window_id": "window-1",
            "bracket_session_id": "bracket-1",
            "consumption": {"path": "/consume.json", "sha256": "a" * 64},
            "start": {"path": "/start.json", "sha256": "b" * 64},
            "settle": {"path": "/settle.json", "sha256": "c" * 64},
            "completion": None,
        }
        consumption = ({"schema_version": "fixture"}, b"", "a" * 64, Path("/consume.json"))
        with patch.object(arm_readiness, "_read_launch_consumption", return_value=consumption), \
                self.assertRaisesRegex(AssertionError, "_replay_consumed_arm"):
            arm_readiness.authenticate_launch_lineage(arm_lineage, require_completion=False)
        self.assertEqual(self.sentinel_calls, ["_replay_consumed_arm"])
        self.sentinel_calls.clear()

    def test_arm_locators_and_malformed_files_keep_their_arm_refusals(self) -> None:
        locator = self.w.claim / window_lineage.LOCATOR_BASENAME
        locator.unlink()
        locator.write_bytes(b"{}\n")
        with self.assertRaises(arm_readiness.LaunchLineageError) as caught:
            arm_readiness.authenticate_campaign_launch_lineage(self.w.claim)
        self.assertEqual(caught.exception.reason_code, "launch_consumption_invalid")
        self.assertFalse(window_lineage.is_hazard_locator(locator))
        self.assertFalse(window_lineage.is_hazard_locator(self.w.claim / "absent.json"))
        self.assertFalse(window_lineage.is_hazard_locator(self.w.claim))
        self.assertFalse(window_lineage.is_hazard_lineage({"schema_version": arm_readiness.LAUNCH_LINEAGE_SCHEMA}))
        self.assertFalse(window_lineage.is_hazard_lineage(None))

    def test_hazard_refusals_surface_as_registered_launch_lineage_errors(self) -> None:
        self.assertLessEqual(window_lineage.REASON_CODES, arm_readiness.LAUNCH_LINEAGE_REASON_CODES)
        self.assertEqual(window_lineage.LOCATOR_BASENAME, arm_readiness.LAUNCH_LINEAGE_LOCATOR_BASENAME)
        broken = copy.deepcopy(self.w.lineage)
        broken["pack_root"] = "relative/pack"
        with self.assertRaises(arm_readiness.LaunchLineageError) as caught:
            arm_readiness.authenticate_launch_lineage(broken, require_completion=False)
        self.assertEqual(caught.exception.reason_code, "launch_consumption_invalid")
        with self.assertRaises(arm_readiness.LaunchLineageError) as caught:
            arm_readiness.authenticate_launch_lineage(self.w.lineage, require_completion=True)
        self.assertEqual(caught.exception.reason_code, "launch_lifecycle_incomplete")
        with self.assertRaises(arm_readiness.LaunchLineageError) as caught:
            arm_readiness.authenticate_launch_lineage(
                self.w.lineage, require_completion=False, expected_pack_root=self.w.base)
        self.assertEqual(caught.exception.reason_code, "launch_binding_mismatch")
        with self.assertRaises(ValueError):
            arm_readiness.authenticate_launch_lineage(
                self.w.lineage, require_completion=True, require_completion_absent=True)


class PublicationAndAuditTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.w = build_window(Path(tmp.name))

    def audit(self, **kwargs) -> list[str]:
        findings = window_lineage.audit_window_lineage(
            claim_runs_root=self.w.claim, bound_runs_root=self.w.bound, **kwargs)
        for finding in findings:
            self.assertIn(finding["code"], window_lineage.FINDING_CODES)
        return sorted(finding["code"] for finding in findings)

    def test_publication_is_create_once_canonical_and_records_chain(self) -> None:
        w = self.w
        for root, role in ((w.claim, "claim_runs_root"), (w.bound, "bound_runs_root")):
            raw = (root / window_lineage.LOCATOR_BASENAME).read_bytes()
            locator = json.loads(raw)
            self.assertEqual(raw, window_lineage.render_json(locator))
            self.assertEqual(locator["root_role"], role)
            self.assertEqual(locator["launch_lineage"], w.lineage)
        self.assertEqual(w.lineage["pack_sha256"], arm_readiness.committed_pack_tree_sha256(w.pack))
        self.assertEqual(w.lineage["window_context"]["night_dir"], str(w.custody.resolve() / "night"))
        go = json.loads(Path(w.published["records"]["go"]["path"]).read_bytes())
        self.assertEqual(go["arm_decision"]["sha256"], hashlib.sha256(w.arm_decision.read_bytes()).hexdigest())
        with self.assertRaises(window_lineage.LineagePublicationError):
            publish_lineage(w)
        self.assertEqual(self.audit(), ["lineage.completion_records_absent"])

    def test_publication_refuses_shared_roots_and_unusable_inventory(self) -> None:
        with self.assertRaisesRegex(window_lineage.LineagePublicationError, "distinct"):
            window_lineage.publish_window_lineage(
                pack_root=self.w.pack, pack_id=PACK_ID, plan_id=PLAN_ID, window_id=WINDOW_ID,
                bracket_session_id=SESSION_ID, pre_attempt_id=PRE_ATTEMPT, post_attempt_id=POST_ATTEMPT,
                claim_runs_root=self.w.claim, bound_runs_root=self.w.claim, custody_root=self.w.custody)
        empty_pack = self.w.base / "empty-pack"
        empty_pack.mkdir()
        (empty_pack / "plan_tree.json").write_text("{}\n")
        with self.assertRaisesRegex(window_lineage.LineagePublicationError, "inventory"):
            window_lineage.publish_window_lineage(
                pack_root=empty_pack, pack_id=PACK_ID, plan_id=PLAN_ID, window_id=WINDOW_ID,
                bracket_session_id=SESSION_ID, pre_attempt_id=PRE_ATTEMPT, post_attempt_id=POST_ATTEMPT,
                claim_runs_root=self.w.claim, bound_runs_root=self.w.bound, custody_root=self.w.custody,
                pack_sha256="0" * 64)

    def test_records_formalities_are_findings_not_refusals(self) -> None:
        w = self.w
        write_night_records(w)
        self.assertEqual(self.audit(), [])
        claim_locator = w.claim / window_lineage.LOCATOR_BASENAME
        sidecar = claim_locator.with_name(claim_locator.name + ".sha256")
        sidecar.write_text("0" * 64 + "  " + claim_locator.name + "\n")
        bound_locator = w.bound / window_lineage.LOCATOR_BASENAME
        bound_value = json.loads(bound_locator.read_bytes())
        bound_value["launch_lineage"]["plan_id"] = "drifted"
        bound_locator.write_text(json.dumps(bound_value))  # noncanonical bytes
        launch = Path(w.lineage["launch_record"]["path"])
        launch.write_bytes(launch.read_bytes() + b" ")
        self.assertEqual(self.audit(), [
            "lineage.locator_noncanonical",
            "lineage.locator_sidecar_mismatch",
            "lineage.locator_sidecar_mismatch",
            "lineage.record_chain_unverified",
            "lineage.sibling_lineage_differs",
        ])
        # None of these stops collection: the claim root still authenticates
        # its member configs.
        remove_night_records(w)
        context = arm_readiness.authenticate_campaign_launch_lineage(w.claim, config_paths=(w.member_path,))
        self.assertEqual(context["launch_lineage"], w.lineage)

    def test_moved_roots_and_bundle_stamps_are_findings(self) -> None:
        w = self.w
        write_night_records(w)
        moved = w.base / "archive-copy"
        shutil.copytree(w.claim, moved)
        bundle = moved / "stamped"
        bundle.mkdir()
        stamp = copy.deepcopy(w.lineage)
        stamp["window_id"] = "another-window"
        (bundle / "metadata.json").write_text(json.dumps({"extra": {
            "launch_lineage": stamp, "launch_lineage_locator_sha256": "0" * 64}}))
        unstamped = moved / "unstamped"
        unstamped.mkdir()
        (unstamped / "metadata.json").write_text("{}")
        findings = window_lineage.audit_window_lineage(
            claim_runs_root=moved, bound_runs_root=w.bound, bundle_paths=[bundle, unstamped])
        self.assertEqual(sorted(finding["code"] for finding in findings), [
            "lineage.bundle_locator_digest_differs",
            "lineage.bundle_stamp_absent",
            "lineage.bundle_stamp_differs",
            "lineage.context_root_differs",
            "lineage.locator_root_path_differs",
        ])
        # The archive copy still authenticates for analysis readers.
        archived = moved / "reader"
        archived.mkdir()
        (archived / "config.json").write_text(json.dumps({"run_metadata": {"tags": [TAG]}}))
        (archived / "metadata.json").write_text(json.dumps({"extra": {
            "launch_lineage": w.lineage, "launch_lineage_locator_sha256": "0" * 64}}))
        context = arm_readiness.authenticate_bundle_launch_lineage(archived, require_completion=True)
        self.assertEqual(context["launch_lineage"], w.lineage)

    def test_an_untagged_bundle_without_a_stamp_is_not_a_finding(self) -> None:
        """Rehearsal round 1, B6: the writer stamps only marker-bearing configs.

        Before the fix every NEG-8 corpus and window-reference bundle (19 per
        window) was a lineage.bundle_stamp_absent finding.
        """
        w = self.w
        write_night_records(w)

        def bundle(name: str, config: object | None, metadata: dict) -> Path:
            path = w.base / "bundles" / name
            path.mkdir(parents=True)
            if config is not None:
                (path / "config.json").write_text(config if isinstance(config, str) else json.dumps(config))
            (path / "metadata.json").write_text(json.dumps(metadata))
            return path

        stamp = copy.deepcopy(w.lineage)
        stamp["window_id"] = "another-window"
        cases = {
            "tagged_unstamped": ({"run_metadata": {"tags": [TAG]}}, {}, ["lineage.bundle_stamp_absent"]),
            "untagged_unstamped": ({"run_metadata": {"tags": ["mock"]}}, {}, []),
            "no_tags_unstamped": ({"run_metadata": {}}, {}, []),
            "unreadable_config_unstamped": ("{not json", {}, ["lineage.bundle_stamp_absent"]),
            "absent_config_unstamped": (None, {}, ["lineage.bundle_stamp_absent"]),
            "untagged_with_a_differing_stamp": ({"run_metadata": {"tags": []}}, {"extra": {
                "launch_lineage": stamp, "launch_lineage_locator_sha256": "0" * 64}},
                ["lineage.bundle_locator_digest_differs", "lineage.bundle_stamp_differs"]),
        }
        for name, (config, metadata, expected) in cases.items():
            with self.subTest(case=name):
                path = bundle(name, config, metadata)
                self.assertEqual(self.audit(bundle_paths=[path]), expected)
                if isinstance(config, dict):  # the writer's own predicate agrees
                    self.assertEqual(window_lineage._bundle_config_untagged(path),
                                     not arm_readiness.launch_lineage_required(config))

    def test_plan_tree_change_is_a_pack_identity_finding(self) -> None:
        tree = self.w.pack / "plan_tree.json"
        tree.write_bytes(tree.read_bytes() + b"\n")
        findings = [finding for finding in window_lineage.audit_window_lineage(
            claim_runs_root=self.w.claim, bound_runs_root=self.w.bound)
            if finding["code"] == "lineage.plan_tree_digest_differs"]
        self.assertEqual(len(findings), 1)
        self.assertEqual((findings[0]["family"], findings[0]["klass"]), ("PACK_IDENTITY", "NUMBER"))
        self.assertEqual(findings[0]["expected"], self.w.lineage["plan_tree_sha256"])

    def test_changed_arm_decision_is_a_finding(self) -> None:
        write_night_records(self.w)
        self.w.arm_decision.write_text('{"decision": "GO", "edited": true}\n')
        self.assertEqual(self.audit(), ["lineage.arm_decision_digest_differs"])

    def test_audit_never_raises_on_missing_records(self) -> None:
        for path in (self.w.claim / window_lineage.LOCATOR_BASENAME,
                     self.w.bound / window_lineage.LOCATOR_BASENAME):
            path.unlink()
        self.assertEqual(self.audit(), ["lineage.locator_unreadable", "lineage.locator_unreadable"])


class UnrecordableValuesTests(_SentinelMixin, unittest.TestCase):
    """Publication-time reads that fail are records findings, never a lost window.

    Review finding (L3 round 1, MAJOR): an untracked pack entry, a git failure
    or an unreadable boot id used to refuse publication, so no chain ran.
    """

    OTHER_BOOT = "00000000-0000-4000-8000-000000000000"

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.w = build_window(Path(tmp.name), publish=False)
        self.addCleanup(self._start_sentinels().close)

    def tearDown(self) -> None:
        self.assertEqual(type(self).sentinel_calls, [], "a hazard path reached the ARM replay")

    def audit(self) -> list[dict]:
        return window_lineage.audit_window_lineage(
            claim_runs_root=self.w.claim, bound_runs_root=self.w.bound)

    def assert_collection_proceeds(self, lineage: dict, **kwargs) -> None:
        w = self.w
        context = arm_readiness.authenticate_campaign_launch_lineage(
            w.claim, config_paths=(w.member_path,), **kwargs)
        self.assertEqual(context["launch_lineage"], lineage)
        config = BenchmarkConfig.from_mapping(json.loads(w.member_path.read_bytes()))
        with patch.object(sys, "argv", ["joulewise", "run", str(w.member_path)]):
            stamped, _digest = bundle_module._writer_launch_lineage(w.claim, config)
        self.assertEqual(stamped, lineage)
        # The kept per-member check still refuses unregistered bytes.
        with self.assertRaises(arm_readiness.LaunchLineageError):
            arm_readiness.authenticate_campaign_launch_lineage(
                w.claim, config_paths=(w.unregistered_path,))
        write_night_records(w)
        self.assertEqual(arm_readiness.authenticate_launch_lineage(
            lineage, require_completion=True)["launch_lineage"], lineage)
        remove_night_records(w)

    def test_untracked_pack_entries_publish_with_the_digest_unrecorded(self) -> None:
        w = self.w
        (w.pack / ".DS_Store").write_bytes(b"\0\0\0\1Bud1")
        (w.pack / "__pycache__").mkdir()
        (w.pack / "__pycache__/generate_configs.cpython-313.pyc").write_bytes(b"\0")
        with self.assertRaisesRegex(arm_readiness.ArmReadinessError, "untracked pack"):
            arm_readiness.committed_pack_tree_sha256(w.pack)
        published = publish_lineage(w)
        lineage = published["launch_lineage"]
        self.assertIsNone(lineage["pack_sha256"])
        self.assertIsNotNone(lineage["collection_boot_session_id"])
        self.assertEqual([item["field"] for item in published["unrecorded"]], ["pack_sha256"])
        self.assertIn("untracked pack", published["unrecorded"][0]["error"])
        self.assert_collection_proceeds(lineage)
        write_night_records(w)
        findings = self.audit()
        self.assertEqual([finding["code"] for finding in findings], ["lineage.pack_digest_unrecorded"])
        self.assertIn("untracked pack", findings[0]["detail"])

    def test_git_failure_publishes_with_the_digest_unrecorded(self) -> None:
        with patch.object(window_lineage, "committed_pack_sha256",
                          side_effect=RuntimeError("git: command not found")):
            published = publish_lineage(self.w)
        self.assertIsNone(published["launch_lineage"]["pack_sha256"])
        self.assert_collection_proceeds(published["launch_lineage"])
        write_night_records(self.w)
        [finding] = self.audit()
        self.assertEqual(finding["code"], "lineage.pack_digest_unrecorded")
        self.assertIn("git: command not found", finding["detail"])

    def _publish_with_unreadable_boot(self, **failure) -> None:
        with patch.object(window_lineage, "current_boot_session_id", **failure):
            published = publish_lineage(self.w)
        lineage = published["launch_lineage"]
        self.assertIsNone(lineage["collection_boot_session_id"])
        self.assertEqual([item["field"] for item in published["unrecorded"]], ["collection_boot_session_id"])
        # Collection on whatever boot it runs in is admitted, through the
        # dispatch (real boot reader) and with a foreign boot.
        self.assert_collection_proceeds(lineage)
        context = window_lineage.authenticate_campaign(
            self.w.claim, config_paths=(self.w.member_path,), boot_reader=lambda: self.OTHER_BOOT)
        self.assertIsNone(context["authentication"]["boot_session_id"])
        write_night_records(self.w)
        self.assertEqual([finding["code"] for finding in self.audit()], ["lineage.collection_boot_unrecorded"])

    def test_unreadable_boot_publishes_and_skips_the_boot_comparison(self) -> None:
        self._publish_with_unreadable_boot(return_value=None)

    def test_raising_boot_reader_publishes_and_skips_the_boot_comparison(self) -> None:
        self._publish_with_unreadable_boot(side_effect=OSError("sysctl unavailable"))

    def test_malformed_supplied_values_are_recorded_null(self) -> None:
        published = window_lineage.publish_window_lineage(
            pack_root=self.w.pack, pack_id=PACK_ID, plan_id=PLAN_ID, window_id=WINDOW_ID,
            bracket_session_id=SESSION_ID, pre_attempt_id=PRE_ATTEMPT, post_attempt_id=POST_ATTEMPT,
            claim_runs_root=self.w.claim, bound_runs_root=self.w.bound, custody_root=self.w.custody,
            pack_sha256="not-a-digest", boot_session_id="not-a-uuid")
        lineage = published["launch_lineage"]
        self.assertIsNone(lineage["pack_sha256"])
        self.assertIsNone(lineage["collection_boot_session_id"])
        self.assertEqual(sorted(item["field"] for item in published["unrecorded"]),
                         ["collection_boot_session_id", "pack_sha256"])
        self.assert_collection_proceeds(lineage)

    def test_supplied_boot_is_recorded_in_canonical_form(self) -> None:
        published = window_lineage.publish_window_lineage(
            pack_root=self.w.pack, pack_id=PACK_ID, plan_id=PLAN_ID, window_id=WINDOW_ID,
            bracket_session_id=SESSION_ID, pre_attempt_id=PRE_ATTEMPT, post_attempt_id=POST_ATTEMPT,
            claim_runs_root=self.w.claim, bound_runs_root=self.w.bound, custody_root=self.w.custody,
            boot_session_id="AAAAAAAA-AAAA-4AAA-8AAA-AAAAAAAAAAAA")
        self.assertEqual(published["launch_lineage"]["collection_boot_session_id"],
                         "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa")
        self.assertEqual(published["unrecorded"], [])

    def test_unreadable_arm_decision_publishes_without_it(self) -> None:
        self.w.arm_decision.unlink()
        published = publish_lineage(self.w)
        go = json.loads(Path(published["records"]["go"]["path"]).read_bytes())
        self.assertIsNone(go["arm_decision"])
        self.assertEqual([item["field"] for item in published["unrecorded"]], ["arm_decision"])
        self.assert_collection_proceeds(published["launch_lineage"])
        write_night_records(self.w)
        self.assertEqual([finding["code"] for finding in self.audit()], ["lineage.arm_decision_unrecorded"])

    def test_null_records_validate_but_malformed_strings_do_not(self) -> None:
        lineage = publish_lineage(self.w)["launch_lineage"]
        for name in ("pack_sha256", "collection_boot_session_id"):
            with self.subTest(field=name):
                nulled = {**lineage, name: None}
                self.assertEqual(arm_readiness.authenticate_launch_lineage(
                    nulled, require_completion=False, require_current_boot=True)["launch_lineage"], nulled)
                with self.assertRaises(arm_readiness.LaunchLineageError) as caught:
                    arm_readiness.authenticate_launch_lineage({**lineage, name: "x"}, require_completion=False)
                self.assertEqual(caught.exception.reason_code, "launch_consumption_invalid")

    def test_publication_still_refuses_unwritable_roots(self) -> None:
        missing = self.w.base / "absent-root"
        with self.assertRaisesRegex(window_lineage.LineagePublicationError, "unavailable"):
            window_lineage.publish_window_lineage(
                pack_root=self.w.pack, pack_id=PACK_ID, plan_id=PLAN_ID, window_id=WINDOW_ID,
                bracket_session_id=SESSION_ID, pre_attempt_id=PRE_ATTEMPT, post_attempt_id=POST_ATTEMPT,
                claim_runs_root=self.w.claim, bound_runs_root=missing, custody_root=self.w.custody)


class CompletionTests(_SentinelMixin, unittest.TestCase):
    """Analysis completion is chain.exited; moved custody is readable.

    Review finding (L3 round 1, MINOR): result.json (written only after the
    G10 tail) was required, and a moved custody root refused every member.
    """

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.w = build_window(Path(tmp.name))
        self.addCleanup(self._start_sentinels().close)
        self.bundle = self.w.claim / "stamped"
        self.bundle.mkdir()
        (self.bundle / "config.json").write_text(json.dumps({"run_metadata": {"tags": [TAG]}}) + "\n")
        (self.bundle / "metadata.json").write_text(json.dumps({"extra": {
            "launch_lineage": self.w.lineage,
            "launch_lineage_locator_sha256": self.w.published["locators"]["claim_runs_root"]["sha256"],
        }}) + "\n")

    def tearDown(self) -> None:
        self.assertEqual(type(self).sentinel_calls, [], "a hazard path reached the ARM replay")

    def audit_codes(self) -> list[str]:
        return sorted(finding["code"] for finding in window_lineage.audit_window_lineage(
            claim_runs_root=self.w.claim, bound_runs_root=self.w.bound))

    def test_chain_exited_alone_completes_the_window(self) -> None:
        self.w.night.mkdir()
        exited = self.w.night / "chain.exited"
        exited.write_text('{"exit_code": 0}\n')
        context = arm_readiness.authenticate_launch_lineage(self.w.lineage, require_completion=True)
        self.assertEqual(context["completion"]["chain_exited"]["path"], str(exited))
        self.assertIsNone(context["completion"]["result"])
        self.assertEqual(context["completion_sha256"], hashlib.sha256(exited.read_bytes()).hexdigest())
        self.assertEqual(arm_readiness.authenticate_bundle_launch_lineage(
            self.bundle, require_completion=True)["launch_lineage"], self.w.lineage)
        # The absent result.json is a records finding.
        self.assertEqual(self.audit_codes(), ["lineage.completion_records_absent"])
        # The completion digest does not move when result.json lands.
        (self.w.night / "result.json").write_text('{"verdict": "GO"}\n')
        later = arm_readiness.authenticate_launch_lineage(self.w.lineage, require_completion=True)
        self.assertEqual(later["completion_sha256"], context["completion_sha256"])
        self.assertIsNotNone(later["completion"]["result"])

    def test_result_alone_does_not_complete_the_window(self) -> None:
        self.w.night.mkdir()
        (self.w.night / "result.json").write_text('{"verdict": "GO"}\n')
        with self.assertRaises(arm_readiness.LaunchLineageError) as caught:
            arm_readiness.authenticate_launch_lineage(self.w.lineage, require_completion=True)
        self.assertEqual(caught.exception.reason_code, "launch_lifecycle_incomplete")

    def test_moved_custody_is_read_through_relocated_custody(self) -> None:
        write_night_records(self.w)
        recorded = self.w.lineage["window_context"]["custody_root"]
        moved = self.w.base / "offloaded/custody"
        moved.parent.mkdir()
        shutil.move(self.w.custody, moved)
        with self.assertRaises(arm_readiness.LaunchLineageError) as caught:
            arm_readiness.authenticate_bundle_launch_lineage(self.bundle, require_completion=True)
        self.assertEqual(caught.exception.reason_code, "launch_lifecycle_incomplete")
        self.assertIn("relocated_custody", str(caught.exception))
        # Without relocation the audit reports the moved records, never raises.
        self.assertEqual(self.audit_codes(),
                         ["lineage.completion_records_absent", "lineage.record_chain_unverified"])
        with window_lineage.relocated_custody({recorded: moved}):
            context = arm_readiness.authenticate_bundle_launch_lineage(self.bundle, require_completion=True)
            self.assertEqual(context["completion"]["chain_exited"]["path"], str(moved / "night/chain.exited"))
            self.assertEqual(context["launch_lineage"], self.w.lineage)
            self.assertEqual(whole_window._authenticated_bundle_launch_lineage_set(
                [self.bundle], require_completion=True), self.w.lineage)
            self.assertEqual(self.audit_codes(), [])
        # The relocation ends with its context.
        with self.assertRaises(arm_readiness.LaunchLineageError):
            arm_readiness.authenticate_launch_lineage(self.w.lineage, require_completion=True)
        with self.assertRaises(ValueError):
            with window_lineage.relocated_custody({"relative/custody": moved}):
                pass


if __name__ == "__main__":
    unittest.main()
