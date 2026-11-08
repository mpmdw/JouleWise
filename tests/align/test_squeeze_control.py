import sys
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import patch

from joulewise.align.squeeze.config import seal
from joulewise.align.squeeze.control import ControlEndpoint, HiddenDecode, MlxDecoder
from tests.align.squeeze_fixtures import TinyDecoder, VirtualClock, control_config, variant


class ControlTests(unittest.TestCase):
    def control(self, k=5, decoder=None, call=0):
        clock = VirtualClock()
        decoder = decoder or TinyDecoder(clock)
        return HiddenDecode(control_config(k, call), decoder, clock=clock,
                            clock_domain="synthetic"), decoder

    def test_exact_forwards_and_independent_prompt_accounting(self):
        control, decoder = self.control()
        control.execute()
        receipt = control.receipt()
        self.assertEqual(receipt["status"], "completed")
        self.assertEqual(receipt["completed_tokens"], 5)
        self.assertEqual(receipt["H"], 5)
        self.assertEqual(len(receipt["output_token_ids"]), 5)
        self.assertEqual(receipt["prefill_tokens"], 3)
        self.assertEqual(receipt["incremental_decode_forwards"], 4)
        self.assertEqual(receipt["completed_forward_input_tokens"], 7)
        self.assertEqual(len(decoder.forward_inputs), 5)
        self.assertEqual(decoder.forward_inputs[0], (1, 2, 3))
        self.assertTrue(all(len(ids) == 1 for ids in decoder.forward_inputs[1:]))
        self.assertEqual(receipt["end_ns"] - receipt["start_ns"], 50)
        self.assertFalse(receipt["unknown_work_on_failure"])
        receipt["output_token_ids"].clear()
        self.assertEqual(control.receipt()["completed_tokens"], 5)
        with self.assertRaises(RuntimeError):
            control.execute()

    def test_zero_sham_does_no_prefill_or_decode(self):
        control, decoder = self.control(k=0)
        control.execute()
        receipt = control.receipt()
        self.assertEqual(receipt["status"], "completed")
        self.assertEqual(receipt["H"], 0)
        self.assertEqual(decoder.forward_inputs, [])
        for key in ("completed_tokens", "prefill_tokens", "incremental_decode_forwards",
                    "completed_forward_input_tokens"):
            self.assertEqual(receipt[key], 0)

    def test_short_and_interrupted_decodes_never_certify_requested_dose(self):
        for exception in (None, RuntimeError, KeyboardInterrupt, SystemExit):
            class Broken(TinyDecoder):
                def decode(self, prompt, *, max_tokens):
                    yield 7
                    if exception:
                        raise exception()

            control, _ = self.control(decoder=Broken())
            with self.subTest(exception=exception), self.assertRaises(BaseException):
                control.execute()
            receipt = control.receipt()
            self.assertIn(receipt["status"], ("failed", "interrupted"))
            self.assertEqual(receipt["completed_tokens"], 1)
            self.assertEqual(receipt["output_token_ids"], [7])
            self.assertTrue(receipt["unknown_work_on_failure"])
            self.assertIsNone(receipt["H"])

    def test_invalid_token_and_cleanup_failure_invalidate_receipt(self):
        for bad in (True, -1, 8, "3"):
            class Invalid(TinyDecoder):
                def decode(self, prompt, *, max_tokens):
                    yield bad

            control, _ = self.control(decoder=Invalid())
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                control.execute()
            self.assertEqual(control.receipt()["status"], "failed")
            self.assertEqual(control.receipt()["completed_tokens"], 0)

        class CleanupError(TinyDecoder):
            def decode(self, prompt, *, max_tokens):
                try:
                    for _ in range(max_tokens):
                        yield 1
                finally:
                    raise RuntimeError("cleanup")

        control, _ = self.control(decoder=CleanupError())
        with self.assertRaisesRegex(RuntimeError, "cleanup"):
            control.execute()
        self.assertEqual(control.receipt()["status"], "failed")

    def test_invalid_native_limits_and_vocab_refused_before_compute(self):
        for changes in ({"vocab_size": 3}, {"vocab_size": True},
                        {"max_context_tokens": 32}, {"identity": ""}):
            decoder = TinyDecoder()
            decoder.__dict__.update(changes)
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                self.control(decoder=decoder)
            self.assertEqual(decoder.forward_inputs, [])

    def test_endpoint_preserves_visible_result_and_hides_receipt(self):
        class Endpoint:
            identity = "visible-synthetic"
            events = []
            result = object()

            def chat(self, messages, **kwargs):
                self.seen = messages, kwargs
                return self.result

        control, decoder = self.control(call=1)
        endpoint = Endpoint()
        wrapped = ControlEndpoint(endpoint, variant_sha256=variant()["config_sha256"], control=control)
        messages = [{"role": "user", "content": "main task"}]
        kwargs = dict(tools=(), max_tokens=10, temperature=0.0, seed=42)
        for index in range(3):
            self.assertIs(wrapped.chat(messages, **kwargs), endpoint.result)
            self.assertIs(endpoint.seen[0], messages)
            self.assertEqual(endpoint.seen[1], kwargs)
            self.assertEqual(len(decoder.forward_inputs), 0 if index == 0 else 5)
        self.assertIs(wrapped.events, endpoint.events)
        self.assertNotIn("test-control", wrapped.identity)
        self.assertNotIn("hidden_decode", endpoint.seen[1])

    def test_not_reached_and_variant_control_model_identities(self):
        class Endpoint:
            identity = "visible-synthetic"

        control, _ = self.control(call=2)
        self.assertEqual(control.receipt()["status"], "not_triggered")
        identities = set()
        for name, k in (("unaware", 0), ("meter-aware", 0), ("meter-aware", 1)):
            config = seal({**control_config(k), "id": "different-control"})
            other = HiddenDecode(config, TinyDecoder(), clock_domain="synthetic")
            identities.add(ControlEndpoint(Endpoint(), variant_sha256=variant(name)["config_sha256"],
                                           control=other).identity)
        self.assertEqual(len(identities), 3)
        decoder = TinyDecoder()
        decoder.identity = "different-synthetic-model"
        other_control = HiddenDecode(control.config, decoder, clock_domain="synthetic")
        self.assertNotEqual(
            ControlEndpoint(Endpoint(), variant_sha256=variant()["config_sha256"], control=control).identity,
            ControlEndpoint(Endpoint(), variant_sha256=variant()["config_sha256"], control=other_control).identity)

    def test_control_config_cannot_be_mutated_after_validation(self):
        control, _ = self.control(k=5)
        exposed = control.config
        exposed["decode_tokens"] = 100
        exposed["prompt_token_ids"].clear()
        control.execute()
        self.assertEqual(control.receipt()["H"], 5)
        self.assertEqual(control.receipt()["prefill_tokens"], 3)

    def test_system_exit_from_control_uses_runner_interruption_path(self):
        class Exiting(TinyDecoder):
            def decode(self, prompt, *, max_tokens):
                yield 1
                raise SystemExit(23)

        control, _ = self.control(decoder=Exiting())
        endpoint = SimpleNamespace(identity="synthetic-visible")
        wrapped = ControlEndpoint(endpoint, variant_sha256=variant()["config_sha256"],
                                  control=control)
        # The pinned runner catches KeyboardInterrupt and stops samplers, but
        # SystemExit would escape before sampler.stop() and lose its run receipt.
        with self.assertRaises(KeyboardInterrupt):
            wrapped.chat([], max_tokens=5, temperature=0.0, seed=1)
        receipt = control.receipt()
        self.assertEqual(receipt["status"], "interrupted")
        self.assertEqual(receipt["error_type"], "SystemExit")
        self.assertEqual(receipt["completed_tokens"], 1)
        self.assertIsNone(receipt["H"])

    def test_mlx_evaluation_includes_independent_cache_arrays(self):
        # Interface-level spy only: no MLX import, kernels or native evidence.
        # These independent cache leaves need not be dependencies of argmax.
        class Array:
            nbytes = 4

            def __init__(self, shape=(1, 3)):
                self.shape = shape

            def __getitem__(self, key):
                return self

            def item(self):
                return 1

        class Cache:
            state = (Array(),)

            def __init__(self):
                self.auxiliary = Array()

        layer = Cache()
        evaluated = []
        forward_lengths = []
        token = Array((1,))

        def model(inputs, *, cache):
            forward_lengths.append(inputs.shape[1])
            return Array((1, inputs.shape[1], 8))

        mx = ModuleType("mlx.core")
        mx.array = lambda rows, **kwargs: Array((1, len(rows[0])))
        mx.int32 = object()
        mx.argmax = lambda *args, **kwargs: token
        mx.eval = lambda *arrays: evaluated.append(arrays)
        mlx = ModuleType("mlx")
        mlx.core = mx
        decoder = MlxDecoder(model, cache_factory=lambda: [layer], identity="spy-only",
                             vocab_size=8, max_context_tokens=64)
        with patch.dict(sys.modules, {"mlx": mlx, "mlx.core": mx}):
            control, _ = self.control(k=1, decoder=decoder)
            control.execute()
        self.assertEqual(forward_lengths, [3])
        self.assertEqual(len(evaluated), 1)
        self.assertIn(token, evaluated[0])
        self.assertIn(layer.state[0], evaluated[0])
        self.assertIn(layer.auxiliary, evaluated[0])


if __name__ == "__main__":
    unittest.main()
