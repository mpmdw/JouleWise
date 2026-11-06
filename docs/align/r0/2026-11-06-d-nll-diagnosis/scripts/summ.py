import sys, json, re
for line in open(sys.argv[1]):
    m = re.match(r'\[\s*([\d.]+)s\] (\{"layer".*\}) (rss=.*)', line)
    if not m: continue
    r = json.loads(m.group(2)); s = r['s0']
    print(f"{r['layer']:2d} {r['type']:4s} rms={s['hf_rms']:<7}", ' '.join(f"{v}:" + '/'.join(f"{s[v][k]:.3f}" for k in ('0-40', '40-100', '100-900', '900-')) for v in ('mlx16', 'mlxD')),
          '| s900', r['s900']['mlx16']['900-'], r['s900']['mlxD']['900-'])
