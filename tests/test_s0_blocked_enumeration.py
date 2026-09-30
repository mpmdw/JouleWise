"""Keep expected failures out of both test lanes."""

import ast
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class S0BlockedEnumerationTests(unittest.TestCase):
    def test_no_expected_failures(self) -> None:
        expected_failures = []
        for lane in ("tests", "tests_tools"):
            for path in sorted((ROOT / lane).rglob("test_*.py")):
                for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"), path)):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        for decorator in node.decorator_list:
                            if (isinstance(decorator, ast.Attribute)
                                    and isinstance(decorator.value, ast.Name)
                                    and decorator.value.id == "unittest"
                                    and decorator.attr == "expectedFailure"):
                                expected_failures.append(f"{path.relative_to(ROOT)}:{node.name}")
        self.assertEqual(expected_failures, [])


if __name__ == "__main__":
    unittest.main()
