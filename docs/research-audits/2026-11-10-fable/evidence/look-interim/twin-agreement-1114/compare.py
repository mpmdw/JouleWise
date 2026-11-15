#!/usr/bin/env python3
"""Twin agreement comparator per RL-166c section 4.2. Usage: compare.py [set ...]"""
import json, math, re, sys, os
BASE = os.path.dirname(os.path.abspath(__file__))
SETS = ["exact","exact-c","few_hot_days","no_heat","noisy","onset_not_estimable","baseline","constant_start","single_cell_onsets"]

def flat(x, p=""):
    if isinstance(x, dict):
        if not x: yield p + "/{}", {}
        for k, v in x.items(): yield from flat(v, p + "/" + k)
    elif isinstance(x, list):
        if not x: yield p + "/[]", []
        for i, v in enumerate(x): yield from flat(v, p + f"/{i}")
    else: yield p, x

SKIP = re.compile(r"(^|/)(model_sha256|code_sha256|stage1_sha256|input_sha256|numpy_version|roster_sha256)(/|$)|_sha256$")
CENS = [re.compile(p) for p in (r"^/onset/coefficients/", r"^/onset/sigma_s$", r"^/onset/tau_hat_s$", r"^/onset/lodo/", r"^/onset/count_only_cut/offset_s$")]
ENERGY = re.compile(r"^/channels/([^/]+)/(coefficients/([^/]+)|fold_coefficients/[^/]+/([^/]+))$")
COV = re.compile(r"^/channels/([^/]+)/covariance/(\d+)/(\d+)$")
ISNUM = lambda v: isinstance(v, (int, float)) and not isinstance(v, bool)

def compare_level(a, b, ctx_a=None):
    """Returns list of (path, a, b, cls, note)."""
    fa, fb = dict(flat(a)), dict(flat(b))
    fails = []
    for p in sorted(set(fa) | set(fb)):
        if SKIP.search(p): continue
        if p not in fa or p not in fb:
            fails.append((p, fa.get(p, "<absent>"), fb.get(p, "<absent>"), "keyset", "")); continue
        x, y = fa[p], fb[p]
        cls, tol_ok = "exact", None
        if ISNUM(x) and ISNUM(y) and not (isinstance(x, int) and isinstance(y, int)):
            if any(c.search(p) for c in CENS):
                cls = "censored"; ok = abs(x - y) <= 1e-6 * max(abs(x), abs(y)) + 1e-10
            elif ctx_a and (m := ENERGY.match(p)):
                cls = "energy"; ch = m.group(1); col = m.group(3) or m.group(4)
                cols = ctx_a["channels"][ch]["columns"]; cov = ctx_a["channels"][ch]["covariance"]
                se = math.sqrt(max(cov[cols.index(col)][cols.index(col)], 0)) if col in cols else 0.0
                ok = abs(x - y) <= 1e-8 * (abs(x) + se) if True else None
                if not ok: pass
            elif ctx_a and (m := COV.match(p)):
                cls = "cov"; ch = m.group(1); i, j = int(m.group(2)), int(m.group(3))
                cov = ctx_a["channels"][ch]["covariance"]
                ok = abs(x - y) <= 1e-6 * math.sqrt(abs(cov[i][i] * cov[j][j]))
            else:
                cls = "float"; ok = abs(x - y) <= 1e-8 * max(abs(x), abs(y)) + 1e-10
            if not ok: fails.append((p, x, y, cls, f"|d|={abs(x-y):.3e}"))
        else:
            if type(x) is not type(y) and not (ISNUM(x) and ISNUM(y)):
                fails.append((p, x, y, "exact", "type")); continue
            if x != y: fails.append((p, x, y, "exact", ""))
    return fails

def run_set(s):
    d = os.path.join(BASE, s); res = {}
    for lvl in ("D", "O"):
        A = os.path.join(d, "analyst", lvl + ".json"); S = os.path.join(d, "sol", lvl + ".json")
        ea, es = os.path.exists(A), os.path.exists(S)
        if not (ea and es):
            res[lvl] = [("<file>", "present" if ea else "REFUSED/absent", "present" if es else "REFUSED/absent", "refusal", "")]; continue
        a, b = json.load(open(A)), json.load(open(S))
        res[lvl] = compare_level(a, b, a if lvl == "O" else None)
    return res

if __name__ == "__main__":
    sets = sys.argv[1:] or SETS
    out = {}
    for s in sets:
        r = run_set(s); out[s] = r
        n = sum(len(v) for v in r.values())
        print(f"{s:22s} {'PASS' if n == 0 else 'FAIL'}  D:{len(r['D'])} O:{len(r['O'])}")
        for lvl, fl in r.items():
            for f in fl[:60]: print(f"   [{lvl}] {f[3]:9s} {f[0]}  analyst={f[1]!r}  sol={f[2]!r} {f[4]}")
            if len(fl) > 60: print(f"   [{lvl}] ... {len(fl)-60} more")
    json.dump(out, open(os.path.join(BASE, "compare_result.json"), "w"), indent=1, default=str)
