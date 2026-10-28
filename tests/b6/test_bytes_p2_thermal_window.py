"""§21 request-end OS window on production journals and the real BYTES harvester.

All inputs are synthetic. No collector, reducer, catalog or exclusion is mocked.
The end-to-end baseline is loaded from the brief's base commit when available.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

from joulewise.b5 import harvest as h
from scripts import harvest_b6_session as entry
from tests import test_harvest_b5_window as windows

NS = 10**9
FIELD = "thermal_os_level_nonzero_member_hull"
BASE = "de35f6403"


def setUpModule():
    # The shared b5 fixture's own teardown removes its directory. Support a
    # command that runs that module before this one in the same interpreter.
    if windows._TEMPLATE is not None and not windows._TEMPLATE.is_dir():
        windows._TEMPLATE = None


def tearDownModule():
    windows.tearDownModule()
    windows._TEMPLATE = None


def thermal_journal(times, nonzero=(), *, failed=()):
    journal = windows.L1Journal("thermal")
    for stamp in times:
        ns = round(stamp * NS)
        journal.write("reading", ns - 1000, ns,
                      values={"source": "notifyutil", "level": 1 if stamp in nonzero else 0},
                      error={"type": "read_failed"} if stamp in failed else None)
    return journal


def fixed_seams(module=h):
    return module.Seams(group_alive=lambda _pgid: False, now=lambda: 1786200000.0,
                        monotonic_ns=lambda: 123456, boot_session_uuid=lambda: "SYNTHETIC",
                        harvest_checkout=lambda **_kw: {"schema": h.HARVEST_CHECKOUT_SCHEMA,
                            "root": "synthetic-desk", "head": "0" * 40, "status_clean": True,
                            "status_lines": [], "files": {}, "errors": []})


class ThermalWindowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def joined(self, journal, *, pass_two=True, kind="science", request=(40, 80), hull=(20, 100)):
        monitor = self.root / "monitor"
        monitor.mkdir(exist_ok=True)
        journal.dump(monitor / "thermal.jsonl")
        inputs = types.SimpleNamespace(plan={}, catalog_path=None, plan_id="thermal-test", attempt=1,
            h_claim=None, monitor_dir=monitor, thresholds=windows.REGISTERED_HARVEST_THRESHOLDS)
        writer = h._Harvest(inputs, self.root / "archive", fixed_seams(), prepare_desk=False, run_g3=False)
        writer.bytes_pass_two = pass_two
        writer.roster = {"members": [{"run_id": "m", "stage_id": "science", "kind": kind}]}
        writer.spans = {"m": {"member": [round(t * NS) for t in hull] if hull else None,
                              "request": [round(t * NS) for t in request] if request else None}}
        writer.members = {"m": {}}
        if pass_two:
            writer.record_thermal_hull()
        writer.monitor_joins()
        self.assertEqual(writer.faults, [])
        flags = [f for f in writer.flags.records if f["code"].startswith("thermal.")]
        return flags, writer.members["m"]

    def test_tail_only_is_kept_in_pass2_and_excluded_in_pass1(self):
        for times in (list(range(0, 126, 5)), [t if t < 50 else t + 0.3 for t in range(0, 126, 5)]):
            late = next(t for t in times if t >= 90)
            journal = thermal_journal(times, {late})
            p2, member = self.joined(journal)
            p1, old_member = self.joined(journal, pass_two=False)
            self.assertEqual(p2, [])
            self.assertEqual([f["code"] for f in p1], ["thermal.os_level_nonzero"])
            self.assertEqual(member[FIELD]["excluded"], True)
            self.assertEqual(member[FIELD]["samples"], [{"monotonic_ns": round(late * NS), "level": 1}])
            self.assertNotIn(FIELD, old_member)

    def test_inside_and_boundary_reads_exclude_in_both_passes(self):
        # The request starts at 40; a read at 30 must still count from hull start.
        for nonzero, request in ((30, (40, 80)), (60, (40, 80)), (80, (40, 80)), (85, (40, 82))):
            for pass_two in (False, True):
                with self.subTest(nonzero=nonzero, request=request, pass_two=pass_two):
                    flags, _ = self.joined(thermal_journal(range(0, 126, 5), {nonzero}),
                                           pass_two=pass_two, request=request)
                    self.assertEqual([f["code"] for f in flags], ["thermal.os_level_nonzero"])
                    self.assertEqual(flags[0]["observed"]["samples"],
                                     [{"monotonic_ns": nonzero * NS, "level": 1}])
        # The last successful read before hull start and the first successful
        # read after request end count even when those polls are not on the edge.
        for nonzero in (17, 82):
            flags, _ = self.joined(thermal_journal(range(2, 128, 5), {nonzero}))
            self.assertEqual([f["code"] for f in flags], ["thermal.os_level_nonzero"])

    def test_failed_boundary_read_uses_the_next_successful_numeric_read(self):
        for numeric in (True, False):
            journal = thermal_journal(range(0, 126, 5), {85}, failed={80} if numeric else ())
            if not numeric:
                journal.lines[16]["values"]["level"] = None  # successful probe, absent numeric level
            flags, _ = self.joined(journal)
            self.assertEqual([f["code"] for f in flags], ["thermal.os_level_nonzero"])
            self.assertEqual(flags[0]["observed"]["samples"][0]["monotonic_ns"], 85 * NS)

    def test_absent_request_and_reference_keep_full_hull(self):
        journal = thermal_journal(range(0, 126, 5), {90})
        for options in ({"request": None}, {"kind": "external_input"}):
            flags, member = self.joined(journal, **options)
            self.assertEqual([f["code"] for f in flags], ["thermal.os_level_nonzero"])
            self.assertEqual(FIELD in member, options.get("kind") != "external_input")

    def test_hull_coverage_holes_are_identical_even_after_request(self):
        journal = thermal_journal([*range(0, 86, 5), 110, 115, 120])
        p1, _ = self.joined(journal, pass_two=False)
        p2, member = self.joined(journal)
        self.assertEqual(p2, p1)
        self.assertEqual([f["code"] for f in p2], ["thermal.unmeasured"])
        self.assertFalse(member[FIELD]["excluded"])

    def test_evidence_retains_all_samples_and_explicit_missing_observations(self):
        flags, member = self.joined(thermal_journal(range(0, 126, 5), set(range(20, 106, 5))))
        self.assertEqual(len(flags[0]["observed"]["samples"]), 8)
        self.assertEqual(len(member[FIELD]["samples"]), 17)
        flags, member = self.joined(thermal_journal(range(0, 126, 5)), hull=None)
        self.assertEqual(flags, [])
        self.assertIsNone(member[FIELD]["excluded"])

    def test_clean_hull_records_false_and_missing_journal_keeps_unmeasured(self):
        flags, member = self.joined(thermal_journal(range(0, 126, 5)))
        self.assertEqual(flags, [])
        self.assertEqual(member[FIELD]["excluded"], False)
        self.assertEqual(member[FIELD]["samples"], [])
        (self.root / "monitor/thermal.jsonl").unlink()
        inputs = types.SimpleNamespace(plan={}, catalog_path=None, plan_id="missing", attempt=1,
            h_claim=None, monitor_dir=self.root / "monitor", thresholds=windows.REGISTERED_HARVEST_THRESHOLDS)
        writer = h._Harvest(inputs, self.root / "archive", fixed_seams(), prepare_desk=False, run_g3=False)
        writer.bytes_pass_two = True
        writer.roster = {"members": [{"run_id": "m", "kind": "science"}]}
        writer.members = {"m": {}}
        writer.spans = {"m": {"member": [20 * NS, 100 * NS], "request": [40 * NS, 80 * NS]}}
        writer.record_thermal_hull()
        writer.monitor_joins()
        self.assertFalse(writer.members["m"][FIELD]["journal_available"])
        self.assertEqual([f["code"] for f in writer.flags.records if f["code"].startswith("thermal.")],
                         ["thermal.unmeasured"])

    def test_committed_plan_trees_select_all_six_pass2_packs_only(self):
        packs = [f"bytes-s{n}-p{pass_id}" for n in range(1, 7) for pass_id in (1, 2)]
        packs += ["d117_floor_qwen3-1p7b_v5", "d117_floor_qwen3-8b_v5",
                  "d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5"]
        for pack in packs:
            with self.subTest(pack=pack):
                inputs = types.SimpleNamespace(plan={"hazard_window": {"bindings": {"capture_screen": {}}}},
                    catalog_path=None, plan_id="plan-selection", attempt=1, h_claim=None,
                    measurement_root=windows.ROOT, pack_root=windows.ROOT / "configs/campaigns" / pack)
                writer = h._Harvest(inputs, self.root / "archive", fixed_seams(), prepare_desk=False, run_g3=False)
                writer.build_roster()
                self.assertEqual(writer.bytes_pass_two, pack.startswith("bytes-") and pack.endswith("-p2"))

    def test_request_end_os_exclusions_are_a_subset_of_hull_exclusions(self):
        trials = 0
        for phase in range(5):
            for gap in (0, 0.3):
                times = [t + phase + (gap if t >= 50 else 0) for t in range(0, 126, 5)]
                for onset in range(0, 126, 5):
                    for length in (5, 20, 50):
                        readings = windows.parsed(thermal_journal(times, {t for t in times if onset <= t < onset + length}))
                        hull = h.thermal_member_flags([20 * NS, 100 * NS], readings, windows.REGISTERED_HARVEST_THRESHOLDS)
                        request_end = h.thermal_member_flags([20 * NS, 82 * NS], readings, windows.REGISTERED_HARVEST_THRESHOLDS)
                        has_os = lambda flags: any(code == "thermal.os_level_nonzero" for code, *_ in flags)
                        self.assertFalse(has_os(request_end) and not has_os(hull))
                        trials += 1
        self.assertEqual(trials, 780)


def load_base():
    result = subprocess.run(["git", "show", f"{BASE}:joulewise/b5/harvest.py"], cwd=windows.ROOT,
                            capture_output=True, check=False)
    if result.returncode:
        raise unittest.SkipTest(f"{BASE} not available for byte-identity replay")
    name = "joulewise.b5._bytes_thermal_base"
    module = types.ModuleType(name)
    module.__file__ = str(windows.ROOT / "joulewise/b5/harvest.py")
    sys.modules[name] = module
    exec(compile(result.stdout, module.__file__, "exec"), module.__dict__)
    return module


class HarvestEntryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def window(self, pass_id=2, *, block_six=True, group="bytes", name="window"):
        window = windows.Window(self.root / name)
        plan = json.loads(window.plan_path.read_bytes())
        if block_six:
            plan["hazard_window"]["bindings"]["capture_screen"] = {}
        windows.put(window.plan_path, plan)
        tree_path = window.pack / "plan_tree.json"
        tree = json.loads(tree_path.read_bytes())
        tree.update(bytes_pass=pass_id, blinding_group=group)
        windows.put(tree_path, tree)
        # Keep the seed's clock-anchor evidence intact. The production hull
        # also covers the post-request sentinel's controller event stamps.
        for run_id, *_ in windows.MEMBERS:
            path = window.claim / run_id / "events.jsonl"
            _start, end = windows.member_span_ns(run_id)
            events = [json.loads(line) for line in path.read_text().splitlines()]
            finalized = events.pop()
            for event_type, stamp in (("stage_started", end), ("stage_completed", end + 30 * NS)):
                events.append({"timestamp_s": (stamp + windows.WALL_OFFSET_NS) / NS,
                    "event_type": event_type, "phase": "idle_drift_sentinel",
                    "message": "synthetic post-request sentinel",
                    "metadata": {"run_id": run_id, "monotonic_ns": stamp}})
            finalized["timestamp_s"] = events[-1]["timestamp_s"] + 1
            events.append(finalized)
            path.write_text("".join(json.dumps(event) + "\n" for event in events))
        # Polls are 5 s apart, with one 5.3 s gap; tails contain a level-1 read.
        journal = windows.L1Journal("thermal")
        for run_id, *_ in windows.MEMBERS:
            start, _end = windows.member_span_ns(run_id)
            start_s = start // NS
            times = [start_s - 20 + 5 * i + (0.3 if i >= 9 else 0) for i in range(17)]
            late = next(t for t in times if t > start_s + 15)
            part = thermal_journal(times, {late})
            for line in part.lines:
                journal.write("reading", line["started"]["monotonic_ns"], line["finished"]["monotonic_ns"],
                              values=line["values"])
        journal.dump(window.custody / "hazards/monitor/thermal.jsonl")
        return window

    def harvest(self, window, module=h):
        # DeskLane.session_desk invokes scripts/harvest_b6_session.py; that
        # wrapper imports this exact callable. Real strict validation, reducer,
        # roster, monitor joins, exclusions and archive writers run here.
        self.assertIs(entry.harvest, h.harvest)
        with patch.object(module.time, "monotonic", return_value=100.0):
            record = (entry.harvest if module is h else module.harvest)(
                module.resolve_inputs(window.plan_path), window.archive,
                seams=fixed_seams(module), prepare_desk=False, run_g3=False)
        self.assertEqual(record["verdict"], h.COLLECTED, record)
        return record

    def test_pass2_primary_and_full_hull_member_record(self):
        window = self.window()
        self.harvest(window)
        self.assertNotIn("thermal.os_level_nonzero", window.codes())
        records = json.loads((window.archive / "withheld/member-assessments.json").read_bytes())["members"]
        for run_id, *_ in windows.MEMBERS:
            member = records[run_id]
            self.assertTrue(member["strict_valid"], member.get("strict_problems"))
            self.assertTrue(member[FIELD]["excluded"])
            self.assertEqual(member[FIELD]["span_monotonic_ns"], member["spans"]["member"])
            self.assertTrue(member[FIELD]["samples"])
        self.assertTrue(all("thermal.os_level_nonzero" not in row["codes"]
                            for row in window.exclusions()["members_excluded"]))

    def test_pass1_and_other_lanes_are_byte_identical_to_base(self):
        base = load_base()
        self.addCleanup(sys.modules.pop, base.__name__, None)
        # Explicit wrong-lane and wrong-group cases guard against a global
        # bytes_pass switch. No evidence field or new flag appears in them.
        for name, pass_id, block_six, group in (("pass1", 1, True, "bytes"),
                ("block5", 2, False, "bytes"), ("alpha", 2, True, "alpha")):
            with self.subTest(lane=name):
                window = self.window(pass_id, block_six=block_six, group=group, name=name)
                self.harvest(window, base)
                before = {p.relative_to(window.archive).as_posix(): p.read_bytes()
                          for p in window.archive.rglob("*") if p.is_file()}
                shutil.rmtree(window.archive)
                self.harvest(window)
                after = {p.relative_to(window.archive).as_posix(): p.read_bytes()
                         for p in window.archive.rglob("*") if p.is_file()}
                self.assertEqual(before.keys(), after.keys())
                for path in before:
                    self.assertEqual(before[path], after[path], path)
                self.assertIn("thermal.os_level_nonzero", window.codes())
                assessments = json.loads(after["withheld/member-assessments.json"])["members"]
                self.assertTrue(all(FIELD not in member for member in assessments.values()))
                digest = hashlib.sha256(b"".join(p.encode() + b"\0" + hashlib.sha256(after[p]).digest()
                                               for p in sorted(after))).hexdigest()
                print(f"BYTE_IDENTITY {name}: {len(after)} files, exact equality; manifest_sha256={digest}")
