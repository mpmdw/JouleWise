"""Table-driven file-fault agreement on compact, production-shaped synthetic archives."""
from __future__ import annotations

from contextlib import chdir, contextmanager, redirect_stderr, redirect_stdout
import errno
import hashlib
import io
import json
from pathlib import Path
import plistlib
import shutil
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from joulewise.desk_restore import StorageStop
from joulewise.b6.acceptance import evidence_from_archive
from scripts import bytes_analyze, bytes_commitment, bytes_twin
from tests import test_bytes_agreement as agreement
from tests.bytes_commitment_support import commitment_fixture
from tests.desk_restore_support import compress_member

TABLE = agreement.FIXTURES / "availability_contract.json"
CONTRACT = {row["id"]: row for row in json.loads(TABLE.read_text())}
FAULTS = ("absent", "zero", "half", "garbage")
PHASES = ("before_export", "after_export")
MODEL = "Qwen3-8B-4bit"
SESSION = "bytes-s2-p1"


@contextmanager
def file_fault(path, fault):
    original = path.read_bytes() if path.is_file() else None
    if fault == "absent":
        path.unlink(missing_ok=True)
    else:
        damage = {"zero": b"", "half": (original or b"")[:len(original or b"") // 2],
                  "garbage": b"\xffbroken input\n"}
        path.write_bytes(damage[fault])
    try:
        yield
    finally:
        if original is None:
            path.unlink(missing_ok=True)
        else:
            path.write_bytes(original)


class AvailabilityFixture:
    def __init__(self, root, timing):
        self.root = root
        self.manifest_path = root / "manifest.json"
        uncollected = tuple(f"bytes-s{subpack}-p{p}" for subpack in range(1, 7) for p in (1, 2)
                            if f"bytes-s{subpack}-p{p}" != SESSION)
        with patch("os.fsync", return_value=None):
            self.manifest = agreement.archive_campaign(
                root, non_claim=False, release="none", subpack_sessions=True,
                uncollected_sessions=uncollected, anchor_profile="narrow" if timing == "native" else None)
        agreement._write(self.manifest_path, self.manifest)
        self.archive = Path(self.manifest["sessions"][0]["archive"])
        self.member = agreement._run_ids(self.archive, self.manifest["models"], MODEL)[20]
        self.bundle = self.archive / "sources/claim-runs" / self.member
        # The library selects dispatch by reading a finalized summary when one exists.
        agreement._write(self.bundle / "summary_metrics.json", {"summary_provenance": {"reducer_version": "0.5.2"}})
        roster = agreement.load(self.archive / "derived/roster.json")["members"]
        self.evidence = SimpleNamespace(runtime={}, session_id=SESSION, stages=[SimpleNamespace(members=[
            SimpleNamespace(**member, status="succeeded", config_key="fixture") for member in roster])])
        self.private = root / "private-keys/bytes/blinding"
        self.keys = root / "released-keys/bytes/blinding"
        for path in self.private.glob("*.json"):
            shutil.copyfile(path, self.keys / path.name)
        self.export = self.export_path(root / "export")
        self.stream = self.archive / "sources/night-custody/hazards/meter/stream-001.jsonl"

    @staticmethod
    def export_path(output):
        return next(output.rglob(f"{SESSION}.runs.csv"))

    def targets(self, export, *, keys=None):
        keys = self.keys if keys is None else keys
        model = next(m for m in self.manifest["models"] if m["model"] == MODEL)
        sidecar = export.with_name(f"{SESSION}.session.json")
        withheld = agreement.load(sidecar)["blinding"]["withheld"]["path"]
        return {**{row_id: self.bundle / filename for row_id, filename in (
                    ("config", "config.json"), ("metadata", "metadata.json"), ("events", "events.jsonl"),
                    ("trace", "power_trace.csv"), ("status", "status.json"), ("summary", "summary_metrics.json"))},
                "reduction": self.archive / "withheld/reductions" / (self.member + ".summary_metrics.rereduced.json"),
                "roster": self.archive / "derived/roster.json", "acceptance": self.archive / "derived/b6-acceptance.json",
                "flags": self.archive / "derived/flags.jsonl", "meter": self.stream,
                "harvest_receipt": self.archive / "harvest.json", "source_inventory": self.archive / "sources/SHA256SUMS",
                "manifest": self.manifest_path, "export_csv": export, "export_sidecar": sidecar,
                "withheld_csv": export.parent / withheld, "pack_key": keys / "pack.json",
                "config_key": keys / agreement.blinding._config_filename(model["config_key"])}

    def export_again(self, destination, private, *, read_registration=False, grouped=True):
        pack = {"blinding_group": "bytes", "bytes_pass": 1} if grouped else {"pack_id": SESSION}
        with patch("os.fsync", return_value=None):
            agreement.export_runs.export(self.archive, {}, self.root / "registration", private, destination,
                                         evidence=self.evidence, pack_registration=None if read_registration else pack)
        return self.export_path(destination), private / ("bytes" if grouped else SESSION) / "blinding"

    def compare(self, test, export, keys, scratch, *, stage="fit", expect_kept=None):
        modes = {"fit": "1", "heldout": "2", "blinded": "blinded"}
        try:
            manifest = agreement.ba.validate_manifest(agreement.ba.read_json(self.manifest_path))
            passes, _ = bytes_analyze._reduce([export.parents[1]], manifest, stage, keys)
            primary_status = 0
        except (StorageStop, OSError, ValueError, KeyError, TypeError, AttributeError):
            primary_status = 1
        output = scratch / "twin.json"
        output.unlink(missing_ok=True)
        # The test checks the table-reader seam after synthetic key release. The end-to-end
        # agreement suite separately checks the CLI commitment gate.
        if stage == "heldout":
            twin_status, twin = self.heldout_twin(export, keys)
        else:
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                twin_status = bytes_twin.main(["--export-dir", str(export.parents[1]), "--manifest", str(self.manifest_path),
                    "--archive", str(self.archive), "--key-dir", str(keys), "--stage", modes[stage], "--out", str(output)])
            twin = agreement.load(output) if twin_status == 0 else None
        recorder = agreement.Recorder()
        recorder.exact(stage, "stage", "refusal", primary_status, twin_status)
        if primary_status == twin_status == 0:
            if stage == "heldout":
                twin["cells"] = {model: block for model, block in twin["cells"].items() if model not in bytes_twin.FIT_SET}
            agreement.compare_cells(recorder, stage, passes, twin)
            agreement.compare_neg8(recorder, stage, passes, twin)
        counts = recorder.counts()
        test.assertEqual(counts["above_bar"], 0, [(row["group"], row["key"]) for row in recorder.above()[:14]])
        if expect_kept is not None:
            member_cells = [row for row in recorder.rows if row["key"] == "kept_runs"
                            and row["group"].startswith(f"cell/{bytes_twin.canon(MODEL)}/pass1/")]
            test.assertTrue(member_cells)
            for row in member_cells:
                test.assertEqual((self.member in row["a"], self.member in row["t"]), (expect_kept, expect_kept))
        return counts["compared"]

    def heldout_twin(self, export, keys):
        try:
            manifest = bytes_twin.read_manifest(self.manifest_path)
            sidecar = bytes_twin.read_sidecar(export)
            store = bytes_twin.load_withheld(export, sidecar, manifest)
            rows = (bytes_twin.read_export(export) if export.is_file() else []) + store["rows"]
            archive = bytes_twin.load_archive(self.archive)
            result = bytes_twin.analyse(rows, manifest, [archive], stage="2", key_dir=keys,
                sidecars={SESSION: sidecar}, listed={SESSION: self.manifest["sessions"][0]},
                withheld={SESSION: store}, synthetic=True)
            return 0, result
        except (bytes_twin.StorageStop, OSError, ValueError, KeyError, TypeError, AttributeError):
            return 1, None


class BytesAvailabilityTests(unittest.TestCase):
    def exercise(self, timing, rows, *, phases=PHASES, faults=FAULTS, expect_kept=None):
        compared = checked = export_stops = 0
        with tempfile.TemporaryDirectory(prefix=f"bytes-availability-{timing}-") as directory:
            root = Path(directory)
            fixture = AvailabilityFixture(root / "base", timing)
            targets = fixture.targets(fixture.export)
            for row_id in rows:
                self.assertEqual(tuple(CONTRACT[row_id]["faults"]), FAULTS)
                for fault in faults:
                    for phase in phases:
                        with self.subTest(timing=timing, file=row_id, fault=fault, phase=phase):
                            checked += 1
                            scratch = root / f"{row_id}-{fault}-{phase}"
                            scratch.mkdir()
                            heldout = row_id in {"export_sidecar", "withheld_csv"}
                            stage = "heldout" if heldout else "fit"
                            if phase == "after_export":
                                with file_fault(targets[row_id], fault):
                                    compared += fixture.compare(self, fixture.export, fixture.keys, scratch,
                                                                stage=stage, expect_kept=expect_kept)
                                continue
                            out = scratch / "export"
                            private = scratch / "private"
                            target = targets[row_id]
                            if row_id in {"export_csv", "export_sidecar", "withheld_csv"}:
                                target = out / target.relative_to(fixture.root / "export")
                                target.parent.mkdir(parents=True)
                            if row_id in {"pack_key", "config_key"}:
                                shutil.copytree(fixture.root / "private-keys", private)
                                target = private / "bytes/blinding" / target.name
                            with file_fault(target, fault):
                                try:
                                    export, keys = fixture.export_again(out, private)
                                except (StorageStop, OSError, ValueError, KeyError, TypeError) as exc:
                                    self.assertIn(row_id, {"events", "roster", "acceptance", "flags", "harvest_receipt",
                                                              "source_inventory", "pack_key", "config_key"}, type(exc).__name__)
                                    export_stops += 1
                                    continue
                                compared += fixture.compare(self, export, keys, scratch, stage=stage, expect_kept=expect_kept)
        print(f"\nBYTES {timing} availability: {checked} cases, {export_stops} export refusals, "
              f"{compared} comparisons", flush=True)

    def test_mock_timing_member_faults(self):
        self.exercise("mock", (row_id for row_id, row in CONTRACT.items() if row["scope"] == "member"))

    def test_native_timing_member_faults(self):
        self.exercise("native", (row_id for row_id, row in CONTRACT.items() if row["scope"] == "member"))

    def test_mock_timing_campaign_faults(self):
        self.exercise("mock", (row_id for row_id, row in CONTRACT.items() if row["scope"] == "campaign"))

    def test_native_timing_campaign_faults(self):
        self.exercise("native", (row_id for row_id, row in CONTRACT.items() if row["scope"] == "campaign"))

    def test_unreadable_reduction_drops_native_science_member(self):
        self.exercise("native", ["reduction"], phases=("after_export",), faults=("zero", "half"), expect_kept=False)

    def test_unavailable_native_trace_keeps_explicit_synthetic_summary(self):
        self.exercise("native", ["trace"], phases=("after_export",), faults=("absent", "half"), expect_kept=True)

    def test_bundle_restored_after_export_supplies_unblinded_science_record(self):
        for timing in ("mock", "native"):
            with self.subTest(timing=timing), tempfile.TemporaryDirectory(prefix="bytes-bundle-return-") as directory:
                root = Path(directory)
                fixture = AvailabilityFixture(root / "base", timing)
                held = root / "temporarily-absent-bundle"
                fixture.bundle.rename(held)
                try:
                    export, keys = fixture.export_again(root / "export", root / "private", grouped=False)
                finally:
                    held.rename(fixture.bundle)
                exported, = [row for row in bytes_twin.read_export(export) if row["run_id"] == fixture.member]
                self.assertIsNone(exported["model_name"])
                self.assertEqual(exported["status"], "succeeded")
                self.assertGreater(fixture.compare(self, export, keys, root, expect_kept=True), 100)

    def test_export_absences_repaired_before_analysis(self):
        compared = checked = 0
        for timing in ("mock", "native"):
            with tempfile.TemporaryDirectory(prefix=f"bytes-repaired-files-{timing}-") as directory:
                root = Path(directory)
                fixture = AvailabilityFixture(root / "base", timing)
                targets = fixture.targets(fixture.export)
                rows = [row_id for row_id, row in CONTRACT.items() if row["scope"] == "member"] + ["meter"]
                for row_id in rows:
                    with self.subTest(timing=timing, file=row_id):
                        scratch = root / row_id
                        scratch.mkdir()
                        with file_fault(targets[row_id], "absent"):
                            export, keys = fixture.export_again(scratch / "export", scratch / "private", grouped=False)
                        compared += fixture.compare(self, export, keys, scratch, expect_kept=True)
                        checked += 1
        print(f"\nBYTES restored export inputs: {checked} cases, {compared} comparisons", flush=True)

    def check_control_files(self, timing):
        with tempfile.TemporaryDirectory(prefix=f"bytes-availability-controls-{timing}-") as directory:
            root = Path(directory)
            fixture = AvailabilityFixture(root / "base", timing)
            archive = fixture.archive
            capture = archive / "sources/pre-calibration"
            controls = {
                "raw_powermetrics": (fixture.bundle / "raw/powermetrics.plist", b"synthetic inactive capture"),
                "cal_manifest": (fixture.bundle / "validation-manifest.json", b'{"artifacts": {}}'),
                "cal_evidence": (fixture.bundle / "instrument_evidence.json", b'{"status":"valid"}'),
                "cal_members": (fixture.bundle / "calibration/events.jsonl", b'{"fixture_event":true}\n'),
                "member_assessments": (archive / "withheld/member-assessments.json", b'{"members": {}}'),
                "export_registration": (archive / "sources/pack/registration.json",
                    json.dumps({"pack_id": SESSION, "blinding_group": "bytes", "bytes_pass": 1}).encode()),
                "export_key_binding": (fixture.private.parent / "blinding-sessions" / f"{SESSION}.json", None),
                "smoke_witness": (archive / "sources/pack/smoke-registered-tree.json", b'{"stage_graph":[]}'),
                "spans": (archive / "withheld/spans.json", b'{"spans": {}}'),
                "chain_journal": (archive / "night/chain-stages.jsonl", b'{"stage_id":"chain.complete","exit_code":0}\n'),
                "chain_result": (archive / "night/result.json", b'{"chain_exit_code":0}'),
                "neg8_screen": (archive / "withheld/b6-neg8.json", b'{"verdict":"synthetic"}'),
                "capture_evidence": (capture / "instrument_evidence.json", b'{"b_fiducial_s":0.04}'),
                "capture_raw": (capture / "raw/powermetrics.plist", b"synthetic optional capture"),
            }
            self.assertEqual(set(controls) | {"compression", "registered_manifest"}, {
                row_id for row_id, row in CONTRACT.items() if row["scope"].startswith("conditional_")})
            for file, seed in controls.values():
                if seed is not None:
                    file.parent.mkdir(parents=True, exist_ok=True)
                    file.write_bytes(seed)
            before_evidence = {"spans", "chain_journal", "chain_result", "neg8_screen", "capture_evidence", "capture_raw"}
            cases = compared = 0
            for row_id, (file, _) in controls.items():
                for fault in CONTRACT[row_id]["faults"]:
                    for phase in PHASES:
                        with self.subTest(timing=timing, file=row_id, fault=fault, phase=phase):
                            cases += 1
                            if phase == "before_export" and row_id in before_evidence:
                                # This is the producer's optional-evidence reader; the twin starts at its export.
                                with file_fault(file, fault):
                                    evidence = evidence_from_archive(archive, {"pre_calibration_dir": str(capture)}, root)
                                self.assertEqual(evidence.pack_id, SESSION)
                                compared += 1
                                continue
                            scratch = root / f"{row_id}-{fault}-{phase}"
                            scratch.mkdir()
                            if phase == "before_export" and row_id in {"member_assessments", "export_registration",
                                                                      "export_key_binding", "smoke_witness"}:
                                private = scratch / "private"
                                shutil.copytree(fixture.root / "private-keys", private)
                                target = (private / "bytes/blinding-sessions" / f"{SESSION}.json"
                                          if row_id == "export_key_binding" else file)
                                with file_fault(target, fault):
                                    if row_id == "export_key_binding" and fault != "absent":
                                        with self.assertRaises(ValueError):
                                            fixture.export_again(scratch / "export", private)
                                        compared += 1
                                        continue
                                    export, keys = fixture.export_again(scratch / "export", private,
                                                                          read_registration=row_id == "export_registration")
                                    compared += fixture.compare(self, export, keys, scratch)
                            else:
                                # These paths are conditional on the producer or native hardware path.
                                # Exercise their absence from this synthetic science reader, too.
                                with file_fault(file, fault):
                                    compared += fixture.compare(self, fixture.export, fixture.keys, scratch)
            print(f"\nBYTES {timing} optional controls: {cases} cases, {compared} comparisons", flush=True)

    def test_mock_timing_control_faults(self):
        self.check_control_files("mock")

    def test_native_timing_control_faults(self):
        self.check_control_files("native")

    def check_admission(self, timing):
        with tempfile.TemporaryDirectory(prefix=f"bytes-availability-admission-{timing}-") as directory:
            root = Path(directory)
            fixture = AvailabilityFixture(root / "base", timing)
            repo, prediction, receipt, commit = commitment_fixture(root)
            journal = repo / bytes_commitment.JOURNAL
            release = root / "release.json"
            release.write_text('{"stage":"fit"}')
            journal.write_text("\n\n")
            source = repo / "joulewise/bytes_analysis.py"
            locator = {"prediction": (prediction, prediction.with_suffix(".sha256")), "push_receipt": (receipt,),
                       "journal": (journal,), "release_record": (release,), "source_digests": (source,)}
            self.assertEqual(set(locator), {row_id for row_id, row in CONTRACT.items() if row["scope"] == "commitment"})
            original_blob = bytes_commitment._blob

            def blob(tree, revision, path, **kwargs):
                if path == "joulewise/bytes_analysis.py":
                    return source.read_bytes()
                return original_blob(tree, revision, path, **kwargs)

            comparisons = 0
            for row_id, files in locator.items():
                for file in files:
                    for fault in CONTRACT[row_id]["faults"]:
                        for phase in PHASES:
                            with self.subTest(timing=timing, file=file.name, fault=fault, phase=phase):
                                expected = (row_id == "journal" and fault in {"zero", "half"}
                                            or row_id == "release_record" and fault == "absent")
                                with file_fault(file, fault), patch.object(bytes_commitment, "ROOT", repo), patch.object(
                                        bytes_commitment, "_blob", side_effect=blob):
                                    if phase == "before_export":
                                        scratch = root / f"{file.name}-{fault}-{phase}"
                                        fixture.export_again(scratch / "export", scratch / "private")
                                    if expected:
                                        bytes_commitment.verify_commitment(commit, prediction, repo=repo,
                                                                                receipt=receipt, unblinding_records=(release,))
                                    else:
                                        with self.assertRaises((OSError, ValueError, KeyError, TypeError)):
                                            bytes_commitment.verify_commitment(commit, prediction, repo=repo,
                                                                                    receipt=receipt, unblinding_records=(release,))
                                comparisons += 1
            print(f"\nBYTES {timing} shared admission: {comparisons} file-fault comparisons", flush=True)

    def test_mock_timing_admission_faults(self):
        self.check_admission("mock")

    def test_native_timing_admission_faults(self):
        self.check_admission("native")

    def test_registered_manifest_file_faults(self):
        checked = 0
        for timing in ("mock", "native"):
            with tempfile.TemporaryDirectory(prefix="bytes-registered-manifest-") as directory:
                root = Path(directory)
                fixture = AvailabilityFixture(root / "base", timing)
                registered = root / "configs/bytes/bytes_manifest.json"
                registered.parent.mkdir(parents=True)
                shutil.copyfile(agreement.ROOT / "configs/bytes/bytes_manifest.json", registered)
                for fault in CONTRACT["registered_manifest"]["faults"]:
                    for phase in PHASES:
                        with self.subTest(timing=timing, fault=fault, phase=phase):
                            scratch = root / f"{fault}-{phase}"
                            scratch.mkdir()
                            with file_fault(registered, fault):
                                export, keys = ((fixture.export, fixture.keys) if phase == "after_export" else
                                                fixture.export_again(scratch / "export", scratch / "private"))
                                agreement.ba._registered_predictors.cache_clear()
                                try:
                                    with chdir(root), patch.object(agreement.ba, "__file__", root / "joulewise/bytes_analysis.py"), \
                                            patch.object(bytes_twin, "__file__", root / "scripts/bytes_twin.py"):
                                        self.assertEqual(fixture.compare(self, export, keys, scratch), 1)
                                        checked += 1
                                finally:
                                    agreement.ba._registered_predictors.cache_clear()
        print(f"\nBYTES registered manifest: {checked} file-fault comparisons", flush=True)

    @unittest.skipUnless(shutil.which("zstd"), "compressed-file fault matrix needs zstd")
    def test_compressed_member_and_journal_faults(self):
        compared = checked = export_stops = 0
        for timing in ("mock", "native"):
            with tempfile.TemporaryDirectory(prefix="bytes-compression-faults-") as directory:
                root = Path(directory)
                fixture = AvailabilityFixture(root / "base", timing)
                member = fixture.bundle / "events.jsonl"
                compress_member(member, fixture.archive)
                journal = Path(str(fixture.archive) + ".desk") / "compression.jsonl"
                for file in (journal, member.with_suffix(".jsonl.zst")):
                    for fault in CONTRACT["compression"]["faults"]:
                        for phase in PHASES:
                            with self.subTest(timing=timing, file=file.name, fault=fault, phase=phase):
                                checked += 1
                                scratch = root / f"{file.name}-{fault}-{phase}"
                                scratch.mkdir()
                                with file_fault(file, fault):
                                    try:
                                        export, keys = ((fixture.export, fixture.keys) if phase == "after_export" else
                                                        fixture.export_again(scratch / "export", scratch / "private"))
                                    except OSError as exc:
                                        self.assertEqual(file.suffix, ".zst")
                                        self.assertEqual(exc.errno, errno.EIO)
                                        export_stops += 1
                                    else:
                                        compared += fixture.compare(self, export, keys, scratch)
        print(f"\nBYTES compressed inputs: {checked} cases, {export_stops} export refusals, {compared} comparisons", flush=True)

    def test_native_reader_authenticates_each_required_capture_input(self):
        with tempfile.TemporaryDirectory(prefix="bytes-native-availability-") as directory:
            bundle = Path(directory)
            calibration = bundle / "calibration"
            processor = {**{rail + "_power": 1000.0 for rail in ("cpu", "gpu", "ane")},
                         **{rail + "_energy": 1000 for rail in ("cpu", "gpu", "ane")}}
            frame = plistlib.dumps({"timestamp": "2026-11-01T10:00:00Z", "elapsed_ns": 1_000_000_000,
                                    "processor": processor})
            capture = frame + b"\0" + frame

            def artifact(path, raw):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(raw)
                return hashlib.sha256(raw).hexdigest()

            capture_file = bundle / "raw/powermetrics.plist"
            artifact(capture_file, capture)
            hashes = {"raw/powermetrics.plist": artifact(calibration / "raw/powermetrics.plist", capture),
                      "events.jsonl": artifact(calibration / "events.jsonl", b'{"event_type":"synthetic"}\n')}
            evidence = calibration / "instrument_evidence.json"
            evidence_sha = artifact(evidence, json.dumps({"artifact_sha256": hashes}).encode())
            manifest = calibration / "manifest.json"
            manifest_sha = artifact(manifest, json.dumps({"artifacts": {**hashes, evidence.name: evidence_sha}}).encode())
            metadata = {"device": {"telemetry": "powermetrics"}, "instrument_calibration": {
                "validation_manifest_path": "calibration/manifest.json", "validation_manifest_sha256": manifest_sha,
                "artifact_path": "calibration/instrument_evidence.json", "artifact_sha256": evidence_sha}}
            trace = [(0.0, 1.0, 3.0), (1.0, 2.0, 3.0)]
            bytes_twin._verify_native_trace(trace, bytes_twin._native_science_inputs(bundle, metadata, "0.5.2"))
            files = {"raw_powermetrics": capture_file, "cal_manifest": manifest, "cal_evidence": evidence,
                     "cal_members": calibration / "events.jsonl"}
            for row_id, file in files.items():
                for fault in CONTRACT[row_id]["faults"]:
                    with self.subTest(file=row_id, fault=fault), file_fault(file, fault), \
                            self.assertRaises((ValueError, OSError)):
                        inputs = bytes_twin._native_science_inputs(bundle, metadata, "0.5.2")
                        bytes_twin._verify_native_trace(trace, inputs)
