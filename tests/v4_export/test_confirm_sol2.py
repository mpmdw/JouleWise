"""Confirmation witnesses for terminal custody. Synthetic Git blobs and native fixtures only.

These are required-property tests: a present watchdog source must authenticate
and contain the release latch. A red test is an exporter defect, not an xfail.
"""
from copy import deepcopy
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from scripts import align_v4_next_arm_packet as packet
from scripts import export_v4_series as ex
from tests.align import synthetic_custody
from tests.v4_export import test_review_sol1 as seat1
from tests.v4_release import native_series, support, test_exporter_e2e as fixture

setUpModule = synthetic_custody.setUpModule
tearDownModule = synthetic_custody.tearDownModule


class TerminalSourceChecks(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix='v4-confirm-sol2-terminal-')
        self.addCleanup(tmp.cleanup)
        self.repo = Path(tmp.name)
        native_series.git(self.repo, 'init', '-q')
        self.result = ex.canonical(dict(schema=ex.RESULT_SCHEMA, plan_id='current',
                                        verdict='GO', chain_exit_code=0))
        self.sources = {}
        for name, raw in {
            'plan': ex.canonical(dict(plan_id='current', custody_root='/synthetic/custody')),
            'result': self.result,
            'chain_exited': ex.canonical(dict(exit_code=0)),
            'courier_sent': b'',
        }.items():
            self.put(name, raw)

    def put(self, name, raw):
        path = self.repo / (name + '.json')
        path.write_bytes(raw)
        self.sources[name] = dict(path=path.name, sha256=ex.sha256_bytes(raw))

    def terminal(self):
        native_series.git(self.repo, 'add', '.')
        native_series.git(self.repo, 'commit', '-qm', 'synthetic terminal sources')
        commit = native_series.git(self.repo, 'rev-parse', 'HEAD')
        evidence = packet.GitEvidence(self.repo)
        sources = self.sources

        class Record:
            def __init__(self):
                self.record = {'sources': sources}

            def source(self, name, *, json_value=True):
                return evidence.source(commit, sources.get(name), json_value=json_value)

        return ex.terminal_evidence(Record(), None, None)

    def test_matching_digest_bound_watchdog_latch_passes(self):
        key = 'current:/synthetic/custody:' + ex.sha256_bytes(self.result)
        self.put('watchdog_state', ex.canonical(dict(released_terminal_windows=[key])))
        self.assertEqual(self.terminal(), self.result)

    def test_stale_digest_bound_watchdog_latch_refuses(self):
        self.put('watchdog_state', ex.canonical(dict(released_terminal_windows=['previous-window'])))
        with self.assertRaises(ex.Refused):
            self.terminal()

    def test_stale_watchdog_with_wrong_digest_must_still_refuse(self):
        self.put('watchdog_state', ex.canonical(dict(released_terminal_windows=['previous-window'])))
        self.sources['watchdog_state']['sha256'] = '0' * 64
        with self.assertRaises(ex.Refused, msg='a failed watchdog digest was silently ignored'):
            self.terminal()

    def test_unparseable_present_watchdog_source_must_refuse(self):
        self.put('watchdog_state', b'partial snapshot\n')
        with self.assertRaises(ex.Refused, msg='a present but unreadable watchdog source was ignored'):
            self.terminal()

    def test_present_watchdog_snapshot_without_release_field_must_refuse(self):
        self.put('watchdog_state', ex.canonical(dict(released_terminal_window=[])))
        with self.assertRaises(ex.Refused, msg='a present watchdog snapshot lacked the release latch'):
            self.terminal()


@unittest.skipUnless(support.have_commits(), 'pinned synthetic producer commits unavailable')
class NativeTerminalCheck(unittest.TestCase):
    def test_stale_watchdog_digest_cannot_bypass_a_native_window_refusal(self):
        """Keep real producer custody unchanged; mutate only our committed watchdog source/descriptor."""
        with tempfile.TemporaryDirectory(prefix='v4-confirm-sol2-native-') as tmp:
            work = Path(tmp)
            config, value = fixture.config_copy(work)
            repo = work / 'records'
            shutil.copytree(value['records_repo'], repo)
            value['records_repo'] = str(repo)
            c1 = next(w for w in value['windows'] if w['attempt_id'] == 'C1#1')
            original = json.loads(native_series.git(repo, 'show', c1['record_commit'] + ':' + c1['record_path']))

            def export(attempt):
                config.write_bytes(ex.canonical(value))
                with patch.object(ex, 'battery_evidence', seat1.serial_battery):
                    return ex.run(config, [attempt])

            def record_with_watchdog(correct_digest):
                record = deepcopy(original)
                raw = ex.canonical(dict(released_terminal_windows=['previous-window']))
                folder = repo / 'confirmation'
                folder.mkdir(exist_ok=True)
                (folder / 'watchdog.json').write_bytes(raw)
                record['sources']['watchdog_state'] = dict(
                    path='confirmation/watchdog.json',
                    sha256=ex.sha256_bytes(raw) if correct_digest else '0' * 64)
                (folder / 'record.json').write_bytes(ex.canonical(record))
                native_series.git(repo, 'add', 'confirmation')
                native_series.git(repo, 'commit', '-qm', 'synthetic watchdog digest control')
                c1.update(record_commit=native_series.git(repo, 'rev-parse', 'HEAD'),
                          record_path='confirmation/record.json')

            export('W1#1')
            record_with_watchdog(True)
            with self.assertRaises(ex.Refused) as caught:
                export('C1#1')
            self.assertEqual(caught.exception.code, 'terminal_evidence_mismatch')

            record_with_watchdog(False)
            try:
                export('C1#1')
            except ex.Refused:
                return
            root = Path(value['export_root'])
            engine = json.loads((root / 'engine/windows/C1/raw.json').read_bytes())
            recompute = json.loads((root / 'recompute/windows/C1/window.json').read_bytes())
            self.assertEqual(sum(m['captured'] for m in engine['members']), 22)
            self.assertEqual(sum(m['captured'] for m in recompute['members']), 22)
            self.fail('the valid stale latch refused, but its wrong digest exported all 22 captures to both builds')


if __name__ == '__main__':
    unittest.main()
