"""Driver probe for L9-STEP4-OPUS-REV: each step-4 report shape through d.run.

Reuses the synthetic DriverDouble from tests/b5_analysis/test_dry_run.py and
overwrites only the ALPHA extraction report and exit status. Synthetic only.
Run from the repo root: python3.13 -m unittest <this file's module path>.
"""
import dataclasses, json, unittest
from pathlib import Path
from tests.b5_analysis import test_dry_run as t
from joulewise.b5_analysis import dry_run as d

LATER = ('5', '8', '6', '9', '9b', '10', '11')


class Override(t.DriverDouble):
    report = None   # callable(window) -> report value for ALPHA
    exit = 1

    def run(self, main, argv, *, step, window=None, stdout_path=None):
        result = super().run(main, argv, step=step, window=window, stdout_path=stdout_path)
        if step == '4' and window == 'alpha' and type(self).report is not None:
            out = Path(argv[argv.index('--out') + 1])
            out.write_bytes(d._canonical(type(self).report('alpha')))
            result = dataclasses.replace(result, exit_status=type(self).exit)
        return result


def cells(w, target=True, p42=True):
    return [{'cell_id': w + '-target', 'extractable': target}, {'cell_id': w + '-p42', 'extractable': p42}]


def base(w, **kw):
    v = {'schema_version': 'joulewise.detection_floor_extraction.v1',
         'kept_units_binding': {'exclusions_sha256': 'e' * 64, 'harvest_pin': 'a' * 40},
         'spec_membership_refusals': [], 'cells': cells(w)}
    v.update(kw)
    return v


CASES = {
    # name: (exit, report(w), expected run code, expected step-4 alpha (status, refusal), reaches step 5)
    'p42_only': (1, lambda w: base(w, cells=cells(w, p42=False)), 0, ('ok', None), True),
    'target_only': (1, lambda w: base(w, cells=cells(w, target=False)), 3, ('outcome_class', 'outcome-class refusal at step 4'), False),
    'target_and_p42': (1, lambda w: base(w, cells=cells(w, False, False)), 3, ('outcome_class', 'outcome-class refusal at step 4'), False),
    'membership': (1, lambda w: base(w, cells=cells(w, p42=False), spec_membership_refusals=[{'bundle_id': 'x'}]), 2, ('tooling_refusal', 'extraction_spec_membership_refused'), False),
    'report_list': (1, lambda w: [], 2, ('tooling_refusal', 'extraction_report_malformed'), False),
    'report_null': (1, lambda w: None, 2, ('tooling_refusal', 'extraction_report_malformed'), False),
    'cell_missing': (1, lambda w: base(w, cells=cells(w, p42=False)[1:]), 2, ('tooling_refusal', 'extraction_cell_set_differs_from_spec'), False),
    'dup_id': (1, lambda w: base(w, cells=cells(w, p42=False) + cells(w)[:1]), 2, ('tooling_refusal', 'extraction_cell_ids_duplicated'), False),
    'nonbool': (1, lambda w: base(w, cells=[{'cell_id': w + '-target', 'extractable': 0}, {'cell_id': w + '-p42', 'extractable': False}]), 2, ('tooling_refusal', 'extraction_extractable_not_boolean'), False),
    'nothing_refused': (1, lambda w: base(w), 2, ('tooling_refusal', 'extraction_exit_without_refused_cell'), False),
    # Exit 0 with a refused target cell or a non-mapping report (pre-existing / regression probes).
    'exit0_target_refused': (0, lambda w: base(w, cells=cells(w, target=False)), None, None, None),
    'exit0_report_list': (0, lambda w: [], None, None, None),
}


class DriverProbe(t.DriverAcceptanceTests):
    def setUp(self):
        super().setUp(); Override.report = None; Override.exit = 1

    def go(self, name):
        Override.exit, Override.report = CASES[name][0], CASES[name][1]
        result = self.execute(runner=Override)
        rows = [r for r in result.record['steps'] if r['step'] == '4']
        return result, rows

    def test_cases(self):
        for name, (status, rep, code, alpha, step5) in CASES.items():
            with self.subTest(name):
                t.DriverDouble.calls = []
                result, rows = self.go(name)
                a = rows[0]
                reached5 = any(s == '5' for s, _, _ in t.DriverDouble.calls)
                print(f"{name:22} run={result.code} step4-alpha=({a['status']}, {a['refusal']}, registered={a['registered_exit']}) "
                      f"windows={[r['window'] for r in rows]} step5_called={reached5} "
                      f"later={sorted({r['status'] for r in result.record['steps'] if r['step'] in LATER})}")
                raw = result.path.read_text()
                for token in ('-target', '-p42', 'floor_cell_not_extractable', '"extractable"'):
                    self.assertNotIn(token, raw, (name, token))
                if code is None: continue
                self.assertEqual(result.code, code)
                self.assertEqual((a['status'], a['refusal']), alpha)
                self.assertEqual(reached5, step5)
                if not step5:
                    self.assertEqual([r['window'] for r in rows], ['alpha'])
                    self.assertTrue(all(r['status'] == 'not_run' for r in result.record['steps'] if r['step'] in LATER))


if __name__ == '__main__':
    unittest.main()
