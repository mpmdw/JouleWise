"""R0 host admission and power state are tested entirely through fake probes."""
from dataclasses import replace
import math
import os
import random
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from joulewise.align.apple import smc_enumeration as r0
from joulewise import prewindow
from joulewise.hazards import base, contention
from joulewise.measurement_liveness import Census
from joulewise.night_gate import ProbeResult
from scripts import align_smc_enumerate as cli
from tests.hazards.fakes import FakeClocks


class QuietTests(unittest.TestCase):
    def adaptive_capture(self, cooling, maximum, other=lambda t: 0.0):
        clock = FakeClocks(read_cost_ns=0)
        ctx = base.Context(clocks=clock)
        origin = clock.monotonic_ns()
        class Reader:
            def enumerate_sensors(self):
                return {'complete': True, 'errors': {}, 'keys': [
                    {'key': key, 'unit': 'degC', 'data_type': 'flt '} for key in ('TDIE', 'TGAT')]}
            def read(self, selected):
                t = (clock.monotonic_ns()-origin)/1e9
                return {'values': {key: cooling(t) if key == 'TDIE' else other(t) for key in selected}, 'errors': {}}
        quiet_times = []
        def quiet():
            quiet_times.append((clock.monotonic_ns()-origin)/1e9)
        load = mock.Mock()
        result = r0.collect(Reader(), seconds=60, idle_s=300, idle_max_s=maximum,
                            load_s=900, recovery_s=600, gpu_step=True,
                            quiet_check=quiet, ctx=ctx, sink=lambda row: None,
                            load_factory=lambda duration: load)
        return result, quiet_times, load

    def test_fable_f2_opus_f1_flicker_does_not_hold_idle_to_cap(self):
        # collect_fakes.py/d3_fakes.py: flat physical key plus SD~6 degC
        # flicker. A 7 degC sinusoid has SD~5; its slope is undecidable at
        # the D5 0.15 degC noise bar and it must not prolong the 300 s idle.
        result, _, _ = self.adaptive_capture(lambda t: 48+.03*math.sin(t/5), 1200,
                                             other=lambda t: 50+7*math.sin(t))
        idle = result['phases'][0]
        self.assertEqual(idle['actual_seconds'], 300)
        self.assertTrue(idle['settled'])
        self.assertEqual(idle['settle_keys'], 1)
        self.assertNotIn('TGAT', idle['baseline_slopes_c_min'])

    def test_empty_settle_set_is_indeterminate(self):
        result, _, _ = self.adaptive_capture(lambda t: 30.0, 1200)
        idle = result['phases'][0]
        self.assertEqual(idle['actual_seconds'], 300)
        self.assertIsNone(idle['settled'])
        self.assertEqual(idle['settle_keys'], 0)
        self.assertEqual(idle['settle_consecutive'], 0)

    def test_settle_set_keeps_stationary_noise_below_noise_limit(self):
        # .1*sin(1.7*t) has SD~.071 (<.15), but a one-second jump can
        # exceed .15, larger than half its .2 degC idle range (D1(b)).
        result, _, _ = self.adaptive_capture(lambda t: 48+.03*math.sin(t/5), 1200,
                                             other=lambda t: 50+.1*math.sin(1.7*t))
        idle = result['phases'][0]
        self.assertEqual(idle['actual_seconds'], 300)
        self.assertEqual(idle['settle_keys'], 2)
        self.assertIn('TGAT', idle['baseline_slopes_c_min'])

    def test_twenty_stationary_gaussian_keys_are_decidable(self):
        # Opus d3.py quiet:0.05:20 keys, seed 11, sigma .05 C (one third
        # of D3's .15 C noise limit). Half-range rejects stationary noise.
        rng = random.Random(11)
        keys = [f'TQ{i:02d}' for i in range(20)]
        class Reader:
            def enumerate_sensors(self):
                return {'complete': True, 'errors': {}, 'keys': [
                    {'key': k, 'unit': 'degC', 'data_type': 'flt '} for k in keys]}
            def read(self, selected):
                return {'values': {k: 40+i+rng.gauss(0, .05)
                                   for i, k in enumerate(selected)}, 'errors': {}}
        ctx = base.Context(clocks=FakeClocks(read_cost_ns=0))
        result = r0.collect(Reader(), seconds=60, idle_s=300, idle_max_s=1200,
                            load_s=1, recovery_s=1, gpu_step=True,
                            quiet_check=lambda: None, ctx=ctx, sink=lambda row: None,
                            load_factory=lambda duration: mock.Mock())
        idle = result['phases'][0]
        self.assertEqual(idle['settle_keys'], len(keys))
        self.assertTrue(idle['settled'])
        self.assertEqual(idle['actual_seconds'], 300)  # Default D3 minimum.

    def test_empty_set_needs_ten_consecutive_evaluations(self):
        original = r0._idle_stats
        def transient(points):
            t = points[-1][0] + 1  # Evaluation precedes the current tick's read.
            slope, noise = original(points)
            # Lose the sole decidable key at t=300..304, restore it for one
            # evaluation, then lose it at 306..315 (ten confirmations).
            return (slope, 1.0) if 300 <= t <= 304 or t >= 306 else (1.0, noise)
        with mock.patch.object(r0, '_idle_stats', side_effect=transient):
            result, _, _ = self.adaptive_capture(lambda t: 48+.03*math.sin(t/5), 1200)
        idle = result['phases'][0]
        self.assertEqual(idle['actual_seconds'], 315)
        self.assertEqual(idle['settle_empty_consecutive'], 10)
        self.assertIsNone(idle['settled'])

    def test_collector_records_deadline_before_exit_census_overrun(self):
        clock = FakeClocks(read_cost_ns=0)
        ctx = base.Context(clocks=clock)
        origin = clock.monotonic_ns()
        active = [None]
        class Reader:
            def enumerate_sensors(self):
                return {'complete': True, 'errors': {}, 'keys': [
                    {'key': 'TDIE', 'unit': 'degC', 'data_type': 'flt '}]}
            def read(self, selected):
                t = (clock.monotonic_ns()-origin)/1e9
                return {'values': {'TDIE': 48+.03*math.sin(t/5)}, 'errors': {}}
        load = mock.Mock()
        load.start.side_effect = lambda: active.__setitem__(0, clock.monotonic_ns())
        load.stop.side_effect = lambda: active.__setitem__(0, None)
        def quiet():
            if active[0] is not None and clock.monotonic_ns()-active[0] >= 5*r0.temperature.NS:
                clock.advance(2.6)
        # A 6 s fake load's final tick is t=5 s, the normal census cadence.
        # A 2.6 s census then ends at t=7.6: +1.6 s exit overrun, with all
        # six configured cells present. One recovery tick isolates this grid.
        data = r0.collect(Reader(), seconds=60, idle_s=300, idle_max_s=300,
                          load_s=6, recovery_s=1, gpu_step=True,
                          quiet_check=quiet, ctx=ctx, sink=lambda row: None,
                          load_factory=lambda duration: load)
        phase = data['phases'][1]
        # Exact arithmetic on the same synthetic clock; allow float noise only.
        self.assertAlmostEqual(phase['actual_seconds'], 7.6, places=9)
        self.assertEqual(phase['deadline_s']-phase['start_s'], 6)
        row = r0.rank(data)['ranking'][0]
        self.assertEqual(row['phase_max_empty_cells']['load'], 0)
        self.assertEqual(row['phase_coverage']['load'], 1)

    def test_settle_set_checks_noise_even_when_idle_jumps_are_resolved(self):
        # A smooth 7*sin(t/10) oscillation has residual noise >>.15, but
        # one-second jumps <=.7 are well below half its 14 degC idle range.
        result, _, _ = self.adaptive_capture(lambda t: 48+.03*math.sin(t/5), 1200,
                                             other=lambda t: 50+7*math.sin(t/10))
        idle = result['phases'][0]
        self.assertEqual(idle['actual_seconds'], 300)
        self.assertEqual(idle['settle_keys'], 1)
        self.assertNotIn('TGAT', idle['baseline_slopes_c_min'])

    def test_adaptive_idle_extends_until_ten_settled_evaluations(self):
        # Cooling at -1 degC/min until t=330, then flat with small noise.
        # The trailing 60 s slope cannot settle at the minimum t=300.
        result, quiet_times, load = self.adaptive_capture(
            lambda t: 40-min(t, 330)/60+.005*math.sin(t), 1200)
        idle = result['phases'][0]
        self.assertTrue(idle['settled'])
        self.assertGreater(idle['actual_seconds'], 300)
        # The final all-flat window ends at 390, then ten successes need
        # at most nine more evaluations: conservative upper bound 400 s.
        self.assertLessEqual(idle['actual_seconds'], 400)
        self.assertGreaterEqual(idle['settle_consecutive'], 10)  # D3's ten consecutive 1 s tests.
        self.assertNotIn('TGAT', idle['baseline_slopes_c_min'])
        self.assertLessEqual(abs(idle['baseline_slopes_c_min']['TDIE']), .2)  # G0 slope bar.
        # The retained 5 s census bounds consecutive probes throughout capture.
        self.assertLessEqual(max(b-a for a, b in zip(quiet_times, quiet_times[1:])), 5)
        load.start.assert_called_once()
        load.stop.assert_called_once()

    def test_adaptive_idle_cap_proceeds_with_per_key_unsettled_flag(self):
        result, _, _ = self.adaptive_capture(lambda t: 50-t/60+.005*math.sin(t), 360)
        idle = result['phases'][0]
        # 360 is a test cap one trailing window beyond the 300 s minimum.
        self.assertEqual(idle['actual_seconds'], 360)
        self.assertFalse(idle['settled'])
        row = next(r for r in r0.rank(result)['ranking'] if r['key'] == 'TDIE')
        self.assertTrue(row['baseline_unsettled'])
        # The analytic slope is -1 degC/min; .005 degC noise contributes <.01.
        self.assertAlmostEqual(row['baseline_slope_c_min'], -1, delta=.01)

    def inputs(self, parent, result):
        return {"agent_probe": lambda: (ProbeResult(("fake",), 1, "", "", 0), None),
                "measurement_probe": lambda: Census(), "custody_parents": [parent],
                "contention_probe": lambda: result,
                "process_probe": lambda: SimpleNamespace(returncode=0, stderr="", stdout="1 launchd\n")}

    def test_measured_outside_job_and_missing_host_counter_refuse(self):
        with tempfile.TemporaryDirectory() as tmp:
            # 0.06 = 0.05 + 0.01 is measured per-process contention;
            # an unread host counter remains an instrument error.
            for result in ({"clean": False, "error": None, "max_outside": {"cpu_s_per_s": .06}},
                           {"clean": None, "error": "host CPU unread"}):
                with self.subTest(result=result), self.assertRaises(r0.NotQuiet):
                    r0.require_quiet(**self.inputs(Path(tmp), result))

    def test_missing_custody_parent_refuses_even_when_census_is_clear(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(r0.NotQuiet, "custody parent"):
                r0.require_quiet(**self.inputs(Path(tmp)/"missing", {"clean": True, "error": None}))

    def test_contention_uses_host_delta_and_excludes_only_own_tree(self):
        clock = FakeClocks(read_cost_ns=0)
        ctx = base.Context(clocks=clock)
        own = os.getpid()
        def make_probe(outside):
            start = clock.monotonic_ns()
            def snapshot():
                stamp = ctx.stamp()
                elapsed = (stamp.monotonic_ns - start) / 1e9
                rows = {}
                # Tree rates are 4 * 0.05 and 8 * 0.05; both must be
                # excluded. Outside .2 = 4 * 0.05 must still refuse.
                for pid, parent, rate in ((own, 1, .2), (987654, own, .4), (123456, 1, outside)):
                    rows[(pid, "start")] = {"pid": pid, "ppid": parent, "start_identity": "start",
                        "start_epoch_s": 0, "command": "python", "cumulative_cpu_seconds": elapsed*rate}
                hz = os.sysconf("SC_CLK_TCK")
                # .6 = .2 + .4 tree CPU; one core of idle ticks.
                host = [[round(elapsed*(.6+outside)*hz), 0, round(elapsed*hz), 0]]
                return contention.Snapshot(stamp, stamp, rows, None, host=host)
            return r0.CpuQuietProbe(ctx=ctx, snapshot=snapshot)
        with mock.patch.object(r0, "time", wraps=r0.time):
            clean = make_probe(0)()
            dirty = make_probe(.2)()
        self.assertTrue(clean["clean"])
        # Host ticks and TIME each resolve 0.01 CPU-s on this Mac.
        self.assertAlmostEqual(clean["outside_aggregate_cpu_s_per_s"], 0,
                               delta=contention.PS_TIME_QUANTUM_S / prewindow.INTERVAL_S)
        self.assertFalse(dirty["clean"])
        self.assertGreater(dirty["outside_aggregate_cpu_s_per_s"], .05)

    def test_metadata_records_raw_power_modes_ac_and_os_thermal_level(self):
        outputs = {("/usr/sbin/sysctl", "-n", "hw.model"): "MacFAKE\n",
                   ("/usr/sbin/sysctl", "-n", "hw.memsize"): "1000\n",
                   ("/usr/bin/pmset", "-g"): " lowpowermode 0\n highpowermode 1\n powermode 2\n",
                   ("/usr/bin/pmset", "-g", "custom"): " highpowermode 1\n",
                   ("/usr/bin/pmset", "-g", "batt"): "Now drawing from 'AC Power'\n"}
        def probe(argv):
            return SimpleNamespace(returncode=0, stdout=outputs[tuple(argv)], stderr="")
        reader = mock.Mock()
        reader.read.return_value = 0
        metadata = cli.host_metadata(probe=probe, thermal_reader_factory=lambda: reader)
        self.assertTrue(metadata["ac_power"])
        self.assertEqual(metadata["power_mode"], {"lowpowermode": 0, "highpowermode": 1, "powermode": 2})
        self.assertEqual(metadata["os_thermal_level"], 0)
        self.assertEqual(metadata["pmset_g"]["stdout"], outputs[("/usr/bin/pmset", "-g")])
        reader.close.assert_called_once()

    def test_unavailable_power_or_thermal_probe_is_explicitly_unknown(self):
        def missing(_argv):
            raise OSError("synthetic unavailable")
        metadata = cli.host_metadata(probe=missing, thermal_reader_factory=mock.Mock(side_effect=OSError("gone")))
        self.assertIsNone(metadata["ac_power"])
        self.assertIsNone(metadata["os_thermal_level"])
        self.assertIn("gone", metadata["os_thermal_error"])
        self.assertIn("unavailable", metadata["pmset_g"]["error"])
        self.assertTrue(all(v is None for v in metadata["power_mode"].values()))

class CpuQuietProbeTests(unittest.TestCase):
    def make_probe(self, processes, host_cpu, *, host_error=None):
        """Counters and host CPU are cumulative functions of simulated seconds."""
        clock = FakeClocks(read_cost_ns=0)
        ctx = base.Context(clocks=clock)
        start = clock.monotonic_ns()
        wall = ctx.stamp().wall_ns / 1e9
        snapshots = []
        def snapshot():
            stamp = ctx.stamp()
            elapsed = (stamp.monotonic_ns - start) / 1e9
            # Root predates the interval by 30 s; synthetic identities need
            # no ps rounding. TIME counters below use 0.01 s quanta.
            entries = [(os.getpid(), 1, -prewindow.INTERVAL_S, 0, "probe"), *processes(elapsed)]
            rows = {}
            for pid, parent, born, cpu, name in entries:
                identity = (pid, f"birth:{born}")
                rows[identity] = {"pid": pid, "ppid": parent, "start_identity": identity[1],
                                  "start_epoch_s": wall + born, "command": name,
                                  "cumulative_cpu_seconds": cpu}
            hz = os.sysconf("SC_CLK_TCK")
            # Host CPU ticks measure busy work plus one core of idle time.
            host = [[round(host_cpu(elapsed) * hz), 0, round(elapsed * hz), 0]]
            sample = contention.Snapshot(stamp, stamp, rows, None, host=None if host_error else host,
                                         host_error=host_error)
            snapshots.append(sample)
            return sample
        return r0.CpuQuietProbe(ctx=ctx, snapshot=snapshot), clock, snapshots

    def test_per_process_bar_on_both_sides_and_first_admission_wait(self):
        # (0.05 +/- 0.01) * 30 gives 1.80 / 1.20 CPU-s. One TIME
        # quantum / 30 bounds rate rounding without moving the bar.
        for rate, clean in ((.06, False), (.04, True)):
            with self.subTest(rate=rate):
                probe, clock, snapshots = self.make_probe(
                    lambda t: [(42, 1, -prewindow.INTERVAL_S, t * rate, "outside")],
                    lambda t: t * rate)
                result = probe()
                self.assertIs(result["clean"], clean)
                self.assertIsNone(result["error"])
                self.assertEqual(clock.sleeps, [prewindow.INTERVAL_S])
                self.assertEqual(len(snapshots), 2)
                self.assertGreaterEqual(result["elapsed_s"], prewindow.INTERVAL_S)
                self.assertAlmostEqual(result["max_outside"]["cpu_s_per_s"], rate,
                                       delta=contention.PS_TIME_QUANTUM_S / prewindow.INTERVAL_S)

    def test_aggregate_is_flagged_and_not_judged(self):
        # Five processes each use 0.05 - 0.01 = 0.04. Their aggregate
        # is 5 * 0.04 = 0.2, with no per-process hazard over 30 s.
        probe, _, _ = self.make_probe(
            lambda t: [(pid, 1, -prewindow.INTERVAL_S, t * .04, "outside")
                       for pid in range(42, 47)], lambda t: t * .2)
        result = probe()
        self.assertTrue(result["clean"])
        self.assertTrue(result["aggregate_above_0_05"])
        self.assertIsNone(result["aggregate_cpu_limit_s_per_s"])
        self.assertIsNone(result["aggregate_limit_s_per_s"])
        self.assertFalse(result["aggregate_over_limit"])
        self.assertAlmostEqual(result["outside_aggregate_cpu_s_per_s"], .2,
                               delta=contention.PS_TIME_QUANTUM_S / prewindow.INTERVAL_S)
        # Exercise the admission wrapper too: this aggregate must pass.
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(r0.require_quiet(**QuietTests().inputs(Path(tmp), result))["contention"], result)

    def test_run4_replay_embeds_short_burst_in_full_interval(self):
        # Run 4: two mdworkers born 0.6 s = 60 TIME quanta before the
        # close, with .12 / .09 CPU-s = 12 / 9 quanta total. The host
        # uses .25 = 5 * .05 for the last 1.18 s = 118 TIME quanta,
        # otherwise .04 = .05 - .01 throughout the 30 s interval.
        short = 118 * contention.PS_TIME_QUANTUM_S
        born = prewindow.INTERVAL_S - 60 * contention.PS_TIME_QUANTUM_S
        def processes(t):
            background = [(42, 1, -prewindow.INTERVAL_S, t * .04, "background")]
            return background + ([(43, 1, born, .12, "mdworker_shared"),
                                  (44, 1, born, .09, "mdworker_shared")] if t >= born else [])
        def host_cpu(t):
            before_burst = prewindow.INTERVAL_S - short
            return min(t, before_burst) * .04 + max(0, t - before_burst) * .25
        probe, _, _ = self.make_probe(processes, host_cpu)
        result = probe()
        self.assertTrue(result["clean"])
        self.assertIsNone(result["error"])
        rates = {row["pid"]: row["cpu_s_per_s"] for row in result["outside_listed"]}
        # .12 / 30 and .09 / 30 are below the .005 reporting floor;
        # they are still counted in outside_total, proving birth accounting.
        self.assertNotIn(43, rates)
        self.assertNotIn(44, rates)
        self.assertAlmostEqual(result["outside_total_cpu_s_per_s"], .04 + (.12 + .09) / prewindow.INTERVAL_S,
                               delta=contention.PS_TIME_QUANTUM_S / prewindow.INTERVAL_S)
        expected_aggregate = (.04 * (prewindow.INTERVAL_S - short) + .25 * short) / prewindow.INTERVAL_S
        self.assertAlmostEqual(result["outside_aggregate_cpu_s_per_s"], expected_aggregate,
                               delta=contention.PS_TIME_QUANTUM_S / prewindow.INTERVAL_S)
        self.assertFalse(result["aggregate_above_0_05"])

    def test_short_calls_choose_newest_eligible_opening_and_bound_history(self):
        # Calls at 30 + 10 TIME quanta, 1.5 * 30, and 2 * 30 +
        # 20 TIME quanta must use openings 0, 0, and 30.1 respectively.
        probe, clock, _ = self.make_probe(
            lambda t: [(42, 1, -prewindow.INTERVAL_S, t * .04, "outside")], lambda t: t * .04)
        first = probe()
        start = first["interval"]["monotonic_ns"][0]
        clock.advance(10 * contention.PS_TIME_QUANTUM_S)
        self.assertEqual(probe()["interval"]["monotonic_ns"][0], start)
        clock.advance(prewindow.INTERVAL_S / 2 - 10 * contention.PS_TIME_QUANTUM_S)
        probe()
        clock.advance(prewindow.INTERVAL_S / 2 + 20 * contention.PS_TIME_QUANTUM_S)
        result = probe()
        self.assertEqual(result["interval"]["monotonic_ns"][0],
                         start + int((prewindow.INTERVAL_S + 10 * contention.PS_TIME_QUANTUM_S) * 1e9))
        self.assertGreaterEqual(result["elapsed_s"], prewindow.INTERVAL_S)
        self.assertEqual(len(probe._snapshots), 3)
        self.assertEqual(clock.sleeps, [prewindow.INTERVAL_S])

    def test_gap_contender_is_detected_on_first_wholly_post_gap_window(self):
        # Gap 20 * 30 = 600 s. Recent contention uses 10 * .05 = .5
        # for its last 30 s, then continues. At the 30 / 6 = 5 s cadence,
        # the sixth call after the gap call (t=660) first judges a wholly
        # post-gap 30 s window, 630 -> 660. Earlier diluted rates stay < .05.
        dwell = prewindow.INTERVAL_S
        end = 21 * dwell
        def cpu(t):
            return max(0, t - (end - dwell)) * .5
        probe, clock, _ = self.make_probe(
            lambda t: [(42, 1, -dwell, cpu(t), "outside")], cpu)
        self.assertTrue(probe()["clean"])
        with mock.patch.object(clock, "sleep", side_effect=AssertionError("slept after first admission")):
            clock.advance(20 * dwell)
            result = probe()
            gap_end = result["interval"]["monotonic_ns"][1]
            self.assertTrue(result["clean"])
            self.assertTrue(result["long_interval"])
            self.assertEqual(result["elapsed_s"], 20 * dwell)
            self.assertAlmostEqual(result["max_outside"]["cpu_s_per_s"], .5 / 20,
                                   delta=contention.PS_TIME_QUANTUM_S / (20 * dwell))
            for call in range(1, 7):
                clock.advance(dwell / 6)
                result = probe()
                self.assertIs(result["clean"], call < 6)
            self.assertEqual(result["interval"]["monotonic_ns"][0], gap_end)
            self.assertEqual(result["elapsed_s"], dwell)
            self.assertAlmostEqual(result["max_outside"]["cpu_s_per_s"], .5,
                                   delta=contention.PS_TIME_QUANTUM_S / dwell)
        self.assertEqual(clock.sleeps, [dwell])
        self.assertEqual(len(probe._snapshots), 7)  # Opening plus six 5 s calls in 30 s.

    def test_gap_contention_refuses_on_the_long_judged_interval(self):
        # (0.05 + 0.01) * (20 * 30) = 36 CPU-s over the gap itself.
        dwell = prewindow.INTERVAL_S
        def cpu(t):
            return max(0, t - dwell) * .06
        probe, clock, _ = self.make_probe(
            lambda t: [(42, 1, -dwell, cpu(t), "outside")], cpu)
        self.assertTrue(probe()["clean"])
        with mock.patch.object(clock, "sleep", side_effect=AssertionError("slept after first admission")):
            clock.advance(20 * dwell)
            result = probe()
        self.assertFalse(result["clean"])
        self.assertTrue(result["long_interval"])
        self.assertEqual(result["elapsed_s"], 20 * dwell)

    def test_no_sleep_after_first_admission_at_cadence_or_after_gaps(self):
        dwell = prewindow.INTERVAL_S
        # Cadence = 30 / 6 = 5 s; gaps = 20 * 30 and 30 + 100 TIME
        # quanta (600 and 31 s). Follow both gaps with another full cadence.
        steps = (dwell / 6,) * 6 + (20 * dwell, dwell + 100 * contention.PS_TIME_QUANTUM_S) + (dwell / 6,) * 6
        probe, clock, _ = self.make_probe(lambda t: [], lambda t: 0)
        self.assertTrue(probe()["clean"])
        self.assertEqual(clock.sleeps, [dwell])
        with mock.patch.object(clock, "sleep", side_effect=AssertionError("slept after first admission")):
            for step in steps:
                clock.advance(step)
                result = probe()
                self.assertTrue(result["clean"])
                self.assertGreaterEqual(result["elapsed_s"], dwell)
        self.assertLessEqual(len(probe._snapshots), 7)  # 30 / 5 intervals plus their opening.

    def test_zombie_counter_is_disclosed_and_other_processes_still_judged(self):
        # 500 TIME quanta -> zero for the zombie. Another process uses
        # .05 +/- .01 over 30 s, so the regression cannot mask contention.
        for rate, clean in ((.04, True), (.06, False)):
            with self.subTest(rate=rate):
                probe, _, _ = self.make_probe(
                    lambda t: [(42, 1, -prewindow.INTERVAL_S, 5 if t == 0 else 0, "zombie"),
                               (43, 1, -prewindow.INTERVAL_S, t * rate, "outside")], lambda t: t * rate)
                result = probe()
                self.assertIs(result["clean"], clean)
                self.assertIsNone(result["error"])
                self.assertEqual([row["pid"] for row in result["regressed_counters"]], [42])
                self.assertFalse(result["regressed_counters"][0]["contaminant"])

    def test_zombie_regressions_without_prior_over_limit_are_disclosed_for_every_process(self):
        # TIME 3.00 = 300 quanta -> zero, with no prior judged over-limit
        # interval. Contaminant status is disclosed but does not change this rule.
        for name, contaminant in (("mdworker_shared", True), ("Safari", False)):
            with self.subTest(name=name):
                probe, _, _ = self.make_probe(
                    lambda t: [(42, 1, -prewindow.INTERVAL_S, 3 if t == 0 else 0, name)], lambda t: 0)
                result = probe()
                self.assertTrue(result["clean"])
                self.assertIsNone(result["error"])
                self.assertEqual([(row["pid"], row["contaminant"]) for row in result["regressed_counters"]],
                                 [(42, contaminant)])

    def test_failed_snapshot_and_host_ticks_remain_errors(self):
        # A full 30 s baseline cannot make failed instruments clean.
        probe, _, _ = self.make_probe(lambda t: [], lambda t: 0, host_error="host unavailable")
        self.assertIn("host unavailable", probe()["error"])
        for error in ("ps failed", "ps output unparsable"):
            with self.subTest(error=error):
                probe, _, _ = self.make_probe(lambda t: [], lambda t: 0)
                snapshot = probe.snapshot
                def failed():
                    return replace(snapshot(), error=error)
                probe.snapshot = failed
                result = probe()
                self.assertIsNone(result["clean"])
                self.assertEqual(result["error"], error)
                self.assertFalse(probe._snapshots)
                self.assertIsNone(probe.previous)

    def test_failed_startup_closing_snapshot_never_becomes_a_future_opening(self):
        # Fail the closing read at 30 s, then supervise every 30 / 6 = 5 s
        # through 2 * 30. The failed snapshot would resurface at t=60 if kept.
        dwell = prewindow.INTERVAL_S
        probe, clock, snapshots = self.make_probe(lambda t: [], lambda t: 0)
        original = probe.snapshot
        def transient_failure():
            sample = original()
            return replace(sample, error="transient ps failure") if len(snapshots) == 2 else sample
        probe.snapshot = transient_failure
        self.assertEqual(probe()["error"], "transient ps failure")
        self.assertEqual(len(probe._snapshots), 1)
        with mock.patch.object(clock, "sleep", side_effect=AssertionError("retained opening already exists")):
            for _ in range(6):
                clock.advance(dwell / 6)
                result = probe()
                self.assertTrue(result["clean"])
                self.assertIsNone(result["error"])
                self.assertTrue(all(not sample.error for sample in probe._snapshots))

    def test_previous_over_limit_exit_and_regression_evidence_is_preserved(self):
        # .06 = .05 + .01 over the first 30 s. Existing previous_over
        # evidence must still refuse a subsequent exit or zombie regression.
        for exited in (True, False):
            with self.subTest(exited=exited):
                def processes(t):
                    if t > prewindow.INTERVAL_S:
                        return [] if exited else [(42, 1, -prewindow.INTERVAL_S, 0, "outside")]
                    return [(42, 1, -prewindow.INTERVAL_S, .06 * t, "outside")]
                probe, clock, _ = self.make_probe(processes, lambda t: t * .06)
                self.assertFalse(probe()["clean"])
                clock.advance(prewindow.INTERVAL_S)
                result = probe()
                self.assertFalse(result["clean"])
                self.assertIsNone(result["error"])
                self.assertEqual(result["exited_over_limit"][0]["pid"], 42)
                if not exited:
                    self.assertFalse(result["regressed_counters"][0]["contaminant"])

    def test_reused_root_pid_does_not_exempt_replacement(self):
        # Replacement is born one TIME quantum into the 30 s interval
        # and uses (.05 + .01) * 30 = 1.80 CPU-s. Pin the original root.
        probe, _, snapshots = self.make_probe(lambda t: [], lambda t: t * .06)
        original = probe.snapshot
        def reused():
            sample = original()
            if len(snapshots) == 1:
                return sample
            old_identity = next(iter(sample.rows))
            row = {**sample.rows[old_identity], "start_identity": "replacement",
                   "start_epoch_s": snapshots[0].started.wall_ns / 1e9 + contention.PS_TIME_QUANTUM_S,
                   "cumulative_cpu_seconds": .06 * prewindow.INTERVAL_S}
            return replace(sample, rows={(os.getpid(), "replacement"): row})
        probe.snapshot = reused
        result = probe()
        self.assertFalse(result["clean"])
        self.assertEqual(result["outside_over_limit"][0]["pid"], os.getpid())
        self.assertNotEqual(probe.root_identities[os.getpid()][1], "replacement")

    def test_host_tick_error_remains_an_error_without_aggregate_limit(self):
        # A changed logical CPU count is an error from host_ticks_delta,
        # even over the full 30 s baseline and with no aggregate limit.
        probe, _, snapshots = self.make_probe(lambda t: [], lambda t: 0)
        original = probe.snapshot
        def changed_count():
            sample = original()
            host = [[0, 0, 0, 0]] if len(snapshots) == 1 else [[0, 0, 0, 0], [0, 0, 0, 0]]
            return replace(sample, host=host)
        probe.snapshot = changed_count
        result = probe()
        self.assertIsNone(result["clean"])
        self.assertIn("logical CPU count changed", result["error"])


def r0l3_interval(start_s, end_s, cores, *, over=(), processes=None, aggregate=None, kernel=None):
    """One CpuQuietProbe-shaped interval.

    ``cores`` is one outside process (pid 777 busyd) unless ``processes``
    lists (pid, command, rate) rows; ``aggregate`` defaults to their sum.
    """
    rows = [(777, "busyd", cores)] if processes is None else list(processes)
    rows += [(pid, name, rate) for pid, name, rate in over if pid not in {r[0] for r in rows}]
    listed = [{"pid": pid, "command": name, "start": "s", "cpu_s_per_s": rate} for pid, name, rate in rows]
    return {"contention": {"interval": {"monotonic_ns": [round(start_s * 1e9), round(end_s * 1e9)]},
                           "elapsed_s": end_s - start_s,
                           "outside_aggregate_cpu_s_per_s": sum(r[2] for r in rows) if aggregate is None else aggregate,
                           "kernel_task_cpu_s_per_s": kernel, "outside_listed": listed,
                           "clean": not over, "error": None,
                           "outside_over_limit": [{"pid": pid, "command": name, "cpu_s_per_s": rate}
                                                  for pid, name, rate in over]}}


def r0l3_census(intervals):
    results = iter(intervals)
    return lambda: next(results)


class R0L3ContentionTests(unittest.TestCase):
    # Ruling 8 (R1): 0.5 cores sustained 60 s. CpuQuietProbe judges >= 30 s
    # windows at the capture's 5 s census cadence, so ends step by 5 s.
    def windows(self, first_end, last_end, cores, **kwargs):
        return [r0l3_interval(end - 30, end, cores, **kwargs) for end in range(first_end, last_end + 1, 5)]

    def test_sustained_half_core_for_60_s_redoes_once_then_flags(self):
        # Windows ending 30..60 s cover [0, 60]: 60 s at >= 0.5 cores.
        sustained = self.windows(30, 60, 0.5)
        quiet = r0.Ruling8Quiet("redo", census=r0l3_census(sustained))
        for _ in sustained[:-1]:
            quiet()
        with self.assertRaises(r0.ContentionRedo) as caught:
            quiet()
        self.assertEqual(caught.exception.summary["episodes"][0]["seconds"], 60)
        self.assertFalse(caught.exception.summary["contended"])
        # The redo capture: an episode extended to 90 s, a light window,
        # then a second episode over [40, 100]. Neither aborts; both are kept.
        redo = (self.windows(30, 90, 0.7) + [r0l3_interval(35, 65, 0.0)]
                + self.windows(70, 100, 0.6))
        flagged = r0.Ruling8Quiet("flag", census=r0l3_census(redo))
        for _ in redo:
            flagged()
        summary = flagged.summary()
        self.assertTrue(summary["contended"])
        self.assertEqual([e["seconds"] for e in summary["episodes"]], [90, 60])
        self.assertEqual(len(summary["flags"]), len(redo) - 1)  # the 0.0 window is clean

    def test_shorter_or_lower_contention_is_flagged_never_redone(self):
        cases = {
            # 55 s at 0.5 cores: one 5 s cadence short of ruling 8.
            "55 s at 0.5": self.windows(30, 55, 0.5),
            # Re-run 8: frauddefensed 0.092 CPU-s/s for 30-60 s, aggregate well below 0.5.
            "frauddefensed": self.windows(30, 60, 0.05, over=[(61967, "frauddefensed", 0.092)],
                                          processes=[(61967, "frauddefensed", 0.092), (88, "WindowServer", 0.05)]),
            # 0.49 cores for 10 min, no process over 0.05.
            "0.49 for 600 s": self.windows(30, 600, 0.49),
        }
        for name, intervals in cases.items():
            with self.subTest(name):
                quiet = r0.Ruling8Quiet("redo", census=r0l3_census(intervals))
                for _ in intervals:
                    quiet()
                summary = quiet.summary()
                self.assertEqual(summary["episodes"], [])
                self.assertFalse(summary["contended"])
        frauddefensed = r0.Ruling8Quiet("redo", census=r0l3_census(cases["frauddefensed"]))
        for _ in cases["frauddefensed"]:
            frauddefensed()
        flags = frauddefensed.summary()["flags"]
        self.assertEqual(len(flags), len(cases["frauddefensed"]))
        self.assertEqual(flags[0]["over_0_05"][0]["command"], "frauddefensed")
        self.assertFalse(flags[0]["heavy"])

    def test_follow_up_ruling_1_judges_largest_single_process_not_aggregate_or_kernel_task(self):
        # Ten processes at 0.2 each: aggregate 2.0 cores, no single one >= 0.5.
        spread = [(100 + i, f"worker{i}", 0.2) for i in range(10)]
        # kernel_task (pid 0) at 0.9 cores, driven by our own GPU load step.
        kernel_rows = [(0, "kernel_task", 0.9), (88, "WindowServer", 0.1)]
        cases = {
            "aggregate only": (self.windows(30, 120, 0, processes=spread), False),
            "kernel_task": (self.windows(30, 120, 0, processes=kernel_rows, kernel=0.9), False),
            "single process": (self.windows(30, 60, 0.5), True),
        }
        for name, (intervals, redo) in cases.items():
            with self.subTest(name):
                quiet = r0.Ruling8Quiet("redo", census=r0l3_census(intervals))
                if redo:
                    for _ in intervals[:-1]:
                        quiet()
                    with self.assertRaises(r0.ContentionRedo) as caught:
                        quiet()
                    self.assertEqual(caught.exception.summary["episodes"][0]["processes"],
                                     [{"pid": 777, "command": "busyd"}])
                    continue
                for _ in intervals:
                    quiet()
                summary = quiet.summary()
                self.assertEqual(summary["episodes"], [])
                # Recorded, never judged.
                self.assertTrue(summary["flags"])
                self.assertFalse(any(f["heavy"] for f in summary["flags"]))
                if name == "aggregate only":
                    self.assertAlmostEqual(summary["flags"][0]["outside_aggregate_cpu_s_per_s"], 2.0)
                    self.assertEqual(summary["flags"][0]["largest_process_cores"], 0.2)
                else:
                    self.assertEqual(summary["flags"][0]["kernel_task_cpu_s_per_s"], 0.9)
                    self.assertEqual(summary["flags"][0]["largest_process"]["command"], "WindowServer")

    def test_a_light_interval_breaks_the_sustained_run(self):
        intervals = (self.windows(30, 50, 0.6) + [r0l3_interval(25, 55, 0.1)]
                     + self.windows(60, 85, 0.6))  # second run covers [30, 85]: 55 s
        quiet = r0.Ruling8Quiet("redo", census=r0l3_census(intervals))
        for _ in intervals:
            quiet()
        self.assertEqual(quiet.summary()["episodes"], [])

    def test_census_refusals_still_refuse_under_r0l3(self):
        def refused():
            raise r0.NotQuiet("measurement process active: 99 run_night.py")
        for policy in ("redo", "flag"):
            with self.subTest(policy), self.assertRaisesRegex(r0.NotQuiet, "run_night"):
                r0.Ruling8Quiet(policy, census=refused)()
        with self.assertRaises(ValueError):
            r0.Ruling8Quiet("refuse")

    def test_require_quiet_records_contention_but_refuses_unmeasured_cpu(self):
        with tempfile.TemporaryDirectory() as tmp:
            dirty = {"clean": False, "error": None, "max_outside": {"cpu_s_per_s": .06}}
            inputs = QuietTests().inputs(Path(tmp), dirty)
            self.assertIs(r0.require_quiet(**inputs, record_contention=True)["contention"], dirty)
            with self.assertRaises(r0.NotQuiet):
                r0.require_quiet(**inputs)  # the default (non-R0) census is unchanged
            unread = QuietTests().inputs(Path(tmp), {"clean": None, "error": "host CPU unread"})
            with self.assertRaisesRegex(r0.NotQuiet, "host CPU unread"):
                r0.require_quiet(**unread, record_contention=True)
