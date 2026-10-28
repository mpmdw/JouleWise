"""One strict_validate_bundles call over two same-evidence bundles whose metadata bounds differ (+5e-13)."""
import json, sys
from pathlib import Path


def main():
    from joulewise import whole_window as ww
    lo, hi = Path(sys.argv[1]), Path(sys.argv[2])
    R = {}
    for label, paths in (('low_then_high', [lo, hi]), ('high_then_low', [hi, lo])):
        res = ww.strict_validate_bundles(paths, workers=1)
        R[label] = [len(p) for p in res]
        if hasattr(ww, 'shared_instrument_calibration_physics_cache'):
            with ww.shared_instrument_calibration_physics_cache({}):
                R[label + '_in_run'] = [len(p) for p in ww.strict_validate_bundles(paths, workers=1)]
                R[label + '_in_run_separate_calls'] = [len(ww.strict_validate_bundles([p], workers=1)[0]) for p in paths]
    print(json.dumps(R))


if __name__ == '__main__':
    main()
