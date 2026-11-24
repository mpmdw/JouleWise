"""Round-6 named faults and receipt compatibility. Every file is planted synthetic data."""
from __future__ import annotations

import copy
import csv
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from joulewise.cadence_looks import inclusion_34 as I34
from joulewise.cadence_looks import time_fields as TF

try:
    from joulewise.cadence_looks import fit_interim as F
    from scripts import cadence_look_run as R
    from scripts import cadence_look_synth as synth
except ModuleNotFoundError as exc:  # pragma: no cover
    if exc.name != "numpy":
        raise
    F = R = synth = None


class ReceiptKinds(unittest.TestCase):
    def receipt(self):
        return {"soak_attempts": [{"attempt": 1, "refused": "soak refused"}, {"attempt": 2, "refused": None}],
                "steps": [{"name": "soak", "rc": 2}, {"name": "soak.a2", "rc": 0}]}

    def test_ruled_field_supplies_kind_without_mutating_receipt(self):
        receipt = self.receipt()
        receipt["soak_refusals"] = [{"attempt": 1, "kind": "load"}]
        before = copy.deepcopy(receipt)
        result = I34.soak_retries_from({"synthetic-span": I34.soak_fields(receipt)})
        self.assertEqual(result["spans"]["synthetic-span"]["retried"],
                         [{"attempt": 1, "kind": "load", "read_from": "receipt soak_refusals[].kind"}])
        self.assertEqual(result["retried_by_kind"]["load"], 1)
        self.assertEqual(receipt, before)

    def test_legacy_refusal_kind_and_absent_kind_remain_supported(self):
        receipt = self.receipt()
        receipt["soak_attempts"][0]["refusal_kind"] = "slope"
        result = I34.soak_retries_from({"synthetic-span": I34.soak_fields(receipt)})
        self.assertEqual(result["retried_by_kind"]["slope"], 1)
        del receipt["soak_attempts"][0]["refusal_kind"]
        result = I34.soak_retries_from({"synthetic-span": I34.soak_fields(receipt)})
        self.assertEqual(result["retried_by_kind"]["kind not recorded"], 1)

    def test_empty_refusals_preserve_the_legacy_single_attempt(self):
        fields = I34.soak_fields({"soak_refusals": [], "steps": [{"name": "soak", "rc": 0}]})
        result = I34.soak_retries_from({"synthetic-span": fields})
        self.assertEqual(result["spans"]["synthetic-span"]["attempts"], 1)
        self.assertEqual(result["retried_by_kind"], {"slope": 0, "load": 0, "kind not recorded": 0})

    def test_refusals_are_unique_and_name_refused_attempts(self):
        for refs in ([{"attempt": 2, "kind": "load"}], [{"attempt": 3, "kind": "load"}],
                     [{"attempt": 1, "kind": "load"}] * 2, [{"attempt": 1, "kind": "unknown"}]):
            receipt = self.receipt()
            receipt["soak_refusals"] = refs
            with self.subTest(refs=refs), self.assertRaisesRegex(ValueError, "soak_refusals"):
                I34.soak_fields(receipt)

    def test_writer_provenance_and_legacy_interruption(self):
        first = {"attempt": 1, "started_epoch_s": 1, "refused": None, "output_dir": "soak"}
        for raw, field_present, attempts, accepted in (
                ({"steps": [{"name": "soak", "rc": None}]}, False, 1, False),
                ({"steps": [{"name": "soak"}]}, False, 1, False),
                ({"steps": [], "soak_attempts": []}, True, 0, False),
                ({"steps": [], "soak_attempts": [first]}, True, 1, False)):
            with self.subTest(raw=raw):
                result = I34.soak_retries_from({"s": I34.soak_fields(raw)})["spans"]["s"]
                self.assertEqual(result, {"field_present": field_present, "attempts": attempts,
                                          "accepted": accepted, "retried": []})
        raw = self.receipt()
        raw["soak_attempts"][0]["soak_refusals_kind"] = "slope"
        result = I34.soak_retries_from({"s": I34.soak_fields(raw)})["spans"]["s"]
        self.assertEqual(result["retried"], [{"attempt": 1, "kind": "kind not recorded", "read_from": None}])


class TraceTimes(unittest.TestCase):
    def test_timestamp_s_is_validated_without_converting_power(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "power_trace.csv"
            for stamp in ("", "not-a-stamp", "nan", "inf", "2.0"):
                with p.open("w", newline="") as f:
                    out = csv.DictWriter(f, fieldnames=("rail", "source", "interval_start_s", "interval_end_s",
                                                       "timestamp_s", "power_w"))
                    out.writeheader()
                    out.writerow({"rail": "gpu_power", "source": "powermetrics", "interval_start_s": "1",
                                  "interval_end_s": "2", "timestamp_s": stamp, "power_w": "DO-NOT-DECODE"})
                if stamp == "2.0":
                    self.assertEqual(TF.gpu_rows(d), [(1.0, 2.0)])
                else:
                    with self.subTest(stamp=stamp), self.assertRaisesRegex(TF.TimeFieldError, "stamp"):
                        TF.gpu_rows(d)

    def test_stamps_are_the_writer_spelling_not_every_text_float_accepts(self):
        """``csv.writer`` writes ``repr(float)``. ``float`` alone also takes digits outside ASCII, a sign, spaces
        and underscores; a row spelled that way is no writer's, on any of the three stamp columns."""
        fields = ("rail", "source", "interval_start_s", "interval_end_s", "timestamp_s", "power_w")
        control = {"rail": "gpu_power", "source": "powermetrics", "interval_start_s": "1.5",
                   "interval_end_s": "2.5", "timestamp_s": "2.5", "power_w": "DO-NOT-DECODE"}
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "power_trace.csv"

            def rows(**change):
                with p.open("w", newline="", encoding="utf-8") as f:
                    out = csv.DictWriter(f, fieldnames=fields)
                    out.writeheader()
                    out.writerow(dict(control, **change))
                return TF.gpu_rows(d)

            for spelling, value in (("1.5", 1.5), ("2", 2.0), ("-0.0", -0.0), ("1e-05", 1e-05), ("1.5e+16", 1.5e16),
                                    ("1794719426.5356786", 1794719426.5356786)):
                with self.subTest(admitted=spelling):
                    self.assertEqual(rows(interval_start_s=spelling), [(value, 2.5)])
            for spelling in ("\u0661.\u0665", "1\u0662", " 1.5", "1.5 ", "+1.5", "1_0", "1.", ".5", "0x1p0", "1,5",
                             "\uff11.5", "Infinity", "NaN"):
                for column in fields[2:5]:
                    with self.subTest(refused=spelling, column=column), \
                            self.assertRaisesRegex(TF.TimeFieldError, "stamp"):
                        rows(**{column: spelling})


@unittest.skipIf(R is None, "numpy is not installed; required NumPy CI exercises this class")
class NamedFaults(unittest.TestCase):
    KEY = "synthetic-span/L001"

    def test_compressed_trace_names_the_leg(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "power_trace.csv.zst").write_bytes(b"synthetic placeholder")
            turn = {"segments": [{"wall_start_s": 1.0, "wall_end_s": 2.0}], "prefix_tails": []}
            with self.assertRaises(F.LookInputError) as raised:
                R.trace_holes(turn, Path(d), None, "unavailable", self.KEY)
            self.assertIn(self.KEY, str(raised.exception))
            self.assertIn("power_trace.csv.zst", str(raised.exception))

    def test_meter_decoder_fault_names_leg_stream_and_unavailable_gap(self):
        from tests.cadence.test_time_fields import stream_lines, write_stream
        with tempfile.TemporaryDirectory() as d:
            lines = stream_lines(seconds=20.0)
            for i, line in enumerate(lines):
                doc = json.loads(line)
                if doc["k"] == "b":
                    doc["smc"] = 987654
                    lines[i] = json.dumps(doc)
                    break
            meter = write_stream(Path(d), lines, "stream-synthetic.jsonl")
            # The permitted time projection still decodes normally; only the value decoder faults.
            times = TF.SpanMeter(Path(d)).t
            with self.assertRaises(F.LookInputError) as raised:
                R.MeterSpan(Path(d), expected_t=times, leg_key=self.KEY)
            msg = str(raised.exception)
            for field in (self.KEY, meter.name, "decoder fault", "gap unavailable"):
                self.assertIn(field, msg)
            self.assertNotIn("987654", msg)

    def test_gpu_reader_fault_names_leg_and_trace_without_exception_values(self):
        with tempfile.TemporaryDirectory() as d:
            leg = Path(d) / "legs/L001"
            bundle = leg / "runtime/synthetic-bundle"
            bundle.mkdir(parents=True)
            (leg / "leg_record.json").write_text(json.dumps({"result": {"bundle": "synthetic-bundle"}}))
            (bundle / "power_trace.csv").write_text(
                "timestamp_s,power_w,source,rail,interval_start_s,interval_end_s\n"
                "2.0,SECRET_123,powermetrics,gpu_power,1.0,2.0\n")
            stage1 = {"input_sha256": "a" * 64,
                      "legs": [{"leg_key": self.KEY, "span_id": "synthetic-span", "in_energy_fit": True}]}
            with self.assertRaises(F.LookInputError) as raised:
                R.read_segment_energy(stage1, lambda _: Path(d))
            msg = str(raised.exception)
            self.assertIn(self.KEY, msg)
            self.assertIn("power_trace.csv", msg)
            self.assertIn("gap unavailable", msg)
            self.assertNotIn("SECRET_123", msg)

    def test_nonpositive_measured_leg_names_leg_and_channel_without_values(self):
        li, energy, _ = synth.build("exact")
        s1 = F.stage1(li, hashlib.sha256(synth.dump(li)).hexdigest())
        key = next(x["leg_key"] for x in s1["legs"] if x["in_energy_fit"])
        entry = energy["legs"][key]["gpu_rail"]
        entry["segments"] = [0.0] * len(entry["segments"])
        with self.assertRaises(F.LookInputError) as raised:
            F.stage2(s1, hashlib.sha256(F.dump(s1)).hexdigest(), energy)
        msg = str(raised.exception)
        self.assertIn(key, msg)
        self.assertIn("gpu_rail", msg)
        self.assertIn("R-18", msg)


if __name__ == "__main__":
    unittest.main()
