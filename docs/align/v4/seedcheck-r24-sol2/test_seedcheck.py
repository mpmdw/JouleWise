"""Mutation checks for the independent comparator; no production imports."""

import copy
import importlib.util
import json
from pathlib import Path
import unittest


spec = importlib.util.spec_from_file_location("independent_r24", Path(__file__).with_name("check_manifest.py"))
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class SeedCheckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.candidate = (checker.ROOT / checker.MANIFEST).read_bytes()
        cls.prior = checker.git_bytes(checker.PRIOR, checker.MANIFEST)
        cls.manifest = checker.load_json(cls.candidate)

    def test_exact_candidate(self):
        result = checker.check(self.candidate, self.prior)
        self.assertEqual(result["verdict"], "MATCH")
        self.assertEqual(result["differences"], [])
        self.assertTrue(all(result["checks"].values()))

    def test_every_member_field_mutation_is_located(self):
        # Cover both role-bearing W1 records and role-by-pool C/T records,
        # including a reserve and a frozen test window. Bypass no fields.
        for wi in (0, 1, 9, 15):
            for key, value in self.manifest["windows"][wi]["members"][5].items():
                with self.subTest(window=wi, field=key):
                    altered = copy.deepcopy(self.manifest)
                    altered["windows"][wi]["members"][5][key] = (
                        value + 1 if isinstance(value, int) else value + "_changed")
                    result = checker.check(json.dumps(altered).encode(), self.prior)
                    self.assertEqual(result["verdict"], "MISMATCH")
                    self.assertIn(f"$.windows[{wi}].members[5].{key}",
                                  [d["path"] for d in result["differences"]])
                    self.assertTrue(all(d["authority"] for d in result["differences"]))

    def test_order_missing_and_extra_fields_are_reported_together(self):
        altered = copy.deepcopy(self.manifest)
        altered["order"][1:3] = reversed(altered["order"][1:3])
        altered["windows"][9]["members"].reverse()
        del altered["calibration"]["replacement_cap"]
        altered["sentinel"]["unexpected"] = True
        result = checker.check(json.dumps(altered).encode(), self.prior)
        paths = {d["path"] for d in result["differences"]}
        self.assertEqual(result["verdict"], "MISMATCH")
        self.assertTrue({"$.order[1]", "$.calibration.replacement_cap",
                         "$.sentinel.unexpected", "$.windows[9].members[0].ordinal"} <= paths)

    def test_wrong_types_and_multiple_differences(self):
        diffs = checker.differences({"cap": 1, "rows": [1, 2]}, {"cap": True, "rows": [3]})
        self.assertEqual({d["path"] for d in diffs}, {"$.cap", "$.rows.length", "$.rows[0]"})

    def test_duplicate_keys_refused(self):
        with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
            checker.load_json(b'{"a": 1, "a": 2}')

    def test_semantically_equal_whitespace_change_breaks_r15_bytes(self):
        changed_prior = self.prior.replace(b'"id": "T1"', b'"id" : "T1"', 1)
        self.assertNotEqual(changed_prior, self.prior)
        self.assertEqual(json.loads(changed_prior), json.loads(self.prior))
        result = checker.check(self.candidate, changed_prior)
        self.assertEqual(result["verdict"], "MISMATCH")
        self.assertFalse(result["checks"]["r15_T1_raw_bytes"])
        self.assertTrue(result["checks"]["r15_T2_raw_bytes"])

    def test_prior_seed_change_cannot_hide_behind_candidate_match(self):
        changed_prior = self.prior.replace(b'"seed_index": 66', b'"seed_index": 67', 1)
        self.assertNotEqual(changed_prior, self.prior)
        result = checker.check(self.candidate, changed_prior)
        self.assertEqual(result["verdict"], "MISMATCH")
        self.assertTrue(result["checks"]["all_json_fields"])
        self.assertFalse(result["checks"]["r15_T1_raw_bytes"])


if __name__ == "__main__":
    unittest.main()
