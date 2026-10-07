"""Bound-slot, source-pin, ratchet and deterministic-generation checks.

All paper locations use textual anchors; line numbers are diagnostic output only.
Mutations and CLI probes use scratch files and never write the tracked skeleton.
"""

from __future__ import annotations

import copy
from contextlib import redirect_stdout
import hashlib
import importlib.util
import io
import json
import os
import subprocess
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "docs" / "paper" / "tools"
SCRIPT = TOOLS / "check_paper_number_inventory.py"
GENERATOR = TOOLS / "gen_paper_number_inventory.py"
_spec = importlib.util.spec_from_file_location("check_paper_number_inventory", SCRIPT)
inv = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = inv
_spec.loader.exec_module(inv)

SKELETON_PATH = Path(os.environ.get(
    "PAPER_NUMBER_SKELETON", ROOT / "docs/paper/draft-v2-skeleton.md"))
SKELETON = SKELETON_PATH.read_text(encoding="utf-8")
INVENTORY = json.loads((ROOT / "docs" / "paper" / "number-inventory.json").read_text(encoding="utf-8"))
BAD = lambda rep: [f for f in rep.findings if f.status not in inv.OK_STATUSES and f.status != "CLASS_COUNT_CHANGED"]  # noqa: E731


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
        self.assertEqual(self.rep.check_failures(), [])
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
        self.assertEqual((c["bound"], c["tied"], c["classed"]), (87, 1, 10))
        for name, ceiling in INVENTORY["ratchet"].items():
            self.assertLessEqual(c[name], ceiling)
        self.assertEqual(c["literals"], sum(c[k] for k in ("bound", "tied", "classed", "unbound-results", "unaccounted")))

    def test_sections_fully_accounted(self):
        # Use section/prose anchors, never physical line positions.
        for start, end in (
            ("### Historical current-method edge result", "### Record support in two historical model stacks"),
            ("In the 1.5B run r03,", "The earlier clock-anchor defect voids these captures"),
            ("#### A.3.8 Retained calibration corpus", "#### A.3.9 Table A3:"),
        ):
            self.assertEqual(SKELETON.count(start), 1)
            self.assertEqual(SKELETON.count(end), 1)
            lo, hi = SKELETON.index(start), SKELETON.index(end)
            self.assertLess(lo, hi)
            left = [l.lit for l in self.rep.unaccounted() if lo <= l.start < hi]
            self.assertEqual(left, [], start)

    def test_cli_report_and_check_pass(self):
        out = io.StringIO()
        with redirect_stdout(out):
            for mode in ("--report", "--check"):
                self.assertEqual(inv.main([mode, "--skeleton", str(SKELETON_PATH)]), 0)
        self.assertIn("GROUP dx: bound MATCH 27", out.getvalue())
        self.assertIn("CHECK PASS: 0 finding(s)", out.getvalue())

    def test_unrelated_sentence_insertions(self):
        for anchor in ("## Abstract", "### Historical current-method edge result",
                       "In the 1.5B run r03,", "#### A.3.8 Retained calibration corpus"):
            self.assertEqual(SKELETON.count(anchor), 1)
            text = SKELETON.replace(anchor, "An unrelated sentence helps the reader follow the discussion.\n\n" + anchor)
            rep = inv.run_check(ROOT, text, INVENTORY)
            self.assertEqual(rep.check_failures(), [], anchor)
            self.assertEqual(rep.counts(), self.rep.counts(), anchor)
            self.assertEqual(len(rep.slots), 118, anchor)

    def test_generator_matches_committed_json(self):
        result = subprocess.run(
            [sys.executable, "-B", str(GENERATOR), "--check"],
            cwd=ROOT, text=True, capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("GENERATOR: PASS", result.stdout)

    def test_generator_output_is_deterministic(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "inventory.json"
            for _ in range(2):
                result = subprocess.run(
                    [sys.executable, "-B", str(GENERATOR),
                     "--output", str(output)], cwd=ROOT, text=True, capture_output=True,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertEqual(output.read_bytes(), (ROOT / "docs/paper/number-inventory.json").read_bytes())


class Mutations(unittest.TestCase):
    def assert_single_mismatch(self, text: str, slot: str, printed: str, expected: str, anchor_bit: str):
        rep = inv.run_check(ROOT, text, INVENTORY)
        bad = BAD(rep)
        self.assertEqual([(f.status, f.where) for f in bad], [("MISMATCH", slot)])
        self.assertIn(f"printed {printed!r} expected {expected!r}", bad[0].detail)
        self.assertIn(anchor_bit, bad[0].detail)  # reported with its anchor
        self.assertIsNotNone(bad[0].line)
        self.assertTrue(rep.check_failures())
        with tempfile.TemporaryDirectory() as directory:
            scratch = Path(directory) / "skeleton.md"
            scratch.write_text(text, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, "-B", str(SCRIPT), "--check", "--skeleton", str(scratch)],
                cwd=ROOT, text=True, capture_output=True,
            )
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertEqual(sum(line.startswith("MISMATCH ") for line in result.stdout.splitlines()), 1)
            self.assertIn(f"MISMATCH {slot} ", result.stdout)

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
        self.assertEqual([(f.status, f.where) for f in BAD(rep)], [("ANCHOR_MISSING", "dx.medians"), ("RATCHET_GROWTH", "unaccounted")])
        self.assertFalse([s for s in rep.slots if s["slot"].startswith("dx.medians.")])
        left = {l.lit for l in rep.unaccounted()}
        self.assertIn("+13.0", left)
        self.assertIn("−5.5", left)
        self.assertTrue(rep.check_failures())

    def test_missing_anchor_fails_cli(self):
        text = mutated("Their medians are +13.0", "Their typical values are +13.0")
        with tempfile.TemporaryDirectory() as directory:
            scratch = Path(directory) / "skeleton.md"
            scratch.write_text(text, encoding="utf-8")
            out = io.StringIO()
            with redirect_stdout(out):
                self.assertEqual(inv.main(["--check", "--skeleton", str(scratch)]), 1)
            self.assertIn("ANCHOR_MISSING dx.medians:", out.getvalue())

    def test_anchor_removed_goes_unaccounted(self):
        old = "The leader at pulse index 9 marks its +27-ms best-fit onset. "
        rep = inv.run_check(ROOT, mutated(old, "Its +27-ms best-fit onset leads. "), INVENTORY)
        self.assertEqual([(f.status, f.where) for f in BAD(rep)], [("ANCHOR_MISSING", "dx.caption_leader"), ("RATCHET_GROWTH", "unaccounted")])
        self.assertIn("+27", {l.lit for l in rep.unaccounted()})

    def test_anchor_duplicated_is_ambiguous(self):
        s = "Their medians are +13.0 ms and\n−5.5 ms."
        rep = inv.run_check(ROOT, mutated(s, s + " " + s), INVENTORY)
        self.assertIn(("ANCHOR_AMBIGUOUS", "dx.medians"), [(f.status, f.where) for f in BAD(rep)])

    def test_stale_unbound_result(self):
        # census row :718 '37' (NR is not hash-pinned, so it is left unbound)
        rep = inv.run_check(ROOT, mutated("record width; 37 phases", "record width; 38 phases"), INVENTORY)
        self.assertEqual([f.status for f in BAD(rep)], ["STALE", "RATCHET_GROWTH"])
        self.assertIn("38", {l.lit for l in rep.unaccounted()})

    def test_spelled_out_count_is_informational(self):
        rep = inv.run_check(ROOT, mutated("from one capture,\nnot independent", "from one capture and three runs,\nnot independent"), INVENTORY)
        self.assertEqual(len(rep.by_status("CLASS_COUNT_CHANGED")), 1)
        self.assertEqual(rep.check_failures(), [])


class Ratchets(unittest.TestCase):
    def test_current_ceilings(self):
        self.assertEqual(INVENTORY["ratchet"], {"unbound-results": 155, "unaccounted": 853})
        self.assertEqual(inv.run_check(ROOT, SKELETON, INVENTORY).check_failures(), [])

    def test_new_unaccounted_literal_fails_cli(self):
        text = SKELETON + "\nAn unrelated diagnostic is 987654321.\n"
        rep = inv.run_check(ROOT, text, INVENTORY)
        self.assertEqual([(f.status, f.where) for f in BAD(rep)], [("RATCHET_GROWTH", "unaccounted")])
        with tempfile.TemporaryDirectory() as directory:
            scratch = Path(directory) / "skeleton.md"
            scratch.write_text(text, encoding="utf-8")
            with redirect_stdout(io.StringIO()):
                self.assertEqual(inv.main(["--check", "--skeleton", str(scratch)]), 1)

    def test_new_unbound_result_fails_cli(self):
        text = SKELETON + "\nAn unrelated diagnostic is 987654321.\n"
        inv2 = copy.deepcopy(INVENTORY)
        inv2["unbound_results"].append({
            "literal": "987654321", "ctx": "An unrelated diagnostic is 987654321.",
            "offset": len("An unrelated diagnostic is "),
        })
        rep = inv.run_check(ROOT, text, inv2)
        self.assertEqual([(f.status, f.where) for f in BAD(rep)], [("RATCHET_GROWTH", "unbound-results")])
        with tempfile.TemporaryDirectory() as directory:
            scratch = Path(directory) / "skeleton.md"
            scratch.write_text(text, encoding="utf-8")
            inventory = Path(directory) / "inventory.json"
            inventory.write_text(json.dumps(inv2), encoding="utf-8")
            with redirect_stdout(io.StringIO()):
                self.assertEqual(inv.main(["--check", "--skeleton", str(scratch),
                                           "--inventory", str(inventory)]), 1)

    def test_decreasing_either_count_passes(self):
        original = inv.run_check(ROOT, SKELETON, INVENTORY)
        for name, literal in (("unaccounted", original.unaccounted()[0]),
                              ("unbound-results", next(l for l in original.literals if l.claim == "unbound-results"))):
            # Keep the surrounding context, removing only the unbound number.
            text = SKELETON[:literal.start] + "several" + SKELETON[literal.end:]
            rep = inv.run_check(ROOT, text, INVENTORY)
            self.assertLess(rep.counts()[name], original.counts()[name])
            self.assertEqual(rep.check_failures(), [], name)

    def test_missing_or_invalid_ceiling_fails(self):
        for value in (None, -1, True, "853"):
            inv2 = copy.deepcopy(INVENTORY)
            inv2["ratchet"]["unaccounted"] = value
            self.assertIn("ERROR ratchet unaccounted", inv.run_check(ROOT, SKELETON, inv2).check_failures())


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
        self.assertTrue(rep.check_failures())

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
            self.assertEqual(inv.main(["--check", "--source", f"XD={self.bad_xd}"]), 1)
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
