"""Print lines of a committed blob that carry a timing-like token next to a held-out
session/model mention, with every digit masked to '#'. Structure only."""
import re, subprocess, sys
TOK = re.compile(r'\b(?:r[12]-)?(?:bytes-)?s[2-6]-p[12]\b|70[bB]|30B-A3B|80B|122B|14B|32B|8B-8bit|llama', re.I)
TIME = re.compile(r'\d\s*(?:s|ms|µs|min|h)\b|\d{1,2}:\d{2}|decode|duration|span|elapsed|timestamp|_utc|wall', re.I)
spec = sys.argv[1]
text = subprocess.run(['git', 'show', spec], capture_output=True, check=True).stdout.decode('utf-8', 'replace')
n = 0
for i, line in enumerate(text.splitlines(), 1):
    if TOK.search(line) and TIME.search(line):
        n += 1
        if n <= int(sys.argv[2] if len(sys.argv) > 2 else 12):
            print(f'{i}: ' + re.sub(r'\d', '#', line)[:260])
print(f'-- {n} lines with a held-out token and a timing-like token')
