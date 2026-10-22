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

    def test_generated_align_pack_identity_pins_use_real_mlx_projection(self) -> None:
        import tempfile
        from pathlib import Path
        from unittest.mock import patch
        from joulewise.align.apple.campaign import generate_campaign
        from joulewise.identity_pins import _runtime_probe_metadata, derive_model_runtime_config_from_metadata
        from joulewise.schemas import BenchmarkConfig
        from tests.align.test_apple_campaign import episode_spec
        import json

        def stream_generate(model, tokenizer, prompt, *, max_tokens, sampler):
            yield from ()  # projection never generates; retain the real native API signature

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            mirror = root / "model"
            mirror.mkdir()
            (mirror / "weights.safetensors").write_bytes(b"synthetic-local-weight")
            native = SimpleNamespace(
                __version__="synthetic-native", load=lambda *args, **kwargs: (object(), Tokenizer(), {}),
                stream_generate=stream_generate, make_sampler=lambda temp: object(),
            )
            base = base_config()
            base = replace(base, model=replace(base.model, source=str(mirror), revision="synthetic-pinned"),
                           hardware_target=replace(base.hardware_target, runtime_backend=RuntimeBackend.MLX))
            members = generate_campaign(
                base, (episode_spec(hidden=False), episode_spec(hidden=True)), root / "pack", model_tag="apple"
            )
            for member in members:
                config = BenchmarkConfig.from_mapping(json.loads(member.read_text()))
                # Inject only the native MLX library. Registry resolution,
                # prepare, wrapper forwarding and identity derivation are real.
                with patch.object(MlxRuntimeAdapter, "_import_mlx_lm", return_value=native), patch(
                    "joulewise.adapters.mlx_runtime._distribution_version", return_value="synthetic-native"
                ):
                    metadata = _runtime_probe_metadata(config)
                stack, pins = derive_model_runtime_config_from_metadata(config.to_dict(), metadata)
                self.assertEqual(stack["runtime_version"]["name"], "mlx")
                self.assertEqual(set(pins), {"model_artifact_sha256", "runtime_identity_sha256", "config_set_sha256"})
                self.assertTrue(all(len(value) == 64 and int(value, 16) >= 0 for value in pins.values()))

    def test_non_align_registry_resolution_does_not_import_alignment(self) -> None:
        import os
        import subprocess
        import sys
        from tests.align.test_apple_campaign import ROOT

        code = (
            "import sys; from joulewise.adapters import resolve_runtime; "
            "from joulewise.clock import FakeClock; "
            "from joulewise.schemas import BenchmarkConfig; import json; "
            "c=BenchmarkConfig.from_mapping(json.load(open('configs/examples/mock_local.json'))); "
            "r,f=resolve_runtime(c,FakeClock()); assert r is not None and f is None; "
            "assert not any(n.startswith('joulewise.align') for n in sys.modules)"
        )
        result = subprocess.run(
            [sys.executable, "-B", "-c", code], cwd=ROOT,
            env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"), text=True, capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
