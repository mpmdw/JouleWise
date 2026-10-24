"""BYTES device-counter dropout checks; host jitter is not a missing sample."""
import unittest

from joulewise.external import km003c_parse as kp


class MeterGapTests(unittest.TestCase):
    def stream(self, device):
        samples = kp.Samples(device, [1] * len(device), [10] * len(device),
                             [0] * len(device), 0, 20)
        fit = kp.Fit(0, 1_000_000, {})
        return kp.Stream({}, {}, [], [], samples, fit,
                         [fit.host_ns(d) for d in device], samples.watts, [], [])

    def test_missing_counter_at_each_edge_and_half_open_end(self):
        stream = self.stream([0, 20, 60, 80, 100])  # counter 40 is missing
        for span, missing in (((40_000_000, 60_000_000), True),
                              ((20_000_000, 41_000_000), True),
                              ((20_000_000, 40_000_000), False),
                              ((40_000_001, 80_000_000), False),
                              ((60_000_000, 100_000_000), False)):
            with self.subTest(span=span):
                self.assertIs(kp.span_has_drops(stream, *span), missing)

    def test_one_missing_counter_and_host_time_jitter(self):
        stream = self.stream(list(range(0, 101, 20)))
        stream.host_ns[2] += 1_000_000
        self.assertFalse(kp.span_has_drops(stream, 0, 100_000_000))
        stream.samples.dev_ms.pop(3)
        stream.host_ns.pop(3)
        self.assertTrue(kp.span_has_drops(stream, 0, 100_000_000))

    def test_integrate_has_no_device_counter_and_remains_a_mean(self):
        # The low-level integrator also serves battery polls, whose intervals
        # vary. BYTES checks the device counter before invoking it.
        self.assertEqual(kp.integrate([0, 20_000_000, 80_000_000], [10, 20, 30],
                                     0, 100_000_000), (2.0, 3))


if __name__ == "__main__":
    unittest.main()
