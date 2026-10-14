"""Specification cases A-I, parse flags, exclusion, and estimator CLI."""
import csv
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from joulewise.packs.difficulty import estimators as est
from joulewise.packs.difficulty.config import load_config

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/difficulty/pack_config.json"
ENERGIES = [100, 120, 140, 160, 180]
TOKENS = [50, 70, 80, 90, 110]


def bench_row(index=0, **changes):
    return dict(model="X", mode="off", item_id=f"i{index}", level=1, outcome="correct",
                correct=1, prompt_tokens=100, generated_tokens=20, cap_hit=0, flags="") | changes


def energy_row(index=0, **changes):
    return dict(model="X", mode="off", item_id=f"i{index}", level=1, boundary="rails",
                energy_j=100, prompt_tokens=100, generated_tokens=20, flags="") | changes


def ols_rows(noise=None):
    p, g = [100, 120, 80, 150, 110, 90], [50, 70, 80, 90, 110, 60]
    return [energy_row(index, prompt_tokens=x, generated_tokens=y, energy_j=10+.5*x+1.5*y+z)
            for index, (x, y, z) in enumerate(zip(p, g, noise or [0]*6))]


class AcceptanceTests(unittest.TestCase):
    def test_A_wilson(self):
        p, lo, hi = est.wilson(15, 20)
        self.assertEqual(p, .75)
        self.assertAlmostEqual(lo, .531299, places=6)
        self.assertAlmostEqual(hi, .888138, places=6)
        self.assertAlmostEqual(est.wilson(20, 20)[1], .838875, places=6)
        self.assertEqual(est.wilson(20, 20)[2], 1)
        self.assertEqual(est.wilson(0, 20)[1], 0)
        self.assertAlmostEqual(est.wilson(0, 20)[2], .161125, places=6)

    def test_B_mean_energy(self):
        avg, lo, hi = est.mean_interval(ENERGIES)
        self.assertEqual(avg, 140)
        self.assertAlmostEqual(lo, 100.7351, places=4)
        self.assertAlmostEqual(hi, 179.2649, places=4)

    def test_C_energy_per_correct(self):
        result = est.energy_per_correct(15, 20, ENERGIES)
        self.assertEqual(result["epc_status"], "ok")
        self.assertAlmostEqual(result["epc_j"], 186.6667, places=4)
        self.assertAlmostEqual(result["epc_lo_j"], 128.934, places=3)
        self.assertAlmostEqual(result["epc_hi_j"], 285.303, places=3)
        result = est.energy_per_correct(20, 20, ENERGIES)
        self.assertEqual(result["epc_j"], 140)
        self.assertAlmostEqual(result["epc_lo_j"], 100.735, places=3)
        self.assertAlmostEqual(result["epc_hi_j"], 189.604, places=3)

    def test_D_joules_per_token(self):
        ratio, lo, hi = est.joules_per_token(ENERGIES, TOKENS)
        self.assertEqual(ratio, 1.75)
        self.assertAlmostEqual(lo, 1.610097, places=6)
        self.assertAlmostEqual(hi, 1.889903, places=6)

    def test_E_exact_decomposition(self):
        fit, residuals = est.decomposition(ols_rows())
        self.assertEqual(fit["status"], "ok")
        for key, expected in (("a_j", 10), ("b_prompt_j_per_tok", .5), ("b_gen_j_per_tok", 1.5), ("r2", 1)):
            self.assertAlmostEqual(fit[key], expected, places=12)
        self.assertAlmostEqual(fit["gen_share"], .641860, places=6)
        self.assertAlmostEqual(fit["r2_gen_only"], .910222, places=6)
        self.assertEqual(residuals[0]["mean_residual_j"], 0)
        self.assertEqual(residuals[0]["lo_j"], 0)
        self.assertEqual(residuals[0]["hi_j"], 0)
        self.assertEqual(residuals[0]["contains_zero"], 1)

    def test_F_noisy_decomposition(self):
        rows = ols_rows([2, -1, 0, -2, 1, 0])
        fit, residuals = est.decomposition(rows)
        for key, expected in (("a_j", 13.980831), ("a_se", 3.137012),
                              ("b_prompt_j_per_tok", .465176), ("b_prompt_se", .027441),
                              ("b_gen_j_per_tok", 1.497284), ("b_gen_se", .031545), ("r2", .999164)):
            self.assertAlmostEqual(fit[key], expected, places=6)
        residual = [row["energy_j"] - (fit["a_j"] + fit["b_prompt_j_per_tok"]*row["prompt_tokens"]
                    + fit["b_gen_j_per_tok"]*row["generated_tokens"]) for row in rows]
        self.assertAlmostEqual(sum(value*value for value in residual), 6.060703, places=6)
        avg = sum(row["energy_j"] for row in rows)/6
        self.assertAlmostEqual(sum((row["energy_j"]-avg)**2 for row in rows), 7250.833, places=3)
        self.assertAlmostEqual(est.student_t_quantile(.975, 3), 3.182446, places=6)
        self.assertEqual(residuals[0]["contains_zero"], 1)
        half = est.student_t_quantile(.975, 5) * math.sqrt(sum(v*v for v in residual) / (5*6))
        self.assertAlmostEqual(residuals[0]["hi_j"], half, places=12)

    def test_G_crossover(self):
        cells = [dict(model=model, mode="off", epc_j=point, epc_lo_j=lo, epc_hi_j=hi, epc_status="ok")
                 for model, point, lo, hi in (("X", 100, 80, 125), ("Y", 200, 160, 250), ("Z", 110, 85, 140))]
        result = est.crossover(cells)
        self.assertEqual(result, {"cheapest": "X/off", "cheapest_epc_j": 100, "status": "unresolved", "tied": "Z/off"})
        first = dict(level=1, **est.crossover(cells[:2]))
        self.assertEqual(first["status"], "resolved")
        last = dict(level=5, cheapest="Y/off", status="resolved")
        self.assertEqual(est.crossover_verdict([first, last])["verdict"], "crossover_resolved")
        last["status"] = "unresolved"
        self.assertEqual(est.crossover_verdict([first, last])["verdict"], "no_resolved_crossover")
        cells[1]["epc_lo_j"] = 0
        self.assertEqual(est.crossover(cells[:2])["tied"], "Y/off")
        self.assertEqual(est.crossover([])["status"], "none_estimable")

    def test_H_student_t(self):
        for df, expected in ((3, 3.182446305), (4, 2.776445105), (9, 2.262157163),
                             (19, 2.093024054), (29, 2.045229642)):
            with self.subTest(df=df):
                self.assertAlmostEqual(est.student_t_quantile(.975, df), expected, delta=1e-9)
        self.assertEqual(est.student_t_quantile(.5, 4), 0)
        self.assertAlmostEqual(est.student_t_quantile(.025, 4), -2.776445105, delta=1e-9)
        self.assertAlmostEqual(est.student_t_quantile(.75, 1), 1, delta=1e-12)

    def test_nonestimable_and_nonpositive_lower(self):
        self.assertEqual(est.energy_per_correct(0, 20, ENERGIES)["epc_status"], "not_estimable_zero_correct")
        few = est.energy_per_correct(15, 20, [100])
        self.assertEqual(few["epc_status"], "not_estimable_few_attempts")
        self.assertIsNone(few["epc_j"])
        self.assertIsNone(few["mean_energy_j"])
        result = est.energy_per_correct(15, 20, [1, 100])
        self.assertEqual(result["epc_status"], "energy_lower_nonpositive")
        self.assertEqual(result["epc_lo_j"], 0)
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
        self.assertEqual(residuals[1]["mean_residual_j"], 0)
        self.assertIsNone(residuals[1]["lo_j"])
        self.assertIsNone(residuals[1]["contains_zero"])
        small_k = est.energy_per_correct(1, 20, ENERGIES)
        self.assertEqual(small_k["epc_status"], "ok")
        self.assertGreater(small_k["epc_hi_j"], small_k["epc_j"])


class TableTests(unittest.TestCase):
    def parse(self, *rows):
        return est.parse_energy(rows, est.parse_bench([bench_row()]))

    def test_every_energy_parse_flag(self):
        for value in (0, -1, "nan", "inf", "-inf", "", "not-a-number", None):
            with self.subTest(energy=value):
                self.assertIn("bad_number", self.parse(energy_row(energy_j=value))[0]["flags"])
        for key in ("prompt_tokens", "generated_tokens"):
            for value in (-1, "1.5", True, None, "", "1.0", "١", "++1"):
                with self.subTest(key=key, value=value):
                    self.assertIn("bad_number", self.parse(energy_row(**{key: value}))[0]["flags"])
        for level in (0, 6, "1.0", None):
            self.assertIn("bad_level", self.parse(energy_row(level=level))[0]["flags"])
        self.assertIn("bad_mode", self.parse(energy_row(mode="auto"))[0]["flags"])
        self.assertIn("not_in_bench", self.parse(energy_row(item_id="missing"))[0]["flags"])
        self.assertIn("level_mismatch", self.parse(energy_row(level=2))[0]["flags"])
        self.assertIn("token_mismatch", self.parse(energy_row(generated_tokens=21))[0]["flags"])
        first, second, wall = self.parse(energy_row(), energy_row(), energy_row(boundary="wall"))
        self.assertNotIn("duplicate", first["flags"])
        self.assertIn("duplicate", second["flags"])
        self.assertNotIn("duplicate", wall["flags"])

    def test_token_comparison_requires_two_parsed_counts(self):
        for value in ("abc", "12.0", "١"):
            self.assertEqual(self.parse(energy_row(generated_tokens=value))[0]["flags"], {"bad_number"})
            bench = est.parse_bench([bench_row(generated_tokens=value)])
            self.assertEqual(est.parse_energy([energy_row()], bench)[0]["flags"], set())

    def test_holdout_uses_all_energy_items_for_same_model_and_mode(self):
        bench = [bench_row(i) for i in range(8)]
        energy = [energy_row(0), energy_row(1), energy_row(2, boundary="wall", flags="contention"),
                  energy_row(3, level=9), energy_row(4, energy_j="nan"),
                  energy_row(5, model="Y"), energy_row(6, mode="on")]
        tables = est.estimate_tables(bench, energy, exclude_flags=["contention"])
        cell = next(row for row in tables["cells"] if row["model"] == "X" and row["mode"] == "off")
        self.assertEqual((cell["n_bench"], cell["n_holdout"], cell["k_holdout"]), (8, 3, 3))
        cell = est.estimate_tables(bench[:2], energy[:2])["cells"][0]
        self.assertEqual((cell["n_holdout"], cell["k_holdout"]), (0, 0))
        self.assertEqual(cell["epc_status"], "not_estimable_zero_correct")
        self.assertIsNone(cell["epc_j"])

    def test_I_holdout_accuracy_through_cli(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            bench = [bench_row(i, item_id=f"i{i:02}", correct=int(i == 1 or 6 <= i <= 20))
                     for i in range(1, 26)]
            energy = [energy_row(i, item_id=f"i{i:02}", energy_j=value)
                      for i, value in enumerate(ENERGIES, 1)]
            est.write_csv(path / "bench.csv", est.BENCH_COLUMNS, bench)
            est.write_csv(path / "energy.csv", est.ENERGY_COLUMNS, energy)
            result = subprocess.run([sys.executable, str(ROOT / "scripts/difficulty_estimate.py"),
                                     "--bench", str(path / "bench.csv"), "--energy", str(path / "energy.csv"),
                                     "--out", str(path / "out")], capture_output=True, text=True,
                                    env=os.environ.copy())
            self.assertEqual(result.returncode, 0, result.stderr)
            with (path / "out/cells.csv").open(newline="") as stream:
                cell = next(csv.DictReader(stream))
            self.assertEqual((cell["n_bench"], cell["k_correct"], cell["accuracy"],
                              cell["n_holdout"], cell["k_holdout"]), ("25", "16", "0.64", "20", "15"))
            for key, expected, digits in (("epc_j", 186.6667, 4), ("epc_lo_j", 128.934, 3),
                                          ("epc_hi_j", 285.303, 3)):
                self.assertAlmostEqual(float(cell[key]), expected, delta=.5 * 10**-digits)

    def test_runtime_failed_cli_default_and_empty_override(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            bench = [bench_row(0), bench_row(1, correct=0, outcome="malformed", flags="runtime_failed")]
            est.write_csv(path / "bench.csv", est.BENCH_COLUMNS, bench)
            est.write_csv(path / "energy.csv", est.ENERGY_COLUMNS, [energy_row(2), energy_row(3)])
            self.assertEqual(est.estimate_tables(bench, [energy_row(2), energy_row(3)])["cells"][0]["n_bench"], 1)
            command = [sys.executable, str(ROOT / "scripts/difficulty_estimate.py"),
                       "--bench", str(path / "bench.csv"), "--energy", str(path / "energy.csv"),
                       "--out", str(path / "out")]
            for options, n, accuracy in (([], "1", "1.0"), (["--exclude-flags", ""], "2", "0.5")):
                result = subprocess.run(command + options, capture_output=True, text=True, env=os.environ.copy())
                self.assertEqual(result.returncode, 0, result.stderr)
                with (path / "out/cells.csv").open(newline="") as stream:
                    cell = next(csv.DictReader(stream))
                self.assertEqual((cell["n_bench"], cell["k_correct"], cell["accuracy"]), (n, "1", accuracy))
                summary = json.loads((path / "out/summary.json").read_text())
                self.assertEqual(summary["flag_counts"]["bench"]["runtime_failed"], 1)

    def test_exclusion_counts_and_default_use_of_adapter_flags(self):
        bench = [bench_row(i) for i in range(12)]
        energy = [energy_row(0), energy_row(1, flags="contention"), energy_row(2, flags="battery_assist"),
                  energy_row(3, generated_tokens=21), energy_row(4, energy_j="nan"),
                  energy_row(0), energy_row(5, flags="unknown_item"), energy_row(6, flags="unknown_config"),
                  energy_row(7, level=9), energy_row(8, mode="auto")]
        tables = est.estimate_tables(bench, energy, exclude_flags=["battery_assist"])
        cell = tables["cells"][0]
        self.assertEqual(cell["n_bench"], 12)
        self.assertEqual(cell["m_energy"], 3)
        self.assertEqual(cell["excluded_rows"], 5)
        self.assertEqual(cell["token_mismatch_count"], 1)
        self.assertEqual(tables["summary"]["flag_counts"]["energy"]["bad_level"], 1)
        self.assertEqual(tables["summary"]["flag_counts"]["energy"]["bad_mode"], 1)
        self.assertEqual(tables["decomposition"][0]["N"], 3)
        tables = est.estimate_tables(bench, energy)
        self.assertEqual(tables["cells"][0]["m_energy"], 4)

    def test_bench_exclusion_and_both_boundaries(self):
        bench = [bench_row(0), bench_row(1, flags="unknown_finish_reason", correct=0, outcome="malformed"),
                 bench_row(2, level=2)]
        bench.extend(bench_row(i+10, flags=flag) for i, flag in enumerate(
            ("unknown_item", "unknown_config", "duplicate", "bad_number", "missing_text", "contention")))
        energy = [energy_row(0), energy_row(1), energy_row(0, boundary="wall"), energy_row(1, boundary="wall")]
        tables = est.estimate_tables(bench, energy, exclude_flags=["contention"])
        self.assertEqual([(r["boundary"], r["level"]) for r in tables["cells"]],
                         [("rails", 1), ("rails", 2), ("wall", 1), ("wall", 2)])
        for row in tables["cells"]:
            if row["level"] == 1:
                self.assertEqual((row["n_bench"], row["k_correct"], row["m_energy"]), (2, 1, 2))
            else:
                self.assertEqual((row["n_bench"], row["m_energy"]), (1, 0))
                self.assertEqual(row["epc_status"], "not_estimable_few_attempts")
        self.assertEqual(est.estimate_tables(bench, [energy_row(energy_j=0)])["cells"], [])
        self.assertEqual(est.estimate_tables(bench, [])["cells"], [])

    def test_unmatched_and_level_mismatch_used_until_excluded(self):
        energy = [energy_row(item_id="unmatched"), energy_row(1, level=2)]
        tables = est.estimate_tables([bench_row(1)], energy)
        self.assertEqual(sum(row["m_energy"] for row in tables["cells"]), 2)
        tables = est.estimate_tables([bench_row(1)], energy, exclude_flags=["not_in_bench", "level_mismatch"])
        self.assertEqual(tables["cells"], [])
        self.assertEqual(tables["summary"]["flag_counts"]["energy"], {"level_mismatch": 1, "not_in_bench": 1})

    def test_decomposition_and_residuals_use_same_rows_as_cells(self):
        rows = ols_rows([2, -1, 0, -2, 1, 0])
        for index, row in enumerate(rows):
            row["level"] = index // 2 + 1
        rows.append(energy_row(6, energy_j=1000, flags="contention"))
        bench = [bench_row(i, level=row["level"], generated_tokens=row["generated_tokens"])
                 for i, row in enumerate(rows)]
        tables = est.estimate_tables(bench, rows, exclude_flags=["contention"])
        self.assertEqual(sum(row["m_energy"] for row in tables["cells"]), 6)
        self.assertEqual(tables["decomposition"][0]["N"], 6)
        self.assertEqual(sum(row["m"] for row in tables["level_residuals"]), 6)
        self.assertAlmostEqual(tables["decomposition"][0]["a_j"], 13.980831, places=6)

    def test_end_to_end_and_config_overrides(self):
        directory = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, directory)
        path = Path(directory)
        bench = [bench_row(i, correct=int(i < 15), generated_tokens=TOKENS[i] if i < 5 else 20) for i in range(20)]
        energy = [energy_row(i, energy_j=value, generated_tokens=TOKENS[i], flags="contention" if i == 0 else "")
                  for i, value in enumerate(ENERGIES)]
        est.write_csv(path / "bench.csv", est.BENCH_COLUMNS, bench)
        est.write_csv(path / "energy.csv", est.ENERGY_COLUMNS, energy)
        config = {**load_config(FIXTURE), "confidence": .8, "exclude_flags": ["contention"]}
        (path / "config.json").write_text(json.dumps(config), encoding="utf-8")
        command = [sys.executable, str(ROOT / "scripts/difficulty_estimate.py"), "--bench", str(path / "bench.csv"),
                   "--energy", str(path / "energy.csv"), "--out", str(path / "out"), "--config", str(path / "config.json")]
        result = subprocess.run(command, capture_output=True, text=True, env=os.environ.copy())
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual({file.name for file in (path / "out").iterdir()},
                         {"cells.csv", "decomposition.csv", "level_residuals.csv", "crossover.csv", "summary.json"})
        for name, columns in (("cells", est.CELL_COLUMNS), ("decomposition", est.DECOMPOSITION_COLUMNS),
                              ("level_residuals", est.RESIDUAL_COLUMNS), ("crossover", est.CROSSOVER_COLUMNS)):
            payload = (path / "out" / (name + ".csv")).read_bytes()
            self.assertNotIn(b"\r", payload)
            self.assertEqual(payload.decode().splitlines()[0], ",".join(columns))
        summary = json.loads((path / "out/summary.json").read_text())
        self.assertEqual(summary["confidence"], .8)
        with (path / "out/cells.csv").open(newline="") as stream:
            cell = next(csv.DictReader(stream))
        self.assertEqual(cell["m_energy"], "4")
        self.assertEqual(cell["excluded_rows"], "1")
        result = subprocess.run(command + ["--confidence", ".95", "--exclude-flags", ""],
                                capture_output=True, text=True, env=os.environ.copy())
        self.assertEqual(result.returncode, 0, result.stderr)
        with (path / "out/cells.csv").open(newline="") as stream:
            cell = next(csv.DictReader(stream))
        self.assertEqual(cell["n_bench"], "20")
        self.assertEqual(cell["k_correct"], "15")
        self.assertEqual(cell["m_energy"], "5")
        self.assertEqual((cell["n_holdout"], cell["k_holdout"]), ("15", "10"))
        self.assertEqual(cell["epc_j"], repr(140/(10/15)))
        self.assertAlmostEqual(float(cell["epc_hi_j"]), 356.798, places=3)
        self.assertEqual(json.loads((path / "out/summary.json").read_text())["confidence"], .95)
        est.write_csv(path / "energy.csv", est.ENERGY_COLUMNS, energy + [energy_row(99, energy_j="nan")])
        result = subprocess.run(command[:-2], capture_output=True, text=True, env=os.environ.copy())
        self.assertEqual(result.returncode, 0, result.stderr)
        summary = json.loads((path / "out/summary.json").read_text())
        self.assertEqual(summary["confidence"], .95)
        self.assertEqual(summary["flag_counts"]["energy"]["bad_number"], 1)
        with (path / "out/cells.csv").open(newline="") as stream:
            cell = next(csv.DictReader(stream))
        self.assertEqual((cell["m_energy"], cell["excluded_rows"]), ("5", "1"))
        bad = subprocess.run(command + ["--confidence", "1"], capture_output=True, text=True, env=os.environ.copy())
        self.assertEqual(bad.returncode, 2)
        missing = command.copy()
        missing[missing.index("--bench") + 1] = str(path / "absent.csv")
        result = subprocess.run(missing, capture_output=True, text=True, env=os.environ.copy())
        self.assertEqual(result.returncode, 1)


if __name__ == "__main__":
    unittest.main()
