"""Execute the unchanged V2 suite and the independent RL-187 hand vectors."""

from contextlib import contextmanager
from dataclasses import replace
from hashlib import sha256
from importlib import import_module
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
NS = 10**9
KERNEL_COMMIT = "82542232dbb7459b0320c37380925e9372afb7e8"
KERNEL_FILES = (
    "align/__init__.py", "align/apple/__init__.py", "align/apple/rl176_phases.py",
    "align/records.py", "align/attribution.py", "align/power/__init__.py", "align/power/windows.py",
)
HAND_SUMS = "e6204aa10c440a661ed1ca92c98f54df757bc975746f88c221b0d90a6add01ab"
V2_DIGEST = "031a7c3f1b9d1bed4a52b6e2e7f2534b50c3c5484852575d0eb561e891b7a92c"
CHANNEL = {"gpu": "gpu_rail", "cpu": "cpu_rail", "rail_sum": "rail_sum", "dc_in": "dc_in"}


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


@contextmanager
def frozen_kernel():
    sys.path.insert(0, str(ROOT))
    import joulewise

    with TemporaryDirectory() as directory:
        overlay = Path(directory)
        for name in KERNEL_FILES:
            path = overlay / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(subprocess.check_output(
                ["git", "show", f"{KERNEL_COMMIT}:joulewise/{name}"], cwd=ROOT
            ))
        # Prepend the phase, codec and integration source as a single pinned package.
        joulewise.__path__.insert(0, str(overlay))
        try:
            yield
        finally:
            joulewise.__path__.remove(str(overlay))


def numbers(value):
    return value["value"] if isinstance(value, dict) and "exact" in value else value


def series(end, spec):
    samples = [spec["level"]] * (end + 1)
    if spec["excess"] != "none":
        for item in spec["excess"].split(", "):
            indices, _, excess = item.partition(":")
            ends = [int(token) for token in indices.split("-")]
            for second in range(ends[0], ends[-1] + 1):
                samples[second] += float(excess)
    return samples


def episode_leg(key, inputs):
    end = inputs["episode"][1]
    gate_end = inputs["g0_gate"][1]
    specs = inputs["traces"]
    traces = {name: series(end, spec) for name, spec in specs.items() if isinstance(spec, dict)}
    if "rail_sum" in specs:
        traces["rail_sum"] = [sum(x) for x in zip(traces["cpu"], traces["gpu"], traces["ane"], strict=True)]
    if isinstance(specs.get("dc_in"), str):
        traces["dc_in"] = [power + 6 for power in traces["rail_sum"]]
    native_traces = tuple(v2.rec.PowerTrace(*v2.analysis.TRACE_CHANNELS[CHANNEL[name]], "toy",
                                          tuple(t * NS for t in range(end + 1)), tuple(values), "W", NS)
                          for name, values in traces.items() if name in CHANNEL)
    steps = []
    for data in inputs["physical_steps"]:
        kind = {"visible_call": "turn", "hidden_call": "hidden"}.get(data["kind"], data["kind"])
        row = dict(kind=kind, started_ns=data["start"] * NS, ended_ns=data["end"] * NS,
                   complete=data.get("complete", data.get("delivered") == data.get("requested")))
        if kind in ("turn", "hidden"):
            row.update(first_token_ns=data["first_token"] * NS, actual_tokens=data["delivered"],
                       requested_tokens=data["requested"], context_tokens=data["context_tokens"])
        else:
            row.update(requested_s=inputs.get("kit_recovery_s", data["end"] - data["start"])
                       if kind == "recovery" else data["end"] - data["start"])
        steps.append(row)
    envelope = inputs["logged_envelope"]
    turn = v2.rec.Turn(0, envelope["start"] * NS, envelope["end"] * NS, 0, envelope["prompt_tokens"],
                       envelope["decode_tokens"], hidden_tokens=envelope["hidden_tokens"],
                       first_token_ns=envelope["first_token"] * NS)
    # The native episode starts at G0 release. The oracle lists G0 in its
    # full timeline. The frozen integrator excludes exactly that prefix.
    episode = v2.rec.Episode(key, "invented", "benign", "toy", "toy", 0, "toy", gate_end * NS, end * NS,
                             (turn,), power_traces=native_traces)
    payload = v2.blob(dict(schema="joulewise.cadence_script_work.v1", leg_id=key,
                           script={"kind": inputs["kind"]}, steps=steps))
    return v2.analysis.LegInput(key, inputs["kind"], True, True, episode, payload, v2.SHA(payload))


class TestIndependentHandVectors(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if digest(HERE / "SHA256SUMS") != HAND_SUMS:
            raise AssertionError("oracle checksum manifest changed")
        if digest(HERE / "test_ctl01_print_v2.py") != V2_DIGEST:
            raise AssertionError("V2 test source changed")
        entries = dict(line.split()[::-1] for line in (HERE / "SHA256SUMS").read_text().splitlines())
        if digest(HERE / "hand_vectors.json") != entries["hand_vectors.json"]:
            raise AssertionError("independent hand-vector bytes changed")
        cls.cases = {row["id"]: row for row in json.loads((HERE / "hand_vectors.json").read_bytes())["vectors"]}

    def number(self, actual, expected):
        expected = numbers(expected)
        if expected is None:
            self.assertIsNone(actual)
        else:
            self.assertAlmostEqual(actual, expected, places=9)

    def compare_table(self, table, baseline, expected):
        for phase, operands in expected["phases"].items():
            for key, value in operands.items():
                actual = (table["phases"][phase]["joules"] - baseline * table["phases"][phase]["seconds"]
                          if key == "above_baseline_J" and baseline is not None else
                          None if key == "above_baseline_J" else table["phases"][phase][key])
                self.number(actual, value)
        for key, name in (("phase_sum_J", "phase_sum_j"), ("absolute_error_j", "absolute_error_j"),
                          ("relative_error", "relative_error")):
            self.number(table[name], expected[key])
        self.assertIs(table["closes"], expected["closes"])

    def pooled(self, data):
        pool = v2.analysis.pool_hold_windows([], set())
        pool.update({(CHANNEL[channel], int(window)): (numbers(value), ())
                     for channel, windows in data.items() for window, value in windows.items()})
        return pool

    def fits(self, short=()):
        from copy import deepcopy

        vector = self.cases["V4"]["inputs"]["channel_gpu_hidden_call_above_baseline_J"]
        change = self.cases["V5"]["inputs"]["change"]
        legs = []
        for row in vector:
            inputs = deepcopy(self.cases["V3"]["inputs"])
            delivered = (change["delivered"] if row["leg"] == change["leg"] else row["delivered"] - 1
                         ) if row["leg"] in short else row["delivered"]
            inputs["physical_steps"][0].update(delivered=delivered, requested=row["delivered"])
            prefill, decode = row["prefill_part_J"], row["decode_part_J"]
            inputs["traces"]["gpu"]["excess"] = f"31:+{prefill}, 34:+{decode}"
            inputs["traces"]["dc_in"]["excess"] = f"31:+{2*prefill+5}, 34:+{2*decode}"
            legs.append(episode_leg(row["leg"], inputs))
        return v2.pri(v2.roster(*legs))

    def check_fit(self, actual, expected):
        self.number(actual["slope"], expected["slope_J_per_token"])
        self.number(actual["intercept"], expected["intercept_J"])
        for found, want in zip(actual["range"], expected["range"], strict=True):
            self.number(found, want)

    def test_V1_cpu_episode_and_call_view(self):
        vector = self.cases["V1"]
        leg = episode_leg("L003", vector["inputs"])
        row = v2.one(leg)
        self.assertEqual(row["disposition"], "admitted")
        for ch, expected in vector["expected"]["channels"].items():
            with self.subTest(channel=ch):
                channel = row["channels"][CHANNEL[ch]]
                baseline = numbers(expected["baseline_W"])
                self.number(channel["baseline_w"], baseline)
                self.number(channel["absolute"]["ungated_j"], expected["whole_ungated_J"])
                logged = v2.KERNEL.phases.phase_table(leg.episode, v2.analysis.TRACE_CHANNELS[CHANNEL[ch]])
                self.compare_table(logged, baseline, expected["envelope"])
                self.compare_table(channel["absolute"], baseline, expected["view"])
                for part, spans in expected["view"]["other_split"].items():
                    for key, value in spans.items():
                        self.number(channel["other"].get(part, {}).get(key, 0), value)

    def test_V2_absolute_closure(self):
        leg = episode_leg("L003", self.cases["V1"]["inputs"])
        for row in self.cases["V2"]["expected"]:
            with self.subTest(case=row["case"]):
                def energy(key):
                    return v2.EnergyEstimate(numbers(row[key]), 0, "toy", ())

                segment = v2.SegmentEnergy(None, "gap", leg.episode.start_ns, leg.episode.end_ns,
                                           energy("phase_sum_J"))
                attrs = v2.EpisodeAttribution(leg.episode.episode_id, "cpu_power", energy("whole_J"),
                                              (segment,), ())
                result = v2.KERNEL.phases.phase_table(leg.episode, v2.KERNEL.phases.CPU, attrs)
                self.number(result["absolute_error_j"], row["absolute_error_j"])
                self.number(result["relative_error"], row["relative_error"])
                self.assertIs(result["closes"], row["closes"])

    def test_V3_hidden_baseline_and_floor(self):
        vector = self.cases["V3"]
        leg = episode_leg("L005", vector["inputs"])
        row = v2.one(leg, pooled=self.pooled(self.cases["V8"]["inputs"]["pooled_floors_W"]))
        for ch, expected in vector["expected"].items():
            channel = row["channels"][CHANNEL[ch]]
            self.number(channel["baseline_w"], expected["baseline_W"])
            self.number(channel["baseline_drift_j"] / 40, expected["check_prior40_minus_baseline_W"])
            self.number(channel["baseline_drift_floor"]["units"], expected["check_in_40s_floor_units"])
            self.number(channel["hidden"]["j_per_token"], expected["joules_per_delivered_hidden_token"])
            self.assertIs(channel["hidden"]["tail_cut"], expected["tail_cut"])
            for part in ("call", "prefill", "decode"):
                expected_phase = expected["hidden_" + part]
                amount = channel["hidden"][part + "_j"]
                self.number(amount, expected_phase["above_baseline_J"])
                self.number(amount + channel["baseline_w"] * expected_phase["seconds"], expected_phase["absolute_J"])
                floor = (channel["hidden"]["floor"] if part == "call" else
                         channel["other"]["hidden_" + part]["floor"])
                expect_floor = expected["floor_units_secondary"][part]
                self.assertEqual(floor["window_s"], expect_floor["w_star_s"])
                self.assertIs(floor["under_shortest_window"], expect_floor["under_shortest_window"])
                self.number(floor["floor_j"], expect_floor["floor_J"])
                self.number(floor["units"], expect_floor["floor_units"])

    def test_V4_six_leg_fit(self):
        vector = self.cases["V4"]
        result = self.fits()
        for ch in ("gpu", "dc_in"):
            self.check_fit(result["dose_response"][CHANNEL[ch]], vector["expected"][ch])
        expected = vector["expected"]["gpu"]
        by_leg = {row["leg_id"]: row for row in result["legs"]}
        for leg_id, rate in expected["per_leg_joules_per_delivered_token"].items():
            self.number(by_leg[leg_id]["channels"]["gpu_rail"]["hidden"]["j_per_token"], rate)
        points = {row["leg"]: (row["delivered"], row["E_J"])
                  for row in vector["inputs"]["channel_gpu_hidden_call_above_baseline_J"]}
        for key, slope in expected["loo_slopes"].items():
            self.number(v2.analysis._ols(tuple(val for leg, val in points.items() if key != leg))[0], slope)

    def test_V5_short_delivery(self):
        vector = self.cases["V5"]["expected"]
        doc = self.fits(("L009",))
        fit = doc["dose_response"]["gpu_rail"]
        self.check_fit(fit, vector["gpu"])
        self.assertEqual(set(fit["legs"]), set(vector["fit_over"]))
        row = doc["legs"][8]
        call = next(step for step in row["calls"] if step["kind"] == "hidden")
        expected = vector["L009_row"]
        self.assertEqual((row["delivery"], call["requested_tokens"], call["delivered_tokens"]),
                         (expected["delivery"], expected["requested"], expected["delivered"]))
        self.number(row["channels"]["gpu_rail"]["hidden"]["j_per_token"],
                    expected["joules_per_delivered_token"])
        self.assertTrue(row["channels"]["gpu_rail"]["absolute"]["closes"])
        fit = self.fits(("L002", "L009"))["dose_response"]["gpu_rail"]
        expected = vector["V5b_both_512_short"]
        self.assertEqual((fit["slope"], fit["range"], fit["reason"], len(fit["legs"])),
                         (expected["slope"], expected["range"], expected["reason"], expected["contributing"]))

    def test_V6_recovery_and_reason_precedence(self):
        vector = self.cases["V6"]
        leg = episode_leg("L005", vector["inputs"])
        row = v2.one(leg)["channels"]["gpu_rail"]
        expected = vector["expected"]["gpu"]
        self.assertIsNone(row["baseline_w"])
        self.assertEqual(row["baseline_reason"], expected["baseline_reason"])
        table = row["absolute"]
        self.number(table["ungated_j"], expected["whole_ungated_J"])
        self.compare_table(table, None, expected)
        for part, amount in expected["other_split_J"].items():
            self.number(row["other"].get(part, {}).get("joules", 0), amount)
        self.assertIsNone(row["hidden"]["j_per_token"])
        self.assertEqual(row["hidden"]["floor"]["reason"], expected["baseline_reason"])

        # Probe a baseline-window gap, then the same gap in the preceding window.
        complete = episode_leg("L005", self.cases["V3"]["inputs"])
        for removed, baseline_reason, check_reason in (
            ((240, 241), "gap_over_u1", None), ((200, 201), None, "gap_over_u1"),
        ):
            trace, *others = complete.episode.power_traces
            samples = [(t, p) for t, p in zip(trace.t_ns, trace.values, strict=True) if t // NS not in removed]
            trace = replace(trace, t_ns=tuple(t for t, _ in samples), values=tuple(p for _, p in samples))
            ep = replace(complete.episode, power_traces=(trace, *others))
            gpu = v2.one(replace(complete, episode=ep))["channels"]["gpu_rail"]
            self.assertEqual(gpu["baseline_reason"], baseline_reason)
            if check_reason:
                self.assertEqual(gpu["baseline_drift_floor"]["reason"], check_reason)
                self.assertEqual(gpu["baseline_w"], 4)

    def test_V7_pooled_floors(self):
        vector = self.cases["V7"]
        rows = []
        members = set()
        for width, inputs in vector["inputs"]["hold_rows"].items():
            for row in inputs:
                if row["stage1_qualified"]:
                    member = ("invented", "a" * 64, row["leg"])
                    members.add(member)
                    rows.append(v2.analysis.HoldWindow(member, "gpu_rail", int(width),
                                                       row["retained_windows"], numbers(row["sd_W"])))
        pooled = v2.analysis.pool_hold_windows(rows, members)
        for window, sd in vector["expected"]["pooled_sd_W"].items():
            self.number(pooled["gpu_rail", int(window)][0], sd)
        for row in vector["expected"]["rows"]:
            result = v2.analysis.floor_units(numbers(vector["inputs"]["value_J"]), numbers(row["T_s"]),
                                             "gpu_rail", pooled, "a" * 64)
            self.assertEqual(result["window_s"], row["w_star_s"])
            self.assertIs(result["under_shortest_window"], row["under_shortest_window"])
            self.number(result["floor_j"], row["floor_J"])
            self.number(result["units"], row["floor_units"])

    def test_V8_above_baseline_floor_and_cpu(self):
        vector = self.cases["V8"]
        leg = episode_leg("L003", self.cases["V1"]["inputs"])
        row = v2.one(leg, pooled=self.pooled(vector["inputs"]["pooled_floors_W"]))
        for ch, expected in vector["expected"].items():
            other = row["channels"][CHANNEL[ch]]["other"]["cpu"]
            self.number(other["joules"], expected["absolute_J"])
            self.number(other["above_baseline_j"], expected["above_baseline_J"])
            self.number(other["floor"]["floor_j"], expected["floor_J"])
            self.number(other["floor"]["units"], expected["floor_units"])
            if ch == "cpu":
                self.assertEqual(other["floor"]["reason"], expected["floor_units_reason"])

    def test_V9_strict_absolute_cpu_order(self):
        from copy import deepcopy

        vector = self.cases["V9"]
        for case, expected in vector["expected"].items():
            exercises = vector["inputs"]["legs"]["9a" if case == "9c_tie" else case]
            legs = {leg.leg_id: leg for leg in v2.complete()}
            for entry in exercises:
                dose, excess = entry["dose_s"], entry["x_W"]
                key = next(leg for leg, seconds in v2.BURNS.items() if seconds == dose)
                inputs = deepcopy(self.cases["V1"]["inputs"])
                inputs["episode"][1] = 180 + dose
                inputs["physical_steps"][1]["end"] = 40 + dose
                for step in inputs["physical_steps"][2:]:
                    for stamp in ("start", "end", "first_token"):
                        if stamp in step:
                            step[stamp] += dose - 30
                inputs["logged_envelope"]["end"] = 60 + dose
                # In 9c a one-second interior pulse supplies the exact tie.
                burn = "41:+350" if dose == 10 and case == "9c_tie" else f"41-{39+dose}:+{excess}"
                inputs["traces"]["cpu"]["excess"] = f"21-24:+1, 26-39:+1, {burn}, {41+dose}:+1, {43+dose}-{59+dose}:+1"
                inputs["traces"]["gpu"]["excess"] = "none"
                legs[key] = episode_leg(key, inputs)
            result = v2.pri(v2.roster(*legs.values()))
            for key, dose in v2.BURNS.items():
                cpu = result["legs"][v2.v1.IDS.index(key)]["channels"]["cpu_rail"]
                self.number(cpu["absolute"]["phases"]["other"]["joules"], expected["cpu_other_J_by_dose"][str(dose)])
                if "cpu_other_above_baseline_J_by_dose" in expected:
                    self.number(cpu["above_baseline_j"]["other"], expected["cpu_other_above_baseline_J_by_dose"][str(dose)])
            self.assertEqual(result["aligned_power"], {key: expected[key] for key in
                             ("all_legs_close", "cpu_burn_order", "qualified")})


if __name__ == "__main__":
    with frozen_kernel():
        v2 = import_module("test_ctl01_print_v2")
        suite = unittest.TestSuite((
            unittest.defaultTestLoader.loadTestsFromModule(v2),
            unittest.defaultTestLoader.loadTestsFromTestCase(TestIndependentHandVectors),
        ))
        runner = unittest.TextTestRunner(verbosity=2)
        raise SystemExit(not runner.run(suite).wasSuccessful())
