"""Structure-only census: which committed files (origin refs, since a date) name a
BYTES session or model that carries held-out rows. Prints path, commit, date and hit
counts only; never prints file content."""
import re, subprocess, sys
since = sys.argv[1]
SESS = re.compile(rb'\b(?:r[12]-)?(?:bytes-)?s[2-6]-p[12]\b')
MODEL = re.compile(rb'Llama-3\.3-70B|Llama-70B|70B|30B-A3B|Next-80B|80B-A3B|122B|Qwen3-14B|Qwen3-32B|8B-8bit|\b14B\b|\b32B\b')
SKIP = ('docs/process_traces/night-results/', '.codex-report/logs/')
log = subprocess.run(['git', 'log', '--remotes=origin', f'--since={since}', '--no-merges',
                      '--raw', '--no-abbrev', '--format=C %H %cI'], capture_output=True, check=True).stdout
seen = {}
commit = date = None
for line in log.splitlines():
    if line.startswith(b'C '):
        _, commit, date = line.split(b' ', 2); continue
    if not line.startswith(b':'):
        continue
    meta, path = line.split(b'\t', 1)
    parts = meta.split()
    blob, status = parts[3], parts[4]
    if status.startswith(b'D') or set(blob) == {48}:
        continue
    p = path.decode()
    if p.startswith(SKIP):
        continue
    seen.setdefault((p, blob), (commit.decode()[:9], date.decode()))
items = list(seen.items())
proc = subprocess.Popen(['git', 'cat-file', '--batch'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
for (p, blob), (c, d) in items:
    proc.stdin.write(blob + b'\n'); proc.stdin.flush()
    header = proc.stdout.readline().split()
    size = int(header[2]); data = proc.stdout.read(size); proc.stdout.read(1)
    s, m = len(SESS.findall(data)), len(MODEL.findall(data))
    if s or m:
        print(f'{d}\t{c}\t{s}\t{m}\t{size}\t{p}')
