"""Public-model policy on synthetic trees; HF transport/census are injected."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock

SPEC = importlib.util.spec_from_file_location('public_guard', Path(__file__).resolve().parents[1] / 'scripts/align_offload_delete_root.py')
g = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(g)


class PublicWeightsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.models = self.root / 'jw_models'
        self.src = self.models / 'Qwen9-99B-4bit'
        self.src.mkdir(parents=True)
        (self.src / 'weights.safetensors').write_bytes(b'public synthetic weights')
        self.other = self.root / 'other-KEEP'
        self.other.mkdir()
        self.op = self.root / 'operation'
        self.item = self.op / 'unused-model'
        self.item.mkdir(parents=True)
        self.keep = self.op / 'KEEP.txt'
        self.keep.write_text(str(self.models) + '\n' + str(self.other) + '\n')
        self.journal = self.op / 'deletions.tsv'
        self.addCleanup(mock.patch.stopall)
        mock.patch.object(g, 'MODEL_ROOTS', (self.models,)).start()
        mock.patch.object(g, 'MANDATORY_KEEP', (self.models, self.other)).start()
        self.acl = mock.patch.object(g, 'check_acl_flags').start()
        self.pause = mock.patch.object(g, 'check_pause_and_disk').start()
        self.replay = mock.patch.object(g, 'replay_census').start()
        self.head = mock.patch.object(g, 'check_hf_downloadable', return_value={'method': 'HEAD'}).start()
        self.upload = mock.patch.object(g, 'check_uploaded').start()
        self.census = {'schema': 'joulewise.offload.model-census.v2', 'paths': ['/text/other-model'],
                       'model_ids': ['Qwen3.8-27B', 'Qwen3-30B-A3B', 'Qwen2.5-1.5B']}
        self.prepare()

    def prepare(self):
        rows = g.encoded(g.tree(self.src))
        for name in ('source.json', 'source-after.json'):
            (self.item / name).write_bytes(rows)
        sha = hashlib.sha256(rows).hexdigest()
        (self.item / 'source.sha256').write_text(sha + '  ' + str(self.item / 'source.json') + '\n')
        (self.item / 'source-path.txt').write_text(str(self.src) + '\n')
        (self.item / 'model-census.json').write_text(json.dumps(self.census))
        csha = g.sha_file(self.item / 'model-census.json')
        self.claim = dict(source=str(self.src), repo_id='synthetic/Qwen9-99B-4bit', revision='a' * 40,
                          manifest_sha256=sha, census_sha256=csha,
                          files={r[0]: r[0] for r in json.loads(rows) if r[1] == 'file'})
        (self.item / 'public-weights.json').write_text(json.dumps(self.claim))
        (self.item / 'ed-approval.json').write_text(json.dumps({'approver': 'Ed', 'approved': [self.claim]}))
        (self.item / 'independent-receipt.txt').write_text('\n'.join(
            (str(self.src), sha, csha, self.claim['repo_id'], self.claim['revision'])))
        (self.item / 'retention-review.json').write_text(json.dumps(dict(
            source=str(self.src), manifest_sha256=sha, model_class='public-weights',
            no_retained_ledger_locators=True, no_measurement_data=True)))

    def delete(self):
        return g.delete_root(self.item, self.keep, None, self.journal, 'public-weights')

    def refused(self, reason):
        with mock.patch.object(g.shutil, 'rmtree') as rm:
            with self.assertRaisesRegex(Exception, reason):
                self.delete()
            rm.assert_not_called()
        self.assertTrue(self.src.exists())

    def test_approved_unreferenced_exact_path_needs_no_cloud_copy(self):
        expected_bytes = (self.src / 'weights.safetensors').stat().st_size
        result = self.delete()
        self.assertFalse(self.src.exists())
        self.assertTrue(self.models.exists())
        self.assertTrue(self.other.exists())
        self.assertEqual(result['source_regular_bytes'], expected_bytes)
        self.assertIsInstance(result['available_bytes_delta'], int)
        self.assertIn('\tDELETED\t', self.journal.read_text())
        self.assertEqual(self.replay.call_count, 2)
        self.head.assert_called_once()
        self.upload.assert_not_called()
        self.acl.assert_called()
        self.pause.assert_called_once()
        pointer = json.loads(self.src.with_name(self.src.name + '.OFFLOADED.json').read_text())
        self.assertEqual(pointer['model_class'], 'public-weights')
        self.assertEqual(pointer['revision'], 'a' * 40)

    def test_mandatory_root_itself_and_another_path_cannot_use_approval(self):
        self.src = self.models
        self.prepare()
        self.refused('strict model-root descendant')
        self.src = self.models / 'another'
        self.src.mkdir()
        (self.src / 'weights.safetensors').write_bytes(b'x')
        (self.item / 'source-path.txt').write_text(str(self.src) + '\n')
        self.refused('exact source/manifest')

    def test_other_keep_entries_are_never_relaxed(self):
        for entry in (self.src, self.src / 'weights.safetensors', self.root):
            self.keep.write_text(str(self.models) + '\n' + str(self.other) + '\n' + str(entry) + '\n')
            self.refused('KEEP inode overlap')

    def test_referenced_by_any_census_path_or_model_alias_refuses(self):
        for paths, ids in (([str(self.src)], []), ([str(self.models)], []),
                           ([str(self.src / 'weights.safetensors')], []),
                           ([], ['Qwen9-99B']), ([], ['Qwen9-99B-4bit'])):
            self.census.update(paths=paths, model_ids=ids)
            self.prepare()
            self.refused('referenced by census')

    def test_unreplayable_or_changed_census_refuses(self):
        self.replay.side_effect = g.Refusal('model census replay mismatch')
        self.refused('census replay')
        self.replay.side_effect = None
        (self.item / 'model-census.json').write_text('{}')
        self.refused('census digest')

    def test_dropped_align_models_stay_keep_when_bytes_references_them(self):
        for name in ('Qwen3-Next-80B-A3B-Instruct-4bit', 'Qwen3.5-122B-A10B-4bit'):
            with self.subTest(model=name), self.assertRaisesRegex(g.Refusal, 'census identity'):
                g.unreferenced(self.models / name, 'mlx-community/' + name,
                               {'paths': [], 'model_ids': [name]})

    def test_missing_or_changed_specific_ed_approval_refuses(self):
        p = self.item / 'ed-approval.json'
        for value in ({'approver': 'someone', 'approved': [self.claim]},
                      {'approver': 'Ed', 'approved': [{**self.claim, 'revision': 'b' * 40}]},
                      {'approver': 'Ed', 'approved': [self.claim, self.claim]}):
            p.write_text(json.dumps(value))
            self.refused('specific public-model list')
        p.unlink()
        self.refused('No such file')

    def test_bad_repo_revision_manifest_or_file_bytes_refuse(self):
        p = self.item / 'public-weights.json'
        for key, value in (('revision', 'main'), ('repo_id', '../escape'), ('manifest_sha256', '0' * 64)):
            p.write_text(json.dumps({**self.claim, key: value}))
            self.refused('required|mismatch')
        p.write_text(json.dumps(self.claim))
        (self.src / 'weights.safetensors').write_bytes(b'changed')
        self.refused('predelete source mismatch')

    def test_symlinks_hardlinks_captures_and_acl_failures_still_refuse(self):
        link = self.src / 'snapshot-link'
        link.symlink_to('/must-not-follow')
        self.prepare()
        self.refused('blobs, not symlinks')
        link.unlink()
        os.link(self.src / 'weights.safetensors', link)
        self.refused('hardlink')
        link.unlink()
        captures = self.src / 'instrument_validation'
        captures.mkdir()
        self.prepare()
        self.refused('capture retention')
        captures.rmdir()
        self.prepare()
        self.acl.side_effect = g.Refusal('protected flag')
        self.refused('protected flag')

    def test_hf_unavailable_or_source_changed_at_fresh_head_refuses(self):
        self.head.side_effect = g.Refusal('HF unavailable')
        self.refused('HF unavailable')
        self.head.side_effect = lambda *args: (self.src / 'weights.safetensors').write_bytes(b'changed')
        self.refused('source changed before delete')


class HFHeadTests(unittest.TestCase):
    def test_census_replay_rejects_modified_receipts_or_lane_pins(self):
        roles = ('main', 'bytes', 'b6', 'align-v4', 'amendment-1', 'r0-v4')
        refs = dict.fromkeys(roles, 'a' * 40)
        census = dict(schema='joulewise.offload.model-census.v2', reviewed_refs=refs,
                      r0_config='docs/align/r0.json', paths=['/text/Qwen3-8B'],
                      model_ids=['Qwen3-8B'], inputs=[dict(role='main', ref='main',
                          commit='a' * 40, input='configs/identity_pins.json', sha256='b' * 64)])
        helper = {'ROLES': roles, 'commit': lambda *args: 'a' * 40,
                  'derive': lambda *args: json.loads(json.dumps(census))}
        with mock.patch.object(g.runpy, 'run_path', return_value=helper):
            g.replay_census(census)
            changed = json.loads(json.dumps(census))
            changed['paths'] = []
            with self.assertRaisesRegex(g.Refusal, 'replay mismatch'):
                g.replay_census(changed)
            changed['reviewed_refs']['bytes'] = 'c' * 40
            with self.assertRaisesRegex(g.Refusal, 'lane pins'):
                g.replay_census(changed)

    def test_api_and_each_blob_head_at_full_revision_without_auth(self):
        claim = dict(repo_id='synthetic/Qwen9-99B-4bit', revision='a' * 40,
                     files={'blobs/123': 'weights.safetensors'})
        rows = [['blobs/123', 'file', 0o644, 1, '0' * 64]]
        with mock.patch.object(g, 'urlopen') as request:
            request.return_value.__enter__.return_value.status = 200
            result = g.check_hf_downloadable(claim, rows)
            self.assertEqual(result['files_checked'], 1)
            self.assertEqual(request.call_count, 2)
            for call in request.call_args_list:
                req = call.args[0]
                self.assertEqual(req.get_method(), 'HEAD')
                self.assertIn('a' * 40, req.full_url)
                self.assertFalse(req.has_header('Authorization'))
            self.assertIn('/api/models/', request.call_args_list[0].args[0].full_url)
            request.return_value.__enter__.return_value.status = 403
            with self.assertRaisesRegex(g.Refusal, 'unavailable'):
                g.check_hf_downloadable(claim, rows)

    def test_missing_file_mapping_or_snapshot_link_refuses_before_network(self):
        claim = dict(repo_id='synthetic/Test', revision='a' * 40, files={})
        for rows in ([['weights', 'file', 0o644, 1, '0' * 64]], [['link', 'link', 0o777, 'target']]):
            with mock.patch.object(g, 'urlopen') as request, self.assertRaises(g.Refusal):
                g.check_hf_downloadable(claim, rows)
            request.assert_not_called()


if __name__ == '__main__':
    unittest.main()
