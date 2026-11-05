"""Renderer integration on the repo's small synthetic comparator/producer builders.

No analysis driver, raw study inputs, or restricted directory is accessed. The
comparator runs on the existing synthetic files under TMPDIR/artifacts only.
"""
from copy import deepcopy
from contextlib import redirect_stderr
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from joulewise.b5_analysis import results_renderer as r
from joulewise.b5_analysis import dry_run as driver
from joulewise.b5_analysis.disclosures import render_disclosures
from scripts import render_b5_results as cli
from tests.independent_recompute import test_comparator as fixtures


class SyntheticRelease:
    def __init__(self, root):
        self.root = root
        self.artifacts = root / 'artifacts'
        self.files = fixtures.l9_files()
        self.fill_name = f'outputs/{fixtures.SHA}-results-fill-input.json'
        self.disclosure_name = f'disclosures/{fixtures.SHA}.json'
        self.verdict_name = f'outputs/{fixtures.SHA}-claim-verdicts.json'
        self.files[self.disclosure_name].pop('note', None)
        fill, verdicts = self.files[self.fill_name], self.files[self.verdict_name]
        gamma = fill['gamma']
        # Parent header absent from the arithmetic comparator's fixture: copy
        # the adapter's input identity fields without inventing new estimates.
        verdicts['claim_verdicts_id'] = gamma['claim_verdicts_id']
        verdicts['inputs'] = {'evidence_class': gamma['evidence_class'], 'limitations': gamma['limitations'],
                              'analysis_manifest': gamma['finalized_manifest'], 'floor_artifact': gamma['floor_artifact']}
        gamma['claim_verdicts_sha256'] = r.sha(fixtures.written(self.verdict_name, verdicts))
        self.ours = fixtures.recompute_output()
        self.ours.update(schema='joulewise.independent_recompute_b5.v1', mode='REGISTERED')
        self.recompute_path = root / 'recompute.json'
        self.recompute_path.write_bytes(r.canonical(self.ours))
        self.comparison_path = root / 'comparison.json'
        self.index_path = fixtures.WINDOW_INDEX
        steps = [{'step': step, 'window': None, 'status': 'ok', 'exit_status': 0, 'registered_exit': None,
                  'schema_valid': True, 'outputs': [], 'refusal': None, 'flags': []} for step in driver.STEP_IDS]
        # D-189's exact allowed non-stopping row, made by the driver's builder.
        nonissuance = next(row for row in steps if row['step'] == '9b')
        nonissuance.update(status='outcome_class', exit_status=3, schema_valid=None,
                           refusal='outcome-class refusal at step 9b')
        self.record = driver.build_dry_run_record(mode='release', analysis_commit='a' * 40,
            window_index_sha256=r.sha(self.index_path.read_bytes()),
            sealed={k: 'b' * 64 for k in driver.SEAL_KEYS}, steps=steps)
        self.write()
        # The real independent comparator on the repo's synthetic outputs;
        # redirect its conventional directory name BEFORE any filesystem I/O.
        with mock.patch.object(r.cmp, 'RESTRICTED', 'artifacts'), \
             mock.patch.object(r.cmp, 'RECORD', 'B5-RELEASE-RECORD.json'):
            self.report = r.cmp.run(root, self.recompute_path, window_index=self.index_path)
        assert not self.report['structure_flags'], self.report['structure_flags']
        assert not self.report['coverage']['unmapped'], self.report['coverage']['unmapped']
        assert all(c['fail'] == 0 for c in self.report['counts'].values()), self.report['counts']
        self.comparison_path.write_bytes(r.canonical(self.report))

    def write(self):
        for step in self.record['steps']:
            step['outputs'] = []
        for name, value in self.files.items():
            raw = fixtures.written(name, value)
            path = self.artifacts / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
            step = '9' if name == self.verdict_name else '11'
            next(s for s in self.record['steps'] if s['step'] == step)['outputs'].append({'name': name, 'sha256': r.sha(raw)})
        record = self.files[self.disclosure_name]
        for released in (True, False):
            name = f"disclosures/{fixtures.SHA}.{'released' if released else 'unreleased'}.txt"
            raw = render_disclosures(record, released=released).encode()
            (self.artifacts / name).write_bytes(raw)
            self.record['steps'][-1]['outputs'].append({'name': name, 'sha256': r.sha(raw)})
        (self.root / 'B5-RELEASE-RECORD.json').write_bytes(r.canonical(self.record))

    def load(self):
        return r.load_inputs(self.root, self.artifacts, self.comparison_path, self.recompute_path, self.index_path)

    def argv(self):
        return ['--release-dir', str(self.root), '--artifacts-dir', str(self.artifacts),
                '--comparison', str(self.comparison_path), '--recompute', str(self.recompute_path),
                '--window-index', str(self.index_path)]


def reviewed(inputs):
    """Synthetic reader attestation only; never used on live study artifacts."""
    review = r.prepare_review(inputs)
    review['gate'] = {'release_event': 'SYNTHETIC release event', 'reader': 'synthetic reader',
                      'first_read_utc': '2026-11-05T00:00:00Z', 'results_cold_gate': 'SYNTHETIC gate',
                      'judge': 'synthetic judge', 'refuter': 'synthetic refuter'}
    for check in review['checks'].values():
        if check['status'] == 'PENDING':
            check.update(status='HAND_CHECKED', reviewer='synthetic reader',
                         recompute_pointers=['/contrasts'], note='SYNTHETIC test attestation; no live validation')
    return review


class ResultsRendererTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='b5-renderer-')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.fixture = SyntheticRelease(self.root)

    def test_complete_candidate_and_byte_validator(self):
        inputs = self.fixture.load()
        review = reviewed(inputs)
        expected = r.render(inputs, review)
        destination = self.root / 'paper-candidate'
        r.publish(destination, expected)
        r.validate_rendered(destination, expected)
        text = expected['Results.md'].decode()
        for cid in (fixtures.DECODE, fixtures.PREFILL):
            self.assertEqual(text.count('| ' + cid + ' | not_resolvable |'), 1)
        self.assertIn('claim_side_bound_not_issuable; no VerifiedClaimEvidence; STOP_FILL', text)
        self.assertIn('NEEDS-LEAD', text)
        provenance = json.loads(expected['provenance.json'])
        keys = {row['leaf'] for row in provenance['leaves']}
        self.assertEqual(keys, set(review['checks']))
        for row in provenance['leaves']:
            label, _ = row['leaf'].split(':', 1)
            self.assertEqual(row['value'], r.resolve(inputs.documents[label], row['json_pointer']))
            self.assertEqual(row['sha256'], inputs.bindings[label])
        (destination / 'Results.md').write_text(text.replace('not_resolvable', 'direction_supported', 1))
        with self.assertRaisesRegex(r.RendererRefusal, 'rendered_mismatch'):
            r.validate_rendered(destination, expected)
        with self.assertRaisesRegex(r.RendererRefusal, 'output_exists'):
            r.publish(destination, expected)

    def test_cli_prepare_render_and_validate(self):
        args = self.fixture.argv()
        checks = self.root / 'checks.json'
        self.assertEqual(cli.main(args + ['--prepare-checks', str(checks)]), 0)
        pending = json.loads(checks.read_bytes())
        self.assertTrue(any(c['status'] == 'PENDING' for c in pending['checks'].values()))
        out = self.root / 'cli-candidate'
        with redirect_stderr(io.StringIO()):
            self.assertEqual(cli.main(args + ['--checks', str(checks), '--out', str(out)]), 2)
        self.assertFalse(out.exists())
        preview = self.root / 'cli-preview'
        self.assertEqual(cli.main(args + ['--checks', str(checks), '--preview', str(preview)]), 0)
        self.assertIn('PENDING / REVIEW CANDIDATE ONLY', (preview / 'Results.md').read_text())
        checks.write_bytes(r.canonical(reviewed(self.fixture.load())))
        self.assertEqual(cli.main(args + ['--checks', str(checks), '--out', str(out)]), 0)
        self.assertEqual(cli.main(args + ['--checks', str(checks), '--validate-rendered', str(out)]), 0)

    def test_missing_extra_or_changed_source_leaf_refuses(self):
        original = deepcopy(self.fixture.files)
        for mutate in (lambda row: row.pop('estimate'), lambda row: row.update(unregistered=5),
                       lambda row: row['metric'].pop('unit'), lambda row: row.update(estimate=99),
                       lambda row: row['floor'].update(unregistered=0)):
            with self.subTest(mutate=mutate):
                self.fixture.files = deepcopy(original)
                mutate(self.fixture.files[self.fixture.fill_name]['gamma']['contrasts'][0])
                self.fixture.write()
                with self.assertRaises((r.RendererRefusal, KeyError)):
                    self.fixture.load()

    def test_dropped_added_reordered_or_duplicated_contrast_refuses(self):
        original = deepcopy(self.fixture.files)
        for action in ('drop', 'add', 'reverse', 'duplicate'):
            with self.subTest(action=action):
                self.fixture.files = deepcopy(original)
                rows = self.fixture.files[self.fixture.fill_name]['gamma']['contrasts']
                if action == 'drop':
                    rows.pop()
                elif action in ('add', 'duplicate'):
                    rows.append(deepcopy(rows[0]))
                    if action == 'add':
                        rows[-1]['contrast_id'] = 'unregistered'
                else:
                    rows.reverse()
                self.fixture.write()
                with self.assertRaises(r.RendererRefusal):
                    self.fixture.load()

    def test_digest_and_deterministic_disclosure_views_are_checked(self):
        path = self.fixture.artifacts / self.fixture.fill_name
        original = path.read_bytes()
        path.write_bytes(original + b' ')
        with self.assertRaisesRegex(r.RendererRefusal, 'release_digest_mismatch'):
            self.fixture.load()
        self.fixture.write()
        self.fixture.files[self.fixture.disclosure_name]['block_lines'][0]['text'] = 'changed text'
        # Recommit only JSON; the old view is now inconsistent with the record.
        raw = fixtures.written(self.fixture.disclosure_name, self.fixture.files[self.fixture.disclosure_name])
        (self.fixture.artifacts / self.fixture.disclosure_name).write_bytes(raw)
        for output in self.fixture.record['steps'][-1]['outputs']:
            if output['name'] == self.fixture.disclosure_name:
                output['sha256'] = r.sha(raw)
        (self.root / 'B5-RELEASE-RECORD.json').write_bytes(r.canonical(self.fixture.record))
        with self.assertRaisesRegex(r.RendererRefusal, 'disclosure_view_mismatch'):
            self.fixture.load()

    def test_stale_missing_extra_or_pending_review_refuses(self):
        inputs = self.fixture.load()
        baseline = reviewed(inputs)
        for action in ('pending', 'stale', 'missing', 'extra', 'bad_pointer', 'auto_changed'):
            review = deepcopy(baseline)
            leaf = next(k for k, v in review['checks'].items() if v['status'] == 'HAND_CHECKED')
            if action == 'pending':
                review['checks'][leaf]['status'] = 'PENDING'
            elif action == 'stale':
                review['bindings']['fill'] = 'f' * 64
            elif action == 'missing':
                review['checks'].pop(leaf)
            elif action == 'extra':
                review['checks']['fill:/unknown'] = review['checks'][leaf]
            elif action == 'bad_pointer':
                review['checks'][leaf]['recompute_pointers'] = ['/not-present']
            else:
                auto = next(k for k, v in review['checks'].items() if v['status'] == 'AUTO_AGREE')
                review['checks'][auto]['key'] = 'someone-elses-row'
            with self.subTest(action=action), self.assertRaises(r.RendererRefusal):
                r.render(inputs, review)

    def test_recompute_failure_wrong_bars_or_swapped_binding_refuses(self):
        report = deepcopy(self.fixture.report)
        for action in ('fail', 'bars', 'program', 'leaf'):
            value = deepcopy(report)
            if action == 'fail':
                value['comparisons'][0]['verdict'] = 'DISAGREE'
            elif action == 'bars':
                value['bar_set'] = 's13_block6'
            elif action == 'program':
                value['recompute_program_sha256'] = 'e' * 64
            else:
                row = next(r for r in value['comparisons'] if r['family'] == 'contrast_j')
                row['l9'] = 9999
            self.fixture.comparison_path.write_bytes(r.canonical(value))
            with self.subTest(action=action), self.assertRaises(r.RendererRefusal):
                r.prepare_review(self.fixture.load())

    def test_existing_comparator_null_gap_stays_closed(self):
        # The comparator's own ConsultControlTests witness, using artifacts/
        # instead of its conventional restricted directory. This is not a fix
        # or waiver: a legitimate refused-arm null still cannot enter Results.
        for name in (self.fixture.fill_name, self.fixture.verdict_name):
            value = self.fixture.files[name]
            rows = value['gamma']['contrasts'] if name == self.fixture.fill_name else value['contrasts']
            rows[0]['floor']['arm_gates'][1].update(status='refused', floor_gate_j=None)
        self.fixture.ours['floor_cells']['Qwen3-8B-4bit/decode']['floor_gate_j'] = None
        self.fixture.recompute_path.write_bytes(r.canonical(self.fixture.ours))
        self.fixture.write()
        with mock.patch.object(r.cmp, 'RESTRICTED', 'artifacts'), \
             mock.patch.object(r.cmp, 'RECORD', 'B5-RELEASE-RECORD.json'):
            report = r.cmp.run(self.root, self.fixture.recompute_path, window_index=self.fixture.index_path)
        self.assertIn('fill:gamma/contrasts/*/floor/arm_gates/*/floor_gate_j', report['coverage']['unmapped'])
        self.fixture.comparison_path.write_bytes(r.canonical(report))
        with self.assertRaises(r.RendererRefusal):
            self.fixture.load()

    def test_nonfinite_duplicate_keys_and_symlinks_refuse(self):
        for raw in (b'{"a":1,"a":2}', b'{"a":NaN}', b'{"a":Infinity}', b'{"a":1e999}'):
            with self.subTest(raw=raw), self.assertRaises(r.RendererRefusal):
                r.loads(raw)
        path = self.fixture.artifacts / self.fixture.fill_name
        path.unlink()
        path.symlink_to(self.root / 'recompute.json')
        with self.assertRaisesRegex(r.RendererRefusal, 'input_unreadable_or_symlink'):
            self.fixture.load()

    def test_write_failure_leaves_no_partial_candidate(self):
        destination = self.root / 'failed-candidate'
        with mock.patch.object(r.os, 'rename', side_effect=OSError('synthetic failure')):
            with self.assertRaises(OSError):
                r.publish(destination, {'Results.md': b'synthetic'})
        self.assertFalse(destination.exists())
        self.assertFalse(list(self.root.glob('.b5-results-*')))

    def test_missing_or_extra_disclosure_leaf_and_row_refuse(self):
        original = deepcopy(self.fixture.files)
        for action in ('extra', 'missing_value', 'drop_row', 'duplicate_row'):
            self.fixture.files = deepcopy(original)
            lines = self.fixture.files[self.fixture.disclosure_name]['contrasts']
            if action == 'extra':
                lines[0]['unregistered'] = 9
            elif action == 'missing_value':
                lines[0]['estimator'].pop('estimate')
            elif action == 'drop_row':
                lines.pop(0)
            else:
                lines.append(deepcopy(lines[0]))
            self.fixture.write()
            with self.subTest(action=action), self.assertRaises(r.RendererRefusal):
                self.fixture.load()

    def test_refused_floor_and_not_estimable_nulls_remain_visible(self):
        # Real engine estimator/evaluator/finalizer + the real fill adapter,
        # independently exercised here without changing the comparator fixture.
        from tests.test_results_fill_adapter import produced_verdict, campaigns
        from joulewise.analysis_engine.artifact import render_claim_verdicts
        from joulewise.results_fill_adapter import adapt_claim_verdicts
        for outcome in ('not_resolvable', 'not_estimable', 'unresolved', 'direction_supported', 'equivalent'):
            verdict = produced_verdict(outcome)
            fill = adapt_claim_verdicts(render_claim_verdicts(verdict), campaigns=campaigns())
            row = fill['gamma']['contrasts'][0]
            self.assertEqual(row['claim_evaluation']['outcome'], outcome)
            self.assertEqual(r.cell(row['claim_evaluation']['outcome']), outcome)
            table, details = r.contrast_sections(fill['gamma']['contrasts'])
            self.assertIn('| ctr-test | ' + outcome + ' |', table)
            self.assertIn(outcome, details)
            if outcome == 'not_estimable':
                self.assertIn('not available (null)', table)
                for key in ('estimate', 'interval', 'decision_interval'):
                    self.assertEqual(r.cell(row[key]), 'not available (null)')

        from joulewise.analysis_engine.artifact import finalize_claim_verdicts
        from joulewise.analysis_engine.claims import evaluate_claim
        verdict = produced_verdict('not_resolvable')
        row = verdict['contrasts'][0]
        row['floor']['resolutions'][0].update(status='refused', floor_abs_j=None, floor_cmp_j=None,
                                              floor_gate_j=None, reason_codes=['consumer_term_unknown'])
        row['floor'].update(status='refused', transport_verdict='refused', floor_abs_j=None,
                            floor_cmp_j=None, active_floor_j=None)
        row['claim_evaluation'] = evaluate_claim(estimate=row['estimator']['estimate'],
            metrology_aware_ci95=row['estimator']['metrology_aware_CI95'],
            decision_interval=row['deterministic_bounds']['decision_interval'], floor_gate_j=None,
            adjusted_rejected=row['multiplicity']['rejected'], hypothesized_direction=row['hypothesized_direction'],
            equivalence=row['equivalence'])
        verdict = finalize_claim_verdicts(verdict)
        fill = adapt_claim_verdicts(render_claim_verdicts(verdict), campaigns=campaigns())
        table, details = r.contrast_sections(fill['gamma']['contrasts'])
        self.assertIn('| ctr-test | not_resolvable |', table)
        self.assertIn('not available (null)', table)
        self.assertIn('/floor/active_floor_j | not available (null)', details)


if __name__ == '__main__':
    unittest.main()
