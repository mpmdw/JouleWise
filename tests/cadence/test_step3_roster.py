"""The step 3 adapter (RL-166 Q6). The behaviour tests run on a stubbed step 3 module, so no energy and no
bundle is read. Two tests use the real committed module: the sha256 gate, and failure attribution on bundles
that do not exist. A planted-truth run of the real module waits for the analyst seat's generator
(RL-166 §2 item 5)."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from joulewise.cadence_looks import manifest as lm
from joulewise.cadence_looks import step3_roster as sr

REPO = Path(__file__).resolve().parents[2]
OUTPUT_SCHEMA = REPO / "docs/process/cadence/looks/lm-interim-01.output.schema.json"

# A stand-in for step3_energy_ratios.py with the same entry points. A bundle string carries the stub's
# behaviour: "BAD" raises in analyse_leg with a message holding a value; "AGG" raises in analyse after the
# legs; "drift=<x>" sets the leg's drift; "est=0" makes gamma not estimable.
STUB = '''
import math
LEGS = [("/Users/x/night-align/a", "1112", "A1", "Automatic", "/Users/x/night-align/a")]
ORIGINAL_EIGHT = [LEGS[0][0]]

def _opt(bundle, key, default):
    for part in bundle.split(";"):
        if part.startswith(key + "="):
            return float(part.split("=", 1)[1])
    return default

def analyse_leg(leg, bundle):
    if "BAD" in bundle:
        raise KeyError("secret 123.456 J in " + bundle)
    return {"leg_id": leg[0]}, {"drift": _opt(bundle, "drift", 0.01), "est": _opt(bundle, "est", 1)}

def analyse(roots):
    internal = {}
    for leg in LEGS:
        o, i = analyse_leg(leg, roots[leg[0]])
        internal[leg[0]] = i
    if any("AGG" in roots[x[0]] for x in LEGS):
        raise ZeroDivisionError("secret 9.9 W")
    ids = [x[0] for x in LEGS]
    d = max(internal[x]["drift"] for x in ids)
    auto6 = [x for x in ids if x in ORIGINAL_EIGHT]
    d6 = max(internal[x]["drift"] for x in auto6) if auto6 else None
    return {"schema": "stub", "legs": [{"leg_id": x} for x in ids],
            "ii_gamma_per_degC": {"all_nine_legs": {"slope": 0.004, "n_obs": 10}, "leave_one_leg_out": {x: 0.004 for x in ids},
                                  "max_abs_over_reported": 0.004},
            "gamma_estimability": {"estimable": all(internal[x]["est"] for x in ids), "max_range_c": 3.0},
            "iii_precut_drift": {"drift_fraction_linear": {"six_automatic_legs": d6, "seven_automatic_legs_incl_partc": d},
                                 "drift_fraction_exp_form": {"six_automatic_legs": None if d6 is None else math.expm1(d6),
                                                             "seven_automatic_legs_incl_partc": math.expm1(d)}},
            "iv_jpt_after_over_before": {"per_leg": {x: 0.9 for x in ids}, "automatic_median": 0.91,
                                         "automatic_min": 0.85, "automatic_max": 0.96},
            "v_block_ratio_spread": {"all_nine_legs": [1, 2, 3]},
            "vi_slope_lnE_on_lnclock": {"all_blocks_k_ge_1_all_nine_legs": {"slope": 1.59},
                                        "all_blocks_leave_one_leg_out": {x: 1.5 for x in ids}}}

def custody_check(obj, path="$"):
    leg_ids = {leg[0] for leg in LEGS}
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k.endswith("_j"):
                raise ValueError("forbidden key")
            custody_check(v, path + "." + k)
'''


def entry(key, size, bundle="ok", day="2026-11-15", **kw):
    return {"key": key, "day": day, "bundle": bundle, "role": "fit", "leg_type": "A", "included": True,
            "prompt_tokens_nominal": size, **kw}


class Base(unittest.TestCase):
    def setUp(self):
        d = Path(tempfile.mkdtemp(prefix="s3r-"))
        self.addCleanup(lambda: shutil.rmtree(d, ignore_errors=True))
        self.stub = d / "stub_step3.py"
        self.stub.write_text(STUB, encoding="utf-8")
        self.sha = hashlib.sha256(self.stub.read_bytes()).hexdigest()
        self.modules = []

    def loader(self):
        m = sr.load_step3(self.stub, self.sha)
        self.modules.append(m)
        return m


class Rebinding(Base):
    def test_one_fresh_module_per_cell_with_legs_rebound(self):
        entries = [entry("dev-01:dev-01-s01:L001", 2000, day="2026-11-14"), entry("dev-01:dev-01-s01:L002", 19458),
                   entry("dev-03:dev-03-s01:L001", 10000), entry("dev-03:dev-03-s01:L003", 10000),
                   entry("dev-02:dev-02-s01:L001", 2000)]
        out = sr.run_roster(entries, loader=self.loader)
        self.assertEqual([c["prompt_tokens"] for c in out["cells"]], [10000, 2000, 19458])   # 10k first
        self.assertEqual(len(self.modules), 3)
        self.assertEqual(len({id(m) for m in self.modules}), 3)
        m10 = self.modules[0]
        self.assertEqual(m10.LEGS, [("dev-03:dev-03-s01:L001", "2026-11-15", "dev-03:dev-03-s01:L001", "Automatic", "ok"),
                                    ("dev-03:dev-03-s01:L003", "2026-11-15", "dev-03:dev-03-s01:L003", "Automatic", "ok")])
        self.assertEqual(m10.ORIGINAL_EIGHT, ["dev-03:dev-03-s01:L001", "dev-03:dev-03-s01:L003"])
        self.assertEqual(self.modules[1].LEGS[0][1], "2026-11-14")            # the day rides in step 3's night slot

    def test_only_included_type_a_fit_legs_enter(self):
        entries = [entry("a", 10000), entry("b", 10000, included=False), entry("c", 10000, role="describe"),
                   entry("d", 10000, leg_type="H"), entry("e", 10000, leg_type="T")]
        sr.run_roster(entries, loader=self.loader)
        self.assertEqual([t[0] for t in self.modules[0].LEGS], ["a"])

    def test_projection_keeps_the_ruled_fields_and_drops_per_leg_lists(self):
        out = sr.run_roster([entry("a", 10000), entry("b", 10000)], loader=self.loader)
        cell = out["cells"][0]
        self.assertEqual(cell["status"], "ok")
        self.assertEqual(cell["n_legs"], 2)
        self.assertNotIn("leave_one_leg_out", cell["ii_gamma"])
        self.assertNotIn("all_blocks_leave_one_leg_out", cell["vi_slope_lnE_on_lnclock"])
        self.assertEqual(cell["iv_after_over_before"], {"median": 0.91, "min": 0.85, "max": 0.96})
        self.assertTrue(cell["gamma_estimable"])
        self.assertNotIn("v_block_ratio_spread", json.dumps(cell))
        self.assertNotIn("per_leg", json.dumps(cell))
        cell_schema = json.loads(OUTPUT_SCHEMA.read_text())["$defs"]["step3_output"]["properties"]["cells"]["items"]
        self.assertEqual(set(cell), set(cell_schema["required"]))


class Failures(Base):
    def test_a_raising_leg_is_named_by_type_left_out_and_counted(self):
        out = sr.run_roster([entry("a", 10000), entry("b", 10000, bundle="BAD"), entry("c", 10000)], loader=self.loader)
        cell = out["cells"][0]
        self.assertEqual(cell["status"], "ok")
        self.assertEqual(cell["n_legs"], 2)
        self.assertEqual(cell["failed_legs"], [{"key": "b", "exception_type": "KeyError"}])
        self.assertNotIn("secret", json.dumps(out))                          # never the message
        self.assertEqual([t[0] for t in self.modules[-1].LEGS], ["a", "c"])

    def test_two_failures_run_three_fail_the_cell(self):
        two = sr.run_roster([entry("a", 10000)] + [entry(k, 10000, bundle="BAD") for k in "xy"], loader=self.loader)
        self.assertEqual(two["cells"][0]["status"], "ok")
        self.assertEqual(len(two["cells"][0]["failed_legs"]), 2)
        three = sr.run_roster([entry("a", 10000)] + [entry(k, 10000, bundle="BAD") for k in "xyz"], loader=self.loader)
        cell = three["cells"][0]
        self.assertEqual(cell["status"], "not_run")
        self.assertEqual([f["key"] for f in cell["failed_legs"]], ["x", "y", "z"])
        self.assertIsNone(cell["iii_drift_fraction_linear"])

    def test_a_cell_level_exception_fails_the_cell(self):
        out = sr.run_roster([entry("a", 10000, bundle="AGG"), entry("b", 2000)], loader=self.loader)
        self.assertEqual(out["cells"][0]["status"], "not_run")
        self.assertEqual(out["cells"][0]["failed_legs"], [{"key": "(cell)", "exception_type": "ZeroDivisionError"}])
        self.assertEqual(out["cells"][1]["status"], "ok")
        self.assertNotIn("secret", json.dumps(out))

    def test_every_leg_failing_ends_the_cell(self):
        out = sr.run_roster([entry(k, 10000, bundle="BAD") for k in "xy"], loader=self.loader)
        self.assertEqual(out["cells"][0]["status"], "not_run")


class Tripwire(Base):
    def test_largest_drift_over_estimable_cells(self):
        entries = [entry("a", 10000, bundle="drift=0.03"), entry("b", 2000, bundle="drift=0.06"),
                   entry("c", 19458, bundle="drift=0.20;est=0")]               # not estimable: ignored
        out = sr.run_roster(entries, loader=self.loader)
        t = out["tripwire"]
        self.assertEqual((t["value"], t["cell"], t["trips"], t["decision"]), (0.06, 2000, False, "within"))
        self.assertEqual((t["threshold"], t["fallback_threshold"], t["threshold_applied"]), (0.08, 0.04, 0.08))
        out = sr.run_roster(entries, loader=self.loader, threshold=0.04)
        self.assertEqual((out["tripwire"]["trips"], out["tripwire"]["decision"]), (True, "to the research lead"))

    def test_boundary_and_not_evaluable(self):
        at = sr.run_roster([entry("a", 10000, bundle="drift=0.08")], loader=self.loader)["tripwire"]
        self.assertFalse(at["trips"])                                          # "above the threshold" trips
        above = sr.run_roster([entry("a", 10000, bundle="drift=0.0801")], loader=self.loader)["tripwire"]
        self.assertTrue(above["trips"])
        none = sr.run_roster([entry("a", 10000, bundle="drift=0.5;est=0")], loader=self.loader)["tripwire"]
        self.assertEqual((none["value"], none["trips"], none["decision"]), (None, None, "not_evaluable"))
        with self.assertRaises(sr.Step3Refused):
            sr.run_roster([entry("a", 10000)], loader=self.loader, threshold=0.05)

    def test_tripwire_keys_match_the_output_schema(self):
        out = sr.run_roster([entry("a", 10000)], loader=self.loader)
        schema = json.loads(OUTPUT_SCHEMA.read_text())["$defs"]["step3_output"]
        self.assertEqual(set(out) | {"schema", "stage1_sha256", "step3_sha256", "manifest_sha256", "code_sha256",
                                     "allow_draft", "synthetic", "ledger_gate"}, set(schema["required"]))
        self.assertEqual(set(out["tripwire"]), set(schema["properties"]["tripwire"]["required"]))


class RealModule(unittest.TestCase):
    def test_the_committed_bytes_load_and_an_edit_is_refused(self):
        self.assertEqual(hashlib.sha256(sr.STEP3_PATH.read_bytes()).hexdigest(), sr.STEP3_SHA256)
        m = sr.load_step3()
        self.assertTrue(callable(m.analyse) and callable(m.custody_check) and hasattr(m, "LEGS"))
        d = Path(tempfile.mkdtemp(prefix="s3r-real-"))
        self.addCleanup(lambda: shutil.rmtree(d, ignore_errors=True))
        edited = d / "step3_energy_ratios.py"
        edited.write_bytes(sr.STEP3_PATH.read_bytes() + b"\n# edit\n")
        with self.assertRaises(sr.Step3Refused):
            sr.load_step3(edited)

    def test_failure_attribution_on_the_real_module(self):
        d = Path(tempfile.mkdtemp(prefix="s3r-missing-"))
        self.addCleanup(lambda: shutil.rmtree(d, ignore_errors=True))
        legs = [{"key": f"dev-01:dev-01-s01:L00{i}", "day": "2026-11-14", "bundle": str(d / f"nope{i}")}
                for i in range(1, 5)]
        cell = sr.run_cell(10000, legs)
        self.assertEqual(cell["status"], "not_run")
        self.assertEqual(cell["failed_legs"], [{"key": f"dev-01:dev-01-s01:L00{i}", "exception_type": "FileNotFoundError"}
                                               for i in range(1, 4)])


class Stage1Custody(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="s3r-s1-"))
        self.addCleanup(lambda: shutil.rmtree(self.root, ignore_errors=True))
        legs = []
        for i, (cell, inc, role, typ) in enumerate([(10000, True, "fit", "A"), (2000, True, "fit", "A"),
                                                     (10000, False, "fit", "A"), (10000, True, "describe", "A"),
                                                     (10000, True, "fit", "T")], 1):
            span = "hp-01-s01" if role == "describe" else "dev-03-s01"
            ldir = self.root / span / "legs" / f"L00{i}"
            ldir.mkdir(parents=True)
            (ldir / "leg_record.json").write_text(json.dumps({"result": {"bundle": f"b{i}"}}))
            legs.append({"leg_key": f"{span}/L00{i}", "day": "2026-11-16", "role": role, "leg_type": typ,
                         "included": inc, "cell_prompt_tokens": cell})
        self.legs = legs
        for span in ("dev-03-s01", "hp-01-s01"):                      # synthetic custody (Mythos round-3 N1)
            (self.root / span / "runner_receipt.json").write_text(json.dumps({"synthetic": True}))
        self.stage1 = self.root / "stage1.json"
        self.roster_sha, self.verdicts_sha = "c" * 64, "e" * 64
        self.write_stage1()

    def write_stage1(self, mini=None, **changes):
        """The stage-1 file, bound to ``mini``'s manifest as it now stands (any manifest when None)."""
        from tests.cadence import look_minirepo as mr
        doc = {"schema": "joulewise.cadence_look_stage1.v1", "legs": self.legs, "synthetic": True,
               "manifest_sha256": (hashlib.sha256((mini / mr.MANIFEST).read_bytes()).hexdigest() if mini else "0" * 64),
               "code_sha256": {"input:roster_sha256": self.roster_sha, "input:rules_3_4_sha256": self.verdicts_sha}}
        doc.update(changes)
        self.stage1.write_text(json.dumps(doc))
        self.sha = hashlib.sha256(self.stage1.read_bytes()).hexdigest()
        return self.sha

    def test_entries_from_stage1(self):
        from joulewise.cadence_looks.inclusion_34 import span_dirs
        entries = sr.entries_from_stage1(json.loads(self.stage1.read_text()), span_dirs(self.root))
        self.assertEqual([e["key"] for e in entries], ["dev-03-s01/L001", "dev-03-s01/L002"])
        self.assertEqual(entries[0]["bundle"], str(self.root / "dev-03-s01/legs/L001/runtime/b1"))
        self.assertEqual(entries[1]["prompt_tokens_nominal"], 2000)

    def test_main_takes_stage1_by_hash_and_the_threshold_from_the_manifest(self):
        from tests.cadence import look_minirepo as mr
        mini = mr.mini_repo(self)
        self.write_stage1(mini)
        out = self.root / "step3.json"
        base = ["--manifest", mini / mr.MANIFEST, "--stage1", self.stage1, "--custody", self.root, "--out", out]
        r = mr.py(mini, "joulewise/cadence_looks/step3_roster.py", *base, "--stage1-sha256", "0" * 64, "--allow-draft")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertFalse(out.exists())
        r = mr.py(mini, "joulewise/cadence_looks/step3_roster.py", *base, "--stage1-sha256", self.sha, "--allow-draft")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        doc = json.loads(out.read_text())
        schema = json.loads(OUTPUT_SCHEMA.read_text())["$defs"]["step3_output"]
        self.assertEqual(set(doc), set(schema["required"]))
        self.assertEqual((doc["stage1_sha256"], doc["step3_sha256"]), (self.sha, sr.STEP3_SHA256))
        self.assertEqual([c["status"] for c in doc["cells"]], ["not_run", "not_run"])   # bundles absent here
        self.assertEqual(doc["tripwire"]["decision"], "not_evaluable")
        manifest = json.loads((mini / mr.MANIFEST).read_text())
        pins = {p: sha for _, p, sha in lm.code_refs(manifest)}
        self.assertEqual(doc["code_sha256"][lm.STEP3_PATH], pins[lm.STEP3_PATH])     # runs outside sys.modules
        self.assertEqual(doc["code_sha256"]["joulewise/cadence_looks/step3_roster.py"],
                         pins["joulewise/cadence_looks/step3_roster.py"])
        drift = next(d for d in manifest["decisions"] if d["id"] == "drift_tripwire")
        self.assertEqual(doc["tripwire"]["threshold_applied"], drift["threshold"])   # Mythos 11: frozen, not a flag
        r = mr.py(mini, "joulewise/cadence_looks/step3_roster.py", *base, "--stage1-sha256", self.sha, "--allow-draft",
                  "--threshold", "0.08")
        self.assertEqual(r.returncode, 2)                                              # no run-time threshold

    def test_main_needs_stage1_committed_in_looks(self):
        """Mythos 8, Sol N1 / Mythos N1: without --allow-draft, the COMMITTED LOOKS.json must name this stage-1 hash
        and its roster; a loose (uncommitted) ledger, a ledger off the shared history and a wrong roster refuse."""
        from tests.cadence import look_minirepo as mr
        mini = mr.mini_repo(self)
        mr.commit(mini)
        self.write_stage1(mini, allow_draft=False)
        out = self.root / "step3.json"
        base = ["--manifest", mini / mr.MANIFEST, "--stage1", self.stage1, "--stage1-sha256", self.sha,
                "--custody", self.root, "--out", out]
        r = mr.py(mini, "joulewise/cadence_looks/step3_roster.py", *base)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("stage 1 is not committed", r.stdout)
        # Sol's loose-LOOKS case: the right row, written but not committed
        mr.commit(mini, stage1_sha256=self.sha, roster_sha256=self.roster_sha, verdicts_sha256=self.verdicts_sha,
                  git_commit_it=False)
        r = mr.py(mini, "joulewise/cadence_looks/step3_roster.py", *base)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("differs from the one committed", r.stdout)
        self.assertFalse(out.exists())
        # committed, but not on the shared history
        mr.git_commit(mini, "local only", publish=False)
        r = mr.py(mini, "joulewise/cadence_looks/step3_roster.py", *base)
        self.assertEqual(r.returncode, 1)
        self.assertIn("is not on refs/remotes/origin/main", r.stdout)
        for ref in ("HEAD", "main", self_sha := mr.git(mini, "rev-parse", "HEAD").stdout.strip(), "origin/main~0"):
            r = mr.py(mini, "joulewise/cadence_looks/step3_roster.py", *base, "--ledger-ref", ref)  # Sol NEW-2
            self.assertEqual(r.returncode, 1, ref)
            self.assertIn("the shared ref is a remote-tracking branch", r.stdout)
            self.assertFalse(out.exists())
        # a detached HEAD on a campaign branch not yet on main: name that branch's remote-tracking ref (Mythos N3)
        mr.git(mini, "update-ref", "refs/remotes/origin/look", self_sha)
        mr.git(mini, "checkout", "-q", "--detach", self_sha)
        r = mr.py(mini, "joulewise/cadence_looks/step3_roster.py", *base)
        self.assertEqual(r.returncode, 1)
        r = mr.py(mini, "joulewise/cadence_looks/step3_roster.py", *base, "--ledger-ref", "origin/look")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(json.loads(out.read_text())["ledger_gate"]["ref"], "refs/remotes/origin/look")
        out.unlink()
        mr.git(mini, "checkout", "-q", "main")
        mr.git(mini, "update-ref", "refs/remotes/origin/main", "HEAD")
        r = mr.py(mini, "joulewise/cadence_looks/step3_roster.py", *base)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        doc = json.loads(out.read_text())
        self.assertIs(doc["allow_draft"], False)
        self.assertEqual(doc["manifest_sha256"], hashlib.sha256((mini / mr.MANIFEST).read_bytes()).hexdigest())
        head = mr.git(mini, "rev-parse", "HEAD").stdout.strip()
        self.assertEqual(doc["ledger_gate"], {"commit": head, "ref": "refs/remotes/origin/main", "ref_commit": head})
        # the roster and verdict hashes must be the ones stage 1 recorded (Mythos N7; round-3 N8)
        for field, fragment in (("roster_sha256", "is not the roster the stage-1 file records"),
                                ("verdicts_sha256", "is not the rules-3-4 verdict file the stage-1 file records")):
            hashes = {"roster_sha256": self.roster_sha, "verdicts_sha256": self.verdicts_sha, field: "d" * 64}
            mr.commit(mini, stage1_sha256=self.sha, **hashes)
            r = mr.py(mini, "joulewise/cadence_looks/step3_roster.py", *base)
            self.assertEqual(r.returncode, 1)
            self.assertIn(fragment, r.stdout)

    def test_allow_draft_needs_a_synthetic_stage1(self):
        """Mythos N2."""
        from tests.cadence import look_minirepo as mr
        mini = mr.mini_repo(self)
        sha = self.write_stage1(mini, synthetic=False)
        out = self.root / "step3.json"
        run = lambda sha: mr.py(mini, "joulewise/cadence_looks/step3_roster.py", "--manifest", mini / mr.MANIFEST,
                                "--stage1", self.stage1, "--stage1-sha256", sha, "--custody", self.root, "--out", out,
                                "--allow-draft")
        r = run(sha)
        self.assertEqual(r.returncode, 1)
        self.assertIn("--allow-draft on a stage-1 file that is not synthetic", r.stdout)
        self.assertFalse(out.exists())
        # Mythos round-3 N1: a synthetic stage-1 file over custody whose receipts are not synthetic
        sha = self.write_stage1(mini)
        (self.root / "hp-01-s01" / "runner_receipt.json").write_text(json.dumps({"roster": []}))
        r = run(sha)
        self.assertEqual(r.returncode, 1)
        self.assertIn("--allow-draft on custody that is not synthetic: hp-01-s01", r.stdout)
        self.assertFalse(out.exists())
        # Mythos round-3 N2: a stage-1 file made under another manifest is refused before any energy
        sha = self.write_stage1(None)
        r = run(sha)
        self.assertEqual(r.returncode, 1)
        self.assertIn("the stage-1 file was made under another manifest", r.stdout)


if __name__ == "__main__":
    unittest.main()


class RunsUnderIsolatedMode(unittest.TestCase):
    """RL-166 Q1: the look's code runs with -I. Both custody entry points run as files on the stdlib alone."""

    def test_both_files_start_under_dash_i(self):
        import subprocess
        import sys
        for rel in ("joulewise/cadence_looks/inclusion_34.py", "joulewise/cadence_looks/step3_roster.py"):
            r = subprocess.run([sys.executable, "-I", "-B", str(REPO / rel), "--help"], capture_output=True, text=True,
                               cwd=tempfile.gettempdir(), timeout=60)
            self.assertEqual(r.returncode, 0, (rel, r.stderr[-400:]))
