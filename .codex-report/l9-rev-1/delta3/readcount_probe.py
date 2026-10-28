"""Read counts and authentication records of one V2 session, per code tree (no-difference path)."""
import contextlib, hashlib, io, json, sys
from pathlib import Path


def main():
    from joulewise import cli, whole_window as ww
    from joulewise.authentication_io import V2AuthenticationReadSession
    A, B = Path(sys.argv[1]), Path(sys.argv[2]); out = Path(sys.argv[3]); out.mkdir(exist_ok=True)
    def run(*argv):
        o = io.StringIO()
        with contextlib.redirect_stdout(o), contextlib.redirect_stderr(io.StringIO()):
            try: c = cli.main([str(a) for a in argv])
            except SystemExit as x: c = x.code
        return [c, hashlib.sha256(o.getvalue().replace(str(out), '<OUT>').encode()).hexdigest()]
    def records(session):
        return {str(Path(p).relative_to('/tmp/jwtmp/alpha')) if p.startswith('/tmp/jwtmp/alpha') else p.replace(sys.argv[4], '<TREE>'):
                [r.read_count, r.sha256[:16], r.grammar, r.strict_parse_succeeded] for p, r in sorted(session.records.items())}
    R = {}
    for label, store in (('no_run_store', None), ('run_store', {})):
        ctx = ww.shared_instrument_calibration_physics_cache(store) if store is not None else contextlib.nullcontext()
        with ctx, V2AuthenticationReadSession() as session:
            res = [run('validate-bundle', '--strict', A), run('validate-bundle', '--strict', B),
                   run('reduce', A, '--output', out / (label + '.json')),
                   ww.strict_validate_bundles([A, B], workers=1)]
            R[label] = dict(results=res, records=records(session), reduced=hashlib.sha256((out / (label + '.json')).read_bytes()).hexdigest())
    print(json.dumps(R, indent=1, sort_keys=True))


if __name__ == '__main__':
    main()
