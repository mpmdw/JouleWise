"""Battery evidence on ledger calibration endpoints."""

from __future__ import annotations

from dataclasses import replace
import ast
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import subprocess
import unittest
from unittest.mock import patch

from joulewise import battery_float
import joulewise.calibration_bracketing as bracket
from joulewise.calibration_bracketing import (
    calibration_bracket_for_bundles, discover_calibration_candidates,
    evaluate_calibration_bracket,
)
from joulewise.calibration_ledger import CalibrationLedgerSnapshot, LEDGER_SCHEMA, LedgerObservation
from joulewise.calibration_ledger import content_id_from_artifact_hashes
from joulewise.uncertainty_evidence import ACTIVE_CAPTURE_ANCHOR_METHOD
import tests.test_battery_float as battery_test
import tests.test_calibration_bracketing as legacy


def _battery_exclusion_for_observation(observation):
    return bracket._battery_exclusion_for_observation(observation)


def _battery_classification_for_observation(observation):
    return bracket._battery_classification_for_observation(observation)


def _capture(root: Path, attempt_id: str, *, charging: bool = False,
             battery_key: bool = True, sequence: int = 176):
    root.mkdir(parents=True, exist_ok=True)
    pair = battery_test.PairAuthenticationTests().pair(
        root, pre=battery_test.raw("charging-synthetic-from-real.ioreg") if charging else None
    )
    for phase in ("pre", "post"):
        pair[phase]["phase"] = f"slot_{phase}"
        pair[phase]["session_id"] = None
    evidence = {"validation_id": attempt_id}
    if battery_key:
        evidence["battery_float"] = pair
    evidence_raw = json.dumps(evidence, sort_keys=True).encode()
    (root / "instrument_evidence.json").write_bytes(evidence_raw)
    observation = SimpleNamespace(
        sequence=sequence, custody_locator=str(root), attempt_id=attempt_id,
        artifact_sha256={"instrument_evidence.json": hashlib.sha256(evidence_raw).hexdigest()},
        bracket_session_id=None, bracket_slot=None,
    )
    return observation


class BatteryBracketingTests(unittest.TestCase):
    def test_fixture_flag_has_no_production_true_caller(self) -> None:
        root = Path(__file__).resolve().parents[1]
        tracked = subprocess.check_output(
            ["git", "ls-files", "-z", "joulewise", "scripts"], cwd=root
        ).decode().split("\0")
        for relative in tracked:
            if not relative.endswith(".py"):
                continue
            tree = ast.parse((root / relative).read_text())
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                for keyword in node.keywords:
                    if keyword.arg in {"_allow_unissued_fixture",
                                       "_allow_unissued_calibration_fixture"}:
                        self.assertFalse(isinstance(keyword.value, ast.Constant)
                                         and keyword.value.value is True,
                                         (relative, node.lineno))

    def test_digest_bound_pass_confounded_and_identity(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            good = _capture(Path(tmp) / "good", "good")
            bad = _capture(Path(tmp) / "bad", "bad", charging=True)
            self.assertIsNone(_battery_exclusion_for_observation(good))
            self.assertEqual(_battery_exclusion_for_observation(bad),
                             "battery_float_confounded")
            self.assertEqual(_battery_classification_for_observation(good)[0], "pass")
            other = SimpleNamespace(**{**vars(good), "attempt_id": "different"})
            self.assertEqual(_battery_classification_for_observation(other)[0],
                             "battery_float_evidence_missing")

    def test_deleted_raw_is_custody_and_removed_key_breaks_digest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            observation = _capture(Path(tmp) / "capture", "capture")
            (Path(observation.custody_locator) / "raw/battery_float.post.ioreg").unlink()
            with self.assertRaises(battery_float.CustodyFailure):
                _battery_exclusion_for_observation(observation)
        with tempfile.TemporaryDirectory() as tmp:
            observation = _capture(Path(tmp) / "capture", "capture", sequence=177)
            path = Path(observation.custody_locator) / "instrument_evidence.json"
            evidence = json.loads(path.read_text())
            del evidence["battery_float"]
            path.write_text(json.dumps(evidence))
            with self.assertRaises(battery_float.CustodyFailure):
                _battery_exclusion_for_observation(observation)

    def test_historical_boundary_and_prospective_missing(self) -> None:
        self.assertEqual(bracket.BFGS_HISTORICAL_LEDGER_SEQUENCE, 176)
        self.assertGreater(bracket.BFGS_HISTORICAL_CUTOFF_WALL_S, 0)
        with tempfile.TemporaryDirectory() as tmp:
            old = _capture(Path(tmp) / "old", "old", battery_key=False,
                           sequence=bracket.BFGS_HISTORICAL_LEDGER_SEQUENCE)
            new = _capture(Path(tmp) / "new", "new", battery_key=False,
                           sequence=bracket.BFGS_HISTORICAL_LEDGER_SEQUENCE + 1)
            self.assertEqual(_battery_classification_for_observation(old)[0],
                             "unobserved_historical")
            self.assertIsNone(_battery_exclusion_for_observation(old))
            self.assertEqual(_battery_exclusion_for_observation(new),
                             "battery_float_evidence_missing")

    def test_confounded_ordinary_row_does_not_empty_discovery(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            first = _capture(Path(tmp) / "first", "first", charging=True)
            second = _capture(Path(tmp) / "second", "second")
            observations = tuple(LedgerObservation(
                sequence=index + 177, receipt_digest="a" * 64,
                attempt_id=row.attempt_id, content_id="b" * 64,
                artifact_sha256=row.artifact_sha256, identity_epoch={},
                t1_bindings={"anchor_method_version": ACTIVE_CAPTURE_ANCHOR_METHOD},
                capture_wall_time_s="100", exact_bound_lexeme_s="0.02",
                disposition="valid", custody_locator=row.custody_locator,
            ) for index, row in enumerate((first, second)))
            snapshot = CalibrationLedgerSnapshot(
                ledger_schema=LEDGER_SCHEMA, ledger_path=Path(tmp) / "ledger.jsonl",
                head_sequence=178, head_digest="a" * 64, receipts=(),
                observations=observations, refusal_reasons=(),
            )
            with patch("joulewise.calibration_bracketing._candidate_from_observation",
                       side_effect=lambda observation, **_: observation.attempt_id):
                self.assertEqual(discover_calibration_candidates(snapshot), ("second",))

    def test_confounded_row_is_excluded_from_evaluator_universe(self) -> None:
        fixture = legacy.CalibrationBracketingTests()
        fixture.setUp()
        artifact = legacy._synthetic_issued_artifact()
        baseline = legacy._synthetic_issued_snapshot(artifact)
        with tempfile.TemporaryDirectory() as tmp:
            passing = _capture(Path(tmp) / "passing", "passing")
            charging = _capture(Path(tmp) / "charging", "charging", charging=True)
            rows = []
            for sequence, captured in ((78, passing), (80, charging)):
                hashes = {"manifest.json": hashlib.sha256(captured.attempt_id.encode()).hexdigest(),
                          "instrument_evidence.json": captured.artifact_sha256["instrument_evidence.json"]}
                rows.append(LedgerObservation(
                    sequence=sequence, receipt_digest=hashlib.sha256(str(sequence).encode()).hexdigest(),
                    attempt_id=captured.attempt_id,
                    content_id=content_id_from_artifact_hashes(hashes),
                    artifact_sha256=hashes,
                    identity_epoch=artifact["identity_epoch"],
                    t1_bindings=fixture.bindings,
                    capture_wall_time_s="99", exact_bound_lexeme_s="0.025",
                    disposition="valid", custody_locator=captured.custody_locator,
                ))
            snapshot = replace(baseline, observations=(*baseline.observations, *rows),
                               head_sequence=80, head_digest="e" * 64)
            candidate = replace(fixture.candidate("current-pre", 99.0, "0.025"),
                                relative_path=passing.custody_locator,
                                manifest_sha256=rows[0].artifact_sha256["manifest.json"],
                                evidence_sha256=rows[0].artifact_sha256["instrument_evidence.json"],
                                attempt_id="passing", content_id=rows[0].content_id,
                                ledger_receipt_digest=rows[0].receipt_digest)
            with patch("joulewise.calibration_bracketing._candidate_from_observation",
                       return_value=candidate):
                self.assertEqual(discover_calibration_candidates(snapshot), (candidate,))
            with patch("joulewise.calibration_bracketing.load_calibration_acceptance_bound",
                       return_value=artifact):
                result, reasons = evaluate_calibration_bracket(
                    (candidate,), window_start_s=100.0, window_end_s=110.0,
                    bindings=fixture.bindings, policy=fixture.policy,
                    ledger_snapshot=snapshot,
                )
            self.assertNotIn("calibration_ledger_off_ledger_artifact", reasons)
            self.assertEqual([row["attempt_id"] for row in result["battery_excluded_endpoints"]],
                             ["charging"])
            reader = SimpleNamespace(
                measured_window=lambda: SimpleNamespace(start_s=100.0, end_s=110.0),
                metadata=lambda: {"instrument_calibration": {"bindings": fixture.bindings}},
            )
            with (patch("joulewise.calibration_bracketing.BundleReader", return_value=reader),
                  patch("joulewise.calibration_bracketing._candidate_from_observation",
                        return_value=candidate),
                  patch("joulewise.calibration_bracketing.load_calibration_acceptance_bound",
                        return_value=artifact)):
                _wrapped, wrapped_reasons = calibration_bracket_for_bundles(
                    Path(tmp), [Path(tmp) / "bundle"], fixture.policy,
                    ledger_snapshot=snapshot,
                )
            self.assertNotIn("calibration_ledger_custody_invalid", wrapped_reasons)

    def test_evaluator_reauthenticates_and_refuses_disagreement(self) -> None:
        fixture = legacy.CalibrationBracketingTests()
        fixture.setUp()
        with tempfile.TemporaryDirectory() as tmp:
            paths = [Path(tmp) / name for name in ("pre", "post")]
            observations = [_capture(path, name) for path, name in zip(paths, ("pre", "post"))]
            candidates = [replace(fixture.candidate(name, stamp, "0.025"),
                                  relative_path=str(path), attempt_id=name,
                                  evidence_sha256=observation.artifact_sha256["instrument_evidence.json"])
                          for name, stamp, path, observation in zip(
                              ("pre", "post"), (99.0, 111.0), paths, observations)]
            snapshot, normalized = legacy._fixture_snapshot(candidates)
            def classify(observation, *, custody=None):
                return (("battery_float_confounded", (), None, None)
                        if custody is not None else ("pass", (), None, None))
            with patch("joulewise.calibration_bracketing._battery_classification_for_observation",
                       side_effect=classify):
                _result, reasons = legacy._evaluate_with_unissued_acceptance(
                    normalized, window_start_s=100.0, window_end_s=110.0,
                    bindings=fixture.bindings, policy=fixture.policy,
                    ledger_snapshot=snapshot, _allow_unissued_fixture=True,
                )
            self.assertEqual(reasons, ("calibration_battery_float_disagreement",))

    def test_late_window_cannot_use_historical_endpoint(self) -> None:
        fixture = legacy.CalibrationBracketingTests()
        fixture.setUp()
        cutoff = bracket.BFGS_HISTORICAL_CUTOFF_WALL_S
        with tempfile.TemporaryDirectory() as tmp:
            paths = [Path(tmp) / name for name in ("pre", "post")]
            observations = [_capture(path, name, battery_key=False)
                            for path, name in zip(paths, ("pre", "post"))]
            candidates = [replace(fixture.candidate(name, stamp, "0.025"),
                                  relative_path=str(path), attempt_id=name,
                                  evidence_sha256=observation.artifact_sha256["instrument_evidence.json"])
                          for name, stamp, path, observation in zip(
                              ("pre", "post"), (cutoff - 2.0, cutoff + 3.0),
                              paths, observations)]
            snapshot, normalized = legacy._fixture_snapshot(candidates)
            _result, reasons = legacy._evaluate_with_unissued_acceptance(
                normalized, window_start_s=cutoff - 1.0, window_end_s=cutoff + 1.0,
                bindings=fixture.bindings, policy=fixture.policy,
                ledger_snapshot=snapshot, _allow_unissued_fixture=True,
            )
            self.assertEqual(reasons, ("calibration_battery_float_evidence_missing",))


if __name__ == "__main__":
    unittest.main()
