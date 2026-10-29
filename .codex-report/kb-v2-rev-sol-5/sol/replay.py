import os,subprocess,sys
from pathlib import Path
P=Path(__file__).resolve().parent;R=Path('/workspace/JouleWise')
commands=[['scripts/repin.py','--check'],['scripts/bytes_mac_kit.py','--check'],[str(P/'sol3/ci_diagnose.py')],[str(P/'sol3/scan_e2e.py')],[str(P/'sol3/read_cases.py'),str(P/'e2e/input_A_knee_found.json')],[str(P/'sol3/consult/verify_round4.py')]]
for n in ('knee_noise_diag','scan_cases','knee_fix_check','dram_noise','tick_quant'):
 commands.append([str(P/'sol3/adapted'/f'{n}.py'),str(R)])
commands.append([str(P/'sol3/original/refusals.py'),str(R),str(P/'e2e')])
for i,args in enumerate(commands):
 with (P/f'replay-{i:02}.log').open('w') as f:
  c=subprocess.run([sys.executable,'-B',*args],cwd=R,stdout=f,stderr=subprocess.STDOUT)
 print(i,c.returncode,args,flush=True)
