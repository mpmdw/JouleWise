"""Repin only current synthetic custody envelopes after validator changes."""
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from joulewise import paper_custody as custody


def encoded(value):
    return custody._canonical_json_bytes(value)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def repin():
    path = ROOT / custody._SUPPLY_MAP_PATH
    supply = json.loads(path.read_bytes())
    supply['schema_version'] = custody._SUPPLY_MAP_SCHEMA
    supply['pending_roles'] = {
        'production.reported_energy_parents.qwen3-1p7b.v5': {
            'status': 'pending_desk_day', 'family': 'reported_energy_parents',
            'input_role': 'extraction_spec', 'base': 'repository', 'authority': 'git_blob',
            'path': 'configs/campaigns/d117_floor_qwen3-1p7b_v5/extraction_spec.json',
        }
    }
    for role, entry in supply['roles'].items():
        if not role.startswith('fixture.'):
            raise ValueError('repin is restricted to fixture maps')
        family = entry['family']
        entry.update(mode='test_fixture_non_issuing', issuance_gate_id=None, subjects=[])
        entry['source_census'] = [{
            'authority': 'generated', 'base': 'runs_root',
            'path': f'{family}/sources/member.json',
            'expected_sha256': digest(encoded({'family': family, 'marker': 'synthetic-no-measurement-value'})),
        }]
        if family == 'reported_energy_parents':
            row = entry['inputs'][0]
            row.update(authority='git_blob', base='repository',
                       path='tests/fixtures/paper_custody/extraction_spec.json')
            (ROOT / row['path']).write_bytes(encoded({
                'family': family, 'marker': 'synthetic-no-measurement-value',
                'role': 'extraction_spec', 'schema_version': custody._FIXTURE_SCHEMA,
            }))
        consumed = [*entry['inputs'], *[dict(row, role='authenticated_source') for row in entry['source_census']]]
        receipt = {
            'family': family,
            'inputs': sorted([{'path': row['path'], 'role': row['role'], 'sha256': row['expected_sha256']}
                              for row in consumed], key=lambda row: (row['role'], row['path'])),
            'replay_codes': [], 'schema_version': custody._RECEIPT_SCHEMA, 'status': 'PASS',
            'validator': entry['validator'], 'validator_source_sha256': custody._validator_source_sha256(family),
        }
        entry['receipt']['expected_sha256'] = digest(encoded(receipt))
        inventory = {
            'family': family,
            'files': sorted([{'authority': row['authority'], 'path': row['path'], 'role': row['role'],
                              'sha256': row['expected_sha256']} for row in consumed] + [{
                'authority': 'generated', 'path': entry['receipt']['path'], 'role': 'validator_receipt',
                'sha256': entry['receipt']['expected_sha256']}], key=lambda row: (row['role'], row['path'])),
            'inventory_id': f'fixture-{family}', 'mode': 'test_fixture_non_issuing',
            'schema_version': custody._INVENTORY_SCHEMA,
        }
        entry['inventory']['expected_sha256'] = digest(encoded(inventory))
    path.write_text(json.dumps(supply, indent=2, sort_keys=True) + '\n')
    print('Repinned five synthetic, non-issuing fixture envelopes; production role pending.')


if __name__ == '__main__':
    repin()
