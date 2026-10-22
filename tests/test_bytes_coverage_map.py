"""Exhaustive field inventory of the primary's real synthetic CLI outputs (audit F10).

The checked-in map has one entry per JSON field path, with list indices folded to
``[]``. A new field must acquire a comparison or a specific exemption. Every
declared comparison is also exercised by changing that field alone in memory.
No stored campaign, measurement archive, or claim data is opened.
"""
from __future__ import annotations

import copy
import functools
import json
import math
import re
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tests import test_bytes_agreement as agreement


MAP = Path(__file__).parent / "fixtures/bytes/output_coverage.json"


def coverage_map():
    source = json.loads(MAP.read_text())
    result = {field: {"status": "compared", "reason": "A field mutation is detected by the real agreement comparer."}
              for field in source["compared"]}
    for group in source["exempt"]:
        for field in group["fields"]:
            if field in result:
                raise AssertionError("duplicate coverage decision: " + field)
            result[field] = {"status": "exempt", "reason": group["reason"]}
    return result


def fields(value, path=(), actual=()):
    """Enumerate leaves, retaining concrete addresses for mutation and stable schema paths."""
    if isinstance(value, dict) and value:
        for key, item in value.items():
            schema_key = "<session>" if re.fullmatch(r"bytes-(?:s[1-6]-)?p[12]", key) else key
            yield from fields(item, path + (schema_key,), actual + (key,))
    elif isinstance(value, list) and value:
        for index, item in enumerate(value):
            yield from fields(item, path + ("[]",), actual + (index,))
    else:
        yield "/".join(path), actual, value


def output_documents(root):
    def trim(value):
        if isinstance(value, dict):
            for key, item in value.items():
                if key == "meter_run_terms" and item:
                    value[key] = item[:1]
                trim(value[key])
        elif isinstance(value, list):
            for item in value:
                trim(item)
    documents = {str(p): json.loads(p.read_text()) for p in sorted((root / "out").glob("a-*/*.json"))}
    for value in documents.values():
        trim(value)
    return documents


def samples(documents):
    result = {}
    for filename, value in documents.items():
        for schema, actual, leaf in fields(value):
            key = Path(filename).name + "/" + schema
            # Prefer an evaluated value to null / an empty collection at an earlier stage.
            if key not in result or result[key][2] in (None, [], {}):
                result[key] = filename, actual, leaf
    return result


def corrupt(value):
    if isinstance(value, bool):
        return not value
    if isinstance(value, (int, float)) and math.isfinite(value):
        # A planted gross fault, not a bar: at least 1000 units and a 1000-fold
        # change (also large for VIF). The comparer's own registered bars decide.
        return value + max(1000, abs(value) * 1000)
    if isinstance(value, str):
        return value + "__coverage_fault__"
    return "__coverage_fault__"


@functools.lru_cache(maxsize=32)
def twin_document(path):
    return agreement.load(path)


def mutation_is_compared(root, documents, sample):
    filename, actual, leaf = sample
    # Per-run meter terms are repeated across passes, bases and without-assisted
    # descriptions. Retain one member per list to keep this field-level probe small;
    # the unabridged agreement suite compares every run.
    cache = dict(documents)
    cache[filename] = copy.copy(documents[filename])
    if not actual:
        return False  # Empty output table; inventory still requires a named exemption.
    parent = cache[filename]
    for key in actual[:-1]:
        parent[key] = copy.copy(parent[key])
        parent = parent[key]
    parent[actual[-1]] = corrupt(leaf)
    original = agreement.load
    def load(path):
        if str(path) in cache:
            return cache[str(path)]
        if Path(path).name.startswith("t-"):
            return twin_document(str(path))
        return original(path)
    # Fill the immutable twin cache before installing the primary-output loader.
    for path in (root / "out").glob("t-*.json"):
        twin_document(str(path))
    try:
        with mock.patch.object(agreement, "load", side_effect=load):
            return bool(agreement.compare_campaign(root).above())
    except (KeyError, TypeError, ValueError, IndexError, StopIteration):
        # Reading a field and then crashing is not a numerical/word comparison.
        return False


class OutputCoverageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="bytes-output-coverage-")
        cls.documents = {}
        for name in ("bytes", "minimum", "withheld"):
            root = Path(cls.temp.name) / name
            manifest = agreement.build(root, name)
            agreement.run_both(root, manifest)
            if agreement.compare_campaign(root).above():
                raise AssertionError(name + ": agreement must pass before coverage mutations")
            cls.documents.update(output_documents(root))
        cls.observed = samples(cls.documents)

    @classmethod
    def tearDownClass(cls):
        twin_document.cache_clear()
        cls.temp.cleanup()

    def test_every_output_field_is_compared_or_explicitly_exempt(self):
        mapping = coverage_map()
        self.assertEqual(set(self.observed) - set(mapping), set(), "new output fields need coverage decisions")
        for field in self.observed:
            entry = mapping[field]
            self.assertIn(entry["status"], ("compared", "exempt"), field)
            self.assertTrue(entry["reason"].strip(), field)

    def test_declared_comparisons_detect_changed_fields(self):
        mapping = coverage_map()
        for field, sample in self.observed.items():
            if mapping.get(field, {}).get("status") == "compared":
                with self.subTest(field=field):
                    root = Path(sample[0]).parents[2]
                    self.assertTrue(mutation_is_compared(root, self.documents, sample), field)

    def test_inventory_sees_an_added_nested_output_field(self):
        documents = copy.deepcopy(self.documents)
        path = next(p for p in documents if p.endswith("/h2.json") and documents[p])
        documents[path][0]["unregistered_output"] = 1
        self.assertTrue(set(samples(documents)) - set(self.observed))


if __name__ == "__main__":
    unittest.main()
