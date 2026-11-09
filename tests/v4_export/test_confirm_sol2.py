"""Confirmation witnesses for terminal custody. Synthetic Git blobs and native fixtures only.

These are required-property tests: a present watchdog source must authenticate
and contain the release latch. A red test is an exporter defect, not an xfail.
Lead ruling CF1: the exporter verifies the latch with the production next-arm
verifier (``align_v4_next_arm_packet.watchdog_latch_check``); invalid present
evidence refuses ``terminal_evidence_mismatch`` and absence refuses
``terminal_evidence_missing``. The native witness now asserts the refusal.
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
        # Producer shape (native_series / the night driver): a HAZARD_PACK collected window, delivered.
        self.result = ex.canonical(dict(schema=ex.RESULT_SCHEMA, plan_id='current', receipt_class='HAZARD_PACK',
                                        verdict='GO', chain_exit_code=0, ended_epoch_s=100))
        self.finalized = 101
        self.sources = {}
        for name, raw in {
            'plan': ex.canonical(dict(plan_id='current', receipt_class='HAZARD_PACK',
                                      custody_root='/synthetic/custody')),
            'result': self.result,
            'chain_started': ex.canonical(dict(pgid=123)),
            'chain_exited': ex.canonical(dict(exit_code=0)),
            'courier': ex.canonical(dict(sent=True)),
            'courier_sent': b'',
        }.items():
            self.put(name, raw)

    def put(self, name, raw):
        path = self.repo / (name + '.json')
        path.write_bytes(raw)
        self.sources[name] = dict(path=path.name, sha256=ex.sha256_bytes(raw))

    def terminal(self):
        return ex.terminal_evidence(self.record_view(), None, None)

    def record_view(self):
        native_series.git(self.repo, 'add', '.')
        native_series.git(self.repo, 'commit', '-qm', 'synthetic terminal sources', '--allow-empty')
        commit = native_series.git(self.repo, 'rev-parse', 'HEAD')
        evidence = packet.GitEvidence(self.repo)
        sources, finalized = self.sources, self.finalized

        class Record:
            def __init__(self):
                self.record = {'sources': sources, 'finalized_at_epoch_s': finalized}

            def source(self, name, *, json_value=True):
                return evidence.source(commit, sources.get(name), json_value=json_value)

        return Record()

    def test_matching_digest_bound_watchdog_latch_passes(self):
        key = 'current:/synthetic/custody:' + ex.sha256_bytes(self.result)
        self.put('watchdog_state', ex.canonical(dict(released_terminal_windows=[key])))
        self.assertEqual(self.terminal(), self.result)

    def test_stale_digest_bound_watchdog_latch_refuses(self):
        self.put('watchdog_state', ex.canonical(dict(released_terminal_windows=['previous-window'])))
        with self.assertRaises(ex.Refused):
            self.terminal()

    def assertRefuses(self, code, msg=None):
        with self.assertRaises(ex.Refused, msg=msg) as caught:
            self.terminal()
        self.assertEqual(caught.exception.code, code)

    def test_absent_watchdog_source_refuses_missing(self):
        """Lead ruling CF1: the latch is required for a captured C attempt; absence refuses."""
        self.assertRefuses('terminal_evidence_missing')

    def test_null_watchdog_descriptor_refuses_missing(self):
        self.sources['watchdog_state'] = None
        self.assertRefuses('terminal_evidence_missing')

    def test_malformed_watchdog_descriptor_refuses(self):
        self.put('watchdog_state', ex.canonical(dict(released_terminal_windows=['x'])))
        self.sources['watchdog_state'] = dict(path=self.sources['watchdog_state']['path'])
        self.assertRefuses('terminal_evidence_mismatch')

    def test_non_object_watchdog_snapshot_refuses(self):
        key = 'current:/synthetic/custody:' + ex.sha256_bytes(self.result)
        self.put('watchdog_state', ex.canonical([key]))
        self.assertRefuses('terminal_evidence_mismatch')

    def test_latch_for_another_result_digest_refuses(self):
        key = 'current:/synthetic/custody:' + '1' * 64
        self.put('watchdog_state', ex.canonical(dict(released_terminal_windows=[key])))
        self.assertRefuses('terminal_evidence_mismatch')

    def test_exporter_uses_the_production_verifier(self):
        key = 'current:/synthetic/custody:' + ex.sha256_bytes(self.result)
        self.put('watchdog_state', ex.canonical(dict(released_terminal_windows=[key])))
        with patch.object(packet, 'watchdog_latch_check', side_effect=ValueError('production says no')) as v:
            self.assertRefuses('terminal_evidence_mismatch')
        v.assert_called_once()

    # ---- Terminal release (lead ruling, exporter admission): the production next-arm decision.
    def latch(self):
        key = 'current:/synthetic/custody:' + ex.sha256_bytes(self.result)
        self.put('watchdog_state', ex.canonical(dict(released_terminal_windows=[key])))

    def mutate_json(self, name, **change):
        value = json.loads((self.repo / self.sources[name]['path']).read_bytes())
        value.update(change)
        raw = ex.canonical(value)
        if name == 'result':
            self.result = raw
        self.put(name, raw)

    def refuses_release(self, reason):
        self.latch()
        with self.assertRaises(ex.Refused) as caught:
            self.terminal()
        self.assertEqual((caught.exception.code, caught.exception.detail), ('terminal_not_released', reason))

    def test_release_refuses_with_production_reason_not_hazard_pack(self):
        self.mutate_json('plan', receipt_class='OTHER_PACK')
        self.refuses_release('not_hazard_pack')

    def test_release_refuses_with_production_reason_result_class(self):
        self.mutate_json('result', receipt_class='OTHER_PACK')
        self.refuses_release('result_class_mismatch')

    def test_release_refuses_with_production_reason_not_terminal(self):
        self.finalized = 99      # the result ended after the record's committed finalization
        self.refuses_release('result_not_terminal')

    def test_release_refuses_with_production_reason_unknown_verdict(self):
        self.mutate_json('result', verdict='MAYBE')
        self.refuses_release('unknown_verdict')

    def test_release_refuses_undelivered_courier(self):
        self.mutate_json('courier', sent=False)
        self.refuses_release('courier delivery missing')

    def test_release_refuses_chain_closure_disagreement(self):
        self.put('chain_exited', ex.canonical(dict(exit_code=3)))
        self.refuses_release('chain closure and terminal result disagree')

    def test_release_refuses_missing_finalization(self):
        self.finalized = None
        self.refuses_release('record finalization missing')

    def test_release_refuses_missing_courier_source(self):
        self.sources.pop('courier')
        self.latch()
        with self.assertRaises(ex.Refused) as caught:
            self.terminal()
        self.assertEqual(caught.exception.code, 'terminal_not_released')

    def test_exporter_uses_the_production_release_decision(self):
        self.latch()
        with patch.object(packet, 'terminal_release_check', side_effect=ValueError('production says no')) as v:
            self.refuses_release('production says no')
        v.assert_called_once()

    def test_exporter_releases_exactly_what_the_production_check_releases(self):
        """Over a grid of terminal shapes, the exporter accepts iff packet.terminal_release_check (with the
        record's finalization as the clock) releases, and then refuses with the production reason."""
        grid = [dict(), dict(verdict='REFUSED'), dict(verdict='ABORTED'), dict(verdict='CHAIN_STOPPED'),
                dict(verdict='MAYBE'), dict(receipt_class='X'), dict(ended_epoch_s=101), dict(ended_epoch_s=102),
                dict(ended_epoch_s='late'), dict(plan_id='other')]
        base = dict(self.sources)
        for change in grid:
            with self.subTest(change=change):
                self.sources = dict(base)
                self.mutate_json('result', **change)
                self.latch()
                record = self.record_view()
                plan = record.source('plan')
                try:
                    packet.terminal_release_check(record, plan, self.finalized)
                    production = None
                except (ValueError, KeyError, TypeError, AttributeError) as exc:
                    production = str(exc)
                try:
                    self.terminal()
                    exporter = None
                except ex.Refused as exc:
                    exporter = exc
                if production is None:
                    self.assertIsNone(exporter, change)
                else:
                    self.assertIsNotNone(exporter, change)
                    if exporter.code == 'terminal_not_released':
                        self.assertEqual(exporter.detail, production)
                    else:  # refused earlier by the exporter's own result shape / plan ownership checks
                        self.assertIn(exporter.code, ('terminal_evidence_mismatch',))

    def test_stale_watchdog_with_wrong_digest_must_still_refuse(self):
        self.put('watchdog_state', ex.canonical(dict(released_terminal_windows=['previous-window'])))
        self.sources['watchdog_state']['sha256'] = '0' * 64
        self.assertRefuses('terminal_evidence_mismatch', msg='a failed watchdog digest was silently ignored')

    def test_unparseable_present_watchdog_source_must_refuse(self):
        self.put('watchdog_state', b'partial snapshot\n')
        self.assertRefuses('terminal_evidence_mismatch', msg='a present but unreadable watchdog source was ignored')

    def test_present_watchdog_snapshot_without_release_field_must_refuse(self):
        self.put('watchdog_state', ex.canonical(dict(released_terminal_window=[])))
        self.assertRefuses('terminal_evidence_mismatch', msg='a present watchdog snapshot lacked the release latch')


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

            # CF1 (lead ruling): the wrong digest is verified by the production latch verifier and refuses too;
            # nothing of C1 lands in either layout.
            record_with_watchdog(False)
            with self.assertRaises(ex.Refused, msg='a failed watchdog digest was silently ignored') as caught:
                export('C1#1')
            self.assertEqual(caught.exception.code, 'terminal_evidence_mismatch')
            root = Path(value['export_root'])
            self.assertFalse((root / 'engine/windows/C1').exists())
            self.assertFalse((root / 'recompute/windows/C1').exists())


if __name__ == '__main__':
    unittest.main()
