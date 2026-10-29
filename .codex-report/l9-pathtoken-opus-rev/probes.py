"""L9-PATHTOKEN-OPUS-REV adversarial probes (synthetic archives only).

Run from the repo root:
  JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 .codex-report/l9-pathtoken-opus-rev/probes.py -v
"""
import json, os, sys, unittest
from pathlib import Path
sys.path.insert(0, os.getcwd())
from joulewise.b5_analysis import dry_run as d
from tests.b5_analysis import test_census_path_token as t

ROW = {'sha256': 'a'*64, 'check': 'sources_sha256sums'}


class Probes(t.CensusPathTokenTests):
    # Inherit fixtures only; do not re-run the seat's tests here.
    for _n in [n for n in dir(t.CensusPathTokenTests) if n.startswith('test_')]:
        locals()[_n] = None

    def test_A_appended_value_after_inventory_prefix_refused(self):
        s, record = self.valid_record()
        base = 'sources/'+t.COMMON[0]
        for path in (base+'/0.731', base+'.0.731', base+'-0.731', 'sources/'+t.TRACES+'0.731', base[:-4]+'-0.731.txt'):
            with self.subTest(validator=path):
                changed = json.loads(json.dumps(record))
                changed['input_census'].append({'window': 'gamma', 'path': path, **ROW})
                self.assert_invalid(s, changed)
            with self.subTest(writer=path), self.assertRaisesRegex(d.AnalysisRefusal, '^reader_record_not_structure_only$'):
                s.write('census_gamma', 'supply-census/p.json', [{'path': path, **ROW}], inventory=frozenset({base}))

    def test_B_listing_is_trusted_from_disk_not_from_the_index_pin(self):
        # A listing edited on disk (consistent bytes) before step 0 admits an
        # arbitrary number-like name end to end: harvest.json is unchanged and
        # still index-pinned, but nothing pins sources/SHA256SUMS.
        gamma = self.built['gamma'].entry_data['archive_root']
        t._inject(self, gamma, ('planted/value-0.7310.txt',))
        s, record = self.valid_record()
        census = {r['path'] for r in s.read('census_gamma')}
        self.assertIn('sources/planted/value-0.7310.txt', census)
        self.assertIn(('gamma', 'sources/planted/value-0.7310.txt'),
                      {(r['window'], r['path']) for r in record['input_census']})

    def test_C_listing_changed_after_write_fails_closed(self):
        s, record = self.valid_record()
        gamma = self.built['gamma'].entry_data['archive_root']
        t._inject(self, gamma, ('later-1.2.3.txt',))
        self.assert_invalid(s, record)

    def test_D_symlinked_listing_same_bytes_is_not_a_separate_bypass(self):
        gamma = Path(self.built['gamma'].entry_data['archive_root'])
        sums = gamma/'sources/SHA256SUMS'; raw = sums.read_bytes()
        copy = self.root/'sums-copy'; copy.write_bytes(raw)
        sums.unlink(); sums.symlink_to(copy)
        self.addCleanup(lambda: (sums.unlink(), sums.write_bytes(raw)))
        # The archive reader refuses a symlinked listing before any census write.
        s = self.state(); records = d.step_0(s, d.StepRunner(s.restricted))
        self.assertEqual((records[0].status, records[0].refusal), ('tooling_refusal', 'archive_path_invalid'))
        self.assertNotIn('census_gamma', s.outputs)

    def test_E_no_index_no_exemption(self):
        s, record = self.valid_record()
        with self.assertRaisesRegex(d.AnalysisRefusal, '^dry_run_record_invalid$'):
            d.validate_dry_run_record(record, index=None, kept_units=s.kept)

    def test_F_write_and_validate_inventories_identical(self):
        s = self.state(); records = d.step_0(s, d.StepRunner(s.restricted))
        record = self.record(s, records)
        d.validate_dry_run_record(record, index=s.index, kept_units=s.kept)
        for pack, w in s.windows.items():
            census = {r.path: r.sha256 for r in s.archives[pack].census()}
            write_inv = d.archive_inventory(w.archive_root, w.harvest_record_sha256, census['sources/SHA256SUMS'],
                                            claim_runs_root=w.claim_runs_root, custody_root=w.custody_root)
            entry = next(e for e in s.index.entries if e.plan_id == w.plan_id and e.archive_root is not None)
            sums = next(r['sha256'] for r in record['input_census']
                        if r['window'] == pack and r['path'] == 'sources/SHA256SUMS')
            val_inv = d.archive_inventory(entry.archive_root, entry.harvest_record_sha256, sums,
                                          claim_runs_root=entry.claim_runs_root, custody_root=entry.custody_root)
            self.assertTrue(write_inv)
            self.assertEqual(write_inv, val_inv, pack)
            floaty = sorted(p.rsplit('/', 1)[-1] for p in write_inv if d._FLOAT_TOKEN.search(p))
            print(pack, 'inventory', len(write_inv), 'number-like', floaty)

if __name__ == '__main__':
    unittest.main()
