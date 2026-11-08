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

from tests.align import synthetic_custody  # noqa: I001 (BEFORE the B5 fixture: synthetic custody is the default)
from joulewise.adapters import powermetrics as pm
from joulewise.b5 import harvest as h
from tests import test_harvest_b5_window as w

REAL_TMP = os.path.realpath(tempfile.gettempdir())
SEED_PLIST = Path(__file__).resolve().parents[1] / 'fixtures/d117_v2_production/strict_seed_bundle/raw/powermetrics.plist'


def setUpModule():  # noqa: N802 (unittest hook): no test probes a home custody locator
    synthetic_custody.setUpModule()


def tearDownModule():  # noqa: N802 (unittest hook): the shared member template
    w.tearDownModule()
    synthetic_custody.tearDownModule()


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
        return self.off.pack_unbound(self.src, self.root / name, external=(self.ledger,))

    def test_round_trip_restores_every_byte_link_mode_and_ledger_at_the_same_path(self):
        manifest = self.pack()
        before = inventory(self.src)
        shutil.move(self.src, self.root / 'moved')
        self.ledger.write_bytes(b'{"row": 1}\n')       # the Air mirror holds an older prefix
        self.off.unpack_unbound(self.root / 'out', self.src)
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
            self.off.unpack_unbound(self.root / 'out', self.root / 'elsewhere')
        with self.assertRaisesRegex(self.off.OffloadRefused, 'already exists'):
            self.off.unpack_unbound(self.root / 'out')
        shutil.move(self.src, self.root / 'moved')
        payload = self.root / 'out' / self.off.PAYLOAD
        raw = bytearray(payload.read_bytes())
        raw[len(raw) // 2] ^= 0xFF
        payload.write_bytes(bytes(raw))
        with self.assertRaisesRegex(self.off.OffloadRefused, 'payload digest mismatch'):
            self.off.unpack_unbound(self.root / 'out')
        self.assertFalse(self.src.exists())

    def test_refuses_a_manifest_mismatch_and_leaves_nothing_behind(self):
        manifest = self.pack()
        manifest['entries']['runs/m1/run.sh']['size'] += 1
        (self.root / 'out' / self.off.MANIFEST).write_text(json.dumps(manifest))
        shutil.move(self.src, self.root / 'moved')
        with self.assertRaisesRegex(self.off.OffloadRefused, 'differs from manifest'):
            self.off.unpack_unbound(self.root / 'out')
        self.assertFalse(self.src.exists())
        self.assertFalse(self.src.with_name('session.restoring').exists())

    def test_refuses_a_ledger_that_is_not_an_append_only_extension(self):
        self.pack()
        shutil.move(self.src, self.root / 'moved')
        self.ledger.write_bytes(b'{"row": 9}\n')
        with self.assertRaisesRegex(self.off.OffloadRefused, 'append-only'):
            self.off.unpack_unbound(self.root / 'out')
        self.assertFalse(self.src.exists())

    def test_record_bound_manifest_chains_committed_digest_to_restored_bytes(self):
        finalized = self.off.finalized_manifest(self.src)              # MBP, at finalize
        committed = self.off.manifest_sha256(finalized)                 # goes into the window record
        (self.src / 'runs/m1/late.txt').write_text('written after finalize')
        with self.assertRaisesRegex(self.off.OffloadRefused, 'finalized record manifest'):
            self.off.pack(self.src, self.root / 'late', finalized=finalized)
        self.assertFalse((self.root / 'late').exists())
        (self.src / 'runs/m1/late.txt').unlink()
        manifest = self.off.pack(self.src, self.root / 'bound', finalized=finalized)
        self.assertEqual(manifest['finalized_manifest_sha256'], committed)
        shutil.move(self.src, self.root / 'moved')
        with self.assertRaisesRegex(self.off.OffloadRefused, 'committed digest'):
            self.off.unpack(self.root / 'bound', finalized=finalized, finalized_sha256='0' * 64)
        forged = deepcopy(finalized)
        forged['entries']['runs/m1/run.sh'] = {'sha256': '1' * 64, 'size': 10}
        with self.assertRaisesRegex(self.off.OffloadRefused, 'offload manifest differs'):
            self.off.unpack(self.root / 'bound', finalized=forged, finalized_sha256=self.off.manifest_sha256(forged))
        self.assertFalse(self.src.exists())
        self.off.unpack(self.root / 'bound', finalized=finalized, finalized_sha256=committed)
        self.assertEqual(self.off.finalized_manifest(self.src), finalized)

    def test_refuses_unsupported_file_types(self):
        os.mkfifo(self.src / 'fifo')
        with self.assertRaisesRegex(self.off.OffloadRefused, 'unsupported file type'):
            self.pack('out2')


@unittest.skipUnless(shutil.which('zstd'), 'zstd CLI required')
class R17ReviewCustodyTests(unittest.TestCase):
    """R17 review F1/F2 and the Sol seat-2 custody findings: the finite external closure."""

    def setUp(self):
        from joulewise.align.apple import harvest_offload as off
        self.off = off
        self.root = Path(tempfile.mkdtemp(prefix='offload-closure-', dir=REAL_TMP))
        self.addCleanup(shutil.rmtree, self.root, True)
        self.src = self.root / 'session'
        (self.src / 'runs').mkdir(parents=True)
        (self.src / 'runs/raw.txt').write_bytes(b'raw\n')
        self.checkout = self.root / 'checkout'
        (self.checkout / 'runs').mkdir(parents=True)
        (self.checkout / 'joulewise.py').write_bytes(b'code\n')
        self.ledger = self.checkout / 'runs/ledger.jsonl'
        self.ledger.write_bytes(b'{"row": 1}\n')
        (self.src / 'measurement').symlink_to(self.checkout, target_is_directory=True)
        import subprocess
        subprocess.run(['git', 'init', '-q', str(self.checkout)], check=True, capture_output=True)   # D3: ignored-content probe
        self.identity = {'head': 'a' * 40, 'tracked_clean': True}
        self.mirror = {'root': str(self.checkout), 'identity': self.identity}

    def finalize(self, **kwargs):
        return self.off.finalized_manifest(self.src, **kwargs)

    def test_library_route_requires_the_record_binding(self):
        with self.assertRaisesRegex(self.off.OffloadRefused, 'requires the finalized record manifest'):
            self.off.pack(self.src, self.root / 'o', finalized=None)
        self.assertFalse((self.root / 'o').exists())
        self.off.pack_unbound(self.src, self.root / 'o')
        shutil.move(self.src, self.root / 'kept')
        with self.assertRaisesRegex(self.off.OffloadRefused, 'committed digest'):
            self.off.unpack(self.root / 'o', finalized=None, finalized_sha256=None)
        self.assertFalse(self.src.exists())

    def test_mirror_links_bind_the_checkout_identity_and_declared_inputs_their_bytes(self):
        final = self.finalize(mirror=self.mirror, inputs=(self.ledger,))
        self.assertEqual(final['closure']['links']['measurement']['class'], 'mirror')
        self.assertEqual(set(final['closure']['files']), {str(self.ledger)})   # the checkout is never traversed
        with self.assertRaisesRegex(self.off.OffloadRefused, 'mirror differs'):
            self.off.pack(self.src, self.root / 'o', finalized=final, mirror_identity={'head': 'b' * 40})
        self.off.pack(self.src, self.root / 'o', finalized=final, external=(self.ledger,),
                      mirror_identity=self.identity)
        shutil.move(self.src, self.root / 'kept')
        digest = self.off.manifest_sha256(final)
        with self.assertRaisesRegex(self.off.OffloadRefused, 'mirror differs'):
            self.off.unpack(self.root / 'o', finalized=final, finalized_sha256=digest)
        self.assertFalse(self.src.exists())
        self.off.unpack(self.root / 'o', finalized=final, finalized_sha256=digest, mirror_identity=self.identity)
        self.assertEqual(self.finalize(mirror=self.mirror, inputs=(self.ledger,)), final)   # same closure on the Air

    def test_a_retargeted_external_destination_refuses_and_writes_nothing(self):
        # Sol seat 2: the payload names its own destinations; only the record-bound closure may.
        final = self.finalize(mirror=self.mirror, inputs=(self.ledger,))
        manifest = self.off.pack(self.src, self.root / 'o', finalized=final, external=(self.ledger,),
                                 mirror_identity=self.identity)
        code = self.checkout / 'collector.py'
        code.write_bytes(b'')
        next(iter(manifest['external'].values()))['path'] = str(code)
        (self.root / 'o' / self.off.MANIFEST).write_text(json.dumps(manifest))
        shutil.move(self.src, self.root / 'kept')
        with self.assertRaisesRegex(self.off.OffloadRefused, 'not bound by the finalized record manifest'):
            self.off.unpack(self.root / 'o', finalized=final, finalized_sha256=self.off.manifest_sha256(final),
                            mirror_identity=self.identity)
        self.assertEqual(code.read_bytes(), b'')
        self.assertEqual(self.ledger.read_bytes(), b'{"row": 1}\n')
        self.assertFalse(self.src.exists())

    def test_byte_closure_is_reverified_on_the_air_before_publication(self):
        shutil.rmtree(self.checkout / '.git')    # no mirror here: a plain linked directory
        final = self.finalize()           # no mirror: the linked directory is bound by its bytes
        self.assertEqual(set(final['closure']['files']), {str(self.checkout / 'joulewise.py'), str(self.ledger)})
        self.off.pack(self.src, self.root / 'o', finalized=final)
        shutil.move(self.src, self.root / 'kept')
        digest = self.off.manifest_sha256(final)
        for change, undo in ((lambda: (self.checkout / 'joulewise.py').write_bytes(b'Air code\n'),
                              lambda: (self.checkout / 'joulewise.py').write_bytes(b'code\n')),
                             (lambda: (self.checkout / 'extra.py').write_bytes(b''),
                              lambda: (self.checkout / 'extra.py').unlink())):
            change()
            with self.assertRaisesRegex(self.off.OffloadRefused, 'differs from the finalized record manifest'):
                self.off.unpack(self.root / 'o', finalized=final, finalized_sha256=digest)
            self.assertFalse(self.src.exists())
            undo()
        self.off.unpack(self.root / 'o', finalized=final, finalized_sha256=digest)

    def test_an_absent_link_target_stays_absent(self):
        missing = self.root / 'never-created'
        (self.src / 'dangling').symlink_to(missing)
        final = self.finalize(mirror=self.mirror)
        self.assertEqual(final['closure']['links']['dangling']['class'], 'absent')
        self.off.pack(self.src, self.root / 'o', finalized=final, mirror_identity=self.identity)
        shutil.move(self.src, self.root / 'kept')
        missing.write_bytes(b'appeared on the Air')
        with self.assertRaisesRegex(self.off.OffloadRefused, 'resolves differently'):
            self.off.unpack(self.root / 'o', finalized=final, finalized_sha256=self.off.manifest_sha256(final),
                            mirror_identity=self.identity)

    def test_the_byte_closure_is_finite_and_never_follows_further_links(self):
        weights = self.root / 'weights'
        weights.mkdir()
        (weights / 'model.safetensors').write_bytes(b'w' * 64)
        (self.src / 'model').symlink_to(weights, target_is_directory=True)
        with mock.patch.object(self.off, 'CLOSURE_MAX_FILE_BYTES', 32):
            with self.assertRaisesRegex(self.off.OffloadRefused, 'never bound or copied'):
                self.finalize(mirror=self.mirror)
        with mock.patch.object(self.off, 'CLOSURE_MAX_FILES', 1):
            (weights / 'other.bin').write_bytes(b'x')
            with self.assertRaisesRegex(self.off.OffloadRefused, 'not finite'):
                self.finalize(mirror=self.mirror)
        (weights / 'nested').symlink_to(self.root)
        with self.assertRaisesRegex(self.off.OffloadRefused, 'further link'):
            self.finalize(mirror=self.mirror)

    def test_a_nested_session_chain_is_resolved_in_the_staged_tree_and_still_bound(self):
        # Confirmation seat: S/selected -> external alias -> S/current -> data. The honest layout restores
        # (the session hops resolve inside the staged tree); retargeting the external alias still refuses.
        for retarget in (False, True):
            with self.subTest(retarget=retarget):
                base = Path(tempfile.mkdtemp(prefix='nested-', dir=REAL_TMP))
                self.addCleanup(shutil.rmtree, base, True)
                source = base / 'session'
                source.mkdir()
                (source / 'data.json').write_bytes(b'{"a":1}')
                (source / 'other.json').write_bytes(b'{"b":2}')
                (source / 'current.json').symlink_to('data.json')
                alias = base / 'operator-current'
                alias.symlink_to(source / 'current.json')
                (source / 'selected.json').symlink_to(alias)
                final = self.off.finalized_manifest(source)
                self.off.pack(source, base / 'o', finalized=final)
                source.rename(base / 'kept')
                if retarget:
                    alias.unlink()
                    alias.symlink_to(source / 'other.json')
                    with self.assertRaisesRegex(self.off.OffloadRefused, 'resolves differently'):
                        self.off.unpack(base / 'o', finalized=final,
                                        finalized_sha256=self.off.manifest_sha256(final))
                    self.assertFalse(source.exists())
                else:
                    self.off.unpack(base / 'o', finalized=final, finalized_sha256=self.off.manifest_sha256(final))
                    self.assertEqual((source / 'selected.json').read_bytes(), b'{"a":1}')

    def test_transport_manifest_cannot_choose_the_namespace(self):
        final = self.finalize(mirror=self.mirror)
        manifest = self.off.pack(self.src, self.root / 'o', finalized=final, mirror_identity=self.identity)
        manifest['source_root'] = str(self.root / 'elsewhere')
        (self.root / 'o' / self.off.MANIFEST).write_text(json.dumps(manifest))
        with self.assertRaisesRegex(self.off.OffloadRefused, 'restore namespace differs'):
            self.off.unpack(self.root / 'o', finalized=final, finalized_sha256=self.off.manifest_sha256(final),
                            mirror_identity=self.identity)
        self.assertFalse((self.root / 'elsewhere').exists())


class SyntheticCustodyFenceTests(unittest.TestCase):
    """Test hygiene: inside these modules a home custody locator is never probed."""

    def test_home_locators_are_answered_absent_before_any_probe(self):
        from joulewise import calibration_ledger as ledger
        self.assertEqual(os.environ.get('JW_B5_SYNTHETIC_ONLY'), '1')
        locator = synthetic_custody.HOME / 'night-custody' / 'synthetic-never-probed'
        before = len(synthetic_custody.REFUSED)
        with mock.patch('pathlib.Path.exists', side_effect=AssertionError('probed')):
            self.assertEqual(ledger._custody_probe_paths(locator, mode='read_replay'), ())
        self.assertEqual(synthetic_custody.REFUSED[before:], [str(locator)])
        self.assertTrue(synthetic_custody.outside_synthetic_custody(locator))
        self.assertFalse(synthetic_custody.outside_synthetic_custody(Path(REAL_TMP) / 'x'))
        self.assertFalse(synthetic_custody.outside_synthetic_custody(synthetic_custody.REPO / 'tests'))


class SamePathHarvestEqualityTests(unittest.TestCase):
    """MBP harvest on the live record == Air harvest on the verified copy at the same path."""

    def setUp(self):
        from joulewise.align.apple import harvest_offload as off
        self.off = off
        self.tmp = Path(tempfile.mkdtemp(prefix='harvest-off-', dir=REAL_TMP))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.window = w.Window(self.tmp / 'w', catalog_overrides={'member.cooldown_evidence_unverified': 'DISCLOSE'})
        self.finalized = self.off.finalized_manifest(self.tmp / 'w')       # record-bound, as in production
        self.manifest = self.off.pack(self.tmp / 'w', self.tmp / 'offload', finalized=self.finalized)

    def seams(self, workers, boot, pinned):
        clocks = {'now': lambda: 1786300000.0, 'monotonic_ns': lambda: 123} if pinned else {}
        # The harvest program's checkout record is pinned: on the Air, unpack's mirror check makes it
        # identical to the MBP's; in this shared worktree, concurrent test modules may dirty git status.
        checkout = h.harvest_checkout(block_six=False)
        return h.Seams(group_alive=lambda pgid: False, exclusions_compute=w.EXCLUSIONS,
                       boot_session_uuid=lambda: boot, workers=workers, io_workers=workers,
                       harvest_checkout=lambda **_: checkout, **clocks)

    def mbp_then_air(self, *, pinned, boots):
        # MBP: today's path (one worker, no parse dedupe) on the live record.
        with mock.patch.object(pm, 'document_memo', contextlib.nullcontext):
            mbp = h.harvest(h.resolve_inputs(self.window.plan_path), self.window.archive,
                            seams=self.seams(1, boots[0], pinned), prepare_desk=True)
        os.rename(self.tmp / 'w', self.tmp / 'w.mbp')
        # Air: restore the verified copy at the SAME path; three workers, dedupe on.
        self.off.unpack(self.tmp / 'offload', self.tmp / 'w', finalized=self.finalized,
                        finalized_sha256=self.off.manifest_sha256(self.finalized))
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
            self.assertEqual(runner.main(['finalize-manifest', '--session-root', str(session),
                                          '--out', str(root / 'M.json')], run=self.fake_run('a' * 40)), 0)
        finalized = json.loads(out.getvalue())
        self.assertEqual(hashlib.sha256((root / 'M.json').read_bytes()).hexdigest(), finalized['sha256'])
        with contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(runner.main(['pack', '--session-root', str(session), '--out', str(root / 'o'),
                                          '--finalized-manifest', str(root / 'M.json')],
                                         run=self.fake_run('a' * 40)), 0)
        packed = json.loads(out.getvalue())
        self.assertEqual(packed['external'], [str(ledger)])
        shutil.move(session, root / 'session.mbp')
        with contextlib.redirect_stderr(io.StringIO()) as err:      # R17 review F2: the binding is required
            self.assertEqual(runner.main(['unpack', '--offload', str(root / 'o')], run=self.fake_run('a' * 40)), 1)
        self.assertIn('requires the record binding', err.getvalue())
        with contextlib.redirect_stderr(io.StringIO()) as err:
            self.assertEqual(runner.main(['unpack', '--offload', str(root / 'o'), '--finalized-manifest',
                                          str(root / 'M.json'), '--finalized-sha256', finalized['sha256']],
                                         run=self.fake_run('b' * 40)), 1)
        self.assertIn('mirror differs', err.getvalue())
        self.assertFalse(session.exists())
        with contextlib.redirect_stderr(io.StringIO()) as err:
            self.assertEqual(runner.main(['unpack', '--offload', str(root / 'o'), '--finalized-manifest',
                                          str(root / 'M.json'), '--finalized-sha256', '0' * 64],
                                         run=self.fake_run('a' * 40)), 1)
        self.assertIn('committed digest', err.getvalue())
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(runner.main(['unpack', '--offload', str(root / 'o'), '--finalized-manifest',
                                          str(root / 'M.json'), '--finalized-sha256', finalized['sha256']],
                                         run=self.fake_run('a' * 40)), 0)
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


class SyntheticV4SessionE2ETests(unittest.TestCase):
    """R17: triage -> desk -> final -> reduce through the runner on a synthetic v4 kit session.

    Real native-endpoint bundles (fake MLX), a v4 kit layout with a synthetic registration,
    the real light triage, the real v4 desk (only the harvest subprocess is replaced by a
    synthetic archive writer; the harvest itself is covered by SamePathHarvestEqualityTests),
    the real final row and reduce-once with per-turn tables proven equal to PILOT.json.
    """

    @classmethod
    def setUpClass(cls):
        from joulewise.clock import FakeClock
        from joulewise.align.apple.r1_runtime import SOAK_REFERENCE_SCHEMA
        from scripts import align_v4_kit as kit
        from tests.align.test_apple_endpoint import run_native_review
        from tests.align.test_pilot3_cache import CacheAPI
        from tests.align.test_thermal_desk import DeskTests
        cls.tmp = tempfile.TemporaryDirectory(prefix='v4-e2e-', dir=REAL_TMP)
        root = cls.root = Path(cls.tmp.name).resolve()
        runs, session = root / 'runs', root / 'session'
        reg = root / kit.KIT / 'registration'
        reg.mkdir(parents=True)
        DeskTests.synthetic_registration(None, reg)
        (reg / 'inputs.json').write_text(json.dumps({'R1': {'thermal_policy': {'sensors': {'s_fast': 'TF', 's_slow': 'TS'}}}}))
        (reg / 'r1_soak_reference.json').write_text(json.dumps({'schema': SOAK_REFERENCE_SCHEMA,
                                                               'sensors_c': {'TF': 40.0, 'TS': 38.0}}))
        rows = []
        for i, pair in enumerate(('spam_filter_update', 'bank_transfer_2', 'spam_filter_update')):
            rid = f'e2e-m{i}'
            with mock.patch('joulewise.align.apple.prompt_cache.native_cache_api', return_value=CacheAPI()):
                bundle, status, _ = run_native_review(root / 'src' / rid, 'think', FakeClock(),
                                                      prompt_cache='episode_prefix')
            assert status.status.value == 'succeeded'
            shutil.copytree(bundle, runs / rid)
            episode = runs / rid / 'outputs/align_episode.json'
            value = json.loads(episode.read_text())
            value['episode_id'] = rid
            value.setdefault('hardware', {})['ac_powermode'] = {'value': 0}
            from tests.align.test_thermal_gate import policy as gate_policy
            value['hardware'].setdefault('thermal', {'policy': gate_policy(), 'intervals': []})   # gated: U1-U3 evaluated
            episode.write_text(json.dumps(value))
            rows.append({'run_id': rid, 'ordinal': 5 + i, 'role': 'D', 'model_id': 'qwen3.8-27b',
                         'task_pair': pair, 'condition': 'benign', 'repeat': 1, 'ac_powermode': 0,
                         'stage_id': 's1', 'block': 'A'})
        (reg.parent / 'collection_plan.json').write_text(json.dumps({'members': rows}))
        custody = root / 'custody'
        (custody / 'night').mkdir(parents=True)
        (custody / 'night/result.json').write_text('{}')
        (root / 'plan.json').write_text(json.dumps({'custody_root': str(custody)}))
        (session / 'staging').mkdir(parents=True)
        (session / 'session.json').write_text(json.dumps({
            'session_id': 'v4-e2e', 'measurement_root': str(root), 'registration_dir': str(reg),
            'plan_path': str(root / 'plan.json'), 'inputs': {'custody_root': str(custody)},
            'runs_roots': {'claim': str(runs)}}))
        cls.rows, cls.session, cls.runs = rows, session, runs

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def runner(self, argv, run=None):
        import io
        from scripts import align_v4_harvest_off as runner
        with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()) as err:
            code = runner.main(argv, **({'run': run} if run else {}))
        self.assertEqual(code, 0, err.getvalue()[-2000:])
        return json.loads(out.getvalue().strip().splitlines()[-1])

    def test_triage_desk_final_reduce_end_to_end(self):
        import io
        import subprocess
        from scripts import align_v4_session as v4
        from joulewise.align.apple import light_triage, turn_table, pm_reduce
        session = self.session
        excluded = self.rows[2]['run_id']
        light_path = self.root / 'light_triage.json'
        light = self.runner(['triage', '--session-root', str(session), '--window-id', 'C1', '--out', str(light_path)])
        self.assertEqual(light['member_eligibility']['stage'], 'provisional')
        self.assertEqual(light['calibration_row']['status'], 'provisional')
        source = json.loads(light_path.read_text())
        self.assertEqual(source['schema'], light_triage.SCHEMA)
        self.assertEqual(source['thermal']['schema'], 'joulewise.align.thermal_desk.v1')
        seen = []

        def harvest(argv, **_):
            seen.append(argv)
            derived = session / 'archive/derived'
            derived.mkdir(parents=True, exist_ok=True)
            (derived / 'exclusions.json').write_text(json.dumps(
                {'members_excluded': [{'run_id': excluded, 'codes': ['clock.step']}]}))
            (derived / 'flags.jsonl').write_text('')
            return subprocess.CompletedProcess(argv, 0, stdout='', stderr='')

        def desk_in_process(argv, **_):
            workers = int(argv[argv.index('--harvest-workers') + 1])
            with contextlib.redirect_stdout(io.StringIO()):
                status = v4.desk(session, run=harvest, harvest_workers=workers)
            return subprocess.CompletedProcess(argv, 0 if status else 1)

        desk = self.runner(['desk', '--session-root', str(session), '--workers', 'auto'], run=desk_in_process)
        self.assertGreaterEqual(desk['workers'], 1)
        self.assertEqual(desk['sizing']['peak_basis'], '8x_largest_plist')
        self.assertEqual(seen[0][-2:], ['--workers', str(desk['workers'])])
        final = self.runner(['final', '--session-root', str(session), '--window-id', 'C1'])
        self.assertEqual(final['member_eligibility']['stage'], 'final')
        self.assertLessEqual(set(final['member_eligibility']['eligible']), set(light['member_eligibility']['eligible']))
        self.assertFalse(final['member_eligibility']['members'][excluded]['eligible'])
        self.assertEqual(final['member_eligibility']['captured_members'], light['member_eligibility']['captured_members'])
        self.assertTrue(light['thermal_escalation']['models'])                       # U1-U3 were evaluated
        self.assertEqual(final['thermal_escalation'], light['thermal_escalation'])   # U1-U3 ignore the harvest
        reduced = self.runner(['reduce', '--session-root', str(session), '--out', str(self.root / 'reduced'),
                               '--workers', '2'])
        self.assertEqual(reduced['reduced_members'], len(self.rows))
        pilot = json.loads((session / 'PILOT.json').read_text())
        manifest = json.loads((self.root / 'reduced/MANIFEST.json').read_text())
        for member in manifest['members']:
            table = json.loads((self.root / 'reduced' / member['turn_table']['path']).read_text())
            self.assertTrue(turn_table.equal_to_pilot(table, pilot), member['run_id'])
            self.assertTrue(any(table['channels'][c]['per_turn_j'] for c in table['channels']))
            self.assertTrue(table['thermal']['per_turn'])
            for row in member['files']:
                binding, _rows = pm_reduce.read_npy((self.root / 'reduced' / row['reduced']).read_bytes())
                self.assertEqual(binding['raw_sha256'], row['raw_sha256'])

    def test_turn_table_binds_every_file_the_projection_opens(self):
        # R17 review F8: every bundle file opened while the table is computed is digest-bound.
        import sys
        from joulewise.align.apple import turn_table
        for row in self.rows:
            rid = row['run_id']
            bundle = (self.runs / rid).resolve()
            opened, state = set(), {'on': True}

            def hook(event, args, bundle=bundle, opened=opened, state=state):
                if state['on'] and event == 'open' and args and isinstance(args[0], (str, Path)):
                    path = Path(os.path.abspath(args[0]))
                    if path.is_relative_to(bundle):
                        name = path.relative_to(bundle).as_posix()
                        opened.add(name[:-4] if name.endswith('.zst') else name)
            sys.addaudithook(hook)
            try:
                table = turn_table.member_table(bundle, rid)
            finally:
                state['on'] = False
            self.assertIn('metadata.json', opened)
            self.assertLessEqual(opened, set(table['inputs']), rid)
            self.assertEqual(set(table['inputs']), set(turn_table.INPUT_FILES))

    def test_turn_table_differs_from_a_tampered_pilot(self):
        from joulewise.align.apple import turn_table
        rid = self.rows[0]['run_id']
        table = turn_table.member_table(self.runs / rid, rid)
        thermal = turn_table._canonical(__import__('scripts.align_v4_thermal_desk', fromlist=['x']).enrich_record(
            __import__('joulewise.align.apple.thermal_desk', fromlist=['x']).read_bundle_record(self.runs / rid),
            self.runs / rid))
        from scripts.align_pilot_session import episode_summary
        pilot = {'members': [{'run_id': rid, 'summary': episode_summary(self.runs / rid)}],
                 'extra_checks': {'thermal': {'members': [thermal]}}}
        self.assertTrue(turn_table.equal_to_pilot(table, pilot))
        pilot['extra_checks']['thermal']['members'][0]['per_turn'][0]['owned_j'] = 123.0
        self.assertFalse(turn_table.equal_to_pilot(table, pilot))


class WorkerSizingTests(unittest.TestCase):
    """R17: workers = min(free cores, free memory / measured peak per worker)."""

    def test_auto_workers_takes_the_binding_limit_and_postpones_at_zero(self):
        from scripts import align_v4_harvest_off as runner
        gib = 1 << 30
        self.assertEqual(runner.auto_workers(peak_bytes=4 * gib, memory=28 * gib, cores=10)['workers'], 6)
        self.assertEqual(runner.auto_workers(peak_bytes=1 * gib, memory=64 * gib, cores=3)['workers'], 3)
        # R17 review F5: no worker fits -> postpone (refuse), never one worker over the memory budget.
        with self.assertRaisesRegex(ValueError, 'postpone the desk'):
            runner.auto_workers(peak_bytes=64 * gib, memory=8 * gib, cores=10)
        for bad in (0, -1, 1.5):
            with self.assertRaises(ValueError):
                runner.auto_workers(peak_bytes=bad, memory=64 * gib, cores=10)
        self.assertEqual(runner.free_cores(load_average=7.6, cpu_count=10), 2)
        self.assertEqual(runner.free_cores(load_average=30.0, cpu_count=10), 1)

    def test_sweep_is_used_only_when_bound_to_this_code_and_scaled_to_this_input(self):
        from scripts import align_v4_harvest_off as runner
        root = Path(tempfile.mkdtemp(prefix='sweep-bind-', dir=REAL_TMP))
        self.addCleanup(shutil.rmtree, root, True)
        code = {'head': 'a' * 40, 'python': ['3.13', 'pkgs']}

        def receipt(**fields):
            path = root / 'SWEEP.json'
            path.write_text(json.dumps({'schema': runner.SWEEP_SCHEMA, 'largest_plist_bytes': 500, 'code': code,
                                        'runs': [{'workers': 2, 'exit': 0, 'peak_child_rss_bytes': 1000}], **fields}))
            return path
        with mock.patch.object(runner, 'largest_plist_bytes', return_value=1000), \
             mock.patch.object(runner, 'sweep_code_identity', return_value=code):
            peak, basis = runner.sweep_basis(receipt(), root)
            self.assertEqual((peak, basis['reason']), (2000, 'bound'))            # twice the input: twice the peak
            self.assertEqual(runner.sweep_basis(receipt(largest_plist_bytes=5000), root)[0], 1000)  # never scaled down
            self.assertIsNone(runner.sweep_basis(receipt(code={'head': 'b' * 40, 'python': code['python']}), root)[0])
            self.assertIsNone(runner.sweep_basis(receipt(schema='joulewise.align_v4.harvest_sweep.v1'), root)[0])
            for bad in ({'exit': 1, 'peak_child_rss_bytes': 1000}, {'exit': 0, 'peak_child_rss_bytes': 0},
                        {'exit': 0}):
                with self.assertRaises(ValueError):
                    runner.sweep_basis(receipt(runs=[bad]), root)

    def test_free_memory_reads_vm_stat_pages(self):
        import subprocess
        from scripts import align_v4_harvest_off as runner
        text = ('Mach Virtual Memory Statistics: (page size of 16384 bytes)\nPages free: 100.\n'
                'Pages active: 999.\nPages inactive: 50.\nPages speculative: 10.\nPages purgeable: 5.\n')
        run = lambda argv, **_: subprocess.CompletedProcess(argv, 0, stdout=text)  # noqa: E731
        self.assertEqual(runner.free_memory_bytes(run), 165 * 16384)

    def test_sweep_records_each_worker_count_and_its_peak(self):
        import subprocess
        from scripts import align_v4_harvest_off as runner
        root = Path(tempfile.mkdtemp(prefix='sweep-', dir=REAL_TMP))
        self.addCleanup(shutil.rmtree, root, True)
        (root / 'plan.json').write_text(json.dumps({'custody_root': str(root / 'custody')}))
        (root / 'runs/m1/raw').mkdir(parents=True)
        (root / 'runs/m1/raw/powermetrics.plist').write_bytes(b'x' * 1000)
        (root / 'session.json').write_text(json.dumps({'plan_path': str(root / 'plan.json'), 'session_id': 's',
            'measurement_root': str(root), 'registration_dir': str(root / 'reg'),
            'runs_roots': {'claim': str(root / 'runs')}}))
        calls = []
        run = lambda argv, **_: calls.append(argv) or subprocess.CompletedProcess(argv, 0)  # noqa: E731
        receipt = runner.cmd_sweep(type('A', (), {'session_root': root, 'out': root / 'sweep',
                                                  'workers': [2, 4, 6, 8, 10]})(), run=run)
        self.assertEqual([r['workers'] for r in receipt['runs']], [2, 4, 6, 8, 10])
        self.assertEqual([c[c.index('--workers') + 1] for c in calls], ['2', '4', '6', '8', '10'])
        self.assertEqual(len({c[c.index('--archive-root') + 1] for c in calls}), 5)
        self.assertTrue(all('--profile' in c for c in calls))
        self.assertTrue((root / 'sweep/SWEEP.json').is_file())
        # R17 review F5: the receipt is bound to the input size and the harvest code it measured.
        self.assertEqual(receipt['schema'], runner.SWEEP_SCHEMA)
        self.assertEqual(receipt['largest_plist_bytes'], 1000)
        self.assertEqual(set(receipt['code']), {'root', 'head', 'tracked_clean', 'python'})


if __name__ == '__main__':
    unittest.main()
