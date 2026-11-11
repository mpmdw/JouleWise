"""Synthetic contract tests and AST-only drift checks; no operational imports."""
from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError
from pathlib import Path
import tempfile
from types import MappingProxyType
import unittest

from joulewise.exit_contract import (
    CONTRACTS, PLAN_WORDS, Classified, Contract, ExitClass, ExitCode,
    PlanContractError, as_outcome_map, classify, parse_plan_contract,
)


ROOT = Path(__file__).resolve().parents[1]
# Independent expectations: neither keys nor classes are derived from CONTRACTS.
EXPECTED = {
    "night_driver": {0: ("GO", "SUCCESS"), 3: ("REFUSED", "REFUSED"),
                     4: ("ABORTED", "STOPPED"), 5: ("CHAIN_FAILED", "FAILED"),
                     6: ("COURIER_FAILED", "FAILED")},
    "r1_driver": {0: ("complete", "SUCCESS"), 3: ("refused", "REFUSED"), 4: ("aborted", "STOPPED")},
    "r1_runtime": {0: ("complete", "SUCCESS"), 2: ("refused", "REFUSED"), 3: ("failed", "FAILED"),
                   **{code: ("aborted", "STOPPED") for code in range(129, 256)}},
    "b5_chain": {0: ("completed", "SUCCESS"), 10: ("reservation_failed", "STOPPED"),
                 11: ("pre_calibration_capture_failed", "STOPPED"),
                 12: ("pre_calibration_screen_failed", "STOPPED"),
                 13: ("operative_bound_above_stop", "STOPPED"),
                 64: ("inspection_refused", "REFUSED"), 75: ("horizon_skipped", "STOPPED")},
    "dry_run": {0: ("completed_without_tooling_refusal", "SUCCESS"),
                2: ("tooling_refusal", "REFUSED"), 3: ("outcome_class", "HOLD")},
    "release_check": {0: ("agree", "SUCCESS"), 1: ("hold", "HOLD"), 2: ("refused", "REFUSED")},
    "harvest": {0: ("COLLECTED/NO_COLLECTION/NULL", "SUCCESS"), 2: ("HARVEST_FAULT", "FAILED"),
                3: ("unresolvable_input", "REFUSED"), 4: ("NOT_READY", "HOLD"), 6: ("none_present", "FAILED")},
    "offload": {0: ("ok", "SUCCESS"), 2: ("Refusal", "REFUSED"), 3: ("Mismatch", "FAILED"),
                4: ("DeadlineStop", "STOPPED"), 5: ("TransportError", "FAILED"), 6: ("io_error", "FAILED")},
    "prequal": {0: ("pass", "SUCCESS"), 1: ("fail", "FAILED"),
                3: ("incomplete", "HOLD"), 2: ("usage", "USAGE")},
}


class ClassifierTests(unittest.TestCase):
    def assert_undeclared(self, actual):
        self.assertEqual(actual, Classified(ExitClass.UNDECLARED, "undeclared", False))
        self.assertFalse(actual.is_success)

    def test_every_tool_every_declared_code(self):
        self.assertEqual(set(CONTRACTS), set(EXPECTED))
        for tool, expected in EXPECTED.items():
            self.assertTrue(CONTRACTS[tool].verified)
            self.assertEqual(as_outcome_map(CONTRACTS[tool]), {code: word for code, (word, _) in expected.items()})
            for code, (word, name) in expected.items():
                with self.subTest(tool=tool, code=code):
                    actual = classify(tool, code)
                    self.assertEqual(actual, Classified(ExitClass[name], word, True))
                    self.assertEqual(actual.is_success, name == "SUCCESS")

    def test_every_undeclared_exit_byte(self):
        for tool, expected in EXPECTED.items():
            for code in range(256):
                if code not in expected:
                    with self.subTest(tool=tool, code=code):
                        self.assert_undeclared(classify(tool, code))

    def test_negative_signals_and_out_of_byte_codes(self):
        for tool in EXPECTED:
            for code in (*range(-255, 0), -10**40, 256, 257, 10**40):
                with self.subTest(tool=tool, code=code):
                    self.assert_undeclared(classify(tool, code))

    def test_type_abuse_including_zero_equivalents(self):
        class IntSubclass(int):
            pass

        class EqualToZero:
            def __eq__(self, other):
                return True

        for tool in EXPECTED:
            for value in (None, False, True, 0.0, 3.0, "0", b"0", [], {}, set(),
                          object(), IntSubclass(0), EqualToZero()):
                with self.subTest(tool=tool, value=repr(value)):
                    self.assert_undeclared(classify(tool, value))

    def test_unknown_tool_is_not_an_undeclared_code(self):
        for value in (0, None, False, -9):
            with self.subTest(value=value), self.assertRaises(KeyError):
                classify("missing-tool", value)

    def test_success_property_requires_both_guards(self):
        for category in ExitClass:
            for declared in (True, False):
                with self.subTest(category=category, declared=declared):
                    self.assertEqual(Classified(category, "word", declared).is_success,
                                     category is ExitClass.SUCCESS and declared)

    def test_unverified_contract_fails_closed_even_at_zero(self):
        contract = Contract((ExitCode(0, "complete", ExitClass.SUCCESS),), verified=False)
        self.assert_undeclared(classify(contract, 0))
        self.assertEqual(as_outcome_map(contract), {})

    def test_bounds_guard_cannot_be_bypassed_by_a_declaration(self):
        for code in (-9, 256):
            contract = Contract((ExitCode(code, "complete", ExitClass.SUCCESS),))
            with self.subTest(code=code):
                self.assert_undeclared(classify(contract, code))

    def test_precedence_is_explicit_highest_first(self):
        expected = {"dry_run": (2, 3, 0), "release_check": (2, 1, 0)}
        for tool, contract in CONTRACTS.items():
            with self.subTest(tool=tool):
                self.assertEqual(contract.precedence, expected.get(tool, ()))
                if contract.precedence:
                    self.assertEqual(set(contract.precedence), set(EXPECTED[tool]))
                    self.assertTrue(classify(tool, contract.precedence[-1]).is_success)
                    self.assertFalse(classify(tool, contract.precedence[0]).is_success)

    def test_immutable_data_and_detached_outcome_map(self):
        with self.assertRaises(TypeError):
            CONTRACTS["new"] = Contract(())
        with self.assertRaises(TypeError):
            PLAN_WORDS["GO"] = ExitClass.SUCCESS
        contract = CONTRACTS["night_driver"]
        with self.assertRaises(FrozenInstanceError):
            contract.verified = False
        with self.assertRaises(FrozenInstanceError):
            contract.entries[0].word = "changed"
        with self.assertRaises(FrozenInstanceError):
            classify("night_driver", 0).declared = False
        words = as_outcome_map(contract)
        self.assertIs(type(words), dict)
        words[0] = "changed"
        self.assertEqual(as_outcome_map(contract)[0], "GO")
        self.assertTrue(all(type(key) is int for key in words))

    def test_provenance_and_generation_caveats(self):
        for tool, contract in CONTRACTS.items():
            expanded = []
            for entry in contract.entries:
                with self.subTest(tool=tool, code=entry.code):
                    self.assertIsInstance(entry.sources, tuple)
                    self.assertTrue(entry.sources)
                    for source in entry.sources:
                        self.assertRegex(source, r"^origin/[^:]+:(scripts|joulewise)/[^:]+\.py:[1-9][0-9]*$")
                    expanded.extend(entry.code if isinstance(entry.code, range) else (entry.code,))
            self.assertEqual(len(expanded), len(set(expanded)), tool)
        chain = {entry.code: entry for entry in CONTRACTS["b5_chain"].entries}
        self.assertIn("W1-only", chain[13].note)
        self.assertTrue(all("v4-r11:" in source for source in chain[13].sources))
        self.assertIn("not a terminal chain exit", chain[75].note)


class PlanContractTests(unittest.TestCase):
    def refusal(self, value, reason):
        with self.assertRaises(PlanContractError) as caught:
            parse_plan_contract(value)
        self.assertEqual(caught.exception.reason, reason)
        self.assertEqual(str(caught.exception), reason)

    def test_valid_json_and_integer_keys_all_closed_words(self):
        expected = {0: "complete", 3: "refused", 4: "failed", 5: "stopped", 64: "usage", 75: "hold"}
        self.assertEqual(dict(PLAN_WORDS), {"complete": ExitClass.SUCCESS, "refused": ExitClass.REFUSED,
                                          "failed": ExitClass.FAILED, "stopped": ExitClass.STOPPED,
                                          "usage": ExitClass.USAGE, "hold": ExitClass.HOLD})
        for mapping in (expected, MappingProxyType(expected),
                        {str(code): word for code, word in expected.items()}):
            contract = parse_plan_contract(mapping)
            self.assertEqual(as_outcome_map(contract), expected)
            for code, word in expected.items():
                self.assertEqual(classify(contract, code), Classified(PLAN_WORDS[word], word, True))
            self.assertEqual(classify(contract, 2), Classified(ExitClass.UNDECLARED, "undeclared", False))

    def test_multiple_success_codes_and_zero_need_only_be_declared(self):
        contract = parse_plan_contract({"255": "complete", "0": "refused", "1": "complete"})
        self.assertEqual([entry.code for entry in contract.entries], [0, 1, 255])
        self.assertFalse(classify(contract, 0).is_success)
        self.assertTrue(classify(contract, 1).is_success)
        self.assertTrue(classify(contract, 255).is_success)

    def test_parsed_contract_is_detached_from_input(self):
        mapping = {"0": "complete"}
        contract = parse_plan_contract(mapping)
        mapping["0"] = "failed"
        mapping["3"] = "refused"
        self.assertEqual(as_outcome_map(contract), {0: "complete"})

    def test_refuses_non_mapping(self):
        for value in (None, [], (), "", 0, False, [("0", "complete")]):
            with self.subTest(value=value):
                self.refusal(value, "not_a_mapping")

    def test_refuses_invalid_code_types_and_spelling(self):
        for key in (False, True, None, 0.0, b"0", (0,), "00", "+0", "-0", " 0", "0 ",
                    "0\n", "1.0", "1e0", "٠", "０", "", "-1", "1000"):
            with self.subTest(key=key):
                self.refusal({key: "complete"}, "invalid_code")

    def test_refuses_integer_subclass(self):
        class IntSubclass(int):
            pass
        self.refusal({IntSubclass(0): "complete"}, "invalid_code")

    def test_refuses_out_of_range(self):
        for key in (-1, 256, 10**40, "256", "999"):
            with self.subTest(key=key):
                self.refusal({key: "complete"}, "code_out_of_range")

    def test_refuses_normalized_duplicates(self):
        self.refusal({0: "complete", "0": "complete"}, "duplicate_code")
        self.refusal({"0": "complete", 0: "complete"}, "duplicate_code")

    def test_refuses_unknown_and_non_string_words(self):
        for word in (None, True, 0, [], {}, "", "GO", "success", "ok", "Complete", "complete ",
                     "undeclared", "outcome_class"):
            with self.subTest(word=word):
                self.refusal({"0": word}, "invalid_word")

    def test_refuses_missing_zero_even_with_success(self):
        self.refusal({}, "zero_required")
        self.refusal({"1": "complete"}, "zero_required")

    def test_refuses_missing_success_even_with_zero(self):
        self.refusal({"0": "failed"}, "success_required")
        self.refusal({"0": "refused", "1": "hold"}, "success_required")

    def test_accepts_only_value_not_a_plan_wrapper(self):
        self.refusal({"exit_contract": {"0": "complete"}}, "invalid_code")


# AST fragments include the condition or assignment linking the code to its
# meaning. A bare search for an integer would miss swapped branches. These probes
# are independent of the contract table and never import/execute a cited module.
# Key: (source path, tool key, code or 'signals'); value: (named AST owner, fragment).
PROBES = {}
for code, symbol in ((0, "EXIT_GO"), (3, "EXIT_REFUSED"), (4, "EXIT_ABORTED"),
                     (5, "EXIT_CHAIN_FAILED"), (6, "EXIT_COURIER_FAILED")):
    PROBES["scripts/run_night.py", "night_driver", code] = ("", f"{symbol} = {code}")
for code, symbol in ((0, "EXIT_COMPLETED"), (10, "EXIT_RESERVATION_FAILED"),
                     (11, "EXIT_PRE_CAPTURE_FAILED"), (12, "EXIT_PRE_SCREEN_FAILED"),
                     (13, "EXIT_OPERATIVE_BOUND_STOP"), (64, "EXIT_INSPECTION_REFUSED"),
                     (75, "HORIZON_SKIPPED_RC")):
    PROBES["joulewise/b5/chain.py", "b5_chain", code] = ("", f"{symbol} = {code}")
PROBES.update({
    ("scripts/align_r1_rehearsal.py", "r1_driver", 0): ("run", 'record.update(status="complete", registration_path=str(reg), registration_sha256=hashlib.sha256(staged_registration[1].encode()).hexdigest(), **{k: v for k, v in registration.items() if k not in ("schema", "source")})\nreturn 0'),
    ("scripts/align_r1_rehearsal.py", "r1_driver", 3): ("run", 'record.update(status="refused" if isinstance(error, Refusal) else "aborted", error=f"{type(error).__name__}: {error}")\nreturn 3 if isinstance(error, Refusal) else 4'),
    ("scripts/align_r1_rehearsal.py", "r1_driver", 4): ("run", 'return 3 if isinstance(error, Refusal) else 4'),
    ("joulewise/align/apple/r1_runtime.py", "r1_runtime", 0): ("main", 'record["status"], code = "complete", 0'),
    ("joulewise/align/apple/r1_runtime.py", "r1_runtime", 2): ("", 'EXIT_REFUSED, EXIT_FAILED = 2, 3'),
    ("joulewise/align/apple/r1_runtime.py", "r1_runtime", 3): ("", 'EXIT_REFUSED, EXIT_FAILED = 2, 3'),
    ("joulewise/align/apple/r1_runtime.py", "r1_runtime", "signals"): ("Termination.handler", 'raise SystemExit(128 + signum)'),
    ("joulewise/b5_analysis/dry_run.py", "dry_run", 0): ("_record_exit", "def _record_exit(record):\n    if not record['completed_without_tooling_refusal']: return 2\n    return 3 if any(row['status']=='outcome_class' for row in record['steps']) else 0"),
    ("scripts/release_b5.py", "release_check", 0): ("_release", 'verdict["verdict"] = "agree"\nreturn finish(verdict, restricted, started), 0'),
    ("scripts/release_b5.py", "release_check", 1): ("_release", 'if refusal:\n    verdict["reason"] = refusal\n    return finish(verdict, restricted, started), 1 if disagreement else 2'),
    ("scripts/release_b5.py", "release_check", 2): ("_release", 'if refusal:\n    verdict["reason"] = refusal\n    return finish(verdict, restricted, started), 2'),
    ("scripts/release_v4.py", "release_check", 0): ("", 'EXIT = {"agree": 0, "hold": 1, "refused": 2}'),
    ("scripts/harvest_b5_window.py", "harvest", 0): ("main", 'if record["verdict"] == h.HARVEST_FAULT:\n    return 2\nif record["verdict"] in (h.COLLECTED, h.NO_COLLECTION) and counts.get("planned") and not counts.get("present"):\n    return 6\nreturn 0'),
    ("scripts/harvest_b5_window.py", "harvest", 2): ("main", 'if record["verdict"] == h.HARVEST_FAULT:\n    return 2'),
    ("scripts/harvest_b5_window.py", "harvest", 3): ("main", 'try: pass\nexcept (h.HarvestFault, OSError, ValueError) as exc:\n    print(f"verdict=HARVEST_FAULT reason={type(exc).__name__}:{str(exc)[:200]}")\n    return 3'),
    ("scripts/harvest_b5_window.py", "harvest", 4): ("main", 'try: pass\nexcept h.NotReady as exc:\n    print(f"verdict=NOT_READY reason={exc}")\n    return 4'),
    ("scripts/harvest_b5_window.py", "harvest", 6): ("main", 'if record["verdict"] in (h.COLLECTED, h.NO_COLLECTION) and counts.get("planned") and not counts.get("present"):\n    return 6'),
    ("scripts/offload_window.py", "offload", 0): ("run_offload", 'return 0, outcome'),
    ("scripts/offload_window.py", "offload", 2): ("Refusal", 'code = 2'),
    ("scripts/offload_window.py", "offload", 3): ("Mismatch", 'code = 3'),
    ("scripts/offload_window.py", "offload", 4): ("DeadlineStop", 'code = 4'),
    ("scripts/offload_window.py", "offload", 5): ("TransportError", 'code = 5'),
    ("scripts/offload_window.py", "offload", 6): ("_supervised", 'rc, outcome = 6, {"outcome": "io_error", "reason": f"{type(exc).__name__}:{exc}"}'),
    ("scripts/align_v4_prequal.py", "prequal", 0): ("", 'EXIT = {"pass": 0, "fail": 1, "incomplete": 3}'),
    ("scripts/align_v4_prequal.py", "prequal", 2): ("main", 'parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])\nparser.add_argument("--output", type=Path, required=True, help="new report directory")'),
})
for code in (2, 3):
    PROBES["joulewise/b5_analysis/dry_run.py", "dry_run", code] = PROBES["joulewise/b5_analysis/dry_run.py", "dry_run", 0]
for code in (1, 2):
    PROBES["scripts/release_v4.py", "release_check", code] = PROBES["scripts/release_v4.py", "release_check", 0]
for code in (1, 3):
    PROBES["scripts/align_v4_prequal.py", "prequal", code] = PROBES["scripts/align_v4_prequal.py", "prequal", 0]


def assert_fragment(tree, owner, fragment, label):
    """Find a named owner and exact AST node(s), ignoring formatting and lines."""
    for part in owner.split(".") if owner else ():
        found = [node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name == part]
        if len(found) != 1:
            raise AssertionError(f"{label}: source owner {owner!r} moved or disappeared")
        tree = found[0]
    expected = ast.parse(fragment).body
    # An except probe checks the handler, not the synthetic try/pass wrapper.
    if len(expected) == 1 and isinstance(expected[0], ast.Try):
        expected = expected[0].handlers
    wanted = [ast.dump(node) for node in expected]
    if not owner:
        # A module constant moved into a function/class is no longer the same
        # declaration, even if its spelling and integer are unchanged.
        actual = [ast.dump(node) for node in tree.body]
        if any(actual[i:i + len(wanted)] == wanted for i in range(len(actual) - len(wanted) + 1)):
            return
        raise AssertionError(f"{label}: module declaration changed or moved: {fragment}")
    if len(wanted) == 1 and any(ast.dump(node) == wanted[0] for node in ast.walk(tree)):
        return
    for node in ast.walk(tree):
        for _, value in ast.iter_fields(node):
            if isinstance(value, list):
                actual = [ast.dump(item) if isinstance(item, ast.AST) else None for item in value]
                if any(actual[i:i + len(wanted)] == wanted for i in range(len(actual) - len(wanted) + 1)):
                    return
    raise AssertionError(f"{label}: source declaration changed or moved: {fragment}")


class SourceDriftTests(unittest.TestCase):
    def test_verified_sources_at_head(self):
        baseline_paths = {"scripts/run_night.py", "joulewise/b5/chain.py",
                          "joulewise/b5_analysis/dry_run.py", "scripts/release_b5.py",
                          "scripts/harvest_b5_window.py"}
        trees = {}
        checked = set()
        for tool, contract in CONTRACTS.items():
            if not contract.verified:
                continue
            for entry in contract.entries:
                code = "signals" if isinstance(entry.code, range) else entry.code
                for citation in entry.sources:
                    _, path, _ = citation.split(":")
                    key = (path, tool, code)
                    label = f"{tool}:{code} ({citation})"
                    with self.subTest(entry=label):
                        self.assertIn(key, PROBES, f"{label}: missing drift probe")
                        source = ROOT / path
                        if not source.is_file():
                            self.assertNotIn(path, baseline_paths, f"{label}: source file moved or disappeared")
                            continue  # W1/offload/release-only files absent on main.
                        if path not in trees:
                            trees[path] = ast.parse(source.read_text(encoding="utf-8"))
                        tree = trees[path]
                        if tool == "b5_chain" and code == 13:
                            # Known two-generation difference, not an unverifiable code:
                            # main never declared 13. If W1's declaration arrives, check it.
                            names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
                            if "EXIT_OPERATIVE_BOUND_STOP" not in names:
                                assert_fragment(tree, "", 'STOP_EXITS = {"reservation_failed": EXIT_RESERVATION_FAILED, "pre_calibration_capture_failed": EXIT_PRE_CAPTURE_FAILED, "pre_calibration_screen_failed": EXIT_PRE_SCREEN_FAILED}', label)
                                continue
                        if key not in checked:
                            assert_fragment(tree, *PROBES[key], label)
                            checked.add(key)
        self.assertTrue(baseline_paths <= set(trees))

    def test_drift_checker_rejects_changed_code_and_moved_owner(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "synthetic.py"
            source.write_text("def main():\n    if failed:\n        return 3\n    return 0\n", encoding="utf-8")
            tree = ast.parse(source.read_text(encoding="utf-8"))
            assert_fragment(tree, "main", "if failed:\n    return 3", "synthetic:3")
            assert_fragment(tree, "main", "if failed:\n    return 3\nreturn 0", "synthetic:0")
            for owner, fragment in (("main", "if failed:\n    return 0"),
                                    ("moved", "return 0"), ("main", "return 9")):
                with self.subTest(owner=owner, fragment=fragment), self.assertRaisesRegex(AssertionError, "synthetic:3"):
                    assert_fragment(tree, owner, fragment, "synthetic:3")

    def test_drift_checker_requires_module_scope_for_constants(self):
        assert_fragment(ast.parse("EXIT_GO = 0"), "", "EXIT_GO = 0", "night_driver:0")
        for source in ("EXIT_GO = 1", "def moved():\n    EXIT_GO = 0"):
            with self.subTest(source=source), self.assertRaisesRegex(AssertionError, "night_driver:0"):
                assert_fragment(ast.parse(source), "", "EXIT_GO = 0", "night_driver:0")


if __name__ == "__main__":
    unittest.main()
