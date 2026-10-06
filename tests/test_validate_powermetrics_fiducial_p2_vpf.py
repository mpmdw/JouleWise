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

    def test_the_re_anchor_copies_every_record_field(self):
        # The helper builds records field by field; a new PowermetricsRecord
        # field must be added there too (this pins the field set it copies).
        from dataclasses import fields

        from joulewise.adapters.powermetrics import PowermetricsRecord

        self.assertEqual([field.name for field in fields(PowermetricsRecord)], [
            "timestamp_s", "elapsed_ns", "rail_power_w", "combined_power_w",
            "rail_energy_mj", "thermal_pressure", "metadata"])

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


_PARSE_COUNTER_SITECUSTOMIZE = """
# P2-VPF test hook: log every parse of a powermetrics stream and its caller.
# Installed through PYTHONPATH so no sandbox source byte changes.
import importlib.abc
import importlib.util
import json
import os
import sys

_TARGET = "joulewise.adapters.powermetrics"


class _CountingFinder(importlib.abc.MetaPathFinder):
    def find_spec(self, name, path, target=None):
        if name != _TARGET:
            return None
        sys.meta_path.remove(self)
        try:
            spec = importlib.util.find_spec(name)
        finally:
            sys.meta_path.insert(0, self)
        if spec is None or spec.loader is None:
            return spec
        exec_module = spec.loader.exec_module

        def counted_exec(module):
            exec_module(module)
            original = module.parse_powermetrics_records

            def parse_powermetrics_records(data, **kwargs):
                caller = sys._getframe(1)
                with open(os.environ["JW_P2_VPF_PARSE_LOG"], "a", encoding="utf-8") as log:
                    log.write(json.dumps([caller.f_code.co_name,
                                          os.path.basename(caller.f_code.co_filename),
                                          sorted(kwargs)]) + "\\n")
                return original(data, **kwargs)

            module.parse_powermetrics_records = parse_powermetrics_records

        spec.loader.exec_module = counted_exec
        return spec


if os.environ.get("JW_P2_VPF_PARSE_LOG"):
    sys.meta_path.insert(0, _CountingFinder())
"""


class ParseCountTests(hazard_tests._SandboxCase):
    """main() parses a slot's plist once on HAZARD and twice on legacy (review M6/M9)."""

    def _main_parses(self, *, hazard: bool) -> list[list[str]]:
        hook = Path(self.enterContext(tempfile.TemporaryDirectory()))
        (hook / "sitecustomize.py").write_text(_PARSE_COUNTER_SITECUSTOMIZE, encoding="utf-8")
        log = hook / "parses.jsonl"
        log.touch()
        state = self.rig.real_writer_state("session-p2-parse")
        if hazard:
            self.rig.hazard(state)
        completed = self.rig.run_writer(state, slot="pre", JW_P2_VPF_PARSE_LOG=str(log),
                                        PYTHONPATH=str(hook))
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        calls = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()]
        self.assertTrue(calls, "the parse hook did not load")
        return [kwargs for function, filename, kwargs in calls
                if (function, filename) == ("main", "validate_powermetrics_fiducial.py")]

    # main() also parses the sampler's first frame once (readiness), so the
    # whole plist is the second call; legacy adds the anchored re-parse.
    def test_hazard_slot_parses_its_plist_once(self):
        self.assertEqual(self._main_parses(hazard=True), [[], []])

    def test_legacy_slot_still_parses_twice(self):
        self.assertEqual(self._main_parses(hazard=False),
                         [[], [], ["first_record_endpoint_s"]])


class SessionCustodyAllowanceTests(unittest.TestCase):
    """The session check's time and teardown (P2-VPF review R1, R2), in process."""

    def setUp(self) -> None:
        from dataclasses import replace
        from types import SimpleNamespace

        from joulewise import calibration_ledger as ledger
        from tests.calibration_exits_fixtures.custody_hang import CustodyFixture

        self.ledger = ledger
        fixture = CustodyFixture().__enter__()
        self.addCleanup(fixture.__exit__, None, None, None)
        self.fixture = fixture
        self.state = fixture.witness._state_real_writer("session-p2-allowance")
        snapshot = ledger.load_calibration_ledger_snapshot(
            fixture.ledger, fixture.pin, repo_root=fixture.repo, verify_custody=False)
        row = replace(snapshot.observations[0], bracket_session_id=self.state["session_id"])
        self.snapshot = SimpleNamespace(
            bracket_session_by_id={self.state["session_id"]: SimpleNamespace(
                finalized_slots={"pre": row})},
            head_digest=snapshot.head_digest)

    def _lifecycle(self, budget_s: float):
        deadline = self.ledger.CustodyDeadline(budget_s, telemetry_stream=None)
        state = self.state
        lifecycle = writer._CaptureLedgerLifecycle(
            ledger_path=self.fixture.ledger, head_pin_path=self.fixture.pin,
            attempt_id=state["attempt_id"], custody_locator=state["custody_locator"],
            identity_epoch=state["epoch"], t1_bindings=state["t1"],
            session_id=state["session_id"], slot="pre", require_committed_pin=False,
            verify_historical_custody=False, custody_deadline=deadline)
        return lifecycle, deadline

    def _begin(self, lifecycle, **ledger_patches):
        original = writer._session_custody_check

        def check(*args, **kwargs):
            with mock.patch.object(writer, "load_calibration_ledger_snapshot",
                                   return_value=self.snapshot), \
                    contextlib.ExitStack() as stack:
                for name, value in ledger_patches.items():
                    stack.enter_context(mock.patch.object(self.ledger, name, value))
                return original(*args, **kwargs)

        with mock.patch.object(writer, "_session_custody_check", side_effect=check), \
                contextlib.redirect_stderr(io.StringIO()):
            lifecycle.begin()
        self.addCleanup(lifecycle._release_writer_lease)

    def test_a_slow_session_check_does_not_spend_the_preparation_allowance(self):
        import time

        def slow(_rows, _root, worker_deadline):
            time.sleep(worker_deadline.remaining() + 0.05)
            worker_deadline.check()

        lifecycle, _deadline = self._lifecycle(0.4)
        self._begin(lifecycle, bounded_custody_reasons=mock.Mock(side_effect=slow))
        self.assertTrue(lifecycle.begun)
        self.assertEqual(lifecycle.session_custody["status"], "unmeasured")
        self.assertIn("calibration_ledger_custody_timeout", lifecycle.session_custody["error"])

    def test_a_worker_whose_teardown_failed_refuses_before_the_capture(self):
        import subprocess

        def unreaped(*_args, **_kwargs):
            raise subprocess.TimeoutExpired("worker reap", 2)

        lifecycle, _deadline = self._lifecycle(30.0)
        with self.assertRaises(self.ledger.CalibrationLedgerError) as caught:
            self._begin(lifecycle, bounded_custody_reasons=mock.Mock(side_effect=unreaped))
        self.assertFalse(lifecycle.begun)
        self.assertEqual(caught.exception.code, RefusalCode.LEDGER_CUSTODY_INVALID)
        self.assertEqual(caught.exception.context["reason"],
                         "session_custody_worker_not_quiescent")

    def test_a_verification_refusal_after_teardown_stays_a_record(self):
        def invalid(*_args, **_kwargs):
            raise self.ledger.CalibrationLedgerError(
                RefusalCode.LEDGER_CUSTODY_INVALID, context={"reason": "custody_worker_protocol"})

        lifecycle, _deadline = self._lifecycle(30.0)
        self._begin(lifecycle, bounded_custody_reasons=mock.Mock(side_effect=invalid))
        self.assertTrue(lifecycle.begun)
        self.assertEqual(lifecycle.session_custody["status"], "unmeasured")

    def test_the_credit_never_moves_the_window_deadline(self):
        deadline = self.ledger.CustodyDeadline(10.0, telemetry_stream=None)
        deadline.window_deadline = deadline.deadline + 1.0
        before = deadline.deadline
        writer._credit_preparation_allowance(deadline, 5.0)
        self.assertEqual(deadline.deadline, before + 1.0)
        writer._credit_preparation_allowance(deadline, 5.0)
        self.assertEqual(deadline.deadline, before + 1.0)
        unbounded = self.ledger.CustodyDeadline(10.0, telemetry_stream=None)
        start = unbounded.deadline
        writer._credit_preparation_allowance(unbounded, 2.5)
        self.assertEqual(unbounded.deadline, start + 2.5)
        self.assertAlmostEqual(unbounded.budget_s, 12.5)


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
