"""Failed-first acceptance for the revision 2 synthetic envelope projection."""

from dataclasses import replace
import unittest

from joulewise.cadence_looks import controls_analysis as analysis

from . import test_controls_analysis as fixture


class TestEnvelopeDisclosure(unittest.TestCase):
    def assert_refused(self, envelope):
        episode = fixture.Episode(turns=(envelope,))
        cpu = fixture.leg(episode, "L010", "cpu", fixture.cpu_steps())
        kernel = fixture.synthetic_cpu_kernel()
        result = fixture.calculate(kernel, cpu)
        row = result["legs"][9]
        self.assertEqual(row["disposition"], "not_evaluable")
        self.assertEqual(row, {
            "leg_id": "L010", "kind": "cpu", "disposition": "not_evaluable",
            "reason": "envelope_counts",
        })
        kernel.attribute_episode.assert_not_called()
        kernel.phases.phase_table.assert_not_called()
        kernel.phases.qualify_ctl01.assert_called_once_with([])

    def test_in_memory_hidden_token_reproductions_refuse(self):
        for value in (37, "detected", "K_outcome", "S_score"):
            with self.subTest(value=value):
                self.assert_refused(fixture.Turn(hidden_tokens=value))

    def test_envelope_counts_require_exact_integers(self):
        for fields in ({"hidden_tokens": False}, {"hidden_tokens": 0.0},
                       {"context_tokens": True, "prefill_tokens": 3999},
                       {"prefill_tokens": 3000.0}, {"decode_tokens": 1024.0}):
            with self.subTest(fields=fields):
                self.assert_refused(fixture.Turn(**fields))

    def test_accepted_envelope_is_a_closed_visible_count_projection(self):
        episode = fixture.Episode()
        cpu = fixture.leg(episode, "L010", "cpu", fixture.cpu_steps())
        row = fixture.calculate(fixture.synthetic_cpu_kernel(), cpu)["legs"][9]
        self.assertEqual(row["disposition"], "admitted")
        self.assertEqual(row["envelope"], {"prompt_tokens": 4000, "decode_tokens": 1024})

    def test_native_round_trip_hidden_token_reproduction_refuses(self):
        try:
            kernel = analysis.PhaseKernel.frozen()
        except ModuleNotFoundError as error:
            if error.name != "joulewise.align":
                raise
            self.skipTest("native record codec awaits the pinned kernel overlay")
        from joulewise.align.records import Episode, from_json, to_json

        episode = fixture.TestFrozenPhaseIntegration().episode(fixture.Turn(), 135)
        native = replace(episode, turns=(replace(episode.turns[0], hidden_tokens=37),))
        round_tripped = from_json(Episode, to_json(native))
        cpu = fixture.leg(round_tripped, "L010", "cpu", fixture.cpu_steps())
        row = fixture.calculate(kernel, cpu)["legs"][9]
        self.assertEqual(row["disposition"], "not_evaluable")
        self.assertEqual(row, {
            "leg_id": "L010", "kind": "cpu", "disposition": "not_evaluable",
            "reason": "envelope_counts",
        })
