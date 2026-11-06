"""ALIGN extensions preserve the core bytes and disabled-checkpoint runtime."""
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from joulewise.align.apple.endpoint import MlxEndpoint
from joulewise.align.apple.generation import generate_turn
from joulewise.align.apple.prompt_cache import EpisodePromptCache
from tests.align.test_pilot3_cache import CacheAPI, chat, fake_endpoint


class MeasurementCoreBoundaryTests(unittest.TestCase):
    def test_pilot9_measurement_core_is_unchanged(self):
        # SHA-256 of each complete file at pilot-9 c9a0a3943. No Git or
        # access to measurement data is needed to enforce this in shallow CI.
        expected = {
            'joulewise/schemas.py': '344b12ce178b8acb212059097a4ade507812a4be1673a6552ec221a83055e1d1',
            'joulewise/b5/driver.py': 'e1b3df745c82f4a4cec812ade3e4e7c1b460c6c4bec1f6970a3ef13736ab2e89',
            'joulewise/b5/harvest.py': '2aec65877b3a7e6da096171eb305833750932e2b5e0674eb835f408a0ad6c744',
            'joulewise/hazards/smc.py': 'c1896f0c4fd8510ab4a2273927d4d71d8cc7a1a6940928117ba50d8441f70351',
            'joulewise/hazards/monitor.py': '9ed83410fc2fe7bdbf8e8acffcf913af5bd4442bb23adc14ed61430e0a3c957b',
        }
        root = Path(__file__).resolve().parents[2]
        for name, digest in expected.items():
            with self.subTest(name=name):
                self.assertEqual(hashlib.sha256((root/name).read_bytes()).hexdigest(), digest)

    def test_mlx_core_is_byte_identical_to_pilot10(self):
        # Complete file at 83e2dac59, before #657/0ba413d40. Earlier ALIGN
        # extensions predate this package; no new rebind of file@c27485347.
        root = Path(__file__).resolve().parents[2]
        self.assertEqual(hashlib.sha256((root/'joulewise/adapters/mlx_runtime.py').read_bytes()).hexdigest(),
                         '953e6fec990c1d7e0702a8abb199a55f179e50d28854f4b62d0e95302dde0c45')

    def test_disabled_checkpoint_anchor_runtime_bytes_match_pilot10_path(self):
        def pilot10_generate(runtime, stream, *args, **kwargs):
            # Reproduce the old endpoint dispatch against the unchanged core.
            # This rebind is only the baseline fixture, never production code.
            with patch.object(runtime, '_mlx_lm', stream):
                return runtime._generate(*args, **kwargs)

        def episode(dispatch, limit, cache, sampled):
            api = CacheAPI()
            seeds = []
            core = SimpleNamespace(random=SimpleNamespace(seed=seeds.append))
            with patch('joulewise.align.apple.prompt_cache.native_cache_api', return_value=api), \
                 patch('joulewise.align.apple.endpoint.generate_turn', dispatch), \
                 patch('joulewise.adapters.mlx_runtime._resolve_mlx_core', return_value=core), \
                 patch.object(EpisodePromptCache, 'plan_checkpoint', side_effect=AssertionError('off')), \
                 patch.object(EpisodePromptCache, 'prefill_checkpoint', side_effect=AssertionError('off')):
                original, fed = fake_endpoint(api, cache=cache)
                original.runtime._mlx_lm.make_sampler = lambda **kwargs: kwargs
                endpoint = MlxEndpoint(original.runtime, original.config, original.clock,
                                       episode_domain='synthetic', hybrid_checkpoint_limit=limit,
                                       sampler={'temperature': 0.6, 'top_p': 0.95, 'top_k': 20, 'min_p': 0.0}
                                           if sampled else None,
                                       prompt_cache='episode_prefix' if cache else None)
                native = endpoint.runtime._mlx_lm
                ids = [1, 90, 3, 91, 4]
                results = []
                for _ in range(3):
                    results.append(asdict(chat(endpoint, ids)))
                    self.assertFalse(any(f.startswith('endpoint_error') for f in endpoint.flags), endpoint.flags)
                    self.assertIs(endpoint.runtime._mlx_lm, native)
                    ids += endpoint.turn_provenance[-1]['generation']['output_token_ids'] + [5]
                return json.dumps({'results': results, 'events': [asdict(e) for e in endpoint.events],
                                   'turns': endpoint.turn_provenance, 'identity': endpoint.identity,
                                   'flags': endpoint.flags, 'native_inputs': fed, 'seeds': seeds}, sort_keys=True).encode()

        for limit in (None, 0):
            for cache in (False, True):
                for sampled in (False, True):
                    with self.subTest(limit=limit, cache=cache, sampled=sampled):
                        self.assertEqual(episode(generate_turn, limit, cache, sampled),
                                         episode(pilot10_generate, limit, cache, sampled))

    def test_align_stream_does_not_rebind_the_prepared_runtime(self):
        api = CacheAPI()
        with patch('joulewise.align.apple.prompt_cache.native_cache_api', return_value=api):
            endpoint, _ = fake_endpoint(api)
            native = endpoint.runtime._mlx_lm
            stream_generate = native.stream_generate

            def observe(*args, **kwargs):
                self.assertIs(endpoint.runtime._mlx_lm, native)
                yield from stream_generate(*args, **kwargs)

            with patch.object(native, 'stream_generate', observe):
                chat(endpoint, [1, 2, 3])
            self.assertFalse(any(f.startswith('endpoint_error') for f in endpoint.flags), endpoint.flags)
