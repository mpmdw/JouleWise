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
from unittest import mock

from .support import (assert_values_agree, SCRIPT, ROOT, agreement_bar, bundle, dump, full_pack,
                      recompute as r, remove_member, run_cli)
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

    def test_missing_compressed_and_unreadable_plists_are_counted_stops_in_cli(self):
        archive = full_pack(self.root, "ALPHA", 5)
        rid = "fixture-decode-r01"
        self.production_claim(archive, rid)
        raw = archive / "sources/claim-runs" / rid / "raw/powermetrics.plist"
        original = raw.read_bytes()
        for state in ("present", "missing", "compressed", "empty", "garbage", "truncated"):
            with self.subTest(state=state):
                if state in ("present", "empty", "garbage", "truncated"):
                    raw.write_bytes({"present": original, "empty": b"", "garbage": b"\x00not a plist",
                                     "truncated": original[:-20]}[state])
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
                    self.assertIn(" comparison_stopped=false", result.stdout)
                else:
                    reason = "trace_plist_unreadable" if state in ("empty", "garbage", "truncated") else "trace_plist_missing"
                    self.assertEqual(row["status"], "not_compared")
                    self.assertEqual(row["reason"], reason)
                    self.assertEqual(summary["compared_runs"], 68)
                    self.assertEqual(summary["not_compared_runs"], 1)
                    self.assertEqual(summary["not_compared_by_reason"], {reason: 1})
                    self.assertEqual(detail["E_j"], {})
                    self.assertTrue(out["comparison_stopped"])
                    self.assertIn(" comparison_stopped=true", result.stdout)
                    flag = next(f for f in out["flags"] if f["code"] == reason)
                    self.assertTrue(flag["stops_comparison"])
                    if state == "compressed":
                        self.assertEqual(row["input_status"], "compressed")
                        self.assertEqual(row["compressed_input"], "raw/powermetrics.plist.zst")
                        self.assertEqual(row["restore_tool"], "scripts/restore_run_to_scratch.py")
                        self.assertNotIn("restore_tool_availability", row)
                        self.assertEqual(compressed.read_bytes(), b"synthetic compressed input, do not open")

    def test_trace_stops_are_scoped_to_selected_runs_in_both_detail_modes(self):
        for kind in ("excluded_science", "lost_reference", "unselected_corpus"):
            archive = full_pack(self.root / kind, "ALPHA", 6)
            if kind == "excluded_science":
                rid = "fixture-decode-r01"
                remove_member(archive, rid)
            elif kind == "lost_reference":
                rid = "neg8-window-start-r1"
                screen_path = archive / "derived/neg8-screen.json"
                screen = json.loads(screen_path.read_text())
                screen["rescreen"]["survivors"]["reference_losses"] = [{"bundle_id": rid}]
                screen["rescreen"]["survivors"]["reference_counts"]["start"] = 2
                dump(screen_path, screen)
            else:
                rid = "neg8-refcorpus-r13"
                bundle(archive / "sources/bound-runs", rid, model="Qwen2.5-1.5B-Instruct-4bit")
            root = "bound-runs" if kind == "unselected_corpus" else "claim-runs"
            raw = archive / "sources" / root / rid / "raw/powermetrics.plist"
            # A meter disclosure also loads excluded roster members in default
            # mode, so the comparison set cannot be inferred from loaded ids.
            for meter in (False, True):
                if meter:
                    stream_file(archive / "sources/night-custody/hazards/meter/stream-001.jsonl", lambda t: 10.)
                for reason in ("trace_plist_missing", "trace_plist_unreadable"):
                    raw.unlink(missing_ok=True)
                    if reason == "trace_plist_unreadable":
                        raw.write_bytes(b"malformed plist")
                    for detail in (False, True):
                        with self.subTest(kind=kind, meter=meter, reason=reason, detail=detail):
                            _, out, _ = run_cli({"ALPHA": archive}, self.root / "unselected.json",
                                                ("--member-detail",) if detail else ())
                            self.assertFalse(out["comparison_stopped"])
                            flags = [f for f in out["flags"] if f["code"] == reason and f["scope"] == rid]
                            if detail:
                                self.assertEqual(len(flags), 1)
                            self.assertTrue(all(not f["stops_comparison"] for f in flags))

    def test_comparison_counts_are_invariant_to_detail_and_meter_disclosures(self):
        archive = full_pack(self.root, "ALPHA", 5)
        rid = "fixture-decode-r01"
        remove_member(archive, rid)
        raw = archive / "sources/claim-runs" / rid / "raw/powermetrics.plist"
        original = raw.read_bytes()
        meter = archive / "sources/night-custody/hazards/meter/stream-001.jsonl"
        expected = {"compared_runs": 68, "not_compared_runs": 0, "not_compared_by_reason": {}}
        for present in (True, False):
            if present:
                raw.write_bytes(original)
            else:
                raw.unlink()
            for has_meter in (False, True):
                if has_meter:
                    stream_file(meter, lambda t: 10.)
                else:
                    meter.unlink(missing_ok=True)
                for detail in (False, True):
                    with self.subTest(plist=present, meter=has_meter, detail=detail):
                        _, out, stdout = run_cli({"ALPHA": archive}, self.root / "counts.json",
                                                 ("--member-detail",) if detail else ())
                        report = out["comparison"]
                        self.assertEqual(report["summary"], expected)
                        fields = dict(field.split("=", 1) for field in stdout.split())
                        self.assertEqual(json.loads(fields["comparison"]), expected)
                        self.assertFalse(out["comparison_stopped"])
                        self.assertFalse(json.loads(fields["comparison_stopped"]))
                        loaded = detail or has_meter
                        self.assertEqual(rid in report["members"]["ALPHA"], loaded)
                        self.assertEqual(report["detail_only_runs"], {
                            "count": int(loaded), "compared_runs": int(loaded and present),
                            "not_compared_runs": int(loaded and not present),
                            "not_compared_by_reason": {"trace_plist_missing": 1} if loaded and not present else {}})

    def test_selected_reference_and_corpus_trace_failures_stop_in_both_detail_modes(self):
        for kind, rid in (("claim-runs", "neg8-window-start-r1"), ("bound-runs", "neg8-refcorpus-r01")):
            archive = full_pack(self.root / kind, "ALPHA", 5)
            raw = archive / "sources" / kind / rid / "raw/powermetrics.plist"
            for reason in ("trace_plist_missing", "trace_plist_unreadable"):
                raw.unlink(missing_ok=True)
                if reason == "trace_plist_unreadable":
                    raw.write_bytes(b"unparsable")
                for detail in (False, True):
                    with self.subTest(kind=kind, reason=reason, detail=detail):
                        _, out, _ = run_cli({"ALPHA": archive}, self.root / "selected.json",
                                            ("--member-detail",) if detail else ())
                        self.assertTrue(out["comparison_stopped"])
                        flag = next(f for f in out["flags"] if f["code"] == reason and f["scope"] == rid)
                        self.assertTrue(flag["stops_comparison"])

    def test_stored_pre_bound_copy_is_exact_and_bop_bar_is_relative_only(self):
        archive = full_pack(self.root, "ALPHA", 5)
        rid = "fixture-decode-r01"
        path = archive / "sources/claim-runs" / rid / "metadata.json"
        meta = json.loads(path.read_text())
        pre = meta["instrument_calibration"]["b_fiducial_s"]
        for value in (pre, math.nextafter(pre, math.inf), pre + 5e-7):
            with self.subTest(pre=value):
                meta["instrument_calibration"]["b_fiducial_s"] = value
                dump(path, meta)
                flags = []
                window = r.Window("ALPHA", archive, flags)
                window.member(rid)
                self.assertEqual(any(f["code"] == "member_pre_bound_mismatch" for f in flags), value != pre)
        path = archive / "withheld/bracket-evaluation.json"
        # At 45 ms the ruling's relative bar is 45 ns; a 0.5 us edit passed
        # the former absolute 1 us floor. Half/twice the bar pin its boundary.
        bop = window.b["b_op_s"]
        for edit, mismatch in ((0., False), (.5e-6 * bop, False), (2e-6 * bop, True), (5e-7, True)):
            with self.subTest(bop_edit=edit):
                dump(path, {"assessment": {"b_fiducial_s": bop + edit}})
                flags = []
                r.Window("ALPHA", archive, flags)
                self.assertEqual(any(f["code"] == "b_op_mismatch" for f in flags), mismatch)

    def test_plist_csv_copy_identity_rejects_one_epoch_ulp_or_power_ulp(self):
        archive = full_pack(self.root, "ALPHA", 5)
        rid = "fixture-decode-r01"
        path = self.production_claim(archive, rid)
        trace = list(csv.DictReader((path / "power_trace.csv").read_text().splitlines()))
        for column in (None, "interval_start_s", "interval_end_s", "power_w"):
            with self.subTest(column=column):
                rows = copy.deepcopy(trace)
                if column:
                    # Timestamp placement belongs to all three rails of the
                    # record; changing just one would test malformed CSV.
                    for row in rows[:1 if column == "power_w" else 3]:
                        row[column] = str(math.nextafter(float(row[column]), math.inf))
                output = io.StringIO()
                writer = csv.DictWriter(output, fieldnames=list(trace[0]))
                writer.writeheader()
                writer.writerows(rows)
                (path / "power_trace.csv").write_text(output.getvalue())
                flags = []
                member = r.Member(path, rid, r.Reader("ALPHA", flags), .045)
                self.assertEqual(any(f["code"] == "trace_csv_plist_mismatch" for f in flags), column is not None)
                self.assertEqual(member.comparison["status"], "compared")

    def test_one_percent_shared_csv_summary_fault_remains_visible(self):
        archive = full_pack(self.root, "ALPHA", 5)
        rid = "fixture-decode-r01"
        path = self.production_claim(archive, rid)
        # Planted defect is 1%, vastly above the agreement policy's 1e-6 relative agreement
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
        # Closed-form 10.1 W over 1 s, unrounded J, Agreement policy bar.
        assert_values_agree(self, out["members"]["ALPHA"][rid]["E_j"]["decode"], 10.1)

    def test_extra_session_missing_plist_is_reported_and_counted_separately(self):
        archive = full_pack(self.root, "BETA", 5)
        rid = "fixture-decode-r01"
        (archive / "sources/claim-runs" / rid / "raw/powermetrics.plist").unlink()
        primary = full_pack(self.root, "ALPHA", 5)
        for pack in (archive, primary):
            remove_member(pack, "fixture-decode-r02")
        _, out, stdout = run_cli({"ALPHA": primary}, self.root / "extra.json",
                                 ("--member-detail", "--extra-beta", str(archive)))
        report = out["comparison"]["extra_beta"]
        self.assertEqual(report["members"]["0"][rid]["status"], "not_compared")
        self.assertTrue(report["comparison_stopped"])
        self.assertFalse(out["comparison_stopped"])
        self.assertEqual(out["comparison"]["summary"], {
            "compared_runs": 68, "not_compared_runs": 0, "not_compared_by_reason": {}})
        self.assertEqual(report["summary"], {
            "compared_runs": 67, "not_compared_runs": 1, "not_compared_by_reason": {"trace_plist_missing": 1}})
        self.assertEqual(out["comparison"]["detail_only_runs"], {
            "count": 1, "compared_runs": 1, "not_compared_runs": 0, "not_compared_by_reason": {}})
        self.assertEqual(report["detail_only_runs"]["count"], 0)
        fields = dict(field.split("=", 1) for field in stdout.split())
        self.assertEqual(json.loads(fields["comparison"]), out["comparison"]["summary"])
        self.assertFalse(json.loads(fields["comparison_stopped"]))
        self.assertEqual(json.loads(fields["extra_beta_comparison"]), {
            "summary": report["summary"], "comparison_stopped": True})

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
        self.assertTrue(all(type(t) is int for t in own["window_ns"] + own["baseline_ns"]))
        self.assertEqual(own["meter"]["n"], recorded["members"][rid]["machine"]["meter"]["n"])
        # The old event-based stop omits 0.4 ms and a sample. The duration adds
        # 62 W *0.0004 s =0.0248 J; one ramp sample adds 0.01 W *2 s =0.02 J.
        # Their 0.0448 J sum exceeds the agreement policy's 1e-6 relative bar; no bar widens.
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
                # reproduces F12; 1% scalar edits exceed Agreement policy; count/ns edits
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
                    self.assertNotIn("restore_tool_availability", flag["detail"])

    def test_unusable_anchor_and_failed_status_are_never_counted_as_compared(self):
        archive, rid, _, _ = self.machine_archive()
        path = archive / "sources/claim-runs" / rid
        original_meta = json.loads((path / "metadata.json").read_text())
        original_summary = json.loads((path / "summary_metrics.json").read_text())
        for state, reason in (("unresolved", "anchor_unbounded"), ("no_endpoint", "anchor_unbounded"),
                              ("failed", "status_not_succeeded")):
            with self.subTest(state=state):
                meta, summary = copy.deepcopy(original_meta), copy.deepcopy(original_summary)
                if state == "failed":
                    summary["status"] = "failed"
                elif state == "no_endpoint":
                    del meta["uncertainty_evidence"]["clock_anchor"]["first_sample_end_point_epoch_s"]
                else:
                    meta["uncertainty_evidence"]["clock_anchor"]["status"] = "unresolved"
                dump(path / "metadata.json", meta)
                dump(path / "summary_metrics.json", summary)
                _, out, _ = run_cli({"ALPHA": archive}, self.root / "unusable.json", ("--member-detail",))
                self.assertEqual(out["comparison"]["members"]["ALPHA"][rid], {"status": "not_compared", "reason": reason})
                self.assertEqual(out["comparison"]["summary"], {
                    "compared_runs": 68, "not_compared_runs": 1, "not_compared_by_reason": {reason: 1}})
                self.assertEqual(out["members"]["ALPHA"][rid]["E_j"], {})
                machine = out["disclosures"]["whole_machine"]["windows"]["ALPHA"]["members"][rid]["phases"]["request"]
                self.assertIsNone(machine["delta_J"])
                self.assertEqual(machine["recorded_comparison"], {"status": "not_compared", "matches": None, "reason": reason})

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

    def adversarial_fit_window(self):
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
        primary_stream = primary.parse(path)
        # The pre-RC-CMP-2 binning (7e322b767) placed sample 1150, 23 s after
        # stream start at 50 Hz, 1249 ns from the parser. The stop sits between
        # the two placements, where the old method moved a sample across it.
        from .test_meter_fit import old_clock_fit
        with mock.patch.object(r, "meter_clock_fit", old_clock_fit):
            old_stream = r.MeterStream(path, r.Reader("synthetic", []))
        sample = 1150
        boundary = (old_stream.times[sample] + primary_stream.host_ns[sample]) // 2
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
        return archive, rid, machine, old_stream, primary_stream, path, sample

    def test_adversarial_clock_fit_jitter_agrees_with_parser_within_coded_bar(self):
        archive, rid, machine, old_stream, primary_stream, path, sample = self.adversarial_fit_window()
        own_stream = r.MeterStream(path, r.Reader("synthetic", []))
        self.assertLessEqual(max(abs(a - b) for a, b in zip(own_stream.times, primary_stream.host_ns)), 1)
        _, out, _ = run_cli({"ALPHA": archive}, self.root / "fit-agreement.json")
        own = out["disclosures"]["whole_machine"]["windows"]["ALPHA"]["members"][rid]["phases"]["request"]
        difference = own["meter"]["energy_J"] - machine["meter"]["energy_J"]
        self.assertFalse([f for f in out["flags"] if f["code"] == "meter_request_mismatch" and f["scope"] == rid])
        self.assertTrue(own["recorded_comparison"]["matches"], own["recorded_comparison"])
        self.assertEqual(own["meter"]["n"], machine["meter"]["n"])
        self.assertLessEqual(abs(difference), agreement_bar(machine["meter"]["energy_J"]))
        print("synthetic_fit_agreement=" + json.dumps({
            "energy_difference_J": difference,
            "agreement_bar_J": agreement_bar(machine["meter"]["energy_J"]),
            "old_sample_time_difference_ns": old_stream.times[sample] - primary_stream.host_ns[sample],
            "sample_time_difference_ns": own_stream.times[sample] - primary_stream.host_ns[sample]},
            sort_keys=True))

    def test_counterfactual_old_clock_fit_bins_fail_the_coded_bar(self):
        archive, rid, machine, *_ = self.adversarial_fit_window()
        from .test_meter_fit import old_clock_fit
        with mock.patch.object(r, "meter_clock_fit", old_clock_fit):
            _, out, _ = run_cli({"ALPHA": archive}, self.root / "fit-difference.json")
        own = out["disclosures"]["whole_machine"]["windows"]["ALPHA"]["members"][rid]["phases"]["request"]
        difference = own["meter"]["energy_J"] - machine["meter"]["energy_J"]
        flag = next(f for f in out["flags"] if f["code"] == "meter_request_mismatch" and f["scope"] == rid)
        self.assertIn("meter/energy_J", flag["detail"]["fields"])
        self.assertIn("meter/n", flag["detail"]["fields"])
        self.assertGreater(abs(difference), agreement_bar(machine["meter"]["energy_J"]))
        # One extra sample on the 1 W/s ramp changes mean power by 0.01 W;
        # over about 2 s that is the 0.02 J of commit 7e322b767.
        assert_values_agree(self, difference, -.02)
