"""Fable review probes for L9-PATHTOKEN-1 (synthetic fixtures only)."""
import json, os, sys, tempfile, shutil
from pathlib import Path
sys.path.insert(0, '/home/user/JouleWise')
os.chdir('/home/user/JouleWise')
from joulewise.b5_analysis import dry_run as d
from joulewise.b5_analysis.windows import AnalysisRefusal
from tests.b5_analysis import test_census_path_token as T
import unittest

class Probe(T.CensusPathTokenTests):
    def refusal(self, fn):
        try: fn()
        except AnalysisRefusal as e: return e.code
        return 'NO_REFUSAL'
    def test_fable_probes(self):
        s, record = self.valid_record()
        base = 'sources/'+T.COMMON[0]
        inv = {'sources/'+n for n in T.COMMON}
        out = {}
        # (a) writer: inventory prefix + appended value / value inside
        for label, p in (('prefix+appended', base+'/1.5'), ('prefix-suffix', base+'-1.5'), ('prefix+e', base+'1e5'),
                         ('trailing-slash', base+'/'), ('leading-dot', './'+base), ('case', base.upper())):
            row = {'path': p, 'sha256': 'a'*64, 'check': 'sources_sha256sums'}
            out['writer '+label] = self.refusal(lambda: s.write('census_gamma', 'supply-census/x'+label.replace('+','')+'.json', [row], inventory=frozenset(inv)))
            changed = json.loads(json.dumps(record)); changed['input_census'].append({'window': 'gamma', **row})
            out['validator '+label] = self.refusal(lambda: d.validate_dry_run_record(changed, index=s.index, kept_units=s.kept))
        # (b) validator: symlinked listing with an extra number-like name (digest differs) and identical bytes (digest same)
        gamma = next(e for e in s.index.entries if e.pack == 'gamma')
        sums = gamma.archive_root/'sources/SHA256SUMS'; original = sums.read_bytes()
        outside = Path(tempfile.mkdtemp(prefix='l9-fable-outside-'))/'SHA256SUMS'
        self.addCleanup(lambda: (sums.unlink() if sums.is_symlink() else None, sums.write_bytes(original), shutil.rmtree(outside.parent)))
        outside.write_bytes(original+('b'*64+'  '+T.TRACES+'planted-3.14.txt\n').encode())
        sums.unlink(); sums.symlink_to(outside)
        changed = json.loads(json.dumps(record))
        out['validator symlinked listing, extra name, legit record'] = self.refusal(lambda: d.validate_dry_run_record(changed, index=s.index, kept_units=s.kept))
        changed['input_census'].append({'window': 'gamma', 'path': 'sources/'+T.TRACES+'planted-3.14.txt', 'sha256': 'b'*64, 'check': 'sources_sha256sums'})
        out['validator symlinked listing, planted name'] = self.refusal(lambda: d.validate_dry_run_record(changed, index=s.index, kept_units=s.kept))
        # write-time: step 0 with the symlinked listing (outside the archive)
        s2 = self.state(); rec = d.step_0(s2, d.StepRunner(s2.restricted))
        out['step0 with listing symlinked outside archive'] = (rec[0].status, rec[0].refusal)
        sums.unlink(); sums.write_bytes(original)
        # (c) inventory computed from a wrong-window harvest digest / claim roots swapped
        alpha = next(e for e in s.index.entries if e.pack == 'alpha')
        out['inventory(gamma root, alpha harvest digest)'] = len(d.archive_inventory(gamma.archive_root, alpha.harvest_record_sha256,
            next(r['sha256'] for r in record['input_census'] if r['window']=='gamma' and r['path']=='sources/SHA256SUMS'),
            claim_runs_root=gamma.claim_runs_root, custody_root=gamma.custody_root))
        # (d) offline validator: no index / tracked index (archives absent here)
        out['validator index=None (tracked index, roots absent)'] = self.refusal(lambda: d.validate_dry_run_record(record))
        # (e) number-like name in a step output name and in release_difference.output
        changed = json.loads(json.dumps(record))
        changed['steps'][0]['outputs'].append({'name': 'supply-census/'+Path(base).name, 'sha256': 'a'*64})
        out['validator step output named like inventory file'] = self.refusal(lambda: d.validate_dry_run_record(changed, index=s.index, kept_units=s.kept))
        # (f) write-time and validation-time inventories identical
        from joulewise.b5_analysis import dry_run
        w = {pack: dry_run.archive_inventory(win.archive_root, win.harvest_record_sha256,
                {r.path: r.sha256 for r in s.archives[pack].census()}.get('sources/SHA256SUMS'),
                claim_runs_root=win.claim_runs_root, custody_root=win.custody_root) for pack, win in s.windows.items()}
        v = {e.pack: dry_run.archive_inventory(e.archive_root, e.harvest_record_sha256,
                next(r['sha256'] for r in record['input_census'] if r['window']==e.pack and r['path']=='sources/SHA256SUMS'),
                claim_runs_root=e.claim_runs_root, custody_root=e.custody_root)
             for e in s.index.entries if e.archive_root is not None and any(x['plan_id']==e.plan_id for x in record['windows'])}
        out['write/validate inventories identical'] = (w == v, {k: len(x) for k, x in w.items()})
        # (g) every census path in the record that carries a float token is in its window inventory
        hits = [(r['window'], r['path']) for r in record['input_census'] if d._FLOAT_TOKEN.search(r['path'])]
        out['float-like census rows all in own inventory'] = (len(hits), all(p in v[wn] for wn, p in hits))
        for k, val in out.items(): print(f'{k}: {val}')

if __name__ == '__main__':
    unittest.main(argv=['x', 'Probe.test_fable_probes'], verbosity=1)
