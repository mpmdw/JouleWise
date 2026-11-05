"""Spec-carried history/template policy, with legacy bytes preserved when unset."""
from dataclasses import asdict, replace
import hashlib
import json
import os
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from joulewise.adapters.mock_runtime import MockRuntimeAdapter
from joulewise.align.apple.endpoint import MlxEndpoint
from joulewise.align.apple.campaign import _counterbalanced
from joulewise.align.apple.workload import EpisodeRuntimeAdapter, EpisodeSpec
from joulewise.align.interfaces import ChatMessage, ChatResult
from joulewise.clock import FakeClock
from joulewise.identity_pins import _runtime_probe_metadata, derive_model_runtime_config_from_metadata
from tests.align.test_apple_campaign import as_config, base_config, episode_spec
from tests.align.test_xml_tool_calls import (
    TOOLS, FIXTURES, jinja2, synthetic_endpoint_cache_probe, template_renderer,
)


class CaptureTokenizer:
    def apply_chat_template(self, messages, **kwargs):
        self.messages, self.kwargs = messages, kwargs
        return json.dumps({"messages": messages, "kwargs": kwargs}, sort_keys=True)


class HistoryRenderingTests(unittest.TestCase):
    def test_unset_fields_preserve_spec_bytes(self):
        spec = episode_spec(hidden=False)
        obj = asdict(spec)
        for key in ("assistant_history", "chat_template_kwargs"):
            obj.pop(key, None)
        obj = {key: value for key, value in obj.items() if value is not None}
        legacy = json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False)
        self.assertEqual(spec.to_text(), legacy)
        self.assertEqual(EpisodeSpec.from_text(legacy).to_text(), legacy)

    def test_explicit_fields_roundtrip_and_validate(self):
        spec = replace(episode_spec(hidden=False), assistant_history="reasoning_content",
                       chat_template_kwargs={"reasoning_effort": "medium", "preserve_thinking": True})
        self.assertEqual(EpisodeSpec.from_text(spec.to_text()), spec)
        for updates in ({"assistant_history": "raw"}, {"chat_template_kwargs": []},
                        {"chat_template_kwargs": {"tokenize": True}},
                        {"chat_template_kwargs": {"reasoning_effort": float("nan")}},
                        {"enable_thinking": True, "chat_template_kwargs": {"enable_thinking": False}}):
            obj = json.loads(episode_spec(hidden=False).to_text())
            obj.update(updates)
            with self.subTest(updates=updates), self.assertRaises(ValueError):
                EpisodeSpec.from_text(json.dumps(obj))

    def test_history_and_template_kwargs_reach_both_render_paths(self):
        for family in ("qwen3_moe", "qwen3_8", "qwen3.8"):
            with self.subTest(family=family):
                tokenizer = CaptureTokenizer()
                config = base_config()
                config = replace(config, model=replace(config.model, family=family))
                endpoint = MlxEndpoint(SimpleNamespace(_tokenizer=tokenizer), config, FakeClock(),
                    episode_domain="synthetic", assistant_history="reasoning_content",
                    chat_template_kwargs={"reasoning_effort": "low"}, enable_thinking=True)
                result = ChatResult("answer", "private", (), 0, 0, 0, 0, 0, None, 0)
                stored = endpoint.assistant_history_message(result)
                endpoint._render_prompt([ChatMessage("user", "x"), stored], TOOLS)
                self.assertEqual(tokenizer.messages[-1]["content"], "answer")
                self.assertEqual(tokenizer.messages[-1]["reasoning_content"], "private")
                self.assertEqual(tokenizer.kwargs["reasoning_effort"], "low")
                self.assertIs(tokenizer.kwargs["enable_thinking"], True)
                self.assertEqual(json.loads(endpoint.identity)["execution_policy"], {
                    "assistant_history": "reasoning_content",
                    "chat_template_kwargs": {"reasoning_effort": "low"}})

    def test_policy_changes_identity_and_workload_passes_controls(self):
        hashes = set()
        for effort in ("xhigh", "medium", "low"):
            spec = replace(episode_spec(hidden=False), max_turns=1,
                           assistant_history="reasoning_content",
                           chat_template_kwargs={"reasoning_effort": effort})
            config = as_config(spec, "synthetic-template-policy")
            clock = FakeClock()
            runtime = EpisodeRuntimeAdapter(MockRuntimeAdapter(clock), clock)
            self.assertTrue(runtime.prepare(config).ok)
            identity = runtime.identity_projection_metadata(config)
            policy = identity["sampler"]["execution_policy"]
            self.assertEqual(policy["chat_template_kwargs"], {"reasoning_effort": effort})
            self.assertEqual(policy["assistant_history"], "reasoning_content")
            stack, pins = derive_model_runtime_config_from_metadata(config.to_dict(), _runtime_probe_metadata(config))
            self.assertEqual(stack["sampler_output_policy"]["sampler"]["execution_policy"], policy)
            hashes.add(pins["runtime_identity_sha256"])
            with patch("joulewise.align.apple.workload.MlxEndpoint", wraps=MlxEndpoint) as constructor:
                runtime.run_workload(config)
            self.assertEqual(constructor.call_args.kwargs["chat_template_kwargs"], spec.chat_template_kwargs)
            self.assertEqual(constructor.call_args.kwargs["assistant_history"], "reasoning_content")
        self.assertEqual(len(hashes), 3)

    def test_counterbalance_keeps_different_template_policies_in_separate_cells(self):
        benign = replace(episode_spec(hidden=False), condition="benign",
                         chat_template_kwargs={"reasoning_effort": "low"})
        sabotage = replace(benign, condition="sabotage", chat_template_kwargs={"reasoning_effort": "medium"})
        self.assertEqual(_counterbalanced([benign, sabotage])[1], ("unmatched_condition_cells_retained",))
        self.assertEqual(_counterbalanced([benign, replace(benign, condition="sabotage")])[1], ())

    def test_implicit_xml_history_is_recorded_and_legacy_json_identity_stays_unset(self):
        # Legacy (pre-#657) specs omit the checkpoint field; new specs carry 0.
        spec = replace(episode_spec(hidden=False), hybrid_checkpoint_limit=None)
        for family in ("qwen3_moe", "qwen3_8"):
            config = as_config(spec, "synthetic-policy")
            config = replace(config, model=replace(config.model, family=family))
            runtime = EpisodeRuntimeAdapter(MockRuntimeAdapter(FakeClock()), FakeClock())
            self.assertTrue(runtime.prepare(config).ok)
            sampler = runtime.identity_projection_metadata(config)["sampler"]
            if family == "qwen3_8":
                self.assertEqual(sampler["execution_policy"]["assistant_history"], "reasoning_content")
            else:
                self.assertNotIn("execution_policy", sampler)


@unittest.skipIf(jinja2 is None, "real template rendering needs optional Jinja2")
class RealTemplateHistoryTests(unittest.TestCase):
    def test_effort_ladder_and_scrub_use_the_same_render_path(self):
        import jinja2.sandbox
        template = template_renderer()
        for effort in ("xhigh", "medium", "low"):
            with self.subTest(effort=effort):
                rows = synthetic_endpoint_cache_probe(template, endpoint_options={
                    "assistant_history": "reasoning_content",
                    "chat_template_kwargs": {"reasoning_effort": effort},
                })
                self.assertTrue(all(row["rewritten_suffix_bytes"] == 0 for row in rows), rows)


@unittest.skipUnless(os.environ.get("JW_ALIGN_NATIVE_TESTS") == "1",
                     "opt-in native MLX/pinned-tokenizer gate; run outside sandbox")
class NativeHistoryRenderingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            import mlx.core as mx
            from transformers import AutoTokenizer
        except ImportError as exc:
            raise unittest.SkipTest(f"native MLX and transformers required: {exc}")
        model = os.environ.get("JW_ALIGN_QWEN38_MODEL")
        if not model:
            raise AssertionError("set JW_ALIGN_QWEN38_MODEL to the local 815b83c0 tokenizer snapshot")
        cls.mx = mx
        cls.tokenizer = AutoTokenizer.from_pretrained(model, local_files_only=True)
        expected = hashlib.sha256((FIXTURES / "qwen38_chat_template.jinja").read_bytes()).hexdigest()
        if hashlib.sha256(cls.tokenizer.chat_template.encode()).hexdigest() != expected:
            raise AssertionError("815b83c0 template differs from the supplied offline fixture; reverify provenance")

    def test_pinned_tokenizer_closed_reasoning_has_zero_rewritten_tokens(self):
        from joulewise.align.apple.endpoint import parse_completion
        config = base_config()
        config = replace(config, model=replace(config.model, family="qwen3_8"))
        endpoint = MlxEndpoint(SimpleNamespace(_tokenizer=self.tokenizer), config, FakeClock(),
            episode_domain="native-tokenizer", assistant_history="reasoning_content")
        for mode in ("one_call", "two_calls", "prose"):
            with self.subTest(mode=mode):
                history, previous = [ChatMessage("user", "Do it")], []
                for turn in range(6):
                    prompt_ids = self.tokenizer.encode(endpoint._render_prompt(history, TOOLS), add_special_tokens=False)
                    self.assertEqual(prompt_ids[:len(previous)], previous)
                    call = ("<tool_call>\n<function=update>\n<parameter=text>\nrow " + str(turn)
                            + "\n</parameter>\n</function>\n</tool_call>")
                    visible = "Before.\n\n" + call if mode == "prose" else call
                    if mode == "two_calls":
                        visible += "\n" + call
                    wire = f"reason {turn}\n</think>\n\n" + visible
                    content, reasoning, calls, flags = parse_completion(
                        wire, model_family="qwen3_8", tools=TOOLS, reasoning_open=True, reasoning_tokens=1)
                    self.assertFalse(any(flag.startswith("malformed_tool_call:") for flag in flags), flags)
                    result = ChatResult(content, reasoning, calls, 0, 0, 0, 0, 0, None, 0)
                    emitted = self.tokenizer.encode(wire + "<|im_end|>", add_special_tokens=False)
                    # Exercise native ID storage too; no weights or measurement data.
                    native_ids = self.mx.array(emitted)
                    self.mx.eval(native_ids)
                    previous = prompt_ids + native_ids.tolist()
                    history.extend([endpoint.assistant_history_message(result), ChatMessage("tool", f"result {turn}")])

    def test_pinned_ids_do_not_count_literal_think_in_arguments(self):
        from joulewise.align.apple.endpoint import reasoning_tokens_from_ids
        wire = ("plan\n</think>\n\n<tool_call>\n<function=update>\n<parameter=text>\n"
                "literal <think>quoted\n</parameter>\n</function>\n</tool_call>")
        ids = self.mx.array(self.tokenizer.encode(wire, add_special_tokens=False))
        self.mx.eval(ids)
        self.assertEqual(reasoning_tokens_from_ids(self.tokenizer, ids.tolist(), reasoning_open=True,
                                                 stop_at_tool_call=True),
                         len(self.tokenizer.encode("plan\n", add_special_tokens=False)))
