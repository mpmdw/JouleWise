"""D-138 claim hold routes through the real calibration loader."""

from __future__ import annotations

import copy
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from contextlib import ExitStack, redirect_stderr
from types import SimpleNamespace
from unittest.mock import patch

import joulewise.arm_readiness as arm
import joulewise.calibration_bracketing as bracket
from joulewise.calibration_ledger import (
    CalibrationBracketSession, CalibrationLedgerSnapshot, LedgerObservation,
)
from joulewise.schemas import CalibrationBracketingPolicy
from scripts import run_campaign, validate_powermetrics_fiducial as preflight
from scripts import write_derivation_night_inputs as night_inputs


ROOT = Path(__file__).resolve().parents[1]
HELD_PATH = bracket.EPOCH_25G83_R1_ACCEPTANCE_BOUND_PATH


def _hold_table():
    try:
        from joulewise.claim_hold import CLAIM_HELD_OS_BUILDS
        return CLAIM_HELD_OS_BUILDS
    except ImportError:
        return getattr(bracket, "CLAIM_HELD_" + "ACCEPTANCE_IDS", {})


def _hold_for_build(os_build):
    try:
        from joulewise.claim_hold import claim_hold_for_os_build
        return claim_hold_for_os_build(os_build)
    except ImportError:
        return _hold_table().get(bracket.EPOCH_25G83_R1_ACCEPTANCE_ID)


def _held_artifact():
    inspector = getattr(bracket, "inspect_acceptance_without_claim_authority", None)
    artifact = (inspector(HELD_PATH).artifact if inspector is not None
                else json.loads(HELD_PATH.read_bytes()))
    assert artifact is not None
    return artifact


def synthetic_bracket(artifact, identity, count, *, explicit=False):
    """Exercise real evaluation with a ledger built from authenticated prior rows."""
    prior = artifact["prior_observation_set"]
    cutoff = artifact["ledger_cutoff"]
    observations = []
    for sequence, row in enumerate(prior["observations"], 1):
        observations.append(LedgerObservation(
            sequence=sequence,
            receipt_digest=hashlib.sha256(row["attempt_id"].encode()).hexdigest(),
            attempt_id=row["attempt_id"], content_id=row["content_id"],
            artifact_sha256={}, identity_epoch=prior["epoch_catalog"][row["epoch_id"]],
            t1_bindings={}, capture_wall_time_s="1", exact_bound_lexeme_s="0.025",
            disposition=row["disposition"], custody_locator="/tmp/d138-hold-unused",
            observation_kind="live-capture" if row.get("session_id") else "historical-import",
            bracket_session_id=row.get("session_id"),
        ))
    sessions = tuple(CalibrationBracketSession(
        session_id=session_id, window_id=session_id, plan_id=session_id,
        plan_sha256="a" * 64, evidence_root_id="synthetic", runs_root="/tmp",
        capability_receipt_digest="b" * 64, capability_sequence=1,
        slot_attempt_ids={}, state="finalized", finalized_slots={},
        session_kind="derivation",
    ) for session_id in bracket._D102_GENERATION_DERIVATIONS[
        artifact["acceptance_id"]]["registration_session_ids"])
    bindings = {field: "synthetic-" + field for field in bracket.V2_BINDING_FIELDS}
    bindings.update(identity)
    bindings["anchor_method_version"] = bracket.ACTIVE_CAPTURE_ANCHOR_METHOD
    values = [member["b_fiducial_s"] for member in artifact["derivation_corpus"]["members"]]
    candidates = []
    for index in range(count):
        name = f"endpoint-{index}"
        digest = hashlib.sha256(name.encode()).hexdigest()
        wall_time = 99 if index == 0 else 111 if index == 1 else 200 + index
        value = values[index % len(values)]
        candidates.append(bracket.CalibrationCandidate(
            name, digest, digest, bracket.PROTOCOL_ID, wall_time, value,
            bindings, attempt_id=name, content_id=digest, ledger_receipt_digest=digest,
        ))
        observations.append(LedgerObservation(
            sequence=cutoff["sequence"] + index + 1, receipt_digest=digest,
            attempt_id=name, content_id=digest,
            artifact_sha256={"manifest.json": digest, "instrument_evidence.json": digest},
            identity_epoch=identity, t1_bindings=bindings,
            capture_wall_time_s=str(wall_time), exact_bound_lexeme_s=value,
            disposition="valid", custody_locator=f"/tmp/d138-hold-{name}",
        ))
    snapshot = CalibrationLedgerSnapshot(
        ledger_schema=cutoff["ledger_schema"], ledger_path=Path("/tmp/d138-hold-ledger"),
        head_sequence=cutoff["sequence"] + max(count, 1), head_digest="c" * 64,
        receipts=(), observations=tuple(observations), refusal_reasons=(),
        bracket_sessions=sessions, baseline_sequence=cutoff["sequence"],
        baseline_digest=cutoff["head_digest"],
    )
    policy = CalibrationBracketingPolicy(
        require_bracket=True, calibration_bracket_max_drift_s=.010,
    )
    kwargs = {"acceptance_bound": artifact} if explicit else {}
    return bracket.evaluate_calibration_bracket(
        candidates, window_start_s=100, window_end_s=110, bindings=bindings,
        policy=policy, ledger_snapshot=snapshot, **kwargs,
    )


class ClaimHoldRouteTests(unittest.TestCase):
    def setUp(self):
        self.held = _held_artifact()
        self.identity = dict(self.held["identity_epoch"])

    @staticmethod
    def _r7_pack():
        return {"acceptance_policy": {
            "selection": "issued_d116_artifact_only",
            "issued": bracket.ANCHOR_V3_R7_ACCEPTANCE_ID,
        }}

    def test_hr1_r7_pack_capture_preflight_stays_at_r7(self):
        self.assertTrue(arm._issued_d079(self._r7_pack()))
        with self.assertRaises(preflight._AcceptancePreflightError) as caught:
            preflight._derive_preflight_systematic_screen_s(self.identity)
        self.assertEqual(caught.exception.reason, "acceptance_artifact_epoch_mismatch")
        self.assertEqual(caught.exception.context["stale_fields"], ["os_build"])

    def test_hr2_r7_pack_default_bracket_refuses_new_epoch(self):
        self.assertTrue(arm._issued_d079(self._r7_pack()))
        r7 = bracket.load_calibration_acceptance_bound()
        result, reasons = synthetic_bracket(r7, self.identity, 2)
        self.assertEqual(reasons, ("calibration_acceptance_bound_stale",))
        self.assertEqual(result["acceptance"]["artifact"]["acceptance_id"],
                         bracket.ANCHOR_V3_R7_ACCEPTANCE_ID)
        self.assertEqual(result["acceptance"]["freshness"]["stale_fields"], ["os_build"])

    def test_hr3_manual_route_cannot_consume_held_file(self):
        config = ROOT / "configs/campaigns/p2_015_floors/11_neg8_end/p2015-neg8-reference-end.json"
        with patch.object(arm, "_issued_d079", side_effect=AssertionError("admission called")):
            self.assertIsNone(run_campaign.authenticate_campaign_writer_preflight(
                [config], Path("/tmp/d138-hold-runs-unused")))
        with self.assertRaises(preflight._AcceptancePreflightError) as default:
            preflight._derive_preflight_systematic_screen_s(self.identity)
        self.assertEqual(default.exception.reason, "acceptance_artifact_epoch_mismatch")
        with self.assertRaises(preflight._AcceptancePreflightError) as named:
            preflight._derive_preflight_systematic_screen_s(
                self.identity, acceptance_path=HELD_PATH)
        self.assertEqual(named.exception.reason, "acceptance_artifact_unauthenticated")
        self.assertIsNone(bracket.issued_calibration_allowance_projection(
            self.held, pre_exact_bound_lexeme_s="0.030",
            post_exact_bound_lexeme_s="0.036"))
        result, reasons = synthetic_bracket(self.held, self.identity, 2, explicit=True)
        self.assertEqual(reasons, ("calibration_acceptance_bound_stale",))
        self.assertIsNone(result["acceptance"]["artifact"])
        self.assertEqual(result["acceptance"]["freshness"]["reason"],
                         "acceptance_artifact_claim_held")
        self.assertEqual(result["acceptance"]["freshness"]["hold"],
                         _hold_for_build(self.identity["os_build"]))

    def test_hr4_clearing_hold_opens_same_explicit_routes(self):
        with patch.dict(_hold_table(), {}, clear=True):
            self.assertIsNotNone(bracket.load_calibration_acceptance_bound(HELD_PATH))
            self.assertEqual(preflight._derive_preflight_systematic_screen_s(
                self.identity, acceptance_path=HELD_PATH),
                bracket.Decimal("0.038078579302948"))
            self.assertIsNotNone(bracket.issued_calibration_allowance_projection(
                self.held, pre_exact_bound_lexeme_s="0.030",
                post_exact_bound_lexeme_s="0.036"))
            result, reasons = synthetic_bracket(self.held, self.identity, 2, explicit=True)
            self.assertEqual(reasons, ())
            self.assertEqual(result["status"], "passed")

    def test_hr5_loader_never_returns_held_authority(self):
        self.assertIsNone(bracket.load_calibration_acceptance_bound(HELD_PATH))
        inspector = getattr(bracket, "inspect_acceptance_without_claim_authority", None)
        inspected = inspector(HELD_PATH).artifact if inspector else bracket.load_calibration_acceptance_bound(HELD_PATH)
        self.assertEqual(inspected, self.held)
        with patch.dict(_hold_table(), {}, clear=True):
            self.assertEqual(bracket.load_calibration_acceptance_bound(HELD_PATH), self.held)

    def test_hr6_authenticator_refuses_held_bytes(self):
        raw = HELD_PATH.read_bytes()
        self.assertIsNone(bracket._acceptance_bound_from_authenticated_bytes(raw))
        with patch.dict(_hold_table(), {}, clear=True):
            self.assertEqual(bracket._acceptance_bound_from_authenticated_bytes(raw), self.held)

    def test_hr7_held_default_import_refuses(self):
        self.assertEqual(bracket.ACTIVE_ACCEPTANCE_ID, bracket.ANCHOR_V3_R7_ACCEPTANCE_ID)
        self.assertIsNone(bracket.claim_hold_for_acceptance_id(bracket.ACTIVE_ACCEPTANCE_ID))
        source = Path(bracket.__file__).read_text(encoding="utf-8")
        source = source.replace(
            "ACTIVE_ACCEPTANCE_ID = ANCHOR_V3_R7_ACCEPTANCE_ID",
            "ACTIVE_ACCEPTANCE_ID = EPOCH_25G83_R1_ACCEPTANCE_ID",
        )
        with tempfile.TemporaryDirectory() as directory:
            mutant = Path(directory) / "mutant.py"
            mutant.write_text(source, encoding="utf-8")
            code = ("import sys; sys.path.insert(0, %r); "
                    "exec(compile(open(%r).read(), %r, 'exec'), "
                    "{'__name__': 'joulewise.calibration_bracketing', '__file__': %r})"
                    % (str(ROOT), str(mutant), str(mutant), str(bracket.__file__)))
            run = subprocess.run([sys.executable, "-B", "-c", code],
                                 capture_output=True, text=True)
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("the default calibration acceptance is claim-held", run.stderr)

    def test_hr8_derivation_night_remains_open_for_new_epoch(self):
        self.assertEqual(night_inputs._stale_identity_fields(
            self.identity, bracket.DEFAULT_ACCEPTANCE_BOUND_PATH), ["os_build"])

    def test_e2_observed_build_gate_with_file_gate_switched_off(self):
        unchecked = getattr(bracket, "_authenticate_acceptance_bytes",
                            bracket._acceptance_bound_from_authenticated_bytes)
        with patch.object(bracket, "_acceptance_bound_from_authenticated_bytes", unchecked):
            result, reasons = synthetic_bracket(self.held, self.identity, 2, explicit=True)
        self.assertEqual(reasons, ("calibration_acceptance_bound_stale",))
        self.assertEqual(result["acceptance"]["freshness"]["reason"], "observed_epoch_claim_held")
        self.assertFalse(result["acceptance"]["artifact"]["claim_eligible"])
        with patch.dict(_hold_table(), {}, clear=True):
            result, reasons = synthetic_bracket(self.held, self.identity, 2, explicit=True)
        self.assertEqual(reasons, ())
        self.assertEqual(result["status"], "passed")

    def test_e4_nested_mixed_identifier_is_refused(self):
        tree = self._r7_pack()
        tree["acceptance_policy"]["issued_acceptance"] = {
            "acceptance_id": self.held["acceptance_id"], "path": str(HELD_PATH),
        }
        self.assertFalse(arm._issued_d079(tree))
        with patch.dict(_hold_table(), {}, clear=True):
            self.assertFalse(arm._issued_d079(tree))
            del tree["acceptance_policy"]["issued"]
            self.assertTrue(arm._issued_d079(tree))

    def test_e5_flat_mixed_identifier_is_refused(self):
        tree = self._r7_pack()
        tree["acceptance_policy"]["issued_artifact_id"] = self.held["acceptance_id"]
        self.assertFalse(arm._issued_d079(tree))
        with patch.dict(_hold_table(), {}, clear=True):
            self.assertFalse(arm._issued_d079(tree))
            del tree["acceptance_policy"]["issued"]
            self.assertTrue(arm._issued_d079(tree))

    def test_e12_bare_legacy_identifier_is_refused(self):
        # HOLD-BY-CONSTRUCTION-01-A1 §4.4: the bare "d079" names no calibration file, so it has
        # no registered build and is refused. RED at main 9eab16f8, where it was admitted.
        tree = {"acceptance_policy": {"selection": "issued_d116_artifact_only", "issued": "d079"}}
        self.assertFalse(arm._issued_d079(tree))
        hold_for_id = getattr(bracket, "claim_hold_for_acceptance_id", None)
        if hold_for_id is not None:
            from joulewise.claim_hold import UNKNOWN_BUILD_HOLD
            self.assertEqual(hold_for_id("d079"), UNKNOWN_BUILD_HOLD)
        # Control: with a build planted for the bare form it is admitted, so the refusal above
        # is caused by the missing build and nothing else.
        table = getattr(bracket, "REGISTERED_GENERATION_OS_BUILD", None)
        if table is not None:
            with patch.dict(table, {"d079": "25F84"}):
                self.assertTrue(arm._issued_d079(tree))

    def test_e5c_all_nine_committed_packs_stay_admitted(self):
        paths = sorted((ROOT / "configs/campaigns").glob("d117*/plan_tree.json"))
        self.assertEqual(len(paths), 9)
        for path in paths:
            with self.subTest(pack=path.parent.name):
                self.assertTrue(arm._issued_d079(json.loads(path.read_bytes())))
        self.assertTrue(arm._issued_d079(self._r7_pack()))

    def test_e6b_loader_has_no_hold_bypass_keyword(self):
        self.assertIsNone(bracket.load_calibration_acceptance_bound(HELD_PATH))
        with self.assertRaises(TypeError):
            bracket.load_calibration_acceptance_bound(
                HELD_PATH, **{"allow_" + "claim_held": True})
        with patch.dict(_hold_table(), {}, clear=True):
            self.assertEqual(bracket.load_calibration_acceptance_bound(HELD_PATH), self.held)

    def test_e6c_identifier_operatives_are_held(self):
        self.assertIsNone(bracket.acceptance_generation_operatives(self.held["acceptance_id"]))
        self.assertIsNone(bracket.acceptance_bracket_screen_s(self.held["acceptance_id"]))
        with patch.dict(_hold_table(), {}, clear=True):
            self.assertEqual(bracket.acceptance_bracket_screen_s(self.held["acceptance_id"]), "0.013701")

    def test_e6d_later_registered_file_at_held_build_is_refused(self):
        from scripts.issue_calibration_acceptance_generation import derivation_input_sha256, derivation_sha256
        value = copy.deepcopy(self.held)
        new_id = self.held["acceptance_id"].replace("_r1", "_r2")
        value["acceptance_id"] = new_id
        value["derivation_input_sha256"] = derivation_input_sha256(value)
        value["derivation_sha256"] = derivation_sha256(value)
        raw = (json.dumps(value, indent=2, ensure_ascii=True) + "\n").encode()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "new-generation.json"
            path.write_bytes(raw)
            with ExitStack() as stack:
                stack.enter_context(patch.dict(bracket.ISSUED_ACCEPTANCE_REGISTRY, {
                    new_id: {"path": path, "relative_path": "new-generation.json",
                             "file_sha256": hashlib.sha256(raw).hexdigest()},
                }))
                stack.enter_context(patch.dict(bracket._D102_GENERATION_DERIVATIONS, {
                    new_id: bracket._D102_GENERATION_DERIVATIONS[self.held["acceptance_id"]],
                }))
                registered_builds = getattr(bracket, "REGISTERED_GENERATION_OS_BUILD", None)
                if registered_builds is not None:
                    stack.enter_context(patch.dict(registered_builds, {new_id: "25G83"}))
                self.assertIsNone(bracket.load_calibration_acceptance_bound(path))
                self.assertIsNone(bracket._acceptance_bound_from_authenticated_bytes(raw))
                self.assertFalse(arm._issued_d079({"acceptance_policy": {
                    "selection": "issued_d116_artifact_only", "issued": new_id}}))
                with patch.dict(_hold_table(), {}, clear=True):
                    self.assertEqual(bracket.load_calibration_acceptance_bound(path), value)
                    self.assertEqual(bracket._acceptance_bound_from_authenticated_bytes(raw), value)

    def test_e6e_continuation_into_held_build_is_refused(self):
        from joulewise import calibration_epoch_continuation as continuation
        from tests.test_epoch_continuation import EpochContinuationTests, _seal
        case = EpochContinuationTests("runTest")
        case.setUp()
        try:
            payload = case.candidate()
            payload["continued_identity_epoch"]["os_build"] = "25G83"
            _seal(payload)
            with case.issued(payload) as (_, path):
                with self.assertRaisesRegex(continuation.ContinuationRefusal,
                                            "continued_identity_epoch_claim_held"):
                    continuation.authenticate_epoch_continuation(path, case.artifact, None)
                with patch.dict(_hold_table(), {}, clear=True):
                    result = continuation.authenticate_epoch_continuation(path, case.artifact, None)
                self.assertEqual(result.continued_identity_epoch["os_build"], "25G83")
        finally:
            case.doCleanups()

    def test_e7_go_receipt_refuses_claim_on_held_machine(self):
        from tests.test_arm_readiness import LaunchConsumptionV2Tests
        case = LaunchConsumptionV2Tests("runTest")
        case.setUp()
        try:
            inputs = case._consumer_inputs()
            go = inputs["authenticated_go_receipt"]
            manifest = inputs["authenticated_launch_manifest"]
            window = Path(manifest["window_plan_root"])

            def reference(path):
                return {"path": str(path.resolve()),
                        "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}

            kwargs = dict(
                night_plan=inputs["night_plan"], go_receipt=inputs["go_receipt"],
                authenticated_go_receipt=go, go_receipt_sha256=inputs["go_receipt_sha256"],
                arm=case.arm, arm_sha256=inputs["arm_receipt_sha256"],
                custody_pack_root=case.custody / case.pack.name,
                manifest_ref=reference(case.manifest_path),
                env_ref=reference(window / "window.env"),
                chain_ref=reference(window / "window-chain.zsh"),
                step6_confirmation_table=inputs["step6_confirmation_table"],
                expected_confirmation_digest=inputs["expected_confirmation_digest"],
                require_current_boot=True, at_monotonic_ns=go["issued_monotonic_ns"] + 1,
            )
            with patch.object(arm, "machine_os_build", return_value="25G83"):
                fields, _ = arm._authenticate_pack_launch_go(**kwargs)
            self.assertFalse(fields["go_receipt"]["claim_eligible"])

            authorization_path = Path(go["authorization"]["path"])
            authorization = arm.parse_json_bytes(authorization_path.read_bytes())
            authorization.update(purpose="CAMPAIGN_TRANSACTION", claim_eligible=True,
                                 authority="V5-TRANSACTION-GO-01")
            authorization_path.write_bytes(arm.render_json(authorization))
            plan = arm.parse_json_bytes(inputs["night_plan"].read_bytes())
            plan["pack_night"]["authorization_record"] = reference(authorization_path)
            inputs["night_plan"].write_bytes(arm.render_json(plan))
            go["authorization"].update(reference(authorization_path))
            go["authorization"].update(purpose="CAMPAIGN_TRANSACTION", claim_eligible=True)
            go["purpose"] = "CAMPAIGN_TRANSACTION"
            go["plan_sha256"] = reference(inputs["night_plan"])["sha256"]
            for condition in go["conditions"]:
                for evidence in condition["evidence"]:
                    if evidence["path"] == "night/authorization.json":
                        evidence["sha256"] = reference(authorization_path)["sha256"]
            inputs["go_receipt"].write_bytes(arm.render_json(go))
            kwargs["go_receipt_sha256"] = hashlib.sha256(inputs["go_receipt"].read_bytes()).hexdigest()
            for os_build, refused in (("25G83", True), ("25F84", False), (None, True)):
                with self.subTest(os_build=os_build), patch.object(
                    arm, "machine_os_build", return_value=os_build
                ):
                    if refused:
                        with self.assertRaisesRegex(arm.LaunchLineageError, "claim_hold:"):
                            arm._authenticate_pack_launch_go(**kwargs)
                    else:
                        fields, _ = arm._authenticate_pack_launch_go(**kwargs)
                        self.assertTrue(fields["go_receipt"]["claim_eligible"])
            with patch.dict(_hold_table(), {}, clear=True), patch.object(
                arm, "machine_os_build", return_value="25G83"
            ):
                fields, _ = arm._authenticate_pack_launch_go(**kwargs)
                self.assertTrue(fields["go_receipt"]["claim_eligible"])
            with patch.object(arm, "machine_os_build", side_effect=AssertionError("replay read machine")):
                fields, _ = arm._authenticate_pack_launch_go(**{**kwargs, "require_current_boot": False})
                self.assertTrue(fields["go_receipt"]["claim_eligible"])
        finally:
            case.doCleanups()

    def test_e8_manual_campaign_refuses_before_runner(self):
        from joulewise import claim_hold
        args = SimpleNamespace(repair_campaign_provenance=False, check_prompt_hashes=None,
                               record_supersession=None, derive_neg8_drift_bound=None,
                               whole_window_verdict=False, dry_run=False,
                               campaign_policy="unused")
        policy = SimpleNamespace(idle_admission_extension=SimpleNamespace(claim_bearing=True))
        with patch.object(run_campaign, "parse_args", return_value=args), patch.object(
            run_campaign, "load_campaign_policy", return_value=policy
        ), patch.object(claim_hold, "machine_os_build", return_value="25G83"), patch.object(
            run_campaign, "run_campaign", return_value=19
        ) as runner, redirect_stderr(io.StringIO()) as stderr:
            self.assertEqual(run_campaign.main([]), 2)
            runner.assert_not_called()
        self.assertIn("H1-25G83", stderr.getvalue())
        with patch.dict(_hold_table(), {}, clear=True), patch.object(
            run_campaign, "parse_args", return_value=args
        ), patch.object(run_campaign, "load_campaign_policy", return_value=policy), patch.object(
            claim_hold, "machine_os_build", return_value="25G83"
        ), patch.object(run_campaign, "run_campaign", return_value=19) as runner:
            self.assertEqual(run_campaign.main([]), 19)
            runner.assert_called_once()
        with patch.object(run_campaign, "parse_args", return_value=args), patch.object(
            run_campaign, "load_campaign_policy", return_value=policy
        ), patch.object(claim_hold, "machine_os_build", return_value="25F84"), patch.object(
            run_campaign, "run_campaign", return_value=19
        ) as runner:
            self.assertEqual(run_campaign.main([]), 19)
            runner.assert_called_once()

    def test_e9_identity_override_requires_test_sampler(self):
        with redirect_stderr(io.StringIO()) as stderr, self.assertRaises(SystemExit):
            preflight.main(["--identity-epoch-json-for-test", "unused.json",
                            "--custody-budget-s", "-1"])
        self.assertIn("identity epoch test input requires", stderr.getvalue())

    def test_e10_inspection_and_derivation_provenance(self):
        self.assertEqual(night_inputs._stale_identity_fields(
            self.identity, bracket.DEFAULT_ACCEPTANCE_BOUND_PATH), ["os_build"])
        inspection = bracket.inspect_acceptance_without_claim_authority(HELD_PATH)
        self.assertEqual(inspection.artifact, self.held)
        self.assertEqual(inspection.claim_hold, _hold_for_build("25G83"))
        self.assertEqual(inspection.file_sha256, hashlib.sha256(HELD_PATH.read_bytes()).hexdigest())
        with patch.dict(_hold_table(), {}, clear=True):
            self.assertIsNone(bracket.inspect_acceptance_without_claim_authority(HELD_PATH).claim_hold)

    def test_e11_default_path_and_identifier_must_agree(self):
        source = Path(bracket.__file__).read_text(encoding="utf-8")
        source = source.replace(
            "DEFAULT_ACCEPTANCE_BOUND_PATH = ANCHOR_V3_R7_ACCEPTANCE_BOUND_PATH",
            "DEFAULT_ACCEPTANCE_BOUND_PATH = ANCHOR_V3_R6_ACCEPTANCE_BOUND_PATH",
        )
        with tempfile.TemporaryDirectory() as directory:
            mutant = Path(directory) / "mutant.py"
            mutant.write_text(source, encoding="utf-8")
            code = ("import sys; sys.path.insert(0, %r); "
                    "exec(compile(open(%r).read(), %r, 'exec'), "
                    "{'__name__': 'joulewise.calibration_bracketing', '__file__': %r})"
                    % (str(ROOT), str(mutant), str(mutant), str(bracket.__file__)))
            run = subprocess.run([sys.executable, "-B", "-c", code],
                                 capture_output=True, text=True)
        self.assertNotEqual(run.returncode, 0)
        with patch.dict(_hold_table(), {}, clear=True):
            self.assertIsNotNone(bracket.load_calibration_acceptance_bound())


if __name__ == "__main__":
    unittest.main()
