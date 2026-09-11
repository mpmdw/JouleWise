"""Run each continuation cut against one killing test, without changing files.

Only a compiled function copy is replaced inside this process. The original
function objects and source-file SHA-256s are checked after every cut.
"""

from __future__ import annotations

import hashlib
import inspect
import io
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from joulewise import calibration_bracketing as bracket
from joulewise import calibration_epoch_continuation as continuation
from scripts import issue_epoch_continuation as issuer


CONVERSE_CHECKS = '''        _require(all(slot["slot"] not in session.finalized_slots
                     for slot in slots if slot["content_id"] is None), "hidden_finalized_row")
        _require(file_finalized == ledger_finalized, "ledger_finalized_slots_mismatch")
        _require(all((row.bracket_slot, row.attempt_id) in file_finalized
                     for row in ledger_snapshot.observations
                     if row.bracket_session_id == session.session_id), "hidden_finalized_row")
'''

# Function, original expression, mutation, single killing test.
CUTS = (
    (continuation, "equivalence_statistics", "max(values)", "min(values)", "full_precision_decimal_extrema_and_range_survive"),
    (continuation, "equivalence_statistics", "min(values)", "max(values)", "full_precision_decimal_extrema_and_range_survive"),
    (continuation, "equivalence_statistics", "value <= level", "level <= level", "one_quantum_above_level_fails_without_writing"),
    (continuation, "equivalence_statistics", "value <= level", "value <= value", "one_quantum_above_level_fails_without_writing"),
    (continuation, "equivalence_statistics", "spread <= bracket", "bracket <= bracket", "range_above_screen_fails_even_when_every_value_meets_level"),
    (continuation, "equivalence_statistics", "spread <= bracket", "spread <= spread", "range_above_screen_fails_even_when_every_value_meets_level"),
    (continuation, "equivalence_statistics", "value <= level", "value < level", "level_equality_passes"),
    (continuation, "equivalence_statistics", "spread <= bracket", "spread < bracket", "range_equality_passes_with_distinct_min_and_max"),
    (continuation, "equivalence_statistics", "high - low", "high - high", "full_precision_decimal_extrema_and_range_survive"),
    (continuation, "equivalence_statistics", "high - low", "low - low", "full_precision_decimal_extrema_and_range_survive"),
    (continuation, "equivalence_statistics", "len(values) >= MINIMUM_RETAINED", "True", "five_retained_is_inconclusive_and_writes_nothing"),
    (issuer, "derive_record", 'disposition == "valid" and resolved', "resolved", "only_valid_resolved_values_are_retained_but_all_finalized_acknowledged"),
    (issuer, "derive_record", 'disposition == "valid" and resolved', 'disposition == "valid"', "only_valid_resolved_values_are_retained_but_all_finalized_acknowledged"),
    (issuer, "_s9_projection", 'Decimal(high) <= Decimal(rule["level_screen_s"])', 'Decimal(rule["level_screen_s"]) <= Decimal(rule["level_screen_s"])', "s9_level_fail_witness_preserves_false_comparison"),
    (issuer, "_s9_projection", 'Decimal(high) <= Decimal(rule["level_screen_s"])', "Decimal(high) <= Decimal(high)", "s9_level_fail_witness_preserves_false_comparison"),
    (issuer, "_s9_projection", 'Decimal(spread) <= Decimal(rule["operative_bracket_screen_s"])', 'Decimal(rule["operative_bracket_screen_s"]) <= Decimal(rule["operative_bracket_screen_s"])', "s9_bracket_fail_witness_preserves_false_comparison"),
    (issuer, "_s9_projection", 'Decimal(spread) <= Decimal(rule["operative_bracket_screen_s"])', "Decimal(spread) <= Decimal(spread)", "s9_bracket_fail_witness_preserves_false_comparison"),
    (continuation, "authenticate_epoch_continuation", 'file_sha == registered.get("file_sha256")', "True", "rotated_byte_surfaces_invalid_and_stale"),
    (continuation, "authenticate_epoch_continuation", CONVERSE_CHECKS, "", "failed_nine_row_night_cannot_hide_three_finalized_rows_to_pass"),
    (continuation, "authenticate_epoch_continuation", 'bool(slot["anchor_v3_detail"])', "True", "unresolved_valid_row_requires_nonempty_anchor_detail"),
    (bracket, "evaluate_calibration_bracket", 'observation.disposition == "systematic-invalid"\n        and dict(observation.identity_epoch) in judged_epochs',
     'observation.disposition == "systematic-invalid"\n        and observation.attempt_id not in acknowledged_attempt_ids\n        and dict(observation.identity_epoch) in judged_epochs',
     "systematic_row_in_the_equivalence_night_still_fires"),
    (issuer, "derive_record", 'observation.classification_disposition == "systematic-invalid"', "False", "prepare_refuses_systematic_failure_night_without_writing"),
    (continuation, "authenticate_epoch_continuation", "file_finalized == ledger_finalized", "True", "finalized_slots_must_match_ledger_attempt_ids"),
    (continuation, "authenticate_epoch_continuation", 'all((row.bracket_slot, row.attempt_id) in file_finalized\n                     for row in ledger_snapshot.observations\n                     if row.bracket_session_id == session.session_id)',
     "True", "every_session_observation_must_be_disclosed"),
    (continuation, "authenticate_epoch_continuation", 'all(slot["slot"] not in session.finalized_slots\n                     for slot in slots if slot["content_id"] is None)',
     "True", "failed_nine_row_night_cannot_hide_three_finalized_rows_to_pass"),
    (continuation, "authenticate_epoch_continuation", "set(slot) == SLOT_KEYS", "True",
     "every_slot_has_exact_documented_keys"),
    (continuation, "authenticate_epoch_continuation", "envelope_holds_over_all_valid(lexemes_all_valid, rule)", "True",
     "failed_nine_row_night_cannot_relabel_over_level_rows_unresolved"),
    (continuation, "authenticate_epoch_continuation", 'lexemes_all_valid.append(slot["b_fiducial_s"])',
     'lexemes_all_valid.extend([slot["b_fiducial_s"]] if slot["anchor_v3_resolved"] else [])',
     "failed_nine_row_night_cannot_relabel_range_extrema_unresolved"),
    (issuer, "derive_record", "not envelope_holds_over_all_valid(all_valid, rule)", "False",
     "prepare_refuses_unresolved_valid_row_above_level_without_writing"),
    (issuer, "derive_record", "all_valid.append(lexeme)", "all_valid.extend([lexeme] if resolved else [])",
     "prepare_refuses_unresolved_valid_row_widening_range_without_writing"),
    (issuer, "derive_record", "if not resolved:", "if False:",
     "prepare_refuses_unresolved_valid_row_above_level_without_writing"),
    (continuation, "envelope_holds_over_all_valid", "value <= level", "level <= level",
     "prepare_refuses_unresolved_valid_row_above_level_without_writing"),
    (continuation, "envelope_holds_over_all_valid", "max(values) - min(values) <= bracket", "bracket <= bracket",
     "prepare_refuses_unresolved_valid_row_widening_range_without_writing"),
    (continuation, "envelope_holds_over_all_valid", "value <= level", "value < level",
     "one_unresolved_valid_row_inside_envelope_prepares_and_authenticates"),
    (continuation, "envelope_holds_over_all_valid", "max(values) - min(values) <= bracket", "max(values) - min(values) < bracket",
     "one_unresolved_valid_row_inside_envelope_prepares_and_authenticates"),
    (continuation, "envelope_holds_over_all_valid", "not values or", "bool(values) and",
     "all_valid_envelope_has_no_minimum_count"),
    (continuation, "envelope_holds_over_all_valid", "return all(", "return len(values) >= MINIMUM_RETAINED and all(",
     "all_valid_envelope_has_no_minimum_count"),
    (continuation, "envelope_holds_over_all_valid", "max(values)", "min(values)",
     "prepare_checks_combined_unresolved_range"),
    (continuation, "envelope_holds_over_all_valid", "min(values)", "max(values)",
     "prepare_checks_combined_unresolved_range"),
    (continuation, "envelope_holds_over_all_valid", "context.prec = 80 + sum(", "context.prec = 28 or sum(",
     "prepare_refuses_unresolved_valid_row_widening_range_without_writing"),
    (continuation, "envelope_holds_over_all_valid", "value <= level", "value <= value",
     "prepare_refuses_unresolved_valid_row_above_level_without_writing"),
    (continuation, "envelope_holds_over_all_valid", "max(values) - min(values) <= bracket", "max(values) - min(values) <= max(values) - min(values)",
     "prepare_refuses_unresolved_valid_row_widening_range_without_writing"),
)


def main() -> int:
    paths = [Path(continuation.__file__), Path(issuer.__file__), Path(bracket.__file__)]
    before = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
    survivors = []
    for index, (module, function, original, mutation, test) in enumerate(CUTS, 1):
        target = getattr(module, function)
        source = inspect.getsource(target)
        if source.count(original) != 1:
            raise RuntimeError(f"cut {index}: expression is not unique")
        namespace = dict(vars(module))
        exec(compile(source.replace(original, mutation), f"<continuation-cut-{index}>", "exec"), namespace)
        mutated = namespace[function]
        name = f"tests.test_epoch_continuation.EpochContinuationTests.test_{test}"
        test_suite = unittest.defaultTestLoader.loadTestsFromName(name)
        log = io.StringIO()
        # issuer imports the shared calculations by name; move both references.
        with patch.object(module, function, mutated):
            if module is continuation and function in {"equivalence_statistics", "envelope_holds_over_all_valid"}:
                with patch.object(issuer, function, mutated):
                    result = unittest.TextTestRunner(stream=log).run(test_suite)
            else:
                result = unittest.TextTestRunner(stream=log).run(test_suite)
        assert getattr(module, function) is target
        assert {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in paths} == before
        killed = result.testsRun == 1 and bool(result.failures) and not result.errors
        print(f"C{index:02d} {'KILLED' if killed else 'SURVIVED'} {function}: {original!r} -> {mutation!r} | test_{test}")
        if not killed:
            survivors.append(index)
            print(log.getvalue())
    print(f"cuts={len(CUTS)} killed={len(CUTS) - len(survivors)} survivors={len(survivors)} source_sha256_restored=true")
    return 1 if survivors else 0


if __name__ == "__main__":
    raise SystemExit(main())
