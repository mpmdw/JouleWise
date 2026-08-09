"""Discrimination tests for the Results-prose semantic linter."""

from __future__ import annotations

import importlib.util
import re
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
LINTER_PATH = (
    ROOT / "docs" / "process_traces" / "2026-08-07-plan-factory"
    / "lint_results_prose_template.py"
)
SPEC = importlib.util.spec_from_file_location(
    "lint_results_prose_template", LINTER_PATH)
assert SPEC is not None and SPEC.loader is not None
LINTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(LINTER)
TEMPLATE = LINTER.TEMPLATE_PATH.read_text(encoding="utf-8")


class ResultsProseTemplateTests(unittest.TestCase):
    def assert_refused(self, mutated: str) -> None:
        self.assertNotEqual(mutated, TEMPLATE, "mutation must alter the template")
        with self.assertRaises(LINTER.TemplateLintError):
            LINTER.lint_text(mutated)

    def test_real_template_passes(self) -> None:
        LINTER.lint_text(TEMPLATE)

    # The thirteen tests below correspond one-for-one to the extension's ten
    # mutations plus the three delta-3 evasions. Each changes substantive
    # template semantics.

    def test_refuses_u_publishing_absolute_component(self) -> None:
        old = (
            "[F_1p5B_prompt_operative_J] J operative floor is published "
            "without that label."
        )
        new = (
            "[F_1p5B_prompt_abs_J] J operative floor is published "
            "without that label."
        )
        self.assert_refused(TEMPLATE.replace(old, new, 1))

    def test_refuses_t_positive_point_floor_publication(self) -> None:
        old = "No floor is published for this cell. The governing refusal was:"
        new = (
            "No floor is published for this cell. The point-only value is "
            "published as a floor. The governing refusal was:"
        )
        self.assert_refused(TEMPLATE.replace(old, new, 1))

    def test_refuses_u_attribution_limited_publication(self) -> None:
        old = "operative floor is published without that label."
        new = "operative floor is published with the label *attribution-limited*."
        self.assert_refused(TEMPLATE.replace(old, new, 1))

    def test_refuses_three_session_rule_moved_out_of_section_6_a(self) -> None:
        a_body = LINTER.section(TEMPLATE, LINTER.S6_HEADINGS["A"])
        self.assertIn(LINTER.BETWEEN, a_body)
        moved = a_body.replace(LINTER.BETWEEN, "", 1)
        mutated = TEMPLATE.replace(a_body, moved, 1) + "\n" + LINTER.BETWEEN + "\n"
        self.assert_refused(mutated)

    def test_refuses_lowercase_professor_facing_enum_choice(self) -> None:
        self.assert_refused(
            TEMPLATE + "\nProfessor-facing choice: [supported/refused]\n")

    def test_refuses_concrete_operative_source_declaration(self) -> None:
        insertion = (
            "### Source values\n\n"
            "- F_1p5B_decode_operative_J is supplied independently.\n"
        )
        self.assert_refused(
            TEMPLATE.replace("### Source values\n", insertion, 1))

    def test_refuses_a_predicate_overlap_after_guard_is_updated(self) -> None:
        a_body = LINTER.section(TEMPLATE, LINTER.S7_HEADINGS["7_A"])
        b1_body = LINTER.section(TEMPLATE, LINTER.S7_HEADINGS["7_B1"])
        a_match = LINTER.PREDICATE_RE.search(a_body)
        b1_match = LINTER.PREDICATE_RE.search(b1_body)
        assert a_match is not None and b1_match is not None
        a_tree = LINTER.parse_expr(a_match.group("expr").strip())
        b1_tree = LINTER.parse_expr(b1_match.group("expr").strip())
        new_comment = (
            "<!-- VARIANT_PREDICATE 7_A:\n"
            + b1_match.group("expr").strip()
            + "\n-->"
        )
        mutated = TEMPLATE.replace(a_match.group(0), new_comment, 1)
        mutated = mutated.replace(
            LINTER.render_variant_guard(a_tree),
            LINTER.render_variant_guard(b1_tree),
            1,
        )
        self.assert_refused(mutated)

    def test_refuses_claim_floor_paragraph_moved_to_c3(self) -> None:
        a_body = LINTER.section(TEMPLATE, LINTER.S7_HEADINGS["7_A"])
        paragraph = re.search(
            r"The pre-registered token-generation contrast estimated.*?"
            r"the direction gate passed\.\n",
            a_body,
            re.S,
        )
        assert paragraph is not None
        moved = paragraph.group(0)
        mutated = TEMPLATE.replace(moved, "", 1)
        c3_anchor = (
            "Every per-token denominator is the token count recorded by the "
            "runtime for\n"
        )
        mutated = mutated.replace(c3_anchor, moved + "\n" + c3_anchor, 1)
        self.assert_refused(mutated)

    def test_refuses_c_measurement_token_outside_present_renderer(self) -> None:
        c1_body = LINTER.section(TEMPLATE, LINTER.S7_HEADINGS["7_C1"])
        token = "[E_1p5B_prompt_J_per_request]"
        mutated_c1 = c1_body.replace(token, "[REMOVED_C_MEASUREMENT]", 1)
        end = "<!-- END_MEASUREMENT_RENDER: 1p5B_prompt -->"
        mutated_c1 = mutated_c1.replace(
            end, end + "\n\nMoved measurement: " + token, 1)
        self.assert_refused(TEMPLATE.replace(c1_body, mutated_c1, 1))

    def test_refuses_absent_diagnostic_surviving_section_6_render(self) -> None:
        b_body = LINTER.section(TEMPLATE, LINTER.S6_HEADINGS["B"])
        token = "[D_C_null_max_abs_J]"
        mutated_b = b_body.replace(token, "[REMOVED_NULL_DIAGNOSTIC]", 1)
        absent = "<!-- ELSE: emit no numeric null clause -->"
        mutated_b = mutated_b.replace(
            absent, absent + "\nAbsent branch leaked " + token + " J.", 1)
        self.assert_refused(TEMPLATE.replace(b_body, mutated_b, 1))

    def test_refuses_removed_section_6_b_visible_guard(self) -> None:
        b_body = LINTER.section(TEMPLATE, LINTER.S6_HEADINGS["B"])
        guard = LINTER.S6_GUARDS["B"]
        self.assertIn(guard, b_body)
        self.assert_refused(TEMPLATE.replace(guard + "\n\n", "", 1))

    def test_refuses_claim_floor_token_outside_all_sections(self) -> None:
        self.assert_refused(
            TEMPLATE + "\nUnlicensed claim floor [F_claim_decode_armwise_max_J] J.\n"
        )

    def test_refuses_a_presence_atom_removed_with_regenerated_guard(self) -> None:
        a_body = LINTER.section(TEMPLATE, LINTER.S7_HEADINGS["7_A"])
        match = LINTER.PREDICATE_RE.search(a_body)
        assert match is not None
        old_tree = LINTER.parse_expr(match.group("expr").strip())
        mutated_expr = match.group("expr").replace(
            "AND contrast_signed_present\n", "", 1)
        self.assertNotEqual(mutated_expr, match.group("expr"))
        new_tree = LINTER.parse_expr(mutated_expr.strip())
        new_comment = "<!-- VARIANT_PREDICATE 7_A:\n" + mutated_expr + "\n-->"
        mutated = TEMPLATE.replace(match.group(0), new_comment, 1)
        mutated = mutated.replace(
            LINTER.render_variant_guard(old_tree),
            LINTER.render_variant_guard(new_tree),
            1,
        )
        self.assert_refused(mutated)

    def test_refuses_b1_interval_note_made_unconditional(self) -> None:
        old = "Any arm-level intervals reported above"
        new = "The arm-level intervals reported above"
        self.assert_refused(TEMPLATE.replace(old, new, 1))

    def test_refuses_lowercase_factual_tokenizer_in_fill_key(self) -> None:
        old = "## Fill key"
        new = (
            "## Fill key\n\nboth arms record the same tokenizer identity "
            "for every reported companion."
        )
        self.assert_refused(TEMPLATE.replace(old, new, 1))


if __name__ == "__main__":
    unittest.main()
