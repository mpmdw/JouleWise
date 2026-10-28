"""RC-CMP-OPUS-REV probes: false agreement in scripts/compare_b5_recompute.py.

Synthetic fixture from tests/independent_recompute/test_comparator.py only.
Each probe plants an L9-vs-recompute difference far beyond the bars and prints
whether the comparator would exit 0 (no failing family, no unmapped leaf).
Run from the repo root: python3.13 .codex-report/rc-cmp-opus-rev/probe_comparator.py
"""
import copy, hashlib, json, sys, tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tests.independent_recompute import test_comparator as t

cmp, SHA, DECODE, PREFILL = t.cmp, t.SHA, t.DECODE, t.PREFILL
FILL = f"outputs/{SHA}-results-fill-input.json"
VERD = f"outputs/{SHA}-claim-verdicts.json"
DISC = f"disclosures/{SHA}.json"


def run(files, ours, rules=t.RULES, bars=t.BARS["recompute_coded_7e322b76"], meter=()):
    root = Path(tempfile.mkdtemp())
    outputs = []
    for name, value in files.items():
        path = root / "custody" / cmp.RESTRICTED / name
        path.parent.mkdir(parents=True, exist_ok=True)
        raw = json.dumps(value).encode()
        path.write_bytes(raw)
        outputs.append({"name": name, "sha256": hashlib.sha256(raw).hexdigest()})
    (root / "custody" / cmp.RECORD).write_text(json.dumps({"steps": [{"step": "11", "window": None, "status": "ok", "outputs": outputs}]}))
    (root / "ours.json").write_text(json.dumps(ours))
    specs = []
    for pack, record in meter:
        (root / f"meter-{pack}.json").write_text(json.dumps(record))
        specs.append(f"{pack}=" + str(root / f"meter-{pack}.json"))
    try:
        result = cmp.run(root / "custody", root / "ours.json", bars, rules, specs)
    except cmp.Refusal as exc:
        return "REFUSED " + str(exc)
    fails = {f: n["fail"] for f, n in result["counts"].items() if n["fail"]}
    exit0 = not fails and not result["coverage"]["unmapped"] and not result["coverage"]["absent_sources"]
    return f"exit0={exit0} fails={fails} unmapped={result['coverage']['unmapped']}"


def base():
    return t.l9_files(), t.recompute_output()


def probe(name, edit, **kw):
    files, ours = base()
    extra = edit(files, ours) or {}
    if kw.get("rules", t.RULES) is None:
        files[DISC].pop("note", None)  # fixture-only text leaf the shipped COVERAGE does not map
    print(f"{name}: {run(files, ours, **{**kw, **extra})}")


print("baseline:", run(*base()))
_f, _o = base(); _f[DISC].pop("note")
print("baseline, shipped COVERAGE:", run(_f, _o, rules=None))


def swap_fill(files, ours):
    # PREFILL's estimate becomes -2.5 on both sides; the FILL (what step 11 prints) swaps the two contrasts.
    for row in files[VERD]["contrasts"]:
        if row["contrast_id"] == PREFILL:
            row["estimator"]["estimate"] = -2.5
    ours["contrasts"][PREFILL]["dbar_j"] = -2.5
    files[FILL]["gamma"]["contrasts"][0]["estimate"] = -2.5   # DECODE printed as -2.5 (truth -1.25)
    files[FILL]["gamma"]["contrasts"][1]["estimate"] = -1.25  # PREFILL printed as -1.25 (truth -2.5)
probe("P1 fill swaps two contrasts' estimates (test RULES)", swap_fill)
probe("P1b same, shipped COVERAGE rules", swap_fill, rules=None)


def cross_field(files, ours):
    # DECODE's printed fill estimate is its s_d (16.0): a value compared in contrast_j, but for another key.
    files[FILL]["gamma"]["contrasts"][0]["estimate"] = 16.0
probe("P2 fill prints another field's value (s_d) as the estimate, COVERAGE", cross_field, rules=None)


def wrong_word(files, ours):
    # Fill carries an outcome word for DECODE that differs from the verdict ("not_resolvable"); "L1" is a compared
    # outcome_word value (the ceiling), and null matches the compared direction "none".
    files[FILL]["gamma"]["contrasts"][0]["claim_evaluation"] = {"outcome": "L1"}
    files[FILL]["gamma"]["contrasts"][1]["claim_evaluation"] = {"outcome": None}
probe("P3 fill outcome words 'L1' and null (truth not_resolvable), COVERAGE", wrong_word, rules=None)


def drop_contrast(files, ours):
    # L9 silently omits PREFILL everywhere; the recompute has it with a very different estimate.
    files[VERD]["contrasts"] = [r for r in files[VERD]["contrasts"] if r["contrast_id"] != PREFILL]
    files[FILL]["gamma"]["contrasts"] = files[FILL]["gamma"]["contrasts"][:1]
    ours["contrasts"][PREFILL].update(dbar_j=500.0, p=1e-9, outcome="direction_supported")
probe("P4 contrast present on the recompute side only", drop_contrast)


def drop_run(files, ours):
    del files["rereduced/alpha/run-a.rereduced.json"]
    ours["members"]["ALPHA"]["run-a"]["E_j"]["decode"] = 1e6
probe("P5 run present on the recompute side only (no L9 rereduced file)", drop_run)


def drop_cells(files, ours):
    files[f"mint/{SHA}-extraction-beta.json"]["cells"] = []
    ours["floors"]["Qwen3-8B-4bit/decode/absolute"]["guarded_floor_j"] = 1e6
probe("P6 L9 extraction report with no cells (recompute has floors)", drop_cells)


def meter_one_sided(files, ours):
    # The recompute and the harvest record both carry a whole-machine line; L9's disclosure has no machine_member line.
    ours["disclosures"]["whole_machine"] = {"windows": {"ALPHA": {"members": {"run-a": {"phases": {"request": {
        "rho": 0.5, "rail_delta_J": 10.0, "delta_J": 20.0, "meter": {"energy_J": 99.0, "n": 5}}}}}}}}
    record = {"members": {"run-a": {"rho": 0.9, "rail_delta_J": 1.0,
                                    "machine": {"delta_J": 2.0, "meter": {"energy_J": 1.0, "n": 50}}}}}
    return {"meter": [("alpha", record)]}
probe("P7 meter line on recompute + harvest record, none in L9 disclosure, --harvest-meter given", meter_one_sided)


def override(files, ours):
    bars = json.loads(Path(t.BARS["recompute_coded_7e322b76"]).read_text())
    bars["families"]["contrast_j"]["keys"] = [{"match": ".*", "absolute": float("inf")}]
    path = Path(tempfile.mkdtemp()) / "bars.json"
    path.write_text(json.dumps(bars))  # json writes Infinity; json.loads accepts it
    ours["contrasts"][DECODE]["D_j"] = 1e9
    return {"bars": path}
probe("P8 per-key override absolute=Infinity accepted by load_bars (planted D_j=1e9)", override)


def override_neg(files, ours):
    bars = json.loads(Path(t.BARS["recompute_coded_7e322b76"]).read_text())
    bars["families"]["contrast_j"]["keys"] = [{"match": ".*", "printed_decimals": -9}]
    path = Path(tempfile.mkdtemp()) / "bars.json"
    path.write_text(json.dumps(bars))
    ours["contrasts"][DECODE]["D_j"] = 1e8
    return {"bars": path}
probe("P8b per-key override printed_decimals=-9 accepted (planted D_j=1e8)", override_neg)


def family_level_inf(files, ours):
    bars = json.loads(Path(t.BARS["recompute_coded_7e322b76"]).read_text())
    bars["families"]["contrast_j"]["absolute"] = float("inf")
    path = Path(tempfile.mkdtemp()) / "bars.json"
    path.write_text(json.dumps(bars))
    return {"bars": path}
probe("P8c control: family-level Infinity", family_level_inf)


def bool_int(files, ours):
    for row in files[VERD]["contrasts"]:
        row["multiplicity"]["rejected"] = True
    ours["contrasts"][DECODE]["holm_reject"] = 1
    ours["contrasts"][PREFILL]["holm_reject"] = 1.0
probe("P9 exact(): L9 True vs recompute 1 / 1.0", bool_int)


def nan_side(files, ours):
    ours["contrasts"][DECODE]["D_j"] = float("nan")
probe("P10 NaN on the recompute side (run() level)", nan_side)


def no_bar(files, ours):
    bars = json.loads(Path(t.BARS["recompute_coded_7e322b76"]).read_text())
    del bars["families"]["count"]
    path = Path(tempfile.mkdtemp()) / "bars.json"
    path.write_text(json.dumps(bars))
    return {"bars": path}
probe("P11 numeric family absent from bar file", no_bar)


def catch_all(files, ours):
    # Numeric energy leaves under subtrees the shipped COVERAGE maps wholesale to "uncovered".
    files[DISC]["window_lines"] = {"alpha": [{"line": "machine_member", "run_id": "run-a", "meter_energy_j": 999.0,
                                              "values": {"rho": 7.0}}]}
    files[FILL]["campaigns"] = {"gamma": {"gross_energy_j": 12345.0}}
    files[FILL]["characterization"] = {"delta_j": 5.0}
probe("P12 energy leaves under window_lines/*, fill:campaigns/*, fill:characterization/* (COVERAGE)", catch_all, rules=None, bars=cmp.DEFAULT_BARS)


def catch_all_report(files, ours):
    files[DISC].pop("note", None)
    catch_all(files, ours)
    root = Path(tempfile.mkdtemp()); outputs = []
    for name, value in files.items():
        p = root / cmp.RESTRICTED / name; p.parent.mkdir(parents=True, exist_ok=True); raw = json.dumps(value).encode()
        p.write_bytes(raw); outputs.append({"name": name, "sha256": hashlib.sha256(raw).hexdigest()})
    (root / cmp.RECORD).write_text(json.dumps({"steps": [{"step": "11", "window": None, "status": "ok", "outputs": outputs}]}))
    (root / "o.json").write_text(json.dumps(ours))
    leaves = cmp.run(root, root / "o.json", cmp.DEFAULT_BARS, None)["coverage"]["leaves"]
    for k, v in leaves.items():
        if any(s in k for s in ("meter_energy", "values/rho", "gross_energy", "characterization")):
            print("    ", k, "->", v[:60])
catch_all_report(*base())
