"""Independent PR #701 probes. Only temporary synthetic records are used.

Expected failures specify guards missing at ed2b2d72b; remove the decorators
when those findings are fixed. No real archive, key, meter or store is opened.
"""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import patch

from joulewise.flags import catalog, core
from joulewise.schemas import IdleAdmissionPolicy
from scripts import bytes_stage1 as s1
from tests.test_bytes_agreement import Recorder


class CensusReviewTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="sol-review-701-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.export = self.root / "export"
        self.tables = []
        for pack in s1.PACKS:
            directory = self.export / pack
            directory.mkdir(parents=True)
            store = self.root / "stores" / pack / (pack + ".runs.csv")
            store.parent.mkdir(parents=True)
            store.write_text("synthetic sealed sentinel\n")
            side = {"pack_id": pack, "counting": True, "non_claim": False,
                    "blinding": {"group": "bytes", "applied": True,
                                 "pass_id": int(pack[-1]),
                                 "withheld": {"path": str(store), "row_count": 1}}}
            (directory / (pack + ".session.json")).write_text(json.dumps(side))
            table = directory / (pack + ".runs.csv")
            self.write_table(table)
            self.tables.append(table)

    @staticmethod
    def write_table(path, extra=None):
        row = {"run_id": "synthetic", "role": "science",
               "model_name": "Qwen3-1.7B-4bit", "config_key": "synthetic-fit",
               "phase_decode_j": "NOT_AN_ENERGY", "idle_power_w": "NOT_A_POWER",
               **(extra or {})}
        with path.open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(row))
            writer.writeheader()
            writer.writerow(row)

    def test_identity_census_does_not_interpret_energy_or_open_external_store(self):
        opened = []
        original = Path.open

        def guarded(path, *args, **kwargs):
            opened.append(path)
            self.assertNotIn("stores", path.parts)
            return original(path, *args, **kwargs)

        with patch.object(Path, "open", guarded):
            record, reasons = s1.census([self.export])
        self.assertEqual(reasons, [])
        self.assertEqual(record["verdict"], "OK")
        self.assertTrue(opened)
        self.assertNotIn("NOT_AN_ENERGY", json.dumps(record))

    def test_heldout_identity_refuses_without_interpreting_energy(self):
        self.write_table(self.tables[0], {"model_name": "Qwen3-32B-4bit"})
        _, reasons = s1.census([self.export])
        self.assertTrue(any("held-out row" in r for r in reasons))

    def test_registered_clock_column_refuses(self):
        self.write_table(self.tables[0], {"run_start_utc": "synthetic-clock"})
        _, reasons = s1.census([self.export])
        self.assertTrue(any("clock column" in r for r in reasons))

    @unittest.expectedFailure
    def test_other_clock_column_also_refuses_under_section_11_item_2(self):
        self.write_table(self.tables[0], {"run_end_utc": "synthetic-clock"})
        _, reasons = s1.census([self.export])
        self.assertTrue(any("clock column" in r for r in reasons), reasons)

    @unittest.expectedFailure
    def test_missing_store_does_not_refuse_under_section_11_item_4(self):
        store = self.root / "stores" / s1.PACKS[0] / (s1.PACKS[0] + ".runs.csv")
        store.unlink()
        record, reasons = s1.census([self.export])
        self.assertEqual(reasons, [])
        self.assertEqual(record["verdict"], "OK")

    @unittest.expectedFailure
    def test_nested_withheld_directory_is_never_opened_as_visible_export(self):
        # A misplaced visible table must not make the scanner treat the
        # registered withheld/<pack>/<session>.runs.csv layout as public.
        table = self.tables[0]
        nested = self.export / "withheld" / s1.PACKS[0] / table.name
        nested.parent.mkdir(parents=True)
        table.rename(nested)
        opened = []
        original = Path.open

        def guarded(path, *args, **kwargs):
            if "withheld" in path.parts:
                opened.append(path)
                raise s1.Stage1Error("synthetic store-open trap")
            return original(path, *args, **kwargs)

        with patch.object(Path, "open", guarded):
            try:
                s1.census([self.export])
            except s1.Stage1Error:
                pass
        self.assertEqual(opened, [])


class RunReviewTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="sol-review-701-run-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.manifest = self.root / "manifest.json"
        document = json.loads((s1.ROOT / "configs/bytes/bytes_manifest.json").read_text())
        document["sessions"] = [{"session_id": p, "pack_id": p, "pass_id": int(p[-1]),
                                 "archive": str(self.root / p)} for p in s1.PACKS]
        self.manifest.write_text(json.dumps(document))

    def simulate(self, exits=None, *, disagreement=False, actual_comparer=False):
        exits = exits or {}
        events = []
        released = []

        def child(command, **_kwargs):
            output = Path(command[command.index("--out") + 1])
            tag = output.name.removesuffix(".json")
            events.append(tag)
            default = 1 if tag.endswith("nokeys") else 0
            return subprocess.CompletedProcess(command, exits.get(tag, default), "", "synthetic")

        def release(_root, keys, _out):
            events.append("release")
            released.extend(keys)
            # Stop here; these probes never copy even synthetic factors.
            raise s1.Stage1Error("synthetic release trap")

        recorder = Recorder()
        if disagreement:
            recorder.exact("blinded", "science", "synthetic", "left", "right")
        with patch.object(s1.subprocess, "run", side_effect=child), \
                patch.object(s1, "_git_state", return_value=("synthetic", False)):
            if actual_comparer:
                try:
                    result = s1.run_stage1(self.manifest, [self.root], self.root, self.root / "run",
                                           release_fn=release)
                except s1.Stage1Error:
                    result = None
            else:
                with patch("tests.test_bytes_agreement.compare_campaign", return_value=recorder):
                    try:
                        result = s1.run_stage1(self.manifest, [self.root], self.root, self.root / "run",
                                               release_fn=release)
                    except s1.Stage1Error:
                        result = None
        return result, events, released

    def test_blinded_disagreement_stops_before_release(self):
        result, events, released = self.simulate(disagreement=True)
        self.assertEqual(result[0], 3)
        self.assertEqual(events, ["a-blinded", "t-blinded"])
        self.assertEqual(released, [])

    def test_blinded_refusal_stops_before_release(self):
        result, _, released = self.simulate({"t-blinded": 2})
        self.assertEqual(result[0], 2)
        self.assertEqual(released, [])

    def test_unkeyed_success_stops_before_release(self):
        result, _, released = self.simulate({"a-fit-nokeys": 0})
        self.assertEqual(result[0], 4)
        self.assertEqual(released, [])

    def test_normal_prefix_orders_release_and_selects_only_fit_keys(self):
        _, events, released = self.simulate()
        self.assertEqual(events, ["a-blinded", "t-blinded", "a-fit-nokeys", "t-1-nokeys", "release"])
        manifest = json.loads(self.manifest.read_text())
        self.assertEqual(set(released), {"neg8_reference"} | {
            m["config_key"] for m in manifest["models"] if m["role"] == "fit"})
        self.assertFalse(set(released) & {m["config_key"] for m in manifest["models"]
                                         if m["role"] != "fit"})

    @unittest.expectedFailure
    def test_no_key_refusal_exit_mismatch_stops_before_release(self):
        _, _, released = self.simulate({"a-fit-nokeys": 1, "t-1-nokeys": 2})
        self.assertEqual(released, [])

    @unittest.expectedFailure
    def test_missing_blinded_products_cannot_count_as_agreement(self):
        # Use the actual registered comparer. Equal exit files alone currently
        # skip every cell/NEG-8 comparison and still allow release.
        _, _, released = self.simulate(actual_comparer=True)
        self.assertEqual(released, [])


class LineageReviewTests(unittest.TestCase):
    @unittest.expectedFailure
    def test_b5_neg8_member_comparison_keeps_registered_one_e_minus_nine_bar(self):
        from joulewise.b5 import harvest
        # registration_block5.md, member check (vii), requires both relative
        # and absolute 1e-9. This ordinary sub-mJ mismatch must remain a
        # mismatch on B5; the shared helper currently applies B6's 1 mJ bar.
        self.assertFalse(harvest._close(1.0, 1.0005))

    def test_sealed_b5_exclusions_equal_main_for_synthetic_member_losses(self):
        from joulewise.flags import exclusions
        from tests.flags.test_flags_exclusions import floor_roster, member_flag, spans_for
        source = subprocess.check_output([
            "git", "show", "722f3a293:joulewise/flags/exclusions.py"], cwd=s1.ROOT)
        previous = ModuleType("sol701_old_exclusions")
        with patch.dict(sys.modules, {previous.__name__: previous}):
            exec(compile(source, "<main-parent-exclusions>", "exec"), previous.__dict__)
        sealed = catalog.load_catalog(s1.ROOT / catalog.SEALED_CATALOG_RELATIVE_PATH)
        roster = floor_roster()
        spans = spans_for(roster)
        for lost in range(11):
            flags = [member_flag("member.admission_aborted", f"a-q{q:02d}-A1")
                     for q in range(1, lost + 1)]
            with self.subTest(lost_quads=lost):
                self.assertEqual(exclusions.compute(flags, roster, spans, sealed),
                                 previous.compute(flags, roster, spans, sealed))

    def test_registered_agent_presence_interval_drops_overlapped_quad(self):
        from joulewise.flags import exclusions
        from tests.flags.test_flags_exclusions import floor_roster, spans_for, window_flag, cell
        roster = floor_roster()
        spans = spans_for(roster)
        flag = window_flag("agent.presence", family="PHYSICS_IN_SPAN", klass="PHYSICS",
                           interval=spans["a-q04-B2"]["monotonic_ns"])
        b6_catalog = catalog.load_catalog(s1.ROOT / "configs/b6/flag_catalog_b6.json")
        result = exclusions.compute([flag], roster, spans, b6_catalog)
        self.assertEqual([r["run_id"] for r in result["members_excluded"]], ["a-q04-B2"])
        self.assertEqual(cell(result)["n_quads"], 9)
        self.assertEqual(cell(result)["dropped_units"][0]["unit_id"], "q04")

    def test_eight_candidate_codes_are_registered_for_all_twelve_bytes_packs(self):
        codes = {"calibration.acceptance_preflight_unverified", "agent.capture_overlap",
                 "agent.presence", "agent.presence_overlap", "sleep.assertion_lost",
                 "sleep.assertion_unverified", "sleep.in_chain", "sleep.reading_unmeasured"}
        entries = json.loads((s1.ROOT / "configs/b6/flag_catalog_b6.json").read_text())["codes"]
        digest = hashlib.sha256((s1.ROOT / "configs/b6/flag_catalog_b6.json").read_bytes()).hexdigest()
        for pack in s1.PACKS:
            registration = json.loads((s1.ROOT / "configs/b6/packs" / pack / "registration.json").read_text())
            self.assertIn(digest, json.dumps(registration))
            for code in codes:
                expected = "EXCLUDE_MEMBER" if code in {"agent.presence", "agent.presence_overlap"} else "DISCLOSE"
                self.assertEqual(entries[code]["effect"], expected)
                self.assertEqual(registration["flag_effects"][code], expected)
        self.assertIn("calibration.acceptance_preflight_unverified", core.CORE_FLAG_CODES)
        self.assertEqual(catalog.load_catalog(s1.ROOT / catalog.SEALED_CATALOG_RELATIVE_PATH)
                         .entry("cell.below_minimum")["effect"], catalog.EXCLUDE_WINDOW)

    def test_legacy_idle_policy_now_extends_hazard_timeout(self):
        # Behavioral counterexample to blanket "inert for block 5": no B6
        # pack selector is consulted, and old sidecars omit both wait fields.
        import importlib.util
        spec = importlib.util.spec_from_file_location("sol701_campaign", s1.ROOT / "scripts/run_campaign.py")
        module = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {spec.name: module}):
            spec.loader.exec_module(module)
        temp = tempfile.TemporaryDirectory(prefix="sol701-timeout-")
        self.addCleanup(temp.cleanup)
        extra = module._hazard_effective_wait_cap(SimpleNamespace(custody_root=Path(temp.name)),
                                                  SimpleNamespace(idle_admission=IdleAdmissionPolicy()))
        self.assertEqual(module.HAZARD_MEMBER_CAP_S, 1800)
        self.assertEqual(extra, 1500)


if __name__ == "__main__":
    unittest.main()
