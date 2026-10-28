"""L9-REV-1 delta-3 probes at 2ea99f51f: partition by exact metadata bound."""
import contextlib, hashlib, io, json, math, shutil, sys, tempfile
from pathlib import Path
from unittest import mock


def main():
    from joulewise import cli, powermetrics_fiducial as pf, whole_window as ww
    from joulewise.b5_analysis import dry_run as d
    refits = [0]; orig = pf.rederive_detection_from_artifacts
    def counted(*a, **k):
        refits[0] += 1; return orig(*a, **k)
    pf.rederive_detection_from_artifacts = counted
    src = Path(sys.argv[1]); root = Path(tempfile.mkdtemp(prefix='rev1-d3-', dir='/tmp/jwtmp'))
    h = lambda b: hashlib.sha256(b).hexdigest()

    def run(*argv):
        o, e = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(o), contextlib.redirect_stderr(e):
            try: c = cli.main([str(a) for a in argv])
            except SystemExit as x: c = x.code
        return c, o.getvalue(), e.getvalue()

    base = json.loads((src / 'metadata.json').read_bytes())['instrument_calibration']['b_fiducial_s']
    variants = {'orig': base, 'ulp_up': math.nextafter(base, 1.0), 'ulp_down': math.nextafter(base, 0.0),
                'up_5e13': base + 5e-13, 'down_5e13': base - 5e-13}
    bundles = {}
    for name, b in variants.items():
        if name == 'orig':
            bundles[name] = src; continue
        dst = root / name; shutil.copytree(src, dst)
        meta = json.loads((dst / 'metadata.json').read_bytes()); meta['instrument_calibration']['b_fiducial_s'] = b
        (dst / 'metadata.json').write_text(json.dumps(meta))
        # self-consistent stored summary from a real (uncached) reduce
        out = root / (name + '.seed.json'); c, _, _ = run('reduce', dst, '--output', out)
        assert c == 0, name
        (dst / 'summary_metrics.json').write_bytes(out.read_bytes())
        bundles[name] = dst
    R = {'bounds': {k: [repr(v), float(v).hex()] for k, v in variants.items()}}

    def strict_all(order):
        return {n: (lambda r: [r[0], h(r[1].replace(str(bundles[n]), '<B>').encode()), r[2]])(run('validate-bundle', '--strict', bundles[n])) for n in order}

    refits[0] = 0
    R['uncached'] = strict_all(list(variants)); R['uncached_refits'] = refits[0]
    for label, order in (('shared_forward', list(variants)), ('shared_reversed', list(reversed(variants))),
                         ('shared_high_first', ['up_5e13', 'orig', 'down_5e13', 'ulp_up', 'ulp_down'])):
        refits[0] = 0
        with ww.shared_instrument_calibration_physics_cache({}) as store:
            res = strict_all(order); again = strict_all(order)
        R[label] = dict(equal_to_uncached=all(res[n] == R['uncached'][n] for n in order) and res == again,
                        refits=refits[0], partitions=sorted(store), entries=sum(len(v) for v in store.values()),
                        values={k: {kk: repr(vv) for kk, vv in v.items()} for k, v in store.items()})
    # reduce (step 2) is cache-free now: identical with/without run store, refits each time
    refits[0] = 0
    with ww.shared_instrument_calibration_physics_cache({}) as store:
        run('validate-bundle', '--strict', bundles['up_5e13'])
        c, _, _ = run('reduce', bundles['orig'], '--output', root / 'r.json')
    R['reduce_orig_after_high_seed'] = dict(exit=c, equal_stored=(root / 'r.json').read_bytes() == (src / 'summary_metrics.json').read_bytes(),
                                            refits=refits[0])
    # driver step 1 with all five bundles, real step_1 only, both orders
    for label, order in (('driver_forward', list(variants)), ('driver_reversed', list(reversed(variants)))):
        steps = tuple((s, d.step_1 if s == '1' else (lambda st, r, s=s: [st.record(s)])) for s in d.STEP_IDS)
        tmp = root / label; (tmp / 'repo').mkdir(parents=True)
        idx = tmp / 'index.json'; idx.write_bytes(d._canonical({'schema': 'joulewise.b5_window_index.v1', 'attempts': []}))
        with mock.patch.object(d, 'STEPS', steps), mock.patch.object(d.RunState, 'prepare_kept', lambda self, a: 0), \
             mock.patch.object(d.RunState, 'kept_bundles', lambda self: [('alpha', n, bundles[n]) for n in order]), \
             contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            refits[0] = 0
            rc = d.run('blind-dry-run', idx, tmp / 'custody', _test_repo_root=tmp / 'repo', _git=lambda _: 'b' * 40)
        rec = json.loads((tmp / 'custody/dry-run/B5-BLIND-DRY-RUN-RECORD.json').read_bytes())
        R[label] = dict(ret=rc, steps=[(r['step'], r['status'], r['refusal']) for r in rec['steps']][:3], refits=refits[0])
    # observer unavailable (no sys.monitoring): classified code in the record
    steps = tuple((s, lambda st, r, s=s: [st.record(s)]) for s in d.STEP_IDS)
    tmp = root / 'nomon'; (tmp / 'repo').mkdir(parents=True)
    idx = tmp / 'index.json'; idx.write_bytes(d._canonical({'schema': 'joulewise.b5_window_index.v1', 'attempts': []}))
    with mock.patch.object(d, 'STEPS', steps), mock.patch.dict(sys.__dict__, clear=False), \
         contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        del sys.monitoring
        rc = d.run('blind-dry-run', idx, tmp / 'custody', _test_repo_root=tmp / 'repo', _git=lambda _: 'b' * 40)
    rec = json.loads((tmp / 'custody/dry-run/B5-BLIND-DRY-RUN-RECORD.json').read_bytes())
    R['no_monitoring'] = dict(ret=rc, first=[(r['step'], r['status'], r['refusal']) for r in rec['steps']][:2])
    print(json.dumps(R, indent=1))


if __name__ == '__main__':
    main()
