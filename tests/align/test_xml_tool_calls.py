"""Synthetic wire/template checks only; no models, network, or measurements."""
from __future__ import annotations

from dataclasses import asdict, replace
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from joulewise.adapters.mlx_runtime import MlxRuntimeAdapter
from joulewise.adapters.mock_runtime import MockRuntimeAdapter
from joulewise.align.apple.endpoint import MlxEndpoint, parse_completion
from joulewise.align.apple.xml_tool_calls import XML_MODEL_FAMILIES
from joulewise.align.endpoints import AssistantMessage
from joulewise.align.interfaces import ChatMessage, ChatResult, ToolCallRequest
from joulewise.clock import FakeClock
from joulewise.schemas import RuntimeBackend
from tests.align.test_apple_campaign import as_config, base_config, episode_spec

try:
    import jinja2
except ImportError:
    jinja2 = None

FIXTURES = Path(__file__).with_name("fixtures")
TOOLS = [{"type": "function", "function": {
    "name": "update", "parameters": {
        "type": "object", "additionalProperties": False,
        "properties": {
            "text": {"type": "string"}, "count": {"type": "integer"},
            "amount": {"type": "number"}, "active": {"type": "boolean"},
            "rows": {"type": "array", "items": {"type": "integer"}},
            "meta": {"type": "object", "properties": {"name": {"type": "string"}},
                     "required": ["name"], "additionalProperties": False},
            "empty": {"type": "null"},
            "mode": {"enum": ["read", "write"], "type": "string"},
        }, "required": ["text"],
    },
}}, {"type": "function", "function": {"name": "end_task", "parameters": {
    "type": "object", "properties": {}, "additionalProperties": False,
}}}]


def xml(parameters="<parameter=text>hello</parameter>", name="update"):
    return f"<tool_call><function={name}>{parameters}</function></tool_call>"


def parse(text, **kwargs):
    return parse_completion(text, model_family="qwen3_8", tools=TOOLS, **kwargs)


def template_renderer(fixture="qwen38_chat_template.jinja"):
    environment = jinja2.sandbox.ImmutableSandboxedEnvironment(
        trim_blocks=True, lstrip_blocks=True, extensions=["jinja2.ext.loopcontrols"])
    # Match HF's JSON filter rather than Jinja's HTML-safe JSON default.
    environment.filters["tojson"] = lambda value, **kwargs: json.dumps(value, ensure_ascii=False, **kwargs)

    def fail(message):
        raise ValueError(message)
    environment.globals["raise_exception"] = fail
    return environment.from_string((FIXTURES / fixture).read_text())


def synthetic_prefix_probe(template, *, preserve_thinking=None, tool_chain=False):
    """UTF-8 byte LCP of six completed assistant turns as history grows.

    Report the old suffix made unusable, not a tokenizer-derived token count.
    A tool chain has one real query; ordinary dialogue has six real queries.
    """
    history = [{"role": "user", "content": "query 0"}]
    previous = b""
    rows = []
    kwargs = {} if preserve_thinking is None else {"preserve_thinking": preserve_thinking}
    for turn in range(6):
        if turn:
            history.append({"role": "tool" if tool_chain else "user", "content": f"result {turn}"})
        message = {"role": "assistant", "content": "" if tool_chain else f"answer {turn}",
                   "reasoning_content": f"reason {turn}"}
        if tool_chain:
            message["tool_calls"] = [{"function": {"name": "update", "arguments": {"text": f"row {turn}"}}}]
        history.append(message)
        rendered = template.render(messages=history, tools=TOOLS, add_generation_prompt=False, **kwargs).encode()
        shared = 0
        for a, b in zip(previous, rendered):
            if a != b:
                break
            shared += 1
        if turn:
            rows.append({"turn": turn + 1, "old_bytes": len(previous), "common_prefix_bytes": shared,
                         "rewritten_suffix_bytes": len(previous) - shared})
        previous = rendered
    return rows


def synthetic_endpoint_cache_probe(template, *, compact=False, multiple_parameters=False,
                                   raw_history=False, dialogue=False):
    """Compare rendered next prompts with prior prompt + synthetic emitted bytes.

    UTF-8 bytes stand in for text only, never for the pinned model's token IDs.
    Include the consumed EOS spelling, without inventing a post-EOS newline.
    Only native computation is replaced; chat, generation and history are real.
    """
    class Tokenizer:
        eos_token_ids = {0}

        def apply_chat_template(self, messages, **kwargs):
            return template.render(messages=messages, **kwargs)

        def encode(self, text, **kwargs):
            return list(text.encode())  # Synthetic byte IDs, not Qwen token IDs.

    clock = FakeClock()
    runtime = MlxRuntimeAdapter(clock)
    runtime._model, runtime._tokenizer = object(), Tokenizer()
    emitted = ""

    def stream_generate(*args, **kwargs):
        for character in emitted:  # All probe emissions are ASCII.
            clock.sleep(.001)
            yield SimpleNamespace(token=ord(character), text=character, finish_reason=None)
        yield SimpleNamespace(token=0, text="", finish_reason="stop")

    runtime._mlx_lm = SimpleNamespace(stream_generate=stream_generate, make_sampler=lambda temp: object())
    config = base_config()
    config = replace(config, model=replace(config.model, family="qwen3_8"),
                     hardware_target=replace(config.hardware_target, runtime_backend=RuntimeBackend.MLX))
    endpoint = MlxEndpoint(runtime, config, clock, episode_domain="synthetic")
    history = [ChatMessage("user", "query 0")]
    previous = b""
    rows = []
    for turn in range(6):
        prompt = endpoint._render_prompt(history, TOOLS).encode()
        if turn:
            shared = 0
            for a, b in zip(previous, prompt):
                if a != b:
                    break
                shared += 1
            rows.append({"turn": turn + 1, "old_bytes": len(previous), "common_prefix_bytes": shared,
                         "rewritten_suffix_bytes": len(previous) - shared})
        wire = (xml(f"<parameter=text>row {turn}</parameter>") if compact else
                f"<tool_call>\n<function=update>\n<parameter=text>\nrow {turn}\n</parameter>\n</function>\n</tool_call>")
        if multiple_parameters:
            # Deliberately nonalphabetical: reordering this mapping rewrites
            # canonical generated bytes even when all whitespace matches.
            wire = wire.replace("</function>", (
                "<parameter=count>1</parameter>" if compact else
                "<parameter=count>\n1\n</parameter>\n") + "</function>")
        emitted = f"reason {turn}\n</think>\n\n" + (f"answer {turn}" if dialogue else wire)
        previous = prompt + emitted.encode() + b"<|im_end|>"
        result = endpoint.chat(history, tools=TOOLS, max_tokens=512, temperature=0, seed=None)
        if any(flag.startswith(("endpoint_error:", "malformed_tool_call:")) for flag in endpoint.flags):
            raise AssertionError(endpoint.flags)
        if not raw_history and endpoint.turn_provenance[-1]["generation"]["prior_hidden_prefill_tokens"] != 8 * turn:
            raise AssertionError("separate historical reasoning was not counted exactly once")
        assistant = (ChatMessage("assistant", emitted) if raw_history else
                     endpoint.assistant_history_message(result))
        history.extend([assistant, ChatMessage("user" if dialogue else "tool", f"result {turn}")])
    return rows


class XmlToolCallTests(unittest.TestCase):
    def test_schema_types_literal_strings_and_multiple_calls(self):
        wire = "Before. " + xml(
            '<parameter=text>\n  é & <tag> \\"quoted\\"\nline\n\n</parameter>'
            '<parameter=count>2</parameter><parameter=amount>1.25</parameter>'
            '<parameter=active>false</parameter><parameter=rows>[1,2]</parameter>'
            '<parameter=meta>{"name":"A & B"}</parameter><parameter=empty>null</parameter>'
            '<parameter=mode>write</parameter>') + "\n" + xml("", "end_task")
        visible, _, calls, flags = parse(wire)
        self.assertEqual(flags, ())
        self.assertEqual(visible, wire)
        self.assertEqual([c.name for c in calls], ["update", "end_task"])
        self.assertEqual(json.loads(calls[0].arguments_json), {
            "text": '  é & <tag> \\"quoted\\"\nline\n', "count": 2, "amount": 1.25,
            "active": False, "rows": [1, 2], "meta": {"name": "A & B"},
            "empty": None, "mode": "write",
        })
        self.assertEqual(calls[1].arguments_json, "{}")
        self.assertNotEqual(calls[0].call_id, calls[1].call_id)

    def test_strings_are_never_json_decoded_or_entity_unescaped(self):
        for value in ("", "\n", "null", "true", "123", '"quoted"', '[1,2]', "&amp;", "  spaces  ",
                      "literal <think>thought</think>"):
            with self.subTest(value=value):
                _, _, calls, flags = parse(xml(f"<parameter=text>\n{value}\n</parameter>"))
                self.assertEqual(flags, ())
                self.assertEqual(json.loads(calls[0].arguments_json), {"text": value})

    def test_malformed_nested_unknown_duplicate_and_partial_calls_refused_atomically(self):
        valid = xml()
        invalid = [
            valid[:-1], valid.replace("</tool_call>", ""), "</tool_call>" + valid,
            valid + "</tool_call>", valid + " suffix", valid + "<tool_call>",
            valid.replace("</function>", "</wrong>"),
            valid.replace("<function=update>", "<function=unknown>"),
            valid.replace("<function=update>", "<function =update>"),
            xml(""), xml("<parameter=unknown>x</parameter>"),
            xml("<parameter=text>a</parameter><parameter=text>b</parameter>"),
            xml("<parameter=text>" + valid + "</parameter>"),
            xml("<parameter=text><parameter=count>1</parameter></parameter>"),
            xml("<function=end_task></function>"),
            valid.replace("</parameter>", ""),
            '<tool_call>{"name":"update","arguments":{"text":"x"}}</tool_call>',
            valid + '<tool_call>{broken}</tool_call>',
            valid.replace("<tool_call>", "<tool_call extra>"),
            valid.replace("</function>", "</function><function=end_task></function>"),
        ]
        for wire in invalid:
            with self.subTest(wire=wire):
                visible, _, calls, flags = parse(wire)
                self.assertEqual(visible, wire)
                self.assertEqual(calls, ())
                self.assertTrue(any(f.startswith("malformed_tool_call:xml:") for f in flags), flags)

    def test_schema_type_mismatches_and_nonfinite_or_duplicate_json_refused(self):
        for key, value in (("count", "true"), ("count", "1.5"), ("count", '"2"'),
                           ("active", "1"), ("active", "False"), ("empty", '"null"'),
                           ("amount", "NaN"), ("amount", "Infinity"), ("amount", "1e999"),
                           ("rows", "[true]"), ("meta", "{}"), ("mode", "execute"),
                           ("meta", '{"name":"a","name":"b"}')):
            with self.subTest(key=key, value=value):
                _, _, calls, flags = parse(xml("<parameter=text>x</parameter>" + f"<parameter={key}>{value}</parameter>"))
                self.assertEqual(calls, ())
                self.assertTrue(flags)

    def test_local_refs_unions_and_ambiguous_wire_values(self):
        tools = [{"function": {"name": "choose", "parameters": {
            "type": "object", "$defs": {"record": {"type": "object", "properties": {
                "id": {"type": "integer"}}, "required": ["id"]}},
            "properties": {"x": {"anyOf": [{"$ref": "#/$defs/record"}, {"type": "null"}]}},
            "required": ["x"],
        }}}]
        for value in ('{"id":7}', 'null'):
            result = parse_completion(xml(f"<parameter=x>{value}</parameter>", "choose"),
                                      model_family="qwen3_8", tools=tools)
            self.assertEqual(result[3], ())
            self.assertEqual(json.loads(result[2][0].arguments_json), {"x": json.loads(value)})
        tools[0]["function"]["parameters"]["properties"]["x"] = {"type": ["string", "null"]}
        result = parse_completion(xml("<parameter=x>null</parameter>", "choose"), model_family="qwen3_8", tools=tools)
        self.assertEqual(result[2], ())  # null vs the literal string 'null' is undecidable.
        self.assertIn("ambiguous_or_invalid_parameter_type", result[3][0])

    def test_config_selection_never_uses_model_name_or_output_sniffing(self):
        wire = xml()
        for family in XML_MODEL_FAMILIES:
            self.assertEqual(len(parse_completion(wire, model_family=family, tools=TOOLS)[2]), 1)
        for family in (None, "qwen3", "qwen3_moe", "qwen3_next", "unknown"):
            with self.subTest(family=family):
                config = base_config()
                config = replace(config, model=replace(config.model, family=family, name="Qwen3.8-27B"))
                clock = FakeClock()
                endpoint = MlxEndpoint(MockRuntimeAdapter(clock), config, clock, episode_domain="synthetic",
                                       mock_turns=({"content": wire, "completion_tokens": 100},))
                result = endpoint.chat([ChatMessage("user", "x")], tools=TOOLS, max_tokens=200, temperature=0, seed=None)
                self.assertEqual(result.tool_calls, ())
                self.assertTrue(any(f.startswith("malformed_tool_call:") for f in endpoint.flags))

    def test_endpoint_dispatch_and_reasoning_cuts(self):
        config = base_config()
        config = replace(config, model=replace(config.model, family="qwen3_8"))
        clock = FakeClock()
        endpoint = MlxEndpoint(MockRuntimeAdapter(clock), config, clock, episode_domain="synthetic",
                               mock_turns=({"content": xml(), "completion_tokens": 100},))
        result = endpoint.chat([ChatMessage("user", "x")], tools=TOOLS, max_tokens=200, temperature=0, seed=None)
        self.assertEqual([c.name for c in result.tool_calls], ["update"])
        self.assertTrue(result.tool_calls[0].call_id.startswith("0-"))
        for wire in ("<think>hidden " + xml(), "hidden " + xml()):
            _, _, calls, flags = parse(wire, reasoning_open=not wire.startswith("<think>"))
            self.assertEqual(calls, ())
            self.assertIn("unclosed_reasoning_span", flags)
        _, reasoning, calls, _ = parse("plan</think>" + xml(), reasoning_open=True, reasoning_tokens=1)
        self.assertEqual(reasoning, "plan")
        self.assertEqual(len(calls), 1)

    def test_json_parser_bytes_match_pilot9_base(self):
        fixture = json.loads((FIXTURES / "json_tool_calls_c9a0a3943.json").read_text())
        for row in fixture["cases"]:
            for family in (None, "qwen3_moe", "qwen3_next"):
                with self.subTest(case=row["label"], family=family):
                    visible, reasoning, calls, flags = parse_completion(row["text"], model_family=family, **row["kwargs"])
                    actual = [visible, reasoning, [asdict(call) for call in calls], list(flags)]
                    self.assertEqual(json.dumps(actual, ensure_ascii=False).encode(),
                                     json.dumps(row["expected"], ensure_ascii=False).encode())

    def test_json_render_and_endpoint_bytes_match_pilot9_base(self):
        fixture = json.loads((FIXTURES / "json_endpoint_c9a0a3943.json").read_text())
        class Tokenizer:
            def apply_chat_template(self, messages, **kwargs):
                return json.dumps({"messages": messages, "kwargs": kwargs}, sort_keys=True, ensure_ascii=False)
        for family in ("qwen3_moe", "qwen3_next"):
            config = base_config()
            config = replace(config, model=replace(config.model, family=family))
            clock = FakeClock()
            endpoint = MlxEndpoint(MockRuntimeAdapter(clock), config, clock, episode_domain="synthetic",
                                   mock_turns=tuple(fixture["scripts"]), enable_thinking=True)
            endpoint.runtime._tokenizer = Tokenizer()
            history = [ChatMessage(**item) for item in fixture["messages"]]
            self.assertEqual(endpoint._render_prompt(history, TOOLS).encode(), fixture["rendered"].encode())
            trace = [asdict(endpoint.chat(history, tools=TOOLS, max_tokens=200, temperature=0, seed=None))
                     for _ in fixture["scripts"]]
            self.assertEqual(json.dumps(trace, sort_keys=True).encode(),
                             json.dumps(fixture["trace"], sort_keys=True).encode())

    def test_fixture_digest(self):
        for name in ("qwen38_chat_template", "flashnext_chat_template"):
            provenance = json.loads((FIXTURES / f"{name}.provenance.json").read_text())
            self.assertEqual(hashlib.sha256((FIXTURES / f"{name}.jinja").read_bytes()).hexdigest(),
                             provenance["sha256"])

    def test_endpoint_stores_split_history_only_for_xml_families(self):
        class Tokenizer:
            def apply_chat_template(self, messages, **kwargs):
                self.messages = messages
                return "rendered"
        raw = "plan\n</think>\n\n" + xml()
        content, reasoning, calls, _ = parse(raw, reasoning_open=True, reasoning_tokens=1)
        result = ChatResult(content, reasoning, calls, 0, 0, 0, 0, 0, None, 0,
                            raw_usage={"raw_text": raw})
        tokenizer = Tokenizer()
        config = base_config()
        for family in (*sorted(XML_MODEL_FAMILIES), "qwen3_moe", "qwen3_next", None):
            with self.subTest(family=family):
                endpoint = MlxEndpoint(SimpleNamespace(_tokenizer=tokenizer),
                    replace(config, model=replace(config.model, family=family, name="Qwen3.8-27B")),
                    FakeClock(), episode_domain="synthetic")
                stored = endpoint.assistant_history_message(result)
                endpoint._render_prompt([ChatMessage("user", "Do it"), stored], TOOLS)
                item = tokenizer.messages[-1]
                if family in XML_MODEL_FAMILIES:
                    self.assertEqual(stored.reasoning_content, "plan\n")
                    self.assertEqual(stored.content, "")
                    self.assertEqual(item["reasoning_content"], "plan\n")
                    self.assertEqual(item["content"], "")
                    self.assertEqual(item["tool_calls"][0]["function"]["arguments"], {"text": "hello"})
                else:
                    self.assertIs(type(stored), ChatMessage)
                    self.assertEqual(item, {"role": "assistant", "content": raw})

    def test_structured_visible_think_tags_are_not_split_again(self):
        class Tokenizer:
            def apply_chat_template(self, messages, **kwargs):
                return json.dumps(messages)
        config = base_config()
        endpoint = MlxEndpoint(SimpleNamespace(_tokenizer=Tokenizer()),
            replace(config, model=replace(config.model, family="qwen3_8")),
            FakeClock(), episode_domain="synthetic")
        visible = "Explain literal <think> and </think> tags."
        for reasoning in ("", "already separated"):
            result = ChatResult(visible, reasoning, (), 0, 0, 0, 0, 0, None, 0)
            history = [ChatMessage("user", "Explain"), endpoint.assistant_history_message(result)]
            item = json.loads(endpoint._render_prompt(history, TOOLS))[-1]
            self.assertEqual(item["content"], visible)
            self.assertEqual(item["reasoning_content"], reasoning)

    def test_workload_stores_separate_fields_and_replays_next_turn(self):
        from joulewise.align.apple.workload import EpisodeRuntimeAdapter
        for family in ("qwen3_5", "qwen3_moe", "qwen3_next"):
            with self.subTest(family=family):
                call = (xml("<parameter=step>0</parameter>", "lookup")
                        if family in XML_MODEL_FAMILIES else
                        '<tool_call>{"name":"lookup","arguments":{"step":0}}</tool_call>')
                raw = "<think>plan</think>" + call
                spec = replace(episode_spec(hidden=False), max_turns=2, mock_turns=(
                    {"content": raw, "completion_tokens": 100, "reasoning_tokens": 1},
                    {"content": "Done", "completion_tokens": 10},
                ))
                config = as_config(spec, "synthetic-history")
                config = replace(config, model=replace(config.model, family=family))
                clock = FakeClock()
                runtime = EpisodeRuntimeAdapter(MockRuntimeAdapter(clock), clock)
                self.assertTrue(runtime.prepare(config).ok)
                result = runtime.run_workload(config)
                rows = [json.loads(line) for line in result.output_artifacts["align_transcript.jsonl"].splitlines()]
                self.assertEqual([row["role"] for row in rows],
                                 ["system", "user", "assistant", "tool", "assistant"])
                if family in XML_MODEL_FAMILIES:
                    self.assertEqual(rows[2]["reasoning_content"], "plan")
                    self.assertEqual(rows[2]["content"], "")
                    self.assertEqual(rows[2]["tool_calls"][0]["name"], "lookup")
                else:
                    self.assertEqual(rows[2], asdict(ChatMessage("assistant", raw)))


@unittest.skipIf(jinja2 is None, "real template rendering needs optional Jinja2")
class QwenTemplateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import jinja2.sandbox
        cls.template = template_renderer()

    def test_real_template_round_trip_multiple_calls_all_parameter_types(self):
        arguments = {"text": ' \nUnicode é & <tag> "quote"\n ', "count": 2, "amount": 1.25,
                     "active": False, "rows": [1, 2], "meta": {"name": "é"}, "empty": None, "mode": "read"}
        expected = [("update", arguments), ("end_task", {}), ("update", {"text": ""})]
        messages = [{"role": "user", "content": "Do it"}, {"role": "assistant", "content": "Before.",
            "reasoning_content": "plan", "tool_calls": [
                {"type": "function", "function": {"name": name, "arguments": args}} for name, args in expected]}]
        rendered = self.template.render(messages=messages, tools=TOOLS, add_generation_prompt=False)
        assistant = rendered.rsplit("<|im_start|>assistant\n", 1)[1].removesuffix("<|im_end|>\n")
        _, reasoning, calls, flags = parse(assistant, reasoning_tokens=1)
        self.assertEqual(flags, ())
        self.assertEqual(reasoning.strip(), "plan")
        self.assertEqual([(c.name, json.loads(c.arguments_json)) for c in calls], expected)

    def test_endpoint_renders_arguments_as_mappings_and_raw_calls_only_once(self):
        class Tokenizer:
            def apply_chat_template(inner, messages, **kwargs):
                return self.template.render(messages=messages, **kwargs)
        config = base_config()
        config = replace(config, model=replace(config.model, family="qwen3_5_moe"))
        endpoint = MlxEndpoint(SimpleNamespace(_tokenizer=Tokenizer()), config, FakeClock(), episode_domain="synthetic")
        raw = "<think>\nplan\n</think>\n\n" + xml()
        history = [ChatMessage("user", "Do it"), ChatMessage("assistant", raw),
                   ChatMessage("assistant", '{"text":"hello"}', name="update", tool_call_id="a"),
                   ChatMessage("tool", "ok", name="update", tool_call_id="a")]
        rendered = endpoint._render_prompt(history, TOOLS)
        assistant = rendered.split("<|im_start|>assistant\n", 1)[1].split("<|im_end|>", 1)[0]
        self.assertEqual(assistant.count("<tool_call>"), 1)
        self.assertIn("<think>\nplan\n</think>", assistant)
        self.assertIn("<parameter=text>\nhello\n</parameter>", assistant)
        _, _, calls, flags = parse(assistant, reasoning_tokens=1)
        self.assertEqual(flags, ())
        self.assertEqual(json.loads(calls[0].arguments_json), {"text": "hello"})
        # Actual workload.py stores raw assistant text followed by tool results,
        # without a separate per-call assistant record.
        raw_only = [history[0], history[1], history[-1]]
        self.assertEqual(endpoint._render_prompt(raw_only, TOOLS), rendered)
        # A prefilled reasoning span may quote full tool-call syntax.
        quoted = "plan quotes " + xml() + "</think>" + xml()
        raw_only[1] = ChatMessage("assistant", quoted)
        rendered = endpoint._render_prompt(raw_only, TOOLS)
        assistant = rendered.split("<|im_start|>assistant\n", 1)[1].split("<|im_end|>", 1)[0]
        _, reasoning, calls, flags = parse(assistant, reasoning_tokens=1)
        self.assertEqual(flags, ())
        self.assertEqual(reasoning.strip(), "plan quotes " + xml())
        self.assertEqual(len(calls), 1)

    def test_structured_history_keeps_separate_reasoning_and_literal_think_arguments(self):
        class Tokenizer:
            def apply_chat_template(inner, messages, **kwargs):
                return self.template.render(messages=messages, **kwargs)
        config = base_config()
        config = replace(config, model=replace(config.model, family="qwen3_8"))
        endpoint = MlxEndpoint(SimpleNamespace(_tokenizer=Tokenizer()), config, FakeClock(), episode_domain="synthetic")
        arguments = {"text": "literal <think>value</think>"}
        history = [ChatMessage("user", "Do it"), AssistantMessage("assistant", "",
            tool_calls=(ToolCallRequest("a", "update", json.dumps(arguments)),), reasoning_text="plan"),
            ChatMessage("tool", "ok", tool_call_id="a")]
        rendered = endpoint._render_prompt(history, TOOLS)
        assistant = rendered.split("<|im_start|>assistant\n", 1)[1].split("<|im_end|>", 1)[0]
        _, reasoning, calls, flags = parse(assistant, reasoning_tokens=1)
        self.assertEqual(flags, ())
        self.assertEqual(reasoning.strip(), "plan")
        self.assertEqual(json.loads(calls[0].arguments_json), arguments)

    def test_reasoning_effort_and_enable_thinking_kwargs(self):
        def render(**kwargs):
            return self.template.render(messages=[{"role": "user", "content": "Hi"}],
                                        tools=None, add_generation_prompt=True, **kwargs)
        self.assertEqual(render(), render(enable_thinking=True, reasoning_effort="xhigh"))
        self.assertIn("Reasoning effort is set to low.", render(reasoning_effort="low"))
        self.assertNotIn("Reasoning effort is set", render(reasoning_effort="medium"))
        self.assertTrue(render().endswith("<think>\n"))
        self.assertTrue(render(enable_thinking=False).endswith("<think>\n\n</think>\n\n"))
        self.assertNotIn("Reasoning effort is set", render(enable_thinking=False, reasoning_effort="invalid"))
        for effort in ("high", "none", "invalid", None):
            with self.subTest(effort=effort), self.assertRaises(ValueError):
                render(reasoning_effort=effort)
        messages = [{"role": "user", "content": "First"}, {"role": "assistant", "content": "Answer",
                    "reasoning_content": "earlier reasoning"}, {"role": "user", "content": "Next"}]
        self.assertIn("earlier reasoning", self.template.render(
            messages=messages, enable_thinking=False, add_generation_prompt=True))

    def test_six_turn_prefix_stability_and_preserve_thinking(self):
        for chain in (False, True):
            defaults = synthetic_prefix_probe(self.template, tool_chain=chain)
            explicit = synthetic_prefix_probe(self.template, preserve_thinking=True, tool_chain=chain)
            self.assertEqual(defaults, explicit)
            self.assertEqual([r["rewritten_suffix_bytes"] for r in defaults], [0] * 5)
        dialogue = synthetic_prefix_probe(self.template, preserve_thinking=False)
        self.assertEqual([r["rewritten_suffix_bytes"] for r in dialogue], [46] * 5)
        chain = synthetic_prefix_probe(self.template, preserve_thinking=False, tool_chain=True)
        self.assertEqual([r["rewritten_suffix_bytes"] for r in chain], [0] * 5)

    def test_actual_endpoint_prompt_cache_prefix_with_canonical_and_compact_calls(self):
        canonical = synthetic_endpoint_cache_probe(self.template)
        self.assertEqual([r["rewritten_suffix_bytes"] for r in canonical], [0] * 5)
        multiple = synthetic_endpoint_cache_probe(self.template, multiple_parameters=True)
        self.assertEqual([r["rewritten_suffix_bytes"] for r in multiple], [0] * 5)
        compact = synthetic_endpoint_cache_probe(self.template, compact=True)
        self.assertEqual([r["rewritten_suffix_bytes"] for r in compact], [83] * 5)

    def test_both_real_templates_replay_six_split_assistant_turns(self):
        def unsplit(endpoint, messages, tools):
            # Reproduce the council's content-only history mapping, bypassing
            # the existing raw-history compatibility splitter as well.
            return endpoint.runtime._tokenizer.apply_chat_template(
                [{"role": message.role, "content": message.content} for message in messages],
                tools=list(tools), tokenize=False, add_generation_prompt=True)

        for fixture in ("qwen38_chat_template.jinja", "flashnext_chat_template.jinja"):
            template = template_renderer(fixture)
            for dialogue in (False, True):
                with self.subTest(template=fixture, dialogue=dialogue):
                    rows = synthetic_endpoint_cache_probe(template, dialogue=dialogue)
                    self.assertEqual([r["rewritten_suffix_bytes"] for r in rows], [0] * 5)
                    self.assertEqual(rows, synthetic_endpoint_cache_probe(
                        template, raw_history=True, dialogue=dialogue))
                    with patch.object(MlxEndpoint, "_render_xml_prompt", unsplit):
                        garbled = synthetic_endpoint_cache_probe(template, raw_history=True, dialogue=dialogue)
                    self.assertEqual([r["rewritten_suffix_bytes"] for r in garbled],
                                     [37 if dialogue else 119] * 5)


if __name__ == "__main__":
    unittest.main()
