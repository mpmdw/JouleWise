"""v2 acceptance cases A-F/H/I/L-Q and parse, bootstrap and CLI boundaries."""
import copy
import csv
import json
import math
import os
import random
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from joulewise.packs.difficulty import estimators as est
from joulewise.packs.difficulty.config import load_config, validate_config

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/difficulty/pack_config.json"
ENERGIES = [100, 120, 140, 160, 180]
TOKENS = [50, 70, 80, 90, 110]


def bench_row(index=0, **changes):
    return dict(model="X", mode="off", item_id=f"i{index}", level=1, attempt=1, outcome="correct",
                correct=1, prompt_tokens=100, generated_tokens=20, cap_hit=0, flags="") | changes


def energy_row(index=0, **changes):
    return dict(model="X", mode="off", item_id=f"i{index}", level=1, boundary="rails", attempt=1,
                energy_j=100, prompt_tokens=100, generated_tokens=20, flags="") | changes


def ols_rows(noise=None):
    p, g = [100, 120, 80, 150, 110, 90], [50, 70, 80, 90, 110, 60]
    return [energy_row(index, prompt_tokens=x, generated_tokens=y, energy_j=10+.5*x+1.5*y+z)
            for index, (x, y, z) in enumerate(zip(p, g, noise or [0]*6))]


def design(bench_ids, energy_ids, models=("X", "Y"), seed="tests", b=200):
    """Hand fixtures register their sizes and a second, absent optional primary arm."""
    config = load_config(FIXTURE)
    config.update(seed=seed, exclude_importer_sets=False, exclude_item_id_files=[], boundaries=["rails"])
    config["configurations"] = [dict(model=model, mode="off", output_cap=4096,
                                     status="measured" if i == 0 else "optional") for i, model in enumerate(models)]
    config["primary_comparison"] = {"a": models[0] + "/off", "b": models[1] + "/off"}
    config["bootstrap"] = {"seed": seed, "replicates": b}
    lists = {mode: {role: {str(l): [] for l in range(1, 6)} for role in ("bench", "energy")} for mode in ("off", "on")}
    for role, ids in (("bench", bench_ids), ("energy", energy_ids)):
        lists["off"][role].update({str(l): list(values) for l, values in ids.items()})
    config["sizes"] = {mode: {role: {l: len(values) for l, values in lists[mode][role].items()} for role in ("bench", "energy")}
                       for mode in lists}
    config["n_per_level"] = max(1, *(config["sizes"]["off"]["bench"].values()))
    selections = {"schema_version": "difficulty_manifest.v2", "pack_version": config["version"], "seed": seed,
                  "selection_domain": "joulewise.packs.difficulty.selection.v2/" + seed,
                  "sizes": copy.deepcopy(config["sizes"]), "selections": lists}
    validate_config(config)
    return config, selections


def cell(tables, model="X", level=1, variant="primary", boundary="rails"):
    return next(row for row in tables["cells"] if (row["model"], row["level"], row["variant"], row["boundary"]) ==
                (model, level, variant, boundary))


def read_outputs(path):
    result = {"summary": json.loads((path / "summary.json").read_text())}
    for name in ("cells", "decomposition", "level_residuals", "primary", "rivals", "crossover"):
        with (path / (name + ".csv")).open(newline="") as stream:
            rows = list(csv.DictReader(stream))
        for row in rows:
            for key, value in row.items():
                if value == "":
                    row[key] = None
                else:
                    try:
                        row[key] = float(value)
                    except ValueError:
                        pass
        result[name] = rows
    return result


def cli_run(bench, energy, config, selections):
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory)
        est.write_csv(path / "bench.csv", est.BENCH_COLUMNS, bench)
        est.write_csv(path / "energy.csv", est.ENERGY_COLUMNS, energy)
        (path / "config.json").write_text(json.dumps(config))
        (path / "selections.json").write_text(json.dumps(selections))
        command = [sys.executable, str(ROOT / "scripts/difficulty_estimate.py"), "--config", str(path / "config.json"),
                   "--selections", str(path / "selections.json"), "--bench", str(path / "bench.csv"),
                   "--energy", str(path / "energy.csv"), "--out", str(path / "out")]
        result = subprocess.run(command, capture_output=True, text=True, env=os.environ.copy())
        if result.returncode:
            raise AssertionError(result.stderr)
        return read_outputs(path / "out")


class FloatAssertions(unittest.TestCase):
    def assertFloatClose(self, actual, expected):
        # COMMON/revision 2.3: 1e-6 relative, or 1e-6 in the column unit near
        # zero, for a numerical re-derivation. Both exceed 1e6 * double noise
        # (2.2e-16 * 1e6 = 2.2e-10 relative); no decimal-place rounding bar.
        self.assertTrue(math.isclose(actual, expected, rel_tol=1e-6, abs_tol=1e-6),
                        f"{actual!r} != {expected!r}")


class AcceptanceTests(FloatAssertions):
    def test_A_wilson(self):
        p, lo, hi = est.wilson(15, 20)
        self.assertFloatClose(p, .75)
        self.assertFloatClose(lo, .531299)
        self.assertFloatClose(hi, .888138)
        self.assertFloatClose(est.wilson(20, 20)[1], .838875)
        self.assertFloatClose(est.wilson(20, 20)[2], 1)
        self.assertFloatClose(est.wilson(0, 20)[1], 0)
        self.assertFloatClose(est.wilson(0, 20)[2], .161125)

    def test_B_mean_energy(self):
        avg, lo, hi = est.mean_interval(ENERGIES)
        self.assertFloatClose(avg, 140)
        self.assertFloatClose(lo, 100.7351)
        self.assertFloatClose(hi, 179.2649)

    def test_C_energy_per_correct(self):
        # §6 MOVER pins re-derived from t(.975,4)=2.7764451051977987 and
        # Wilson(.95); six decimals avoid the old three-decimal rounding gaps.
        result = est.energy_per_correct(15, 20, ENERGIES)
        self.assertEqual(result["epc_status"], "ok")
        self.assertFloatClose(result["epc_j"], 186.6667)
        self.assertFloatClose(result["epc_lo_j"], 128.934010)
        self.assertFloatClose(result["epc_hi_j"], 285.303377)
        result = est.energy_per_correct(20, 20, ENERGIES)
        self.assertFloatClose(result["epc_j"], 140)
        self.assertFloatClose(result["epc_lo_j"], 100.735137)
        self.assertFloatClose(result["epc_hi_j"], 189.603682)

    def test_D_joules_per_token(self):
        ratio, lo, hi = est.joules_per_token(ENERGIES, TOKENS)
        self.assertFloatClose(ratio, 1.75)
        self.assertFloatClose(lo, 1.610097)
        self.assertFloatClose(hi, 1.889903)

    def test_E_exact_decomposition(self):
        fit, residuals = est.decomposition(ols_rows())
        self.assertEqual(fit["status"], "ok")
        for key, expected in (("a_j", 10), ("b_prompt_j_per_tok", .5), ("b_gen_j_per_tok", 1.5), ("r2", 1)):
            self.assertFloatClose(fit[key], expected)
        self.assertFloatClose(fit["gen_share"], .641860)
        self.assertFloatClose(fit["r2_gen_only"], .910222)
        self.assertFloatClose(residuals[0]["mean_residual_j"], 0)
        self.assertFloatClose(residuals[0]["lo_j"], 0)
        self.assertFloatClose(residuals[0]["hi_j"], 0)
        self.assertEqual(residuals[0]["contains_zero"], 1)

    def test_F_noisy_decomposition(self):
        rows = ols_rows([2, -1, 0, -2, 1, 0])
        fit, residuals = est.decomposition(rows)
        for key, expected in (("a_j", 13.980831), ("a_se", 3.137012),
                              ("b_prompt_j_per_tok", .465176), ("b_prompt_se", .027441),
                              ("b_gen_j_per_tok", 1.497284), ("b_gen_se", .031545), ("r2", .999164)):
            self.assertFloatClose(fit[key], expected)
        residual = [row["energy_j"] - (fit["a_j"] + fit["b_prompt_j_per_tok"]*row["prompt_tokens"]
                    + fit["b_gen_j_per_tok"]*row["generated_tokens"]) for row in rows]
        self.assertFloatClose(sum(value*value for value in residual), 6.060703)
        avg = sum(row["energy_j"] for row in rows)/6
        self.assertFloatClose(sum((row["energy_j"]-avg)**2 for row in rows), 7250.833)
        self.assertFloatClose(est.student_t_quantile(.975, 3), 3.182446)
        self.assertEqual(residuals[0]["contains_zero"], 1)
        half = est.student_t_quantile(.975, 5) * math.sqrt(sum(v*v for v in residual) / (5*6))
        self.assertFloatClose(residuals[0]["hi_j"], half)

    def test_F_prime_coefficient_intervals(self):
        fit, _ = est.decomposition(ols_rows([2, -1, 0, -2, 1, 0]))
        for key, expected in (("a_lo_j", 3.997459), ("a_hi_j", 23.964202),
                              ("b_prompt_lo", .377846), ("b_prompt_hi", .552506),
                              ("b_gen_lo", 1.396896), ("b_gen_hi", 1.597673)):
            self.assertFloatClose(fit[key], expected)
        for rows in (ols_rows()[:3], [energy_row(i) for i in range(4)]):
            fit, _ = est.decomposition(rows)
            self.assertIsNone(fit["a_lo_j"])
            self.assertIsNone(fit["b_gen_hi"])

    def test_H_student_t(self):
        for df, expected in ((3, 3.182446305), (4, 2.776445105), (9, 2.262157163),
                             (19, 2.093024054), (29, 2.045229642)):
            with self.subTest(df=df):
                self.assertFloatClose(est.student_t_quantile(.975, df), expected)
        self.assertFloatClose(est.student_t_quantile(.5, 4), 0)
        self.assertFloatClose(est.student_t_quantile(.025, 4), -2.776445105)
        self.assertFloatClose(est.student_t_quantile(.75, 1), 1)

    def test_nonestimable_and_nonpositive_lower(self):
        self.assertEqual(est.energy_per_correct(0, 20, ENERGIES)["epc_status"], "not_estimable_zero_correct")
        few = est.energy_per_correct(15, 20, [100])
        self.assertEqual(few["epc_status"], "not_estimable_few_attempts")
        self.assertIsNone(few["epc_j"])
        self.assertIsNone(few["mean_energy_j"])
        result = est.energy_per_correct(15, 20, [1, 100])
        self.assertEqual(result["epc_status"], "energy_lower_nonpositive")
        self.assertFloatClose(result["epc_lo_j"], 0)
        # A nonzero energy spread makes the registered MOVER upper bound exceed its point.
        self.assertGreater(result["epc_hi_j"], result["epc_j"])
        self.assertEqual(est.joules_per_token([100], [20]), (None, None, None))
        self.assertEqual(est.joules_per_token([100, 120], [0, 0]), (None, None, None))
        self.assertEqual(est.decomposition(ols_rows()[:3])[0]["status"], "few_rows")
        self.assertEqual(est.decomposition([energy_row(i) for i in range(4)])[0]["status"], "singular")
        linear = [energy_row(i, prompt_tokens=100+i, generated_tokens=2*(100+i)+1) for i in range(4)]
        self.assertEqual(est.decomposition(linear)[0]["status"], "singular")
        singleton_levels = ols_rows()
        for index, row in enumerate(singleton_levels):
            row["level"] = index % 5 + 1
        _, residuals = est.decomposition(singleton_levels)
        self.assertEqual(residuals[1]["m"], 1)
        self.assertFloatClose(residuals[1]["mean_residual_j"], 0)
        self.assertIsNone(residuals[1]["lo_j"])
        self.assertIsNone(residuals[1]["contains_zero"])
        small_k = est.energy_per_correct(1, 20, ENERGIES)
        self.assertEqual(small_k["epc_status"], "ok")
        # Positive energy/accuracy uncertainty gives an upper bound above the point.
        self.assertGreater(small_k["epc_hi_j"], small_k["epc_j"])


class V2AcceptanceTests(FloatAssertions):
    def test_I_holdout_through_cli(self):
        ids = [f"i{i:02}" for i in range(1, 26)]
        config, selections = design({1: ids}, {1: ids[:5]})
        bench = [bench_row(i, item_id=item, correct=int(i == 1 or 6 <= i <= 20)) for i, item in enumerate(ids, 1)]
        energy = [energy_row(i, item_id=item, energy_j=value) for i, (item, value) in enumerate(zip(ids, ENERGIES), 1)]
        tables = cli_run(bench, energy, config, selections)
        row = cell(tables)
        self.assertEqual((row["n_bench"], row["k_correct"], row["n_holdout"], row["k_holdout"]), (25, 16, 20, 15))
        self.assertFloatClose(row["accuracy"], .64)
        # SPEC-v2 case I says "keeps its numbers", but 8.9 requires bootstrap primary bounds.
        # Its old [128.934, 285.303] pins therefore belong to the secondary MOVER columns.
        # For this seed (tests), B=200, 8.9 supports the primary bounds pinned below.
        for key, expected in (("epc_direct_j", 186.6667), ("epc_direct_lo_j", 128.934010),
                              ("epc_direct_hi_j", 285.303377)):
            self.assertFloatClose(row[key], expected)
        self.assertEqual(row["primary_source"], "direct")
        self.assertEqual(row["primary_reason"], "model_fit_singular")
        # These columns copy the same computed point: bit identity is required.
        self.assertEqual(row["epc_j"], row["epc_direct_j"])
        self.assertFloatClose(row["epc_lo_j"], 138.94736842105263)
        self.assertFloatClose(row["epc_hi_j"], 258.46153846153845)
        primary = next(r for r in tables["primary"] if r["variant"] == "primary" and r["level"] == 1)
        self.assertEqual(primary["status"], "unresolved_incomplete")
        # The comparison table copies this exact cell point without re-deriving it.
        self.assertEqual(primary["epc_a_j"], row["epc_j"])
        self.assertEqual(primary["reason"], "Y/off:not_measured")

    def test_L_model_points(self):
        rows = ols_rows()
        for i, row in enumerate(rows):
            row["level"] = i//3 + 1
        fit, _ = est.decomposition(rows)
        h1 = [bench_row(i, prompt_tokens=p, generated_tokens=g, correct=c)
              for i, (p, g, c) in enumerate(((100, 60, 1), (110, 80, 1), (90, 100, 0), (100, 40, 1)))]
        h2 = [bench_row(i, prompt_tokens=p, generated_tokens=g, correct=c)
              for i, (p, g, c) in enumerate(((130, 100, 1), (150, 120, 0)))]
        for h, mu, epc, direct in ((h1, 165, 220, 213.333333333333), (h2, 245, 490, 396.666666666667)):
            result = est.model_epc(fit, h, 3)
            self.assertEqual(result["epc_model_status"], "ok")
            self.assertFloatClose(result["model_energy_j"], mu)
            self.assertFloatClose(result["epc_model_j"], epc)
            en = rows[:3] if h is h1 else rows[3:]
            self.assertFloatClose(est.energy_per_correct(sum(r["correct"] for r in h), len(h), [r["energy_j"] for r in en])["epc_j"], direct)

    def test_M_misfit_through_cli(self):
        ps = [100,120,80,110, 105,125,85,115, 95,115,90,120, 110,100,85,125, 90,130,100,105]
        gs = [50,70,80,60, 75,55,90,65, 60,85,70,55, 80,65,75,90, 70,60,85,55]
        es = [141,169,175,150, 181,149,192.5,160, 160.5,206,172.5,164, 191,151.5,170,202.5, 166,159,192.5,140]
        energy = [energy_row(i, model="m", level=i//4+1, item_id=f"m{i//4+1}e{i%4}",
                    prompt_tokens=p, generated_tokens=g, energy_j=e) for i, (p, g, e) in enumerate(zip(ps, gs, es))]
        holdout = [bench_row(i, model="m", level=l, item_id=f"m{l}h{i}", prompt_tokens=100+5*i,
                            generated_tokens=60+5*i, correct=int(i != 5)) for l in range(1, 6) for i in range(6)]
        bench = holdout + [bench_row(model="m", item_id=r["item_id"], level=r["level"], prompt_tokens=r["prompt_tokens"],
                                      generated_tokens=r["generated_tokens"]) for r in energy]
        config, selections = design({l: [r["item_id"] for r in bench if r["level"] == l] for l in range(1, 6)},
            {l: [r["item_id"] for r in energy if r["level"] == l] for l in range(1, 6)}, models=("m", "absent"), seed="case-M")
        tables = cli_run(bench, energy, config, selections)
        fit = next(r for r in tables["decomposition"] if r["variant"] == "primary")
        for key, expected in (("a_j", 33.503039), ("b_prompt_j_per_tok", .271248), ("b_gen_j_per_tok", 1.542626)):
            self.assertFloatClose(fit[key], expected)
        pins = [(-5.748090, .946453), (-4.415225, 1.460235), (5.579092, 11.109952), (-6.475269, 2.171315), (-5.407524, .914395)]
        residuals = [r for r in tables["level_residuals"] if r["variant"] == "primary"]
        for r, (lo, hi) in zip(residuals, pins):
            self.assertFloatClose(r["boot_lo_j"], lo)
            self.assertFloatClose(r["boot_hi_j"], hi)
            self.assertEqual(r["misfit"], int(r["level"] == 3))
        for l in range(1, 6):
            r = cell(tables, "m", l)
            self.assertFloatClose(r["model_energy_j"], 175.858766)
            self.assertFloatClose(r["epc_model_j"], 211.030519)
            self.assertEqual(r["primary_source"], "direct" if l == 3 else "model")
        r = cell(tables, "m", 3)
        self.assertEqual(r["primary_reason"], "misfit")
        self.assertFloatClose(r["epc_j"], 210.9)
        self.assertFloatClose(r["epc_lo_j"], 162.25)
        self.assertFloatClose(r["epc_hi_j"], 518.25)
        self.assertEqual(tables["summary"]["variants"]["primary"]["rails"]["misfit_cells"], ["m/off:3"])

    def test_N_primary_through_cli(self):
        models = ("qwen3-1.7b", "qwen3-4b")
        noise = (-4,-3,4,3,3,4,-3,-4)
        bench, energy = [], []
        for model, scale in zip(models, (1, 2)):
            for l in (1, 2):
                for i in range(8):
                    p, g = 60+7*i+20*l, 100*l+37*((5*i)%8)+40*(l-1)
                    e = repr(round(scale*(20+.05*p+.4*g+noise[i]), 6))
                    energy.append(energy_row(model=model, item_id=f"e{l}{i:02}", level=l, prompt_tokens=p, generated_tokens=g, energy_j=e))
                    bench.append(bench_row(model=model, item_id=f"e{l}{i:02}", level=l, prompt_tokens=p, generated_tokens=g))
                wrong = ({11} if l == 1 else {1,4,6,9}) if model == models[0] else (set() if l == 1 else {3,8})
                for i in range(12):
                    bench.append(bench_row(model=model, item_id=f"h{l}{i:02}", level=l, prompt_tokens=62+6*i+20*l,
                                          generated_tokens=100*l+31*((7*i)%12)+40*(l-1), correct=int(i not in wrong)))
        config, selections = design({l: [r["item_id"] for r in bench if r["model"] == models[0] and r["level"] == l] for l in (1,2)},
            {l: [r["item_id"] for r in energy if r["model"] == models[0] and r["level"] == l] for l in (1,2)}, models, seed="case-N")
        config["configurations"][1]["status"] = "measured"
        tables = cli_run(bench, energy, config, selections)
        pins = [(models[0], 1, 133.95, 146.127273, 112.843767, 194.765079, 127.663636),
                (models[0], 2, 190.95, 286.425, 202.676733, 465.784376, 261.0375),
                (models[1], 1, 267.9, 267.9, 223.119116, 318.065197, 234.05),
                (models[1], 2, 381.9, 458.28, 350.592955, 658.884550, 417.66)]
        for model, l, mu, point, lo, hi, direct in pins:
            r = cell(tables, model, l)
            self.assertEqual((r["cell_status"], r["primary_source"], r["epc_model_status"]), ("complete", "model", "ok"))
            for key, expected in (("model_energy_j", mu), ("epc_model_j", point), ("epc_model_lo_j", lo),
                                  ("epc_model_hi_j", hi), ("epc_direct_j", direct)):
                self.assertFloatClose(r[key], expected)
        residual_pins = {models[0]: [(-1.459451, 1.241493), (-1.241493, 1.459451)],
                         models[1]: [(-2.730711, 2.264987), (-2.264987, 2.730711)]}
        for r in tables["level_residuals"]:
            if r["variant"] == "primary":
                lo, hi = residual_pins[r["model"]][int(r["level"])-1]
                self.assertFloatClose(r["boot_lo_j"], lo)
                self.assertFloatClose(r["boot_hi_j"], hi)
                self.assertEqual(r["misfit"], 0)
        comparison_pins = [(-.606136, -.963820, -.239224, -1.037935, -.101456, "resolved"),
                           (-.470004, -.945010, .045545, -1.002726, .507957, "unresolved")]
        for r, pins in zip([r for r in tables["primary"] if r["variant"] == "primary" and r["level"] <= 2], comparison_pins):
            for key, expected in zip(("log_ratio", "desc_lo", "desc_hi", "dec_lo", "dec_hi"), pins[:5]):
                self.assertFloatClose(r[key], expected)
            self.assertEqual(r["status"], pins[5])
        self.assertEqual(tables["summary"]["variants"]["primary"]["rails"]["primary_question"]["verdict"], "no_resolved_change")

    def test_O_two_confidences_percentiles_and_verdicts(self):
        values = [b/100-.03 for b in range(1, 201)]
        r = est.compare_replicates(.975, values, .95, .99)
        for key, expected in (("desc_lo", .02), ("desc_hi", 1.93), ("dec_lo", -.02), ("dec_hi", 1.97)):
            self.assertFloatClose(r[key], expected)
        self.assertEqual(r["status"], "unresolved")
        self.assertEqual(est.percentile(list(range(1, 41)), .95), (1,40))
        self.assertEqual(est.percentile(list(range(1, 41)), .5), (10,31))
        self.assertEqual(est.percentile(list(range(1, 4001)), .95), (100,3901))
        self.assertEqual(est.percentile(list(range(1, 4001)), .99), (20,3981))
        a = est.compare_replicates(-1, [-1]*200, .95, .99) | {"level": 1, "cheaper": "a"}
        b = est.compare_replicates(1, [1]*200, .95, .99) | {"level": 2, "cheaper": "b"}
        self.assertEqual(est.primary_verdict([a,b])["verdict"], "cheaper_size_changes_with_level")
        b["status"] = "unresolved"
        self.assertEqual(est.primary_verdict([a,b])["verdict"], "no_resolved_change")
        self.assertEqual(est.crossover_verdict([{"level":1, "cheapest":"a", "status":"resolved"},
            {"level":2, "cheapest":"b", "status":"resolved"}])["verdict"], "crossover_resolved")

    def test_P1_P2_incomplete_rivals(self):
        ids = [f"i{i:03}" for i in range(200)]
        config, selections = design({1: ids}, {1: ids[:20]}, models=("A", "B"))
        config["configurations"][1]["status"] = "measured"
        for zero_correct, energy_count, reason in ((True, 20, "B/off:not_estimable_zero_correct"),
                                                  (False, 1, "B/off:short"), (False, 0, "B/off:short")):
            with self.subTest(reason=reason, m=energy_count):
                bench = [bench_row(model=model, item_id=item, correct=int(not (model == "B" and zero_correct)))
                         for model in ("A", "B") for item in ids]
                energy = [energy_row(model=model, item_id=item, energy_j=100 if model == "A" else 1)
                          for model in ("A", "B") for item in ids[:20 if model == "A" else energy_count]]
                tables = est.estimate_tables(bench, energy, config, selections)
                secondary = next(r for r in tables["crossover"] if r["variant"] == "primary" and r["level"] == 1)
                self.assertEqual((secondary["status"], secondary["cheapest"], secondary["incomplete"]), ("unresolved_incomplete", "A/off", reason))
                rival = next(r for r in tables["rivals"] if r["variant"] == "primary" and r["level"] == 1)
                self.assertEqual(rival["reason"], reason)
                self.assertIsNone(rival["dec_lo"])
                self.assertEqual(next(r for r in tables["primary"] if r["variant"] == "primary" and r["level"] == 1)["status"], "unresolved_incomplete")

    def test_P3_P4_retries_duplicates_and_counts(self):
        ids = [f"i{i:02}" for i in range(25)]
        config, selections = design({1: ids}, {1: ids[:2]})
        bench = [bench_row(item_id=item) for item in ids]
        energy = [energy_row(item_id=ids[0], flags="runtime_failed"), energy_row(item_id=ids[0], attempt=2), energy_row(item_id=ids[1])]
        tables = est.estimate_tables(bench, energy, config, selections)
        r = cell(tables)
        self.assertEqual((r["m_energy"], r["n_holdout"], r["replaced_rows"], r["rows_not_used"], r["cell_status"]), (2,23,1,1,"complete"))
        self.assertNotIn("duplicate", tables["summary"]["flag_counts"]["energy"])
        energy.append(energy_row(item_id=ids[1], attempt=2))
        tables = est.estimate_tables(bench, energy, config, selections)
        self.assertEqual(cell(tables)["m_energy"], 2)
        self.assertEqual(tables["summary"]["flag_counts"]["energy"]["duplicate"], 1)
        # Same-attempt duplicates use file order; blank attempts cannot participate.
        parsed = est.parse_energy(energy + [energy_row(item_id=ids[0], attempt=2), energy_row(item_id=ids[0], attempt="")],
                                  est.parse_bench(bench, config, selections), config, selections)
        self.assertIn("duplicate", parsed[-2]["flags"])
        self.assertNotIn("duplicate", parsed[-1]["flags"])
        bench[0]["flags"] = "runtime_failed"
        bench.append(bench_row(item_id=ids[0], attempt=2))
        self.assertEqual(cell(est.estimate_tables(bench, energy[:3], config, selections))["n_bench"], 25)

    def test_P5_optional_absent_present_stream_independence(self):
        ids = {l: [f"l{l}i{i}" for i in range(10)] for l in range(1,6)}
        config, selections = design(ids, {l: values[:4] for l, values in ids.items()}, models=("X", "Y"), b=20)
        config["configurations"][1]["status"] = "measured"
        bench = [bench_row(model=model, level=l, item_id=item) for model in ("X", "Y") for l in ids for item in ids[l]]
        energy = [energy_row(model=model, level=l, item_id=item, energy_j=100 if model=="X" else 300)
                  for model in ("X", "Y") for l in ids for item in ids[l][:4]]
        before = est.estimate_tables(bench, energy, config, selections)
        config["configurations"].append(dict(model="qwen3-8b", mode="on", output_cap=16384, status="optional"))
        config["sizes"]["on"] = copy.deepcopy(config["sizes"]["off"])
        selections["selections"]["on"] = copy.deepcopy(selections["selections"]["off"])
        absent = est.estimate_tables(bench, energy, config, selections)
        # Same code, inputs and seeded streams: an absent party must be bit-identical.
        self.assertEqual(absent["cells"], before["cells"])
        self.assertEqual(absent["primary"], before["primary"])
        self.assertEqual(absent["summary"]["roster"]["qwen3-8b/on"], "not_measured")
        self.assertFalse(any(r["rival"] == "qwen3-8b/on" for r in absent["rivals"]))
        bench.append(bench_row(model="qwen3-8b", mode="on", level=1, item_id=ids[1][0]))
        present = est.estimate_tables(bench, energy, config, selections)
        # Optional-party activation must leave the existing parties' seeded streams identical.
        self.assertEqual(present["primary"], before["primary"])
        self.assertEqual(present["summary"]["roster"]["qwen3-8b/on"], "optional")
        for r in present["crossover"]:
            self.assertEqual(r["status"], "unresolved_incomplete")
            self.assertIn("qwen3-8b/on:" + ("short" if r["level"] == 1 else "missing"), r["incomplete"])
        optional_cells = [r for r in present["cells"] if r["model"] == "qwen3-8b"]
        self.assertEqual([r["cell_status"] for r in optional_cells[:5]], ["short"]+["missing"]*4)

    def test_Q_physical_variants_and_retry(self):
        ids = [f"i{i}" for i in range(10)]
        config, selections = design({1: ids}, {1: ids[:5]})
        bench = [bench_row(i) for i in range(10)]
        energy = [energy_row(i, energy_j=1000 if i == 4 else 10, flags="contention_above_level" if i == 4 else "") for i in range(5)]
        tables = est.estimate_tables(bench, energy, config, selections)
        self.assertEqual((cell(tables)["m_energy"], cell(tables)["cell_status"]), (4,"short"))
        self.assertFloatClose(cell(tables)["mean_energy_j"], 10)
        self.assertEqual(cell(tables, variant="flagged_inclusive")["m_energy"], 5)
        self.assertFloatClose(cell(tables, variant="flagged_inclusive")["mean_energy_j"], 208)
        energy.append(energy_row(4, attempt=2, energy_j=12))
        tables = est.estimate_tables(bench, energy, config, selections)
        r = cell(tables)
        self.assertEqual((r["m_energy"], r["replaced_rows"], r["cell_status"]), (5,1,"complete"))
        self.assertFloatClose(r["mean_energy_j"], 10.4)
        self.assertFloatClose(cell(tables, variant="flagged_inclusive")["mean_energy_j"], 208)
        energy[4]["flags"] = "contention"
        tables = est.estimate_tables(bench, energy[:5], config, selections)
        for variant in est.VARIANTS:
            self.assertFloatClose(cell(tables, variant=variant)["mean_energy_j"], 208)
        # A physical flag on a bench attempt also uses the first inclusive attempt.
        bench[7]["flags"] = "sleep"
        bench.append(bench_row(7, attempt=2, correct=0))
        tables = est.estimate_tables(bench, energy[:5], config, selections)
        self.assertEqual((cell(tables)["k_holdout"], cell(tables, variant="flagged_inclusive")["k_holdout"]), (4,5))


class TableTests(FloatAssertions):
    def setUp(self):
        self.config, self.selections = design({1: [f"i{i}" for i in range(8)]}, {1: [f"i{i}" for i in range(5)]}, b=20)

    def parse(self, *rows, bench=None):
        return est.parse_energy(rows, est.parse_bench(bench or [bench_row()], self.config, self.selections), self.config, self.selections)

    def test_parse_numbers_selection_boundary_and_recorded_flags(self):
        for value in (0, -1, "nan", "inf", "-inf", "", "abc", None):
            self.assertIn("bad_number", self.parse(energy_row(energy_j=value))[0]["flags"])
        for key in ("prompt_tokens", "generated_tokens", "attempt"):
            for value in (-1, "1.5", True, None, "", "1.0", "١", "++1"):
                with self.subTest(key=key, value=value):
                    self.assertIn("bad_number", self.parse(energy_row(**{key:value}))[0]["flags"])
        for level in (0, 6, "1.0", None, "١"):
            self.assertIn("bad_level", self.parse(energy_row(level=level))[0]["flags"])
        self.assertIn("bad_mode", self.parse(energy_row(mode="auto"))[0]["flags"])
        self.assertIn("unknown_config", self.parse(energy_row(model="unknown"))[0]["flags"])
        self.assertIn("unknown_boundary", self.parse(energy_row(boundary="cpu"))[0]["flags"])
        self.assertIn("not_selected", self.parse(energy_row(level=2))[0]["flags"])
        self.assertIn("not_in_bench", self.parse(energy_row(1))[0]["flags"])
        self.assertIn("token_mismatch", self.parse(energy_row(generated_tokens=21))[0]["flags"])
        for value in ("abc", "12.0", "١"):
            self.assertEqual(self.parse(energy_row(generated_tokens=value))[0]["flags"], {"bad_number"})
            self.assertNotIn("token_mismatch", self.parse(energy_row(), bench=[bench_row(generated_tokens=value)])[0]["flags"])
        self.assertEqual(est._integer(" +12 "), 12)
        for key in ("correct", "cap_hit"):
            self.assertIn("bad_number", est.parse_bench([bench_row(**{key:2})], self.config, self.selections)[0]["flags"])

    def test_selection_defined_holdout_targets_missing_rows_and_two_boundaries(self):
        bench = [bench_row(i) for i in range(8)]
        energy = [energy_row(0), energy_row(1, energy_j="nan"), energy_row(2, flags="sleep"), energy_row(3, flags="runtime_failed")]
        self.config["boundaries"] = ["wall", "rails"]
        tables = est.estimate_tables(bench, energy, self.config, self.selections)
        for boundary in self.config["boundaries"]:
            r = cell(tables, boundary=boundary)
            self.assertEqual((r["n_holdout"], r["n_holdout_target"], r["m_energy_target"]), (3,3,5))
            self.assertEqual(r["m_energy"], 1 if boundary == "rails" else 0)
            self.assertEqual(r["cell_status"], "short")
        self.selections["selections"]["off"]["energy"]["1"].pop()
        tables = est.estimate_tables(bench, energy, self.config, self.selections)
        self.assertIn("selection_size_mismatch:off:energy:1", tables["summary"]["selection_size_mismatch"])
        self.assertEqual(cell(tables)["m_energy_target"], 5)
        empty = est.estimate_tables([], [], self.config, self.selections)
        self.assertEqual(len(empty["cells"]), 20)
        self.assertTrue(all(r["cell_status"] == "missing" for r in empty["cells"] if r["level"] == 1))

    def test_always_exclusions_counts_cap_loop_and_nonexcluding_flags(self):
        bench = [bench_row(i, flags="repetition_loop" if i == 6 else "", cap_hit=int(i == 7)) for i in range(8)]
        energy = [energy_row(0), energy_row(1, flags="contention;battery_assist"), energy_row(2, generated_tokens=21),
                  energy_row(3, flags="unknown_item"), energy_row(4, energy_j="nan"), energy_row(0),
                  energy_row(0, attempt=2), energy_row(3, level=9), energy_row(4, mode="auto")]
        tables = est.estimate_tables(bench, energy, self.config, self.selections)
        r = cell(tables)
        self.assertEqual((r["m_energy"], r["token_mismatch_count"], r["rows_not_used"]), (3,1,4))
        self.assertFloatClose(r["loop_rate_bench"], 1/8)
        self.assertFloatClose(r["cap_hit_rate_bench"], 1/8)
        self.assertEqual(tables["summary"]["flag_counts"]["energy"]["duplicate"], 3)
        self.assertEqual(tables["decomposition"][-1]["N"], 3)

    def test_bootstrap_invalid_infinity_and_model_statuses(self):
        er = ols_rows()[:4]
        h = [bench_row(i, correct=int(i == 0)) for i in range(4)]
        config = copy.deepcopy(self.config)
        config["bootstrap"] = {"seed":"invalid", "replicates":200}
        reps = est.bootstrap({1: er}, {1:h}, config, "primary", "rails", "X", "off")
        # Invalid-replicate counts are integers: at least one exercises the invalid path.
        self.assertGreater(reps[1]["invalid"], 0)
        self.assertIn(math.inf, reps[1]["direct"])
        fit, _ = est.decomposition(er)
        self.assertEqual(est.model_epc(fit, h, 4, reps[1]["invalid"])["epc_model_status"], "bootstrap_invalid")
        self.assertEqual(est.model_epc(fit, h, 1)["epc_model_status"], "few_attempts")
        self.assertEqual(est.model_epc(fit, [], 4)["epc_model_status"], "zero_correct")
        negative = fit | {"a_j":-10000}
        self.assertEqual(est.model_epc(negative, h, 4)["epc_model_status"], "nonpositive")
        self.assertEqual(est.log_ratio_replicates([math.inf, math.inf, 1], [math.inf, 1, math.inf]), [0,math.inf,-math.inf])
        self.assertEqual(est.percentile([1]*19+[math.inf], .95), (1,math.inf))
        other = est.bootstrap({1:list(reversed(er))}, {1:list(reversed(h))}, config, "primary", "rails", "X", "off")
        # Sorting restores identical inputs to the same code and seeded stream.
        self.assertEqual(reps, other)

    def test_cli_outputs_data_errors_usage_config_and_unreadable_inputs(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            est.write_csv(path / "bench.csv", est.BENCH_COLUMNS, [bench_row(correct="abc", level="١")])
            est.write_csv(path / "energy.csv", est.ENERGY_COLUMNS, [energy_row(energy_j="nan")])
            (path / "config.json").write_text(json.dumps(self.config))
            (path / "selections.json").write_text(json.dumps(self.selections))
            command = [sys.executable, str(ROOT / "scripts/difficulty_estimate.py"), "--config", str(path / "config.json"),
                "--selections", str(path / "selections.json"), "--bench", str(path / "bench.csv"),
                "--energy", str(path / "energy.csv"), "--out", str(path / "out")]
            def run(args=command):
                return subprocess.run(args, capture_output=True, text=True, env=os.environ.copy())
            result = run()
            self.assertEqual(result.returncode, 0, result.stderr)
            expected = {name+'.csv' for name in ("cells", "decomposition", "level_residuals", "primary", "rivals", "crossover")} | {"summary.json"}
            self.assertEqual({p.name for p in (path/"out").iterdir()}, expected)
            for name, columns in (("cells", est.CELL_COLUMNS), ("decomposition", est.DECOMPOSITION_COLUMNS),
                ("level_residuals", est.RESIDUAL_COLUMNS), ("primary", est.PRIMARY_COLUMNS), ("rivals", est.RIVAL_COLUMNS),
                ("crossover", est.CROSSOVER_COLUMNS)):
                data = (path / "out" / (name+'.csv')).read_bytes()
                self.assertNotIn(b"\r", data)
                self.assertEqual(data.decode().splitlines()[0], ','.join(columns))
            summary = read_outputs(path/"out")["summary"]
            # Untransformed config copies must preserve their exact input bits.
            self.assertEqual((summary["descriptive_confidence"], summary["decision_confidence"]), (.95,.99))
            self.assertEqual(summary["flag_counts"]["bench"]["bad_level"], 1)
            self.assertEqual(summary["flag_counts"]["energy"]["bad_number"], 1)
            self.assertEqual(run(command+["--confidence", ".95"]).returncode, 2)
            self.assertEqual(run(command+["--exclude-flags", ""]).returncode, 2)
            missing = command.copy()
            missing[missing.index("--bench")+1] = str(path/"absent.csv")
            self.assertEqual(run(missing).returncode, 1)
            (path / "selections.json").write_text("not JSON")
            self.assertEqual(run().returncode, 0)
            (path / "config.json").write_text(json.dumps(self.config | {"confidence": .95}))
            self.assertEqual(run().returncode, 2)


if __name__ == "__main__":
    unittest.main()
