"""Each individual sh block and joined blocks under bash/zsh; compile all Python heredocs."""
import ast
from pathlib import Path
import re
import subprocess
HERE=Path(__file__).resolve().parents[1]; checks=0; programs=0
for file in sorted([*HERE.glob('ITEM-*.md'),HERE/'STANDING-F0-r2.md']):
    blocks=re.findall(r'```sh\n(.*?)```',file.read_text(),re.S)
    for text in [*blocks,'\n'.join(blocks)]:
        text=re.sub(r'<LEAD FILLS:[^>]*>','0',text).replace('<token>','TOKEN')
        for shell in ('bash','zsh'):
            r=subprocess.run([shell,'-n'],input=text,text=True,capture_output=True)
            assert r.returncode==0,(file.name,shell,r.stderr); checks+=1
    for program in re.findall(r"<<'PY'\n(.*?)\nPY",'\n'.join(blocks),re.S):
        ast.parse(program,filename=file.name); programs+=1
    print('PASS',file.name,len(blocks),'sh blocks; Python heredocs compile')
for file in [HERE/'gates.sh',HERE/'tests/run_all_gates.sh']:
    text=re.sub(r'<LEAD FILLS:[^>]*>','0',file.read_text())
    for shell in ('bash','zsh'):
        r=subprocess.run([shell,'-n'],input=text,text=True,capture_output=True); assert r.returncode==0,(file,shell,r.stderr); checks+=1
for file in HERE.rglob('*.py'):
    if any(part.startswith('.pinned-') for part in file.parts): continue
    ast.parse(file.read_text(),filename=str(file)); programs+=1
print(checks,'shell syntax checks;',programs,'Python programs compiled; BAD 0')
