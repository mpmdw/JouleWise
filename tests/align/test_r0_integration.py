"""Synthetic production/R0 history parity; no native runtime or study data."""
from dataclasses import replace
import json
from types import SimpleNamespace
import unittest

from joulewise.align import r0
from joulewise.align.apple.endpoint import MlxEndpoint
from joulewise.align.interfaces import ChatMessage, ChatResult, ToolCallRequest
from joulewise.clock import FakeClock
from tests.align.test_apple_campaign import base_config


class IntegrationTest(unittest.TestCase):
    def endpoint(self, effort=None):
        config = base_config()
        config = replace(config, model=replace(config.model, family="qwen3_5"))
        class Tokenizer:
            def apply_chat_template(self, messages, **kwargs):
                self.kwargs = kwargs
                return json.dumps(messages, sort_keys=True)
        tokenizer = Tokenizer()
        return MlxEndpoint(SimpleNamespace(_tokenizer=tokenizer), config, FakeClock(),
                           episode_domain="r0-parity", reasoning_effort=effort)

    def test_r0_and_workload_history_render_identical_prompt_ids(self):
        endpoint = self.endpoint()
        # Reasoning quotes an apparent call; endpoint's split is authoritative.
        result = ChatResult("<tool_call>actual call</tool_call>", "A thought quotes <tool_call>",
                            (ToolCallRequest("echo", "r0_echo", '{"value":"desk-check"}'),),
                            1, 0, 10, 4, 0, 1, 2,
                            {"raw_text": "ambiguous raw completion"})
        backend = SimpleNamespace(endpoint=endpoint)
        actual = [ChatMessage("user", "echo")]
        r0.append_result(backend, actual, result, r0.EchoTask())
        # Same transition used by EpisodeRuntimeAdapter in workload.py.
        production = [ChatMessage("user", "echo"), endpoint.assistant_history_message(result),
                      ChatMessage("tool", r0.EchoTask().call_tool("r0_echo", '{"value":"desk-check"}'),
                                  name="r0_echo", tool_call_id="echo")]
        ids = lambda messages: list(endpoint._render_prompt(messages, r0.ECHO_TOOLS).encode())
        self.assertEqual(ids(actual), ids(production))
        self.assertEqual(actual[1].reasoning_content, result.reasoning_text)

    def test_effort_reaches_production_template_and_default_is_omitted(self):
        for effort in (None, "medium", "low"):
            endpoint = self.endpoint(effort)
            endpoint._render_prompt([ChatMessage("user", "echo")], r0.ECHO_TOOLS)
            kwargs = endpoint.runtime._tokenizer.kwargs
            if effort is None:
                self.assertNotIn("reasoning_effort", kwargs)
            else:
                self.assertEqual(kwargs["reasoning_effort"], effort)


if __name__ == "__main__":
    unittest.main()
