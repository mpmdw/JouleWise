"""Cold ruling ACCEPTANCE-25G83-01, Revision 4 desk regressions."""

from __future__ import annotations

from contextlib import redirect_stdout
from decimal import Decimal
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from joulewise.bundle_read import TracePoint, Window
from joulewise.powermetrics_fiducial import (
    CommandedPulse,
    PROTOCOL_ID,
    PROTOCOL_V3_ID,
    TraceInterval,
    authenticate_protocol_schedule,
    protocol_definition,
    protocol_definition_matches,
    pulse_schedule,
)
from joulewise.reduce import _native_frame_cadence_flag
from scripts import issue_calibration_acceptance_generation as issuer
from tests.fixtures.epoch_bootstrap.build import (
    Slot, TARGET_EPOCH, T1_BINDINGS, build_derivation_ledger,
)


ROOT = Path(__file__).resolve().parents[1]
PREREG = ROOT / "configs/calibration/preregistration_d079_epoch_25g83_rev1.md"
R6 = ROOT / "configs/calibration/calibration_acceptance_d079_v2_n17_r6.json"


class ProtocolV4Tests(unittest.TestCase):
    def test_v4_geometry_and_historical_v3(self) -> None:
        v4 = json.loads((ROOT / "configs/calibration/powermetrics_fiducial/protocol_v4.json").read_text())
        v3 = json.loads((ROOT / "configs/calibration/powermetrics_fiducial/protocol_v3.json").read_text())
        self.assertTrue(protocol_definition_matches(v4))
        self.assertTrue(protocol_definition_matches(v3))
        self.assertEqual(protocol_definition(PROTOCOL_V3_ID)["pulse_duration_s"], 1.0)
        self.assertEqual(protocol_definition(PROTOCOL_ID)["pulse_duration_s"], 2.0)
        historical = [CommandedPulse(on_s=on, off_s=off)
                      for on, off in pulse_schedule(2, start_s=5.0, duration_s=1.0)]
        authenticate_protocol_schedule(
            historical,
            [TraceInterval(start_s=0, end_s=historical[-1].off_s + 5, power_w=20)],
            PROTOCOL_V3_ID,
        )
        pulses = [CommandedPulse(on_s=on, off_s=off) for on, off in pulse_schedule(2, start_s=5.0)]
        end_s = pulses[-1].off_s + 5.0
        frames = [TraceInterval(start_s=i * 0.419, end_s=(i + 1) * 0.419, power_w=20.0)
                  for i in range(int(end_s / 0.419) + 1)]
        authenticate_protocol_schedule(pulses, frames, PROTOCOL_ID)
        for pulse in pulses:
            self.assertTrue(any(frame.start_s >= pulse.on_s + 0.25
                                and frame.end_s <= pulse.off_s - 0.25
                                for frame in frames))
        for duration in (1.799, 2.201):
            bad = [CommandedPulse(on_s=5.0, off_s=5.0 + duration)]
            with self.assertRaisesRegex(ValueError, "pulse duration disagrees"):
                authenticate_protocol_schedule(bad, frames, PROTOCOL_ID)

    def test_native_cadence_flag_never_refuses(self) -> None:
        curve = [TracePoint(t=0.4, power_w=10, support_start_s=0, support_end_s=0.4),
                 TracePoint(t=0.8, power_w=10, support_start_s=0.4, support_end_s=0.8),
                 TracePoint(t=1.6, power_w=10, support_start_s=0.8, support_end_s=1.6)]
        result = _native_frame_cadence_flag(curve, Window(0, 1.6),
                                            {"median_s": 0.245, "max_s": 0.419})
        self.assertAlmostEqual(result["measured_interior_median_s"], 0.4)
        self.assertAlmostEqual(result["measured_interior_max_s"], 0.8)
        self.assertTrue(result["median_exceeds_corpus"])
        self.assertTrue(result["max_exceeds_corpus"])
        self.assertTrue(result["a243_trigger_flag"])


class RevisionFourIssuerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.predecessor = json.loads(R6.read_text())
        self.epoch = {**TARGET_EPOCH, "pulse_protocol_id": PROTOCOL_ID}
        self.t1 = {**T1_BINDINGS, "pulse_protocol_id": PROTOCOL_ID}

    def issue(self, values: list[str], *, minimum: int | None = None,
              historical_shape_ruling: bool = False) -> tuple[int, str, dict | None]:
        slots = [Slot(value) for value in values]
        slots += [Slot("0.020", disposition="ordinary-invalid") for _ in range(12 - len(slots))]
        fixture = build_derivation_ledger(
            self.root / "ledger", slots, session_id="w1",
            second_session=("w2", [Slot("0.020", disposition="ordinary-invalid") for _ in range(12)]),
            session_epoch=self.epoch, second_session_epoch=self.epoch,
            t1_bindings=self.t1,
        )
        out = self.root / "candidate.json"
        argv = [
            "prepare-candidate", "--ledger", str(fixture["ledger"]),
            "--head-pin", str(fixture["pin"]), "--repo-root", str(fixture["root"]),
            "--preregistration", str(PREREG), "--predecessor-acceptance", str(R6),
            "--registration-session-id", "w1", "--registration-session-id", "w2",
            "--preregistration-sha256", hashlib.sha256(PREREG.read_bytes()).hexdigest(),
            "--d125-ruling", "D-125 2026-09-24 addendum", "--out", str(out),
        ]
        if minimum is not None:
            argv += ["--minimum-corpus-size", str(minimum)]
        if historical_shape_ruling:
            argv += ["--nights-ruling", "synthetic historical shape"]
        printed = io.StringIO()
        # The r8 pin transaction is a later seat; isolate the issuer's new
        # rules from the old artifact's expected code hash in this desk test.
        with mock.patch.object(issuer, "_authenticated_predecessor", return_value=self.predecessor), \
             mock.patch.object(issuer, "_derivation_frame_cadence",
                               return_value={"median_s": 0.245, "max_s": 0.419}), \
             redirect_stdout(printed):
            rc = issuer.main(argv)
        return rc, printed.getvalue(), json.loads(out.read_text()) if out.exists() else None

    def test_n12_zero_headroom_issues_and_n11_refuses(self) -> None:
        rc, _, payload = self.issue(["0.020"] * 12)
        self.assertEqual(rc, 0)
        assert payload is not None
        outcomes = payload["derivation_notes"]["rule_outcomes"]
        self.assertEqual(outcomes["minimum_corpus_size"], 12)
        self.assertEqual(outcomes["headroom_status"], "zero_headroom")
        self.assertEqual(Decimal(payload["registered_generation_row"]["operatives"]["max_budgetable_excess_s"]), 0)
        self.assertEqual(payload["derivation_notes"]["native_frame_cadence_s"]["max_s"], 0.419)
        # A separate fixture root is needed because each builder creates Git.
        self.root = self.root / "next"
        self.root.mkdir()
        rc, printed, payload = self.issue(["0.020"] * 11)
        self.assertEqual(rc, 3)
        self.assertIn("below the required floor 12", printed)
        self.assertIsNone(payload)

    def test_excursion_label_and_over_interval_refusal(self) -> None:
        rc, _, payload = self.issue(["0.020"] * 10 + ["0.100", "0.110"])
        self.assertEqual(rc, 0)
        assert payload is not None
        outcomes = payload["derivation_notes"]["rule_outcomes"]
        self.assertEqual(outcomes["excursion_member_count"], 2)
        self.assertEqual(outcomes["excursion_label"], "excursion_limited")
        self.assertEqual(outcomes["screen_challenge_member_count"], 2)
        self.root = self.root / "next"
        self.root.mkdir()
        rc, printed, payload = self.issue(["0.020"] * 11 + ["0.251"])
        self.assertEqual(rc, 3)
        self.assertIn("exceeds one native sample interval", printed)
        self.assertIsNone(payload)

    def test_twelve_does_not_issue_under_historical_v3_epoch(self) -> None:
        self.epoch = TARGET_EPOCH
        self.t1 = T1_BINDINGS
        rc, printed, payload = self.issue(["0.020"] * 12,
                                          historical_shape_ruling=True)
        self.assertEqual(rc, 3)
        self.assertIn("below the required floor 19", printed)
        self.assertIsNone(payload)


if __name__ == "__main__":
    unittest.main()
