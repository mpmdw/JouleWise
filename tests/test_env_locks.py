"""REPRO-1 CI check: environment lockfiles exist, are pinned, and match the corpus.

Spec: docs/specs/c027/doc-009_repro-001_authority_and_repro.md (Part B, REPRO-1,
decision 4). The cross-check leg is skipped when the runs/ corpus is absent
(clean CI checkout without bundles).
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ENV_DIR = REPO_ROOT / "env"
LOCKFILES = (
    ENV_DIR / "analysis-lock.txt",
    ENV_DIR / "mac-measurement-lock.txt",
)
CANONICAL_BUNDLE_METADATA = REPO_ROOT / "runs" / "example-mac-mlx-local__r1" / "metadata.json"


def _requirement_lines(path: Path) -> list[str]:
    lines = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line and not line.startswith("#"):
            lines.append(line)
    return lines


class TestEnvLocks(unittest.TestCase):
    def test_lockfiles_exist_and_are_pinned(self) -> None:
        for path in LOCKFILES:
            with self.subTest(lockfile=path.name):
                self.assertTrue(path.is_file(), f"missing lockfile: {path}")
                lines = _requirement_lines(path)
                self.assertTrue(lines, f"lockfile has no requirement lines: {path}")
                for line in lines:
                    # Lock-what-IS: PEP 508 direct references (`name @ url`) are
                    # recorded verbatim (e.g. Homebrew's vendored wheel).
                    self.assertTrue(
                        "==" in line or " @ " in line,
                        f"unpinned line in {path.name}: {line!r}",
                    )

    def test_mac_lock_matches_canonical_bundle(self) -> None:
        if not CANONICAL_BUNDLE_METADATA.is_file():
            self.skipTest("runs/ corpus absent (clean checkout without bundles)")
        metadata = json.loads(CANONICAL_BUNDLE_METADATA.read_text(encoding="utf-8"))
        prepare = metadata["adapters"]["runtime"]["prepare_metadata"]
        expected = {
            "mlx": prepare["mlx_version"],
            "mlx-lm": prepare["mlx_lm_version"],
        }
        # The bundle metadata does not record a transformers version, so that
        # leg of the spec's cross-check is not enforceable here (see env/README.md).
        pins = {}
        for line in _requirement_lines(ENV_DIR / "mac-measurement-lock.txt"):
            if "==" in line:
                name, _, version = line.partition("==")
                pins[name.strip().lower()] = version.strip()
        for package, expected_version in expected.items():
            with self.subTest(package=package):
                self.assertEqual(
                    pins.get(package),
                    expected_version,
                    f"mac lock pin for {package} does not match canonical bundle",
                )


if __name__ == "__main__":
    unittest.main()
