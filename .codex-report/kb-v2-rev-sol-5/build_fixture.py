import sys, runpy, math, json
from pathlib import Path
R=Path(__file__).resolve().parent
source=R/'sol/sol3/adapted/e2e.py'
sys.path.insert(0,str(source.parent))
sys.argv=[str(source),'/workspace/JouleWise',str(R/'e2e-positive')]
s=source.read_text().replace('vals = [(-1)**i for i in range(n)]',"vals = [(63 if i%64 == 0 else -1) if kind in ('rails','gpu','meter') else (-1)**i for i in range(n)]")
exec(compile(s,str(source),'exec'),{'__name__':'__main__','__file__':str(source)})
