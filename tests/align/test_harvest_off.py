"""HARVEST-OFF-opus: verified offload, same-path harvest equality, parse dedupe, light triage.

All synthetic. The harvest windows are tests.test_harvest_b5_window's real-shaped
strict bundles; no real record, night-* or restricted path is read.
"""
from __future__ import annotations

import contextlib
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import plistlib
import random
import shutil
import tempfile
import unittest
from unittest import mock

from joulewise.adapters import powermetrics as pm
from joulewise.b5 import harvest as h
from tests import test_harvest_b5_window as w

REAL_TMP = os.path.realpath(tempfile.gettempdir())
SEED_PLIST = Path(__file__).resolve().parents[1] / 'fixtures/d117_v2_production/strict_seed_bundle/raw/powermetrics.plist'


def tearDownModule():  # noqa: N802 (unittest hook): the shared member template
    w.tearDownModule()


def inventory(root: Path) -> dict[str, str]:
    rows = {}
    for path in sorted(root.rglob('*')):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            rows[relative] = 'link:' + os.readlink(path)
        elif path.is_file():
            rows[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    return rows


class DocumentMemoTests(unittest.TestCase):
    def setUp(self):
        raw = SEED_PLIST.read_bytes()
        self.data = b'\0'.join([raw.rstrip(b'\0')] * 2)
        self.loads = mock.patch.object(pm.plistlib, 'loads', wraps=plistlib.loads)
        self.counter = self.loads.start()
        self.addCleanup(self.loads.stop)

    def test_memo_parses_identical_bytes_once_and_isolates_callers(self):
        documents, _ = pm._powermetrics_documents(self.data)
        per_parse = self.counter.call_count
        self.counter.reset_mock()
        with pm.document_memo():
            first, diag1 = pm._powermetrics_documents(self.data)
            first[0]['__mutated_by_first_caller__'] = True
            second, diag2 = pm._powermetrics_documents(self.data)
        self.assertEqual(self.counter.call_count, per_parse)        # one parse, not two
        self.assertNotIn('__mutated_by_first_caller__', second[0])  # callers never share objects
        self.assertEqual(second, documents)
        self.assertEqual((diag1, diag2), (None, None))
        self.assertIsNone(pm._DOCUMENT_MEMO.get())                  # the scope ends

    def test_memo_is_off_by_default(self):
        pm._powermetrics_documents(self.data)
        once = self.counter.call_count
        pm._powermetrics_documents(self.data)
        self.assertEqual(self.counter.call_count, 2 * once)

    def test_memo_never_keeps_a_refusal(self):
        parts = self.data.split(b'\0')
        broken = b'\0'.join([parts[0], parts[1][:len(parts[1]) // 2], *parts[2:]])
        with pm.document_memo():
            messages = []
            for _ in range(2):
                with self.assertRaises(ValueError) as caught:
                    pm._powermetrics_documents(broken)
                messages.append(str(caught.exception))
            self.assertEqual(pm._DOCUMENT_MEMO.get(), {})
        self.assertEqual(messages[0], messages[1])

    def test_dropped_final_frame_diagnostic_is_reproduced_exactly(self):
        truncated = self.data[:-500]
        plain = pm._powermetrics_documents(truncated)
        self.assertIsNotNone(plain[1])
        with pm.document_memo():
            pm._powermetrics_documents(truncated)
            self.assertEqual(pm._powermetrics_documents(truncated), plain)


class MemberDedupeEqualityTests(unittest.TestCase):
    """The deduped member assessment equals the legacy one, field for field and byte for byte."""

    def assess(self, bundle, memo):
        withheld = Path(tempfile.mkdtemp(dir=REAL_TMP))
        self.addCleanup(shutil.rmtree, withheld, True)
        patch = contextlib.nullcontext() if memo else mock.patch.object(pm, 'document_memo', contextlib.nullcontext)
        with patch:
            result = h.assess_member({'run_id': w.MEMBERS[0][0], 'bundle_path': str(bundle),
                                      'withheld_dir': str(withheld)})
        rereduced = result.get('rereduced')
        raw = Path(rereduced.pop('path')).read_bytes() if isinstance(rereduced, dict) else None
        return result, raw

    def test_assessment_identical_with_and_without_dedupe(self):
        bundle = w.template() / w.MEMBERS[0][0]
        legacy, legacy_raw = self.assess(bundle, memo=False)
        deduped, deduped_raw = self.assess(bundle, memo=True)
        self.assertTrue(legacy['strict_valid'])
        self.assertEqual(deduped, legacy)
        self.assertEqual(deduped_raw, legacy_raw)

    def test_damaged_member_refuses_identically(self):
        root = Path(tempfile.mkdtemp(dir=REAL_TMP))
        self.addCleanup(shutil.rmtree, root, True)
        bundle = root / w.MEMBERS[0][0]
        w.copy_member(w.template() / w.MEMBERS[0][0], bundle)
        plist = bundle / 'raw/powermetrics.plist'
        raw = plist.read_bytes()
        plist.unlink()                                  # break the clone, then damage one frame
        plist.write_bytes(raw[:len(raw) // 2] + b'<junk>' + raw[len(raw) // 2:])
        legacy, legacy_raw = self.assess(bundle, memo=False)
        deduped, deduped_raw = self.assess(bundle, memo=True)
        self.assertFalse(legacy['strict_valid'])
        self.assertEqual(deduped, legacy)
        self.assertEqual(deduped_raw, legacy_raw)


class OffloadTests(unittest.TestCase):
    def setUp(self):
        from joulewise.align.apple import harvest_offload as off
        self.off = off
        self.root = Path(tempfile.mkdtemp(prefix='offload-', dir=REAL_TMP))
        self.addCleanup(shutil.rmtree, self.root, True)
        self.src = self.root / 'session'
        (self.src / 'runs/m1/raw').mkdir(parents=True)
        (self.src / 'runs/m1/raw/powermetrics.plist').write_bytes(SEED_PLIST.read_bytes())
        (self.src / 'runs/m1/run.sh').write_text('#!/bin/sh\n')
        os.chmod(self.src / 'runs/m1/run.sh', 0o755)
        (self.src / 'empty').mkdir()
        os.symlink('/nonexistent/measurement/checkout/joulewise', self.src / 'joulewise')
        os.symlink('runs/m1', self.src / 'relative-link')
        self.ledger = self.root / 'checkout/runs/ledger.jsonl'
        self.ledger.parent.mkdir(parents=True)
        self.ledger.write_bytes(b'{"row": 1}\n{"row": 2}\n')

    def pack(self, name='out'):
        return self.off.pack(self.src, self.root / name, external=(self.ledger,))

    def test_round_trip_restores_every_byte_link_mode_and_ledger_at_the_same_path(self):
        manifest = self.pack()
        before = inventory(self.src)
        shutil.move(self.src, self.root / 'moved')
        self.ledger.write_bytes(b'{"row": 1}\n')       # the Air mirror holds an older prefix
        self.off.unpack(self.root / 'out', self.src)
        self.assertEqual(inventory(self.src), before)
        self.assertEqual(self.off.verify_tree(self.src, manifest), [])
        self.assertEqual(os.stat(self.src / 'runs/m1/run.sh').st_mode & 0o777, 0o755)
        self.assertEqual(os.readlink(self.src / 'joulewise'), '/nonexistent/measurement/checkout/joulewise')
        self.assertEqual(self.ledger.read_bytes(), b'{"row": 1}\n{"row": 2}\n')
        self.assertFalse((self.src / '.external-staged').exists())
        self.assertLess(manifest['payload']['size'], manifest['bytes'])

    def test_refuses_relocation_existing_destination_and_tampering(self):
        self.pack()
        with self.assertRaisesRegex(self.off.OffloadRefused, 'differs from the recorded source root'):
            self.off.unpack(self.root / 'out', self.root / 'elsewhere')
        with self.assertRaisesRegex(self.off.OffloadRefused, 'already exists'):
            self.off.unpack(self.root / 'out')
        shutil.move(self.src, self.root / 'moved')
        payload = self.root / 'out' / self.off.PAYLOAD
        raw = bytearray(payload.read_bytes())
        raw[len(raw) // 2] ^= 0xFF
        payload.write_bytes(bytes(raw))
        with self.assertRaisesRegex(self.off.OffloadRefused, 'payload digest mismatch'):
            self.off.unpack(self.root / 'out')
        self.assertFalse(self.src.exists())

    def test_refuses_a_manifest_mismatch_and_leaves_nothing_behind(self):
        manifest = self.pack()
        manifest['entries']['runs/m1/run.sh']['size'] += 1
        (self.root / 'out' / self.off.MANIFEST).write_text(json.dumps(manifest))
        shutil.move(self.src, self.root / 'moved')
        with self.assertRaisesRegex(self.off.OffloadRefused, 'differs from manifest'):
            self.off.unpack(self.root / 'out')
        self.assertFalse(self.src.exists())
        self.assertFalse(self.src.with_name('session.restoring').exists())

    def test_refuses_a_ledger_that_is_not_an_append_only_extension(self):
        self.pack()
        shutil.move(self.src, self.root / 'moved')
        self.ledger.write_bytes(b'{"row": 9}\n')
        with self.assertRaisesRegex(self.off.OffloadRefused, 'append-only'):
            self.off.unpack(self.root / 'out')
        self.assertFalse(self.src.exists())

    def test_refuses_unsupported_file_types(self):
        os.mkfifo(self.src / 'fifo')
        with self.assertRaisesRegex(self.off.OffloadRefused, 'unsupported file type'):
            self.pack('out2')


class SamePathHarvestEqualityTests(unittest.TestCase):
    """MBP harvest on the live record == Air harvest on the verified copy at the same path."""

    def setUp(self):
        from joulewise.align.apple import harvest_offload as off
        self.off = off
        self.tmp = Path(tempfile.mkdtemp(prefix='harvest-off-', dir=REAL_TMP))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.window = w.Window(self.tmp / 'w', catalog_overrides={'member.cooldown_evidence_unverified': 'DISCLOSE'})
        self.manifest = self.off.pack(self.tmp / 'w', self.tmp / 'offload')

    def seams(self, workers, boot, pinned):
        clocks = {'now': lambda: 1786300000.0, 'monotonic_ns': lambda: 123} if pinned else {}
        return h.Seams(group_alive=lambda pgid: False, exclusions_compute=w.EXCLUSIONS,
                       boot_session_uuid=lambda: boot, workers=workers, **clocks)

    def mbp_then_air(self, *, pinned, boots):
        # MBP: today's path (one worker, no parse dedupe) on the live record.
        with mock.patch.object(pm, 'document_memo', contextlib.nullcontext):
            mbp = h.harvest(h.resolve_inputs(self.window.plan_path), self.window.archive,
                            seams=self.seams(1, boots[0], pinned), prepare_desk=True)
        os.rename(self.tmp / 'w', self.tmp / 'w.mbp')
        # Air: restore the verified copy at the SAME path; three workers, dedupe on.
        self.off.unpack(self.tmp / 'offload', self.tmp / 'w')
        air = h.harvest(h.resolve_inputs(self.window.plan_path), self.window.archive,
                        seams=self.seams(3, boots[1], pinned), prepare_desk=True)
        return mbp, air, self.tmp / 'w.mbp/archive', self.tmp / 'w/archive'

    def test_air_harvest_from_verified_copy_is_byte_identical(self):
        mbp, air, a, b = self.mbp_then_air(pinned=True, boots=('BOOT', 'BOOT'))
        self.assertEqual(mbp['verdict'], 'COLLECTED')
        self.assertEqual(mbp['members_assessed'], len(w.MEMBERS))
        self.assertEqual(air, mbp)
        left, right = inventory(a), inventory(b)
        self.assertGreater(len(left), 100)
        self.assertEqual(right, left)

    def test_unpinned_runs_differ_only_in_declared_provenance(self):
        _mbp, _air, a, b = self.mbp_then_air(pinned=False, boots=('MBP-BOOT', 'AIR-BOOT'))
        left, right = inventory(a), inventory(b)
        differing = {k for k in set(left) | set(right) if left.get(k) != right.get(k)}
        self.assertEqual(differing, {'derived/flags.jsonl', 'derived/window_flags.json', 'harvest.json'})
        self.assertTrue(differing <= set(self.off.PROVENANCE_FIELDS))
        self.assertEqual(self.off.archive_projection(b), self.off.archive_projection(a))


class LightTriageTests(unittest.TestCase):
    """The light triage's verdicts equal the full desk's on synthetic thermal records."""

    def setUp(self):
        from joulewise.align.apple import light_triage, thermal_desk
        from tests.align.test_thermal_desk import member
        self.lt, self.desk, self.member = light_triage, thermal_desk, member

    def roster(self, seed):
        rng = random.Random(seed)
        rows, records = [], []
        pathologies = [[], ['thermal.os_level_nonzero'], ['thermal.gate_timeout:G1:2'], ['episode.deadman:1800'],
                       ['thermal.collector_thread_dead'], ['episode.malformed_tool_call:3'], ['endpoint_error:x']]
        for i in range(22):
            pair = ('spam_filter_update', 'bank_transfer_2')[i % 2]
            role = 'D' if i >= 4 else 'anchor'
            row = {'run_id': f'm{i:02d}', 'role': role, 'task_pair': pair,
                   'condition': 'sabotage' if i in (20, 21) else 'benign', 'ordinal': i}
            r = self.member(row['run_id'], energy=1000 + rng.uniform(-2, 2), slow=40 + rng.uniform(-1, 1))
            r['model'] = 'qwen3.8-27b' if role == 'D' else 'qwen3-30b-a3b'
            r['window'] = 'D1'
            r['flags'] = list(rng.choice(pathologies)) if rng.random() < .4 else []
            if rng.random() < .15:
                r['energy_flags'] = ['trace.missing']
            if i in (6, 7):
                r['identical_work_group'] = 'g'
                if rng.random() < .5:
                    r['tokens'] = [[9, 9]]                       # X5 token mismatch
            r['calibration_exclusions'] = self.desk.calibration_exclusions(r)
            rows.append(row)
            records.append(r)
        codes = {}
        for row in rows:
            if rng.random() < .3:
                codes[row['run_id']] = rng.sample(['battery.member_span', 'contention.outside_process',
                                                   'member.strict_invalid', 'clock.step'], rng.randint(1, 2))
        return rows, records, codes

    def report(self, records):
        return self.desk.window_report(deepcopy(records), v4=True)

    def test_u1_u3_and_thermal_escalation_are_invariant_to_the_harvest(self):
        for seed in range(40):
            with self.subTest(seed=seed):
                rows, light, codes = self.roster(seed)
                full = [self.lt.apply_harvest_codes(deepcopy(r), codes.get(r['id'], [])) for r in light]
                lr, fr = self.report(light), self.report(full)
                for key in fr['model_windows']:
                    for n in (1, 2, 3):
                        self.assertEqual(lr['model_windows'][key][f'U{n}'], fr['model_windows'][key][f'U{n}'])
                self.assertEqual(self.lt.thermal_escalation(lr), self.lt.thermal_escalation(fr))
                self.assertEqual(self.lt.u_checks(lr), self.lt.u_checks(fr))

    def test_eligibility_final_is_a_subset_and_equal_without_harvest_exclusions(self):
        seen_strict_subset = False
        for seed in range(40):
            with self.subTest(seed=seed):
                rows, light, codes = self.roster(seed)
                captured = {row['run_id'] for row in rows if row['run_id'] != 'm09'}
                full = [self.lt.apply_harvest_codes(deepcopy(r), codes.get(r['id'], [])) for r in light]
                provisional = self.lt.member_eligibility(light, rows, captured=captured, final=False)
                final = self.lt.member_eligibility(full, rows, captured=captured, final=True)
                self.assertEqual(provisional['status'], final['status'])
                self.assertEqual(provisional['captured_members'], final['captured_members'])
                self.assertLessEqual(set(final['eligible']), set(provisional['eligible']))
                seen_strict_subset |= set(final['eligible']) < set(provisional['eligible'])
                none = [self.lt.apply_harvest_codes(deepcopy(r), []) for r in light]
                same = self.lt.member_eligibility(none, rows, captured=captured, final=True)
                self.assertEqual(same['eligible'], provisional['eligible'])
                self.assertNotIn('m09', provisional['eligible'])
        self.assertTrue(seen_strict_subset)

    def test_fixed_8_decisions_match_until_counts_are_used(self):
        from joulewise.align.apple import v4_cadence
        rows, light, codes = self.roster(3)
        captured = {row['run_id'] for row in rows}
        full = [self.lt.apply_harvest_codes(deepcopy(r), codes.get(r['id'], [])) for r in light]
        prov = self.lt.calibration_row('C', rows, self.lt.member_eligibility(light, rows, captured=captured, final=False))
        fin = self.lt.calibration_row('C', rows, self.lt.member_eligibility(full, rows, captured=captured, final=True))
        for k in range(1, 8):  # windows 1-7: the arm decision reads captured counts only
            with self.subTest(windows=k):
                p = v4_cadence.calibration_stop([{**prov, 'window': f'C{i}'} for i in range(k)])
                f = v4_cadence.calibration_stop([{**fin, 'window': f'C{i}'} for i in range(k)])
                self.assertEqual((p['decision'], p['attempted']), (f['decision'], f['attempted']))
        eight = [{**fin, 'window': f'C{i}'} for i in range(7)] + [{**prov, 'window': 'C7'}]
        self.assertEqual(v4_cadence.calibration_stop(eight)['decision'], 'pending_final_eligibility')

    def test_full_desk_routes_its_harvest_step_and_u_checks_through_light_triage(self):
        import inspect
        from scripts import align_v4_session
        source = inspect.getsource(align_v4_session.powermode_desk_check)
        self.assertIn('light_triage.apply_harvest_codes(r, ', source)
        self.assertIn('light_triage.u_checks(report', source)
        self.assertNotIn("r['excluded'] =", source)


class DeskWorkersTests(unittest.TestCase):
    def test_desk_passes_harvest_workers_only_when_asked(self):
        from scripts import align_pilot_session as pilot
        captured = []

        def run(argv, **_):
            captured.append(argv)
            raise RuntimeError('stop after argv')
        with mock.patch.object(pilot, 'desk', wraps=pilot.desk):
            for workers, expect in ((None, None), (4, ['--workers', '4'])):
                with self.subTest(workers=workers), tempfile.TemporaryDirectory(dir=REAL_TMP) as td:
                    session = self.session(Path(td))
                    with self.assertRaisesRegex(RuntimeError, 'stop after argv'):
                        pilot.desk(session, run=run, **({} if workers is None else {'harvest_workers': workers}))
                    argv = captured[-1]
                    self.assertEqual(argv[-2:] == ['--workers', '4'], expect is not None)
                    self.assertNotIn('--workers', argv[:-2])
        with self.assertRaisesRegex(ValueError, 'positive integer'):
            pilot.desk(self.session(Path(tempfile.mkdtemp(dir=REAL_TMP))), run=run, harvest_workers=0)

    def session(self, root):
        from scripts import align_pilot_session as pilot
        custody = root / 'custody'
        (custody / 'night').mkdir(parents=True)
        (custody / 'night/result.json').write_text('{}')
        (root / 'staging').mkdir()
        (root / 'runs').mkdir()
        registration = root / 'kit/registration'
        registration.mkdir(parents=True)
        (registration.parent / 'collection_plan.json').write_text(json.dumps({'members': []}))
        (root / 'plan.json').write_text(json.dumps({'custody_root': str(custody)}))
        (root / 'session.json').write_text(json.dumps({
            'plan_path': str(root / 'plan.json'), 'session_id': 's', 'measurement_root': str(root),
            'registration_dir': str(registration), 'runs_roots': {'claim': str(root / 'runs')}, 'inputs': {}}))
        return root


class RunnerTests(unittest.TestCase):
    """MBP pack and Air unpack through the CLI; the Air mirror must match the MBP checkout."""

    def fake_run(self, head):
        import subprocess

        def run(argv, **_):
            out = {'rev-parse': head + '\n', 'status': ''}.get(argv[3], 'Python 3.13.x\nabc\n')
            return subprocess.CompletedProcess(argv, 0, stdout=out, stderr='')
        return run

    def test_pack_then_unpack_only_onto_an_identical_mirror(self):
        import io
        from scripts import align_v4_harvest_off as runner
        root = Path(tempfile.mkdtemp(prefix='runner-', dir=REAL_TMP))
        self.addCleanup(shutil.rmtree, root, True)
        session, checkout = root / 'session', root / 'checkout'
        (session / 'custody/night').mkdir(parents=True)
        (session / 'custody/night/result.json').write_text('{}')
        (checkout / '.venv/bin').mkdir(parents=True)
        (checkout / '.venv/bin/python').write_text('')
        ledger = checkout / 'runs/ledger.jsonl'
        ledger.parent.mkdir()
        ledger.write_text('{"row": 1}\n')
        (session / 'plan.json').write_text(json.dumps({'custody_root': str(session / 'custody'),
                                                       'hazard_window': {'bindings': {'ledger_path': str(ledger)}}}))
        (session / 'session.json').write_text(json.dumps({'plan_path': str(session / 'plan.json'),
                                                          'measurement_root': str(session / 'measurement'),
                                                          'source_measurement_root': str(checkout)}))
        with contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(runner.main(['pack', '--session-root', str(session), '--out', str(root / 'o')],
                                         run=self.fake_run('a' * 40)), 0)
        packed = json.loads(out.getvalue())
        self.assertEqual(packed['external'], [str(ledger)])
        shutil.move(session, root / 'session.mbp')
        with contextlib.redirect_stderr(io.StringIO()) as err:
            self.assertEqual(runner.main(['unpack', '--offload', str(root / 'o')], run=self.fake_run('b' * 40)), 1)
        self.assertIn('mirror differs', err.getvalue())
        self.assertFalse(session.exists())
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(runner.main(['unpack', '--offload', str(root / 'o')], run=self.fake_run('a' * 40)), 0)
        self.assertEqual(inventory(session), inventory(root / 'session.mbp'))


PM_FIXTURES = ('powermetrics_sample.plist', 'replay/envelope-01/raw/powermetrics-idle-1.plist',
               'controller_g2b/block3-pre/raw/powermetrics.plist.gz', 'd078_r01/raw/powermetrics.plist',
               'd117_v2_production/strict_seed_bundle/raw/powermetrics_idle.plist',
               'd117_v2_production/strict_seed_bundle/raw/powermetrics_idle_post.plist',
               'd117_v2_production/strict_seed_bundle/raw/powermetrics.plist')


def fixture_plist(relative):
    import gzip
    raw = (Path(__file__).resolve().parents[1] / 'fixtures' / relative).read_bytes()
    return gzip.decompress(raw) if relative.endswith('.gz') else raw


class PmReduceTests(unittest.TestCase):
    """Reduce-once: the targeted extractor equals plistlib, and the columns equal the registered parser."""

    def setUp(self):
        from joulewise.align.apple import pm_reduce
        self.r = pm_reduce

    def test_fast_extractor_equals_plistlib_on_every_fixture_document(self):
        total = 0
        for relative in PM_FIXTURES:
            with self.subTest(fixture=relative):
                data = fixture_plist(relative)
                parts = [p for p in data.split(b'\0') if p.strip()]
                expected = [self.r._without_clusters(plistlib.loads(p)) for p in parts]
                self.assertTrue(all(self.r.strip_clusters(p) is not None for p in parts))  # fast path taken
                self.assertEqual(self.r.fast_documents(data, verify_every=1), expected)
                total += len(parts)
        self.assertGreater(total, 1700)

    def test_columns_equal_the_registered_parser(self):
        for relative in PM_FIXTURES:
            with self.subTest(fixture=relative):
                data = fixture_plist(relative)
                records = pm.parse_powermetrics_records(data)
                binding, rows = self.r.read_npy(self.r.reduce_plist(data))
                self.assertEqual(binding['raw_sha256'], hashlib.sha256(data).hexdigest())
                self.assertEqual(binding['raw_size'], len(data))
                self.assertEqual(len(rows), len(records))
                for row, rec in zip(rows, records):
                    self.assertEqual(row[0], rec.elapsed_ns)
                    self.assertEqual(row[1], rec.metadata['plist_timestamp_s'])
                    self.assertEqual(row[2:5], tuple(rec.rail_power_w[k] for k in pm.RAIL_MANIFEST))
                    self.assertEqual(row[5:8], tuple(rec.rail_energy_mj[k] for k in
                                                     ('cpu_energy', 'gpu_energy', 'ane_energy')))
                    self.assertEqual(row[8], self.r.THERMAL_CODES[rec.thermal_pressure])

    def test_awkward_documents_fall_back_to_whole_parse_and_stay_equal(self):
        data = fixture_plist(PM_FIXTURES[-1])
        part = [p for p in data.split(b'\0') if p.strip()][0]
        doubled = part.replace(b'<key>kern_bootargs</key>\n\t<string></string>',
                               b'<key>kern_bootargs</key>\n\t<string>&lt;key&gt;clusters&lt;/key&gt;</string>', 1)
        empty = part.replace(b'<key>clusters</key>', b'<key>clusters</key><array/><key>x</key>', 1)
        for document in (doubled, empty):
            self.assertEqual(self.r.fast_documents(document, verify_every=1),
                             [self.r._without_clusters(plistlib.loads(document))])

    def test_refuses_when_the_fast_path_would_differ(self):
        data = fixture_plist(PM_FIXTURES[-1])
        wrong = lambda part: part.replace(b'<key>thermal_pressure</key>', b'<key>thermal_pressure_x</key>', 1)  # noqa: E731
        with mock.patch.object(self.r, 'strip_clusters', side_effect=lambda p: wrong(p)):
            with self.assertRaisesRegex(self.r.ReduceRefused, 'differs from plistlib at document 0'):
                self.r.fast_documents(data)

    def test_member_pool_equals_serial_and_binds_every_raw_file(self):
        root = Path(tempfile.mkdtemp(prefix='reduce-', dir=REAL_TMP))
        self.addCleanup(shutil.rmtree, root, True)
        tasks = lambda out: [{'run_id': rid, 'bundle_path': str(w.template() / rid), 'out_dir': str(root / out)}  # noqa: E731
                             for rid, *_ in w.MEMBERS[:3]]
        serial = self.r.reduce_members(tasks('serial'), workers=1)
        pooled = self.r.reduce_members(tasks('pooled'), workers=3)
        self.assertEqual(pooled, serial)
        self.assertEqual(inventory(root / 'pooled'), inventory(root / 'serial'))
        for member in serial:
            self.assertEqual(len(member['files']), 3)
            for row in member['files']:
                raw = (w.template() / row['raw']).read_bytes()
                self.assertEqual(row['raw_sha256'], hashlib.sha256(raw).hexdigest())
                self.assertLess(row['reduced_size'] * 50, row['raw_size'])


if __name__ == '__main__':
    unittest.main()
