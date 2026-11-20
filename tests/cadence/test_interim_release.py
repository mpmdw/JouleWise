"""Frozen interim-look acceptance tests. Every input and subprocess is generated."""
from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import random
import re
import runpy
import shutil
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
UUID_LINE = '  |   "IOPlatformUUID" = "12345678-9abc-def0-1234-56789abcdef0"\n'
HOST_TOKEN = "hw1:6fd8db3c47b37aaa51f7b08c4f9af1bc1b989f8adda676166a4ad80b83565a11"
BAD_UUID_PROBES = ("", UUID_LINE.replace("12345678", "xyz"), UUID_LINE + UUID_LINE)
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


class HostIdentity(unittest.TestCase):
    def test_host_probe_argv_and_normalized_digest(self):
        for line in (UUID_LINE, UUID_LINE.replace("9abc-def0", "9ABC-DEF0")):
            with mock.patch.object(M.subprocess, "run", return_value=SimpleNamespace(stdout=line.encode())) as probe:
                self.assertEqual(M.execution_host(), HOST_TOKEN)
            probe.assert_called_once_with(["/usr/sbin/ioreg", "-rd1", "-c", "IOPlatformExpertDevice"],
                                          capture_output=True, check=True)
        for line in BAD_UUID_PROBES:
            with mock.patch.object(M.subprocess, "run", return_value=SimpleNamespace(stdout=line.encode())):
                with self.assertRaisesRegex(M.ManifestError, "exactly one UUID-shaped IOPlatformUUID"):
                    M.execution_host()
        with mock.patch.object(M.subprocess, "run", side_effect=FileNotFoundError):
            with self.assertRaisesRegex(M.ManifestError, "could not read IOPlatformUUID"):
                M.execution_host()

    @unittest.skipIf(R is None, "numpy is required by the CLI")
    def test_host_id_cli_prints_only_the_token(self):
        from tests.cadence import test_look_run as cli_fixture

        result = cli_fixture._cli_subprocess(["host-id"], extra={"host_probe": UUID_LINE})
        self.assertEqual(result, (0, HOST_TOKEN + "\n", ""))


class FreezeNaming(unittest.TestCase):
    def test_named_no_uses_exact_main_record_and_audit_stanza(self):
        mini = MR.mini_repo(self)
        MR.commit(mini, stage1_sha256="c" * 64)
        ledger = mini / M.LOOK_LEDGER_PATH
        data = M.load_json(ledger)
        row = M._look_row(data, LOOK)
        row.update(public_root="public", custody_root=str(mini.parent / "synthetic-only"), execution_host=HOST_TOKEN)
        ledger.write_bytes(C.dump(data))
        MR.git_commit(mini, "commit generated stage one")
        record = dict(report(twin="no"), commit=MR.git(mini, "rev-parse", "HEAD").stdout.strip(),
                      manifest_sha256=row["sha256"])
        public = mini / "public" / LOOK / "PUBLIC.json"
        public.parent.mkdir(parents=True)
        public.write_bytes(C.dump(record))
        row.update(status="run", output_sha256=digest(public.read_bytes()),
                   coefficients_sha256=record["coefficients_sha256"])
        ledger.write_bytes(C.dump(data))
        MR.git_commit(mini, "publish generated no")
        with self.assertRaisesRegex(M.ManifestError, "twin agreement"):
            M.freeze2_commitment(mini)

        rule = "RL-999"
        stanza = (f'FREEZE-2-NAMING ruling={rule} look={LOOK} coefficients_sha256={row["coefficients_sha256"]} '
                  f'public_sha256={row["output_sha256"]} designation=freeze-2')
        MR.git(mini, "checkout", "-qb", "fixture-audit")
        decisions = mini / M._FREEZE2_DECISIONS_PATH
        decisions.parent.mkdir(parents=True, exist_ok=True)
        decisions.write_text(f"# {rule}. Generated ruling\n\n{stanza}\n")
        MR.git_commit(mini, "name the generated digest", publish=False)
        audit = MR.git(mini, "rev-parse", "HEAD").stdout.strip()
        audit_ref = "refs/remotes/" + M._FREEZE2_AUDIT_REF
        MR.git(mini, "update-ref", audit_ref, audit)
        MR.git(mini, "checkout", "-q", "main")
        naming = {"schema": "joulewise.cadence_looks.freeze2_naming.v1", "look_id": LOOK, "ruling": rule,
                  "coefficients_sha256": row["coefficients_sha256"], "public_sha256": row["output_sha256"],
                  "designation": "freeze-2", "decisions_path": M._FREEZE2_DECISIONS_PATH,
                  "decisions_commit": audit, "stanza": stanza}
        path = mini / MR.MANIFEST.replace(".json", ".freeze2.json")
        path.write_bytes(C.dump(naming))
        row.update(status="frozen", ruling=rule)
        ledger.write_bytes(C.dump(data))
        MR.git_commit(mini, "register the exact generated naming record")
        with mock.patch.object(Path, "read_bytes", side_effect=AssertionError("filesystem artifact read")):
            accepted, evidence = M.freeze2_authority(mini, expected_coefficients_sha256=row["coefficients_sha256"])
        self.assertEqual(accepted, row)
        self.assertEqual(evidence["decision_source"], rule)
        result = MR.py(mini, "scripts/cadence_look_manifest.py", "authorize-freeze2", "--repo", mini,
                       "--look-id", LOOK, "--expected-coefficients-sha256", row["coefficients_sha256"])
        self.assertEqual((result.returncode, json.loads(result.stdout)), (0, evidence), result.stderr)
        for updates in ({"public_sha256": "0" * 64}, {"designation": "other"}, {"stanza": stanza + " "},
                        {"decisions_commit": record["commit"]}, {"extra": False}):
            with self.subTest(updates=updates):
                path.write_bytes(C.dump(dict(naming, **updates)))
                MR.git_commit(mini, "plant bad generated naming record")
                with self.assertRaises(M.ManifestError):
                    M.freeze2_commitment(mini)

    def test_bound_successor_report_preserves_closed_id(self):
        doc = M.load_json(REPO / MR.MANIFEST)
        successor = "lm-interim-02"
        manifest = dict(doc, look_id=successor, supersedes=LOOK, status="committed")
        M.require_successor_ruling(manifest, {"looks": [{"look_id": LOOK, "status": "interrupted", "ruling": "RL-999"}]})
        published = dict(report(), look_id=successor)
        self.assertEqual(C.read_public(C.dump(published), SCHEMA, look_id=manifest["look_id"]), published)
        with self.assertRaises(ValueError):
            C.read_public(C.dump(published), SCHEMA, look_id=LOOK)


class MainPort(unittest.TestCase):
    def test_mixed_ledger_preserves_v2_registration_and_v1_look(self):
        mini = MR.mini_repo(self)
        MR.commit(mini)
        ledger = M.load_json(mini / M.LOOK_LEDGER_PATH)
        registered = M._look_row(ledger, "lm-qual-01")
        self.assertEqual(registered["status"], "registered")
        self.assertEqual(M._look_row(ledger, LOOK)["status"], "committed")
        self.assertEqual(M.validate_look_ledger(ledger, mini), ledger)
        bad = copy.deepcopy(ledger)
        M._look_row(bad, LOOK)["status"] = "registered"
        with self.assertRaises(M.ManifestError):
            M.validate_look_ledger(bad, mini)

    def test_port_includes_historical_kits_and_checks_every_pin(self):
        mini = MR.mini_repo(self)
        args = ("port-files", mini / MR.MANIFEST, "--repo", mini)
        result = MR.py(mini, "scripts/cadence_look_manifest.py", *args)
        self.assertEqual(result.returncode, 0, result.stderr)
        pins = json.loads(result.stdout)
        for name in ("docs/process/cadence/kits/cl-dev-01.json", "docs/process/cadence/kits/cl-dev-02.json",
                     "configs/align/v4/r1_runtime.json", "joulewise/external/km003c_parse.py"):
            with self.subTest(name=name):
                path = mini / name
                original = path.read_bytes()
                self.assertEqual(pins[name], digest(original))
                path.unlink()
                result = MR.py(mini, "scripts/cadence_look_manifest.py", *args)
                self.assertEqual(result.returncode, 1)
                self.assertIn(name, result.stderr)
                path.write_bytes(original)


@unittest.skipIf(R is None, "numpy is required")
class PostNo(unittest.TestCase):
    def paired_fit(self, scale=None):
        from joulewise.cadence_looks import interim_twin as parent
        from scripts import cadence_interim_twin as child

        level_r, energy, _ = S.build("exact", seed=20261114)
        stage1 = R.F.stage1(level_r, energy["input_sha256"])
        legs = [leg for leg in stage1["legs"] if leg["in_energy_fit"]]
        if scale is not None:
            for leg in legs:
                if leg["day"] == stage1["roster"]["fit_days"][0]:
                    channel = energy["legs"][leg["leg_key"]]["gpu_rail"]
                    channel["segments"] = [x * scale for x in channel["segments"]]
        stage1_sha = digest(C.dump(stage1))
        fit = R.F.stage2(stage1, stage1_sha, energy)
        coefficients = R.F.write_coefficients(stage1, stage1_sha, fit, "a" * 64)
        fit["soak_retries"] = stage1["soak_retries"]
        marked = {leg["span_id"] for leg in legs if leg["marks"]}
        twin = child.recompute_fit(stage1, legs, [energy["legs"][leg["leg_key"]] for leg in legs], marked)
        twin["soak_retries"] = stage1["soak_retries"]
        step = {"cells": [], "tripwire": {"decision": "not_evaluable", "trips": None}}
        return parent, child, stage1, coefficients, fit, twin, step, energy

    def test_near_zero_leaves_still_give_no_and_use_predictions(self):
        for family in ("coefficients", "onset"):
            with self.subTest(family=family):
                parent, child, stage1, c, fit, twin, step, energy = self.paired_fit()
                # Plant the relative-only failure in C while holding other predictions at their agreeing values.
                twin = dict(copy.deepcopy(fit), onset=copy.deepcopy(c["onset"]))
                if family == "coefficients":
                    c["channels"]["gpu_rail"]["coefficients"]["k_fan"] = 1e-14
                    twin["channels"]["gpu_rail"]["coefficients"]["k_fan"] = -1e-14
                else:
                    c["onset"]["coefficients"]["t_p_s"] = 1e-17
                    twin["onset"]["coefficients"]["t_p_s"] = -1e-17
                left = child.projections(stage1, c, fit, step)
                right = child.projections(stage1, twin, fit, step)
                frame = parent.compare(C.dump(child.comparison_frame(left, right)), stage1, c, fit, step)
                self.assertEqual(frame["agreement"], "no")
                self.assertTrue(parent.post_no(stage1, fit, energy, frame)["predictions_within_tolerances"])

    def test_a_parseable_cell_map_difference_is_no_and_only_a_malformed_map_is_unevaluable(self):
        """Census P02 on the production adjudicator with a completed frame: the cell map's syntax is validated,
        its key set is an agreement predicate."""
        parent, child, stage1, c, fit, _, step, _ = self.paired_fit()
        ok = {"status": "ok", "gamma_estimable": True}
        empty = {"status": "not_run", "gamma_estimable": None}
        step = dict(step, cells=[dict(ok, prompt_tokens=10000), dict(empty, prompt_tokens=64)])
        primary = child.projections(stage1, c, fit, step)
        self.assertEqual(primary["verdicts"]["D#/cells"], {"10000": ok, "64": empty})

        def adjudicate(cells, text=None):
            twin = copy.deepcopy(primary)
            twin["verdicts"]["D#/cells"] = cells
            raw = C.dump(child.comparison_frame(primary, twin))
            if text is not None:
                self.assertEqual(raw.count(text[0]), 1)
                raw = raw.replace(*text)
            return parent.compare(raw, stage1, c, fit, step)["agreement"]

        self.assertEqual(adjudicate({"10000": ok, "64": empty}), "yes")
        for label, cells in (("the census's extra cell", {"10000": ok, "64": empty, "32": empty}),
                             ("an extra estimable cell", {"10000": ok, "64": empty, "128": ok}),
                             ("a removed cell", {"10000": ok}), ("no cells", {}),
                             ("a replaced key", {"10000": ok, "65": empty}),
                             ("a changed status", {"10000": ok, "64": dict(empty, status="ok")}),
                             ("a changed word", {"10000": dict(ok, gamma_estimable=False), "64": empty})):
            with self.subTest(parseable=label):
                self.assertEqual(adjudicate(cells), "no")
        for label, cells in (("a leading zero", {"10000": ok, "064": empty}), ("zero", {"10000": ok, "0": empty}),
                             ("a sign", {"10000": ok, "-64": empty}), ("a space", {"10000": ok, "64 ": empty}),
                             ("digits outside ASCII", {"10000": ok, "\u0666\u0664": empty}),
                             ("an empty key", {"10000": ok, "": empty}),
                             ("an unlisted status", {"10000": ok, "64": dict(empty, status="maybe")}),
                             ("a word that is not boolean", {"10000": dict(ok, gamma_estimable=1), "64": empty}),
                             ("an extra member", {"10000": dict(ok, note="generated"), "64": empty}),
                             ("a missing member", {"10000": {"status": "ok"}, "64": empty}),
                             ("a list", [ok, empty]), ("null", None)):
            with self.subTest(malformed=label), self.assertRaises((ValueError, TypeError, KeyError)):
                adjudicate(cells)
        with self.subTest(malformed="a repeated key"), self.assertRaises(ValueError):
            adjudicate({"10000": ok, "64": empty, "777": empty}, (b'"777":{', b'"64":{'))

    def test_valid_boundary_crossing_is_reviewable_and_larger_difference_is_not(self):
        for scale, expected in ((0.9816460542338478, True), (1.0217132401209437, True), (0.95, False)):
            with self.subTest(scale=scale):
                parent, child, stage1, c, fit, twin, step, energy = self.paired_fit(scale)
                word = fit["qualified_interim_half"]["verdict"]
                # Plant the opposite word if this platform's rounding puts both solvers on the same side.
                twin["qualified_interim_half"]["verdict"] = "fails" if word == "passes" else "passes"
                left = child.projections(stage1, c, fit, step)
                right = child.projections(stage1, twin, twin, step)
                frame = parent.compare(C.dump(child.comparison_frame(left, right)), stage1, c, fit, step)
                self.assertEqual(frame["agreement"], "no")
                self.assertEqual(parent.post_no(stage1, fit, energy, frame)["verdicts_within_boundary"], expected)


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
        self.row.update(status="stage1_committed", execution_host=HOST_TOKEN, public_root="public",
                        custody_root=str(self.private.parent.parent), roster_sha256="c" * 64,
                        verdicts_sha256="d" * 64, stage1_sha256=self.stage1_sha,
                        holds_cleared={flag: "RL-999" for flag in M.STAGE2_HOLD_FLAGS["interim"]
                                       if self.stage1[flag.split(".")[0]].get(flag.split(".")[1]) is True})
        self.ledger = self.root / "ledger.json"
        self.save_ledger()

    def save_ledger(self):
        self.ledger.write_bytes(C.dump({"schema": M.LOOK_LEDGER_SCHEMA, "looks": [self.row]}))

    def stage2(self, *, host_probe=UUID_LINE):
        from tests.cadence import test_look_run as cli_fixture

        responses = self.root / "must-not-be-opened"
        args = ["stage2", "--stage1", self.stage1_path, "--stage1-sha256", self.stage1_sha,
                "--manifest", self.manifest_path, "--allow-draft", "--looks", self.ledger, "--energy", responses]
        with cli_fixture.spy_opens() as opened:
            code, stdout, stderr = cli_fixture._cli_subprocess(args, repo=self.mini, extra={"host_probe": host_probe})
        self.assertNotIn(str(responses), opened)
        self.assertFalse(self.private.exists())
        self.assertFalse(self.public.exists())
        return subprocess.CompletedProcess(args, code, stdout, stderr)

    def test_successor_refuses_before_stage2_reads_or_execution(self):
        from tests.cadence import test_look_run as cli_fixture

        successor = "lm-interim-02"
        pin = M.load_json(REPO / MR.MANIFEST)["fit"]["twin"]
        self.assertEqual(pin, {"path": "scripts/cadence_interim_twin.py",
                               "sha256": "91ca54ab8747ede3d0fe8826e1b7d06ef721bce94de52969b9508a3eac890aab"})
        twin = (self.mini / pin["path"]).resolve()
        self.assertEqual(digest(twin.read_bytes()), pin["sha256"])
        MR.commit(self.mini, stage1_sha256=self.stage1_sha)
        first = M.load_json(self.manifest_path)
        manifest = dict(first, look_id=successor, supersedes=LOOK, fit=dict(first["fit"], twin=pin))
        path = self.manifest_path.with_name(f"{successor}.json")
        manifest_bytes = C.dump(manifest)
        path.write_bytes(manifest_bytes)
        stage1 = dict(self.stage1, manifest_sha256=digest(manifest_bytes))
        successor_stage1 = self.root / f"{successor}-stage1.json"
        successor_stage1.write_bytes(C.dump(dict(stage1, look_id=successor)))
        successor_sha = digest(successor_stage1.read_bytes())
        ledger_path = self.mini / M.LOOK_LEDGER_PATH
        ledger = M.load_json(ledger_path)
        M._look_row(ledger, LOOK).update(status="interrupted", error_type="none_recorded", ruling="RL-999")
        ledger["looks"].append(dict(self.row, look_id=successor, manifest_path=path.relative_to(self.mini).as_posix(),
                                    sha256=stage1["manifest_sha256"], stage1_sha256=successor_sha))
        ledger_path.write_bytes(C.dump(ledger))
        MR.git_commit(self.mini, "register synthetic successor")
        self.assertEqual(M.committed_ledger(self.mini)[2], ledger)
        M.require_successor_ruling(manifest, ledger)

        # A draft caller can name the predecessor's stage-1 row and rebind its manifest hash.
        # That route must still refuse on the successor manifest before reading generated inputs.
        self.stage1_path.write_bytes(C.dump(stage1))
        self.row["stage1_sha256"] = draft_sha = digest(self.stage1_path.read_bytes())
        self.save_ledger()
        responses = self.root / "responses.json"
        responses.write_bytes(C.dump(self.energy))
        root = Path(self.row["custody_root"])
        (root / successor).mkdir()
        (self.public.parent.parent / successor).mkdir()
        for source, sha, args in (
            (successor_stage1, successor_sha, ["--custody", root]),
            (self.stage1_path, draft_sha, ["--allow-draft", "--looks", self.ledger, "--energy", responses]),
        ):
            with self.subTest(args=args[0]), cli_fixture.spy_opens() as opened:
                rc, stdout, stderr = cli_fixture._cli_subprocess(
                    ["stage2", "--manifest", path, "--stage1", source, "--stage1-sha256", sha, *args],
                    repo=self.mini, extra={"host_probe": UUID_LINE, "twin_path": str(twin)})
                self.assertEqual(cli_fixture.LAST_RUN["reservation_attempts"], 0)
                reads = [item for item in opened if item in (str(source), str(responses))
                         or Path(item).is_relative_to(root)]
                self.assertEqual(reads, [])
                self.assertEqual(cli_fixture.LAST_RUN["twin_launches"], 0)
                self.assertEqual((rc, stdout), (2, ""))
                self.assertIn("look_id: the v1 validator admits only lm-interim-01", stderr)
        self.assertFalse(any(root.glob("*/RESTRICTED")))
        self.assertFalse(any(self.public.parent.parent.glob("*/PUBLIC.json")))

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
        for host, reason in ((None, "register the execution_host"), ("hw1:" + "0" * 64, "does not match")):
            with self.subTest(host=host):
                self.row.pop("execution_host", None)
                if host is not None:
                    self.row["execution_host"] = host
                self.save_ledger()
                result = self.stage2()
                self.assertEqual(result.returncode, 2)
                self.assertIn(reason, result.stderr)

    def test_exact_host_match_uses_the_same_gate_for_both_modes(self):
        with mock.patch.object(R.M, "execution_host", return_value=HOST_TOKEN) as probe:
            for synthetic in (True, False):
                R.validate_execution_row(self.row, dict(self.stage1, synthetic=synthetic), self.row["custody_root"])
            self.assertEqual(probe.call_count, 2)

    def test_missing_malformed_and_duplicate_uuid_refuse_before_reservation(self):
        for index, probe in enumerate(BAD_UUID_PROBES):
            with self.subTest(probe=index):
                result = self.stage2(host_probe=probe)
                self.assertEqual(result.returncode, 2)
                self.assertIn("exactly one UUID-shaped IOPlatformUUID", result.stderr)

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
    if argv[0] == "/usr/sbin/ioreg":
        assert argv == ["/usr/sbin/ioreg", "-rd1", "-c", "IOPlatformExpertDevice"]
        return subprocess.CompletedProcess(argv, 0,
            b'    "IOPlatformUUID" = "12345678-9abc-def0-1234-56789abcdef0"\n', b"")
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
    if fault == "missing_input":
        argv = list(argv)
        missing = path.with_name("missing-fit.json")
        assert not missing.exists()
        argv[argv.index("--fit") + 1] = str(missing)
    result = original_run(argv, *args, **kwargs)
    assert path.read_bytes() == before
    if fault == "missing_input":
        assert result.returncode == 1 and result.stdout == b""
        return result
    assert result.returncode == 0, result.returncode
    if fault == "malformed":
        result.stdout = b"not a frame\n"
    elif fault == "coefficient_change":
        path.write_bytes(before[:-1] + b" ")
    elif fault in ("missing_cell", "extra_cell", "malformed_cell"):
        frame = json.loads(result.stdout)
        cells = frame["verdicts"]["twin"]["D#/cells"]
        if fault == "missing_cell":
            cells.pop("10000")
        else:
            key = "32" if fault == "extra_cell" else "032"
            assert key not in cells
            cells[key] = {"status": "not_run", "gamma_estimable": None}
        result.stdout = json.dumps(frame, sort_keys=True, separators=(",", ":")).encode() + b"\n"
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
        self.twin = self.mini / pin["path"]
        self.assertEqual(digest(self.twin.read_bytes()),
                         "91ca54ab8747ede3d0fe8826e1b7d06ef721bce94de52969b9508a3eac890aab")
        draft["fit"]["twin"] = pin
        self.manifest.write_bytes(C.dump(draft))
        tokens = {}
        look_input, energy, _ = S.build("exact", tokens=tokens)
        source = self.root / "generated-bundles"
        self.source = source
        locators = S.write_custody(source, look_input, energy, tokens)
        # Duplicate each GPU interval. Its two positive overlaps count in both readers (P01).
        for trace in source.glob("*/legs/*/runtime/runs/cadence-leg/power_trace.csv"):
            header, *rows = trace.read_bytes().splitlines(keepends=True)
            trace.write_bytes(header + b"".join(row * (2 if b",gpu_power," in row else 1) for row in rows))
        # Use complete Step 3 telemetry so both implementations evaluate three
        # cells on the same generated native state and clock frames.
        for rich in source.glob("*/legs/*/runtime/runs/cadence-leg/rich_telemetry.jsonl"):
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
        self.stage1_args = ["stage1", "--roster", locators["roster.json"], "--rules-3-4", locators["rules_3_4.json"],
                            "--custody", source, "--manifest", self.manifest, "--allow-draft"]
        stage1 = MR.py(self.mini, "scripts/cadence_look_run.py", *self.stage1_args, "--out", self.stage1)
        self.assertEqual(stage1.returncode, 0, stage1.stderr)
        doc = M.load_json(self.stage1)
        self.response_sha = digest(self.stage1.read_bytes())
        self.spans = [row["span_id"] for row in doc["roster"]["spans"]]
        self.row = {"look_id": LOOK, "manifest_path": MR.MANIFEST, "sha256": digest(self.manifest.read_bytes()),
                    "stage1_sha256": self.response_sha, "status": "stage1_committed",
                    "roster_sha256": doc["code_sha256"]["input:roster_sha256"],
                    "verdicts_sha256": doc["code_sha256"]["input:rules_3_4_sha256"],
                    "execution_host": HOST_TOKEN,
                    "holds_cleared": {flag: "RL-999" for flag in M.STAGE2_HOLD_FLAGS["interim"]
                                      if doc[flag.split(".")[0]].get(flag.split(".")[1]) is True}}
        self.driver = self.root / "run.py"
        self.driver.write_text(TWIN_DRIVER)
        self.basename = MR.synthetic_reservation_name(self.root)

    def trial(self, fault, *, relocated=None):
        private_root = self.source if relocated is None else self.root / fault
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
        if relocated is not None:
            for sid in self.spans:
                argv.extend(("--span-dir", f"{sid}={relocated / sid}"))
        result = subprocess.run(argv, cwd=self.root, capture_output=True, timeout=180)
        return result, private, public

    def test_actual_parent_child_handshake_and_failure_channels(self):
        direct, private, public = self.trial("match")
        self.assertEqual((direct.returncode, direct.stdout, direct.stderr), (0, b"", b""))
        self.assertEqual(C.read_public(public.read_bytes(), SCHEMA)["twin_agrees"], "yes")
        fit = M.load_json(private / "fit.json")
        self.assertTrue(any("/runtime/runs/cadence-leg/" in f["path"] for f in fit["custody"]["files"]))
        direct_coefficients = (private / "coefficients.json").read_bytes()
        relocated = self.root / "relocated-spans"
        relocated.mkdir()
        for sid in self.spans:
            shutil.move(self.source / sid, relocated / sid)
            self.assertFalse((self.source / sid).exists())
        for fault, agreement in (("relocated", "yes"), ("numeric", "no"), ("missing_cell", "no"), ("extra_cell", "no"),
                                 ("malformed_cell", "not_evaluable"),
                                 ("omitted_fold", "not_evaluable"), ("forged_primary", "not_evaluable"),
                                 ("missing_input", "not_evaluable"),
                                 ("malformed", "not_evaluable"), ("timeout", "not_evaluable")):
            with self.subTest(fault=fault):
                run, private, public = self.trial(fault, relocated=relocated)
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
                if fault == "relocated":
                    self.assertTrue(json.loads(frame)["schema"].endswith(".v1"))
                    for side in ("primary", "twin"):
                        coverage = comparison["trace_coverage"]["gpu_rail"][side]["F#/channels/gpu_rail/trace_coverage"]
                        self.assertAlmostEqual(coverage["min"], 2.0)
                    self.assertTrue(all(cell["status"] == "ok" for cell in M.load_json(private / "step3.json")["cells"]))
                    fit = M.load_json(private / "fit.json")
                    paths = [Path(f["path"]) for f in fit["custody"]["files"] if "/runtime/runs/cadence-leg/" in f["path"]]
                    self.assertTrue(paths)
                    self.assertTrue(all(path.is_relative_to(relocated) for path in paths))
                    self.assertEqual(coefficients, direct_coefficients)
                    original = dict(row, twin_agrees=None)
                    original_coefficients = coefficients
                else:
                    self.assertEqual(dict(row, twin_agrees=None), original)
                    self.assertEqual(coefficients, original_coefficients)
                if fault == "numeric":
                    self.assertEqual(json.loads(frame)["max_relative_difference"]["gpu_rail"], 0)
                    self.assertGreater(comparison["max_relative_difference"]["gpu_rail"], 1e-8)
                if fault == "missing_input":
                    self.assertEqual((private / "stderr").read_bytes(), b"stage2_error\nFileNotFoundError\n")
                if fault == "malformed":
                    self.assertEqual(frame, b"not a frame\n")
                if fault == "timeout":
                    self.assertEqual(frame, b"synthetic partial frame")
        run, private, public = self.trial("coefficient_change", relocated=relocated)
        self.assertEqual((run.returncode, run.stdout, run.stderr), (C.FAILURE_STATUS, b"", b"stage2_error\nOtherError\n"))
        self.assertTrue(private.is_dir())
        self.assertFalse(public.exists())

    def test_primary_and_twin_refuse_bad_bundle_locators_before_response_reads(self):
        from tests.cadence import test_look_run as cli_fixture

        child_span = runpy.run_path(str(self.twin))["span_identities"]
        span = self.source / self.spans[0]
        leg = next(row for row in M.load_json(self.stage1)["legs"]
                   if row["span_id"] == self.spans[0] and row["in_energy_fit"])
        record_path = span / "legs" / leg["leg_key"].split("/", 1)[1] / "leg_record.json"
        record = M.load_json(record_path)
        self.assertEqual(record["result"]["bundle"], "runs/cadence-leg")
        out = self.root / "refused-stage1.json"
        ledger = self.root / "refusal-ledger.json"
        row = dict(self.row, custody_root=str(self.source), public_root="generated-refusal")
        ledger.write_bytes(C.dump({"schema": M.LOOK_LEDGER_SCHEMA, "looks": [row]}))
        (self.source / LOOK).mkdir()
        (self.mini / row["public_root"] / LOOK).mkdir(parents=True)
        private = self.source / LOOK / "RESTRICTED"
        stage2 = ["stage2", "--stage1", self.stage1, "--stage1-sha256", self.response_sha, "--manifest", self.manifest,
                  "--allow-draft", "--looks", ledger, "--custody", self.source]
        outside = self.root / "outside-runtime"
        outside.mkdir()
        (record_path.parent / "runtime" / "runs" / "escaped").symlink_to(outside, target_is_directory=True)
        bad = ("", "/runs/cadence-leg", "runs//cadence-leg", "runs/cadence-leg/", "./runs/cadence-leg",
               "runs/../cadence-leg", "runs/escaped")
        for locator in bad:
            with self.subTest(locator=locator):
                record["result"]["bundle"] = locator
                record_path.write_bytes(C.dump(record))
                reason = "escapes the leg runtime" if locator == "runs/escaped" else "invalid runtime bundle path"
                with self.assertRaisesRegex(ValueError, reason):
                    child_span(span)
                for args in ([*self.stage1_args, "--out", out], stage2):
                    with cli_fixture.spy_opens() as opened:
                        code, stdout, stderr = cli_fixture._cli_subprocess(args, repo=self.mini,
                                                                          extra={"host_probe": UUID_LINE})
                    self.assertEqual((code, stdout), (2, ""), stderr)
                    self.assertIn(reason, stderr)
                    self.assertFalse([path for path in opened if "/hazards/meter/" in path or Path(path).name in
                                      ("power_trace.csv", "rich_telemetry.jsonl", "powermetrics.plist")])
                self.assertFalse(out.exists() or private.exists())
        record["attempts"] = []
        record["result"].update(bundle=None, leg_status="incomplete", decode_cap_reached=False, g0_released=False)
        record_path.write_bytes(C.dump(record))
        self.assertIsNone(M.runtime_bundle(span, record_path.parent.name, record))
        self.assertNotIn(record_path.parent.name, child_span(span)[1])

    def test_writer_shapes_refuse_both_stages_before_response_reads(self):
        from tests.cadence import test_look_run as cli_fixture

        span = self.source / self.spans[0]
        receipt = span / "runner_receipt.json"
        original = receipt.read_bytes()
        leg = next(leg for leg in M.load_json(self.stage1)["legs"] if leg["in_energy_fit"] and leg["span_id"] == span.name)
        events = span / "legs" / leg["leg_key"].split("/", 1)[1] / "runtime/runs/cadence-leg/events.jsonl"
        original_events = events.read_bytes()
        out = self.root / "refused-stage1.json"
        private = self.source / LOOK / "RESTRICTED"
        public = self.mini / "public" / LOOK
        private.parent.mkdir()
        public.mkdir(parents=True)
        manifest = dict(M.load_json(self.manifest), status="committed")
        self.manifest.write_bytes(C.dump(manifest))
        ledger = self.mini / M.LOOK_LEDGER_PATH
        row = dict(self.row, sha256=digest(self.manifest.read_bytes()), status="committed",
                   custody_root=str(self.source), public_root="public")
        row.pop("stage1_sha256")
        ledger_doc = {"schema": M.LOOK_LEDGER_SCHEMA, "looks": [row]}
        ledger.write_bytes(C.dump(ledger_doc))
        MR.git_commit(self.mini, "register generated stage-1 inputs")
        stage1 = [arg for arg in self.stage1_args if arg != "--allow-draft"] + ["--ledger-ref", "origin/main"]
        committed_stage1 = self.root / "committed-stage1.json"
        control = MR.py(self.mini, "scripts/cadence_look_run.py", *stage1, "--out", committed_stage1)
        self.assertEqual(control.returncode, 0, control.stderr)
        stage1_sha = digest(committed_stage1.read_bytes())
        stage2 = ["stage2", "--stage1", committed_stage1, "--stage1-sha256", stage1_sha, "--manifest", self.manifest,
                  "--ledger-ref", "origin/main", "--custody", self.source]

        first = {"attempt": 1, "started_epoch_s": 1, "refused": "generated refusal", "output_dir": "soak.rejected1"}
        second = {"attempt": 2, "started_epoch_s": 2, "refused": None, "output_dir": "soak"}
        failed = {"name": "soak", "rc": 2, "error": "SoakRefusal: generated refusal"}
        success = {"name": "soak.a2", "rc": 0}
        cases = [
            ("duplicate", b'"rc":0,"rc":0', "duplicate keys"),
            ("nan", b'"rc":NaN', "nonfinite"), ("infinity", b'"rc":Infinity', "nonfinite"),
            ("overflow", b'"rc":1e999', "nonfinite"),
            ("contradictory exit", {"rc": 0, "error": "ValueError: generated fixture", "result": {"rc": 0}}, "contradicts its error"),
            ("unexplained exit", {"rc": 73}, "invalid span return code"),
            ("contradictory result", {"rc": 0, "result": {"rc": 3}}, "contradicts its result"),
            ("failed wait", {"steps": [{"name": "soak-blackout-wait", "rc": 130}, {"name": "soak", "rc": 0}]}, "failed soak wait"),
            ("null refusals", {"soak_refusals": None}, "soak_refusals"),
            ("missing refused", {"soak_attempts": [{k: v for k, v in first.items() if k != "refused"}], "steps": []}, "soak attempt fields"),
            ("retry limit", {"soak_attempts": [first, second, second], "steps": [failed, success]}, "soak attempt count"),
            ("forged provenance", {"soak_attempts": [dict(first, soak_refusals_kind="slope"), second], "steps": [failed, success]}, "soak attempt fields"),
            ("unknown kind", {"soak_attempts": [dict(first, refusal_kind="other"), second], "steps": [failed, success]}, "soak attempt fields"),
            ("unknown phase", {}, "invalid writer phase"),
            ("align_tool_1\u0662_0", {}, "invalid writer phase"),
            ("align_tool_0_1\u0662", {}, "invalid writer phase"),
            # The same two classes one level down: a step's exit path, and text where the writers put a number.
            ("unexplained step exit", {"steps": [{"name": "soak", "rc": 73}]}, "invalid step return code"),
            ("unpropagated step failure", {"steps": [{"name": "plan", "rc": 2, "error": "ValueError: generated"},
                                                     {"name": "soak", "rc": 0}]}, "failed step without the span's error"),
            ("step after the stop", {"rc": 2, "error": "ValueError: generated",
                                     "steps": [{"name": "plan", "rc": 2, "error": "ValueError: generated"},
                                               {"name": "soak", "rc": 0}]}, "after the span stopped"),
            ("text epoch", {"started": {"epoch_s": "\u0661\u0667\u0669\u0664\u0667\u0661\u0668\u0668\u0660\u0660"}},
             "started.epoch_s"),
        ]
        # A journal beside the receipt carries the same refusals: a duplicated key, and a token index in digits
        # outside ASCII, which ``int`` would read as 0.
        soak_reference = span / "soak/soak_reference.json"
        files = {receipt: original, events: original_events, soak_reference: soak_reference.read_bytes()}
        token = original_events.index(b'"event_type": "token"')
        line = original_events.rindex(b"\n", 0, token) + 1
        token_row = json.loads(original_events[line:original_events.index(b"\n", token)])
        token_row["metadata"]["index"] = "\u0660"
        other = [
            ("duplicate soak reference", soak_reference, b'{"generated":1,"generated":1,' + files[soak_reference][1:],
             "duplicate keys"),
            ("text token index", events, original_events[:line] + C.dump(token_row)
             + original_events[original_events.index(b"\n", token) + 1:], "invalid writer token"),
        ]
        for args in ([*stage1, "--out", out], stage2):
            if args[0] == "stage2":
                row.update(status="stage1_committed", stage1_sha256=stage1_sha)
                ledger.write_bytes(C.dump(ledger_doc))
                MR.git_commit(self.mini, "register generated stage-1 output")
            for label, mutation, reason in cases + [(name, path, why) for name, path, _, why in other]:
                with self.subTest(stage=args[0], label=label):
                    for path, data in files.items():
                        path.write_bytes(data)
                    receipt_doc = json.loads(original)
                    if isinstance(mutation, Path):
                        mutation.write_bytes(next(data for name, path, data, _ in other if name == label))
                    elif type(mutation) is bytes:
                        receipt_doc.pop("rc", None)
                        receipt.write_bytes(b"{" + mutation + b"," + C.dump(receipt_doc)[1:])
                    else:
                        receipt.write_bytes(C.dump(dict(receipt_doc, **mutation)))
                    phase = "not_a_writer_phase" if label == "unknown phase" else label
                    if reason == "invalid writer phase":
                        events.write_bytes(original_events + C.dump({"event_type": "phase_start", "phase": phase,
                                                                     "timestamp_s": 1, "metadata": {}}))
                    with cli_fixture.spy_opens() as opened:
                        code, stdout, stderr = cli_fixture._cli_subprocess(args, repo=self.mini,
                                                                          extra={"host_probe": UUID_LINE,
                                                                                 "twin_path": str(self.twin.resolve())})
                    self.assertEqual((code, stdout), (2, ""), stderr)
                    self.assertIn(reason, stderr)
                    self.assertEqual(cli_fixture.LAST_RUN["reservation_attempts"], 0)
                    self.assertEqual(cli_fixture.LAST_RUN["twin_launches"], 0)
                    self.assertFalse([name for name in opened if "/hazards/meter/" in name or Path(name).name in
                                      ("power_trace.csv", "rich_telemetry.jsonl", "powermetrics.plist")])
                    self.assertFalse(out.exists() or private.exists() or (public / "PUBLIC.json").exists())


@unittest.skipIf(R is None, "numpy is required")
class WriterShapes(unittest.TestCase):
    """RL-184 section 3.3 on generated custody. Each shape no pinned writer serializes refuses in the reader's
    pre-pass, before a meter stream, a power trace or native telemetry opens. One file changes per case."""

    @classmethod
    def setUpClass(cls):
        from joulewise.cadence_looks import fit_interim, time_fields

        cls.F, cls.TF = fit_interim, time_fields
        cls.root = Path(tempfile.mkdtemp(prefix="jw-writer-shapes-")).resolve()
        cls.addClassCleanup(shutil.rmtree, cls.root, True)
        tokens = {}
        look_input, energy, _ = S.build("exact", tokens=tokens)
        source = cls.root / "generated-bundles"
        locators = S.write_custody(source, look_input, energy, tokens)
        cls.roster = M.load_json(locators["roster.json"])[:1]
        cls.rules = M.load_json(locators["rules_3_4.json"])
        cls.span = source / cls.roster[0]["span_id"]
        cls.source = source
        control = cls.read()
        leg = next(leg for leg in control["legs"] if leg["turn"])
        cls.leg = cls.span / "legs" / leg["leg_id"]
        cls.bundle = cls.leg / "runtime" / M.load_json(cls.leg / "leg_record.json")["result"]["bundle"]

    @classmethod
    def read(cls):
        return R.read_look_input(cls.roster, R.span_dirs(cls.source, None), cls.rules)

    def refuses(self, label, path, data, reason):
        original = path.read_bytes()
        self.addCleanup(path.write_bytes, original)
        path.write_bytes(data)
        late = AssertionError("a response-bearing file opened before the refusal")
        with self.subTest(label=label), mock.patch.object(self.TF, "SpanMeter", side_effect=late), \
                mock.patch.object(self.TF, "gpu_rows", side_effect=late), \
                mock.patch.object(R, "native_states", side_effect=late), \
                self.assertRaisesRegex((self.F.LookInputError, M.ManifestError), reason):
            self.read()
        path.write_bytes(original)

    @staticmethod
    def changed(path, change, pick=None):
        """The file's bytes with one object changed: the document, or the first ``.jsonl`` row ``pick`` takes."""
        if pick is None:
            doc = json.loads(path.read_bytes())
            change(doc)
            return C.dump(doc)
        rows = [json.loads(line) for line in path.read_bytes().splitlines() if line.strip()]
        change(next(row for row in rows if pick(row)))
        return b"".join(C.dump(row) for row in rows)

    def test_the_generated_control_is_admitted(self):
        self.assertEqual(len(self.read()["spans"]), 1)

    def test_every_operational_file_is_strict_json(self):
        files = {"leg record": self.leg / "leg_record.json", "leg summary": self.leg / "leg_summary.json",
                 "soak reference": self.span / "soak/soak_reference.json", "config": self.bundle / "config.json",
                 "turns": self.bundle / "outputs/align_turns.jsonl",
                 "thermal journal": self.bundle / "outputs/align_thermal.jsonl", "events": self.bundle / "events.jsonl"}
        for name, path in files.items():
            data = path.read_bytes()
            self.assertEqual(data[:1], b"{", name)
            self.refuses(f"{name}: duplicate key", path, b'{"generated":1,"generated":1,' + data[1:], "duplicate keys")
            for token in (b"NaN", b"Infinity", b"-Infinity", b"1e999"):
                self.refuses(f"{name}: {token.decode()}", path, b'{"generated":' + token + b"," + data[1:], "nonfinite")
            self.refuses(f"{name}: not JSON", path, b"{" + data, "not JSON as the pinned writers serialize it")
            for encoding in ("utf-16", "utf-16-le", "utf-32-be", "utf-8-sig"):
                self.refuses(f"{name}: {encoding}", path, data.decode("utf-8").encode(encoding),
                             "not JSON as the pinned writers serialize it")

    def test_step_exit_paths_refuse_through_the_reader(self):
        receipt = self.span / "runner_receipt.json"
        failed = {"name": "plan", "rc": 2, "error": "ValueError: generated"}
        for label, change, reason in (
                ("unexplained step exit", {"steps": [{"name": "soak", "rc": 73}]}, "invalid step return code"),
                ("unpropagated failure", {"steps": [failed]}, "failed step without the span's error"),
                ("step after the stop", {"rc": 2, "error": failed["error"], "steps": [failed, {"name": "soak", "rc": 0}]},
                 "after the span stopped"),
                ("roster text", {"roster": "L001"}, "invalid receipt roster")):
            self.refuses(label, receipt, self.changed(receipt, lambda doc: doc.update(change)), reason)

    def test_text_and_booleans_are_never_read_as_numbers(self):
        """``float`` and ``int`` take digits outside ASCII, signs, spaces and underscores in text; the writers
        serialize JSON numbers."""
        receipt, record = self.span / "runner_receipt.json", self.leg / "leg_record.json"
        soak, turns = self.span / "soak/soak_reference.json", self.bundle / "outputs/align_turns.jsonl"
        thermal, events = self.bundle / "outputs/align_thermal.jsonl", self.bundle / "events.jsonl"
        reading = lambda row: row.get("kind") == "reading"                                  # noqa: E731
        token = lambda row: row.get("event_type") == "token"                                # noqa: E731
        for label, path, change, pick, reason in (
                ("receipt epoch text", receipt, lambda d: d["started"].update(epoch_s=str(d["started"]["epoch_s"])),
                 None, "started.epoch_s"),
                ("receipt epoch boolean", receipt, lambda d: d["started"].update(epoch_s=True), None, "started.epoch_s"),
                ("soak reference text", soak, lambda d: d["sensors_c"].update(TV0h="\u0665\u0667"), None, "TV0h"),
                ("cell prompt text", record, lambda d: d["spec"].update(prefill_tokens="\u0661\u0662"), None,
                 "spec.prefill_tokens"),
                ("cell prompt float", record, lambda d: d["spec"].update(prefill_tokens=12.0), None,
                 "spec.prefill_tokens"),
                ("cell prompt negative", record, lambda d: d["spec"].update(prefill_tokens=-1), None,
                 "spec.prefill_tokens"),
                ("recorded prefill text", record, lambda d: d["result"].update(prefill_tokens="12"), None,
                 "result.prefill_tokens"),
                ("turn prefill text", turns, lambda d: d["generation"].update(prefill_tokens="12"), bool,
                 "align_turns: prefill_tokens"),
                ("turn start text", turns, lambda d: d["start_stamp"].update(epoch_s=str(d["start_stamp"]["epoch_s"])),
                 bool, "start_stamp.epoch_s"),
                ("output ids text", turns, lambda d: d["generation"].update(output_token_ids="7" * 4096), bool,
                 "output_token_ids"),
                ("sensor text", thermal, lambda d: d["values"]["sensors"].update(Tf08="40.5"), reading, "Tf08"),
                ("soak sensor text", thermal, lambda d: d["values"]["sensors"].update(TV0h="\u0664\u0660"), reading,
                 "TV0h"),
                ("fan boolean", thermal, lambda d: d["values"]["sensors"].update(F0Ac=True), reading, "F0Ac"),
                ("journal stamp text", thermal, lambda d: d["finished"].update(wall_ns=str(d["finished"]["wall_ns"])),
                 reading, "finished.wall_ns"),
                ("token index text", events, lambda d: d["metadata"].update(index="\u0660"), token,
                 "invalid writer token"),
                ("token index boolean", events, lambda d: d["metadata"].update(index=False), token,
                 "invalid writer token"),
                ("token index float", events, lambda d: d["metadata"].update(index=0.0), token, "invalid writer token"),
                ("token index negative", events, lambda d: d["metadata"].update(index=-1), token,
                 "invalid writer token"),
                ("turn index boolean", events, lambda d: d["metadata"].update(align_turn_index=False), token,
                 "invalid writer token"),
                ("token metadata list", events, lambda d: d.update(metadata=[]), token, "invalid writer token"),
                ("token metadata null", events, lambda d: d.update(metadata=None), token, "invalid writer token"),
                ("token without an index", events, lambda d: d["metadata"].pop("index"), token,
                 "invalid writer token"),
                ("turn end text", turns, lambda d: d["end_stamp"].update(epoch_s=str(d["end_stamp"]["epoch_s"])),
                 bool, "end_stamp.epoch_s"),
                ("journal clock text", thermal,
                 lambda d: d["started"].update(monotonic_ns=str(d["started"]["monotonic_ns"])), reading,
                 "started.monotonic_ns"),
                ("token stamp text", events, lambda d: d.update(timestamp_s=str(d["timestamp_s"])), token,
                 "invalid writer timestamp"),
                ("token stamp boolean", events, lambda d: d.update(timestamp_s=True), token,
                 "invalid writer timestamp"),
                ("event type number", events, lambda d: d.update(event_type=5), token, "invalid writer event")):
            self.refuses(label, path, self.changed(path, change, pick), reason)
        self.refuses("event row list", events, b"[]\n" + events.read_bytes(), "invalid writer event")

    def test_phase_labels_are_the_writer_grammar(self):
        """``align_tool_<turn>_<call>`` is formatted from ``range`` and ``enumerate`` integers
        (joulewise/align/apple/workload.py:587 at the three pins)."""
        events = self.bundle / "events.jsonl"
        original = events.read_bytes()

        def phase(name, kind="phase_start", **more):
            return original + C.dump({"event_type": kind, "phase": name, "timestamp_s": 1, "metadata": {}, **more})

        for name in ("align_tool_0_0", "align_tool_12_3", "decode", "align_thermal_gate"):
            events.write_bytes(phase(name))
            with self.subTest(admitted=name):
                self.read()
        events.write_bytes(original)
        for name in ("align_tool_1\u0662_0", "align_tool_0_1\u0662", "align_tool_\u0661_0", "align_tool_0_\uff11",
                     "align_tool_01_0", "align_tool_0_00", "align_tool_-1_0", "align_tool_+1_0", "align_tool_1_ 0",
                     "align_tool_1_0\n", "align_tool_1__0", "align_tool_1", "align_tool_1_0_0", "ALIGN_TOOL_1_0",
                     "decode\n", " decode", "Decode", "not_a_writer_phase", "", None, 7, ["decode"]):
            self.refuses(f"phase {name!r}", events, phase(name), "invalid writer phase")
        self.refuses("phase kind", events, phase("decode", "phase_middle"), "invalid writer phase")
        self.refuses("phase metadata", events, phase("decode", metadata=[]), "invalid writer phase")
        self.refuses("phase stamp", events, phase("decode", timestamp_s="1"), "invalid writer timestamp")
