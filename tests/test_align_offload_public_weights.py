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
    def test_public_only_deletion_is_retired_before_any_source_read(self):
        with tempfile.TemporaryDirectory() as d:
            op = Path(d).resolve()
            item = op / 'model'
            item.mkdir()
            with mock.patch.object(g.shutil, 'rmtree') as rm, \
                 mock.patch.object(g, 'check_hf_downloadable') as network:
                with self.assertRaisesRegex(g.Refusal, 'all deletions require SSD'):
                    g.delete_root(item, op / 'KEEP.txt', None, op / 'deletions.tsv', 'public-weights')
                rm.assert_not_called()
                network.assert_not_called()
            self.assertIn('REFUSED_NO_DELETE', (op / 'deletions.tsv').read_text())

    def test_dropped_align_models_stay_keep_when_bytes_references_them(self):
        for name in ('Qwen3-Next-80B-A3B-Instruct-4bit', 'Qwen3.5-122B-A10B-4bit'):
            with self.subTest(model=name), self.assertRaisesRegex(g.Refusal, 'census identity'):
                g.unreferenced(Path('/synthetic') / name, 'mlx-community/' + name,
                               {'paths': [], 'model_ids': [name]})


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
