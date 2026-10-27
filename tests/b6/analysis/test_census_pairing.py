"""A1 (counting from the loop's acceptance) and A2 (GAMMA pairing by round)."""
from __future__ import annotations

import builtins
import json
import pathlib
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from joulewise.b6.analysis import census as census_module
from joulewise.b6.analysis import pairing
from joulewise.b6.analysis.census import CensusRefusal, census_from_state, load_census
from tests.b6.analysis.fakes import CLOSED_BLOCK6, attempt_line, write_loop_root, write_r2_gamma_exclusions


class OpenTripwire:
    """Record every path opened while active."""

    def __init__(self):
        self.paths = []

    def __enter__(self):
        real_open, real_path_open = builtins.open, pathlib.Path.open
        tripwire = self

        def record_open(file, *args, **kwargs):
            tripwire.paths.append(str(file))
            return real_open(file, *args, **kwargs)

        def record_path_open(self, *args, **kwargs):
            tripwire.paths.append(str(self))
            return real_path_open(self, *args, **kwargs)

        self._patches = [mock.patch("builtins.open", record_open), mock.patch.object(pathlib.Path, "open", record_path_open)]
        for patch in self._patches:
            patch.start()
        return self

    def __exit__(self, *exc):
        for patch in reversed(self._patches):
            patch.stop()


class CountingFromLoopAcceptance(unittest.TestCase):
    def test_closed_block6_census(self):
        with tempfile.TemporaryDirectory() as tmp:
            census = load_census(write_loop_root(Path(tmp)))
        counting = {p: [e.session_id for e in census.counting(p)] for p in ("alpha", "beta", "gamma")}
        self.assertEqual(counting, {"alpha": ["r1-alpha", "r3-alpha", "r4-alpha"],
                                    "beta": ["r1-beta", "r2-beta", "r3-beta"],
                                    "gamma": ["r1-gamma", "r2-gamma", "r3-gamma"]})
        self.assertTrue(census.closed)
        self.assertEqual([e.session_id for e in census.pack("alpha")], ["r1-alpha", "r2-alpha", "r3-alpha", "r4-alpha"])
        self.assertFalse(census.get("r2-alpha").counting)

    def test_r2_gamma_counts_although_its_exclusions_say_claim_usable_false(self):
        """RUN_STATE item 53: block 5's neg8.midpoint_lost_primary must not decide counting."""
        with tempfile.TemporaryDirectory() as tmp:
            root = write_loop_root(Path(tmp))
            exclusions = write_r2_gamma_exclusions(root)
            self.assertFalse(json.loads(exclusions.read_text())["claim_usable"])
            with OpenTripwire() as tripwire:
                census = load_census(root)
        self.assertTrue(census.get("r2-gamma").counting)
        self.assertFalse(any(p.endswith("exclusions.json") for p in tripwire.paths))
        self.assertTrue(any(p.endswith("attempts.jsonl") for p in tripwire.paths))

    def test_reharvest_correction_in_state_decides(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = write_loop_root(Path(tmp), reharvested={"r2-alpha": {"alpha": {"status": "counting", "cause": None}}})
            census = load_census(root)
        self.assertTrue(census.get("r2-alpha").counting)

    def test_codes_are_read_from_the_attempt_line(self):
        state = {"attempts": [attempt_line("r1-alpha", "alpha", 1, "not_counting",
                                           codes=("neg8.survivor_screen_failed",))]}
        entry = census_from_state(state).get("r1-alpha")
        self.assertEqual(entry.codes, ("neg8.survivor_screen_failed",))
        self.assertFalse(entry.counting)

    def test_other_loops_packs_are_ignored(self):
        state = {"attempts": [attempt_line("s1", "bytes-s1-p1", 1, "counting")]}
        self.assertEqual(census_from_state(state).entries, ())

    def test_malformed_records_refuse(self):
        good = attempt_line("r1-alpha", "alpha", 1, "counting")
        for broken in ({**good, "round": 0}, {**good, "round": "1"}, {k: v for k, v in good.items() if k != "line"},
                       {**good, "outcomes": {"alpha": {}}}):
            with self.subTest(broken=sorted(broken)), self.assertRaises(CensusRefusal):
                census_from_state({"attempts": [broken]})
        with self.assertRaises(CensusRefusal) as caught:
            census_from_state({"attempts": [good, good]})
        self.assertEqual(caught.exception.code, "attempt_session_duplicated")
        with self.assertRaises(CensusRefusal) as caught:
            census_from_state({"attempts": [good, attempt_line("r1-alpha-b", "alpha", 1, "counting")]})
        self.assertEqual(caught.exception.code, "two_counting_sessions_in_one_round")

    def test_unreadable_loop_root_refuses(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(CensusRefusal) as caught:
                load_census(Path(tmp))
        self.assertEqual(caught.exception.code, "loop_record_unreadable")

    def test_structure_record_has_no_number_but_rounds(self):
        with tempfile.TemporaryDirectory() as tmp:
            record = census_module.structure_record(load_census(write_loop_root(Path(tmp))))
        self.assertEqual(set(record["sessions"][0]), {"session_id", "pack", "round", "status", "counting", "structure_ok"})


def census_of(rows, closed=True):
    state = {"state": "DONE" if closed else "NEXT", "attempts": [attempt_line(*row) for row in rows]}
    return census_from_state(state)


class PairingByRound(unittest.TestCase):
    def test_closed_block6_pairing(self):
        census = census_of(CLOSED_BLOCK6)
        pairs = {p.gamma: (p.alpha.session_id, p.beta.session_id) for p in pairing.pair_all(census)}
        self.assertEqual(pairs, {"r1-gamma": ("r1-alpha", "r1-beta"), "r2-gamma": ("r3-alpha", "r2-beta"),
                                 "r3-gamma": ("r3-alpha", "r3-beta")})
        rules = {p.gamma: (p.alpha.rule, p.beta.rule) for p in pairing.pair_all(census)}
        self.assertEqual(rules["r2-gamma"], ("next_counting", "same_round"))
        self.assertFalse(any(p.provisional or p.floor_from_block5 for p in pairing.pair_all(census)))

    def test_registration_worked_example(self):
        """§6.2: BETA_1 stopped; BETA_4 counts; GAMMA_1 takes BETA_2 (rule 2)."""
        rows = [("A1", "alpha", 1, "counting"), ("B1", "beta", 1, "physics_stopped"), ("G1", "gamma", 1, "counting"),
                ("B2", "beta", 2, "counting"), ("G2", "gamma", 2, "counting"), ("A2", "alpha", 2, "counting"),
                ("G3", "gamma", 3, "counting"), ("A3", "alpha", 3, "counting"), ("B3", "beta", 3, "counting"),
                ("B4", "beta", 4, "counting")]
        pairs = {p.gamma: (p.alpha.session_id, p.beta.session_id) for p in pairing.pair_all(census_of(rows))}
        self.assertEqual(pairs, {"G1": ("A1", "B2"), "G2": ("A2", "B2"), "G3": ("A3", "B3")})

    def test_pairing_never_reads_a_value(self):
        # Same counting and rounds, different everything else: same pairing.
        rows = list(CLOSED_BLOCK6)
        census = census_of(rows)
        reordered = census_of(list(reversed(rows)))
        self.assertEqual([p.as_record() for p in pairing.pair_all(census)],
                         [p.as_record() for p in pairing.pair_all(reordered)])

    def test_rule_three_and_floor_from_block5(self):
        rows = [("A1", "alpha", 1, "counting"), ("G3", "gamma", 3, "counting")]
        (only,) = pairing.pair_all(census_of(rows))
        self.assertEqual((only.alpha.session_id, only.alpha.rule), ("A1", "last_earlier"))
        self.assertEqual((only.beta.session_id, only.beta.rule), (pairing.BLOCK5, "floor_from_block_5"))
        self.assertTrue(only.floor_from_block5)

    def test_before_the_close_a_non_same_round_pairing_is_provisional(self):
        rows = [("A2", "alpha", 2, "counting"), ("B1", "beta", 1, "counting"), ("G1", "gamma", 1, "counting")]
        (only,) = pairing.pair_all(census_of(rows, closed=False))
        self.assertTrue(only.provisional)
        (closed,) = pairing.pair_all(census_of(rows, closed=True))
        self.assertFalse(closed.provisional)

    def test_a_gamma_session_s_own_counting_does_not_change_its_pairing(self):
        census = census_of(CLOSED_BLOCK6 + (("r4-gamma", "gamma", 4, "physics_stopped"),))
        paired = pairing.pair(census, census.get("r4-gamma"))
        self.assertEqual((paired.alpha.session_id, paired.beta.session_id), ("r4-alpha", "r3-beta"))


if __name__ == "__main__":
    unittest.main()
