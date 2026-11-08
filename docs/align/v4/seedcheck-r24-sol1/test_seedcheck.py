"""Focused counterexamples for the independent comparator, stdlib only."""

import ast
import copy
import json
from pathlib import Path
import subprocess
import unittest

import derive_and_check as check


class SeedCheckTests(unittest.TestCase):
    def test_derivation_functions_unchanged_since_precomparison_commit(self):
        original = subprocess.run(
            ["git", "show", "f969514ed:docs/align/v4/seedcheck-r24-sol1/derive_and_check.py"],
            cwd=check.ROOT, check=True, capture_output=True, text=True,
        ).stdout
        current = Path(check.__file__).read_text()

        def functions(source):
            return {node.name: ast.dump(node) for node in ast.parse(source).body
                    if isinstance(node, ast.FunctionDef)}

        before, after = functions(original), functions(current)
        for name, body in before.items():
            with self.subTest(function=name):
                self.assertEqual(body, after[name])
        for node in ast.parse(original).body:
            if isinstance(node, ast.Assign):
                self.assertIn(ast.dump(node), {ast.dump(n) for n in ast.parse(current).body})

    def test_member_and_policy_mutations_report_exact_field(self):
        expected = check.expected_manifest()
        # W1 explicit roles plus C1, C9, C14 and T1 exercise each schema variant.
        paths = [
            ("windows", wi, "members", mi, key)
            for wi, mi in [(0, 16), (1, 4), (1, 8), (9, 5), (14, 17), (15, 21)]
            for key in expected["windows"][wi]["members"][mi]
        ]
        paths += [
            ("calibration", "replacement_cap"),
            ("calibration", "replacement_rule"),
            ("seed_allocation", "reserve_pool", "start"),
            ("sentinel", "extra_on_inconclusive"),
            ("sentinel", "escalated_ceiling_s"),
            ("windows", 9, "replacement"),
            ("windows", 1, "midpoint_after_ordinal"),
            ("windows", 1, "aliases", 0),
        ]
        for path in paths:
            with self.subTest(path=path):
                actual = copy.deepcopy(expected)
                target = actual
                for key in path[:-1]:
                    target = target[key]
                value = target[path[-1]]
                target[path[-1]] = (not value if isinstance(value, bool) else
                                    value + 1 if isinstance(value, int) else value + "_changed")
                found = check.differences(expected, actual)
                pointer = "$" + "".join(f"[{p}]" if isinstance(p, int) else "." + p for p in path)
                self.assertEqual([pointer], [d["path"] for d in found])
                self.assertTrue(found[0]["authority"])

    def test_missing_extra_types_and_order_are_not_hidden(self):
        expected = check.expected_manifest()
        changed = copy.deepcopy(expected)
        del changed["windows"][0]["members"][0]["pair"]
        changed["windows"][0]["members"][1]["unexpected"] = "extra"
        changed["calibration"]["replacement_cap"] = "6"
        changed["order"][1:3] = changed["order"][1:3][::-1]
        changed["windows"][9]["members"][5:7] = changed["windows"][9]["members"][5:7][::-1]
        changed["windows"].pop()
        found = check.differences(expected, changed)
        paths = {d["path"] for d in found}
        for path in (
            "$.windows[0].members[0].pair", "$.windows[0].members[1].unexpected",
            "$.calibration.replacement_cap", "$.order[1]", "$.order[2]", "$.windows",
            "$.windows[9].members[5].pair", "$.windows[9].members[6].pair",
        ):
            self.assertIn(path, paths)

    def test_byte_preservation_uses_original_bytes_including_whitespace(self):
        before = b'{"windows":[{"id":"W1","members":[]}]}'
        after = b'{"windows":[{"id": "W1", "members": []}]}'
        self.assertEqual(json.loads(before), json.loads(after))
        self.assertNotEqual(check.raw_window_objects(before)["W1"],
                            check.raw_window_objects(after)["W1"])
        # A nested key of the same name must not be mistaken for the top-level array.
        nested = b'{"metadata":{"windows":[]},"windows":[{"id":"W1","members":[]}]}'
        self.assertEqual(check.raw_window_objects(before), check.raw_window_objects(nested))


if __name__ == "__main__":
    unittest.main()
