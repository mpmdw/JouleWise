"""B5 slots proofs (RL-135 spec 2.5) on a synthetic git repository; no real suite is run."""
import contextlib
import io
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts import align_r1_slots_proofs as proofs

TEN = [f'src/f{i}.py' for i in range(10)]
REGISTRATION = '''
import subprocess
from pathlib import Path
R1_EXECUTED_SOURCES = %r


def verify_r1_executed_sources(root, slots):
    commit = slots.get("executed_commit")
    for path in R1_EXECUTED_SOURCES:
        night = subprocess.run(["git", "show", f"{commit}:{path}"], cwd=root, capture_output=True).stdout
        if (Path(root) / path).read_bytes() != night:
            raise ValueError(f"R1 executed source differs (condition 13): {path}")
    return commit
''' % (TEN,)
FAKE_TESTS = '''
import unittest


class Good(unittest.TestCase):
    def test_a(self):
        pass

    def test_b(self):
        """A docstring puts the result on the next line."""


class Skips(unittest.TestCase):
    @unittest.skip("not here")
    def test_s(self):
        pass


class Mixed(unittest.TestCase):
    def test_ok(self):
        pass

    @unittest.skip("one skip spoils the class")
    def test_skip(self):
        pass
'''
P1 = ('tests.test_fake.Good.test_a', 'tests.test_fake.Good.test_b')
P4 = ('tests.test_fake.Good', 'tests.test_fake.Good.test_a', 'tests.test_fake.Good.test_b')


class SlotsProofTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / 'repo'
        self.root.mkdir()
        self.git('init', '-q')
        for path in TEN:
            (self.root / path).parent.mkdir(parents=True, exist_ok=True)
            (self.root / path).write_text(path + '\n')
        reg = self.root / 'joulewise/align/apple/v4_registration.py'
        reg.parent.mkdir(parents=True)
        reg.write_text(REGISTRATION)
        (self.root / 'tests').mkdir()
        (self.root / 'tests/__init__.py').write_text('')
        (self.root / 'tests/test_fake.py').write_text(FAKE_TESTS)
        self.commit('night')
        self.night = self.git('rev-parse', 'HEAD')
        slots = self.root / proofs.SLOTS_PATH
        slots.parent.mkdir(parents=True)
        slots.write_text(json.dumps({'executed_commit': self.night}, sort_keys=True) + '\n')
        self.commit('slots')
        self.record = Path(self.tmp.name) / 'record.json'
        self.write_record(proofs.sha256_bytes(slots.read_bytes()))
        patches = [mock.patch.object(proofs, 'PROOF1_IDS', P1), mock.patch.object(proofs, 'PROOF4_IDS', P4)]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)

    def tearDown(self):
        self.tmp.cleanup()

    def git(self, *args):
        return subprocess.check_output(['git', *args], cwd=self.root, text=True).strip()

    def commit(self, message):
        self.git('add', '.')
        self.git('-c', 'user.name=Synthetic', '-c', 'user.email=synthetic@example.invalid',
                 'commit', '-qm', message)

    def write_record(self, digest):
        self.record.write_text(json.dumps({'identity': {'registration_sha256': digest}}))

    def prove(self):
        return proofs.prove(self.root, self.record, self.night)

    def by_id(self, report):
        return {p['id']: p for p in report['proofs']}

    def test_all_ok(self):
        report = self.prove()
        self.assertTrue(report['all_ok'], json.dumps(report, indent=1))
        self.assertEqual(report['head'], self.git('rev-parse', 'HEAD'))
        self.assertEqual(len(report['ten_paths']), 10)
        self.assertTrue(all(r['equals_night'] for r in report['ten_paths']))
        lines = self.by_id(report)['proof1:test_b']['evidence_lines']
        self.assertTrue(lines and lines[0].endswith('... ok'), lines)
        self.assertEqual(len(self.by_id(report)['proof4:Good']['evidence_lines']), 2)
        out = Path(self.tmp.name) / 'proofs.json'
        with contextlib.redirect_stdout(io.StringIO()):
            rc = proofs.main(['--root', str(self.root), '--record', str(self.record),
                              '--night-commit', self.night, '--json-out', str(out)])
        self.assertEqual(rc, 0)
        self.assertEqual(json.loads(out.read_text())['schema'], proofs.SCHEMA)
        self.assertEqual(json.dumps(self.prove(), sort_keys=True), json.dumps(report, sort_keys=True))

    def test_one_of_the_ten_differing_fails_proof_3(self):
        (self.root / TEN[3]).write_text('stray edit\n')
        self.commit('stray')
        report = self.prove()
        p3 = self.by_id(report)['proof3:condition13_sources']
        self.assertFalse(p3['ok'])
        self.assertFalse(report['all_ok'])
        self.assertEqual([r['path'] for r in report['ten_paths'] if not r['equals_night']], [TEN[3]])
        self.assertTrue(any('differs' in line for line in p3['evidence_lines']), p3)

    def test_a_skipped_test_is_not_ok(self):
        for ids in (('tests.test_fake.Skips.test_s',), ('tests.test_fake.Mixed',)):
            with self.subTest(ids=ids), mock.patch.object(proofs, 'PROOF4_IDS', ids):
                report = self.prove()
                proof = next(p for p in report['proofs'] if p['id'].startswith('proof4:'))
                self.assertFalse(proof['ok'])
                self.assertTrue(any('skipped' in line for line in proof['evidence_lines']), proof)
                self.assertFalse(report['all_ok'])

    def test_missing_test_id_is_not_ok(self):
        with mock.patch.object(proofs, 'PROOF1_IDS', ('tests.test_fake.Good.test_missing',)):
            report = self.prove()
        proof = report['proofs'][0]
        self.assertFalse(proof['ok'])
        self.assertTrue(proof['evidence_lines'][0].startswith('test id not found'), proof)

    def test_proof_2_slot_hash_and_commit(self):
        self.write_record('0' * 64)
        self.assertFalse(self.by_id(self.prove())['proof2:slots_commit_and_sha']['ok'])
        self.record.write_text(json.dumps({'registration_sha256': 'top-level is not read'}))
        p2 = self.by_id(self.prove())['proof2:slots_commit_and_sha']
        self.assertFalse(p2['ok'])
        self.assertTrue(any('absent' in line for line in p2['evidence_lines']))
        slots = self.root / proofs.SLOTS_PATH
        slots.write_text(json.dumps({'executed_commit': '1' * 40}) + '\n')
        self.write_record(proofs.sha256_bytes(slots.read_bytes()))
        report = self.prove()
        self.assertFalse(self.by_id(report)['proof2:slots_commit_and_sha']['ok'])
        self.assertFalse(self.by_id(report)['proof3:condition13_sources']['ok'])   # verify names the wrong commit

    def test_unusable_input_exits_2(self):
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(proofs.main(['--root', str(self.root), '--record', str(self.record),
                                          '--night-commit', 'a6a09e6d7']), 2)


if __name__ == '__main__':
    unittest.main()
