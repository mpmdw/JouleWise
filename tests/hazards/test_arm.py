"""The thin arm: order, GO only on all-PASS plus a clean census, NULL on any
REFUSE or UNMEASURED, record-only collectors outside the decision, and a
create-once arm.json.  Hardware is faked at the seams; the instrument probe
runs its real child process against the fake powermetrics."""
from __future__ import annotations

import json
import os
import re
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from joulewise import night_gate
from joulewise.hazards import arm, base, battery, clock, contention, thermal
from tests.hazards.fakes import (
    BOOT_UUID, FAKE_POWERMETRICS, INSTRUMENT, FakeClocks, FakeProcessTable, FakeSmc, FrequencyReader,
    Runner, battery_bytes, completed, ppm_word,
)

GIB = 1024 ** 3
DRIVER = 4000
OFF_ALREADY = b"Network Time is already off.\n"  # the 10-01 0137Z wording


class Rig:
    """One fake Mac: clocks, gauge, notify bus, process table, disks, ntp_adjtime."""

    def __init__(self, directory: Path) -> None:
        self.custody = directory / "custody"
        self.clocks = FakeClocks()
        self.table = FakeProcessTable(self.clocks, driver_pid=DRIVER)
        self.battery_file = "float-20261005-desk.ioreg"
        self.battery_after_s: tuple[float, str] | None = None
        self.thermal_level = 0
        self.free_bytes = 264 * GIB
        self.census = (1, b"")
        self.census_after_s: tuple[float, tuple[int, bytes]] | None = None
        self.off = (0, OFF_ALREADY)
        self.cadence_fixture = INSTRUMENT / "cadence-20261004-block3-idle.json"
        self.reader = FrequencyReader(self.clocks)
        self.smc = FakeSmc(self.clocks)  # B0AC 0 mA unless a test sets ``current``
        self.smc_enabled = True
        self.boot = BOOT_UUID
        self.fail: set[str] = set()
        self.t_start = self.clocks.raw_ns
        self.runner = Runner({
            arm.AGENT_CENSUS_ARGV: self._census,
            battery.IOREG_BATTERY_ARGV: self._ioreg,
            thermal.NOTIFYUTIL_ARGV: self._notify,
            thermal.PMSET_THERM_ARGV: lambda argv: completed(argv, b"Note: No thermal warning level has been recorded\n"),
            clock.BOOT_ARGV: self._boot,
            arm.NETWORK_TIME_OFF_ARGV: lambda argv: completed(argv, self.off[1], returncode=self.off[0]),
            contention.PS_ARGV: self._ps,
            arm.DIAGNOSTIC_ARGVS[0]: lambda argv: completed(argv, b"System-wide power settings:\n lowpowermode 0\n"),
            "/usr/bin/false": lambda argv: completed(argv, b"", returncode=1),
            "/no/such/collector": lambda argv: completed(argv, error="FileNotFoundError: x"),
            "/usr/bin/slow-collector": lambda argv: completed(argv, timed_out=True, returncode=None),
            "/usr/bin/good-collector": lambda argv: completed(argv, b'{"ok": true}\n'),
        })

    def elapsed_s(self) -> float:
        return (self.clocks.raw_ns - self.t_start) / 1e9

    def _census(self, argv):
        if "census" in self.fail:
            return completed(argv, error="OSError: pgrep missing")
        returncode, stdout = self.census
        if self.census_after_s and self.elapsed_s() >= self.census_after_s[0]:
            returncode, stdout = self.census_after_s[1]
        return completed(argv, stdout, returncode=returncode)

    def _ioreg(self, argv):
        if "battery" in self.fail:
            return completed(argv, timed_out=True, returncode=None)
        name = self.battery_file
        if self.battery_after_s and self.elapsed_s() >= self.battery_after_s[0]:
            name = self.battery_after_s[1]
        raw = battery_bytes(name)
        fresh = int(self.clocks.wall_s) - 20  # the gauge publishes every 60 s
        return completed(argv, re.sub(rb'^( {6}"UpdateTime" = )[0-9]+$',
                                      lambda m: m.group(1) + str(fresh).encode(), raw, count=1,
                                      flags=re.M))

    def _notify(self, argv):
        if "thermal" in self.fail:
            return completed(argv, returncode=1)
        return completed(argv, f"com.apple.system.thermalpressurelevel {self.thermal_level}\n".encode())

    def _boot(self, argv):
        if "boot" in self.fail:
            return completed(argv, returncode=1)
        return completed(argv, (self.boot + "\n").encode())

    def _ps(self, argv):
        if "contention" in self.fail:
            return completed(argv, returncode=1)
        return self.table.ps(argv)

    def statvfs(self, path):
        if "disk" in self.fail:
            raise PermissionError(13, "Permission denied", path)
        return SimpleNamespace(f_bavail=self.free_bytes // 4096, f_frsize=4096, f_blocks=10**9)

    def stat(self, path):
        return SimpleNamespace(st_dev=1 if "runs" in str(path) else 2)

    def config(self, **overrides) -> arm.ArmConfig:
        values = dict(custody_dir=self.custody, thresholds=arm.default_thresholds(),
                      disk_targets=[{"path": "/Volumes/x/runs", "copies": 1},
                                    {"path": "/Volumes/backup", "copies": 1}],
                      tree_roots=(DRIVER,), powermetrics_executable=str(FAKE_POWERMETRICS),
                      privilege_prefix=())
        values.update(overrides)
        return arm.ArmConfig(**values)

    def run(self, **overrides) -> arm.ArmResult:
        seams = arm.Seams(ctx=base.Context(run=self.runner, clocks=self.clocks),
                          frequency_reader=self.reader, statvfs=self.statvfs, stat=self.stat,
                          host_cpu=self.table.host_cpu,
                          smc_read=self.smc if self.smc_enabled else None)
        with mock.patch.dict(os.environ, {"FAKE_PM_FIXTURE": str(self.cadence_fixture)}):
            return arm.run(self.config(**overrides), seams)


class ArmTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR"))
        self.addCleanup(self.tmp.cleanup)
        self.rig = Rig(Path(self.tmp.name))

    def steps(self, result):
        return [step["step"] for step in result.document["steps"]]

    def test_quiet_float_mac_arms_go_in_the_registered_order(self):
        result = self.rig.run()
        self.assertEqual(result.decision, arm.GO, result.reasons)
        self.assertEqual(self.steps(result), [
            "census", "battery.instant", "thermal.instant", "disk.instant", "clock.instant",
            "network_time_off", "instrument.probe", "contention.dwell", "battery.final",
            "thermal.final", "clock.dwell_and_go", "census_at_go", "decision"])
        first_calls = [call[0] for call in self.rig.runner.calls[:2]]
        self.assertEqual(first_calls, ["/usr/bin/pgrep", "/usr/sbin/ioreg"])
        record = json.loads(result.path.read_text())
        self.assertEqual(record["decision"], "GO")
        self.assertEqual(record["network_time_off"]["stdout"], OFF_ALREADY.decode())
        self.assertEqual(record["hazards"]["clock"][-1]["verdict"]["status"], "PASS")
        series = record["hazards"]["clock"][-1]["measurement"]["values"]["samples"]
        self.assertGreater(len(series), 600)  # 1 Hz over the 600 s dwell, plus start/end/GO
        self.assertTrue((self.rig.custody / "hazards" / "arm.steps.jsonl").exists())
        self.assertIn("lowpowermode 0", record["diagnostics"][0]["stdout"])
        self.assertTrue(any((self.rig.custody / "hazards" / "arm-raw").glob("*ps.txt.gz")))
        dwell_s = record["hazards"]["contention"][0]["measurement"]["values"]["elapsed_s"]
        self.assertTrue(600 <= dwell_s <= 2700)

    def test_agent_present_refuses_at_the_census_before_any_action(self):
        self.rig.census = (0, b"812 /usr/local/bin/claude --resume\n")
        result = self.rig.run()
        self.assertEqual((result.decision, result.refused_at), (arm.NULL, "census"))
        self.assertEqual(self.rig.runner.calls, [arm.AGENT_CENSUS_ARGV])
        self.assertIn("claude", result.reasons[0])

    def test_census_that_cannot_run_refuses(self):
        self.rig.fail.add("census")
        self.assertEqual(self.rig.run().refused_at, "census")

    def test_pgrep_failure_with_empty_output_is_not_a_clean_census(self):
        # pgrep exits 2 (syntax) or 3 (fatal) with nothing on stdout: no census ran.
        for returncode in (2, 3):
            with self.subTest(returncode=returncode):
                rig = Rig(Path(tempfile.mkdtemp(dir=self.tmp.name)))
                rig.census = (returncode, b"")
                result = rig.run()
                self.assertEqual((result.decision, result.refused_at), (arm.NULL, "census"))
                self.assertEqual(rig.runner.calls, [arm.AGENT_CENSUS_ARGV])

    def test_agent_that_starts_during_the_dwell_gets_no_go(self):
        # Review finding: step 1 runs up to ~47 min before GO.
        self.rig.census_after_s = (300.0, (0, b"91234 /opt/homebrew/bin/codex exec\n"))
        result = self.rig.run()
        self.assertEqual((result.decision, result.refused_at), (arm.NULL, "census_at_go"))
        self.assertIn("codex", result.reasons[0])
        self.assertEqual(self.steps(result)[-3:], ["clock.dwell_and_go", "census_at_go", "decision"])
        record = json.loads(result.path.read_text())
        self.assertTrue(record["census"]["clean"])
        self.assertFalse(record["census_at_go"]["clean"])
        self.assertEqual(self.rig.runner.calls[-1], arm.AGENT_CENSUS_ARGV)

    def test_go_records_a_clean_census_taken_after_the_final_reads(self):
        result = self.rig.run()
        self.assertEqual(result.decision, arm.GO, result.reasons)
        census = result.document["census_at_go"]
        self.assertTrue(census["clean"])
        final_clock = result.document["hazards"]["clock"][-1]["measurement"]["finished"]
        self.assertGreater(census["stamp"]["monotonic_ns"], final_clock["monotonic_ns"])

    def test_each_instant_hazard_refuses_before_network_time_is_touched(self):
        cases = {
            "battery": lambda rig: setattr(rig, "battery_file", "charging-1716ma-synthetic-from-real.ioreg"),
            "thermal": lambda rig: setattr(rig, "thermal_level", 1),
            "disk": lambda rig: setattr(rig, "free_bytes", 30 * GIB),
            "clock": lambda rig: setattr(rig.clocks, "drift_word", ppm_word(3.7)),
        }
        for module, inject in cases.items():
            with self.subTest(module=module):
                rig = Rig(Path(tempfile.mkdtemp(dir=self.tmp.name)))
                inject(rig)
                result = rig.run()
                self.assertEqual((result.decision, result.refused_at), (arm.NULL, "instant"))
                self.assertTrue(any(reason.startswith(f"{module} REFUSE") for reason in result.reasons),
                                result.reasons)
                self.assertNotIn(arm.NETWORK_TIME_OFF_ARGV, rig.runner.calls)

    def test_unmeasured_refuses_at_arm_for_every_module(self):
        for module in ("battery", "thermal", "disk", "clock", "instrument", "contention"):
            with self.subTest(module=module):
                rig = Rig(Path(tempfile.mkdtemp(dir=self.tmp.name)))
                if module == "clock":
                    rig.reader.fail = True
                elif module == "instrument":
                    rig.cadence_fixture = Path("/no/such/fixture.json")  # the fake cannot start
                else:
                    rig.fail.add(module)
                result = rig.run(thresholds={**arm.default_thresholds(),
                                             "contention": {**arm.default_thresholds()["contention"],
                                                            "cap_s": 120}})
                self.assertEqual(result.decision, arm.NULL)
                self.assertTrue(any(module in reason for reason in result.reasons), result.reasons)

    def test_slow_launchd_cadence_refuses(self):
        self.rig.cadence_fixture = INSTRUMENT / "cadence-20260919-n1-d01-launchd.json"
        result = self.rig.run()
        self.assertEqual((result.decision, result.refused_at), (arm.NULL, "instrument"))

    def test_contending_daemon_times_the_dwell_out(self):
        self.rig.table.processes[340].cpu_per_s = 1.84  # fseventsd, 09-22
        result = self.rig.run()
        self.assertEqual((result.decision, result.refused_at), (arm.NULL, "dwell"))
        self.assertIn("fseventsd", result.reasons[0])
        self.assertGreaterEqual(self.rig.elapsed_s(), 2700)

    def test_charging_that_starts_during_the_dwell_refuses_at_the_final_read(self):
        self.rig.battery_after_s = (300.0, "charging-1716ma-synthetic-from-real.ioreg")
        result = self.rig.run()
        self.assertEqual((result.decision, result.refused_at), (arm.NULL, "final"))
        self.assertTrue(result.reasons[0].startswith("battery REFUSE"))

    def test_a_battery_current_burst_at_the_instant_read_refuses_before_network_time(self):
        # B0AC -865 mA (the 10-06 probe burst) while the registry reads a clean float.
        self.rig.smc.current = lambda t: -865
        result = self.rig.run()
        self.assertEqual((result.decision, result.refused_at), (arm.NULL, "instant"))
        self.assertIn("|SMC B0AC| 865 mA > 200 mA", result.reasons[0])
        self.assertNotIn(arm.NETWORK_TIME_OFF_ARGV, self.rig.runner.calls)

    def test_a_battery_current_that_starts_during_the_dwell_refuses_at_the_final_read(self):
        self.rig.smc.current = lambda t: -450 if t >= 300.0 else 0
        result = self.rig.run()
        self.assertEqual((result.decision, result.refused_at), (arm.NULL, "final"))
        self.assertIn("|SMC B0AC| 450 mA", result.reasons[0])

    def test_without_the_smc_the_arm_judges_the_registry_and_records_the_fallback(self):
        self.rig.smc_enabled = False
        result = self.rig.run()
        self.assertEqual(result.decision, arm.GO, result.reasons)
        record = json.loads(result.path.read_text())
        for entry in record["hazards"]["battery"]:
            observed = entry["verdict"]["observed"]
            self.assertEqual(observed["current_source"], "registry")
            self.assertEqual([flag["code"] for flag in observed["flags"]], [battery.SMC_UNAVAILABLE])

    def test_go_records_the_smc_current_beside_the_registry_cross_check(self):
        result = self.rig.run()
        record = json.loads(result.path.read_text())
        self.assertEqual([entry["phase"] for entry in record["hazards"]["battery"]], ["instant", "final"])
        for entry in record["hazards"]["battery"]:
            observed = entry["verdict"]["observed"]
            self.assertEqual((observed["current_source"], observed["smc_current_ma"],
                              observed["instant_amperage_ma"], observed["flags"]), ("smc", 0, 0, []))

    def test_clock_step_during_the_dwell_refuses(self):
        self.rig.clocks.step_at(500.0, 6_000_000)
        result = self.rig.run()
        self.assertEqual((result.decision, result.refused_at), (arm.NULL, "final"))
        self.assertTrue(any("residual" in reason for reason in result.reasons))

    def test_frequency_word_change_at_the_end_of_the_dwell_refuses(self):
        original = self.rig.reader.__call__
        self.rig.battery_after_s = None

        def reader():
            # A quiet Mac's dwell is READY 600 s in; re-disciplining starts just before.
            if self.rig.elapsed_s() > 590:
                self.rig.clocks.drift_word = ppm_word(-3.0)
            return original()

        self.rig.reader = reader
        result = self.rig.run()
        self.assertEqual(result.decision, arm.NULL)
        self.assertTrue(any("frequency word changed" in reason for reason in result.reasons))

    def test_record_only_collectors_never_change_the_decision(self):
        collectors = [{"name": "pack-tree", "argv": ["/usr/bin/good-collector"], "timeout_s": 5},
                      {"name": "model-identity", "argv": ["/usr/bin/slow-collector"], "timeout_s": 1},
                      {"name": "ledger", "argv": ["/usr/bin/false"]},
                      {"name": "missing", "argv": ["/no/such/collector"]},
                      {"name": "malformed"}]
        result = self.rig.run(record_only=collectors)
        self.assertEqual(result.decision, arm.GO, result.reasons)
        recorded = {item["name"]: item for item in result.document["record_only"]}
        self.assertTrue(recorded["model-identity"]["timed_out"])
        self.assertEqual(recorded["ledger"]["returncode"], 1)
        self.assertIn("KeyError", recorded["malformed"]["error"])
        self.assertEqual(recorded["pack-tree"]["stdout"]["sha256"],
                         base.sha256_hex(b'{"ok": true}\n'))

    def test_network_time_off_output_is_recorded_not_judged(self):
        self.rig.off = (1, b"sudo: a password is required\n")
        result = self.rig.run()
        self.assertEqual(result.decision, arm.GO, result.reasons)
        self.assertEqual(result.document["network_time_off"]["returncode"], 1)

    def test_arm_json_is_created_once(self):
        self.rig.census = (0, b"812 claude\n")
        first = self.rig.run()
        with self.assertRaises(FileExistsError):
            self.rig.run()
        self.assertEqual(json.loads(first.path.read_text())["decision"], "NULL")

    def test_thresholds_for_every_module_are_required(self):
        thresholds = arm.default_thresholds()
        del thresholds["thermal"]
        with self.assertRaises(KeyError):
            self.rig.run(thresholds=thresholds)

    def test_census_argv_is_night_gates(self):
        self.assertEqual(arm.AGENT_CENSUS_ARGV, night_gate.AGENT_CENSUS_ARGV)


if __name__ == "__main__":
    unittest.main()
