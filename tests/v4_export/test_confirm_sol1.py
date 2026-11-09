"""Confirmation-seat probes. Synthetic only. Required-property tests: lead ruling CF1/H1 makes every
watchdog authentication failure refuse (production next-arm verifier); absence refuses where required.

Run alone under Python 3.13 with the synthetic-custody environment used by the exporter reviews.
Exporter validation and build implementations are unchanged. Battery joining uses serial production code.
"""
from copy import deepcopy
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from scripts import export_v4_series as ex
from tests.align import synthetic_custody
from tests.v4_release import native_series, support
from tests.v4_export import test_review_sol1 as review

setUpModule = synthetic_custody.setUpModule
tearDownModule = synthetic_custody.tearDownModule


class ReferenceCoverage(unittest.TestCase):
    def test_every_required_output_reference_refuses_a_missing_digest(self):
        with tempfile.TemporaryDirectory(prefix='v4-confirm-refs-') as tmp:
            # Restate the runbook's required fields, independently of ENGINE_ROW_REFS, so deleting a
            # reference from that implementation constant still makes this test fail.
            required = ('episode', 'powermetrics', 'config', 'planned_config', 'journal', 'metadata',
                        'events', 'turns_source')
            writer = ex.Writer(tmp)
            ref = writer.bytes('recompute/ref.json', b'{}\n')
            rec_ref = dict(ref, path='ref.json')
            window = {key: dict(ref) for key in ('raw_source', 'plan_source', 'terminal_result_source')}
            member = dict(captured=True, **{key: dict(ref) for key in required},
                          dc_streams=[dict(ref)])
            doc = dict(plan_source=dict(rec_ref), terminal_result_source=dict(rec_ref),
                       members=[dict(captured=True, planned_config=dict(rec_ref))])
            ex.verify_references(writer, window, [member], doc, captured_c=True)
            targets = [('window', key) for key in window]
            targets += [('member', key) for key in required]
            targets += [('stream', None), ('recompute', 'plan_source'),
                        ('recompute', 'terminal_result_source'), ('recompute_member', 'planned_config')]
            for scope, key in targets:
                with self.subTest(scope=scope, key=key):
                    ew, m, wd = deepcopy((window, member, doc))
                    if scope == 'window':
                        target = ew[key]
                    elif scope == 'member':
                        target = m[key]
                    elif scope == 'stream':
                        target = m['dc_streams'][0]
                    elif scope == 'recompute':
                        target = wd[key]
                    else:
                        target = wd['members'][0][key]
                    target.pop('sha256')
                    with self.assertRaises(ex.Refused) as caught:
                        ex.verify_references(writer, ew, [m], wd, captured_c=True)
                    self.assertEqual(caught.exception.code, 'reference_digest_missing')


@unittest.skipUnless(support.have_commits(), 'pinned synthetic producer support unavailable')
class TerminalCustody(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix='v4-confirm-native-')
        cls.work = Path(cls.tmp.name)
        cls.addClassCleanup(cls.tmp.cleanup)
        synth = support.synth_module()
        config, _ = native_series.cached(synth, synth.FrameTemplate(n_tasks=0, seed=7, clusters=0))
        cls.value = json.loads(config.read_bytes())
        cls.repo = cls.work / 'records'
        shutil.copytree(cls.value['records_repo'], cls.repo)
        cls.value['records_repo'] = str(cls.repo)
        cls.seed = cls.work / 'prefix'
        cls.value['export_root'] = str(cls.seed)
        path = cls.work / 'base.json'
        path.write_bytes(ex.canonical(cls.value))
        with patch.object(ex, 'battery_evidence', review.serial_battery):
            ex.run(path, ['W1#1'])

    def setUp(self):
        self.case_tmp = tempfile.TemporaryDirectory(prefix='case-', dir=self.work)
        self.addCleanup(self.case_tmp.cleanup)
        self.case = Path(self.case_tmp.name)
        self.value = deepcopy(type(self).value)
        self.root = self.case / 'export'
        shutil.copytree(self.seed, self.root, copy_function=os.link)
        self.value['export_root'] = str(self.root)
        self.enterContext(patch.object(ex, 'battery_evidence', review.serial_battery))

    def record(self, *, corrupt_digest=False, stale_latch=False, drop_latch=False):
        entry = next(w for w in self.value['windows'] if w['attempt_id'] == 'C1#1')
        git = lambda *args: native_series.git(self.repo, *args)
        record = json.loads(git('show', entry['record_commit'] + ':' + entry['record_path']))
        if stale_latch:
            raw = ex.canonical({'released_terminal_windows': ['previous-window:old-custody:' + '0' * 64]})
            rel = f'confirm/{self.case.name}/watchdog.json'
            path = self.repo / rel
            path.parent.mkdir(parents=True)
            path.write_bytes(raw)
            record['sources']['watchdog_state'] = dict(path=rel, sha256=ex.sha256_bytes(raw))
        if corrupt_digest:
            record['sources']['watchdog_state']['sha256'] = '0' * 64
        if drop_latch:
            record['sources'].pop('watchdog_state')
        rel = f'confirm/{self.case.name}/record.json'
        path = self.repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(ex.canonical(record))
        git('add', 'confirm')
        git('commit', '-qm', 'synthetic confirmation terminal mutation')
        entry.update(record_commit=git('rev-parse', 'HEAD'), record_path=rel)
        return entry

    def export(self):
        path = self.case / 'config.json'
        path.write_bytes(ex.canonical(self.value))
        return ex.run(path, ['C1#1'])

    def test_extending_a_prefix_reverifies_prior_metadata_events_and_turns(self):
        state = json.loads((self.root / 'state/W1.json').read_bytes())
        for suffix in ('/metadata.json', '/events.jsonl', '/outputs/align_turns.jsonl'):
            rel = next(p for p in state['files'] if p.endswith(suffix))
            with self.subTest(reference=rel):
                path = self.root / rel
                raw = path.read_bytes()
                try:
                    review.replace_bytes(path, raw + b' ')
                    with self.assertRaises(ex.Refused) as caught:
                        self.export()
                    self.assertEqual(caught.exception.code, 'landed_window_changed')
                    self.assertFalse((self.root / 'state/C1.json').exists())
                finally:
                    review.replace_bytes(path, raw)

    def test_digest_valid_stale_watchdog_latch_refuses(self):
        self.record(stale_latch=True)
        with self.assertRaises(ex.Refused) as caught:
            self.export()
        self.assertEqual(caught.exception.code, 'terminal_evidence_mismatch')

    def test_present_watchdog_with_wrong_digest_cannot_disable_its_stale_latch(self):
        """A stale/wrong SHA descriptor must not turn supplied terminal evidence into optional absence."""
        entry = self.record(corrupt_digest=True, stale_latch=True)
        record, _ = ex.open_record(self.value, entry)
        with self.assertRaisesRegex(ValueError, 'source SHA-256 mismatch'):
            record.source('watchdog_state')
        with self.assertRaises(ex.Refused, msg='unverified terminal latch accepted') as caught:
            self.export()
        self.assertEqual(caught.exception.code, 'terminal_evidence_mismatch')
        self.assertFalse((self.root / 'state/C1.json').exists())
        self.assertFalse((self.root / 'recompute/windows/C1').exists())

    def test_absent_watchdog_latch_refuses_for_a_captured_c_window(self):
        """Lead ruling: absent evidence refuses where it is required (every captured C attempt)."""
        self.record(drop_latch=True)
        with self.assertRaises(ex.Refused) as caught:
            self.export()
        self.assertEqual(caught.exception.code, 'terminal_evidence_missing')
        self.assertFalse((self.root / 'state/C1.json').exists())
