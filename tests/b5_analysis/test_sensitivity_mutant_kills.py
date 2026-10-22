"""Public sensitivity-pass boundaries on fabricated arithmetic inputs."""
from copy import deepcopy
from dataclasses import replace
import unittest

from joulewise.detection_floor import TRANSPORT_RULE_ID
from joulewise.b5_analysis.bracket import BMax
from joulewise.b5_analysis.windows import AnalysisRefusal
from tests.b5_analysis.test_sensitivity import PassHarness


class SensitivityBoundaryTests(unittest.TestCase):
    def test_attainer_may_be_the_terminal_receipt(self):
        """An attainer at T=500 is included in the prefix. Kills M04949."""
        record = PassHarness().call(BMax(.0625, 500, 500))
        # .0625 = 1/16 s is exact binary64; this test pins integer boundaries.
        self.assertEqual(record["b_max"], {"value_s": .0625, "attained_by_sequence": 500, "T": 500})

    def test_terminal_count_must_be_positive(self):
        """Zero and negative terminal receipt counts refuse. Kills M04846."""
        h = PassHarness()
        for terminal in (0, -1):
            with self.subTest(terminal=terminal), self.assertRaisesRegex(AnalysisRefusal, "^sensitivity_inputs_invalid$"):
                h.call(BMax(.0625, None, terminal))

    def test_transported_floor_takes_the_larger_later_source(self):
        """A same-pack transport composes unequal source floors. Kills M05008."""
        h = PassHarness()
        # Add a second ALPHA source, with separate extraction components. Both
        # sources share a pack/stack; transport validators require matching
        # backend/metric/window/stack, but do not require equal floor values.
        # Loader and member physics remain the existing named arithmetic seams.
        extra = deepcopy(h.f.artifact["cells"][0])
        extra["cell_id"] = "minted-alpha-high"
        for kind, component in (("absolute", "component-31"), ("comparative", "component-37")):
            extra["provenance"][kind]["calibration_cell_id"] = component
            h.f.specs["alpha"]["cells"].append({"cell_id": component, "kind": kind})
            source = next(row for row in h.f.reports["alpha"]["cells"] if row["kind"] == kind)
            h.f.reports["alpha"]["cells"].append({**deepcopy(source), "cell_id": component})
        h.f.artifact["cells"].append(extra)
        original_resolutions = h.resolutions

        def resolutions():
            rows = original_resolutions()
            alpha = next(row for row in rows if row.source_cell_ids == ("minted-alpha",))
            beta = next(row for row in rows if row.source_cell_ids == ("minted-beta",))
            return [replace(alpha, status="transported",
                source_cell_ids=("minted-alpha", "minted-alpha-high"),
                transport_group_id="synthetic-alpha-transport", transport_rule_id=TRANSPORT_RULE_ID), beta]

        h.resolutions = resolutions
        h.primary = h.primary_verdicts()

        def extract(_runs_root, _spec, *, kept_units, archive_context, **_kwargs):
            pack = kept_units.window.pack
            report = deepcopy(h.f.reports[pack])
            if archive_context.sensitivity_bound_s > h.f.brackets[pack].b_fiducial_s:
                values = (1.5, 1.75, 2., 3.) if pack == "alpha" else (1.25, 1.5)
                for row, value in zip(report["cells"], values):
                    row["floor"]["drift_widened_guarded_floor_j"] = value
            return report

        h.extract = extract
        record = h.call(.0625)
        self.assertEqual(len(record["contrasts"]), 2)
        # ALPHA source corners are (1.5,1.75) and (2,3) J; BETA's (1.25,1.5)
        # cannot dominate either component. Thus the contrast uses (2,3,3) J.
        # These dyadic values are exact binary64. COMMON bars are (2,3,3)e-6 J;
        # M05008 shifts .5 / 1.25 / 1.25 J, at least 250,000 bars.
        for contrast in record["contrasts"]:
            with self.subTest(contrast=contrast["contrast_id"]):
                value = contrast["sensitivity"]
                self.assertEqual((value["floor_abs_j"], value["floor_cmp_j"], value["floor_gate_j"]),
                                 (2., 3., 3.))
