"""Count, per committed blob, lines that look like a per-request duration: a decode/
prefill/request/member word and a number with a seconds unit on the same line, or a
'dec s'/'decode_s'/'duration' column. Prints counts and masked line numbers only."""
import re, subprocess, sys
WORD = re.compile(r'decode|prefill|request|member|dec s|decode_s|duration|tok/s|tokens/s|per token', re.I)
SECS = re.compile(r'\d(?:\.\d+)?\s*(?:s|ms|µs)\b|decode_s|dec s|tok/s|tokens/s')
HELD = re.compile(r'\b(?:r[12]-)?(?:bytes-)?s[2-6]-p[12]\b|70[bB]|llama|30B-A3B|80B|122B|14B|32B|8B-8bit', re.I)
for spec in sys.argv[1:]:
    text = subprocess.run(['git', 'show', spec], capture_output=True).stdout.decode('utf-8', 'replace')
    lines = text.splitlines(); held = bool(HELD.search(text))
    hits = [i for i, l in enumerate(lines, 1) if WORD.search(l) and SECS.search(l)]
    if hits and held:
        print(f'{len(hits)}\t{spec}\t' + ','.join(map(str, hits[:12])))
