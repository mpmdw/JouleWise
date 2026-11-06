"""Exercise the real R0 MLX shim against fake native/cache/array APIs."""
import math
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from joulewise.align.r0_mlx import MlxBackend, ObservedNative
from tests.align.test_r0_checks import FakeGuard


class Array:
    def __init__(self, data):
        self.data = data
    def astype(self, kind):
        return self
    def __getitem__(self, key):
        return self
    def squeeze(self, axis):
        return self
    def __sub__(self, other):
        return Array([a - b for a, b in zip(self.data, other.data)])
    def item(self):
        return self.data
    def tolist(self):
        return list(self.data)


class FakeCore:
    float32 = "float32"
    def __init__(self):
        self.eval_calls = []
    array = staticmethod(Array)
    def eval(self, *args):
        self.eval_calls.append(args)
    def clear_cache(self):
        pass
    def synchronize(self):
        pass
    @staticmethod
    def logsumexp(logits, axis):
        return Array([math.log(sum(math.exp(v) for v in row)) for row in logits.data])
    @staticmethod
    def take_along_axis(logits, targets, axis):
        return Array([row[target] for row, target in zip(logits.data, targets.data[0])])
    @staticmethod
    def sum(values):
        return Array(sum(values.data))


class ShimTest(unittest.TestCase):
    def test_constructor_builds_valid_config_and_checks_pins_without_real_models(self):
        mx = FakeCore()
        runtime = SimpleNamespace(_model=SimpleNamespace(parameters=lambda: []), _mlx_lm=SimpleNamespace(),
                                  _tokenizer=SimpleNamespace(),
                                  prepare=lambda config: SimpleNamespace(ok=True, metadata={}),
                                  cleanup=lambda config: None)
        class Endpoint:
            def __init__(self, *args, chat_template_kwargs=None, **kwargs):
                self.template_kwargs = chat_template_kwargs
            def assistant_history_message(self, result):
                return result
        versions = {"mlx": "0.31.2", "mlx-lm": "0.31.3", "transformers": "5.12.1"}
        with tempfile.TemporaryDirectory() as tmp, \
                patch("joulewise.align.apple.endpoint.MlxEndpoint", Endpoint), \
                patch("joulewise.adapters.mlx_runtime.MlxRuntimeAdapter", return_value=runtime), \
                patch("joulewise.align.shade.upstream.PinnedUpstream") as upstream, \
                patch("importlib.metadata.version", side_effect=versions.__getitem__), \
                patch.dict("sys.modules", {"mlx": SimpleNamespace(core=mx), "mlx.core": mx}):
            backend = MlxBackend("D", tmp, str(Path(tmp) / "shade"), FakeGuard())
            self.assertEqual(backend.config.model.context_window, 40960)
            self.assertIsNone(backend.endpoint.template_kwargs)
            backend.new_session("medium")
            self.assertEqual(backend.endpoint.template_kwargs, {"reasoning_effort": "medium"})
            upstream.assert_called_once_with(cache_dir=str(Path(tmp) / "shade"), allow_fetch=False)
            backend.close()

    def test_teacher_forcing_across_chunk_boundaries_uses_next_token_targets(self):
        backend = MlxBackend.__new__(MlxBackend)
        backend.mx, backend.guard = FakeCore(), FakeGuard()
        seen = []
        cache = [SimpleNamespace(state=[])]
        def model(array, *, cache):
            seen.extend(array.data[0])
            # Given 0, next token is 1 with probability 3/4; vice versa.
            return Array([[0, math.log(3)] if token == 0 else [math.log(3), 0]
                          for token in array.data[0]])
        backend.runtime = SimpleNamespace(_model=model)
        with patch.dict("sys.modules", {"mlx_lm": SimpleNamespace(), "mlx_lm.models": SimpleNamespace(),
                                        "mlx_lm.models.cache": SimpleNamespace(make_prompt_cache=lambda model: cache)}):
            ids = [i % 2 for i in range(259)]
            nll = backend.nll(ids)
        self.assertAlmostEqual(nll, -math.log(0.75))
        self.assertEqual(seen, ids[:-1])
        self.assertEqual(len(backend.mx.eval_calls), 3)

    def test_nll_losses_are_per_target_and_nll_is_their_mean(self):
        backend = MlxBackend.__new__(MlxBackend)
        backend.mx, backend.guard = FakeCore(), FakeGuard()
        cache = [SimpleNamespace(state=[])]
        backend.runtime = SimpleNamespace(_model=lambda array, *, cache: Array(
            [[0, math.log(3)] if token == 0 else [math.log(3), 0] for token in array.data[0]]))
        with patch.dict("sys.modules", {"mlx_lm": SimpleNamespace(), "mlx_lm.models": SimpleNamespace(),
                                        "mlx_lm.models.cache": SimpleNamespace(make_prompt_cache=lambda model: cache)}):
            ids = [0, 1, 1] + [i % 2 for i in range(256)]
            losses = backend.nll_losses(ids)
            mean = backend.nll(ids)
        self.assertEqual(len(losses), len(ids) - 1)
        self.assertAlmostEqual(losses[1], -math.log(0.25))  # 1 -> 1 is the unlikely transition
        self.assertAlmostEqual(mean, sum(losses) / len(losses))

    def test_greedy_session_has_no_sampler_and_chat_mode_must_match(self):
        seen = []
        class Endpoint:
            def __init__(self, *args, sampler=None, **kwargs):
                self.sampler = sampler
            def chat(self, messages, **kwargs):
                seen.append(kwargs)
                return SimpleNamespace(raw_usage={"joulewise": {"flags": []}})
        backend = MlxBackend.__new__(MlxBackend)
        backend.guard, backend.tag = FakeGuard(), "D"
        backend.runtime = backend.config = backend.clock = backend.prepared = None
        with patch("joulewise.align.apple.endpoint.MlxEndpoint", Endpoint):
            backend.new_session(None, greedy=True)
            self.assertIsNone(backend.endpoint.sampler)
            with self.assertRaises(RuntimeError):
                backend.chat([], [], 16, 1)
            backend.chat([], [], 16, None, greedy=True)
            self.assertEqual((seen[-1]["temperature"], seen[-1]["seed"]), (0.0, None))
            backend.new_session(None)
            self.assertEqual(backend.endpoint.sampler["temperature"], 1.0)
            with self.assertRaises(RuntimeError):
                backend.chat([], [], 16, None, greedy=True)

    def test_fixed_context_uses_episode_cache_exact_positions_and_absent_metadata(self):
        backend = MlxBackend.__new__(MlxBackend)
        backend.mx, backend.guard = FakeCore(), FakeGuard()
        backend.mx.get_active_memory = lambda: 123
        backend.mx.get_peak_memory = lambda: 456
        backend.new_session = Mock()
        backend.encode = lambda text: [1, 2, 3]
        backend.native = SimpleNamespace(observe=None)
        native_cache = [SimpleNamespace(lengths=None, left_padding=None)]
        cache = Mock()
        cache.cache = native_cache
        cache.prepare.side_effect = lambda ids: (ids, {})
        calls = []
        def generate(delta, prompt, text, output_size, *, suppress_eos, stream_options):
            calls.append((len(prompt), output_size, suppress_eos, stream_options))
            for i in range(output_size):
                backend.native.observe(i + 1)
            return SimpleNamespace(output_tokens=output_size, output_token_ids=[1] * output_size)
        backend.runtime = SimpleNamespace(_model="fake-model", _generate=generate)
        with patch("joulewise.align.apple.prompt_cache.EpisodePromptCache", return_value=cache):
            result = backend.long_decode(eval_metadata=True)
        self.assertEqual(calls, [(2048, 38912, True, {"prompt_cache": native_cache})])
        self.assertEqual(result["positions"], 40960)
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["memory_samples"][-1]["position"], 40960)
        self.assertEqual(backend.mx.eval_calls, [])
        self.assertEqual(result["metadata_arrays_evaluated"], 0)
        self.assertEqual(result["metadata_evaluation"], "metadata_absent_single_stream")
        cache.finish.assert_called_once()

    def test_close_uses_config_argument_of_pinned_runtime(self):
        backend = MlxBackend.__new__(MlxBackend)
        backend.config = "config"
        calls = []
        backend.runtime = SimpleNamespace(cleanup=lambda config: calls.append(config))
        backend.mx = FakeCore()
        backend.close()
        self.assertEqual(calls, ["config"])

    def test_stream_observer_checks_guard_and_preserves_response(self):
        responses = [SimpleNamespace(token=1), SimpleNamespace(token=2)]
        native = SimpleNamespace(stream_generate=lambda *args, **kwargs: iter(responses))
        guard = FakeGuard()
        wrapped = ObservedNative(native, guard)
        counts = []
        wrapped.observe = counts.append
        self.assertEqual(list(wrapped.stream_generate("model")), responses)
        self.assertEqual(counts, [1, 2])
        self.assertEqual(len(guard.receipts), 2)


if __name__ == "__main__":
    unittest.main()
