"""Fail-closed tests against the live Results fill registry.

All numeric inputs in this module and its fixtures are deliberately obvious
synthetic magnitudes.  They are not historical or measured JouleWise results.

The historical prose template remains the canonical vocabulary for its
retained variants; registry globals always come from the current checkout.
"""

from __future__ import annotations

from decimal import Decimal
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
RENDERER_PATH = ROOT / "scripts" / "render_results_fills.py"
LINTER_PATH = (
    ROOT
    / "docs"
    / "process_traces"
    / "2026-08-07-plan-factory"
    / "lint_results_prose_template.py"
)
FIXTURES = ROOT / "tests" / "fixtures" / "results_prose_render"

RENDERER_SPEC = importlib.util.spec_from_file_location(
    "render_results_fills", RENDERER_PATH
)
assert RENDERER_SPEC is not None and RENDERER_SPEC.loader is not None
RENDERER = importlib.util.module_from_spec(RENDERER_SPEC)
RENDERER_SPEC.loader.exec_module(RENDERER)

LINTER_SPEC = importlib.util.spec_from_file_location(
    "lint_results_prose_template_for_renderer", LINTER_PATH
)
assert LINTER_SPEC is not None and LINTER_SPEC.loader is not None
LINTER = importlib.util.module_from_spec(LINTER_SPEC)
LINTER_SPEC.loader.exec_module(LINTER)


def renderer_cli(*args: str) -> list[str]:
    """Run the actual script against its unmodified live registry."""
    return [sys.executable, "-B", str(RENDERER_PATH), *args]


def fixture(name: str) -> Path:
    return FIXTURES / name


def load_fixture(name: str):
    return json.loads(fixture(name).read_text(encoding="utf-8"))


def make_paths_absolute(manifest: dict) -> dict:
    for campaign in manifest["campaigns"].values():
        for key in ("verdict", "floor_artifact", "extraction"):
            value = campaign.get(key)
            if isinstance(value, str):
                campaign[key] = str(fixture(value))
    characterization = manifest["characterization"]
    if isinstance(characterization.get("verdict"), str):
        characterization["verdict"] = str(fixture(characterization["verdict"]))
    return manifest


def write_json(directory: Path, name: str, value) -> Path:
    path = directory / name
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return path


class AppendixDeriveProductionTests(unittest.TestCase):
    def setUp(self) -> None:
        # Load an independent production module for registry-parser tests.
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


class LiveVocabularyContractTests(unittest.TestCase):
    def test_renderer_vocabulary_matches_canonical_linter(self):
        self.assertEqual(RENDERER.TERMINAL_REASON_CODES, frozenset(LINTER.TERMINAL_REASON_CODES))
        self.assertEqual(RENDERER.NONTERMINAL_CODES, frozenset(LINTER.NONTERMINAL_CODES))
        self.assertEqual(RENDERER.S7_HEADINGS, LINTER.S7_HEADINGS)
        self.assertEqual(RENDERER.S6_HEADINGS, LINTER.S6_HEADINGS)
        self.assertEqual(RENDERER.S6_GUARDS, LINTER.S6_GUARDS)

    def test_canonical_unfilled_template_passes_custodied_linter(self):
        LINTER.lint_text(LINTER.TEMPLATE_PATH.read_text(encoding="utf-8"))

    def test_registry_is_live_and_not_rebound_by_tests(self):
        rows, unknown, unissued = RENDERER._registry_rows()
        self.assertEqual(RENDERER.REGISTRY_ROWS, rows)
        self.assertEqual(RENDERER.SUPPLIER_UNKNOWN_ROWS, unknown)
        self.assertEqual(RENDERER.VALUE_UNISSUED_ROWS, unissued)
        for row in ("[F_1p7B_decode_operative_J]", "[F_8B_decode_operative_J]", "[R_8B_decode_abs]"):
            with self.subTest(row=row):
                self.assertIn(row, rows)
                self.assertEqual(RENDERER.StopFill(row, "VALUE_UNISSUED", "probe").registry_row, row)
        for row in ("[F_1p5B_prompt_operative_J]", "[F_7B_decode_operative_J]"):
            with self.assertRaisesRegex(ValueError, "unknown Results fill registry row"):
                RENDERER.StopFill(row, "VALUE_UNISSUED", "probe")


class VariantSelectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cases = load_fixture("synthetic_variant_cases.json")

    def test_all_seven_section7_variants_select_exactly(self) -> None:
        observed = {
            RENDERER.select_variant_from_atoms("7", case["atoms"])
            for case in self.cases["section7"]
        }
        expected = {case["expected"] for case in self.cases["section7"]}
        self.assertEqual(observed, expected)
        self.assertEqual(expected, set(RENDERER.S7_HEADINGS))

    def test_all_four_section6_variants_select_exactly(self) -> None:
        observed = {
            RENDERER.select_variant_from_atoms("6", case["atoms"])
            for case in self.cases["section6"]
        }
        expected = {case["expected"] for case in self.cases["section6"]}
        self.assertEqual(observed, expected)
        self.assertEqual(expected, set(RENDERER.S6_HEADINGS))

    def test_incomplete_predicate_state_stops_instead_of_defaulting(self) -> None:
        with self.assertRaisesRegex(ValueError, "unknown Results fill registry row"):
            RENDERER.select_variant_from_atoms(
                "7", {"window_1p5B_pass": True, "window_7B_pass": True}
            )


class RendererHappyPathTests(unittest.TestCase):
    def test_variant_c3_copies_both_refusal_verdicts(self):
        rendered = RENDERER.render_from_manifest(fixture("synthetic_c3_and_0_manifest.json"))
        self.assertEqual(RENDERER.validate_rendered(rendered), {"section7": "7_C3", "section6": "0"})
        self.assertEqual(rendered.count("conditions: synthetic_fixture_refusal"), 2)
        self.assertNotIn("0 J", rendered)

    def test_retained_legacy_numeric_variant_uses_real_script(self):
        rendered = RENDERER.render_from_manifest(fixture("synthetic_d_and_0_manifest.json"))
        self.assertEqual(RENDERER.validate_rendered(rendered), {"section7": "7_D", "section6": "0"})
        self.assertIn("Their operative floor is 222222 J", rendered)
        self.assertIn("exact authorized\n444444 J operative floor", rendered)
        self.assertIn("point-only repeatability diagnostic was 10101 J", rendered)
        self.assertIn("The available absolute component was 555555 J", rendered)
        self.assertIn("bundle_missing", rendered)
        self.assertNotRegex(rendered, RENDERER.FILL_TOKEN_RE)
        completed = subprocess.run(renderer_cli(str(fixture("synthetic_d_and_0_manifest.json"))),
                                   cwd=ROOT, text=True, capture_output=True, check=False)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(completed.stdout, rendered)
        self.assertEqual(completed.stderr, "")

    def test_validate_mode_accepts_rendered_sample(self):
        rendered = RENDERER.render_from_manifest(fixture("synthetic_c3_and_0_manifest.json"))
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "rendered.md"
            path.write_text(rendered, encoding="utf-8")
            completed = subprocess.run(renderer_cli("--validate-rendered", str(path)),
                                       cwd=ROOT, text=True, capture_output=True, check=False)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(completed.stdout, "results prose rendered lint: PASS (§7 7_C3; §6 0; zero fill tokens)\n")


class DerivationTests(unittest.TestCase):
    def test_remaining_registered_derivations_match_exact_arithmetic(self):
        low, middle, high = map(Decimal, ("111111", "222222", "888888"))
        floor = RENDERER.derive_numeric("F_claim_decode_armwise_max_J", (low, middle), stored=middle)
        magnitude = RENDERER.derive_numeric("M_decode_contrast_abs_J_per_request", (-high,))
        clearance = RENDERER.derive_numeric("C_decode_floor_clearance_J", (high, floor), predicate="floor_gate_pass")
        shortfall = RENDERER.derive_numeric("S_decode_floor_shortfall_J", (high, middle), predicate="floor_gate_refused")
        ratio = RENDERER.derive_numeric("R_decode_effect_x_floor", (high, middle))
        self.assertEqual((floor, magnitude, clearance, shortfall, ratio),
                         (middle, high, Decimal("666666"), Decimal("666666"), Decimal(4)))

    def test_live_model_row_has_no_legacy_derivation_rule(self):
        with self.assertRaises(RENDERER.StopFill) as caught:
            RENDERER.derive_numeric("F_8B_decode_operative_J", (Decimal(1), Decimal(2)))
        self.assertEqual(caught.exception.registry_row, "[F_8B_decode_operative_J]")
        self.assertEqual(caught.exception.label, "UNKNOWN_FIELD")

    def test_invalid_stored_value_and_gate_predicate_refuse(self):
        for kwargs in ({"stored": Decimal(99)}, {"predicate": "floor_gate_refused"}):
            token = "F_claim_decode_armwise_max_J" if "stored" in kwargs else "C_decode_floor_clearance_J"
            with self.assertRaises(RENDERER.StopFill):
                RENDERER.derive_numeric(token, (Decimal(1), Decimal(2)), **kwargs)

    def test_zero_and_nonterminating_ratio_denominators_refuse(self):
        for parents in ((Decimal(1), Decimal(0)), (Decimal(1), Decimal(3))):
            with self.assertRaises(RENDERER.StopFill):
                RENDERER.derive_numeric("R_decode_effect_x_floor", parents)

    def test_joint_sizing_still_requires_issued_bound(self):
        with self.assertRaises(RENDERER.StopFill) as caught:
            RENDERER.derive_numeric("S_decode_joint_J", (Decimal(3), Decimal(1)))
        self.assertEqual(caught.exception.registry_row, "[B_decode_claim_J]")
        self.assertEqual(caught.exception.label, "SUPPLIER_UNKNOWN")


class StopFillTests(unittest.TestCase):
    def test_live_refusal_constructor_keeps_structured_metadata(self):
        refusal = RENDERER.StopFill("[REFUSAL_REASON_8B_floor_window]", "ABSENT_ARTIFACT", "probe")
        self.assertEqual(json.loads(str(refusal).removeprefix("STOP_FILL ")), refusal.as_dict())

    def test_characterization_still_stops_on_live_unissued_rows(self):
        for verdict, row in (("synthetic_pass_verdict.json", "[PLAIN_LANGUAGE_RESULT_linearity]"),
                             ("synthetic_refused_verdict.json", "[D_C_linearity_diagnostic_J_per_token]")):
            manifest = make_paths_absolute(load_fixture("synthetic_c3_and_0_manifest.json"))
            manifest["characterization"] = {"funded": True, "run": True, "verdict": str(fixture(verdict))}
            with tempfile.TemporaryDirectory() as tmp:
                path = write_json(Path(tmp), "manifest.json", manifest)
                with self.assertRaises(RENDERER.StopFill) as caught:
                    RENDERER.render_from_manifest(path)
            self.assertEqual(caught.exception.registry_row, row)
            self.assertEqual(caught.exception.label, "VALUE_UNISSUED")

    def test_invalid_floor_arithmetic_and_unknown_reasons_refuse_live_cli(self):
        for kind in ("floor_mismatch", "unknown_reason"):
            manifest = make_paths_absolute(load_fixture("synthetic_d_and_0_manifest.json"))
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                if kind == "floor_mismatch":
                    floor = load_fixture("synthetic_alpha_floor.json")
                    floor["cells"][0]["floor_gate_j"] = 999999
                    manifest["campaigns"]["alpha"]["floor_artifact"] = str(write_json(root, "floor.json", floor))
                else:
                    extraction = load_fixture("synthetic_alpha_extraction.json")
                    extraction["cells"][0]["refusal_reasons"] = ["synthetic_unknown_reason"]
                    manifest["campaigns"]["alpha"]["extraction"] = str(write_json(root, "extraction.json", extraction))
                path = write_json(root, "manifest.json", manifest)
                completed = subprocess.run(renderer_cli(str(path)), cwd=ROOT,
                                           capture_output=True, text=True, check=False)
            self.assertEqual(completed.returncode, 2, completed.stderr)
            self.assertEqual(completed.stdout, "")
            self.assertNotIn("Traceback", completed.stderr)


class RenderedValidatorMutationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.rendered = RENDERER.render_from_manifest(
            fixture("synthetic_c3_and_0_manifest.json")
        )

    def assert_refused(self, mutated: str) -> None:
        self.assertNotEqual(mutated, self.rendered)
        with self.assertRaises(RENDERER.RenderedValidationError):
            RENDERER.validate_rendered(mutated)

    def test_refuses_remaining_fill_token(self) -> None:
        self.assert_refused(
            self.rendered + "\n[F_8B_decode_abs_J]\n"
        )

    def test_refuses_second_section7_variant(self) -> None:
        marker = RENDERER.S6_HEADINGS["0"]
        mutated = self.rendered.replace(
            marker,
            RENDERER.S7_HEADINGS["7_D"] + "\n\n" + marker,
            1,
        )
        self.assert_refused(mutated)

    def test_refuses_surviving_guard(self) -> None:
        self.assert_refused(
            self.rendered.replace(
                RENDERER.S7_HEADINGS["7_C3"],
                RENDERER.S7_HEADINGS["7_C3"] + "\n\n**SELECTION GUARD**",
                1,
            )
        )

    def test_refuses_noncanonical_line(self) -> None:
        self.assert_refused(self.rendered + "\nAn invented conclusion replaced the registered sentence\n")

    def test_refuses_body_under_wrong_variant_heading(self) -> None:
        self.assert_refused(
            self.rendered.replace(
                RENDERER.S7_HEADINGS["7_C3"],
                RENDERER.S7_HEADINGS["7_D"],
                1,
            )
        )


if __name__ == "__main__":
    unittest.main()
