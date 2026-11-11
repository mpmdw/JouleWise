"""Failing-first CLI witnesses and local-Git commitment checks; synthetic only."""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from scripts import bytes_analyze as analysis
from tests.bytes_commitment_support import commitment_fixture, git


class CommitmentGateTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix='bytes-commitment-')
        self.addCleanup(temp.cleanup)
        self.repo, self.predictions, self.receipt, self.commit = commitment_fixture(temp.name)
        self.journal = self.receipt.parent / 'unblinding.jsonl'

    def invoke(self, commit=None, before_reduce=None):
        # ROOT selects the analysis checkout, without adding an option that the old CLI lacks.
        with mock.patch.object(analysis, 'ROOT', self.repo, create=True), \
                mock.patch.object(analysis.ba, 'read_json', return_value={}), \
                mock.patch.object(analysis.ba, 'validate_manifest', return_value={}), \
                mock.patch.object(analysis.ba, 'frozen_predictions', return_value={}), \
                mock.patch.object(analysis, '_reduce', side_effect=before_reduce, return_value=([], [])) as reduce, \
                contextlib.redirect_stderr(io.StringIO()) as error:
            code = analysis.main(['--manifest', 'synthetic.json', '--export', 'NEVER_OPEN', '--stage', 'blinded',
                                  '--stage1-commit', commit or self.commit, '--predictions', str(self.predictions),
                                  '--out', str(self.repo / 'output')])
        return code, reduce, error.getvalue()

    def assert_refused_before_input(self, commit=None):
        code, reduce, error = self.invoke(commit)
        self.assertEqual(code, 1, error)
        reduce.assert_not_called()
        self.assertFalse((self.repo / 'output').exists())

    def amend(self):
        git(self.repo, 'add', '.')
        git(self.repo, 'commit', '--amend', '--no-edit', '-q')
        self.commit = git(self.repo, 'rev-parse', 'HEAD')
        git(self.repo, 'update-ref', 'refs/remotes/origin/synthetic', self.commit)
        record = json.loads(self.receipt.read_text())
        record.update(stage1_commit=self.commit, origin_tip=self.commit)
        self.receipt.write_text(json.dumps(record))

    def test_nonexistent_hex_commit_refuses_before_input(self):
        self.assert_refused_before_input('f' * 40)

    def test_blob_object_is_not_a_commit(self):
        blob = git(self.repo, 'rev-parse', 'HEAD:joulewise/bytes_analysis.py')
        self.assert_refused_before_input(blob)

    def test_annotated_tag_object_is_not_itself_a_commit(self):
        git(self.repo, 'tag', '-a', 'synthetic-tag', '-m', 'Synthetic tag')
        self.assert_refused_before_input(git(self.repo, 'rev-parse', 'refs/tags/synthetic-tag'))

    def test_local_only_commit_refuses_before_input(self):
        git(self.repo, 'update-ref', '-d', 'refs/remotes/origin/synthetic')
        self.assert_refused_before_input()

    def test_nonancestor_commit_refuses_before_input(self):
        git(self.repo, 'checkout', '--orphan', 'unrelated', '-q')
        git(self.repo, 'commit', '-qm', 'Unrelated analysis head', date='2026-11-02T10:00:00+00:00')
        self.assert_refused_before_input()

    def test_changed_prediction_blob_refuses_before_input(self):
        # The local JSON and sidecar agree, but no longer match the committed blob.
        import hashlib
        self.predictions.write_text('{"different": true}')
        self.predictions.with_suffix('.sha256').write_text(hashlib.sha256(self.predictions.read_bytes()).hexdigest())
        self.assert_refused_before_input()

    def test_missing_estimator_blob_refuses_before_input(self):
        (self.repo / 'joulewise/bytes_analysis.py').unlink()
        self.amend()
        self.assert_refused_before_input()

    def test_wrong_estimator_digest_refuses_before_input(self):
        (self.repo / 'joulewise/bytes_analysis.py').write_text('# synthetic changed estimator\n')
        self.amend()
        self.assert_refused_before_input()

    def test_commit_after_unblinding_refuses_before_input(self):
        self.journal.write_text(json.dumps({'event': 'heldout_rows', 'unblinded_utc': '2026-11-01T09:59:59+00:00',
                                          'stage1_commit': self.commit}) + '\n')
        self.assert_refused_before_input()

    def test_push_after_unblinding_refuses_before_input(self):
        self.journal.write_text(json.dumps({'event': 'heldout_rows', 'unblinded_utc': '2026-11-01T10:00:30+00:00',
                                          'stage1_commit': self.commit}) + '\n')
        self.assert_refused_before_input()

    def test_missing_push_time_refuses_before_input(self):
        record = json.loads(self.receipt.read_text())
        del record['pushed_utc']
        self.receipt.write_text(json.dumps(record))
        self.assert_refused_before_input()

    def test_valid_commit_records_push_time_and_unblinding_before_read(self):
        def before_reduce(*args, **kwargs):
            self.assertTrue(self.journal.read_text().strip(), 'admission must be journaled before input reads')
            return [], []
        code, reduce, error = self.invoke(before_reduce=before_reduce)
        self.assertEqual(code, 0, error)
        reduce.assert_called_once()
        record = json.loads((self.repo / 'output/analysis_record.json').read_text())['stage1_verification']
        self.assertEqual(record['stage1_commit'], self.commit)
        self.assertEqual(record['pushed_utc'], '2026-11-01T10:01:00+00:00')
        self.assertTrue(self.journal.read_text().strip())


    def test_bad_local_sidecar_refuses_before_input(self):
        self.predictions.with_suffix('.sha256').write_text('0' * 64)
        self.assert_refused_before_input()

    def test_missing_journal_refuses_before_input(self):
        self.journal.unlink()
        self.assert_refused_before_input()

    def test_malformed_journal_refuses_before_input(self):
        self.journal.write_text('{broken')
        self.assert_refused_before_input()

    def test_missing_receipt_refuses_before_input(self):
        self.receipt.unlink()
        self.assert_refused_before_input()

    def test_existing_journal_without_final_newline_remains_valid(self):
        self.journal.write_text(json.dumps({'event': 'heldout_rows', 'unblinded_utc': '2026-11-02T10:00:00+00:00'}))
        self.assertEqual(self.invoke()[0], 0)
        self.assertEqual(len([json.loads(line) for line in self.journal.read_text().splitlines()]), 2)

    def test_future_push_refuses_before_input(self):
        record = json.loads(self.receipt.read_text())
        record['pushed_utc'] = '2999-01-01T00:00:00+00:00'
        self.receipt.write_text(json.dumps(record))
        self.assert_refused_before_input()

    def test_deleted_historical_unblinding_record_is_still_checked(self):
        self.journal.write_text(json.dumps({'event': 'heldout_rows', 'unblinded_utc': '2026-11-01T09:00:00+00:00'}) + '\n')
        git(self.repo, 'add', 'docs/bytes/stage1/unblinding.jsonl')
        git(self.repo, 'commit', '-qm', 'Synthetic historical unblinding', date='2026-11-02T10:00:00+00:00')
        self.journal.write_text('')
        git(self.repo, 'add', 'docs/bytes/stage1/unblinding.jsonl')
        git(self.repo, 'commit', '-qm', 'Synthetic journal deletion', date='2026-11-03T10:00:00+00:00')
        self.assert_refused_before_input()

    def test_git_unblinding_record_at_commit_cannot_be_backdated_away(self):
        self.journal.write_text(json.dumps({'event': 'heldout_rows', 'unblinded_utc': '2026-11-02T10:00:00+00:00'}) + '\n')
        self.amend()
        self.assert_refused_before_input()

    def test_fit_release_metadata_does_not_count_as_heldout_unblinding(self):
        (self.receipt.parent / 'heldout-release.json').write_text(json.dumps({'stage': 'fit', 'released_utc': '2026-10-01T00:00:00+00:00'}))
        self.assertEqual(self.invoke()[0], 0)

    def test_heldout_release_metadata_is_checked(self):
        (self.receipt.parent / 'heldout-release.json').write_text(json.dumps({'stage': 'heldout', 'released_utc': '2026-10-01T00:00:00+00:00'}))
        self.assert_refused_before_input()

    def test_git_commit_timezone_is_normalized(self):
        git(self.repo, 'commit', '--amend', '--no-edit', '-q', date='2026-11-01T02:00:00-08:00')
        self.commit = git(self.repo, 'rev-parse', 'HEAD')
        git(self.repo, 'update-ref', 'refs/remotes/origin/synthetic', self.commit)
        record = json.loads(self.receipt.read_text())
        record.update(stage1_commit=self.commit, origin_tip=self.commit)
        self.receipt.write_text(json.dumps(record))
        self.assertEqual(self.invoke()[0], 0)


class EntrypointGateTests(unittest.TestCase):
    def test_all_heldout_entrypoints_refuse_fake_commit_before_source_reads(self):
        from scripts import bytes_twin, b6_release_subset, b6_unblind
        with tempfile.TemporaryDirectory(prefix='bytes-gate-entry-') as temp:
            root = Path(temp)
            calls = [
                (bytes_twin.main, ['--export', 'NEVER_OPEN', '--manifest', 'NEVER_OPEN', '--stage', '2',
                                  '--stage1-commit', 'f' * 40, '--out', str(root / 'twin')]),
                (b6_unblind.main, ['--export', 'NEVER_OPEN', '--key-dir', 'NEVER_OPEN',
                                  '--stage1-commit', 'f' * 40, '--out', str(root / 'unblind')]),
                (b6_release_subset.main, ['--pack-records-root', 'NEVER_OPEN', '--blinding-group', 'bytes',
                                         '--keys', 'NEVER_OPEN', '--stage', 'heldout',
                                         '--stage1-commit', 'f' * 40, '--out', str(root / 'release')]),
            ]
            for main, args in calls:
                with self.subTest(main=main.__module__), contextlib.redirect_stdout(io.StringIO()), \
                        contextlib.redirect_stderr(io.StringIO()), \
                        mock.patch.object(Path, 'open', side_effect=AssertionError('source opened before preflight')):
                    self.assertEqual(main(args), 1)
            self.assertEqual(list(root.iterdir()), [])

    def test_push_receipt_command_records_time_without_unblinding(self):
        from scripts import bytes_commitment as bc
        with tempfile.TemporaryDirectory(prefix='bytes-push-receipt-') as temp:
            repo, predictions, receipt, commit = commitment_fixture(temp)
            receipt.unlink()
            with contextlib.redirect_stdout(io.StringIO()):
                code = bc.main(['record-push', '--commitment-repo', str(repo), '--stage1-commit', commit,
                                '--predictions', str(predictions), '--origin-ref', 'refs/remotes/origin/synthetic',
                                '--pushed-utc', '2026-11-01T10:01:00+00:00'])
            self.assertEqual(code, 0)
            self.assertEqual(json.loads(receipt.read_text())['pushed_utc'], '2026-11-01T10:01:00+00:00')
            self.assertEqual((repo / 'docs/bytes/stage1/unblinding.jsonl').read_text(), '')


if __name__ == '__main__':
    unittest.main()
