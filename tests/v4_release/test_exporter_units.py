"""Exporter contract units (scripts/export_v4_series.py). Synthetic only; no custody is read."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from scripts import export_v4_series as ex  # noqa: E402


class ContractDigestTests(unittest.TestCase):
    def test_identity_sha256_is_the_registered_canonicalization(self):
        rows = [{'turn': 0, 'generation': {'prompt_token_ids': [1, 2, 3], 'output_token_ids': [4, 5]}},
                {'turn': 1, 'generation': {'prompt_token_ids': [1, 2, 3, 4, 5, 6], 'output_token_ids': [7]}}]
        # Hand-computed: [[p0, o0], [p1, o1]] compact ASCII JSON, no trailing newline.
        text = b'[[[1,2,3],[4,5]],[[1,2,3,4,5,6],[7]]]'
        self.assertEqual(ex.identity_sha256(rows), hashlib.sha256(text).hexdigest())

    def test_identity_is_unavailable_when_a_turn_lacks_its_ids(self):
        rows = [{'turn': 0, 'generation': {'prompt_token_ids': [1], 'output_token_ids': None}}]
        self.assertIsNone(ex.identity_sha256(rows))

    def test_identity_depends_on_turn_order_and_boundaries(self):
        a = [{'generation': {'prompt_token_ids': [1], 'output_token_ids': [2, 3]}}]
        b = [{'generation': {'prompt_token_ids': [1, 2], 'output_token_ids': [3]}}]
        self.assertNotEqual(ex.identity_sha256(a), ex.identity_sha256(b))

    def test_registered_span_is_the_wp22_rule(self):
        ep = {'start_ns': 100, 'end_ns': 900, 'hardware': {'thermal': {'intervals': [
            {'kind': 'G1', 'start_ns': 300}, {'kind': 'G0', 'start_ns': 40}, {'kind': 'G0', 'start_ns': 60}]}}}
        self.assertEqual(ex.registered_span_ns(ep), [40, 900])
        ep['hardware']['thermal']['intervals'] = [{'kind': 'G1', 'start_ns': 300}]
        self.assertEqual(ex.registered_span_ns(ep), [100, 900])
        ep['hardware'] = {}
        self.assertEqual(ex.registered_span_ns(ep), [100, 900])

    def test_cohort_digest_is_canonical(self):
        identity = {'model_source': 's', 'model_revision': 'r', 'runtime_sha256': 'a' * 64,
                    'execution_policy_sha256': 'b' * 64}
        configuration = {'max_turns': 12, 'deadman_s': 1.5, 'max_tokens': 4, 'max_episode_decode_tokens': None}
        text = json.dumps({'configuration': configuration, 'identity': identity}, sort_keys=True,
                          separators=(',', ':')).encode()
        self.assertEqual(ex.cohort_sha256(identity, configuration), hashlib.sha256(text).hexdigest())


class PlanCustodyTests(unittest.TestCase):
    SERIES = {'schema_version': 'joulewise.align_v4.series_window.v1', 'plan_id': 'align-v4-c3', 'window_id': 'C3',
              'series_manifest_sha256': ex.ALLOCATION_SHA256, 'members': []}

    def refused(self, *args):
        with self.assertRaises(ex.Refused) as caught:
            ex.plan_owner_check(*args)
        return caught.exception.code

    def test_own_window_plan_passes(self):
        ex.plan_owner_check(dict(self.SERIES), 'C3', 'C3#2')
        ex.plan_owner_check({'schema_version': 'joulewise.align_v4.v1', 'plan_id': 'align-v4', 'members': []},
                            'W1', 'W1#1')

    def test_a_sibling_or_foreign_plan_refuses_wrong_window(self):
        wrong = 'config_digest_not_planned:wrong_window'
        self.assertEqual(self.refused(dict(self.SERIES), 'C4', 'C4#1'), wrong)
        self.assertEqual(self.refused(dict(self.SERIES, series_manifest_sha256='0' * 64), 'C3', 'C3#1'), wrong)
        self.assertEqual(self.refused(dict(self.SERIES, attempt_id='C3#1'), 'C3', 'C3#2'), wrong)
        self.assertEqual(self.refused({'members': []}, 'C3', 'C3#1'), wrong)
        self.assertEqual(self.refused(dict(self.SERIES), 'W1', 'W1#1'), wrong)

    def test_an_invalid_kit_is_not_an_exporter_refusal(self):
        # A digest-verified kit that is not a JSON object, or fails normalization, is the builds' config_invalid.
        self.assertIsNone(ex.writer_config_bytes(b'[1, 2]'))
        self.assertIsNone(ex.writer_config_bytes(b'{"run_id": 3}'))
        self.assertIsNone(ex.writer_config_bytes(b'not json'))

    def test_writer_bytes_are_the_bundle_writers(self):
        from joulewise.schemas import BenchmarkConfig
        kit = (REPO / 'configs/campaigns/align_v4/stages/episodes-a/align-v4-episodes-a-e05.json').read_bytes()
        expected = (json.dumps(BenchmarkConfig.from_mapping(json.loads(kit)).to_dict(), indent=2, sort_keys=True)
                    + '\n').encode()
        self.assertEqual(ex.writer_config_bytes(kit), expected)


class ConfigTests(unittest.TestCase):
    def config(self, **changes):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        value = {'schema': ex.CONFIG_SCHEMA, 'export_root': tmp.name + '/e', 'records_repo': tmp.name,
                 'kit_root': tmp.name,
                 'engine_route': 'raw_source',
                 'windows': [{'attempt_id': 'W1#1', 'record_commit': 'a' * 40, 'record_path': 'r.json'}]}
        value.update(changes)
        path = Path(tmp.name) / 'c.json'
        path.write_text(json.dumps(value))
        return path

    def refused(self, path):
        with self.assertRaises(ex.Refused) as caught:
            ex.load_config(path)
        return caught.exception.code

    def test_valid_config_loads(self):
        self.assertEqual(ex.load_config(self.config())['windows'][0]['attempt_id'], 'W1#1')

    def test_unknown_config_key_refuses(self):
        self.assertEqual(self.refused(self.config(extra=1)), 'unknown_contract_key')

    def test_thermal_source_route_refuses(self):
        # Lead ruling 4 (2026-11-08): the release path exports through raw_source only.
        self.assertEqual(self.refused(self.config(engine_route='thermal_source')), 'thermal_source_refused')

    def test_bad_attempt_ids_refuse(self):
        for bad in ('C3', 'C15#1', 'T4#1', 'W1#0', 'C3#2#1'):
            with self.subTest(attempt=bad):
                windows = [{'attempt_id': bad, 'record_commit': 'a' * 40, 'record_path': 'r.json'}]
                self.assertEqual(self.refused(self.config(windows=windows)), 'config_invalid')

    def test_duplicate_attempt_refuses(self):
        row = {'attempt_id': 'C1#1', 'record_commit': 'a' * 40, 'record_path': 'r.json'}
        self.assertEqual(self.refused(self.config(windows=[row, dict(row)])), 'config_invalid')


class CliTests(unittest.TestCase):
    def test_refusal_prints_structure_only_and_exits_2(self):
        import contextlib
        import io
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'c.json'
            path.write_text(json.dumps({'schema': ex.CONFIG_SCHEMA, 'surprise': True}))
            with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()):
                code = ex.main(['export', '--config', str(path), '--all'])
        self.assertEqual(code, 2)
        self.assertEqual(json.loads(out.getvalue()), {'status': 'refused', 'code': 'unknown_contract_key'})


if __name__ == '__main__':
    unittest.main()
