"""Read-only strict-validation regression over the retained run corpus."""

from __future__ import annotations

import unittest
from pathlib import Path

from joulewise.cli import validate_bundle


REPO_ROOT = Path(__file__).resolve().parents[1]
RUNS_ROOT = REPO_ROOT / "runs"


@unittest.skipUnless(RUNS_ROOT.is_dir(), "retained runs/ corpus is not present")
class RetainedCorpusStrictValidationTests(unittest.TestCase):
    def test_all_retained_run_bundles_pass_strict_read_only(self) -> None:
        bundles = sorted(
            path.parent for path in RUNS_ROOT.rglob("summary_metrics.json")
        )
        self.assertTrue(bundles, "runs/ exists but contains no run bundles")
        failures = {}
        for bundle in bundles:
            problems = validate_bundle(bundle, strict=True)
            if problems:
                failures[str(bundle.relative_to(REPO_ROOT))] = problems
        self.assertEqual(failures, {})


if __name__ == "__main__":
    unittest.main()
