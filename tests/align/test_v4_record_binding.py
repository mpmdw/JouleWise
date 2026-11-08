"""Smoke G1: the next-arm triage packet is bound to the last committed window record.

Real temporary Git repositories, synthetic record bytes only.
"""
import hashlib
from pathlib import Path
import subprocess
import tempfile
import unittest

from scripts import align_v4_session as session
from tests.align.test_v4_cadence import INTERNAL, IDENTITY, passing_packet
from joulewise.align.apple import v4_cadence as cad

RECORD = 'staging/window-C2-record.json'


class RecordBindingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.git('init', '-q')

    def git(self, *args):
        return subprocess.run(['git', '-c', 'core.hooksPath=/dev/null', *args], cwd=self.root, check=True,
                              capture_output=True, text=True).stdout.strip()

    def commit(self, relative, text):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        self.git('add', '.')
        self.git('-c', 'user.name=S', '-c', 'user.email=s@example.invalid', 'commit', '-qm', f'record {text[:8]}')
        return self.git('rev-parse', 'HEAD'), hashlib.sha256(text.encode()).hexdigest()

    def packet(self, commit, digest, **kw):
        return passing_packet(record_commit=commit, record_path=RECORD, record_sha256=digest, **kw)

    def arm_identity(self, packet):
        return {**IDENTITY, 'record_commit_exists': session._commit_exists(self.root, packet['record_commit']),
                'record_bound': session._record_bound(self.root, packet)}

    def test_a_packet_for_the_last_committed_record_is_admitted(self):
        commit, digest = self.commit(RECORD, '{"window": "C2", "v": 1}\n')
        packet = self.packet(commit, digest)
        result = cad.next_arm_triage(packet, INTERNAL, self.arm_identity(packet))
        self.assertTrue(result['admitted'], result['reasons'])
        self.assertTrue(result['derived']['record_bound'])

    def test_a_stale_but_well_formed_packet_refuses(self):
        old_commit, old_digest = self.commit(RECORD, '{"window": "C2", "v": 1}\n')
        self.commit(RECORD, '{"window": "C2", "v": 2, "amended": true}\n')      # the record was re-committed
        stale = self.packet(old_commit, old_digest)
        self.assertTrue(session._commit_exists(self.root, old_commit))          # well formed and findable
        self.assertFalse(session._record_bound(self.root, stale))
        result = cad.next_arm_triage(stale, INTERNAL, self.arm_identity(stale))
        self.assertFalse(result['admitted'])
        self.assertIn('triage record_committed failed', result['reasons'])

    def test_wrong_digest_wrong_path_missing_record_and_unsafe_paths_refuse(self):
        commit, digest = self.commit(RECORD, '{"window": "C2"}\n')
        for change in ({'record_sha256': 'f' * 64}, {'record_path': 'staging/other.json'},
                       {'record_path': '../escape'}, {'record_path': '/etc/hosts'},
                       {'record_commit': 'a' * 40}, {'record_sha256': None}, {'record_path': ''}):
            packet = self.packet(commit, digest)
            packet.update(change)
            with self.subTest(change=change):
                self.assertFalse(session._record_bound(self.root, packet))
                self.assertFalse(cad.next_arm_triage(packet, INTERNAL, self.arm_identity(packet))['admitted'])

    def test_a_later_unrelated_commit_does_not_make_the_packet_stale(self):
        commit, digest = self.commit(RECORD, '{"window": "C2"}\n')
        self.commit('docs/note.md', 'unrelated\n')
        packet = self.packet(commit, digest)
        self.assertTrue(session._record_bound(self.root, packet))

    def test_the_arm_wires_the_binding_into_the_arm_record(self):
        from unittest.mock import patch
        from tests.align.test_v4_cadence import write_battery_log
        commit, digest = self.commit(RECORD, '{"window": "C2"}\n')
        self.commit(RECORD, '{"window": "C2", "v": 2}\n')
        good = dict(passed=True, probe_error=False, external_connected=True, is_charging=False,
                    current_capacity_pct=100, instant_amperage_ma=0, update_age_s=1)
        with patch('joulewise.align.apple.powermode.admit_ac_powermode', return_value={'admitted': True}), \
             patch('joulewise.align.apple.external_volume.census', return_value={}), \
             patch('joulewise.align.apple.external_volume.arm_check', return_value={'verdict': 'PASS', 'reasons': []}), \
             patch('joulewise.battery_float.observe', return_value=(good, b'raw')):
            run = lambda argv: subprocess.CompletedProcess(argv, 0, 'pmset', '')
            log = write_battery_log(self.root / 'battery.jsonl', 5000.)
            record = session.arm_checks(self.root, {}, runner=run, now=lambda: 5000., obc_off_attested_by='synthetic',
                                        battery_log=log, next_arm_triage=self.packet(commit, digest))
        self.assertFalse(record['admitted'])
        self.assertIn('next_arm_triage: triage record_committed failed', record['reasons'])
        self.assertFalse(record['next_arm_triage']['derived']['record_bound'])
        self.assertTrue(record['next_arm_triage']['derived']['record_commit_exists'])


if __name__ == '__main__':
    unittest.main()
