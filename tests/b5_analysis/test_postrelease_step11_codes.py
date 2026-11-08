"""Exact step-11 tooling taxonomy, using source literals and synthetic failures."""
import ast
from pathlib import Path
import re
import tempfile
import unittest

from joulewise.b5_analysis import dry_run as d, disclosures, sensitivity
from joulewise.b5_analysis.windows import AnalysisRefusal
from scripts import produce_b5_disclosures as script

ROOT = Path(__file__).resolve().parents[2]
NEW_CODES = {
    'disclosure_input_invalid', 'sensitivity_changed_bound_independent_value',
    'sensitivity_floor_composition_differs_from_mint', 'sensitivity_inputs_invalid',
    'sensitivity_record_invalid',
}


class Step11CodeTests(unittest.TestCase):
    def test_step11_emitted_code_literals_and_detail_prefixes_are_registered(self):
        emitted = set()
        for relative in ('joulewise/b5_analysis/sensitivity.py', 'joulewise/b5_analysis/disclosures.py',
                         'scripts/produce_b5_disclosures.py'):
            for node in ast.walk(ast.parse((ROOT/relative).read_text())):
                if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name):
                    continue
                index = {'AnalysisRefusal': 0, '_strict_json': 1}.get(node.func.id)
                if index is None or len(node.args) <= index:
                    continue
                value = node.args[index]
                while isinstance(value, ast.BinOp) and isinstance(value.op, ast.Add):
                    value = value.left
                if isinstance(value, ast.Constant) and isinstance(value.value, str):
                    code = value.value.split(':', 1)[0]
                    if re.fullmatch(r'(sensitivity|disclosure)_[a-z_]+', code):
                        emitted.add(code)
        classes = d.refusal_classes()
        self.assertTrue(NEW_CODES <= emitted)
        self.assertTrue(emitted <= set(classes['tooling_refusal']), emitted-set(classes['tooling_refusal']))
        self.assertTrue(emitted.isdisjoint(classes['outcome_class']))

    def classify(self, operation):
        with tempfile.TemporaryDirectory(prefix='b5-step11-codes-') as directory:
            root = Path(directory)
            state = d.RunState('blind-dry-run', root/'index.json', root, 'a'*40)
            return d._internal_step(state, d.StepRunner(root), '11', operation)[0]

    def test_new_codes_reach_the_real_helper_runner_and_record_as_tooling(self):
        for code in sorted(NEW_CODES):
            def fail(argv):
                raise AnalysisRefusal(code)
            with self.subTest(code=code):
                row = self.classify(fail)
                self.assertEqual((row.status, row.refusal, row.exit_status), ('tooling_refusal', code, 2))

    def test_real_malformed_disclosure_is_a_tooling_refusal(self):
        def fail(argv):
            return script._strict_json(b'not JSON', 'disclosure_input_invalid')
        row = self.classify(fail)
        self.assertEqual((row.status, row.refusal), ('tooling_refusal', 'disclosure_input_invalid'))

    def test_real_invalid_sensitivity_record_is_a_tooling_refusal(self):
        def fail(argv):
            return disclosures._validate_sensitivity({})
        row = self.classify(fail)
        self.assertEqual((row.status, row.refusal), ('tooling_refusal', 'sensitivity_record_invalid'))

    def test_real_invalid_sensitivity_number_is_a_tooling_refusal(self):
        def fail(argv):
            return sensitivity._number(None)
        row = self.classify(fail)
        self.assertEqual((row.status, row.refusal), ('tooling_refusal', 'sensitivity_inputs_invalid'))

    def test_unknown_prefix_lookalikes_stay_unclassified_and_outcomes_are_unchanged(self):
        classes = d.refusal_classes()
        self.assertEqual(classes['outcome_class'], ['claim_side_bound_not_issuable', 'dominance_ratio_zero_denominator'])
        for code in ('sensitivity_future_unknown', 'disclosure_input_invalid_extra'):
            def fail(argv):
                raise AnalysisRefusal(code)
            with self.subTest(code=code):
                row = self.classify(fail)
                self.assertEqual((row.status, row.refusal), ('unclassified_refusal', 'unclassified refusal at step 11'))

    def test_missing_input_details_keep_the_registered_base_token(self):
        def fail(argv):
            raise AnalysisRefusal('disclosure_input_missing:synthetic-role')
        row = self.classify(fail)
        self.assertEqual((row.status, row.refusal), ('tooling_refusal', 'disclosure_input_missing'))
