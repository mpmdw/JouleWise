"""D-138 claim hold routes through the real calibration loader."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
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


def _held_artifact():
    # Governance tests state a non-claim purpose. Production callers never do.
    kwargs = ({"allow_claim_held": True}
              if hasattr(bracket, "CLAIM_HELD_ACCEPTANCE_IDS") else {})
    artifact = bracket.load_calibration_acceptance_bound(
        HELD_PATH, **kwargs,
    )
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
                         bracket.CLAIM_HELD_ACCEPTANCE_IDS[self.held["acceptance_id"]])

    def test_hr4_clearing_hold_opens_same_explicit_routes(self):
        with patch.dict(bracket.CLAIM_HELD_ACCEPTANCE_IDS, {}, clear=True):
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

    def test_hr5_loader_opt_in_is_explicit(self):
        self.assertIsNone(bracket.load_calibration_acceptance_bound(HELD_PATH))
        self.assertEqual(bracket.load_calibration_acceptance_bound(
            HELD_PATH, allow_claim_held=True), self.held)

    def test_hr6_no_production_call_opts_in(self):
        # AST checks call sites, avoiding the loader's own explanatory docstring.
        callers = []
        for base in (ROOT / "joulewise", ROOT / "scripts"):
            for path in base.rglob("*.py"):
                tree = ast.parse(path.read_text(encoding="utf-8"))
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call) and any(
                        keyword.arg == "allow_claim_held" and isinstance(keyword.value, ast.Constant)
                        and keyword.value.value is True for keyword in node.keywords
                    ):
                        callers.append(path.relative_to(ROOT).as_posix())
        self.assertEqual(callers, [])

    def test_hr7_held_default_import_refuses(self):
        self.assertEqual(bracket.ACTIVE_ACCEPTANCE_ID, bracket.ANCHOR_V3_R7_ACCEPTANCE_ID)
        self.assertNotIn(bracket.ACTIVE_ACCEPTANCE_ID, bracket.CLAIM_HELD_ACCEPTANCE_IDS)
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


if __name__ == "__main__":
    unittest.main()
