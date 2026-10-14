"""Step-11 probes reading the JoinedRunTests cache; never rerun the driver."""
import unittest

from tests.b5_analysis.joined_s10 import cached_primary


class JoinedProbeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture, cls.harness, cls.result = cached_primary()
        cls.addClassCleanup(cls.harness.remove_repository)

    def test_load_correlated_restored_units_pass_real_tripwire_and_validator(self):
        from joulewise.b5_analysis.disclosures import LOAD_CODES
        from joulewise.b5_analysis.kept_units import require_kept_members_in_verdict
        from joulewise import whole_window as ww
        from joulewise.cli import validate_bundle

        state = self.result.state
        self.assertEqual(self.result.code, 0, self.result.stderr)
        self.assertTrue(state.read('sensitivity')['reported_cells'])
        member = self.fixture.windows['beta'].restorable
        self.assertIsNotNone(member, 'BETA must name the load-only removed member')
        primary = state.kept['beta']
        removed = [(cid, unit) for cid, cell in primary.cells.items() for unit in cell.dropped
                   if member in unit.run_ids]
        self.assertTrue(removed, 'BETA restorable member is absent from dropped units')
        self.assertTrue(all(unit.codes and set(unit.codes) <= LOAD_CODES for _, unit in removed))
        self.assertEqual(validate_bundle(self.fixture.windows['beta'].claim/member, strict=True), [])
        observed = [item for item in self.result.restored_contexts
                    if item['view'].window.pack == 'beta'
                    and any(member in item['view'].kept_run_ids(cid) for cid, _ in removed)]
        self.assertTrue(observed, 'real disclosure builder never restored the BETA member')
        for item in observed:
            view = item['view']
            self.assertEqual(view.sensitivity_label, 'load-correlated')
            self.assertTrue(any(trip['view'] is view for trip in self.result.tripwires),
                            'restored view never passed the real kept-member tripwire')
            require_kept_members_in_verdict(view, item['row']['bundle_ids'])
            ids = {run for cid in view.cells for run in view.kept_run_ids(cid)}
            session = ww.AuthenticatedConsumptionSession(view.window.claim_runs_root, ids,
                mode='read_replay', evaluation_basis_sha256=item['row']['evaluation_basis']['sha256'],
                consumption_semantics_id=ww.MAX_BRACKET_CONSUMPTION_SEMANTICS_ID,
                archive_context=item['context'])
            self.assertTrue(session.ready, session.refusal_reasons)
            validation = ww.validate_whole_window_verdict_row(item['row'], view.window.claim_runs_root,
                ids, consumption_session=session, archive_context=item['context'])
            self.assertTrue(validation.admitted, validation.reasons)
        lines = [row for row in state.read('disclosure_record')['cells']
                 if row['line'] == 'load_correlated_cell' and row['pack'] == 'beta']
        self.assertTrue(lines)
        self.assertTrue(any(sum(row['restored_counts'].values()) > 0 for row in lines))
        self.assertTrue(any(row['values'].get('status') == 'computed' for row in lines))

    def test_disclosure_main_read_only_driver_output_paths_without_builder_seam(self):
        from scripts import produce_b5_disclosures as disclosures
        state = self.result.state
        calls = [call for call in self.result.calls if call['main'] is disclosures.main]
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0]['step'], '11')
        self.assertEqual(calls[0]['result'].exit_status, 0)
        self.assertEqual(len(self.result.disclosure_reads), 1)
        self.assertEqual(len(self.result.disclosure_builds), 1,
                         'real input builder did not return')
        read = self.result.disclosure_reads[0]
        built = self.result.disclosure_builds[0]
        self.assertEqual(read['custody'], state.restricted)
        self.assertEqual(read['registry'], state.output('step_outputs'))
        self.assertEqual(set(read['paths']), set(disclosures.ROLES))
        self.assertEqual(built['index'], state.index_path)
        self.assertEqual(built['paths'], read['paths'])
        for role, path in read['paths'].items():
            with self.subTest(role=role):
                self.assertEqual(path, state.output(role))
                self.assertTrue(path.is_relative_to(state.restricted))
                self.assertTrue(any(output['name'] == state.outputs[role]['name']
                    and output['sha256'] == state.outputs[role]['sha256']
                    for row in self.result.record['steps'] for output in row['outputs']))


if __name__ == '__main__':
    unittest.main()
