from __future__ import annotations

import importlib.metadata
import shlex
import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch

from joulewise.environment import (
    collect_environment_snapshot,
    evaluate_environment_policy,
)


def completed(command: list[str], stdout: str = "", returncode: int = 0):
    return subprocess.CompletedProcess(command, returncode, stdout=stdout, stderr="")


LIVE_SYSTEM_PROFILER_SP_DISPLAYS_JSON = """{
  "SPDisplaysDataType" : [
    {
      "_name" : "Apple M3 Max",
      "spdisplays_metal" : "spdisplays_supported",
      "spdisplays_vendor" : "sppci_vendor_Apple",
      "sppci_bus" : "spdisplays_builtin",
      "sppci_cores" : "40",
      "sppci_device_type" : "spdisplays_gpu",
      "sppci_model" : "Apple M3 Max"
    }
  ]
}"""


SUCCESS_OUTPUTS = {
    ("pmset", "-g", "batt"): (
        "Now drawing from 'AC Power'\n"
        " -InternalBattery-0\t99%; charged; 0:00 remaining present: true\n"
    ),
    ("pmset", "-g"): " lowpowermode      1\n",
    ("pmset", "-g", "assertions"): "   PreventUserIdleDisplaySleep    1\n",
    ("pmset", "-g", "systemstate"): (
        # Verbatim shape observed live on macOS (Darwin 25.5.0, 2026-07-17):
        # the capabilities line reads "Capabilities are:", not "Capabilities:".
        "Current System Capabilities are: CPU Audio Network \n"
        "Current Power State: 4\n"
    ),
    ("pmset", "-g", "therm"): "No thermal warning level has been recorded\n",
    ("defaults", "-currentHost", "read", "com.apple.screensaver"): (
        "{ moduleDict = { moduleName = Ventura; }; idleTime = 1200; }\n"
    ),
    ("ioreg", "-c", "IOHIDSystem"): '"HIDIdleTime" = 5000000000\n',
    ("memory_pressure", "-Q"): "System-wide memory free percentage: 42%\n",
    ("vm_stat",): (
        "Mach Virtual Memory Statistics: (page size of 4096 bytes)\n"
        "Pages free:                               1000.\n"
        "Pageins:                                  2000.\n"
        "Pageouts:                                 30.\n"
        "Pages occupied by compressor:             400.\n"
        "Pages stored in compressor:               500.\n"
    ),
    ("sysctl", "vm.swapusage"): "vm.swapusage: total = 1024.00M used = 128.00M free = 896.00M\n",
    ("system_profiler", "SPDisplaysDataType", "-json"): LIVE_SYSTEM_PROFILER_SP_DISPLAYS_JSON,
    ("ioreg", "-r", "-c", "IOMobileFramebuffer"): (
        "+-o IOMobileFramebufferShim  <class IOMobileFramebufferShim, id 0x1, registered>\n"
        '  |   "IONameMatched" = "disp0,t603x"\n'
        "+-o IOMobileFramebufferShim  <class IOMobileFramebufferShim, id 0x2, registered>\n"
        '  |   "external" = Yes\n'
        '  |   "IONameMatched" = "dispext0,t603x"\n'
    ),
    ("ioreg", "-r", "-c", "AppleSmartBattery", "-d", "1"): (
        '"ExternalConnected" = Yes\n'
        '"IsCharging" = No\n'
        '"FullyCharged" = Yes\n'
        '"AdapterDetails" = {"Watts"=96,"Description"="USB-C Power Adapter"}\n'
    ),
    ("sysctl", "-n", "kern.boottime"): "{ sec = 1700000000, usec = 0 } Tue Nov 14 00:00:00 2023\n",
    ("pgrep", "-x", "timed"): "123\n",
    ("uptime",): "10:00  up 1 day,  3 users, load averages: 1.25 2.50 3.75\n",
    ("sw_vers",): (
        "ProductName:\t\tmacOS\n"
        "ProductVersion:\t\t15.5\n"
        "BuildVersion:\t\t24F74\n"
    ),
    ("sysctl", "-n", "hw.model", "hw.ncpu", "machdep.cpu.brand_string"): (
        "Mac15,9\n12\nApple M3 Max\n"
    ),
}

COMMAND_FIELDS = {
    "pmset_batt": ("power_source", "battery_percent", "battery_state"),
    "pmset": ("low_power_mode",),
    "pmset_assertions": ("display_sleep_prevented",),
    "pmset_systemstate": ("display_power_state",),
    "screensaver_defaults": ("screensaver_delay_s",),
    "ioreg_hid_idle": ("hid_idle_s",),
    "system_profiler_spdisplays": (
        "display",
    ),
    "uptime": ("load_average_1m", "load_average_5m", "load_average_15m"),
    "sw_vers": ("product_name", "product_version", "build_version"),
    "sysctl_host": ("hw_model", "logical_cpu_count", "cpu_brand"),
}

COMMANDS_BY_ERROR_KEY = {
    "pmset_batt": ("pmset", "-g", "batt"),
    "pmset": ("pmset", "-g"),
    "pmset_assertions": ("pmset", "-g", "assertions"),
    "pmset_systemstate": ("pmset", "-g", "systemstate"),
    "screensaver_defaults": ("defaults", "-currentHost", "read", "com.apple.screensaver"),
    "ioreg_hid_idle": ("ioreg", "-c", "IOHIDSystem"),
    "system_profiler_spdisplays": ("system_profiler", "SPDisplaysDataType", "-json"),
    "uptime": ("uptime",),
    "sw_vers": ("sw_vers",),
    "sysctl_host": ("sysctl", "-n", "hw.model", "hw.ncpu", "machdep.cpu.brand_string"),
}


def successful_fake_run(command, **kwargs):
    return completed(command, SUCCESS_OUTPUTS[tuple(command)])


class EnvironmentSnapshotTests(unittest.TestCase):
    def test_quiet_mac_shell_accepts_live_capabilities_are_spelling(self) -> None:
        pattern = r"Current System Capabilities( are)?:.*Graphics"
        script = (
            Path(__file__).resolve().parents[1] / "scripts" / "quiet_mac_prep.sh"
        ).read_text(encoding="utf-8")
        self.assertIn(pattern, script)
        result = subprocess.run(
            ["bash", "-c", f"grep -E {shlex.quote(pattern)} >/dev/null"],
            input="Current System Capabilities are: CPU Graphics Audio Network\n",
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0)

    def test_shared_policy_evaluator_fails_closed_but_never_gates_load_average(self) -> None:
        snapshot = {
            "power_source": "AC Power",
            "power": {"external_connected": True},
            "low_power_mode": False,
            "display_power_state": "all_asleep",
            "screensaver_engaged": False,
            "thermal_pressure": "nominal",
            "load_average_1m": 999.0,
        }
        clean = evaluate_environment_policy(snapshot)
        self.assertTrue(clean["eligible"])
        self.assertFalse(clean["load_average_evidence"]["admission_gate"])

        unknown = dict(snapshot)
        unknown["screensaver_engaged"] = None
        blocked = evaluate_environment_policy(unknown)
        self.assertFalse(blocked["eligible"])
        finding = next(
            row for row in blocked["findings"] if row["field"] == "screensaver_engaged"
        )
        self.assertEqual(finding["status"], "unknown")
        self.assertNotEqual(clean["snapshot_sha256"], blocked["snapshot_sha256"])

    def test_display_and_screensaver_probes_parse_defensively(self) -> None:
        outputs = {
            **SUCCESS_OUTPUTS,
            ("system_profiler", "SPDisplaysDataType", "-json"): """{
              "SPDisplaysDataType": [{"spdisplays_ndrvs": [{
                "spdisplays_online": "spdisplays_yes",
                "spdisplays_connection_type": "spdisplays_internal"
              }]}]
            }""",
            ("pmset", "-g", "systemstate"): (
                "Current System Capabilities are: CPU Graphics Audio Network \n"
                "Current Power State: 4\n"
            ),
            ("defaults", "-currentHost", "read", "com.apple.screensaver"): (
                "{ moduleDict = { moduleName = Ventura; }; }\n"
            ),
            ("ioreg", "-c", "IOHIDSystem"): '"HIDIdleTime" = 1200000000001\n',
        }

        with patch(
            "joulewise.environment.subprocess.run",
            side_effect=lambda command, **kwargs: completed(
                command, outputs[tuple(command)]
            ),
        ):
            snapshot = collect_environment_snapshot()

        self.assertEqual(snapshot["display_power_state"], "any_awake")
        self.assertEqual(snapshot["screensaver_delay_s"], 1200)
        self.assertGreater(snapshot["hid_idle_s"], 1200)
        self.assertIs(snapshot["screensaver_engaged"], True)

    def test_missing_screensaver_defaults_domain_uses_macos_default(self) -> None:
        def fake_run(command, **kwargs):
            if tuple(command) == (
                "defaults",
                "-currentHost",
                "read",
                "com.apple.screensaver",
            ):
                return subprocess.CompletedProcess(
                    command,
                    1,
                    stdout="",
                    stderr=(
                        "Domain com.apple.screensaver does not exist\n"
                    ),
                )
            return successful_fake_run(command, **kwargs)

        with patch("joulewise.environment.subprocess.run", side_effect=fake_run):
            snapshot = collect_environment_snapshot()

        self.assertNotIn("screensaver_defaults", snapshot["errors"])
        self.assertEqual(snapshot["screensaver_delay_s"], 1200)
        self.assertIsNone(snapshot["screensaver_module"])
        self.assertIs(snapshot["screensaver_engaged"], False)

    def test_collect_environment_snapshot_records_present_and_absent_package_versions(self) -> None:
        def fake_version(distribution: str) -> str:
            if distribution == "mlx":
                return "1.2.3"
            raise importlib.metadata.PackageNotFoundError(distribution)

        with patch("joulewise.environment.subprocess.run", side_effect=successful_fake_run):
            with patch("joulewise.environment.importlib_metadata.version", side_effect=fake_version):
                snapshot = collect_environment_snapshot()

        self.assertEqual(
            snapshot["python_packages"]["mlx"],
            {"present": True, "version": "1.2.3"},
        )
        self.assertEqual(
            snapshot["python_packages"]["mlx-lm"],
            {"present": False, "version": None},
        )
        self.assertEqual(
            snapshot["python_packages"]["transformers"],
            {"present": False, "version": None},
        )

    def test_package_records_survive_subprocess_failure_paths(self) -> None:
        def fake_version(distribution: str) -> str:
            if distribution == "mlx":
                return "1.2.3"
            raise importlib.metadata.PackageNotFoundError(distribution)

        def fake_run(command, **kwargs):
            return completed(command, returncode=1)

        with patch("joulewise.environment.subprocess.run", side_effect=fake_run):
            with patch("joulewise.environment.importlib_metadata.version", side_effect=fake_version):
                snapshot = collect_environment_snapshot()

        self.assertEqual(
            snapshot["python_packages"],
            {
                "mlx": {"present": True, "version": "1.2.3"},
                "mlx-lm": {"present": False, "version": None},
                "transformers": {"present": False, "version": None},
            },
        )
        self.assertTrue(snapshot["errors"])

    def test_collect_environment_snapshot_parses_successful_commands(self) -> None:
        outputs = {
            **SUCCESS_OUTPUTS,
            ("pmset", "-g", "batt"): (
                "Now drawing from 'AC Power'\n"
                " -InternalBattery-0\t99%; charged; 0:00 remaining present: true\n"
            ),
            ("pmset", "-g"): " lowpowermode      1\n",
            ("pmset", "-g", "assertions"): (
                "Listed by owning process:\n"
                "   PreventUserIdleDisplaySleep    1\n"
            ),
            ("memory_pressure", "-Q"): "System-wide memory free percentage: 42%\n",
            ("uptime",): (
                "10:00  up 1 day,  3 users, load averages: 1.25 2.50 3.75\n"
            ),
            ("sw_vers",): (
                "ProductName:\t\tmacOS\n"
                "ProductVersion:\t\t15.5\n"
                "BuildVersion:\t\t24F74\n"
            ),
            ("sysctl", "-n", "hw.model", "hw.ncpu", "machdep.cpu.brand_string"): (
                "Mac15,9\n12\nApple M3 Max\n"
            ),
        }

        def fake_run(command, **kwargs):
            return completed(command, outputs[tuple(command)])

        with patch("joulewise.environment.subprocess.run", side_effect=fake_run):
            snapshot = collect_environment_snapshot()

        self.assertEqual(snapshot["power_source"], "AC Power")
        self.assertEqual(snapshot["battery_percent"], 99)
        self.assertEqual(snapshot["battery_state"], "charged")
        self.assertIs(snapshot["low_power_mode"], True)
        self.assertIs(snapshot["display_sleep_prevented"], True)
        self.assertEqual(snapshot["memory_free_percent"], 42.0)
        self.assertEqual(snapshot["memory_pressure_percent"], 58.0)
        self.assertEqual(
            set(snapshot["python_packages"]),
            {"mlx", "mlx-lm", "transformers"},
        )
        for record in snapshot["python_packages"].values():
            self.assertIn("present", record)
            self.assertIn("version", record)
        self.assertEqual(
            snapshot["memory"]["swap_usage"],
            {"total": "1024.00M", "used": "128.00M", "free": "896.00M"},
        )
        self.assertEqual(snapshot["memory"]["pageins"], 2000)
        self.assertEqual(snapshot["memory"]["pageouts"], 30)
        self.assertEqual(snapshot["memory"]["compressor_bytes"], 400 * 4096)
        self.assertEqual(snapshot["memory"]["pages_occupied_by_compressor"], 400)
        self.assertEqual(snapshot["memory"]["pages_stored_in_compressor"], 500)
        self.assertEqual(snapshot["display"]["active_displays"], 0)
        self.assertEqual(snapshot["display"]["status"], "ok")
        self.assertEqual(snapshot["display"]["probe"], "system_profiler_spdisplays")
        self.assertEqual(snapshot["display"]["built_in_display_count"], 0)
        self.assertEqual(snapshot["display"]["external_display_count"], 0)
        self.assertEqual(snapshot["display"]["framebuffer_pipes_total"], 2)
        self.assertEqual(snapshot["display"]["framebuffer_pipes_external_capable"], 1)
        self.assertEqual(snapshot["power"]["adapter_watts"], 96)
        self.assertEqual(snapshot["power"]["adapter_description"], "USB-C Power Adapter")
        self.assertTrue(snapshot["power"]["external_connected"])
        self.assertFalse(snapshot["power"]["is_charging"])
        self.assertTrue(snapshot["power"]["fully_charged"])
        self.assertEqual(snapshot["boot_time_s"], 1700000000)
        self.assertGreaterEqual(snapshot["uptime_s"], 0.0)
        self.assertEqual(snapshot["clock_sync"]["status"], "limited_without_admin")
        self.assertTrue(snapshot["clock_sync"]["timed_running"])
        self.assertEqual(snapshot["load_average_1m"], 1.25)
        self.assertEqual(snapshot["product_version"], "15.5")
        self.assertEqual(snapshot["build_version"], "24F74")
        self.assertEqual(snapshot["hw_model"], "Mac15,9")
        self.assertEqual(snapshot["logical_cpu_count"], 12)
        self.assertEqual(snapshot["cpu_brand"], "Apple M3 Max")
        self.assertEqual(snapshot["errors"], {})

    def test_collect_environment_snapshot_degrades_per_command(self) -> None:
        def fake_run(command, **kwargs):
            key = tuple(command)
            if key == ("pmset", "-g", "batt"):
                raise FileNotFoundError("pmset")
            if key == ("pmset", "-g"):
                return completed(command, " lowpowermode      0\n")
            if key == ("pmset", "-g", "assertions"):
                return completed(command, returncode=1)
            if key == ("memory_pressure", "-Q"):
                raise subprocess.TimeoutExpired(command, timeout=kwargs["timeout"])
            if key == ("vm_stat",):
                return completed(
                    command,
                    "Mach Virtual Memory Statistics: (page size of 4096 bytes)\n"
                    "Pages free:                               1000.\n",
                )
            if key == ("sysctl", "-n", "hw.memsize"):
                return completed(command, "4096000\n")
            if key == ("sysctl", "vm.swapusage"):
                return completed(command, returncode=1)
            if key == ("system_profiler", "SPDisplaysDataType", "-json"):
                return completed(command, returncode=1)
            if key == ("ioreg", "-r", "-c", "IOMobileFramebuffer"):
                return completed(command, "no matching services\n")
            if key == ("ioreg", "-r", "-c", "AppleSmartBattery", "-d", "1"):
                return completed(command, returncode=1)
            if key == ("sysctl", "-n", "kern.boottime"):
                return completed(command, returncode=1)
            if key == ("pgrep", "-x", "timed"):
                return completed(command, returncode=3)
            if key == ("uptime",):
                return completed(command, "unparseable\n")
            if key == ("sw_vers",):
                return completed(command, "ProductVersion:\t15.5\n")
            if key == ("sysctl", "-n", "hw.model", "hw.ncpu", "machdep.cpu.brand_string"):
                return completed(command, returncode=1)
            raise AssertionError(command)

        with patch("joulewise.environment.subprocess.run", side_effect=fake_run):
            snapshot = collect_environment_snapshot()

        self.assertIsNone(snapshot["power_source"])
        self.assertIsNone(snapshot["battery_percent"])
        self.assertIs(snapshot["low_power_mode"], False)
        self.assertIsNone(snapshot["display_sleep_prevented"])
        self.assertEqual(snapshot["memory_free_percent"], 100.0)
        self.assertEqual(snapshot["memory_pressure_percent"], 0.0)
        self.assertIsNone(snapshot["load_average_1m"])
        self.assertEqual(snapshot["product_version"], "15.5")
        self.assertIsNone(snapshot["hw_model"])
        self.assertEqual(snapshot["errors"]["pmset_batt"], "not_found")
        self.assertEqual(snapshot["errors"]["pmset_assertions"], "returncode_1")
        self.assertEqual(snapshot["errors"]["memory_pressure"], "timeout")
        self.assertEqual(snapshot["errors"]["sysctl_vm_swapusage"], "returncode_1")
        self.assertEqual(snapshot["errors"]["system_profiler_spdisplays"], "returncode_1")
        self.assertEqual(snapshot["errors"]["ioreg_framebuffer_pipes"], "parse")
        self.assertEqual(snapshot["display"]["status"], "probe_unavailable")
        self.assertEqual(snapshot["display"]["reason"], "returncode_1")
        self.assertEqual(snapshot["errors"]["ioreg_battery"], "returncode_1")
        self.assertEqual(snapshot["errors"]["sysctl_kern_boottime"], "returncode_1")
        self.assertEqual(snapshot["errors"]["pgrep_timed"], "returncode_3")
        self.assertFalse(snapshot["clock_sync"]["timed_running"])
        self.assertEqual(snapshot["errors"]["uptime"], "parse")
        self.assertEqual(snapshot["errors"]["sysctl_host"], "returncode_1")

    def test_battery_and_sw_vers_garbage_outputs_record_parse_errors(self) -> None:
        outputs = {
            **SUCCESS_OUTPUTS,
            ("pmset", "-g", "batt"): "garbage\n",
            ("pmset", "-g"): "",
            ("pmset", "-g", "assertions"): "",
            ("memory_pressure", "-Q"): "System-wide memory free percentage: 50%\n",
            ("uptime",): "10:00  up 1 day, load averages: 1.0 2.0 3.0\n",
            ("sw_vers",): "garbage\n",
            ("sysctl", "-n", "hw.model", "hw.ncpu", "machdep.cpu.brand_string"): (
                "Mac15,9\n12\nApple M3 Max\n"
            ),
        }

        def fake_run(command, **kwargs):
            return completed(command, outputs[tuple(command)])

        with patch("joulewise.environment.subprocess.run", side_effect=fake_run):
            snapshot = collect_environment_snapshot()

        self.assertIsNone(snapshot["power_source"])
        self.assertIsNone(snapshot["product_version"])
        self.assertEqual(snapshot["errors"]["pmset_batt"], "parse")
        self.assertEqual(snapshot["errors"]["sw_vers"], "parse")
        self.assertNotIn("pmset", snapshot["errors"])
        self.assertNotIn("pmset_assertions", snapshot["errors"])

    def test_live_system_profiler_fixture_records_zero_online_displays(self) -> None:
        outputs = {
            **SUCCESS_OUTPUTS,
            ("system_profiler", "SPDisplaysDataType", "-json"): LIVE_SYSTEM_PROFILER_SP_DISPLAYS_JSON,
            ("ioreg", "-r", "-c", "IOMobileFramebuffer"): "no matching services\n",
        }

        def fake_run(command, **kwargs):
            return completed(command, outputs[tuple(command)])

        with patch("joulewise.environment.subprocess.run", side_effect=fake_run):
            snapshot = collect_environment_snapshot()

        self.assertEqual(snapshot["errors"], {"ioreg_framebuffer_pipes": "parse"})
        self.assertEqual(snapshot["display"]["status"], "ok")
        self.assertEqual(snapshot["display"]["probe"], "system_profiler_spdisplays")
        self.assertIsNone(snapshot["display"]["reason"])
        self.assertEqual(snapshot["display"]["active_displays"], 0)
        self.assertEqual(snapshot["display"]["built_in_display_count"], 0)
        self.assertEqual(snapshot["display"]["external_display_count"], 0)
        self.assertIsNone(snapshot["display"]["framebuffer_pipes_total"])

    def test_system_profiler_display_probe_counts_only_online_displays(self) -> None:
        outputs = {
            **SUCCESS_OUTPUTS,
            ("system_profiler", "SPDisplaysDataType", "-json"): """{
              "SPDisplaysDataType": [
                {
                  "_name": "Apple GPU",
                  "spdisplays_ndrvs": [
                    {
                      "_name": "Built-in Liquid Retina XDR Display",
                      "spdisplays_online": "spdisplays_yes",
                      "spdisplays_connection_type": "spdisplays_internal"
                    },
                    {
                      "_name": "Studio Display",
                      "spdisplays_online": "spdisplays_yes",
                      "spdisplays_connection_type": "spdisplays_displayport"
                    },
                    {
                      "_name": "Offline HDMI",
                      "spdisplays_online": "spdisplays_no",
                      "spdisplays_connection_type": "spdisplays_hdmi"
                    }
                  ]
                }
              ]
            }""",
        }

        def fake_run(command, **kwargs):
            return completed(command, outputs[tuple(command)])

        with patch("joulewise.environment.subprocess.run", side_effect=fake_run):
            snapshot = collect_environment_snapshot()

        self.assertEqual(snapshot["display"]["status"], "ok")
        self.assertEqual(snapshot["display"]["active_displays"], 2)
        self.assertEqual(snapshot["display"]["built_in_display_count"], 1)
        self.assertEqual(snapshot["display"]["external_display_count"], 1)

    def test_system_profiler_display_probe_unavailable_is_fail_soft(self) -> None:
        outputs = {
            **SUCCESS_OUTPUTS,
            ("system_profiler", "SPDisplaysDataType", "-json"): "",
        }

        def fake_run(command, **kwargs):
            if tuple(command) == ("system_profiler", "SPDisplaysDataType", "-json"):
                return completed(command, returncode=1)
            return completed(command, outputs[tuple(command)])

        with patch("joulewise.environment.subprocess.run", side_effect=fake_run):
            snapshot = collect_environment_snapshot()

        self.assertEqual(snapshot["errors"], {"system_profiler_spdisplays": "returncode_1"})
        self.assertEqual(snapshot["display"]["status"], "probe_unavailable")
        self.assertEqual(snapshot["display"]["probe"], "system_profiler_spdisplays")
        self.assertEqual(snapshot["display"]["reason"], "returncode_1")
        self.assertIsNone(snapshot["display"]["active_displays"])
        self.assertEqual(snapshot["display"]["framebuffer_pipes_total"], 2)

    def test_each_primary_command_failure_is_isolated(self) -> None:
        cases = [
            ("not_found", lambda command, kwargs: (_ for _ in ()).throw(FileNotFoundError(command))),
            ("returncode_1", lambda command, kwargs: completed(command, returncode=1)),
            (
                "timeout",
                lambda command, kwargs: (_ for _ in ()).throw(
                    subprocess.TimeoutExpired(command, timeout=kwargs["timeout"])
                ),
            ),
        ]
        for error_key, command in COMMANDS_BY_ERROR_KEY.items():
            for expected_error, failure in cases:
                with self.subTest(command=error_key, failure=expected_error):
                    def fake_run(actual_command, **kwargs):
                        if tuple(actual_command) == command:
                            return failure(actual_command, kwargs)
                        return successful_fake_run(actual_command, **kwargs)

                    with patch("joulewise.environment.subprocess.run", side_effect=fake_run):
                        snapshot = collect_environment_snapshot()

                    self.assertEqual(snapshot["errors"], {error_key: expected_error})
                    for field in COMMAND_FIELDS[error_key]:
                        if field == "display":
                            self.assertIsNone(snapshot["display"]["active_displays"], field)
                        else:
                            self.assertIsNone(snapshot[field], field)
                    untouched_fields = [
                        field
                        for other_key, fields in COMMAND_FIELDS.items()
                        if other_key != error_key
                        for field in fields
                    ]
                    for field in untouched_fields:
                        self.assertIsNotNone(snapshot[field], field)

    def test_parse_sensitive_commands_record_garbage_as_isolated_failure(self) -> None:
        garbage_by_key = {
            "pmset_batt": ("pmset", "-g", "batt"),
            "uptime": ("uptime",),
            "sw_vers": ("sw_vers",),
            "sysctl_host": ("sysctl", "-n", "hw.model", "hw.ncpu", "machdep.cpu.brand_string"),
        }
        for error_key, command in garbage_by_key.items():
            with self.subTest(command=error_key):
                def fake_run(actual_command, **kwargs):
                    if tuple(actual_command) == command:
                        return completed(actual_command, "garbage\n")
                    return successful_fake_run(actual_command, **kwargs)

                with patch("joulewise.environment.subprocess.run", side_effect=fake_run):
                    snapshot = collect_environment_snapshot()

                self.assertEqual(snapshot["errors"], {error_key: "parse"})
                for field in COMMAND_FIELDS[error_key]:
                    if field == "display":
                        self.assertIsNone(snapshot["display"]["active_displays"], field)
                    else:
                        self.assertIsNone(snapshot[field], field)

    def test_all_commands_failing_returns_full_none_snapshot_and_errors(self) -> None:
        def fake_run(command, **kwargs):
            raise FileNotFoundError(command)

        with patch("joulewise.environment.subprocess.run", side_effect=fake_run):
            snapshot = collect_environment_snapshot()

        for key, value in snapshot.items():
            if key == "errors":
                continue
            if key == "thermal_probe_reason":
                self.assertEqual(value, "not_found")
                continue
            if key == "clock_sync":
                self.assertEqual(value["status"], "limited_without_admin")
                self.assertFalse(value["timed_running"])
                self.assertEqual(value["timed_probe_error"], "not_found")
                continue
            if key == "display":
                self.assertEqual(value["status"], "probe_unavailable")
                self.assertEqual(value["reason"], "not_found")
                continue
            if key == "python_packages":
                self.assertEqual(set(value), {"mlx", "mlx-lm", "transformers"})
                continue
            if isinstance(value, dict):
                for nested_value in value.values():
                    self.assertIsNone(nested_value, key)
                continue
            self.assertIsNone(value, key)
        self.assertEqual(
            snapshot["errors"],
            {
                "pmset_batt": "not_found",
                "pmset": "not_found",
                "pmset_assertions": "not_found",
                "pmset_systemstate": "not_found",
                "screensaver_defaults": "not_found",
                "ioreg_hid_idle": "not_found",
                "pmset_therm": "not_found",
                "memory_pressure": "not_found",
                "vm_stat": "not_found",
                "sysctl_hw_memsize": "not_found",
                "sysctl_vm_swapusage": "not_found",
                "system_profiler_spdisplays": "not_found",
                "ioreg_framebuffer_pipes": "not_found",
                "ioreg_battery": "not_found",
                "sysctl_kern_boottime": "not_found",
                "pgrep_timed": "not_found",
                "uptime": "not_found",
                "sw_vers": "not_found",
                "sysctl_host": "not_found",
            },
        )

    def test_unexpected_subprocess_exceptions_never_raise(self) -> None:
        def fake_run(command, **kwargs):
            raise RuntimeError("boom")

        with patch("joulewise.environment.subprocess.run", side_effect=fake_run):
            snapshot = collect_environment_snapshot()

        for key, value in snapshot.items():
            if key == "errors":
                continue
            if key == "thermal_probe_reason":
                self.assertEqual(value, "failed")
                continue
            if key == "clock_sync":
                self.assertEqual(value["status"], "limited_without_admin")
                self.assertFalse(value["timed_running"])
                self.assertEqual(value["timed_probe_error"], "failed")
                continue
            if key == "display":
                self.assertEqual(value["status"], "probe_unavailable")
                self.assertEqual(value["reason"], "failed")
                continue
            if key == "python_packages":
                self.assertEqual(set(value), {"mlx", "mlx-lm", "transformers"})
                continue
            if isinstance(value, dict):
                for nested_value in value.values():
                    self.assertIsNone(nested_value, key)
                continue
            self.assertIsNone(value, key)
        self.assertEqual(
            snapshot["errors"],
            {
                "pmset_batt": "failed",
                "pmset": "failed",
                "pmset_assertions": "failed",
                "pmset_systemstate": "failed",
                "screensaver_defaults": "failed",
                "ioreg_hid_idle": "failed",
                "pmset_therm": "failed",
                "memory_pressure": "failed",
                "vm_stat": "failed",
                "sysctl_hw_memsize": "failed",
                "sysctl_vm_swapusage": "failed",
                "system_profiler_spdisplays": "failed",
                "ioreg_framebuffer_pipes": "failed",
                "ioreg_battery": "failed",
                "sysctl_kern_boottime": "failed",
                "pgrep_timed": "failed",
                "uptime": "failed",
                "sw_vers": "failed",
                "sysctl_host": "failed",
            },
        )

    def test_memory_pressure_failure_uses_vm_stat_fallback_successfully(self) -> None:
        def fake_run(command, **kwargs):
            key = tuple(command)
            if key == ("memory_pressure", "-Q"):
                return completed(command, returncode=1)
            if key == ("vm_stat",):
                return completed(
                    command,
                    "Mach Virtual Memory Statistics: (page size of 4096 bytes)\n"
                    "Pages free:                               1000.\n",
                )
            if key == ("sysctl", "-n", "hw.memsize"):
                return completed(command, "4096000\n")
            return successful_fake_run(command, **kwargs)

        with patch("joulewise.environment.subprocess.run", side_effect=fake_run):
            snapshot = collect_environment_snapshot()

        self.assertEqual(snapshot["memory_free_percent"], 100.0)
        self.assertEqual(snapshot["memory_pressure_percent"], 0.0)
        self.assertEqual(snapshot["errors"], {"memory_pressure": "returncode_1"})

    def test_memory_pressure_fallback_parse_failure_leaves_memory_fields_none(self) -> None:
        def fake_run(command, **kwargs):
            key = tuple(command)
            if key == ("memory_pressure", "-Q"):
                return completed(command, "garbage\n")
            if key == ("vm_stat",):
                return completed(command, "garbage\n")
            if key == ("sysctl", "-n", "hw.memsize"):
                return completed(command, "4096000\n")
            return successful_fake_run(command, **kwargs)

        with patch("joulewise.environment.subprocess.run", side_effect=fake_run):
            snapshot = collect_environment_snapshot()

        self.assertIsNone(snapshot["memory_free_percent"])
        self.assertIsNone(snapshot["memory_pressure_percent"])
        self.assertEqual(
            snapshot["errors"],
            {"memory_pressure": "parse", "vm_stat": "parse"},
        )

    def test_weird_but_real_output_formats_parse(self) -> None:
        outputs = {
            **SUCCESS_OUTPUTS,
            ("pmset", "-g", "batt"): (
                "Now drawing from 'Battery Power'\n"
                " -InternalBattery-0\t77%; present: true\n"
            ),
            ("uptime",): "10:00 up 1 day, 1 user, load average: 0.10 0.20 0.30\n",
            ("sw_vers",): (
                "ProductName:\t\tmacOS\n"
                "ProductVersion:\t\t15.5\n"
                "BuildVersion:\t\t24F74\n"
                "ExtraKey:\t\tignored\n"
            ),
        }

        def fake_run(command, **kwargs):
            return completed(command, outputs[tuple(command)])

        with patch("joulewise.environment.subprocess.run", side_effect=fake_run):
            snapshot = collect_environment_snapshot()

        self.assertEqual(snapshot["power_source"], "Battery Power")
        self.assertEqual(snapshot["battery_percent"], 77)
        self.assertIsNone(snapshot["battery_state"])
        self.assertEqual(snapshot["load_average_1m"], 0.10)
        self.assertEqual(snapshot["load_average_5m"], 0.20)
        self.assertEqual(snapshot["load_average_15m"], 0.30)
        self.assertEqual(snapshot["product_version"], "15.5")
        self.assertEqual(snapshot["display_power_state"], "unknown")
        self.assertEqual(snapshot["screensaver_module"], "Ventura")
        self.assertEqual(snapshot["screensaver_delay_s"], 1200)
        self.assertEqual(snapshot["hid_idle_s"], 5.0)
        self.assertIs(snapshot["screensaver_engaged"], False)
        self.assertEqual(snapshot["thermal_pressure"], "nominal")
        self.assertEqual(snapshot["errors"], {})


class DisplayAsleepDerivationTests(unittest.TestCase):
    """macOS 26 keeps Graphics in systemstate through display-only sleep.

    Live-validated 2026-07-18 (macOS 26.5, Mac15,9): with the display
    verifiably asleep, `pmset -g systemstate` still lists Graphics while
    system_profiler reports `spdisplays_asleep: spdisplays_yes`. Complete
    per-display asleep evidence must win; partial or absent evidence stays
    fail-closed as any_awake.
    """

    LIVE_SYSTEMSTATE = (
        "Current System Capabilities are: CPU Graphics Audio Network \n"
        "Current Power State: 4\n"
    )

    def _derive(self, ndrvs: list[dict]) -> str:
        from joulewise.environment import (
            _parse_pmset_systemstate,
            _parse_system_profiler_displays,
            empty_environment_snapshot,
        )
        import json as _json

        snapshot = empty_environment_snapshot()
        profiler = {"SPDisplaysDataType": [{"spdisplays_ndrvs": ndrvs}]}
        _parse_system_profiler_displays(snapshot, _json.dumps(profiler))
        _parse_pmset_systemstate(snapshot, self.LIVE_SYSTEMSTATE)
        return snapshot["display_power_state"]

    @staticmethod
    def _display(asleep: str | None) -> dict:
        entry = {
            "_name": "Color LCD",
            "spdisplays_online": "spdisplays_yes",
            "spdisplays_connection_type": "spdisplays_internal",
        }
        if asleep is not None:
            entry["spdisplays_asleep"] = asleep
        return entry

    def test_live_asleep_display_wins_over_graphics_capability(self) -> None:
        state = self._derive([self._display("spdisplays_yes")])
        self.assertEqual(state, "all_asleep")

    def test_awake_display_stays_any_awake(self) -> None:
        state = self._derive([self._display("spdisplays_no")])
        self.assertEqual(state, "any_awake")

    def test_absent_asleep_key_fails_closed_any_awake(self) -> None:
        state = self._derive([self._display(None)])
        self.assertEqual(state, "any_awake")

    def test_mixed_displays_one_awake_fails_closed(self) -> None:
        state = self._derive(
            [self._display("spdisplays_yes"), self._display("spdisplays_no")]
        )
        self.assertEqual(state, "any_awake")

    def test_partial_evidence_fails_closed(self) -> None:
        state = self._derive(
            [self._display("spdisplays_yes"), self._display(None)]
        )
        self.assertEqual(state, "any_awake")

    def test_guard_observation_sees_asleep_display(self) -> None:
        """The lightweight guard observation must carry display inventory.

        Live-observed 2026-07-18: without it, every idle admission aborted
        with 'display became or remained awake' on macOS 26.5 because
        systemstate alone always lists Graphics.
        """
        import json as _json
        from joulewise.environment import collect_environment_guard_observation

        profiler = _json.dumps(
            {
                "SPDisplaysDataType": [
                    {"spdisplays_ndrvs": [self._display("spdisplays_yes")]}
                ]
            }
        )

        def fake_run(command, **kwargs):
            class Completed:
                returncode = 0
                stderr = ""

                def __init__(self, stdout):
                    self.stdout = stdout

            if command[:2] == ["system_profiler", "SPDisplaysDataType"]:
                return Completed(profiler)
            if command == ["pmset", "-g", "systemstate"]:
                return Completed(self.LIVE_SYSTEMSTATE)
            if command[:2] == ["defaults", "-currentHost"]:
                return Completed("{\n    idleTime = 0;\n}\n")
            if command[:2] == ["ioreg", "-c"]:
                return Completed('"HIDIdleTime" = 242818958916\n')
            if command[:2] == ["ioreg", "-r"]:
                return Completed(
                    '"ExternalConnected" = Yes\n'
                    '"AdapterDetails" = {"Watts"=140,"Description"='
                    '"140W USB-C Power Adapter"}\n'
                )
            raise AssertionError(command)

        with patch("joulewise.environment.subprocess.run", side_effect=fake_run):
            observation = collect_environment_guard_observation(
                include_adapter_power=True
            )

        self.assertEqual(observation["display_power_state"], "all_asleep")
        self.assertEqual(observation["errors"], {})
        # T0.5 idle-admission core: the guard observation records the adapter
        # wattage surface per admission observation.
        self.assertEqual(observation["power"]["adapter_watts"], 140)
        self.assertEqual(
            observation["power"]["adapter_description"], "140W USB-C Power Adapter"
        )
        self.assertEqual(
            observation["adapter_power_observation"],
            {
                "source": "admission_guard_observation",
                "adapter_watts": 140.0,
                "adapter_description": "140W USB-C Power Adapter",
                "power_source": None,
            },
        )

    def test_guard_observation_profiler_failure_fails_closed(self) -> None:
        from joulewise.environment import collect_environment_guard_observation

        def fake_run(command, **kwargs):
            class Completed:
                returncode = 0
                stderr = ""

                def __init__(self, stdout, returncode=0):
                    self.stdout = stdout
                    self.returncode = returncode

            if command[:2] == ["system_profiler", "SPDisplaysDataType"]:
                return Completed("", returncode=1)
            if command == ["pmset", "-g", "systemstate"]:
                return Completed(self.LIVE_SYSTEMSTATE)
            if command[:2] == ["defaults", "-currentHost"]:
                return Completed("{\n    idleTime = 0;\n}\n")
            if command[:2] == ["ioreg", "-c"]:
                return Completed('"HIDIdleTime" = 242818958916\n')
            if command[:2] == ["ioreg", "-r"]:
                return Completed("", returncode=1)
            raise AssertionError(command)

        with patch("joulewise.environment.subprocess.run", side_effect=fake_run):
            observation = collect_environment_guard_observation(
                include_adapter_power=True
            )

        self.assertEqual(observation["display_power_state"], "any_awake")
        # Adapter capture stays fail-soft: probe failure leaves None fields
        # (the production admission policy fails closed on unknown wattage).
        self.assertIsNone(observation["power"]["adapter_watts"])
        self.assertIsNone(observation["adapter_power_observation"]["adapter_watts"])
        self.assertIn("ioreg_battery", observation["errors"])

    def test_guard_observation_default_skips_adapter_probe(self) -> None:
        """Pre-hookup callers keep the exact legacy probe sequence."""

        from joulewise.environment import collect_environment_guard_observation

        commands: list[list[str]] = []

        def fake_run(command, **kwargs):
            class Completed:
                returncode = 0
                stderr = ""

                def __init__(self, stdout):
                    self.stdout = stdout

            commands.append(list(command))
            if command[:2] == ["ioreg", "-r"]:
                raise AssertionError(
                    "adapter probe must not run without include_adapter_power"
                )
            return Completed("")

        with patch("joulewise.environment.subprocess.run", side_effect=fake_run):
            observation = collect_environment_guard_observation()

        self.assertNotIn(
            ["ioreg", "-r", "-c", "AppleSmartBattery", "-d", "1"], commands
        )
        self.assertIsNone(observation["power"]["adapter_watts"])
        self.assertIsNone(
            observation["adapter_power_observation"]["adapter_watts"]
        )


class PmsetPowerModeParsingTests(unittest.TestCase):
    """The tri-state `powermode` key must feed low_power_mode (D-077 gap).

    A live 2026-07-18 preflight on macOS 26.5 (Mac15,9) failed closed with
    low_power_mode=None because `pmset -g` no longer emits `lowpowermode`;
    the machine reports `powermode 0`. Fixture lines are verbatim live forms.
    """

    def _parse(self, text: str) -> dict:
        from joulewise.environment import _parse_pmset

        snapshot = {"low_power_mode": None}
        _parse_pmset(snapshot, text)
        return snapshot

    def test_live_powermode_zero_is_not_low_power(self) -> None:
        text = (
            "System-wide power settings:\n"
            " Sleep On Power Button 1\n"
            " powernap             1\n"
            " sleep                0 (sleep prevented by caffeinate, powerd)\n"
            " powermode            0\n"
        )
        self.assertIs(self._parse(text)["low_power_mode"], False)

    def test_powermode_one_is_low_power(self) -> None:
        self.assertIs(self._parse(" powermode            1\n")["low_power_mode"], True)

    def test_powermode_two_high_power_is_not_low_power(self) -> None:
        self.assertIs(self._parse(" powermode            2\n")["low_power_mode"], False)

    def test_absent_both_keys_stays_unknown(self) -> None:
        self.assertIsNone(self._parse(" powernap             1\n")["low_power_mode"])

    def test_lowpowermode_key_takes_precedence(self) -> None:
        text = " lowpowermode         1\n powermode            0\n"
        self.assertIs(self._parse(text)["low_power_mode"], True)


if __name__ == "__main__":
    unittest.main()
