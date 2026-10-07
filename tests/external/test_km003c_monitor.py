"""scripts/km003c_monitor.py and joulewise.external.km003c_usb: the protocol helpers,
the absent path (exit 0, an "absent" header and a trailer), and a real-device
smoke run that is skipped unless the meter is plugged in."""
from __future__ import annotations

import json
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

from joulewise.external import km003c_parse as kp
from joulewise.external import km003c_usb as usb
from tests import child_guard

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "km003c_monitor.py"


def meter_enumerated() -> bool:
    if sys.platform != "darwin":
        return False
    try:
        listing = subprocess.run(["/usr/sbin/ioreg", "-p", "IOUSB", "-l", "-w0"], capture_output=True,
                                 timeout=10).stdout
    except (OSError, subprocess.TimeoutExpired):
        return False
    return f'"idVendor" = {usb.VID}'.encode() in listing


def lines(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


class ProtocolTests(unittest.TestCase):
    @unittest.skipUnless(sys.platform == "darwin", "CommonCrypto is macOS only")
    def test_aes_matches_the_fips_197_vector(self):
        key = bytes(range(16))
        plain = bytes.fromhex("00112233445566778899aabbccddeeff")
        cipher = usb.aes_encrypt(key, plain)
        self.assertEqual(cipher.hex(), "69c4e0d86a7b0430d8cdb78070b4c55a")
        self.assertEqual(usb.aes_decrypt(key, cipher), plain)
        with self.assertRaises(ValueError):
            usb.aes_encrypt(key, b"short")

    def test_control_word_layout(self):
        # StartGraph at 50 SPS is [0x0E, tid, rate_index << 1, 0x00] on the wire.
        self.assertEqual(usb.control(0x0E, 7, 2), bytes([0x0E, 7, 0x04, 0x00]))
        self.assertEqual(usb.control(0x0C, 1, 0x0002), bytes([0x0C, 1, 0x04, 0x00]))

    def test_put_data_parsing(self):
        empty = bytes([0x41, 3, 0, 0])
        self.assertEqual(usb.parse_put_data(empty), (b"", 0, True))
        payload = bytes(range(40))
        ext = (2 << 16) | 0x0002
        good = bytes([0x41, 3, 0, 0]) + ext.to_bytes(4, "little") + payload
        self.assertEqual(usb.parse_put_data(good), (payload, 2, True))
        self.assertFalse(usb.parse_put_data(good[:-1])[2])                      # short payload
        wrong = bytes([0x41, 3, 0, 0]) + ((2 << 16) | 0x0001).to_bytes(4, "little") + payload
        self.assertFalse(usb.parse_put_data(wrong)[2])                          # not AdcQueue
        self.assertFalse(usb.parse_put_data(bytes([0x06, 3, 0, 0]))[2])         # Reject
        self.assertFalse(usb.parse_put_data(good + bytes(20))[2])              # surplus sample bytes

    def test_a_partial_bulk_write_is_an_error(self):
        """Review F5: libusb returning success with fewer bytes sent than the command."""

        class Lib:
            def libusb_bulk_transfer(self, handle, endpoint, data, length, transferred, timeout):
                transferred._obj.value = 1
                return 0

        device = object.__new__(usb.UsbDevice)
        device.lib, device.handle = Lib(), object()
        device.transferred = __import__("ctypes").c_int(0)
        with self.assertRaises(usb.UsbError):
            device.write(bytes([0x0C, 1, 0x04, 0x00]))


class CleanupTests(unittest.TestCase):
    """Review F2: a write that fails after the meter started still releases it."""

    def test_a_full_disk_at_the_header_still_stops_and_releases_the_meter(self):
        import importlib.util
        from unittest import mock

        spec = importlib.util.spec_from_file_location("km003c_monitor_cleanup", SCRIPT)
        script = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(script)
        calls: list[str] = []

        class FakeUsb:
            def close(self):
                calls.append("usb.close")

        class FakeMeter:
            usb = FakeUsb()

            def stop_graph(self):
                calls.append("stop_graph")

            def disconnect(self):
                calls.append("disconnect")

        class FullDisk:
            def write(self, _text):
                raise OSError(28, "No space left on device")

            def flush(self):
                pass

            def fileno(self):
                return 0

            def close(self):
                calls.append("out.close")

        handlers = {sig: signal.getsignal(sig) for sig in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP)}
        self.addCleanup(lambda: [signal.signal(sig, handler) for sig, handler in handlers.items()])
        with mock.patch.object(script, "init_meter", lambda *a, **k: (FakeMeter(), {})), \
                mock.patch.object(script, "open", lambda *a, **k: FullDisk(), create=True):
            with self.assertRaises(OSError):
                script.main(["--out", "/nonexistent/never-written.jsonl"])
        self.assertEqual(calls, ["stop_graph", "disconnect", "usb.close", "out.close"])


class InitCancellationTests(unittest.TestCase):
    """Review F6: a SIGTERM during initialisation ends the retries."""

    def test_stopping_between_attempts_ends_init_without_retry_sleeps(self):
        import importlib.util
        from types import SimpleNamespace
        from unittest import mock

        spec = importlib.util.spec_from_file_location("km003c_monitor_under_test", SCRIPT)
        script = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(script)
        attempts = []

        def failing_device(*_args, **_kwargs):
            attempts.append(1)
            raise usb.UsbError("open", -4)

        stop = {"now": False}
        args = SimpleNamespace(libusb=None, init_attempts=4, vid=usb.VID, pid=usb.PID, reset=False, rate=2)
        errors: list[str] = []
        with mock.patch.object(script.usb, "load_libusb", lambda path: object()), \
                mock.patch.object(script.usb, "UsbDevice", failing_device), \
                mock.patch.object(script.time, "sleep") as sleep:
            def stopping():
                return stop["now"]

            original = failing_device

            def device_then_signal(*a, **k):
                stop["now"] = True  # the SIGTERM handler ran during attempt 1
                return original(*a, **k)

            with mock.patch.object(script.usb, "UsbDevice", device_then_signal):
                with self.assertRaises(usb.MeterAbsent) as caught:
                    script.init_meter(args, errors, stopping=stopping)
        self.assertEqual(len(attempts), 1)
        sleep.assert_not_called()
        self.assertIn("stopped by a signal", str(caught.exception))


class AbsentMeterTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def run_script(self, *extra: str, out: Path | None = None) -> tuple[subprocess.CompletedProcess, Path]:
        out = out or Path(self.tmp.name) / "stream.jsonl"
        done = subprocess.run([sys.executable, str(SCRIPT), "--out", str(out), "--init-attempts", "1", *extra],
                              capture_output=True, timeout=60)
        return done, out

    def assert_absent(self, done: subprocess.CompletedProcess, out: Path, reason_part: str) -> None:
        self.assertEqual(done.returncode, 0, done.stderr)
        header, trailer = lines(out)
        self.assertEqual(header["k"], "h")
        self.assertEqual(header["status"], "absent")
        self.assertEqual(header["schema"], "joulewise.km003c_stream.v1")
        self.assertIn(reason_part, json.dumps(header))
        self.assertEqual(trailer["k"], "t")
        self.assertEqual(trailer["stop_reason"], "absent")
        self.assertEqual(trailer["polls"], 0)
        self.assertEqual([f["code"] for f in kp.flags(kp.parse(out))], ["meter.absent"])

    def test_no_such_device_exits_zero_with_an_absent_header(self):
        done, out = self.run_script("--pid", "0xfffe")
        self.assert_absent(done, out, "fffe")

    def test_missing_libusb_exits_zero_with_an_absent_header(self):
        done, out = self.run_script("--libusb", "/nonexistent/libusb-1.0.dylib")
        self.assert_absent(done, out, "libusb-1.0 not found")

    def test_unwritable_or_existing_out_is_a_usage_error(self):
        done, _ = self.run_script(out=Path(self.tmp.name) / "missing-dir" / "s.jsonl")
        self.assertEqual(done.returncode, 2)
        existing = Path(self.tmp.name) / "exists.jsonl"
        existing.write_text("keep\n")
        done, _ = self.run_script("--pid", "0xfffe", out=existing)
        self.assertEqual(done.returncode, 2)
        self.assertEqual(existing.read_text(), "keep\n")


@unittest.skipUnless(meter_enumerated(), "POWER-Z KM003C not on the USB bus")
class RealMeterSmokeTests(unittest.TestCase):
    def test_streams_then_stops_cleanly_on_sigterm(self):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory) / "stream.jsonl"
            process = subprocess.Popen([sys.executable, str(SCRIPT), "--out", str(out)],
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            child_guard.own(self, process)   # a failed wait or assertion must not leave the meter program running
            time.sleep(6.0)
            process.send_signal(signal.SIGTERM)
            _stdout, stderr = process.communicate(timeout=30)
            self.assertEqual(process.returncode, 0, stderr)
            stream = kp.parse(out)
            self.assertEqual(stream.header["status"], "streaming", stream.header)
            self.assertGreaterEqual(stream.header["auth_level"], 1)
            self.assertEqual(len(bytes.fromhex(stream.header["hardware_id"])), 12)
            self.assertIsNotNone(stream.header["firmware_version"])
            self.assertGreaterEqual(len(stream.host_ns), 200)
            self.assertTrue(all(b["rx"] > a["rx"] for a, b in zip(stream.batches, stream.batches[1:])))
            self.assertTrue(all(b["tx"] < b["rx"] for b in stream.batches))
            self.assertTrue(all(v.get("B0AC") is not None and v.get("PDTR") is not None
                                for v in stream.smc))
            self.assertEqual(stream.trailer["stop_reason"], f"signal {int(signal.SIGTERM)}")
            self.assertEqual(stream.trailer["bad"] + stream.trailer["usb_errors"], 0)
            self.assertEqual(stream.samples.duplicates, 0)
            self.assertEqual(kp.drops(stream.samples)["dropped"], 0)
            offset = kp.raw_offset_ns(stream)
            self.assertIsNotNone(offset)
            self.assertLess(abs(offset - (time.clock_gettime_ns(time.CLOCK_MONOTONIC_RAW) - time.monotonic_ns())),
                            1_000_000)


# Test hygiene (2026-10-07): a test or class in this module that leaves a child process running
# is reported as failed, and the child is stopped (tests/child_guard.py).
child_guard.guard_test_classes(globals())


if __name__ == "__main__":
    unittest.main()
