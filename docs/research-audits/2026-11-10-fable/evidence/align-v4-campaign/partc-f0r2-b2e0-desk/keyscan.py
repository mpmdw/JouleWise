"""Structural key scan: prints only key names (never values). Usage: keyscan.py FILE..."""
import json, re, sys
PAT = re.compile(r"energy|power|joule|watt|slot|transcript", re.I)
MW = re.compile(r"mW|_mw\b|^mw$|_mw_", re.I)
def walk(o, keys):
    if isinstance(o, dict):
        for k, v in o.items():
            keys.add(k); walk(v, keys)
    elif isinstance(o, list):
        for v in o: walk(v, keys)
for p in sys.argv[1:]:
    keys = set()
    try:
        txt = open(p).read()
        try:
            walk(json.loads(txt), keys)
        except json.JSONDecodeError:
            for line in txt.splitlines():
                if line.strip(): walk(json.loads(line), keys)
    except Exception as e:
        print(p, "ERR", type(e).__name__); continue
    hits = sorted(k for k in keys if PAT.search(k) or MW.search(k))
    print(p, "nkeys=%d" % len(keys), "HITS=" + repr(hits))
