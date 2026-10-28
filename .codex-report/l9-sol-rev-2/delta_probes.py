"""Synthetic delta probes; baseline modules are loaded from Git, without checkout writes."""
import contextlib
import dataclasses
import hashlib
import importlib.abc
import importlib.util
import io
import itertools
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
from unittest import mock


class GitModules(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    names = {'joulewise.whole_window', 'joulewise.cli',
             'joulewise.b5_analysis.bracket', 'joulewise.b5_analysis.deadline_observer'}

    def find_spec(self, fullname, path, target=None):
        if fullname in self.names:
            return importlib.util.spec_from_loader(fullname, self)

    def create_module(self, spec):
        return None

    def exec_module(self, module):
        name = module.__name__.replace('.', '/') + '.py'
        source = subprocess.check_output(['git', 'show', 'f059286bc:' + name])
        module.__file__ = str(Path(name).resolve())
        exec(compile(source, module.__file__, 'exec'), module.__dict__)


if '--baseline' in sys.argv:
    sys.meta_path.insert(0, GitModules())

from joulewise import cli, whole_window as ww, powermetrics_fiducial as pf
from joulewise.authentication_io import V2AuthenticationReadSession
from tests.b5_analysis.test_shared_physics_cache import ARCHIVE, MEMBER


def invoke(*args):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            result = cli.main([str(arg) for arg in args])
        except SystemExit as exc:
            result = exc.code
    return result, out.getvalue(), err.getvalue()


def extract(root):
    with tarfile.open(ARCHIVE) as blob:
        blob.extractall(root, members=[m for m in blob.getmembers() if m.name.startswith(MEMBER)], filter='data')
    return root / MEMBER


def boundaries():
    with tempfile.TemporaryDirectory(prefix='sol-boundaries-') as tmp:
        root = Path(tmp)
        member = extract(root)
        calls = []
        original = pf.rederive_detection_from_artifacts

        def counted(*args, **kwargs):
            value = original(*args, **kwargs)
            calls.append(value)
            return value

        with mock.patch.object(pf, 'rederive_detection_from_artifacts', counted):
            assert invoke('reduce', member, '--output', root/'original.json')[0] == 0
            fresh = calls[-1].b_fiducial_s
            declared = json.loads((member/'metadata.json').read_bytes())['instrument_calibration']['b_fiducial_s']
            print('fresh/declared:', repr(fresh), repr(declared), flush=True)
            values = (math.nextafter(fresh, -math.inf), fresh, math.nextafter(fresh, math.inf))
            bundles, plain = [], []
            for n, value in enumerate(values):
                target = root/('bundle-'+str(n))
                shutil.copytree(member, target)
                metadata = json.loads((target/'metadata.json').read_bytes())
                metadata['instrument_calibration']['b_fiducial_s'] = value
                (target/'metadata.json').write_text(json.dumps(metadata))
                output = root/('plain-'+str(n)+'.json')
                assert invoke('reduce', target, '--output', output)[0] == 0
                (target/'summary_metrics.json').write_bytes(output.read_bytes())
                plain.append(invoke('validate-bundle', '--strict', target))
                assert plain[-1][0] == 0, plain[-1]
                bundles.append(target)
            evidence = {hashlib.sha256((b/'instrument_calibration/instrument_evidence.json').read_bytes()).hexdigest() for b in bundles}
            assert len(evidence) == 1
            print('bounds hex:', [v.hex() for v in values], 'one evidence hash:', next(iter(evidence)), flush=True)
            for order in ((0,1,2), (2,1,0), (1,2,0)):
                before = len(calls)
                with ww.shared_instrument_calibration_physics_cache({}) as store:
                    for n in order + tuple(reversed(order)):
                        observed = invoke('validate-bundle', '--strict', bundles[n])
                        assert observed == plain[n], (order, n, observed, plain[n])
                    assert len(store) == 3, store
                print('order', order, 'six strict outputs identical; partitions', len(store), 'refits', len(calls)-before, flush=True)
            with ww.shared_instrument_calibration_physics_cache({}):
                for n in (2,1,0):
                    output = root/('shared-'+str(n)+'.json')
                    assert invoke('reduce', bundles[n], '--output', output)[0] == 0
                    assert output.read_bytes() == (root/('plain-'+str(n)+'.json')).read_bytes()
            # Identical binary values serialized differently share a partition.
            assert ww._effective_bound_partition({'instrument_calibration': {'b_fiducial_s': fresh}}) == fresh.hex()
            for invalid in (None, True, float('nan'), float('inf'), 10**400):
                assert ww._effective_bound_partition({'instrument_calibration': {'b_fiducial_s': invalid}}) is None
            print('PASS: last-ULP separation, fresh-bound equality, reversed orders, three bundles, exact reduction bytes, invalid keys', flush=True)


def authentication(root):
    member = root / MEMBER
    if not member.exists():
        extract(root)
    result = {}
    for kind in ('strict_implicit', 'strict_explicit', 'reduce'):
        with V2AuthenticationReadSession() as session, ww.shared_instrument_calibration_physics_cache({}):
            def operation():
                ordinary_read = Path.read_bytes
                def guarded(path):
                    if path.name == 'metadata.json':
                        raise AssertionError('extra unauthenticated metadata read')
                    return ordinary_read(path)
                with mock.patch.object(Path, 'read_bytes', guarded):
                    if kind == 'reduce':
                        (root/'auth-reduced.json').unlink(missing_ok=True)
                        return invoke('reduce', member, '--output', root/'auth-reduced.json')
                    if kind == 'strict_explicit':
                        return cli.validate_bundle(member, strict=True, physics_cache=session.instrument_calibration_physics_cache)
                    return invoke('validate-bundle', '--strict', member)
            first, second = operation(), operation()
            assert first == second, (kind, first, second)
            records = {str(Path(k).relative_to(root)) if Path(k).is_relative_to(root) else k:
                       dataclasses.asdict(v) for k,v in session.records.items()}
            for record in records.values():
                record.pop('normalized_path')
            result[kind] = {'output': first, 'records': records}
            if kind == 'reduce':
                result[kind]['summary_sha256'] = hashlib.sha256((root/'auth-reduced.json').read_bytes()).hexdigest()
            metadata = member/'metadata.json'
            saved = metadata.read_bytes()
            data = json.loads(saved)
            data['instrument_calibration']['b_fiducial_s'] += 5e-13
            metadata.write_text(json.dumps(data))
            try:
                try:
                    outcome = operation()
                except Exception as exc:
                    outcome = {'exception': type(exc).__name__, 'code': getattr(exc, 'reason_code', None), 'message': str(exc)}
            finally:
                metadata.write_bytes(saved)
            result[kind]['mutation_refusal'] = outcome
            print(kind, 'registered paths', len(records), 'read_count total', sum(v['read_count'] for v in records.values()), 'mutation', str(outcome)[:180], file=sys.stderr, flush=True)
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == '__main__':
    if '--authentication' in sys.argv:
        authentication(Path(sys.argv[sys.argv.index('--authentication')+1]))
    else:
        boundaries()
