"""R0 host admission and power state are tested entirely through fake probes."""
import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from joulewise.align.apple import smc_enumeration as r0
from joulewise.hazards import base, contention
from joulewise.measurement_liveness import Census
from joulewise.night_gate import ProbeResult
from scripts import align_smc_enumerate as cli
from tests.hazards.fakes import FakeClocks


class QuietTests(unittest.TestCase):
    def inputs(self, parent, result):
        return {"agent_probe": lambda: (ProbeResult(("fake",), 1, "", "", 0), None),
                "measurement_probe": lambda: Census(), "custody_parents": [parent],
                "contention_probe": lambda: result,
                "process_probe": lambda: SimpleNamespace(returncode=0, stderr="", stdout="1 launchd\n")}

    def test_unnamed_cpu_job_and_missing_host_counter_refuse(self):
        with tempfile.TemporaryDirectory() as tmp:
            for result in ({"clean": False, "error": None, "outside_aggregate_cpu_s_per_s": .2},
                           {"clean": None, "error": "host CPU unread"}):
                with self.subTest(result=result), self.assertRaises(r0.NotQuiet):
                    r0.require_quiet(**self.inputs(Path(tmp), result))

    def test_missing_custody_parent_refuses_even_when_census_is_clear(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(r0.NotQuiet, "custody parent"):
                r0.require_quiet(**self.inputs(Path(tmp)/"missing", {"clean": True, "error": None}))

    def test_contention_uses_host_delta_and_excludes_only_own_tree(self):
        clock = FakeClocks(read_cost_ns=0)
        ctx = base.Context(clocks=clock)
        own = os.getpid()
        def make_probe(outside):
            calls = 0
            def snapshot():
                nonlocal calls
                stamp = ctx.stamp()
                rows = {}
                for pid, parent, rate in ((own, 1, .2), (987654, own, .4), (123456, 1, outside)):
                    rows[(pid, "start")] = {"pid": pid, "ppid": parent, "start_identity": "start",
                        "start_epoch_s": 0, "command": "python", "cumulative_cpu_seconds": calls*rate}
                hz = os.sysconf("SC_CLK_TCK")
                host = [[round(calls*(.6+outside)*hz), 0, round(calls*hz*8), 0]]
                calls += 1
                return contention.Snapshot(stamp, stamp, rows, None, host=host)
            return r0.CpuQuietProbe(ctx=ctx, snapshot=snapshot)
        with mock.patch.object(r0, "time", wraps=r0.time):
            clean = make_probe(0)()
            dirty = make_probe(.2)()
        self.assertTrue(clean["clean"])
        self.assertAlmostEqual(clean["outside_aggregate_cpu_s_per_s"], 0)
        self.assertFalse(dirty["clean"])
        self.assertGreater(dirty["outside_aggregate_cpu_s_per_s"], .05)

    def test_metadata_records_raw_power_modes_ac_and_os_thermal_level(self):
        outputs = {("/usr/sbin/sysctl", "-n", "hw.model"): "MacFAKE\n",
                   ("/usr/sbin/sysctl", "-n", "hw.memsize"): "1000\n",
                   ("/usr/bin/pmset", "-g"): " lowpowermode 0\n highpowermode 1\n powermode 2\n",
                   ("/usr/bin/pmset", "-g", "custom"): " highpowermode 1\n",
                   ("/usr/bin/pmset", "-g", "batt"): "Now drawing from 'AC Power'\n"}
        def probe(argv):
            return SimpleNamespace(returncode=0, stdout=outputs[tuple(argv)], stderr="")
        reader = mock.Mock()
        reader.read.return_value = 0
        metadata = cli.host_metadata(probe=probe, thermal_reader_factory=lambda: reader)
        self.assertTrue(metadata["ac_power"])
        self.assertEqual(metadata["power_mode"], {"lowpowermode": 0, "highpowermode": 1, "powermode": 2})
        self.assertEqual(metadata["os_thermal_level"], 0)
        self.assertEqual(metadata["pmset_g"]["stdout"], outputs[("/usr/bin/pmset", "-g")])
        reader.close.assert_called_once()

    def test_unavailable_power_or_thermal_probe_is_explicitly_unknown(self):
        def missing(_argv):
            raise OSError("synthetic unavailable")
        metadata = cli.host_metadata(probe=missing, thermal_reader_factory=mock.Mock(side_effect=OSError("gone")))
        self.assertIsNone(metadata["ac_power"])
        self.assertIsNone(metadata["os_thermal_level"])
        self.assertIn("gone", metadata["os_thermal_error"])
        self.assertIn("unavailable", metadata["pmset_g"]["error"])
        self.assertTrue(all(v is None for v in metadata["power_mode"].values()))
