"""Adversarial probes of the R0 load verdict (executing review, 2026-11-06).

Synthetic losses and canned completions only; never imports MLX or study data.
"""
from __future__ import annotations

import json
import unittest

from joulewise.align import r0
from tests.align.test_r0_checks import FakeBackend, fake_references
from tests.align.test_r0_load_reference import (
    D_FIXTURE, D_MLX_BINS, SHADE_LIKE_TOOLS, CannedBackend, d_verdict, losses_from_bins, shipped)

D_REV = r0.PINS["D"]["revision"]


def d_entry(table):
    return next(e for e in table["models"] if e["label"] == "D")


class SilentPassProbes(unittest.TestCase):
    def test_absolute_wildcard_beside_reference_entry_is_never_a_fallback(self):
        # Someone adds a null-fixture absolute entry for D next to the reference entry.
        table = shipped()
        table["models"].append({"label": "D-abs", "revision": D_REV, "mode": "absolute",
                                "fixture_sha256": None, "nll_limit": 20.0, "provenance": {"x": 1}})
        same = d_verdict(losses_from_bins(D_MLX_BINS), table)
        self.assertEqual(same["status"], "fail", same)
        # Bug found in review: an unlisted D fixture fell back to the 20.0 absolute bar and passed.
        other = d_verdict([5.0] * 2048, table, fixture="a" * 64)
        self.assertEqual((other["status"], other["reason"]), ("fail", "invalid_reference_config"), other)
        # The shipped anchor wildcard stays valid (it is the anchor revision's only entry).
        self.assertEqual(r0.nll_verdict([0.37] * 2048, revision="d388dead1515f5e085ef7a0431dd8fadf0886c57",
                                        fixture_sha256="b" * 64, references=shipped())["status"], "pass")

    def test_non_finite_or_bool_table_values_invalidate_the_table(self):
        for path, value in ((("tolerance", "mean_nats_per_token"), float("nan")),
                            (("tolerance", "bin_nats_per_token"), float("inf")),
                            (("tolerance", "mean_nats_per_token"), True),
                            (("reference", "nll_nats_per_token"), float("nan"))):
            table = json.loads(json.dumps(shipped()))
            d_entry(table)[path[0]][path[1]] = value
            with self.subTest(path=path, value=value):
                self.assertEqual(d_verdict(losses_from_bins(D_MLX_BINS), table)["reason"],
                                 "invalid_reference_config")
        table = json.loads(json.dumps(shipped()))
        d_entry(table)["reference"]["bins256"][3] = float("nan")
        self.assertEqual(d_verdict(losses_from_bins(D_MLX_BINS), table)["reason"], "invalid_reference_config")
        # JSON's NaN literal parses; it must still be refused.
        text = json.dumps(shipped()).replace('"bin_nats_per_token": 0.5', '"bin_nats_per_token": NaN')
        self.assertEqual(d_verdict(losses_from_bins(D_MLX_BINS), json.loads(text))["reason"],
                         "invalid_reference_config")

    def test_one_bad_entry_invalidates_the_whole_table_including_d(self):
        table = shipped()
        del next(e for e in table["models"] if e["label"] == "anchor")["mode"]
        self.assertEqual(d_verdict(losses_from_bins(D_MLX_BINS), table)["reason"], "invalid_reference_config")

    def test_empty_overflowing_and_mixed_nan_losses_never_pass(self):
        for losses in ([], [1e306] * 2048, losses_from_bins(D_MLX_BINS)[:-1] + [float("nan")],
                       [float("-inf")] + losses_from_bins(D_MLX_BINS)[1:]):
            with self.subTest(n=len(losses)):
                self.assertEqual(d_verdict(losses)["status"], "fail")

    def test_identity_must_be_exact(self):
        for revision in ("", D_REV.upper(), D_REV[:8], " " + D_REV):
            with self.subTest(revision=revision):
                v = r0.nll_verdict(losses_from_bins(D_MLX_BINS), revision=revision,
                                   fixture_sha256=D_FIXTURE, references=shipped())
                self.assertEqual((v["status"], v["reason"]), ("fail", "no_reference"))
        backend = FakeBackend()
        backend.nll_reference_revision = ""  # explicit but empty: never falls back to config
        self.assertEqual(r0.model_revision(backend), "")

    def test_bins_are_positional_so_a_reordered_profile_fails(self):
        # Same multiset of losses (same mean), wrong positions: e.g. a cache/position fault.
        losses = losses_from_bins(D_MLX_BINS)
        verdict = d_verdict(list(reversed(losses)))
        self.assertLess(abs(verdict["delta_nats_per_token"]), 0.1)
        self.assertEqual(verdict["reason"], "bin_outside_tolerance")

    def test_localized_fault_detection_floor_is_tolerance_times_bin_width(self):
        # Characterises (does not change) the bar: a k-token fault of +x nats/token in one bin
        # is invisible iff k*x <= 0.5*256 = 128 (and k*x <= 0.10*2048 = 204.8 overall).
        base = d_entry(shipped())["reference"]["bins256"]
        for k, x, expected in ((16, 7.9, "pass"), (16, 8.1, "fail"), (128, 0.99, "pass"), (128, 1.01, "fail")):
            losses = losses_from_bins(base)
            for i in range(1024, 1024 + k):
                losses[i] += x
            with self.subTest(k=k, x=x):
                self.assertEqual(d_verdict(losses)["status"], expected)


class GenerationProbes(unittest.TestCase):
    def test_json_string_encoded_arguments_are_decoded_then_validated(self):
        # The production parser decodes OpenAI-style string arguments; the check validates the object.
        raw = ('x\n</think>\n\n<tool_call>\n{"name": "search_emails", '
               '"arguments": "{\\"query\\": \\"spam\\"}"}\n</tool_call>')
        result = r0.generation_check(CannedBackend(raw, family="qwen3_moe"))
        self.assertEqual(result["status"], "pass", result)
        self.assertEqual(json.loads(result["calls"][0]["arguments_json"]), {"query": "spam"})
        raw = raw.replace('\\"spam\\"', "7")
        result = r0.generation_check(CannedBackend(raw, family="qwen3_moe"))
        self.assertIn("arguments_schema_invalid:search_emails", result["problems"])

    def test_call_only_inside_reasoning_fails(self):
        raw = ("<tool_call>\n<function=search_emails>\n<parameter=query>\nspam\n</parameter>\n</function>\n"
               "</tool_call>\n</think>\n\nDone.")
        result = r0.generation_check(CannedBackend(raw))
        self.assertEqual(result["status"], "fail", result)
        self.assertIn("no_tool_call", result["problems"])

    def test_dangling_second_envelope_without_cap_fails(self):
        raw = ("x\n</think>\n\n<tool_call>\n<function=get_received_emails>\n</function>\n</tool_call>\n"
               "<tool_call>\n<function=search_emails>")
        result = r0.generation_check(CannedBackend(raw))
        self.assertEqual(result["status"], "fail", result)

    def test_xml_argument_of_wrong_type_fails(self):
        raw = ("x\n</think>\n\n<tool_call>\n<function=search_emails>\n<parameter=query>\nspam\n</parameter>\n"
               "<parameter=limit>\nmany\n</parameter>\n</function>\n</tool_call>")
        result = r0.generation_check(CannedBackend(raw))
        self.assertEqual(result["status"], "fail", result)

    def test_other_listed_tool_passes_but_is_recorded(self):
        # Documented: the requested tool is diagnostic; any listed, schema-valid call passes.
        raw = ("x\n</think>\n\n<tool_call>\n<function=search_emails>\n<parameter=query>\nspam\n</parameter>\n"
               "</function>\n</tool_call>")
        result = r0.generation_check(CannedBackend(raw, tools=SHADE_LIKE_TOOLS))
        self.assertEqual((result["status"], result["called_requested_tool"]), ("pass", False))

    def test_generation_and_nll_failures_are_both_reported(self):
        backend = CannedBackend("x\n</think>\n\nno call", tools=r0.ECHO_TOOLS)
        result = r0.load_coherence(backend, references=fake_references(mean=11.0))
        self.assertEqual(result["status"], "fail")
        self.assertEqual([r.split(":")[0] for r in result["reasons"]], ["nll", "generation"])


if __name__ == "__main__":
    unittest.main()
