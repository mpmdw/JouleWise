"""Reachable desk-check counterexamples over newly generated synthetic bundles."""
from contextlib import redirect_stdout
from dataclasses import replace
import io
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts import align_pilot_session as pilot, bytes_h_session as h
from tests.test_align_pilot_session import SyntheticDeskTests, fixture_spec
from tests.align.test_shade import fixture_source

results = {}
with tempfile.TemporaryDirectory(prefix='probe-') as directory, fixture_source() as source:
    root = Path(directory)
    runs = root / 'runs'
    rows = []
    for repeat in (1, 2, 3):
        spec = fixture_spec(source, 'benign', repeat)
        turns = [dict(t) for t in spec.mock_turns]
        turns[0]['prompt_tokens'] += 100 * repeat
        spec = replace(spec, mock_turns=tuple(turns))
        bundle = SyntheticDeskTests.run_member(SyntheticDeskTests(), runs, spec, f'repeat-{repeat}')
        rows.append({'run_id': bundle.name, 'task_pair': 'ledger_review', 'condition': 'benign',
                     'repeat': repeat, 'ordinal': repeat, 'summary': pilot.episode_summary(bundle)})
    checks, deterministic, spreads = pilot.instrument_checks(rows)
    assert all(checks.values())
    assert len({r['summary']['totals']['prefill_tokens'] for r in rows}) == 3
    results['different_prefill_work'] = {
        'decode': [r['summary']['per_turn_decode_tokens'] for r in rows],
        'prefill': [r['summary']['totals']['prefill_tokens'] for r in rows],
        'checks': checks, 'repeat_token_identity': deterministic, 'spread': spreads}

    # A failed anchor is an ordinary instrument-fault outcome. Exercise desk,
    # including its real bundle reader and writer; only the harvest is stubbed.
    bundle = runs / 'repeat-1'
    metadata = h.read(bundle / 'metadata.json')
    metadata['uncertainty_evidence'] = {'clock_anchor': {'status': 'unresolved'}}
    h.write(bundle / 'metadata.json', metadata)
    summary = pilot.episode_summary(bundle)
    assert 'clock_anchor_unresolved' in summary['flags']
    assert any(e['half_width_j'] == float('inf') for e in summary['energy'].values())
    measurement = root / 'measurement'
    h.write(measurement / pilot.KIT / 'collection_plan.json', {'members': [
        {k: v for k, v in rows[0].items() if k != 'summary'}]})
    custody = root / 'custody'
    h.write(custody / 'night/result.json', {})
    h.write(root / 'plan.json', {'custody_root': str(custody)})
    session = root / 'session'
    (session / 'staging').mkdir(parents=True)
    h.write(session / 'session.json', {'session_id': 'synthetic-fault', 'plan_path': str(root / 'plan.json'),
        'measurement_root': str(measurement), 'registration_dir': str(measurement / pilot.KIT / 'registration'),
        'runs_roots': {'claim': str(runs)}, 'inputs': {'runs_parent': str(root)}})
    calls = []
    def harvest(argv, **kwargs):
        calls.append(argv)
        return SimpleNamespace(returncode=0, stdout='{}', stderr='')
    try:
        with redirect_stdout(io.StringIO()):
            pilot.desk(session, run=harvest)
    except ValueError as exc:
        error = str(exc)
    else:
        raise AssertionError('expected current desk serialization failure')
    assert not calls
    results['unresolved_anchor_desk'] = {'error': error, 'harvest_calls': len(calls),
        'pilot_written': (session / 'PILOT.json').exists(), 'desk_written': (session / 'desk.json').exists(),
        'flags': summary['flags'], 'half_width_j': 'infinity'}
print(json.dumps(results, sort_keys=True, indent=2))
