"""(b) NEG-8 replay strict_invalid callback (sources_replay.py:251) on a runs_bound reference, control vs forced."""
import json, sys, time, types
from pathlib import Path
from unittest import mock


class JumpingClock(types.ModuleType):
    def __init__(self):
        super().__init__('time'); self._now = time.monotonic()
    def monotonic(self):
        self._now += 1000.0; return self._now
    def __getattr__(self, n):
        return getattr(time, n)


def main():
    from joulewise import powermetrics_fiducial as pf, whole_window as ww
    from joulewise.b5_analysis.sources_replay import neg8_reference_strict_invalid
    ref = Path(sys.argv[1]); R = {}
    R['control_invalid'] = neg8_reference_strict_invalid(ref).invalid
    with mock.patch.object(pf, 'time', JumpingClock()):
        R['forced_uncached_invalid'] = neg8_reference_strict_invalid(ref).invalid
    with ww.shared_instrument_calibration_physics_cache({}):
        neg8_reference_strict_invalid(ref)
        with mock.patch.object(pf, 'time', JumpingClock()):
            R['forced_warm_cache_invalid'] = neg8_reference_strict_invalid(ref).invalid
    print(json.dumps(R, indent=1))


if __name__ == '__main__':
    main()
