"""Run old synthetic probes with explicit fixture journal seals, per U2.
Never used for the fault matrix or original-script replays.
"""
import hashlib,json,runpy,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from scripts import bytes_thermal_lines as t
real=t.transform
def sealed(mode,archive,output,export=None):
 archive=Path(archive); journal=archive/'sources/night-custody/hazards/monitor/thermal.jsonl'
 if mode=='request-end-p1' and journal.is_file():
  flags=archive/'derived/window_flags.json'
  flags.parent.mkdir(parents=True,exist_ok=True)
  flags.write_text(json.dumps({'hazards':{'thermal':{'continuous':{'journal':{'sha256':hashlib.sha256(journal.read_bytes()).hexdigest()}}}}}))
 return real(mode,archive,output,export)
t.transform=sealed
name=sys.argv[1];sys.argv=sys.argv[1:]
runpy.run_path(str(Path(__file__).parent/name),run_name='__main__')
