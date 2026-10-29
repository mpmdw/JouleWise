"""Losslessly compact generated synthetic artefacts after all executions finish."""
from pathlib import Path
import gzip,shutil,tarfile
R=Path(__file__).resolve().parent
for root in (R/'e2e-positive',R/'e2e-literal'):
 for d in list(root.iterdir()):
  if d.is_dir():
   target=d.with_suffix('.tar.gz')
   with tarfile.open(target,'w:gz') as f:f.add(d,arcname=d.name)
   shutil.rmtree(d)
for f in list(R.rglob('*.json')):
 if f.name in ('input_A_knee_found.json','compact.json'):continue
 if f.stat().st_size>200_000:
  with f.open('rb') as src,gzip.open(str(f)+'.gz','wb') as dst:shutil.copyfileobj(src,dst)
  f.unlink()
for f in R.glob('independent-current*.json'):f.unlink()
