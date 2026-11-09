"""Sol1 review witnesses, synthetic only, first written against release-tools 99875485d.

INVERTED (F1-F4 fixed): each witness that asserted an observed defect now asserts the registered
behaviour, so a green run means the defect is gone. Adaptations to the fixed contract are marked
"inverted:". No real custody, model weights, or measurement code is used.
"""
import ast
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from tests.v4_release import support

sys.path.insert(0, str(support.REPO / "scripts"))
import compare_v4_recompute as cmp
import release_v4 as release


def pinned_module(commit, rel, directory, name):
    """Extract only the requested tracked Python file; never inspect custody."""
    raw = subprocess.run(["git", "-C", str(support.REPO), "show", f"{commit}:{rel}"],
                         capture_output=True, check=True).stdout
    path = directory / (name + ".py")
    path.write_bytes(raw)
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def pinned_function(commit, rel, name):
    """Load a function verbatim, without importing unrelated module dependencies.

    The W1 empty-input branch uses no module globals. Its internal import of
    contrast_delivery is harmless: delta_slow_c=None avoids calling that helper.
    """
    source = subprocess.run(["git", "-C", str(support.REPO), "show", f"{commit}:{rel}"],
                            capture_output=True, check=True).stdout
    node = next(n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef) and n.name == name)
    namespace = {}
    exec(compile(ast.Module(body=[node], type_ignores=[]), rel, "exec"), namespace)
    return namespace[name]


@unittest.skipUnless(support.have_commits(), "pinned builds unavailable")
class RegisteredTextWitnesses(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix="jw-sol1-text-")
        root = Path(cls.tmp.name)
        cls.rec = pinned_module(support.RECOMPUTE_COMMIT, "scripts/independent_recompute_v4.py",
                                root, "sol1_recompute")
        cls.cadence = pinned_module(support.ENGINE_COMMIT, "joulewise/align/apple/v4_cadence.py",
                                    root, "sol1_cadence")
        cls.thermal_decider = staticmethod(pinned_function(
            support.ENGINE_COMMIT, "joulewise/align/apple/thermal_desk.py", "deciding_experiment"))

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def calibration(self, n):
        windows, eligibility, barred, engine_rows = [], {}, {}, []
        for i in range(1, n + 1):
            wid = f"C{i}"
            members = [dict(run_id=f"{wid}-{p}-{j}", kind="benign", model="D", pair=p)
                       for p in ("spam", "bank") for j in range(7)]
            windows.append(dict(window_id=wid, role="calibration", members=members,
                                record=dict(adjudication=dict(final=True))))
            eligibility[wid] = {m["run_id"]: dict(captured=True, eligible=True) for m in members}
            barred[wid] = i == 1
            counts = dict(spam=0 if i == 1 else 7, bank=0 if i == 1 else 7)
            row = dict(window=wid, status="final", captured_members=14,
                       eligible_benign=counts, eligible_total=sum(counts.values()))
            if i == 1:
                row["barred"] = "u1_u3_fail"     # inverted: r23i ledger rows carry the committed bar
            engine_rows.append(row)
        return windows, eligibility, barred, engine_rows

    def test_r22_both_builds_continue_after_only_seven_admitted_windows(self):
        """F1 (inverted): R22/R24 require 8 admitted windows; barred C1 is not counted on either side."""
        windows, eligibility, barred, rows = self.calibration(8)
        rec = self.rec.calibration_stop(windows, eligibility, barred)
        eng = self.cadence.calibration_stop(rows)
        self.assertEqual(sum(not b for b in barred.values()), 7)
        self.assertEqual(rec["status"], "continue")
        self.assertEqual(eng["decision"], "continue")
        self.assertEqual(rec["counted_windows"], 7)
        self.assertFalse(rec["windows"][0]["counted"])
        self.assertEqual(rec["barred_windows"], ["C1"])

    def test_r24_valid_eighth_admitted_window_completes(self):
        """F1 (inverted): C9 legitimately replaces C1; both admit eight and complete."""
        windows, eligibility, barred, rows = self.calibration(9)
        self.assertEqual(sum(not b for b in barred.values()), 8)
        rec = self.rec.calibration_stop(windows, eligibility, barred)
        eng = self.cadence.calibration_stop(rows)
        self.assertEqual((rec["status"], rec["admitted_windows"], rec["replacements_used"]),
                         ("calibration_complete", 8, 1))
        self.assertEqual(eng["decision"], "calibration_complete")
        self.assertEqual(rec["eligible_benign_totals"], eng["eligible_by_pair"])

    def test_a19_legitimate_unavailable_w1_agrees(self):
        """F3 (inverted): both producers say INCONCLUSIVE with reason_code insufficient_contrast_runs and no
        fit statistics; the comparator agrees on the code and the common absence."""
        eng = self.thermal_decider([], v4=True, delta_slow_c=None)
        rec = self.rec.w1_contrast(dict(record={}, members=[]), {}, {})
        self.assertEqual(eng["verdict"], rec["verdict"])
        self.assertEqual(eng["verdict"], "INCONCLUSIVE")
        bars, _ = cmp.load_bars(release.RELEASE_BARS)
        # A structure-only dummy keeps this focused on w1(), without inventing
        # fit numbers. The missing contrast is a registered A19 producer path.
        member = dict(window="W1", attempt_id="W1#1", ordinal=1, engine_run_id="a",
                      recompute_window_id="W1", recompute_run_id="a", pair="spam", condition="benign",
                      model="30B", role="anchor", captured=False, seed_index=1)
        c = cmp.Comparison(cmp.Engine(dict(W1=dict(contrast=eng)), {}),
                           dict(claim=dict(w1_contrast=rec)),
                           dict(schema="joulewise.v4_release.crosswalk.v1", members=[member]), bars)
        c.w1()
        self.assertEqual(eng.get("reason_code"), "insufficient_contrast_runs")
        self.assertEqual(rec.get("reason_code"), "insufficient_contrast_runs")
        bad = [r for r in c.rows if not r["ok"]]
        self.assertEqual(bad, [])
        keys = {json.dumps(r["key"]) for r in c.rows}
        self.assertIn(json.dumps("reason_code"), keys)
        self.assertIn(json.dumps(["absent", "arm_effect_j"]), keys)
        self.assertNotIn(json.dumps("reason"), keys)          # reason strings are never compared


@unittest.skipUnless(support.have_commits(), "pinned builds unavailable")
class ReleaseCoverageWitnesses(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = support.rehearsal("full")
        cls.tmp = tempfile.TemporaryDirectory(prefix="jw-sol1-release-")
        cls.dir = Path(cls.tmp.name)
        cls.fill = json.loads((cls.base / "engine-out/fill.json").read_text())
        cls.verdict = json.loads((cls.base / "engine-out/verdict.json").read_text())
        cls.rec = json.loads((cls.base / "recompute-out.json").read_text())
        cls.cross = json.loads((cls.base / "crosswalk.json").read_text())

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def compare_fill(self, name, fill):
        body = {k: v for k, v in fill.items() if k != "leaf_inventory"}
        fill["leaf_inventory"] = [dict(pointer=p, kind="null" if v is None else "bool" if type(v) is bool
                                       else "number" if type(v) in (int, float) else "string")
                                  for p, v in cmp.leaves(body).items()]
        path = self.dir / (name + "-fill.json")
        path.write_text(json.dumps(fill))
        return cmp.compare(path, self.base / "engine-out/verdict.json", self.base / "recompute-out.json",
                           self.base / "crosswalk.json", release.RELEASE_BARS,
                           identity_path=support.engine_identity_file())   # inverted: identity is checked

    def assert_cannot_agree(self, name, fill, family="row_completeness"):
        """Inverted: the mutation must refuse through the named refusing family (no unmapped leaf)."""
        pub, detail, code = self.compare_fill(name, fill)
        self.assertEqual((code, pub["verdict"], pub["unmapped_leaves"]), (2, "refused", 0))
        self.assertEqual(pub["families"][family]["verdict"], "refused")
        return detail

    def test_baseline_agrees(self):          # control
        pub, _, code = self.compare_fill("baseline", copy.deepcopy(self.fill))
        self.assertEqual((code, pub["verdict"]), (0, "agree"))

    def test_r26_whole_h_grid_can_disappear(self):
        """F2a (inverted): every scored member losing the required dose table refuses."""
        fill = copy.deepcopy(self.fill)
        removed = sum(len(s.pop("H_grid", [])) for f in fill["fits"] for s in f["scores"])
        self.assertGreater(removed, 0)
        self.assert_cannot_agree("missing-grid", fill)

    def test_r26_interior_carrier_curve_dose_can_disappear(self):
        """F2b (inverted): R26 says every dose; a partial curve refuses."""
        fill = copy.deepcopy(self.fill)
        for pair in fill["benign_carriers"]["pairs"].values():
            self.assertTrue(any(row[0] == 384 for row in pair["curve"]))
            pair["curve"] = [row for row in pair["curve"] if row[0] != 384]
            pair["n_by_h"].pop("384")
        self.assert_cannot_agree("missing-dose", fill)

    def test_a13_u3_replay_pair_can_disappear(self):
        """F2c (inverted): dropping the required replay pair in both print locations refuses."""
        fill = copy.deepcopy(self.fill)
        model = cmp.D_MODEL
        locations = [fill["acceptance"]["C2"][model]["U3"]]
        locations += [w["checks"][model]["U3"] for w in fill["windows"] if w["window"] == "C2"]
        for row in locations:
            self.assertTrue(row["pairs"])
            row["pairs"] = []
        self.assert_cannot_agree("missing-pair", fill)

    def test_per_turn_residual_tail_can_disappear(self):
        """F2d (inverted): a member's missing residual rows refuse."""
        fill = copy.deepcopy(self.fill)
        removed = 0
        for fit in fill["fits"]:
            for score in fit["scores"]:
                vals = score["turn_residuals_j"]
                removed += max(0, len(vals) - 1)
                score["turn_residuals_j"] = vals[:1]
        self.assertGreater(removed, 0)
        self.assert_cannot_agree("missing-turns", fill)

    def test_changed_loaded_scorer_binding_refuses(self):
        """F4 (inverted): a producer identity mismatch refuses (producer_identity), never exempt."""
        fill = copy.deepcopy(self.fill)
        key = "loaded_scorer_sha256"
        self.assertIn(key, fill["threshold_freeze"])
        fill["threshold_freeze"][key] = "0" * 64
        detail = self.assert_cannot_agree("scorer-binding", fill, "producer_identity")
        self.assertNotIn("build_digests", detail["coverage_map"]["/fill/threshold_freeze/" + key])
        # Without the pinned identity the producer leaves stay unmapped and refuse too.
        body = copy.deepcopy(self.fill)
        path = self.dir / "no-identity-fill.json"
        path.write_text(json.dumps(body))
        pub, _, code = cmp.compare(path, self.base / "engine-out/verdict.json", self.base / "recompute-out.json",
                                   self.base / "crosswalk.json", release.RELEASE_BARS)
        self.assertEqual((code, pub["reason"]), (2, "unmapped_leaf"))

    def test_release_refuses_changed_producer_identity_in_recorded_artifacts(self):
        """F4 end-to-end (inverted): a record's commit label cannot override contradictory producer identity.

        This models an operator writing the default engine commit into the run
        record for outputs made with different loaded code. All input files and
        numerical output are unchanged; no raw synthetic file is rewritten.
        """
        fill = copy.deepcopy(self.fill)
        fill["threshold_freeze"]["loaded_scorer_sha256"] = "0" * 64
        self.compare_fill("producer", fill)  # refresh the printed inventory
        out = self.dir / "different-producer"
        out.mkdir()
        (out / "fill.json").write_text(json.dumps(fill))
        (out / "verdict.json").write_bytes((self.base / "engine-out/verdict.json").read_bytes())
        freeze = json.loads((self.base / "engine-out/thresholds.json").read_text())
        freeze["loaded_scorer_sha256"] = "0" * 64
        (out / "thresholds.json").write_text(json.dumps(freeze))
        record = dict(schema=release.ENGINE_RECORD_SCHEMA, engine_commit=support.ENGINE_COMMIT,
                      input_sha256=support.sha256(self.base / "engine-input.json"),
                      **{name + "_sha256": support.sha256(out / (name + ".json"))
                         for name in ("fill", "verdict", "thresholds")})
        record_path = self.dir / "different-producer-record.json"
        record_path.write_text(json.dumps(record))
        checkout = support.release_checkout(self.dir / "release-checkout")
        code, public, _ = support.run_release(
            checkout, self.base, self.dir / "different-producer-release",
            extra=("--engine-out", str(out), "--engine-record", str(record_path)))
        self.assertEqual((code, public["verdict"], public["reason"]), (2, "refused", "engine_producer_identity_differs"))

    def test_a27_token_count_leak_refuses(self):
        """Control: the engine-side A27 token-count guard actually refuses."""
        fill = copy.deepcopy(self.fill)
        row = next(r for r in fill["realized_counts"] if r.get("status") == "sealed")
        row["rows"] = [dict(decode_tokens=123)]
        pub, _, code = self.compare_fill("sealed-count", fill)
        self.assertEqual((code, pub["reason"]), (2, "unmapped_leaf"))

    def test_refusal_takes_precedence_over_hold(self):
        """Control: simultaneous numeric hold and eligible-m refusal exits 2."""
        fill = copy.deepcopy(self.fill)
        fill["fits"][0]["scores"][0]["measured_j"] *= 1.1
        fill["calibration"]["eligible_by_pair"]["spam"] -= 1
        pub, _, code = self.compare_fill("precedence", fill)
        self.assertEqual((code, pub["verdict"]), (2, "refused"))
        self.assertEqual(pub["families"]["turn_owned_energy_j"]["verdict"], "hold")


if __name__ == "__main__":
    unittest.main()
