"""Tiny PM records built from scratch; no captured fixture or data reads."""
from datetime import datetime, timedelta
import plistlib


def synthetic_frames(count):
    for i in range(count):
        yield plistlib.dumps(dict(
            elapsed_ns=100_000_000 + (i % 7 - 3) * 1000,
            timestamp=datetime(2026, 1, 1) + timedelta(seconds=i // 10),
            processor=dict(cpu_power=1000., gpu_power=2000., ane_power=0.,
                           cpu_energy=100, gpu_energy=200, ane_energy=0),
            thermal_pressure='Nominal',
            gpu=dict(dvfm_states=[dict(freq=1200, used_ns=50_000_000)]))) + b'\0'
