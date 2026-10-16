"""SPEC-v2 arithmetic pins and independent black-box CLI agreement.

The main estimator is executed only as a subprocess; no production pack code
is imported or inspected. Fixtures and output schemas come from the spec.
"""
import copy
import csv
import hashlib
import json
import math
import os
from pathlib import Path
import random
import runpy
import shutil
import subprocess
import sys
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parent.parent
TWIN = ROOT / "scripts" / "difficulty_twin.py"
REFERENCE = ROOT / "scripts" / "difficulty_estimate.py"

# §10, kept independently of the twin's constants.
AGREEMENT_TOL = 1e-6

SCHEMAS = {
    "cells.csv": "variant boundary model mode level cell_status n_bench_target n_bench k_correct accuracy acc_lo acc_hi mean_generated_tokens_bench cap_hit_rate_bench loop_rate_bench n_holdout_target n_holdout k_holdout holdout_accuracy mean_prompt_tokens_holdout mean_generated_tokens_holdout m_energy_target m_energy mean_energy_j energy_lo_j energy_hi_j model_energy_j epc_model_j epc_model_lo_j epc_model_hi_j epc_model_status epc_direct_j epc_direct_lo_j epc_direct_hi_j epc_direct_status epc_j epc_lo_j epc_hi_j epc_status primary_source primary_reason j_per_token jpt_lo jpt_hi token_mismatch_count rows_not_used replaced_rows".split(),
    "decomposition.csv": "variant boundary model mode N a_j a_se a_lo_j a_hi_j b_prompt_j_per_tok b_prompt_se b_prompt_lo b_prompt_hi b_gen_j_per_tok b_gen_se b_gen_lo b_gen_hi r2 r2_gen_only gen_share status".split(),
    "level_residuals.csv": "variant boundary model mode level m mean_residual_j lo_j hi_j contains_zero boot_lo_j boot_hi_j misfit".split(),
    "primary.csv": "variant boundary level a b epc_a_j epc_b_j source_a source_b log_ratio ratio desc_lo desc_hi dec_lo dec_hi status cheaper reason".split(),
    "rivals.csv": "variant boundary level cheapest rival log_ratio desc_lo desc_hi dec_lo dec_hi beaten reason".split(),
    "crossover.csv": "variant boundary level cheapest cheapest_epc_j status tied incomplete".split(),
}
KEYS = {
    "cells.csv": ("variant", "boundary", "model", "mode", "level"),
    "decomposition.csv": ("variant", "boundary", "model", "mode"),
    "level_residuals.csv": ("variant", "boundary", "model", "mode", "level"),
    "primary.csv": ("variant", "boundary", "level"),
    "rivals.csv": ("variant", "boundary", "level", "cheapest", "rival"),
    "crossover.csv": ("variant", "boundary", "level"),
}
STRINGS = set("variant boundary model mode cell_status epc_model_status epc_direct_status epc_status primary_source primary_reason status cheapest tied incomplete a b source_a source_b cheaper reason rival".split())
INTEGERS = set("level n_bench_target n_bench k_correct n_holdout_target n_holdout k_holdout m_energy_target m_energy token_mismatch_count rows_not_used replaced_rows N m contains_zero misfit beaten".split())
BENCH_COLUMNS = "model mode item_id level attempt outcome correct prompt_tokens generated_tokens cap_hit flags".split()
ENERGY_COLUMNS = "model mode level item_id boundary attempt energy_j prompt_tokens generated_tokens flags".split()


def bench_row(model, level, item, correct=1, prompt=100, generated=100, mode="off", flags="", cap=0, attempt=1):
    return dict(zip(BENCH_COLUMNS, (model, mode, item, level, attempt, "correct" if correct else "incorrect", correct, prompt, generated, cap, flags)))


def energy_row(bench, energy, boundary="rails", **overrides):
    row = {key: bench[key] for key in ("model", "mode", "level", "item_id", "attempt", "prompt_tokens", "generated_tokens")}
    row.update(boundary=boundary, energy_j=energy, flags="")
    return row | overrides


def config(roster, bench_sizes, energy_sizes, seed="pins", boundaries=("rails",)):
    """A full §2 config; unused mode and unspecified levels have zero sizes."""
    entries = []
    for model, mode, status in roster:
        entries.append(dict(model=model, mode=mode, status=status, repo="fixture/"+model,
                            revision="fixture-pin", output_cap=4096 if mode == "off" else 16384))
    ids = [r["model"]+"/"+r["mode"] for r in entries]
    sizes = {mode: {role: {str(l): source.get(mode, {}).get(l, 0) for l in range(1, 6)}
                    for role, source in (("bench", bench_sizes), ("energy", energy_sizes))}
             for mode in ("off", "on")}
    return dict(schema_version="difficulty_config.v2", version="difficulty-v2-test", seed="test-selection",
                n_per_level=max(1, *(v for ms in sizes.values() for rs in ms.values() for v in rs.values())),
                sizes=sizes, exclude_importer_sets=True, exclude_item_id_files=[], boundaries=list(boundaries),
                configurations=entries, primary_comparison={"a": ids[0], "b": ids[1]},
                descriptive_confidence=0.95, decision_confidence=0.99,
                bootstrap={"replicates": 200, "seed": seed}, exclude_flags=["runtime_failed"],
                physical_exclude_flags=["agent_overlap", "sleep", "contention_above_level", "idle_wait_cap"],
                loop_detector={"tail_fraction": 0.25, "min_span": 20, "min_repeats": 3})


def selections(cfg, bench_ids, energy_ids):
    lists = {mode: {role: {str(l): list(source.get(mode, {}).get(l, [])) for l in range(1, 6)}
                    for role, source in (("bench", bench_ids), ("energy", energy_ids))} for mode in ("off", "on")}
    return dict(schema_version="difficulty_selections.v2", pack_version=cfg["version"], seed=cfg["seed"],
                selection_domain="joulewise.packs.difficulty.selection.v2/"+cfg["seed"],
                sizes=copy.deepcopy(cfg["sizes"]), selections=lists)


def single_fixture(model, bench, energy, seed="pins"):
    bi, ei = {}, {}
    for l in range(1, 6):
        bi[l] = list(dict.fromkeys(r["item_id"] for r in bench if r["level"] == l))
        ei[l] = list(dict.fromkeys(r["item_id"] for r in energy if r["level"] == l))
    cfg = config([(model, "off", "measured"), ("absent", "off", "optional")],
                 {"off": {l: len(v) for l, v in bi.items()}}, {"off": {l: len(v) for l, v in ei.items()}}, seed)
    return cfg, selections(cfg, {"off": bi}, {"off": ei}), bench, energy


def cases_a_to_d():
    bench, energy = [], []
    models = ("A-C-D", "C-all", "C-zero", "C-one")
    for model, correct, m in ((models[0],15,5),(models[1],20,5),(models[2],0,5),(models[3],15,1)):
        # The twenty holdout rows realize A's denominator; the five energy
        # rows share the registered selection and enter the headline only.
        rows = [bench_row(model,1,f"e{i}",generated=g) for i,g in enumerate((50,70,80,90,110))]
        rows += [bench_row(model,1,f"h{i:02}",int(i<correct)) for i in range(20)]
        bench.extend(rows)
        energy.extend(energy_row(r,e) for r,e in zip(rows[:m],(100,120,140,160,180)))
    cfg = config([(m,"off","measured") for m in models],{"off":{1:25}},{"off":{1:5}})
    sel = selections(cfg,{"off":{1:[r["item_id"] for r in bench[:25]]}},{"off":{1:[f"e{i}" for i in range(5)]}})
    return cfg,sel,bench,energy


def cases_e_f():
    bench,energy = [],[]
    coordinates = [(100,50),(120,70),(80,80),(150,90),(110,110),(90,60)]
    for model,noise in (("E",(0,)*6),("F",(2,-1,0,-2,1,0))):
        for i,((p,g),delta) in enumerate(zip(coordinates,noise)):
            r = bench_row(model,1 if i<3 else 2,f"e{i}",prompt=p,generated=g)
            bench.append(r)
            energy.append(energy_row(r,10+.5*p+1.5*g+delta))
    cfg = config([("E","off","measured"),("F","off","measured")],{"off":{1:3,2:3}},{"off":{1:3,2:3}})
    ids = {"off":{1:["e0","e1","e2"],2:["e3","e4","e5"]}}
    return cfg,selections(cfg,ids,ids),bench,energy


def case_i():
    bench = [bench_row("I", 1, f"i{i:02}", int(i == 1 or 6 <= i <= 20)) for i in range(1, 26)]
    energy = [energy_row(r, e) for r, e in zip(bench, (100, 120, 140, 160, 180))]
    return single_fixture("I", bench, energy)


def case_m():
    ps = ((100,120,80,110), (105,125,85,115), (95,115,90,120), (110,100,85,125), (90,130,100,105))
    gs = ((50,70,80,60), (75,55,90,65), (60,85,70,55), (80,65,75,90), (70,60,85,55))
    es = ((141,169,175,150), (181,149,192.5,160), (160.5,206,172.5,164), (191,151.5,170,202.5), (166,159,192.5,140))
    bench, energy = [], []
    for l in range(1, 6):
        for i in range(4):
            r = bench_row("m", l, f"m{l}e{i}", prompt=ps[l-1][i], generated=gs[l-1][i])
            bench.append(r)
            energy.append(energy_row(r, es[l-1][i]))
        bench.extend(bench_row("m", l, f"m{l}h{i}", int(i != 5), 100+5*i, 60+5*i) for i in range(6))
    return single_fixture("m", bench, energy, "case-M")


def case_n(levels=(1, 2), optional=False, optional_present=False):
    models = ("qwen3-1.7b", "qwen3-4b")
    roster = [(m, "off", "measured") for m in models]
    if optional:
        roster.append(("qwen3-8b", "on", "optional"))
    cfg = config(roster, {"off": {l: 20 for l in levels}, "on": {l: 20 for l in range(1, 6)}},
                 {"off": {l: 8 for l in levels}, "on": {l: 8 for l in range(1, 6)}}, "case-N")
    bi = {l: [f"e{l}{i:02}" for i in range(8)]+[f"h{l}{i:02}" for i in range(12)] for l in levels}
    ei = {l: [f"e{l}{i:02}" for i in range(8)] for l in levels}
    sel = selections(cfg, {"off": bi, "on": bi}, {"off": ei, "on": ei})
    bench, energy = [], []
    noise = (-4,-3,4,3,3,4,-3,-4)
    for s, model in enumerate(models, 1):
        for l in levels:
            for i in range(8):
                p, g = 60+7*i+20*l, 100*l+37*((5*i)%8)+40*(l-1)
                r = bench_row(model, l, f"e{l}{i:02}", prompt=p, generated=g)
                bench.append(r)
                energy.append(energy_row(r, repr(round(s*(20+0.05*p+0.4*g+noise[i]), 6))))
            wrong = {11} if s == 1 and l == 1 else {1,4,6,9} if s == 1 else set() if l == 1 else {3,8}
            for i in range(12):
                bench.append(bench_row(model, l, f"h{l}{i:02}", int(i not in wrong),
                                       62+6*i+20*l, 100*l+31*((7*i)%12)+40*(l-1)))
    if optional_present:
        bench.append(bench_row("qwen3-8b", 1, "e100", mode="on"))
    return cfg, sel, bench, energy


def case_p(number, optional_present=False):
    if number == 5:
        return case_n(tuple(range(1, 6)), True, optional_present)
    if number in (3, 4):
        bench = [bench_row("retry", 1, f"i{i:02}") for i in range(25)]
        energy = [energy_row(bench[0], 100, flags="runtime_failed"),
                  energy_row(bench[0], 120, attempt=2), energy_row(bench[1], 140)]
        if number == 4:
            energy.append(energy_row(bench[1], 160, attempt=2))
        return single_fixture("retry", bench, energy)
    bench, energy = [], []
    for model in ("A", "B"):
        rows = [bench_row(model, 1, f"i{i:03}", int(model == "A" or number == 2 or i < 20)) for i in range(200)]
        bench.extend(rows)
        energy.extend(energy_row(r, 100 if model == "A" else 1) for r in rows[:1 if model == "B" and number == 2 else 20])
    cfg = config([("A", "off", "measured"), ("B", "off", "measured")], {"off": {1: 200}}, {"off": {1: 20}})
    sel = selections(cfg, {"off": {1: [f"i{i:03}" for i in range(200)]}}, {"off": {1: [f"i{i:03}" for i in range(20)]}})
    return cfg, sel, bench, energy


def case_q(state):
    bench = [bench_row("Q", 1, f"q{i:02}") for i in range(10)]
    energy = [energy_row(r, e) for r, e in zip(bench, (10,10,10,10,1000))]
    energy[-1]["flags"] = "contention" if state == "contention" else "contention_above_level"
    if state == "retry":
        energy.append(energy_row(bench[4], 12, attempt=2))
    return single_fixture("Q", bench, energy)


def synthetic_fixture(defects=True):
    rng = random.Random(20261014)
    roster = [("qwen3-1.7b", "off", "measured"), ("qwen3-4b", "off", "measured"),
              ("qwen3-8b", "off", "measured"), ("qwen3-4b", "on", "measured"), ("qwen3-8b", "on", "optional")]
    cfg = config(roster, {"off": {l: 30 for l in range(1,6)}, "on": {l: 16 for l in range(1,6)}},
                 {"off": dict(zip(range(1,6), (6,6,10,10,10))), "on": {l: 6 for l in range(1,6)}},
                 "joulewise.packs.difficulty.v2.bootstrap", ("rails", "wall"))
    # §3 orders, independently constructed on eligible synthetic ids.
    domain = "joulewise.packs.difficulty.selection.v2/" + cfg["seed"]
    def order(ids, tag):
        return sorted(ids, key=lambda item: (hashlib.sha256((domain+"/"+tag+"/"+item).encode()).hexdigest(), item))
    bi, ei = {m: {} for m in ("off", "on")}, {m: {} for m in ("off", "on")}
    for l in range(1, 6):
        population = order([f"synthetic-{l}-{i:02}" for i in range(30)], "level")
        for mode in ("off", "on"):
            bi[mode][l] = order(population, f"bench/{mode}/{l}")[:cfg["sizes"][mode]["bench"][str(l)]]
            ei[mode][l] = order(bi[mode][l], f"energy/{mode}/{l}")[:cfg["sizes"][mode]["energy"][str(l)]]
    sel = selections(cfg, bi, ei)
    bench, energy = [], []
    for model, mode, _ in roster:
        mi = ("qwen3-1.7b", "qwen3-4b", "qwen3-8b").index(model)
        for l in range(1, 6):
            rows = []
            for i, item in enumerate(bi[mode][l]):
                p = rng.randint(80, 500)
                g = rng.randint(50+100*l, 100+200*l)+(150 if mode == "on" else 0)
                k = int(rng.random() < 0.97-0.15*(l-1)+0.01*mi+(0.02 if mode == "on" else 0))
                if defects and (model, mode, l) == ("qwen3-8b", "on", 5):
                    k = 0
                rows.append(bench_row(model, l, item, k, p, g, mode,
                                      flags="repetition_loop" if i == 9 else "", cap=int(i % 13 == 0)))
            bench.extend(rows)
            lookup = {r["item_id"]: r for r in rows}
            for boundary in ("rails", "wall"):
                for item in ei[mode][l]:
                    r = lookup[item]
                    value = (30+0.02*r["prompt_tokens"]+(0.08+0.05*mi)*r["generated_tokens"])*rng.lognormvariate(0, 0.1)
                    energy.append(energy_row(r, value, boundary))
    if defects:
        # Exactly five numeric defects, on separate selected problems.
        for row, bad in zip(energy[20:25], ({"energy_j": "nan"}, {"energy_j": 0}, {"energy_j": "bad"},
                                           {"prompt_tokens": "1.5"}, {"generated_tokens": -1})):
            row.update(bad)
        energy.append(dict(energy[0]))  # same attempt, file-order duplicate
        retry_bench = bench[15]
        bench.append(retry_bench | {"attempt": 2})
        retry_bench.update(flags="runtime_failed", correct=0, outcome="malformed")
        for index in (2, 4):
            energy[index]["flags"] = "contention_above_level"
        energy.append(energy[2] | {"attempt": 2, "flags": "", "energy_j": energy[2]["energy_j"]*1.02})
        energy[5]["flags"] = "contention"
        # One expressly short cell, independent of the bad numbers and flags.
        removed = next(r for r in reversed(energy) if (r["model"],r["mode"],r["level"],r["boundary"]) == ("qwen3-1.7b","off",2,"wall"))
        energy.remove(removed)
        bench.append(bench[0] | {"item_id": "outside-selection"})
        bench.append(bench[0] | {"model": "unknown-model"})
    return cfg, sel, bench, energy


class TwinAgreementTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.twin = runpy.run_path(os.fspath(TWIN))

    def setUp(self):
        self.directory = Path(tempfile.mkdtemp(prefix="difficulty-v2-twin-"))
        self.addCleanup(shutil.rmtree, self.directory)

    def write_inputs(self, fixture):
        cfg, sel, bench, energy = fixture
        (self.directory/"config.json").write_text(json.dumps(cfg), encoding="utf-8")
        (self.directory/"selections.json").write_text(json.dumps(sel), encoding="utf-8")
        for name, columns, rows in (("bench.csv", BENCH_COLUMNS, bench), ("energy.csv", ENERGY_COLUMNS, energy)):
            with (self.directory/name).open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
                writer.writeheader()
                writer.writerows(rows)

    def command(self, script, tag):
        return [sys.executable, os.fspath(script), "--config", os.fspath(self.directory/"config.json"),
                "--selections", os.fspath(self.directory/"selections.json"), "--bench", os.fspath(self.directory/"bench.csv"),
                "--energy", os.fspath(self.directory/"energy.csv"), "--out", os.fspath(self.directory/tag)]

    def run_program(self, script, tag):
        command = self.command(script, tag)
        completed = subprocess.run(command, cwd=ROOT, env=os.environ | {"PYTHONDONTWRITEBYTECODE": "1"},
                                   text=True, capture_output=True, timeout=60)
        self.assertEqual(completed.returncode, 0, f"{script.name} failed: {completed.stderr}")
        tables = {}
        for name, schema in SCHEMAS.items():
            self.assertNotIn(b"\r", (self.directory/tag/name).read_bytes())
            with (self.directory/tag/name).open(newline="", encoding="utf-8") as handle:
                reader = csv.DictReader(handle)
                self.assertEqual(reader.fieldnames, schema, name)
                tables[name] = list(reader)
            keys = [self.row_key(name, r) for r in tables[name]]
            self.assertEqual(keys, sorted(keys), f"{script.name}/{name} unsorted")
            self.assertEqual(len(keys), len(set(keys)), f"{script.name}/{name} duplicate keys")
        tables["summary.json"] = json.loads((self.directory/tag/"summary.json").read_text(encoding="utf-8"))
        return tables

    @staticmethod
    def row_key(name, row):
        return tuple(int(row[k]) if k == "level" else row[k] for k in KEYS[name])

    def compare(self, main, twin):
        differences = []
        for name, schema in SCHEMAS.items():
            r = {self.row_key(name, row): row for row in main[name]}
            t = {self.row_key(name, row): row for row in twin[name]}
            if set(r) != set(t):
                differences.append(f"{name} row keys: main-only={sorted(set(r)-set(t))}, twin-only={sorted(set(t)-set(r))}")
            # Registration revision 2.3 (orchestrator, 2026-10-15): one bar for every float, 1e-6 relative
            # or absolute in the column's own unit. It sits about 1e9 above the float differences two
            # independent programs leave (1.8e-15 seen) and far below any printed digit; words, verdicts,
            # integers and strings stay exact.
            tolerance = AGREEMENT_TOL
            for key in sorted(set(r) & set(t)):
                for column in schema:
                    actual, expected = t[key][column], r[key][column]
                    if column in STRINGS or column in INTEGERS or actual == "" or expected == "":
                        matches = actual == expected
                    else:
                        x, y = float(actual), float(expected)
                        matches = x == y if math.isinf(x) or math.isinf(y) else math.isclose(x, y, rel_tol=tolerance, abs_tol=tolerance)
                    if not matches:
                        differences.append(f"{name} {key} {column}: twin={actual!r}, main={expected!r}")
        # §11: identical summary.json apart from method_note. Orchestrator ruling (2026-10-14): every
        # structure, key, string, integer and verdict must be equal; a float is the same number as the
        # CSV columns it repeats, so it takes the CSV tolerance (AGREEMENT_TOL, revision 2.3), since
        # two independent programs need not round the last binary digit alike.
        ms = {k: v for k, v in main["summary.json"].items() if k != "method_note"}
        ts = {k: v for k, v in twin["summary.json"].items() if k != "method_note"}

        def walk(x, y, path="summary"):
            if isinstance(x, dict) and isinstance(y, dict):
                for k in sorted(set(x) | set(y)):
                    walk(x.get(k), y.get(k), path+"."+k)
            elif isinstance(x, list) and isinstance(y, list) and len(x) == len(y):
                for i, (a, b) in enumerate(zip(x, y)):
                    walk(a, b, f"{path}[{i}]")
            elif isinstance(x, float) and isinstance(y, float) and type(x) is type(y):
                same = x == y if math.isinf(x) or math.isinf(y) else math.isclose(x, y, rel_tol=AGREEMENT_TOL, abs_tol=AGREEMENT_TOL)
                if not same:
                    differences.append(f"{path}: twin={y!r}, main={x!r}")
            elif type(x) is not type(y) or x != y:
                differences.append(f"{path}: twin={y!r}, main={x!r}")
        walk(ms, ts)
        self.assertFalse(differences, "\n"+"\n".join(differences[:100])+f"\nTotal disagreements: {len(differences)}")

    def agreement(self, fixture, tag):
        self.write_inputs(fixture)
        twin = self.run_program(TWIN, tag+"-twin")
        self.compare(self.run_program(REFERENCE, tag+"-main"), twin)
        return twin

    def twin_only(self, fixture, tag):
        self.write_inputs(fixture)
        return self.run_program(TWIN, tag)

    @staticmethod
    def cell(tables, model, level=1, variant="primary", boundary="rails", mode="off"):
        return next(r for r in tables["cells.csv"] if (r["model"],int(r["level"]),r["variant"],r["boundary"],r["mode"]) == (model,level,variant,boundary,mode))

    def pins(self, row, values, digits=6):
        for key, value in values.items():
            with self.subTest(field=key):
                self.assertAlmostEqual(float(row[key]), value, delta=0.5*10**(-digits))

    def test_cli_acceptance_agreement(self):
        start = time.monotonic()
        cases = [("A-D", cases_a_to_d()), ("E-F", cases_e_f()), ("I", case_i()), ("M", case_m()), ("N", case_n())]
        cases += [(f"P{i}", case_p(i)) for i in range(1,6)]
        cases += [("P5-present", case_p(5, True))]
        cases += [("Q-"+s, case_q(s)) for s in ("flag", "retry", "contention")]
        for tag, fixture in cases:
            with self.subTest(case=tag):
                self.agreement(fixture, tag)
        elapsed = time.monotonic()-start
        print(f"CLI acceptance agreement runtime: {elapsed:.3f}s", flush=True)
        self.assertLess(elapsed,60,"§11 runtime budget")

    def test_seeded_synthetic_agreement(self):
        start = time.monotonic()
        try:
            self.agreement(synthetic_fixture(), "synthetic")
        finally:
            elapsed = time.monotonic()-start
            print(f"Seeded synthetic agreement runtime: {elapsed:.3f}s", flush=True)
            self.assertLess(elapsed, 60, "§11 runtime budget")

    def test_twin_pinned_a_to_f_and_fprime(self):
        w = self.twin["wilson"]
        for k, lo, hi in ((15,0.531299,0.888138), (20,0.838875,1), (0,0,0.161125)):
            p, actual_lo, actual_hi = w(k,20,0.95)
            self.pins(dict(lo=actual_lo, hi=actual_hi), dict(lo=lo,hi=hi))
            self.assertEqual(p, k/20)
        energies = [100,120,140,160,180]
        mean, elo, ehi = self.twin["mean_interval"](energies,0.95)
        self.pins(dict(mean=mean,lo=elo,hi=ehi), dict(mean=140,lo=100.7351,hi=179.2649),4)
        for k, point, lo, hi in ((15,186.6667,128.934,285.303), (20,140,100.735,189.604)):
            p, pl, ph = w(k,20,0.95)
            point0, lo0, hi0, status = self.twin["energy_per_correct"](mean,elo,ehi,p,pl,ph,k,5)
            self.assertEqual(status,"ok")
            self.pins(dict(point=point0),dict(point=point),4)
            self.pins(dict(lo=lo0,hi=hi0),dict(lo=lo,hi=hi),3)
        self.assertEqual(self.twin["energy_per_correct"](mean,elo,ehi,0,0,1,0,5)[3], "not_estimable_zero_correct")
        self.assertEqual(self.twin["energy_per_correct"](None,None,None,.75,.5,.9,15,1)[3], "not_estimable_few_attempts")
        point, lo, hi = self.twin["joules_per_token"](energies,[50,70,80,90,110],0.95)
        self.pins(dict(point=point,lo=lo,hi=hi),dict(point=1.75,lo=1.610097,hi=1.889903))
        coordinates = [(100,50),(120,70),(80,80),(150,90),(110,110),(90,60)]
        for model, noise in (("E",(0,)*6),("F",(2,-1,0,-2,1,0))):
            rows = [dict(prompt_tokens=p,generated_tokens=g,energy_j=10+.5*p+1.5*g+delta,level=1 if i<3 else 2)
                    for i, ((p,g),delta) in enumerate(zip(coordinates,noise))]
            fit, residuals = self.twin["decompose"](rows,.95)
            if model == "E":
                self.pins(fit,dict(a_j=10,b_prompt_j_per_tok=.5,b_gen_j_per_tok=1.5,r2=1,gen_share=.641860,r2_gen_only=.910222))
                for r in residuals:
                    self.pins(r,dict(mean_residual_j=0,lo_j=0,hi_j=0))
                    self.assertEqual(r["contains_zero"],1)
            else:
                self.pins(fit,dict(a_j=13.980831,a_se=3.137012,b_prompt_j_per_tok=.465176,b_prompt_se=.027441,
                                   b_gen_j_per_tok=1.497284,b_gen_se=.031545,r2=.999164,
                                   a_lo_j=3.997459,a_hi_j=23.964202,b_prompt_lo=.377846,b_prompt_hi=.552506,
                                   b_gen_lo=1.396896,b_gen_hi=1.597673))
                rss = math.fsum((r["energy_j"]-self.twin["predict"](fit,r["prompt_tokens"],r["generated_tokens"]))**2 for r in rows)
                self.pins(dict(rss=rss),dict(rss=6.060703))
                self.pins(dict(tss=fit["_tss"]),dict(tss=7250.833),3)

    def test_twin_case_h(self):
        t = self.twin["student_t_quantile"]
        for df, expected in ((3,3.182446305),(4,2.776445105),(9,2.262157163),(19,2.093024054),(29,2.045229642)):
            with self.subTest(df=df):
                self.assertAlmostEqual(t(.975,df),expected,delta=1e-9)
                self.assertAlmostEqual(t(.025,df),-expected,delta=1e-9)
        self.assertEqual(t(.5,19),0)

    def test_twin_case_i(self):
        row = self.cell(self.twin_only(case_i(),"I-pins"),"I")
        self.assertEqual((row["n_bench"],row["k_correct"],row["n_holdout"],row["k_holdout"]),("25","16","20","15"))
        self.pins(row,dict(accuracy=.64,epc_direct_j=186.6667),4)
        self.pins(row,dict(epc_direct_lo_j=128.934,epc_direct_hi_j=285.303),3)

    def test_twin_case_l_points(self):
        coords = [(100,50,135),(120,70,175),(80,80,170),(150,90,220),(110,110,230),(90,60,145)]
        bench, energy = [], []
        for i,(p,g,e) in enumerate(coords):
            r = bench_row("L",1 if i<3 else 2,f"e{i}",prompt=p,generated=g)
            bench.append(r)
            energy.append(energy_row(r,e))
        for l, values in ((1,((100,60,1),(110,80,1),(90,100,0),(100,40,1))),(2,((130,100,1),(150,120,0)))):
            bench.extend(bench_row("L",l,f"h{l}-{i}",k,p,g) for i,(p,g,k) in enumerate(values))
        tables = self.twin_only(single_fixture("L",bench,energy),"L-pins")
        for l, mu, epc, direct in ((1,165,220,213.3333),(2,245,490,396.6667)):
            self.pins(self.cell(tables,"L",l),dict(model_energy_j=mu,epc_model_j=epc,epc_direct_j=direct),4)

    def test_twin_case_m(self):
        tables = self.twin_only(case_m(),"M-pins")
        fit = next(r for r in tables["decomposition.csv"] if r["variant"] == "primary")
        self.pins(fit,dict(a_j=33.503039,b_prompt_j_per_tok=.271248,b_gen_j_per_tok=1.542626))
        expected = [(-2.826596,-5.748090,.946453),(-1.949246,-4.415225,1.460235),(9.638720,5.579092,11.109952),
                    (-2.787539,-6.475269,2.171315),(-2.075339,-5.407524,.914395)]
        for l, (mean,lo,hi) in enumerate(expected,1):
            residual = next(r for r in tables["level_residuals.csv"] if r["variant"] == "primary" and int(r["level"]) == l)
            self.pins(residual,dict(mean_residual_j=mean,boot_lo_j=lo,boot_hi_j=hi))
            self.assertEqual(residual["misfit"],str(int(l==3)))
            self.assertEqual(residual["contains_zero"],str(int(l!=3)))
            cell = self.cell(tables,"m",l)
            self.pins(cell,dict(model_energy_j=175.858766,epc_model_j=211.030519))
            self.assertEqual(cell["primary_source"],"direct" if l==3 else "model")
            if l==3:
                self.assertEqual(cell["primary_reason"],"misfit")
                self.pins(cell,dict(epc_j=210.9,epc_lo_j=162.25,epc_hi_j=518.25),2)
            else:
                self.pins(cell,dict(epc_j=211.030519))
        self.assertEqual(tables["summary.json"]["variants"]["primary"]["rails"]["misfit_cells"],["m/off:3"])

    def test_twin_case_n(self):
        tables = self.twin_only(case_n(),"N-pins")
        pins = [("qwen3-1.7b",1,133.95,146.127273,117.025,127.663636,112.843767,194.765079,-1.459451,1.241493),
                ("qwen3-1.7b",2,190.95,286.425,174.025,261.0375,202.676733,465.784376,-1.241493,1.459451),
                ("qwen3-4b",1,267.9,267.9,234.05,234.05,223.119116,318.065197,-2.730711,2.264987),
                ("qwen3-4b",2,381.9,458.28,348.05,417.66,350.592955,658.884550,-2.264987,2.730711)]
        for model,l,mu,epc,em,direct,lo,hi,rlo,rhi in pins:
            self.pins(self.cell(tables,model,l),dict(model_energy_j=mu,epc_model_j=epc,mean_energy_j=em,epc_direct_j=direct,epc_model_lo_j=lo,epc_model_hi_j=hi))
            residual = next(r for r in tables["level_residuals.csv"] if r["variant"]=="primary" and r["model"]==model and int(r["level"])==l)
            self.pins(residual,dict(boot_lo_j=rlo,boot_hi_j=rhi))
            self.assertEqual(residual["misfit"],"0")
        for l, points in ((1,(-.606136,-.963820,-.239224,-1.037935,-.101456)),(2,(-.470004,-.945010,.045545,-1.002726,.507957))):
            r = next(r for r in tables["primary.csv"] if r["variant"]=="primary" and int(r["level"])==l)
            self.pins(r,dict(zip(("log_ratio","desc_lo","desc_hi","dec_lo","dec_hi"),points)))
            self.assertEqual(r["status"],"resolved" if l==1 else "unresolved")
            self.assertEqual(r["cheaper"],"qwen3-1.7b/off" if l==1 else "")
        self.assertEqual(tables["summary.json"]["variants"]["primary"]["rails"]["primary_question"]["verdict"],"no_resolved_change")

    def test_twin_case_o(self):
        percentile = self.twin["percentile"]
        values = [b/100-.03 for b in range(1,201)]
        self.pins(dict(zip(("lo","hi"),percentile(values,.95))),dict(lo=.02,hi=1.93),2)
        self.pins(dict(zip(("lo","hi"),percentile(values,.99))),dict(lo=-.02,hi=1.97),2)
        lo,hi = percentile(values,.99)
        self.assertTrue(lo <= 0 <= hi)
        self.assertEqual(percentile(list(range(1,41)),.95),(1,40))
        self.assertEqual(percentile(list(range(1,41)),.5),(10,31))
        rows = [dict(status="resolved",cheaper="a"),dict(status="unresolved",cheaper="")]
        verdict = self.twin["primary_verdict"]
        self.assertEqual(verdict(rows),"no_resolved_change")
        lo,hi = percentile([x+1 for x in values],.99)
        self.assertGreater(lo,0)
        rows[1] = dict(status="resolved",cheaper="b")
        self.assertEqual(verdict(rows),"cheaper_size_changes_with_level")
        self.assertEqual(self.twin["log_replicates"]([math.inf,10,math.inf],[math.inf,math.inf,10]),[0,-math.inf,math.inf])

    def test_twin_case_p(self):
        for number in (1,2):
            with self.subTest(case=number):
                tables = self.twin_only(case_p(number),f"P{number}-pins")
                cross = next(r for r in tables["crossover.csv"] if r["variant"]=="primary" and r["level"]=="1")
                self.assertEqual(cross["cheapest"],"A/off")
                self.assertEqual(cross["status"],"unresolved_incomplete")
                self.assertEqual(cross["incomplete"],"B/off:"+("not_estimable_zero_correct" if number==1 else "short"))
        for number in (3,4):
            with self.subTest(case=number):
                tables = self.twin_only(case_p(number),f"P{number}-pins")
                row = self.cell(tables,"retry")
                self.assertEqual((row["m_energy"],row["n_holdout"],row["cell_status"]),("2","23","complete"))
                self.assertEqual(row["replaced_rows"],str(number-2))
                self.assertEqual(tables["summary.json"]["flag_counts"]["energy"].get("duplicate",0),int(number==4))
        absent = self.twin_only(case_p(5),"P5-absent-pins")
        present = self.twin_only(case_p(5,True),"P5-present-pins")
        self.assertEqual(absent["summary.json"]["roster"]["qwen3-8b/on"],"not_measured")
        self.assertFalse(any(r["model"]=="qwen3-8b" for r in absent["cells.csv"]))
        self.assertFalse(any(r["rival"]=="qwen3-8b/on" for r in absent["rivals.csv"]))
        for l in range(1,6):
            self.assertEqual(self.cell(present,"qwen3-8b",l,mode="on")["cell_status"],"short" if l==1 else "missing")
        self.assertTrue(all(r["status"]=="unresolved_incomplete" for r in present["crossover.csv"]))
        self.assertEqual(absent["primary.csv"],present["primary.csv"])

    def test_twin_case_q(self):
        for state in ("flag","retry","contention"):
            tables = self.twin_only(case_q(state),"Q-"+state+"-pins")
            for variant in ("primary","flagged_inclusive"):
                with self.subTest(state=state,variant=variant):
                    r = self.cell(tables,"Q",variant=variant)
                    mean = 208 if variant=="flagged_inclusive" or state=="contention" else 10.4 if state=="retry" else 10
                    self.pins(r,dict(mean_energy_j=mean),1)
                    self.assertEqual(r["m_energy"],"4" if state=="flag" and variant=="primary" else "5")
                    self.assertEqual(r["cell_status"],"short" if state=="flag" and variant=="primary" else "complete")
                    self.assertEqual(r["replaced_rows"],"1" if state=="retry" else "0")

    def test_twin_infinite_bootstrap_bounds_and_manifest_input(self):
        fixture = list(case_n())
        cfg, sel, bench, energy = fixture
        for r in bench:
            if r["item_id"].startswith("h"):
                r["correct"] = int(r["item_id"].endswith("00"))
        sel["schema_version"] = "difficulty_manifest.v2"
        sel["items"] = []  # The estimator uses the selection keys only (§3).
        tables = self.twin_only(fixture,"infinity-manifest")
        for model in ("qwen3-1.7b","qwen3-4b"):
            for l in (1,2):
                self.assertEqual(self.cell(tables,model,l)["epc_hi_j"],"inf")
        self.assertTrue(all(not math.isnan(float(r["dec_lo"])) and not math.isnan(float(r["dec_hi"]))
                            for r in tables["primary.csv"] if r["dec_lo"]))

    def test_config_number_bearing_validation(self):
        base = case_n()[0]
        mutations = [("schema_version","v1"),("version",""),("seed",""),("n_per_level",True),
                     ("descriptive_confidence",.5),("decision_confidence",float("nan"))]
        for key,value in mutations:
            with self.subTest(key=key):
                cfg = copy.deepcopy(base)
                cfg[key] = value
                with self.assertRaisesRegex(ValueError,key):
                    self.twin["validate_config"](cfg)
        for root,key,value in (("bootstrap","seed",""),("bootstrap","replicates",19),
                               ("loop_detector","tail_fraction",0),("loop_detector","min_span",0),
                               ("loop_detector","min_repeats",1)):
            with self.subTest(root=root,key=key):
                cfg = copy.deepcopy(base)
                cfg[root][key] = value
                with self.assertRaisesRegex(ValueError,key):
                    self.twin["validate_config"](cfg)

    def test_invalid_config_and_unreadable_inputs(self):
        fixture = case_n()
        for key in ("confidence","sizes","physical_exclude_flags","primary_comparison.b","status"):
            with self.subTest(key=key):
                mutated = copy.deepcopy(fixture)
                cfg = mutated[0]
                if key=="confidence":
                    cfg[key] = .95
                elif key=="sizes":
                    cfg["sizes"]["off"]["energy"]["1"] = 30
                elif key=="physical_exclude_flags":
                    cfg[key].append("runtime_failed")
                elif key=="status":
                    del cfg["configurations"][0][key]
                else:
                    cfg["primary_comparison"]["b"] = "unknown/off"
                self.write_inputs(mutated)
                for script in (TWIN,REFERENCE):
                    result = subprocess.run(self.command(script,"invalid"),cwd=ROOT,text=True,capture_output=True,timeout=60,
                                            env=os.environ | {"PYTHONDONTWRITEBYTECODE":"1"})
                    self.assertNotEqual(result.returncode,0)
                    self.assertIn(key.split(".")[-1] if key!="confidence" else "descriptive_confidence",result.stderr)
        self.write_inputs(fixture)
        for extra in (("--bench",str(self.directory/"missing.csv")),("--confidence",".9")):
            result = subprocess.run(self.command(TWIN,"bad")+list(extra),cwd=ROOT,text=True,capture_output=True,timeout=60)
            self.assertNotEqual(result.returncode,0)

    def test_parse_variants_and_selection_mismatch(self):
        fixture = list(case_n())
        cfg, sel, b, e = fixture
        # Bad modes/levels take no part in cell attribution; token parsing is ASCII.
        b += [b[0] | {"level":v,"item_id":f"badlevel-{i}"} for i,v in enumerate(("", "1.5",9,"١"))]
        b.append(b[0] | {"mode":"invalid"})
        e += [e[0] | {"item_id":f"badtoken-{i}","generated_tokens":v} for i,v in enumerate(("abc","12.0"))]
        e.append(e[1] | {"attempt":2,"boundary":"unknown"})
        sel["selections"]["on"]["bench"]["1"] = []
        self.agreement(fixture,"parse")


if __name__ == "__main__":
    unittest.main()
