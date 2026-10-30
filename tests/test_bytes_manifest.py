"""Hand-computed synthetic safetensors and fake MLX/cache arithmetic only."""
import contextlib
from copy import deepcopy
import io
import json
from pathlib import Path
import struct
import tempfile
from types import SimpleNamespace
import sys
import unittest
from unittest import mock

from scripts import bytes_manifest as b


def safetensors(path, tensors):
    header, offset = {}, 0
    for name, (dtype, shape) in tensors.items():
        size = b.DTYPE_BYTES[dtype]
        for dimension in shape:
            size *= dimension
        header[name] = {"dtype": dtype, "shape": shape, "data_offsets": [offset, offset + size]}
        offset += size
    raw = json.dumps(header).encode()
    path.write_bytes(struct.pack('<Q', len(raw)) + raw + bytes(offset))


class HeaderTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'Qwen3-4B-4bit'
        self.root.mkdir()
        (self.root / 'tokenizer.json').write_text('{}')

    def fixture(self, family='qwen3', tied=False, prefix='model.', moe=False, hybrid=False, shared=False):
        cfg = {'model_type': family, 'vocab_size': 4, 'tie_word_embeddings': tied,
               '_commit_hash': 'synthetic-revision'}
        if moe:
            cfg.update(num_experts=4, num_experts_per_tok=1)
        if shared:
            cfg['shared_expert_intermediate_size'] = 8
        # Embed: 4*2*4 + 4*1*2 + 4*1*2 = 48 bytes; row = 12.
        tensors = {prefix + 'embed_tokens.weight': ('U32', [4, 2]),
                   prefix + 'embed_tokens.scales': ('F16', [4, 1]),
                   prefix + 'embed_tokens.biases': ('BF16', [4, 1]),
                   prefix + 'norm.weight': ('F32', [2]),  # 8
                   prefix + 'layers.0.self_attn.q_proj.weight': ('U32', [2, 2]),  # 16
                   prefix + 'layers.0.self_attn.q_proj.scales': ('F16', [2, 1]),  # 4
                   prefix + 'layers.0.self_attn.q_proj.biases': ('F16', [2, 1])}  # 4
        if not tied:
            tensors['lm_head.weight'] = ('U32', [4, 2])  # 32+8+8 = 48
            tensors['lm_head.scales'] = ('F16', [4, 1])
            tensors['lm_head.biases'] = ('F16', [4, 1])
        if moe:
            # 4 expert weights: 128+32+32 =192 stored; k/E ->48.
            stem = prefix + 'layers.0.mlp.switch_mlp.up_proj.'
            tensors.update({stem + 'weight': ('U32', [4, 4, 2]),
                            stem + 'scales': ('F16', [4, 4, 1]),
                            stem + 'biases': ('F16', [4, 4, 1])})
        if hybrid:
            tensors[prefix + 'layers.1.linear_attn.in_proj_qkvz.weight'] = ('U32', [2, 2])  #16
            tensors[prefix + 'layers.1.linear_attn.A_log'] = ('F32', [2])  #8
            tensors[prefix + 'layers.1.linear_attn.dt_bias'] = ('F32', [2])  #8
            tensors[prefix + 'layers.1.linear_attn.conv1d.weight'] = ('F16', [2, 2])  #8
        if shared:
            tensors[prefix + 'layers.0.mlp.shared_expert.up_proj.weight'] = ('U32', [2, 2])  #16
            tensors[prefix + 'layers.0.mlp.shared_expert.up_proj.scales'] = ('F16', [2, 1])  #4
            tensors[prefix + 'layers.0.mlp.shared_expert.up_proj.biases'] = ('F16', [2, 1])  #4
            tensors[prefix + 'layers.0.mlp.shared_expert_gate.weight'] = ('F32', [2])  #8 always active
        # Qwen3.5 uses a nested text_config.
        if family == 'qwen3_5_moe_text':
            cfg = {'model_type': 'qwen3_5_moe', 'text_config': cfg}
        (self.root / 'config.json').write_text(json.dumps(cfg))
        safetensors(self.root / 'model.safetensors', tensors)
        return tensors

    def test_dense_qwen_and_llama_with_quantization_storage_and_tying(self):
        for family, tied, expected_w, expected_r in (
                ('qwen3', False, 92, 128), ('llama', True, 92, 80)):
            with self.subTest(family=family):
                self.fixture(family, tied)
                row = b.headers(self.root)
                # always=32; row=12; output=48. R excludes duplicate tied head.
                self.assertEqual(row['W_bytes'], expected_w)
                self.assertEqual(row['R_bytes'], expected_r)
                self.assertEqual(row['tied_embeddings'], tied)

    def test_qwen3_moe_expert_fraction(self):
        self.fixture('qwen3_moe', moe=True)
        row = b.headers(self.root)
        self.assertEqual(row['categories']['routed_experts'], 192)
        self.assertEqual(row['routed_fraction'], 0.25)
        self.assertEqual((row['W_bytes'], row['R_bytes']), (140, 320))

    def test_qwen_next_shared_experts_and_linear_attention(self):
        self.fixture('qwen3_next', moe=True, hybrid=True, shared=True)
        row = b.headers(self.root)
        # W=92+48 routed+40 recurrent weights+24 shared+8 shared gate.
        self.assertEqual((row['W_bytes'], row['R_bytes']), (212, 392))
        self.assertEqual(row['shared_experts']['stored_bytes'], 24)

    def test_qwen35_nested_text_config_and_language_model_names(self):
        self.fixture('qwen3_5_moe_text', prefix='language_model.model.', moe=True, hybrid=True, shared=True)
        row = b.headers(self.root)
        self.assertEqual((row['W_bytes'], row['R_bytes']), (212, 392))
        self.assertEqual(row['experts_per_tok'], 1)

    def test_unsanitized_multimodal_text_prefix_is_supported(self):
        self.fixture('qwen3_5_moe_text', prefix='model.language_model.', moe=True, hybrid=True, shared=True)
        self.assertEqual((b.headers(self.root)['W_bytes'], b.headers(self.root)['R_bytes']), (212, 392))

    def test_sanitize_dropped_tensors_are_recorded_but_never_loaded(self):
        tensors = self.fixture('qwen3_5_moe_text', prefix='model.language_model.',
                               moe=True, hybrid=True, shared=True)
        baseline = b.headers(self.root)
        dropped = ('vision_tower.blocks.0.attn.qkv.weight',
                   'model.visual.blocks.0.attn.qkv.weight',
                   'mtp.layers.0.weight', 'model.mtp.layers.0.weight',
                   'model.language_model.mtp.layers.0.weight')
        for name in dropped:
            tensors[name] = ('BF16', [2, 3])
        safetensors(self.root / 'model.safetensors', tensors)
        row = b.headers(self.root)
        self.assertEqual(row['categories']['not_loaded'], 12 * len(dropped))
        self.assertEqual((row['W_bytes'], row['R_bytes']), (212, 392))
        self.assertEqual((row['W_bytes'], row['R_bytes']),
                         (baseline['W_bytes'], baseline['R_bytes']))
        for name in dropped:
            self.assertEqual(row['tensors'][name]['category'], 'not_loaded')
            self.assertEqual(row['tensors'][name]['stored_bytes'], 12)

    def test_sanitize_namespace_near_misses_still_refuse(self):
        for name in ('model.visualizer.weight', 'vision_tower_extra.weight',
                     'model.vision_tower.weight', 'model.notmtp.weight',
                     'model.mtp_extra.weight', 'model.mtp', 'visual.blocks.0.weight'):
            with self.subTest(name=name):
                with self.assertRaisesRegex(ValueError, 'unclassified tensor'):
                    b.classify(name)

    def test_individual_expert_names_shards_and_index(self):
        tensors = self.fixture('qwen3_moe', moe=True)
        tensors = {k: v for k, v in tensors.items() if '.switch_mlp.' not in k}
        for i in range(4):
            tensors[f'model.layers.0.mlp.experts.{i}.up_proj.weight'] = ('U32', [4, 2])
            tensors[f'model.layers.0.mlp.experts.{i}.up_proj.scales'] = ('F16', [4, 1])
            tensors[f'model.layers.0.mlp.experts.{i}.up_proj.biases'] = ('F16', [4, 1])
        (self.root / 'model.safetensors').unlink()
        names = list(tensors)
        first = {n: tensors[n] for n in names[:5]}
        last = {n: tensors[n] for n in names[5:]}
        safetensors(self.root / 'a.safetensors', first)
        safetensors(self.root / 'b.safetensors', last)
        (self.root / 'model.safetensors.index.json').write_text(json.dumps({'weight_map': {
            **dict.fromkeys(first, 'a.safetensors'), **dict.fromkeys(last, 'b.safetensors')}}))
        self.assertEqual((b.headers(self.root)['W_bytes'], b.headers(self.root)['R_bytes']), (140, 320))

    def test_unknown_tensor_and_bad_expert_or_tied_metadata_fail(self):
        tensors = self.fixture()
        tensors['model.layers.0.surprise.weight'] = ('F16', [2])
        safetensors(self.root / 'model.safetensors', tensors)
        with self.assertRaisesRegex(ValueError, 'unclassified tensor'):
            b.headers(self.root)
        self.fixture('qwen3_moe', moe=True)
        cfg = json.loads((self.root / 'config.json').read_bytes())
        cfg['num_experts_per_tok'] = 5
        (self.root / 'config.json').write_text(json.dumps(cfg))
        with self.assertRaisesRegex(ValueError, 'valid k/E'):
            b.headers(self.root)
        self.fixture()
        cfg = json.loads((self.root / 'config.json').read_bytes())
        cfg['tie_word_embeddings'] = True
        (self.root / 'config.json').write_text(json.dumps(cfg))
        with self.assertRaisesRegex(ValueError, 'tie_word_embeddings'):
            b.headers(self.root)

    def test_bad_span_truncation_duplicates_and_dtype_fail(self):
        self.fixture()
        path = self.root / 'model.safetensors'
        raw = path.read_bytes()
        path.write_bytes(raw[:-1])
        with self.assertRaisesRegex(ValueError, 'stored span'):
            b.headers(self.root)
        path.write_bytes(raw)
        (self.root / 'duplicate.safetensors').write_bytes(raw)
        with self.assertRaisesRegex(ValueError, 'duplicate tensor'):
            b.headers(self.root)
        (self.root / 'duplicate.safetensors').unlink()
        header = {'model.norm.weight': {'dtype': 'UNKNOWN', 'shape': [1], 'data_offsets': [0, 1]}}
        encoded = json.dumps(header).encode()
        path.write_bytes(struct.pack('<Q', len(encoded)) + encoded + b'0')
        with self.assertRaisesRegex(ValueError, 'dtype/shape'):
            b.headers(self.root)

    def test_headers_cli_and_merge_compare_weight_column_not_kv(self):
        self.fixture()
        out = self.root / 'headers.json'
        self.assertEqual(b.main(['headers', '--model-dir', str(self.root), '--out', str(out)]), 0)
        h = json.loads(out.read_bytes())
        k = {key: h[key] for key in ('model_dir', 'revision', 'tokenizer', 'config_sha256')}
        k['KV_bytes'] = 20
        result, delta = b.merge([h], [k], [{'repo': 'mlx-community/Qwen3-4B-4bit', 'read_meas_GB': 80 / 1e9}])
        self.assertEqual(result['models'][0]['b_bytes'], 112)
        self.assertAlmostEqual(delta[0]['W_minus_pilot_bytes'], 12)
        kpath, pilot, merged = (self.root / n for n in ('kv.json', 'pilot.json', 'merged.json'))
        b.write_json(kpath, k)
        b.write_json(pilot, [])
        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            b.main(['merge', '--headers', str(out), '--kv', str(kpath), '--pilot', str(pilot), '--out', str(merged)])
        self.assertIsNone(json.loads(stdout.getvalue())['W_minus_pilot_bytes'])
        self.assertEqual(json.loads(merged.read_bytes())['models'][0]['b_bytes'], 112)
        bad = deepcopy(k)
        bad['revision'] = 'other'
        with self.assertRaisesRegex(ValueError, 'identity mismatch'):
            b.merge([h], [bad], [])
        with self.assertRaisesRegex(ValueError, 'duplicate KV'):
            b.merge([h], [k, k], [])

    def test_manifest_config_key_comes_from_registered_identity(self):
        self.fixture()
        header = b.headers(self.root)
        cache = {key: header[key] for key in ('model_dir', 'revision', 'tokenizer', 'config_sha256')}
        cache['KV_bytes'] = 20
        # A deliberately different workload proves the key is read, not guessed
        # from the model name or a duplicated workload/token constant.
        project = self.root / 'registered-project'
        configs = project / 'modules/model'
        configs.mkdir(parents=True)
        config = {'model': {'name': 'Qwen3-4B-4bit'},
                  'workload_profile': {'name': 'registered-workload', 'output_tokens': 777}}
        (configs / 'run.json').write_text(json.dumps(config))
        registration = project / 'configs/b6/packs/synthetic/registration.json'
        registration.parent.mkdir(parents=True)
        registration.write_text(json.dumps({'blinding_group': 'bytes',
            'modules': [{'config_dirs': ['modules/model']}]}))
        baseline, _ = b.merge([header], [cache], [])
        with mock.patch.object(b, 'ROOT', project):
            result, _ = b.merge([header], [cache], [])
        self.assertEqual(result['models'][0]['config_key'], 'Qwen3-4B-4bit|registered-workload|777')
        old = baseline['models'][0].copy()
        new = result['models'][0].copy()
        old.pop('config_key')
        new.pop('config_key')
        # Identical records through identical arithmetic; every other field stays exact.
        self.assertEqual(new, old)


class Array:
    def __init__(self, shape, itemsize=2):
        self.shape = shape
        self.nbytes = itemsize
        for n in shape:
            self.nbytes *= n

    def __getitem__(self, key):
        return self


class KVCache:
    def __init__(self, length, capacity):
        self.offset = length
        self.keys = Array((1, 2, capacity, 4))
        self.values = Array((1, 2, capacity, 4))

    @property
    def state(self):
        return (Array((1, 2, self.offset, 4)), Array((1, 2, self.offset, 4)))


class ArraysCache:
    state = [Array((1, 2, 3)), {'recurrent': Array((1, 2, 2), 4)}]  #12+16=28 constant


class KVTests(unittest.TestCase):
    def test_snapshot_counts_occupied_and_backing_separately(self):
        start = b.cache_snapshot([KVCache(2048, 2304), ArraysCache()])
        end = b.cache_snapshot([KVCache(2560, 2560), ArraysCache()])
        record = b.kv_record(start, end)
        # KV is 32 bytes/context token and recurrent state stays at 28 bytes.
        self.assertEqual(record['decode_forward_passes'], 512)
        self.assertEqual(record['KV_bytes'], (2048 * 32 + 28 + 2560 * 32 + 28) / 2)
        self.assertEqual(start['layers'][0]['allocated_bytes'], 2304 * 32)
        self.assertEqual(end['layers'][0]['occupied_length'], 2560)
        self.assertEqual(end['layers'][0]['allocated_capacity'], 2560)
        self.assertEqual(end['layers'][1]['cache_class'], 'ArraysCache')
        self.assertIsNone(end['layers'][1]['allocated_capacity'])
        with self.assertRaisesRegex(ValueError, 'layer count'):
            b.kv_record(start, {'layers': []})

    def test_explicit_generation_has_exactly_512_decode_forwards(self):
        calls = []
        def model(prompt, cache):
            n = 2048 if not calls else 1
            calls.append(n)
            cache[0].offset += n
            return Array((1, n, 4))
        mx = SimpleNamespace(argmax=lambda *a, **k: Array((1,)), eval=lambda *a: None)
        start, end = b.generate_cache(model, Array((2048,)), mx, lambda model: [KVCache(0, 2560)])
        self.assertEqual(calls, [2048] + [1] * 512)
        self.assertEqual(start['layers'][0]['occupied_length'], 2048)
        self.assertEqual(end['layers'][0]['occupied_length'], 2560)

    def test_mac_kv_orchestration_with_fake_mlx_and_tokenizer(self):
        from joulewise.adapters import mlx_runtime
        fake_mx = SimpleNamespace(array=lambda ids: Array((len(ids),)), eval=lambda *a: None)
        model = SimpleNamespace(parameters=lambda: [])
        tokenizer = object()
        modules = {'mlx': SimpleNamespace(core=fake_mx), 'mlx.core': fake_mx,
                   'mlx_lm': SimpleNamespace(load=lambda path: (model, tokenizer)),
                   'mlx_lm.models': SimpleNamespace(),
                   'mlx_lm.models.cache': SimpleNamespace(make_prompt_cache=lambda model: [])}
        warm = b.cache_snapshot([KVCache(2048, 2304)])
        end = b.cache_snapshot([KVCache(2560, 2560)])
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            (directory / 'config.json').write_text('{"model_type":"qwen3"}')
            with mock.patch.object(b.platform, 'system', return_value='Darwin'), \
                 mock.patch.dict(sys.modules, modules), \
                 mock.patch.object(mlx_runtime, '_synthetic_prompt_tokens', return_value=[0] * 2048) as prompt, \
                 mock.patch.object(b, 'generate_cache', side_effect=[(warm, warm), (warm, end)]) as generate, \
                 mock.patch('time.sleep') as settle:
                row = b.kv(directory, revision='fake-revision')
            prompt.assert_called_once_with(tokenizer, 2048)
            self.assertEqual(generate.call_args_list[0].kwargs, {'output_tokens': 4})
            self.assertEqual(generate.call_count, 2)
            settle.assert_called_once_with(5.0)
            self.assertEqual(row['KV_bytes'], (2048 + 2560) * 16)
            self.assertEqual(row['revision'], 'fake-revision')

    def test_linux_kv_gate_does_not_import_mlx(self):
        with mock.patch.object(b.platform, 'system', return_value='Linux'):
            with self.assertRaisesRegex(RuntimeError, 'requires Mac MLX'):
                b.kv(Path('/synthetic/absent'))


class FrozenManifestTests(unittest.TestCase):
    def test_frozen_manifest_reproduces_and_validates_analysis_models(self):
        from joulewise.bytes_analysis import validate_manifest
        root = Path(__file__).resolve().parents[1]
        records = root / 'configs/bytes/records'
        result, _ = b.merge([json.loads(p.read_bytes()) for p in sorted(records.glob('*.headers.json'))],
                            [json.loads(p.read_bytes()) for p in sorted(records.glob('*.kv.json'))],
                            json.loads((root / 'docs/design/bytes_pilot/summary_rows.json').read_bytes()))
        raw = (json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + '\n').encode()
        self.assertEqual((root / 'configs/bytes/bytes_manifest.json').read_bytes(), raw)
        validate_manifest({**result, 'sessions': []})
        from joulewise.b5.harvest import build_roster, l4_exclusion_inputs
        families = {c['cell_id'] for pack in (root / 'configs/campaigns').glob('bytes-s*-p1')
                    for c in l4_exclusion_inputs(build_roster(pack, root), {}, plan_id=None, attempt=None)[0]['cells']}
        self.assertEqual({cell for m in result['models'] for cell in m['cell_ids']}, families)


class ExtensionReceiptTests(unittest.TestCase):
    def test_exact_committed_headers(self):
        from fractions import Fraction
        root = Path(__file__).resolve().parents[1]
        receipts = root / 'configs/campaigns/bytes_v1/extension/receipts'
        dump = json.loads((receipts / 'qwen38-27b-8bit-safetensors-headers.json').read_bytes())
        config = (receipts / 'qwen38-27b-8bit-config.json').read_bytes()
        totals = dict.fromkeys(('embed', 'lm_head', 'always_active', 'routed_experts', 'shared_experts', 'not_loaded'), 0)
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp) / 'Qwen3.8-27B-8bit'
            directory.mkdir()
            (directory / 'config.json').write_bytes(config)
            for shard, header in dump.items():
                raw = json.dumps(header).encode()
                end = 0
                for name, item in header.items():
                    if name == '__metadata__':
                        continue
                    # Independent census: this dense checkpoint has only these namespaces.
                    cat = ('not_loaded' if name.startswith('vision_tower.') else
                           'embed' if '.embed_tokens.' in name else
                           'lm_head' if '.lm_head.' in name else 'always_active')
                    totals[cat] += item['data_offsets'][1] - item['data_offsets'][0]
                    end = max(end, item['data_offsets'][1])
                with (directory / shard).open('wb') as stream:
                    stream.write(struct.pack('<Q', len(raw)) + raw)
                    stream.truncate(8 + len(raw) + end)  # sparse; no tensor body read
            row = b.headers(directory, '815b83c0df8ffd1d1b5244cf75fd6ef14fca9ef9')
            self.assertEqual(row['categories'], totals)
            vocab = json.loads(config)['text_config']['vocab_size']
            w = totals['always_active'] + totals['lm_head'] + Fraction(totals['embed'], vocab)
            self.assertEqual(w.denominator, 1)
            self.assertEqual(row['W_bytes'], int(w))
            self.assertEqual(row['R_bytes'], sum(totals.values()) - totals['not_loaded'])
            self.assertEqual(b.analysis_fields(row), {'model': 'Qwen3.8-27B-8bit',
                'role': 'extension_held_out', 'moe': False, 'tier': False,
                'cell_ids': ['bytes-qwen38-27b-8bit-decode']})
            self.assertTrue(b.registered_config_key('Qwen3.8-27B-8bit'))

    def test_registered_manifest_remerges_byte_identically(self):
        root = Path(__file__).resolve().parents[1]
        path = root / 'configs/bytes/bytes_manifest.json'
        original = json.loads(path.read_bytes())
        pilot = json.loads((root / 'docs/design/bytes_pilot/summary_rows.json').read_bytes())
        headers = [{k: v for k, v in row.items() if k not in
                    {'model', 'role', 'moe', 'tier', 'cell_ids', 'config_key', 'kv', 'KV_bytes',
                     'b_bytes', 'W_GB', 'KV_GB', 'b_GB', 'R_GB', 'pilot_difference'}} for row in original['models']]
        result, _ = b.merge(headers, [row['kv'] for row in original['models']], pilot)
        self.assertEqual(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + '\n', path.read_text())
