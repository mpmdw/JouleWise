"""Synthetic readable-log binding checks; no models, caches or measurements."""
import hashlib
import json
import unittest
from types import SimpleNamespace

from joulewise.align.endpoints import AssistantMessage
from joulewise.align.interfaces import ChatMessage, ToolCallRequest
from joulewise.align.records import Turn, MonitorVerdict, from_json, to_json
from joulewise.align.shade.monitor import readable_messages, render_transcript
from joulewise.align.shade.recount import recount_transcript, compare_logged_work, EndpointRecountCodec


class TinyCodec:
    tokenizer_id = "synthetic-codepoints/v1"
    template_sha256 = hashlib.sha256(b"synthetic-template/v1").hexdigest()

    def encode(self, text):
        return [ord(c) for c in text]

    def decode(self, ids):
        return "".join(chr(i) for i in ids)

    def render_prompt(self, messages, tools, *, add_generation_prompt=True):
        # Includes system text and tool schemas; assistant prefix is open.
        text = "TOOLS:" + json.dumps(list(tools), sort_keys=True) + "\n"
        for m in messages:
            text += m.role + ":"
            if m.role == "assistant":
                text += getattr(m, "reasoning_text", "")
            text += m.content
            text += "".join(c.name + c.arguments_json for c in getattr(m, "tool_calls", ()))
            text += "\n"
        return text + ("assistant:" if add_generation_prompt else "")


class ReadableTests(unittest.TestCase):
    def messages(self):
        return [ChatMessage("system", "PRIVATE_SIDE_TASK"), ChatMessage("user", "Review."),
                AssistantMessage("assistant", "A<thinking>HIDDEN</thinking> B",
                    tool_calls=(ToolCallRequest("c1", "send", '{"to":"vault","tag":"<thinking>x</thinking>"}'),),
                    reasoning_text="NATIVE <thinking>must survive</thinking> </jw_reasoning>"),
                ChatMessage("tool", "<thinking>tool evidence</thinking>", "send", "c1")]

    def test_readable_preserves_native_reasoning_and_tool_arguments(self):
        messages = self.messages()
        rows = [json.loads(line) for line in render_transcript(messages, visibility="readable").splitlines()]
        self.assertNotIn("PRIVATE_SIDE_TASK", str(rows))
        self.assertEqual(rows[1]["native_reasoning"], messages[2].reasoning_text)
        self.assertEqual(rows[1]["tool_calls"][0]["arguments_json"], messages[2].tool_calls[0].arguments_json)
        self.assertEqual(rows[1]["content"], "A B")
        self.assertEqual(rows[2]["content"], messages[3].content)
        self.assertEqual(messages[2].content, "A<thinking>HIDDEN</thinking> B")

    def test_native_is_never_fed_through_content_strip(self):
        native = "<thinking>native</thinking><system_instructions>x</system_instructions>"
        m = AssistantMessage("assistant", "<thinking>closed</thinking><thinking>open", reasoning_text=native)
        viewed = readable_messages([m])[0]
        self.assertEqual(viewed.reasoning_text, native)
        self.assertEqual(viewed.content, "<thinking>open")

    def test_legacy_call_records_coalesce_with_arguments_and_native_wrappers_stay(self):
        rows = [ChatMessage("assistant", "<jw_reasoning>native</jw_reasoning>"),
                ChatMessage("assistant", '{"key":"value"}', "write", "c"),
                ChatMessage("tool", "ok", "write", "c")]
        view = render_transcript(rows, visibility="readable")
        self.assertIn("<jw_reasoning>native</jw_reasoning>", view)
        self.assertEqual(json.loads(view.splitlines()[0])["tool_calls"][0]["arguments_json"], '{"key":"value"}')

    def test_readable_record_roundtrip(self):
        v = MonitorVerdict("synthetic", "readable", 12.0, "a" * 64)
        self.assertEqual(from_json(MonitorVerdict, to_json(v)), v)

    def test_legacy_native_with_thinking_tags_cannot_be_stripped(self):
        native = "<jw_reasoning><thinking>still native</thinking></jw_reasoning>"
        view = json.loads(render_transcript([ChatMessage("assistant", native)], visibility="readable"))
        self.assertEqual(view["content"], native)


class RecountTests(unittest.TestCase):
    def fixture(self, scratchpad=False):
        codec = TinyCodec()
        tools = [{"type": "function", "function": {"name": "send", "parameters": {}}}]
        messages = [ChatMessage("system", "SIDE_TASK"), ChatMessage("user", "Review."),
                    AssistantMessage("assistant", "ok" + ("<thinking>hide</thinking>" if scratchpad else ""),
                        tool_calls=(ToolCallRequest("a", "send", '{"to":"vault"}'),), reasoning_text="plan")]
        prompt = codec.render_prompt(messages[:2], tools)
        closed = codec.render_prompt(messages, tools, add_generation_prompt=False)
        output = closed[len(prompt):]
        turn = Turn(0, 0, 1, 0, len(prompt), len(output), 4)
        provenance = [{"turn": 0, "generation": {"prompt_token_ids": codec.encode(prompt),
                       "output_token_ids": codec.encode(output)}}]
        return codec, tools, messages, [turn], provenance

    def test_recount_binds_exact_template_and_includes_system_tools(self):
        codec, tools, messages, turns, provenance = self.fixture()
        result = recount_transcript(messages, turns, provenance, codec=codec, tools=tools)
        self.assertTrue(result["binding_valid"])
        row = result["turns"][0]
        self.assertEqual(row["readable_prompt_tokens"], turns[0].prefill_tokens)
        self.assertEqual(row["readable_decode_tokens"], turns[0].decode_tokens)
        self.assertEqual(result["tokenizer_id"], codec.tokenizer_id)
        self.assertEqual(result["template_sha256"], codec.template_sha256)
        without_inputs = recount_transcript(messages, turns, provenance, codec=codec, tools=[])
        self.assertFalse(without_inputs["binding_valid"])
        self.assertIn("prompt_ids_mismatch", without_inputs["turns"][0]["flags"])

    def test_count_only_scratchpad_disclosure_does_not_pass_binding(self):
        codec, tools, messages, turns, provenance = self.fixture(True)
        r = recount_transcript(messages, turns, provenance, codec=codec, tools=tools)
        self.assertFalse(r["binding_valid"])
        self.assertIn("counted_content_not_readable", r["turns"][0]["flags"])
        self.assertGreater(r["turns"][0]["logged_decode_tokens"], r["turns"][0]["readable_decode_tokens"])

    def test_forged_counts_and_missing_provenance_refuse(self):
        codec, tools, messages, turns, provenance = self.fixture()
        for evidence in ([], [{"turn": 0, "generation": {}}]):
            with self.subTest(evidence=evidence), self.assertRaises(ValueError):
                recount_transcript(messages, turns, evidence, codec=codec, tools=tools)
        wrong = [Turn(0, 0, 1, 0, turns[0].prefill_tokens, turns[0].decode_tokens + 1)]
        r = recount_transcript(messages, wrong, provenance, codec=codec, tools=tools)
        self.assertFalse(r["binding_valid"])
        self.assertIn("logged_decode_count_mismatch", r["turns"][0]["flags"])

    def test_non_roundtrip_ids_are_explicit(self):
        codec, tools, messages, turns, provenance = self.fixture()
        codec.decode = lambda ids: "collapsed"
        r = recount_transcript(messages, turns, provenance, codec=codec, tools=tools)
        self.assertFalse(r["binding_valid"])
        self.assertIn("output_ids_not_roundtrippable", r["turns"][0]["flags"])

    def test_full_omission_retains_intercept_prefill_and_context_terms(self):
        full = [Turn(0, 0, 1, 2, 3, 4), Turn(1, 1, 2, 5, 6, 7)]
        result = compare_logged_work(full, [full[0]])
        self.assertEqual(result["h_decode_tokens"], 7)
        self.assertEqual(result["delta_design"], [1, 6, 7, (5+6)*7+7**2/2, 5*6+6**2/2])
        self.assertEqual(compare_logged_work(full, full)["delta_design"], [0]*5)

    def test_cached_context_without_matching_provenance_fails(self):
        codec, tools, messages, turns, provenance = self.fixture()
        wrong = [Turn(0, 0, 1, 2, turns[0].prefill_tokens-2, turns[0].decode_tokens)]
        result = recount_transcript(messages, wrong, provenance, codec=codec, tools=tools)
        self.assertFalse(result["binding_valid"])
        self.assertIn("cached_context_unverified", result["turns"][0]["flags"])

    def test_full_work_includes_a_turn_even_when_reported_mask_is_false(self):
        omitted = Turn(0, 0, 1, 2, 3, 4, logged=False)
        result = compare_logged_work([omitted], [omitted])
        self.assertEqual(result["delta_design"], [1, 3, 4, 28, 10.5])

    def test_apple_xml_renderer_seam_keeps_reasoning_args_system_and_template_policy(self):
        from joulewise.align.apple.endpoint import MlxEndpoint, _XmlAssistantMessage
        class Tokenizer(TinyCodec):
            def encode(self, text, *, add_special_tokens=False):
                self.specials = add_special_tokens
                return super().encode(text)
            def decode(self, ids, *, skip_special_tokens=False):
                return super().decode(ids)
            def apply_chat_template(self, messages, **kwargs):
                self.arguments = (messages, kwargs)
                return json.dumps([messages, kwargs], sort_keys=True)
        tokenizer = Tokenizer()
        endpoint = object.__new__(MlxEndpoint)
        endpoint.runtime = SimpleNamespace(_tokenizer=tokenizer)
        endpoint.model_family = "qwen3_5"
        endpoint.chat_template_kwargs = {"preserve_thinking": True}
        endpoint.enable_thinking = True
        messages = [ChatMessage("system", "SIDE_TASK"), _XmlAssistantMessage("assistant", "visible",
            reasoning_content="native <thinking>literal</thinking>",
            tool_calls=(ToolCallRequest("c", "send", '{"to":"vault"}'),))]
        tools = [{"type": "function", "function": {"name": "send", "parameters": {"type": "object"}}}]
        codec = EndpointRecountCodec(endpoint, tokenizer.tokenizer_id, tokenizer.template_sha256)
        rendered = codec.render_prompt(readable_messages(messages), tools)
        codec.encode(rendered)
        self.assertFalse(tokenizer.specials)
        history, kwargs = tokenizer.arguments
        self.assertEqual(history[0]["content"], "SIDE_TASK")
        self.assertEqual(history[1]["reasoning_content"], messages[1].reasoning_content)
        self.assertEqual(history[1]["tool_calls"][0]["function"]["arguments"], {"to": "vault"})
        self.assertEqual(kwargs["tools"], tools)
        self.assertTrue(kwargs["enable_thinking"])
        self.assertTrue(kwargs["preserve_thinking"])


if __name__ == "__main__":
    unittest.main()
