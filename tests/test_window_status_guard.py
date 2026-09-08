from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts/window_status.sh'
START = 'Tue Sep 8 01:02:03 2026'


class WindowStatusGuardTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.repository = self.root / 'repository unittest'
        self.repository.mkdir()
        self.parent = self.root / 'custody'
        self.night = self.parent / 'unittest spaced plan' / 'night'
        self.night.mkdir(parents=True)
        self.sentinel = self.root / 'freeze'
        self.bin = self.root / 'bin'
        self.bin.mkdir()
        self.git_log = self.root / 'git.log'
        self.ps_log = self.root / 'ps.log'
        self.probe = self.bin / 'identity probe'
        self.probe.write_text('#!/bin/sh\nprintf "%s\\n" "${TEST_IDENTITY_OUTPUT}"\nexit "${TEST_IDENTITY_EXIT}"\n')
        self.probe.chmod(0o755)
        for name, content in {
            'ps': '#!/bin/sh\necho forbidden >> "$PS_LOG"\nexit 99\n',
            'git': '#!/bin/sh\nprintf "%s\\n" "$*" >> "$GIT_LOG"\nif [ "$1" = diff ]; then exit 1; fi\n',
        }.items():
            path = self.bin / name
            path.write_text(content)
            path.chmod(0o755)
        self.env = {
            **os.environ, 'PATH': str(self.bin) + os.pathsep + os.environ['PATH'],
            'JOULEWISE_CUSTODY_PARENT': str(self.parent),
            'JOULEWISE_ADDITIONAL_CUSTODY_PARENTS': '[]',
            'JOULEWISE_IDENTITY_PROBE': str(self.probe),
            'JOULEWISE_STATUS_REPO': str(self.repository),
            'JOULEWISE_COMMIT_FREEZE_SENTINEL': str(self.sentinel),
            'TEST_IDENTITY_OUTPUT': START + ' S', 'TEST_IDENTITY_EXIT': '0',
            'GIT_LOG': str(self.git_log), 'PS_LOG': str(self.ps_log),
        }
        self.status = self.repository / 'WINDOW_STATUS.md'
        self.status.write_text('original status\n')

    def marker(self, value=None):
        (self.night / 'chain.started').write_text(json.dumps(
            {'pid': 41, 'start_time': START} if value is None else value))

    def run_status(self, headline='Synthetic status'):
        result = subprocess.run(['/bin/bash', str(SCRIPT), 'idle', headline],
                                cwd=self.root, env=self.env, capture_output=True, text=True)
        self.assertFalse(self.ps_log.exists(), 'status consulted process argv')
        return result

    def assert_refused(self):
        result = self.run_status()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.status.read_text(), 'original status\n')
        self.assertFalse(self.git_log.exists())
        return result

    def assert_published(self):
        result = self.run_status()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('Synthetic status', self.status.read_text())
        calls = self.git_log.read_text().splitlines()
        self.assertEqual(calls, ['add WINDOW_STATUS.md', 'diff --cached --quiet',
                                 'commit -q -m status: idle — Synthetic status', 'push -q origin HEAD'])
        return result

    def test_open_chain_refuses_before_status_or_git_even_with_sent_and_freeze(self):
        self.marker()
        (self.night / 'courier.sent').touch()
        self.sentinel.touch()
        self.assertIn('live measurement', self.assert_refused().stderr)

    def test_successful_empty_probe_refuses_live_pid(self):
        self.marker({'pid': os.getpid(), 'start_time': START})
        self.env['JOULEWISE_IDENTITY_PROBE'] = '/usr/bin/true'
        self.assertIn('indeterminate', self.assert_refused().stderr)

    def test_complete_marker_without_start_time_refuses_dead_pid(self):
        self.marker({'pid': 41, 'pgid': 41, 'epoch_s': 1})
        self.env.update(TEST_IDENTITY_OUTPUT='', TEST_IDENTITY_EXIT='1')
        self.assertIn('indeterminate', self.assert_refused().stderr)

    def test_closed_chain_permits_publication(self):
        self.marker()
        (self.night / 'chain.exited').write_text(json.dumps(
            {'exit_code': 0, 'epoch_s': 1, 'monotonic_ns': 2}))
        self.assert_published()

    def test_reused_pid_warns_and_permits(self):
        self.marker()
        self.env['TEST_IDENTITY_OUTPUT'] = 'Tue Sep 8 01:02:04 2026 S'
        self.assertIn('WARN: stale reused PID', self.assert_published().stderr)

    def test_dead_pid_warns_and_permits(self):
        self.marker()
        self.env.update(TEST_IDENTITY_OUTPUT='', TEST_IDENTITY_EXIT='1')
        self.assertIn('WARN: stale dead owner', self.assert_published().stderr)

    def test_legacy_and_malformed_open_markers_refuse(self):
        self.marker({'pid': 41})
        self.assertIn('indeterminate', self.assert_refused().stderr)
        (self.night / 'chain.started').write_text('')
        self.assertIn('indeterminate', self.assert_refused().stderr)

    def test_unrelated_campaign_entry_refuses_without_target_lock(self):
        registry = self.parent / 'active-campaigns'
        registry.mkdir()
        (registry / 'owner.json').write_text(json.dumps({
            'schema': 'joulewise.active_campaign.v1', 'pid': 42, 'start_time': START,
            'nonce': 'n', 'runs_root': str(self.root / 'unrelated spaced runs unittest'),
        }))
        (self.night / 'courier.sent').touch()
        self.assertIn('live measurement', self.assert_refused().stderr)

    def test_mentions_do_not_change_output(self):
        for headline in ('vim run_campaign.py', 'prompt window-chain -- unittest',
                         'tests/test_run_campaign.py', '/spaced paths/window-chain.zsh'):
            with self.subTest(headline=headline):
                result = self.run_status(headline)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn(headline, self.status.read_text())

    def test_freeze_writes_locally_without_git(self):
        self.sentinel.touch()
        result = self.run_status()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('Synthetic status', self.status.read_text())
        self.assertFalse(self.git_log.exists())
        self.assertIn('freeze span open', result.stdout)

    def test_root_and_probe_errors_refuse_before_mutation(self):
        self.env['JOULEWISE_CUSTODY_PARENT'] = str(self.status)
        self.assertIn('indeterminate', self.assert_refused().stderr)
        self.env['JOULEWISE_CUSTODY_PARENT'] = str(self.parent)
        self.marker()
        self.env['TEST_IDENTITY_EXIT'] = '2'
        self.assertIn('indeterminate', self.assert_refused().stderr)
        self.env['JOULEWISE_IDENTITY_PROBE'] = str(self.root / 'missing probe')
        self.assertIn('indeterminate', self.assert_refused().stderr)


if __name__ == '__main__':
    unittest.main()
