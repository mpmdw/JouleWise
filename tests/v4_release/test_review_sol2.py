"""Sol seat 2: synthetic witnesses against release-tools @ 99875485d.

Expected failures assert the required behavior, rather than blessing the defect.
Remove the corresponding decorator when its fix lands. Only Git code objects and
the repository's synthetic rehearsal are used; no study custody is accessed.
"""
import ast
import copy
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import shutil
from statistics import fmean
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

from tests.v4_release import support

sys.path.insert(0, str(support.REPO / "scripts"))
import compare_v4_recompute as comparator  # noqa: E402
import release_v4 as release  # noqa: E402


def pinned_source(commit, path):
    return subprocess.run(
        ["git", "-C", str(support.REPO), "show", f"{commit}:{path}"],
        check=True, capture_output=True,
    ).stdout.decode()


def load_pinned(directory, name, commit, path):
    target = directory / (name + ".py")
    target.write_text(pinned_source(commit, path))
    spec = importlib.util.spec_from_file_location(name, target)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def inventory(fill):
    body = {k: v for k, v in fill.items() if k != "leaf_inventory"}
    fill["leaf_inventory"] = [
        dict(pointer=p, kind="null" if v is None else "bool" if type(v) is bool
             else "number" if type(v) in (int, float) else "string")
        for p, v in comparator.leaves(body).items()
    ]


@unittest.skipUnless(support.have_commits(), "pinned build objects unavailable")
class RegisteredTextWitnesses(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix="jw-v4-sol2-text-")
        root = Path(cls.tmp.name)
        cls.rec = load_pinned(root, "review_sol2_recompute", support.RECOMPUTE_COMMIT,
                              "scripts/independent_recompute_v4.py")
        cls.cadence = load_pinned(root, "review_sol2_cadence", support.ENGINE_COMMIT,
                                  "joulewise/align/apple/v4_cadence.py")

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def calibration(self, count=8):
        windows, eligibility, barred, ledger = [], {}, {}, []
        for i in range(1, count + 1):
            wid = f"C{i}"
            members = [dict(run_id=f"{wid}-{p}-{j}", kind="benign", model="D", pair=p)
                       for p in ("spam", "bank") for j in range(7)]
            windows.append(dict(window_id=wid, role="calibration", members=members,
                                record={"adjudication": {"final": True}}))
            eligibility[wid] = {m["run_id"]: dict(captured=True, eligible=True) for m in members}
            barred[wid] = i == 1
            counts = dict.fromkeys(("spam", "bank"), 0 if barred[wid] else 7)
            # This is the exact shape the frozen engine passes to its predicate:
            # it has already zeroed counts, and drops the bar identity entirely.
            ledger.append(dict(window=wid, status="final", captured_members=14,
                               eligible_benign=counts, eligible_total=sum(counts.values())))
        return windows, eligibility, barred, ledger

    @unittest.expectedFailure
    def test_r22_barred_window_does_not_complete_eight_admitted_windows(self):
        """F1: R22-2/R24 require eight admitted windows, not eight captured ones."""
        windows, eligibility, barred, ledger = self.calibration()
        r = self.rec.calibration_stop(windows, eligibility, barred)
        e = self.cadence.calibration_stop(ledger)
        self.assertEqual(r["eligible_benign_totals"], {"spam": 49, "bank": 49})
        self.assertEqual(e["eligible_by_pair"], {"spam": 49, "bank": 49})
        self.assertEqual((e["decision"], r["status"]), ("continue", "continue"))

    @unittest.expectedFailure
    def test_r24_c9_replacement_is_not_a_ninth_counted_window(self):
        """F1: C1 barred plus C2-C9 healthy is eight admitted, not nine."""
        windows, eligibility, barred, ledger = self.calibration(9)
        errors, results = [], []
        for fn, args in ((self.rec.calibration_stop, (windows, eligibility, barred)),
                         (self.cadence.calibration_stop, (ledger,))):
            try:
                results.append(fn(*args))
            except (ValueError, self.rec.Refusal) as exc:
                errors.append(type(exc).__name__)
        self.assertEqual(errors, [], "both pinned predicates reject the legitimate reserve")
        self.assertEqual(len(results), 2)

    @unittest.expectedFailure
    def test_r24_engine_roster_accepts_predeclared_c9(self):
        """F1: execute the pinned ORDER and roster definitions, without loading data."""
        source = ast.parse(pinned_source(support.ENGINE_COMMIT,
                                        "joulewise/align/v4_analysis/engine.py"))
        nodes = [n for n in source.body if
                 (isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "ORDER"
                                                    for t in n.targets))
                 or (isinstance(n, ast.FunctionDef) and n.name == "roster")]
        namespace = {}
        exec(compile(ast.Module(body=nodes, type_ignores=[]), "pinned-engine-roster", "exec"), namespace)
        try:
            namespace["roster"]("C9")
        except ValueError as exc:
            self.fail(str(exc))

    @unittest.expectedFailure
    def test_r25_u3_budget_includes_six_reserve_comparisons(self):
        """F1: the engine must use R25's expanded N, even before a reserve is needed."""
        source = ast.parse(pinned_source(support.ENGINE_COMMIT,
                                        "joulewise/align/v4_analysis/acceptance.py"))
        nodes = [n for n in source.body if isinstance(n, ast.FunctionDef)
                 and n.name in ("_series_tail", "u3_derivation")]
        namespace = {"math": math, "fmean": fmean}
        exec(compile(ast.Module(body=nodes, type_ignores=[]), "pinned-engine-u3", "exec"), namespace)
        differences = [0.004, -0.006, 0.003, 0.005, -0.002, 0.001, -0.004]
        evidence = dict(pilot_pairs=[dict(session=str(i), ordinals=[2, 7], prespecified=True,
                                          token_identical=True,
                                          energies_j=[1000 * (1 - r / 2), 1000 * (1 + r / 2)])
                                    for i, r in enumerate(differences)], frozen_before_W1=True,
                        r1_d_screen=dict(token_identical=True, eligible=True, relative_difference=0.0))
        engine_bar = namespace["u3_derivation"](evidence)
        rec_bar = self.rec.u3_bar(dict(signed=True, beta=0.05, N=22, f=1.5, r1_d_screen=0.0,
                                      pilot_relative_differences=differences))
        self.assertEqual(rec_bar["N"], 22)
        self.assertEqual(engine_bar["comparisons"], rec_bar["N"])

    @unittest.expectedFailure
    def test_runbook_command_uses_the_release_recompute_pin(self):
        """F6: copying the documented release command must not select an obsolete build."""
        text = (support.REPO / "docs/analysis/v4/RELEASE-RUNBOOK-v4.md").read_text()
        commits = re.findall(r"--recompute-commit ([0-9a-f]{40})", text)
        self.assertTrue(commits)
        self.assertEqual(set(commits), {release.RELEASE_RECOMPUTE_COMMIT})


@unittest.skipUnless(support.have_commits(), "pinned build objects unavailable")
class ComparatorWitnesses(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = support.rehearsal("full")
        cls.tmp = tempfile.TemporaryDirectory(prefix="jw-v4-sol2-compare-")
        cls.root = Path(cls.tmp.name)
        cls.fill = json.loads((cls.base / "engine-out/fill.json").read_text())
        cls.rec = json.loads((cls.base / "recompute-out.json").read_text())
        cls.cross = json.loads((cls.base / "crosswalk.json").read_text())
        code, public, _ = support.compare(cls.base, cls.root / "baseline.json")
        if (code, public.get("verdict")) != (0, "agree"):
            raise AssertionError("the unmodified rehearsal must agree before applying witnesses")

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def compare(self, name, fill=None, rec=None):
        paths = {}
        for key, doc in (("fill", fill), ("recompute", rec)):
            if doc is not None:
                if key == "fill":
                    inventory(doc)
                target = self.root / f"{name}-{key}.json"
                target.write_text(json.dumps(doc))
                paths[key] = target
        return support.compare(self.base, self.root / f"{name}-out.json", **paths)

    @unittest.expectedFailure
    def test_r26_missing_one_h_star_row_cannot_agree(self):
        """F2: a partial family survives the empty-family guard and has no unit manifest."""
        fill = copy.deepcopy(self.fill)
        rows = [s for f in fill["fits"] for s in f["scores"] if "H_star" in s]
        self.assertGreater(len(rows), 1)
        del rows[0]["H_star"]
        code, _, _ = self.compare("missing-hstar", fill=fill)
        self.assertNotEqual(code, 0)

    @unittest.expectedFailure
    def test_r26_missing_one_grid_dose_cannot_agree(self):
        """F2: units are per scored member, so deletion of a dose leaves counts unchanged."""
        fill = copy.deepcopy(self.fill)
        score = next(s for f in fill["fits"] if f["convention"] == "counts_logged"
                     for s in f["scores"] if "H_star" in s
                     and any(p["nominal_H"] == 1536 for p in s["H_grid"]))
        score["H_grid"] = [p for p in score["H_grid"] if p["nominal_H"] != 1536]
        code, _, _ = self.compare("missing-dose", fill=fill)
        self.assertNotEqual(code, 0)

    @unittest.expectedFailure
    def test_u5_negative_slope_agrees_on_absolute_point_shift(self):
        """F7: A15 uses a magnitude; negating a slope must not reverse that magnitude."""
        fill, rec = copy.deepcopy(self.fill), copy.deepcopy(self.rec)
        eu, ru = fill["U5"], rec["acceptance"]["U5"]
        self.assertGreater(eu["beta_T_j_per_c"], 0)
        eu["beta_T_j_per_c"] *= -1
        ru["beta_T"] *= -1
        eu["beta_T_ci90"] = [-v for v in reversed(eu["beta_T_ci90"])]
        ru["interval"] = [-v for v in reversed(ru["interval"])]
        eu["intercept_j"] = 3000.0 - eu["intercept_j"]
        # Reflect the synthetic designed-state energies as well. Neither the
        # magnitude, the absolute interval bound nor the U5 verdict changes.
        for state in eu["designed_states"]:
            state["turn_owned_j"] = 3000.0 - state["turn_owned_j"]
        code, _, _ = self.compare("u5-negative", fill=fill, rec=rec)
        self.assertEqual(code, 0)

    @unittest.expectedFailure
    def test_u5_interval_slope_bound_is_scaled_to_joules(self):
        """F7: abs_upper_90 is J/C; upper90_shift_j must multiply delta_slow_c."""
        fill, rec = copy.deepcopy(self.fill), copy.deepcopy(self.rec)
        eu, ru = fill["U5"], rec["acceptance"]["U5"]
        eu["delta_slow_c"] *= 2
        ru["delta_slow_c"] *= 2
        eu["point_shift_j"] *= 2
        eu["upper90_shift_j"] *= 2
        code, _, _ = self.compare("u5-delta", fill=fill, rec=rec)
        self.assertEqual(code, 0)

    def test_a12_not_applicable_release_part_stays_not_applicable(self):
        """Positive control: A12's string-valued not-applicable part compares exactly."""
        engine = comparator.Engine({}, {})
        bars, _ = comparator.load_bars(release.RELEASE_BARS)
        c = comparator.Comparison(engine, {}, self.cross, bars)
        engine.fill["U2"] = dict(status="pass", g0_slow_range_c=0.0,
                                  parts={"a": "pass", "b": "not_applicable"})
        rec = dict(verdict="pass", g0_slow_range_c=0.0,
                   parts={"a_g0_slow_range_le_3c": True,
                          "b_releases_verified_within_delta": "not_applicable"})
        c._u2(("fill", "U2"), rec, ("synthetic",))
        self.assertTrue(all(r["ok"] for r in c.rows))

    def test_a27_plaintext_token_counts_refuse_without_public_value(self):
        """Positive control: the engine's scored C-sabotage count leak is refused."""
        fill = copy.deepcopy(self.fill)
        row = next(r for r in fill["realized_counts"] if r.get("status") == "sealed")
        row["rows"] = [dict(decode_tokens=123456789)]
        code, public, _ = self.compare("sealed-token-leak", fill=fill)
        self.assertEqual((code, public["reason"]), (2, "unmapped_leaf"))
        self.assertNotIn("123456789", json.dumps(public))
        self.assertNotIn("rows", public)


@unittest.skipUnless(support.have_commits(), "pinned build objects unavailable")
class ReleaseWitnesses(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = support.rehearsal("full")
        cls.tmp = tempfile.TemporaryDirectory(prefix="jw-v4-sol2-release-")
        cls.root = Path(cls.tmp.name)
        cls.checkout = support.release_checkout(cls.root / "checkout")

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def custody(self, name):
        target = self.root / name
        shutil.copytree(self.base, target, copy_function=os.link)
        return target

    @staticmethod
    def replace_json(path, doc):
        # Copies share immutable fixture inodes. Never write through a hard link.
        path.unlink()
        path.write_text(json.dumps(doc))

    @unittest.expectedFailure
    def test_pinned_engine_identity_cannot_be_relabelled_in_the_record(self):
        """F3: a stale/modified producer may be recorded under the default engine pin."""
        root = self.custody("foreign-producer")
        fill = json.loads((root / "engine-out/fill.json").read_text())
        fill["threshold_freeze"]["loaded_scorer_sha256"] = "0" * 64
        fill["threshold_freeze"]["raw_reducer_sha256"] = "1" * 64
        inventory(fill)
        self.replace_json(root / "engine-out/fill.json", fill)
        self.replace_json(root / "engine-out/thresholds.json", fill["threshold_freeze"])
        (root / "engine-run-record.json").unlink()
        support.write_record(root)  # synthetic writer hashes files and defaults the commit label to the pin
        code, _, _ = support.run_release(self.checkout, root, self.root / "foreign-out", workers=1)
        self.assertEqual(code, 2)

    @unittest.expectedFailure
    def test_malformed_census_is_refused_2_not_an_uncaught_exit_1(self):
        """F5: a malformed but valid-JSON export must retain the refused exit contract."""
        root = self.custody("malformed-census")
        fill = json.loads((root / "engine-out/fill.json").read_text())
        fill["input_census"] = [None]
        inventory(fill)
        self.replace_json(root / "engine-out/fill.json", fill)
        (root / "engine-run-record.json").unlink()
        support.write_record(root)
        code, _, _ = support.run_release(self.checkout, root, self.root / "malformed-out", workers=1)
        self.assertEqual(code, 2)

    @unittest.expectedFailure
    def test_changed_referenced_journal_refuses_in_digest_stage(self):
        """F4: isolated stage-(a) witness; all synthetic records are sealed before corruption."""
        root = self.root / "journal-custody"
        root.mkdir()
        out = root / "engine-out"
        out.mkdir()
        rec = root / "recompute/windows/C1"
        rec.mkdir(parents=True)
        journal = root / "journal.json"
        journal.write_text("[]\n")
        manifest = root / "raw-source.json"
        manifest.write_text(json.dumps({"members": [{"run_id": "run", "journal": {
            "path": journal.name, "sha256": support.sha256(journal)}}]}))
        (root / "engine-input.json").write_text(json.dumps({"windows": [{
            "attempt_id": "C1#1", "roster": [{"run_id": "run", "ordinal": 6}],
            "raw_source": {"path": manifest.name, "sha256": support.sha256(manifest)}}]}))
        (out / "fill.json").write_text(json.dumps({"input_census": [
            {"path": manifest.name, "sha256": support.sha256(manifest)}]}))
        (out / "verdict.json").write_text('{"status":"provisional"}')
        (out / "thresholds.json").write_text("{}")
        (rec / "window.json").write_text(json.dumps({"members": [{"run_id": "run", "ordinal": 6}]}))
        (root / "crosswalk.json").write_text(json.dumps({"members": [{
            "attempt_id": "C1#1", "engine_run_id": "run", "ordinal": 6,
            "recompute_window_id": "C1", "recompute_run_id": "run"}]}))
        support.write_record(root)
        journal.write_text('[{"changed_after_engine":true}]\n')
        restricted = root / "synthetic-private"
        restricted.mkdir(mode=0o700)
        args = SimpleNamespace(engine_commit=support.ENGINE_COMMIT,
                               recompute_commit=support.RECOMPUTE_COMMIT, programs_repo=support.REPO,
                               engine_record=root / "engine-run-record.json",
                               engine_input=root / "engine-input.json", engine_out=out,
                               recompute_root=root / "recompute", crosswalk=root / "crosswalk.json")
        with mock.patch.object(release, "ROOT", self.checkout):
            with self.assertRaises(release.Refused):
                release.stage_digests(args, restricted)


if __name__ == "__main__":
    unittest.main()
