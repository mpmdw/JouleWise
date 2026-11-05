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

    def test_archived_import_binds_only_readers_and_is_removed(self):
        from joulewise.stored_generator import historical_reader_imports
        name = "joulewise.arm_readiness"
        self.assertNotIn(name, sys.modules)
        with historical_reader_imports():
            self.assertIs(sys.modules[name], readers)
            for issuer in ("generate_arm_receipt", "generate_freeze_receipt",
                           "generate_dry_run_receipt", "_consume_launch_capability"):
                self.assertFalse(hasattr(sys.modules[name], issuer))
        self.assertNotIn(name, sys.modules)

    def test_generator_execution_adapter_preserves_recorded_argv(self):
        from joulewise import evidence_replay
        command = evidence_replay._generator_command("/synthetic/generate_configs.py")
        self.assertEqual(command, [sys.executable, "-I", "-B",
                                   "/synthetic/generate_configs.py", "--check"])
        adapted = evidence_replay._stored_generator_check_command(command)
        self.assertEqual(adapted[:3], command[:3])
        self.assertTrue(adapted[3].endswith("scripts/check_stored_generator.py"))
        self.assertEqual(adapted[4:], command[3:])

    def test_archived_imports_restore_names_after_parallel_and_nested_loads(self):
        from concurrent.futures import ThreadPoolExecutor
        import joulewise
        from joulewise.stored_generator import historical_reader_imports

        def load(_):
            with historical_reader_imports():
                with historical_reader_imports():
                    from joulewise.arm_readiness import render_json
                    return render_json({"reader": True})

        with ThreadPoolExecutor(max_workers=2) as pool:
            self.assertEqual(list(pool.map(load, range(8))), [readers.render_json({"reader": True})] * 8)
        self.assertNotIn("joulewise.arm_readiness", sys.modules)
        self.assertNotIn("arm_readiness", vars(joulewise))

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
