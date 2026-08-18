"""Fast static guard for the decisive mint test's module references.

The decisive full-fixture leg (test_coordinated_report_and_pin_change_
refuses_against_floor_evidence) is excluded from the hosted CI matrix for
runtime, so a refactor that removes a module attribute the decisive test
references only surfaces hours into an operator replay (observed live
2026-08-17: mint1.STACK_IDENTITY_DOMAIN drift from #131 hit ED-QUAL-L4-1
fifteen minutes into fixture build). This test resolves every
`mint1.<attr>` / `generalized.<attr>` reference in the decisive test's
source against the imported modules in under a second, so the drift class
fails in CI instead of at the hardware.
"""

import ast
import unittest
from pathlib import Path

from scripts import mint_floor_artifact as mint1
from scripts import mint_floor_artifact_generalized as generalized


class DecisiveModuleReferenceResolutionTest(unittest.TestCase):
    def test_every_module_attribute_reference_resolves(self) -> None:
        source_path = Path(__file__).with_name(
            "test_mint_floor_artifact_generalized.py"
        )
        tree = ast.parse(source_path.read_text(encoding="utf-8"))
        modules = {"mint1": mint1, "generalized": generalized}
        missing = []
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Attribute)
                and isinstance(node.value, ast.Name)
                and node.value.id in modules
                and not hasattr(modules[node.value.id], node.attr)
            ):
                missing.append(
                    f"{node.value.id}.{node.attr} (line {node.lineno})"
                )
        self.assertEqual(
            missing,
            [],
            "decisive test references module attributes that no longer "
            "exist; fix the reference or restore the attribute before "
            "the drift reaches an operator replay: " + ", ".join(missing),
        )


if __name__ == "__main__":
    unittest.main()
