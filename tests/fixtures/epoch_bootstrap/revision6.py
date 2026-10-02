"""Synthetic producer records with the exact shared Revision 6 interface.

These fixtures authorize no capture; all Git writes occur in disposable roots.
"""
import copy
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import subprocess

from joulewise.calibration_ledger import load_calibration_ledger_snapshot
from scripts import issue_calibration_acceptance_generation as issuer
from tests.fixtures.epoch_bootstrap.build import Slot, build_derivation_ledger
from tests.test_acc_25g83_rev5 import sealed_registration, R7


def canonical(value):
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n").encode()


def declaration():
    raw = json.loads((Path(__file__).parent / 'revision6_declaration.json').read_bytes())
    def seal(value):
        if isinstance(value, dict):
            return {key: seal(item) for key, item in value.items()}
        if isinstance(value, list):
            return [seal(item) for item in value]
        return "a" * 64 if value == "TO BE PINNED AT SEAL" else value
    block = seal(raw)
    block['pins'].update(cap_cells=1_000_000, ledger_head_pin_at_first_window={'sequence': 0, 'digest': '0'*64})
    return block


def sid(index):
    return f'd079-epoch-25g83-r6-20261001T{index:04d}Z'


def night_plan_of(session_id):
    """The night plan id a window's harvest record carries (distinct from its session id)."""
    return f'night-{session_id}'


def commit(root):
    subprocess.run(['git', '-C', str(root), 'add', '.'], check=True, capture_output=True)
    subprocess.run(['git', '-C', str(root), '-c', 'user.email=fixture@example.invalid', '-c', 'user.name=fixture',
                    'commit', '-qm', 'synthetic Revision 6 harvest'], check=True, capture_output=True)


def window_records(root, session, block, *, previous=None, adverse=False, night_plan_id=None):
    custody = root / session.session_id
    def write(path, raw):
        target = custody / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
        return {'path': path, 'sha256': hashlib.sha256(raw).hexdigest()}
    start = float(1_800_000_000 + session.capability_sequence * 10_000)
    # Production shape: the night plan's id differs from the ledger session's
    # calibration plan id, and the window's records carry the night plan's.
    night_plan_id = night_plan_id or night_plan_of(session.session_id)
    monotonic = start - 1_700_000_000
    off = {'schema': 'joulewise.network_time_off.v1', 'argv': list(issuer.network_time_off.OFF_ARGV),
           'exit_code': 0, 'stdout': issuer.network_time_off.EXPECTED_STDOUT, 'stderr': 'Error:-99\n',
           'boot_id': 'synthetic-boot', 'plan_id': night_plan_id, 'window_id': night_plan_id,
           'epoch_s': start - 1000, 'monotonic_s': monotonic - 1000}
    prior = None
    if previous is not None:
        prior_source = root / previous / 'harvest.json'
        prior_path = custody / 'night/prior_harvest.json'
        prior_path.parent.mkdir(parents=True, exist_ok=True)
        prior_path.write_bytes(prior_source.read_bytes())
        prior_harvest = json.loads(prior_path.read_bytes())
        prior = {'session_id': previous, 'harvest_file': str(prior_path),
                 'harvest_sha256': hashlib.sha256(prior_path.read_bytes()).hexdigest(),
                 'decision_sha256': prior_harvest['next_window_sha256']}
    manifest = {'prior_revision6_session': prior, 'reason': 'first session' if prior is None else None}
    manifest_ref = write('night/start_conditions_manifest.json', canonical(manifest))
    evidence = {
        'a_prior_session_manifest': manifest_ref,
        'b_blind_checks': {**manifest_ref, 'decision_sha256': prior['decision_sha256'] if prior else None},
        'c_agent_census': write('night/gate.json', canonical({'agent_census': 0, 'thermal': 100, 'battery': 'pass'})),
    }
    evidence['d_thermal'] = dict(evidence['c_agent_census'])
    evidence['e_battery_float'] = dict(evidence['c_agent_census'])
    evidence['f_network_time_off_receipt'] = {**write('night/network_time_off.json', canonical(off)), 'settled_seconds': 1000.0}
    evidence['g_clean_dwell'] = {**write('night/prewindow_check.out', b'continuous clean dwell 600/600s (check 21)\nREADY after 10 min.\n'),
        'script_sha256': block['pins']['prewindow_check_sha256'], 'exit': 0,
        'passed_epoch_s': start - .1, 'deadline_epoch_s': start}
    start_record = {'schema': 'joulewise.revision6.start_conditions.v1', 'session_id': session.session_id,
        'plan_id': night_plan_id, 'result': 'admitted' if session.finalized_slots else 'refused',
        'refusal_reason': None if session.finalized_slots else session.abort_reason,
        'evidence': evidence, 'written_epoch_s': start + 20, 'written_monotonic_s': monotonic + 20,
        'boot_id': 'synthetic-boot',
        'chain_start_admitted': {'epoch_s': start, 'monotonic_s': monotonic} if session.finalized_slots else None}
    captures = []
    for slot, row in session.finalized_slots.items():
        captures.append({'slot': session.declared_slots.index(slot)+1, 'capture_id': row.attempt_id,
            'content_id': row.content_id, 'has_recording': True, 'cells': 100, 'median_frame_ms': 132.0,
            'ratio': .0001, 'disposition': row.classification_disposition, 'cap_trigger': None,
            'median_frame_reported': True, 'counted': not adverse})
    r9 = {'schema': 'joulewise.revision6.r9_window.v1', 'session_id': session.session_id,
        'slots': 12, 'captures': captures, 'counted': sum(row['counted'] for row in captures),
        'valid': sum(row['disposition'] == 'valid' for row in captures) if not adverse else 0,
        'harness_sha256': block['pins']['harness_sha256'],
        'rule_ref': 'CAP-COUNCIL-25G83-01 R9 as amended; Revision 6 §4'}
    if not captures:
        r9['abort_reason'] = session.abort_reason
    harvest = {'schema': 'joulewise.harvest_window.v1', 'custody_root': str(custody), 'plan_id': night_plan_id,
               'boot_id': 'synthetic-boot', 'window_end': None,
               'next_window': {'verdict': 'NEXT_WINDOW'},
               'next_window_sha256': hashlib.sha256(canonical({'verdict': 'NEXT_WINDOW'})).hexdigest(),
               'start_conditions': write('night/start_conditions.json', canonical(start_record)),
               'r9_window': write('harvest/r9_window.json', canonical(r9))}
    if captures:
        harvest['window_end'] = {'epoch_s': start + 7200, 'monotonic_s': monotonic + 7200,
            'source': write('night/chain.exited', canonical({'exit_code': 0, 'epoch_s': start + 7200,
                'monotonic_ns': int((monotonic + 7200) * 1_000_000_000)}))}
    path = root / session.session_id / 'harvest.json'
    path.write_bytes(canonical(harvest))
    return path


def build(root, *, slots=None, second_slots=None, third_slots=None, null_first=False,
          corpus_root=False, custody_names=None):
    """``corpus_root`` puts member custody outside the repository, as production
    does: ``<root>/night-custody/<night plan id>/runs/instrument_validation/<capture>``,
    the night plan id being the one each window's harvest record carries.
    ``custody_names`` overrides a session's directory name (negative tests)."""
    block = declaration()
    pin_files = {"chain": root / 'fixture/scripts/night_chains/calibration_derivation_only.zsh',
                 "validator": root / 'fixture/scripts/validate_powermetrics_fiducial.py',
                 "cap_rule_text": root / 'cap-rule.md', "roster": root / 'roster.json'}
    for name, path in pin_files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes((name + ' synthetic pinned bytes\n').encode())
        block['pins'][name + '_sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
    predecessor = json.loads(R7.read_bytes())
    predecessor['acceptance_id'] = 'd079_calibration_acceptance_v2_n17_r8'
    predecessor_path = root / 'p8.json'
    root.mkdir(parents=True, exist_ok=True)
    predecessor_path.write_bytes(canonical(predecessor))
    block['predecessor'].update(file_sha256=hashlib.sha256(predecessor_path.read_bytes()).hexdigest(),
                               derivation_sha256=predecessor['derivation_sha256'])
    block['pins']['estimator_code_sha256'] = predecessor['prospective_rederivation']['estimator_code_sha256']
    text = sealed_registration() + '\n# Revision 6 (sealed synthetic fixture)\n\n```json\n' + json.dumps(block) + '\n```\n'
    prereg = root / 'sealed.md'
    prereg.write_text(text)
    prereg_digest = hashlib.sha256(prereg.read_bytes()).hexdigest()
    slots = slots if slots is not None else [Slot('0.025') for _ in range(12)]
    second_slots = second_slots if second_slots is not None else [Slot('0.026') for _ in range(12)]
    custody_parent = root / 'night-custody' if corpus_root else None
    names = {sid(i): night_plan_of(sid(i)) for i in (1, 2, 3)}
    names.update(custody_names or {})
    fixture = build_derivation_ledger(root / 'fixture', slots, session_id=sid(1),
        custody_parent=custody_parent, custody_names=names if corpus_root else None,
        fill_slots=0 if null_first else None, abort_reason='zero capture refusal' if null_first else None,
        second_session=(sid(2), second_slots), third_session=(sid(3), third_slots) if third_slots is not None else None,
        verdict_records=True, preregistration_sha256=prereg_digest)
    snapshot = load_calibration_ledger_snapshot(fixture['ledger'], fixture['pin'], require_committed_pin=True,
                                               verify_custody=False, mode='read_replay', repo_root=fixture['root'])
    registry = issuer._registered_dispositions()
    base = snapshot.observations[0]
    # Archived rows are immutable design-input placeholders, never opened.
    archived = tuple(replace(base, attempt_id=f'archived-{i}', bracket_session_id='archived-w1w2', content_id=cid)
                     for i, cid in enumerate(registry))
    snapshot = replace(snapshot, observations=snapshot.observations + archived)
    paths = []
    previous = None
    for session in snapshot.bracket_sessions:
        adverse = bool(session.finalized_slots) and issuer.battery_float.authenticate_committed_verdict(
            fixture['root'], session=session, preregistration_sha256=prereg_digest).status != 'pass'
        paths.append(window_records(fixture['root'], session, block, previous=previous, adverse=adverse))
        previous = session.session_id
    commit(fixture['root'])
    argv = ['prepare-candidate', '--ledger', str(fixture['ledger']), '--head-pin', str(fixture['pin']),
            '--repo-root', str(fixture['root']), '--preregistration', str(prereg),
            '--preregistration-sha256', prereg_digest, '--predecessor-acceptance', str(predecessor_path),
            '--d125-ruling', 'synthetic Revision 6 D-125', '--out', str(root/'candidate.json')]
    for session in snapshot.bracket_sessions:
        argv += ['--registration-session-id', session.session_id]
    for path in paths:
        argv += ['--harvest-record', str(path)]
    argv += ['--cap-rule-text', str(pin_files['cap_rule_text']), '--roster', str(pin_files['roster'])]
    if corpus_root:
        argv += ['--corpus-root', str(custody_parent.resolve())]
    return {'args': issuer.build_parser().parse_args(argv), 'snapshot': snapshot, 'block': block,
            'paths': paths, 'predecessor': predecessor, 'fixture': fixture}


def rewrite_record(harvest_path, name, mutate, *, refresh_digest=True):
    harvest = json.loads(harvest_path.read_bytes())
    path = Path(harvest['custody_root']) / harvest[name]['path']
    record = json.loads(path.read_bytes())
    mutate(record)
    path.write_bytes(canonical(record))
    if refresh_digest:
        harvest[name]['sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
        harvest_path.write_bytes(canonical(harvest))
