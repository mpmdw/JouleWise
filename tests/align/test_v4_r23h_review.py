"""Independent R23h review witnesses; synthetic inputs only."""
import copy
import math
from pathlib import Path
import unittest
from unittest.mock import patch

from joulewise.align.v4_analysis import analyze, engine, raw
from joulewise.align.v4_analysis.io import canonical, digest
from joulewise.align.v4_analysis.synthetic import series


def leaves(value, path=''):
    if isinstance(value, dict):
        return {p: v for k, child in value.items()
                for p, v in leaves(child, path+'/'+str(k).replace('~', '~0').replace('/', '~1')).items()}
    if isinstance(value, list):
        return {p: v for i, child in enumerate(value)
                for p, v in leaves(child, path+'/'+str(i)).items()}
    return {path: value}


def member_seals(value, targets, path=''):
    result = {}
    if isinstance(value, dict):
        if value.get('run_id') in targets:
            assert value.get('status') == 'sealed', path
            assert set(value) <= {'run_id', 'window', 'attempt_id', 'status', 'sha256', 'captured'}, path
            assert value['sha256'] == targets[value['run_id']], path
            result[path+'/sha256'] = value['sha256']
        for k, child in value.items():
            result.update(member_seals(child, targets, path+'/'+k))
    elif isinstance(value, list):
        for i, child in enumerate(value):
            result.update(member_seals(child, targets, path+'/'+str(i)))
    return result


class SealedLeafReviewTests(unittest.TestCase):
    def test_all_output_leaves_ignore_scored_c_values_except_whole_record_commitments(self):
        original = series(turns=4)
        changed = copy.deepcopy(original)
        targets = {}
        for window in changed['windows']:
            if not window['window'].startswith('C'):
                continue
            for member in window['members']:
                if member['slot']['series_role'] != 'sabotage':
                    continue
                thermal, summary = member['thermal'], member['summary']
                for convention, rows in summary['residual_rows'].items():
                    for row in rows:
                        row['context_tokens'] += 7654321
                        row['prefill_tokens'] += 7654321
                        row['energy_j'] += 7654321.125
                        row['energy_half_width_j'] = 7654321.125
                        if convention == 'True':
                            row['decode_tokens'] += 31
                thermal.update(start_ns=7654321125000000, g0_slow_c=55.75,
                    turn_owned_j=math.fsum(r['energy_j'] for r in summary['residual_rows']['True']),
                    turn_owned_half_width_j=7654321.125, gross_episode_j=7654321.125,
                    gross_episode_half_width_j=7654321.125, identity_sha256='f'*64)
                thermal['turn_counts'] = [[r[k] for k in ('context_tokens', 'prefill_tokens', 'decode_tokens')]
                                          for r in summary['residual_rows']['True']]
                thermal['tokens'][0]['output_token_ids'] = [7654321]
                thermal['intervals'].append(dict(kind='G1', outcome='released'))
                thermal['coverage'][0]['sample_fraction'] = .995
                thermal['battery'].update(soc_pct=[76.54321, 76.54321], charger_w=[7654321.125],
                                          flags=['battery.assist'])
                summary['cache_statistics'].update(rebuilds=7654321, rewinds=7654321)
                summary['energy']['powermetrics:gpu_power'].update(joules=7654321.125, half_width_j=7654321.125)
                member['dc'] = dict(joules=7654321.125, flags=['review-marker'])
                targets[member['slot']['run_id']] = digest(canonical(member))
        self.assertEqual(len(targets), 16)
        before, before_verdict = analyze(original)
        after, after_verdict = analyze(changed)
        self.assertEqual(before_verdict, after_verdict)
        self.assertEqual(before['leaf_inventory'], after['leaf_inventory'])
        left, right = leaves(before), leaves(after)
        self.assertEqual(left.keys(), right.keys())
        differences = {p for p in left if left[p] != right[p]}
        seals = member_seals(after, targets)
        self.assertEqual(len(seals), 80)  # eligibility, battery, DC, cache and counts
        self.assertEqual(differences, set(seals) | {'/threshold_freeze/calibration_inputs_sha256'})


class RecordedSecondsReviewTests(unittest.TestCase):
    def test_every_endpoint_and_stamp_seconds_field_refuses_strings_and_both_bools(self):
        base = dict(captured=True, first_record_endpoint_s=1767225601.,
            stamps=[dict(epoch_s=1767225600., monotonic_before_s=100., monotonic_after_s=100.,
                         wall_resolution_s=0., monotonic_resolution_s=0.)])
        for field in ('first_record_endpoint_s', *raw.STAMP_SECOND_FIELDS):
            for value in ('0.0', True, False):
                source = copy.deepcopy(base)
                target = source if field == 'first_record_endpoint_s' else source['stamps'][0]
                target[field] = value
                with self.subTest(field=field, value=value):
                    with patch.object(raw, 'read_blob', side_effect=AssertionError('source opened')):
                        with self.assertRaisesRegex(ValueError, 'must be a recorded number'):
                            raw.member(Path.cwd(), engine.roster('C1')[5], source)


if __name__ == '__main__':
    unittest.main()
