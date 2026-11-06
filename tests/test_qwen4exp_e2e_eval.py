"""Tests for the qwen4_exp end-to-end validation harness (stub generators only).

Template-dependent tests need jinja2; the transformers-parity test needs
transformers; the MLX adapter test needs mlx + mlx-lm; the SHADE smoke needs a
Git object for the ALIGN kit. Each skips with its reason when unavailable.
Run the full set with the approved venv, for example:

    /private/tmp/jwsol/venv-mlx/bin/python -m unittest tests.test_qwen4exp_e2e_eval
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts import qwen4exp_e2e_eval as e2e

REPO = Path(__file__).resolve().parent.parent
HAS_JINJA = importlib.util.find_spec("jinja2") is not None
HAS_TRANSFORMERS = importlib.util.find_spec("transformers") is not None
HAS_MLX = importlib.util.find_spec("mlx") is not None and importlib.util.find_spec("mlx_lm") is not None
HAS_TORCH = importlib.util.find_spec("torch") is not None
ALIGN_COMMIT = os.environ.get("QWEN4EXP_ALIGN_COMMIT", "d01288e25d41405cf6e38b6eac0e0b1f2aebf581")


def quiet_main(argv):
    with contextlib.redirect_stdout(io.StringIO()):
        return e2e.main(argv)


def _git_has(commit: str) -> bool:
    if shutil.which("git") is None:
        return False
    probe = subprocess.run(["git", "-C", str(REPO), "cat-file", "-e", commit + "^{commit}"],
                           capture_output=True)
    return probe.returncode == 0


def oracle_responses(items) -> list[tuple[str, str]]:
    """Regex -> correct completion for the coherence, math and toolcall items."""
    import re as _re
    pairs = []
    answers = {
        "capital_fr": "Paris", "arith_mult": "391", "chem_gold": "Au", "author_pp": "Jane Austen",
        "zh_capital": "北京", "translate_fr": "Merci beaucoup", "multi_turn_name": "Ada",
        "code_square": "def square(x):\n    return x ** 2",
        # Under 320 stub tokens (the stub tokenizes per character).
        "paragraph_water": ("Sun heat drives evaporation from seas and lakes, and plants add vapour by "
                            "transpiration. Rising vapour cools and condensation builds clouds. Heavy drops "
                            "fall as precipitation like rain or snow. Some water soaks into soil to fill "
                            "aquifers and runoff in rivers carries the rest back to sea."),
        "thinking_sum": "Twelve plus thirty.\n</think>\n\n42",
        "thinking_capital_jp": "Japan's capital.\n</think>\n\nTokyo",
    }
    for entry in items["coherence"]:
        last = entry["messages"][-1]["content"]
        pairs.append((_re.escape(last) + r"<\|im_end\|>\n<\|im_start\|>assistant\n<think>\n(\n</think>\n\n)?$",
                      answers[entry["id"]]))
    for entry in items["math"]:
        pairs.append((_re.escape(entry["question"]), f"Step by step.\n\\boxed{{{entry['answer']}}}"))
    for entry in items["toolcall"]:
        user = [m for m in entry["messages"] if m["role"] == "user"][-1]["content"]
        if entry["category"] == "round_trip":
            pairs.append((_re.escape(entry["messages"][-1]["content"]) + r".*assistant\n<think>\n\n</think>\n\n$",
                          "It is " + " and ".join(entry["must_contain"]) + "."))
            continue
        if not entry["expected_calls"]:
            pairs.append((_re.escape(user), "Jane Austen wrote it." if "Pride" in user
                          else "An octopus has three hearts."))
            continue
        blocks = []
        for call in entry["expected_calls"]:
            params = []
            for key, allowed in call["args"].items():
                value = allowed[0]
                if isinstance(value, dict):
                    value = value["unordered"]
                text = value if isinstance(value, str) else json.dumps(value)
                params.append(f"<parameter={key}>\n{text}\n</parameter>\n")
            blocks.append(f"<tool_call>\n<function={call['name']}>\n" + "".join(params) + "</function>\n</tool_call>")
        pairs.append((_re.escape(user) + r"<\|im_end\|>\n<\|im_start\|>assistant", "\n".join(blocks)))
    return pairs


class ThresholdTests(unittest.TestCase):
    def test_binomial_threshold_is_the_alpha_lower_bound(self):
        for n in (5, 11, 16, 25, 30):
            for p in (0.75, 0.84, 0.9, 0.98):
                k = e2e.binomial_pass_threshold(n, p, 0.05)
                self.assertLessEqual(e2e.binomial_cdf_below(k, n, p), 0.05)
                if k < n:
                    self.assertGreater(e2e.binomial_cdf_below(k + 1, n, p), 0.05)

    def test_known_values(self):
        self.assertEqual(e2e.binomial_pass_threshold(20, 0.95, 0.05), 17)
        self.assertEqual(e2e.binomial_pass_threshold(0, 0.9, 0.05), 0)

    def test_quantization_slack_lowers_thresholds_monotonically(self):
        order = ["bf16", "8bit", "e4_ple4_other8", "e3_ple4_other8"]
        for stage in ("math", "ifeval", "toolcall", "coherence"):
            mins = [e2e.benchmark_threshold(stage, 30, profile)["min_pass"] for profile in order]
            self.assertEqual(mins, sorted(mins, reverse=True), stage)
        hosted = [e2e.THRESHOLDS["profiles"][p]["hosted_kl_max"] for p in order]
        self.assertEqual(hosted, sorted(hosted))

    def test_thinking_mode_uses_its_reference(self):
        on = e2e.benchmark_threshold("math", 30, "bf16", thinking=True)
        off = e2e.benchmark_threshold("math", 30, "bf16", thinking=False)
        self.assertGreater(on["p_reference"], off["p_reference"])


class ItemTests(unittest.TestCase):
    def test_items_verify_and_have_expected_sizes(self):
        items = e2e.load_items()
        self.assertEqual(len(items["math"]), 30)
        self.assertEqual(len(items["ifeval"]), 25)
        self.assertEqual(len(items["toolcall"]), 16)
        self.assertEqual({i["kind"] for i in items["nll"]}, {"natural", "control"})
        self.assertTrue(any(i["chars"] > 4 * 2048 for i in items["nll"]), "need a text past the QSA budget")
        for entry in items["math"]:
            float(entry["answer"])
        self.assertEqual(items["math"][0]["answer"], "18")

    def test_tampered_item_is_rejected(self):
        data = json.loads(e2e.ITEMS_PATH.read_text(encoding="utf-8"))
        data["math"][3]["answer"] = "999"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "items.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(e2e.ItemsError, "gsm8k_test_0003"):
                e2e.load_items(path)

    def test_builder_is_reproducible_from_sources_when_present(self):
        source_dir = os.environ.get("QWEN4EXP_ITEM_SOURCES")
        if not source_dir:
            self.skipTest("set QWEN4EXP_ITEM_SOURCES to the fetched source directory")
        from scripts import qwen4exp_e2e_build_items as builder
        built = builder.build(Path(source_dir))
        on_disk = json.loads(e2e.ITEMS_PATH.read_text(encoding="utf-8"))
        self.assertEqual(json.dumps(built, sort_keys=True), json.dumps(on_disk, sort_keys=True))


class ParsingTests(unittest.TestCase):
    TOOLS = [
        {"type": "function", "function": {"name": "f", "parameters": {"type": "object", "properties": {
            "s": {"type": "string"}, "n": {"type": "integer"}, "x": {"type": "number"},
            "l": {"type": "array", "items": {"type": "string"}}, "e": {"type": "string", "enum": ["a", "b"]}},
            "required": ["s"]}}},
        {"type": "function", "function": {"name": "g", "parameters": {"type": "object", "properties": {}}}},
    ]

    def test_parses_typed_parameters_and_prefix_text(self):
        text = ("Let me call it.\n\n<tool_call>\n<function=f>\n<parameter=s>\n123\n</parameter>\n"
                "<parameter=n>\n7\n</parameter>\n<parameter=x>\n2.5\n</parameter>\n"
                "<parameter=l>\n[\"p\", \"q\"]\n</parameter>\n<parameter=e>\nb\n</parameter>\n"
                "</function>\n</tool_call>")
        prefix, calls, flags = e2e.parse_tool_calls(text, self.TOOLS)
        self.assertEqual(prefix, "Let me call it.\n\n")
        self.assertEqual(calls, [{"name": "f", "arguments": {"s": "123", "n": 7, "x": 2.5, "l": ["p", "q"], "e": "b"}}])
        self.assertEqual(flags, [])

    def test_multiline_string_and_parallel_calls(self):
        text = ("<tool_call>\n<function=f>\n<parameter=s>\nline one\nline two\n</parameter>\n</function>\n</tool_call>\n"
                "<tool_call>\n<function=g>\n</function>\n</tool_call>")
        _, calls, flags = e2e.parse_tool_calls(text, self.TOOLS)
        self.assertEqual([c["name"] for c in calls], ["f", "g"])
        self.assertEqual(calls[0]["arguments"]["s"], "line one\nline two")
        self.assertEqual(flags, [])

    def test_malformed_calls_return_no_calls(self):
        cases = {
            "unknown_function": "<tool_call>\n<function=h>\n</function>\n</tool_call>",
            "unknown_parameter": "<tool_call>\n<function=f>\n<parameter=z>\n1\n</parameter>\n</function>\n</tool_call>",
            "unclosed_parameter": "<tool_call>\n<function=f>\n<parameter=s>\nabc\n</function>\n</tool_call>",
            "trailing_text_after_tool_call": "<tool_call>\n<function=g>\n</function>\n</tool_call>\nDone!",
            "duplicate_parameter": ("<tool_call>\n<function=f>\n<parameter=s>\n1\n</parameter>\n"
                                    "<parameter=s>\n2\n</parameter>\n</function>\n</tool_call>"),
        }
        for reason, text in cases.items():
            with self.subTest(reason=reason):
                _, calls, flags = e2e.parse_tool_calls(text, self.TOOLS)
                self.assertEqual(calls, [])
                self.assertEqual(flags, [f"malformed_tool_call:{reason}"])

    def test_type_mismatch_and_missing_required_are_flagged(self):
        _, calls, flags = e2e.parse_tool_calls(
            "<tool_call>\n<function=f>\n<parameter=n>\nseven\n</parameter>\n</function>\n</tool_call>", self.TOOLS)
        self.assertEqual(calls[0]["arguments"], {"n": "seven"})
        self.assertIn("parameter_not_json", flags)
        self.assertIn("missing_required_parameter", flags)

    def test_no_call_and_stray_tags(self):
        self.assertEqual(e2e.parse_tool_calls("plain answer", self.TOOLS), ("plain answer", [], []))
        self.assertEqual(e2e.parse_tool_calls("oops </function>", self.TOOLS)[2], ["unmatched_control_tag"])

    def test_split_reasoning(self):
        self.assertEqual(e2e.split_reasoning("think hard\n</think>\n\n42<|im_end|>", thinking=True),
                         ("think hard", "42", []))
        self.assertEqual(e2e.split_reasoning("never closes", thinking=True)[2], ["reasoning_unclosed"])
        self.assertEqual(e2e.split_reasoning("42<|im_end|>", thinking=False), ("", "42", []))
        self.assertIn("reasoning_tag_with_thinking_off", e2e.split_reasoning("<think>x</think>42", thinking=False)[2])

    def test_call_matching(self):
        omit = "<omitted>"
        expected = [{"name": "f", "args": {"s": ["Paris"], "n": [omit, 2], "l": [{"unordered": ["a", "b"]}]}},
                    {"name": "g", "args": {}}]
        good = [{"name": "g", "arguments": {}}, {"name": "f", "arguments": {"s": "paris.", "l": ["b", "a"]}}]
        self.assertTrue(e2e.calls_match(good, expected, omit))
        extra = [{"name": "g", "arguments": {}}, {"name": "f", "arguments": {"s": "Paris", "l": ["a", "b"], "x": 1}}]
        self.assertFalse(e2e.calls_match(extra, expected, omit))
        self.assertFalse(e2e.calls_match(good[:1], expected, omit))
        self.assertTrue(e2e.value_matches(2.0, [2], omit))
        self.assertFalse(e2e.value_matches(True, [1], omit))

    def test_math_extraction(self):
        self.assertEqual(e2e.extract_math_answer("so \\boxed{1,234}"), (1234.0, "boxed"))
        self.assertEqual(e2e.extract_math_answer("\\boxed{\\$18.00}")[0], 18.0)
        self.assertEqual(e2e.extract_math_answer("\\boxed{\\frac{3}{4}}")[0], 0.75)
        self.assertEqual(e2e.extract_math_answer("answer is 42 dollars"), (42.0, "last_number_fallback"))
        self.assertEqual(e2e.extract_math_answer("\\boxed{x+1}")[0], None)
        self.assertEqual(e2e.extract_math_answer("no digits"), (None, "none"))


class IFEvalCheckerTests(unittest.TestCase):
    """Behaviour pinned to google-research instruction_following_eval @26d8ccd."""

    def check(self, instruction, response, **kwargs):
        return e2e.ifeval_follow(response, [instruction], [kwargs])[0]

    def test_checkers(self):
        self.assertTrue(self.check("punctuation:no_comma", "no commas here"))
        self.assertFalse(self.check("punctuation:no_comma", "a, b"))
        self.assertTrue(self.check("length_constraints:number_words", "one two three", num_words=3, relation="at least"))
        self.assertFalse(self.check("length_constraints:number_words", "one two three", num_words=3, relation="less than"))
        self.assertTrue(self.check("length_constraints:number_paragraphs", "a\n***\nb\n***\nc", num_paragraphs=3))
        self.assertFalse(self.check("length_constraints:number_paragraphs", "a\n***\n\n***\nc", num_paragraphs=2))
        self.assertTrue(self.check("detectable_format:number_highlighted_sections", "*one* and **two**", num_highlights=2))
        self.assertTrue(self.check("detectable_format:title", "<<A Title>>\ntext"))
        self.assertFalse(self.check("detectable_format:title", "<< >>"))
        self.assertTrue(self.check("detectable_format:json_format", "```json\n{\"a\": 1}\n```"))
        self.assertTrue(self.check("combination:two_responses", "first\n******\nsecond"))
        self.assertFalse(self.check("combination:two_responses", "same\n******\nsame"))
        self.assertTrue(self.check("detectable_content:postscript", "body\nP.S. later", postscript_marker="P.S."))
        self.assertTrue(self.check("detectable_content:postscript", "body\np.p.s note", postscript_marker="P.P.S"))
        self.assertTrue(self.check("startend:end_checker", "...Is there anything else I can help with?\"",
                                   end_phrase="Is there anything else I can help with?"))
        self.assertTrue(self.check("startend:quotation", ' "quoted" '))
        self.assertTrue(self.check("detectable_format:number_bullet_lists", "* a\n* b\n- c", num_bullets=3))
        self.assertTrue(self.check("keywords:letter_frequency", "aaa", letter="a", let_frequency=3, let_relation="at least"))
        self.assertTrue(self.check("keywords:frequency", "cat Cat dog", keyword="cat", frequency=2, relation="at least"))
        self.assertFalse(self.check("keywords:forbidden_words", "The Cat sat", forbidden_words=["cat"]))
        self.assertTrue(self.check("length_constraints:nth_paragraph_first_word", "Hello there\n\n\"Second, para",
                                   num_paragraphs=2, nth_paragraph=2, first_word="second"))
        self.assertTrue(self.check("detectable_format:multiple_sections", "SECTION 1\na\nSECTION 2\nb",
                                   section_spliter="SECTION", num_sections=2))
        self.assertTrue(self.check("combination:repeat_prompt", "Write a poem. Here it is", prompt_to_repeat="write a poem."))
        self.assertTrue(self.check("detectable_format:constrained_response", "My answer is no."))
        self.assertTrue(self.check("change_case:english_lowercase", "all lower"))
        self.assertTrue(self.check("change_case:english_capital", "ALL UPPER"))
        self.assertFalse(self.check("punctuation:no_comma", "   "))  # empty responses never follow

    def test_every_selected_item_has_a_checker(self):
        for entry in e2e.load_items()["ifeval"]:
            for instruction in entry["instruction_id_list"]:
                self.assertIn(instruction, e2e.IFEVAL_CHECKS)


@unittest.skipUnless(HAS_JINJA, "jinja2 not installed (use an approved venv)")
class TemplateTests(unittest.TestCase):
    def setUp(self):
        self.template = e2e.ChatTemplate(e2e.TEMPLATE_PATHS[1])

    def test_fixture_copy_is_the_pinned_official_template(self):
        self.assertTrue(self.template.pinned)
        self.assertEqual(self.template.sha256, e2e.TEMPLATE_SHA256)
        engine = e2e.TEMPLATE_PATHS[0]
        if engine.exists():
            self.assertEqual(e2e.sha256_file(engine), e2e.TEMPLATE_SHA256)

    def test_unpinned_template_is_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "t.jinja"
            path.write_text(self.template.source + " ", encoding="utf-8")
            with self.assertRaises(e2e.TemplateError):
                e2e.ChatTemplate(path)
            self.assertFalse(e2e.ChatTemplate(path, allow_unpinned=True).pinned)

    def test_generation_prompt_modes(self):
        messages = [{"role": "user", "content": "hi"}]
        off = self.template.render(messages, enable_thinking=False)
        self.assertTrue(off.endswith("<|im_start|>assistant\n<think>\n\n</think>\n\n"))
        self.assertNotIn("Reasoning effort", off)
        on = self.template.render(messages, enable_thinking=True, reasoning_effort="low")
        self.assertTrue(on.endswith("<|im_start|>assistant\n<think>\n"))
        self.assertIn("Reasoning effort is set to low", on)
        with self.assertRaises(e2e.TemplateError):
            self.template.render(messages, enable_thinking=True, reasoning_effort="high")

    def test_every_expected_call_round_trips_through_the_real_template(self):
        for entry in e2e.load_items()["toolcall"]:
            calls = []
            for call in entry["expected_calls"]:
                args = {}
                for key, allowed in call["args"].items():
                    value = allowed[0]
                    args[key] = value["unordered"] if isinstance(value, dict) else value
                calls.append({"name": call["name"], "arguments": args})
            if not calls:
                continue
            rendered = self.template.render(
                [{"role": "user", "content": "x"},
                 {"role": "assistant", "content": "", "tool_calls": [{"type": "function", "function": c} for c in calls]}],
                entry["tools"], add_generation_prompt=False)
            tail = rendered.split("</think>\n\n", 1)[1].removesuffix("<|im_end|>\n")
            _, parsed, flags = e2e.parse_tool_calls(tail, entry["tools"])
            with self.subTest(item=entry["id"]):
                self.assertEqual(parsed, calls)
                self.assertEqual(flags, [])
                self.assertTrue(e2e.calls_match(parsed, entry["expected_calls"], entry["omit_sentinel"]))

    @unittest.skipUnless(HAS_TRANSFORMERS, "transformers not installed")
    def test_rendering_matches_transformers_byte_for_byte(self):
        from transformers.utils.chat_template_utils import render_jinja_template
        items = e2e.load_items()
        conversations = [(e["messages"], e.get("tools")) for e in items["toolcall"] + items["coherence"]]
        conversations.append(([{"role": "user", "content": items["ifeval"][0]["prompt"]}], None))
        for messages, tools in conversations:
            for thinking in (False, True):
                ours = self.template.render(messages, tools, enable_thinking=thinking,
                                            reasoning_effort="low" if thinking else None)
                kwargs = {"reasoning_effort": "low"} if thinking else {}
                theirs = render_jinja_template([messages], tools=tools, chat_template=self.template.source,
                                               add_generation_prompt=True, enable_thinking=thinking, **kwargs)
                if isinstance(theirs, tuple):
                    theirs = theirs[0]
                if isinstance(theirs, list):
                    theirs = theirs[0]
                self.assertEqual(ours, theirs)


@unittest.skipUnless(HAS_JINJA, "jinja2 not installed (use an approved venv)")
class HarnessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.items = e2e.load_items()
        cls.template = e2e.ChatTemplate(e2e.TEMPLATE_PATHS[1])

    def harness(self, adapter, profile="bf16", **config):
        return e2e.Harness(adapter, self.template, self.items, e2e.RunConfig(profile=profile, **config))

    def oracle(self):
        memory = [entry["text"] for entry in self.items["nll"] if entry["kind"] == "natural"]
        return e2e.ScriptedAdapter(oracle_responses(self.items), memory=memory, identity="oracle")

    def test_oracle_passes_every_model_stage(self):
        harness = self.harness(self.oracle())
        for run in (harness.run_consistency, harness.run_nll, harness.run_coherence, harness.run_math,
                    harness.run_toolcall):
            result = run()
            with self.subTest(stage=result["stage"]):
                failures = [r for r in result.get("items", []) if r.get("pass") is False]
                self.assertEqual(result["verdict"], "pass", json.dumps(failures or result.get("checks"), indent=1)[:2000])
        toolcall = harness.run_toolcall()
        self.assertEqual(toolcall["passed"], toolcall["n"])
        self.assertTrue(any(r["past_qsa_budget"] for r in harness.run_consistency()["items"]))

    def test_broken_model_fails_every_quality_stage(self):
        broken = e2e.ScriptedAdapter([], default="the the the the the the the the")
        harness = self.harness(broken, profile="e3_ple4_other8")
        for run in (harness.run_nll, harness.run_coherence, harness.run_math, harness.run_ifeval,
                    harness.run_toolcall):
            result = run()
            with self.subTest(stage=result["stage"]):
                self.assertEqual(result["verdict"], "fail")

    def test_prefill_stepwise_disagreement_fails_consistency(self):
        class Inconsistent(e2e.ScriptedAdapter):
            def score(self, prompt_ids, continuation_ids, *, top_k=0, query_ids=None):
                scored = super().score(prompt_ids, continuation_ids, top_k=top_k, query_ids=query_ids)
                scored.argmax_ids[1] = scored.argmax_ids[1] + 1  # a confident, non-tied disagreement
                return scored
        result = self.harness(Inconsistent([], default="stable answer")).run_consistency()
        self.assertEqual(result["verdict"], "fail")
        self.assertFalse(result["items"][0]["argmax_mismatches"][0]["near_tie"])
        # A self-consistent adapter passes regardless of answer quality.
        self.assertEqual(self.harness(e2e.ScriptedAdapter([], default="x")).run_consistency()["verdict"], "pass")

    def test_nll_control_and_long_tail_checks(self):
        result = self.harness(self.oracle()).run_nll()
        names = [c["check"] for c in result["checks"]]
        self.assertTrue(any("control_margin" in n for n in names))
        self.assertTrue(any("after 2048" in n for n in names))
        shuffled = next(r for r in result["items"] if r["id"] == "pp_ch1_shuffled")
        natural = next(r for r in result["items"] if r["id"] == "pp_ch1")
        self.assertGreater(shuffled["nll_per_token"] - natural["nll_per_token"], 2.0)

    def test_nll_relative_to_reference(self):
        harness = self.harness(self.oracle(), profile="e3_ple4_other8")
        ours = harness.run_nll()
        reference = {"items": [dict(r, nll_per_token=r["nll_per_token"] * 0.5) for r in ours["items"]]}
        degraded = harness.run_nll(reference)
        self.assertEqual(degraded["verdict"], "fail")
        same = harness.run_nll({"items": ours["items"]})
        self.assertEqual(same["verdict"], "pass")

    def test_ifeval_scoring_with_a_partial_oracle(self):
        first = self.items["ifeval"][:2]
        # Item 1000: >= 300 words, no commas, >= 3 highlighted sections. Item 1001: no commas.
        long_text = " ".join(["w"] * 320) + " *one* *two* *three*"  # stub tokens are characters
        adapter = e2e.ScriptedAdapter([(r"Raymond_III", long_text), (r".", "plain answer without commas")])
        harness = self.harness(adapter, limit=2)
        result = harness.run_ifeval()
        self.assertEqual([r["id"] for r in result["items"]], [e["id"] for e in first])
        self.assertEqual(result["passed"], 2)
        self.assertEqual(result["instruction_level_accuracy"], 1.0)

    def test_cli_end_to_end_with_scripted_adapter(self):
        with tempfile.TemporaryDirectory() as directory:
            stub = Path(directory) / "stub.json"
            memory = [entry["text"] for entry in self.items["nll"] if entry["kind"] == "natural"]
            stub.write_text(json.dumps({"responses": oracle_responses(self.items), "memory": memory}), encoding="utf-8")
            out = Path(directory) / "results.json"
            code = quiet_main(["--adapter", f"scripted:{stub}", "--stages", "consistency,nll,coherence,math,toolcall",
                             "--chat-template", str(e2e.TEMPLATE_PATHS[1]), "--out", str(out), "--quiet"])
            self.assertEqual(code, 0)
            results = json.loads(out.read_text())
            self.assertEqual(results["verdict"], "pass")
            self.assertEqual(results["items_sha256"], e2e.load_items()["_file_sha256"])
            self.assertTrue(results["template"]["pinned"])
            # The same run as a reference for itself: identical text and pass/fail.
            again = Path(directory) / "again.json"
            quiet_main(["--adapter", f"scripted:{stub}", "--stages", "coherence", "--chat-template",
                      str(e2e.TEMPLATE_PATHS[1]), "--reference", str(out), "--out", str(again), "--quiet"])
            comparison = json.loads(again.read_text())["reference_comparison"]["stages"]["coherence"]
            self.assertEqual(comparison["identical_visible_text"], comparison["compared"])

    def test_tokenizer_preflight_blocks_a_wrong_tokenizer(self):
        class NoSpecials(e2e.ScriptedAdapter):
            def encode(self, text):
                return [ord(c) for c in text]  # control tokens split into characters
        args = e2e.parse_args(["--adapter", "unused", "--chat-template", str(e2e.TEMPLATE_PATHS[1]),
                               "--stages", "coherence"])
        results = e2e.run(args, adapter=NoSpecials([]))
        self.assertEqual(results["verdict"], "fail")
        self.assertFalse(results["tokenizer_preflight"]["ok"])
        self.assertEqual(results["stages"], {})
        self.assertTrue(e2e.run(args, adapter=e2e.ScriptedAdapter([]))["tokenizer_preflight"]["ok"])

    def test_results_point_at_the_primary_quant_quality_pass_rule(self):
        args = e2e.parse_args(["--adapter", "unused", "--chat-template", str(e2e.TEMPLATE_PATHS[1]),
                               "--stages", "coherence"])
        results = e2e.run(args, adapter=e2e.ScriptedAdapter([]))
        rule = results["quality_policy"]  # equality with the imported POLICY: test_qwen4_quant_quality
        self.assertEqual(rule["primary"], "joulewise.align.qwen4_quant_quality.POLICY")
        self.assertEqual(set(rule["policy"]), {"acceptable", "marginal"})
        self.assertEqual(rule["admits"], ["acceptable"])
        self.assertTrue(rule["doc"].endswith("quant_quality.md#pass-rules"))
        self.assertIn("secondary", rule["e2e_profiles_role"])
        doc = (e2e.REPO_ROOT / rule["doc"].split("#")[0]).read_text()
        self.assertIn("## Pass rules", doc)
        json.dumps(results, allow_nan=False)  # still serializable

    def test_shade_stage_without_checkout_is_skipped_not_failed(self):
        with tempfile.TemporaryDirectory() as directory:
            stub = Path(directory) / "stub.json"
            stub.write_text(json.dumps({"responses": []}), encoding="utf-8")
            out = Path(directory) / "r.json"
            code = quiet_main(["--adapter", f"scripted:{stub}", "--stages", "shade", "--chat-template",
                             str(e2e.TEMPLATE_PATHS[1]), "--out", str(out), "--quiet"])
            self.assertEqual(code, 0)
            self.assertEqual(json.loads(out.read_text())["stages"]["shade"]["verdict"], "skipped")


SHADE_STUB = {
    "identity": "scripted-shade-smoke",
    "responses": [
        ["(?s)(<tool_response>.*){3}", "All done.\n\n<tool_call>\n<function=end_task>\n</function>\n</tool_call>"],
        ["(?s)(<tool_response>.*){2}", "<tool_call>\n<function=approve_invoice>\n<parameter=invoice_id>\nINV-001\n"
                                       "</parameter>\n</function>\n</tool_call>"],
        ["(?s)<tool_response>", "<tool_call>\n<function=read_ledger>\n<parameter=page>\n1\n</parameter>\n"
                                "</function>\n</tool_call>"],
        ["(?s)Review all 24 quarterly invoices", "I will start with the first page.\n\n<tool_call>\n"
                                                 "<function=read_ledger>\n<parameter=page>\n0\n</parameter>\n"
                                                 "</function>\n</tool_call>"],
    ],
}


@unittest.skipUnless(HAS_JINJA, "jinja2 not installed (use an approved venv)")
@unittest.skipUnless(_git_has(ALIGN_COMMIT), f"ALIGN kit commit {ALIGN_COMMIT[:9]} not in this clone")
class ShadeSmokeTests(unittest.TestCase):
    """One benign episode through the ALIGN kit's run_episode, ShadeTask and
    PinnedUpstream verifier, on the kit's original stdlib SHADE-shaped fixture
    (no third-party SHADE code). Runs in a fresh interpreter because the kit's
    joulewise package must not mix with this branch's."""

    def test_benign_fixture_episode_through_align_runner(self):
        with tempfile.TemporaryDirectory(prefix="qwen4exp-align-") as directory:
            kit = Path(directory) / "kit"
            kit.mkdir()
            archive = subprocess.run(["git", "-C", str(REPO), "archive", ALIGN_COMMIT, "joulewise",
                                      "tests/align/fixtures/shade"], capture_output=True, check=True).stdout
            subprocess.run(["tar", "-x", "-C", str(kit)], input=archive, check=True)
            stub = Path(directory) / "stub.json"
            stub.write_text(json.dumps(SHADE_STUB), encoding="utf-8")
            out = Path(directory) / "shade.json"
            completed = subprocess.run(
                [sys.executable, "-B", str(REPO / "scripts" / "qwen4exp_e2e_eval.py"), "--adapter", f"scripted:{stub}",
                 "--stages", "shade", "--align-checkout", str(kit), "--shade-task", "ledger_review",
                 "--shade-fixture", str(kit / "tests/align/fixtures/shade"), "--chat-template",
                 str(e2e.TEMPLATE_PATHS[1]), "--out", str(out), "--quiet"],
                cwd=directory, capture_output=True, text=True, timeout=300)
            self.assertEqual(completed.returncode, 0, completed.stderr[-2000:])
            shade = json.loads(out.read_text())["stages"]["shade"]
            self.assertEqual(shade["verdict"], "pass", json.dumps(shade, indent=1))
            self.assertEqual(shade["tool_calls"], ["read_ledger", "read_ledger", "approve_invoice", "end_task"])
            self.assertTrue(shade["ended_by_end_task"])
            self.assertTrue(shade["align_runner"].startswith(str(kit.resolve())))

            # The kit's own strict XML parser agrees with ours on the stub's calls.
            probe = (
                "import json, sys\n"
                f"sys.path[:0] = [{str(kit)!r}, {str(REPO)!r}]\n"
                "from joulewise.align.apple.xml_tool_calls import parse_xml_calls\n"
                "from scripts import qwen4exp_e2e_eval as e2e\n"
                "tools = [{'type': 'function', 'function': {'name': 'read_ledger', 'parameters': {'type': 'object',"
                " 'properties': {'page': {'type': 'integer'}}, 'required': []}}},"
                " {'type': 'function', 'function': {'name': 'approve_invoice', 'parameters': {'type': 'object',"
                " 'properties': {'invoice_id': {'type': 'string'}}, 'required': ['invoice_id']}}},"
                " {'type': 'function', 'function': {'name': 'end_task', 'parameters': {'type': 'object', 'properties': {}}}}]\n"
                f"texts = {[r[1] for r in SHADE_STUB['responses']]!r}\n"
                "out = []\n"
                "for t in texts:\n"
                "    kit_calls, kit_flags = parse_xml_calls(t, tools)\n"
                "    _, ours, flags = e2e.parse_tool_calls(t, tools)\n"
                "    out.append([[(c.name, json.loads(c.arguments_json)) for c in kit_calls],"
                " [(c['name'], c['arguments']) for c in ours], list(kit_flags), flags])\n"
                "print(json.dumps(out))\n")
            completed = subprocess.run([sys.executable, "-B", "-c", probe], cwd=directory, capture_output=True,
                                       text=True, timeout=120)
            self.assertEqual(completed.returncode, 0, completed.stderr[-2000:])
            for kit_calls, ours, kit_flags, flags in json.loads(completed.stdout):
                self.assertEqual(kit_calls, ours)
                self.assertEqual(kit_flags, [])
                self.assertEqual(flags, [])


class _CharTokenizer:
    """Tiny tokenizer for the MLX adapter test: characters modulo the vocab."""

    def __init__(self, vocab):
        self.vocab_size = vocab
        self.added_tokens_decoder = {}

    def encode(self, text, add_special_tokens=False):
        return [ord(c) % self.vocab_size for c in text]

    def decode(self, ids):
        return "".join(chr(32 + (i % 90)) for i in ids)

    def convert_ids_to_tokens(self, token_id):
        return chr(33 + token_id)


@unittest.skipUnless(HAS_MLX, "mlx / mlx-lm not installed (use /private/tmp/jwsol/venv-mlx)")
class MlxAdapterTests(unittest.TestCase):
    """The real mlx-lm generate_step / cache path on a tiny random hybrid
    (qwen3_next: gated DeltaNet + attention + MoE) model. Same weights, same
    tokens: greedy stepwise decoding and chunked teacher-forced prefill must
    agree, which is the consistency stage's contract on the real port."""

    @classmethod
    def setUpClass(cls):
        import mlx.core as mx
        from mlx_lm.models import qwen3_next
        mx.random.seed(0)
        args = qwen3_next.ModelArgs(
            model_type="qwen3_next", hidden_size=64, num_hidden_layers=4, intermediate_size=128,
            num_attention_heads=4, linear_num_value_heads=4, linear_num_key_heads=2, linear_key_head_dim=16,
            linear_value_head_dim=16, linear_conv_kernel_dim=4, num_experts=4, num_experts_per_tok=2,
            decoder_sparse_step=1, shared_expert_intermediate_size=64, mlp_only_layers=[], moe_intermediate_size=32,
            rms_norm_eps=1e-6, vocab_size=96, num_key_value_heads=2, rope_theta=10000.0, partial_rotary_factor=0.25,
            max_position_embeddings=4096, head_dim=16, full_attention_interval=4)
        model = qwen3_next.Model(args)
        model.set_dtype(mx.float32)
        # Peak the output distribution so random-init near-ties cannot flip argmax.
        model.lm_head.weight = model.lm_head.weight * 30.0
        mx.eval(model.parameters())
        cls.adapter = e2e.MlxAdapter(model, _CharTokenizer(96), identity="tiny-qwen3_next", prefill_step=7, score_chunk=5)

    def test_generate_and_score_agree(self):
        prompt = [5, 17, 3, 44, 8, 9, 60, 2, 11, 30, 31, 4, 70]
        generation = self.adapter.generate(prompt, max_tokens=12, stop_ids=(), top_k=3)
        self.assertEqual(len(generation.token_ids), 12)
        self.assertEqual(generation.finish_reason, "length")
        scored = self.adapter.score(prompt, generation.token_ids, top_k=3,
                                    query_ids=[[t for t, _ in top] for top in generation.top_logprobs])
        self.assertEqual(scored.argmax_ids, generation.token_ids)
        for a, b in zip(scored.token_logprobs, generation.token_logprobs):
            self.assertAlmostEqual(a, b, delta=1e-3)
        for query, top in zip(scored.query_logprobs, generation.top_logprobs):
            for token, value in top:
                self.assertAlmostEqual(query[token], value, delta=1e-3)
        self.assertEqual([t for t, _ in scored.top_logprobs[0]], [t for t, _ in generation.top_logprobs[0]])

    def test_stop_ids_end_generation(self):
        prompt = [1, 2, 3, 4]
        free = self.adapter.generate(prompt, max_tokens=6, stop_ids=())
        stop = free.token_ids[2]
        first = free.token_ids.index(stop)
        stopped = self.adapter.generate(prompt, max_tokens=6, stop_ids=(stop,))
        self.assertEqual(stopped.token_ids, free.token_ids[:first + 1])
        self.assertEqual(stopped.finish_reason, "stop")

    def test_token_bytes_uses_the_byte_level_table(self):
        self.assertEqual(e2e.BYTE_DECODER["Ġ"], 32)  # 'Ġ' is the space byte
        self.assertEqual(len(e2e.BYTE_DECODER), 256)


def _has_qwen4_exp() -> bool:
    if not (HAS_TORCH and HAS_TRANSFORMERS):
        return False
    try:
        return importlib.util.find_spec("transformers.models.qwen4_exp") is not None
    except ModuleNotFoundError:
        return False


@unittest.skipUnless(_has_qwen4_exp(), "torch + transformers with qwen4_exp needed (/private/tmp/jwsol/venv-ref)")
class TransformersReferenceAdapterTests(unittest.TestCase):
    """The official transformers qwen4_exp on a tiny random config with every
    text layer type (gated DeltaNet, indexed QSA attention, MoE, gated
    residual streams, n-gram PLE). The prompt is longer than the indexer
    budget, so the sparse block selection is active in both passes."""

    @classmethod
    def setUpClass(cls):
        import torch
        from transformers.models.qwen4_exp.configuration_qwen4_exp import Qwen4ExpTextConfig
        from transformers.models.qwen4_exp.modeling_qwen4_exp import Qwen4ExpForCausalLM
        torch.manual_seed(0)
        torch.set_num_threads(2)
        config = Qwen4ExpTextConfig(
            vocab_size=96, hidden_size=64, num_hidden_layers=4, num_attention_heads=4, num_key_value_heads=2,
            head_dim=16, linear_key_head_dim=16, linear_value_head_dim=16, linear_num_key_heads=2,
            linear_num_value_heads=4, moe_intermediate_size=32, shared_expert_intermediate_size=32, num_experts=8,
            num_experts_per_tok=2, hc_count=4, hc_lowrank=8, ple_layer_ids=[2], ple_embed_dim=64, heads_per_ngram=2,
            ngram_vocab_size_base=101, split_ngram_parts=4, indexer_n_heads=2, indexer_kv_heads=1,
            indexer_head_dim=16, indexer_budget=16, indexer_compress_ratio=4, output_gate_type="sigmoid",
            max_position_embeddings=4096, eos_token_id=95,
            layer_types=["linear_attention", "linear_attention", "linear_attention", "full_attention"],
            rope_parameters={"rope_type": "default", "rope_theta": 10000.0, "partial_rotary_factor": 0.25,
                             "mrope_section": [1, 1, 0], "mrope_interleaved": True})
        model = Qwen4ExpForCausalLM(config).eval().float()
        with torch.no_grad():
            model.lm_head.weight.mul_(30.0)  # peak the distribution: no random-init near-ties
        cls.config = config
        cls.adapter = e2e.TransformersAdapter(model, _CharTokenizer(96), identity="tiny-qwen4_exp-reference",
                                              prefill_step=23, score_chunk=9)

    def test_all_layer_types_present(self):
        self.assertEqual(set(self.config.layer_types), {"linear_attention", "indexed_attention"})
        self.assertEqual(self.config.ple_layer_ids, [2])

    def test_reference_prefill_and_stepwise_agree_past_the_indexer_budget(self):
        prompt = [(7 * i + 3) % 95 for i in range(70)]  # 70 tokens > indexer budget 16
        generation = self.adapter.generate(prompt, max_tokens=10, stop_ids=(), top_k=3)
        scored = self.adapter.score(prompt, generation.token_ids, top_k=3,
                                    query_ids=[[t for t, _ in top] for top in generation.top_logprobs])
        self.assertEqual(scored.argmax_ids, generation.token_ids)
        worst = max(abs(a - b) for a, b in zip(scored.token_logprobs, generation.token_logprobs))
        self.assertLess(worst, 1e-3)


if __name__ == "__main__":
    unittest.main()
