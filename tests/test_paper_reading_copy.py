from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT / "scripts"))
import render_reading_copy as module


class ReadingCopyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.paper = self.root / "paper"
        self.figures = self.paper / "figures"
        self.output = self.paper / "build" / "out" / "reading.md"
        self.figures.mkdir(parents=True)
        for number in (3, 4, 5):
            (self.figures / f"fig{number}.svg").write_text(
                f"<svg><title>Figure {number}</title></svg>\n", encoding="utf-8"
            )

        self.draft = self.paper / "draft.md"
        self.draft.write_text(
            """# Fixture

Text [1] and [3]. `code [2]`.
Inline math \\( [2,3] \\).
Split math \\(a +
b\\). The literal `<!-- -->` is documentation.

<!-- build [FILL:ROW-99] -->

[FILL:ROW-01] — “old explanation naming registry row ROW-01.”
[FILL:R_small_p[LENGTH]_abs]

![Figure 4. Fixture.](figures/fig4.svg)
![Figure 5. Fixture.](figures/fig5.svg)

## 11. References

<!-- assembled -->

## Appendix

\\[ [2] \\]
""",
            encoding="utf-8",
        )
        self.registry = self.paper / "registry.md"
        self.registry.write_text(
            """| Draft site | Exact marker | Role |
|---|---|---|
| ROW-01 — requested energy result, line 7 | marker | fixture / energy result |
| ROW-99 — comment-only result, line 5 | marker | fixture / comment result |

| Exact token | Producer | Campaign / cell role |
|---|---|---|
| `[R_small_p[LENGTH]_abs]` | result | fixture / absolute independent-edge ratio |
""",
            encoding="utf-8",
        )
        self.bibliography = self.paper / "old.md"
        self.bibliography.write_text(
            """# Old

Cites [1] and [3].

## 11. References

1. First reference.
2. Orphan reference.
3. Third reference.
""",
            encoding="utf-8",
        )
        self.plan = self.paper / "plan.md"
        self.plan.write_text(
            """| Old | New | Old | New | Old | New |
|---:|---:|---:|---:|---:|---:|
| 1 | 1 | 3 | 2 | 3 | 2 |
""",
            encoding="utf-8",
        )
        self.kernel = self.root / "kernel.json"
        self.kernel.write_text('{"tasks":{"KERNEL-ROW-01":{}}}\n', encoding="utf-8")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def render(self):
        return module.render_reading_copy(
            draft_path=self.draft,
            output_path=self.output,
            registry_path=self.registry,
            bibliography_source_path=self.bibliography,
            bibliography_plan_path=self.plan,
            figures_dir=self.figures,
            state_kernel_path=self.kernel,
        )

    def test_small_fixture_renders_comments_fills_references_and_figures(self) -> None:
        result = self.render()
        self.assertNotIn("<!--", result.text.replace("`<!-- -->`", ""))
        self.assertNotIn("ROW-01", result.text)
        self.assertNotIn("old explanation", result.text)
        self.assertIn("[not yet measured: requested energy result]", result.text)
        self.assertIn("[not yet measured: absolute independent-edge ratio]", result.text)
        self.assertIn("Text [1] and [2]. `code [2]`.", result.text)
        self.assertIn("Inline math \\( [2,3] \\).", result.text)
        self.assertIn("Split math \\(a + b\\).", result.text)
        self.assertIn("The literal `<!-- -->` is documentation.", result.text)
        self.assertIn("\\[ [2] \\]", result.text)
        self.assertIn("1. First reference.\n2. Third reference.", result.text)
        self.assertIn("../../figures/fig4.svg", result.text)
        self.assertIn("../../figures/fig5.svg", result.text)
        self.assertEqual(result.fill_sites, 2)
        self.assertEqual(result.reference_count, 2)
        self.assertEqual(result.figure_count, 2)

    def test_validation_rejects_registry_and_kernel_names(self) -> None:
        registry = module.parse_registry(self.registry.read_text(encoding="utf-8"))
        for survivor in ("ROW-01", "KERNEL-ROW-01"):
            with self.subTest(survivor=survivor):
                with self.assertRaises(module.ReadingCopyError):
                    module.validate_rendered_text(
                        f"visible {survivor}\n",
                        registry_ids=registry.internal_ids,
                        kernel_rows=frozenset({"KERNEL-ROW-01"}),
                    )

    def test_unknown_fill_and_missing_figure_fail_closed(self) -> None:
        original = self.draft.read_text(encoding="utf-8")
        for replacement in ("[FILL:UNKNOWN-01]", "![missing](figures/missing.svg)"):
            with self.subTest(replacement=replacement):
                self.draft.write_text(original + "\n" + replacement + "\n", encoding="utf-8")
                with self.assertRaises(module.ReadingCopyError):
                    self.render()


if __name__ == "__main__":
    unittest.main()
