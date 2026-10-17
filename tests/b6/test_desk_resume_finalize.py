"""Stopped block-6 sessions use real recovery, ledger, desk and harvest."""
import json
from pathlib import Path
import subprocess
from unittest import mock

from joulewise import calibration_ledger as ledger, window_lineage
from joulewise.b5 import chain, plan
from joulewise.b6.driver_lane import metadata_path, read, write
from joulewise.b6.lanes import Prepared
from tests.b6.round_support import Round
from tests.b6.support import DeskCase


class DeskResumeFinalizeTests(DeskCase):
    def stopped_round(self, control):
        r = Round(self.root)
        r.until('SESSION_RUN')
        write(r.control, {**read(r.control), **control})
        r.loop.tick()  # Install/launch; driver status has not polled yet.
        return r

    def events(self, r):
        prepared = Prepared(**r.state()['session']['prepared'])
        md = read(metadata_path(prepared))
        return md, [row for line in (r.measurement / plan.DEFAULT_LEDGER_RELATIVE).read_text().splitlines()
                    if (row := json.loads(line)).get('session_id') == md['inputs']['bracket_session_id']
                    and row.get('event')]

    def test_unfinalized_pre_40ms_keeps_physical_abort(self):
        r = self.stopped_round({'unfinalized': 'pre', 'b_fiducial': '0.040', 'stop': 'night_stopped_disk_low'})
        r.until('ROTATE')
        md, rows = self.events(r)
        final = next(row for row in rows if row['event'] == ledger.BRACKET_SESSION_FINALIZATION_EVENT)
        self.assertEqual((final['slot'], final['disposition']), ('pre', 'valid'))
        self.assertEqual(rows[-1]['reason'], 'night_stopped_disk_low')
        self.assertEqual(md['bracket_abort']['reason'], 'night_stopped_disk_low')
        self.assertTrue(md['bracket_resume'][0]['exceeds_prior_level_screen'])
        self.assertFalse(plan.ledger_head_status(r.measurement)['blocking'])

    def test_unfinalized_post_40ms_finalizes_valid_and_keeps_window_stop(self):
        r = self.stopped_round({'unfinalized': 'post', 'b_fiducial': '0.040', 'stop': 'night_window_exceeded'})
        r.until('ROTATE')
        md, rows = self.events(r)
        self.assertEqual((rows[-1]['slot'], rows[-1]['disposition']), ('post', 'valid'))
        # Post is terminal: no second terminal abort is legal after it.
        self.assertFalse(any(row['event'] == ledger.BRACKET_SESSION_ABORT_EVENT for row in rows))
        self.assertEqual(read(Path(md['paths']['custody']) / 'night/result.json')['aborted_reason'],
                         'night_window_exceeded')
        self.assertEqual(r.state()['attempts'][0]['line']['physics_stop'], 'time_limit')
        self.assertTrue(md['bracket_resume'][0]['exceeds_prior_level_screen'])

    def test_block5_recovery_retains_systematic_invalid_pre_abort(self):
        r = self.stopped_round({'unfinalized': 'pre', 'b_fiducial': '0.040', 'stop': 'night_stopped_disk_low'})
        # Same interrupted capture and CLI, but the window selects block 5.
        prepared = Prepared(**r.state()['session']['prepared'])
        p = read(prepared.plan_path)
        p['hazard_window']['bindings'].pop('capture_screen')
        write(Path(p['custody_root']) / 'night_plan.json', p)
        r.until('ROTATE')
        _, rows = self.events(r)
        final = next(row for row in rows if row['event'] == ledger.BRACKET_SESSION_FINALIZATION_EVENT)
        self.assertEqual(final['disposition'], 'systematic-invalid')
        self.assertEqual(rows[-1]['reason'], 'pre_capture_systematic-invalid')

    def test_resume_commits_then_times_out_is_finalized_without_failure_flag(self):
        r = self.stopped_round({'unfinalized': 'pre', 'b_fiducial': '0.040', 'stop': 'night_stopped_disk_low'})
        runner = r.lanes.desk.run
        attempts = []
        def commit_then_timeout(argv, **kwargs):
            result = runner(argv, **kwargs)
            if 'resume-finalize' in argv:
                attempts.append(result.returncode)
                if len(attempts) == 1:
                    self.assertEqual(result.returncode, 0, result.stderr)
                    raise subprocess.TimeoutExpired(argv, kwargs['timeout'])
            return result
        r.lanes.desk.run = commit_then_timeout
        r.until('ROTATE')
        md, rows = self.events(r)
        self.assertEqual(len(attempts), 2)
        self.assertNotEqual(attempts[1], 0)  # The retry finds an already finalized slot.
        self.assertEqual(md['bracket_resume'][0]['status'], 'FINALIZED')
        final = next(row for row in rows if row['event'] == ledger.BRACKET_SESSION_FINALIZATION_EVENT)
        self.assertEqual((final['slot'], final['disposition']), ('pre', 'valid'))
        self.assertEqual(md['bracket_abort']['reason'], 'night_stopped_disk_low')
        flags = r.state()['attempts'][0]['line']['window_flags']
        self.assertNotIn('records.resume_finalize_failed', flags)
        self.assertNotIn('records.pin_ledger', flags)
        self.assertFalse(plan.ledger_head_status(r.measurement)['blocking'])

    def test_failed_resume_with_lineage_writes_slot_flag_to_custody(self):
        r = self.stopped_round({'unfinalized': 'pre', 'b_fiducial': '0.040', 'stop': 'night_stopped_disk_low'})
        prepared = Prepared(**r.state()['session']['prepared'])
        md = read(metadata_path(prepared))
        custody = Path(md['paths']['custody'])
        # The fake launcher bypasses run_night's locator publication. Publish
        # it for this desk path without changing the legacy-root regression.
        write(Path(md['runs_roots'][0]) / window_lineage.LOCATOR_BASENAME, {
            'schema_version': window_lineage.HAZARD_LOCATOR_SCHEMA,
            'launch_lineage': {'window_context': {'custody_root': str(custody)}}})
        runner = r.lanes.desk.run
        timeouts = []
        def fail_resume(argv, **kwargs):
            if 'resume-finalize' in argv:
                timeouts.append(kwargs['timeout'])
                return subprocess.CompletedProcess(argv, 3, '', 'synthetic resume failure')
            return runner(argv, **kwargs)
        r.lanes.desk.run = fail_resume
        r.until('ROTATE')
        md, rows = self.events(r)
        self.assertEqual(timeouts, [120, 600])
        self.assertEqual(md['bracket_resume'][0]['status'], 'FAILED')
        self.assertEqual(rows[-1]['reason'], 'night_stopped_disk_low')
        self.assertIn('records.resume_finalize_failed', r.state()['attempts'][0]['line']['window_flags'])
        flags = [json.loads(line) for path in (custody / 'flags').glob('*.jsonl')
                 for line in path.read_text().splitlines()]
        failed = [flag for flag in flags if flag['code'] == 'records.resume_finalize_failed']
        self.assertEqual(len(failed), 1)
        self.assertEqual(failed[0]['observed'], {
            'slot': 'pre', 'session_id': md['inputs']['bracket_session_id']})
        self.assertEqual(failed[0]['scope']['level'], 'window')

    def test_bare_named_and_unmapped_exits_abort_by_table(self):
        # One real stopped session per case, with the production driver
        # interpreting the exit and the desk closing its ledger.
        for rc, reason in ((13, 'operative_bound_above_stop'), (12, 'pre_calibration_screen_failed'),
                           (11, 'pre_calibration_capture_failed'), (10, 'reservation_failed'),
                           (91, 'chain_exit:91')):
            with self.subTest(rc=rc):
                root = self.root / str(rc)
                root.mkdir()
                with mock.patch.object(self, 'root', root):
                    r = self.stopped_round({'stop': 'operative_bound_above_stop'})
                prepared = Prepared(**r.state()['session']['prepared'])
                md = read(metadata_path(prepared))
                night = Path(md['paths']['custody']) / 'night'
                rows = [row for row in chain.stage_journal(night) if row.get('stage_id') != 'chain.stop']
                (night / chain.STAGE_JOURNAL).write_text(''.join(json.dumps(row) + '\n' for row in rows))
                write(night / 'chain.exited', {'epoch_s': 1786216000, 'exit_code': rc})
                write(night / 'result.json', {'chain_exit_code': rc, 'verdict': 'CHAIN_STOPPED'})
                r.until('SESSION_DESK')
                # Unmapped exits hold after desk, so exercise that one desk tick.
                r.loop.tick()
                md, events = self.events(r)
                self.assertEqual(events[-1]['reason'], reason)
                self.assertEqual(md['bracket_abort']['reason'], reason)
