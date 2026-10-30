"""RC-CMP9-FABLE-REV answer 3: do the producer pins fail when the producer changes? Each mutation edits the origin/main
producer text in memory (test_rc_cmp9.producer is patched; nothing on disk changes) and runs ProducerPinTests plus the
two A1 producer-analysis tests. A mutation that leaves every test passing is a pin that does not pin."""
import io
import re
import subprocess
import sys
import unittest
from unittest import mock

sys.path.insert(0, "/home/user/JouleWise")
from tests.independent_recompute import test_rc_cmp9 as t  # noqa: E402

ORIGINAL = {}


def original(path):
    if path not in ORIGINAL:
        ORIGINAL[path] = subprocess.run(["git", "-C", "/home/user/JouleWise", "show", "origin/main:" + path],
                                        capture_output=True, check=True, text=True).stdout
    return ORIGINAL[path]


def sub(pattern, repl, count=1):
    def apply(text):
        new, n = re.subn(pattern, repl, text, count=count)
        assert n == count, (pattern, n)
        return new
    return apply


A = "joulewise/analysis_engine/artifact.py"
F = "joulewise/results_fill_adapter.py"
D = "joulewise/b5_analysis/disclosures.py"
SE = "joulewise/b5_analysis/sensitivity.py"
BR = "joulewise/b5_analysis/bracket.py"
DC = "joulewise/dominance_closeout.py"
BU = "scripts/build_results_fill_input.py"
MUTATIONS = [
    ("M1 artifact: a key added to _ESTIMATOR_KEYS", A, sub(r"_ESTIMATOR_KEYS = \{\n", '_ESTIMATOR_KEYS = {\n    "extra_key",\n')),
    ("M2 artifact: a key removed from _LOO_ROW_KEYS", A, sub(r'(_LOO_ROW_KEYS = \{[^}]*?)\n\s+"influence_triggers",', r"\1")),
    ("M3 artifact: kept sampling keys no longer conditional on kept_sampling", A,
     sub(r'\(\{"kept_n", "removed_block_ids"\} if kept_sampling else set\(\)\)', '{"kept_n", "removed_block_ids"}')),
    ("M4 fill adapter: a key added to each contrast row", F, sub(r'"contrast_id": row\["contrast_id"\], "metric"', '"contrast_id": row["contrast_id"], "extra": None, "metric"')),
    ("M5 fill adapter: an extended key dropped (df)", F, sub(r'for key in \("df", "t_critical_95"\)', 'for key in ("t_critical_95",)')),
    ("M6 fill adapter: a gamma key added", F, sub(r'"limitations": artifact\["inputs"\]\["limitations"\], "contrasts": rows\}',
                                                   '"limitations": artifact["inputs"]["limitations"], "contrasts": rows, "extra": 1}')),
    ("M7 build script: a campaign key dropped", BU, sub(r",\n\s*'harvest_record_sha256':window\.harvest_record_sha256\}", "}")),
    ("M8 disclosures: a section added to the record", D, sub(r'("fixed_sentences"\s*:\s*\[\s*\])', r'\1, "extra_section": []')),
    ("M9 disclosures: decision_floor renamed (an unconditional line the table would no longer see)", D,
     sub(r'_item\("decision_floor"', '_item("decision_floor2"')),
    ("M10 disclosures: a literal keyword added to harvest_once", D,
     sub(r"no_analysed_window_harvested_twice=", "extra_kw=1, no_analysed_window_harvested_twice=")),
    ("M11 disclosures: monitor_sentence made conditional", D,
     sub(r'\n(\s+)(result\["window_lines"\]\[pack\]\.append\(_item\("monitor_sentence",[^\n]*\))', r'\n\1if pack == "alpha":\n\1    \2')),
    ("M12 disclosures: a tripwire key added", D,
     sub(r"\('excluded_reference_in_screen', ?'kept_member_outside_verdict_membership'\)|\(\"excluded_reference_in_screen\", ?\"kept_member_outside_verdict_membership\"\)",
         '("excluded_reference_in_screen", "kept_member_outside_verdict_membership", "extra_tripwire")')),
    ("M13 disclosures: a cell value key added to _cell_values", D, sub(r'("upper_j": )', r'"extra_j": 0, \1')),
    ("M14 sensitivity: a key appended to _reported_values", SE, sub(r'("attribution_floor_j": [^\n,}]+)', r'\1, "extra_j": 0')),
    ("M15 sensitivity: a record section added", SE, sub(r'("contrasts": \[\])', r'\1, "extra": []')),
    ("M16 bracket: a BMax field added", BR, sub(r"\n(\s+)(value_s:\s*[^\n]+)", r"\n\1\2\n\1extra_s: float")),
    ("M17 closeout: nine independent ratios", DC, sub(r"must contain exactly eight records", "must contain exactly nine records")),
    ("M18 disclosures: a battery code added", D, sub(r'(battery_codes\s*=\s*\()', r'\1"battery.extra", ')),
    ("M19 disclosures: a trigger key added", D, sub(r'("observed_triggers"\s*:)', r'"extra_triggers": 0, \1')),
    ("M20 artifact: a third arm gate allowed", A, sub(r"requires exactly two arm gates", "requires exactly three arm gates")),
]


def run_tests(mutated_path=None, mutate=None):
    def patched(path):
        text = original(path)
        return mutate(text) if path == mutated_path else text
    loader = unittest.TestLoader()
    suite = unittest.TestSuite([loader.loadTestsFromTestCase(t.ProducerPinTests),
                                loader.loadTestsFromName("TableTests.test_unconditional_producer_line_kinds_are_in_the_table", t),
                                loader.loadTestsFromName("TableTests.test_unconditional_keys_of_each_line_are_required", t)])
    stream = io.StringIO()
    with mock.patch.object(t, "producer", side_effect=patched):
        result = unittest.TextTestRunner(stream=stream, verbosity=0).run(suite)
    failed = sorted({test.id().split(".")[-1] for test, _ in result.failures + result.errors})
    return result.testsRun, failed, result.skipped


if __name__ == "__main__":
    ran, failed, skipped = run_tests()
    print(f"unmutated: ran={ran} failed={failed} skipped={len(skipped)}")
    assert not failed and not skipped
    weak = []
    for label, path, mutate in MUTATIONS:
        try:
            mutate(original(path))
        except AssertionError as exc:
            print(f"{label}: MUTATION DID NOT APPLY {exc}")
            weak.append(label)
            continue
        ran, failed, skipped = run_tests(path, mutate)
        print(f"{label}: failed={failed or 'NONE'}")
        if not failed:
            weak.append(label)
    print("mutations:", len(MUTATIONS), "not caught:", weak)
