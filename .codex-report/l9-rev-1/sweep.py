"""Tripwire false-refusal sweep: unforced reduce of every succeeded ALPHA claim member, shared cache on."""
import contextlib, io, json, sys, tempfile
from pathlib import Path


def main():
    from joulewise import cli, whole_window as ww
    from joulewise.b5_analysis import dry_run as d
    root = Path(sys.argv[1]); out = Path(tempfile.mkdtemp(prefix='sweep-', dir='/tmp/jwtmp'))
    R = {'admitted': 0, 'refused': [], 'skipped_not_succeeded': 0, 'reduce_nonzero': []}
    with ww.shared_instrument_calibration_physics_cache({}) as cache:
        for m in sorted(p for p in root.iterdir() if (p / 'summary_metrics.json').is_file()):
            try:
                if json.loads((m / 'summary_metrics.json').read_bytes()).get('status') != 'succeeded':
                    R['skipped_not_succeeded'] += 1; continue
            except ValueError:
                R['skipped_not_succeeded'] += 1; continue
            t = out / (m.name + '.json')
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                try: c = cli.main(['reduce', str(m), '--output', str(t)])
                except SystemExit as e: c = e.code
            if c != 0 or not t.is_file():
                R['reduce_nonzero'].append([m.name, c]); continue
            try:
                d.require_rereduction_matches_stored(m, t); R['admitted'] += 1
            except d.AnalysisRefusal as exc:
                R['refused'].append([m.name, exc.code])
        R['cache_keys'] = len(cache)
    print(json.dumps(R, indent=1))


if __name__ == '__main__':
    main()
