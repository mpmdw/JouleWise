import re, subprocess, sys
spec, nums = sys.argv[1], [int(x) for x in sys.argv[2].split(',')]
lines = subprocess.run(['git', 'show', spec], capture_output=True).stdout.decode('utf-8', 'replace').splitlines()
for n in nums:
    print(f'{n}: ' + re.sub(r'\d', '#', lines[n-1])[:230])
