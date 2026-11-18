"""Synthetic hand cases for RL-187. All record and trace values are invented."""

from dataclasses import dataclass, field, replace
from hashlib import sha256
import json
from math import sqrt
from types import SimpleNamespace
import unittest
from unittest.mock import Mock

from joulewise.cadence_looks import controls_analysis as analysis


NS = analysis.NS


@dataclass(frozen=True)
class Turn:
    index: int = 0
    start_ns: int = NS
    end_ns: int = 15 * NS
    first_token_ns: int = 2 * NS
    context_tokens: int = 1_000
    prefill_tokens: int = 3_000
    decode_tokens: int = 1_024
    hidden_tokens: int = 0
    logged: bool = True
    tool_calls: tuple = ()


@dataclass(frozen=True)
class Episode:
    episode_id: str = "invented"
    turns: tuple = (Turn(),)
    hardware: dict = field(default_factory=dict)
    start_ns: int = 0
    end_ns: int = 135 * NS


def call(start, first, end, *, kind="turn", requested=512, delivered=512):
    return dict(kind=kind, started_ns=start * NS, first_token_ns=first * NS, ended_ns=end * NS,
                complete=requested == delivered, requested_tokens=requested, actual_tokens=delivered,
                context_tokens=2000)


def interval(kind, start, end, *, complete=True):
    return dict(kind=kind, started_ns=start * NS, ended_ns=end * NS,
                complete=complete, requested_s=end - start)


def leg(episode, name, kind, steps):
    blob = json.dumps({"schema": "joulewise.cadence_script_work.v1", "leg_id": name,
                       "script": {"kind": kind}, "steps": steps}).encode()
    return analysis.LegInput(name, kind, True, True, episode, blob, sha256(blob).hexdigest())


def cpu_steps():
    return (call(1, 2, 3), interval("cpu", 3, 13), call(13, 14, 15), interval("recovery", 15, 135))


def calculate(kernel, *legs):
    supplied = {row.leg_id: row for row in legs}
    full = [supplied.get(leg_id, analysis.LegInput(leg_id, "plain", False, False))
            for leg_id in analysis.PILOT + analysis.REMAINDER]
    return analysis.print_controls(full, kernel=kernel,
                                   gap_limits_ns=dict.fromkeys(analysis.CHANNELS, 2 * NS),
                                   pooled=analysis.pool_hold_windows([], set()),
                                   instrument_manifest_sha256="a" * 64)


class TestControlsConventions(unittest.TestCase):
    def test_physical_call_view_and_work_evidence_refusals(self):
        steps = cpu_steps()
        episode = Episode()
        candidate = leg(episode, "L010", "cpu", steps)
        view = analysis.physical_call_view(candidate)
        self.assertEqual(view.episode, replace(episode, turns=view.episode.turns))
        self.assertEqual(tuple((t.start_ns, t.end_ns) for t in view.episode.turns),
                         ((NS, 3 * NS), (13 * NS, 15 * NS)))
        self.assertEqual(tuple(t.prefill_tokens for t in view.episode.turns), (2000, 2000))
        with self.assertRaisesRegex(analysis.ViewError, "^script_digest$"):
            analysis.physical_call_view(replace(candidate, work_bytes=candidate.work_bytes + b"\n"))
        with self.assertRaisesRegex(analysis.ViewError, "^step_order_or_episode_bounds$"):
            analysis.physical_call_view(replace(candidate, episode=replace(episode, end_ns=134 * NS)))

    def test_shared_envelope_stamps_gate_phase_code_and_qualifier(self):
        # PR #808 at 87b9b5df places the first visible call's two endpoint
        # stamps in both the authenticated work record and the logged envelope.
        steps = cpu_steps()
        first = steps[0]
        envelope = Turn(start_ns=first["started_ns"], first_token_ns=first["first_token_ns"])
        accepted = leg(Episode("invented-shared-stamps", (envelope,)), "L010", "cpu", steps)
        rejected = (
            leg(Episode("invented-start-mismatch", (replace(envelope, start_ns=envelope.start_ns + 1),)),
                "L003", "cpu", steps),
            leg(Episode("invented-first-token-mismatch", (replace(envelope, first_token_ns=envelope.first_token_ns + 1),)),
                "L004", "cpu", steps),
        )

        # Use spies so the routing assertions also run before the pinned phase
        # implementation reaches this checkout. The frozen phase tests below
        # cover the calculations on the same CPU step sequence.
        trace = SimpleNamespace(t_ns=tuple(seconds * NS for seconds in range(136)))
        other = tuple(SimpleNamespace(kind="gap", start_ns=start * NS, end_ns=end * NS)
                      for start, end in ((0, 1), (3, 13), (15, 135)))
        phases = SimpleNamespace(
            with_package=Mock(side_effect=lambda episode: episode),
            selected_trace=Mock(return_value=(trace, None)),
            phase_table=Mock(return_value={"phases": {}}),
            ControlLeg=lambda episode, dose: (episode, dose),
            qualify_ctl01=Mock(return_value={"qualified": "no"}),
            TIMING_EDGE_J=1.0,
        )
        kernel = analysis.PhaseKernel(
            phases, Mock(return_value=SimpleNamespace(segments=other)),
            Mock(return_value=SimpleNamespace(joules=0, flags=())),
        )

        result = calculate(kernel, *rejected, accepted)
        rows = {row["leg_id"]: row for row in result["legs"]}
        for rejected_leg in rejected:
            self.assertEqual(rows[rejected_leg.leg_id], {
                "leg_id": rejected_leg.leg_id, "kind": "cpu", "disposition": "not_evaluable",
                "reason": "envelope_stamps",
            })
        self.assertEqual(rows["L010"]["disposition"], "admitted")
        self.assertEqual(rows["L010"]["envelope"], envelope)

        phases.with_package.assert_called_once()
        view = phases.with_package.call_args.args[0]
        self.assertEqual(view.episode_id, accepted.episode.episode_id)
        self.assertEqual(tuple((turn.start_ns, turn.first_token_ns, turn.end_ns) for turn in view.turns),
                         ((NS, 2 * NS, 3 * NS), (13 * NS, 14 * NS, 15 * NS)))
        channels = tuple(analysis.TRACE_CHANNELS.values())
        self.assertEqual([(entry.args[0], entry.kwargs["source"], entry.kwargs["channel"])
                          for entry in kernel.attribute_episode.call_args_list],
                         [(view, source, channel) for source, channel in channels])
        self.assertEqual([entry.args[:2] for entry in phases.phase_table.call_args_list],
                         [(view, channel) for channel in channels])
        phases.qualify_ctl01.assert_called_once_with([(view, 10)])

    def test_dose_fit_six_legs_and_leave_one_out(self):
        points = {"L005": (128, 5), "L012": (128, 5), "L008": (256, 9),
                  "L011": (256, 9), "L002": (512, 17), "L009": (512, 17)}
        self.assertEqual(analysis.dose_fit(points), {"slope": 0.03125, "intercept": 1.0,
                         "range": (0.03125, 0.03125), "reason": None, "legs": tuple(points)})
        # Removing (3, 5) leaves y=x. Removing (3, 3) leaves covariance
        # numerator 26 and variance numerator 14 in the integer-sum formula.
        noisy = {"a": (1, 1), "b": (1, 1), "c": (2, 2), "d": (2, 2), "e": (3, 3), "f": (3, 5)}
        lo, hi = analysis.dose_fit(noisy)["range"]
        self.assertEqual(lo, 1)
        self.assertAlmostEqual(hi, 13 / 7)
        self.assertEqual(analysis.dose_fit({"a": (128, 5)})["reason"], "insufficient_legs")

    def test_floor_windows_pooling_and_no_cpu_substitution(self):
        first = ("f2-inst-01", "a" * 64, "L001")
        second = ("f2-inst-02", "b" * 64, "L001")
        rows = [analysis.HoldWindow(first, "gpu_rail", 40, 2, 2),
                analysis.HoldWindow(second, "gpu_rail", 40, 4, 4)]
        pooled = analysis.pool_hold_windows(rows, {first, second})
        self.assertEqual(pooled["gpu_rail", 40], (sqrt(13), ()))
        for seconds, expected in ((9.9, 10), (10, 10), (39.9, 10), (40, 40), (128, 128), (500, 128)):
            row = analysis.floor_units(40, seconds, "gpu_rail", pooled, "c" * 64)
            self.assertEqual(row["window_s"], expected)
            self.assertEqual(row["under_shortest_window"], seconds < 10)
        self.assertEqual(analysis.floor_units(40, 40, "gpu_rail", pooled, "c" * 64)["units"], 1 / sqrt(13))
        cpu = analysis.floor_units(40, 40, "cpu_rail", pooled, "c" * 64)
        self.assertEqual((cpu["units"], cpu["reason"]), (None, "no_matched_floor"))
        swap = replace(rows[0], member=(first[0], second[1], first[2]))
        with self.assertRaisesRegex(ValueError, "instrument_member"):
            analysis.pool_hold_windows([swap, rows[1]], {first, second})

    def test_instrument_exact_bytes_and_censored_parameters(self):
        manifest, hold, edges = b"manifest\n", b"hold\n", b"edges\n"
        pins = {f"{name}_sha256": sha256(payload).hexdigest()
                for name, payload in (("manifest", manifest), ("hold", hold), ("edges", edges))}
        analysis.validate_instrument_pins(manifest, hold, edges, **pins)
        with self.assertRaisesRegex(ValueError, "instrument_pin"):
            analysis.validate_instrument_pins(manifest, edges, hold, **pins)
        params = dict(gpu_token_floors=[130, 300, 900], dc_token_floors=[190, 260, 600],
                      return_bounds=[17, 45.5], decode_end_lags=[0.8, None], qualified_prefills=[256, 19458])
        self.assertEqual(analysis.read_parameters(**params), analysis.ReadParameters((512, 1024, 2048), 227.5, 46, 256))
        params.update(return_bounds=[None], qualified_prefills=[2000], dc_token_floors=[128])
        self.assertEqual(analysis.read_parameters(**params), analysis.ReadParameters((128, 256, 512), 600, 60, 2000))
        params.update(gpu_token_floors=[513], dc_token_floors=[514])
        with self.assertRaisesRegex(ValueError, "dose_requires_ruling"):
            analysis.read_parameters(**params)


class TestFrozenPhaseIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            cls.kernel = analysis.PhaseKernel.frozen()
        except ModuleNotFoundError as error:
            if error.name != "joulewise.align":
                raise
            raise unittest.SkipTest("RL-176 kernel awaits the integration base") from error

    def episode(self, envelope, end, *, cpu_watts=4, cpu_pulse=None):
        from joulewise.align.records import Episode, PowerTrace, Turn

        times = tuple(t * NS for t in range(end + 1))
        watts = tuple((cpu_pulse or {}).get(t, cpu_watts) for t in range(end + 1))
        traces = tuple(PowerTrace(source, channel, "toy", times, watts, "W", NS)
                       for source, channel in analysis.TRACE_CHANNELS.values())
        turn = Turn(**vars(envelope))
        return Episode("invented", "controls", "benign", "toy", "fake", 42, "toy", 0, end * NS,
                       (turn,), power_traces=traces)

    def test_cpu_burn_moves_from_decode_to_other(self):
        episode = self.episode(Turn(), 135)
        original = self.kernel.phases.phase_table(episode, self.kernel.phases.CPU)["phases"]
        result = calculate(self.kernel, leg(episode, "L010", "cpu", cpu_steps()))
        cpu = result["legs"][9]["channels"]["cpu_rail"]
        phases = cpu["absolute"]["phases"]
        self.assertEqual((original["decode"]["joules"], original["other"]["joules"]), (52, 484))
        self.assertEqual((phases["decode"]["joules"], phases["other"]["joules"]), (8, 524))
        self.assertEqual(cpu["other"]["cpu"]["joules"], 40)
        self.assertTrue(cpu["absolute"]["closes"])
        self.assertEqual(result["aligned_power"]["qualified"], "no")

    def test_hidden_baseline_and_short_print_stays_out_of_fit(self):
        envelope = Turn(start_ns=5 * NS, first_token_ns=6 * NS, end_ns=7 * NS,
                        prefill_tokens=2000, context_tokens=0, decode_tokens=1024)
        episode = self.episode(envelope, 127, cpu_watts=2, cpu_pulse={2: 6, 4: 10})
        tail = interval("recovery", 7, 127)
        visible = call(5, 6, 7, requested=1024, delivered=1024)
        full = call(1, 3, 5, kind="hidden", requested=128, delivered=128)
        short = call(1, 3, 5, kind="hidden", requested=128, delivered=64)
        rows = calculate(self.kernel, leg(episode, "L002", "hidden", (full, visible, tail)),
                         leg(episode, "L005", "hidden", (short, visible, tail)))
        self.assertEqual(len(rows["legs"]), 12)
        self.assertEqual(rows["dose_response"]["gpu_rail"]["legs"], ("L002",))
        self.assertEqual(rows["legs"][4]["delivery"], "short")
        for index, divisor in ((1, 128), (4, 64)):
            gpu = rows["legs"][index]["channels"]["gpu_rail"]
            hidden = gpu["hidden"]
            self.assertEqual((gpu["baseline_w"], hidden["call_j"], hidden["prefill_j"], hidden["decode_j"],
                              hidden["j_per_token"]), (2, 12, 4, 8, 8 / divisor))
        incomplete = leg(episode, "L002", "hidden", (full, visible, {**tail, "complete": False}))
        gpu = calculate(self.kernel, incomplete)["legs"][1]["channels"]["gpu_rail"]
        self.assertEqual((gpu["baseline_w"], gpu["baseline_reason"]), (None, "incomplete_recovery"))
        self.assertTrue(gpu["absolute"]["closes"])

    def test_frozen_absolute_closure_boundary(self):
        from joulewise.align.attribution import EnergyEstimate, EpisodeAttribution, SegmentEnergy

        phases = self.kernel.phases
        episode = self.episode(Turn(), 135)
        def estimate(joules):
            return EnergyEstimate(joules, 0, "toy", ())

        for amount, expected in ((99, True), (98.999, False)):
            segment = SegmentEnergy(None, "gap", 0, 135 * NS, estimate(amount))
            attrs = EpisodeAttribution(episode.episode_id, "cpu_power", estimate(100), (segment,), ())
            self.assertEqual(phases.phase_table(episode, phases.CPU, attrs)["closes"], expected)

    def test_burns_that_close_but_are_out_of_order(self):
        burns = {"L003": (30, 1), "L004": (90, 2), "L010": (10, 4)}
        legs = []
        for name in analysis.PILOT + analysis.REMAINDER:
            if name in burns:
                dose, watts = burns[name]
                envelope = Turn(end_ns=(dose + 5) * NS)
                steps = (call(1, 2, 3), interval("cpu", 3, 3 + dose),
                         call(3 + dose, 4 + dose, 5 + dose), interval("recovery", 5 + dose, 125 + dose))
                episode = self.episode(envelope, 125 + dose, cpu_watts=watts)
                kind = "cpu"
            else:
                envelope = Turn(end_ns=3 * NS, prefill_tokens=2000, context_tokens=0)
                steps = (call(1, 2, 3, requested=1024, delivered=1024), interval("recovery", 3, 123))
                episode = self.episode(envelope, 123)
                kind = "plain"
            legs.append(leg(replace(episode, episode_id="invented-" + name), name, kind, steps))
        qualifier = calculate(self.kernel, *legs)["aligned_power"]
        # CPU other energy at 10/30/90 s is 524/151/422 J.
        self.assertEqual(qualifier, {"qualified": "no", "all_legs_close": True, "cpu_burn_order": False})
