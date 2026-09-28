"""Tests for the paper-number inventory checker (PROTOTYPE; report-only; not a gate).

The real-skeleton test pins how many slots each bound group checks, so an
inventory whose anchors silently stopped matching cannot pass by checking
nothing.  Every mutation is applied to an in-memory copy of the skeleton; the
tracked file is never written.  A mutation's ``old`` text must occur exactly
once, so each test changes the site it names and no other.
"""

from __future__ import annotations

import copy
from contextlib import redirect_stdout
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_paper_number_inventory.py"
_spec = importlib.util.spec_from_file_location("check_paper_number_inventory", SCRIPT)
inv = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = inv
_spec.loader.exec_module(inv)

SKELETON = (ROOT / "docs" / "paper" / "draft-v2-skeleton.md").read_text(encoding="utf-8")
INVENTORY = json.loads((ROOT / "docs" / "paper" / "number-inventory.json").read_text(encoding="utf-8"))
BAD = lambda rep: [f for f in rep.findings if f.status not in inv.OK_STATUSES]  # noqa: E731


def mutated(old: str, new: str) -> str:
    assert SKELETON.count(old) == 1, f"mutation site {old!r} occurs {SKELETON.count(old)} times"
    return SKELETON.replace(old, new)


class RealSkeleton(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rep = inv.run_check(ROOT, SKELETON, INVENTORY)

    def test_sources_verified(self):
        for name in ("XD", "WEX", "S17"):
            self.assertTrue(self.rep.sources[name].startswith("OK sha256"), self.rep.sources[name])

    def test_bound_groups_all_match(self):
        self.assertEqual(BAD(self.rep), [])
        per_group: dict[str, int] = {}
        for s in self.rep.slots:
            self.assertEqual(s["printed"], s["expected"], s)
            per_group[s["group"]] = per_group.get(s["group"], 0) + 1
        # anti-vacuity: the number of slots each group actually compared
        self.assertEqual(per_group, {"dx": 30, "s4_overlap": 50, "a38": 38})
        self.assertEqual(len(self.rep.by_status("REGISTRY_OK")), 7)
        self.assertEqual(len(self.rep.by_status("PREDICATE_OK")), 28)

    def test_counts(self):
        c = self.rep.counts()
        self.assertEqual(c["literals"], 1106)  # the 2026-09-28 census count
        self.assertEqual((c["bound"], c["tied"], c["classed"]), (87, 1, 10))
        self.assertEqual(c["unbound-results"], len(INVENTORY["unbound_results"]))
        self.assertEqual(c["literals"], sum(c[k] for k in ("bound", "tied", "classed", "unbound-results", "unaccounted")))

    def test_sections_fully_accounted(self):
        # DX section + caption, the Section 4 table, and A.3.8 hold no unaccounted literal
        for lo, hi in ((556, 606), (720, 740), (1245, 1278)):
            left = [(l.line, l.lit) for l in self.rep.unaccounted() if lo <= l.line <= hi]
            self.assertEqual(left, [], (lo, hi))

    def test_cli_report_exit_0_strict_exit_1(self):
        out = io.StringIO()
        with redirect_stdout(out):
            self.assertEqual(inv.main(["--report"]), 0)
            # strict fails today: most literals are not yet inventoried
            self.assertEqual(inv.main(["--strict"]), 1)
        self.assertIn("GROUP dx: bound MATCH 27", out.getvalue())


class Mutations(unittest.TestCase):
    def assert_single_mismatch(self, text: str, slot: str, printed: str, expected: str, anchor_bit: str):
        rep = inv.run_check(ROOT, text, INVENTORY)
        bad = BAD(rep)
        self.assertEqual([(f.status, f.where) for f in bad], [("MISMATCH", slot)])
        self.assertIn(f"printed {printed!r} expected {expected!r}", bad[0].detail)
        self.assertIn(anchor_bit, bad[0].detail)  # reported with its anchor
        self.assertIsNotNone(bad[0].line)

    def test_dx_median(self):
        self.assert_single_mismatch(
            mutated("Their medians are +13.0 ms", "Their medians are +14.0 ms"),
            "dx.medians.onset_median", "+14.0", "+13.0", "Their medians are",
        )

    def test_dx_median_sign(self):
        self.assert_single_mismatch(
            mutated("respective medians,\n+13.0 ms and −5.5 ms", "respective medians,\n+13.0 ms and +5.5 ms"),
            "dx.caption_medians.offset_median", "+5.5", "−5.5", "respective medians",
        )

    def test_dx_count(self):
        self.assert_single_mismatch(
            mutated("; 49 of 59 offset lags", "; 50 of 59 offset lags"),
            "dx.counts.off_neg", "50", "49", "offset lags are negative",
        )

    def test_dx_spelled_count(self):
        self.assert_single_mismatch(
            mutated("eight positive,\nand two zero", "nine positive,\nand two zero"),
            "dx.counts.off_pos", "nine", "eight", "positive, and",
        )

    def test_a38_value(self):
        self.assert_single_mismatch(
            mutated("| 0.027365018417518542 |", "| 0.027365018417518543 |"),
            "a38.table.v1", "0.027365018417518543", "0.027365018417518542", "Capture member",
        )

    def test_overlap_cell(self):
        self.assert_single_mismatch(
            mutated("| 0.0676686 |", "| 0.0676687 |"),
            "s4.table.r03_2_ov", "0.0676687", "0.0676686", "Positive-overlap duration",
        )

    def test_anchor_reworded_goes_unaccounted(self):
        rep = inv.run_check(ROOT, mutated("Their medians are +13.0", "Their typical values are +13.0"), INVENTORY)
        self.assertEqual([(f.status, f.where) for f in BAD(rep)], [("ANCHOR_MISSING", "dx.medians")])
        self.assertFalse([s for s in rep.slots if s["slot"].startswith("dx.medians.")])
        left = {(l.line, l.lit) for l in rep.unaccounted()}
        self.assertIn((573, "+13.0"), left)
        self.assertIn((574, "−5.5"), left)

    def test_anchor_removed_goes_unaccounted(self):
        old = "The leader at pulse index 9 marks its +27-ms best-fit onset. "
        rep = inv.run_check(ROOT, mutated(old, "Its +27-ms best-fit onset leads. "), INVENTORY)
        self.assertEqual([(f.status, f.where) for f in BAD(rep)], [("ANCHOR_MISSING", "dx.caption_leader")])
        self.assertIn("+27", {l.lit for l in rep.unaccounted() if l.line == 590})

    def test_anchor_duplicated_is_ambiguous(self):
        s = "Their medians are +13.0 ms and\n−5.5 ms."
        rep = inv.run_check(ROOT, mutated(s, s + " " + s), INVENTORY)
        self.assertIn(("ANCHOR_AMBIGUOUS", "dx.medians"), [(f.status, f.where) for f in BAD(rep)])

    def test_stale_unbound_result(self):
        # census row :718 '37' (NR is not hash-pinned, so it is left unbound)
        rep = inv.run_check(ROOT, mutated("record width; 37 phases", "record width; 38 phases"), INVENTORY)
        self.assertEqual([f.status for f in BAD(rep)], ["STALE"])
        self.assertIn((718, "38"), {(l.line, l.lit) for l in rep.unaccounted()})

    def test_spelled_out_count_pinned(self):
        rep = inv.run_check(ROOT, mutated("from one capture,\nnot independent", "from one capture and three runs,\nnot independent"), INVENTORY)
        self.assertEqual([f.status for f in BAD(rep)], ["CLASS_COUNT_CHANGED"])


class SourceRefusal(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        xd = (ROOT / INVENTORY["sources"]["XD"]["path"]).read_text(encoding="utf-8")
        self.assertEqual(xd.count('"median_ms": 13.0'), 1)
        self.bad_xd = Path(self.tmp.name) / "xd.json"
        self.bad_xd.write_text(xd.replace('"median_ms": 13.0', '"median_ms": 14.0'), encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def _assert_xd_refused(self, rep, reason: str):
        self.assertTrue(rep.sources["XD"].startswith("REFUSED"), rep.sources["XD"])
        self.assertIn(reason, rep.sources["XD"])
        xd_slots = [s for s in rep.slots if "XD:" in json.dumps(self._slot_spec(s["slot"]))]
        self.assertGreater(len(xd_slots), 20)
        for s in xd_slots:
            self.assertIsNone(s["expected"], s)  # never MATCH on a refused source
        self.assertFalse([f for f in rep.findings if f.status == "PREDICATE_OK" and "XD" in f.detail])

    @staticmethod
    def _slot_spec(sid: str) -> dict:
        eid, sname = sid.rsplit(".", 1)
        for g in INVENTORY["groups"]:
            for e in g["entries"]:
                if e["id"] == eid:
                    return e["slots"][sname]
        raise KeyError(sid)

    def test_tampered_xd_refused(self):
        # even with the paper edited to agree with the tampered value
        text = mutated("Their medians are +13.0 ms", "Their medians are +14.0 ms")
        rep = inv.run_check(ROOT, text, INVENTORY, {"XD": self.bad_xd})
        self._assert_xd_refused(rep, "differs from pin")
        self.assertIn(("REFUSED", "source XD"), [(f.status, f.where) for f in rep.findings])
        self.assertTrue(rep.strict_failures())

    def test_inventory_cannot_self_authorize(self):
        # re-pinning the inventory to the tampered bytes still disagrees with the registry pin
        inv2 = copy.deepcopy(INVENTORY)
        inv2["sources"]["XD"]["sha256"] = hashlib.sha256(self.bad_xd.read_bytes()).hexdigest()
        rep = inv.run_check(ROOT, SKELETON, inv2, {"XD": self.bad_xd})
        self._assert_xd_refused(rep, "differs from authority pin")

    def test_cli_source_override_refused_but_report_exit_0(self):
        out = io.StringIO()
        with redirect_stdout(out):
            self.assertEqual(inv.main(["--report", "--source", f"XD={self.bad_xd}"]), 0)
            self.assertEqual(inv.main(["--strict", "--source", f"XD={self.bad_xd}"]), 1)
        self.assertIn("SOURCE XD: REFUSED", out.getvalue())


class Renderers(unittest.TestCase):
    def test_signed_1(self):
        self.assertEqual(inv.r_signed_1(13.0), "+13.0")
        self.assertEqual(inv.r_signed_1(-5.5), "−5.5")
        self.assertEqual(inv.r_signed_1(0.0), "0.0")

    def test_exact_shift_and_overlap(self):
        self.assertEqual(inv.r_s_to_ms_exact(0.0005), "0.5")
        self.assertEqual(inv.r_s_to_ms_exact("0.02893293456111476"), "28.93293456111476")
        self.assertEqual(inv.r_positive_overlap_decimal("0.671041", "0.807431", "0.799845", "0.9133315"), "0.007586")
        self.assertEqual(inv.r_positive_overlap_decimal("0.267684", "0.3887181", "0.0726435", "0.1945655"), "0")

    def test_word_and_integer(self):
        self.assertEqual(inv.r_word_int(8), "eight")
        with self.assertRaises(inv.ExprError):
            inv.r_integer(True)


if __name__ == "__main__":
    unittest.main()
