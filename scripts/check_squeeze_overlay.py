#!/usr/bin/env python3
"""Run one synthetic unittest module against local, pinned v4 runner code.

No fetch, model, power sampler, campaign, or measurement files. Main deliberately
doesn't carry ALIGN; a temporary import overlay avoids restoring that lane here.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "e901eb2a480d51377a494be9d797733dfcd0220b"
MODULES = ("records.py", "interfaces.py", "runner.py")


def main() -> int:
    sys.path.insert(0, str(ROOT))
    import joulewise.align

    # Explicitly stay in the clone; ignore host-specific data/model config paths.
    with tempfile.TemporaryDirectory(prefix="squeeze-overlay-", dir=ROOT) as directory:
        overlay = Path(directory)
        for name in MODULES:
            source = "joulewise/align/" + name
            try:
                raw = subprocess.check_output(["git", "-C", str(ROOT), "show", SOURCE + ":" + source])
            except subprocess.CalledProcessError:
                print("Pinned code objects unavailable locally; no network attempted.", file=sys.stderr)
                return 2
            (overlay / name).write_bytes(raw)
            print(source, hashlib.sha256(raw).hexdigest(), flush=True)
        joulewise.align.__path__ = [str(overlay), *joulewise.align.__path__]
        suite = unittest.defaultTestLoader.loadTestsFromName("tests.align.test_squeeze_harness")
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        return 0 if result.wasSuccessful() and not result.skipped else 1


if __name__ == "__main__":
    raise SystemExit(main())
