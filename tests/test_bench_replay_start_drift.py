"""Cold ruling 21's admissibility rule, executed on the run it was ruled over.

The bench replay driver (`scripts/bench_replay_start_drift.py`) used to fail a
run unless EVERY slot came back `anchor_status: "bounded"` with
`interior_complete_support` -- the lead's convention, written into record 16
as "X2" before any full replay existed -- and unless every SESSION-level
`start_drift_s` was at or under 0.5 s ("X1").  Cold gate #3 ruling 21 of
2026-09-22
(`docs/process_traces/2026-09-22-activation-59857fe5/08-coldgate-packet-a267-merge-transaction/21-coldgate-fable-replay-verdict-ruling.md`)
struck both and put a six-clause rule in their place; condition C3 of that
ruling requires the driver amendment to show `verdict()` re-run on the
2026-09-22 replay JSON producing PASS.  Test (a) below is that re-run, taken
over the tracked artifact itself rather than a fixture.

Every test here fails on the pre-amendment driver:

(a) the executed replay came back FAIL; (b) a slot RESOLVING an anchor the
archive left unresolved was the pre-amendment driver's idea of a good slot;
(c) a run with no resolved anchor anywhere failed per-slot, not on the ruled
floor, and reported neither; (d) the skipped-tail budget did not exist;
(e) a 2.1 s session figure escalated under the old 0.5 s convention but so
did 0.6 s, which the night's ruled 2 s rule passes; (f) the smoke exemption
covered two admissibility FIELDS, and now covers the two ruled RULES taken
over them.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts import bench_replay_start_drift as bench  # noqa: E402

# The tracked artifact of the full replay executed at the merged head
# 4f8bc36d on 2026-09-22, and the ruling that condition C3 comes from.
REPLAY_JSON = (REPO_ROOT / "docs" / "process_traces"
               / "2026-09-22-activation-59857fe5" / "24-bench-replay.json")
RULING = ("docs/process_traces/2026-09-22-activation-59857fe5/"
          "08-coldgate-packet-a267-merge-transaction/"
          "21-coldgate-fable-replay-verdict-ruling.md")
# The full protocol's own figures: a 620 s pitch over a 600 s envelope leaves
# the 20 s inter-slot gap that produces the bar.
PROTOCOL = {"envelopes": 12, "slot_pitch_s": 620, "envelope_s": 600}
SMOKE_PROTOCOL = {"envelopes": 12, "slot_pitch_s": 80, "envelope_s": 60}


def faithful_rows(**overrides):
    """Twelve rows whose anchor CLASS is the archived night's own for each slot.

    This is what a faithful replay looks like: the archive resolved seven of
    its twelve envelopes and left five unresolved, and a replay reproducing
    those classes is the one ruling 21 rule (4) admits.  Every other field is
    inert and clean unless a test changes it.
    """

    rows = []
    for index in range(1, 13):
        bounded = index in bench.ARCHIVED_V31_BOUNDED
        row = {"index": index, "chain_start_drift_s": 0.150,
               "session_start_drift_s": 0.404, "collector_exit": 0,
               "cleanup_proven": True, "attestation_state": "authenticated",
               "anchor_status": "bounded" if bounded else "unknown",
               "anchor_detail": None if bounded else "affine_clock_fit_empty",
               "interior_complete_support": bounded,
               "tail_s": 8.0 if bounded else 5.5}
        row.update(overrides)
        rows.append(row)
    return rows


class RuledReplayVerdictTests(unittest.TestCase):

    def test_a_the_executed_2026_09_22_replay_passes_the_ruled_rule(self):
        """Ruling 21 condition C3: `verdict()` re-run on THIS JSON produces PASS.

        The rows are the tracked artifact's own twelve, read from
        `24-bench-replay.json`; nothing here is a fixture.  The
        pre-amendment driver returned FAIL on them, for the seven slots whose
        anchors the ARCHIVE also left unresolved.
        """

        report = json.loads(REPLAY_JSON.read_text())
        result = bench.verdict(report["slots"], report["protocol"])
        self.assertEqual(result["status"], "PASS", result["statement"])
        # (1) twelve of twelve, no missing chain figure.
        self.assertEqual(result["slots_recorded"], 12)
        self.assertEqual(result["slots_expected"], 12)
        self.assertEqual(result["slots_missing_chain_drift"], [])
        # (2) every slot exited, was torn down and attested.
        self.assertEqual(result["slot_defects"], [])
        # (3) the ruled bar, on the chain-level figure.
        self.assertAlmostEqual(result["max_chain_start_drift_s"], 0.352, places=3)
        self.assertEqual(result["slots_over_bar"], [])
        self.assertIn("0.352 s <= 0.5 s", result["statement"])
        # (4) the fidelity table and its tally: two refusing, none admitting.
        self.assertEqual(result["fidelity"]["tally"],
                         "10/12 match; admitting-direction 0; refusing-direction 2")
        self.assertEqual(result["admitting_direction_slots"], [])
        self.assertEqual(result["refusing_direction_slots"], [8, 9])
        # (5) the floor: five slots bounded with complete interior support.
        self.assertEqual(result["bounded_interior_slots"], [2, 5, 6, 11, 12])
        self.assertTrue(result["bounded_interior_floor_met"])
        # (6) the worst tail plus the archive's worst skipped tail, in the gap.
        budget = result["tail_budget"]
        self.assertAlmostEqual(budget["max_tail_s"], 8.410, places=3)
        self.assertEqual(budget["gap_s"], 20)
        self.assertAlmostEqual(budget["budget_s"], 10.710, places=3)
        self.assertTrue(budget["fits"])
        self.assertIn("8.410 s + 2.3 s worst skipped tail = 10.710 s < the 20 s "
                      "inter-slot gap", result["statement"])
        # The session figure is REPORTED and assessed against the night's 2 s
        # rule, which slot 1's 0.608 s clears with 1.39 s of margin.
        self.assertAlmostEqual(result["max_session_start_drift_s"], 0.608, places=3)
        self.assertEqual(result["session_slots_over_bar"], [])
        self.assertFalse(result["session_bar_exceeded"])
        # And the artifact a magistrate reads carries the ruled text, the
        # fidelity table with its tally, and the tail budget with figures.
        report["verdict"] = result
        text = bench.markdown(report)
        self.assertIn("**PASS**", text)
        self.assertIn(bench.RULED_ADMISSIBILITY_TEXT, text)
        self.assertIn("## Anchor fidelity vs the archived v3.1 class", text)
        self.assertIn("| 8 | unknown | affine_clock_residual_exceeded | bounded | refusing |",
                      text)
        self.assertIn("| 2 | bounded | None | bounded | match |", text)
        self.assertIn("Tally: 10/12 match; admitting-direction 0; refusing-direction 2.",
                      text)
        self.assertIn("max tail_s 8.410 s + 2.3 s worst skipped tail = 10.710 s < the "
                      "20 s inter-slot gap", text)

    def test_b_a_slot_resolving_what_the_archive_refused_voids_the_run(self):
        """Ruling 21 rule (4), ADMITTING direction: one such slot VOIDS the run.

        Envelope 01 is `affine_clock_fit_empty` in the archive's own v3.1
        projection -- a real slew inside the capture.  A replay that resolves
        it is a recorder producing a result the archive lacks, which is
        infidelity.  The pre-amendment driver treated exactly this slot as
        the only acceptable kind.
        """

        rows = faithful_rows()
        rows[0].update(anchor_status="bounded", anchor_detail=None,
                       interior_complete_support=True, tail_s=8.0)
        result = bench.verdict(rows, PROTOCOL)
        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(result["admitting_direction_slots"], [1])
        self.assertIn({"index": 1, "field": "anchor_status", "value": "bounded",
                       "required": "not 'bounded' where the archived v3.1 class is "
                                   "unresolved (an ADMITTING-direction mismatch VOIDS "
                                   "the run)"},
                      result["slot_defects"])
        self.assertTrue(result["statement"].startswith(
            "anchor fidelity VOIDS the run: slots [1] resolved"), result["statement"])
        self.assertIn("11/12 match; admitting-direction 1; refusing-direction 0",
                      result["statement"])
        # The counterfactual, executed: the SAME run with envelope 01 left
        # unresolved, as the archive left it, passes.
        self.assertEqual(bench.verdict(faithful_rows(), PROTOCOL)["status"], "PASS")
        # And the fidelity function says the same thing on its own.
        table = bench.fidelity(rows)
        self.assertEqual(table["admitting"], [1])
        self.assertEqual(table["refusing"], [])
        self.assertEqual([entry["direction"] for entry in table["table"] if entry["index"] == 1],
                         ["admitting"])

    def test_c_a_run_with_no_resolved_anchor_anywhere_fails_the_floor(self):
        """Ruling 21 rule (5): at least one slot `bounded` with complete interior support.

        This is what X2 was actually for (execution lens 17b B2): proof that
        the finalisation tail the bench exists to time ran at this head.  A
        run in which `align_frames` returned nothing anywhere fails here --
        at the RUN level, not per slot, because a single unresolved slot is a
        faithful reproduction of the archive and not a defect.
        """

        rows = faithful_rows(anchor_status="unknown",
                             anchor_detail="affine_clock_fit_empty",
                             interior_complete_support=False)
        result = bench.verdict(rows, PROTOCOL)
        self.assertEqual(result["status"], "FAIL")
        self.assertFalse(result["bounded_interior_floor_met"])
        self.assertEqual(result["bounded_interior_slots"], [])
        self.assertEqual(result["slot_defects"], [])
        self.assertTrue(result["statement"].startswith(
            "no slot is 'bounded' with complete interior support"), result["statement"])
        self.assertIn("5/12 match; admitting-direction 0; refusing-direction 7",
                      result["statement"])
        # A slot that resolved its anchor but whose interior reduction did
        # NOT complete does not satisfy the floor either: the expensive part
        # of the tail is the interior.
        half = faithful_rows()
        for row in half:
            row["interior_complete_support"] = False
        self.assertEqual(bench.verdict(half, PROTOCOL)["status"], "FAIL")
        self.assertEqual(bench.verdict(half, PROTOCOL)["bounded_interior_slots"], [])
        # The counterfactual, executed: ONE slot with both is the floor.
        one = faithful_rows()
        for row in one[1:]:
            row.update(anchor_status="unknown", anchor_detail="affine_clock_fit_empty",
                       interior_complete_support=False)
        one[1].update(anchor_status="bounded", anchor_detail=None,
                      interior_complete_support=True)
        floor = bench.verdict(one, PROTOCOL)
        self.assertEqual(floor["status"], "PASS", floor["statement"])
        self.assertEqual(floor["bounded_interior_slots"], [2])

    def test_d_a_tail_that_would_not_fit_the_gap_with_the_skipped_work_fails(self):
        """Ruling 21 rule (6): max `tail_s` + 2.3 s < the inter-slot gap.

        A refusing-direction slot does LESS tail work than the archive did,
        by at most the archive's own worst skipped tail (A269 exhibit C,
        `end-postparse` max 2.291 s).  Adding that to the worst MEASURED tail
        bounds what a fully-resolving replay could have cost, and that bound
        must still fit the gap, or the fidelity tolerance in rule (4) is not
        safe.  The pre-amendment driver budgeted nothing.
        """

        rows = faithful_rows()
        rows[10]["tail_s"] = 17.7
        result = bench.verdict(rows, PROTOCOL)
        self.assertEqual(result["status"], "FAIL")
        self.assertFalse(result["tail_budget"]["fits"])
        self.assertTrue(result["statement"].startswith(
            "the skipped-tail budget does not fit the inter-slot gap"), result["statement"])
        self.assertIn("max tail_s 17.700 s + 2.3 s worst skipped tail = 20.000 s >= "
                      "the 20 s inter-slot gap", result["statement"])
        # The counterfactual, executed: a millisecond under the gap passes.
        rows[10]["tail_s"] = 17.699
        self.assertEqual(bench.verdict(rows, PROTOCOL)["status"], "PASS")
        # A protocol that states no gap leaves the rule UNASSESSABLE, which
        # is a FAIL and not a skip.
        blind = bench.verdict(faithful_rows(), {"envelopes": 12})
        self.assertEqual(blind["status"], "FAIL")
        self.assertIsNone(blind["tail_budget"]["gap_s"])
        self.assertIn("the inter-slot gap the tail must fit is unknown", blind["statement"])

    def test_e_the_session_figure_is_assessed_against_the_nights_two_second_rule(self):
        """Ruling 21 Q1: the 0.5 s bench bar binds the CHAIN-level figure only.

        The session-level figure runs ~0.12-0.16 s above the chain-level one
        and is reported per slot, but the only ruled session bar in the lane
        is the night's own 2 s rule (A269 ruling 10 amendment A1).  The
        driver's 0.5 s session bar was a lead convention, and on the executed
        2026-09-22 replay it would have exited ESCALATE rc 3 on slot 1's
        0.608 s -- a figure that clears the ruled rule by 1.39 s.  The third
        status itself is unchanged: a chain pass over the 2 s rule still
        escalates and still exits 3.
        """

        self.assertEqual(bench.SESSION_BAR_S, 2.0)
        over = faithful_rows()
        over[0]["session_start_drift_s"] = 2.1
        result = bench.verdict(over, PROTOCOL)
        self.assertEqual(result["status"], "ESCALATE")
        self.assertTrue(result["escalate_chain_pass_session_fail"])
        self.assertTrue(result["session_bar_exceeded"])
        self.assertEqual(result["session_slots_over_bar"], [1])
        self.assertIn("max 2.100 s > 2.0 s on slots [1]", result["statement"])
        self.assertIn("ESCALATED to the magistrate", result["statement"])
        # The behaviour that CHANGED: the executed replay's own slot 1
        # figure is not an escalation.
        under = faithful_rows()
        under[0]["session_start_drift_s"] = 0.608
        ruled = bench.verdict(under, PROTOCOL)
        self.assertEqual(ruled["status"], "PASS")
        self.assertFalse(ruled["escalate_chain_pass_session_fail"])
        self.assertFalse(ruled["session_bar_exceeded"])
        self.assertEqual(ruled["session_slots_over_bar"], [])
        self.assertIn("max(session start_drift_s) = 0.608 s <= 2.0 s, the night's rule",
                      ruled["statement"])
        # And the old convention, executed as a counterfactual: pass the
        # struck 0.5 s bar in explicitly and the same run escalates again.
        self.assertEqual(bench.verdict(under, PROTOCOL, session_bar_s=0.5)["status"],
                         "ESCALATE")

    def test_f_a_smoke_does_not_have_rules_four_and_five_applied_to_it(self):
        """A 60 s smoke envelope cannot resolve an anchor, so (4) and (5) do not apply.

        The exemption is the same one the driver has always carried for
        `SMOKE_EXEMPT_FIELDS`; what it switches off is now the two ruled
        RULES taken over those fields rather than two per-slot admissibility
        requirements.  Nothing else is exempt -- (1), (2), (3) and (6), and
        the attestation states, bind a smoke as they bind a full run.
        """

        rows = faithful_rows(anchor_status="unknown",
                             anchor_detail="clock_fit_span_insufficient",
                             interior_complete_support=False, tail_s=1.0)
        smoke = bench.verdict(rows, SMOKE_PROTOCOL, smoke=True)
        self.assertEqual(smoke["status"], "PASS", smoke["statement"])
        self.assertFalse(smoke["fidelity_applied"])
        self.assertEqual(smoke["admitting_direction_slots"], [])
        self.assertEqual(smoke["refusing_direction_slots"], [])
        self.assertTrue(smoke["bounded_interior_floor_met"])
        self.assertEqual(smoke["smoke_exempt_fields"],
                         list(bench.SMOKE_EXEMPT_FIELDS))
        self.assertIn("anchor fidelity and the bounded-with-interior floor are NOT "
                      "applied to a smoke", smoke["statement"])
        # An ADMITTING-direction slot is not a defect under smoke either,
        # because the comparison is not made at all.
        admitting = [dict(row) for row in rows]
        admitting[0].update(anchor_status="bounded", interior_complete_support=True)
        self.assertEqual(bench.verdict(admitting, SMOKE_PROTOCOL, smoke=True)["status"],
                         "PASS")
        # The counterfactual, executed: the same rows under the FULL protocol
        # fail, on the floor and then on fidelity.
        self.assertEqual(bench.verdict(rows, SMOKE_PROTOCOL)["status"], "FAIL")
        self.assertTrue(bench.verdict(rows, SMOKE_PROTOCOL)["statement"].startswith(
            "no slot is 'bounded' with complete interior support"))
        self.assertEqual(bench.verdict(admitting, SMOKE_PROTOCOL)["admitting_direction_slots"],
                         [1])
        # Rule (6) is NOT exempt: a smoke whose tail overruns its own gap fails.
        long_tail = [dict(row, tail_s=18.0) for row in rows]
        overrun = bench.verdict(long_tail, SMOKE_PROTOCOL, smoke=True)
        self.assertEqual(overrun["status"], "FAIL")
        self.assertIn("the skipped-tail budget does not fit", overrun["statement"])
        # Nor are the attestation states.
        asserted = [dict(row) for row in rows]
        asserted[3]["attestation_state"] = "asserted"
        self.assertEqual(bench.verdict(asserted, SMOKE_PROTOCOL, smoke=True)["status"],
                         "FAIL")

    def test_the_archived_class_constant_is_the_one_the_ruling_cites(self):
        """The fidelity comparison is a CONSTANT, never read from the run it judges.

        A269 record 01 step 10: "v3.1 forward projection over the twelve
        fixtures at 447fd6bf: bounded {02, 05, 06, 08, 09, 11, 12}".  The
        ruled admissibility text names the same set, and the exhibit-E
        generator the cold gate read carries the same mapping independently.
        """

        self.assertEqual(sorted(bench.ARCHIVED_V31_BOUNDED), [2, 5, 6, 8, 9, 11, 12])
        self.assertIn("{02,05,06,08,09,11,12}", bench.RULED_ADMISSIBILITY_TEXT)
        self.assertEqual(bench.WORST_SKIPPED_TAIL_S, 2.3)
        self.assertEqual(bench.ADMISSIBLE_SLOT,
                         (("collector_exit", 0), ("cleanup_proven", True)))
        self.assertTrue((REPO_ROOT / RULING).is_file())
        # A caller may supply a different archived class; the comparison is a
        # pure function of the rows and that set.
        rows = faithful_rows()
        swapped = bench.fidelity(rows, frozenset({1, 3, 4, 7, 10}))
        self.assertEqual(swapped["admitting"], [2, 5, 6, 8, 9, 11, 12])
        self.assertEqual(swapped["refusing"], [1, 3, 4, 7, 10])
        self.assertEqual(swapped["tally"],
                         "0/12 match; admitting-direction 7; refusing-direction 5")


if __name__ == "__main__":
    unittest.main()
