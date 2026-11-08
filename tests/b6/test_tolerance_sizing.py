"""Instrument-scale perturbations distinguish float noise from changed evidence."""
from types import SimpleNamespace
import unittest

from joulewise.b5.harvest import _close
from joulewise.idle_dependence import _metadata_matches


class ToleranceSizingTests(unittest.TestCase):
    def test_energy_noise_below_one_millijoule_is_allowed_but_changes_are_not(self):
        # 1 mJ is 0.1% of the roughly 1 J attribution limit; 2 mJ crosses it.
        self.assertTrue(_close(10, 10 + 0.0005))
        self.assertFalse(_close(10, 10 + 0.002))
        self.assertFalse(_close(float('nan'), 10))
        self.assertFalse(_close(10, None))

    def test_idle_metadata_compares_absolute_power_and_duration_resolution(self):
        baseline = SimpleNamespace(sample_count=300, power_w_mean=0.1, power_w_stddev=0.01, duration_s=30)
        for field in ('mean_w', 'stddev_w', 'duration_s'):
            values = dict(sample_count=300, mean_w=.1, stddev_w=.01, duration_s=30)
            # 1 uW over 30 s is 30 uJ; 1 us is 1/100,000 of a sampler tick.
            self.assertTrue(_metadata_matches(baseline, **{**values, field: values[field] + .5e-6}))
            self.assertFalse(_metadata_matches(baseline, **{**values, field: values[field] + 2e-6}))
        self.assertFalse(_metadata_matches(baseline, sample_count=299, mean_w=.1, stddev_w=.01, duration_s=30))
