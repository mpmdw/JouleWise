"""Composition uses committed config structure, never collected data."""
import json
import unittest

from joulewise.b6 import compose, queue
from joulewise.b5.chain import stage_plan
from tests.test_b6_registration import ROOT, modular, registrations


def sequence(layout):
    return [(e["run_id"], e["role"], e["block_id"], e["position"], e["arm"])
            for s in layout.stages for e in s["entries"]]


class ComposeTests(unittest.TestCase):
    def test_all_three_modular_sequences_counts_and_references_match_fixed(self):
        for p in ("alpha", "beta", "gamma"):
            with self.subTest(pack=p):
                fixed = compose.layout(queue.Selection((p,), 1), registrations(), ROOT)
                reg = modular(p)
                built = compose.layout(queue.Selection((p,), 1), {p: reg}, ROOT)
                self.assertEqual(sequence(built), sequence(fixed))
                self.assertEqual([s["expected_count"] for s in built.stages], [s["expected_count"] for s in fixed.stages])
                refs = [s["expected_count"] for s in built.stages if "reference" in s["stage_id"]]
                self.assertEqual(refs, [3, 1, 1, 1, 3] if p == "gamma" else [3, 1, 3])

    def test_fixed_render_bytes_identical_all_three(self):
        for p, reg in registrations().items():
            layout = compose.layout(queue.Selection((p,), 1), {p: reg}, ROOT)
            tree, files = compose.render(layout)
            self.assertEqual(files["plan_tree.json"], (ROOT / reg.plan_tree_ref).read_bytes())
            self.assertEqual(tree, json.loads(files["plan_tree.json"]))

    def test_modular_render_parses_and_copies_attachments_config_hashes(self):
        layout = compose.layout(queue.Selection(("beta",), 1), {"beta": modular()}, ROOT)
        tree, files = compose.render(layout)
        self.assertEqual(len(stage_plan(tree)), len(layout.stages))
        self.assertEqual(tree["arm_attachments"], layout.template["arm_attachments"])
        for s in tree["stage_graph"]:
            if s["kind"] == "campaign_collection":
                self.assertEqual(s["input"]["kind"], "manifest")
                manifest = json.loads(files[s["input"]["path"]])
                for e in manifest["executed_order"]:
                    self.assertTrue(e["config_path"].startswith("configs/"))
                    self.assertTrue((ROOT / e["config_path"]).is_file())

    def test_quad_round_robin_never_splits_or_reorders_a_quad(self):
        reg = modular("gamma", interleave="quad_round_robin")
        layout = compose.layout(queue.Selection(("gamma",), 1), {"gamma": reg}, ROOT)
        for s in layout.stages:
            if s.get("module_id"):
                self.assertEqual(len(s["entries"]), 4)
                self.assertEqual([e["arm"] for e in s["entries"]], ["A", "B", "B", "A"])
                self.assertEqual(len({e["block_id"] for e in s["entries"]}), 1)
        reg = modular("beta", interleave="quad_round_robin")
        layout = compose.layout(queue.Selection(("beta",), 1), {"beta": reg}, ROOT)
        quad_modules = [s["module_id"] for s in layout.stages if s.get("module_id") and "quads" in s["stage_id"]]
        self.assertEqual(quad_modules, ["beta-decode", "beta-prefill"] * 10)

    def test_smoke_keep_four_four_six_no_zero(self):
        for p, n in (("alpha", 4), ("beta", 4), ("gamma", 6)):
            for regs in (registrations(), {p: modular(p)}):
                layout = compose.layout(queue.Selection((p,), 1), regs, ROOT)
                keep = compose.smoke_keep(layout)
                self.assertEqual(sum(keep.values()), n)
                self.assertTrue(all(k > 0 for k in keep.values()))

    def test_mixed_models_carry_pack_id(self):
        regs = {p: modular(p) for p in ("alpha", "beta")}
        layout = compose.layout(queue.Selection(("alpha", "beta"), 1), regs, ROOT)
        entries = [e for s in layout.stages for e in s["entries"] if e["module_id"]]
        self.assertEqual({e["pack_id"] for e in entries}, {"alpha", "beta"})
        self.assertEqual(len(entries), 200)
