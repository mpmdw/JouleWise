"""Read-only strict-validation regression over the retained run corpus."""

from __future__ import annotations

import json
import unittest
import sys
from pathlib import Path

from joulewise.cli import _STRICT_LEGACY_BUNDLE_IDENTITIES, validate_bundle


REPO_ROOT = Path(__file__).resolve().parents[1]
RUNS_ROOT = REPO_ROOT / "runs"


class RetainedCorpusStrictValidationTests(unittest.TestCase):
    def test_six_frozen_acceptance_gate_bundles_pass_strict_read_only(self) -> None:
        if not RUNS_ROOT.is_dir():
            message = (
                "ACCEPTANCE GATE SKIP: six frozen legacy corpus bundles require "
                "the retained runs/ corpus"
            )
            print(message, file=sys.stderr)
            self.skipTest(message)
        bundles = sorted(
            path.parent for path in RUNS_ROOT.rglob("summary_metrics.json")
        )
        self.assertTrue(bundles, "runs/ exists but contains no run bundles")
        by_identity = {}
        for bundle in bundles:
            metadata = json.loads((bundle / "metadata.json").read_text())
            identity = (metadata.get("run_id"), metadata.get("config_sha256"))
            if identity in _STRICT_LEGACY_BUNDLE_IDENTITIES:
                by_identity[identity] = bundle
        self.assertEqual(set(by_identity), set(_STRICT_LEGACY_BUNDLE_IDENTITIES))
        self.assertEqual(len(by_identity), 6)
        failures = {}
        for bundle in by_identity.values():
            problems = validate_bundle(bundle, strict=True)
            if problems:
                failures[str(bundle.relative_to(REPO_ROOT))] = problems
        self.assertEqual(failures, {})


if __name__ == "__main__":
    unittest.main()
