"""Cheap, platform-independent checks for the qwen4_exp upstream surface.

The numerical suite requires Metal, MLX, and transformers.  These checks keep
the reviewable mlx-lm entry points, remote-model packaging, and license marker
covered on every platform without pretending to replace numerical parity.
"""

import ast
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODEL = ROOT / "joulewise" / "align" / "models" / "qwen4_exp.py"
CONVERTER = ROOT / "scripts" / "align_convert_qwen4_exp.py"


def _classes(path: Path):
    tree = ast.parse(path.read_text(), filename=str(path))
    return {node.name: node for node in tree.body if isinstance(node, ast.ClassDef)}


class Qwen4ExpUpstreamContractTest(unittest.TestCase):
    def test_model_has_repository_license_marker(self):
        first_lines = MODEL.read_text().splitlines()[:3]
        self.assertEqual(first_lines[0], "# SPDX-License-Identifier: MIT")
        self.assertRegex(first_lines[1], r"^# Copyright \(c\) 2026 .+")
        self.assertIn("MIT License", (ROOT / "LICENSE").read_text())

    def test_model_args_have_native_module_defaults(self):
        model_args = _classes(MODEL)["ModelArgs"]
        assignments = {
            node.target.id: node.value
            for node in model_args.body
            if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name)
        }
        self.assertEqual(ast.literal_eval(assignments["model_type"]), "qwen4_exp")
        factory = assignments["text_config"]
        self.assertIsInstance(factory, ast.Call)
        self.assertEqual(ast.unparse(factory), "field(default_factory=dict)")

        from_dict = next(
            node for node in model_args.body if isinstance(node, ast.FunctionDef) and node.name == "from_dict"
        )
        self.assertIn("params.get('model_type', 'qwen4_exp')", ast.unparse(from_dict))

    def test_model_exposes_mlx_lm_generation_surface(self):
        model = _classes(MODEL)["Model"]
        methods = {node.name: node for node in model.body if isinstance(node, ast.FunctionDef)}
        required = {"__call__", "make_cache", "sanitize", "quant_predicate", "cast_predicate",
                    "layers", "head_dim", "n_kv_heads"}
        self.assertTrue(required <= set(methods), required - set(methods))
        self.assertTrue(any(isinstance(d, ast.Name) and d.id == "property" for d in methods["head_dim"].decorator_list))
        self.assertTrue(any(isinstance(d, ast.Name) and d.id == "property" for d in methods["n_kv_heads"].decorator_list))

    def test_model_file_is_packaging_only_in_verified_loader(self):
        source = CONVERTER.read_text()
        self.assertRegex(source, r'model_file="qwen4_exp\.py"')
        self.assertIn('config.get("model_file") != "qwen4_exp.py"', source)
        self.assertIn('"model_file": None', source)
        self.assertRegex(source, re.compile(r"get_model_classes=lambda config: \(module\.Model, module\.ModelArgs\)"))


if __name__ == "__main__":
    unittest.main()
