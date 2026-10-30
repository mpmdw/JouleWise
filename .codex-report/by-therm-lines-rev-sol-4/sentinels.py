"""Run the prior guarded sentinel probe with W3 identity only, not its fault probes."""
import json,runpy,tempfile
from pathlib import Path
p=Path(__file__).parent
ns=runpy.run_path(str(p/'prior_sol/probes_delta.py'),run_name='sentinel_probe')
t=ns['t'];real=t.transform
def identified(mode,archive,output,export=None):
 q=Path(archive)/'sources/repo/plan_tree.json';q.parent.mkdir(parents=True,exist_ok=True)
 q.write_text(json.dumps({'bytes_pass':2 if mode=='hull-p2' else 1}))
 return real(mode,archive,output,export)
t.transform=identified
with tempfile.TemporaryDirectory() as tmp:ns['blinding'](Path(tmp))
