"""(b) NEG-8 site: _reference_energy_evidence_detail on a NEG-8 member, control vs forced wall deadline."""
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
    m = Path(sys.argv[1])
    R = {'NEG8_MINT_DROP_REASONS': sorted(ww.NEG8_MINT_DROP_REASONS)}
    R['control'] = ww._reference_energy_evidence_detail(m)
    with mock.patch.object(pf, 'time', JumpingClock()):
        R['forced_uncached'] = ww._reference_energy_evidence_detail(m)
    with ww.shared_instrument_calibration_physics_cache({}):
        ww._reference_energy_evidence_detail(m)  # warm
        with mock.patch.object(pf, 'time', JumpingClock()):
            R['forced_warm_cache'] = ww._reference_energy_evidence_detail(m)
    print(json.dumps(R, indent=1, default=str))


if __name__ == '__main__':
    main()
