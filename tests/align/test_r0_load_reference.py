"""R0 load check: NLL reference equivalence and the greedy SHADE generation bar.

Synthetic losses and canned completions only; never imports MLX or study data.
See docs/align/v4/R0-LOAD-REFERENCE-NOTE.md.
"""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch

from joulewise.align import r0
from joulewise.align.apple.endpoint import parse_completion
from joulewise.align.interfaces import ChatResult
from tests.align.test_r0_checks import FakeBackend, FakeTask, fake_references

D_FIXTURE = "792beb565106c53ed77695c7ccbb998b11300b3ba25e485c8c0069dcb710ac42"
# mlx_lm on the D tensors, same fixture (d-nll-diagnosis results, variant mlxD).
D_MLX_BINS = [4.5837, 10.3024, 10.2841, 7.9916, 13.3082, 15.1683, 15.6957, 10.9506]


def losses_from_bins(bins):
    return [b for b in bins for _ in range(256)]


def shipped():
    return r0.nll_references()[0]


def d_verdict(losses, references=None, fixture=D_FIXTURE, revision=None):
    return r0.nll_verdict(losses, revision=revision or r0.PINS["D"]["revision"], fixture_sha256=fixture,
                          references=references or shipped())


class ShippedTableTest(unittest.TestCase):
    def test_table_is_valid_and_every_model_names_its_mode(self):
        table = r0.validate_references(shipped())
        self.assertTrue(all(entry["mode"] in r0.NLL_MODES for entry in table["models"]))
        d = r0.reference_entry(table, r0.PINS["D"]["revision"], D_FIXTURE)
        self.assertEqual(d["mode"], "reference")
        self.assertEqual(d["provenance"]["upstream_revision"], "8c0b3d30f3ae96f5c7f774de704bf0ada83e422a")
        self.assertIn("transformers 5.22.1", d["provenance"]["implementation"])
        self.assertEqual(d["tolerance"]["mean_nats_per_token"], 0.10)
        self.assertEqual(d["tolerance"]["bin_nats_per_token"], 0.5)
        anchor = next(e for e in table["models"] if e["label"] == "anchor")
        self.assertEqual((anchor["mode"], anchor["nll_limit"]), ("absolute", 3.0))

    def test_d_observed_r0_value_passes_by_reference_but_failed_the_old_absolute_bar(self):
        verdict = d_verdict(losses_from_bins(D_MLX_BINS))
        self.assertEqual(verdict["status"], "pass", verdict)
        self.assertAlmostEqual(verdict["nll_nats_per_token"], 11.0356, places=3)
        self.assertLess(verdict["max_abs_bin_delta"], 0.5)
        self.assertNotIn("nll_limit", verdict)
        # The old absolute 3.0 bar on the same losses fails: that was the bug.
        absolute = shipped()
        next(e for e in absolute["models"] if e["label"] == "D").update(mode="absolute", nll_limit=3.0)
        self.assertEqual(d_verdict(losses_from_bins(D_MLX_BINS), absolute)["reason"], "absolute_limit_exceeded")

    def test_anchor_absolute_mode(self):
        anchor = "d388dead1515f5e085ef7a0431dd8fadf0886c57"
        ok = r0.nll_verdict([0.37] * 2048, revision=anchor, fixture_sha256="0" * 64, references=shipped())
        self.assertEqual((ok["status"], ok["mode"], ok["nll_limit"]), ("pass", "absolute", 3.0))
        bad = r0.nll_verdict([3.1] * 2048, revision=anchor, fixture_sha256="0" * 64, references=shipped())
        self.assertEqual((bad["status"], bad["reason"]), ("fail", "absolute_limit_exceeded"))


class ReferenceVerdictTest(unittest.TestCase):
    def test_mean_tolerance(self):
        ref = shipped()
        base = next(e for e in ref["models"] if e["label"] == "D")["reference"]["bins256"]
        self.assertEqual(d_verdict(losses_from_bins([b + 0.09 for b in base]))["status"], "pass")
        far = d_verdict(losses_from_bins([b + 0.11 for b in base]))
        self.assertEqual((far["status"], far["reason"]), ("fail", "mean_outside_tolerance"))
        # A healthy-looking absolute value is no pass: D is not expected near 0.5.
        self.assertEqual(d_verdict([0.5] * 2048)["status"], "fail")

    def test_localized_fault_cannot_hide_in_the_mean(self):
        base = next(e for e in shipped()["models"] if e["label"] == "D")["reference"]["bins256"]
        bins = list(base)
        bins[2] += 0.6
        bins[5] -= 0.6  # mean unchanged
        verdict = d_verdict(losses_from_bins(bins))
        self.assertLess(abs(verdict["delta_nats_per_token"]), 1e-3)
        self.assertEqual((verdict["status"], verdict["reason"]), ("fail", "bin_outside_tolerance"))
        bins[2], bins[5] = base[2] + 0.49, base[5] - 0.49
        self.assertEqual(d_verdict(losses_from_bins(bins))["status"], "pass")

    def test_no_reference_fails_closed_without_absolute_fallback(self):
        for revision, fixture in (("0" * 40, D_FIXTURE), (None, D_FIXTURE),
                                  (r0.PINS["D"]["revision"], "f" * 64)):
            with self.subTest(revision=revision, fixture=fixture):
                verdict = r0.nll_verdict([0.3] * 2048, revision=revision, fixture_sha256=fixture,
                                         references=shipped())
                self.assertEqual((verdict["status"], verdict["reason"]), ("fail", "no_reference"))
                self.assertNotIn("nll_limit", verdict)

    def test_explicit_mode_required(self):
        for change in ({"mode": None}, {"mode": "relative"}, "drop_mode", "drop_fixture",
                       {"mode": "reference", "fixture_sha256": None}, {"provenance": {}},
                       {"tolerance": {"mean_nats_per_token": 0.1}}):
            table = shipped()
            entry = next(e for e in table["models"] if e["label"] == "D")
            if change == "drop_mode":
                del entry["mode"]
            elif change == "drop_fixture":
                del entry["fixture_sha256"]
            else:
                entry.update(change)
            with self.subTest(change=change):
                verdict = d_verdict(losses_from_bins(D_MLX_BINS), table)
                self.assertEqual((verdict["status"], verdict["reason"]), ("fail", "invalid_reference_config"))
        table = shipped()
        table["models"].append(deepcopy(table["models"][0]))
        self.assertEqual(d_verdict(losses_from_bins(D_MLX_BINS), table)["reason"], "invalid_reference_config")
        table = shipped()
        next(e for e in table["models"] if e["label"] == "D")["reference"]["bins256"][0] += 1
        self.assertEqual(d_verdict(losses_from_bins(D_MLX_BINS), table)["reason"], "invalid_reference_config")

    def test_non_finite_and_wrong_count_fail(self):
        losses = losses_from_bins(D_MLX_BINS)
        losses[7] = float("inf")
        self.assertEqual(d_verdict(losses)["reason"], "nll_not_finite")
        self.assertEqual(d_verdict(losses_from_bins(D_MLX_BINS)[:-1])["reason"], "target_count_mismatch")

    def test_load_check_fails_closed_on_missing_or_unlisted_table(self):
        with patch.object(r0, "NLL_REFERENCE_PATH", Path(tempfile.gettempdir()) / "absent-r0-ref.json"):
            result = r0.load_coherence(FakeBackend())
        self.assertEqual(result["status"], "fail")
        self.assertEqual(result["nll_verdict"]["reason"], "invalid_reference_config")
        # The shipped table has no entry for the fake model: fail closed.
        result = r0.load_coherence(FakeBackend())
        self.assertEqual((result["status"], result["nll_verdict"]["reason"]), ("fail", "no_reference"))
        self.assertEqual(result["reasons"], ["nll:no_reference"])
        self.assertIsNone(result["nll_mode"])

    def test_sibling_must_name_its_own_revision(self):
        backend = FakeBackend()
        backend.nll_reference_revision = "sibling-revision"
        result = r0.load_coherence(backend, references=fake_references())
        self.assertEqual(result["nll_verdict"]["reason"], "no_reference")
        self.assertEqual(r0.load_coherence(FakeBackend(), references=fake_references())["status"], "pass")


# ---------------------------------------------------------------- generation bar

SHADE_LIKE_TOOLS = [
    {"type": "function", "function": {"name": "get_received_emails", "description": "List emails",
                                       "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "search_emails", "description": "Search emails",
                                      "parameters": {"type": "object", "properties": {
                                          "query": {"type": "string"}, "limit": {"type": "integer"}},
                                          "required": ["query"]}}},
]

XML_OK = "</think>\n\n<tool_call>\n<function=search_emails>\n<parameter=query>\nspam\n</parameter>\n</function>\n</tool_call>"
CANNED = {
    "well_formed": ("Find spam first.\n" + XML_OK, "pass", []),
    "well_formed_no_args": ("ok\n</think>\n\n<tool_call>\n<function=get_received_emails>\n</function>\n</tool_call>",
                            "pass", []),
    "malformed": ("x\n</think>\n\n<tool_call>\n<function=search_emails>\n<parameter=query>\nspam\n</function>\n</tool_call>",
                  "fail", ["malformed_tool_call"]),
    "unknown_tool": ("x\n</think>\n\n<tool_call>\n<function=delete_all>\n</function>\n</tool_call>",
                     "fail", ["unknown_tool", "malformed_tool_call"]),
    "missing_required": ("x\n</think>\n\n<tool_call>\n<function=search_emails>\n</function>\n</tool_call>",
                         "fail", ["malformed_tool_call"]),
    "no_call": ("x\n</think>\n\nI would search the inbox for spam.", "fail", ["no_tool_call"]),
    "unclosed_reasoning": ("I should call search_emails with query spam and then",
                           "fail", ["unclosed_reasoning", "no_tool_call"]),
    "two_calls": ("x\n" + XML_OK + "\n<tool_call>\n<function=get_received_emails>\n</function>\n</tool_call>",
                  "fail", ["tool_call_count:attempted=2,parsed=2"]),
}


class CannedBackend(FakeBackend):
    """FakeBackend whose greedy turn runs the production completion parser."""

    def __init__(self, raw, *, family="qwen3_5", hit_cap=False, tools=SHADE_LIKE_TOOLS):
        super().__init__()
        self.raw, self.family, self.hit_cap, self.tools = raw, family, hit_cap, tools

    def task(self, pair, seed):
        task = FakeTask()
        task.tool_schemas = lambda: self.tools
        return task

    def chat(self, messages, tools, max_tokens, seed, *, greedy=False):
        if not greedy:
            return super().chat(messages, tools, max_tokens, seed, greedy=greedy)
        assert self.greedy_session and seed is None
        self.greedy_messages = messages
        visible, reasoning, calls, flags = parse_completion(
            self.raw, reasoning_open=True, reasoning_tokens=1, model_family=self.family, tools=tools)
        flags = list(flags) + ([f"turn_token_budget_reached:{max_tokens}"] if self.hit_cap else [])
        output = self.encode(self.raw + "!")
        self.generation = {"prompt_token_ids": self.render(messages, tools), "output_token_ids": output}
        return ChatResult(visible, reasoning, calls, len(self.generation["prompt_token_ids"]), 0, len(output),
                          1, 0, 1, 2_000_000_000, {"raw_text": self.raw, "joulewise": {"flags": flags}})


class GenerationCheckTest(unittest.TestCase):
    def test_canned_outputs(self):
        for name, (raw, status, problems) in CANNED.items():
            with self.subTest(name):
                result = r0.generation_check(CannedBackend(raw))
                self.assertEqual(result["status"], status, result["problems"])
                for problem in problems:
                    self.assertIn(problem, result["problems"])
                self.assertEqual(result["decode"], "greedy")
                self.assertEqual(result["seconds"], 2.0)
                self.assertGreater(result["tokens"], 0)
        ok = r0.generation_check(CannedBackend(CANNED["well_formed"][0]))
        self.assertEqual(ok["calls"], [{"name": "search_emails", "arguments_json": '{"query":"spam"}'}])

    def test_hit_cap_fails_even_with_a_call(self):
        result = r0.generation_check(CannedBackend(CANNED["well_formed"][0], hit_cap=True))
        self.assertEqual(result["status"], "fail")
        self.assertIn("hit_cap", result["problems"])

    def test_json_family_unknown_tool_and_schema_invalid_arguments(self):
        # JSON-envelope families parse any name/arguments; the check validates them itself.
        unknown = 'x\n</think>\n\n<tool_call>\n{"name": "delete_all", "arguments": {}}\n</tool_call>'
        result = r0.generation_check(CannedBackend(unknown, family="qwen3_moe"))
        self.assertEqual(result["status"], "fail")
        self.assertIn("unknown_tool:delete_all", result["problems"])
        wrong = 'x\n</think>\n\n<tool_call>\n{"name": "search_emails", "arguments": {"query": 7}}\n</tool_call>'
        result = r0.generation_check(CannedBackend(wrong, family="qwen3_moe"))
        self.assertIn("arguments_schema_invalid:search_emails", result["problems"])
        good = 'x\n</think>\n\n<tool_call>\n{"name": "search_emails", "arguments": {"query": "spam"}}\n</tool_call>'
        self.assertEqual(r0.generation_check(CannedBackend(good, family="qwen3_moe"))["status"], "pass")

    def test_prompt_is_real_shade_system_plus_tools_and_targets_a_listed_tool(self):
        backend = CannedBackend(CANNED["well_formed"][0])
        result = r0.generation_check(backend)
        self.assertEqual([m.role for m in backend.greedy_messages], ["system", "user"])
        self.assertEqual(backend.greedy_messages[0].content, FakeTask().system_prompt("benign"))
        self.assertEqual(result["requested_tool"], "get_received_emails")  # fewest required parameters
        self.assertIn("get_received_emails", backend.greedy_messages[1].content)
        self.assertEqual(result["tool_names"], ["get_received_emails", "search_emails"])
        self.assertEqual(backend.sessions[-1], None)  # default effort
        self.assertFalse(result["called_requested_tool"])

    def test_generation_failure_fails_the_load_check(self):
        backend = CannedBackend(CANNED["no_call"][0], tools=r0.ECHO_TOOLS)
        result = r0.load_coherence(backend, references=fake_references())
        self.assertEqual(result["nll_verdict"]["status"], "pass")
        self.assertEqual(result["status"], "fail")
        self.assertEqual(result["reasons"], ["generation:no_tool_call"])
        good = 'x\n</think>\n\n<tool_call>\n<function=r0_echo>\n<parameter=value>\nhi\n</parameter>\n</function>\n</tool_call>'
        result = r0.load_coherence(CannedBackend(good, tools=r0.ECHO_TOOLS), references=fake_references())
        self.assertEqual(result["status"], "pass", result["reasons"])
        self.assertEqual(result["generation_summary"]["calls"][0]["name"], "r0_echo")
        json.dumps(result)  # report-serializable


if __name__ == "__main__":
    unittest.main()
