#!/usr/bin/env python3.13
"""RC-CMP7-OPUS-REV probes at c372211bf (synthetic fixtures only; nothing in production edited).

Run from the repo root:
  TMPDIR=/tmp/rcopus7_tmp PYTHONPATH=. JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 \
    python3.13 .codex-report/rc-cmp7-opus-rev/probe_cmp7.py [g7|words|relabel|keys|all]
"""
import copy
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT)]
os.environ.setdefault("JW_B5_SYNTHETIC_ONLY", "1")
from tests.independent_recompute import test_comparator as tc  # noqa: E402
from tests.independent_recompute import test_input_gate as g  # noqa: E402
from tests.independent_recompute import test_rc_cmp7 as t7  # noqa: E402

cmp, DISC, CODED, SHA = g.cmp, g.DISCLOSURE, g.CODED, tc.SHA
KEPT = {p: f"kept-units/{SHA}-{p}.json" for p in ("alpha", "beta", "gamma")}
FILL = f"outputs/{SHA}-results-fill-input.json"


def case():
    c = g.GateCase("run")
    c.setUp()
    return c


def run(c):
    try:
        code, err, out = c.exit_code(CODED)
    except cmp.Refusal as exc:
        return 2, f"Refusal({exc})", {}
    return code, err.strip(), out


def show(label, c):
    code, err, out = run(c)
    fails = c.fails(out) if "counts" in out else None
    print(f"{label}: exit={code} err={err!r} fails={fails}", flush=True)
    return code, out


def g7():
    print("## G7: run_phase_energy_j universe from L9's kept-units record")
    show("A0 control", case())
    c = case(); c.files[KEPT["alpha"]] = tc.kept_units_record("alpha", [])
    show("A1 L9 drops run-a from kept-units (rereduced file kept; recompute selects)", c)
    c = case(); c.files[KEPT["alpha"]] = tc.kept_units_record("alpha", []); c.files.pop("rereduced/alpha/run-a.rereduced.json")
    show("A2 L9 drops run-a from kept-units and does not re-reduce it (recompute selects)", c)
    c = case(); c.files[KEPT["alpha"]] = tc.kept_units_record("alpha", []); c.files.pop("rereduced/alpha/run-a.rereduced.json")
    c.files[KEPT["alpha"]]["exclusions_sha256"] = "9" * 64
    show("A3 as A2 plus L9 states other exclusions (recompute unchanged)", c)
    c = case(); c.files[KEPT["alpha"]] = tc.kept_units_record("alpha", []); c.files.pop("rereduced/alpha/run-a.rereduced.json")
    c.ours["members"]["ALPHA"]["run-a"]["selected"] = False
    show("A4 shared: both sides drop run-a (recompute unselected), same exclusions hash", c)
    c = case(); c.files[KEPT["alpha"]] = tc.kept_units_record("alpha", []); c.files.pop("rereduced/alpha/run-a.rereduced.json")
    c.ours["members"]["ALPHA"]["run-a"]["selected"] = False
    c.files[KEPT["alpha"]]["exclusions_sha256"] = "9" * 64; c.ours["inputs"]["ALPHA"]["exclusions_sha256"] = "9" * 64
    show("A5 shared: as A4 with both sides on one other exclusions file", c)
    c.ours["exclusions_rederivation"]["ALPHA"]["status"] = "disagrees"
    show("A5b as A5 with the recompute's re-derivation disagreeing with that file", c)
    c = case(); c.files[KEPT["alpha"]] = tc.kept_units_record("alpha", ["run-a", "run-z"])
    show("A6 L9 adds run-z (no rereduced file, recompute lacks it)", c)
    c = case(); c.files[KEPT["alpha"]] = tc.kept_units_record("alpha", ["run-a", "run-z"])
    c.files["rereduced/alpha/run-z.rereduced.json"] = {"phase_energy_j": {"prefill": 1.0, "decode": 1.0}, "gross_energy_j": 2.0}
    show("A7 L9 adds and re-reduces run-z", c)
    c = case(); c.files[KEPT["alpha"]] = tc.kept_units_record("alpha", []); c.files[KEPT["beta"]] = tc.kept_units_record("beta", ["run-a"])
    show("A8 run-a moved to beta's kept-units record", c)
    c = case(); c.files[KEPT["alpha"]]["cells"][tc.ALPHA_CELLS["absolute"]]["kept"]["repeat"][0]["run_ids"] = "run-a"
    show("A9 run_ids a bare string (characters become ids)", c)
    c = case(); c.files[f"kept-units/{'f' * 64}-alpha.json"] = tc.kept_units_record("alpha", [])
    show("A10 a second alpha kept-units record", c)
    c = case(); c.files.pop(KEPT["gamma"]); c.ours["inputs"]["GAMMA"].pop("exclusions_sha256")
    show("A11 gamma: no kept-units record and no recompute hash (both absent)", c)
    c = case(); c.files[KEPT["alpha"]] = tc.kept_units_record("alpha", ["run-a", "neg8-window-start-spare-2"])
    show("A12 a registered spare reference in kept-units", c)
    c = case(); rid = "d117fq31p7-df-ph-decode-abs-r01"
    c.ours["members"]["ALPHA"][rid] = {"selected": True, "role": "reference", "E_j": {"prefill": 1.0, "decode": 1.0, "request": 1.0}}
    show("A13 a registered science run that the recompute labels role=reference, selected, L9 lacks", c)
    c = case(); c.ours["members"]["ALPHA"]["neg8-window-midpoint"] = {"selected": True, "E_j": {"prefill": 9.0, "decode": 9.0, "request": 9.0}}
    c.files["rereduced/alpha/neg8-window-midpoint.rereduced.json"] = {"phase_energy_j": {"prefill": 1.0, "decode": 1.0}, "gross_energy_j": 2.0}
    c.files[KEPT["alpha"]] = tc.kept_units_record("alpha", ["run-a"])
    show("A14 reference re-reduced by L9 (not kept) with other values, recompute selects it", c)


def words():
    print("\n## every exempt string/boolean leaf of the step-11 outputs, mutated alone")
    base = case()
    t7.with_neg8(base); t7.with_references(base)
    code, err, out = run(base)
    print("base (with NEG-8 lines):", code, repr(err))
    leaves = out["coverage"]["leaves"]
    reasons = {}
    for path, reason in leaves.items():
        reasons.setdefault(reason, []).append(path)

    def walk(node, ptr):
        if isinstance(node, dict):
            for k, v in node.items():
                yield from walk(v, ptr + (k,))
        elif isinstance(node, list):
            for i, v in enumerate(node):
                yield from walk(v, ptr + (i,))
        else:
            yield ptr, node
    hits = []
    for name in (FILL, DISC):
        for ptr, value in list(walk(base.files[name], ())):
            if not isinstance(value, (str, bool)) or ptr[-1] in ("text", "label", "line"):
                continue
            c = case(); t7.with_neg8(c); t7.with_references(c)
            node = c.files[name]
            for k in ptr[:-1]:
                node = node[k]
            new = (not value) if isinstance(value, bool) else ("computed" if value != "computed" else "refused")
            node[ptr[-1]] = new
            code, err, o = run(c)
            if code == 0:
                hits.append((name.split("/")[0], "/".join(map(str, ptr)), value, new))
    print("exit-0 mutations:", len(hits))
    for h in hits:
        print("   ", h)
    return hits


def relabel():
    print("\n## relabel sweep (probe_cmp6 relabel, all sections incl. window_lines and cells)")
    base = case(); t7.with_neg8(base)
    record = base.files[DISC]
    words = sorted({w for table in cmp.LINE_KEYS.values() for w in table})
    secs = [(s, None) for s in ("cells", "floors", "contrasts", "block_lines", "fixed_sentences")] + \
           [("window_lines", p) for p in record["window_lines"]]
    exits, total = [], 0
    for sec, pack in secs:
        rows = record[sec] if pack is None else record["window_lines"][pack]
        for index, row in enumerate(rows):
            for word in words:
                if word == row["line"]:
                    continue
                c = case(); t7.with_neg8(c)
                rec = c.files[DISC]
                item = (rec[sec] if pack is None else rec["window_lines"][pack])[index]
                item["line"] = item["label"] = word
                total += 1
                if run(c)[0] == 0:
                    exits.append((sec, pack, row["line"], word))
    print(f"relabels tried: {total}; exit 0: {len(exits)}")
    for e in exits:
        print("   ", e)


def keys():
    print("\n## key-set and duplicate-line variants")
    def edit(label, fn):
        c = case(); t7.with_neg8(c)
        fn(c.files[DISC]); show(label, c)

    def find(rec, word):
        for lines in [rec[s] for s in ("cells", "floors", "contrasts", "block_lines", "fixed_sentences")] + list(rec["window_lines"].values()):
            for i, r in enumerate(lines):
                if r["line"] == word:
                    return lines, i
    def dup(word, **change):
        def fn(rec):
            lines, i = find(rec, word)
            extra = copy.deepcopy(lines[i]); extra.update(change); lines.append(extra)
        return fn
    edit("K1 duplicate dominance_branch with branch A appended", dup("dominance_branch", branch="A"))
    edit("K2 duplicate dominance_branch with licensed True", dup("dominance_branch", dominance_sentence_licensed=True))
    edit("K3 duplicate below_screen_bound with below True", dup("below_screen_bound", below=True))
    edit("K4 duplicate sensitivity_window with widened flipped", lambda rec: dup("sensitivity_window", widened=not find(rec, "sensitivity_window")[0][find(rec, "sensitivity_window")[1]]["widened"])(rec))
    def strip(word, *drop):
        def fn(rec):
            lines, i = find(rec, word)
            for k in drop:
                lines[i].pop(k, None)
        return fn
    edit("K5 dominance_branch without branch (licensed only)", strip("dominance_branch", "branch"))
    edit("K6 dominance_branch without licensed", strip("dominance_branch", "dominance_sentence_licensed"))
    edit("K7 below_screen_bound without below", strip("below_screen_bound", "below"))
    edit("K8 sensitivity_window without widened", strip("sensitivity_window", "widened"))
    edit("K9 neg8_screen line removed from alpha", lambda rec: rec["window_lines"]["alpha"].__setitem__(
        slice(None), [r for r in rec["window_lines"]["alpha"] if r["line"] != "neg8_screen"]))
    def move_window(rec):
        a = rec["window_lines"]["alpha"]; b = rec["window_lines"]["beta"]
        ia = [i for i, r in enumerate(a) if r["line"] == "below_screen_bound"]
        ib = [i for i, r in enumerate(b) if r["line"] == "below_screen_bound"]
        if ia and ib:
            a[ia[0]], b[ib[0]] = b[ib[0]], a[ia[0]]
    edit("K10 below_screen_bound lines swapped alpha<->beta", move_window)
    def into_block(rec):
        lines, i = find(rec, "below_screen_bound"); item = lines.pop(i); item["below"] = not item["below"]
        rec["block_lines"].append(item)
    edit("K11 wrong below_screen_bound moved into block_lines", into_block)
    def nested(rec):
        lines, i = find(rec, "dominance_branch"); lines[i]["branch"] = {"value": "A"}
    edit("K12 branch nested in an object", nested)


def claims():
    print("\n## claim words in the fill, one at a time (ceiling compared; these not)")
    def fill_edit(label, fn):
        c = case(); fn(c.files[FILL]); show(label, c)
    def contrast(fill):
        return fill["gamma"]["contrasts"][0]
    c0 = case(); print("   fixture ceiling/ready:", contrast(c0.files[FILL])["claim_evaluation"].get("claim_level_ceiling"),
                       contrast(c0.files[FILL])["claim_evaluation"].get("claim_ready_for_l2_l3"))
    fill_edit("C1 claim_ready_for_l2_l3 True (ceiling stays L1)",
              lambda f: contrast(f)["claim_evaluation"].update(claim_ready_for_l2_l3=True))
    fill_edit("C2 claim_level_ceiling L2 (control: compared)",
              lambda f: contrast(f)["claim_evaluation"].update(claim_level_ceiling="L2"))
    fill_edit("C3 campaigns/alpha/claim_usable False", lambda f: f["campaigns"]["alpha"].update(claim_usable=False))
    c = case(); c.ours["inputs"]["ALPHA"]["claim_usable"] = False
    c.ours.setdefault("flags", []).append({"code": "claim_usable_false", "pack": "ALPHA", "scope": "window"})
    show("C3b recompute: ALPHA claim_usable False (+ its claim_usable_false flag); fill prints True", c)
    fill_edit("C4 hypothesized_direction negative", lambda f: contrast(f).update(hypothesized_direction="negative"))
    fill_edit("C5 reason_codes [] (floor_not_cleared dropped)", lambda f: contrast(f)["claim_evaluation"].update(reason_codes=[]))
    fill_edit("C6 loo/status computed with no rows", lambda f: contrast(f)["loo"].update(status="computed"))


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    for name, fn in (("g7", g7), ("claims", claims), ("keys", keys), ("relabel", relabel), ("words", words)):
        if which in (name, "all"):
            fn()
