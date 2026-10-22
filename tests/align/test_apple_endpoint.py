"""The MLX endpoint uses the existing stream-generation path without extras."""

from __future__ import annotations

import math
import unittest
from dataclasses import replace
from types import SimpleNamespace

from joulewise.adapters.mlx_runtime import MlxRuntimeAdapter
from joulewise.align.apple.endpoint import MlxEndpoint, parse_completion
from joulewise.align.interfaces import ChatEndpoint, ChatMessage
from joulewise.clock import FakeClock
from joulewise.schemas import RuntimeBackend
from tests.align.test_apple_campaign import base_config


class Tokenizer:
    eos_token_ids = {0}

    def apply_chat_template(self, messages, *, tools, tokenize, add_generation_prompt):
        self.template_arguments = (messages, tools, tokenize, add_generation_prompt)
        return "A rendered local chat prompt."

    def encode(self, text, *, add_special_tokens):
        return list(range(2048))


class AppleEndpointTests(unittest.TestCase):
    def test_real_mlx_generation_helper_with_a_synthetic_stream(self) -> None:
        clock = FakeClock()
        runtime = MlxRuntimeAdapter(clock)
        runtime._model = object()
        runtime._tokenizer = Tokenizer()

        def stream_generate(model, tokenizer, prompt, *, max_tokens, sampler):
            # D-019 production-shaped prompt and decode timings. This replaces
            # only native computation, exercising the real _generate markers,
            # sampler selection, detokenization and token accounting.
            clock.sleep(2048 * 0.001)
            for token in range(max_tokens):
                clock.sleep(0.010)
                yield SimpleNamespace(token=token, text="x", finish_reason=None)

        runtime._mlx_lm = SimpleNamespace(
            stream_generate=stream_generate, make_sampler=lambda temp: object()
        )
        config = base_config()
        config = replace(config, hardware_target=replace(
            config.hardware_target, runtime_backend=RuntimeBackend.MLX
        ))
        endpoint = MlxEndpoint(
            runtime, config, clock, episode_domain="synthetic.monotonic",
            prepare_metadata={"mlx_version": "synthetic", "mlx_lm_version": "synthetic"},
        )
        self.assertIsInstance(endpoint, ChatEndpoint)
        result = endpoint.chat(
            [ChatMessage("user", "Reconcile the ledger.")],
            tools=(), max_tokens=512, temperature=0.0, seed=19,
        )
        self.assertEqual(result.prompt_tokens, 2048)
        self.assertEqual(result.completion_tokens, 512)
        self.assertEqual(len(endpoint.prompt_token_ids), 2048)
        self.assertFalse(any(flag.startswith("endpoint_error:") for flag in endpoint.flags), endpoint.flags)
        self.assertTrue(any(event.phase == "prefill" for event in endpoint.events))
        self.assertTrue(any(event.phase == "decode" for event in endpoint.events))
        # No physical uncertainty is assigned to D-019's synthetic constants;
        # compare its closed-form interval at the required 1e-6 relative bar.
        self.assertTrue(math.isclose(
            (result.end_ns - result.start_ns) / 1e9, 2048 * 0.001 + 512 * 0.010,
            rel_tol=1e-6,
        ))
        self.assertIsNotNone(result.first_token_ns)
        self.assertIn('"mlx_version": "synthetic"', endpoint.identity)

    def test_malformed_tool_envelope_is_retained_and_flagged(self) -> None:
        text = "Visible answer. <tool_call>{broken}</tool_call>"
        content, reasoning, calls, flags = parse_completion(text)
        self.assertEqual(content, text)
        self.assertEqual(calls, ())
        self.assertTrue(any(flag.startswith("malformed_tool_call:") for flag in flags))
