"""Source safety, deterministic fresh outputs, and matching-seal stop checks."""
import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from scripts import bytes_thermal_lines as t
from tests.test_bytes_thermal_lines import RecordedFaultTests
from tests.b6.test_bytes_p2_thermal_window import thermal_journal
f=RecordedFaultTests();f.setUp()
try:
 def snap():return {str(p):p.read_bytes() for p in f.archive.rglob('*') if p.is_file()}
 original=snap()
 for case in ('existing','symlink','dangling','inside'):
  dest=f.root/case
  if case=='existing':dest.mkdir()
  if case=='symlink':dest.symlink_to(f.archive,target_is_directory=True)
  if case=='dangling':dest.symlink_to(f.root/'absent',target_is_directory=True)
  if case=='inside':dest=f.archive/'new'
  try:t.transform('request-end-p1',f.archive,dest)
  except ValueError as exc:print('REFUSED',case,str(exc),'source_unchanged',snap()==original)
  else:raise AssertionError(case)
 a,b=f.root/'fresh-a',f.root/'fresh-b'
 ra=t.transform('request-end-p1',f.archive,a);rb=t.transform('request-end-p1',f.archive,b)
 assert (a/'view_manifest.json').read_bytes()==(b/'view_manifest.json').read_bytes()
 assert json.dumps(ra['changes'])==json.dumps(rb['changes'])
 print('FRESH_MANIFEST_AND_CHANGES_BYTE_IDENTICAL',True)
 # Guard directory links, including dangling links, below a fresh root before write_copy.
 for dangling in (False,True):
  o=f.root/('guard-'+str(dangling));o.mkdir();(o/'nested').symlink_to(f.root/'nonexistent' if dangling else f.archive,target_is_directory=True)
  try:t.write_copy(o/'nested/file','opaque',o,[f.archive])
  except ValueError as exc:print('GUARD_REFUSED',dangling,str(exc).split(':')[0],snap()==original)
  else:raise AssertionError('guard')
 thermal_journal(range(0,126,5),{60}).dump(f.journal)
 f.put('derived/b6-acceptance.json',{'session_id':'s','excluding':[]})
 for seal in ('mismatched','missing','matched'):
  flags=f.archive/'derived/window_flags.json'
  if seal=='missing':flags.unlink()
  else:f.put('derived/window_flags.json',{'hazards':{'thermal':{'continuous':{'journal':{'sha256':hashlib.sha256(f.journal.read_bytes()).hexdigest() if seal=='matched' else '0'*64}}}}})
  o=f.root/seal
  try:r=t.transform('request-end-p1',f.archive,o)
  except ValueError as exc:
   assert seal=='matched' and not o.exists();print('WOULD_ADD',seal,'STOP_BEFORE_WRITE',str(exc))
  else:
   assert seal!='matched' and not r['changes'];print('WOULD_ADD',seal,r['status'])
finally:f.doCleanups()
