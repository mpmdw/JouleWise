from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
GENERATOR_PATH = (
    REPO_ROOT
    / "configs"
    / "campaigns"
    / "metrology_v1"
    / "micro_delta"
    / "generate_configs.py"
)
SPEC = importlib.util.spec_from_file_location("microdelta_generate_configs", GENERATOR_PATH)
assert SPEC is not None and SPEC.loader is not None
GENERATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GENERATOR)


def snapshot(root: Path) -> dict[str, bytes]:
    return {
        str(path.relative_to(root)): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


class MicroDeltaGenerateConfigsTests(unittest.TestCase):
    def test_unordered_duplicate_k_values_match_canonical_form(self) -> None:
        self.assertEqual(
            GENERATOR.parse_k_values(
                ["--k", "128", "--k", "64", "--k", "128", "--k", "64"]
            ),
            [64, 128],
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            unordered = root / "unordered"
            canonical = root / "canonical"

            GENERATOR.generate_configs([128, 64, 128, 64], unordered)
            GENERATOR.generate_configs([64, 128], canonical)

            self.assertEqual(snapshot(unordered), snapshot(canonical))

    def test_stale_k_outputs_are_refused_before_any_write(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            out = Path(temp_dir)
            GENERATOR.generate_configs([64, 128], out)
            before = snapshot(out)

            with self.assertRaisesRegex(
                ValueError, r"refusing to mix.*k0128"
            ):
                GENERATOR.generate_configs([64], out)

            self.assertEqual(snapshot(out), before)

    def test_regenerate_twice_is_byte_identical(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            out = Path(temp_dir)
            GENERATOR.generate_configs([64, 128], out)
            first = snapshot(out)

            GENERATOR.generate_configs([128, 64, 64], out)

            self.assertEqual(snapshot(out), first)

    def test_k_values_remain_bounded_and_positive(self) -> None:
        with self.assertRaisesRegex(ValueError, "positive integer"):
            GENERATOR.canonicalize_k_values([0])
        with self.assertRaisesRegex(ValueError, "context window"):
            GENERATOR.canonicalize_k_values(
                [GENERATOR.MODEL["context_window"] - GENERATOR.BASE_OUTPUT_TOKENS + 1]
            )


if __name__ == "__main__":
    unittest.main()
