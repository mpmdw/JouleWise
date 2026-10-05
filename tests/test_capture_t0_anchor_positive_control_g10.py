"""Native custody replay checks for measured-offset G10 scheduling."""
import unittest

from joulewise import arm_readiness as readiness
from scripts.ed_session import capture_t0_anchor_positive_control as g10
from tests.test_capture_t0_anchor_positive_control import ControlFixture


class PreflightCustodyTests(unittest.TestCase):
    def test_tampered_measurement_fails_even_after_manifest_is_resealed(self):
        fixture = ControlFixture(self)
        self.assertEqual(fixture.run()["status"], "DISCHARGED")
        path = fixture.case.control / "preflight.json"
        value = g10.read_json(path)
        value["midpoint_s"] = "0.021"
        path.write_bytes(readiness.render_json(value))
        with self.assertRaisesRegex(ValueError, "g10_custody_hash_or_census"):
            fixture.verify()
        fixture.reseal()
        with self.assertRaisesRegex(ValueError, "g10_preflight_measurement"):
            fixture.verify()

    def test_preflight_argv_streams_and_stamps_are_replayed(self):
        for defect in ("argv", "stream", "stamp"):
            with self.subTest(defect=defect):
                fixture = ControlFixture(self)
                self.assertEqual(fixture.run()["status"], "DISCHARGED")
                root = fixture.case.control
                path = root / "commands/preflight.json"
                value = g10.read_json(path)
                if defect == "argv":
                    value["argv"].append("--invented")
                    path.write_bytes(readiness.render_json(value))
                elif defect == "stream":
                    (root / "commands/preflight/stderr.txt").write_text("tampered\n")
                else:
                    value["finished"]["boot_id"] = "another-boot"
                    path.write_bytes(readiness.render_json(value))
                fixture.reseal()
                with self.assertRaises(ValueError):
                    fixture.verify()

    def test_offset_reparsed_from_raw_sntp_even_with_self_consistent_manifest(self):
        fixture = ControlFixture(self)
        self.assertEqual(fixture.run()["status"], "DISCHARGED")
        path = fixture.case.control / "commands/preflight.json"
        value = g10.read_json(path)
        report = readiness.parse_json_bytes(value["stdout"].encode())
        for sample in report["samples"]:
            sample["stdout"] = sample["stdout"].replace("0.020 +/-", "0.019 +/-")
            sample["raw_line"] = sample["raw_line"].replace("0.020 +/-", "0.019 +/-")
            sample["offset_s"] = 0.019
        value["stdout"] = readiness.render_json(report).decode()
        path.write_bytes(readiness.render_json(value))
        (fixture.case.control / "commands/preflight/stdout.txt").write_bytes(value["stdout"].encode())
        fixture.reseal()
        with self.assertRaisesRegex(ValueError, "g10_preflight_measurement"):
            fixture.verify()


if __name__ == "__main__":
    unittest.main()
