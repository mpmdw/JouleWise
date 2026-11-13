"""B-4, mapping.json from names, on synthetic names lists in the R12 archive layout. No custody is read."""
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import b6_mapping_build as mb  # noqa: E402

KIT = Path(os.environ.get("JW_B6_CUSTODY_KIT", "/Volumes/JW-EXT/jw-wt/b6-custody-kit/scripts/b6_custody_kit.py"))
# §17-R7's t0 order with RUN_STATE 302's open part filled in one consistent way.
ORDER = ("r1-alpha", "r1-beta", "r1-gamma", "r2-beta", "r2-gamma", "r3-gamma", "r3-alpha", "r3-beta", "r4-alpha")


def archive_names(*, clock=True, flags=mb.FLAGS, drop=(), streams=("stream-001.jsonl",), extra_clock=False):
    names = {"harvest.json", "sources/SHA256SUMS", "derived/b6-acceptance.json", "withheld/spans.json",
             "derived/bracket-binding.json", "derived/roster.json", mb.CONTENTION,
             "sources/claim-runs/fixture-decode-r01/metadata.json"}
    names |= {mb.METER_DIR + s for s in streams}
    names.add(mb.METER_DIR + "raw/not-a-stream.jsonl")
    for family, wanted in mb.VERIFY_MAP.items():
        names |= {n for n in wanted if n != mb.FLAGS}
    if flags:
        names.add(flags)
    if clock:
        names.add(mb.MONITOR + "clock.jsonl")
    if extra_clock:
        names.add("sources/night-custody/other/monitor/clock.jsonl")
    return sorted(n for n in names if n not in drop)


def attempts_rows(order=ORDER, not_counting=("r2-alpha",)):
    rows = []
    for i, sid in enumerate(order):
        rnd, pack = sid.split("-")
        rows.append({"session_id": sid, "round": int(rnd[1:]), "packs": [pack], "t0": 1.79e9 + 1000 * i,
                     "outcomes": {pack: {"status": "counting", "cause": None}}, "line": {"ignored": True}})
    for sid in not_counting:
        rnd, pack = sid.split("-")
        rows.append({"session_id": sid, "round": int(rnd[1:]), "packs": [pack], "t0": 1.79e9 + 3500,
                     "outcomes": {pack: {"status": "not_counting", "cause": "x"}}})
    return rows


class MappingBuild(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="b6-mapping-", dir=os.environ.get("TMPDIR")))
        self.names = self.tmp / "names"
        self.names.mkdir()
        self.attempts = self.tmp / "attempts.jsonl"

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def write(self, per_session=None, rows=None):
        for sid in ORDER:
            names = (per_session or {}).get(sid) or archive_names()
            (self.names / (sid + ".txt")).write_text("".join(n + "\n" for n in names))
        self.attempts.write_text("".join(json.dumps(r) + "\n" for r in (rows or attempts_rows())))

    def run_build(self, *extra):
        out, report = self.tmp / "mapping.json", self.tmp / "report.json"
        with contextlib.redirect_stdout(io.StringIO()) as buffer:
            rc = mb.main(["--names-dir", str(self.names), "--loop-attempts", str(self.attempts), "--verify-map",
                          str(ROOT / "scripts/b6_r12_verify.py"), "--out", str(out), "--report", str(report), *extra])
        load = lambda p: json.loads(p.read_text()) if p.exists() else None
        return rc, buffer.getvalue().splitlines(), load(out), load(report)

    def test_nine_sessions_every_family_equal_to_the_verify_map(self):
        self.write()
        rc, lines, mapping, report = self.run_build()
        self.assertEqual(rc, 0, lines)
        self.assertEqual(lines[:3], ["mapping sessions=9", "clock_journal: 9 of 9", "copied_records_equal: true"])
        self.assertEqual(set(mapping["sessions"]), {s + "/archive" for s in ORDER})
        pin = mapping["sessions"]["r1-alpha/archive"]
        self.assertEqual(pin["meter_streams"], [mb.METER_DIR + "stream-001.jsonl"])
        self.assertEqual(pin["contention_journal"], mb.CONTENTION)
        self.assertEqual(pin["clock_journal"], mb.MONITOR + "clock.jsonl")
        self.assertEqual(pin["copied_records"], mb.VERIFY_MAP)
        self.assertNotIn("relocations", pin)
        self.assertTrue(report["r7"]["stated_order_holds"])
        self.assertTrue(report["r7"]["pairing_equals_r7"])
        self.assertEqual(report["r7"]["open_statements"]["1_order_of_the_three"], "r2-beta then r2-gamma then r3-gamma")
        self.assertEqual(report["r7"]["open_statements"]["2_relative_to_r1_gamma"], "all three after r1-gamma")
        self.assertEqual([r["t0_rank"] for r in report["session_index"] if r["session_id"] == "r2-alpha"], [5])
        self.assertTrue(report["names_vs_counting_attempts"]["equal"])
        self.assertNotIn("t0", json.dumps(report["session_index"]).replace("t0_rank", ""))
        self.assertEqual((self.tmp / "mapping.json").stat().st_mode & 0o777, 0o600)

    def test_missing_thermal_journal_refuses_naming_the_family(self):
        self.write({"r3-beta": archive_names(drop=(mb.MONITOR + "thermal.jsonl",))})
        rc, lines, mapping, report = self.run_build()
        self.assertEqual((rc, lines), (4, ["refused: family_empty session=r3-beta family=subject_temperature"]))
        self.assertIsNone(mapping)
        self.assertIsNone(report)

    def test_other_refusals(self):
        cases = {"meter_streams_empty": dict(streams=()),
                 "contention_journal_missing": dict(drop=(mb.CONTENTION,)),
                 "clock_journal_ambiguous": dict(extra_clock=True)}
        for code, kw in cases.items():
            with self.subTest(code=code):
                for p in self.names.glob("*"):
                    p.unlink()
                self.write({"r1-gamma": archive_names(**kw)})
                rc, lines, _, _ = self.run_build()
                self.assertEqual((rc, lines), (4, ["refused: " + code + " session=r1-gamma"]))

    def test_b6_flags_stands_in_and_is_reported(self):
        self.write({s: archive_names(flags=mb.B6_FLAGS) for s in ORDER})
        rc, lines, mapping, report = self.run_build()
        self.assertEqual(rc, 0)
        self.assertEqual(lines[2], "copied_records_equal: false reference_history,block5_codes_carried")
        self.assertEqual(mapping["sessions"]["r1-alpha/archive"]["copied_records"]["block5_codes_carried"], [mb.B6_FLAGS])
        self.assertIn("block5_codes_carried", report["flags_file_substitutions"]["r1-alpha"])
        self.assertFalse(report["families"]["reference_history"]["equal_to_verify_map"])

    def test_both_flag_files_listed_takes_the_verify_map_name(self):
        names = archive_names() + [mb.B6_FLAGS]
        self.write({s: names for s in ORDER})
        rc, _, mapping, report = self.run_build()
        self.assertEqual(rc, 0)
        self.assertTrue(report["copied_records_equal"])

    def test_clock_journal_count_and_zst_streams(self):
        self.write({"r4-alpha": archive_names(clock=False, streams=("stream-001.jsonl.zst", "stream-002.jsonl"))})
        rc, lines, mapping, _ = self.run_build()
        self.assertEqual(lines[1], "clock_journal: 8 of 9")
        pin = mapping["sessions"]["r4-alpha/archive"]
        self.assertNotIn("clock_journal", pin)
        self.assertEqual(pin["meter_streams"], [mb.METER_DIR + "stream-001.jsonl", mb.METER_DIR + "stream-002.jsonl"])

    def test_order_contradicting_r7_departs(self):
        order = ("r1-alpha", "r1-beta", "r1-gamma", "r2-beta", "r2-gamma", "r3-alpha", "r3-gamma", "r3-beta", "r4-alpha")
        self.write(rows=attempts_rows(order))
        rc, lines, mapping, report = self.run_build()
        self.assertEqual(rc, 5)
        self.assertEqual(lines[-1], "r7: departs (comes to the research lead)")
        self.assertIn("r3-gamma before r3-alpha", report["r7"]["contradictions"])
        self.assertIsNotNone(mapping)

    def test_relocations_and_wrong_verify_map(self):
        self.write()
        rc, _, mapping, _ = self.run_build("--relocation", "/old/path=archive")
        self.assertEqual(rc, 0)
        self.assertEqual(mapping["sessions"]["r1-alpha/archive"]["relocations"], {"/old/path": "archive"})
        bad = self.tmp / "verify.py"
        bad.write_text("# not the map\n")
        with contextlib.redirect_stdout(io.StringIO()) as buffer:
            rc = mb.main(["--names-dir", str(self.names), "--loop-attempts", str(self.attempts), "--verify-map",
                          str(bad), "--out", str(self.tmp / "m2.json"), "--report", str(self.tmp / "r2.json")])
        self.assertEqual((rc, buffer.getvalue().strip()), (4, "refused: verify_map_digest_mismatch"))

    def test_verify_map_copy_equals_the_file(self):
        text = (ROOT / "scripts/b6_r12_verify.py").read_text().splitlines()
        block = "\n".join(text[88:97])
        for family, names in mb.VERIFY_MAP.items():
            self.assertIn('"' + family + '"', block)
            for name in names:
                tail = name.split("/")[-1]
                self.assertIn(tail, block)

    @unittest.skipUnless(KIT.is_file(), "custody kit worktree not present")
    def test_the_kit_accepts_the_mapping(self):
        spec = importlib.util.spec_from_file_location("b6_custody_kit_for_test", KIT)
        kit = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(kit)
        self.write()
        rc, _, mapping, _ = self.run_build()
        self.assertEqual(rc, 0)
        entry = {"harvest_sha256": "a" * 64, "acceptance_sha256": "b" * 64, "sha256sums_sha256": "c" * 64,
                 "outside_sources": {"derived/b6-acceptance.json": "d" * 64}, "compression": None}
        for copy_path, session_map in mapping["sessions"].items():
            sid = copy_path.split("/")[0]
            names = set(archive_names())
            pin = kit.session_pin(self.tmp / sid, entry, session_map, names)
            self.assertEqual(pin["copied_records"], mb.VERIFY_MAP)
            self.assertEqual(pin["clock_journal"], mb.MONITOR + "clock.jsonl")
        del sid


if __name__ == "__main__":
    unittest.main()
