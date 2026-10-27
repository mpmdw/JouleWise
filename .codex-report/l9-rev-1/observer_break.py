"""L9-REV-1 break probes for the fix round's deadline observer (f059286bc)."""
import contextlib, hashlib, io, json, os, sys, threading, time, types
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest import mock


class JumpingClock(types.ModuleType):
    def __init__(self):
        super().__init__('time'); self._now = time.monotonic()
    def monotonic(self):
        self._now += 1000.0; return self._now
    def __getattr__(self, n):
        return getattr(time, n)


def run_cli(cli, *argv):
    o = io.StringIO()
    with contextlib.redirect_stdout(o), contextlib.redirect_stderr(io.StringIO()):
        try: c = cli.main([str(a) for a in argv])
        except SystemExit as e: c = e.code
    return c, o.getvalue()


def steps(cli, m, out):
    c1, o1 = run_cli(cli, 'validate-bundle', '--strict', m)
    t = out / (m.name + '.json'); t.unlink(missing_ok=True)
    c2, _ = run_cli(cli, 'reduce', m, '--output', t)
    return [c1, hashlib.sha256(o1.encode()).hexdigest(), c2, hashlib.sha256(t.read_bytes()).hexdigest()]


def main():
    from joulewise import cli, powermetrics_fiducial as pf, whole_window as ww
    from joulewise.b5_analysis.deadline_observer import observe_wall_deadline
    A, B = Path(sys.argv[1]), Path(sys.argv[2]); out = Path('/tmp/jwtmp/obs'); out.mkdir(exist_ok=True)
    R = {}
    # P1 unforced byte-identity: no observer/no cache vs observer+cache, as in dry_run.run.
    R['P1_plain'] = {m.name: steps(cli, m, out) for m in (A, B)}
    with ww.shared_instrument_calibration_physics_cache({}), observe_wall_deadline() as obs:
        R['P1_observed'] = {m.name: steps(cli, m, out) for m in (A, B)}
        R['P1_firings'] = obs.firings
    R['P1_identical'] = R['P1_plain'] == R['P1_observed']
    # P2 a firing on a worker thread inside the run is counted.
    with observe_wall_deadline() as obs, mock.patch.object(pf, 'time', JumpingClock()):
        t = threading.Thread(target=lambda: run_cli(cli, 'validate-bundle', '--strict', A)); t.start(); t.join()
        with ThreadPoolExecutor(1) as ex:
            ex.submit(run_cli, cli, 'validate-bundle', '--strict', A).result()
        R['P2_thread_firings'] = obs.firings
    # P4 another sys.monitoring tool on the same code object that returns DISABLE does not blind the observer.
    mon = sys.monitoring; other = 4 if mon.get_tool(4) is None else 3
    code = pf.detect_pulses.__code__
    mon.use_tool_id(other, 'rev1-competing-tool')
    mon.register_callback(other, mon.events.PY_RETURN, lambda *_: mon.DISABLE)
    mon.set_local_events(other, code, mon.events.PY_RETURN)
    try:
        with observe_wall_deadline() as obs, mock.patch.object(pf, 'time', JumpingClock()):
            run_cli(cli, 'validate-bundle', '--strict', A)
            R['P4_firings_with_disabling_tool'] = obs.firings
            R['P4_observer_tool_id'] = next((n for n in range(6) if mon.get_tool(n) == 'joulewise-b5-wall-deadline-observer'), None)
    finally:
        mon.set_local_events(other, code, 0); mon.register_callback(other, mon.events.PY_RETURN, None); mon.free_tool_id(other)
    # P3 spawn-pool worker firing (forced through sitecustomize in every process): invisible in-process.
    os.environ['REV1_FORCE_DEADLINE'] = '1'
    with ww.shared_instrument_calibration_physics_cache({}), observe_wall_deadline() as obs:
        pooled = ww.strict_validate_bundles([A, B], workers=2)
        R['P3_pool_problem_counts'] = [len(p) for p in pooled]
        R['P3_pool_firings_seen'] = obs.firings
    os.environ['REV1_FORCE_DEADLINE'] = '0'
    print(json.dumps(R, indent=1))


if __name__ == '__main__':
    main()
