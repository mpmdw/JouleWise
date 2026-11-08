"""Synthetic W1/D meter stream; no USB, SMC, model or study-data access."""
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from joulewise.align import energy_residual as er
from joulewise.align.apple import km003c as meter
from joulewise.align.records import Episode, Turn, to_jsonable
from joulewise.external import km003c_parse as kp
from scripts import align_v4_kit as kit

NS = 1_000_000_000
OFFSET = 7 * NS


def fake_stream(path, *, omit=(), status='streaming', end=5000):
    """50 SPS, 28 V * 1 A, identity device/RAW fit + distinct mono offset."""
    lines = [{'k': 'h', 'schema': 'joulewise.km003c_stream.v1', 'status': status,
              'rate_idx': 2, 'start_raw_ns': OFFSET, 'start_mono_ns': 0}]
    if status == 'streaming':
        for ms in range(0, end + 1, 20):
            if ms in omit:
                continue
            payload = kp.SAMPLE.pack(ms, 0, 28_000_000, 1_000_000, 0, 0, 0, 0)
            lines.append({'k': 'b', 'tx': OFFSET + ms * 1_000_000 - 1000,
                          'rx': OFFSET + ms * 1_000_000, 'rt': 0,
                          'n': 1, 'p': payload.hex(), 'smc': {'B0AC': 0, 'B0AV': 12000}})
    lines.append({'k': 't', 'end_raw_ns': OFFSET + end * 1_000_000,
                  'end_mono_ns': end * 1_000_000, 'stop_reason': 'signal 15'})
    path.write_text(''.join(json.dumps(line) + '\n' for line in lines))
    return kp.parse(path)


def episode():
    return Episode(episode_id='synthetic', task_pair='synthetic', condition='benign',
                   agent_model='synthetic', endpoint='synthetic',
                   seed=1, clock_domain='synthetic.monotonic_ns', start_ns=2*NS, end_ns=4*NS,
                   turns=(Turn(0, 2*NS, 3*NS, 10, 2, 3),))


class MemberTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / 'stream-001.jsonl'

    def capture(self, stream, **kwargs):
        return meter.capture_member([(self.path.name, stream)], member_span=(NS, 4*NS),
                                    baseline_span=(NS, 2*NS), episode=episode(), **kwargs)

    def test_integral_and_five_term_residual_use_dc_units(self):
        model = er.EnergyModel(('intercept', 'prefill_tokens', 'decode_tokens',
                                'context_decode_tokens', 'context_prefill_tokens'),
                               (1, 2, 3, 4, 5), ((0,)*5,)*5, 1, 10)
        row = self.capture(fake_stream(self.path), model=model)
        self.assertEqual(row['status'], 'available')
        self.assertTrue(row['print_only'])
        self.assertEqual(row['label'], 'SECONDARY / not yet registered')
        self.assertEqual(row['dc_in_energy_j'], 84)
        self.assertEqual(row['episode_dc_in_energy_j'], 56)
        self.assertEqual(row['baseline_w'], 28)
        self.assertEqual(row['dc_in_delta_j'], 0)
        # Five terms: 1 + 2*2 + 3*3 + 4*10*3 + 5*10*2 = 234 J.
        self.assertEqual(row['predicted_j'], 234)
        self.assertEqual(row['dc_in_residual_j'], -234)
        self.assertIsNone(row['score'])  # no invented meter uncertainty / threshold

    def test_one_dropped_sample_inside_baseline_or_member_means_missing_dc(self):
        for ms in (1500, 2500, 3500):
            with self.subTest(ms=ms):
                row = self.capture(fake_stream(self.path, omit=(ms,)))
                self.assertEqual(row['status'], 'missing')
                self.assertIn('meter.member_gap', row['flags'])
                self.assertIsNone(row['dc_in_energy_j'])
                self.assertTrue(row['powermetrics_admissibility_unchanged'])

    def test_gap_outside_member_does_not_remove_dc(self):
        row = self.capture(fake_stream(self.path, omit=(400,)))
        self.assertEqual(row['status'], 'available')

    def test_absent_or_short_stream_is_never_silent(self):
        for stream in (fake_stream(self.path, status='absent'), fake_stream(self.path, end=3000)):
            row = self.capture(stream)
            self.assertEqual(row['status'], 'missing')
            self.assertTrue(row['flags'])
            self.assertIsNone(row['dc_in_residual_j'])

    def test_unclosed_stream_salvages_members_it_fully_covers_and_flags_the_rest(self):
        # Smoke G3: the reader died, so the stream has no closing line. A member inside the
        # complete records keeps DC (disclosed); one past the last valid record is missing.
        covered = self.capture(replace(fake_stream(self.path), trailer=None))
        self.assertEqual(covered['status'], 'available')
        self.assertIn('meter.stream_unclosed', covered['flags'])
        self.assertEqual(covered['dc_in_energy_j'], 84)
        truncated = replace(fake_stream(self.path, end=3000), trailer=None)
        row = self.capture(truncated)
        self.assertEqual(row['status'], 'missing')
        self.assertIn('meter.member_uncovered', row['flags'])
        self.assertIn('meter.stream_unclosed', row['flags'])
        self.assertIsNone(row['dc_in_energy_j'])

    def test_protocol_error_inside_member_is_missing_even_with_contiguous_samples(self):
        stream = fake_stream(self.path)
        stream.errors.append({'k': 'e', 'rx': OFFSET + 2500_000_000, 'usb_error': 'synthetic'})
        self.assertIn('meter.member_error', self.capture(stream)['flags'])

    def test_restart_streams_are_not_spliced_across_a_member(self):
        first = fake_stream(self.path, end=2500)
        second = fake_stream(self.path)
        second.host_ns = second.host_ns[125:]
        second.watts = second.watts[125:]
        row = meter.capture_member([('one', first), ('two', second)],
                                   member_span=(NS, 4*NS), baseline_span=(NS, 2*NS), episode=episode())
        self.assertEqual(row['status'], 'missing')


class KitTests(unittest.TestCase):
    def test_generated_collection_plan_explicitly_enables_the_existing_reader(self):
        files = kit.build_files()
        plan = json.loads(files[kit.KIT / 'collection_plan.json'])
        self.assertEqual(plan['runtime_requirements']['km003c'], meter.REQUIREMENT)

    def test_require_w1_ready_refuses_missing_disabled_or_wrong_reader_before_other_inputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / kit.KIT / 'collection_plan.json'
            path.parent.mkdir(parents=True)
            for value in (None, {**meter.REQUIREMENT, 'enabled': False},
                          {**meter.REQUIREMENT, 'reader': 'another-reader'}):
                path.write_text(json.dumps({'runtime_requirements': {'km003c': value}}))
                with self.subTest(value=value), self.assertRaisesRegex(ValueError, 'RUN_STATE 210.*squeeze'):
                    kit.require_w1_ready(Path(tmp))

    def test_a_missing_plan_refusal_names_the_ruling(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, 'RUN_STATE 210.*squeeze'):
                kit.require_w1_ready(Path(tmp))


class DeskTests(unittest.TestCase):
    def fixture(self, root):
        custody, runs = root / 'custody', root / 'runs'
        stream = custody / 'hazards/meter/stream-001.jsonl'
        stream.parent.mkdir(parents=True)
        fake_stream(stream)
        (custody / 'night').mkdir()
        (custody / 'night/hazard_result.json').write_text(json.dumps({'meter': {
            'streams': [{'path': 'hazards/meter/stream-001.jsonl',
                         'sha256': hashlib.sha256(stream.read_bytes()).hexdigest()}],
            'stop': {'proven_stopped': True}}}))
        bundle = runs / 'member'
        (bundle / 'outputs').mkdir(parents=True)
        (bundle / 'outputs/align_episode.json').write_text(json.dumps(to_jsonable(episode())))
        stamps = {name: {'monotonic_before_s': a, 'monotonic_after_s': b, 'epoch_s': 100 + a}
                  for name, a, b in (('pre_spawn', 1, 1), ('sampling_started', 2, 2),
                                     ('sampling_stopped', 4, 4), ('post_parse', 4, 4))}
        (bundle / 'metadata.json').write_text(json.dumps({'uncertainty_evidence': {
            'clock_anchor': {'clock_stamps': stamps}}}))
        events = [{'event_type': 'stage_started', 'phase': 'idle_baseline',
                   'timestamp_s': 101, 'metadata': {'monotonic_ns': NS}},
                  {'event_type': 'stage_completed', 'phase': 'idle_baseline', 'timestamp_s': 102}]
        (bundle / 'events.jsonl').write_text(''.join(json.dumps(e) + '\n' for e in events))
        plan = [{'run_id': 'member', 'condition': 'benign', 'task_pair': 'synthetic',
                 'model_id': 'synthetic', 'seed_index': 1}]
        summaries = [{'run_id': 'member', 'excluded': False, 'summary': {'configuration': {'model': 'synthetic'}}}]
        return custody, runs, stream, plan, summaries

    def test_desk_authenticates_custody_and_never_mutates_rail_admission(self):
        with tempfile.TemporaryDirectory() as tmp:
            custody, runs, stream, plan, summaries = self.fixture(Path(tmp))
            before = json.dumps(summaries)
            report = meter.session_report(custody, plan, runs, summaries)
            row = report['members']['member']
            self.assertEqual(row['dc_in_energy_j'], 84)
            self.assertEqual(report['sources'][0]['sha256'], hashlib.sha256(stream.read_bytes()).hexdigest())
            self.assertEqual(json.dumps(summaries), before)
            # Insufficient benign turns must not fabricate a usable DC fit.
            self.assertEqual(row['residual_status'], 'dc_fit_unavailable')
            self.assertIsNone(row['dc_in_residual_j'])
            self.assertNotIn('instrument_ok', report)
            stream.write_text(stream.read_text() + '\n')
            row = meter.session_report(custody, plan, runs, summaries)['members']['member']
            self.assertEqual(row['status'], 'missing')
            self.assertIn('meter.custody_hash_mismatch', row['flags'])

    def crashed_fixture(self, root, *, record_hash):
        """A stream cut mid-line after 3.4 s with no closing line; two members at 1-3 s and 3-4.5 s."""
        custody, runs, stream, plan, summaries = self.fixture(root)
        fake_stream(stream)
        lines = stream.read_text().split('\n')
        cut = next(i for i, line in enumerate(lines) if '"rx": %d' % (OFFSET + 3_400_000_000) in line)
        stream.write_text('\n'.join(lines[:cut]) + '\n' + lines[cut][:25])      # half a line, no trailer
        record = json.loads((custody / 'night/hazard_result.json').read_text())
        record['meter']['streams'][0]['sha256'] = hashlib.sha256(stream.read_bytes()).hexdigest() if record_hash else None
        if not record_hash:
            del record['meter']['streams'][0]['sha256']
        (custody / 'night/hazard_result.json').write_text(json.dumps(record))
        # the first member ends at 3 s, inside the complete records (last valid sample is about 3.38 s)
        early = json.loads((runs / 'member/metadata.json').read_text())
        for key in ('sampling_stopped', 'post_parse'):
            stamps = early['uncertainty_evidence']['clock_anchor']['clock_stamps']
            stamps[key] = {**stamps[key], 'monotonic_before_s': 3, 'monotonic_after_s': 3}
        (runs / 'member/metadata.json').write_text(json.dumps(early))
        shortened = replace(episode(), end_ns=3*NS, turns=(Turn(0, 2*NS, 3*NS, 10, 2, 3),))
        (runs / 'member/outputs/align_episode.json').write_text(json.dumps(to_jsonable(shortened)))
        # a second member, later than the last valid record
        late = runs / 'late'
        late.mkdir()
        for name in ('metadata.json', 'events.jsonl'):
            (late / name).write_text((runs / 'member' / name).read_text())
        (late / 'outputs').mkdir()
        shifted = replace(episode(), start_ns=3*NS, end_ns=4*NS, turns=(Turn(0, 3*NS, 4*NS, 10, 2, 3),))
        (late / 'outputs/align_episode.json').write_text(json.dumps(to_jsonable(shifted)))
        late_meta = json.loads((late / 'metadata.json').read_text())
        stamps = late_meta['uncertainty_evidence']['clock_anchor']['clock_stamps']
        for key in ('sampling_stopped', 'post_parse'):
            stamps[key] = {**stamps[key], 'monotonic_before_s': 5, 'monotonic_after_s': 5}
        (late / 'metadata.json').write_text(json.dumps(late_meta))
        plan.append({**plan[0], 'run_id': 'late', 'seed_index': 2})
        summaries.append({**summaries[0], 'run_id': 'late'})
        return custody, runs, stream, plan, summaries

    def test_crashed_reader_with_a_recorded_digest_keeps_dc_before_the_gap_and_never_fabricates_samples(self):
        # Smoke G3: a listed, supervised stream whose recorded digest matches its (truncated) bytes.
        with tempfile.TemporaryDirectory() as tmp:
            custody, runs, stream, plan, summaries = self.crashed_fixture(Path(tmp), record_hash=True)
            parsed = kp.parse(stream)
            self.assertIsNone(parsed.trailer)
            self.assertLess(parsed.host_ns[-1], OFFSET + 3_400_000_000)           # only complete records survive
            report = meter.session_report(custody, plan, runs, summaries)
            before, after = report['members']['member'], report['members']['late']
            self.assertEqual(before['status'], 'available', before['flags'])
            self.assertEqual(before['dc_in_energy_j'], 56)                       # 28 W over its 2 s, as recorded
            self.assertIn('meter.stream_unclosed', before['flags'])
            self.assertEqual(after['status'], 'missing')
            self.assertIn('meter.member_uncovered', after['flags'])
            self.assertIsNone(after['dc_in_energy_j'])
            self.assertIsNone(after['dc_in_residual_j'])

    def test_unrecorded_digest_means_exclude_not_salvage(self):
        # A listed stream whose digest the supervisor never recorded: not authenticated, so excluded.
        with tempfile.TemporaryDirectory() as tmp:
            custody, runs, stream, plan, summaries = self.crashed_fixture(Path(tmp), record_hash=False)
            row = meter.session_report(custody, plan, runs, summaries)['members']['member']
            self.assertEqual(row['status'], 'missing')
            self.assertIn('meter.custody_digest_unrecorded', row['flags'])
            self.assertNotIn('meter.stream_unlisted', row['flags'])
            self.assertIsNone(row['dc_in_energy_j'])

    def test_unrecorded_stream_means_never_available_dc(self):
        # A file the custody manifest never names (a stray or copied stream): separate case, own flag.
        with tempfile.TemporaryDirectory() as tmp:
            custody, runs, stream, plan, summaries = self.crashed_fixture(Path(tmp), record_hash=True)
            stream.rename(stream.with_name('stream-099.jsonl'))
            row = meter.session_report(custody, plan, runs, summaries)['members']['member']
            self.assertEqual(row['status'], 'missing')
            self.assertIn('meter.stream_unlisted', row['flags'])
            self.assertNotIn('meter.custody_digest_unrecorded', row['flags'])
            self.assertIsNone(row['dc_in_energy_j'])

    def test_a_stray_stream_cannot_preempt_the_authenticated_one(self):
        with tempfile.TemporaryDirectory() as tmp:
            custody, runs, stream, plan, summaries = self.fixture(Path(tmp))
            stray = stream.with_name('stream-000.jsonl')                          # sorts first, never listed
            rows = [json.loads(line) for line in stream.read_text().splitlines()]
            for row in rows:
                if row['k'] == 'b':
                    fields = list(kp.SAMPLE.unpack(bytes.fromhex(row['p'])))
                    fields[3] *= 2
                    row['p'] = kp.SAMPLE.pack(*fields).hex()
            stray.write_text(''.join(json.dumps(r) + '\n' for r in rows if r['k'] != 't'))
            result = meter.session_report(custody, plan, runs, summaries)['members']['member']
            self.assertEqual((result['status'], result['dc_in_energy_j']), ('available', 84.))
            self.assertEqual(result['stream'], 'hazards/meter/stream-001.jsonl')
            self.assertIn('meter.stream_unlisted', result['flags'])               # disclosed, never used

    def test_no_supervisor_record_means_no_stream_has_provenance(self):
        with tempfile.TemporaryDirectory() as tmp:
            custody, runs, stream, plan, summaries = self.crashed_fixture(Path(tmp), record_hash=True)
            (custody / 'night/hazard_result.json').unlink()
            row = meter.session_report(custody, plan, runs, summaries)['members']['member']
            self.assertEqual(row['status'], 'missing')
            self.assertIn('meter.unsupervised', row['flags'])
            self.assertIsNone(row['dc_in_energy_j'])

    def test_closed_streams_with_a_missing_or_wrong_hash_are_excluded_with_their_own_flags(self):
        with tempfile.TemporaryDirectory() as tmp:
            custody, runs, stream, plan, summaries = self.fixture(Path(tmp))
            record = json.loads((custody / 'night/hazard_result.json').read_text())
            del record['meter']['streams'][0]['sha256']
            (custody / 'night/hazard_result.json').write_text(json.dumps(record))
            row = meter.session_report(custody, plan, runs, summaries)['members']['member']
            self.assertEqual(row['status'], 'missing')
            self.assertIn('meter.custody_digest_unrecorded', row['flags'])
        with tempfile.TemporaryDirectory() as tmp:
            custody, runs, stream, plan, summaries = self.crashed_fixture(Path(tmp), record_hash=True)
            record = json.loads((custody / 'night/hazard_result.json').read_text())
            record['meter']['streams'][0]['sha256'] = '0' * 64            # recorded, but not these bytes
            (custody / 'night/hazard_result.json').write_text(json.dumps(record))
            row = meter.session_report(custody, plan, runs, summaries)['members']['member']
            self.assertEqual(row['status'], 'missing')
            self.assertIn('meter.custody_hash_mismatch', row['flags'])

    def test_gap_flag_is_persisted_per_member_in_the_desk_addendum(self):
        with tempfile.TemporaryDirectory() as tmp:
            custody, runs, path, plan, summaries = self.fixture(Path(tmp))
            fake_stream(path, omit=(2500,))
            hazard = custody / 'night/hazard_result.json'
            record = json.loads(hazard.read_text())
            record['meter']['streams'][0]['sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
            hazard.write_text(json.dumps(record))
            row = meter.session_report(custody, plan, runs, summaries)['members']['member']
            self.assertEqual(row['status'], 'missing')
            self.assertIn('meter.member_gap', row['flags'])
            self.assertFalse(summaries[0]['excluded'])

    def test_desk_fits_a_separate_dc_model_on_benign_turns(self):
        with tempfile.TemporaryDirectory() as tmp:
            custody, runs, _, plan, summaries = self.fixture(Path(tmp))
            turns = tuple(Turn(i, 2*NS + i*200_000_000, 2*NS + (i+1)*200_000_000,
                               c, p, d) for i, (c, p, d) in enumerate(
                                   ((1, 2, 3), (2, 3, 1), (4, 1, 5), (5, 4, 2),
                                    (3, 5, 4), (7, 2, 6), (6, 6, 3), (8, 3, 7))))
            path = runs / 'member/outputs/align_episode.json'
            path.write_text(json.dumps(to_jsonable(replace(episode(), turns=turns))))
            report = meter.session_report(custody, plan, runs, summaries)
            row = report['members']['member']
            self.assertEqual(report['models'][0]['training_run_ids'], ['member'])
            self.assertEqual(report['models'][0]['model']['n_turns'], 8)
            self.assertEqual(row['residual_status'], 'diagnostic_only')
            self.assertAlmostEqual(row['dc_in_residual_j'], 0)
            self.assertIsNone(row['score'])
            summaries[0]['excluded'] = True
            excluded = meter.session_report(custody, plan, runs, summaries)
            self.assertEqual(excluded['models'][0]['training_run_ids'], [])
            self.assertEqual(excluded['members']['member']['residual_status'], 'dc_fit_unavailable')

    def test_parser_failure_is_a_per_member_missing_channel(self):
        with tempfile.TemporaryDirectory() as tmp:
            custody, runs, _, plan, summaries = self.fixture(Path(tmp))
            with patch.object(kp, 'parse', side_effect=RuntimeError('synthetic parser failure')):
                row = meter.session_report(custody, plan, runs, summaries)['members']['member']
            self.assertEqual(row['status'], 'missing')
            self.assertIn('meter.stream_unreadable:RuntimeError', row['flags'])
            self.assertFalse(summaries[0]['excluded'])

    def test_unexpected_dc_desk_failure_cannot_add_an_instrument_gate(self):
        from scripts import align_v4_session as session
        from contextlib import redirect_stdout
        import io
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            custody, runs, _, plan, summaries = self.fixture(root)
            plan[0]['ac_powermode'] = 0
            reg = root / 'kit/registration'
            reg.mkdir(parents=True)
            (reg.parent / 'collection_plan.json').write_text(json.dumps({'members': plan}))
            state = {'measurement_root': str(root), 'registration_dir': str(reg),
                     'inputs': {'custody_root': str(custody)}}
            with patch.object(session, 'bundle_ac_powermode', return_value=0), \
                    patch.object(meter, 'session_report', side_effect=RuntimeError('synthetic desk error')), \
                    redirect_stdout(io.StringIO()):
                checks, report = session.powermode_desk_check(state=state, members=summaries,
                                                              runs_root=runs, kit_path=kit.KIT)
            self.assertEqual(checks, {'ac_powermode_members': True, 'v4_registration_evidence': False})
            self.assertIn('registration_error', report)
            self.assertFalse(any('meter' in key or 'km003c' in key for key in checks))
            row = report['km003c']['members']['member']
            self.assertEqual(row['status'], 'missing')
            self.assertIn('meter.desk_failed:RuntimeError', row['flags'])


class NightChainTests(unittest.TestCase):
    def test_existing_block_supervisor_covers_first_idle_through_last_member_and_hashes(self):
        # Production run_night -> HAZARD_PACK driver; only hardware/children
        # are fake. A short synthetic chain stands for W1's member sequence.
        import shlex
        from tests.test_b5_driver import Harness
        from tests.test_b5_driver_p3 import fake_meter_argv, journal
        from joulewise.b5 import driver
        harness = Harness(self, g10=False)
        # ps/pgrep are unavailable in the sandbox. This fixture chain has no
        # background children; its process census is a synthetic host seam.
        # Retain Popen handles so cleanup never needs a machine-wide census.
        import subprocess
        from tests.process_reaper import kill_and_wait
        children = []
        real_popen = subprocess.Popen

        def popen(*args, **kwargs):
            process = real_popen(*args, **kwargs)
            children.append(process)
            return process

        self.addCleanup(lambda: [kill_and_wait(p) for p in children])
        census = patch.object(harness.driver, '_group_census', return_value=(True, ['synthetic absence']))
        census.start()
        self.addCleanup(census.stop)
        original_seams = harness.seams

        def seams():
            return replace(original_seams(), popen=popen)

        harness.driver._hazard_seams = seams
        stream = harness.custody / 'hazards/meter/stream-001.jsonl'
        markers = harness.custody / 'member-markers'
        harness.replace_chain('#!/bin/zsh -f\n'
            'for i in {1..100}; do\n'
            f'  [[ -s {shlex.quote(str(stream))} ]] && break\n'
            '  /bin/sleep 0.05\n'
            'done\n'
            f'[[ -s {shlex.quote(str(stream))} ]] || exit 90\n'
            f'print idle_baseline_started > {shlex.quote(str(markers))}\n'
            '/bin/sleep 0.1\n'
            f'[[ $(/usr/bin/tail -1 {shlex.quote(str(stream))}) != *stop_reason* ]] || exit 91\n'
            f'print last_member_finished >> {shlex.quote(str(markers))}\n')
        harness.meter_argv = fake_meter_argv()
        self.assertEqual(harness.run(), harness.driver.EXIT_GO,
                         json.dumps({'result': harness.result(), 'hazard': harness.hazard()}, default=str))
        self.assertEqual(markers.read_text().splitlines(), ['idle_baseline_started', 'last_member_finished'])
        captured = harness.hazard()['meter']
        self.assertTrue(captured['stop']['proven_stopped'])
        self.assertEqual(captured['streams'][0]['sha256'], hashlib.sha256(stream.read_bytes()).hexdigest())
        events = journal(harness.night / driver.METER_JOURNAL)
        self.assertEqual([e['event'] for e in events], ['start', 'stop'])
        chain_started = json.loads((harness.night / 'chain.started').read_text())
        chain_exited = json.loads((harness.night / 'chain.exited').read_text())
        self.assertLessEqual(events[0]['at']['monotonic_ns'], chain_started['monotonic_ns'])
        self.assertGreaterEqual(events[-1]['requested']['monotonic_ns'], chain_exited['monotonic_ns'])
        self.assertEqual(json.loads(stream.read_text().splitlines()[-1])['k'], 't')

    def test_w1_uses_the_block_production_reader_command_without_starting_hardware(self):
        from joulewise.b5 import driver
        with tempfile.TemporaryDirectory() as tmp:
            custody = Path(tmp)
            request = driver.MonitorRequest(None, custody / 'plan.json', custody, custody / 'night', 1)
            argv = driver.production_seams(kit.ROOT).meter_argv(request)
            self.assertEqual(argv[-3:], [str(kit.ROOT / meter.REQUIREMENT['reader']),
                                        '--out', str(custody / 'hazards/meter/stream-001.jsonl')])


if __name__ == '__main__':
    unittest.main()
