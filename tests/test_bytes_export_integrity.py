"""Synthetic regressions for the shared two-phase BYTES export seal."""
from contextlib import redirect_stderr, redirect_stdout
import hashlib
import io
from pathlib import Path
import shutil
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from joulewise.b6 import bytes_integrity as integrity
from scripts import bytes_analyze, bytes_commitment, bytes_stage1, bytes_twin
from tests.bytes_commitment_support import commitment_fixture
from tests.test_bytes_availability import AvailabilityFixture, SESSION, agreement, file_fault


class ExportIntegrityTests(unittest.TestCase):
    def test_export_capture_release_and_all_four_consumers(self):
        for timing in ("mock", "native"):
            with self.subTest(timing=timing), tempfile.TemporaryDirectory(prefix="bytes-export-seal-") as directory:
                self.check_fixture(Path(directory), timing)

    def check_fixture(self, root, timing):
        fixture = AvailabilityFixture(root / "inputs", timing, complete_fit=True)
        self.assertTrue(fixture.manifest["synthetic"])
        export = fixture.root / "export"
        private = fixture.root / "private-keys"
        bindings = fixture.private.parent / "blinding-sessions"
        binding = bindings / (SESSION + ".json")
        self.assertTrue((bindings / "bytes-s1-p1.json").is_file())
        with file_fault(binding, "absent"):
            with self.assertRaisesRegex(ValueError, "manifest: missing session binding"):
                fixture.export_again(root / "retry-export", private)
            with self.assertRaisesRegex(ValueError, "manifest: unexpected or missing bindings file"):
                integrity.capture(export, fixture.manifest_path, [export], private)

        baseline = root / "baseline"
        baseline.mkdir()
        self.assertGreater(fixture.compare(self, fixture.export, fixture.keys, baseline, fit_cli=True,
                                           expect_exit=0, expect_kept=True), 100)
        # Keep release artifacts out of the capture. Then simulate the existing
        # verbatim release into the unchanged fit key path.
        staged = root / "fixture-fit-release"
        fixture.keys.rename(staged)
        empty = root / "empty-keys"
        empty.mkdir()
        blank = fixture.archive / "derived/empty.sidecar"
        blank.touch()
        roster = fixture.archive / "derived/roster.json"
        original = roster.read_bytes()
        edited = agreement.load(roster)
        edited["members"] = [member for member in edited["members"] if member["run_id"] != fixture.member]
        try:
            agreement._write(roster, edited)
            with self.assertRaisesRegex(ValueError, "manifest: roster differs"):
                integrity.capture(export, fixture.manifest_path, [export], private)
        finally:
            roster.write_bytes(original)
        captured = integrity.capture(export, fixture.manifest_path, [export], private)
        capture_args = integrity.options(export, captured)

        first_args = ["--export", str(export), "--manifest", str(fixture.manifest_path), "--stage", "fit"]
        twin_args = ["--export-dir", str(export), "--manifest", str(fixture.manifest_path), "--stage", "1"]
        for archive in fixture.archives:
            twin_args += ["--archive", str(archive)]

        def run_fit(args, keys, outcome, *, twin=False):
            out = root / outcome
            stdout, stderr = io.StringIO(), io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                if twin:
                    result = bytes_twin.main(twin_args + args + ["--key-dir", str(keys), "--out", str(out)])
                else:
                    result = bytes_analyze.main(first_args + args + ["--key-dir", str(keys), "--out", str(out)])
            return result, stdout.getvalue(), stderr.getvalue()

        for tag, is_twin in (("a-fit-nokeys", False), ("t-1-nokeys", True)):
            status, stdout, stderr = run_fit(capture_args + ["--no-key-probe"], empty, "probe", twin=is_twin)
            (root / (tag + ".stdout")).write_text(stdout)
            (root / (tag + ".stderr")).write_text(stderr)
            self.assertEqual(status, 1)
        exits = dict.fromkeys(("a-fit-nokeys", "t-1-nokeys"), 1)
        self.assertTrue(bytes_stage1._expected_no_key_refusals(root, exits, empty, fixture.manifest))
        staged.rename(fixture.keys)
        self.assertEqual(run_fit(capture_args, fixture.keys, "no-final-primary")[0], 1)
        self.assertEqual(run_fit(capture_args, fixture.keys, "no-final-twin", twin=True)[0], 1)

        try:
            agreement._write(roster, edited)
            with self.assertRaisesRegex(ValueError, "manifest: changed input"):
                integrity.finalize(export, captured, fixture.keys)
        finally:
            roster.write_bytes(original)

        pack = fixture.keys / "pack.json"
        raw = pack.read_bytes()
        try:
            pack.write_bytes(raw + b" ")
            with self.assertRaisesRegex(ValueError, "released key differs"):
                integrity.finalize(export, captured, fixture.keys)
        finally:
            pack.write_bytes(raw)
        finalized = integrity.finalize(export, captured, fixture.keys)
        seal = integrity.options(export, finalized)
        self.assertEqual(run_fit(seal, fixture.keys, "primary")[0], 0)
        self.assertEqual(run_fit(seal, fixture.keys, "twin.json", twin=True)[0], 0)
        results = agreement.Recorder()
        primary = agreement.load(root / "primary/fit_pass_estimates.json")
        twin = agreement.load(root / "twin.json")
        agreement.compare_cells(results, "fit", primary, twin)
        agreement.compare_neg8(results, "fit", primary, twin)
        self.assertEqual(results.counts()["above_bar"], 0)
        for name in ("predictions.json", "predictions.sha256"):
            self.assertEqual((root / "primary" / name).read_bytes(), (baseline / "primary" / name).read_bytes())

        repo, predictions, receipt, commit = commitment_fixture(root, root / "primary/predictions.json")
        guard = {"export_seal_repo": export, "export_seal_commit": finalized}
        args = SimpleNamespace(stage1_commit=commit, commitment_repo=repo, predictions=predictions,
                               stage1_receipt=receipt, **guard)
        journal = repo / bytes_commitment.JOURNAL
        before = journal.read_bytes()

        def refuses(options, auth):
            with patch.object(bytes_analyze.ba, "read_json", side_effect=AssertionError("read after seal refusal")), \
                    patch.object(bytes_twin, "read_manifest", side_effect=AssertionError("read after seal refusal")), \
                    patch.object(bytes_commitment, "ROOT", repo):
                for is_twin in (False, True):
                    status, stdout, stderr = run_fit(options, fixture.keys, "refused", twin=is_twin)
                    self.assertEqual(status, 1)
                    self.assertIn("export manifest", stdout if is_twin else stderr)
                for command in (lambda: bytes_commitment.verify_commitment(commit, predictions, repo=repo, **auth),
                                lambda: bytes_commitment.admit(SimpleNamespace(**{**vars(args), **auth}), "heldout_rows")):
                    with self.assertRaisesRegex((OSError, ValueError), "export manifest"):
                        command()
            self.assertEqual(journal.read_bytes(), before)
            self.assertFalse((root / "refused").exists())

        document = integrity.verify(export, finalized)
        manifest = export / integrity.NAME
        original = manifest.read_bytes()
        with file_fault(manifest, "absent"):
            refuses(seal, guard)
        try:
            manifest.write_bytes(original + b" ")
            refuses(seal, guard)
        finally:
            manifest.write_bytes(original)
        extra = fixture.archive / "derived/extra"
        extra.touch()
        try:
            refuses(seal, guard)
        finally:
            extra.unlink()

        # Round 10 reproduction. The added whitespace leaves valid JSON
        # and the same parsed config, but changes one authenticated input.
        archive_inputs = {row["path"] for row in document["files"]
                          if row["root"] == f"fit_archive:{SESSION}"}
        self.assertIn((fixture.bundle / "config.json").relative_to(fixture.archive).as_posix(),
                      archive_inputs)
        self.assertIn(fixture.stream.relative_to(fixture.archive).as_posix(), archive_inputs)
        for path in (fixture.bundle / "config.json", fixture.targets(fixture.export)["reduction"], fixture.stream):
            original_input = path.read_bytes()
            try:
                path.write_bytes(original_input + b" ")
                refuses(seal, guard)
            finally:
                path.write_bytes(original_input)

        # Exercise malformed committed manifests, as well as local substitution
        # against a pinned commit. Neither case opens the declared escaped path.
        for fault in ("escape", "duplicate"):
            records = [dict(entry) for entry in document["files"]]
            if fault == "escape":
                records[0]["path"] = "../out-of-root"
            else:
                records.insert(0, records[0])
            new_commit = integrity._publish(export, {**document, "files": records})
            bad = {**guard, "export_seal_commit": new_commit}
            refuses(integrity.options(export, new_commit), bad)
            manifest.write_bytes(original)
        with patch.object(bytes_commitment, "ROOT", repo), redirect_stderr(io.StringIO()):
            bytes_commitment.verify_commitment(commit, predictions, repo=repo, **guard)
            bytes_commitment.admit(args, "heldout_rows")
        self.assertNotEqual(journal.read_bytes(), before)

    def test_every_finalized_input_is_protected_for_all_four_consumers(self):
        with tempfile.TemporaryDirectory(prefix="bytes-input-faults-") as directory:
            self.check_input_faults(Path(directory))

    def check_input_faults(self, root):
        # Build a compact fixture for the exhaustive matrix. The native and
        # mock campaign tests above also run clean fits using the larger trees.
        app = root / "fixture-checkout"
        checker = app / "joulewise/b6/bytes_integrity.py"
        checker.parent.mkdir(parents=True)
        shutil.copyfile(integrity.__file__, checker)
        export = root / "export"
        archive = root / "archive"
        campaign = root / "manifest.json"
        private = root / "private"
        keys = root / "fit-keys"
        models = [{"role": "fit", "config_key": "synthetic-fit", "cell_ids": ["fit-cell"]},
                  {"role": "heldout", "config_key": "synthetic-held", "cell_ids": ["held-cell"]}]

        def put(path, data):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)

        agreement._write(campaign, {"sessions": [{"session_id": "sim", "archive": str(archive)}],
                                    "models": models, "synthetic": True})
        roster = archive / "derived/roster.json"
        roster.parent.mkdir(parents=True)
        agreement._write(roster, {"members": [
            {"run_id": "fit", "role": "science", "units": [{"cell_id": "fit-cell"}]},
            {"run_id": "ref", "role": "corpus"},
            {"run_id": "held", "role": "science", "units": [{"cell_id": "held-cell"}]}]})
        agreement._write(archive / "harvest.json", {
            "outputs": {"derived/roster.json": hashlib.sha256(roster.read_bytes()).hexdigest()}})
        put(archive / "derived/empty", b"")
        put(export / "sim.runs.csv", b"run_id,role,cell_ids\nfit,science,fit-cell\nref,corpus,\n")
        digests = {}
        for name in ("pack.json", integrity._key_name("neg8_reference"), integrity._key_name("synthetic-fit")):
            put(keys / name, b"{}\n")
            digests[name] = hashlib.sha256(b"{}\n").hexdigest()
        agreement._write(export / "sim.session.json", {"blinding": {"key_sha256": digests}})
        (private / "bytes/blinding-sessions").mkdir(parents=True)
        agreement._write(private / "bytes/blinding-sessions/sim.json", {
            "session_id": "sim", "key_sha256": digests})

        bundle = archive / "sources/claim-runs/fit"
        fit_paths = (bundle / "config.json", bundle / "raw/powermetrics.plist",
                     bundle / "calibration/member.json", bundle / "outputs/request_tokens.jsonl",
                     archive / "sources/bound-runs/ref/metadata.json.zst",
                     archive / integrity.REDUCTIONS / "fit.summary_metrics.rereduced.json",
                     archive / integrity.REDUCTIONS / "fit.summary_metrics.rereduced.json.zst",
                     archive / integrity.METER_DIR / "stream-001.jsonl")
        for path in (*fit_paths, Path(str(archive) + ".desk") / "compression.jsonl",
                     app / "configs/campaign_policies/synthetic.json", app / "configs/bytes/bytes_manifest.json"):
            put(path, b"synthetic input\n")
        outside = (archive / "sources/claim-runs/held/config.json",
                   archive / integrity.REDUCTIONS / "held.summary_metrics.rereduced.json")
        for path in outside:
            put(path, b"synthetic outside the fit census\n")

        with patch.object(integrity, "ROOT", app), patch.object(bytes_twin, "__file__", app / "scripts/bytes_twin.py"):
            table = export / "sim.runs.csv"
            visible = table.read_bytes()
            try:
                table.write_bytes(visible + b"held,science,fit-cell\n")
                with self.assertRaisesRegex(ValueError, "unauthorized or duplicate fit table row"):
                    integrity.capture(export, campaign, [export], private)
            finally:
                table.write_bytes(visible)
            captured = integrity.capture(export, campaign, [export], private)
            finalized = integrity.finalize(export, captured, keys)
            document = integrity.verify(export, finalized)
            self.check_sealed_file_faults(root, export, campaign, archive, keys, finalized, document, fit_paths, outside)

    def check_sealed_file_faults(self, root, export, campaign, archive, keys, finalized, document, fit_paths, outside):
        repo, predictions, receipt, commit = commitment_fixture(root)
        before = (repo / bytes_commitment.JOURNAL).read_bytes()
        guard = {"export_seal_repo": export, "export_seal_commit": finalized}
        auth = SimpleNamespace(stage1_commit=commit, commitment_repo=repo, predictions=predictions,
                               stage1_receipt=receipt, **guard)
        seal = integrity.options(export, finalized)
        common = ["--manifest", str(campaign), "--key-dir", str(keys), "--out", str(root / "refused"), *seal]
        primary = ["--export", str(export), "--stage", "fit", *common]
        twin = ["--export-dir", str(export), "--archive", str(archive), "--stage", "1", *common]
        paths = [Path(document["roots"][row["root"]]["path"]) / row["path"] for row in document["files"]]
        self.assertLessEqual(set(fit_paths), set(paths))
        self.assertTrue(set(outside).isdisjoint(paths))

        def refuses():
            with patch.object(bytes_analyze.ba, "read_json", side_effect=AssertionError("read after seal refusal")), \
                    patch.object(bytes_twin, "read_manifest", side_effect=AssertionError("read after seal refusal")), \
                    patch.object(bytes_commitment, "ROOT", repo):
                messages = io.StringIO()
                with redirect_stdout(messages), redirect_stderr(messages):
                    self.assertEqual(bytes_analyze.main(primary), 1)
                    self.assertEqual(bytes_twin.main(twin), 1)
                self.assertEqual(messages.getvalue().count("BYTES export manifest:"), 2)
                with self.assertRaisesRegex((OSError, ValueError), "export manifest"):
                    bytes_commitment.verify_commitment(commit, predictions, repo=repo, **guard)
                with self.assertRaisesRegex((OSError, ValueError), "export manifest"):
                    bytes_commitment.admit(auth, "heldout_rows")
            self.assertEqual((repo / bytes_commitment.JOURNAL).read_bytes(), before)
            self.assertFalse((root / "refused").exists())

        for path in outside:
            with file_fault(path, "garbage"):
                self.assertEqual(integrity.verify(export, finalized), document)
        shadow = archive / "sources/claim-runs/ref"
        shadow.mkdir()
        try:
            refuses()
        finally:
            shadow.rmdir()
        for path in (archive / "sources/claim-runs/fit/extra",
                     archive / "sources/bound-runs/fit/config.json",
                     archive / integrity.METER_DIR / "stream-002.jsonl"):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.touch()
            try:
                refuses()
            finally:
                path.unlink()
        count = 0
        for path in paths:
            with self.subTest(path=path.relative_to(root)):
                data = path.read_bytes()
                for fault in ("absent", "zero") if data else ("absent",):
                    with file_fault(path, fault):
                        refuses()
                    count += 1
                try:
                    path.write_bytes(bytes([data[0] ^ 1]) + data[1:] if data else b"\0")
                    refuses()
                    count += 1
                finally:
                    path.write_bytes(data)
        print(f"\nBYTES seal: {len(paths)} entries, {count} per-file mutations refused by four consumers", flush=True)
