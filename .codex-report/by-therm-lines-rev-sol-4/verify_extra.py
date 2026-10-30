"""Real CLI verifier damage and source safety checks."""
import copy,json,subprocess,sys,tempfile,shutil,hashlib
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
from scripts import bytes_thermal_lines as t
from tests.test_bytes_thermal_lines import RecordedFaultTests

def cli(*args):return subprocess.run([sys.executable,t.__file__,*map(str,args)],capture_output=True,text=True)
def digest(a):return {str(p.relative_to(a)):hashlib.sha256(p.read_bytes()).hexdigest() for p in a.rglob('*') if p.is_file()}
for name,value in [('notices-int',[1]),('notices-code-int',[{'code':1}]),('source-list',[]),('source-value-int',{'x':1}),('binding-null',None),('binding-missing',None)]:
 f=RecordedFaultTests();f.setUp()
 try:
  o=f.root/'o';p=cli('request-end-p1',f.archive,o);assert p.returncode==0
  path=o/'thermal_line.json';r=json.loads(path.read_text())
  if name.startswith('notices'):r['notices']=value
  elif name.startswith('source'):r['source_sha256']=value
  elif name=='binding-missing':r.pop('view_manifest_sha256')
  else:r['view_manifest_sha256']=value
  path.chmod(0o644);path.write_text(json.dumps(r));p=cli('verify',o);r=json.loads(path.read_text())
  print('DAMAGE',name,p.returncode,r.get('records.thermal_view_changed'),'thermal_line.json' in r.get('view_differing_paths',[]),flush=True)
 finally:f.doCleanups()
f=RecordedFaultTests();f.setUp()
try:
 o=f.root/'o';assert cli('request-end-p1',f.archive,o).returncode==0
 link=f.root/'link';link.symlink_to(o,target_is_directory=True)
 p=cli('verify',link);print('SYMLINK',p.returncode,p.stdout.strip())
 missing=f.root/'missing';p=cli('verify',missing);print('MISSING',p.returncode,p.stdout.strip(),missing.exists())
 # Real output copied into recorded source, with symlinks left intact.
 inside=f.archive/'view';shutil.copytree(o,inside,symlinks=True)
 before=digest(f.archive);p=cli('verify',inside);print('INSIDE_SOURCE',p.returncode,'records.thermal_view_changed' in p.stdout,'UNCHANGED',before==digest(f.archive))
 # Combined damaged-control plus inside-source case.
 path=inside/'thermal_line.json';r=json.loads(path.read_text());r['source_sha256']=[];path.chmod(0o644);path.write_text(json.dumps(r))
 before=digest(f.archive);p=cli('verify',inside);print('INSIDE_SOURCE_DAMAGED_ROOTS',p.returncode,'UNCHANGED',before==digest(f.archive),'TAIL',p.stdout.splitlines()[-1:])
finally:f.doCleanups()
