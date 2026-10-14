"""Spec-pinned checks and black-box agreement for the independent twin.

The reference implementation is only executed as a subprocess. This module
does not import or inspect any production DIFFICULTY module.
"""

import csv
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
import unittest

ROOT = Path(__file__).resolve().parent.parent
TWIN = ROOT / "scripts" / "difficulty_twin.py"
REFERENCE = ROOT / "scripts" / "difficulty_estimate.py"

# Output schemas are copied from spec section 7, independently of the twin.
SCHEMAS = {
    "cells.csv": "boundary model mode level n_bench k_correct accuracy acc_lo acc_hi mean_generated_tokens_bench cap_hit_rate_bench m_energy mean_energy_j energy_lo_j energy_hi_j n_holdout k_holdout epc_j epc_lo_j epc_hi_j epc_status j_per_token jpt_lo jpt_hi token_mismatch_count excluded_rows".split(),
    "decomposition.csv": "boundary model mode N a_j a_se b_prompt_j_per_tok b_prompt_se b_gen_j_per_tok b_gen_se r2 r2_gen_only gen_share status".split(),
    "level_residuals.csv": "boundary model mode level m mean_residual_j lo_j hi_j contains_zero".split(),
    "crossover.csv": "boundary level cheapest cheapest_epc_j status tied".split(),
}
KEYS = {
    "cells.csv": ("boundary", "model", "mode", "level"),
    "decomposition.csv": ("boundary", "model", "mode"),
    "level_residuals.csv": ("boundary", "model", "mode", "level"),
    "crossover.csv": ("boundary", "level"),
}
STRINGS = {"boundary", "model", "mode", "epc_status", "status", "cheapest", "tied"}
INTEGERS = {"level", "n_bench", "k_correct", "n_holdout", "k_holdout", "m_energy", "token_mismatch_count", "excluded_rows", "N", "m", "contains_zero"}
BENCH_COLUMNS = "model mode item_id level outcome correct prompt_tokens generated_tokens cap_hit flags".split()
ENERGY_COLUMNS = "model mode level item_id boundary energy_j prompt_tokens generated_tokens flags".split()


def bench_row(model, level, item, correct=1, prompt=100, generated=100, mode="off", flags="", cap=0):
    return dict(zip(BENCH_COLUMNS, (model, mode, item, level, "correct" if correct else "incorrect", correct, prompt, generated, cap, flags)))


def energy_row(bench, energy, boundary="rails", **overrides):
    row = {name: bench[name] for name in ("model", "mode", "level", "item_id", "prompt_tokens", "generated_tokens")}
    row.update(boundary=boundary, energy_j=energy, flags="")
    row.update(overrides)
    return row


def acceptance_tables():
    """Realize A-D, all C edge cases, E/F, and G's two verdicts."""
    bench, energy = [], []
    energies, tokens = [100, 120, 140, 160, 180], [50, 70, 80, 90, 110]
    for model, k, m in (("A-C-D", 15, 5), ("C-all", 20, 5), ("C-zero", 0, 5), ("C-one", 15, 1)):
        rows = [bench_row(model, 1, f"{model}-{i}", int(i < k), generated=tokens[i] if i < 5 else 100) for i in range(20)]
        bench.extend(rows)
        energy.extend(energy_row(row, value) for row, value in zip(rows[:m], energies))
    coordinates = [(100, 50), (120, 70), (80, 80), (150, 90), (110, 110), (90, 60)]
    for model, noise in (("E", (0,)*6), ("F", (2, -1, 0, -2, 1, 0))):
        for i, ((p, g), delta) in enumerate(zip(coordinates, noise)):
            row = bench_row(model, 1 if i < 3 else 5, f"{model}-{i}", prompt=p, generated=g)
            bench.append(row)
            energy.append(energy_row(row, 10+0.5*p+1.5*g+delta))
    # At n=200,k=150 the 100/110 pair is unresolved; 100/200 resolves.
    for model in ("X", "Y", "Z"):
        for level in (1, 5):
            rows = [bench_row(model, level, f"G-{level}-{i}", int(i < 150)) for i in range(200)]
            bench.extend(rows)
            for boundary in ("rails", "wall"):
                if boundary == "wall" and model == "Z":
                    continue
                costs = {"X": 100, "Y": 200, "Z": 110} if level == 1 else {"X": 200, "Y": 100, "Z": 110}
                energy.extend(energy_row(row, costs[model], boundary) for row in rows[:20])
    return bench, energy


def synthetic_tables():
    rng = random.Random(20261014)
    bench, energy = [], []
    for mi, model in enumerate(("model-a", "model-b", "model-c")):
        for mode in ("off", "on"):
            for level in range(1, 6):
                rows = []
                accuracy = 0.97-0.15*(level-1)+0.01*mi+(0.02 if mode == "on" else 0.0)
                for i in range(200):
                    p = rng.randint(80, 500)
                    g = rng.randint(50+100*level, 100+200*level)+(150 if mode == "on" else 0)
                    correct = int(rng.random() < accuracy)
                    if (model, mode, level) == ("model-c", "on", 5):
                        correct = 0
                    rows.append(bench_row(model, level, f"synthetic-{level}-{i}", correct, p, g, mode, cap=int(i % 37 == 0)))
                bench.extend(rows)
                for boundary in ("rails", "wall"):
                    m = 1 if (boundary, model, mode, level) == ("wall", "model-a", "off", 2) else 20
                    for row in rows[:m]:
                        value = (30+0.02*row["prompt_tokens"]+(0.08+0.05*mi)*row["generated_tokens"])*rng.lognormvariate(0.0, 0.1)
                        energy.append(energy_row(row, value, boundary))
    for i, overrides in enumerate(({"energy_j": "nan"}, {"energy_j": 0}, {"energy_j": "not-a-number"}, {"prompt_tokens": "1.5"}, {"generated_tokens": -1})):
        energy.append(energy[0] | {"item_id": f"bad-number-{i}"} | overrides)
    energy.append(dict(energy[0]))
    return bench, energy


def parsing_tables():
    bench = [bench_row("parse", 1, f"parse-{i}", int(i < 15), prompt=100+i*i, generated=50+i*7) for i in range(20)]
    energy = [energy_row(row, 90+i*3+(i % 3)) for i, row in enumerate(bench[:8])]
    energy.extend((
        energy_row(bench[8], 130, level=2),
        energy_row(bench[9], 140, generated_tokens=114),
        energy_row(bench[10], 150, flags="battery_assist"),
        energy_row(bench[11], 160, flags="contention"),
        energy_row(bench[12], 170, item_id="not-in-bench"),
    ))
    for i, override in enumerate((
        {"energy_j": "inf"}, {"energy_j": -2}, {"energy_j": "bad"},
        {"prompt_tokens": "2.5"}, {"generated_tokens": -3},
        {"flags": "unknown_item"}, {"flags": "unknown_config"},
        {"flags": "duplicate"}, {"level": ""}, {"level": "1.5"},
        {"level": 6}, {"mode": "invalid"}, {"flags": "bad_level"}, {"flags": "bad_mode"},
    )):
        energy.append(energy_row(bench[13], 180, item_id=f"excluded-{i}", **override))
    energy.append(energy[0] | {"energy_j": 999, "level": 5})
    energy.extend(energy_row(bench[i], 180, generated_tokens=value)
                  for i, value in ((14, "abc"), (15, "12.0")))
    for i, flag in enumerate(("unknown_item", "unknown_config", "duplicate", "bad_number", "missing_text", "contention")):
        bench.append(bench_row("parse", 1, f"bench-excluded-{i}", flags=flag))
    bench.extend((bench_row("parse", "", "blank-level"), bench_row("parse", "1.5", "noninteger-level"),
                  bench_row("parse", 9, "out-of-range-level"), bench_row("parse", "١", "non-ascii-level"),
                  bench_row("parse", 1, "bad-mode", mode="invalid"), dict(bench[0]),
                  bench_row("parse", 1, "retained-flag", flags="unknown_finish_reason")))
    out_of_range = next(row for row in bench if row["item_id"] == "out-of-range-level")
    energy.append(energy_row(out_of_range, 100, level=8))
    # An excluded-only boundary cannot produce output rows.
    energy.append(energy_row(bench[0], 0, boundary="excluded-boundary"))
    return bench, energy


class TwinAgreementTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.twin_functions = runpy.run_path(os.fspath(TWIN))

    def setUp(self):
        self.directory = Path(tempfile.mkdtemp(prefix="difficulty-twin-"))
        self.addCleanup(shutil.rmtree, self.directory)

    def write_inputs(self, bench, energy):
        for name, columns, rows in (("bench.csv", BENCH_COLUMNS, bench), ("energy.csv", ENERGY_COLUMNS, energy)):
            with (self.directory/name).open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
                writer.writeheader()
                writer.writerows(rows)

    def run_program(self, script, tag, options=()):
        out = self.directory/tag
        command = [sys.executable, os.fspath(script), "--bench", os.fspath(self.directory/"bench.csv"), "--energy", os.fspath(self.directory/"energy.csv"), "--out", os.fspath(out), *options]
        completed = subprocess.run(command, cwd=ROOT, env=os.environ | {"PYTHONDONTWRITEBYTECODE": "1"}, text=True, capture_output=True, timeout=60)
        self.assertEqual(completed.returncode, 0, f"{script.name} failed: {completed.stderr}")
        tables = {}
        for name, schema in SCHEMAS.items():
            data = (out/name).read_bytes()
            self.assertNotIn(b"\r", data)
            with (out/name).open(newline="", encoding="utf-8") as handle:
                reader = csv.DictReader(handle)
                self.assertEqual(reader.fieldnames, schema, name)
                tables[name] = list(reader)
            keys = [self.row_key(name, row) for row in tables[name]]
            self.assertEqual(keys, sorted(keys), f"{script.name}/{name} not sorted")
            self.assertEqual(len(keys), len(set(keys)), f"{script.name}/{name} duplicate keys")
        tables["summary.json"] = json.loads((out/"summary.json").read_text(encoding="utf-8"))
        return tables

    @staticmethod
    def row_key(name, row):
        return tuple(int(row[field]) if field == "level" else row[field] for field in KEYS[name])

    def compare(self, reference, twin):
        differences = []
        for name, schema in SCHEMAS.items():
            r = {self.row_key(name, row): row for row in reference[name]}
            t = {self.row_key(name, row): row for row in twin[name]}
            self.assertEqual(set(r), set(t), name)
            tolerance = 1e-8 if name == "decomposition.csv" else 1e-9
            for key in sorted(r):
                for column in schema:
                    actual, expected = t[key][column], r[key][column]
                    if column in STRINGS or column in INTEGERS or actual == "" or expected == "":
                        matches = actual == expected
                    else:
                        matches = math.isclose(float(actual), float(expected), rel_tol=tolerance, abs_tol=1e-12)
                    if not matches:
                        differences.append(f"{name} {key} {column}: twin={actual!r}, first={expected!r}")
        self.assertFalse(differences, "\n"+"\n".join(differences[:60])+f"\nTotal disagreements: {len(differences)}")
        self.assertEqual({k: v for k, v in reference["summary.json"].items() if k != "method_note"},
                         {k: v for k, v in twin["summary.json"].items() if k != "method_note"})

    def agreement(self, fixture, options=()):
        self.write_inputs(*fixture)
        twin = self.run_program(TWIN, "twin", options)
        reference = self.run_program(REFERENCE, "first", options)
        self.compare(reference, twin)

    def test_acceptance_tables_agree(self):
        self.agreement(acceptance_tables())

    def test_seeded_synthetic_tables_agree(self):
        self.agreement(synthetic_tables())

    def test_nondefault_confidence_and_exclusions_agree(self):
        self.agreement(synthetic_tables(), ("--confidence", "0.9", "--exclude-flags", "token_mismatch"))

    def test_parse_flags_and_exclusions_agree(self):
        for options in ((), ("--exclude-flags", "battery_assist,contention,not_in_bench,level_mismatch,token_mismatch")):
            with self.subTest(options=options):
                self.agreement(parsing_tables(), options)

    def test_case_I_holdout_agrees_and_matches_pins(self):
        bench = [bench_row("I", 1, f"i{i:02}", correct=int(i == 1 or 6 <= i <= 20))
                 for i in range(1, 26)]
        energy = [energy_row(row, value) for row, value in zip(bench, (100, 120, 140, 160, 180))]
        self.write_inputs(bench, energy)
        tables = self.run_program(TWIN, "holdout")
        self.compare(self.run_program(REFERENCE, "holdout-first"), tables)
        cell = tables["cells.csv"][0]
        self.assertEqual((cell["n_bench"], cell["k_correct"], cell["accuracy"],
                          cell["n_holdout"], cell["k_holdout"]), ("25", "16", "0.64", "20", "15"))
        for field, expected, digits in (("epc_j", 186.6667, 4), ("epc_lo_j", 128.934, 3),
                                        ("epc_hi_j", 285.303, 3)):
            self.assert_printed(cell[field], expected, digits)

    def test_holdout_all_energy_rows_and_runtime_defaults_agree(self):
        bench = [bench_row("holdout", 1, f"i{i}") for i in range(8)]
        bench[7].update(flags="runtime_failed", correct=0, outcome="malformed")
        energy = [energy_row(bench[0], 100), energy_row(bench[1], 120),
                  energy_row(bench[2], 140, boundary="wall", flags="contention"),
                  energy_row(bench[3], 100, level=9), energy_row(bench[4], "nan"),
                  energy_row(bench[5], 100, model="other"), energy_row(bench[6], 100, mode="on")]
        for options in ((), ("--exclude-flags", "contention,runtime_failed"), ("--exclude-flags", "")):
            with self.subTest(options=options):
                self.agreement((bench, energy), options)

    def assert_printed(self, value, expected, digits):
        # Half a unit in the last printed decimal, not an agreement tolerance.
        self.assertAlmostEqual(float(value), expected, delta=0.5*10**(-digits))

    def test_twin_pinned_cases_a_to_f(self):
        self.write_inputs(*acceptance_tables())
        tables = self.run_program(TWIN, "pinned")
        cells = {(r["boundary"], r["model"], int(r["level"])): r for r in tables["cells.csv"]}
        c = cells["rails", "A-C-D", 1]
        for field, expected, digits in (
            ("accuracy", 0.75, 2), ("acc_lo", 0.531299, 6), ("acc_hi", 0.888138, 6),
            ("mean_energy_j", 140, 0), ("energy_lo_j", 100.7351, 4), ("energy_hi_j", 179.2649, 4),
            ("epc_j", 210, 0), ("epc_lo_j", 139.664, 3), ("epc_hi_j", 356.798, 3),
            ("j_per_token", 1.75, 2), ("jpt_lo", 1.610097, 6), ("jpt_hi", 1.889903, 6),
        ):
            with self.subTest(case="A-D", field=field):
                self.assert_printed(c[field], expected, digits)
        self.assertEqual(c["epc_status"], "ok")
        self.assertEqual((c["n_holdout"], c["k_holdout"]), ("15", "10"))
        all_correct = cells["rails", "C-all", 1]
        for field, expected, digits in (("acc_lo", 0.838875, 6), ("acc_hi", 1, 0), ("epc_j", 140, 0), ("epc_lo_j", 100.735, 3), ("epc_hi_j", 195.969, 3)):
            self.assert_printed(all_correct[field], expected, digits)
        zero = cells["rails", "C-zero", 1]
        self.assert_printed(zero["acc_lo"], 0, 0)
        self.assert_printed(zero["acc_hi"], 0.161125, 6)
        for row, status in ((zero, "not_estimable_zero_correct"), (cells["rails", "C-one", 1], "not_estimable_few_attempts")):
            self.assertEqual(row["epc_status"], status)
            for field in ("epc_j", "epc_lo_j", "epc_hi_j"):
                self.assertEqual(row[field], "")
        fits = {(r["boundary"], r["model"]): r for r in tables["decomposition.csv"]}
        exact = fits["rails", "E"]
        for field, expected, digits in (("a_j", 10, 0), ("b_prompt_j_per_tok", 0.5, 1), ("b_gen_j_per_tok", 1.5, 1), ("r2", 1, 0), ("gen_share", 0.641860, 6), ("r2_gen_only", 0.910222, 6)):
            self.assert_printed(exact[field], expected, digits)
        for row in tables["level_residuals.csv"]:
            if row["model"] == "E":
                self.assertEqual(float(row["mean_residual_j"]), 0.0)
                self.assertEqual(float(row["lo_j"]), 0.0)
                self.assertEqual(float(row["hi_j"]), 0.0)
                self.assertEqual(row["contains_zero"], "1")
        noisy = fits["rails", "F"]
        for field, expected in (("a_j", 13.980831), ("a_se", 3.137012), ("b_prompt_j_per_tok", 0.465176), ("b_prompt_se", 0.027441), ("b_gen_j_per_tok", 1.497284), ("b_gen_se", 0.031545), ("r2", 0.999164)):
            self.assert_printed(noisy[field], expected, 6)
        # Reconstruct RSS and TSS from the actual table and independently
        # verify the extra printed F pins, absent from section 7's CSV schema.
        rows = [row for row in acceptance_tables()[1] if row["model"] == "F"]
        residuals = [row["energy_j"]-(float(noisy["a_j"])+float(noisy["b_prompt_j_per_tok"])*row["prompt_tokens"]+float(noisy["b_gen_j_per_tok"])*row["generated_tokens"]) for row in rows]
        self.assert_printed(math.fsum(r*r for r in residuals), 6.060703, 6)
        mean = math.fsum(row["energy_j"] for row in rows)/len(rows)
        self.assert_printed(math.fsum((row["energy_j"]-mean)**2 for row in rows), 7250.833, 3)

    def test_twin_case_h_quantiles(self):
        quantile = self.twin_functions["student_t_quantile"]
        for df, expected in ((3, 3.182446305), (4, 2.776445105), (9, 2.262157163), (19, 2.093024054), (29, 2.045229642)):
            with self.subTest(df=df):
                self.assertAlmostEqual(quantile(0.975, df), expected, delta=1e-9)
                self.assertAlmostEqual(quantile(0.025, df), -expected, delta=1e-9)
        self.assertEqual(quantile(0.5, 19), 0.0)

    def test_twin_crossover_verdicts_and_summary(self):
        # A-F configurations coexist, so isolate G for its actual verdicts.
        bench, energy = acceptance_tables()
        self.write_inputs([r for r in bench if r["model"] in {"X", "Y", "Z"}], [r for r in energy if r["model"] in {"X", "Y", "Z"}])
        tables = self.run_program(TWIN, "g-only")
        self.compare(self.run_program(REFERENCE, "g-first"), tables)
        cross = {(r["boundary"], int(r["level"])): r for r in tables["crossover.csv"]}
        for level, winner in ((1, "X/off"), (5, "Y/off")):
            self.assertEqual(cross["wall", level]["cheapest"], winner)
            self.assertEqual(cross["wall", level]["status"], "resolved")
            self.assertEqual(cross["rails", level]["status"], "unresolved")
            self.assertEqual(cross["rails", level]["tied"], "Z/off")
        summary = json.loads((self.directory/"g-only"/"summary.json").read_text())
        self.assertEqual(summary["boundaries"]["wall"]["verdict"], "crossover_resolved")
        self.assertEqual(summary["boundaries"]["rails"]["verdict"], "no_resolved_crossover")
        self.assertEqual(summary["boundaries"]["wall"]["resolved_winners"], {"1": "X/off", "5": "Y/off"})

    def test_twin_parse_counts(self):
        self.write_inputs(*parsing_tables())
        tables = self.run_program(TWIN, "parse", ("--exclude-flags", "contention"))
        cells = {int(r["level"]): r for r in tables["cells.csv"]}
        self.assertEqual(set(cells), {1, 2})
        self.assertEqual(cells[1]["n_bench"], "21")
        self.assertEqual(cells[1]["m_energy"], "11")
        self.assertEqual(cells[1]["token_mismatch_count"], "1")
        self.assertEqual(cells[1]["excluded_rows"], "11")
        self.assertEqual(cells[2]["m_energy"], "1")
        self.assertEqual(cells[2]["n_bench"], "0")
        singleton = next(r for r in tables["level_residuals.csv"] if r["level"] == "2")
        self.assertNotEqual(singleton["mean_residual_j"], "")
        self.assertEqual(singleton["lo_j"], "")
        self.assertEqual(singleton["hi_j"], "")
        self.assertEqual(singleton["contains_zero"], "")
        counts = json.loads((self.directory/"parse"/"summary.json").read_text())["flag_counts"]["energy"]
        for flag in ("bad_number", "bad_level", "bad_mode", "duplicate", "not_in_bench", "level_mismatch", "token_mismatch"):
            self.assertGreater(counts[flag], 0, flag)
        self.assertEqual(counts["token_mismatch"], 1)
        counts = tables["summary.json"]["flag_counts"]["bench"]
        self.assertEqual(counts["bad_level"], 4)
        self.assertEqual(counts["bad_mode"], 1)
        self.assertEqual(counts["duplicate"], 2)

    def test_twin_empty_and_ineligible_cells(self):
        bench = [bench_row("empty", 1, "b")]
        self.write_inputs(bench, [energy_row(bench[0], "nan")])
        tables = self.run_program(TWIN, "empty")
        self.assertTrue(all(not tables[name] for name in SCHEMAS))
        self.write_inputs([bench_row("zero", 1, "z", correct=0)], [energy_row(bench_row("zero", 1, "z", correct=0), 1)])
        tables = self.run_program(TWIN, "zero")
        self.assertEqual(tables["crossover.csv"][0]["status"], "none_estimable")
        self.assertEqual(tables["crossover.csv"][0]["cheapest"], "")

    def test_twin_nonpositive_energy_lower_and_zero_tokens(self):
        bench = [bench_row(model, 1, f"{model}-{i}", generated=0) for model in ("cheap", "noisy") for i in range(20)]
        energy = [energy_row(r, (1 if r["model"] == "cheap" else (1 if r["item_id"].endswith("-0") else 200))) for r in bench if r["item_id"].endswith(("-0", "-1"))]
        self.write_inputs(bench, energy)
        tables = self.run_program(TWIN, "nonpositive")
        noisy = next(r for r in tables["cells.csv"] if r["model"] == "noisy")
        self.assertEqual(noisy["epc_status"], "energy_lower_nonpositive")
        self.assertEqual(noisy["epc_lo_j"], "0.0")
        self.assertEqual(noisy["j_per_token"], "")
        self.assertEqual(tables["crossover.csv"][0]["status"], "unresolved")
        self.assertEqual(tables["crossover.csv"][0]["tied"], "noisy/off")

    def test_twin_usage_and_unreadable_inputs_fail(self):
        self.write_inputs([], [])
        base = [sys.executable, os.fspath(TWIN), "--bench", os.fspath(self.directory/"bench.csv"), "--energy", os.fspath(self.directory/"energy.csv"), "--out", os.fspath(self.directory/"bad-cli")]
        for options in (("--confidence", "1"), ("--confidence", "nan"), ("--bench", os.fspath(self.directory/"missing.csv"))):
            with self.subTest(options=options):
                completed = subprocess.run(base+list(options), cwd=ROOT, text=True, capture_output=True, timeout=60)
                self.assertNotEqual(completed.returncode, 0)


if __name__ == "__main__":
    unittest.main()
