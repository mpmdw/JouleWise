import sys, json, copy
from pathlib import Path
sys.path.insert(0,'/tmp/jw')
from joulewise import bytes_analysis as ba
root = Path(sys.argv[1]); work = root/'bytes-s2-p1-fit'
from tests.test_bytes_analysis import archive_campaign
# rebuild manifest cheaply from the session sidecars is not possible; reuse design
design = ba.read_json(Path('/tmp/jw/tests/fixtures/bytes/campaign_design.json'))
from joulewise.b6 import blinding
for m in design['models']:
    m['config_key'] = blinding.configuration_key({"model": {"name": m["model"]}, "workload_profile": {"name": "bytes-synthetic", "output_tokens": 512}})
man = {"synthetic": True, "models": design["models"], "sessions": [{"session_id": "bytes-s2-p1", "pass_id": 1, "archive": str(work/'archive'), "released_key_dir": str((root/'released-keys/bytes/blinding').resolve()), "test7_passed": False}]}
for label, src in (("source", work/'one-export'), ("line", work/'line-blinded/export')):
    recs = ba.load_records(src, man, stage="blinded", stage1_commit="a"*40)
    cells = ba.reduce_models(recs, man, boundaries=("rails",))
    print(label, sorted((c['model'], c['status'], c.get('n_b')) for c in cells if c['model'] in ('Qwen3-30B-A3B-4bit','Qwen3-8B-4bit')), 'records', len(recs))
