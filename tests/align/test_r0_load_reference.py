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



# ---------------------------------------------------------------- exact-reproduction tier

STACK = {"mlx": "0.31.2", "mlx-lm": "0.31.3", "transformers": "5.12.1"}


def qualified_losses():
    """A D-regime profile with per-token spread (deterministic)."""
    return [b + 0.25 * ((i * 7919) % 13 - 6) / 6 for i, b in enumerate(losses_from_bins(D_MLX_BINS))]


def pin(table, losses, *, stack=STACK):
    """Pin a qualified run's profile into D's entry, as an operator copies it from report.json."""
    profile = json.loads(json.dumps(r0.loss_profile(losses, revision=r0.PINS["D"]["revision"],
                                                    fixture_sha256=D_FIXTURE, stack_versions=stack)))
    entry = next(e for e in table["models"] if e["label"] == "D")
    entry["reproduce"] = {"profile_sha256": r0._canonical_sha256(profile), "profile": profile,
                          "source": {"report": "records/<qualified-r0>/report.json", "check": "load"}}
    return table


def reproduce(losses, table, stack=STACK):
    return r0.nll_verdict(losses, revision=r0.PINS["D"]["revision"], fixture_sha256=D_FIXTURE,
                          references=table, stack_versions=stack)


class ReproductionTierTest(unittest.TestCase):
    def test_not_pinned_is_reported_and_is_not_a_fail(self):
        verdict = reproduce(qualified_losses(), shipped())
        self.assertEqual(verdict["status"], "pass", verdict)
        self.assertEqual(verdict["reproduction"], {"status": "not_pinned"})
        profile = verdict["loss_profile"]
        self.assertEqual(profile["losses_sha256"], r0.digest(qualified_losses()))
        self.assertEqual((profile["targets"], profile["stack_versions"]), (2048, STACK))
        self.assertEqual(verdict["loss_profile_sha256"], r0._canonical_sha256(profile))

    def test_exact_match_passes_bit_identical(self):
        table = pin(shipped(), qualified_losses())
        verdict = reproduce(qualified_losses(), table)
        self.assertEqual((verdict["status"], verdict["reproduction"]["status"]), ("pass", "pass"), verdict)
        self.assertTrue(verdict["reproduction"]["bit_identical"])
        self.assertEqual(verdict["reproduction"]["max_abs_bin_delta"], 0.0)

    def test_drift_inside_reproduction_tolerance_passes_but_is_not_bit_identical(self):
        table = pin(shipped(), qualified_losses())
        drifted = [v + 5e-4 for v in qualified_losses()]
        verdict = reproduce(drifted, table)
        self.assertEqual(verdict["status"], "pass", verdict)
        self.assertFalse(verdict["reproduction"]["bit_identical"])

    def test_mismatch_fails_even_inside_the_reference_tolerance(self):
        table = pin(shipped(), qualified_losses())
        # A subtle fault (the reviewer's middle-layer skip moved the sibling mean 0.017).
        shifted = [v + 0.017 for v in qualified_losses()]
        verdict = reproduce(shifted, table)
        self.assertLessEqual(abs(verdict["delta_nats_per_token"]), 0.10)  # reference tier alone passes
        self.assertEqual((verdict["status"], verdict["reason"]), ("fail", "reproduce_reproduction_mismatch"))
        # Mean unchanged, one bin +0.02 and another -0.02: the bin bar catches it.
        moved = qualified_losses()
        moved[:256] = [v + 0.02 for v in moved[:256]]
        moved[256:512] = [v - 0.02 for v in moved[256:512]]
        verdict = reproduce(moved, table)
        self.assertLess(abs(verdict["reproduction"]["delta_nats_per_token"]), 1e-9)
        self.assertEqual(verdict["reproduction"]["reason"], "reproduction_mismatch")
        self.assertEqual(verdict["status"], "fail")

    def test_stack_version_mismatch_is_not_comparable_and_fails_closed(self):
        table = pin(shipped(), qualified_losses())
        for stack in ({**STACK, "mlx": "0.31.3"}, {k: v for k, v in STACK.items() if k != "transformers"}, None):
            with self.subTest(stack=stack):
                verdict = reproduce(qualified_losses(), table, stack=stack)
                self.assertEqual(verdict["status"], "fail", verdict)
                self.assertEqual(verdict["reason"], "reproduce_not_comparable")
                self.assertEqual(verdict["reproduction"]["mismatch"], ["stack_versions"])

    def test_reproduction_failure_combines_with_reference_failure(self):
        table = pin(shipped(), qualified_losses())
        verdict = reproduce([v + 0.2 for v in qualified_losses()], table)
        self.assertEqual(verdict["reason"], "mean_outside_tolerance+reproduce_reproduction_mismatch")

    def test_malformed_or_tampered_pin_invalidates_the_table(self):
        def tampered(edit):
            table = pin(shipped(), qualified_losses())
            edit(r0.reference_entry(table, r0.PINS["D"]["revision"], D_FIXTURE)["reproduce"])
            return reproduce(qualified_losses(), table)
        cases = {
            "edited mean": lambda p: p["profile"].update(nll_nats_per_token=p["profile"]["nll_nats_per_token"] + 0.01),
            "wrong sha": lambda p: p.update(profile_sha256="0" * 64),
            "no source": lambda p: p.pop("source"),
            "empty pin": lambda p: p.clear(),
        }
        for name, edit in cases.items():
            with self.subTest(name):
                verdict = tampered(edit)
                self.assertEqual((verdict["status"], verdict["reason"]), ("fail", "invalid_reference_config"))
        # A self-consistent pin for another revision is rejected, not silently not_comparable.
        table = pin(shipped(), qualified_losses())
        entry = r0.reference_entry(table, r0.PINS["D"]["revision"], D_FIXTURE)
        entry["reproduce"]["profile"]["model_revision"] = "0" * 40
        entry["reproduce"]["profile_sha256"] = r0._canonical_sha256(entry["reproduce"]["profile"])
        self.assertEqual(reproduce(qualified_losses(), table)["reason"], "invalid_reference_config")

    def test_load_check_records_the_profile_and_a_later_run_reproduces_it(self):
        backend = FakeBackend()
        backend.stack_versions = dict(STACK)
        first = r0.load_coherence(backend, references=fake_references())
        self.assertEqual(first["status"], "pass", first["reasons"])
        self.assertEqual(first["nll_reproduction"], {"status": "not_pinned"})
        self.assertEqual(len(first["nll_losses"]), 2048)
        self.assertEqual(first["nll_loss_profile"]["losses_sha256"], r0.digest(first["nll_losses"]))
        report = json.loads(json.dumps(first))  # pin from the serialized report, as an operator would
        table = fake_references(reproduce={"profile_sha256": report["nll_loss_profile_sha256"],
                                           "profile": report["nll_loss_profile"],
                                           "source": {"report": "synthetic"}})
        again = r0.load_coherence(backend, references=table)
        self.assertEqual((again["status"], again["nll_reproduction"]["status"]), ("pass", "pass"))
        self.assertTrue(again["nll_reproduction"]["bit_identical"])
        backend.stack_versions["mlx-lm"] = "0.32.0"
        moved = r0.load_coherence(backend, references=table)
        self.assertEqual((moved["status"], moved["reasons"]), ("fail", ["nll:reproduce_not_comparable"]))
        self.assertEqual(r0.load_coherence(FakeBackend(), references=table)["reasons"],
                         ["nll:reproduce_not_comparable"])  # a backend that reports no stack


# ---------------------------------------------------------------- generation bar

SHADE_LIKE_TOOLS = [
    {"type": "function", "function": {"name": "get_received_emails", "description": "List emails",
                                       "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "search_emails", "description": "Search emails",
                                      "parameters": {"type": "object", "properties": {
                                          "query": {"type": "string"}, "limit": {"type": "integer"}},
                                          "required": ["query"]}}},
]

# search_emails (1 required) is the requested tool here: send_email needs 2.
SEARCH_TARGET_TOOLS = [
    SHADE_LIKE_TOOLS[1],
    {"type": "function", "function": {"name": "send_email", "description": "Send an email",
                                      "parameters": {"type": "object", "properties": {
                                          "to": {"type": "string"}, "body": {"type": "string"}},
                                          "required": ["to", "body"]}}},
]

XML_OK = "</think>\n\n<tool_call>\n<function=search_emails>\n<parameter=query>\nspam\n</parameter>\n</function>\n</tool_call>"
CANNED = {
    "well_formed": ("Find spam first.\n" + XML_OK, "pass", []),  # under SEARCH_TARGET_TOOLS
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


# Cases whose call names search_emails are judged where search_emails is the requested tool.
CANNED_TOOLS = {"well_formed": SEARCH_TARGET_TOOLS, "malformed": SEARCH_TARGET_TOOLS,
                "missing_required": SEARCH_TARGET_TOOLS}


class GenerationCheckTest(unittest.TestCase):
    def test_canned_outputs(self):
        for name, (raw, status, problems) in CANNED.items():
            with self.subTest(name):
                result = r0.generation_check(CannedBackend(raw, tools=CANNED_TOOLS.get(name, SHADE_LIKE_TOOLS)))
                self.assertEqual(result["status"], status, result["problems"])
                for problem in problems:
                    self.assertIn(problem, result["problems"])
                self.assertEqual(result["decode"], "greedy")
                self.assertEqual(result["seconds"], 2.0)
                self.assertGreater(result["tokens"], 0)
        ok = r0.generation_check(CannedBackend(CANNED["well_formed"][0], tools=SEARCH_TARGET_TOOLS))
        self.assertEqual(ok["calls"], [{"name": "search_emails", "arguments_json": '{"query":"spam"}'}])
        self.assertTrue(ok["called_requested_tool"])

    def test_a_listed_tool_other_than_the_requested_one_fails(self):
        # Executing review LOW: any listed tool used to pass, e.g. a no-argument end_task.
        # Mirrors real SHADE: analyze_spam_patterns (0 required) is requested; end_task also needs none.
        def no_arg(name):
            return {"type": "function", "function": {"name": name, "description": name,
                                                     "parameters": {"type": "object", "properties": {}}}}
        tools = SHADE_LIKE_TOOLS + [no_arg("end_task"), no_arg("analyze_spam_patterns")]
        call = "x\n</think>\n\n<tool_call>\n<function={}>\n</function>\n</tool_call>"
        result = r0.generation_check(CannedBackend(call.format("end_task"), tools=tools))
        self.assertEqual(result["requested_tool"], "analyze_spam_patterns")
        self.assertEqual(result["status"], "fail", result)
        self.assertEqual(result["problems"], ["wrong_tool:end_task"])
        self.assertFalse(result["called_requested_tool"])
        # A schema-valid call with arguments to another listed tool also fails.
        result = r0.generation_check(CannedBackend(CANNED["well_formed"][0], tools=tools))
        self.assertEqual(result["problems"], ["wrong_tool:search_emails"])
        # The requested tool itself passes.
        ok = r0.generation_check(CannedBackend(call.format("analyze_spam_patterns"), tools=tools))
        self.assertEqual((ok["status"], ok["called_requested_tool"]), ("pass", True))

    def test_hit_cap_fails_even_with_a_call(self):
        result = r0.generation_check(CannedBackend(CANNED["well_formed"][0], hit_cap=True,
                                                   tools=SEARCH_TARGET_TOOLS))
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
        self.assertEqual(r0.generation_check(CannedBackend(good, family="qwen3_moe", tools=SEARCH_TARGET_TOOLS))
                         ["status"], "pass")

    def test_prompt_is_real_shade_system_plus_tools_and_targets_a_listed_tool(self):
        backend = CannedBackend(CANNED["well_formed"][0])
        result = r0.generation_check(backend)
        self.assertEqual([m.role for m in backend.greedy_messages], ["system", "user"])
        self.assertEqual(backend.greedy_messages[0].content, FakeTask().system_prompt("benign"))
        self.assertEqual(result["requested_tool"], "get_received_emails")  # fewest required parameters
        self.assertIn("get_received_emails", backend.greedy_messages[1].content)
        self.assertEqual(result["tool_names"], ["get_received_emails", "search_emails"])
        self.assertEqual(backend.sessions[-1], None)  # template default effort (renders as xhigh)
        self.assertEqual(result["effort"], "template_default")
        self.assertIn("xhigh", result["effort_basis"])
        self.assertFalse(result["called_requested_tool"])
        self.assertIn("wrong_tool:search_emails", result["problems"])

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
