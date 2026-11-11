"""RL-53/RL-54 W-7: execute finality orders against synthetic records only.

The real packet rebuild, series binding and latest-record check all run. No
measurement, host probe, custody locator or model is used.
"""
import copy
import json
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from tests.align import synthetic_custody  # fence before importing other fixtures
from tests.align.test_v4_next_arm_packet import INTERNAL, NOW, Scenario
from joulewise.align.apple import v4_cadence as cadence
from joulewise.align.apple import v4_registration as registration
from joulewise.align.apple import light_triage
from scripts import align_v4_harvest_off as harvest_off
from scripts import align_v4_next_arm_packet as builder
from scripts import align_v4_series as series
from scripts import align_v4_session as session

setUpModule = synthetic_custody.setUpModule
tearDownModule = synthetic_custody.tearDownModule


def final_receipt(scenario, sources):
    """Run the final eligibility reader on synthetic desk files, without a window record.

    Empty directories stand for captured bundles. No bundle reader or harvest runs.
    All paths the command opens are inside the scenario's TemporaryDirectory.
    """
    directory = scenario.dir + '/desk-reader'
    plan_path = directory + '/plan.json'
    scenario.write(plan_path, scenario.sources['plan'])
    scenario.write(directory + '/collection_plan.json', {'members': scenario.members})
    scenario.write(directory + '/session.json', {
        'session_id': scenario.sources['plan']['plan_id'],
        'plan_path': str(scenario.root / plan_path),
        'measurement_root': str(scenario.root),
        'registration_dir': str(scenario.root / directory / 'registration'),
        'runs_roots': {'claim': str(scenario.root / directory / 'bundles')}})
    for member in scenario.members:
        (scenario.root / directory / 'bundles' / member['run_id']).mkdir(parents=True, exist_ok=True)
    scenario.write(directory + '/PILOT.json', sources['pilot'])
    scenario.write(directory + '/desk.json', sources['desk'])
    scenario.write(directory + '/archive/derived/exclusions.json', sources['exclusions'])
    return harvest_off.cmd_final(SimpleNamespace(
        session_root=scenario.root / directory, window_id=scenario.window, pilot=None))


class FinalityPathsTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='jw-finality-', dir='/private/tmp')
        self.addCleanup(temporary.cleanup)
        self.w1 = Scenario(temporary.name, 'W1')
        # Seed arithmetic only: the frozen manifest contains no measurement inputs.
        self.w1.write(series.MANIFEST, series.raw_json(series.candidate()))
        self.w1.finish()

    def calibration(self, name, previous, **options):
        scenario = Scenario(previous.root, name, previous=previous, **options)
        scenario.next_plan['window'] = 'C' + str(int(name[1:]) + 1)
        scenario.series['pool_members'] = [m['run_id'] for m in scenario.members]
        scenario.sources['pilot']['extra_checks']['series_desk_row'][
            'desk_eligible_benign'] = dict.fromkeys(cadence.CAL_PAIRS, 1)
        if name == 'C2':
            # Mix the main-era sent receipt with W1's digest-bound delivery receipt.
            scenario.sources['courier'] = {'sent': False}
            plan_id = scenario.sources['plan']['plan_id']
            scenario.sources['courier_delivery'] = {
                'transport': 'git-push', 'plan_id': plan_id,
                'ref': 'refs/heads/night-results/' + plan_id, 'commit': 'd' * 40,
                'result_sha256': builder.digest(
                    (json.dumps(scenario.sources['result'], sort_keys=True) + '\n').encode())}
        return scenario

    def commit_series(self, scenario):
        scenario.write(scenario.series_path, scenario.series)
        scenario.series_commit = scenario.commit()

    def final_descriptor(self, successor, prior):
        return {'record_sha256': prior.link['sha256'], 'sources': {
            name: successor.write(f'{successor.dir}/previous-final/{name}.json', value)
            for name, value in prior.final_sources.items()}}

    def assert_arm_accepts(self, scenario, packet):
        self.assertNotIn('calibration_error', packet)
        self.assertTrue(packet['packet_preflight']['ready'], packet['packet_preflight'])
        current = registration.artifact_set_digest(scenario.root)
        rebuilt, matches = builder.rebuild_and_compare(
            scenario.root, packet, now_epoch_s=NOW, current_artifact_set_sha256=current)
        self.assertTrue(matches)
        self.assertEqual(builder.canonical(packet), builder.canonical(rebuilt))
        bound = session._record_bound(scenario.root, rebuilt)
        self.assertTrue(bound, 'latest record and HEAD series ledger must name this packet')
        result = cadence.next_arm_triage(rebuilt, INTERNAL, {
            'artifact_set_sha256': current, 'record_commit_exists': True,
            'record_bound': bound}, now_epoch_s=NOW)
        self.assertTrue(result['admitted'], result['reasons'])
        if scenario.window == 'C2':
            self.assertIn(f'{scenario.dir}/evidence/courier_delivery.json',
                          [row['path'] for row in rebuilt['evidence']])
        self.assertIs(series.bind_packet(scenario.root, scenario.next_plan['window'], rebuilt,
                                        authenticated_by_rebuild=True), rebuilt)
        return rebuilt

    def late_exclusion(self):
        c1 = self.calibration('C1', self.w1, provisional=True).finish()
        provisional = self.assert_arm_accepts(c1, c1.build())
        self.assertEqual(provisional['calibration_windows'][0]['status'], 'provisional')
        self.assertEqual(provisional['calibration_windows'][0]['eligible_benign'],
                         dict.fromkeys(cadence.CAL_PAIRS, 1))
        excluded = c1.members[0]['run_id']
        self.assertIn(excluded, c1.series['pool_members'])
        # The off-host desk finishes AFTER the C2-arm evidence was committed.
        c1.final_sources['pilot']['extra_checks']['thermal']['members'][0]['excluded'] = True
        c1.final_sources['exclusions']['members_excluded'] = [
            {'run_id': excluded, 'codes': ['clock.step']}]
        c2 = self.calibration('C2', c1, previous_final=True).finish()
        return c1, c2, provisional, excluded

    def test_order1_desk_final_before_successor_first_commit_accepts_k_plus_2(self):
        c1, c2, provisional, excluded = self.late_exclusion()
        # k=C1. Its final sources already exist when C2 is first committed.
        self.assertEqual(c2.git('rev-list', '--count', 'HEAD', '--', c2.record_path), '1')
        committed = json.loads(c2.git('show', c2.record_commit + ':' + c2.record_path))
        self.assertEqual(committed['previous_final']['record_sha256'], c1.link['sha256'])
        packet = self.assert_arm_accepts(c2, c2.build())
        self.assertEqual(packet['next_window_id'], 'C3')
        before = provisional['calibration_windows'][0]
        after = packet['calibration_windows'][0]
        expected = dict(before['eligible_benign'])
        expected[cadence.CAL_PAIRS[0]] -= 1
        self.assertEqual(after, {**before, 'status': 'final', 'eligible_benign': expected})
        self.assertEqual(packet['calibration_windows'][1]['eligible_benign'],
                         dict.fromkeys(cadence.CAL_PAIRS, 1))
        self.assertEqual(packet['series_history'][0]['desk_eligible_benign'],
                         before['eligible_benign'])
        self.assertNotIn(excluded, c2.series['pool_members'])
        self.assertEqual(c2.series['pool_members'], [m['run_id'] for m in c2.members])
        # Replay did not edit C1's original provisional record or its captures.
        self.assertEqual(c1.build()['calibration_windows'][0], before)

    def test_stale_pool_refuses_cohort_first_and_new_series_commit_repairs_it(self):
        _c1, c2, _provisional, excluded = self.late_exclusion()
        c2.series['pool_members'].append(excluded)
        self.commit_series(c2)
        with patch.object(builder, 'require', wraps=builder.require) as requirements:
            stale = c2.build()
        failures = [call.args[1] for call in requirements.call_args_list if not call.args[0]]
        self.assertEqual(failures[:2], [
            'pool members outside previous D roster',
            'R17: a finally excluded member of C1 is in the pool'])
        self.assertEqual(stale['checks']['cohort_pool_rules']['status'], 'fail')
        self.assertEqual(stale['checks']['cohort_pool_rules']['basis'], failures[0])
        self.assertEqual(stale['calibration_error'], failures[1])
        self.assertFalse(stale['packet_preflight']['ready'])
        self.assertTrue(session._record_bound(c2.root, stale))
        record_commit, series_commit = c2.record_commit, c2.series_commit
        c2.series['pool_members'] = [m['run_id'] for m in c2.members]
        self.commit_series(c2)
        self.assertNotEqual(c2.series_commit, series_commit)
        self.assertEqual(c2.record_commit, record_commit)
        self.assertFalse(session._record_bound(c2.root, stale))
        repaired = self.assert_arm_accepts(c2, c2.build())
        self.assertEqual(repaired['checks']['cohort_pool_rules']['status'], 'pass')
        self.assertEqual(repaired['calibration_windows'][0]['status'], 'final')

    def test_final_counts_above_desk_ceiling_refuse_at_series_binding(self):
        c1 = self.calibration('C1', self.w1, provisional=True)
        pair = cadence.CAL_PAIRS[0]
        c1.thermal['members'][0].update(
            excluded=True, calibration_exclusions=['thermal.state_unobserved'])
        c1.series['pool_members'].remove(c1.members[0]['run_id'])
        c1.sources['pilot']['extra_checks']['series_desk_row']['desk_eligible_benign'][pair] = 0
        c1.finish()
        before = self.assert_arm_accepts(c1, c1.build())
        self.assertEqual(before['calibration_windows'][0]['eligible_benign'][pair], 0)
        # The final desk reverses that exclusion, but retains its committed ceiling.
        c1.final_sources['pilot']['extra_checks']['thermal']['members'][0].update(
            excluded=False, calibration_exclusions=[])
        c2 = self.calibration('C2', c1, previous_final=True).finish()
        packet = c2.build()
        self.assertNotIn('calibration_error', packet)
        self.assertTrue(packet['packet_preflight']['ready'], packet['packet_preflight'])
        current = registration.artifact_set_digest(c2.root)
        rebuilt, matches = builder.rebuild_and_compare(
            c2.root, packet, now_epoch_s=NOW, current_artifact_set_sha256=current)
        self.assertTrue(matches)
        self.assertTrue(session._record_bound(c2.root, rebuilt))
        row = rebuilt['series_history'][0]
        self.assertEqual(row['status'], 'final')
        self.assertEqual(row['eligible_benign'][pair], 1)
        self.assertEqual(row['desk_eligible_benign'][pair], 0)
        with self.assertRaisesRegex(ValueError,
                                   '^final adjudication may lower the desk counts, never raise them$'):
            series.bind_packet(c2.root, 'C3', rebuilt, authenticated_by_rebuild=True)

    def test_ACTUAL_non_successor_final_fails_binding_before_R17(self):
        c1 = self.calibration('C1', self.w1, provisional=True).finish()
        c2 = self.calibration('C2', c1).finish()
        c3 = self.calibration('C3', c2)
        c3.record['previous_final'] = self.final_descriptor(c3, c1)
        c3.finish()
        evidence = builder.GitEvidence(c3.root)
        original = builder.WindowRecord(evidence, c1.record_commit, c1.record_path)
        successor = builder.WindowRecord(evidence, c2.record_commit, c2.record_path)
        original.bind_final(successor)
        self.assertFalse(original.is_final())
        self.assertEqual(original.final_evidence(), 'no final sources')
        packet = c3.build()
        self.assertEqual(packet['calibration_error'],
                         'previous_final must name this record and carry exactly the full desk sources')
        self.assertFalse(packet['packet_preflight']['ready'])
        self.assertEqual(packet['calibration_windows'], [{}])  # fail-closed history sentinel
        self.assertNotIn('R17:', packet['calibration_error'])
        # C2 is the immediate predecessor C3 would have to finalize.
        with self.assertRaisesRegex(ValueError, '^previous_final must name this record'):
            successor.bind_final(builder.WindowRecord(evidence, c3.record_commit, c3.record_path))

    def test_missing_successor_final_refuses_R17_even_after_another_record(self):
        c1 = self.calibration('C1', self.w1, provisional=True).finish()
        c2 = self.calibration('C2', c1).finish()
        c3 = self.calibration('C3', c2).finish()
        packet = c3.build()
        self.assertFalse(packet['packet_preflight']['ready'])
        self.assertIn('R17: final eligibility of C1 must be recorded', packet['calibration_error'])
        self.assertEqual(packet['checks']['member_eligibility']['status'], 'fail')
        self.assertIn('R17: final eligibility of C1',
                      packet['checks']['member_eligibility']['basis'])

    def test_order2_desk_final_after_successor_commit_reissues_tail_and_accepts_k_plus_2(self):
        c1 = self.calibration('C1', self.w1, provisional=True).finish()
        self.assert_arm_accepts(c1, c1.build())  # C2 arms on C1, before C2 has a record.
        c2 = self.calibration('C2', c1).finish()
        stale = c2.build()
        self.assertIn('R17: final eligibility of C1', stale['calibration_error'])
        self.assertFalse(stale['packet_preflight']['ready'])
        self.assertTrue(session._record_bound(c2.root, stale))
        original_record = copy.deepcopy(c2.record)
        original_commit, original_link = c2.record_commit, dict(c2.link)
        original_series_commit = c2.series_commit
        original_bytes = builder.GitEvidence(c2.root).read(original_commit, c2.record_path)
        self.assertNotIn('previous_final', json.loads(original_bytes))
        # The desk for k completes only after the first k+1 record exists.
        c1.final_sources['pilot']['extra_checks']['thermal']['members'][0]['excluded'] = True
        c1.final_sources['exclusions']['members_excluded'] = [
            {'run_id': c1.members[0]['run_id'], 'codes': ['clock.step']}]
        c2.record['previous_final'] = self.final_descriptor(c2, c1)
        descriptor = c2.write(c2.record_path, c2.record)
        revised_bytes = (c2.root / c2.record_path).read_bytes()
        before, after = json.loads(original_bytes), json.loads(revised_bytes)
        changed = {key: (before.get(key), after.get(key)) for key in before.keys() | after.keys()
                   if key not in before or key not in after or before[key] != after[key]}
        self.assertEqual(set(changed), {'previous_final'}, changed)
        self.assertEqual(after['previous_final'], c2.record['previous_final'])
        without_final = dict(after)
        del without_final['previous_final']
        # The record's actual encoding, including its newline, is otherwise byte-identical.
        self.assertEqual((json.dumps(without_final, sort_keys=True) + '\n').encode(), original_bytes)
        self.assertEqual((json.dumps(after, sort_keys=True) + '\n').encode(), revised_bytes)
        self.assertNotEqual(original_bytes, revised_bytes)
        c2.git('add', '.')
        message = 'Re-issue C2: compared decoded records; only previous_final changed'
        c2.git('commit', '-qm', message)
        c2.record_commit = c2.git('rev-parse', 'HEAD')
        c2.link = {'commit': c2.record_commit, **descriptor}
        c2.git('update-ref', 'refs/remotes/synthetic/records', c2.record_commit)
        evidence = builder.GitEvidence(c2.root)
        self.assertEqual(evidence.read(original_commit, c2.record_path), original_bytes)
        self.assertEqual(evidence.read(c2.record_commit, c2.record_path), revised_bytes)
        self.assertEqual(c2.git('log', '-1', '--format=%B'), message)
        self.assertEqual(c2.git('rev-list', '--count', 'HEAD', '--', c2.record_path), '2')
        self.assertNotEqual(c2.record_commit, original_commit)
        self.assertEqual(c2.record, {**original_record, 'previous_final': c2.record['previous_final']})
        self.assertEqual(json.loads(c2.git('show', original_commit + ':' + c2.record_path)),
                         original_record)
        self.assertEqual(c2.git('log', '-1', '--format=%H', '--', c2.record_path), c2.record_commit)
        c2.git('merge-base', '--is-ancestor', original_commit, c2.record_commit)
        self.assertFalse(session._record_bound(c2.root, stale))
        # Re-issuing the record alone cannot use the ledger that still names its old bytes.
        with self.assertRaisesRegex(ValueError, '^series previous record binding mismatch$'):
            c2.build()
        self.assertEqual(c2.series['previous_record'], original_link)
        c2.series['previous_record'] = dict(c2.link)
        c2.series['last_passed_record'] = dict(c2.link)
        self.commit_series(c2)
        self.assertNotEqual(c2.series_commit, original_series_commit)
        evidence = builder.GitEvidence(c2.root)
        current = registration.artifact_set_digest(c2.root)
        for commit in (original_record['code_commit'], original_commit, c2.record_commit):
            self.assertEqual(builder.committed_artifact_set_digest(evidence, commit), current)
        packet = self.assert_arm_accepts(c2, c2.build())
        self.assertEqual(packet['next_window_id'], 'C3')
        self.assertEqual(packet['last_desk_passed_artifact_set_sha256'], current)
        self.assertEqual(packet['record_commit'], c2.record_commit)
        self.assertEqual(packet['series_commit'], c2.series_commit)
        self.assertEqual([(row['window'], row['status']) for row in packet['calibration_windows']],
                         [('C1', 'final'), ('C2', 'final')])
        expected = dict.fromkeys(cadence.CAL_PAIRS, 1)
        expected[cadence.CAL_PAIRS[0]] = 0
        self.assertEqual(packet['series_history'][0]['eligible_benign'], expected)
        head_ledger = json.loads(c2.git('show', 'HEAD:' + c2.series_path))
        self.assertEqual(head_ledger['previous_record'], c2.link)
        self.assertEqual(head_ledger['last_passed_record'], c2.link)
        self.assertEqual(packet['series_sha256'], builder.digest(
            (c2.root / c2.series_path).read_bytes()))
        self.assertFalse(session._record_bound(c2.root, stale))

    def test_order3_successor_held_until_prior_desk_final_then_committed_once_accepts_k_plus_2(self):
        c1 = self.calibration('C1', self.w1, provisional=True).finish()
        c2_arm = self.assert_arm_accepts(c1, c1.build())
        c2 = self.calibration('C2', c1)
        held_path = c2.dir + '/record.json'
        # Window C2 has ended and its own desk can finish, but its record is HELD.
        self.assertEqual(c2.sources['result']['chain_exit_code'], 0)
        c2.write(c2.dir + '/evidence/result.json', c2.sources['result'])
        own_receipt = final_receipt(c2, c2.sources)
        self.assertEqual(own_receipt['member_eligibility']['stage'], 'final')
        self.assertEqual(own_receipt['member_eligibility']['eligible'],
                         sorted(member['run_id'] for member in c2.members))
        self.assertFalse((c2.root / held_path).exists())
        self.assertEqual(c2.git('log', '--format=%H', '--', held_path), '')
        self.assertNotIn('previous_final', c2.record)
        # The C2-arm packet still reads C1 and its unchanged ledger, even after C2 ended.
        self.assertEqual(c2_arm['record_commit'], c1.record_commit)
        replayed = self.assert_arm_accepts(c1, c2_arm)
        self.assertEqual(replayed['next_window_id'], 'C2')
        self.assertNotIn(held_path, [row['path'] for row in replayed['evidence']])
        # C3's packet DOES need C2, but only after C1 is final and C2 can be released.
        with self.assertRaisesRegex(ValueError,
                                    '^source is not a committed regular blob: w-C2/record.json$'):
            builder.build_packet(c2.root, record_commit=c1.record_commit, record_path=held_path,
                                 series_commit=c1.series_commit, series_path=c1.series_path,
                                 pushed_ref='refs/remotes/synthetic/records', now_epoch_s=NOW,
                                 current_artifact_set_sha256=registration.artifact_set_digest(c2.root))
        evidence = builder.GitEvidence(c1.root)
        self.assertFalse(builder.WindowRecord(evidence, c1.record_commit, c1.record_path).is_final())
        # Only now does k's final desk complete; k+1 has never been committed.
        excluded = c1.members[0]['run_id']
        c1.final_sources['pilot']['extra_checks']['thermal']['members'][0]['excluded'] = True
        c1.final_sources['exclusions']['members_excluded'] = [
            {'run_id': excluded, 'codes': ['clock.step']}]
        self.assertNotIn(excluded, final_receipt(c1, c1.final_sources)['member_eligibility']['eligible'])
        self.assertEqual(c2.git('log', '--format=%H', '--', held_path), '')
        c2.previous_final = True
        c2.finish()
        self.assertEqual(c2.record_path, held_path)
        self.assertEqual(c2.git('rev-list', '--count', 'HEAD', '--', held_path), '1')
        committed = json.loads(c2.git('show', c2.record_commit + ':' + held_path))
        self.assertEqual(committed['previous_final']['record_sha256'], c1.link['sha256'])
        packet = self.assert_arm_accepts(c2, c2.build())
        self.assertEqual(packet['next_window_id'], 'C3')
        self.assertEqual([(row['window'], row['status']) for row in packet['calibration_windows']],
                         [('C1', 'final'), ('C2', 'final')])
        self.assertEqual(packet['calibration_windows'][0]['eligible_benign'][cadence.CAL_PAIRS[0]], 0)
        self.assertFalse(session._record_bound(c2.root, c2_arm))

    def test_final_receipt_and_desk_counts_recompute_despite_stale_stored_pool(self):
        c1 = self.calibration('C1', self.w1)
        # Use the real frozen pool allocation for the separate desk_row reader.
        manifest = series.candidate()
        allocations = series.selected(manifest, 'C1')['members']
        c1.members = [{'run_id': (f'anchor-{m["ordinal"]}' if m['pool'] == 'anchor' else
                                 series.pack_id('C1') + f'-e{m["ordinal"]:02}'),
                       'role': 'anchor' if m['pool'] == 'anchor' else 'D',
                       'pool_role': m['pool'], 'condition': m['condition'],
                       'task_pair': series.PAIR_KEYS[m['pair']]} for m in allocations]
        thermal = c1.sources['pilot']['extra_checks']['thermal']
        thermal['members'] = [{'id': m['run_id'], 'excluded': False,
                               'calibration_exclusions': [], 'flags': []} for m in c1.members]
        stored_pool = [m['run_id'] for m in c1.members if m['pool_role'] == 'calibration']
        c1.sources['pilot']['extra_checks']['pool_members'] = {'calibration': stored_pool}
        c1.series['pool_members'] = list(stored_pool)
        c1.series_path = builder.SERIES_PATH
        self.commit_series(c1)
        ledger_bytes = (c1.root / c1.series_path).read_bytes()
        before = final_receipt(c1, c1.sources)
        excluded = stored_pool[0]
        pair = next(m['task_pair'] for m in c1.members if m['run_id'] == excluded)
        record = next(r for r in thermal['members'] if r['id'] == excluded)
        light_triage.apply_harvest_codes(record, ['clock.step'])
        c1.sources['exclusions']['members_excluded'] = [{'run_id': excluded, 'codes': ['clock.step']}]
        after = final_receipt(c1, c1.sources)
        self.assertIn(excluded, stored_pool)
        self.assertIn(excluded, before['member_eligibility']['eligible'])
        self.assertNotIn(excluded, after['member_eligibility']['eligible'])
        self.assertEqual(after['member_eligibility']['members'][excluded]['reasons'], ['harvest.excluded'])
        expected = dict(before['calibration_row']['eligible_benign'])
        expected[pair] -= 1
        self.assertEqual(after['calibration_row']['eligible_benign'], expected)
        self.assertEqual((c1.root / c1.series_path).read_bytes(), ledger_bytes)
        stored_pilot = json.loads((c1.root / c1.dir / 'desk-reader/PILOT.json').read_bytes())
        self.assertIn(excluded, stored_pilot['extra_checks']['pool_members']['calibration'])
        # desk_row uses the manifest's planned pool labels plus current captured/excluded rows.
        rows = [{'run_id': r['id'], 'captured': True, 'excluded': r['excluded']} for r in thermal['members']]
        desk = series.desk_row(manifest, 'C1', rows, True)
        self.assertEqual(desk['desk_eligible_benign'], expected)
        next(r for r in rows if r['run_id'] == excluded)['excluded'] = False
        control = series.desk_row(manifest, 'C1', rows, True)
        self.assertEqual(control['desk_eligible_benign'], before['calibration_row']['eligible_benign'])


if __name__ == '__main__':
    unittest.main()
