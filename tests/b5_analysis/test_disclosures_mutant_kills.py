"""Public disclosure outputs on fabricated journals and member records."""
import json
import unittest

from joulewise.b5_analysis import disclosures as d
from tests.b5_analysis.test_disclosures import Harness


def journal(*rows):
    return b"\n".join(d.canonical_json_bytes(row) for row in rows)


def window_line(record, name):
    return next(row for row in record["window_lines"]["alpha"] if row["line"] == name)


def request_harness(*, epoch_events=False):
    h = Harness()
    archive = h.archives["alpha"]
    for row, (lo, hi) in zip(h.rows[:2], ((1, 2), (3, 4))):
        run = row["member"]["bundle_id"]
        archive.sources[f"sources/claim-runs/{run}/metadata.json"] = d.canonical_json_bytes({
            "uncertainty_evidence": {"clock_anchor": {"status": "bounded",
                "effective_clock_anchor_bound_s": .04, "clock_stamps": {
                    "sampling_started": {"monotonic_before_s": lo, "epoch_s": 100},
                    "sampling_stopped": {"monotonic_after_s": hi}}}}})
        events = []
        for kind, mono, epoch in (("phase_start", lo, 100), ("phase_end", hi, 101)):
            event = {"phase": "decode", "event_type": kind, "timestamp_s": epoch}
            if not epoch_events:
                event["metadata"] = {"monotonic_ns": mono * 1_000_000_000}
            events.append(event)
        archive.sources[f"sources/claim-runs/{run}/events.jsonl"] = journal(*events)
    return h


def probe(lo, hi, *, module="synthetic", busy=None):
    return {"module": module, "kind": "interval", "started": {"monotonic_ns": lo},
            "finished": {"monotonic_ns": hi},
            "values": {} if busy is None else {"host_busy_cpu_s_per_s": busy}}


class MonitorDisclosureTests(unittest.TestCase):
    def test_cpu_sums_disjoint_requests_and_clips_both_edges(self):
        """Host CPU integrates each clipped request. Kills M02423, M04013, M04011."""
        h = request_harness()
        h.archives["alpha"].sources["sources/night-custody/hazards/monitor/contention.jsonl"] = journal(
            probe(1_000_000_000, 4_000_000_000, module="contention", busy=2))
        # The busy interval crosses the two inner request edges: only [1,2]
        # and [3,4] contribute. 2 CPU s/s x (1 s + 1 s) = 4 CPU s exactly.
        # Dyadic inputs and integer-second arithmetic are exact in binary64.
        # COMMON bar 4e-6 s: shifts 2 s / 4 s are at least 500,000 bars.
        self.assertEqual(window_line(h.produce(), "host_cpu")["value_s"], 4.)

    def test_restarted_monitor_adds_final_cumulative_session_costs(self):
        """Restarted sessions retain both final CPU totals. Kills M01873."""
        h = Harness()
        h.archives["alpha"].sources["sources/night-custody/hazards/monitor/monitor.jsonl"] = journal(
            {"kind": "session_start"},
            {"kind": "cost", "values": {"cpu_self_s": 1, "cpu_children_s": 1}},
            {"kind": "cost", "values": {"cpu_self_s": 2, "cpu_children_s": 3}},
            {"kind": "session_start"},
            {"kind": "cost", "values": {"cpu_self_s": 3, "cpu_children_s": 4}},
            {"kind": "cost", "values": {"cpu_self_s": 5, "cpu_children_s": 7}})
        # Only the last cumulative cost per session counts: (2+3)+(5+7)=17.
        # Integers are exact binary64; 5 s shift / 17e-6 bar > 294,117 bars.
        self.assertEqual(window_line(h.produce(), "monitor_cost")["cpu_s"], 17.)

    def test_probe_at_phase_end_is_excluded(self):
        """A right-edge probe adds no second phase overlap. Kills M02958."""
        h = request_harness()
        h.archives["alpha"].sources["sources/night-custody/hazards/monitor/probes.jsonl"] = journal(
            probe(1_250_000_000, 1_500_000_000), probe(2_000_000_000, 2_500_000_000))
        # First probe lies inside [1,2); second begins at its excluded end.
        self.assertEqual(window_line(h.produce(), "monitor_cost")["probes_inside_target_phases"], 1)

    def test_epoch_events_use_the_member_clock_anchor(self):
        """Epoch-only events still locate an interior probe. Kills M03440."""
        h = request_harness(epoch_events=True)
        h.archives["alpha"].sources["sources/night-custody/hazards/monitor/probes.jsonl"] = journal(
            probe(1_250_000_000, 1_500_000_000))
        # Epoch 100 is anchored at monotonic 1 s, so this probe is inside.
        self.assertEqual(window_line(h.produce(), "monitor_cost")["probes_inside_target_phases"], 1)


class EnergyDisclosureTests(unittest.TestCase):
    def test_exact_minimum_and_quad_limited_warning(self):
        """Five is sufficient; four quads require a warning. Kills M02220, M02717."""
        for n_r, n_b, warned in ((5, 5, False), (10, 4, True)):
            with self.subTest(n_r=n_r, n_b=n_b):
                h = Harness()
                for row in h.rows[n_r:10]:
                    h.flag("alpha", "battery.assist", row["member"]["bundle_id"])
                for index in range(n_b, 10):
                    h.flag("alpha", "battery.assist", h.rows[10 + 4 * index]["member"]["bundle_id"])
                record = h.produce()
                line = next(row for row in record["cells"] if row["line"] == "battery_assist_cell")
                self.assertEqual((line["n_r"], line["n_b"]), (n_r, n_b))
                self.assertEqual("below the registered minimum of 5 units" in line["text"], warned)

    def test_zero_ratio_is_an_outside_band_member(self):
        """A finite zero rail ratio produces its outside-band record. Kills M02826."""
        h = Harness()
        run = h.rows[0]["member"]["bundle_id"]
        h.archives["alpha"].withheld["withheld/meter.json"] = d.canonical_json_bytes({"members": {
            run: {"rho": 0., "rail_delta_J": 0.,
                  "machine": {"delta_J": 600., "battery_available": True}}}})
        line = window_line(h.produce(), "machine_member")
        self.assertEqual(line["run_id"], run)
        self.assertIs(line["plausible"], False)
        self.assertIn("outside the hard band", line["text"])


class ReferenceDisclosureTests(unittest.TestCase):
    def test_historical_counts_default_to_three_one_three(self):
        """Absent historical counts retain the registered shape. Kills M01948."""
        h = Harness()
        archive = h.archives["alpha"]
        screen = json.loads(archive.outputs["derived/neg8-screen.json"])
        del screen["rescreen"]["survivors"]["reference_counts"]
        archive.outputs["derived/neg8-screen.json"] = d.canonical_json_bytes(screen)
        line = window_line(h.produce(), "reference_counts")
        self.assertEqual(line["counts"], {"start": 3, "midpoint": 1, "end": 3})
        self.assertIn("3, 1, 3 against planned (3, 1, 3)", line["text"])

    def test_rendered_corpus_includes_nonzero_drop_count(self):
        """The released corpus sentence prints reason and count. Kills M01974."""
        h = Harness()
        for row in h.rows[:2]:
            h.flag("alpha", "neg8.corpus_member_dropped", row["member"]["bundle_id"],
                   observed={"reasons": ["synthetic_reason"]})
        record = h.produce()
        self.assertEqual(window_line(record, "corpus_counts")["drop_counts"]["synthetic_reason"], 2)
        self.assertIn("synthetic_reason 2", d.render_disclosures(record, released=True))


class TemperatureDisclosureTests(unittest.TestCase):
    def temperature(self, values):
        h = Harness()
        h.archives["alpha"].sources["sources/claim-runs/campaign_manifests/synthetic.json"] = d.canonical_json_bytes({
            "stage_id": "synthetic", "members": [{}], "battery_temperature_readings": [
                {"temperature_centi_c": value} for value in values]})
        return h.produce()

    def test_single_centi_degree_reading_prints_celsius(self):
        """One reading of 3000 centi-degrees prints 30.00 C. Kills M04168, M04119."""
        record = self.temperature([3000])
        # 3000 centi-C is 30 C. The .30 C / 299970 C mutant shifts are at
        # least 10,000 x COMMON's 1e-6 relative bar (30e-6 C).
        self.assertIn("battery temperature readings: 30.00 C;", d.render_disclosures(record, released=True))

    def test_three_readings_can_form_a_level_plateau(self):
        """Exactly three trailing readings are sufficient for a plateau. Kills M04111."""
        line = window_line(self.temperature([3000, 3025, 3000]), "battery_temperature")
        # The .25 K range is comfortably below the registered .5 K limit.
        self.assertIs(line["plateau"], True)
        self.assertIs(line["producer_flag"], False)

    def test_trailing_range_prevents_false_plateau(self):
        """A rising trailing triplet is not level and emits a warning. Kills M03509."""
        line = window_line(self.temperature([3000, 3350, 3400, 3500]), "battery_temperature")
        # Trailing 33.5,34,35 C span 1.5 K, well above .5 K; total rise is 5 K.
        self.assertIs(line["plateau"], False)
        self.assertIs(line["producer_flag"], True)
