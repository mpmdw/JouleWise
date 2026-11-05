"""PR 659 regressions; native computation is replaced by synthetic streams."""
from dataclasses import replace
import json
from types import SimpleNamespace
import unittest

from joulewise.adapters.mlx_runtime import MlxRuntimeAdapter
from joulewise.align.apple.endpoint import MlxEndpoint, parse_completion
from joulewise.align.apple.xml_tool_calls import XML_MODEL_FAMILIES
from joulewise.align.interfaces import ChatMessage
from joulewise.clock import FakeClock
from joulewise.schemas import RuntimeBackend
from tests.align.test_apple_campaign import base_config
from tests.align.test_xml_tool_calls import TOOLS, xml


class ByteTokenizer:
    eos_token_ids = {0}

    def encode(self, text, **kwargs):
        return list(text.encode())

    def apply_chat_template(self, messages, **kwargs):
        return "synthetic prompt<think>\n"


def endpoint(family="qwen3_8", text="", finish_reason="length", **kwargs):
    clock = FakeClock()
    runtime = MlxRuntimeAdapter(clock)
    runtime._model, runtime._tokenizer = object(), ByteTokenizer()

    def stream_generate(*args, **options):
        for character in text:
            clock.sleep(.001)
            yield SimpleNamespace(token=ord(character), text=character, finish_reason=None)
        yield SimpleNamespace(token=0, text="", finish_reason=finish_reason)

    runtime._mlx_lm = SimpleNamespace(stream_generate=stream_generate, make_sampler=lambda temp: object())
    config = base_config()
    config = replace(config, model=replace(config.model, family=family),
                     hardware_target=replace(config.hardware_target, runtime_backend=RuntimeBackend.MLX))
    return MlxEndpoint(runtime, config, clock, episode_domain="synthetic", **kwargs)


class XmlFixRoundTests(unittest.TestCase):
    def test_unverified_122b_template_is_explicitly_unsupported(self):
        for family in ("qwen3_5_moe", "qwen3_5_moe_text", "qwen3.5_moe"):
            with self.subTest(family=family):
                self.assertNotIn(family, XML_MODEL_FAMILIES)
                with self.assertRaisesRegex(ValueError, "unverified_xml_template"):
                    endpoint(family)
                with self.assertRaisesRegex(ValueError, "unverified_xml_template"):
                    endpoint("qwen3.8", prepare_metadata={"model_config_name": family})

    def test_dotted_families_select_xml_and_split_history(self):
        for family in ("qwen3.5", "qwen3.8"):
            with self.subTest(family=family):
                ep = endpoint(family, "plan</think>" + xml(), "stop",
                              prepare_metadata={"model_config_name": "qwen3_5"})
                result = ep.chat([ChatMessage("user", "x")], tools=TOOLS,
                                 max_tokens=1024, temperature=0, seed=None)
                self.assertEqual(len(result.tool_calls), 1)
                self.assertEqual(ep.assistant_history_message(result).content, "")
                self.assertEqual(len(parse_completion(xml(), model_family=family, tools=TOOLS)[2]), 1)

    def test_artifact_family_mismatch_is_refused_before_generation(self):
        for family, artifact in (("qwen3_next", "qwen3_5"), (None, "qwen3_5"),
                                 ("qwen3.8", "qwen3_next"), ("qwen3_5", "qwen3_moe")):
            with self.subTest(family=family, artifact=artifact):
                with self.assertRaisesRegex(ValueError, "model_family_artifact_mismatch"):
                    endpoint(family, prepare_metadata={"model_config_name": artifact})

    def test_length_cut_keeps_prefilled_thought_private_and_never_executes_draft(self):
        for family, call in (("qwen3_8", xml()), ("qwen3_next", '<tool_call>{"name":"update","arguments":{"text":"hello"}}</tool_call>')):
            for tail in ("", "<think>\nStill deciding"):
                with self.subTest(family=family, tail=tail):
                    text = "Draft action:\n" + call + "\n" + tail
                    ep = endpoint(family, text)
                    result = ep.chat([ChatMessage("user", "x")], tools=TOOLS,
                                     max_tokens=1024, temperature=0, seed=None)
                    self.assertEqual(result.tool_calls, ())
                    self.assertEqual(result.content, "")
                    self.assertEqual(result.reasoning_text, text)
                    self.assertIn("reasoning_censored_at_token_limit", ep.flags)
                    self.assertFalse(any(f.startswith("endpoint_error:") for f in ep.flags), ep.flags)
