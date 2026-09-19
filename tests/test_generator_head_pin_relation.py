"""Generation checks pin ordering; runtime evaluation owns chain ancestry."""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from tests.test_d117_floor_qwen3_v5_generate import (
    FLOORS,
    ROOT,
    file_snapshot,
    fixture_prefill_pin,
    load_generator,
)


class GeneratorHeadPinRelationTests(unittest.TestCase):
    maxDiff = None

    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory(prefix="head-pin-relation-", dir="/tmp")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.repository = self.root / "repository"
        subprocess.run(
            ("git", "clone", "-q", "--shared", str(ROOT), str(self.repository)),
            check=True,
            capture_output=True,
        )
        # Include uncommitted generator edits in both in-process and CLI tests.
        for _, pack_id, *_ in FLOORS:
            relative = Path("configs/campaigns") / pack_id / "generate_configs.py"
            shutil.copy2(ROOT / relative, self.repository / relative)
        self.prefill_pin = fixture_prefill_pin(self.root)

    def generators(self):
        for _, pack_id, *_ in FLOORS:
            module = load_generator(pack_id, repository=self.repository)
            module.configure_prefill_pin(self.prefill_pin)
            yield module

    def cutoff(self, module) -> dict:
        acceptance = self.repository / module.acceptance_pin()["rel"]
        return json.loads(acceptance.read_text(encoding="utf-8"))["ledger_cutoff"]

    def cutoff_pin(self, module) -> dict:
        cutoff = self.cutoff(module)
        return {key: cutoff[key] for key in ("sequence", "head_digest", "ledger_schema")}

    def write_pin(self, module, pin) -> None:
        (self.repository / module.LEDGER_HEAD_REL).write_text(
            json.dumps(pin, indent=2) + "\n", encoding="utf-8"
        )

    def assert_refused_without_writes(self, module, message: str) -> None:
        output = self.root / f"{module.PACK_REL.name}-refused"
        self.assertFalse(output.exists())
        with self.assertRaises(ValueError) as caught:
            module.generate(output)
        self.assertEqual(str(caught.exception), message)
        self.assertFalse(output.exists(), "refusal must precede every output write")

    def test_advanced_pin_emits_identical_bytes_to_cutoff(self) -> None:
        """Any later digest is accepted here; ancestry is evaluation-owned."""
        for module in self.generators():
            with self.subTest(pack_id=module.PACK_REL.name):
                pin = self.cutoff_pin(module)
                self.write_pin(module, pin)
                at_cutoff = self.root / f"{module.PACK_REL.name}-cutoff"
                baseline = module.generate(at_cutoff)
                baseline_bytes = file_snapshot(at_cutoff)
                self.assertTrue(baseline_bytes)
                self.write_pin(
                    module, {**pin, "sequence": pin["sequence"] + 100, "head_digest": "f" * 64}
                )
                advanced = self.root / f"{module.PACK_REL.name}-advanced"
                self.assertEqual(module.generate(advanced), baseline)
                # Compare the entire emitted tree, including generator and sidecars.
                self.assertEqual(file_snapshot(advanced), baseline_bytes)

    def test_rolled_back_pin_refuses_before_any_write(self) -> None:
        for module in self.generators():
            with self.subTest(pack_id=module.PACK_REL.name):
                pin = self.cutoff_pin(module)
                self.write_pin(module, {**pin, "sequence": pin["sequence"] - 1})
                self.assert_refused_without_writes(
                    module,
                    f"ledger head pin behind the acceptance cutoff: {module.LEDGER_HEAD_REL}",
                )

    def test_schema_mismatch_refuses(self) -> None:
        for module in self.generators():
            with self.subTest(pack_id=module.PACK_REL.name):
                self.write_pin(module, {**self.cutoff_pin(module), "ledger_schema": "altered"})
                self.assert_refused_without_writes(
                    module, f"ledger head pin schema mismatch: {module.LEDGER_HEAD_REL}"
                )

    def test_equal_sequence_with_different_digest_refuses(self) -> None:
        for module in self.generators():
            with self.subTest(pack_id=module.PACK_REL.name):
                pin = self.cutoff_pin(module)
                self.assertNotEqual(pin["head_digest"], "f" * 64)
                self.write_pin(module, {**pin, "head_digest": "f" * 64})
                self.assert_refused_without_writes(
                    module,
                    f"ledger head pin diverged from the acceptance cutoff: {module.LEDGER_HEAD_REL}",
                )

    def test_non_integer_sequence_refuses_shape(self) -> None:
        for module in self.generators():
            with self.subTest(pack_id=module.PACK_REL.name):
                for sequence in (True, "176", 176.0, None):
                    with self.subTest(sequence=sequence):
                        self.write_pin(module, {**self.cutoff_pin(module), "sequence": sequence})
                        self.assert_refused_without_writes(module, "ledger head pin shape invalid")

    def test_missing_or_extra_keys_refuse_shape(self) -> None:
        for module in self.generators():
            with self.subTest(pack_id=module.PACK_REL.name):
                pin = self.cutoff_pin(module)
                malformed = {"extra": {**pin, "extra": "unexpected"}}
                malformed.update(
                    (f"missing-{key}", {name: value for name, value in pin.items() if name != key})
                    for key in pin
                )
                malformed.update({"array": [], "null": None})
                for label, value in malformed.items():
                    with self.subTest(shape=label):
                        self.write_pin(module, value)
                        self.assert_refused_without_writes(module, "ledger head pin shape invalid")

    def test_acceptance_byte_drift_refuses_before_head_check(self) -> None:
        for module in self.generators():
            with self.subTest(pack_id=module.PACK_REL.name):
                acceptance_rel = module.acceptance_pin()["rel"]
                acceptance = self.repository / acceptance_rel
                original = acceptance.read_bytes()
                # An invalid head would raise the shape refusal if checked first.
                self.write_pin(module, {})
                try:
                    acceptance.write_bytes(original + b"\n")
                    self.assert_refused_without_writes(
                        module, f"pinned input drifted: {acceptance_rel}"
                    )
                finally:
                    acceptance.write_bytes(original)

    def test_acceptance_cutoff_digest_must_match_generator_binding(self) -> None:
        for module in self.generators():
            with self.subTest(pack_id=module.PACK_REL.name):
                self.write_pin(module, self.cutoff_pin(module))
                self.assertNotEqual(module.LEDGER_HEAD_SHA256, "f" * 64)
                module.LEDGER_HEAD_SHA256 = "f" * 64
                self.assert_refused_without_writes(
                    module, f"acceptance ledger cutoff drifted: {module.acceptance_pin()['rel']}"
                )

    def test_manifest_issued_head_is_exactly_the_acceptance_binding(self) -> None:
        for module in self.generators():
            with self.subTest(pack_id=module.PACK_REL.name):
                pin = self.cutoff_pin(module)
                self.write_pin(
                    module, {**pin, "sequence": pin["sequence"] + 100, "head_digest": "f" * 64}
                )
                output = self.root / f"{module.PACK_REL.name}-manifest"
                module.generate(output)
                tree = json.loads(
                    (output / module.PACK_REL / "plan_tree.json").read_text(encoding="utf-8")
                )
                self.assertEqual(
                    tree["acceptance_policy"]["issued_ledger_head"],
                    {"path": module.LEDGER_HEAD_REL.as_posix(), "head_sha256": pin["head_digest"]},
                )
                self.assertEqual(module.LEDGER_HEAD_SHA256, pin["head_digest"])

    def test_check_subprocess_uses_real_committed_pin_without_fixture(self) -> None:
        for module in self.generators():
            with self.subTest(pack_id=module.PACK_REL.name):
                path = self.repository / module.LEDGER_HEAD_REL
                committed = subprocess.check_output(
                    ("git", "show", f"HEAD:{module.LEDGER_HEAD_REL.as_posix()}"),
                    cwd=self.repository,
                )
                self.assertEqual(path.read_bytes(), committed)
                output = self.root / f"{module.PACK_REL.name}-check"
                module.generate(output)
                checked = subprocess.run(
                    (
                        sys.executable,
                        str(self.repository / module.PACK_REL / "generate_configs.py"),
                        "--check", "--output-root", str(output),
                    ),
                    cwd=self.repository,
                    env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)
                self.assertIn("verified", checked.stdout)
                self.assertEqual(path.read_bytes(), committed)


if __name__ == "__main__":
    unittest.main()
