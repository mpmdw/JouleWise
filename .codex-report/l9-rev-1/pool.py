"""T4: spawn pool inside the shared-cache context (main-guarded)."""
import json, sys, time
from pathlib import Path


def main():
    from joulewise import whole_window as ww
    A, B = Path(sys.argv[1]), Path(sys.argv[2])
    R = {}
    cache = {}
    t = time.monotonic()
    with ww.shared_instrument_calibration_physics_cache(cache):
        pooled = ww.strict_validate_bundles([A, B], workers=2)
        R['pool_wall_s'] = round(time.monotonic() - t, 1)
        R['shared_cache_after_pool'] = list(cache)  # empty => no in-process fallback ran
        R['inproc_with_ctx'] = ww.strict_validate_bundles([A, B], workers=1)
        R['shared_cache_after_inproc'] = list(cache)
    serial = ww.strict_validate_bundles([A, B], workers=1)
    R['pool_results'] = pooled
    R['pool_eq_serial_eq_ctx'] = pooled == serial == R['inproc_with_ctx']
    print(json.dumps(R, indent=1))


if __name__ == '__main__':
    main()
