"""L9-REV-1 break tests for the shared physics cache. Synthetic ALPHA members only."""
import contextlib, hashlib, io, json, sys, tempfile, threading, time, types
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest import mock

from joulewise import cli, powermetrics_fiducial as pf, whole_window as ww
from joulewise.b5 import harvest
from joulewise.b5_analysis import dry_run as d

A, B = Path(sys.argv[1]), Path(sys.argv[2])
OUT = Path(tempfile.mkdtemp(prefix='rev1-', dir='/tmp/jwtmp'))
EVID = hashlib.sha256((A / 'instrument_calibration/instrument_evidence.json').read_bytes()).hexdigest()
h = lambda b: hashlib.sha256(b).hexdigest()
refits = [0]
_orig = pf.rederive_detection_from_artifacts


def counted(*a, **k):
    refits[0] += 1
    return _orig(*a, **k)


pf.rederive_detection_from_artifacts = counted


class JumpingClock(types.ModuleType):
    def __init__(self):
        super().__init__('time'); self._now = time.monotonic()

    def monotonic(self):
        self._now += 1000.0; return self._now

    def __getattr__(self, n):
        return getattr(time, n)


def run_cli(*argv):
    o, e = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(o), contextlib.redirect_stderr(e):
        try:
            c = cli.main([str(x) for x in argv])
        except SystemExit as x:
            c = x.code
    return c, o.getvalue()


def steps(m, label):
    c1, o1 = run_cli('validate-bundle', '--strict', m)
    t = OUT / f'{label}.{m.name}.reduced.json'
    c2, o2 = run_cli('reduce', m, '--output', t)
    return dict(validate_exit=c1, validate_stdout=h(o1.encode()), reduce_exit=c2,
                reduce_stdout=h(o2.encode()), reduced_json=(h(t.read_bytes()) if t.exists() else None))


R = {}

# T1 cross-member reuse within one run: B uses the fit verified on A.
refits[0] = 0
cache = {}
with ww.shared_instrument_calibration_physics_cache(cache):
    R['T1_cached_A'] = steps(A, 'T1')
    R['T1_cached_B'] = steps(B, 'T1')
R['T1_refits'] = refits[0]
R['T1_cache_keys'] = list(cache)
R['T1_key_is_evidence_sha'] = list(cache) == [EVID]

# T2 deadline forced in step 2 only: uncached vs warm shared cache.
refits[0] = 0
with mock.patch.object(pf, 'time', JumpingClock()):
    c, _ = run_cli('reduce', A, '--output', OUT / 'T2u.json')
R['T2_uncached_forced_reduce'] = dict(exit=c, reduced_json=h((OUT / 'T2u.json').read_bytes()),
    uncertainty=json.loads((OUT / 'T2u.json').read_bytes()).get('energy_uncertainty_status'))
cache = {}
with ww.shared_instrument_calibration_physics_cache(cache):
    run_cli('validate-bundle', '--strict', A)
    with mock.patch.object(pf, 'time', JumpingClock()):
        c, _ = run_cli('reduce', A, '--output', OUT / 'T2c.json')
R['T2_cached_forced_reduce'] = dict(exit=c, reduced_json=h((OUT / 'T2c.json').read_bytes()),
    uncertainty=json.loads((OUT / 'T2c.json').read_bytes()).get('energy_uncertainty_status'))
R['T2_refits'] = refits[0]

# T3 failed fit first, then a verified one, in the same run.
refits[0] = 0
cache = {}
with ww.shared_instrument_calibration_physics_cache(cache):
    with mock.patch.object(pf, 'time', JumpingClock()):
        R['T3_forced_validate_exit'] = run_cli('validate-bundle', '--strict', A)[0]
    R['T3_cache_after_failure'] = dict(cache)
    R['T3_normal_validate_exit'] = run_cli('validate-bundle', '--strict', A)[0]
    R['T3_cache_after_success'] = list(cache)
R['T3_refits'] = refits[0]

# T4 spawn process pool inside the run context.
cache = {}
with ww.shared_instrument_calibration_physics_cache(cache):
    pooled = ww.strict_validate_bundles([A, B], workers=2)
    R['T4_pool_cache_after'] = list(cache)
    R['T4_inproc_with_ctx'] = ww.strict_validate_bundles([A, B], workers=1)
serial = ww.strict_validate_bundles([A, B], workers=1)
R['T4_pool_equals_serial'] = pooled == serial == R['T4_inproc_with_ctx']
R['T4_pool_results'] = pooled

# T5 harvest path inside a run context: harvest's own cache, shared untouched.
cache, own = {}, {}
refits[0] = 0
with ww.shared_instrument_calibration_physics_cache(cache):
    probs = harvest.strict_problems(A, own)
R['T5_harvest_problems'] = probs
R['T5_shared_after'] = list(cache)
R['T5_harvest_own_after'] = list(own)
R['T5_refits'] = refits[0]

# T6 threads inside the context do not see the shared cache (fallback per call).
seen = {}
with ww.shared_instrument_calibration_physics_cache({}) as c6:
    t = threading.Thread(target=lambda: seen.__setitem__('thread', ww.shared_physics_cache())); t.start(); t.join()
    with ThreadPoolExecutor(1) as ex:
        seen['pool_thread'] = ex.submit(ww.shared_physics_cache).result()
R['T6_thread_sees'] = {k: (v is c6) if v is not None else None for k, v in seen.items()}

# T7 driver run that raises / refuses mid-run: scope reset, next run starts empty.
obs = []


def filler(s, r):
    cc = ww.shared_physics_cache(); obs.append((id(cc), dict(cc))); cc['poison'] = 0.0
    return [s.record('0')]


def raiser(s, r):
    raise RuntimeError('boom')


def refuser(s, r):
    raise d.AnalysisRefusal('custody_path_invalid')


with tempfile.TemporaryDirectory(dir='/tmp/jwtmp') as tmp:
    root = Path(tmp); (root / 'repo').mkdir()
    index = root / 'index.json'
    index.write_bytes(d._canonical({'schema': 'joulewise.b5_window_index.v1', 'attempts': []}))
    outcomes = []
    for name, second in (('r1', raiser), ('r2', refuser), ('r3', raiser)):
        with mock.patch.object(d, 'STEPS', [('0', filler), ('1', second)]), \
             contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            try:
                d.run('blind-dry-run', index, root / name, _test_repo_root=root / 'repo', _git=lambda r: 'b' * 40)
                outcomes.append('returned')
            except BaseException as exc:  # noqa: BLE001
                outcomes.append(type(exc).__name__)
        outcomes.append(('after', ww.shared_physics_cache()))
R['T7_outcomes'] = outcomes
R['T7_each_run_starts_empty'] = [o[1] for o in obs]
R['T7_distinct_dicts'] = len({o[0] for o in obs}) == len(obs)
print(json.dumps(R, indent=1, sort_keys=True, default=str))
