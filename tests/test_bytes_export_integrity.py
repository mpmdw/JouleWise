"""Synthetic regressions for the shared two-phase BYTES export seal."""
from contextlib import redirect_stderr, redirect_stdout
import csv
import hashlib
import io
import json
from pathlib import Path
import shutil
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from joulewise.b5 import harvest
from joulewise.b6 import bytes_integrity as integrity
from joulewise.b6.acceptance import _stage_roles
from scripts import bytes_analyze, bytes_commitment, bytes_stage1, bytes_twin
from tests.bytes_commitment_support import commitment_fixture
from tests.fixtures.bytes import harvest_roster
from tests.test_bytes_availability import AvailabilityFixture, SESSION, agreement, file_fault

ROOT = Path(__file__).resolve().parents[1]
# joulewise/b5/harvest.py l4_exclusion_inputs: the only member keys a real roster has.
HARVEST_MEMBER_KEYS = {"run_id", "stage_id", "kind", "units"}


def compact_fixture(root):
    """One synthetic session: a fit run, a reference and a held-out run, with a harvest-shaped roster."""
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
    digest = harvest_roster.write(roster, "sim", [
        harvest_roster.member("fit", "decode", [{"cell_id": "fit-cell", "stratum": "repeat", "unit_id": "fit"}]),
        harvest_roster.member("ref", "corpus_reference"),
        harvest_roster.member("held", "decode", [{"cell_id": "held-cell", "stratum": "repeat", "unit_id": "held"}])])
    agreement._write(archive / "harvest.json", {"outputs": {"derived/roster.json": digest}})
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
    return SimpleNamespace(app=app, export=export, archive=archive, campaign=campaign, private=private, keys=keys,
                           seal=root / "seal", fit_paths=fit_paths, outside=outside)


def harvested_roster(pack):
    """The roster the harvest's own writer gives for a registered BYTES sub-pack (configs only, no archive)."""
    pack_root = ROOT / "configs/campaigns" / pack
    written, _spans = harvest.l4_exclusion_inputs(harvest.build_roster(pack_root, ROOT), {}, plan_id=pack, attempt=1)
    return ({key: value for key, value in written.items() if key not in harvest_roster.WITHHELD_KEYS},
            _stage_roles(json.loads((pack_root / "plan_tree.json").read_bytes()))[1])


def write_table(path, rows):
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(("run_id", "role", "cell_ids"))
        writer.writerows(rows)
    return path


class RealShapeFitRowTests(unittest.TestCase):
    """Cold review of #949: the seal reads harvest-shaped rosters, which name units and no role."""

    def test_harvest_roster_and_plan_walk_table_authorize_exactly_the_fit_runs(self):
        registered = json.loads((ROOT / "configs/bytes/bytes_manifest.json").read_bytes())
        cell_roles = {cell: model["role"] for model in registered["models"] for cell in model["cell_ids"]}
        expected = {"bytes-s1-p1": (100, 25), "bytes-s5-p1": (0, 25)}
        with tempfile.TemporaryDirectory(prefix="bytes-real-roster-") as directory:
            for pack, (fit_science, references) in expected.items():
                with self.subTest(pack=pack):
                    roster, roles = harvested_roster(pack)
                    self.assertEqual({key for member in roster["members"] for key in member}, HARVEST_MEMBER_KEYS)
                    # The exporter's fit-visible table: plan-walk roles, held-out science rows withheld.
                    visible, withheld = [], []
                    for member in roster["members"]:
                        cells = [unit["cell_id"] for unit in member["units"]]
                        row = (member["run_id"], roles[member["run_id"]], ";".join(cells))
                        fit = cells and all(cell_roles.get(cell) == "fit" for cell in cells)
                        (visible if fit or (not cells and row[1] in integrity.REFERENCE_ROLES) else withheld).append(row)
                    self.assertEqual((sum(bool(row[2]) for row in visible), sum(not row[2] for row in visible)),
                                     (fit_science, references))
                    table = write_table(Path(directory) / (pack + ".runs.csv"), visible)
                    self.assertEqual(integrity._fit_run_ids(roster, table, cell_roles), {row[0] for row in visible})
                    for row in withheld[:3]:
                        write_table(table, [*visible, row])
                        with self.assertRaisesRegex(ValueError, "unauthorized or duplicate fit table row"):
                            integrity._fit_run_ids(roster, table, cell_roles)

    def test_fit_row_rule_on_a_harvest_shaped_roster(self):
        roles = {"fit-cell": "fit", "held-cell": "heldout"}
        roster = harvest_roster.document("sim", [
            harvest_roster.member("ref1", "start_reference"),
            harvest_roster.member("fit1", "decode", [{"cell_id": "fit-cell", "stratum": "repeat", "unit_id": "0"}]),
            harvest_roster.member("held1", "decode", [{"cell_id": "held-cell", "stratum": "repeat", "unit_id": "0"}])])
        cases = [
            ("reference row and fit science row", [("ref1", "start", ""), ("fit1", "science", "fit-cell")], {"ref1", "fit1"}),
            ("held-out science row", [("held1", "science", "held-cell")], None),
            ("held-out run relabelled as a cell-less reference", [("held1", "start", "")], None),
            ("run not in the roster", [("ghost", "start", "")], None),
            ("duplicate row", [("fit1", "science", "fit-cell"), ("fit1", "science", "fit-cell")], None),
            ("cell-less row with a non-reference role", [("ref1", "science", "")], None),
            ("fit run with another cell than the roster's", [("fit1", "science", "held-cell")], None),
            ("fit run with its cell dropped", [("fit1", "start", "")], None),
        ]
        with tempfile.TemporaryDirectory(prefix="bytes-fit-rows-") as directory:
            for label, rows, expected in cases:
                with self.subTest(label):
                    table = write_table(Path(directory) / "sim.runs.csv", rows)
                    if expected is None:
                        with self.assertRaisesRegex(ValueError, "unauthorized or duplicate fit table row"):
                            integrity._fit_run_ids(roster, table, roles)
                    else:
                        self.assertEqual(integrity._fit_run_ids(roster, table, roles), expected)


class SealLocationTests(unittest.TestCase):
    """Cold review of #949, MED 1: the seal repository lives outside every export directory."""

    def refused_fits(self, f, seal, out):
        """Both sealed fit CLIs on the compact fixture; any read past the seal check fails the test."""
        common = ["--manifest", str(f.campaign), "--key-dir", str(f.keys), "--out", str(out), *seal]
        messages = io.StringIO()
        with patch.object(bytes_analyze.ba, "read_json", side_effect=AssertionError("read after seal refusal")), \
                patch.object(bytes_twin, "read_manifest", side_effect=AssertionError("read after seal refusal")), \
                redirect_stdout(messages), redirect_stderr(messages):
            primary = bytes_analyze.main(["--export", str(f.export), "--stage", "fit", *common])
            twin = bytes_twin.main(["--export-dir", str(f.export), "--archive", str(f.archive), "--stage", "1", *common])
        self.assertEqual((primary, twin), (1, 1))
        self.assertEqual(messages.getvalue().count("BYTES export manifest:"), 2, messages.getvalue())
        self.assertFalse(out.exists())

    def test_capture_refuses_a_seal_repository_inside_an_export_directory(self):
        with tempfile.TemporaryDirectory(prefix="bytes-seal-inside-") as directory:
            f = compact_fixture(Path(directory))
            with patch.object(integrity, "ROOT", f.app):
                for repo in (f.export, f.export / "seal"):
                    with self.subTest(repo=repo.name), \
                            self.assertRaisesRegex(ValueError, "seal repository must be outside every export directory"):
                        integrity.capture(repo, f.campaign, [f.export], f.private)
                self.assertEqual(sorted(path.name for path in f.export.iterdir()), ["sim.runs.csv", "sim.session.json"])
                captured = integrity.capture(f.seal, f.campaign, [f.export], f.private)
                self.assertTrue(integrity.verify(f.seal, captured, phase="captured"))

    def test_table_planted_under_git_refuses_both_fit_clis(self):
        with tempfile.TemporaryDirectory(prefix="bytes-seal-plant-") as directory:
            root = Path(directory)
            f = compact_fixture(root)
            with patch.object(integrity, "ROOT", f.app), patch.object(bytes_twin, "__file__", f.app / "scripts/bytes_twin.py"):
                finalized = integrity.finalize(f.seal, integrity.capture(f.seal, f.campaign, [f.export], f.private), f.keys)
                check = dict(stage="fit", campaign=f.campaign, export_dirs=[f.export], archives=[f.archive], key_dir=f.keys)
                integrity.check_inputs(f.seal, finalized, **check)
                for name in ("sim.runs.csv", "sim.session.json"):
                    planted = f.export / ".git/planted" / name
                    planted.parent.mkdir(parents=True)
                    shutil.copyfile(f.export / name, planted)
                    try:
                        with self.subTest(planted=name):
                            self.refused_fits(f, integrity.options(f.seal, finalized), root / "planted")
                            with self.assertRaisesRegex(ValueError, "missing or extra file"):
                                integrity.check_inputs(f.seal, finalized, **check)
                    finally:
                        shutil.rmtree(f.export / ".git")
                integrity.check_inputs(f.seal, finalized, **check)

    def test_seal_made_inside_the_export_refuses_and_its_git_plant_is_seen(self):
        # The layout #949's driver made by default: the seal repository is the export
        # directory, and its census ignored .git. Rebuild that document, plant a table
        # under .git, and check each refusal layer on its own.
        with tempfile.TemporaryDirectory(prefix="bytes-seal-legacy-") as directory:
            root = Path(directory)
            f = compact_fixture(root)
            with patch.object(integrity, "ROOT", f.app), patch.object(bytes_twin, "__file__", f.app / "scripts/bytes_twin.py"):
                captured = integrity.verify(f.seal, integrity.capture(f.seal, f.campaign, [f.export], f.private),
                                            phase="captured")
                tables = next(name for name, scope in captured["roots"].items() if scope["kind"] == "tables")
                captured["roots"][tables]["ignore"] = [".git", integrity.NAME]
                legacy = integrity._repo(f.export, create=True)
                with patch.object(integrity, "_outside_exports"):
                    finalized = integrity.finalize(legacy, integrity._publish(legacy, captured), f.keys)
                planted = f.export / ".git/planted/sim.runs.csv"
                planted.parent.mkdir()
                shutil.copyfile(f.export / "sim.runs.csv", planted)
                check = dict(stage="fit", campaign=f.campaign, export_dirs=[f.export], archives=None, key_dir=f.keys)
                with self.assertRaisesRegex(ValueError, "seal repository must be outside every export directory"):
                    integrity.check_inputs(legacy, finalized, **check)
                self.refused_fits(f, integrity.options(legacy, finalized), root / "legacy-out")
                with patch.object(integrity, "_outside_exports"):
                    self.assertTrue(integrity.verify(legacy, finalized))   # the census ignores .git
                    with self.assertRaisesRegex(ValueError, "table paths differ"):
                        integrity.check_inputs(legacy, finalized, **check)
                planted.unlink()
                with patch.object(integrity, "_outside_exports"):
                    integrity.check_inputs(legacy, finalized, **check)


class ExportIntegrityTests(unittest.TestCase):
    def test_export_capture_release_and_all_four_consumers(self):
        for timing in ("mock", "native"):
            with self.subTest(timing=timing), tempfile.TemporaryDirectory(prefix="bytes-export-seal-") as directory:
                self.check_fixture(Path(directory), timing)

    def check_fixture(self, root, timing):
        fixture = AvailabilityFixture(root / "inputs", timing, complete_fit=True)
        self.assertTrue(fixture.manifest["synthetic"])
        for archive in fixture.archives:
            members = agreement.load(archive / "derived/roster.json")["members"]
            self.assertEqual({key for member in members for key in member}, HARVEST_MEMBER_KEYS)
        export = fixture.root / "export"
        # The seal repository lives outside every export directory (cold review of #949, MED 1).
        seal_repo = root / "seal"
        private = fixture.root / "private-keys"
        bindings = fixture.private.parent / "blinding-sessions"
        binding = bindings / (SESSION + ".json")
        self.assertTrue((bindings / "bytes-s1-p1.json").is_file())
        with file_fault(binding, "absent"):
            with self.assertRaisesRegex(ValueError, "manifest: missing session binding"):
                fixture.export_again(root / "retry-export", private)
            with self.assertRaisesRegex(ValueError, "manifest: unexpected or missing bindings file"):
                integrity.capture(seal_repo, fixture.manifest_path, [export], private)

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
                integrity.capture(seal_repo, fixture.manifest_path, [export], private)
        finally:
            roster.write_bytes(original)
        captured = integrity.capture(seal_repo, fixture.manifest_path, [export], private)
        capture_args = integrity.options(seal_repo, captured)

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
                integrity.finalize(seal_repo, captured, fixture.keys)
        finally:
            roster.write_bytes(original)

        pack = fixture.keys / "pack.json"
        raw = pack.read_bytes()
        try:
            pack.write_bytes(raw + b" ")
            with self.assertRaisesRegex(ValueError, "released key differs"):
                integrity.finalize(seal_repo, captured, fixture.keys)
        finally:
            pack.write_bytes(raw)
        finalized = integrity.finalize(seal_repo, captured, fixture.keys)
        seal = integrity.options(seal_repo, finalized)
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
        guard = {"export_seal_repo": seal_repo, "export_seal_commit": finalized}
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

        document = integrity.verify(seal_repo, finalized)
        manifest = seal_repo / integrity.NAME
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
            new_commit = integrity._publish(seal_repo, {**document, "files": records})
            bad = {**guard, "export_seal_commit": new_commit}
            refuses(integrity.options(seal_repo, new_commit), bad)
            manifest.write_bytes(original)
        with patch.object(bytes_commitment, "ROOT", repo), redirect_stderr(io.StringIO()):
            bytes_commitment.verify_commitment(commit, predictions, repo=repo, **guard)
            bytes_commitment.admit(args, "heldout_rows")
        self.assertNotEqual(journal.read_bytes(), before)

    def test_every_finalized_input_is_protected_for_all_four_consumers(self):
        with tempfile.TemporaryDirectory(prefix="bytes-input-faults-") as directory:
            self.check_input_faults(Path(directory))

    def check_input_faults(self, root):
        # The compact fixture for the exhaustive matrix. The native and mock
        # campaign tests above also run clean fits using the larger trees.
        f = compact_fixture(root)
        with patch.object(integrity, "ROOT", f.app), patch.object(bytes_twin, "__file__", f.app / "scripts/bytes_twin.py"):
            table = f.export / "sim.runs.csv"
            visible = table.read_bytes()
            for row in (b"held,science,fit-cell\n", b"held,science,held-cell\n", b"held,corpus,\n"):
                try:
                    table.write_bytes(visible + row)
                    with self.assertRaisesRegex(ValueError, "unauthorized or duplicate fit table row"):
                        integrity.capture(root / "refused-seal", f.campaign, [f.export], f.private)
                finally:
                    table.write_bytes(visible)
            captured = integrity.capture(f.seal, f.campaign, [f.export], f.private)
            finalized = integrity.finalize(f.seal, captured, f.keys)
            document = integrity.verify(f.seal, finalized)
            self.check_sealed_file_faults(root, f, finalized, document)

    def check_sealed_file_faults(self, root, f, finalized, document):
        export, campaign, archive, keys, fit_paths, outside = f.export, f.campaign, f.archive, f.keys, f.fit_paths, f.outside
        repo, predictions, receipt, commit = commitment_fixture(root)
        before = (repo / bytes_commitment.JOURNAL).read_bytes()
        guard = {"export_seal_repo": f.seal, "export_seal_commit": finalized}
        auth = SimpleNamespace(stage1_commit=commit, commitment_repo=repo, predictions=predictions,
                               stage1_receipt=receipt, **guard)
        seal = integrity.options(f.seal, finalized)
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
                self.assertEqual(integrity.verify(f.seal, finalized), document)
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
