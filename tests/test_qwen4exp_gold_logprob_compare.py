import hashlib
import importlib.util
import json
import math
import tempfile
import unittest
from pathlib import Path


PATH = Path(__file__).parents[1] / "scripts" / "qwen4exp_gold_logprob_compare.py"
SPEC = importlib.util.spec_from_file_location("gold_compare", PATH)
gold = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gold)


class GoldLogprobMathTests(unittest.TestCase):
    def test_identical_logits_have_zero_symmetric_kl(self):
        result = gold.distribution_metrics([1.0, 2.0, -3.0], [1.0, 2.0, -3.0], top_k=2, target_id=0)
        self.assertAlmostEqual(result["kl_bf16_quant"], 0.0, places=14)
        self.assertAlmostEqual(result["kl_quant_bf16"], 0.0, places=14)
        self.assertEqual(result["top1_agreement"], True)
        self.assertEqual(result["topk_overlap"], 1.0)
        self.assertAlmostEqual(result["nll_difference"], 0.0, places=14)

    def test_synthetic_binary_kl_and_reverse(self):
        # softmax(log probabilities) recovers the desired distributions.
        result = gold.distribution_metrics([math.log(.8), math.log(.2)],
                                           [math.log(.5), math.log(.5)], top_k=1, target_id=1)
        expected = .8 * math.log(.8 / .5) + .2 * math.log(.2 / .5)
        reverse = .5 * math.log(.5 / .8) + .5 * math.log(.5 / .2)
        self.assertAlmostEqual(result["kl_bf16_quant"], expected, places=14)
        self.assertAlmostEqual(result["kl_quant_bf16"], reverse, places=14)
        self.assertAlmostEqual(result["nll_difference"], math.log(.2 / .5), places=14)

    def test_shape_and_target_validation(self):
        with self.assertRaises(ValueError):
            gold.distribution_metrics([1], [1, 2])
        with self.assertRaises(ValueError):
            gold.distribution_metrics([1], [1], target_id=2)


try:
    import numpy as np
except ImportError:
    np = None


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


@unittest.skipUnless(np is not None, "optional NumPy")
class GoldStreamCompareTests(unittest.TestCase):
    """compare consumes the real qwen4-gold-stream/v1 work-folder layout."""

    prompts = [{"name": "tokens-a", "input_ids": [3, 1, 4, 1, 5]}, {"name": "tokens-b", "input_ids": [2, 7, 1]}]
    vocab = 9

    def make_work(self, root):
        rng = np.random.default_rng(11)
        work = Path(root) / "work"
        artifacts, chain, logits = {}, {}, {}
        for p in self.prompts:
            base = rng.normal(size=(1, len(p["input_ids"]), self.vocab)).astype(np.float32)
            logits[p["name"]] = base[0]
            for dtype, value in (("bf16", base), ("fp32", base + np.float32(1e-3))):
                rel = f"parity/head/{p['name']}-{dtype}-real/reference/output.npy"
                (work / rel).parent.mkdir(parents=True, exist_ok=True)
                np.save(work / rel, value)
                artifacts[rel] = _sha(work / rel)
                chain[f"{dtype}:{p['name']}"] = str(work / rel)
        (work / "parity" / "provenance.json").write_text(json.dumps({"fingerprint": "p" * 64, "prompts": self.prompts}))
        (work / "manifest.json").write_text(json.dumps({
            "schema": "qwen4-gold-stream/v1", "fingerprint": "f" * 64,
            "units": {"head": {"state": "done", "status": "PASS", "artifacts": artifacts}},
            "chain": {"head": chain}}))
        return work, logits

    def run_compare(self, root, work, quant, *extra):
        npz = Path(root) / "quant.npz"
        np.savez(npz, **quant)
        out = Path(root) / "report.json"
        code = gold.main(["compare", "--work-folder", str(work), "--quant-logits", str(npz),
                          "--quant-profile", "maxfit", "--top-k", "3", "--out", str(out), *extra])
        return code, json.loads(out.read_text())

    def test_identical_quant_passes_with_exact_next_token_nll(self):
        with tempfile.TemporaryDirectory() as root:
            work, logits = self.make_work(root)
            code, report = self.run_compare(root, work, logits)
            self.assertEqual(code, 0)
            quant = report["cases"]["maxfit"]
            self.assertEqual(quant["verdict"], "pass")
            self.assertAlmostEqual(quant["summary"]["kl_bf16_quant"], 0.0, places=12)
            self.assertEqual(quant["summary"]["positions"], 8)
            self.assertEqual(quant["summary"]["nll_positions"], 6)  # last position has no target
            expected = []
            for p in self.prompts:
                rows = logits[p["name"]].astype(np.float64)
                lse = np.log(np.exp(rows).sum(-1))
                expected += [lse[t] - rows[t, p["input_ids"][t + 1]] for t in range(len(p["input_ids"]) - 1)]
            self.assertAlmostEqual(quant["summary"]["nll_reference"], float(np.mean(expected)), places=6)
            floor = report["cases"]["fp32"]
            self.assertNotIn("verdict", floor)
            self.assertLess(floor["summary"]["kl_bf16_quant"], 1e-6)
            self.assertEqual(report["head_outputs"]["tokens-a"]["bf16"],
                             _sha(work / "parity/head/tokens-a-bf16-real/reference/output.npy"))

    def test_perturbed_quant_fails(self):
        with tempfile.TemporaryDirectory() as root:
            work, logits = self.make_work(root)
            code, report = self.run_compare(root, work, {k: -v for k, v in logits.items()})
            self.assertEqual(code, 1)
            self.assertEqual(report["cases"]["maxfit"]["verdict"], "fail")

    def test_tampered_or_incomplete_head_fails_closed(self):
        with tempfile.TemporaryDirectory() as root:
            work, logits = self.make_work(root)
            target = work / "parity/head/tokens-b-bf16-real/reference/output.npy"
            target.write_bytes(target.read_bytes()[:-4] + b"\0\0\0\0")
            with self.assertRaises(ValueError):
                self.run_compare(root, work, logits)
            manifest = json.loads((work / "manifest.json").read_text())
            manifest["units"].pop("head")
            (work / "manifest.json").write_text(json.dumps(manifest))
            with self.assertRaises(ValueError):
                self.run_compare(root, work, logits)

    def test_prepared_must_match_gold_prompts_and_adds_continuation_group(self):
        with tempfile.TemporaryDirectory() as root:
            work, logits = self.make_work(root)
            prepared = Path(root) / "prepared.json"
            records = [{"name": "tokens-a", "input_ids": [3, 1, 4], "token_ids": [3, 1, 4, 1, 5]},
                       {"name": "tokens-b", "input_ids": [2, 7], "token_ids": [2, 7, 1]}]
            prepared.write_text(json.dumps({"schema": gold.SCHEMA, "prompts": records}))
            _, report = self.run_compare(root, work, logits, "--prepared", str(prepared))
            # tokens-a positions 2..4, tokens-b positions 1..2
            self.assertEqual(report["cases"]["maxfit"]["groups"]["continuation"]["positions"], 5)
            records[1]["token_ids"] = [2, 7, 2]
            prepared.write_text(json.dumps({"schema": gold.SCHEMA, "prompts": records}))
            with self.assertRaises(ValueError):
                self.run_compare(root, work, logits, "--prepared", str(prepared))


    def test_policy_is_the_primary_pass_rule_and_e2e_is_a_secondary_screen(self):
        with tempfile.TemporaryDirectory() as root:
            work, logits = self.make_work(root)
            code, report = self.run_compare(root, work, logits)
            quant = report["cases"]["maxfit"]
            self.assertEqual(quant["classification"], "acceptable")
            self.assertEqual(quant["pass_rule"]["primary"], "joulewise.align.qwen4_quant_quality.POLICY")
            self.assertTrue(quant["pass_rule"]["doc"].startswith("docs/align/qwen4_exp_port/quant_quality.md"))
            self.assertEqual(quant["e2e_screen"]["role"], "secondary; not decisive")
            self.assertIn("top5_overlap", quant["summary"])
            # A variant that passes the old e2e screen but not POLICY's p99 bar fails.
            from unittest import mock
            from joulewise.align import qwen4_quant_quality as qq
            strict = {**qq.POLICY, "acceptable": {**qq.POLICY["acceptable"], "p99_projected_kl_max": -1.0}}
            with mock.patch.object(qq, "POLICY", strict):
                code, report = self.run_compare(root, work, logits)
            self.assertEqual(code, 1)
            self.assertEqual(report["cases"]["maxfit"]["classification"], "marginal")
            self.assertEqual(report["cases"]["maxfit"]["verdict"], "fail")
            self.assertTrue(report["cases"]["maxfit"]["e2e_screen"]["pass"])

    def test_moved_work_folder_opens_against_its_manifest(self):
        import shutil
        with tempfile.TemporaryDirectory() as root:
            work, logits = self.make_work(root)
            moved = Path(root) / "moved" / "work"
            moved.parent.mkdir()
            shutil.move(str(work), str(moved))
            code, report = self.run_compare(root, moved, logits)
            self.assertEqual(code, 0)
            self.assertEqual(report["head_outputs"]["tokens-a"]["bf16"],
                             _sha(moved / "parity/head/tokens-a-bf16-real/reference/output.npy"))

    def test_quality_ref_prompts_json_adds_continuation_group(self):
        with tempfile.TemporaryDirectory() as root:
            work, logits = self.make_work(root)
            prompts = Path(root) / "prompts.json"
            rows = [{"name": "tokens-a", "input_ids": [3, 1, 4, 1, 5], "continuation_from": 3},
                    {"name": "tokens-b", "input_ids": [2, 7, 1], "continuation_from": 2}]
            prompts.write_text(json.dumps(rows))
            _, report = self.run_compare(root, work, logits, "--prepared", str(prompts))
            self.assertEqual(report["cases"]["maxfit"]["groups"]["continuation"]["positions"], 5)
            rows[0]["input_ids"] = [3, 1, 4, 1, 6]
            prompts.write_text(json.dumps(rows))
            with self.assertRaises(ValueError):
                self.run_compare(root, work, logits, "--prepared", str(prompts))


class PrepareGuardTests(unittest.TestCase):
    def test_live_load_sets_metal_limits_before_loading_and_checks_ple(self):
        import sys
        from types import SimpleNamespace
        from unittest import mock
        try:
            import mlx.core as mx
        except ImportError:
            self.skipTest("MLX is available only on the native Mac")
        from scripts import qwen4exp_mbp_live as live
        order = []
        model = SimpleNamespace()
        fake_adapter = SimpleNamespace(model=model)
        args = SimpleNamespace(artifact=Path("/Volumes/JW-EXT/x"), metal_cap_gb=1e6)
        with mock.patch.object(live, "measurement_agents_loaded", return_value=[]), \
             mock.patch.object(live, "external", side_effect=lambda p: order.append(("external", str(p)))), \
             mock.patch.object(mx, "set_memory_limit", side_effect=lambda v: order.append(("limit", v))), \
             mock.patch.object(mx, "set_cache_limit", side_effect=lambda v: order.append(("cache", v))), \
             mock.patch.object(live, "load_adapter", side_effect=lambda a: order.append(("load",)) or fake_adapter), \
             mock.patch.object(live, "table_stats", return_value={"1": {"path": "/Volumes/JW-EXT/t", "resident_bytes": 0}}), \
             mock.patch.object(live, "check_tables", side_effect=lambda s: order.append(("check",))):
            self.assertIs(gold.load_live_adapter(args), fake_adapter)
        kinds = [o[0] for o in order]
        self.assertLess(kinds.index("limit"), kinds.index("load"))
        self.assertLess(kinds.index("cache"), kinds.index("load"))
        self.assertEqual(kinds[-2:], ["external", "check"])
        self.assertLess(args.metal_cap_gb, 1e6)  # clamped to the device's recommended set
        with mock.patch.object(live, "measurement_agents_loaded", return_value=["com.jw.agent"]):
            with self.assertRaises(ValueError):
                gold.load_live_adapter(args)


if __name__ == "__main__":
    unittest.main()
