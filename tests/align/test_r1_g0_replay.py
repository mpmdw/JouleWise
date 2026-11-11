"""2026-11-10 ruling: production wait replay and accepted R_op custody."""
import json
import io
from pathlib import Path
import tempfile
import unittest

from joulewise.align.apple import r1_runtime as rt
from scripts import replay_r1_g0 as replay
from tests.align import r1_synthetic as rs


class ReplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(replay.FIXTURE.read_text())
        cls.result = replay.replay(cls.data)

    def test_actual_record_and_model_b_use_the_production_wait(self):
        result = self.result
        self.assertEqual(result["old"]["outcome"], "timeout")
        # Agreement bar from the build brief, in seconds. The observed
        # record overshoots its 600 s cap by less than one 1 Hz poll.
        self.assertAlmostEqual(result["old"]["duration_s"], 600, delta=1e-6)
        self.assertLess(abs(result["recorded_wait_s"] - result["old"]["duration_s"]), 1)
        self.assertEqual(result["new_observed"]["outcome"], "record_ended_unreleased")
        self.assertEqual(result["new_model_b"]["outcome"], "released")
        # These are the recorded span and the ruled cap, not fitted bars.
        self.assertGreater(result["new_model_b"]["duration_s"], 600)
        self.assertLess(result["new_model_b"]["duration_s"], 1200)
        self.assertLessEqual(abs(result["new_model_b"]["slope_c_per_min"]), .2)  # registered slope bar
        self.assertLessEqual(result["new_model_b"]["release"]["slow_c"], result["R_op"]["slow_c"] + 1.5)

    def test_capture_and_fixture_projection_retain_the_recorded_precision(self):
        # Full-precision medians of the source record; 1e-6 C agreement bar
        # is the build brief's absolute column tolerance.
        self.assertAlmostEqual(self.result["R_op"]["slow_c"], 26.571249961853027, delta=1e-6)
        self.assertAlmostEqual(self.result["R_op"]["fast_c"], 34.106462478637695, delta=1e-6)
        # Ruling prints model-B slow RMSE at .001 C precision, hence .0005 C.
        self.assertAlmostEqual(self.result["model_b"]["slow_c"]["rmse_c"], .076, delta=.0005)
        self.assertLessEqual(replay.FIXTURE.stat().st_size, 200_000)  # brief fixture cap, bytes


class AcceptedReferenceTests(unittest.TestCase):
    def segment(self, root):
        segment = rt.Segment.__new__(rt.Segment)
        segment.kind, segment.out = "g0-release-soak", root / "release"
        segment.config = {"sensors": {"s_fast": "TV0h", "s_slow": "Tf08", "fan_keys": [], "r0_sha256": "a"*64}}
        segment.soak = {"sensors_c": {"TV0h": 34., "Tf08": 25.},
                        "detrended": {k: {"detrended_sd_c": .078} for k in ("TV0h", "Tf08")}}
        return segment

    def test_before_acceptance_rejected_attempt_is_ignored_then_custody_binds_r_op(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            segment = self.segment(root)
            rejected = root / "step_30b.rejected1"
            rejected.mkdir()
            (rejected / rt.RESULT_NAME).write_text('{}')
            self.assertEqual(segment.reference()["source_member"], "r1_soak_reference")
            op = {"source_member": rt.OPERATING_REFERENCE_SOURCE, "fast_c": 34.1, "slow_c": 26.5,
                  "span_ns": [0, 60 * rt.NS]}
            source = root / rt.STEP_30B_SEGMENT
            source.mkdir()
            result = source / rt.RESULT_NAME
            result.write_text(json.dumps({"kind": "step-30b", "operating_reference": op}))
            rt.write_custody(source, {"status": "complete"})
            self.assertEqual(segment.reference(), op)  # identical JSON inputs
            result.write_text(json.dumps({"kind": "step-30b", "operating_reference": {**op, "slow_c": 30.}}))
            with self.assertRaisesRegex(rt.Refused, "complete runtime custody"):
                segment.reference()

    def test_s5_formula_stays_and_s6_band_keeps_the_soak_spread(self):
        with tempfile.TemporaryDirectory() as td:
            segment = self.segment(Path(td))
            s5 = rt.bands_c(segment.soak, segment.sensors, slow_floor=rt.BAND_FLOOR_C)
            bands = segment.bands()
            # 3 x .078 C = .234 C below both registered floors.
            self.assertAlmostEqual(s5["delta_slow_c"], 1., delta=1e-6)
            self.assertAlmostEqual(bands["delta_slow_c"], 1.5, delta=1e-6)
            self.assertAlmostEqual(bands["delta_fast_c"], 1., delta=1e-6)
            segment.soak["detrended"]["Tf08"]["detrended_sd_c"] = .6
            self.assertAlmostEqual(segment.bands()["delta_slow_c"], 3 * .6, delta=1e-6)

    def test_unobserved_step_30b_capture_still_makes_the_member_incomplete(self):
        class MissingCaptureBackend(rs.SyntheticBackend):
            def run_member(self, config_map, runs_root, hook):
                def missing(session):
                    hook(session)
                    original = session.capture_reference

                    def capture(member):
                        # A collector gap covering the entire WP14(b) window
                        # has zero coverage, below the registered 0.9 minimum.
                        session.sidecar.readings.clear()
                        return original(member)
                    session.capture_reference = capture
                return super().run_member(config_map, runs_root, missing)

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            config = rs.synthetic_config(root / "cfg")
            soak = self.segment(root).soak
            soak["schema"] = rt.SOAK_REFERENCE_SCHEMA
            # Use the synthetic world's selected keys.
            soak["sensors_c"] = {rs.syn.FAST: 38., rs.syn.SLOW: 38.}
            soak["detrended"] = {k: {"detrended_sd_c": .078} for k in soak["sensors_c"]}
            source = root / "soak.json"
            source.write_text(json.dumps(soak))
            output = root / "step_30b"
            rc = rt.main(["--config", str(config), "--output", str(output), "--r1-kind", "step-30b",
                          "--soak-reference", str(source)], stdout=io.StringIO(),
                         backend_factory=MissingCaptureBackend)
            self.assertEqual(rc, rt.EXIT_FAILED)
            terminal = json.loads((output / rt.CUSTODY_NAME).read_text())
            self.assertIn("thermal.state_unobserved", terminal["error"])
            self.assertFalse((output / rt.RESULT_NAME).exists())


if __name__ == "__main__":
    unittest.main()
