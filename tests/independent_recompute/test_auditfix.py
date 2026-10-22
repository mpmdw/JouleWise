"""F4/F12 witnesses: production-shaped synthetic archives through the real CLI."""
import copy
import csv
import io
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from .support import (assert_values_agree, SCRIPT, ROOT, agreement_bar, bundle, dump, full_pack, recompute as r, run_cli)
from .test_meter import stream_file


class AuditFixTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def production_claim(self, archive, rid):
        # Production sampler cadence is 100 ms; Unix epoch placement exercises
        # cancellation that quarter-second, near-zero fixtures cannot expose.
        epoch = 1_800_000_000.
        return bundle(archive / "sources/claim-runs", rid, power=10.1, prompt=42,
                      records=[(epoch + i / 10, epoch + (i + 1) / 10, 10.1) for i in range(40)],
                      edges={"request": (epoch + 1, epoch + 3), "decode": (epoch + 2, epoch + 3),
                             "prefill": (epoch + 1, epoch + 1.03125)})

    def test_missing_and_compressed_plists_are_counted_stops_in_cli(self):
        archive = full_pack(self.root, "ALPHA", 5)
        rid = "fixture-decode-r01"
        self.production_claim(archive, rid)
        raw = archive / "sources/claim-runs" / rid / "raw/powermetrics.plist"
        original = raw.read_bytes()
        for state in ("present", "missing", "compressed"):
            with self.subTest(state=state):
                if state == "present":
                    raw.write_bytes(original)
                else:
                    raw.unlink(missing_ok=True)
                compressed = raw.with_suffix(raw.suffix + ".zst")
                if state == "compressed":
                    # Opaque synthetic compressed sibling: recompute must never
                    # open or decode it; restoration belongs to the other lane.
                    compressed.write_bytes(b"synthetic compressed input, do not open")
                out_path = self.root / (state + ".json")
                result = subprocess.run([sys.executable, str(SCRIPT), "--alpha", str(archive),
                                         "--member-detail", "--out", str(out_path)],
                                        cwd=ROOT, text=True, capture_output=True, check=True)
                out = json.loads(out_path.read_text())
                row = out["comparison"]["members"]["ALPHA"][rid]
                detail = out["members"]["ALPHA"][rid]
                self.assertEqual(row, detail["comparison"])
                self.assertIn('"not_compared_runs":', result.stdout)
                summary = out["comparison"]["summary"]
                if state == "present":
                    self.assertEqual(row["status"], "compared")
                    self.assertEqual(summary["not_compared_runs"], 0)
                    self.assertTrue(detail["E_j"])
                    self.assertFalse(out["comparison_stopped"])
                else:
                    self.assertEqual(row["status"], "not_compared")
                    self.assertEqual(row["reason"], "trace_plist_missing")
                    self.assertEqual(summary["not_compared_runs"], 1)
                    self.assertEqual(summary["not_compared_by_reason"], {"trace_plist_missing": 1})
                    self.assertEqual(detail["E_j"], {})
                    self.assertTrue(out["comparison_stopped"])
                    flag = next(f for f in out["flags"] if f["code"] == "trace_plist_missing")
                    self.assertTrue(flag["stops_comparison"])
                    if state == "compressed":
                        self.assertEqual(row["input_status"], "compressed")
                        self.assertEqual(row["compressed_input"], "raw/powermetrics.plist.zst")
                        self.assertEqual(row["restore_tool"], "scripts/restore_run_to_scratch.py")
                        self.assertEqual(compressed.read_bytes(), b"synthetic compressed input, do not open")

    def test_one_percent_shared_csv_summary_fault_remains_visible(self):
        archive = full_pack(self.root, "ALPHA", 5)
        rid = "fixture-decode-r01"
        path = self.production_claim(archive, rid)
        # Planted defect is 1%, vastly above COMMON's 1e-6 relative agreement
        # bar; it must not leak into the independent raw-plist integration.
        factor = 1.01
        trace = list(csv.DictReader((path / "power_trace.csv").read_text().splitlines()))
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=list(trace[0]))
        writer.writeheader()
        for row in trace:
            row["power_w"] = str(float(row["power_w"]) * factor)
            writer.writerow(row)
        (path / "power_trace.csv").write_text(output.getvalue())
        summary = json.loads((path / "summary_metrics.json").read_text())
        summary["gross_energy_j"] *= factor
        summary["phase_energy_j"] = {k: v * factor for k, v in summary["phase_energy_j"].items()}
        for envelope in summary["energy_anchor_shift_envelopes"].values():
            for key in envelope:
                envelope[key] *= factor
        dump(path / "summary_metrics.json", summary)
        _, out, _ = run_cli({"ALPHA": archive}, self.root / "fault.json", ("--member-detail",))
        codes = [f["code"] for f in out["flags"] if f["scope"].split("/")[0] == rid]
        self.assertEqual(codes.count("trace_csv_plist_mismatch"), 1)
        self.assertEqual(codes.count("stored_energy_mismatch"), 3)
        self.assertEqual(codes.count("stored_envelope_mismatch"), 3)
        self.assertEqual(out["comparison"]["summary"]["not_compared_runs"], 0)
        # Closed-form 10.1 W over 1 s, unrounded J, COMMON bar.
        assert_values_agree(self, out["members"]["ALPHA"][rid]["E_j"]["decode"], 10.1)

    def test_extra_session_missing_plist_is_reported_and_counted_separately(self):
        archive = full_pack(self.root, "BETA", 5)
        rid = "fixture-decode-r01"
        (archive / "sources/claim-runs" / rid / "raw/powermetrics.plist").unlink()
        _, out, stdout = run_cli({}, self.root / "extra.json", ("--extra-beta", str(archive)))
        report = out["comparison"]["extra_beta"]
        self.assertEqual(report["members"]["0"][rid]["status"], "not_compared")
        self.assertTrue(report["comparison_stopped"])
        self.assertEqual(out["comparison"]["summary"]["not_compared_runs"], 1)
        self.assertIn('"not_compared_runs":1', stdout)

    def machine_archive(self):
        from joulewise.external import km003c_parse as primary

        archive = full_pack(self.root, "ALPHA", 5)
        rid = "fixture-decode-r01"
        for path in (archive / "sources/claim-runs").glob("*/metadata.json"):
            meta = json.loads(path.read_text())
            anchor = meta["uncertainty_evidence"]["clock_anchor"]
            anchor.update(wall_minus_monotonic_lower_s=-1020., wall_minus_monotonic_upper_s=-1020.,
                          clock_stamps={"sampling_started": {"epoch_s": 1., "monotonic_before_s": 1021.},
                                        "sampling_stopped": {"epoch_s": 3., "monotonic_after_s": 1023.0004}})
            dump(path, meta)
            events = path.parent / "events.jsonl"
            idle = [{"event_type": "stage_started", "phase": "idle_baseline", "timestamp_s": -19.,
                     "metadata": {"monotonic_ns": 1_001_000_000_000}},
                    {"event_type": "stage_completed", "phase": "idle_baseline", "timestamp_s": -17.}]
            events.write_text("".join(json.dumps(e) + "\n" for e in idle) + events.read_text())
            (path.parent / "rich_telemetry_idle.jsonl").write_text(
                json.dumps({"elapsed_ns": 100_000_000, "rail_sum_power_w": 1.}) + "\n")
        meter = archive / "sources/night-custody/hazards/meter/stream-001.jsonl"
        stream_file(meter, lambda t: 10. if t < 15. else 40. + t,
                    battery=lambda t: 0. if t < 15. else .5)
        stream = primary.parse(meter)
        # Controller start-before / stop-after in integer ns, including a
        # 0.4 ms stop bracket. A 50 Hz sample lies on the old stop edge.
        window = [1_021_000_000_000, 1_023_000_400_000]
        baseline = [1_001_000_000_000, 1_003_000_000_000]
        machine = primary.delta_machine_energy(stream, window, baseline)
        # REG 5.8: rail gross and idle subtraction both use the event's 2 s;
        # the meter's controller brackets do not change the rail duration.
        rail = 2 * (10.1 - 1.)
        recorded = {"members": {rid: {"machine": machine, "rail_delta_J": rail,
                                     "rho": rail / machine["delta_J"]}}}
        dump(archive / "withheld/meter.json", recorded)
        return archive, rid, recorded, stream

    def test_machine_strict_bars_and_controller_window_agree_with_primary(self):
        archive, rid, recorded, stream = self.machine_archive()
        _, clean, _ = run_cli({"ALPHA": archive}, self.root / "machine.json")
        own = clean["disclosures"]["whole_machine"]["windows"]["ALPHA"]["members"][rid]["phases"]["request"]
        self.assertTrue(own["recorded_comparison"]["matches"], own["recorded_comparison"])
        self.assertEqual(own["window_ns"], recorded["members"][rid]["machine"]["window_ns"])
        self.assertEqual(own["meter"]["n"], recorded["members"][rid]["machine"]["meter"]["n"])
        # The old event-based stop omits 0.4 ms and a sample. The duration adds
        # 62 W *0.0004 s =0.0248 J; one ramp sample adds 0.01 W *2 s =0.02 J.
        # Their 0.0448 J sum exceeds COMMON's 1e-6 relative bar; no bar widens.
        old = r.sampled_term(stream.host_ns, stream.watts, [1_021_000_000_000, 1_023_000_000_000],
                             own["baseline_ns"])
        self.assertGreater(abs(old["energy_J"] - own["meter"]["energy_J"]), agreement_bar(own["meter"]["energy_J"]))
        assert_values_agree(self, own["meter"]["energy_J"] - old["energy_J"], .0448)
        mutations = (("rho",), ("rail_delta_J",), ("machine", "delta_J"),
                     ("machine", "meter", "energy_J"), ("machine", "meter", "baseline_W"),
                     ("machine", "meter", "n"), ("machine", "window_ns"))
        for keys in mutations:
            with self.subTest(field=keys):
                changed = copy.deepcopy(recorded)
                row = changed["members"][rid]
                for key in keys[:-1]:
                    row = row[key]
                # Mutation sizes are faults, not comparison bars: +0.125 rho
                # reproduces F12; 1% scalar edits exceed COMMON; count/ns edits
                # exercise the exact discrete input properties.
                if keys[-1] == "rho":
                    row["rho"] += .125
                elif keys[-1] == "n":
                    row["n"] += 1
                elif keys[-1] == "window_ns":
                    row["window_ns"][0] += 1
                else:
                    row[keys[-1]] *= 1.01
                dump(archive / "withheld/meter.json", changed)
                _, out, _ = run_cli({"ALPHA": archive}, self.root / "changed.json")
                flag = next(f for f in out["flags"] if f["code"] == "meter_request_mismatch" and f["scope"] == rid)
                name = "window_start_ns" if keys[-1] == "window_ns" else "/".join(keys[1:] if keys[0] == "machine" else keys)
                self.assertIn(name, flag["detail"]["fields"])

    def test_absent_or_compressed_meter_names_the_uncomputed_input(self):
        archive = full_pack(self.root, "ALPHA", 5)
        for compressed in (False, True):
            with self.subTest(compressed=compressed):
                if compressed:
                    path = archive / "sources/night-custody/hazards/meter/stream-001.jsonl.zst"
                    path.parent.mkdir(parents=True)
                    path.write_bytes(b"synthetic compressed stream")
                _, out, _ = run_cli({"ALPHA": archive}, self.root / "absent.json")
                line = out["disclosures"]["whole_machine"]["windows"]["ALPHA"]
                self.assertEqual(line["status"], "not_computed")
                flag = next(f for f in out["flags"] if f["code"] == "meter_absent")
                self.assertEqual(flag["detail"], line["input_detail"])
                if compressed:
                    self.assertEqual(flag["detail"]["compressed_inputs"], ["stream-001.jsonl.zst"])
                    self.assertEqual(flag["detail"]["restore_tool"], "scripts/restore_run_to_scratch.py")

    def test_missing_plist_never_passes_machine_comparison_even_in_diagnostic_mode(self):
        archive, rid, _, _ = self.machine_archive()
        (archive / "sources/claim-runs" / rid / "raw/powermetrics.plist").unlink()
        for extra in ((), ("--diagnostic-ignore-exclusions",)):
            with self.subTest(diagnostic=bool(extra)):
                _, out, _ = run_cli({"ALPHA": archive}, self.root / "missing-machine.json", extra)
                row = out["disclosures"]["whole_machine"]["windows"]["ALPHA"]["members"][rid]["phases"]["request"]
                self.assertIsNone(row["delta_J"])
                self.assertEqual(row["recorded_comparison"], {
                    "status": "not_compared", "matches": None, "reason": "trace_plist_missing"})
                self.assertEqual(out["comparison"]["summary"]["not_compared_runs"], 1)
                self.assertTrue(out["comparison_stopped"])

    def test_different_clock_fit_bins_disclose_energy_difference_without_slack(self):
        from joulewise.external import km003c_parse as primary

        archive, rid, recorded, _ = self.machine_archive()
        path = archive / "sources/night-custody/hazards/meter/stream-001.jsonl"
        rows = [json.loads(line) for line in path.read_text().splitlines()]
        for i, row in enumerate(rows):
            if row.get("k") == "b":
                # Bounded synthetic arrival jitter, below the meter's 3 ms
                # eligible RTT cap. It exercises different bin-minimum methods.
                latency = ((i * 137) % 1800) * 1000
                row["tx"] += latency
                row["rx"] += latency
        path.write_text("".join(json.dumps(row) + "\n" for row in rows))
        own_stream = r.MeterStream(path, r.Reader("synthetic", []))
        primary_stream = primary.parse(path)
        # At 50 Hz, sample 1150 is 23 s after stream start. Place the stop
        # between the two fits' placements so their method difference matters.
        sample = 1150
        boundary = (own_stream.times[sample] + primary_stream.host_ns[sample]) // 2
        metadata_path = archive / "sources/claim-runs" / rid / "metadata.json"
        metadata = json.loads(metadata_path.read_text())
        stamp = metadata["uncertainty_evidence"]["clock_anchor"]["clock_stamps"]["sampling_stopped"]
        stamp["monotonic_after_s"] = boundary / 1e9
        dump(metadata_path, metadata)
        record = recorded["members"][rid]
        window = [1_021_000_000_000, math.floor(stamp["monotonic_after_s"] * 1e9)]
        machine = primary.delta_machine_energy(primary_stream, window, record["machine"]["baseline_ns"])
        record.update(machine=machine, rail_delta_J=2 * (10.1 - 1.))
        record["rho"] = record["rail_delta_J"] / machine["delta_J"]
        dump(archive / "withheld/meter.json", recorded)
        _, out, _ = run_cli({"ALPHA": archive}, self.root / "fit-difference.json")
        own = out["disclosures"]["whole_machine"]["windows"]["ALPHA"]["members"][rid]["phases"]["request"]
        difference = own["meter"]["energy_J"] - machine["meter"]["energy_J"]
        flag = next(f for f in out["flags"] if f["code"] == "meter_request_mismatch" and f["scope"] == rid)
        self.assertIn("meter/energy_J", flag["detail"]["fields"])
        self.assertIn("meter/n", flag["detail"]["fields"])
        self.assertGreater(abs(difference), agreement_bar(machine["meter"]["energy_J"]))
        # A single extra sample on the 1 W/s ramp changes mean power by
        # 0.01 W; over approximately 2 s this is 0.02 J (COMMON unrounded bar).
        assert_values_agree(self, difference, -.02)
        print("synthetic_fit_difference=" + json.dumps({
            "energy_difference_J": difference,
            "agreement_bar_J": agreement_bar(machine["meter"]["energy_J"]),
            "sample_time_difference_ns": own_stream.times[sample] - primary_stream.host_ns[sample],
            "count_difference": own["meter"]["n"] - machine["meter"]["n"]}, sort_keys=True))
