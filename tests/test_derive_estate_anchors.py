from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from collections import Counter
from pathlib import Path

from scripts.derive_estate_anchors import (
    ESTATE_12_ANCHOR_SPEC,
    AnchorRefusal,
    derive_anchor_map,
    main,
    render_anchor_map,
)


ROOT = Path(__file__).resolve().parents[1]


def _row(anchor_id: str, pin: str, kind: str = "symbol") -> dict[str, str]:
    return {
        "anchor_id": anchor_id,
        "file": "sample.py",
        "symbol_or_content_pin": pin,
        "kind": kind,
    }


class DeriveEstateAnchorsTests(unittest.TestCase):
    def test_resolves_known_symbol_and_ast_range(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "sample.py").write_text(
                "# drift before the symbol\n\ndef known(value):\n    return value + 1\n",
                encoding="utf-8",
            )
            result = derive_anchor_map(root, [_row("known", "known", "symbol_range")])

        self.assertEqual(result["anchor_count"], 1)
        self.assertEqual(result["anchors"]["known"]["line"], 3)
        self.assertEqual(result["anchors"]["known"]["end_line"], 4)

    def _run_refusal(self, source: str, pin: str) -> tuple[int, dict[str, str]]:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "sample.py").write_text(source, encoding="utf-8")
            spec = root / "spec.json"
            spec.write_text(json.dumps([_row("target", pin)]), encoding="utf-8")
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                code = main([str(root), str(spec)])
        return code, json.loads(stderr.getvalue())

    def test_missing_symbol_refuses_with_named_nonzero_exit(self) -> None:
        code, refusal = self._run_refusal("def present():\n    pass\n", "missing")
        self.assertEqual(code, 2)
        self.assertEqual(refusal["status"], "REFUSE")
        self.assertEqual(refusal["reason"], "anchor_symbol_missing")
        self.assertEqual(refusal["anchor_id"], "target")

    def test_ambiguous_symbol_refuses_with_named_nonzero_exit(self) -> None:
        code, refusal = self._run_refusal(
            "def repeated():\n    pass\n\ndef repeated():\n    pass\n",
            "repeated",
        )
        self.assertEqual(code, 2)
        self.assertEqual(refusal["status"], "REFUSE")
        self.assertEqual(refusal["reason"], "anchor_symbol_ambiguous")
        self.assertIn("lines [1, 4]", refusal["detail"])

    def test_rendering_is_deterministic_and_anchor_keys_are_sorted(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "sample.py").write_text(
                "def alpha():\n    pass\n\ndef omega():\n    pass\n",
                encoding="utf-8",
            )
            spec = [_row("z-last", "omega"), _row("a-first", "alpha")]
            first = render_anchor_map(derive_anchor_map(root, spec))
            second = render_anchor_map(derive_anchor_map(root, list(reversed(spec))))

        self.assertEqual(first, second)
        decoded = json.loads(first)
        self.assertEqual(list(decoded["anchors"]), ["a-first", "z-last"])
        self.assertEqual(first, (json.dumps(decoded, indent=2, sort_keys=True) + "\n").encode())

    def test_embedded_estate_12_spec_resolves_against_this_checkout(self) -> None:
        result = derive_anchor_map(ROOT, ESTATE_12_ANCHOR_SPEC)
        legacy = [key for key in result["anchors"] if key.startswith("legacy.")]
        counts = Counter(row["kind"] for row in result["anchors"].values())

        self.assertEqual(len(legacy), 15)
        self.assertEqual(result["anchor_count"], len(ESTATE_12_ANCHOR_SPEC))
        self.assertEqual(
            result["anchors"]["legacy.14"]["symbol_or_content_pin"],
            "ReceiptHistoricalSemanticsTests."
            "test_pinset_is_byte_pinned_and_has_no_unreviewed_update_lane",
        )
        self.assertEqual(
            counts,
            {"content": 6, "content_range": 1, "symbol": 12, "symbol_range": 49},
        )

    def test_direct_api_exposes_named_refusal(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "sample.py").write_text("def one():\n    pass\n", encoding="utf-8")
            with self.assertRaises(AnchorRefusal) as caught:
                derive_anchor_map(root, [_row("missing", "two")])
        self.assertEqual(caught.exception.reason, "anchor_symbol_missing")


if __name__ == "__main__":
    unittest.main()
