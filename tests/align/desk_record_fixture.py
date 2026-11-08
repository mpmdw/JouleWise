"""Small sealed-record fixtures; no machine state, model downloads or real data."""
from contextlib import redirect_stdout
import io
from pathlib import Path
from unittest.mock import patch

from scripts import bytes_h_session as h
from joulewise.align.apple import desk_record as dr


def write_json(path, value):
    h.write(Path(path), value)


def successful_desk(session, *, output, state, **kwargs):
    """Inert consumer for artifact-validation tests, not scientific pass evidence."""
    pilot = {'session_id': state['session_id'], 'plan_id': state['session_id'],
             'status': 'instrument_ok', 'checks': {'synthetic': True}}
    write_json(Path(output)/'PILOT.json', pilot)
    status = {'pilot_status': 'instrument_ok', 'harvest_status': 'not_run', 'harvest_exit': None}
    write_json(Path(output)/'desk.json', status)
    return status


def seal(repository, inputs, layout):
    write_json(repository/'finalize.json', dr.finalize(inputs, layout))
    layout = {**layout, 'finalize_manifest': 'finalize.json',
              'records_ref': 'refs/remotes/origin/records/synthetic'}
    write_json(repository/'record.json', dr.describe(inputs, layout, repository=repository))
    dr._git(repository, 'add', 'record.json', 'finalize.json')
    dr._git(repository, '-c', 'core.hooksPath=/dev/null', '-c', 'user.name=Synthetic',
            '-c', 'user.email=synthetic@example.invalid', 'commit', '--allow-empty', '-qm', 'Synthetic finalize')
    commit = dr._git(repository, 'rev-parse', 'HEAD').decode().strip()
    dr._git(repository, 'update-ref', layout['records_ref'], commit)
    return commit


def passing_artifact(root, session_id='synthetic'):
    from tests.align.test_desk_parallel import CommittedRecordTests
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    repository, _, inputs, layout = CommittedRecordTests().record(root)
    for path, field in ((inputs/'session/session.json', 'session_id'),
                        (inputs/'plan.json', 'plan_id'),
                        (inputs/'custody/night/result.json', 'plan_id'),
                        (inputs/'session/desk.json', 'plan_id')):
        value = h.read(path)
        value[field] = session_id
        write_json(path, value)
    commit = seal(repository, inputs, layout)
    output = root/'report'
    with patch('scripts.align_pilot_session._desk', successful_desk), redirect_stdout(io.StringIO()):
        dr.replay(repository, commit, 'record.json', inputs, output)
    return dr.gate_evidence(repository, commit, 'record.json', output)
