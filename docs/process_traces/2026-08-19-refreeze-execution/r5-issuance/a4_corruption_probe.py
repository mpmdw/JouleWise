#!/usr/bin/env python3
"""Record the A4 corrupted-rich-telemetry confirmation probe."""

from __future__ import annotations

import io
import sys
import unittest
from pathlib import Path

sys.path.insert(0, sys.argv[1])
suite = unittest.defaultTestLoader.loadTestsFromName(
    "tests.test_capture_pipeline_era.CapturePipelineEraTests.test_v3_corrupt_rich_telemetry_is_not_fail_open"
)
stream = io.StringIO()
result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
text = "A4_CORRUPTION_PROBE=p2-038.3\n" + stream.getvalue()
Path(__file__).with_name("a4-corruption-probe-transcript.txt").write_text(text, encoding="utf-8")
print(text, end="")
raise SystemExit(not result.wasSuccessful())
