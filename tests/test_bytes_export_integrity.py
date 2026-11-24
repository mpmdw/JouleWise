"""Synthetic regressions for the shared two-phase BYTES export seal."""
from contextlib import redirect_stderr, redirect_stdout
import io
from pathlib import Path
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
        checked = 0
        for entry in document["files"]:
            path = Path(document["roots"][entry["root"]]["path"]) / entry["path"]
            with self.subTest(root=entry["root"], path=entry["path"]):
                data = path.read_bytes()
                with file_fault(path, "absent"):
                    refuses(seal, guard)
                    checked += 1
                if data:
                    with file_fault(path, "zero"):
                        refuses(seal, guard)
                        checked += 1
                try:
                    path.write_bytes(bytes([data[0] ^ 1]) + data[1:] if data else b"\0")
                    refuses(seal, guard)
                    checked += 1
                finally:
                    path.write_bytes(data)

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
        print(f"\nBYTES {timing} seal: {checked} per-file mutations refused by four consumers", flush=True)
