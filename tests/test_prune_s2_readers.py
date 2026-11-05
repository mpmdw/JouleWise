"""Synthetic golden equivalence against pre-prune reader source, never evidence."""
from __future__ import annotations

import copy
import os
from pathlib import Path
import subprocess
import sys
import types
import unittest

from joulewise import receipt_readers as readers
from tests import test_arm_readiness_schemas as fixtures

BASE = "92026c1849c0f053e56bdac6110c079211db2c31"


class ReaderEquivalenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Git reads source objects only. The frozen module has no import-time
        # probes. Adapt its single retired eager import to the byte-identical
        # extracted OFF comparator; no original function body is modified.
        source = subprocess.check_output(
            ["git", "show", BASE + ":joulewise/arm_readiness.py"],
            env=dict(os.environ, GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_NOSYSTEM="1"),
            text=True,
        ).replace("from joulewise import network_time_off as _network_time_off",
                  "from joulewise.hazards import network_time as _network_time_off")
        cls.baseline = types.ModuleType("_prune_s2_baseline")
        cls.baseline.__file__ = readers.__file__
        sys.modules[cls.baseline.__name__] = cls.baseline
        exec(compile(source, "<pre-prune reader source>", "exec"), vars(cls.baseline))

    @classmethod
    def tearDownClass(cls):
        sys.modules.pop(cls.baseline.__name__, None)

    def test_canonical_bytes_hashes_and_sidecars(self):
        for value in ({"unicode": "é雪", "null": None}, [False, 1, 1.25], {"nested": ["a\nb"]}):
            with self.subTest(value=value):
                old = self.baseline.render_json(value)
                self.assertEqual(readers.render_json(value), old)
                self.assertEqual(readers.sha256_bytes(old), self.baseline.sha256_bytes(old))
                self.assertEqual(readers.gnu_sidecar(readers.sha256_bytes(old), "receipt.json"),
                                 self.baseline.gnu_sidecar(self.baseline.sha256_bytes(old), "receipt.json"))

    def test_json_rejection_and_canonical_policy(self):
        for raw in (b'{"x":1,"x":2}', b'{"x":NaN}', b'{"x":1e999}', b'\xff',
                    b'{"x": 1}', b'{"x":1}\n'):
            for canonical in (False, True):
                outcomes = []
                for module in (self.baseline, readers):
                    try:
                        outcomes.append(("value", module.parse_json_bytes(raw, require_canonical=canonical)))
                    except ValueError as error:
                        outcomes.append(("refusal", getattr(error, "reason_code", None), str(error)))
                self.assertEqual(*outcomes)

    def test_stored_receipt_versions_and_unknown_key_refusals(self):
        root = Path("/synthetic-prune-context")
        cases = [
            ("validate_freeze_receipt", fixtures.sample_freeze()),
            ("validate_freeze_receipt", fixtures.sample_freeze_v2()),
            ("validate_arm_receipt", fixtures.sample_arm(root)),
            ("validate_dry_run_receipt", fixtures.sample_dry_run(root)),
            ("validate_evidence_receipt", fixtures.sample_evidence()),
        ]
        for function, value in cases:
            for extra in (False, True):
                obj = copy.deepcopy(value)
                if extra:
                    obj["unregistered"] = True
                outcomes = []
                for module in (self.baseline, readers):
                    try:
                        outcomes.append(("value", getattr(module, function)(copy.deepcopy(obj))))
                    except ValueError as error:
                        outcomes.append(("refusal", getattr(error, "reason_code", None), str(error)))
                self.assertEqual(*outcomes, (function, extra))


if __name__ == "__main__":
    unittest.main()
