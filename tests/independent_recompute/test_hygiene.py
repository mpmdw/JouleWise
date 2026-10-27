"""RC-CMP-1 A5: structure-only public streams, the AN-18 partial exclusion
re-derivation and the recorded interpreter. Synthetic inputs only."""
import contextlib
import hashlib
import io
import json
from pathlib import Path
import platform
import tempfile
import unittest
from unittest import mock

from .support import dump, full_pack, recompute as r, run_cli

CATALOG = {"schema_version": "joulewise.flag_catalog.v1", "rules": {"cell_unit_minimum": 2}, "codes": {
    "m.bad": {"effect": "EXCLUDE_MEMBER", "family": "MEMBER_VALIDITY"},
    "s.hot": {"effect": "EXCLUDE_MEMBER", "family": "PHYSICS_IN_SPAN"},
    "w.dead": {"effect": "EXCLUDE_WINDOW", "family": "CALIBRATION"},
    "d.note": {"effect": "DISCLOSE", "family": "DIAGNOSTIC"},
    "neg8.midpoint_lost": {"effect": "DISCLOSE", "family": "NEG8"}}}


def flag(fid, code, level="member", run_id=None, interval=None, stage_id=None, plan_id="p1", attempt=1):
    return {"flag_id": fid, "code": code, "interval": {"monotonic_ns": interval},
            "scope": {"level": level, "run_id": run_id, "stage_id": stage_id, "plan_id": plan_id,
                      "attempt": attempt, "bundle_id": run_id},
            # A value the rule must never need; the expected document does not depend on it.
            "observed": {"energy_j": 12.3457}}


def roster(pack_id="ALPHA"):
    members, spans = [], {}
    for i in range(1, 4):
        for s in ("repeat", "quad"):
            for pos in (("",) if s == "repeat" else ("a1", "b1")):
                rid = f"c-{s[0]}{i}" + ("-" + pos if pos else "")
                members.append({"run_id": rid, "stage_id": "st-" + s,
                                "units": [{"cell_id": "c", "stratum": s, "unit_id": f"c-{s[0]}{i}"}]})
                spans[rid] = {"monotonic_ns": [100 * len(spans), 100 * len(spans) + 50]}
    members.append({"run_id": "ref", "stage_id": "ref", "units": []})
    spans["ref"] = {"monotonic_ns": [5000, 5050]}
    return ({"pack_id": pack_id, "plan_id": "p1", "attempt": 1, "members": members,
             "cells": [{"cell_id": "c", "target": True, "strata": ["quad", "repeat"]}]}, spans)


class RederivationTests(unittest.TestCase):
    def derive(self, flags, pack_id="ALPHA", bundles=None):
        ros, spans = roster(pack_id)
        if bundles is not None:
            ros["bundles"] = bundles
        return r.rederive_exclusions(flags, ros, spans, CATALOG, "sha")

    def test_hand_derived_member_interval_stage_window_and_foreign_rules(self):
        # Members in plan order: c-r1 0, c-q1-a1 1, c-q1-b1 2, c-r2 3, c-q2-a1 4, c-q2-b1 5, c-r3 6, ...
        flags = [flag("f1", "m.bad", run_id="c-r1"),
                 flag("f1", "m.bad", run_id="c-r2"),                         # duplicate flag id: ignored
                 flag("f2", "s.hot", level="window", interval=[420, 430]),    # overlaps c-q2-a1 [400, 450] only
                 flag("f3", "s.hot", level="stage", stage_id="st-quad", interval=None),  # every quad member
                 flag("f4", "m.bad", run_id="c-r3", plan_id="other"),         # foreign plan: ignored
                 flag("f5", "d.note", level="window"),
                 flag("f6", "unknown.code", level="window")]
        out = self.derive(flags)
        self.assertEqual([(m["run_id"], m["position"], m["codes"]) for m in out["members_excluded"]],
                         [("c-r1", 0, ["m.bad"]), ("c-q1-a1", 1, ["s.hot"]), ("c-q1-b1", 2, ["s.hot"]),
                          ("c-q2-a1", 4, ["s.hot"]), ("c-q2-b1", 5, ["s.hot"]),
                          ("c-q3-a1", 7, ["s.hot"]), ("c-q3-b1", 8, ["s.hot"])])
        cell = out["cells"][0]
        self.assertEqual(cell["kept_units"], {"quad": [], "repeat": ["c-r2", "c-r3"]})
        self.assertEqual(cell["n_kept"], {"quad": 0, "repeat": 2})
        self.assertFalse(cell["resolvable"])
        self.assertEqual(out["reasons"], ["cell.below_minimum"])
        self.assertEqual(out["unclassified"], ["unknown.code"])
        self.assertTrue(out["release_blocked"])
        self.assertEqual(out["flag_counts"]["foreign_scope"], 1)
        self.assertEqual(out["flag_counts"]["by_effect"],
                         {"DISCLOSE": 1, "EXCLUDE_MEMBER": 3, "UNCLASSIFIED": 1})

    def test_window_effect_and_gamma_only_midpoint_rule(self):
        self.assertEqual(self.derive([flag("w", "w.dead", level="window")])["reasons"], ["w.dead"])
        lost = [flag("n", "neg8.midpoint_lost", level="window")]
        self.assertEqual(self.derive(lost)["reasons"], [])
        self.assertTrue(self.derive(lost)["claim_usable"])
        gamma = self.derive(lost, pack_id=r.GAMMA_PACK_ID)
        self.assertEqual(gamma["reasons"], ["neg8.midpoint_lost_primary"])
        self.assertFalse(gamma["claim_usable"])

    def test_roster_bundle_rule(self):
        ros, _ = roster()
        bundles = [{"bundle_id": m["run_id"], "run_id": m["run_id"], "attempt": 1, "created_monotonic_ns": 10}
                   for m in ros["members"] if m["run_id"] != "c-r1"]
        bundles.append({"bundle_id": "dup", "run_id": "c-r2", "attempt": 1, "created_monotonic_ns": 10})
        bundles.append({"bundle_id": "stray", "run_id": "not-planned", "attempt": 1, "created_monotonic_ns": 10})
        out = self.derive([], bundles=bundles)
        self.assertEqual({m["run_id"]: m["codes"] for m in out["members_excluded"]},
                         {"c-r1": ["member.bytes_missing"], "c-r2": ["member.bytes_ambiguous"]})
        self.assertEqual(out["duplicate_bundles"], ["c-r2"])
        self.assertEqual(out["bundles_ignored"], [{"bundle_id": "stray", "run_id": "not-planned",
                                                   "code": "roster.not_in_plan"}])


def write_inputs(archive):
    """Harvest-shaped exclusion inputs for a support.full_pack archive, plus the stored
    exclusions the registered catalog gives for them."""
    ros = json.loads((archive / "derived/roster.json").read_text())
    members = [{"run_id": m["run_id"], "stage_id": m["stage_id"], "units": m["units"]} for m in ros["members"]]
    inputs = {"pack_id": ros["pack_id"], "plan_id": "plan", "attempt": 1, "members": members, "cells": ros["cells"]}
    spans = {m["run_id"]: {"monotonic_ns": [i * 10, i * 10 + 5]} for i, m in enumerate(members)}
    dump(archive / "withheld/exclusion-inputs.json", {"schema": "joulewise.b5_exclusion_inputs.v1",
                                                      "roster": inputs, "spans": spans})
    raw = r.CATALOG_PATH.read_bytes()
    stored = r.rederive_exclusions([], inputs, spans, json.loads(raw), hashlib.sha256(raw).hexdigest())
    dump(archive / "derived/exclusions.json", stored)
    return stored


class ArchiveHygieneTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def test_stdout_prints_structure_codes_only_and_the_interpreter(self):
        archive = full_pack(self.root, "ALPHA", 5)
        rc, out, stdout = run_cli({"ALPHA": archive}, self.root / "out.json")
        self.assertEqual(rc, 0)
        codes = {f["code"] for f in out["flags"]}
        # The rail-only fixture raises meter_absent, a science-side code (not STRUCTURE).
        self.assertIn("meter_absent", codes)
        self.assertNotIn("meter_absent", r.STRUCTURE_FLAG_CODES)
        fields = dict(field.split("=", 1) for field in stdout.split())
        self.assertEqual(json.loads(fields["flags"]), {"exclusions_rederivation_unavailable": 1})
        self.assertTrue(set(json.loads(fields["flags"])) <= r.STRUCTURE_FLAG_CODES)
        self.assertNotIn("meter_absent", stdout)
        self.assertEqual(fields["python"], platform.python_version())
        self.assertEqual(out["interpreter"], {"implementation": platform.python_implementation(),
                                              "version": platform.python_version()})
        self.assertEqual(json.loads(fields["exclusions_rederivation"]), {"ALPHA": "not_computed"})

    def test_uncaught_exception_prints_its_type_only(self):
        stderr = io.StringIO()
        with mock.patch.object(r, "main", side_effect=ValueError("value 12.3457 J")), \
                contextlib.redirect_stderr(stderr):
            self.assertEqual(r.guarded_main([]), 2)
        self.assertEqual(stderr.getvalue(), "error: internal ValueError\n")

    def test_stored_exclusions_agree_then_a_planted_drop_stops_the_comparison(self):
        archive = full_pack(self.root, "ALPHA", 5)
        stored = write_inputs(archive)
        _, out, stdout = run_cli({"ALPHA": archive}, self.root / "agree.json")
        check = out["exclusions_rederivation"]["ALPHA"]
        self.assertEqual((check["status"], check["differing_keys"]), ("agrees", []))
        self.assertFalse(out["comparison_stopped"])
        self.assertNotIn("exclusions_rederivation_mismatch", stdout)
        # A consumer error: the stored file loses one excluded member that a flag requires.
        rid = "fixture-decode-r01"
        (archive / "derived/flags.jsonl").write_text(json.dumps(
            flag("f", "member.bytes_missing", run_id=rid, plan_id="plan")) + "\n")
        _, out, stdout = run_cli({"ALPHA": archive}, self.root / "drop.json")
        check = out["exclusions_rederivation"]["ALPHA"]
        self.assertEqual(check["status"], "disagrees")
        self.assertIn("members_excluded", check["differing_keys"])
        self.assertEqual(check["members_only_rederived"], [rid])
        self.assertTrue(out["comparison_stopped"])
        self.assertIn("exclusions_rederivation_mismatch", json.loads(dict(
            f.split("=", 1) for f in stdout.split())["flags"]))
        self.assertEqual(stored["members_excluded"], [])


if __name__ == "__main__":
    unittest.main()
