"""Hermetic Darwin ABI probes; no clock-changing or privileged calls."""
import ctypes
from fractions import Fraction
from types import SimpleNamespace
import unittest

from joulewise import kernel_clock as clock

REAL_READ = clock.read_kernel_frequency


def frequency_probe(word=0, *, call_status=0, errno=0):
    def call(pointer):
        value = ctypes.cast(pointer, ctypes.POINTER(clock.Timex)).contents
        assert value.modes == 0
        value.freq = word
        value.status = 64
        ctypes.set_errno(errno)
        return call_status
    return REAL_READ(libc=SimpleNamespace(ntp_adjtime=call))


class KernelClockTests(unittest.TestCase):
    def test_darwin_lp64_layout_and_read_only_output_custody(self):
        self.assertEqual(ctypes.sizeof(clock.Timex), 136)
        self.assertEqual(clock.Timex.freq.offset, 16)
        self.assertEqual(clock.Timex.status.offset, 40)
        self.assertEqual(clock.Timex.shift.offset, 88)
        probe = frequency_probe(-207591, call_status=5)
        self.assertEqual(probe["raw_word"], -207591)
        self.assertEqual(probe["ppm"], -207591 / 65536)
        self.assertEqual(probe["call_status"], 5)
        self.assertEqual(probe["timex_status"], 64)
        self.assertEqual(clock.validate_probe(probe), probe)
        raw = bytes.fromhex(probe["raw_hex"])
        self.assertEqual(clock.Timex.from_buffer_copy(raw).freq, -207591)

    def test_errno_failure_and_inconsistent_custody_refuse(self):
        with self.assertRaisesRegex(ValueError, "read failed"):
            clock.validate_probe(frequency_probe(call_status=-1, errno=1))
        for field, value in (("raw_word", 2), ("ppm", 3.), ("modes", 1),
                             ("call_status", True), ("raw_hex", "00")):
            with self.subTest(field=field), self.assertRaises(ValueError):
                clock.validate_probe(dict(frequency_probe(), **{field: value}))

    def test_signed_drift_and_exact_residual_boundary(self):
        probe = frequency_probe(-207749)  # -3.1700 ppm, quantized kernel word
        span = 3600 * 10**9
        drift = Fraction(probe["raw_word"] * span, 65536 * 10**6)
        self.assertLess(clock.anchor_residual_ns(round(drift), span, probe), 1)
        self.assertGreater(clock.anchor_residual_ns(round(drift) + 6_000_000, span, probe), 5_000_000)
        self.assertEqual(clock.anchor_residual_ns(5_000_000, 1000, frequency_probe()), 5_000_000)

    def test_frequency_gate_budget_and_inclusive_boundary(self):
        gate = clock.frequency_gate(frequency_probe(-207749), 320)
        self.assertTrue(gate["passes"])
        self.assertAlmostEqual(gate["margin_ms"], 5 - 3.6 - .1 - (207749 / 65536 + .25) * 320 / 1000)
        self.assertFalse(clock.frequency_gate(frequency_probe(12 * 65536), 320)["passes"])
        self.assertTrue(clock.frequency_gate(frequency_probe(0), 5200)["passes"])
        self.assertFalse(clock.frequency_gate(frequency_probe(0), 5200.000001)["passes"])
        for span in (None, True, 0, -1, float("nan"), float("inf")):
            with self.subTest(span=span), self.assertRaises((ValueError, TypeError)):
                clock.frequency_gate(frequency_probe(), span)


if __name__ == "__main__":
    unittest.main()
