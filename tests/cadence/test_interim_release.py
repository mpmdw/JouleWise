"""Frozen interim-look acceptance tests. Every input and subprocess is generated."""
from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import random
import re
import socket
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

from joulewise.cadence_looks import interim_release as C, manifest as M
from tests.cadence import look_minirepo as MR

REPO = MR.REPO
LOOK = "lm-interim-01"
SCHEMA = M.look_schemas(REPO)[1]
try:
    from scripts import cadence_look_run as R, cadence_look_synth as S
except ModuleNotFoundError as exc:
    if exc.name != "numpy":
        raise
    R = S = None


def digest(data):
    return hashlib.sha256(data).hexdigest()


def report(count=1, *, twin="yes"):
    stage1 = {"counts": {"in_energy_fit": count},
              "tripwires": {key: {"trips": False} for key in C.TRIPWIRES}}
    return C.public_record(LOOK, "a" * 64, "b" * 40, stage1, "c" * 64, "d" * 64, "passes", "within", twin)


class PublicSchema(unittest.TestCase):
    def test_closed_types_words_and_source_bindings(self):
        valid = report()
        with tempfile.TemporaryDirectory() as tmp:
            private = Path(tmp) / MR.synthetic_reservation_name(tmp)
            private.mkdir()
            public = Path(tmp) / "PUBLIC.json"
            C.write_public(public, private, valid, SCHEMA, expected=valid)
            self.assertEqual(public.read_bytes(), C.dump(valid))
            public.unlink()
            mutations = [
                dict(valid, in_energy_fit=1.0), dict(valid, in_energy_fit=True), dict(valid, in_energy_fit=2),
                dict(valid, qualified_interim="123.456"), dict(valid, coefficients_sha256="e" * 64),
                dict(valid, residual=0), list(valid), {k: v for k, v in valid.items() if k != "stage2_error"},
                *(dict(valid, **{word: "maybe"}) for word in C.PUBLIC_WORDS),
            ]
            for changed in mutations:
                with self.subTest(changed=changed), self.assertRaises(ValueError):
                    C.write_public(public, private, changed, SCHEMA, expected=valid)
                self.assertFalse(public.exists())
                self.assertFalse(list(private.iterdir()))
            for literal in (b"1.0", b"1e0"):
                with self.assertRaises(ValueError):
                    C.read_public(C.dump(valid).replace(b'"in_energy_fit":1', b'"in_energy_fit":' + literal), SCHEMA)

    def test_fuzz_public_bytes(self):
        rng = random.Random(20261114)
        with tempfile.TemporaryDirectory() as tmp:
            private = Path(tmp) / "private"
            private.mkdir()
            public = Path(tmp) / "PUBLIC.json"
            for _ in range(100):
                count = rng.randrange(0, 10000)
                record = report(count)
                for key, words in C.PUBLIC_WORDS.items():
                    record[key] = rng.choice(words)
                for key in ("manifest_sha256", "commit", "stage1_sha256", "coefficients_sha256"):
                    record[key] = rng.randbytes(len(record[key]) // 2).hex()
                C.write_public(public, private, record, SCHEMA, expected=record)
                raw = public.read_bytes()
                public.unlink()
                self.assertEqual(C.read_public(raw, SCHEMA), record)
                self.assertTrue(raw.isascii())
                for forbidden in ("\u2028", "\u2029", r"\u2028", r"\u2029"):
                    self.assertNotIn(forbidden.encode(), raw)
                self.assertNotRegex(raw, rb"[0-9].*\.[0-9]")
                # Remove exact literal keys and fixed ID, then independently account for every digit.
                pairs = re.findall(rb'"([^"]+)":("[^"]*"|[0-9]+)', raw)
                self.assertEqual(len(pairs), 15)
                for key, token in pairs:
                    name = key.decode()
                    if name == "in_energy_fit":
                        self.assertEqual(token, str(count).encode())
                    elif name == "commit" or name.endswith("_sha256"):
                        width = 40 if name == "commit" else 64
                        self.assertRegex(token, rb'^"[a-f0-9]{%d}"$' % width)
                    elif name == "look_id":
                        self.assertEqual(token, b'"lm-interim-01"')
                    else:
                        self.assertIn(token, [json.dumps(word).encode() for word in C.PUBLIC_WORDS[name]])


DRIVER = r'''
import os, subprocess, sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
from joulewise.cadence_looks import interim_release as C, manifest as M
repo, private_root, points, source = Path(sys.argv[2]), sys.argv[3], sys.argv[4], Path(sys.argv[5])
row = dict(look_id="lm-interim-01", public_root="public", custody_root=private_root)
point = lambda name: os._exit(73) if points == name else None
try:
    private, public = C.destinations(repo, row)
    assert private.name == "RESTRICTED"
    private = private.with_name(sys.argv[6])
    if private.exists():
        sys.exit(2)
except ValueError:
    sys.exit(2)
real_mkdir, real_open, real_dup2, real_write, real_rename = Path.mkdir, os.open, os.dup2, C.write_private, os.rename

def mkdir(path, *args, **kwargs):
    real_mkdir(path, *args, **kwargs)
    if path == private:
        point("mkdir")

def open_fd(path, *args, **kwargs):
    fd = real_open(path, *args, **kwargs)
    if isinstance(path, Path) and path.parent == private:
        point("open-" + path.name)
    return fd

def dup2(src, target, *args, **kwargs):
    result = real_dup2(src, target, *args, **kwargs)
    point("redirect-" + str(target))
    return result

def write(path, data):
    real_write(path, data)
    point(path.name)

def rename(source, target):
    point("publish-before")
    real_rename(source, target)
    point("publish-after")

Path.mkdir, os.open, os.dup2, C.write_private, os.rename = mkdir, open_fd, dup2, write, rename

def audit(event, args):
    if event == "open" and not isinstance(args[0], int):
        path = Path(args[0])
        writing = args[2] & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC)
        if writing and not path.is_relative_to(private):
            raise AssertionError("unexpected write")
    if event == "os.rename" and (Path(args[0]).parent != private or Path(args[1]) != public):
        raise AssertionError("unexpected rename")
    if event == "os.mkdir" and Path(args[0]) != private:
        raise AssertionError("unexpected directory")

sys.addaudithook(audit)
schema = M.look_schemas(Path(sys.argv[1]))[1]
s1 = dict(counts={"in_energy_fit": 1}, tripwires={key: {"trips": False} for key in C.TRIPWIRES})
def execute():
    source.read_bytes()
    os.write(1, b"PRIVATE-CANARY 123.456 /private/input\n")
    os.write(2, b"PRIVATE-CANARY 123.456 /private/input\n")
    point("read")
    if points == "RuntimeError":
        subprocess.run([sys.executable, "-I", "-B", "-c",
                        "import os; os.write(1,b'CHILD-STDOUT'); os.write(2,b'CHILD-STDERR')"], check=True)
    if points in ("RuntimeError", "OtherError"):
        cls = RuntimeError if points == "RuntimeError" else type("Leak_123_456", (Exception,), {})
        raise cls("PRIVATE-CANARY 123.456 /private/input")
    for name in ("fit.json", "step3.json", "coefficients.json", "twin.json"):
        C.write_private(private / name, b"{}\n")
    record = C.public_record("lm-interim-01", "a"*64, "b"*40, s1, "c"*64, "d"*64, "passes", "within", "yes")
    C.write_public(public, private, record, schema, expected=record)

try:
    sys.exit(C.run_reserved(private, execute, linear_algebra_error=None, keep_redirected=True))
except FileExistsError:
    sys.exit(2)
'''


class Reservation(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="jw-release-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.private_name = MR.synthetic_reservation_name(self.root)
        self.driver = self.root / "driver.py"
        self.driver.write_text(DRIVER)
        self.source = self.root / "synthetic-response"
        self.source.write_bytes(b"123.456\n")

    def layout(self, name):
        repo, custody = self.root / name / "repo", self.root / name / "custody"
        public = repo / "public" / LOOK / "PUBLIC.json"
        private = custody / LOOK / self.private_name
        public.parent.mkdir(parents=True)
        private.parent.mkdir(parents=True)
        return repo, custody, public, private

    def argv(self, layout, point):
        return [sys.executable, "-I", "-B", self.driver, REPO, layout[0], layout[1], point, self.source, self.private_name]

    def run_case(self, layout, point="", *, cwd=None):
        return subprocess.run(self.argv(layout, point), cwd=cwd or self.root, capture_output=True, timeout=60)

    def test_each_interrupted_reservation_is_consumed(self):
        checkpoints = ("mkdir", "open-stderr", "redirect-2", "open-stdout", "redirect-1", "read",
                       "fit.json", "step3.json", "coefficients.json", "twin.json", ".publication",
                       "publish-before", "publish-after")
        for point in checkpoints:
            with self.subTest(point=point):
                layout = self.layout(point)
                gone = self.run_case(layout, point)
                self.assertEqual((gone.returncode, gone.stdout, gone.stderr), (73, b"", b""))
                public, private = layout[2:]
                self.assertEqual(public.exists(), point == "publish-after")
                self.assertTrue(private.is_dir())
                original = {p.name: p.read_bytes() for p in private.iterdir()}
                prior_public = public.read_bytes() if public.exists() else None
                refused = self.run_case(layout, cwd=layout[0])
                self.assertEqual((refused.returncode, refused.stdout, refused.stderr), (2, b"", b""))
                self.assertEqual({p.name: p.read_bytes() for p in private.iterdir()}, original)
                self.assertEqual(public.read_bytes() if public.exists() else None, prior_public)

    def test_two_first_callers_and_uncommitted_result(self):
        layout = self.layout("competition")
        processes = [subprocess.Popen(self.argv(layout, ""), cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                     for cwd in (self.root, layout[0])]
        messages = [p.communicate(timeout=60) for p in processes]
        self.assertEqual(messages, [(b"", b"")] * 2)
        self.assertEqual(sorted(p.returncode for p in processes), [0, 2])
        public, private = layout[2:]
        self.assertEqual({p.name for p in private.iterdir()}, C.PRIVATE_NAMES)
        self.assertEqual((private / "stdout").read_bytes().count(b"PRIVATE-CANARY"), 1)
        self.assertEqual(private.stat().st_mode & 0o777, 0o700)
        self.assertEqual(C.read_public(public.read_bytes(), SCHEMA), report())
        old = {p.name: p.read_bytes() for p in [public, *private.iterdir()]}
        self.assertEqual(self.run_case(layout, cwd=layout[0]).returncode, 2)
        self.assertEqual({p.name: p.read_bytes() for p in [public, *private.iterdir()]}, old)

    def test_failure_is_two_stderr_lines_and_one_exit_code(self):
        for error in ("RuntimeError", "OtherError"):
            with self.subTest(error=error):
                layout = self.layout(error)
                run = self.run_case(layout, error)
                self.assertEqual(run.returncode, C.FAILURE_STATUS)
                self.assertEqual(run.stdout, b"")
                self.assertEqual(run.stderr, f"stage2_error\n{error}\n".encode())
                self.assertFalse(layout[2].exists())
                self.assertEqual({p.name for p in layout[3].iterdir()}, {"stdout", "stderr"})
                for stream in ("stdout", "stderr"):
                    raw = (layout[3] / stream).read_bytes()
                    self.assertIn(b"PRIVATE-CANARY 123.456 /private/input", raw)
                    if error == "RuntimeError":
                        self.assertIn(f"CHILD-{stream.upper()}".encode(), raw)


@unittest.skipIf(R is None, "numpy is required")
class LookExecution(unittest.TestCase):
    def setUp(self):
        self.mini = MR.mini_repo(self)
        self.tmp = tempfile.TemporaryDirectory(prefix="jw-release-input-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.manifest_path = self.mini / MR.MANIFEST
        self.manifest = M.load_json(self.manifest_path)
        self.manifest_sha = digest(self.manifest_path.read_bytes())
        self.input, self.energy, _ = S.build("noisy", seed=20261114)
        self.stage1_path = self.root / "stage1.json"
        source = self.root / "source.json"
        source.write_bytes(S.dump(self.input))
        result = MR.py(self.mini, "scripts/cadence_look_run.py", "stage1", "--input", source,
                       "--out", self.stage1_path, "--allow-draft", "--manifest", self.manifest_path)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.stage1 = M.load_json(self.stage1_path)
        self.stage1_sha = digest(self.stage1_path.read_bytes())
        self.commit = MR.git(self.mini, "rev-parse", "HEAD").stdout.strip()
        self.private_name = MR.synthetic_reservation_name(self.root)
        self.private = self.root / "custody" / LOOK / self.private_name
        self.public = self.mini / "public" / LOOK / "PUBLIC.json"
        self.private.parent.mkdir(parents=True)
        self.public.parent.mkdir(parents=True)
        self.row = M.load_json(self.mini / M.LOOK_LEDGER_PATH)["looks"][0]
        self.row.update(status="stage1_committed", execution_host=socket.gethostname(), public_root="public",
                        custody_root=str(self.private.parent.parent), roster_sha256="c" * 64,
                        verdicts_sha256="d" * 64, stage1_sha256=self.stage1_sha,
                        holds_cleared={flag: "RL-999" for flag in M.STAGE2_HOLD_FLAGS["interim"]
                                       if self.stage1[flag.split(".")[0]].get(flag.split(".")[1]) is True})
        self.ledger = self.root / "ledger.json"
        self.save_ledger()

    def save_ledger(self):
        self.ledger.write_bytes(C.dump({"schema": M.LOOK_LEDGER_SCHEMA, "looks": [self.row]}))

    def stage2(self):
        from tests.cadence import test_look_run as cli_fixture

        responses = self.root / "must-not-be-opened"
        args = ["stage2", "--stage1", self.stage1_path, "--stage1-sha256", self.stage1_sha,
                "--manifest", self.manifest_path, "--allow-draft", "--looks", self.ledger, "--energy", responses]
        with cli_fixture.spy_opens() as opened:
            code, stdout, stderr = cli_fixture._cli_subprocess(args, repo=self.mini)
        self.assertNotIn(str(responses), opened)
        self.assertFalse(self.private.exists())
        self.assertFalse(self.public.exists())
        return subprocess.CompletedProcess(args, code, stdout, stderr)

    def test_missing_twin_and_wrong_host_refuse_before_reservation(self):
        result = self.stage2()
        self.assertEqual(result.returncode, 2)
        self.assertIn("independent twin path and sha256", result.stderr)
        for pin in (None, {"path": MR.TWIN_PATH}, {"sha256": MR.TWIN_PIN["sha256"]}):
            draft = copy.deepcopy(self.manifest)
            draft["status"] = "committed"
            draft["fit"]["twin"] = pin
            with self.assertRaisesRegex(M.ManifestError, "fit.twin"):
                M.validate_manifest(draft, final=True)
        for host, reason in ((None, "register the execution_host"), ("synthetic-wrong-host", "does not match")):
            with self.subTest(host=host):
                self.row.pop("execution_host", None)
                if host is not None:
                    self.row["execution_host"] = host
                self.save_ledger()
                result = self.stage2()
                self.assertEqual(result.returncode, 2)
                self.assertIn(reason, result.stderr)

    def test_unconfirmed_production_host_cannot_reserve(self):
        with self.assertRaisesRegex(R.F.LookInputError, "production host identity awaits"):
            R.validate_execution_row(self.row, dict(self.stage1, synthetic=False), self.row["custody_root"])

    def test_missing_and_one_byte_twin_script_refuse_before_reservation(self):
        pin = M.load_json(REPO / MR.MANIFEST)["fit"]["twin"]
        script = self.mini / pin["path"]
        original = script.read_bytes()
        self.manifest["fit"]["twin"] = pin
        self.manifest_path.write_bytes(C.dump(self.manifest))
        self.stage1["manifest_sha256"] = digest(self.manifest_path.read_bytes())
        self.stage1_path.write_bytes(C.dump(self.stage1))
        self.stage1_sha = self.row["stage1_sha256"] = digest(self.stage1_path.read_bytes())
        self.save_ledger()
        script.unlink()
        result = self.stage2()
        self.assertEqual(result.returncode, 2)
        self.assertIn("fit.twin:", result.stderr)
        self.assertIn("not in the repository", result.stderr)
        script.write_bytes(original[:-1] + b" ")
        result = self.stage2()
        self.assertEqual(result.returncode, 2)
        self.assertIn("fit.twin:", result.stderr)
        self.assertIn("sha256 differs from the pin", result.stderr)

    def test_interrupted_ledger_spends_id_in_a_fresh_checkout(self):
        from tests.cadence import test_look_run as cli_fixture

        MR.commit(self.mini, stage1_sha256=self.stage1_sha)
        path = self.mini / M.LOOK_LEDGER_PATH
        self.row["sha256"] = digest(self.manifest_path.read_bytes())
        self.stage1["manifest_sha256"] = self.row["sha256"]
        self.stage1_path.write_bytes(C.dump(self.stage1))
        self.row["stage1_sha256"] = digest(self.stage1_path.read_bytes())
        ledger = {"schema": M.LOOK_LEDGER_SCHEMA, "looks": [self.row]}
        path.write_bytes(C.dump(ledger))
        MR.git_commit(self.mini, "register synthetic stage 1")
        args = ["row", "--manifest", self.manifest_path, "--repo", self.mini, "--write"]
        # The lead records the outcome after observing a reservation. The row command
        # uses only public records, so it also works in a checkout without that directory.
        with cli_fixture.spy_opens() as opened:
            rc, _, err = cli_fixture._cli_subprocess([*args, "--interrupted"], repo=self.mini,
                                                    extra={"entry": "manifest"})
        self.assertEqual(rc, 0, err)
        self.assertFalse(any(p.startswith(str(self.private.parent.parent)) for p in opened))
        spent = M.load_json(path)["looks"][0]
        self.assertEqual((spent["status"], spent["error_type"]), ("interrupted", "none_recorded"))
        self.assertNotIn("output_sha256", spent)
        self.assertNotIn("coefficients_sha256", spent)
        MR.git_commit(self.mini, "spend synthetic id")
        fresh = self.root / "fresh"
        MR.git(self.mini, "clone", "--no-local", str(self.mini), str(fresh))
        with cli_fixture.spy_opens() as opened:
            rc, _, err = cli_fixture._cli_subprocess(
                ["stage2", "--manifest", fresh / MR.MANIFEST, "--stage1", self.stage1_path,
                 "--stage1-sha256", self.row["stage1_sha256"], "--custody", self.row["custody_root"]], repo=fresh)
        self.assertEqual(rc, 2, err)
        self.assertIn("already spent (interrupted)", err)
        self.assertFalse(any(p.startswith(self.row["custody_root"]) for p in opened))
        self.assertFalse(self.private.exists())

    def test_interruption_vocabulary_and_completed_report_guard(self):
        MR.commit(self.mini, stage1_sha256=self.stage1_sha)
        path = self.mini / M.LOOK_LEDGER_PATH
        self.row["sha256"] = digest(self.manifest_path.read_bytes())
        ledger = {"schema": M.LOOK_LEDGER_SCHEMA, "looks": [self.row]}
        path.write_bytes(C.dump(ledger))
        MR.git_commit(self.mini, "register synthetic execution")
        self.public.write_bytes(C.dump(report()))
        result = MR.py(self.mini, "scripts/cadence_look_manifest.py", "row", "--manifest", self.manifest_path,
                       "--repo", self.mini, "--write", "--interrupted")
        self.assertEqual(result.returncode, 1)
        self.assertIn("no completed report", result.stdout)
        self.assertEqual(M.load_json(path), ledger)
        for state, error in (("interrupted", "RuntimeError"), ("failed", "none_recorded")):
            altered = {"schema": M.LOOK_LEDGER_SCHEMA, "looks": [dict(self.row, status=state, error_type=error)]}
            with self.assertRaisesRegex(M.ManifestError, "error_type"):
                M.validate_look_ledger(altered)

    def test_failure_ledger_keeps_the_delivered_type(self):
        MR.commit(self.mini, stage1_sha256=self.stage1_sha)
        result = MR.py(self.mini, "scripts/cadence_look_manifest.py", "row", "--manifest", self.manifest_path,
                       "--repo", self.mini, "--write", "--error-type", "RuntimeError")
        self.assertEqual(result.returncode, 0, result.stderr)
        row = M.load_json(self.mini / M.LOOK_LEDGER_PATH)["looks"][0]
        self.assertEqual((row["status"], row["error_type"]), ("failed", "RuntimeError"))

    def test_wrong_numpy_refuses_before_reservation(self):
        self.stage1["numpy_version"] = "0.0.0"
        raw = C.dump(self.stage1)
        self.stage1_path.write_bytes(raw)
        self.stage1_sha = self.row["stage1_sha256"] = digest(raw)
        self.save_ledger()
        result = self.stage2()
        self.assertEqual(result.returncode, 2)
        self.assertIn("numpy version differs", result.stderr)
        self.assertFalse(self.private.exists())

    def test_public_ledger_and_main_freeze_refuse_a_changed_coefficient_byte(self):
        from scripts import cadence_look_manifest as cli

        MR.commit(self.mini, stage1_sha256=self.stage1_sha)
        ledger_path = self.mini / M.LOOK_LEDGER_PATH
        self.row["sha256"] = digest(self.manifest_path.read_bytes())
        self.stage1["manifest_sha256"] = self.row["sha256"]
        self.row["stage1_sha256"] = digest(C.dump(self.stage1))
        ledger_path.write_bytes(C.dump({"schema": M.LOOK_LEDGER_SCHEMA, "looks": [self.row]}))
        MR.git_commit(self.mini, "register execution")
        commit = MR.git(self.mini, "rev-parse", "HEAD").stdout.strip()
        fit = R.F.stage2(self.stage1, self.row["stage1_sha256"], self.energy)
        coefficients = R.F.write_coefficients(self.stage1, self.row["stage1_sha256"], fit, self.row["sha256"])
        stored = C.dump(coefficients)
        self.private.mkdir()
        local_coefficient = self.private / "coefficients.json"
        local_coefficient.write_bytes(stored)
        registered_path = self.private.with_name("RESTRICTED") / local_coefficient.name
        leg = next(item for item in self.input["legs"] if item["leg_key"] in self.energy["legs"])
        soak = next(sp["soak_reference_tv0h_c"] for sp in self.input["spans"] if sp["span_id"] == leg["span_id"])
        original_read = Path.read_bytes

        def read(path):
            if path == registered_path:
                reads.append(path)
                return original_read(local_coefficient)
            return original_read(path)

        for agreement in ("no", "not_evaluable", "yes"):
            reads = []
            with self.subTest(agreement=agreement), mock.patch.object(Path, "read_bytes", read):
                record = C.public_record(LOOK, self.row["sha256"], commit, self.stage1, self.row["stage1_sha256"],
                                        digest(stored), "passes", "within", agreement)
                self.public.write_bytes(C.dump(record))
                outcome = cli.public_row(self.mini, self.row)
                self.assertFalse(reads)
                ledger_path.write_bytes(C.dump({"schema": M.LOOK_LEDGER_SCHEMA, "looks": [dict(self.row, **outcome)]}))
                if agreement == "no":
                    with self.assertRaisesRegex(M.ManifestError, "not committed on origin/main"):
                        R.F.predict_frozen(self.mini, leg, soak)
                MR.git_commit(self.mini, f"publish synthetic {agreement}")
                if agreement != "yes":
                    with self.assertRaisesRegex(M.ManifestError, "does not record twin agreement"):
                        R.F.predict_frozen(self.mini, leg, soak)
                    self.assertFalse(reads)
                else:
                    score = R.F.predict_frozen(self.mini, leg, soak)
                    self.assertEqual(score, R.F.predict(coefficients, leg, soak))
                    local_coefficient.write_bytes(stored[:-1] + b" ")
                    with self.assertRaisesRegex(R.F.LookInputError, "stored coefficient bytes differ"):
                        R.F.predict_frozen(self.mini, leg, soak)
                    self.assertEqual(reads, [registered_path, registered_path])

    def test_noisy_legwise_public_byte_invariance(self):
        prepared = R.F.stage2_preflight(self.stage1)
        args = SimpleNamespace(energy=self.root / "response.json", stage1_sha256=self.stage1_sha)
        coefficient_schema = M.coefficients_schema(REPO)
        from joulewise.cadence_looks import step3_roster as s3

        def trial(name, energy):
            dest = self.root / name
            dest.mkdir()
            private, public = dest / self.private_name, dest / "PUBLIC.json"
            args.energy.write_bytes(C.dump(energy))
            # The planted level-E fixture has no Step 3 bundle. Feed the same response to the
            # decision and comparison stubs while exercising the normal primary fit and writer.
            def step3(*_args, **_kwargs):
                total = sum(sum(leg["gpu_rail"]["segments"]) for leg in energy["legs"].values())
                return {"tripwire": {"decision": "within", "value": total}}
            with mock.patch.object(R, "code_hashes", return_value={}), mock.patch.object(s3, "run_roster", side_effect=step3):
                rc = C.run_reserved(private, lambda: R.finish_stage2(
                    args, self.stage1, prepared, self.manifest, self.commit, self.manifest_sha, private, public,
                    SCHEMA, coefficient_schema, None, None), linear_algebra_error=R.F.np.linalg.LinAlgError)
            self.assertEqual(rc, 0, (private / "stderr").read_text())
            self.assertEqual({p.name for p in private.iterdir()}, C.PRIVATE_NAMES)
            raw = public.read_bytes()
            rec = C.read_public(raw, SCHEMA)
            self.assertEqual(rec["coefficients_sha256"], digest((private / "coefficients.json").read_bytes()))
            self.assertEqual((rec["commit"], rec["manifest_sha256"], rec["stage1_sha256"]),
                             (self.commit, self.manifest_sha, self.stage1_sha))
            self.assertEqual(rec["in_energy_fit"], self.stage1["counts"]["in_energy_fit"])
            masked = re.sub(rb'("(?:manifest|stage1|coefficients)_sha256":")[a-f0-9]{64}(")',
                            rb'\g<1>' + b"x" * 64 + rb'\2', raw)
            return tuple(rec[word] for word in ("qualified_interim", "drift_tripwire", "twin_agrees", "stage2_error")), masked

        base_words, base = trial("base", self.energy)
        compared = skipped = 0
        for index, key in enumerate(self.energy["legs"]):
            perturbed = copy.deepcopy(self.energy)
            for response in perturbed["legs"][key].values():
                response["segments"] = [x * 1.005 for x in response["segments"]]
                response["prefix_tails"] = {k: x * 1.005 for k, x in response["prefix_tails"].items()}
            words, raw = trial(f"trial-{index}", perturbed)
            if words != base_words:
                skipped += 1
            else:
                self.assertEqual(raw, base, key)
                compared += 1
        print(f"synthetic legwise invariance: attempted={len(self.energy['legs'])} compared={compared} word_flip_skips={skipped}",
              file=sys.stderr)
        self.assertEqual(compared + skipped, len(self.energy["legs"]))
        self.assertGreater(compared, 0)


TWIN_DRIVER = r'''
import json, os, subprocess, sys
from pathlib import Path
repo, basename, fault = Path(sys.argv[1]), sys.argv[2], sys.argv[3]
sys.path.insert(0, str(repo))
from scripts import cadence_look_run as look
from joulewise.cadence_looks import interim_twin

original_destinations = look.release.destinations
def destinations(repo, row):
    private, public = original_destinations(repo, row)
    assert private.name == "RESTRICTED"
    return private.with_name(basename), public
look.release.destinations = destinations

original_run = subprocess.run
attempts = []
def run(argv, *args, **kwargs):
    if Path(argv[0]) != Path(sys.executable) or argv[1:4] != ["-I", "-B", str(repo / "scripts/cadence_interim_twin.py")]:
        return original_run(argv, *args, **kwargs)
    attempts.append(argv)
    assert len(attempts) == 1 and not kwargs.get("shell")
    assert kwargs["stdout"] == subprocess.PIPE and kwargs.get("stderr") is None
    path = Path(argv[argv.index("--coefficients") + 1])
    assert path.parent.name == basename and path.parent.is_dir()
    assert path.with_name("fit.json").is_file() and path.with_name("step3.json").is_file()
    before = path.read_bytes()
    assert look.sha256_file(path) == argv[argv.index("--coefficients-sha256") + 1]
    if fault == "timeout":
        raise subprocess.TimeoutExpired(argv, kwargs["timeout"], output=b"synthetic partial frame")
    if fault == "nonzero":
        argv = list(argv)
        argv[argv.index("--coefficients-sha256") + 1] = "0" * 64
    result = original_run(argv, *args, **kwargs)
    assert path.read_bytes() == before
    if fault == "nonzero":
        assert result.returncode == 1 and result.stdout == b""
        return result
    assert result.returncode == 0, result.returncode
    if fault == "malformed":
        result.stdout = b"not a frame\n"
    elif fault == "coefficient_change":
        path.write_bytes(before[:-1] + b" ")
    elif fault in ("numeric", "omitted_fold", "forged_primary"):
        frame = json.loads(result.stdout)
        pair = frame["coefficients"]["gpu_rail"]
        key = "C#/channels/gpu_rail/fold_coefficients"
        side = pair["primary" if fault == "forged_primary" else "twin"]
        first_fold = side[key][sorted(side[key])[0]]
        if fault == "omitted_fold":
            first_fold.pop("p1")
        else:
            first_fold["p1"] *= 1.1
            frame["max_relative_difference"]["gpu_rail"] = 0.0
        result.stdout = json.dumps(frame, sort_keys=True, separators=(",", ":")).encode() + b"\n"
    return result
interim_twin.subprocess.run = run
status = look.main(sys.argv[4:], keep_redirected=True)
assert len(attempts) == 1, len(attempts)
sys.exit(status)
'''


@unittest.skipIf(R is None, "numpy is required")
class TwinThroughCLI(unittest.TestCase):
    def setUp(self):
        import plistlib

        tmp = tempfile.TemporaryDirectory(prefix="jw-parent-twin-")
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name).resolve()
        self.mini = MR.mini_repo(self)
        self.manifest = self.mini / MR.MANIFEST
        draft = M.load_json(self.manifest)
        pin = M.load_json(REPO / MR.MANIFEST)["fit"]["twin"]
        self.assertEqual(digest((self.mini / pin["path"]).read_bytes()),
                         "aa041772d45bc955aba999721cfdea4b9776875ca635449fd0ff60593a5ba22a")
        draft["fit"]["twin"] = pin
        self.manifest.write_bytes(C.dump(draft))
        tokens = {}
        look_input, energy, _ = S.build("exact", tokens=tokens)
        source = self.root / "generated-bundles"
        locators = S.write_custody(source, look_input, energy, tokens)
        # The accepted #816 pin accepts a single component per receipt locator.
        # Generate that layout before stage 1 binds the fixture's record bytes.
        for path in source.glob("*/legs/*/leg_record.json"):
            record = M.load_json(path)
            if record["result"]["bundle"]:
                runtime = path.parent / "runtime"
                (runtime / record["result"]["bundle"]).rename(runtime / "mock-bundle")
                record["result"]["bundle"] = "mock-bundle"
                path.write_bytes(C.dump(record))
        # Use complete Step 3 telemetry so both implementations evaluate three
        # cells on the same generated native state and clock frames.
        for rich in source.glob("*/legs/*/runtime/mock-bundle/rich_telemetry.jsonl"):
            rows = [json.loads(line) for line in rich.read_bytes().splitlines()]
            for item in rows:
                item["gpu"]["dvfm_states"] = [{"freq": 1000, "used_ns": 10**9}]
            rich.write_bytes(b"".join(C.dump(item) for item in rows))
            native = rich.parent / "raw/powermetrics.plist"
            frames = [plistlib.loads(item) for item in native.read_bytes().split(b"\0") if item]
            for item in frames:
                item.setdefault("thermal_pressure", "Unknown")
            native.write_bytes(b"".join(plistlib.dumps(item) + b"\0" for item in frames))
        self.stage1 = self.root / "stage1.json"
        stage1 = MR.py(self.mini, "scripts/cadence_look_run.py", "stage1", "--roster", locators["roster.json"],
                       "--rules-3-4", locators["rules_3_4.json"], "--custody", source, "--out", self.stage1,
                       "--manifest", self.manifest, "--allow-draft")
        self.assertEqual(stage1.returncode, 0, stage1.stderr)
        doc = M.load_json(self.stage1)
        self.response_sha = digest(self.stage1.read_bytes())
        self.overrides = [(row["span_id"], source / row["span_id"]) for row in doc["roster"]["spans"]]
        self.row = {"look_id": LOOK, "manifest_path": MR.MANIFEST, "sha256": digest(self.manifest.read_bytes()),
                    "stage1_sha256": self.response_sha, "status": "stage1_committed",
                    "roster_sha256": doc["code_sha256"]["input:roster_sha256"],
                    "verdicts_sha256": doc["code_sha256"]["input:rules_3_4_sha256"],
                    "execution_host": socket.gethostname(),
                    "holds_cleared": {flag: "RL-999" for flag in M.STAGE2_HOLD_FLAGS["interim"]
                                      if doc[flag.split(".")[0]].get(flag.split(".")[1]) is True}}
        self.driver = self.root / "run.py"
        self.driver.write_text(TWIN_DRIVER)
        self.basename = MR.synthetic_reservation_name(self.root)

    def trial(self, fault):
        private_root = self.root / fault
        private = private_root / LOOK / self.basename
        public_rel = f"generated-{fault}"
        public = self.mini / public_rel / LOOK / "PUBLIC.json"
        private.parent.mkdir(parents=True)
        public.parent.mkdir(parents=True)
        ledger = private_root / "ledger.json"
        row = dict(self.row, custody_root=str(private_root), public_root=public_rel)
        ledger.write_bytes(C.dump({"schema": M.LOOK_LEDGER_SCHEMA, "looks": [row]}))
        argv = [sys.executable, "-I", "-B", self.driver, self.mini, self.basename, fault,
                "stage2", "--manifest", self.manifest, "--stage1", self.stage1, "--stage1-sha256", self.response_sha,
                "--looks", ledger, "--allow-draft", "--custody", private_root]
        for sid, path in self.overrides:
            argv.extend(("--span-dir", f"{sid}={path}"))
        result = subprocess.run(argv, cwd=self.root, capture_output=True, timeout=180)
        return result, private, public

    def test_actual_parent_child_handshake_and_failure_channels(self):
        for fault, agreement in (("match", "yes"), ("numeric", "no"), ("omitted_fold", "not_evaluable"),
                                 ("forged_primary", "not_evaluable"), ("nonzero", "not_evaluable"),
                                 ("malformed", "not_evaluable"), ("timeout", "not_evaluable")):
            with self.subTest(fault=fault):
                run, private, public = self.trial(fault)
                self.assertEqual((run.returncode, run.stdout, run.stderr), (0, b"", b""),
                                 (private / "stderr").read_bytes() if private.exists() else run.stderr)
                self.assertEqual({path.name for path in private.iterdir()}, C.PRIVATE_NAMES)
                row = C.read_public(public.read_bytes(), SCHEMA)
                comparison = M.load_json(private / "twin.json")
                self.assertEqual((row["twin_agrees"], row["stage2_error"], comparison["agreement"]),
                                 (agreement, "no", agreement))
                coefficients = (private / "coefficients.json").read_bytes()
                self.assertEqual(row["coefficients_sha256"], digest(coefficients))
                frame = (private / "stdout").read_bytes()
                if fault == "match":
                    self.assertTrue(json.loads(frame)["schema"].endswith(".v1"))
                    self.assertTrue(all(cell["status"] == "ok" for cell in M.load_json(private / "step3.json")["cells"]))
                    original = dict(row, twin_agrees=None)
                    original_coefficients = coefficients
                else:
                    self.assertEqual(dict(row, twin_agrees=None), original)
                    self.assertEqual(coefficients, original_coefficients)
                if fault == "numeric":
                    self.assertEqual(json.loads(frame)["max_relative_difference"]["gpu_rail"], 0)
                    self.assertGreater(comparison["max_relative_difference"]["gpu_rail"], 1e-8)
                if fault == "nonzero":
                    self.assertEqual((private / "stderr").read_bytes(), b"stage2_error\nValueError\n")
                if fault == "malformed":
                    self.assertEqual(frame, b"not a frame\n")
                if fault == "timeout":
                    self.assertEqual(frame, b"synthetic partial frame")
        run, private, public = self.trial("coefficient_change")
        self.assertEqual((run.returncode, run.stdout, run.stderr), (C.FAILURE_STATUS, b"", b"stage2_error\nOtherError\n"))
        self.assertTrue(private.is_dir())
        self.assertFalse(public.exists())
