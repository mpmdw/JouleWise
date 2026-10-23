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
    if set(source["campaigns"]) != set(agreement.CAMPAIGNS):
        raise AssertionError("coverage map must inventory every agreement campaign")
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
    documents = {str(p): json.loads(p.read_text()) for p in sorted((root / "out").glob("a-*/*.json"))}
    for value in documents.values():
        trim_meter_terms(value)
    return documents


def trim_meter_terms(value):
    """Retain fixed run identities covering every emitted schema, on BOTH sides.

    Full agreement compares every run. This projection keeps field mutations
    small without losing a field present only on a later run or breaking census.
    """
    if isinstance(value, dict):
        for key, item in value.items():
            if key == "meter_run_terms" and item:
                covered, keep = set(), []
                for run in sorted(item, key=lambda r: r["run_id"]):
                    schema = {field for field, _, _ in fields(run)}
                    if schema - covered:
                        keep.append(run)
                        covered.update(schema)
                value[key] = keep
            trim_meter_terms(value[key])
    elif isinstance(value, list):
        for item in value:
            trim_meter_terms(item)


def sample_key(filename, document, actual, leaf):
    """Choose by semantic row identity, never JSON list/dict encounter order."""
    node, identity = document, []
    keys = ("model", "pass_id", "session_id", "boundary", "basis", "selection",
            "run_id", "hypothesis", "term", "analysis")
    for key in actual:
        if isinstance(node, list):
            child = node[key]
            labels = tuple((k, str(child[k])) for k in keys if isinstance(child, dict) and k in child)
            # H1/H2's independent twin prints registered gross-primary answers.
            # Select that fixed scope first; the map explicitly exempts the
            # non-primary descriptive answer reruns, not their measured cells.
            priority = tuple(0 if not isinstance(child, dict) or child.get(k, expected) == expected else 1
                             for k, expected in (("selection", "primary"), ("basis", "gross primary"),
                                                 ("analysis", "primary"), ("role", "heldout")))
            identity.append((*priority, repr(labels) if labels else str(key)))
        node = node[key]
    return (leaf in (None, [], {}), filename, tuple(identity))


def samples(documents):
    result, ranks = {}, {}
    for filename, value in documents.items():
        for schema, actual, leaf in fields(value):
            key = Path(filename).name + "/" + schema
            rank = sample_key(filename, value, actual, leaf)
            if key not in result or rank < ranks[key]:
                result[key] = filename, actual, leaf
                ranks[key] = rank
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
    value = agreement.load(path)
    trim_meter_terms(value)
    return value


def mutation_is_compared(root, documents, sample):
    filename, actual, leaf = sample
    # Projection uses fixed run identities and the same rule on both programs.
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
        for name in agreement.CAMPAIGNS:
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


class SamplingTests(unittest.TestCase):
    def test_row_order_does_not_select_the_mutation_target(self):
        rows = [{"model": name, "basis": "gross primary", "selection": "primary", "mean_j": 1.0}
                for name in ("Z", "A")]
        for ordered in (rows, list(reversed(rows))):
            sample = samples({"model_estimates.json": ordered})["model_estimates.json/[]/mean_j"]
            self.assertEqual(ordered[sample[1][0]]["model"], "A")

    def test_meter_projection_preserves_a_later_runs_new_field(self):
        value = {"meter_run_terms": [{"run_id": "b", "late_field": 1}, {"run_id": "a", "energy": 1}]}
        before = {field for field, _, _ in fields(value)}
        trim_meter_terms(value)
        self.assertEqual({field for field, _, _ in fields(value)}, before)


if __name__ == "__main__":
    unittest.main()
