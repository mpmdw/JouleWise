"""RL-80 attribution probe: on synthetic stage-1 outputs, the output holds only names, counts,
multiples of a bar and yes/no answers, never a value or a sign, and the stated questions come
out as constructed."""
from __future__ import annotations

import contextlib
import csv
import io
import json
import re
import statistics
import tempfile
import unittest
from pathlib import Path

from scripts import bytes_stage1_attribution_probe as probe

ROOT = Path(__file__).resolve().parents[1]
FACTOR = 1.0731                       # the synthetic blinding factor (pack x configuration)
OPERATIVE = 0.0456789                 # a duration; must never print
DECODE = 4321.987654                  # an energy; must never print
EXPORT_ANCHOR = 0.0471234             # unblinded export-column anchor; must never print
ESTIMATOR_ANCHOR = 0.0612345          # the estimator's re-derived anchor; must never print
H = 0.0123456
PLANTED = ("4321", "0.0471", "0.047", "0.0612", "0.061", "0.0456", "0.0457", "0.045", "1.0731", "1.07",
           "0.0123", "secret", "qwen3-14b", "Qwen3-14B")
SID = "r1-bytes-s1-p1-calibration"
MODEL = "Qwen3-1.7B-4bit"
CANON = "qwen3-1.7b-4bit"

LINE_RE = re.compile("|".join((
    r"# BYTES stage-1 attribution probe \(RL-80\): names, counts, multiples of bar and yes/no only",
    r"Q [A-Za-z_]+ [^0-9]+",
    r"TOTAL above_bar=\d+ compared_fit=\d+",
    r"ABOVE (fit|fit-commit) (rails|dc_input|rest|commit) [A-Za-z_]+(:[A-Za-z_]+)? \d+",
    r"MULT [a-z0-9_./-]+ [A-Za-z_]+(:[A-Za-z_]+)? [0-9.e+]+",
    r"EXACT [a-z0-9_./-]+ [A-Za-z_]+(:[A-Za-z_]+)?",
    r"A [A-Za-z_]+ yes=\d+ no=\d+ not_evaluable=\d+",
    r"FLAG (rails|dc_input|rest) (estimator_only|twin_only) [a-z0-9_.]+ cells=\d+( effect=[A-Z_]+)?",
    r"FLAG_UNCATALOGUED cells=\d+",
    r"FLAGQ [a-z0-9_.]+ [A-Za-z_]+ yes=\d+ no=\d+ not_evaluable=\d+",
    r"WITHHELD unprintable_rows=\d+",
)))


def status(a, t, bar):
    if bar == "exact":
        return "equal" if a == t else "above_bar"
    d = abs(a - t)
    return "equal" if d == 0 else "under_bar" if d <= bar else "above_bar"


def row(stage, group, key, a, t, bar):
    out = {"stage": stage, "group": group, "key": key, "a": a, "t": t, "bar": bar, "status": status(a, t, bar)}
    if bar != "exact":
        out["abs"] = abs(a - t)
    return out


def strat(values):
    return 0.2 * statistics.fmean(values[:2]) + 0.8 * statistics.fmean(values[2:])


class Campaign:
    """One fit model, one pass, two rails variants and one dc_input cell, written to disk."""

    def __init__(self, base: Path, *, swap=False):
        self.base = base
        run_ids = [f"{CANON}-r{i:02d}" for i in range(10)]
        decode = [DECODE + 0.01 * i for i in range(10)]
        anchor = [EXPORT_ANCHOR + 0.0001 * i for i in range(10)]
        mean = strat(decode)
        twin_anchor = strat(anchor)
        est_anchor = ESTIMATOR_ANCHOR
        B_t, B_a = twin_anchor + 0.5, est_anchor + 0.5
        bar = 0.01 * (H + B_a)
        rows = []
        for variant in ("gross", "flagged_inclusive"):
            g = f"cell/{CANON}/pass1/rails/{variant}"
            pairs = {"mean_j": (mean, mean), "h_j": (H, H), "B_j": (B_a, B_t),
                     "lower_j": (mean - H - B_a, mean - H - B_t), "upper_j": (mean + H + B_a, mean + H + B_t),
                     "B_kind:anchor": (est_anchor, twin_anchor), "B_kind:interp": (0.0, 0.0),
                     "B_kind:drift": (0.5, 0.5), "B_kind:meter_edge": (0.0, 0.0),
                     "attribution_floor_j": (est_anchor + 0.001, max(anchor)),
                     "rails_attribution_floor_j": (est_anchor + 0.001, max(anchor))}
            for key, (a, t) in pairs.items():
                if swap:
                    a, t = t, a
                rows.append(row("fit", g, key, a, t, bar))
            rows.append(row("fit", g, "duration_s", 12.345678, 12.345678, 1e-3))
            rows.append(row("fit", g, "kept_runs", sorted(run_ids), sorted(run_ids), "exact"))
            rows.append(row("fit", g, "flags", ["battery.assist", "power.pstar_unsized", "secret.value_4321"],
                            ["battery.assist"], "exact"))
        g = f"cell/{CANON}/pass1/dc_input/gross"
        rows.append(row("fit", g, "flags", ["battery.assist", "power.pstar_unsized"], ["battery.assist"], "exact"))
        rows.append(row("fit", g, "B_j", 0.9, 0.9, bar))
        rows.append(row("fit", g, "kept_runs", sorted(run_ids), sorted(run_ids), "exact"))
        w_a, w_t = H + B_a, H + B_t
        if swap:
            w_a, w_t = w_t, w_a
        rows.append(row("fit-commit", f"commit/fit_point/rails/{CANON}", "w", w_a, w_t, 0.01 * (H + B_a)))
        # A held-out model's group must never print, even if a row for it existed.
        rows.append(row("fit", "cell/qwen3-14b-4bit/pass1/rails/gross", "B_j", 3.0, 1.0, 0.01))
        self.rows = rows
        run = base / "run"
        (run / "out/a-fit").mkdir(parents=True)
        (run / "agreement-stage1.json").write_text(json.dumps(rows))
        (run / "agreement-blinded.json").write_text(json.dumps([
            row("blinded", f"cell/{CANON}/pass1/rails/{v}", "flags", ["battery.assist"], ["battery.assist"], "exact")
            for v in ("gross", "flagged_inclusive")]))
        fit_rows = []
        for boundary in ("rails", "DC input", "rest"):
            for basis in ("gross primary", "idle-subtracted secondary"):
                for selection in ("primary", "flagged-inclusive"):
                    fit_rows.append({"model": MODEL, "role": "fit", "pass_id": 1, "session_id": SID,
                                     "boundary": boundary, "basis": basis, "selection": selection,
                                     "status": "computed", "flags": ["battery.assist", "power.pstar_unsized"],
                                     "operative": [{"operative_bound_s": OPERATIVE, "status": "rereduced"}]})
        (run / "out/a-fit/fit_pass_estimates.json").write_text(json.dumps(fit_rows))
        export = base / "export/bytes-s1-p1"
        export.mkdir(parents=True)
        columns = ["run_id", "model_name", "pass_id", "role", "strata", "unit_ids", "flag_codes",
                   "exclusion_codes", "phase_decode_j", "bound_E_clock_anchor_shift_bound_j", "dur_decode_s"]
        with (export / f"{SID}.runs.csv").open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=columns)
            writer.writeheader()
            for i, rid in enumerate(run_ids):
                writer.writerow({"run_id": rid, "model_name": "mlx-community/" + MODEL, "pass_id": 1,
                                 "role": "science", "strata": "repeat" if i < 2 else "quad",
                                 "unit_ids": str(i if i < 2 else (i - 2) // 4),
                                 "flag_codes": "battery.assist" if i == 3 else "", "exclusion_codes": "",
                                 "phase_decode_j": repr(decode[i] * FACTOR),
                                 "bound_E_clock_anchor_shift_bound_j": repr(anchor[i] * FACTOR),
                                 "dur_decode_s": "12.345678"})
        (export / f"{SID}.session.json").write_text(json.dumps({
            "session_id": SID, "operative_bound_s": str(OPERATIVE),
            "flag_counts": {"power.pstar_unsized": 1, "battery.assist": 2}}))

    def run(self):
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = probe.main(["--run-root", str(self.base / "run"), "--export", str(self.base / "export"),
                               "--repo", str(ROOT)])
        return code, stdout.getvalue(), stderr.getvalue()


def answers(text):
    out = {}
    for line in text.splitlines():
        parts = line.split()
        if parts[0] == "A":
            out[parts[1]] = tuple(int(p.split("=")[1]) for p in parts[2:])
        elif parts[0] == "FLAGQ":
            out[(parts[1], parts[2])] = tuple(int(p.split("=")[1]) for p in parts[3:])
    return out


class ProbeOutputTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def output(self, **kw):
        code, text, err = Campaign(self.base / ("c" + str(len(list(self.base.iterdir())))), **kw).run()
        self.assertEqual((code, err), (0, ""))
        return text

    def test_every_line_is_a_name_count_multiple_or_answer(self):
        for line in self.output().splitlines():
            self.assertRegex(line, LINE_RE)
            self.assertTrue(LINE_RE.fullmatch(line), line)

    def test_no_value_and_no_sign_is_printed(self):
        text = self.output()
        for planted in PLANTED:
            self.assertNotIn(planted, text)
        self.assertIsNone(re.search(r"(?<![A-Za-z0-9])-\d", text))   # no signed number
        self.assertNotIn("larger", text)
        self.assertNotIn("smaller", text)

    def test_output_does_not_depend_on_which_side_is_larger(self):
        """Swapping a and t on every numeric field leaves every bound and w line unchanged."""
        keep = ("ABOVE", "MULT", "A B_other_keys", "A B_other_kinds", "A B_is_anchor", "A B_centre_h",
                "A B_ends", "A W_follows_B", "A W_with_B")
        pick = lambda text: [l for l in text.splitlines() if l.startswith(keep)]
        self.assertEqual(pick(self.output()), pick(self.output(swap=True)))

    def test_questions_answer_as_constructed(self):
        got = answers(self.output())
        self.assertEqual(got["B_twin_is_export"], (2, 0, 0))
        self.assertEqual(got["B_estimator_is_export"], (0, 2, 0))
        # The dc_input cell carries no anchor or interval rows here: not evaluable, never guessed.
        self.assertEqual(got["B_is_anchor"], (2, 0, 1))
        self.assertEqual(got["B_ends"], (2, 0, 1))
        self.assertEqual(got["B_centre_h"][1], 0)
        self.assertEqual(got["B_operative_one"], (12, 0, 0))
        self.assertEqual(got["W_follows_B"], (1, 0, 0))
        self.assertEqual(got["W_with_B"], (1, 0, 0))
        code = "power.pstar_unsized"
        self.assertEqual(got[(code, "F_row_flag_codes")], (0, 1, 0))
        self.assertEqual(got[(code, "F_kept_flag_codes")], (0, 1, 0))
        self.assertEqual(got[(code, "F_sidecar_counts")], (1, 0, 0))
        self.assertEqual(got[(code, "F_every_cell")], (1, 0, 0))
        self.assertEqual(got[(code, "F_meter_flag")], (0, 1, 0))
        self.assertEqual(got[(code, "F_blinded_estimator")], (0, 1, 0))

    def test_flags_listed_by_boundary_and_side_with_counts(self):
        text = self.output()
        self.assertIn("FLAG rails estimator_only power.pstar_unsized cells=2 effect=DISCLOSE", text)
        self.assertIn("FLAG dc_input estimator_only power.pstar_unsized cells=1 effect=DISCLOSE", text)
        self.assertIn("FLAG_UNCATALOGUED cells=2", text)

    def test_heldout_group_is_counted_never_named(self):
        text = self.output()
        self.assertIn("WITHHELD unprintable_rows=1", text)
        self.assertNotIn("14b", text)


class ProbeRefusalTests(unittest.TestCase):
    def test_refuses_withheld_key_custody_and_heldout_paths(self):
        for path in ("/x/withheld/bytes-s3-p1/s.runs.csv", "/x/run/released-keys/pack.json",
                     "/x/night-custody/a.json", "/x/run/out/a-held/h1.json", "/x/run/out/t-2.json",
                     "/x/export/bytes-s1-p1/s.withheld.csv", "/x/post/a-blinded-post"):
            with self.assertRaises(probe.ProbeRefused):
                probe.guard(Path(path))

    def test_cli_refuses_an_export_root_under_withheld(self):
        with tempfile.TemporaryDirectory() as tmp:
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr), contextlib.redirect_stdout(io.StringIO()):
                code = probe.main(["--run-root", tmp, "--export", str(Path(tmp) / "withheld"), "--repo", str(ROOT)])
            self.assertEqual(code, 2)
            self.assertNotRegex(stderr.getvalue(), r"\d")

    def test_untyped_tokens_and_values_cannot_be_emitted(self):
        out = probe.Out({CANON}, {"power.pstar_unsized"})
        with self.assertRaises(probe.ProbeRefused):
            out.emit("MULT", out.group(f"cell/{CANON}/pass1/rails/gross"), "B_j", "4321.98")
        with self.assertRaises(probe.ProbeRefused):
            out.emit("VALUE", out.count(1))
        for bad in (-1, True, 1.5):
            with self.assertRaises(probe.ProbeRefused):
                out.count(bad)
        for bad in (-0.5, float("nan"), float("inf")):
            with self.assertRaises(probe.ProbeRefused):
                out.multiple(bad)
        with self.assertRaises(probe.ProbeRefused):
            out.pair("operative_bound_s", 1)
        self.assertIsNone(out.group("cell/qwen3-14b-4bit/pass1/rails/gross"))
        self.assertIsNone(out.key("value 4321.98"))
        self.assertIsNone(out.code("secret.value_4321"))

    def test_failure_prints_the_exception_class_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr), contextlib.redirect_stdout(io.StringIO()):
                code = probe.main(["--run-root", tmp, "--export", tmp, "--repo", str(ROOT)])
            self.assertEqual(code, 1)
            self.assertEqual(stderr.getvalue().strip(), "probe failed: FileNotFoundError")

    def test_probe_is_standard_library_only(self):
        import ast
        tree = ast.parse((ROOT / "scripts/bytes_stage1_attribution_probe.py").read_text())
        names = {a.name.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
        names |= {n.module.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module}
        self.assertFalse(names & {"joulewise", "scripts", "tests"}, names)


if __name__ == "__main__":
    unittest.main()
