from __future__ import annotations

import contextlib
import io
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from joulewise import cli
from joulewise.doctor import (
    CHECK_ORDER,
    DoctorProbeFixture,
    _sudo_policy_probe,
    build_doctor_report,
    config_warning_gate,
    exit_code,
    render_human,
    render_json,
)
from joulewise.environment import probe_thermal_pressure


ROOT = Path(__file__).resolve().parents[1]
BASE_CONFIG = ROOT / "configs" / "examples" / "mac_mlx_local.json"


def write_config(root: Path, *, unknown: bool = False) -> Path:
    payload = json.loads(BASE_CONFIG.read_text(encoding="utf-8"))
    payload["run_id"] = "doctor-fixture"
    if unknown:
        payload["workload_profile"]["typo_output_tokens"] = 512
        payload["zzz_unknown"] = True
    path = root / "config.json"
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")
    return path


def fixture(**overrides) -> DoctorProbeFixture:
    values = {
        "python_version": "3.14.0",
        "os_name": "macOS",
        "os_version": "26.0",
        "architecture": "arm64",
        "hardware_model": "Mac15,9",
        "cpu_brand": "Apple M3 Max",
        "logical_cpu_count": 12,
        "package_versions": {
            "joulewise": {"present": True, "version": "0.1.0"},
            "mlx": {"present": True, "version": "0.29.0"},
        },
        "powermetrics_path": "/usr/bin/powermetrics",
        "powermetrics_present": True,
        "powermetrics_executable": True,
        "sudo_probe_ok": True,
        "sudo_probe_reason": None,
        "thermal_pressure": "nominal",
        "thermal_probe_reason": None,
        "backup_destination": "/Volumes/research/JouleWise-backup",
        "backup_present": True,
        "backup_free_bytes": 20 * 1024**3,
        "backup_probe_reason": None,
        "power_source": "AC Power",
        "low_power_mode": False,
        "load_average_1m": 0.25,
        "display_active_count": 0,
        "environment_errors": {},
    }
    values.update(overrides)
    return DoctorProbeFixture(**values)


def checks_by_id(report: dict) -> dict[str, dict]:
    return {check["id"]: check for check in report["checks"]}


class DoctorTests(unittest.TestCase):
    def test_all_checks_use_stable_order_and_fixture_values(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config = write_config(Path(tmp))
            report = build_doctor_report([config], probe=fixture())

        self.assertEqual(report["schema_version"], "joulewise.doctor.v1")
        self.assertEqual([check["id"] for check in report["checks"]], list(CHECK_ORDER))
        self.assertEqual(report["verdict"], "warn")
        checks = checks_by_id(report)
        self.assertEqual(checks["config"]["status"], "pass")
        self.assertEqual(checks["versions_arch"]["details"]["architecture"], "arm64")
        self.assertEqual(
            checks["model_tokenizer_identity"]["details"]["models"][0]["revision"],
            "8b403126fc14f14cfc99bb4cfa72ecbc129ea677",
        )
        self.assertEqual(
            checks["model_tokenizer_identity"]["details"]["tokenizers"][0]["identifier"],
            "/Users/edr/jw_models/mlx-community/Qwen2.5-1.5B-Instruct-4bit",
        )
        self.assertTrue(checks["powermetrics"]["details"]["sudo_noninteractive_policy"])
        self.assertFalse(checks["powermetrics"]["details"]["privileged_command_invoked"])
        self.assertEqual(
            checks["samplers"]["details"]["powermetrics_samplers_requested"],
            ["cpu_power", "gpu_power", "ane_power", "thermal"],
        )
        self.assertEqual(checks["samplers"]["details"]["sampling"][0]["power_hz"], 10.0)
        self.assertEqual(checks["thermal_pressure"]["status"], "pass")
        self.assertEqual(checks["backup_destination"]["status"], "pass")
        self.assertEqual(checks["quiet_machine"]["status"], "warn")

    def test_campaign_config_warning_requires_and_records_acknowledgement(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config = write_config(Path(tmp), unknown=True)
            blocked = config_warning_gate([config], acknowledge=False)
            allowed = config_warning_gate([config], acknowledge=True)

        self.assertEqual(blocked["status"], "fail")
        blocked_ack = blocked["details"]["acknowledgement"]
        self.assertTrue(blocked_ack["required"])
        self.assertFalse(blocked_ack["acknowledged"])
        self.assertEqual(
            [row["path"] for row in blocked_ack["warnings"]],
            ["workload_profile.typo_output_tokens", "zzz_unknown"],
        )
        self.assertEqual(allowed["status"], "warn")
        allowed_ack = allowed["details"]["acknowledgement"]
        self.assertTrue(allowed_ack["acknowledged"])
        self.assertEqual(allowed_ack["mechanism"], "--ack-config-warnings")

    def test_inspection_mode_warns_without_requiring_acknowledgement(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config = write_config(Path(tmp), unknown=True)
            report = build_doctor_report(
                [config], probe=fixture(), mode="inspection"
            )

        config_check = checks_by_id(report)["config"]
        self.assertEqual(config_check["status"], "warn")
        self.assertFalse(config_check["details"]["acknowledgement"]["required"])
        self.assertEqual(exit_code(report), 0)

    def test_required_powermetrics_capability_failure_is_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config = write_config(Path(tmp))
            report = build_doctor_report(
                [config],
                probe=fixture(
                    powermetrics_present=False,
                    powermetrics_executable=False,
                    sudo_probe_ok=False,
                    sudo_probe_reason="powermetrics_not_found",
                ),
                mode="campaign",
            )

        check = checks_by_id(report)["powermetrics"]
        self.assertEqual(check["status"], "fail")
        self.assertTrue(check["details"]["required_by_config"])
        self.assertEqual(report["verdict"], "fail")
        self.assertEqual(exit_code(report), 1)

    def test_thermal_backup_and_quiet_warnings_are_explicit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config = write_config(Path(tmp))
            report = build_doctor_report(
                [config],
                probe=fixture(
                    thermal_pressure="elevated",
                    backup_present=True,
                    backup_free_bytes=1024,
                    power_source="Battery Power",
                    low_power_mode=True,
                    load_average_1m=8.0,
                    display_active_count=2,
                    environment_errors={"uptime": "parse"},
                ),
            )

        checks = checks_by_id(report)
        self.assertEqual(checks["thermal_pressure"]["status"], "warn")
        self.assertEqual(checks["backup_destination"]["status"], "warn")
        quiet = checks["quiet_machine"]["details"]
        self.assertIn("low power mode is enabled", quiet["warnings"])
        self.assertIn("power source is Battery Power", quiet["warnings"])
        self.assertEqual(quiet["environment_probe_errors"], {"uptime": "parse"})

    def test_human_and_json_rendering_are_byte_stable_and_ordered(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config = write_config(Path(tmp))
            report = build_doctor_report([config], probe=fixture())

        human = render_human(report)
        self.assertEqual(human, render_human(report))
        self.assertTrue(human.startswith("JouleWise doctor: mode=inspection verdict=WARN\n"))
        offsets = [human.index(check_id) for check_id in CHECK_ORDER]
        self.assertEqual(offsets, sorted(offsets))
        self.assertIn("model=Qwen2.5-1.5B-Instruct-4bit", human)
        self.assertIn("sudo_noninteractive_policy=True", human)
        self.assertIn("power_hz=10.0", human)
        self.assertIn("free_bytes=21474836480", human)
        self.assertIn("doctor cannot certify machine quietness", human)
        machine = render_json(report)
        self.assertEqual(machine, render_json(report))
        decoded = json.loads(machine)
        self.assertEqual([row["id"] for row in decoded["checks"]], list(CHECK_ORDER))

    def test_sudo_probe_is_inspect_only(self) -> None:
        completed = subprocess.CompletedProcess(
            ["sudo", "-n", "-l", "/usr/bin/powermetrics"], 0, "allowed\n", ""
        )
        with patch("joulewise.doctor.subprocess.run", return_value=completed) as run:
            self.assertEqual(_sudo_policy_probe("/usr/bin/powermetrics", 1.0), (True, None))

        self.assertEqual(
            run.call_args.args[0],
            ["sudo", "-n", "-l", "/usr/bin/powermetrics"],
        )
        self.assertNotIn("--samplers", run.call_args.args[0])

    def test_thermal_probe_uses_unprivileged_pmset_and_fails_soft(self) -> None:
        with patch(
            "joulewise.environment._run",
            return_value=("No thermal warning level has been recorded\n", None),
        ) as run:
            self.assertEqual(probe_thermal_pressure(), ("nominal", None))
        self.assertEqual(run.call_args.args[0], ["pmset", "-g", "therm"])

        with patch("joulewise.environment._run", return_value=(None, "not_found")):
            self.assertEqual(probe_thermal_pressure(), (None, "not_found"))

    def test_cli_doctor_json_uses_report_exit_status(self) -> None:
        report = {
            "schema_version": "joulewise.doctor.v1",
            "mode": "campaign",
            "verdict": "fail",
            "checks": [],
        }
        stdout = io.StringIO()
        with patch("joulewise.cli.doctor_report", return_value=report) as collect:
            with contextlib.redirect_stdout(stdout):
                code = cli.main(
                    [
                        "doctor",
                        "config.json",
                        "--campaign",
                        "--ack-config-warnings",
                        "--backup-destination",
                        "~/backup",
                        "--json",
                    ]
                )

        self.assertEqual(code, 1)
        self.assertEqual(json.loads(stdout.getvalue()), report)
        self.assertEqual(collect.call_args.kwargs["mode"], "campaign")
        self.assertTrue(collect.call_args.kwargs["acknowledge_config_warnings"])
        self.assertEqual(collect.call_args.kwargs["backup_destination"], Path("~/backup").expanduser())


if __name__ == "__main__":
    unittest.main()
