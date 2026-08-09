"""Self-tests and complete-corpus gate for receipt provenance analysis."""

from __future__ import annotations

from pathlib import Path
import unittest

from tests.receipt_provenance_analyzer import analyze_paths, analyze_sources
from tests.receipt_corpus import ReceiptCorpus


REPO_ROOT = Path(__file__).resolve().parents[1]


class ReceiptProvenanceAnalyzerTests(unittest.TestCase):
    def test_receipt_corpus_is_semantic_only(self) -> None:
        corpus = ReceiptCorpus(
            (
                {"event": "open", "session_id": "alpha"},
                {"event": "finalization", "session_id": "alpha"},
            )
        )
        self.assertEqual(len(corpus), 2)
        self.assertEqual(
            [row["event"] for row in corpus],
            ["open", "finalization"],
        )
        self.assertEqual(corpus.filter(event="open").one()["event"], "open")
        changed = corpus.replace(
            lambda row: row.get("event") == "open",
            {"event": "reservation", "session_id": "alpha"},
        )
        self.assertEqual(changed.one(event="reservation")["session_id"], "alpha")
        with self.assertRaises(TypeError):
            corpus[0]  # type: ignore[index]

    def test_renamed_filtered_collection_is_still_unsafe(self) -> None:
        source = """
def mutate(snapshot):
    origin = snapshot.receipts
    opaque = [item for item in origin if item.get('event') != 'ignored']
    return opaque[1:]
"""
        findings = analyze_sources({"renamed.py": source})
        self.assertTrue(
            any(
                finding.kind == "positional_receipt_access"
                and finding.detail == "opaque[1:]"
                for finding in findings
            ),
            findings,
        )

    def test_deepcopy_alias_is_still_unsafe_without_name_hints(self) -> None:
        source = """
import copy
def mutate(snapshot):
    opaque = copy.deepcopy(snapshot.receipts)
    opaque[1] = {'event': 'changed'}
"""
        findings = analyze_sources({"deepcopy.py": source})
        self.assertTrue(
            any(
                finding.kind == "positional_receipt_access"
                and finding.detail == "opaque[1]"
                for finding in findings
            ),
            findings,
        )

    def test_interprocedural_alias_and_unwrapped_return_are_rejected(self) -> None:
        source = """
import copy
def relay(value):
    return copy.deepcopy(value)
def mutate(snapshot):
    opaque = relay(snapshot.receipts)
    return opaque[0]
"""
        findings = analyze_sources({"helper.py": source})
        self.assertTrue(
            any(finding.kind == "unwrapped_receipt_return" for finding in findings),
            findings,
        )
        self.assertTrue(
            any(finding.kind == "positional_receipt_access" for finding in findings),
            findings,
        )

    def test_keyword_only_helper_alias_is_rejected(self) -> None:
        source = """
def relay(*, value):
    return value
def mutate(snapshot):
    opaque = relay(value=snapshot.receipts)
    return opaque[0]
"""
        findings = analyze_sources({"keyword_helper.py": source})
        self.assertTrue(
            any(finding.kind == "unwrapped_receipt_return" for finding in findings),
            findings,
        )
        self.assertTrue(
            any(finding.kind == "positional_receipt_access" for finding in findings),
            findings,
        )

    def test_nested_comprehension_alias_is_rejected(self) -> None:
        source = """
def mutate(snapshot):
    opaque = [item for batch in (snapshot.receipts,) for item in batch]
    return opaque[0]
"""
        findings = analyze_sources({"nested_comprehension.py": source})
        self.assertTrue(
            any(finding.kind == "positional_receipt_access" for finding in findings),
            findings,
        )

    def test_safe_semantic_and_nonreceipt_operations_are_accepted(self) -> None:
        source = """
from tests.receipt_corpus import ReceiptCorpus
def safe(rows: ReceiptCorpus):
    events = [row['event'] for row in rows]
    selected = next(row for row in rows if row.get('event') == 'open')
    exact = rows.one(event='open')
    ordinary = [1, 2, 3]
    return events, selected['event'], exact['event'], ordinary[1]
def wrapped(rows: ReceiptCorpus):
    return ReceiptCorpus(row for row in rows if row.get('event'))
"""
        self.assertEqual(analyze_sources({"safe.py": source}), [])

    def test_complete_calibration_test_corpus_has_no_findings(self) -> None:
        paths = sorted((REPO_ROOT / "tests").glob("test_calibration*.py"))
        paths.append(REPO_ROOT / "tests" / "test_powermetrics_fiducial.py")
        self.assertEqual(analyze_paths(paths), [])


if __name__ == "__main__":
    unittest.main()
