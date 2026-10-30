"""Generate only the isolated known-bytes plan; never read a measurement root."""
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

ROOT = Path(__file__).resolve().parent


def raw(value):
    return (json.dumps(value, indent=2, sort_keys=True) + '\n').encode()


def generate():
    config = {'schema_version': '0.1', 'model': {'name': 'not_applicable'},
              'quantization': {'name': 'none'},
              'hardware_target': {'id': 'macbook_m3_max', 'transport': 'local',
                                  'runtime_backend': 'mock', 'telemetry_backend': 'powermetrics'},
              'workload_profile': {'name': 'known_bytes_non_claim', 'prompt_tokens': 1, 'output_tokens': 1},
              # Rule §2: pass-1 rails cadence and own idle length.
              'sampling': {'power_hz': 10, 'idle_seconds': 57.6}}
    plan = {'plan_id': 'bytes-stream-test', 'non_claim': True}
    files = {'telemetry.json': config, 'collection_plan.json': plan,
             'genesis_pin.json': {'ledger_schema': 'joulewise.calibration_observation_ledger.v1',
                                  'sequence': 0, 'head_digest': '0' * 64}}
    def a(kind, value, **kw):
        return dict(kind=kind, value=value, **kw)
    def lit(value):
        return a('literal', str(value))
    def bind(value):
        return a('binding', value)
    def repo(value):
        return a('repo_path', 'configs/campaigns/bytes_stream_test/' + value)
    def pair(flag, value):
        return [lit(flag), value]
    reservation = [lit('--execute')]
    for flag, value in (
        ('--ledger', bind('ledger_path')), ('--head-pin', repo('genesis_pin.json')),
        ('--session-id', bind('bracket_session_id')), ('--window-id', lit('bytes-stream-test')),
        ('--plan-id', lit('bytes-stream-test')), ('--plan-sha256', lit(hashlib.sha256(raw(plan)).hexdigest())),
        ('--plan', repo('collection_plan.json')), ('--evidence-root-id', lit('bytes-stream-test')),
        ('--runs-root', bind('claim_runs_root')), ('--pre-attempt-id', bind('pre_attempt_id')),
        ('--post-attempt-id', bind('post_attempt_id')), ('--pre-custody-locator', bind('pre_calibration_dir')),
        ('--post-custody-locator', bind('post_calibration_dir')),
        ('--identity-epoch-json', bind('identity_epoch_json')), ('--t1-bindings-json', bind('t1_bindings_json'))):
        reservation += pair(flag, value)
    specs = [('reserve', 'bracket_reservation', 'bracket_reserver', reservation, 0)]
    for slot in ('pre', 'post'):
        args = [lit('--allow-live')]
        for flag, value in (('--ledger', bind('ledger_path')), ('--head-pin', repo('genesis_pin.json')),
                            ('--output-root', a('binding_path', 'claim_runs_root', relative='instrument_validation')),
                            ('--session-id', bind('bracket_session_id')), ('--slot', lit(slot)),
                            ('--attempt-id', bind(slot + '_attempt_id')), ('--power-policy', lit('ac_high_power'))):
            args += pair(flag, value)
        specs.append((slot, 'calibration_capture', 'fiducial_capture', args, 0))
        if slot == 'pre':
            specs.append(('known-bytes', 'bytes_stream_capture', 'bytes_stream_capture',
                          pair('--archive', a('binding_path', 'claim_runs_root', relative='capture')) +
                          pair('--device', lit('macbook_m3_max')), 8))
    from joulewise.b5.chain import TOOLS
    graph = []
    for i, (name, kind, tool, args, count) in enumerate(specs):
        graph.append({'stage_id': name, 'kind': kind, 'ordinal': i + 1, 'expected_count': count,
                      'predecessor': specs[i-1][0] if i else None,
                      'successor': specs[i+1][0] if i+1 < len(specs) else None,
                      'launch': {'schema_version': 'joulewise.stage_launch.v1', 'commands': [{
                          'command_id': name, 'cwd': {'kind': 'binding', 'value': 'repo_root'},
                          'success_exit_codes': [0], 'argv_template': {
                              'tool_id': tool, 'interface_id': TOOLS[tool].interface_id, 'arguments': args}}]}})
    tree = {'schema_version': 'joulewise.d117_plan_tree.v1', 'non_claim': True,
            'plan': {'plan_id': plan['plan_id'], 'path': 'collection_plan.json'},
            'window_identity': {'window_id': 'bytes-stream-test', 'evidence_root_id': 'bytes-stream-test'},
            'roots': {'claim_root_leaf': 'runs_bytes_stream_test', 'bound_root_leaf': 'runs_bytes_stream_test_bound'},
            'stage_graph': graph, 'arm_attachments': {'identity_pin_projection': {'identity_units': [
                {'config_inventory': [{'path': 'telemetry.json', 'sha256': hashlib.sha256(raw(config)).hexdigest()}]}]}}}
    files['plan_tree.json'] = tree
    return {name: raw(value) for name, value in files.items()}


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--check', action='store_true')
    args = p.parse_args()
    for name, content in generate().items():
        path = ROOT / name
        if args.check:
            if not path.is_file() or path.read_bytes() != content:
                raise SystemExit('generated bytes differ: ' + name)
        else:
            path.write_bytes(content)
