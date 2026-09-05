from __future__ import annotations

import copy
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tests import test_d117_contrast_v5_pack


class GammaUnitRosterGuardTests(unittest.TestCase):
    def test_generate_refuses_coherent_roster_rewrite_before_tree_publish(self) -> None:
        helper = test_d117_contrast_v5_pack.D117ContrastV5PackTests(
            methodName="test_gamma_identity_roster_is_exact_and_rejects_three_units"
        )
        helper.setUp()

        with tempfile.TemporaryDirectory(prefix="gamma-roster-boundary-") as temp:
            output_root = Path(temp)
            helper.configure(helper.write_prefill_pin(output_root))
            real_build_tree = helper.generator.build_tree

            def rewrite_roster(*args, **kwargs):
                tree = real_build_tree(*args, **kwargs)
                units = tree["arm_attachments"]["identity_pin_projection"][
                    "identity_units"
                ]
                a_producer = copy.deepcopy(units[0]["producer_plan_reference"])
                b_producer = copy.deepcopy(units[2]["producer_plan_reference"])
                for unit, unit_id, producer in zip(
                    units,
                    ("C/decode", "C/prefill_p512", "D/decode", "D/prefill_p512"),
                    (b_producer, b_producer, a_producer, a_producer),
                    strict=True,
                ):
                    unit["identity_unit_id"] = unit_id
                    unit["producer_plan_reference"] = copy.deepcopy(producer)
                return tree

            with (
                mock.patch.object(
                    helper.generator, "build_tree", side_effect=rewrite_roster
                ),
                self.assertRaisesRegex(
                    ValueError, "gamma_identity_unit_roster_invalid"
                ),
            ):
                helper.generate_pack(output_root)

            plan_tree = (
                output_root
                / "configs/campaigns"
                / test_d117_contrast_v5_pack.PACK_ID
                / "plan_tree.json"
            )
            self.assertFalse(plan_tree.exists())


if __name__ == "__main__":
    unittest.main()
