import copy
import json
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from joulewise.b6 import survivor_screen
from joulewise.flags.catalog import load_catalog
from joulewise.flags.exclusions import GAMMA_PACK_ID, compute
from joulewise.flags.schema import make_flag, make_scope, make_source
from joulewise.whole_window import neg8_count_adjusted_bound
from tests.b6.support import ROOT, document


def roster(n=18):
    members = [{"run_id": f"c{i}", "stage_id": "neg8_bound", "status": "succeeded"} for i in range(n)]
    for slot, count in (("start", 3), ("midpoint", 1), ("end", 3)):
        members.extend({"run_id": f"{slot}{i}", "stage_id": f"{slot}_reference", "status": "succeeded"}
                       for i in range(count))
    return {"members": members}


def energies(member):
    run_id = member["run_id"]
    value = 10 + int(run_id[1:]) * .1 if run_id.startswith("c") else 10.5
    return {"gross": value, "idle_subtracted": value - 1, "source": "synthetic"}


class SurvivorTests(unittest.TestCase):
    def screen(self, *, n=18, exclusions=None, energy=energies):
        return survivor_screen.screen(roster(n), exclusions or {}, energy, document())

    def test_one_end_lost_screens_on_3_1_2(self):
        result = self.screen(exclusions={"end2": ["contention.request_overlap"]})
        self.assertEqual(result.verdict, "passed")
        self.assertEqual(result.counts, {"start": 3, "midpoint": 1, "end": 2})
        self.assertIn("neg8.reference_lost", result.flags)
        points = [energies({"run_id": f"c{i}"})["gross"] for i in range(12)]
        self.assertEqual(result.withheld["families"]["gross"]["bound_terms"], neg8_count_adjusted_bound(points, 3, 2))

    def test_two_end_lost_is_undefined(self):
        result = self.screen(exclusions={"end2": ["physics"], "end1": ["physics"]})
        self.assertEqual((result.verdict, result.reason), ("undefined", "references_insufficient"))

    def test_corpus_five_undefined_six_defined_and_first_twelve(self):
        self.assertEqual(self.screen(n=5).reason, "bound_absent")
        six = self.screen(n=6)
        self.assertEqual(six.verdict, "passed")
        self.assertEqual(six.withheld["families"]["gross"]["bound_terms"],
                         neg8_count_adjusted_bound([energies({"run_id": f"c{i}"})["gross"] for i in range(6)], 3, 3))
        result = self.screen()
        self.assertEqual(result.withheld["corpus_run_ids"], [f"c{i}" for i in range(12)])
        self.assertEqual(result.corpus_clean_n, 12)

    def test_physics_flagged_corpus_skipped_in_plan_order(self):
        result = self.screen(exclusions={"c0": ["battery.member_span"]})
        self.assertEqual(result.withheld["corpus_run_ids"], [f"c{i}" for i in range(1, 13)])

    def test_failed_status_dropped(self):
        rows = roster(6)
        rows["members"][0]["status"] = "failed"
        self.assertEqual(survivor_screen.screen(rows, {}, energies, document()).reason, "bound_absent")

    def test_midpoint_lost_discloses_and_gamma_pack_scope_disabled(self):
        result = self.screen(exclusions={"midpoint0": ["sleep.in_run"]})
        self.assertEqual(result.verdict, "passed")
        self.assertIn("neg8.midpoint_lost", result.flags)
        catalog = load_catalog(ROOT / "configs/b6/flag_catalog_b6.json")
        flag = make_flag(code="neg8.midpoint_lost", family="NEG8", klass="NUMBER", scope=make_scope("window"),
                         source=make_source("harvest", "test"))
        rows = {"pack_id": GAMMA_PACK_ID, "members": [], "cells": []}
        self.assertIn("neg8.midpoint_lost_primary", compute([flag], rows, {}, catalog)["reasons"])
        self.assertEqual(compute([flag], rows, {}, catalog, pack_scoped=False)["reasons"], [])

    def test_failed_screen_and_nonfinite_energy(self):
        def shifted(member):
            value = energies(member)
            if member["run_id"].startswith("end"):
                value["idle_subtracted"] += 20
            return value
        self.assertEqual(self.screen(energy=shifted).verdict, "failed")
        self.assertEqual(self.screen(energy=lambda m: {"gross": float("nan"), "idle_subtracted": 1}).verdict, "undefined")

    def test_withheld_write_and_acceptance_projection(self):
        result = self.screen()
        with tempfile.TemporaryDirectory() as tmp:
            path = survivor_screen.write(Path(tmp), result)
            self.assertEqual(json.loads(path.read_text()), result.withheld)
            with self.assertRaises(FileExistsError):
                survivor_screen.write(Path(tmp), result)
        projection = result.acceptance_evidence()
        self.assertEqual(set(projection), {"verdict", "survivors", "corpus_clean_n", "reason", "flags"})

    def test_archive_reader_calls_owning_helper_and_prefers_rereduction(self):
        from joulewise import whole_window

        # The helper is supplied by L9 at merge. This tests only this lane's
        # adapter against that branch's documented pair return shape.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "withheld/reductions/r.summary_metrics.rereduced.json"
            path.parent.mkdir(parents=True)
            path.write_text('{"synthetic_marker":"rereduced"}')
            bundle = root / "sources/claim-runs/r/summary_metrics.json"
            bundle.parent.mkdir(parents=True)
            bundle.write_text('{"synthetic_marker":"stored"}')
            with patch.object(whole_window, "_neg8_writer_reference_energy", create=True,
                              return_value=({"point_j": 10, "lower_j": 9, "upper_j": 11}, 8)) as helper:
                reader = survivor_screen.archive_energy_of(root)
                value = reader({"run_id": "r"})
                helper.assert_called_once_with({"synthetic_marker": "rereduced"})
                self.assertEqual(value["gross"], 10)
                self.assertEqual(value["idle_subtracted"], 8)
                self.assertEqual(value["source"], str(path))
                path.unlink()
                reader({"run_id": "r"})
                helper.assert_called_with({"synthetic_marker": "stored"})
                helper.return_value = (None, None)
                self.assertRaises(ValueError, reader, {"run_id": "r"})

    def test_main_reference_reader_uses_primary_bundle_even_with_rereduction(self):
        # Old-shaped summaries take the main reader's compatibility leg;
        # there is no substitute energy arithmetic in the block-six reader.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            summary = {"gross_energy_j": 10, "idle_subtracted_energy_j": 8,
                       "energy_anchor_shift_envelopes": {"/gross_energy_j":
                           {"point_j": 10, "lower_j": 9, "upper_j": 11}}}
            reduced = root / "withheld/reductions/r.summary_metrics.rereduced.json"
            bundle = root / "sources/claim-runs/r/summary_metrics.json"
            for path in (reduced, bundle):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(json.dumps(summary))
            value = survivor_screen.archive_energy_of(root)({"run_id": "r"})
            self.assertEqual(value["reader"], "whole_window._reference_energy_evidence")
            self.assertEqual((value["gross"], value["idle_subtracted"]), (10, 8))
            self.assertEqual(value["source"], str(bundle))
            reader = survivor_screen.archive_energy_of(root)
            short = survivor_screen.screen(roster(5), {}, reader, document())
            self.assertEqual(short.withheld["energy_reader"], "whole_window._reference_energy_evidence")
            self.assertFalse(short.withheld["energy_reader_used"])
            reduced.unlink()
            self.assertEqual(survivor_screen.archive_energy_of(root)({"run_id": "r"})["source"], str(bundle))
