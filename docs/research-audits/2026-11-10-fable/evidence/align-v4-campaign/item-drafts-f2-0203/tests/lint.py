"""Syntax and binding checks for this draft package only."""
import ast
import hashlib
import json
from pathlib import Path
import re
import subprocess

HERE=Path(__file__).resolve().parents[1]
py=sh=embedded=0
for path in HERE.rglob('*.py'):
    ast.parse(path.read_text(),filename=str(path)); py+=1
for folder in ('f2-inst-02','f2-inst-03','hp-02'):
    for item in json.loads((HERE/folder/'items.json').read_text()):
        text=(HERE/folder/('ITEM-'+item['item']+'.md')).read_text()
        assert item['kit_sha'] in text and ','.join(item['legs']) in text
        blocks=re.findall(r'```sh\n(.*?)```',text,re.S)
        syntax='\n'.join(blocks)
        syntax=re.sub(r'ISSUED_EPOCH=<LEAD FILLS:[^\n]+','ISSUED_EPOCH=1',syntax)
        syntax=re.sub(r'WATCH_UNTIL_EPOCH=<LEAD FILLS:[^\n]+','WATCH_UNTIL_EPOCH=2',syntax)
        for shell in ('bash','zsh'):
            r=subprocess.run([shell,'-n'],input=syntax,text=True,capture_output=True)
            assert r.returncode==0,(folder,item['item'],shell,r.stderr); sh+=1
        for code in re.findall(r"<<'PY'\n(.*?)\nPY",syntax,re.S): ast.parse(code); embedded+=1
    assert not (HERE/folder/'queue-b.json').exists()
    assert 'queue-a.json' in {p.name for p in (HERE/folder).iterdir()}
print(py,'Python sources,',sh,'complete shell item syntax checks,',embedded,'embedded Python checks PASS')
