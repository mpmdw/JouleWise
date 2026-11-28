"""Report U3 equality and relative drift without emitting registration values."""

from contextlib import ExitStack
import ctypes
from functools import partial
import inspect
import json
import math
from pathlib import Path
import platform
import sys
from unittest.mock import patch

from joulewise.align.apple import v4_u3
from joulewise.align.apple.v4_registration import digest


BAR = Path(__file__).resolve().parents[1] / 'configs/campaigns/align_v4/registration/u3_bar.json'
PAYLOAD_KEYS = ('schema', 'pairs', 'source_sha256', 'policy', 'prediction', 'oc')
QUADRATURE_FUNCTIONS = ('log', 'lgamma', 'exp', 'erfc', 'log1p', 'expm1')


def relative_difference(stored, recomputed):
    if stored == recomputed:
        return '0'
    if stored == 0:
        return 'inf'
    return f'{abs(stored - recomputed) / abs(stored):.9e}'


def compare(path, stored, recomputed, *, differences_only=False):
    same_type = type(stored) is type(recomputed)
    equal = same_type and stored == recomputed
    if equal and differences_only:
        return
    if same_type and isinstance(stored, dict) and stored.keys() == recomputed.keys():
        for key in sorted(stored):
            compare(f'{path}.{key}', stored[key], recomputed[key], differences_only=differences_only)
    elif same_type and isinstance(stored, list) and len(stored) == len(recomputed):
        for index, (left, right) in enumerate(zip(stored, recomputed)):
            compare(f'{path}[{index}]', left, right, differences_only=differences_only)
    else:
        numeric = same_type and type(stored) in (float, int) and path != 'oc.seed'
        relative = relative_difference(stored, recomputed) if numeric else 'n/a'
        direction = f' recomputed_greater={recomputed > stored}' if numeric and not equal else ''
        print(f'{path} equal={equal} max_relative_difference={relative}{direction}')


def payload_digest(bar):
    payload = {key: bar[key] for key in PAYLOAD_KEYS}
    return digest(v4_u3.canonical(payload).encode())


def replay(bar):
    return v4_u3.derive(bar['pairs'], bar['source_sha256'], bar['policy'])


def report(label, stored, recomputed, *, differences_only=False):
    print(f'comparison={label}')
    for key in ('prediction', 'oc'):
        print(f'{key} equal={stored[key] == recomputed[key]}')
        compare(key, stored[key], recomputed[key], differences_only=differences_only)
    print(f'derivation_sha256 equal={stored["derivation_sha256"] == recomputed["derivation_sha256"]}')


def native_probe(stored):
    native = replay(stored)
    report('native_vs_stored', stored, native)
    pred = stored['prediction']
    n, q = pred['n'], pred['series_quantile_q']
    for key, recomputed in (
        ('pair_false_fail', v4_u3.per_pair_false_fail(q, n)),
        ('series_false_fail', v4_u3.series_false_fail(q, n, pred['series_comparisons'])),
    ):
        compare(f'fixed_stored_q.prediction.{key}', pred[key], recomputed)
    print(f'fixed_stored_q.oc equal={stored["oc"] == v4_u3.operating_characteristics(stored["policy"], pred)}')


def mpfr_probe(stored):
    import gmpy2

    def rounded(fn, arg):
        return float(fn(gmpy2.mpfr(arg)))

    def square(arg):
        return rounded(gmpy2.square, arg)

    replacements = {
        name: partial(rounded, gmpy2.lngamma if name == 'lgamma' else getattr(gmpy2, name))
        for name in QUADRATURE_FUNCTIONS
    }
    print(f'mpfr={gmpy2.mpfr_version()}')
    native = replay(stored)
    with gmpy2.context(gmpy2.ieee(64)):
        half_df = stored['prediction']['df'] / 2
        compare('quadrature_lgamma_native_vs_mpfr', math.lgamma(half_df), replacements['lgamma'](half_df))
        for name, fn in replacements.items():
            with patch.object(math, name, fn):
                pred = v4_u3.prediction(stored['pairs'], stored['policy'])
            print(f'prediction_change=mpfr_{name}_only compared_to=native')
            compare('prediction', native['prediction'], pred, differences_only=True)

        with ExitStack() as stack:
            for name, fn in replacements.items():
                stack.enter_context(patch.object(math, name, fn))
            rounded_quadrature = replay(stored)
            print('comparison=mpfr_quadrature_vs_native')
            compare('prediction', native['prediction'], rounded_quadrature['prediction'], differences_only=True)

            # Keep binary64 rounding at each original operation, including the
            # t3 denominator's exponentiation, which otherwise dispatches to pow.
            # Rebind _oc in memory with the square operation changed at its sole ** site.
            source = inspect.getsource(v4_u3._oc)
            old = 'rng.gauss(0, 1)**2'
            if source.count(old) != 1:
                raise ValueError('expected one t3 square')
            namespace = {**vars(v4_u3), 'square': square}
            exec(source.replace(old, 'square(rng.gauss(0, 1))'), namespace)
            stack.enter_context(patch.object(v4_u3, '_oc', namespace['_oc']))
            # CPython's distribution transforms use math functions imported by name.
            for name in ('log', 'sin', 'cos'):
                stack.enter_context(patch.object(v4_u3.random, f'_{name}', partial(rounded, getattr(gmpy2, name))))
            exact_candidate = replay(stored)
    report('mpfr_candidate_vs_stored', stored, exact_candidate, differences_only=True)


def libc_version():
    if platform.system() != 'Darwin':
        return ' '.join(platform.libc_ver())
    lookup = ctypes.CDLL(None).NSVersionOfRunTimeLibrary
    lookup.argtypes = [ctypes.c_char_p]
    lookup.restype = ctypes.c_int32
    versions = []
    for name in ('System', 'system_c', 'system_m'):
        version = lookup(name.encode())
        if version >= 0:
            versions.append(f'lib{name}={version >> 16}.{version >> 8 & 255}.{version & 255}')
    return ', '.join(versions) or f'Darwin libSystem ({platform.release()})'


def main():
    print(f'python={platform.python_implementation()} {platform.python_version()}')
    print(f'os={platform.system()} {platform.mac_ver()[0] or platform.release()} arch={platform.machine()}')
    print(f'libc={libc_version()}')
    try:
        stored = json.loads(BAR.read_bytes())
        print(f'stored_canonical_digest_matches={payload_digest(stored) == stored["derivation_sha256"]}')
        if sys.argv[1:] == ['--mpfr']:
            mpfr_probe(stored)
        elif not sys.argv[1:]:
            native_probe(stored)
        else:
            return 2
    except Exception as error:
        print(f'diagnostic_error_type={type(error).__name__}')
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
