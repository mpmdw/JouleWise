"""Merge c84: R22 disclosure must remain compatible with R17 finality. Synthetic only.

The two positive witnesses intentionally fail on c84df94bf; real exclusions
must continue to block the required full desk. No production fix is included.
"""
import contextlib
import io
import json
import subprocess
import tempfile
from types import SimpleNamespace
import unittest

from tests.align import test_harvest_off as fixtures  # installs the synthetic-only import guard
from tests.align.test_v4_next_arm_packet import Scenario, evaluate
from joulewise.align.apple import v4_contention
from scripts import align_pilot_session as pilot
from scripts import align_v4_harvest_off as runner
from scripts import align_v4_session as session


setUpModule = fixtures.setUpModule
tearDownModule = fixtures.tearDownModule


class NativeFinalityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = fixtures.SyntheticV4SessionE2ETests
        cls.fixture.setUpClass()
        cls.addClassCleanup(cls.fixture.tearDownClass)

    def test_completed_native_desk_can_finalize_with_disclosure_only_contention(self):
        fixture = self.fixture
        victim = fixture.rows[0]['run_id']

        def harvest(argv, **kwargs):
            derived = fixture.session / 'archive/derived'
            derived.mkdir(parents=True, exist_ok=True)
            (derived / 'exclusions.json').write_text(json.dumps({'members_excluded': [
                {'run_id': victim, 'codes': ['contention.unmeasured']}]}))
            (derived / 'flags.jsonl').write_text('')
            return subprocess.CompletedProcess(argv, 0, stdout='', stderr='')

        with contextlib.redirect_stdout(io.StringIO()):
            desk = session.desk(fixture.session, run=harvest, harvest_workers=1)
        self.assertEqual(desk['harvest_status'], 'ok')
        self.assertEqual(desk['members_excluded'], [])
        self.assertEqual(desk['members_disclosure_only'], {victim: ['contention.unmeasured']})
        # A completed non-passing desk is also final under R17. The synthetic
        # fixture's other instrument checks need not all pass for this assertion.
        final = runner.cmd_final(SimpleNamespace(session_root=fixture.session, pilot=None, window_id='C1'))
        self.assertEqual(final['member_eligibility']['stage'], 'final')


class CommittedFinalityTests(unittest.TestCase):
    def packet(self, codes):
        with tempfile.TemporaryDirectory(prefix='jw-merge-c84-') as tmp:
            scenario = Scenario(tmp)
            victim = scenario.members[0]['run_id']
            entries = [{'run_id': victim, 'codes': codes}] if codes else []
            excluded, disclosed = pilot.apply_exclusion_policy(entries, v4_contention.split_codes)
            scenario.sources['exclusions']['members_excluded'] = entries
            # These are the fields produced by the native common desk, including
            # its raw-code entries for members that retain a real exclusion.
            for name in ('desk', 'pilot'):
                scenario.sources[name].update(
                    members_excluded=[e for e in entries if e['run_id'] in excluded],
                    members_disclosure_only=disclosed)
            scenario.sources['desk'].update(harvest_status='members_excluded' if excluded else 'ok',
                                           full_desk_gate={'pass': not excluded})
            if excluded:
                scenario.sources['pilot']['status'] = 'instrument_incomplete'
                scenario.sources['desk']['pilot_status'] = 'instrument_incomplete'
                scenario.thermal['members'][0]['excluded'] = True
            scenario.finish()
            packet = scenario.build()
            return packet, evaluate(scenario, packet)

    def test_native_contention_only_record_releases_c1(self):
        clean, clean_arm = self.packet([])
        self.assertTrue(clean['packet_preflight']['ready'], clean['packet_preflight'])
        self.assertTrue(clean_arm['admitted'])
        packet, arm = self.packet(['contention.unmeasured'])
        self.assertTrue(packet['packet_preflight']['ready'], packet['checks']['full_desk_gate'])
        self.assertTrue(arm['admitted'])

    def test_real_and_mixed_exclusions_still_block_c1(self):
        for codes in (['member.runtime_failure'], ['contention.unmeasured', 'member.runtime_failure']):
            with self.subTest(codes=codes):
                packet, arm = self.packet(codes)
                self.assertFalse(packet['packet_preflight']['ready'])
                self.assertEqual(packet['checks']['full_desk_gate']['status'], 'fail')
                self.assertFalse(arm['admitted'])


if __name__ == '__main__':
    unittest.main()
