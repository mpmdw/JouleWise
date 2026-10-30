#!/usr/bin/env python3.13
"""RC-CMP8-OPUS-REV probes at 0d317afd4 (re-run at f9f86869e by RC-CMP9-OPUS-REV; joint() path split fixed for keys containing "/") (synthetic fixtures only; nothing in production edited).

Base: the round's fullest producer-shaped window (with_neg8 + with_references + with_sensitivity(widened)).
  drop     every list element and every dict key of every L9 output, removed alone
  ours     every list element / dict key of the recompute output, removed alone
  joint    each L9-only drop whose only failure is a routing_id row, re-run with the recompute's
           item for the same routing key removed too (pairs over two output-derived sides)
  relabel  every identity-like string leaf of L9's outputs replaced by each other value of the same key
Run from repo root:
  TMPDIR=/tmp/rcopus_eight_tmp PYTHONPATH=. JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 \
    python3.13 .codex-report/rc-cmp8-opus-rev/probe_cmp8.py [drop|ours|joint|relabel|widened]
"""
import copy
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT)]
os.environ.setdefault("JW_B5_SYNTHETIC_ONLY", "1")
from tests.independent_recompute import test_input_gate as g  # noqa: E402
from tests.independent_recompute import test_rc_cmp7 as t7  # noqa: E402
from tests.independent_recompute import test_rc_cmp8 as t8  # noqa: E402

cmp = g.cmp


def case(widened=True):
    c = g.GateCase("run")
    c.setUp()
    t7.with_neg8(c); t7.with_references(c); t8.with_sensitivity(c, widened)
    return c


def run(c):
    try:
        code, err, out = c.exit_code(g.CODED)
    except cmp.Refusal as exc:
        return 2, f"Refusal({exc})", {}
    return code, err.strip(), out


def fails(out):
    return [(r["family"], r["key"], r["l9"], r["recompute"]) for r in out.get("comparisons", []) if r["verdict"] != "AGREE"]


def nodes(node, ptr=()):
    """Every removable position: (ptr to container, key/index)."""
    if isinstance(node, dict):
        for k in list(node):
            yield ptr, k
            yield from nodes(node[k], ptr + (k,))
    elif isinstance(node, list):
        for i in range(len(node)):
            yield ptr, i
            yield from nodes(node[i], ptr + (i,))


def at(root, ptr):
    for k in ptr:
        root = root[k]
    return root


def split(root, text):
    """A printed drop path back to keys; a key may itself contain '/' (the recompute's model/phase keys)."""
    parts, ptr = text.split("/"), []
    while parts:
        for n in range(len(parts), 0, -1):
            key = "/".join(parts[:n])
            node = at(root, ptr)
            if isinstance(node, dict) and key in node:
                ptr.append(key); del parts[:n]; break
            if isinstance(node, list) and n == 1 and key.isdigit():
                ptr.append(int(key)); del parts[:1]; break
        else:
            raise KeyError(text)
    return ptr


def short(name):
    return name.replace("0" * 64, "<sha>").replace("1" * 64, "<sens>")


def drop():
    base = case()
    print("base:", run(base)[:2])
    zero = []
    total = 0
    for name in sorted(base.files):
        for ptr, k in list(nodes(base.files[name])):
            c = case()
            del at(c.files[name], ptr)[k]
            code, err, out = run(c)
            total += 1
            where = short(name) + ":" + "/".join(map(str, ptr + (k,)))
            if code == 0:
                zero.append(where)
            yield where, code, err, fails(out)
    print(f"L9 drops tried: {total}; exit 0: {len(zero)}")
    for z in zero:
        print("   EXIT0", z)


def ours_drop():
    base = case()
    zero, total = [], 0
    for ptr, k in list(nodes(base.ours)):
        c = case()
        del at(c.ours, ptr)[k]
        code, err, out = run(c)
        total += 1
        where = "ours:" + "/".join(map(str, ptr + (k,)))
        if code == 0:
            zero.append(where)
        yield where, code, err, fails(out)
    print(f"recompute drops tried: {total}; exit 0: {len(zero)}")
    for z in zero:
        print("   EXIT0", z)


def joint():
    """Pairs whose both sides are outputs: drop L9's item, then also the recompute's item under the same routing key."""
    l9 = {}
    for where, code, err, f in drop():
        keys = [r[1] for r in f if r[0] == "routing_id" and r[2] is None and r[3] is not None]
        if code == 1 and keys and all(r[0] == "routing_id" for r in f) is False or (code == 1 and keys):
            l9.setdefault(tuple(sorted(keys)), []).append(where)
    ours = {}
    for where, code, err, f in ours_drop():
        keys = [r[1] for r in f if r[0] == "routing_id" and r[3] is None and r[2] is not None]
        if code == 1 and keys:
            ours.setdefault(tuple(sorted(keys)), []).append(where)
    print("\n## joint drops (same routing key dropped on both sides)")
    tried = 0
    for keys, l9_wheres in sorted(l9.items()):
        if keys not in ours:
            continue
        for lw in l9_wheres[:1]:
            for ow in ours[keys][:1]:
                c = case()
                name, _, lp = lw.partition(":")
                name = name.replace("<sha>", "0" * 64).replace("<sens>", "1" * 64)
                lp = split(c.files[name], lp)
                op = split(c.ours, ow.partition(":")[2])
                del at(c.files[name], lp[:-1])[lp[-1]]
                del at(c.ours, op[:-1])[op[-1]]
                code, err, out = run(c)
                tried += 1
                print(f"   joint {keys} | {lw} + {ow}: exit={code} err={err!r} fails={len(fails(out))}")
    print("joint tried:", tried)


IDENT = ("cell_id", "contrast_id", "pack", "omitted_block_id", "block_id", "run_id", "arm_id",
         "condition_family_id", "model", "phase", "component", "numerator_field", "stratum", "line")


def relabel():
    base = case()
    values = {}
    for name, doc in base.files.items():
        for ptr, k in nodes(doc):
            v = at(doc, ptr)[k]
            if isinstance(k, str) and k in IDENT and isinstance(v, str):
                values.setdefault(k, set()).add(v)
            if isinstance(k, int) and ptr and ptr[-1] in ("source_cell_ids", "floor_source_cell_ids", "floor_row_ids",
                                                          "run_ids", "floor_cell_ids") and isinstance(v, str):
                values.setdefault(ptr[-1], set()).add(v)
    zero, total = [], 0
    for name in sorted(base.files):
        for ptr, k in list(nodes(base.files[name])):
            v = at(base.files[name], ptr)[k]
            field = k if isinstance(k, str) else (ptr[-1] if ptr else None)
            if not isinstance(v, str) or field not in values or (field == "line"):
                continue
            for other in sorted(values[field] - {v}):
                c = case()
                at(c.files[name], ptr)[k] = other
                code, err, out = run(c)
                total += 1
                if code == 0:
                    zero.append((short(name) + ":" + "/".join(map(str, ptr + (k,))), v, other))
    print(f"identity relabels tried: {total}; exit 0: {len(zero)}")
    for z in zero:
        print("   EXIT0", z)


if __name__ == "__main__":
    which = sys.argv[1]
    if which == "drop":
        for where, code, err, f in drop():
            print(f"{where}: exit={code} err={err!r} nfails={len(f)}")
    elif which == "ours":
        for where, code, err, f in ours_drop():
            print(f"{where}: exit={code} err={err!r} nfails={len(f)}")
    elif which == "joint":
        joint()
    elif which == "relabel":
        relabel()


def confirm():
    """Named drop/relabel cases behind the findings, on the widened and the unwidened base."""
    FILL = [k for k in case().files if k.endswith("-results-fill-input.json")][0]
    DISC = [k for k in case().files if k.startswith("disclosures/")][0]

    def line_drop(section, word, pack=None, index=0):
        def fn(c):
            rows = c.files[DISC][section] if pack is None else c.files[DISC][section][pack]
            hits = [i for i, r in enumerate(rows) if r["line"] == word]
            del rows[hits[index]]
        return fn

    def fill_contrast(c, i=0):
        return c.files[FILL]["gamma"]["contrasts"][i]

    cases = [
        ("FILL gamma/contrasts/0 (decode contrast) removed", lambda c: c.files[FILL]["gamma"]["contrasts"].pop(0)),
        ("FILL gamma/contrasts emptied", lambda c: c.files[FILL]["gamma"]["contrasts"].clear()),
        ("FILL gamma removed", lambda c: c.files[FILL].pop("gamma")),
        ("FILL contrast estimate removed", lambda c: fill_contrast(c).pop("estimate")),
        ("FILL contrast decision_interval removed", lambda c: fill_contrast(c).pop("decision_interval")),
        ("FILL contrast conditions/difference_orientation removed", lambda c: fill_contrast(c)["conditions"].pop("difference_orientation")),
        ("FILL contrast floor/claim_floor_rule removed", lambda c: fill_contrast(c)["floor"].pop("claim_floor_rule")),
        ("FILL contrast floor removed", lambda c: fill_contrast(c).pop("floor")),
        ("DISC primary_contrast line removed", line_drop("contrasts", "primary_contrast")),
        ("DISC primary_contrast estimator/estimate removed",
         lambda c: next(r for r in c.files[DISC]["contrasts"] if r["line"] == "primary_contrast")["estimator"].pop("estimate")),
        ("DISC decision_floor line removed", line_drop("contrasts", "decision_floor")),
        ("DISC contrast_interval line removed", line_drop("contrasts", "contrast_interval")),
        ("DISC attribution_floor line removed", line_drop("cells", "attribution_floor")),
        ("DISC dominance_branch line removed", line_drop("block_lines", "dominance_branch")),
        ("DISC dominance_ratio line removed", line_drop("block_lines", "dominance_ratio")),
        ("DISC sensitivity_bmax line removed", line_drop("block_lines", "sensitivity_bmax")),
        ("DISC sensitivity_window (alpha) line removed", line_drop("block_lines", "sensitivity_window")),
        ("DISC sensitivity_contrast line removed", line_drop("block_lines", "sensitivity_contrast")),
        ("DISC sensitivity_reported (computed) line removed", line_drop("block_lines", "sensitivity_reported", index=-1)),
        ("DISC sensitivity copy: contrasts emptied", lambda c: c.files[DISC]["sensitivity"]["contrasts"].clear()),
        ("DISC sensitivity copy removed", lambda c: c.files[DISC].pop("sensitivity")),
        ("DISC block_lines removed", lambda c: c.files[DISC].pop("block_lines")),
        ("CONTROL DISC reported_cell line removed", line_drop("cells", "reported_cell")),
        ("CONTROL DISC magnitude_per_token line removed", line_drop("contrasts", "magnitude_per_token")),
        ("CONTROL DISC neg8_screen alpha removed", line_drop("window_lines", "neg8_screen", "alpha")),
        ("CONTROL DISC sensitivity_window widened flipped",
         lambda c: next(r for r in c.files[DISC]["block_lines"] if r["line"] == "sensitivity_window").update(
             widened=not next(r for r in c.files[DISC]["block_lines"] if r["line"] == "sensitivity_window")["widened"])),
        ("RELABEL FILL floor_source_cell_ids/0 decode->prefill floor",
         lambda c: fill_contrast(c)["floor_source_cell_ids"].__setitem__(0, "d117-qwen3-1p7b-prefill-p2048-floor-v5")),
        ("RELABEL VERDICT floor/floor_row_ids swapped to prefill floors",
         lambda c: next(r for r in c.files[[k for k in c.files if k.endswith("claim-verdicts.json")][0]]["contrasts"]
                        if r["contrast_id"] == t8.DECODE)["floor"].__setitem__(
             "floor_row_ids", ["d117-qwen3-1p7b-prefill-p2048-floor-v5", "d117-qwen3-8b-prefill-p2048-floor-v5"])),
        ("RELABEL SENS record contrasts/0/floor_cell_ids swapped",
         lambda c: c.files[t8.SENSITIVITY]["contrasts"][0]["floor_cell_ids"].reverse()),
    ]
    for widened in (True, False):
        print(f"## base widened={widened}:", run(case(widened))[:2])
        for label, fn in cases:
            c = case(widened)
            fn(c)
            code, err, out = run(c)
            print(f"{label}: exit={code} err={err!r} fails={len(fails(out))}")


if __name__ == "__main__" and sys.argv[1] == "confirm":
    confirm()


def joint2():
    """An item removed from every L9 output that prints it AND from the recompute (no registered key left)."""
    def files(c, suffix):
        return c.files[[k for k in c.files if k.endswith(suffix) or k.startswith(suffix)][0]]

    def contrast(c, cid):
        for doc in (files(c, "claim-verdicts.json"), files(c, "-results-fill-input.json")["gamma"]):
            doc["contrasts"][:] = [r for r in doc["contrasts"] if r["contrast_id"] != cid]
        d = files(c, "disclosures/")
        d["contrasts"][:] = [r for r in d["contrasts"] if r.get("contrast_id") != cid]
        for doc in (c.files[t8.SENSITIVITY], d["sensitivity"]):
            doc["contrasts"][:] = [r for r in doc["contrasts"] if r["contrast_id"] != cid]
        d["block_lines"][:] = [r for r in d["block_lines"] if get_cid(r) != cid]
        c.ours["contrasts"].pop(cid, None)
        c.ours.get("descriptive", {}).pop(cid, None)
        c.ours["disclosures"].get("battery_assist", {}).pop(cid, None)
        c.ours["disclosures"]["sensitivity_bound"].get("contrasts", {}).pop(cid, None)

    def get_cid(r):
        return (r.get("record") or {}).get("contrast_id")

    def reported(c):
        files(c, "-projection-alpha.json")["cells"].clear()
        d = files(c, "disclosures/")
        d["cells"][:] = [r for r in d["cells"] if r.get("cell_id") != t8.REPORTED]
        for doc in (c.files[t8.SENSITIVITY], d["sensitivity"]):
            doc["reported_cells"][:] = [r for r in doc["reported_cells"] if r["cell_id"] != t8.REPORTED]
        d["block_lines"][:] = [r for r in d["block_lines"] if (r.get("record") or {}).get("cell_id") != t8.REPORTED]
        c.ours["reported_cells"].pop(t8.FAMILY)
        c.ours["disclosures"]["battery_assist"].pop(t8.FAMILY)
        c.ours["disclosures"]["sensitivity_bound"]["reported_cells"].pop(t8.FAMILY)

    def sens_floor(c):
        d = files(c, "disclosures/")
        cid = t8.FLOOR_CELLS["alpha"]
        for doc in (c.files[t8.SENSITIVITY], d["sensitivity"]):
            doc["floor_cells"][:] = [r for r in doc["floor_cells"] if r["cell_id"] != cid]
        d["block_lines"][:] = [r for r in d["block_lines"] if (r.get("record") or {}).get("cell_id") != cid]
        c.ours["disclosures"]["sensitivity_bound"]["floor_cells"].pop(t8.MODEL_CELLS["alpha"])

    def extraction(c):
        rep = files(c, "-extraction-alpha.json")
        drop_id = rep["cells"][0]["cell_id"]
        rep["cells"].pop(0)
        d = files(c, "disclosures/")
        d["floors"][:] = [r for r in d["floors"] if not (r["line"] == "floor_composition" and r["cell_id"] == drop_id)]
        key = cmp.extraction_key(cmp.load_registry(), drop_id)
        c.ours["floors"].pop(key, None)
        return drop_id

    def ratio(c):
        rows = files(c, "closeout.ratio-table.json")["ratios"]
        gone = rows.pop(0)
        d = files(c, "disclosures/")
        d["block_lines"][:] = [r for r in d["block_lines"] if not (r["line"] == "dominance_ratio"
                               and r.get("cell_id") == gone.get("cell_id") and r.get("component") == gone.get("component"))]
        label = cmp.ratio_label(gone, cmp.load_registry())
        if label.endswith("/common_mode"):
            c.ours["dominance"]["common_mode"].pop(label[: -len("/comparative/common_mode")], None)
        else:
            c.ours["dominance"]["ratios"].pop(label, None)

    for label, fn in (("decode contrast", lambda c: contrast(c, t8.DECODE)),
                      ("alpha decode reported cell", reported),
                      ("alpha decode sensitivity floor cell", sens_floor),
                      ("alpha extraction cell 0 (+its floor_composition line)", extraction),
                      ("ratio row 0 (+its dominance_ratio line)", ratio)):
        for widened in (True, False):
            c = case(widened)
            fn(c)
            code, err, out = run(c)
            print(f"JOINT {label} widened={widened}: exit={code} err={err!r} fails={fails(out)[:4]}")


if __name__ == "__main__" and sys.argv[1] == "joint2":
    joint2()


def loo():
    """Leave-one-out rows (t8.with_loo shape): L9-only drop, fill-only drop, joint drop, block relabel."""
    def fresh():
        c = t8.DefinitionAndStatusWordTests("test_loo_status_word_rule")
        c.setUp()
        t7.with_neg8(c); t7.with_references(c); t8.with_sensitivity(c, True)
        c.with_loo(["estimate_sign"], estimate=1.0)
        return c

    def show(label, fn):
        c = fresh(); fn(c)
        code, err, out = run(c)
        print(f"LOO {label}: exit={code} err={err!r} fails={fails(out)[:3]}")
    show("control", lambda c: None)
    show("verdict row dropped (fill keeps)", lambda c: t8.contrast_rows(c)[0]["loo"]["rows"].clear())
    show("fill row dropped (verdict keeps)", lambda c: t8.contrast_rows(c)[1]["loo"]["rows"].clear())
    show("both L9 rows dropped, status kept complete", lambda c: [r["loo"]["rows"].clear() for r in t8.contrast_rows(c)])
    show("joint: both L9 rows + recompute row dropped, status not_run, loo_counts 0",
         lambda c: ([r["loo"].update(rows=[], status="not_run") for r in t8.contrast_rows(c)],
                    c.ours["contrasts"][t8.DECODE].update(loo=[]),
                    t7.find(c, "loo_counts")[0][t7.find(c, "loo_counts")[1]].update(count=0)))
    show("omitted_block_id relabelled b03->b04 (both L9 copies)",
         lambda c: [r["loo"]["rows"][0].update(omitted_block_id="d117-decode-contrast-b04") for r in t8.contrast_rows(c)])


if __name__ == "__main__" and sys.argv[1] == "loo":
    loo()
