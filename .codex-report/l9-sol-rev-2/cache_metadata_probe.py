"""Can a same-evidence, tolerated metadata-bound difference poison a later call?"""
import contextlib
import hashlib
import io
import json
from pathlib import Path
import shutil
import tarfile
import tempfile
import runpy
from unittest import mock

from joulewise import cli, whole_window as ww
from joulewise.b5_analysis import dry_run as d
from joulewise.b5_analysis.deadline_observer import observe_wall_deadline
from tests.b5_analysis.test_shared_physics_cache import ARCHIVE, MEMBER


def reduce(member, output):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        status = cli.main(['reduce', str(member), '--output', str(output)])
    return status, json.loads(output.read_bytes()), err.getvalue()


def strict(member):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        status = cli.main(['validate-bundle', '--strict', str(member)])
    return status, out.getvalue(), err.getvalue()


def driver_pair(root, high, low):
    """Real step 1 and driver; archive preparation and other steps are stubs."""
    helpers = runpy.run_path(str(Path(__file__).with_name('missing_monitoring.py')))
    baseline, namespace = helpers['original_run']()
    steps = tuple((step, d.step_1 if step == '1' else
                   lambda s, r, step=step: [s.record(step)]) for step in d.STEP_IDS)
    namespace['STEPS'] = steps
    result = {}
    for label, function in [('0576a734d', baseline), ('f059286bc', d.run)]:
        folder = root / label
        (folder / 'repo').mkdir(parents=True)
        index = folder / 'index.json'
        index.write_bytes(d._canonical({'schema': 'joulewise.b5_window_index.v1', 'attempts': []}))
        with mock.patch.object(d, 'STEPS', steps), \
                mock.patch.object(d.RunState, 'prepare_kept', lambda self, argv: 0), \
                mock.patch.object(d.RunState, 'kept_bundles', lambda self: [('alpha', 'higher', high), ('alpha', 'lower', low)]), \
                contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            status = function('blind-dry-run', index, folder / 'custody',
                              _test_repo_root=folder / 'repo', _git=lambda _: 'b' * 40)
        record = json.loads((folder / 'custody/dry-run/B5-BLIND-DRY-RUN-RECORD.json').read_bytes())
        row = next(row for row in record['steps'] if row['step'] == '1')
        result[label] = {'return': status, 'step1_status': row['status'], 'step1_refusal': row['refusal'],
                         'later': [row['status'] for row in record['steps'][2:]]}
    return result


with tempfile.TemporaryDirectory(prefix='sol-bound-key-') as tmp:
    root = Path(tmp)
    with tarfile.open(ARCHIVE) as archive:
        archive.extractall(root, members=[m for m in archive.getmembers() if m.name.startswith(MEMBER)], filter='data')
    member = root / MEMBER
    high = root / 'high'
    shutil.copytree(member, high)
    metadata = json.loads((high / 'metadata.json').read_bytes())
    original = metadata['instrument_calibration']['b_fiducial_s']
    metadata['instrument_calibration']['b_fiducial_s'] = original + 5e-13
    (high / 'metadata.json').write_text(json.dumps(metadata))
    print('original b:', repr(original), 'higher b:', repr(metadata['instrument_calibration']['b_fiducial_s']))
    print('same calibration evidence SHA:', hashlib.sha256((member / 'instrument_calibration/instrument_evidence.json').read_bytes()).hexdigest())
    with observe_wall_deadline() as observer:
        plain_status, plain, plain_err = reduce(member, root / 'plain.json')
        with ww.shared_instrument_calibration_physics_cache({}) as cache:
            high_status, seeded, high_err = reduce(high, root / 'seed.json')
            shared_status, shared, shared_err = reduce(member, root / 'shared.json')
        # Store the genuinely rederived higher-bound summary, making both
        # synthetic bundles self-consistent before testing strict admission.
        (high / 'summary_metrics.json').write_bytes((root / 'seed.json').read_bytes())
        plain_high = strict(high)
        plain_low = strict(member)
        with ww.shared_instrument_calibration_physics_cache(dict(cache)):
            shared_high = strict(high)
            shared_low = strict(member)
        drivers = driver_pair(root, high, member)
    print('CLI statuses plain/seed/shared:', plain_status, high_status, shared_status)
    print('wall-deadline firings:', observer.firings)
    print('cache:', cache)
    differences = {key: {'plain': plain.get(key), 'shared': shared.get(key)}
                   for key in sorted(set(plain) | set(shared)) if plain.get(key) != shared.get(key)}
    print('differing summary keys:', sorted(differences))
    output = Path(__file__).with_name('cache-metadata-differences.json')
    output.write_text(json.dumps(differences, sort_keys=True, indent=2) + '\n')
    for label, summary in [('plain', plain), ('shared', shared)]:
        envelope = summary['energy_anchor_shift_envelopes']['/gross_energy_j']
        print(label, 'gross anchor_bound_s:', repr(envelope['anchor_bound_s']),
              'gross max_abs_delta_j:', repr(envelope['max_abs_delta_j']))
    print('strict uncached high/low:', plain_high[0], plain_low[0])
    print('strict shared high/low:', shared_high[0], shared_low[0])
    print('shared low strict diagnostic:', repr(shared_low[1]), repr(shared_low[2]))
    print('stderr:', repr(plain_err), repr(high_err), repr(shared_err))
    print('real step-1 driver comparison:', json.dumps(drivers, sort_keys=True))
    assert observer.firings == 0
    assert (plain_status, high_status, shared_status) == (0, 0, 0)
    assert differences
    assert (plain_high[0], plain_low[0]) == (0, 0)
    assert (shared_high[0], shared_low[0]) == (0, 2)
    assert drivers['0576a734d']['return'] == 0
    assert (drivers['f059286bc']['return'], drivers['f059286bc']['step1_refusal']) == (2, 'kept_bundle_strict_validation_failed')
