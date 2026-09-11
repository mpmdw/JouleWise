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

from joulewise import calibration_epoch_continuation as continuation
from scripts import issue_epoch_continuation as issuer


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
)


def main() -> int:
    paths = [Path(continuation.__file__), Path(issuer.__file__)]
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
        # issuer imports the shared statistic by name; move both references.
        with patch.object(module, function, mutated):
            if module is continuation and function == "equivalence_statistics":
                with patch.object(issuer, function, mutated):
                    result = unittest.TextTestRunner(stream=log).run(test_suite)
            else:
                result = unittest.TextTestRunner(stream=log).run(test_suite)
        assert getattr(module, function) is target
        assert {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in paths} == before
        killed = result.testsRun == 1 and bool(result.failures) and not result.errors
        print(f"C{index:02d} {'KILLED' if killed else 'SURVIVED'} {function}: {original} -> {mutation} | test_{test}")
        if not killed:
            survivors.append(index)
            print(log.getvalue())
    print(f"cuts={len(CUTS)} killed={len(CUTS) - len(survivors)} survivors={len(survivors)} source_sha256_restored=true")
    return 1 if survivors else 0


if __name__ == "__main__":
    raise SystemExit(main())
