"""Failing-first CLI witnesses and local-Git commitment checks; synthetic only."""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from scripts import bytes_analyze as analysis
from scripts import bytes_commitment as bc
from tests.bytes_commitment_support import commitment_fixture, git, activity_json, ORIGIN_REF, REMOTE_REF


class CommitmentGateTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix='bytes-commitment-')
        self.addCleanup(temp.cleanup)
        self.repo, self.predictions, self.receipt, self.commit = commitment_fixture(temp.name)
        self.journal = self.receipt.parent / 'unblinding.jsonl'
        patcher = mock.patch.object(bc, 'ROOT', self.repo)
        patcher.start()
        self.addCleanup(patcher.stop)

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
        git(self.repo, 'update-ref', ORIGIN_REF, self.commit)
        record = json.loads(self.receipt.read_text())
        record.update(stage1_commit=self.commit, origin_tip=self.commit, github_activity_raw=activity_json(self.commit))
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
        git(self.repo, 'update-ref', '-d', ORIGIN_REF)
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
        self.journal.write_text(json.dumps({'event': 'heldout_rows', 'unblinded_utc': '2026-11-02T10:00:00+00:00',
                                          'stage1_commit': self.commit}))
        git(self.repo, 'add', 'docs/bytes/stage1/unblinding.jsonl')
        git(self.repo, 'commit', '-qm', 'Synthetic committed admission', date='2026-11-03T10:00:00+00:00')
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
        git(self.repo, 'update-ref', ORIGIN_REF, self.commit)
        record = json.loads(self.receipt.read_text())
        record.update(stage1_commit=self.commit, origin_tip=self.commit, github_activity_raw=activity_json(self.commit))
        self.receipt.write_text(json.dumps(record))
        self.assertEqual(self.invoke()[0], 0)

    def test_backdated_prediction_commit_cannot_replace_admitted_commit(self):
        # P1: C1 admitted at 12:00, journal intact but uncommitted. C2 is made
        # afterwards, backdated to 10:30, with an attested 10:31 push.
        self.journal.write_text(json.dumps({'event': 'heldout_rows', 'stage1_commit': self.commit,
                                          'unblinded_utc': '2026-11-01T12:00:00+00:00'}) + '\n')
        import hashlib
        self.predictions.write_text(json.dumps({'bytes_analysis_sha256': bc.ESTIMATORS['joulewise/bytes_analysis.py'],
                                                'synthetic': 'C2'}))
        self.predictions.with_suffix('.sha256').write_text(hashlib.sha256(self.predictions.read_bytes()).hexdigest())
        git(self.repo, 'add', 'docs/bytes/stage1/predictions.json', 'docs/bytes/stage1/predictions.sha256')
        git(self.repo, 'commit', '-qm', 'Backdated synthetic C2', date='2026-11-01T10:30:00+00:00')
        replacement = git(self.repo, 'rev-parse', 'HEAD')
        git(self.repo, 'update-ref', ORIGIN_REF, replacement)
        record = json.loads(self.receipt.read_text())
        activity = json.loads(activity_json(replacement))
        activity[0]['timestamp'] = '2026-11-01T10:31:00+00:00'
        record.update(stage1_commit=replacement, origin_tip=replacement,
                      pushed_utc=activity[0]['timestamp'], github_activity_raw=json.dumps(activity))
        self.receipt.write_text(json.dumps(record))
        with self.assertRaisesRegex(ValueError, 'another stage1_commit'):
            bc.verify_commitment(replacement, repo=self.repo)

    def test_every_journal_event_requires_its_stage1_commit(self):
        for event in ('heldout_rows', 'heldout_keys', 'heldout_analysis'):
            with self.subTest(event=event):
                self.journal.write_text(json.dumps({'event': event, 'unblinded_utc': '2026-11-02T12:00:00+00:00'}))
                with self.assertRaises((KeyError, ValueError)):
                    bc.verify_commitment(self.commit, repo=self.repo)

    def test_admission_requires_committing_each_previous_journal_line(self):
        from types import SimpleNamespace
        args = SimpleNamespace(stage1_commit=self.commit, commitment_repo=self.repo, stage1_receipt=self.receipt)
        with contextlib.redirect_stderr(io.StringIO()) as error:
            bc.admit(args, 'heldout_rows')
        prior = self.journal.read_bytes()
        with self.assertRaisesRegex(ValueError, 'commit and push'):
            bc.admit(args, 'heldout_keys')
        self.assertEqual(self.journal.read_bytes(), prior)
        git(self.repo, 'add', 'docs/bytes/stage1/unblinding.jsonl')
        git(self.repo, 'commit', '-qm', 'Synthetic first admission')
        self.journal.write_bytes(b'')  # P4: truncation of a committed journal must also refuse.
        with self.assertRaisesRegex(ValueError, 'commit and push'):
            bc.admit(args, 'heldout_keys')
        self.journal.write_bytes(prior)
        with contextlib.redirect_stderr(io.StringIO()):
            bc.admit(args, 'heldout_keys')
        self.assertEqual(len(self.journal.read_text().splitlines()), 2)
        self.assertIn('commit and push', error.getvalue())

    def test_foreign_commitment_checkout_is_refused_even_when_valid(self):
        other = self.repo.parent / 'other'
        other.mkdir()
        repo, predictions, receipt, commit = commitment_fixture(other)
        with self.assertRaisesRegex(ValueError, 'running checkout'):
            bc.verify_commitment(commit, predictions, repo=repo, receipt=receipt)

    def test_record_push_rejects_forged_origin_and_invalid_server_events(self):
        import subprocess
        self.receipt.unlink()
        good = json.loads(activity_json(self.commit))[0]
        cases = [('missing remote', 1, '', good), ('stale remote', 0, 'f' * 40, good),
                 ('wrong ref', 0, self.commit, {**good, 'ref': 'refs/heads/other'}),
                 ('wrong after', 0, self.commit, {**good, 'after': 'f' * 40}),
                 ('force activity', 0, self.commit, {**good, 'activity_type': 'force_push'}),
                 ('force flag', 0, self.commit, {**good, 'force_push': True}),
                 ('missing timestamp', 0, self.commit, {k: v for k, v in good.items() if k != 'timestamp'})]
        for label, rc, remote, event in cases:
            with self.subTest(case=label):
                self.receipt.unlink(missing_ok=True)
                def runner(command, **kwargs):
                    raw = remote + '\t' + REMOTE_REF + '\n' if command[0] == 'git' else json.dumps([event])
                    return subprocess.CompletedProcess(command, rc if command[0] == 'git' else 0, raw.encode())
                with contextlib.redirect_stdout(io.StringIO()) as out:
                    code = bc.main(['record-push', '--stage1-commit', self.commit], runner=runner)
                self.assertEqual(code, 1, out.getvalue())
                self.assertIn('BYTES commitment', out.getvalue())
                self.assertFalse(self.receipt.exists())
                self.assertEqual(git(self.repo, 'rev-parse', 'HEAD'), self.commit)

    def test_check_and_admit_do_not_use_network_runner(self):
        runner = mock.Mock(side_effect=AssertionError('offline gate attempted network'))
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(bc.main(['check', '--stage1-commit', self.commit], runner=runner), 0)
            self.assertEqual(bc.main(['admit', '--stage1-commit', self.commit, '--event', 'heldout_rows'], runner=runner), 0)
        runner.assert_not_called()

    def test_record_push_refuses_no_remote_despite_forged_tracking_ref(self):
        git(self.repo, 'remote', 'remove', 'origin')
        git(self.repo, 'update-ref', ORIGIN_REF, self.commit)
        self.receipt.unlink()
        runner = mock.Mock(side_effect=AssertionError('missing remote must refuse locally'))
        with contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(bc.main(['record-push', '--stage1-commit', self.commit], runner=runner), 1)
        self.assertIn('BYTES commitment', out.getvalue())
        runner.assert_not_called()
        self.assertFalse(self.receipt.exists())


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
                with self.subTest(main=main.__module__), contextlib.redirect_stdout(io.StringIO()) as out, \
                        contextlib.redirect_stderr(io.StringIO()) as err, \
                        mock.patch.object(Path, 'open', side_effect=AssertionError('source opened before preflight')) as opened:
                    self.assertEqual(main(args), 1)
                    self.assertIn('BYTES commitment', out.getvalue() + err.getvalue())
                    opened.assert_not_called()
            self.assertEqual(list(root.iterdir()), [])

    def test_push_receipt_command_records_time_without_unblinding(self):
        from scripts import bytes_commitment as bc
        with tempfile.TemporaryDirectory(prefix='bytes-push-receipt-') as temp:
            repo, predictions, receipt, commit = commitment_fixture(temp)
            receipt.unlink()
            # GitHub represents normal pushes via activity_type; force_push is
            # a separate activity type, rather than a required boolean field.
            activity = json.loads(activity_json(commit))
            del activity[0]['force_push']
            raw = json.dumps(activity, indent=2) + '\n'
            (repo / 'unrelated.txt').write_text('synthetic staged work\n')
            git(repo, 'add', 'unrelated.txt')
            def runner(command, **kwargs):
                import subprocess
                if command == ['git', 'ls-remote', 'origin', REMOTE_REF]:
                    return subprocess.CompletedProcess(command, 0, (commit + '\t' + REMOTE_REF + '\n').encode())
                self.assertEqual(command, ['gh', 'api', 'repos/synthetic/bytes/activity?ref=' + REMOTE_REF + '&activity_type=push&per_page=100'])
                return subprocess.CompletedProcess(command, 0, raw.encode())
            with mock.patch.object(bc, 'ROOT', repo), contextlib.redirect_stdout(io.StringIO()):
                code = bc.main(['record-push', '--commitment-repo', str(repo), '--stage1-commit', commit,
                                '--predictions', str(predictions)], runner=runner)
            self.assertEqual(code, 0)
            self.assertEqual(json.loads(receipt.read_text())['pushed_utc'], '2026-11-01T10:01:00+00:00')
            self.assertEqual(json.loads(receipt.read_text())['github_activity_raw'], raw)
            self.assertIs(json.loads(receipt.read_text())['force_push'], False)
            self.assertEqual(git(repo, 'show', 'HEAD:docs/bytes/stage1/push-receipt.json'), receipt.read_text().strip())
            self.assertEqual(git(repo, 'diff', '--cached', '--name-only'), 'unrelated.txt')
            self.assertEqual(git(repo, 'diff-tree', '--no-commit-id', '--name-only', '-r', 'HEAD'),
                             'docs/bytes/stage1/push-receipt.json')
            self.assertEqual((repo / 'docs/bytes/stage1/unblinding.jsonl').read_text(), '')


if __name__ == '__main__':
    unittest.main()
