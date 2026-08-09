#!/usr/bin/env python3
"""Semantic linter for the adopted Results-prose template contract."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import re
from pathlib import Path
from typing import Iterable

TEMPLATE_PATH = Path(__file__).with_name("DRAFT-RESULTS_PROSE.md")

S7_HEADINGS = {
    "7_A": "## §7 Variant A — both floor windows pass; decode contrast clears both gates",
    "7_B1": "## §7 Variant B1 — floor-gate refusal",
    "7_B2": "## §7 Variant B2 — direction-gate refusal",
    "7_D": "## §7 Variant D — a token-generation cell publishes no floor",
    "7_C1": "## §7 Variant C1 — 1.5B floor window passes; 7B floor window is refused",
    "7_C2": "## §7 Variant C2 — 7B floor window passes; 1.5B floor window is refused",
    "7_C3": "## §7 Variant C3 — both floor windows are refused",
}
S6_HEADINGS = {
    "0": "## §6 Variant 0 — Window C not yet result-bearing (DEFAULT)",
    "A": "## §6 Variant A — Window C passes (CONDITIONAL on the night being funded and run)",
    "B": "## §6 Variant B — Window C passes with mixed rows (CONDITIONAL on the night being funded and run)",
    "C": "## §6 Variant C — Window C verdict refusal (CONDITIONAL on the night being funded and run)",
}
S6_GUARDS = {
    "0": """**SELECTION GUARD — remove after filling:** Choose this variant if and only if
NOT(funded AND run AND an issued whole-window verdict exists). If the predicate
is false, do not use any sentence from this variant.""",
    "A": """**SELECTION GUARD — remove after filling:** Choose this variant if and only if
funded AND run AND whole-window verdict = PASS AND every one of the six
registered row outcomes = SUPPORTED. If the predicate is false, do not use any
sentence from this variant.""",
    "B": """**SELECTION GUARD — remove after filling:** Choose this variant if and only if
funded AND run AND whole-window verdict = PASS AND at least one of the six
registered row outcomes != SUPPORTED. If the predicate is false, do not use any
sentence from this variant.""",
    "C": """**SELECTION GUARD — remove after filling:** Choose this variant if and only if
funded AND run AND whole-window verdict = REFUSED. If the predicate is false,
do not use any sentence from this variant.""",
}

DENIAL = """It is not a single summed acceptance
threshold, and the decision interval was not compared with the sum."""
BETWEEN = """Between-session stability requires at least three eligible sessions or days
with the full stack identity recorded. A collection contributing fewer than
three eligible sessions leaves that row pending."""
PROMPT_SCOPE = """Any reported per-token value is also scoped to how the prompt was supplied to
the runtime and whether a beginning-of-sequence token was present, as recorded
for the passing window."""
TOKENIZER_CONDITIONAL = """When both arms record the same tokenizer identity, that match makes the
per-token companion comparable between those arms. No per-token number may be
compared with a stack carrying a different tokenizer identity."""

DERIVATIONS = (
    """DERIVE F_*_operative_J :=
  max(F_*_abs_J, F_*_cmp_J)""",
    """DERIVE F_claim_decode_armwise_max_J :=
  max(F_1p5B_decode_operative_J, F_7B_decode_operative_J)""",
    """DERIVE M_decode_contrast_abs_J_per_request :=
  abs(E_decode_contrast_signed_J_per_request)""",
    """DERIVE C_decode_floor_clearance_J :=
  M_decode_contrast_abs_J_per_request -
  F_claim_decode_armwise_max_J""",
    """DERIVE S_decode_floor_shortfall_J :=
  F_claim_decode_armwise_max_J -
  M_decode_contrast_abs_J_per_request""",
    """DERIVE R_decode_effect_x_floor :=
  M_decode_contrast_abs_J_per_request /
  F_claim_decode_armwise_max_J""",
    """DERIVE S_decode_joint_J :=
  F_claim_decode_armwise_max_J + B_decode_claim_J""",
)
CONCRETE_DERIVED = (
    "F_1p5B_prompt_operative_J", "F_1p5B_decode_operative_J",
    "F_7B_prompt_operative_J", "F_7B_decode_operative_J",
    "F_claim_decode_armwise_max_J", "M_decode_contrast_abs_J_per_request",
    "C_decode_floor_clearance_J", "S_decode_floor_shortfall_J",
    "R_decode_effect_x_floor", "S_decode_joint_J",
)
TERMINAL_REASON_CODES = {
    "bundle_missing", "summary_unreadable", "bundle_strict_invalid",
    "bundle_hash_unresolved", "bundle_status_not_succeeded",
    "reducer_wire_unknown", "idle_method_pair_invalid",
    "metric_missing_or_nonfinite", "window_evidence_precheck_failed",
    "campaign_cooldown_evidence_missing", "cooldown_cap_hit_unverified",
    "campaign_member_omitted_from_spec", "campaign_member_unattributable",
    "cap_hit_drift_term_unavailable", "insufficient_members_after_exclusion",
    "anchor_energy_envelope_unrecorded",
    "anchor_energy_envelope_exceeds_quarter_metric",
    "anchor_fallback_member_unusable", "clock_anchor_unresolved",
    "environment_admission_missing", "cpu_admission_unenforced",
    "whole_window_neg8_verdict_missing", "whole_window_neg8_verdict_failed",
    "adapter_continuity_evidence_missing", "adapter_continuity_failed",
    "cpu_admission_core_missing", "cpu_admission_core_failed",
    "whole_window_verdict_coverage_incomplete",
    "whole_window_verdict_provenance_invalid", "whole_window_verdict_conflict",
    "calibration_bracket_exceeds_minted_bound",
    "whole_window_drift_allowance_unrecorded",
    "mock_telemetry_claim_ineligible", "attribution_dominance_unlicensed",
}
NONTERMINAL_CODES = {
    "exact_corner_widened_absolute_floor_unavailable",
    "exact_corner_widened_comparative_floor_unavailable",
}
EXPECTED_CELL_IDS = {
    *(f"A_{s}" for s in ("1p5B_prompt", "1p5B_decode", "7B_prompt", "7B_decode")),
    *(f"B1_{s}" for s in ("1p5B_prompt", "1p5B_decode", "7B_prompt", "7B_decode")),
    *(f"B2_{s}" for s in ("1p5B_prompt", "1p5B_decode", "7B_prompt", "7B_decode")),
    *(f"D_{s}" for s in ("1p5B_prompt", "1p5B_decode", "7B_prompt", "7B_decode")),
    "C1_1p5B_prompt", "C1_1p5B_decode", "C2_7B_prompt", "C2_7B_decode",
}

CELL_RE = re.compile(
    r"<!-- CELL_BRANCH_SET: (?P<id>[A-Za-z0-9_]+); SELECT EXACTLY ONE BRANCH -->"
    r"(?P<body>.*?)<!-- END_CELL_BRANCH_SET: (?P=id) -->", re.S)
BRANCH_RE = re.compile(r"^  \*\*BRANCH ([TNLU]) — [^\n]+\*\*$", re.M)
PREDICATE_RE = re.compile(
    r"<!-- VARIANT_PREDICATE (?P<id>7_(?:A|B1|B2|C1|C2|C3|D)):\n"
    r"(?P<expr>.*?)\n-->", re.S)
MEASUREMENT_RE = re.compile(
    r"<!-- MEASUREMENT_RENDER: (?P<id>(?:1p5B|7B)_(?:prompt|decode)) -->"
    r"(?P<body>.*?)<!-- END_MEASUREMENT_RENDER: (?P=id) -->", re.S)
ROW_RE = re.compile(
    r"<!-- ROW_RENDER: (?P<id>[a-z_]+) -->"
    r"(?P<body>.*?)<!-- END_ROW_RENDER: (?P=id) -->", re.S)

CANONICAL_CELL_SCHEMA_SHA256 = (
    "ed5216bb3d785378f3c9e786478f20866ca072dfb5b185423206fe5a0491a69a"
)


class TemplateLintError(AssertionError):
    pass


def norm(value: str) -> str:
    return " ".join(value.split())


def need(errors: list[str], condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def section(text: str, heading: str) -> str:
    start = text.find(heading + "\n")
    if start < 0:
        return ""
    end = text.find("\n## ", start + len(heading) + 1)
    return text[start:] if end < 0 else text[start:end]


def branch_parts(body: str) -> tuple[list[str], dict[str, str]]:
    matches = list(BRANCH_RE.finditer(body))
    labels = [m.group(1) for m in matches]
    parts = {}
    for i, match in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        parts[match.group(1)] = body[match.start():end]
    return labels, parts


def cell_stem(cell_id: str) -> str:
    return cell_id.split("_", 1)[1]


def normalize_cell_body(body: str, stem: str) -> str:
    model, phase = stem.split("_")
    model_display = "1.5B" if model == "1p5B" else model
    display = "prompt-processing" if phase == "prompt" else "token-generation"
    value = body.replace(f"{model_display} {display} cell", "MODEL PHASE cell")
    return norm(value.replace(stem, "CELL"))


def tokenize_expr(expression: str) -> list[str]:
    tokens = re.findall(r"[A-Za-z_][A-Za-z0-9_]*|\(|\)", expression)
    if re.sub(r"\s+", "", expression).upper() != "".join(tokens).upper():
        raise ValueError(f"invalid predicate syntax near {expression!r}")
    return tokens


class PredicateParser:
    def __init__(self, expression: str):
        self.tokens = tokenize_expr(expression)
        self.index = 0

    def peek(self):
        return self.tokens[self.index] if self.index < len(self.tokens) else None

    def take(self, expected=None):
        token = self.peek()
        if token is None or (expected is not None and token.upper() != expected):
            raise ValueError(f"expected {expected or 'token'}, got {token}")
        self.index += 1
        return token

    def parse(self):
        tree = self.expr()
        if self.peek() is not None:
            raise ValueError(f"unexpected token {self.peek()}")
        return tree

    def expr(self):
        node = self.term()
        while (self.peek() or "").upper() == "OR":
            self.take("OR")
            node = ("OR", node, self.term())
        return node

    def term(self):
        node = self.unary()
        while (self.peek() or "").upper() == "AND":
            self.take("AND")
            node = ("AND", node, self.unary())
        return node

    def unary(self):
        token = self.peek()
        if token is None:
            raise ValueError("unexpected end of predicate")
        if token.upper() == "NOT":
            self.take("NOT")
            return ("NOT", self.unary())
        if token == "(":
            self.take("(")
            node = self.expr()
            self.take(")")
            return node
        if token.upper() in {"AND", "OR"}:
            raise ValueError(f"unexpected operator {token}")
        return ("IDENT", self.take())


def parse_expr(expression: str):
    return PredicateParser(expression).parse()


def eval_expr(node, values: dict[str, bool]) -> bool:
    if node[0] == "IDENT":
        return bool(values.get(node[1], False))
    if node[0] == "NOT":
        return not eval_expr(node[1], values)
    if node[0] == "AND":
        return eval_expr(node[1], values) and eval_expr(node[2], values)
    if node[0] == "OR":
        return eval_expr(node[1], values) or eval_expr(node[2], values)
    raise ValueError(f"unknown AST node {node[0]}")


def expr_atoms(node) -> set[str]:
    if node[0] == "IDENT":
        return {node[1]}
    if node[0] == "NOT":
        return expr_atoms(node[1])
    return expr_atoms(node[1]) | expr_atoms(node[2])


def expr_key(node) -> str:
    if node[0] == "IDENT":
        return node[1]
    if node[0] == "NOT":
        return f"NOT({expr_key(node[1])})"
    return f"({expr_key(node[1])} {node[0]} {expr_key(node[2])})"


def implies_atom(node, atom: str) -> bool:
    atoms = sorted(expr_atoms(node) | {atom})
    for bits in itertools.product((False, True), repeat=len(atoms)):
        values = dict(zip(atoms, bits))
        if eval_expr(node, values) and not values[atom]:
            return False
    return True


def parse_variant_predicates(text: str):
    trees, raw = {}, {}
    for match in PREDICATE_RE.finditer(text):
        variant = match.group("id")
        if variant in trees:
            raise TemplateLintError(f"duplicate VARIANT_PREDICATE {variant}")
        expression = match.group("expr").strip()
        try:
            trees[variant] = parse_expr(expression)
        except ValueError as exc:
            raise TemplateLintError(f"{variant} predicate parse failed: {exc}") from exc
        raw[variant] = expression
    return trees, raw


def render_variant_guard(node) -> str:
    guards = {
        expr_key(parse_expr(
            "window_1p5B_pass AND window_7B_pass AND decode_1p5B_published "
            "AND decode_7B_published AND claim_floor_defined "
            "AND contrast_signed_present AND contrast_interval_present "
            "AND claim_bound_present AND tokenizer_identity_match "
            "AND floor_gate_pass AND direction_gate_pass"
        )): """**SELECTION GUARD — remove after filling:** Choose this variant if and only if
both model-specific floor windows passed, both token-generation cells selected
L or U, the claim-level floor gate was mechanically derived, the authenticated
signed contrast, contrast interval, and claim-side bound are present, and both
arms record the same tokenizer identity, and both the floor and direction gates
passed. If the predicate is false, do not use any sentence from this variant.""",
        expr_key(parse_expr(
            "window_1p5B_pass AND window_7B_pass AND decode_1p5B_published "
            "AND decode_7B_published AND claim_floor_defined "
            "AND contrast_magnitude_present AND claim_bound_present "
            "AND tokenizer_identity_match AND floor_gate_refused"
        )): """**SELECTION GUARD — remove after filling:** Choose this variant if and only if
both model-specific floor windows passed, both token-generation cells selected
L or U, the claim-level floor gate was mechanically derived, the authenticated
contrast magnitude and claim-side bound are present, both arms record the same
tokenizer identity, and the floor gate was refused. If the predicate is false,
do not use any sentence from this variant.""",
        expr_key(parse_expr(
            "window_1p5B_pass AND window_7B_pass AND decode_1p5B_published "
            "AND decode_7B_published AND claim_floor_defined "
            "AND contrast_signed_present AND contrast_interval_present "
            "AND claim_bound_present AND tokenizer_identity_match "
            "AND floor_gate_pass AND direction_gate_refused"
        )): """**SELECTION GUARD — remove after filling:** Choose this variant if and only if
both model-specific floor windows passed, both token-generation cells selected
L or U, the claim-level floor gate was mechanically derived, the authenticated
signed contrast, contrast interval, and claim-side bound are present, the floor
gate passed, both arms record the same tokenizer identity, and the direction
gate was refused. If the predicate is false, do not use any sentence from this
variant.""",
        expr_key(parse_expr(
            "window_1p5B_pass AND window_7B_pass "
            "AND (decode_1p5B_nonpublication OR decode_7B_nonpublication)"
        )): """**SELECTION GUARD — remove after filling:** Choose this variant if and only if
both model-specific windows passed their whole-window verdicts and at least one
token-generation cell selected T or N. If the predicate is false, do not use
any sentence from this variant.""",
        expr_key(parse_expr("window_1p5B_pass AND window_7B_refused")):
            """**SELECTION GUARD:** Select iff the 1.5B whole-window verdict is PASS and the
7B whole-window verdict is REFUSED.""",
        expr_key(parse_expr("window_1p5B_refused AND window_7B_pass")):
            """**SELECTION GUARD:** Select iff the 7B whole-window verdict is PASS and the
1.5B whole-window verdict is REFUSED.""",
        expr_key(parse_expr("window_1p5B_refused AND window_7B_refused")):
            """**SELECTION GUARD:** Select iff the 1.5B whole-window verdict is REFUSED and the
7B whole-window verdict is REFUSED.""",
    }
    key = expr_key(node)
    if key in guards:
        return guards[key]
    return (
        "**SELECTION GUARD — remove after filling:** Choose this variant if "
        f"and only if {key}. If the predicate is false, do not use any "
        "sentence from this variant."
    )


def parse_section6_predicates(text: str):
    marker = "The master §6 selection predicates are:"
    start = text.find(marker)
    fence_mark = chr(96) * 3
    fence = text.find(fence_mark + "text", start)
    end = text.find(fence_mark, fence + len(fence_mark + "text"))
    block = text[fence + len(fence_mark + "text"):end]
    found = re.findall(
        r"Variant ([0ABC]) =\n(.*?)(?=\n\nVariant [0ABC] =|\Z)", block, re.S)
    if len(found) != 4:
        raise TemplateLintError("master §6 predicate block must define 0/A/B/C")
    replacements = (
        ("an issued whole-window verdict exists", "verdict_exists"),
        ("whole-window verdict = PASS", "verdict_pass"),
        ("whole-window verdict = REFUSED", "verdict_refused"),
        ("every one of the six registered row outcomes = SUPPORTED", "all_rows_supported"),
        ("at least one of the six registered row outcomes != SUPPORTED", "some_row_not_supported"),
    )
    trees = {}
    for variant, expression in found:
        for old, new in replacements:
            expression = expression.replace(old, new)
        try:
            trees[variant] = parse_expr(expression)
        except ValueError as exc:
            raise TemplateLintError(f"§6 Variant {variant} parse failed: {exc}") from exc
    return trees


def valid_section7_states() -> Iterable[dict[str, bool]]:
    atoms = {
        "window_1p5B_pass", "window_1p5B_refused",
        "window_7B_pass", "window_7B_refused",
        "decode_1p5B_published", "decode_1p5B_nonpublication",
        "decode_7B_published", "decode_7B_nonpublication",
        "claim_floor_defined", "contrast_signed_present",
        "contrast_interval_present", "contrast_magnitude_present",
        "claim_bound_present", "tokenizer_identity_match",
        "floor_gate_pass", "floor_gate_refused",
        "direction_gate_pass", "direction_gate_refused",
    }

    def state(**truths):
        values = {atom: False for atom in atoms}
        values.update(truths)
        return values

    yield state(window_1p5B_pass=True, window_7B_refused=True)
    yield state(window_1p5B_refused=True, window_7B_pass=True)
    yield state(window_1p5B_refused=True, window_7B_refused=True)
    for p1, p7 in ((False, False), (False, True), (True, False)):
        yield state(
            window_1p5B_pass=True, window_7B_pass=True,
            decode_1p5B_published=p1, decode_1p5B_nonpublication=not p1,
            decode_7B_published=p7, decode_7B_nonpublication=not p7)
    common = dict(
        window_1p5B_pass=True, window_7B_pass=True,
        decode_1p5B_published=True, decode_7B_published=True,
        claim_floor_defined=True, claim_bound_present=True,
        tokenizer_identity_match=True)
    yield state(**common, contrast_signed_present=True,
                contrast_interval_present=True, contrast_magnitude_present=True,
                floor_gate_pass=True, direction_gate_pass=True)
    yield state(**common, contrast_magnitude_present=True, floor_gate_refused=True)
    yield state(**common, contrast_signed_present=True,
                contrast_interval_present=True, contrast_magnitude_present=True,
                floor_gate_pass=True, direction_gate_refused=True)


def invalid_section7_states() -> Iterable[dict[str, bool]]:
    """Yield canonical one-required-atom-missing states that select nothing."""
    valid = list(valid_section7_states())[-3:]
    required = (
        (
            "window_1p5B_pass", "window_7B_pass", "decode_1p5B_published",
            "decode_7B_published", "claim_floor_defined",
            "contrast_signed_present", "contrast_interval_present",
            "claim_bound_present", "tokenizer_identity_match",
            "floor_gate_pass", "direction_gate_pass",
        ),
        (
            "window_1p5B_pass", "window_7B_pass", "decode_1p5B_published",
            "decode_7B_published", "claim_floor_defined",
            "contrast_magnitude_present", "claim_bound_present",
            "tokenizer_identity_match", "floor_gate_refused",
        ),
        (
            "window_1p5B_pass", "window_7B_pass", "decode_1p5B_published",
            "decode_7B_published", "claim_floor_defined",
            "contrast_signed_present", "contrast_interval_present",
            "claim_bound_present", "tokenizer_identity_match",
            "floor_gate_pass", "direction_gate_refused",
        ),
    )
    seen = set()
    for state, atoms in zip(valid, required):
        for atom in atoms:
            flipped = dict(state)
            flipped[atom] = False
            key = tuple(sorted(flipped.items()))
            if key not in seen:
                seen.add(key)
                yield flipped


def expected_measurement_body(renderer_id: str) -> str:
    model, phase = renderer_id.split("_")
    display = "prompt-processing" if phase == "prompt" else "token-generation"
    token = "prompt" if phase == "prompt" else "output"
    # Hoisted out of the f-string below: backslash escapes inside an
    # f-string EXPRESSION are Python 3.12+ (PEP 701); CI runs 3.11.
    # Behavior-identical compat fix, 2026-08-09.
    prefill_note = (
        "\n**This prefill value remains floors-only, so it supports no model-size\n"
        "direction claim.** Gross joules per request remain primary.\n"
        if phase == "prompt"
        else ""
    )
    return f"""

**PRESENT GUARD:** Emit the gross measurement clause only when the authenticated
phase estimate, both composed interval endpoints, and independent-valid-bundle
count exist.

**PRESENT TEXT:** Gross {display} energy was
[E_{model}_{phase}_J_per_request] J per request, with a fully composed interval of
[E_{model}_{phase}_lower_J]–[E_{model}_{phase}_upper_J] J across
[N_bundles_{model}_{phase}] independent valid run bundles.
{prefill_note}

**ABSENT TEXT:** No gross {display} energy estimate is reported because
the authenticated estimate-and-interval record is unavailable. An absent
measurement is not zero.

**COMPANION GUARD:** Append the companion clause only when its authenticated
per-token value and runtime-observed denominator provenance both exist.

**COMPANION TEXT:** Its tokenizer-scoped companion was
[E_{model}_{phase}_J_per_token] J per recorded {token} token. The
denominator is the token count recorded by the runtime for that request, not a
requested maximum or generator estimate.

**NO-COMPANION TEXT:** No per-token companion is reported because an
authenticated runtime-observed denominator is unavailable.

"""


def containing_interval(position: int, intervals):
    for start, end, identity in intervals:
        if start <= position < end:
            return identity
    return None


def code_set(text: str, name: str) -> set[str]:
    match = re.search(rf"{name} = \{{\n(?P<body>.*?)\n\}}", text, re.S)
    if not match:
        return set()
    return {
        item.strip().rstrip(",")
        for item in match.group("body").splitlines() if item.strip()
    }


def strip_non_prose(text: str) -> str:
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    fence_mark = chr(96) * 3
    return re.sub(re.escape(fence_mark) + r".*?" + re.escape(fence_mark),
                  "", text, flags=re.S)


def lint_text(text: str) -> None:
    errors: list[str] = []
    headings = (
        "## Fill key", "### Source values", "### Mechanical derivations",
        "### Cell-state inputs", "### N-branch available-diagnostic renderer",
        "### Plain-language outcome fills", "### §7 variant predicates",
    )
    positions = [text.find(heading) for heading in headings]
    need(errors, all(p >= 0 for p in positions) and positions == sorted(positions),
         "fill-key sections are missing or out of order")
    for heading in headings:
        need(errors, text.count(heading) == 1, f"{heading} must occur once")
    need(errors,
         "`tokenizer_identity_match` is the same-tokenizer selector atom."
         in text,
         "fill key does not define tokenizer_identity_match as a selector rule")

    need(errors, code_set(text, "TERMINAL_REASON_CODES") == TERMINAL_REASON_CODES,
         "TERMINAL_REASON_CODES is not the adopted closed set")
    need(errors, code_set(text, "NONTERMINAL_EXACT_FLOOR_UNAVAILABLE_CODES") == NONTERMINAL_CODES,
         "NONTERMINAL_EXACT_FLOOR_UNAVAILABLE_CODES is not the adopted closed set")
    selector_text = text.replace(chr(96), "")
    for fragment in (
        "Unknown code, malformed metadata, or stored/recomputed mismatch => STOP_FILL.",
        "Before selecting any branch, classify both components independently as terminal, exact-unavailable, or exact.",
        "A generically absent, null, or unmatched component in either position => STOP_FILL.",
        "If terminal is nonempty => E=false; select T.",
        "every absent or inexact component must be exact-unavailable under step 3.",
        "Set E=true and X=false; select N.",
        "On the two-exact-component path, set E=true.",
        "Do not infer N from nullness.", "Compute DOMINANCE_STATE:",
        "LICENSED iff at least one component:", "ABSENT iff:",
        "UNLICENSED otherwise.",
        "attribution_dominance_unlicensed, set E=false, and select T.",
        "A=false and DOMINANCE_STATE=ABSENT => select U.",
        "11. Every other state => STOP_FILL.",
        "U is reachable only from ABSENT, never from a generic A=false.",
    ):
        need(errors, norm(fragment) in norm(selector_text),
             f"selector fragment changed/missing: {fragment}")
    for fragment in (
        "Inspect authenticated values in this fixed order:",
        "The available [absolute/comparative] component was [VALUE] J.",
        "No authenticated numeric component or point-only repeatability diagnostic is available for this cell.",
        "Never emit an empty token, an empty sentence",
    ):
        need(errors, norm(fragment) in norm(text),
             f"N diagnostic renderer changed/missing: {fragment}")

    starts = re.findall(r"<!-- CELL_BRANCH_SET: ([A-Za-z0-9_]+);", text)
    ends = re.findall(r"<!-- END_CELL_BRANCH_SET: ([A-Za-z0-9_]+) -->", text)
    blocks = list(CELL_RE.finditer(text))
    need(errors, len(starts) == len(ends) == len(blocks) == 20,
         "expected exactly 20 complete CELL_BRANCH_SET blocks")
    need(errors, set(starts) == EXPECTED_CELL_IDS and len(set(starts)) == 20,
         "CELL_BRANCH_SET IDs do not match A/B1/B2/D/C1/C2")
    guards = {
        "T": "Select this branch first if E_CELL is false because one or more terminal refusal reasons are present.",
        "N": "Select this branch iff E_CELL is true and X_CELL is false.",
        "L": "Select this branch iff E_CELL, X_CELL, and A_CELL are all true.",
        "U": "Select this branch iff E_CELL and X_CELL are true and A_CELL is false.",
    }
    for match in blocks:
        identity = match.group("id")
        stem = cell_stem(identity)
        body = match.group("body")
        labels, parts = branch_parts(body)
        need(errors, labels == ["T", "N", "L", "U"],
             f"{identity}: branch order/count is not T/N/L/U")
        need(errors, "**ELSE**" not in body, f"{identity}: catch-all ELSE is forbidden")
        if labels != ["T", "N", "L", "U"]:
            continue
        for label, guard in guards.items():
            need(errors, norm(guard) in norm(parts[label].replace(chr(96), "")),
                 f"{identity}: {label} guard changed")
        for label in ("T", "N"):
            need(errors, parts[label].count("No floor is published for this cell.") == 1,
                 f"{identity}: {label} must contain exact nonpublication sentence once")
            remainder = parts[label].replace("No floor is published for this cell.", "")
            need(errors, re.search(r"\bpublish(?:ed|es|ing)?\b", remainder, re.I) is None,
                 f"{identity}: {label} contains a publication verb")
        for label in ("L", "U"):
            need(errors, "operative floor is published" in parts[label],
                 f"{identity}: {label} does not publish an operative floor")
            need(errors, "No floor is published" not in parts[label],
                 f"{identity}: {label} contains refusal prose")
        need(errors, "*attribution-limited*" in parts["L"],
             f"{identity}: L lacks attribution-limited publication label")
        for label in ("T", "N", "U"):
            need(errors, not (
                "*attribution-limited*" in parts[label]
                and re.search(r"\bpublish(?:ed|es|ing)?\b", parts[label], re.I)
            ), f"{identity}: non-L branch combines label with publication")

        sentences = [
            sentence for sentence in re.split(r"(?<=[.!?])\s+", norm(parts["U"]))
            if "operative floor is published" in sentence
        ]
        operative = f"[F_{stem}_operative_J]"
        need(errors, len(sentences) == 1,
             f"{identity}: U must have exactly one publication sentence")
        if len(sentences) == 1:
            need(errors, sentences[0].count(operative) == 1,
                 f"{identity}: U must publish exactly its derived operative token")
            need(errors, not any(suffix in sentences[0] for suffix in
                                 ("_abs_J]", "_cmp_J]", "_point_J]", "_corner_J]")),
                 f"{identity}: U publication uses component/diagnostic token")
        schema_hash = hashlib.sha256(
            normalize_cell_body(body, stem).encode("utf-8")).hexdigest()
        need(errors, schema_hash == CANONICAL_CELL_SCHEMA_SHA256,
             f"{identity}: normalized body differs from canonical schema")

    need(errors, "UNLABELLED at its point-only value" not in text,
         "retired point-only publication wording remains")
    need(errors, norm(DERIVATIONS[0]) in norm(text),
         "generic max rule does not define concrete operative tokens")
    source = text[text.find("### Source values"):text.find("### Mechanical derivations")]
    for token in CONCRETE_DERIVED:
        need(errors, re.search(
            rf"(?<![A-Za-z0-9_]){re.escape(token)}(?![A-Za-z0-9_])", source
        ) is None, f"derived token {token} independently declared in Source values")
    for declaration in DERIVATIONS:
        need(errors, norm(text).count(norm(declaration)) == 1,
             f"DERIVE declaration changed/duplicated: {declaration.splitlines()[0]}")
    need(errors, len(re.findall(
        r"\bDERIVE\s+(?:F_\*|F_claim|M_decode|C_decode|S_decode|R_decode)", text
    )) == 7, "unexpected or missing DERIVE declaration")
    forbidden = (
        r"\bF_passing_", r"\bE_passing_", r"\bN_bundles_passing_",
        r"\[F_[A-Za-z0-9]+(?:_[A-Za-z0-9]+)*_corner_J\]",
        r"\[F_[A-Za-z0-9]+(?:_[A-Za-z0-9]+)*_point_J\]",
        r"\[(?:1\.5B/7B|7B/1\.5B)\]",
    )
    for pattern in forbidden:
        need(errors, re.search(pattern, text) is None,
             f"forbidden token matches {pattern}")

    try:
        predicates, _ = parse_variant_predicates(text)
    except TemplateLintError as exc:
        errors.append(str(exc))
        predicates = {}
    need(errors, set(predicates) == set(S7_HEADINGS),
         "expected exactly seven parsed §7 VARIANT_PREDICATE blocks")
    for variant, heading in S7_HEADINGS.items():
        body = section(text, heading)
        match = PREDICATE_RE.search(body)
        need(errors, bool(match) and match.group("id") == variant,
             f"{heading}: predicate is not adjacent to heading")
        if variant in predicates:
            guard = render_variant_guard(predicates[variant])
            lead = body.find("**Lead-in")
            prefix = body if lead < 0 else body[:lead]
            need(errors, norm(guard) in norm(prefix),
                 f"{heading}: visible guard does not render from parsed AST")
    if set(predicates) == set(S7_HEADINGS):
        for index, values in enumerate(valid_section7_states()):
            selected = [name for name, tree in predicates.items()
                        if eval_expr(tree, values)]
            need(errors, len(selected) == 1,
                 f"§7 truth table overlap/gap in valid state {index}: {selected}")
        for index, values in enumerate(invalid_section7_states()):
            selected = [name for name, tree in predicates.items()
                        if eval_expr(tree, values)]
            need(errors, not selected,
                 f"§7 truth table selected variant(s) in per-atom-flipped "
                 f"invalid state {index}: {selected}")
        for variant in ("7_A", "7_B1", "7_B2"):
            for atom in ("decode_1p5B_published", "decode_7B_published",
                         "claim_floor_defined", "tokenizer_identity_match"):
                need(errors, implies_atom(predicates[variant], atom),
                     f"{variant} predicate does not imply {atom}")

    try:
        s6_predicates = parse_section6_predicates(text)
    except TemplateLintError as exc:
        errors.append(str(exc))
        s6_predicates = {}
    if set(s6_predicates) == {"0", "A", "B", "C"}:
        states = itertools.product(
            (False, True), (False, True), (None, "PASS", "REFUSED"),
            itertools.product((False, True), repeat=6))
        for funded, run, verdict, rows in states:
            values = {
                "funded": funded, "run": run,
                "verdict_exists": verdict is not None,
                "verdict_pass": verdict == "PASS",
                "verdict_refused": verdict == "REFUSED",
                "all_rows_supported": all(rows),
                "some_row_not_supported": not all(rows),
            }
            selected = [name for name, tree in s6_predicates.items()
                        if eval_expr(tree, values)]
            need(errors, len(selected) == 1,
                 f"§6 truth table overlap/gap: {funded=}, {run=}, "
                 f"{verdict=}, {rows=}, {selected=}")
    for variant, heading in S6_HEADINGS.items():
        body = section(text, heading)
        immediate = body[len(heading):].lstrip("\n")
        need(errors, immediate.startswith(S6_GUARDS[variant]),
             f"§6 Variant {variant} must have its visible guard immediately "
             "after the heading")
    need(errors, text.count(S6_HEADINGS["0"]) == 1,
         "neutral §6 Variant 0 heading must occur exactly once")
    need(errors, "## §6 Variant 0 — Window C unfunded (DEFAULT)" not in text,
         "retired unfunded-only Variant 0 heading remains")
    for variant in ("A", "B"):
        need(errors, section(text, S6_HEADINGS[variant]).count(BETWEEN) == 1,
             f"§6 Variant {variant} must contain exact ≥3-session paragraph once")
    need(errors, "results\nawait the governing verdict" in section(text, S6_HEADINGS["0"]),
         "§6 Variant 0 lacks run-without-verdict wording")

    measurements = list(MEASUREMENT_RE.finditer(text))
    need(errors, len(measurements) == 16,
         "expected exactly 16 MEASUREMENT_RENDER blocks")
    occurrence_counts = {
        identity: 0 for identity in
        ("1p5B_prompt", "1p5B_decode", "7B_prompt", "7B_decode")
    }
    intervals = []
    for match in measurements:
        identity = match.group("id")
        occurrence_counts[identity] += 1
        intervals.append((match.start(), match.end(), identity))
        need(errors, norm(match.group("body")) ==
             norm(expected_measurement_body(identity)),
             f"{identity}: MEASUREMENT_RENDER schema changed")
    need(errors, occurrence_counts == {
        "1p5B_prompt": 4, "1p5B_decode": 4,
        "7B_prompt": 4, "7B_decode": 4,
    }, f"measurement renderer census changed: {occurrence_counts}")
    phase_token_re = re.compile(
        r"\[(?:(?:E_(?P<emodel>1p5B|7B)_(?P<ephase>prompt|decode)_"
        r"(?:J_per_request|lower_J|upper_J|J_per_token))|"
        r"(?:N_bundles_(?P<nmodel>1p5B|7B)_(?P<nphase>prompt|decode)))\]")
    for match in phase_token_re.finditer(text):
        expected = (
            f"{match.group('emodel') or match.group('nmodel')}_"
            f"{match.group('ephase') or match.group('nphase')}"
        )
        actual = containing_interval(match.start(), intervals)
        need(errors, actual == expected,
             f"phase-measurement token {match.group(0)} is outside matching renderer")

    b_body = section(text, S6_HEADINGS["B"])
    b_rows = {match.group("id"): match for match in ROW_RE.finditer(b_body)}
    row_tokens = {
        "linearity": (
            "S_C_linearity_request_J_per_token",
            "S_C_linearity_decode_J_per_token", "R_C_linearity_limit_J"),
        "null": ("D_C_null_max_abs_J",),
        "empirical_floor": ("R_C_micro_min_x_floor", "R_C_micro_max_x_floor"),
        "phase_attribution": (
            "D_C_additivity_J", "S_C_prompt_invariance_J_per_token"),
        "drift_settling": ("D_C_reference_excursion_J", "T_C_recovery_s"),
        "between_sessions": ("N_C_eligible_sessions",),
    }
    need(errors, set(b_rows) == set(row_tokens),
         "§6 B must contain six adopted ROW_RENDER blocks")
    for row, tokens in row_tokens.items():
        match = b_rows.get(row)
        if not match:
            continue
        body = match.group("body")
        if_start = body.find(f"<!-- IF diagnostic_{row}_present -->")
        else_pos = body.find("<!-- ELSE:", if_start)
        need(errors, if_start >= 0 and else_pos > if_start,
             f"§6 B {row}: present branch markers missing")
        for token in tokens:
            positions = [
                item.start()
                for item in re.finditer(rf"\[{re.escape(token)}\]", b_body)
            ]
            need(errors, len(positions) == 1,
                 f"§6 B {token} must occur exactly once")
            if len(positions) == 1 and if_start >= 0:
                absolute_start = match.start("body") + if_start
                absolute_end = match.start("body") + else_pos
                need(errors, absolute_start <= positions[0] < absolute_end,
                     f"§6 B {token} occurs outside diagnostic_{row}_present")
    drift = b_rows.get("drift_settling")
    if drift:
        passed = "The drift screen passed; the allowance remains positive by construction."
        support_start = drift.group("body").find(
            "<!-- IF outcome_drift_supported -->")
        support_end = drift.group("body").find(
            "<!-- ELSE: emit no passed-screen sentence -->")
        sentence_pos = drift.group("body").find(passed)
        need(errors, support_start < sentence_pos < support_end,
             "§6 B passed-screen sentence is outside outcome_drift_supported")

    c_body = section(text, S6_HEADINGS["C"])
    c_render = re.search(
        r"<!-- PRESENT_DIAGNOSTICS_RENDER: section_6_C.*?"
        r"<!-- END_PRESENT_DIAGNOSTICS_RENDER: section_6_C -->",
        c_body, re.S)
    need(errors, c_render is not None,
         "§6 C PRESENT_DIAGNOSTICS_RENDER is missing")
    c_tokens = (
        "D_C_linearity_diagnostic_J_per_token",
        "D_C_null_diagnostic_J", "D_C_micro_diagnostic_x_floor",
        "D_C_phase_diagnostic_J", "D_C_drift_diagnostic_J",
    )
    for token in c_tokens:
        positions = [
            item.start()
            for item in re.finditer(rf"\[{re.escape(token)}\]", c_body)
        ]
        need(errors, len(positions) == 1,
             f"§6 C {token} must occur exactly once")
        if len(positions) == 1 and c_render:
            need(errors, c_render.start() <= positions[0] < c_render.end(),
                 f"§6 C {token} survives outside present-only renderer")
    for fragment in (
        "ORDER: linearity, null, empirical_floor, phase_attribution, drift_settling",
        "serial commas, and “and” before the final",
        "Their absence is not treated as zero",
        "No authenticated numeric characterization diagnostic is available from the refused window.",
    ):
        need(errors, norm(fragment) in norm(c_body),
             f"§6 C renderer rule changed/missing: {fragment}")

    claim_token_re = re.compile(
        r"\[(?:F_claim_decode_armwise_max_J|E_decode_contrast_[A-Za-z0-9_]+|"
        r"M_decode_contrast_abs_J_per_request|B_decode_claim_J|"
        r"C_decode_floor_clearance_J|S_decode_floor_shortfall_J|"
        r"R_decode_effect_x_floor|S_decode_joint_J)\]")
    section7_intervals = []
    for variant, heading in S7_HEADINGS.items():
        start = text.find(heading + "\n")
        body = section(text, heading)
        if start >= 0 and body:
            section7_intervals.append((start, start + len(body), variant))
    for match in claim_token_re.finditer(text):
        variant = containing_interval(match.start(), section7_intervals)
        tree = predicates.get(variant) if variant else None
        licensed = bool(tree) and all(
            implies_atom(tree, atom) for atom in (
                "decode_1p5B_published", "decode_7B_published",
                "claim_floor_defined"))
        need(errors, licensed,
             f"global claim/contrast token {match.group(0)} at offset "
             f"{match.start()} is outside a predicate-licensed §7 section")
    d_body = section(text, S7_HEADINGS["7_D"])
    for pattern in (
        r"\[F_claim_", r"\[E_decode_contrast_", r"\[M_decode_contrast_",
        r"\[B_decode_claim_", r"\[C_decode_floor_", r"\[S_decode_",
        r"\[R_decode_effect_",
    ):
        need(errors, re.search(pattern, d_body) is None,
             f"§7 D contains forbidden claim/contrast/sizing token {pattern}")
    need(errors, "[CELL_NONPUBLICATION_SUMMARY]" in d_body,
         "§7 D lacks CELL_NONPUBLICATION_SUMMARY")
    for fragment in (
        "The claim-level floor gate is therefore\nundefined",
        "The registered cross-model contrast was not\nevaluated",
        "No claim-side sizing quantity or\nmodel-size direction claim is reported.",
    ):
        need(errors, fragment in d_body,
             f"§7 D terminating denial changed: {fragment}")

    b1 = section(text, S7_HEADINGS["7_B1"])
    for model in ("1p5B", "7B"):
        for phase in ("prompt", "decode"):
            for suffix in ("lower_J", "upper_J"):
                token = f"[E_{model}_{phase}_{suffix}]"
                need(errors, token in b1, f"B1 lacks arm interval {token}")
    for token in (
        "[E_decode_contrast_signed_J_per_request]",
        "[E_decode_contrast_lower_J]", "[E_decode_contrast_upper_J]",
    ):
        need(errors, token not in b1,
             f"B1 magnitude-only shape contains {token}")
    b1_interval_note = norm(
        "Any arm-level intervals reported above are intervals for the "
        "individual arms, not a signed cross-model estimate or a directional "
        "contrast interval.")
    need(errors, b1_interval_note in norm(b1),
         "B1 lacks the exact self-licensing arm-interval sentence")
    for match in re.finditer(r"arm-level intervals reported above", text, re.I):
        prefix = text[max(0, match.start() - 4):match.start()]
        need(errors, re.search(r"(?i)\bany\s+$", prefix) is not None,
             "arm-interval reference is not the self-licensing 'Any' form")
    for variant in ("7_A", "7_B1", "7_B2"):
        body = section(text, S7_HEADINGS[variant])
        need(errors, DENIAL in body,
             f"{variant} lost exact two-half sizing denial")
        need(errors, TOKENIZER_CONDITIONAL in body,
             f"{variant} lacks conditional tokenizer licence")
    need(errors, text.count(DENIAL) == 3,
         "sizing denial must occur in A/B1/B2 only")
    for variant in ("7_C1", "7_C2"):
        body = section(text, S7_HEADINGS[variant])
        need(errors, PROMPT_SCOPE in body,
             f"{variant} lacks prompt/BOS scope sentence")
        need(errors, TOKENIZER_CONDITIONAL in body,
             f"{variant} lacks conditional tokenizer licence")
        need(errors, "Both arms record the SAME tokenizer identity" not in body,
             f"{variant} retains factual tokenizer assertion")
    for variant in ("A", "B", "C"):
        need(errors, TOKENIZER_CONDITIONAL in section(text, S6_HEADINGS[variant]),
             f"§6 Variant {variant} lacks conditional tokenizer licence")
    for match in re.finditer(
            r"both arms record the same tokenizer identity", text, re.I):
        before = text[max(0, match.start() - 5):match.start()]
        para_start = text.rfind("\n\n", 0, match.start()) + 2
        paragraph = text[para_start:match.start()]
        need(errors,
             before == "When " or
             paragraph.lstrip().startswith("**SELECTION GUARD"),
             "factual tokenizer-identity assertion outside the conditional "
             f"licence or a selection guard at offset {match.start()}")
    c3 = """Both model-specific floor windows were refused: the 1.5B window because
[REFUSAL_REASON_1p5B_floor_window], and the 7B window because
[REFUSAL_REASON_7B_floor_window]. Neither window supplies a claim-bearing
phase value or floor. No four-cell floor artifact is issued, the registered
contrast is not evaluated, and no model-size energy ranking follows."""
    need(errors, c3 in section(text, S7_HEADINGS["7_C3"]),
         "C3 terminating prose changed")

    prose = strip_non_prose(text[text.find(S7_HEADINGS["7_A"]):])
    for pattern in (
        r"\[[^\]\n]*:[^\]\n]*/[^\]\n]*\]",
        r"\[[^\]\n]*(supported|refused|failed[_ -]?expected)[^\]\n]*/[^\]\n]*\]",
    ):
        need(errors, re.search(pattern, prose, re.I) is None,
             f"professor-facing enum choice matches {pattern}")

    if errors:
        raise TemplateLintError("\n".join(f"- {error}" for error in errors))


def lint_file(path: Path = TEMPLATE_PATH) -> None:
    lint_text(path.read_text(encoding="utf-8"))


def census(text: str) -> dict[str, int]:
    predicates, _ = parse_variant_predicates(text)
    parse_section6_predicates(text)
    forbidden = (
        r"\bF_passing_", r"\bE_passing_", r"\bN_bundles_passing_",
        r"\[F_[A-Za-z0-9_]+_corner_J\]",
        r"\[F_[A-Za-z0-9_]+_point_J\]",
    )
    return {
        "cell_blocks": len(list(CELL_RE.finditer(text))),
        "section7_predicates": len(predicates),
        "section6_states": 2 * 2 * 3 * 64,
        "section7_states": len(list(valid_section7_states())),
        "section7_invalid_states": len(list(invalid_section7_states())),
        "forbidden_tokens": sum(bool(re.search(pattern, text))
                                for pattern in forbidden),
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("template", nargs="?", type=Path, default=TEMPLATE_PATH)
    args = parser.parse_args(argv)
    try:
        text = args.template.read_text(encoding="utf-8")
        lint_text(text)
        counts = census(text)
    except (OSError, TemplateLintError, ValueError) as exc:
        print(f"results prose template lint: REFUSED\n{exc}")
        return 1
    print(
        "results prose template lint: PASS "
        f"({counts['cell_blocks']} CELL_BRANCH_SET blocks; "
        f"{counts['section7_predicates']} §7 predicates parsed)")
    print(
        "results prose template census: "
        f"{counts['cell_blocks']} blocks; "
        f"{counts['section7_predicates']} §7 predicates parsed; "
        f"§6+§7 truth tables exactly-one over "
        f"{counts['section6_states']}+{counts['section7_states']} enumerated states; "
        f"§7 zero-selection over {counts['section7_invalid_states']} "
        "per-atom-flipped invalid states; "
        f"{counts['forbidden_tokens']} forbidden tokens")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
