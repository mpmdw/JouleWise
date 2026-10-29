"""L9-PATHTOKEN-1: number-like archive inventory names in the structure-only census.

Synthetic archives only. Real harvest archives hold source files whose names
carry git short hashes or versions (82622e70, 21e2, 2.1.260) that _FLOAT_TOKEN
reads as numbers; step 0 and the run-record validator must admit exactly those
authenticated inventory entries and nothing else.
"""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from joulewise.b5_analysis import dry_run as d
from joulewise.b5_analysis.windows import AnalysisRefusal, SealPins

TRACES = 'night-custody/results-clone/docs/process_traces/x/'
COMMON = (TRACES+'replay-branch-82622e70-summary.txt', TRACES+'21e2-delta2-final-head-opus.md',
          TRACES+'claude-help-2.1.260.txt')
GAMMA_ONLY = TRACES+'gamma-only-4158e658.md'


def _hash(raw): return hashlib.sha256(raw).hexdigest()


def _inject(testcase, archive_root, names):
    """Add listed inventory files; restore the shared cached archive afterwards."""
    sums = Path(archive_root)/'sources/SHA256SUMS'
    original = sums.read_bytes()
    added = []
    def restore():
        for path in added: path.unlink()
        sums.write_bytes(original)
    testcase.addCleanup(restore)
    lines = original
    for name in names:
        path = Path(archive_root)/'sources'/name
        path.parent.mkdir(parents=True, exist_ok=True)
        raw = ('synthetic inventory file '+Path(name).name+'\n').encode()
        path.write_bytes(raw); added.append(path)
        lines += (_hash(raw)+'  '+name+'\n').encode()
    sums.write_bytes(lines)


class CensusPathTokenTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from tests.b5_analysis import fixtures as fx
        from tests.b5_analysis import fixtures_s3 as s3
        from tests.b5_analysis import fixtures_s3b as sb
        cls.fx = fx
        cls.built = {pack: (sb.cached(pack.upper()+'_STD') if pack == 'beta' else s3.cached(pack.upper()+'_STD'))
                     for pack in d.PACKS}
        cls.pins = SealPins.load()
        cls.tmp = tempfile.TemporaryDirectory(prefix='l9-census-path-'); cls.addClassCleanup(cls.tmp.cleanup)
        cls.root = Path(cls.tmp.name)
        rows = [built.entry_data for built in cls.built.values()]
        beta = next(row for row in rows if row['pack'] == 'beta')
        rows = [{**beta, 'attempt': n, 'entry_kind': 'no_archive', 'archive_root': None, 'harvest_record_sha256': None,
                 'verdict': 'NO_COLLECTION', 'claim_usable': False, 'record_citation': 'synthetic-history.md:1'}
                for n in range(1, beta['attempt'])]+rows
        cls.index_path = cls.root/'index.json'
        cls.index_path.write_bytes(d._canonical({'schema': 'joulewise.b5_window_index.v1', 'attempts': rows}))
        cls.serial = 0

    def setUp(self):
        for pack, built in self.built.items():
            _inject(self, built.entry_data['archive_root'], COMMON+((GAMMA_ONLY,) if pack == 'gamma' else ()))

    def state(self):
        type(self).serial += 1
        restricted = self.root/str(self.serial)/'restricted'; restricted.mkdir(parents=True)
        return d.RunState('blind-dry-run', self.index_path, restricted, 'b'*40, pack_table=self.fx.PACK_TABLE)

    def record(self, s, records):
        steps = list(records)
        if all(r.status == 'ok' for r in steps):
            # A later registered tooling stop keeps the record's step order closed.
            steps.append(s.record('1', exit_status=2, code='analysis_arguments_invalid'))
        done = {r.step for r in steps}
        steps += [d.StepRecord(step, None, 'not_run') for step in d.STEP_IDS if step not in done]
        attempts, windows, census = d._record_parts(s)
        sealed = {key: s.pins.sealed[{'flag_catalog_sha256': 'catalog_sha256'}.get(key, key)] for key in d.SEAL_KEYS}
        return d.build_dry_run_record(mode='blind-dry-run', analysis_commit=s.commit, window_index_sha256=s.index.sha256,
            sealed=sealed, attempts=attempts, windows=windows, input_census=census, steps=steps)

    def valid_record(self):
        s = self.state(); records = d.step_0(s, d.StepRunner(s.restricted))
        self.assertEqual(records[0].status, 'ok', records[0])
        record = self.record(s, records)
        d.validate_dry_run_record(record, index=s.index, kept_units=s.kept)
        return s, record

    def test_P1_step0_admits_authenticated_inventory_names_with_number_like_tokens(self):
        # At b13a510dc: tooling_refusal reader_record_not_structure_only.
        s = self.state(); records = d.step_0(s, d.StepRunner(s.restricted))
        self.assertEqual(records[0].status, 'ok', records[0])
        for pack in d.PACKS:
            paths = {row['path'] for row in s.read('census_'+pack)}
            self.assertTrue({'sources/'+name for name in COMMON} <= paths)
            self.assertEqual('sources/'+GAMMA_ONLY in paths, pack == 'gamma')
        self.assertTrue(any(d._FLOAT_TOKEN.search(name) for name in COMMON+(GAMMA_ONLY,)))

    def test_P1_run_record_validates_inventory_census_paths(self):
        # At b13a510dc the attempt-A shaped record refuses dry_run_record_invalid.
        s = self.state(); records = d.step_0(s, d.StepRunner(s.restricted))
        record = self.record(s, records)
        d.validate_dry_run_record(record, index=s.index, kept_units=s.kept)
        self.assertTrue({('gamma', 'sources/'+GAMMA_ONLY)} <= {(r['window'], r['path']) for r in record['input_census']})

    def assert_invalid(self, s, record):
        with self.assertRaisesRegex(AnalysisRefusal, '^dry_run_record_invalid$'):
            d.validate_dry_run_record(record, index=s.index, kept_units=s.kept)

    def test_P2_validator_keeps_the_guard_outside_the_exact_window_inventory(self):
        s, record = self.valid_record()
        sums = next(r for r in record['input_census'] if r['window'] == 'gamma' and r['path'] == 'sources/SHA256SUMS')
        cases = {
            'unlisted source name': lambda r: r['input_census'].append(
                {'window': 'gamma', 'path': 'sources/'+TRACES+'unlisted-9.9.txt', 'sha256': 'a'*64, 'check': 'sources_sha256sums'}),
            'another window\'s inventory name': lambda r: r['input_census'].append(
                {'window': 'alpha', 'path': 'sources/'+GAMMA_ONLY, 'sha256': 'a'*64, 'check': 'sources_sha256sums'}),
            'history-prefixed name': lambda r: r['input_census'].append(
                {'window': 'gamma', 'path': 'sources/attempts/p/sources/'+COMMON[0], 'sha256': 'a'*64, 'check': 'input_census'}),
            'listing digest not the recorded one': lambda r: r['input_census'][r['input_census'].index(sums)].update(sha256='0'*64),
            'release difference path': lambda r: r.update(release_difference={'path': 'sources/'+COMMON[0]}),
        }
        for label, mutate in cases.items():
            with self.subTest(label):
                changed = json.loads(json.dumps(record)); mutate(changed)
                self.assert_invalid(s, changed)

    def test_P2_validator_requires_the_index_pinned_harvest(self):
        s, record = self.valid_record()
        gamma = next(e for e in s.index.entries if e.pack == 'gamma')
        harvest = gamma.archive_root/'harvest.json'; original = harvest.read_bytes()
        self.addCleanup(harvest.write_bytes, original)
        harvest.write_bytes(original+b' ')
        self.assert_invalid(s, record)

    def test_P2_writer_exempts_only_exact_census_paths(self):
        s = self.state()
        inventory = frozenset({'sources/'+COMMON[0]})
        row = {'path': 'sources/'+COMMON[0], 'sha256': 'a'*64, 'check': 'sources_sha256sums'}
        refused = (
            ('census_gamma', [{**row, 'path': 'sources/1e-100.json'}], None),
            ('census_gamma', [{**row, 'check': '1.5'}], None),
            ('census_gamma', [{**row, 'note': row['path']}], None),
            ('census_gamma', {'path': row['path']}, None),
            ('census_gamma', None, d._canonical([row])),
            ('attempt_gamma', [row], None),
            ('kept_gamma', [row], None),
        )
        for role, value, raw in refused:
            with self.subTest(role=role, value=value, raw=raw is not None), \
                    self.assertRaisesRegex(AnalysisRefusal, '^reader_record_not_structure_only$'):
                s.write(role, 'supply-census/test.json', value, raw=raw, inventory=inventory)
        self.assertEqual(s.outputs, {})
        with self.assertRaisesRegex(AnalysisRefusal, '^reader_record_not_structure_only$'):
            s.write('census_gamma', 'supply-census/test.json', [row])
        s.write('census_gamma', 'supply-census/test.json', [row], inventory=inventory)
        self.assertEqual(s.read('census_gamma'), [row])

    def test_P2_inventory_is_empty_unless_harvest_and_listing_authenticate(self):
        gamma = self.built['gamma'].entry_data
        root = Path(gamma['archive_root'])
        harvest = _hash((root/'harvest.json').read_bytes()); sums = _hash((root/'sources/SHA256SUMS').read_bytes())
        roots = {'claim_runs_root': gamma['claim_runs_root'], 'custody_root': gamma['custody_root']}
        inventory = d.archive_inventory(root, harvest, sums, **roots)
        self.assertIn('sources/'+GAMMA_ONLY, inventory)
        self.assertIn('derived/exclusions.json', inventory)
        self.assertTrue(any(p.startswith('original/claim-runs/') for p in inventory))
        self.assertEqual(d.archive_inventory(root, '0'*64, sums, **roots), frozenset())
        self.assertEqual(d.archive_inventory(root, harvest, '0'*64, **roots), frozenset())


if __name__ == '__main__':
    unittest.main()
