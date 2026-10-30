"""Restore the exact full-size real-stream input preserved by this review."""
import gzip
from pathlib import Path
D=Path(__file__).parent
raw=gzip.open(D/'fixture-input.json.gz','rb').read()
p=D/'fixture/input_A_knee_found.json'
if p.exists():
    assert p.read_bytes()==raw, 'preserve an existing different fixture'
else:
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_bytes(raw)
print('verified/restored full fixture bytes',len(raw))
