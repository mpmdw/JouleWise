"""Gate-prune round 2, lane P2-CTL, PLAN2 row 5: the auxiliary-member match
records the exception it used to swallow; the refusal itself stays."""

from __future__ import annotations

import unittest
from unittest.mock import patch

from joulewise import controller
from joulewise.bundle import BundleError
from tests.test_controller_hazard_flags import load_attachment, read_flags
from tests.test_p2_ctl_calibration import StubVerify, _WindowCase



class AuxiliaryMatchErrorTests(_WindowCase):
    def unmatched(self):
        return (
            patch.object(controller, "_writer_launch_lineage",
                         side_effect=BundleError("member carries no writer lineage")),
            patch.object(controller, "_cli_config_source",
                         side_effect=ValueError("config source outside the repository 42")),
        )

    def test_hazard_refusal_names_the_swallowed_exception_and_flags_it(self) -> None:
        lineage, source = self.unmatched()
        with lineage, source, StubVerify().patch():
            with self.assertRaisesRegex(
                    ValueError,
                    r"auxiliary member match raised ValueError: config source outside the repository 42"):
                load_attachment(self.w, hazard=self.hazard)
        flags = self.flags("records.auxiliary_match_raised")
        self.assertEqual(len(flags), 1)
        value = flags[0]["observed"]
        value = value.get("value", value) if value.get("scope_unresolved") else value
        self.assertEqual(value["errors"], ["ValueError: config source outside the repository 42"])

    def test_legacy_refusal_text_is_unchanged(self) -> None:
        lineage, source = self.unmatched()
        with lineage, source, StubVerify().patch():
            with self.assertRaises(ValueError) as caught:
                load_attachment(self.w, hazard=None)
        self.assertEqual(str(caught.exception),
                         "revision_five evidence cannot be attached as instrument calibration")
        self.assertEqual(read_flags(self.custody), [])

if __name__ == "__main__":
    unittest.main()
