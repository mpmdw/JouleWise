"""Fail-closed tests for the INTERIM Results fill renderer contract.

All numeric inputs in this module and its fixtures are deliberately obvious
synthetic magnitudes.  They are not historical or measured JouleWise results.

This suite pins the pre-``_v5`` renderer vocabulary during the interim.  The
lead-owned successor renderer, after G2-a, replaces the pinned-frozen
assertions with live-registry synchronization.
"""

from __future__ import annotations

from decimal import Decimal
import hashlib
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


# The renderer implementation is deliberately frozen while the live registry
# advances to _v5.  Bind its historical mechanics to the last synchronized
# pre-_v5 vocabulary rather than allowing the imported module's registry read
# to reinterpret old row-building code under the successor namespace.
_FROZEN_CELL_STEMS = tuple(
    f"{model}_{phase}"
    for model in ("1p5B", "7B")
    for phase in ("prompt", "decode")
)
FROZEN_SUPPLIER_UNKNOWN_ROWS = frozenset(
    {
        "[B_decode_claim_J]",
        "[F_decode_contrast_cmp_worst_case_J]",
    }
    | {
        f"[E_{stem}_{suffix}]"
        for stem in _FROZEN_CELL_STEMS
        for suffix in (
            "J_per_request",
            "J_per_token",
            "lower_J",
            "upper_J",
        )
    }
    | {f"[N_bundles_{stem}]" for stem in _FROZEN_CELL_STEMS}
)
FROZEN_VALUE_UNISSUED_ROWS = frozenset(
    {
        "[B_C_prompt_invariance_J_per_token]",
        "[CELL_NONPUBLICATION_SUMMARY]",
        "[C_decode_floor_clearance_J]",
        "[D_C_additivity_J]",
        "[D_C_drift_diagnostic_J]",
        "[D_C_linearity_diagnostic_J_per_token]",
        "[D_C_micro_diagnostic_x_floor]",
        "[D_C_null_diagnostic_J]",
        "[D_C_null_max_abs_J]",
        "[D_C_phase_diagnostic_J]",
        "[D_C_reference_excursion_J]",
        "[E_decode_contrast_lower_J]",
        "[E_decode_contrast_signed_J_per_request]",
        "[E_decode_contrast_upper_J]",
        "[F_claim_decode_armwise_max_J]",
        "[F_decode_contrast_cmp_two_edge_J]",
        "[M_decode_contrast_abs_J_per_request]",
        "[N_C_eligible_sessions]",
        "[PLAIN_LANGUAGE_RESULT_between_sessions]",
        "[PLAIN_LANGUAGE_RESULT_drift]",
        "[PLAIN_LANGUAGE_RESULT_floor]",
        "[PLAIN_LANGUAGE_RESULT_linearity]",
        "[PLAIN_LANGUAGE_RESULT_null]",
        "[PLAIN_LANGUAGE_RESULT_phase]",
        "[R_C_linearity_limit_J]",
        "[R_C_micro_max_x_floor]",
        "[R_C_micro_min_x_floor]",
        "[R_decode_effect_x_floor]",
        "[S_C_linearity_decode_J_per_token]",
        "[S_C_linearity_request_J_per_token]",
        "[S_C_prompt_invariance_J_per_token]",
        "[S_decode_floor_shortfall_J]",
        "[S_decode_joint_J]",
        "[T_C_recovery_s]",
    }
    | {
        f"[{prefix}_{stem}{suffix}]"
        for stem in _FROZEN_CELL_STEMS
        for prefix, suffix in (
            ("AVAILABLE_DIAGNOSTIC_CLAUSE", ""),
            ("F", "_abs_J"),
            ("F", "_cmp_J"),
            ("F", "_operative_J"),
            ("NO_EXACT_FLOOR_REASON", ""),
            ("POINT_DIAGNOSTIC_CLAUSE", ""),
            ("TERMINAL_REFUSAL_REASON", ""),
            ("TERM_A", "_abs_J"),
            ("TERM_A", "_cmp_J"),
            ("TERM_B", "_abs_J"),
            ("TERM_B", "_cmp_J"),
        )
    }
)
FROZEN_OTHER_ROWS = frozenset(
    {
        "[ABSENT_DIAGNOSTIC_ROW_LIST]",
        "[NO_EXACT_FLOOR_REASON_*]",
        "[PLAIN_LANGUAGE_RESULT_*]",
        "[PRESENT_DIAGNOSTIC_LIST]",
        "[REFUSAL_REASON_1p5B_floor_window]",
        "[REFUSAL_REASON_7B_floor_window]",
        "[REFUSAL_REASON_window_C]",
        "[TERMINAL_REFUSAL_REASON_*]",
        "[VALUE]",
    }
)
FROZEN_RENDERER_ROWS = frozenset(
    FROZEN_SUPPLIER_UNKNOWN_ROWS
    | FROZEN_VALUE_UNISSUED_ROWS
    | FROZEN_OTHER_ROWS
)

RENDERER.REGISTRY_ROWS = FROZEN_RENDERER_ROWS
RENDERER.SUPPLIER_UNKNOWN_ROWS = FROZEN_SUPPLIER_UNKNOWN_ROWS
RENDERER.VALUE_UNISSUED_ROWS = FROZEN_VALUE_UNISSUED_ROWS


def renderer_row(row: str) -> str:
    """Return a row only when it belongs to the frozen renderer vocabulary."""

    if row not in RENDERER.REGISTRY_ROWS:
        raise AssertionError(f"test requested non-renderer row {row}")
    return row


def renderer_token(row: str) -> str:
    return renderer_row(row)[1:-1]


def renderer_cli(*args: str) -> list[str]:
    """Invoke ``main`` with this module's frozen renderer constants bound."""

    return [
        sys.executable,
        "-c",
        (
            "from tests.test_render_results_fills import RENDERER; "
            "raise SystemExit(RENDERER.main())"
        ),
        *args,
    ]


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


class InterimVocabularyContractTests(unittest.TestCase):
    def test_renderer_vocabulary_is_pinned_to_canonical_linter(self) -> None:
        self.assertEqual(
            RENDERER.TERMINAL_REASON_CODES,
            frozenset(LINTER.TERMINAL_REASON_CODES),
        )
        self.assertEqual(
            RENDERER.NONTERMINAL_CODES,
            frozenset(LINTER.NONTERMINAL_CODES),
        )
        self.assertEqual(RENDERER.S7_HEADINGS, LINTER.S7_HEADINGS)
        self.assertEqual(RENDERER.S6_HEADINGS, LINTER.S6_HEADINGS)
        self.assertEqual(RENDERER.S6_GUARDS, LINTER.S6_GUARDS)

    def test_canonical_unfilled_template_still_passes_custodied_linter(self) -> None:
        LINTER.lint_text(LINTER.TEMPLATE_PATH.read_text(encoding="utf-8"))

    def test_renderer_vocabulary_is_frozen_pre_v5(self) -> None:
        rows = tuple(sorted(RENDERER.REGISTRY_ROWS))
        digest = hashlib.sha256(repr(rows).encode("utf-8")).hexdigest()
        self.assertEqual(len(rows), 109)
        self.assertEqual(
            digest,
            "0882cf7240e137adeea12a9ec2c074856fabd83d96383d1af5134f5b8a636c85",
        )
        self.assertEqual(len(RENDERER.SUPPLIER_UNKNOWN_ROWS), 22)
        self.assertEqual(len(RENDERER.VALUE_UNISSUED_ROWS), 78)

    def test_v5_registry_rows_are_unknown_to_frozen_renderer(self) -> None:
        # Round-7 fill-checklist ruling: the pre-_v5 renderer is not fill
        # authority for renamed rows and must fail closed.  Its lead-owned
        # successor restores live-registry synchronization after G2-a.
        registry_bytes = RENDERER.REGISTRY_PATH.read_bytes()
        live_v5_rows = (
            "[F_8B_decode_operative_J]",
            "[R_8B_decode_abs]",
        )
        for row in live_v5_rows:
            with self.subTest(row=row):
                self.assertIn(f"`{row}`".encode("utf-8"), registry_bytes)
                self.assertNotIn(row, RENDERER.REGISTRY_ROWS)
                with self.assertRaises(ValueError) as caught:
                    RENDERER.StopFill(row, "VALUE_UNISSUED", "synthetic")
                self.assertEqual(
                    str(caught.exception),
                    f"unknown Results fill registry row: {row}",
                )


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
        with self.assertRaises(RENDERER.StopFill) as caught:
            RENDERER.select_variant_from_atoms(
                "7", {"window_1p5B_pass": True, "window_7B_pass": True}
            )
        self.assertEqual(caught.exception.label, "FAILED_PREDICATE")


class RendererHappyPathTests(unittest.TestCase):
    def test_variant_d_and_section6_zero_render_and_validate(self) -> None:
        rendered = RENDERER.render_from_manifest(
            fixture("synthetic_d_and_0_manifest.json")
        )
        self.assertEqual(
            RENDERER.validate_rendered(rendered),
            {"section7": "7_D", "section6": "0"},
        )
        self.assertIn("Their operative floor is 222222 J", rendered)
        self.assertIn("exact authorized\n444444 J operative floor", rendered)
        self.assertIn("point-only repeatability diagnostic was 10101 J", rendered)
        self.assertIn("The available absolute component was 555555 J", rendered)
        self.assertIn("bundle_missing", rendered)
        self.assertIn("**1.5B prompt-processing cell:**", rendered)
        self.assertIn("**7B token-generation cell:**", rendered)
        self.assertNotRegex(rendered, RENDERER.FILL_TOKEN_RE)
        self.assertNotIn("SELECTION GUARD", rendered)

    def test_variant_c3_copies_both_refusal_verdicts(self) -> None:
        rendered = RENDERER.render_from_manifest(
            fixture("synthetic_c3_and_0_manifest.json")
        )
        self.assertEqual(
            RENDERER.validate_rendered(rendered),
            {"section7": "7_C3", "section6": "0"},
        )
        self.assertEqual(rendered.count("conditions: synthetic_fixture_refusal"), 2)
        self.assertNotIn("0 J", rendered)

    def test_cli_emits_only_validated_prose(self) -> None:
        completed = subprocess.run(
            renderer_cli(str(fixture("synthetic_d_and_0_manifest.json"))),
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(completed.stderr, "")
        self.assertEqual(
            RENDERER.validate_rendered(completed.stdout),
            {"section7": "7_D", "section6": "0"},
        )

    def test_validate_mode_accepts_rendered_sample(self) -> None:
        rendered = RENDERER.render_from_manifest(
            fixture("synthetic_c3_and_0_manifest.json")
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "rendered.md"
            path.write_text(rendered, encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, str(RENDERER_PATH), "--validate-rendered", str(path)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(
            completed.stdout,
            "results prose rendered lint: PASS (§7 7_C3; §6 0; zero fill tokens)\n",
        )


class DerivationTests(unittest.TestCase):
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

    def test_joint_sizing_stops_on_supplier_unknown_parent(self) -> None:
        with self.assertRaises(RENDERER.StopFill) as caught:
            RENDERER.derive_numeric(
                renderer_token("[S_decode_joint_J]"),
                (Decimal("333333"), Decimal("111111")),
            )
        self.assertEqual(
            caught.exception.registry_row,
            renderer_row("[B_decode_claim_J]"),
        )
        self.assertEqual(caught.exception.label, "SUPPLIER_UNKNOWN")


class StopFillTests(unittest.TestCase):
    def test_absent_artifact_names_first_blocked_registry_row(self) -> None:
        with self.assertRaises(RENDERER.StopFill) as caught:
            RENDERER.render_from_manifest(
                fixture("synthetic_absent_artifact_manifest.json")
            )
        self.assertEqual(
            caught.exception.registry_row,
            renderer_row("[F_1p5B_prompt_abs_J]"),
        )
        self.assertEqual(caught.exception.label, "ABSENT_ARTIFACT")

    def test_malformed_json_stops_without_placeholder_output(self) -> None:
        completed = subprocess.run(
            renderer_cli(str(fixture("synthetic_malformed_input.json.invalid"))),
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 2)
        self.assertEqual(completed.stdout, "")
        self.assertIn('"label": "MALFORMED_INPUT"', completed.stderr)
        expected_row = renderer_row("[REFUSAL_REASON_1p5B_floor_window]")
        self.assertIn(
            f'"registry_row": "{expected_row}"',
            completed.stderr,
        )

    def test_supplier_unknown_mean_row_hard_stops(self) -> None:
        with self.assertRaises(RENDERER.StopFill) as caught:
            RENDERER.render_from_manifest(
                fixture("synthetic_c1_supplier_unknown_manifest.json")
            )
        self.assertEqual(
            caught.exception.registry_row,
            renderer_row("[E_1p5B_prompt_J_per_request]"),
        )
        self.assertEqual(caught.exception.label, "SUPPLIER_UNKNOWN")
        completed = subprocess.run(
            renderer_cli(
                str(fixture("synthetic_c1_supplier_unknown_manifest.json"))
            ),
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 2)
        self.assertEqual(completed.stdout, "")
        self.assertIn('"label": "SUPPLIER_UNKNOWN"', completed.stderr)

    def test_two_published_decode_cells_stop_on_unknown_claim_bound(self) -> None:
        manifest = make_paths_absolute(
            load_fixture("synthetic_d_and_0_manifest.json")
        )
        alpha_floor = load_fixture("synthetic_alpha_floor.json")
        alpha_extract = load_fixture("synthetic_alpha_extraction.json")
        beta_floor = load_fixture("synthetic_beta_floor.json")
        beta_extract = load_fixture("synthetic_beta_extraction.json")
        alpha_floor["cells"][1].update(
            {
                "eligibility": {
                    "claim_usable": True,
                    "reason_codes": [],
                    "status": "claim_ready",
                },
                "floor_abs_j": 666666,
                "floor_gate_j": 666666,
            }
        )
        alpha_extract["cells"][2] = {
            "cell_id": "SYNTHETIC-ALPHA-DECODE-ABS",
            "extractable": True,
            "floor": {"drift_widened_guarded_floor_j": 666666},
            "kind": "absolute",
            "operative_floor_j": 666666,
            "refusal_reasons": [],
        }
        beta_floor["cells"][1].update(
            {
                "eligibility": {
                    "claim_usable": True,
                    "reason_codes": [],
                    "status": "claim_ready",
                },
                "floor_cmp_j": 666666,
                "floor_gate_j": 666666,
            }
        )
        beta_extract["cells"][3] = {
            "cell_id": "SYNTHETIC-BETA-DECODE-CMP",
            "extractable": True,
            "floor": {"drift_widened_guarded_floor_j": 666666},
            "kind": "comparative",
            "operative_floor_j": 666666,
            "refusal_reasons": [],
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest["campaigns"]["alpha"]["floor_artifact"] = str(
                write_json(root, "alpha-floor.json", alpha_floor)
            )
            manifest["campaigns"]["alpha"]["extraction"] = str(
                write_json(root, "alpha-extract.json", alpha_extract)
            )
            manifest["campaigns"]["beta"]["floor_artifact"] = str(
                write_json(root, "beta-floor.json", beta_floor)
            )
            manifest["campaigns"]["beta"]["extraction"] = str(
                write_json(root, "beta-extract.json", beta_extract)
            )
            manifest_path = write_json(root, "manifest.json", manifest)
            with self.assertRaises(RENDERER.StopFill) as caught:
                RENDERER.render_from_manifest(manifest_path)
        self.assertEqual(
            caught.exception.registry_row,
            renderer_row("[B_decode_claim_J]"),
        )
        self.assertEqual(caught.exception.label, "SUPPLIER_UNKNOWN")

    def test_section6_pass_and_refusal_both_stop_on_unissued_report(self) -> None:
        for verdict, expected_row in (
            (
                "synthetic_pass_verdict.json",
                renderer_row("[PLAIN_LANGUAGE_RESULT_linearity]"),
            ),
            (
                "synthetic_refused_verdict.json",
                renderer_row("[D_C_linearity_diagnostic_J_per_token]"),
            ),
        ):
            with self.subTest(verdict=verdict):
                manifest = make_paths_absolute(
                    load_fixture("synthetic_c3_and_0_manifest.json")
                )
                manifest["characterization"] = {
                    "funded": True,
                    "run": True,
                    "verdict": str(fixture(verdict)),
                }
                with tempfile.TemporaryDirectory() as tmp:
                    path = write_json(Path(tmp), "manifest.json", manifest)
                    with self.assertRaises(RENDERER.StopFill) as caught:
                        RENDERER.render_from_manifest(path)
                self.assertEqual(caught.exception.registry_row, expected_row)
                self.assertEqual(caught.exception.label, "VALUE_UNISSUED")

    def test_stored_operative_gate_mismatch_is_failed_predicate(self) -> None:
        manifest = make_paths_absolute(
            load_fixture("synthetic_d_and_0_manifest.json")
        )
        floor = load_fixture("synthetic_alpha_floor.json")
        floor["cells"][0]["floor_gate_j"] = 999999
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest["campaigns"]["alpha"]["floor_artifact"] = str(
                write_json(root, "alpha-floor.json", floor)
            )
            path = write_json(root, "manifest.json", manifest)
            with self.assertRaises(RENDERER.StopFill) as caught:
                RENDERER.render_from_manifest(path)
        self.assertEqual(
            caught.exception.registry_row,
            renderer_row("[F_1p5B_prompt_operative_J]"),
        )
        self.assertEqual(caught.exception.label, "FAILED_PREDICATE")

    def test_unknown_component_reason_code_is_rejected(self) -> None:
        manifest = make_paths_absolute(
            load_fixture("synthetic_d_and_0_manifest.json")
        )
        extraction = load_fixture("synthetic_alpha_extraction.json")
        extraction["cells"][0]["refusal_reasons"] = ["synthetic_unknown_reason"]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest["campaigns"]["alpha"]["extraction"] = str(
                write_json(root, "alpha-extraction.json", extraction)
            )
            path = write_json(root, "manifest.json", manifest)
            with self.assertRaises(RENDERER.StopFill) as caught:
                RENDERER.render_from_manifest(path)
        self.assertEqual(
            caught.exception.registry_row,
            renderer_row("[F_1p5B_prompt_abs_J]"),
        )
        self.assertEqual(caught.exception.label, "UNKNOWN_FIELD")


class RenderedValidatorMutationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.rendered = RENDERER.render_from_manifest(
            fixture("synthetic_d_and_0_manifest.json")
        )

    def assert_refused(self, mutated: str) -> None:
        self.assertNotEqual(mutated, self.rendered)
        with self.assertRaises(RENDERER.RenderedValidationError):
            RENDERER.validate_rendered(mutated)

    def test_refuses_remaining_fill_token(self) -> None:
        self.assert_refused(
            self.rendered + "\n[F_1p5B_prompt_abs_J]\n"
        )

    def test_refuses_second_section7_variant(self) -> None:
        marker = RENDERER.S6_HEADINGS["0"]
        mutated = self.rendered.replace(
            marker,
            RENDERER.S7_HEADINGS["7_C3"] + "\n\n" + marker,
            1,
        )
        self.assert_refused(mutated)

    def test_refuses_surviving_guard(self) -> None:
        self.assert_refused(
            self.rendered.replace(
                RENDERER.S7_HEADINGS["7_D"],
                RENDERER.S7_HEADINGS["7_D"] + "\n\n**SELECTION GUARD**",
                1,
            )
        )

    def test_refuses_noncanonical_line(self) -> None:
        self.assert_refused(
            self.rendered.replace(
                "Both model-specific windows completed with passing",
                "An invented conclusion replaced the registered sentence",
                1,
            )
        )

    def test_refuses_body_under_wrong_variant_heading(self) -> None:
        self.assert_refused(
            self.rendered.replace(
                RENDERER.S7_HEADINGS["7_D"],
                RENDERER.S7_HEADINGS["7_C3"],
                1,
            )
        )


if __name__ == "__main__":
    unittest.main()
