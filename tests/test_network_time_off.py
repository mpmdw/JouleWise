import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

from joulewise.hazards import network_time as nt


def receipt(**changes):
    return {"schema": nt.SCHEMA, "argv": list(nt.OFF_ARGV), "exit_code": 0,
            "stdout": nt.EXPECTED_STDOUT, "stderr": "Error:-99\n", "error": None,
            "epoch_s": 1000., "monotonic_s": 10., "boot_id": "boot",
            "plan_id": "plan", "window_id": "window", **changes}


class NetworkTimeOffTests(unittest.TestCase):
    def save(self, root, result=None, **kwargs):
        runner = mock.Mock(return_value=result or subprocess.CompletedProcess(
            nt.OFF_ARGV, 0, nt.EXPECTED_STDOUT.encode(), b"Error:-99\n"))
        value = nt.set_network_time_off(Path(root) / nt.RECEIPT_BASENAME,
            "plan", "window", runner=runner, boot_probe=lambda: "boot",
            clock=lambda: {"epoch_s": 1000., "monotonic_s": 10.}, **kwargs)
        runner.assert_called_once_with(nt.OFF_ARGV, timeout=30)
        return value

    def test_exact_off_and_diagnostic_saved_separately_write_once(self):
        with tempfile.TemporaryDirectory() as root:
            value = self.save(root)
            path = Path(root) / nt.RECEIPT_BASENAME
            self.assertEqual(nt.read_receipt(path), value)
            with self.assertRaises(FileExistsError):
                self.save(root)
            self.assertEqual(nt.read_receipt(path), value)

    def test_already_off_wording_admitted(self):
        # C1 2026-09-30: the Mac was already Off and macOS said so in other
        # words; the window was refused at t0.  Both wordings end Off.
        for stdout in ("Network Time is already off.\n", "setUsingNetworkTime: Off\n",
                       "setUsingNetworkTime: off\n", "setUsingNetworkTime: Off",
                       "  network time is ALREADY off \n"):
            with self.subTest(stdout=stdout), tempfile.TemporaryDirectory() as root:
                self.assertEqual(self.save(root, subprocess.CompletedProcess(
                    nt.OFF_ARGV, 0, stdout.encode(), b""))["stdout"], stdout)

    def test_c1_refused_receipt_is_now_admitted(self):
        c1 = receipt(stdout="Network Time is already off.\n", stderr="")
        self.assertIs(nt.admit(c1), c1)

    def test_nonzero_and_wrong_stdout_saved_but_refused(self):
        for code, stdout in ((1, nt.EXPECTED_STDOUT), (1, "Network Time is already off.\n"),
                             (0, "setUsingNetworkTime: On\n"), (0, "Network Time is already on.\n"),
                             (0, ""), (0, "You need administrator access to run this tool... exiting!\n"),
                             (0, "setUsingNetworkTime: Off\nsetUsingNetworkTime: On\n"),
                             (0, "Network Time: Off\n"), (0, "not setUsingNetworkTime: Off\n")):
            with self.subTest(code=code, stdout=stdout), tempfile.TemporaryDirectory() as root:
                with self.assertRaises(ValueError):
                    self.save(root, subprocess.CompletedProcess(nt.OFF_ARGV, code, stdout, ""))
                self.assertEqual(json.loads((Path(root) / nt.RECEIPT_BASENAME).read_bytes())["stdout"], stdout)

    def test_timeout_receipt_preserves_partial_outputs(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / nt.RECEIPT_BASENAME
            with self.assertRaises(ValueError):
                nt.set_network_time_off(path, "plan", "window",
                    runner=mock.Mock(side_effect=subprocess.TimeoutExpired(nt.OFF_ARGV, 30,
                        output=b"partial", stderr=b"diagnostic")), boot_probe=lambda: "boot")
            value = json.loads(path.read_bytes())
            self.assertEqual((value["stdout"], value["stderr"]), ("partial", "diagnostic"))

    def test_missing_receipt_refused(self):
        with tempfile.TemporaryDirectory() as root:
            with self.assertRaises(FileNotFoundError):
                nt.read_receipt(Path(root) / "missing")
        with self.assertRaises(ValueError):
            nt.seconds_since_receipt(None, {})

    def test_both_clocks_and_boot_required(self):
        now = {"epoch_s": 1600., "monotonic_s": 610., "boot_id": "boot"}
        self.assertEqual(nt.seconds_since_receipt(receipt(), now), 600)
        for change in ({"epoch_s": 1599.99}, {"monotonic_s": 609.99},
                       {"boot_id": "other"}, {"epoch_s": float("nan")}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                nt.seconds_since_receipt(receipt(), {**now, **change})

    def test_raw_uppercase_sysctl_boot_matches_lowercased_receipt(self):
        # macOS prints kern.bootsessionuuid in upper case; the sampler passes it raw.
        uuid = "CD5B815A-0F3E-4C2A-9B1D-7E6F5A4B3C2D"
        stored = {**receipt(), "boot_id": uuid.lower()}
        now = {"epoch_s": 1600., "monotonic_s": 610., "boot_id": uuid}
        self.assertEqual(nt.seconds_since_receipt(stored, now), 600)
        with self.assertRaises(ValueError):
            nt.seconds_since_receipt(stored, {**now, "boot_id": uuid.replace("CD5B", "CD5C")})

    def test_identity_and_symlink_refused(self):
        with tempfile.TemporaryDirectory() as root:
            self.save(root)
            path = Path(root) / nt.RECEIPT_BASENAME
            with self.assertRaises(ValueError):
                nt.read_receipt(path, plan_id="other")
            link = Path(root) / "link"
            link.symlink_to(path)
            with self.assertRaises(ValueError):
                nt.read_receipt(link)


class WiredAdmissionTests(unittest.TestCase):
    def test_night_derivation_refuses_failed_receipt_before_launch(self):
        from tests.test_run_night import NightDriverTests
        fixture = NightDriverTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        self.addCleanup(fixture.tearDown)
        fixture.off_admission_mock.side_effect = ValueError("missing admitted OFF receipt")
        with mock.patch.object(fixture.driver, "_run_chain_once") as launch:
            fixture.driver.run_night(fixture.plan_path)
        launch.assert_not_called()
        fixture.off_admission_mock.assert_called_once()




class ArmResyncTests(unittest.TestCase):
    def context(self, root):
        from types import SimpleNamespace
        paths = {}
        for name in ("RUNS_ROOT", "BOUND_RUNS_ROOT", "CUSTODY_ROOT", "QUARANTINE_ROOT"):
            path = root / name
            path.mkdir()
            paths[name] = str(path)
        inputs = root / "inputs"
        inputs.mkdir()
        return SimpleNamespace(input_root=inputs, repository=root, plan_id="plan",
            boot_session_id="aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
            assignments={**paths, "WINDOW_ID": "window"})




class SingleComparatorGuardTests(unittest.TestCase):
    """No module may compare the OFF stdout to a literal again (C1 refusal)."""

    def test_no_raw_equality_against_off_wording(self):
        import re
        root = Path(__file__).resolve().parents[1]
        pattern = re.compile(r"[!=]=\s*(?:\w+\.)*(?:EXPECTED_NETWORK_TIME_OFF_STDOUT|EXPECTED_STDOUT)\b"
                             r"|(?:EXPECTED_NETWORK_TIME_OFF_STDOUT|EXPECTED_STDOUT)\s*[!=]="
                             r"|setUsingNetworkTime: Off\\n\"\s*[!=]=|[!=]=\s*\"setUsingNetworkTime")
        offenders = [f"{path.relative_to(root)}:{number}"
                     for directory in ("joulewise", "scripts")
                     for path in sorted((root / directory).rglob("*.py"))
                     for number, line in enumerate(path.read_text().splitlines(), 1)
                     if pattern.search(line)]
        self.assertEqual(offenders, [], "use network_time_off.off_stdout_admitted")
