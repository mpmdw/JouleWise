"""W3-only positive fixture port. Adds exactly the command's pass identity."""
import json,runpy,sys
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
from scripts import bytes_thermal_lines as t
real=t.transform
def identified(mode,archive,output,export=None):
 p=Path(archive)/'sources/repo/plan_tree.json';p.parent.mkdir(parents=True,exist_ok=True)
 # Only positive fixtures; never use this wrapper for fault probes.
 data=json.loads(p.read_text()) if p.exists() else {}
 data['bytes_pass']=2 if mode=='hull-p2' else 1
 p.write_text(json.dumps(data))
 return real(mode,archive,output,export)
t.transform=identified
name=sys.argv[1];sys.argv=sys.argv[1:];runpy.run_path(name,run_name='__main__')
