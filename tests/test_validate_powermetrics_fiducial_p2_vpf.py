"""Gate prune 2, lane P2-VPF, in the fiducial writer.

S5 (finding t3-10): on a HAZARD window each slot parses its plist once, and
in place of the skipped historical custody pass (A6-R2/R3) a slot verifies
custody of its own session's finalized rows (the post slot: the pre capture),
as a record.  Sol F2: the HAZARD writer authenticates continued epochs past a
stale head pin.  The legacy path (no HAZARD locator) is unchanged.

The slot tests run the real writer CLI in the calibration witness sandbox, as
tests/test_validate_powermetrics_fiducial_hazard.py does.
"""

from __future__ import annotations

import contextlib
import gzip
import io
import json
import math
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from joulewise.adapters.powermetrics import parse_powermetrics_records, samples_from_records
from joulewise.calibration_exits import RefusalCode
from scripts import validate_powermetrics_fiducial as writer
from tests import test_calibration_exits as exits
from tests import test_validate_powermetrics_fiducial_hazard as hazard_tests

REPO_ROOT = Path(__file__).resolve().parents[1]
PLIST_FIXTURES = (
    "tests/fixtures/d078_r01/raw/powermetrics.plist",
    "tests/fixtures/d117_v2_production/strict_seed_bundle/raw/powermetrics.plist",
    "tests/fixtures/d117_v2_production/strict_seed_bundle/raw/powermetrics_idle.plist",
    "tests/fixtures/controller_g2b/block3-pre/raw/powermetrics.plist.gz",
    "tests/fixtures/powermetrics_sample.plist",
)


def tearDownModule() -> None:
    exits.assert_no_owned_fake_sampler_survivors()


def _plist(relative: str) -> bytes:
    raw = (REPO_ROOT / relative).read_bytes()
    return gzip.decompress(raw) if relative.endswith(".gz") else raw


def _trace(records) -> str:
    # The writer's power_trace.csv rows (repr of every float).
    return "".join(
        f"{sample.timestamp_s!r},{sample.power_w!r},{sample.source},"
        f"{sample.rail},{sample.interval_start_s!r},{sample.interval_end_s!r}\n"
        for sample in samples_from_records(records))


class ParseOnceTests(unittest.TestCase):
    """The re-anchored records equal a second, anchored parse of the same bytes."""

    def test_reanchored_records_equal_the_anchored_parse_on_every_fixture(self):
        for relative in PLIST_FIXTURES:
            with self.subTest(relative):
                data = _plist(relative)
                native = parse_powermetrics_records(data)
                self.assertGreater(len(native), 1)
                for endpoint in (native[0].metadata["plist_first_timestamp_s"] + 0.123456789,
                                 1_791_249_487.0371, 0.0):
                    parsed = parse_powermetrics_records(data, first_record_endpoint_s=endpoint)
                    reanchored = writer._anchored_from_native_records(native, endpoint)
                    self.assertEqual(reanchored, parsed)
                    self.assertEqual([record.timestamp_s.hex() for record in reanchored],
                                     [record.timestamp_s.hex() for record in parsed])
                    self.assertEqual(_trace(reanchored), _trace(parsed))

    def test_the_native_records_are_not_mutated(self):
        data = _plist(PLIST_FIXTURES[0])
        native = parse_powermetrics_records(data)
        before = parse_powermetrics_records(data)
        reanchored = writer._anchored_from_native_records(native, 12.5)
        reanchored[0].metadata["x"] = 1
        reanchored[0].rail_power_w["cpu_power"] = -1.0
        self.assertEqual(native, before)

    def test_a_non_finite_endpoint_refuses_like_the_parse(self):
        native = parse_powermetrics_records(_plist(PLIST_FIXTURES[0]))
        for endpoint in (math.nan, math.inf):
            with self.subTest(endpoint):
                with self.assertRaises(ValueError):
                    writer._anchored_from_native_records(native, endpoint)


class SessionCustodyTests(hazard_tests._SandboxCase):
    """The post slot re-hashes the pre capture of its own session (HAZARD only)."""

    def _pre(self, state: dict) -> None:
        completed = self.rig.run_writer(state, slot="pre")
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)

    def _tamper_pre(self, state: dict) -> None:
        events = Path(state["custody_locator"]) / "events.jsonl"
        events.write_bytes(events.read_bytes() + b"\n")

    def test_tampered_pre_capture_is_flagged_by_the_hazard_post_slot(self):
        state = self.rig.real_writer_state("session-p2-tamper")
        self.rig.hazard(state)
        self._pre(state)
        self.assertEqual(self.rig.flags_of_kind(state, "session_custody_unverified"), [])
        self._tamper_pre(state)
        completed = self.rig.run_writer(state, slot="post")
        # A record, never a refusal: the post capture still runs.
        self.assertIn(completed.returncode, (0, 1), completed.stdout + completed.stderr)
        self.assertTrue((Path(state["output_root"]) / "session-p2-tamper-post"
                         / "manifest.json").is_file())
        flags = self.rig.flags_of_kind(state, "session_custody_unverified")
        self.assertEqual(len(flags), 1, self.rig.flags(state))
        self.assert_window_flag(flags[0], "calibration.writer_record_flagged")
        observed = flags[0]["observed"]
        self.assertEqual(observed["status"], "mismatch")
        self.assertEqual(observed["slot"], "post")
        self.assertEqual(observed["session_id"], "session-p2-tamper")
        self.assertEqual(observed["attempt_ids"], ["session-p2-tamper-pre"])
        self.assertEqual(observed["reasons"], ["calibration_ledger_custody_invalid"])

    def test_a_clean_session_emits_no_session_custody_flag(self):
        state = self.rig.real_writer_state("session-p2-clean")
        self.rig.hazard(state)
        self._pre(state)
        completed = self.rig.run_writer(state, slot="post")
        self.assertIn(completed.returncode, (0, 1), completed.stdout + completed.stderr)
        self.assertEqual(self.rig.flags_of_kind(state, "session_custody_unverified"), [])

    def test_legacy_post_slot_still_refuses_a_tampered_pre_capture(self):
        # Legacy keeps its full historical pass, which covers the pre row.
        state = self.rig.real_writer_state("session-p2-legacy")
        self._pre(state)
        self._tamper_pre(state)
        completed = self.rig.run_writer(state, slot="post")
        self.assertEqual(completed.returncode, 2, completed.stdout + completed.stderr)
        self.assertEqual(self.rig.flags(state), [])


class StalePinWiringTests(unittest.TestCase):
    """main() passes allow_stale_pin to the acceptance preflight on HAZARD only."""

    def _run(self, *, hazard: bool, derivation_only: bool = False) -> dict:
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        runs = root / "runs"
        output_root = runs / "instrument_validation"
        output_root.mkdir(parents=True)
        custody = root / "custody"
        custody.mkdir()
        if hazard:
            (custody / "night_plan.json").write_text(json.dumps(
                {"plan_id": "p", "hazard_window": {"attempt": 1}}), encoding="utf-8")
            (runs / hazard_tests.LOCATOR_BASENAME).write_text(json.dumps({
                "schema_version": hazard_tests.HAZARD_LOCATOR_SCHEMA,
                "launch_lineage": {"window_context": {"custody_root": str(custody)}},
            }), encoding="utf-8")
        identity = root / "identity.json"
        identity.write_text(json.dumps({"os_build": "25G83", "hardware_model": "Mac15,9"}),
                            encoding="utf-8")
        captured: dict = {}

        def stop(*args, **kwargs):
            captured.update(kwargs)
            raise writer._AcceptancePreflightError("wiring_probe")

        argv = ["--allow-live", "--power-policy", "ac_high_power",
                "--ledger", str(root / "ledger.jsonl"), "--head-pin", str(root / "pin.json"),
                "--output-root", str(output_root), "--sampler-direct-for-test",
                "--identity-epoch-json-for-test", str(identity),
                *(["--derivation-only"] if derivation_only else [])]
        target = ("_derivation_only_screen_basis" if derivation_only
                  else "_derive_preflight_systematic_screen_s")
        with mock.patch.object(writer, target, side_effect=stop), \
                contextlib.redirect_stderr(io.StringIO()) as stderr:
            rc = writer.main(argv)
        self.assertEqual(rc, 2, stderr.getvalue())
        self.assertIn("wiring_probe", stderr.getvalue())
        return captured

    def test_hazard_writer_authenticates_continued_epochs_past_a_stale_pin(self):
        self.assertIs(self._run(hazard=True).get("allow_stale_pin"), True)
        self.assertIs(self._run(hazard=True, derivation_only=True).get("allow_stale_pin"), True)

    def test_legacy_writer_does_not(self):
        self.assertNotIn("allow_stale_pin", self._run(hazard=False))
        self.assertNotIn("allow_stale_pin", self._run(hazard=False, derivation_only=True))


if __name__ == "__main__":
    unittest.main()
