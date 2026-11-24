"""Synthetic regressions for the pre-reservation audit findings."""

import json
import os
from pathlib import Path
import runpy
import shutil
import stat
import subprocess
import sys
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import Mock, patch

from joulewise.cadence_looks import controls_analysis as analysis
from joulewise.cadence_looks import controls_book as book
from joulewise.cadence_looks import controls_inputs as inputs
from joulewise.cadence_looks import controls_layout as layout
from joulewise.cadence_looks import controls_reader as reader
from joulewise.cadence_looks import controls_release as release
from joulewise.cadence_looks import controls_time_fields as blind
from tests.contracts.cadence_looks import look_path_driver as registrar


FROZEN = runpy.run_path(str(Path(__file__).with_name("look_path") / "suite/run_suite.py"))
CHANNELS = b"REFUSE PREFLIGHT INPUT_CHANNELS\n"
BINDING = b"REFUSE PREFLIGHT INPUT_BINDING\n"
FREEZE = b"REFUSE PREFLIGHT FREEZE\n"
OFFLINE_BOOTSTRAP = """
import runpy
import sys
def offline():
    raise OSError("synthetic offline")
main = runpy.run_path(sys.argv[1])["main"]
main.__globals__["_public_tip"] = offline
raise SystemExit(main(["stage2"]))
"""


def mutate(world, role, fault, *, leg="L002"):
    span, runtime, bundle = FROZEN["location"](world, leg)
    path = {
        "stream": FROZEN["meter"](span),
        "stream-order": FROZEN["meter"](span),
        "leg-record": runtime.parent / "leg_record.json",
        "episode": bundle / "outputs/align_episode.json",
        "config": bundle / "config.json",
        "metadata": bundle / "metadata.json",
        "rails": bundle / "power_trace.csv",
        "script": runtime / "script-work.json",
    }[role]
    if role == "stream":
        lines = path.read_bytes().splitlines()
        header, poll, trailer = map(json.loads, (lines[0], lines[1], lines[-1]))
        fault(header, poll)
        path.write_bytes(b"\n".join([
            registrar.manifest.canonical(header), registrar.manifest.canonical(poll),
            *lines[2:-1], registrar.manifest.canonical(trailer),
        ]) + b"\n")
    elif role == "stream-order":
        path.write_bytes(b"\n".join(fault(path.read_bytes().splitlines())) + b"\n")
    elif role == "rails":
        path.write_bytes(fault(path.read_bytes()))
    elif role == "script":
        if callable(fault):
            document = registrar.read(path)
            fault(document)
            registrar.put(path, document)
        else:
            path.write_bytes(path.read_bytes().rstrip()[:-1] + fault)
        pin = registrar.digest(path.read_bytes())
        result_path = runtime / "runtime_result.json"
        leg_path = runtime.parent / "leg_record.json"
        leg, result = registrar.read(leg_path), registrar.read(result_path)
        result["script_record_sha256"] = leg["result"]["script_record_sha256"] = pin
        registrar.put(result_path, result)
        registrar.put(leg_path, leg)
    else:
        document = registrar.read(path)
        fault(document)
        registrar.put(path, document)
        if role == "config":
            metadata = bundle / "metadata.json"
            registrar.put(metadata, dict(registrar.read(metadata), config_sha256=registrar.digest(path.read_bytes())))
    FROZEN["reanchor"](world, span)


def blind_values(world):
    def config_observations(document):
        document["synthetic_telemetry"] = {"power_w": 91827.375}
        document["run_metadata"]["ambient_temp_c"] = 19.8375

    mutate(world, "config", config_observations)
    span, runtime, _ = FROZEN["location"](world, "L002")
    receipt_path, record_path = span / "runner_receipt.json", runtime.parent / "leg_record.json"
    receipt, record = registrar.read(receipt_path), registrar.read(record_path)
    receipt_leg = next(row for row in receipt["legs"] if row["leg_id"] == "L002")
    for row in (receipt_leg, record):
        row["attempts"][0]["os_load"] = {"synthetic_observation": 91827.375}
    registrar.put(receipt_path, receipt)
    registrar.put(record_path, record)
    FROZEN["reanchor"](world, span)


def add_diagnostic_flag(document):
    document["flags"].append("task.synthetic_telemetry.power_w=91827.375")


def project_label(document):
    document["run_metadata"]["project"] = "JouleWise (synthetic ambient_temp_c=19.8375)"


def recovery_diagnostic(work):
    recovery = next(step for step in work["steps"] if step["kind"] == "recovery")
    recovery["first_token_ns"] = "no first token during recovery; synthetic power_w=91827.375"


def link_observation(config):
    config["interconnect"].update(name="synthetic test link", link_speed_mbps=91827.375)


def overlapping_support(raw):
    header, *lines = raw.splitlines()
    rows = [line.split(b",") for line in lines]
    stamps = sorted({row[0] for row in rows}, key=float)
    midpoint = stamps[len(stamps) // 2]
    for row in rows:
        if row[0] == midpoint:
            row[4] = str(float(row[4]) - 0.5).encode()
    return b"\n".join([header, *(b",".join(row) for row in rows)]) + b"\n"


def overflowing_counts(world, *, shape_only=False, decode=False):
    def work(record):
        visible = [step for step in record["steps"] if step["kind"] == "turn"]
        for step in visible:
            if decode:
                step.update(requested_tokens=10**308, actual_tokens=10**308)
            else:
                step["context_tokens"] = 10**308
        if shape_only:
            visible[-1]["first_token_ns"] = None

    def episode(record):
        if decode:
            record["turns"][0]["decode_tokens"] = 2 * 10**308
        else:
            record["turns"][0].update(context_tokens=0, prefill_tokens=2 * 10**308)

    mutate(world, "script", work, leg="L001")
    mutate(world, "episode", episode, leg="L001")


def duplicate_episode(world):
    _, _, bundle = FROZEN["location"](world, "L001")
    other = registrar.read(bundle / "outputs/align_episode.json")
    identity = {name: other[name] for name in ("episode_id", "clock_domain")}
    mutate(world, "episode", lambda episode: episode.update(identity))


def recorded_request(world, leg, kind, key, value):
    def change(work):
        next(row for row in work["steps"] if row["kind"] == kind)[key] = value

    mutate(world, "script", change, leg=leg)


def single_support(raw):
    header, *lines = raw.splitlines()
    latest = [line.split(b",") for line in lines[-3:]]
    start = lines[0].split(b",")[4]
    for row in latest:
        row[4] = start
    return b"\n".join([header, *(b",".join(row) for row in latest)]) + b"\n"


def rail_field(raw, index, value):
    header, first, *rest = raw.splitlines()
    fields = first.split(b",")
    fields[index] = value(fields) if callable(value) else value
    return b"\n".join([header, b",".join(fields), *rest]) + b"\n"


def conflicting_boot_ids(world):
    mutate(world, "episode", lambda d: d["hardware"].update(boot_id="synthetic-episode"))
    mutate(world, "metadata", lambda d: d.update(boot_id="synthetic-bundle"))


def bad_tool_interval(document):
    start = document["start_ns"]
    document["turns"][0]["tool_calls"] = [{
        "name": "synthetic", "start_ns": start + 1, "end_ns": start,
        "args_bytes": 0, "result_bytes": 0,
    }]


def interrupted_script(world):
    def interrupt(work):
        turn = next(row for row in work["steps"] if row["kind"] == "turn")
        work["steps"] = [work["steps"][0], {
            "kind": "turn", "complete": False, "actual_tokens": None,
            "requested_tokens": turn["requested_tokens"], "started_ns": turn["started_ns"],
        }]
        work["complete"] = False

    mutate(world, "script", interrupt)
    span, runtime, _ = FROZEN["location"](world, "L002")
    result_path = runtime / "runtime_result.json"
    record_path = runtime.parent / "leg_record.json"
    receipt_path = span / "runner_receipt.json"
    result, record, receipt = map(registrar.read, (result_path, record_path, receipt_path))
    receipt_leg = next(leg for leg in receipt["legs"] if leg["leg_id"] == "L002")
    for row in (result, record["result"]):
        row.update(script_complete=False, leg_status="incomplete")
    for row in (record, receipt_leg):
        row["attempts"][-1]["leg_status"] = "incomplete"
    receipt_leg["summary"]["admitted"] = False
    for path, document in zip((result_path, record_path, receipt_path), (result, record, receipt), strict=True):
        registrar.put(path, document)
    FROZEN["reanchor"](world, span)


class LookPathFollowupTests(TestCase):
    @classmethod
    def setUpClass(cls):
        temporary = TemporaryDirectory(prefix="ctl01-followups-")
        cls.addClassCleanup(temporary.cleanup)
        cls.base = Path(temporary.name).resolve()
        cls.pristine = cls.base / "pristine"
        FROZEN["unpack"](cls.pristine)

    def prepare(self, name, *, role=None, fault=None, configure=None):
        root = self.base / name
        world, bench = root / "source", root / "bench"
        shutil.copytree(self.pristine, world)
        for parent in ("private", "public"):
            (bench / parent / registrar.LOOK).mkdir(parents=True, mode=0o700)
        if role is not None:
            mutate(world, role, fault)
        if configure is not None:
            configure(world)
        self.assertEqual(self.invoke(world, bench, "install-v2"), (0, b"", b""))
        return world, bench

    @staticmethod
    def invoke(world, bench, operation, fault="none"):
        result = subprocess.run(
            [sys.executable, "-B", registrar.__file__, operation, str(world), str(bench), fault],
            capture_output=True, check=False,
        )
        return result.returncode, result.stdout, result.stderr

    @staticmethod
    def private(bench):
        return bench / "private" / registrar.LOOK

    def assert_fresh(self, world, bench):
        self.assertEqual(self.invoke(world, bench, "status"), (0, b"", b""))
        private = self.private(bench)
        self.assertFalse(os.path.lexists(private / layout.PRIVATE_NAME))
        self.assertFalse(os.path.lexists(private / layout.MARKER_NAME))
        self.assertEqual(list((bench / "public" / registrar.LOOK).iterdir()), [])
        self.assertFalse((bench / "events.jsonl").exists())

    @staticmethod
    def bootstrap_offline(repo):
        launcher = repo / registrar.manifest.CODE_PATHS["print_code/launcher"]
        result = subprocess.run([sys.executable, "-I", "-B", "-c", OFFLINE_BOOTSTRAP, str(launcher)],
                                capture_output=True, check=False)
        return result.returncode, result.stdout, result.stderr

    def stage_scaffold(self, name):
        good_world, good_bench = self.prepare(name)
        self.assertEqual(self.invoke(good_world, good_bench, "stage1"), (0, b"", b""))
        self.assertEqual(self.invoke(good_world, good_bench, "commit-stage1"), (0, b"", b""))
        self.assertEqual(self.invoke(good_world, good_bench, "preflight"), (0, b"", b""))
        return self.private(good_bench)

    def assert_refuses_at_blind_gates(self, world, bench, scaffold, *, token=CHANNELS,
                                     driver_fault="require_structural_cause"):
        self.assertEqual(self.invoke(world, bench, "stage1", driver_fault), (2, b"", token))
        # The synthetic commitment lets preflight reach the same structural
        # predicate even though the malformed world cannot produce a roster.
        for basename in ("stage1.json", "inputs.v1.json"):
            shutil.copy2(scaffold / basename, self.private(bench) / basename)
        self.assertEqual(self.invoke(world, bench, "commit-stage1"), (0, b"", b""))
        for operation in ("preflight", "stage2"):
            self.assertEqual(self.invoke(world, bench, operation, driver_fault), (2, b"", token))
        self.assert_fresh(world, bench)

    def test_structural_faults_refuse_stage1_and_preflight_fresh(self):
        scaffold = self.stage_scaffold("good")

        faults = (
            ("rate-missing", "stream", lambda h, p: h.pop("rate_idx")),
            ("rate-unknown", "stream", lambda h, p: h.update(rate_idx=99)),
            ("rate-float", "stream", lambda h, p: h.update(rate_idx=2.0)),
            ("status-missing", "stream", lambda h, p: h.pop("status")),
            ("status-invalid", "stream", lambda h, p: h.update(status="unknown")),
            ("smc-scalar", "stream", lambda h, p: p.update(smc=1)),
            ("smc-array", "stream", lambda h, p: p.update(smc=[])),
            ("smc-null", "stream", lambda h, p: p.update(smc=None)),
            ("empty-poll-rx", "stream", lambda h, p: (p.update(n=0, p=""), p.pop("rx"))),
            ("config-version", "config", lambda d: d.update(schema_version="invalid")),
            ("config-type", "config", lambda d: d.update(model=[])),
            ("episode-traces", "episode", lambda d: d.update(power_traces=[{"values": [123]}])),
            ("episode-mappings", "episode", lambda d: d.update(clock_mappings=[{}])),
            ("episode-schema", "episode", lambda d: d.update(schema="invalid")),
            ("episode-fields", "episode", lambda d: d.update(unexpected=True)),
            ("episode-flags", "episode", lambda d: d.update(flags=[[]])),
            ("episode-condition", "episode", lambda d: d.update(condition="invalid")),
            ("monitor-fields", "episode", lambda d: d.update(monitor_verdicts=[{"suspicion": 0}])),
            ("router-shape", "episode", lambda d: d.update(router_log=[])),
            ("turn-fields", "episode", lambda d: d["turns"][0].pop("index")),
            ("turn-counts", "episode", lambda d: d["turns"][0].update(prefill_tokens=-1)),
            ("turn-bounds", "episode", lambda d: d["turns"][0].update(start_ns=d["start_ns"] - 1)),
            ("tool-shape", "episode", lambda d: d["turns"][0].update(tool_calls=[[]])),
            ("rail-bound", "metadata", lambda d: d["uncertainty_evidence"]["clock_anchor"].update(
                effective_clock_anchor_bound_s="0.0001")),
            ("rail-columns", "rails", lambda raw: raw.replace(b",power_w,", b",wrong,", 1)),
            ("rail-support", "rails", lambda raw: raw.replace(b",cpu_power,", b",unknown,", 1)),
            ("rail-single-sample", "rails", single_support),
            ("thermal-missing-end", "episode", lambda d: d["hardware"].update(
                thermal={"intervals": [{"kind": "G0"}]})),
            ("thermal-object", "episode", lambda d: d["hardware"].update(thermal=[])),
            ("thermal-interval-list", "episode", lambda d: d["hardware"]["thermal"].update(intervals={})),
            ("thermal-entry", "episode", lambda d: d["hardware"]["thermal"]["intervals"].append(None)),
            ("thermal-kind", "episode", lambda d: d["hardware"]["thermal"]["intervals"][0].update(kind="invalid")),
            ("thermal-time", "episode", lambda d: d["hardware"]["thermal"]["intervals"][0].update(end_ns="1")),
            ("thermal-hold-turn", "episode", lambda d: d["hardware"]["thermal"]["intervals"][0].update(kind="H")),
            ("thermal-overlap", "episode", lambda d: d["hardware"]["thermal"]["intervals"].extend(
                d["hardware"]["thermal"]["intervals"][:1])),
            ("script-duplicate", "script", b',"extra":{"nested":[{"a":0,"\\u0061":1}]}}\n'),
            ("script-nonfinite", "script", b',"extra":{"nested":[NaN]}}\n'),
            ("script-missing-end", "script", lambda d: d["steps"][0].pop("ended_ns")),
            ("script-overflow-dose", "script", lambda d: d["steps"][-1].update(requested_s=10**309)),
            ("script-bool-dose", "script", lambda d: d["steps"][-1].update(requested_s=True)),
            ("script-missing-context", "script", lambda d: next(
                step for step in d["steps"] if step["kind"] == "turn").pop("context_tokens")),
            ("script-reversed-step", "script", lambda d: d["steps"][-1].update(
                ended_ns=d["steps"][-1]["started_ns"] - 1)),
        )
        for name, role, fault in faults:
            with self.subTest(fault=name):
                world, bench = self.prepare(name, role=role, fault=fault)
                self.assert_refuses_at_blind_gates(world, bench, scaffold)

    def test_stream_wire_prerequisites_at_both_blind_gates(self):
        scaffold = self.stage_scaffold("valid-meter")
        faults = (
            ("meter-schema", "stream", lambda h, p: h.update(schema="synthetic.unknown")),
            ("late-header", "stream-order", lambda rows: [rows[1], rows[0], *rows[2:]]),
            ("duplicate-header", "stream-order", lambda rows: [rows[0], *rows]),
            ("duplicate-trailer", "stream-order", lambda rows: [*rows, rows[-1]]),
            ("poll-after-trailer", "stream-order", lambda rows: [*rows, rows[1]]),
            ("sampled-tx-missing", "stream", lambda h, p: p.pop("tx")),
            ("sampled-count-mismatch", "stream", lambda h, p: p.update(n=p["n"] + 1)),
            ("count-without-payload", "stream", lambda h, p: p.pop("p")),
            ("payload-object", "stream", lambda h, p: p.update(p={})),
            ("nonhex-payload", "stream", lambda h, p: p.update(p="xy")),
            ("partial-packet", "stream", lambda h, p: p.update(p="00")),
        )
        for name, role, fault in faults:
            with self.subTest(fault=name):
                world, bench = self.prepare(name, role=role, fault=fault)
                self.assert_refuses_at_blind_gates(world, bench, scaffold)

    def test_bundle_and_work_prerequisites_at_both_blind_gates(self):
        scaffold = self.stage_scaffold("valid-bundle")
        faults = (
            ("config-cadence", "config", lambda d: d["sampling"].update(power_hz=0)),
            ("rail-manifest-duplicate", "metadata", lambda d: d["device"]["rail_manifest"].append("cpu_power")),
            ("rail-manifest-missing-member", "metadata", lambda d: d["device"]["rail_manifest"].remove("cpu_power")),
            ("episode-domain", "episode", lambda d: d.update(clock_domain="synthetic:other")),
            ("episode-zero-extent", "episode", lambda d: d.update(end_ns=d["start_ns"], turns=[])),
            ("stamp-missing-member", "episode", lambda d: d["hardware"]["paired_clock_stamps_ns"][0].pop(
                "wall_resolution_ns")),
            ("stamp-reversed-pair", "episode", lambda d: d["hardware"]["paired_clock_stamps_ns"][0].update(
                monotonic_before_ns=d["hardware"]["paired_clock_stamps_ns"][0]["monotonic_after_ns"] + 1)),
            ("tool-interval", "episode", bad_tool_interval),
            ("router-dimension", "episode", lambda d: d.update(router_log={
                "model": "synthetic", "num_experts": 2, "top_k": 1, "layers": [0],
                "phase": ["decode"], "experts": [[]],
            })),
            ("rail-row-width", "rails", lambda raw: raw + b"123\n"),
            ("rail-source", "rails", lambda raw: rail_field(raw, 2, b"synthetic")),
            ("rail-nonfinite-stamp", "rails", lambda raw: rail_field(raw, 0, b"nan")),
            ("rail-width", "rails", lambda raw: rail_field(raw, 4, lambda fields: fields[5])),
            ("rail-end-stamp", "rails", lambda raw: rail_field(raw, 0, lambda fields: fields[4])),
            ("rail-unequal-grid", "rails", lambda raw: b"\n".join(raw.splitlines()[:1] + raw.splitlines()[2:])),
            ("rail-duplicate-stamp", "rails", lambda raw: raw + raw.splitlines()[1] + b"\n"),
            ("rail-coverage", "rails", lambda raw: b"\n".join(raw.splitlines()[:1] + raw.splitlines()[301:])),
            ("thermal-only-end-missing", "episode", lambda d: d["hardware"]["thermal"]["intervals"][0].pop("end_ns")),
            ("script-order", "script", lambda d: d["steps"].reverse()),
            ("script-completion-type", "script", lambda d: d["steps"][0].update(complete=1)),
            ("script-first-token-bounds", "script", lambda d: d["steps"][0].update(
                first_token_ns=d["steps"][0]["ended_ns"] + 1)),
        )
        for name, role, fault in faults:
            with self.subTest(fault=name):
                world, bench = self.prepare(name, role=role, fault=fault)
                self.assert_refuses_at_blind_gates(world, bench, scaffold)
        world, bench = self.prepare("boot-id-conflict", configure=conflicting_boot_ids)
        self.assert_refuses_at_blind_gates(world, bench, scaffold)

    def test_authentication_and_candidate_refusals_at_both_blind_gates(self):
        scaffold = self.stage_scaffold("valid-auth")
        wired_faults = (
            ("run-id-mismatch", "metadata", lambda d: d.update(run_id="synthetic-other"), FREEZE),
            ("config-digest-mismatch", "metadata", lambda d: d.update(config_sha256="0" * 64), FREEZE),
            ("leg-attempt-mismatch", "leg-record", lambda d: d["attempts"][-1].update(attempt=2), BINDING),
            ("work-leg-mismatch", "script", lambda d: d.update(leg_id="L003"), BINDING),
        )
        for name, role, fault, token in wired_faults:
            with self.subTest(fault=name):
                world, bench = self.prepare(name, role=role, fault=fault)
                self.assert_refuses_at_blind_gates(world, bench, scaffold, token=token,
                                                  driver_fault="worker_entrypoint")
        for name, token in (("missing-pinned-role", CHANNELS), ("changed-pinned-payload", BINDING)):
            with self.subTest(fault=name):
                world, bench = self.prepare(name)
                _, _, bundle = FROZEN["location"](world, "L002")
                path = bundle / "power_trace.csv"
                if token == CHANNELS:
                    path.unlink()
                else:
                    path.write_bytes(path.read_bytes() + b"\n")
                self.assert_refuses_at_blind_gates(world, bench, scaffold, token=token, driver_fault="none")

        fixture_dir = Path(__file__).with_name("look_path")
        with patch.object(sys, "path", sys.path.copy()):
            v2 = runpy.run_path(str(fixture_dir / "suite-v2/fixtures.py"))
            with patch.dict(sys.modules, fixtures=SimpleNamespace(**v2)):
                v3 = runpy.run_path(str(fixture_dir / "suite-v3/bundle_cases.py"))
        profiles = v3["catalog"]()["profiles"]
        for name, configure in (
            ("boot-mismatch", lambda world: v2["make"](world, "boot_mismatch")),
            ("ambiguous-candidates", lambda world: v2["make"](world, "ambiguous_overlap")),
            ("absent-samples", lambda world: v3["materialize"](world, "absent_span", profiles["absent_span"])),
        ):
            with self.subTest(fault=name):
                world, bench = self.prepare(name, configure=configure)
                self.assert_refuses_at_blind_gates(world, bench, scaffold, driver_fault="none")

    def test_stage1_and_preflight_skip_config_and_receipt_observations(self):
        world, bench = self.prepare("blind-values", configure=blind_values)
        self.assertEqual(self.invoke(world, bench, "stage1", "guard_blind_values"), (0, b"", b""))
        self.assertEqual(self.invoke(world, bench, "commit-stage1"), (0, b"", b""))
        self.assertEqual(self.invoke(world, bench, "preflight", "guard_blind_values"), (0, b"", b""))
        self.assert_fresh(world, bench)

    def test_stage1_and_preflight_keep_diagnostic_flags_opaque(self):
        world, bench = self.prepare("blind-flags", role="episode", fault=add_diagnostic_flag)
        self.assertEqual(self.invoke(world, bench, "stage1", "guard_blind_values"), (0, b"", b""))
        self.assertEqual(self.invoke(world, bench, "commit-stage1"), (0, b"", b""))
        self.assertEqual(self.invoke(world, bench, "preflight", "guard_blind_values"), (0, b"", b""))
        self.assert_fresh(world, bench)

    def test_round3_structural_faults_refuse_fresh_at_three_entry_points(self):
        scaffold = self.stage_scaffold("round3-scaffold")
        cases = (
            ("count-sum", overflowing_counts),
            ("count-shape-only", lambda world: overflowing_counts(world, shape_only=True)),
            ("decode-sum", lambda world: overflowing_counts(world, decode=True)),
            ("rail-overlap", lambda world: mutate(world, "rails", overlapping_support)),
            ("duplicate-episode", duplicate_episode),
            ("cpu-dose", lambda world: recorded_request(world, "L003", "cpu", "requested_s", 10)),
            ("recovery-dose", lambda world: recorded_request(world, "L002", "recovery", "requested_s", 599)),
            ("turn-dose", lambda world: recorded_request(world, "L002", "turn", "requested_tokens", 4097)),
            ("blank-notes", lambda world: mutate(world, "config", lambda cfg: cfg["run_metadata"].update(notes=" "))),
            ("unicode-blank-notes", lambda world: mutate(
                world, "config", lambda cfg: cfg["run_metadata"].update(notes="\t\u2003\r"))),
        )
        for name, configure in cases:
            with self.subTest(name=name):
                world, bench = self.prepare("round3-" + name, configure=configure)
                self.assert_refuses_at_blind_gates(world, bench, scaffold)

    def test_descriptive_config_strings_are_validated_without_conversion(self):
        def other_labels(document):
            document["model"].update(name="\t synthetic 19.8375 \u2003", revision="19.8375")
            document["hardware_target"]["notes"] = "synthetic 91827.375"
            document["workload_profile"]["name"] = "synthetic 19.8375"
            document["run_metadata"]["tags"] = ["", "\t", "synthetic 91827.375"]

        for label, fault in (("project", project_label), ("other-labels", other_labels)):
            world, bench = self.prepare("opaque-" + label, role="config", fault=fault)
            with self.subTest(label=label, operation="stage1"):
                self.assertEqual(self.invoke(world, bench, "stage1", "guard_blind_values"), (0, b"", b""))
            self.assertEqual(self.invoke(world, bench, "stage1"), (0, b"", b""))
            self.assertEqual(self.invoke(world, bench, "commit-stage1"), (0, b"", b""))
            with self.subTest(label=label, operation="preflight"):
                self.assertEqual(self.invoke(world, bench, "preflight", "guard_blind_values"), (0, b"", b""))
            self.assert_fresh(world, bench)

    def test_native_script_completion_and_clock_bounds_refuse_fresh(self):
        scaffold = self.stage_scaffold("completion-clock-scaffold")

        def step_complete(world, leg, kind):
            def change(work):
                next(step for step in work["steps"] if step["kind"] == kind)["complete"] = False
            mutate(world, "script", change, leg=leg)

        def anchor(world, **changes):
            mutate(world, "metadata", lambda doc: doc["uncertainty_evidence"]["clock_anchor"].update(changes))

        def resolution(world, key, value):
            def change(episode):
                for stamp in episode["hardware"]["paired_clock_stamps_ns"]:
                    stamp[key] = value
            mutate(world, "episode", change)

        cases = (
            ("cpu-completion", lambda world: step_complete(world, "L003", "cpu")),
            ("call-completion", lambda world: step_complete(world, "L002", "turn")),
            ("recovery-completion", lambda world: step_complete(world, "L002", "recovery")),
            ("bound-negative", lambda world: anchor(world, effective_clock_anchor_bound_s=-0.25)),
            ("wall-resolution-negative", lambda world: resolution(world, "wall_resolution_ns", -250000000)),
            ("mono-resolution-masked-by-rounding", lambda world: resolution(world, "monotonic_resolution_ns", -1)),
            ("inverted-anchor-bracket", lambda world: anchor(world, wall_minus_monotonic_lower_s=18001)),
            ("link-negative", lambda world: mutate(
                world, "config", lambda cfg: cfg["interconnect"].update(link_speed_mbps=-0.25))),
            ("link-overflow", lambda world: mutate(
                world, "config", lambda cfg: cfg["interconnect"].update(link_speed_mbps=10**309))),
        )
        for name, configure in cases:
            with self.subTest(name=name):
                world, bench = self.prepare(name, configure=configure)
                self.assert_refuses_at_blind_gates(world, bench, scaffold)

    def test_inapplicable_script_fields_and_config_link_rate_are_opaque(self):
        cases = (("script-incidental", "script", recovery_diagnostic),
                 ("config-link-rate", "config", link_observation))
        for name, role, fault in cases:
            world, bench = self.prepare(name, role=role, fault=fault)
            with self.subTest(name=name, operation="stage1"):
                self.assertEqual(self.invoke(world, bench, "stage1", "guard_blind_values"), (0, b"", b""))
            self.assertEqual(self.invoke(world, bench, "stage1"), (0, b"", b""))
            self.assertEqual(self.invoke(world, bench, "commit-stage1"), (0, b"", b""))
            with self.subTest(name=name, operation="preflight"):
                self.assertEqual(self.invoke(world, bench, "preflight", "guard_blind_values"), (0, b"", b""))
            self.assert_fresh(world, bench)

    def test_step_projection_keeps_only_applicable_fields_independent_of_key_order(self):
        rows = [dict(first_token_ns={"synthetic": "opaque"}, requested_s=600, kind="recovery"),
                dict(kind="turn", requested_s="opaque", requested_tokens=4)]
        expected = {"steps": [{"kind": "recovery", "requested_s": 600},
                              {"kind": "turn", "requested_tokens": 4}]}
        original = blind._convert

        def checked(kind, text):
            self.assertNotIn("opaque", text)
            return original(kind, text)

        for sort_keys in (False, True):
            with patch.object(blind, "_convert", checked):
                raw = json.dumps({"steps": rows}, sort_keys=sort_keys).encode()
                self.assertEqual(blind.project_json(raw, inputs.WORK_FIELDS, strict=True), expected)

    def test_opaque_numeric_shape_preserves_binary64_boundaries(self):
        midpoint = 2**1024 - 2**970
        half_subnormal = 5**1075
        valid = (b"91827.375", b"-0.0", b"-1e-9999", str(midpoint - 1).encode(),
                 f"-{half_subnormal}e-1075".encode())
        invalid = (b"-0.25", str(midpoint).encode(), b"1e9999", b'"91827.375"',
                   f"-{half_subnormal + 1}e-1075".encode())
        with patch.object(blind, "_convert", side_effect=AssertionError("opaque value converted")):
            for raw in valid:
                with self.subTest(raw=raw):
                    self.assertEqual(blind.project_json(raw, blind.OPAQUE_NONNEGATIVE_NUMBER), 0)
            for raw in invalid:
                with self.subTest(raw=raw), self.assertRaises(blind.TimeFieldError):
                    blind.project_json(raw, blind.OPAQUE_NONNEGATIVE_NUMBER)
            self.assertEqual(blind.project_json(b"-0.25", blind.OPAQUE_FINITE_NUMBER), 0)

    def test_rail_edge_snapping_preserves_rounded_edges_and_gaps(self):
        def rows(start):
            for rail in reader.RAILS:
                yield "10", "opaque", "powermetrics", rail, "9", "10"
                yield "11", "opaque", "powermetrics", rail, start, "11"

        for start in ("9.999999999", "10", "10.01"):
            with self.subTest(start=start):
                self.assertEqual(len(reader._native_grid(rows(start))), 2)
        with self.assertRaises(blind.TimeFieldError):
            reader._native_grid(rows("9.999999998"))

    def test_aggregate_token_bounds_cover_both_totals_before_numerical_work(self):
        _, runtime, _ = FROZEN["location"](self.pristine, "L001")
        for count in ("context_tokens", "actual_tokens"):
            with self.subTest(count=count):
                work = registrar.read(runtime / "script-work.json")
                visible = [step for step in work["steps"] if step["kind"] == "turn"]
                for step in visible:
                    step[count] = 10**308
                    if count == "actual_tokens":
                        step["requested_tokens"] = step[count]
                visible[-1][count] = 10**307
                self.assertTrue(analysis.script_steps(work, work["script"]["kind"]))
                visible[-1][count] = 10**308
                with self.assertRaisesRegex(analysis.ViewError, "^aggregate_token_counts$"):
                    analysis.script_steps(work, work["script"]["kind"])
        with self.assertRaisesRegex(ValueError, "^controls_output_schema$"):
            release.validate_shape(2 * 10**308, {"type": "integer"}, {})

    def test_blind_stamp_disposition_and_opacity_survive_native_publication(self):
        def configure(world):
            blind_values(world)
            mutate(world, "config", project_label)
            mutate(world, "config", link_observation)
            mutate(world, "episode", add_diagnostic_flag)

            def mismatch(work):
                recovery_diagnostic(work)
                turn = next(step for step in work["steps"] if step["kind"] == "turn")
                turn["first_token_ns"] += 1

            mutate(world, "script", mismatch)

        world, bench = self.prepare("blind-publication", configure=configure)
        self.assertEqual(self.invoke(world, bench, "stage1", "guard_blind_values"), (0, b"", b""))
        self.assertEqual(self.invoke(world, bench, "commit-stage1"), (0, b"", b""))
        self.assertEqual(self.invoke(world, bench, "preflight", "guard_blind_values"), (0, b"", b""))
        self.assert_fresh(world, bench)
        result = self.invoke(world, bench, "stage2")
        if sys.platform == "darwin" and result == (2, b"", b"REFUSE PREFLIGHT CLAIM_SETUP\n"):
            self.assert_fresh(world, bench)
            self.skipTest("local runner cannot create the synthetic reservation directory")
        self.assertEqual(result, (0, b"", b""))

        private = self.private(bench)
        public_path = bench / "public" / registrar.LOOK / layout.PUBLIC_NAME
        self.assertEqual(registrar.read(public_path), registrar.read(bench / "registered-public.json"))
        for sentinel in (b"91827.375", b"19.8375"):
            self.assertNotIn(sentinel, public_path.read_bytes())
        report = registrar.read(private / layout.PRIVATE_NAME / "controls.json")
        rows = {row["leg_id"]: row for row in report["legs"]}
        self.assertEqual((rows["L002"]["disposition"], rows["L002"]["reason"]),
                         ("not_evaluable", "envelope_stamps"))
        self.assertEqual(sum("channels" in row for row in rows.values()), 11)
        certificate = registrar.read(private / "certificates/L002.json")
        joined = registrar.read(bench / "joined-observed.json")["L002"]
        self.assertEqual(joined, {
            "method": certificate["method"], "offset_ns": certificate["offset_ns"],
            "uncertainty_ns": certificate["H_ns"], "dc_times_sha256": certificate["dc_times_sha256"],
        })

    def test_blind_view_preserves_ruled_per_leg_dispositions(self):
        _, runtime, bundle = FROZEN["location"](self.pristine, "L002")
        episode = registrar.read(bundle / "outputs/align_episode.json")
        work = registrar.read(runtime / "script-work.json")
        kind = work["script"]["kind"]

        def reason():
            projected = reader.episode_timing(registrar.manifest.canonical(episode), {}).projected_episode
            return analysis.blind_view_refusal(projected, work, kind)

        self.assertIsNone(reason())
        turn = next(step for step in work["steps"] if step["kind"] == "turn")
        turn["first_token_ns"] += 1
        self.assertEqual(reason(), "envelope_stamps")
        turn["first_token_ns"] -= 1
        episode["start_ns"] -= 2
        episode["hardware"]["thermal"]["intervals"][0]["end_ns"] = episode["start_ns"] + 1
        self.assertEqual(reason(), "leg_record_invalid")

    def test_incomplete_script_allows_a_native_interrupted_tail(self):
        work = {"steps": [{"kind": "turn", "complete": False, "actual_tokens": None,
                           "requested_tokens": 64, "started_ns": 1}]}
        self.assertEqual(analysis.script_steps(work, "plain", allow_interrupted=True), (None,))
        work["steps"][0]["actual_tokens"] = 1
        with self.assertRaisesRegex(analysis.ViewError, "^script_record_shape$"):
            analysis.script_steps(work, "plain", allow_interrupted=True)

        world, bench = self.prepare("interrupted", configure=interrupted_script)
        self.assertEqual(self.invoke(world, bench, "stage1"), (0, b"", b""))
        self.assertEqual(self.invoke(world, bench, "commit-stage1"), (0, b"", b""))
        self.assertEqual(self.invoke(world, bench, "preflight"), (0, b"", b""))
        self.assert_fresh(world, bench)

    def test_blind_projection_skips_value_tokens(self):
        forbidden = "987654321"
        original = blind._convert

        def convert(kind, value):
            self.assertNotEqual(value, forbidden)
            return original(kind, value)

        with patch.object(blind, "_convert", convert):
            payload = b'{"clock":17,"cpu":{"thread_cpu_ns":987654321}}'
            self.assertEqual(blind.project_json(payload, {"clock": None}, strict=True), {"clock": 17})
            stream = (b'{"k":"h","schema":"joulewise.km003c_stream.v1","rate_idx":2,"status":"streaming"}\n'
                      b'{"k":"b","rx":1,"n":0,"p":"","smc":{"sensor":987654321}}\n')
            self.assertFalse(reader.blind_stream("synthetic", stream).present)
            _, _, bundle = FROZEN["location"](self.pristine, "L002")
            episode = registrar.read(bundle / "outputs/align_episode.json")
            episode["main_task_score"] = episode["hardware"]["ignored_sensor"] = int(forbidden)
            timing = reader.episode_timing(registrar.manifest.canonical(episode), {})
            rails = (bundle / "power_trace.csv").read_bytes().splitlines()
            masked = [rails[0]]
            for row in rails[1:]:
                fields = row.split(b",")
                fields[1] = b"opaque-value"
                masked.append(b",".join(fields))
            metadata = registrar.read(bundle / "metadata.json")
            evidence = metadata["uncertainty_evidence"]
            self.assertEqual(reader.rail_timing(b"\n".join(masked), timing, 100_000_000, evidence),
                             reader.rail_timing(b"\n".join(rails), timing, 100_000_000, evidence))

    def test_mkdir_denied_without_reservation_reports_claim_setup(self):
        world, bench = self.prepare("mkdir")
        self.assertEqual(self.invoke(world, bench, "stage1"), (0, b"", b""))
        self.assertEqual(self.invoke(world, bench, "commit-stage1"), (0, b"", b""))
        self.assertEqual(self.invoke(world, bench, "stage2", "mkdir_denied"),
                         (2, b"", b"REFUSE PREFLIGHT CLAIM_SETUP\n"))
        self.assert_fresh(world, bench)

    def test_unconfirmed_cleanup_preserves_half_made(self):
        with (patch.object(layout.os, "mkdir") as mkdir,
              patch.object(layout.os, "fsync", side_effect=OSError),
              patch.object(layout.os, "rmdir", side_effect=OSError) as rmdir,
              patch.object(layout, "_observation", side_effect=[None, OSError])):
            with self.assertRaises(layout.GateRefusal) as caught:
                layout.claim(123, 456, {}, Mock())
        mkdir.assert_called_once_with(layout.PRIVATE_NAME, 0o700, dir_fd=123)
        rmdir.assert_called_once_with(layout.PRIVATE_NAME, dir_fd=123)
        self.assertEqual((caught.exception.status, caught.exception.notice), (4, "REFUSE HALF_MADE\n"))

    def test_mkdir_collision_with_failed_restat_preserves_half_made(self):
        with (patch.object(layout.os, "mkdir", side_effect=FileExistsError),
              patch.object(layout, "_observation", side_effect=OSError),
              patch.object(layout.os, "rmdir") as rmdir):
            with self.assertRaises(layout.GateRefusal) as caught:
                layout.claim(123, 456, {}, Mock())
        rmdir.assert_not_called()
        self.assertEqual((caught.exception.status, caught.exception.notice), (4, "REFUSE HALF_MADE\n"))

    def test_regular_file_collision_agrees_with_freshness_check(self):
        entry = SimpleNamespace(st_mode=stat.S_IFREG | 0o600)
        with (patch.object(layout.os, "mkdir", side_effect=FileExistsError),
              patch.object(layout, "_observation", return_value=entry),
              patch.object(layout, "marker_valid", return_value=False)):
            for operation, call in (("claim", lambda: layout.claim(123, 456, {}, Mock())),
                                    ("status", lambda: layout.require_fresh(123, 456, []))):
                with self.subTest(operation=operation):
                    with self.assertRaises(layout.GateRefusal) as caught:
                        call()
                    self.assertEqual((caught.exception.status, caught.exception.notice), (4, "REFUSE HALF_MADE\n"))

    def test_claim_sync_failure_after_bound_marker_reports_spent_immediately(self):
        world, bench = self.prepare("marker-final-sync")
        self.assertEqual(self.invoke(world, bench, "stage1"), (0, b"", b""))
        self.assertEqual(self.invoke(world, bench, "commit-stage1"), (0, b"", b""))
        for operation in ("stage2", "status", "stage2"):
            with self.subTest(operation=operation):
                self.assertEqual(self.invoke(world, bench, operation, "marker_final_sync"),
                                 (3, b"", b"REFUSE SPENT\n"))
        self.assertTrue((self.private(bench) / layout.MARKER_NAME).is_file())
        self.assertEqual(list((bench / "public" / registrar.LOOK).iterdir()), [])
        self.assertEqual((bench / "events.jsonl").read_text().splitlines(), ['"claim"'])

    def test_bootstrap_reports_spent_before_source_layout_and_offline_checks(self):
        world, bench = self.prepare("spent")
        self.assertEqual(self.invoke(world, bench, "stage1"), (0, b"", b""))
        self.assertEqual(self.invoke(world, bench, "commit-stage1"), (0, b"", b""))
        repo = bench / "checkout"
        private = self.private(bench)
        reservation = private / layout.PRIVATE_NAME
        try:
            reservation.mkdir(mode=0o700)
        except PermissionError:
            self.skipTest("local runner cannot create the synthetic reservation directory")
        registered = registrar.read(bench / "registered-public.json")
        marker = {key: registered[key] for key in ("look_id", "manifest_sha256", "stage1_sha256")}
        document = registrar.read(repo / book.MANIFEST)
        registered_layout = document["release_layout"]["private"]
        marker.update(device=registered_layout["device"], inode=reservation.stat().st_ino)
        launcher = repo / registrar.manifest.CODE_PATHS["print_code/launcher"]
        original_launcher = launcher.read_bytes()
        launcher.write_bytes(original_launcher + b"\n")
        (bench / "public" / registrar.LOOK).rename(bench / "missing-public")

        registrar.put(private / layout.MARKER_NAME, dict(marker, inode=marker["inode"] + 1), mode=0o600)
        self.assertEqual(self.bootstrap_offline(repo), (2, b"", b"REFUSE PREFLIGHT FREEZE\n"))
        registrar.put(private / layout.MARKER_NAME, marker, mode=0o600)
        reservation.chmod(0o000)
        try:
            self.assertEqual(self.bootstrap_offline(repo), (3, b"", b"REFUSE SPENT\n"))
        finally:
            reservation.chmod(0o700)
        self.assertEqual(registrar.read(private / layout.MARKER_NAME), marker)
        self.assertEqual(list(reservation.iterdir()), [])
        self.assertFalse((bench / "events.jsonl").exists())
        launcher.write_bytes(original_launcher)
        (bench / "missing-public").rename(bench / "public" / registrar.LOOK)
        ledger_path = repo / book.LOOKS
        ledger = registrar.read(ledger_path)
        ledger["events"] = [entry for entry in ledger["events"] if entry["kind"] != "stage1"]
        registrar.put(ledger_path, ledger)
        registrar.commit(repo, "Synthetic successor drops marker binding")
        self.assertEqual(self.bootstrap_offline(repo), (3, b"", b"REFUSE SPENT\n"))
        old_device = registered_layout["device"] + 1
        registrar.put(private / layout.MARKER_NAME, dict(marker, device=old_device), mode=0o600)
        self.assertTrue(runpy.run_path(str(launcher))["_read_started"](
            dict(registered_layout, device=old_device), os.geteuid(),
            marker["manifest_sha256"], marker["stage1_sha256"],
        ))

    def test_committed_spend_reports_spent_offline_even_without_local_marker(self):
        _, bench = self.prepare("recorded-spend")
        repo = bench / "checkout"
        self.assertEqual(self.bootstrap_offline(repo), (2, b"", b"REFUSE PREFLIGHT FREEZE\n"))
        manifest_sha = registrar.digest((repo / book.MANIFEST).read_bytes())
        registrar.add_event(repo, "first_ctl_read", manifest_sha256=manifest_sha, stage1_sha256="a" * 64)
        self.assertEqual(self.bootstrap_offline(repo), (3, b"", b"REFUSE SPENT\n"))
        ledger_path = repo / book.LOOKS
        ledger = registrar.read(ledger_path)
        ledger["events"].pop()
        registrar.put(ledger_path, ledger)
        registrar.commit(repo, "Synthetic successor drops spend row")
        self.assertEqual(self.bootstrap_offline(repo), (3, b"", b"REFUSE SPENT\n"))
        ledger_path.unlink()
        registrar.commit(repo, "Synthetic successor drops ledger")
        self.assertEqual(self.bootstrap_offline(repo), (3, b"", b"REFUSE SPENT\n"))

    def test_byte_pass_requires_cumulative_disposition_receipt(self):
        _, bench = self.prepare("receipt")
        authority = book.Authority(book.Book(bench / "checkout"))
        authority._verify_byte_pass()
        revision, event = next((rev, event) for rev, event in authority.events if event["kind"] == "byte_pass")
        raw = authority.book.blob(revision, book.BYTE_RECEIPT)
        receipt = json.loads(raw)
        self.assertEqual(receipt["installed_bundle_cases"], "75 raw + 4 superseded "
                         "(RL-202a §2.4; lead record audit branch 1850d6930 SUPERSESSION-v2.md)")
        self.assertEqual(receipt["supersession_sha256"],
                         "1c4b7086a03487e1059748364e56061d1175614bf4a4d0c5ff304c542009325d")
        for change in ({"installed_bundle_cases": 79}, {"supersession_sha256": "0" * 64}):
            with self.subTest(change=change):
                changed = registrar.manifest.canonical(dict(receipt, **change))
                event["receipt_sha256"] = registrar.digest(changed)
                with patch.object(authority.book, "blob", Mock(return_value=changed)):
                    with self.assertRaisesRegex(layout.GateRefusal, "FREEZE"):
                        authority._verify_byte_pass()
