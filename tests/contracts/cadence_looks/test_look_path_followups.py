"""Synthetic regressions for the pre-reservation audit findings."""

import json
import os
from pathlib import Path
import runpy
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import Mock, patch

from joulewise.cadence_looks import controls_book as book
from joulewise.cadence_looks import controls_layout as layout
from joulewise.cadence_looks import controls_reader as reader
from joulewise.cadence_looks import controls_time_fields as blind
from tests.contracts.cadence_looks import look_path_driver as registrar


FROZEN = runpy.run_path(str(Path(__file__).with_name("look_path") / "suite/run_suite.py"))
CHANNELS = b"REFUSE PREFLIGHT INPUT_CHANNELS\n"
OFFLINE_BOOTSTRAP = """
import runpy
import sys
def offline():
    raise OSError("synthetic offline")
main = runpy.run_path(sys.argv[1])["main"]
main.__globals__["_public_tip"] = offline
raise SystemExit(main(["stage2"]))
"""


def mutate(world, role, fault):
    span, runtime, bundle = FROZEN["location"](world, "L002")
    path = {
        "stream": FROZEN["meter"](span),
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
        path.write_bytes(b"".join(registrar.manifest.canonical(row) + b"\n"
                                  for row in (header, poll, trailer)))
    elif role == "rails":
        path.write_bytes(fault(path.read_bytes()))
    elif role == "script":
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


class LookPathFollowupTests(TestCase):
    @classmethod
    def setUpClass(cls):
        temporary = TemporaryDirectory(prefix="ctl01-followups-")
        cls.addClassCleanup(temporary.cleanup)
        cls.base = Path(temporary.name).resolve()
        cls.pristine = cls.base / "pristine"
        FROZEN["unpack"](cls.pristine)

    def prepare(self, name, *, role=None, fault=None):
        root = self.base / name
        world, bench = root / "source", root / "bench"
        shutil.copytree(self.pristine, world)
        for parent in ("private", "public"):
            (bench / parent / registrar.LOOK).mkdir(parents=True, mode=0o700)
        if role is not None:
            mutate(world, role, fault)
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

    def test_structural_faults_refuse_stage1_and_preflight_fresh(self):
        good_world, good_bench = self.prepare("good")
        self.assertEqual(self.invoke(good_world, good_bench, "stage1"), (0, b"", b""))
        self.assertEqual(self.invoke(good_world, good_bench, "commit-stage1"), (0, b"", b""))
        self.assertEqual(self.invoke(good_world, good_bench, "preflight"), (0, b"", b""))

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
            ("script-duplicate", "script", b',"extra":{"nested":[{"a":0,"\\u0061":1}]}}\n'),
            ("script-nonfinite", "script", b',"extra":{"nested":[NaN]}}\n'),
        )
        for name, role, fault in faults:
            with self.subTest(fault=name):
                world, bench = self.prepare(name, role=role, fault=fault)
                self.assertEqual(self.invoke(world, bench, "stage1"), (2, b"", CHANNELS))
                # A synthetic registrar supplies a committed prior roster. The
                # invalid inputs are already pinned in this world's Check so
                # preflight must reach structure validation, not a hash error.
                for basename in ("stage1.json", "inputs.v1.json"):
                    shutil.copy2(self.private(good_bench) / basename, self.private(bench) / basename)
                self.assertEqual(self.invoke(world, bench, "commit-stage1"), (0, b"", b""))
                for operation in ("preflight", "stage2"):
                    self.assertEqual(self.invoke(world, bench, operation), (2, b"", CHANNELS))
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
        launcher.write_bytes(launcher.read_bytes() + b"\n")
        (bench / "public" / registrar.LOOK).rename(bench / "missing-public")

        registrar.put(private / layout.MARKER_NAME, dict(marker, inode=marker["inode"] + 1), mode=0o600)
        self.assertEqual(self.bootstrap_offline(repo), (2, b"", b"REFUSE PREFLIGHT FREEZE\n"))
        registrar.put(private / layout.MARKER_NAME, marker, mode=0o600)
        self.assertEqual(self.bootstrap_offline(repo), (3, b"", b"REFUSE SPENT\n"))
        self.assertEqual(registrar.read(private / layout.MARKER_NAME), marker)
        self.assertEqual(list(reservation.iterdir()), [])
        self.assertFalse((bench / "events.jsonl").exists())
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
