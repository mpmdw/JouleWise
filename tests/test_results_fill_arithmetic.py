"""Synthetic arithmetic regressions retained from the retired fill renderer.

The current appendix refusal guards remain separate from historical arithmetic.
"""
from decimal import Decimal
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
RENDERER_PATH = ROOT / "scripts" / "render_results_fills.py"
SPEC = importlib.util.spec_from_file_location("results_fill_arithmetic", RENDERER_PATH)
RENDERER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RENDERER)
# Only the old tokens exercised below: no frozen renderer registry or prose fixture.
ARITHMETIC_ROWS = frozenset({
    "[F_1p5B_prompt_operative_J]", "[F_7B_decode_operative_J]",
    "[F_claim_decode_armwise_max_J]", "[M_decode_contrast_abs_J_per_request]",
    "[C_decode_floor_clearance_J]", "[S_decode_floor_shortfall_J]",
    "[R_decode_effect_x_floor]",
})

def renderer_row(row):
    assert row in ARITHMETIC_ROWS
    return row

def renderer_token(row):
    return renderer_row(row)[1:-1]


class AppendixDeriveProductionTests(unittest.TestCase):
    def setUp(self) -> None:
        # Do not inherit this module's historical registry-global overrides.
        spec = importlib.util.spec_from_file_location("appendix_renderer", RENDERER_PATH)
        self.renderer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.renderer)

    def test_production_renderer_knows_pe01_and_refuses_results_prose(self) -> None:
        renderer = self.renderer
        row = "[FILL:PE-01]"
        self.assertIn(row, renderer.REGISTRY_ROWS)
        self.assertIn(row, renderer.VALUE_UNISSUED_ROWS)
        self.assertNotIn(row, renderer.SUPPLIER_UNKNOWN_ROWS)
        self.assertEqual(renderer.StopFill(row, "VALUE_UNISSUED", "probe").label, "VALUE_UNISSUED")
        for operation in (
            lambda: renderer._replace_tokens(row, {}),
            lambda: renderer._replace_tokens(row, {"FILL:PE-01": "9.0 J"}),
            lambda: renderer.validate_rendered(row),
        ):
            with self.subTest(operation=operation):
                with self.assertRaises(renderer.StopFill) as caught:
                    operation()
                self.assertEqual(caught.exception.registry_row, row)
                self.assertEqual(caught.exception.label, "VALUE_UNISSUED")

    def test_future_appendix_derive_row_uses_the_same_nonresults_path(self) -> None:
        renderer = self.renderer
        text = renderer.REGISTRY_PATH.read_text(encoding="utf-8")
        text = text.replace("PE-01", "ZZ-42").replace("Appendix A.7", "Appendix A.8")
        with tempfile.TemporaryDirectory() as directory:
            registry = Path(directory) / "registry.md"
            registry.write_text(text, encoding="utf-8")
            with mock.patch.object(renderer, "REGISTRY_PATH", registry):
                rows, unknown, unissued = renderer._registry_rows()
        row = "[FILL:ZZ-42]"
        self.assertIn(row, rows)
        self.assertIn(row, unissued)
        self.assertNotIn(row, unknown)
        with mock.patch.multiple(
            renderer, REGISTRY_ROWS=rows, VALUE_UNISSUED_ROWS=unissued,
            APPENDIX_DERIVE_ROWS=frozenset({row}),
        ):
            with self.assertRaises(renderer.StopFill) as caught:
                renderer._replace_tokens(row, {"FILL:ZZ-42": "9.0 J"})
        self.assertEqual(caught.exception.label, "VALUE_UNISSUED")


class DerivationTests(unittest.TestCase):
    def setUp(self):
        self.rows = mock.patch.object(RENDERER, "REGISTRY_ROWS", ARITHMETIC_ROWS)
        self.rows.start()
        self.addCleanup(self.rows.stop)

    def test_registry_named_derivations_match_hand_computation(self) -> None:
        low = Decimal("111111")
        middle = Decimal("222222")
        high = Decimal("888888")
        operative = RENDERER.derive_numeric(
            renderer_token("[F_1p5B_prompt_operative_J]"),
            (low, middle),
            stored=middle,
        )
        claim_floor = RENDERER.derive_numeric(
            renderer_token("[F_claim_decode_armwise_max_J]"),
            (middle, Decimal("333333")),
            stored=Decimal("333333"),
        )
        magnitude = RENDERER.derive_numeric(
            renderer_token("[M_decode_contrast_abs_J_per_request]"),
            (Decimal("-888888"),),
        )
        clearance = RENDERER.derive_numeric(
            renderer_token("[C_decode_floor_clearance_J]"),
            (high, claim_floor),
            predicate="floor_gate_pass",
        )
        shortfall = RENDERER.derive_numeric(
            renderer_token("[S_decode_floor_shortfall_J]"),
            (high, Decimal("333333")),
            predicate="floor_gate_refused",
        )
        ratio = RENDERER.derive_numeric(
            renderer_token("[R_decode_effect_x_floor]"), (high, middle)
        )
        self.assertEqual(operative, middle)
        self.assertEqual(claim_floor, Decimal("333333"))
        self.assertEqual(magnitude, high)
        self.assertEqual(clearance, Decimal("555555"))
        self.assertEqual(shortfall, Decimal("555555"))
        self.assertEqual(ratio, Decimal("4"))


    def test_independently_supplied_derived_value_is_rejected(self) -> None:
        with self.assertRaises(RENDERER.StopFill) as caught:
            RENDERER.derive_numeric(
                renderer_token("[F_7B_decode_operative_J]"),
                (Decimal("111111"), Decimal("222222")),
                stored=Decimal("999999"),
            )
        self.assertEqual(
            caught.exception.registry_row,
            renderer_row("[F_7B_decode_operative_J]"),
        )
        self.assertEqual(caught.exception.label, "FAILED_PREDICATE")


    def test_branch_predicates_and_zero_ratio_denominator_fail_closed(self) -> None:
        with self.assertRaises(RENDERER.StopFill):
            RENDERER.derive_numeric(
                renderer_token("[C_decode_floor_clearance_J]"),
                (Decimal("888888"), Decimal("222222")),
                predicate="floor_gate_refused",
            )
        with self.assertRaises(RENDERER.StopFill):
            RENDERER.derive_numeric(
                renderer_token("[R_decode_effect_x_floor]"),
                (Decimal("888888"), Decimal("0")),
            )
        with self.assertRaises(RENDERER.StopFill) as nonterminating:
            RENDERER.derive_numeric(
                renderer_token("[R_decode_effect_x_floor]"),
                (Decimal("111111"), Decimal("333333")),
            )
        self.assertIn("no rounding rule", nonterminating.exception.reason)


if __name__ == "__main__":
    unittest.main()
