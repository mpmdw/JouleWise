"""Every RC-CMP-4 real-shape numeric leaf path (rc-cmp6-fable-rev/rc-cmp-4-paths.txt, 324 paths) through the
RC-CMP-7 line gate's table: its line word must be registered for its section and its key for its word."""
import importlib.util, re, sys
spec = importlib.util.spec_from_file_location("cmp", sys.argv[1]); cmp = importlib.util.module_from_spec(spec); spec.loader.exec_module(cmp)
bad, words, n = [], set(), 0
for line in open(sys.argv[2]):
    p = line.strip(); n += 1
    m = re.fullmatch(r"disclosure:(cells|floors|contrasts|fixed_sentences|block_lines|window_lines/[a-z]+)/([a-z0-9_]+)/([A-Za-z0-9_.]+)(/.*)?", p)
    if not m:
        continue
    sec, word, key = m.group(1).split("/")[0], m.group(2), m.group(3)
    words.add((sec, word))
    if word not in cmp.LINE_KEYS[sec]:
        bad.append(("word", p))
    elif key not in cmp.LINE_KEYS[sec][word] and key not in cmp.LINE_COMMON:
        bad.append(("key", p))
print(f"{n} paths; {len(words)} (section, line word) pairs:", sorted(words))
print("violations:", bad)
