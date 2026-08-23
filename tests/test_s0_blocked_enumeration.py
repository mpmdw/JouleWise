from __future__ import annotations

import ast
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TARGET_MODULES = {
    "test_arm_readiness_dry_run.py",
    "test_arm_readiness_evidence_t0.py",
    "test_arm_readiness_integration.py",
    "test_arm_readiness_lifecycle.py",
    "test_d117_decode_contrast_plan.py",
}
BLOCKED_PREFIXES = (
    "S0-BLOCKED:",
    "STRUCTURAL-BLOCKED:",
    "CRASH-BLOCKED:",
)


def _skip_reason(decorator: ast.expr) -> str | None:
    if not (
        isinstance(decorator, ast.Call)
        and isinstance(decorator.func, ast.Attribute)
        and isinstance(decorator.func.value, ast.Name)
        and decorator.func.value.id == "unittest"
        and decorator.func.attr == "skip"
        and len(decorator.args) == 1
        and not decorator.keywords
    ):
        return None
    try:
        reason = ast.literal_eval(decorator.args[0])
    except (ValueError, TypeError):
        return None
    return reason if isinstance(reason, str) else None


class S0BlockedEnumerationTests(unittest.TestCase):
    def test_blocked_skip_partition_is_exact_and_machine_readable(self) -> None:
        blocked: list[tuple[str, str, str | None]] = []
        expected_failures: list[str] = []
        for source_path in sorted((ROOT / "tests").glob("test_*.py")):
            tree = ast.parse(source_path.read_text(encoding="utf-8"), source_path)
            for node in ast.walk(tree):
                if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                if source_path.name in TARGET_MODULES and any(
                    isinstance(decorator, ast.Attribute)
                    and isinstance(decorator.value, ast.Name)
                    and decorator.value.id == "unittest"
                    and decorator.attr == "expectedFailure"
                    for decorator in node.decorator_list
                ):
                    expected_failures.append(f"{source_path.name}:{node.name}")
                for decorator in node.decorator_list:
                    reason = _skip_reason(decorator)
                    if reason is not None and reason.startswith(BLOCKED_PREFIXES):
                        blocked.append(
                            (
                                f"{source_path.name}:{node.name}",
                                reason,
                                ast.get_docstring(node),
                            )
                        )

        self.assertEqual(expected_failures, [])
        counts = Counter(
            prefix
            for _test_id, reason, _docstring in blocked
            for prefix in BLOCKED_PREFIXES
            if reason.startswith(prefix)
        )
        self.assertEqual(counts["S0-BLOCKED:"], 0)
        self.assertEqual(counts["STRUCTURAL-BLOCKED:"], 17)
        self.assertEqual(counts["CRASH-BLOCKED:"], 4)
        self.assertEqual(len(blocked), 21)
        for test_id, reason, docstring in blocked:
            with self.subTest(test_id=test_id):
                matching = [
                    prefix for prefix in BLOCKED_PREFIXES if reason.startswith(prefix)
                ]
                self.assertEqual(len(matching), 1)
                artifact_clause = reason.removeprefix(matching[0]).strip()
                self.assertTrue(artifact_clause)
                self.assertIsNotNone(docstring)
                self.assertTrue(docstring.strip())
                if matching[0] == "S0-BLOCKED:":
                    self.assertRegex(
                        reason,
                        r"\AS0-BLOCKED: requires minted _v4 packs — .+\Z",
                    )


if __name__ == "__main__":
    unittest.main()
