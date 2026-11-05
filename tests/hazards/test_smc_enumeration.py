"""R0 uses only fake IOKit, fake clocks/load, and injected process censuses."""
from __future__ import annotations

import hashlib
import json
import math
import signal
import struct
import subprocess
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from joulewise.hazards import base
from joulewise.align.apple import smc_reader as smc, smc_enumeration as r0
from joulewise.measurement_liveness import Census
from joulewise.night_gate import ProbeResult
from scripts import align_smc_enumerate as cli
from tests.hazards.fakes import FakeClocks
from tests.hazards.test_smc import FakeTransport


class IndexedTransport(FakeTransport):
    def __init__(self, *, broken_index=None):
        super().__init__({"#KEY": ("ui32", struct.pack(">I", 7)),
                          "TG0D": ("flt ", struct.pack("<f", 45)),
                          "TH0P": ("sp78", struct.pack(">h", 33 * 256)),
                          "F0Ac": ("fpe2", struct.pack(">H", 1200 * 4)),
                          "FNum": ("ui8 ", b"\x01"),
                          "TBAD": ("ch8*", b"bad!"),
                          "PSTR": ("flt ", struct.pack("<f", 10))})
        self.broken_index = broken_index

    def call(self, request):
        if request.data8 == smc.CMD_GET_KEY_BY_INDEX:
            if request.data32 == self.broken_index:
                raise OSError("index unavailable")
            return smc.SMCKeyData(key=smc.fourcc(list(self.keys)[request.data32]))
        return super().call(request)


class EnumerationTests(unittest.TestCase):
    def test_observed_apple_silicon_count_bytes(self):
        transport = IndexedTransport()
        transport.keys["#KEY"] = ("ui32", bytes.fromhex("0000086e"))
        self.assertEqual(smc.Reader(transport).read_key("#KEY"), (2158, None))
        original = transport.call
        def indexed(request):
            if request.data8 == smc.CMD_GET_KEY_BY_INDEX and request.data32 >= len(transport.keys):
                return smc.SMCKeyData(key=smc.fourcc("PSTR"))
            return original(request)
        transport.call = indexed
        self.assertTrue(smc.Reader(transport).enumerate_sensors()["complete"])
        # This exception must not byte-swap normal battery integer readings.
        self.assertEqual(smc.decode("ui16", struct.pack("<H", 13264)), 13264)
        self.assertEqual(smc.decode("ui32", struct.pack("<I", 117)), 117)

    def test_observed_ioft_bytes(self):
        transport = FakeTransport({"TG0B": ("ioft", bytes.fromhex("9999270000000000"))})
        value, error = smc.Reader(transport).read_key("TG0B")
        self.assertIsNone(error)
        self.assertAlmostEqual(value, 39.6, places=4)

    def test_index_enumeration_does_not_assume_model_keys(self):
        reader = smc.Reader(IndexedTransport())
        result = reader.enumerate_sensors()
        self.assertTrue(result["complete"])
        self.assertEqual([s["key"] for s in result["keys"]], ["F0Ac", "FNum", "TG0D", "TH0P"])
        self.assertIn("TBAD", result["errors"])
        self.assertEqual(result["unsupported_types"]["TBAD"]["data_type"], "ch8*")
        self.assertEqual(result["keys"][0]["initial_value"], 1200)
        self.assertEqual(result["keys"][3]["initial_value"], 33)
        self.assertEqual(smc.decode("sp78", struct.pack(">h", -256)), -1)

    def test_failed_count_or_index_is_not_complete(self):
        self.assertFalse(smc.Reader(FakeTransport({})).enumerate_sensors()["complete"])
        result = smc.Reader(IndexedTransport(broken_index=2)).enumerate_sensors()
        self.assertFalse(result["complete"])
        self.assertIn("index:2", result["errors"])



class QuietTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def inputs(self):
        return {"agent_probe": lambda: (ProbeResult(("fake",), 1, "", "", 0), None),
                "measurement_probe": lambda: Census(),
                "custody_parents": [Path(self.tmp.name)],
                "contention_probe": lambda: {"clean": True, "error": None},
                "process_probe": lambda: SimpleNamespace(returncode=0, stderr="", stdout="1 /sbin/launchd\n")}

    def test_clean_fake_census_passes(self):
        self.assertEqual(r0.require_quiet(**self.inputs())["agent_exit_code"], 1)

    def test_agent_or_live_chain_or_direct_meter_refuses(self):
        cases = [{"agent_probe": lambda: (None, SimpleNamespace(detail="Codex present"))},
                 {"measurement_probe": lambda: Census(refusals=["live measurement owner"])},
                 {"process_probe": lambda: SimpleNamespace(returncode=0, stderr="",
                                     stdout="22 python /repo/scripts/run_night.py --plan desk.json\n")},
                 {"process_probe": lambda: SimpleNamespace(returncode=0, stderr="",
                                     stdout="23 /usr/bin/powermetrics -i 100\n")},
                 {"process_probe": lambda: SimpleNamespace(returncode=2, stderr="denied", stdout="")},
                 {"process_probe": lambda: SimpleNamespace(returncode=0, stderr="", stdout="bad\n")}]
        for case in cases:
            with self.subTest(case=case), self.assertRaises(r0.NotQuiet):
                r0.require_quiet(**{**self.inputs(), **case})


class CaptureTests(unittest.TestCase):
    def setUp(self):
        self.clock = FakeClocks(read_cost_ns=0)
        self.ctx = base.Context(clocks=self.clock)
        self.reader = smc.Reader(IndexedTransport())
        self.addCleanup(self.reader.close)

    def capture(self, **kwargs):
        return r0.collect(self.reader, seconds=5, idle_s=5, load_s=5, recovery_s=5,
                          gpu_step=False, quiet_check=lambda: {}, ctx=self.ctx, sink=lambda _: None, **kwargs)

    def test_idle_capture_is_one_hz_and_carries_three_clocks(self):
        result = self.capture()
        self.assertEqual(len(result["samples"]), 5)
        for row in result["samples"]:
            base.Stamp.from_json(row["started"])
            base.Stamp.from_json(row["finished"])
            self.assertEqual(row["values"]["units"]["TH0P"], "degC")
        self.assertEqual([r["elapsed_s"] for r in result["samples"]], list(range(5)))

    def test_refusal_precedes_smc_access(self):
        reader = mock.Mock()
        with self.assertRaises(r0.NotQuiet):
            r0.collect(reader, seconds=5, idle_s=5, load_s=5, recovery_s=5, gpu_step=False,
                       quiet_check=mock.Mock(side_effect=r0.NotQuiet("agent")), ctx=self.ctx, sink=lambda _: None)
        reader.enumerate_sensors.assert_not_called()

    def test_fake_load_starts_and_stops_on_periodic_census_failure(self):
        load = mock.Mock()
        calls = 0
        def quiet():
            nonlocal calls
            calls += 1
            if calls == 7:
                raise r0.NotQuiet("new agent")
        with self.assertRaises(r0.NotQuiet):
            r0.collect(self.reader, seconds=5, idle_s=5, load_s=10, recovery_s=5, gpu_step=True,
                       quiet_check=quiet, ctx=self.ctx, sink=lambda _: None, load_factory=lambda _: load)
        load.start.assert_called_once()
        load.stop.assert_called_once()

    def test_fake_step_has_all_phases_and_cleans_worker_on_normal_exit(self):
        load = mock.Mock()
        result = r0.collect(self.reader, seconds=5, idle_s=5, load_s=5, recovery_s=5, gpu_step=True,
                            quiet_check=lambda: {}, ctx=self.ctx, sink=lambda _: None, load_factory=lambda _: load)
        self.assertEqual([p["phase"] for p in result["phases"]], ["idle", "load", "recovery"])
        self.assertEqual(len(result["samples"]), 15)
        load.stop.assert_called_once()

    def test_cli_fake_capture_writes_json_markdown_and_compatible_journal(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "r0"
            result = cli.main(["--output", str(output), "--seconds", "5"], reader_factory=lambda: self.reader,
                              quiet_check=lambda: {}, ctx_factory=lambda: self.ctx,
                              metadata=lambda: {"hw.model": "FAKE"})
            self.assertEqual(result, 0)
            raw = (output / "r0.json").read_bytes()
            report = json.loads(raw)
            self.assertEqual(report["hardware"]["hw.model"], "FAKE")
            self.assertEqual(report["hardware_after"]["hw.model"], "FAKE")
            self.assertGreater(len(report["quiet_observations"]), 2)
            self.assertIn(hashlib.sha256(raw).hexdigest(), (output / "summary.md").read_text())
            self.assertEqual(report["coverage"]["all_keys"]["sample_fraction"], 1)
            readings = [json.loads(line) for line in (output / "samples.jsonl").read_text().splitlines()]
            self.assertEqual(len(readings), 5)

    def test_cli_refuses_before_output_creation_or_backend_construction(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "r0"
            factory = mock.Mock()
            result = cli.main(["--output", str(output)], reader_factory=factory,
                              quiet_check=mock.Mock(side_effect=r0.NotQuiet("agent present")))
            self.assertEqual(result, 3)
            self.assertFalse(output.exists())
            factory.assert_not_called()

    def test_interrupted_cli_preserves_failure_journal_and_restores_handlers(self):
        calls = 0
        def quiet():
            nonlocal calls
            calls += 1
            if calls == 4:
                raise InterruptedError("synthetic SIGTERM")
            return {}
        before = signal.getsignal(signal.SIGTERM)
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "r0"
            result = cli.main(["--output", str(output), "--seconds", "5"], reader_factory=lambda: self.reader,
                              quiet_check=quiet, ctx_factory=lambda: self.ctx, metadata=lambda: {})
            self.assertEqual(result, 3)
            self.assertFalse((output / "r0.json").exists())
            self.assertIn("capture_failed", (output / "samples.jsonl").read_text())
        self.assertEqual(signal.getsignal(signal.SIGTERM), before)

    def test_gpu_worker_cleanup_escalates_and_closes_pipes_using_fake_process(self):
        load = r0.GpuLoad(5)
        child = mock.Mock(pid=424242)
        child.poll.return_value = None
        child.wait.side_effect = [subprocess.TimeoutExpired("fake", 5), 0]
        load.process = child
        with mock.patch.object(r0.os, "killpg") as kill:
            load.stop()
        self.assertEqual(kill.call_args_list, [mock.call(424242, signal.SIGTERM), mock.call(424242, signal.SIGKILL)])
        child.stdin.close.assert_called_once()
        child.stdout.close.assert_called_once()
